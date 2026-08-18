from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest
import yaml
from jsonschema import ValidationError

from scripts.ariadne_agent_error_register import (
    REGISTER_PATH,
    ROOT,
    SCHEMA_PATH,
    build_pattern_report,
    validate_register,
    write_json_lf,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _register() -> dict:
    return _json(REGISTER_PATH)


def _schema() -> dict:
    return _json(SCHEMA_PATH)


def test_register_is_valid_after_durability_schema_recovery() -> None:
    register = _register()

    validate_register(register, _schema())

    assert register["schema_version"] == "ariadne.agent-error-register.v1"
    assert register["register_revision"] == 495
    assert register["scope"]["coverage"] == "bounded_known_preserved_incidents"
    assert [row["incident_id"] for row in register["incidents"]] == [
        f"AER-{index:04d}" for index in range(1, 575)
    ]
    assert [
        row["incident_id"] for row in register["incidents"] if row["status"] == "open"
    ] == []


def test_seed_separates_agent_behavior_from_transport() -> None:
    incidents = _register()["incidents"]
    agent_incidents = [row for row in incidents if row["origin"] == "agent_behavior"]
    transport_incidents = [row for row in incidents if row["origin"] == "transport"]

    assert len(agent_incidents) == 403
    assert len(transport_incidents) == 16
    assert [row["incident_id"] for row in transport_incidents] == [
        "AER-0007",
        "AER-0022",
        "AER-0031",
        "AER-0034",
        "AER-0036",
        "AER-0038",
        "AER-0039",
        "AER-0081",
        "AER-0198",
        "AER-0326",
        "AER-0367",
        "AER-0380",
        "AER-0382",
        "AER-0391",
        "AER-0419",
        "AER-0427",
    ]
    assert {row["category"] for row in transport_incidents} == {"transport_timeout"}
    assert {row["causal_claim_level"] for row in transport_incidents} == {
        "observation_only"
    }

    r7_transport = next(
        row for row in transport_incidents if row["incident_id"] == "AER-0081"
    )
    assert r7_transport["status"] == "corrected"
    assert r7_transport["correction"]["status"] == "corrected_fresh_attempt"
    assert any(
        path.endswith("r7-final-review-retry-receipt.json")
        for path in r7_transport["correction"]["evidence_paths"]
    )


def test_r7_continuity_baseline_repository_defects_are_corrected() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    for incident_id in ("AER-0082", "AER-0083"):
        incident = incidents[incident_id]
        assert incident["origin"] == "repository"
        assert incident["category"] == "repository_defect"
        assert incident["candidate_state"] == "canonical_unchanged"
        assert incident["status"] == "corrected"
        assert incident["correction"]["status"] == "control_added"
    assert incidents["AER-0082"]["related_incident_ids"] == ["AER-0083"]
    assert incidents["AER-0083"]["related_incident_ids"] == ["AER-0082"]


def test_inert_ddl_plan_challenge_incidents_are_preserved_and_contained() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    predispatch = incidents["AER-0084"]
    assert predispatch["category"] == "output_contract_violation"
    assert predispatch["status"] == "corrected"
    assert predispatch["correction"]["status"] == "corrected_fresh_attempt"
    assert "pre_worker_dispatch" in predispatch["correction"]["action"]

    verifier = incidents["AER-0085"]
    assert verifier["category"] == "evidence_misreport"
    assert verifier["process_severity"] == "material"
    assert verifier["workflow_disposition"] == "review_rejected"
    assert verifier["status"] == "corrected"
    assert verifier["correction"]["status"] == "corrected_fresh_attempt"
    assert "F_CARDINALITY/CF004" in verifier["correction"]["action"]

    inventory = incidents["AER-0086"]
    assert inventory["category"] == "output_contract_violation"
    assert inventory["status"] == "corrected"
    assert inventory["correction"]["status"] == "corrected_fresh_attempt"
    assert "deepseek-flash-workers" in inventory["correction"]["action"]


def test_observation_signal_worker_veto_requires_fresh_acceptance() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0046"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["status"] == "corrected"


def test_observation_signal_sol_recovery_requires_two_sided_clock_veto() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0047"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["related_incident_ids"] == []
    assert rows["AER-0046"]["related_incident_ids"] == []
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["status"] == "corrected"


def test_durability_schema_veto_requires_exact_list_recovery() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0048"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["status"] == "corrected"


def test_durability_state_plan_veto_requires_complete_recovery_semantics() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0049"
    )
    assert incident["status"] == "corrected"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    joined = " ".join(
        (
            incident["expected_invariant"],
            incident["observed_error"],
            incident["correction"]["action"],
        )
    ).lower()
    for phrase in (
        "complete non-consumed-generation census",
        "recoveryanchor",
        "future-position-fenced",
        "predecessor",
    ):
        assert phrase in joined


def test_durability_state_candidate_veto_is_closed_by_fresh_review() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0050"
    )
    assert incident["status"] == "corrected"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "recovery_lease_applied"


def test_migration_architecture_plan_veto_and_review_bootstrap_are_preserved() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    plan = incidents["AER-0051"]
    assert plan["status"] == "corrected"
    assert plan["workflow_disposition"] == "recovery_lease_invoked"
    assert plan["category"] == "reasoning_claim_error"
    assert plan["correction"]["status"] == "recovery_lease_applied"
    assert "bounded PRIMARY/CONFLICT admission" in plan["correction"]["action"]
    assert "purge-safe comparison" in plan["correction"]["action"]
    assert (
        "sole owner-private immutable alias bijection" in plan["correction"]["action"]
    )
    assert "exact low-XID32 provenance" in plan["correction"]["action"]
    assert "all-UPDATE appointment constraint trigger" in plan["correction"]["action"]
    assert "no-write savepoints not database-observable" in plan["correction"]["action"]
    assert (
        "persistent outbox-to-product-event foreign key" in plan["correction"]["action"]
    )
    assert "44 executable RLS policies" in plan["correction"]["action"]
    assert "digest-resealed semantic validator" in plan["correction"]["action"]
    assert "structural renderer" in plan["correction"]["action"]
    assert "function-and-trigger-body architecture" in plan["correction"]["action"]
    assert "appointments SELECT" in plan["correction"]["action"]
    assert "c55d25d6c9704ae4612ef2d123158f71302ab411" in plan["correction"]["action"]

    process = incidents["AER-0052"]
    assert process["status"] == "corrected"
    assert process["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert process["category"] == "command_scope_violation"
    assert process["recurrence_signature"] == (
        "verifier.unapproved_environment_bootstrap"
    )
    assert process["correction"]["status"] == "corrected_fresh_attempt"
    assert (
        "uv, pip and environment bootstrap"
        in process["correction"]["prevention_control"]
    )


def test_migration_architecture_recovery_review_path_enumeration_is_contained() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0053"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "verifier.forbidden_repository_path_enumeration"
    )
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert "no Git discovery command" in incident["correction"]["prevention_control"]
    assert incident["status"] == "contained"


def test_migration_architecture_recovery_broad_search_is_contained() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0054"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "orchestrator.overbroad_repository_content_search"
    )
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert (
        "explicit exact-path read allowlist"
        in incident["correction"]["prevention_control"]
    )
    assert incident["status"] == "contained"


def test_migration_architecture_recovery_dispatch_receipt_failed_closed() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0055"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "pre_worker_dispatch" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_migration_architecture_reviewer_preflight_requires_full_head() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0056"]

    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.verifier_expected_head_not_full_sha"
    )
    assert "complete git rev-parse HEAD" in incident["correction"]["prevention_control"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_migration_architecture_review_packet_paths_are_preflighted() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0057"]

    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.review_packet_missing_allowlisted_path"
    )
    assert (
        "Test-Path every exact allowlisted file"
        in incident["correction"]["prevention_control"]
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_continuity_updater_uses_package_module_invocation() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0058"]

    assert incident["role"] == "orchestrator"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.python_package_script_path_invocation"
    )
    assert "python -m scripts" in incident["correction"]["prevention_control"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_function_trigger_body_recovery_incidents_are_preserved_and_corrected() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert incidents["AER-0059"]["recurrence_signature"] == (
        "implementer.semantic_labels_without_executable_operands"
    )
    assert incidents["AER-0060"]["recurrence_signature"] == (
        "implementer.typed_ir_systemic_relation_and_source_misbinding"
    )
    assert incidents["AER-0061"]["recurrence_signature"] == (
        "orchestrator.dispatch_before_exact_postcommit_receipt"
    )
    assert incidents["AER-0062"]["recurrence_signature"] == (
        "orchestrator.receipt_head_evidence_not_git_verified"
    )
    assert all(
        incidents[incident_id]["status"] == "corrected"
        for incident_id in ("AER-0059", "AER-0060", "AER-0061", "AER-0062")
    )


def test_function_trigger_body_verifier_path_failure_uses_short_recovery() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0063"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-long-worktree-failure-receipt.json"
    )

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "harness.windows_verifier_worktree_destination_path_too_long"
    )
    assert receipt["candidate_head"] == ("f51f5b65dd77d9282e5325a5e4f17edd872d14df")
    assert receipt["postcondition"] == {
        "destination_exists": False,
        "worktree_registered": False,
        "reviewer_dispatched": False,
        "candidate_changed": False,
        "protected_ref_changed": False,
    }
    assert receipt["correction"]["next_destination"].endswith("/r33")
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_function_trigger_body_exact_veto_is_contained_pending_fresh_acceptance() -> (
    None
):
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0064"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "independent_review"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["recurrence_signature"] == (
        "implementer.typed_ir_structurally_valid_but_normatively_underclosed"
    )
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "contained"

    review = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-exact-veto.md"
    ).read_text(encoding="utf-8")
    recovery = (
        ROOT
        / "docs"
        / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture-exact-veto-recovery.md"
    ).read_text(encoding="utf-8")
    assert "DECISION: revision_required" in review
    assert "absence of effects caused by this exact" in recovery
    assert "top-level" in recovery
    assert "regenerated-baseline byte equality" in recovery


def test_function_trigger_body_recovery_receipt_preserves_empty_required_pool() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0065"]
    failed = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-exact-veto-recovery-precommit-v2-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-exact-veto-recovery-precommit-v3-receipt.json"
    )
    corrected_state = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-exact-veto-recovery-precommit-v3-runtime-state.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert failed["status"] == "revision_required"
    assert failed["reasons"] == ["worker_slot_inventory_missing:deepseek-flash-workers"]
    assert corrected["status"] == "passed"
    assert corrected["reasons"] == []
    inventories = {
        row["resource_id"]: (row["active_instance_ids"], row["stale_instance_ids"])
        for row in corrected_state["worker_slots"]
    }
    assert inventories["deepseek-flash-workers"] == ([], [])
    assert incident["status"] == "corrected"


def test_function_trigger_schema_module_path_failure_reuses_package_control() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0066"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-schema-direct-invocation-failure-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.python_package_script_path_invocation"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert receipt["reason_code"] == "python_package_module_invoked_by_path"
    assert receipt["candidate_changed"] is False
    assert receipt["correction"]["result"] == "module_import_pass"
    assert incident["status"] == "corrected"


def test_function_trigger_builder_path_failure_tightens_package_control() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0067"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-builder-direct-invocation-failure-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.python_package_script_path_invocation"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert receipt["failure_point"] == (
        "schema_module_import_before_artifact_open_or_write"
    )
    assert receipt["generated_artifact_changed_by_failed_attempt"] is False
    assert receipt["correction"]["result"] == "contract_and_schema_generated"
    assert incident["status"] == "corrected"


def test_function_trigger_api_spine_baseline_drift_is_contained() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0068"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-api-spine-baseline-failure-receipt.json"
    )

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.api_spine_historical_expectation_drift"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert receipt["remaining_cohort"] == {
        "file_count": 57,
        "collected_test_count": 535,
        "passed_test_count": 530,
        "failed_test_count": 5,
        "failed_paths": [
            "tests/test_api_spine_update_confirm_idempotency_preflight.py",
            "tests/test_api_spine_status_confirm_idempotency_preflight.py",
            "tests/test_api_spine_practitioner_directory_security_audit_preflight.py",
            "tests/test_api_spine_idempotency_continuity_index.py",
            "tests/test_api_spine_external_read_model_gap_inventory.py",
        ],
        "failure_class": "historical_preflight_or_inventory_expectation_drift",
    }
    assert receipt["implicated_paths_changed_since_source_head"] is False
    assert incident["status"] == "contained"


def test_function_trigger_current_digest_provenance_is_corrected_before_review() -> (
    None
):
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0069"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-current-digest-correction-receipt.json"
    )
    design = (
        ROOT
        / "docs"
        / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture-design.md"
    ).read_text(encoding="utf-8")

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["recurrence_signature"] == (
        "orchestrator.current_candidate_digest_provenance_mismatch"
    )
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert receipt["status"] == "corrected_before_independent_review"
    assert receipt["expected_digest"] in design
    assert receipt["correction"]["contract_or_schema_changed"] is False


def test_function_trigger_second_exact_veto_remains_contained_for_fresh_recovery() -> (
    None
):
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0070"]
    review = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-rebuilt-candidate-exact-veto.md"
    ).read_text(encoding="utf-8")
    recovery = (
        ROOT
        / "docs"
        / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture-second-exact-veto-recovery.md"
    ).read_text(encoding="utf-8")

    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "contained"
    assert "128/128 passed" in review
    assert "DECISION: revision_required" in review
    for phrase in (
        "SET_CONTAINS_KEY",
        "SET_COVERS_KEYS",
        "classified_receipt_digest_v1",
        "complete registration replay",
        "field-specific",
    ):
        assert phrase in recovery


def test_function_trigger_reviewer_ruff_boolean_failure_is_corrected_cleanly() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0071"]
    review = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-rebuilt-candidate-exact-veto.md"
    ).read_text(encoding="utf-8")

    assert incident["role"] == "verifier"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert "RUFF_NO_CACHE=1" in review
    assert "RUFF_NO_CACHE=true" in review
    assert "Final `git status --short`: empty" in review


def test_function_trigger_reviewer_path_transcription_failure_is_corrected_cleanly() -> (
    None
):
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0072"]
    review = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-r6-independent-veto.md"
    ).read_text(encoding="utf-8")

    assert incident["role"] == "verifier"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert "hyphenated filename" in review
    assert "exact prescribed Ruff rerun passed" in review
    assert "Exact HEAD was clean before and after review" in review


def test_function_trigger_third_exact_veto_remains_contained_for_fresh_recovery() -> (
    None
):
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0073"]
    review = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-r6-independent-veto.md"
    ).read_text(encoding="utf-8")
    recovery = (
        ROOT
        / "docs"
        / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture-third-exact-veto-recovery.md"
    ).read_text(encoding="utf-8")

    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "contained"
    assert "passed 192/192" in review
    assert "DECISION: revision_required" in review
    for phrase in (
        "source-independent replay",
        "complete recovery anchors",
        "checkpoint_rebase_digest_v1",
        "key_rotation_digest_v1",
        "uniqueItems: true",
    ):
        assert phrase in recovery


def test_function_trigger_r6_predispatch_managed_inventory_is_corrected() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0074"]
    failed = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-r6-implementation-predispatch-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-r6-implementation-predispatch-v2-receipt.json"
    )

    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert failed["status"] == "revision_required"
    assert failed["worker_dispatch_permitted"] is False
    assert failed["reasons"] == ["worker_slot_inventory_missing:deepseek-flash-workers"]
    assert corrected["status"] == "passed"
    assert corrected["worker_dispatch_permitted"] is True


def test_function_trigger_r6_parent_branch_mismatch_invokes_recovery() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    parent_mismatch = rows["AER-0075"]
    nonterminal = rows["AER-0076"]
    evidence = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-function-trigger-body-architecture-r6-anchor-challenger-interrupted.md"
    ).read_text(encoding="utf-8")
    recovery = (
        ROOT
        / "docs"
        / "raisa-provider-free-unmounted-durability-function-trigger-body-architecture-third-exact-veto-recovery.md"
    ).read_text(encoding="utf-8")

    assert parent_mismatch["category"] == "reasoning_claim_error"
    assert parent_mismatch["candidate_state"] == "untrusted_partial_worktree"
    assert parent_mismatch["workflow_disposition"] == "recovery_lease_invoked"
    assert parent_mismatch["status"] == "contained"
    assert nonterminal["category"] == "output_contract_violation"
    assert nonterminal["role"] == "verifier"
    assert nonterminal["status"] == "contained"
    assert "source_position IS NULL" in evidence
    assert "terminal acceptance decision" in evidence
    assert "latest earlier audit head" in recovery
    assert "necessarily NULL lifecycle source position" in recovery


def test_operational_weave_auth_timeout_is_sanitized_and_recovered() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0034"
    )
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-current-operational-weave-auth-timeout-failure-receipt.json"
    )
    review = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "raisa-context-fabric-current-operational-weave-review-1-receipt.json"
    )

    assert incident["origin"] == "transport"
    assert incident["status"] == "corrected"
    assert failure["packet_delivered_to_model"] is False
    assert failure["provider_or_model_calls"] == 0
    assert failure["credentials_or_oauth_values_retained"] is False
    assert review["decision"] == "pass"
    assert review["head_before"] == review["head_after"] == failure["head_before"]
    assert review["dirty_after"] is False


def test_invalidation_reassembly_orchestration_failures_are_contained() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    dispatch = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-rayleen-invalidation-reassembly-worker-predispatch-ordering-failure-receipt.json"
    )
    search = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-rayleen-invalidation-reassembly-register-search-scope-failure-receipt.json"
    )

    assert rows["AER-0043"]["category"] == "command_scope_violation"
    assert rows["AER-0043"]["status"] == "corrected"
    assert (
        dispatch["containment"]["worker_interrupted_before_candidate_acceptance"]
        is True
    )
    assert dispatch["containment"]["worker_source_adopted"] is False
    assert rows["AER-0044"]["category"] == "command_scope_violation"
    assert rows["AER-0044"]["status"] == "contained"
    assert search["containment"]["broad_output_used_for_candidate_analysis"] is False
    assert search["containment"]["literal_path_chunked_read_substituted"] is True


def test_operational_weave_review_count_is_reconciled_at_exact_head() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0035"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-current-operational-weave-review-count-reconciliation-receipt.json"
    )

    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"
    assert receipt["review_decision"] == "pass"
    assert receipt["review_claimed_test_count"] == 71
    assert receipt["authoritative_reproduced_test_count"] == 155
    assert sum(receipt["collection_breakdown"].values()) == 155
    assert receipt["reproduction"]["execution_status"] == "passed"
    assert (
        receipt["reproduction"]["head_before"] == receipt["reproduction"]["head_after"]
    )
    assert receipt["reproduction"]["dirty_after"] is False
    assert receipt["additional_provider_calls"] == 0


def test_temporal_weave_deepseek_timeout_is_sanitized_and_contained() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0036"
    )
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-patient-free-temporal-weave-deepseek-timeout-failure-receipt.json"
    )

    assert incident["origin"] == "transport"
    assert incident["role"] == "implementer"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert failure["status"] == "failed_closed"
    assert failure["secrets_recorded"] is False
    assert failure["owned_files_created"] == []
    assert failure["candidate_commit"] is None
    assert failure["protected_refs_moved"] is False
    assert failure["recovery"]["scope_changed"] is False


def test_temporal_weave_review_evidence_is_reconciled_at_exact_head() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0037"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-patient-free-temporal-weave-review-evidence-reconciliation-receipt.json"
    )

    assert incident["category"] == "evidence_misreport"
    assert incident["status"] == "corrected"
    assert incident["recurrence_signature"] == (
        "verifier.exact_packet_test_count_underreport"
    )
    assert receipt["review_decision"] == "pass"
    assert receipt["review_claimed_test_count"] == 67
    assert receipt["authoritative_reproduced_test_count"] == 120
    assert sum(receipt["collection_breakdown"].values()) == 120
    assert receipt["reproduction"]["passed"] == 120
    assert (
        receipt["reproduction"]["head_before"] == receipt["reproduction"]["head_after"]
    )
    assert receipt["reproduction"]["dirty_after"] is False
    assert (
        receipt["review_claimed_failure_receipt_path"]
        != receipt["authoritative_failure_receipt_path"]
    )
    assert receipt["additional_provider_calls"] == 0


def test_source_adapter_deepseek_timeout_is_sanitized_and_contained() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0038"
    )
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-rayleen-waiting-room-source-adapter-deepseek-timeout-failure-receipt.json"
    )

    assert incident["origin"] == "transport"
    assert incident["role"] == "implementer"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert failure["status"] == "contained_transport_timeout"
    assert failure["observation"]["owned_files_created_or_modified"]
    assert failure["observation"]["candidate_commit_created"] is False
    assert failure["observation"]["tracked_worktree_clean_after_stop"] is False
    assert failure["observation"]["late_partial_writes_detected"] is True
    assert failure["containment"]["worker_source_adopted"] is False
    assert failure["containment"]["provider_call_made"] is False
    assert failure["containment"]["product_or_database_accessed"] is False
    assert failure["containment"]["protected_ref_moved"] is False


def test_source_adapter_antigravity_timeout_is_sanitized_and_falls_back() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0039"
    )
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "raisa-context-fabric-rayleen-waiting-room-source-adapter-auth-timeout-failure-receipt.json"
    )

    assert incident["origin"] == "transport"
    assert incident["role"] == "verifier"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert failure["status"] == "transport_failed"
    assert failure["packet_delivered_to_model"] is False
    assert failure["provider_or_model_calls"] == 0
    assert failure["credentials_or_oauth_values_retained"] is False
    assert failure["bounded_retry_exhausted"] is True
    assert failure["candidate_unchanged"] is True
    assert failure["head_before"] == failure["head_after"]


def test_source_adapter_review_worktree_regeneration_is_restored() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0040"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-rayleen-waiting-room-source-adapter-review-worktree-postcondition-recovery-receipt.json"
    )

    assert incident["category"] == "read_only_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"
    assert receipt["status"] == "restored_exact_committed_state"
    assert len(receipt["observed_mutations"]) == 2
    assert receipt["head_before"] == receipt["head_after"] == receipt["required_head"]
    assert receipt["source_or_test_code_changed"] is False
    assert receipt["candidate_commit_changed"] is False
    assert receipt["candidate_worktree_clean_after"] is True
    assert receipt["provider_or_model_calls"] == 0
    assert receipt["product_or_database_reads"] == 0
    assert receipt["protected_ref_updates"] == 0


def test_source_adapter_protected_path_enumeration_attempt_is_rejected() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0041"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-rayleen-source-adapter-protected-path-enumeration-failure-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert receipt["status"] == "attempt_rejected_and_contained"
    assert receipt["incident"]["protected_path_names_observed"] is True
    assert receipt["incident"]["protected_file_content_opened_or_read"] is False
    assert receipt["incident"]["protected_hash_or_metadata_queried"] is False
    assert receipt["incident"]["patient_or_product_data_accessed"] is False
    assert receipt["candidate"]["candidate_changed"] is False
    assert receipt["candidate"]["tracked_clean_after_containment"] is True
    assert (
        receipt["correction"]["next_attempt_requires_exact_allowlisted_paths"] is True
    )


def test_source_adapter_review_packet_count_is_exactly_reconciled() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0042"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-rayleen-source-adapter-review-packet-count-reconciliation-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"
    assert receipt["classification"]["reviewer_error"] is False
    assert receipt["classification"]["candidate_finding"] is False
    assert receipt["observed_run"]["actual_collected_and_passed_count"] == 167
    assert receipt["observed_run"]["incorrectly_named_path_test_count"] == 3
    assert receipt["correction"]["required_path_test_count"] == 31
    assert receipt["correction"]["corrected_expected_test_count"] == 195
    assert receipt["correction"]["arithmetic_reconciliation"] == "167 - 3 + 31 = 195"
    assert receipt["candidate_changed"] is False


def test_a5_worker_scope_breach_closes_only_through_recovery_lease() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0021"
    )
    review = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-a5-b4-code-review-receipt.json"
    )

    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert review["decision"] == "pass"
    assert review["head_before"] == review["head_after"]
    assert review["dirty_after"] is False


