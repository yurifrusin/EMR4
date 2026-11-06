"""Inert, synthetic-only Account browser bridge; no credentials in projections.

Startup supplies four fixed typed transport methods, not a URL/request proxy.
JWT payload extraction below follows backend /me acceptance of the SAME token;
it is correlation of backend-validated data, never local JWT authentication.
"""
from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import re
import secrets
from typing import Awaitable, Callable, Any

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse

COOKIE = "stage1_demo_session"
PREFIX = "/demo/stage1/account"
PRACTICE = "10000000-0000-4000-8000-000000000001"
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
FIXTURES = {
    "Receptionist": ("20000000-0000-4000-8000-000000000002",
        "40000000-0000-4000-8000-000000000004",
        "50000000-0000-4000-8000-000000000005", "interactive-staff@example.invalid"),
    "PracticeOwner": ("20000000-0000-4000-8000-000000000003",
        "40000000-0000-4000-8000-000000000006",
        "50000000-0000-4000-8000-000000000007", "interactive-owner@example.invalid"),
}


@dataclass(frozen=True, repr=False)
class SeededLoginBinding:
    # Exact signatures match the independently reviewed BackendExecTransport.
    account_login: Callable[..., Awaitable[httpx.Response]]
    account_memberships: Callable[..., Awaitable[httpx.Response]]
    account_select_membership: Callable[..., Awaitable[httpx.Response]]
    account_me: Callable[..., Awaitable[httpx.Response]]
    ends_at: datetime
    enabled: bool = False
    private_recipient_current: object = field(default=None, repr=False)
    invitation_join_enabled: bool = False
    invitation_accept: object = field(default=None, repr=False)
    invitation_ready: object = field(default=None, repr=False)


@dataclass(repr=False)
class _Login:
    csrf: str
    expires_at: datetime
    bootstrap: str | None = None
    tenant: str | None = None
    choices: list[dict] = field(default_factory=list)
    selected: dict | None = None
    identity: dict | None = None
    staff_session: Any = None
    patient_current_authority: dict | None = None
    invitation_receipt: dict | None = None
    invitation_context: object = field(default=None, repr=False)
    invitation_attempted: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)


class _Denied(Exception):
    pass


class _Unavailable(Exception):
    pass


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _Denied()
        result[key] = value
    return result


def _json(raw):
    return json.loads(raw, object_pairs_hook=_object,
        parse_constant=lambda _: (_ for _ in ()).throw(_Denied()))


def _reply(value, code=200):
    return JSONResponse(value, status_code=code, headers={
        "Cache-Control": "no-store", "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff"})


