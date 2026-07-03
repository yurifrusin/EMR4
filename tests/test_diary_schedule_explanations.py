"""Sprint N2 diary schedule-explanation invariant tests."""

from datetime import date

import app.services.bernie as bernie_domain
import app.services.bernie.schedule_explanations as bernie_schedule
import app.services.diary as diary_domain
import app.services.diary.schedule_explanations as diary_schedule
from app.services.diary import (
    DIARY_SCHEDULE_COPY_CATALOG,
    DIARY_SCHEDULE_REASON_ALIASES,
    DiaryScheduleExplanationReason,
    DiaryScheduleExplanationEvidence,
    BernieReceptionContextFrameSet,
    BernieRosterScheduleFrame,
    BernieSlotSearchFrame,
    evaluate_reception_context,
    explain_schedule,
    get_schedule_copy,
    parse_schedule_explanation_reason,
)


REFERENCE_DATE = date(2026, 7, 3)


def _frame_set(*frames):
    return BernieReceptionContextFrameSet(
        reference_date=REFERENCE_DATE,
        frames=list(frames),
    )


def test_schedule_reason_catalog_covers_required_no_slot_states():
    expected = {
        "no_roster_row",
        "practitioner_unavailable",
        "outside_request_window",
        "breaks_only_window",
        "fully_booked",
        "same_day_window_elapsed",
        "searched_no_candidates",
    }

    assert {reason.value for reason in DiaryScheduleExplanationReason} == expected
    assert {reason.value for reason in DIARY_SCHEDULE_COPY_CATALOG} == expected


def test_every_schedule_reason_has_copy_keyed_by_reason_code():
    seen_titles = set()

    for reason in DiaryScheduleExplanationReason:
        copy = get_schedule_copy(reason)

        assert copy.reason_code is reason
        assert copy.title
        assert copy.staff_prompt
        assert copy.title not in seen_titles
        seen_titles.add(copy.title)


def test_schedule_reason_parser_ignores_non_schedule_codes():
    assert parse_schedule_explanation_reason("fully_booked") is DiaryScheduleExplanationReason.fully_booked
    assert parse_schedule_explanation_reason("no_slot_candidates") is (
        DiaryScheduleExplanationReason.searched_no_candidates
    )
    assert parse_schedule_explanation_reason("clinic_day_exhausted") is (
        DiaryScheduleExplanationReason.same_day_window_elapsed
    )
    assert parse_schedule_explanation_reason("patient_identity_required") is None
    assert parse_schedule_explanation_reason(None) is None


def test_legacy_reason_aliases_point_to_catalog_entries():
    assert DIARY_SCHEDULE_REASON_ALIASES

    for typed_reason in DIARY_SCHEDULE_REASON_ALIASES.values():
        assert typed_reason in DIARY_SCHEDULE_COPY_CATALOG


def test_roster_schedule_reasons_do_not_become_searched_no_candidates():
    for reason in (
        DiaryScheduleExplanationReason.no_roster_row,
        DiaryScheduleExplanationReason.practitioner_unavailable,
        DiaryScheduleExplanationReason.outside_request_window,
        DiaryScheduleExplanationReason.breaks_only_window,
        DiaryScheduleExplanationReason.fully_booked,
        DiaryScheduleExplanationReason.same_day_window_elapsed,
    ):
        decision = evaluate_reception_context(
            _frame_set(
                BernieRosterScheduleFrame(
                    status="unavailable",
                    reason_code=reason.value,
                    basis=f"Schedule explanation: {reason.value}.",
                    reference_date=REFERENCE_DATE,
                )
            )
        )

        assert decision.availability == "roster_unavailable"
        assert decision.roster_unavailable is True
        assert decision.search_ran_no_candidates is False
        assert decision.can_search_slots is False
        assert decision.schedule_reason_codes == [reason.value]


