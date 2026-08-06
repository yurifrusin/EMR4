"""Focused deterministic tests for the Bureau C5 implementation contracts.

These tests exercise the closed contracts, parser/proofreader, authority/
evidence state machine, provider-request builder and source/import boundaries.
They deliberately do not import ``app`` or any production actuator code and
never start a process, socket, port, directory or provider operation.
"""

from __future__ import annotations

import ast as _ast
import hashlib
import inspect
import json
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

import scripts.model_required_bureau_c5_contract as c5
import scripts.model_required_bureau_c5_rehearsal as c5_rehearsal

from scripts.model_required_bureau_c5_acceptance import (
    CATALOG_DIGEST,
    CORRELATION_ID,
    EVIDENCE_LABEL,
    PLAN_SOURCE_HEAD,
    EXPECTED_RESULT,
    NOW,
    POLICY_DIGEST,
    TARGET_NONCE,
    PYTHON_EXECUTABLE_SHA256,
    PORT,
    admit_provider_candidate,
    build_frame,
    load_candidate_example,
    now_callable,
    parse_candidate,
    _validate_argument_vector,
    _validate_candidate_parsing_and_proofreading,
    _validate_cleanup,
    _validate_cross_runtime_single_winner,
    _validate_digest_reproduction,
    _validate_evidence_issuance,
    _validate_execution_and_replay,
    _validate_fault_injection_and_rollback,
    _validate_frame_minimisation,
    _validate_provider_request_metadata,
    _validate_source_checks,
    build_approval,
    build_evidence,
    mint_evidence as build_issued_evidence,
)
from scripts.model_required_bureau_c5_contract import (
    C5EvidenceIssuer,
    C5SharedStore,
    IssuanceDenied,
    RunbookCatalog,
    build_provider_request_metadata,
    proofread_candidate,
)

ROOT = Path(__file__).resolve().parents[1]


def _errors(schema_path, value):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value)
    )


def test_acceptance_passes_with_exact_label_and_zero_operation_counters():
    evidence = build_evidence()
    assert evidence["passed"] is True
    assert evidence["result"] == EXPECTED_RESULT
    assert "source_head" not in evidence
    assert evidence["plan_source_head"] == PLAN_SOURCE_HEAD
    assert evidence["candidate_source_binding"] == {
        "binding_kind": "repository_relative_artifact_sha256_set",
        "artifact_count": len(evidence["artifact_hashes"]),
        "artifact_set_sha256": c5.canonical_sha256(evidence["artifact_hashes"]),
        "exact_git_head_bound_by_external_review_receipt": True,
        "embedded_git_head": False,
    }
    assert evidence["evidence_label"] == EVIDENCE_LABEL
    assert len(evidence["operation_counters"]) == 20
    assert set(evidence["operation_counters"].values()) == {0}
    assert evidence["context_fabric_implemented"] is False


def test_nine_schemas_are_closed_draft_2020_12_and_examples_validate():
    from scripts.model_required_bureau_c5_acceptance import SCHEMA_EXAMPLES

    assert len(SCHEMA_EXAMPLES) == 9
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert not _errors(schema_path, json.loads(example_path.read_text(encoding="utf-8")))


def test_lf_byte_hashes_and_digests_reproduce():
    evidence = build_evidence()
    for path_string, stored_hash in evidence["artifact_hashes"].items():
        path = ROOT / path_string
        assert hashlib.sha256(path.read_bytes()).hexdigest() == stored_hash
    digests = _validate_digest_reproduction()
    assert digests["catalog_digest_reproduces"] == CATALOG_DIGEST
    assert digests["policy_digest_reproduces"] == POLICY_DIGEST
    catalog = RunbookCatalog.frozen_catalog()
    assert catalog.digest() == CATALOG_DIGEST


def test_frame_minimisation_excludes_internal_values():
    minimisation = _validate_frame_minimisation()
    assert minimisation["port_excluded"] is True
    assert minimisation["pid_excluded"] is True
    assert minimisation["nonce_excluded"] is True
    assert minimisation["path_excluded"] is True
    assert minimisation["environment_excluded"] is True
    assert minimisation["log_excluded"] is True
    assert minimisation["product_excluded"] is True


def test_provider_request_metadata_is_exact_without_sdk_or_network():
    metadata = _validate_provider_request_metadata()["exact"]
    assert metadata["model"] == "gemini-2.5-flash"
    assert metadata["project"] == "bernie-emr4-dev"
    assert metadata["identity"] == "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    assert metadata["region"] == "australia-southeast1"
    assert metadata["endpoint"] == "australia-southeast1-aiplatform.googleapis.com"
    assert metadata["thinking_budget"] == 1024
    assert metadata["max_output_tokens"] == 2048
    assert metadata["candidate_count"] == 1
    assert metadata["temperature"] == 0
    assert metadata["call_limit"] == 2
    assert metadata["cost_ceiling_usd"] == 0.50
    assert metadata["fallback_enabled"] is False
    source = Path("scripts/model_required_bureau_c5_contract.py").read_text(encoding="utf-8")
    assert "import google" not in source and "vertexai" not in source and "anthropic" not in source


def test_candidate_parsing_and_proofreading_ground_every_claim():
    parsing = _validate_candidate_parsing_and_proofreading()
    assert parsing["nominal_admitted"] is True
    assert parsing["grounding_all_true"] is True
    assert parsing["correction_ticket_at_most_one"] is True
    assert parsing["rejections"]["unknown_runbook"] == "UNKNOWN_RUNBOOK"
    assert parsing["rejections"]["scope_expansion"] == "SCOPE_EXPANSION_REJECTED"
    assert parsing["rejections"]["success_claim"] == "SUCCESS_CLAIM_REJECTED"
    assert parsing["rejections"]["duplicate_key"] == "REJECTED"


def test_approval_is_exact_plan_bound_non_transferable_expiring_one_use():
    from scripts.model_required_bureau_c5_acceptance import _validate_approval

    approval = _validate_approval()
    assert approval["exact_plan_bound"] is True
    assert approval["non_transferable"] is True
    assert approval["expiring"] is True
    assert approval["one_rehearsal"] is True


def test_evidence_issuance_is_one_use_expiring_and_non_caller_selectable():
    evidence = _validate_evidence_issuance()
    assert evidence["one_use"] is True
    assert evidence["expiring"] is True
    assert evidence["raw_reference_not_persisted"] is True
    assert evidence["production_signature_has_no_reference_or_nonce"] is True
    assert evidence["unpatched_issuances_differ"] is True


def test_replay_idempotency_and_cross_runtime_single_winner():
    execution = _validate_execution_and_replay()
    assert execution["result"] == "live_development_recovery_verified"
    assert execution["same_key_exact_replay"]["same_receipt"] is True
    assert execution["same_key_changed_fingerprint"] == "IDEMPOTENCY_CONFLICT"
    assert execution["different_key_evidence_reuse"] == "EXECUTION_EVIDENCE_REPLAY"
    concurrency = _validate_cross_runtime_single_winner()
    assert concurrency["launch_attempts"] == 1
    assert concurrency["attempt_record_count"] == 1


def test_faults_never_release_success_and_rollback_is_distinct():
    faults = _validate_fault_injection_and_rollback()
    for name, outcome in faults.items():
        assert outcome["success"] is False, name
        assert outcome["evidence_consumed"] == "consumed", name
        assert outcome["attempt_record_count"] == 1, name
    assert faults["readback_failed_rollback_verified"]["rollback"] == {"invoked": True, "verified": True}
    assert faults["readback_failed_rollback_inconclusive"]["rollback"] == {"invoked": True, "verified": False}


def test_cleanup_rejects_broad_paths_and_proves_absence():
    cleanup = _validate_cleanup()
    assert cleanup["workspace_rejected"] is True
    assert cleanup["broad_path_rejected"] is True
    assert cleanup["no_process"] is True
    assert cleanup["no_listener"] is True


def test_argument_vector_rejects_overrides_and_contains_no_shell():
    argvec = _validate_argument_vector()
    assert argvec["contains_no_shell_string"] is True
    assert argvec["executable_override_rejected"] is True
    assert argvec["module_override_rejected"] is True
    assert argvec["host_override_rejected"] is True
    assert argvec["environment_credential_free"] is True


def test_acceptance_argument_vector_is_portable_across_worktree_roots(
    monkeypatch, tmp_path
):
    first = _validate_argument_vector()["vector"]
    alternate_root = tmp_path / "fresh-review-worktree"
    monkeypatch.setattr(c5_rehearsal, "REPOSITORY_ROOT", alternate_root)
    monkeypatch.setattr(
        c5_rehearsal,
        "TARGET_MODULE_PATH",
        alternate_root / "scripts" / "model_required_bureau_c5_target.py",
    )
    second = _validate_argument_vector()["vector"]

    assert second == first
    assert first[0] == "controller://active-python"
    assert first[2] == "repository://scripts/model_required_bureau_c5_target.py"
    assert not any(str(ROOT) in item for item in first)


def test_production_mint_signature_has_no_reference_or_nonce():
    signature = inspect.signature(C5EvidenceIssuer.mint)
    assert "reference" not in signature.parameters
    assert "nonce" not in signature.parameters


def test_two_unpatched_issuances_produce_different_values():
    def mint_once():
        return build_issued_evidence(
            C5EvidenceIssuer(lambda: NOW), fixed_entropy=False
        )

    first = mint_once()
    second = mint_once()
    assert first.reference != second.reference
    assert first.record.nonce != second.record.nonce
    assert first.record.reference_sha256 != second.record.reference_sha256


def test_source_checks_prove_no_app_database_cloud_or_provider_sdk():
    source = _validate_source_checks()
    for module in ("contract", "rehearsal", "target", "acceptance"):
        assert "app" not in source["imported_modules"][module]
    assert source["no_shell_invocation"] is True
    assert source["no_generic_runner"] is True
    assert source["no_process_discovery"] is True
    assert source["no_dynamic_import_in_contract"] is True
    assert source["no_mounted_route"] is True
    assert source["lf_bytes"]["contract"] is True
    assert source["lf_bytes"]["target"] is True
    assert source["lf_bytes"]["rehearsal"] is True


def test_contract_has_no_ambient_live_capability_imports():
    source = Path("scripts/model_required_bureau_c5_contract.py").read_text(encoding="utf-8")
    tree = _ast.parse(source)
    imported = set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, _ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    banned = {"subprocess", "socket", "http", "urllib", "pathlib", "os", "app"}
    assert not (imported & banned)


def _mint_with_approval(approval):
    frame = build_frame()
    candidate = parse_candidate(frame)
    proofreader = proofread_candidate(candidate, frame)
    return C5EvidenceIssuer(now_callable, C5SharedStore()).mint(
        approval=approval,
        frame=frame,
        candidate=candidate,
        proofreader=proofreader,
        provider_admission_digest="3" * 64,
        port=PORT,
        target_nonce=c5._generate_nonce(),
        generation=2,
        artifact_sha256=c5.EXPECTED_ARTIFACT_SHA256,
        python_executable_sha256=PYTHON_EXECUTABLE_SHA256,
        correlation_id=CORRELATION_ID,
    )


@pytest.mark.parametrize(
    ("field", "value", "expected_reason"),
    [
        ("schema_version", "emr4.execution_approval.v0", "AUTHORITY_MISMATCH"),
        ("approval_id", "not-an-approval", "AUTHORITY_MISMATCH"),
        ("approval_basis", "unrecorded_basis", "AUTHORITY_MISMATCH"),
        ("plan_sha256", "0" * 64, "AUTHORITY_MISMATCH"),
        ("plan_revision", 1, "AUTHORITY_MISMATCH"),
        ("target", c5.TargetRef(c5.PLAN_ENVIRONMENT, c5.TARGET_KIND, "synthetic:other"), "AUTHORITY_MISMATCH"),
        ("fault", "different_fault", "AUTHORITY_MISMATCH"),
        ("runbook_id", "attacker-runbook", "AUTHORITY_MISMATCH"),
        ("rollback_runbook_id", "attacker-rollback", "AUTHORITY_MISMATCH"),
        ("provider", {"model": "other"}, "AUTHORITY_MISMATCH"),
        ("cost_ceiling_usd", 0.51, "AUTHORITY_MISMATCH"),
        ("call_limit", 3, "AUTHORITY_MISMATCH"),
        ("thinking_budget", 0, "AUTHORITY_MISMATCH"),
        ("max_output_tokens", 4096, "AUTHORITY_MISMATCH"),
        ("expires_at", "2026-08-05T08:20:00Z", "STALE_OR_SUPERSEDED"),
        ("rehearsal_count", 2, "AUTHORITY_MISMATCH"),
        ("evidence_label", "different_label", "AUTHORITY_MISMATCH"),
        ("scope_expansion", True, "AUTHORITY_MISMATCH"),
        ("non_transferable", False, "AUTHORITY_MISMATCH"),
    ],
)
def test_every_mutated_frozen_approval_field_is_denied_at_issuance(
    field, value, expected_reason
):
    with pytest.raises(IssuanceDenied) as caught:
        _mint_with_approval(replace(build_approval(), **{field: value}))
    assert caught.value.reason == expected_reason


