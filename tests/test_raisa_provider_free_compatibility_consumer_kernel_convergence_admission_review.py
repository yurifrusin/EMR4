import json
from pathlib import Path

from scripts import (
    raisa_provider_free_compatibility_consumer_kernel_convergence_admission_review as review,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-plan.md"
FINDING = ROOT / "docs/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review.md"
THREAT = ROOT / "docs/security/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-threat-model-delta.md"
INVENTORY = review.INVENTORY


def _inventory() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def test_source_bound_consumer_census_is_exact() -> None:
    result = review.validate()
    assert result["status"] == "passed", result["reasons"]
    assert result["observed"]["counts"] == {
        "create": 51,
        "update": 20,
        "status": 40,
        "delete": 15,
    }
    assert result["observed"]["total"] == 126
    assert len(result["observed"]["files"]) == 21


def test_no_repository_system_consumer_is_inferred_from_conformance_or_fixtures() -> None:
    census = _inventory()["consumer_census"]
    assert census["native_diary_raw_call_expressions"] == 0
    for key in (
        "other_product_runtime_raw_http_consumers",
        "import_raw_http_consumers",
        "recovery_raw_http_consumers",
        "migration_raw_http_consumers",
        "operational_script_raw_http_consumers",
    ):
        assert census[key] == []
    assert len(census["direct_database_non_route_obligations"]) == 4
    assert census["external_consumer_posture"] == "unknown_without_operational_observation"


def test_conformance_health_keeps_stale_tests_as_named_repair_obligations() -> None:
    conformance = _inventory()["consumer_census"]["executable_conformance"]
    broad = conformance["broad_ordinary_collection"]
    assert broad["test_count"] == 311
    assert broad["passed"] == 266
    assert broad["failed"] == 45
    assert broad["failure_classification"] == {
        "past_or_elapsed_time_fixture": 33,
        "missing_required_proposal_idempotency_header": 12,
    }
    assert len(broad["stale_files"]) == 8
    assert conformance["current_behavior_baseline"] == {
        "test_count": 184,
        "passed": 184,
        "failed": 0,
    }


def test_all_four_route_behavior_profiles_are_frozen() -> None:
    inventory = _inventory()
    rows = {row["family"]: row for row in inventory["route_families"]}
    assert set(rows) == {"create", "update", "status", "delete"}
    assert rows["create"]["success_status"] == 201
    assert rows["update"]["success_status"] == 200
    assert rows["status"]["success_body"] == "AppointmentOut"
    assert rows["delete"]["success_status"] == 204
    assert rows["delete"]["success_body"] == "empty"
    assert all(row["kernel_eligible_now"] is False for row in rows.values())
    common = inventory["common_current_behavior"]
    assert common["mutation_and_audit_commit_together"] is True
    assert common["command_idempotency_key_required"] is False
    assert common["completed_command_receipt_written"] is False
    assert common["missing_control_groups"] == [
        "backend_precondition_missing",
        "confirmation_evidence_missing",
        "idempotency_identity_missing",
    ]


def test_status_confirm_first_slice_keeps_raw_patch_unchanged() -> None:
    selected = _inventory()["selected_first_slice"]
    assert selected == {
        "family": "status",
        "slice": "provider_free_unmounted_status_transaction_kernel_protocol_rehearsal",
        "confirm_first": True,
        "raw_route_changed": False,
        "canonical_lock_order": ["practice", "appointment", "idempotency_record"],
        "later_runtime_candidate": "status_confirm_only_before_any_raw_status_convergence",
        "create_excluded": True,
    }
    inventory = _inventory()
    assert inventory["next_dependency_gate"] == (
        "provider_free_compatibility_conformance_harness_temporal_idempotency_readiness_repair"
    )
    assert inventory["status_kernel_protocol_after_next_gate"] is True


def test_parent_contract_rebind_changes_only_two_descendant_document_hashes() -> None:
    rebind = _inventory()["parent_contract_source_rebind"]
    assert rebind["semantic_contract_changed"] is False
    assert len(rebind["root_bindings"]) == 2
    assert {row["path"] for row in rebind["root_bindings"]} == {
        "docs/api-spine/legacy-compatibility-write-deprecation-map.md",
        "docs/api-spine/raw-compat-consumer-signal-readiness.md",
    }
    assert len(rebind["cascade_artifacts"]) == 5
    assert all(
        row["prior_sha256"] != row["current_sha256"]
        for row in rebind["root_bindings"] + rebind["cascade_artifacts"]
    )


def test_plan_finding_and_threat_delta_hold_runtime_and_retirement_closed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in (PLAN, FINDING, THREAT)
    )
    for phrase in (
        "unknown_without_operational_observation",
        "all four routes remain mounted",
        "raw `PATCH` remains unchanged",
        "no kernel, adapter, schedule fence",
        "no database/source/watcher/event",
        "No patient, clinical, product or operational data",
        "Create remains last",
        "No current safety control is weakened",
    ):
        assert phrase in combined
