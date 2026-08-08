import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-"
    "rehearsal-plan"
)
SOURCE_HEAD = "07e8750548ed69aba5a19f693a72397121a340e5"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_behavior_transaction_plan_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 233
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 215
    assert compass["source_graph_revision"] == 233
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "runtime implementation is paused" in compass[
        "orientation_statement"
    ].lower()


def test_plan_acceptance_opens_no_runtime_authority() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["kind"] == "concept"
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "twenty",
        "proves no database behavior",
        "networkless",
        "no applied migration",
        "operational database/source",
        "command",
        "deployment",
        "pause",
    ):
        assert phrase in notes


def test_runtime_and_later_live_gates_remain_separate() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "fixed-path",
        "implementation veto",
        "trigger",
        "rls",
        "idempotency",
        "rollback",
        "concurrency",
        "key rotation",
        "retention",
        "applied migration",
        "database/outbox/feed/watcher/listener/source",
        "patient/product data",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_exact_review_and_error_register_bind_plan_result() -> None:
    contract = load(
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
        "durability-behavior-transaction-rehearsal/behavior-transaction-"
        "rehearsal-contract.json"
    )
    rejected = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
        "behavior-transaction-rehearsal-plan-review-receipt.json"
    )
    review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
        "behavior-transaction-rehearsal-plan-correction-review-receipt.json"
    )
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert contract["status"] == "accepted_plan_runtime_closed"
    assert len(contract["scenario_order"]) == 20
    assert rejected["decision"] == "revision_required"
    assert review["decision"] == "pass"
    assert review["dirty_after"] is False
    assert "124` admitted, 124 passed" in review["result"]
    assert "79 collected, 79 passed" in review["result"]
    assert register["register_revision"] == 94
    assert [row["incident_id"] for row in register["incidents"][-4:]] == [
        "AER-0111",
        "AER-0112",
        "AER-0113",
        "AER-0114",
    ]
    assert not [item for item in register["incidents"] if item["status"] == "open"]
