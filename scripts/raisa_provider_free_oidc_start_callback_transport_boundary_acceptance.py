"""Live-local HTTP/PostgreSQL proof for the provider-free OIDC transport."""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import json
import secrets
import socket
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

import uvicorn
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.routers.application_auth import (  # noqa: E402
    get_application_auth_operational_hardening,
    get_application_identity_oidc_transport,
    router,
)
from app.services.application_auth_operational_hardening import (  # noqa: E402
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
)
from app.services.application_auth_transport import (  # noqa: E402
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
)
from app.services.application_identity_oidc_adapter import (  # noqa: E402
    InMemoryOIDCAdapterAuditSink,
    MicrosoftOIDCAdapterConfig,
    Surface,
    TwoComponentOIDCAdapter,
    VerifiedMicrosoftPrincipal,
)
from app.services.application_identity_oidc_attempt_database_role import (  # noqa: E402
    ATTEMPT_TABLE,
    create_oidc_attempt_deployment_login_statements,
    create_oidc_attempt_runtime_role_statements,
)
from app.services.application_identity_oidc_attempt_operational import (  # noqa: E402
    PostgresAuthorizationAttemptRuntime,
    build_postgres_authorization_attempt_runtime,
)
from app.services.application_identity_oidc_transport import (  # noqa: E402
    OIDCStartCallbackTransport,
)
from scripts.raisa_postgresql_oidc_operational_connection_boundary_acceptance import (  # noqa: E402
    CAPABILITY_PATTERN,
    DATABASE_PATTERN,
    LOGIN_PATTERN,
    MIGRATION_HEAD,
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


EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-oidc-start-callback-transport-boundary"
    / "live-local-http-backend-postgres-evidence.json"
)
RESULT = "provider_free_oidc_start_callback_transport_boundary_pass"
TENANT = "11111111-2222-3333-4444-555555555555"
CLIENT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
CALLBACK = (
    "https://oidc-transport.synthetic.invalid/api/v1/application-auth/"
    "federation/microsoft/callback"
)
ORIGINS = {
    Surface.WORD_DESKTOP: "https://localhost:3000",
    Surface.WORD_ONLINE: "https://word-edit.officeapps.live.com",
    Surface.NATIVE_DIARY: "https://oidc-transport.synthetic.invalid",
}
CSRF = "csrf." + "c" * 43
IDEMPOTENCY = "idem." + "i" * 43


class AcceptanceFailure(RuntimeError):
    pass


class _Protocol:
    def __init__(self) -> None:
        self.create_calls = 0
        self.redeem_calls = 0
        self.state = ""
        self.nonce = ""
        self.verifier = ""

    def create_authorization_flow(self) -> dict[str, Any]:
        self.create_calls += 1
        self.state = "s" * 43
        self.nonce = "n" * 43
        self.verifier = "v" * 43
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self.verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        query = urlencode(
            {
                "client_id": CLIENT,
                "response_type": "code",
                "redirect_uri": CALLBACK,
                "scope": "openid profile",
                "state": self.state,
                "nonce": hashlib.sha256(self.nonce.encode("ascii")).hexdigest(),
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "response_mode": "form_post",
                "client_info": "1",
            }
        )
        return {
            "auth_uri": (
                f"https://login.microsoftonline.com/{TENANT}"
                f"/oauth2/v2.0/authorize?{query}"
            ),
            "state": self.state,
            "redirect_uri": CALLBACK,
            "scope": ["openid", "profile"],
            "nonce": self.nonce,
            "code_verifier": self.verifier,
            "claims_challenge": None,
        }

    def redeem_authorization_flow(
        self,
        stored_flow: dict[str, Any],
        auth_response: dict[str, str],
    ) -> dict[str, Any]:
        self.redeem_calls += 1
        if stored_flow["state"] != auth_response["state"]:
            raise AcceptanceFailure("synthetic_state_mismatch")
        return {
            "id_token": "signed.authored.synthetic.token",
            "access_token": "discarded-authored-synthetic-access-token",
        }


