"""Live-local HTTP/PostgreSQL proof for atomic admission-grant redemption."""

from __future__ import annotations

import argparse
import http.client
import json
import re
import secrets
import socket
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.routers.application_auth import (  # noqa: E402
    get_application_auth_operational_hardening,
    get_application_identity_oidc_redemption_transport,
    router,
)
from app.services.application_auth_operational_hardening import (  # noqa: E402
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
)
from app.services.application_auth_role_runtime import (  # noqa: E402
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (  # noqa: E402
    Surface as ApplicationSurface,
)
from app.services.application_auth_transport import (  # noqa: E402
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
)
from app.services.application_identity_federation import (  # noqa: E402
    FederationReferenceHasher,
)
from app.services.application_identity_oidc_adapter import (  # noqa: E402
    CompletedAuthorization,
    MicrosoftOIDCAdapterConfig,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    ReturnTarget,
    Surface,
    VerifiedMicrosoftPrincipal,
)
from app.services.application_identity_oidc_admission_grant import (  # noqa: E402
    AdmissionGrantDigestKey,
    OIDCBindingAdmissionConfiguration,
    PostgresOIDCBindingAdmissionService,
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
from app.services.application_identity_oidc_redemption import (  # noqa: E402
    OIDCAdmissionGrantConflict,
    OIDCAdmissionGrantRedemptionTransport,
    OIDCAdmissionRedemptionConfiguration,
    PostgresOIDCAdmissionGrantRedemptionService,
)
from app.services.application_identity_oidc_redemption_database_role import (  # noqa: E402
    create_redemption_capability_statements,
    create_redemption_login_statements,
    drop_redemption_role_statement,
)
from app.services.application_identity_oidc_redemption_operational import (  # noqa: E402
    create_oidc_admission_redemption_engine,
    create_oidc_admission_redemption_session_factory,
)
from scripts.raisa_postgresql_oidc_operational_connection_boundary_acceptance import (  # noqa: E402
    DATABASE_PATTERN,
    _base_database_url,
    _create_database,
    _drop_database,
    _require_alembic,
    _role_absent,
)
from scripts.raisa_provider_free_oidc_binding_admission_grant_boundary_acceptance import (  # noqa: E402
    _seed_binding,
)
from scripts.raisa_provider_free_oidc_start_callback_transport_boundary_acceptance import (  # noqa: E402
    CALLBACK,
    CLIENT,
    ORIGINS,
    TENANT,
    _DenialSink,
)


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-oidc-admission-grant-redemption-bridge"
    / "live-local-http-backend-postgres-redemption-evidence.json"
)
RESULT = "provider_free_oidc_admission_grant_redemption_bridge_pass"
MIGRATION_HEAD = "t9u0v1w2x3y4"

_BINDING_LOGIN = re.compile(r"^emr4_oidc_binding_login_[0-9a-f]{12}$")
_RESOLVER_CALL = re.compile(r"^emr4_oidc_binding_resolver_call_[0-9a-f]{12}$")
_RESOLVER_OWNER = re.compile(r"^emr4_oidc_binding_resolver_owner_[0-9a-f]{12}$")
_GRANT_ISSUER = re.compile(r"^emr4_oidc_grant_issuer_[0-9a-f]{12}$")
_REDEMPTION_LOGIN = re.compile(r"^emr4_oidc_redemption_login_[0-9a-f]{12}$")
_REDEMPTION_CALL = re.compile(r"^emr4_oidc_redemption_call_[0-9a-f]{12}$")
_REDEMPTION_OWNER = re.compile(r"^emr4_oidc_redemption_owner_[0-9a-f]{12}$")
_COOKIE_VALUE = re.compile(r"^[^=]+=([^;]+)")
CSRF = "csrf." + "c" * 43


class AcceptanceFailure(RuntimeError):
    pass


def _completed() -> CompletedAuthorization:
    return CompletedAuthorization(
        principal=VerifiedMicrosoftPrincipal(
            tenant_id=TENANT,
            object_id="22222222-3333-4444-5555-666666666666",
            subject="authored-synthetic-subject",
        ),
        surface=Surface.WORD_ONLINE,
        origin=ORIGINS[Surface.WORD_ONLINE],
        return_target=ReturnTarget.CLINICIAN_ONE,
    )


def _seed_principal_truth(owner: Engine, seeded: dict[str, str], now: datetime) -> None:
    with owner.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO public.application_auth_synthetic_principal_truth ("
                "practice_ref, user_ref, current_backend_role, practitioner_ref, "
                "user_active, practice_active, membership_active, "
                "practitioner_link_active, truth_version, data_class, updated_at"
                ") VALUES ("
                ":practice, :user, 'GP', :practitioner, true, true, true, true, "
                "1, 'authored_synthetic', :now)"
            ),
            {
                "practice": seeded["practice_ref"],
                "user": seeded["user_ref"],
                "practitioner": "synthetic-practitioner-redemption-one",
                "now": now,
            },
        )


