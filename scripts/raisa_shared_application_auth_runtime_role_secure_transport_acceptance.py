"""Disposable PostgreSQL acceptance for the shared-auth secure transport.

The runner creates one uniquely named loopback database and one cluster-scoped
NOLOGIN capability role, exercises the real FastAPI router through that role,
and removes both. It records neither target name, database URL nor raw opaque
value in its evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Iterable

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.routers.application_auth import (  # noqa: E402
    AUTHENTICATION_FAILED,
    AUTHENTICATION_UNAVAILABLE,
    REQUEST_NOT_ADMITTED,
    get_application_auth_operational_hardening,
    get_application_auth_transport,
    router,
)
from app.services.application_auth_database_role import (  # noqa: E402
    AUDIT_SEQUENCE,
    AUDIT_TABLE,
    RESOLVER_SIGNATURE,
    STATE_TABLES,
    create_runtime_role_statements,
    drop_runtime_role_statement,
)
from app.services.application_auth_role_runtime import (  # noqa: E402
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (  # noqa: E402
    Surface,
    SyntheticPrincipal,
    pkce_s256_challenge,
)
from app.services.application_auth_transport import (  # noqa: E402
    ApplicationAuthTransport,
    CSRF_COOKIE_NAME,
    OneUseSyntheticBootstrapRegistry,
    SESSION_COOKIE_NAME,
)
from app.services.application_auth_operational_hardening import (  # noqa: E402
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
    TransportDenialEvent,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-runtime-role-secure-transport"
    / "live-local-backend-postgres-transport-evidence.json"
)
DATABASE_NAME_PATTERN = re.compile(
    r"^emr4_auth_transport_acceptance_[0-9a-f]{12}$"
)
ROLE_NAME_PATTERN = re.compile(
    r"^emr4_application_auth_runtime_[0-9a-f]{12}$"
)
DEFAULT_DATABASE_URL = (
    "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
)
PARENT_HEAD = "o4p5q6r7s8t9"
MIGRATION_HEAD = "p5q6r7s8t9u0"
TABLE_NAMES = (*STATE_TABLES, AUDIT_TABLE)
SURFACE_ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online.synthetic.invalid",
    Surface.NATIVE_DIARY: "https://diary.synthetic.invalid",
}
FIXED_NOW = datetime(2026, 8, 1, 2, 0, tzinfo=timezone.utc)


class AcceptanceFailure(RuntimeError):
    """Bounded acceptance failure that never contains a secret or target URL."""


class RecordingTokenSource:
    """Thread-safe opaque source retained only for the in-process raw scan."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._values: list[str] = []

    def __call__(self, _kind: str) -> str:
        value = secrets.token_urlsafe(32)
        with self._lock:
            self._values.append(value)
        return value

    def values(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._values)


class RecordingCsrfSource:
    def __init__(self) -> None:
        self._lock = Lock()
        self._values: list[str] = []

    def __call__(self) -> str:
        value = secrets.token_urlsafe(32)
        with self._lock:
            self._values.append(value)
        return value

    def values(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._values)


def _base_database_url() -> URL:
    target = make_url(os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
    if target.get_backend_name() != "postgresql":
        raise AcceptanceFailure("postgresql_required")
    if target.host not in {"127.0.0.1", "localhost"}:
        raise AcceptanceFailure("loopback_database_required")
    if target.port != 5434:
        raise AcceptanceFailure("expected_local_postgresql_port_required")
    if target.database in {None, "", "postgres"}:
        raise AcceptanceFailure("bounded_source_database_name_required")
    return target


def _database_exists(maintenance: Engine, database_name: str) -> bool:
    with maintenance.connect() as connection:
        return bool(
            connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            ).scalar_one_or_none()
        )


def _role_exists(maintenance: Engine, role_name: str) -> bool:
    with maintenance.connect() as connection:
        return bool(
            connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
                {"name": role_name},
            ).scalar_one_or_none()
        )


def _create_database(maintenance: Engine, database_name: str) -> None:
    if not DATABASE_NAME_PATTERN.fullmatch(database_name):
        raise AcceptanceFailure("unsafe_disposable_database_name")
    if _database_exists(maintenance, database_name):
        raise AcceptanceFailure("disposable_database_preexisted")
    with maintenance.connect() as connection:
        quoted = connection.dialect.identifier_preparer.quote(database_name)
        connection.execute(text(f"CREATE DATABASE {quoted}"))


def _drop_database(maintenance: Engine, database_name: str) -> bool:
    if not DATABASE_NAME_PATTERN.fullmatch(database_name):
        raise AcceptanceFailure("unsafe_disposable_database_cleanup_name")
    with maintenance.connect() as connection:
        connection.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = :name AND pid <> pg_backend_pid()"
            ),
            {"name": database_name},
        )
        if _database_exists(maintenance, database_name):
            quoted = connection.dialect.identifier_preparer.quote(database_name)
            connection.execute(text(f"DROP DATABASE {quoted}"))
    return not _database_exists(maintenance, database_name)


