"""Pure active-location projection for the Davida read/context desk.

Side-effect-free by construction: it selects exactly ``PracticeLocation.id``
and ``.name`` scoped to the already-authenticated backend ``current_user``. It
exposes no role policy, contains no commit/flush/add/delete/normalization path
and creates no new action or resource identifier. No route or GraphQL field is
added here; database truth remains authoritative.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.tenancy import PracticeLocation, User
from app.schemas.practice_administration import ActivePracticeLocationOut


MAX_ACTIVE_LOCATION_DIRECTORY_ROWS = 200


def list_active_location_directory(
    *,
    db: Session,
    current_user: User,
) -> list[ActivePracticeLocationOut]:
    """Return the exact active-location projection for the current practice.

    The caller is an already-authenticated backend principal; no role policy is
    exposed here. Only ``PracticeLocation.id`` and ``.name`` are queried,
    scoped to ``current_user.practice_id`` with ``is_active IS TRUE``, ordered
    by ``name, id`` and bounded to a fixed maximum of 200 rows under
    ``db.no_autoflush``.
    """
    with db.no_autoflush:
        rows = (
            db.query(
                PracticeLocation.id.label("location_id"),
                PracticeLocation.name.label("location_name"),
            )
            .filter(
                PracticeLocation.practice_id == current_user.practice_id,
                PracticeLocation.is_active.is_(True),
            )
            .order_by(
                PracticeLocation.name.asc(),
                PracticeLocation.id.asc(),
            )
            .limit(MAX_ACTIVE_LOCATION_DIRECTORY_ROWS)
            .all()
        )

    return [
        ActivePracticeLocationOut(
            id=row.location_id,
            name=row.location_name,
        )
        for row in rows
    ]
