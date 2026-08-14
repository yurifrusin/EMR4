from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-same-update-family-multi-change-editor-composition"
SOURCE_HEAD = "daed421954d65c159871585559f45caa32d95aee"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_combined_editor_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 293
    assert compass["map_revision"] >= 275
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_shared_draft_single_proposal_and_fresh_truth() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "docs/diary/meta-grid.js",
        "docs/diary/diary.js",
        "review/test_reception_one_same_update_family_multi_change_editor_composition.py",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-same-update-family-multi-change-editor-composition-gemini-review-receipt.json",
        "docs/ariadne-agent-error-correction-register-revision-280.md",
        "docs/raisa-reception-one-same-update-family-multi-change-editor-composition-closeout.md",
    } <= evidence
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "one local provisional draft",
        "one visible explicit human confirmation",
        "exactly one existing handlemoveresize call",
        "fresh practitioner admission",
        "status remains distinct",
        "route_intercepted_browser_authored_synthetic",
    ):
        assert phrase in joined


def test_compass_names_read_only_post_editor_orientation_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "read-only post-editor programme orientation" in unlocks
    assert "without presuming a new authority opening" in unlocks
    assert "Continuity 293 / Compass 275" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-same-update-family-multi-change-editor-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--reception-one-same-update-family-multi-change-editor-composition.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_keep_wider_runtime_closed() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = (ROOT / "implementation_plan.md").read_text(encoding="utf-8")
    assert "Continuity 293 / Compass 275" in handover
    assert "post_combined_editor_compass_baton_orientation" in handover
    assert "Status remains distinct" in handover
    assert "same-update-family multi-change kernel and visible editor" in plan
    assert "No watcher runtime" in plan


def test_register_revision_280_binds_latest_contained_incident() -> None:
    register = _load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert register["register_revision"] == 280
    incident = register["incidents"][-1]
    assert incident["incident_id"] == "AER-0319"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_active_operation_latch_closes_exact_accepted_source() -> None:
    latch = _load(
        "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    assert latch["operation_id"] == NODE_ID
    assert latch["status"] == "complete"
    assert latch["source_head"] == SOURCE_HEAD
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is True
