# AGENTS.md — Blueprint

Shared instructions for **Cursor**, **Claude Code**, **Codex**, **Antigravity**, and any other coding agent.

Modular copies (same policies) live under:

- [`.agents/rules/`](.agents/rules/) — Antigravity / Gemini workspace rules
- [`.cursor/rules/`](.cursor/rules/) — Cursor `.mdc` rules with globs

If a tool-specific file conflicts with this document, **this file wins** unless the user overrides in chat.

---

## Project shape

| Path | Role |
|------|------|
| `apps/web` | Vite + React + TypeScript + Clerk (`@clerk/react`) |
| `src/` | FastAPI + SQLModel backend |
| `infra/` | Empty placeholder — do not invent CDK unless asked |
| `scripts/run.py` | CLI for db / app / API |

Python: `>=3.12,<3.13`. Package mode is off (`pyproject.toml`). Frontend path alias: `@/*` → `apps/web/src/*`.

---

## Non-negotiables

1. Do not edit `genesys/` or `foundry/` from this repo’s work unless the user explicitly asks.
2. Only create `__init__.py` at `src/models/__init__.py` (Alembic barrel). Ask before adding any other `__init__.py`.
3. Migrations: **autogenerate only** (`pnpm run db:make "…"`). Never hand-write Alembic revisions.
4. Table models live in `src/models/`. Auth/DB helpers live in `src/lib/`. Routes stay thin in `src/services/api/routes/`.
5. Do not invent product tables beyond what the user asks. Prefer extending `User` carefully over sprawling schemas.
6. Never commit secrets. `.env` is gitignored; only update `.env.example` / `.env.example.api` with placeholder names.
7. Follow SOLID (see below). Prefer small, typed modules over god-files.

---

## Git commit messages

Only commit when the user asks. Use a HEREDOC; follow this repo’s style.

### Format

```text
<type>(optional-scope): <imperative summary>

Optional body: why, not a file laundry list.
```

### Types

| Type | Use when |
|------|----------|
| `feat` | New user-facing capability |
| `fix` | Bug fix |
| `refactor` | Behavior-preserving restructure |
| `chore` | Tooling, deps, ignore files, scaffolding |
| `docs` | Documentation / agent rules only |
| `test` | Tests only |
| `style` | Formatting with no logic change |

### Rules

- Subject: imperative mood, ≤72 chars, no trailing period
- Explain **why** in the body when non-obvious
- One logical change per commit; do not mix feat + chore unless asked
- Never `--no-verify` unless the user explicitly requests it
- Never amend a pushed commit unless the user explicitly requests it

### Examples

```text
feat(api): add Clerk-backed GET /api/me

Product user id is the Clerk JWT sub so the SPA and API share identity.
```

```text
fix(web): pass publishable key into ClerkProvider

Without the key Clerk JS fails to load and the root stays blank.
```

```text
chore: add shared AGENTS.md for multi-tool coding agents
```

```text
# BAD — vague, past tense, file dump
Updated stuff and fixed bugs in auth.py db.py me.py app.tsx
```

---

## SOLID (apply everywhere)

| Principle | In this repo |
|-----------|--------------|
| **S**ingle responsibility | One module = one reason to change. Routes do not open DB engines; models do not verify JWTs. |
| **O**pen/closed | Extend via new route modules / lib domains; avoid editing core `db.py` / `clerk.py` for every feature. |
| **L**iskov | Schema subtypes (`UserCreate`) must remain valid substitutes for their base fields. |
| **I**nterface segregation | Depend on `ClerkIdentityDep` / `AsyncSession`, not a mega “AppContext”. |
| **D**ependency inversion | Routes depend on FastAPI `Depends` abstractions; libraries do not import route modules. |

### Good vs bad layering

```text
# ✅ GOOD
route → Depends(ClerkIdentityDep, get_session) → lib/auth + lib/db → models.User

# ❌ BAD
route → creates Clerk client + engine + runs raw SQL + returns ORM dump with secrets
```

```python
# ❌ BAD — route owns everything
@router.get("/me")
async def me(request: Request):
    clerk = Clerk(bearer_auth=os.environ["CLERK_SECRET_KEY"])
    engine = create_async_engine(...)
    ...

# ✅ GOOD — route only wires dependencies
@router.get("/me")
async def me(
    identity: ClerkIdentityDep,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    user = await session.get(User, identity.user_id)
    if user is None:
        raise NotFound("User not found")
    return user
```

---

## Python / SQLModel

### Folder map

```text
src/
  constants/     # ORM_METADATA, naming conventions (not business logic)
  enums/         # StrEnum only
  models/        # SQLModel tables + *Create/*Update/*Delete in same file
    __init__.py  # ONLY table=True classes for Alembic
    base.py      # Base = SQLModel bound to ORM_METADATA
    common.py    # TimestampMixin, VerificationMixin (not tables)
  lib/
    auth/        # Clerk verification + ClerkIdentityDep
    db.py        # engines, URLs, get_session
    exception.py # HTTPException subclasses
    fastapi/     # create_server, health
    schemas/     # shared Pydantic value objects (non-table)
  services/api/
    app.py       # compose routers
    routes/      # thin HTTP handlers
```

### Typing rules

- Use `from __future__ import annotations` in new modules.
- Prefer `X | None` over `Optional[X]`.
- Annotate public functions; keep mypy strict happy.
- FastAPI deps: `Annotated[T, Depends(...)]`.
- Do not use `Any` to silence types; narrow with `isinstance` or explicit casts.

### Model pattern (only tables the user asked for)

