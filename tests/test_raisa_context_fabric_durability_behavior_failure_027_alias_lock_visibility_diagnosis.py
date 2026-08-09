from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-027.json"
)


def test_failure_027_is_preserved_byte_identically() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(failure_bytes).hexdigest() == (
        diagnosis.EXPECTED_FAILURE_SHA256
    )
    failure = json.loads(failure_bytes)
    mutable = diagnosis.BEHAVIOR_DIR / "provider-free-behavior-transaction-evidence.json"
    if mutable.exists():
        mutable_bytes = mutable.read_bytes()
        mutable_evidence = json.loads(mutable_bytes)
        if mutable_evidence.get("attempt_id") == failure.get("attempt_id"):
            assert failure_bytes == mutable_bytes


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(RECEIPT.read_bytes())


def test_diagnosis_proves_lock_visibility_gap_without_widening_authority() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_alias_lock_update_policy_gap_proven_cleanup_verified"
    )
    assert result["diagnosis"]["row_lock_mode"] == "FOR_KEY_SHARE"
    assert result["diagnosis"]["rls_forced"] is True
    assert result["diagnosis"]["existing_policy_commands"] == ["SELECT", "INSERT"]
    assert result["diagnosis"]["applicable_update_using_policy_present"] is False
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "policy_change": "add_producer_scoped_alias_update_using_visibility_with_permanently_false_write_check",
        "direct_table_grant_change": False,
        "immutable_guard_change": False,
        "body_program_change": False,
        "scenario_change": False,
        "authority_change": False,
    }
