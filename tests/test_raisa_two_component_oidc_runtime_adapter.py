from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
from dataclasses import fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

import jwt as pyjwt
import pytest
from authlib.integrations.base_client.sync_openid import OpenIDMixin
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa

from app.services.application_identity_oidc_adapter import (
    AuthlibIDTokenVerifier,
    AuthlibOpenIDClient,
    CompletedAuthorization,
    EncryptedAuthorizationAttemptStore,
    InMemoryOIDCAdapterAuditSink,
    MSALAuthorizationCodeClient,
    MicrosoftOIDCAdapterConfig,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    ReturnTarget,
    Surface,
    TwoComponentOIDCAdapter,
    VerifiedMicrosoftPrincipal,
)
from scripts.raisa_two_component_oidc_runtime_adapter_acceptance import (
    CASES_PATH,
    DEFAULT_OUTPUT,
    run_acceptance,
)


TENANT_ID = "11111111-2222-3333-4444-555555555555"
CLIENT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
REDIRECT_URI = (
    "https://synthetic.invalid/api/v1/application-auth/"
    "federation/microsoft/callback"
)
NOW = datetime(2026, 8, 2, 4, 0, tzinfo=timezone.utc)
STATE = "s" * 43
NONCE = "n" * 43
CODE_VERIFIER = "v" * 43
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
ROOT = Path(__file__).resolve().parents[1]