def _drop_role(maintenance: Engine, role_name: str) -> bool:
    if not ROLE_NAME_PATTERN.fullmatch(role_name):
        raise AcceptanceFailure("unsafe_disposable_role_cleanup_name")
    if _role_exists(maintenance, role_name):
        with maintenance.connect() as connection:
            connection.execute(text(drop_runtime_role_statement(role_name)))
    return not _role_exists(maintenance, role_name)


def _run_alembic(target: URL, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = target.render_as_string(hide_password=False)
    return subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        shell=False,
    )


def _require_alembic(target: URL, *arguments: str) -> str:
    completed = _run_alembic(target, *arguments)
    if completed.returncode != 0:
        raise AcceptanceFailure(f"alembic_{arguments[0]}_failed")
    return completed.stdout + completed.stderr


def _apply_role_contract(engine: Engine, role_name: str) -> None:
    with engine.begin() as connection:
        for statement in create_runtime_role_statements(role_name):
            connection.execute(text(statement))


def _role_engine(target: URL, role_name: str) -> Engine:
    if not ROLE_NAME_PATTERN.fullmatch(role_name):
        raise AcceptanceFailure("unsafe_runtime_role_name")
    engine = create_engine(target, pool_pre_ping=True)
    quoted = engine.dialect.identifier_preparer.quote(role_name)

    @event.listens_for(engine, "begin")
    def _set_local_role(connection) -> None:
        connection.exec_driver_sql(f"SET LOCAL ROLE {quoted}")

    return engine


def _session_factory(engine: Engine):
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def create_session() -> Session:
        return factory()

    return create_session


def _privilege_matrix(engine: Engine, role_name: str) -> dict[str, Any]:
    state_positive: dict[str, dict[str, bool]] = {}
    state_forbidden: dict[str, dict[str, bool]] = {}
    forbidden_table_privileges = (
        "DELETE",
        "TRUNCATE",
        "REFERENCES",
        "TRIGGER",
    )
    with engine.connect() as connection:
        role_row = connection.execute(
            text(
                "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
                "rolreplication, rolbypassrls, rolinherit "
                "FROM pg_roles WHERE rolname = :role"
            ),
            {"role": role_name},
        ).one()

        for table_name in STATE_TABLES:
            qualified = f"public.{table_name}"
            state_positive[table_name] = {
                privilege.lower(): bool(
                    connection.execute(
                        text(
                            "SELECT has_table_privilege(:role, :table, :privilege)"
                        ),
                        {
                            "role": role_name,
                            "table": qualified,
                            "privilege": privilege,
                        },
                    ).scalar_one()
                )
                for privilege in ("SELECT", "INSERT", "UPDATE")
            }
            state_forbidden[table_name] = {
                privilege.lower(): bool(
                    connection.execute(
                        text(
                            "SELECT has_table_privilege(:role, :table, :privilege)"
                        ),
                        {
                            "role": role_name,
                            "table": qualified,
                            "privilege": privilege,
                        },
                    ).scalar_one()
                )
                for privilege in forbidden_table_privileges
            }

        audit_positive = {
            privilege.lower(): bool(
                connection.execute(
                    text("SELECT has_table_privilege(:role, :table, :privilege)"),
                    {
                        "role": role_name,
                        "table": f"public.{AUDIT_TABLE}",
                        "privilege": privilege,
                    },
                ).scalar_one()
            )
            for privilege in ("SELECT", "INSERT")
        }
        audit_forbidden = {
            privilege.lower(): bool(
                connection.execute(
                    text("SELECT has_table_privilege(:role, :table, :privilege)"),
                    {
                        "role": role_name,
                        "table": f"public.{AUDIT_TABLE}",
                        "privilege": privilege,
                    },
                ).scalar_one()
            )
            for privilege in (
                "UPDATE",
                "DELETE",
                "TRUNCATE",
                "REFERENCES",
                "TRIGGER",
            )
        }
        schema_usage = bool(
            connection.execute(
                text("SELECT has_schema_privilege(:role, 'public', 'USAGE')"),
                {"role": role_name},
            ).scalar_one()
        )
        schema_create = bool(
            connection.execute(
                text("SELECT has_schema_privilege(:role, 'public', 'CREATE')"),
                {"role": role_name},
            ).scalar_one()
        )
        sequence_positive = {
            privilege.lower(): bool(
                connection.execute(
                    text(
                        "SELECT has_sequence_privilege(:role, :sequence, :privilege)"
                    ),
                    {
                        "role": role_name,
                        "sequence": f"public.{AUDIT_SEQUENCE}",
                        "privilege": privilege,
                    },
                ).scalar_one()
            )
            for privilege in ("USAGE", "SELECT")
        }
        sequence_update = bool(
            connection.execute(
                text(
                    "SELECT has_sequence_privilege(:role, :sequence, 'UPDATE')"
                ),
                {
                    "role": role_name,
                    "sequence": f"public.{AUDIT_SEQUENCE}",
                },
            ).scalar_one()
        )
        resolver_execute = bool(
            connection.execute(
                text(
                    "SELECT has_function_privilege(:role, :resolver, 'EXECUTE')"
                ),
                {"role": role_name, "resolver": RESOLVER_SIGNATURE},
            ).scalar_one()
        )
        product_tables = tuple(
            connection.execute(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = 'public' "
                    "AND tablename <> ALL(:auth_tables) "
                    "ORDER BY tablename"
                ),
                {"auth_tables": list(TABLE_NAMES)},
            ).scalars()
        )
        product_privilege_hits = 0
        for table_name in product_tables:
            if connection.execute(
                text(
                    "SELECT has_any_column_privilege(:role, :table, 'SELECT') "
                    "OR has_table_privilege(:role, :table, "
                    "'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')"
                ),
                {"role": role_name, "table": f"public.{table_name}"},
            ).scalar_one():
                product_privilege_hits += 1

    role_properties = {
        "login": bool(role_row.rolcanlogin),
        "superuser": bool(role_row.rolsuper),
        "createdb": bool(role_row.rolcreatedb),
        "createrole": bool(role_row.rolcreaterole),
        "replication": bool(role_row.rolreplication),
        "bypass_rls": bool(role_row.rolbypassrls),
        "inherit": bool(role_row.rolinherit),
    }
    passed = (
        not any(role_properties.values())
        and schema_usage
        and not schema_create
        and all(all(values.values()) for values in state_positive.values())
        and all(not any(values.values()) for values in state_forbidden.values())
        and all(audit_positive.values())
        and not any(audit_forbidden.values())
        and all(sequence_positive.values())
        and not sequence_update
        and resolver_execute
        and product_privilege_hits == 0
        and len(product_tables) > 0
    )
    return {
        "role_properties": role_properties,
        "state_table_positive_all": all(
            all(values.values()) for values in state_positive.values()
        ),
        "state_table_forbidden_all_false": all(
            not any(values.values()) for values in state_forbidden.values()
        ),
        "audit_positive_all": all(audit_positive.values()),
        "audit_forbidden_all_false": not any(audit_forbidden.values()),
        "schema_usage": schema_usage,
        "schema_create": schema_create,
        "sequence_positive_all": all(sequence_positive.values()),
        "sequence_update": sequence_update,
        "resolver_execute": resolver_execute,
        "product_table_count": len(product_tables),
        "product_privilege_hits": product_privilege_hits,
        "passed": passed,
    }


