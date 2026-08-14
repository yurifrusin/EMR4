from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-multi-change-request-atomicity-orientation"
SOURCE_HEAD = "fbb7ffb46e041bbfc193ff3a76b2f970c06dee58"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_multi_change_orientation_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 291
    assert compass["map_revision"] >= 273
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_one_family_commands_and_adapter_containment() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "orchestration/continuity/raisa-reception-one-multi-change-request-atomicity-orientation/multi-change-action-atomicity-contract.json",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-multi-change-request-atomicity-orientation-gemini-review-receipt.json",
        "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-gemini-report-reconciliation-incident.json",
        "docs/raisa-reception-one-multi-change-request-atomicity-orientation-closeout.md",
    } <= evidence
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "typed inert",
        "one existing update-family proposal",
        "cross-family",
        "non-executable",
        "model authority remains zero",
        "repository_static_authored_synthetic",
    ):
        assert phrase in joined


def test_compass_names_same_update_family_kernel_rehearsal_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "practitioner, time and duration together" in unlocks
    assert "Continuity 291 / Compass 273" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-multi-change-request-atomicity-orientation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-multi-change-request-atomicity-orientation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--reception-one-multi-change-request-atomicity-orientation.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_keep_external_and_cross_family_runtime_closed() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = (ROOT / "implementation_plan.md").read_text(encoding="utf-8")
    assert "Continuity 291 / Compass 273" in handover
    assert "same_update_family_multi_change_kernel_rehearsal" in handover
    assert "cross-family request is non-executable" in handover
    assert "provider-free multi-change request atomicity orientation" in plan
    assert "No watcher runtime" in plan


def test_register_revision_269_is_bound_to_reconciled_review() -> None:
    register = _load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert register["register_revision"] == 269
    incident = register["incidents"][-1]
    assert incident["incident_id"] == "AER-0308"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "control_added"
