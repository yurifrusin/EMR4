import uuid
from datetime import datetime, date, time
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.models.appointments import AppointmentStatus, BookingChannel, AppointmentAuditAction
from app.services.diary.confirm_gate import ConfirmAffordanceDecision


STATUS_REASON_CODES = frozenset({
    "PATIENT_CANCELLED",
    "PATIENT_RESCHEDULED",
    "PATIENT_UNWELL",
    "PATIENT_TRANSPORT",
    "PRACTITIONER_UNAVAILABLE",
    "CLINIC_OPERATIONAL",
    "CLINIC_RESCHEDULED",
    "ADMIN_ERROR",
    "DUPLICATE_BOOKING",
    "DID_NOT_ATTEND",
    "LEFT_WITHOUT_SEEN",
    "OTHER",
    "LEGACY_UNCLASSIFIED",
})


def validate_status_reason_code(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if value not in STATUS_REASON_CODES:
        raise ValueError("status_reason_code must be one of the configured appointment reason codes")
    return value


# Status-specific reason-code policy: single source of truth for which reason
# codes are valid for each terminal appointment status. This mirrors the
# frontend's STATUS_SPECIFIC_REASON_CODE_OPTIONS in docs/diary/diary.js.
# A frontend-drift detection test validates that the JS constants match here.
STATUS_SPECIFIC_REASON_CODE_POLICY: dict[AppointmentStatus, frozenset[str]] = {
    AppointmentStatus.Cancelled: frozenset({
        "PATIENT_CANCELLED",
        "PATIENT_RESCHEDULED",
        "PATIENT_UNWELL",
        "PATIENT_TRANSPORT",
        "PRACTITIONER_UNAVAILABLE",
        "CLINIC_OPERATIONAL",
        "CLINIC_RESCHEDULED",
        "ADMIN_ERROR",
        "DUPLICATE_BOOKING",
        "OTHER",
    }),
    AppointmentStatus.DNA: frozenset({
        "DID_NOT_ATTEND",
        "LEFT_WITHOUT_SEEN",
        "ADMIN_ERROR",
        "DUPLICATE_BOOKING",
        "OTHER",
    }),
    AppointmentStatus.NoShow: frozenset({
        "DID_NOT_ATTEND",
        "LEFT_WITHOUT_SEEN",
        "ADMIN_ERROR",
        "DUPLICATE_BOOKING",
        "OTHER",
    }),
}


def validate_status_reason_code_for_status(
    status: AppointmentStatus,
    code: Optional[str],
) -> Optional[str]:
    """Validate status_reason_code against the status-specific policy.

    Returns the code (or None) on success, raises ValueError on mismatch.
    Non-terminal statuses and statuses without a policy entry are not
    restricted (pass-through, matching existing behaviour).
    """
    if code is None:
        return None
    allowed = STATUS_SPECIFIC_REASON_CODE_POLICY.get(status)
    if allowed is not None and code not in allowed:
        raise ValueError(
            f"status_reason_code '{code}' is not valid for status '{status.value}'"
        )
    return code


# ── Bernie typed turn contract ────────────────────────────────────────────────

BernieTurnEventKind = Literal[
    "staff_instruction",
    "bernie_clarification",
    "no_slot_suggestion_selection",
    "candidate_selection",
    "proposal_preview",
    "confirmation",
]


class BernieTurnRef(BaseModel):
    """Typed turn identity for a Bernie session step.

    session_id is minted by the server on the first interpret call and must be
    echoed unchanged by the client on every subsequent turn in the same session.
    turn_id is minted per server response and is unique within a session.
    turn_index is a monotonically increasing integer (0-based, minted by server).
    reference_date is the immutable clinic-local date captured at session start
    and echoed on every turn; the server rejects turns that supply a different
    reference_date than the one established on turn-0.
    """
    session_id: str
    turn_id: str
    turn_index: int = Field(ge=0)
    event_kind: BernieTurnEventKind
    reference_date: date


class AppointmentTypeOut(BaseModel):
    id: uuid.UUID
    name: str
    default_duration: int
    color_hex: Optional[str] = None
    is_bookable_online: bool

    model_config = {"from_attributes": True}


class PatientBrief(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    medicare_number: Optional[str] = None
    phone_mobile: Optional[str] = None

    model_config = {"from_attributes": True}


class PractitionerBrief(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    provider_number: Optional[str] = None
    ahpra_number: Optional[str] = None

    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    practitioner_id: uuid.UUID
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    appointment_date: Optional[date] = None
    start_time_local: Optional[time] = None
    duration_minutes: int = Field(default=15, gt=0, le=480)
    reason: Optional[str] = None
    notes: Optional[str] = None
    booked_via: BookingChannel = BookingChannel.Receptionist
    confirmed_warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_patient_identity_and_time(self):
        if self.patient_id is None and not self.patient_name_provisional:
            raise ValueError(
                "patient_id or patient_name_provisional is required"
            )
        has_local_pair = self.appointment_date is not None and self.start_time_local is not None
        has_partial_local_pair = (self.appointment_date is None) != (self.start_time_local is None)
        if has_partial_local_pair:
            raise ValueError("appointment_date and start_time_local must be supplied together")
        if self.start_time is None and not has_local_pair:
            raise ValueError("start_time or appointment_date + start_time_local is required")
        return self


class AppointmentUpdate(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    practitioner_id: Optional[uuid.UUID] = None
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    appointment_date: Optional[date] = None
    start_time_local: Optional[time] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0, le=480)
    reason: Optional[str] = None
    notes: Optional[str] = None
    waiting_room: Optional[str] = None
    waiting_area_id: Optional[uuid.UUID] = None
    queue_position: Optional[int] = None
    confirmed_warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_partial_local_pair(self):
        has_partial = (self.appointment_date is None) != (self.start_time_local is None)
        if has_partial:
            raise ValueError("appointment_date and start_time_local must be supplied together")
        return self


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
    waiting_area_id: Optional[uuid.UUID] = None
    status_reason_code: Optional[str] = Field(default=None, max_length=50)
    confirmed_warnings: list[str] = Field(default_factory=list)

    @field_validator("status_reason_code")
    @classmethod
    def validate_reason_code(cls, value: Optional[str]) -> Optional[str]:
        return validate_status_reason_code(value)

    @model_validator(mode="after")
    def validate_reason_code_for_status(self) -> "AppointmentStatusUpdate":
        validate_status_reason_code_for_status(self.status, self.status_reason_code)
        return self

class AppointmentOut(BaseModel):
    id: uuid.UUID
    practice_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    practitioner_id: uuid.UUID
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    start_time: datetime
    appointment_date: date
    start_time_local: time
    end_time: datetime
    duration_minutes: int
    status: AppointmentStatus
    reason: Optional[str] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    status_reason_code: Optional[str] = None
    booked_via: BookingChannel
    waiting_room: Optional[str] = None
    waiting_area_id: Optional[uuid.UUID] = None
    queue_position: Optional[int] = None
    created_at: datetime
    patient: Optional[PatientBrief] = None
    practitioner: PractitionerBrief
    appointment_type: Optional[AppointmentTypeOut] = None
    breaks_overlap: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class AppointmentCheckinDefaults(BaseModel):
    suggested_waiting_area_id: Optional[uuid.UUID] = None
    room_name: Optional[str] = None


class AppointmentConflictBrief(BaseModel):
    appointment_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    start_time_local: time
    duration_minutes: int
    status: AppointmentStatus
    patient_name: Optional[str] = None


class AppointmentProposalIssue(BaseModel):
    code: str
    severity: Literal["warning", "blocked"]
    message: str


class AppointmentCreateCommand(BaseModel):
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    practitioner_id: uuid.UUID
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    appointment_date: date
    start_time_local: time
    start_time: datetime
    duration_minutes: int
    reason: Optional[str] = None
    notes: Optional[str] = None
    booked_via: BookingChannel = BookingChannel.Receptionist


class AppointmentCreateProposalOut(BaseModel):
    intent: Literal["create_appointment"] = "create_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    command: AppointmentCreateCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    conflict: Optional[AppointmentConflictBrief] = None
    breaks_overlap: list[str] = Field(default_factory=list)
    patient_identity: Literal["linked", "provisional"]
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    create_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentCreateProposalConfirmationIn(BaseModel):
    """Explicit staff confirmation for a backend-prepared human create proposal."""
    confirmed: bool = False
    create_proposal: AppointmentCreateProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
    create_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class ConfirmationReceiptVerification(BaseModel):
    """Deterministic verification flags for a confirmation receipt.

    All fields are derived from the confirmation flow that the server actually
    performed — never from client input.  visual_diary_check_required is always
    false by contract for this accessible booking path.
    """
    actor_authenticated: bool
    practice_scope_verified: bool
    proposal_revalidated: bool
    conflict_check_passed: bool
    idempotency_verified: bool
    audit_recorded: bool
    signed_evidence_verified: bool
    visual_diary_check_required: Literal[False]


class ConfirmationReceipt(BaseModel):
    """Typed appointment confirmation receipt (appointment.confirmation_receipt.v1).

    Additive response object carried on successful appointment-create confirmations.
    Blocked responses never include a receipt.  Idempotent replay returns the
    stored receipt without another write.
    """
    schema_version: Literal["appointment.confirmation_receipt.v1"] = (
        "appointment.confirmation_receipt.v1"
    )
    outcome: Literal["appointment_created"] = "appointment_created"
    appointment_id: uuid.UUID
    patient_display: str
    practitioner_display: str
    appointment_date: date
    start_time_local: time
    duration_minutes: int
    status: AppointmentStatus
    appointment_type: Optional[str] = None
    confirmed_by_display: str
    confirmed_by_role: Optional[str] = None
    correlation_id: Optional[uuid.UUID] = None
    audit_event_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    verification: ConfirmationReceiptVerification


class AppointmentConfirmCreateProposalOut(BaseModel):
    intent: Literal["confirm_create_appointment"] = "confirm_create_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["confirmed_write", "blocked"]
    summary: str
    appointment: Optional[AppointmentOut] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    audit_evidence: list[str] = Field(default_factory=list)
    confirmation_receipt: Optional[ConfirmationReceipt] = None


class AppointmentUpdateProposalIn(BaseModel):
    """All fields optional — unset fields keep the appointment's current values."""
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    practitioner_id: Optional[uuid.UUID] = None
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    appointment_date: Optional[date] = None
    start_time_local: Optional[time] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0, le=480)
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentUpdateCommand(BaseModel):
    appointment_id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    practitioner_id: uuid.UUID
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    appointment_date: date
    start_time_local: time
    start_time: datetime
    duration_minutes: int
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentUpdateProposalOut(BaseModel):
    intent: Literal["update_appointment"] = "update_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    command: AppointmentUpdateCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    conflict: Optional[AppointmentConflictBrief] = None
    breaks_overlap: list[str] = Field(default_factory=list)
    patient_identity: Literal["linked", "provisional"]
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    update_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class BernieUpdateProposalConfirmationIn(BaseModel):
    """Explicit staff confirmation for backend-prepared Bernie update evidence."""
    confirmed: bool = False
    update_proposal: AppointmentUpdateProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
    turn_ref: Optional["BernieTurnRef"] = None
    update_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False
    session_binding: Optional[dict[str, Any]] = None


class AppointmentConfirmUpdateProposalOut(BaseModel):
    intent: Literal["confirm_update_appointment"] = "confirm_update_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["confirmed_write", "blocked"]
    summary: str
    appointment: Optional[AppointmentOut] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    audit_evidence: list[str] = Field(default_factory=list)


class BernieToolIntentIn(BaseModel):
    """Raw Bernie reception-tool intake for non-booking diary actions.

    This is intentionally a non-mutating proposal surface. Tool intents may
    resolve to existing deterministic proposal contracts, but they never write
    appointment state directly.
    """
    instruction: str = Field(min_length=1, max_length=1000)
    reference_date: Optional[date] = None
    context_frames: list[dict[str, Any]] = Field(default_factory=list)


class BernieToolIntentOut(BaseModel):
    """Typed, non-mutating Bernie tool-intent response."""
    intent: Literal["bernie_tool_intent"] = "bernie_tool_intent"
    safe: bool
    result: Literal["proposal_ready", "clarification_required", "blocked", "unsupported"]
    tool_intent: Optional[Literal["extend_appointment"]] = None
    autonomy_tier: Literal["proposal", "blocked", "execute_with_report"]
    requires_confirmation: bool
    summary: str
    proposal: Optional[AppointmentUpdateProposalOut] = None
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    update_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    source_attribution: dict[str, Any] = Field(default_factory=dict)


class AppointmentStatusProposalIn(BaseModel):
    status: AppointmentStatus
    waiting_area_id: Optional[uuid.UUID] = None
    status_reason_code: Optional[str] = Field(default=None, max_length=50)

    @field_validator("status_reason_code")
    @classmethod
    def validate_reason_code(cls, value: Optional[str]) -> Optional[str]:
        return validate_status_reason_code(value)

    @model_validator(mode="after")
    def validate_reason_code_for_status(self) -> "AppointmentStatusProposalIn":
        validate_status_reason_code_for_status(self.status, self.status_reason_code)
        return self

class AppointmentStatusCommand(BaseModel):
    appointment_id: uuid.UUID
    status: AppointmentStatus
    waiting_area_id: Optional[uuid.UUID] = None
    waiting_area_id_supplied: bool = False
    clears_waiting_area: bool
    status_reason_code: Optional[str] = Field(default=None, max_length=50)

    @field_validator("status_reason_code")
    @classmethod
    def validate_reason_code(cls, value: Optional[str]) -> Optional[str]:
        return validate_status_reason_code(value)

    @model_validator(mode="after")
    def validate_reason_code_for_status(self) -> "AppointmentStatusCommand":
        validate_status_reason_code_for_status(self.status, self.status_reason_code)
        return self

class AppointmentStatusProposalOut(BaseModel):
    intent: Literal["update_appointment_status"] = "update_appointment_status"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    command: AppointmentStatusCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    status_proposal_freshness_id: Optional[str] = None
    status_proposal_version_binding: Optional[dict[str, Any]] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentWaitingAreaProposalIn(BaseModel):
    waiting_area_id: Optional[uuid.UUID] = None


class AppointmentWaitingAreaCommand(BaseModel):
    appointment_id: uuid.UUID
    waiting_area_id: Optional[uuid.UUID] = None
    waiting_area_id_supplied: bool = True
    clears_waiting_area: bool


class AppointmentWaitingAreaProposalOut(BaseModel):
    intent: Literal["update_appointment_waiting_area"] = "update_appointment_waiting_area"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    command: AppointmentWaitingAreaCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    status_proposal_freshness_id: Optional[str] = None
    status_proposal_version_binding: Optional[dict[str, Any]] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentStatusProposalConfirmationIn(BaseModel):
    confirmed: bool = False
    status_proposal: AppointmentStatusProposalOut | AppointmentWaitingAreaProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
    status_proposal_freshness_id: Optional[str] = None
    status_proposal_version_binding: dict[str, Any]
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentConfirmStatusProposalOut(BaseModel):
    intent: Literal["confirm_status_appointment"] = "confirm_status_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["confirmed_write", "blocked"]
    summary: str
    appointment: Optional[AppointmentOut] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    audit_evidence: list[str] = Field(default_factory=list)


class AppointmentCheckInProposalIn(BaseModel):
    """A5.1 dedicated check-in proposal input.

    waiting_area_id may assign only when no waiting area is currently set;
    omitted/null preserves an existing area and never removes or moves it.
    """

    waiting_area_id: Optional[uuid.UUID] = None


class AppointmentCheckInCommand(BaseModel):
    appointment_id: uuid.UUID
    waiting_area_id: Optional[uuid.UUID] = None
    waiting_area_id_supplied: bool = False


class AppointmentCheckInProposalOut(BaseModel):
    intent: Literal["check_in_appointment"] = "check_in_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    command: AppointmentCheckInCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    check_in_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[str] = None
    signed_confirmation_evidence_required: bool = False
    evidence_expires_at: Optional[datetime] = None


class AppointmentCheckInProposalConfirmationIn(BaseModel):
    confirmed: bool = False
    check_in_proposal: AppointmentCheckInProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
    check_in_proposal_freshness_id: Optional[str] = None
    signed_confirmation_evidence: Optional[str] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentCheckInReceipt(BaseModel):
    """Bounded, patient-free A5.1 confirmation receipt serialization."""

    schema_version: Literal["appointment.check_in_receipt.v1"] = (
        "appointment.check_in_receipt.v1"
    )
    appointment_id: uuid.UUID
    status: AppointmentStatus
    waiting_area_id: Optional[uuid.UUID] = None
    audit_log_id: uuid.UUID
    event_id: uuid.UUID
    command_id: uuid.UUID
    commit_time: datetime


class AppointmentConfirmCheckInProposalOut(BaseModel):
    intent: Literal["confirm_check_in_appointment"] = "confirm_check_in_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["confirmed_write", "blocked"]
    summary: str
    receipt: Optional[AppointmentCheckInReceipt] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    audit_evidence: list[str] = Field(default_factory=list)


class AppointmentDeleteIn(BaseModel):
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    status_reason_code: Optional[str] = Field(default=None, max_length=50)
    confirmed_warnings: list[str] = Field(default_factory=list)

    @field_validator("status_reason_code")
    @classmethod
    def validate_reason_code(cls, value: Optional[str]) -> Optional[str]:
        return validate_status_reason_code(value)


class AppointmentDeleteCommand(BaseModel):
    appointment_id: uuid.UUID
    clears_waiting_area: bool
    cancellation_reason: Optional[str] = None
    status_reason_code: Optional[str] = Field(default=None, max_length=50)

    @field_validator("status_reason_code")
    @classmethod
    def validate_reason_code(cls, value: Optional[str]) -> Optional[str]:
        return validate_status_reason_code(value)

    @model_validator(mode="after")
    def validate_reason_code_for_status(self) -> "AppointmentDeleteCommand":
        # Delete always implies Cancelled; validate against Cancelled policy.
        validate_status_reason_code_for_status(AppointmentStatus.Cancelled, self.status_reason_code)
        return self

class AppointmentDeleteProposalOut(BaseModel):
    intent: Literal["delete_appointment"] = "delete_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["proposal", "blocked"]
    summary: str
    command: AppointmentDeleteCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    delete_proposal_freshness_id: Optional[str] = None
    delete_proposal_version_binding: Optional[dict[str, Any]] = None
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentDeleteProposalConfirmationIn(BaseModel):
    confirmed: bool = False
    delete_proposal: AppointmentDeleteProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
    delete_proposal_freshness_id: Optional[str] = None
    delete_proposal_version_binding: dict[str, Any]
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False


class AppointmentDeleteConfirmationReceipt(BaseModel):
    schema_version: Literal[
        "appointment.delete_confirmation_receipt.v1"
    ] = "appointment.delete_confirmation_receipt.v1"
    appointment_id: uuid.UUID
    status: Literal["Cancelled"] = "Cancelled"
    status_reason_code: Optional[str] = None
    cancellation_reason: Optional[str] = None
    waiting_area_id: Optional[uuid.UUID] = None
    warning_codes: list[str] = Field(default_factory=list)


class AppointmentConfirmDeleteProposalOut(BaseModel):
    """Versioned minimal public delete-confirm envelope.

    Success delivery and replay share this exact patient-free receipt envelope.
    It never exposes an ``appointment`` read model, patient, practitioner,
    schedule, notes, mutable identity or unknown extra field.
    """

    model_config = {"extra": "forbid"}

    schema_version: Literal[
        "raisa.delete_confirm_public_envelope.v1"
    ] = "raisa.delete_confirm_public_envelope.v1"
    intent: Literal["confirm_delete_appointment"] = "confirm_delete_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["confirmed_write", "blocked"]
    summary: str
    receipt: Optional[AppointmentDeleteConfirmationReceipt] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    audit_evidence: list[str] = Field(default_factory=list)


class AppointmentAuditLogOut(BaseModel):
    id: uuid.UUID
    appointment_id: uuid.UUID
    practice_id: uuid.UUID
    confirmed_by_user_id: uuid.UUID
    confirmed_by_display: str
    confirmed_by_role: Optional[str] = None
    action: AppointmentAuditAction
    status_before: Optional[AppointmentStatus] = None
    status_after: Optional[AppointmentStatus] = None
    cancellation_reason: Optional[str] = None
    status_reason_code: Optional[str] = None
    confirmed_warnings: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class ScheduleSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    available: bool


class PractitionerScheduleOut(BaseModel):
    id: uuid.UUID
    practitioner_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int

    model_config = {"from_attributes": True}


# ── Bernie slot-search proposal ───────────────────────────────────────────────

class SlotSearchProposalIn(BaseModel):
    practitioner_id: uuid.UUID
    date_from: date
    date_to: Optional[date] = None
    duration_minutes: Optional[int] = Field(default=None, gt=0, le=480)
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    earliest_time: Optional[time] = None
    latest_time: Optional[time] = None
    temporal_relation: Optional[str] = None
    patient_id: Optional[uuid.UUID] = None
    limit: int = Field(default=20, gt=0, le=100)

    @model_validator(mode="after")
    def validate_date_range(self):
        effective_to = self.date_to if self.date_to is not None else self.date_from
        if effective_to < self.date_from:
            raise ValueError("date_to must not be before date_from")
        delta = (effective_to - self.date_from).days
        if delta > 13:
            raise ValueError("date range must not exceed 14 days")
        return self


class SlotCandidate(BaseModel):
    appointment_date: date
    start_time: datetime
    end_time: datetime
    start_time_local: time
    duration_minutes: int
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    # Deterministic freshness id stamped by the server on candidate issuance.
    # Clients echo it back in the confirmation body; the server recomputes and
    # compares to detect stale or tampered candidates.  Optional for backward compat.
    candidate_freshness_id: Optional[str] = None


class SlotSearchProposalOut(BaseModel):
    intent: Literal["search_slots"] = "search_slots"
    safe: bool
    requires_confirmation: bool = False
    autonomy_tier: Literal["execute_with_report", "blocked"]
    summary: str
    resolved_duration_minutes: Optional[int] = None
    candidates: list[SlotCandidate] = Field(default_factory=list)
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)


# ── Bernie slot-search command normalizer ─────────────────────────────────────

class SlotSearchCommandIn(BaseModel):
    """Permissive input for a Bernie/LLM slot-search command.

    All fields accept raw strings, native Python types, or None.
    Unknown keys from LLM output are silently ignored.
    The normalizer (bernie_slot_normalizer.normalize_slot_search_command)
    validates and coerces these into a SlotSearchProposalIn constraint.

    temporal_relation is an optional string indicating the temporal nature
    of the slot request: 'exact', 'not_before', 'not_after', 'interval',
    'approximate', or 'unspecified'.
    """
    model_config = ConfigDict(extra="ignore")

    practitioner_id: Optional[Any] = None
    date_from: Optional[Any] = None
    date_to: Optional[Any] = None
    duration_minutes: Optional[Any] = None
    appointment_type_id: Optional[Any] = None
    location_id: Optional[Any] = None
    earliest_time: Optional[Any] = None
    latest_time: Optional[Any] = None
    temporal_relation: Optional[str] = None
    patient_id: Optional[Any] = None
    limit: Optional[Any] = None


class SlotSearchCommandResult(BaseModel):
    """Result of deterministic Bernie slot-search command normalization.

    safe=True means constraint is populated and ready to pass to /proposals/slot-search.
    safe=False means blocks contains the reason(s); constraint is None.
    No DB, no LLM, no slot-search, no appointment mutation involved in producing this.
    """
    safe: bool
    constraint: Optional[SlotSearchProposalIn] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    summary: str


class SlotSearchCommandExecutionOut(BaseModel):
    """Result of normalizing a Bernie slot-search command and, when safe, searching slots."""
    intent: Literal["search_slots_from_command"] = "search_slots_from_command"
    safe: bool
    normalization: SlotSearchCommandResult
    proposal: Optional[SlotSearchProposalOut] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    summary: str


class SlotSelectionProposalIn(BaseModel):
    """Supervised selection of one slot-search candidate for create-proposal review."""
    search_execution: Optional[SlotSearchCommandExecutionOut] = None
    selected_candidate_index: Optional[int] = Field(default=None, ge=0)
    selected_candidate: Optional[SlotCandidate] = None
    practitioner_id: Optional[uuid.UUID] = None
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    booked_via: BookingChannel = BookingChannel.Receptionist

    @model_validator(mode="after")
    def require_candidate_and_patient_context(self):
        if self.search_execution is None and self.selected_candidate is None:
            raise ValueError("search_execution or selected_candidate is required")
        if self.patient_id is None and not self.patient_name_provisional:
            execution_patient_id = None
            if (
                self.search_execution is not None
                and self.search_execution.normalization.constraint is not None
            ):
                execution_patient_id = self.search_execution.normalization.constraint.patient_id
            if execution_patient_id is None:
                raise ValueError("patient_id or patient_name_provisional is required")
        return self


class SlotSelectionProposalOut(BaseModel):
    intent: Literal["select_slot_for_create_proposal"] = "select_slot_for_create_proposal"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["proposal", "blocked"]
    summary: str
    selected_candidate: Optional[SlotCandidate] = None
    create_proposal: Optional[AppointmentCreateProposalOut] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    # Additive turn tracking (default None for backward compat with Sprint 104).
    turn_ref: Optional["BernieTurnRef"] = None
    # Deterministic freshness id for the create proposal. Stamped by server;
    # clients echo back in confirmation; server recomputes and compares.
    proposal_freshness_id: Optional[str] = None
    # Optional server-owned Bernie session coordinates stamped by the backend
    # when the proposal was staged through a live server session.
    session_binding: Optional[dict[str, Any]] = None
    # Server-signed confirmation evidence. The client must echo this unchanged;
    # the server verifies it before any confirmation-grade write.
    signed_confirmation_evidence: Optional[dict[str, Any]] = None


class BernieStaffReviewSlotSummary(BaseModel):
    appointment_date: date
    start_time_local: time
    duration_minutes: int
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)


