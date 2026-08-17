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
NODE_ID = "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review"
PARENT = "raisa-reception-one-selected-appointment-cancellation-composition"
SOURCE_HEAD = "0f3b0c73fef0a2a52186a8f86bae8cf351d1a8df"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_continuity_accepts_exact_static_review_candidate() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    Draft202012Validator(_json(GRAPH_SCHEMA)).validate(graph)
    Draft202012Validator(_json(COMPASS_SCHEMA)).validate(compass)

    assert graph["graph_revision"] == 312
    node = graph["nodes"][-1]
    assert node["id"] == NODE_ID
    assert node["kind"] == "review"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "validates"}]
    assert node["authority"]["authorized_openings"] == []

    assert compass["map_revision"] == 294
    assert compass["source_graph_revision"] == 312
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "Continuity 312 / Compass 294" in compass["orientation_statement"]


def test_continuity_names_client_only_convergence_and_preserves_limits() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = graph["nodes"][-1]
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "repository-static",
        "client-only",
        "404-to-status",
        "appointment read model",
        "live backend/database",
    ):
        assert phrase in joined

    unlocks = " ".join(compass["current_position"]["unlocks"]).lower()
    limits = " ".join(compass["current_position"]["does_not_solve"]).lower()
    assert "client-only canonical cancellation" in unlocks
    assert "strict minimal receipt" in unlocks
    assert "stale pre-adapter route-contract" in limits


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
        "docs/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-closeout.md",
        "orchestration/agent_inbox/codex/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-17--ordinary-diary-cancellation-compatibility-consumer-convergence-review.md",
    ]
    for path in closeouts:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-17" in head
        assert "Timestamp: 2026-08-17T" in head
        assert "+10:00 (Australia/Brisbane)" in head

    report = REPORT.read_text(encoding="utf-8")
    assert "Continuity 312 / Compass 294" in report
    assert "client-only canonical delete convergence" in report
