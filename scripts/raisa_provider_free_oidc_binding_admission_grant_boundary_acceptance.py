"""Live-local HTTP/PostgreSQL proof for HMAC binding and admission grants."""

from __future__ import annotations

import argparse
import json
import re
import secrets
import socket
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urlsplit

import uvicorn
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_identity_federation import (  # noqa: E402
    FEDERATION_PROVIDER,
    POLICY_VERSION,
    FederationReferenceHasher,
)
from app.services.application_identity_oidc_adapter import (  # noqa: E402
    CompletedAuthorization,
    InMemoryOIDCAdapterAuditSink,
    MicrosoftOIDCAdapterConfig,
    ReturnTarget,
    Surface,
    TwoComponentOIDCAdapter,
    VerifiedMicrosoftPrincipal,
)
from app.services.application_identity_oidc_admission_grant import (  # noqa: E402
    AdmissionGrantDigestKey,
    OIDCBindingAdmissionConfiguration,
    PostgresOIDCBindingAdmissionService,
)
from app.services.application_identity_oidc_attempt_database_role import (  # noqa: E402
    create_oidc_attempt_deployment_login_statements,
    create_oidc_attempt_runtime_role_statements,
)
from app.services.application_identity_oidc_attempt_operational import (  # noqa: E402
    PostgresAuthorizationAttemptRuntime,
    build_postgres_authorization_attempt_runtime,
)
from app.services.application_identity_oidc_binding_database_role import (  # noqa: E402
    create_binding_admission_capability_statements,
    create_binding_admission_login_statements,
    drop_binding_admission_role_statement,
)
from app.services.application_identity_oidc_binding_operational import (  # noqa: E402
    create_oidc_binding_admission_engine,
    create_oidc_binding_admission_session_factory,
)
from app.services.application_identity_oidc_transport import (  # noqa: E402
    OIDCStartCallbackTransport,
)
from app.services.application_identity_oidc_adapter import (  # noqa: E402
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
)
from scripts.raisa_postgresql_oidc_operational_connection_boundary_acceptance import (  # noqa: E402
    CAPABILITY_PATTERN,
    DATABASE_PATTERN,
    LOGIN_PATTERN,
    _SyntheticSecretProvider,
    _base_database_url,
    _create_database,
    _drop_database,
    _drop_role,
    _materials,
    _operational_configuration,
    _references,
    _require_alembic,
    _role_absent,
)
from scripts.raisa_provider_free_oidc_start_callback_transport_boundary_acceptance import (  # noqa: E402
    CALLBACK,
    ORIGINS,
    TENANT,
    CLIENT,
    _DenialSink,
    _Protocol,
    _Verifier,
    _application,
    _callback,
    _start,
    _start_server,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-oidc-binding-admission-grant-boundary"
    / "live-local-http-backend-postgres-evidence.json"
)
RESULT = "provider_free_oidc_binding_admission_grant_boundary_pass"
PARENT_MIGRATION_HEAD = "s8t9u0v1w2x3"
MIGRATION_HEAD = "t9u0v1w2x3y4"

_BINDING_LOGIN = re.compile(r"^emr4_oidc_binding_login_[0-9a-f]{12}$")
_RESOLVER_CALL = re.compile(r"^emr4_oidc_binding_resolver_call_[0-9a-f]{12}$")
_RESOLVER_OWNER = re.compile(r"^emr4_oidc_binding_resolver_owner_[0-9a-f]{12}$")
_GRANT_ISSUER = re.compile(r"^emr4_oidc_grant_issuer_[0-9a-f]{12}$")
_RAW_GRANT = re.compile(r'"admission_grant":"([A-Za-z0-9_-]{43})"')


class AcceptanceFailure(RuntimeError):
    pass


