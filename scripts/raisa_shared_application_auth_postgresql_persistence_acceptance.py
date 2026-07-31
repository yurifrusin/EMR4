"""Disposable PostgreSQL acceptance for shared application-auth persistence.

The runner creates one uniquely named loopback database, proves the reversible
migration and the authored-synthetic persistence boundary, then drops only that
database and verifies its absence.  It never targets the shared development or
test databases and never records a database URL or raw opaque value.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import Barrier, Lock
from typing import Any, Callable, Iterable

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.application_auth import (
    ApplicationAuthAuditEvent,
    ApplicationAuthExchangeGrant,
    ApplicationAuthParentSession,
    ApplicationAuthPrincipalGeneration,
    ApplicationAuthSurfaceSession,
)
from app.services.application_auth_persistence import (
    PostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (
    AuthRuntimeDenied,
    RequiredAuditUnavailable,
    Surface,
    SyntheticPrincipal,
    pkce_s256_challenge,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-postgresql-persistence"
    / "live-local-backend-postgres-evidence.json"
)
DATABASE_NAME_PATTERN = re.compile(
    r"^emr4_auth_persistence_acceptance_[0-9a-f]{12}$"
)
TABLE_NAMES = (
    "application_auth_principal_generations",
    "application_auth_parent_sessions",
    "application_auth_surface_sessions",
    "application_auth_exchange_grants",
    "application_auth_audit_events",
)
MODEL_TABLES = (
    ApplicationAuthPrincipalGeneration,
    ApplicationAuthParentSession,
    ApplicationAuthSurfaceSession,
    ApplicationAuthExchangeGrant,
    ApplicationAuthAuditEvent,
)
MIGRATION_BASE = "n3o4p5q6r7s8"
MIGRATION_HEAD = "o4p5q6r7s8t9"
DEFAULT_DATABASE_URL = (
    "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
)
SURFACE_ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop.synthetic.example",
    Surface.WORD_ONLINE: "https://word-online.synthetic.example",
    Surface.NATIVE_DIARY: "https://diary.synthetic.example",
}
FIXED_NOW = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)


class AcceptanceFailure(RuntimeError):
    """Bounded failure whose message contains no secret or database URL."""


class DeterministicTokenSource:
    """Thread-safe acceptance-only source producing unique opaque entropy."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counter = 0

    def __call__(self, kind: str) -> str:
        with self._lock:
            self._counter += 1
            counter = self._counter
        return f"{kind}-{counter:04d}-{'x' * 48}"


def _base_database_url() -> URL:
    raw = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    target = make_url(raw)
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


def _run_alembic(target: URL, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = target.render_as_string(hide_password=False)
    completed = subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        shell=False,
    )
    return completed


def _require_alembic(target: URL, *arguments: str) -> str:
    completed = _run_alembic(target, *arguments)
    if completed.returncode != 0:
        raise AcceptanceFailure(f"alembic_{arguments[0]}_failed")
    return completed.stdout + completed.stderr