def test_antigravity_auth_timeout_retains_no_oauth_material_or_fake_decision() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0022"
    )
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-a5-b4-code-review-1-auth-transport-failure.json"
    )
    review = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-a5-b4-code-review-receipt.json"
    )

    assert incident["origin"] == "transport"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert failure["review_prompt_transmitted"] is False
    assert failure["reviewer_decision_produced"] is False
    assert failure["raw_authorization_url_retained"] is False
    assert failure["authorization_code_or_credential_retained"] is False
    assert review["decision"] == "pass"
    assert review["head_before"] == failure["candidate_head"]
    assert review["head_after"] == failure["candidate_head"]
    assert review["dirty_after"] is False


def test_c4_preplan_event_failure_is_preserved_before_corrected_receipt() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0023"
    )
    failed = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c4-preplan-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c4-preplan-2-receipt.json"
    )

    assert incident["status"] == "corrected"
    assert incident["recurrence_signature"] == (
        "orchestrator.unapproved_continuation_event"
    )
    assert failed["continuation_event"] == "pre_plan"
    assert failed["status"] == "revision_required"
    assert failed["worker_dispatch_permitted"] is False
    assert corrected["continuation_event"] == "pre_sprint_planning"
    assert corrected["status"] == "passed"
    assert corrected["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]


def test_c4_worker_dispatch_contract_fails_closed_before_corrected_receipt() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0024"
    )
    failed = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c4-worker-predispatch-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c4-worker-predispatch-2-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["status"] == "corrected"
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )
    assert failed["status"] == "revision_required"
    assert failed["worker_dispatch_permitted"] is False
    assert set(failed["reasons"]) == {
        "adapter_probe_method_invalid:deepseek_via_claude_code_bare",
        "workspace_receipt_missing:model-required-bureau-c4-simulator-001",
    }
    assert corrected["status"] == "passed"
    assert corrected["worker_dispatch_permitted"] is True
    assert corrected["reasons"] == []


def test_c4_worker_self_pass_is_corrected_only_through_sol_recovery() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0025"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "deepseek"
        / "model-required-bureau-c4-simulator-worker-receipt.json"
    )
    review = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c4-worker-independent-review.md"
    ).read_text(encoding="utf-8")

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    verifier = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-c4-code-review-receipt.json"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert receipt["model"] == "deepseek-v4-flash"
    assert "DECISION: pass" in receipt["result"]
    assert "P1 — malformed scalar input" in review
    assert "P1 — fresh readback" in review
    assert "Disposition: `revision_required`" in review
    assert verifier["decision"] == "pass"
    assert verifier["head_after"] == "955b6a566f7097f58929dcb2fa9c4ed0aaad8b29"
    assert verifier["dirty_after"] is False


def test_c4_bounded_repair_self_pass_is_corrected_by_exact_transactional_controls() -> (
    None
):
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0026"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "deepseek"
        / "model-required-bureau-c4-simulator-repair-worker-receipt.json"
    )
    audit = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c4-repair-independent-audit.md"
    ).read_text(encoding="utf-8")

    assert incident["related_incident_ids"] == []
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["status"] == "corrected"
    assert receipt["model"] == "deepseek-v4-flash"
    assert "DECISION: pass" in receipt["result"]
    assert "Current reviewer role is not bound" in audit
    assert "Current-authority mutation is not transactionally excluded" in audit
    assert "One-use evidence is not atomic across runtime instances" in audit
    assert "Disposition: `revision_required`" in audit
    action = incident["correction"]["action"]
    assert "shared execution-store transaction" in action
    assert "exact reviewer role" in action


def test_c5_worker_self_pass_remains_rejected_after_sol_recovery() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0027"
    )
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "deepseek"
        / "model-required-bureau-c5-implementation-worker-receipt.json"
    )
    audit = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c5-worker-independent-audit.md"
    ).read_text(encoding="utf-8")

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["status"] == "corrected"
    assert (
        "d82de54ba59071d231adbf45a3aae1bbc0642ff4" in incident["correction"]["action"]
    )
    assert receipt["model"] == "deepseek-v4-flash"
    assert "DECISION: pass" in receipt["result"]
    assert "execution is not bound" in audit
    assert "cleanup can falsely claim" in audit
    assert "proofreader does not require" in audit
    assert "Disposition: `revision_required`" in audit


def test_c5_windows_teardown_repository_defect_is_corrected_by_endpoint_ownership() -> (
    None
):
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0028"
    )
    diagnostic = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c5-windows-teardown-diagnostic-receipt.json"
    )

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"
    assert diagnostic["original_failure"]["provider_calls"] == 0
    assert diagnostic["bounded_diagnosis"]["exact_port_reacquisition_succeeded"]
    assert diagnostic["bounded_diagnosis"][
        "windows_exclusive_address_use_set_before_bind"
    ]
    assert diagnostic["bounded_diagnosis"]["so_reuseaddr_used"] is False
    lifecycle = diagnostic["repaired_provider_free_lifecycle"]
    assert lifecycle["attempt_result"] == "live_development_recovery_verified"
    assert lifecycle["cleanup_result"] == "cleanup_verified"
    assert lifecycle["operation_counters"]["provider_calls"] == 0


def test_c5_credential_restoration_guidance_separates_adc_and_cli_stores() -> None:
    incident = next(
        row for row in _register()["incidents"] if row["incident_id"] == "AER-0029"
    )
    analysis = (
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c5-credential-restoration-guidance-analysis.md"
    ).read_text(encoding="utf-8")
    preflight = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-c5-live-cli-reauth-cloud-preflight.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert "Application" in analysis and "Default Credentials" in analysis
    assert "gcloud CLI credential store" in analysis
    assert preflight["result"] == "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
    assert all(preflight["checks"].values())


def test_davida_review_errors_match_preserved_evidence() -> None:
    register = _register()
    rows = {row["incident_id"]: row for row in register["incidents"]}
    first_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "davida-default-location-dry-run-gemini-review-receipt.json"
    )
    corrected_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "davida-default-location-dry-run-gemini-review-receipt-2.json"
    )
    evidence = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "davida-provider-free-practice-administration-default-location-dry-run"
        / "provider-free-acceptance-evidence.json"
    )

    assert "--output orchestration" in first_receipt["result"]
    assert "25/25 acceptance cases passed" in first_receipt["result"]
    assert evidence["case_count"] == 60
    assert evidence["passed_case_count"] == 60
    assert "Total Cases Recorded:** 60" in corrected_receipt["result"]
    assert rows["AER-0001"]["category"] == "command_scope_violation"
    assert rows["AER-0002"]["category"] == "evidence_misreport"
    assert rows["AER-0001"]["related_incident_ids"] == ["AER-0002"]
    assert rows["AER-0002"]["related_incident_ids"] == ["AER-0001"]


def test_disposable_postgresql_plan_review_underreport_is_contained() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0093"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["model"] == "gemini-3.6-flash-high"
    assert incident["category"] == "evidence_misreport"
    assert incident["process_severity"] == "material"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "verifier.postgresql_cluster_scope_and_psql_atomicity_underreport"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "--file=-" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_disposable_postgresql_long_review_path_is_recovered() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0094"]

    assert incident["origin"] == "harness"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "harness_failure"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "harness.windows_verifier_worktree_destination_path_too_long"
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "r41" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_disposable_postgresql_catalogue_split_underreport_is_corrected() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0095"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["process_severity"] == "material"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "verifier.exact_catalogue_kind_population_underreport"
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "4/19/9/32" in incident["correction"]["action"]
    assert "all 388 ordered-node kind counts" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_disposable_postgresql_closeout_count_underreport_requires_replacement() -> (
    None
):
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0110"]
    rejected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-parse-catalogue-closeout-review-sol-rejection.json"
    )
    replacement = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "raisa-context-fabric-durability-parse-catalogue-closeout-retry-review-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "verifier.exact_packet_test_count_underreport"
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert rejected["review_decision"] == "pass"
    assert rejected["admitted"] is False
    assert rejected["finding"]["detail"].endswith(
        "the missing three are exactly tests/test_agents_acceptance_index.py."
    )
    assert replacement["decision"] == "pass"
    assert (
        "**Total** | **217** | **217** | **217** | **PASSED**" in replacement["result"]
    )
    assert incident["status"] == "corrected"


def test_behavior_transaction_plan_review_incidents_are_preserved() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "raisa-context-fabric-durability-behavior-transaction-rehearsal-plan-review-receipt.json"
    )

    parent_hash = rows["AER-0111"]
    assert parent_hash["role"] == "orchestrator"
    assert parent_hash["category"] == "output_contract_violation"
    assert parent_hash["candidate_state"] == "accepted_candidate_changed"
    assert parent_hash["workflow_disposition"] == "revision_required"
    assert parent_hash["correction"]["status"] == "control_added"
    assert "canonical UTF-8/LF" in parent_hash["correction"]["action"]

    accounting = rows["AER-0112"]
    assert accounting["role"] == "verifier"
    assert accounting["category"] == "evidence_misreport"
    assert accounting["candidate_state"] == "canonical_unchanged"
    assert accounting["workflow_disposition"] == "review_rejected"
    assert accounting["recurrence_signature"] == (
        "verifier.exact_packet_test_count_underreport"
    )
    assert receipt["decision"] == "revision_required"
    assert "118 total tests" in receipt["result"]
    assert "Finding P2-01" in receipt["result"]
    assert parent_hash["status"] == accounting["status"] == "corrected"


def test_agent_execution_containment_preplanning_receipt_failure_is_preserved() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    failed = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-agent-execution-containment-behavior-transaction-postpause-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-agent-execution-containment-behavior-transaction-preplanning-receipt.json"
    )

    incident = rows["AER-0113"]
    assert incident["recurrence_signature"] == (
        "orchestrator.unapproved_continuation_event"
    )
    assert incident["related_incident_ids"] == []
    assert failed["status"] == "revision_required"
    assert failed["reasons"] == ["continuation_event_missing_or_unapproved"]
    assert failed["rehydration_sources"] == []
    assert corrected["status"] == "passed"
    assert corrected["continuation_event"] == "pre_sprint_planning"
    assert corrected["rehydrated_from_receipt"] is True
    assert incident["status"] == "corrected"


def test_behavior_rehearsal_first_effective_boundary_recovery_is_preserved() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0114"]

    assert incident["category"] == "reasoning_claim_error"
    assert incident["stage"] == "implementation"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.behavior_scenario_first_effective_boundary_mismatch"
    )
    assert "BTR-T03" in incident["observed_error"]
    assert "BTR-T02" in incident["observed_error"]
    assert "first effective boundary" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0115_preserves_failed_runtime_and_bounded_database_adapter() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0115"]

    assert incident["stage"] == "deterministic_verification"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "database sentinel" in incident["recurrence_signature"].replace("_", " ")
    assert any(
        path.endswith("provider-free-behavior-transaction-failure-evidence-001.json")
        for path in incident["evidence_paths"]
    )


def test_aer_0116_preserves_failed_bootstrap_and_dependency_dag_repair() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0116"]

    assert incident["stage"] == "deterministic_verification"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "foreign_key_topology_gap" in incident["recurrence_signature"]
    assert "dependency DAG" in incident["correction"]["prevention_control"]


def test_aer_0117_and_0118_correct_causal_overclaim_and_safe_telemetry() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}

    causal = rows["AER-0117"]
    assert causal["role"] == "verifier"
    assert causal["category"] == "reasoning_claim_error"
    assert causal["correction"]["status"] == "control_added"
    assert "sole_runtime_cause" in causal["recurrence_signature"]

    telemetry = rows["AER-0118"]
    assert telemetry["origin"] == "harness"
    assert telemetry["category"] == "harness_failure"
    assert telemetry["correction"]["status"] == "corrected_fresh_attempt"
    assert "SQLSTATE" in telemetry["correction"]["prevention_control"]


def test_aer_0119_adds_only_an_allowlisted_bootstrap_coordinate() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0119"]

    assert incident["origin"] == "harness"
    assert incident["related_incident_ids"] == []
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "per-relation" in incident["correction"]["prevention_control"]


def test_aer_0120_and_0121_correct_symbol_and_closed_rejection_branch() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}

    symbol = rows["AER-0120"]
    assert symbol["role"] == "verifier"
    assert symbol["category"] == "evidence_misreport"
    assert symbol["candidate_state"] == "canonical_unchanged"
    assert "symbol" in symbol["correction"]["prevention_control"]

    branch = rows["AER-0121"]
    assert branch["origin"] == "harness"
    assert branch["category"] == "harness_failure"
    assert branch["candidate_state"] == "accepted_candidate_changed"
    assert "reason code" in branch["correction"]["prevention_control"]


def test_aer_0122_adds_only_fixed_not_null_header_fallback() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0122"]

    assert incident["origin"] == "harness"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert "free-text" in incident["correction"]["prevention_control"]


def test_aer_0123_repairs_digest_domain_presence_at_consuming_columns() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0123"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert "domain-level NOT NULL" in incident["observed_error"]
    assert "consuming column" in incident["correction"]["prevention_control"]


def test_aer_0124_closes_touched_python_format_preflight() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0124"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert "every touched Python path" in incident["correction"]["prevention_control"]


def test_aer_0125_rebinds_the_sole_changed_catalogue_digest() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0125"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert "expected_query_digests.types" in incident["observed_error"]
    assert "full digest map" in incident["correction"]["prevention_control"]


def test_aer_0126_requires_full_projection_digest_reconstruction() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0126"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert "incomplete simplified projection" in incident["observed_error"]
    assert incident["related_incident_ids"] == []
    assert (
        "reproduce the accepted predecessor digest"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0127_rejects_internally_inconsistent_verifier_digest_claim() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0127"]

    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert "internally contradictory" in incident["detection_method"]
    assert (
        "never copied into a parent binding"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0128_rejects_nonexistent_verifier_evidence_path() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0128"]

    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert "nonexistent" in incident["observed_error"]


def test_aer_0129_separates_application_rows_from_structural_catalogue() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0129"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "application_relations,relation_acl" in incident["observed_error"]
    assert (
        "transaction snapshot invariants"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0130_adds_bounded_query_site_diagnostics() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0130"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert "sha256(3)" in incident["observed_error"]
    assert (
        "non-caller-selectable query id" in incident["correction"]["prevention_control"]
    )


def test_aer_0131_repairs_schema_qualified_postgresql_special_form() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0131"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "SQLSTATE 42883" in incident["observed_error"]
    assert "pg_catalog.coalesce" in incident["observed_error"]
    assert (
        "distinguish special syntactic forms"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0132_closes_snapshot_query_id_evidence_schema() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0132"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["related_incident_ids"] == []
    assert "additional property" in incident["observed_error"]
    assert "whole-document-validate" in incident["correction"]["prevention_control"]


def test_aer_0133_adds_expected_success_scenario_diagnostics() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0133"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert "empty-detail digest" in incident["observed_error"]
    assert "fixed scenario identifier" in incident["correction"]["prevention_control"]


def test_aer_0134_aligns_isolation_with_parent_entry_point() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0134"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "CF303" in incident["observed_error"]
    assert "per entry point" in incident["correction"]["prevention_control"]


def test_aer_0135_adds_safe_plpgsql_function_coordinate() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0135"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert "22P02" in incident["observed_error"]
    assert "scenario-bound coordinate" in incident["correction"]["prevention_control"]


def test_aer_0136_rejects_unregistered_adapter_observation_method() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0136"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert "operator_selected_transport" in incident["observed_error"]
    assert "verbatim" in incident["correction"]["prevention_control"]


def test_aer_0137_admits_only_closed_postgresql_function_name_forms() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0137"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert "22P02" in incident["observed_error"]
    assert "arbitrary qualifiers" in incident["correction"]["prevention_control"]


def test_aer_0138_closes_positional_row_projection_order() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0138"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "stream_id" in incident["observed_error"]
    assert "hostile order swap" in incident["correction"]["prevention_control"]


def test_aer_0139_requires_shared_barrier_fixture_before_behavior() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0139"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert "CF004" in incident["observed_error"]
    assert "pre-effect exact reads" in incident["correction"]["prevention_control"]


def test_aer_0140_closes_artifact_wide_special_form_recurrence() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0140"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "42883" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.schema_qualified_postgresql_special_form"
    )
    assert "artifact-wide census" in incident["correction"]["prevention_control"]


def test_aer_0141_binds_registration_effects_to_forced_rls_capabilities() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0141"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "42501" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.entry_point_effect_missing_forced_rls_capability"
    )
    assert "relation operation summary" in incident["correction"]["prevention_control"]


def test_aer_0142_binds_local_system_xmin_to_an_exact_projection() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0142"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "42703" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.local_system_xmin_without_exact_projection"
    )
    assert "xmin_not_selected" in incident["correction"]["prevention_control"]


def test_aer_0143_binds_system_xmin_record_field_to_explicit_alias() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0143"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["related_incident_ids"] == []
    assert "42703" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.system_xmin_record_field_without_explicit_alias"
    )
    assert ".xmin INTO STRICT" in incident["correction"]["prevention_control"]


def test_aer_0144_rejects_mistyped_full_packet_identifiers() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0144"]

    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["related_incident_ids"] == []
    assert (
        "prefix agreement is insufficient"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0145_rejects_pass_that_contradicts_its_packet() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0145"]

    assert incident["role"] == "verifier"
    assert incident["model"] == "gemini-3.6-flash-high"
    assert incident["category"] == "evidence_misreport"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["related_incident_ids"] == []
    assert "contradiction" in incident["correction"]["prevention_control"]


def test_aer_0146_requires_direct_anonymous_record_xmin_access() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0146"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["related_incident_ids"] == []
    assert "42703" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.anonymous_record_xmin_composite_access"
    )
    assert "(record).xmin" in incident["correction"]["prevention_control"]


def test_aer_0147_preserves_failed_dispatch_receipt_shape() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0147"]

    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "adapter_probe_method_invalid" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )


def test_aer_0148_rejects_stale_behavior_attempt_identifier() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0148"]

    assert incident["role"] == "verifier"
    assert incident["model"] == "gemini-3.6-flash-high"
    assert incident["category"] == "evidence_misreport"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["related_incident_ids"] == []
    assert "attempt 016" in incident["observed_error"]
    assert "attempt 021" in incident["observed_error"]


