"""STOPPED/default-off owner first-weekly-window bridge.

Inert source candidate only. Core-v2 context ABI, fixed trusted transports and
separate admission are dependencies. No installation, runtime or bookability
claim. Public CREATE references are selectors; only backend context is resource
truth. Tokens, authority, signed evidence and canonical bodies remain private.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import secrets
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from stage1_owner_onboarding import COOKIE, OwnerAuthority, OwnerController
from stage1_seeded_login import _Denied, _json, _reply

MAX_RESPONSE_BYTES = 32768
_UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_CLOCK = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]\Z")
_CURRENT_CLOCK = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:\.[0-9]{1,6})?\Z")
_MAX = 9223372036854775807
_FIELDS = frozenset(("weekday", "start_time", "end_time", "slot_duration_minutes"))
_BODY = _FIELDS | {"practitioner_id", "practitioner_create_command_id",
    "practitioner_create_command_key", "location_id", "practice_timezone"}
_CONTEXT = frozenset(("schema_version", "practice_id", "practitioner_id",
    "practitioner_create_command_id", "practitioner_create_command_key", "location_id",
    "location_create_command_id", "location_create_command_key", "practice_timezone",
    "practitioner_active", "location_active", "role", "authority_generation"))
_DRAFT = frozenset(("command_id", "command_key", "canonicalization_version", "body",
    "body_digest", "context_digest", "role", "authority_generation", "expires_at"))
_RECEIPT = frozenset(("schema_version", "command_id", "command_key", "practice_id",
    "practitioner_id", "location_id", "schedule_id", "body", "body_digest", "context_digest",
    "actor_account_id", "actor_membership_id", "actor_user_id", "role", "authority_generation",
    "audit_event_id", "outbox_event_id", "committed_at"))
_CURRENT = frozenset(("schedule_id", "practitioner_id", "location_id", "weekday",
    "start_time", "end_time", "slot_duration_minutes", "practice_timezone",
    "practitioner_active", "location_active"))
_REFUSALS = {
    (400, "FIRST_WEEKLY_WINDOW_CONTEXT_INVALID"),
    (400, "FIRST_WEEKLY_WINDOW_INVALID"), (400, "FIRST_WEEKLY_WINDOW_CREATE_INVALID"),
    (400, "FIRST_WEEKLY_WINDOW_COMMAND_KEY_INVALID"),
    (400, "FIRST_WEEKLY_WINDOW_CONFIRMATION_INVALID"),
    (401, "FIRST_WEEKLY_WINDOW_AUTHENTICATION_REQUIRED"),
    (403, "FIRST_WEEKLY_WINDOW_CREATE_DENIED"),
    (404, "FIRST_WEEKLY_WINDOW_CREATE_NOT_FOUND"),
    (409, "FIRST_WEEKLY_WINDOW_CREATE_CONFLICT"),
    (409, "FIRST_WEEKLY_WINDOW_CONFLICT"),
    (409, "FIRST_WEEKLY_WINDOW_CONFIRMATION_INVALID"),
}


@dataclass(frozen=True, repr=False)
class FirstWeeklyWindowBinding:
    # Trusted fixed-route callbacks only; no caller URL, principal or secret.
    context: object = None
    prepare: object = None
    confirm: object = None
    receipt: object = None
    ends_at: datetime | None = None
    enabled: bool = False


def validate_optional_binding(binding):
    if binding is None:
        return False
    if type(binding) is not FirstWeeklyWindowBinding or type(binding.enabled) is not bool:
        raise ValueError("FIRST_WEEKLY_WINDOW_BINDING_INVALID")
    if not binding.enabled:
        if any(getattr(binding, k) is not None for k in ("context", "prepare", "confirm", "receipt", "ends_at")):
            raise ValueError("FIRST_WEEKLY_WINDOW_DISABLED_BINDING_INVALID")
        return False
    if (any(not callable(getattr(binding, k)) for k in ("context", "prepare", "confirm", "receipt"))
            or type(binding.ends_at) is not datetime or binding.ends_at.tzinfo is None
            or binding.ends_at.utcoffset().total_seconds() != 0):
        raise ValueError("FIRST_WEEKLY_WINDOW_BINDING_INVALID")
    return True


class _Invalid(Exception):
    pass


class _Uncertain(Exception):
    pass


class _Refused(Exception):
    def __init__(self, code):
        self.code = code


def _uuid(v):
    return type(v) is str and _UUID.fullmatch(v) is not None


def _integer(v, low=1, high=_MAX):
    return type(v) is int and low <= v <= high


def _digest(v):
    return type(v) is str and _HEX.fullmatch(v) is not None


def _utc(v, draft=False):
    if type(v) is not str or not 1 <= len(v) <= 64:
        raise _Invalid()
    try:
        if draft:
            result = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            if result.strftime("%Y-%m-%dT%H:%M:%S.%fZ") != v:
                raise _Invalid()
        else:
            result = datetime.fromisoformat(v[:-1] + "+00:00" if v.endswith("Z") else v)
        if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
            raise _Invalid()
        return result
    except (ValueError, OverflowError):
        raise _Invalid() from None


def _zone(v):
    if type(v) is not str or not re.fullmatch(r"[A-Za-z0-9._+/-]{1,50}", v):
        raise _Invalid()
    try:
        ZoneInfo(v)
    except (ZoneInfoNotFoundError, ValueError):
        raise _Invalid() from None
    return v


def _fields(v):
    if (type(v) is not dict or set(v) != _FIELDS or not _integer(v["weekday"], 0, 6)
            or any(type(v[k]) is not str or not _CLOCK.fullmatch(v[k]) for k in ("start_time", "end_time"))
            or not _integer(v["slot_duration_minutes"], 1, 1440)):
        raise _Invalid()
    def minutes(s):
        return int(s[:2]) * 60 + int(s[3:])
    width = minutes(v["end_time"]) - minutes(v["start_time"])
    if width <= 0 or v["slot_duration_minutes"] > width:
        raise _Invalid()
    return dict(v)


def _body(v):
    if type(v) is not dict or set(v) != _BODY:
        raise _Invalid()
    _fields({k: v[k] for k in _FIELDS})
    if any(not _uuid(v[k]) for k in ("practitioner_id", "practitioner_create_command_id",
            "practitioner_create_command_key", "location_id")):
        raise _Invalid()
    _zone(v["practice_timezone"])
    return dict(v)


def _body_digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(",", ":")).encode("utf-8", errors="strict")).hexdigest()


def _scope(a):
    return (a.account_id, a.membership_id, a.user_id, a.practice_id)


class FirstWeeklyWindowBridge:
    def __init__(self, owner, binding):
        if (type(owner) is not OwnerController or not validate_optional_binding(binding)
                or owner.binding.private_owner_current is None
                or not datetime.now(timezone.utc) < binding.ends_at <= owner.binding.ends_at):
            raise ValueError("FIRST_WEEKLY_WINDOW_OWNER_BINDING_INVALID")
        self.owner, self.binding, self._closed = owner, binding, False
        self.contexts = {}
        self.pending = {}

    def _active(self):
        if self._closed or self.binding.enabled is not True or datetime.now(timezone.utc) >= self.binding.ends_at:
            raise _Denied()

    def _invalidate(self, key, value):
        self.contexts.pop(key, None)
        for r in self.pending.values():
            if r["owner_key"] == key and r["owner"] is value:
                r.update(confirm=None, draft_current=False)
        # Attempted/uncertain keys and immutable receipts are never rearmed.

    def _abandon_prepared(self, key, value, a):
        # Called only while the existing per-owner lock is held. A positively
        # validated prepare reply proves no confirmation attempt by this bridge.
        # Unknown/incomplete prepares and ALL attempted confirmations survive.
        for (scope, _), r in self.pending.items():
            if (scope == _scope(a) and r["owner_key"] == key and r["owner"] is value
                    and r["prepare_complete"] is True and r["attempted"] is False
                    and r["receipt"] is None and not r["resolved"] and not r["abandoned"]):
                r.update(abandoned=True, confirm=None, draft_current=False)
        # Historical keys, bodies and draft facts remain; abandoned != committed.

    def _context(self, key, value):
        self._active()
        a, same_owner, read_owner = self.owner.practitioner_context(key, value)
        for (scope, _), r in self.pending.items():
            if scope == _scope(a) and (r["authority"] != a or r["owner"] is not value
                    or r["owner_key"] != key or r["csrf"] != value.csrf):
                r.update(confirm=None, draft_current=False)
        def same():
            self._active()
            same_owner()
            return True
        async def current():
            same()
            await read_owner()
            same()
            return True
        return a, same, current

    async def _exchange(self, action, value, same, current, **kwargs):
        same()
        await current()
        same()
        response = await getattr(self.binding, action)(tenant_bearer=value.tenant,
            current=current, local_current=same, **kwargs)
        same()
        await current()
        same()
        raw = response.content
        if (type(raw) is not bytes or not 0 < len(raw) <= MAX_RESPONSE_BYTES
                or response.headers.get("content-type", "").split(";")[0] != "application/json"
                or response.headers.get("cache-control", "").lower() != "no-store"):
            raise _Uncertain()
        result = _json(raw.decode("utf-8", errors="strict"))
        same()
        if response.status_code != 200:
            if (type(result) is dict and set(result) == {"detail"} and type(result["detail"]) is str
                    and (response.status_code, result["detail"]) in _REFUSALS):
                raise _Refused(result["detail"])
            raise _Uncertain()
        return result

    def _checked_context(self, result, a, selectors):
        if (type(result) is not dict or set(result) != _CONTEXT
                or result["schema_version"] != "practitioner.first_weekly_window.context.v1"
                or result["practice_id"] != a.practice_id or result["role"] != "PracticeOwner"
                or type(result["authority_generation"]) is not int
                or result["authority_generation"] != a.authority_generation
                or result["practitioner_active"] is not True or result["location_active"] is not True
                or any(not _uuid(result[k]) for k in ("practice_id", "practitioner_id",
                    "practitioner_create_command_id", "practitioner_create_command_key", "location_id",
                    "location_create_command_id", "location_create_command_key"))
                or any(result[k] != selectors[k] for k in selectors)):
            raise _Invalid()
        _zone(result["practice_timezone"])
        return dict(result)

    async def _fresh_context(self, stored, a, value, same, current):
        if (self.contexts.get(stored["owner_key"]) is not stored
                or stored["owner"] is not value or stored["authority"] != a or stored["csrf"] != value.csrf):
            raise _Denied()
        result = await self._exchange("context", value, same, current, body=stored["selectors"])
        checked = self._checked_context(result, a, stored["selectors"])
        if checked != stored["facts"]:
            raise _Denied()
        return checked

    def _receipt(self, result, a, command_key, r=None):
        if (type(result) is not dict or set(result) != _RECEIPT
                or result["schema_version"] != "practitioner.first_weekly_window.receipt.v1"
                or result["command_key"] != command_key or result["role"] != "PracticeOwner"
                or any(not _uuid(result[k]) for k in ("command_id", "command_key", "practice_id",
                    "practitioner_id", "location_id", "schedule_id", "actor_account_id",
                    "actor_membership_id", "actor_user_id", "audit_event_id", "outbox_event_id"))
                or (result["practice_id"], result["actor_account_id"], result["actor_membership_id"], result["actor_user_id"])
                    != (a.practice_id, a.account_id, a.membership_id, a.user_id)
                or not _integer(result["authority_generation"])
                or not _digest(result["body_digest"]) or not _digest(result["context_digest"])):
            raise _Invalid()
        body = _body(result["body"])
        if (result["practitioner_id"] != body["practitioner_id"] or result["location_id"] != body["location_id"]
                or result["body_digest"] != _body_digest(body)):
            raise _Invalid()
        _utc(result["committed_at"])
        if r is not None:
            if body != r["body"] or result["body_digest"] != r["body_digest"]:
                raise _Invalid()
            if r["draft"] is not None and any(result[k] != r["draft"][k]
                    for k in ("command_id", "command_key", "body_digest", "context_digest", "authority_generation")):
                raise _Invalid()
            if r["receipt"] is not None and r["receipt"] != result:
                raise _Invalid()
        return dict(result)

    @staticmethod
    def _public_receipt(r):
        return {k: r[k] for k in ("command_key", "command_id", "schedule_id", "body_digest",
            "context_digest", "committed_at")}

    def _prepared(self, result, a, r):
        if (type(result) is not dict or set(result) != {"state", "draft", "receipt", "confirmation_evidence"}
                or result["state"] != "prepared" or result["receipt"] is not None):
            raise _Invalid()
        d, evidence = result["draft"], result["confirmation_evidence"]
        if (type(d) is not dict or set(d) != _DRAFT or d["command_key"] != r["command_key"]
                or not _uuid(d["command_id"]) or d["body"] != r["body"]
                or d["canonicalization_version"] != "practitioner.first_weekly_window.body.v1"
                or d["body_digest"] != r["body_digest"] or not _digest(d["context_digest"])
                or d["role"] != "PracticeOwner" or type(d["authority_generation"]) is not int
                or d["authority_generation"] != a.authority_generation):
            raise _Invalid()
        expiry = _utc(d["expires_at"], draft=True)
        payload = {"schema_version": "practitioner.first_weekly_window.confirmation.v1",
            "canonicalization_version": "practitioner.first_weekly_window.body.v1",
            "account_id": a.account_id, "membership_id": a.membership_id, "user_id": a.user_id,
            "practice_id": a.practice_id, "role": "PracticeOwner", "authority_generation": a.authority_generation,
            **{k: d[k] for k in ("command_id", "command_key", "body_digest", "context_digest", "expires_at")}}
        if (type(evidence) is not dict or set(evidence) != {"schema_version", "purpose", "payload", "signature"}
                or evidence["schema_version"] != "bernie.confirmation_evidence.v1"
                or evidence["purpose"] != "practitioner_first_weekly_window_confirm"
                or not _digest(evidence["signature"]) or type(evidence["payload"]) is not dict
                or evidence["payload"].keys() != payload.keys()
                or any(type(evidence["payload"][k]) is not type(v) or evidence["payload"][k] != v for k, v in payload.items())
                or len(json.dumps(evidence, ensure_ascii=False).encode("utf-8")) > 8192):
            raise _Invalid()
        if r["draft"] is not None and r["draft"] != d:
            raise _Invalid()
        r.update(draft=dict(d), draft_current=True, confirm={"command_key": d["command_key"],
            "command_id": d["command_id"], "body_digest": d["body_digest"], "context_digest": d["context_digest"],
            "signed_confirmation_evidence": evidence, "confirmed": True}, prepare_complete=True)
        return {"state": "prepared", "draft": {"command_key": d["command_key"], "command_id": d["command_id"],
            "body": {k: d["body"][k] for k in _FIELDS}, "practice_timezone": d["body"]["practice_timezone"],
            "body_digest": d["body_digest"], "context_digest": d["context_digest"], "expires_at": d["expires_at"],
            "can_confirm": datetime.now(timezone.utc) < expiry}}

    def _recovery(self, result, a, command_key, r):
        if type(result) is not dict or set(result) != {"receipt", "readback"}:
            raise _Invalid()
        receipt = self._receipt(result["receipt"], a, command_key, r)
        rb = result["readback"]
        if (type(rb) is not dict or set(rb) != {"status", "expected", "current"}
                or rb["status"] not in ("matches_created", "diverged", "missing")
                or _body(rb["expected"]) != receipt["body"]):
            raise _Invalid()
        c = rb["current"]
        if c is None:
            if rb["status"] != "missing":
                raise _Invalid()
            public_current = None
        else:
            if (type(c) is not dict or set(c) != _CURRENT or c["schedule_id"] != receipt["schedule_id"]
                    or c["practitioner_id"] != receipt["practitioner_id"]
                    or not _uuid(c["schedule_id"]) or not _uuid(c["practitioner_id"])
                    or c["location_id"] is not None and not _uuid(c["location_id"])
                    or not _integer(c["weekday"], 0, 6)
                    or any(type(c[k]) is not str or not _CURRENT_CLOCK.fullmatch(c[k]) for k in ("start_time", "end_time"))
                    or c["slot_duration_minutes"] is not None and not _integer(c["slot_duration_minutes"], 1, 1440)
                    or any(type(c[k]) not in (bool, type(None)) for k in ("practitioner_active", "location_active"))
                    or c["practice_timezone"] is not None and type(c["practice_timezone"]) is not str):
                raise _Invalid()
            matches = (c["start_time"] == receipt["body"]["start_time"] + ":00"
                and c["end_time"] == receipt["body"]["end_time"] + ":00"
                and all(c[k] == receipt["body"][k] and type(c[k]) is type(receipt["body"][k])
                    for k in {"weekday", "slot_duration_minutes", "location_id", "practice_timezone"})
                and c["practitioner_active"] is True and c["location_active"] is True)
            if rb["status"] != ("matches_created" if matches else "diverged"):
                raise _Invalid()
            public_current = {k: c[k] for k in _FIELDS | {"practice_timezone", "practitioner_active", "location_active"}}
        if r is not None:
            r.update(receipt=receipt, resolved=True, confirm=None, draft_current=False)
        return {"state": "committed", "receipt": self._public_receipt(receipt),
            "readback": {"status": rb["status"],
                "expected": {k: receipt["body"][k] for k in _FIELDS | {"practice_timezone"}}, "current": public_current}}

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, "")
        value = self.owner.sessions.get(key)
        r, command_key, dispatched = None, None, False
        try:
            self._active()
            if (value is None or action not in ("context", "prepare", "confirm", "receipt")
                    or request.method != "POST" or request.url.query
                    or request.headers.get("authorization") is not None
                    or request.headers.get("origin") != self.owner.origin
                    or request.headers.get("content-type") != "application/json"):
                raise _Denied()
            async with value.lock:
                a, same, current = self._context(key, value)
                if not secrets.compare_digest(request.headers.get("x-csrf-token", ""), value.csrf):
                    raise _Denied()
                chunks, size = [], 0
                same()
                async for chunk in request.stream():
                    same()
                    size += len(chunk)
                    if size > 4096:
                        raise _Invalid()
                    chunks.append(chunk)
                same()
                body = _json(b"".join(chunks).decode("utf-8", errors="strict"))
                if type(body) is not dict:
                    raise _Invalid()
                if action == "context":
                    refs = {"practitioner_create_command_key", "location_create_command_key"}
                    if set(body) != refs or any(not _uuid(body[k]) for k in refs):
                        raise _Invalid()
                    self._abandon_prepared(key, value, a)
                    self._invalidate(key, value)
                    if len(self.contexts) >= 256:
                        raise _Denied()
                    result = await self._exchange(action, value, same, current, body=body)
                    facts = self._checked_context(result, a, body)
                    same()
                    context_ref = secrets.token_hex(32)
                    self.contexts[key] = {"ref": context_ref, "owner_key": key, "selectors": dict(body), "facts": facts,
                        "authority": a, "owner": value, "csrf": value.csrf}
                    return _reply({"state": "context_ready", "context_ref": context_ref,
                        "practice_timezone": facts["practice_timezone"], **body})
                if not _uuid(body.get("command_key")):
                    raise _Invalid()
                command_key = body["command_key"]
                r = self.pending.get((_scope(a), command_key))
                if action == "prepare":
                    if (set(body) != {"command_key", "context_ref", "body"}
                            or not _digest(body["context_ref"])):
                        raise _Invalid()
                    selected = self.contexts.get(key)
                    if selected is None or selected["ref"] != body["context_ref"]:
                        raise _Denied()
                    fields = _fields(body["body"])
                    facts = await self._fresh_context(selected, a, value, same, current)
                    native_body = {**fields, **{k: facts[k] for k in ("practitioner_id",
                        "practitioner_create_command_id", "practitioner_create_command_key", "location_id", "practice_timezone")}}
                    fingerprint = json.dumps(native_body, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
                    if r is None:
                        self._abandon_prepared(key, value, a)
                    if any(scope == _scope(a) and not other["resolved"] and not other["abandoned"] and other_key != command_key
                            for (scope, other_key), other in self.pending.items()):
                        raise _Uncertain()
                    if r is None:
                        if len(self.pending) >= 256:
                            raise _Denied()
                        r = {"command_key": command_key, "body": native_body, "body_digest": _body_digest(native_body),
                            "fingerprint": fingerprint, "selected": selected, "authority": a, "owner": value,
                            "owner_key": key, "csrf": value.csrf, "attempted": False, "prepare_complete": False,
                            "resolved": False, "abandoned": False, "draft_current": False, "draft": None, "confirm": None, "receipt": None}
                        self.pending[(_scope(a), command_key)] = r
                    elif (r["fingerprint"] != fingerprint or r["authority"] != a or r["owner"] is not value
                            or r["csrf"] != value.csrf or r["attempted"] or r["resolved"] or r["abandoned"] or r["receipt"] is not None
                            or r["prepare_complete"] and not r["draft_current"]):
                        raise _Uncertain()
                    same()
                    dispatched = True
                    result = await self._exchange(action, value, same, current,
                        body={"command_key": command_key, "body": r["body"]})
                    same()
                    if type(result) is dict and result.get("state") == "committed":
                        if (set(result) != {"state", "draft", "receipt", "confirmation_evidence"}
                                or result["draft"] is not None or result["confirmation_evidence"] is not None):
                            raise _Invalid()
                        receipt = self._receipt(result["receipt"], a, command_key, r)
                        r.update(receipt=receipt, confirm=None, draft_current=False)
                        recovery = await self._exchange("receipt", value, same, current, command_key=command_key)
                        same()
                        return _reply(self._recovery(recovery, a, command_key, r))
                    return _reply(self._prepared(result, a, r))
                if action == "confirm":
                    expected_keys = {"command_key", "command_id", "body_digest", "context_digest", "confirmed"}
                    if (set(body) != expected_keys or body["confirmed"] is not True or r is None
                            or r["attempted"] or r["abandoned"] or not r["draft_current"] or r["confirm"] is None
                            or r["authority"] != a or r["owner"] is not value or r["csrf"] != value.csrf
                            or any(type(body[k]) is not type(r["confirm"][k]) or body[k] != r["confirm"][k] for k in body)):
                        raise _Denied()
                    if datetime.now(timezone.utc) >= _utc(r["draft"]["expires_at"], draft=True):
                        raise _Denied()
                    r["attempted"] = True  # Consume before the first confirmation await.
                    r["draft_current"] = False
                    retained_confirm, r["confirm"] = r["confirm"], None
                    await self._fresh_context(r["selected"], a, value, same, current)
                    same()
                    dispatched = True
                    result = await self._exchange(action, value, same, current, body=retained_confirm)
                    same()
                    receipt = self._receipt(result, a, command_key, r)
                    r.update(receipt=receipt)
                    # One fresh read of the SAME key; never resend confirmation.
                    # Failed/cancelled read leaves this attempted record unresolved.
                    recovery = await self._exchange("receipt", value, same, current, command_key=command_key)
                    same()
                    return _reply(self._recovery(recovery, a, command_key, r))
                if set(body) != {"command_key"}:
                    raise _Invalid()
                result = await self._exchange("receipt", value, same, current, command_key=command_key)
                same()
                return _reply(self._recovery(result, a, command_key, r))
        except asyncio.CancelledError:
            if value is not None:
                self._invalidate(key, value)
            raise
        except _Refused as error:
            if value is not None:
                self._invalidate(key, value)
            if dispatched or action == "receipt":
                return _reply({"state": "uncertain", "command_key": command_key,
                    "detail": "Check this same working-hours reference before any new save."}, 409)
            return _reply({"state": "refused", "detail": "Working hours unavailable; check fresh owner and resource facts."}, 409)
        except Exception:
            if value is not None:
                self._invalidate(key, value)
            if dispatched or action == "receipt":
                return _reply({"state": "uncertain", "command_key": command_key,
                    "detail": "The result is uncertain. Check this same reference; do not submit another save."}, 503)
            return _reply({"detail": "Working hours are unavailable. Check the current owner account."}, 403)

    async def close(self):
        self._closed = True
        self.contexts.clear()
        for r in self.pending.values():
            r.update(confirm=None, draft_current=False)
        # Keep original keys/receipts for this object's remaining lifetime; no rearm.