class _ClaimsShortcutProtocol:
    def __init__(self) -> None:
        self.redeem_calls = 0

    def create_authorization_flow(self) -> dict[str, str]:
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(CODE_VERIFIER.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        query = urlencode(
            {
                "client_id": CLIENT_ID,
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "scope": "openid profile",
                "state": STATE,
                "nonce": hashlib.sha256(NONCE.encode("ascii")).hexdigest(),
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "response_mode": "form_post",
                "client_info": "1",
            }
        )
        return {
            "auth_uri": (
                f"https://login.microsoftonline.com/{TENANT_ID}"
                f"/oauth2/v2.0/authorize?{query}"
            ),
            "state": STATE,
            "redirect_uri": REDIRECT_URI,
            "scope": ["openid", "profile"],
            "nonce": NONCE,
            "code_verifier": CODE_VERIFIER,
            "claims_challenge": None,
        }

    def redeem_authorization_flow(
        self,
        stored_flow: dict[str, str],
        auth_response: dict[str, str],
    ) -> dict[str, object]:
        self.redeem_calls += 1
        assert stored_flow["state"] == STATE
        assert auth_response == {"code": "authored-synthetic-code", "state": STATE}
        return {
            "id_token": "forged.raw.id-token",
            "id_token_claims": {
                "tid": TENANT_ID,
                "oid": "claims-shortcut-object",
                "sub": "claims-shortcut-subject",
            },
            "access_token": "must-be-discarded",
            "refresh_token": "must-also-be-discarded",
        }


class _RejectingVerifier:
    def __init__(self) -> None:
        self.seen: list[tuple[str, str]] = []

    def verify_id_token(
        self,
        raw_id_token: str,
        *,
        expected_nonce: str,
        now: datetime,
    ) -> None:
        self.seen.append((raw_id_token, expected_nonce))
        raise OIDCAuthenticationFailed("token_signature_invalid")


class _AcceptingVerifier:
    def __init__(self) -> None:
        self.seen: list[tuple[str, str]] = []

    def verify_id_token(
        self,
        raw_id_token: str,
        *,
        expected_nonce: str,
        now: datetime,
    ) -> VerifiedMicrosoftPrincipal:
        self.seen.append((raw_id_token, expected_nonce))
        return VerifiedMicrosoftPrincipal(
            tenant_id=TENANT_ID,
            object_id="authored-synthetic-object",
            subject="authored-synthetic-subject",
        )


class _SuccessProtocol(_ClaimsShortcutProtocol):
    def __init__(self, *, fail_redeem: bool = False) -> None:
        super().__init__()
        self.fail_redeem = fail_redeem

    def redeem_authorization_flow(
        self,
        stored_flow: dict[str, str],
        auth_response: dict[str, str],
    ) -> dict[str, object]:
        self.redeem_calls += 1
        if self.fail_redeem:
            raise RuntimeError("raw provider diagnostic must be normalized")
        return {
            "id_token": "signed.synthetic.id-token",
            "id_token_claims": {"admin": True},
            "access_token": "discarded-access-token",
            "refresh_token": "discarded-refresh-token",
        }


class _CountingDisabledProtocol:
    def __init__(self) -> None:
        self.create_calls = 0
        self.redeem_calls = 0

    def create_authorization_flow(self) -> dict[str, str]:
        self.create_calls += 1
        raise AssertionError("disabled adapter called MSAL")

    def redeem_authorization_flow(self, *_: Any) -> dict[str, str]:
        self.redeem_calls += 1
        raise AssertionError("disabled adapter redeemed a code")


class _Response:
    status_code = 200
    headers: dict[str, str] = {}

    def __init__(self, value: dict[str, Any]) -> None:
        self._value = value
        self.text = json.dumps(value)

    def json(self) -> dict[str, Any]:
        return self._value

    def raise_for_status(self) -> None:
        return None


class _MsalHttp:
    def __init__(self, post_response: dict[str, Any] | None = None) -> None:
        self.get_count = 0
        self.post_count = 0
        self.post_response = post_response

    def get(self, url: str, **_: Any) -> _Response:
        self.get_count += 1
        assert url.startswith(AUTHORITY)
        return _Response(
            {
                "authorization_endpoint": f"{AUTHORITY}/oauth2/v2.0/authorize",
                "token_endpoint": f"{AUTHORITY}/oauth2/v2.0/token",
                "issuer": ISSUER,
                "jwks_uri": JWKS_URI,
            }
        )

    def post(self, *_: Any, **__: Any) -> _Response:
        self.post_count += 1
        if self.post_response is None:
            raise AssertionError("provider token exchange is forbidden")
        return _Response(self.post_response)


class _JwksSession:
    def __init__(self, refreshed_jwks: dict[str, Any] | None) -> None:
        self.refreshed_jwks = refreshed_jwks
        self.requests = 0

    def __enter__(self) -> "_JwksSession":
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        assert method == "GET"
        assert url == JWKS_URI
        assert kwargs.get("withhold_token") is True
        self.requests += 1
        if self.refreshed_jwks is None:
            raise RuntimeError("raw refresh diagnostic")
        return _Response(self.refreshed_jwks)


class _OfflineOpenIDClient(OpenIDMixin):
    def __init__(
        self,
        initial_jwks: dict[str, Any],
        refreshed_jwks: dict[str, Any] | None = None,
        *,
        metadata_overrides: dict[str, Any] | None = None,
    ) -> None:
        self.client_id = CLIENT_ID
        self.server_metadata = {
            "issuer": ISSUER,
            "authorization_endpoint": f"{AUTHORITY}/oauth2/v2.0/authorize",
            "token_endpoint": f"{AUTHORITY}/oauth2/v2.0/token",
            "jwks_uri": JWKS_URI,
            "jwks": initial_jwks,
            "id_token_signing_alg_values_supported": ["RS256"],
        }
        self.server_metadata.update(metadata_overrides or {})
        self.session = _JwksSession(refreshed_jwks)

    def load_server_metadata(self) -> dict[str, Any]:
        return self.server_metadata

    def _get_session(self) -> _JwksSession:
        return self.session


class _PinnedMetadataSession:
    def __init__(self, jwks: dict[str, Any]) -> None:
        self.jwks = jwks
        self.urls: list[str] = []

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        assert method == "GET"
        assert kwargs["allow_redirects"] is False
        assert kwargs["stream"] is True
        self.urls.append(url)
        if url == _config().discovery_url:
            return _Response(
                {
                    "issuer": ISSUER,
                    "authorization_endpoint": f"{AUTHORITY}/oauth2/v2.0/authorize",
                    "token_endpoint": f"{AUTHORITY}/oauth2/v2.0/token",
                    "jwks_uri": JWKS_URI,
                    "id_token_signing_alg_values_supported": ["RS256"],
                }
            )
        if url == JWKS_URI:
            return _Response(self.jwks)
        raise AssertionError("unpinned URL")

    def close(self) -> None:
        return None


def _b64uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _public_jwk(private_key: rsa.RSAPrivateKey, kid: str) -> dict[str, str]:
    numbers = private_key.public_key().public_numbers()
    return {
        "kty": "RSA",
        "use": "sig",
        "kid": kid,
        "n": _b64uint(numbers.n),
        "e": _b64uint(numbers.e),
    }


def _signed_token(
    private_key: rsa.RSAPrivateKey,
    kid: str,
    *,
    omit: tuple[str, ...] = (),
    **overrides: Any,
) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "sub": "authored-synthetic-subject",
        "tid": TENANT_ID,
        "oid": "authored-synthetic-object",
        "nonce": NONCE,
        "iat": now,
        "nbf": now - 1,
        "exp": now + 300,
    }
    claims.update(overrides)
    for key in omit:
        claims.pop(key, None)
    return pyjwt.encode(
        claims,
        private_key,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT"},
    )