def _session_factory(engine: Engine) -> Callable[[], Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def _runtime(
    factory: Callable[[], Session],
    token_source: DeterministicTokenSource,
) -> PostgresApplicationAuthRuntime:
    return PostgresApplicationAuthRuntime(
        session_factory=factory,
        surface_origins=SURFACE_ORIGINS,
        clock=lambda: FIXED_NOW,
        token_source=token_source,
    )


def _principal(suffix: str, practice_suffix: str = "alpha") -> SyntheticPrincipal:
    return SyntheticPrincipal(
        user_id=f"synthetic-user-{suffix}",
        practice_id=f"synthetic-practice-{practice_suffix}",
        current_backend_role="GP",
        practitioner_id=f"synthetic-practitioner-{suffix}",
    )


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


def _database_error_state(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except DBAPIError as exc:
        original = exc.orig
        return getattr(original, "sqlstate", None) or getattr(
            original, "pgcode", None
        )
    return None


def _raw_secret_scan(engine: Engine, raw_values: Iterable[str]) -> dict[str, Any]:
    persisted: list[str] = []
    with engine.connect() as connection:
        for table_name in TABLE_NAMES:
            persisted.extend(
                str(value)
                for value in connection.execute(
                    text(f'SELECT to_jsonb(t)::text FROM "{table_name}" AS t')
                ).scalars()
            )
    joined = "\n".join(persisted)
    values = tuple(raw_values)
    matched = sum(1 for value in values if value and value in joined)
    return {
        "scanned_table_count": len(TABLE_NAMES),
        "scanned_row_count": len(persisted),
        "raw_value_count": len(values),
        "matched_raw_value_count": matched,
        "passed": matched == 0,
    }


def _schema_contract(engine: Engine) -> dict[str, Any]:
    inspector = inspect(engine)
    database_tables = set(inspector.get_table_names())
    model_columns = {
        model.__tablename__: tuple(column.name for column in model.__table__.columns)
        for model in MODEL_TABLES
    }
    database_columns = {
        table_name: tuple(
            column["name"] for column in inspector.get_columns(table_name)
        )
        for table_name in TABLE_NAMES
    }
    column_matches = {
        table_name: model_columns[table_name] == database_columns[table_name]
        for table_name in TABLE_NAMES
    }
    with engine.connect() as connection:
        policies = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM pg_policies "
                    "WHERE schemaname = 'public' AND tablename = ANY(:tables)"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalar_one()
        )
        triggers = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM information_schema.triggers "
                    "WHERE event_object_schema = 'public' "
                    "AND event_object_table = ANY(:tables)"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalar_one()
        )
        forced_rls = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM pg_class c "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relname = ANY(:tables) "
                    "AND c.relrowsecurity AND c.relforcerowsecurity"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalar_one()
        )
        named_constraints = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM pg_constraint con "
                    "JOIN pg_class rel ON rel.oid = con.conrelid "
                    "JOIN pg_namespace n ON n.oid = rel.relnamespace "
                    "WHERE n.nspname = 'public' AND rel.relname = ANY(:tables)"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalar_one()
        )
        indexes = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM pg_indexes WHERE schemaname = 'public' "
                    "AND tablename = ANY(:tables)"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalar_one()
        )
    exact_tables_present = all(name in database_tables for name in TABLE_NAMES)
    return {
        "exact_tables_present": exact_tables_present,
        "model_database_column_matches": column_matches,
        "policy_count": policies,
        "trigger_event_count": triggers,
        "forced_rls_table_count": forced_rls,
        "constraint_count": named_constraints,
        "index_count": indexes,
        "passed": (
            exact_tables_present
            and all(column_matches.values())
            and policies == 6
            and triggers == 4
            and forced_rls == 5
            and named_constraints > 20
            and indexes >= 18
        ),
    }


