from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text
from app.database import SessionLocal
from app.services.auth_service import verify_token
from app.models.tenancy import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_command_session_factory(
    request_db: Session = Depends(get_db),
) -> Callable[[], Session]:
    """Return the configured factory for a fresh, command-owned transaction."""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=request_db.get_bind(),
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    token_data = verify_token(token)
    db.execute(
        text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
        {"practice_id": str(token_data.practice_id)},
    )
    user = db.query(User).filter(User.id == token_data.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    if user.practice_id != token_data.practice_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token practice does not match the current user practice",
        )
    return user


def require_role(*roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return checker
