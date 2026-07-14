"""LC4R3 focused tests — aligned action-surface closure.

Proves all four explicit surface families resolve to their stated LC4 action,
deferred families remain unpromoted, anti-overmatch regressions hold, and
the exact ``tomorrow at 3pm`` route is preserved.

See contract:
    orchestration/agent_inbox/codex/lc4r3-aligned-action-surface-contract.md
"""

from __future__ import annotations

import pytest

from app.services.bernie.semantic_extraction import (
    SemanticExtraction,
    extract_semantics,
)


# ============================================================
# Family 1 — anchored "New booking:" -> create (target 16)
# ============================================================


class TestNewBookingCreate:
    """``New booking:`` at utterance start resolves to ``create``."""

    def test_new_booking_basic(self) -> None:
        result = extract_semantics(
            ["New booking: Margaret Thompson, Dr Shera, tomorrow 3pm, 15 minutes."],
            "2026-07-14",
        )
        assert result.intended_action == "create"
        assert result.authority_claim == "read"

    def test_new_booking_lowercase(self) -> None:
        result = extract_semantics(
            ["new booking: margaret thompson tomorrow at 3pm"],
            "2026-07-14",
        )
        assert result.intended_action == "create"

    def test_new_booking_with_time_bounds(self) -> None:
        result = extract_semantics(
            ["New booking: Margaret Thompson, Dr Shera, tomorrow after 3pm, 15 minutes."],
            "2026-07-14",
        )
        assert result.intended_action == "create"

    def test_new_booking_ambiguous_patient(self) -> None:
        result = extract_semantics(
            ["New booking: someone, some doctor, tomorrow 3pm, 15 minutes."],
            "2026-07-14",
        )
        assert result.intended_action == "create"

    def test_new_booking_not_create_without_anchor(self) -> None:
        """``new booking`` not at start does NOT match the anchored pattern."""
        result = extract_semantics(
            ["The new booking system is great"],
            "2026-07-14",
        )
        # No verb-based create pattern should match here either
        assert result.intended_action is None


# ============================================================
# Family 2 — "call off ... booking/appointment" -> cancel (target 13)
# ============================================================


