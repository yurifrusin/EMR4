import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal"
)
SOURCE_HEAD = "c3ca2515b9f2c4b20cb7230364de7417f48eab54"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def accepted_parse_node() -> dict:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_disposable_postgresql_catalogue_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    node = accepted_parse_node()
    assert graph["graph_revision"] >= 232
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 214
    assert compass["source_graph_revision"] == graph["graph_revision"]


def test_catalogue_acceptance_opens_no_behavioral_authority() -> None:
    node = accepted_parse_node()
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "networkless",
        "parse",
        "atomic installation/rollback",
        "no function",
        "trigger",
        "rls",
        "no migration",
        "operational database/source",
        "command",
        "deployment",
    ):
        assert phrase in notes


def test_behavior_and_later_live_gates_remain_separate() -> None:
    node = accepted_parse_node()
    rebind = (
        ROOT
        / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-outbox-select-rls-rebind.md"
    ).read_text(encoding="utf-8")
    joined = " ".join(
        node["claim_scope"]
        + node["unresolved_gates"]
        + [rebind]
    ).lower()
    for phrase in (
        "behavior",
        "function",
        "trigger",
        "rls",
        "applied migration",
        "database/outbox/feed/watcher/listener/source",
        "patient",
        "product",
        "command",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_terminal_evidence_review_and_error_register_bind_result() -> None:
    base = (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
        "durability-parse-catalogue-rehearsal/"
    )
    assert base.endswith("durability-parse-catalogue-rehearsal/")
    review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
        "exact-catalogue-binding-review-receipt.json"
    )
    closeout_review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
        "parse-catalogue-closeout-retry-review-receipt.json"
    )
    rejected_closeout_review = load(
        "orchestration/agent_inbox/codex/raisa-context-fabric-durability-parse-"
        "catalogue-closeout-review-sol-rejection.json"
    )
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert review["decision"] == "pass"
    assert review["dirty_after"] is False
    assert rejected_closeout_review["admitted"] is False
    assert rejected_closeout_review["review_decision"] == "pass"
    assert closeout_review["decision"] == "pass"
    assert "**Total** | **217** | **217** | **217** | **PASSED**" in closeout_review[
        "result"
    ]
    assert register["register_revision"] >= 91
    incident = next(
        row for row in register["incidents"] if row["incident_id"] == "AER-0110"
    )
    assert incident["status"] == "corrected"
    assert not [item for item in register["incidents"] if item["status"] == "open"]
