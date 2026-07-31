"""Default-off, provider-free authored-synthetic browser transport service."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from threading import RLock
from typing import Callable, Mapping

from app.services.application_auth_role_runtime import (
    RoleScopedPostgresApplicationAuthRuntime,
    RotatedSurfaceSession,
)
from app.services.application_auth_runtime import (
    EXCHANGE_AUDIENCE,
    SURFACE_AUDIENCE,
    AuthRuntimeDenied,
    CreatedApplicationSession,
    IssuedExchangeGrant,
    RedeemedExchangeGrant,
    Surface,
    SyntheticPrincipal,
    ValidatedSurfaceContext,
)


SESSION_COOKIE_NAME = "__Host-emr4-application-session"
CSRF_COOKIE_NAME = "__Host-emr4-application-csrf"
CSRF_HEADER_NAME = "X-EMR4-CSRF"
PREAUTH_CSRF_MAX_AGE_SECONDS = 300

_OPAQUE_VALUE = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")


class TransportRequestDenied(RuntimeError):
    """Origin or CSRF admission failed without exposing supplied values."""


@dataclass(frozen=True)
class _BootstrapReservation:
    credential_hash: str
    principal: SyntheticPrincipal


class OneUseSyntheticBootstrapRegistry:
    """Hash-only, process-local and one-use synthetic identity establishment."""

    def __init__(self, credentials: Mapping[str, SyntheticPrincipal]) -> None:
        self._lock = RLock()
        self._entries: dict[str, tuple[SyntheticPrincipal, str]] = {}
        for credential, principal in credentials.items():
            if not _OPAQUE_VALUE.fullmatch(credential):
                raise ValueError("synthetic bootstrap credential is not bounded")
            reference_hash = self._hash(credential)
            if reference_hash in self._entries:
                raise ValueError("synthetic bootstrap credential collision")
            self._entries[reference_hash] = (principal, "available")

    @staticmethod
    def _hash(value: str) -> str:
        return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"

    def reserve(self, credential: str) -> _BootstrapReservation:
        supplied_hash = self._hash(credential) if isinstance(credential, str) else ""
        selected_hash: str | None = None
        selected_principal: SyntheticPrincipal | None = None
        with self._lock:
            for candidate_hash, (principal, state) in self._entries.items():
                if hmac.compare_digest(supplied_hash, candidate_hash) and state == "available":
                    selected_hash = candidate_hash
                    selected_principal = principal
            if selected_hash is None or selected_principal is None:
                raise AuthRuntimeDenied("synthetic_bootstrap_invalid")
            self._entries[selected_hash] = (selected_principal, "reserved")
        return _BootstrapReservation(selected_hash, selected_principal)

    def commit(self, reservation: _BootstrapReservation) -> None:
        with self._lock:
            current = self._entries.get(reservation.credential_hash)
            if current != (reservation.principal, "reserved"):
                raise AuthRuntimeDenied("synthetic_bootstrap_invalid")
            self._entries[reservation.credential_hash] = (
                reservation.principal,
                "consumed",
            )

    def release(self, reservation: _BootstrapReservation) -> None:
        with self._lock:
            current = self._entries.get(reservation.credential_hash)
            if current == (reservation.principal, "reserved"):
                self._entries[reservation.credential_hash] = (
                    reservation.principal,
                    "available",
                )

    def state_counts(self) -> dict[str, int]:
        with self._lock:
            return {
                state: sum(1 for _, item_state in self._entries.values() if item_state == state)
                for state in ("available", "reserved", "consumed")
            }


class ApplicationAuthTransport:
    """Transport admission around the accepted role-scoped runtime."""

    def __init__(
        self,
        *,
        runtime: RoleScopedPostgresApplicationAuthRuntime,
        bootstrap_registry: OneUseSyntheticBootstrapRegistry,
        surface_origins: Mapping[Surface, str],
        csrf_token_source: Callable[[], str] | None = None,
    ) -> None:
        self.runtime = runtime
        self.bootstrap_registry = bootstrap_registry
        self.surface_origins = dict(surface_origins)
        if set(self.surface_origins) != set(Surface):
            raise ValueError("all three shared-auth surface origins are required")
        self._csrf_token_source = csrf_token_source or (
            lambda: f"csrf.{secrets.token_urlsafe(32)}"
        )

    def require_origin(self, surface: Surface, origin: str | None) -> str:
        expected = self.surface_origins.get(surface)
        if not isinstance(origin, str) or origin != expected:
            raise TransportRequestDenied()
        return origin

    @staticmethod
    def require_csrf(cookie_value: str | None, header_value: str | None) -> None:
        cookie = cookie_value if isinstance(cookie_value, str) else ""
        header = header_value if isinstance(header_value, str) else ""
        valid_shape = bool(
            _OPAQUE_VALUE.fullmatch(cookie) and _OPAQUE_VALUE.fullmatch(header)
        )
        if not valid_shape or not hmac.compare_digest(cookie, header):
            raise TransportRequestDenied()

    def new_csrf_token(self) -> str:
        value = self._csrf_token_source()
        if not isinstance(value, str) or not _OPAQUE_VALUE.fullmatch(value):
            raise AuthRuntimeDenied("csrf_token_source_invalid")
        return value

    def login(
        self,
        *,
        bootstrap_credential: str,
        surface: Surface,
        origin: str,
        correlation_id: str | None,
    ) -> tuple[CreatedApplicationSession, str]:
        reservation = self.bootstrap_registry.reserve(bootstrap_credential)
        try:
            created = self.runtime.create_session(
                principal=reservation.principal,
                surface=surface,
                origin=origin,
                audience=SURFACE_AUDIENCE,
                correlation_id=correlation_id,
            )
        except Exception:
            self.bootstrap_registry.release(reservation)
            raise
        self.bootstrap_registry.commit(reservation)
        return created, self.new_csrf_token()

    def validate(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        correlation_id: str | None,
    ) -> ValidatedSurfaceContext:
        return self.runtime.validate_surface_session(
            surface_session_value=surface_session_value,
            surface=surface,
            origin=origin,
            audience=SURFACE_AUDIENCE,
            correlation_id=correlation_id,
        )

    def rotate(
        self,
        *,
        surface_session_value: str,
        surface: Surface,
        origin: str,
        correlation_id: str | None,
    ) -> tuple[RotatedSurfaceSession, str]:
        rotated = self.runtime.rotate_surface_session(
            surface_session_value=surface_session_value,
            surface=surface,
            origin=origin,
            audience=SURFACE_AUDIENCE,
            correlation_id=correlation_id,
        )
        return rotated, self.new_csrf_token()

    def logout(
        self,
        *,
        surface_session_value: str,
        correlation_id: str | None,
    ) -> None:
        self.runtime.revoke_surface_session(
            surface_session_value=surface_session_value,
            correlation_id=correlation_id,
            reason="security_reset",
        )

    def issue_exchange(
        self,
        *,
        source_surface_session_value: str,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        state: str,
        nonce: str,
        pkce_challenge: str,
        correlation_id: str | None,
    ) -> IssuedExchangeGrant:
        return self.runtime.issue_exchange(
            source_surface_session_value=source_surface_session_value,
            source_surface=source_surface,
            target_surface=target_surface,
            source_origin=source_origin,
            target_origin=target_origin,
            audience=EXCHANGE_AUDIENCE,
            state=state,
            nonce=nonce,
            pkce_challenge=pkce_challenge,
            correlation_id=correlation_id,
        )

    def redeem_exchange(
        self,
        *,
        exchange_code: str,
        source_surface: Surface,
        target_surface: Surface,
        source_origin: str,
        target_origin: str,
        state: str,
        nonce: str,
        pkce_verifier: str,
        correlation_id: str | None,
    ) -> tuple[RedeemedExchangeGrant, str]:
        redeemed = self.runtime.redeem_exchange(
            exchange_code=exchange_code,
            source_surface=source_surface,
            target_surface=target_surface,
            source_origin=source_origin,
            target_origin=target_origin,
            audience=EXCHANGE_AUDIENCE,
            state=state,
            nonce=nonce,
            pkce_verifier=pkce_verifier,
            correlation_id=correlation_id,
        )
        return redeemed, self.new_csrf_token()


__all__ = [
    "ApplicationAuthTransport",
    "CSRF_COOKIE_NAME",
    "CSRF_HEADER_NAME",
    "OneUseSyntheticBootstrapRegistry",
    "PREAUTH_CSRF_MAX_AGE_SECONDS",
    "SESSION_COOKIE_NAME",
    "TransportRequestDenied",
]
