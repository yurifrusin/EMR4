"""Default-off provider-free HTTP boundary for Microsoft OIDC start/callback."""

from __future__ import annotations

import hashlib
import hmac
import html
import json
import re
import secrets
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Callable, Mapping
from urllib.parse import parse_qsl, parse_qs, urlsplit

from app.services.application_identity_oidc_adapter import (
    AuthorizationStart,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    ReturnTarget,
    Surface,
    TwoComponentOIDCAdapter,
)


CALLBACK_MEDIA_TYPE = "application/x-www-form-urlencoded"
MAX_CALLBACK_BODY_BYTES = 12 * 1024
MAX_CALLBACK_FIELDS = 4
MAX_START_REPLAYS = 128

_OPAQUE = re.compile(r"^[A-Za-z0-9._~-]{16,256}$")
_CSRF = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")
_CSP_NONCE = re.compile(r"^[A-Za-z0-9_-]{32,64}$")
_CALLBACK_KEYS = frozenset({"code", "state", "error", "error_description"})


class OIDCTransportRequestDenied(RuntimeError):
    """Origin, CSRF, or idempotency admission failed generically."""


class OIDCTransportRequestInvalid(RuntimeError):
    """Callback transport input was malformed or outside fixed bounds."""


class OIDCTransportUnavailable(RuntimeError):
    """Required bounded transport state could not be provided."""


@dataclass(frozen=True)
class OIDCBridgePage:
    html: str
    headers: Mapping[str, str]
    target_origin: str
    surface: Surface
    return_target: ReturnTarget


@dataclass(frozen=True)
class _StartReplay:
    request_reference: str
    state_reference: str
    response: AuthorizationStart


