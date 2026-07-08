from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.tenancy import User
from app.schemas.practice import PractitionerOut
from app.services.practice.practitioner_directory_read import (
    list_practitioner_directory,
)

router = APIRouter(prefix="/api/v1/practice", tags=["practice"])


@router.get("/practitioners", response_model=list[PractitionerOut])
def get_practitioners(
    active_only: bool = Query(True, alias="activeOnly"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_practitioner_directory(
        db=db,
        current_user=current_user,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
