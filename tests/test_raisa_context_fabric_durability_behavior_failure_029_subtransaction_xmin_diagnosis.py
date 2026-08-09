from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-029.json"
)


def test_failure_029_is_preserved_byte_identically() -> None:
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
        if mutable_evidence.get("attempt_id") == failure.get("attempt_id"):
            assert failure_bytes == mutable_bytes


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(RECEIPT.read_bytes())


def test_diagnosis_proves_subtransaction_xmin_mismatch_without_new_runtime() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_update_subtransaction_xmin_mismatch_proven_cleanup_verified"
    )
    assert result["diagnosis"]["write_inside_exception_block"] is True
    assert result["diagnosis"]["writing_subtransaction_receives_subxid"] is True
    assert result["diagnosis"]["pg_current_xact_id_returns_top_level_xid"] is True
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "update_rendering": (
            "direct_uniquely_keyed_update_returning_into_without_exception_subtransaction"
        ),
        "zero_row_mapping": "found_check_to_cf004",
        "multiple_row_prevention": "renderer_verified_primary_or_unique_key",
        "body_program_change": False,
        "scenario_change": False,
        "authority_change": False,
    }
