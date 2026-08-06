import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-authored-synthetic-durability-state-machine-"
    "rehearsal"
)
SOURCE_HEAD = "95a2ed5e960c58686262b5e82ce2e89354a3860a"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_durability_rehearsal_continuity_and_compass_are_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 228
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 210
    assert compass["source_graph_revision"] == 228
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "migration-and-transaction architecture" in compass[
        "orientation_statement"
    ]


def test_durability_rehearsal_authority_remains_closed() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "pure",
        "provider-free",
        "unmounted",
        "authored-synthetic",
        "not a cryptographic mac",
        "no application",
        "migration",
        "database/source",
        "product read",
        "provider",
        "command",
        "runtime",
    ):
        assert phrase in notes


def test_unresolved_live_and_real_data_gates_remain_explicit() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "historical-phi",
        "migrations",
        "database/outbox/feed/watcher/listener/source",
        "operational credentials",
        "product reads",
        "providers",
        "command/write",
        "deployment",
        "production",
        "release",
        "pages",
        "protected refs",
    ):
        assert phrase in unresolved


def test_next_candidate_is_architecture_only() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "postgresql schema",
        "isolation",
        "locking",
        "rollback",
        "rls/roles",
        "without creating or mounting",
        "migrations",
        "live database/outbox/feed/watcher/listener/source",
        "operational credentials",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