def test_aer_0149_rejects_unadmitted_preexecution_event_before_runtime() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0149"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert "pre_execution" in incident["observed_error"]
    assert "before Docker or PostgreSQL contact" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "pre_worker_dispatch" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0150_rejects_schema_qualified_postgresql_special_form() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0150"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["workflow_disposition"] == "revision_required"
    assert "pg_catalog.coalesce" in incident["observed_error"]
    assert "without releasing a conjunct result" in incident["observed_error"]
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_aer_0151_removes_insert_reload_write_subtransactions() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0151"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert "EXCEPTION block" in incident["observed_error"]
    assert "top-level transaction ID" in incident["observed_error"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert "twenty-one" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0152_rejects_repeated_descriptive_continuation_event() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0152"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert "pre_execution" in incident["observed_error"]
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0153_rejects_predeclared_verifier_without_assignment_receipt() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0153"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert "workspace_receipt_missing" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0154_rejects_wrong_native_subagent_probe_method() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0154"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert (
        "adapter_probe_method_invalid:codex_subagent_spawn"
        in incident["observed_error"]
    )
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0155_preserves_rls_lock_visibility_repository_defect() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0155"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert "SELECT FOR UPDATE" in incident["observed_error"]
    assert "UPDATE USING" in incident["observed_error"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert "WITH CHECK remains PRODUCER-only" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0156_rejects_repeated_unapproved_preexecution_event() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0156"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert "continuation_event_missing_or_unapproved" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.unapproved_continuation_event"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0157_rejects_invalid_antigravity_acceptance_method() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0157"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert (
        "adapter_probe_method_invalid:antigravity_cli_print"
        in (incident["observed_error"])
    )
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0158_preserves_diagnostic_parser_undercoverage() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0158"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["workflow_disposition"] == "revision_required"
    assert "single_allowlisted_undefined_symbol_missing" in (incident["observed_error"])
    assert incident["recurrence_signature"] == (
        "diagnosis.undefined_symbol_parser_undercoverage"
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0159_preserves_numeric_times_interval_repository_defect() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0159"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert "pg_catalog.*(integer,interval)" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.renderer_numeric_times_interval_and_fixture_duplicate"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0160_rejects_dispatch_after_revision_required_receipt() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0160"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "material"
    assert incident["workflow_disposition"] == "revision_required"
    assert "workspace_receipt_missing" in incident["observed_error"]
    assert "inadmissible" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.worker_dispatch_runtime_contract"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0161_preserves_repeated_diagnostic_parser_undercoverage() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0161"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["workflow_disposition"] == "revision_required"
    assert "single_allowlisted_undefined_symbol_missing" in (incident["observed_error"])
    assert incident["recurrence_signature"] == (
        "diagnosis.undefined_symbol_parser_undercoverage"
    )
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0162_preserves_uuid_minimum_repository_defect() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0162"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert "pg_catalog.min" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.uuid_min_aggregate_lowering"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0163_preserves_clean_checkout_mutable_fixture_dependency() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0163"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["role"] == "verifier"
    assert incident["workflow_disposition"] == "review_rejected"
    assert "FileNotFoundError" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.clean_checkout_mutable_fixture_dependency"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0164_preserves_json_keys_exact_ordering_defect() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0164"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["role"] == "orchestrator"
    assert incident["workflow_disposition"] == "revision_required"
    assert "JSON_KEYS_EXACT" in incident["expected_invariant"]
    assert "CF103" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "repository.json_keys_exact_expected_order_mismatch"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0165_preserves_historical_mutable_attempt_mismatch() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0165"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["role"] == "orchestrator"
    assert incident["workflow_disposition"] == "revision_required"
    assert "attempt-025" in incident["observed_error"]
    assert "attempt-026" in incident["observed_error"]
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "repository.historical_mutable_fixture_attempt_mismatch"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0166_preserves_non_handoff_verifier_workspace_receipt() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0166"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["workflow_disposition"] == "revision_required"
    assert "workspace_not_at_handoff" in incident["observed_error"]
    assert "before any Antigravity or model call" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.non_handoff_verifier_workspace_receipt"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0167_preserves_alias_lock_visibility_repository_defect() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0167"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["process_severity"] == "material"
    assert incident["workflow_disposition"] == "revision_required"
    assert "FOR KEY SHARE" in incident["expected_invariant"]
    assert "no applicable UPDATE USING" in incident["observed_error"]
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "repository.alias_for_key_share_missing_update_using_visibility"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0168_closes_descendant_provenance_assertion_drift() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0168"]

    assert incident["origin"] == "repository"
    assert incident["stage"] == "acceptance"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.descendant_provenance_assertion_drift"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0169_preserves_plpgsql_dml_namespace_ambiguity() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0169"]

    assert incident["origin"] == "repository"
    assert incident["stage"] == "acceptance"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.plpgsql_dml_local_column_namespace_ambiguity"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0170_removes_update_write_subtransactions() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0170"]

    assert incident["origin"] == "repository"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.write_exception_subtransaction_breaks_top_level_xid"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0171_restores_exact_support_execute_grants() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0171"]

    assert incident["origin"] == "repository"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.effective_support_executor_role_field_mismatch"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0172_restores_admission_receiver_binding_visibility() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0172"]

    assert incident["origin"] == "repository"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.security_definer_binding_owner_missing_from_forced_rls"
    )
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0173_corrects_missing_renderer_subcommand() -> None:
    rows = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = rows["AER-0173"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.required_cli_subcommand_omitted"
    )
    assert incident["related_incident_ids"] == []
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0174_corrects_exact_pytest_node_selection() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0174"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.exact_pytest_node_name_unverified"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0175_reconciles_all_exact_register_counts() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0175"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0176_rebinds_representability_parent_digest() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0176"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.inert_descendant_body_parent_digest_drift"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0177_reconciles_parse_parent_expectations() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0177"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.parse_parent_rebind_exact_expectations_incomplete"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0178_corrects_windows_shell_preflight_omission() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0178"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.windows_shell_runtime_and_path_preflight_omitted"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0179_reconciles_final_register_population() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0179"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert incident["related_incident_ids"] == []
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0180_corrects_serial_pytest_delimiter() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0180"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.serial_pytest_option_delimiter_omitted"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0181_decouples_historical_tests_from_mutable_live_state() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0181"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.historical_continuity_test_bound_to_mutable_live_state"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0182_corrects_exact_review_format_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0182"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.exact_review_format_gate_drift"
    )
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0183_rejects_wrong_decision_on_exact_count_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0183"]
    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["recurrence_signature"] == (
        "verifier.packet_exact_count_mismatch_wrong_terminal_decision"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0259_records_exact_receipt_event_vocabulary_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0259"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "pre_plan" in incident["observed_error"]
    assert "pre_sprint_planning" in incident["correction"]["action"]


def test_aer_0260_records_predispatch_profile_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0260"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "adapter_probe_method_invalid" in incident["observed_error"]
    assert "agy_cli_observation" in incident["detection_method"]


def test_aer_0261_preserves_and_corrects_nonexistent_source_binding() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0261"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "ec6a04345fb8a5ec65da112fbacbc98bfb040030" in incident["observed_error"]
    assert (
        "ec6a043410661d563c53d205cd4958d100732e97" in incident["correction"]["action"]
    )


def test_aer_0262_records_repeated_receipt_event_vocabulary_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0262"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "pre_plan" in incident["observed_error"]
    assert "pre_sprint_planning" in incident["correction"]["action"]


def test_aer_0263_contains_protected_search_scope_breach() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0263"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "contained"
    assert "explicit named non-protected" in incident["correction"]["action"]
    assert "No output from that search is admitted" in incident["observed_error"]


def test_aer_0264_preserves_expired_legacy_readiness_gate() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0264"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "expired" in incident["expected_invariant"]
    assert "No product source" in incident["observed_error"]


def test_pattern_report_detects_recurring_control_signals() -> None:
    report = build_pattern_report()

    assert report["incident_count"] == 574


def test_aer_0292_records_protected_filename_metadata_scope_breach() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0292"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"
    assert "No file content was opened" in incident["observed_error"]
    assert (
        "exact already-known non-protected files"
        in (incident["correction"]["prevention_control"])
    )


def test_aer_0293_records_cf_d2_authenticated_readiness_race() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0293"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "artifact was never executed" in incident["observed_error"]
    assert "three consecutive" in incident["correction"]["prevention_control"]


def test_aer_0294_through_0311_record_reschedule_and_multi_change_recovery() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    main_search = incidents["AER-0294"]
    assert main_search["category"] == "command_scope_violation"
    assert main_search["process_severity"] == "material"
    assert main_search["recurrence_signature"] == (
        "orchestrator.overbroad_repository_content_search"
    )
    assert main_search["status"] == "corrected"
    assert main_search["correction"]["status"] == "control_added"

    ui_search = incidents["AER-0295"]
    assert ui_search["role"] == "implementer"
    assert ui_search["category"] == "command_scope_violation"
    assert ui_search["status"] == "corrected"
    assert ui_search["correction"]["status"] == "corrected_fresh_attempt"

    predispatch = incidents["AER-0296"]
    representation = incidents["AER-0297"]
    assert predispatch["related_incident_ids"] == ["AER-0297"]
    assert representation["related_incident_ids"] == ["AER-0296"]
    assert predispatch["recurrence_signature"] == (
        "orchestrator.worker_spawn_before_distinct_predispatch_receipt"
    )
    assert predispatch["status"] == "corrected"
    assert predispatch["correction"]["status"] == "corrected_fresh_attempt"
    assert representation["category"] == "output_contract_violation"
    assert representation["status"] == "corrected"
    assert representation["correction"]["status"] == "corrected_fresh_attempt"

    active_operation = incidents["AER-0298"]
    assert active_operation["category"] == "evidence_misreport"
    assert active_operation["related_incident_ids"] == []
    assert active_operation["recurrence_signature"] == (
        "orchestrator.stale_active_operation_embedded_in_fresh_receipt"
    )
    assert active_operation["status"] == "corrected"
    assert active_operation["correction"]["status"] == "corrected_fresh_attempt"

    powershell = incidents["AER-0299"]
    assert powershell["category"] == "command_scope_violation"
    assert powershell["candidate_state"] == "canonical_unchanged"
    assert powershell["recurrence_signature"] == (
        "orchestrator.powershell_statement_sequence_embedded_inside_expression"
    )
    assert powershell["status"] == "corrected"

    recurrence = incidents["AER-0300"]
    assert recurrence["stage"] == "deterministic_verification"
    assert recurrence["category"] == "command_scope_violation"
    assert recurrence["candidate_state"] == "canonical_unchanged"
    assert recurrence["related_incident_ids"] == []
    assert recurrence["recurrence_signature"] == (
        "orchestrator.powershell_statement_sequence_embedded_inside_expression"
    )
    assert recurrence["status"] == "corrected"
    assert recurrence["correction"]["status"] == "corrected_fresh_attempt"

    source_binding = incidents["AER-0301"]
    assert source_binding["stage"] == "integration"
    assert source_binding["category"] == "evidence_misreport"
    assert source_binding["candidate_state"] == "canonical_unchanged"
    assert source_binding["related_incident_ids"] == []
    assert source_binding["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert source_binding["status"] == "corrected"
    assert source_binding["correction"]["status"] == "corrected_fresh_attempt"

    module_invocation = incidents["AER-0302"]
    assert module_invocation["stage"] == "dispatch"
    assert module_invocation["category"] == "command_scope_violation"
    assert module_invocation["candidate_state"] == "canonical_unchanged"
    assert module_invocation["recurrence_signature"] == (
        "orchestrator.python_package_script_path_invocation"
    )
    assert module_invocation["status"] == "corrected"
    assert module_invocation["correction"]["status"] == "corrected_fresh_attempt"

    slot_inventory = incidents["AER-0303"]
    assert slot_inventory["stage"] == "dispatch"
    assert slot_inventory["category"] == "output_contract_violation"
    assert slot_inventory["candidate_state"] == "canonical_unchanged"
    assert slot_inventory["recurrence_signature"] == (
        "orchestrator.configured_worker_slot_inventory_omitted_when_idle"
    )
    assert slot_inventory["status"] == "corrected"
    assert slot_inventory["correction"]["status"] == "corrected_fresh_attempt"

    adapter_method = incidents["AER-0304"]
    assert adapter_method["stage"] == "dispatch"
    assert adapter_method["category"] == "output_contract_violation"
    assert adapter_method["candidate_state"] == "canonical_unchanged"
    assert adapter_method["recurrence_signature"] == (
        "orchestrator.antigravity_adapter_probe_method_vocabulary_mismatch"
    )
    assert adapter_method["status"] == "corrected"
    assert adapter_method["correction"]["status"] == "corrected_fresh_attempt"

    count_reconciliation = incidents["AER-0305"]
    assert count_reconciliation["stage"] == "independent_review"
    assert count_reconciliation["category"] == "evidence_misreport"
    assert count_reconciliation["candidate_state"] == "canonical_unchanged"
    assert count_reconciliation["recurrence_signature"] == (
        "orchestrator.review_packet_exact_test_count_underreport"
    )
    assert count_reconciliation["status"] == "corrected"
    assert count_reconciliation["correction"]["status"] == "control_added"

    contract_map = incidents["AER-0306"]
    assert contract_map["stage"] == "implementation"
    assert contract_map["category"] == "command_scope_violation"
    assert contract_map["process_severity"] == "moderate"
    assert contract_map["candidate_state"] == "canonical_unchanged"
    assert contract_map["related_incident_ids"] == []
    assert contract_map["status"] == "corrected"
    assert contract_map["correction"]["status"] == "contained_then_escalated"

    adapter_authority = incidents["AER-0307"]
    assert adapter_authority["stage"] == "implementation"
    assert adapter_authority["category"] == "command_scope_violation"
    assert adapter_authority["process_severity"] == "material"
    assert adapter_authority["candidate_state"] == "canonical_unchanged"
    assert adapter_authority["related_incident_ids"] == []
    assert adapter_authority["status"] == "corrected"
    assert adapter_authority["correction"]["status"] == "contained_then_escalated"

    review_report = incidents["AER-0308"]
    assert review_report["stage"] == "independent_review"
    assert review_report["category"] == "evidence_misreport"
    assert review_report["process_severity"] == "moderate"
    assert review_report["candidate_state"] == "canonical_unchanged"
    assert review_report["related_incident_ids"] == []
    assert review_report["recurrence_signature"] == (
        "verifier.review_receipt_command_count_and_format_check_wording_misreport"
    )
    assert review_report["status"] == "corrected"
    assert review_report["correction"]["status"] == "control_added"

    deepseek_egress = incidents["AER-0309"]
    assert deepseek_egress["stage"] == "implementation"
    assert deepseek_egress["role"] == "implementer"
    assert deepseek_egress["category"] == "output_contract_violation"
    assert deepseek_egress["process_severity"] == "low"
    assert deepseek_egress["candidate_state"] == "accepted_candidate_changed"
    assert deepseek_egress["related_incident_ids"] == []
    assert deepseek_egress["recurrence_signature"] == (
        "implementer.required_single_json_decision_wrapped_in_prose_and_fence"
    )
    assert deepseek_egress["status"] == "corrected"
    assert deepseek_egress["correction"]["status"] == "control_added"

    source_binding_recurrence = incidents["AER-0310"]
    assert source_binding_recurrence["stage"] == "integration"
    assert source_binding_recurrence["role"] == "orchestrator"
    assert source_binding_recurrence["category"] == "evidence_misreport"
    assert source_binding_recurrence["process_severity"] == "low"
    assert source_binding_recurrence["candidate_state"] == "canonical_unchanged"
    assert source_binding_recurrence["related_incident_ids"] == []
    assert source_binding_recurrence["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert source_binding_recurrence["status"] == "corrected"
    assert source_binding_recurrence["correction"]["status"] == (
        "corrected_fresh_attempt"
    )

    antigravity_help = incidents["AER-0311"]
    assert antigravity_help["stage"] == "dispatch"
    assert antigravity_help["role"] == "orchestrator"
    assert antigravity_help["category"] == "command_scope_violation"
    assert antigravity_help["process_severity"] == "low"
    assert antigravity_help["candidate_state"] == "canonical_unchanged"
    assert antigravity_help["related_incident_ids"] == []
    assert antigravity_help["recurrence_signature"] == (
        "orchestrator.python_package_script_path_invocation"
    )
    assert antigravity_help["status"] == "corrected"
    assert antigravity_help["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0312_records_recurring_deepseek_fenced_egress() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    deepseek_egress = incidents["AER-0312"]
    assert deepseek_egress["stage"] == "implementation"
    assert deepseek_egress["role"] == "implementer"
    assert deepseek_egress["category"] == "output_contract_violation"
    assert deepseek_egress["process_severity"] == "low"
    assert deepseek_egress["candidate_state"] == "untrusted_partial_worktree"
    assert deepseek_egress["related_incident_ids"] == []
    assert deepseek_egress["recurrence_signature"] == (
        "implementer.required_single_json_decision_wrapped_in_prose_and_fence"
    )
    assert deepseek_egress["status"] == "corrected"
    assert deepseek_egress["correction"]["status"] == "control_added"


def test_aer_0313_records_unverified_module_name_invocation() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    module_discovery = incidents["AER-0313"]
    assert module_discovery["stage"] == "integration"
    assert module_discovery["role"] == "orchestrator"
    assert module_discovery["category"] == "command_scope_violation"
    assert module_discovery["process_severity"] == "low"
    assert module_discovery["candidate_state"] == "canonical_unchanged"
    assert module_discovery["related_incident_ids"] == []
    assert module_discovery["recurrence_signature"] == (
        "orchestrator.unverified_repository_module_name_invocation"
    )
    assert module_discovery["status"] == "corrected"
    assert module_discovery["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0314_records_parallelism_leverage_vocabulary_mismatch() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    vocabulary = incidents["AER-0314"]
    assert vocabulary["stage"] == "integration"
    assert vocabulary["role"] == "orchestrator"
    assert vocabulary["category"] == "command_scope_violation"
    assert vocabulary["process_severity"] == "low"
    assert vocabulary["candidate_state"] == "canonical_unchanged"
    assert vocabulary["related_incident_ids"] == []
    assert vocabulary["recurrence_signature"] == (
        "orchestrator.parallelism_expected_leverage_vocabulary_mismatch"
    )
    assert vocabulary["status"] == "corrected"
    assert vocabulary["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0315_records_mixed_language_static_tool_routing() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    tool_routing = incidents["AER-0315"]
    assert tool_routing["stage"] == "deterministic_verification"
    assert tool_routing["role"] == "orchestrator"
    assert tool_routing["category"] == "command_scope_violation"
    assert tool_routing["process_severity"] == "low"
    assert tool_routing["candidate_state"] == "canonical_unchanged"
    assert tool_routing["related_incident_ids"] == []
    assert tool_routing["recurrence_signature"] == (
        "orchestrator.python_linter_invoked_on_javascript_source"
    )
    assert tool_routing["status"] == "corrected"
    assert tool_routing["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0316_records_recurring_detached_verifier_worktree() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    detached = incidents["AER-0316"]
    assert detached["stage"] == "independent_review"
    assert detached["role"] == "orchestrator"
    assert detached["category"] == "output_contract_violation"
    assert detached["process_severity"] == "low"
    assert detached["candidate_state"] == "canonical_unchanged"
    assert detached["related_incident_ids"] == []
    assert detached["recurrence_signature"] == "orchestrator.detached_verifier_branch"
    assert detached["status"] == "corrected"
    assert detached["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0317_records_continuity_contract_evidence_mapping_error() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    mapping = incidents["AER-0317"]
    assert mapping["stage"] == "closeout"
    assert mapping["role"] == "orchestrator"
    assert mapping["category"] == "reasoning_claim_error"
    assert mapping["process_severity"] == "low"
    assert mapping["candidate_state"] == "canonical_unchanged"
    assert mapping["related_incident_ids"] == []
    assert mapping["recurrence_signature"] == (
        "orchestrator.continuity_contract_evidence_category_mapping_error"
    )
    assert mapping["status"] == "corrected"
    assert mapping["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0318_records_recurring_register_fixture_maintenance_error() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    fixture = incidents["AER-0318"]
    assert fixture["stage"] == "deterministic_verification"
    assert fixture["role"] == "orchestrator"
    assert fixture["category"] == "output_contract_violation"
    assert fixture["process_severity"] == "low"
    assert fixture["candidate_state"] == "canonical_unchanged"
    assert fixture["related_incident_ids"] == []
    assert fixture["recurrence_signature"] == (
        "orchestrator.agent_error_register_population_fixture_update_incomplete"
    )
    assert fixture["status"] == "corrected"
    assert fixture["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0319_records_closeout_latch_and_global_fixture_errors() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    closeout = incidents["AER-0319"]
    assert closeout["stage"] == "closeout"
    assert closeout["role"] == "orchestrator"
    assert closeout["category"] == "output_contract_violation"
    assert closeout["process_severity"] == "low"
    assert closeout["candidate_state"] == "canonical_unchanged"
    assert closeout["related_incident_ids"] == []
    assert closeout["recurrence_signature"] == (
        "orchestrator.closeout_latch_enum_and_current_baton_fixture_stale"
    )
    assert closeout["status"] == "corrected"
    assert closeout["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0320_records_rejected_pre_verifier_runtime_state() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    incident = incidents["AER-0320"]
    assert incident["stage"] == "independent_review"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "orchestrator.pre_verifier_parallelism_disposition_and_workspace_receipt_shape_invalid"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0321_through_0323_preserve_fail_closed_receipt_recoveries() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    leverage = incidents["AER-0321"]
    assert leverage["origin"] == "agent_behavior"
    assert leverage["category"] == "command_scope_violation"
    assert leverage["candidate_state"] == "canonical_unchanged"
    assert leverage["workflow_disposition"] == "revision_required"
    assert leverage["recurrence_signature"] == (
        "orchestrator.parallelism_expected_leverage_vocabulary_mismatch"
    )
    assert "positive_after_contract_freeze" in leverage["observed_error"]
    assert leverage["correction"]["status"] == "corrected_fresh_attempt"

    disposition = incidents["AER-0322"]
    assert disposition["category"] == "output_contract_violation"
    assert disposition["candidate_state"] == "canonical_unchanged"
    assert disposition["workflow_disposition"] == "revision_required"
    assert "selected" in disposition["observed_error"]
    assert "planned" in disposition["correction"]["action"]

    workspace = incidents["AER-0323"]
    assert workspace["category"] == "output_contract_violation"
    assert workspace["candidate_state"] == "canonical_unchanged"
    assert workspace["workflow_disposition"] == "revision_required"
    assert "workspace_not_at_handoff" in workspace["observed_error"]
    assert "workspace_receipt_missing" in workspace["observed_error"]
    assert "at_handoff_current false" in workspace["correction"]["action"]


def test_aer_0324_rejects_underclosed_deepseek_self_pass() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0324"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["resource_id"] == "deepseek-flash-workers"
    assert incident["model"] == "deepseek-v4-flash"
    assert incident["transport"] == "claude_code_bare_deepseek"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert "after its own evidence expiry" in incident["observed_error"]
    assert "null optional cancellation-text" in incident["observed_error"]
    assert incident["correction"]["status"] == "recovery_lease_applied"
    assert incident["status"] == "corrected"


def test_aer_0325_records_repeated_protected_metadata_scope_breach() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0325"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["transport"] == "git_filename_metadata"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.overbroad_protected_path_metadata_enumeration"
    )
    assert "No file content was opened" in incident["observed_error"]
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_aer_0326_contains_deepseek_inventory_transport_timeout() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0326"]

    assert incident["origin"] == "transport"
    assert incident["resource_id"] == "deepseek-flash-workers"
    assert incident["transport"] == "claude_code_bare_deepseek"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "transport.deepseek_occupied_worker_no_terminal_response"
    )
    assert "no owned inventory path" in incident["observed_error"]
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert incident["status"] == "contained"


def test_aer_0327_corrects_detached_gemini_worktree_before_model_call() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0327"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["transport"] == "antigravity_local_wrapper_preflight"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == "orchestrator.detached_verifier_branch"
    assert "before project creation" in incident["observed_error"]
    assert "provider_or_model_calls zero" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0328_validates_command_manifest_before_gemini_dispatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0328"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["transport"] == "antigravity_local_wrapper_manifest_admission"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "orchestrator.verifier_command_manifest_id_vocabulary_mismatch"
    )
    assert "before project creation" in incident["observed_error"]
    assert "scripts.ariadne_evidence_gate" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0329_rejects_inferred_full_head_before_verifier_receipt() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0329"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert "f6502046c5dcc5b446e63fb9035d91f66d9d993c" in incident["observed_error"]
    assert "git rev-parse HEAD" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0273_and_0274_preserve_cf_d2_planning_stops() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    predispatch = incidents["AER-0273"]
    assert predispatch["stage"] == "dispatch"
    assert predispatch["candidate_state"] == "canonical_unchanged"
    assert predispatch["workflow_disposition"] == "revision_required"
    assert predispatch["status"] == "corrected"
    assert predispatch["correction"]["status"] == "control_added"

    formatting = incidents["AER-0274"]
    assert formatting["stage"] == "independent_review"
    assert formatting["candidate_state"] == "accepted_candidate_changed"
    assert formatting["workflow_disposition"] == "review_rejected"
    assert formatting["status"] == "corrected"
    assert formatting["correction"]["status"] == ("corrected_fresh_attempt")


def test_aer_0275_records_the_stale_behavior_parent_test_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0275"]

    assert incident["origin"] == "repository"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "three stale expected binding tuples" in incident["correction"]["action"]


def test_aer_0330_records_prime_harness_preplanning_contract_recovery() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0330"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "orchestrator.parallelism_expected_leverage_vocabulary_mismatch"
    )
    assert "parallelism_assessment_operation_mismatch" in incident["detection_method"]
    assert "required_independence" in incident["correction"]["action"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0331_contains_prime_harness_deepseek_self_pass() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0331"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["resource_id"] == "deepseek-flash-workers"
    assert incident["stage"] == "implementation"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "implementer.self_pass_with_contradictory_or_underclosed_canonical_contract"
    )
    assert "7ff8ea25b03b691bad0feef179e9cb05f01c72f4" in incident["observed_error"]
    assert "173 focused tests" in incident["observed_error"]
    assert "139 hostile mutations" in incident["observed_error"]
    assert "five fail-closed contract gaps" in incident["detection_method"]
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert "one bounded five-part correction" in incident["correction"]["action"]
    assert incident["status"] == "contained"


def test_aer_0332_corrects_outer_timeout_without_duplicate_gemini_dispatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0332"]

    assert incident["origin"] == "harness"
    assert incident["role"] == "orchestrator"
    assert incident["resource_id"] == "codex-shell-command-timeout-wrapper"
    assert incident["model"] is None
    assert incident["stage"] == "independent_review"
    assert incident["category"] == "harness_failure"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "harness.shell_wrapper_timeout_before_live_external_worker_completion"
    )
    assert "30-minute print timeout" in incident["observed_error"]
    assert "did not retry" in incident["detection_method"]
    assert "79f5d6cf1cbe4ca9ad4893f257e92eccfd2ac2ce" in incident["detection_method"]
    assert incident["correction"]["status"] == "control_added"
    assert "forbid duplicate dispatch" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0333_rejects_reused_outer_timeout_and_chained_gate_claims() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0333"]

    assert incident["origin"] == "harness"
    assert incident["role"] == "orchestrator"
    assert incident["resource_id"] == "codex-shell-command-timeout-wrapper"
    assert incident["model"] is None
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "harness_failure"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "harness.shell_wrapper_timeout_before_live_external_worker_completion"
    )
    assert "123.7 seconds" in incident["observed_error"]
    assert "stdout-flush OSError" in incident["observed_error"]
    assert "no surviving Python child" in incident["detection_method"]
    assert "claimed no Ruff or diff outcome" in incident["detection_method"]
    assert incident["correction"]["status"] == "control_added"
    assert "ariadne_serial_pytest" in incident["correction"]["action"]
    assert "never chain" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0334_rejects_chained_validation_exit_masking() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0334"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert (
        incident["recurrence_signature"]
        == "orchestrator.chained_validation_exit_masking"
    )
    assert "final successful diff" in incident["observed_error"]
    assert "python -m" in incident["correction"]["action"]
    assert "separately captured" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0335_corrects_worker_predispatch_receipt_before_launch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0335"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert (
        incident["recurrence_signature"]
        == "orchestrator.worker_dispatch_runtime_contract"
    )
    assert "disposition active" in incident["observed_error"]
    assert "at_handoff_current" in incident["observed_error"]
    assert "before any worker dispatch" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "dispatched" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0336_rejects_worker_pass_with_failed_mandatory_gate() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0336"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["resource_id"] == "deepseek-flash-workers"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "moderate"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "implementer.self_pass_despite_failed_mandatory_gate"
    )
    assert "bc0b8adcdc9f1c11bb69abe1514677a92d17f9c7" in incident["observed_error"]
    assert "command 3 exited 1" in incident["observed_error"]
    assert "no integration or acceptance followed" in incident["detection_method"]
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert incident["status"] == "contained"


def test_aer_0337_rejects_recurrent_chained_validation_after_control() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0337"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "moderate"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert (
        incident["recurrence_signature"]
        == "orchestrator.chained_validation_exit_masking"
    )
    assert "after AER-0334" in incident["observed_error"]
    assert "with semicolons" in incident["observed_error"]
    assert "reran every affected" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0338_contains_source_identical_status_openapi_hash_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0338"]

    assert incident["origin"] == "repository"
    assert incident["role"] == "orchestrator"
    assert incident["resource_id"] == "api-spine-historical-regression-suite"
    assert incident["category"] == "repository_defect"
    assert incident["process_severity"] == "moderate"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "repository.api_spine_historical_expectation_drift"
    )
    assert "d500f1f86a83695cee0c2aac93aa2e2735e8f799" in incident["observed_error"]
    assert (
        "c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6"
        in incident["observed_error"]
    )
    assert (
        "c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a"
        in incident["observed_error"]
    )
    assert incident["correction"]["status"] == "control_implemented_pending_acceptance"
    assert "one test-only digest correction" in incident["correction"]["action"]
    assert incident["status"] == "contained"


def test_aer_0339_contains_omitted_plan_source_canonical_fast_profile() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0339"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "moderate"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.plan_preflight_mandatory_regression_profile_omitted"
    )
    assert "four failures" in incident["observed_error"]
    assert "one candidate-caused dependency assertion" in incident["observed_error"]
    assert "three stale current-baton assertions" in incident["observed_error"]
    assert "reproduced the three" in incident["detection_method"]
    assert incident["correction"]["status"] == "control_implemented_pending_acceptance"
    assert "complete canonical fast profile" in incident["correction"]["action"]
    assert incident["status"] == "contained"


