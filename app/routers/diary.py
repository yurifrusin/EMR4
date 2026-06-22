import json
import uuid
from datetime import date
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user
from app.models.tenancy import Practitioner, User, PracticeLocation
from app.models.diary import DiaryTemplate, Room, DiaryRoster, WaitingArea
from app.schemas.diary import (
    DiaryTemplateOut, DiaryRosterOut, DiaryRosterEntryOut,
    WaitingAreaOut, PracticeLocationOut,
)

router = APIRouter(prefix="/api/v1/diary", tags=["diary"])

_TEMPLATE_JSON = Path(__file__).resolve().parents[2] / "diary_template.json"


def _load_json_fallback() -> dict:
    with open(_TEMPLATE_JSON, encoding="utf-8") as f:
        return json.load(f)


def _ensure_location(
    location_id: Optional[uuid.UUID],
    practice_id: uuid.UUID,
    db: Session,
) -> None:
    """Raise 404 if location_id is not active and owned by this practice."""
    if not location_id:
        return
    exists = db.query(PracticeLocation.id).filter(
        PracticeLocation.id == location_id,
        PracticeLocation.practice_id == practice_id,
        PracticeLocation.is_active == True,
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Practice location not found")


def _practitioner_ids_by_ahpra(db: Session, practice_id) -> dict[str, str]:
    practitioners = (
        db.query(Practitioner)
        .filter(
            Practitioner.practice_id == practice_id,
            Practitioner.ahpra_number.isnot(None),
        )
        .all()
    )
    return {p.ahpra_number: p.id for p in practitioners if p.ahpra_number}


def _load_with_joins(q):
    from app.models.diary import DiaryColumn as _DC
    return q.options(joinedload(DiaryTemplate.columns).joinedload(_DC.breaks))


def _db_template_to_out(tmpl: DiaryTemplate, db: Session) -> DiaryTemplateOut:
    ahpra_to_id = _practitioner_ids_by_ahpra(db, tmpl.practice_id)
    return DiaryTemplateOut(
        practice_name=tmpl.practice_name,
        location_id=tmpl.location_id,
        slot_start=tmpl.slot_start,
        slot_end=tmpl.slot_end,
        slot_interval_minutes=tmpl.slot_interval_minutes,
        footer=tmpl.footer or [],
        columns=[
            {
                "room_label": c.room_label,
                "assignment": c.assignment,
                "practitioner_id": c.practitioner_id or ahpra_to_id.get(c.practitioner_ahpra),
                "practitioner_ahpra": c.practitioner_ahpra,
                "tint_hex": c.tint_hex,
                "slot_interval_minutes": c.slot_interval_minutes,
                "breaks": c.breaks,
            }
            for c in tmpl.columns
            if c.is_active
        ],
    )


@router.get("/locations", response_model=list[PracticeLocationOut])
def get_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active practice locations for the authenticated user's practice."""
    return (
        db.query(PracticeLocation)
        .filter(
            PracticeLocation.practice_id == current_user.practice_id,
            PracticeLocation.is_active == True,
        )
        .order_by(PracticeLocation.name)
        .all()
    )


@router.get("/waiting-areas", response_model=list[WaitingAreaOut])
def get_waiting_areas(
    location_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List named physical waiting areas for the practice, ordered by display_order.

    If location_id is supplied, only waiting areas at that location are returned.
    """
    _ensure_location(location_id, current_user.practice_id, db)
    q = (
        db.query(WaitingArea)
        .filter(
            WaitingArea.practice_id == current_user.practice_id,
            WaitingArea.is_active == True,
        )
    )
    if location_id:
        q = q.filter(WaitingArea.location_id == location_id)
    return q.order_by(WaitingArea.display_order).all()


@router.get("/template", response_model=DiaryTemplateOut)
def get_diary_template(
    location_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the diary template for the authenticated user's practice.

    Fallback chain (first match wins):
      1. Location-specific template for location_id (if supplied)
      2. Practice-wide template (location_id IS NULL)
      3. Static diary_template.json (no DB record at all)

    Returns 404 if location_id is cross-practice or inactive.
    """
    _ensure_location(location_id, current_user.practice_id, db)

    practice_id = current_user.practice_id
    tmpl = None

    if location_id:
        tmpl = _load_with_joins(
            db.query(DiaryTemplate).filter(
                DiaryTemplate.practice_id == practice_id,
                DiaryTemplate.location_id == location_id,
            )
        ).first()

    if tmpl is None:
        tmpl = _load_with_joins(
            db.query(DiaryTemplate).filter(
                DiaryTemplate.practice_id == practice_id,
                DiaryTemplate.location_id.is_(None),
            )
        ).first()

    if tmpl is not None:
        return _db_template_to_out(tmpl, db)

    # JSON fallback when no DB record exists for this practice yet
    if not _TEMPLATE_JSON.exists():
        raise HTTPException(status_code=404, detail="No diary template configured for this practice")
    raw = _load_json_fallback()
    sd = raw.get("slot_defaults", {})
    ahpra_to_id = _practitioner_ids_by_ahpra(db, practice_id)
    from datetime import time as _time

    def _parse_time(s: str) -> _time:
        h, m = map(int, s.split(":"))
        return _time(h, m)

    cols = []
    for c in raw.get("columns", []):
        cols.append({
            "room_label": c.get("room_label", ""),
            "assignment": c.get("assignment"),
            "practitioner_id": ahpra_to_id.get(c.get("practitioner_ahpra")),
            "practitioner_ahpra": c.get("practitioner_ahpra"),
            "tint_hex": c.get("tint"),
            "breaks": [
                {
                    "label": b["label"],
                    "from_time": _parse_time(b["from"]),
                    "to_time": _parse_time(b["to"]),
                }
                for b in c.get("breaks", [])
            ],
        })
    return DiaryTemplateOut(
        practice_name=raw.get("practice_name"),
        location_id=None,
        slot_start=_parse_time(sd.get("start", "09:00")),
        slot_end=_parse_time(sd.get("end", "17:00")),
        slot_interval_minutes=sd.get("interval_minutes", 15),
        footer=raw.get("footer", []),
        columns=cols,
    )


@router.get("/roster", response_model=DiaryRosterOut)
def get_diary_roster(
    roster_date: date = Query(..., alias="date", description="Date in YYYY-MM-DD format"),
    location_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the room roster for the authenticated user's practice on the given date.

    If location_id is supplied, only rooms at that location are included.
    Returns an empty entries list if no matching rooms are configured.
    """
    _ensure_location(location_id, current_user.practice_id, db)

    q = db.query(Room).filter(
        Room.practice_id == current_user.practice_id,
        Room.is_active == True,
    )
    if location_id:
        q = q.filter(Room.location_id == location_id)
    rooms = q.order_by(Room.display_order).all()

    if not rooms:
        return DiaryRosterOut(date=roster_date, entries=[])

    room_ids = [r.id for r in rooms]
    roster_by_room = {
        entry.room_id: entry
        for entry in db.query(DiaryRoster).filter(
            DiaryRoster.practice_id == current_user.practice_id,
            DiaryRoster.room_id.in_(room_ids),
            DiaryRoster.roster_date == roster_date,
        ).all()
    }

    entries = [
        DiaryRosterEntryOut(
            room_id=room.id,
            room_name=room.name,
            display_order=room.display_order,
            location_id=room.location_id,
            practitioner_id=roster_by_room[room.id].practitioner_id if room.id in roster_by_room else None,
            practitioner_ahpra=roster_by_room[room.id].practitioner_ahpra if room.id in roster_by_room else None,
            label=roster_by_room[room.id].label if room.id in roster_by_room else None,
        )
        for room in rooms
    ]
    return DiaryRosterOut(date=roster_date, entries=entries)
