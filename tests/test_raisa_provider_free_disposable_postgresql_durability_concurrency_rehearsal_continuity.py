from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
SOURCE_HEAD = "fed81847b4155d49cf997905e79cf31808ceb017"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_cf_d1_is_current_and_points_to_cf_d2() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 243
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 225
    assert compass["source_graph_revision"] == 243
    assert compass["current_position"]["node_id"] == NODE_ID
    orientation = compass["orientation_statement"].lower()
    for phrase in (
        "cf-d1 proves six exact",
        "postgresql 16",
        "bounded overlap",
        "zero retry",
        "exact cleanup",
        "cf-d2",
        "restart and unknown-commit",
        "standing authority",
    ):
        assert phrase in orientation


def test_cf_d1_opens_no_continuing_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "six fixed",
        "zero automatic retries",
        "crash/restart",
        "unknown commit",
        "operational database/source",
        "patient/clinical data",
        "provider",
        "tool",
        "command",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_cf_d1_pass_and_recovery_evidence_are_bound() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    findings = set(node["evidence"]["findings"])
    assert {
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence-attempt-002.json",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence-attempt-003.json",
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence-attempt-004.json",
    } <= findings
    assert (
        "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-replay-vocabulary-recovery-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/raisa-context-fabric-durability-concurrency-rehearsal-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--context-fabric-durability-concurrency-rehearsal.md"
        in node["evidence"]["closeouts"]
    )


def test_cf_d1_immutable_pass_evidence_is_exact() -> None:
    evidence = _load(
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
        "durability-concurrency-rehearsal/"
        "provider-free-durability-concurrency-evidence-attempt-004.json"
    )

    assert evidence["result"] == (
        "raisa_provider_free_disposable_postgresql_"
        "durability_concurrency_rehearsal_pass"
    )
    assert evidence["scenario_reconciliation"] == {
        "expected": 6,
        "observed": 6,
        "passed": 6,
    }
    assert evidence["operation_counts"] == {
        "participant_transactions": 12,
        "precondition_transactions": 11,
        "participant_retries": 0,
        "docker_containers": 1,
        "provider_calls": 0,
        "product_reads": 0,
        "product_commands": 0,
        "external_network_operations": 0,
    }
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    assert evidence["cleanup"]["removed"] is True
    assert evidence["cleanup"]["absence_verified"] is True
    assert all(scenario["passed"] for scenario in evidence["scenarios"])


def test_cf_d2_handoff_stays_narrow_and_fail_closed() -> None:
    position = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(position["unlocks"] + position["does_not_solve"]).lower()

    for phrase in (
        "definitely committed",
        "definitely rolled back",
        "genuinely indeterminate",
        "without guessing success",
        "fresh five-source rehydration",
        "real/product/patient/clinical data",
        "tools or commands",
        "production",
        "protected-ref",
    ):
        assert phrase in joined
