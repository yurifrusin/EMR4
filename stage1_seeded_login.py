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
    lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)


class _Denied(Exception):
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
        self.binding = binding
        self.make_staff, self.drop_staff = make_staff, drop_staff
        self.sessions: dict[str, _Login] = {}

    def _alive(self, value):
        if datetime.now(timezone.utc) >= min(value.expires_at, self.binding.ends_at):
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
        self._require_current(key, expected)
        self._alive(value)
        if not value.tenant or value.selected is None:
            raise _Denied()
        # The protected backend endpoint authenticates AND checks current rows.
        me = await self._call(self.binding.account_me, tenant_bearer=value.tenant)
        self._require_current(key, expected)
        self._alive(value)
        if type(me) is not dict or set(me) != {"id", "email", "role", "practice_id"}:
            raise _Denied()
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

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, "")
        value = self.sessions.get(key)
        try:
            if request.url.query or request.headers.get("authorization") is not None:
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
                    replacement = _Login("", self.binding.ends_at, tenant=token, selected=selected[0])
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
                return self._cookie(_reply({"enabled": True, "csrf": value.csrf,
                    "phase": "selected" if value.tenant else "choose" if value.bootstrap else "login",
                    "memberships": value.choices if value.bootstrap else [],
                    "identity": value.identity,
                    "bureau_available": value.staff_session is not None}), key, value)
        except asyncio.CancelledError:
            self._drop(key, expected=value)
            raise
        except Exception:
            self._drop(key, expected=value)
            response = _reply({"detail": "Sign-in could not be completed. Please sign in again."}, 403)
            response.delete_cookie(COOKIE, path="/demo/stage1", httponly=True, samesite="strict")
            return response
