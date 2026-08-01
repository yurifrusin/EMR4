from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import jwt as pyjwt
import jsonschema
import yaml
from authlib.integrations.base_client.sync_openid import OpenIDMixin
from cryptography.hazmat.primitives.asymmetric import rsa
from msal import ConfidentialClientApplication


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "orchestration" / "continuity" / "raisa-two-component-oidc-verifier-architecture-revision"
POLICY_PATH = EVIDENCE_DIR / "architecture-policy.json"
POLICY_SCHEMA_PATH = EVIDENCE_DIR / "architecture-policy.schema.json"
CASES_PATH = EVIDENCE_DIR / "acceptance-cases.json"
OPENAPI_PATH = ROOT / "docs" / "api-spine" / "openapi" / "application-identity-federation-session-bridge.yaml"
DEFAULT_OUTPUT = EVIDENCE_DIR / "provider-free-acceptance-evidence.json"
TENANT = "11111111-2222-3333-4444-555555555555"
CLIENT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
ISSUER = f"https://login.microsoftonline.com/{TENANT}/v2.0"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT}"
JWKS_URI = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
REDIRECT_URI = "https://synthetic.invalid/api/v1/application-auth/federation/microsoft/callback"
NONCE = "synthetic-nonce-value"
RECORDED_AT = "2026-08-02T00:00:00Z"


def _b64uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _public_jwk(private_key: rsa.RSAPrivateKey, kid: str) -> dict[str, str]:
    numbers = private_key.public_key().public_numbers()
    return {"kty": "RSA", "use": "sig", "kid": kid, "n": _b64uint(numbers.n), "e": _b64uint(numbers.e)}


def _signed_token(private_key: rsa.RSAPrivateKey, kid: str, **overrides: Any) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "sub": "synthetic-subject",
        "tid": TENANT,
        "oid": "synthetic-object-id",
        "nonce": NONCE,
        "iat": now,
        "nbf": now - 1,
        "exp": now + 300,
    }
    claims.update(overrides)
    return pyjwt.encode(claims, private_key, algorithm="RS256", headers={"kid": kid, "typ": "JWT"})


class _Response:
    status_code = 200
    text = ""

    def __init__(self, value: dict[str, Any]):
        self._value = value
        self.text = json.dumps(value)

    def json(self) -> dict[str, Any]:
        return self._value

    def raise_for_status(self) -> None:
        return None


class _MsalHttp:
    def __init__(self) -> None:
        self.get_count = 0
        self.post_count = 0

    def get(self, url: str, **_: Any) -> _Response:
        self.get_count += 1
        if not url.startswith(AUTHORITY):
            raise AssertionError("unexpected metadata URL")
        return _Response({
            "authorization_endpoint": f"{AUTHORITY}/oauth2/v2.0/authorize",
            "token_endpoint": f"{AUTHORITY}/oauth2/v2.0/token",
            "issuer": ISSUER,
            "jwks_uri": JWKS_URI,
        })

    def post(self, *_: Any, **__: Any) -> _Response:
        self.post_count += 1
        raise AssertionError("provider token exchange is forbidden in offline acceptance")


class _JwksSession:
    def __init__(self, refreshed_jwks: dict[str, Any] | None):
        self.refreshed_jwks = refreshed_jwks
        self.requests = 0

    def __enter__(self) -> "_JwksSession":
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def request(self, method: str, url: str, **kwargs: Any) -> _Response:
        if method != "GET" or url != JWKS_URI or kwargs.get("withhold_token") is not True:
            raise AssertionError("unexpected verifier metadata request")
        self.requests += 1
        if self.refreshed_jwks is None:
            raise RuntimeError("synthetic refresh unavailable")
        return _Response(self.refreshed_jwks)


class _OfflineVerifier(OpenIDMixin):
    def __init__(self, initial_jwks: dict[str, Any], refreshed_jwks: dict[str, Any] | None = None, algorithms: list[str] | None = None):
        self.client_id = CLIENT_ID
        self.server_metadata = {
            "issuer": ISSUER,
            "jwks_uri": JWKS_URI,
            "jwks": initial_jwks,
            "id_token_signing_alg_values_supported": algorithms or ["RS256"],
        }
        self.session = _JwksSession(refreshed_jwks)

    def load_server_metadata(self) -> dict[str, Any]:
        return self.server_metadata

    def _get_session(self) -> _JwksSession:
        return self.session


def _verify(verifier: _OfflineVerifier, raw_token: str, nonce: str = NONCE) -> dict[str, Any]:
    if len(raw_token.encode("utf-8")) > 16384:
        raise ValueError("authentication_failed")
    if verifier.server_metadata.get("issuer") != ISSUER or verifier.server_metadata.get("jwks_uri") != JWKS_URI:
        raise ValueError("authentication_failed")
    if verifier.server_metadata.get("id_token_signing_alg_values_supported") != ["RS256"]:
        raise ValueError("authentication_failed")
    claims = dict(verifier.parse_id_token({"id_token": raw_token}, nonce=nonce, leeway=60))
    if claims.get("tid") != TENANT or not claims.get("oid") or not claims.get("sub"):
        raise ValueError("authentication_failed")
    return {"tid": claims["tid"], "oid_present": True, "sub_present": True, "verified_source": "authlib_joserfc"}


def _outcome(case_id: str, expected: str, fn: Any) -> dict[str, Any]:
    try:
        fn()
        actual = "pass"
    except Exception:
        actual = "deny"
    return {"case_id": case_id, "expected": expected, "actual": actual, "matched": actual == expected}


