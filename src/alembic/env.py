"""Alembic environment file."""

from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool, text
from sqlmodel import SQLModel

from alembic import context

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from src.lib.db import sync_database_url

_sync_url = sync_database_url()

config.set_main_option("sqlalchemy.url", _sync_url.replace("%", "%%"))

import src.models  # noqa: F401, E402

target_metadata = SQLModel.metadata


def _ensure_postgres_extensions(connection) -> None:
    """Enable Postgres extensions required by models before migrations run."""
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
    connection.commit()


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a live DB connection (useful for dry-runs)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the DB and apply migrations."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _ensure_postgres_extensions(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
