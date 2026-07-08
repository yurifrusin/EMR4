from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, Optional

from pydantic import BaseModel, Field

from app.schemas.appointments import BernieSessionSnapshotOut
from app.services.bernie.session import BernieSessionState


class NodeSource(str, Enum):
    server_snapshot = "server_snapshot"
    client_transient = "client_transient"
    derived = "derived"


class ConfirmationState(str, Enum):
    not_applicable = "not_applicable"
    required = "required"
    ready = "ready"
    pressed = "pressed"
    awaiting_backend = "awaiting_backend"
    confirmed = "confirmed"
    failed = "failed"
    stale = "stale"
    blocked = "blocked"


class ClientConfirmationRequestState(str, Enum):
    idle = "idle"
    pressed = "pressed"
    awaiting_backend = "awaiting_backend"
    failed = "failed"


class NodeValue(BaseModel):
    value: str
    source: NodeSource


class BernieUiFlags(BaseModel):
    show_clarification_prompt: bool = False
    show_candidate_slots: bool = False
    show_no_slot_suggestions: bool = False
    show_pending_proposal_card: bool = False
    show_confirm_button: bool = False
    enable_confirm_button: bool = False
    show_choose_another_time: bool = False
    show_identity_verification_panel: bool = False
    show_success_copy: bool = False
    show_stale_warning: bool = False
    show_retry_action: bool = False
    show_edit_action: bool = False
    show_technical_details: bool = False


class BernieUiViewModel(BaseModel):
    schema_version: str = "bernie.ui_view_model.v1"
    session_phase: NodeValue
    clarification_state: NodeValue
    candidate_state: NodeValue
    proposal_state: NodeValue
    confirmation_state: NodeValue
    freshness_state: NodeValue
    identity_state: NodeValue
    copy_mode: NodeValue
    flags: BernieUiFlags
    primary_copy: str
    secondary_copy: Optional[str] = None


def build_bernie_ui_view_model(
    snapshot: BernieSessionSnapshotOut | Mapping[str, Any],
    *,
    client_confirmation_request_state: ClientConfirmationRequestState | str = (
        ClientConfirmationRequestState.idle
    ),
) -> BernieUiViewModel:
    """Project a Bernie session snapshot into display-only UI state.

    This is pure display logic. It does not authorize writes, call AI adapters,
    read databases, or emit command payload fields.
    """

    parsed = _coerce_snapshot(snapshot)
    request_state = _coerce_request_state(client_confirmation_request_state)
    state = _coerce_session_state(parsed.state)

    freshness = "stale" if parsed.stale_reason_code else "fresh"
    identity = _identity_state(parsed)
    candidate = _candidate_state(parsed, state)
    proposal = _proposal_state(parsed, state, freshness, identity)
    clarification = _clarification_state(state, identity)
    confirmation = _confirmation_state(
        state=state,
        proposal_state=proposal,
        freshness=freshness,
        identity_state=identity,
        request_state=request_state,
    )
    copy_mode = _copy_mode(confirmation, clarification, candidate, proposal, freshness)
    flags = _flags(
        confirmation_state=confirmation,
        clarification_state=clarification,
        candidate_state=candidate,
        proposal_state=proposal,
        freshness_state=freshness,
        identity_state=identity,
    )

    return BernieUiViewModel(
        session_phase=NodeValue(value=state.value, source=NodeSource.server_snapshot),
        clarification_state=NodeValue(value=clarification, source=NodeSource.derived),
        candidate_state=NodeValue(value=candidate, source=NodeSource.derived),
        proposal_state=NodeValue(value=proposal, source=NodeSource.derived),
        confirmation_state=NodeValue(
            value=confirmation.value,
            source=(
                NodeSource.server_snapshot
                if confirmation is ConfirmationState.confirmed
                else NodeSource.derived
            ),
        ),
        freshness_state=NodeValue(value=freshness, source=NodeSource.derived),
        identity_state=NodeValue(value=identity, source=NodeSource.derived),
        copy_mode=NodeValue(value=copy_mode, source=NodeSource.derived),
        flags=flags,
        primary_copy=_primary_copy(copy_mode),
        secondary_copy=_secondary_copy(copy_mode),
    )


def _coerce_snapshot(snapshot: BernieSessionSnapshotOut | Mapping[str, Any]) -> BernieSessionSnapshotOut:
    if isinstance(snapshot, BernieSessionSnapshotOut):
        return snapshot
    try:
        return BernieSessionSnapshotOut.model_validate(snapshot)
    except Exception as exc:
        raise ValueError("Invalid BernieSessionSnapshotOut input") from exc


def _coerce_session_state(raw_state: str) -> BernieSessionState:
    try:
        return BernieSessionState(raw_state)
    except ValueError as exc:
        raise ValueError(f"Unknown Bernie session state: {raw_state!r}") from exc


def _coerce_request_state(raw_state: ClientConfirmationRequestState | str) -> ClientConfirmationRequestState:
    try:
        return ClientConfirmationRequestState(raw_state)
    except ValueError as exc:
        raise ValueError(f"Unknown client confirmation request state: {raw_state!r}") from exc


def _identity_state(snapshot: BernieSessionSnapshotOut) -> str:
    bands = {snapshot.patient_band, snapshot.practitioner_band}
    if "ambiguous" in bands:
        return "ambiguous"
    if snapshot.patient_id and snapshot.practitioner_id:
        return "recognized"
    if snapshot.patient_id or snapshot.practitioner_id:
        return "partial"
    return "absent"


