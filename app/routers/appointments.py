import uuid
from datetime import date as date_type, datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user, require_role
from app.models.patients import Patient
from app.models.tenancy import User, UserRole, Practitioner, Practice, PracticeLocation
from app.models.appointments import (
    Appointment, AppointmentType, AppointmentStatus,
    PractitionerSchedule, ScheduleOverride,
)
from app.schemas.appointments import (
    AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate,
    AppointmentOut, AppointmentTypeOut, PractitionerScheduleOut, ScheduleSlot,
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
        return ZoneInfo(DEFAULT_PRACTICE_TIMEZONE)


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
    exclude_id: Optional[uuid.UUID] = None,
) -> Optional[Appointment]:
    q = db.query(Appointment).filter(
        Appointment.practice_id == practice_id,
        Appointment.practitioner_id == practitioner_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status.notin_(NON_BLOCKING_STATUSES),
    )
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


def _raise_if_conflict(
    db: Session,
    practice_id: uuid.UUID,
    practitioner_id: uuid.UUID,
    appointment_date: date_type,
    start_time_local: time,
    duration_minutes: int,
    exclude_id: Optional[uuid.UUID] = None,
) -> None:
    conflict = _find_conflicting_appointment(
        db, practice_id, practitioner_id, appointment_date, start_time_local, duration_minutes, exclude_id
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    practice_tz = _practice_zoneinfo(db, current_user.practice_id)
    q = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.practitioner),
            joinedload(Appointment.appointment_type),
        )
        .filter(Appointment.practice_id == current_user.practice_id)
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
    )

    appt = Appointment(
        practice_id=practice_id,
        booked_by=booked_by,
        **values,
    )
    db.add(appt)
    db.commit()
    return _get_appointment(appt.id, practice_id, db)


@router.get("/waiting-room", response_model=list[AppointmentOut])
def get_waiting_room(
    practitioner_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Today's booked/arrived/in-consult appointments — the live waiting room queue."""
    practice_tz = _practice_zoneinfo(db, current_user.practice_id)
    today = datetime.now(practice_tz).date()

    q = (
        db.query(Appointment)
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.practitioner),
            joinedload(Appointment.appointment_type),
        )
        .filter(
            Appointment.practice_id == current_user.practice_id,
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

    _ensure_practitioner(practitioner_id, practice_id, db)
    _ensure_appointment_type(appointment_type_id, practice_id, db)
    _ensure_location(location_id, practice_id, db)
    if {"practitioner_id", "start_time", "appointment_date", "start_time_local", "duration_minutes"} & values.keys():
        _raise_if_conflict(
            db,
            practice_id,
            practitioner_id,
            appointment_date,
            start_time_local,
            duration_minutes,
            exclude_id=appointment_id,
        )

    for field, value in values.items():
        setattr(appt, field, value)
    db.commit()
    return _get_appointment(appointment_id, practice_id, db)


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: uuid.UUID,
    body: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)
    appt.status = body.status
    db.commit()
    return _get_appointment(appointment_id, practice_id, db)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    practice_id = current_user.practice_id
    appt = _get_appointment(appointment_id, practice_id, db)
    appt.status = AppointmentStatus.Cancelled
    db.commit()


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
