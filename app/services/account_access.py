"""Restricted, explicitly injected Account database API; no tenant fallback."""
import uuid

from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.auth_service import hash_password, verify_password


def get_account_auth_db(request: Request):
    factory = getattr(request.app.state, "account_auth_session_factory", None)
    if factory is None:
        raise HTTPException(status_code=503, detail="Account authentication unavailable")
    db = factory()
    try:
        # Registration binds a verifier parameter; the reviewed factory must
        # suppress SQL parameter logging as well as use the exact auth login.
        if getattr(db.get_bind(), "hide_parameters", False) is not True:
            raise HTTPException(status_code=503, detail="Account authentication unavailable")
        identity = db.execute(text("SELECT session_user, current_user")).one()
        if tuple(identity) != ("raisa_local_account_auth", "raisa_local_account_auth"):
            raise HTTPException(status_code=503, detail="Account authentication unavailable")
        yield db
    finally:
        db.close()


def active_account(db: Session, account_id: uuid.UUID) -> bool:
    return db.execute(text("SELECT account_api.account_is_active(:account)"), {
        "account": account_id,
    }).scalar_one() is True


def _audit_login(db, account_id, allowed):
    db.execute(text("SELECT account_api.record_login(:account, :allowed)"), {
        "account": account_id, "allowed": allowed,
    })
    # A failed password response can retain its denial audit. No credentials,
    # email or token are recorded and this is not a tenant command transaction.
    db.commit()


def authenticate_account(db: Session, email: str, password: str) -> uuid.UUID:
    if not 1 <= len(email) <= 255:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    row = db.execute(text("SELECT * FROM account_api.credential_lookup(:email)"), {
        "email": email,
    }).mappings().one_or_none()
    allowed = row is not None and verify_password(password, row["password_hash"])
    account_id = row["account_id"] if row else None
    _audit_login(db, account_id, allowed)
    if not allowed:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    # Recheck after the audit commit; selection/current tenant checks recheck
    # again. This is not claimed as a cross-transaction revocation fence.
    if not active_account(db, account_id):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return account_id


def register_account(db: Session, email: str, password: str) -> uuid.UUID:
    if not 12 <= len(password.encode("utf-8")) <= 72:
        raise HTTPException(status_code=422, detail="Password must contain 12 to 72 UTF-8 bytes")
    try:
        account_id = db.execute(text("SELECT account_api.register_account(:email, :verifier)"), {
            "email": email, "verifier": hash_password(password),
        }).scalar_one()
        db.commit()
        return account_id
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account could not be registered") from None


def eligible_memberships(db: Session, account_id: uuid.UUID, membership_id=None):
    return db.execute(text("SELECT * FROM account_api.eligible_memberships(:account, :membership)"), {
        "account": account_id, "membership": membership_id,
    }).mappings().all()


def record_selection(db: Session, account_id: uuid.UUID, membership_id: uuid.UUID):
    accepted = db.execute(text("SELECT account_api.record_selection(:account, :membership)"), {
        "account": account_id, "membership": membership_id,
    }).scalar_one()
    db.commit()
    if accepted is not True:
        raise HTTPException(status_code=401, detail="Could not validate current membership")


def create_first_practice(db: Session, account_id: uuid.UUID, name: str):
    try:
        row = db.execute(text("SELECT * FROM account_api.create_first_practice(:account, :name)"), {
            "account": account_id, "name": name,
        }).mappings().one_or_none()
        if row is None:
            db.rollback()
            raise HTTPException(status_code=409, detail="First practice could not be created")
        db.commit()
        return row
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="First practice could not be created") from None
