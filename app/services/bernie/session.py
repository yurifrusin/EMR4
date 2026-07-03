"""Persistence-shaped Bernie booking-session and event contracts.

Contract scaffolding for the server-owned booking-session statechart from the
Fable 5 architecture consult (Sprint C substrate). This module defines the
typed shapes and the static transition tables only - there is NO persisted
session table, no session store, and no endpoint wiring in this slice.

Design constraints:

- **Persistence-shaped, not persisted.** ``BernieSessionRecord`` and
  ``BernieSessionEvent`` are flat, JSON-serializable Pydantic models whose
  fields map 1:1 onto a future DB row / event-log row. Timestamps and ids are
  stored fields, never derived at read time.
- **Backend owns semantic state; frontend owns presentation state.** The
  states here are semantic booking-session states. Panel open/closed, composer
  mode, and disclosure state are frontend presentation state and deliberately
  absent.
- **Two kinds of transition.** Clients send typed events
  (``BernieSessionEventType``); ``CLIENT_EVENT_TRANSITIONS`` says which are
  legal from which state. Transient states advance by server-side outcomes
  (interpretation, slot search, confirmation results); ``SERVER_ADVANCE_TARGETS``
  bounds those. Invalid client events become typed rejections (the future 409
  substrate), not console warnings.
- **Core invariant (statically checkable):** no client event targets
  ``confirmed`` directly; ``confirmed`` is reachable only as a server advance
  from ``confirmation``, and ``confirmation`` only via ``confirm_submitted``
  from ``proposal_preview``.
- **PHI note:** ``staff_instruction`` event payloads and recognised patient
  ids make a persisted session row potentially PHI-bearing. Retention
  classification is an open Yuri decision (consult plan section 9) and must be made
  before any table lands.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class BernieSessionState(str, Enum):
    """Semantic states of a Bernie booking session."""

    instruction_entry = "instruction_entry"
    recognition = "recognition"
    clarification = "clarification"
    context_enrichment = "context_enrichment"
    slot_search = "slot_search"
    candidate_selection = "candidate_selection"
    proposal_preview = "proposal_preview"
    confirmation = "confirmation"
    confirmed = "confirmed"
    no_slot = "no_slot"
    clinic_day_exhausted = "clinic_day_exhausted"
    handed_off = "handed_off"


class BernieSessionEventType(str, Enum):
    """Typed events a client may send into a Bernie booking session."""

    staff_instruction = "staff_instruction"
    clarification_reply = "clarification_reply"
    candidate_selected = "candidate_selected"
    suggestion_selected = "suggestion_selected"
    diary_navigated = "diary_navigated"
    refresh_requested = "refresh_requested"
    confirm_submitted = "confirm_submitted"
    new_session = "new_session"


#: States the server advances out of by computing an outcome; clients cannot
#: drive these except by starting a new session.
TRANSIENT_STATES: frozenset[BernieSessionState] = frozenset({
    BernieSessionState.recognition,
    BernieSessionState.context_enrichment,
    BernieSessionState.slot_search,
    BernieSessionState.confirmation,
})

#: Terminal states for the booking flow - only ``new_session`` leaves them.
TERMINAL_STATES: frozenset[BernieSessionState] = frozenset({
    BernieSessionState.confirmed,
    BernieSessionState.handed_off,
})

#: Legal client events per state and their target state. ``new_session`` and
#: ``diary_navigated`` are handled uniformly in ``validate_session_event`` and
#: are deliberately absent from this table: ``new_session`` is legal from every
#: state and targets ``instruction_entry``; ``diary_navigated`` is legal in
#: every non-transient state and is memory-only (stale marking), leaving the
#: state unchanged.
CLIENT_EVENT_TRANSITIONS: dict[
    BernieSessionState, dict[BernieSessionEventType, BernieSessionState]
] = {
    BernieSessionState.instruction_entry: {
        BernieSessionEventType.staff_instruction: BernieSessionState.recognition,
    },
    BernieSessionState.recognition: {},
    BernieSessionState.clarification: {
        BernieSessionEventType.clarification_reply: BernieSessionState.recognition,
        BernieSessionEventType.staff_instruction: BernieSessionState.recognition,
    },
    BernieSessionState.context_enrichment: {},
    BernieSessionState.slot_search: {},
    BernieSessionState.candidate_selection: {
        BernieSessionEventType.candidate_selected: BernieSessionState.proposal_preview,
        BernieSessionEventType.staff_instruction: BernieSessionState.recognition,
        BernieSessionEventType.refresh_requested: BernieSessionState.slot_search,
    },
    BernieSessionState.proposal_preview: {
        BernieSessionEventType.confirm_submitted: BernieSessionState.confirmation,
        BernieSessionEventType.candidate_selected: BernieSessionState.proposal_preview,
        BernieSessionEventType.staff_instruction: BernieSessionState.recognition,
        BernieSessionEventType.refresh_requested: BernieSessionState.slot_search,
    },
    BernieSessionState.confirmation: {},
    BernieSessionState.confirmed: {},
    BernieSessionState.no_slot: {
        BernieSessionEventType.suggestion_selected: BernieSessionState.slot_search,
        BernieSessionEventType.staff_instruction: BernieSessionState.recognition,
        BernieSessionEventType.refresh_requested: BernieSessionState.slot_search,
    },
    BernieSessionState.clinic_day_exhausted: {
        BernieSessionEventType.suggestion_selected: BernieSessionState.slot_search,
        BernieSessionEventType.staff_instruction: BernieSessionState.recognition,
    },
    BernieSessionState.handed_off: {},
}

#: Bounds on server-side outcome advances out of transient states.
SERVER_ADVANCE_TARGETS: dict[BernieSessionState, frozenset[BernieSessionState]] = {
    BernieSessionState.recognition: frozenset({
        BernieSessionState.clarification,
        BernieSessionState.context_enrichment,
        BernieSessionState.handed_off,
    }),
    BernieSessionState.context_enrichment: frozenset({
        BernieSessionState.slot_search,
    }),
    BernieSessionState.slot_search: frozenset({
        BernieSessionState.candidate_selection,
        BernieSessionState.no_slot,
        BernieSessionState.clinic_day_exhausted,
    }),
    BernieSessionState.confirmation: frozenset({
        BernieSessionState.confirmed,
        BernieSessionState.proposal_preview,
        BernieSessionState.handed_off,
    }),
}


class SessionTransitionValidation(BaseModel):
    """Typed verdict for a client event against the transition table."""

    model_config = {"frozen": True}

    allowed: bool
    current_state: BernieSessionState
    event_type: BernieSessionEventType
    target_state: Optional[BernieSessionState] = None
    reason_code: Optional[str] = None
    detail: Optional[str] = None


def validate_session_event(
    current_state: BernieSessionState,
    event_type: BernieSessionEventType,
) -> SessionTransitionValidation:
    """Validate a client event against the static transition table.

    Pure function - no session store, no side effects. Returns an allowed
    verdict with the target state, or a typed rejection (the payload a future
    session endpoint returns as a 409).
    """
    if event_type is BernieSessionEventType.new_session:
        return SessionTransitionValidation(
            allowed=True,
            current_state=current_state,
            event_type=event_type,
            target_state=BernieSessionState.instruction_entry,
        )

    if event_type is BernieSessionEventType.diary_navigated:
        if current_state in TRANSIENT_STATES:
            return SessionTransitionValidation(
                allowed=False,
                current_state=current_state,
                event_type=event_type,
                reason_code="event_not_allowed_in_transient_state",
                detail=(
                    f"{current_state.value} is server-owned; diary navigation "
                    "cannot be applied until the turn resolves."
                ),
            )
        return SessionTransitionValidation(
            allowed=True,
            current_state=current_state,
            event_type=event_type,
            target_state=current_state,
        )

    target = CLIENT_EVENT_TRANSITIONS[current_state].get(event_type)
    if target is None:
        reason_code = (
            "event_not_allowed_in_transient_state"
            if current_state in TRANSIENT_STATES
            else "event_not_allowed_in_state"
        )
        return SessionTransitionValidation(
            allowed=False,
            current_state=current_state,
            event_type=event_type,
            reason_code=reason_code,
            detail=(
                f"Event {event_type.value} is not legal from state "
                f"{current_state.value}."
            ),
        )
    return SessionTransitionValidation(
        allowed=True,
        current_state=current_state,
        event_type=event_type,
        target_state=target,
    )


class BernieSessionEvent(BaseModel):
    """One typed event in a Bernie booking session's turn log.

    Shaped to become an event-log row later: flat fields, stored timestamp,
    JSON payload. ``payload`` should carry structured ids/coordinates only;
    ``staff_instruction`` payloads may carry the instruction text and are the
    PHI-retention decision point noted in the module docstring.
    """

    model_config = {"frozen": True}

    event_id: str
    session_id: str
    event_type: BernieSessionEventType
    turn_index: int = Field(ge=0)
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class BernieSessionRecord(BaseModel):
    """Persistence-shaped snapshot of a Bernie booking session.

    Field set mirrors the session memory named by the architecture consult:
    immutable ``request_reference_date``, recognised patient/practitioner ids
    with their confidence bands, candidate freshness ids, the staged proposal
    freshness id, and the turn log. Maps 1:1 onto a future DB row; no ORM,
    no table, no store in this slice.
    """

    session_id: str
    practice_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    state: BernieSessionState = BernieSessionState.instruction_entry
    request_reference_date: Optional[date] = None
    patient_id: Optional[uuid.UUID] = None
    patient_band: Optional[str] = None
    practitioner_id: Optional[uuid.UUID] = None
    practitioner_band: Optional[str] = None
    candidate_freshness_ids: list[str] = Field(default_factory=list)
    staged_proposal_freshness_id: Optional[str] = None
    turn_count: int = Field(default=0, ge=0)
    events: list[BernieSessionEvent] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


__all__ = [
    "BernieSessionState",
    "BernieSessionEventType",
    "BernieSessionEvent",
    "BernieSessionRecord",
    "SessionTransitionValidation",
    "CLIENT_EVENT_TRANSITIONS",
    "SERVER_ADVANCE_TARGETS",
    "TRANSIENT_STATES",
    "TERMINAL_STATES",
    "validate_session_event",
]
