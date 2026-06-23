from datetime import date, time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class PracticeLocationOut(BaseModel):
    id: UUID
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class DiaryBreakOut(BaseModel):
    label: str
    from_time: time
    to_time: time

    model_config = {"from_attributes": True}


class DiaryColumnOut(BaseModel):
    room_label: str
    assignment: Optional[str] = None
    practitioner_id: Optional[UUID] = None
    practitioner_ahpra: Optional[str] = None
    tint_hex: Optional[str] = None
    slot_interval_minutes: Optional[int] = Field(default=None, ge=5)
    breaks: list[DiaryBreakOut] = Field(default_factory=list)

    @field_validator("slot_interval_minutes", mode="before")
    @classmethod
    def must_be_multiple_of_five(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v % 5 != 0:
            raise ValueError(f"slot_interval_minutes must be a multiple of 5, got {v}")
        return v

    model_config = {"from_attributes": True}


class DiaryTemplateOut(BaseModel):
    practice_name: Optional[str] = None
    location_id: Optional[UUID] = None
    slot_start: time
    slot_end: time
    slot_interval_minutes: int
    footer: list[str] = Field(default_factory=list)
    columns: list[DiaryColumnOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class WaitingAreaOut(BaseModel):
    id: UUID
    name: str
    display_order: int
    is_active: bool
    location_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class WaitingAreaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)
    location_id: Optional[UUID] = None


class WaitingAreaUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    display_order: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class RoomOut(BaseModel):
    id: UUID
    name: str
    display_order: int
    is_active: bool
    location_id: Optional[UUID] = None
    default_waiting_area_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class RoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_order: int = Field(..., ge=0)
    location_id: Optional[UUID] = None
    default_waiting_area_id: Optional[UUID] = None


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    display_order: Optional[int] = Field(default=None, ge=0)
    default_waiting_area_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DiaryRosterEntryOut(BaseModel):
    room_id: UUID
    room_name: str
    display_order: int
    practitioner_id: Optional[UUID] = None
    practitioner_ahpra: Optional[str] = None
    label: Optional[str] = None
    location_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class DiaryRosterOut(BaseModel):
    date: date
    entries: list[DiaryRosterEntryOut] = Field(default_factory=list)