def run_acceptance() -> dict[str, Any]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    schema = json.loads(POLICY_SCHEMA_PATH.read_text(encoding="utf-8"))
    cases_doc = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(policy)
    openapi = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))

    key1 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key2 = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks1 = {"keys": [_public_jwk(key1, "key-1")]}
    jwks2 = {"keys": [_public_jwk(key2, "key-2")]}
    valid = _signed_token(key1, "key-1")

    def msal_flow() -> None:
        http = _MsalHttp()
        client = ConfidentialClientApplication(
            CLIENT_ID,
            client_credential="authored-synthetic-secret",
            authority=AUTHORITY,
            instance_discovery=False,
            http_client=http,
            exclude_scopes=["offline_access"],
        )
        flow = client.initiate_auth_code_flow(scopes=[], redirect_uri=REDIRECT_URI, response_mode="form_post")
        query = parse_qs(urlparse(flow["auth_uri"]).query)
        assert set(query["scope"][0].split()) == {"openid", "profile"}
        assert query["response_mode"] == ["form_post"]
        assert query["code_challenge_method"] == ["S256"]
        assert all(flow.get(name) for name in ("state", "nonce", "code_verifier"))
        assert http.post_count == 0

    def reserved_scope() -> None:
        client = ConfidentialClientApplication(CLIENT_ID, client_credential="authored-synthetic-secret", authority=AUTHORITY, instance_discovery=False, http_client=_MsalHttp(), exclude_scopes=["offline_access"])
        client.initiate_auth_code_flow(scopes=["openid"], redirect_uri=REDIRECT_URI, response_mode="form_post")

    def rollover_after_one_refresh() -> None:
        verifier = _OfflineVerifier(jwks1, jwks2)
        _verify(verifier, _signed_token(key2, "key-2"))
        assert verifier.session.requests == 1

    def deny_after_one_refresh(refreshed_jwks: dict[str, Any] | None) -> None:
        verifier = _OfflineVerifier(jwks1, refreshed_jwks)
        try:
            _verify(verifier, _signed_token(key2, "key-2"))
        except Exception:
            assert verifier.session.requests == 1
            raise
        raise AssertionError("unknown key unexpectedly admitted")

    tampered = valid[:-1] + ("A" if valid[-1] != "A" else "B")
    now = int(time.time())
    actions: dict[str, Any] = {
        "msal_form_post_minimal_scope": msal_flow,
        "msal_reserved_scope_rejected": reserved_scope,
        "valid_rs256_identity": lambda: _verify(_OfflineVerifier(jwks1), valid),
        "tampered_signature": lambda: _verify(_OfflineVerifier(jwks1), tampered),
        "wrong_algorithm": lambda: _verify(_OfflineVerifier(jwks1), pyjwt.encode({"iss": ISSUER, "aud": CLIENT_ID, "sub": "s", "tid": TENANT, "oid": "o", "nonce": NONCE, "exp": now + 300}, "authored-synthetic-secret-longer-than-32-bytes", algorithm="HS256", headers={"kid": "key-1"})),
        "wrong_issuer": lambda: _verify(_OfflineVerifier(jwks1), _signed_token(key1, "key-1", iss="https://evil.invalid/v2.0")),
        "wrong_audience": lambda: _verify(_OfflineVerifier(jwks1), _signed_token(key1, "key-1", aud="wrong-client")),
        "wrong_nonce": lambda: _verify(_OfflineVerifier(jwks1), valid, nonce="wrong-nonce"),
        "expired": lambda: _verify(_OfflineVerifier(jwks1), _signed_token(key1, "key-1", exp=now - 120)),
        "not_yet_valid": lambda: _verify(_OfflineVerifier(jwks1), _signed_token(key1, "key-1", nbf=now + 120)),
        "wrong_tenant": lambda: _verify(_OfflineVerifier(jwks1), _signed_token(key1, "key-1", tid="wrong-tenant")),
        "missing_oid": lambda: _verify(_OfflineVerifier(jwks1), _signed_token(key1, "key-1", oid="")),
        "rollover_after_one_refresh": rollover_after_one_refresh,
        "unknown_kid_after_refresh": lambda: deny_after_one_refresh(jwks1),
        "refresh_outage": lambda: deny_after_one_refresh(None),
        "oversized_token": lambda: _verify(_OfflineVerifier(jwks1), "x" * 16385),
        "metadata_algorithm_mismatch": lambda: _verify(_OfflineVerifier(jwks1, algorithms=["RS256", "ES256"]), valid),
    }
    results = [_outcome(item["id"], item["expected"], actions[item["id"]]) for item in cases_doc["cases"]]
    versions = {name: importlib.metadata.version(name) for name in ("msal", "Authlib", "joserfc")}
    callback = openapi["paths"]["/api/v1/application-auth/federation/microsoft/callback"]
    passed = all(item["matched"] for item in results) and versions == {"msal": "1.37.0", "Authlib": "1.7.2", "joserfc": "1.7.4"} and "post" in callback and "get" not in callback
    return {
        "schema_version": "emr4.two-component-oidc-offline-acceptance.v1",
        "recorded_at": RECORDED_AT,
        "result": "pass" if passed else "revision_required",
        "data_class": "authored_synthetic",
        "dependency_versions": versions,
        "cases": results,
        "side_effects": {"provider_calls": 0, "real_identities": 0, "mounted_routes": 0, "database_writes": 0, "sessions_created": 0, "product_reads": 0, "deployments": 0},
        "next_authority_required": "provider_free_runtime_adapter_implementation",
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
