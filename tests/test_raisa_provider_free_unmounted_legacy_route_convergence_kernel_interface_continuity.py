import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface"
PARENT = "raisa-provider-free-unmounted-conditional-command-admission-rehearsal"
SOURCE_HEAD = "47e08eada878d8f6dd2a9b100e706404d3594e5a"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _node(graph: dict) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == NODE_ID]
    assert len(matches) == 1
    return matches[0]


def test_convergence_design_is_the_accepted_continuity_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 247
    assert compass["map_revision"] == 229
    assert compass["source_graph_revision"] == 247
    assert compass["current_position"]["node_id"] == NODE_ID
    node = _node(graph)
    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_convergence_design_opens_no_runtime_authority() -> None:
    node = _node(_load("orchestration/continuity/emr4-continuity-graph.json"))

    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "provider-free",
        "no application route",
        "four raw",
        "forty-eight",
        "kernel-ineligible",
        "patient/product data",
        "protected refs",
    ):
        assert phrase in joined


def test_compass_names_pure_route_adapter_rehearsal_next() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(
        [current["strategic_role"], current["why_now"], current["outcome"]]
        + current["unlocks"]
        + current["does_not_solve"]
    ).lower()

    assert "route-adapter differential" in joined
    assert "conditionalappointmentcommand" in joined
    assert "four raw, six proposal and five confirm" in joined
    assert "continuity 247 / compass 229" in compass["orientation_statement"].lower()
    assert "48 hostile mutations" in compass["orientation_statement"]


def test_evidence_binds_failed_corrected_receipts_and_human_summary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    evidence = _node(graph)["evidence"]

    assert (
        "orchestration/agent_inbox/codex/"
        "raisa-legacy-route-convergence-kernel-interface-preplanning-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/"
        "raisa-legacy-route-convergence-kernel-interface-preplanning-v2-receipt.json"
        in evidence["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/"
        "2026-08-12--legacy-route-convergence-kernel-interface.md"
        in evidence["closeouts"]
    )
