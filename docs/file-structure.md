# Current File Structure

This document shows only the current file structure and short descriptions.

## Root

- `apps/` - Frontend workspace (`apps/web` Vite + React).
- `docs/` - Project documentation files.
- `infra/` - Empty infrastructure placeholder (no CDK yet).
- `scripts/` - Helper scripts for local development workflows.
- `src/` - Backend Python source.
- `AGENTS.md` - Shared coding-agent instructions (Cursor, Claude Code, Codex, Antigravity).
- `CLAUDE.md` / `GEMINI.md` - Thin pointers to `AGENTS.md` for Claude Code / Antigravity.
- `.agents/rules/` - Modular agent rules (TypeScript, SQLModel, auth/db, SOLID, commits).
- `.cursor/rules/` - Cursor `.mdc` rules with globs / always-apply.
- `.env.example` - Index pointing to per-service env templates.
- `.env.example.api` - Root environment template (database, Clerk).
- `alembic.ini` - Alembic migration configuration.
- `package.json` - Root Node scripts and workspace commands.
- `pnpm-workspace.yaml` - PNPM workspace package definitions (`apps/*`).
- `pyproject.toml` - Python project metadata and dependencies.
- `ruff.toml` - Ruff lint/format configuration.
- `mypy.ini` - Mypy strict type-checking configuration.
- `README.md` - Project overview and setup guide.

## Apps

### `apps/web`

Vite + React SPA with Clerk (`@clerk/react`).

#### `apps/web/src`

- `api/` - Typed HTTP helpers (placeholder).
- `assets/` - Static images and icons.
- `components/` - UI by feature; `auth/` holds Clerk sign-in shell.
- `hooks/` - React hooks (placeholder).
- `lib/` - Utilities; `lib/api/config.ts` for API base URL.
- `stat/` - Client state placeholder.
- `styles/` - Global (`index.css`) and app (`app.css`) styles.
- `types/` - Shared TypeScript types (placeholder).
- `app.tsx` - Root app component (signed-in starter content).
- `main.tsx` - Entry; wraps app in `ClerkProvider`.

## Scripts

- `scripts/run.py` - Unified CLI for db, apps, and API commands.

## Backend `src`

- `alembic/` - Database migration scripts and Alembic runtime files.
- `constants/` - Shared backend constants.
- `enums/` - Enumerations (placeholder).
- `lib/` - Shared backend libraries.
- `models/` - SQLModel model definitions (User only).
- `services/` - Backend service-layer compose points.

### `src/constants`

- `model.py` - Shared SQLAlchemy `MetaData` and naming convention for tables.

### `src/models`

- `__init__.py` - Alembic/ORM barrel importing table models only.
- `base.py` - Shared SQLModel base bound to ORM metadata.
- `common.py` - Timestamp and verification mixins.
- `user.py` - User table and create/update/delete schemas.

### `src/lib`

- `auth/` - Clerk session verification (`clerk.py`).
- `agent/` - Agent/LLM integration placeholder.
- `db.py` - Async/sync database engines and session dependency.
- `exception.py` - HTTP exception helpers.
- `fastapi/` - FastAPI server utilities and health route.
- `jobs/` - Background/job helpers placeholder.
- `schemas/` - Shared Pydantic schemas.
- `storage/` - Object storage helpers placeholder.

### `src/services`

- `api/` - FastAPI HTTP service (`app.py`, `routes/me.py`).
- `agent/` - Agent service placeholder.

## Infra

- `infra/` - Empty (`.gitkeep` only). Add CDK or other IaC later.
