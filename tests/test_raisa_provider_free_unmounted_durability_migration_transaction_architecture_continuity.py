import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-durability-migration-transaction-architecture"
SOURCE_HEAD = "c55d25d6c9704ae4612ef2d123158f71302ab411"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_durability_migration_architecture_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 229
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 211
    assert compass["source_graph_revision"] == 229
    assert compass["current_position"]["node_id"] == NODE_ID
    assert (
        "function-and-trigger-body architecture is next"
        in compass["orientation_statement"].lower()
    )


def test_structural_acceptance_does_not_open_executable_authority() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "structural/signature-only",
        "bodies",
        "trigger declarations",
        "execute grants",
        "no sql/ddl",
        "database/source",
        "product read",
        "provider",
        "command",
        "runtime",
    ):
        assert phrase in notes


def test_next_candidate_and_later_gates_remain_separate() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "function bodies",
        "without rendering sql",
        "sql/ddl",
        "migrations",
        "database objects",
        "database/outbox/feed/watcher/listener/source",
        "patient/product data",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_closeout_and_error_register_bind_the_final_result() -> None:
    closeout = (
        ROOT
        / "docs/raisa-provider-free-unmounted-durability-migration-transaction-architecture-closeout.md"
    ).read_text(encoding="utf-8")
    acceptance = (
        ROOT
        / "orchestration/agent_inbox/codex/raisa-context-fabric-durability-migration-transaction-architecture-sol-acceptance.md"
    ).read_text(encoding="utf-8")
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert SOURCE_HEAD in closeout
    assert SOURCE_HEAD in acceptance
    assert "212/212" in closeout
    assert "155/155" in acceptance
    assert register["register_revision"] == 62
    assert not [item for item in register["incidents"] if item["status"] == "open"]
