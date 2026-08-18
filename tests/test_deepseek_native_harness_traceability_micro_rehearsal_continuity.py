from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal"
PARENT = (
    "raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal"
)
SOURCE_HEAD = "ed044625b6f1e59d323c21ced6ec6e2372a11d3f"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_native_harness_no_call_result_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 318
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 300
    assert compass["source_graph_revision"] == 318
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []


def test_evidence_proves_no_provider_request_and_no_session_trace() -> None:
    evidence = _load(
        "orchestration/agent_inbox/codex/"
        "deepseek-native-harness-traceability-micro-rehearsal-evidence.json"
    )
    accounting = evidence["request_and_trace_accounting"]
    assert evidence["result"] == "bounded_no_provider_call_configuration_failure"
    assert accounting["provider_requests_started"] == 0
    assert accounting["provider_retries_started"] == 0
    assert accounting["sessions_directory_present"] is False
    assert accounting["durable_session_or_trace_files"] == []
    assert evidence["assessment"]["reliability_or_model_performance_measured"] is False
    assert evidence["cleanup"]["workspace_present_after_cleanup"] is False


def test_compass_names_read_only_product_successor_and_keeps_admission_closed() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "provider-free read-only orientation" in current["outcome"]
    assert "No ordinary practice" in " ".join(current["does_not_solve"])
    assert "Continuity 318 / Compass 300" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/deepseek-native-harness-traceability-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-traceability-micro-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