class BerniePractitionerEvidence(BaseModel):
    """Structured practitioner evidence for a supervised Bernie booking proposal."""
    practitioner_id: uuid.UUID
    display_name: str
    provider_number: Optional[str] = None
    location_label: Optional[str] = None


class BerniePatientEvidence(BaseModel):
    """Structured patient evidence for a supervised Bernie booking proposal."""
    patient_id: Optional[uuid.UUID] = None
    patient_label: str
    date_of_birth: Optional[date] = None
    masked_phone: Optional[str] = None
    confidence: Literal["unlinked", "low", "medium", "high", "ambiguous"]
    is_provisional: bool = False


class BernieIdentityEvidence(BaseModel):
    """Staff-facing identity evidence for a supervised Bernie booking proposal."""
    patient_id: Optional[uuid.UUID] = None
    patient_label: Optional[str] = None
    confidence: Literal["unlinked", "low", "medium", "high", "ambiguous"]
    recognition_status: Literal[
        "not_recognized",
        "recognized",
        "ambiguous",
        "provisional",
    ] = "not_recognized"
    details_verification_status: Literal[
        "not_checked",
        "verified",
        "requires_follow_up",
        "not_required_for_booking",
    ] = "not_checked"
    verification_status: Literal[
        "not_applicable",
        "requires_staff_verification",
        "verified_by_staff",
    ] = "not_applicable"
    matched_fields: list[str] = Field(default_factory=list)
    supporting_context: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    staff_prompt: str


