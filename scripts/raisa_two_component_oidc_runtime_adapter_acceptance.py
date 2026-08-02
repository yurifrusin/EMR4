from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urlsplit

import jwt as pyjwt
from authlib.integrations.base_client.sync_openid import OpenIDMixin
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_identity_oidc_adapter import (
    AuthlibIDTokenVerifier,
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


TRANCHE = "raisa-two-component-oidc-runtime-adapter"
EVIDENCE_DIR = ROOT / "orchestration" / "continuity" / TRANCHE
CASES_PATH = EVIDENCE_DIR / "acceptance-cases.json"
DEFAULT_OUTPUT = EVIDENCE_DIR / "provider-free-acceptance-evidence.json"
RECORDED_AT = "2026-08-02T04:30:00Z"
TENANT_ID = "11111111-2222-3333-4444-555555555555"
CLIENT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
ISSUER = f"{AUTHORITY}/v2.0"
JWKS_URI = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
REDIRECT_URI = "https://synthetic.invalid/api/v1/application-auth/federation/microsoft/callback"
NOW = datetime(2026, 8, 2, 4, 0, tzinfo=timezone.utc)
STATE = "s" * 43
NONCE = "n" * 43
CODE_VERIFIER = "v" * 43


def _config(*, enabled: bool = True) -> MicrosoftOIDCAdapterConfig:
    return MicrosoftOIDCAdapterConfig(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        surface_origins={
            Surface.WORD_DESKTOP: "https://localhost:3000",
            Surface.WORD_ONLINE: "https://word-edit.officeapps.live.com",
            Surface.NATIVE_DIARY: "https://synthetic.invalid",
        },
        enabled=enabled,
    )


def _store() -> EncryptedAuthorizationAttemptStore:
    return EncryptedAuthorizationAttemptStore(
        encryption_key=Fernet.generate_key(),
        digest_key=b"authored-synthetic-digest-key-01",
    )


def _flow() -> dict[str, Any]:
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
            "response_mode": "form_post",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "nonce": hashlib.sha256(NONCE.encode("ascii")).hexdigest(),
            "client_info": "1",
        }
    )
    return {
        "state": STATE,
        "redirect_uri": REDIRECT_URI,
        "scope": ["openid", "profile"],
        "auth_uri": f"{AUTHORITY}/oauth2/v2.0/authorize?{query}",
        "code_verifier": CODE_VERIFIER,
        "nonce": NONCE,
        "claims_challenge": None,
    }


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
        self.post_response = post_response
        self.get_count = 0
        self.post_count = 0

    def get(self, url: str, **_: Any) -> _Response:
        self.get_count += 1
        if not url.startswith(AUTHORITY):
            raise AssertionError("unexpected intercepted metadata URL")
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
            raise AssertionError("unexpected intercepted token exchange")
        return _Response(self.post_response)


class _Protocol:
    def __init__(self, token: str = "signed.synthetic.id-token", *, fail: bool = False) -> None:
        self.token = token
        self.fail = fail
        self.create_calls = 0
        self.redeem_calls = 0

    def create_authorization_flow(self) -> dict[str, Any]:
        self.create_calls += 1
        return _flow()

    def redeem_authorization_flow(self, *_: Any) -> dict[str, Any]:
        self.redeem_calls += 1
        if self.fail:
            raise RuntimeError("provider diagnostic must never escape")
        return {
            "id_token": self.token,
            "id_token_claims": {"tid": TENANT_ID, "oid": "unsafe", "sub": "unsafe"},
            "access_token": "discarded-access-token",
            "refresh_token": "discarded-refresh-token",
        }


class _AcceptingVerifier:
    def verify_id_token(self, raw_id_token: str, *, expected_nonce: str, now: datetime) -> VerifiedMicrosoftPrincipal:
        if raw_id_token != "signed.synthetic.id-token" or expected_nonce != NONCE:
            raise OIDCAuthenticationFailed("token_signature_invalid")
        return VerifiedMicrosoftPrincipal(
            tenant_id=TENANT_ID,
            object_id="authored-synthetic-object",
            subject="authored-synthetic-subject",
        )


