from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text, func
from app.database import SessionLocal
from app.services.auth_service import verify_token
from app.models.tenancy import User, UserRole, Practice
from app.models.account_membership import PracticeMembership, PracticeMembershipRole

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
    claims = verify_token(token)  # Reject bootstrap before establishing RLS context.
    db.execute(
        text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
        {"practice_id": str(claims.practice_id)},
    )
    # One tenant SELECT checks current state and role/generation agreement. The
    # verifier-free exact-ID function is the only global Account access here.
    user = (
        db.query(User)
        .join(PracticeMembership, (
            (PracticeMembership.legacy_user_id == User.id) &
            (PracticeMembership.practice_id == User.practice_id)
        ))
        .join(PracticeMembershipRole, PracticeMembershipRole.membership_id == PracticeMembership.id)
        .join(Practice, Practice.id == PracticeMembership.practice_id)
        .filter(
            User.id == claims.user_id,
            User.practice_id == claims.practice_id,
            User.is_active.is_(True),
            User.authority_generation == claims.authority_generation,
            User.role == UserRole(claims.role),
            PracticeMembership.id == claims.membership_id,
            PracticeMembership.account_id == claims.account_id,
            PracticeMembership.practice_id == claims.practice_id,
            PracticeMembership.is_active.is_(True),
            PracticeMembership.authority_generation == claims.authority_generation,
            PracticeMembershipRole.role == claims.role,
            func.account_api.account_is_active(claims.account_id).is_(True),
        ).one_or_none()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate current membership",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return checker