class BernieStaffReviewPayload(BaseModel):
    headline: str
    status: Literal["blocked", "candidate_selection_required", "confirmation_ready", "clinic_day_exhausted", "existing_booking_found"]
    staff_action_required: str
    confirmation_ready: bool
    selected_slot: Optional[BernieStaffReviewSlotSummary] = None
    candidate_slots: list[BernieStaffReviewSlotSummary] = Field(default_factory=list)
    identity_evidence: Optional[BernieIdentityEvidence] = None
    practitioner_evidence: Optional[BerniePractitionerEvidence] = None
    patient_evidence: Optional[BerniePatientEvidence] = None
    warning_summary: str
    evidence_summary: str
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    confirm_endpoint: Optional[str] = None
    confirm_payload: Optional[dict[str, Any]] = None
    confirm_evidence: list[str] = Field(default_factory=list)
    confirm_affordance: Optional[ConfirmAffordanceDecision] = None
    ui_view_model: Optional[dict[str, Any]] = None


class BerniePilotEligibilityOut(BaseModel):
    surface: Literal["bernie_staff_review"]
    enabled: bool
    eligible: bool
    reason: Literal["pilot_disabled", "allowlist_match", "no_allowlist_match"]
    practice_allowed: bool
    user_allowed: bool


# ── Bernie confidence/decision-policy contract ────────────────────────────────

BernieConfidenceBand = Literal["assume", "proceed_with_check", "ask", "block"]
# Lattice order (most permissive → most restrictive): assume < proceed_with_check < ask < block


class BernieConfidenceAxis(BaseModel):
    """Per-axis confidence/decision result for the Bernie interpreter."""
    axis: str  # intent | temporal | practitioner | patient_identity | slot_validity | speech_transcription
    band: BernieConfidenceBand
    basis: str  # human-readable explanation; no raw field names / UUIDs
    staff_detail: Optional[str] = None  # additional context shown to staff
    debug_score: Optional[float] = None  # only present when bernie_interpreter_debug_disclosure=True


class BernieAssumption(BaseModel):
    """A deterministic assumption Bernie made that can be reversed by staff."""
    field: str  # e.g. "date_from"
    assumed_value: str  # e.g. "today"
    basis: str  # why
    reversible_copy: str  # first-person reversal instruction, e.g. "Tell me the date if today is wrong."


class BernieStaffCheck(BaseModel):
    """A check Bernie is asking staff to perform before confirming."""
    code: str
    staff_prompt: str  # first-person prompt, e.g. "Please verify the patient's date of birth."


class BernieDecisionPolicy(BaseModel):
    """Aggregated decision-policy result — the sole authoritative gate."""
    overall_band: BernieConfidenceBand  # lattice-min over all axes
    rationale: str
    requires_staff_confirmation: bool = True  # always True; never set False by the interpreter


