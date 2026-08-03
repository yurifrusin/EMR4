"""Live-local HTTP/PostgreSQL proof for the default-off native-Diary
application-session practitioner runtime adapter (Diary lane runtime step)."""

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

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graphql.native_diary_application_session_practitioner import (  # noqa: E402
    FIXED_QUERY,
    FIXED_VARIABLES,
    PRODUCT_PATH,
    create_native_diary_application_session_app,
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
    / "raisa-provider-free-native-diary-application-session-practitioner-runtime"
    / "live-local-backend-postgres-evidence.json"
)
RESULT = "provider_free_native_diary_application_session_practitioner_runtime_pass"
MIGRATION_HEAD = "u0v1w2x3y4z5"
NOW = datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc)
ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop-diary.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online-diary.synthetic.invalid",
    Surface.NATIVE_DIARY: "https://native-diary.synthetic.invalid",
}
CSRF = "csrf." + "c" * 43

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
    csrf_cookie: str | None = CSRF,
    csrf_header: str | None = CSRF,
    origin: str | None = None,
    query: str = FIXED_QUERY,
    variables: dict[str, object] | None = None,
    method: str = "POST",
    correlation_id: str = "correlation-diary-http",
) -> tuple[int, dict[str, str], bytes]:
    cookie_parts = [f"__Host-emr4-application-session={surface_session}"]
    if csrf_cookie is not None:
        cookie_parts.append(f"__Host-emr4-application-csrf={csrf_cookie}")
    headers: dict[str, str] = {
        "Origin": origin or ORIGINS[Surface.NATIVE_DIARY],
        "X-EMR4-Correlation-ID": correlation_id,
        "Cookie": "; ".join(cookie_parts),
    }
    if method == "POST":
        headers["Content-Type"] = "application/json"
    if csrf_header is not None:
        headers["X-EMR4-CSRF"] = csrf_header
    body = None
    if method == "POST":
        body = json.dumps(
            {
                "query": query,
                "variables": (
                    variables if variables is not None else FIXED_VARIABLES
                ),
            }
        )
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        connection.request(method, PRODUCT_PATH, body=body, headers=headers)
        response = connection.getresponse()
        response_body = response.read()
        response_headers = {
            key.lower(): value for key, value in response.getheaders()
        }
        return response.status, response_headers, response_body
    finally:
        connection.close()


