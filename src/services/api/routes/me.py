"""Authenticated user routes."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from src.lib.auth.clerk import ClerkIdentityDep, resolve_clerk_email
from src.lib.db import get_session
from src.lib.exception import NotFound, Unprocessable
from src.models.user import User

router = APIRouter(tags=["Me"])

_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


class MeCreateRequest(SQLModel):
    """Fields required to create a product user after Clerk sign-in."""

    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=3, max_length=30)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "Name must not be blank"
            raise ValueError(msg)
        return stripped

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not _USERNAME_PATTERN.fullmatch(normalized):
            msg = "Username must be 3-30 characters: letters, numbers, underscore"
            raise ValueError(msg)
        return normalized


@router.get("/me", response_model=User)
async def get_me(
    identity: ClerkIdentityDep,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Return the signed-in user's DB row."""
    user = await session.get(User, identity.user_id)
    if user is None:
        raise NotFound("User not found")
    return user


@router.post("/me", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_me(
    body: MeCreateRequest,
    identity: ClerkIdentityDep,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Create the product user row for a signed-in Clerk account."""
    existing = await session.get(User, identity.user_id)
    if existing is not None:
        raise Unprocessable("User already exists")

    username_taken = await session.execute(
        select(User.id).where(User.username == body.username),
    )
    if username_taken.scalar_one_or_none() is not None:
        raise Unprocessable("Username is already taken")

    email: EmailStr
    if identity.email:
        email = identity.email
    else:
        email = resolve_clerk_email(identity.user_id)

    email_taken = await session.execute(select(User.id).where(User.email == email))
    if email_taken.scalar_one_or_none() is not None:
        raise Unprocessable("Email is already registered")

    now = datetime.now(UTC)
    user = User(
        id=identity.user_id,
        name=body.name,
        username=body.username,
        email=email,
        verified=True,
        verified_at=now,
        onboarding_done=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
