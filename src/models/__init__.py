"""SQLModel domain models.

Import all table models here so metadata is registered for Alembic and the ORM.
"""

from src.models.base import Base  # noqa: F401
from src.models.user import User  # noqa: F401

User.model_rebuild()

__all__ = [
    "Base",
    "User",
]