def test_aer_0340_corrects_stale_standalone_agent_population_fixture() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0340"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.agent_error_register_population_fixture_update_incomplete"
    )
    assert (
        "left the standalone agent_incidents length at 230"
        in incident["observed_error"]
    )
    assert "assert 234 == 230" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "final exact 235" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0341_preserves_cross_checkout_relative_test_path_veto() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0341"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "independent_review"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "relative candidate test paths" in incident["observed_error"]
    assert "exact absolute test paths" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0276_reconciles_the_verifier_timeout_value_misreport() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0276"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"
    assert "8000ms" in incident["correction"]["action"]


def test_aer_0277_records_the_rejected_cf_d2_preexecution_event() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0277"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "pre_worker_dispatch" in incident["correction"]["action"]


def test_aer_0278_contains_the_cf_d2_successor_admission_ordering_failure() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0278"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_implemented_pending_acceptance"
    assert "attempt 002" in incident["correction"]["action"]


def test_aer_0279_stops_cf_d2_after_attempt_002() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0279"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "control_added"
    assert "Yuri" in incident["correction"]["action"]


def test_aer_0280_rejects_the_repeated_missing_formatter_gate() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0280"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "orchestrator.pre_review_format_gate_omitted"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "fresh exact-head" in incident["correction"]["action"]


def test_aer_0281_replaces_mutable_roadmap_numbers_with_semantic_order() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0281"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "semantic heading labels" in incident["correction"]["action"]


def test_aer_0282_corrects_the_cf_d2_anchor_revision_off_by_one() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0282"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "harness.lifecycle_anchor_revision_off_by_one"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert "lifecycle revision one" in incident["correction"]["action"]


def test_aer_0283_rejects_verifier_command_target_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0283"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "command_scope_violation"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == ("verifier.allowed_command_target_drift")
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "normalized command list" in incident["correction"]["prevention_control"]


def test_aer_0284_contains_the_cf_d2_insufficient_diagnosis() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0284"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "orchestrator.coordinate_isolation_misread_as_assertion_isolation"
    )
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert "discriminator table" in incident["correction"]["prevention_control"]


def test_aer_0285_makes_receipt_event_vocabulary_discoverable() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0285"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.orchestrator_receipt_continuation_event_vocabulary_mismatch"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "receipt CLI" in incident["correction"]["prevention_control"]


def test_aer_0286_forbids_manual_short_sha_expansion() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0286"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.manual_short_sha_expansion"
    )
    assert incident["status"] == "corrected"
    assert "git rev-parse" in incident["correction"]["prevention_control"]


def test_aer_0287_preserves_failed_predispatch_state_and_v2_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0287"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "worker-slot" in incident["correction"]["prevention_control"]


def test_aer_0288_keeps_provider_shape_and_local_exactness_separate() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0288"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["stage"] == "dispatch"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["status"] == "corrected"
    assert (
        "deterministic local release boundary"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0289_rejects_inferred_full_source_head_before_acceptance() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0289"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["stage"] == "acceptance"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert incident["status"] == "corrected"
    assert "git rev-parse" in incident["correction"]["prevention_control"]


def test_aer_0290_preserves_rejected_preplanning_event_before_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0290"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.orchestrator_receipt_continuation_event_vocabulary_mismatch"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "--list-continuation-events" in incident["correction"]["prevention_control"]


def test_aer_0291_contains_protected_scope_search_before_adapter_planning() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0291"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.overbroad_repository_content_search"
    )
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "corrected"
    assert "exact-file allowlist" in incident["correction"]["prevention_control"]


