from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.tenancy import Practice, User
from app.schemas.practice import PracticeContextOut, PractitionerOut
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

@router.get("/context", response_model=PracticeContextOut)
def get_practice_context(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    response.headers["Cache-Control"] = "no-store"
    if request.url.query:
        raise HTTPException(status_code=400, detail="Practice context unavailable", headers={"Cache-Control": "no-store"})
    row = db.query(Practice.id, Practice.timezone).filter(
        Practice.id == current_user.practice_id
    ).one_or_none()
    if row is None or type(row.timezone) is not str or not row.timezone or row.timezone != row.timezone.strip():
        raise HTTPException(status_code=503, detail="Practice context unavailable", headers={"Cache-Control": "no-store"})
    try:
        ZoneInfo(row.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=503, detail="Practice context unavailable", headers={"Cache-Control": "no-store"}) from None
    return PracticeContextOut(practice_id=row.id, timezone=row.timezone)