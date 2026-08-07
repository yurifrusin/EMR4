import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
SOURCE_HEAD = "46e16622471a192353cb82a33acf301dc2cfb7aa"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_inert_ddl_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 231
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 213
    assert compass["source_graph_revision"] == 231
    assert compass["current_position"]["node_id"] == NODE_ID
    assert (
        "parse-and-catalogue rehearsal is next"
        in compass["orientation_statement"].lower()
    )


def test_inert_ddl_acceptance_opens_no_executable_authority() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        ".sql.inert",
        "never sent to a database",
        "no migration",
        "driver",
        "connection",
        "database/source",
        "product read",
        "provider product path",
        "command",
        "deployment",
    ):
        assert phrase in notes


def test_database_execution_and_later_live_gates_remain_separate() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "disposable",
        "postgresql",
        "applied migration",
        "database/outbox/feed/watcher/listener/source",
        "patient/product data",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_closeout_review_and_error_register_bind_the_result() -> None:
    closeout = (
        ROOT
        / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-closeout.md"
    ).read_text(encoding="utf-8")
    acceptance = (
        ROOT
        / "orchestration/agent_inbox/codex/raisa-context-fabric-durability-inert-ddl-rehearsal-sol-acceptance.md"
    ).read_text(encoding="utf-8")
    review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-inert-ddl-postgresql-recovery-implementation-review-receipt.json"
    )
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert SOURCE_HEAD in closeout
    assert SOURCE_HEAD in acceptance
    assert "62/62" in closeout
    assert "412 statements" in acceptance
    assert review["decision"] == "pass"
    assert review["dirty_after"] is False
    assert register["register_revision"] == 84
    assert [
        row
        for row in register["incidents"]
        if row["incident_id"]
        in {"AER-0087", "AER-0088", "AER-0089", "AER-0090", "AER-0091"}
    ] == register["incidents"][-5:]
    assert not [item for item in register["incidents"] if item["status"] == "open"]
