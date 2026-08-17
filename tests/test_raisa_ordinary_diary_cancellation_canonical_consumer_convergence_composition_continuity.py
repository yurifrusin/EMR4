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
NODE_ID = "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition"
PARENT = "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review"
SOURCE_HEAD = "bfac65298e1d4aaca85d1c9dcb20329ef298c485"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_accepts_exact_canonical_cancellation_candidate() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    Draft202012Validator(_json(GRAPH_SCHEMA)).validate(graph)
    Draft202012Validator(_json(COMPASS_SCHEMA)).validate(compass)

    assert graph["graph_revision"] == 313
    node = graph["nodes"][-1]
    assert node["id"] == NODE_ID
    assert node["kind"] == "implementation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "implements"}]
    assert node["authority"]["authorized_openings"] == []

    assert compass["map_revision"] == 295
    assert compass["source_graph_revision"] == 313
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "Continuity 313 / Compass 295" in compass["orientation_statement"]


def test_continuity_names_truth_kernel_and_preserves_limits() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = graph["nodes"][-1]
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free",
        "canonical delete",
        "minimal public delete receipt",
        "refresh-required",
        "live backend/database",
    ):
        assert phrase in joined

    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "post-cancellation programme orientation" in unlocks
    assert "narrowest next" in unlocks
    assert "external-adapter" in limits


def test_continuity_evidence_exists_and_closeouts_are_timestamped() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    paths: set[str] = set()
    for values in graph["nodes"][-1]["evidence"].values():
        paths.update(values)
    paths.update(compass["journey"][-1]["evidence"])
    for path in paths:
        assert (ROOT / path).exists(), path

    closeouts = [
        "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
        "orchestration/agent_inbox/codex/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--ordinary-diary-cancellation-canonical-consumer-convergence.md",
    ]
    for path in closeouts:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:16])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head

    report = REPORT.read_text(encoding="utf-8")
    assert "Continuity 313 / Compass 295" in report
    assert "one canonical cancellation command" in report