```python
# src/models/user.py
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from src.models.base import Base
from src.models.common import TimestampMixin, VerificationMixin


class UserBase(SQLModel):
    name: str = Field(max_length=100)
    username: str = Field(max_length=30, unique=True)
    email: EmailStr = Field(max_length=255, unique=True)


class User(UserBase, TimestampMixin, VerificationMixin, Base, table=True):
    """Product user. Primary key is Clerk user id (JWT sub)."""

    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    onboarding_done: bool = Field(default=False)


class UserCreate(UserBase):
    id: str
    onboarding_done: bool = False


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    username: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = Field(default=None, max_length=255)
    onboarding_done: bool | None = None
```

```python
# src/models/__init__.py — barrel exports TABLE classes only
from src.models.user import User

User.model_rebuild()

__all__ = ["User"]
```

```python
# ❌ BAD — do not put table models under lib/
# src/lib/user_model.py

# ❌ BAD — do not add UserCreate to models/__init__.py
```

### Auth module (`src/lib/auth/clerk.py`)

Responsibilities: verify Bearer session JWT, expose identity, optional Clerk API lookups.

```python
@dataclass(frozen=True, slots=True)
class ClerkIdentity:
    user_id: str
    email: str | None = None


def require_clerk_identity(request: Request) -> ClerkIdentity:
    """Verify session; raise Unauthorized on failure."""
    ...


ClerkIdentityDep = Annotated[ClerkIdentity, Depends(require_clerk_identity)]
```

Rules:

- Read `CLERK_SECRET_KEY` from env; fail fast if missing.
- Map auth failures to `Unauthorized` from `src.lib.exception`.
- Do **not** load SQLModel users inside `clerk.py` (SRP).
- Product `User.id` **is** `identity.user_id` (Clerk `sub`).

### DB module (`src/lib/db.py`)

Responsibilities: build URLs from `DATABASE_*`, sync + async engines, `get_session`.

```python
def sync_database_url() -> str:
    """Used by Alembic only."""
    return build_database_url(driver="postgresql+psycopg2")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

Rules:

- Load root `.env` once; never hard-code credentials.
- Support local Postgres and Supabase SSL/pooler quirks in URL builders.
- Routes import `get_session`, not engines (except health checks).
- Alembic `env.py` calls `sync_database_url()` and `import src.models`.

### Exceptions

Use `src.lib.exception` (`Unauthorized`, `NotFound`, `Unprocessable`). Do not raise bare `HTTPException` in new route code unless extending that module.

---

## TypeScript / `apps/web`

### Folder map

```text
apps/web/src/
  api/           # typed fetch helpers (prefer over ad-hoc fetch in components)
  components/    # kebab-case files; feature folders OK
  hooks/
  lib/           # pure helpers; lib/api/config.ts for VITE_API_BASE_URL
  stat/          # client state when needed
  styles/        # index.css (entry), app.css (app shell)
  types/         # flat type files (no deep type trees)
  app.tsx
  main.tsx       # ClerkProvider here
```

### Typing rules

- Strict TypeScript; no implicit `any`.
- Prefer `type` for object shapes; use `interface` only when extending/merging is needed.
- Props: explicit `type FooProps = { ... }` (or interface); no untyped `children` without `ReactNode`.
- Use `import type` for type-only imports (`verbatimModuleSyntax`).
- Env: only `VITE_*` via `import.meta.env`; extend `vite-env.d.ts` when adding keys.
- Path imports: `@/components/...`, not long relative `../../../`.

### Clerk (Vite)

```tsx
// main.tsx
const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
if (!publishableKey) {
  throw new Error("Missing VITE_CLERK_PUBLISHABLE_KEY")
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ClerkProvider publishableKey={publishableKey}>
      <Show when="signed-out">
        <SignInPage />
      </Show>
      <Show when="signed-in">
        <AuthShell>
          <App />
        </AuthShell>
      </Show>
    </ClerkProvider>
  </StrictMode>,
)
```

Rules:

- No silent auth fallback UI when keys are missing — fail loud.
- Keep auth chrome under `components/auth/`.
- API calls that need the session: get a Clerk token and send `Authorization: Bearer <token>` to `VITE_API_BASE_URL`.

### API helper example

```ts
// lib/api/config.ts
export function apiBaseUrl(): string {
  const value = import.meta.env.VITE_API_BASE_URL
  if (!value) {
    throw new Error("Missing VITE_API_BASE_URL")
  }
  return value.replace(/\/$/, "")
}

// api/me.ts
import { apiBaseUrl } from "@/lib/api/config"

export type UserDto = {
  id: string
  name: string
  username: string
  email: string
  onboarding_done: boolean
}

export async function fetchMe(token: string): Promise<UserDto> {
  const res = await fetch(`${apiBaseUrl()}/api/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    throw new Error(`GET /api/me failed: ${res.status}`)
  }
  return res.json() as Promise<UserDto>
}
```

```ts
// ❌ BAD
fetch("http://localhost:8000/api/me") // hard-coded origin, no types, no auth header
```

---

## Commands agents should know

```bash
pnpm install
pnpm run dev          # API (:8000) + web (Vite) via concurrently
pnpm run app:web dev
pnpm run service:api
pnpm run db:create
pnpm run db:make "describe change"
pnpm run db:upgrade
poetry install   # or venv + pip from pyproject.toml
```

---

## When unsure

1. Match existing blueprint files before inventing new layers.
2. Prefer copying patterns from `src/lib/auth/clerk.py`, `src/lib/db.py`, and `src/models/user.py`.
3. Ask the user before adding new SQLModel tables, `__init__.py` files, or infra/CDK code.
