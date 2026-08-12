from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal"
)
PARENT = "raisa-status-confirm-preflight-idempotency-expectation-repair"
SOURCE_HEAD = "41f978ae9837cba50737cfb5f457ab62ac28dbdb"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_composition_rehearsal_is_the_accepted_current_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 268
    assert compass["map_revision"] >= 250
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_composition_acceptance_remains_unmounted_and_provider_free() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "unmounted",
        "absent from the router",
        "authored-synthetic in-memory doubles",
        "complete current public envelope",
        "65 hostile mutations",
        "product data",
        "providers",
        "protected integration",
    ):
        assert phrase in joined


def test_next_direction_is_read_only_route_readiness_rereview() -> None:
    current = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free read-only",
        "route-mounting readiness",
        "seven prior blockers",
        "product adapters",
        "physical postgresql",
        "unknown commit",
        "protected-ref",
    ):
        assert phrase in joined


def test_live_handover_names_result_and_next_boundary() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for phrase in (
        "Continuity 268 / Compass 250",
        "raisa_provider_free_unmounted_status_confirm_route_convergence_composition_rehearsal_pass",
        SOURCE_HEAD,
        "provider-free read-only status-confirm route-mounting readiness re-review",
        "Preserve `docs/branding/`",
    ):
        assert phrase in text


def test_all_composition_orchestrator_receipts_pass() -> None:
    root = "orchestration/agent_inbox/codex/"
    stem = (
        "raisa-provider-free-unmounted-status-confirm-route-convergence-"
        "composition-rehearsal"
    )
    for suffix in (
        "-preplanning-receipt.json",
        "-precommit-receipt.json",
        "-closeout-precommit-receipt.json",
    ):
        receipt = _load(root + stem + suffix)
        assert receipt["status"] == "passed"
        assert receipt["rehydrated_from_receipt"] is True
        assert receipt["rehydration_sources"] == [
            "live_handover_current_baton",
            "current_authority_allocation",
            "active_plan_and_acceptance",
            "protected_evidence_boundaries",
            "git_refs_and_worktree",
        ]
