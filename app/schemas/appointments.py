import uuid
from datetime import datetime, date, time
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.appointments import AppointmentStatus, BookingChannel, AppointmentAuditAction


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
    confirmed_warnings: list[str] = Field(default_factory=list)


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


class AppointmentStatusProposalIn(BaseModel):
    status: AppointmentStatus
    waiting_area_id: Optional[uuid.UUID] = None


class AppointmentStatusCommand(BaseModel):
    appointment_id: uuid.UUID
    status: AppointmentStatus
    waiting_area_id: Optional[uuid.UUID] = None
    clears_waiting_area: bool


class AppointmentStatusProposalOut(BaseModel):
    intent: Literal["update_appointment_status"] = "update_appointment_status"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["execute_with_report", "proposal", "blocked"]
    summary: str
    command: AppointmentStatusCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)


class AppointmentWaitingAreaProposalIn(BaseModel):
    waiting_area_id: Optional[uuid.UUID] = None


class AppointmentWaitingAreaCommand(BaseModel):
    appointment_id: uuid.UUID
    waiting_area_id: Optional[uuid.UUID] = None
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


class AppointmentDeleteIn(BaseModel):
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    confirmed_warnings: list[str] = Field(default_factory=list)


class AppointmentDeleteCommand(BaseModel):
    appointment_id: uuid.UUID
    clears_waiting_area: bool
    cancellation_reason: Optional[str] = None


class AppointmentDeleteProposalOut(BaseModel):
    intent: Literal["delete_appointment"] = "delete_appointment"
    safe: bool
    requires_confirmation: bool
    autonomy_tier: Literal["proposal", "blocked"]
    summary: str
    command: AppointmentDeleteCommand
    warnings: list[AppointmentProposalIssue] = Field(default_factory=list)
    blocks: list[AppointmentProposalIssue] = Field(default_factory=list)


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
    status: Literal["blocked", "candidate_selection_required", "confirmation_ready", "clinic_day_exhausted"]
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


class BernieBookingInstructionInterpretIn(BaseModel):
    """Raw staff text intake for read-only Bernie booking interpretation."""
    instruction: str = Field(min_length=1, max_length=1000)
    reference_date: Optional[date] = None
    context_frames: list[dict[str, Any]] = Field(default_factory=list)


class BernieBookingInterpreterMetadata(BaseModel):
    provider: Literal["disabled", "fake", "gemini_vertex"]
    mode: Literal["disabled", "mocked", "live", "deterministic_fallback"]
    live_provider: bool = False


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


class BernieSupervisedBookingOut(BaseModel):
    """Discriminated non-mutating response for supervised Bernie booking intake."""
    intent: Literal["bernie_supervised_booking"] = "bernie_supervised_booking"
    # clinic_day_exhausted: same-day request whose clamped slot search yielded zero
    # remaining bookable slots; staff should restate the date. Never auto-advances date.
    result: Literal["blocked", "candidate_selection_required", "confirmation_ready", "clinic_day_exhausted"]
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


class BernieCreateProposalConfirmationIn(BaseModel):
    """Explicit staff confirmation for supervised Bernie create-proposal evidence."""
    confirmed: bool = False
    selection_proposal: SlotSelectionProposalOut
    confirmed_warnings: list[str] = Field(default_factory=list)