class _Verifier:
    def __init__(self) -> None:
        self.calls = 0

    def verify_id_token(
        self,
        raw_id_token: str,
        *,
        expected_nonce: str,
        now: datetime,
    ) -> VerifiedMicrosoftPrincipal:
        self.calls += 1
        if raw_id_token != "signed.authored.synthetic.token" or not expected_nonce:
            raise AcceptanceFailure("synthetic_verifier_input_invalid")
        return VerifiedMicrosoftPrincipal(
            tenant_id=TENANT,
            object_id="22222222-3333-4444-5555-666666666666",
            subject="authored-synthetic-subject",
        )


class _DenialSink:
    def __init__(self) -> None:
        self.events: list[Any] = []

    def record(self, event: Any) -> None:
        self.events.append(event)


def _application(
    transport: OIDCStartCallbackTransport,
    denial_sink: _DenialSink,
) -> FastAPI:
    guard = ApplicationAuthOperationalHardening(
        proxy_policy=ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=100,
            max_keys=8,
        ),
        denial_audit_sink=denial_sink,
        client_hmac_key=b"authored-synthetic-client-hmac-key-01",
        clock=lambda: datetime.now(timezone.utc),
    )
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: guard
    application.dependency_overrides[
        get_application_identity_oidc_transport
    ] = lambda: transport
    return application


def _request(
    port: int,
    method: str,
    path: str,
    *,
    body: bytes,
    headers: dict[str, str],
) -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        return (
            response.status,
            {key.lower(): value for key, value in response.getheaders()},
            response.read(),
        )
    finally:
        connection.close()


def _start(port: int) -> tuple[int, dict[str, str], bytes]:
    return _request(
        port,
        "POST",
        "/api/v1/application-auth/federation/microsoft/start",
        body=json.dumps(
            {"surface": "word_online", "return_target": "clinician_one"}
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Origin": ORIGINS[Surface.WORD_ONLINE],
            CSRF_HEADER_NAME: CSRF,
            "Cookie": f"{CSRF_COOKIE_NAME}={CSRF}",
            "Idempotency-Key": IDEMPOTENCY,
        },
    )


def _callback(port: int, body: bytes, content_type: str) -> tuple[int, dict[str, str], bytes]:
    return _request(
        port,
        "POST",
        "/api/v1/application-auth/federation/microsoft/callback",
        body=body,
        headers={"Content-Type": content_type},
    )


def _start_server(application: FastAPI) -> tuple[uvicorn.Server, socket.socket, threading.Thread, int]:
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
            access_log=False,
        )
    )
    thread = threading.Thread(
        target=server.run,
        kwargs={"sockets": [listener]},
        name="provider-free-oidc-acceptance",
        daemon=True,
    )
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.02)
    if not server.started:
        server.should_exit = True
        thread.join(timeout=5)
        listener.close()
        raise AcceptanceFailure("loopback_server_start_failed")
    return server, listener, thread, port


def _attempt_count(owner: Engine) -> int:
    with owner.connect() as connection:
        return int(
            connection.execute(
                text(f'SELECT count(*) FROM public."{ATTEMPT_TABLE}"')
            ).scalar_one()
        )


