from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering"
SOURCE_HEAD = "cd890647d327a3d9bf4f60e5e1d6f9a1924bab29"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_inert_ddl_node_is_accepted_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}

    assert graph["graph_revision"] >= 279
    assert compass["map_revision"] >= 261
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["kind"] == "foundation"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["authority"]["authorized_openings"] == []
    assert NODE_ID in journeys


def test_inert_ddl_evidence_and_boundaries_are_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    joined = " ".join(node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]).lower()

    assert {
        "docs/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-closeout.md",
        "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--cf-d2-event-cue-inert-ddl-lowering.md",
        "orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/event-cue-schema.sql.inert",
    } <= evidence
    for phrase in (
        "seven relations", "fifty fields", "nineteen honest", "sixty-five hostile",
        "postgresql parse", "database/source", "unknown commit", "product/patient data",
        "pages", "protected refs",
    ):
        assert phrase in joined


def test_compass_records_explicit_pause_before_parse_catalogue() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "pause is lifted" in unlocks
    assert "disposable postgresql-16" in unlocks
    assert "postgresql parse" in limits
    assert "explicit pause" in compass["orientation_statement"].lower()


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-closeout.md",
        "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--cf-d2-event-cue-inert-ddl-lowering.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
