from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from cryptography.fernet import Fernet
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.application_auth import (
    get_application_auth_operational_hardening,
    get_application_identity_oidc_transport,
    router,
)
from app.services.application_auth_operational_hardening import (
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
)
from app.services.application_auth_transport import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
)
from app.services.application_identity_oidc_adapter import (
    EncryptedAuthorizationAttemptStore,
    InMemoryOIDCAdapterAuditSink,
    MicrosoftOIDCAdapterConfig,
    ReturnTarget,
    Surface,
    TwoComponentOIDCAdapter,
    VerifiedMicrosoftPrincipal,
)
from app.services.application_identity_oidc_transport import (
    MAX_CALLBACK_BODY_BYTES,
    OIDCStartCallbackTransport,
    OIDCTransportRequestDenied,
    OIDCTransportRequestInvalid,
    parse_microsoft_callback_form,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-oidc-start-callback-transport-boundary"
    / "live-local-http-backend-postgres-evidence.json"
)
TENANT = "11111111-2222-3333-4444-555555555555"
CLIENT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
CALLBACK = (
    "https://synthetic.invalid/api/v1/application-auth/"
    "federation/microsoft/callback"
)
ORIGINS = {
    Surface.WORD_DESKTOP: "https://localhost:3000",
    Surface.WORD_ONLINE: "https://word-edit.officeapps.live.com",
    Surface.NATIVE_DIARY: "https://synthetic.invalid",
}
NOW = datetime(2026, 8, 2, 9, 0, tzinfo=timezone.utc)
CSRF = "csrf." + "c" * 43
IDEMPOTENCY = "idem." + "i" * 43
TEST_CLIENT = ("198.51.100.24", 42000)
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


class _Protocol:
    def __init__(self) -> None:
        self.create_calls = 0
        self.redeem_calls = 0
        self.state = ""
        self.nonce = ""
        self.verifier = ""

    def create_authorization_flow(self) -> dict[str, Any]:
        self.create_calls += 1
        marker = str(self.create_calls)
        self.state = "s" * 42 + marker
        self.nonce = "n" * 42 + marker
        self.verifier = "v" * 42 + marker
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
        assert stored_flow["state"] == auth_response["state"]
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
        assert raw_id_token == "signed.authored.synthetic.token"
        assert expected_nonce
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


def _transport() -> tuple[OIDCStartCallbackTransport, _Protocol, _Verifier]:
    protocol = _Protocol()
    verifier = _Verifier()
    config = MicrosoftOIDCAdapterConfig(
        tenant_id=TENANT,
        client_id=CLIENT,
        redirect_uri=CALLBACK,
        surface_origins=ORIGINS,
        enabled=True,
    )
    adapter = TwoComponentOIDCAdapter(
        config=config,
        protocol_client=protocol,
        verifier=verifier,
        attempt_store=EncryptedAuthorizationAttemptStore(
            encryption_key=Fernet.generate_key(),
            digest_key=b"authored-synthetic-transport-digest-key",
        ),
        audit_sink=InMemoryOIDCAdapterAuditSink(),
    )
    return (
        OIDCStartCallbackTransport(
            adapter=adapter,
            surface_origins=ORIGINS,
            idempotency_hmac_key=b"authored-synthetic-idempotency-hmac-key",
            nonce_source=lambda: "N" * 43,
        ),
        protocol,
        verifier,
    )


def _app(
    transport: OIDCStartCallbackTransport,
) -> tuple[FastAPI, _DenialSink]:
    sink = _DenialSink()
    guard = ApplicationAuthOperationalHardening(
        proxy_policy=ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=100,
            max_keys=8,
        ),
        denial_audit_sink=sink,
        client_hmac_key=b"authored-synthetic-client-hmac-key-01",
        clock=lambda: NOW,
    )
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: guard
    application.dependency_overrides[
        get_application_identity_oidc_transport
    ] = lambda: transport
    return application, sink


def _start(client: TestClient, **body_overrides: str):
    body = {"surface": "word_online", "return_target": "clinician_one"}
    body.update(body_overrides)
    return client.post(
        "/api/v1/application-auth/federation/microsoft/start",
        headers={
            "Origin": ORIGINS[Surface.WORD_ONLINE],
            CSRF_HEADER_NAME: CSRF,
            "Idempotency-Key": IDEMPOTENCY,
        },
        cookies={CSRF_COOKIE_NAME: CSRF},
        json=body,
    )


