"""Verify one empty, explicitly owned PostgreSQL migration chain.

The caller must supply a reviewed disposable loopback server and an immutable
source capsule without .env or provider configuration. Importing this module
does not load application settings or database packages.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode


REPO_ROOT = Path(__file__).parents[1]
DATABASE_NAME_RE = re.compile(r"emr4_migration_verify_[0-9a-f]{16}\Z")
ROLE_RE = re.compile(r"[a-z_][a-z0-9_]{0,62}\Z")
SYSTEM_ID_RE = re.compile(r"[1-9][0-9]*\Z")
ADMIN_DATABASE = "postgres"
IDENTITY_SQL = (
    "SELECT (SELECT system_identifier::text FROM pg_control_system()), "
    "current_user, (SELECT oid FROM pg_roles WHERE rolname = current_user), "
    "inet_server_addr()::text, inet_server_port()"
)
DATABASE_SQL = "SELECT oid, datdba FROM pg_database WHERE datname = %s"
PUBLIC_TABLES_SQL = (
    "SELECT tablename FROM pg_tables "
    "WHERE schemaname = 'public' AND tablename <> 'alembic_version' "
    "ORDER BY tablename"
)
LIMIT_SQL = (
    "SELECT set_config('statement_timeout', %s, false), "
    "set_config('lock_timeout', %s, false)"
)


@dataclass(frozen=True)
class MigrationConfig:
    host: str
    port: int
    user: str
    database_name: str
    system_identifier: str
    total_seconds: int = 300
    cleanup_seconds: int = 30
    connect_timeout_seconds: int = 5
    statement_timeout_ms: int = 10000


@dataclass(frozen=True)
class MigrationResult:
    primary_exit_code: int
    cleanup_exit_code: int
    database_created: bool | None
    database_removed: bool | None
    failure_reason: str | None
    cleanup_reason: str | None

    @property
    def exit_code(self) -> int:
        if self.primary_exit_code:
            return self.primary_exit_code
        if self.cleanup_exit_code:
            return self.cleanup_exit_code
        return 0 if self.database_created and self.database_removed else 2


class _Failure(Exception):
    def __init__(self, reason: str, code: int = 2):
        self.reason = reason
        self.code = code
        super().__init__(reason)


@dataclass
class _StatementLimit:
    milliseconds: int


def _positive_number(value: object, maximum: float) -> bool:
    return type(value) is int and 0 < value <= maximum


def validate_config(config: MigrationConfig) -> None:
    """Reject coerced, ambiguous or unbounded target and timing inputs."""
    if type(config) is not MigrationConfig:
        raise ValueError("invalid_config_type")
    if type(config.host) is not str or config.host != "127.0.0.1":
        raise ValueError("invalid_host")
    if type(config.port) is not int or not 1 <= config.port <= 65535:
        raise ValueError("invalid_port")
    if type(config.user) is not str or ROLE_RE.fullmatch(config.user) is None:
        raise ValueError("invalid_user")
    if (type(config.database_name) is not str
            or DATABASE_NAME_RE.fullmatch(config.database_name) is None):
        raise ValueError("invalid_database_name")
    if (type(config.system_identifier) is not str
            or SYSTEM_ID_RE.fullmatch(config.system_identifier) is None
            or len(config.system_identifier) > 20
            or int(config.system_identifier) > 2**64 - 1):
        raise ValueError("invalid_system_identifier")
    if not _positive_number(config.total_seconds, 600):
        raise ValueError("invalid_total_seconds")
    if (not _positive_number(config.cleanup_seconds, 600)
            or config.cleanup_seconds < 5
            or config.cleanup_seconds >= config.total_seconds):
        raise ValueError("invalid_cleanup_seconds")
    if (not _positive_number(config.connect_timeout_seconds, 10)
            or config.connect_timeout_seconds > config.cleanup_seconds):
        raise ValueError("invalid_connect_timeout_seconds")
    if (type(config.statement_timeout_ms) is not int
            or not 1 <= config.statement_timeout_ms <= 10000):
        raise ValueError("invalid_statement_timeout_ms")


def _remaining(deadline: float, reason: str) -> float:
    value = deadline - time.monotonic()
    if value <= 0:
        raise _Failure(reason)
    return value


def _connection_settings(config: MigrationConfig, deadline: float,
                         reason: str) -> tuple[dict, int]:
    # libpq's integer connect timeout has a two-second effective minimum. A
    # shorter requested or remaining interval cannot be represented honestly.
    remaining = _remaining(deadline, reason)
    connect_seconds = math.floor(min(config.connect_timeout_seconds, remaining / 2))
    if connect_seconds < 2:
        raise _Failure(reason)
    statement_ms = min(config.statement_timeout_ms,
                       math.floor((remaining - connect_seconds) * 1000) - 100)
    if statement_ms < 1:
        raise _Failure(reason)
    options = f"-c statement_timeout={statement_ms} -c lock_timeout={statement_ms}"
    return {
        "host": config.host,
        "hostaddr": config.host,
        "port": config.port,
        "user": config.user,
        "connect_timeout": connect_seconds,
        "sslmode": "disable",
        "gssencmode": "disable",
        "passfile": os.devnull,
        "options": options,
    }, statement_ms


def _connect(config: MigrationConfig, database: str, deadline: float,
             reason: str):
    kwargs, initial_limit_ms = _connection_settings(config, deadline, reason)
    kwargs["dbname"] = database
    import psycopg2  # Deferred until configuration and ambient checks succeed.

    connection = psycopg2.connect(**kwargs)
    try:
        connection.autocommit = True
    except Exception:
        connection.close()
        raise
    return connection, _StatementLimit(initial_limit_ms)


def _limit_statement(cursor, config: MigrationConfig, deadline: float,
                     reason: str, installed: _StatementLimit) -> None:
    remaining_ms = math.floor(_remaining(deadline, reason) * 1000)
    # The SET query runs under the prior session limit, including the initial
    # limit installed by libpq startup options. Reserve for both that query
    # and the target statement, rather than timing only the target statement.
    if installed.milliseconds + 100 >= remaining_ms:
        raise _Failure(reason)
    limit_ms = min(config.statement_timeout_ms, installed.milliseconds,
                   remaining_ms - installed.milliseconds - 100)
    if limit_ms < 1:
        raise _Failure(reason)
    cursor.execute(LIMIT_SQL, (str(limit_ms), str(limit_ms)))
    installed.milliseconds = limit_ms
    _ensure_query_budget(deadline, reason, installed)


def _ensure_query_budget(deadline: float, reason: str,
                         installed: _StatementLimit) -> None:
    if installed.milliseconds + 100 > math.floor(_remaining(deadline, reason) * 1000):
        raise _Failure(reason)


def _execute(cursor, query, params, config: MigrationConfig,
             deadline: float, reason: str, installed: _StatementLimit) -> None:
    _limit_statement(cursor, config, deadline, reason, installed)
    _ensure_query_budget(deadline, reason, installed)
    cursor.execute(query, params)


def _identity(cursor, config: MigrationConfig, deadline: float,
              prefix: str, installed: _StatementLimit) -> int:
    _execute(cursor, IDENTITY_SQL, None, config, deadline,
             prefix + "_deadline_exhausted", installed)
    row = cursor.fetchone()
    if (type(row) not in (tuple, list) or len(row) != 5
            or type(row[0]) is not str or type(row[1]) is not str
            or type(row[2]) is not int or row[2] <= 0
            or type(row[3]) is not str or type(row[4]) is not int):
        raise _Failure(prefix + "_identity_unconfirmed")
    if row[0] != config.system_identifier:
        raise _Failure(prefix + "_server_identity_mismatch")
    if row[1] != config.user:
        raise _Failure(prefix + "_role_mismatch")
    if row[3] != config.host or row[4] != config.port:
        raise _Failure(prefix + "_endpoint_mismatch")
    return row[2]


def _database_record(cursor, config: MigrationConfig,
                     deadline: float, reason: str,
                     installed: _StatementLimit) -> tuple[int, int] | None:
    _execute(cursor, DATABASE_SQL, (config.database_name,), config,
             deadline, reason, installed)
    row = cursor.fetchone()
    if row is None:
        return None
    if (type(row) not in (tuple, list) or len(row) != 2
            or type(row[0]) is not int or row[0] <= 0
            or type(row[1]) is not int or row[1] <= 0):
        raise _Failure("database_record_invalid")
    return (row[0], row[1])


def _public_tables(config: MigrationConfig, deadline: float,
                   stage: str) -> None:
    connection, installed = _connect(config, config.database_name, deadline,
                                     "primary_deadline_exhausted")
    try:
        with connection.cursor() as cursor:
            _identity(cursor, config, deadline, "primary", installed)
            _execute(cursor, PUBLIC_TABLES_SQL, None, config, deadline,
                     "primary_deadline_exhausted", installed)
            rows = cursor.fetchall()
            if type(rows) not in (tuple, list) or any(
                    type(row) not in (tuple, list) or len(row) != 1
                    or type(row[0]) is not str for row in rows):
                raise _Failure(stage + "_public_tables_unconfirmed")
            if rows:
                raise _Failure(stage + "_public_user_tables_present")
    finally:
        connection.close()


def _database_url(config: MigrationConfig, deadline: float) -> str:
    kwargs, _ = _connection_settings(config, deadline, "primary_deadline_exhausted")
    query = urlencode({
        "hostaddr": kwargs["hostaddr"],
        "connect_timeout": kwargs["connect_timeout"],
        "sslmode": kwargs["sslmode"],
        "gssencmode": kwargs["gssencmode"],
        "passfile": kwargs["passfile"],
        "options": kwargs["options"],
    })
    return (f"postgresql+psycopg2://{config.user}@{config.host}:{config.port}/"
            f"{config.database_name}?{query}")


def _run_alembic(label: str, arguments: tuple[str, ...],
                 database_url: str, deadline: float) -> int:
    # Import only after explicit target validation and creation. This module
    # preserves the existing direct-child timeout semantics unchanged.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.verification_runtime import (  # noqa: E402
        TIMEOUT_SECONDS, VerificationCommand, run_command,
    )

    remaining = math.floor(_remaining(deadline, "primary_deadline_exhausted"))
    timeout = min(TIMEOUT_SECONDS["migration_step"], remaining)
    if timeout < 1:
        raise _Failure("primary_deadline_exhausted")
    return run_command(
        VerificationCommand(
            label=label,
            argv=[sys.executable, "-I", "-B", "-m", "alembic", "-c",
                  str(REPO_ROOT / "alembic.ini"), *arguments],
            timeout_seconds=timeout,
        ),
        cwd=REPO_ROOT,
        env={"DATABASE_URL": database_url},
    )


def _cleanup(config: MigrationConfig, deadline: float,
             owned: tuple[int, int]) -> tuple[bool, bool]:
    connection, installed = _connect(config, ADMIN_DATABASE, deadline,
                                     "cleanup_deadline_exhausted")
    removed = False
    close_failed = False
    try:
        with connection.cursor() as cursor:
            role_oid = _identity(cursor, config, deadline, "cleanup", installed)
            if role_oid != owned[1]:
                raise _Failure("cleanup_role_oid_mismatch")
            record = _database_record(cursor, config, deadline,
                                      "cleanup_deadline_exhausted", installed)
            if record != owned:
                raise _Failure("cleanup_database_identity_mismatch")
            from psycopg2 import sql  # Deferred and never used for raw caller SQL.

            drop = sql.SQL("DROP DATABASE {}").format(sql.Identifier(config.database_name))
            _limit_statement(cursor, config, deadline,
                             "cleanup_deadline_exhausted", installed)
            _ensure_query_budget(deadline, "cleanup_deadline_exhausted", installed)
            try:
                cursor.execute(drop)
            except Exception as exc:
                raise _Failure("drop_acknowledgement_uncertain") from exc
            try:
                record = _database_record(cursor, config, deadline,
                                          "cleanup_absence_unconfirmed", installed)
            except _Failure:
                raise
            except Exception as exc:
                raise _Failure("cleanup_absence_unconfirmed") from exc
            if record is not None:
                raise _Failure("cleanup_database_still_present")
            removed = True
    finally:
        try:
            connection.close()
        except Exception:
            close_failed = True
    return removed, close_failed


def verify(config: MigrationConfig) -> MigrationResult:
    try:
        validate_config(config)
    except ValueError as exc:
        return MigrationResult(2, 0, False, False, str(exc), None)
    if any(name.upper().startswith("PG") for name in os.environ):
        return MigrationResult(2, 0, False, False, "ambient_pg_override", None)

    start = time.monotonic()
    primary_deadline = start + config.total_seconds - config.cleanup_seconds
    cleanup_deadline = start + config.total_seconds
    created = False
    create_sent = False
    owned: tuple[int, int] | None = None
    primary_code = 0
    failure_reason: str | None = None
    stage = "admin_precondition_failed"
    connection = None
    try:
        connection, installed = _connect(config, ADMIN_DATABASE, primary_deadline,
                                         "primary_deadline_exhausted")
        with connection.cursor() as cursor:
            role_oid = _identity(cursor, config, primary_deadline,
                                 "primary", installed)
            record = _database_record(cursor, config, primary_deadline,
                                      "primary_deadline_exhausted", installed)
            if record is not None:
                raise _Failure("database_already_exists")
            from psycopg2 import sql  # Import after precondition readback.

            create = sql.SQL("CREATE DATABASE {} WITH OWNER {} TEMPLATE template0").format(
                sql.Identifier(config.database_name), sql.Identifier(config.user)
            )
            stage = "create_failed"
            _limit_statement(cursor, config, primary_deadline,
                             "primary_deadline_exhausted", installed)
            _ensure_query_budget(primary_deadline, "primary_deadline_exhausted",
                                 installed)
            create_sent = True
            try:
                cursor.execute(create)
            except Exception as exc:
                raise _Failure("create_acknowledgement_uncertain") from exc
            created = True
            stage = "created_database_unconfirmed"
            record = _database_record(cursor, config, primary_deadline,
                                      "primary_deadline_exhausted", installed)
            if record is None or record[1] != role_oid:
                raise _Failure("created_database_unconfirmed")
            owned = record
        stage = "admin_connection_close_failed"
        connection.close()
        connection = None

        stage = "initial_public_tables_check_failed"
        _public_tables(config, primary_deadline, "initial")
        for label, argv, reason in (
            ("empty database upgrade to head", ("upgrade", "head"), "upgrade_failed"),
            ("empty database model drift check", ("check",), "head_check_failed"),
            ("empty database downgrade to base", ("downgrade", "base"), "downgrade_failed"),
        ):
            stage = reason
            result = _run_alembic(label, argv, _database_url(config, primary_deadline),
                                  primary_deadline)
            if result:
                raise _Failure(reason, result)

        stage = "downgrade_public_tables_check_failed"
        _public_tables(config, primary_deadline, "downgrade")
        for label, argv, reason in (
            ("empty database re-upgrade to head", ("upgrade", "head"),
             "reupgrade_failed"),
            ("re-upgraded database model drift check", ("check",),
             "reupgrade_check_failed"),
        ):
            stage = reason
            result = _run_alembic(label, argv, _database_url(config, primary_deadline),
                                  primary_deadline)
            if result:
                raise _Failure(reason, result)
    except _Failure as exc:
        primary_code, failure_reason = exc.code, exc.reason
    except Exception:
        primary_code, failure_reason = 2, stage
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                if primary_code == 0:
                    primary_code, failure_reason = 2, "admin_connection_close_failed"

    cleanup_code = 0
    cleanup_reason: str | None = None
    removed = False
    if create_sent and not created:
        cleanup_code, cleanup_reason = 3, "create_acknowledgement_uncertain"
    elif created and owned is None:
        cleanup_code, cleanup_reason = 3, "ownership_unconfirmed"
    elif created:
        try:
            removed, close_failed = _cleanup(config, cleanup_deadline, owned)
            if close_failed:
                cleanup_code, cleanup_reason = 3, "cleanup_database_step_failed"
        except _Failure as exc:
            cleanup_code, cleanup_reason = 3, exc.reason
        except Exception:
            cleanup_code, cleanup_reason = 3, "cleanup_database_step_failed"
    return MigrationResult(primary_code, cleanup_code, created, removed,
                           failure_reason, cleanup_reason)


class _QuietArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.exit(2, "invalid_cli_arguments\n")


def _windows_standard_output():
    """Bind Win32 child standard handles to the same CRT fds as Python output."""
    import ctypes
    import msvcrt

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetStdHandle.argtypes = [ctypes.c_uint32]
    kernel.GetStdHandle.restype = ctypes.c_void_p
    kernel.SetStdHandle.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
    kernel.SetStdHandle.restype = ctypes.c_int
    for fd, number in ((1, -11), (2, -12)):
        actual = kernel.GetStdHandle(ctypes.c_uint32(number))
        expected = ctypes.c_void_p(msvcrt.get_osfhandle(fd)).value
        if actual is None or actual != expected:
            raise OSError("noncanonical_standard_handle")
    return kernel, ctypes, msvcrt


def _set_windows_standard_output(windows) -> None:
    kernel, ctypes, msvcrt = windows
    for fd, number in ((1, -11), (2, -12)):
        handle = ctypes.c_void_p(msvcrt.get_osfhandle(fd))
        if not kernel.SetStdHandle(ctypes.c_uint32(number), handle):
            raise OSError("standard_handle_update_failed")


def _quiet_cli_verify(config: MigrationConfig) -> tuple[MigrationResult, str | None]:
    """Suppress Python and inherited child output in this single-thread CLI.

    File descriptors and Windows process standard handles are process-global.
    A reviewed outer supervisor must run this helper without peer threads.
    """
    saved_out = None
    saved_err = None
    null_fd = None
    windows = None
    phase = "setup"
    problem = None
    result = None
    restore_failed = False
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        if os.name == "nt":
            windows = _windows_standard_output()
        saved_out = os.dup(1)
        saved_err = os.dup(2)
        null_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null_fd, 1)
        os.dup2(null_fd, 2)
        if windows is not None:
            _set_windows_standard_output(windows)
        # Redirect Python streams as well as inherited descriptors. This also
        # supports callers that capture Python output without replacing fd1/2.
        with os.fdopen(os.dup(null_fd), "w", encoding="utf-8") as quiet:
            with redirect_stdout(quiet), redirect_stderr(quiet):
                phase = "verify"
                result = verify(config)
    except Exception:
        problem = phase
    finally:
        # Flush while both streams still point to NUL, then restore all
        # available descriptors even if an earlier restoration step failed.
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.flush()
            except Exception:
                restore_failed = True
        for saved, target in ((saved_out, 1), (saved_err, 2)):
            if saved is not None:
                try:
                    os.dup2(saved, target)
                except Exception:
                    restore_failed = True
        if windows is not None and saved_out is not None and saved_err is not None:
            try:
                _set_windows_standard_output(windows)
            except Exception:
                restore_failed = True
        for fd in (saved_out, saved_err, null_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    restore_failed = True
    if problem == "setup":
        return MigrationResult(2, 0, False, False,
                               "cli_output_setup_failed", None), "cli_output_setup_failed"
    if problem == "verify":
        return MigrationResult(2, 3, None, None,
                               "cli_verification_unhandled", "cleanup_unconfirmed"), "cli_verification_unhandled"
    if restore_failed:
        if result.exit_code == 0:
            result = MigrationResult(2, result.cleanup_exit_code,
                                     result.database_created, result.database_removed,
                                     "cli_output_restore_failed", result.cleanup_reason)
        return result, "cli_output_restore_failed"
    return result, None


def main(argv: list[str] | None = None) -> int:
    parser = _QuietArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--user", required=True)
    parser.add_argument("--database-name", required=True)
    parser.add_argument("--system-identifier", required=True)
    parser.add_argument("--total-seconds", type=int, default=300)
    parser.add_argument("--cleanup-seconds", type=int, default=30)
    parser.add_argument("--connect-timeout-seconds", type=int, default=5)
    parser.add_argument("--statement-timeout-ms", type=int, default=10000)
    args = parser.parse_args(argv)
    result, output_issue = _quiet_cli_verify(MigrationConfig(**vars(args)))
    try:
        if output_issue is not None:
            print(output_issue, file=sys.stderr)
        print(json.dumps({**asdict(result), "exit_code": result.exit_code},
                         sort_keys=True))
    except Exception:
        return 2
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