class BerniePatientCandidate(BaseModel):
    """A fuzzy or ambiguous patient candidate surfaced as a 'Do you mean...?' choice.

    candidate_key holds the patient UUID as a string. Staff MUST verify DOB/identity
    before using this key to link a patient. It is never auto-selected or confirmed.
    """
    candidate_key: str
    display_name: str
    dob_masked: Optional[str] = None  # e.g. "1955-**-**"
    match_kind: Literal["exact", "fuzzy"]
    requires_identifier: bool = True


class BernieBookingContextEntry(BaseModel):
    """Compact, PHI-safe appointment entry for staff-facing booking context."""
    appointment_date: date
    relative_label: str  # e.g. "3 days ago", "in 7 days", "today"
    status: str  # AppointmentStatus.value
    practitioner_display: str
    appointment_type_name: Optional[str] = None
    duration_minutes: int


class BerniePatientBookingContext(BaseModel):
    """Compact read-only context returned only for a recognized (exact-match) patient."""
    patient_key: str  # patient UUID as string
    recent_bookings: list[BernieBookingContextEntry] = Field(default_factory=list)
    future_bookings: list[BernieBookingContextEntry] = Field(default_factory=list)
    has_future_booking: bool
    existing_future_follow_up: bool
    recent_count: int
    future_count: int
    reference_date: date
    generated_at: datetime


