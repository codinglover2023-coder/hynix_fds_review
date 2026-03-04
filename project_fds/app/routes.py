from fastapi import FastAPI

from .routers import sample


def register_routes(app: FastAPI) -> None:
    app.include_router(sample.router)