def test_frame_semantics_and_proofreader_require_distinct_post_fault_evidence():
    frame = build_frame()
    duplicate = replace(
        frame,
        observations=(frame.observations[0], frame.observations[0]),
        frame_digest="",
    )
    duplicate = replace(duplicate, frame_digest=duplicate.digest())
    with pytest.raises(ValueError):
        c5.validate_frame_semantics(duplicate, now=NOW)

    wrong_source = replace(
        frame,
        observations=(
            frame.observations[0],
            replace(
                frame.observations[1],
                observation_source_id=frame.observations[0].observation_source_id,
            ),
        ),
        frame_digest="",
    )
    wrong_source = replace(wrong_source, frame_digest=wrong_source.digest())
    with pytest.raises(ValueError):
        c5.validate_frame_semantics(wrong_source, now=NOW)

    candidate = parse_candidate(frame)
    baseline_only = replace(
        candidate,
        diagnosis=replace(
            candidate.diagnosis,
            evidence_observation_ids=(frame.observations[0].observation_id,),
        ),
    )
    disposition = proofread_candidate(baseline_only, frame)
    assert disposition.admitted is False
    assert "POST_FAULT_EVIDENCE_REQUIRED" in disposition.reason_codes


def test_frame_source_policy_catalog_and_runbook_drift_are_denied():
    frame = build_frame()
    for mutation in (
        {"service_artifact_sha256": "0" * 64},
        {"policy_digest": "0" * 64},
        {"catalog_digest": "0" * 64},
        {"target_reference": "c5:other-target"},
        {"runbooks": {"forward": {}, "rollback": {}}},
    ):
        changed = replace(frame, **mutation, frame_digest="")
        changed = replace(changed, frame_digest=changed.digest())
        with pytest.raises(ValueError):
            c5.validate_frame_semantics(changed, now=NOW)


def test_two_issuers_over_one_shared_store_have_exactly_one_winner():
    store = C5SharedStore()
    frame = build_frame()
    candidate = parse_candidate(frame)
    proofreader = proofread_candidate(candidate, frame)
    admission = admit_provider_candidate(
        store, frame=frame, candidate=candidate, proofreader=proofreader
    )
    first = C5EvidenceIssuer(now_callable, store)
    second = C5EvidenceIssuer(now_callable, store)
    issued = first.mint(
        approval=build_approval(),
        frame=frame,
        candidate=candidate,
        proofreader=proofreader,
        provider_admission_digest=admission,
        port=PORT,
        target_nonce=TARGET_NONCE,
        generation=2,
        artifact_sha256=c5.EXPECTED_ARTIFACT_SHA256,
        python_executable_sha256=PYTHON_EXECUTABLE_SHA256,
        correlation_id=CORRELATION_ID,
    )
    assert issued.record.state == "issued"
    with pytest.raises(IssuanceDenied, match="STALE_OR_SUPERSEDED"):
        second.mint(
            approval=build_approval(),
            frame=frame,
            candidate=candidate,
            proofreader=proofreader,
            provider_admission_digest=admission,
            port=PORT,
            target_nonce=TARGET_NONCE,
            generation=2,
            artifact_sha256=c5.EXPECTED_ARTIFACT_SHA256,
            python_executable_sha256=PYTHON_EXECUTABLE_SHA256,
            correlation_id=CORRELATION_ID,
        )
    assert len(store.evidence_records) == 1


