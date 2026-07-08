from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.tenancy import PracticeLocation, Practitioner, User, UserRole
from app.schemas.practice import PractitionerDefaultLocationOut, PractitionerOut


ADMIN_DIRECTORY_ROLES = {UserRole.Admin, UserRole.PracticeOwner}


def _display_name(practitioner: Practitioner) -> str:
    parts = [
        str(part).strip()
        for part in (practitioner.first_name, practitioner.last_name)
        if part and str(part).strip()
    ]
    return " ".join(parts)


def _default_location_out(location: PracticeLocation | None) -> PractitionerDefaultLocationOut | None:
    if location is None:
        return None
    return PractitionerDefaultLocationOut(id=location.id, name=location.name)


def list_practitioner_directory(
    *,
    db: Session,
    current_user: User,
    active_only: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> list[PractitionerOut]:
    if not active_only and current_user.role not in ADMIN_DIRECTORY_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive practitioner directory access requires Admin or PracticeOwner",
        )

    location_join = and_(
        PracticeLocation.id == Practitioner.default_location_id,
        PracticeLocation.practice_id == current_user.practice_id,
        PracticeLocation.is_active == True,
    )
    query = (
        db.query(Practitioner, PracticeLocation)
        .outerjoin(PracticeLocation, location_join)
        .filter(Practitioner.practice_id == current_user.practice_id)
    )
    if active_only:
        query = query.filter(Practitioner.is_active == True)

    rows = (
        query.order_by(
            Practitioner.last_name.asc(),
            Practitioner.first_name.asc(),
            Practitioner.id.asc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        PractitionerOut(
            id=practitioner.id,
            displayName=_display_name(practitioner),
            roleLabel=practitioner.specialty,
            active=bool(practitioner.is_active),
            defaultLocation=_default_location_out(location),
        )
        for practitioner, location in rows
    ]
