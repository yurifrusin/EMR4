from datetime import time
from typing import Optional
from pydantic import BaseModel, Field


class DiaryBreakOut(BaseModel):
    label: str
    from_time: time
    to_time: time

    model_config = {"from_attributes": True}


class DiaryColumnOut(BaseModel):
    room_label: str
    assignment: Optional[str] = None
    practitioner_ahpra: Optional[str] = None
    tint_hex: Optional[str] = None
    breaks: list[DiaryBreakOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DiaryTemplateOut(BaseModel):
    practice_name: Optional[str] = None
    slot_start: time
    slot_end: time
    slot_interval_minutes: int
    footer: list[str] = Field(default_factory=list)
    columns: list[DiaryColumnOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}
