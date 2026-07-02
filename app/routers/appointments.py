import uuid
import re
from datetime import date as date_type, datetime, time, timedelta, timezone
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.config import settings
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
    AppointmentCreateProposalOut, AppointmentConfirmCreateProposalOut, AppointmentProposalIssue,
    AppointmentUpdateProposalIn, AppointmentUpdateCommand, AppointmentUpdateProposalOut,
    AppointmentStatusProposalIn, AppointmentStatusCommand, AppointmentStatusProposalOut,
    AppointmentWaitingAreaProposalIn, AppointmentWaitingAreaCommand, AppointmentWaitingAreaProposalOut,
    AppointmentDeleteIn, AppointmentDeleteCommand, AppointmentDeleteProposalOut,
    AppointmentAuditLogOut,
    SlotSearchProposalIn, SlotCandidate, SlotSearchProposalOut,
    SlotSearchCommandIn, SlotSearchCommandResult, SlotSearchCommandExecutionOut,
    SlotSelectionProposalIn, SlotSelectionProposalOut,
    BernieIdentityEvidence, BerniePractitionerEvidence, BerniePatientEvidence,
    BernieStaffReviewPayload, BernieStaffReviewSlotSummary,
    BernieSupervisedBookingIn, BernieSupervisedBookingOut,
    BernieCreateProposalConfirmationIn, BerniePilotEligibilityOut,
    BernieBookingInstructionInterpretIn, BernieBookingInstructionInterpretOut,
    BernieConfidenceAxis, BernieConfidenceBand, BernieDecisionPolicy,
    BernieAssumption, BernieStaffCheck, BerniePatientCandidate,
    BerniePatientBookingContext, BernieContextFreshness, BernieSlotSuggestion,
    BernieTurnRef, BernieTurnEventKind,
    BernieNoSlotSuggestionSelectionIn, BernieNoSlotSuggestionSelectionOut,
)
from app.services.bernie_turn_evidence import (
    compute_candidate_freshness_id,
    compute_proposal_freshness_id,
    check_staleness,
    mint_session_id,
    mint_turn_id,
    StalenessVerdict,
)
from app.services.bernie_patient_context import (
    build_patient_booking_context,
    build_existing_future_follow_up_warning,
    has_existing_booking_on_requested_day,
)
from app.services.bernie_booking_interpreter import (
    actor_context_for_interpreter_user,
    get_booking_instruction_interpreter,
)
from app.services.ai.audit_store import persist_access_ai_audit_events
from app.services.bernie_pilot_gate import evaluate_bernie_pilot_eligibility
from app.services.bernie_slot_normalizer import normalize_slot_search_command
from app.services.bernie_transition_table import resolve_booking_date_transition

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

MUTATING_APPOINTMENT_ROLES = (
    UserRole.Receptionist,
    UserRole.GP,
    UserRole.Nurse,
    UserRole.Admin,
    UserRole.PracticeOwner,
)

KNOWN_APPOINTMENT_WARNING_CODES = {
    "already_terminal",
    "break_overlap",
    "provisional_patient",
    "waiting_area_assigned_on_terminal",
    "waiting_area_cleared",
}

BERNIE_IDENTITY_CONFIDENCE_AUDIT_CODES: dict[str, str] = {
    "unlinked": "bernie_identity_confidence_unlinked",
    "low": "bernie_identity_confidence_low",
    "medium": "bernie_identity_confidence_medium",
    "high": "bernie_identity_confidence_high",
    "ambiguous": "bernie_identity_confidence_ambiguous",
}

_BERNIE_CONFIRM_CREATE_BASE_EVIDENCE = [
    "bernie_confirm_create_proposal",
    "source_slot_selection_proposal",
    "source_create_proposal",
]

BERNIE_CONFIRM_CREATE_AUDIT_EVIDENCE = [
    *_BERNIE_CONFIRM_CREATE_BASE_EVIDENCE,
    *BERNIE_IDENTITY_CONFIDENCE_AUDIT_CODES.values(),
]

BERNIE_AUTONOMOUS_BOOKING_TERMS = (
    "book it",
    "create it",
    "confirm it",
    "make the booking",
    "write it",
)
BERNIE_WEEK_RELATIVE_RE = re.compile(
    r"\b(?:in\s+(?:a|one|1)\s+week(?:['’`\\]s)?(?:\s+time)?|next\s+week)\b",
    re.IGNORECASE,
)


def _mint_next_turn_ref(
    incoming: Optional[BernieTurnRef],
    event_kind: BernieTurnEventKind,
    reference_date: date_type,
) -> BernieTurnRef:
    """Mint the next turn_ref for a Bernie response.

    If the client supplied an incoming turn_ref we continue its session;
    otherwise we start a new session.  reference_date is always taken from the
    server-side intake value, not the client-supplied turn_ref, so it is
    immutable across turns.
    """
    if incoming is not None:
        session_id = incoming.session_id
        next_index = incoming.turn_index + 1
    else:
        session_id = mint_session_id()
        next_index = 0
    return BernieTurnRef(
        session_id=session_id,
        turn_id=mint_turn_id(session_id, next_index),
        turn_index=next_index,
        event_kind=event_kind,
        reference_date=reference_date,
    )


def _resolve_bernie_instruction_relative_date(
    instruction: str,
    reference_date: Optional[date_type],
) -> Optional[str]:
    if reference_date is None:
        return None
    if BERNIE_WEEK_RELATIVE_RE.search(instruction):
        return (reference_date + timedelta(days=7)).isoformat()
    return None

# ── Bernie confidence-policy helpers ─────────────────────────────────────────

# Lattice order: assume=0 (most permissive) < proceed_with_check=1 < ask=2 < block=3
_BAND_ORDER: dict[str, int] = {
    "assume": 0,
    "proceed_with_check": 1,
    "ask": 2,
    "block": 3,
}


def _lattice_min(bands: list[BernieConfidenceBand]) -> BernieConfidenceBand:
    """Return the most restrictive band (highest order) across a list of bands."""
    if not bands:
        return "assume"
    return max(bands, key=lambda b: _BAND_ORDER[b])  # type: ignore[arg-type]


def _levenshtein(a: str, b: str) -> int:
    """Simple Wagner-Fischer edit distance for short name tokens."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for ca in a:
        curr = [prev[0] + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


def _tokens_near_match(name_tokens: list[str], instruction_tokens: set[str]) -> bool:
    """True when at least one name token has Levenshtein ≤ 2 to any instruction token."""
    for nt in name_tokens:
        if len(nt) < 3:
            continue
        for it in instruction_tokens:
            if len(it) < 3:
                continue
            if _levenshtein(nt, it) <= 2:
                return True
    return False


def _second_identifier_present(instruction: str) -> bool:
    """Return True when the instruction appears to carry a patient DOB, Medicare number, or phone.

    Uses past-year-only DOB patterns to avoid matching booking dates (which are present
    or future). A 'second identifier' must be clearly patient-specific, not a slot date.
    """
    # DOB in DMY format: day/month/year or day-month-year
    dob_dmy = re.compile(r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b")
    # ISO DOB: only years clearly in the past (1900–2015) to avoid matching booking dates
    dob_iso = re.compile(r"\b(?:19\d{2}|200\d|201[0-5])-\d{2}-\d{2}\b")
    # Medicare: 10-digit number optionally followed by a reference digit
    medicare_pat = re.compile(r"\b\d{10}(?:[/\s]\d)?\b")
    # Australian phone: mobile (04xx) or landline (0[2-9]xxxxxxxx) or +61
    phone_pat = re.compile(r"\b0[24-9]\d{8}\b|\b\+61\d{9}\b")
    return bool(
        dob_dmy.search(instruction)
        or dob_iso.search(instruction)
        or medicare_pat.search(instruction)
        or phone_pat.search(instruction)
    )


def _mask_dob(dob: object) -> Optional[str]:
    """Return a masked DOB string like '1955-**-**' for candidate display."""
    if dob is None:
        return None
    try:
        return str(dob)[:4] + "-**-**"
    except Exception:
        return None


def _clinic_local_now(practice_tz: ZoneInfo) -> datetime:
    """Return the current datetime in clinic-local timezone. Monkeypatchable in tests."""
    return datetime.now(tz=practice_tz)


def _sanitize_confirmed_warnings(codes: Optional[list[str]]) -> Optional[list[str]]:
    if not codes:
        return None
    confirmed_warnings: list[str] = []
    for code in codes:
        if not isinstance(code, str):
            continue
        normalized = code.strip()
        if normalized in KNOWN_APPOINTMENT_WARNING_CODES and normalized not in confirmed_warnings:
            confirmed_warnings.append(normalized)
    return confirmed_warnings or None


def _sanitize_audit_evidence(codes: Optional[list[str]]) -> list[str]:
    if not codes:
        return []
    evidence: list[str] = []
    for code in codes:
        if code in BERNIE_CONFIRM_CREATE_AUDIT_EVIDENCE and code not in evidence:
            evidence.append(code)
    return evidence

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


def _check_create_command_entities(
    command: "AppointmentCreateCommand",
    practice_id: uuid.UUID,
    db: Session,
) -> list["AppointmentProposalIssue"]:
    """Non-raising entity check for the Bernie confirm path.

    Returns structured AppointmentProposalIssue blocks for any missing or
    out-of-scope patient/practitioner/appointment_type/location. Never raises.
    The raising _ensure_* helpers remain for the direct create/edit routes.
    """
    blocks: list[AppointmentProposalIssue] = []
    if command.patient_id is not None:
        exists = db.query(Patient.id).filter(
            Patient.id == command.patient_id,
            Patient.practice_id == practice_id,
        ).first()
        if not exists:
            blocks.append(AppointmentProposalIssue(
                code="patient_not_found",
                severity="blocked",
                message="The patient linked to this proposal was not found or is not accessible.",
            ))
    if not db.query(Practitioner.id).filter(
        Practitioner.id == command.practitioner_id,
        Practitioner.practice_id == practice_id,
    ).first():
        blocks.append(AppointmentProposalIssue(
            code="practitioner_not_found",
            severity="blocked",
            message="The practitioner linked to this proposal was not found or is not accessible.",
        ))
    if command.appointment_type_id is not None:
        if not db.query(AppointmentType.id).filter(
            AppointmentType.id == command.appointment_type_id,
            AppointmentType.practice_id == practice_id,
        ).first():
            blocks.append(AppointmentProposalIssue(
                code="appointment_type_not_found",
                severity="blocked",
                message="The appointment type linked to this proposal was not found or is not accessible.",
            ))
    if command.location_id is not None:
        if not db.query(PracticeLocation.id).filter(
            PracticeLocation.id == command.location_id,
            PracticeLocation.practice_id == practice_id,
            PracticeLocation.is_active == True,
        ).first():
            blocks.append(AppointmentProposalIssue(
                code="location_not_found",
                severity="blocked",
                message="The location linked to this proposal was not found or is no longer active.",
            ))
    return blocks


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
    values = body.model_dump(exclude={"confirmed_warnings"})
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
    confirmed_warnings: Optional[list[str]] = None,
    audit_evidence: Optional[list[str]] = None,
) -> None:
    bounded_codes = [
        *_sanitize_audit_evidence(audit_evidence),
        *(_sanitize_confirmed_warnings(confirmed_warnings) or []),
    ]
    db.add(AppointmentAuditLog(
        practice_id=practice_id,
        appointment_id=appointment_id,
        confirmed_by_user_id=confirmed_by_user_id,
        action=action,
        status_before=status_before,
        status_after=status_after,
        cancellation_reason=cancellation_reason,
        confirmed_warnings=bounded_codes or None,
    ))


def _audit_actor_display(user: Optional[User]) -> tuple[str, Optional[str]]:
    if user is None:
        return "Unknown", None

    role = user.role.value if user.role else None
    practitioner = user.practitioner
    if practitioner:
        display = " ".join(
            part for part in (practitioner.first_name, practitioner.last_name) if part
        ).strip()
        if display:
            return display, role

    if user.email:
        display = user.email.split("@", 1)[0].strip()
        if display:
            return display, role

    return "Unknown", role


def _create_appointment_from_body(
    body: AppointmentCreate,
    db: Session,
    current_user: User,
    confirmed_warnings: Optional[list[str]] = None,
    audit_evidence: Optional[list[str]] = None,
) -> AppointmentOut:
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
    db.flush()
    appt_id = appt.id
    _write_audit(
        db,
        practice_id=practice_id,
        appointment_id=appt_id,
        confirmed_by_user_id=current_user.id,
        action=AppointmentAuditAction.create,
        status_after=AppointmentStatus.Booked,
        confirmed_warnings=confirmed_warnings,
        audit_evidence=audit_evidence,
    )
    db.commit()
    out = AppointmentOut.model_validate(_get_appointment(appt_id, practice_id, db))
    out.breaks_overlap = _get_break_overlaps(
        db, practice_id, body.practitioner_id,
        appointment_date, start_time_local, values["duration_minutes"],
        location_id=body.location_id,
    )
    return out


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
    return _create_appointment_from_body(
        body,
        db,
        current_user,
        confirmed_warnings=body.confirmed_warnings,
    )


@router.post("/proposals/create", response_model=AppointmentCreateProposalOut)
def propose_create_appointment(
    body: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    return _build_create_appointment_proposal(body, db, current_user.practice_id)


def _build_create_appointment_proposal(
    body: AppointmentCreate,
    db: Session,
    practice_id: uuid.UUID,
) -> AppointmentCreateProposalOut:
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


@router.get("/bernie/pilot-eligibility", response_model=BerniePilotEligibilityOut)
def get_bernie_pilot_eligibility(
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    return evaluate_bernie_pilot_eligibility(
        enabled=settings.bernie_staff_pilot_enabled,
        practice_allowlist=settings.bernie_staff_pilot_practice_ids,
        user_allowlist=settings.bernie_staff_pilot_user_ids,
        current_user=current_user,
    )


@router.post(
    "/proposals/bernie/interpret-booking-instruction",
    response_model=BernieBookingInstructionInterpretOut,
)
def interpret_bernie_booking_instruction(
    body: BernieBookingInstructionInterpretIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Interpret staff booking text into structured intent without side effects.

    The interpreter provider is disabled by default. This endpoint never creates
    proposals, searches slots, confirms bookings, or writes appointment audit
    rows. Live provider mode writes bounded Access AI audit metadata only.
    """
    provider = get_booking_instruction_interpreter(
        settings.bernie_booking_interpreter_provider,
    )
    access_ai_audit_events = []
    result = provider.interpret(
        body,
        actor_context_for_interpreter_user(current_user),
        access_ai_audit_events,
    )
    result = _resolve_bernie_interpretation_context(
        result,
        body,
        db,
        current_user.practice_id,
    )
    if access_ai_audit_events:
        persist_access_ai_audit_events(db, access_ai_audit_events)
        db.commit()
    # Stamp turn_ref on the response (additive; does not affect existing fields).
    effective_reference_date = result.request_reference_date or (
        body.reference_date if body.reference_date is not None else date_type.today()
    )
    turn_ref = _mint_next_turn_ref(body.turn_ref, "staff_instruction", effective_reference_date)
    result = result.model_copy(update={"turn_ref": turn_ref})
    return result


def _text_tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (value or "").lower())


def _text_contains_name(instruction_tokens: set[str], *name_parts: str) -> bool:
    parts = [
        token
        for part in name_parts
        for token in _text_tokens(part)
        if token not in {"dr", "doctor", "nurse", "mr", "mrs", "ms", "miss"}
    ]
    return bool(parts) and all(part in instruction_tokens for part in parts)


def _context_frame_value(
    body: BernieBookingInstructionInterpretIn,
    key: str,
) -> Optional[str]:
    for frame in body.context_frames:
        if not isinstance(frame, dict):
            continue
        value = frame.get(key)
        if value:
            return str(value)
    return None


def _booking_context_practitioner_for_patient(
    body: BernieBookingInstructionInterpretIn,
    instruction_tokens: set[str],
    db: Session,
    practice_id: uuid.UUID,
) -> tuple[Optional[uuid.UUID], Optional[str], Optional[str]]:
    """Infer practitioner from same-day diary context for a named patient."""
    matches: list[tuple[uuid.UUID, str, str]] = []
    for frame in body.context_frames:
        if not isinstance(frame, dict) or frame.get("type") != "diary_day_booking":
            continue
        practitioner_id = frame.get("booking_practitioner_id")
        if not _valid_uuid_text(practitioner_id):
            continue
        patient_label = str(frame.get("patient_label") or "").strip()
        label_tokens = [
            token
            for token in _text_tokens(patient_label)
            if token not in {"dr", "doctor", "nurse", "mr", "mrs", "ms", "miss"}
        ]
        if not label_tokens or not all(token in instruction_tokens for token in label_tokens):
            continue
        try:
            parsed_practitioner_id = uuid.UUID(str(practitioner_id))
        except (TypeError, ValueError):
            continue
        matches.append((
            parsed_practitioner_id,
            str(frame.get("practitioner_label") or "").strip(),
            str(frame.get("start_time_local") or frame.get("appointment_time") or "").strip(),
        ))

    unique_ids = {item[0] for item in matches}
    if len(unique_ids) != 1:
        return None, None, None

    practitioner_id = next(iter(unique_ids))
    label = next((item[1] for item in matches if item[1]), "")
    if not label:
        practitioner = db.query(Practitioner).filter(
            Practitioner.practice_id == practice_id,
            Practitioner.id == practitioner_id,
        ).first()
        if practitioner:
            label = f"{practitioner.first_name} {practitioner.last_name}".strip()
    time_hint = next((item[2] for item in matches if item[2]), None)
    return practitioner_id, label or None, time_hint


def _valid_uuid_text(value: object) -> bool:
    if value in (None, ""):
        return False
    try:
        uuid.UUID(str(value))
    except (TypeError, ValueError):
        return False
    return True


def _resolve_practitioner_from_instruction(
    instruction_tokens: set[str],
    instruction: str,
    db: Session,
    practice_id: uuid.UUID,
) -> tuple[Optional[uuid.UUID], list[AppointmentProposalIssue], BernieConfidenceAxis, list[BernieAssumption]]:
    """Resolve a practitioner from free-text.

    Practitioner set is small and closed → typo-tolerant matching (Levenshtein ≤ 2
    on surname) produces a proceed_with_check assumption rather than a hard block.
    """
    exact_matches: list[Practitioner] = []
    near_matches: list[Practitioner] = []
    practitioners = db.query(Practitioner).filter(
        Practitioner.practice_id == practice_id,
        Practitioner.is_active == True,
    ).all()
    for pr in practitioners:
        full_name_exact = _text_contains_name(instruction_tokens, pr.first_name, pr.last_name)
        surname_exact = _text_contains_name(instruction_tokens, pr.last_name)
        if full_name_exact or surname_exact:
            exact_matches.append(pr)
            continue
        # Typo-tolerant: check surname token Levenshtein ≤ 2
        surname_tokens = [t for t in _text_tokens(pr.last_name) if t not in {"dr", "doctor", "nurse"}]
        if _tokens_near_match(surname_tokens, instruction_tokens):
            near_matches.append(pr)

    if len(exact_matches) == 1:
        pr = exact_matches[0]
        axis = BernieConfidenceAxis(
            axis="practitioner",
            band="assume",
            basis=f"Unique exact name match: {pr.first_name} {pr.last_name}.",
        )
        return pr.id, [
            AppointmentProposalIssue(
                code="practitioner_name_resolved",
                severity="warning",
                message=(
                    "Bernie resolved the practitioner name in the instruction "
                    f"to {pr.first_name} {pr.last_name}."
                ),
            )
        ], axis, []

    if len(exact_matches) > 1:
        axis = BernieConfidenceAxis(
            axis="practitioner",
            band="ask",
            basis="Multiple practitioners match the name — needs clarification.",
        )
        return None, [
            AppointmentProposalIssue(
                code="ambiguous_practitioner_name",
                severity="warning",
                message="Multiple active practitioners match the name in the instruction.",
            )
        ], axis, []

    # No exact match — try unique near-match (typo-tolerant, proceed_with_check)
    if len(near_matches) == 1:
        pr = near_matches[0]
        display = f"{pr.first_name} {pr.last_name}"
        axis = BernieConfidenceAxis(
            axis="practitioner",
            band="proceed_with_check",
            basis=f"Near-match: instruction appears to mean {display} (possible typo).",
            staff_detail=f"I think you mean {display} — please confirm.",
        )
        assumption = BernieAssumption(
            field="practitioner",
            assumed_value=display,
            basis="Name in instruction is a close match (possible typo).",
            reversible_copy=f"Tell me if {display} is not the right practitioner.",
        )
        return pr.id, [
            AppointmentProposalIssue(
                code="practitioner_name_near_match",
                severity="warning",
                message=(
                    f"I think you mean {display} — please confirm before searching."
                ),
            )
        ], axis, [assumption]

    if len(near_matches) > 1:
        axis = BernieConfidenceAxis(
            axis="practitioner",
            band="ask",
            basis="Multiple practitioners are close matches — needs clarification.",
        )
        return None, [
            AppointmentProposalIssue(
                code="ambiguous_practitioner_name",
                severity="warning",
                message="Multiple active practitioners match the name in the instruction.",
            )
        ], axis, []

    # No match at all — practitioner axis unresolved (normalizer will produce block if required)
    axis = BernieConfidenceAxis(
        axis="practitioner",
        band="ask",
        basis="No practitioner matched the name in the instruction.",
    )
    return None, [], axis, []


def _resolve_patient_from_instruction(
    instruction_tokens: set[str],
    instruction: str,
    db: Session,
    practice_id: uuid.UUID,
) -> tuple[Optional[uuid.UUID], list[AppointmentProposalIssue], BernieConfidenceAxis, list[BernieStaffCheck], list[BerniePatientCandidate]]:
    """Resolve a patient from free-text instruction.

    Patient table is large and identity-critical (PHI) → exact-match only can proceed.
    Fuzzy matches are surfaced as 'Do you mean...?' candidates (band=ask); they never
    silently link, auto-select, or reach band=assume/proceed_with_check on their own.
    A unique fuzzy match backed by a second identifier (DOB/Medicare/phone) may rise
    to proceed_with_check with a staff DOB/identity check.
    """
    exact_matches: list[Patient] = []
    patients = db.query(Patient).filter(Patient.practice_id == practice_id).all()
    for pat in patients:
        if _text_contains_name(instruction_tokens, pat.first_name, pat.last_name):
            exact_matches.append(pat)

    if len(exact_matches) == 1:
        pat = exact_matches[0]
        axis = BernieConfidenceAxis(
            axis="patient_identity",
            band="assume",
            basis="Unique patient register match.",
            staff_detail="I found one current patient with that name in the practice register.",
        )
        return pat.id, [
            AppointmentProposalIssue(
                code="patient_recognized_by_register",
                severity="warning",
                message="I found one current patient with that name in the practice register.",
            )
        ], axis, [], []

    if len(exact_matches) > 1:
        axis = BernieConfidenceAxis(
            axis="patient_identity",
            band="ask",
            basis="Multiple patients share this name — need DOB or another identifier.",
        )
        return None, [
            AppointmentProposalIssue(
                code="ambiguous_patient_name",
                severity="warning",
                message=(
                    "I found more than one patient with that name. "
                    "Can you give me a date of birth?"
                ),
            )
        ], axis, [], []

    # No exact match — try fuzzy (near-match) for candidate proposal only
    _MAX_FUZZY_CANDIDATES = 5
    fuzzy_candidates: list[Patient] = []
    for pat in patients:
        first_tokens = [t for t in _text_tokens(pat.first_name) if len(t) >= 3]
        last_tokens = [t for t in _text_tokens(pat.last_name) if len(t) >= 3]
        name_tokens = first_tokens + last_tokens
        if not name_tokens:
            continue
        if _tokens_near_match(name_tokens, instruction_tokens):
            fuzzy_candidates.append(pat)
        if len(fuzzy_candidates) > _MAX_FUZZY_CANDIDATES:
            break

    # Cap and rank (alphabetical for determinism)
    fuzzy_candidates = sorted(fuzzy_candidates[:_MAX_FUZZY_CANDIDATES], key=lambda p: (p.last_name, p.first_name))

    if fuzzy_candidates:
        has_second_id = _second_identifier_present(instruction)
        if len(fuzzy_candidates) == 1 and has_second_id:
            # Unique fuzzy + corroborating identifier → proceed_with_check
            pat = fuzzy_candidates[0]
            display = f"{pat.first_name} {pat.last_name}"
            axis = BernieConfidenceAxis(
                axis="patient_identity",
                band="proceed_with_check",
                basis=(
                    f"Near-match for {display} corroborated by a second identifier. "
                    "Staff DOB/identity verification still required."
                ),
                staff_detail="Please confirm patient identity and date of birth.",
            )
            candidates = [
                BerniePatientCandidate(
                    candidate_key=str(pat.id),
                    display_name=display,
                    dob_masked=_mask_dob(pat.date_of_birth),
                    match_kind="fuzzy",
                    requires_identifier=True,
                )
            ]
            staff_checks = [
                BernieStaffCheck(
                    code="verify_patient_dob",
                    staff_prompt="Please confirm the patient's identity and date of birth before confirming.",
                )
            ]
            return None, [
                AppointmentProposalIssue(
                    code="patient_fuzzy_corroborated",
                    severity="warning",
                    message=(
                        f"I found a close match: {display}. "
                        "Please confirm patient identity before proceeding."
                    ),
                )
            ], axis, staff_checks, candidates
        else:
            # Fuzzy without corroboration (or multiple fuzzy) → ask + candidate list
            candidates = [
                BerniePatientCandidate(
                    candidate_key=str(p.id),
                    display_name=f"{p.first_name} {p.last_name}",
                    dob_masked=_mask_dob(p.date_of_birth),
                    match_kind="fuzzy",
                    requires_identifier=True,
                )
                for p in fuzzy_candidates
            ]
            axis = BernieConfidenceAxis(
                axis="patient_identity",
                band="ask",
                basis="No exact patient match — fuzzy candidates surfaced for staff selection.",
                staff_detail="I could not find an exact match. Did you mean one of these patients?",
            )
            return None, [
                AppointmentProposalIssue(
                    code="patient_fuzzy_candidates",
                    severity="warning",
                    message=(
                        "I could not find an exact match. "
                        "Did you mean one of these patients?"
                    ),
                )
            ], axis, [], candidates

    # No match at all — patient was not mentioned or not needed; do not block slot search
    axis = BernieConfidenceAxis(
        axis="patient_identity",
        band="assume",
        basis="No patient name detected in instruction — patient context is optional for slot search.",
    )
    return None, [], axis, [], []


