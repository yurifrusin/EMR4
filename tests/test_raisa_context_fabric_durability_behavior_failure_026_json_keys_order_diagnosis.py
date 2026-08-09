from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-026.json"
)


def test_failure_026_is_preserved_byte_identically() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert (
        hashlib.sha256(failure_bytes).hexdigest() == diagnosis.EXPECTED_FAILURE_SHA256
    )
    mutable = (
        diagnosis.BEHAVIOR_DIR / "provider-free-behavior-transaction-evidence.json"
    )
    if mutable.exists():
        mutable_bytes = mutable.read_bytes()
        immutable_attempt = json.loads(failure_bytes)["attempt_id"]
        mutable_attempt = json.loads(mutable_bytes).get("attempt_id")
        if mutable_attempt == immutable_attempt:
            assert failure_bytes == mutable_bytes


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(RECEIPT.read_bytes())


def test_diagnosis_proves_order_mismatch_without_runtime_or_authority_change() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_json_key_order_mismatch_proven_cleanup_verified"
    )
    assert (
        result["diagnosis"]["declared_expected_keys"]
        != result["diagnosis"]["actual_ordered_keys"]
    )
    assert result["diagnosis"]["actual_ordered_keys"] == sorted(
        result["diagnosis"]["declared_expected_keys"]
    )
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["diagnosis"]["raw_postgresql_error_persisted"] is False
    assert result["bounded_repair"] == {
        "renderer_change": "canonicalize_fixed_expected_json_keys_to_lexicographic_order",
        "body_program_change": False,
        "scenario_change": False,
        "authority_change": False,
    }