def _resolver_contract(engine: Engine) -> dict[str, Any]:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT p.prosecdef, p.proconfig, p.provolatile, p.prorows, "
                "pg_get_functiondef(p.oid) AS definition, "
                "has_function_privilege('public', p.oid, 'EXECUTE') AS public_execute "
                "FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
                "WHERE n.nspname = 'public' "
                "AND p.proname = 'emr4_resolve_application_auth_principal'"
            )
        ).one()
    definition = row.definition
    empty_search_path = (
        isinstance(row.proconfig, list)
        and len(row.proconfig) == 1
        and row.proconfig[0].startswith("search_path=")
        and row.proconfig[0].removeprefix("search_path=").strip('"') == ""
    )
    fixed_kinds = all(
        f"'{kind}'" in definition for kind in ("parent", "surface", "exchange")
    )
    passed = (
        row.prosecdef is True
        and empty_search_path
        and row.provolatile == "s"
        and int(row.prorows) == 1
        and row.public_execute is False
        and fixed_kinds
        and "^sha256:[0-9a-f]{64}$" in definition
        and "LIMIT 1" in definition
    )
    return {
        "security_definer": bool(row.prosecdef),
        "empty_search_path": empty_search_path,
        "stable": row.provolatile == "s",
        "rows_one": int(row.prorows) == 1,
        "public_execute": bool(row.public_execute),
        "fixed_kind_allowlist": fixed_kinds,
        "hash_bounded": "^sha256:[0-9a-f]{64}$" in definition,
        "limit_one": "LIMIT 1" in definition,
        "passed": passed,
    }


def _table_counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as connection:
        return {
            table_name: int(
                connection.execute(
                    text(f'SELECT count(*) FROM "{table_name}"')
                ).scalar_one()
            )
            for table_name in TABLE_NAMES
        }