def _bernie_clarifying_question(missing_fields: list[str]) -> Optional[str]:
    labels = []
    for field in missing_fields:
        if field == "practitioner_id":
            labels.append("the doctor or nurse")
        elif field == "date_from":
            labels.append("the day")
        else:
            labels.append(field.replace("_", " "))
    if not labels:
        return None
    if len(labels) == 1:
        if missing_fields[0] == "practitioner_id":
            return "Did you forget to mention the doctor or nurse?"
        if missing_fields[0] == "date_from":
            return "Which day would you like me to check?"
        return f"Please tell me {labels[0]} before I search."
    return f"I need {', '.join(labels[:-1])}, and {labels[-1]} before I search."


def _resolve_bernie_interpretation_context(
    result: BernieBookingInstructionInterpretOut,
    body: BernieBookingInstructionInterpretIn,
    db: Session,
    practice_id: uuid.UUID,
) -> BernieBookingInstructionInterpretOut:
    if result.command_candidate is None:
        return result

    command_values = result.command_candidate.model_dump()
    resolver_warnings: list[AppointmentProposalIssue] = []
    instruction_tokens = set(_text_tokens(body.instruction))
    all_assumptions: list[BernieAssumption] = []
    all_staff_checks: list[BernieStaffCheck] = []
    all_patient_candidates: list[BerniePatientCandidate] = []

    # ── Practitioner resolution ───────────────────────────────────────────────
    practitioner_axis: Optional[BernieConfidenceAxis] = None
    if command_values.get("practitioner_id") and not _valid_uuid_text(command_values.get("practitioner_id")):
        command_values["practitioner_id"] = None
    if not command_values.get("practitioner_id"):
        frame_practitioner_id = _context_frame_value(body, "practitioner_id")
        if _valid_uuid_text(frame_practitioner_id):
            command_values["practitioner_id"] = frame_practitioner_id
            practitioner_axis = BernieConfidenceAxis(
                axis="practitioner",
                band="assume",
                basis="Practitioner resolved from context frame UUID.",
            )
        else:
            practitioner_id, warnings, practitioner_axis, pr_assumptions = (
                _resolve_practitioner_from_instruction(
                    instruction_tokens,
                    body.instruction,
                    db,
                    practice_id,
                )
            )
            resolver_warnings.extend(warnings)
            all_assumptions.extend(pr_assumptions)
            if practitioner_id:
                command_values["practitioner_id"] = str(practitioner_id)
            else:
                inferred_practitioner_id, inferred_label, inferred_time = (
                    _booking_context_practitioner_for_patient(
                        body,
                        instruction_tokens,
                        db,
                        practice_id,
                    )
                )
                if inferred_practitioner_id:
                    command_values["practitioner_id"] = str(inferred_practitioner_id)
                    hint = f" from the earlier diary booking at {inferred_time}" if inferred_time else ""
                    practitioner_axis = BernieConfidenceAxis(
                        axis="practitioner",
                        band="proceed_with_check",
                        basis="Practitioner inferred from today's diary context for the named patient.",
                        staff_detail=(
                            f"I used today's diary context{hint} and assumed "
                            f"{inferred_label or 'the same practitioner'}."
                        ),
                    )
                    resolver_warnings.append(AppointmentProposalIssue(
                        code="practitioner_inferred_from_diary_context",
                        severity="warning",
                        message=(
                            f"I used today's diary context{hint} and assumed "
                            f"{inferred_label or 'the same practitioner'}."
                        ),
                    ))
                    all_assumptions.append(BernieAssumption(
                        field="practitioner_id",
                        assumed_value=str(inferred_practitioner_id),
                        basis="Named patient had a unique practitioner in today's diary context.",
                        reversible_copy="Tell me the practitioner if that assumption is wrong.",
                    ))
    else:
        practitioner_axis = BernieConfidenceAxis(
            axis="practitioner",
            band="assume",
            basis="Practitioner UUID provided directly.",
        )

    # ── Patient resolution ────────────────────────────────────────────────────
    patient_axis: Optional[BernieConfidenceAxis] = None
    if command_values.get("patient_id") and not _valid_uuid_text(command_values.get("patient_id")):
        command_values["patient_id"] = None
    if not command_values.get("patient_id"):
        frame_patient_id = _context_frame_value(body, "patient_id")
        if _valid_uuid_text(frame_patient_id):
            command_values["patient_id"] = frame_patient_id
            patient_axis = BernieConfidenceAxis(
                axis="patient_identity",
                band="assume",
                basis="Patient resolved from trusted diary context.",
                staff_detail="I used the selected diary context for patient recognition.",
            )
        else:
            patient_id, warnings, patient_axis, pat_checks, pat_candidates = (
                _resolve_patient_from_instruction(
                    instruction_tokens,
                    body.instruction,
                    db,
                    practice_id,
                )
            )
            resolver_warnings.extend(warnings)
            all_staff_checks.extend(pat_checks)
            all_patient_candidates.extend(pat_candidates)
            if patient_id:
                command_values["patient_id"] = str(patient_id)
    else:
        patient_axis = BernieConfidenceAxis(
            axis="patient_identity",
            band="assume",
            basis="Patient UUID provided directly.",
            staff_detail="Patient record supplied by the calling workflow.",
        )

    # ── Duration default ──────────────────────────────────────────────────────
    if not command_values.get("duration_minutes") and not command_values.get("appointment_type_id"):
        command_values["duration_minutes"] = 15
        resolver_warnings.append(AppointmentProposalIssue(
            code="appointment_duration_defaulted",
            severity="warning",
            message=(
                "Bernie defaulted this generic appointment request to 15 minutes. "
                "Staff should change it if a longer appointment type is needed."
            ),
        ))
        all_assumptions.append(BernieAssumption(
            field="duration_minutes",
            assumed_value="15",
            basis="No duration or appointment type supplied.",
            reversible_copy="Tell me the appointment duration or type if 15 minutes is wrong.",
        ))

    # ── Normalization ─────────────────────────────────────────────────────────
    instruction_relative_date = _resolve_bernie_instruction_relative_date(
        body.instruction,
        body.reference_date,
    )
    if (
        instruction_relative_date
        and command_values.get("date_from") != instruction_relative_date
    ):
        command_values["date_from"] = instruction_relative_date
        resolver_warnings.append(AppointmentProposalIssue(
            code="date_resolved_from_instruction_relative_week",
            severity="warning",
            message="Bernie resolved the requested week-relative date from the instruction.",
        ))
        all_assumptions.append(BernieAssumption(
            field="date_from",
            assumed_value=instruction_relative_date,
            basis="Instruction said in a week's time/next week.",
            reversible_copy="Tell me the date if that week-relative interpretation is wrong.",
        ))

    date_transition = resolve_booking_date_transition(
        date_from=command_values.get("date_from"),
        context_frames=body.context_frames,
    )
    if date_transition.action == "assume" and date_transition.date_from:
        command_values["date_from"] = date_transition.date_from
        resolver_warnings.append(AppointmentProposalIssue(
            code=date_transition.warning_code or "date_assumed_from_context",
            severity="warning",
            message=date_transition.basis,
        ))
        all_assumptions.append(BernieAssumption(
            field="date_from",
            assumed_value=date_transition.date_from,
            basis=date_transition.basis,
            reversible_copy="Tell me the date if this diary page is not what you meant.",
        ))

    command = SlotSearchCommandIn(**command_values)
    normalization = normalize_slot_search_command(
        command,
        reference_date=body.reference_date,
    )

    # ── Intent axis ───────────────────────────────────────────────────────────
    safety_flags = list(result.safety_flags)
    has_autonomous_language = any(
        term in body.instruction.lower() for term in BERNIE_AUTONOMOUS_BOOKING_TERMS
    )
    if has_autonomous_language and "autonomous_booking_language" not in safety_flags:
        safety_flags.append("autonomous_booking_language")

    if "autonomous_booking_language" in safety_flags:
        intent_axis = BernieConfidenceAxis(
            axis="intent",
            band="proceed_with_check",
            basis="Instruction contains booking/confirmation language — staff confirmation still required.",
        )
    else:
        intent_axis = BernieConfidenceAxis(
            axis="intent",
            band="assume",
            basis="Instruction appears to be a read-only slot-search request.",
        )

    # ── Temporal axis (including same-day validity) ───────────────────────────
    date_from_raw = command_values.get("date_from")
    has_explicit_date = (
        bool(date_from_raw) and str(date_from_raw).lower() in ("today", "tomorrow")
    ) or bool(
        date_from_raw and re.match(r"^\d{4}-\d{2}-\d{2}$", str(date_from_raw))
    )
    # Only truly contradictory/invalid dates (not missing-field) warrant a temporal block.
    # missing_date_from / relative_date_no_reference are clarification signals handled below.
    has_invalid_date_block = any(
        b.code == "invalid_date_from"
        for b in normalization.blocks
    )

    temporal_band: BernieConfidenceBand
    temporal_basis: str
    temporal_clarifying: Optional[str] = None

    if has_invalid_date_block:
        temporal_band = "block"
        temporal_basis = "Date provided is invalid or contradictory."
    elif has_explicit_date:
        temporal_band = "assume"
        temporal_basis = (
            date_transition.basis
            if date_transition.action == "assume"
            else "Explicit date provided."
        )
    else:
        # No explicit or UI-derived date: must ask.
        temporal_band = "ask"
        temporal_basis = date_transition.basis
        temporal_clarifying = (
            date_transition.clarifying_question
            or "Which day would you like me to check?"
        )

    # Same-day validity: if resolved date == today (clinic-local), check that time is not past.
    # The normalizer resolves "today" → reference_date; we check if that equals actual today.
    resolved_date = (
        normalization.constraint.date_from
        if normalization.constraint is not None
        else None
    )
    if resolved_date is not None and temporal_band in ("assume", "proceed_with_check"):
        practice_tz = _practice_zoneinfo(db, practice_id)
        clinic_now = _clinic_local_now(practice_tz)
        if resolved_date == clinic_now.date():
            # Same-day request: check earliest_time (or latest_time) against now
            _earliest = normalization.constraint.earliest_time if normalization.constraint else None
            _latest = normalization.constraint.latest_time if normalization.constraint else None
            now_time = clinic_now.time().replace(second=0, microsecond=0)
            if _earliest is not None and _latest is not None:
                # Window defined: check if it is fully past
                if _latest <= now_time:
                    temporal_band = "ask"
                    temporal_basis = "Same-day request: the requested time window has already passed today."
                    temporal_clarifying = (
                        "That time has already passed today — would you like a later time or another day?"
                    )
                elif _earliest < now_time:
                    # Partly past — clamp earliest_time forward to now
                    clamp_hhmm = now_time.strftime("%H:%M")
                    if command_values.get("earliest_time"):
                        command_values["earliest_time"] = clamp_hhmm
                    # Re-normalize with clamped time
                    command = SlotSearchCommandIn(**command_values)
                    normalization = normalize_slot_search_command(
                        command, reference_date=body.reference_date
                    )
                    temporal_basis = (
                        f"Same-day request: earliest time clamped to {clamp_hhmm} "
                        "(original time had partly passed)."
                    )
            elif _earliest is not None and _earliest <= now_time:
                # Open-ended "after X today" requests remain useful after X has passed:
                # clamp forward so Bernie never offers past slots, but does not block.
                clamp_hhmm = now_time.strftime("%H:%M")
                if command_values.get("earliest_time"):
                    command_values["earliest_time"] = clamp_hhmm
                command = SlotSearchCommandIn(**command_values)
                normalization = normalize_slot_search_command(
                    command, reference_date=body.reference_date
                )
                temporal_basis = (
                    f"Same-day request: earliest time clamped to {clamp_hhmm} "
                    "(open-ended start time had already passed)."
                )

    temporal_axis = BernieConfidenceAxis(
        axis="temporal",
        band=temporal_band,
        basis=temporal_basis,
    )

    # ── Slot-validity axis (mirrors normalization, excluding missing-field blocks) ──
    # missing_practitioner_id / missing_date_from are handled by practitioner/temporal
    # axes as "ask"; do not double-count them as hard blocks in slot_validity.
    _FIELD_BLOCK_CODES = frozenset({
        "missing_practitioner_id",
        "missing_date_from",
        "relative_date_no_reference",
    })
    non_field_blocks = [b for b in normalization.blocks if b.code not in _FIELD_BLOCK_CODES]
    if non_field_blocks:
        slot_validity_band: BernieConfidenceBand = "block"
        slot_basis = "Normalization blocked: " + "; ".join(b.code for b in non_field_blocks)
    elif not normalization.safe:
        slot_validity_band = "ask"
        slot_basis = "Normalization has warnings that require clarification."
    else:
        slot_validity_band = "assume"
        slot_basis = "Slot-search constraint is valid."
    slot_validity_axis = BernieConfidenceAxis(
        axis="slot_validity",
        band=slot_validity_band,
        basis=slot_basis,
    )

    # ── Aggregate axes ────────────────────────────────────────────────────────
    # Preserve speech_transcription placeholder from the service if present
    speech_axis = next(
        (a for a in result.confidence_axes if a.axis == "speech_transcription"),
        BernieConfidenceAxis(
            axis="speech_transcription",
            band="assume",
            basis="No transcription input — reserved placeholder.",
        ),
    )
    computed_axes = [
        intent_axis,
        temporal_axis,
        practitioner_axis or BernieConfidenceAxis(axis="practitioner", band="ask", basis="Unresolved"),
        patient_axis or BernieConfidenceAxis(axis="patient_identity", band="ask", basis="Unresolved"),
        slot_validity_axis,
        speech_axis,
    ]
    overall_band = _lattice_min([a.band for a in computed_axes])  # type: ignore[arg-type]

    # ── Map overall band to result/autonomy_tier ──────────────────────────────
    missing_fields: list[str] = []
    if command.practitioner_id is None:
        missing_fields.append("practitioner_id")
    if command.date_from is None:
        missing_fields.append("date_from")

    if overall_band == "block":
        final_result = "blocked"
        final_autonomy = "blocked"
        final_safe = False
    elif overall_band == "ask":
        final_result = "clarification_required"
        final_autonomy = "blocked"
        final_safe = False
    else:
        # assume or proceed_with_check — interpreted if required fields are present
        if missing_fields or not normalization.safe:
            final_result = "clarification_required"
            final_autonomy = "blocked"
            final_safe = False
        else:
            final_result = "interpreted"
            final_autonomy = "execute_with_report"
            final_safe = True

    # ── Build BernieDecisionPolicy ────────────────────────────────────────────
    decision = BernieDecisionPolicy(
        overall_band=overall_band,
        rationale=(
            f"Axes: {', '.join(f'{a.axis}={a.band}' for a in computed_axes)}. "
            f"Result: {final_result}."
        ),
        requires_staff_confirmation=True,
    )

    # ── First-person clarifying copy ──────────────────────────────────────────
    clarifying: Optional[str] = temporal_clarifying
    if not clarifying:
        clarifying = _bernie_clarifying_question(missing_fields)
    # Add patient-specific clarifying copy if needed
    if not clarifying and all_patient_candidates:
        clarifying = "I could not find an exact patient match — did you mean one of these patients?"
    if not clarifying and any(a.axis == "practitioner" and a.band == "ask" for a in computed_axes):
        clarifying = "Which practitioner would you like the appointment with?"

    # ── Autonomous language warning (de-duped) ────────────────────────────────
    warnings = [*result.warnings, *resolver_warnings, *normalization.warnings]
    if (
        "autonomous_booking_language" in safety_flags
        and not any(w.code == "autonomous_booking_language" for w in warnings)
    ):
        warnings.append(AppointmentProposalIssue(
            code="autonomous_booking_language",
            severity="warning",
            message=(
                "Instruction contains booking/confirmation language; staff "
                "confirmation is still required."
            ),
        ))
    blocks = list(normalization.blocks)

    # ── Debug field (gated by config flag) ───────────────────────────────────
    debug_payload: Optional[dict] = None
    if settings.bernie_interpreter_debug_disclosure:
        debug_payload = {
            "axes": {a.axis: {"band": a.band, "basis": a.basis} for a in computed_axes},
            "scalar_confidence_advisory": result.confidence,
            "normalization_safe": normalization.safe,
        }

    # ── Immutable request reference date ─────────────────────────────────────
    # Echo the inbound reference_date, or resolve clinic-local today when omitted.
    request_ref_date = body.reference_date
    if request_ref_date is None:
        _ref_tz = _practice_zoneinfo(db, practice_id)
        request_ref_date = _clinic_local_now(_ref_tz).date()

    # ── Patient booking context (recognized-patient only, band=assume) ───────────
    # Fetch context only for exact-match recognized patients; fuzzy/ambiguous
    # candidates stay at band=ask with patient_id unset — no context for them.
    patient_booking_ctx: Optional[BerniePatientBookingContext] = None
    context_freshness_val: Optional[BernieContextFreshness] = None
    if (
        patient_axis is not None
        and patient_axis.band == "assume"
        and command_values.get("patient_id")
    ):
        try:
            _pid = uuid.UUID(str(command_values["patient_id"]))
            patient_booking_ctx = build_patient_booking_context(
                db, practice_id, _pid, request_ref_date
            )
            if has_existing_booking_on_requested_day(
                patient_booking_ctx,
                normalization.constraint.date_from if normalization.constraint else None,
            ):
                if not any(w.code == "existing_future_follow_up" for w in warnings):
                    warnings.append(build_existing_future_follow_up_warning())
            _ref_tz2 = _practice_zoneinfo(db, practice_id)
            _clinic_today = _clinic_local_now(_ref_tz2).date()
            context_freshness_val = BernieContextFreshness(
                reference_date=request_ref_date,
                generated_at=patient_booking_ctx.generated_at,
                stale=request_ref_date != _clinic_today,
                basis=(
                    "reference_date matches clinic-local today"
                    if request_ref_date == _clinic_today
                    else "reference_date differs from clinic-local today; context may be stale"
                ),
            )
        except (TypeError, ValueError):
            pass

    return result.model_copy(update={
        "safe": final_safe,
        "result": final_result,
        "autonomy_tier": final_autonomy,
        "summary": result.summary,
        "request_reference_date": request_ref_date,
        "command_candidate": command,
        "missing_fields": missing_fields,
        "clarifying_question": clarifying,
        "safety_flags": safety_flags,
        "normalization": normalization,
        "warnings": warnings,
        "blocks": blocks,
        "confidence_axes": computed_axes,
        "decision": decision,
        "assumptions": all_assumptions,
        "staff_checks": all_staff_checks,
        "patient_candidates": all_patient_candidates,
        "debug": debug_payload,
        "patient_booking_context": patient_booking_ctx,
        "context_freshness": context_freshness_val,
    })


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
    values = body.model_dump(exclude_unset=True, exclude={"confirmed_warnings"})

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
        confirmed_warnings=body.confirmed_warnings,
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
    entries = (
        db.query(AppointmentAuditLog)
        .filter(
            AppointmentAuditLog.practice_id == practice_id,
            AppointmentAuditLog.appointment_id == appointment_id,
        )
        .order_by(AppointmentAuditLog.created_at)
        .all()
    )
    actor_ids = {entry.confirmed_by_user_id for entry in entries}
    actors = {}
    if actor_ids:
        actors = {
            user.id: user
            for user in (
                db.query(User)
                .options(joinedload(User.practitioner))
                .filter(User.practice_id == practice_id, User.id.in_(actor_ids))
                .all()
            )
        }

    response = []
    for entry in entries:
        actor_display, actor_role = _audit_actor_display(actors.get(entry.confirmed_by_user_id))
        response.append(AppointmentAuditLogOut(
            id=entry.id,
            appointment_id=entry.appointment_id,
            practice_id=entry.practice_id,
            confirmed_by_user_id=entry.confirmed_by_user_id,
            confirmed_by_display=actor_display,
            confirmed_by_role=actor_role,
            action=entry.action,
            status_before=entry.status_before,
            status_after=entry.status_after,
            cancellation_reason=entry.cancellation_reason,
            confirmed_warnings=entry.confirmed_warnings or [],
            created_at=entry.created_at,
        ))
    return response


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
        confirmed_warnings=body.confirmed_warnings,
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
        confirmed_warnings=body.confirmed_warnings if body else None,
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

