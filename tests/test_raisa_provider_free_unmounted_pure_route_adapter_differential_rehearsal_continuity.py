import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal"
)
PARENT = "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface"
SOURCE_HEAD = "beb4e65cddf72437948d72e08dd18c2ea4f0c609"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_pure_adapter_rehearsal_is_the_accepted_continuity_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 248
    assert compass["map_revision"] == 230
    assert compass["source_graph_revision"] == 248
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_pure_adapter_rehearsal_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free",
        "no application route",
        "nine adapters",
        "three exact gap codes",
        "forty-five",
        "runtime-ineligible",
        "patient/product data",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_names_non_enforcing_shadow_architecture_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()

    assert "shadow-comparison" in joined
    assert "cannot gate" in joined
    assert "cannot" in joined and "mutate" in joined
    assert "continuity 248 / compass 230" in compass["orientation_statement"].lower()
    assert "45 hostile mutations" in compass["orientation_statement"]


def test_evidence_binds_receipts_acceptance_and_human_summary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    evidence = _node(graph)["evidence"]

    assert (
        "orchestration/agent_inbox/codex/"
        "raisa-pure-route-adapter-differential-rehearsal-preplanning-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/"
        "raisa-pure-route-adapter-differential-rehearsal-"
        "candidate-precommit-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/"
        "2026-08-12--pure-route-adapter-differential-rehearsal.md"
        in evidence["closeouts"]
    )
