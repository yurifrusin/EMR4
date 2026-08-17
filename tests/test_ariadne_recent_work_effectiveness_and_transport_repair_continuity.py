from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
GRAPH_SCHEMA = ROOT / "orchestration/continuity/ariadne-continuity-graph.schema.json"
COMPASS_SCHEMA = ROOT / "orchestration/continuity/ariadne-compass.schema.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "ariadne-recent-work-effectiveness-and-transport-repair"
PARENT = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-http-"
    "integration-rehearsal"
)
SOURCE_HEAD = "73bea42b37424ca3f53240d52f8e5c10120a5ce7"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_accept_exact_reviewed_repair() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    Draft202012Validator(_json(GRAPH_SCHEMA)).validate(graph)
    Draft202012Validator(_json(COMPASS_SCHEMA)).validate(compass)

    assert graph["graph_revision"] == 310
    node = graph["nodes"][-1]
    assert node["id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["kind"] == "review"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert any("150.578" in claim for claim in node["claim_scope"])
    assert any("45-minute" in claim for claim in node["claim_scope"])

    assert compass["map_revision"] == 292
    assert compass["source_graph_revision"] == 310
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "Continuity 310 / Compass 292" in compass["orientation_statement"]
    assert "cancellation composition" in compass["orientation_statement"]


def test_all_node_and_journey_evidence_exists_and_report_is_current() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = graph["nodes"][-1]
    paths: set[str] = set()
    for values in node["evidence"].values():
        paths.update(values)
    paths.update(compass["journey"][-1]["evidence"])
    for path in paths:
        assert (ROOT / path).exists(), path

    report = REPORT.read_text(encoding="utf-8")
    assert "Continuity 310 / Compass 292" in report
    assert "Five evidence-backed Ariadne effectiveness and transport repairs pass" in report
    assert "selected-appointment cancellation composition is next" in report
