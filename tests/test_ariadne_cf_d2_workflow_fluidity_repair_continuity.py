import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair"
PARENT = "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
SOURCE_HEAD = "018099dd6c5f0502121360732feb602252eb34cc"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_workflow_repair_is_the_accepted_maintenance_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 244
    assert compass["map_revision"] == 226
    assert compass["source_graph_revision"] == 244
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "maintenance"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_workflow_repair_opens_no_authority_and_does_not_accept_cf_d2() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "does not accept or reopen cf-d2",
        "crash/restart",
        "unknown-commit",
        "key rotation",
        "retention/purge",
        "patient/clinical",
        "provider tools",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_requires_a_genuine_programme_choice() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()
    assert "independent programme" in joined
    assert "observability-first cf-d2" in joined
    assert "key rotation" in joined
    assert "no automatic durability tranche" in compass["orientation_statement"].lower()


def test_accepted_evidence_binds_review_and_human_summary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    evidence = _node(graph)["evidence"]
    assert (
        "orchestration/agent_inbox/antigravity/"
        "ariadne-cf-d2-workflow-fluidity-final-review-v2-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/"
        "2026-08-12--cf-d2-workflow-incident-diagnosis-and-fluidity-repair.md"
        in evidence["closeouts"]
    )
