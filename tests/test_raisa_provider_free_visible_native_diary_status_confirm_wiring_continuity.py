from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-visible-native-diary-status-confirm-wiring"
SOURCE_HEAD = "bed49be3d78d79207857b3d3a044cebd334112dc"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_visible_status_confirm_node_is_accepted_at_exact_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    nodes = {node["id"]: node for node in graph["nodes"]}
    journeys = {item["node_id"]: item for item in compass["journey"]}

    assert graph["graph_revision"] >= 275
    assert compass["map_revision"] >= 257
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert nodes[NODE_ID]["status"] == "accepted"
    assert nodes[NODE_ID]["coordinates"]["source_head"] == SOURCE_HEAD
    assert nodes[NODE_ID]["authority"]["authorized_openings"] == []
    assert NODE_ID in journeys


def test_visible_status_confirm_evidence_and_boundaries_are_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = {item for values in node["evidence"].values() for item in values}
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    assert {
        "docs/raisa-provider-free-visible-native-diary-status-confirm-wiring-closeout.md",
        "orchestration/agent_inbox/codex/raisa-provider-free-visible-native-diary-status-confirm-wiring-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--visible-native-diary-status-confirm-wiring.md",
        "orchestration/continuity/raisa-provider-free-visible-native-diary-status-confirm-wiring/visible-status-confirm-evidence.json",
    } <= evidence
    for phrase in (
        "sole write authority",
        "no raw fallback",
        "route-intercepted",
        "cf-d2",
        "patient/product data",
        "providers",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_preserves_visible_status_and_advances_to_cf_d2_observability() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == (
        "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
    )
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "inert-ddl lowering" in unlocks
    assert "database connection" in unlocks
    assert "restart, unknown commit" in limits
    assert "no database, watcher" in compass["orientation_statement"].lower()


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-visible-native-diary-status-confirm-wiring-closeout.md",
        "orchestration/agent_inbox/codex/raisa-provider-free-visible-native-diary-status-confirm-wiring-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--visible-native-diary-status-confirm-wiring.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head
