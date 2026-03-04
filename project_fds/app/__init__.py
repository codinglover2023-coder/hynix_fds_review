from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from dotenv import load_dotenv

from .bootstrap import seed_sample_data
from .db import SessionLocal, init_db
from .routes import register_routes

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with SessionLocal() as session:
        await seed_sample_data(session)
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    try:
        yield
    finally:
        await app.state.http_client.aclose()


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
