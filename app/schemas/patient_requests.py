"""Narrow patient and receptionist request shapes; no patient staff command."""

import uuid
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PatientRequestSubmissionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["patient.request_submission.v1"]
    request_id: uuid.UUID
    request_version: int = Field(ge=1)
    date: date
    earliest_local: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    latest_local: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    reason_code: Literal["follow_up"]
    authority: Literal["request_only"]


class PatientRequestVersionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_version: int = Field(ge=1)


class PatientRequestOption(BaseModel):
    date: date
    local_time: time
    zone: str


class PatientRequestReadback(BaseModel):
    request_id: uuid.UUID
    state: Literal["draft", "submitted", "booked", "cancelled", "expired"]
    request_version: int
    preference_date: date | None = None
    earliest_local: time | None = None
    latest_local: time | None = None
    booked_appointment_id: uuid.UUID | None = None
    booked_start_time: datetime | None = None
    booked_status: str | None = None
    historical_request_result: bool = False


class StaffRequestProposalIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_version: int = Field(ge=1)
    selected: PatientRequestOption


class StaffRequestReadback(BaseModel):
    request_id: uuid.UUID
    patient_id: uuid.UUID
    state: str
    request_version: int
    preference_date: date | None
    earliest_local: time | None
    latest_local: time | None
    practice_timezone: str
    booked_appointment_id: uuid.UUID | None
