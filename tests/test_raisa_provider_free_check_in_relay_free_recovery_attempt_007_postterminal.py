from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_007 as attempt,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-007"
)
FAILURE = TOPIC / "rehearsal-failure-evidence.json"
ENVELOPE = TOPIC / "attempt-007-execution-envelope.json"
INSPECTION = TOPIC / "postterminal-read-only-docker-inspection.json"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_attempt_007_terminal_is_closed_and_exact() -> None:
    failure = json.loads(FAILURE.read_text(encoding="utf-8"))
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    schema = json.loads(attempt.ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema).iter_errors(envelope))
    assert failure == {
        "cleanup": {"status": "not_started"},
        "code": "forbidden_field",
        "evidence_label": (
            "authored_synthetic_provider_free_disposable_postgresql_check_in_"
            "relay_free_rollback_unknown_terminal_response_recovery"
        ),
        "failed_predicates": [],
        "lifecycle": ["attempt_007_wrapper_failed_closed"],
        "plan_source": "eb568174debd6dba2a32d1dea94be7f6b9fd3ddc",
        "result": "failed_closed",
        "retry_count": 0,
        "schema_version": (
            "emr4.check-in-relay-free-rollback-unknown-response-rehearsal-"
            "failure.v1"
        ),
        "server_post_readiness": None,
        "stage": "redaction",
        "success_released": False,
    }
    assert envelope["result"] == "failed_closed"
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["ordinary_admission_release_count"] == 0
    assert envelope["product_record_count"] == 0
    assert envelope["terminal_artifact_sha256"] == _digest(FAILURE)
    assert envelope["transaction_attestation_sha256"] is None
    assert envelope["cleanup_status"] == "not_started"


def test_attempt_007_namespace_mechanically_denies_reuse() -> None:
    with pytest.raises(attempt.accepted.RehearsalFailure) as caught:
        attempt.static_check()
    assert caught.value.stage == "attempt_007_execution"
    assert caught.value.code == "terminal_artifact_already_exists"


def test_postterminal_inspection_binds_absence_without_broad_claim() -> None:
    inspection = json.loads(INSPECTION.read_text(encoding="utf-8"))
    assert inspection["status"] == "owned_docker_resources_absent"
    assert inspection["occupied_execution_count"] == 1
    assert inspection["automatic_retry_count"] == 0
    assert inspection["terminal"]["failure_sha256"] == _digest(FAILURE)
    assert inspection["terminal"]["execution_envelope_sha256"] == _digest(ENVELOPE)
    assert inspection["terminal"]["transaction_attestation_present"] is False
    assert inspection["terminal"]["success_evidence_present"] is False
    assert inspection["residue"]["matching_resource_count"] == 0
    assert inspection["residue"]["container_ids"] == []
    assert inspection["residue"]["network_ids"] == []
    assert inspection["claim_boundary"] == (
        "read_only_owned_docker_resource_absence_only_role_and_transaction_"
        "acceptance_unproved"
    )


def test_terminal_and_inspection_are_sanitized() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in (FAILURE, ENVELOPE, INSPECTION)
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