def _application(
    transport: OIDCAdmissionGrantRedemptionTransport,
    denial_sink: _DenialSink,
) -> FastAPI:
    guard = ApplicationAuthOperationalHardening(
        proxy_policy=ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=100,
            max_keys=8,
        ),
        denial_audit_sink=denial_sink,
        client_hmac_key=b"redemption-authored-synthetic-client-key",
        clock=lambda: datetime.now(timezone.utc),
    )
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: guard
    application.dependency_overrides[
        get_application_identity_oidc_redemption_transport
    ] = lambda: transport
    return application


def _start_server(
    application: FastAPI,
) -> tuple[uvicorn.Server, socket.socket, threading.Thread, int]:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    port = int(listener.getsockname()[1])
    server = uvicorn.Server(
        uvicorn.Config(
            application,
            host="127.0.0.1",
            port=port,
            log_level="critical",
            lifespan="off",
        )
    )
    thread = threading.Thread(
        target=server.run,
        kwargs={"sockets": [listener]},
        daemon=True,
    )
    thread.start()
    if not server.started:
        for _ in range(100):
            if server.started:
                break
            threading.Event().wait(0.01)
    if not server.started:
        raise AcceptanceFailure("loopback_server_not_started")
    return server, listener, thread, port


def _redeem_request(
    port: int,
    raw_grant: str,
    *,
    surface: str = "word_online",
    origin: str | None = None,
    csrf: str = CSRF,
) -> tuple[int, list[tuple[str, str]], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        connection.request(
            "POST",
            "/api/v1/application-auth/federation/session/redeem",
            body=json.dumps(
                {"admission_grant": raw_grant, "surface": surface}
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Origin": origin or ORIGINS[Surface.WORD_ONLINE],
                CSRF_HEADER_NAME: csrf,
                "Cookie": f"{CSRF_COOKIE_NAME}={csrf}",
            },
        )
        response = connection.getresponse()
        return response.status, response.getheaders(), response.read()
    finally:
        connection.close()


def _sqlstate(operation: Callable[[], None]) -> str | None:
    try:
        operation()
    except DBAPIError as exc:
        return getattr(exc.orig, "sqlstate", None) or getattr(
            exc.orig, "pgcode", None
        )
    return None


def _role_probe(
    redemption_engine: Engine,
    owner: Engine,
    *,
    redemption_owner: str,
) -> dict[str, Any]:
    def call_reads_grant() -> None:
        with redemption_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT count(*) FROM "
                    "application_identity_federation_admission_grants"
                )
            ).scalar_one()

    def call_reads_binding() -> None:
        with redemption_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT count(*) FROM application_identity_federation_bindings"
                )
            ).scalar_one()

    def call_reads_truth() -> None:
        with redemption_engine.connect() as connection:
            connection.execute(
                text(
                    "SELECT count(*) FROM application_auth_synthetic_principal_truth"
                )
            ).scalar_one()

    def login_reads_session() -> None:
        with redemption_engine.connect() as connection:
            connection.execute(text("RESET ROLE"))
            connection.execute(
                text("SELECT count(*) FROM application_auth_parent_sessions")
            ).scalar_one()

    def login_enters_owner() -> None:
        with redemption_engine.connect() as connection:
            connection.execute(text("RESET ROLE"))
            connection.execute(text(f'SET ROLE "{redemption_owner}"'))

    def owner_reads_session() -> None:
        with owner.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(f'SET LOCAL ROLE "{redemption_owner}"'))
                connection.execute(
                    text("SELECT count(*) FROM application_auth_parent_sessions")
                ).scalar_one()
            finally:
                transaction.rollback()

    states = {
        "call_grant_select": _sqlstate(call_reads_grant),
        "call_binding_select": _sqlstate(call_reads_binding),
        "call_truth_select": _sqlstate(call_reads_truth),
        "login_session_select": _sqlstate(login_reads_session),
        "login_set_owner": _sqlstate(login_enters_owner),
        "owner_session_select": _sqlstate(owner_reads_session),
    }
    with redemption_engine.connect() as connection:
        identity = tuple(
            connection.execute(text("SELECT session_user, current_user")).one()
        )
    return {
        "denial_sqlstates": states,
        "all_direct_denials_are_insufficient_privilege": set(states.values())
        == {"42501"},
        "login_and_call_are_distinct": identity[0] != identity[1],
        "role_names_recorded": False,
    }


