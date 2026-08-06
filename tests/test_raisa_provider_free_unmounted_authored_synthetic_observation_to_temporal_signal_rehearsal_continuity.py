import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-authored-synthetic-observation-to-"
    "temporal-signal-rehearsal"
)
SOURCE_HEAD = "c0502c398df4a56c9558bc68eddedb2adf20d12d"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_observation_signal_continuity_and_compass_are_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 226
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 208
    assert compass["source_graph_revision"] == 226
    assert compass["current_position"]["node_id"] == NODE_ID
    assert (
        "source-specific durability architecture" in (compass["orientation_statement"])
    )


def test_observation_signal_authority_and_egress_remain_closed() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == []
    notes = " ".join(node["authority"]["notes"]).lower()
    for phrase in (
        "pure",
        "authored-synthetic",
        "observer emits no truth",
        "no read",
        "proofreader release",
        "live source",
        "durable checkpoint",
    ):
        assert phrase in notes


def test_unresolved_live_and_real_data_gates_remain_explicit() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "patient",
        "product-derived",
        "historical-phi",
        "database/outbox/feed/watcher/listener",
        "operational credentials",
        "checkpoint persistence",
        "restart recovery",
        "product reads",
        "provider calls",
        "clinical",
        "command/write",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_next_candidate_is_source_specific_architecture_only() -> None:
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "diary.appointment_rescheduled.v1",
        "durable monotonic outbox/transaction coordinate",
        "without mounting a source",
        "live database/outbox/feed/watcher/listener",
        "operational credentials",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined
