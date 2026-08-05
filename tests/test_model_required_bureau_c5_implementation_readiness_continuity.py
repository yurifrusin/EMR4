import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-c5-provider-free-implementation-readiness"
SOURCE_HEAD = "d82de54ba59071d231adbf45a3aae1bbc0642ff4"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_c5_implementation_readiness_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 215
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 197
    assert compass["source_graph_revision"] == 215
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "no live C5 result exists yet" in compass["orientation_statement"]


def test_c5_node_opens_only_distinct_pre_execution_preparation():
    node = load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]
    assert node["authority"]["authorized_openings"] == [
        {
            "boundary": "autonomous-action",
            "source": (
                "docs/emr4-model-required-bureau-c5-provider-free-"
                "implementation-readiness-closeout.md"
            ),
            "scope": (
                "Prepare the distinct exact-head C5 pre-execution receipt; "
                "this opening itself performs no live action."
            ),
        }
    ]
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "pre-execution receipt",
        "task-owned target",
        "sydney vertex",
        "two calls",
        "usd 0.50",
        "patient",
        "product-derived",
        "real databases",
        "ordinary services",
        "context fabric",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved


def test_c5_recovery_closes_aer_0027_without_erasing_failed_candidate():
    register = load(
        "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
    )
    assert register["register_revision"] == 23
    incident = next(
        item for item in register["incidents"] if item["incident_id"] == "AER-0027"
    )
    assert incident["status"] == "corrected"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert "45a7a76e0705a2b534779847866507017370c557" in incident["detection_method"]


def test_two_c5_review_outcomes_are_preserved_and_final_head_passes():
    first = load(
        "orchestration/agent_inbox/antigravity/"
        "model-required-bureau-c5-sol-recovery-review-receipt.json"
    )
    final = load(
        "orchestration/agent_inbox/antigravity/"
        "model-required-bureau-c5-sol-recovery-review-2-receipt.json"
    )
    assert first["decision"] == "revision_required"
    assert first["head_before"] == first["head_after"]
    assert first["dirty_after"] is False
    assert final["decision"] == "pass"
    assert final["head_before"] == SOURCE_HEAD
    assert final["head_after"] == SOURCE_HEAD
    assert final["dirty_after"] is False


def test_context_fabric_remains_candidate_and_unimplemented_successor():
    compass = load("orchestration/continuity/emr4-compass.json")
    fabric = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "raisa-practice-context-fabric"
    )
    assert fabric["status"] == "candidate"
    assert fabric["boundary_changes"] == []
    assert "Practice Context Fabric contract" in compass["current_position"][
        "unlocks"
    ][1]
