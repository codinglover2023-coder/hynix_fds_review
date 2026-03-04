from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.mapping import path_allowed_for_service
from ..crud.service import get_service_by_sub_prefix
from ..deps import get_db
from ..models import Service

router = APIRouter(tags=["proxy"])

DbSession = Annotated[AsyncSession, Depends(get_db)]

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def build_auth_header(service: Service) -> dict[str, str]:
    if service.auth_type == "bearer":
        return {"Authorization": f"Bearer {service.auth_value}"}
    if service.auth_type == "basic":
        return {"Authorization": f"Basic {service.auth_value}"}
    if service.auth_type == "api_key":
        return {"X-API-Key": service.auth_value}
    return {}


def filter_request_headers(headers: dict[str, str]) -> dict[str, str]:
    # accept-encoding 제거: httpx가 자체적으로 디코딩 처리하므로 이중 압축 방지
    ignored = HOP_BY_HOP_HEADERS.union({"host", "content-length", "accept-encoding"})
    return {k: v for k, v in headers.items() if k.lower() not in ignored}


def filter_response_headers(headers: dict[str, str]) -> dict[str, str]:
    # content-encoding 제거: httpx가 이미 디코딩한 응답을 그대로 전달
    ignored = HOP_BY_HOP_HEADERS.union({"content-length", "content-encoding"})
    return {k: v for k, v in headers.items() if k.lower() not in ignored}


def build_target_url(base_url: str, path: str) -> str:
    cleaned_base = base_url.rstrip("/")
    cleaned_path = path.lstrip("/")
    return f"{cleaned_base}/{cleaned_path}"


@router.api_route(
    "/{sub_prefix}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
async def proxy_endpoint(sub_prefix: str, path: str, request: Request, db: DbSession):
    service = await get_service_by_sub_prefix(db, sub_prefix)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    if not service.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Service is inactive")

    request_path = f"/{path.lstrip('/')}"
    allowed = await path_allowed_for_service(db, service.id, request_path)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Path is not allowed for this service",
        )

    target_url = build_target_url(service.base_url, path)
    headers = filter_request_headers(dict(request.headers))
    headers.update(build_auth_header(service))

    body = await request.body()
    client: httpx.AsyncClient = request.app.state.http_client
    try:
        upstream_response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    response_headers = filter_response_headers(dict(upstream_response.headers))
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )

