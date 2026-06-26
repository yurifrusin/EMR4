import uuid
from datetime import date as date_type, datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user, require_role
from app.models.patients import Patient
from app.models.tenancy import User, UserRole, Practitioner, Practice, PracticeLocation
from app.models.appointments import (
    Appointment, AppointmentType, AppointmentStatus,
    PractitionerSchedule, ScheduleOverride,
    AppointmentAuditLog, AppointmentAuditAction,
)
from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate, WaitingArea, Room, DiaryRoster
from app.schemas.appointments import (
    AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate,
    AppointmentOut, AppointmentTypeOut, PractitionerScheduleOut, ScheduleSlot,
    AppointmentCheckinDefaults, AppointmentConflictBrief, AppointmentCreateCommand,
    AppointmentCreateProposalOut, AppointmentProposalIssue,
    AppointmentUpdateProposalIn, AppointmentUpdateCommand, AppointmentUpdateProposalOut,
    AppointmentStatusProposalIn, AppointmentStatusCommand, AppointmentStatusProposalOut,
    AppointmentWaitingAreaProposalIn, AppointmentWaitingAreaCommand, AppointmentWaitingAreaProposalOut,
    AppointmentDeleteIn, AppointmentDeleteCommand, AppointmentDeleteProposalOut,
    AppointmentAuditLogOut,
)

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

MUTATING_APPOINTMENT_ROLES = (
    UserRole.Receptionist,
    UserRole.GP,
    UserRole.Nurse,
    UserRole.Admin,
    UserRole.PracticeOwner,
)

NON_BLOCKING_STATUSES = (
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
)

TERMINAL_STATUSES = (
    AppointmentStatus.Completed,
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
)

DEFAULT_PRACTICE_TIMEZONE = "Australia/Sydney"


def _practice_zoneinfo(db: Session, practice_id: uuid.UUID) -> ZoneInfo:
    timezone_name = (
        db.query(Practice.timezone)
        .filter(Practice.id == practice_id)
        .scalar()
    ) or DEFAULT_PRACTICE_TIMEZONE
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        try:
            return ZoneInfo(DEFAULT_PRACTICE_TIMEZONE)
        except ZoneInfoNotFoundError:
            return timezone.utc


def _as_practice_local(start_time: datetime, practice_tz: ZoneInfo) -> datetime:
    if start_time.tzinfo is None:
        return start_time.replace(tzinfo=practice_tz)
    return start_time.astimezone(practice_tz)


def _utc_from_local(
    appointment_date: date_type,
    start_time_local: time,
    practice_tz: ZoneInfo,
) -> datetime:
    local_time = start_time_local.replace(tzinfo=None)
    local_dt = datetime.combine(appointment_date, local_time).replace(tzinfo=practice_tz)
    return local_dt.astimezone(timezone.utc)


def _canonical_time_values(
    practice_tz: ZoneInfo,
    start_time: Optional[datetime] = None,
    appointment_date: Optional[date_type] = None,
    start_time_local: Optional[time] = None,
) -> tuple[date_type, time, datetime]:
    if appointment_date is not None and start_time_local is not None:
        local_time = start_time_local.replace(tzinfo=None)
        return appointment_date, local_time, _utc_from_local(appointment_date, local_time, practice_tz)

    if start_time is not None:
        local_dt = _as_practice_local(start_time, practice_tz)
        return local_dt.date(), local_dt.time().replace(tzinfo=None), local_dt.astimezone(timezone.utc)

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="start_time or appointment_date + start_time_local is required",
    )


def _local_datetime(appointment_date: date_type, start_time_local: time) -> datetime:
    return datetime.combine(appointment_date, start_time_local.replace(tzinfo=None))


def _get_appointment(appt_id: uuid.UUID, practice_id: uuid.UUID, db: Session) -> Appointment:
    appt = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.practitioner),
            joinedload(Appointment.appointment_type),
        )
        .filter(Appointment.id == appt_id, Appointment.practice_id == practice_id)
        .first()
    )
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def _ensure_patient(patient_id: uuid.UUID, practice_id: uuid.UUID, db: Session) -> None:
    exists = db.query(Patient.id).filter(
        Patient.id == patient_id,
        Patient.practice_id == practice_id,
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Patient not found")


def _ensure_practitioner(practitioner_id: uuid.UUID, practice_id: uuid.UUID, db: Session) -> None:
    exists = db.query(Practitioner.id).filter(
        Practitioner.id == practitioner_id,
        Practitioner.practice_id == practice_id,
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Practitioner not found")


def _ensure_appointment_type(appointment_type_id: Optional[uuid.UUID], practice_id: uuid.UUID, db: Session) -> None:
    if not appointment_type_id:
        return
    exists = db.query(AppointmentType.id).filter(
        AppointmentType.id == appointment_type_id,
        AppointmentType.practice_id == practice_id,
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Appointment type not found")


def _ensure_location(location_id: Optional[uuid.UUID], practice_id: uuid.UUID, db: Session) -> None:
    if not location_id:
        return
    exists = db.query(PracticeLocation.id).filter(
        PracticeLocation.id == location_id,
        PracticeLocation.practice_id == practice_id,
        PracticeLocation.is_active == True,
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Practice location not found")


def _single_active_location(practice_id: uuid.UUID, db: Session) -> bool:
    return (
        db.query(PracticeLocation.id)
        .filter(
            PracticeLocation.practice_id == practice_id,
            PracticeLocation.is_active == True,
        )
        .count()
        <= 1
    )


def _filter_by_location(q, location_id: Optional[uuid.UUID], practice_id: uuid.UUID, db: Session):
    if not location_id:
        return q
    if _single_active_location(practice_id, db):
        return q.filter(or_(Appointment.location_id == location_id, Appointment.location_id.is_(None)))
    return q.filter(Appointment.location_id == location_id)


def _ensure_waiting_area(waiting_area_id: Optional[uuid.UUID], practice_id: uuid.UUID, db: Session) -> None:
    if not waiting_area_id:
        return
    exists = db.query(WaitingArea.id).filter(
        WaitingArea.id == waiting_area_id,
        WaitingArea.practice_id == practice_id,
        WaitingArea.is_active == True,
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Waiting area not found")


def _overlaps(start_a: datetime, duration_a: int, start_b: datetime, duration_b: int) -> bool:
    # Strip timezone info so naive (request) and aware (DB TIMESTAMPTZ) datetimes compare safely.
    if start_a.tzinfo is not None:
        start_a = start_a.replace(tzinfo=None)
    if start_b.tzinfo is not None:
        start_b = start_b.replace(tzinfo=None)
    end_a = start_a + timedelta(minutes=duration_a)
    end_b = start_b + timedelta(minutes=duration_b)
    return start_a < end_b and end_a > start_b


def _find_conflicting_appointment(
    db: Session,
    practice_id: uuid.UUID,
    practitioner_id: uuid.UUID,
    appointment_date: date_type,
    start_time_local: time,
    duration_minutes: int,
    location_id: Optional[uuid.UUID] = None,
    exclude_id: Optional[uuid.UUID] = None,
) -> Optional[Appointment]:
    q = db.query(Appointment).filter(
        Appointment.practice_id == practice_id,
        Appointment.practitioner_id == practitioner_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status.notin_(NON_BLOCKING_STATUSES),
    )
    q = _filter_by_location(q, location_id, practice_id, db)
    if exclude_id:
        q = q.filter(Appointment.id != exclude_id)

    candidate_start = _local_datetime(appointment_date, start_time_local)
    for existing in q.all():
        if _overlaps(
            candidate_start,
            duration_minutes,
            _local_datetime(existing.appointment_date, existing.start_time_local),
            existing.duration_minutes or 0,
        ):
            return existing
    return None


def _conflict_brief(conflict: Appointment) -> AppointmentConflictBrief:
    patient_name = None
    if conflict.patient:
        patient_name = f"{conflict.patient.first_name} {conflict.patient.last_name}".strip()
    elif conflict.patient_name_provisional:
        patient_name = conflict.patient_name_provisional
    return AppointmentConflictBrief(
        appointment_id=conflict.id,
        start_time=conflict.start_time,
        end_time=conflict.end_time,
        start_time_local=conflict.start_time_local,
        duration_minutes=conflict.duration_minutes,
        status=conflict.status,
        patient_name=patient_name,
    )


def _raise_if_conflict(
    db: Session,
    practice_id: uuid.UUID,
    practitioner_id: uuid.UUID,
    appointment_date: date_type,
    start_time_local: time,
    duration_minutes: int,
    location_id: Optional[uuid.UUID] = None,
    exclude_id: Optional[uuid.UUID] = None,
) -> None:
    conflict = _find_conflicting_appointment(
        db,
        practice_id,
        practitioner_id,
        appointment_date,
        start_time_local,
        duration_minutes,
        location_id=location_id,
        exclude_id=exclude_id,
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Appointment conflicts with an existing booking",
                "conflicting_appointment_id": str(conflict.id),
                "conflicting_start_time": conflict.start_time.isoformat(),
                "conflicting_end_time": conflict.end_time.isoformat(),
            },
        )


def _canonical_create_values(
    body: AppointmentCreate,
    practice_tz: ZoneInfo,
) -> tuple[dict, date_type, time, datetime]:
    values = body.model_dump()
    appointment_date, start_time_local, start_time = _canonical_time_values(
        practice_tz,
        start_time=values.get("start_time"),
        appointment_date=values.get("appointment_date"),
        start_time_local=values.get("start_time_local"),
    )
    values["appointment_date"] = appointment_date
    values["start_time_local"] = start_time_local
    values["start_time"] = start_time
    return values, appointment_date, start_time_local, start_time


def _get_break_overlaps(
    db: Session,
    practice_id: uuid.UUID,
    practitioner_id: uuid.UUID,
    appointment_date: date_type,
    start_time_local: time,
    duration_minutes: int,
    location_id: Optional[uuid.UUID] = None,
) -> list[str]:
    """Return labels of DiaryBreak blocks that overlap the appointment (soft-block check)."""
    appt_start = _local_datetime(appointment_date, start_time_local)
    appt_end = appt_start + timedelta(minutes=duration_minutes)
    practitioner_ahpra = (
        db.query(Practitioner.ahpra_number)
        .filter(
            Practitioner.id == practitioner_id,
            Practitioner.practice_id == practice_id,
        )
        .scalar()
    )
    column_filters = [DiaryColumn.practitioner_id == practitioner_id]
    if practitioner_ahpra:
        column_filters.append(DiaryColumn.practitioner_ahpra == practitioner_ahpra)

    template_filters = [DiaryTemplate.practice_id == practice_id]
    if location_id:
        template_filters.append(or_(
            DiaryTemplate.location_id == location_id,
            DiaryTemplate.location_id.is_(None),
        ))

    breaks = (
        db.query(DiaryBreak)
        .join(DiaryColumn, DiaryBreak.column_id == DiaryColumn.id)
        .join(DiaryTemplate, DiaryColumn.template_id == DiaryTemplate.id)
        .filter(*template_filters, or_(*column_filters))
        .all()
    )
    overlapping = []
    for brk in breaks:
        brk_start = datetime.combine(appointment_date, brk.from_time)
        brk_end = datetime.combine(appointment_date, brk.to_time)
        if appt_start < brk_end and appt_end > brk_start:
            overlapping.append(brk.label)
    return overlapping


def _appointment_create_command(
    body: AppointmentCreate,
    values: dict,
) -> AppointmentCreateCommand:
    return AppointmentCreateCommand(
        patient_id=body.patient_id,
        patient_name_provisional=body.patient_name_provisional,
        practitioner_id=body.practitioner_id,
        appointment_type_id=body.appointment_type_id,
        location_id=body.location_id,
        appointment_date=values["appointment_date"],
        start_time_local=values["start_time_local"],
        start_time=values["start_time"],
        duration_minutes=values["duration_minutes"],
        reason=body.reason,
        notes=body.notes,
        booked_via=body.booked_via,
    )


def _write_audit(
    db: Session,
    *,
    practice_id: uuid.UUID,
    appointment_id: uuid.UUID,
    confirmed_by_user_id: uuid.UUID,
    action: AppointmentAuditAction,
    status_before: Optional[AppointmentStatus] = None,
    status_after: Optional[AppointmentStatus] = None,
    cancellation_reason: Optional[str] = None,
) -> None:
    db.add(AppointmentAuditLog(
        practice_id=practice_id,
        appointment_id=appointment_id,
        confirmed_by_user_id=confirmed_by_user_id,
        action=action,
        status_before=status_before,
        status_after=status_after,
        cancellation_reason=cancellation_reason,
    ))


# ── Appointment Types ─────────────────────────────────────────────────────────

@router.get("/types", response_model=list[AppointmentTypeOut])
def list_appointment_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AppointmentType)
        .filter(AppointmentType.practice_id == current_user.practice_id)
        .order_by(AppointmentType.name)
        .all()
    )


# ── Appointments CRUD ─────────────────────────────────────────────────────────

@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    practitioner_id: Optional[uuid.UUID] = Query(None),
    patient_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[AppointmentStatus] = Query(None, alias="status"),
    location_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    practice_id = current_user.practice_id
    if location_id:
        _ensure_location(location_id, practice_id, db)
    practice_tz = _practice_zoneinfo(db, practice_id)
    q = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.practitioner),
            joinedload(Appointment.appointment_type),
        )
        .filter(Appointment.practice_id == practice_id)
    )
    if date_from:
        q = q.filter(
            Appointment.start_time >= _as_practice_local(date_from, practice_tz).astimezone(timezone.utc)
        )
    if date_to:
        q = q.filter(
            Appointment.start_time < _as_practice_local(date_to, practice_tz).astimezone(timezone.utc)
        )
    if practitioner_id:
        q = q.filter(Appointment.practitioner_id == practitioner_id)
    if patient_id:
        q = q.filter(Appointment.patient_id == patient_id)
    if status_filter:
        q = q.filter(Appointment.status == status_filter)
    q = _filter_by_location(q, location_id, practice_id, db)
    return q.order_by(Appointment.appointment_date, Appointment.start_time_local).all()


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    body: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    booked_by = current_user.id
    practice_tz = _practice_zoneinfo(db, practice_id)
    values, appointment_date, start_time_local, _ = _canonical_create_values(body, practice_tz)

    if body.patient_id is not None:
        _ensure_patient(body.patient_id, practice_id, db)
    _ensure_practitioner(body.practitioner_id, practice_id, db)
    _ensure_appointment_type(body.appointment_type_id, practice_id, db)
    _ensure_location(body.location_id, practice_id, db)
    _raise_if_conflict(
        db,
        practice_id,
        body.practitioner_id,
        appointment_date,
        start_time_local,
        values["duration_minutes"],
        location_id=body.location_id,
    )

    appt = Appointment(
        practice_id=practice_id,
        booked_by=booked_by,
        **values,
    )
    db.add(appt)
    db.flush()           # generate PK in Python before commit expires the instance
    appt_id = appt.id   # capture UUID while still in pre-commit state
    _write_audit(
        db,
        practice_id=practice_id,
        appointment_id=appt_id,
        confirmed_by_user_id=current_user.id,
        action=AppointmentAuditAction.create,
        status_after=AppointmentStatus.Booked,
    )
    db.commit()
    out = AppointmentOut.model_validate(_get_appointment(appt_id, practice_id, db))
    out.breaks_overlap = _get_break_overlaps(
        db, practice_id, body.practitioner_id,
        appointment_date, start_time_local, values["duration_minutes"],
        location_id=body.location_id,
    )
    return out


