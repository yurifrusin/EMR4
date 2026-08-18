from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "deepseek-native-harness-authored-synthetic-agentic-coding-"
    "traceability-rehearsal"
)
PARENT = "deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal"
SOURCE_HEAD = "25067e7d633eae597929d6969a35b22b735b253e"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_occupied_native_harness_result_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 319
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 301
    assert compass["source_graph_revision"] == 319
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []


def test_traceability_pass_and_completion_failure_are_both_preserved() -> None:
    evidence = _load(
        "orchestration/agent_inbox/codex/"
        "deepseek-native-harness-agentic-coding-rehearsal-evidence.json"
    )
    assert evidence["result"] == (
        "bounded_occupied_traceability_demonstrated_worker_completion_not_demonstrated"
    )
    assert evidence["session"]["model_steps_with_usage"] == 6
    assert evidence["session"]["tool_calls"] == 8
    assert evidence["synthetic_candidate"]["independent_tests_passed"] == 4
    assert evidence["synthetic_candidate"]["regression_tests_added"] == 0
    assert evidence["acceptance"]["occupied_traceability"] == "passed"
    assert evidence["acceptance"]["overall_occupied_task"] == "failed_incomplete"
    assert evidence["cleanup"]["target_absent_after_cleanup"] is True


def test_compass_selects_monitored_real_work_not_more_broad_rehearsal() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "one monitored low-risk EMR4 trial" in current["strategic_role"]
    assert "profile family" in current["outcome"]
    assert "not an unrestricted default" in " ".join(current["does_not_solve"])
    assert "Continuity 319 / Compass 301" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/deepseek-native-harness-authored-synthetic-agentic-coding-traceability-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/deepseek-native-harness-agentic-coding-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-agentic-coding-traceability-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
