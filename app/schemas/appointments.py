import uuid
from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel
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

    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    patient_id: uuid.UUID
    practitioner_id: uuid.UUID
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    start_time: datetime
    duration_minutes: int = 15
    reason: Optional[str] = None
    notes: Optional[str] = None
    booked_via: BookingChannel = BookingChannel.Receptionist


class AppointmentUpdate(BaseModel):
    appointment_type_id: Optional[uuid.UUID] = None
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    waiting_room: Optional[str] = None
    queue_position: Optional[int] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentOut(BaseModel):
    id: uuid.UUID
    practice_id: uuid.UUID
    patient_id: uuid.UUID
    practitioner_id: uuid.UUID
    appointment_type_id: Optional[uuid.UUID] = None
    location_id: Optional[uuid.UUID] = None
    start_time: datetime
    duration_minutes: int
    status: AppointmentStatus
    reason: Optional[str] = None
    notes: Optional[str] = None
    booked_via: BookingChannel
    waiting_room: Optional[str] = None
    queue_position: Optional[int] = None
    created_at: datetime
    patient: PatientBrief
    practitioner: PractitionerBrief

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
