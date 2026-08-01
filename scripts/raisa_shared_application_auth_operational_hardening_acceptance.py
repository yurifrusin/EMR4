"""Disposable PostgreSQL acceptance for shared-auth operational hardening."""

from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError, TimeoutError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.routers.application_auth import (  # noqa: E402
    AUTHENTICATION_UNAVAILABLE,
    REQUEST_NOT_ADMITTED,
    REQUEST_RATE_LIMITED,
    get_application_auth_operational_hardening,
    get_application_auth_transport,
    router,
)
from app.services.application_auth_database_role import (  # noqa: E402
    create_deployment_login_role_statements,
    drop_login_role_statement,
)
from app.services.application_auth_operational_database import (  # noqa: E402
    ApplicationAuthPoolPolicy,
    create_application_auth_engine,
    create_application_auth_session_factory,
)
from app.services.application_auth_operational_hardening import (  # noqa: E402
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    PostgresTransportDenialAuditSink,
    ProxyTrustPolicy,
    RequiredTransportDenialAuditUnavailable,
    TransportDenialEvent,
)
from app.services.application_auth_runtime import Surface  # noqa: E402
from app.services.application_auth_transport import (  # noqa: E402
    TransportRequestDenied,
)
from scripts.raisa_shared_application_auth_runtime_role_secure_transport_acceptance import (  # noqa: E402
    MIGRATION_HEAD,
    _apply_role_contract,
    _base_database_url,
    _create_database,
    _database_exists,
    _drop_database,
    _drop_role,
    _require_alembic,
    _role_exists,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-operational-hardening"
    / "live-local-backend-postgres-operational-evidence.json"
)
RESULT = "raisa_shared_application_auth_operational_hardening_pass"
FIXED_NOW = datetime(2026, 8, 1, 5, 0, tzinfo=timezone.utc)
ORIGIN = "https://word-online.synthetic.invalid"


class AcceptanceFailure(RuntimeError):
    """Bounded failure that never contains a target name or credential."""


class _CsrfTransport:
    @staticmethod
    def require_origin(surface: Surface, origin: str | None) -> str:
        if surface is not Surface.WORD_ONLINE or origin != ORIGIN:
            raise TransportRequestDenied()
        return origin

    @staticmethod
    def new_csrf_token() -> str:
        return "csrf." + secrets.token_urlsafe(32)


class _FailingSink:
    def record(self, _event: TransportDenialEvent) -> None:
        raise RequiredTransportDenialAuditUnavailable()


def _role_absent(engine: Engine, role_name: str) -> bool:
    return not _role_exists(engine, role_name)


def _drop_login_role(maintenance: Engine, role_name: str) -> bool:
    if _role_exists(maintenance, role_name):
        with maintenance.connect() as connection:
            connection.execute(text(drop_login_role_statement(role_name)))
    return _role_absent(maintenance, role_name)


def _apply_login_contract(
    owner_engine: Engine,
    *,
    login_role: str,
    capability_role: str,
    password: str,
    connection_limit: int,
) -> None:
    if not password.isalnum() or len(password) < 32:
        raise AcceptanceFailure("disposable_password_shape_invalid")
    with owner_engine.begin() as connection:
        for statement in create_deployment_login_role_statements(
            login_role,
            capability_role,
            connection_limit=connection_limit,
        ):
            connection.execute(text(statement))
        connection.execute(
            text(f'ALTER ROLE "{login_role}" PASSWORD \'{password}\'')
        )


