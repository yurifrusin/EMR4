"""Prove Alembic head on a disposable, genuinely empty PostgreSQL database."""

from __future__ import annotations

from pathlib import Path
import re
import secrets
import sys

import psycopg2
from psycopg2 import sql
from sqlalchemy.engine import make_url

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import settings
from scripts.verification_runtime import (
    TIMEOUT_SECONDS,
    VerificationCommand,
    run_command,
)


DATABASE_NAME_RE = re.compile(r"^emr4_migration_verify_[0-9a-f]{16}$")


def _connection_url(database_name: str) -> str:
    url = make_url(settings.database_url)
    if not url.drivername.startswith("postgresql"):
        raise ValueError("empty-database migration verification requires PostgreSQL")
    return url.set(database=database_name).render_as_string(hide_password=False)


def _create_database(admin_url: str, database_name: str) -> None:
    if not DATABASE_NAME_RE.fullmatch(database_name):
        raise ValueError("refusing unsafe disposable database name")
    connection = psycopg2.connect(admin_url)
    try:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
            )
    finally:
        connection.close()


def _drop_database(admin_url: str, database_name: str) -> None:
    if not DATABASE_NAME_RE.fullmatch(database_name):
        raise ValueError("refusing unsafe disposable database name")
    connection = psycopg2.connect(admin_url)
    try:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (database_name,),
            )
            cursor.execute(
                sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(database_name)
                )
            )
    finally:
        connection.close()


def _assert_no_user_tables(database_url: str) -> None:
    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' "
                "AND tablename <> 'alembic_version' "
                "ORDER BY tablename"
            )
            tables = [row[0] for row in cursor.fetchall()]
    if tables:
        raise RuntimeError(
            "downgrade-to-base left unexpected user tables: " + ", ".join(tables)
        )


def _run_alembic(label: str, arguments: list[str], database_url: str) -> int:
    return run_command(
        VerificationCommand(
            label=label,
            argv=[sys.executable, "-m", "alembic", *arguments],
            timeout_seconds=TIMEOUT_SECONDS["migration_step"],
        ),
        cwd=REPO_ROOT,
        env={"DATABASE_URL": database_url},
    )


def main() -> int:
    database_name = f"emr4_migration_verify_{secrets.token_hex(8)}"
    admin_url = _connection_url("postgres")
    database_url = _connection_url(database_name)
    created = False
    try:
        _create_database(admin_url, database_name)
        created = True
        print(f"[verify] disposable database created: {database_name}")

        for label, arguments in (
            ("empty database upgrade to head", ["upgrade", "head"]),
            ("empty database model drift check", ["check"]),
            ("empty database downgrade to base", ["downgrade", "base"]),
        ):
            result = _run_alembic(label, arguments, database_url)
            if result:
                return result

        _assert_no_user_tables(database_url)
        print("[pass] downgrade returned the bootstrapped database to no user tables")

        for label, arguments in (
            ("empty database re-upgrade to head", ["upgrade", "head"]),
            ("re-upgraded database model drift check", ["check"]),
        ):
            result = _run_alembic(label, arguments, database_url)
            if result:
                return result
        return 0
    except (OSError, ValueError, RuntimeError, psycopg2.Error) as error:
        print(f"empty-database migration verification failed: {error}", file=sys.stderr)
        return 2
    finally:
        if created:
            try:
                _drop_database(admin_url, database_name)
                print(f"[cleanup] disposable database removed: {database_name}")
            except psycopg2.Error as error:
                print(
                    "failed to remove disposable migration database: "
                    f"{error.__class__.__name__}",
                    file=sys.stderr,
                )


if __name__ == "__main__":
    raise SystemExit(main())
