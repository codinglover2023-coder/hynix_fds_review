import os
from typing import Annotated

from fastapi import Header, HTTPException, status

from .db import get_session


async def get_db():
    async for session in get_session():
        yield session


def verify_admin_key(x_admin_key: Annotated[str | None, Header(alias="X-ADMIN-KEY")] = None) -> None:
    expected_key = os.getenv("FDS_ADMIN_KEY", "fds-admin-key")
    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-ADMIN-KEY header is required",
        )
    if x_admin_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin key",
        )

