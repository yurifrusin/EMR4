from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-post-combined-editor-compass-baton-orientation"
SOURCE_HEAD = "2ca3a111d2ee9277571ea3c905f22ce78c8e9745"
DECISION_ID = "reception-one-appointment-cancellation-direction"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_orientation_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 294
    assert compass["map_revision"] >= 276
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_preserves_revocation_and_committed_truth_boundary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "revocable for future acts",
        "already committed appointment",
        "separately authorised cancellation or rescheduling",
        "events remain acceleration hints",
        "genuine yuri-owned fork",
    ):
        assert phrase in joined


def test_compass_records_recommended_cancellation_decision_without_opening_it() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    horizon = next(
        item for item in compass["decision_horizon"] if item["id"] == DECISION_ID
    )
    decision = next(
        item for item in compass["user_owned_decisions"] if item["id"] == DECISION_ID
    )
    assert horizon["status"] == "candidate"
    assert (
        "read-only cancellation command-path readiness review"
        in horizon["strategic_question"]
    )
    assert (
        "before any cancellation family convergence or ui exposure"
        in decision["required_before"].lower()
    )


def test_latch_is_blocked_and_stops_for_the_genuine_fork() -> None:
    latch = _load(
        "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    assert latch["operation_id"] == NODE_ID
    assert latch["status"] == "blocked"
    assert latch["source_head"] == SOURCE_HEAD
    assert latch["checkpoint"]["next_executable_stage"] is None
    assert latch["resume_after_compaction"] is False
    assert latch["user_attention"]["required"] is True
    assert latch["terminal_response"]["reason"] == "genuine_user_attention_fork"


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-post-combined-editor-compass-baton-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--post-combined-editor-programme-orientation.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_pause_before_cancellation_implementation() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = " ".join(
        (ROOT / "implementation_plan.md").read_text(encoding="utf-8").split()
    )
    assert "Continuity 294 / Compass 276" in handover
    assert "genuine Yuri-owned programme fork" in handover
    assert "read-only cancellation command-path readiness review" in handover
    assert "No cancellation implementation" in handover
    assert "read-only cancellation command-path readiness review" in plan
    assert "Yuri's programme choice" in plan


def test_register_revision_281_is_bound() -> None:
    register = _load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert register["register_revision"] >= 281
    incident = next(
        item for item in register["incidents"] if item["incident_id"] == "AER-0320"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
