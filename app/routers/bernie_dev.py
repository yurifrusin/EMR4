"""
Dev-only fixture route for Bernie supervised review payloads.

Gated to ENVIRONMENT=dev only; returns 404 in all other environments.
No appointment writes, no audit rows, no LLM/provider calls.
"""
import uuid
from datetime import date, datetime, time, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import settings
from app.dependencies import get_current_user
from app.models.appointments import BookingChannel
from app.models.tenancy import User
from app.routers.appointments import _bernie_staff_review_payload
from app.schemas.appointments import (
    AppointmentCreateCommand,
    AppointmentCreateProposalOut,
    AppointmentProposalIssue,
    BernieSupervisedBookingOut,
    SlotCandidate,
    SlotSearchCommandResult,
    SlotSearchProposalIn,
    SlotSearchProposalOut,
    SlotSelectionProposalOut,
)


def _require_dev_environment() -> None:
    if settings.environment.lower() != "dev":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


router = APIRouter(
    prefix="/api/v1/appointments/dev",
    tags=["dev"],
    dependencies=[Depends(_require_dev_environment)],
)

# ── Sentinel fixture IDs (clearly non-PHI, deterministic across runs) ─────────

_FX_PRACTITIONER_ID = uuid.UUID("00000000-0000-0000-0000-f17000000001")
_FX_APPT_TYPE_ID = uuid.UUID("00000000-0000-0000-0000-f17000000002")
_FX_LOCATION_ID = uuid.UUID("00000000-0000-0000-0000-f17000000003")
_FX_PATIENT_ID = uuid.UUID("00000000-0000-0000-0000-f17000000004")
_FX_DATE = date(2026, 7, 14)  # fixed Tuesday — stable across test runs


def _issue(code: str, severity: Literal["warning", "blocked"], message: str) -> AppointmentProposalIssue:
    return AppointmentProposalIssue(code=code, severity=severity, message=message)


def _build_normalization(safe: bool = True) -> SlotSearchCommandResult:
    if not safe:
        block = _issue(
            "missing_practitioner_id",
            "blocked",
            "practitioner_id is required to search slots.",
        )
        return SlotSearchCommandResult(
            safe=False,
            constraint=None,
            blocks=[block],
            warnings=[],
            summary="Slot-search command blocked: practitioner_id is required to search slots.",
        )
    return SlotSearchCommandResult(
        safe=True,
        constraint=SlotSearchProposalIn(
            practitioner_id=_FX_PRACTITIONER_ID,
            date_from=_FX_DATE,
            date_to=_FX_DATE,
            duration_minutes=15,
            appointment_type_id=_FX_APPT_TYPE_ID,
            location_id=_FX_LOCATION_ID,
        ),
        warnings=[],
        blocks=[],
        summary="Slot-search command normalised. Ready to search.",
    )


def _build_candidates() -> list[SlotCandidate]:
    return [
        SlotCandidate(
            appointment_date=_FX_DATE,
            start_time=datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 7, 13, 23, 15, tzinfo=timezone.utc),
            start_time_local=time(9, 0),
            duration_minutes=15,
        ),
        SlotCandidate(
            appointment_date=_FX_DATE,
            start_time=datetime(2026, 7, 13, 23, 15, tzinfo=timezone.utc),
            end_time=datetime(2026, 7, 13, 23, 30, tzinfo=timezone.utc),
            start_time_local=time(9, 15),
            duration_minutes=15,
        ),
        SlotCandidate(
            appointment_date=_FX_DATE,
            start_time=datetime(2026, 7, 14, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 7, 14, 0, 15, tzinfo=timezone.utc),
            start_time_local=time(10, 0),
            duration_minutes=15,
            warnings=[_issue("break_overlap", "warning", "Slot overlaps with the morning tea break.")],
        ),
    ]


def _build_search_proposal() -> SlotSearchProposalOut:
    return SlotSearchProposalOut(
        safe=True,
        requires_confirmation=False,
        autonomy_tier="execute_with_report",
        summary="Found 3 candidate slots on 2026-07-14.",
        resolved_duration_minutes=15,
        candidates=_build_candidates(),
        warnings=[],
        blocks=[],
    )