class _RejectingVerifier:
    def verify_id_token(self, *_: Any, **__: Any) -> VerifiedMicrosoftPrincipal:
        raise OIDCAuthenticationFailed("token_signature_invalid")


class _JwksSession:
    def __init__(self, refreshed: dict[str, Any] | None) -> None:
        self.refreshed = refreshed
        self.requests = 0

    def __enter__(self) -> "_JwksSession":
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        if method != "GET" or url != JWKS_URI or kwargs.get("withhold_token") is not True:
            raise AssertionError("unexpected verifier request")
        self.requests += 1
        if self.refreshed is None:
            raise RuntimeError("refresh unavailable")
        return _Response(self.refreshed)


class _OfflineOpenIDClient(OpenIDMixin):
    def __init__(
        self,
        initial: dict[str, Any],
        refreshed: dict[str, Any] | None = None,
        *,
        algorithms: list[str] | None = None,
    ) -> None:
        self.client_id = CLIENT_ID
        self.server_metadata = {
            "issuer": ISSUER,
            "authorization_endpoint": f"{AUTHORITY}/oauth2/v2.0/authorize",
            "token_endpoint": f"{AUTHORITY}/oauth2/v2.0/token",
            "jwks_uri": JWKS_URI,
            "jwks": initial,
            "id_token_signing_alg_values_supported": algorithms or ["RS256"],
        }
        self.session = _JwksSession(refreshed)

    def load_server_metadata(self) -> dict[str, Any]:
        return self.server_metadata

    def _get_session(self) -> _JwksSession:
        return self.session


def _b64uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _jwk(key: rsa.RSAPrivateKey, kid: str) -> dict[str, str]:
    numbers = key.public_key().public_numbers()
    return {"kty": "RSA", "use": "sig", "kid": kid, "n": _b64uint(numbers.n), "e": _b64uint(numbers.e)}


def _token(key: rsa.RSAPrivateKey, kid: str, **overrides: Any) -> str:
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
    return pyjwt.encode(claims, key, algorithm="RS256", headers={"kid": kid})


def _verifier(client: OpenIDMixin) -> AuthlibIDTokenVerifier:
    return AuthlibIDTokenVerifier(config=_config(), client_factory=lambda: client)


def _adapter(protocol: Any, verifier: Any, *, store: EncryptedAuthorizationAttemptStore | None = None, audit: InMemoryOIDCAdapterAuditSink | None = None, enabled: bool = True) -> TwoComponentOIDCAdapter:
    return TwoComponentOIDCAdapter(
        config=_config(enabled=enabled),
        protocol_client=protocol,
        verifier=verifier,
        attempt_store=store or _store(),
        audit_sink=audit or InMemoryOIDCAdapterAuditSink(),
    )


def _start(adapter: TwoComponentOIDCAdapter) -> None:
    adapter.create_authorization_flow(surface=Surface.WORD_ONLINE, return_target=ReturnTarget.CLINICIAN_ONE, now=NOW)


def _complete(adapter: TwoComponentOIDCAdapter, state: str = STATE) -> Any:
    return adapter.complete_authorization_flow(auth_response={"code": "authored-synthetic-code", "state": state}, now=NOW)


