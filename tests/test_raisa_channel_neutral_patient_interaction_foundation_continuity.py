from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-channel-neutral-patient-interaction-foundation"
SOURCE_HEAD = "17d9da1844e59406eecda44b5029e839b2e8a573"
CURRENT_POSITION = "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_patient_interaction_foundation_remains_accepted() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}

    assert graph["graph_revision"] >= 274
    assert compass["map_revision"] >= 256
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["authority"]["authorized_openings"] == []
    assert NODE_ID in journeys


def test_patient_interaction_foundation_preserves_closed_boundaries() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    for phrase in (
        "future-closed",
        "real identity",
        "patient clients",
        "command authority",
        "cf-d2",
        "patient/product data",
        "providers",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_patient_foundation_evidence_remains_bound_after_cf_d2_advance() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}

    assert {
        "docs/raisa-channel-neutral-patient-interaction-foundation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-channel-neutral-patient-interaction-foundation-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--channel-neutral-patient-interaction-foundation.md",
        "orchestration/continuity/raisa-channel-neutral-patient-interaction-foundation/provider-free-acceptance-evidence.json",
    } <= evidence
    assert compass["current_position"]["node_id"] == CURRENT_POSITION
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "unmounted event/cue representation architecture" in unlocks
    assert "without opening a database connection" in unlocks
    assert "external identity/channel delivery" in limits
    assert "unmounted cf-d2 event/cue admission rehearsal" in compass[
        "orientation_statement"
    ].lower()
