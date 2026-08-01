"""Bounded operational admission for the authored-synthetic auth transport.

This guard can only deny.  It does not authenticate, map identity, evaluate
product permissions or grant command authority.
"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import math
import secrets
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.application_auth import ApplicationAuthAuditEvent
from app.services.application_auth_transport import TransportRequestDenied


TRANSPORT_AUDIT_PRACTICE = "synthetic-transport-audit"
TRANSPORT_AUDIT_POLICY = "clinician-workspace-read.v1"
_AUTH_PREFIX = "/api/v1/application-auth"
_PATH_ACTIONS = {
    f"{_AUTH_PREFIX}/csrf": "auth.transport.csrf",
    f"{_AUTH_PREFIX}/synthetic/session": "auth.transport.login",
    f"{_AUTH_PREFIX}/session/validate": "auth.transport.validate",
    f"{_AUTH_PREFIX}/session/rotate": "auth.transport.rotate",
    f"{_AUTH_PREFIX}/session/logout": "auth.transport.logout",
    f"{_AUTH_PREFIX}/exchange/issue": "auth.transport.exchange.issue",
    f"{_AUTH_PREFIX}/exchange/redeem": "auth.transport.exchange.redeem",
}
_ALLOWED_DENIAL_REASONS = frozenset(
    {
        "transport_request_invalid",
        "transport_request_not_admitted",
        "transport_authentication_failed",
        "transport_rate_limited",
    }
)


class TransportRateLimited(Exception):
    """Generic bounded rate denial with a safe Retry-After value."""

    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("application auth transport rate limited")
        self.retry_after_seconds = max(1, min(retry_after_seconds, 3600))


class RequiredTransportDenialAuditUnavailable(RuntimeError):
    """A required denial event could not be committed."""


@dataclass(frozen=True)
class ProxyTrustPolicy:
    """One-hop forwarded-client contract with an exact direct-peer allowlist."""

    trusted_proxy_networks: tuple[
        ipaddress.IPv4Network | ipaddress.IPv6Network, ...
    ] = ()

    @classmethod
    def from_cidrs(cls, values: tuple[str, ...] | list[str]) -> "ProxyTrustPolicy":
        networks = []
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("trusted proxy CIDRs must be non-empty strings")
            try:
                network = ipaddress.ip_network(value.strip(), strict=True)
            except ValueError as exc:
                raise ValueError("invalid trusted proxy CIDR") from exc
            networks.append(network)
        if len(networks) > 32:
            raise ValueError("trusted proxy CIDR count exceeds 32")
        return cls(tuple(networks))

    def _is_trusted(self, address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        return any(address in network for network in self.trusted_proxy_networks)

    def resolve_client(
        self,
        *,
        direct_peer: str | None,
        headers: Mapping[str, str],
    ) -> str:
        try:
            peer = ipaddress.ip_address((direct_peer or "").strip())
        except ValueError as exc:
            raise TransportRequestDenied() from exc

        forwarded = headers.get("forwarded")
        forwarded_for = headers.get("x-forwarded-for")
        forwarded_proto = headers.get("x-forwarded-proto")
        has_forwarded = any(
            value is not None
            for value in (forwarded, forwarded_for, forwarded_proto)
        )

        if forwarded is not None:
            raise TransportRequestDenied()
        if has_forwarded:
            if not self._is_trusted(peer):
                raise TransportRequestDenied()
            if forwarded_for is None or forwarded_proto is None:
                raise TransportRequestDenied()
            if len(forwarded_for) > 255 or "," in forwarded_for:
                raise TransportRequestDenied()
            if len(forwarded_proto) > 32 or forwarded_proto.strip().lower() != "https":
                raise TransportRequestDenied()
            try:
                client = ipaddress.ip_address(forwarded_for.strip())
            except ValueError as exc:
                raise TransportRequestDenied() from exc
            return client.compressed

        if self._is_trusted(peer):
            # A configured proxy without its complete forwarding pair would
            # collapse every caller into one abuse key.
            raise TransportRequestDenied()
        return peer.compressed


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    audit_required: bool
    retry_after_seconds: int


@dataclass
class _RateWindow:
    window_number: int
    count: int = 0
    blocked_audit_reserved: bool = False


class BoundedFixedWindowRateLimiter:
    """Thread-safe per-process limiter with a strict live-key bound."""

    def __init__(
        self,
        *,
        requests_per_window: int = 20,
        window_seconds: int = 60,
        max_keys: int = 2048,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not 1 <= requests_per_window <= 10_000:
            raise ValueError("requests_per_window outside 1..10000")
        if not 1 <= window_seconds <= 3600:
            raise ValueError("window_seconds outside 1..3600")
        if not 1 <= max_keys <= 100_000:
            raise ValueError("max_keys outside 1..100000")
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._clock = clock
        self._entries: OrderedDict[str, _RateWindow] = OrderedDict()
        self._lock = threading.Lock()

    def check(self, key: str) -> RateLimitDecision:
        if not isinstance(key, str) or len(key) != 71 or not key.startswith("sha256:"):
            raise ValueError("rate-limit key must be one bounded hash")
        now = max(0.0, float(self._clock()))
        window_number = int(now // self.window_seconds)
        with self._lock:
            # Expired windows are never useful and must not consume key space.
            expired = [
                item_key
                for item_key, item in self._entries.items()
                if item.window_number != window_number
            ]
            for item_key in expired:
                self._entries.pop(item_key, None)

            item = self._entries.pop(key, None)
            if item is None:
                while len(self._entries) >= self.max_keys:
                    self._entries.popitem(last=False)
                item = _RateWindow(window_number=window_number)
            item.count += 1
            self._entries[key] = item

            if item.count <= self.requests_per_window:
                return RateLimitDecision(True, False, 0)

            audit_required = not item.blocked_audit_reserved
            item.blocked_audit_reserved = True
            remaining = ((window_number + 1) * self.window_seconds) - now
            return RateLimitDecision(
                False,
                audit_required,
                max(1, min(3600, math.ceil(remaining))),
            )

    def live_key_count(self) -> int:
        with self._lock:
            return len(self._entries)

    def release_blocked_audit_reservation(self, key: str) -> None:
        """Allow a later blocked request to retry an audit that did not commit."""

        with self._lock:
            item = self._entries.get(key)
            if item is not None:
                item.blocked_audit_reserved = False


@dataclass(frozen=True)
class TransportDenialEvent:
    action: str
    surface: str
    reason_code: str
    correlation_id: str
    client_reference_hash: str
    occurred_at: datetime


class TransportDenialAuditSink(Protocol):
    def record(self, event: TransportDenialEvent) -> None: ...


class PostgresTransportDenialAuditSink:
    """Append one metadata-only denial through the accepted audit table."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def record(self, event: TransportDenialEvent) -> None:
        try:
            with self._session_factory() as db:
                with db.begin():
                    for setting, value in (
                        ("statement_timeout", "5s"),
                        ("lock_timeout", "2s"),
                        ("idle_in_transaction_session_timeout", "5s"),
                        ("row_security", "on"),
                        ("app.current_practice_ref", TRANSPORT_AUDIT_PRACTICE),
                    ):
                        db.execute(
                            text("SELECT set_config(:setting, :value, true)"),
                            {"setting": setting, "value": value},
                        )
                    db.add(
                        ApplicationAuthAuditEvent(
                            practice_ref=TRANSPORT_AUDIT_PRACTICE,
                            user_ref=None,
                            current_backend_role=None,
                            event_type="auth.authorization_denied",
                            occurred_at=event.occurred_at,
                            correlation_id=event.correlation_id,
                            session_reference_hash=event.client_reference_hash,
                            surface=event.surface,
                            action=event.action,
                            resource_type="application_auth_transport",
                            policy_version=TRANSPORT_AUDIT_POLICY,
                            decision="denied",
                            reason_codes=[event.reason_code],
                            grant_reference_hash=None,
                            target_surface=None,
                            data_class="authored_synthetic",
                        )
                    )
        except SQLAlchemyError as exc:
            raise RequiredTransportDenialAuditUnavailable() from exc


