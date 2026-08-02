"""Live-local GraphQL/PostgreSQL proof for the first product read."""

from __future__ import annotations

import argparse
import http.client
import json
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graphql.application_auth_product import (  # noqa: E402
    create_application_session_practitioner_directory_router,
)
from app.models.tenancy import (  # noqa: E402
    Practice,
    PracticeLocation,
    Practitioner,
    User,
    UserRole,
)
from app.services.application_auth_database_role import (  # noqa: E402
    create_deployment_login_role_statements,
    create_runtime_role_statements,
    drop_login_role_statement,
    drop_runtime_role_statement,
)
from app.services.application_auth_operational_database import (  # noqa: E402
    ApplicationAuthPoolPolicy,
    create_application_auth_engine,
    create_application_auth_session_factory,
)
from app.services.application_auth_product_read import (  # noqa: E402
    ApplicationSessionPractitionerDirectoryBridge,
    SyntheticProductPrincipalBinding,
    SyntheticProductPrincipalRegistry,
)
from app.services.application_auth_product_read_database_role import (  # noqa: E402
    create_product_read_capability_statements,
    create_product_read_login_statements,
    drop_product_read_role_statement,
)
from app.services.application_auth_product_read_operational import (  # noqa: E402
    ProductReadPoolPolicy,
    create_product_read_engine,
    create_product_read_session_factory,
)
from app.services.application_auth_role_runtime import (  # noqa: E402
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (  # noqa: E402
    Surface,
    SyntheticPrincipal,
)
from app.services.auth_service import hash_password  # noqa: E402
from scripts.raisa_postgresql_oidc_operational_connection_boundary_acceptance import (  # noqa: E402
    DATABASE_PATTERN,
    _base_database_url,
    _create_database,
    _drop_database,
    _require_alembic,
    _role_absent,
)
from scripts.raisa_provider_free_oidc_admission_grant_redemption_bridge_acceptance import (  # noqa: E402
    _start_server,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-session-practitioner-directory-read-bridge"
    / "live-local-http-backend-postgres-directory-evidence.json"
)
RESULT = "provider_free_session_practitioner_directory_read_bridge_pass"
MIGRATION_HEAD = "u0v1w2x3y4z5"
PARENT_HEAD = "t9u0v1w2x3y4"
NOW = datetime(2026, 8, 2, 14, 0, tzinfo=timezone.utc)
ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop-directory.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online-directory.synthetic.invalid",
    Surface.NATIVE_DIARY: "https://diary-directory.synthetic.invalid",
}
CSRF = "csrf." + "c" * 43
QUERY = """
query Directory($practiceId: ID, $activeOnly: Boolean = true) {
  practice(id: $practiceId) {
    practitioners(activeOnly: $activeOnly) {
      id
      displayName
      roleLabel
      active
      defaultLocation { id name }
    }
  }
}
"""

_AUTH_LOGIN = re.compile(r"^emr4_application_auth_login_[0-9a-f]{12}$")
_AUTH_CAPABILITY = re.compile(
    r"^emr4_application_auth_runtime_[0-9a-f]{12}$"
)
_PRODUCT_LOGIN = re.compile(r"^emr4_product_read_login_[0-9a-f]{12}$")
_PRODUCT_CAPABILITY = re.compile(
    r"^emr4_product_read_runtime_[0-9a-f]{12}$"
)


class AcceptanceFailure(RuntimeError):
    pass


