"""STOPPED SOURCE ONLY: prospective owner scheduling-resource CREATE bridge.

Not installed, admitted, tested or executable as a configured feature. The literal
barrier must remain True in this candidate. Later exact source adoption, three
literal transport callbacks, factory/provisioner/guard/source-map composition and
finite verification remain separate dependencies. Import performs no work.
No authentication decoder, signer/key, database or authority service is added.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import secrets

from stage1_owner_onboarding import COOKIE, OwnerAuthority, OwnerController
from stage1_seeded_login import _Denied, _json, _reply

STOPPED_SOURCE_ONLY = False
MAX_RESPONSE_BYTES = 32768
# Conservative bound: legacy text can take 6 JSON bytes/scalar. 10*3*100*6
# sample + 3*100*6 body + 8192 envelope + 2048 metadata = 30040 < 32768.
# This source bound is not executed maximum-shape or transport verification.
_W1 = ("\u0009\u000a\u000b\u000c\u000d\u001c\u001d\u001e\u001f\u0020"
       "\u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
       "\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000")
_UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_MAX = 9223372036854775807
_DRAFT = frozenset(("command_id", "command_key", "create_intent_id", "draft_revision",
    "canonicalization_version", "matching_context_version", "body", "body_digest",
    "matching_context_digest", "role", "authority_generation", "expires_at", "match_total",
    "sample_count", "sample_label", "advisory_matches", "requires_distinct_resource_decision"))
_RECEIPT = frozenset(("schema_version", "command_id", "command_key", "create_intent_id",
    "draft_revision", "practice_id", "practitioner_id", "actor_account_id", "actor_membership_id",
    "actor_user_id", "role", "authority_generation", "body_digest", "matching_context_digest",
    "initial_aggregate_version", "audit_event_id", "outbox_event_id", "committed_at"))
_FACTS = frozenset(("first_name", "last_name", "specialty", "is_active",
    "default_location_id", "aggregate_version"))
_REFUSALS = {
    (400, "PRACTITIONER_CREATE_INVALID"), (400, "PRACTITIONER_COMMAND_KEY_INVALID"),
    (400, "PRACTITIONER_CONFIRMATION_INVALID"),
    (401, "PRACTITIONER_AUTHENTICATION_REQUIRED"), (403, "PRACTITIONER_CREATE_DENIED"),
    (404, "PRACTITIONER_CREATE_NOT_FOUND"), (409, "PRACTITIONER_CREATE_CONFLICT"),
    (409, "PRACTITIONER_CONFIRMATION_INVALID"),
}


@dataclass(frozen=True, repr=False)
class PractitionerCreateBinding:
    # Future trusted callbacks return httpx.Response and select literal paths.
    # Private guards must surround their blocking/child boundaries; not HTTP input.
    prepare: object = None
    confirm: object = None
    receipt: object = None
    ends_at: datetime | None = None
    enabled: bool = False


def validate_optional_binding(binding):
    if binding is None:
        return False
    if type(binding) is not PractitionerCreateBinding or type(binding.enabled) is not bool:
        raise ValueError("PRACTITIONER_CREATE_BINDING_INVALID")
    if binding.enabled is False:
        if any(getattr(binding, k) is not None for k in ("prepare", "confirm", "receipt", "ends_at")):
            raise ValueError("PRACTITIONER_CREATE_DISABLED_BINDING_INVALID")
        return False
    if (any(not callable(getattr(binding, k)) for k in ("prepare", "confirm", "receipt"))
            or type(binding.ends_at) is not datetime or binding.ends_at.tzinfo is None
            or binding.ends_at.utcoffset().total_seconds() != 0):
        raise ValueError("PRACTITIONER_CREATE_BINDING_INVALID")
    return True


class _Invalid(Exception):
    pass


class _Refused(Exception):
    def __init__(self, code):
        self.code = code


class _Uncertain(Exception):
    pass


def _uuid(v):
    return type(v) is str and _UUID.fullmatch(v) is not None


def _int(v, low=0, high=_MAX):
    return type(v) is int and low <= v <= high


def _digest(v):
    return type(v) is str and _HEX.fullmatch(v) is not None


def _decimal(v, high=_MAX):
    if (type(v) is not str or re.fullmatch(r"[1-9][0-9]{0,18}", v) is None
            or len(v) > len(str(high)) or len(v) == len(str(high)) and v > str(high)):
        raise _Invalid()
    return v


def _text(v, *, optional=False, stored=False):
    if optional and v is None:
        return None
    if type(v) is not str:
        raise _Invalid()
    v.encode("utf-8", errors="strict")
    if stored:
        if len(v) > 100:
            raise _Invalid()
        return v  # Preserve legacy stored spelling/spacing; never recanonicalize a sample.
    v = v.strip(_W1)
    if optional and v == "":
        return None
    if not 1 <= len(v) <= 100 or any(ord(c) < 32 or ord(c) == 127 for c in v):
        raise _Invalid()
    return v


def _body(v):
    if (type(v) is not dict or set(v) != {"first_name", "last_name", "specialty", "distinct_resource"}
            or type(v["distinct_resource"]) is not bool):
        raise _Invalid()
    return {"first_name": _text(v["first_name"]), "last_name": _text(v["last_name"]),
        "specialty": _text(v["specialty"], optional=True), "distinct_resource": v["distinct_resource"]}


def _body_digest(v):
    raw = json.dumps(v, sort_keys=True, ensure_ascii=False, allow_nan=False,
        separators=(",", ":")).encode("utf-8", errors="strict")
    return hashlib.sha256(raw).hexdigest()


def _utc(v, *, draft=False):
    if type(v) is not str or not 1 <= len(v) <= 64:
        raise _Invalid()
    if draft:
        parsed = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        if parsed.strftime("%Y-%m-%dT%H:%M:%S.%fZ") != v:
            raise _Invalid()
    else:
        parsed = datetime.fromisoformat(v[:-1] + "+00:00" if v.endswith("Z") else v)
        if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
            raise _Invalid()
    return parsed


def _scope(a):
    return (a.account_id, a.membership_id, a.user_id, a.practice_id)


def _facts(v, *, current=False):
    keys = _FACTS | {"id", "practice_id"} if current else _FACTS
    if (type(v) is not dict or set(v) != keys
            or type(v["is_active"]) not in (bool, type(None))
            or v["default_location_id"] is not None and not _uuid(v["default_location_id"])
            or not _int(v["aggregate_version"], -9223372036854775808)):
        raise _Invalid()
    for k in ("first_name", "last_name", "specialty"):
        _text(v[k], optional=k == "specialty", stored=True)
    if current and (not _uuid(v["id"]) or not _uuid(v["practice_id"])):
        raise _Invalid()
    return {k: v[k] for k in _FACTS}


def _public_facts(v):
    # Version stays decimal text; location UUID is unnecessary presentation data.
    return {k: (str(v[k]) if k == "aggregate_version" else v[k]) for k in
        ("first_name", "last_name", "specialty", "is_active", "aggregate_version")}


class PractitionerCreateBridge:
    def __init__(self, owner, binding):
        if STOPPED_SOURCE_ONLY:
            raise ValueError("PRACTITIONER_CREATE_STOPPED_SOURCE_ONLY")
        if (type(owner) is not OwnerController or not validate_optional_binding(binding)
                or owner.binding.private_owner_current is None
                or not datetime.now(timezone.utc) < binding.ends_at <= owner.binding.ends_at
                or owner._practitioner_create is not None):
            raise ValueError("PRACTITIONER_CREATE_OWNER_BINDING_INVALID")
        self.owner, self.binding, self._closed = owner, binding, False
        self.pending = {}  # Bounded correlation/one-dispatch memory; never durable truth.
        owner._practitioner_create = self

    def _active(self):
        if (STOPPED_SOURCE_ONLY or self._closed or self.binding.enabled is not True
                or datetime.now(timezone.utc) >= self.binding.ends_at):
            raise _Denied()

    def _invalidate(self, key, value):
        for r in self.pending.values():
            if r.get("owner_key") == key and r.get("owner") is value:
                r.update(confirm=None, draft_current=False)
                # Preserve attempted/unresolved keys and immutable receipts.

    def _context(self, key, value):
        self._active()
        a, same, read_current = self.owner.practitioner_context(key, value)
        for (s, _), r in self.pending.items():
            if s == _scope(a) and (r["authority"] != a or r["owner"] is not value
                    or r["owner_key"] != key or r["csrf"] != value.csrf):
                r.update(confirm=None, draft_current=False)
        def local():
            self._active()
            same()
            return True
        async def current():
            local()
            await read_current()
            local()
            return True
        return a, local, current

    async def owner_scope(self, key, value):
        self._active()
        self.owner._current(key, value)
        if value.phase != "verified":
            self._invalidate(key, value)
            return None
        a, same, current = self._context(key, value)
        try:
            same()
            await current()
            same()
        except BaseException:
            self._invalidate(key, value)
            raise
        return {"practice_id": a.practice_id}  # No await before projection.

    async def _exchange(self, action, bearer, same, current, **kwargs):
        same()
        await current()
        same()
        response = await getattr(self.binding, action)(tenant_bearer=bearer,
            current=current, local_current=same, **kwargs)
        same()
        await current()
        same()
        raw = response.content
        if (type(raw) is not bytes or not 0 < len(raw) <= MAX_RESPONSE_BYTES
                or response.headers.get("content-type", "").split(";")[0] != "application/json"):
            raise _Uncertain()
        result = _json(raw.decode("utf-8", errors="strict"))
        same()
        if response.status_code != 200:
            if (type(result) is dict and set(result) == {"detail"} and type(result["detail"]) is str
                    and (response.status_code, result["detail"]) in _REFUSALS):
                raise _Refused(result["detail"])
            raise _Uncertain()  # A 503/malformed/timeout response does not prove rollback.
        return result

    def _receipt(self, v, a, command_key, r):
        if (type(v) is not dict or set(v) != _RECEIPT
                or v["schema_version"] != "practitioner.create.receipt.v1" or v["role"] != "PracticeOwner"
                or v["practice_id"] != a.practice_id or v["command_key"] != command_key
                or any(not _uuid(v[k]) for k in ("command_id", "command_key", "create_intent_id",
                    "practice_id", "practitioner_id", "actor_account_id", "actor_membership_id",
                    "actor_user_id", "audit_event_id", "outbox_event_id"))
                or not _int(v["draft_revision"], 1) or not _int(v["authority_generation"], 1)
                or type(v["initial_aggregate_version"]) is not int or v["initial_aggregate_version"] != 0
                or not _digest(v["body_digest"]) or not _digest(v["matching_context_digest"])
                or tuple(v[k] for k in ("actor_account_id", "actor_membership_id", "actor_user_id", "practice_id")) != _scope(a)):
            raise _Invalid()
        _utc(v["committed_at"])
        # Do NOT compare immutable receipt generation to the fresh current generation.
        if r is not None:
            if v["body_digest"] != r["body_digest"]:
                raise _Invalid()
            d = r.get("draft")
            if d is not None and any(v[k] != d[k] for k in
                    ("command_id", "create_intent_id", "draft_revision", "body_digest", "matching_context_digest")):
                raise _Invalid()
            if r.get("receipt") is not None and r["receipt"] != v:
                raise _Invalid()
        return dict(v)

    @staticmethod
    def _public_receipt(v):
        return {k: (str(v[k]) if k == "draft_revision" else v[k]) for k in
            ("command_key", "command_id", "create_intent_id", "draft_revision",
             "body_digest", "matching_context_digest", "committed_at")}

    def _recovery(self, result, a, command_key, r):
        if type(result) is not dict or set(result) != {"receipt", "readback"}:
            raise _Invalid()
        receipt = self._receipt(result["receipt"], a, command_key, r)
        rb = result["readback"]
        if (type(rb) is not dict or set(rb) != {"status", "expected", "current"}
                or rb["status"] not in ("matches_created", "diverged", "missing")):
            raise _Invalid()
        expected = _facts(rb["expected"])
        normalized = _body({**{k: expected[k] for k in ("first_name", "last_name", "specialty")},
            "distinct_resource": False})
        if (expected["is_active"] is not True or expected["default_location_id"] is not None
                or expected["aggregate_version"] != 0
                or any(normalized[k] != expected[k] for k in ("first_name", "last_name", "specialty"))
                or r is not None and any(expected[k] != r["body"][k] for k in ("first_name", "last_name", "specialty"))):
            raise _Invalid()
        if rb["current"] is None:
            if rb["status"] != "missing":
                raise _Invalid()
            public_current = None
        else:
            current = _facts(rb["current"], current=True)
            if (rb["current"]["id"] != receipt["practitioner_id"]
                    or rb["current"]["practice_id"] != receipt["practice_id"]
                    or rb["status"] != ("matches_created" if current == expected else "diverged")):
                raise _Invalid()
            public_current = _public_facts(current)
        if r is not None:
            r.update(receipt=receipt, resolved=True, confirm=None, draft_current=False)
        return {"state": "committed", "receipt": self._public_receipt(receipt),
            "readback": {"status": rb["status"], "expected": _public_facts(expected), "current": public_current}}

    def _prepared(self, result, a, r):
        if (type(result) is not dict or set(result) != {"state", "draft", "receipt", "confirmation_evidence"}
                or result["state"] != "prepared" or result["receipt"] is not None):
            raise _Invalid()
        d, evidence = result["draft"], result["confirmation_evidence"]
        if (type(d) is not dict or set(d) != _DRAFT or d["command_key"] != r["command_key"]
                or not _uuid(d["command_id"]) or not _uuid(d["create_intent_id"])
                or not _int(d["draft_revision"], 1) or not _int(d["authority_generation"], 1)
                or d["authority_generation"] != a.authority_generation or d["role"] != "PracticeOwner"
                or d["canonicalization_version"] != "practitioner.create.body.v1"
                or d["matching_context_version"] != "practitioner.create.matches.v1"
                or type(d["body"]) is not dict or _body(d["body"]) != d["body"] or d["body"] != r["body"]
                or d["body_digest"] != r["body_digest"] or not _digest(d["matching_context_digest"])
                or not _int(d["match_total"]) or not _int(d["sample_count"], 0, 10)
                or d["sample_count"] != min(10, d["match_total"])
                or type(d["sample_label"]) is not str or d["sample_label"] != f'Showing {d["sample_count"]} of {d["match_total"]}'
                or type(d["advisory_matches"]) is not list or len(d["advisory_matches"]) != d["sample_count"]
                or type(d["requires_distinct_resource_decision"]) is not bool
                or d["requires_distinct_resource_decision"] != (d["match_total"] > 0 and not d["body"]["distinct_resource"])):
            raise _Invalid()
        if r["request"]["new_intent"]:
            if d["draft_revision"] != 1:
                raise _Invalid()
        elif (d["create_intent_id"] != r["request"]["create_intent_id"]
                or d["draft_revision"] != r["request"]["supersedes_revision"] + 1):
            raise _Invalid()
        expiry = _utc(d["expires_at"], draft=True)
        matches, ids = [], []
        for row in d["advisory_matches"]:
            if (type(row) is not dict or set(row) != {"id", "first_name", "last_name", "specialty", "is_active", "aggregate_version"}
                    or not _uuid(row["id"]) or row["id"] in ids
                    or type(row["is_active"]) not in (bool, type(None))
                    or not _int(row["aggregate_version"], -9223372036854775808)):
                raise _Invalid()
            for k in ("first_name", "last_name", "specialty"):
                _text(row[k], optional=k == "specialty", stored=True)
            ids.append(row["id"])
            matches.append({k: row[k] for k in ("first_name", "last_name", "specialty", "is_active")})
        if ids != sorted(ids):
            raise _Invalid()
        confirm = None
        if d["requires_distinct_resource_decision"]:
            if evidence is not None:
                raise _Invalid()
        else:
            payload = {"schema_version": "practitioner.create.confirmation.v1",
                "canonicalization_version": "practitioner.create.body.v1", "account_id": a.account_id,
                "membership_id": a.membership_id, "user_id": a.user_id, "practice_id": a.practice_id,
                "role": "PracticeOwner", "authority_generation": a.authority_generation,
                **{k: d[k] for k in ("command_id", "command_key", "create_intent_id", "draft_revision",
                    "body_digest", "matching_context_digest", "expires_at")}}
            if (type(evidence) is not dict or set(evidence) != {"schema_version", "purpose", "payload", "signature"}
                    or evidence["schema_version"] != "bernie.confirmation_evidence.v1"
                    or evidence["purpose"] != "practitioner_confirm_create_resource" or not _digest(evidence["signature"])
                    or type(evidence["payload"]) is not dict or set(evidence["payload"]) != set(payload)
                    or any(type(evidence["payload"][k]) is not type(v) or evidence["payload"][k] != v for k, v in payload.items())
                    or len(json.dumps(evidence, ensure_ascii=False).encode("utf-8")) > 8192):
                raise _Invalid()
            confirm = {k: d[k] for k in ("command_key", "command_id", "create_intent_id",
                "draft_revision", "body_digest", "matching_context_digest")}
            confirm.update(confirmed=True, signed_confirmation_evidence=evidence)
        if r.get("draft") is not None and r["draft"] != d:
            raise _Invalid()
        r.update(draft=dict(d), prepare_complete=True, draft_current=True, confirm=confirm)
        return {"state": "prepared", "draft": {
            **{k: d[k] for k in ("command_key", "command_id", "create_intent_id", "body", "body_digest",
                "matching_context_digest", "expires_at", "sample_count", "sample_label", "requires_distinct_resource_decision")},
            "draft_revision": str(d["draft_revision"]), "match_total": str(d["match_total"]),
            "advisory_matches": matches, "can_confirm": confirm is not None and datetime.now(timezone.utc) < expiry}}

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, "")
        value = self.owner.sessions.get(key)
        r, command_key, dispatched = None, None, False
        try:
            self._active()
            if (value is None or action not in ("prepare", "confirm", "receipt") or request.method != "POST"
                    or request.url.query or request.headers.get("authorization") is not None
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
                same()
                body = _json(b"".join(chunks).decode("utf-8", errors="strict"))
                same()
                if type(body) is not dict or not _uuid(body.get("command_key")):
                    raise _Invalid()
                command_key = body["command_key"]
                r = self.pending.get((_scope(a), command_key))
                await current()
                same()
                if action == "prepare":
                    if (set(body) != {"command_key", "body", "new_intent", "create_intent_id",
                            "supersedes_command_id", "supersedes_revision"} or type(body["new_intent"]) is not bool):
                        raise _Invalid()
                    canonical = _body(body["body"])
                    native = {**body, "body": canonical}
                    links = (body["create_intent_id"], body["supersedes_command_id"], body["supersedes_revision"])
                    predecessor = None
                    if body["new_intent"]:
                        if any(v is not None for v in links):
                            raise _Invalid()
                    else:
                        if not _uuid(links[0]) or not _uuid(links[1]):
                            raise _Invalid()
                        revision = _decimal(links[2], _MAX - 1)
                        prior = [p for (s, _), p in self.pending.items() if s == _scope(a)
                            and p.get("draft_current") and p["authority"] == a and p["owner"] is value
                            and p["owner_key"] == key and p["draft"]["command_id"] == links[1]
                            and p["draft"]["create_intent_id"] == links[0]
                            and str(p["draft"]["draft_revision"]) == revision]
                        if len(prior) != 1:
                            raise _Invalid()
                        predecessor = prior[0]
                        # Forward the EXACT retained native integer, never a client conversion.
                        native["supersedes_revision"] = predecessor["draft"]["draft_revision"]
                    fingerprint = json.dumps(native, sort_keys=True, ensure_ascii=False,
                        allow_nan=False, separators=(",", ":"))
                    if len(fingerprint.encode("utf-8")) > 4096:
                        raise _Invalid()
                    if any(s == _scope(a) and not p["resolved"] and (p["attempted"] or not p["prepare_complete"])
                            and k != command_key for (s, k), p in self.pending.items()):
                        raise _Uncertain()
                    if r is not None:
                        if (r["fingerprint"] != fingerprint or r["attempted"]
                                or r["prepare_complete"] and not r["draft_current"] or r["authority"] != a
                                or r["owner"] is not value or r["owner_key"] != key or r["csrf"] != value.csrf):
                            raise _Uncertain()
                    else:
                        if len(self.pending) >= 256:
                            raise _Uncertain()
                        r = {"command_key": command_key, "request": native, "fingerprint": fingerprint,
                            "body": canonical, "body_digest": _body_digest(canonical), "authority": a,
                            "owner": value, "owner_key": key, "csrf": value.csrf, "attempted": False,
                            "prepare_complete": False, "resolved": False, "draft_current": False,
                            "draft": None, "confirm": None, "receipt": None}
                        self.pending[(_scope(a), command_key)] = r
                    same()
                    dispatched = True  # Prepare persists only prepared-command state.
                    result = await self._exchange(action, value.tenant, same, current, body=r["request"])
                    same()
                    if type(result) is dict and result.get("state") == "committed":
                        if (set(result) != {"state", "draft", "receipt", "confirmation_evidence"}
                                or result["draft"] is not None or result["confirmation_evidence"] is not None):
                            raise _Invalid()
                        receipt = self._receipt(result["receipt"], a, command_key, r)
                        r.update(receipt=receipt, resolved=True, confirm=None, draft_current=False)
                        output = {"state": "committed", "receipt": self._public_receipt(receipt), "readback": None}
                    else:
                        output = self._prepared(result, a, r)
                        if predecessor is not None:
                            predecessor.update(confirm=None, draft_current=False)
                elif action == "confirm":
                    if (set(body) != {"command_key", "command_id", "create_intent_id", "draft_revision",
                            "body_digest", "matching_context_digest", "confirmed"} or body["confirmed"] is not True):
                        raise _Invalid()
                    if (r is None or r["attempted"] or not r["draft_current"] or r["confirm"] is None
                            or r["authority"] != a or r["owner"] is not value
                            or r["owner_key"] != key or r["csrf"] != value.csrf):
                        raise _Denied()
                    _decimal(body["draft_revision"])
                    expected = {k: (str(r["confirm"][k]) if k == "draft_revision" else r["confirm"][k]) for k in body}
                    if any(type(body[k]) is not type(v) or body[k] != v for k, v in expected.items()):
                        raise _Invalid()
                    if datetime.now(timezone.utc) >= _utc(r["draft"]["expires_at"], draft=True):
                        r["confirm"] = None  # Preserve the exact nonconfirmable predecessor for explicit re-review.
                        raise _Refused("PRACTITIONER_CREATE_CONFLICT")
                    same()
                    r["attempted"] = True  # Before dispatch; cancellation never rearms it.
                    dispatched = True
                    result = await self._exchange(action, value.tenant, same, current, body=r["confirm"])
                    same()
                    receipt = self._receipt(result, a, command_key, r)
                    r.update(receipt=receipt, resolved=True, confirm=None, draft_current=False)
                    output = {"state": "committed", "receipt": self._public_receipt(receipt), "readback": None}
                else:
                    if set(body) != {"command_key"}:
                        raise _Invalid()
                    # No live cache, old token, evidence or old generation is required.
                    result = await self._exchange(action, value.tenant, same, current, command_key=command_key)
                    same()
                    output = self._recovery(result, a, command_key, r)
                same()
                output["practitioner_create_scope"] = {"practice_id": a.practice_id}
                return _reply(output)
        except asyncio.CancelledError:
            if value is not None:
                self._invalidate(key, value)
            raise
        except _Refused as error:
            if r is not None:
                r["confirm"] = None
                if action != "receipt" and error.code != "PRACTITIONER_CREATE_NOT_FOUND":
                    r["resolved"] = True  # Keep an exact same-context predecessor; confirmation stays consumed.
            if action == "receipt" or error.code == "PRACTITIONER_CREATE_NOT_FOUND":
                return _reply({"state": "uncertain", "command_key": command_key,
                    "detail": "No committed receipt is available yet. Check this same creation reference again."}, 409)
            return _reply({"state": "refused", "code": error.code,
                "detail": "Creation was refused. Check the owner account and explicitly review fresh details."}, 409)
        except Exception:
            if value is not None:
                self._invalidate(key, value)
            if dispatched or action == "receipt":
                return _reply({"state": "uncertain", "command_key": command_key,
                    "detail": "The creation result is uncertain. Check this same creation reference; do not submit another creation."}, 503)
            return _reply({"detail": "Practitioner creation is unavailable. Check the current owner account."}, 403)

    async def close(self):
        self._closed = True
        for r in self.pending.values():
            r.update(confirm=None, draft_current=False)
        # Durable backend receipts survive cache loss; exact-key recovery needs
        # fresh authority after restart, never this process's old token/evidence.
