import base64
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.diary_events import DiaryCommittedEvent
from app.models.tenancy import User
from app.schemas.diary_events import (
    AppointmentRescheduledEventPayload,
    DiaryCommittedEventFeedOut,
    DiaryCommittedEventOut,
)


router = APIRouter(prefix="/api/v1/diary/events", tags=["diary-events"])


_CURSOR_MAX_AGE = timedelta(hours=24)
_CURSOR_CLOCK_SKEW = timedelta(minutes=5)
# The committed-event feed is the reschedule-only delivery surface. The A5.1
# check-in committed event shares the table but is never delivered by this feed.
# Requiring the exact event type during cursor validation and row selection keeps
# an interleaved check-in row out of reschedule payload parsing and cursor
# semantics.
_RESCHEDULE_EVENT_TYPE = "diary.appointment_rescheduled"


def _encode_cursor(
    practice_id: uuid.UUID,
    occurred_at: datetime,
    event_id: uuid.UUID | None,
) -> str:
    timestamp_us = int(occurred_at.timestamp() * 1_000_000)
    coordinate = f"{timestamp_us}:{event_id or ''}".encode("ascii")
    encoded = base64.urlsafe_b64encode(coordinate).decode("ascii").rstrip("=")
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        f"{practice_id}:{encoded}".encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{encoded}.{signature}"


def _decode_cursor(
    cursor: str,
    practice_id: uuid.UUID,
    now: datetime,
) -> tuple[datetime, uuid.UUID | None] | None:
    try:
        encoded, supplied_signature = cursor.split(".", 1)
        expected_signature = hmac.new(
            settings.secret_key.encode("utf-8"),
            f"{practice_id}:{encoded}".encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(supplied_signature, expected_signature):
            return None
        padded = encoded + "=" * (-len(encoded) % 4)
        raw_coordinate = base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")
        timestamp_text, event_id_text = raw_coordinate.split(":", 1)
        occurred_at = datetime.fromtimestamp(
            int(timestamp_text) / 1_000_000,
            tz=timezone.utc,
        )
        if occurred_at < now - _CURSOR_MAX_AGE or occurred_at > now + _CURSOR_CLOCK_SKEW:
            return None
        event_id = uuid.UUID(event_id_text) if event_id_text else None
    except (TypeError, ValueError, UnicodeDecodeError):
        return None
    return occurred_at, event_id


def _event_out(row: DiaryCommittedEvent, received_at: datetime) -> DiaryCommittedEventOut:
    return DiaryCommittedEventOut(
        event_id=row.id,
        event_type=row.event_type,
        schema_version=row.schema_version,
        source_system=row.source_system,
        aggregate_id=row.appointment_id,
        aggregate_revision=row.aggregate_revision,
        occurred_at=row.occurred_at,
        received_at=received_at,
        evidence_mode=row.evidence_mode,
        payload=AppointmentRescheduledEventPayload.model_validate(row.payload),
    )


@router.get("/committed", response_model=DiaryCommittedEventFeedOut)
def read_committed_diary_events(
    cursor: str | None = Query(default=None, max_length=256),
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DiaryCommittedEventFeedOut:
    if not settings.reception_one_committed_event_runtime_enabled:
        return DiaryCommittedEventFeedOut(
            enabled=False,
            baseline_established=False,
        )

    now = datetime.now(timezone.utc)
    if cursor is None:
        return DiaryCommittedEventFeedOut(
            enabled=True,
            baseline_established=True,
            cursor=_encode_cursor(current_user.practice_id, now, None),
        )

    coordinate = _decode_cursor(cursor, current_user.practice_id, now)
    if coordinate is None:
        return DiaryCommittedEventFeedOut(
            enabled=True,
            baseline_established=True,
            cursor=_encode_cursor(current_user.practice_id, now, None),
        )
    cursor_time, cursor_event_id = coordinate
    if cursor_event_id is not None:
        cursor_row = (
            db.query(DiaryCommittedEvent.id)
            .filter(
                DiaryCommittedEvent.practice_id == current_user.practice_id,
                DiaryCommittedEvent.event_type == _RESCHEDULE_EVENT_TYPE,
                DiaryCommittedEvent.id == cursor_event_id,
                DiaryCommittedEvent.occurred_at == cursor_time,
                DiaryCommittedEvent.expires_at > now,
            )
            .one_or_none()
        )
        if cursor_row is None:
            return DiaryCommittedEventFeedOut(
                enabled=True,
                baseline_established=True,
                cursor=_encode_cursor(current_user.practice_id, now, None),
            )

    later_than_cursor = DiaryCommittedEvent.occurred_at > cursor_time
    if cursor_event_id is not None:
        later_than_cursor = or_(
            later_than_cursor,
            and_(
                DiaryCommittedEvent.occurred_at == cursor_time,
                DiaryCommittedEvent.id > cursor_event_id,
            ),
        )

    rows = (
        db.query(DiaryCommittedEvent)
        .filter(
            DiaryCommittedEvent.practice_id == current_user.practice_id,
            DiaryCommittedEvent.event_type == _RESCHEDULE_EVENT_TYPE,
            DiaryCommittedEvent.expires_at > now,
            later_than_cursor,
        )
        .order_by(DiaryCommittedEvent.occurred_at, DiaryCommittedEvent.id)
        .limit(limit)
        .all()
    )
    return DiaryCommittedEventFeedOut(
        enabled=True,
        baseline_established=False,
        cursor=(
            _encode_cursor(
                current_user.practice_id,
                rows[-1].occurred_at,
                rows[-1].id,
            )
            if rows
            else cursor
        ),
        events=[_event_out(row, now) for row in rows],
    )