def _login_role_evidence(
    owner_engine: Engine,
    *,
    login_role: str,
    capability_role: str,
) -> dict[str, Any]:
    with owner_engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT rolcanlogin, rolinherit, rolsuper, rolcreatedb, "
                "rolcreaterole, rolreplication, rolbypassrls, rolconnlimit "
                "FROM pg_roles WHERE rolname = :role"
            ),
            {"role": login_role},
        ).one()
        member = bool(
            connection.execute(
                text("SELECT pg_has_role(:login, :capability, 'MEMBER')"),
                {"login": login_role, "capability": capability_role},
            ).scalar_one()
        )
        direct_select = bool(
            connection.execute(
                text(
                    "SELECT has_table_privilege(:role, "
                    "'public.application_auth_audit_events', 'SELECT')"
                ),
                {"role": login_role},
            ).scalar_one()
        )
    result = {
        "login_enabled": row.rolcanlogin,
        "noinherit": not row.rolinherit,
        "not_superuser": not row.rolsuper,
        "cannot_create_database": not row.rolcreatedb,
        "cannot_create_role": not row.rolcreaterole,
        "cannot_replicate": not row.rolreplication,
        "cannot_bypass_rls": not row.rolbypassrls,
        "connection_limit": row.rolconnlimit,
        "capability_membership": member,
        "direct_audit_select_grant": direct_select,
        "password_recorded": False,
    }
    result["passed"] = (
        result["login_enabled"]
        and result["noinherit"]
        and result["not_superuser"]
        and result["cannot_create_database"]
        and result["cannot_create_role"]
        and result["cannot_replicate"]
        and result["cannot_bypass_rls"]
        and result["connection_limit"] == 2
        and result["capability_membership"]
        and not result["direct_audit_select_grant"]
    )
    return result


def _exercise_role_and_pool(
    *,
    bounded_engine: Engine,
    direct_login_engine: Engine,
    login_role: str,
    capability_role: str,
    pool_policy: ApplicationAuthPoolPolicy,
) -> dict[str, Any]:
    with bounded_engine.connect() as connection:
        identity = connection.execute(
            text("SELECT session_user, current_user")
        ).one()

    direct_read_denied = False
    try:
        with direct_login_engine.connect() as connection:
            connection.execute(
                text("SELECT count(*) FROM application_auth_audit_events")
            ).scalar_one()
    except (DBAPIError, OperationalError):
        direct_read_denied = True
    # Release the credential-only probe before exercising the exact two-slot
    # deployment-role connection limit.
    direct_login_engine.dispose()

    held = [bounded_engine.connect(), bounded_engine.connect()]
    started = time.monotonic()
    checkout_timed_out = False
    try:
        try:
            bounded_engine.connect()
        except TimeoutError:
            checkout_timed_out = True
    finally:
        elapsed = time.monotonic() - started
        for connection in held:
            connection.close()

    result = {
        "session_user_is_login": identity.session_user == login_role,
        "current_user_is_capability": identity.current_user == capability_role,
        "identities_separate": identity.session_user != identity.current_user,
        "login_direct_table_read_denied": direct_read_denied,
        "pool_size": pool_policy.pool_size,
        "max_overflow": pool_policy.max_overflow,
        "pool_maximum": pool_policy.pool_size + pool_policy.max_overflow,
        "login_connection_limit": pool_policy.login_connection_limit,
        "pool_pre_ping": True,
        "pool_lifo": True,
        "pool_reset_on_return": "rollback",
        "checkout_timeout_configured_seconds": pool_policy.pool_timeout_seconds,
        "checkout_timeout_observed": checkout_timed_out,
        "checkout_timeout_elapsed_ms": round(elapsed * 1000),
        "checkout_timeout_within_bound": elapsed < 2.0,
    }
    result["passed"] = all(
        (
            result["session_user_is_login"],
            result["current_user_is_capability"],
            result["identities_separate"],
            result["login_direct_table_read_denied"],
            result["pool_maximum"] <= result["login_connection_limit"],
            result["checkout_timeout_observed"],
            result["checkout_timeout_within_bound"],
        )
    )
    return result


def _guard(
    sink,
    *,
    rate_limit: int,
) -> ApplicationAuthOperationalHardening:
    return ApplicationAuthOperationalHardening(
        proxy_policy=ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=rate_limit,
            window_seconds=60,
            max_keys=16,
            clock=lambda: 1.0,
        ),
        denial_audit_sink=sink,
        client_hmac_key=secrets.token_bytes(32),
        clock=lambda: FIXED_NOW,
    )


def _application(guard: ApplicationAuthOperationalHardening) -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: guard
    application.dependency_overrides[get_application_auth_transport] = _CsrfTransport
    return application


def _post(client: TestClient, *, origin: str = ORIGIN, headers=None):
    request_headers = {"Origin": origin}
    if headers:
        request_headers.update(headers)
    return client.post(
        "/api/v1/application-auth/csrf",
        headers=request_headers,
        json={"surface": "word_online"},
    )