def test_aer_0184_records_input_column_ambiguity_and_collision_proof_lowering() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0184"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert "cf_arg_" in incident["correction"]["action"]

    report = build_pattern_report()
    assert report["register_revision"] == 495
    assert report["incident_count"] == 574
    assert report["open_incident_ids"] == []
    assert report["counts"]["by_origin"] == {
        "agent_behavior": 403,
        "harness": 53,
        "operator": 17,
        "repository": 85,
        "transport": 16,
    }
    assert report["counts"]["by_category"] == {
        "command_scope_violation": 82,
        "evidence_misreport": 66,
        "harness_failure": 53,
        "operator_error": 17,
        "output_contract_violation": 206,
        "read_only_violation": 3,
        "reasoning_claim_error": 46,
        "repository_defect": 85,
        "transport_timeout": 16,
    }
    assert report["counts"]["by_candidate_state"] == {
        "accepted_candidate_changed": 114,
        "canonical_unchanged": 364,
        "untrusted_partial_worktree": 96,
    }
    receipt_event_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.orchestrator_receipt_continuation_event_vocabulary_mismatch"
    )
    assert receipt_event_recurrence["incident_ids"] == [
        "AER-0259",
        "AER-0262",
        "AER-0268",
        "AER-0277",
        "AER-0285",
        "AER-0290",
        "AER-0451",
    ]
    assert receipt_event_recurrence["incident_count"] == 7
    tree_object_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.git_refs_evidence_included_noncommit_tree_object"
    )
    assert tree_object_recurrence["incident_ids"] == ["AER-0365", "AER-0368"]
    assert tree_object_recurrence["incident_count"] == 2
    register_metadata_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert register_metadata_recurrence["incident_ids"] == [
        "AER-0175",
        "AER-0179",
        "AER-0211",
        "AER-0389",
        "AER-0395",
        "AER-0543",
        "AER-0545",
        "AER-0546",
    ]
    assert register_metadata_recurrence["incident_count"] == 8
    deepseek_exit_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "transport.deepseek_claude_exit_1_before_worker_result"
    )
    # AER-0419 uses the same transport signature but remains a distinct
    # implementation-worker resource dimension, so the report does not merge it.
    assert deepseek_exit_recurrence["incident_ids"] == ["AER-0382", "AER-0391"]
    assert deepseek_exit_recurrence["incident_count"] == 2
    manual_sha_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"] == "orchestrator.manual_short_sha_expansion"
    )
    assert manual_sha_recurrence["incident_ids"] == [
        "AER-0286",
        "AER-0399",
        "AER-0426",
        "AER-0452",
    ]
    assert manual_sha_recurrence["incident_count"] == 4
    closeout_fixture_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.closeout_latch_enum_and_current_baton_fixture_stale"
    )
    assert closeout_fixture_recurrence["incident_ids"] == ["AER-0319", "AER-0402"]
    assert closeout_fixture_recurrence["incident_count"] == 2
    baton_prose_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.current_baton_prose_assertion_representation_mismatch"
    )
    assert baton_prose_recurrence["incident_ids"] == [
        "AER-0403",
        "AER-0411",
        "AER-0413",
    ]
    assert baton_prose_recurrence["incident_count"] == 3
    complete_latch_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.active_operation_complete_retained_resume_or_next_stage"
    )
    assert complete_latch_recurrence["incident_ids"] == ["AER-0390", "AER-0414"]
    assert complete_latch_recurrence["incident_count"] == 2
    register_prose_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.agent_error_register_test_prose_assertion_mismatch"
    )
    assert register_prose_recurrence["incident_ids"] == ["AER-0401", "AER-0412"]
    assert register_prose_recurrence["incident_count"] == 2
    asymmetric_peer_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.agent_error_register_asymmetric_peer_link"
    )
    assert asymmetric_peer_recurrence["incident_ids"] == ["AER-0400", "AER-0406"]
    assert asymmetric_peer_recurrence["incident_count"] == 2
    population_fixture_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.agent_error_register_population_fixture_update_incomplete"
    )
    assert population_fixture_recurrence["incident_ids"] == [
        "AER-0255",
        "AER-0318",
        "AER-0340",
        "AER-0520",
        "AER-0566",
        "AER-0571",
        "AER-0572",
    ]
    assert population_fixture_recurrence["incident_count"] == 7
    plan_disposition_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.plan_precommit_parallelism_disposition_invalid"
    )
    assert plan_disposition_recurrence["incident_ids"] == ["AER-0322", "AER-0428"]
    assert plan_disposition_recurrence["incident_count"] == 2
    continuity_inventory_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.continuity_node_contract_evidence_inventory_incomplete"
    )
    assert continuity_inventory_recurrence["incident_ids"] == [
        "AER-0461",
        "AER-0462",
        "AER-0502",
        "AER-0525",
    ]
    assert continuity_inventory_recurrence["incident_count"] == 4
    compass_sentinel_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "repository.compass_current_position_literal_stale_after_valid_advance"
    )
    assert compass_sentinel_recurrence["incident_ids"] == [
        "AER-0388",
        "AER-0463",
        "AER-0505",
        "AER-0527",
    ]
    assert compass_sentinel_recurrence["incident_count"] == 4
    register_literal_baseline_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "repository.agent_error_register_literal_baseline_stale_after_valid_advance"
    )
    assert register_literal_baseline_recurrence["incident_ids"] == [
        "AER-0470",
        "AER-0471",
    ]
    assert register_literal_baseline_recurrence["incident_count"] == 2
    powershell_pipeline_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.powershell_pipeline_used_for_read_only_projection"
    )
    assert powershell_pipeline_recurrence["incident_ids"] == [
        "AER-0484",
        "AER-0485",
        "AER-0494",
        "AER-0499",
        "AER-0519",
    ]
    assert powershell_pipeline_recurrence["incident_count"] == 5
    baseline_advance_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.new_recurring_pattern_baseline_not_advanced_atomically"
    )
    assert baseline_advance_recurrence["incident_ids"] == [
        "AER-0487",
        "AER-0495",
        "AER-0521",
        "AER-0522",
        "AER-0561",
    ]
    assert baseline_advance_recurrence["incident_count"] == 5
    latch_revision_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.current_latch_revision_assertion_stale_after_incident_advance"
    )
    assert latch_revision_recurrence["incident_ids"] == ["AER-0498", "AER-0500"]
    assert latch_revision_recurrence["incident_count"] == 2
    repeated_patch_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.apply_patch_repeated_value_target_missing_incident_context"
    )
    assert repeated_patch_recurrence["incident_ids"] == [
        "AER-0490",
        "AER-0508",
        "AER-0573",
    ]
    assert repeated_patch_recurrence["incident_count"] == 3
    checkpoint_bound_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.active_operation_checkpoint_text_exceeded_bound"
    )
    assert checkpoint_bound_recurrence["incident_ids"] == ["AER-0460", "AER-0512"]
    assert checkpoint_bound_recurrence["incident_count"] == 2
    latch_phrase_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.latch_continuity_phrase_stale_after_bounded_checkpoint_rewrite"
    )
    assert latch_phrase_recurrence["incident_ids"] == ["AER-0513", "AER-0524"]
    assert latch_phrase_recurrence["incident_count"] == 2
    boundary_phrase_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "repository.current_baton_protected_boundary_literal_paraphrased"
    )
    assert boundary_phrase_recurrence["incident_ids"] == ["AER-0558", "AER-0560"]
    assert boundary_phrase_recurrence["incident_count"] == 2
    assert [
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        not in {
            "orchestrator.orchestrator_receipt_continuation_event_vocabulary_mismatch",
            "orchestrator.git_refs_evidence_included_noncommit_tree_object",
            "repository.agent_error_register_exact_count_update_incomplete",
            "transport.deepseek_claude_exit_1_before_worker_result",
            "orchestrator.manual_short_sha_expansion",
            "orchestrator.closeout_latch_enum_and_current_baton_fixture_stale",
            "orchestrator.current_baton_prose_assertion_representation_mismatch",
            "orchestrator.active_operation_complete_retained_resume_or_next_stage",
            "orchestrator.agent_error_register_test_prose_assertion_mismatch",
            "orchestrator.agent_error_register_asymmetric_peer_link",
            "orchestrator.plan_precommit_parallelism_disposition_invalid",
            "orchestrator.continuity_node_contract_evidence_inventory_incomplete",
            "repository.compass_current_position_literal_stale_after_valid_advance",
            "repository.agent_error_register_literal_baseline_stale_after_valid_advance",
            "orchestrator.powershell_pipeline_used_for_read_only_projection",
            "orchestrator.new_recurring_pattern_baseline_not_advanced_atomically",
            "orchestrator.current_latch_revision_assertion_stale_after_incident_advance",
            "orchestrator.apply_patch_repeated_value_target_missing_incident_context",
            "orchestrator.active_operation_checkpoint_text_exceeded_bound",
            "orchestrator.latch_continuity_phrase_stale_after_bounded_checkpoint_rewrite",
            "repository.current_baton_protected_boundary_literal_paraphrased",
        }
    ] == [
        {
            "recurrence_signature": "orchestrator.chained_validation_exit_masking",
            "incident_count": 8,
            "incident_ids": [
                "AER-0334",
                "AER-0337",
                "AER-0372",
                "AER-0397",
                "AER-0429",
                "AER-0432",
                "AER-0455",
                "AER-0458",
            ],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Admission gates may be parallelized only as separately captured process results. Never chain validations where a later success can mask an earlier exit, and invoke repository package CLIs through their admitted python -m module path.",
                "After a no-chaining incident, semicolon-composed validation or readback commands are prohibited. Use one process call per gate and record its exit before starting the next gate.",
                "Every validation gate in this tranche must be one separately captured process invocation with exact plan-derived paths. A later Ariadne harness repair will prohibit semicolon-composed validation sequences and fail before execution when an exact requested test path is absent.",
                "For the remainder of this tranche, every shell process contains exactly one executable command with no pipe, semicolon or newline-composed successor; output limiting must use that executable's native options only.",
                "No validation, staging, commit or readback operation may share a shell invocation with another gate; record every exit before starting the next process.",
                "No validation, updater or mutating acceptance command may share a shell sequence with readback or later checks; capture its process result first and start every inspection in a distinct tool call.",
                "One command and one result per process for all remaining gates; newline separation inside one shell invocation is prohibited just like semicolon or pipeline composition.",
                "One process per validation, staging, commit or readback gate; semicolon-composed gate invocations are prohibited even when every operation is read-only.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.fixture_dependent_pytest_invoked_without_conftest"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0378", "AER-0384"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Prerequisite validators and dependent pytest commands must not be joined by an unconditional separator; repository pytest always uses the serial launcher when tests/conftest.py loads.",
                "The post-closeout effectiveness repair must make each named pytest profile declare conftest_required and have the launcher reject --noconftest when any selected file is fixture-dependent.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.overbroad_protected_path_metadata_enumeration"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0292", "AER-0325"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "For physical-representability discovery, every filename-metadata and content command must name exact already-known non-protected files. Directory roots are prohibited even when narrowly scoped or filtered. Any expansion must follow an exact link inside an already allowlisted file and requires plan revision before opening.",
                "Near protected evidence, every content or filename-metadata command must name exact already-known non-protected files. A directory root may not be used to derive candidates. Any expansion must follow an exact import or migration link found inside a file already authorized by a frozen plan.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.overbroad_repository_content_search",
            "incident_count": 4,
            "incident_ids": ["AER-0054", "AER-0092", "AER-0291", "AER-0294"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Architecture recovery packets and Sol self-checks must carry an explicit exact-path read allowlist. Environment facts are read from one named configuration or handover path; broad rg, recursive content search and wildcard discovery are prohibited under protected-evidence containment.",
                "Every content-search command in this and later protected-evidence-adjacent work must supply an explicit exact-file allowlist assembled from already known non-protected baton/API paths. Searching a directory root such as tests, docs or the repository root is prohibited even when the textual pattern appears narrow.",
                "Every environment-discovery step must carry an exact path or executable-name allowlist before execution. Unknown facts become explicit fail-closed plan preconditions rather than triggers for broad search.",
                "No content-search, recursive or glob command may target a directory root in protected-evidence-adjacent work; every read must name one predeclared non-protected literal file.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.parallelism_expected_leverage_vocabulary_mismatch"
            ),
            "incident_count": 5,
            "incident_ids": [
                "AER-0314",
                "AER-0321",
                "AER-0330",
                "AER-0385",
                "AER-0398",
            ],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Construct every parallelism assessment from the configured enum vocabulary and the last passing exact analogue; express timing, qualifications and net leverage only in rationale text.",
                "Copy every expected_leverage value from orchestration/harness_settings/orchestrator_requirements.yaml; express qualifications only in rationale text and require exact passed readback before planning or dispatch.",
                "Copy operation_id directly from the validated live latch and select every expected_leverage value from the configured enum before receipt generation; express timing or qualifications only in rationale text and require exact passed readback before dispatch.",
                "Use only the configured expected_leverage vocabulary in Ariadne runtime states; express qualified or net assessments in rationale text, never by inventing a new enum value.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.powershell_statement_sequence_embedded_inside_expression"
            ),
            "incident_count": 4,
            "incident_ids": ["AER-0242", "AER-0246", "AER-0299", "AER-0300"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Do not place a Git command, semicolon or if statement inside a PowerShell assignment expression. Use newline-separated scalar assignments exclusively for all remaining Git/ref/worktree probes in this tranche.",
                "For PowerShell orchestration probes, use one statement per step: capture collection output, run Git or shell commands, capture $LASTEXITCODE, and only then construct the final object. Never place a semicolon-delimited statement sequence inside a property expression.",
                "For every remaining worktree and worker probe, execute each PowerShell and Git statement separately, capture LASTEXITCODE immediately, and construct objects only from named scalar variables.",
                "For the rest of AES-C2 orchestration, every PowerShell diagnostic uses literal command statements with named intermediate values and no script-text variable in command position; Git revision-path arguments are always quoted.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.python_package_script_path_invocation",
            "incident_count": 6,
            "incident_ids": [
                "AER-0058",
                "AER-0066",
                "AER-0067",
                "AER-0204",
                "AER-0302",
                "AER-0311",
            ],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "For every remaining repository Python harness in this tranche, use python -m scripts.<module> exclusively; never infer direct-path safety from an AGENTS.md launcher label.",
                "For the remainder of this tranche, invoke every repository Python harness only as python -m scripts.<module>; use filesystem paths only for non-Python executables or files passed as data arguments.",
                "Invoke every repository script that imports the scripts package through python -m scripts.<module> from the repository root; direct path invocation is reserved for self-contained scripts whose imports have been preflighted.",
                "Invoke import-dependent scripts as python -m scripts.<module> when they expose a module CLI, or import their public API from the repository root; never execute them by filesystem path.",
                "The direct-path exception is removed for this tranche: every Python file under scripts is invoked as a package module unless a recorded preflight proves it has no package imports on every execution path.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.worker_spawn_before_distinct_predispatch_receipt"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0043", "AER-0296"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Treat pre_sprint_planning and pre_worker_dispatch as distinct ordered events; the dispatch command may be issued only after the latter receipt is generated and read back as passed.",
                "Treat worker_dispatch_permitted true in the immediately preceding distinct receipt as a hard executable precondition for every native or external worker spawn or follow-up task.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.git_evidence_future_commit_hash_invented_from_short_prefix"
            ),
            "incident_count": 5,
            "incident_ids": [
                "AER-0354",
                "AER-0356",
                "AER-0363",
                "AER-0370",
                "AER-0376",
            ],
            "origins": ["agent_behavior"],
            "categories": ["evidence_misreport"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "A follow-on Ariadne workflow repair must machine-populate or mechanically compare Git object-ID fields; prose-only copying instruction has now proved insufficient.",
                "Every full 40-character Git object ID in continuation Git-ref evidence is now mechanically resolved with git cat-file before a receipt can pass; unresolvable IDs return revision_required and forbid dispatch or publication.",
                "Precommit evidence may name only current exact HEAD and a pending commit; post-commit hashes must be machine-populated or mechanically compared with direct Git output.",
                "The existing Git-object-resolution preflight remains fail-closed for every continuation event. Orchestrator evidence authoring must capture the full object first and paste only that machine output; short displayed prefixes are presentation only.",
                "The post-closeout Ariadne effectiveness review must prioritize machine-populating all Git-ref fields from one resolved-ref snapshot so the orchestrator never manually transcribes a full object ID.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.raw_text_hash_bound_to_primary_crlf_worktree_bytes"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0349", "AER-0357"],
            "origins": ["agent_behavior"],
            "categories": ["evidence_misreport"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Every future text-bound review must reuse a checkout-stable canonical LF helper and prove its bindings in a fresh exact-HEAD worktree before verifier dispatch; raw SHA-256 remains only for explicitly binary artifacts.",
                "Text source bindings must declare and test a checkout-stable canonical line-ending mode; raw worktree-byte hashes remain only for explicitly binary artifacts.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
            ),
            "incident_count": 13,
            "incident_ids": [
                "AER-0192",
                "AER-0196",
                "AER-0205",
                "AER-0207",
                "AER-0210",
                "AER-0219",
                "AER-0241",
                "AER-0261",
                "AER-0267",
                "AER-0289",
                "AER-0301",
                "AER-0310",
                "AER-0329",
            ],
            "origins": ["agent_behavior"],
            "categories": ["evidence_misreport"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Before any source-bound evidence generation, capture full HEAD from git rev-parse, verify it with git cat-file, and pass that same captured value directly to the harness; never copy a restored summary or abbreviated display hash into source_head.",
                "Capture and retain the forty-character HEAD in a named scalar immediately after every commit and before drafting any source-bound packet, runtime state or receipt; never construct or autocomplete an object ID from abbreviated terminal output.",
                "Capture and retain the forty-character HEAD in a named scalar immediately after every commit; do not author any source-bound latch, packet or receipt field from Git's abbreviated commit output.",
                "Copy every full commit identifier only from an exact Git command result, even immediately after a successful command prints a short hash; never synthesize or autocomplete an object ID.",
                "Move exact git rev-parse capture ahead of every packet or runtime-state drafting step and mechanically interpolate only the captured forty-character value; do not begin authoring from abbreviated commit output.",
                "Never expand or infer a short Git hash. Capture every exact object ID with git rev-parse, verify it resolves, and reconcile every packet diff range before generating the final dispatch receipt.",
                "Never expand or infer a short Git hash. Capture every exact object ID with git rev-parse, verify it with git cat-file, and test the full value before review or runtime dispatch.",
            ],
        },
        {
            "recurrence_signature": "verifier.exact_packet_test_count_underreport",
            "incident_count": 4,
            "incident_ids": ["AER-0035", "AER-0037", "AER-0110", "AER-0112"],
            "origins": ["agent_behavior"],
            "categories": ["evidence_misreport"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "Acceptance must machine-reconcile every verifier test-count and repository-path claim against exact collection output and the candidate tree; prose discrepancies are preserved and never copied as authoritative evidence.",
                "Acceptance must reconcile every verifier test-count claim against exact machine collection output; a numerical discrepancy is preserved explicitly and never copied into closeout as authoritative evidence.",
                "Final closeout acceptance must bind each required test path to exact per-file collection and pass counts; any missing path or arithmetic mismatch rejects the review even when its terminal decision says pass.",
                "Fresh replacement review admission requires exact per-file collect-only and pass arithmetic, not an aggregate progress-line estimate.",
            ],
        },
        {
            "recurrence_signature": (
                "implementer.required_single_json_decision_wrapped_in_prose_and_fence"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0309", "AER-0312"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["implementer"],
            "resource_ids": ["deepseek-flash-workers"],
            "prevention_controls": [
                "Validate worker egress shape separately from candidate source: extra prose or fencing remains an output-contract violation even when an embedded object parses, and no self-reported pass may substitute for Git and independently reproduced checks.",
                "Validate worker egress shape separately from candidate source: extra prose or fencing remains an output-contract violation even when an embedded object parses, and no self-reported pass may substitute for Git inspection, explicit Sol recovery and independently reproduced checks.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.agent_error_register_population_fixture_update_incomplete"
            ),
            "incident_count": 7,
            "incident_ids": [
                "AER-0255",
                "AER-0318",
                "AER-0340",
                "AER-0520",
                "AER-0566",
                "AER-0571",
                "AER-0572",
            ],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "After adding any incident, search the complete focused register test for register_revision, incident_count, ordered range, origin/category/candidate-state aggregates and recurring-pattern equality; update them as one atomic mechanical change before running pattern generation.",
                "After adding any incident, search the complete focused register test for register_revision, incident_count, ordered range, standalone origin lengths, origin/category/candidate-state aggregate dictionaries and recurring-pattern equality; update them as one atomic mechanical change before pattern generation.",
                "Before the first full run after any incident addition, search for the previous total, revision, final ID, standalone origin lengths, aggregate dictionaries and affected recurrence signature; update every match as one mechanical patch.",
                "Before the first full run after any register edit, mechanically search the entire focused test for revision, ID range, standalone origin lengths, totals, aggregate dictionaries and recurrence equality, then compare every literal with a freshly built report.",
                "The clockwork reducer computes direct and aggregate population views from one journal and emits tests from the same typed result, removing independent population literals.",
                "The clockwork reducer computes population views and emits exact typed fields from one journal so neither aggregate values nor narrative bindings are independently retyped.",
                "The clockwork reducer must expose one generated recurrence projection; tests should validate reducer properties instead of copying the reducer's complete incident list into multiple fixtures.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.detached_verifier_branch",
            "incident_count": 4,
            "incident_ids": ["AER-0012", "AER-0014", "AER-0316", "AER-0327"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Create every verifier worktree directly on a named non-protected codex/review branch; never use --detach even temporarily before the mandatory preflight.",
                "Never create an Antigravity verifier worktree with --detach. Create it directly on a named codex/review branch and require scripts.ariadne_verifier_worktree_preflight to pass before constructing the pre-verifier runtime state.",
                "Verifier setup must validate a non-empty non-protected codex/review branch and exact candidate HEAD before issuing the pre-verifier receipt or invoking Antigravity.",
                "scripts/ariadne_verifier_worktree_preflight.py must pass on the exact candidate and codex/review branch before a pre-verifier receipt or Antigravity launch; policy ordering and tests enforce the gate.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.provider_free_test_allowlist_included_fixture_or_known_negative_suites"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0420", "AER-0425"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Before a no-conftest dispatch, inspect every selected file for repository fixtures and known-negative classification; fixture-backed coverage belongs only to an explicitly authorised database profile and documented negative suites cannot become positive admission gates.",
                "Verifier manifest construction must classify every pytest path as self-contained or conftest-required before selection and obtain the digest only through load_command_manifest plus command_manifest_sha256; raw JSON file hashing is not an admitted substitute.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.touched_python_format_preflight_incomplete"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0124", "AER-0223"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Derive local Ruff check and format targets from every touched Python path in the candidate and run the exact packet commands after the final formatting pass, not a hand-selected subset.",
                "Derive local Ruff lint and format targets mechanically from git diff --name-only filtered to Python after the final edit; do not use a hand-selected subset copied from an earlier candidate stage.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.unapproved_continuation_event",
            "incident_count": 7,
            "incident_ids": [
                "AER-0013",
                "AER-0023",
                "AER-0113",
                "AER-0149",
                "AER-0152",
                "AER-0156",
                "AER-0187",
            ],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Before constructing any receipt, copy continuation_event verbatim from orchestration/harness_settings/orchestrator_requirements.yaml; descriptive lifecycle detail belongs in planned_action and source evidence, never in the enum field.",
                "Before drafting any receipt state, copy both continuation_event and the complete adapter/managed-slot inventory directly from the active orchestrator requirements and a recent passing envelope; descriptive phase names belong only in planned_action.",
                "Before every orchestrator receipt, copy continuation_event from orchestration/harness_settings/orchestrator_requirements.yaml and put task-specific phase language only in planned_action; a revision_required receipt forbids runtime until a distinct corrected state passes.",
                "Copy continuation_event from orchestration/harness_settings/orchestrator_requirements.yaml before drafting each runtime state; never infer an event label from a filename or planned action, especially after the same recurrence has already been recorded.",
                "Every Ariadne receipt state must copy continuation_event directly from orchestration/harness_settings/orchestrator_requirements.yaml before planned_action is drafted; any unapproved event produces immutable revision_required evidence and a distinct corrected state.",
                "Receipt construction must select continuation_event directly from orchestration/harness_settings/orchestrator_requirements.yaml and preserve any fail-closed envelope before issuing a corrected distinct receipt.",
                "Receipt construction must select continuation_event directly from orchestration/harness_settings/orchestrator_requirements.yaml; pre-planning specifically uses pre_sprint_planning and sprint_planning, and any fail-closed envelope remains immutable before a corrected distinct receipt.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.verifier_preflight_expected_head_not_read_from_git"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0090", "AER-0091"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Populate verifier expected_head only from the literal output of git rev-parse HEAD in the target worktree.",
                "The closeout protocol now requires a standalone git rev-parse HEAD read immediately before every verifier preflight and forbids manually completing abbreviated hashes.",
            ],
        },
        {
            "recurrence_signature": (
                "orchestrator.worker_dispatch_continuation_event_and_assignment_envelope"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0080", "AER-0253"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Copy the approved continuation event from a passing native-worker predispatch receipt and leave assigned_agent_ids empty unless an actual workspace receipt is already present; descriptive lane availability belongs in adapter evidence and worker_slots.",
                "For every remaining AES-C3 dispatch receipt, copy continuation_event and assignment fields from a passing external-worker receipt; a separately preflighted worktree belongs in source evidence, while workspace_receipts and assigned_agent_ids remain empty until their harness-governed assignment exists.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.worker_dispatch_runtime_contract",
            "incident_count": 11,
            "incident_ids": [
                "AER-0024",
                "AER-0030",
                "AER-0055",
                "AER-0147",
                "AER-0153",
                "AER-0154",
                "AER-0157",
                "AER-0160",
                "AER-0250",
                "AER-0297",
                "AER-0335",
            ],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Before any receipt is generated, copy both adapter_id and method as an exact admitted pair from orchestration/harness_settings/transport_adapters.yaml; keep descriptive evidence classification only in the evidence string and never promote it into method.",
                "Before each verifier dispatch receipt, copy adapter methods from transport_adapters.yaml and use workspace_receipts only for handoff-aligned assigned worker contracts; a separately preflighted external review worktree belongs in source evidence rather than that structure.",
                "Before every dispatch receipt, copy the continuation_event verbatim from orchestrator_requirements.yaml, keep assigned_agent_ids empty until the native reviewer exists, and mirror a previously admitted native-review workspace receipt rather than inventing event labels or assignment identities.",
                "Before orchestrator preflight, treat workspace_receipts as a schema-governed assignment structure rather than an arbitrary evidence-path list; never predeclare an external verifier active or assigned when only the separate read-only worktree preflight exists.",
                "Before pre-worker-dispatch receipt construction, copy adapter methods from orchestration/harness_settings/transport_adapters.yaml and require one field-complete workspace_receipt whose agent_id matches every assigned and active worker; never infer these values from transport prose.",
                "Construct every adapter observation by copying allowed_probe_methods from orchestration/harness_settings/transport_adapters.yaml for that exact adapter_id; never reuse the primary-session method when a native subagent is merely being observed.",
                "Construct every adapter observation by copying an admitted method from orchestration/harness_settings/transport_adapters.yaml; descriptive transport prose belongs in evidence, never in the method field.",
                "Construct worker predispatch lane and workspace objects from the last passing stage-equivalent receipt, selecting disposition from the configured enum and emitting every required workspace field before preflight.",
                "Copy adapter observation and assignment shapes only from the current harness contract, keep native session coordination out of adapter probes and validate the state before any worker spawn.",
                "Every Antigravity launch must supply --orchestrator-receipt; scripts/ariadne_antigravity.py verifies the exact five sources, status passed and worker_dispatch_permitted true before reading the packet or invoking agy. External verifier worktrees remain separate evidence and are never predeclared as native assigned agents.",
                "For every remaining AES-C2 receipt, copy each adapter_id and method as an exact pair from transport_adapters.yaml; completed-transport detail belongs only in the observation evidence string.",
            ],
        },
        {
            "recurrence_signature": "verifier.multiple_terminal_decisions",
            "incident_count": 6,
            "incident_ids": [
                "AER-0004",
                "AER-0006",
                "AER-0018",
                "AER-0020",
                "AER-0032",
                "AER-0033",
            ],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "New Antigravity reviews must use one closed schema-constrained JSON decision object; deterministic parsing deduplicates identical wrapper mirrors, rejects missing or conflicting envelopes and forbids legacy terminal markers inside review text.",
                "The verifier wrapper admits exactly one terminal decision and rejects zero or duplicate terminal envelopes before acceptance.",
                "The verifier wrapper must continue exact-single-decision admission; duplicate output never becomes a verdict, and bounded recovery uses a fresh project/worktree without changing candidate scope.",
                "The wrapper regex counts terminal decisions and rejects any count other than one; tests cover missing and duplicate decisions.",
                "Verifier packets for potentially asynchronous checks must require all background notifications to complete before one final terminal response and forbid any later follow-up; exact-single-decision wrapper admission remains mandatory.",
                "Verifier packets must require all commands and notifications to settle before exactly one terminal line, and the wrapper must continue rejecting every zero-or-duplicate result before candidate acceptance.",
            ],
        },
        {
            "recurrence_signature": (
                "implementer.self_pass_with_contradictory_or_underclosed_canonical_contract"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0324", "AER-0331"],
            "origins": ["agent_behavior"],
            "categories": ["reasoning_claim_error"],
            "roles": ["implementer"],
            "resource_ids": ["deepseek-flash-workers"],
            "prevention_controls": [
                "Before admitting any worker self-pass for a stateful harness contract, independently probe every command state for identity conflict, preserve literal append order, reject contradictory same-fingerprint gate history, require exact proposal/source/reviewer/promoter binding, and derive rollback solely from validated immutable promotion history; test counts and hostile-mutation totals never substitute for semantic admission.",
                "Before any worker self-pass is admitted, independently validate canonical temporal relations and enumerate every frozen closed-contract field and nullable success coordinate; focused test success cannot substitute for semantic packet admission.",
            ],
        },
        {
            "recurrence_signature": "implementer.self_pass_with_material_acceptance_gaps",
            "incident_count": 2,
            "incident_ids": ["AER-0025", "AER-0026"],
            "origins": ["agent_behavior"],
            "categories": ["reasoning_claim_error"],
            "roles": ["implementer"],
            "resource_ids": ["deepseek-v4-flash-c4-worker"],
            "prevention_controls": [
                "Authority and one-use review must exercise more than single-instance happy paths: mutate current role during a blocked handler, race two runtime instances over the same evidence store, and prove shared idempotency, attempt sequencing and authority locking before a repair self-pass can be considered.",
                "Worker path compliance and passing authored tests are necessary but insufficient: before integration, independently adversarially exercise malformed scalar admission, actual-target readback, current authority drift, rollback audit disposition, exact schema property names, non-caller-selectable entropy and concurrent issuance uniqueness.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.pre_review_format_gate_omitted",
            "incident_count": 2,
            "incident_ids": ["AER-0274", "AER-0280"],
            "origins": ["agent_behavior"],
            "categories": ["reasoning_claim_error"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-sol-orchestrator"],
            "prevention_controls": [
                "Before every external review, execute and record every command in the packet's allowlist locally, including format checks, rather than treating Ruff lint as a formatter substitute.",
                "Generate verifier allowed-command blocks from one executable local gate list, persist each exit code before dispatch, and make the launcher reject any external pass receipt whose required command outcomes are nonzero.",
            ],
        },
        {
            "recurrence_signature": ("diagnosis.undefined_symbol_parser_undercoverage"),
            "incident_count": 2,
            "incident_ids": ["AER-0158", "AER-0161"],
            "origins": ["harness"],
            "categories": ["harness_failure"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Database diagnostics should prefer typed catalogue-resolution probes over human-formatted error-text parsing; when text is used, an unrecognized format must emit a bounded unresolved classification rather than erase otherwise valid cleanup and observation evidence.",
                "Undefined-symbol diagnostics must combine fixed catalogue probes with repository-bounded identifier admission; a historical failure allowlist may be the first classifier but never the sole classifier for a later execution path.",
            ],
        },
        {
            "recurrence_signature": (
                "harness.shell_wrapper_timeout_before_live_external_worker_completion"
            ),
            "incident_count": 3,
            "incident_ids": ["AER-0256", "AER-0332", "AER-0333"],
            "origins": ["harness"],
            "categories": ["harness_failure"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-shell-command-timeout-wrapper"],
            "prevention_controls": [
                "Never reuse an arbitrary fixed wrapper timeout after a timeout incident. Derive outer timeout greater than inner timeout plus margin, and never chain Ruff, diff or other later gates behind a long pytest process.",
                "Run future long external worker launchers through a sufficiently long or asynchronous wrapper and monitor their own terminal receipt; a shell timeout is harness evidence, not a worker decision, while the exact authorized process remains live.",
                "Set every outer orchestration timeout to cover the declared inner adapter timeout. After any outer timeout, inspect the exact process, receipt and worktree before considering recovery; never retry while the original authorized process may still complete.",
            ],
        },
        {
            "recurrence_signature": "harness.windows_verifier_worktree_destination_path_too_long",
            "incident_count": 3,
            "incident_ids": ["AER-0063", "AER-0078", "AER-0094"],
            "origins": ["harness"],
            "categories": ["harness_failure"],
            "roles": ["orchestrator"],
            "resource_ids": ["git-worktree-windows-path-layout"],
            "prevention_controls": [
                "All Windows verifier worktrees use the next short rNN path by default; descriptive tranche identity belongs only in branch, packet and receipt metadata.",
                "On Windows this repository must allocate every new verifier worktree from the next available short rNN destination before constructing any descriptive path; tranche identity belongs only in the branch, packet and receipt.",
                "Windows verifier worktrees use the short rNN root naming pattern; descriptive tranche identity belongs in the review packet and receipt rather than the filesystem destination.",
            ],
        },
        {
            "recurrence_signature": "repository.api_spine_historical_expectation_drift",
            "incident_count": 2,
            "incident_ids": ["AER-0068", "AER-0338"],
            "origins": ["repository"],
            "categories": ["repository_defect"],
            "roles": ["orchestrator"],
            "resource_ids": ["api-spine-historical-regression-suite"],
            "prevention_controls": [
                "Future cross-programme regression gates must run a source-HEAD baseline preflight and separate pre-existing collection or expectation drift from candidate-caused regressions before using the suite as acceptance evidence.",
                "Run every mandatory legacy regression at the plan source before worker dispatch, bind frozen digests to the exact current source, and classify any source-identical expectation drift before evaluating descendant causation.",
            ],
        },
        {
            "recurrence_signature": (
                "repository.schema_qualified_postgresql_special_form"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0131", "AER-0140"],
            "origins": ["repository"],
            "categories": ["repository_defect"],
            "roles": ["orchestrator"],
            "resource_ids": ["emr4-disposable-postgresql-harness"],
            "prevention_controls": [
                "Generated PostgreSQL SQL must distinguish special syntactic forms from callable functions, and exact renderer tests must forbid schema-qualified special forms before runtime review.",
                "Generated PostgreSQL SQL must maintain an artifact-wide census of non-callable special forms, forbid namespace qualification for each form, and hostile-test the full accepted renderer independently of any downstream harness query generator.",
            ],
        },
        {
            "recurrence_signature": (
                "repository.clean_checkout_mutable_fixture_dependency"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0163", "AER-0222"],
            "origins": ["repository"],
            "categories": ["repository_defect"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "Review-packet tests must be collected and executed in a clean committed worktree before verifier admission; assertions over mutable untracked evidence must state and handle its optional clean-checkout absence.",
                "Run each exact review packet from a clean committed worktree before verifier admission; diagnosis code and tests may compare a mutable untracked alias only behind an explicit existence guard while immutable evidence remains mandatory.",
            ],
        },
        {
            "recurrence_signature": "transport.deepseek_occupied_worker_no_terminal_response",
            "incident_count": 4,
            "incident_ids": ["AER-0036", "AER-0038", "AER-0326", "AER-0367"],
            "origins": ["transport"],
            "categories": ["transport_timeout"],
            "roles": ["implementer"],
            "resource_ids": ["deepseek-flash-workers"],
            "prevention_controls": [
                "A failed bounded Flash correction receives no further same-lane retry. Exact HEAD, changed-path and receipt readback remain mandatory; partial source stays quarantined while Sol independently reimplements and verifies the correction.",
                "A recurrent DeepSeek no-terminal transport event triggers direct Sol fallback after exact result-path, owned-path, HEAD and worktree readback; no same-lane retry or late source adoption is permitted without a distinct authorised recovery.",
                "DeepSeek implementation leases retain the bounded no-artifact/no-terminal observation window, exact process/worktree readback, sanitized failure receipt and no-source-adoption rule; recurrence triggers direct Sol fallback rather than a same-lane retry.",
                "Occupied development workers require a bounded no-artifact/no-terminal observation window, exact process and worktree readback, a sanitized failure receipt, and a declared fallback that cannot broaden the frozen packet or protected authority.",
            ],
        },
        {
            "recurrence_signature": "transport.antigravity_oauth_timeout_without_closeout",
            "incident_count": 5,
            "incident_ids": [
                "AER-0022",
                "AER-0031",
                "AER-0034",
                "AER-0039",
                "AER-0198",
            ],
            "origins": ["transport"],
            "categories": ["transport_timeout"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "After one bounded fresh-project authentication retry, preserve a sanitized zero-call receipt and use the configured authentication-or-transport fallback against the same exact clean HEAD instead of repeatedly interrupting the programme for ceremonial reauthentication.",
                "Authentication failures remain transport incidents with no inferred reviewer decision; preserve a sanitized failure, require human credential restoration, then use a fresh process and reverify exact HEAD, clean status and single-decision admission.",
                "Preserve every Antigravity OAuth timeout as a sanitized zero-model transport incident, permit at most one same-head same-model retry, and require exact clean postflight plus a distinct successful receipt before review admission; never silently change verifier or model.",
                "Treat Antigravity OAuth as a human-restored transport boundary distinct from ADC and gcloud stores; preserve every sanitized timeout and require exact-head plus clean-worktree readback before a fresh-project recovery result is admitted.",
                "Treat Antigravity OAuth as its own human-restored credential boundary, distinct from ADC and gcloud stores; preserve sanitized timeout failures, then use a fresh new-project process and require one decision plus unchanged postflight before acceptance.",
            ],
        },
    ]
    assert "do not prove model" in report["interpretation_boundary"]


def test_native_reviewer_environment_bootstrap_is_separate_and_contained() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0011"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["resource_id"] == "codex-native-independent-reviewer"
    assert incident["category"] == "command_scope_violation"
    assert incident["recurrence_signature"] == (
        "verifier.unapproved_environment_bootstrap"
    )
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert incident["status"] == "contained"


def test_detached_antigravity_preflight_is_orchestrator_not_provider_error() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0012"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["resource_id"] == "codex-primary-orchestrator"
    assert incident["model"] is None
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == ("orchestrator.detached_verifier_branch")
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_unapproved_acceptance_event_failed_closed_before_corrected_receipt() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0013"]
    failed_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-architecture-preacceptance-receipt.json"
    )
    corrected_receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-architecture-pre-verifier-acceptance-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.unapproved_continuation_event"
    )
    assert failed_receipt["continuation_event"] == "pre_acceptance"
    assert failed_receipt["status"] == "revision_required"
    assert failed_receipt["worker_dispatch_permitted"] is False
    assert failed_receipt["rehydrated_from_receipt"] is False
    assert corrected_receipt["continuation_event"] == "pre_verifier_acceptance"
    assert corrected_receipt["status"] == "passed"
    assert corrected_receipt["rehydrated_from_receipt"] is True


def test_recurrent_detached_branch_activates_pre_receipt_control() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    first = incidents["AER-0012"]
    recurrence = incidents["AER-0014"]
    preflight = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-gate-minus-one-verifier-worktree-preflight.json"
    )
    policy = yaml.safe_load(
        (
            ROOT
            / "orchestration"
            / "harness_settings"
            / "verifier_execution_policy.yaml"
        ).read_text(encoding="utf-8")
    )

    assert first["recurrence_signature"] == recurrence["recurrence_signature"]
    assert recurrence["correction"]["status"] == "control_added"
    assert preflight["status"] == "passed"
    assert preflight["clean"] is True
    assert preflight["branch"].startswith("codex/review-")
    assert policy["execution_order"][0] == "verifier_worktree_preflight"
    assert (
        policy["deterministic_gate"]["required_results"]["verifier_worktree_preflight"]
        == "passed"
    )


def test_gate_minus_one_review_transport_claim_is_corrected_fresh() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0015"]
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-gate-minus-one-review-claim-failure-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-gate-minus-one-review-2-receipt.json"
    )

    assert incident["category"] == "evidence_misreport"
    assert incident["recurrence_signature"] == (
        "verifier.review_transport_misreported_as_zero"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert failure["raw_receipt_sha256"] == (
        "9a5ed7c38fd21ddd2d9616730fc5fd584684e058c4021e6c3e405abe288e8ec5"
    )
    assert "review itself invoked Gemini" in failure["conflict"]
    assert failure["decision_admitted"] is False
    assert failure["candidate_changed"] is False
    assert corrected["decision"] == "pass"
    assert (
        corrected["head_before"]
        == corrected["head_after"]
        == ("2b62f040bcc1c300dca6fb730e0f986d22f3be85")
    )
    assert corrected["dirty_after"] is False
    assert (
        "Candidate Product/Runtime Side Effects (Observed): Exactly 0"
        in (corrected["result"])
    )
    assert "Development Review Transport (Observed): Non-Zero" in corrected["result"]
    assert "invoked `gemini-3.6-flash-high`" in corrected["result"]


def test_a3_b3_preflight_reservation_failure_has_hash_bound_resume_control() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0016"]
    blocked = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "model-required-bureau-a3-b3"
        / "occupied-preflight-blocked-evidence.json"
    )

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["recurrence_signature"] == (
        "harness.preflight_blocked_cost_reservation_orphaned"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"
    assert blocked["reason_code"] == "impersonated_adc_refresh_failed"
    assert blocked["provider_call_count"] == 0
    assert blocked["cost_reservation"]["provider_calls_reserved"] == 1
    assert blocked["cost_reservation"]["provider_calls_consumed"] == 0


def test_a3_b3_terminal_broker_failure_has_evidence_only_recovery() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0017"]
    interruption = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "model-required-bureau-a3-b3"
        / "occupied-terminal-interruption-evidence.json"
    )

    assert incident["origin"] == "harness"
    assert incident["model"] is None
    assert incident["category"] == "harness_failure"
    assert incident["recurrence_signature"] == (
        "harness.postcall_terminal_evidence_and_parent_consumption_split"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"
    assert interruption["reason_code"] == "provider_content_invalid"
    assert interruption["provider_call_count"] == 1
    assert interruption["proofreader_reached"] is False
    assert interruption["correction_eligible"] is False
    assert interruption["release_created"] is False
    assert interruption["davida_b3_started"] is False
    assert interruption["cause_beyond_structural_failure_established"] is False


def test_a3_b3_review_7_duplicate_decision_is_contained() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0018"]
    failure = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "model-required-bureau-a3-b3-review-7-transport-failure.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == ("verifier.multiple_terminal_decisions")
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert failure["observed_terminal_decision_count"] == 2
    assert failure["candidate_finding_established"] is False
    assert failure["candidate_runtime_provider_calls"] == 0
    assert failure["worktree_clean_after"] is True
    assert failure["worktree_head_after"] == failure["candidate_head"]
    assert failure["raw_verifier_output_retained"] is False


def test_a3_b3_recovery_review_duplicate_decision_is_corrected() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0020"]
    review = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-a3-b3-request-contract-recovery-review-2-receipt.json"
    )

    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert review["decision"] == "pass"
    assert review["result"].count("DECISION: pass") == 1
    assert "DECISION: revision_required" not in review["result"]
    assert review["head_before"] == review["head_after"]
    assert review["dirty_after"] is False


def test_a3_b3_hashed_audit_checkout_is_lf_pinned() -> None:
    relative = (
        "orchestration/continuity/model-required-bureau-a3-b3/"
        "rayleen-a3-attempt-1-occupied-audit.jsonl"
    )
    audit_bytes = (ROOT / relative).read_bytes()
    interruption = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "model-required-bureau-a3-b3"
        / "occupied-terminal-interruption-evidence.json"
    )
    attribute = subprocess.run(
        ["git", "check-attr", "eol", "--", relative],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )

    assert attribute.stdout.strip().endswith(": eol: lf")
    assert b"\r\n" not in audit_bytes
    assert (
        "sha256:" + hashlib.sha256(audit_bytes).hexdigest()
        == (interruption["source_artifact_hashes"]["audit_chain"])
    )


def test_a3_b3_review_8_checkout_defect_is_registered() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0019"]
    review = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "model-required-bureau-a3-b3-review-8-receipt.json"
    )

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["recurrence_signature"] == (
        "repository.hash_bound_jsonl_checkout_line_ending_drift"
    )
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"
    assert review["decision"] == "revision_required"
    assert review["head_before"] == review["head_after"]
    assert review["dirty_after"] is False


