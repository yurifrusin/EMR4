"""Sprint D5 route-builder search_horizon threading tests.

Verifies that _build_bernie_reception_context correctly derives and threads
search_horizon into BernieSlotSearchFrame for searched_with_candidates and
searched_no_candidates frames only.  Policy and outcome semantics must remain
unchanged: a real searched_no_candidates result stays no_matching_times
regardless of horizon (Ariadne amendment; also tested in D4 suite).
"""

from datetime import date, datetime, timezone
import uuid

import pytest

from app.routers.appointments import (
    _build_bernie_reception_context,
    _derive_search_horizon,
)
from app.schemas.appointments import (
    AppointmentProposalIssue,
    SlotCandidate,
    SlotSearchCommandResult,
    SlotSearchProposalIn,
    SlotSearchProposalOut,
)
from app.services.diary.frames import BernieSlotSearchFrame
from app.services.diary.outcomes import BernieBookingOutcomeKind, classify_booking_outcome
from app.services.diary.policy import evaluate_reception_context


REFERENCE_DATE = date(2026, 7, 4)
ADVANCE_DATE = date(2026, 7, 7)
PAST_DATE = date(2026, 7, 1)
_PRACTITIONER_ID = uuid.uuid4()


# _derive_search_horizon unit tests

def _normalization(date_from: date) -> SlotSearchCommandResult:
    return SlotSearchCommandResult(
        safe=True,
        constraint=SlotSearchProposalIn(
            practitioner_id=_PRACTITIONER_ID,
            date_from=date_from,
        ),
        summary="normalized",
    )


def test_derive_horizon_same_day():
    assert _derive_search_horizon(REFERENCE_DATE, _normalization(REFERENCE_DATE)) == "same_day"


def test_derive_horizon_advance():
    assert _derive_search_horizon(REFERENCE_DATE, _normalization(ADVANCE_DATE)) == "advance"


def test_derive_horizon_past_returns_none():
    assert _derive_search_horizon(REFERENCE_DATE, _normalization(PAST_DATE)) is None


def test_derive_horizon_no_normalization_returns_none():
    assert _derive_search_horizon(REFERENCE_DATE, None) is None


def test_derive_horizon_no_constraint_returns_none():
    norm = SlotSearchCommandResult(safe=False, constraint=None, summary="blocked")
    assert _derive_search_horizon(REFERENCE_DATE, norm) is None


# _build_bernie_reception_context frame-level tests

def _empty_proposal(*, candidates=None) -> SlotSearchProposalOut:
    return SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="No candidates.",
        candidates=candidates or [],
    )


def _candidate() -> SlotCandidate:
    dt = datetime(2026, 7, 4, 9, 0, tzinfo=timezone.utc)
    return SlotCandidate(
        appointment_date=REFERENCE_DATE,
        start_time=dt,
        end_time=datetime(2026, 7, 4, 9, 15, tzinfo=timezone.utc),
        start_time_local=dt.time(),
        duration_minutes=15,
    )


def _slot_frame(frame_set) -> BernieSlotSearchFrame:
    frame = frame_set.first_frame("slot_search")
    assert frame is not None
    assert isinstance(frame, BernieSlotSearchFrame)
    return frame


def test_searched_no_candidates_same_day_horizon():
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(REFERENCE_DATE),
        search_proposal=_empty_proposal(),
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "searched_no_candidates"
    assert frame.search_horizon == "same_day"


def test_searched_no_candidates_advance_horizon():
    norm = _normalization(ADVANCE_DATE)
    proposal = SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="Advance search, no candidates.",
        candidates=[],
    )
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=norm,
        search_proposal=proposal,
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "searched_no_candidates"
    assert frame.search_horizon == "advance"


def test_searched_no_candidates_missing_normalization_horizon_is_none():
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=None,
        search_proposal=_empty_proposal(),
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "searched_no_candidates"
    assert frame.search_horizon is None


def test_searched_with_candidates_same_day_horizon():
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(REFERENCE_DATE),
        search_proposal=_empty_proposal(candidates=[_candidate()]),
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "searched_with_candidates"
    assert frame.search_horizon == "same_day"


def test_searched_with_candidates_advance_horizon():
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(ADVANCE_DATE),
        search_proposal=_empty_proposal(candidates=[_candidate()]),
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "searched_with_candidates"
    assert frame.search_horizon == "advance"


def test_not_run_frame_horizon_is_none():
    """not_run frames (no schedule) must not receive a search_horizon tag."""
    schedule_warning = AppointmentProposalIssue(
        code="no_practitioner_schedule",
        severity="warning",
        message="No schedule found.",
    )
    proposal = SlotSearchProposalOut(
        safe=True,
        autonomy_tier="execute_with_report",
        summary="No schedule.",
        candidates=[],
        warnings=[schedule_warning],
    )
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(REFERENCE_DATE),
        search_proposal=proposal,
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "not_run"
    assert frame.search_horizon is None


def test_blocked_frame_horizon_is_none():
    """blocked frames (unsafe proposal) must not receive a search_horizon tag."""
    proposal = SlotSearchProposalOut(
        safe=False,
        autonomy_tier="blocked",
        summary="Blocked.",
        candidates=[],
        blocks=[AppointmentProposalIssue(code="slot_search_blocked", severity="blocked", message="Blocked.")],
    )
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(REFERENCE_DATE),
        search_proposal=proposal,
        search_ran=True,
    )
    frame = _slot_frame(fs)
    assert frame.status == "blocked"
    assert frame.search_horizon is None


# Outcome-semantics unchanged

@pytest.mark.parametrize(
    "target_date,expected_horizon",
    [
        (REFERENCE_DATE, "same_day"),
        (ADVANCE_DATE, "advance"),
        (PAST_DATE, None),  # past date -> None horizon; normalization still safe
    ],
)
def test_searched_no_candidates_stays_no_matching_times_regardless_of_horizon(
    target_date, expected_horizon
):
    """Ariadne amendment: genuine searched_no_candidates -> no_matching_times always."""
    fs = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(target_date),
        search_proposal=_empty_proposal(),
        search_ran=True,
    )

    slot_frame = _slot_frame(fs)
    assert slot_frame.status == "searched_no_candidates"
    assert slot_frame.search_horizon == expected_horizon

    policy = evaluate_reception_context(fs)
    assert policy.search_ran_no_candidates is True

    outcome = classify_booking_outcome(policy)
    assert outcome.kind == BernieBookingOutcomeKind.no_matching_times
    assert outcome.family == "no_availability"


def test_search_horizon_not_read_by_policy():
    """Policy predicates are identical for same_day vs advance searched_no_candidates."""
    fs_same = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(REFERENCE_DATE),
        search_proposal=_empty_proposal(),
        search_ran=True,
    )
    fs_adv = _build_bernie_reception_context(
        reference_date=REFERENCE_DATE,
        normalization=_normalization(ADVANCE_DATE),
        search_proposal=_empty_proposal(),
        search_ran=True,
    )
    p_same = evaluate_reception_context(fs_same)
    p_adv = evaluate_reception_context(fs_adv)

    assert p_same.availability == p_adv.availability
    assert p_same.search_ran_no_candidates == p_adv.search_ran_no_candidates
    assert p_same.schedule_reason_codes == p_adv.schedule_reason_codes