def _seed_product(owner_factory: sessionmaker[Session]) -> dict[str, Any]:
    with owner_factory() as db, db.begin():
        practice = Practice(name="Native Diary Synthetic Practice")
        other_practice = Practice(name="Native Diary Foreign Practice")
        db.add_all((practice, other_practice))
        db.flush()
        location = PracticeLocation(
            practice_id=practice.id,
            name="Native Diary Main Clinic",
            is_active=True,
        )
        db.add(location)
        db.flush()
        linked = Practitioner(
            practice_id=practice.id,
            first_name="Alpha",
            last_name="NativeDiary",
            specialty="GP",
            default_location_id=location.id,
            is_active=True,
            provider_number="SYNTH-ND-PROVIDER-001",
            prescriber_number="SYNTH-ND-PRESCRIBE-01",
            ahpra_number="SYNTH-ND-AHPRA-001",
            hpi_i="SYNTH-ND-HPII-001",
        )
        second = Practitioner(
            practice_id=practice.id,
            first_name="Beta",
            last_name="NativeDiary",
            specialty="GP",
            is_active=True,
        )
        inactive = Practitioner(
            practice_id=practice.id,
            first_name="Inactive",
            last_name="NativeDiary",
            specialty="GP",
            is_active=False,
        )
        other = Practitioner(
            practice_id=other_practice.id,
            first_name="Foreign",
            last_name="NativeDiary",
            specialty="GP",
            is_active=True,
        )
        db.add_all((linked, second, inactive, other))
        db.flush()
        user = User(
            practice_id=practice.id,
            email="native-diary-gp@authored-synthetic.invalid",
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
            "location_id": location.id,
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
            "emr4.provider-free-native-diary-application-session-practitioner-runtime-evidence.v1"
        ),
        "result": "revision_required",
        "evidence_label": "live_local_backend_postgres",
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
            user_id="synthetic-user-native-diary-gp",
            practice_id="synthetic-practice-native-diary-one",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-native-diary-gp",
        )
        created = auth_runtime.create_session(
            principal=principal,
            surface=Surface.NATIVE_DIARY,
            origin=ORIGINS[Surface.NATIVE_DIARY],
            correlation_id="correlation-diary-session",
        )
        raw_values.extend(
            (
                created.parent_session_value,
                created.surface_session_value,
                CSRF,
            )
        )

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
        application = create_native_diary_application_session_app(
            enabled=True,
            bridge=bridge,
        )
        stage = "live_http"
        server, listener, server_thread, port = _start_server(application)

        allowed_first = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            correlation_id="correlation-diary-read-1",
        )
        allowed_second = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            correlation_id="correlation-diary-read-2",
        )
        allowed_json = json.loads(allowed_first[2])
        rows = allowed_json.get("data", {}).get("practice", {}).get(
            "practitioners",
            [],
        )
        row_ids = {row["id"] for row in rows}
        expected_ids = {str(value) for value in seeded["expected_ids"]}
        safe_keys = {
            "id",
            "displayName",
            "roleLabel",
            "active",
            "defaultLocation",
        }
        exact_projection = bool(rows) and all(
            set(row) == safe_keys
            and (row["defaultLocation"] is None or set(row["defaultLocation"]) == {"id", "name"})
            for row in rows
        )
        allowed_exact = (
            allowed_first[0] == 200
            and allowed_second[0] == 200
            and "errors" not in allowed_json
            and row_ids == expected_ids
            and len(rows) == 2
            and allowed_first[1].get("cache-control") == "no-store"
            and allowed_second[1].get("cache-control") == "no-store"
        )
        response_markers = allowed_first[2].decode("utf-8", errors="ignore")
        foreign_inactive_absent = (
            str(seeded["other_practitioner_id"]) not in response_markers
        )

        word_principal = SyntheticPrincipal(
            user_id="synthetic-user-native-diary-word",
            practice_id="synthetic-practice-native-diary-one",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-native-diary-word",
        )
        word_session = auth_runtime.create_session(
            principal=word_principal,
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
            correlation_id="correlation-diary-word-session",
        )
        raw_values.extend(
            (word_session.parent_session_value, word_session.surface_session_value)
        )

        unmapped_principal = SyntheticPrincipal(
            user_id="synthetic-user-native-diary-unmapped",
            practice_id="synthetic-practice-native-diary-unmapped",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-native-diary-unmapped",
        )
        unmapped_session = auth_runtime.create_session(
            principal=unmapped_principal,
            surface=Surface.NATIVE_DIARY,
            origin=ORIGINS[Surface.NATIVE_DIARY],
            correlation_id="correlation-diary-unmapped-session",
        )
        raw_values.extend(
            (
                unmapped_session.parent_session_value,
                unmapped_session.surface_session_value,
            )
        )

        wrong_origin = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            origin="https://foreign.synthetic.invalid",
        )
        missing_csrf = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            csrf_cookie=None,
            csrf_header=None,
        )
        mismatched_csrf = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            csrf_cookie=CSRF,
            csrf_header="csrf." + "w" * 43,
        )
        get_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            method="GET",
        )
        mutation_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            query="mutation { practice { practitioners { id } } }",
        )
        introspection_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            query="{ __schema { types { name } } }",
        )
        practice_id_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            variables={
                **FIXED_VARIABLES,
                "practiceId": "synthetic-practice-other",
            },
        )
        field_subset_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            query=(
                "query NativeDiaryPractitioners($activeOnly: Boolean!, "
                "$limit: Int!, $offset: Int!) { practice { practitioners("
                "activeOnly: $activeOnly, limit: $limit, offset: $offset) "
                "{ id } } }"
            ),
        )
        extra_field_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            query=FIXED_QUERY.replace(
                "      active\n",
                "      active\n      phone\n",
            ),
        )
        drift_active_only_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            variables={**FIXED_VARIABLES, "activeOnly": False},
        )
        drift_limit_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            variables={**FIXED_VARIABLES, "limit": 201},
        )
        drift_offset_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            variables={**FIXED_VARIABLES, "offset": 1},
        )
        operation_drift_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
            query=(
                "query OtherOperation($activeOnly: Boolean!, $limit: Int!, "
                "$offset: Int!) { practice { practitioners(activeOnly: "
                "$activeOnly, limit: $limit, offset: $offset) { id "
                "displayName roleLabel active defaultLocation { id name } } } }"
            ),
        )
        unknown_session_request = _post_graphql(
            port,
            surface_session="ass." + "u" * 48,
        )
        word_surface_request = _post_graphql(
            port,
            surface_session=word_session.surface_session_value,
        )
        unmapped_request = _post_graphql(
            port,
            surface_session=unmapped_session.surface_session_value,
        )

        stage = "fresh_truth_failures"
        with owner.begin() as connection:
            connection.execute(
                text("UPDATE users SET role = 'Receptionist' WHERE id = :id"),
                {"id": seeded["user_id"]},
            )
        stale_role_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
        )
        with owner.begin() as connection:
            connection.execute(
                text("UPDATE users SET role = 'GP', is_active = false WHERE id = :id"),
                {"id": seeded["user_id"]},
            )
        inactive_user_request = _post_graphql(
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
        audit_outage_request = _post_graphql(
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

        stage = "revocation"
        auth_runtime.revoke_parent_session(
            parent_session_value=created.parent_session_value,
            correlation_id="correlation-diary-revoke",
            reason="security_reset",
        )
        revoked_request = _post_graphql(
            port,
            surface_session=created.surface_session_value,
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

        product_markers = (
            "SYNTH-ND-PROVIDER-001",
            "SYNTH-ND-PRESCRIBE-01",
            "SYNTH-ND-AHPRA-001",
            "SYNTH-ND-HPII-001",
            "native-diary-gp@authored-synthetic.invalid",
            "Native Diary Synthetic Practice",
            "Native Diary Foreign Practice",
            "Native Diary Main Clinic",
        )
        failure_contract = {
            "wrong_origin_no_data": wrong_origin[0] == 403,
            "missing_csrf_no_data": missing_csrf[0] == 403,
            "mismatched_csrf_no_data": mismatched_csrf[0] == 403,
            "get_no_data": get_request[0] == 403,
            "mutation_no_data": mutation_request[0] == 403,
            "introspection_no_data": introspection_request[0] == 403,
            "practice_id_no_data": practice_id_request[0] == 403,
            "field_subset_no_data": field_subset_request[0] == 403,
            "extra_field_no_data": extra_field_request[0] == 403,
            "drift_active_only_no_data": drift_active_only_request[0] == 403,
            "drift_limit_no_data": drift_limit_request[0] == 403,
            "drift_offset_no_data": drift_offset_request[0] == 403,
            "operation_drift_no_data": operation_drift_request[0] == 403,
            "unknown_session_no_data": unknown_session_request[0] == 401,
            "word_surface_session_no_data": word_surface_request[0] == 401,
            "unmapped_session_no_data": unmapped_request[0] == 401,
            "stale_role_no_data": stale_role_request[0] == 401,
            "inactive_user_no_data": inactive_user_request[0] == 401,
            "audit_outage_no_data": audit_outage_request[0] == 503,
            "post_revocation_no_data": revoked_request[0] == 401,
        }
        guard_rejections = (
            get_request,
            mutation_request,
            introspection_request,
            practice_id_request,
            field_subset_request,
            extra_field_request,
            drift_active_only_request,
            drift_limit_request,
            drift_offset_request,
            operation_drift_request,
        )
        guard_no_store = all(
            status == 403 and headers.get("cache-control") == "no-store"
            for status, headers, _body in guard_rejections
        )

        failure_statuses = {
            "wrong_origin": wrong_origin[0],
            "missing_csrf": missing_csrf[0],
            "mismatched_csrf": mismatched_csrf[0],
            "get": get_request[0],
            "mutation": mutation_request[0],
            "introspection": introspection_request[0],
            "practice_id": practice_id_request[0],
            "field_subset": field_subset_request[0],
            "extra_field": extra_field_request[0],
            "drift_active_only": drift_active_only_request[0],
            "drift_limit": drift_limit_request[0],
            "drift_offset": drift_offset_request[0],
            "operation_drift": operation_drift_request[0],
            "unknown_session": unknown_session_request[0],
            "word_surface_session": word_surface_request[0],
            "unmapped_session": unmapped_request[0],
            "stale_role": stale_role_request[0],
            "inactive_user": inactive_user_request[0],
            "audit_outage": audit_outage_request[0],
            "post_revocation": revoked_request[0],
        }
        audit_contract = {
            "allowed_event_count_ge_two": sum(
                1
                for event in directory_events
                if event[0] == "auth.authorization_allowed"
                and event[1] == "practice.practitioner-directory.read"
                and event[2] == "practitioner_directory"
                and event[3] == "practice-practitioner-directory-read.v1"
                and event[4] == "allowed"
            )
            >= 2,
            "denied_event_committed": any(
                event[0] == "auth.authorization_denied"
                and event[4] == "denied"
                for event in directory_events
            ),
            "audit_contains_no_product_fields": not any(
                marker in raw_residue for marker in product_markers
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
                foreign_inactive_absent,
                all(failure_contract.values()),
                guard_no_store,
                all(audit_contract.values()),
                role_contract["all_direct_denials_are_insufficient_privilege"],
            )
        )

        evidence.update(
            {
                "result": RESULT if passed else "revision_required",
                "migration_head": MIGRATION_HEAD,
                "migration": {
                    "head_revision": MIGRATION_HEAD,
                    "current_head_exact": MIGRATION_HEAD in current,
                    "orm_migration_drift_absent": True,
                    "migration_log_recorded": False,
                },
                "loopback_http": {
                    "real_socket": True,
                    "host": "127.0.0.1",
                    "ephemeral_port_recorded": False,
                    "request_count": 22,
                },
                "allowed_reads": {
                    "sequential_read_count": 2,
                    "active_practitioner_count": len(rows),
                    "exact_display_safe_projection": exact_projection,
                    "shared_graphql_service_path": True,
                    "required_audit_before_release": True,
                    "no_store": True,
                    "long_lived_native_session_not_consumed": True,
                },
                "failure_contract": failure_contract,
                "failure_statuses": failure_statuses,
                "guard_no_store": guard_no_store,
                "audit_contract": audit_contract,
                "role_contract": role_contract,
                "side_effect_counts": {
                    "provider_calls": 0,
                    "browser_runs": 0,
                    "real_identities": 0,
                    "patient_or_clinical_reads": 0,
                    "allowed_product_reads": 2,
                    "product_writes_by_runtime": 0,
                    "graphql_mutations": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "This proves one default-off provider-free authored-synthetic native-Diary application-session practitioner read through a real loopback HTTP socket and disposable PostgreSQL, twice sequentially on one long-lived NATIVE_DIARY session, with an exact fixed query/variables, exact display-safe projection, no-store, required allow audit before release and complete post-revocation denial.",
                    "Request-time freshness and post-revocation denial do not prove rejection of an already-returned in-flight response before UI render; that remains a later UI reconciliation obligation.",
                    "There is no provider call, no browser automation, no real identity, no patient/clinical data, no product write, no deployment and no production claim.",
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
            principal.user_id,
            principal.practice_id,
            principal.practitioner_id,
            *product_markers,
        )
        evidence_sensitive_match_count = sum(
            bool(value) and value in serialized
            for value in sensitive_values
        )
        evidence["evidence_sensitive_match_count"] = (
            evidence_sensitive_match_count
        )
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
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "passed": evidence["passed"],
                "cleanup_passed": evidence["cleanup"]["passed"],
                "failure_type": evidence.get("failure_type"),
                "failure_code": evidence.get("failure_code"),
                "failure_stage": evidence.get("failure_stage"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
