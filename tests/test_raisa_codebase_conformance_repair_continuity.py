import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-codebase-conformance-repair"
SOURCE_HEAD = "8ce3a591fa0e63ad2d68bf95a8d7e24369dd872f"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_conformance_repair_is_current() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 236
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 218
    assert compass["source_graph_revision"] == 236
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "aes-c0 architecture and contract is next" in compass[
        "orientation_statement"
    ].lower()


def test_repair_opens_no_product_or_runtime_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
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
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "capability classes",
        "external broker",
        "immutable generation manifest",
        "no-fallback",
        "command separation",
        "provider-free",
        "patient/product/clinical",
        "deployment",
        "protected-ref",
    ):
        assert phrase in joined


def test_repair_evidence_is_bound() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
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
