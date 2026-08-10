import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
SOURCE_HEAD = "a93d07405ad35d7d6c0603065625c17ec14ab23e"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def accepted_body_node() -> dict:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_durability_body_architecture_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    node = accepted_body_node()
    assert graph["graph_revision"] >= 230
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] >= 212
    assert compass["source_graph_revision"] == graph["graph_revision"]


def test_body_acceptance_opens_no_executable_authority() -> None:
    node = accepted_body_node()
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "machine-readable only",
        "nine entry-point",
        "thirteen trigger-function",
        "not sql/ddl",
        "no migration",
        "database/source",
        "product read",
        "provider product path",
        "command",
        "runtime",
    ):
        assert phrase in notes


def test_inert_ddl_and_later_live_gates_remain_separate() -> None:
    node = accepted_body_node()
    rebind = (
        ROOT
        / "docs/raisa-provider-free-unmounted-durability-function-trigger-body-outbox-select-policy-parent-rebind.md"
    ).read_text(encoding="utf-8")
    joined = " ".join(
        node["claim_scope"]
        + node["unresolved_gates"]
        + [rebind]
    ).lower()
    for phrase in (
        "inert",
        "non-executable",
        "sql/ddl execution",
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


def test_closeout_review_and_error_register_bind_the_result() -> None:
    closeout = (
        ROOT
        / "docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-closeout.md"
    ).read_text(encoding="utf-8")
    acceptance = (
        ROOT
        / "orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-sol-acceptance.md"
    ).read_text(encoding="utf-8")
    review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-function-trigger-body-architecture-r7-final-review-retry-receipt.json"
    )
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert SOURCE_HEAD in closeout
    assert SOURCE_HEAD in acceptance
    assert "339/339" in closeout
    assert "44/44" in acceptance
    assert review["decision"] == "pass"
    assert review["dirty_after"] is False
    assert register["register_revision"] >= 81
    incident = next(
        row for row in register["incidents"] if row["incident_id"] == "AER-0081"
    )
    assert incident["status"] == "corrected"
    assert not [item for item in register["incidents"] if item["status"] == "open"]