def _force_audit_outage(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE FUNCTION emr4_auth_transport_force_audit_outage()
                RETURNS trigger LANGUAGE plpgsql AS $$
                BEGIN
                  RAISE EXCEPTION 'acceptance audit outage' USING ERRCODE = '55000';
                END
                $$
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE TRIGGER trg_emr4_auth_transport_force_audit_outage
                BEFORE INSERT ON application_auth_audit_events
                FOR EACH ROW
                EXECUTE FUNCTION emr4_auth_transport_force_audit_outage()
                """
            )
        )


def _remove_audit_outage(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "DROP TRIGGER IF EXISTS "
                "trg_emr4_auth_transport_force_audit_outage "
                "ON application_auth_audit_events"
            )
        )
        connection.execute(
            text("DROP FUNCTION IF EXISTS emr4_auth_transport_force_audit_outage()")
        )


def _hash_reference(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _role_scope_probe(
    role_engine: Engine,
    *,
    surface_value: str,
    own_practice: str,
    foreign_practice: str,
) -> dict[str, Any]:
    with role_engine.begin() as connection:
        effective_role = connection.execute(text("SELECT current_user")).scalar_one()
        no_context_counts = {
            table_name: int(
                connection.execute(
                    text(f'SELECT count(*) FROM "{table_name}"')
                ).scalar_one()
            )
            for table_name in TABLE_NAMES
        }
        resolved = connection.execute(
            text(
                "SELECT user_ref, practice_ref "
                "FROM public.emr4_resolve_application_auth_principal("
                "'surface', :reference_hash)"
            ),
            {"reference_hash": _hash_reference(surface_value)},
        ).all()
        invalid_kind = connection.execute(
            text(
                "SELECT count(*) FROM "
                "public.emr4_resolve_application_auth_principal("
                "'invalid', :reference_hash)"
            ),
            {"reference_hash": _hash_reference(surface_value)},
        ).scalar_one()
        invalid_hash = connection.execute(
            text(
                "SELECT count(*) FROM "
                "public.emr4_resolve_application_auth_principal("
                "'surface', 'not-a-hash')"
            )
        ).scalar_one()
        connection.execute(
            text("SELECT set_config('app.current_practice_ref', :practice, true)"),
            {"practice": own_practice},
        )
        own_counts = {
            table_name: int(
                connection.execute(
                    text(f'SELECT count(*) FROM "{table_name}"')
                ).scalar_one()
            )
            for table_name in TABLE_NAMES
        }
        connection.execute(
            text("SELECT set_config('app.current_practice_ref', :practice, true)"),
            {"practice": foreign_practice},
        )
        foreign_context_counts = {
            table_name: int(
                connection.execute(
                    text(f'SELECT count(*) FROM "{table_name}"')
                ).scalar_one()
            )
            for table_name in TABLE_NAMES
        }
        foreign_context_own_rows = {
            table_name: int(
                connection.execute(
                    text(
                        f'SELECT count(*) FROM "{table_name}" '
                        "WHERE practice_ref = :own_practice"
                    ),
                    {"own_practice": own_practice},
                ).scalar_one()
            )
            for table_name in TABLE_NAMES
        }
    passed = (
        isinstance(effective_role, str)
        and effective_role.startswith("emr4_application_auth_runtime_")
        and all(value == 0 for value in no_context_counts.values())
        and len(resolved) == 1
        and resolved[0].practice_ref == own_practice
        and int(invalid_kind) == 0
        and int(invalid_hash) == 0
        and all(value > 0 for value in own_counts.values())
        and sum(value > 0 for value in foreign_context_counts.values()) >= 4
        and all(value == 0 for value in foreign_context_own_rows.values())
    )
    return {
        "effective_role_matches": isinstance(effective_role, str)
        and effective_role.startswith("emr4_application_auth_runtime_"),
        "no_context_all_zero": all(
            value == 0 for value in no_context_counts.values()
        ),
        "valid_reference_result_count": len(resolved),
        "valid_reference_practice_matches": bool(resolved)
        and resolved[0].practice_ref == own_practice,
        "invalid_kind_result_count": int(invalid_kind),
        "invalid_hash_result_count": int(invalid_hash),
        "own_context_nonzero_tables": sum(
            value > 0 for value in own_counts.values()
        ),
        "foreign_context_nonzero_tables": sum(
            value > 0 for value in foreign_context_counts.values()
        ),
        "foreign_context_own_rows_all_zero": all(
            value == 0 for value in foreign_context_own_rows.values()
        ),
        "passed": passed,
    }


def _cookie_headers(response) -> list[str]:
    return response.headers.get_list("set-cookie")


def _response_cookie_value(response, name: str) -> str | None:
    for header in _cookie_headers(response):
        if header.startswith(f"{name}="):
            return header.split(";", 1)[0].split("=", 1)[1].strip('"')
    return None


def _cookies_exact(headers: Iterable[str], *, deleted: bool = False) -> bool:
    bounded = tuple(headers)
    expected_names = {SESSION_COOKIE_NAME, CSRF_COOKIE_NAME}
    observed_names = {header.split("=", 1)[0] for header in bounded}
    if observed_names != expected_names:
        return False
    for header in bounded:
        lowered = header.lower()
        required = (
            "secure",
            "httponly",
            "partitioned",
            "path=/",
            "samesite=none",
        )
        if not all(value in lowered for value in required):
            return False
        if "domain=" in lowered:
            return False
        if deleted and not ("max-age=0" in lowered and "expires=" in lowered):
            return False
    return True


def _generic(response, status_code: int, detail: str) -> bool:
    return (
        response.status_code == status_code
        and response.json() == {"detail": detail}
        and response.headers.get("cache-control") == "no-store"
        and response.headers.get("pragma") == "no-cache"
        and response.headers.get("referrer-policy") == "no-referrer"
    )


def _principal(suffix: str, practice: str) -> SyntheticPrincipal:
    return SyntheticPrincipal(
        user_id=f"synthetic-user-{suffix}",
        practice_id=f"synthetic-practice-{practice}",
        current_backend_role="GP",
        practitioner_id=f"synthetic-practitioner-{suffix}",
    )


def _new_client(application: FastAPI, surface: Surface) -> TestClient:
    return TestClient(
        application,
        base_url=SURFACE_ORIGINS[surface],
        client=("127.0.0.1", 50000),
    )


class _AcceptanceDenialSink:
    def __init__(self) -> None:
        self.events: list[TransportDenialEvent] = []

    def record(self, event: TransportDenialEvent) -> None:
        self.events.append(event)


def _issue_csrf(client: TestClient, surface: Surface) -> str:
    response = client.post(
        "/api/v1/application-auth/csrf",
        headers={"Origin": SURFACE_ORIGINS[surface]},
        json={"surface": surface.value},
    )
    if response.status_code != 200:
        raise AcceptanceFailure("csrf_issue_failed")
    return str(response.json()["csrf_token"])


def _exercise_transport(
    *,
    owner_engine: Engine,
    role_engine: Engine,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    token_source = RecordingTokenSource()
    csrf_source = RecordingCsrfSource()
    bootstrap_word = secrets.token_urlsafe(32)
    bootstrap_foreign = secrets.token_urlsafe(32)
    bootstrap_outage = secrets.token_urlsafe(32)
    principal = _principal("alpha", "alpha")
    foreign_principal = _principal("beta", "beta")
    runtime = RoleScopedPostgresApplicationAuthRuntime(
        session_factory=_session_factory(role_engine),
        surface_origins=SURFACE_ORIGINS,
        clock=lambda: FIXED_NOW,
        token_source=token_source,
    )
    registry = OneUseSyntheticBootstrapRegistry(
        {
            bootstrap_word: principal,
            bootstrap_foreign: foreign_principal,
            bootstrap_outage: _principal("outage", "outage"),
        }
    )
    transport = ApplicationAuthTransport(
        runtime=runtime,
        bootstrap_registry=registry,
        surface_origins=SURFACE_ORIGINS,
        csrf_token_source=csrf_source,
    )
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: ApplicationAuthOperationalHardening(
        proxy_policy=ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=10_000,
            max_keys=8,
        ),
        denial_audit_sink=_AcceptanceDenialSink(),
        client_hmac_key=b"authored-synthetic-acceptance-key",
        clock=lambda: FIXED_NOW,
    )
    application.dependency_overrides[get_application_auth_transport] = (
        lambda: transport
    )

    origin_denials: list[bool] = []
    with _new_client(application, Surface.WORD_ONLINE) as word:
        for bad_origin in (
            None,
            "null",
            "http://word-online.synthetic.invalid",
            SURFACE_ORIGINS[Surface.WORD_ONLINE] + "/path",
            "https://foreign.synthetic.invalid",
        ):
            headers = {} if bad_origin is None else {"Origin": bad_origin}
            denied = word.post(
                "/api/v1/application-auth/csrf",
                headers=headers,
                json={"surface": Surface.WORD_ONLINE.value},
            )
            origin_denials.append(
                _generic(denied, 403, REQUEST_NOT_ADMITTED)
                and not _cookie_headers(denied)
            )

        csrf = _issue_csrf(word, Surface.WORD_ONLINE)
        missing_csrf = word.post(
            "/api/v1/application-auth/synthetic/session",
            headers={"Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE]},
            json={
                "surface": Surface.WORD_ONLINE.value,
                "bootstrap_credential": bootstrap_word,
            },
        )
        csrf_denial_passed = _generic(
            missing_csrf, 403, REQUEST_NOT_ADMITTED
        ) and not _cookie_headers(missing_csrf)

        login = word.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": csrf,
            },
            json={
                "surface": Surface.WORD_ONLINE.value,
                "bootstrap_credential": bootstrap_word,
                "correlation_id": "correlation-transport-login",
            },
        )
        old_surface = _response_cookie_value(login, SESSION_COOKIE_NAME)
        active_csrf = str(login.json().get("csrf_token", ""))
        login_passed = (
            login.status_code == 200
            and isinstance(old_surface, str)
            and old_surface not in login.text
            and "parent" not in login.text
            and _cookies_exact(_cookie_headers(login))
        )

        replay_csrf = _issue_csrf(word, Surface.WORD_ONLINE)
        replay = word.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": replay_csrf,
            },
            json={
                "surface": Surface.WORD_ONLINE.value,
                "bootstrap_credential": bootstrap_word,
            },
        )
        bootstrap_replay_passed = _generic(
            replay, 401, AUTHENTICATION_FAILED
        ) and not _cookie_headers(replay)

        active_csrf = _issue_csrf(word, Surface.WORD_ONLINE)
        assert old_surface is not None
        validated = word.post(
            "/api/v1/application-auth/session/validate",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": active_csrf,
            },
            json={"surface": Surface.WORD_ONLINE.value},
        )
        validate_passed = (
            validated.status_code == 200
            and validated.json().get("current_backend_role") == "GP"
            and validated.json().get("authority_source") == "emr4_backend"
            and "synthetic-user" not in validated.text
            and "synthetic-practice" not in validated.text
        )

        rotated = word.post(
            "/api/v1/application-auth/session/rotate",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": active_csrf,
            },
            json={"surface": Surface.WORD_ONLINE.value},
        )
        replacement_surface = _response_cookie_value(rotated, SESSION_COOKIE_NAME)
        rotated_csrf = str(rotated.json().get("csrf_token", ""))
        rotate_passed = (
            rotated.status_code == 200
            and isinstance(replacement_surface, str)
            and replacement_surface != old_surface
            and replacement_surface not in rotated.text
            and _cookies_exact(_cookie_headers(rotated))
        )

        state = secrets.token_urlsafe(24)
        nonce = secrets.token_urlsafe(24)
        verifier = secrets.token_urlsafe(32)
        challenge = pkce_s256_challenge(verifier)
        issued = word.post(
            "/api/v1/application-auth/exchange/issue",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": rotated_csrf,
            },
            json={
                "source_surface": Surface.WORD_ONLINE.value,
                "target_surface": Surface.NATIVE_DIARY.value,
                "target_origin": SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                "state": state,
                "nonce": nonce,
                "pkce_challenge": challenge,
            },
        )
        exchange_code = str(issued.json().get("exchange_code", ""))
        issue_passed = (
            issued.status_code == 200
            and exchange_code
            and set(issued.json())
            == {"exchange_code", "target_surface", "expires_at"}
            and not _cookie_headers(issued)
        )

    with _new_client(application, Surface.WORD_ONLINE) as old_client:
        old_denied = old_client.post(
            "/api/v1/application-auth/session/validate",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": rotated_csrf,
                "Cookie": (
                    f"{SESSION_COOKIE_NAME}={old_surface}; "
                    f"{CSRF_COOKIE_NAME}={rotated_csrf}"
                ),
            },
            json={"surface": Surface.WORD_ONLINE.value},
        )
        old_rotation_denied = _generic(
            old_denied, 401, AUTHENTICATION_FAILED
        )

    with _new_client(application, Surface.NATIVE_DIARY) as diary:
        diary_csrf = _issue_csrf(diary, Surface.NATIVE_DIARY)
        binding_denials = []
        for field, wrong_value in (
            ("source_origin", "https://wrong-source.synthetic.invalid"),
            ("state", state + "-wrong"),
            ("nonce", nonce + "-wrong"),
            ("pkce_verifier", secrets.token_urlsafe(32)),
        ):
            payload = {
                "exchange_code": exchange_code,
                "source_surface": Surface.WORD_ONLINE.value,
                "target_surface": Surface.NATIVE_DIARY.value,
                "source_origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "state": state,
                "nonce": nonce,
                "pkce_verifier": verifier,
            }
            payload[field] = wrong_value
            denied = diary.post(
                "/api/v1/application-auth/exchange/redeem",
                headers={
                    "Origin": SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                    "X-EMR4-CSRF": diary_csrf,
                },
                json=payload,
            )
            binding_denials.append(
                _generic(denied, 401, AUTHENTICATION_FAILED)
                and not _cookie_headers(denied)
            )

        redeemed = diary.post(
            "/api/v1/application-auth/exchange/redeem",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                "X-EMR4-CSRF": diary_csrf,
            },
            json={
                "exchange_code": exchange_code,
                "source_surface": Surface.WORD_ONLINE.value,
                "target_surface": Surface.NATIVE_DIARY.value,
                "source_origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "state": state,
                "nonce": nonce,
                "pkce_verifier": verifier,
            },
        )
        target_surface = _response_cookie_value(redeemed, SESSION_COOKIE_NAME)
        target_csrf = str(redeemed.json().get("csrf_token", ""))
        redeem_passed = (
            redeemed.status_code == 200
            and isinstance(target_surface, str)
            and target_surface not in redeemed.text
            and _cookies_exact(_cookie_headers(redeemed))
        )
        replay = diary.post(
            "/api/v1/application-auth/exchange/redeem",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                "X-EMR4-CSRF": target_csrf,
            },
            json={
                "exchange_code": exchange_code,
                "source_surface": Surface.WORD_ONLINE.value,
                "target_surface": Surface.NATIVE_DIARY.value,
                "source_origin": SURFACE_ORIGINS[Surface.WORD_ONLINE],
                "state": state,
                "nonce": nonce,
                "pkce_verifier": verifier,
            },
        )
        exchange_replay_passed = _generic(
            replay, 401, AUTHENTICATION_FAILED
        ) and not _cookie_headers(replay)

        logout = diary.post(
            "/api/v1/application-auth/session/logout",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                "X-EMR4-CSRF": target_csrf,
            },
            json={"surface": Surface.NATIVE_DIARY.value},
        )
        logout_passed = (
            logout.status_code == 204
            and logout.content == b""
            and _cookies_exact(_cookie_headers(logout), deleted=True)
        )

    with _new_client(application, Surface.NATIVE_DIARY) as logged_out:
        post_logout = logged_out.post(
            "/api/v1/application-auth/session/validate",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                "X-EMR4-CSRF": target_csrf,
                "Cookie": (
                    f"{SESSION_COOKIE_NAME}={target_surface}; "
                    f"{CSRF_COOKIE_NAME}={target_csrf}"
                ),
            },
            json={"surface": Surface.NATIVE_DIARY.value},
        )
        post_logout_denied = _generic(
            post_logout, 401, AUTHENTICATION_FAILED
        )

    with _new_client(application, Surface.WORD_DESKTOP) as foreign:
        foreign_csrf = _issue_csrf(foreign, Surface.WORD_DESKTOP)
        foreign_login = foreign.post(
            "/api/v1/application-auth/synthetic/session",
            headers={
                "Origin": SURFACE_ORIGINS[Surface.WORD_DESKTOP],
                "X-EMR4-CSRF": foreign_csrf,
            },
            json={
                "surface": Surface.WORD_DESKTOP.value,
                "bootstrap_credential": bootstrap_foreign,
            },
        )
        foreign_login_passed = (
            foreign_login.status_code == 200
            and _cookies_exact(_cookie_headers(foreign_login))
        )

    before_outage = _table_counts(owner_engine)
    _force_audit_outage(owner_engine)
    try:
        with _new_client(application, Surface.WORD_DESKTOP) as outage:
            outage_csrf = _issue_csrf(outage, Surface.WORD_DESKTOP)
            failed = outage.post(
                "/api/v1/application-auth/synthetic/session",
                headers={
                    "Origin": SURFACE_ORIGINS[Surface.WORD_DESKTOP],
                    "X-EMR4-CSRF": outage_csrf,
                },
                json={
                    "surface": Surface.WORD_DESKTOP.value,
                    "bootstrap_credential": bootstrap_outage,
                },
            )
            audit_failure_response = _generic(
                failed, 503, AUTHENTICATION_UNAVAILABLE
            ) and not _cookie_headers(failed)
    finally:
        _remove_audit_outage(owner_engine)
    after_outage = _table_counts(owner_engine)
    audit_atomicity = {
        "response_generic_503": audit_failure_response,
        "state_and_audit_unchanged": before_outage == after_outage,
        "bootstrap_released": registry.state_counts()["available"] == 1,
    }
    audit_atomicity["passed"] = all(audit_atomicity.values())

    raw_values = (
        bootstrap_word,
        bootstrap_foreign,
        bootstrap_outage,
        state,
        nonce,
        verifier,
        *token_source.values(),
        *csrf_source.values(),
    )
    scope_probe = _role_scope_probe(
        role_engine,
        surface_value=str(replacement_surface),
        own_practice=principal.practice_id,
        foreign_practice=foreign_principal.practice_id,
    )
    result = {
        "origin_matrix": {
            "invalid_case_count": len(origin_denials),
            "all_generic_403": all(origin_denials),
        },
        "csrf_matrix": {
            "missing_or_mismatched_fails_before_runtime": csrf_denial_passed,
        },
        "lifecycle": {
            "login_passed": login_passed,
            "bootstrap_replay_generic_401": bootstrap_replay_passed,
            "validate_passed": validate_passed,
            "rotate_passed": rotate_passed,
            "old_surface_denied_after_rotation": old_rotation_denied,
            "issue_passed": issue_passed,
            "binding_denials_generic_401": all(binding_denials),
            "redeem_passed": redeem_passed,
            "exchange_replay_generic_401": exchange_replay_passed,
            "logout_passed": logout_passed,
            "old_surface_denied_after_logout": post_logout_denied,
            "foreign_practice_fixture_created": foreign_login_passed,
        },
        "audit_atomicity": audit_atomicity,
        "role_scope": scope_probe,
    }
    result["passed"] = (
        result["origin_matrix"]["all_generic_403"]
        and result["csrf_matrix"]["missing_or_mismatched_fails_before_runtime"]
        and all(result["lifecycle"].values())
        and audit_atomicity["passed"]
        and scope_probe["passed"]
    )
    return result, tuple(dict.fromkeys(raw_values))


def _raw_persistence_scan(
    engine: Engine,
    raw_values: Iterable[str],
) -> dict[str, Any]:
    values = tuple(raw_values)
    matches = 0
    scanned_rows = 0
    with engine.connect() as connection:
        for table_name in TABLE_NAMES:
            rows = connection.execute(
                text(f'SELECT row_to_json(row_value)::text FROM "{table_name}" row_value')
            ).scalars()
            for serialized in rows:
                scanned_rows += 1
                matches += sum(value in serialized for value in values)
    return {
        "raw_value_count": len(values),
        "scanned_table_count": len(TABLE_NAMES),
        "scanned_row_count": scanned_rows,
        "matched_raw_value_count": matches,
        "passed": matches == 0,
    }


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    database_name = f"emr4_auth_transport_acceptance_{secrets.token_hex(6)}"
    role_name = f"emr4_application_auth_runtime_{secrets.token_hex(6)}"
    if not DATABASE_NAME_PATTERN.fullmatch(database_name):
        raise AcceptanceFailure("generated_database_name_invalid")
    if not ROLE_NAME_PATTERN.fullmatch(role_name):
        raise AcceptanceFailure("generated_role_name_invalid")

    base = _base_database_url()
    target = base.set(database=database_name)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner_engine: Engine | None = None
    role_engine: Engine | None = None
    database_created = False
    role_created = False
    failure_type: str | None = None
    evidence: dict[str, Any] = {
        "schema_version": (
            "raisa.shared-auth-runtime-role-secure-transport.evidence.v1"
        ),
        "result": "revision_required",
        "evidence_label": "live_local_backend_postgres_transport",
        "data_class": "authored_synthetic",
        "database": {
            "name_recorded": False,
            "unique_allowlisted_name_used": True,
            "loopback_only": True,
            "preexisting": False,
        },
        "role": {
            "name_recorded": False,
            "unique_allowlisted_name_used": True,
            "preexisting": False,
        },
        "cleanup": {
            "database_drop_attempted": False,
            "role_drop_attempted": False,
            "database_absent_after": False,
            "role_absent_after": False,
        },
    }
    raw_values: tuple[str, ...] = ()
    try:
        if _role_exists(maintenance, role_name):
            raise AcceptanceFailure("disposable_role_preexisted")
        _create_database(maintenance, database_name)
        database_created = True

        _require_alembic(target, "upgrade", PARENT_HEAD)
        upgrade = _require_alembic(target, "upgrade", "head")
        current = _require_alembic(target, "current")
        _require_alembic(target, "downgrade", PARENT_HEAD)
        _require_alembic(target, "upgrade", "head")
        reupgraded_current = _require_alembic(target, "current")
        drift = _require_alembic(target, "check")
        migration = {
            "parent_revision": PARENT_HEAD,
            "head_revision": MIGRATION_HEAD,
            "parent_to_head_upgrade_passed": bool(upgrade.strip()),
            "current_head_exact": MIGRATION_HEAD in current,
            "downgrade_to_parent_passed": True,
            "reupgrade_passed": MIGRATION_HEAD in reupgraded_current,
            "orm_migration_drift_absent": (
                "No new upgrade operations detected" in drift
            ),
        }
        migration["passed"] = all(
            value for key, value in migration.items() if key.endswith("passed")
        ) and migration["orm_migration_drift_absent"]
        if not migration["passed"]:
            raise AcceptanceFailure("migration_contract_failed")

        owner_engine = create_engine(target, pool_pre_ping=True)
        _apply_role_contract(owner_engine, role_name)
        role_created = True
        privileges = _privilege_matrix(owner_engine, role_name)
        resolver = _resolver_contract(owner_engine)
        evidence.update(
            {
                "migration": migration,
                "privilege_matrix": privileges,
                "resolver": resolver,
            }
        )
        if not privileges["passed"] or not resolver["passed"]:
            raise AcceptanceFailure("role_or_resolver_contract_failed")

        role_engine = _role_engine(target, role_name)
        transport, raw_values = _exercise_transport(
            owner_engine=owner_engine,
            role_engine=role_engine,
        )
        raw_scan = _raw_persistence_scan(owner_engine, raw_values)
        passed = (
            migration["passed"]
            and privileges["passed"]
            and resolver["passed"]
            and transport["passed"]
            and raw_scan["passed"]
        )
        evidence.update(
            {
                "result": (
                    "raisa_shared_application_auth_runtime_role_secure_transport_pass"
                    if passed
                    else "revision_required"
                ),
                "migration": migration,
                "privilege_matrix": privileges,
                "resolver": resolver,
                "transport": transport,
                "raw_secret_scan": raw_scan,
                "side_effect_counts": {
                    "database_migrations_disposable": 4,
                    "database_reads_disposable": "performed",
                    "database_writes_disposable": "performed",
                    "provider_calls": 0,
                    "external_identity_calls": 0,
                    "microsoft_office_identity_calls": 0,
                    "cloud_or_iam_mutations": 0,
                    "product_data_reads": 0,
                    "patient_or_clinical_field_reads": 0,
                    "appointment_or_arrival_commands": 0,
                    "microphone_captures": 0,
                    "document_mutations": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "No live identity, external federation or product authorization is established.",
                    "Only a uniquely named disposable local authored-synthetic PostgreSQL database and NOLOGIN capability role were exercised.",
                    "Office compatibility, rate limiting, deployment, production and release remain unproved and closed.",
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        evidence_scan_matches = sum(value in serialized for value in raw_values)
        evidence["raw_secret_scan"]["evidence_artifact_match_count"] = (
            evidence_scan_matches
        )
        evidence["raw_secret_scan"]["evidence_artifact_passed"] = (
            evidence_scan_matches == 0
        )
        if evidence_scan_matches:
            evidence["result"] = "revision_required"
            raise AcceptanceFailure("raw_value_in_evidence")
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
    finally:
        if role_engine is not None:
            role_engine.dispose()
        if owner_engine is not None:
            owner_engine.dispose()
        if database_created:
            evidence["cleanup"]["database_drop_attempted"] = True
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance, database_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_cleanup_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = not _database_exists(
                maintenance, database_name
            )
        if role_created:
            evidence["cleanup"]["role_drop_attempted"] = True
            try:
                evidence["cleanup"]["role_absent_after"] = _drop_role(
                    maintenance, role_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["role_cleanup_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["role_absent_after"] = not _role_exists(
                maintenance, role_name
            )
        maintenance.dispose()

    evidence["cleanup"]["passed"] = bool(
        evidence["cleanup"]["database_absent_after"]
        and evidence["cleanup"]["role_absent_after"]
    )
    if not evidence["cleanup"]["passed"]:
        evidence["result"] = "revision_required"
    evidence["passed"] = (
        evidence["result"]
        == "raisa_shared_application_auth_runtime_role_secure_transport_pass"
        and evidence["cleanup"]["passed"]
        and failure_type is None
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    evidence = run_acceptance(output_path=args.output)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "passed": evidence["passed"],
                "cleanup_passed": evidence["cleanup"]["passed"],
                "failure_type": evidence.get("failure_type"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