class BernieContextFreshness(BaseModel):
    """Freshness signal so the UI can detect and clear stale Bernie context."""
    reference_date: date
    generated_at: datetime
    stale: bool
    basis: str


class ExistingBookingSummary(BaseModel):
    """Additive typed existing-booking summary for staff review context.

    Carries only structured metadata serving the existing-booking-finding outcome.
    Does not broaden PHI beyond the current staff-review context.
    """
    appointment_date: date
    start_time_local: time
    practitioner_display: str
    status: str
    appointment_type_name: Optional[str] = None
    duration_minutes: int


class BernieSlotSuggestion(BaseModel):
    """A typed, non-mutating next-step suggestion when no slots are found."""
    kind: Literal["next_available_day", "widen_time_window", "alternate_practitioner"]
    summary: str
    params: Optional[dict[str, Any]] = None
    requires_confirmation: bool = True


class BernieNoSlotSuggestionSelectionIn(BaseModel):
    """Typed event for staff selecting one of Bernie's no-slot suggestions.

    Carries the originating turn_ref (so the server can verify the suggestion
    came from a known turn in the same session) and the selected suggestion kind.
    This is a non-mutating read-only event — it produces a new supervised-booking
    request pre-populated with the suggestion's adjusted params, not a booking.
    """
    turn_ref: "BernieTurnRef"
    suggestion: BernieSlotSuggestion
    # Original supervised-booking request that yielded the no-slot suggestions;
    # the server uses this to build the next slot-search command.
    original_request: "BernieSupervisedBookingIn"


class BernieNoSlotSuggestionSelectionOut(BaseModel):
    """Result of a no-slot suggestion selection."""
    intent: Literal["no_slot_suggestion_selection"] = "no_slot_suggestion_selection"
    accepted: bool
    turn_ref: "BernieTurnRef"
    next_request: Optional["BernieSupervisedBookingIn"] = None
    summary: str
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)


class BernieBookingInstructionInterpretIn(BaseModel):
    """Raw staff text intake for read-only Bernie booking interpretation."""
    instruction: str = Field(min_length=1, max_length=1000)
    reference_date: Optional[date] = None
    context_frames: list[dict[str, Any]] = Field(default_factory=list)
    # Additive turn tracking (Optional for backward compat).
    # Clients may supply session_id to continue a session; the server mints a
    # new turn_ref on the response with the next turn_index.  On the first call
    # (session_id absent) the server mints a fresh session_id.
    turn_ref: Optional["BernieTurnRef"] = None
    # Additive N8 server-owned session coordinates. These are distinct from
    # the legacy/UI turn_ref and are optional for backward compatibility.
    server_session_id: Optional[str] = None
    server_session_surface_id: Optional[str] = None
    server_session_expected_revision: Optional[int] = Field(default=None, ge=0)
    server_session_idempotency_key: Optional[str] = None


class BernieBookingInterpreterMetadata(BaseModel):
    provider: Literal["disabled", "fake", "gemini_vertex"]
    mode: Literal["disabled", "mocked", "live", "deterministic_fallback"]
    live_provider: bool = False


class BernieBookingOutcomeOut(BaseModel):
    """Read-only typed outcome label for a single Bernie booking turn.

    Schema mirror of app.services.diary.outcomes.BernieBookingOutcome.
    Attached as an additive Optional field on both interpret and supervised-booking
    envelopes so callers can read one authoritative classification instead of
    reconciling the result literal, reception_policy flags, and server_session state.

    kind: BernieBookingOutcomeKind value (str enum — see app.services.diary.outcomes)
    family: one of "proceed", "clarify", "advisory", "no_availability", "roster_gap",
            "blocked", "terminal"
    session_state: BernieSessionState value (str enum) the outcome maps to

    can_confirm is REPORT ONLY and never itself a confirm grant. Confirm authority
    still requires the existing gate, signed evidence, and session binding.
    """
    kind: str
    family: str
    session_state: str
    requires_confirmation: bool
    can_confirm: bool = False
    is_terminal: bool = False
    reason_codes: list[str] = Field(default_factory=list)
    basis: str = ""
    schedule_explanation: Optional[dict[str, Any]] = None


class BernieBookingInstructionInterpretOut(BaseModel):
    """Structured, non-mutating intent envelope for a booking instruction."""
    intent: Literal["interpret_booking_instruction"] = "interpret_booking_instruction"
    safe: bool
    result: Literal["blocked", "clarification_required", "interpreted"]
    autonomy_tier: Literal["execute_with_report", "blocked"]
    summary: str
    confidence: float = Field(ge=0, le=1)  # advisory/display-only; NOT a gating signal
    # Immutable reference date captured once from intake; echoed in every response so the
    # client never needs to re-derive it. All relative tokens (today/tomorrow) are resolved
    # against this value and it is never overwritten by downstream steps.
    request_reference_date: Optional[date] = None
    command_candidate: Optional[SlotSearchCommandIn] = None
    missing_fields: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    clarifying_question: Optional[str] = None
    normalization: Optional[SlotSearchCommandResult] = None
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    provider_metadata: BernieBookingInterpreterMetadata
    # ── Confidence/decision-policy axes (additive; default-empty for backward compat) ──
    confidence_axes: list[BernieConfidenceAxis] = Field(default_factory=list)
    decision: Optional[BernieDecisionPolicy] = None
    assumptions: list[BernieAssumption] = Field(default_factory=list)
    staff_checks: list[BernieStaffCheck] = Field(default_factory=list)
    patient_candidates: list[BerniePatientCandidate] = Field(default_factory=list)
    debug: Optional[dict[str, Any]] = None  # only populated when bernie_interpreter_debug_disclosure=True
    # ── Patient booking context (additive; only populated for recognized patients) ──
    patient_booking_context: Optional[BerniePatientBookingContext] = None
    context_freshness: Optional[BernieContextFreshness] = None
    reception_context: Optional[dict[str, Any]] = None
    reception_policy: Optional[dict[str, Any]] = None
    # Additive turn tracking (default None for backward compat).
    turn_ref: Optional["BernieTurnRef"] = None
    # Additive N9 server-owned session coordinate echo. Only populated when the
    # caller supplied a valid Bernie server session and the route appended its
    # compact outcome event.
    server_session: Optional["BernieSessionSnapshotOut"] = None
    # Additive N10 typed outcome classification. Read-only report field; never
    # a confirm grant. Default None preserves backward compat for existing clients.
    outcome: Optional["BernieBookingOutcomeOut"] = None


