import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointments import Appointment, AppointmentAuditLog
from app.models.diary_events import DiaryCommittedEvent
from app.models.tenancy import User
from app.schemas.diary_events import AppointmentRescheduledEventPayload


EVENT_TYPE = "diary.appointment_rescheduled"
EVENT_SCHEMA_VERSION = "diary.appointment_rescheduled.v1"
EVENT_SOURCE_SYSTEM = "emr4-diary"
EVENT_EVIDENCE_MODE = "authored_synthetic_local"
EVENT_DELIVERY_TTL = timedelta(hours=24)


def record_appointment_rescheduled_event(
    db: Session,
    *,
    appointment: Appointment,
    audit: AppointmentAuditLog,
    actor: User,
    command_id: uuid.UUID,
    occurred_at: datetime | None = None,
) -> DiaryCommittedEvent:
    """Append the one authorized event inside the caller's update transaction."""

    event_time = occurred_at or datetime.now(timezone.utc)
    aggregate_revision = (
        db.query(func.count(AppointmentAuditLog.id))
        .filter(
            AppointmentAuditLog.practice_id == appointment.practice_id,
            AppointmentAuditLog.appointment_id == appointment.id,
        )
        .scalar()
    )
    payload = AppointmentRescheduledEventPayload(
        appointment_id=appointment.id,
        practitioner_id=appointment.practitioner_id,
        location_id=appointment.location_id,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        reason_codes=["appointment_time_changed"],
    )
    event = DiaryCommittedEvent(
        practice_id=appointment.practice_id,
        event_type=EVENT_TYPE,
        schema_version=EVENT_SCHEMA_VERSION,
        source_system=EVENT_SOURCE_SYSTEM,
        appointment_id=appointment.id,
        aggregate_revision=int(aggregate_revision),
        occurred_at=event_time,
        expires_at=event_time + EVENT_DELIVERY_TTL,
        actor_user_id=actor.id,
        actor_role=actor.role.value if actor.role else "unknown",
        command_id=command_id,
        audit_log_id=audit.id,
        correlation_id=command_id,
        evidence_mode=EVENT_EVIDENCE_MODE,
        payload=payload.model_dump(mode="json"),
    )
    db.add(event)
    db.flush()
    return event
