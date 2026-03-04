from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Service, UriMapping


async def seed_sample_data(session: AsyncSession) -> None:
    specs = [
        {
            "name": "confluence",
            "sub_prefix": "conf",
            "base_url": "https://company.atlassian.net",
            "auth_type": "bearer",
            "auth_value": "sample_token",
            "is_active": True,
            "path_pattern": "/wiki/rest/api",
            "description": "Confluence REST API",
        },
        {
            "name": "jira",
            "sub_prefix": "jira",
            "base_url": "https://company.atlassian.net",
            "auth_type": "bearer",
            "auth_value": "sample_token",
            "is_active": True,
            "path_pattern": "/rest/api/2",
            "description": "Jira REST API",
        },
    ]

    for spec in specs:
        result = await session.execute(
            select(Service).where(Service.sub_prefix == spec["sub_prefix"])
        )
        service = result.scalar_one_or_none()
        if service is None:
            service = Service(
                name=spec["name"],
                sub_prefix=spec["sub_prefix"],
                base_url=spec["base_url"],
                auth_type=spec["auth_type"],
                auth_value=spec["auth_value"],
                is_active=spec["is_active"],
            )
            session.add(service)
            await session.flush()

        mapping_result = await session.execute(
            select(UriMapping).where(
                UriMapping.service_id == service.id,
                UriMapping.path_pattern == spec["path_pattern"],
            )
        )
        mapping = mapping_result.scalar_one_or_none()
        if mapping is None:
            session.add(
                UriMapping(
                    service_id=service.id,
                    path_pattern=spec["path_pattern"],
                    description=spec["description"],
                    is_active=True,
                )
            )

    await session.commit()

