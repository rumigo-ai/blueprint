"""Unified CLI runner for all project scripts.

Usage (via pnpm):
    pnpm run db:create
    pnpm run db:clean
    pnpm run db:make "migration name"
    pnpm run db:upgrade
    pnpm run app:web dev
    pnpm run service:api

Usage (directly):
    python scripts/run.py db:create
    python scripts/run.py db:clean
    python scripts/run.py db:make "migration name"
    python scripts/run.py app:web dev
    python scripts/run.py service:api
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from contextlib import suppress
from pathlib import Path
from typing import NoReturn

try:
    import psycopg2
    from psycopg2 import errors as pg_errors
    from psycopg2 import sql as pg_sql
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

ROOT = Path(__file__).parent.parent

VENV_BIN = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
ALEMBIC = str(VENV_BIN / "alembic")
PNPM = "pnpm.cmd" if sys.platform == "win32" else "pnpm"


def load_env() -> dict[str, str]:
    """Read key=value pairs from the root .env file."""
    env: dict[str, str] = {}
    env_file = ROOT / ".env"
    if not env_file.exists():
        die(f".env file not found at {env_file}")
    for raw in env_file.read_text().splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        env[key.strip()] = value.strip()
    return env


def load_env_optional() -> dict[str, str]:
    """Read root .env if present; return empty dict otherwise."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return {}
    env: dict[str, str] = {}
    for raw in env_file.read_text().splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        env[key.strip()] = value.strip()
    return env


def die(msg: str) -> NoReturn:
    """Print an error message to stderr and exit with code 1."""
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], extra_env: dict[str, str] | None = None) -> None:
    """Run a subprocess command, exit with its return code on failure.

    If extra_env is provided, it is merged with os.environ for the subprocess.
    """
    env = {**os.environ, **extra_env} if extra_env else None
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    process = subprocess.Popen(cmd, cwd=ROOT, env=env, creationflags=creationflags)
    interrupted_once = False
    while True:
        try:
            return_code = process.wait(timeout=0.25)
            break
        except subprocess.TimeoutExpired:
            continue
        except KeyboardInterrupt:
            if not interrupted_once:
                interrupted_once = True
                print(
                    "\nStopping service... (press Ctrl+C again to force kill)",
                    file=sys.stderr,
                )
                _terminate_process_tree(process, force=False)
                continue
            _terminate_process_tree(process, force=True)
            sys.exit(130)
    if return_code != 0:
        sys.exit(return_code)


def _terminate_process_tree(process: subprocess.Popen[bytes], *, force: bool) -> None:
    """Best-effort terminate for a process and all of its descendants."""
    if process.poll() is not None:
        return

    if sys.platform == "win32":
        if force:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        with suppress(Exception):
            process.send_signal(signal.CTRL_BREAK_EVENT)
        deadline = time.monotonic() + 5
        while process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return

    process.send_signal(signal.SIGKILL if force else signal.SIGTERM)
    deadline = time.monotonic() + 3
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.05)
    if process.poll() is None:
        process.kill()


def require_args(args: list[str], count: int, usage: str) -> None:
    """Exit with an error message if fewer than count args are provided."""
    if len(args) < count:
        print(f"Error: missing argument.\nUsage: {usage}", file=sys.stderr)
        sys.exit(1)


def _pg_connect_app_db(
    *,
    host: str,
    port: str,
    user: str,
    password: str,
    db_name: str,
) -> object:
    """Open a connection to the application database."""
    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=db_name,
    )


def _terminate_sessions_on_database(
    *,
    host: str,
    port: str,
    user: str,
    password: str,
    db_name: str,
) -> None:
    """Disconnect other backends using ``db_name`` so ``DROP SCHEMA`` can lock."""
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
        "WHERE datname = %s AND pid <> pg_backend_pid()",
        (db_name,),
    )
    cur.close()
    conn.close()


def _public_base_tables(cursor: object) -> list[str]:
    """Return sorted physical table names in ``public`` (no views)."""
    cursor.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname = %s ORDER BY tablename",
        ("public",),
    )
    return [row[0] for row in cursor.fetchall()]


