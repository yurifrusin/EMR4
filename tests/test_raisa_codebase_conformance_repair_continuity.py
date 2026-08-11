import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-codebase-conformance-repair"
SOURCE_HEAD = "8ce3a591fa0e63ad2d68bf95a8d7e24369dd872f"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _repair_node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_conformance_repair_remains_accepted_in_history() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    node = _repair_node(graph)
    assert graph["graph_revision"] >= 236
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert any(step["node_id"] == NODE_ID for step in compass["journey"])


def test_repair_opens_no_product_or_runtime_authority() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = _repair_node(graph)
    assert node["kind"] == "maintenance"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "python 3.11",
        "graphql",
        "rest/openapi",
        "protected evidence",
        "patient/clinical/product",
        "provider",
        "database/source",
        "tool",
        "command",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_hands_off_to_architecture_only_aes_c0() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    steps = [step for step in compass["journey"] if step["node_id"] == NODE_ID]
    assert len(steps) == 1
    joined = " ".join([steps[0]["strategic_role"], steps[0]["outcome"]]).lower()
    for phrase in (
        "repair repository fitness",
        "aes-c0 architecture",
    ):
        assert phrase in joined


def test_repair_evidence_is_bound() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = _repair_node(graph)
    evidence = node["evidence"]
    assert "orchestration/harness_settings/python_source_state.json" in evidence[
        "findings"
    ]
    assert (
        "docs/api-spine/external-read-model-current-surface-status.json"
        in evidence["findings"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--codebase-conformance-repair.md"
        in evidence["closeouts"]
    )
    assert node["status"] == "accepted"
