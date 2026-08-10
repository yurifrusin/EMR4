from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis as diagnosis,
)


def test_failure_037_and_prior_mutable_restoration_anchor_are_preserved() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(failure_bytes).hexdigest() == diagnosis.EXPECTED_FAILURE_SHA256
    failure = json.loads(failure_bytes)
    anchor_bytes = diagnosis.RESTORED_MUTABLE_ANCHOR_PATH.read_bytes()
    assert hashlib.sha256(anchor_bytes).hexdigest() == (
        diagnosis.EXPECTED_RESTORED_MUTABLE_ANCHOR_SHA256
    )
    anchor = json.loads(anchor_bytes)
    assert anchor["parent_failure"]["internal_attempt_id"] == (
        diagnosis.EXPECTED_RESTORED_MUTABLE_ATTEMPT_ID
    )
    assert anchor["parent_failure"]["evidence_sha256"] == (
        "sha256:" + diagnosis.EXPECTED_RESTORED_MUTABLE_EVIDENCE_SHA256
    )
    assert anchor["parent_failure"]["internal_attempt_id"] != failure["attempt_id"]


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(diagnosis.RECEIPT_PATH.read_bytes())


def test_diagnosis_proves_admission_for_update_rls_gap() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_admission_for_update_policy_gap_proven_cleanup_verified"
    )
    assert result["parent_failure"]["mapped_sql_line"] == 1262
    assert result["diagnosis"]["lock_mode"] == "FOR_UPDATE"
    assert result["diagnosis"]["admission_lock_node_count"] == 3
    assert result["diagnosis"]["present_admission_policy_ids"] == [
        "pol_cf_04_select",
        "pol_cf_04_insert",
    ]
    assert result["diagnosis"]["missing_lock_policy_id"] == "pol_cf_04_update_lock"
    assert result["bounded_repair"]["using_capabilities"] == ["COORDINATOR"]
    assert result["bounded_repair"]["with_check_sql"].endswith(" AND FALSE")
    assert result["bounded_repair"]["append_only_invariant_unchanged"] is True
    assert result["bounded_repair"]["body_program_change"] is False
    assert result["bounded_repair"]["new_external_authority"] is False
