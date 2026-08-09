from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_030_support_execute_grant_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-030.json"
)


def test_failure_030_is_preserved_byte_identically() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(failure_bytes).hexdigest() == (
        diagnosis.EXPECTED_FAILURE_SHA256
    )
    failure = json.loads(failure_bytes)
    mutable = (
        diagnosis.BEHAVIOR_DIR / "provider-free-behavior-transaction-evidence.json"
    )
    if mutable.exists():
        mutable_bytes = mutable.read_bytes()
        mutable_evidence = json.loads(mutable_bytes)
        assert mutable_evidence.get("attempt_id") != failure.get("attempt_id")


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(RECEIPT.read_bytes())


def test_diagnosis_proves_contract_to_renderer_field_mismatch() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_support_execute_grant_omission_proven_cleanup_verified"
    )
    assert result["diagnosis"]["contract_executor_field"] == "executor_roles"
    assert result["diagnosis"]["renderer_lookup_field"] == "execute_roles"
    assert result["diagnosis"]["support_execute_grants_emitted"] == 0
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"]["authority_change"] is False
    assert result["bounded_repair"]["exact_grantee_roles"] == (
        diagnosis.EXPECTED_EXECUTOR_ROLES
    )