def _tamper_signature(token: str) -> str:
    header, payload, signature = token.split(".")
    padded = signature + "=" * (-len(signature) % 4)
    raw = bytearray(base64.urlsafe_b64decode(padded))
    raw[0] ^= 1
    changed = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return f"{header}.{payload}.{changed}"


def _config() -> MicrosoftOIDCAdapterConfig:
    return MicrosoftOIDCAdapterConfig(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        surface_origins={
            Surface.WORD_ONLINE: "https://word-edit.officeapps.live.com",
            Surface.WORD_DESKTOP: "https://localhost:3000",
            Surface.NATIVE_DIARY: "https://synthetic.invalid",
        },
        enabled=True,
    )


def _store(*, max_attempts: int = 128) -> EncryptedAuthorizationAttemptStore:
    return EncryptedAuthorizationAttemptStore(
        encryption_key=Fernet.generate_key(),
        digest_key=b"authored-synthetic-digest-key-01",
        max_attempts=max_attempts,
    )


def _adapter(
    protocol: Any,
    verifier: Any,
    *,
    store: EncryptedAuthorizationAttemptStore | None = None,
    audit: InMemoryOIDCAdapterAuditSink | None = None,
    config: MicrosoftOIDCAdapterConfig | None = None,
) -> TwoComponentOIDCAdapter:
    return TwoComponentOIDCAdapter(
        config=config or _config(),
        protocol_client=protocol,
        verifier=verifier,
        attempt_store=store or _store(),
        audit_sink=audit or InMemoryOIDCAdapterAuditSink(),
    )


def test_msal_claims_cannot_bypass_raw_id_token_verification() -> None:
    protocol = _ClaimsShortcutProtocol()
    verifier = _RejectingVerifier()
    audit = InMemoryOIDCAdapterAuditSink()
    adapter = TwoComponentOIDCAdapter(
        config=_config(),
        protocol_client=protocol,
        verifier=verifier,
        attempt_store=EncryptedAuthorizationAttemptStore(
            encryption_key=Fernet.generate_key(),
            digest_key=b"authored-synthetic-digest-key-01",
        ),
        audit_sink=audit,
    )

    started = adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )
    assert started.authorization_uri.startswith(
        f"https://login.microsoftonline.com/{TENANT_ID}/"
    )

    with pytest.raises(OIDCAuthenticationFailed) as caught:
        adapter.complete_authorization_flow(
            auth_response={"code": "authored-synthetic-code", "state": STATE},
            now=NOW,
        )

    assert str(caught.value) == "authentication_failed"
    assert verifier.seen == [("forged.raw.id-token", NONCE)]
    assert protocol.redeem_calls == 1
    serialized_audit = repr(audit.events)
    assert "claims-shortcut" not in serialized_audit
    assert "must-be-discarded" not in serialized_audit
    assert "forged.raw.id-token" not in serialized_audit


