"""Minimal, read-only Rayleen waiting-room projection service.

The service reads one authenticated practice/location scope and returns only
the bounded A1 waiting-room fact vocabulary plus deterministic display signals.
It never flushes, commits, emits an event, invokes a provider, or returns a
write-capable object.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import json
from typing import Any
import uuid
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointments import (
    Appointment,
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
)
from app.models.tenancy import Practice, PracticeLocation, User, UserRole


MAX_FACTS = 21
MAX_SIGNALS = 64
FRAME_TTL = timedelta(minutes=2)
ALLOWED_ROLES = frozenset(
    {
        UserRole.Receptionist,
    }
)
EXCLUDED_FIELD_CLASSES = (
    "contact_details",
    "national_identifiers",
    "clinical_text",
    "appointment_notes",
    "unrestricted_history",
    "credentials",
    "raw_provider_data",
)


class WaitingRoomReadDenied(RuntimeError):
    """The role, practice, location, or requested selector is not authorized."""


class ProjectionKind(str, Enum):
    full_queue = "full_queue"
    practitioner_group = "practitioner_group"
    waiting_area_group = "waiting_area_group"
    longest_wait = "longest_wait"


@dataclass(frozen=True)
class FactLabel:
    source_ids: tuple[str, ...]
    integrity_principals: tuple[str, ...]
    confidentiality_readers: tuple[str, ...]
    observed_at: datetime
    expires_at: datetime
    freshness_state: str = "fresh"
    authority_ceiling: str = "data_only"


@dataclass(frozen=True)
class WaitingRoomFact:
    appointment_id: uuid.UUID
    patient_display_token: str
    practitioner_id: uuid.UUID
    status: str
    scheduled_at: datetime
    waiting_area_id: uuid.UUID | None
    arrived_at: datetime | None
    label: FactLabel


@dataclass(frozen=True)
class WaitingRoomSignal:
    kind: str
    appointment_id: uuid.UUID
    value: int | str | bool
    derived_by: str
    label: FactLabel


@dataclass(frozen=True)
class WaitingRoomProjection:
    kind: ProjectionKind
    selected_count: int
    practitioner_id: uuid.UUID | None
    waiting_area_id: uuid.UUID | None
    focus_appointment_id: uuid.UUID | None
    selector_provenance: str
    authority_ceiling: str = "data_only"
    writes_authorized: bool = False


@dataclass(frozen=True)
class WaitingRoomContextFrame:
    schema_version: str
    frame_id: uuid.UUID
    practice_id: uuid.UUID
    location_id: uuid.UUID
    context_revision: int
    generated_at: datetime
    expires_at: datetime
    reader: str
    backend_facts: tuple[WaitingRoomFact, ...]
    derived_signals: tuple[WaitingRoomSignal, ...]
    excluded_field_classes: tuple[str, ...]


@dataclass(frozen=True)
class WaitingRoomReadResult:
    """A4 envelope around the unchanged accepted A1 data frame."""

    frame: WaitingRoomContextFrame
    projection: WaitingRoomProjection


def practice_is_allowlisted(practice_id: uuid.UUID, raw_allowlist: str) -> bool:
    allowed = {
        item.strip().lower()
        for item in (raw_allowlist or "").split(",")
        if item.strip()
    }
    return str(practice_id).lower() in allowed


def read_waiting_room_projection(
    db: Session,
    *,
    current_user: User,
    location_id: uuid.UUID,
    projection_kind: ProjectionKind = ProjectionKind.full_queue,
    practitioner_id: uuid.UUID | None = None,
    waiting_area_id: uuid.UUID | None = None,
    focus_appointment_id: uuid.UUID | None = None,
    observed_at: datetime | None = None,
) -> WaitingRoomReadResult:
    """Read one minimized, fresh, practice-scoped waiting-room projection."""

    if current_user.role not in ALLOWED_ROLES or not current_user.is_active:
        raise WaitingRoomReadDenied("role_not_authorized")

    location = (
        db.query(PracticeLocation.id, Practice.timezone)
        .join(Practice, Practice.id == PracticeLocation.practice_id)
        .filter(
            PracticeLocation.id == location_id,
            PracticeLocation.practice_id == current_user.practice_id,
            PracticeLocation.is_active.is_(True),
        )
        .one_or_none()
    )
    if location is None:
        raise WaitingRoomReadDenied("location_not_authorized")

    effective_now = observed_at or datetime.now(timezone.utc)
    if effective_now.tzinfo is None:
        raise ValueError("observed_at must be timezone-aware")
    effective_now = effective_now.astimezone(timezone.utc)
    expires_at = effective_now + FRAME_TTL
    try:
        practice_today = effective_now.astimezone(ZoneInfo(location.timezone)).date()
    except (TypeError, ZoneInfoNotFoundError):
        raise WaitingRoomReadDenied("practice_timezone_invalid") from None

    rows = (
        db.query(
            Appointment.id,
            Appointment.practitioner_id,
            Appointment.status,
            Appointment.start_time,
            Appointment.waiting_area_id,
        )
        .filter(
            Appointment.practice_id == current_user.practice_id,
            Appointment.location_id == location_id,
            Appointment.appointment_date == practice_today,
            Appointment.status.in_(
                (
                    AppointmentStatus.Booked,
                    AppointmentStatus.Confirmed,
                    AppointmentStatus.Arrived,
                    AppointmentStatus.InConsult,
                )
            ),
        )
        .order_by(
            Appointment.queue_position.nullslast(),
            Appointment.start_time_local,
            Appointment.id,
        )
        .limit(MAX_FACTS)
        .all()
    )

    appointment_ids = tuple(row.id for row in rows)
    arrival_times = _arrival_times(
        db,
        practice_id=current_user.practice_id,
        appointment_ids=appointment_ids,
    )
    facts = tuple(
        _fact_from_row(
            row,
            arrived_at=arrival_times.get(row.id),
            observed_at=effective_now,
            expires_at=expires_at,
        )
        for row in rows
    )
    signals = _derive_signals(
        facts,
        observed_at=effective_now,
        expires_at=expires_at,
    )
    selected_facts, projection = _select_projection(
        facts,
        signals,
        projection_kind=projection_kind,
        practitioner_id=practitioner_id,
        waiting_area_id=waiting_area_id,
        focus_appointment_id=focus_appointment_id,
    )
    selected_ids = {item.appointment_id for item in selected_facts}
    selected_signals = tuple(
        item for item in signals if item.appointment_id in selected_ids
    )
    if len(selected_signals) > MAX_SIGNALS:
        raise WaitingRoomReadDenied("signal_limit_exceeded")
    context_revision = _context_revision(selected_facts, selected_signals)
    frame_id = uuid.uuid5(
        uuid.NAMESPACE_URL,
        (
            "emr4:rayleen:a4:"
            f"{current_user.practice_id}:{location_id}:{context_revision}"
        ),
    )
    return WaitingRoomReadResult(
        frame=WaitingRoomContextFrame(
            schema_version="emr4.waiting_room_context_frame.v1",
            frame_id=frame_id,
            practice_id=current_user.practice_id,
            location_id=location_id,
            context_revision=context_revision,
            generated_at=effective_now,
            expires_at=expires_at,
            reader="authorized_reception_surface",
            backend_facts=selected_facts,
            derived_signals=selected_signals,
            excluded_field_classes=EXCLUDED_FIELD_CLASSES,
        ),
        projection=projection,
    )


def _arrival_times(
    db: Session,
    *,
    practice_id: uuid.UUID,
    appointment_ids: tuple[uuid.UUID, ...],
) -> dict[uuid.UUID, datetime]:
    if not appointment_ids:
        return {}
    rows = (
        db.query(
            AppointmentAuditLog.appointment_id,
            func.max(AppointmentAuditLog.created_at).label("arrived_at"),
        )
        .filter(
            AppointmentAuditLog.practice_id == practice_id,
            AppointmentAuditLog.appointment_id.in_(appointment_ids),
            AppointmentAuditLog.action == AppointmentAuditAction.status_change,
            AppointmentAuditLog.status_after == AppointmentStatus.Arrived,
        )
        .group_by(AppointmentAuditLog.appointment_id)
        .all()
    )
    return {
        row.appointment_id: _as_utc(row.arrived_at)
        for row in rows
        if row.arrived_at is not None
    }


def _fact_from_row(
    row: Any,
    *,
    arrived_at: datetime | None,
    observed_at: datetime,
    expires_at: datetime,
) -> WaitingRoomFact:
    appointment_id = row.id
    label = _label(
        appointment_id,
        observed_at=observed_at,
        expires_at=expires_at,
    )
    return WaitingRoomFact(
        appointment_id=appointment_id,
        patient_display_token=_patient_display_token(appointment_id),
        practitioner_id=row.practitioner_id,
        status=_status_value(row.status),
        scheduled_at=_as_utc(row.start_time),
        waiting_area_id=row.waiting_area_id,
        arrived_at=arrived_at,
        label=label,
    )


def _derive_signals(
    facts: tuple[WaitingRoomFact, ...],
    *,
    observed_at: datetime,
    expires_at: datetime,
) -> tuple[WaitingRoomSignal, ...]:
    signals: list[WaitingRoomSignal] = []
    elapsed: list[tuple[int, uuid.UUID]] = []
    for fact in facts:
        label = _label(
            fact.appointment_id,
            observed_at=observed_at,
            expires_at=expires_at,
        )
        if fact.status in {"arrived", "in_consult"}:
            if fact.arrived_at is None:
                signals.append(
                    WaitingRoomSignal(
                        kind="flow_exception",
                        appointment_id=fact.appointment_id,
                        value="missing_arrival_timestamp",
                        derived_by="deterministic_projection_engine",
                        label=label,
                    )
                )
                continue
            wait_minutes = max(
                0,
                int((observed_at - fact.arrived_at).total_seconds() // 60),
            )
            elapsed.append((wait_minutes, fact.appointment_id))
            signals.extend(
                (
                    WaitingRoomSignal(
                        kind="elapsed_wait_minutes",
                        appointment_id=fact.appointment_id,
                        value=wait_minutes,
                        derived_by="deterministic_projection_engine",
                        label=label,
                    ),
                    WaitingRoomSignal(
                        kind="threshold_band",
                        appointment_id=fact.appointment_id,
                        value=_threshold_band(wait_minutes),
                        derived_by="deterministic_projection_engine",
                        label=label,
                    ),
                )
            )
        elif fact.scheduled_at < observed_at:
            signals.append(
                WaitingRoomSignal(
                    kind="flow_exception",
                    appointment_id=fact.appointment_id,
                    value="expected_arrival_overdue",
                    derived_by="deterministic_projection_engine",
                    label=label,
                )
            )

    for rank, (_, appointment_id) in enumerate(
        sorted(elapsed, key=lambda item: (-item[0], str(item[1]))),
        start=1,
    ):
        signals.append(
            WaitingRoomSignal(
                kind="longest_wait_rank",
                appointment_id=appointment_id,
                value=rank,
                derived_by="deterministic_projection_engine",
                label=_label(
                    appointment_id,
                    observed_at=observed_at,
                    expires_at=expires_at,
                ),
            )
        )
    return tuple(signals)


def _select_projection(
    facts: tuple[WaitingRoomFact, ...],
    signals: tuple[WaitingRoomSignal, ...],
    *,
    projection_kind: ProjectionKind,
    practitioner_id: uuid.UUID | None,
    waiting_area_id: uuid.UUID | None,
    focus_appointment_id: uuid.UUID | None,
) -> tuple[tuple[WaitingRoomFact, ...], WaitingRoomProjection]:
    if not isinstance(projection_kind, ProjectionKind):
        raise WaitingRoomReadDenied("projection_not_authorized")
    selected = facts
    if projection_kind is ProjectionKind.practitioner_group:
        if practitioner_id is None or practitioner_id not in {
            item.practitioner_id for item in facts
        }:
            raise WaitingRoomReadDenied("practitioner_not_authorized")
        selected = tuple(
            item for item in facts if item.practitioner_id == practitioner_id
        )
    elif projection_kind is ProjectionKind.waiting_area_group:
        if waiting_area_id is None or waiting_area_id not in {
            item.waiting_area_id for item in facts
        }:
            raise WaitingRoomReadDenied("waiting_area_not_authorized")
        selected = tuple(
            item for item in facts if item.waiting_area_id == waiting_area_id
        )
    elif projection_kind is ProjectionKind.longest_wait:
        longest_ids = {
            item.appointment_id
            for item in signals
            if item.kind == "longest_wait_rank" and item.value == 1
        }
        selected = tuple(
            item for item in facts if item.appointment_id in longest_ids
        )

    selected_ids = {item.appointment_id for item in selected}
    if focus_appointment_id is not None:
        if focus_appointment_id not in selected_ids:
            raise WaitingRoomReadDenied("focus_not_authorized")
        selected = tuple(
            item
            for item in selected
            if item.appointment_id == focus_appointment_id
        )
    return selected, WaitingRoomProjection(
        kind=projection_kind,
        selected_count=len(selected),
        practitioner_id=(
            practitioner_id
            if projection_kind is ProjectionKind.practitioner_group
            else None
        ),
        waiting_area_id=(
            waiting_area_id
            if projection_kind is ProjectionKind.waiting_area_group
            else None
        ),
        focus_appointment_id=focus_appointment_id,
        selector_provenance="deterministic_product_read",
    )


def _context_revision(
    facts: tuple[WaitingRoomFact, ...],
    signals: tuple[WaitingRoomSignal, ...],
) -> int:
    payload = {
        "facts": [
            {
                "appointment_id": str(item.appointment_id),
                "practitioner_id": str(item.practitioner_id),
                "status": item.status,
                "scheduled_at": item.scheduled_at.isoformat(),
                "waiting_area_id": (
                    str(item.waiting_area_id)
                    if item.waiting_area_id is not None
                    else None
                ),
                "arrived_at": (
                    item.arrived_at.isoformat()
                    if item.arrived_at is not None
                    else None
                ),
            }
            for item in facts
        ],
        "signals": [
            {
                "kind": item.kind,
                "appointment_id": str(item.appointment_id),
                "value": item.value,
            }
            for item in signals
        ],
    }
    digest = hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).digest()
    return max(1, int.from_bytes(digest[:4], "big") & 0x7FFFFFFF)


def _label(
    appointment_id: uuid.UUID,
    *,
    observed_at: datetime,
    expires_at: datetime,
) -> FactLabel:
    return FactLabel(
        source_ids=(f"backend:appointment:{appointment_id}",),
        integrity_principals=("backend_truth",),
        confidentiality_readers=("authorized_reception_surface",),
        observed_at=observed_at,
        expires_at=expires_at,
    )


def _status_value(value: AppointmentStatus | str) -> str:
    if isinstance(value, AppointmentStatus):
        return {
            AppointmentStatus.Booked: "booked",
            AppointmentStatus.Confirmed: "confirmed",
            AppointmentStatus.Arrived: "arrived",
            AppointmentStatus.InConsult: "in_consult",
            AppointmentStatus.Completed: "completed",
            AppointmentStatus.Cancelled: "cancelled",
            AppointmentStatus.NoShow: "no_show",
            AppointmentStatus.DNA: "dna",
        }[value]
    return str(value).casefold()


def _threshold_band(wait_minutes: int) -> str:
    if wait_minutes < 15:
        return "under_15_minutes"
    if wait_minutes < 30:
        return "15_to_29_minutes"
    return "30_minutes_or_more"


def _patient_display_token(appointment_id: uuid.UUID) -> str:
    digest = hashlib.sha256(
        f"emr4:rayleen:a4:patient-token:{appointment_id}".encode("utf-8")
    ).hexdigest()
    return f"synthetic:patient-{digest[:12]}"


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


__all__ = [
    "ALLOWED_ROLES",
    "EXCLUDED_FIELD_CLASSES",
    "FactLabel",
    "ProjectionKind",
    "WaitingRoomContextFrame",
    "WaitingRoomFact",
    "WaitingRoomProjection",
    "WaitingRoomReadDenied",
    "WaitingRoomSignal",
    "practice_is_allowlisted",
    "read_waiting_room_projection",
]