class SeededLoginController:
    def __init__(self, binding, *, human_end, practice_id, make_staff, drop_staff):
        now = datetime.now(timezone.utc)
        if (type(binding) is not SeededLoginBinding or binding.enabled is not True
                or type(binding.ends_at) is not datetime or binding.ends_at.tzinfo is None
                or binding.ends_at.utcoffset() != timedelta(0)
                or human_end is None or not now < binding.ends_at <= human_end
                or practice_id != PRACTICE
                or any(not callable(getattr(binding, name)) for name in (
                    "account_login", "account_memberships", "account_select_membership", "account_me"))):
            raise ValueError("SEEDED_LOGIN_BINDING_INVALID")
        if binding.private_recipient_current is not None and not callable(binding.private_recipient_current):
            raise ValueError("SEEDED_PRIVATE_CALLBACK_INVALID")
        if (type(binding.invitation_join_enabled) is not bool or
                (binding.invitation_join_enabled and (binding.private_recipient_current is None or
                 not callable(binding.invitation_accept) or not callable(binding.invitation_ready))) or
                (not binding.invitation_join_enabled and (binding.invitation_accept is not None or binding.invitation_ready is not None))):
            raise ValueError("SEEDED_INVITATION_BINDING_INVALID")
        self.invitation_owner = None
        self._closed = False
        self.binding = binding
        self.make_staff, self.drop_staff = make_staff, drop_staff
        self.sessions: dict[str, _Login] = {}

    def _alive(self, value):
        if self._closed or datetime.now(timezone.utc) >= min(value.expires_at, self.binding.ends_at):
            raise _Denied()

    def _require_current(self, key, value):
        if self.sessions.get(key) is not value:
            raise _Denied()
        self._alive(value)

    def _drop(self, key, *, expected=None):
        if expected is not None and self.sessions.get(key) is not expected:
            return
        value = self.sessions.pop(key, None)
        if value:
            if value.staff_session is not None:
                self.drop_staff(key)
            value.bootstrap = value.tenant = None
            value.choices.clear()
            value.selected = value.identity = value.staff_session = None
            value.patient_current_authority = None
            value.invitation_receipt = value.invitation_context = None

    def _rotate(self, old, value, *, expected=None):
        # Conditional replacement is synchronous: no awaited completion can
        # recreate a removed/expired original or overwrite an unrelated entry.
        if expected is not None:
            self._require_current(old, expected)
        elif old in self.sessions:
            raise _Denied()
        self._alive(value)
        self._drop(old)
        key = secrets.token_urlsafe(32)
        value.csrf = secrets.token_urlsafe(24)
        self.sessions[key] = value
        return key

    def _cookie(self, response, key, value):
        self._alive(value)
        response.set_cookie(COOKIE, key, httponly=True, samesite="strict",
            secure=False, path="/demo/stage1",
            max_age=max(1, int((min(value.expires_at, self.binding.ends_at)
                               - datetime.now(timezone.utc)).total_seconds())))
        return response

    async def _call(self, method, **kwargs):
        try:
            response = await method(**kwargs)
            if (type(response.status_code) is not int or response.status_code != 200
                    or len(response.content) > 16384
                    or response.headers.get("content-type", "").split(";")[0] != "application/json"):
                raise _Denied()
            return _json(response.content)
        except Exception:
            # Never forward backend validation, response text, transport error,
            # credentials or tokens into a browser response or diagnostic.
            raise _Denied() from None

    async def _current_call(self, *, tenant_bearer):
        # The same account endpoint provides typed availability only for _current.
        try:
            response = await self.binding.account_me(tenant_bearer=tenant_bearer)
            status = response.status_code
            if type(status) is not int:
                raise _Unavailable()
            if status in (401, 403):
                raise _Denied()
            if (status != 200 or len(response.content) > 16384
                    or response.headers.get("content-type", "").split(";")[0] != "application/json"):
                raise _Unavailable()
            try:
                return _json(response.content)
            except Exception:
                raise _Unavailable() from None
        except (_Denied, _Unavailable):
            raise
        except Exception:
            raise _Unavailable() from None

    def _token(self, data):
        if (type(data) is not dict or set(data) != {"access_token", "token_type"}
                or data["token_type"] != "bearer" or type(data["access_token"]) is not str
                or not 1 <= len(data["access_token"]) <= 8192
                or not re.fullmatch(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", data["access_token"])):
            raise _Denied()
        return data["access_token"]

    async def _choices(self, bootstrap):
        rows = await self._call(self.binding.account_memberships, bootstrap_bearer=bootstrap)
        if type(rows) is not list or not 1 <= len(rows) <= 8:
            raise _Denied()
        seen = set()
        for row in rows:
            if (type(row) is not dict or set(row) != {
                    "membership_id", "practice_id", "practice_name", "role"}
                    or any(type(row[k]) is not str or not UUID.fullmatch(row[k])
                           for k in ("membership_id", "practice_id"))
                    or row["membership_id"] in seen
                    or type(row["practice_name"]) is not str
                    or not 1 <= len(row["practice_name"]) <= 255
                    or row["role"] not in FIXTURES):
                raise _Denied()
            seen.add(row["membership_id"])
        return rows

    async def _current(self, value, *, key, expected):
        value.patient_current_authority = None
        self._require_current(key, expected)
        self._alive(value)
        if not value.tenant or value.selected is None:
            raise _Denied()
        # The protected backend endpoint authenticates AND checks current rows.
        try:
            me = await self._current_call(tenant_bearer=value.tenant)
        except _Unavailable:
            self._require_current(key, expected)
            self._alive(value)
            raise
        self._require_current(key, expected)
        self._alive(value)
        if (type(me) is not dict or set(me) != {"id", "email", "role", "practice_id"}
                or any(type(me[name]) is not str for name in ("id", "email", "role", "practice_id"))
                or not UUID.fullmatch(me["id"]) or not UUID.fullmatch(me["practice_id"])
                or not 1 <= len(me["email"]) <= 254 or any(ord(c) < 32 or ord(c) == 127 for c in me["email"])):
            raise _Unavailable()
        role = me.get("role")
        if type(role) is not str or role not in FIXTURES:
            raise _Denied()
        user, account, member, email = FIXTURES[role]
        # Only this server-origin token, after /me succeeded, is decoded. No key
        # is loaded and no caller-supplied token is ever accepted by this bridge.
        try:
            middle = value.tenant.split(".")[1]
            claims = _json(base64.b64decode(middle + "=" * (-len(middle) % 4),
                altchars=b"-_", validate=True))
        except Exception:
            raise _Denied() from None
        if value.invitation_receipt is not None:
            receipt = value.invitation_receipt
            if (not self.binding.invitation_join_enabled or self.invitation_owner is None
                    or self.invitation_owner.invitation_context() != value.invitation_context
                    or self.binding.invitation_ready() is not True
                    or role != "Receptionist" or receipt["practice_id"] == PRACTICE
                    or type(claims) is not dict or claims.get("account_id") != FIXTURES["Receptionist"][1]
                    or claims.get("membership_id") != receipt["membership_id"]
                    or claims.get("practice_id") != receipt["practice_id"]
                    or claims.get("role") != "Receptionist" or claims.get("sub") != me["id"]
                    or type(me["id"]) is not str or not UUID.fullmatch(me["id"])
                    or type(me["email"]) is not str
                    or me["email"] != "invitation-" + me["id"] + "@synthetic.invalid"
                    or me["practice_id"] != receipt["practice_id"]
                    or type(claims.get("authority_generation")) is not int or claims["authority_generation"] < 1
                    or claims.get("aud") != "raisa-tenant" or claims.get("token_kind") != "selected_membership"
                    or any(value.selected[k] != receipt[k] for k in ("membership_id","practice_id","role"))):
                raise _Denied()
            value.patient_current_authority = {"account_id": claims["account_id"], "membership_id": claims["membership_id"],
                "user_id": claims["sub"], "practice_id": claims["practice_id"], "role": claims["role"],
                "authority_generation": claims["authority_generation"]}
            value.identity = {"email":me["email"],"role":"Receptionist","practice_name":value.selected["practice_name"]}
            return "InvitedReceptionist"  # Identity only; never a make_staff/Bureau capability.
        if (type(claims) is not dict or claims.get("sub") != user
                or claims.get("account_id") != account or claims.get("membership_id") != member
                or claims.get("practice_id") != PRACTICE or claims.get("role") != role
                or type(claims.get("authority_generation")) is not int
                or claims["authority_generation"] != 1
                or claims.get("aud") != "raisa-tenant"
                or claims.get("token_kind") != "selected_membership"
                or me != {"id": user, "email": email, "role": role, "practice_id": PRACTICE}
                or value.selected["membership_id"] != member
                or value.selected["practice_id"] != PRACTICE or value.selected["role"] != role):
            raise _Denied()
        value.patient_current_authority = {"account_id": account, "membership_id": member, "user_id": user,
            "practice_id": PRACTICE, "role": role, "authority_generation": claims["authority_generation"]}
        value.identity = {"email": email, "role": role,
                          "practice_name": value.selected["practice_name"]}
        return role

    async def require_staff(self, session):
        # Used immediately before AND after each protected backend exchange.
        for key, value in list(self.sessions.items()):
            if value.staff_session is session:
                try:
                    if await self._current(value, key=key, expected=value) != "Receptionist":
                        raise _Denied()
                    if self.sessions.get(key) is not value or value.staff_session is not session:
                        raise _Denied()
                    return
                except Exception:
                    self._drop(key, expected=value)
                    break
        raise _Denied()

    def invitation_projection(self, value):
        if not self.binding.invitation_join_enabled or self.invitation_owner is None:
            return None
        if value.invitation_receipt is not None:
            return {"phase":"selected" if value.tenant else "choose","can_accept":False}
        try:
            context = self.invitation_owner.invitation_context()
        except _Denied:
            return None
        if not value.tenant or value.identity is None or value.identity.get("role") != "Receptionist":
            return None
        return {"phase":"review","practice_name":context[3],"role":"Receptionist",
                "target":"Existing synthetic receptionist","can_accept":not value.invitation_attempted}

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, "")
        value = self.sessions.get(key)
        try:
            if self._closed or request.url.query or request.headers.get("authorization") is not None:
                raise _Denied()
            if action == "state" and request.method == "GET" and value is None:
                # Finite memory bound within the existing 256-call envelope.
                # A new tab never removes another tab's live preauth/selection.
                for stale, item in list(self.sessions.items()):
                    if datetime.now(timezone.utc) >= min(item.expires_at, self.binding.ends_at):
                        self._drop(stale)
                if len(self.sessions) >= 256:
                    raise _Denied()
                value = _Login("", self.binding.ends_at)
                key = self._rotate(key, value)
            if value is None:
                raise _Denied()
            async with value.lock:
                self._alive(value)
                if self.sessions.get(key) is not value:
                    raise _Denied()
                if request.method == "POST":
                    if (request.headers.get("origin") != request.app.state.seeded_login_origin
                            or request.headers.get("content-type") != "application/json"
                            or not secrets.compare_digest(request.headers.get("x-csrf-token", ""), value.csrf)):
                        raise _Denied()
                    chunks, size = [], 0
                    async for chunk in request.stream():
                        size += len(chunk)
                        if size > 4096:
                            raise _Denied()
                        chunks.append(chunk)
                    body = _json(b"".join(chunks))
                    if type(body) is not dict:
                        raise _Denied()
                self._require_current(key, value)
                selection_checked = False
                if action == "login" and request.method == "POST":
                    if (set(body) != {"username", "password"} or value.bootstrap or value.tenant
                            or type(body["username"]) is not str or type(body["password"]) is not str
                            or not 1 <= len(body["username"]) <= 254
                            or not 1 <= len(body["password"].encode("utf-8")) <= 72):
                        raise _Denied()
                    token = self._token(await self._call(self.binding.account_login,
                        username=body["username"], password=body["password"]))
                    self._require_current(key, value)
                    body.clear()
                    choices = await self._choices(token)
                    self._require_current(key, value)
                    replacement = _Login("", value.expires_at, bootstrap=token, choices=choices)
                    key = self._rotate(key, replacement, expected=value)
                    value = replacement
                elif action == "accept-invitation" and request.method == "POST":
                    if (not self.binding.invitation_join_enabled or self.invitation_owner is None
                            or body != {"confirmed":True} or type(body["confirmed"]) is not bool
                            or not value.bootstrap or not value.tenant or value.invitation_attempted
                            or self.binding.invitation_ready() is not True):
                        raise _Denied()
                    if await self._current(value,key=key,expected=value) != "Receptionist":
                        raise _Denied()
                    self._require_current(key,value)
                    context = self.invitation_owner.invitation_context()
                    value.invitation_attempted = True
                    receipt = await self._call(self.binding.invitation_accept,bootstrap_bearer=value.bootstrap)
                    self._require_current(key,value)
                    if (self.invitation_owner.invitation_context() != context or type(receipt) is not dict
                            or set(receipt) != {"membership_id","practice_id","role"}
                            or any(type(receipt[k]) is not str or not UUID.fullmatch(receipt[k])
                                   for k in ("membership_id","practice_id"))
                            or receipt["practice_id"] != context[2] or receipt["practice_id"] == PRACTICE
                            or receipt["role"] != "Receptionist"):
                        raise _Denied()
                    rows = await self._choices(value.bootstrap)
                    self._require_current(key,value)
                    choices = [r for r in rows if all(r[k] == receipt[k] for k in ("membership_id","practice_id","role"))]
                    if len(choices) != 1 or choices[0]["practice_name"] != context[3]:
                        raise _Denied()
                    replacement = _Login("",value.expires_at,bootstrap=value.bootstrap,choices=choices,
                        invitation_receipt=dict(receipt),invitation_context=context,invitation_attempted=True)
                    key = self._rotate(key,replacement,expected=value)
                    value = replacement  # No tenant and no automatic selection or staff capability.
                elif action == "select" and request.method == "POST":
                    if (set(body) != {"membership_id"} or type(body["membership_id"]) is not str
                            or not value.bootstrap or value.tenant):
                        raise _Denied()
                    # Re-list before choice; backend selection independently rechecks.
                    rows = await self._choices(value.bootstrap)
                    self._require_current(key, value)
                    selected = [r for r in rows if r["membership_id"] == body["membership_id"]]
                    if len(selected) != 1 or selected[0] not in value.choices:
                        raise _Denied()
                    token = self._token(await self._call(self.binding.account_select_membership,
                        bootstrap_bearer=value.bootstrap, membership_id=body["membership_id"]))
                    self._require_current(key, value)
                    replacement = _Login("", self.binding.ends_at, tenant=token, selected=selected[0],
                        bootstrap=(value.bootstrap if self.binding.private_recipient_current is not None else None),
                        invitation_receipt=(dict(value.invitation_receipt) if value.invitation_receipt else None),
                        invitation_context=value.invitation_context,invitation_attempted=value.invitation_attempted)
                    role = await self._current(replacement, key=key, expected=value)
                    key = self._rotate(key, replacement, expected=value)
                    value = replacement
                    if role == "Receptionist":
                        value.staff_session = self.make_staff(key, token, value.expires_at, value.csrf)
                    selection_checked = True
                elif action == "logout" and request.method == "POST":
                    if body != {}:
                        raise _Denied()
                    replacement = _Login("", self.binding.ends_at)
                    key = self._rotate(key, replacement, expected=value)
                    value = replacement
                elif action != "state" or request.method != "GET":
                    raise _Denied()
                if value.tenant and not selection_checked:
                    await self._current(value, key=key, expected=value)
                # Selection's same-token /me result crosses only synchronous
                # rotation/mock issuance above; reuse it without another call.
                self._require_current(key, value)
                if (self.binding.private_recipient_current is not None and value.tenant and value.invitation_receipt is None
                        and value.identity is not None and value.identity.get('role') == 'Receptionist'):
                    # Recheck bootstrap using the same fixed backend/runtime.
                    # Current /me above validated tenant identity; this current
                    # membership query authenticates the same session's retained
                    # bootstrap before payload correlation, never local auth.
                    captured_key, captured_value = key, value
                    captured_bootstrap = value.bootstrap
                    captured_tenant = value.tenant
                    captured_selected = value.selected
                    def local_recipient_context():
                        self._require_current(captured_key,captured_value)  # Synchronous identity/closed/expiry checks.
                        return (captured_value.bootstrap == captured_bootstrap and captured_value.tenant == captured_tenant
                            and captured_value.selected is captured_selected and captured_value.identity is not None
                            and captured_value.identity.get('role') == 'Receptionist')
                    async def current_recipient_context():
                        await self._current(value,key=key,expected=value)
                        rows = await self._choices(value.bootstrap)
                        self._require_current(key,value)
                        if value.selected not in rows:
                            raise _Denied()
                        try:
                            middle = value.bootstrap.split('.')[1]
                            claims = _json(base64.b64decode(middle + '=' * (-len(middle)%4),
                                altchars=b'-_',validate=True))
                        except Exception:
                            raise _Denied() from None
                        if (type(claims) is not dict or claims.get('account_id') != FIXTURES['Receptionist'][1]
                                or claims.get('aud') != 'raisa-account-bootstrap'
                                or claims.get('token_kind') != 'account_bootstrap'):
                            raise _Denied()
                        return True
                    await current_recipient_context()
                    if not self.binding.invitation_join_enabled or self.binding.invitation_ready() is not True:
                        await self.binding.private_recipient_current(recipient_bootstrap_bearer=value.bootstrap,
                            current=current_recipient_context, local_current=local_recipient_context)
                    self._require_current(key,value)
                return self._cookie(_reply({"enabled": True, "csrf": value.csrf,
                    "phase": "selected" if value.tenant else "choose" if value.bootstrap else "login",
                    "memberships": value.choices if value.bootstrap else [],
                    "identity": value.identity,
                    "bureau_available": value.staff_session is not None,
                    **({"invitation":self.invitation_projection(value)} if self.binding.invitation_join_enabled else {})}), key, value)
        except asyncio.CancelledError:
            self._drop(key, expected=value)
            raise
        except Exception:
            self._drop(key, expected=value)
            response = _reply({"detail": "Sign-in could not be completed. Please sign in again."}, 403)
            response.delete_cookie(COOKIE, path="/demo/stage1", httponly=True, samesite="strict")
            return response

    async def close(self):
        self._closed = True
        for key, value in list(self.sessions.items()):
            async with value.lock:
                self._drop(key,expected=value)
