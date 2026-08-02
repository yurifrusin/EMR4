"""Provider-free PostgreSQL authorization-attempt-store implementation."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Protocol

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.application_identity_oidc_attempt import (
    ApplicationIdentityOIDCAuthorizationAttempt,
)
from app.services.application_identity_oidc_adapter import (
    ATTEMPT_TTL_SECONDS,
    MAX_ATTEMPTS,
    OIDCAdapterError,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    ReturnTarget,
    Surface,
    _canonical_https_origin,
    _ConsumedAttempt,
    _OPAQUE,
    _validate_storable_flow,
)
from app.services.application_identity_oidc_attempt_database_role import (
    require_oidc_attempt_runtime_role_identifier,
)


ENVELOPE_VERSION = "oidc-authorization-attempt-envelope.v1"
MAX_ENVELOPE_PLAINTEXT_BYTES = 65_536
MAX_ENVELOPE_CIPHERTEXT_BYTES = 131_072
MAX_RETAINED_KEYS = 4
CAPACITY_ADVISORY_LOCK_KEY = 5_276_462_801_106_285_119

_KEY_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")


@dataclass(frozen=True)
class EncryptedAuthorizationAttemptEnvelope:
    key_id: str
    ciphertext: bytes


class AuthorizationAttemptCipher(Protocol):
    def encrypt(self, plaintext: bytes) -> EncryptedAuthorizationAttemptEnvelope:
        raise NotImplementedError

    def decrypt(self, *, key_id: str, ciphertext: bytes) -> bytes:
        raise NotImplementedError


class FernetAuthorizationAttemptCipher:
    """Bounded active-plus-retained authenticated-encryption keyring."""

    def __init__(self, *, active_key_id: str, keys: Mapping[str, bytes]) -> None:
        normalized = _validated_key_mapping(active_key_id=active_key_id, keys=keys)
        try:
            self._fernets = {
                key_id: Fernet(key_material)
                for key_id, key_material in normalized.items()
            }
        except (TypeError, ValueError):
            raise ValueError("invalid Fernet authorization-attempt key") from None
        self._active_key_id = active_key_id

    @property
    def active_key_id(self) -> str:
        return self._active_key_id

    def encrypt(self, plaintext: bytes) -> EncryptedAuthorizationAttemptEnvelope:
        if not isinstance(plaintext, bytes) or not plaintext:
            raise ValueError("authorization-attempt plaintext must be nonempty bytes")
        if len(plaintext) > MAX_ENVELOPE_PLAINTEXT_BYTES:
            raise OIDCTemporarilyUnavailable("authorization_flow_oversized")
        ciphertext = self._fernets[self._active_key_id].encrypt(plaintext)
        if len(ciphertext) > MAX_ENVELOPE_CIPHERTEXT_BYTES:
            raise OIDCTemporarilyUnavailable("authorization_flow_oversized")
        return EncryptedAuthorizationAttemptEnvelope(
            key_id=self._active_key_id,
            ciphertext=ciphertext,
        )

    def decrypt(self, *, key_id: str, ciphertext: bytes) -> bytes:
        fernet = self._fernets.get(key_id)
        if fernet is None:
            raise OIDCTemporarilyUnavailable("authorization_attempt_key_unavailable")
        if (
            not isinstance(ciphertext, bytes)
            or not ciphertext
            or len(ciphertext) > MAX_ENVELOPE_CIPHERTEXT_BYTES
        ):
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
        try:
            plaintext = fernet.decrypt(ciphertext)
        except InvalidToken:
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable") from None
        if not plaintext or len(plaintext) > MAX_ENVELOPE_PLAINTEXT_BYTES:
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
        return plaintext


class AuthorizationAttemptDigestKeyring:
    """Versioned domain-separated lookup references for state and nonce."""

    def __init__(self, *, active_key_id: str, keys: Mapping[str, bytes]) -> None:
        normalized = _validated_key_mapping(active_key_id=active_key_id, keys=keys)
        if any(len(key_material) < 32 for key_material in normalized.values()):
            raise ValueError("authorization-attempt digest keys require 32 bytes")
        self._active_key_id = active_key_id
        self._keys = normalized
        self._lookup_order = (
            active_key_id,
            *sorted(key_id for key_id in normalized if key_id != active_key_id),
        )

    def active_reference(self, *, label: str, value: str) -> str:
        return self._reference(self._active_key_id, label=label, value=value)

    def lookup_references(self, *, label: str, value: str) -> tuple[str, ...]:
        return tuple(
            self._reference(key_id, label=label, value=value)
            for key_id in self._lookup_order
        )

    def _reference(self, key_id: str, *, label: str, value: str) -> str:
        if label not in {"state", "nonce"}:
            raise ValueError("authorization-attempt digest label is invalid")
        if not isinstance(value, str) or not value:
            raise ValueError("authorization-attempt digest value is invalid")
        material = f"{label}\x00{value}".encode("utf-8")
        digest = hmac.new(self._keys[key_id], material, hashlib.sha256).hexdigest()
        return f"hmac-sha256:{key_id}:{digest}"


class PostgresAuthorizationAttemptStore:
    """Durable one-use implementation of the accepted attempt-store port."""

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        cipher: AuthorizationAttemptCipher,
        digest_keyring: AuthorizationAttemptDigestKeyring,
        max_attempts: int = MAX_ATTEMPTS,
    ) -> None:
        if not callable(session_factory):
            raise TypeError("authorization-attempt session factory must be callable")
        if not 1 <= max_attempts <= MAX_ATTEMPTS:
            raise ValueError("authorization-attempt capacity exceeds frozen bound")
        self._session_factory = session_factory
        self._cipher = cipher
        self._digest_keyring = digest_keyring
        self._max_attempts = max_attempts

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
        if ttl_seconds != ATTEMPT_TTL_SECONDS:
            raise OIDCTemporarilyUnavailable("authorization_attempt_expiry_invalid")
        normalized_flow = _validate_storable_flow(flow)
        surface = Surface(surface)
        origin = _canonical_https_origin(origin)
        return_target = ReturnTarget(return_target)
        expires_at = now + timedelta(seconds=ATTEMPT_TTL_SECONDS)
        state = normalized_flow["state"]
        nonce = normalized_flow["nonce"]
        state_reference = self._digest_keyring.active_reference(
            label="state", value=state
        )
        nonce_reference = self._digest_keyring.active_reference(
            label="nonce", value=nonce
        )
        state_candidates = self._digest_keyring.lookup_references(
            label="state", value=state
        )
        nonce_candidates = self._digest_keyring.lookup_references(
            label="nonce", value=nonce
        )
        plaintext = _encode_envelope(
            flow=normalized_flow,
            surface=surface,
            origin=origin,
            return_target=return_target,
            state_reference=state_reference,
            nonce_reference=nonce_reference,
            created_at=now,
            expires_at=expires_at,
        )
        encrypted = self._cipher.encrypt(plaintext)
        row = ApplicationIdentityOIDCAuthorizationAttempt(
            state_reference_hmac=state_reference,
            nonce_reference_hmac=nonce_reference,
            cipher_key_id=encrypted.key_id,
            ciphertext=encrypted.ciphertext,
            envelope_version=ENVELOPE_VERSION,
            created_at=now,
            expires_at=expires_at,
            data_class="authored_synthetic",
        )
        try:
            with self._session_factory() as session:
                with session.begin():
                    _require_capability_role(session)
                    session.execute(
                        text("SELECT pg_advisory_xact_lock(:lock_key)"),
                        {"lock_key": CAPACITY_ADVISORY_LOCK_KEY},
                    )
                    session.execute(
                        delete(ApplicationIdentityOIDCAuthorizationAttempt).where(
                            ApplicationIdentityOIDCAuthorizationAttempt.expires_at
                            <= now
                        )
                    )
                    collision_count = int(
                        session.execute(
                            select(func.count())
                            .select_from(ApplicationIdentityOIDCAuthorizationAttempt)
                            .where(
                                or_(
                                    ApplicationIdentityOIDCAuthorizationAttempt.state_reference_hmac.in_(
                                        state_candidates
                                    ),
                                    ApplicationIdentityOIDCAuthorizationAttempt.nonce_reference_hmac.in_(
                                        nonce_candidates
                                    ),
                                )
                            )
                        ).scalar_one()
                    )
                    if collision_count:
                        raise OIDCTemporarilyUnavailable(
                            "authorization_state_collision"
                        )
                    active_count = int(
                        session.execute(
                            select(func.count()).select_from(
                                ApplicationIdentityOIDCAuthorizationAttempt
                            )
                        ).scalar_one()
                    )
                    if active_count >= self._max_attempts:
                        raise OIDCTemporarilyUnavailable(
                            "authorization_attempt_capacity"
                        )
                    session.add(row)
        except OIDCAdapterError:
            raise
        except IntegrityError:
            raise OIDCTemporarilyUnavailable(
                "authorization_state_collision"
            ) from None
        except SQLAlchemyError:
            raise OIDCTemporarilyUnavailable(
                "authorization_attempt_store_unavailable"
            ) from None
        return state_reference, expires_at

    def consume(self, *, state: str, now: datetime) -> _ConsumedAttempt:
        now = _aware_utc(now)
        if not isinstance(state, str) or not _OPAQUE.fullmatch(state):
            raise OIDCAuthenticationFailed("state_invalid")
        state_candidates = self._digest_keyring.lookup_references(
            label="state", value=state
        )
        rows: list[Mapping[str, Any]]
        try:
            with self._session_factory() as session:
                with session.begin():
                    _require_capability_role(session)
                    statement = (
                        delete(ApplicationIdentityOIDCAuthorizationAttempt)
                        .where(
                            ApplicationIdentityOIDCAuthorizationAttempt.state_reference_hmac.in_(
                                state_candidates
                            )
                        )
                        .returning(
                            ApplicationIdentityOIDCAuthorizationAttempt.state_reference_hmac,
                            ApplicationIdentityOIDCAuthorizationAttempt.nonce_reference_hmac,
                            ApplicationIdentityOIDCAuthorizationAttempt.cipher_key_id,
                            ApplicationIdentityOIDCAuthorizationAttempt.ciphertext,
                            ApplicationIdentityOIDCAuthorizationAttempt.envelope_version,
                            ApplicationIdentityOIDCAuthorizationAttempt.created_at,
                            ApplicationIdentityOIDCAuthorizationAttempt.expires_at,
                            ApplicationIdentityOIDCAuthorizationAttempt.data_class,
                        )
                    )
                    rows = list(session.execute(statement).mappings().all())
        except SQLAlchemyError:
            raise OIDCTemporarilyUnavailable(
                "authorization_attempt_store_unavailable"
            ) from None
        if not rows:
            raise OIDCAuthenticationFailed("authorization_attempt_required")
        if len(rows) != 1:
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
        row = rows[0]
        expires_at = _aware_utc(row["expires_at"])
        if now >= expires_at:
            raise OIDCAuthenticationFailed("authorization_attempt_expired")
        if (
            row["envelope_version"] != ENVELOPE_VERSION
            or row["data_class"] != "authored_synthetic"
        ):
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
        plaintext = self._cipher.decrypt(
            key_id=row["cipher_key_id"],
            ciphertext=bytes(row["ciphertext"]),
        )
        try:
            payload = _decode_envelope(plaintext)
            flow = _validate_storable_flow(payload["flow"])
            surface = Surface(payload["surface"])
            origin = _canonical_https_origin(payload["origin"])
            return_target = ReturnTarget(payload["return_target"])
        except (OIDCAdapterError, KeyError, TypeError, ValueError):
            raise OIDCTemporarilyUnavailable(
                "authorization_attempt_unreadable"
            ) from None
        if not hmac.compare_digest(flow["state"], state):
            raise OIDCAuthenticationFailed("state_mismatch")
        expected_nonce_references = self._digest_keyring.lookup_references(
            label="nonce", value=flow["nonce"]
        )
        checks = (
            _constant_equal(payload["state_reference_hmac"], row["state_reference_hmac"]),
            _constant_equal(payload["nonce_reference_hmac"], row["nonce_reference_hmac"]),
            row["state_reference_hmac"] in state_candidates,
            row["nonce_reference_hmac"] in expected_nonce_references,
            payload["envelope_version"] == ENVELOPE_VERSION,
            _parse_timestamp(payload["created_at"]) == _aware_utc(row["created_at"]),
            _parse_timestamp(payload["expires_at"]) == expires_at,
        )
        if not all(checks):
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
        return _ConsumedAttempt(
            flow=flow,
            surface=surface,
            origin=origin,
            return_target=return_target,
            attempt_reference=row["state_reference_hmac"],
        )

    def discard(self, *, state: str) -> None:
        if not isinstance(state, str) or not _OPAQUE.fullmatch(state):
            return
        candidates = self._digest_keyring.lookup_references(
            label="state", value=state
        )
        try:
            with self._session_factory() as session:
                with session.begin():
                    _require_capability_role(session)
                    session.execute(
                        delete(ApplicationIdentityOIDCAuthorizationAttempt).where(
                            ApplicationIdentityOIDCAuthorizationAttempt.state_reference_hmac.in_(
                                candidates
                            )
                        )
                    )
        except SQLAlchemyError:
            raise OIDCTemporarilyUnavailable(
                "authorization_attempt_store_unavailable"
            ) from None

    def active_count(self, *, now: datetime) -> int:
        now = _aware_utc(now)
        try:
            with self._session_factory() as session:
                _require_capability_role(session)
                return int(
                    session.execute(
                        select(func.count())
                        .select_from(ApplicationIdentityOIDCAuthorizationAttempt)
                        .where(
                            ApplicationIdentityOIDCAuthorizationAttempt.expires_at
                            > now
                        )
                    ).scalar_one()
                )
        except SQLAlchemyError:
            raise OIDCTemporarilyUnavailable(
                "authorization_attempt_store_unavailable"
            ) from None


def _validated_key_mapping(
    *, active_key_id: str, keys: Mapping[str, bytes]
) -> dict[str, bytes]:
    if not isinstance(active_key_id, str) or not _KEY_ID.fullmatch(active_key_id):
        raise ValueError("authorization-attempt active key identifier is invalid")
    if not isinstance(keys, Mapping) or not 1 <= len(keys) <= MAX_RETAINED_KEYS:
        raise ValueError("authorization-attempt keyring must contain one to four keys")
    normalized: dict[str, bytes] = {}
    for key_id, key_material in keys.items():
        if not isinstance(key_id, str) or not _KEY_ID.fullmatch(key_id):
            raise ValueError("authorization-attempt key identifier is invalid")
        if not isinstance(key_material, bytes):
            raise TypeError("authorization-attempt key material must be bytes")
        normalized[key_id] = bytes(key_material)
    if active_key_id not in normalized:
        raise ValueError("authorization-attempt active key is absent")
    return normalized


def _encode_envelope(
    *,
    flow: Mapping[str, Any],
    surface: Surface,
    origin: str,
    return_target: ReturnTarget,
    state_reference: str,
    nonce_reference: str,
    created_at: datetime,
    expires_at: datetime,
) -> bytes:
    payload = {
        "envelope_version": ENVELOPE_VERSION,
        "flow": dict(flow),
        "surface": surface.value,
        "origin": origin,
        "return_target": return_target.value,
        "state_reference_hmac": state_reference,
        "nonce_reference_hmac": nonce_reference,
        "created_at": _format_timestamp(created_at),
        "expires_at": _format_timestamp(expires_at),
    }
    rendered = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    if len(rendered) > MAX_ENVELOPE_PLAINTEXT_BYTES:
        raise OIDCTemporarilyUnavailable("authorization_flow_oversized")
    return rendered


def _decode_envelope(plaintext: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(plaintext)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError):
        raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable") from None
    expected = {
        "envelope_version",
        "flow",
        "surface",
        "origin",
        "return_target",
        "state_reference_hmac",
        "nonce_reference_hmac",
        "created_at",
        "expires_at",
    }
    if not isinstance(payload, dict) or set(payload) != expected:
        raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
    for key in (
        "envelope_version",
        "surface",
        "origin",
        "return_target",
        "state_reference_hmac",
        "nonce_reference_hmac",
        "created_at",
        "expires_at",
    ):
        if not isinstance(payload[key], str):
            raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable")
    return payload


def _require_capability_role(session: Session) -> str:
    try:
        current_role = session.execute(text("SELECT current_user")).scalar_one()
        return require_oidc_attempt_runtime_role_identifier(current_role)
    except (SQLAlchemyError, ValueError):
        raise OIDCTemporarilyUnavailable("authorization_attempt_role_required") from None


def _aware_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timezone-aware authorization-attempt clock required")
    return value.astimezone(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    return _aware_utc(value).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    try:
        return _aware_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except (AttributeError, TypeError, ValueError):
        raise OIDCTemporarilyUnavailable("authorization_attempt_unreadable") from None


def _constant_equal(left: Any, right: Any) -> bool:
    return isinstance(left, str) and isinstance(right, str) and hmac.compare_digest(
        left, right
    )


__all__ = [
    "AuthorizationAttemptCipher",
    "AuthorizationAttemptDigestKeyring",
    "CAPACITY_ADVISORY_LOCK_KEY",
    "ENVELOPE_VERSION",
    "EncryptedAuthorizationAttemptEnvelope",
    "FernetAuthorizationAttemptCipher",
    "PostgresAuthorizationAttemptStore",
]
