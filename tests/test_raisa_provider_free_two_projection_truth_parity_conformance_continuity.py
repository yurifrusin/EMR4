from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-two-projection-truth-parity-conformance-rehearsal"
SOURCE_HEAD = "18aa4b613d735a68a7f6f2e55d34e498176c9935"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_truth_parity_is_current_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 285
    assert compass["map_revision"] >= 267
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []
    assert node["contract_evidence"] == []


def test_compass_records_yuris_selected_direction_as_an_accepted_descendant() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    assert compass["current_position"]["node_id"] == (
        "raisa-reception-one-selected-appointment-time-reschedule-composition"
    )
    assert not any(
        item["id"] == "post-truth-parity-programme-direction"
        for item in compass["decision_horizon"]
    )
    assert "Continuity 286 / Compass 268" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-projection-neutral-kernel-truth-architecture.md",
        "docs/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/raisa-two-projection-truth-parity-conformance-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-14--two-projection-truth-parity-conformance.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