def _force_audit_outage(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE FUNCTION emr4_auth_acceptance_force_audit_outage()
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
                CREATE TRIGGER trg_emr4_auth_acceptance_force_audit_outage
                BEFORE INSERT ON application_auth_audit_events
                FOR EACH ROW
                EXECUTE FUNCTION emr4_auth_acceptance_force_audit_outage()
                """
            )
        )


def _remove_audit_outage(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "DROP TRIGGER IF EXISTS "
                "trg_emr4_auth_acceptance_force_audit_outage "
                "ON application_auth_audit_events"
            )
        )
        connection.execute(
            text(
                "DROP FUNCTION IF EXISTS "
                "emr4_auth_acceptance_force_audit_outage()"
            )
        )


def _audit_atomicity(
    engine: Engine,
    factory: Callable[[], Session],
    token_source: DeterministicTokenSource,
) -> dict[str, Any]:
    before = _table_counts(engine)
    _force_audit_outage(engine)
    reason = None
    try:
        _runtime(factory, token_source).create_session(
            principal=_principal("audit-outage", "outage"),
            surface=Surface.WORD_ONLINE,
            origin=SURFACE_ORIGINS[Surface.WORD_ONLINE],
            correlation_id="correlation-audit-outage",
        )
    except RequiredAuditUnavailable as exc:
        reason = exc.reason_code
    finally:
        _remove_audit_outage(engine)
    after = _table_counts(engine)
    return {
        "denial_reason": reason,
        "state_and_audit_unchanged": before == after,
        "passed": reason == "required_audit_unavailable" and before == after,
    }


def _postgres_guards(engine: Engine, practice_ref: str) -> dict[str, Any]:
    with engine.connect() as connection:
        audit_id = int(
            connection.execute(
                text(
                    "SELECT id FROM application_auth_audit_events "
                    "WHERE practice_ref = :practice ORDER BY id LIMIT 1"
                ),
                {"practice": practice_ref},
            ).scalar_one()
        )
        grant_hash = connection.execute(
            text(
                "SELECT grant_reference_hash FROM application_auth_exchange_grants "
                "WHERE practice_ref = :practice AND consumed_at IS NOT NULL LIMIT 1"
            ),
            {"practice": practice_ref},
        ).scalar_one()
        generation = int(
            connection.execute(
                text(
                    "SELECT generation FROM application_auth_principal_generations "
                    "WHERE practice_ref = :practice ORDER BY user_ref LIMIT 1"
                ),
                {"practice": practice_ref},
            ).scalar_one()
        )

    def attempt(statement: str, parameters: dict[str, Any]) -> str | None:
        def execute() -> None:
            with engine.connect() as connection:
                transaction = connection.begin()
                try:
                    connection.execute(text(statement), parameters)
                    transaction.commit()
                except Exception:
                    transaction.rollback()
                    raise

        return _database_error_state(execute)

    states = {
        "audit_update": attempt(
            "UPDATE application_auth_audit_events SET action = action WHERE id = :id",
            {"id": audit_id},
        ),
        "audit_delete": attempt(
            "DELETE FROM application_auth_audit_events WHERE id = :id",
            {"id": audit_id},
        ),
        "generation_rollback": attempt(
            "UPDATE application_auth_principal_generations "
            "SET generation = :value WHERE practice_ref = :practice",
            {"value": generation - 1, "practice": practice_ref},
        ),
        "generation_skip": attempt(
            "UPDATE application_auth_principal_generations "
            "SET generation = :value WHERE practice_ref = :practice",
            {"value": generation + 2, "practice": practice_ref},
        ),
        "exchange_consumption_reset": attempt(
            "UPDATE application_auth_exchange_grants SET consumed_at = NULL "
            "WHERE grant_reference_hash = :grant",
            {"grant": grant_hash},
        ),
        "exchange_consumption_rewrite": attempt(
            "UPDATE application_auth_exchange_grants "
            "SET consumed_at = consumed_at + interval '1 second' "
            "WHERE grant_reference_hash = :grant",
            {"grant": grant_hash},
        ),
    }
    return {
        "sqlstates": states,
        "passed": all(value == "55000" for value in states.values()),
    }


def _rls_probe(
    engine: Engine,
    own_practice: str,
    foreign_practice: str,
) -> dict[str, Any]:
    role_name = f"emr4_auth_probe_{secrets.token_hex(6)}"
    if not re.fullmatch(r"emr4_auth_probe_[0-9a-f]{12}", role_name):
        raise AcceptanceFailure("unsafe_rls_probe_role")

    no_context: dict[str, int] = {}
    own_context: dict[str, int] = {}
    foreign_visible = -1
    foreign_update_count = -1
    foreign_insert_state: str | None = None

    with engine.connect() as connection:
        outer = connection.begin()
        quoted_role = connection.dialect.identifier_preparer.quote(role_name)
        try:
            connection.execute(
                text(
                    f"CREATE ROLE {quoted_role} NOLOGIN NOSUPERUSER NOCREATEDB "
                    "NOCREATEROLE NOINHERIT NOBYPASSRLS"
                )
            )
            for table_name in TABLE_NAMES:
                connection.execute(
                    text(
                        f'GRANT SELECT, INSERT, UPDATE, DELETE ON "{table_name}" '
                        f"TO {quoted_role}"
                    )
                )
            connection.execute(
                text(
                    "GRANT USAGE, SELECT ON SEQUENCE "
                    "application_auth_audit_events_id_seq "
                    f"TO {quoted_role}"
                )
            )
            connection.execute(text(f"SET LOCAL ROLE {quoted_role}"))
            connection.execute(
                text("SELECT set_config('app.current_practice_ref', '', true)")
            )
            for table_name in TABLE_NAMES:
                no_context[table_name] = int(
                    connection.execute(
                        text(f'SELECT count(*) FROM "{table_name}"')
                    ).scalar_one()
                )

            connection.execute(
                text(
                    "SELECT set_config('app.current_practice_ref', :practice, true)"
                ),
                {"practice": own_practice},
            )
            for table_name in TABLE_NAMES:
                own_context[table_name] = int(
                    connection.execute(
                        text(f'SELECT count(*) FROM "{table_name}"')
                    ).scalar_one()
                )
            foreign_visible = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM application_auth_principal_generations "
                        "WHERE practice_ref = :foreign"
                    ),
                    {"foreign": foreign_practice},
                ).scalar_one()
            )
            foreign_update_count = int(
                connection.execute(
                    text(
                        "UPDATE application_auth_principal_generations "
                        "SET updated_at = updated_at WHERE practice_ref = :foreign"
                    ),
                    {"foreign": foreign_practice},
                ).rowcount
            )
            try:
                with connection.begin_nested():
                    connection.execute(
                        text(
                            "INSERT INTO application_auth_principal_generations "
                            "(practice_ref, user_ref, generation, data_class) "
                            "VALUES (:practice, :user, 1, 'authored_synthetic')"
                        ),
                        {
                            "practice": foreign_practice,
                            "user": "synthetic-user-rls-foreign-insert",
                        },
                    )
            except DBAPIError as exc:
                foreign_insert_state = getattr(exc.orig, "sqlstate", None) or getattr(
                    exc.orig, "pgcode", None
                )
        finally:
            outer.rollback()

    with engine.connect() as connection:
        role_exists_after = bool(
            connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
                {"name": role_name},
            ).scalar_one_or_none()
        )
    return {
        "role_properties": {
            "login": False,
            "superuser": False,
            "bypass_rls": False,
        },
        "no_context_all_zero": all(value == 0 for value in no_context.values()),
        "own_context_nonzero_tables": sum(
            1 for value in own_context.values() if value > 0
        ),
        "foreign_visible_rows": foreign_visible,
        "foreign_update_rows": foreign_update_count,
        "foreign_insert_sqlstate": foreign_insert_state,
        "role_absent_after_rollback": not role_exists_after,
        "passed": (
            all(value == 0 for value in no_context.values())
            and all(value > 0 for value in own_context.values())
            and foreign_visible == 0
            and foreign_update_count == 0
            and foreign_insert_state == "42501"
            and not role_exists_after
        ),
    }


def _exercise_runtime(engine: Engine) -> dict[str, Any]:
    factory = _session_factory(engine)
    token_source = DeterministicTokenSource()
    principal_a = _principal("alpha", "alpha")
    principal_b = _principal("beta", "beta")

    created = _runtime(factory, token_source).create_session(
        principal=principal_a,
        surface=Surface.WORD_DESKTOP,
        origin=SURFACE_ORIGINS[Surface.WORD_DESKTOP],
        correlation_id="correlation-create-alpha",
    )
    validated = _runtime(factory, token_source).validate_surface_session(
        surface_session_value=created.surface_session_value,
        surface=Surface.WORD_DESKTOP,
        origin=SURFACE_ORIGINS[Surface.WORD_DESKTOP],
        correlation_id="correlation-validate-alpha",
    )

    verifier = "v" * 64
    state = "state-authored-synthetic-alpha"
    nonce = "nonce-authored-synthetic-alpha"
    issued = _runtime(factory, token_source).issue_exchange(
        source_surface_session_value=created.surface_session_value,
        source_surface=Surface.WORD_DESKTOP,
        target_surface=Surface.NATIVE_DIARY,
        source_origin=SURFACE_ORIGINS[Surface.WORD_DESKTOP],
        target_origin=SURFACE_ORIGINS[Surface.NATIVE_DIARY],
        state=state,
        nonce=nonce,
        pkce_challenge=pkce_s256_challenge(verifier),
        correlation_id="correlation-issue-alpha",
    )

    barrier = Barrier(2)

    def redeem(index: int) -> tuple[str, str]:
        barrier.wait(timeout=10)
        try:
            result = _runtime(factory, token_source).redeem_exchange(
                exchange_code=issued.exchange_code,
                source_surface=Surface.WORD_DESKTOP,
                target_surface=Surface.NATIVE_DIARY,
                source_origin=SURFACE_ORIGINS[Surface.WORD_DESKTOP],
                target_origin=SURFACE_ORIGINS[Surface.NATIVE_DIARY],
                state=state,
                nonce=nonce,
                pkce_verifier=verifier,
                correlation_id=f"correlation-redeem-alpha-{index}",
            )
            return "success", result.target_surface_session_value
        except AuthRuntimeDenied as exc:
            return "denied", exc.reason_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        concurrent_results = tuple(executor.map(redeem, (1, 2)))
    successes = tuple(value for status, value in concurrent_results if status == "success")
    denials = tuple(value for status, value in concurrent_results if status == "denied")
    if len(successes) != 1:
        raise AcceptanceFailure("concurrent_redemption_success_count_mismatch")

    target_surface_value = successes[0]
    restarted_target = _runtime(factory, token_source).validate_surface_session(
        surface_session_value=target_surface_value,
        surface=Surface.NATIVE_DIARY,
        origin=SURFACE_ORIGINS[Surface.NATIVE_DIARY],
        correlation_id="correlation-validate-target-alpha",
    )

    _runtime(factory, token_source).create_session(
        principal=principal_b,
        surface=Surface.WORD_ONLINE,
        origin=SURFACE_ORIGINS[Surface.WORD_ONLINE],
        correlation_id="correlation-create-beta",
    )

    new_generation = _runtime(factory, token_source).advance_principal_generation(
        principal=principal_a,
        reason="role_changed",
        correlation_id="correlation-generation-alpha",
    )
    post_generation_reason = None
    try:
        _runtime(factory, token_source).validate_surface_session(
            surface_session_value=target_surface_value,
            surface=Surface.NATIVE_DIARY,
            origin=SURFACE_ORIGINS[Surface.NATIVE_DIARY],
            correlation_id="correlation-generation-denial-alpha",
        )
    except AuthRuntimeDenied as exc:
        post_generation_reason = exc.reason_code

    raw_scan = _raw_secret_scan(
        engine,
        (
            created.parent_session_value,
            created.surface_session_value,
            issued.exchange_code,
            target_surface_value,
            state,
            nonce,
            verifier,
        ),
    )
    audit_atomicity = _audit_atomicity(engine, factory, token_source)
    guards = _postgres_guards(engine, principal_a.practice_id)
    rls = _rls_probe(engine, principal_a.practice_id, principal_b.practice_id)

    return {
        "durability": {
            "validated_after_fresh_database_session": (
                validated.user_id == principal_a.user_id
                and validated.practice_id == principal_a.practice_id
            ),
            "target_validated_after_fresh_database_session": (
                restarted_target.surface is Surface.NATIVE_DIARY
            ),
            "generation_after_advance": new_generation,
            "post_generation_denial": post_generation_reason,
        },
        "concurrency": {
            "independent_database_sessions": 2,
            "success_count": len(successes),
            "denial_reasons": list(denials),
            "exactly_one_consumer": (
                len(successes) == 1 and denials == ("exchange_already_consumed",)
            ),
        },
        "raw_secret_scan": raw_scan,
        "audit_atomicity": audit_atomicity,
        "postgres_guards": guards,
        "rls": rls,
        "passed": (
            validated.user_id == principal_a.user_id
            and restarted_target.surface is Surface.NATIVE_DIARY
            and new_generation == 2
            and post_generation_reason is not None
            and len(successes) == 1
            and denials == ("exchange_already_consumed",)
            and raw_scan["passed"]
            and audit_atomicity["passed"]
            and guards["passed"]
            and rls["passed"]
        ),
    }


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    database_name = f"emr4_auth_persistence_acceptance_{secrets.token_hex(6)}"
    if not DATABASE_NAME_PATTERN.fullmatch(database_name):
        raise AcceptanceFailure("generated_database_name_invalid")

    base = _base_database_url()
    target = base.set(database=database_name)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    engine: Engine | None = None
    created = False
    evidence: dict[str, Any] = {
        "schema_version": "raisa.shared-auth-postgresql-persistence.evidence.v1",
        "result": "revision_required",
        "evidence_label": "live_local_backend_postgres",
        "data_class": "authored_synthetic",
        "database": {
            "name_recorded": False,
            "unique_allowlisted_name_used": True,
            "loopback_only": True,
            "preexisting": False,
        },
        "cleanup": {
            "exact_database_drop_attempted": False,
            "database_absent_after": False,
        },
    }
    failure_type: str | None = None
    try:
        _create_database(maintenance, database_name)
        created = True
        upgrade = _require_alembic(target, "upgrade", "head")
        _require_alembic(target, "downgrade", MIGRATION_BASE)
        _require_alembic(target, "upgrade", "head")
        current = _require_alembic(target, "current")
        drift_check = _require_alembic(target, "check")
        migration = {
            "base_revision": MIGRATION_BASE,
            "head_revision": MIGRATION_HEAD,
            "upgrade_passed": True,
            "downgrade_passed": True,
            "reupgrade_passed": True,
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": (
                "No new upgrade operations detected" in drift_check
            ),
            "migration_log_recorded": False,
            "initial_upgrade_log_nonempty": bool(upgrade.strip()),
        }
        if not (
            migration["current_head_exact"]
            and migration["orm_migration_drift_absent"]
        ):
            raise AcceptanceFailure("migration_current_or_drift_mismatch")

        engine = create_engine(target, pool_pre_ping=True)
        schema = _schema_contract(engine)
        runtime = _exercise_runtime(engine)
        passed = (
            migration["current_head_exact"]
            and migration["orm_migration_drift_absent"]
            and schema["passed"]
            and runtime["passed"]
        )
        evidence.update(
            {
                "result": (
                    "raisa_shared_application_auth_postgresql_persistence_pass"
                    if passed
                    else "revision_required"
                ),
                "migration": migration,
                "schema_contract": schema,
                "runtime": runtime,
                "side_effect_counts": {
                    "database_migrations_disposable": 3,
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
                    "No live identity, route, cookie, runtime database role or product authorization is established.",
                    "Only a uniquely named disposable local authored-synthetic PostgreSQL database was exercised.",
                    "External identity, Microsoft or Office authority, product-derived data, commands, deployment, production and release remain closed.",
                ],
            }
        )
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
    finally:
        if engine is not None:
            engine.dispose()
        if created:
            evidence["cleanup"]["exact_database_drop_attempted"] = True
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance, database_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["cleanup_failure_type"] = type(cleanup_exc).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = not _database_exists(
                maintenance, database_name
            )
        maintenance.dispose()

    evidence["cleanup"]["passed"] = bool(
        evidence["cleanup"]["database_absent_after"]
    )
    if not evidence["cleanup"]["passed"]:
        evidence["result"] = "revision_required"
    evidence["passed"] = (
        evidence["result"]
        == "raisa_shared_application_auth_postgresql_persistence_pass"
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
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
