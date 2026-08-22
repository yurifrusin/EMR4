from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_008 as attempt,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-008"
)
EVIDENCE = TOPIC / "rehearsal-evidence.json"
ATTESTATION = TOPIC / "transaction-attestation.json"
ENVELOPE = TOPIC / "attempt-008-execution-envelope.json"
FAILURE = TOPIC / "rehearsal-failure-evidence.json"
INSPECTION = TOPIC / "postterminal-read-only-docker-inspection.json"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_attempt_008_success_terminal_is_closed_and_exact() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    envelope_schema = json.loads(
        attempt.ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    evidence_schema = attempt.accepted._load_json(attempt.accepted.EVIDENCE_SCHEMA_PATH)
    attestation_schema = attempt.accepted._load_json(
        attempt.accepted.ATTESTATION_SCHEMA_PATH
    )
    assert not list(Draft202012Validator(envelope_schema).iter_errors(envelope))
    assert not list(Draft202012Validator(evidence_schema).iter_errors(evidence))
    assert not list(
        Draft202012Validator(attestation_schema).iter_errors(attestation)
    )
    assert not FAILURE.exists()
    assert envelope["result"] == attempt.PASS_RESULT
    assert envelope["base_result"] == attempt.accepted.PASS_RESULT
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["resume_count"] == 0
    assert envelope["fallback_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["ordinary_admission_release_count"] == 0
    assert envelope["product_record_count"] == 0
    assert envelope["cleanup_status"] == "cleanup_verified"
    assert envelope["finalized_cleanup_projection_preserved"] is True
    assert envelope["terminal_artifact_sha256"] == _digest(EVIDENCE)
    assert envelope["transaction_attestation_sha256"] == _digest(ATTESTATION)


def test_transaction_semantics_and_isolation_are_exact() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    assert attestation["explicit_rollback"]["classification"] == (
        "rolled_back_zero_effect"
    )
    assert attestation["explicit_rollback"]["staged_counts"] == {
        "audit": 1,
        "effect": 1,
        "receipt": 1,
    }
    assert attestation["explicit_rollback"]["readback_counts"] == {
        "audit": 0,
        "effect": 0,
        "receipt": 0,
    }
    assert attestation["ambiguous_response"]["classification"] == (
        "connection_lost_without_complete_terminal_response"
    )
    assert attestation["ambiguous_response"]["complete_terminal_response"] is False
    assert attestation["ambiguous_response"]["success_released"] is False
    assert attestation["ambiguous_response"]["retry_count"] == 0
    assert attestation["authoritative_readback"]["classification"] == (
        "committed_exactly_once"
    )
    assert attestation["authoritative_readback"]["counts"] == {
        "audit": 1,
        "effect": 1,
        "receipt": 1,
    }
    assert attestation["authoritative_readback"]["duplicate_effect_count"] == 0
    assert attestation["authoritative_readback"]["other_practice_visible_count"] == 0
    assert attestation["role_catalogue"]["bypass_rls"] is False
    assert attestation["role_catalogue"]["product_privileges"] == 0
    assert evidence["cleanup"] == {
        "attachments_absent": True,
        "matching_owned_resources": 0,
        "network_absent": True,
        "role_absent_before_teardown": True,
        "server_absent": True,
        "sidecars_absent": True,
        "status": "cleanup_verified",
    }


def test_attempt_008_namespace_mechanically_denies_reuse() -> None:
    with pytest.raises(attempt.accepted.RehearsalFailure) as caught:
        attempt.static_check()
    assert caught.value.stage == "attempt_008_execution"
    assert caught.value.code == "terminal_artifact_already_exists"


def test_postterminal_inspection_binds_absence_and_terminal() -> None:
    inspection = json.loads(INSPECTION.read_text(encoding="utf-8"))
    assert inspection["status"] == "owned_docker_resources_absent"
    assert inspection["occupied_execution_count"] == 1
    assert inspection["automatic_retry_count"] == 0
    assert inspection["resume_count"] == 0
    assert inspection["fallback_count"] == 0
    assert inspection["terminal"]["evidence_sha256"] == _digest(EVIDENCE)
    assert inspection["terminal"]["transaction_attestation_sha256"] == _digest(
        ATTESTATION
    )
    assert inspection["terminal"]["execution_envelope_sha256"] == _digest(ENVELOPE)
    assert inspection["terminal"]["failure_evidence_present"] is False
    assert inspection["terminal"]["success_evidence_present"] is True
    assert inspection["terminal"]["transaction_attestation_present"] is True
    assert inspection["terminal"]["cleanup_status"] == "cleanup_verified"
    assert inspection["residue"]["matching_resource_count"] == 0
    assert inspection["residue"]["container_ids"] == []
    assert inspection["residue"]["network_ids"] == []


def test_terminal_and_inspection_are_sanitized() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (EVIDENCE, ATTESTATION, ENVELOPE, INSPECTION)
    )
    for forbidden in (
        "postgresql://",
        "postgres://",
        "PGPASSWORD",
        "BEGIN TRANSACTION",
        "patient_name",
        "appointment_id",
    ):
        assert forbidden not in text
