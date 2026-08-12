import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
PARENT = (
    "raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-"
    "readiness-repair"
)
SOURCE_HEAD = "bd381de83bc0b5d4b6b43b4bbb4e1e70a68d7f62"
PARENT_SOURCE_HEAD = "48c1821ad8b28c68204e70dea9972b6ba27e4dc1"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict, node_id: str = NODE_ID) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == node_id]
    assert len(matches) == 1
    return matches[0]


def test_status_protocol_is_the_current_continuity_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 256
    assert compass["map_revision"] == 238
    assert compass["source_graph_revision"] == 256
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_parent_coordinate_is_a_real_corrected_git_object() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    parent = _node(graph, PARENT)
    assert parent["coordinates"]["source_head"] == PARENT_SOURCE_HEAD
    assert any("corrected" in note.lower() for note in parent["authority"]["notes"])


def test_node_keeps_the_protocol_unmounted_and_effect_free() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "authored-synthetic",
        "unmounted",
        "fifteen decision",
        "eleven transaction",
        "thirty-seven hostile",
        "mutation, audit and completed receipt",
        "policy-deferred",
        "no status route",
        "raw status remains mounted and unchanged",
    ):
        assert phrase in joined


def test_compass_names_the_pure_status_adapter_contract_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()
    assert "pure adapter contract next" in joined
    assert "signed-confirmation-envelope" in joined
    assert "terminal parity" in joined
    assert "post-commit receipt serialization" in joined
    assert "continuity 256 / compass 238" in compass["orientation_statement"].lower()


def test_evidence_binds_packet_acceptance_and_yuri_summary() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))
    root = "orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
    assert node["contract_evidence"] == []
    assert f"{root}/protocol-packet.json" in node["evidence"]["artifacts"]
    assert f"{root}/protocol-evidence.json" in node["evidence"]["artifacts"]
    assert (
        "orchestration/agent_inbox/codex/raisa-status-transaction-kernel-protocol-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-transaction-kernel-protocol.md"
        in node["evidence"]["closeouts"]
    )
