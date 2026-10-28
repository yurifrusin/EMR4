"""Trusted server-only local synthetic invitation commands. No HTTP surface.

The existing private Account-auth engine is injected by the reviewed server.
Never supply this object/engine to a browser/model or treat DB trust as JWT proof.
No account_access helper is called: those helpers commit their transactions.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import re
import secrets
import uuid

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from app.services import auth_service


class InvitationDenied(RuntimeError):
    def __init__(self):
        super().__init__("invitation denied")


@dataclass(frozen=True)
class _Owner:
    account: uuid.UUID
    membership: uuid.UUID
    user: uuid.UUID
    practice: uuid.UUID
    role: str
    generation: int
    expiry: datetime


def _expiry(payload):
    value = payload.get("exp")
    if type(value) is not int or not 1 <= value <= 253402300799:
        raise InvitationDenied()
    expiry = datetime.fromtimestamp(value, timezone.utc)
    if expiry <= datetime.now(timezone.utc):
        raise InvitationDenied()
    return expiry


def _owner(token):
    try:
        # Both calls use the existing exact signature/audience/kind/schema rules;
        # expiry is additionally retained, rather than discarded by TokenData.
        claims = auth_service.verify_token(token)
        payload = auth_service._decode(token, auth_service.TENANT_AUDIENCE, [
            "sub", "account_id", "membership_id", "practice_id", "authority_generation", "role"])
        if claims.role != "PracticeOwner":
            raise InvitationDenied()
        return _Owner(claims.account_id, claims.membership_id, claims.user_id,
                      claims.practice_id, claims.role, claims.authority_generation, _expiry(payload))
    except Exception:
        raise InvitationDenied() from None


def _account(token):
    try:
        claims = auth_service.verify_bootstrap_token(token)
        payload = auth_service._decode(token, auth_service.BOOTSTRAP_AUDIENCE, ["account_id"])
        return claims.account_id, _expiry(payload)
    except Exception:
        raise InvitationDenied() from None


def _uuid(value):
    if type(value) is not uuid.UUID:
        raise InvitationDenied()
    return value


def _params(owner):
    return dict(account=owner.account, membership=owner.membership, user=owner.user,
                practice=owner.practice, role=owner.role, generation=owner.generation, expiry=owner.expiry)


_INVITATION_VERIFIER_DOMAIN = b"raisa.local-synthetic-invitation.v1\x00"


def _verifier_digest(secret):
    return hashlib.sha256(_INVITATION_VERIFIER_DOMAIN + secret.encode("ascii")).digest()


OWNER_CALL = ":account,:membership,:user,:practice,:role,:generation,:expiry"


class LocalSyntheticInvitationService:
    """Internal dependency; each command owns one fresh READ COMMITTED transaction.

    Successful issue returns a secret exactly once, after commit. Its caller must
    use the reviewed synthetic handoff with no-store/redaction, never logging or
    generic dataclass serialization. A compromised trusted caller can bypass this
    adapter and lie to the DB; that is outside the accepted design guarantee.
    """
    def __init__(self, auth_engine):
        if auth_engine.echo or auth_engine.hide_parameters is not True:
            raise InvitationDenied()
        self._engine = auth_engine

    def _identity(self, connection):
        if tuple(connection.execute(text("SELECT session_user,current_user")).one()) != (
                "raisa_local_account_auth", "raisa_local_account_auth"):
            raise InvitationDenied()
        if connection.execute(text("SHOW transaction_isolation")).scalar_one() != "read committed":
            raise InvitationDenied()

    def issue(self, owner_token, fixture_binding_id, role, ttl_seconds, issue_key):
        owner = _owner(owner_token)  # Authenticate before starting the command.
        _uuid(fixture_binding_id); _uuid(issue_key)
        if type(role) is not str or role not in ("GP", "Receptionist") or type(ttl_seconds) is not int or not 60 <= ttl_seconds <= 3600:
            raise InvitationDenied()
        secret = secrets.token_urlsafe(32)
        params = dict(_params(owner), fixture=fixture_binding_id, requested_role=role,
                      ttl=ttl_seconds, key=issue_key, digest=_verifier_digest(secret))
        try:
            with self._engine.begin() as connection:
                self._identity(connection)
                row = connection.execute(text("SELECT * FROM account_api.local_invitation_issue("
                    + OWNER_CALL + ",:fixture,:requested_role,:ttl,:key,:digest)"), params).mappings().one()
                receipt = {name: row[name] for name in ("invitation_id", "state", "expires_at", "created")}
            # The generated replacement secret/digest never participates in replay
            # identity and is never released on an existing-key receipt.
            return receipt, secret if receipt["created"] is True else None
        except DBAPIError:
            raise InvitationDenied() from None
        finally:
            params.pop("digest", None)
            secret = None  # Not a claim of guaranteed Python-memory zeroization.

    def accept(self, account_token, invitation_id, secret):
        account, expiry = _account(account_token)
        _uuid(invitation_id)
        if type(secret) is not str or re.fullmatch(r"[A-Za-z0-9_-]{43}", secret) is None:
            raise InvitationDenied()
        params = dict(account=account, expiry=expiry, invitation=invitation_id)
        try:
            with self._engine.begin() as connection:
                self._identity(connection)
                locked = connection.execute(text("SELECT * FROM account_api.local_invitation_accept_lock("
                    ":account,:expiry,:invitation)"), params).mappings().one()
                stored = bytes(locked["verifier_digest"])
                if len(stored) != 32 or not hmac.compare_digest(
                        stored, _verifier_digest(secret)):
                    raise InvitationDenied()  # Context manager rolls back, no finish.
                row = connection.execute(text("SELECT * FROM account_api.local_invitation_accept_finish("
                    ":account,:expiry,:invitation)"), params).mappings().one()
                receipt = {name: row[name] for name in ("membership_id", "practice_id", "role")}
            return receipt  # Committed membership only; never implicit selection/token issuance.
        except DBAPIError:
            raise InvitationDenied() from None

    def revoke(self, owner_token, invitation_id):
        owner = _owner(owner_token)
        _uuid(invitation_id)
        try:
            with self._engine.begin() as connection:
                self._identity(connection)
                row = connection.execute(text("SELECT * FROM account_api.local_invitation_revoke("
                    + OWNER_CALL + ",:invitation)"), dict(_params(owner), invitation=invitation_id)).mappings().one()
                receipt = {name: row[name] for name in ("invitation_id", "state")}
            return receipt
        except DBAPIError:
            raise InvitationDenied() from None