class BernieSupervisedBookingIn(BaseModel):
    """Typed deterministic intake for supervised Bernie booking proposals."""
    command: SlotSearchCommandIn
    reference_date: date
    context_frames: list[dict[str, Any]] = Field(default_factory=list)
    selected_candidate_index: Optional[int] = Field(default=None, ge=0)
    selected_candidate: Optional[SlotCandidate] = None
    practitioner_id: Optional[uuid.UUID] = None
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    patient_id: Optional[uuid.UUID] = None
    patient_name_provisional: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    booked_via: BookingChannel = BookingChannel.Receptionist
    # Additive turn tracking (Optional for backward compat with Sprint 104).
    # Clients may supply a session_id to continue an existing session;
    # turn_ref is then stamped on the response with the next turn_index.
    turn_ref: Optional["BernieTurnRef"] = None
    # Additive N8 server-owned session coordinates. When supplied, the route
    # appends compact server outcome events as it progresses through the
    # supervised booking workflow.
    server_session_id: Optional[str] = None
    server_session_surface_id: Optional[str] = None
    server_session_expected_revision: Optional[int] = Field(default=None, ge=0)
    server_session_idempotency_key: Optional[str] = None


class BernieSupervisedBookingOut(BaseModel):
    """Discriminated non-mutating response for supervised Bernie booking intake."""
    intent: Literal["bernie_supervised_booking"] = "bernie_supervised_booking"
    # clinic_day_exhausted: same-day request whose clamped slot search yielded zero
    # remaining bookable slots; staff should restate the date. Never auto-advances date.
    result: Literal["blocked", "candidate_selection_required", "confirmation_ready", "clinic_day_exhausted", "existing_booking_found"]
    # Immutable reference date echoed from intake; never overwritten by downstream steps.
    request_reference_date: Optional[date] = None
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    normalization: SlotSearchCommandResult
    search_proposal: Optional[SlotSearchProposalOut] = None
    selection_proposal: Optional[SlotSelectionProposalOut] = None
    staff_review: BernieStaffReviewPayload
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)
    # ── Additive context fields (default None/empty for backward compat) ──
    patient_booking_context: Optional[BerniePatientBookingContext] = None
    context_freshness: Optional[BernieContextFreshness] = None
    reception_context: Optional[dict[str, Any]] = None
    reception_policy: Optional[dict[str, Any]] = None
    suggestions: list[BernieSlotSuggestion] = Field(default_factory=list)
    # ── Additive existing-booking finding (only present when result is existing_booking_found) ──
    existing_booking: Optional["ExistingBookingSummary"] = None
    # ── Additive turn tracking (default None for backward compat) ──
    turn_ref: Optional["BernieTurnRef"] = None
    server_session: Optional["BernieSessionSnapshotOut"] = None
    # Additive N10 typed outcome classification. Read-only report field; never
    # a confirm grant. Default None preserves backward compat for existing clients.
    outcome: Optional["BernieBookingOutcomeOut"] = None


class ReceptionOneProductContextRequestIn(BaseModel):
    """Default-off authored-synthetic request for the Reception One planner."""

    model_config = ConfigDict(extra="forbid")

    contract_version: Literal[
        "reception.one.product-context-request.v1"
    ] = "reception.one.product-context-request.v1"
    instruction: str = Field(min_length=1, max_length=512)
    reference_date: date
    surface_id: str = Field(default="diary-main", min_length=1, max_length=100)
    correlation_id: str = Field(min_length=3, max_length=100)
    data_class: Literal["authored_synthetic"] = "authored_synthetic"
    selected_appointment_id: Optional[uuid.UUID] = None
    planner_mode: Literal["deterministic", "isolated_vertex"] = "deterministic"


class ReceptionOneProductContextReviewOut(BaseModel):
    disposition: Literal[
        "admit",
        "revision_required",
        "clarification_required",
        "reject",
    ]
    plan_hash: Optional[str] = None
    operator_ids: list[str] = Field(default_factory=list, max_length=12)
    safe_repairs: list[str] = Field(default_factory=list, max_length=12)
    violation_paths: list[str] = Field(default_factory=list, max_length=20)
    context_revision: int = Field(ge=1)


class ReceptionOneProductContextSlotOut(BaseModel):
    slot_handle: str = Field(min_length=3, max_length=100)
    appointment_date: date
    start_time_local: time
    duration_minutes: int = Field(ge=5, le=180)
    warning_codes: list[str] = Field(default_factory=list, max_length=8)


class ReceptionOneProductContextAppointmentOut(BaseModel):
    appointment_handle: str = Field(min_length=3, max_length=100)
    appointment_date: date
    start_time_local: time
    duration_minutes: int = Field(ge=5, le=480)
    status: Literal["booked", "arrived", "completed", "dna"]


class ReceptionOneProductContextAdapterReviewOut(BaseModel):
    adapter_kind: Literal[
        "update_proposal",
        "delete_proposal",
        "squeeze_in_assessment",
    ]
    performed: Literal[True] = True
    safe: bool
    summary: str = Field(min_length=1, max_length=500)
    warning_codes: list[str] = Field(default_factory=list, max_length=20)
    block_codes: list[str] = Field(default_factory=list, max_length=20)
    candidate_count: int = Field(default=0, ge=0, le=24)
    freshness_verified: bool
    confirmation_evidence_released: Literal[False] = False
    write_performed: Literal[False] = False


class ReceptionOneProductContextProposalOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: Literal[
        "reception.one.product-context-proposal.v1"
    ] = "reception.one.product-context-proposal.v1"
    result: Literal[
        "proposal_ready",
        "clarification_required",
        "revision_required",
        "blocked",
    ]
    safe: bool
    summary: str = Field(min_length=1, max_length=500)
    request_id: str = Field(min_length=3, max_length=100)
    correlation_id: str = Field(min_length=3, max_length=100)
    context_revision: int = Field(ge=1)
    data_class: Literal["authored_synthetic"] = "authored_synthetic"
    patient_handle: Optional[str] = Field(default=None, max_length=100)
    patient_display: Optional[str] = Field(default=None, max_length=80)
    practitioner_handle: Optional[str] = Field(default=None, max_length=100)
    practitioner_display: Optional[str] = Field(default=None, max_length=80)
    goal: Optional[str] = Field(default=None, max_length=80)
    operation_id: Optional[str] = Field(default=None, max_length=100)
    candidate_slots: list[ReceptionOneProductContextSlotOut] = Field(
        default_factory=list,
        max_length=24,
    )
    selected_appointment: Optional[
        ReceptionOneProductContextAppointmentOut
    ] = None
    proposed_appointment_date: Optional[date] = None
    proposed_start_time_local: Optional[time] = None
    proposed_duration_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=480,
    )
    adapter_review: Optional[
        ReceptionOneProductContextAdapterReviewOut
    ] = None
    warning_codes: list[str] = Field(default_factory=list, max_length=20)
    review: ReceptionOneProductContextReviewOut
    requires_confirmation: Literal[True] = True
    proposal_only: Literal[True] = True
    write_performed: Literal[False] = False
    confirmation_performed: Literal[False] = False
    planner_mode: Literal["deterministic", "isolated_vertex"] = "deterministic"
    provider_calls: int = Field(default=0, ge=0, le=2)
    runtime_audit_ref: Optional[str] = Field(default=None, max_length=100)
    model_database_access: Literal[False] = False
    database_reads_performed: bool
    legacy_interpreter_gate_changed: Literal[False] = False


class BernieCreateProposalConfirmationIn(BaseModel):
    """Explicit staff confirmation for supervised Bernie create-proposal evidence."""
    confirmed: bool = False
    selection_proposal: SlotSelectionProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
    # Additive turn tracking (Optional for backward compat).
    # When turn_ref is supplied the server validates that reference_date matches
    # the session reference_date captured on turn-0 and that the echoed
    # candidate/proposal freshness ids match recomputed expected values.
    turn_ref: Optional["BernieTurnRef"] = None
    # Client echoes back the freshness ids it received from the server.
    # Presence triggers the staleness gate; absence is tolerated for backward compat.
    candidate_freshness_id: Optional[str] = None
    proposal_freshness_id: Optional[str] = None
    # S1 signed evidence path. New backend-prepared confirm payloads set
    # signed_confirmation_evidence_required=True and include the signed envelope.
    # Legacy unsigned callers are accepted only through explicit compatibility.
    signed_confirmation_evidence: Optional[dict[str, Any]] = None
    signed_confirmation_evidence_required: bool = False
    # Optional N7 server-session binding. When present, it is included in the
    # signed evidence payload and validated fail-closed against current
    # server-owned Bernie session coordinates.
    session_binding: Optional[dict[str, Any]] = None


# ── Bernie server-owned session endpoint contract ───────────────────────────

BernieSessionStateValue = Literal[
    "instruction_entry",
    "recognition",
    "clarification",
    "context_enrichment",
    "slot_search",
    "candidate_selection",
    "proposal_preview",
    "confirmation",
    "confirmed",
    "no_slot",
    "clinic_day_exhausted",
    "handed_off",
]

BernieSessionEventTypeValue = Literal[
    "staff_instruction",
    "clarification_reply",
    "candidate_selected",
    "suggestion_selected",
    "diary_navigated",
    "refresh_requested",
    "confirm_submitted",
    "new_session",
    "interpretation_outcome",
    "context_outcome",
    "slot_search_outcome",
    "proposal_outcome",
    "confirmation_outcome",
]


class BernieSessionEventOut(BaseModel):
    event_id: str
    session_id: str
    event_type: BernieSessionEventTypeValue
    turn_index: int
    occurred_at: datetime
    expected_revision: Optional[int] = None
    idempotency_key: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)


class BernieSessionSnapshotOut(BaseModel):
    session_id: str
    surface_id: str
    state: BernieSessionStateValue
    revision: int
    request_reference_date: Optional[date] = None
    patient_id: Optional[uuid.UUID] = None
    patient_band: Optional[str] = None
    practitioner_id: Optional[uuid.UUID] = None
    practitioner_band: Optional[str] = None
    candidate_freshness_ids: list[str] = Field(default_factory=list)
    staged_proposal_freshness_id: Optional[str] = None
    turn_count: int = 0
    last_event_id: Optional[str] = None
    stale_reason_code: Optional[str] = None
    events: list[BernieSessionEventOut] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BernieSessionActiveOut(BaseModel):
    result: Literal["active_session"]
    session: BernieSessionSnapshotOut


class BernieSessionNewIn(BaseModel):
    surface_id: str = Field(min_length=1, max_length=100)
    reference_date: Optional[date] = None


class BernieSessionEventAppendIn(BaseModel):
    event_type: BernieSessionEventTypeValue
    expected_revision: int = Field(ge=0)
    surface_id: str = Field(min_length=1, max_length=100)
    event_id: Optional[str] = Field(default=None, min_length=1, max_length=100)
    idempotency_key: Optional[str] = Field(default=None, min_length=1, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)


class BernieSessionEventAppendOut(BaseModel):
    result: Literal["accepted", "rejected"]
    accepted: bool
    session: Optional[BernieSessionSnapshotOut] = None
    event: Optional[BernieSessionEventOut] = None
    code: Optional[str] = None
    detail: Optional[str] = None


# Resolve forward references now that all models are defined.
BernieTurnRef.model_rebuild()
SlotSelectionProposalOut.model_rebuild()
BernieSupervisedBookingIn.model_rebuild()
BernieSupervisedBookingOut.model_rebuild()
BernieCreateProposalConfirmationIn.model_rebuild()
BernieBookingInstructionInterpretIn.model_rebuild()
BernieBookingInstructionInterpretOut.model_rebuild()
BernieNoSlotSuggestionSelectionIn.model_rebuild()
BernieNoSlotSuggestionSelectionOut.model_rebuild()
