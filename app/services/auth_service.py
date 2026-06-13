from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings
from app.schemas.auth import TokenData


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> TokenData:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        practice_id: str = payload.get("practice_id")
        role: str = payload.get("role")
        if user_id is None or practice_id is None:
            raise credentials_exc
        return TokenData(
            user_id=uuid.UUID(user_id),
            practice_id=uuid.UUID(practice_id),
            role=role,
        )
    except (JWTError, ValueError):
        raise credentials_exc
