"""User model for the platform using SQLModel."""

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from src.models.base import Base
from src.models.common import TimestampMixin, VerificationMixin


class UserBase(SQLModel):
    """Base schema for User."""

    name: str = Field(max_length=100)
    username: str = Field(max_length=30, unique=True)
    email: EmailStr = Field(max_length=255, unique=True)


class User(UserBase, TimestampMixin, VerificationMixin, Base, table=True):
    """Product identity for the platform.

    Primary key ``id`` is the Clerk user id (JWT ``sub``).
    """

    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    onboarding_done: bool = Field(default=False)


class UserCreate(UserBase):
    """Schema for creating a user."""

    id: str
    onboarding_done: bool = False


class UserUpdate(SQLModel):
    """Schema for updating a user."""

    name: str | None = Field(default=None, max_length=100)
    username: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = Field(default=None, max_length=255)
    verified: bool | None = None
    onboarding_done: bool | None = None


class UserDelete(SQLModel):
    """Schema for deleting a user."""

    id: str
