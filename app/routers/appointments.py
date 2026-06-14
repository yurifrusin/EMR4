import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user
from app.models.tenancy import User, Practitioner
from app.models.appointments import (
    Appointment, AppointmentType, AppointmentStatus,
    PractitionerSchedule, ScheduleOverride,
)
from app.schemas.appointments import (
    AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate,
    AppointmentOut, AppointmentTypeOut, PractitionerScheduleOut, ScheduleSlot,
)

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])


def _get_appointment(appt_id: uuid.UUID, practice_id: uuid.UUID, db: Session) -> Appointment:
    appt = (
        db.query(Appointment)
        .options(joinedload(Appointment.patient), joinedload(Appointment.practitioner))
        .filter(Appointment.id == appt_id, Appointment.practice_id == practice_id)
        .first()
    )
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


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
    q = (
        db.query(Appointment)
        .options(joinedload(Appointment.patient), joinedload(Appointment.practitioner))
        .filter(Appointment.practice_id == current_user.practice_id)
    )
    if date_from:
        q = q.filter(Appointment.start_time >= date_from)
    if date_to:
        q = q.filter(Appointment.start_time < date_to)
    if practitioner_id:
        q = q.filter(Appointment.practitioner_id == practitioner_id)
    if patient_id:
        q = q.filter(Appointment.patient_id == patient_id)
    if status_filter:
        q = q.filter(Appointment.status == status_filter)
    return q.order_by(Appointment.start_time).all()


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(
    body: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    practitioner = db.query(Practitioner).filter(
        Practitioner.id == body.practitioner_id,
        Practitioner.practice_id == current_user.practice_id,
    ).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    appt = Appointment(
        practice_id=current_user.practice_id,
        booked_by=current_user.id,
        **body.model_dump(),
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return _get_appointment(appt.id, current_user.practice_id, db)


@router.get("/waiting-room", response_model=list[AppointmentOut])
def get_waiting_room(
    practitioner_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Today's booked/arrived/in-consult appointments — the live waiting room queue."""
    now = datetime.utcnow()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    q = (
        db.query(Appointment)
        .options(joinedload(Appointment.patient), joinedload(Appointment.practitioner))
        .filter(
            Appointment.practice_id == current_user.practice_id,
            Appointment.start_time >= day_start,
            Appointment.start_time < day_end,
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
    return q.order_by(Appointment.queue_position.nullslast(), Appointment.start_time).all()


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
    current_user: User = Depends(get_current_user),
):
    appt = _get_appointment(appointment_id, current_user.practice_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(appt, field, value)
    db.commit()
    return _get_appointment(appointment_id, current_user.practice_id, db)


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_appointment_status(
    appointment_id: uuid.UUID,
    body: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appt = _get_appointment(appointment_id, current_user.practice_id, db)
    appt.status = body.status
    db.commit()
    return _get_appointment(appointment_id, current_user.practice_id, db)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appt = _get_appointment(appointment_id, current_user.practice_id, db)
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

    target_date = date.date()
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
        Appointment.practitioner_id == practitioner_id,
        Appointment.start_time >= day_start,
        Appointment.start_time < day_end,
        Appointment.status != AppointmentStatus.Cancelled,
    ).all()

    booked_times = {a.start_time for a in booked}

    slots = []
    current = day_start
    while current + timedelta(minutes=slot_mins) <= day_end:
        slots.append(ScheduleSlot(
            start_time=current,
            end_time=current + timedelta(minutes=slot_mins),
            available=current not in booked_times,
        ))
        current += timedelta(minutes=slot_mins)

    return slots
