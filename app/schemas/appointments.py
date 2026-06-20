import uuid
from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.models.appointments import AppointmentStatus, BookingChannel


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
    queue_position: Optional[int] = None

    @model_validator(mode="after")
    def reject_partial_local_pair(self):
        has_partial = (self.appointment_date is None) != (self.start_time_local is None)
        if has_partial:
            raise ValueError("appointment_date and start_time_local must be supplied together")
        return self


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


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
    booked_via: BookingChannel
    waiting_room: Optional[str] = None
    queue_position: Optional[int] = None
    created_at: datetime
    patient: Optional[PatientBrief] = None
    practitioner: PractitionerBrief
    appointment_type: Optional[AppointmentTypeOut] = None

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
