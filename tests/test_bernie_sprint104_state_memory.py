"""Sprint 104 Bernie conversational-state invariant harness.

These tests are intentionally implementation-neutral. They encode the state
contracts that Claude's backend work and Antigravity's Diary UI work must
satisfy without this Codex worker owning those production surfaces.
"""

from copy import deepcopy
from datetime import datetime, timezone

import pytest


@pytest.fixture(autouse=True)
def clean_db():
    """This pure state harness must not spin up the shared Postgres fixtures."""

    yield


DOWNSTREAM_STATE_KEYS = (
    "command_snapshot",
    "patient_booking_context",
    "candidate_snapshot",
    "selected_candidate",
    "proposal",
)


def _base_session():
    return {
        "session_id": "bernie-session-104",
        "request_reference_date": "2026-07-15",
        "visible_diary_date": "2026-07-15",
        "turn_history": [
            {
                "turn_id": "turn-1",
                "actor": "staff",
                "text": "Book Margaret Thompson with Dr Shera after 3 today",
                "kind": "instruction",
            }
        ],
        "active_turn_id": "turn-1",
        "original_request_text": "Book Margaret Thompson with Dr Shera after 3 today",
        "command_snapshot": {
            "turn_id": "turn-1",
            "date_from": "2026-07-15",
            "practitioner_id": "practitioner-shera",
            "patient_id": "patient-margaret",
        },
        "patient_booking_context": {
            "context_id": "patient-context-1",
            "patient_id": "patient-margaret",
            "turn_id": "turn-1",
            "generated_at": "2026-07-15T10:02:00Z",
        },
        "candidate_snapshot": {
            "snapshot_id": "candidate-snapshot-1",
            "session_id": "bernie-session-104",
            "turn_id": "turn-1",
            "context_id": "patient-context-1",
            "candidates": [
                {
                    "candidate_id": "slot-1515",
                    "appointment_date": "2026-07-15",
                    "start_time": "15:15",
                    "end_time": "15:30",
                }
            ],
        },
        "selected_candidate": {"candidate_id": "slot-1515"},
        "proposal": {
            "proposal_id": "proposal-1",
            "session_id": "bernie-session-104",
            "turn_id": "turn-1",
            "candidate_snapshot_id": "candidate-snapshot-1",
            "candidate_id": "slot-1515",
            "fresh": True,
        },
        "state": "slot_preview",
    }


def _append_staff_turn(session, *, text, kind="instruction"):
    next_session = deepcopy(session)
    new_turn_id = f"turn-{len(next_session['turn_history']) + 1}"
    next_session["turn_history"].append(
        {
            "turn_id": new_turn_id,
            "actor": "staff",
            "text": text,
            "kind": kind,
        }
    )
    next_session["active_turn_id"] = new_turn_id

    if kind == "instruction":
        for key in DOWNSTREAM_STATE_KEYS:
            next_session[key] = None
        next_session["state"] = "interpreting"
        next_session["stale_reason"] = "new_staff_instruction"
    elif kind == "clarification":
        next_session["state"] = "context_enrichment"
        next_session["clarifies_turn_id"] = session["active_turn_id"]

    return next_session


def _mark_navigation_stale(session, *, visible_diary_date, event):
    next_session = deepcopy(session)
    next_session["visible_diary_date"] = visible_diary_date
    next_session["state"] = "stale_context"
    next_session["stale_reason"] = event
    next_session["candidate_snapshot"]["fresh"] = False
    next_session["proposal"]["fresh"] = False
    next_session["selected_candidate"] = None
    return next_session