def _drop_task_role(
    maintenance: Engine,
    role_name: str,
    *,
    redemption: bool,
) -> bool:
    patterns = (
        (_REDEMPTION_LOGIN, _REDEMPTION_CALL, _REDEMPTION_OWNER)
        if redemption
        else (_BINDING_LOGIN, _RESOLVER_CALL, _RESOLVER_OWNER, _GRANT_ISSUER)
    )
    if not any(pattern.fullmatch(role_name) for pattern in patterns):
        raise AcceptanceFailure("unsafe_role_cleanup_name")
    with maintenance.begin() as connection:
        if connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
            {"name": role_name},
        ).scalar_one_or_none() is not None:
            statement = (
                drop_redemption_role_statement(role_name)
                if redemption
                else drop_binding_admission_role_statement(role_name)
            )
            connection.execute(text(statement))
    return _role_absent(maintenance, role_name)


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_oidc_operational_acceptance_{suffix}"
    binding_login = f"emr4_oidc_binding_login_{suffix}"
    resolver_call = f"emr4_oidc_binding_resolver_call_{suffix}"
    resolver_owner = f"emr4_oidc_binding_resolver_owner_{suffix}"
    grant_issuer = f"emr4_oidc_grant_issuer_{suffix}"
    redemption_login = f"emr4_oidc_redemption_login_{suffix}"
    redemption_call = f"emr4_oidc_redemption_call_{suffix}"
    redemption_owner = f"emr4_oidc_redemption_owner_{suffix}"
    binding_password = secrets.token_urlsafe(36)
    redemption_password = secrets.token_urlsafe(36)
    identity_key = secrets.token_bytes(32)
    grant_key = secrets.token_bytes(32)
    now = datetime.now(timezone.utc)

    base = _base_database_url()
    target = base.set(database=database_name)
    binding_target = target.set(username=binding_login, password=binding_password)
    redemption_target = target.set(
        username=redemption_login,
        password=redemption_password,
    )
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    binding_engine: Engine | None = None
    redemption_engine: Engine | None = None
    server: uvicorn.Server | None = None
    listener: socket.socket | None = None
    server_thread: threading.Thread | None = None
    database_created = False
    created_roles: list[str] = []
    raw_values: list[str] = []
    failure_type: str | None = None
    stage = "preflight"
    cleanup_roles = (
        (binding_login, False),
        (resolver_call, False),
        (grant_issuer, False),
        (resolver_owner, False),
        (redemption_login, True),
        (redemption_call, True),
        (redemption_owner, True),
    )
    evidence: dict[str, Any] = {
        "schema_version": (
            "emr4.provider-free-oidc-admission-grant-redemption-bridge-evidence.v1"
        ),
        "result": "revision_required",
        "evidence_label": "live_local_http_backend_postgres_redemption",
        "data_class": "authored_synthetic",
        "default_off": True,
        "cleanup": {
            "server_stopped": False,
            "database_absent_after": False,
            "task_roles_absent_after": False,
            "identifiers_recorded": False,
        },
    }
    try:
        if not all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                _BINDING_LOGIN.fullmatch(binding_login),
                _RESOLVER_CALL.fullmatch(resolver_call),
                _RESOLVER_OWNER.fullmatch(resolver_owner),
                _GRANT_ISSUER.fullmatch(grant_issuer),
                _REDEMPTION_LOGIN.fullmatch(redemption_login),
                _REDEMPTION_CALL.fullmatch(redemption_call),
                _REDEMPTION_OWNER.fullmatch(redemption_owner),
            )
        ):
            raise AcceptanceFailure("generated_identifier_invalid")
        _create_database(maintenance, database_name)
        database_created = True
        stage = "migration"
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        _require_alembic(target, "downgrade", "s8t9u0v1w2x3")
        _require_alembic(target, "upgrade", MIGRATION_HEAD)
        current = _require_alembic(target, "current")
        _require_alembic(target, "check")
        if MIGRATION_HEAD not in current:
            raise AcceptanceFailure("migration_head_mismatch")

        owner = create_engine(target, pool_pre_ping=True)
        stage = "roles"
        with owner.begin() as connection:
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
            for statement in create_redemption_capability_statements(
                call_role=redemption_call,
                owner_role=redemption_owner,
            ):
                connection.execute(text(statement))
            created_roles.extend((redemption_owner, redemption_call))
            for statement in create_redemption_login_statements(
                redemption_login,
                call_role=redemption_call,
                connection_limit=2,
            ):
                connection.execute(text(statement))
            created_roles.append(redemption_login)
            connection.execute(
                text(
                    f'ALTER ROLE "{redemption_login}" PASSWORD '
                    f"'{redemption_password}'"
                )
            )

        stage = "runtime"
        adapter_config = MicrosoftOIDCAdapterConfig(
            tenant_id=TENANT,
            client_id=CLIENT,
            redirect_uri=CALLBACK,
            surface_origins=ORIGINS,
            enabled=True,
        )
        hasher = FederationReferenceHasher(identity_key)
        digest = AdmissionGrantDigestKey(key_id="grant-v1", key=grant_key)
        seeded = _seed_binding(owner, hasher=hasher, adapter_config=adapter_config)
        _seed_principal_truth(owner, seeded, now)
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
                max_active_grants=8,
            ),
            session_factory=create_oidc_binding_admission_session_factory(
                binding_engine
            ),
            reference_hasher=hasher,
            grant_digest_key=digest,
        )
        redemption_engine = create_oidc_admission_redemption_engine(
            redemption_target,
            login_role=redemption_login,
            call_role=redemption_call,
        )
        redemption_factory = create_oidc_admission_redemption_session_factory(
            redemption_engine
        )
        app_runtime = RoleScopedPostgresApplicationAuthRuntime(
            session_factory=redemption_factory,
            surface_origins={
                ApplicationSurface(surface.value): origin
                for surface, origin in ORIGINS.items()
            },
            clock=lambda: now,
        )
        service = PostgresOIDCAdmissionGrantRedemptionService(
            configuration=OIDCAdmissionRedemptionConfiguration(
                adapter=adapter_config,
                login_role=redemption_login,
                call_role=redemption_call,
                enabled=True,
            ),
            session_factory=redemption_factory,
            reference_hasher=hasher,
            grant_digest_key=digest,
            application_auth_runtime=app_runtime,
            clock=lambda: now,
        )
        transport = OIDCAdmissionGrantRedemptionTransport(
            service=service,
            surface_origins=ORIGINS,
            csrf_token_source=lambda: "csrf." + "r" * 43,
        )

        first_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(first_grant.raw_grant)
        denial_sink = _DenialSink()
        stage = "live_http"
        server, listener, server_thread, port = _start_server(
            _application(transport, denial_sink)
        )
        first = _redeem_request(port, first_grant.raw_grant)
        replay = _redeem_request(port, first_grant.raw_grant)
        unknown = _redeem_request(port, "U" * 43)
        wrong_origin = _redeem_request(
            port,
            "W" * 43,
            origin="https://foreign.synthetic.invalid",
        )
        first_json = json.loads(first[2])
        replay_json = json.loads(replay[2])
        unknown_json = json.loads(unknown[2])
        set_cookies = [
            value for key, value in first[1] if key.lower() == "set-cookie"
        ]
        if first[0] != 200 or len(set_cookies) != 2:
            raise AcceptanceFailure("live_http_redemption_failed")
        for cookie in set_cookies:
            match = _COOKIE_VALUE.match(cookie)
            if match is not None:
                raw_values.append(match.group(1))
        raw_values.append(first_json["csrf_token"])

        stage = "concurrency"
        concurrent_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(concurrent_grant.raw_grant)
        barrier = threading.Barrier(2)
        outcomes: list[str] = []
        outcome_lock = threading.Lock()

        def redeem_concurrently() -> None:
            barrier.wait(timeout=5)
            try:
                result = service.redeem(
                    raw_grant=concurrent_grant.raw_grant,
                    surface=Surface.WORD_ONLINE,
                    origin=ORIGINS[Surface.WORD_ONLINE],
                )
                raw_values.append(result.surface_session_value)
                outcome = "admitted"
            except OIDCAdmissionGrantConflict:
                outcome = "already_consumed"
            with outcome_lock:
                outcomes.append(outcome)

        threads = [threading.Thread(target=redeem_concurrently) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        concurrency_exact = sorted(outcomes) == ["admitted", "already_consumed"]

        stage = "failure_modes"
        stage = "failure_surface_mismatch"
        surface_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(surface_grant.raw_grant)
        surface_rejected = False
        try:
            service.redeem(
                raw_grant=surface_grant.raw_grant,
                surface=Surface.WORD_DESKTOP,
                origin=ORIGINS[Surface.WORD_DESKTOP],
            )
        except OIDCAuthenticationFailed:
            surface_rejected = True

        stage = "failure_inactive_principal"
        inactive_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(inactive_grant.raw_grant)
        with owner.begin() as connection:
            connection.execute(
                text(
                    "UPDATE application_auth_synthetic_principal_truth "
                    "SET membership_active = false, truth_version = 2, "
                    "updated_at = :now WHERE practice_ref = :practice "
                    "AND user_ref = :user"
                ),
                {"now": now, "practice": seeded["practice_ref"], "user": seeded["user_ref"]},
            )
        inactive_rejected = False
        try:
            service.redeem(
                raw_grant=inactive_grant.raw_grant,
                surface=Surface.WORD_ONLINE,
                origin=ORIGINS[Surface.WORD_ONLINE],
            )
        except OIDCAuthenticationFailed:
            inactive_rejected = True
        with owner.begin() as connection:
            connection.execute(
                text(
                    "UPDATE application_auth_synthetic_principal_truth "
                    "SET membership_active = true, truth_version = 3, "
                    "updated_at = :now WHERE practice_ref = :practice "
                    "AND user_ref = :user"
                ),
                {"now": now, "practice": seeded["practice_ref"], "user": seeded["user_ref"]},
            )

        stage = "failure_federation_audit"
        federation_audit_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(federation_audit_grant.raw_grant)
        with owner.begin() as connection:
            connection.execute(
                text(
                    "REVOKE INSERT ON TABLE "
                    "application_identity_federation_audit_events "
                    f'FROM "{redemption_owner}"'
                )
            )
        federation_audit_failed_closed = False
        try:
            service.redeem(
                raw_grant=federation_audit_grant.raw_grant,
                surface=Surface.WORD_ONLINE,
                origin=ORIGINS[Surface.WORD_ONLINE],
            )
        except OIDCTemporarilyUnavailable:
            federation_audit_failed_closed = True
        finally:
            with owner.begin() as connection:
                connection.execute(
                    text(
                        "GRANT INSERT ON TABLE "
                        "application_identity_federation_audit_events "
                        f'TO "{redemption_owner}"'
                    )
                )

        stage = "failure_application_audit"
        app_audit_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(app_audit_grant.raw_grant)
        with owner.begin() as connection:
            connection.execute(
                text(
                    "REVOKE INSERT ON TABLE application_auth_audit_events "
                    f'FROM "{redemption_call}"'
                )
            )
        app_audit_failed_closed = False
        try:
            service.redeem(
                raw_grant=app_audit_grant.raw_grant,
                surface=Surface.WORD_ONLINE,
                origin=ORIGINS[Surface.WORD_ONLINE],
            )
        except OIDCTemporarilyUnavailable:
            app_audit_failed_closed = True
        finally:
            with owner.begin() as connection:
                connection.execute(
                    text(
                        "GRANT INSERT ON TABLE application_auth_audit_events "
                        f'TO "{redemption_call}"'
                    )
                )

        stage = "failure_binding_revocation"
        binding_grant = admission.issue(completed=_completed(), now=now)
        raw_values.append(binding_grant.raw_grant)
        with owner.begin() as connection:
            connection.execute(
                text("SELECT pg_catalog.set_config('emr4.practice_ref', :p, true)"),
                {"p": seeded["practice_ref"]},
            )
            connection.execute(
                text(
                    "UPDATE application_identity_federation_bindings "
                    "SET status = 'revoked', version = 2, "
                    "updated_at = clock_timestamp(), "
                    "revoked_at = clock_timestamp() WHERE binding_ref = :binding"
                ),
                {"binding": seeded["binding_ref"]},
            )
        binding_rejected = False
        try:
            service.redeem(
                raw_grant=binding_grant.raw_grant,
                surface=Surface.WORD_ONLINE,
                origin=ORIGINS[Surface.WORD_ONLINE],
            )
        except OIDCAuthenticationFailed:
            binding_rejected = True

        stage = "database_assertions"
        with owner.connect() as connection:
            grant_states = tuple(
                tuple(row)
                for row in connection.execute(
                    text(
                        "SELECT status, version, consumed_at IS NOT NULL "
                        "FROM application_identity_federation_admission_grants "
                        "ORDER BY operation_ref"
                    )
                )
            )
            parent_count = int(
                connection.execute(
                    text("SELECT count(*) FROM application_auth_parent_sessions")
                ).scalar_one()
            )
            surface_count = int(
                connection.execute(
                    text("SELECT count(*) FROM application_auth_surface_sessions")
                ).scalar_one()
            )
            federation_events = tuple(
                connection.execute(
                    text(
                        "SELECT event_type FROM "
                        "application_identity_federation_audit_events ORDER BY id"
                    )
                ).scalars()
            )
            auth_events = tuple(
                connection.execute(
                    text(
                        "SELECT event_type FROM application_auth_audit_events "
                        "ORDER BY id"
                    )
                ).scalars()
            )
            residue = "".join(
                str(value)
                for table in (
                    "application_identity_federation_admission_grants",
                    "application_identity_federation_audit_events",
                    "application_auth_synthetic_principal_truth",
                    "application_auth_principal_generations",
                    "application_auth_parent_sessions",
                    "application_auth_surface_sessions",
                    "application_auth_audit_events",
                )
                for value in connection.execute(
                    text(f"SELECT row_to_json(t)::text FROM {table} AS t")
                ).scalars()
            )

        role_contract = _role_probe(
            redemption_engine,
            owner,
            redemption_owner=redemption_owner,
        )
        cookie_contract = {
            "two_cookies": len(set_cookies) == 2,
            "session_cookie_present": any(
                cookie.startswith(f"{SESSION_COOKIE_NAME}=") for cookie in set_cookies
            ),
            "csrf_cookie_present": any(
                cookie.startswith(f"{CSRF_COOKIE_NAME}=") for cookie in set_cookies
            ),
            "secure_http_only_partitioned": all(
                all(
                    marker in cookie
                    for marker in (
                        "Path=/",
                        "HttpOnly",
                        "SameSite=none",
                        "Secure",
                        "Partitioned",
                    )
                )
                and "Domain=" not in cookie
                for cookie in set_cookies
            ),
            "no_store": any(
                key.lower() == "cache-control" and value == "no-store"
                for key, value in first[1]
            ),
            "csrf_returned_once": first[2].decode("utf-8").count(first_json["csrf_token"])
            == 1,
        }
        atomic_contract = {
            "first_http_authenticated": first_json["status"] == "authenticated",
            "replay_conflict_generic": replay[0] == 409
            and replay_json == {"error": "authentication_failed"},
            "unknown_generic": unknown[0] == 401
            and unknown_json == {"error": "authentication_failed"},
            "wrong_origin_denied": wrong_origin[0] == 403,
            "no_failure_cookie": all(
                key.lower() != "set-cookie"
                for response in (replay, unknown, wrong_origin)
                for key, _ in response[1]
            ),
            "concurrency_exactly_one": concurrency_exact,
            "surface_mismatch_rejected": surface_rejected,
            "inactive_principal_rejected": inactive_rejected,
            "revoked_binding_rejected": binding_rejected,
            "federation_audit_failure_rolled_back": federation_audit_failed_closed,
            "application_audit_failure_rolled_back": app_audit_failed_closed,
            "two_committed_sessions_only": parent_count == surface_count == 2,
            "consumed_audit_exact": federation_events.count(
                "federation.admission_grant_consumed"
            )
            == 2,
            "session_audit_exact": auth_events.count("auth.session_created")
            == auth_events.count("auth.surface_bound")
            == 2,
            "failed_grants_unconsumed": sum(
                state == ("active", 1, False) for state in grant_states
            )
            >= 5,
        }
        residue_contract = {
            "raw_values_absent_from_database": all(
                value not in residue for value in raw_values
            ),
            "raw_grant_absent_from_evidence": True,
            "provider_calls": 0,
            "product_reads": 0,
            "real_identities": 0,
        }
        passed = all(cookie_contract.values()) and all(atomic_contract.values()) and all(
            (
                role_contract["all_direct_denials_are_insufficient_privilege"],
                role_contract["login_and_call_are_distinct"],
                residue_contract["raw_values_absent_from_database"],
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
                    "requests_performed": 4,
                },
                "cookie_contract": cookie_contract,
                "atomic_redemption_contract": atomic_contract,
                "role_contract": role_contract,
                "residue_contract": residue_contract,
                "side_effect_counts": {
                    "provider_calls": 0,
                    "real_identities": 0,
                    "product_or_clinical_reads": 0,
                    "committed_admission_redemptions": 2,
                    "committed_parent_sessions": parent_count,
                    "committed_surface_sessions": surface_count,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "This proves only provider-free authored-synthetic atomic grant redemption into the accepted application-session runtime over real loopback HTTP and disposable PostgreSQL.",
                    "It establishes no live Microsoft call, real identity or product truth, product authorization, deployment, production or release authority.",
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        sensitive_values = (
            database_name,
            binding_login,
            resolver_call,
            resolver_owner,
            grant_issuer,
            redemption_login,
            redemption_call,
            redemption_owner,
            binding_password,
            redemption_password,
            *raw_values,
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
        if binding_engine is not None:
            binding_engine.dispose()
        if redemption_engine is not None:
            redemption_engine.dispose()
        if owner is not None:
            owner.dispose()
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
        for role_name, redemption in cleanup_roles:
            try:
                role_absence.append(
                    _drop_task_role(
                        maintenance,
                        role_name,
                        redemption=redemption,
                    )
                    if role_name in created_roles
                    else _role_absent(maintenance, role_name)
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["role_failure_type"] = type(
                    cleanup_exc
                ).__name__
                role_absence.append(False)
        evidence["cleanup"]["task_roles_absent_after"] = all(role_absence)
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(
        (
            evidence["cleanup"]["server_stopped"],
            evidence["cleanup"]["database_absent_after"],
            evidence["cleanup"]["task_roles_absent_after"],
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