def test_actual_msal_start_uses_minimal_form_post_flow_over_fake_transport() -> None:
    http = _MsalHttp()
    protocol = MSALAuthorizationCodeClient(
        config=_config(),
        client_credential="authored-synthetic-secret",
        http_client=http,
    )
    store = _store()
    adapter = _adapter(protocol, _AcceptingVerifier(), store=store)

    result = adapter.create_authorization_flow(
        surface=Surface.WORD_DESKTOP,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )

    query = parse_qs(urlsplit(result.authorization_uri).query)
    assert set(query["scope"][0].split()) == {"openid", "profile"}
    assert query["response_mode"] == ["form_post"]
    assert query["code_challenge_method"] == ["S256"]
    assert "offline_access" not in query["scope"][0]
    assert "email" not in query["scope"][0]
    assert len(query["state"][0]) == 22
    assert result.attempt_expires_at == NOW + timedelta(minutes=5)
    assert store.active_count == 1
    assert http.get_count >= 1
    assert http.post_count == 0


def test_actual_msal_redemption_port_performs_one_intercepted_exchange() -> None:
    http = _MsalHttp(
        post_response={
            "error": "invalid_grant",
            "error_description": "authored-synthetic rejection",
        }
    )
    protocol = MSALAuthorizationCodeClient(
        config=_config(),
        client_credential="authored-synthetic-secret",
        http_client=http,
    )
    flow = protocol.create_authorization_flow()

    result = protocol.redeem_authorization_flow(
        flow,
        {"code": "authored-synthetic-code", "state": flow["state"]},
    )

    assert result["error"] == "invalid_grant"
    assert http.post_count == 1


def test_success_returns_only_verified_principal_and_bounded_context() -> None:
    protocol = _SuccessProtocol()
    verifier = _AcceptingVerifier()
    audit = InMemoryOIDCAdapterAuditSink()
    adapter = _adapter(protocol, verifier, audit=audit)
    adapter.create_authorization_flow(
        surface=Surface.NATIVE_DIARY,
        return_target=ReturnTarget.DIARY,
        now=NOW,
    )

    completed = adapter.complete_authorization_flow(
        auth_response={"code": "authored-synthetic-code", "state": STATE},
        now=NOW,
    )

    assert completed == CompletedAuthorization(
        principal=VerifiedMicrosoftPrincipal(
            tenant_id=TENANT_ID,
            object_id="authored-synthetic-object",
            subject="authored-synthetic-subject",
        ),
        surface=Surface.NATIVE_DIARY,
        origin="https://synthetic.invalid",
        return_target=ReturnTarget.DIARY,
    )
    assert {field.name for field in fields(VerifiedMicrosoftPrincipal)} == {
        "tenant_id",
        "object_id",
        "subject",
        "provider",
        "authority_mode",
        "verified_source",
        "authorization_granted",
        "session_created",
    }
    assert not completed.authorization_granted
    assert not completed.session_created
    assert not completed.product_data_released
    serialized = repr((completed, audit.events))
    assert "discarded-access-token" not in serialized
    assert "discarded-refresh-token" not in serialized
    assert "signed.synthetic.id-token" not in serialized
    assert audit.events[-1].token_exchange_attempted is True


def test_default_off_rejects_before_protocol_or_verifier_work() -> None:
    protocol = _CountingDisabledProtocol()
    config = MicrosoftOIDCAdapterConfig(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        surface_origins=_config().surface_origins,
        enabled=False,
    )
    adapter = _adapter(protocol, _RejectingVerifier(), config=config)

    with pytest.raises(OIDCAuthenticationFailed) as caught:
        adapter.create_authorization_flow(
            surface=Surface.WORD_ONLINE,
            return_target=ReturnTarget.CLINICIAN_ONE,
            now=NOW,
        )

    assert caught.value.reason_code == "federation_disabled"
    assert protocol.create_calls == 0
    assert protocol.redeem_calls == 0


def test_default_off_is_enforced_inside_both_component_ports() -> None:
    disabled = MicrosoftOIDCAdapterConfig(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        surface_origins=_config().surface_origins,
        enabled=False,
    )
    http = _MsalHttp()
    protocol = MSALAuthorizationCodeClient(
        config=disabled,
        client_credential="authored-synthetic-secret",
        http_client=http,
    )
    with pytest.raises(OIDCAuthenticationFailed) as protocol_error:
        protocol.create_authorization_flow()
    assert protocol_error.value.reason_code == "federation_disabled"
    assert http.get_count == http.post_count == 0

    factory_calls = 0

    def factory() -> _OfflineOpenIDClient:
        nonlocal factory_calls
        factory_calls += 1
        return _OfflineOpenIDClient({"keys": []})

    verifier = AuthlibIDTokenVerifier(config=disabled, client_factory=factory)
    with pytest.raises(OIDCAuthenticationFailed) as verifier_error:
        verifier.verify_id_token("x.y.z", expected_nonce=NONCE, now=NOW)
    assert verifier_error.value.reason_code == "federation_disabled"
    assert factory_calls == 0


