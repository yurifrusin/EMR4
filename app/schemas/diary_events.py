import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AppointmentRescheduledEventPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    appointment_id: uuid.UUID
    practitioner_id: uuid.UUID
    location_id: uuid.UUID | None = None
    start_time: datetime
    end_time: datetime
    reason_codes: list[Literal["appointment_time_changed"]] = Field(
        min_length=1,
        max_length=1,
    )

    @model_validator(mode="after")
    def require_ordered_window(self):
        if self.end_time <= self.start_time:
            raise ValueError("event end_time must be after start_time")
        return self


class DiaryCommittedEventOut(BaseModel):
    event_id: uuid.UUID
    event_type: Literal["diary.appointment_rescheduled"]
    schema_version: Literal["diary.appointment_rescheduled.v1"]
    source_system: Literal["emr4-diary"]
    aggregate_id: uuid.UUID
    aggregate_revision: int = Field(gt=0)
    occurred_at: datetime
    received_at: datetime
    evidence_mode: Literal["authored_synthetic_local"]
    payload: AppointmentRescheduledEventPayload


class DiaryCommittedEventFeedOut(BaseModel):
    schema_version: Literal["diary.committed_event_feed.v1"] = (
        "diary.committed_event_feed.v1"
    )
    enabled: bool
    baseline_established: bool
    cursor: str | None = Field(default=None, max_length=256)
    events: list[DiaryCommittedEventOut] = Field(default_factory=list)