def _build_patient_booking_context(recognition):
    if recognition["status"] != "recognised":
        return {
            "state": "patient_recognition_needed",
            "patient_booking_context": None,
            "clarifying_question": "Which Margaret do you mean?",
        }

    return {
        "state": "patient_context_ready",
        "patient_booking_context": {
            "type": "patient_booking_context",
            "context_id": f"context-{recognition['patient_id']}",
            "patient_id": recognition["patient_id"],
            "generated_at": "2026-07-15T10:03:00Z",
            "lookback_days": 90,
            "lookahead_days": 60,
            "recent_bookings": [],
            "future_bookings": [
                {
                    "appointment_id": "future-follow-up-1",
                    "appointment_date": "2026-07-22",
                    "practitioner_label": "Dr Shera",
                    "purpose_label": "follow-up",
                }
            ],
            "derived_signals": ["has_future_follow_up"],
            "fresh_for_turn_id": recognition["turn_id"],
            "source": "deterministic_patient_context",
        },
    }


def _no_slot_response():
    return {
        "state": "no_slots",
        "result": "no_slots",
        "candidates": [],
        "message": "I could not find a free time in that window.",
        "suggestions": [
            {
                "label": "Try the next available time today",
                "event": "NO_SLOT_SUGGESTION_SELECTED",
                "payload": {
                    "suggestion_id": "next_available_today",
                    "command_delta": {"strategy": "next_available_same_day"},
                },
            },
            {
                "label": "Try tomorrow afternoon",
                "event": "NO_SLOT_SUGGESTION_SELECTED",
                "payload": {
                    "suggestion_id": "next_business_day_afternoon",
                    "command_delta": {
                        "date_from": "2026-07-16",
                        "earliest_time": "12:00",
                    },
                },
            },
        ],
    }


def _can_confirm(session, evidence):
    proposal = session.get("proposal") or {}
    selected = session.get("selected_candidate") or {}
    return all(
        (
            evidence.get("confirmed") is True,
            evidence.get("actor_type") == "staff",
            evidence.get("session_id") == session["session_id"],
            evidence.get("turn_id") == proposal.get("turn_id"),
            evidence.get("proposal_id") == proposal.get("proposal_id"),
            evidence.get("candidate_snapshot_id") == proposal.get("candidate_snapshot_id"),
            evidence.get("candidate_id") == selected.get("candidate_id"),
            proposal.get("fresh") is True,
            evidence.get("confirmation_text") == "Confirm booking",
        )
    )


def test_sprint104_new_staff_turn_clears_stale_prompt_candidate_and_proposal():
    session = _base_session()

    next_session = _append_staff_turn(
        session,
        text="Actually make that tomorrow morning",
        kind="instruction",
    )

    assert next_session["request_reference_date"] == session["request_reference_date"]
    assert next_session["visible_diary_date"] == session["visible_diary_date"]
    assert next_session["active_turn_id"] == "turn-2"
    assert next_session["turn_history"][-1]["text"] != session["original_request_text"]
    assert next_session["stale_reason"] == "new_staff_instruction"
    assert all(next_session[key] is None for key in DOWNSTREAM_STATE_KEYS)


def test_sprint104_clarification_turn_extends_history_without_reusing_prompt_or_date():
    session = _base_session()
    session["state"] = "clarification_needed"
    session["clarifying_question"] = "Do you mean Margaret Thompson or Maggie Thompson?"
    original_prompt = session["original_request_text"]

    next_session = _append_staff_turn(
        session,
        text="Margaret Thompson",
        kind="clarification",
    )

    assert next_session["request_reference_date"] == "2026-07-15"
    assert next_session["original_request_text"] == original_prompt
    assert next_session["active_turn_id"] == "turn-2"
    assert next_session["clarifies_turn_id"] == "turn-1"
    assert next_session["turn_history"][-1]["text"] == "Margaret Thompson"
    assert next_session["state"] == "context_enrichment"


def test_sprint104_diary_navigation_marks_proposal_stale_not_semantic_date_input():
    session = _base_session()

    stale = _mark_navigation_stale(
        session,
        visible_diary_date="2026-07-16",
        event="diary_date_changed",
    )

    assert stale["request_reference_date"] == "2026-07-15"
    assert stale["command_snapshot"]["date_from"] == "2026-07-15"
    assert stale["visible_diary_date"] == "2026-07-16"
    assert stale["state"] == "stale_context"
    assert stale["proposal"]["fresh"] is False
    assert stale["candidate_snapshot"]["fresh"] is False
    assert stale["selected_candidate"] is None