@router.post("/proposals/create", response_model=AppointmentCreateProposalOut)
def propose_create_appointment(
    body: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    practice_tz = _practice_zoneinfo(db, practice_id)
    values, appointment_date, start_time_local, _ = _canonical_create_values(body, practice_tz)

    if body.patient_id is not None:
        _ensure_patient(body.patient_id, practice_id, db)
    _ensure_practitioner(body.practitioner_id, practice_id, db)
    _ensure_appointment_type(body.appointment_type_id, practice_id, db)
    _ensure_location(body.location_id, practice_id, db)

    warnings: list[AppointmentProposalIssue] = []
    blocks: list[AppointmentProposalIssue] = []
    conflict = _find_conflicting_appointment(
        db,
        practice_id,
        body.practitioner_id,
        appointment_date,
        start_time_local,
        values["duration_minutes"],
        location_id=body.location_id,
    )
    conflict_brief = _conflict_brief(conflict) if conflict else None
    if conflict:
        blocks.append(AppointmentProposalIssue(
            code="appointment_conflict",
            severity="blocked",
            message="This appointment overlaps an existing booking.",
        ))

    breaks_overlap = _get_break_overlaps(
        db,
        practice_id,
        body.practitioner_id,
        appointment_date,
        start_time_local,
        values["duration_minutes"],
        location_id=body.location_id,
    )
    for label in breaks_overlap:
        warnings.append(AppointmentProposalIssue(
            code="break_overlap",
            severity="warning",
            message=f"This appointment overlaps {label}.",
        ))

    patient_identity = "linked" if body.patient_id else "provisional"
    if patient_identity == "provisional":
        warnings.append(AppointmentProposalIssue(
            code="provisional_patient",
            severity="warning",
            message="This booking is not linked to a verified patient record yet.",
        ))

    safe = not blocks
    # Creating a diary booking reserves clinical time, so this proposal always
    # needs staff confirmation even when there are no warnings.
    requires_confirmation = True
    if not safe:
        autonomy_tier = "blocked"
    else:
        autonomy_tier = "proposal"

    patient_label = "linked patient" if body.patient_id else body.patient_name_provisional or "provisional patient"
    summary = (
        f"Create {values['duration_minutes']} minute booking for {patient_label} "
        f"on {appointment_date.isoformat()} at {start_time_local.strftime('%H:%M')}."
    )
    if conflict_brief:
        summary += " Blocked by an existing booking."
    elif warnings:
        summary += " Confirmation recommended because warnings are present."
    else:
        summary += " Staff confirmation is required before creating the booking."

    return AppointmentCreateProposalOut(
        safe=safe,
        requires_confirmation=requires_confirmation,
        autonomy_tier=autonomy_tier,
        summary=summary,
        command=_appointment_create_command(body, values),
        warnings=warnings,
        blocks=blocks,
        conflict=conflict_brief,
        breaks_overlap=breaks_overlap,
        patient_identity=patient_identity,
    )


@router.post("/proposals/update/{appointment_id}", response_model=AppointmentUpdateProposalOut)
def propose_update_appointment(
    appointment_id: uuid.UUID,
    body: AppointmentUpdateProposalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Non-mutating proposal for editing/rescheduling an existing appointment.

    Merges supplied fields over the appointment's current values and evaluates
    conflicts, break overlaps, and patient-identity state without writing anything.
    The returned command payload is ready to pass to PUT /{id} after staff confirmation.
    """
    practice_id = current_user.practice_id
    practice_tz = _practice_zoneinfo(db, practice_id)
    appt = _get_appointment(appointment_id, practice_id, db)
    incoming = body.model_dump(exclude_unset=True)

    practitioner_id = incoming.get("practitioner_id", appt.practitioner_id)
    appointment_type_id = incoming.get("appointment_type_id", appt.appointment_type_id)
    location_id = incoming.get("location_id", appt.location_id)
    duration_minutes = incoming.get("duration_minutes", appt.duration_minutes)
    patient_id = incoming.get("patient_id", appt.patient_id)
    patient_name_provisional = incoming.get("patient_name_provisional", appt.patient_name_provisional)
    reason = incoming.get("reason", appt.reason)
    notes = incoming.get("notes", appt.notes)

    if "appointment_date" in incoming or "start_time_local" in incoming:
        new_date = incoming.get("appointment_date", appt.appointment_date)
        new_time_local = incoming.get("start_time_local", appt.start_time_local)
        appointment_date, start_time_local, start_time = _canonical_time_values(
            practice_tz,
            appointment_date=new_date,
            start_time_local=new_time_local,
        )
    else:
        appointment_date = appt.appointment_date
        start_time_local = appt.start_time_local
        start_time = appt.start_time

    warnings: list[AppointmentProposalIssue] = []
    blocks: list[AppointmentProposalIssue] = []

    if "practitioner_id" in incoming and practitioner_id is None:
        blocks.append(AppointmentProposalIssue(
            code="practitioner_required",
            severity="blocked",
            message="Practitioner cannot be removed from an appointment.",
        ))
        practitioner_id = appt.practitioner_id

    if patient_id is None and not patient_name_provisional:
        blocks.append(AppointmentProposalIssue(
            code="patient_identity_required",
            severity="blocked",
            message="Appointment must retain a linked patient or a provisional patient name.",
        ))

    if patient_id is not None:
        _ensure_patient(patient_id, practice_id, db)
    _ensure_practitioner(practitioner_id, practice_id, db)
    _ensure_appointment_type(appointment_type_id, practice_id, db)
    _ensure_location(location_id, practice_id, db)

    if appt.status in TERMINAL_STATUSES:
        blocks.append(AppointmentProposalIssue(
            code="terminal_status",
            severity="blocked",
            message=f"This appointment is already {appt.status.value} and cannot be rescheduled.",
        ))

    conflict = _find_conflicting_appointment(
        db, practice_id, practitioner_id,
        appointment_date, start_time_local, duration_minutes,
        location_id=location_id,
        exclude_id=appointment_id,
    )
    conflict_brief = _conflict_brief(conflict) if conflict else None
    if conflict:
        blocks.append(AppointmentProposalIssue(
            code="appointment_conflict",
            severity="blocked",
            message="The proposed time overlaps an existing booking.",
        ))

    breaks_overlap = _get_break_overlaps(
        db, practice_id, practitioner_id,
        appointment_date, start_time_local, duration_minutes,
        location_id=location_id,
    )
    for label in breaks_overlap:
        warnings.append(AppointmentProposalIssue(
            code="break_overlap",
            severity="warning",
            message=f"This appointment overlaps {label}.",
        ))

    patient_identity = "linked" if patient_id else "provisional"
    if patient_identity == "provisional":
        warnings.append(AppointmentProposalIssue(
            code="provisional_patient",
            severity="warning",
            message="This booking is not linked to a verified patient record yet.",
        ))

    safe = not blocks
    requires_confirmation = True
    autonomy_tier = "blocked" if not safe else "proposal"

    patient_label = "linked patient" if patient_id else (patient_name_provisional or "provisional patient")
    summary = (
        f"Update booking for {patient_label} to "
        f"{appointment_date.isoformat()} at {start_time_local.strftime('%H:%M')}, "
        f"{duration_minutes} min."
    )
    if not safe:
        summary += " Blocked — see issues."
    elif warnings:
        summary += " Confirmation recommended."
    else:
        summary += " Staff confirmation required."

    return AppointmentUpdateProposalOut(
        safe=safe,
        requires_confirmation=requires_confirmation,
        autonomy_tier=autonomy_tier,
        summary=summary,
        command=AppointmentUpdateCommand(
            appointment_id=appointment_id,
            patient_id=patient_id,
            patient_name_provisional=patient_name_provisional,
            practitioner_id=practitioner_id,
            appointment_type_id=appointment_type_id,
            location_id=location_id,
            appointment_date=appointment_date,
            start_time_local=start_time_local,
            start_time=start_time,
            duration_minutes=duration_minutes,
            reason=reason,
            notes=notes,
        ),
        warnings=warnings,
        blocks=blocks,
        conflict=conflict_brief,
        breaks_overlap=breaks_overlap,
        patient_identity=patient_identity,
    )


@router.post("/proposals/status/{appointment_id}", response_model=AppointmentStatusProposalOut)
def propose_status_update(
    appointment_id: uuid.UUID,
    body: AppointmentStatusProposalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Non-mutating proposal for changing an appointment's status (including cancellation).

    Surfaces waiting-area side-effects and unusual transitions without writing anything.
    The returned command payload is ready to pass to PATCH /{id}/status after confirmation.
    autonomy_tier is metadata for Bernie/tool policy — this endpoint never executes.
    """
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)

    if body.waiting_area_id is not None:
        _ensure_waiting_area(body.waiting_area_id, practice_id, db)

    warnings: list[AppointmentProposalIssue] = []
    blocks: list[AppointmentProposalIssue] = []

    if body.status == appt.status:
        blocks.append(AppointmentProposalIssue(
            code="already_in_status",
            severity="blocked",
            message=f"This appointment is already {appt.status.value}.",
        ))

    if appt.status in TERMINAL_STATUSES and body.status != appt.status:
        warnings.append(AppointmentProposalIssue(
            code="already_terminal",
            severity="warning",
            message=f"This appointment is already {appt.status.value}. Re-transitioning is unusual.",
        ))

    clears_waiting_area = (
        body.status in TERMINAL_STATUSES
        and appt.waiting_area_id is not None
        and body.waiting_area_id is None
    )
    if clears_waiting_area:
        warnings.append(AppointmentProposalIssue(
            code="waiting_area_cleared",
            severity="warning",
            message="This status change will remove the patient from the waiting area.",
        ))

    if body.status in TERMINAL_STATUSES and body.waiting_area_id is not None:
        warnings.append(AppointmentProposalIssue(
            code="waiting_area_assigned_on_terminal",
            severity="warning",
            message=(
                "Assigning a waiting area while marking the appointment as "
                f"{body.status.value} is contradictory; the area will be set but "
                "the appointment will be closed."
            ),
        ))

    safe = not blocks
    requires_confirmation = True

    if not safe:
        autonomy_tier = "blocked"
    elif warnings or body.status in TERMINAL_STATUSES:
        # Terminal status changes (Completed, Cancelled, NoShow, DNA) are irreversible
        # clinical decisions — always require proposal/confirmation regardless of warnings.
        autonomy_tier = "proposal"
    else:
        # Routine non-terminal transitions (e.g. Booked→Confirmed, Confirmed→Arrived).
        # execute_with_report is policy metadata for Bernie tooling; this endpoint
        # still does not execute anything.
        autonomy_tier = "execute_with_report"

    if appt.patient:
        patient_label = f"{appt.patient.first_name} {appt.patient.last_name}".strip()
    elif appt.patient_name_provisional:
        patient_label = appt.patient_name_provisional
    else:
        patient_label = "appointment"

    summary = (
        f"Change {patient_label}'s appointment status "
        f"from {appt.status.value} to {body.status.value}."
    )
    if not safe:
        summary += " Blocked — see issues."
    elif warnings:
        summary += " Confirmation recommended."

    return AppointmentStatusProposalOut(
        safe=safe,
        requires_confirmation=requires_confirmation,
        autonomy_tier=autonomy_tier,
        summary=summary,
        command=AppointmentStatusCommand(
            appointment_id=appointment_id,
            status=body.status,
            waiting_area_id=body.waiting_area_id,
            clears_waiting_area=clears_waiting_area,
        ),
        warnings=warnings,
        blocks=blocks,
    )


@router.post("/proposals/waiting-area/{appointment_id}", response_model=AppointmentWaitingAreaProposalOut)
def propose_waiting_area_update(
    appointment_id: uuid.UUID,
    body: AppointmentWaitingAreaProposalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Non-mutating proposal for changing an appointment's waiting area without a status change.

    Covers the reception workflow of moving a patient between areas (or removing them).
    The returned command payload is ready to pass to PUT /{id} after confirmation.
    autonomy_tier is policy metadata for Bernie tooling; this endpoint never executes.
    """
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)

    if body.waiting_area_id is not None:
        _ensure_waiting_area(body.waiting_area_id, practice_id, db)

    warnings: list[AppointmentProposalIssue] = []
    blocks: list[AppointmentProposalIssue] = []

    if body.waiting_area_id == appt.waiting_area_id:
        blocks.append(AppointmentProposalIssue(
            code="already_in_area",
            severity="blocked",
            message=(
                "The appointment is already in this waiting area."
                if body.waiting_area_id is not None
                else "The appointment is not currently in any waiting area."
            ),
        ))

    clears_waiting_area = body.waiting_area_id is None and appt.waiting_area_id is not None
    if clears_waiting_area:
        warnings.append(AppointmentProposalIssue(
            code="waiting_area_cleared",
            severity="warning",
            message="This will remove the patient from the waiting area.",
        ))

    safe = not blocks
    requires_confirmation = True

    if not safe:
        autonomy_tier = "blocked"
    elif warnings:
        autonomy_tier = "proposal"
    else:
        autonomy_tier = "execute_with_report"

    if appt.patient:
        patient_label = f"{appt.patient.first_name} {appt.patient.last_name}".strip()
    elif appt.patient_name_provisional:
        patient_label = appt.patient_name_provisional
    else:
        patient_label = "appointment"

    if body.waiting_area_id is not None:
        summary = f"Move {patient_label} to a different waiting area."
    elif clears_waiting_area:
        summary = f"Remove {patient_label} from the waiting area."
    else:
        summary = f"No waiting-area change for {patient_label}."

    if not safe:
        summary += " Blocked — see issues."
    elif warnings:
        summary += " Confirmation recommended."

    return AppointmentWaitingAreaProposalOut(
        safe=safe,
        requires_confirmation=requires_confirmation,
        autonomy_tier=autonomy_tier,
        summary=summary,
        command=AppointmentWaitingAreaCommand(
            appointment_id=appointment_id,
            waiting_area_id=body.waiting_area_id,
            clears_waiting_area=clears_waiting_area,
        ),
        warnings=warnings,
        blocks=blocks,
    )


@router.get("/waiting-room", response_model=list[AppointmentOut])
def get_waiting_room(
    practitioner_id: Optional[uuid.UUID] = Query(None),
    waiting_area_id: Optional[uuid.UUID] = Query(None),
    location_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Today's booked/arrived/in-consult appointments — the live waiting room queue.

    Optional filters: practitioner_id, waiting_area_id, location_id.
    Omit all for the full queue.
    """
    practice_id = current_user.practice_id
    if location_id:
        _ensure_location(location_id, practice_id, db)
    practice_tz = _practice_zoneinfo(db, practice_id)
    today = datetime.now(practice_tz).date()

    q = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.practitioner),
            joinedload(Appointment.appointment_type),
        )
        .filter(
            Appointment.practice_id == practice_id,
            Appointment.appointment_date == today,
            Appointment.status.in_([
                AppointmentStatus.Booked,
                AppointmentStatus.Confirmed,
                AppointmentStatus.Arrived,
                AppointmentStatus.InConsult,
            ]),
        )
    )
    if practitioner_id:
        q = q.filter(Appointment.practitioner_id == practitioner_id)
    if waiting_area_id:
        q = q.filter(Appointment.waiting_area_id == waiting_area_id)
    q = _filter_by_location(q, location_id, practice_id, db)
    return q.order_by(Appointment.queue_position.nullslast(), Appointment.start_time_local).all()


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_appointment(appointment_id, current_user.practice_id, db)


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: uuid.UUID,
    body: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    practice_tz = _practice_zoneinfo(db, practice_id)
    appt = _get_appointment(appointment_id, practice_id, db)
    status_before_update = appt.status
    values = body.model_dump(exclude_unset=True)

    practitioner_id = values.get("practitioner_id", appt.practitioner_id)
    appointment_type_id = values.get("appointment_type_id", appt.appointment_type_id)
    location_id = values.get("location_id", appt.location_id)
    appointment_date = values.get("appointment_date", appt.appointment_date)
    start_time_local = values.get("start_time_local", appt.start_time_local)
    duration_minutes = values.get("duration_minutes", appt.duration_minutes)

    if {"start_time", "appointment_date", "start_time_local"} & values.keys():
        if "start_time" in values and not ({"appointment_date", "start_time_local"} & values.keys()):
            appointment_date, start_time_local, start_time = _canonical_time_values(
                practice_tz,
                start_time=values["start_time"],
            )
        else:
            appointment_date, start_time_local, start_time = _canonical_time_values(
                practice_tz,
                appointment_date=appointment_date,
                start_time_local=start_time_local,
            )
        values["appointment_date"] = appointment_date
        values["start_time_local"] = start_time_local
        values["start_time"] = start_time

    if "patient_id" in values and values["patient_id"] is not None:
        _ensure_patient(values["patient_id"], practice_id, db)
    next_patient_id = values.get("patient_id", appt.patient_id)
    next_provisional_name = values.get(
        "patient_name_provisional",
        appt.patient_name_provisional,
    )
    if next_patient_id is None and not next_provisional_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="patient_id or patient_name_provisional is required",
        )
    _ensure_practitioner(practitioner_id, practice_id, db)
    _ensure_appointment_type(appointment_type_id, practice_id, db)
    _ensure_location(location_id, practice_id, db)
    _ensure_waiting_area(values.get("waiting_area_id"), practice_id, db)
    if {"practitioner_id", "start_time", "appointment_date", "start_time_local", "duration_minutes"} & values.keys():
        _raise_if_conflict(
            db,
            practice_id,
            practitioner_id,
            appointment_date,
            start_time_local,
            duration_minutes,
            location_id=location_id,
            exclude_id=appointment_id,
        )

    for field, value in values.items():
        setattr(appt, field, value)
    _write_audit(
        db,
        practice_id=practice_id,
        appointment_id=appointment_id,
        confirmed_by_user_id=current_user.id,
        action=AppointmentAuditAction.update,
        status_before=status_before_update,
    )
    db.commit()
    out = AppointmentOut.model_validate(_get_appointment(appointment_id, practice_id, db))
    out.breaks_overlap = _get_break_overlaps(
        db, practice_id, practitioner_id,
        appointment_date, start_time_local, duration_minutes,
        location_id=location_id,
    )
    return out


