from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.mapping import (
    create_mapping,
    delete_mapping,
    get_mapping_by_id,
    get_mappings_by_service_id,
)
from ..crud.service import (
    create_service,
    delete_service,
    get_service_by_id,
    list_services,
    update_service,
)
from ..deps import get_db, verify_admin_key
from ..schemas import (
    ServiceCreate,
    ServiceOut,
    ServiceUpdate,
    UriMappingCreate,
    UriMappingOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(verify_admin_key)])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
async def create_service_endpoint(payload: ServiceCreate, db: DbSession):
    try:
        return await create_service(db, payload)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service name or sub_prefix already exists",
        ) from None


@router.get("/services", response_model=list[ServiceOut])
async def list_services_endpoint(db: DbSession):
    return await list_services(db)


@router.get("/services/{service_id}", response_model=ServiceOut)
async def get_service_endpoint(service_id: int, db: DbSession):
    service = await get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.put("/services/{service_id}", response_model=ServiceOut)
async def update_service_endpoint(service_id: int, payload: ServiceUpdate, db: DbSession):
    service = await get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    try:
        return await update_service(db, service, payload)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service name or sub_prefix already exists",
        ) from None


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_endpoint(service_id: int, db: DbSession):
    service = await get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    await delete_service(db, service)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/services/{service_id}/mappings",
    response_model=UriMappingOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_mapping_endpoint(service_id: int, payload: UriMappingCreate, db: DbSession):
    service = await get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return await create_mapping(db, service_id, payload)


@router.get("/services/{service_id}/mappings", response_model=list[UriMappingOut])
async def list_mappings_endpoint(service_id: int, db: DbSession):
    service = await get_service_by_id(db, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return await get_mappings_by_service_id(db, service_id)


@router.delete("/mappings/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mapping_endpoint(mapping_id: int, db: DbSession):
    mapping = await get_mapping_by_id(db, mapping_id)
    if mapping is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")
    await delete_mapping(db, mapping)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

