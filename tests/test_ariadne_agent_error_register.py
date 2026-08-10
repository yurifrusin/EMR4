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
    assert register["register_revision"] == 168
    assert register["scope"]["coverage"] == "bounded_known_preserved_incidents"
    assert [row["incident_id"] for row in register["incidents"]] == [
        f"AER-{index:04d}" for index in range(1, 195)
    ]
    assert [
        row["incident_id"] for row in register["incidents"] if row["status"] == "open"
    ] == []


def test_seed_separates_agent_behavior_from_transport() -> None:
    incidents = _register()["incidents"]
    agent_incidents = [row for row in incidents if row["origin"] == "agent_behavior"]
    transport_incidents = [row for row in incidents if row["origin"] == "transport"]

    assert len(agent_incidents) == 122
    assert len(transport_incidents) == 8
    assert [row["incident_id"] for row in transport_incidents] == [
        "AER-0007",
        "AER-0022",
        "AER-0031",
        "AER-0034",
        "AER-0036",
        "AER-0038",
        "AER-0039",
        "AER-0081",
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


def test_pattern_report_detects_recurring_control_signals() -> None:
    report = build_pattern_report()

    assert report["incident_count"] == 194


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
    assert report["register_revision"] == 168
    assert report["incident_count"] == 194
    assert report["open_incident_ids"] == []
    assert report["counts"]["by_origin"] == {
        "agent_behavior": 122,
        "harness": 22,
        "repository": 42,
        "transport": 8,
    }
    assert report["counts"]["by_category"] == {
        "command_scope_violation": 20,
        "evidence_misreport": 23,
        "harness_failure": 22,
        "output_contract_violation": 51,
        "read_only_violation": 3,
        "reasoning_claim_error": 25,
        "repository_defect": 42,
        "transport_timeout": 8,
    }
    assert report["counts"]["by_candidate_state"] == {
        "accepted_candidate_changed": 63,
        "canonical_unchanged": 109,
        "untrusted_partial_worktree": 22,
    }
    assert report["recurring_patterns"] == [
        {
            "recurrence_signature": "orchestrator.overbroad_repository_content_search",
            "incident_count": 2,
            "incident_ids": ["AER-0054", "AER-0092"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Architecture recovery packets and Sol self-checks must carry an explicit exact-path read allowlist. Environment facts are read from one named configuration or handover path; broad rg, recursive content search and wildcard discovery are prohibited under protected-evidence containment.",
                "Every environment-discovery step must carry an exact path or executable-name allowlist before execution. Unknown facts become explicit fail-closed plan preconditions rather than triggers for broad search.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.python_package_script_path_invocation",
            "incident_count": 3,
            "incident_ids": ["AER-0058", "AER-0066", "AER-0067"],
            "origins": ["agent_behavior"],
            "categories": ["command_scope_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Invoke every repository script that imports the scripts package through python -m scripts.<module> from the repository root; direct path invocation is reserved for self-contained scripts whose imports have been preflighted.",
                "Invoke import-dependent scripts as python -m scripts.<module> when they expose a module CLI, or import their public API from the repository root; never execute them by filesystem path.",
                "The direct-path exception is removed for this tranche: every Python file under scripts is invoked as a package module unless a recorded preflight proves it has no package imports on every execution path.",
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
            "recurrence_signature": "orchestrator.detached_verifier_branch",
            "incident_count": 2,
            "incident_ids": ["AER-0012", "AER-0014"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Verifier setup must validate a non-empty non-protected codex/review branch and exact candidate HEAD before issuing the pre-verifier receipt or invoking Antigravity.",
                "scripts/ariadne_verifier_worktree_preflight.py must pass on the exact candidate and codex/review branch before a pre-verifier receipt or Antigravity launch; policy ordering and tests enforce the gate.",
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
            "recurrence_signature": "orchestrator.worker_dispatch_runtime_contract",
            "incident_count": 8,
            "incident_ids": [
                "AER-0024",
                "AER-0030",
                "AER-0055",
                "AER-0147",
                "AER-0153",
                "AER-0154",
                "AER-0157",
                "AER-0160",
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
                "Every Antigravity launch must supply --orchestrator-receipt; scripts/ariadne_antigravity.py verifies the exact five sources, status passed and worker_dispatch_permitted true before reading the packet or invoking agy. External verifier worktrees remain separate evidence and are never predeclared as native assigned agents.",
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
            "recurrence_signature": (
                "repository.agent_error_register_exact_count_update_incomplete"
            ),
            "incident_count": 2,
            "incident_ids": ["AER-0175", "AER-0179"],
            "origins": ["repository"],
            "categories": ["repository_defect"],
            "roles": ["orchestrator"],
            "resource_ids": ["emr4-ariadne-agent-error-register-acceptance"],
            "prevention_controls": [
                "Before regenerating the report after any future register edit, search the whole exact register test for every revision, ID-range, seed, origin, category, candidate-state and total-count literal; then run the entire register file as the only acceptance packet.",
                "Every register edit must run the whole exact register test file after regenerating pattern-report.json; partial node selection cannot serve as final register acceptance.",
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
            "recurrence_signature": "transport.deepseek_occupied_worker_no_terminal_response",
            "incident_count": 2,
            "incident_ids": ["AER-0036", "AER-0038"],
            "origins": ["transport"],
            "categories": ["transport_timeout"],
            "roles": ["implementer"],
            "resource_ids": ["deepseek-flash-workers"],
            "prevention_controls": [
                "DeepSeek implementation leases retain the bounded no-artifact/no-terminal observation window, exact process/worktree readback, sanitized failure receipt and no-source-adoption rule; recurrence triggers direct Sol fallback rather than a same-lane retry.",
                "Occupied development workers require a bounded no-artifact/no-terminal observation window, exact process and worktree readback, a sanitized failure receipt, and a declared fallback that cannot broaden the frozen packet or protected authority.",
            ],
        },
        {
            "recurrence_signature": "transport.antigravity_oauth_timeout_without_closeout",
            "incident_count": 4,
            "incident_ids": ["AER-0022", "AER-0031", "AER-0034", "AER-0039"],
            "origins": ["transport"],
            "categories": ["transport_timeout"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "After one bounded fresh-project authentication retry, preserve a sanitized zero-call receipt and use the configured authentication-or-transport fallback against the same exact clean HEAD instead of repeatedly interrupting the programme for ceremonial reauthentication.",
                "Authentication failures remain transport incidents with no inferred reviewer decision; preserve a sanitized failure, require human credential restoration, then use a fresh process and reverify exact HEAD, clean status and single-decision admission.",
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
    contract = _json(
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal"
        / "rehearsal-contract.json"
    )

    assert incident["origin"] == "agent_behavior"
    assert incident["role"] == "orchestrator"
    assert incident["category"] == "evidence_misreport"
    assert incident["recurrence_signature"] == (
        "orchestrator.short_git_hash_fabricated_into_nonexistent_full_object_id"
    )
    assert contract["parent"]["accepted_source_head"] == (
        "c8ab7602e16e24453dbf909597b4f702a2388416"
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