@router.get("/{appointment_id}/checkin-defaults", response_model=AppointmentCheckinDefaults)
def get_checkin_defaults(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the suggested waiting area for check-in based on the practitioner's
    DiaryRoster entry for the appointment date.  Returns nulls when no safe
    default can be inferred (no roster entry, room has no default, or area
    is inactive)."""
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)

    roster_q = db.query(DiaryRoster).filter(
        DiaryRoster.practice_id == practice_id,
        DiaryRoster.practitioner_id == appt.practitioner_id,
        DiaryRoster.roster_date == appt.appointment_date,
    )
    if appt.location_id is not None:
        # Disambiguate when the same practitioner is rostered at multiple locations
        # on the same date: match only roster entries whose room is at this location.
        roster_q = roster_q.join(Room, DiaryRoster.room_id == Room.id).filter(
            Room.location_id == appt.location_id
        )
    roster = roster_q.first()
    if roster is None:
        return AppointmentCheckinDefaults()

    room = db.query(Room).filter(Room.id == roster.room_id).first()
    if room is None or room.default_waiting_area_id is None:
        return AppointmentCheckinDefaults(room_name=room.name if room else None)

    area = db.query(WaitingArea).filter(
        WaitingArea.id == room.default_waiting_area_id,
        WaitingArea.is_active == True,
    ).first()
    if area is None:
        return AppointmentCheckinDefaults(room_name=room.name)

    return AppointmentCheckinDefaults(
        suggested_waiting_area_id=area.id,
        room_name=room.name,
    )


@router.get("/{appointment_id}/audit", response_model=list[AppointmentAuditLogOut])
def get_appointment_audit(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the confirmed-mutation audit trail for a single appointment.

    Practice-scoped: only entries belonging to the caller's practice are returned.
    The appointment itself must also belong to the caller's practice (404 otherwise).
    """
    practice_id = current_user.practice_id
    _get_appointment(appointment_id, practice_id, db)  # 404 if not in practice
    return (
        db.query(AppointmentAuditLog)
        .filter(
            AppointmentAuditLog.practice_id == practice_id,
            AppointmentAuditLog.appointment_id == appointment_id,
        )
        .order_by(AppointmentAuditLog.created_at)
        .all()
    )


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: uuid.UUID,
    body: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)
    status_before_patch = appt.status
    appt.status = body.status
    if "waiting_area_id" in body.model_fields_set:
        if body.waiting_area_id is not None:
            _ensure_waiting_area(body.waiting_area_id, practice_id, db)
        appt.waiting_area_id = body.waiting_area_id
    elif body.status in TERMINAL_STATUSES:
        appt.waiting_area_id = None
    _write_audit(
        db,
        practice_id=practice_id,
        appointment_id=appointment_id,
        confirmed_by_user_id=current_user.id,
        action=AppointmentAuditAction.status_change,
        status_before=status_before_patch,
        status_after=body.status,
    )
    db.commit()
    return _get_appointment(appointment_id, practice_id, db)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: uuid.UUID,
    body: Optional[AppointmentDeleteIn] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)
    status_before_delete = appt.status
    cancellation_reason = body.cancellation_reason if body else None
    appt.status = AppointmentStatus.Cancelled
    appt.waiting_area_id = None
    appt.cancellation_reason = cancellation_reason
    _write_audit(
        db,
        practice_id=practice_id,
        appointment_id=appointment_id,
        confirmed_by_user_id=current_user.id,
        action=AppointmentAuditAction.delete,
        status_before=status_before_delete,
        status_after=AppointmentStatus.Cancelled,
        cancellation_reason=cancellation_reason,
    )
    db.commit()