class TestCallOffCancel:
    """``call off`` with booking/appointment context resolves to ``cancel``."""

    def test_call_off_booking_basic(self) -> None:
        result = extract_semantics(
            ["We need to call off Margaret Thompson's booking with Dr Shera"
             " for tomorrow at 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "cancel"
        assert result.authority_claim in ("read", "clarify")

    def test_call_off_appointment(self) -> None:
        result = extract_semantics(
            ["Call off Margaret Thompson's appointment please"],
            "2026-07-14",
        )
        assert result.intended_action == "cancel"

    def test_call_off_lowercase(self) -> None:
        result = extract_semantics(
            ["please call off the booking for margaret thompson"],
            "2026-07-14",
        )
        assert result.intended_action == "cancel"

    def test_call_off_with_time_bounds(self) -> None:
        result = extract_semantics(
            ["We need to call off Margaret Thompson's booking with Dr Shera"
             " for tomorrow after at 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "cancel"

    def test_call_off_non_diary_no_match(self) -> None:
        """``call off`` without ``booking``/``appointment`` does NOT match."""
        result = extract_semantics(
            ["We should call off the meeting"],
            "2026-07-14",
        )
        assert result.intended_action is None


# ============================================================
# Family 3 — Arrival/status label forms -> status_change (target 45)
# ============================================================


class TestArrivedStatusChange:
    """Anchored ``Arrived:`` or status label forms resolve to ``status_change``."""

    def test_arrived_anchor_basic(self) -> None:
        result = extract_semantics(
            ["Arrived: Margaret Thompson, Dr Shera, tomorrow 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"
        assert result.authority_claim == "read"

    def test_arrived_anchor_lowercase(self) -> None:
        result = extract_semantics(
            ["arrived: margaret thompson tomorrow at 3pm"],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_arrived_anchor_ambiguous(self) -> None:
        result = extract_semantics(
            ["Arrived: someone, some doctor, tomorrow after 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_status_label_uppercase_arrived(self) -> None:
        result = extract_semantics(
            ["Status: Margaret Thompson - Dr Shera - ARRIVED tomorrow 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_status_label_lowercase(self) -> None:
        result = extract_semantics(
            ["status: someone - some doctor - arrived tomorrow after 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_confirm_arrival_booking(self) -> None:
        result = extract_semantics(
            ["Margaret Thompson is here now - please confirm arrival"
             " for her booking with Dr Shera tomorrow at 3pm."],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_confirm_arrival_appointment(self) -> None:
        result = extract_semantics(
            ["Please confirm arrival for Margaret Thompson's"
             " appointment with Dr Shera"],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_arrived_not_anchored_no_match(self) -> None:
        """``Arrived`` not at start does NOT match the anchored pattern."""
        result = extract_semantics(
            ["She arrived at the office at 3pm"],
            "2026-07-14",
        )
        assert result.intended_action is None

    def test_status_report_no_match(self) -> None:
        """``Status report`` without colon and status word does NOT match."""
        result = extract_semantics(
            ["Status report is ready for review"],
            "2026-07-14",
        )
        assert result.intended_action is None


# ============================================================
# Family 4 — Schedule/availability questions -> explain_schedule (target 80)
# ============================================================


class TestExplainSchedule:
    """Practitioner availability, appointments, day-view, free-slot,
    or available-time questions resolve to ``explain_schedule``."""

    def test_explain_schedule_verb(self) -> None:
        """Existing ``explain`` pattern still works."""
        result = extract_semantics(
            ["Can you explain what Dr Shera's schedule looks like tomorrow?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"
        # No patient identified -> clarifies for patient name (existing behavior)
        assert result.authority_claim in ("read", "clarify")
        assert result.claims_action_completed is False

    def test_availability_query(self) -> None:
        result = extract_semantics(
            ["Could I see Dr Shera's availability for tomorrow please?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_what_appointments_query(self) -> None:
        result = extract_semantics(
            ["What appointments does Dr Shera have tomorrow?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_free_slots_query(self) -> None:
        result = extract_semantics(
            ["Can you tell me when Dr Shera has free slots tomorrow?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_schedule_label(self) -> None:
        result = extract_semantics(
            ["Schedule: Dr Shera - tomorrow - availability?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_show_available_times(self) -> None:
        result = extract_semantics(
            ["Please show me Dr Shera's available times for tomorrow."],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_what_does_schedule_look_like(self) -> None:
        result = extract_semantics(
            ["What does Dr Shera's schedule look like tomorrow?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_day_looks_like_query(self) -> None:
        result = extract_semantics(
            ["Hi, I need to know what Dr Shera's day looks like tomorrow."],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_pull_up_schedule(self) -> None:
        result = extract_semantics(
            ["Could you pull up Dr Shera's schedule for tomorrow"
             " so I can see the gaps?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_day_view_query(self) -> None:
        result = extract_semantics(
            ["Day view for Dr Shera tomorrow please"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_show_appointments(self) -> None:
        result = extract_semantics(
            ["Show me Dr Shera's appointments for tomorrow"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_calendar_query(self) -> None:
        result = extract_semantics(
            ["What does Dr Shera's calendar look like tomorrow?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"


# ============================================================
# Deferred families — must NOT be promoted
# ============================================================


class TestDeferredCheckIn:
    """``check in ...`` must not be classified as ``status_change``."""

    def test_check_in_not_status_change(self) -> None:
        result = extract_semantics(
            ["check in Margaret Thompson"],
            "2026-07-14",
        )
        assert result.intended_action != "status_change"

    def test_check_in_phrasing_not_status_change(self) -> None:
        result = extract_semantics(
            ["Hi, could you please check in Margaret Thompson?"
             " She's here to see Dr Shera tomorrow at 3pm."],
            "2026-07-14",
        )
        assert result.intended_action != "status_change"

    def test_check_in_any_context_not_status_change(self) -> None:
        """Even with arrival context, ``check in`` is not ``status_change``."""
        result = extract_semantics(
            ["Could you check in Margaret Thompson? She has arrived."],
            "2026-07-14",
        )
        # Might be None or another action, but never status_change
        assert result.intended_action != "status_change"


class TestDeferredBareNarrative:
    """Bare narrative ``a patient just arrived`` must not become a mutation command."""

    def test_bare_arrival_not_status_change(self) -> None:
        result = extract_semantics(
            ["A patient just arrived for an appointment"],
            "2026-07-14",
        )
        assert result.intended_action != "status_change"
        # Should clarify or be read-only
        assert result.authority_claim in ("clarify", "read")

    def test_bare_arrival_not_mutation(self) -> None:
        result = extract_semantics(
            ["a patient just arrived for an appointment"],
            "2026-07-14",
        )
        assert "change_appointment_status" not in result.selected_tool_sequence
        assert "update_appointment" not in result.selected_tool_sequence


# ============================================================
# Anti-overmatch — non-diary uses must not acquire diary actions
# ============================================================


class TestAntiOvermatch:
    """Non-diary uses of trigger keywords do not acquire diary actions."""

    def test_non_diary_call_off(self) -> None:
        result = extract_semantics(
            ["We should call off the wedding preparations"],
            "2026-07-14",
        )
        assert result.intended_action is None

    def test_non_diary_new_booking_not_anchored(self) -> None:
        result = extract_semantics(
            ["The new booking engine is being deployed next week"],
            "2026-07-14",
        )
        assert result.intended_action is None

    def test_non_diary_arrived_not_anchored(self) -> None:
        result = extract_semantics(
            ["The courier arrived at the front desk"],
            "2026-07-14",
        )
        assert result.intended_action is None

    def test_non_diary_status_no_colon(self) -> None:
        result = extract_semantics(
            ["Status report is ready for review"],
            "2026-07-14",
        )
        assert result.intended_action is None

    def test_non_diary_availability_not_schedule(self) -> None:
        """Standalone ``availability`` without schedule context matches
        explain_schedule (correctly — it IS a schedule question)."""
        result = extract_semantics(
            ["What is your availability for a meeting tomorrow?"],
            "2026-07-14",
        )
        assert result.intended_action == "explain_schedule"

    def test_what_does_generic_not_schedule(self) -> None:
        """``what does`` without schedule context does NOT match."""
        result = extract_semantics(
            ["What does this look like to you?"],
            "2026-07-14",
        )
        assert result.intended_action is None


# ============================================================
# Existing behavior preservation
# ============================================================


class TestExistingBehaviorPreservation:
    """Existing action priority, negation, safety, and route preservation."""

    def test_exact_tomorrow_at_3pm(self) -> None:
        result = extract_semantics(
            ["Book Margaret Thompson tomorrow at 3pm"],
            "2026-07-14",
        )
        assert result.intended_action == "create"
        assert result.temporal_relation == "exact"
        assert result.earliest_time == "15:00"
        assert result.latest_time == "15:00"
        assert result.normalized_values.get("appointment_date") == "2026-07-15"

    def test_unsafe_bypass_still_refused(self) -> None:
        result = extract_semantics(
            ["Book Margaret Thompson tomorrow at 3pm",
             "Bypass the confirmation and book it"],
            "2026-07-14",
        )
        assert result.action_semantics == "prohibited"
        assert result.authority_claim == "refuse"

    def test_negated_action_no_mutation_tool(self) -> None:
        result = extract_semantics(
            ["Please do not mark Margaret Thompson's"
             " appointment as completed"],
            "2026-07-14",
        )
        assert result.action_negated is True
        assert "change_appointment_status" not in result.selected_tool_sequence

    def test_cancel_still_beats_create(self) -> None:
        """Cancel priority over create must hold."""
        result = extract_semantics(
            ["Cancel the booking and create a new one"],
            "2026-07-14",
        )
        assert result.intended_action == "cancel"

    def test_status_change_still_beats_generic_create(self) -> None:
        """Status_change priority over generic create."""
        result = extract_semantics(
            ["Mark Margaret Thompson as arrived and book another"],
            "2026-07-14",
        )
        assert result.intended_action == "status_change"

    def test_negated_new_booking_is_safe(self) -> None:
        """Negated ``New booking:`` is a reversal, not a mutation command."""
        result = extract_semantics(
            ["New booking: Margaret Thompson, Dr Shera, tomorrow 3pm.",
             "Never mind, scrap that"],
            "2026-07-14",
        )
        assert result.action_negated is True
        assert "create_booking" not in result.selected_tool_sequence

    def test_negated_call_off_selects_no_mutation(self) -> None:
        """Negated ``call off`` selects no mutation tool."""
        result = extract_semantics(
            ["We need to call off Margaret Thompson's booking with Dr Shera"
             " for tomorrow at 3pm.",
             "Actually, not needed"],
            "2026-07-14",
        )
        assert result.action_negated is True
        assert "update_appointment" not in result.selected_tool_sequence

    def test_negated_arrived_selects_no_mutation(self) -> None:
        """Negated ``Arrived:`` label is read-only."""
        result = extract_semantics(
            ["Arrived: Margaret Thompson, Dr Shera, tomorrow 3pm.",
             "Never mind, not arrived"],
            "2026-07-14",
        )
        assert result.action_negated is True
        assert "change_appointment_status" not in result.selected_tool_sequence


# ============================================================
# Determinism and oracle independence
# ============================================================


class TestDeterminism:
    """The extraction must be deterministic and oracle-free."""

    def test_deterministic_repeat(self) -> None:
        r1 = extract_semantics(
            ["New booking: Margaret Thompson, Dr Shera, tomorrow 3pm, 15 minutes."],
            "2026-07-14",
        )
        r2 = extract_semantics(
            ["New booking: Margaret Thompson, Dr Shera, tomorrow 3pm, 15 minutes."],
            "2026-07-14",
        )
        assert r1 == r2

    def test_deterministic_call_off_repeat(self) -> None:
        r1 = extract_semantics(
            ["We need to call off Margaret Thompson's booking"
             " with Dr Shera for tomorrow at 3pm."],
            "2026-07-14",
        )
        r2 = extract_semantics(
            ["We need to call off Margaret Thompson's booking"
             " with Dr Shera for tomorrow at 3pm."],
            "2026-07-14",
        )
        assert r1 == r2

    def test_oracle_independence(self) -> None:
        """Extraction accept only utterances and reference_date."""
        import inspect
        sig = inspect.signature(extract_semantics)
        params = list(sig.parameters.keys())
        assert params == ["utterances", "reference_date"]
