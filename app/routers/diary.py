import json
from datetime import date
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user
from app.models.tenancy import User
from app.models.diary import DiaryTemplate, Room, DiaryRoster
from app.schemas.diary import DiaryTemplateOut, DiaryRosterOut, DiaryRosterEntryOut

router = APIRouter(prefix="/api/v1/diary", tags=["diary"])

_TEMPLATE_JSON = Path(__file__).resolve().parents[2] / "diary_template.json"


def _load_json_fallback() -> dict:
    with open(_TEMPLATE_JSON, encoding="utf-8") as f:
        return json.load(f)


@router.get("/template", response_model=DiaryTemplateOut)
def get_diary_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the diary template for the authenticated user's practice.

    Falls back to the static diary_template.json if the practice has no DB record yet,
    so the frontend works before any migration or seed data is in place.
    """
    from app.models.diary import DiaryColumn as _DiaryColumn
    tmpl = (
        db.query(DiaryTemplate)
        .options(
            joinedload(DiaryTemplate.columns).joinedload(_DiaryColumn.breaks),
        )
        .filter(DiaryTemplate.practice_id == current_user.practice_id)
        .first()
    )

    if tmpl is None:
        if not _TEMPLATE_JSON.exists():
            raise HTTPException(status_code=404, detail="No diary template configured for this practice")
        raw = _load_json_fallback()
        sd = raw.get("slot_defaults", {})
        from datetime import time as _time

        def _parse_time(s: str) -> _time:
            h, m = map(int, s.split(":"))
            return _time(h, m)

        cols = []
        for c in raw.get("columns", []):
            cols.append({
                "room_label": c.get("room_label", ""),
                "assignment": c.get("assignment"),
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
            slot_start=_parse_time(sd.get("start", "09:00")),
            slot_end=_parse_time(sd.get("end", "17:00")),
            slot_interval_minutes=sd.get("interval_minutes", 15),
            footer=raw.get("footer", []),
            columns=cols,
        )

    return tmpl


@router.get("/roster", response_model=DiaryRosterOut)
def get_diary_roster(
    roster_date: date = Query(..., alias="date", description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the room roster for the authenticated user's practice on the given date.

    Returns an empty entries list if no rooms are configured or no roster entries
    exist for that date — the frontend falls back to template columns in that case.
    """
    rooms = (
        db.query(Room)
        .filter(Room.practice_id == current_user.practice_id, Room.is_active == True)
        .order_by(Room.display_order)
        .all()
    )
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

    room_map = {r.id: r for r in rooms}
    entries = [
        DiaryRosterEntryOut(
            room_id=room.id,
            room_name=room.name,
            display_order=room.display_order,
            practitioner_id=roster_by_room[room.id].practitioner_id if room.id in roster_by_room else None,
            practitioner_ahpra=roster_by_room[room.id].practitioner_ahpra if room.id in roster_by_room else None,
            label=roster_by_room[room.id].label if room.id in roster_by_room else None,
        )
        for room in rooms
    ]
    return DiaryRosterOut(date=roster_date, entries=entries)
