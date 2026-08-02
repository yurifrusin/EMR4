"""Route-free shared application-authentication runtime foundation.

This module is intentionally unmounted and persistence-free.  It implements
only the authored-synthetic server-side primitives accepted by the Raisa
shared-authentication architecture.  A future route, cookie, database or
external-identity adapter requires a separate authority and threat review.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import RLock
from typing import Callable, Mapping, Protocol, Sequence
from urllib.parse import urlsplit


AUTHORED_SYNTHETIC_DATA_CLASS = "authored_synthetic"
SURFACE_AUDIENCE = "emr4-api"
EXCHANGE_AUDIENCE = "emr4-session-exchange"
POLICY_VERSION = "clinician-workspace-read.v1"
PRACTITIONER_DIRECTORY_POLICY_VERSION = (
    "practice-practitioner-directory-read.v1"
)
PRACTITIONER_DIRECTORY_ACTION = "practice.practitioner-directory.read"
PRACTITIONER_DIRECTORY_RESOURCE_TYPE = "practitioner_directory"
MAX_PARENT_TTL = timedelta(hours=8)
MAX_IDLE_TTL = timedelta(minutes=30)
MAX_EXCHANGE_TTL = timedelta(seconds=60)

_SYNTHETIC_REFERENCE = re.compile(r"^synthetic-[a-z0-9-]{1,64}$")
_CORRELATION_ID = re.compile(r"^correlation-[a-z0-9-]{1,64}$")
_PKCE_VALUE = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")
_PKCE_CHALLENGE = re.compile(r"^[A-Za-z0-9_-]{43}$")
_BACKEND_ROLES = {"GP", "Receptionist", "Nurse", "Admin", "PracticeOwner"}
_REVOCATION_REASONS = {
    "logout_everywhere",
    "user_deactivated",
    "role_changed",
    "practice_changed",
    "practitioner_link_changed",
    "security_reset",
}


class Surface(str, Enum):
    WORD_DESKTOP = "word_desktop"
    WORD_ONLINE = "word_online"
    NATIVE_DIARY = "native_diary"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class AuthAuditEventType(str, Enum):
    SESSION_CREATED = "auth.session_created"
    SESSION_REFRESHED = "auth.session_refreshed"
    SESSION_REVOKED = "auth.session_revoked"
    SURFACE_BOUND = "auth.surface_bound"
    EXCHANGE_ISSUED = "auth.exchange_issued"
    EXCHANGE_REDEEMED = "auth.exchange_redeemed"
    EXCHANGE_REJECTED = "auth.exchange_rejected"
    AUTHORIZATION_ALLOWED = "auth.authorization_allowed"
    AUTHORIZATION_DENIED = "auth.authorization_denied"


class AuthAuditDecision(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    RECORDED = "recorded"


class AuthRuntimeDenied(RuntimeError):
    """Fail-closed typed denial whose message never includes supplied secrets."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(f"application authentication denied: {reason_code}")


class RequiredAuditUnavailable(AuthRuntimeDenied):
    def __init__(self) -> None:
        super().__init__("required_audit_unavailable")


@dataclass(frozen=True)
class SyntheticPrincipal:
    user_id: str
    practice_id: str
    current_backend_role: str
    practitioner_id: str | None

    def __post_init__(self) -> None:
        _require_synthetic_reference(self.user_id, "user_id")
        _require_synthetic_reference(self.practice_id, "practice_id")
        if self.practitioner_id is not None:
            _require_synthetic_reference(self.practitioner_id, "practitioner_id")
        if self.current_backend_role not in _BACKEND_ROLES:
            raise ValueError("current_backend_role must be a known backend role")


@dataclass(frozen=True)
class ParentSessionRecord:
    session_reference_hash: str
    principal: SyntheticPrincipal
    generation: int
    status: SessionStatus
    created_at: datetime
    last_observed_at: datetime
    idle_expires_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class SurfaceSessionRecord:
    surface_reference_hash: str
    parent_session_reference_hash: str
    surface: Surface
    origin: str
    audience: str
    parent_generation: int
    status: SessionStatus
    created_at: datetime
    last_observed_at: datetime
    idle_expires_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class ExchangeGrantRecord:
    grant_reference_hash: str
    parent_session_reference_hash: str
    source_surface_reference_hash: str
    parent_generation: int
    source_surface: Surface
    target_surface: Surface
    source_origin: str
    target_origin: str
    audience: str
    state_hash: str
    nonce_hash: str
    pkce_challenge: str
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None


@dataclass(frozen=True)
class AuthAuditEvent:
    event_type: AuthAuditEventType
    occurred_at: datetime
    correlation_id: str
    session_reference_hash: str
    user_id: str | None
    practice_id: str | None
    current_backend_role: str | None
    surface: str
    action: str
    resource_type: str
    policy_version: str
    decision: AuthAuditDecision
    reason_codes: tuple[str, ...]
    grant_reference_hash: str | None = None
    target_surface: str | None = None

    def __post_init__(self) -> None:
        _aware_utc(self.occurred_at)
        if not _CORRELATION_ID.fullmatch(self.correlation_id):
            raise ValueError("correlation_id must be a bounded opaque reference")
        if not self.session_reference_hash.startswith("sha256:"):
            raise ValueError("session_reference_hash must be a SHA-256 reference")
        if self.grant_reference_hash is not None and not (
            self.grant_reference_hash.startswith("sha256:")
        ):
            raise ValueError("grant_reference_hash must be a SHA-256 reference")
        if not self.reason_codes:
            raise ValueError("reason_codes must not be empty")


