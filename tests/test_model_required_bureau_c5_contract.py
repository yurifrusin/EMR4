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
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

import scripts.model_required_bureau_c5_contract as c5

from scripts.model_required_bureau_c5_acceptance import (
    CATALOG_DIGEST,
    CORRELATION_ID,
    EVIDENCE_LABEL,
    EXPECTED_HEAD,
    EXPECTED_RESULT,
    NOW,
    POLICY_DIGEST,
    TARGET_NONCE,
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
)
from scripts.model_required_bureau_c5_contract import (
    C5EvidenceIssuer,
    RunbookCatalog,
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
    assert evidence["source_head"] == EXPECTED_HEAD
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


def test_production_mint_signature_has_no_reference_or_nonce():
    signature = inspect.signature(C5EvidenceIssuer.mint)
    assert "reference" not in signature.parameters
    assert "nonce" not in signature.parameters


def test_two_unpatched_issuances_produce_different_values():
    approval = build_approval()

    def mint_once():
        return C5EvidenceIssuer(lambda: NOW).mint(
            approval=approval,
            target_nonce=TARGET_NONCE,
            generation=2,
            artifact_sha256=c5.EXPECTED_ARTIFACT_SHA256,
            correlation_id=CORRELATION_ID,
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
