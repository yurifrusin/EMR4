import ast
import json
from pathlib import Path

from scripts.raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal import (
    EVIDENCE_PATH,
    LOCK_ORDER,
    PACKET_PATH,
    SCHEMA_PATH,
    build_report,
    hostile_mutations,
    simulate_schedule,
    validate_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_packet_schema_and_hostile_gate_pass() -> None:
    packet = _load(PACKET_PATH)
    schema = _load(SCHEMA_PATH)
    evidence = _load(EVIDENCE_PATH)

    assert validate_packet(packet, schema) == []
    report = build_report(packet, schema)
    assert report == evidence
    assert report["status"] == "passed"
    assert report["decision_scenario_count"] == 15
    assert report["transaction_schedule_count"] == 11
    assert report["hostile_mutation_count"] >= 30
    assert report["admitted_hostile_mutations"] == []
    assert not any(report["effect_boundary"].values())


def test_authority_precedes_receipt_disclosure() -> None:
    packet = _load(PACKET_PATH)
    scenario = next(
        item
        for item in packet["decision_scenarios"]
        if item["id"] == "stk-004-authority-before-replay"
    )
    assert scenario["expected"]["outcome"] == "authority_revoked"
    assert scenario["expected"]["receipt_disclosed"] is False


def test_status_lock_order_is_exact_and_schedule_domain_is_skipped() -> None:
    packet = _load(PACKET_PATH)
    assert packet["status_lock_plan"] == LOCK_ORDER
    assert packet["global_lock_order"] == [
        "practice",
        "schedule_domain",
        "appointment",
        "idempotency_record",
    ]
    assert packet["unused_lock_rule"] == "skip_schedule_domain_without_reordering"
    assert all(
        schedule["lock_plan"] == LOCK_ORDER
        for schedule in packet["transaction_schedules"]
    )


def test_precommit_failures_rollback_all_three_components() -> None:
    packet = _load(PACKET_PATH)
    precommit = {
        "before_locks",
        "after_staged_mutation",
        "after_staged_audit",
        "after_staged_receipt",
    }
    for schedule in packet["transaction_schedules"]:
        if schedule["injection"] not in precommit:
            continue
        result = simulate_schedule(schedule)
        durable = result["durable_state"]
        assert durable["mutation_count"] == 0
        assert durable["audit_count"] == 0
        assert durable["completed_receipt_count"] == 0
        assert durable["appointment_version"] == 7


def test_lost_response_is_durable_and_retry_is_effect_free() -> None:
    packet = _load(PACKET_PATH)
    lost = next(
        item for item in packet["transaction_schedules"] if item["id"] == "sts-006-lost-response"
    )
    retry = next(
        item for item in packet["transaction_schedules"] if item["id"] == "sts-007-retry"
    )
    lost_result = simulate_schedule(lost)
    retry_result = simulate_schedule(retry)
    assert lost_result["participant_results"] == ["committed"]
    assert lost_result["response_delivered"] is False
    assert retry_result["participant_results"] == ["committed", "idempotent_replay"]
    assert retry_result["durable_state"]["mutation_count"] == 1
    assert retry_result["durable_state"]["audit_count"] == 1
    assert retry_result["durable_state"]["completed_receipt_count"] == 1


def test_concurrent_losers_are_typed_and_effect_free() -> None:
    packet = _load(PACKET_PATH)
    expected = {
        "sts-008-same-digest": "idempotent_replay",
        "sts-009-different-digest": "idempotency_conflict",
        "sts-010-stale-source": "stale_precondition",
        "sts-011-authority-loss": "authority_revoked",
    }
    for schedule in packet["transaction_schedules"]:
        if schedule["id"] not in expected:
            continue
        result = simulate_schedule(schedule)
        assert result["participant_results"] == ["committed", expected[schedule["id"]]]
        assert result["durable_state"]["mutation_count"] == 1
        assert result["durable_state"]["audit_count"] == 1
        assert result["durable_state"]["completed_receipt_count"] == 1


def test_terminal_retransition_is_deferred_without_effect() -> None:
    packet = _load(PACKET_PATH)
    scenario = next(
        item
        for item in packet["decision_scenarios"]
        if item["id"] == "stk-009-terminal-policy-deferred"
    )
    assert scenario["expected"]["outcome"] == "validation_rejected"
    assert scenario["expected"]["reason"] == "transition_policy_deferred"
    assert scenario["expected"]["planned_effect"] is False


def test_every_hostile_mutation_fails_closed() -> None:
    packet = _load(PACKET_PATH)
    schema = _load(SCHEMA_PATH)
    for name, candidate in hostile_mutations(packet):
        assert validate_packet(candidate, schema), name


def test_script_has_no_application_database_network_or_provider_import() -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden_roots = {
        "app",
        "sqlalchemy",
        "psycopg",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "google",
        "anthropic",
        "openai",
    }
    assert not {name.split(".")[0] for name in imported}.intersection(forbidden_roots)
