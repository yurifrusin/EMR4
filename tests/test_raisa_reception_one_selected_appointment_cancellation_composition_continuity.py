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
NODE_ID = "raisa-reception-one-selected-appointment-cancellation-composition"
PARENT = "ariadne-recent-work-effectiveness-and-transport-repair"
SOURCE_HEAD = "856ebc3d832d5b64ce65c2e0732eaa63d926c600"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_and_compass_accept_exact_cancellation_candidate() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    Draft202012Validator(_json(GRAPH_SCHEMA)).validate(graph)
    Draft202012Validator(_json(COMPASS_SCHEMA)).validate(compass)

    assert graph["graph_revision"] == 311
    node = graph["nodes"][-1]
    assert node["id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["kind"] == "implementation"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "implements"}]
    assert node["authority"]["authorized_openings"] == []

    assert compass["map_revision"] == 293
    assert compass["source_graph_revision"] == 311
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "Continuity 311 / Compass 293" in compass["orientation_statement"]


def test_evidence_exists_and_adapter_neutral_claim_stays_bounded() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = graph["nodes"][-1]
    paths: set[str] = set()
    for values in node["evidence"].values():
        paths.update(values)
    paths.update(compass["journey"][-1]["evidence"])
    for path in paths:
        assert (ROOT / path).exists(), path

    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "reference renderer",
        "presentation freedom",
        "explicit staff confirmation",
        "raw compatibility delete",
        "route-intercepted",
        "external-adapter interoperability",
    ):
        assert phrase in joined


def test_compass_names_read_only_ordinary_diary_convergence_next() -> None:
    compass = _json(COMPASS)
    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "read-only ordinary diary cancellation" in unlocks
    assert "deletebooking" in unlocks
    assert "ordinary diary dual-family cancellation fallback" in limits
    assert "external-adapter" in limits

    report = REPORT.read_text(encoding="utf-8")
    assert "Continuity 311 / Compass 293" in report
    assert "ordinary Diary cancellation compatibility-consumer" in report


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-selected-appointment-cancellation-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-cancellation-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-17--reception-one-selected-appointment-cancellation-composition.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-17" in head
        assert "Timestamp: 2026-08-17T" in head
        assert "+10:00 (Australia/Brisbane)" in head
