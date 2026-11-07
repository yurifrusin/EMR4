"""Prospective owner-only onboarding. Inert until explicitly bound by a reviewed host.

No tenant is joined to the synthetic Bureau. Backend tokens stay in server memory.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
from dataclasses import dataclass, field
from datetime import datetime, timezone
import secrets
import uuid

from stage1_seeded_login import _Denied, _json, _reply, UUID

COOKIE = "stage1_owner_session"

@dataclass(frozen=True, repr=False)
class OwnerBinding:
    register: object
    login: object
    memberships: object
    create_practice: object
    select: object
    me: object
    ends_at: datetime
    enabled: bool = False
    private_owner_current: object = field(default=None, repr=False)
    invitation_join_enabled: bool = False
    invitation_issue: object = field(default=None, repr=False)
    invitation_ready: object = field(default=None, repr=False)

@dataclass(frozen=True, repr=False)
class OwnerAuthority:
    # Private verified tuple; never serialized by owner state or browser routes.
    account_id: str
    membership_id: str
    user_id: str
    practice_id: str
    role: str
    authority_generation: int

@dataclass(repr=False)
class _Owner:
    csrf: str
    bootstrap: str | None = None
    account_id: str | None = None
    tenant: str | None = None
    phase: str = "credentials"
    write_attempted: bool = False
    registration_attempted: bool = False
    identity: dict | None = None
    practice_id: str | None = None
    authority: OwnerAuthority | None = None
    invitation_attempted: bool = False
    invitation_issued: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

class OwnerController:
    def __init__(self, binding, *, origin, human_end):
        if (type(binding) is not OwnerBinding or binding.enabled is not True
                or type(binding.ends_at) is not datetime or binding.ends_at.tzinfo is None
                or human_end is None or not datetime.now(timezone.utc) < binding.ends_at <= human_end
                or not all(callable(getattr(binding, k)) for k in
                    ("register", "login", "memberships", "create_practice", "select", "me"))):
            raise ValueError("OWNER_BINDING_INVALID")
        if binding.private_owner_current is not None and not callable(binding.private_owner_current):
            raise ValueError("OWNER_PRIVATE_CALLBACK_INVALID")
        if (type(binding.invitation_join_enabled) is not bool or
                (binding.invitation_join_enabled and (binding.private_owner_current is None or
                 not callable(binding.invitation_issue) or not callable(binding.invitation_ready))) or
                (not binding.invitation_join_enabled and (binding.invitation_issue is not None or binding.invitation_ready is not None))):
            raise ValueError("OWNER_INVITATION_BINDING_INVALID")
        self._practitioner_create = None  # Optional same-owner bridge; absent preserves old response.
        self._practice_location_create = None  # Independent optional location-only bridge.
        self._invitation_owner = None
        self._closed = False
        self.binding, self.origin = binding, origin
        self.sessions = {}
        self.registration_attempts, self.creation_attempts = set(), set()
        self.attempt_key = secrets.token_bytes(32)

    def _current(self, key, value):
        if self._closed or self.sessions.get(key) is not value or datetime.now(timezone.utc) >= self.binding.ends_at:
            raise _Denied()

    async def _call(self, fn, **kwargs):
        try:
            response = await fn(**kwargs)
            if (response.status_code != 200 or len(response.content) > 16384
                    or response.headers.get("content-type", "").split(";")[0] != "application/json"):
                raise _Denied()
            return _json(response.content)
        except Exception:
            raise _Denied() from None

    @staticmethod
    def _token(data):
        import re
        if (type(data) is not dict or set(data) != {"access_token", "token_type"}
                or data["token_type"] != "bearer" or type(data["access_token"]) is not str
                or not re.fullmatch(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", data["access_token"])
                or len(data["access_token"]) > 4096):
            raise _Denied()
        return data["access_token"]

    async def _memberships(self, value, *, current=None):
        if current is not None: current()
        rows = await self._call(self.binding.memberships, bootstrap_bearer=value.bootstrap)
        if current is not None: current()
        if type(rows) is not list or len(rows) > 8:
            raise _Denied()
        seen = set()
        for row in rows:
            if (type(row) is not dict or set(row) != {"membership_id", "practice_id", "practice_name", "role"}
                    or any(type(row[k]) is not str or not UUID.fullmatch(row[k]) for k in ("membership_id", "practice_id"))
                    or type(row["practice_name"]) is not str or not 1 <= len(row["practice_name"]) <= 255
                    or row["role"] not in ("PracticeOwner", "Receptionist") or row["membership_id"] in seen):
                raise _Denied()
            seen.add(row["membership_id"])
        return rows

    async def _verified(self, value, token, rows, *, current=None):
        if current is not None: current()
        me = await self._call(self.binding.me, tenant_bearer=token)
        if current is not None: current()
        if (type(me) is not dict or set(me) != {"id", "email", "role", "practice_id"}
                or type(me["id"]) is not str or not UUID.fullmatch(me["id"])
                or type(me["email"]) is not str or not 1 <= len(me["email"]) <= 255
                or me["role"] != "PracticeOwner" or type(me["practice_id"]) is not str
                or not UUID.fullmatch(me["practice_id"])):
            raise _Denied()
        match = [r for r in rows if r["practice_id"] == me["practice_id"] and r["role"] == "PracticeOwner"]
        if len(match) != 1:
            raise _Denied()
        try:
            middle = token.split(".")[1]
            claims = _json(base64.b64decode(middle + "=" * (-len(middle) % 4), altchars=b"-_", validate=True))
        except Exception:
            raise _Denied() from None
        if (type(claims) is not dict or claims.get("account_id") != value.account_id
                or claims.get("membership_id") != match[0]["membership_id"]
                or claims.get("practice_id") != me["practice_id"] or claims.get("sub") != me["id"]
                or claims.get("role") != "PracticeOwner" or claims.get("aud") != "raisa-tenant"
                or claims.get("token_kind") != "selected_membership"
                or type(claims.get("authority_generation")) is not int):
            raise _Denied()
        if current is not None: current()
        value.practice_id = me["practice_id"]
        value.tenant = token
        value.identity = {"email": me["email"], "practice_name": match[0]["practice_name"], "role": "PracticeOwner"}
        value.phase = "verified"
        # Reuse only claims already correlated with the accepted backend /me.
        # Invalid CREATE precision/range yields no private CREATE authority; the
        # optional feature being absent preserves existing onboarding responses.
        generation = claims["authority_generation"]
        value.authority = (OwnerAuthority(value.account_id, match[0]["membership_id"],
            me["id"], me["practice_id"], "PracticeOwner", generation)
            if (1 <= generation <= 9223372036854775807
                and type(value.account_id) is str and UUID.fullmatch(value.account_id)) else None)
        return value.authority

    def practitioner_context(self, key, value):
        """Under the EXISTING per-owner lock; never acquires it recursively."""
        self._current(key, value)
        captured = (value.tenant, value.bootstrap, value.account_id, value.practice_id,
            value.csrf, value.authority)
        if (value.phase != "verified" or type(value.authority) is not OwnerAuthority
                or value.authority.role != "PracticeOwner" or value.authority.practice_id != value.practice_id):
            raise _Denied()
        authority = value.authority
        identity = dict(value.identity)
        def local():
            self._current(key, value)
            if (value.phase != "verified" or (value.tenant, value.bootstrap, value.account_id,
                    value.practice_id, value.csrf, value.authority) != captured
                    or value.identity != identity):
                raise _Denied()
            return True
        async def read_current():
            local()
            rows = await self._memberships(value, current=local)
            local()
            await self._verified(value, captured[0], rows, current=local)
            local()
            return True
        async def current():
            local()
            await read_current()
            local()
            # Reuse the already bound private current-owner service. The callback
            # receives a NONRECURSIVE fresh read and synchronous local predicate.
            await self.binding.private_owner_current(owner_tenant_bearer=captured[0],
                current=read_current, local_current=local)
            local()
            return True
        return authority, local, current

    def invitation_context(self):
        if not self.binding.invitation_join_enabled or self._invitation_owner is None:
            raise _Denied()
        key,value = self._invitation_owner
        self._current(key,value)
        if (value.phase != "verified" or not value.invitation_issued
                or self.binding.invitation_ready() is not True):
            raise _Denied()
        return (key,value,value.practice_id,value.identity["practice_name"])

    def invitation_projection(self, key, value):
        if not self.binding.invitation_join_enabled or value.phase != "verified":
            return None
        self._current(key,value)
        return {"target":"Existing synthetic receptionist", "practice_name":value.identity["practice_name"],
                "role":"Receptionist", "issued":value.invitation_issued,
                "can_issue":not value.invitation_attempted and self._invitation_owner is None
                    and self.binding.invitation_ready() is True}

    async def handle(self, request, action):
        key = request.cookies.get(COOKIE, "")
        value = self.sessions.get(key)
        try:
            if self._closed or request.url.query or request.headers.get("authorization") is not None:
                raise _Denied()
            if action == "state" and request.method == "GET" and value is None:
                if datetime.now(timezone.utc) >= self.binding.ends_at or len(self.sessions) >= 256:
                    raise _Denied()
                key, value = secrets.token_urlsafe(32), _Owner(secrets.token_urlsafe(24))
                self.sessions[key] = value
            if value is None:
                raise _Denied()
            async with value.lock:
                self._current(key, value)
                body = {}
                if request.method == "POST":
                    if (request.headers.get("origin") != self.origin
                            or request.headers.get("content-type") != "application/json"
                            or not secrets.compare_digest(request.headers.get("x-csrf-token", ""), value.csrf)):
                        raise _Denied()
                    chunks, size = [], 0
                    async for chunk in request.stream():
                        size += len(chunk)
                        if size > 4096: raise _Denied()
                        chunks.append(chunk)
                    body = _json(b"".join(chunks))
                    if type(body) is not dict: raise _Denied()
                if action in ("register", "signin") and request.method == "POST":
                    if (value.phase != "credentials" or set(body) != {"email", "password"}
                            or type(body["email"]) is not str or not 1 <= len(body["email"]) <= 254
                            or type(body["password"]) is not str or not 12 <= len(body["password"].encode("utf-8")) <= 72
                            or (action == "register" and value.registration_attempted)):
                        raise _Denied()
                    if action == "register":
                        fingerprint = hmac.digest(self.attempt_key, body["email"].strip().lower().encode("utf-8"), "sha256")
                        if fingerprint in self.registration_attempts: raise _Denied()
                        self.registration_attempts.add(fingerprint)
                        value.registration_attempted = True
                    try:
                        fn = self.binding.register if action == "register" else self.binding.login
                        args = {"email": body["email"], "password": body["password"]} if action == "register" else {"username": body["email"], "password": body["password"]}
                        token = self._token(await self._call(fn, **args))
                    finally:
                        body.clear()
                        if "args" in locals(): args.clear()
                    self._current(key, value)
                    value.bootstrap = token
                    rows = await self._memberships(value)
                    self._current(key, value)
                    try:
                        middle = token.split(".")[1]
                        claims = _json(base64.b64decode(middle + "=" * (-len(middle) % 4), altchars=b"-_", validate=True))
                        account_id = claims["account_id"]
                        if type(account_id) is not str or not UUID.fullmatch(account_id): raise _Denied()
                    except Exception:
                        raise _Denied() from None
                    # The membership endpoint accepted this same server-origin token first.
                    value.account_id = account_id
                    value.phase = "pending" if not rows and account_id not in self.creation_attempts else "inspect"
                    # Rotate both cookie and CSRF synchronously after authentication.
                    self._current(key, value)
                    self.sessions.pop(key)
                    key = secrets.token_urlsafe(32)
                    value.csrf = secrets.token_urlsafe(24)
                    self.sessions[key] = value
                elif action == "create" and request.method == "POST":
                    if (value.phase != "pending" or value.write_attempted or set(body) != {"name", "confirmed"}
                            or body["confirmed"] is not True or type(body["name"]) is not str
                            or not 1 <= len(body["name"]) <= 255): raise _Denied()
                    if value.account_id in self.creation_attempts: raise _Denied()
                    self.creation_attempts.add(value.account_id)
                    value.write_attempted = True
                    value.phase = "inspect"
                    try:
                        token = self._token(await self._call(self.binding.create_practice,
                            bootstrap_bearer=value.bootstrap, name=body["name"]))
                        self._current(key, value)
                        rows = await self._memberships(value)
                        self._current(key, value)
                        await self._verified(value, token, rows)
                        self._current(key, value)
                    except _Denied:
                        # The write might have committed; retain bootstrap for explicit inspection.
                        value.phase = "inspect"
                elif action == "invite" and request.method == "POST":
                    if (not self.binding.invitation_join_enabled or value.phase != "verified"
                            or body != {"confirmed":True} or type(body["confirmed"]) is not bool
                            or value.invitation_attempted or self._invitation_owner is not None
                            or self.binding.invitation_ready() is not True):
                        raise _Denied()
                    rows = await self._memberships(value)
                    self._current(key,value)
                    await self._verified(value,value.tenant,rows)
                    self._current(key,value)
                    if self._invitation_owner is not None or self.binding.invitation_ready() is not True:
                        raise _Denied()  # Recheck after the awaited current-authority reads.
                    value.invitation_attempted = True
                    self._invitation_owner = (key,value)  # Consume before dispatch, including ambiguous failure.
                    receipt = await self._call(self.binding.invitation_issue,
                        tenant_bearer=value.tenant,idempotency_key=str(uuid.uuid4()))
                    self._current(key,value)
                    if (type(receipt) is not dict or set(receipt) != {"state","created"}
                            or receipt["state"] != "pending" or receipt["created"] is not True):
                        raise _Denied()
                    value.invitation_issued = True
                    value.csrf = secrets.token_urlsafe(24)
                elif action == "inspect" and request.method == "POST":
                    if body != {} or value.phase != "inspect" or not value.bootstrap: raise _Denied()
                    rows = await self._memberships(value)
                    self._current(key, value)
                    owners = [r for r in rows if r["role"] == "PracticeOwner"]
                    if len(rows) == 1 and len(owners) == 1:
                        token = self._token(await self._call(self.binding.select,
                            bootstrap_bearer=value.bootstrap, membership_id=owners[0]["membership_id"]))
                        self._current(key, value)
                        await self._verified(value, token, rows)
                        self._current(key, value)
                elif action == "state" and request.method == "GET":
                    if value.phase == "verified":
                        rows = await self._memberships(value)
                        self._current(key, value)
                        await self._verified(value, value.tenant, rows)
                        self._current(key, value)
                else: raise _Denied()
                if (self._practitioner_create is None and self._practice_location_create is None
                        and value.phase == 'verified'
                        and self.binding.private_owner_current is not None):
                    self._current(key,value)
                    # _verified accepted this same tenant token through current
                    # backend /me and membership correlation; no browser token.
                    captured_key, captured_value = key, value
                    captured_owner = value.tenant
                    captured_bootstrap = value.bootstrap
                    def local_owner_context():
                        self._current(captured_key,captured_value)  # Synchronous identity/closed/expiry checks.
                        return (captured_value.phase == 'verified' and captured_value.tenant == captured_owner
                            and captured_value.bootstrap == captured_bootstrap)
                    async def current_owner_context():
                        self._current(key,value)
                        rows = await self._memberships(value)
                        self._current(key,value)
                        await self._verified(value,value.tenant,rows)
                        self._current(key,value)
                        return True
                    await self.binding.private_owner_current(owner_tenant_bearer=value.tenant,
                        current=current_owner_context, local_current=local_owner_context)
                    self._current(key,value)
                create_projection = {}
                if self._practitioner_create is not None:
                    scope = await self._practitioner_create.owner_scope(key, value)
                    self._current(key, value)
                    create_projection = {"practitioner_create_scope": scope}
                if self._practice_location_create is not None:
                    location_scope = await self._practice_location_create.owner_scope(key, value)
                    self._current(key, value)
                    create_projection["practice_location_create_scope"] = location_scope
                response = _reply({"enabled": True, "csrf": value.csrf, "phase": value.phase,
                    **create_projection,
                    "identity": value.identity if value.phase == "verified" else None,
                    **({"invitation":self.invitation_projection(key,value)} if self.binding.invitation_join_enabled else {})})
                response.set_cookie(COOKIE, key, httponly=True, samesite="strict", secure=False,
                    path="/demo/stage1", max_age=max(1, int((self.binding.ends_at-datetime.now(timezone.utc)).total_seconds())))
                return response
        except asyncio.CancelledError:
            if value is not None: self.sessions.pop(key, None)
            raise
        except Exception:
            # Retain the latch in this session: a failed/uncertain write cannot be retried.
            return _reply({"detail": "Onboarding could not be completed. Sign in or inspect the current account."}, 403)

    async def close(self):
        self._closed = True
        for key, value in list(self.sessions.items()):
            async with value.lock:
                value.bootstrap = value.tenant = None
                value.account_id = value.identity = value.authority = None
                self.sessions.pop(key,None)
        self.registration_attempts.clear()
        self.creation_attempts.clear()
        self.attempt_key = b''
