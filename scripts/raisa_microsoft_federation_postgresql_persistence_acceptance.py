"""Disposable PostgreSQL acceptance for synthetic federation persistence."""

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
from threading import Barrier
from typing import Any, Callable, Iterable

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.application_identity_federation import (  # noqa: E402
    ApplicationIdentityFederationAuditEvent,
    ApplicationIdentityFederationBinding,
)
from app.services.application_identity_federation import (  # noqa: E402
    ExternalIdentityBinding,
    FederationReferenceHasher,
)
from app.services.application_identity_federation_persistence import (  # noqa: E402
    FederationPersistenceAuditUnavailable,
    FederationPersistenceDenied,
    PostgresFederationBindingRepository,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-microsoft-federation-postgresql-persistence"
    / "live-local-backend-postgres-evidence.json"
)
DATABASE_NAME_PATTERN = re.compile(
    r"^emr4_federation_persistence_acceptance_[0-9a-f]{12}$"
)
TABLE_NAMES = (
    "application_identity_federation_bindings",
    "application_identity_federation_audit_events",
)
MODEL_TABLES = (
    ApplicationIdentityFederationBinding,
    ApplicationIdentityFederationAuditEvent,
)
MIGRATION_BASE = "p5q6r7s8t9u0"
MIGRATION_HEAD = "q6r7s8t9u0v1"
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
FIXED_NOW = datetime(2026, 8, 1, 5, 0, tzinfo=timezone.utc)
HMAC_KEY = b"authored-synthetic-persistence-hmac-key-000000000001"
ISSUER = "https://login.microsoftonline.invalid/synthetic-tenant-001/v2.0"
TENANT = "synthetic-tenant-001"
SUBJECT = "synthetic-subject-001"


class AcceptanceFailure(RuntimeError):
    pass


class _FailingAuditRepository(PostgresFederationBindingRepository):
    def _before_audit_flush(self) -> None:
        raise FederationPersistenceAuditUnavailable("forced acceptance audit outage")


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


def _factory(engine: Engine) -> Callable[[], Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def _repository(
    factory: Callable[[], Session],
    repository_type: type[PostgresFederationBindingRepository] = (
        PostgresFederationBindingRepository
    ),
) -> PostgresFederationBindingRepository:
    return repository_type(
        session_factory=factory,
        reference_hasher=FederationReferenceHasher(HMAC_KEY),
        clock=lambda: FIXED_NOW,
    )


def _binding(
    suffix: str,
    *,
    practice: str = "alpha",
    object_suffix: str | None = None,
) -> ExternalIdentityBinding:
    return ExternalIdentityBinding(
        provider="microsoft_entra",
        tenant_id=TENANT,
        object_id=f"synthetic-object-{object_suffix or suffix}",
        binding_ref=f"synthetic-binding-{suffix}",
        user_ref=f"synthetic-user-{suffix}",
        practice_ref=f"synthetic-practice-{practice}",
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


def _schema_contract(engine: Engine) -> dict[str, Any]:
    inspector = inspect(engine)
    column_matches = {}
    for model in MODEL_TABLES:
        model_columns = {column.name for column in model.__table__.columns}
        database_columns = {
            column["name"] for column in inspector.get_columns(model.__tablename__)
        }
        column_matches[model.__tablename__] = model_columns == database_columns

    with engine.connect() as connection:
        rls_rows = connection.execute(
            text(
                "SELECT relname, relrowsecurity, relforcerowsecurity "
                "FROM pg_class WHERE relname = ANY(:tables)"
            ),
            {"tables": list(TABLE_NAMES)},
        ).mappings()
        rls = {
            row["relname"]: bool(row["relrowsecurity"] and row["relforcerowsecurity"])
            for row in rls_rows
        }
        policy_count = int(
            connection.execute(
                text(
                    "SELECT count(*) FROM pg_policies "
                    "WHERE tablename = ANY(:tables)"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalar_one()
        )
        trigger_names = set(
            connection.execute(
                text(
                    "SELECT tgname FROM pg_trigger t "
                    "JOIN pg_class c ON c.oid = t.tgrelid "
                    "WHERE c.relname = ANY(:tables) AND NOT t.tgisinternal"
                ),
                {"tables": list(TABLE_NAMES)},
            ).scalars()
        )
    expected_triggers = {
        "trg_app_id_fed_audit_append_only",
        "trg_app_id_fed_binding_terminal",
    }
    passed = (
        set(inspector.get_table_names()) >= set(TABLE_NAMES)
        and all(column_matches.values())
        and set(rls) == set(TABLE_NAMES)
        and all(rls.values())
        and policy_count == 3
        and expected_triggers <= trigger_names
    )
    return {
        "table_count": len(TABLE_NAMES),
        "model_database_column_matches": column_matches,
        "forced_rls": rls,
        "policy_count": policy_count,
        "trigger_names": sorted(trigger_names),
        "passed": passed,
    }


def _raw_scan(engine: Engine, raw_values: Iterable[str]) -> dict[str, Any]:
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
    matched = sorted(value for value in raw_values if value and value in joined)
    return {
        "persisted_row_count": len(persisted),
        "raw_value_count": len(tuple(raw_values)),
        "matched_raw_value_count": len(matched),
        "matched_values_recorded": False,
        "passed": not matched,
    }


def _database_error_state(call: Callable[[], Any]) -> str | None:
    try:
        call()
    except DBAPIError as exc:
        original = exc.orig
        return getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)
    return None


def _guard_probe(engine: Engine, audit_id: int, binding_ref: str) -> dict[str, Any]:
    def update_audit() -> None:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE application_identity_federation_audit_events "
                    "SET reason_code = 'tampered' WHERE id = :id"
                ),
                {"id": audit_id},
            )

    def delete_audit() -> None:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "DELETE FROM application_identity_federation_audit_events "
                    "WHERE id = :id"
                ),
                {"id": audit_id},
            )

    def reactivate_binding() -> None:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "UPDATE application_identity_federation_bindings "
                    "SET status = 'active', version = version + 1, "
                    "revoked_at = NULL, updated_at = now() "
                    "WHERE binding_ref = :binding"
                ),
                {"binding": binding_ref},
            )

    states = {
        "audit_update": _database_error_state(update_audit),
        "audit_delete": _database_error_state(delete_audit),
        "binding_reactivation": _database_error_state(reactivate_binding),
    }
    return {
        "sqlstates": states,
        "passed": set(states.values()) == {"55000"},
    }


