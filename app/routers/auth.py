import ipaddress

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import settings
from app.dependencies import get_current_user, oauth2_scheme
from app.models.tenancy import User
from app.schemas.auth import (
    Token, UserOut, AccountRegistrationRequest, FirstPracticeRequest,
    MembershipSelectionRequest, MembershipOut,
)
from app.services.auth_service import (
    create_bootstrap_token, create_membership_token, verify_bootstrap_token,
)
from app.services.account_access import (
    get_account_auth_db, authenticate_account, register_account, active_account,
    eligible_memberships, create_first_practice, record_selection,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _no_store(response: Response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def require_local_account_bootstrap(request: Request):
    # Synthetic onboarding remains explicitly default-off. No host-header or
    # forwarded-header substitution establishes loopback origin.
    try:
        local = request.client is not None and ipaddress.ip_address(request.client.host).is_loopback
    except ValueError:
        local = False
    if (settings.environment != "dev" or not local or
            getattr(request.app.state, "local_account_bootstrap_enabled", False) is not True):
        raise HTTPException(status_code=404, detail="Not found")


def get_current_bootstrap_account(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_account_auth_db),
):
    claims = verify_bootstrap_token(token)
    if not active_account(db, claims.account_id):
        raise HTTPException(status_code=401, detail="Could not validate account")
    return claims


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    bootstrap: bool = False,
    db: Session = Depends(get_account_auth_db),
):
    _no_store(response)
    account_id = authenticate_account(db, form_data.username, form_data.password)
    memberships = eligible_memberships(db, account_id)
    # Existing single-practice clients retain a directly usable tenant token.
    # Explicit bootstrap requests and accounts without one unambiguous current
    # membership receive no tenant claims.
    if not bootstrap and len(memberships) == 1:
        record_selection(db, account_id, memberships[0]["membership_id"])
        return Token(access_token=create_membership_token(memberships[0]))
    return Token(access_token=create_bootstrap_token(account_id))


@router.post("/register", response_model=Token, dependencies=[Depends(require_local_account_bootstrap)])
async def register(
    body: AccountRegistrationRequest, response: Response,
    db: Session = Depends(get_account_auth_db),
):
    _no_store(response)
    return Token(access_token=create_bootstrap_token(register_account(db, body.email, body.password.get_secret_value())))


@router.get("/memberships", response_model=list[MembershipOut])
async def list_memberships(
    response: Response, account=Depends(get_current_bootstrap_account),
    db: Session = Depends(get_account_auth_db),
):
    _no_store(response)
    return [MembershipOut(**row) for row in eligible_memberships(db, account.account_id)]


@router.post("/select-membership", response_model=Token)
async def select_membership(
    body: MembershipSelectionRequest, response: Response,
    account=Depends(get_current_bootstrap_account), db: Session = Depends(get_account_auth_db),
):
    _no_store(response)
    rows = eligible_memberships(db, account.account_id, body.membership_id)
    if len(rows) != 1:
        raise HTTPException(status_code=401, detail="Could not validate current membership")
    record_selection(db, account.account_id, body.membership_id)
    return Token(access_token=create_membership_token(rows[0]))


@router.post("/practices", response_model=Token, dependencies=[Depends(require_local_account_bootstrap)])
async def first_practice(
    body: FirstPracticeRequest, response: Response,
    account=Depends(get_current_bootstrap_account), db: Session = Depends(get_account_auth_db),
):
    _no_store(response)
    membership = create_first_practice(db, account.account_id, body.name)
    return Token(access_token=create_membership_token(membership))


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id, email=current_user.email,
        role=current_user.role.value, practice_id=current_user.practice_id,
    )
