from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-cf-d2-observability-first-event-cue"
SOURCE_HEAD = "e8677b54d1c339dcd14776ce8bf15e7db2980378"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_cf_d2_observability_node_is_accepted_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}

    assert graph["graph_revision"] >= 276
    assert compass["map_revision"] >= 258
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["kind"] == "foundation"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["authority"]["authorized_openings"] == []
    assert NODE_ID in journeys


def test_cf_d2_observability_evidence_and_boundaries_are_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    assert {
        "docs/raisa-provider-free-cf-d2-observability-first-event-cue-closeout.md",
        "orchestration/agent_inbox/codex/raisa-cf-d2-observability-first-event-cue-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--cf-d2-observability-first-event-cue-architecture.md",
        "orchestration/continuity/raisa-provider-free-cf-d2-observability-first-event-cue/observability-contract.json",
        "docs/api-spine/async/durable-diary-event-cue-observability.yaml",
    } <= evidence
    for phrase in (
        "source services retain current truth",
        "payload-free refresh obligation",
        "ten diagnostic stages",
        "39 hostile mutations",
        "restart",
        "unknown commit",
        "product/patient data",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_observability_journey_declares_admission_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    assert journey["lineage_parent"] == (
        "raisa-provider-free-visible-native-diary-status-confirm-wiring"
    )
    assert "unmounted state admission is next" in journey["outcome"].lower()


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-cf-d2-observability-first-event-cue-closeout.md",
        "orchestration/agent_inbox/codex/raisa-cf-d2-observability-first-event-cue-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--cf-d2-observability-first-event-cue-architecture.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
