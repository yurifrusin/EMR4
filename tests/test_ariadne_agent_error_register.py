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
    assert register["register_revision"] == 56
    assert register["scope"]["coverage"] == "bounded_known_preserved_incidents"
    assert [row["incident_id"] for row in register["incidents"]] == [
        f"AER-{index:04d}" for index in range(1, 55)
    ]
    assert [
        row["incident_id"] for row in register["incidents"] if row["status"] == "open"
    ] == ["AER-0051"]


def test_seed_separates_agent_behavior_from_transport() -> None:
    incidents = _register()["incidents"]
    agent_incidents = [row for row in incidents if row["origin"] == "agent_behavior"]
    transport_incidents = [row for row in incidents if row["origin"] == "transport"]

    assert len(agent_incidents) == 42
    assert len(transport_incidents) == 7
    assert [row["incident_id"] for row in transport_incidents] == [
        "AER-0007",
        "AER-0022",
        "AER-0031",
        "AER-0034",
        "AER-0036",
        "AER-0038",
        "AER-0039",
    ]
    assert {row["category"] for row in transport_incidents} == {"transport_timeout"}
    assert {row["causal_claim_level"] for row in transport_incidents} == {
        "observation_only"
    }


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
    assert plan["status"] == "open"
    assert plan["workflow_disposition"] == "recovery_lease_invoked"
    assert plan["category"] == "reasoning_claim_error"
    assert plan["correction"]["status"] == "control_implemented_pending_acceptance"
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


def test_pattern_report_detects_recurring_control_signals() -> None:
    report = build_pattern_report()

    assert report["incident_count"] == 54
    assert report["open_incident_ids"] == ["AER-0051"]
    assert report["counts"]["by_origin"] == {
        "agent_behavior": 42,
        "harness": 3,
        "repository": 2,
        "transport": 7,
    }
    assert report["counts"]["by_category"] == {
        "command_scope_violation": 9,
        "evidence_misreport": 5,
        "harness_failure": 3,
        "output_contract_violation": 17,
        "read_only_violation": 2,
        "reasoning_claim_error": 9,
        "repository_defect": 2,
        "transport_timeout": 7,
    }
    assert report["counts"]["by_candidate_state"] == {
        "accepted_candidate_changed": 2,
        "canonical_unchanged": 43,
        "untrusted_partial_worktree": 9,
    }
    assert report["recurring_patterns"] == [
        {
            "recurrence_signature": "verifier.exact_packet_test_count_underreport",
            "incident_count": 2,
            "incident_ids": ["AER-0035", "AER-0037"],
            "origins": ["agent_behavior"],
            "categories": ["evidence_misreport"],
            "roles": ["verifier"],
            "resource_ids": ["antigravity-gemini-flash-3-6-high-verifier"],
            "prevention_controls": [
                "Acceptance must machine-reconcile every verifier test-count and repository-path claim against exact collection output and the candidate tree; prose discrepancies are preserved and never copied as authoritative evidence.",
                "Acceptance must reconcile every verifier test-count claim against exact machine collection output; a numerical discrepancy is preserved explicitly and never copied into closeout as authoritative evidence.",
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
            "incident_count": 2,
            "incident_ids": ["AER-0013", "AER-0023"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Receipt construction must select continuation_event directly from orchestration/harness_settings/orchestrator_requirements.yaml and preserve any fail-closed envelope before issuing a corrected distinct receipt.",
                "Receipt construction must select continuation_event directly from orchestration/harness_settings/orchestrator_requirements.yaml; pre-planning specifically uses pre_sprint_planning and sprint_planning, and any fail-closed envelope remains immutable before a corrected distinct receipt.",
            ],
        },
        {
            "recurrence_signature": "orchestrator.worker_dispatch_runtime_contract",
            "incident_count": 2,
            "incident_ids": ["AER-0024", "AER-0030"],
            "origins": ["agent_behavior"],
            "categories": ["output_contract_violation"],
            "roles": ["orchestrator"],
            "resource_ids": ["codex-primary-orchestrator"],
            "prevention_controls": [
                "Before pre-worker-dispatch receipt construction, copy adapter methods from orchestration/harness_settings/transport_adapters.yaml and require one field-complete workspace_receipt whose agent_id matches every assigned and active worker; never infer these values from transport prose.",
                "Construct every adapter observation by copying an admitted method from orchestration/harness_settings/transport_adapters.yaml; descriptive transport prose belongs in evidence, never in the method field.",
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