class AuthAuditSink(Protocol):
    """A sink must either admit the complete batch or raise without admission."""

    def record_batch(self, events: Sequence[AuthAuditEvent]) -> None:
        pass


class InMemoryAuthAuditSink:
    """Thread-safe authored-synthetic acceptance sink."""

    def __init__(self, *, data_class: str) -> None:
        _require_authored_synthetic_data_class(data_class)
        self.data_class = data_class
        self._events: list[AuthAuditEvent] = []
        self._lock = RLock()

    def record_batch(self, events: Sequence[AuthAuditEvent]) -> None:
        bounded = tuple(events)
        if not bounded:
            raise ValueError("audit batch must not be empty")
        with self._lock:
            self._events.extend(bounded)

    def snapshot(self) -> tuple[AuthAuditEvent, ...]:
        with self._lock:
            return tuple(self._events)


@dataclass(frozen=True)
class AuthRuntimeStateSnapshot:
    parent_sessions: tuple[ParentSessionRecord, ...]
    surface_sessions: tuple[SurfaceSessionRecord, ...]
    exchange_grants: tuple[ExchangeGrantRecord, ...]
    principal_generations: tuple[tuple[tuple[str, str], int], ...]


class InMemoryAuthoredSyntheticStore:
    """Explicit process-local store; never suitable as a live auth adapter."""

    def __init__(self, *, data_class: str) -> None:
        _require_authored_synthetic_data_class(data_class)
        self.data_class = data_class
        self.lock = RLock()
        self.parent_sessions: dict[str, ParentSessionRecord] = {}
        self.surface_sessions: dict[str, SurfaceSessionRecord] = {}
        self.exchange_grants: dict[str, ExchangeGrantRecord] = {}
        self.principal_generations: dict[tuple[str, str], int] = {}

    def snapshot(self) -> AuthRuntimeStateSnapshot:
        with self.lock:
            return AuthRuntimeStateSnapshot(
                parent_sessions=tuple(
                    self.parent_sessions[key]
                    for key in sorted(self.parent_sessions)
                ),
                surface_sessions=tuple(
                    self.surface_sessions[key]
                    for key in sorted(self.surface_sessions)
                ),
                exchange_grants=tuple(
                    self.exchange_grants[key]
                    for key in sorted(self.exchange_grants)
                ),
                principal_generations=tuple(
                    sorted(self.principal_generations.items())
                ),
            )


@dataclass(frozen=True)
class CreatedApplicationSession:
    parent_session_value: str
    surface_session_value: str
    surface: Surface
    generation: int
    parent_expires_at: datetime
    surface_idle_expires_at: datetime


@dataclass(frozen=True)
class ValidatedSurfaceContext:
    user_id: str
    practice_id: str
    current_backend_role: str
    practitioner_id: str | None
    surface: Surface
    origin: str
    audience: str
    generation: int
    parent_expires_at: datetime
    surface_idle_expires_at: datetime
    authority_source: str = "emr4_backend"
    data_class: str = AUTHORED_SYNTHETIC_DATA_CLASS


@dataclass(frozen=True)
class IssuedExchangeGrant:
    exchange_code: str
    source_surface: Surface
    target_surface: Surface
    expires_at: datetime


@dataclass(frozen=True)
class RedeemedExchangeGrant:
    target_surface_session_value: str
    target_surface: Surface
    parent_generation: int
    surface_idle_expires_at: datetime