@router.post("/proposals/delete/{appointment_id}", response_model=AppointmentDeleteProposalOut)
def propose_delete_appointment(
    appointment_id: uuid.UUID,
    body: Optional[AppointmentDeleteIn] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Non-mutating proposal for deleting (soft-cancelling) an appointment.

    Surfaces waiting-area side-effects before the destructive write.
    Always returns autonomy_tier='proposal' — deletion is irreversible.
    The returned command payload is ready to pass to DELETE /{id} after confirmation.
    """
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)

    warnings: list[AppointmentProposalIssue] = []
    blocks: list[AppointmentProposalIssue] = []

    if appt.status == AppointmentStatus.Cancelled:
        blocks.append(AppointmentProposalIssue(
            code="already_in_status",
            severity="blocked",
            message="This appointment is already Cancelled.",
        ))

    clears_waiting_area = appt.waiting_area_id is not None
    if clears_waiting_area:
        warnings.append(AppointmentProposalIssue(
            code="waiting_area_cleared",
            severity="warning",
            message="Deleting this appointment will remove the patient from the waiting area.",
        ))

    safe = not blocks
    requires_confirmation = True
    autonomy_tier = "blocked" if not safe else "proposal"

    if appt.patient:
        patient_label = f"{appt.patient.first_name} {appt.patient.last_name}".strip()
    elif appt.patient_name_provisional:
        patient_label = appt.patient_name_provisional
    else:
        patient_label = "appointment"

    summary = f"Cancel and remove {patient_label}'s appointment."
    if not safe:
        summary += " Blocked — see issues."
    elif warnings:
        summary += " Confirmation recommended."

    cancellation_reason = body.cancellation_reason if body else None

    return AppointmentDeleteProposalOut(
        safe=safe,
        requires_confirmation=requires_confirmation,
        autonomy_tier=autonomy_tier,
        summary=summary,
        command=AppointmentDeleteCommand(
            appointment_id=appointment_id,
            clears_waiting_area=clears_waiting_area,
            cancellation_reason=cancellation_reason,
        ),
        warnings=warnings,
        blocks=blocks,
    )


# ── Availability / Slot Generation ───────────────────────────────────────────

@router.get("/slots/{practitioner_id}", response_model=list[ScheduleSlot])
def get_available_slots(
    practitioner_id: uuid.UUID,
    date: datetime = Query(..., description="Date to check (ISO datetime, time is ignored)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all time slots for a practitioner on a given date, with availability flag."""
    practitioner = db.query(Practitioner).filter(
        Practitioner.id == practitioner_id,
        Practitioner.practice_id == current_user.practice_id,
    ).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    practice_tz = _practice_zoneinfo(db, current_user.practice_id)
    target_date = _as_practice_local(date, practice_tz).date()
    day_of_week = target_date.weekday()  # 0=Mon

    # Check for override on this date
    override = db.query(ScheduleOverride).filter(
        ScheduleOverride.practitioner_id == practitioner_id,
        ScheduleOverride.date == target_date,
    ).first()

    if override and override.is_unavailable:
        return []

    # Get base schedule for this day
    schedule = db.query(PractitionerSchedule).filter(
        PractitionerSchedule.practitioner_id == practitioner_id,
        PractitionerSchedule.day_of_week == day_of_week,
    ).first()

    if not schedule:
        return []

    start_t = override.override_start if (override and override.override_start) else schedule.start_time
    end_t = override.override_end if (override and override.override_end) else schedule.end_time
    slot_mins = schedule.slot_duration_minutes

    day_start = datetime.combine(target_date, start_t)
    day_end = datetime.combine(target_date, end_t)

    # Existing appointments that day
    booked = db.query(Appointment).filter(
        Appointment.practice_id == current_user.practice_id,
        Appointment.practitioner_id == practitioner_id,
        Appointment.appointment_date == target_date,
        Appointment.status.notin_(NON_BLOCKING_STATUSES),
    ).all()

    slots = []
    current = day_start
    while current + timedelta(minutes=slot_mins) <= day_end:
        available = not any(
            _overlaps(
                current,
                slot_mins,
                _local_datetime(appt.appointment_date, appt.start_time_local),
                appt.duration_minutes or 0,
            )
            for appt in booked
        )
        slots.append(ScheduleSlot(
            start_time=current,
            end_time=current + timedelta(minutes=slot_mins),
            available=available,
        ))
        current += timedelta(minutes=slot_mins)

    return slots
