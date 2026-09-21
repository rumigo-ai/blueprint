"""Blueprint FastAPI application."""

from src.lib.fastapi.server import cors_allow_origins, create_server
from src.lib.schemas.fastapi import Middleware, Server
from src.services.api.routes.me import router as me_router

server = Server(
    title="Blueprint API",
    description="Blueprint platform API",
    version="0.1.0",
    base_path="/api",
)

middleware = Middleware(
    allow_origins=cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app, router = create_server(server, middleware)
router.include_router(me_router)
app.include_router(router)