def cmd_db_create(_args: list[str]) -> None:
    """Create the application database, or reset ``public`` if it already exists."""
    if not _PSYCOPG2_AVAILABLE:
        die("psycopg2 is not installed. Run: .venv/Scripts/pip install psycopg2-binary")

    env = load_env()
    host = env.get("DATABASE_HOST", "localhost")
    port = env.get("DATABASE_PORT", "5432")
    user = env.get("DATABASE_USER", "postgres")
    password = env.get("DATABASE_PASSWORD", "")
    db_name = env.get("DATABASE_NAME")

    if not db_name:
        die("DATABASE_NAME is not set in .env")

    try:
        conn_admin = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres",
        )
    except psycopg2.OperationalError as exc:
        die(f"Could not connect to PostgreSQL: {exc}")

    conn_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur_admin = conn_admin.cursor()
    cur_admin.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    db_exists = cur_admin.fetchone() is not None

    if not db_exists:
        cur_admin.execute(
            pg_sql.SQL("CREATE DATABASE {}").format(pg_sql.Identifier(db_name)),
        )
        print(f"Database '{db_name}' created successfully.")
        cur_admin.close()
        conn_admin.close()
        return

    cur_admin.close()
    conn_admin.close()

    print(
        f"Database '{db_name}' already exists; dropping all objects in schema public...",
    )
    with suppress(psycopg2.Error):
        _terminate_sessions_on_database(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
        )

    try:
        conn_app = _pg_connect_app_db(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
        )
    except psycopg2.OperationalError as exc:
        die(f"Could not connect to database '{db_name}' to reset schema: {exc}")

    conn_app.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur_app = conn_app.cursor()
    cur_app.execute("SET lock_timeout = '120s'")
    try:
        cur_app.execute("DROP SCHEMA public CASCADE")
    except pg_errors.LockNotAvailable as exc:
        die(
            "Timed out waiting for an exclusive lock on schema public (120s). "
            "Another process is still using this database; stop API servers, IDE "
            f"database panels, and other tools using '{db_name}', then retry. ({exc})",
        )
    cur_app.execute("CREATE SCHEMA public")
    cur_app.execute(
        pg_sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(pg_sql.Identifier(user)),
    )
    cur_app.execute("GRANT ALL ON SCHEMA public TO PUBLIC")
    cur_app.close()
    conn_app.close()
    print(
        "Schema public was recreated (all tables removed). Run: pnpm run db:upgrade",
    )


def cmd_db_clean(_args: list[str]) -> None:
    """Truncate every table in ``public`` (keeps schema; destructive)."""
    if not _PSYCOPG2_AVAILABLE:
        die("psycopg2 is not installed. Run: .venv/Scripts/pip install psycopg2-binary")

    env = load_env()
    host = env.get("DATABASE_HOST", "localhost")
    port = env.get("DATABASE_PORT", "5432")
    user = env.get("DATABASE_USER", "postgres")
    password = env.get("DATABASE_PASSWORD", "")
    db_name = env.get("DATABASE_NAME")

    if not db_name:
        die("DATABASE_NAME is not set in .env")

    try:
        conn = _pg_connect_app_db(
            host=host,
            port=port,
            user=user,
            password=password,
            db_name=db_name,
        )
    except psycopg2.OperationalError as exc:
        die(f"Could not connect to database '{db_name}': {exc}")

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    tables = _public_base_tables(cursor)
    if not tables:
        print("No tables in schema public; nothing to clean.")
        cursor.close()
        conn.close()
        return

    truncate_sql = pg_sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE").format(
        pg_sql.SQL(", ").join(
            pg_sql.Identifier("public", table_name) for table_name in tables
        ),
    )
    cursor.execute(truncate_sql)
    cursor.close()
    conn.close()
    print(f"Truncated {len(tables)} table(s) in '{db_name}'.")


def cmd_db_make(args: list[str]) -> None:
    """Generate a new Alembic migration file from model changes."""
    require_args(args, 1, 'pnpm run db:make "migration name"')
    run([ALEMBIC, "revision", "--autogenerate", "-m", args[0]])


def cmd_db_upgrade(_args: list[str]) -> None:
    """Apply all pending migrations to the database."""
    run([ALEMBIC, "upgrade", "head"])


def _cmd_pnpm_app(app_relative_dir: str, args: list[str], usage: str) -> None:
    """Run ``pnpm run`` for a workspace app under ``apps/``."""
    require_args(args, 1, usage)
    run([PNPM, "--dir", app_relative_dir, "run", *args], extra_env=load_env_optional())


def cmd_app_web(args: list[str]) -> None:
    """Run a pnpm script inside apps/web (Vite default port 5173)."""
    _cmd_pnpm_app(
        "apps/web",
        args,
        usage="pnpm run app:web <script>  e.g. pnpm run app:web dev",
    )


def cmd_service_api(_args: list[str]) -> None:
    """Start the FastAPI development server.

    Injects root .env so the API uses the same config as db scripts.
    """
    run(
        [
            str(VENV_BIN / "uvicorn"),
            "src.services.api.app:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        extra_env=load_env_optional(),
    )


COMMANDS: dict[str, object] = {
    "db:create": cmd_db_create,
    "db:clean": cmd_db_clean,
    "db:make": cmd_db_make,
    "db:upgrade": cmd_db_upgrade,
    "app:web": cmd_app_web,
    "service:api": cmd_service_api,
}


def main() -> None:
    """Parse the command name and delegate to the matching handler."""
    if len(sys.argv) < 2:
        print("Available commands:", file=sys.stderr)
        for name in COMMANDS:
            print(f"  {name}", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    extra_args = sys.argv[2:]

    handler = COMMANDS.get(command)
    if handler is None:
        print(f"Error: unknown command '{command}'", file=sys.stderr)
        print("Available commands:", file=sys.stderr)
        for name in COMMANDS:
            print(f"  {name}", file=sys.stderr)
        sys.exit(1)

    handler(extra_args)  # type: ignore[call-arg]


if __name__ == "__main__":
    main()