def _seed_binding(
    owner: Engine,
    *,
    hasher: FederationReferenceHasher,
    adapter_config: MicrosoftOIDCAdapterConfig,
) -> dict[str, str]:
    values = {
        "issuer_hmac": hasher.component_reference(
            label="issuer", value=adapter_config.issuer
        ),
        "tenant_hmac": hasher.component_reference(label="tenant", value=TENANT),
        "object_hmac": hasher.component_reference(
            label="object", value="22222222-3333-4444-5555-666666666666"
        ),
        "subject_hmac": hasher.component_reference(
            label="subject", value="authored-synthetic-subject"
        ),
        "external_hmac": hasher.reference(
            provider=FEDERATION_PROVIDER,
            tenant_id=TENANT,
            object_id="22222222-3333-4444-5555-666666666666",
        ),
        "correlation_hmac": hasher.component_reference(
            label="correlation", value="synthetic-seed-correlation"
        ),
        "binding_ref": "synthetic-binding-admission-one",
        "user_ref": "synthetic-user-admission-one",
        "practice_ref": "synthetic-practice-admission-one",
    }
    with owner.begin() as connection:
        connection.execute(
            text("SELECT pg_catalog.set_config('emr4.practice_ref', :practice, true)"),
            {"practice": values["practice_ref"]},
        )
        connection.execute(
            text(
                "INSERT INTO public.application_identity_federation_bindings ("
                "binding_ref, provider, issuer_reference_hmac, "
                "tenant_reference_hmac, object_reference_hmac, "
                "subject_reference_hmac, user_ref, practice_ref, status, version, "
                "created_at, updated_at, revoked_at, data_class"
                ") VALUES ("
                ":binding_ref, :provider, :issuer_hmac, :tenant_hmac, :object_hmac, "
                ":subject_hmac, :user_ref, :practice_ref, 'active', 1, "
                "clock_timestamp(), clock_timestamp(), NULL, 'authored_synthetic')"
            ),
            {**values, "provider": FEDERATION_PROVIDER},
        )
        connection.execute(
            text(
                "INSERT INTO public.application_identity_federation_audit_events ("
                "operation_ref, correlation_reference_hmac, external_reference_hmac, "
                "binding_ref, user_ref, practice_ref, provider, event_type, decision, "
                "reason_code, policy_version, occurred_at, data_class"
                ") VALUES ("
                "'synthetic-seed-binding-created', :correlation_hmac, "
                ":external_hmac, :binding_ref, :user_ref, :practice_ref, :provider, "
                "'federation.binding_created', 'recorded', 'binding_created', "
                ":policy, clock_timestamp(), 'authored_synthetic')"
            ),
            {**values, "provider": FEDERATION_PROVIDER, "policy": POLICY_VERSION},
        )
    return values


def _sqlstate(operation: Callable[[], None]) -> str | None:
    try:
        operation()
    except DBAPIError as exc:
        return getattr(exc.orig, "sqlstate", None) or getattr(
            exc.orig, "pgcode", None
        )
    return None


