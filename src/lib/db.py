"""Database connection and session management."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path
from urllib.parse import quote_plus
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        msg = f"{name} is not set in the environment"
        raise RuntimeError(msg)
    return value


def _is_supabase_host(host: str) -> bool:
    return "supabase.co" in host or "pooler.supabase.com" in host


def _pooler_mode() -> str | None:
    """Return Supavisor pool mode from host/port, or None for direct connections."""
    host = _require_env("DATABASE_HOST")
    port = _require_env("DATABASE_PORT")
    if "pooler.supabase.com" not in host:
        return None
    if port == "6543":
        return "transaction"
    if port == "5432":
        return "session"
    return None


def build_database_url(*, driver: str) -> str:
    """Build a SQLAlchemy URL with encoded credentials and Supabase SSL when needed."""
    user = quote_plus(_require_env("DATABASE_USER"))
    password = quote_plus(_require_env("DATABASE_PASSWORD"))
    host = _require_env("DATABASE_HOST")
    port = _require_env("DATABASE_PORT")
    name = _require_env("DATABASE_NAME")

    url = f"{driver}://{user}:{password}@{host}:{port}/{name}"
    if _is_supabase_host(host):
        if driver.endswith("+asyncpg"):
            return f"{url}?ssl=require"
        return f"{url}?sslmode=require"
    return url


def sync_database_url() -> str:
    """Sync driver URL for Alembic and bootstrap scripts."""
    return build_database_url(driver="postgresql+psycopg2")


_sync_engine = create_engine(
    sync_database_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SyncSessionLocal = sessionmaker(
    bind=_sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


_async_url = build_database_url(driver="postgresql+asyncpg")

_async_connect_args: dict[str, object] = {}
_async_engine_kwargs: dict[str, object] = {
    "echo": False,
    "future": True,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}
if _pooler_mode() == "transaction":
    _async_connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    }
    _async_engine_kwargs["poolclass"] = NullPool
    _async_engine_kwargs.pop("pool_size", None)
    _async_engine_kwargs.pop("max_overflow", None)

engine: AsyncEngine = create_async_engine(
    _async_url,
    connect_args=_async_connect_args,
    **_async_engine_kwargs,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session per request, always closes cleanly."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