def pkce_s256_challenge(verifier: str) -> str:
    """Return the RFC 7636 S256 code challenge for an accepted verifier."""

    if not _PKCE_VALUE.fullmatch(verifier):
        raise AuthRuntimeDenied("exchange_pkce_verifier_invalid")
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class ApplicationAuthRuntime:
    """Backend-owned coordinator for the bounded synthetic runtime foundation."""

    def __init__(
        self,
        *,
        store: InMemoryAuthoredSyntheticStore,
        audit_sink: AuthAuditSink,
        surface_origins: Mapping[Surface, str],
        clock: Callable[[], datetime] | None = None,
        token_source: Callable[[str], str] | None = None,
        parent_ttl: timedelta = MAX_PARENT_TTL,
        idle_ttl: timedelta = MAX_IDLE_TTL,
        exchange_ttl: timedelta = MAX_EXCHANGE_TTL,
    ) -> None:
        _require_authored_synthetic_data_class(store.data_class)
        if set(surface_origins) != set(Surface):
            raise ValueError("surface_origins must name exactly all three surfaces")
        self._surface_origins = {
            surface: _canonical_https_origin(origin)
            for surface, origin in surface_origins.items()
        }
        self._require_ttl(parent_ttl, MAX_PARENT_TTL, "parent_ttl")
        self._require_ttl(idle_ttl, MAX_IDLE_TTL, "idle_ttl")
        self._require_ttl(exchange_ttl, MAX_EXCHANGE_TTL, "exchange_ttl")
        self._store = store
        self._audit_sink = audit_sink
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._token_source = token_source or (
            lambda _kind: secrets.token_urlsafe(32)
        )
        self._parent_ttl = parent_ttl
        self._idle_ttl = idle_ttl
        self._exchange_ttl = exchange_ttl

    @staticmethod
    def _require_ttl(value: timedelta, maximum: timedelta, name: str) -> None:
        if value <= timedelta(0) or value > maximum:
            raise ValueError(f"{name} must be positive and no greater than {maximum}")

    def create_session(
        self,
        *,
        principal: SyntheticPrincipal,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> CreatedApplicationSession:
        now = self._now()
        self._require_surface_binding(surface, origin, audience)
        parent_value = self._new_opaque_value("parent")
        surface_value = self._new_opaque_value("surface")
        parent_hash = _hash_secret(parent_value)
        surface_hash = _hash_secret(surface_value)
        key = _principal_key(principal)

        with self._store.lock:
            self._require_unique_hash(parent_hash, surface_hash)
            generation = self._store.principal_generations.get(key, 1)
            parent_expires = now + self._parent_ttl
            idle_expires = min(parent_expires, now + self._idle_ttl)
            parent = ParentSessionRecord(
                session_reference_hash=parent_hash,
                principal=principal,
                generation=generation,
                status=SessionStatus.ACTIVE,
                created_at=now,
                last_observed_at=now,
                idle_expires_at=idle_expires,
                expires_at=parent_expires,
            )
            binding = SurfaceSessionRecord(
                surface_reference_hash=surface_hash,
                parent_session_reference_hash=parent_hash,
                surface=surface,
                origin=origin,
                audience=audience,
                parent_generation=generation,
                status=SessionStatus.ACTIVE,
                created_at=now,
                last_observed_at=now,
                idle_expires_at=idle_expires,
                expires_at=idle_expires,
            )
            cid = self._bounded_correlation_id(correlation_id)
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.SESSION_CREATED,
                        now=now,
                        correlation_id=cid,
                        parent=parent,
                        surface=surface.value,
                        action="auth.session.create",
                        resource_type="application_session",
                        decision=AuthAuditDecision.RECORDED,
                        reason="session_created",
                    ),
                    self._event(
                        AuthAuditEventType.SURFACE_BOUND,
                        now=now,
                        correlation_id=cid,
                        parent=parent,
                        surface=surface.value,
                        action="auth.surface.bind",
                        resource_type="surface_session",
                        decision=AuthAuditDecision.RECORDED,
                        reason="surface_bound",
                    ),
                )
            )
            self._store.principal_generations.setdefault(key, generation)
            self._store.parent_sessions[parent_hash] = parent
            self._store.surface_sessions[surface_hash] = binding

        return CreatedApplicationSession(
            parent_session_value=parent_value,
            surface_session_value=surface_value,
            surface=surface,
            generation=generation,
            parent_expires_at=parent_expires,
            surface_idle_expires_at=idle_expires,
        )

    def validate_surface_session(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> ValidatedSurfaceContext:
        now = self._now()
        surface_hash = _hash_secret(surface_session_value)
        with self._store.lock:
            try:
                self._require_surface_binding(surface, origin, audience)
                parent, binding = self._active_surface_records(
                    surface_hash=surface_hash,
                    expected_surface=surface,
                    expected_origin=origin,
                    expected_audience=audience,
                    now=now,
                )
            except AuthRuntimeDenied as exc:
                self._record_surface_denial(
                    surface_hash=surface_hash,
                    requested_surface=surface,
                    now=now,
                    correlation_id=correlation_id,
                    reason=exc.reason_code,
                )
                raise

            refreshed_parent, refreshed_binding = self._refreshed_records(
                parent, binding, now
            )
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.SESSION_REFRESHED,
                        now=now,
                        correlation_id=self._bounded_correlation_id(
                            correlation_id
                        ),
                        parent=parent,
                        surface=surface.value,
                        action="auth.session.validate",
                        resource_type="surface_session",
                        decision=AuthAuditDecision.ALLOWED,
                        reason="session_current",
                    ),
                )
            )
            self._store.parent_sessions[
                parent.session_reference_hash
            ] = refreshed_parent
            self._store.surface_sessions[surface_hash] = refreshed_binding

        principal = parent.principal
        return ValidatedSurfaceContext(
            user_id=principal.user_id,
            practice_id=principal.practice_id,
            current_backend_role=principal.current_backend_role,
            practitioner_id=principal.practitioner_id,
            surface=surface,
            origin=origin,
            audience=audience,
            generation=parent.generation,
            parent_expires_at=parent.expires_at,
            surface_idle_expires_at=refreshed_binding.idle_expires_at,
        )

    def authorize_practitioner_directory_read(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        fresh_principal: SyntheticPrincipal | None,
        fresh_user_active: bool,
        resource_practice_id: str,
        active_only: bool,
        audience: str = SURFACE_AUDIENCE,
        correlation_id: str | None = None,
    ) -> ValidatedSurfaceContext:
        """Admit the one fixed active practitioner-directory read policy."""

        now = self._now()
        surface_hash = _hash_secret(surface_session_value)
        with self._store.lock:
            try:
                self._require_surface_binding(surface, origin, audience)
                parent, binding = self._active_surface_records(
                    surface_hash=surface_hash,
                    expected_surface=surface,
                    expected_origin=origin,
                    expected_audience=audience,
                    now=now,
                )
            except AuthRuntimeDenied as exc:
                self._record_surface_denial(
                    surface_hash=surface_hash,
                    requested_surface=surface,
                    now=now,
                    correlation_id=correlation_id,
                    reason=exc.reason_code,
                )
                raise

            denial_reason: str | None = None
            if not fresh_user_active or fresh_principal is None:
                denial_reason = "fresh_product_user_inactive"
            elif fresh_principal != parent.principal:
                denial_reason = "fresh_product_principal_mismatch"
            elif resource_practice_id != parent.principal.practice_id:
                denial_reason = "resource_practice_mismatch"
            elif not active_only:
                denial_reason = "inactive_practitioner_directory_closed"

            bounded_correlation_id = self._bounded_correlation_id(correlation_id)
            if denial_reason is not None:
                self._record_required(
                    (
                        self._event(
                            AuthAuditEventType.AUTHORIZATION_DENIED,
                            now=now,
                            correlation_id=bounded_correlation_id,
                            parent=parent,
                            surface=surface.value,
                            action=PRACTITIONER_DIRECTORY_ACTION,
                            resource_type=PRACTITIONER_DIRECTORY_RESOURCE_TYPE,
                            policy_version=PRACTITIONER_DIRECTORY_POLICY_VERSION,
                            decision=AuthAuditDecision.DENIED,
                            reason=denial_reason,
                        ),
                    )
                )
                raise AuthRuntimeDenied(denial_reason)

            refreshed_parent, refreshed_binding = self._refreshed_records(
                parent, binding, now
            )
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.AUTHORIZATION_ALLOWED,
                        now=now,
                        correlation_id=bounded_correlation_id,
                        parent=parent,
                        surface=surface.value,
                        action=PRACTITIONER_DIRECTORY_ACTION,
                        resource_type=PRACTITIONER_DIRECTORY_RESOURCE_TYPE,
                        policy_version=PRACTITIONER_DIRECTORY_POLICY_VERSION,
                        decision=AuthAuditDecision.ALLOWED,
                        reason="active_practitioner_directory_authorized",
                    ),
                )
            )
            self._store.parent_sessions[
                parent.session_reference_hash
            ] = refreshed_parent
            self._store.surface_sessions[surface_hash] = refreshed_binding

        principal = parent.principal
        return ValidatedSurfaceContext(
            user_id=principal.user_id,
            practice_id=principal.practice_id,
            current_backend_role=principal.current_backend_role,
            practitioner_id=principal.practitioner_id,
            surface=surface,
            origin=origin,
            audience=audience,
            generation=parent.generation,
            parent_expires_at=parent.expires_at,
            surface_idle_expires_at=refreshed_binding.idle_expires_at,
        )

    def issue_exchange(
        self,
        *,
        source_surface_session_value: str,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        audience: str,
        state: str,
        nonce: str,
        pkce_challenge: str,
        correlation_id: str | None = None,
    ) -> IssuedExchangeGrant:
        now = self._now()
        source_hash = _hash_secret(source_surface_session_value)
        with self._store.lock:
            try:
                self._require_exchange_flow(
                    source_surface=source_surface,
                    target_surface=target_surface,
                    source_origin=source_origin,
                    target_origin=target_origin,
                    audience=audience,
                )
                self._require_exchange_challenge_inputs(
                    state=state,
                    nonce=nonce,
                    pkce_challenge=pkce_challenge,
                )
                parent, binding = self._active_surface_records(
                    surface_hash=source_hash,
                    expected_surface=source_surface,
                    expected_origin=source_origin,
                    expected_audience=SURFACE_AUDIENCE,
                    now=now,
                )
            except AuthRuntimeDenied as exc:
                audit_parent = self._parent_for_surface(source_hash)
                self._record_exchange_denial(
                    grant=None,
                    parent=audit_parent,
                    requested_surface=source_surface,
                    target_surface=target_surface,
                    now=now,
                    correlation_id=correlation_id,
                    reason=exc.reason_code,
                    operation_action="auth.exchange.issue",
                    session_reference_hash=(
                        (
                            audit_parent.session_reference_hash
                            if audit_parent is not None
                            else None
                        )
                        or _unresolved_hash()
                    ),
                )
                raise

            exchange_code = self._new_opaque_value("exchange")
            grant_hash = _hash_secret(exchange_code)
            if grant_hash in self._store.exchange_grants:
                raise AuthRuntimeDenied("opaque_value_collision")
            grant = ExchangeGrantRecord(
                grant_reference_hash=grant_hash,
                parent_session_reference_hash=parent.session_reference_hash,
                source_surface_reference_hash=source_hash,
                parent_generation=parent.generation,
                source_surface=source_surface,
                target_surface=target_surface,
                source_origin=source_origin,
                target_origin=target_origin,
                audience=audience,
                state_hash=_hash_secret(state),
                nonce_hash=_hash_secret(nonce),
                pkce_challenge=pkce_challenge,
                issued_at=now,
                expires_at=min(parent.expires_at, now + self._exchange_ttl),
                consumed_at=None,
            )
            refreshed_parent, refreshed_binding = self._refreshed_records(
                parent, binding, now
            )
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.EXCHANGE_ISSUED,
                        now=now,
                        correlation_id=self._bounded_correlation_id(
                            correlation_id
                        ),
                        parent=parent,
                        surface=source_surface.value,
                        target_surface=target_surface.value,
                        action="auth.exchange.issue",
                        resource_type="cross_surface_exchange",
                        decision=AuthAuditDecision.ALLOWED,
                        reason="exchange_issued",
                        grant_reference_hash=grant_hash,
                    ),
                )
            )
            self._store.parent_sessions[
                parent.session_reference_hash
            ] = refreshed_parent
            self._store.surface_sessions[source_hash] = refreshed_binding
            self._store.exchange_grants[grant_hash] = grant

        return IssuedExchangeGrant(
            exchange_code=exchange_code,
            source_surface=source_surface,
            target_surface=target_surface,
            expires_at=grant.expires_at,
        )

    def redeem_exchange(
        self,
        *,
        exchange_code: str,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        audience: str,
        state: str,
        nonce: str,
        pkce_verifier: str,
        correlation_id: str | None = None,
    ) -> RedeemedExchangeGrant:
        now = self._now()
        grant_hash = _hash_secret(exchange_code)
        with self._store.lock:
            grant = self._store.exchange_grants.get(grant_hash)
            parent = (
                self._store.parent_sessions.get(
                    grant.parent_session_reference_hash
                )
                if grant is not None
                else None
            )
            try:
                self._require_redeemable_exchange(
                    grant=grant,
                    parent=parent,
                    source_surface=source_surface,
                    target_surface=target_surface,
                    source_origin=source_origin,
                    target_origin=target_origin,
                    audience=audience,
                    state=state,
                    nonce=nonce,
                    pkce_verifier=pkce_verifier,
                    now=now,
                )
                assert grant is not None
                assert parent is not None
                source_parent, source_binding = self._active_surface_records(
                    surface_hash=grant.source_surface_reference_hash,
                    expected_surface=source_surface,
                    expected_origin=source_origin,
                    expected_audience=SURFACE_AUDIENCE,
                    now=now,
                )
                if source_parent.session_reference_hash != (
                    parent.session_reference_hash
                ):
                    raise AuthRuntimeDenied("exchange_parent_session_mismatch")
            except AuthRuntimeDenied as exc:
                self._record_exchange_denial(
                    grant=grant,
                    parent=parent,
                    requested_surface=source_surface,
                    target_surface=target_surface,
                    now=now,
                    correlation_id=correlation_id,
                    reason=exc.reason_code,
                    operation_action="auth.exchange.redeem",
                    session_reference_hash=(
                        parent.session_reference_hash
                        if parent is not None
                        else _unresolved_hash()
                    ),
                )
                raise

            target_value = self._new_opaque_value("surface")
            target_hash = _hash_secret(target_value)
            if target_hash in self._store.surface_sessions:
                raise AuthRuntimeDenied("opaque_value_collision")
            target_idle_expires = min(
                parent.expires_at,
                now + self._idle_ttl,
            )
            target_binding = SurfaceSessionRecord(
                surface_reference_hash=target_hash,
                parent_session_reference_hash=parent.session_reference_hash,
                surface=target_surface,
                origin=target_origin,
                audience=SURFACE_AUDIENCE,
                parent_generation=parent.generation,
                status=SessionStatus.ACTIVE,
                created_at=now,
                last_observed_at=now,
                idle_expires_at=target_idle_expires,
                expires_at=target_idle_expires,
            )
            refreshed_parent, refreshed_source = self._refreshed_records(
                parent, source_binding, now
            )
            cid = self._bounded_correlation_id(correlation_id)
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.EXCHANGE_REDEEMED,
                        now=now,
                        correlation_id=cid,
                        parent=parent,
                        surface=source_surface.value,
                        target_surface=target_surface.value,
                        action="auth.exchange.redeem",
                        resource_type="cross_surface_exchange",
                        decision=AuthAuditDecision.ALLOWED,
                        reason="exchange_redeemed",
                        grant_reference_hash=grant_hash,
                    ),
                    self._event(
                        AuthAuditEventType.SURFACE_BOUND,
                        now=now,
                        correlation_id=cid,
                        parent=parent,
                        surface=target_surface.value,
                        action="auth.surface.bind",
                        resource_type="surface_session",
                        decision=AuthAuditDecision.RECORDED,
                        reason="surface_bound_by_exchange",
                        grant_reference_hash=grant_hash,
                    ),
                )
            )
            self._store.exchange_grants[grant_hash] = replace(
                grant, consumed_at=now
            )
            self._store.parent_sessions[
                parent.session_reference_hash
            ] = refreshed_parent
            self._store.surface_sessions[
                grant.source_surface_reference_hash
            ] = refreshed_source
            self._store.surface_sessions[target_hash] = target_binding

        return RedeemedExchangeGrant(
            target_surface_session_value=target_value,
            target_surface=target_surface,
            parent_generation=parent.generation,
            surface_idle_expires_at=target_idle_expires,
        )

    def revoke_parent_session(
        self,
        *,
        parent_session_value: str,
        correlation_id: str | None = None,
        reason: str = "logout_everywhere",
    ) -> None:
        self._require_revocation_reason(reason)
        now = self._now()
        parent_hash = _hash_secret(parent_session_value)
        with self._store.lock:
            parent = self._store.parent_sessions.get(parent_hash)
            if parent is None:
                raise AuthRuntimeDenied("application_session_required")
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.SESSION_REVOKED,
                        now=now,
                        correlation_id=self._bounded_correlation_id(
                            correlation_id
                        ),
                        parent=parent,
                        surface="all",
                        action="auth.session.revoke",
                        resource_type="application_session",
                        decision=AuthAuditDecision.RECORDED,
                        reason=reason,
                    ),
                )
            )
            self._store.parent_sessions[parent_hash] = replace(
                parent,
                status=SessionStatus.REVOKED,
                last_observed_at=max(now, parent.last_observed_at),
            )

    def revoke_surface_session(
        self,
        *,
        surface_session_value: str,
        correlation_id: str | None = None,
        reason: str = "security_reset",
    ) -> None:
        self._require_revocation_reason(reason)
        now = self._now()
        surface_hash = _hash_secret(surface_session_value)
        with self._store.lock:
            binding = self._store.surface_sessions.get(surface_hash)
            if binding is None:
                raise AuthRuntimeDenied("surface_session_required")
            parent = self._store.parent_sessions.get(
                binding.parent_session_reference_hash
            )
            if parent is None:
                raise AuthRuntimeDenied("application_session_required")
            self._record_required(
                (
                    self._event(
                        AuthAuditEventType.SESSION_REVOKED,
                        now=now,
                        correlation_id=self._bounded_correlation_id(
                            correlation_id
                        ),
                        parent=parent,
                        surface=binding.surface.value,
                        action="auth.surface.revoke",
                        resource_type="surface_session",
                        decision=AuthAuditDecision.RECORDED,
                        reason=reason,
                    ),
                )
            )
            self._store.surface_sessions[surface_hash] = replace(
                binding,
                status=SessionStatus.REVOKED,
                last_observed_at=max(now, binding.last_observed_at),
            )

    def advance_principal_generation(
        self,
        *,
        principal: SyntheticPrincipal,
        reason: str,
        correlation_id: str | None = None,
    ) -> int:
        self._require_revocation_reason(reason)
        now = self._now()
        key = _principal_key(principal)
        with self._store.lock:
            current = self._store.principal_generations.get(key, 1)
            new_generation = current + 1
            matching = tuple(
                parent
                for parent in self._store.parent_sessions.values()
                if _principal_key(parent.principal) == key
            )
            parents_for_audit = matching or (
                ParentSessionRecord(
                    session_reference_hash=_unresolved_hash(),
                    principal=principal,
                    generation=current,
                    status=SessionStatus.REVOKED,
                    created_at=now,
                    last_observed_at=now,
                    idle_expires_at=now,
                    expires_at=now,
                ),
            )
            cid = self._bounded_correlation_id(correlation_id)
            self._record_required(
                tuple(
                    self._event(
                        AuthAuditEventType.SESSION_REVOKED,
                        now=now,
                        correlation_id=cid,
                        parent=parent,
                        surface="all",
                        action="auth.principal.revoke",
                        resource_type="principal_generation",
                        decision=AuthAuditDecision.RECORDED,
                        reason=reason,
                    )
                    for parent in parents_for_audit
                )
            )
            self._store.principal_generations[key] = new_generation
            for parent in matching:
                self._store.parent_sessions[
                    parent.session_reference_hash
                ] = replace(
                    parent,
                    status=SessionStatus.REVOKED,
                    last_observed_at=max(now, parent.last_observed_at),
                )
        return new_generation

    def safe_state_snapshot(self) -> AuthRuntimeStateSnapshot:
        return self._store.snapshot()

    def _now(self) -> datetime:
        return _aware_utc(self._clock())

    def _new_opaque_value(self, kind: str) -> str:
        prefixes = {"parent": "aps", "surface": "ass", "exchange": "aex"}
        entropy = self._token_source(kind)
        if not isinstance(entropy, str) or len(entropy) < 32:
            raise AuthRuntimeDenied("opaque_value_source_invalid")
        if any(character.isspace() for character in entropy):
            raise AuthRuntimeDenied("opaque_value_source_invalid")
        return f"{prefixes[kind]}.{entropy}"

    def _new_correlation_id(self) -> str:
        return f"correlation-{secrets.token_hex(16)}"

    def _bounded_correlation_id(self, value: str | None) -> str:
        effective = value or self._new_correlation_id()
        if not _CORRELATION_ID.fullmatch(effective):
            raise AuthRuntimeDenied("correlation_id_invalid")
        return effective

    def _require_unique_hash(self, parent_hash: str, surface_hash: str) -> None:
        if parent_hash in self._store.parent_sessions:
            raise AuthRuntimeDenied("opaque_value_collision")
        if surface_hash in self._store.surface_sessions:
            raise AuthRuntimeDenied("opaque_value_collision")

    def _require_surface_binding(
        self,
        surface: Surface,
        origin: str,
        audience: str,
    ) -> None:
        if origin != self._surface_origins[surface]:
            raise AuthRuntimeDenied("surface_session_origin_mismatch")
        if audience != SURFACE_AUDIENCE:
            raise AuthRuntimeDenied("surface_session_audience_mismatch")

    def _require_exchange_flow(
        self,
        *,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        audience: str,
    ) -> None:
        if source_surface not in {Surface.WORD_DESKTOP, Surface.WORD_ONLINE}:
            raise AuthRuntimeDenied("exchange_source_surface_mismatch")
        if target_surface is not Surface.NATIVE_DIARY:
            raise AuthRuntimeDenied("exchange_target_surface_mismatch")
        if source_origin != self._surface_origins[source_surface]:
            raise AuthRuntimeDenied("exchange_source_origin_mismatch")
        if target_origin != self._surface_origins[target_surface]:
            raise AuthRuntimeDenied("exchange_target_origin_mismatch")
        if audience != EXCHANGE_AUDIENCE:
            raise AuthRuntimeDenied("exchange_audience_mismatch")

    @staticmethod
    def _require_exchange_challenge_inputs(
        *,
        state: str,
        nonce: str,
        pkce_challenge: str,
    ) -> None:
        if len(state) < 16:
            raise AuthRuntimeDenied("exchange_state_invalid")
        if len(nonce) < 16:
            raise AuthRuntimeDenied("exchange_nonce_invalid")
        if not _PKCE_CHALLENGE.fullmatch(pkce_challenge):
            raise AuthRuntimeDenied("exchange_pkce_challenge_invalid")

    def _require_redeemable_exchange(
        self,
        *,
        grant: ExchangeGrantRecord | None,
        parent: ParentSessionRecord | None,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        audience: str,
        state: str,
        nonce: str,
        pkce_verifier: str,
        now: datetime,
    ) -> None:
        if grant is None:
            raise AuthRuntimeDenied("exchange_invalid")
        if grant.consumed_at is not None:
            raise AuthRuntimeDenied("exchange_already_consumed")
        if now < grant.issued_at:
            raise AuthRuntimeDenied("clock_rollback_detected")
        if now >= grant.expires_at:
            raise AuthRuntimeDenied("exchange_expired")
        if parent is None or parent.status is not SessionStatus.ACTIVE:
            raise AuthRuntimeDenied("exchange_parent_session_inactive")
        current_generation = self._store.principal_generations.get(
            _principal_key(parent.principal)
        )
        if (
            current_generation != grant.parent_generation
            or parent.generation != grant.parent_generation
        ):
            raise AuthRuntimeDenied("exchange_parent_generation_mismatch")
        if source_surface is not grant.source_surface:
            raise AuthRuntimeDenied("exchange_source_surface_mismatch")
        if target_surface is not grant.target_surface:
            raise AuthRuntimeDenied("exchange_target_surface_mismatch")
        if source_origin != grant.source_origin:
            raise AuthRuntimeDenied("exchange_source_origin_mismatch")
        if target_origin != grant.target_origin:
            raise AuthRuntimeDenied("exchange_target_origin_mismatch")
        if audience != grant.audience:
            raise AuthRuntimeDenied("exchange_audience_mismatch")
        if not hmac.compare_digest(_hash_secret(state), grant.state_hash):
            raise AuthRuntimeDenied("exchange_state_mismatch")
        if not hmac.compare_digest(_hash_secret(nonce), grant.nonce_hash):
            raise AuthRuntimeDenied("exchange_nonce_mismatch")
        challenge = pkce_s256_challenge(pkce_verifier)
        if not hmac.compare_digest(challenge, grant.pkce_challenge):
            raise AuthRuntimeDenied("exchange_pkce_mismatch")

    def _active_surface_records(
        self,
        *,
        surface_hash: str,
        expected_surface: Surface,
        expected_origin: str,
        expected_audience: str,
        now: datetime,
    ) -> tuple[ParentSessionRecord, SurfaceSessionRecord]:
        binding = self._store.surface_sessions.get(surface_hash)
        if binding is None:
            raise AuthRuntimeDenied("surface_session_required")
        parent = self._store.parent_sessions.get(
            binding.parent_session_reference_hash
        )
        if parent is None:
            raise AuthRuntimeDenied("application_session_required")
        if parent.status is not SessionStatus.ACTIVE:
            raise AuthRuntimeDenied("application_session_revoked")
        if now < parent.last_observed_at or now < binding.last_observed_at:
            raise AuthRuntimeDenied("clock_rollback_detected")
        if now >= parent.expires_at:
            raise AuthRuntimeDenied("application_session_expired")
        if now >= parent.idle_expires_at:
            raise AuthRuntimeDenied("application_session_idle_expired")
        current_generation = self._store.principal_generations.get(
            _principal_key(parent.principal)
        )
        if current_generation != parent.generation:
            raise AuthRuntimeDenied("application_session_generation_mismatch")
        if binding.status is not SessionStatus.ACTIVE:
            raise AuthRuntimeDenied("surface_session_revoked")
        if binding.parent_generation != parent.generation:
            raise AuthRuntimeDenied("surface_session_generation_mismatch")
        if binding.surface is not expected_surface:
            raise AuthRuntimeDenied("surface_session_surface_mismatch")
        if binding.origin != expected_origin:
            raise AuthRuntimeDenied("surface_session_origin_mismatch")
        if binding.audience != expected_audience:
            raise AuthRuntimeDenied("surface_session_audience_mismatch")
        if now >= binding.expires_at or now >= binding.idle_expires_at:
            raise AuthRuntimeDenied("surface_session_idle_expired")
        if binding.expires_at > parent.expires_at:
            raise AuthRuntimeDenied("surface_session_parent_expiry_mismatch")
        return parent, binding

    def _refreshed_records(
        self,
        parent: ParentSessionRecord,
        binding: SurfaceSessionRecord,
        now: datetime,
    ) -> tuple[ParentSessionRecord, SurfaceSessionRecord]:
        idle_expires = min(parent.expires_at, now + self._idle_ttl)
        return (
            replace(
                parent,
                last_observed_at=now,
                idle_expires_at=idle_expires,
            ),
            replace(
                binding,
                last_observed_at=now,
                idle_expires_at=idle_expires,
                expires_at=idle_expires,
            ),
        )

    def _record_surface_denial(
        self,
        *,
        surface_hash: str,
        requested_surface: Surface,
        now: datetime,
        correlation_id: str | None,
        reason: str,
    ) -> None:
        binding = self._store.surface_sessions.get(surface_hash)
        parent = (
            self._store.parent_sessions.get(
                binding.parent_session_reference_hash
            )
            if binding is not None
            else None
        )
        self._record_required(
            (
                self._event(
                    AuthAuditEventType.AUTHORIZATION_DENIED,
                    now=now,
                    correlation_id=self._bounded_correlation_id(correlation_id),
                    parent=parent,
                    session_reference_hash=(
                        parent.session_reference_hash
                        if parent is not None
                        else _unresolved_hash()
                    ),
                    surface=requested_surface.value,
                    action="auth.session.validate",
                    resource_type="surface_session",
                    decision=AuthAuditDecision.DENIED,
                    reason=reason,
                ),
            )
        )

    def _record_exchange_denial(
        self,
        *,
        grant: ExchangeGrantRecord | None,
        parent: ParentSessionRecord | None,
        requested_surface: Surface,
        target_surface: Surface,
        now: datetime,
        correlation_id: str | None,
        reason: str,
        operation_action: str,
        session_reference_hash: str,
    ) -> None:
        self._record_required(
            (
                self._event(
                    AuthAuditEventType.EXCHANGE_REJECTED,
                    now=now,
                    correlation_id=self._bounded_correlation_id(correlation_id),
                    parent=parent,
                    session_reference_hash=session_reference_hash,
                    surface=requested_surface.value,
                    target_surface=target_surface.value,
                    action=operation_action,
                    resource_type="cross_surface_exchange",
                    decision=AuthAuditDecision.DENIED,
                    reason=reason,
                    grant_reference_hash=(
                        grant.grant_reference_hash
                        if grant is not None
                        else None
                    ),
                ),
            )
        )

    def _event(
        self,
        event_type: AuthAuditEventType,
        *,
        now: datetime,
        correlation_id: str,
        surface: str,
        action: str,
        resource_type: str,
        decision: AuthAuditDecision,
        reason: str,
        policy_version: str = POLICY_VERSION,
        parent: ParentSessionRecord | None = None,
        session_reference_hash: str | None = None,
        grant_reference_hash: str | None = None,
        target_surface: str | None = None,
    ) -> AuthAuditEvent:
        principal = parent.principal if parent is not None else None
        return AuthAuditEvent(
            event_type=event_type,
            occurred_at=now,
            correlation_id=correlation_id,
            session_reference_hash=(
                session_reference_hash
                or (
                    parent.session_reference_hash
                    if parent is not None
                    else _unresolved_hash()
                )
            ),
            user_id=principal.user_id if principal is not None else None,
            practice_id=(principal.practice_id if principal is not None else None),
            current_backend_role=(
                principal.current_backend_role if principal is not None else None
            ),
            surface=surface,
            action=action,
            resource_type=resource_type,
            policy_version=policy_version,
            decision=decision,
            reason_codes=(reason,),
            grant_reference_hash=grant_reference_hash,
            target_surface=target_surface,
        )

    def _record_required(self, events: Sequence[AuthAuditEvent]) -> None:
        try:
            self._audit_sink.record_batch(tuple(events))
        except Exception:
            raise RequiredAuditUnavailable() from None

    def _parent_for_surface(
        self, surface_hash: str
    ) -> ParentSessionRecord | None:
        binding = self._store.surface_sessions.get(surface_hash)
        return self._store.parent_sessions.get(
            binding.parent_session_reference_hash
        ) if binding is not None else None

    @staticmethod
    def _require_revocation_reason(reason: str) -> None:
        if reason not in _REVOCATION_REASONS:
            raise ValueError("revocation reason is not allowlisted")


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AuthRuntimeDenied("timezone_aware_clock_required")
    return value.astimezone(timezone.utc)