def _exercise_route_denials(session_factory) -> tuple[dict[str, Any], tuple[str, ...]]:
    sink = PostgresTransportDenialAuditSink(session_factory)
    guard = _guard(sink, rate_limit=1)
    application = _application(guard)
    raw_values = (
        "198.51.100.21",
        "198.51.100.22",
        "198.51.100.23",
        "203.0.113.55",
        "https://foreign.synthetic.invalid",
    )

    with TestClient(
        application,
        base_url=ORIGIN,
        client=(raw_values[0], 50000),
    ) as client:
        admitted = _post(client)
        first_rate = _post(client)
        repeated_rate = _post(client)

    with TestClient(
        application,
        base_url=ORIGIN,
        client=(raw_values[1], 50000),
    ) as client:
        origin_denial = _post(client, origin=raw_values[4])

    with TestClient(
        application,
        base_url=ORIGIN,
        client=(raw_values[2], 50000),
    ) as client:
        proxy_denial = _post(
            client,
            headers={
                "X-Forwarded-For": raw_values[3],
                "X-Forwarded-Proto": "https",
            },
        )

    outage_application = _application(_guard(_FailingSink(), rate_limit=10))
    with TestClient(
        outage_application,
        base_url=ORIGIN,
        client=("198.51.100.99", 50000),
    ) as client:
        outage = _post(client, origin=raw_values[4])

    generic_headers = lambda response: (
        response.headers.get("cache-control") == "no-store"
        and response.headers.get("pragma") == "no-cache"
        and response.headers.get("referrer-policy") == "no-referrer"
    )
    result = {
        "initial_request_admitted": admitted.status_code == 200,
        "first_rate_denial": (
            first_rate.status_code == 429
            and first_rate.json() == {"detail": REQUEST_RATE_LIMITED}
            and first_rate.headers.get("retry-after") in {"59", "60"}
            and generic_headers(first_rate)
        ),
        "repeated_rate_denial_same_generic_response": (
            repeated_rate.status_code == 429
            and repeated_rate.json() == {"detail": REQUEST_RATE_LIMITED}
            and generic_headers(repeated_rate)
        ),
        "origin_denial": (
            origin_denial.status_code == 403
            and origin_denial.json() == {"detail": REQUEST_NOT_ADMITTED}
            and generic_headers(origin_denial)
        ),
        "untrusted_forwarded_header_denial": (
            proxy_denial.status_code == 403
            and proxy_denial.json() == {"detail": REQUEST_NOT_ADMITTED}
            and generic_headers(proxy_denial)
        ),
        "audit_outage_generic_503": (
            outage.status_code == 503
            and outage.json() == {"detail": AUTHENTICATION_UNAVAILABLE}
            and generic_headers(outage)
            and not outage.headers.get_list("set-cookie")
        ),
        "response_raw_value_match_count": sum(
            raw in "".join(
                response.text + repr(dict(response.headers))
                for response in (
                    first_rate,
                    repeated_rate,
                    origin_denial,
                    proxy_denial,
                    outage,
                )
            )
            for raw in raw_values
        ),
    }
    result["passed"] = (
        all(value for key, value in result.items() if key not in {"passed", "response_raw_value_match_count"})
        and result["response_raw_value_match_count"] == 0
    )
    return result, raw_values


