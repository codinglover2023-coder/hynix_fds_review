from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Service
from ..schemas import ServiceCreate, ServiceUpdate


async def create_service(session: AsyncSession, payload: ServiceCreate) -> Service:
    service = Service(**payload.model_dump())
    session.add(service)
    await session.commit()
    await session.refresh(service)
    return service


async def list_services(session: AsyncSession) -> list[Service]:
    result = await session.execute(select(Service).order_by(Service.id.asc()))
    return list(result.scalars().all())


async def get_service_by_id(session: AsyncSession, service_id: int) -> Service | None:
    result = await session.execute(select(Service).where(Service.id == service_id))
    return result.scalar_one_or_none()


async def get_service_by_sub_prefix(session: AsyncSession, sub_prefix: str) -> Service | None:
    result = await session.execute(select(Service).where(Service.sub_prefix == sub_prefix))
    return result.scalar_one_or_none()


async def update_service(session: AsyncSession, service: Service, payload: ServiceUpdate) -> Service:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, key, value)
    await session.commit()
    await session.refresh(service)
    return service


async def delete_service(session: AsyncSession, service: Service) -> None:
    await session.delete(service)
    await session.commit()

