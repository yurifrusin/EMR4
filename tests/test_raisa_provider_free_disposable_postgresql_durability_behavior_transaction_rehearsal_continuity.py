import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-"
    "rehearsal"
)
SOURCE_HEAD = "f3383dc4099b4ee590014bea62dddb146f5d2a16"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_behavior_transaction_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 234
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 216
    assert compass["source_graph_revision"] == 234
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "twenty exact serial" in compass["orientation_statement"].lower()
    assert "paused" in compass["orientation_statement"].lower()


def test_behavior_acceptance_opens_no_operational_authority() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["kind"] == "implementation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "twenty",
        "not a claim of infallibility",
        "concurrency",
        "restart",
        "rotation",
        "retention",
        "applied migration",
        "operational database",
        "watcher",
        "patient",
        "commands",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_hands_off_to_architecture_health_then_containment() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "architecture-health",
        "agent execution surface",
        "concurrent",
        "unknown-commit",
        "key rotation",
        "retention",
        "applied migration",
        "database/outbox/feed/watcher/listener/source",
        "patient/product data",
        "tools",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_immutable_pass_and_final_review_are_bound() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    evidence = load(
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
        "durability-behavior-transaction-rehearsal/provider-free-behavior-"
        "transaction-evidence-admission-replay-recovery-pass.json"
    )
    review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-"
        "durability-behavior-attempt-048-review-receipt.json"
    )
    assert evidence["scenario_reconciliation"] == {
        "expected": 20,
        "observed": 20,
        "passed": 20,
    }
    assert evidence["cleanup"]["absence_verified"] is True
    assert review["decision"] == "pass"
    assert review["dirty_after"] is False
    assert "498/498" in review["result"]
    assert node["status"] == "accepted"