def test_true_searched_no_candidates_requires_slot_search_frame():
    decision = evaluate_reception_context(
        _frame_set(
            BernieRosterScheduleFrame(
                status="available",
                basis="Roster is available and the slot search ran.",
                reference_date=REFERENCE_DATE,
            ),
            BernieSlotSearchFrame(
                status="searched_no_candidates",
                reason_code=DiaryScheduleExplanationReason.searched_no_candidates.value,
                basis="Search completed with zero candidates.",
                reference_date=REFERENCE_DATE,
                candidate_count=0,
            ),
        )
    )

    assert decision.availability == "search_ran_no_candidates"
    assert decision.roster_unavailable is False
    assert decision.search_ran_no_candidates is True
    assert decision.schedule_reason_codes == ["searched_no_candidates"]


def test_explain_schedule_returns_structural_reasons_before_no_candidates():
    explanation = explain_schedule(
        DiaryScheduleExplanationEvidence(
            reference_date="2026-07-03",
            has_roster_row=False,
            search_ran=True,
            candidate_count=0,
            basis="No roster row exists.",
        )
    )

    assert explanation is not None
    assert explanation.reason_code is DiaryScheduleExplanationReason.no_roster_row


def test_explain_schedule_classifies_each_schedule_state():
    cases = [
        (
            DiaryScheduleExplanationEvidence(reference_date="2026-07-03", has_roster_row=False),
            DiaryScheduleExplanationReason.no_roster_row,
        ),
        (
            DiaryScheduleExplanationEvidence(reference_date="2026-07-03", practitioner_working=False),
            DiaryScheduleExplanationReason.practitioner_unavailable,
        ),
        (
            DiaryScheduleExplanationEvidence(
                reference_date="2026-07-03",
                same_day_window_kind="window_fully_past",
            ),
            DiaryScheduleExplanationReason.same_day_window_elapsed,
        ),
        (
            DiaryScheduleExplanationEvidence(reference_date="2026-07-03", within_request_window=False),
            DiaryScheduleExplanationReason.outside_request_window,
        ),
        (
            DiaryScheduleExplanationEvidence(reference_date="2026-07-03", window_is_breaks_only=True),
            DiaryScheduleExplanationReason.breaks_only_window,
        ),
        (
            DiaryScheduleExplanationEvidence(reference_date="2026-07-03", any_free_capacity=False),
            DiaryScheduleExplanationReason.fully_booked,
        ),
        (
            DiaryScheduleExplanationEvidence(
                reference_date="2026-07-03",
                search_ran=True,
                candidate_count=0,
            ),
            DiaryScheduleExplanationReason.searched_no_candidates,
        ),
    ]

    for evidence, expected_reason in cases:
        explanation = explain_schedule(evidence)

        assert explanation is not None
        assert explanation.reason_code is expected_reason


def test_explain_schedule_does_not_create_false_no_slot_without_search():
    assert explain_schedule(
        DiaryScheduleExplanationEvidence(
            reference_date="2026-07-03",
            search_ran=False,
            candidate_count=0,
        )
    ) is None


def test_bernie_facade_reexports_schedule_explanation_contracts():
    assert bernie_domain.DiaryScheduleExplanationReason is diary_domain.DiaryScheduleExplanationReason
    assert bernie_domain.DiaryScheduleExplanation is diary_domain.DiaryScheduleExplanation
    assert bernie_domain.DiaryScheduleExplanationEvidence is diary_domain.DiaryScheduleExplanationEvidence
    assert bernie_domain.DIARY_SCHEDULE_COPY_CATALOG is diary_domain.DIARY_SCHEDULE_COPY_CATALOG
    assert bernie_domain.DIARY_SCHEDULE_REASON_ALIASES is diary_domain.DIARY_SCHEDULE_REASON_ALIASES
    assert bernie_domain.explain_schedule is diary_domain.explain_schedule
    assert bernie_domain.get_schedule_copy is diary_domain.get_schedule_copy
    assert bernie_domain.parse_schedule_explanation_reason is diary_domain.parse_schedule_explanation_reason
    assert bernie_schedule.DiaryScheduleExplanationReason is diary_schedule.DiaryScheduleExplanationReason
    assert bernie_schedule.DIARY_SCHEDULE_COPY_CATALOG is diary_schedule.DIARY_SCHEDULE_COPY_CATALOG
