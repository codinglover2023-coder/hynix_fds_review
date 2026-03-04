from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UriMapping
from ..schemas import UriMappingCreate


def _normalize_path(value: str) -> str:
    value = value.strip()
    if not value.startswith("/"):
        value = f"/{value}"
    return value


def _matches_prefix(path: str, pattern: str) -> bool:
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)

    if pattern.endswith("*"):
        raw_prefix = pattern[:-1].rstrip("/")
        prefix = raw_prefix if raw_prefix else "/"
        return path == prefix or path.startswith(f"{prefix}/")

    prefix = pattern.rstrip("/")
    if not prefix:
        return path == "/"
    return path == prefix or path.startswith(f"{prefix}/")


async def create_mapping(
    session: AsyncSession, service_id: int, payload: UriMappingCreate
) -> UriMapping:
    mapping = UriMapping(service_id=service_id, **payload.model_dump())
    session.add(mapping)
    await session.commit()
    await session.refresh(mapping)
    return mapping


async def get_mappings_by_service_id(
    session: AsyncSession, service_id: int
) -> list[UriMapping]:
    result = await session.execute(
        select(UriMapping)
        .where(UriMapping.service_id == service_id)
        .order_by(UriMapping.id.asc())
    )
    return list(result.scalars().all())


async def get_mapping_by_id(session: AsyncSession, mapping_id: int) -> UriMapping | None:
    result = await session.execute(select(UriMapping).where(UriMapping.id == mapping_id))
    return result.scalar_one_or_none()


async def delete_mapping(session: AsyncSession, mapping: UriMapping) -> None:
    await session.delete(mapping)
    await session.commit()


async def path_allowed_for_service(
    session: AsyncSession, service_id: int, request_path: str
) -> bool:
    mappings = await get_mappings_by_service_id(session, service_id)
    active_patterns = [m.path_pattern for m in mappings if m.is_active]
    return any(_matches_prefix(request_path, pattern) for pattern in active_patterns)

