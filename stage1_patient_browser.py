"""STOPPED source proposal: default-off patient browser bridge, no mount or authority."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import re
import secrets
from typing import Awaitable, Callable

from stage1_seeded_login import COOKIE, SeededLoginController, _Denied, _Unavailable, _reply

_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_DEMOGRAPHICS = frozenset(("id", "practice_id", "first_name", "last_name", "date_of_birth"))
_RECEIPT = frozenset(("schema_version", "command_id", "command_key", "registration_intent_id",
    "draft_revision", "practice_id", "patient_id", "actor_account_id", "actor_membership_id",
    "actor_user_id", "role", "authority_generation", "body_digest", "audit_event_id", "created_at"))
class _InvalidInput(Exception):
    pass


_DRAFT = frozenset(("command_id", "command_key", "registration_intent_id", "draft_revision", "body",
    "body_digest", "role", "authority_generation", "expires_at", "advisory_matches",
    "requires_distinct_person_decision"))


@dataclass(frozen=True, repr=False)
class PatientBrowserBinding:
    # Callbacks return httpx.Response; adapter owns exact paths, bearer header and status.
    search: Callable[..., Awaitable]
    read: Callable[..., Awaitable]
    prepare: Callable[..., Awaitable]
    confirm: Callable[..., Awaitable]
    receipt: Callable[..., Awaitable]
    enabled: bool = False


def _uuid(value):
    return type(value) is str and _UUID.fullmatch(value) is not None


def _date(value):
    if type(value) is not str or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _name(value):
    return (type(value) is str and 1 <= len(value) <= 100 and value == value.strip()
            and not any(ord(c) < 32 or ord(c) == 127 for c in value))


def _patient(row, practice):
    if (type(row) is not dict or set(row) != _DEMOGRAPHICS or not _uuid(row["id"])
            or row["practice_id"] != practice or not _name(row["first_name"])
            or not _name(row["last_name"]) or not _date(row["date_of_birth"])):
        raise _Denied()
    return {key: row[key] for key in ("id", "practice_id", "first_name", "last_name", "date_of_birth")}


def _receipt(row, practice, command_key):
    if (type(row) is not dict or set(row) != _RECEIPT
            or row["schema_version"] != "patient.registration.receipt.v1"
            or row["practice_id"] != practice or row["command_key"] != command_key
            or any(not _uuid(row[k]) for k in ("command_id", "command_key", "registration_intent_id",
                "practice_id", "patient_id", "actor_account_id", "actor_membership_id", "actor_user_id", "audit_event_id"))
            or type(row["draft_revision"]) is not int or row["draft_revision"] < 1
            or type(row["authority_generation"]) is not int or row["authority_generation"] < 1
            or row["role"] not in ("Receptionist", "PracticeOwner")
            or type(row["body_digest"]) is not str or not _HEX.fullmatch(row["body_digest"])
            or type(row["created_at"]) is not str or not 1 <= len(row["created_at"]) <= 64):
        raise _Denied()
    return {key: row[key] for key in ("schema_version", "command_key", "command_id", "registration_intent_id",
        "draft_revision", "practice_id", "patient_id", "body_digest", "audit_event_id", "created_at")}


class PatientBrowserBridge:
    def __init__(self, controller, binding):
        if (type(controller) is not SeededLoginController or type(binding) is not PatientBrowserBinding or binding.enabled is not True
                or any(not callable(getattr(binding, name)) for name in ("search", "read", "prepare", "confirm", "receipt"))):
            raise ValueError("patient bridge disabled")
        self.controller = controller
        self.binding = binding
        self._closed = False
        self.pending = {}  # Bounded server-only draft evidence; never exposed to browser.

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, "")
        value = self.controller.sessions.get(key)
        confirm_started = False
        result_received = False
        command_key = None
        try:
            if (self._closed or value is None or request.method != "POST" or request.url.query
                    or request.headers.get("authorization") is not None
                    or request.headers.get("origin") != request.app.state.seeded_login_origin
                    or request.headers.get("content-type") != "application/json"
                    or not secrets.compare_digest(request.headers.get("x-csrf-token", ""), value.csrf)):
                raise _Denied()
            async with value.lock:
                self.controller._require_current(key, value)
                chunks, size, body_oversize = [], 0, False
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > 4096:
                        body_oversize = True
                        break
                    chunks.append(chunk)
                self.controller._require_current(key, value)
                tenant, selected, session = value.tenant, value.selected, value.staff_session
                if not tenant or type(selected) is not dict:
                    raise _Denied()
                selected_copy = dict(selected)
                practice = selected_copy.get("practice_id")
                if not _uuid(practice):
                    raise _Denied()
                def same():
                    if self._closed:
                        raise _Denied()
                    self.controller._require_current(key, value)
                    if (value.tenant != tenant or value.selected is not selected
                            or value.selected != selected_copy or value.staff_session is not session):
                        raise _Denied()
                same()
                role = await self.controller._current(value, key=key, expected=value)
                same()
                if role not in ("Receptionist", "InvitedReceptionist", "PracticeOwner"):
                    raise _Denied()
                authority = value.patient_current_authority
                if type(authority) is not dict or authority.get("practice_id") != practice:
                    raise _Denied()
                authority = dict(authority)
                if body_oversize:
                    raise _InvalidInput()
                def pairs(items):
                    result = {}
                    for k, v in items:
                        if k in result:
                            raise _InvalidInput()
                        result[k] = v
                    return result
                try:
                    body = json.loads(b"".join(chunks), object_pairs_hook=pairs,
                        parse_constant=lambda _v: (_ for _ in ()).throw(_InvalidInput()))
                except Exception:
                    raise _InvalidInput() from None
                if type(body) is not dict:
                    raise _InvalidInput()
                request_args = {"tenant_bearer": tenant}
                command_key = None
                if action == "search":
                    if set(body) - {"q", "date_of_birth", "limit"} or not body:
                        raise _InvalidInput()
                    if ("q" in body and (type(body["q"]) is not str or not 2 <= len(body["q"]) <= 100
                            or any(ord(c) < 32 or ord(c) == 127 for c in body["q"]))):
                        raise _InvalidInput()
                    if "date_of_birth" in body and not _date(body["date_of_birth"]):
                        raise _InvalidInput()
                    if "limit" in body and (type(body["limit"]) is not int or not 1 <= body["limit"] <= 20):
                        raise _InvalidInput()
                    request_args["params"] = dict(body)
                elif action == "read":
                    if set(body) != {"patient_id"} or not _uuid(body["patient_id"]):
                        raise _InvalidInput()
                    request_args["patient_id"] = body["patient_id"]
                elif action == "prepare":
                    for old_key, old_record in list(self.pending.items()):
                        if not old_record["attempted"] and old_record["prepare_complete"]:
                            try:
                                self.controller._require_current(old_key, old_record["login"])
                            except _Denied:
                                self.pending.pop(old_key, None)
                    prior = self.pending.get(key)
                    same_principal = [(old_key, record) for old_key, record in self.pending.items()
                        if record.get("authority") == authority]
                    if (any(record["attempted"] for _, record in same_principal)
                            or any(not record["prepare_complete"] and record["command_key"] != body.get("command_key")
                                for _, record in same_principal)):
                        raise _Unavailable()
                    matching = [(old_key, record) for old_key, record in same_principal
                        if record["command_key"] == body.get("command_key") and old_key != key]
                    if len(matching) > 1 or (matching and prior is not None):
                        raise _Unavailable()
                    if matching:
                        old_key, prior = matching[0]
                        try:
                            self.controller._require_current(old_key, prior["login"])
                        except _Denied:
                            pass  # Only a locally noncurrent or expired owner can be migrated.
                        else:
                            raise _Unavailable()
                        self.pending.pop(old_key)
                        prior.update(login=value, selected=selected, selection=selected_copy, staff_session=session)
                        self.pending[key] = prior
                    if prior is not None and prior["attempted"]:
                        raise _Unavailable()
                    if set(body) != {"command_key", "body", "new_registration", "registration_intent_id", "supersedes_command_id", "supersedes_revision"}:
                        raise _InvalidInput()
                    demographics = body["body"]
                    if (not _uuid(body["command_key"]) or type(body["new_registration"]) is not bool
                            or type(demographics) is not dict or set(demographics) != {"first_name", "last_name", "date_of_birth", "distinct_person"}
                            or not _name(demographics["first_name"]) or not _name(demographics["last_name"])
                            or not _date(demographics["date_of_birth"]) or date.fromisoformat(demographics["date_of_birth"]) > datetime.now(timezone.utc).date()
                            or type(demographics["distinct_person"]) is not bool):
                        raise _InvalidInput()
                    links = (body["registration_intent_id"], body["supersedes_command_id"], body["supersedes_revision"])
                    if (body["new_registration"] and any(v is not None for v in links)) or (not body["new_registration"]
                            and (not _uuid(links[0]) or not _uuid(links[1]) or type(links[2]) is not int or links[2] < 1)):
                        raise _InvalidInput()
                    command_key = body["command_key"]
                    fingerprint = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False)
                    if prior is not None:
                        if (prior["login"] is not value or prior["selected"] is not selected
                                or prior["selection"] != selected_copy or prior["staff_session"] is not session):
                            raise _Unavailable()
                        if prior["command_key"] == command_key:
                            if prior["prepare_fingerprint"] != fingerprint:
                                raise _Unavailable()
                        elif not prior["prepare_complete"]:
                            raise _Unavailable()
                        else:
                            self.pending.pop(key, None)
                            prior = None
                    if prior is None:
                        if len(self.pending) >= 256:
                            raise _Unavailable()
                        self.pending[key] = {"command_key": command_key, "practice_id": practice,
                            "login": value, "selected": selected, "selection": selected_copy,
                            "staff_session": session, "authority": dict(authority), "attempted": False, "prepare_complete": False,
                            "prepare_fingerprint": fingerprint, "confirm_body": None}
                    request_args["body"] = body
                elif action in ("confirm", "receipt"):
                    allowed = {"command_key", "confirmed", "command_id", "draft_revision", "body_digest"} if action == "confirm" else {"command_key"}
                    if set(body) != allowed or not _uuid(body["command_key"]) or (action == "confirm" and body["confirmed"] is not True):
                        raise _InvalidInput()
                    command_key = body["command_key"]
                    if action == "receipt":
                        request_args["command_key"] = command_key
                    else:
                        pending = self.pending.get(key)
                        if (type(pending) is not dict or pending["command_key"] != command_key
                                or pending["practice_id"] != practice or pending["attempted"]
                                or pending["login"] is not value or pending["selected"] is not selected
                                or pending["selection"] != selected_copy or pending["staff_session"] is not session
                                or type(pending["confirm_body"]) is not dict
                                or any(type(body[name]) is not type(pending["confirm_body" ][name])
                                    or body[name] != pending["confirm_body" ][name]
                                    for name in ("command_id", "draft_revision", "body_digest"))):
                            raise _Unavailable()
                        pending["attempted"] = True  # A canceled or uncertain write stays consumed.
                        confirm_started = True
                        request_args["body"] = dict(pending["confirm_body"])
                else:
                    raise _InvalidInput()
                same()
                try:
                    result = await self.controller._call(getattr(self.binding, action), **request_args)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    raise _Unavailable() from None
                same()
                role_after = await self.controller._current(value, key=key, expected=value)
                same()
                if role_after != role or value.patient_current_authority != authority:
                    raise _Denied()
                result_received = True
                if action == "search":
                    if type(result) is not list or len(result) > 20:
                        raise _Denied()
                    output = [_patient(row, practice) for row in result]
                elif action == "read":
                    output = _patient(result, practice)
                    if output["id"] != body["patient_id"]:
                        raise _Denied()
                elif action in ("confirm", "receipt"):
                    output = _receipt(result, practice, command_key)
                    if (any(result[name] != authority[target] for name, target in (
                            ("actor_account_id", "account_id"), ("actor_membership_id", "membership_id"),
                            ("actor_user_id", "user_id"), ("role", "role"),
                            ("authority_generation", "authority_generation")))):
                        raise _Denied()
                    retained_matches = [(old_key, record) for old_key, record in self.pending.items()
                        if record["command_key"] == command_key and record.get("authority") == authority]
                    if len(retained_matches) > 1:
                        raise _Unavailable()
                    if retained_matches:
                        retained_key, retained = retained_matches[0]
                        retained_body = retained.get("confirm_body")
                        if retained_body is not None and any(result[name] != retained_body[name]
                                for name in ("command_id", "registration_intent_id", "draft_revision", "body_digest")):
                            raise _Unavailable()
                        if action == "receipt":
                            self.pending.pop(retained_key, None)
                else:
                    if type(result) is not dict or set(result) != {"state", "draft", "receipt", "confirmation_evidence"}:
                        raise _Denied()
                    if result["state"] == "committed" and result["draft"] is None and result["confirmation_evidence"] is None:
                        committed = result["receipt"]
                        output = {"state": "committed", "receipt": _receipt(committed, practice, command_key)}
                        if any(committed[name] != authority[target] for name, target in (
                                ("actor_account_id", "account_id"), ("actor_membership_id", "membership_id"),
                                ("actor_user_id", "user_id"), ("role", "role"),
                                ("authority_generation", "authority_generation"))):
                            raise _Denied()
                        retained = self.pending.get(key)
                        retained_body = retained.get("confirm_body") if retained is not None else None
                        if retained_body is not None and any(committed[name] != retained_body[name]
                                for name in ("command_id", "registration_intent_id", "draft_revision", "body_digest")):
                            raise _Unavailable()
                        self.pending.pop(key, None)
                    elif result["state"] == "prepared" and result["receipt"] is None:
                        draft, evidence = result["draft"], result["confirmation_evidence"]
                        if (type(draft) is not dict or set(draft) != _DRAFT or draft["command_key"] != command_key
                                or not _uuid(draft["command_id"]) or not _uuid(draft["registration_intent_id"])
                                or type(draft["draft_revision"]) is not int or draft["draft_revision"] < 1
                                or type(draft["body_digest"]) is not str or not _HEX.fullmatch(draft["body_digest"])
                                or type(draft["requires_distinct_person_decision"]) is not bool
                                or draft["role"] not in ("Receptionist", "PracticeOwner")
                                or type(draft["authority_generation"]) is not int or draft["authority_generation"] < 1
                                or type(draft["expires_at"]) is not str or not 1 <= len(draft["expires_at"]) <= 64
                                or type(draft["body"]) is not dict
                                or set(draft["body"]) != {"canonicalization_version", "first_name", "last_name", "date_of_birth", "distinct_person"}
                                or draft["body"].get("canonicalization_version") != "patient.registration.body.v1"
                                or any(type(draft["body"].get(name)) is not type(body["body"][name])
                                    or draft["body"].get(name) != body["body"][name] for name in body["body"])
                                or type(draft["advisory_matches"]) is not list or len(draft["advisory_matches" ]) > 20):
                            raise _Denied()
                        matches = [_patient(row, practice) for row in draft["advisory_matches"]]
                        if evidence is not None and (type(evidence) is not dict or len(json.dumps(evidence)) > 8192):
                            raise _Denied()
                        if draft["role"] != authority["role"] or draft["authority_generation"] != authority["authority_generation"]:
                            raise _Denied()
                        retained = self.pending[key]
                        confirm_body = None
                        if evidence is not None and not draft["requires_distinct_person_decision"]:
                            confirm_body = {"command_key": command_key, "command_id": draft["command_id"],
                                "registration_intent_id": draft["registration_intent_id"], "draft_revision": draft["draft_revision"],
                                "body_digest": draft["body_digest"], "confirmed": True, "signed_confirmation_evidence": evidence}
                        if retained["prepare_complete"]:
                            previous = retained["confirm_body"]
                            if ((previous is None) != (confirm_body is None) or (previous is not None
                                    and any(previous[name] != confirm_body[name] for name in
                                        ("command_key", "command_id", "registration_intent_id", "draft_revision", "body_digest")))):
                                raise _Unavailable()
                            confirm_body = previous
                        retained["prepare_complete"] = True
                        retained["confirm_body"] = confirm_body
                        output = {"state": "prepared", "command_key": command_key,
                            "command_id": draft["command_id"], "registration_intent_id": draft["registration_intent_id"],
                            "draft_revision": draft["draft_revision"], "body_digest": draft["body_digest"],
                            "body": dict(draft["body"]),
                            "advisory_matches": matches, "requires_distinct_person_decision": draft["requires_distinct_person_decision"],
                            "can_confirm": evidence is not None and not draft["requires_distinct_person_decision"]}
                    else:
                        raise _Denied()
                return _reply({"result": output})
        except asyncio.CancelledError:
            raise
        except _InvalidInput:
            if "same" in locals():
                try:
                    same()
                except Exception:
                    return _reply({"error": "PATIENT_CONTEXT_UNAVAILABLE"}, 403)
            if ("authority" in locals() and not confirm_started
                    and not any(record.get("authority") == authority and
                        (record["attempted"] or not record["prepare_complete"])
                        for record in self.pending.values())):
                return _reply({"error": "PATIENT_INPUT_INVALID"}, 400)
            return _reply({"error": "PATIENT_REQUEST_UNAVAILABLE"}, 503)
        except _Denied:
            if confirm_started:
                if result_received:
                    return _reply({"status": "uncertain", "command_key": command_key,
                        "next": "recover_same_key_receipt"}, 503)
                return _reply({"error": "PATIENT_CONTEXT_UNAVAILABLE", "command_key": command_key,
                    "next": "recover_same_key_receipt"}, 403)
            if result_received:
                return _reply({"error": "PATIENT_REQUEST_UNAVAILABLE"}, 503)
            return _reply({"error": "PATIENT_CONTEXT_UNAVAILABLE"}, 403)
        except _Unavailable:
            if "same" in locals():
                try:
                    same()
                except Exception:
                    if confirm_started:
                        return _reply({"error": "PATIENT_CONTEXT_UNAVAILABLE", "command_key": command_key,
                            "next": "recover_same_key_receipt"}, 403)
                    return _reply({"error": "PATIENT_CONTEXT_UNAVAILABLE"}, 403)
            if confirm_started:
                return _reply({"status": "uncertain", "command_key": command_key,
                    "next": "recover_same_key_receipt"}, 503)
            return _reply({"error": "PATIENT_REQUEST_UNAVAILABLE"}, 503)
        except Exception:
            if confirm_started:
                return _reply({"status": "uncertain", "command_key": command_key,
                    "next": "recover_same_key_receipt"}, 503)
            return _reply({"error": "PATIENT_REQUEST_UNAVAILABLE"}, 503)

    async def close(self):
        self._closed = True
        self.pending.clear()
