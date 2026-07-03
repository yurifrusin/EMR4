"""Typed receptionist context frames for the Bernie domain.

Frames are compact, deterministic facts assembled before Bernie responds. They
separate world state, advisories, stale evidence, model uncertainty, and hard
guardrails so later route/UI code does not collapse them into the same message.

This module is pure contract code: no DB, no network, no wall-clock.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


BernieFrameSource = Literal[
    "staff_instruction",
    "client_context",
    "server_resolver",
    "patient_context",
    "slot_search",
    "schedule",
    "model",
    "guardrail",
]

BernieFrameStatus = Literal[
    "known",
    "partial",
    "missing",
    "recognized",
    "not_recognized",
    "ambiguous",
    "available",
    "unavailable",
    "unknown",
    "not_run",
    "searched_with_candidates",
    "searched_no_candidates",
    "advisory",
    "fresh",
    "stale",
    "ask",
    "proceed_with_check",
    "allowed",
    "requires_confirmation",
    "blocked",
]

BernieFrameType = Literal[
    "requested_appointment",
    "patient_booking_context",
    "roster_schedule",
    "slot_search",
    "advisory_warning",
    "stale_evidence",
    "model_uncertainty",
    "guardrail_outcome",
]


class BernieReceptionFrameBase(BaseModel):
    """Base fields every Bernie context frame must carry."""

    model_config = ConfigDict(extra="forbid")

    frame_type: BernieFrameType
    status: BernieFrameStatus
    basis: str
    source: BernieFrameSource
    reference_date: date
    reason_code: str | None = None
    fresh_for_turn_ref: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class BernieRequestedAppointmentFrame(BernieReceptionFrameBase):
    frame_type: Literal["requested_appointment"] = "requested_appointment"
    status: Literal["known", "partial", "missing"]
    source: Literal["staff_instruction", "server_resolver"] = "staff_instruction"


class BerniePatientBookingContextFrame(BernieReceptionFrameBase):
    frame_type: Literal["patient_booking_context"] = "patient_booking_context"
    status: Literal["recognized", "not_recognized", "ambiguous"]
    source: Literal["patient_context", "server_resolver"] = "patient_context"


class BernieRosterScheduleFrame(BernieReceptionFrameBase):
    frame_type: Literal["roster_schedule"] = "roster_schedule"
    status: Literal["available", "unavailable", "missing", "unknown"]
    source: Literal["schedule", "server_resolver"] = "schedule"


class BernieSlotSearchFrame(BernieReceptionFrameBase):
    frame_type: Literal["slot_search"] = "slot_search"
    status: Literal["not_run", "searched_with_candidates", "searched_no_candidates", "blocked"]
    source: Literal["slot_search"] = "slot_search"
    candidate_count: int | None = Field(default=None, ge=0)


class BernieAdvisoryWarningFrame(BernieReceptionFrameBase):
    frame_type: Literal["advisory_warning"] = "advisory_warning"
    status: Literal["advisory"] = "advisory"
    source: Literal["patient_context", "server_resolver", "guardrail"] = "server_resolver"
    reason_code: str


class BernieStaleEvidenceFrame(BernieReceptionFrameBase):
    frame_type: Literal["stale_evidence"] = "stale_evidence"
    status: Literal["fresh", "stale"]
    source: Literal["guardrail"] = "guardrail"
    reason_code: str


class BernieModelUncertaintyFrame(BernieReceptionFrameBase):
    frame_type: Literal["model_uncertainty"] = "model_uncertainty"
    status: Literal["ask", "proceed_with_check"]
    source: Literal["model", "server_resolver"] = "model"
    reason_code: str


class BernieGuardrailOutcomeFrame(BernieReceptionFrameBase):
    frame_type: Literal["guardrail_outcome"] = "guardrail_outcome"
    status: Literal["allowed", "requires_confirmation", "blocked"]
    source: Literal["guardrail"] = "guardrail"
    reason_code: str


BernieReceptionFrame = Annotated[
    Union[
        BernieRequestedAppointmentFrame,
        BerniePatientBookingContextFrame,
        BernieRosterScheduleFrame,
        BernieSlotSearchFrame,
        BernieAdvisoryWarningFrame,
        BernieStaleEvidenceFrame,
        BernieModelUncertaintyFrame,
        BernieGuardrailOutcomeFrame,
    ],
    Field(discriminator="frame_type"),
]


class BernieReceptionContextFrameSet(BaseModel):
    """Versioned set of typed frames for one Bernie reception turn."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["bernie.reception_context.v1"] = "bernie.reception_context.v1"
    reference_date: date
    frames: list[BernieReceptionFrame] = Field(default_factory=list)

    def frames_of_type(self, frame_type: BernieFrameType) -> list[BernieReceptionFrame]:
        return [frame for frame in self.frames if frame.frame_type == frame_type]

    def first_frame(self, frame_type: BernieFrameType) -> BernieReceptionFrame | None:
        matches = self.frames_of_type(frame_type)
        return matches[0] if matches else None

    def has_frame(self, frame_type: BernieFrameType, *, status: str | None = None) -> bool:
        return any(
            frame.frame_type == frame_type and (status is None or frame.status == status)
            for frame in self.frames
        )


__all__ = [
    "BernieAdvisoryWarningFrame",
    "BernieFrameSource",
    "BernieFrameStatus",
    "BernieFrameType",
    "BernieGuardrailOutcomeFrame",
    "BernieModelUncertaintyFrame",
    "BerniePatientBookingContextFrame",
    "BernieReceptionContextFrameSet",
    "BernieReceptionFrame",
    "BernieReceptionFrameBase",
    "BernieRequestedAppointmentFrame",
    "BernieRosterScheduleFrame",
    "BernieSlotSearchFrame",
    "BernieStaleEvidenceFrame",
]