def _role_probe(
    runtime_engine: Engine,
    owner: Engine,
    *,
    resolver_call_role: str,
    resolver_owner_role: str,
    grant_issuer_role: str,
    practice_ref: str,
) -> dict[str, Any]:
    def direct_login_binding() -> None:
        with runtime_engine.connect() as connection:
            connection.execute(
                text("SELECT count(*) FROM application_identity_federation_bindings")
            ).scalar_one()

    def resolver_direct_binding() -> None:
        with runtime_engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(f'SET LOCAL ROLE "{resolver_call_role}"'))
                connection.execute(
                    text("SELECT count(*) FROM application_identity_federation_bindings")
                ).scalar_one()
            finally:
                transaction.rollback()

    def issuer_direct_binding() -> None:
        with runtime_engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(f'SET LOCAL ROLE "{grant_issuer_role}"'))
                connection.execute(
                    text("SELECT count(*) FROM application_identity_federation_bindings")
                ).scalar_one()
            finally:
                transaction.rollback()

    def login_enters_owner() -> None:
        with runtime_engine.connect() as connection:
            connection.execute(text(f'SET ROLE "{resolver_owner_role}"'))

    def owner_reads_grant() -> None:
        with owner.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(f'SET LOCAL ROLE "{resolver_owner_role}"'))
                connection.execute(
                    text(
                        "SELECT count(*) FROM "
                        "application_identity_federation_admission_grants"
                    )
                ).scalar_one()
            finally:
                transaction.rollback()

    with runtime_engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(f'SET LOCAL ROLE "{grant_issuer_role}"'))
            connection.execute(
                text("SELECT pg_catalog.set_config('emr4.practice_ref', :p, true)"),
                {"p": practice_ref},
            )
            own_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM "
                        "application_identity_federation_admission_grants"
                    )
                ).scalar_one()
            )
            connection.execute(
                text("SELECT pg_catalog.set_config('emr4.practice_ref', :p, true)"),
                {"p": "synthetic-practice-foreign"},
            )
            foreign_count = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM "
                        "application_identity_federation_admission_grants"
                    )
                ).scalar_one()
            )
        finally:
            transaction.rollback()
    with runtime_engine.connect() as connection:
        reset_identity = tuple(
            connection.execute(text("SELECT session_user, current_user")).one()
        )
    states = {
        "login_binding_select": _sqlstate(direct_login_binding),
        "resolver_call_binding_select": _sqlstate(resolver_direct_binding),
        "grant_issuer_binding_select": _sqlstate(issuer_direct_binding),
        "login_set_resolver_owner": _sqlstate(login_enters_owner),
        "resolver_owner_grant_select": _sqlstate(owner_reads_grant),
    }
    return {
        "denial_sqlstates": states,
        "all_direct_denials_are_insufficient_privilege": set(states.values())
        == {"42501"},
        "issuer_own_practice_grants": own_count,
        "issuer_foreign_practice_grants": foreign_count,
        "pool_returned_to_login": reset_identity[0] == reset_identity[1],
        "role_names_recorded": False,
    }


