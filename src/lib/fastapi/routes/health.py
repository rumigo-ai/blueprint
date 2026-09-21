"""Health API route."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.lib.db import engine

TAG = "Health"
router = APIRouter()


async def database_ping_ok() -> bool:
    """Return whether a trivial database round-trip succeeds."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True


@router.get("/health", tags=[TAG], name="Health check")
async def health_check() -> dict[str, Any]:
    """Return service status after verifying database connectivity."""
    timestamp = datetime.now(UTC).isoformat()
    if not await database_ping_ok():
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "unreachable",
                "timestamp": timestamp,
            },
        )
    return {"status": "healthy", "database": "ok", "timestamp": timestamp}
