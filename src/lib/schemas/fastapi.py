"""FastAPI server configuration schemas."""

from pydantic import BaseModel, Field


class Server(BaseModel):
    """API server metadata."""

    title: str
    description: str
    version: str
    base_path: str = "/api"


class Middleware(BaseModel):
    """CORS middleware options."""

    allow_origins: list[str] = Field(default_factory=list)
    allow_credentials: bool = True
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])