def test_default_routes_fail_closed_without_injected_dependencies() -> None:
    application = FastAPI()
    application.include_router(router)
    with TestClient(
        application,
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        response = _start(client)
    assert response.status_code == 404
    assert response.headers["cache-control"] == "no-store"
    assert "set-cookie" not in response.headers


def test_start_replay_and_callback_bridge_pass_without_authority() -> None:
    transport, protocol, verifier = _transport()
    application, sink = _app(transport)
    with TestClient(
        application,
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        first = _start(client)
        replay = _start(client)
        state = parse_qs(urlsplit(first.json()["authorization_uri"]).query)["state"][0]
        callback = client.post(
            "/api/v1/application-auth/federation/microsoft/callback",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            content=urlencode({"code": "authored-code", "state": state}),
        )
        second_callback = client.post(
            "/api/v1/application-auth/federation/microsoft/callback",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            content=urlencode({"code": "authored-code", "state": state}),
        )

    assert first.status_code == replay.status_code == 201
    assert first.json() == replay.json()
    assert protocol.create_calls == protocol.redeem_calls == verifier.calls == 1
    assert transport.replay_count() == 0
    assert callback.status_code == 200
    assert callback.headers["cache-control"] == "no-store"
    assert callback.headers["referrer-policy"] == "no-referrer"
    assert callback.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'none'" in callback.headers["content-security-policy"]
    assert (
        f"frame-ancestors {ORIGINS[Surface.WORD_ONLINE]}"
        in callback.headers["content-security-policy"]
    )
    assert "set-cookie" not in callback.headers
    assert '"status":"authentication_verified"' in callback.text
    assert json.dumps(ORIGINS[Surface.WORD_ONLINE]) in callback.text
    assert second_callback.status_code == 401
    assert second_callback.json() == {"error": "authentication_failed"}
    assert all(event.action.startswith("auth.oidc.") for event in sink.events)

    serialized = callback.text + repr(callback.headers)
    for forbidden in (
        state,
        protocol.nonce,
        protocol.verifier,
        "authored-code",
        "signed.authored.synthetic.token",
        "22222222-3333-4444-5555-666666666666",
        "authored-synthetic-subject",
        "admission_grant",
        "application-session",
    ):
        assert forbidden not in serialized


def test_origin_csrf_shape_and_idempotency_mismatch_fail_generically() -> None:
    transport, protocol, _ = _transport()
    application, sink = _app(transport)
    with TestClient(
        application,
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        wrong_origin = client.post(
            "/api/v1/application-auth/federation/microsoft/start",
            headers={
                "Origin": "https://foreign.invalid",
                CSRF_HEADER_NAME: CSRF,
                "Idempotency-Key": IDEMPOTENCY,
            },
            cookies={CSRF_COOKIE_NAME: CSRF},
            json={"surface": "word_online", "return_target": "clinician_one"},
        )
        bad_csrf = client.post(
            "/api/v1/application-auth/federation/microsoft/start",
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                CSRF_HEADER_NAME: "csrf." + "x" * 43,
                "Idempotency-Key": IDEMPOTENCY,
            },
            cookies={CSRF_COOKIE_NAME: CSRF},
            json={"surface": "word_online", "return_target": "clinician_one"},
        )
        passed = _start(client)
        mismatched = _start(client, return_target="reception_one")
        invalid_body = _start(client, tenant="forbidden")

    assert wrong_origin.status_code == bad_csrf.status_code == 403
    assert passed.status_code == 201
    assert mismatched.status_code == 403
    assert invalid_body.status_code == 400
    for response in (wrong_origin, bad_csrf, mismatched, invalid_body):
        assert response.json() == {"error": "authentication_failed"}
    assert protocol.create_calls == 1
    assert {event.reason_code for event in sink.events} == {
        "oidc_transport_request_invalid",
        "oidc_transport_request_not_admitted",
    }
    assert "foreign.invalid" not in repr([asdict(event) for event in sink.events])


@pytest.mark.parametrize(
    ("body", "content_type"),
    [
        (b'{"state":"' + b"s" * 43 + b'"}', "application/json"),
        (b"state=" + b"s" * 43 + b"&state=" + b"t" * 43, "application/x-www-form-urlencoded"),
        (b"state=" + b"s" * 43 + b"&unexpected=x", "application/x-www-form-urlencoded"),
        (b"state=%ff", "application/x-www-form-urlencoded"),
        (b"x" * (MAX_CALLBACK_BODY_BYTES + 1), "application/x-www-form-urlencoded"),
    ],
)
def test_callback_parser_rejects_ambiguous_or_oversized_input(
    body: bytes,
    content_type: str,
) -> None:
    with pytest.raises(OIDCTransportRequestInvalid):
        parse_microsoft_callback_form(body, content_type)


def test_callback_route_returns_one_generic_failure_for_bad_forms() -> None:
    transport, protocol, verifier = _transport()
    application, _ = _app(transport)
    with TestClient(
        application,
        base_url=ORIGINS[Surface.WORD_ONLINE],
        client=TEST_CLIENT,
    ) as client:
        responses = [
            client.post(
                "/api/v1/application-auth/federation/microsoft/callback",
                headers={"Content-Type": "application/json"},
                content=b"{}",
            ),
            client.post(
                "/api/v1/application-auth/federation/microsoft/callback",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                content=b"state=" + b"s" * 43 + b"&state=" + b"t" * 43,
            ),
            client.post(
                "/api/v1/application-auth/federation/microsoft/callback",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                content=b"x" * (MAX_CALLBACK_BODY_BYTES + 1),
            ),
        ]
    assert all(response.status_code == 401 for response in responses)
    assert all(
        response.json() == {"error": "authentication_failed"}
        for response in responses
    )
    assert protocol.redeem_calls == verifier.calls == 0


def test_service_rejects_direct_origin_and_csrf_mismatch() -> None:
    transport, _, _ = _transport()
    with pytest.raises(OIDCTransportRequestDenied):
        transport.start(
            surface=Surface.WORD_ONLINE,
            return_target=ReturnTarget.CLINICIAN_ONE,
            origin="https://foreign.invalid",
            csrf_cookie=CSRF,
            csrf_header=CSRF,
            idempotency_key=IDEMPOTENCY,
            now=NOW,
        )


@pytest.mark.parametrize(
    "malicious_origin",
    (
        "https://user:password@synthetic.invalid",
        "https://synthetic.invalid/path",
        "https://synthetic.invalid\r\nx-injected: value",
        "https://SYNTHETIC.invalid",
        "https://synthetic.invalid:70000",
    ),
)
def test_transport_rejects_noncanonical_or_header_unsafe_origins(
    malicious_origin: str,
) -> None:
    transport, _, _ = _transport()
    with pytest.raises(ValueError, match="surface origin is invalid"):
        OIDCStartCallbackTransport(
            adapter=transport._adapter,
            surface_origins={
                **ORIGINS,
                Surface.NATIVE_DIARY: malicious_origin,
            },
            idempotency_hmac_key=b"authored-synthetic-idempotency-hmac-key",
        )


def test_live_local_http_postgres_evidence_passes_with_zero_authority() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["result"] == (
        "provider_free_oidc_start_callback_transport_boundary_pass"
    )
    assert evidence["passed"] is True
    assert evidence["evidence_label"] == "live_local_http_backend_postgres"
    assert evidence["transport_contract"]["idempotent_replay_exact"] is True
    assert evidence["transport_contract"]["fixed_enum_only_bridge"] is True
    assert evidence["persistence_contract"]["one_use_consumption"] is True
    assert evidence["released_sensitive_match_count"] == 0
    assert evidence["evidence_sensitive_match_count"] == 0
    assert evidence["cleanup"]["passed"] is True
    execution = evidence["execution_contract"]
    for field in (
        "provider_calls",
        "real_identities",
        "identity_bindings",
        "admission_grants",
        "application_sessions",
        "product_reads",
    ):
        assert execution[field] == 0


def test_plan_openapi_source_and_receipt_preserve_closed_boundaries() -> None:
    paths = [
        ROOT / "docs/raisa-provider-free-oidc-start-callback-transport-boundary-plan.md",
        ROOT / "docs/raisa-provider-free-oidc-start-callback-transport-boundary-design.md",
        ROOT
        / "docs/security/raisa-provider-free-oidc-start-callback-transport-boundary-threat-model-delta.md",
        ROOT / "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml",
        ROOT / "app/services/application_identity_oidc_transport.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    for required in (
        "exact origin",
        "pre-authentication csrf",
        "form_post",
        "no-store",
        "authentication_failed",
        "no admission grant",
        "no application session",
        "provider-free",
        "product",
        "deployment",
        "production",
    ):
        assert required in combined
    router_source = (ROOT / "app/routers/application_auth.py").read_text(
        encoding="utf-8"
    )
    assert "get_application_identity_oidc_transport" in router_source
    assert "Set-Cookie" not in (
        router_source.split("async def complete_microsoft_federation", 1)[1]
        .split("@router.post", 1)[0]
    )
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/raisa-provider-free-oidc-start-callback-transport-boundary-rehydration-receipt.json"
        ).read_text(encoding="utf-8")
    )
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert set(receipt["source_evidence"]) == FIVE_SOURCES
    assert not any(str(path).startswith("docs/branding/") for path in paths)
