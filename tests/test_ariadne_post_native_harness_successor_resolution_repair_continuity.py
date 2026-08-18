from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-post-native-harness-successor-resolution-repair"
PARENT = (
    "deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-"
    "development-admission"
)
SOURCE_HEAD = "2a31437f6da0defa2dc9247491f04d5b23c97608"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_successor_repair_is_retained_and_contract_evidence_is_inherited() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 322
    assert compass["map_revision"] >= 304
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    assert node["kind"] == "maintenance"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert [row["contract_id"] for row in node["contract_evidence"]] == [
        "combined-patient-practitioner-time-duration-intent",
        "committed-reschedule-availability-reconciliation",
    ]


def test_historical_repair_node_preserves_read_only_default_denial() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(row for row in graph["nodes"] if row["id"] == NODE_ID)
    notes = " ".join(node["authority"]["notes"])
    gates = " ".join(node["unresolved_gates"])
    assert "read-only readiness review" in notes
    assert "No ordinary practice" in gates
    assert "No product code" in gates


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-post-native-harness-successor-resolution-repair-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-post-native-harness-successor-resolution-repair-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--post-native-harness-successor-resolution-repair.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