def test_attempt_store_contains_ciphertext_and_digests_not_flow_secrets() -> None:
    protocol = _SuccessProtocol()
    store = _store()
    adapter = _adapter(protocol, _AcceptingVerifier(), store=store)
    adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )

    stored_repr = repr(store._attempts)  # security regression: inspect residue
    assert STATE not in stored_repr
    assert NONCE not in stored_repr
    assert CODE_VERIFIER not in stored_repr
    assert REDIRECT_URI not in stored_repr
    assert "gAAAA" in stored_repr


def test_wrong_state_and_malformed_callback_do_not_redeem_or_consume() -> None:
    protocol = _SuccessProtocol()
    store = _store()
    audit = InMemoryOIDCAdapterAuditSink()
    adapter = _adapter(protocol, _AcceptingVerifier(), store=store, audit=audit)
    adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )

    with pytest.raises(OIDCAuthenticationFailed):
        adapter.complete_authorization_flow(
            auth_response={"code": "authored-synthetic-code", "state": "x" * 43},
            now=NOW,
        )
    with pytest.raises(OIDCAuthenticationFailed):
        adapter.complete_authorization_flow(
            auth_response={
                "code": "authored-synthetic-code",
                "state": STATE,
                "unexpected": "claim",
            },
            now=NOW,
        )

    assert protocol.redeem_calls == 0
    assert store.active_count == 1
    assert audit.events[-1].reason_code == "callback_response_invalid"


def test_provider_failure_consumes_attempt_and_never_retries_exchange() -> None:
    protocol = _SuccessProtocol(fail_redeem=True)
    store = _store()
    adapter = _adapter(protocol, _AcceptingVerifier(), store=store)
    adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )

    with pytest.raises(OIDCTemporarilyUnavailable) as first:
        adapter.complete_authorization_flow(
            auth_response={"code": "authored-synthetic-code", "state": STATE},
            now=NOW,
        )
    with pytest.raises(OIDCAuthenticationFailed) as replay:
        adapter.complete_authorization_flow(
            auth_response={"code": "authored-synthetic-code", "state": STATE},
            now=NOW,
        )

    assert str(first.value) == "authentication_temporarily_unavailable"
    assert "diagnostic" not in str(first.value)
    assert replay.value.reason_code == "authorization_attempt_required"
    assert protocol.redeem_calls == 1
    assert store.active_count == 0


def test_concurrent_callback_allows_exactly_one_redemption() -> None:
    protocol = _SuccessProtocol()
    store = _store()
    adapter = _adapter(protocol, _AcceptingVerifier(), store=store)
    adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )
    barrier = threading.Barrier(3)
    outcomes: list[str] = []
    outcome_lock = threading.Lock()

    def complete() -> None:
        barrier.wait()
        try:
            adapter.complete_authorization_flow(
                auth_response={"code": "authored-synthetic-code", "state": STATE},
                now=NOW,
            )
            result = "pass"
        except OIDCAuthenticationFailed:
            result = "deny"
        with outcome_lock:
            outcomes.append(result)

    threads = [threading.Thread(target=complete) for _ in range(2)]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == ["deny", "pass"]
    assert protocol.redeem_calls == 1


def test_expiry_capacity_and_required_audit_fail_closed() -> None:
    protocol = _SuccessProtocol()
    store = _store(max_attempts=1)
    adapter = _adapter(protocol, _AcceptingVerifier(), store=store)
    adapter.create_authorization_flow(
        surface=Surface.WORD_ONLINE,
        return_target=ReturnTarget.CLINICIAN_ONE,
        now=NOW,
    )
    with pytest.raises(OIDCAuthenticationFailed) as expired:
        adapter.complete_authorization_flow(
            auth_response={"code": "authored-synthetic-code", "state": STATE},
            now=NOW + timedelta(seconds=301),
        )
    assert expired.value.reason_code == "authorization_attempt_expired"
    assert protocol.redeem_calls == 0

    unavailable_store = _store()
    unavailable_adapter = _adapter(
        _SuccessProtocol(),
        _AcceptingVerifier(),
        store=unavailable_store,
        audit=InMemoryOIDCAdapterAuditSink(available=False),
    )
    with pytest.raises(OIDCTemporarilyUnavailable) as unavailable:
        unavailable_adapter.create_authorization_flow(
            surface=Surface.WORD_ONLINE,
            return_target=ReturnTarget.CLINICIAN_ONE,
            now=NOW,
        )
    assert unavailable.value.reason_code == "required_audit_unavailable"
    assert unavailable_store.active_count == 0


