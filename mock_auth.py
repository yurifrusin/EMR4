"""Synthetic, local-only organisation authorization lifecycle for development.

This models current membership, delegated scope, windows and revocation. It
does not verify a person or implement PRODA. A separately qualified local JWT
codec must sign and verify tokens; this module never accepts an unsigned token.
No web route, database, provider, appointment write or clinical data is here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import re
import secrets
import threading
from typing import Mapping, Protocol


ISSUER = "urn:raisa:mock-proda"
AUDIENCE = "raisa-local-demo"
MAX_TOKEN_SECONDS = 300
SCOPES = frozenset({"demo:use", "proposal:create"})
_USER = re.compile(r"mock-user:[a-z0-9-]{1,40}\Z")
_ORG = re.compile(r"mock-org:[a-z0-9-]{1,40}\Z")
_UTC_INSTANT = re.compile(r"20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
_CLAIM_KEYS = frozenset({"iss", "aud", "mock", "sub", "org", "scope",
                         "iat", "nbf", "exp", "jti"})


class AuthDenied(ValueError):
    """Safe reason codes only, without identity or token material."""


class LocalJwtCodec(Protocol):
    """Injected qualified codec; verify must reject bad signature/algorithm."""

    def issue(self, claims: Mapping[str, object]) -> str: ...

    def verify(self, token: str) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class _Window:
    starts_at: datetime
    ends_at: datetime
    revoked: bool
    revision: int

    def active(self, now: datetime) -> bool:
        return not self.revoked and self.starts_at <= now < self.ends_at


@dataclass(frozen=True)
class _Issued:
    user_id: str
    org_id: str
    scopes: tuple[str, ...]
    membership_revision: int
    delegation_revisions: tuple[int, ...]
    expires_at: int


@dataclass(frozen=True)
class Authorization:
    """Synthetic authorization result; never appointment-write authority."""

    user_id: str
    org_id: str
    granted_scope: str
    mock: bool = True


def _instant(value: object) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise AuthDenied("WINDOW_INVALID")
        return value.astimezone(timezone.utc)
    if (type(value) is not str or _UTC_INSTANT.fullmatch(value) is None):
        raise AuthDenied("WINDOW_INVALID")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthDenied("WINDOW_INVALID") from exc


def _now(value: datetime | None) -> datetime:
    return datetime.now(timezone.utc) if value is None else _instant(value)


def _identity(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise AuthDenied("SYNTHETIC_ID_REQUIRED")
    return value


def _window(start: object, end: object, *, revoked: bool,
            revision: int) -> _Window:
    first, last = _instant(start), _instant(end)
    if first >= last or type(revoked) is not bool:
        raise AuthDenied("WINDOW_INVALID")
    return _Window(first, last, revoked, revision)


class MockOrgAuth:
    """Coordinator-owned, process-local state. Never expose mutations to UI."""

    def __init__(self, *, max_token_seconds: int = MAX_TOKEN_SECONDS) -> None:
        if type(max_token_seconds) is not int or max_token_seconds not in (MAX_TOKEN_SECONDS, 86400):
            raise AuthDenied("TOKEN_DURATION_INVALID")
        self._max_token_seconds = max_token_seconds
        self._users: set[str] = set()
        self._members: dict[tuple[str, str], _Window] = {}
        self._delegations: dict[tuple[str, str, str], _Window] = {}
        self._issued: dict[str, _Issued] = {}
        self._revision = 0
        self._lock = threading.RLock()

    @classmethod
    def from_seed(cls, document: Mapping[str, object], *,
                  max_token_seconds: int = MAX_TOKEN_SECONDS) -> MockOrgAuth:
        """Load an authored synthetic document supplied by the trusted caller."""
        if (type(document) is not dict or set(document) !=
                {"schema", "users", "memberships", "delegations"}
                or document["schema"] != "raisa.mock_org_auth_seed.v1"
                or type(document["users"]) is not list
                or type(document["memberships"]) is not list
                or type(document["delegations"]) is not list):
            raise AuthDenied("SEED_INVALID")
        store = cls(max_token_seconds=max_token_seconds)
        for user in document["users"]:
            store.add_synthetic_user(user)
        if len(store._users) != len(document["users"]):
            raise AuthDenied("SEED_DUPLICATE")
        for row in document["memberships"]:
            if type(row) is not dict or set(row) != {
                    "user_id", "org_id", "starts_at", "ends_at", "revoked"}:
                raise AuthDenied("SEED_INVALID")
            key = (_identity(row["user_id"], _USER),
                   _identity(row["org_id"], _ORG))
            if key in store._members:
                raise AuthDenied("SEED_DUPLICATE")
            store.put_member(**row)
        for row in document["delegations"]:
            if type(row) is not dict or set(row) != {
                    "user_id", "org_id", "scope", "starts_at", "ends_at", "revoked"}:
                raise AuthDenied("SEED_INVALID")
            if type(row["scope"]) is not str or row["scope"] not in SCOPES:
                raise AuthDenied("SEED_INVALID")
            key = (_identity(row["user_id"], _USER),
                   _identity(row["org_id"], _ORG), row["scope"])
            if key in store._delegations:
                raise AuthDenied("SEED_DUPLICATE")
            store.put_delegation(**row)
        return store

    def _next_revision(self) -> int:
        self._revision += 1
        return self._revision

    def add_synthetic_user(self, user_id: str) -> None:
        user_id = _identity(user_id, _USER)
        with self._lock:
            if user_id in self._users:
                raise AuthDenied("USER_EXISTS")
            self._users.add(user_id)

    def put_member(self, *, user_id: str, org_id: str,
                   starts_at: object, ends_at: object,
                   revoked: bool = False) -> None:
        user_id, org_id = _identity(user_id, _USER), _identity(org_id, _ORG)
        with self._lock:
            if user_id not in self._users:
                raise AuthDenied("USER_UNKNOWN")
            self._members[(user_id, org_id)] = _window(
                starts_at, ends_at, revoked=revoked,
                revision=self._next_revision())

    def put_delegation(self, *, user_id: str, org_id: str, scope: str,
                       starts_at: object, ends_at: object,
                       revoked: bool = False) -> None:
        user_id, org_id = _identity(user_id, _USER), _identity(org_id, _ORG)
        if type(scope) is not str or scope not in SCOPES:
            raise AuthDenied("SCOPE_UNAVAILABLE")
        with self._lock:
            if user_id not in self._users or (user_id, org_id) not in self._members:
                raise AuthDenied("MEMBERSHIP_UNKNOWN")
            self._delegations[(user_id, org_id, scope)] = _window(
                starts_at, ends_at, revoked=revoked,
                revision=self._next_revision())

    def revoke_member(self, *, user_id: str, org_id: str) -> None:
        key = (_identity(user_id, _USER), _identity(org_id, _ORG))
        with self._lock:
            old = self._members.get(key)
            if old is None:
                raise AuthDenied("MEMBERSHIP_UNKNOWN")
            self._members[key] = _Window(old.starts_at, old.ends_at,
                                         True, self._next_revision())

    def revoke_delegation(self, *, user_id: str, org_id: str,
                          scope: str) -> None:
        if type(scope) is not str or scope not in SCOPES:
            raise AuthDenied("SCOPE_UNAVAILABLE")
        key = (_identity(user_id, _USER), _identity(org_id, _ORG), scope)
        with self._lock:
            old = self._delegations.get(key)
            if old is None:
                raise AuthDenied("DELEGATION_UNKNOWN")
            self._delegations[key] = _Window(old.starts_at, old.ends_at,
                                             True, self._next_revision())

    def issue(self, *, selected_user_id: str, org_id: str,
              scopes: tuple[str, ...], codec: LocalJwtCodec,
              now: datetime | None = None) -> str:
        """Selection is an explicit simulation, never proof of this person."""
        user_id = _identity(selected_user_id, _USER)
        org_id = _identity(org_id, _ORG)
        if (type(scopes) is not tuple or not scopes or len(scopes) > len(SCOPES)
                or any(type(scope) is not str or scope not in SCOPES
                       for scope in scopes)
                or tuple(sorted(set(scopes))) != scopes):
            raise AuthDenied("SCOPE_UNAVAILABLE")
        instant = _now(now)
        with self._lock:
            member = self._members.get((user_id, org_id))
            delegated = [self._delegations.get((user_id, org_id, scope))
                         for scope in scopes]
            if (user_id not in self._users or member is None
                    or not member.active(instant)):
                raise AuthDenied("MEMBERSHIP_INACTIVE")
            if any(row is None or not row.active(instant) for row in delegated):
                raise AuthDenied("DELEGATION_INACTIVE")
            issued_at = int(instant.timestamp())
            expiry = min(issued_at + self._max_token_seconds,
                         int(member.ends_at.timestamp()),
                         *(int(row.ends_at.timestamp()) for row in delegated))
            if expiry <= issued_at:
                raise AuthDenied("WINDOW_INACTIVE")
            jti = secrets.token_urlsafe(24)
            claims: dict[str, object] = {
                "iss": ISSUER, "aud": AUDIENCE, "mock": True,
                "sub": user_id, "org": org_id, "scope": " ".join(scopes),
                "iat": issued_at, "nbf": issued_at, "exp": expiry, "jti": jti,
            }
            try:
                token = codec.issue(claims)
            except Exception as exc:
                raise AuthDenied("TOKEN_ISSUE_FAILED") from exc
            if type(token) is not str or not token:
                raise AuthDenied("TOKEN_ISSUE_FAILED")
            self._issued[jti] = _Issued(
                user_id, org_id, scopes, member.revision,
                tuple(row.revision for row in delegated), expiry)
            for old_jti, old in tuple(self._issued.items()):
                if old.expires_at <= issued_at:
                    del self._issued[old_jti]
            return token

    def authorize(self, token: str, *, org_id: str, required_scope: str,
                  codec: LocalJwtCodec,
                  now: datetime | None = None) -> Authorization:
        """Verify signature, token and current server-owned state every time."""
        if type(token) is not str or not token or required_scope not in SCOPES:
            raise AuthDenied("TOKEN_INVALID")
        org_id = _identity(org_id, _ORG)
        instant = _now(now)
        try:
            claims = codec.verify(token)
        except Exception as exc:
            raise AuthDenied("TOKEN_INVALID") from exc
        if type(claims) is not dict or set(claims) != _CLAIM_KEYS:
            raise AuthDenied("TOKEN_INVALID")
        if (claims["iss"] != ISSUER or claims["aud"] != AUDIENCE
                or claims["mock"] is not True
                or type(claims["sub"]) is not str
                or _USER.fullmatch(claims["sub"]) is None
                or claims["org"] != org_id
                or type(claims["scope"]) is not str
                or type(claims["jti"]) is not str
                or len(claims["jti"]) < 24
                or any(type(claims[key]) is not int
                       for key in ("iat", "nbf", "exp"))):
            raise AuthDenied("TOKEN_INVALID")
        scopes = tuple(claims["scope"].split(" "))
        if (not scopes or tuple(sorted(set(scopes))) != scopes
                or not set(scopes) <= SCOPES or required_scope not in scopes
                or claims["iat"] != claims["nbf"]
                or not claims["iat"] <= int(instant.timestamp()) < claims["exp"]
                or claims["exp"] - claims["iat"] > self._max_token_seconds):
            raise AuthDenied("TOKEN_INVALID")
        user_id = claims["sub"]
        with self._lock:
            issued = self._issued.get(claims["jti"])
            member = self._members.get((user_id, org_id))
            delegated = [self._delegations.get((user_id, org_id, scope))
                         for scope in scopes]
            if (issued is None or issued.user_id != user_id
                    or issued.org_id != org_id or issued.scopes != scopes
                    or issued.expires_at != claims["exp"]
                    or member is None or not member.active(instant)
                    or issued.membership_revision != member.revision
                    or any(row is None or not row.active(instant)
                           for row in delegated)
                    or issued.delegation_revisions !=
                       tuple(row.revision for row in delegated)):
                raise AuthDenied("CURRENT_AUTHORIZATION_INACTIVE")
        return Authorization(user_id, org_id, required_scope)