class OIDCStartCallbackTransport:
    """Exact-origin transport around the accepted two-component adapter."""

    def __init__(
        self,
        *,
        adapter: TwoComponentOIDCAdapter,
        surface_origins: Mapping[Surface, str],
        idempotency_hmac_key: bytes,
        nonce_source: Callable[[], str] | None = None,
        max_start_replays: int = MAX_START_REPLAYS,
    ) -> None:
        if not isinstance(adapter, TwoComponentOIDCAdapter):
            raise TypeError("OIDC transport requires the accepted adapter")
        origins = {Surface(key): value for key, value in surface_origins.items()}
        if set(origins) != set(Surface):
            raise ValueError("OIDC transport requires exactly three surface origins")
        if any(not _is_canonical_https_origin(value) for value in origins.values()):
            raise ValueError("OIDC transport surface origin is invalid")
        if not isinstance(idempotency_hmac_key, bytes) or len(idempotency_hmac_key) < 32:
            raise ValueError("OIDC transport idempotency key is invalid")
        if not 1 <= max_start_replays <= MAX_START_REPLAYS:
            raise ValueError("OIDC transport replay capacity is outside 1..128")
        self._adapter = adapter
        self._surface_origins = origins
        self._idempotency_hmac_key = bytes(idempotency_hmac_key)
        self._nonce_source = nonce_source or (lambda: secrets.token_urlsafe(32))
        self._max_start_replays = max_start_replays
        self._replays: OrderedDict[str, _StartReplay] = OrderedDict()
        self._lock = RLock()

    def require_origin(self, surface: Surface, supplied_origin: str | None) -> str:
        expected = self._surface_origins.get(Surface(surface))
        supplied = supplied_origin if isinstance(supplied_origin, str) else ""
        if expected is None or not hmac.compare_digest(supplied, expected):
            raise OIDCTransportRequestDenied()
        return expected

    @staticmethod
    def require_csrf(cookie_value: str | None, header_value: str | None) -> None:
        cookie = cookie_value if isinstance(cookie_value, str) else ""
        header = header_value if isinstance(header_value, str) else ""
        if (
            not _CSRF.fullmatch(cookie)
            or not _CSRF.fullmatch(header)
            or not hmac.compare_digest(cookie, header)
        ):
            raise OIDCTransportRequestDenied()

    def start(
        self,
        *,
        surface: Surface,
        return_target: ReturnTarget,
        origin: str | None,
        csrf_cookie: str | None,
        csrf_header: str | None,
        idempotency_key: str | None,
        now: datetime | None = None,
    ) -> AuthorizationStart:
        surface = Surface(surface)
        return_target = ReturnTarget(return_target)
        admitted_origin = self.require_origin(surface, origin)
        self.require_csrf(csrf_cookie, csrf_header)
        key = idempotency_key if isinstance(idempotency_key, str) else ""
        if not 16 <= len(key) <= 128 or not _OPAQUE.fullmatch(key):
            raise OIDCTransportRequestDenied()
        current = _aware_utc(now)
        key_reference = self._reference(f"idempotency:{key}")
        request_reference = self._reference(
            "request:"
            + "|".join((surface.value, return_target.value, admitted_origin))
        )
        with self._lock:
            self._discard_expired_locked(current)
            replay = self._replays.get(key_reference)
            if replay is not None:
                if not hmac.compare_digest(
                    replay.request_reference,
                    request_reference,
                ):
                    raise OIDCTransportRequestDenied()
                self._replays.move_to_end(key_reference)
                return replay.response
            if len(self._replays) >= self._max_start_replays:
                raise OIDCTransportUnavailable()

            response = self._adapter.create_authorization_flow(
                surface=surface,
                return_target=return_target,
                now=current,
            )
            raw_state = _authorization_state(response.authorization_uri)
            self._replays[key_reference] = _StartReplay(
                request_reference=request_reference,
                state_reference=self._reference(f"state:{raw_state}"),
                response=response,
            )
            return response

    def complete(
        self,
        *,
        body: bytes,
        content_type: str | None,
        now: datetime | None = None,
    ) -> OIDCBridgePage:
        auth_response = parse_microsoft_callback_form(body, content_type)
        state_reference = self._reference(f"state:{auth_response['state']}")
        try:
            completed = self._adapter.complete_authorization_flow(
                auth_response=auth_response,
                now=_aware_utc(now),
            )
        finally:
            self._discard_state_reference(state_reference)
        if (
            completed.authorization_granted
            or completed.session_created
            or completed.product_data_released
        ):
            raise OIDCTransportUnavailable()
        expected_origin = self._surface_origins.get(completed.surface)
        if expected_origin is None or not hmac.compare_digest(
            completed.origin,
            expected_origin,
        ):
            raise OIDCTransportUnavailable()
        return self._bridge_page(
            origin=expected_origin,
            surface=completed.surface,
            return_target=completed.return_target,
        )

    def replay_count(self) -> int:
        with self._lock:
            return len(self._replays)

    def _reference(self, value: str) -> str:
        return "hmac-sha256:" + hmac.new(
            self._idempotency_hmac_key,
            value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _discard_expired_locked(self, now: datetime) -> None:
        expired = [
            key
            for key, item in self._replays.items()
            if item.response.attempt_expires_at <= now
        ]
        for key in expired:
            self._replays.pop(key, None)

    def _discard_state_reference(self, state_reference: str) -> None:
        with self._lock:
            matched = [
                key
                for key, item in self._replays.items()
                if hmac.compare_digest(item.state_reference, state_reference)
            ]
            for key in matched:
                self._replays.pop(key, None)

    def _bridge_page(
        self,
        *,
        origin: str,
        surface: Surface,
        return_target: ReturnTarget,
    ) -> OIDCBridgePage:
        nonce = self._nonce_source()
        if not isinstance(nonce, str) or not _CSP_NONCE.fullmatch(nonce):
            raise OIDCTransportUnavailable()
        message = {
            "type": "emr4.oidc.callback",
            "status": "authentication_verified",
            "surface": surface.value,
            "return_target": return_target.value,
        }
        encoded_message = _script_json(message)
        encoded_origin = _script_json(origin)
        escaped_nonce = html.escape(nonce, quote=True)
        page = (
            "<!doctype html><html lang=\"en\"><head>"
            "<meta charset=\"utf-8\"><meta name=\"viewport\" "
            "content=\"width=device-width,initial-scale=1\">"
            "<title>Raisa authentication</title></head><body>"
            "<p>Authentication check complete. Return to Raisa.</p>"
            f"<script nonce=\"{escaped_nonce}\">"
            f"const message={encoded_message};const targetOrigin={encoded_origin};"
            "const receiver=window.opener||(window.parent!==window?window.parent:null);"
            "if(receiver){receiver.postMessage(message,targetOrigin);}window.close();"
            "</script></body></html>"
        )
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
            ),
            "Content-Security-Policy": (
                "default-src 'none'; "
                f"script-src 'nonce-{nonce}'; "
                "style-src 'none'; img-src 'none'; connect-src 'none'; "
                "object-src 'none'; base-uri 'none'; form-action 'none'; "
                f"frame-ancestors {origin}"
            ),
        }
        return OIDCBridgePage(
            html=page,
            headers=headers,
            target_origin=origin,
            surface=surface,
            return_target=return_target,
        )