def test_authlib_verifier_accepts_valid_token_and_one_key_rollover() -> None:
    key1 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key2 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks1 = {"keys": [_public_jwk(key1, "key-1")]}
    jwks2 = {"keys": [_public_jwk(key2, "key-2")]}

    direct_client = _OfflineOpenIDClient(jwks1)
    direct = AuthlibIDTokenVerifier(
        config=_config(), client_factory=lambda: direct_client
    )
    principal = direct.verify_id_token(
        _signed_token(key1, "key-1"), expected_nonce=NONCE, now=NOW
    )
    assert principal.verified_source == "authlib_joserfc"
    assert principal.tenant_id == TENANT_ID
    assert not principal.authorization_granted

    rollover_client = _OfflineOpenIDClient(jwks1, jwks2)
    rollover = AuthlibIDTokenVerifier(
        config=_config(), client_factory=lambda: rollover_client
    )
    rolled = rollover.verify_id_token(
        _signed_token(key2, "key-2"), expected_nonce=NONCE, now=NOW
    )
    assert rolled.object_id == "authored-synthetic-object"
    assert rollover_client.session.requests == 1


def test_concrete_authlib_client_pins_discovery_and_jwks_transport() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = {"keys": [_public_jwk(key, "key-1")]}
    session = _PinnedMetadataSession(jwks)
    client = AuthlibOpenIDClient(config=_config(), http_session=session)
    verifier = AuthlibIDTokenVerifier(config=_config(), client_factory=lambda: client)

    principal = verifier.verify_id_token(
        _signed_token(key, "key-1"),
        expected_nonce=NONCE,
        now=NOW,
    )

    assert principal.tenant_id == TENANT_ID
    assert session.urls == [_config().discovery_url, JWKS_URI]


def test_authlib_verifier_denies_signed_token_fault_matrix() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = {"keys": [_public_jwk(key, "key-1")]}
    now = int(time.time())
    valid = _signed_token(key, "key-1")
    hs256 = pyjwt.encode(
        {
            "iss": ISSUER,
            "aud": CLIENT_ID,
            "sub": "subject",
            "tid": TENANT_ID,
            "oid": "object",
            "nonce": NONCE,
            "iat": now,
            "nbf": now - 1,
            "exp": now + 300,
        },
        "authored-synthetic-secret-longer-than-32-bytes",
        algorithm="HS256",
        headers={"kid": "key-1"},
    )
    cases = {
        "tampered_signature": (_tamper_signature(valid), NONCE),
        "wrong_algorithm": (hs256, NONCE),
        "wrong_issuer": (
            _signed_token(key, "key-1", iss="https://evil.invalid/v2.0"),
            NONCE,
        ),
        "wrong_audience": (_signed_token(key, "key-1", aud="wrong"), NONCE),
        "wrong_nonce": (valid, "x" * 43),
        "expired": (_signed_token(key, "key-1", exp=now - 120), NONCE),
        "not_yet_valid": (_signed_token(key, "key-1", nbf=now + 120), NONCE),
        "future_iat": (_signed_token(key, "key-1", iat=now + 120), NONCE),
        "wrong_tenant": (_signed_token(key, "key-1", tid="wrong"), NONCE),
        "missing_oid": (_signed_token(key, "key-1", omit=("oid",)), NONCE),
        "missing_sub": (_signed_token(key, "key-1", omit=("sub",)), NONCE),
        "missing_nbf": (_signed_token(key, "key-1", omit=("nbf",)), NONCE),
    }

    for case_id, (token, nonce) in cases.items():
        client = _OfflineOpenIDClient(jwks)
        verifier = AuthlibIDTokenVerifier(
            config=_config(), client_factory=lambda client=client: client
        )
        with pytest.raises(OIDCAuthenticationFailed) as caught:
            verifier.verify_id_token(token, expected_nonce=nonce, now=NOW)
        assert str(caught.value) == "authentication_failed", case_id
        assert token not in str(caught.value), case_id


