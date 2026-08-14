from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-selected-appointment-time-reschedule-composition"
SOURCE_HEAD = "d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_time_reschedule_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 286
    assert compass["map_revision"] >= 268
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_binds_workers_fresh_truth_and_closed_command_boundary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    assert {
        "review/test_reception_one_time_reschedule_action.py",
        "orchestration/agent_inbox/deepseek/raisa-reception-one-time-reschedule-test-worker-receipt.json",
        "orchestration/agent_inbox/antigravity/raisa-reception-one-time-reschedule-gemini-review-receipt.json",
        "docs/ariadne-mandatory-parallelism-efficacy-control.md",
        "docs/raisa-reception-one-selected-appointment-time-reschedule-composition-closeout.md",
    } <= evidence
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "duration delta at zero",
        "no raw fallback",
        "same-start",
        "another command",
        "watcher/runtime",
        "deployment",
    ):
        assert phrase in joined


def test_compass_records_duration_only_descendant_and_resolves_direction_fork() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    assert "duration-only" in unlocks
    assert not any(
        item["id"] == "post-truth-parity-programme-direction"
        for item in compass["decision_horizon"]
    )
    assert "Continuity 286 / Compass 268" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-appointment-time-reschedule-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-time-reschedule-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-time-reschedule-composition.md",
        "docs/ariadne-mandatory-parallelism-efficacy-control.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