def _rls_probe(engine: Engine, own_practice: str, foreign_practice: str) -> dict[str, Any]:
    role_name = f"emr4_federation_probe_{secrets.token_hex(6)}"
    if not re.fullmatch(r"emr4_federation_probe_[0-9a-f]{12}", role_name):
        raise AcceptanceFailure("rls_role_name_invalid")
    quoted_role = f'"{role_name}"'
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text(
                    f"CREATE ROLE {quoted_role} NOLOGIN NOSUPERUSER NOCREATEDB "
                    "NOCREATEROLE NOINHERIT NOBYPASSRLS"
                )
            )
            for table_name in TABLE_NAMES:
                connection.execute(
                    text(f'GRANT SELECT ON "{table_name}" TO {quoted_role}')
                )
            connection.execute(text(f"SET LOCAL ROLE {quoted_role}"))
            connection.execute(text("SELECT set_config('emr4.practice_ref', '', true)"))
            without_context = {
                table: int(
                    connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one()
                )
                for table in TABLE_NAMES
            }
            connection.execute(
                text("SELECT set_config('emr4.practice_ref', :practice, true)"),
                {"practice": own_practice},
            )
            own_context = {
                table: int(
                    connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one()
                )
                for table in TABLE_NAMES
            }
            foreign_visible = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM application_identity_federation_bindings "
                        "WHERE practice_ref = :foreign"
                    ),
                    {"foreign": foreign_practice},
                ).scalar_one()
            )
            connection.execute(text("RESET ROLE"))
        finally:
            transaction.rollback()
    with engine.connect() as connection:
        role_absent = (
            connection.execute(
                text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
                {"role": role_name},
            ).scalar_one_or_none()
            is None
        )
    passed = (
        set(without_context.values()) == {0}
        and own_context[TABLE_NAMES[0]] > 0
        and own_context[TABLE_NAMES[1]] > 0
        and foreign_visible == 0
        and role_absent
    )
    return {
        "role_name_recorded": False,
        "without_context": without_context,
        "own_context": own_context,
        "foreign_binding_rows_visible": foreign_visible,
        "role_absent_after_rollback": role_absent,
        "passed": passed,
    }