def test_authlib_verifier_bounds_metadata_rollover_and_client_lifetime() -> None:
    key1 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key2 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks1 = {"keys": [_public_jwk(key1, "key-1")]}
    unknown = _signed_token(key2, "key-2")

    invalid_rollover = _OfflineOpenIDClient(jwks1, jwks1)
    verifier = AuthlibIDTokenVerifier(
        config=_config(), client_factory=lambda: invalid_rollover
    )
    with pytest.raises(OIDCAuthenticationFailed):
        verifier.verify_id_token(unknown, expected_nonce=NONCE, now=NOW)
    assert invalid_rollover.session.requests == 1

    outage = _OfflineOpenIDClient(jwks1, None)
    verifier = AuthlibIDTokenVerifier(config=_config(), client_factory=lambda: outage)
    with pytest.raises(OIDCTemporarilyUnavailable) as unavailable:
        verifier.verify_id_token(unknown, expected_nonce=NONCE, now=NOW)
    assert str(unavailable.value) == "authentication_temporarily_unavailable"
    assert outage.session.requests == 1

    mismatch = _OfflineOpenIDClient(
        jwks1,
        metadata_overrides={
            "id_token_signing_alg_values_supported": ["RS256", "ES256"]
        },
    )
    verifier = AuthlibIDTokenVerifier(config=_config(), client_factory=lambda: mismatch)
    with pytest.raises(OIDCTemporarilyUnavailable) as metadata_error:
        verifier.verify_id_token(
            _signed_token(key1, "key-1"), expected_nonce=NONCE, now=NOW
        )
    assert metadata_error.value.reason_code == "metadata_algorithm_mismatch"

    factory_calls: list[_OfflineOpenIDClient] = []

    def factory() -> _OfflineOpenIDClient:
        client = _OfflineOpenIDClient(jwks1)
        factory_calls.append(client)
        return client

    verifier = AuthlibIDTokenVerifier(config=_config(), client_factory=factory)
    token = _signed_token(key1, "key-1")
    verifier.verify_id_token(token, expected_nonce=NONCE, now=NOW)
    verifier.verify_id_token(
        token,
        expected_nonce=NONCE,
        now=NOW + timedelta(hours=24),
    )
    assert len(factory_calls) == 2

    never_called = 0

    def forbidden_factory() -> _OfflineOpenIDClient:
        nonlocal never_called
        never_called += 1
        return _OfflineOpenIDClient(jwks1)

    verifier = AuthlibIDTokenVerifier(
        config=_config(), client_factory=forbidden_factory
    )
    with pytest.raises(OIDCAuthenticationFailed) as oversized:
        verifier.verify_id_token("x" * 16_385, expected_nonce=NONCE, now=NOW)
    assert oversized.value.reason_code == "raw_id_token_oversized"
    assert never_called == 0


def test_adapter_is_route_free_and_not_wired_to_application_runtime() -> None:
    adapter_name = "application_identity_oidc_adapter"
    runtime_paths = [ROOT / "main.py", *(ROOT / "app" / "routers").rglob("*.py")]
    assert all(adapter_name not in path.read_text(encoding="utf-8") for path in runtime_paths)
    assert "application_identity_federation" not in (
        ROOT / "app" / "services" / "application_identity_oidc_adapter.py"
    ).read_text(encoding="utf-8")


def test_provider_free_acceptance_evidence_is_complete_and_reproducible() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    recorded = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    fresh = run_acceptance()

    assert recorded == fresh
    assert fresh["result"] == "pass"
    assert len(fresh["cases"]) == 25
    assert {item["case_id"] for item in fresh["cases"]} == {
        item["id"] for item in cases["cases"]
    }
    assert all(item["matched"] for item in fresh["cases"])
    assert all(value == 0 for value in fresh["side_effects"].values())
