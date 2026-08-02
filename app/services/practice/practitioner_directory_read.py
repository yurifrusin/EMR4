from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.tenancy import PracticeLocation, Practitioner, User, UserRole
from app.schemas.practice import PractitionerDefaultLocationOut, PractitionerOut


ADMIN_DIRECTORY_ROLES = {UserRole.Admin, UserRole.PracticeOwner}


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
        db.query(
            Practitioner.id.label("practitioner_id"),
            Practitioner.first_name,
            Practitioner.last_name,
            Practitioner.specialty,
            Practitioner.is_active.label("practitioner_active"),
            PracticeLocation.id.label("location_id"),
            PracticeLocation.name.label("location_name"),
        )
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
            id=row.practitioner_id,
            displayName=" ".join(
                part.strip()
                for part in (row.first_name, row.last_name)
                if part and part.strip()
            ),
            roleLabel=row.specialty,
            active=bool(row.practitioner_active),
            defaultLocation=(
                PractitionerDefaultLocationOut(
                    id=row.location_id,
                    name=row.location_name,
                )
                if row.location_id is not None
                else None
            ),
        )
        for row in rows
    ]
