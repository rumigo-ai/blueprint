# Python / SQLModel

Activation: files under `src/**/*.py`

## Layout

| Path | Holds |
|------|--------|
| `src/models/` | SQLModel `table=True` + Create/Update/Delete schemas |
| `src/models/__init__.py` | **Only** table classes (Alembic barrel) |
| `src/enums/` | `StrEnum` only |
| `src/constants/` | `ORM_METADATA`, naming convention |
| `src/lib/` | auth, db, exceptions, fastapi helpers |
| `src/services/api/routes/` | Thin HTTP handlers |

## `__init__.py`

Only `src/models/__init__.py` is allowed. Ask before adding any other.

## Model example

```python
class UserBase(SQLModel):
    name: str = Field(max_length=100)
    username: str = Field(max_length=30, unique=True)
    email: EmailStr = Field(max_length=255, unique=True)

class User(UserBase, TimestampMixin, VerificationMixin, Base, table=True):
    __tablename__ = "users"
    id: str = Field(primary_key=True, max_length=255)  # Clerk sub
    onboarding_done: bool = Field(default=False)
```

- Mixins in `models/common.py` (not tables)
- Base in `models/base.py` bound to `ORM_METADATA`
- Do not put table classes under `src/lib/`

## Typing

- `from __future__ import annotations`
- `X | None` not `Optional[X]`
- `Annotated[T, Depends(...)]` for FastAPI deps
- Migrations: autogenerate only (`pnpm run db:make`)