def _resolve_day_schedule(
    db: Session,
    practitioner_id: uuid.UUID,
    target_date: date_type,
) -> Optional[tuple[time, time, int]]:
    """Return (start_time, end_time, slot_minutes) for practitioner on target_date.

    Returns None when the practitioner has no schedule or an unavailability override.
    """
    override = db.query(ScheduleOverride).filter(
        ScheduleOverride.practitioner_id == practitioner_id,
        ScheduleOverride.date == target_date,
    ).first()

    if override and override.is_unavailable:
        return None

    day_of_week = target_date.weekday()
    schedule = db.query(PractitionerSchedule).filter(
        PractitionerSchedule.practitioner_id == practitioner_id,
        PractitionerSchedule.day_of_week == day_of_week,
    ).first()

    if not schedule:
        return None

    start_t = override.override_start if (override and override.override_start) else schedule.start_time
    end_t = override.override_end if (override and override.override_end) else schedule.end_time
    return start_t, end_t, schedule.slot_duration_minutes


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

    day_schedule = _resolve_day_schedule(db, practitioner_id, target_date)
    if day_schedule is None:
        return []

    start_t, end_t, slot_mins = day_schedule
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


def _build_slot_search_proposal(
    body: SlotSearchProposalIn,
    db: Session,
    practice_id: uuid.UUID,
) -> SlotSearchProposalOut:
    practitioner = db.query(Practitioner).filter(
        Practitioner.id == body.practitioner_id,
        Practitioner.practice_id == practice_id,
    ).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    if body.appointment_type_id is not None:
        _ensure_appointment_type(body.appointment_type_id, practice_id, db)

    if body.location_id is not None:
        _ensure_location(body.location_id, practice_id, db)

    if body.patient_id is not None:
        _ensure_patient(body.patient_id, practice_id, db)

    blocks: list[AppointmentProposalIssue] = []

    # Resolve duration: explicit > appointment type default
    resolved_duration: Optional[int] = body.duration_minutes
    if resolved_duration is None and body.appointment_type_id is not None:
        resolved_duration = (
            db.query(AppointmentType.default_duration)
            .filter(AppointmentType.id == body.appointment_type_id)
            .scalar()
        )

    if resolved_duration is None:
        blocks.append(AppointmentProposalIssue(
            code="missing_duration",
            severity="blocked",
            message=(
                "duration_minutes is required when no appointment_type_id is supplied "
                "or the type has no default duration."
            ),
        ))

    effective_to = body.date_to if body.date_to is not None else body.date_from

    if blocks:
        return SlotSearchProposalOut(
            safe=False,
            autonomy_tier="blocked",
            summary="Cannot search: missing required constraints.",
            resolved_duration_minutes=resolved_duration,
            blocks=blocks,
        )

    practice_tz = _practice_zoneinfo(db, practice_id)
    candidates: list[SlotCandidate] = []
    current_date = body.date_from

    while current_date <= effective_to and len(candidates) < body.limit:
        day_schedule = _resolve_day_schedule(db, body.practitioner_id, current_date)
        if day_schedule is None:
            current_date += timedelta(days=1)
            continue

        sched_start, sched_end, slot_mins = day_schedule
        day_start = datetime.combine(current_date, sched_start)
        day_end = datetime.combine(current_date, sched_end)

        slot_start = day_start
        while slot_start + timedelta(minutes=resolved_duration) <= day_end:
            slot_time_local = slot_start.time()

            # Apply optional time-of-day window
            if body.earliest_time is not None and slot_time_local < body.earliest_time:
                slot_start += timedelta(minutes=slot_mins)
                continue
            if body.latest_time is not None and slot_time_local >= body.latest_time:
                break

            conflict = _find_conflicting_appointment(
                db,
                practice_id,
                body.practitioner_id,
                current_date,
                slot_time_local,
                resolved_duration,
                location_id=body.location_id,
            )

            if conflict is None:
                # Slot is free — check for break overlaps (soft warning)
                break_labels = _get_break_overlaps(
                    db,
                    practice_id,
                    body.practitioner_id,
                    current_date,
                    slot_time_local,
                    resolved_duration,
                    location_id=body.location_id,
                )
                per_candidate_warnings = [
                    AppointmentProposalIssue(
                        code="break_overlap",
                        severity="warning",
                        message=f"This slot overlaps {label}.",
                    )
                    for label in break_labels
                ]

                slot_end_local = slot_start + timedelta(minutes=resolved_duration)
                start_utc = _utc_from_local(current_date, slot_time_local, practice_tz)
                end_utc = start_utc + timedelta(minutes=resolved_duration)

                candidates.append(SlotCandidate(
                    appointment_date=current_date,
                    start_time=start_utc,
                    end_time=end_utc,
                    start_time_local=slot_time_local,
                    duration_minutes=resolved_duration,
                    warnings=per_candidate_warnings,
                ))

                if len(candidates) >= body.limit:
                    break

            slot_start += timedelta(minutes=slot_mins)

        current_date += timedelta(days=1)

    date_range_str = (
        body.date_from.isoformat()
        if body.date_from == effective_to
        else f"{body.date_from.isoformat()} to {effective_to.isoformat()}"
    )

    summary = (
        f"Found {len(candidates)} candidate slot{'s' if len(candidates) != 1 else ''} "
        f"for {resolved_duration} min with {practitioner.first_name} {practitioner.last_name} "
        f"on {date_range_str}."
    )
    if not candidates:
        summary += " No free slots found in the requested window."

    return SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary=summary,
        resolved_duration_minutes=resolved_duration,
        candidates=candidates,
    )