def _hash_secret(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise AuthRuntimeDenied("opaque_value_required")
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _unresolved_hash() -> str:
    return f"sha256:{'0' * 64}"


def _require_authored_synthetic_data_class(data_class: str) -> None:
    if data_class != AUTHORED_SYNTHETIC_DATA_CLASS:
        raise ValueError("only authored_synthetic state is accepted")


def _require_synthetic_reference(value: str, field_name: str) -> None:
    if not _SYNTHETIC_REFERENCE.fullmatch(value):
        raise ValueError(f"{field_name} must be an authored-synthetic reference")


def _principal_key(principal: SyntheticPrincipal) -> tuple[str, str]:
    return principal.user_id, principal.practice_id


def _canonical_https_origin(origin: str) -> str:
    parsed = urlsplit(origin)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("surface origin must be a canonical HTTPS origin")
    canonical = f"https://{parsed.netloc}"
    if origin != canonical:
        raise ValueError("surface origin must not include a path or trailing slash")
    return canonical


__all__ = [
    "AUTHORED_SYNTHETIC_DATA_CLASS",
    "EXCHANGE_AUDIENCE",
    "MAX_EXCHANGE_TTL",
    "MAX_IDLE_TTL",
    "MAX_PARENT_TTL",
    "SURFACE_AUDIENCE",
    "ApplicationAuthRuntime",
    "AuthAuditDecision",
    "AuthAuditEvent",
    "AuthAuditEventType",
    "AuthRuntimeDenied",
    "AuthRuntimeStateSnapshot",
    "CreatedApplicationSession",
    "InMemoryAuthAuditSink",
    "InMemoryAuthoredSyntheticStore",
    "IssuedExchangeGrant",
    "RedeemedExchangeGrant",
    "RequiredAuditUnavailable",
    "SessionStatus",
    "Surface",
    "SyntheticPrincipal",
    "ValidatedSurfaceContext",
    "pkce_s256_challenge",
]
