# Blueprint

Monorepo scaffold: **Vite** web app + **FastAPI** / SQLModel backend, with an empty `infra/` placeholder.

## Layout

| Path | Role |
|------|------|
| `apps/web` | Vite + React frontend with Clerk |
| `src/` | Python backend (`lib`, `models`, `services`, `alembic`) |
| `infra/` | Empty placeholder (no CDK yet) |
| `scripts/` | Unified CLI (`run.py`) wired from root `package.json` |
| `docs/` | Project documentation |
| `AGENTS.md` | Shared rules for Cursor / Claude Code / Codex / Antigravity |

## Tooling

- **Node/pnpm**: workspaces via `pnpm-workspace.yaml` (`apps/*`)
- **Python/Poetry**: `pyproject.toml` (`package-mode = false`)
- **Root scripts**: thin wrappers → `python scripts/run.py …`

### Root scripts

| Script | Purpose |
|--------|---------|
| `db:create` | Create or reset local Postgres app DB |
| `db:clean` | Truncate all tables in `public` |
| `db:make` | Alembic autogenerate revision |
| `db:upgrade` | Alembic upgrade head |
| `dev` | Run API + web together via `concurrently` |
| `app:web` | `pnpm --dir apps/web run <script>` |
| `service:api` | Uvicorn `src.services.api.app:app` on `:8000` |
| `app:clean:all` | Remove root/app `node_modules` and `dist` |
| `app:clean:install` | Clean then `pnpm install` |

## Setup

1. Copy `.env.example.api` → `.env` and fill values.
2. Copy `apps/web/.env.example` → `apps/web/.env` and fill Clerk / API URL.
3. `poetry install` (or create `.venv` and install from `pyproject.toml`).
4. `pnpm install` from this directory.
5. See `docs/file-structure.md` for the current tree.