def test_provider_call_and_one_correction_state_is_shared_and_terminal():
    frame = build_frame()
    valid = parse_candidate(frame)

    store = C5SharedStore()
    store.reserve_provider_attempt(
        correlation_id=CORRELATION_ID,
        request_metadata=build_provider_request_metadata(),
        frame_digest=frame.frame_digest,
    )
    rejected = replace(valid, success_claim=True)
    rejected_proof = proofread_candidate(rejected, frame)
    store.record_provider_candidate(
        correlation_id=CORRELATION_ID,
        frame=frame,
        candidate=rejected,
        disposition=rejected_proof,
    )
    ticket = rejected_proof.correction_ticket
    with pytest.raises(ValueError, match="unchanged correction"):
        store.record_provider_candidate(
            correlation_id=CORRELATION_ID,
            frame=frame,
            candidate=rejected,
            disposition=rejected_proof,
            correction_ticket=ticket,
        )

    corrected_but_denied = replace(
        rejected,
        operator_explanation=rejected.operator_explanation + " Bounded correction.",
    )
    corrected_proof = proofread_candidate(corrected_but_denied, frame)
    store.record_provider_candidate(
        correlation_id=CORRELATION_ID,
        frame=frame,
        candidate=corrected_but_denied,
        disposition=corrected_proof,
        correction_ticket=ticket,
    )
    with pytest.raises(ValueError, match="terminal state"):
        store.record_provider_candidate(
            correlation_id=CORRELATION_ID,
            frame=frame,
            candidate=valid,
            disposition=proofread_candidate(valid, frame),
            correction_ticket=ticket,
        )

    for failure_kind in ("schema", "transport"):
        failed_store = C5SharedStore()
        correlation = CORRELATION_ID[:-1] + ("2" if failure_kind == "schema" else "3")
        failed_store.reserve_provider_attempt(
            correlation_id=correlation,
            request_metadata=build_provider_request_metadata(),
            frame_digest=frame.frame_digest,
        )
        failed_store.record_provider_failure(correlation, failure_kind)
        with pytest.raises(ValueError, match="terminal state"):
            failed_store.record_provider_candidate(
                correlation_id=correlation,
                frame=frame,
                candidate=valid,
                disposition=proofread_candidate(valid, frame),
            )

    admitted_store = C5SharedStore()
    admit_provider_candidate(
        admitted_store,
        frame=frame,
        candidate=valid,
        proofreader=proofread_candidate(valid, frame),
    )
    with pytest.raises(ValueError, match="terminal state"):
        admitted_store.record_provider_candidate(
            correlation_id=CORRELATION_ID,
            frame=frame,
            candidate=valid,
            disposition=proofread_candidate(valid, frame),
        )


def test_runtime_parser_and_schemas_reject_duplicate_or_contradictory_arrays():
    raw = load_candidate_example()
    raw["diagnosis"]["evidence_observation_ids"] = ["post-fault", "post-fault"]
    candidate, denial = c5.parse_recovery_candidate(raw, NOW.isoformat())
    assert candidate is None and denial.reason_codes == ("SCHEMA_REJECTED",)

    raw = load_candidate_example()
    raw["diagnosis"]["missing_evidence"] = ["same", "same"]
    candidate, denial = c5.parse_recovery_candidate(raw, NOW.isoformat())
    assert candidate is None and denial.reason_codes == ("SCHEMA_REJECTED",)

    raw = load_candidate_example()
    raw["diagnosis"]["missing_evidence"] = [str(index) for index in range(9)]
    candidate, denial = c5.parse_recovery_candidate(raw, NOW.isoformat())
    assert candidate is None and denial.reason_codes == ("SCHEMA_REJECTED",)

    artifact_root = ROOT / "orchestration/continuity/model-required-bureau-c5-disposable-live-development-recovery"
    frame_value = json.loads((artifact_root / "system-anatomy-frame-set.example.json").read_text())
    frame_value["observations"][1] = dict(frame_value["observations"][0])
    assert _errors(artifact_root / "system-anatomy-frame-set.schema.json", frame_value)

    proof_value = json.loads((artifact_root / "proofreader-disposition.example.json").read_text())
    proof_value["reason_codes"] = ["CONTRADICTION"]
    proof_value["correction_ticket"] = {
        "ticket_id": "ticket-c5-1234567890abcdef",
        "field_paths": ["diagnosis"],
        "reason_codes": ["CONTRADICTION"],
        "frame_digest": proof_value["frame_digest"],
        "open": True,
    }
    assert _errors(artifact_root / "proofreader-disposition.schema.json", proof_value)

    proof_value["admitted"] = False
    proof_value["reason_codes"] = []
    proof_value["correction_ticket"] = None
    assert _errors(artifact_root / "proofreader-disposition.schema.json", proof_value)
