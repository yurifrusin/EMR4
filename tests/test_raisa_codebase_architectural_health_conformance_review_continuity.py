import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-codebase-architectural-health-conformance-review"
SOURCE_HEAD = "95ce6b75723d57e672858619c3621d4a273c1f34"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_architecture_health_review_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 235
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 217
    assert compass["source_graph_revision"] == 235
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "no p0" in compass["orientation_statement"].lower()
    assert "conformance repair is next" in compass["orientation_statement"].lower()


def test_review_opens_no_product_or_runtime_authority() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["kind"] == "review"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "findings-only",
        "graphql",
        "rest/openapi",
        "python 3.11",
        "patient",
        "clinical",
        "provider",
        "migration",
        "watcher",
        "tools",
        "commands",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_hands_off_to_repair_then_aes_c0() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "maintained/protected/historical",
        "python 3.11",
        "api spine",
        "baton consistency",
        "aes-c0",
        "patient/product/clinical",
        "providers",
        "tools",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_review_evidence_is_bound() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    evidence = node["evidence"]
    assert "docs/raisa-codebase-as-built-architectural-state-map.md" in evidence["findings"]
    assert "docs/raisa-codebase-architectural-health-conformance-review.md" in evidence["findings"]
    assert (
        "orchestration/human_inbox/yuri/"
        "2026-08-11--codebase-architectural-health-conformance-review.md"
        in evidence["closeouts"]
    )
    assert node["status"] == "accepted"