def _post_graphql(
    port: int,
    *,
    surface_session: str,
    csrf: str = CSRF,
    origin: str | None = None,
    query: str = QUERY,
    variables: dict[str, object] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        connection.request(
            "POST",
            "/api/v1/application-auth/product/graphql",
            body=json.dumps(
                {
                    "query": query,
                    "variables": variables or {},
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Origin": origin or ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": csrf,
                "X-EMR4-Correlation-ID": "correlation-directory-http",
                "Cookie": (
                    f"__Host-emr4-application-session={surface_session}; "
                    f"__Host-emr4-application-csrf={CSRF}"
                ),
            },
        )
        response = connection.getresponse()
        body = response.read()
        headers = {key.lower(): value for key, value in response.getheaders()}
        return response.status, headers, body
    finally:
        connection.close()


def _seed_product(owner_factory: sessionmaker[Session]) -> dict[str, Any]:
    with owner_factory() as db, db.begin():
        practice = Practice(name="Authored Synthetic Practice")
        other_practice = Practice(name="Other Synthetic Practice")
        db.add_all((practice, other_practice))
        db.flush()
        location = PracticeLocation(
            practice_id=practice.id,
            name="Synthetic Main Clinic",
            is_active=True,
        )
        db.add(location)
        db.flush()
        linked = Practitioner(
            practice_id=practice.id,
            first_name="Alpha",
            last_name="Synthetic",
            specialty="GP",
            default_location_id=location.id,
            is_active=True,
            provider_number="SYNTH-PROVIDER-001",
            prescriber_number="SYNTH-PRESCRIBE-01",
            ahpra_number="SYNTH-AHPRA-001",
            hpi_i="SYNTH-HPII-001",
        )
        second = Practitioner(
            practice_id=practice.id,
            first_name="Beta",
            last_name="Synthetic",
            specialty="GP",
            is_active=True,
        )
        inactive = Practitioner(
            practice_id=practice.id,
            first_name="Inactive",
            last_name="Synthetic",
            specialty="GP",
            is_active=False,
        )
        other = Practitioner(
            practice_id=other_practice.id,
            first_name="Foreign",
            last_name="Synthetic",
            specialty="GP",
            is_active=True,
        )
        db.add_all((linked, second, inactive, other))
        db.flush()
        user = User(
            practice_id=practice.id,
            email="gp-directory@authored-synthetic.invalid",
            password_hash=hash_password("AuthoredSyntheticOnly1!"),
            role=UserRole.GP,
            practitioner_id=linked.id,
            is_active=True,
        )
        db.add(user)
        db.flush()
        return {
            "practice_id": practice.id,
            "other_practice_id": other_practice.id,
            "user_id": user.id,
            "linked_practitioner_id": linked.id,
            "expected_ids": {linked.id, second.id},
            "other_practitioner_id": other.id,
        }


def _probe_sqlstate(engine: Engine, statement: str) -> str | None:
    try:
        with engine.connect() as connection:
            connection.execute(text(statement)).first()
    except DBAPIError as exc:
        return getattr(exc.orig, "sqlstate", None) or getattr(
            exc.orig,
            "pgcode",
            None,
        )
    return None


def _drop_role(
    maintenance: Engine,
    role_name: str,
    *,
    kind: str,
) -> bool:
    patterns = {
        "auth_login": _AUTH_LOGIN,
        "auth_capability": _AUTH_CAPABILITY,
        "product_login": _PRODUCT_LOGIN,
        "product_capability": _PRODUCT_CAPABILITY,
    }
    if kind not in patterns or not patterns[kind].fullmatch(role_name):
        raise AcceptanceFailure("unsafe_role_cleanup_name")
    with maintenance.begin() as connection:
        present = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
            {"name": role_name},
        ).scalar_one_or_none()
        if present is not None:
            if kind == "auth_login":
                statement = drop_login_role_statement(role_name)
            elif kind == "auth_capability":
                statement = drop_runtime_role_statement(role_name)
            else:
                statement = drop_product_read_role_statement(role_name)
            connection.execute(text(statement))
    return _role_absent(maintenance, role_name)


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_oidc_operational_acceptance_{suffix}"
    auth_login = f"emr4_application_auth_login_{suffix}"
    auth_capability = f"emr4_application_auth_runtime_{suffix}"
    product_login = f"emr4_product_read_login_{suffix}"
    product_capability = f"emr4_product_read_runtime_{suffix}"
    auth_password = secrets.token_urlsafe(36)
    product_password = secrets.token_urlsafe(36)
    base = _base_database_url()
    target = base.set(database=database_name)
    auth_target = target.set(username=auth_login, password=auth_password)
    product_target = target.set(
        username=product_login,
        password=product_password,
    )
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    auth_engine: Engine | None = None
    product_engine: Engine | None = None
    direct_product_login_engine: Engine | None = None
    server = None
    listener = None
    server_thread = None
    database_created = False
    created_roles: list[tuple[str, str]] = []
    raw_values: list[str] = []
    failure_type: str | None = None
    stage = "preflight"
    evidence: dict[str, Any] = {
        "schema_version": (
            "emr4.provider-free-session-practitioner-directory-read-bridge-evidence.v1"
        ),
        "result": "revision_required",
        "evidence_label": "live_local_http_backend_postgres_product_read",
        "data_class": "authored_synthetic",
        "default_off": True,
        "cleanup": {
            "server_stopped": False,
            "database_absent_after": False,
            "task_roles_absent_after": False,
        },
    }
    try:
        if not all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                _AUTH_LOGIN.fullmatch(auth_login),
                _AUTH_CAPABILITY.fullmatch(auth_capability),
                _PRODUCT_LOGIN.fullmatch(product_login),
                _PRODUCT_CAPABILITY.fullmatch(product_capability),
            )
        ):
            raise AcceptanceFailure("generated_identifier_invalid")
        _create_database(maintenance, database_name)
        database_created = True
        stage = "migration"
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        _require_alembic(target, "downgrade", PARENT_HEAD)
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        if MIGRATION_HEAD not in current:
            raise AcceptanceFailure("migration_head_mismatch")

        owner = create_engine(target, pool_pre_ping=True)
        owner_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=owner,
        )
        stage = "roles"
        with owner.begin() as connection:
            for statement in create_runtime_role_statements(auth_capability):
                connection.execute(text(statement))
            created_roles.append((auth_capability, "auth_capability"))
            for statement in create_deployment_login_role_statements(
                auth_login,
                auth_capability,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            created_roles.append((auth_login, "auth_login"))
            connection.execute(
                text(f'ALTER ROLE "{auth_login}" PASSWORD \'{auth_password}\'')
            )
            for statement in create_product_read_capability_statements(
                product_capability
            ):
                connection.execute(text(statement))
            created_roles.append((product_capability, "product_capability"))
            for statement in create_product_read_login_statements(
                product_login,
                product_capability,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            created_roles.append((product_login, "product_login"))
            connection.execute(
                text(
                    f'ALTER ROLE "{product_login}" PASSWORD '
                    f"'{product_password}'"
                )
            )

        stage = "synthetic_product_seed"
        seeded = _seed_product(owner_factory)
        auth_engine = create_application_auth_engine(
            auth_target.render_as_string(hide_password=False),
            login_role=auth_login,
            capability_role=auth_capability,
            policy=ApplicationAuthPoolPolicy(
                pool_size=2,
                max_overflow=0,
                login_connection_limit=2,
            ),
        )
        auth_runtime = RoleScopedPostgresApplicationAuthRuntime(
            session_factory=create_application_auth_session_factory(auth_engine),
            surface_origins=ORIGINS,
            clock=lambda: NOW,
        )
        principal = SyntheticPrincipal(
            user_id="synthetic-user-directory-gp",
            practice_id="synthetic-practice-directory-one",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-directory-gp",
        )
        created = auth_runtime.create_session(
            principal=principal,
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
            correlation_id="correlation-directory-session",
        )
        raw_values.extend((created.parent_session_value, created.surface_session_value, CSRF))

        product_engine = create_product_read_engine(
            product_target,
            login_role=product_login,
            capability_role=product_capability,
            policy=ProductReadPoolPolicy(
                pool_size=2,
                max_overflow=0,
                login_connection_limit=2,
            ),
        )
        bridge = ApplicationSessionPractitionerDirectoryBridge(
            runtime=auth_runtime,
            product_session_factory=create_product_read_session_factory(
                product_engine
            ),
            principal_registry=SyntheticProductPrincipalRegistry(
                (
                    SyntheticProductPrincipalBinding(
                        user_ref=principal.user_id,
                        practice_ref=principal.practice_id,
                        user_id=seeded["user_id"],
                        practice_id=seeded["practice_id"],
                        practitioner_ref=principal.practitioner_id,
                        practitioner_id=seeded["linked_practitioner_id"],
                    ),
                )
            ),
            surface_origins=ORIGINS,
        )
        application = FastAPI()
        application.include_router(
            create_application_session_practitioner_directory_router(
                bridge=bridge,
                surface=Surface.WORD_ONLINE,
            )
        )
        stage = "live_http"
        server, listener, server_thread, port = _start_server(application)

        allowed = _post_graphql(
            port,
            surface_session=created.surface_session_value,
        )
        allowed_json = json.loads(allowed[2])
        rows = allowed_json.get("data", {}).get("practice", {}).get(
            "practitioners",
            [],
        )
        row_ids = {row["id"] for row in rows}
        expected_ids = {str(value) for value in seeded["expected_ids"]}
        allowed_exact = (
            allowed[0] == 200
            and "errors" not in allowed_json
            and row_ids == expected_ids
            and len(rows) == 2
            and allowed[1].get("cache-control") == "no-store"
        )
        safe_keys = {
            "id",
            "displayName",
            "roleLabel",
            "active",
            "defaultLocation",
        }
        exact_projection = all(set(row) == safe_keys for row in rows)

        wrong_origin = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            origin="https://foreign.synthetic.invalid",
        )
        wrong_csrf = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            csrf="csrf." + "w" * 43,
        )
        schema_escape = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            query="{ graphqlHealth { status authenticated } }",
        )
        unknown = _post_graphql(
            port,
            surface_session="ass." + "u" * 48,
        )
        cross_practice = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            variables={"practiceId": str(seeded["other_practice_id"])},
        )
        cross_json = json.loads(cross_practice[2])
        inactive = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            variables={"activeOnly": False},
        )
        inactive_json = json.loads(inactive[2])

        unmapped_principal = SyntheticPrincipal(
            user_id="synthetic-user-directory-unmapped",
            practice_id="synthetic-practice-directory-unmapped",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-directory-unmapped",
        )
        unmapped_session = auth_runtime.create_session(
            principal=unmapped_principal,
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
            correlation_id="correlation-directory-unmapped",
        )
        raw_values.extend(
            (
                unmapped_session.parent_session_value,
                unmapped_session.surface_session_value,
            )
        )
        unmapped = _post_graphql(
            port,
            surface_session=unmapped_session.surface_session_value,
        )

        stage = "fresh_truth_failures"
        with owner.begin() as connection:
            connection.execute(
                text("UPDATE users SET role = 'Receptionist' WHERE id = :id"),
                {"id": seeded["user_id"]},
            )
        stale_role = _post_graphql(
            port,
            surface_session=created.surface_session_value,
        )
        with owner.begin() as connection:
            connection.execute(
                text("UPDATE users SET role = 'GP', is_active = false WHERE id = :id"),
                {"id": seeded["user_id"]},
            )
        inactive_user = _post_graphql(
            port,
            surface_session=created.surface_session_value,
        )
        with owner.begin() as connection:
            connection.execute(
                text("UPDATE users SET is_active = true WHERE id = :id"),
                {"id": seeded["user_id"]},
            )

        stage = "audit_failure"
        with owner.begin() as connection:
            connection.execute(
                text(
                    "REVOKE INSERT ON TABLE application_auth_audit_events "
                    f'FROM "{auth_capability}"'
                )
            )
        audit_failed = _post_graphql(
            port,
            surface_session=created.surface_session_value,
        )
        with owner.begin() as connection:
            connection.execute(
                text(
                    "GRANT INSERT ON TABLE application_auth_audit_events "
                    f'TO "{auth_capability}"'
                )
            )

        stage = "database_assertions"
        with owner.connect() as connection:
            directory_events = tuple(
                tuple(row)
                for row in connection.execute(
                    text(
                        "SELECT event_type, action, resource_type, policy_version, "
                        "decision, reason_codes FROM application_auth_audit_events "
                        "WHERE policy_version = "
                        "'practice-practitioner-directory-read.v1' "
                        "ORDER BY id"
                    )
                )
            )
            raw_residue = json.dumps(
                [
                    tuple(row)
                    for row in connection.execute(
                        text(
                            "SELECT session_reference_hash, correlation_id, "
                            "event_type, action, resource_type, policy_version, "
                            "decision, reason_codes "
                            "FROM application_auth_audit_events ORDER BY id"
                        )
                    )
                ],
                default=str,
            )

        direct_product_login_engine = create_engine(product_target)
        role_probe_states = {
            "product_login_direct_directory": _probe_sqlstate(
                direct_product_login_engine,
                "SELECT id FROM practitioners LIMIT 1",
            ),
            "product_capability_sensitive_provider": _probe_sqlstate(
                product_engine,
                "SELECT provider_number FROM practitioners LIMIT 1",
            ),
            "product_capability_sensitive_user": _probe_sqlstate(
                product_engine,
                "SELECT email FROM users LIMIT 1",
            ),
            "product_capability_write": _probe_sqlstate(
                product_engine,
                "UPDATE practitioners SET is_active = false",
            ),
            "product_capability_auth_state": _probe_sqlstate(
                product_engine,
                "SELECT session_reference_hash FROM application_auth_parent_sessions LIMIT 1",
            ),
            "auth_capability_product_table": _probe_sqlstate(
                auth_engine,
                "SELECT id FROM practitioners LIMIT 1",
            ),
        }

        failure_contract = {
            "wrong_origin_no_data": wrong_origin[0] == 403,
            "wrong_csrf_no_data": wrong_csrf[0] == 403,
            "schema_escape_no_data": schema_escape[0] == 403,
            "unknown_session_no_data": unknown[0] == 401,
            "unmapped_session_no_data": unmapped[0] == 401,
            "stale_role_no_data": stale_role[0] == 401,
            "inactive_user_no_data": inactive_user[0] == 401,
            "audit_failure_no_data": audit_failed[0] == 503,
            "cross_practice_no_leak": (
                cross_practice[0] == 200
                and cross_json.get("data", {}).get("practice") is None
                and str(seeded["other_practitioner_id"])
                not in cross_practice[2].decode("utf-8")
            ),
            "inactive_enumeration_forbidden": (
                inactive[0] == 200
                and (
                    (inactive_json.get("data") or {}).get("practice") or {}
                ).get("practitioners")
                is None
                and inactive_json.get("errors", [{}])[0]
                .get("extensions", {})
                .get("code")
                == "FORBIDDEN"
            ),
        }
        audit_contract = {
            "allowed_event_committed": any(
                event[0] == "auth.authorization_allowed"
                and event[1] == "practice.practitioner-directory.read"
                and event[2] == "practitioner_directory"
                and event[3] == "practice-practitioner-directory-read.v1"
                and event[4] == "allowed"
                for event in directory_events
            ),
            "denied_event_committed": any(
                event[0] == "auth.authorization_denied"
                and event[4] == "denied"
                for event in directory_events
            ),
            "audit_contains_no_product_fields": not any(
                marker in raw_residue
                for marker in (
                    "SYNTH-PROVIDER-001",
                    "SYNTH-PRESCRIBE-01",
                    "SYNTH-AHPRA-001",
                    "SYNTH-HPII-001",
                    "@authored-synthetic.invalid",
                    "Alpha Synthetic",
                    "Beta Synthetic",
                )
            ),
            "raw_session_and_csrf_absent": all(
                value not in raw_residue for value in raw_values
            ),
        }
        role_contract = {
            "six_direct_privilege_denials": len(role_probe_states) == 6,
            "all_direct_denials_are_insufficient_privilege": set(
                role_probe_states.values()
            )
            == {"42501"},
            "role_names_recorded": False,
        }
        passed = all(
            (
                allowed_exact,
                exact_projection,
                all(failure_contract.values()),
                all(audit_contract.values()),
                role_contract["all_direct_denials_are_insufficient_privilege"],
            )
        )
        evidence.update(
            {
                "result": RESULT if passed else "revision_required",
                "migration_head": MIGRATION_HEAD,
                "loopback_http": {
                    "real_socket": True,
                    "host": "127.0.0.1",
                    "ephemeral_port_recorded": False,
                    "request_count": 11,
                },
                "allowed_read": {
                    "active_practitioner_count": len(rows),
                    "exact_display_safe_projection": exact_projection,
                    "shared_graphql_service_path": True,
                    "required_audit_before_release": True,
                    "patient_or_clinical_fields": 0,
                },
                "failure_contract": failure_contract,
                "failure_statuses": {
                    "wrong_origin": wrong_origin[0],
                    "wrong_csrf": wrong_csrf[0],
                    "schema_escape": schema_escape[0],
                    "unknown_session": unknown[0],
                    "unmapped_session": unmapped[0],
                    "stale_role": stale_role[0],
                    "inactive_user": inactive_user[0],
                    "audit_failure": audit_failed[0],
                },
                "audit_contract": audit_contract,
                "role_contract": role_contract,
                "side_effect_counts": {
                    "provider_calls": 0,
                    "real_identities": 0,
                    "patient_or_clinical_reads": 0,
                    "product_reads": 1,
                    "product_writes_by_runtime": 0,
                    "graphql_mutations": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "This proves one default-off provider-free authored-synthetic application-session-authorized active practitioner-directory read through real loopback GraphQL and disposable PostgreSQL.",
                    "It does not establish patient or clinical read safety, real principal mapping, general GraphQL mounting, product-table RLS, live Microsoft interoperability, deployment, production or release readiness."
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        sensitive_values = (
            database_name,
            auth_login,
            auth_capability,
            product_login,
            product_capability,
            auth_password,
            product_password,
            *raw_values,
            *(str(value) for value in seeded.values() if not isinstance(value, set)),
        )
        evidence_sensitive_match_count = sum(
            value in serialized for value in sensitive_values
        )
        evidence["evidence_sensitive_match_count"] = evidence_sensitive_match_count
        if evidence_sensitive_match_count:
            raise AcceptanceFailure("sensitive_value_in_evidence")
        if not passed:
            raise AcceptanceFailure("one_or_more_acceptance_gates_failed")
    except Exception as exc:
        failure_type = type(exc).__name__
        evidence["result"] = "revision_required"
        evidence["failure_type"] = failure_type
        evidence["failure_stage"] = stage
        if isinstance(exc, AcceptanceFailure):
            evidence["failure_code"] = str(exc)
    finally:
        if server is not None:
            server.should_exit = True
        if server_thread is not None:
            server_thread.join(timeout=10)
            evidence["cleanup"]["server_stopped"] = not server_thread.is_alive()
        else:
            evidence["cleanup"]["server_stopped"] = True
        if listener is not None:
            listener.close()
        for engine in (
            direct_product_login_engine,
            product_engine,
            auth_engine,
            owner,
        ):
            if engine is not None:
                engine.dispose()
        if database_created:
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance,
                    database_name,
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = True
        role_absence: list[bool] = []
        for role_name, kind in reversed(created_roles):
            try:
                role_absence.append(
                    _drop_role(
                        maintenance,
                        role_name,
                        kind=kind,
                    )
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["role_failure_type"] = type(
                    cleanup_exc
                ).__name__
                role_absence.append(False)
        evidence["cleanup"]["task_roles_absent_after"] = all(role_absence)
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(evidence["cleanup"].values())
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
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