def _exercise_repository(engine: Engine) -> dict[str, Any]:
    factory = _factory(engine)
    repository = _repository(factory)
    alpha = _binding("alpha")
    beta = _binding("beta", practice="beta")
    repository.create_binding(
        binding=alpha,
        issuer=ISSUER,
        subject=SUBJECT,
        operation_ref="synthetic-operation-create-alpha",
        correlation_ref="synthetic-correlation-create-alpha",
    )
    repository.create_binding(
        binding=beta,
        issuer=ISSUER,
        subject="synthetic-subject-beta",
        operation_ref="synthetic-operation-create-beta",
        correlation_ref="synthetic-correlation-create-beta",
    )
    resolved = _repository(factory).resolve_active_binding(
        provider="microsoft_entra",
        issuer=ISSUER,
        tenant_id=TENANT,
        object_id=alpha.object_id,
        operation_ref="synthetic-operation-resolve-alpha",
        correlation_ref="synthetic-correlation-resolve-alpha",
    )

    barrier = Barrier(2)

    def concurrent_create(index: int) -> str:
        candidate = _binding(
            f"concurrent-{index}",
            object_suffix="concurrent",
        )
        barrier.wait(timeout=10)
        try:
            _repository(factory).create_binding(
                binding=candidate,
                issuer=ISSUER,
                subject=f"synthetic-subject-concurrent-{index}",
                operation_ref=f"synthetic-operation-concurrent-{index}",
                correlation_ref=f"synthetic-correlation-concurrent-{index}",
            )
            return "created"
        except FederationPersistenceDenied as exc:
            return exc.reason_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        concurrent_results = tuple(executor.map(concurrent_create, (1, 2)))

    before_failure = _table_counts(engine)
    audit_failure_reason = None
    try:
        _repository(factory, _FailingAuditRepository).create_binding(
            binding=_binding("audit-failure"),
            issuer=ISSUER,
            subject="synthetic-subject-audit-failure",
            operation_ref="synthetic-operation-audit-failure",
            correlation_ref="synthetic-correlation-audit-failure",
        )
    except FederationPersistenceAuditUnavailable:
        audit_failure_reason = "required_audit_unavailable"
    after_failure = _table_counts(engine)

    new_version = _repository(factory).revoke_binding(
        binding_ref=alpha.binding_ref,
        expected_version=1,
        operation_ref="synthetic-operation-revoke-alpha",
        correlation_ref="synthetic-correlation-revoke-alpha",
    )
    resolved_after_revoke = _repository(factory).resolve_active_binding(
        provider="microsoft_entra",
        issuer=ISSUER,
        tenant_id=TENANT,
        object_id=alpha.object_id,
        operation_ref="synthetic-operation-resolve-revoked",
        correlation_ref="synthetic-correlation-resolve-revoked",
    )

    with engine.connect() as connection:
        audit_id = int(
            connection.execute(
                text(
                    "SELECT min(id) FROM application_identity_federation_audit_events"
                )
            ).scalar_one()
        )
    guards = _guard_probe(engine, audit_id, alpha.binding_ref)
    rls = _rls_probe(engine, alpha.practice_ref, beta.practice_ref)
    raw_values = (
        ISSUER,
        TENANT,
        alpha.object_id,
        SUBJECT,
        "not-authority@example.invalid",
        HMAC_KEY.decode("ascii"),
        "synthetic-correlation-create-alpha",
    )
    raw_scan = _raw_scan(engine, raw_values)

    passed = (
        len(resolved) == 1
        and resolved[0].binding_ref == alpha.binding_ref
        and concurrent_results.count("created") == 1
        and concurrent_results.count("binding_conflict") == 1
        and audit_failure_reason == "required_audit_unavailable"
        and before_failure == after_failure
        and new_version == 2
        and resolved_after_revoke == ()
        and guards["passed"]
        and rls["passed"]
        and raw_scan["passed"]
    )
    return {
        "durability": {
            "resolved_after_fresh_repository": len(resolved) == 1,
            "resolved_binding_ref": resolved[0].binding_ref if resolved else None,
            "revoked_version": new_version,
            "resolution_denied_after_revoke": resolved_after_revoke == (),
        },
        "concurrency": {
            "independent_database_sessions": 2,
            "results": sorted(concurrent_results),
            "exactly_one_binding_created": concurrent_results.count("created") == 1,
        },
        "audit_atomicity": {
            "failure_reason": audit_failure_reason,
            "state_and_audit_unchanged": before_failure == after_failure,
        },
        "postgres_guards": guards,
        "rls": rls,
        "raw_identity_scan": raw_scan,
        "passed": passed,
    }


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    database_name = f"emr4_federation_persistence_acceptance_{secrets.token_hex(6)}"
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
    failure_type: str | None = None
    evidence: dict[str, Any] = {
        "schema_version": "emr4.microsoft-federation-postgresql-persistence-evidence.v1",
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
    try:
        _create_database(maintenance, database_name)
        created = True
        upgrade = _require_alembic(target, "upgrade", MIGRATION_HEAD)
        _require_alembic(target, "downgrade", MIGRATION_BASE)
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        migration = {
            "base_revision": MIGRATION_BASE,
            "head_revision": MIGRATION_HEAD,
            "upgrade_passed": True,
            "downgrade_passed": True,
            "reupgrade_passed": True,
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": True,
            "migration_log_recorded": False,
            "initial_upgrade_log_nonempty": bool(upgrade.strip()),
        }
        engine = create_engine(target, pool_pre_ping=True)
        schema = _schema_contract(engine)
        runtime = _exercise_repository(engine)
        passed = migration["current_head_exact"] and schema["passed"] and runtime["passed"]
        evidence.update(
            {
                "result": (
                    "raisa_microsoft_federation_postgresql_persistence_pass"
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
                    "microsoft_graph_or_office_identity_calls": 0,
                    "http_or_socket_calls": 0,
                    "fastapi_or_graphql_routes_added": 0,
                    "application_sessions_created": 0,
                    "product_data_reads": 0,
                    "patient_or_clinical_field_reads": 0,
                    "cloud_or_iam_mutations": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "Only a uniquely named disposable local authored-synthetic PostgreSQL database was exercised.",
                    "No live Microsoft/OIDC verifier, real identity, route, session, product read, durable runtime role, deployment or production authority is established.",
                ],
            }
        )
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
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
        == "raisa_microsoft_federation_postgresql_persistence_pass"
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
                "failure_code": evidence.get("failure_code"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