def parse_microsoft_callback_form(
    body: bytes,
    content_type: str | None,
) -> dict[str, str]:
    if not isinstance(body, bytes) or not body or len(body) > MAX_CALLBACK_BODY_BYTES:
        raise OIDCTransportRequestInvalid()
    media_type = (content_type or "").split(";", 1)[0].strip().lower()
    if media_type != CALLBACK_MEDIA_TYPE:
        raise OIDCTransportRequestInvalid()
    try:
        decoded = body.decode("utf-8", errors="strict")
        pairs = parse_qsl(
            decoded,
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=MAX_CALLBACK_FIELDS,
            encoding="utf-8",
            errors="strict",
        )
    except (UnicodeError, ValueError):
        raise OIDCTransportRequestInvalid() from None
    keys = [key for key, _ in pairs]
    if (
        not pairs
        or len(pairs) > MAX_CALLBACK_FIELDS
        or len(set(keys)) != len(keys)
        or not set(keys) <= _CALLBACK_KEYS
        or "state" not in keys
    ):
        raise OIDCTransportRequestInvalid()
    return dict(pairs)


def _authorization_state(authorization_uri: str) -> str:
    try:
        values = parse_qs(
            urlsplit(authorization_uri).query,
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=16,
        )
        states = values["state"]
    except (KeyError, ValueError):
        raise OIDCTransportUnavailable() from None
    if len(states) != 1 or not _OPAQUE.fullmatch(states[0]):
        raise OIDCTransportUnavailable()
    return states[0]


def _is_canonical_https_origin(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or any(ord(character) < 33 or ord(character) > 126 for character in value)
    ):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.hostname
        and parsed.netloc == parsed.netloc.lower()
        and parsed.hostname == parsed.hostname.lower()
        and parsed.username is None
        and parsed.password is None
        and parsed.path == ""
        and not parsed.query
        and not parsed.fragment
        and value == f"https://{parsed.netloc}"
        and (port is None or 1 <= port <= 65535)
    )


def _script_json(value: object) -> str:
    return (
        json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def _aware_utc(value: datetime | None) -> datetime:
    candidate = value or datetime.now(timezone.utc)
    if candidate.tzinfo is None:
        raise ValueError("OIDC transport clock must be timezone-aware")
    return candidate.astimezone(timezone.utc)


__all__ = [
    "CALLBACK_MEDIA_TYPE",
    "MAX_CALLBACK_BODY_BYTES",
    "MAX_CALLBACK_FIELDS",
    "MAX_START_REPLAYS",
    "OIDCBridgePage",
    "OIDCAuthenticationFailed",
    "OIDCStartCallbackTransport",
    "OIDCTemporarilyUnavailable",
    "OIDCTransportRequestDenied",
    "OIDCTransportRequestInvalid",
    "OIDCTransportUnavailable",
    "parse_microsoft_callback_form",
]