def run_acceptance(*, output_path: Path | None = None) -> dict[str, Any]:
    suffix = secrets.token_hex(6)
    database_name = f"emr4_oidc_operational_acceptance_{suffix}"
    capability_role = f"emr4_oidc_attempt_runtime_{suffix}"
    login_role = f"emr4_oidc_attempt_login_{suffix}"
    password = secrets.token_urlsafe(36)
    references = _references()
    materials = _materials()
    base = _base_database_url()
    target = base.set(database=database_name)
    login_target = target.set(username=login_role, password=password)
    maintenance = create_engine(
        base.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
    )
    owner: Engine | None = None
    runtime: PostgresAuthorizationAttemptRuntime | None = None
    server: uvicorn.Server | None = None
    listener: socket.socket | None = None
    server_thread: threading.Thread | None = None
    database_created = False
    capability_created = False
    login_created = False
    failure_type: str | None = None
    evidence: dict[str, Any] = {
        "schema_version": "emr4.provider-free-oidc-start-callback-transport-boundary-evidence.v1",
        "result": "revision_required",
        "evidence_label": "live_local_http_backend_postgres",
        "data_class": "authored_synthetic",
        "default_off": True,
        "cleanup": {
            "server_stopped": False,
            "database_absent_after": False,
            "login_role_absent_after": False,
            "capability_role_absent_after": False,
            "identifiers_recorded": False,
        },
    }
    stage = "preflight"
    try:
        if not all(
            (
                DATABASE_PATTERN.fullmatch(database_name),
                CAPABILITY_PATTERN.fullmatch(capability_role),
                LOGIN_PATTERN.fullmatch(login_role),
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
        stage = "roles"
        with owner.begin() as connection:
            for statement in create_oidc_attempt_runtime_role_statements(capability_role):
                connection.execute(text(statement))
            capability_created = True
            for statement in create_oidc_attempt_deployment_login_statements(
                login_role,
                capability_role,
                connection_limit=1,
            ):
                connection.execute(text(statement))
            login_created = True
            connection.execute(text(f'ALTER ROLE "{login_role}" PASSWORD \'{password}\''))

        provider = _SyntheticSecretProvider(
            "syntheticvault",
            {references[key]: value for key, value in materials.items()},
        )
        runtime = build_postgres_authorization_attempt_runtime(
            login_target,
            configuration=_operational_configuration(
                login_role=login_role,
                capability_role=capability_role,
                references=references,
                rotated=False,
            ),
            secret_provider=provider,
        )
        protocol = _Protocol()
        verifier = _Verifier()
        adapter_audit = InMemoryOIDCAdapterAuditSink()
        adapter = TwoComponentOIDCAdapter(
            config=MicrosoftOIDCAdapterConfig(
                tenant_id=TENANT,
                client_id=CLIENT,
                redirect_uri=CALLBACK,
                surface_origins=ORIGINS,
                enabled=True,
            ),
            protocol_client=protocol,
            verifier=verifier,
            attempt_store=runtime.store,
            audit_sink=adapter_audit,
        )
        transport = OIDCStartCallbackTransport(
            adapter=adapter,
            surface_origins=ORIGINS,
            idempotency_hmac_key=secrets.token_bytes(32),
            nonce_source=lambda: "N" * 43,
        )
        denial_sink = _DenialSink()
        stage = "live_http"
        server, listener, server_thread, port = _start_server(
            _application(transport, denial_sink)
        )
        first = _start(port)
        replay = _start(port)
        if first[0] != 201 or replay != first:
            raise AcceptanceFailure("start_or_idempotent_replay_failed")
        authorization_uri = json.loads(first[2])["authorization_uri"]
        state = parse_qs(urlsplit(authorization_uri).query)["state"][0]
        count_after_start = _attempt_count(owner)
        callback = _callback(
            port,
            urlencode({"code": "authored-code", "state": state}).encode("ascii"),
            "application/x-www-form-urlencoded",
        )
        callback_replay = _callback(
            port,
            urlencode({"code": "authored-code", "state": state}).encode("ascii"),
            "application/x-www-form-urlencoded",
        )
        malformed = _callback(port, b"{}", "application/json")
        count_after_callback = _attempt_count(owner)
        callback_text = callback[2].decode("utf-8")
        callback_replay_json = json.loads(callback_replay[2])
        malformed_json = json.loads(malformed[2])
        transport_contract = {
            "start_status": first[0],
            "idempotent_replay_exact": replay == first,
            "callback_status": callback[0],
            "callback_replay_status": callback_replay[0],
            "malformed_status": malformed[0],
            "generic_failure_exact": callback_replay_json == malformed_json == {
                "error": "authentication_failed"
            },
            "no_store": callback[1].get("cache-control") == "no-store",
            "no_referrer": callback[1].get("referrer-policy") == "no-referrer",
            "nosniff": callback[1].get("x-content-type-options") == "nosniff",
            "restrictive_csp": (
                "default-src 'none'" in callback[1].get("content-security-policy", "")
                and "frame-ancestors https://word-edit.officeapps.live.com"
                in callback[1].get("content-security-policy", "")
            ),
            "no_cookie_issued": "set-cookie" not in callback[1],
            "fixed_enum_only_bridge": all(
                value in callback_text
                for value in (
                    '"status":"authentication_verified"',
                    '"surface":"word_online"',
                    '"return_target":"clinician_one"',
                )
            ),
        }
        prohibited = (
            state,
            protocol.nonce,
            protocol.verifier,
            "authored-code",
            "signed.authored.synthetic.token",
            "22222222-3333-4444-5555-666666666666",
            "authored-synthetic-subject",
            "admission_grant",
            "application-session",
        )
        released_sensitive_count = sum(value in callback_text for value in prohibited)
        persistence_contract = {
            "attempt_rows_after_start": count_after_start,
            "attempt_rows_after_callback": count_after_callback,
            "one_use_consumption": count_after_start == 1 and count_after_callback == 0,
            "runtime_secret_resolutions": len(provider.calls),
            "secret_values_recorded": False,
        }
        execution_contract = {
            "protocol_start_calls": protocol.create_calls,
            "protocol_redeem_calls": protocol.redeem_calls,
            "verifier_calls": verifier.calls,
            "adapter_audit_events": len(adapter_audit.events),
            "denial_audit_events": len(denial_sink.events),
            "provider_calls": 0,
            "real_identities": 0,
            "identity_bindings": 0,
            "admission_grants": 0,
            "application_sessions": 0,
            "product_reads": 0,
        }
        passed = all(transport_contract.values()) and all(
            (
                persistence_contract["one_use_consumption"],
                protocol.create_calls == protocol.redeem_calls == verifier.calls == 1,
                len(adapter_audit.events) == 3,
                len(denial_sink.events) == 2,
                released_sensitive_count == 0,
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
                    "requests_performed": 5,
                },
                "transport_contract": transport_contract,
                "persistence_contract": persistence_contract,
                "execution_contract": execution_contract,
                "released_sensitive_match_count": released_sensitive_count,
                "side_effect_counts": {
                    "disposable_database_migrations": 1,
                    "disposable_database_writes": "performed",
                    "loopback_http_requests": 5,
                    "external_http_or_socket_calls": 0,
                    "provider_calls": 0,
                    "real_identities": 0,
                    "identity_bindings": 0,
                    "admission_grants": 0,
                    "application_sessions": 0,
                    "product_or_clinical_reads": 0,
                    "deployments": 0,
                    "production_changes": 0,
                },
                "claim_limits": [
                    "This proves only a provider-free authored-synthetic start/callback transport over real loopback HTTP and disposable loopback PostgreSQL.",
                    "It establishes no live Microsoft call, real identity, binding, admission grant, application session, product read, deployment, production or release authority.",
                ],
            }
        )
        serialized = json.dumps(evidence, sort_keys=True)
        sensitive_values = (
            database_name,
            login_role,
            capability_role,
            password,
            login_target.render_as_string(False),
            *references.values(),
            *(
                base64.urlsafe_b64encode(value).decode("ascii")
                for value in materials.values()
            ),
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
        if runtime is not None:
            runtime.dispose()
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
        if login_created:
            try:
                evidence["cleanup"]["login_role_absent_after"] = _drop_role(
                    maintenance, login_role, login=True
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["login_failure_type"] = type(cleanup_exc).__name__
        else:
            evidence["cleanup"]["login_role_absent_after"] = _role_absent(
                maintenance, login_role
            )
        if capability_created:
            try:
                evidence["cleanup"]["capability_role_absent_after"] = _drop_role(
                    maintenance, capability_role, login=False
                )
            except Exception as cleanup_exc:
                evidence["cleanup"]["capability_failure_type"] = type(
                    cleanup_exc
                ).__name__
        else:
            evidence["cleanup"]["capability_role_absent_after"] = _role_absent(
                maintenance, capability_role
            )
        maintenance.dispose()

    evidence["cleanup"]["passed"] = all(
        (
            evidence["cleanup"]["server_stopped"],
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
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
