from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis as diagnosis,
)


def test_failure_036_is_preserved_and_mutable_evidence_is_restored() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(failure_bytes).hexdigest() == (
        diagnosis.EXPECTED_FAILURE_SHA256
    )
    failure = json.loads(failure_bytes)
    mutable = (
        diagnosis.BEHAVIOR_DIR / "provider-free-behavior-transaction-evidence.json"
    )
    assert mutable.exists()
    mutable_bytes = mutable.read_bytes()
    assert json.loads(mutable_bytes).get("attempt_id") != failure.get("attempt_id")
    assert hashlib.sha256(mutable_bytes).hexdigest() == (
        "09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b"
    )


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(diagnosis.RECEIPT_PATH.read_bytes())


def test_diagnosis_proves_anchor_for_share_rls_gap() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_anchor_for_share_policy_gap_proven_cleanup_verified"
    )
    assert result["parent_failure"]["mapped_sql_line"] == 1254
    assert result["diagnosis"]["lock_mode"] == "FOR_SHARE"
    assert result["diagnosis"]["anchor_lock_node_count"] == 5
    assert result["diagnosis"]["present_anchor_policy_ids"] == [
        "pol_cf_08_select",
        "pol_cf_08_insert",
    ]
    assert result["diagnosis"]["missing_lock_policy_id"] == (
        "pol_cf_08_update_lock"
    )
    assert result["bounded_repair"]["using_capabilities"] == [
        "COORDINATOR",
        "LIFECYCLE",
    ]
    assert result["bounded_repair"]["with_check_sql"].endswith(" AND FALSE")
    assert result["bounded_repair"]["append_only_invariant_unchanged"] is True
    assert result["bounded_repair"]["body_program_change"] is False
    assert result["bounded_repair"]["new_external_authority"] is False