def _candidate_state(snapshot: BernieSessionSnapshotOut, state: BernieSessionState) -> str:
    if state is BernieSessionState.no_slot:
        return "empty_after_search"
    if snapshot.candidate_freshness_ids:
        return "available"
    return "absent"


def _proposal_state(
    snapshot: BernieSessionSnapshotOut,
    state: BernieSessionState,
    freshness: str,
    identity: str,
) -> str:
    if state is BernieSessionState.confirmed:
        return "confirmed"
    if state in {BernieSessionState.proposal_preview, BernieSessionState.confirmation}:
        if identity in {"absent", "ambiguous", "partial"}:
            return "blocked"
        if freshness == "stale":
            return "stale"
        if snapshot.staged_proposal_freshness_id:
            return "ready"
        return "staged"
    return "absent"


def _clarification_state(state: BernieSessionState, identity: str) -> str:
    if state is BernieSessionState.clarification:
        return "required"
    if identity == "ambiguous":
        return "identity_ambiguous"
    return "none"


def _confirmation_state(
    *,
    state: BernieSessionState,
    proposal_state: str,
    freshness: str,
    identity_state: str,
    request_state: ClientConfirmationRequestState,
) -> ConfirmationState:
    if state is BernieSessionState.confirmed:
        return ConfirmationState.confirmed
    if identity_state == "ambiguous" or proposal_state == "blocked":
        return ConfirmationState.blocked
    if freshness == "stale" or proposal_state == "stale":
        return ConfirmationState.stale
    if request_state is ClientConfirmationRequestState.failed:
        return ConfirmationState.failed
    if request_state is ClientConfirmationRequestState.awaiting_backend:
        return ConfirmationState.awaiting_backend
    if request_state is ClientConfirmationRequestState.pressed:
        return ConfirmationState.pressed
    if proposal_state == "ready":
        return ConfirmationState.ready
    if proposal_state == "staged":
        return ConfirmationState.required
    return ConfirmationState.not_applicable


def _copy_mode(
    confirmation: ConfirmationState,
    clarification: str,
    candidate: str,
    proposal: str,
    freshness: str,
) -> str:
    if confirmation is ConfirmationState.confirmed:
        return "success"
    if confirmation in {ConfirmationState.failed, ConfirmationState.stale} or freshness == "stale":
        return "stale_or_retry"
    if confirmation in {ConfirmationState.ready, ConfirmationState.pressed, ConfirmationState.awaiting_backend}:
        return "not_booked_yet"
    if confirmation is ConfirmationState.blocked or proposal == "blocked":
        return "blocked"
    if clarification != "none":
        return "ask"
    if candidate == "available":
        return "offer"
    if candidate == "empty_after_search":
        return "no_slots"
    return "technical_details_only"


def _flags(
    *,
    confirmation_state: ConfirmationState,
    clarification_state: str,
    candidate_state: str,
    proposal_state: str,
    freshness_state: str,
    identity_state: str,
) -> BernieUiFlags:
    terminal = {ConfirmationState.awaiting_backend, ConfirmationState.confirmed}
    show_candidates = candidate_state == "available" and confirmation_state not in terminal
    show_proposal = proposal_state in {"staged", "ready", "stale", "blocked"}
    show_confirm = confirmation_state is ConfirmationState.ready and freshness_state == "fresh"
    return BernieUiFlags(
        show_clarification_prompt=clarification_state in {"required", "identity_ambiguous"},
        show_candidate_slots=show_candidates,
        show_no_slot_suggestions=candidate_state == "empty_after_search",
        show_pending_proposal_card=show_proposal,
        show_confirm_button=show_confirm,
        enable_confirm_button=show_confirm,
        show_choose_another_time=show_candidates and proposal_state in {"staged", "ready", "stale"},
        show_identity_verification_panel=identity_state in {"ambiguous", "recognized", "partial"}
        and confirmation_state is not ConfirmationState.confirmed,
        show_success_copy=confirmation_state is ConfirmationState.confirmed,
        show_stale_warning=freshness_state == "stale"
        or confirmation_state in {ConfirmationState.stale, ConfirmationState.failed},
        show_retry_action=confirmation_state in {ConfirmationState.failed, ConfirmationState.stale},
        show_edit_action=confirmation_state in {ConfirmationState.failed, ConfirmationState.stale},
        show_technical_details=confirmation_state is ConfirmationState.blocked,
    )


def _primary_copy(copy_mode: str) -> str:
    return {
        "ask": "Bernie needs one more detail before offering times.",
        "offer": "Bernie found candidate times for staff review.",
        "no_slots": "Bernie did not find a suitable time in that window.",
        "not_booked_yet": "No appointment has been made yet. Staff review and backend checks are still required.",
        "success": "Appointment booked after backend confirmation.",
        "stale_or_retry": "This proposal needs refresh or retry before booking.",
        "blocked": "Bernie cannot continue until the blocking detail is resolved.",
        "technical_details_only": "Bernie is waiting for the next session event.",
    }[copy_mode]


def _secondary_copy(copy_mode: str) -> Optional[str]:
    if copy_mode == "not_booked_yet":
        return "Confirm uses the existing signed REST command; this display state is not write authority."
    if copy_mode == "success":
        return "Success copy is shown only for a backend-confirmed session."
    if copy_mode == "stale_or_retry":
        return "Choose another time, refresh, or retry before confirming."
    return None