def _outcome(case_id: str, expected: str, action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
        actual = "pass"
    except OIDCAuthenticationFailed:
        actual = "deny"
    except OIDCTemporarilyUnavailable:
        actual = "unavailable"
    except Exception:
        actual = "harness_error"
    return {"case_id": case_id, "expected": expected, "actual": actual, "matched": actual == expected}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_acceptance() -> dict[str, Any]:
    case_doc = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    key1 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key2 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks1 = {"keys": [_jwk(key1, "key-1")]}
    jwks2 = {"keys": [_jwk(key2, "key-2")]}
    valid = _token(key1, "key-1")
    now_epoch = int(time.time())

    def default_off() -> None:
        protocol = _Protocol()
        adapter = _adapter(protocol, _AcceptingVerifier(), enabled=False)
        try:
            _start(adapter)
        finally:
            _require(
                protocol.create_calls == protocol.redeem_calls == 0,
                "disabled adapter invoked a protocol port",
            )

    def msal_start() -> None:
        http = _MsalHttp()
        client = MSALAuthorizationCodeClient(config=_config(), client_credential="authored-synthetic-secret", http_client=http)
        flow = client.create_authorization_flow()
        query = parse_qs(urlsplit(flow["auth_uri"]).query)
        _require(
            set(query["scope"][0].split()) == {"openid", "profile"},
            "MSAL scope mismatch",
        )
        _require(query["response_mode"] == ["form_post"], "MSAL response mode mismatch")
        _require(query["code_challenge_method"] == ["S256"], "MSAL PKCE mismatch")
        _require(http.post_count == 0, "start performed a token exchange")

    def msal_exchange() -> None:
        http = _MsalHttp({"error": "invalid_grant", "error_description": "synthetic"})
        client = MSALAuthorizationCodeClient(config=_config(), client_credential="authored-synthetic-secret", http_client=http)
        flow = client.create_authorization_flow()
        result = client.redeem_authorization_flow(flow, {"code": "synthetic", "state": flow["state"]})
        _require(
            http.post_count == 1 and result["error"] == "invalid_grant",
            "MSAL intercepted exchange count/result mismatch",
        )
        raise OIDCAuthenticationFailed("token_exchange_rejected")

    def verify(token: str, nonce: str = NONCE, *, client: OpenIDMixin | None = None) -> VerifiedMicrosoftPrincipal:
        selected = client or _OfflineOpenIDClient(jwks1)
        return _verifier(selected).verify_id_token(token, expected_nonce=nonce, now=NOW)

    def claims_bypass() -> None:
        adapter = _adapter(_Protocol("forged.raw.token"), _RejectingVerifier())
        _start(adapter)
        _complete(adapter)

    def encrypted_residue() -> None:
        store = _store()
        adapter = _adapter(_Protocol(), _AcceptingVerifier(), store=store)
        _start(adapter)
        residue = repr(store._attempts)
        _require(
            all(value not in residue for value in (STATE, NONCE, CODE_VERIFIER, REDIRECT_URI)),
            "plaintext flow material remained in the attempt store",
        )

    def wrong_state() -> None:
        protocol = _Protocol()
        adapter = _adapter(protocol, _AcceptingVerifier())
        _start(adapter)
        try:
            _complete(adapter, "x" * 43)
        finally:
            _require(protocol.redeem_calls == 0, "wrong state invoked token exchange")

    def consumed_after_failure() -> None:
        protocol = _Protocol(fail=True)
        adapter = _adapter(protocol, _AcceptingVerifier())
        _start(adapter)
        try:
            _complete(adapter)
        except OIDCTemporarilyUnavailable:
            pass
        try:
            _complete(adapter)
        finally:
            _require(protocol.redeem_calls == 1, "failed exchange was retried")

    def concurrent() -> None:
        protocol = _Protocol()
        adapter = _adapter(protocol, _AcceptingVerifier())
        _start(adapter)
        barrier = threading.Barrier(3)
        outcomes: list[str] = []
        lock = threading.Lock()

        def worker() -> None:
            barrier.wait()
            try:
                _complete(adapter)
                value = "pass"
            except OIDCAuthenticationFailed:
                value = "deny"
            with lock:
                outcomes.append(value)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join()
        _require(
            sorted(outcomes) == ["deny", "pass"] and protocol.redeem_calls == 1,
            "concurrent callback did not remain one-use",
        )

    def audit_unavailable() -> None:
        adapter = _adapter(_Protocol(), _AcceptingVerifier(), audit=InMemoryOIDCAdapterAuditSink(available=False))
        _start(adapter)

    def route_free() -> None:
        name = "application_identity_oidc_adapter"
        runtime_paths = [ROOT / "main.py", *(ROOT / "app" / "routers").rglob("*.py")]
        _require(
            all(name not in path.read_text(encoding="utf-8") for path in runtime_paths),
            "adapter is wired to an application route",
        )

    def rollover() -> None:
        client = _OfflineOpenIDClient(jwks1, jwks2)
        verify(_token(key2, "key-2"), client=client)
        _require(client.session.requests == 1, "valid rollover refresh count mismatch")

    def unknown_after_refresh(refreshed: dict[str, Any] | None) -> None:
        client = _OfflineOpenIDClient(jwks1, refreshed)
        try:
            verify(_token(key2, "key-2"), client=client)
        finally:
            _require(client.session.requests == 1, "unknown-key refresh count mismatch")

    valid_parts = valid.split(".")
    signature = bytearray(base64.urlsafe_b64decode(valid_parts[2] + "=" * (-len(valid_parts[2]) % 4)))
    signature[0] ^= 1
    tampered = ".".join((valid_parts[0], valid_parts[1], base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")))
    hs256 = pyjwt.encode(
        {"iss": ISSUER, "aud": CLIENT_ID, "sub": "s", "tid": TENANT_ID, "oid": "o", "nonce": NONCE, "iat": now_epoch, "nbf": now_epoch - 1, "exp": now_epoch + 300},
        "authored-synthetic-secret-longer-than-32-bytes",
        algorithm="HS256",
        headers={"kid": "key-1"},
    )
    actions: dict[str, Callable[[], Any]] = {
        "default_off_before_protocol": default_off,
        "msal_minimal_form_post": msal_start,
        "msal_intercepted_single_exchange": msal_exchange,
        "valid_rs256_external_principal": lambda: verify(valid),
        "msal_claims_bypass": claims_bypass,
        "tampered_signature": lambda: verify(tampered),
        "wrong_algorithm": lambda: verify(hs256),
        "wrong_issuer": lambda: verify(_token(key1, "key-1", iss="https://evil.invalid/v2.0")),
        "wrong_audience": lambda: verify(_token(key1, "key-1", aud="wrong")),
        "wrong_nonce": lambda: verify(valid, "x" * 43),
        "wrong_tenant": lambda: verify(_token(key1, "key-1", tid="wrong")),
        "missing_identifier": lambda: verify(_token(key1, "key-1", oid="")),
        "expired_token": lambda: verify(_token(key1, "key-1", exp=now_epoch - 120)),
        "future_token": lambda: verify(_token(key1, "key-1", nbf=now_epoch + 120)),
        "valid_key_rollover": rollover,
        "unknown_kid_after_one_refresh": lambda: unknown_after_refresh(jwks1),
        "jwks_refresh_outage": lambda: unknown_after_refresh(None),
        "oversized_raw_token": lambda: verify("x" * 16_385),
        "metadata_algorithm_mismatch": lambda: verify(valid, client=_OfflineOpenIDClient(jwks1, algorithms=["RS256", "ES256"])),
        "encrypted_attempt_residue": encrypted_residue,
        "wrong_state_no_exchange": wrong_state,
        "failed_exchange_consumes_attempt": consumed_after_failure,
        "concurrent_callback_single_exchange": concurrent,
        "required_audit_unavailable": audit_unavailable,
        "route_free_non_wiring": route_free,
    }
    results = [_outcome(case["id"], case["expected"], actions[case["id"]]) for case in case_doc["cases"]]
    passed = all(result["matched"] for result in results)
    return {
        "schema_version": "emr4.two-component-oidc-runtime-adapter-acceptance.v1",
        "recorded_at": RECORDED_AT,
        "result": "pass" if passed else "revision_required",
        "data_class": "authored_synthetic",
        "implementation": {
            "module": "app/services/application_identity_oidc_adapter.py",
            "protocol_owner": "msal==1.37.0",
            "verification_owner": "Authlib==1.7.2+joserfc==1.7.4",
            "attempt_store": "bounded_in_memory_envelope_encrypted_provider_free_port",
            "default_off": True,
            "mounted": False,
        },
        "cases": results,
        "side_effects": {
            "outbound_network_calls": 0,
            "microsoft_provider_calls": 0,
            "real_identities": 0,
            "identity_bindings": 0,
            "mounted_routes": 0,
            "database_writes": 0,
            "sessions_created": 0,
            "product_reads": 0,
            "deployments": 0,
        },
        "next_authority_required": "provider_free_postgresql_authorization_attempt_store",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = run_acceptance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
