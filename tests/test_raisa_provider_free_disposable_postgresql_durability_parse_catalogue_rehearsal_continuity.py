import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal"
)
SOURCE_HEAD = "c3ca2515b9f2c4b20cb7230364de7417f48eab54"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_disposable_postgresql_catalogue_continuity_is_current() -> None:
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 232
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 214
    assert compass["source_graph_revision"] == 232
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "behavior/transaction rehearsal is next" in compass[
        "orientation_statement"
    ].lower()


def test_catalogue_acceptance_opens_no_behavioral_authority() -> None:
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
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
    compass = load("orchestration/continuity/emr4-compass.json")
    position = compass["current_position"]
    joined = " ".join(
        position["unlocks"]
        + position["does_not_solve"]
        + [compass["orientation_statement"]]
    ).lower()
    for phrase in (
        "behavior/transaction",
        "entry-point",
        "trigger",
        "rls",
        "applied migration",
        "database/outbox/feed/watcher/listener/source",
        "patient/product data",
        "commands",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_terminal_evidence_review_and_error_register_bind_result() -> None:
    base = (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
        "durability-parse-catalogue-rehearsal/"
    )
    evidence = load(base + "provider-free-disposable-postgresql-evidence.json")
    characterization = load(
        base
        + "provider-free-disposable-postgresql-evidence-catalogue-characterization.json"
    )
    contract = load(base + "rehearsal-contract.json")
    review = load(
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
        "exact-catalogue-binding-review-receipt.json"
    )
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert evidence["result"].endswith("parse_catalogue_rehearsal_pass")
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["cleanup"]["absence_verified"] is True
    expected = {
        key: value
        for key, value in characterization["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert contract["catalogue_expectation"]["expected_query_digests"] == expected
    assert evidence["catalogue"]["query_digests"] | {
        "server": characterization["catalogue"]["query_digests"]["server"],
        "extensions": characterization["catalogue"]["query_digests"]["extensions"],
    } == characterization["catalogue"]["query_digests"]
    assert review["decision"] == "pass"
    assert review["dirty_after"] is False
    assert register["register_revision"] >= 90
    assert register["incidents"][-1]["incident_id"] == "AER-0109"
    assert not [item for item in register["incidents"] if item["status"] == "open"]
