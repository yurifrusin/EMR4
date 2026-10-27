from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import bcrypt
import jwt
from jwt import InvalidTokenError
from fastapi import HTTPException, status
from app.config import settings
from app.schemas.auth import TokenData, AccountBootstrapTokenData

TENANT_AUDIENCE = "raisa-tenant"
BOOTSTRAP_AUDIENCE = "raisa-account-bootstrap"
EXISTING_ROLES = frozenset(("GP", "Receptionist", "Nurse", "Admin", "PracticeOwner"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Retain the signing primitive; only typed builders issue new auth tokens."""
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_bootstrap_token(account_id: uuid.UUID) -> str:
    return create_access_token({
        "account_id": str(account_id), "aud": BOOTSTRAP_AUDIENCE,
        "token_kind": "account_bootstrap",
    }, timedelta(minutes=10))


def create_membership_token(membership) -> str:
    return create_access_token({
        "sub": str(membership["legacy_user_id"]),
        "account_id": str(membership["account_id"]),
        "membership_id": str(membership["membership_id"]),
        "practice_id": str(membership["practice_id"]),
        "authority_generation": membership["authority_generation"],
        "role": membership["role"], "aud": TENANT_AUDIENCE,
        "token_kind": "selected_membership",
    })


def _credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode(token: str, audience: str, required: list[str]):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm],
            audience=audience, options={"require": ["exp", "aud", "token_kind", *required]},
        )
        if payload["aud"] != audience:
            raise ValueError("audience must be exact")
        return payload
    except (InvalidTokenError, ValueError, TypeError):
        raise _credentials_exception() from None


def verify_token(token: str) -> TokenData:
    payload = _decode(token, TENANT_AUDIENCE, [
        "sub", "account_id", "membership_id", "practice_id", "authority_generation", "role",
    ])
    try:
        generation = payload["authority_generation"]
        if (payload["token_kind"] != "selected_membership" or
                type(generation) is not int or generation < 1 or payload["role"] not in EXISTING_ROLES):
            raise ValueError("invalid tenant claims")
        return TokenData(
            user_id=uuid.UUID(payload["sub"]), account_id=uuid.UUID(payload["account_id"]),
            membership_id=uuid.UUID(payload["membership_id"]), practice_id=uuid.UUID(payload["practice_id"]),
            authority_generation=generation, role=payload["role"],
        )
    except (ValueError, TypeError, AttributeError):
        raise _credentials_exception() from None


def verify_bootstrap_token(token: str) -> AccountBootstrapTokenData:
    payload = _decode(token, BOOTSTRAP_AUDIENCE, ["account_id"])
    try:
        if payload["token_kind"] != "account_bootstrap" or any(
            name in payload for name in (
                "sub", "practice_id", "membership_id", "role", "authority_generation",
            )
        ):
            raise ValueError("bootstrap cannot carry tenant authority")
        return AccountBootstrapTokenData(account_id=uuid.UUID(payload["account_id"]))
    except (ValueError, TypeError, AttributeError):
        raise _credentials_exception() from None