def test_aer_0185_updates_live_parent_assertion_before_packet_restart() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0185"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "repository.current_parent_acceptance_test_stale_after_rebind"
    )
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0186_preserves_source_membership_fixture_defect() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0186"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "repository.behavior_fixture_component_digest_substituted_for_canonical_membership"
    )
    assert "all eleven ordered outbox fields" in incident["observed_error"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0187_preserves_rejected_recovery_receipt_and_corrected_v2() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0187"]
    failed = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-source-membership-fixture-recovery-preplanning-receipt.json"
    )
    corrected = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-source-membership-fixture-recovery-preplanning-v2-receipt.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.unapproved_continuation_event"
    )
    assert failed["status"] == "revision_required"
    assert "continuation_event_missing_or_unapproved" in failed["reasons"]
    assert corrected["continuation_event"] == "pre_sprint_planning"
    assert corrected["status"] == "passed"
    assert corrected["rehydrated_from_receipt"] is True
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0188_rejects_nonreproducible_passed_receipt() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0188"]
    original = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-input-namespace-behavior-attempt-033-preexecution-receipt.json"
    )
    reproduction = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-input-namespace-behavior-attempt-033-preexecution-reproduction-receipt.json"
    )
    rejection = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-input-namespace-behavior-attempt-033-preexecution-sol-rejection.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["recurrence_signature"] == (
        "orchestrator.receipt_status_inconsistent_with_deterministic_builder"
    )
    assert original["status"] == "passed"
    assert original["continuation_event"] == "pre_execution"
    assert reproduction["status"] == "revision_required"
    assert "continuation_event_missing_or_unapproved" in reproduction["reasons"]
    assert rejection["decision"] == "revision_required"
    assert rejection["original_receipt"]["accepted"] is False
    assert rejection["additional_database_runs"] == 0
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_aer_0189_preserves_admission_row_shape_and_null_reload_defect() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0189"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "repository.generated_row_shape_contradicts_structural_check_and_null_reload_semantics"
    )
    assert "SQLSTATE 23514" in incident["observed_error"]
    assert "five winner predicates" in incident["observed_error"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0190_preserves_masked_builder_failure_and_independent_rerun() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0190"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.sequential_required_command_failure_masked_by_later_exit"
    )
    assert "ModuleNotFoundError" in incident["observed_error"]
    assert "python -m" in incident["correction"]["action"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0191_preserves_clean_checkout_test_veto_and_guarded_repair() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0191"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "raisa-context-fabric-durability-admission-row-shape-parent-recovery-review-receipt.json"
    )

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["stage"] == "independent_review"
    assert incident["recurrence_signature"] == (
        "repository.clean_checkout_test_requires_untracked_mutable_evidence"
    )
    assert receipt["decision"] == "revision_required"
    assert receipt["head_before"] == "094368904acb79b214c68e8521f789709a832db6"
    assert receipt["head_after"] == receipt["head_before"]
    assert receipt["dirty_after"] is False
    assert "319 passed, 1 failed" in receipt["result"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0192_preserves_nonexistent_parent_binding_and_exact_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0192"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert (
        "c8ab7602e16e24453dbf909597b4f702a2388416" in incident["correction"]["action"]
    )
    assert "No database run occurred" in incident["correction"]["action"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0193_rejects_verifier_pass_with_exact_parent_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0193"]
    receipt = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "antigravity"
        / "raisa-context-fabric-durability-parse-characterization-review-receipt.json"
    )
    rejection = _json(
        ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "raisa-context-fabric-durability-parse-characterization-review-sol-rejection.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["workflow_disposition"] == "review_rejected"
    assert receipt["decision"] == "pass"
    assert rejection["accepted"] is False
    assert rejection["additional_database_runs"] == 0
    assert rejection["actual_parent_head"] == (
        "c8ab7602e16e24453dbf909597b4f702a2388416"
    )
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert incident["status"] == "corrected"


def test_aer_0194_separates_characterization_from_protected_evidence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0194"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "harness.characterization_and_historical_failure_share_evidence_target"
    )
    assert "no second database run" in incident["detection_method"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert "three distinct paths" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0195_aligns_coordinator_generation_lock_rls_without_direct_dml() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0195"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "repository.coordinator_generation_update_policy_hides_authorized_transition_lock"
    )
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert "zero direct table SELECT or DML" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0196_catches_inferred_full_git_hash_before_dispatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0196"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert "Before any verifier or database call" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0197_rejects_hash_equal_evidence_path_substitution() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0197"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "verifier.absent_mutable_evidence_path_substituted_by_hash_equal_historical_file"
    )
    assert "identical bytes" in incident["expected_invariant"]
    assert "opened no reproduction database run" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0198_contains_antigravity_auth_timeout_before_retry_pass() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0198"]

    assert incident["origin"] == "transport"
    assert incident["role"] == "verifier"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "transport.antigravity_oauth_timeout_without_closeout"
    )
    assert "no reviewer receipt" in incident["observed_error"]
    assert "opened no database or behavior run" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0199_rejects_nonexistent_active_plan_path_before_behavior() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0199"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "verifier.nonexistent_active_plan_path_reported_in_five_source_rehydration"
    )
    assert "did not exist" in incident["observed_error"]
    assert "opened no database or behavior run" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0200_rejects_unsupported_preexecution_event_before_dispatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0200"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert "pre_execution" in incident["observed_error"]
    assert "pre_worker_dispatch" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0201_contains_exact_id_absence_command_errors() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0201"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "incorrect Docker executable path" in incident["observed_error"]
    assert "exact-ID absence" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0202_repairs_anchor_lock_visibility_without_write_authority() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0202"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert "FOR SHARE" in incident["observed_error"]
    assert "pol_cf_08_update_lock" in incident["correction"]["action"]
    assert "AND FALSE" in incident["correction"]["action"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0203_corrects_unapproved_native_adapter_probe_method() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0203"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert "codex_native_subagent_observation" in incident["observed_error"]
    assert "non-probing synthetic fixture" in incident["correction"]["action"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0204_reuses_module_invocation_control_after_direct_path_failure() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0204"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.python_package_script_path_invocation"
    )
    assert "ModuleNotFoundError" in incident["observed_error"]
    assert "python -m scripts." in incident["correction"]["action"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0205_rejects_inferred_body_source_commit_before_regeneration() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0205"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert "f94d4c61f1fe" in incident["observed_error"]
    assert "f94d4c610dbf" in incident["correction"]["action"]
    assert "No artifact regeneration" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0206_rejects_untracked_mutable_evidence_test_dependency() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0206"]
    assert incident["origin"] == "repository"
    assert incident["role"] == "verifier"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["recurrence_signature"] == (
        "repository.verifier_test_depended_on_protected_untracked_mutable_evidence"
    )
    assert "intentionally untracked" in incident["observed_error"]
    assert "diagnosis 029" in incident["correction"]["action"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0207_rejects_recurrent_inferred_candidate_commit() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0207"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert incident["related_incident_ids"] == []
    assert "040a069b95e0" in incident["observed_error"]
    assert "040a069b4b64" in incident["correction"]["action"]
    assert "no receipt or model call" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0208_records_admission_row_lock_rls_gap() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0208"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "repository.forced_rls_admission_row_lock_missing_update_visibility"
    )
    assert "function line 307" in incident["observed_error"]
    assert "pol_cf_04_update_lock" in incident["correction"]["action"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0209_corrects_precommit_staged_path_count() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0209"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.precommit_receipt_staged_path_count_mismatch"
    )
    assert "eight" in incident["observed_error"]
    assert "nine" in incident["correction"]["action"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0210_rejects_recurrent_structural_parent_hash_inference() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0210"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert "3a19167e2f00" in incident["observed_error"]
    assert "3a19167e13ac" in incident["correction"]["action"]
    assert "No action used" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0211_reconciles_recurrent_register_count_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0211"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert "expected 131" in incident["detection_method"]
    assert "revision 183 with 211 incidents" in incident["correction"]["action"]
    assert incident["correction"]["status"] == (
        "control_implemented_pending_acceptance"
    )
    assert incident["status"] == "corrected"


def test_aer_0212_records_forced_rls_outbox_coordinator_visibility_gap() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0212"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "repository.forced_rls_coordinator_outbox_select_visibility_missing"
    )
    assert "pol_cf_03_select" in incident["observed_error"]
    assert (
        "zero coordinator direct table SELECT/DML" in incident["correction"]["action"]
    )
    assert incident["status"] == "corrected"


def test_aer_0213_records_closed_result_kind_admission_gap() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0213"]
    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "harness.behavior_success_result_kind_not_admitted"
    )
    assert "REBASE_APPLIED" in incident["observed_error"]
    assert "missing, duplicate and wrong markers" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0214_records_windows_wildcard_and_exit_masking() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0214"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.windows_wildcard_literal_and_chained_exit_masked"
    )
    assert incident["related_incident_ids"] == []
    assert "file was not found" in incident["observed_error"]
    assert "LASTEXITCODE" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0215_records_behavior_probe_index_elision() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0215"]
    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "harness.semantic_probe_failure_index_elided"
    )
    assert incident["related_incident_ids"] == []
    assert "seven value-free boolean predicates" in incident["observed_error"]
    assert "one-based failed probe indexes" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0216_records_behavior_obligation_probe_scope_omission() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0216"]
    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "harness.behavior_obligation_probe_scope_omitted"
    )
    assert incident["related_incident_ids"] == []
    assert "preseeded beta obligation" in incident["observed_error"]
    assert "exact alpha practice and stream" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0217_records_transition_marker_rejection_masking() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0217"]
    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "harness.transition_marker_masked_rejection_classification"
    )
    assert incident["related_incident_ids"] == []
    assert "masking any underlying rejection" in incident["observed_error"]
    assert "SQLSTATE mismatch" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0218_records_receipt_lock_rls_policy_gap() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0218"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["recurrence_signature"] == (
        "repository.forced_rls_lock_policy_missing"
    )
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["related_incident_ids"] == []
    assert "FOR UPDATE" in incident["observed_error"]
    assert "pol_cf_09_update_lock" in incident["correction"]["action"]
    assert incident["correction"]["action"].endswith(
        "before another disposable behavior attempt."
    )
    assert incident["status"] == "corrected"


def test_aer_0219_rejects_inferred_receipt_lock_parent_full_hash() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0219"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert "1b37d217682f" in incident["observed_error"]
    assert "1b37d217779a" in incident["correction"]["action"]
    assert "No action used" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0220_preserves_and_corrects_incomplete_receipt_inventory() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0220"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "worker_slot_inventory_missing" in incident["detection_method"]
    assert "all six configured adapters" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0221_records_failed_r170_powershell_parse_before_git() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0221"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert (
        "before Git ran" in incident["expected_invariant"] + incident["observed_error"]
    )
    assert "r170" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0222_records_recurrent_clean_checkout_mutable_dependency() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0222"]
    assert incident["origin"] == "repository"
    assert incident["role"] == "verifier"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "repository.clean_checkout_mutable_fixture_dependency"
    )
    assert "only when" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0223_records_recurrent_touched_python_format_omission() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0223"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "review_rejected"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "orchestrator.touched_python_format_preflight_incomplete"
    )
    assert "git diff --name-only" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0224_corrects_reviewer_self_provider_call_misreport() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0224"]
    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "verifier.self_model_call_misreported_as_zero_provider_calls"
    )
    assert "one bounded Gemini 3.6 Flash/high" in incident["correction"]["action"]
    assert "zero additional provider" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0225_records_rejected_powershell_backup_parameter() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0225"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "New-Item -LiteralPath" in incident["observed_error"]
    assert "ErrorActionPreference Stop" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0226_records_behavior_missing_source_expectation_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0226"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["related_incident_ids"] == []
    assert "BTR-E06" in incident["observed_error"]
    assert "F_CARDINALITY/CF004" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0227_records_diagnosis_end_delimiter_assumption() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0227"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "str.index" in incident["observed_error"]
    assert "apply_durability_transition_v1" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0228_records_assumed_docker_executable_location() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0228"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "Program Files" in incident["observed_error"]
    assert "docker.exe" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0229_records_scenario_not_null_coordinate_gap() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0229"]
    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["related_incident_ids"] == []
    assert "BTR-I02" in incident["observed_error"]
    assert "23502" in incident["observed_error"]
    assert "raw stderr remains digest-only" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0230_records_not_null_telemetry_scope_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0230"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "non-23502" in incident["observed_error"]
    assert "exact SQLSTATE 23502" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0231_records_base_sqlstate_omission() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0231"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "lacked only its expected SQLSTATE" in incident["detection_method"]
    assert "exactly 23502" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0242_records_fail_closed_powershell_statement_composition() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0242"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "parse time" in incident["observed_error"]
    assert "named Boolean" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0243_separates_inherited_identity_from_definition_digest() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0243"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "infeasible preimage requirement" in incident["observed_error"]
    assert "independently recompute" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0244_records_closed_severity_enum_validation() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0244"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "unrecognised literal" in incident["observed_error"]
    assert "schema-valid value moderate" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0245_records_masked_closed_stage_enum_validation() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0245"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["process_severity"] == "low"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "masked this independent field violation" in incident["observed_error"]
    assert "schema-valid stage" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0246_records_powershell_probe_composition_recurrence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0246"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "JSONDecodeError" in incident["detection_method"]
    assert "quote HEAD:path" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0247_records_incident_specific_patch_context() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0247"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "AER-0003" in incident["observed_error"]
    assert "incident_id" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0248_records_derived_register_expectation_reconciliation() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0248"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "214 tests" in incident["observed_error"]
    assert "recurring-pattern object" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0249_records_runtime_compatible_hash_formatting() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0249"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "ToHexString" in incident["observed_error"]
    assert "BitConverter" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0250_records_exact_adapter_observation_method_recovery() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0250"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "completed_transport_receipt" in incident["observed_error"]
    assert "deepseek_claude_cli_observation" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0251_rejects_false_adapter_call_and_open_packet_self_pass() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0251"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["resource_id"] == "deepseek-flash-workers"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "ACTUAL 0" in incident["detection_method"]
    assert "undeclared top-level field" in incident["observed_error"]
    assert "actual fixed callable" in incident["correction"]["prevention_control"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "fresh exact-head Gemini" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0252_keeps_worker_only_paths_out_of_primary_register_evidence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0252"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "isolated worker worktree" in incident["observed_error"]
    assert "primary repository root" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0342_through_0347_bind_risk_weighted_reform_corrections() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    expected = {
        "AER-0342": (
            "output_contract_violation",
            "canonical_unchanged",
            "orchestrator.risk_weighted_preplanning_latch_and_lane_vocabulary_invalid",
        ),
        "AER-0343": (
            "evidence_misreport",
            "canonical_unchanged",
            "orchestrator.risk_weighted_worker_source_full_sha_manually_invented",
        ),
        "AER-0344": (
            "command_scope_violation",
            "canonical_unchanged",
            "orchestrator.risk_weighted_focused_test_process_identity_discarded",
        ),
        "AER-0345": (
            "reasoning_claim_error",
            "untrusted_partial_worktree",
            "implementer.risk_weighted_admission_trusted_authority_bearing_candidate_claims",
        ),
        "AER-0346": (
            "output_contract_violation",
            "canonical_unchanged",
            "orchestrator.risk_weighted_review_preflight_selected_primary_old_script",
        ),
        "AER-0347": (
            "command_scope_violation",
            "canonical_unchanged",
            "orchestrator.risk_weighted_gemini_manifest_selected_primary_old_serial_runner",
        ),
    }

    for incident_id, (
        category,
        candidate_state,
        recurrence_signature,
    ) in expected.items():
        incident = incidents[incident_id]
        assert incident["origin"] == "agent_behavior"
        assert incident["category"] == category
        assert incident["candidate_state"] == candidate_state
        assert incident["workflow_disposition"] == "revision_required"
        assert incident["recurrence_signature"] == recurrence_signature
        assert incident["causal_claim_level"] == "observation_only"
        assert incident["correction"]["status"] == "corrected_fresh_attempt"
        assert incident["status"] == "corrected"

    assert incidents["AER-0345"]["role"] == "implementer"
    assert incidents["AER-0345"]["resource_id"] == "deepseek-flash-workers"
    assert incidents["AER-0347"]["stage"] == "independent_review"


def test_aer_0348_through_0356_bind_delete_confirm_behavior_recovery() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    expected = {
        "AER-0348": (
            "agent_behavior",
            "output_contract_violation",
            "canonical_unchanged",
        ),
        "AER-0349": (
            "agent_behavior",
            "evidence_misreport",
            "untrusted_partial_worktree",
        ),
        "AER-0350": (
            "agent_behavior",
            "command_scope_violation",
            "untrusted_partial_worktree",
        ),
        "AER-0351": ("harness", "harness_failure", "accepted_candidate_changed"),
        "AER-0352": ("harness", "harness_failure", "accepted_candidate_changed"),
        "AER-0353": ("harness", "harness_failure", "accepted_candidate_changed"),
        "AER-0354": ("agent_behavior", "evidence_misreport", "canonical_unchanged"),
        "AER-0355": ("harness", "harness_failure", "accepted_candidate_changed"),
        "AER-0356": ("agent_behavior", "evidence_misreport", "canonical_unchanged"),
    }

    for incident_id, (origin, category, candidate_state) in expected.items():
        incident = incidents[incident_id]
        assert incident["origin"] == origin
        assert incident["category"] == category
        assert incident["candidate_state"] == candidate_state
        assert incident["causal_claim_level"] == "observation_only"
        assert incident["related_incident_ids"] == []

    assert incidents["AER-0355"]["status"] == "corrected"
    assert incidents["AER-0355"]["correction"]["status"] == "recovery_lease_applied"
    assert incidents["AER-0356"]["status"] == "contained"
    assert incidents["AER-0356"]["correction"]["status"] == "contained_then_escalated"
    assert (
        incidents["AER-0354"]["recurrence_signature"]
        == incidents["AER-0356"]["recurrence_signature"]
    )

    report = build_pattern_report()
    hash_recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.git_evidence_future_commit_hash_invented_from_short_prefix"
    )
    assert hash_recurrence["incident_ids"] == [
        "AER-0354",
        "AER-0356",
        "AER-0363",
        "AER-0370",
        "AER-0376",
    ]


def test_aer_0357_records_checkout_hash_recurrence_and_canonical_lf_control() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0357"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["stage"] == "independent_review"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert (
        incident["recurrence_signature"]
        == incidents["AER-0349"]["recurrence_signature"]
    )
    assert "canonical LF" in incident["correction"]["prevention_control"]

    report = build_pattern_report()
    recurrence = next(
        row
        for row in report["recurring_patterns"]
        if row["recurrence_signature"]
        == "orchestrator.raw_text_hash_bound_to_primary_crlf_worktree_bytes"
    )
    assert recurrence["incident_ids"] == ["AER-0349", "AER-0357"]


def test_pattern_report_is_byte_deterministic(tmp_path: Path) -> None:
    first = build_pattern_report()
    second = build_pattern_report()
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    write_json_lf(first_path, first)
    write_json_lf(second_path, second)

    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_bytes().endswith(b"\n")
    assert b"\r\n" not in first_path.read_bytes()


def test_register_hash_is_invariant_across_checkout_line_endings(
    tmp_path: Path,
) -> None:
    original = REGISTER_PATH.read_text(encoding="utf-8")
    crlf_path = tmp_path / "register-crlf.json"
    crlf_path.write_bytes(
        original.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    )

    original_report = build_pattern_report()
    crlf_report = build_pattern_report(register_path=crlf_path)

    assert (
        original_report["canonical_register_sha256"]
        == crlf_report["canonical_register_sha256"]
    )


def test_committed_pattern_report_matches_fresh_build() -> None:
    committed = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "ariadne-agent-error-register"
        / "pattern-report.json"
    )

    assert committed == build_pattern_report()


def test_verifier_policy_requires_incident_learning_before_acceptance() -> None:
    policy = yaml.safe_load(
        (
            ROOT
            / "orchestration"
            / "harness_settings"
            / "verifier_execution_policy.yaml"
        ).read_text(encoding="utf-8")
    )
    learning = policy["incident_learning"]

    assert learning["register_before_corrected_attempt_acceptance"] is True
    assert learning["controls"] == {
        "immutable_failure_evidence": "required",
        "correction_linkage": "required",
        "recurrence_threshold": 2,
        "raw_prompts_secrets_and_sensitive_values": "forbidden",
        "model_provider_or_role_causal_claim_without_separate_evidence": "forbidden",
        "candidate_runtime_and_review_transport_claims": "separately_required",
    }
    assert set(learning["origin_classes"]) == {
        "agent_behavior",
        "transport",
        "harness",
        "repository",
        "operator",
    }


def test_duplicate_incident_id_fails_closed() -> None:
    register = _register()
    register["incidents"][1]["incident_id"] = "AER-0001"

    with pytest.raises(ValueError, match="duplicate incident_id"):
        validate_register(register, _schema())


def test_aer_0358_records_provider_free_pytest_database_boundary() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0358"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "control_added"
    assert "--noconftest" in incident["correction"]["action"]
    assert (
        "ariadne_provider_free_pytest" in (incident["correction"]["prevention_control"])
    )


def test_aer_0359_and_0360_preserve_delete_confirm_worker_recovery() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    original = incidents["AER-0359"]
    assert original["role"] == "implementer"
    assert original["category"] == "output_contract_violation"
    assert original["workflow_disposition"] == "revision_required"
    assert original["correction"]["status"] == "corrected_fresh_attempt"
    assert original["status"] == "corrected"

    corrected = incidents["AER-0360"]
    assert corrected["role"] == "implementer"
    assert corrected["category"] == "output_contract_violation"
    assert corrected["workflow_disposition"] == "recovery_lease_invoked"
    assert corrected["correction"]["status"] == "recovery_lease_applied"
    assert corrected["status"] == "corrected"
    assert "both freshness coordinates" in corrected["correction"]["action"]
    assert "physical-seam ordering" in (corrected["correction"]["prevention_control"])


def test_aer_0361_requires_acceptance_index_guard_for_handover_edits() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0361"]

    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "control_added"
    assert (
        "handover_edits_require_acceptance_index_guard"
        in (incident["correction"]["action"])
    )
    assert incident["status"] == "corrected"


def test_aer_0362_rejects_stale_latched_settings_fingerprint() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0362"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["correction"]["status"] == "control_added"
    assert "active-operation checkpoint" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0363_requires_local_commit_resolution_for_git_ref_evidence() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0363"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["stage"] == "closeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"
    assert (
        incident["recurrence_signature"]
        == incidents["AER-0354"]["recurrence_signature"]
        == incidents["AER-0356"]["recurrence_signature"]
    )
    assert "git cat-file" in incident["correction"]["prevention_control"]


def test_aer_0364_records_report_timestamp_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0364"]

    assert incident["role"] == "implementer"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "timestamp" in incident["observed_error"].lower()
    assert "adjacent" in incident["correction"]["prevention_control"].lower()


def test_aer_0365_records_tree_object_in_commit_ref_evidence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0365"]

    assert incident["role"] == "orchestrator"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "tree object id" in incident["observed_error"].lower()
    assert "before any model call" in incident["observed_error"].lower()


def test_aer_0366_and_0367_preserve_delete_route_recovery() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    candidate = incidents["AER-0366"]
    assert candidate["origin"] == "agent_behavior"
    assert candidate["role"] == "implementer"
    assert candidate["category"] == "output_contract_violation"
    assert candidate["candidate_state"] == "untrusted_partial_worktree"
    assert candidate["workflow_disposition"] == "recovery_lease_invoked"
    assert candidate["correction"]["status"] == "recovery_lease_applied"
    assert candidate["status"] == "corrected"
    assert "generic appointment envelope" in candidate["observed_error"]
    assert "nested" in candidate["correction"]["prevention_control"]

    correction = incidents["AER-0367"]
    assert correction["origin"] == "transport"
    assert correction["role"] == "implementer"
    assert correction["category"] == "transport_timeout"
    assert correction["candidate_state"] == "untrusted_partial_worktree"
    assert correction["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert correction["correction"]["status"] == "contained_then_escalated"
    assert correction["status"] == "contained"
    assert correction["recurrence_signature"] == (
        "transport.deepseek_occupied_worker_no_terminal_response"
    )


def test_aer_0368_records_tree_object_evidence_recurrence() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0368"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert (
        incident["recurrence_signature"]
        == (incidents["AER-0365"]["recurrence_signature"])
    )
    assert "before Gemini dispatch" in incident["observed_error"]
    assert (
        "dedicated worktree-preflight" in (incident["correction"]["prevention_control"])
    )


