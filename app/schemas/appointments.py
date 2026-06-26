import uuid
from datetime import datetime, date, time
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator
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