@router.post("/proposals/slot-search", response_model=SlotSearchProposalOut)
def propose_slot_search(
    body: SlotSearchProposalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Non-mutating candidate slot search for future Bernie/reception use.

    Evaluates practitioner schedule, existing bookings, break overlaps, and
    optional time-of-day and location constraints without writing appointments
    or audit rows. Returns ranked candidate slots for staff review.
    autonomy_tier='execute_with_report' means the search result may be presented
    directly; a booking still requires POST /proposals/create + confirmation.
    """
    return _build_slot_search_proposal(body, db, current_user.practice_id)


@router.post("/proposals/slot-search/normalize", response_model=SlotSearchCommandResult)
def normalize_slot_search_proposal_command(
    body: SlotSearchCommandIn,
    reference_date: date_type = Query(...),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Deterministically normalize a Bernie slot-search command without side effects.

    The caller must supply reference_date explicitly so relative command tokens
    such as "today" and "tomorrow" never depend on server wall-clock time. This
    endpoint intentionally performs no DB lookup, slot search, LLM call, audit
    write, or appointment mutation.
    """
    _ = current_user
    return normalize_slot_search_command(body, reference_date=reference_date)


@router.post(
    "/proposals/slot-search/normalized",
    response_model=SlotSearchCommandExecutionOut,
)
def propose_normalized_slot_search(
    body: SlotSearchCommandIn,
    reference_date: date_type = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Normalize a Bernie slot-search command and search only when safe.

    The normalization step is deterministic and requires an explicit reference
    date. Blocked normalization returns context without evaluating schedules or
    conflicts. Safe normalization reuses the same non-mutating proposal path as
    /proposals/slot-search.
    """
    normalization = normalize_slot_search_command(body, reference_date=reference_date)
    if not normalization.safe or normalization.constraint is None:
        return SlotSearchCommandExecutionOut(
            safe=False,
            normalization=normalization,
            proposal=None,
            warnings=normalization.warnings,
            blocks=normalization.blocks,
            summary=normalization.summary,
        )

    proposal = _build_slot_search_proposal(
        normalization.constraint,
        db,
        current_user.practice_id,
    )
    warnings = [*normalization.warnings, *proposal.warnings]
    blocks = [*normalization.blocks, *proposal.blocks]
    return SlotSearchCommandExecutionOut(
        safe=proposal.safe,
        normalization=normalization,
        proposal=proposal,
        warnings=warnings,
        blocks=blocks,
        summary=f"{normalization.summary} {proposal.summary}",
    )


def _same_slot_candidate(left: SlotCandidate, right: SlotCandidate) -> bool:
    return (
        left.appointment_date == right.appointment_date
        and left.start_time_local == right.start_time_local
        and left.duration_minutes == right.duration_minutes
        and left.start_time == right.start_time
        and left.end_time == right.end_time
    )


def _selection_block(code: str, message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(
        code=code,
        severity="blocked",
        message=message,
    )


def _block_slot_selection(
    blocks: list[AppointmentProposalIssue],
    selected_candidate: Optional[SlotCandidate] = None,
) -> SlotSelectionProposalOut:
    return SlotSelectionProposalOut(
        safe=False,
        requires_confirmation=True,
        autonomy_tier="blocked",
        summary="Cannot prepare create proposal from selected slot. See blocked issues.",
        selected_candidate=selected_candidate,
        create_proposal=None,
        blocks=blocks,
    )


def _bernie_staff_review_slot_summary(candidate: SlotCandidate) -> BernieStaffReviewSlotSummary:
    return BernieStaffReviewSlotSummary(
        appointment_date=candidate.appointment_date,
        start_time_local=candidate.start_time_local,
        duration_minutes=candidate.duration_minutes,
        warnings=candidate.warnings,
    )


def _digits_only(value: Optional[str]) -> str:
    return "".join(ch for ch in (value or "") if ch.isdigit())


def _bernie_context_frame_types(context_frames: list[dict]) -> list[str]:
    frame_types: list[str] = []
    for frame in context_frames:
        if not isinstance(frame, dict):
            continue
        frame_type = str(frame.get("type") or "").strip()
        if frame_type and frame_type not in frame_types:
            frame_types.append(frame_type)
    return frame_types


def _caller_id_matches_patient(context_frames: list[dict], patient: Patient) -> bool:
    patient_numbers = {
        _digits_only(patient.phone_mobile),
        _digits_only(patient.phone_home),
    }
    patient_numbers.discard("")
    if not patient_numbers:
        return False
    for frame in context_frames:
        if not isinstance(frame, dict) or frame.get("type") != "caller_id":
            continue
        caller_number = _digits_only(
            frame.get("phone_number")
            or frame.get("caller_number")
            or frame.get("from")
        )
        if caller_number and caller_number in patient_numbers:
            return True
    return False


def _identity_verification_frame(context_frames: list[dict]) -> Optional[dict]:
    for frame in context_frames:
        if isinstance(frame, dict) and frame.get("type") == "identity_verification":
            return frame
    return None


def _build_bernie_identity_evidence(
    patient_id: Optional[uuid.UUID],
    patient_name_provisional: Optional[str],
    db: Session,
    practice_id: uuid.UUID,
    context_frames: Optional[list[dict]] = None,
) -> tuple[BernieIdentityEvidence, Optional[Patient]]:
    frames = context_frames or []
    supporting_context = _bernie_context_frame_types(frames)
    if patient_id is None:
        label = patient_name_provisional or "No linked patient"
        return BernieIdentityEvidence(
            patient_label=label,
            confidence="unlinked",
            recognition_status="not_recognized",
            details_verification_status="not_checked",
            verification_status="requires_staff_verification",
            supporting_context=supporting_context,
            warnings=["patient_not_linked"],
            staff_prompt=(
                "Link the patient record or create a provisional booking only "
                "after staff recognise the patient from the practice register "
                "or another reliable identifier."
            ),
        ), None

    patient = db.query(Patient).filter(
        Patient.practice_id == practice_id,
        Patient.id == patient_id,
    ).first()
    if patient is None:
        return BernieIdentityEvidence(
            patient_id=patient_id,
            confidence="low",
            recognition_status="not_recognized",
            details_verification_status="requires_follow_up",
            verification_status="requires_staff_verification",
            supporting_context=supporting_context,
            warnings=["linked_patient_not_found"],
            staff_prompt="The linked patient record was not found in this practice; do not confirm until resolved.",
        ), None

    matched_fields = ["patient_id", "name", "date_of_birth"]
    warnings: list[str] = []
    if patient.medicare_number:
        matched_fields.append("medicare_on_record")
    else:
        warnings.append("medicare_not_on_record")

    caller_match = _caller_id_matches_patient(frames, patient)
    if caller_match:
        matched_fields.append("caller_id_phone_match")

    verification_frame = _identity_verification_frame(frames)
    verification_verified = False
    if verification_frame:
        method = str(verification_frame.get("method") or "identity_verification")
        supporting_label = f"identity_verification:{method}"
        if supporting_label not in supporting_context:
            supporting_context.append(supporting_label)
        if verification_frame.get("verified") is True or verification_frame.get("status") == "verified":
            verification_verified = True
            matched_fields.append(f"{method}_verified")
        else:
            reason_code = verification_frame.get("reason_code") or "not_verified"
            warnings.append(f"identity_verification_{reason_code}")

    duplicate_count = db.query(Patient).filter(
        Patient.practice_id == practice_id,
        Patient.first_name == patient.first_name,
        Patient.last_name == patient.last_name,
        Patient.date_of_birth == patient.date_of_birth,
    ).count()
    if duplicate_count > 1:
        warnings.append("same_name_and_dob_duplicate")

    if (
        patient.first_name.strip().lower() == "onlyname"
        or patient.last_name.strip().lower() == "onlyname"
    ):
        warnings.append("onlyname_mapping_requires_claim_contract_verification")

    confidence: Literal["low", "medium", "high", "ambiguous"] = "medium"
    if duplicate_count > 1:
        confidence = "ambiguous"
    elif verification_verified:
        confidence = "high"
    elif caller_match and patient.medicare_number:
        confidence = "high"
    elif not patient.medicare_number:
        confidence = "medium"

    recognition_status = "recognized"
    details_verification_status = "not_required_for_booking"
    verification_status = "not_applicable"
    staff_prompt = (
        "Patient recognised from the practice register. Medicare/HI details "
        "can be verified separately before billing if they have not already "
        "been checked."
    )
    if duplicate_count > 1:
        recognition_status = "ambiguous"
        details_verification_status = "requires_follow_up"
        verification_status = "requires_staff_verification"
        staff_prompt = (
            "Same name and DOB exists more than once in this practice. Treat "
            "the booking as provisional until Medicare/card or another strong "
            "identifier distinguishes the patient."
        )
    elif caller_match:
        staff_prompt = (
            "Caller ID matches a phone number on the linked record. Patient "
            "recognition is stronger for booking purposes."
        )

    return BernieIdentityEvidence(
        patient_id=patient.id,
        patient_label=f"{patient.first_name} {patient.last_name}",
        confidence=confidence,
        recognition_status=recognition_status,
        details_verification_status=details_verification_status,
        verification_status=verification_status,
        matched_fields=matched_fields,
        supporting_context=supporting_context,
        warnings=warnings,
        staff_prompt=staff_prompt,
    ), patient


def _mask_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "****"
    return "*" * (len(digits) - 4) + digits[-4:]


def _build_bernie_patient_evidence(
    identity_evidence: BernieIdentityEvidence,
    patient: Optional[Patient],
) -> Optional[BerniePatientEvidence]:
    if patient is None:
        if identity_evidence.confidence == "unlinked":
            return BerniePatientEvidence(
                patient_label=identity_evidence.patient_label or "No linked patient",
                confidence="unlinked",
                is_provisional=True,
            )
        return None
    return BerniePatientEvidence(
        patient_id=patient.id,
        patient_label=f"{patient.first_name} {patient.last_name}",
        date_of_birth=patient.date_of_birth,
        masked_phone=_mask_phone(patient.phone_mobile),
        confidence=identity_evidence.confidence,
        is_provisional=False,
    )


def _build_bernie_practitioner_evidence(
    practitioner_id: Optional[uuid.UUID],
    location_id: Optional[uuid.UUID],
    db: Session,
    practice_id: uuid.UUID,
) -> Optional[BerniePractitionerEvidence]:
    if practitioner_id is None:
        return None
    prac = db.query(Practitioner).filter(
        Practitioner.id == practitioner_id,
        Practitioner.practice_id == practice_id,
    ).first()
    if prac is None:
        return None
    location_label: Optional[str] = None
    loc_id = location_id or prac.default_location_id
    if loc_id is not None:
        loc = db.query(PracticeLocation).filter(
            PracticeLocation.id == loc_id,
            PracticeLocation.practice_id == practice_id,
        ).first()
        if loc is not None:
            location_label = loc.name
    return BerniePractitionerEvidence(
        practitioner_id=prac.id,
        display_name=f"{prac.first_name} {prac.last_name}",
        provider_number=prac.provider_number,
        location_label=location_label,
    )


def _bernie_staff_review_payload(
    result: str,
    summary: str,
    warnings: list[AppointmentProposalIssue],
    blocks: list[AppointmentProposalIssue],
    search_proposal: Optional[SlotSearchProposalOut] = None,
    selection_proposal: Optional[SlotSelectionProposalOut] = None,
    identity_evidence: Optional[BernieIdentityEvidence] = None,
    practitioner_evidence: Optional[BerniePractitionerEvidence] = None,
    patient_evidence: Optional[BerniePatientEvidence] = None,
) -> BernieStaffReviewPayload:
    selected_slot = None
    if selection_proposal is not None and selection_proposal.selected_candidate is not None:
        selected_slot = _bernie_staff_review_slot_summary(
            selection_proposal.selected_candidate
        )

    candidate_slots = []
    if result == "candidate_selection_required" and search_proposal is not None:
        candidate_slots = [
            _bernie_staff_review_slot_summary(candidate)
            for candidate in search_proposal.candidates
        ]

    confirmation_ready = (
        result == "confirmation_ready"
        and selection_proposal is not None
        and selection_proposal.safe
        and selection_proposal.create_proposal is not None
    )
    confirm_payload = None
    confirm_endpoint = None
    confirm_evidence: list[str] = []
    if confirmation_ready:
        confirm_endpoint = "/api/v1/appointments/proposals/create/confirm-bernie"
        confirm_payload = BernieCreateProposalConfirmationIn(
            confirmed=False,
            selection_proposal=selection_proposal,
            confirmed_warnings=[],
        ).model_dump(mode="json")
        confirm_evidence = list(_BERNIE_CONFIRM_CREATE_BASE_EVIDENCE)

    warning_summary = "No warnings or blocked issues."
    if warnings or blocks:
        warning_summary = (
            f"{len(warnings)} warning(s), {len(blocks)} blocked issue(s)."
        )
    evidence_summaries = {
        "blocked": "Blocked review payload; no confirm evidence is available.",
        "candidate_selection_required": "Candidate slot summaries are review-only until staff selects one slot.",
        "confirmation_ready": "Confirm payload carries slot-selection and create-proposal evidence for explicit staff approval.",
        "clinic_day_exhausted": "No bookable slots remain today - restate the date to continue.",
    }
    staff_actions = {
        "blocked": "Review blocked issues before retrying; no booking can be confirmed from this payload.",
        "candidate_selection_required": "Select one candidate slot before preparing confirmation evidence.",
        "confirmation_ready": "Review the selected slot and submit the confirm payload only after explicit staff confirmation.",
        "clinic_day_exhausted": "Please restate the date - no slots remain today after the requested time.",
    }
    return BernieStaffReviewPayload(
        headline=summary,
        status=result,
        staff_action_required=staff_actions[result],
        confirmation_ready=confirmation_ready,
        selected_slot=selected_slot,
        candidate_slots=candidate_slots,
        identity_evidence=identity_evidence,
        practitioner_evidence=practitioner_evidence,
        patient_evidence=patient_evidence,
        warning_summary=warning_summary,
        evidence_summary=evidence_summaries[result],
        warnings=warnings,
        blocks=blocks,
        confirm_endpoint=confirm_endpoint,
        confirm_payload=confirm_payload,
        confirm_evidence=confirm_evidence,
    )


def _resolve_selected_candidate(
    body: SlotSelectionProposalIn,
    blocks: list[AppointmentProposalIssue],
) -> Optional[SlotCandidate]:
    if body.search_execution is None:
        return body.selected_candidate

    execution = body.search_execution
    if not execution.safe or execution.proposal is None or not execution.proposal.safe:
        blocks.append(_selection_block(
            "slot_search_not_safe",
            "The slot-search result is not safe to select from.",
        ))
        return None

    candidates = execution.proposal.candidates
    if not candidates:
        blocks.append(_selection_block(
            "no_slot_candidates",
            "The slot-search result contains no selectable candidates.",
        ))
        return None

    indexed_candidate = None
    if body.selected_candidate_index is not None:
        if body.selected_candidate_index >= len(candidates):
            blocks.append(_selection_block(
                "selected_candidate_index_out_of_range",
                "The selected candidate index is outside the slot-search results.",
            ))
            return None
        indexed_candidate = candidates[body.selected_candidate_index]

    if body.selected_candidate is None:
        if indexed_candidate is None:
            blocks.append(_selection_block(
                "selected_candidate_required",
                "Select a candidate by index or supply the selected candidate evidence.",
            ))
            return None
        return indexed_candidate

    if indexed_candidate is not None:
        if not _same_slot_candidate(indexed_candidate, body.selected_candidate):
            blocks.append(_selection_block(
                "selected_candidate_mismatch",
                "The selected candidate evidence does not match the candidate at the selected index.",
            ))
            return None
        return indexed_candidate

    for candidate in candidates:
        if _same_slot_candidate(candidate, body.selected_candidate):
            return candidate

    blocks.append(_selection_block(
        "selected_candidate_not_in_results",
        "The selected candidate was not found in the slot-search results.",
    ))
    return None


def _resolve_selection_context(
    body: SlotSelectionProposalIn,
    blocks: list[AppointmentProposalIssue],
) -> tuple[
    Optional[uuid.UUID],
    Optional[uuid.UUID],
    Optional[uuid.UUID],
    Optional[uuid.UUID],
]:
    constraint = None
    if (
        body.search_execution is not None
        and body.search_execution.normalization.constraint is not None
    ):
        constraint = body.search_execution.normalization.constraint

    practitioner_id = body.practitioner_id
    appointment_type_id = body.appointment_type_id
    location_id = body.location_id
    patient_id = body.patient_id

    if constraint is not None:
        if practitioner_id is None:
            practitioner_id = constraint.practitioner_id
        elif practitioner_id != constraint.practitioner_id:
            blocks.append(_selection_block(
                "practitioner_mismatch",
                "The requested practitioner does not match the normalized slot-search constraint.",
            ))

        if appointment_type_id is None:
            appointment_type_id = constraint.appointment_type_id
        elif (
            constraint.appointment_type_id is not None
            and appointment_type_id != constraint.appointment_type_id
        ):
            blocks.append(_selection_block(
                "appointment_type_mismatch",
                "The requested appointment type does not match the normalized slot-search constraint.",
            ))

        if location_id is None:
            location_id = constraint.location_id
        elif constraint.location_id is not None and location_id != constraint.location_id:
            blocks.append(_selection_block(
                "location_mismatch",
                "The requested location does not match the normalized slot-search constraint.",
            ))

        if patient_id is None:
            patient_id = constraint.patient_id
        elif constraint.patient_id is not None and patient_id != constraint.patient_id:
            blocks.append(_selection_block(
                "patient_mismatch",
                "The requested patient does not match the normalized slot-search constraint.",
            ))

    if practitioner_id is None:
        blocks.append(_selection_block(
            "missing_practitioner",
            "practitioner_id is required when no normalized slot-search constraint supplies it.",
        ))

    return practitioner_id, appointment_type_id, location_id, patient_id


@router.post(
    "/proposals/slot-search/selection",
    response_model=SlotSelectionProposalOut,
)
def propose_slot_selection_for_create(
    body: SlotSelectionProposalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Convert one supervised slot-search candidate into create-proposal evidence.

    This route does not create, confirm, edit, or audit appointments. It only
    validates that the selected slot is consistent with supplied slot-search
    evidence and then reuses the existing non-mutating create-proposal contract
    so staff can review the final booking command before any write.
    """
    blocks: list[AppointmentProposalIssue] = []
    selected_candidate = _resolve_selected_candidate(body, blocks)
    practitioner_id, appointment_type_id, location_id, patient_id = _resolve_selection_context(
        body,
        blocks,
    )

    if selected_candidate is None or blocks:
        return _block_slot_selection(blocks, selected_candidate)

    create_body = AppointmentCreate(
        patient_id=patient_id,
        patient_name_provisional=body.patient_name_provisional,
        practitioner_id=practitioner_id,
        appointment_type_id=appointment_type_id,
        location_id=location_id,
        appointment_date=selected_candidate.appointment_date,
        start_time_local=selected_candidate.start_time_local,
        duration_minutes=selected_candidate.duration_minutes,
        reason=body.reason,
        notes=body.notes,
        booked_via=body.booked_via,
    )
    create_proposal = _build_create_appointment_proposal(
        create_body,
        db,
        current_user.practice_id,
    )

    warnings = [*selected_candidate.warnings, *create_proposal.warnings]
    blocks = [*create_proposal.blocks]
    safe = create_proposal.safe
    summary = (
        "Prepared create proposal from selected slot. "
        f"{create_proposal.summary}"
    )

    return SlotSelectionProposalOut(
        safe=safe,
        requires_confirmation=True,
        autonomy_tier="proposal" if safe else "blocked",
        summary=summary,
        selected_candidate=selected_candidate,
        create_proposal=create_proposal,
        warnings=warnings,
        blocks=blocks,
    )


def _build_no_slot_suggestions(constraint: SlotSearchProposalIn) -> list[BernieSlotSuggestion]:
    """Build typed non-mutating next-step suggestions when a slot search yields zero candidates.

    Called only when the search returned no candidates AND the clinic day is not exhausted.
    Each suggestion carries requires_confirmation=True — the UI must never auto-apply them.
    """
    suggestions: list[BernieSlotSuggestion] = [
        BernieSlotSuggestion(
            kind="next_available_day",
            summary="Search the next day for available slots.",
            params={"date_from": (constraint.date_from + timedelta(days=1)).isoformat()},
            requires_confirmation=True,
        ),
    ]
    if constraint.earliest_time is not None or constraint.latest_time is not None:
        suggestions.append(BernieSlotSuggestion(
            kind="widen_time_window",
            summary="Remove the time-window filter to find more available slots.",
            params={"earliest_time": None, "latest_time": None},
            requires_confirmation=True,
        ))
    return suggestions


def _bernie_supervised_blocked(
    normalization: SlotSearchCommandResult,
    summary: str,
    blocks: list[AppointmentProposalIssue],
    search_proposal: Optional[SlotSearchProposalOut] = None,
    selection_proposal: Optional[SlotSelectionProposalOut] = None,
    warnings: Optional[list[AppointmentProposalIssue]] = None,
    identity_evidence: Optional[BernieIdentityEvidence] = None,
    practitioner_evidence: Optional[BerniePractitionerEvidence] = None,
    patient_evidence: Optional[BerniePatientEvidence] = None,
) -> BernieSupervisedBookingOut:
    effective_warnings = warnings or []
    return BernieSupervisedBookingOut(
        result="blocked",
        safe=False,
        requires_confirmation=True,
        autonomy_tier="blocked",
        summary=summary,
        normalization=normalization,
        search_proposal=search_proposal,
        selection_proposal=selection_proposal,
        staff_review=_bernie_staff_review_payload(
            result="blocked",
            summary=summary,
            warnings=effective_warnings,
            blocks=blocks,
            search_proposal=search_proposal,
            selection_proposal=selection_proposal,
            identity_evidence=identity_evidence,
            practitioner_evidence=practitioner_evidence,
            patient_evidence=patient_evidence,
        ),
        warnings=effective_warnings,
        blocks=blocks,
    )


def _bernie_clinic_day_exhausted(
    normalization: SlotSearchCommandResult,
    summary: str,
    warnings: Optional[list[AppointmentProposalIssue]] = None,
    search_proposal: Optional[SlotSearchProposalOut] = None,
    identity_evidence: Optional[BernieIdentityEvidence] = None,
    patient_evidence: Optional[BerniePatientEvidence] = None,
    request_reference_date: Optional[date_type] = None,
) -> BernieSupervisedBookingOut:
    """Return a clinic_day_exhausted response when no bookable slots remain today."""
    effective_warnings = warnings or []
    exhaustion_block = AppointmentProposalIssue(
        code="clinic_day_exhausted",
        severity="blocked",
        message=summary,
    )
    return BernieSupervisedBookingOut(
        result="clinic_day_exhausted",
        request_reference_date=request_reference_date,
        safe=False,
        requires_confirmation=False,
        autonomy_tier="blocked",
        summary=summary,
        normalization=normalization,
        search_proposal=search_proposal,
        staff_review=_bernie_staff_review_payload(
            result="clinic_day_exhausted",
            summary=summary,
            warnings=effective_warnings,
            blocks=[exhaustion_block],
            search_proposal=search_proposal,
            identity_evidence=identity_evidence,
            patient_evidence=patient_evidence,
        ),
        warnings=effective_warnings,
        blocks=[exhaustion_block],
    )


@router.post(
    "/proposals/bernie/supervised-booking",
    response_model=BernieSupervisedBookingOut,
)
def propose_bernie_supervised_booking(
    body: BernieSupervisedBookingIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Compose deterministic Bernie booking proposal steps without side effects.

    This wrapper is a typed intake/proposal surface for future Bernie UI/runtime
    callers. It normalizes a command, searches slots only when normalization is
    safe, and optionally converts a supervised selected candidate into existing
    create-proposal evidence. It never confirms, creates, audits, calls LLMs, or
    invokes provider integrations.
    """
    # Capture the immutable reference date once; echoed in every response branch.
    request_reference_date = body.reference_date

    normalization = normalize_slot_search_command(
        body.command,
        reference_date=body.reference_date,
    )
    normalized_patient_id = None
    if normalization.constraint is not None:
        normalized_patient_id = normalization.constraint.patient_id
    review_identity_evidence, _review_patient = _build_bernie_identity_evidence(
        body.patient_id or normalized_patient_id,
        body.patient_name_provisional,
        db,
        current_user.practice_id,
        body.context_frames,
    )
    review_patient_evidence = _build_bernie_patient_evidence(review_identity_evidence, _review_patient)
    if not normalization.safe or normalization.constraint is None:
        return _bernie_supervised_blocked(
            normalization=normalization,
            summary=normalization.summary,
            blocks=normalization.blocks,
            warnings=normalization.warnings,
            identity_evidence=review_identity_evidence,
            patient_evidence=review_patient_evidence,
        )

    # Schedule-aware clinic-day exhaustion checks.
    constraint = normalization.constraint
    practice_tz = _practice_zoneinfo(db, current_user.practice_id)
    clinic_now = _clinic_local_now(practice_tz)
    clinic_today = clinic_now.date()
    now_time = clinic_now.time().replace(second=0, microsecond=0)

    # ── Patient booking context (recognized-patient only) ────────────────────
    # Build once after normalization succeeds; attach to all subsequent returns.
    _sb_patient_ctx: Optional[BerniePatientBookingContext] = None
    _sb_context_freshness: Optional[BernieContextFreshness] = None
    if (
        review_identity_evidence.recognition_status == "recognized"
        and review_identity_evidence.patient_id is not None
    ):
        _sb_patient_ctx = build_patient_booking_context(
            db,
            current_user.practice_id,
            review_identity_evidence.patient_id,
            request_reference_date,
        )
        _sb_context_freshness = BernieContextFreshness(
            reference_date=request_reference_date,
            generated_at=_sb_patient_ctx.generated_at,
            stale=request_reference_date != clinic_today,
            basis=(
                "reference_date matches clinic-local today"
                if request_reference_date == clinic_today
                else "reference_date differs from clinic-local today; context may be stale"
            ),
        )
        if has_existing_booking_on_requested_day(
            _sb_patient_ctx,
            constraint.date_from,
        ):
            warnings_for_ctx = list(normalization.warnings)
            if not any(w.code == "existing_future_follow_up" for w in warnings_for_ctx):
                warnings_for_ctx.append(build_existing_future_follow_up_warning())
            normalization = normalization.model_copy(update={"warnings": warnings_for_ctx})

    def _with_ctx(out: BernieSupervisedBookingOut) -> BernieSupervisedBookingOut:
        """Attach patient booking context and freshness to any supervised-booking response."""
        if _sb_patient_ctx is None and _sb_context_freshness is None:
            return out
        return out.model_copy(update={
            "patient_booking_context": _sb_patient_ctx,
            "context_freshness": _sb_context_freshness,
        })

    # Before-search bounded-window pre-check: if the window's upper bound is entirely
    # in the past, short-circuit without running a slot query.
    if (
        constraint.date_from == clinic_today
        and constraint.latest_time is not None
        and constraint.latest_time <= now_time
    ):
        return _with_ctx(_bernie_clinic_day_exhausted(
            normalization=normalization,
            summary=(
                "That time window has already passed today - "
                "would you like a later time today or a different day?"
            ),
            warnings=normalization.warnings,
            identity_evidence=review_identity_evidence,
            patient_evidence=review_patient_evidence,
            request_reference_date=request_reference_date,
        ))

    # Open-ended same-day clamp: if earliest_time is in the past, clamp it to now
    # so the slot search only looks at remaining bookable slots (not past ones).
    if (
        constraint.date_from == clinic_today
        and constraint.earliest_time is not None
        and constraint.latest_time is None
        and constraint.earliest_time < now_time
    ):
        # Re-normalize with the clamped earliest_time so the constraint reflects reality.
        clamped_command_values = body.command.model_dump()
        clamped_command_values["earliest_time"] = now_time.strftime("%H:%M")
        clamped_command = SlotSearchCommandIn(**clamped_command_values)
        normalization = normalize_slot_search_command(
            clamped_command,
            reference_date=body.reference_date,
        )
        if normalization.safe and normalization.constraint is not None:
            constraint = normalization.constraint

    search_proposal = _build_slot_search_proposal(
        constraint,
        db,
        current_user.practice_id,
    )

    # Stamp deterministic freshness ids on every candidate so the confirm gate
    # can detect stale or cross-session evidence.  reference_date is immutable
    # across the session (body.reference_date = request_reference_date).
    _slot_practitioner_id = constraint.practitioner_id if normalization.constraint else None
    if search_proposal.candidates:
        stamped_candidates = [
            c.model_copy(update={
                "candidate_freshness_id": compute_candidate_freshness_id(
                    appointment_date=c.appointment_date,
                    start_time=c.start_time,
                    end_time=c.end_time,
                    start_time_local=c.start_time_local,
                    duration_minutes=c.duration_minutes,
                    practitioner_id=_slot_practitioner_id,
                    reference_date=request_reference_date,
                )
            })
            for c in search_proposal.candidates
        ]
        search_proposal = search_proposal.model_copy(update={"candidates": stamped_candidates})

    warnings = [*normalization.warnings, *search_proposal.warnings]
    blocks = [*normalization.blocks, *search_proposal.blocks]

    if not search_proposal.safe:
        return _with_ctx(_bernie_supervised_blocked(
            normalization=normalization,
            summary=f"{normalization.summary} {search_proposal.summary}",
            blocks=blocks,
            search_proposal=search_proposal,
            warnings=warnings,
            identity_evidence=review_identity_evidence,
            patient_evidence=review_patient_evidence,
        ))

    # Schedule-aware clinic-day exhaustion after open-ended slot search.
    # For open-ended same-day requests (earliest_time set, no latest_time), clamp-to-now
    # may leave zero bookable slots. Return clinic_day_exhausted instead of an empty
    # candidate_selection_required, so the UI prompts for a new day rather than an empty picker.
    if (
        constraint.date_from == clinic_today
        and constraint.earliest_time is not None
        and constraint.latest_time is None
        and len(search_proposal.candidates) == 0
    ):
        return _with_ctx(_bernie_clinic_day_exhausted(
            normalization=normalization,
            summary=(
                "No bookable slots remain today after that time - "
                "would you like to book for another day?"
            ),
            warnings=warnings,
            search_proposal=search_proposal,
            identity_evidence=review_identity_evidence,
            patient_evidence=review_patient_evidence,
            request_reference_date=request_reference_date,
        ))

    search_execution = SlotSearchCommandExecutionOut(
        safe=True,
        normalization=normalization,
        proposal=search_proposal,
        warnings=warnings,
        blocks=blocks,
        summary=f"{normalization.summary} {search_proposal.summary}",
    )
    has_selection = (
        body.selected_candidate_index is not None
        or body.selected_candidate is not None
    )
    if not has_selection:
        summary = (
            f"{search_execution.summary} Select one candidate before "
            "preparing create-proposal evidence."
        )
        # No-slot suggestions: when zero candidates but not clinic_day_exhausted
        no_slot_suggestions: list[BernieSlotSuggestion] = []
        if len(search_proposal.candidates) == 0 and normalization.constraint is not None:
            no_slot_suggestions = _build_no_slot_suggestions(normalization.constraint)
        _csr_turn_ref = _mint_next_turn_ref(body.turn_ref, "candidate_selection", request_reference_date)
        return _with_ctx(BernieSupervisedBookingOut(
            result="candidate_selection_required",
            request_reference_date=request_reference_date,
            safe=True,
            requires_confirmation=False,
            autonomy_tier="execute_with_report",
            summary=summary,
            normalization=normalization,
            search_proposal=search_proposal,
            staff_review=_bernie_staff_review_payload(
                result="candidate_selection_required",
                summary=summary,
                warnings=warnings,
                blocks=blocks,
                search_proposal=search_proposal,
                identity_evidence=review_identity_evidence,
                patient_evidence=review_patient_evidence,
            ),
            warnings=warnings,
            blocks=blocks,
            suggestions=no_slot_suggestions,
            turn_ref=_csr_turn_ref,
        ))

    if (
        body.patient_id is None
        and not body.patient_name_provisional
        and normalization.constraint.patient_id is None
    ):
        patient_block = _selection_block(
            "patient_identity_required",
            "patient_id or patient_name_provisional is required before preparing create-proposal evidence.",
        )
        return _with_ctx(_bernie_supervised_blocked(
            normalization=normalization,
            summary="Cannot prepare create proposal from selected slot. See blocked issues.",
            blocks=[*blocks, patient_block],
            search_proposal=search_proposal,
            warnings=warnings,
            identity_evidence=review_identity_evidence,
            patient_evidence=review_patient_evidence,
        ))

    selection_body = SlotSelectionProposalIn(
        search_execution=search_execution,
        selected_candidate_index=body.selected_candidate_index,
        selected_candidate=body.selected_candidate,
        practitioner_id=body.practitioner_id,
        appointment_type_id=body.appointment_type_id,
        location_id=body.location_id,
        patient_id=body.patient_id,
        patient_name_provisional=body.patient_name_provisional,
        reason=body.reason,
        notes=body.notes,
        booked_via=body.booked_via,
    )
    selection_blocks: list[AppointmentProposalIssue] = []
    selected_candidate = _resolve_selected_candidate(selection_body, selection_blocks)
    practitioner_id, appointment_type_id, location_id, patient_id = _resolve_selection_context(
        selection_body,
        selection_blocks,
    )

    if selected_candidate is None or selection_blocks:
        selection_proposal = _block_slot_selection(selection_blocks, selected_candidate)
        return _with_ctx(_bernie_supervised_blocked(
            normalization=normalization,
            summary=selection_proposal.summary,
            blocks=[*blocks, *selection_proposal.blocks],
            search_proposal=search_proposal,
            selection_proposal=selection_proposal,
            warnings=[*warnings, *selection_proposal.warnings],
            identity_evidence=review_identity_evidence,
            patient_evidence=review_patient_evidence,
        ))

    practitioner_evidence = _build_bernie_practitioner_evidence(
        practitioner_id,
        location_id,
        db,
        current_user.practice_id,
    )

    create_body = AppointmentCreate(
        patient_id=patient_id,
        patient_name_provisional=body.patient_name_provisional,
        practitioner_id=practitioner_id,
        appointment_type_id=appointment_type_id,
        location_id=location_id,
        appointment_date=selected_candidate.appointment_date,
        start_time_local=selected_candidate.start_time_local,
        duration_minutes=selected_candidate.duration_minutes,
        reason=body.reason,
        notes=body.notes,
        booked_via=body.booked_via,
    )
    create_proposal = _build_create_appointment_proposal(
        create_body,
        db,
        current_user.practice_id,
    )
    selection_proposal_warnings = [*selected_candidate.warnings, *create_proposal.warnings]
    selection_proposal_blocks = [*create_proposal.blocks]
    # Compute proposal freshness id from the create command coordinates.
    _cmd = create_proposal.command
    _proposal_fid = compute_proposal_freshness_id(
        appointment_date=_cmd.appointment_date,
        start_time=_cmd.start_time,
        start_time_local=_cmd.start_time_local,
        duration_minutes=_cmd.duration_minutes,
        practitioner_id=_cmd.practitioner_id,
        patient_id=_cmd.patient_id,
        appointment_type_id=_cmd.appointment_type_id,
        location_id=_cmd.location_id,
        reference_date=request_reference_date,
    )
    selection_proposal = SlotSelectionProposalOut(
        safe=create_proposal.safe,
        requires_confirmation=True,
        autonomy_tier="proposal" if create_proposal.safe else "blocked",
        summary=f"Prepared create proposal from selected slot. {create_proposal.summary}",
        selected_candidate=selected_candidate,
        create_proposal=create_proposal,
        warnings=selection_proposal_warnings,
        blocks=selection_proposal_blocks,
        proposal_freshness_id=_proposal_fid,
    )
    combined_warnings = [*warnings, *selection_proposal.warnings]
    combined_blocks = [*blocks, *selection_proposal.blocks]

    if not selection_proposal.safe:
        return _with_ctx(_bernie_supervised_blocked(
            normalization=normalization,
            summary=selection_proposal.summary,
            blocks=combined_blocks,
            search_proposal=search_proposal,
            selection_proposal=selection_proposal,
            warnings=combined_warnings,
            identity_evidence=review_identity_evidence,
            practitioner_evidence=practitioner_evidence,
            patient_evidence=review_patient_evidence,
        ))

    summary = (
        f"{search_execution.summary} {selection_proposal.summary} "
        "Submit selection_proposal to confirm-bernie only after explicit staff confirmation."
    )
    _sb_turn_ref = _mint_next_turn_ref(body.turn_ref, "proposal_preview", request_reference_date)
    return _with_ctx(BernieSupervisedBookingOut(
        result="confirmation_ready",
        request_reference_date=request_reference_date,
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary=summary,
        normalization=normalization,
        search_proposal=search_proposal,
        selection_proposal=selection_proposal,
        staff_review=_bernie_staff_review_payload(
            result="confirmation_ready",
            summary=summary,
            warnings=combined_warnings,
            blocks=combined_blocks,
            search_proposal=search_proposal,
            selection_proposal=selection_proposal,
            identity_evidence=review_identity_evidence,
            practitioner_evidence=practitioner_evidence,
            patient_evidence=review_patient_evidence,
        ),
        warnings=combined_warnings,
        blocks=combined_blocks,
        turn_ref=_sb_turn_ref,
    ))


def _confirm_create_block(code: str, message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(
        code=code,
        severity="blocked",
        message=message,
    )


def _block_bernie_create_confirmation(
    blocks: list[AppointmentProposalIssue],
    warnings: Optional[list[AppointmentProposalIssue]] = None,
    audit_evidence: Optional[list[str]] = None,
) -> AppointmentConfirmCreateProposalOut:
    return AppointmentConfirmCreateProposalOut(
        safe=False,
        requires_confirmation=True,
        autonomy_tier="blocked",
        summary="Cannot confirm Bernie create proposal. See blocked issues.",
        appointment=None,
        warnings=warnings or [],
        blocks=blocks,
        audit_evidence=audit_evidence or [],
    )


def _same_create_command(
    left: AppointmentCreateCommand,
    right: AppointmentCreateCommand,
) -> bool:
    return left.model_dump() == right.model_dump()


def _create_body_from_command(command: AppointmentCreateCommand) -> AppointmentCreate:
    return AppointmentCreate(
        patient_id=command.patient_id,
        patient_name_provisional=command.patient_name_provisional,
        practitioner_id=command.practitioner_id,
        appointment_type_id=command.appointment_type_id,
        location_id=command.location_id,
        appointment_date=command.appointment_date,
        start_time_local=command.start_time_local,
        duration_minutes=command.duration_minutes,
        reason=command.reason,
        notes=command.notes,
        booked_via=command.booked_via,
    )


def _create_command_matches_selected_candidate(
    command: AppointmentCreateCommand,
    selected_candidate: SlotCandidate,
) -> bool:
    return (
        command.appointment_date == selected_candidate.appointment_date
        and command.start_time_local == selected_candidate.start_time_local
        and command.duration_minutes == selected_candidate.duration_minutes
        and command.start_time == selected_candidate.start_time
    )


@router.post(
    "/proposals/create/confirm-bernie",
    response_model=AppointmentConfirmCreateProposalOut,
)
def confirm_bernie_create_proposal(
    body: BernieCreateProposalConfirmationIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Explicitly confirm supervised Bernie create-proposal evidence.

    This is the first Bernie slot flow endpoint that writes an appointment. The
    caller must send an already-supervised slot-selection/create-proposal result
    plus explicit confirmation. The route revalidates the create command against
    current practice/auth/conflict state before writing exactly one appointment
    and one bounded audit evidence trail.
    """
    audit_evidence = list(_BERNIE_CONFIRM_CREATE_BASE_EVIDENCE)
    blocks: list[AppointmentProposalIssue] = []
    selection = body.selection_proposal
    create_proposal = selection.create_proposal

    if body.confirmed is not True:
        blocks.append(_confirm_create_block(
            "explicit_confirmation_required",
            "confirmed=true is required before creating an appointment.",
        ))

    if selection.intent != "select_slot_for_create_proposal":
        blocks.append(_confirm_create_block(
            "invalid_selection_source",
            "The supplied evidence is not a slot-selection create proposal.",
        ))
    if not selection.safe or selection.autonomy_tier != "proposal":
        blocks.append(_confirm_create_block(
            "slot_selection_not_safe",
            "The slot-selection proposal is not safe to confirm.",
        ))
    if selection.selected_candidate is None:
        blocks.append(_confirm_create_block(
            "selected_candidate_required",
            "The slot-selection evidence must include the selected candidate.",
        ))
    if create_proposal is None:
        blocks.append(_confirm_create_block(
            "create_proposal_required",
            "The slot-selection evidence must include a create proposal.",
        ))
    elif (
        not create_proposal.safe
        or create_proposal.autonomy_tier != "proposal"
        or not create_proposal.requires_confirmation
    ):
        blocks.append(_confirm_create_block(
            "create_proposal_not_safe",
            "The create proposal is not safe to confirm.",
        ))

    if create_proposal is not None and selection.selected_candidate is not None:
        if not _create_command_matches_selected_candidate(
            create_proposal.command,
            selection.selected_candidate,
        ):
            blocks.append(_confirm_create_block(
                "selection_create_proposal_mismatch",
                "The create proposal command no longer matches the selected slot evidence.",
            ))

    # ── Staleness gate (fail-closed) ────────────────────────────────────────
    # Only fires when the client explicitly echoes freshness ids or a turn_ref
    # (backward-compat: omitting these fields is tolerated for Sprint 104 clients).
    if body.turn_ref is not None or body.candidate_freshness_id is not None or body.proposal_freshness_id is not None:
        _confirm_reference_date = body.turn_ref.reference_date if body.turn_ref is not None else None

        # Check candidate freshness.
        if body.candidate_freshness_id is not None and selection.selected_candidate is not None:
            _expected_cand_fid = compute_candidate_freshness_id(
                appointment_date=selection.selected_candidate.appointment_date,
                start_time=selection.selected_candidate.start_time,
                end_time=selection.selected_candidate.end_time,
                start_time_local=selection.selected_candidate.start_time_local,
                duration_minutes=selection.selected_candidate.duration_minutes,
                practitioner_id=create_proposal.command.practitioner_id if create_proposal else None,
                reference_date=_confirm_reference_date or selection.selected_candidate.appointment_date,
            )
            _cand_staleness = check_staleness(
                submitted_freshness_id=body.candidate_freshness_id,
                expected_freshness_id=_expected_cand_fid,
                submitted_reference_date=_confirm_reference_date,
                session_reference_date=_confirm_reference_date or selection.selected_candidate.appointment_date,
            )
            if _cand_staleness.verdict == StalenessVerdict.mismatched_reference_date:
                blocks.append(_confirm_create_block(
                    "stale_candidate_reference_date_mismatch",
                    f"Confirmation blocked: {_cand_staleness.detail}",
                ))
            elif _cand_staleness.verdict == StalenessVerdict.stale:
                blocks.append(_confirm_create_block(
                    "stale_candidate_freshness_id",
                    "Confirmation blocked: candidate freshness id does not match current session evidence.",
                ))

        # Check proposal freshness.
        if body.proposal_freshness_id is not None and create_proposal is not None:
            _cmd = create_proposal.command
            _confirm_ref_date_for_proposal = _confirm_reference_date or _cmd.appointment_date
            _expected_prop_fid = compute_proposal_freshness_id(
                appointment_date=_cmd.appointment_date,
                start_time=_cmd.start_time,
                start_time_local=_cmd.start_time_local,
                duration_minutes=_cmd.duration_minutes,
                practitioner_id=_cmd.practitioner_id,
                patient_id=_cmd.patient_id,
                appointment_type_id=_cmd.appointment_type_id,
                location_id=_cmd.location_id,
                reference_date=_confirm_ref_date_for_proposal,
            )
            _prop_staleness = check_staleness(
                submitted_freshness_id=body.proposal_freshness_id,
                expected_freshness_id=_expected_prop_fid,
                submitted_reference_date=_confirm_reference_date,
                session_reference_date=_confirm_ref_date_for_proposal,
            )
            if _prop_staleness.verdict == StalenessVerdict.mismatched_reference_date:
                blocks.append(_confirm_create_block(
                    "stale_proposal_reference_date_mismatch",
                    f"Confirmation blocked: {_prop_staleness.detail}",
                ))
            elif _prop_staleness.verdict == StalenessVerdict.stale:
                blocks.append(_confirm_create_block(
                    "stale_proposal_freshness_id",
                    "Confirmation blocked: proposal freshness id does not match current session evidence.",
                ))

    if blocks:
        return _block_bernie_create_confirmation(
            blocks,
            warnings=selection.warnings,
            audit_evidence=audit_evidence,
        )

    entity_blocks = _check_create_command_entities(
        create_proposal.command,
        current_user.practice_id,
        db,
    )
    if entity_blocks:
        return _block_bernie_create_confirmation(
            entity_blocks,
            warnings=selection.warnings,
            audit_evidence=audit_evidence,
        )

    create_body = _create_body_from_command(create_proposal.command)
    revalidated = _build_create_appointment_proposal(
        create_body,
        db,
        current_user.practice_id,
    )
    if (
        not revalidated.safe
        or revalidated.autonomy_tier != "proposal"
        or not revalidated.requires_confirmation
    ):
        return _block_bernie_create_confirmation(
            [
                _confirm_create_block(
                    "create_proposal_revalidation_blocked",
                    "The create proposal is no longer safe to confirm.",
                ),
                *revalidated.blocks,
            ],
            warnings=[*selection.warnings, *revalidated.warnings],
            audit_evidence=audit_evidence,
        )

    if not _same_create_command(create_proposal.command, revalidated.command):
        return _block_bernie_create_confirmation(
            [_confirm_create_block(
                "create_proposal_revalidation_mismatch",
                "The revalidated create command does not match the supplied proposal evidence.",
            )],
            warnings=[*selection.warnings, *revalidated.warnings],
            audit_evidence=audit_evidence,
        )

    if create_body.patient_id is not None:
        _identity_evidence, _ = _build_bernie_identity_evidence(
            create_body.patient_id,
            None,
            db,
            current_user.practice_id,
        )
        confidence_code = BERNIE_IDENTITY_CONFIDENCE_AUDIT_CODES.get(_identity_evidence.confidence)
        if confidence_code and confidence_code not in audit_evidence:
            audit_evidence.append(confidence_code)

    confirmed_warnings = [
        *[issue.code for issue in selection.warnings],
        *[issue.code for issue in revalidated.warnings],
        *body.confirmed_warnings,
    ]
    appointment = _create_appointment_from_body(
        create_body,
        db,
        current_user,
        confirmed_warnings=confirmed_warnings,
        audit_evidence=audit_evidence,
    )
    return AppointmentConfirmCreateProposalOut(
        safe=True,
        requires_confirmation=False,
        autonomy_tier="confirmed_write",
        summary="Confirmed supervised Bernie create proposal and created one appointment.",
        appointment=appointment,
        warnings=[*selection.warnings, *revalidated.warnings],
        blocks=[],
        audit_evidence=audit_evidence,
    )


@router.post(
    "/proposals/bernie/no-slot-suggestion-selection",
    response_model=BernieNoSlotSuggestionSelectionOut,
)
def select_no_slot_suggestion(
    body: BernieNoSlotSuggestionSelectionIn,
    current_user: User = Depends(require_role(*MUTATING_APPOINTMENT_ROLES)),
):
    """Handle staff selection of a no-slot suggestion from a prior Bernie turn.

    Non-mutating.  Validates that the suggestion came from a turn in the same
    session (via turn_ref) and returns a pre-populated supervised-booking request
    carrying the suggestion's adjusted params.  The caller must submit that
    request to /proposals/bernie/supervised-booking to search for actual slots.
    """
    incoming_turn = body.turn_ref
    suggestion = body.suggestion

    # Build the next supervised-booking request from the suggestion params.
    orig = body.original_request
    adjusted_command_values = orig.command.model_dump()
    if suggestion.params:
        adjusted_command_values.update({
            k: v for k, v in suggestion.params.items()
            if k in adjusted_command_values
        })
    adjusted_command = SlotSearchCommandIn(**adjusted_command_values)

    next_request = BernieSupervisedBookingIn(
        command=adjusted_command,
        reference_date=orig.reference_date,
        context_frames=orig.context_frames,
        patient_id=orig.patient_id,
        patient_name_provisional=orig.patient_name_provisional,
        practitioner_id=orig.practitioner_id,
        appointment_type_id=orig.appointment_type_id,
        location_id=orig.location_id,
        reason=orig.reason,
        notes=orig.notes,
        booked_via=orig.booked_via,
        turn_ref=incoming_turn,
    )

    next_turn_ref = _mint_next_turn_ref(
        incoming_turn,
        "no_slot_suggestion_selection",
        incoming_turn.reference_date,
    )

    return BernieNoSlotSuggestionSelectionOut(
        accepted=True,
        turn_ref=next_turn_ref,
        next_request=next_request,
        summary=(
            f"Accepted suggestion '{suggestion.kind}'. "
            "Submit next_request to /proposals/bernie/supervised-booking."
        ),
        warnings=[],
        blocks=[],
    )