def _fixture_blocked() -> BernieSupervisedBookingOut:
    normalization = _build_normalization(safe=False)
    staff_review = _bernie_staff_review_payload(
        result="blocked",
        summary=normalization.summary,
        warnings=[],
        blocks=normalization.blocks,
    )
    return BernieSupervisedBookingOut(
        result="blocked",
        safe=False,
        requires_confirmation=False,
        autonomy_tier="blocked",
        summary=normalization.summary,
        normalization=normalization,
        staff_review=staff_review,
        blocks=normalization.blocks,
        warnings=[],
    )


def _fixture_candidate_selection_required() -> BernieSupervisedBookingOut:
    normalization = _build_normalization()
    search_proposal = _build_search_proposal()
    summary = (
        "Slot-search command normalised. Found 3 candidate slots on 2026-07-14."
        " Select one candidate before preparing create-proposal evidence."
    )
    staff_review = _bernie_staff_review_payload(
        result="candidate_selection_required",
        summary=summary,
        warnings=[],
        blocks=[],
        search_proposal=search_proposal,
    )
    return BernieSupervisedBookingOut(
        result="candidate_selection_required",
        safe=True,
        requires_confirmation=False,
        autonomy_tier="execute_with_report",
        summary=summary,
        normalization=normalization,
        search_proposal=search_proposal,
        staff_review=staff_review,
        blocks=[],
        warnings=[],
    )


def _fixture_confirmation_ready() -> BernieSupervisedBookingOut:
    normalization = _build_normalization()
    search_proposal = _build_search_proposal()
    selected = search_proposal.candidates[0]

    create_command = AppointmentCreateCommand(
        patient_id=_FX_PATIENT_ID,
        practitioner_id=_FX_PRACTITIONER_ID,
        appointment_type_id=_FX_APPT_TYPE_ID,
        location_id=_FX_LOCATION_ID,
        appointment_date=selected.appointment_date,
        start_time_local=selected.start_time_local,
        start_time=selected.start_time,
        duration_minutes=selected.duration_minutes,
        reason="Routine GP consultation (fixture)",
        booked_via=BookingChannel.Receptionist,
    )
    create_proposal = AppointmentCreateProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Create-proposal evidence ready for staff confirmation.",
        command=create_command,
        patient_identity="linked",
    )
    selection_proposal = SlotSelectionProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Slot selected. Create-proposal evidence attached.",
        selected_candidate=selected,
        create_proposal=create_proposal,
    )
    summary = "Slot selected. Create-proposal evidence ready for staff confirmation."
    staff_review = _bernie_staff_review_payload(
        result="confirmation_ready",
        summary=summary,
        warnings=[],
        blocks=[],
        selection_proposal=selection_proposal,
    )
    return BernieSupervisedBookingOut(
        result="confirmation_ready",
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary=summary,
        normalization=normalization,
        search_proposal=search_proposal,
        selection_proposal=selection_proposal,
        staff_review=staff_review,
        blocks=[],
        warnings=[],
    )


# Built once at import time — all values are static Pydantic model instances.
_ALL_FIXTURES: dict[str, BernieSupervisedBookingOut] = {
    "blocked": _fixture_blocked(),
    "candidate_selection_required": _fixture_candidate_selection_required(),
    "confirmation_ready": _fixture_confirmation_ready(),
}

_VALID_STATES = Literal["blocked", "candidate_selection_required", "confirmation_ready"]


@router.get(
    "/bernie-review-fixtures",
    response_model=dict[str, BernieSupervisedBookingOut],
)
def bernie_review_fixtures(
    state: Optional[_VALID_STATES] = Query(
        default=None,
        description="Filter to a single review state. Omit to return all three.",
    ),
    current_user: User = Depends(get_current_user),
):
    """Return deterministic non-PHI Bernie supervised-review fixture payloads.

    Dev-gated (ENVIRONMENT=dev only). No appointment writes, no audit rows,
    no LLM/provider calls. Default returns all three states keyed by name;
    supply ?state= to return a single state's fixture.
    """
    if state is not None:
        return {state: _ALL_FIXTURES[state]}
    return _ALL_FIXTURES