def test_aer_0369_records_delete_http_postgresql_integration_gap() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0369"]

    assert incident["origin"] == "repository"
    assert incident["role"] == "integration_reviewer"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"
    assert "kind=delete" in incident["observed_error"]
    assert "transaction-local" in incident["correction"]["action"]


def test_aer_0370_records_short_hash_expansion_recurrence() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0370"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert (
        incident["recurrence_signature"]
        == (incidents["AER-0363"]["recurrence_signature"])
    )
    assert "git rev-parse HEAD" in incident["detection_method"]


def test_aer_0371_contains_worker_package_install_outside_worktree() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0371"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "implementer"
    assert incident["resource_id"] == "deepseek-flash-workers"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert "primary repository .venv" in incident["observed_error"]
    assert (
        "package installation is forbidden"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0372_records_recurrent_chained_validation_exit_masking() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0372"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert (
        incident["recurrence_signature"]
        == (incidents["AER-0334"]["recurrence_signature"])
    )
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "corrected"
    assert "file-not-found" in incident["detection_method"]
    assert "separate fail-closed process" in incident["correction"]["action"]


def test_aer_0373_repairs_stale_current_baton_consistency_expectations() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0373"]

    assert incident["origin"] == "repository"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "Continuity 307 / Compass 289" in incident["observed_error"]
    assert "Continuity 308 / Compass 290" in incident["correction"]["action"]
    assert "same candidate" in incident["correction"]["prevention_control"]


def test_aer_0374_repairs_missing_inherited_docker_context() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0374"]

    assert incident["origin"] == "harness"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["status"] == "corrected"
    assert "KeyError('context')" in incident["detection_method"]
    assert "context=default" in incident["correction"]["action"]


def test_aer_0375_repairs_cross_practice_evidence_minter_owner() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0375"]

    assert incident["origin"] == "harness"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["status"] == "corrected"
    assert "DHI-S07" in incident["observed_error"]
    assert "bernie_turn_evidence" in incident["correction"]["action"]


def test_aer_0376_records_recurrent_short_hash_expansion() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0376"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert (
        incident["recurrence_signature"]
        == (incidents["AER-0370"]["recurrence_signature"])
    )
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "corrected"
    assert "git rev-parse HEAD" in incident["detection_method"]
    assert "machine-populating" in incident["correction"]["prevention_control"]


def test_aer_0377_repairs_nested_signed_evidence_copy() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0377"]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "signed_confirmation_evidence_invalid" in incident["observed_error"]
    assert "nested/top-level equality" in incident["correction"]["prevention_control"]


def test_aer_0378_repairs_fixtureless_closeout_invocations() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0378"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "missing client/db fixture" in incident["observed_error"]
    assert "37/37" in incident["detection_method"]
    assert "130/130" in incident["detection_method"]
    assert "conftest_required" in incident["correction"]["prevention_control"]


def test_aer_0379_compacts_the_preexisting_live_handover_overrun() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0379"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["status"] == "corrected"
    assert "80040-byte canonical" in incident["observed_error"]
    assert "stopped all later commands" in incident["detection_method"]
    assert (
        "tests/test_agents_acceptance_index.py"
        in incident["correction"]["prevention_control"]
    )


def test_aer_0380_contains_antigravity_empty_stderr_transport_exhaustion() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0380"]

    assert incident["origin"] == "transport"
    assert incident["role"] == "verifier"
    assert incident["resource_id"] == "antigravity-gemini-flash-3-7-high-verifier"
    assert incident["model"] == "gemini-3.7-flash-high"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "attempt_rejected_and_escalated"
    assert incident["causal_claim_level"] == "observation_only"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"
    assert "exit code 1" in incident["observed_error"]
    assert "empty stderr" in incident["observed_error"]
    assert "no reviewer decision" in incident["detection_method"]
    assert "45-minute" in incident["correction"]["action"]
    assert "stdout/stderr digests" in incident["correction"]["prevention_control"]
    assert (
        "docs/ariadne-antigravity-transport-timeout-diagnosis.md"
        in incident["correction"]["evidence_paths"]
    )
    assert (
        "orchestration/agent_inbox/antigravity/ariadne-effectiveness-and-deepseek-harness-review-gemini37-fresh-review-receipt.json"
        in incident["correction"]["evidence_paths"]
    )


def test_aer_0381_blocks_worker_dispatch_from_terminal_latch_state() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0381"]

    assert incident["origin"] == "harness"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "harness_failure"
    assert incident["process_severity"] == "material"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"
    assert "worker_dispatch_permitted=true" in incident["observed_error"]
    assert "in_progress" in incident["correction"]["action"]


def test_aer_0382_contains_first_deepseek_transport_non_result() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0382"]

    assert incident["origin"] == "transport"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert "before producing a worker result" in incident["observed_error"]
    assert "same-packet retry" in incident["detection_method"]


def test_aer_0383_contains_rejected_preverifier_state_drafts() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0383"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "positive_with_bounded_recovery" in incident["observed_error"]
    assert "No model call" in incident["detection_method"]
    assert "planned" in incident["correction"]["action"]


def test_aer_0384_records_serial_pytest_recurrence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0384"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "PowerShell semicolon" in incident["observed_error"]
    assert "interrupted" in incident["detection_method"]
    assert "ariadne_serial_pytest.py" in incident["correction"]["action"]


def test_aer_0385_records_preplanning_leverage_vocabulary_recurrence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0385"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "positive_independence" in incident["observed_error"]
    assert "No worker ran" in incident["detection_method"]
    assert "required_independence" in incident["correction"]["action"]


def test_aer_0386_records_register_stage_vocabulary_rejection() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0386"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "stage planning" in incident["observed_error"]
    assert "peer linkage mismatch" in incident["detection_method"]
    assert "dispatch" in incident["correction"]["action"]


def test_aer_0387_records_delete_route_fixture_reason_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0387"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "thirteen route-test failures" in incident["observed_error"]
    assert "reason_code_not_dedicated" in incident["observed_error"]
    assert incident["status"] == "contained"
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert "reason-only edit" in incident["correction"]["action"]


def test_aer_0388_records_stale_compass_current_position_literal() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0388"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["stage"] == "closeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "twenty-eight checks" in incident["observed_error"]
    assert "current_position.node_id" in incident["detection_method"]
    assert incident["status"] == "corrected"
    assert incident["correction"]["status"] == "control_added"


def test_aer_0389_records_incomplete_register_metadata_refresh() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0389"]

    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "four failures" in incident["observed_error"]
    assert "two failures" in incident["observed_error"]
    assert "one failure" in incident["observed_error"]
    assert "pattern report equality" in incident["detection_method"]
    assert "ordered ID range" in incident["detection_method"]
    assert "exhaustive pattern set" in incident["detection_method"]
    assert "separately asserted recurrence" in incident["detection_method"]
    assert "superseded phrase" in incident["detection_method"]
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert incident["status"] == "corrected"


def test_aer_0390_records_inconsistent_complete_latch_draft() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0390"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["stage"] == "closeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "resume_after_compaction true" in incident["observed_error"]
    assert "complete state is internally inconsistent" in incident["detection_method"]
    assert incident["status"] == "corrected"


def test_aer_0391_records_deepseek_tests_only_transport_non_result() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0391"]

    assert incident["origin"] == "transport"
    assert incident["role"] == "implementer"
    assert incident["resource_id"] == "deepseek-v4-flash-test-worker"
    assert incident["model"] == "deepseek-v4-flash"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "transport.deepseek_claude_exit_1_before_worker_result"
    )
    assert "before producing a worker result" in incident["observed_error"]
    assert "empty worktree status" in incident["detection_method"]
    assert "without a same-lane retry" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0392_records_exact_verifier_branch_prefix_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0392"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.verifier_preflight_branch_prefix_not_exact_review_prefix"
    )
    assert "codex/review-" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0393_records_combined_browser_timing_control() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0393"]

    assert incident["origin"] == "repository"
    assert incident["role"] == "verifier"
    assert incident["stage"] == "independent_review"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "all 170 combined browser tests" in incident["detection_method"]
    assert "exact same focus predicate" in incident["correction"]["action"]
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_aer_0394_records_postcompaction_receipt_adapter_repair() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0394"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "deepcode_cli and claude_cli_print" in incident["observed_error"]
    assert "synthetic_fixture" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0395_records_direct_register_origin_count_recurrence() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0395"]

    assert incident["origin"] == "repository"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert "len(agent_incidents)" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0396_records_continuity_contract_test_evidence_repair() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0396"]

    assert incident["origin"] == "repository"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "contract_evidence_type_unlinked" in incident["detection_method"]
    assert "required_evidence_types" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0397_records_recurrent_updater_exit_masking() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0397"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.chained_validation_exit_masking"
    )
    assert "shell_sequence_final_exit_code 0" in incident["detection_method"]
    assert "standalone captured process" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0398_records_recurrent_parallelism_leverage_vocabulary_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}["AER-0398"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.parallelism_expected_leverage_vocabulary_mismatch"
    )
    assert "conditional_independence" in incident["observed_error"]
    assert "configured neutral" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0399_records_recurrent_manual_short_sha_expansion() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0399"]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0286"]["recurrence_signature"]
    )
    assert incident["related_incident_ids"] == []
    assert "invalid reference" in incident["detection_method"]
    assert "git rev-parse HEAD" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0400_records_asymmetric_peer_link_validation_failure() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0400"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["related_incident_ids"] == []
    assert "attempt peer linkage mismatch" in incident["observed_error"]
    assert "recurrence grouping" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0401_records_overliteral_register_prose_assertion() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0401"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert "307 tests" in incident["observed_error"]
    assert "semantic phrase" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0402_records_recurrent_closeout_latch_and_baton_fixture_drift() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0402"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0319"]["recurrence_signature"]
    )
    assert "Continuity 313 / Compass 295" in incident["observed_error"]
    assert "Continuity 314 / Compass 296" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0403_records_baton_count_phrase_fixture_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0403"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "11 new checks" in incident["observed_error"]
    assert "Eleven new checks" in incident["correction"]["action"]
    assert "arrival/check-in" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0404_records_live_handover_compactness_overrun() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0404"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "501 lines" in incident["observed_error"]
    assert "two purely presentational blank lines" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0405_records_new_review_prose_fixture_representation_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0405"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "implementation"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["related_incident_ids"] == []
    assert "seven checks" in incident["observed_error"]
    assert "Normalize whitespace" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0406_records_asymmetric_peer_link_rejection() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0406"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0400"]["recurrence_signature"]
    )
    assert "one-way related incident" in incident["observed_error"]
    assert "Remove the unsupported one-way peer" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0407_records_register_population_fixture_drift() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0407"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0340"]["recurrence_signature"]
    )
    assert "four otherwise passing tests" in incident["observed_error"]
    assert "revision 356 and 407 incidents" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0408_records_recurring_pattern_fixture_drift() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0408"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0248"]["recurrence_signature"]
    )
    assert "newly recurrent" in incident["observed_error"]
    assert "five-field recurrence composite" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0409_records_recurrence_composite_misread() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0409"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "five-field composite" in incident["observed_error"]
    assert "matching recurrence_signature text alone is insufficient" in (
        incident["correction"]["prevention_control"]
    )
    assert incident["status"] == "corrected"


def test_aer_0410_records_residual_pattern_exclusion_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0410"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "filtered only from the actual side" in incident["detection_method"]
    assert "one unpaired exclusion" in (
        ROOT / "docs/ariadne-agent-error-correction-register-revision-359.md"
    ).read_text(encoding="utf-8")
    assert incident["status"] == "corrected"


def test_aer_0411_records_compact_baton_historical_name_fixture_drift() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0411"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0403"]["recurrence_signature"]
    )
    assert "historical AER-0399 and AER-0401" in incident["observed_error"]
    assert "current bounded-chain endpoints" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0412_records_register_test_prose_near_synonym() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0412"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0401"]["recurrence_signature"]
    )
    assert "current correction-chain endpoints" in incident["observed_error"]
    assert "current bounded-chain endpoints" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0413_records_closeout_current_fixture_drift() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0413"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0411"]["recurrence_signature"]
    )
    assert "81695 bytes" in incident["observed_error"]
    assert "less-than-80000-byte guard" in incident["observed_error"]
    assert "eight already-live current product-lineage rows" in incident[
        "observed_error"
    ]
    assert incident["status"] == "corrected"


def test_aer_0414_records_complete_latch_terminal_contract_recurrence() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0414"]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        incidents["AER-0390"]["recurrence_signature"]
    )
    assert "complete state is internally inconsistent" in incident[
        "detection_method"
    ]
    assert incident["status"] == "corrected"


def test_aer_0415_records_completed_latch_evidence_drift() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0415"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "closeout"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "revision 362" in incident["observed_error"]
    assert "404-check packet" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0416_records_postpublication_correction_validation_defects() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0416"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "deterministic_verification"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "pre_sprint_planning" in incident["observed_error"]
    assert "CURRENT_LATCH" in incident["observed_error"]
    assert incident["related_incident_ids"] == []
    assert incident["status"] == "corrected"


def test_aer_0417_records_parallelism_leverage_vocabulary_mismatch() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0417"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "required_independence" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0418_records_missing_assigned_worker_workspace_receipt() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0418"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "workspace_receipt_missing" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0419_preserves_non_transferable_deepseek_transport_result() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0419"
    ]

    assert incident["origin"] == "transport"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert "no terminal worker receipt" in incident["observed_error"]
    assert incident["correction"]["status"] == "contained_then_escalated"
    assert incident["status"] == "contained"


def test_aer_0420_and_0421_preserve_sol_admission_selection_and_capture() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    selection = incidents["AER-0420"]
    assert selection["category"] == "output_contract_violation"
    assert "18 missing-fixture errors" in selection["observed_error"]
    assert selection["candidate_state"] == "canonical_unchanged"
    assert selection["status"] == "corrected"

    capture = incidents["AER-0421"]
    assert capture["category"] == "evidence_misreport"
    assert "session identifier" in capture["observed_error"]
    assert "session 38174" in capture["correction"]["action"]
    assert capture["status"] == "corrected"


def test_aer_0422_records_register_aggregate_and_latch_bound_repair() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0422"
    ]

    assert incident["category"] == "output_contract_violation"
    assert "528 characters" in incident["observed_error"]
    assert "293" in incident["observed_error"]
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"


def test_aer_0423_records_compact_latch_prose_fixture_repair() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0423"
    ]

    assert incident["category"] == "output_contract_violation"
    assert "200-test canonical fast profile" in incident["observed_error"]
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"


def test_aer_0424_records_antigravity_egress_failure_receipt_repair() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0424"
    ]

    assert incident["origin"] == "harness"
    assert incident["category"] == "harness_failure"
    assert "observed 0" in incident["observed_error"]
    assert "wrote no failure receipt" in incident["observed_error"]
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["correction"]["status"] == "control_added"
    assert incident["status"] == "corrected"


def test_aer_0425_records_fixture_free_verifier_manifest_correction() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0425"]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert "practice fixture" in incident["observed_error"]
    assert "raw JSON file SHA-256" in incident["observed_error"]
    assert "101/101" in incident["detection_method"]
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["status"] == "corrected"
    assert (
        incidents["AER-0420"]["recurrence_signature"]
        == incident["recurrence_signature"]
    )


def test_missing_or_out_of_scope_evidence_fails_closed() -> None:
    missing = _register()
    missing["incidents"][0]["evidence_paths"][0] = "docs/not-present.json"
    with pytest.raises(ValueError, match="evidence path is missing"):
        validate_register(missing, _schema())

    branding = _register()
    branding["incidents"][0]["evidence_paths"][0] = "docs/branding/README.md"
    with pytest.raises(ValidationError):
        validate_register(branding, _schema())

    mixed_case_branding = _register()
    mixed_case_branding["incidents"][0]["evidence_paths"][0] = (
        "DOCS/Branding/raisa/README.md"
    )
    with pytest.raises(ValidationError):
        validate_register(mixed_case_branding, _schema())


def test_origin_category_mismatch_fails_closed() -> None:
    register = _register()
    register["incidents"][6]["origin"] = "agent_behavior"

    with pytest.raises(ValueError, match="origin/category mismatch"):
        validate_register(register, _schema())


def test_unknown_sensitive_or_raw_prompt_field_fails_closed() -> None:
    register = _register()
    register["incidents"][0]["raw_prompt"] = "forbidden"

    with pytest.raises(ValidationError):
        validate_register(register, _schema())


def test_unknown_related_incident_and_attempt_peer_linkage_fail_closed() -> None:
    unknown = _register()
    unknown["incidents"][0]["related_incident_ids"] = ["AER-9999"]
    with pytest.raises(ValueError, match="unknown related incident"):
        validate_register(unknown, _schema())

    asymmetric = _register()
    asymmetric["incidents"][1].pop("related_incident_ids")
    with pytest.raises(ValidationError):
        validate_register(asymmetric, _schema())

    omitted = _register()
    omitted["incidents"][0]["related_incident_ids"] = []
    omitted["incidents"][1]["related_incident_ids"] = []
    with pytest.raises(ValueError, match="attempt peer linkage mismatch"):
        validate_register(omitted, _schema())


def test_same_signature_across_different_dimensions_does_not_merge(
    tmp_path: Path,
) -> None:
    register = _register()
    register["incidents"][0]["recurrence_signature"] = (
        "verifier.multiple_terminal_decisions"
    )
    register_path = tmp_path / "register.json"
    register_path.write_text(json.dumps(register), encoding="utf-8")

    report = build_pattern_report(register_path=register_path)

    duplicate_decisions = next(
        item
        for item in report["recurring_patterns"]
        if item["recurrence_signature"] == "verifier.multiple_terminal_decisions"
    )
    assert duplicate_decisions["incident_ids"] == [
        "AER-0004",
        "AER-0006",
        "AER-0018",
        "AER-0020",
        "AER-0032",
        "AER-0033",
    ]
    assert duplicate_decisions["incident_count"] == 6


def test_v1_rejects_unproved_causal_claim_level() -> None:
    register = _register()
    register["incidents"][0]["causal_claim_level"] = "confirmed_process_cause"

    with pytest.raises(ValidationError):
        validate_register(register, _schema())


def test_extra_schema_leaf_is_rejected() -> None:
    register = copy.deepcopy(_register())
    register["scope"]["exhaustive"] = True

    with pytest.raises(ValidationError):
        validate_register(register, _schema())


def test_aer_0426_records_literal_git_identity_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0426"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.manual_short_sha_expansion"
    )
    assert incident["related_incident_ids"] == []
    assert "invalid reference" in incident["detection_method"]
    assert (
        "4daa2d772ffcf64e55f69917d2fb21802e959673"
        in incident["correction"]["action"]
    )


def test_aer_0427_preserves_deepseek_route_worker_transport_non_result() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0427"
    ]

    assert incident["origin"] == "transport"
    assert incident["stage"] == "dispatch"
    assert incident["category"] == "transport_timeout"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "recovery_lease_invoked"
    assert incident["recurrence_signature"] == (
        "transport.deepseek_claude_exit_1_before_worker_result"
    )
    assert incident["related_incident_ids"] == []
    assert "remained clean" in incident["observed_error"]
    assert incident["correction"]["status"] == "contained_then_escalated"


def test_aer_0428_corrects_candidate_precommit_lane_disposition() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0428"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.plan_precommit_parallelism_disposition_invalid"
    )
    assert incident["related_incident_ids"] == []
    assert "contained_transport_non_result" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0429_corrects_chained_candidate_admission_commands() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0429"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.chained_validation_exit_masking"
    )
    assert incident["related_incident_ids"] == []
    assert "semicolon-composed" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0430_corrects_antigravity_package_cli_invocation() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0430"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.repository_package_cli_file_invocation"
    )
    assert incident["related_incident_ids"] == []
    assert "ModuleNotFoundError" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0431_corrects_future_manual_evidence_timestamps() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0431"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "evidence_misreport"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.durable_evidence_future_manual_timestamp"
    )
    assert incident["related_incident_ids"] == []
    assert "13:22:34" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0432_corrects_resumed_chained_readback() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0432"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "accepted_candidate_changed"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.chained_validation_exit_masking"
    )
    assert incident["related_incident_ids"] == []
    assert "semicolon-composed" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0433_corrects_closeout_contract_evidence_linkage() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0433"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.check_in_route_closeout_contract_evidence_link_omitted"
    )
    assert incident["related_incident_ids"] == []
    assert "contract_evidence_path_not_node_evidence" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0434_corrects_optional_compass_test_path_guess() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0434"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.optional_compass_maintenance_test_path_guessed"
    )
    assert incident["related_incident_ids"] == []
    assert "file-or-directory-not-found" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0435_corrects_closeout_adapter_probe_method() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0435"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.closeout_adapter_probe_method_invalid"
    )
    assert incident["related_incident_ids"] == []
    assert "adapter_probe_method_invalid" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0436_corrects_terminal_latch_incident_range() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0436"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.terminal_latch_incident_range_stale"
    )
    assert incident["related_incident_ids"] == []
    assert "AER-0435" in incident["observed_error"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0437_corrects_mandatory_file_chunk_bound() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0437"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.mandatory_file_chunk_byte_character_bound_mismatch"
    )
    assert incident["related_incident_ids"] == []
    assert "80261" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0438_corrects_successor_register_stage_value() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0438"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.successor_rehydration_register_stage_invalid"
    )
    assert incident["related_incident_ids"] == []
    assert "jsonschema enum failure" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"


def test_aer_0439_through_0445_preserve_native_harness_no_call_corrections() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[438:445] == [
        f"AER-{index:04d}" for index in range(439, 446)
    ]
    assert incidents["AER-0439"]["origin"] == "operator"
    assert incidents["AER-0440"]["category"] == "output_contract_violation"
    assert incidents["AER-0441"]["category"] == "command_scope_violation"
    assert "non-Git" in incidents["AER-0442"]["expected_invariant"]
    assert incidents["AER-0443"]["status"] == "contained"
    assert "bounded_no_provider_call_configuration_failure" in (
        incidents["AER-0443"]["correction"]["action"]
    )
    assert "git rev-parse" in incidents["AER-0444"]["detection_method"]
    assert incidents["AER-0445"]["origin"] == "harness"


def test_aer_0446_through_0450_preserve_agentic_harness_corrections() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[445:450] == [
        f"AER-{index:04d}" for index in range(446, 451)
    ]
    assert incidents["AER-0446"]["category"] == "command_scope_violation"
    assert "session handle" in incidents["AER-0447"]["expected_invariant"]
    assert "named permission preset" in incidents["AER-0448"]["expected_invariant"]
    assert incidents["AER-0449"]["workflow_disposition"] == "revision_required"
    assert incidents["AER-0450"]["status"] == "contained"
    assert "request-start" in incidents["AER-0450"]["correction"]["action"]


def test_aer_0451_preserves_preplanning_event_vocabulary_correction() -> None:
    incident = {row["incident_id"]: row for row in _register()["incidents"]}[
        "AER-0451"
    ]

    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["related_incident_ids"] == []
    assert "pre_plan" in incident["observed_error"]
    assert "pre_sprint_planning" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0452_and_0453_preserve_native_harness_enclosure_recovery() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[451:453] == ["AER-0452", "AER-0453"]
    sha = incidents["AER-0452"]
    assert sha["origin"] == "agent_behavior"
    assert sha["category"] == "reasoning_claim_error"
    assert sha["recurrence_signature"] == "orchestrator.manual_short_sha_expansion"
    assert "git rev-parse HEAD" in sha["observed_error"]
    assert sha["status"] == "corrected"

    enclosure = incidents["AER-0453"]
    assert enclosure["origin"] == "agent_behavior"
    assert enclosure["category"] == "reasoning_claim_error"
    assert enclosure["process_severity"] == "material"
    assert "reads always pass through" in enclosure["observed_error"]
    assert "broker sidecar" in enclosure["correction"]["action"]
    assert enclosure["status"] == "corrected"


