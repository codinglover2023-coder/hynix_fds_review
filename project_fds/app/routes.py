from fastapi import FastAPI

from .routers import admin, proxy, sample


def register_routes(app: FastAPI) -> None:
    app.include_router(admin.router)
    app.include_router(sample.router)
    app.include_router(proxy.router)
