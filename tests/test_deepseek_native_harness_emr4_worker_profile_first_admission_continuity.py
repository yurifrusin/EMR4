from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission"
)
PARENT = (
    "deepseek-native-harness-authored-synthetic-agentic-coding-"
    "traceability-rehearsal"
)
SOURCE_HEAD = "af1a79f93024a7186849e550b4d529c8c601c93f"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_first_monitored_harness_worker_result_is_retained() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 320
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    journey = next(row for row in compass["journey"] if row["node_id"] == NODE_ID)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert "seven-tool" in journey["outcome"]


def test_broker_rejection_and_zero_candidate_are_preserved() -> None:
    evidence = _load(
        "orchestration/agent_inbox/codex/"
        "deepseek-native-harness-emr4-profile-validator-worker-terminal-"
        "evidence.json"
    )
    assert evidence["result"] == (
        "occupied_worker_dispatch_traceable_broker_tool_contract_rejected_"
        "zero_provider_zero_candidate"
    )
    assert evidence["broker"]["rejection_reason_code"] == "tool-not-allowlisted"
    assert evidence["broker"]["provider_calls"] == 0
    assert evidence["session"]["declared_tool_count"] == 7
    assert evidence["session"]["successful_model_step_count"] == 0
    assert evidence["session"]["tool_call_count"] == 0
    assert evidence["candidate_readback"]["candidate_admitted"] is False
    assert evidence["cleanup"]["status"] == "complete"


def test_compass_preserves_first_attempt_and_records_its_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    journey = next(row for row in compass["journey"] if row["node_id"] == NODE_ID)
    assert "seven-tool" in journey["outcome"]
    assert "default-off canonical check-in route-adapter" in current["strategic_role"]
    assert "not a default transport" in " ".join(current["does_not_solve"])
    assert "Continuity 321 / Compass 303" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission-closeout.md",
        "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-worker-profile-first-admission-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-emr4-first-monitored-worker-admission.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
