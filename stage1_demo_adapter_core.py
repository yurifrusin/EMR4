"""Inert core for a future loopback-only Stage 1 HTTP/session adapter.

This module performs no import of the application, I/O or command effect. The
reviewed route must authenticate the cookie, look up SessionBinding server-side,
call admit_action, and bridge its result to the existing typed backend routes.
It must never serialise SessionBinding or signed proposal evidence to a browser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hmac
import json
from typing import Any, Literal


MAX_BODY_BYTES = 4096
ALLOWED_ACTIONS = {
    "patient": frozenset({"refresh", "reconcile", "submit_request"}),
    "staff": frozenset({"refresh", "diary", "reconcile", "propose_create", "confirm_create", "propose_move", "confirm_move"}),
}


class AdapterRejected(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class SessionBinding:
    """Server-created binding; no field here is accepted as a client role claim."""

    persona: Literal["patient", "staff"]
    session_id: str = field(repr=False)
    csrf: str = field(repr=False)
    practice_id: str = field(repr=False)
    request_id: str = field(repr=False)
    patient_id: str = field(repr=False)
    patient_capability: str | None = field(default=None, repr=False)
    staff_user_id: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class AdmittedAction:
    action: str
    body: dict[str, Any] | None
    idempotency_key: str | None
    binding: SessionBinding = field(repr=False)


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AdapterRejected("DUPLICATE_FIELD")
        result[key] = value
    return result


def admit_action(
    *,
    profile: str,
    enabled: bool,
    listener_host: str,
    request_host: str,
    origin: str | None,
    expected_origin: str,
    content_type: str,
    csrf_header: str | None,
    body_bytes: bytes,
    binding: SessionBinding | None,
) -> AdmittedAction:
    """Fail closed before any backend port receives an action.

    Cookie issuance/flags, expiry, session lookup, network binding, current DB
    actor checks, typed payload construction, proposal storage and readback are
    responsibilities of the separately reviewed HTTP route. This function
    cannot by itself establish those facts or authorise a backend mutation.
    """
    if profile != "STAGE1_SYNTHETIC_DEMO" or enabled is not True:
        raise AdapterRejected("PROFILE_CLOSED")
    if listener_host not in {"127.0.0.1", "::1"} or request_host != listener_host:
        raise AdapterRejected("LOOPBACK_REQUIRED")
    if not origin or origin != expected_origin or not expected_origin.startswith(
        ("http://127.0.0.1:", "http://[::1]:")
    ):
        raise AdapterRejected("ORIGIN_INVALID")
    if content_type != "application/json" or type(body_bytes) is not bytes or len(body_bytes) > MAX_BODY_BYTES:
        raise AdapterRejected("BODY_INVALID")
    if binding is None or binding.persona not in ALLOWED_ACTIONS:
        raise AdapterRejected("SESSION_INVALID")
    if not csrf_header or not hmac.compare_digest(csrf_header, binding.csrf):
        raise AdapterRejected("CSRF_INVALID")
    try:
        raw = json.loads(body_bytes.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterRejected("BODY_INVALID") from exc
    if type(raw) is not dict or set(raw) != {"method", "action", "body", "idempotency_key"}:
        raise AdapterRejected("BODY_INVALID")
    action, method, payload, key = (raw[name] for name in ("action", "method", "body", "idempotency_key"))
    if type(action) is not str or action not in ALLOWED_ACTIONS[binding.persona]:
        raise AdapterRejected("ACTION_UNAVAILABLE")
    if method != ("read" if action in {"refresh", "diary", "reconcile", "propose_create", "propose_move"} else "write"):
        raise AdapterRejected("METHOD_INVALID")
    if action in {"refresh", "diary", "reconcile"}:
        if payload is not None or key is not None:
            raise AdapterRejected("BODY_INVALID")
    elif type(payload) is not dict:
        raise AdapterRejected("BODY_INVALID")
    if method == "write":
        if type(key) is not str or not 8 <= len(key) <= 128 or any(ch not in "0123456789abcdef-" for ch in key):
            raise AdapterRejected("IDEMPOTENCY_INVALID")
    elif key is not None:
        raise AdapterRejected("BODY_INVALID")
    if binding.persona == "patient" and (not binding.patient_capability or binding.staff_user_id):
        raise AdapterRejected("SESSION_INVALID")
    if binding.persona == "staff" and (not binding.staff_user_id or binding.patient_capability):
        raise AdapterRejected("SESSION_INVALID")
    return AdmittedAction(action=action, body=payload, idempotency_key=key, binding=binding)
