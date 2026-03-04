from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import register_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title="FDS Review API",
        description="Hynix FDS Review Sample API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/api/healthz", tags=["health"])
    async def healthz():
        return {"status": "ok"}

    register_routes(app)
    return app