def _drop_binding_role(maintenance: Engine, role_name: str) -> bool:
    patterns = (_BINDING_LOGIN, _RESOLVER_CALL, _RESOLVER_OWNER, _GRANT_ISSUER)
    if not any(pattern.fullmatch(role_name) for pattern in patterns):
        raise AcceptanceFailure("unsafe_binding_role_cleanup_name")
    with maintenance.begin() as connection:
        present = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
            {"name": role_name},
        ).scalar_one_or_none()
        if present is not None:
            connection.execute(text(drop_binding_admission_role_statement(role_name)))
    return _role_absent(maintenance, role_name)


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_oidc_operational_acceptance_{suffix}"
    attempt_role = f"emr4_oidc_attempt_runtime_{suffix}"
    attempt_login = f"emr4_oidc_attempt_login_{suffix}"
    binding_login = f"emr4_oidc_binding_login_{suffix}"
    resolver_call = f"emr4_oidc_binding_resolver_call_{suffix}"
    resolver_owner = f"emr4_oidc_binding_resolver_owner_{suffix}"
    grant_issuer = f"emr4_oidc_grant_issuer_{suffix}"
    attempt_password = secrets.token_urlsafe(36)
    binding_password = secrets.token_urlsafe(36)
    attempt_references = _references()
    attempt_materials = _materials()
    identity_key = secrets.token_bytes(32)
    grant_key = secrets.token_bytes(32)
    base = _base_database_url()
    target = base.set(database=database_name)
    attempt_target = target.set(username=attempt_login, password=attempt_password)
    binding_target = target.set(username=binding_login, password=binding_password)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    attempt_runtime: PostgresAuthorizationAttemptRuntime | None = None
    binding_engine: Engine | None = None
    server: uvicorn.Server | None = None
    listener: socket.socket | None = None
    server_thread: threading.Thread | None = None
    database_created = False
    created_roles: list[str] = []
    failure_type: str | None = None
    stage = "preflight"
    cleanup_roles = (
        binding_login,
        resolver_call,
        grant_issuer,
        resolver_owner,
    )
    evidence: dict[str, Any] = {
        "schema_version": "emr4.provider-free-oidc-binding-admission-grant-boundary-evidence.v1",
        "result": "revision_required",
        "evidence_label": "live_local_http_backend_postgres",
        "data_class": "authored_synthetic",
        "default_off": True,
        "cleanup": {
            "server_stopped": False,
            "database_absent_after": False,
            "attempt_login_absent_after": False,
            "attempt_capability_absent_after": False,
            "binding_roles_absent_after": False,
            "identifiers_recorded": False,
        },
    }
    try:
        if not all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                CAPABILITY_PATTERN.fullmatch(attempt_role),
                LOGIN_PATTERN.fullmatch(attempt_login),
                _BINDING_LOGIN.fullmatch(binding_login),
                _RESOLVER_CALL.fullmatch(resolver_call),
                _RESOLVER_OWNER.fullmatch(resolver_owner),
                _GRANT_ISSUER.fullmatch(grant_issuer),
            )
        ):
            raise AcceptanceFailure("generated_identifier_invalid")
        _create_database(maintenance, database_name)
        database_created = True
        stage = "migration"
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        # This historical replay intentionally stops at its frozen revision.
        # `alembic check` compares against today's descendant metadata and is
        # therefore no longer a valid assertion once a child migration exists.
        if MIGRATION_HEAD not in current:
            raise AcceptanceFailure("migration_head_mismatch")
        owner = create_engine(target, pool_pre_ping=True)
        stage = "roles"
        with owner.begin() as connection:
            for statement in create_oidc_attempt_runtime_role_statements(attempt_role):
                connection.execute(text(statement))
            created_roles.append(attempt_role)
            for statement in create_oidc_attempt_deployment_login_statements(
                attempt_login,
                attempt_role,
                connection_limit=1,
            ):
                connection.execute(text(statement))
            created_roles.append(attempt_login)
            connection.execute(
                text(f'ALTER ROLE "{attempt_login}" PASSWORD \'{attempt_password}\'')
            )
            for statement in create_binding_admission_capability_statements(
                resolver_call_role=resolver_call,
                resolver_owner_role=resolver_owner,
                grant_issuer_role=grant_issuer,
            ):
                connection.execute(text(statement))
            created_roles.extend((resolver_owner, resolver_call, grant_issuer))
            for statement in create_binding_admission_login_statements(
                binding_login,
                resolver_call_role=resolver_call,
                grant_issuer_role=grant_issuer,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            created_roles.append(binding_login)
            connection.execute(
                text(f'ALTER ROLE "{binding_login}" PASSWORD \'{binding_password}\'')
            )

        stage = "runtime"
        attempt_provider = _SyntheticSecretProvider(
            "syntheticvault",
            {
                attempt_references[key]: value
                for key, value in attempt_materials.items()
            },
        )
        attempt_runtime = build_postgres_authorization_attempt_runtime(
            attempt_target,
            configuration=_operational_configuration(
                login_role=attempt_login,
                capability_role=attempt_role,
                references=attempt_references,
                rotated=False,
            ),
            secret_provider=attempt_provider,
        )
        adapter_config = MicrosoftOIDCAdapterConfig(
            tenant_id=TENANT,
            client_id=CLIENT,
            redirect_uri=CALLBACK,
            surface_origins=ORIGINS,
            enabled=True,
        )
        hasher = FederationReferenceHasher(identity_key)
        seeded = _seed_binding(owner, hasher=hasher, adapter_config=adapter_config)
        binding_engine = create_oidc_binding_admission_engine(
            binding_target,
            login_role=binding_login,
        )
        admission = PostgresOIDCBindingAdmissionService(
            configuration=OIDCBindingAdmissionConfiguration(
                adapter=adapter_config,
                login_role=binding_login,
                resolver_call_role=resolver_call,
                grant_issuer_role=grant_issuer,
                enabled=True,
                max_active_grants=1,
            ),
            session_factory=create_oidc_binding_admission_session_factory(
                binding_engine
            ),
            reference_hasher=hasher,
            grant_digest_key=AdmissionGrantDigestKey(
                key_id="grant-v1",
                key=grant_key,
            ),
        )
        protocol = _Protocol()
        verifier = _Verifier()
        adapter_audit = InMemoryOIDCAdapterAuditSink()
        adapter = TwoComponentOIDCAdapter(
            config=adapter_config,
            protocol_client=protocol,
            verifier=verifier,
            attempt_store=attempt_runtime.store,
            audit_sink=adapter_audit,
        )
        transport = OIDCStartCallbackTransport(
            adapter=adapter,
            surface_origins=ORIGINS,
            idempotency_hmac_key=secrets.token_bytes(32),
            admission_service=admission,
            nonce_source=lambda: "N" * 43,
        )
        denial_sink = _DenialSink()
        stage = "live_http"
        server, listener, server_thread, port = _start_server(
            _application(transport, denial_sink)
        )
        started = _start(port)
        if started[0] != 201:
            raise AcceptanceFailure("start_failed")
        authorization_uri = json.loads(started[2])["authorization_uri"]
        state = parse_qs(urlsplit(authorization_uri).query)["state"][0]
        callback = _callback(
            port,
            urlencode({"code": "authored-code", "state": state}).encode("ascii"),
            "application/x-www-form-urlencoded",
        )
        callback_text = callback[2].decode("utf-8")
        match = _RAW_GRANT.search(callback_text)
        if callback[0] != 200 or match is None:
            raise AcceptanceFailure("grant_bridge_failed")
        raw_grant = match.group(1)
        raw_grant_hmac = AdmissionGrantDigestKey(
            key_id="grant-v1", key=grant_key
        ).reference(raw_grant)

        stage = "database_assertions"
        with owner.connect() as connection:
            grant_row = connection.execute(
                text(
                    "SELECT grant_reference_hmac, binding_ref, binding_version, "
                    "user_ref, practice_ref, provider, surface, origin, return_target, "
                    "extract(epoch FROM (expires_at - issued_at))::integer AS ttl, "
                    "status, version, consumed_at, data_class "
                    "FROM application_identity_federation_admission_grants"
                )
            ).mappings().one()
            audit_types = tuple(
                connection.execute(
                    text(
                        "SELECT event_type FROM "
                        "application_identity_federation_audit_events "
                        "ORDER BY id"
                    )
                ).scalars()
            )
            attempt_rows = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM "
                        "public.application_identity_oidc_authorization_attempts"
                    )
                ).scalar_one()
            )
            session_rows = sum(
                int(
                    connection.execute(query).scalar_one()
                )
                for query in (
                    text("SELECT count(*) FROM public.application_auth_parent_sessions"),
                    text("SELECT count(*) FROM public.application_auth_surface_sessions"),
                    text("SELECT count(*) FROM public.application_auth_exchange_grants"),
                )
            )
            raw_database_matches = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM ("
                        "SELECT grant_reference_hmac AS value FROM "
                        "application_identity_federation_admission_grants "
                        "UNION ALL SELECT external_reference_hmac FROM "
                        "application_identity_federation_admission_grants "
                        "UNION ALL SELECT correlation_reference_hmac FROM "
                        "application_identity_federation_admission_grants "
                        "UNION ALL SELECT external_reference_hmac FROM "
                        "application_identity_federation_audit_events"
                        ") AS residue WHERE position(:raw in value) > 0"
                    ),
                    {"raw": raw_grant},
                ).scalar_one()
            )

        stage = "failure_modes"
        exact_completed = CompletedAuthorization(
            principal=VerifiedMicrosoftPrincipal(
                tenant_id=TENANT,
                object_id="22222222-3333-4444-5555-666666666666",
                subject="authored-synthetic-subject",
            ),
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
            return_target=ReturnTarget.CLINICIAN_ONE,
        )
        capacity_failed_closed = False
        try:
            admission.issue(completed=exact_completed, now=datetime.now(timezone.utc))
        except OIDCTemporarilyUnavailable:
            capacity_failed_closed = True

        missing_completed = CompletedAuthorization(
            principal=VerifiedMicrosoftPrincipal(
                tenant_id=TENANT,
                object_id="22222222-3333-4444-5555-666666666666",
                subject="authored-synthetic-subject-missing",
            ),
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
            return_target=exact_completed.return_target,
        )
        missing_failed_closed = False
        try:
            admission.issue(completed=missing_completed, now=datetime.now(timezone.utc))
        except OIDCAuthenticationFailed:
            missing_failed_closed = True

        with owner.begin() as connection:
            connection.execute(
                text(
                    "REVOKE INSERT ON TABLE "
                    "application_identity_federation_audit_events "
                    f'FROM "{resolver_owner}"'
                )
            )
        audit_failure_closed = False
        try:
            admission.issue(completed=exact_completed, now=datetime.now(timezone.utc))
        except OIDCTemporarilyUnavailable:
            audit_failure_closed = True
        finally:
            with owner.begin() as connection:
                connection.execute(
                    text(
                        "GRANT INSERT ON TABLE "
                        "application_identity_federation_audit_events "
                        f'TO "{resolver_owner}"'
                    )
                )

        with owner.connect() as connection:
            final_grants = int(
                connection.execute(
                    text(
                        "SELECT count(*) FROM "
                        "application_identity_federation_admission_grants"
                    )
                ).scalar_one()
            )
            final_audits = tuple(
                connection.execute(
                    text(
                        "SELECT event_type FROM "
                        "application_identity_federation_audit_events ORDER BY id"
                    )
                ).scalars()
            )

        role_contract = _role_probe(
            binding_engine,
            owner,
            resolver_call_role=resolver_call,
            resolver_owner_role=resolver_owner,
            grant_issuer_role=grant_issuer,
            practice_ref=seeded["practice_ref"],
        )
        grant_contract = {
            "one_grant_row": final_grants == 1,
            "raw_grant_hmac_exact": grant_row["grant_reference_hmac"]
            == raw_grant_hmac,
            "binding_exact": (
                grant_row["binding_ref"] == seeded["binding_ref"]
                and grant_row["binding_version"] == 1
                and grant_row["user_ref"] == seeded["user_ref"]
                and grant_row["practice_ref"] == seeded["practice_ref"]
            ),
            "surface_origin_target_exact": (
                grant_row["surface"] == "word_online"
                and grant_row["origin"] == ORIGINS[Surface.WORD_ONLINE]
                and grant_row["return_target"] == "clinician_one"
            ),
            "ttl_exact_seconds": grant_row["ttl"] == 60,
            "active_version_one": (
                grant_row["status"] == "active"
                and grant_row["version"] == 1
                and grant_row["consumed_at"] is None
            ),
            "authored_synthetic_only": grant_row["data_class"]
            == "authored_synthetic",
            "resolved_and_issued_audited": audit_types[-2:]
            == (
                "federation.binding_resolved",
                "federation.admission_grant_issued",
            ),
            "missing_binding_rejected_audited": final_audits[-1]
            == "federation.binding_rejected",
            "capacity_rolled_back": capacity_failed_closed and final_grants == 1,
            "required_audit_failed_closed": audit_failure_closed,
            "missing_binding_failed_closed": missing_failed_closed,
            "raw_bearer_absent_from_database": raw_database_matches == 0,
        }
        bridge_contract = {
            "status": callback[0],
            "grant_status_exact": '"status":"admission_grant_issued"'
            in callback_text,
            "grant_released_once_in_message": callback_text.count(raw_grant) == 1,
            "no_store": callback[1].get("cache-control") == "no-store",
            "no_referrer": callback[1].get("referrer-policy") == "no-referrer",
            "no_cookie": "set-cookie" not in callback[1],
            "exact_origin": ORIGINS[Surface.WORD_ONLINE] in callback_text,
            "grant_absent_from_authorization_url": raw_grant not in authorization_uri,
        }
        no_authority = {
            "attempt_rows_after_callback": attempt_rows,
            "application_session_rows": session_rows,
            "provider_calls": 0,
            "product_reads": 0,
            "session_cookies": 0,
            "real_identities": 0,
        }
        passed = all(grant_contract.values()) and all(bridge_contract.values()) and all(
            (
                role_contract["all_direct_denials_are_insufficient_privilege"],
                role_contract["issuer_own_practice_grants"] == 1,
                role_contract["issuer_foreign_practice_grants"] == 0,
                role_contract["pool_returned_to_login"],
                attempt_rows == 0,
                session_rows == 0,
                protocol.create_calls == protocol.redeem_calls == verifier.calls == 1,
            )
        )
        evidence.update(
            {
                "result": RESULT if passed else "revision_required",
                "migration_head": MIGRATION_HEAD,
                "accepted_parent_migration_head": PARENT_MIGRATION_HEAD,
                "loopback_http": {
                    "real_socket": True,
                    "host": "127.0.0.1",
                    "ephemeral_port_recorded": False,
                    "requests_performed": 2,
                },
                "bridge_contract": bridge_contract,
                "grant_contract": grant_contract,
                "role_contract": role_contract,
                "no_authority_contract": no_authority,
                "execution_counts": {
                    "protocol_start_calls": protocol.create_calls,
                    "protocol_redeem_calls": protocol.redeem_calls,
                    "verifier_calls": verifier.calls,
                    "adapter_audit_events": len(adapter_audit.events),
                    "denial_audit_events": len(denial_sink.events),
                    "provider_calls": 0,
                    "application_sessions": 0,
                    "product_reads": 0,
                },
                "side_effect_counts": {
                    "disposable_database_migrations": 1,
                    "disposable_database_writes": "performed",
                    "loopback_http_requests": 2,
                    "external_http_or_socket_calls": 0,
                    "provider_calls": 0,
                    "real_identities": 0,
                    "admission_grants": 1,
                    "application_sessions": 0,
                    "product_or_clinical_reads": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "This proves only provider-free authored-synthetic HMAC binding resolution and one 60-second admission grant over real loopback HTTP and disposable PostgreSQL.",
                    "It establishes no live Microsoft call, real identity, application session, cookie, product read, deployment, production or release authority.",
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        sensitive_values = (
            database_name,
            attempt_role,
            attempt_login,
            binding_login,
            resolver_call,
            resolver_owner,
            grant_issuer,
            attempt_password,
            binding_password,
            raw_grant,
            *attempt_references.values(),
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
        if attempt_runtime is not None:
            attempt_runtime.dispose()
        if binding_engine is not None:
            binding_engine.dispose()
        if owner is not None:
            owner.dispose()
        if database_created:
            try:
                evidence["cleanup"]["database_absent_after"] = _drop_database(
                    maintenance, database_name
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["database_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["database_absent_after"] = True
        try:
            evidence["cleanup"]["attempt_login_absent_after"] = (
                _drop_role(maintenance, attempt_login, login=True)
                if attempt_login in created_roles
                else _role_absent(maintenance, attempt_login)
            )
        except Exception as cleanup_exc:
            evidence["cleanup"]["attempt_login_failure_type"] = type(
                cleanup_exc
            ).__name__
        try:
            evidence["cleanup"]["attempt_capability_absent_after"] = (
                _drop_role(maintenance, attempt_role, login=False)
                if attempt_role in created_roles
                else _role_absent(maintenance, attempt_role)
            )
        except Exception as cleanup_exc:
            evidence["cleanup"]["attempt_capability_failure_type"] = type(
                cleanup_exc
            ).__name__
        binding_absence: list[bool] = []
        for role_name in cleanup_roles:
            try:
                binding_absence.append(_drop_binding_role(maintenance, role_name))
            except Exception as cleanup_exc:
                evidence["cleanup"]["binding_role_failure_type"] = type(
                    cleanup_exc
                ).__name__
                binding_absence.append(False)
        evidence["cleanup"]["binding_roles_absent_after"] = all(binding_absence)
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(
        (
            evidence["cleanup"]["server_stopped"],
            evidence["cleanup"]["database_absent_after"],
            evidence["cleanup"]["attempt_login_absent_after"],
            evidence["cleanup"]["attempt_capability_absent_after"],
            evidence["cleanup"]["binding_roles_absent_after"],
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
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