def test_sprint104_patient_booking_context_requires_recognised_patient_only():
    recognised = _build_patient_booking_context(
        {
            "status": "recognised",
            "patient_id": "patient-margaret",
            "turn_id": "turn-1",
            "details_verified": False,
        }
    )
    ambiguous = _build_patient_booking_context(
        {
            "status": "ambiguous",
            "candidate_patient_ids": ["patient-margaret", "patient-maggie"],
            "turn_id": "turn-1",
        }
    )

    context = recognised["patient_booking_context"]
    assert recognised["state"] == "patient_context_ready"
    assert context["patient_id"] == "patient-margaret"
    assert context["fresh_for_turn_id"] == "turn-1"
    assert context["generated_at"]
    assert "visible_diary_rows" not in context
    assert "full_diary_dump" not in context
    assert ambiguous["state"] == "patient_recognition_needed"
    assert ambiguous["patient_booking_context"] is None


def test_sprint104_patient_recognition_is_not_details_verification_gate():
    recognised_without_details_check = _build_patient_booking_context(
        {
            "status": "recognised",
            "patient_id": "patient-margaret",
            "turn_id": "turn-1",
            "details_verified": False,
            "medicare_verified": False,
        }
    )

    assert recognised_without_details_check["state"] == "patient_context_ready"
    assert (
        recognised_without_details_check["patient_booking_context"]["patient_id"]
        == "patient-margaret"
    )


def test_sprint104_no_slot_state_returns_typed_suggestions_not_empty_candidates():
    response = _no_slot_response()

    assert response["state"] == "no_slots"
    assert response["result"] == "no_slots"
    assert response["candidates"] == []
    assert response["state"] != "candidate_selection_required"
    assert len(response["suggestions"]) >= 2
    for suggestion in response["suggestions"]:
        assert suggestion["event"] == "NO_SLOT_SUGGESTION_SELECTED"
        assert "command_delta" in suggestion["payload"]
        assert "prompt" not in suggestion["payload"]


def test_sprint104_confirm_requires_staff_evidence_and_matching_fresh_ownership():
    session = _base_session()
    evidence = {
        "confirmed": True,
        "actor_type": "staff",
        "staff_user_id": "staff-reception-1",
        "session_id": "bernie-session-104",
        "turn_id": "turn-1",
        "proposal_id": "proposal-1",
        "candidate_snapshot_id": "candidate-snapshot-1",
        "candidate_id": "slot-1515",
        "confirmation_text": "Confirm booking",
        "source_surface": "bernie_diary_panel",
        "confirmed_at": datetime(2026, 7, 15, 10, 4, tzinfo=timezone.utc).isoformat(),
    }

    assert _can_confirm(session, evidence) is True

    stale = deepcopy(session)
    stale["proposal"]["fresh"] = False
    assert _can_confirm(stale, evidence) is False

    wrong_turn = {**evidence, "turn_id": "turn-2"}
    assert _can_confirm(session, wrong_turn) is False

    wrong_actor = {**evidence, "actor_type": "system"}
    assert _can_confirm(session, wrong_actor) is False


def test_sprint104_choose_another_time_reuses_candidate_snapshot_without_search():
    session = _base_session()
    event = {
        "event": "CHOOSE_ANOTHER_TIME",
        "session_id": "bernie-session-104",
        "candidate_snapshot_id": "candidate-snapshot-1",
    }
    next_state = {
        "state": "candidate_selection",
        "session_id": event["session_id"],
        "candidate_snapshot_id": event["candidate_snapshot_id"],
        "network_effects": [],
    }

    assert next_state["candidate_snapshot_id"] == session["candidate_snapshot"]["snapshot_id"]
    assert next_state["network_effects"] == []