@dataclass
class _RequestAdmission:
    action: str
    client_reference_hash: str
    correlation_id: str
    audit_required: bool = True
    audit_recorded: bool = False


class ApplicationAuthOperationalHardening:
    """Proxy, rate and required-denial-audit guard for the seven routes."""

    def __init__(
        self,
        *,
        proxy_policy: ProxyTrustPolicy,
        rate_limiter: BoundedFixedWindowRateLimiter,
        denial_audit_sink: TransportDenialAuditSink,
        client_hmac_key: bytes,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(client_hmac_key, bytes) or len(client_hmac_key) < 32:
            raise ValueError("client HMAC key must contain at least 32 bytes")
        self.proxy_policy = proxy_policy
        self.rate_limiter = rate_limiter
        self.denial_audit_sink = denial_audit_sink
        self._client_hmac_key = client_hmac_key
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _reference(self, value: str) -> str:
        digest = hmac.new(
            self._client_hmac_key,
            value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"sha256:{digest}"

    @staticmethod
    def _action(path: str) -> str:
        return _PATH_ACTIONS.get(path, "auth.transport.unknown")

    def admit(self, request: Request) -> None:
        direct_peer = request.client.host if request.client is not None else None
        provisional = self._reference(f"direct:{direct_peer or 'missing'}")
        admission = _RequestAdmission(
            action=self._action(request.url.path),
            client_reference_hash=provisional,
            correlation_id=f"correlation-transport-{secrets.token_hex(12)}",
        )
        request.state.application_auth_operational_hardening = self
        request.state.application_auth_admission = admission

        for name in ("forwarded", "x-forwarded-for", "x-forwarded-proto"):
            if len(request.headers.getlist(name)) > 1:
                raise TransportRequestDenied()

        client = self.proxy_policy.resolve_client(
            direct_peer=direct_peer,
            headers=request.headers,
        )
        admission.client_reference_hash = self._reference(f"client:{client}")
        decision = self.rate_limiter.check(admission.client_reference_hash)
        if not decision.allowed:
            admission.audit_required = decision.audit_required
            raise TransportRateLimited(decision.retry_after_seconds)

    def record_denial(self, request: Request, reason_code: str) -> bool:
        if reason_code not in _ALLOWED_DENIAL_REASONS:
            raise ValueError("unbounded transport denial reason")
        admission = getattr(request.state, "application_auth_admission", None)
        if not isinstance(admission, _RequestAdmission):
            raise RequiredTransportDenialAuditUnavailable()
        if not admission.audit_required or admission.audit_recorded:
            return False
        occurred_at = self._clock()
        if occurred_at.tzinfo is None:
            raise RequiredTransportDenialAuditUnavailable()
        event = TransportDenialEvent(
            action=admission.action,
            surface="all",
            reason_code=reason_code,
            correlation_id=admission.correlation_id,
            client_reference_hash=admission.client_reference_hash,
            occurred_at=occurred_at,
        )
        try:
            self.denial_audit_sink.record(event)
        except RequiredTransportDenialAuditUnavailable:
            if reason_code == "transport_rate_limited":
                self.rate_limiter.release_blocked_audit_reservation(
                    admission.client_reference_hash
                )
            raise
        admission.audit_recorded = True
        return True


__all__ = [
    "ApplicationAuthOperationalHardening",
    "BoundedFixedWindowRateLimiter",
    "PostgresTransportDenialAuditSink",
    "ProxyTrustPolicy",
    "RateLimitDecision",
    "RequiredTransportDenialAuditUnavailable",
    "TRANSPORT_AUDIT_PRACTICE",
    "TransportDenialAuditSink",
    "TransportDenialEvent",
    "TransportRateLimited",
]
