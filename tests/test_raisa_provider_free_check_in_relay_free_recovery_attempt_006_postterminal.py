from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_check_in_relay_free_recovery_attempt_006 as attempt,
)


FAILURE_SHA256 = "3c7049b318fffb28aa70e8b4346f1ed857b7cf34e1780eec21373935f6c88efd"
ENVELOPE_SHA256 = "52470c6c6245f0988dd4f580e68f7a0e21ce5b8636e60119091c089d603bde1c"
EXECUTION_SOURCE = "a9567be36c82bc6d2eebc2488b48cd8bfb9f8d23"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_consumed_terminal_is_exact_closed_and_schema_valid() -> None:
    failure = json.loads(attempt.FAILURE_PATH.read_text(encoding="utf-8"))
    envelope = json.loads(attempt.ENVELOPE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(attempt.ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert _sha256(attempt.FAILURE_PATH) == FAILURE_SHA256
    assert _sha256(attempt.ENVELOPE_PATH) == ENVELOPE_SHA256
    assert not list(Draft202012Validator(schema).iter_errors(envelope))
    assert envelope["result"] == "failed_closed"
    assert envelope["source_head"] == EXECUTION_SOURCE
    assert envelope["occupied_execution_count"] == 1
    assert envelope["automatic_retry_count"] == 0
    assert envelope["ambiguous_success_released"] is False
    assert envelope["ordinary_admission_release_count"] == 0
    assert envelope["product_record_count"] == 0
    assert envelope["terminal_artifact_sha256"] == FAILURE_SHA256
    assert envelope["transaction_attestation_sha256"] is None
    assert envelope["cleanup_status"] == "cleanup_verified"
    assert failure["result"] == "failed_closed"
    assert failure["stage"] == "environment"
    assert failure["code"] == "server_not_running_after_readiness"
    assert failure["retry_count"] == 0
    assert failure["success_released"] is False


def test_failure_coordinate_is_sanitized_and_pretransaction() -> None:
    failure = json.loads(attempt.FAILURE_PATH.read_text(encoding="utf-8"))
    assert failure["lifecycle"] == [
        "static_admission_passed",
        "captured_internal_network_verified",
        "captured_server_created_without_secret_configuration",
        "server_credential_delivered_by_attached_stdin",
    ]
    assert failure["failed_predicates"] == []
    assert failure["server_post_readiness"] == {
        "projection_valid": True,
        "status": "created",
        "running": False,
        "exit_code": 0,
        "oom_killed": False,
        "state_error_empty": True,
        "restart_count": 0,
        "attachment_process": "exited_nonzero",
        "attachment_stdin": "open_after_delivery",
    }
    serialized = json.dumps(failure)
    for forbidden in (
        "password",
        "postgresql://",
        "container_id",
        "network_id",
        "stdout",
        "stderr",
    ):
        assert forbidden not in serialized.lower()


def test_cleanup_is_exact_and_no_attestation_exists() -> None:
    failure = json.loads(attempt.FAILURE_PATH.read_text(encoding="utf-8"))
    assert failure["cleanup"] == {
        "role_absent_before_teardown": True,
        "attachments_absent": True,
        "sidecars_absent": True,
        "server_absent": True,
        "network_absent": True,
        "matching_owned_resources": 0,
        "status": "cleanup_verified",
    }
    assert not attempt.ATTESTATION_PATH.exists()
    assert not attempt.EVIDENCE_PATH.exists()


def test_consumed_namespace_refuses_check_or_reexecution() -> None:
    with pytest.raises(attempt.accepted.RehearsalFailure) as caught:
        attempt.static_check()
    assert caught.value.stage == "attempt_006_execution"
    assert caught.value.code == "terminal_artifact_already_exists"
