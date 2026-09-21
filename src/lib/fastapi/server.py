"""FastAPI server."""

import os
from collections.abc import AsyncIterator
from typing import Callable

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.lib.fastapi.routes.health import router as health_router
from src.lib.fastapi.templates.scalar import DOCS_TEMPLATE
from src.lib.schemas.fastapi import Middleware, Server

load_dotenv(".env")


def cors_allow_origins() -> list[str]:
    """Parse ``CORS_ALLOWED_ORIGINS``: comma-separated scheme+host+port origins."""
    cors = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [o.strip() for o in cors.split(",") if o.strip()]


def create_server(
    server: Server,
    middleware: Middleware,
    *,
    lifespan: Callable[[FastAPI], AsyncIterator[None]] | None = None,
) -> tuple[FastAPI, APIRouter]:
    """Create a FastAPI server."""
    env = os.getenv("ENV", "development").strip().lower()
    app = FastAPI(
        title=server.title,
        description=server.description,
        version=server.version,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json" if env != "production" else None,
        lifespan=lifespan,
    )

    app.add_middleware(CORSMiddleware, **middleware.model_dump())

    router = APIRouter(prefix=server.base_path)
    router.include_router(health_router)

    if env != "production":

        @app.get("/docs", include_in_schema=False)
        async def docs() -> HTMLResponse:
            """Scalar based documentation."""
            html = DOCS_TEMPLATE.replace("{{title}}", server.title)
            return HTMLResponse(html)

    return app, router