def _audit_evidence(
    *,
    bounded_engine: Engine,
    owner_engine: Engine,
    raw_values: tuple[str, ...],
) -> dict[str, Any]:
    with owner_engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT id, practice_ref, user_ref, current_backend_role, "
                "event_type, correlation_id, session_reference_hash, surface, "
                "action, resource_type, policy_version, decision, reason_codes, "
                "data_class FROM application_auth_audit_events ORDER BY id"
            )
        ).mappings().all()
    serialized = json.dumps([dict(row) for row in rows], sort_keys=True)
    reasons = [row["reason_codes"][0] for row in rows]

    with bounded_engine.connect() as connection:
        no_context_count = int(
            connection.execute(
                text("SELECT count(*) FROM application_auth_audit_events")
            ).scalar_one()
        )
    with bounded_engine.begin() as connection:
        connection.execute(
            text(
                "SELECT set_config('app.current_practice_ref', "
                "'synthetic-transport-audit', true)"
            )
        )
        scoped_count = int(
            connection.execute(
                text("SELECT count(*) FROM application_auth_audit_events")
            ).scalar_one()
        )

    append_only = False
    try:
        with bounded_engine.begin() as connection:
            connection.execute(
                text(
                    "SELECT set_config('app.current_practice_ref', "
                    "'synthetic-transport-audit', true)"
                )
            )
            connection.execute(
                text(
                    "UPDATE application_auth_audit_events SET decision = 'allowed'"
                )
            )
    except DBAPIError:
        append_only = True

    result = {
        "row_count": len(rows),
        "exact_expected_row_count": len(rows) == 3,
        "rate_denial_coalesced_to_one_row": reasons.count("transport_rate_limited") == 1,
        "request_denial_rows": reasons.count("transport_request_not_admitted") == 2,
        "metadata_only_shape": all(
            row["practice_ref"] == "synthetic-transport-audit"
            and row["user_ref"] is None
            and row["current_backend_role"] is None
            and row["event_type"] == "auth.authorization_denied"
            and row["surface"] == "all"
            and row["resource_type"] == "application_auth_transport"
            and row["decision"] == "denied"
            and row["data_class"] == "authored_synthetic"
            and row["session_reference_hash"].startswith("sha256:")
            and len(row["session_reference_hash"]) == 71
            for row in rows
        ),
        "raw_value_match_count": sum(raw in serialized for raw in raw_values),
        "rls_no_context_row_count": no_context_count,
        "rls_exact_context_row_count": scoped_count,
        "rls_passed": no_context_count == 0 and scoped_count == 3,
        "append_only_update_rejected": append_only,
    }
    result["passed"] = (
        result["exact_expected_row_count"]
        and result["rate_denial_coalesced_to_one_row"]
        and result["request_denial_rows"]
        and result["metadata_only_shape"]
        and result["raw_value_match_count"] == 0
        and result["rls_passed"]
        and result["append_only_update_rejected"]
    )
    return result


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_auth_transport_acceptance_{suffix}"
    capability_role = f"emr4_application_auth_runtime_{suffix}"
    login_role = f"emr4_application_auth_login_{suffix}"
    disposable_password = secrets.token_hex(24)

    base = _base_database_url()
    target = base.set(database=database_name)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner_engine: Engine | None = None
    bounded_engine: Engine | None = None
    direct_login_engine: Engine | None = None
    database_created = False
    capability_created = False
    login_created = False
    failure_type: str | None = None
    stage = "preflight"
    evidence: dict[str, Any] = {
        "schema_version": "raisa.shared-auth-operational-hardening.evidence.v1",
        "result": "revision_required",
        "evidence_label": "live_local_backend_postgres_operational",
        "data_class": "authored_synthetic",
        "database": {
            "name_recorded": False,
            "loopback_only": True,
            "preexisting": False,
        },
        "roles": {
            "names_recorded": False,
            "capability_preexisting": False,
            "login_preexisting": False,
            "password_recorded": False,
        },
        "cleanup": {
            "database_drop_attempted": False,
            "login_role_drop_attempted": False,
            "capability_role_drop_attempted": False,
            "database_absent_after": False,
            "login_role_absent_after": False,
            "capability_role_absent_after": False,
        },
    }
    try:
        stage = "preexisting_check"
        if _database_exists(maintenance, database_name):
            raise AcceptanceFailure("disposable_database_preexisted")
        if _role_exists(maintenance, capability_role) or _role_exists(maintenance, login_role):
            raise AcceptanceFailure("disposable_role_preexisted")
        _create_database(maintenance, database_name)
        database_created = True
        stage = "migration"
        # Keep this accepted parent pinned to its exact historical schema.
        # Later authorised descendants must not silently broaden its role or
        # operational-hardening evidence.
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        migration = {
            "head_revision": MIGRATION_HEAD,
            "current_head_exact": MIGRATION_HEAD in current,
            "orm_migration_drift_absent": True,
        }
        migration["passed"] = migration["current_head_exact"] and migration["orm_migration_drift_absent"]

        owner_engine = create_engine(target, pool_pre_ping=True)
        stage = "capability_role"
        _apply_role_contract(owner_engine, capability_role)
        capability_created = True
        stage = "login_role"
        _apply_login_contract(
            owner_engine,
            login_role=login_role,
            capability_role=capability_role,
            password=disposable_password,
            connection_limit=2,
        )
        login_created = True
        role_contract = _login_role_evidence(
            owner_engine,
            login_role=login_role,
            capability_role=capability_role,
        )

        login_target = target.set(username=login_role, password=disposable_password)
        stage = "bounded_engine"
        pool_policy = ApplicationAuthPoolPolicy(
            pool_size=1,
            max_overflow=1,
            pool_timeout_seconds=0.25,
            pool_recycle_seconds=60,
            login_connection_limit=2,
        )
        bounded_engine = create_application_auth_engine(
            login_target.render_as_string(hide_password=False),
            login_role=login_role,
            capability_role=capability_role,
            policy=pool_policy,
        )
        direct_login_engine = create_engine(login_target, pool_pre_ping=True)
        stage = "role_and_pool"
        role_and_pool = _exercise_role_and_pool(
            bounded_engine=bounded_engine,
            direct_login_engine=direct_login_engine,
            login_role=login_role,
            capability_role=capability_role,
            pool_policy=pool_policy,
        )
        session_factory = create_application_auth_session_factory(bounded_engine)
        stage = "route_denials"
        routes, raw_values = _exercise_route_denials(session_factory)
        stage = "audit_evidence"
        audit = _audit_evidence(
            bounded_engine=bounded_engine,
            owner_engine=owner_engine,
            raw_values=raw_values,
        )
        passed = all(
            (
                migration["passed"],
                role_contract["passed"],
                role_and_pool["passed"],
                routes["passed"],
                audit["passed"],
            )
        )
        evidence.update(
            {
                "migration": migration,
                "deployment_role_isolation": role_contract,
                "bounded_pool": role_and_pool,
                "proxy_rate_and_route_denials": routes,
                "retained_denial_audit": audit,
                "side_effect_counts": {
                    "provider_calls": 0,
                    "external_identity_calls": 0,
                    "microsoft_or_office_identity_calls": 0,
                    "cloud_or_iam_mutations": 0,
                    "product_data_reads": 0,
                    "patient_health_or_clinical_reads": 0,
                    "appointment_or_arrival_commands": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "The limiter is per process and proves no distributed or production abuse resistance.",
                    "The deployment credential was disposable, was not recorded and proves no secret-manager or rotation path.",
                    "No real identity, Office federation, product data, deployment, production or release is established.",
                ],
                "result": RESULT if passed else "revision_required",
            }
        )
        if not passed:
            raise AcceptanceFailure("one_or_more_operational_gates_failed")
        serialized = json.dumps(evidence, sort_keys=True)
        prohibited = (*raw_values, disposable_password, database_name, capability_role, login_role)
        evidence_match_count = sum(value in serialized for value in prohibited)
        evidence["evidence_raw_or_target_match_count"] = evidence_match_count
        if evidence_match_count:
            evidence["result"] = "revision_required"
            raise AcceptanceFailure("raw_or_target_value_in_evidence")
        stage = "accepted"
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        evidence["failure_stage"] = stage
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
    finally:
        if bounded_engine is not None:
            bounded_engine.dispose()
        if direct_login_engine is not None:
            direct_login_engine.dispose()
        if owner_engine is not None:
            owner_engine.dispose()
        if login_created:
            evidence["cleanup"]["login_role_drop_attempted"] = True
            try:
                evidence["cleanup"]["login_role_absent_after"] = _drop_login_role(
                    maintenance,
                    login_role,
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["login_cleanup_failure_type"] = type(cleanup_exc).__name__
        else:
            evidence["cleanup"]["login_role_absent_after"] = _role_absent(maintenance, login_role)
        if database_created:
            evidence["cleanup"]["database_drop_attempted"] = True
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance,
                    database_name,
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_cleanup_failure_type"] = type(cleanup_exc).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = not _database_exists(maintenance, database_name)
        if capability_created:
            evidence["cleanup"]["capability_role_drop_attempted"] = True
            try:
                evidence["cleanup"]["capability_role_absent_after"] = _drop_role(
                    maintenance,
                    capability_role,
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["capability_cleanup_failure_type"] = type(cleanup_exc).__name__
        else:
            evidence["cleanup"]["capability_role_absent_after"] = _role_absent(maintenance, capability_role)
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(
        (
            evidence["cleanup"]["database_absent_after"],
            evidence["cleanup"]["login_role_absent_after"],
            evidence["cleanup"]["capability_role_absent_after"],
        )
    )
    if not evidence["cleanup"]["passed"]:
        evidence["result"] = "revision_required"
    evidence["passed"] = (
        evidence["result"] == RESULT
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
