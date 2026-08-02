"""Default-off, route-free Microsoft OIDC protocol and verifier adapter.

MSAL owns authorization-code protocol mechanics.  Authlib/JOSE RFC owns raw
ID-token verification.  This module deliberately does not mount a route,
resolve an EMR4 identity binding, create a role or session, read product data,
or persist provider material to PostgreSQL.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import parse_qs, urlsplit

import requests
from authlib.integrations.base_client.sync_openid import OpenIDMixin
from cryptography.fernet import Fernet, InvalidToken
from joserfc.errors import JoseError
from msal import ConfidentialClientApplication, TokenCache


PROVIDER = "microsoft_entra"
AUTHORITY_MODE = "tenant_specific_v2"
VERIFIED_SOURCE = "authlib_joserfc"
PKCE_METHOD = "S256"
MAX_ID_TOKEN_BYTES = 16_384
CLAIM_LEEWAY_SECONDS = 60
ATTEMPT_TTL_SECONDS = 300
MAX_VERIFIER_CLIENT_AGE_SECONDS = 86_400
MAX_ATTEMPTS = 128

_GUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
_OPAQUE = re.compile(r"^[A-Za-z0-9._~-]{16,256}$")
_CALLBACK_PATH = "/api/v1/application-auth/federation/microsoft/callback"
_MICROSOFT_HOST = "login.microsoftonline.com"
_JWKS_PATH = "/common/discovery/v2.0/keys"
_ALLOWED_CALLBACK_KEYS = frozenset(
    {"code", "state", "error", "error_description"}
)


class Surface(str, Enum):
    WORD_DESKTOP = "word_desktop"
    WORD_ONLINE = "word_online"
    NATIVE_DIARY = "native_diary"


class ReturnTarget(str, Enum):
    CLINICIAN_ONE = "clinician_one"
    RECEPTION_ONE = "reception_one"
    DIARY = "diary"


class OIDCAdapterError(RuntimeError):
    public_error: str
    http_status: int

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(self.public_error)


class OIDCAuthenticationFailed(OIDCAdapterError):
    public_error = "authentication_failed"
    http_status = 401


class OIDCTemporarilyUnavailable(OIDCAdapterError):
    public_error = "authentication_temporarily_unavailable"
    http_status = 503


class OIDCAdapterAuditUnavailable(RuntimeError):
    """The required normalized adapter audit could not be recorded."""


@dataclass(frozen=True)
class MicrosoftOIDCAdapterConfig:
    tenant_id: str
    client_id: str
    redirect_uri: str
    surface_origins: Mapping[Surface, str]
    enabled: bool = False
    attempt_ttl_seconds: int = ATTEMPT_TTL_SECONDS
    max_id_token_bytes: int = MAX_ID_TOKEN_BYTES
    claim_leeway_seconds: int = CLAIM_LEEWAY_SECONDS
    verifier_client_max_age_seconds: int = MAX_VERIFIER_CLIENT_AGE_SECONDS

    def __post_init__(self) -> None:
        tenant_id = _canonical_guid(self.tenant_id, "tenant_id")
        client_id = _canonical_guid(self.client_id, "client_id")
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "client_id", client_id)
        if self.redirect_uri != _canonical_callback_uri(self.redirect_uri):
            raise ValueError("redirect_uri must be the exact canonical HTTPS callback")
        if set(self.surface_origins) != set(Surface):
            raise ValueError("surface_origins must configure exactly the three surfaces")
        origins = {
            Surface(surface): _canonical_https_origin(origin)
            for surface, origin in self.surface_origins.items()
        }
        object.__setattr__(self, "surface_origins", origins)
        if self.attempt_ttl_seconds != ATTEMPT_TTL_SECONDS:
            raise ValueError("authorization attempt lifetime must be exactly five minutes")
        if self.max_id_token_bytes != MAX_ID_TOKEN_BYTES:
            raise ValueError("raw ID-token bound must be exactly 16 KiB")
        if self.claim_leeway_seconds != CLAIM_LEEWAY_SECONDS:
            raise ValueError("claim leeway must be exactly 60 seconds")
        if self.verifier_client_max_age_seconds > MAX_VERIFIER_CLIENT_AGE_SECONDS:
            raise ValueError("verifier client lifetime must not exceed 24 hours")
        if self.verifier_client_max_age_seconds < 60:
            raise ValueError("verifier client lifetime is too short")

    @property
    def authority(self) -> str:
        return f"https://{_MICROSOFT_HOST}/{self.tenant_id}"

    @property
    def issuer(self) -> str:
        return f"{self.authority}/v2.0"

    @property
    def discovery_url(self) -> str:
        return f"{self.issuer}/.well-known/openid-configuration"

    @property
    def jwks_uri(self) -> str:
        return f"https://{_MICROSOFT_HOST}{_JWKS_PATH}"


@dataclass(frozen=True)
class AuthorizationStart:
    status: str
    authorization_uri: str
    attempt_expires_at: datetime


@dataclass(frozen=True)
class VerifiedMicrosoftPrincipal:
    tenant_id: str
    object_id: str
    subject: str
    provider: str = PROVIDER
    authority_mode: str = AUTHORITY_MODE
    verified_source: str = VERIFIED_SOURCE
    authorization_granted: bool = False
    session_created: bool = False


@dataclass(frozen=True)
class CompletedAuthorization:
    principal: VerifiedMicrosoftPrincipal
    surface: Surface
    origin: str
    return_target: ReturnTarget
    authorization_granted: bool = False
    session_created: bool = False
    product_data_released: bool = False


@dataclass(frozen=True)
class OIDCAdapterAuditEvent:
    occurred_at: datetime
    event_type: str
    decision: str
    reason_code: str
    attempt_reference: str | None
    surface: str | None
    return_target: str | None
    token_exchange_attempted: bool
    principal_released: bool
    session_created: bool = False
    product_data_released: bool = False


class OIDCAdapterAuditSink(Protocol):
    def record(self, event: OIDCAdapterAuditEvent) -> None:
        raise NotImplementedError


class InMemoryOIDCAdapterAuditSink:
    def __init__(self, *, available: bool = True) -> None:
        self._available = available
        self._events: list[OIDCAdapterAuditEvent] = []
        self._lock = threading.Lock()

    def record(self, event: OIDCAdapterAuditEvent) -> None:
        if not self._available:
            raise OIDCAdapterAuditUnavailable("required OIDC adapter audit unavailable")
        with self._lock:
            self._events.append(event)

    @property
    def events(self) -> tuple[OIDCAdapterAuditEvent, ...]:
        with self._lock:
            return tuple(self._events)


class MSALAuthorizationCodePort(Protocol):
    def create_authorization_flow(self) -> Mapping[str, Any]:
        raise NotImplementedError

    def redeem_authorization_flow(
        self,
        stored_flow: Mapping[str, Any],
        auth_response: Mapping[str, str],
    ) -> Mapping[str, Any]:
        raise NotImplementedError


class IDTokenVerifierPort(Protocol):
    def verify_id_token(
        self,
        raw_id_token: str,
        *,
        expected_nonce: str,
        now: datetime,
    ) -> VerifiedMicrosoftPrincipal:
        raise NotImplementedError


class MSALAuthorizationCodeClient:
    """Sole protocol client; each redemption receives a fresh transient cache."""

    def __init__(
        self,
        *,
        config: MicrosoftOIDCAdapterConfig,
        client_credential: Any,
        http_client: Any | None = None,
    ) -> None:
        self._config = config
        self._client_credential = client_credential
        self._http_client = http_client

    def _new_client(self) -> ConfidentialClientApplication:
        kwargs: dict[str, Any] = {
            "client_credential": self._client_credential,
            "authority": self._config.authority,
            "instance_discovery": False,
            "exclude_scopes": ["offline_access"],
            "token_cache": TokenCache(),
        }
        if self._http_client is not None:
            kwargs["http_client"] = self._http_client
        return ConfidentialClientApplication(self._config.client_id, **kwargs)

    def create_authorization_flow(self) -> dict[str, Any]:
        if self._config.enabled is not True:
            raise OIDCAuthenticationFailed("federation_disabled")
        client = self._new_client()
        flow = client.initiate_auth_code_flow(
            scopes=[],
            redirect_uri=self._config.redirect_uri,
            response_mode="form_post",
        )
        return dict(flow)

    def redeem_authorization_flow(
        self,
        stored_flow: Mapping[str, Any],
        auth_response: Mapping[str, str],
    ) -> dict[str, Any]:
        if self._config.enabled is not True:
            raise OIDCAuthenticationFailed("federation_disabled")
        client = self._new_client()
        try:
            result = client.acquire_token_by_auth_code_flow(
                dict(stored_flow),
                dict(auth_response),
                scopes=[],
            )
            return dict(result)
        finally:
            client.token_cache = TokenCache()


class _PinnedOIDCHttpSession:
    def __init__(
        self,
        *,
        allowed_urls: frozenset[str],
        session: requests.Session | Any,
        max_response_bytes: int = 131_072,
    ) -> None:
        self._allowed_urls = allowed_urls
        self._session = session
        self._max_response_bytes = max_response_bytes

    def __enter__(self) -> "_PinnedOIDCHttpSession":
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        if method != "GET" or url not in self._allowed_urls:
            raise OIDCTemporarilyUnavailable("metadata_location_rejected")
        kwargs.pop("withhold_token", None)
        kwargs["allow_redirects"] = False
        kwargs.setdefault("timeout", (3.05, 5.0))
        kwargs.setdefault("stream", True)
        response = self._session.request(method, url, **kwargs)
        if getattr(response, "status_code", None) != 200:
            raise OIDCTemporarilyUnavailable("metadata_http_failure")
        content_length = response.headers.get("Content-Length") if hasattr(response, "headers") else None
        if content_length is not None and int(content_length) > self._max_response_bytes:
            raise OIDCTemporarilyUnavailable("metadata_response_oversized")
        if hasattr(response, "iter_content") and hasattr(response, "_content"):
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_content(chunk_size=16_384):
                total += len(chunk)
                if total > self._max_response_bytes:
                    raise OIDCTemporarilyUnavailable("metadata_response_oversized")
                chunks.append(chunk)
            response._content = b"".join(chunks)
            response._content_consumed = True
        else:
            text = getattr(response, "text", "")
            if (
                isinstance(text, str)
                and len(text.encode("utf-8")) > self._max_response_bytes
            ):
                raise OIDCTemporarilyUnavailable("metadata_response_oversized")
        return response

    def close(self) -> None:
        close = getattr(self._session, "close", None)
        if callable(close):
            close()


class AuthlibOpenIDClient(OpenIDMixin):
    """Pinned discovery/JWKS transport used only by Authlib verification."""

    def __init__(
        self,
        *,
        config: MicrosoftOIDCAdapterConfig,
        http_session: requests.Session | Any | None = None,
    ) -> None:
        self._config = config
        self.client_id = config.client_id
        self.server_metadata: dict[str, Any] = {}
        base_session = http_session if http_session is not None else requests.Session()
        self._session = _PinnedOIDCHttpSession(
            allowed_urls=frozenset({config.discovery_url, config.jwks_uri}),
            session=base_session,
        )

    def _get_session(self) -> _PinnedOIDCHttpSession:
        return self._session

    def load_server_metadata(self) -> dict[str, Any]:
        if self.server_metadata:
            return self.server_metadata
        with self._get_session() as session:
            response = session.request(
                "GET",
                self._config.discovery_url,
                withhold_token=True,
            )
            try:
                metadata = response.json()
            except Exception:
                raise OIDCTemporarilyUnavailable("metadata_json_invalid") from None
        _validate_metadata(self._config, metadata)
        self.server_metadata = dict(metadata)
        return self.server_metadata

    def close(self) -> None:
        self._session.close()


class AuthlibIDTokenVerifier:
    """Verifier-only port; Authlib owns JOSE parsing and one unknown-kid refresh."""

    def __init__(
        self,
        *,
        config: MicrosoftOIDCAdapterConfig,
        client_factory: Callable[[], OpenIDMixin] | None = None,
    ) -> None:
        self._config = config
        self._client_factory = client_factory or (
            lambda: AuthlibOpenIDClient(config=config)
        )
        self._client: OpenIDMixin | None = None
        self._client_created_at: datetime | None = None
        self._lock = threading.Lock()

    def verify_id_token(
        self,
        raw_id_token: str,
        *,
        expected_nonce: str,
        now: datetime,
    ) -> VerifiedMicrosoftPrincipal:
        now = _aware_utc(now)
        if self._config.enabled is not True:
            raise OIDCAuthenticationFailed("federation_disabled")
        if not isinstance(raw_id_token, str) or not raw_id_token:
            raise OIDCAuthenticationFailed("raw_id_token_required")
        if len(raw_id_token.encode("utf-8")) > self._config.max_id_token_bytes:
            raise OIDCAuthenticationFailed("raw_id_token_oversized")
        if not isinstance(expected_nonce, str) or not _OPAQUE.fullmatch(expected_nonce):
            raise OIDCAuthenticationFailed("nonce_invalid")

        try:
            with self._lock:
                client = self._current_client(now)
                metadata = client.load_server_metadata()
                _validate_metadata(self._config, metadata)
                claims = client.parse_id_token(
                    {"id_token": raw_id_token},
                    nonce=expected_nonce,
                    claims_options={
                        "iss": {"essential": True, "values": [self._config.issuer]},
                        "aud": {"essential": True, "values": [self._config.client_id]},
                        "sub": {"essential": True},
                        "exp": {"essential": True},
                        "nbf": {"essential": True},
                        "iat": {"essential": True},
                    },
                    leeway=self._config.claim_leeway_seconds,
                )
        except OIDCAdapterError:
            raise
        except (JoseError, ValueError, TypeError, KeyError):
            raise OIDCAuthenticationFailed("id_token_verification_failed") from None
        except (requests.RequestException, RuntimeError):
            raise OIDCTemporarilyUnavailable("verifier_dependency_unavailable") from None
        except Exception:
            raise OIDCTemporarilyUnavailable("verifier_dependency_unavailable") from None

        if claims is None:
            raise OIDCAuthenticationFailed("id_token_verification_failed")
        tenant_id = claims.get("tid")
        object_id = claims.get("oid")
        subject = claims.get("sub")
        if not isinstance(tenant_id, str) or not hmac.compare_digest(
            tenant_id.lower(), self._config.tenant_id
        ):
            raise OIDCAuthenticationFailed("tenant_mismatch")
        if not _bounded_identifier(object_id) or not _bounded_identifier(subject):
            raise OIDCAuthenticationFailed("immutable_subject_required")
        return VerifiedMicrosoftPrincipal(
            tenant_id=self._config.tenant_id,
            object_id=object_id,
            subject=subject,
        )

    def _current_client(self, now: datetime) -> OpenIDMixin:
        if (
            self._client is None
            or self._client_created_at is None
            or now
            >= self._client_created_at
            + timedelta(seconds=self._config.verifier_client_max_age_seconds)
        ):
            if self._client is not None:
                close = getattr(self._client, "close", None)
                if callable(close):
                    close()
            self._client = self._client_factory()
            self._client_created_at = now
        return self._client


@dataclass(frozen=True)
class _ConsumedAttempt:
    flow: dict[str, Any]
    surface: Surface
    origin: str
    return_target: ReturnTarget
    attempt_reference: str


@dataclass(frozen=True)
class _StoredAttempt:
    ciphertext: bytes
    expires_at: datetime
    nonce_digest: str


class AuthorizationAttemptStore(Protocol):
    """Persistence port for one-use authorization attempts."""

    def store(
        self,
        *,
        flow: Mapping[str, Any],
        surface: Surface,
        origin: str,
        return_target: ReturnTarget,
        now: datetime,
        ttl_seconds: int,
    ) -> tuple[str, datetime]:
        raise NotImplementedError

    def consume(self, *, state: str, now: datetime) -> _ConsumedAttempt:
        raise NotImplementedError

    def discard(self, *, state: str) -> None:
        raise NotImplementedError


class EncryptedAuthorizationAttemptStore:
    """Bounded provider-free store; replaceable by a later authorised port."""

    def __init__(
        self,
        *,
        encryption_key: bytes,
        digest_key: bytes,
        max_attempts: int = MAX_ATTEMPTS,
    ) -> None:
        if len(digest_key) < 32:
            raise ValueError("attempt digest key must be at least 32 bytes")
        if not 1 <= max_attempts <= MAX_ATTEMPTS:
            raise ValueError("attempt store capacity exceeds the frozen bound")
        self._fernet = Fernet(encryption_key)
        self._digest_key = bytes(digest_key)
        self._max_attempts = max_attempts
        self._attempts: dict[str, _StoredAttempt] = {}
        self._lock = threading.Lock()

    def store(
        self,
        *,
        flow: Mapping[str, Any],
        surface: Surface,
        origin: str,
        return_target: ReturnTarget,
        now: datetime,
        ttl_seconds: int,
    ) -> tuple[str, datetime]:
        now = _aware_utc(now)
        normalized_flow = _validate_storable_flow(flow)
        state = normalized_flow["state"]
        nonce = normalized_flow["nonce"]
        expires_at = now + timedelta(seconds=ttl_seconds)
        payload = json.dumps(
            {
                "flow": normalized_flow,
                "surface": surface.value,
                "origin": origin,
                "return_target": return_target.value,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(payload) > 65_536:
            raise OIDCTemporarilyUnavailable("authorization_flow_oversized")
        ciphertext = self._fernet.encrypt(payload)
        state_digest = self._digest("state", state)
        nonce_digest = self._digest("nonce", nonce)
        with self._lock:
            self._purge_expired(now)
            if state_digest in self._attempts:
                raise OIDCTemporarilyUnavailable("authorization_state_collision")
            if len(self._attempts) >= self._max_attempts:
                raise OIDCTemporarilyUnavailable("authorization_attempt_capacity")
            self._attempts[state_digest] = _StoredAttempt(
                ciphertext=ciphertext,
                expires_at=expires_at,
                nonce_digest=nonce_digest,
            )
        return self._reference(state_digest), expires_at

    def consume(self, *, state: str, now: datetime) -> _ConsumedAttempt:
        now = _aware_utc(now)
        if not isinstance(state, str) or not _OPAQUE.fullmatch(state):
            raise OIDCAuthenticationFailed("state_invalid")
        state_digest = self._digest("state", state)
        with self._lock:
            stored = self._attempts.get(state_digest)
            if stored is None:
                raise OIDCAuthenticationFailed("authorization_attempt_required")
            if now >= stored.expires_at:
                self._attempts.pop(state_digest, None)
                raise OIDCAuthenticationFailed("authorization_attempt_expired")
            self._attempts.pop(state_digest, None)
        try:
            payload = json.loads(self._fernet.decrypt(stored.ciphertext))
            flow = _validate_storable_flow(payload["flow"])
            surface = Surface(payload["surface"])
            origin = _canonical_https_origin(payload["origin"])
            return_target = ReturnTarget(payload["return_target"])
        except (InvalidToken, KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable") from None
        if not hmac.compare_digest(flow["state"], state):
            raise OIDCAuthenticationFailed("state_mismatch")
        if not hmac.compare_digest(
            stored.nonce_digest, self._digest("nonce", flow["nonce"])
        ):
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
        return _ConsumedAttempt(
            flow=flow,
            surface=surface,
            origin=origin,
            return_target=return_target,
            attempt_reference=self._reference(state_digest),
        )

    def discard(self, *, state: str) -> None:
        if isinstance(state, str):
            state_digest = self._digest("state", state)
            with self._lock:
                self._attempts.pop(state_digest, None)

    @property
    def active_count(self) -> int:
        with self._lock:
            return len(self._attempts)

    def _purge_expired(self, now: datetime) -> None:
        expired = [
            digest
            for digest, record in self._attempts.items()
            if now >= record.expires_at
        ]
        for digest in expired:
            self._attempts.pop(digest, None)

    def _digest(self, label: str, value: str) -> str:
        material = f"{label}\x00{value}".encode("utf-8")
        return hmac.new(self._digest_key, material, hashlib.sha256).hexdigest()

    @staticmethod
    def _reference(digest: str) -> str:
        return f"hmac-sha256:{digest}"


class TwoComponentOIDCAdapter:
    """Orchestrate one stored MSAL flow and one Authlib verification."""

    def __init__(
        self,
        *,
        config: MicrosoftOIDCAdapterConfig,
        protocol_client: MSALAuthorizationCodePort,
        verifier: IDTokenVerifierPort,
        attempt_store: AuthorizationAttemptStore,
        audit_sink: OIDCAdapterAuditSink,
    ) -> None:
        self._config = config
        self._protocol_client = protocol_client
        self._verifier = verifier
        self._attempt_store = attempt_store
        self._audit_sink = audit_sink

    def create_authorization_flow(
        self,
        *,
        surface: Surface,
        return_target: ReturnTarget,
        now: datetime,
    ) -> AuthorizationStart:
        now = _aware_utc(now)
        surface = Surface(surface)
        return_target = ReturnTarget(return_target)
        if self._config.enabled is not True:
            error = OIDCAuthenticationFailed("federation_disabled")
            self._record(
                now=now,
                event_type="oidc.authorization_start",
                decision="deny",
                reason_code=error.reason_code,
                surface=surface,
                return_target=return_target,
            )
            raise error

        state: str | None = None
        try:
            flow = dict(self._protocol_client.create_authorization_flow())
            normalized_flow = _validate_authorization_flow(self._config, flow)
            state = normalized_flow["state"]
            attempt_reference, expires_at = self._attempt_store.store(
                flow=normalized_flow,
                surface=surface,
                origin=self._config.surface_origins[surface],
                return_target=return_target,
                now=now,
                ttl_seconds=self._config.attempt_ttl_seconds,
            )
        except OIDCAdapterError as error:
            self._record(
                now=now,
                event_type="oidc.authorization_start",
                decision="error" if error.http_status == 503 else "deny",
                reason_code=error.reason_code,
                surface=surface,
                return_target=return_target,
            )
            raise
        except Exception:
            error = OIDCTemporarilyUnavailable("protocol_client_unavailable")
            self._record(
                now=now,
                event_type="oidc.authorization_start",
                decision="error",
                reason_code=error.reason_code,
                surface=surface,
                return_target=return_target,
            )
            raise error from None

        try:
            self._record(
                now=now,
                event_type="oidc.authorization_start",
                decision="allow",
                reason_code="authorization_attempt_created",
                attempt_reference=attempt_reference,
                surface=surface,
                return_target=return_target,
            )
        except OIDCTemporarilyUnavailable:
            if state is None:
                raise OIDCTemporarilyUnavailable(
                    "authorization_attempt_cleanup_failed"
                ) from None
            self._attempt_store.discard(state=state)
            raise
        return AuthorizationStart(
            status="authorization_required",
            authorization_uri=normalized_flow["auth_uri"],
            attempt_expires_at=expires_at,
        )

    def complete_authorization_flow(
        self,
        *,
        auth_response: Mapping[str, str],
        now: datetime,
    ) -> CompletedAuthorization:
        now = _aware_utc(now)
        if self._config.enabled is not True:
            error = OIDCAuthenticationFailed("federation_disabled")
            self._record(
                now=now,
                event_type="oidc.authorization_complete",
                decision="deny",
                reason_code=error.reason_code,
            )
            raise error
        try:
            normalized_response = _validate_callback_response(auth_response)
        except OIDCAuthenticationFailed as error:
            self._record(
                now=now,
                event_type="oidc.authorization_complete",
                decision="deny",
                reason_code=error.reason_code,
            )
            raise
        state = normalized_response["state"]
        try:
            attempt = self._attempt_store.consume(state=state, now=now)
        except OIDCAdapterError as error:
            self._record(
                now=now,
                event_type="oidc.authorization_complete",
                decision="error" if error.http_status == 503 else "deny",
                reason_code=error.reason_code,
            )
            raise

        if "error" in normalized_response:
            error = OIDCAuthenticationFailed("provider_authorization_denied")
            self._record_failure(
                now,
                attempt,
                error,
                token_exchange_attempted=False,
            )
            raise error

        token_exchange_attempted = False
        token_result: dict[str, Any] | None = None
        try:
            token_exchange_attempted = True
            token_result = dict(
                self._protocol_client.redeem_authorization_flow(
                    attempt.flow,
                    normalized_response,
                )
            )
            if token_result.get("error"):
                raise OIDCAuthenticationFailed("token_exchange_rejected")
            raw_id_token = token_result.get("id_token")
            if not isinstance(raw_id_token, str) or not raw_id_token:
                raise OIDCAuthenticationFailed("raw_id_token_required")
            principal = self._verifier.verify_id_token(
                raw_id_token,
                expected_nonce=attempt.flow["nonce"],
                now=now,
            )
            if (
                not isinstance(principal, VerifiedMicrosoftPrincipal)
                or principal.verified_source != VERIFIED_SOURCE
                or principal.tenant_id != self._config.tenant_id
                or principal.authorization_granted
                or principal.session_created
            ):
                raise OIDCAuthenticationFailed("verified_principal_invalid")
        except OIDCAdapterError as error:
            self._record_failure(
                now,
                attempt,
                error,
                token_exchange_attempted=token_exchange_attempted,
            )
            raise
        except Exception:
            error = OIDCTemporarilyUnavailable("protocol_client_unavailable")
            self._record_failure(
                now,
                attempt,
                error,
                token_exchange_attempted=token_exchange_attempted,
            )
            raise error from None
        finally:
            if token_result is not None:
                token_result.clear()

        self._record(
            now=now,
            event_type="oidc.authorization_complete",
            decision="allow",
            reason_code="id_token_verified",
            attempt_reference=attempt.attempt_reference,
            surface=attempt.surface,
            return_target=attempt.return_target,
            token_exchange_attempted=token_exchange_attempted,
            principal_released=True,
        )
        return CompletedAuthorization(
            principal=principal,
            surface=attempt.surface,
            origin=attempt.origin,
            return_target=attempt.return_target,
        )

    def _record_failure(
        self,
        now: datetime,
        attempt: _ConsumedAttempt,
        error: OIDCAdapterError,
        *,
        token_exchange_attempted: bool,
    ) -> None:
        self._record(
            now=now,
            event_type="oidc.authorization_complete",
            decision="error" if error.http_status == 503 else "deny",
            reason_code=error.reason_code,
            attempt_reference=attempt.attempt_reference,
            surface=attempt.surface,
            return_target=attempt.return_target,
            token_exchange_attempted=token_exchange_attempted,
        )

    def _record(
        self,
        *,
        now: datetime,
        event_type: str,
        decision: str,
        reason_code: str,
        attempt_reference: str | None = None,
        surface: Surface | None = None,
        return_target: ReturnTarget | None = None,
        token_exchange_attempted: bool = False,
        principal_released: bool = False,
    ) -> None:
        try:
            self._audit_sink.record(
                OIDCAdapterAuditEvent(
                    occurred_at=now,
                    event_type=event_type,
                    decision=decision,
                    reason_code=reason_code,
                    attempt_reference=attempt_reference,
                    surface=surface.value if surface is not None else None,
                    return_target=(
                        return_target.value if return_target is not None else None
                    ),
                    token_exchange_attempted=token_exchange_attempted,
                    principal_released=principal_released,
                )
            )
        except Exception:
            raise OIDCTemporarilyUnavailable("required_audit_unavailable") from None


def _validate_authorization_flow(
    config: MicrosoftOIDCAdapterConfig,
    flow: Mapping[str, Any],
) -> dict[str, Any]:
    normalized = _validate_storable_flow(flow)
    parsed = urlsplit(normalized["auth_uri"])
    expected_path = f"/{config.tenant_id}/oauth2/v2.0/authorize"
    if (
        parsed.scheme != "https"
        or parsed.hostname != _MICROSOFT_HOST
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != expected_path
        or parsed.fragment
    ):
        raise OIDCTemporarilyUnavailable("authorization_uri_mismatch")
    query = parse_qs(parsed.query, keep_blank_values=True)
    expected_query_keys = {
        "client_id",
        "response_type",
        "redirect_uri",
        "scope",
        "state",
        "response_mode",
        "code_challenge",
        "code_challenge_method",
        "nonce",
        "client_info",
    }
    if set(query) != expected_query_keys:
        raise OIDCTemporarilyUnavailable("authorization_flow_mismatch")
    required = {
        "client_id": config.client_id,
        "response_type": "code",
        "redirect_uri": config.redirect_uri,
        "state": normalized["state"],
        "response_mode": "form_post",
        "code_challenge_method": PKCE_METHOD,
        "nonce": hashlib.sha256(normalized["nonce"].encode("ascii")).hexdigest(),
        "client_info": "1",
    }
    if any(query.get(key) != [value] for key, value in required.items()):
        raise OIDCTemporarilyUnavailable("authorization_flow_mismatch")
    if set(query.get("scope", [""])[0].split()) != {"openid", "profile"}:
        raise OIDCTemporarilyUnavailable("authorization_scope_mismatch")
    expected_challenge = _pkce_s256(normalized["code_verifier"])
    challenge = query.get("code_challenge", [""])
    if challenge != [expected_challenge]:
        raise OIDCTemporarilyUnavailable("pkce_challenge_invalid")
    if any(
        forbidden in query.get("scope", [""])[0].split()
        for forbidden in ("offline_access", "email")
    ):
        raise OIDCTemporarilyUnavailable("authorization_scope_mismatch")
    return normalized


def _validate_storable_flow(flow: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(flow, Mapping):
        raise OIDCTemporarilyUnavailable("authorization_flow_invalid")
    normalized = dict(flow)
    expected_keys = {
        "state",
        "redirect_uri",
        "scope",
        "auth_uri",
        "code_verifier",
        "nonce",
        "claims_challenge",
    }
    if set(normalized) != expected_keys:
        raise OIDCTemporarilyUnavailable("authorization_flow_invalid")
    for key in ("auth_uri", "state", "nonce", "code_verifier"):
        value = normalized.get(key)
        if not isinstance(value, str) or not value:
            raise OIDCTemporarilyUnavailable("authorization_flow_invalid")
    if not _OPAQUE.fullmatch(normalized["state"]):
        raise OIDCTemporarilyUnavailable("authorization_state_invalid")
    if not _OPAQUE.fullmatch(normalized["nonce"]):
        raise OIDCTemporarilyUnavailable("authorization_nonce_invalid")
    if not _OPAQUE.fullmatch(normalized["code_verifier"]):
        raise OIDCTemporarilyUnavailable("pkce_verifier_invalid")
    if len(normalized["auth_uri"].encode("utf-8")) > 8192:
        raise OIDCTemporarilyUnavailable("authorization_flow_oversized")
    if not isinstance(normalized["redirect_uri"], str):
        raise OIDCTemporarilyUnavailable("authorization_flow_invalid")
    if (
        not isinstance(normalized["scope"], list)
        or set(normalized["scope"]) != {"openid", "profile"}
        or len(normalized["scope"]) != 2
        or normalized["claims_challenge"] is not None
    ):
        raise OIDCTemporarilyUnavailable("authorization_flow_invalid")
    return normalized


def _validate_callback_response(response: Mapping[str, str]) -> dict[str, str]:
    if not isinstance(response, Mapping) or not response:
        raise OIDCAuthenticationFailed("callback_response_invalid")
    if not set(response).issubset(_ALLOWED_CALLBACK_KEYS):
        raise OIDCAuthenticationFailed("callback_response_invalid")
    normalized: dict[str, str] = {}
    bounds = {"state": 256, "code": 8192, "error": 128, "error_description": 1024}
    for key, value in response.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise OIDCAuthenticationFailed("callback_response_invalid")
        if not value or len(value.encode("utf-8")) > bounds[key]:
            raise OIDCAuthenticationFailed("callback_response_invalid")
        normalized[key] = value
    if "state" not in normalized or not _OPAQUE.fullmatch(normalized["state"]):
        raise OIDCAuthenticationFailed("state_invalid")
    has_code = "code" in normalized
    has_error = "error" in normalized
    if has_code == has_error or ("error_description" in normalized and not has_error):
        raise OIDCAuthenticationFailed("callback_response_invalid")
    return normalized


def _validate_metadata(config: MicrosoftOIDCAdapterConfig, metadata: Any) -> None:
    if not isinstance(metadata, Mapping):
        raise OIDCTemporarilyUnavailable("metadata_invalid")
    exact = {
        "issuer": config.issuer,
        "authorization_endpoint": f"{config.authority}/oauth2/v2.0/authorize",
        "token_endpoint": f"{config.authority}/oauth2/v2.0/token",
        "jwks_uri": config.jwks_uri,
    }
    if any(metadata.get(key) != value for key, value in exact.items()):
        raise OIDCTemporarilyUnavailable("metadata_mismatch")
    if metadata.get("id_token_signing_alg_values_supported") != ["RS256"]:
        raise OIDCTemporarilyUnavailable("metadata_algorithm_mismatch")


def _canonical_guid(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not _GUID.fullmatch(value.lower()):
        raise ValueError(f"{field_name} must be a canonical UUID-shaped value")
    if value != value.lower():
        raise ValueError(f"{field_name} must be lowercase canonical form")
    return value


def _canonical_callback_uri(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port is not None
        or parsed.path != _CALLBACK_PATH
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("callback URI is invalid")
    return f"https://{parsed.hostname}{_CALLBACK_PATH}"


def _canonical_https_origin(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("surface origin must be a canonical HTTPS origin")
    host = parsed.hostname
    port = f":{parsed.port}" if parsed.port is not None else ""
    canonical = f"https://{host}{port}"
    if value != canonical:
        raise ValueError("surface origin must not include a path or trailing slash")
    return canonical


def _aware_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone-aware clock required")
    return value.astimezone(timezone.utc)


def _bounded_identifier(value: Any) -> bool:
    return isinstance(value, str) and 1 <= len(value.encode("utf-8")) <= 256


def _pkce_s256(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


__all__ = [
    "ATTEMPT_TTL_SECONDS",
    "AUTHORITY_MODE",
    "CLAIM_LEEWAY_SECONDS",
    "MAX_ID_TOKEN_BYTES",
    "MAX_VERIFIER_CLIENT_AGE_SECONDS",
    "PKCE_METHOD",
    "PROVIDER",
    "VERIFIED_SOURCE",
    "AuthlibIDTokenVerifier",
    "AuthlibOpenIDClient",
    "AuthorizationAttemptStore",
    "AuthorizationStart",
    "CompletedAuthorization",
    "EncryptedAuthorizationAttemptStore",
    "InMemoryOIDCAdapterAuditSink",
    "MSALAuthorizationCodeClient",
    "MicrosoftOIDCAdapterConfig",
    "OIDCAdapterAuditEvent",
    "OIDCAdapterAuditUnavailable",
    "OIDCAdapterError",
    "OIDCAuthenticationFailed",
    "OIDCTemporarilyUnavailable",
    "ReturnTarget",
    "Surface",
    "TwoComponentOIDCAdapter",
    "VerifiedMicrosoftPrincipal",
]