def test_aer_0454_and_0455_preserve_container_and_gate_containment() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[453:455] == ["AER-0454", "AER-0455"]
    rootfs = incidents["AER-0454"]
    assert rootfs["origin"] == "harness"
    assert rootfs["category"] == "harness_failure"
    assert rootfs["status"] == "contained"
    assert "MISSING_CREDENTIAL" in rootfs["detection_method"]
    assert "no model-facing shell" in rootfs["correction"]["action"]

    gate = incidents["AER-0455"]
    assert gate["origin"] == "agent_behavior"
    assert gate["category"] == "command_scope_violation"
    assert gate["recurrence_signature"] == (
        "orchestrator.chained_validation_exit_masking"
    )
    assert "newline-separated" in gate["observed_error"]
    assert gate["status"] == "corrected"


def test_aer_0456_preserves_sparse_worker_tools_mode_correction() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0456"]

    assert list(incidents)[455:456] == ["AER-0456"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.deepseek_native_tools_mode_vocabulary_mismatch"
    )
    assert "DSH_TOOLS_MODE=local" in incident["observed_error"]
    assert "MISSING_CREDENTIAL" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0457_and_0458_preserve_predispatch_and_pipeline_corrections() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[456:458] == ["AER-0457", "AER-0458"]
    predispatch = incidents["AER-0457"]
    assert predispatch["category"] == "output_contract_violation"
    assert "selected" in predispatch["observed_error"]
    assert "assigned-agent" in predispatch["correction"]["action"]
    assert predispatch["status"] == "corrected"

    pipeline = incidents["AER-0458"]
    assert pipeline["category"] == "command_scope_violation"
    assert pipeline["related_incident_ids"] == []
    assert pipeline["recurrence_signature"] == (
        "orchestrator.chained_validation_exit_masking"
    )
    assert "Select-Object" in pipeline["observed_error"]
    assert pipeline["status"] == "corrected"


def test_aer_0459_preserves_native_harness_tool_inventory_rejection() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0459"]

    assert list(incidents)[458:459] == ["AER-0459"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "reasoning_claim_error"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["workflow_disposition"] == "revision_required"
    assert incident["recurrence_signature"] == (
        "orchestrator.native_harness_model_facing_tool_inventory_incomplete"
    )
    assert "seven tools" in incident["observed_error"]
    assert "zero provider-call-started" in incident["detection_method"]
    assert "without retry" in incident["correction"]["action"]
    assert incident["status"] == "corrected"


def test_aer_0460_preserves_bounded_latch_checkpoint_correction() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0460"]

    assert list(incidents)[459:460] == ["AER-0460"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.active_operation_checkpoint_text_exceeded_bound"
    )
    assert "completed_stage" in incident["observed_error"]
    assert "standalone active-latch validation" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0461_preserves_continuity_inventory_correction() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0461"]

    assert list(incidents)[460:461] == ["AER-0461"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "orchestrator.continuity_node_contract_evidence_inventory_incomplete"
    )
    assert "contract paths" in incident["observed_error"]
    assert "reentrant branch" in incident["detection_method"]
    assert incident["correction"]["status"] == "corrected_fresh_attempt"
    assert incident["status"] == "corrected"


def test_aer_0462_preserves_typed_continuity_inventory_correction() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0462"]

    assert list(incidents)[461:462] == ["AER-0462"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["related_incident_ids"] == []
    assert incident["recurrence_signature"] == (
        "orchestrator.continuity_node_contract_evidence_inventory_incomplete"
    )
    assert "test paths" in incident["observed_error"]
    assert "typed collection" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0463_preserves_stale_compass_sentinel_correction() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0463"]

    assert list(incidents)[462:463] == ["AER-0463"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["candidate_state"] == "canonical_unchanged"
    assert incident["recurrence_signature"] == (
        "repository.compass_current_position_literal_stale_after_valid_advance"
    )
    assert "already stale" in incident["observed_error"]
    assert "exactly one failure" in incident["detection_method"]
    assert incident["status"] == "corrected"


def test_aer_0473_through_0529_preserve_exact_tool_view_and_successor_corrections() -> (
    None
):
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[472:529] == [
        f"AER-{index:04d}" for index in range(473, 530)
    ]
    assert incidents["AER-0473"]["recurrence_signature"] == (
        "orchestrator.windows_rg_wildcard_path_operand_invalid"
    )
    assert "Normalize" in incidents["AER-0474"]["correction"]["action"]
    assert "dict" in incidents["AER-0475"]["observed_error"]
    assert incidents["AER-0476"]["process_severity"] == "moderate"
    assert "zero" in incidents["AER-0476"]["detection_method"]
    assert incidents["AER-0477"]["related_incident_ids"] == []
    assert incidents["AER-0478"]["attempt_id"].endswith("capture-read-001")
    assert incidents["AER-0479"]["stage"] == "closeout"
    assert "Revision 409" in incidents["AER-0480"]["observed_error"]
    assert "split attempt identity" in incidents["AER-0481"]["detection_method"]
    assert "case-sensitive false negative" in incidents["AER-0482"][
        "observed_error"
    ]
    assert incidents["AER-0483"]["attempt_id"].endswith("register-suite-005")
    assert incidents["AER-0484"]["recurrence_signature"] == (
        "orchestrator.powershell_pipeline_used_for_read_only_projection"
    )
    assert incidents["AER-0485"]["related_incident_ids"] == []
    assert incidents["AER-0486"]["attempt_id"].endswith("validator-006")
    assert incidents["AER-0487"]["stage"] == "deterministic_verification"
    assert incidents["AER-0488"]["category"] == "operator_error"
    assert incidents["AER-0488"]["origin"] == "operator"
    assert incidents["AER-0489"]["category"] == "output_contract_violation"
    assert incidents["AER-0490"]["transport"] == "local_apply_patch"
    assert incidents["AER-0491"]["category"] == "evidence_misreport"
    assert incidents["AER-0492"]["origin"] == "operator"
    assert incidents["AER-0493"]["category"] == "harness_failure"
    assert incidents["AER-0493"]["transport"] == "pinned_linux_docker_provider_free"
    assert incidents["AER-0494"]["recurrence_signature"] == (
        "orchestrator.powershell_pipeline_used_for_read_only_projection"
    )
    assert incidents["AER-0495"]["stage"] == "deterministic_verification"
    assert incidents["AER-0496"]["origin"] == "repository"
    assert incidents["AER-0497"]["workflow_disposition"] == (
        "attempt_rejected_and_escalated"
    )
    assert incidents["AER-0497"]["status"] == "contained"
    assert incidents["AER-0498"]["category"] == "output_contract_violation"
    assert incidents["AER-0499"]["stage"] == "closeout"
    assert incidents["AER-0500"]["correction"]["status"] == "control_added"
    assert incidents["AER-0501"]["candidate_state"] == "untrusted_partial_worktree"
    assert incidents["AER-0502"]["correction"]["status"] == "control_added"
    assert incidents["AER-0503"]["category"] == "output_contract_violation"
    assert incidents["AER-0504"]["origin"] == "repository"
    assert incidents["AER-0505"]["resource_id"] == (
        "ariadne-compass-current-position-test"
    )
    assert incidents["AER-0506"]["process_severity"] == "moderate"
    assert incidents["AER-0503"]["related_incident_ids"] == []
    assert incidents["AER-0507"]["transport"] == "local_repository_validator"
    assert incidents["AER-0508"]["transport"] == "local_apply_patch"
    assert incidents["AER-0509"]["candidate_state"] == "untrusted_partial_worktree"
    assert incidents["AER-0510"]["stage"] == "closeout"
    assert incidents["AER-0511"]["correction"]["status"] == "control_added"
    assert incidents["AER-0512"]["transport"] == "local_active_operation_validator"
    assert incidents["AER-0513"]["stage"] == "closeout"
    assert all(
        incidents[f"AER-{index:04d}"]["status"] == "corrected"
        for index in range(473, 497)
    )
    assert incidents["AER-0498"]["status"] == "corrected"
    assert incidents["AER-0499"]["status"] == "corrected"
    assert incidents["AER-0500"]["status"] == "corrected"
    assert incidents["AER-0501"]["status"] == "corrected"
    assert incidents["AER-0502"]["status"] == "corrected"
    assert all(
        incidents[f"AER-{index:04d}"]["status"] == "corrected"
        for index in range(503, 507)
    )
    assert incidents["AER-0507"]["status"] == "corrected"
    assert incidents["AER-0508"]["status"] == "corrected"
    assert incidents["AER-0509"]["status"] == "corrected"
    assert all(
        incidents[f"AER-{index:04d}"]["status"] == "corrected"
        for index in range(510, 513)
    )
    assert incidents["AER-0513"]["status"] == "corrected"
    assert incidents["AER-0514"]["stage"] == "closeout"
    assert "unmounted" in incidents["AER-0514"]["correction"]["action"]
    assert incidents["AER-0515"]["stage"] == "closeout"
    assert "--output" in incidents["AER-0515"]["observed_error"]
    assert incidents["AER-0516"]["status"] == "corrected"
    assert incidents["AER-0517"]["status"] == "corrected"
    assert incidents["AER-0518"]["status"] == "corrected"
    assert incidents["AER-0519"]["status"] == "corrected"
    assert incidents["AER-0519"]["recurrence_signature"] == (
        "orchestrator.powershell_pipeline_used_for_read_only_projection"
    )
    assert incidents["AER-0520"]["status"] == "corrected"
    assert incidents["AER-0520"]["recurrence_signature"] == (
        "orchestrator.agent_error_register_population_fixture_update_incomplete"
    )
    assert incidents["AER-0521"]["status"] == "corrected"
    assert incidents["AER-0521"]["recurrence_signature"] == (
        "orchestrator.new_recurring_pattern_baseline_not_advanced_atomically"
    )
    assert incidents["AER-0522"]["status"] == "corrected"
    assert incidents["AER-0522"]["recurrence_signature"] == (
        "orchestrator.new_recurring_pattern_baseline_not_advanced_atomically"
    )
    assert incidents["AER-0523"]["status"] == "corrected"
    assert incidents["AER-0523"]["recurrence_signature"] == (
        "orchestrator.current_baton_register_stable_anchor_dropped"
    )
    assert incidents["AER-0524"]["status"] == "corrected"
    assert incidents["AER-0524"]["recurrence_signature"] == (
        "orchestrator.latch_continuity_phrase_stale_after_bounded_checkpoint_rewrite"
    )
    assert incidents["AER-0525"]["status"] == "corrected"
    assert incidents["AER-0525"]["recurrence_signature"] == (
        "orchestrator.continuity_node_contract_evidence_inventory_incomplete"
    )
    assert incidents["AER-0526"]["status"] == "corrected"
    assert incidents["AER-0526"]["recurrence_signature"] == (
        "orchestrator.closeout_continuity_fixture_current_position_mismatch"
    )
    assert incidents["AER-0527"]["status"] == "corrected"
    assert incidents["AER-0527"]["recurrence_signature"] == (
        "repository.compass_current_position_literal_stale_after_valid_advance"
    )
    assert incidents["AER-0528"]["status"] == "corrected"
    assert incidents["AER-0528"]["recurrence_signature"] == (
        "orchestrator.successor_repair_latch_status_fixture_stale_after_completion"
    )
    assert incidents["AER-0529"]["status"] == "corrected"
    assert incidents["AER-0529"]["recurrence_signature"] == (
        "orchestrator.successor_repair_latch_source_fixture_duplicate"
    )


def test_aer_0530_through_0538_preserve_readiness_review_corrections() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[529:538] == [
        f"AER-{index:04d}" for index in range(530, 539)
    ]
    assert incidents["AER-0530"]["origin"] == "repository"
    assert incidents["AER-0530"]["recurrence_signature"] == (
        "repository.active_latch_transition_fixture_stale_after_successor_open"
    )
    assert incidents["AER-0531"]["candidate_state"] == "canonical_unchanged"
    assert "Normalize CRLF" in incidents["AER-0531"]["correction"]["action"]
    assert incidents["AER-0532"]["recurrence_signature"] == (
        "orchestrator.static_marker_ignored_split_string_representation"
    )
    assert incidents["AER-0533"]["related_incident_ids"] == []
    assert incidents["AER-0534"]["related_incident_ids"] == []
    assert incidents["AER-0535"]["transport"] == "local_repository_pytest"
    assert all(incidents[f"AER-{index:04d}"]["origin"] == "operator" for index in range(536, 539))
    assert all(incidents[f"AER-{index:04d}"]["status"] == "corrected" for index in range(530, 539))


def test_aer_0539_corrects_closed_stage_vocabulary() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0539"]

    assert list(incidents)[538:539] == ["AER-0539"]
    assert incident["category"] == "output_contract_violation"
    assert incident["stage"] == "deterministic_verification"
    assert "pre_planning" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.agent_error_stage_value_outside_closed_schema_vocabulary"
    )
    assert incident["status"] == "corrected"


def test_aer_0540_corrects_cross_attempt_peer_links() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0540"]

    assert list(incidents)[539:540] == ["AER-0540"]
    assert incident["related_incident_ids"] == []
    assert "distinct attempt" in incident["observed_error"]
    assert incident["recurrence_signature"] == (
        "orchestrator.agent_error_related_ids_linked_distinct_attempts"
    )
    assert incident["status"] == "corrected"


def test_aer_0541_and_0542_correct_revision_path_and_repeat() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[540:542] == ["AER-0541", "AER-0542"]
    assert incidents["AER-0541"]["recurrence_signature"] == (
        "orchestrator.agent_error_revision_evidence_path_prefix_mistyped"
    )
    assert "raisa-agent-error" in incidents["AER-0541"]["observed_error"]
    assert incidents["AER-0542"]["origin"] == "operator"
    assert "same failure" in incidents["AER-0542"]["observed_error"]
    assert incidents["AER-0541"]["status"] == "corrected"
    assert incidents["AER-0542"]["status"] == "corrected"


def test_aer_0543_and_0544_correct_stale_fixtures_and_guessed_register_path() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[542:544] == ["AER-0543", "AER-0544"]
    assert incidents["AER-0543"]["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert "two stale assertions" in incidents["AER-0543"]["observed_error"]
    assert incidents["AER-0544"]["origin"] == "operator"
    assert "register.json" in incidents["AER-0544"]["observed_error"]
    assert incidents["AER-0543"]["status"] == "corrected"
    assert incidents["AER-0544"]["status"] == "corrected"


def test_aer_0545_completes_the_register_aggregate_fixture_update() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0545"]

    assert list(incidents)[544:545] == ["AER-0545"]
    assert incident["origin"] == "repository"
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert "output_contract_violation" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0546_rebinds_exact_count_recurrence_to_the_canonical_resource() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0546"]

    assert list(incidents)[545:546] == ["AER-0546"]
    assert incident["resource_id"] == "emr4-ariadne-agent-error-register-acceptance"
    assert incident["recurrence_signature"] == (
        "repository.agent_error_register_exact_count_update_incomplete"
    )
    assert "separate two-row group" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0547_and_0548_correct_historical_current_binding_and_utf8_read() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[546:548] == ["AER-0547", "AER-0548"]
    assert incidents["AER-0547"]["recurrence_signature"] == (
        "repository.historical_continuity_test_required_current_position_after_successor"
    )
    assert "passed 135 checks" in incidents["AER-0547"]["observed_error"]
    assert incidents["AER-0548"]["origin"] == "operator"
    assert "cp1252" in incidents["AER-0548"]["observed_error"]
    assert incidents["AER-0547"]["status"] == "corrected"
    assert incidents["AER-0548"]["status"] == "corrected"


def test_aer_0549_corrects_resumed_read_only_pipeline_composition() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0549"]

    assert list(incidents)[548:549] == ["AER-0549"]
    assert incident["origin"] == "operator"
    assert incident["stage"] == "closeout"
    assert incident["recurrence_signature"] == (
        "operator.read_only_shell_pipeline_composed_under_one_executable_control"
    )
    assert "Select-Object pipeline" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0550_corrects_unverified_notification_search_operand() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0550"]

    assert list(incidents)[549:550] == ["AER-0550"]
    assert incident["origin"] == "operator"
    assert incident["recurrence_signature"] == (
        "operator.rg_explicit_path_operand_not_verified_existing"
    )
    assert "nonexistent predecessor" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0551_corrects_abbreviated_continuity_source_head() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0551"]

    assert list(incidents)[550:551] == ["AER-0551"]
    assert incident["origin"] == "agent_behavior"
    assert incident["recurrence_signature"] == (
        "orchestrator.continuity_source_head_used_abbreviated_commit"
    )
    assert "source_head_invalid" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0552_moves_continuity_validation_before_canonical_writes() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0552"]

    assert list(incidents)[551:552] == ["AER-0552"]
    assert incident["origin"] == "repository"
    assert incident["process_severity"] == "moderate"
    assert incident["recurrence_signature"] == (
        "repository.continuity_updater_wrote_canonical_draft_before_semantic_validation"
    )
    assert "acceptance boundary" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0553_through_0555_correct_closeout_fixture_and_operator_failures() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[552:555] == ["AER-0553", "AER-0554", "AER-0555"]
    assert incidents["AER-0553"]["origin"] == "operator"
    assert "verification failed" in incidents["AER-0553"]["detection_method"]
    assert incidents["AER-0554"]["origin"] == "repository"
    assert "passed all other checks" in incidents["AER-0554"]["detection_method"]
    assert incidents["AER-0555"]["origin"] == "operator"
    assert "ParserError" in incidents["AER-0555"]["detection_method"]
    assert all(incidents[f"AER-{index:04d}"]["status"] == "corrected" for index in range(553, 556))


def test_aer_0556_compresses_completed_latch_projection_to_schema_bound() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0556"]

    assert list(incidents)[555:556] == ["AER-0556"]
    assert incident["origin"] == "agent_behavior"
    assert incident["recurrence_signature"] == (
        "orchestrator.active_operation_completed_stage_exceeded_schema_bound"
    )
    assert "ten dependent failures" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0557_corrects_assumed_latch_schema_basename() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0557"]

    assert list(incidents)[556:557] == ["AER-0557"]
    assert incident["origin"] == "agent_behavior"
    assert incident["recurrence_signature"] == (
        "orchestrator.agent_error_evidence_schema_basename_assumed"
    )
    assert "active-operation-latch.schema.json" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0558_and_0559_correct_boundary_literal_and_duplicate_patch_target() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}

    assert list(incidents)[557:559] == ["AER-0558", "AER-0559"]
    assert incidents["AER-0558"]["origin"] == "repository"
    assert "two dependent assertions" in incidents["AER-0558"]["observed_error"]
    assert incidents["AER-0559"]["origin"] == "operator"
    assert "multiple operations target AGENTS.md" in incidents["AER-0559"]["detection_method"]
    assert incidents["AER-0558"]["status"] == "corrected"
    assert incidents["AER-0559"]["status"] == "corrected"


def test_aer_0560_restores_product_data_and_live_provider_boundary_tokens() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0560"]

    assert list(incidents)[559:560] == ["AER-0560"]
    assert incident["origin"] == "repository"
    assert incident["recurrence_signature"] == (
        "repository.current_baton_protected_boundary_literal_paraphrased"
    )
    assert "two remaining dependent" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0561_advances_new_boundary_recurrence_snapshot() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0561"]

    assert list(incidents)[560:561] == ["AER-0561"]
    assert incident["origin"] == "agent_behavior"
    assert incident["recurrence_signature"] == (
        "orchestrator.new_recurring_pattern_baseline_not_advanced_atomically"
    )
    assert "hand-maintained recurring-pattern snapshot" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0562_rebinds_recurrence_composite_resource_identity() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0562"]

    assert list(incidents)[561:562] == ["AER-0562"]
    assert incident["origin"] == "agent_behavior"
    assert incident["recurrence_signature"] == (
        "orchestrator.recurrence_group_resource_identity_not_copied"
    )
    assert "resource_id differed" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0563_separates_preplanning_receipt_from_live_terminal_latch() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0563"]

    assert list(incidents)[562:563] == ["AER-0563"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert incident["related_incident_ids"] == []
    assert "mutable current latch" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0564_corrects_one_way_conceptual_peer_link() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0564"]

    assert list(incidents)[563:564] == ["AER-0564"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["related_incident_ids"] == []
    assert "peer linkage mismatch" in incident["detection_method"]
    assert incident["status"] == "corrected"


def test_aer_0565_advances_source_cutoff_after_date_rollover() -> None:
    register = _register()
    incidents = {row["incident_id"]: row for row in register["incidents"]}
    incident = incidents["AER-0565"]

    assert list(incidents)[564:565] == ["AER-0565"]
    assert register["scope"]["source_cutoff_on"] == "2026-08-19"
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert "source cutoff" in incident["detection_method"]
    assert incident["status"] == "corrected"


def test_aer_0566_advances_standalone_origin_population_fixture() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0566"]

    assert list(incidents)[565:566] == ["AER-0566"]
    assert incident["origin"] == "agent_behavior"
    assert incident["recurrence_signature"] == (
        "orchestrator.agent_error_register_population_fixture_update_incomplete"
    )
    assert "len(agent_incidents)" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0567_resolves_explicit_pytest_paths_before_execution() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0567"]

    assert list(incidents)[566:567] == ["AER-0567"]
    assert incident["origin"] == "operator"
    assert incident["category"] == "operator_error"
    assert "file or directory not found" in incident["detection_method"]
    assert "machine-resolved repository inventory" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0568_separates_historical_terminal_latches_from_live_state() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0568"]

    assert list(incidents)[567:568] == ["AER-0568"]
    assert incident["origin"] == "repository"
    assert incident["category"] == "repository_defect"
    assert "stale else branch" in incident["observed_error"]
    assert "validated generically" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0569_rejects_shell_pipeline_path_discovery() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0569"]

    assert list(incidents)[568:569] == ["AER-0569"]
    assert incident["origin"] == "operator"
    assert incident["category"] == "operator_error"
    assert incident["recurrence_signature"] == (
        "operator.shell_pipeline_used_during_path_discovery"
    )
    assert "one resolved executable and argument vector" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0570_resolves_explicit_repository_paths_before_dispatch() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0570"]

    assert list(incidents)[569:570] == ["AER-0570"]
    assert incident["origin"] == "operator"
    assert incident["category"] == "operator_error"
    assert incident["recurrence_signature"] == (
        "operator.explicit_repository_path_operand_not_inventory_resolved"
    )
    assert "does not exist" in incident["detection_method"]
    assert incident["status"] == "corrected"


def test_aer_0571_derives_population_and_narrative_bindings_from_one_reading() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0571"]

    assert list(incidents)[570:571] == ["AER-0571"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["recurrence_signature"] == (
        "orchestrator.agent_error_register_population_fixture_update_incomplete"
    )
    assert "exactly two failures" in incident["detection_method"]
    assert incident["status"] == "corrected"


def test_aer_0572_replaces_duplicate_recurrence_population_fixtures() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0572"]

    assert list(incidents)[571:572] == ["AER-0572"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "output_contract_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert "second direct assertion" in incident["observed_error"]
    assert "one generated recurrence projection" in incident["correction"]["prevention_control"]
    assert incident["status"] == "corrected"


def test_aer_0573_targets_repeated_count_patches_by_recurrence_signature() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0573"]

    assert list(incidents)[572:573] == ["AER-0573"]
    assert incident["origin"] == "agent_behavior"
    assert incident["category"] == "command_scope_violation"
    assert incident["candidate_state"] == "untrusted_partial_worktree"
    assert incident["transport"] == "local_apply_patch"
    assert "parallelism recurrence count" in incident["observed_error"]
    assert incident["status"] == "corrected"


def test_aer_0574_rejects_verifier_claim_that_widens_evidence_deferral() -> None:
    incidents = {row["incident_id"]: row for row in _register()["incidents"]}
    incident = incidents["AER-0574"]

    assert list(incidents)[573:574] == ["AER-0574"]
    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "verifier"
    assert incident["model"] == "gemini-3.7-flash-high"
    assert incident["category"] == "evidence_misreport"
    assert incident["workflow_disposition"] == "review_rejected"
    assert "newly appended node" in incident["observed_error"]
    assert incident["status"] == "corrected"
