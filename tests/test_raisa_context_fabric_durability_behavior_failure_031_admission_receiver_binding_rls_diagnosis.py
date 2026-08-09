from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_031_admission_receiver_binding_rls_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-031.json"
)


def test_failure_031_is_preserved_byte_identically() -> None:
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


def test_diagnosis_proves_receiver_visibility_gap_without_new_authority() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_admission_receiver_binding_rls_visibility_gap_proven_"
        "cleanup_verified"
    )
    observed = result["diagnosis"]
    assert observed["entry_point_owner"] == diagnosis.RECEIVER_ROLE
    assert observed["entry_point_owner_login"] is False
    assert observed["receiver_binding_select_granted"] is True
    assert observed["policy_current_user_allowlist"] == [
        "emr4_context_fabric.context_schema_owner"
    ]
    assert observed["required_current_user_missing"] == diagnosis.RECEIVER_ROLE
    assert observed["database_login_equals_session_user_retained"] is True
    assert observed["active_interval_fence_retained"] is True
    assert observed["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "policy_change": "allow_exact_nonlogin_owner_pair_while_retaining_session_bound_active_row_filter",
        "current_user_allowlist": [
            "emr4_context_fabric.context_schema_owner",
            diagnosis.RECEIVER_ROLE,
        ],
        "policy_roles_change": False,
        "direct_table_grant_change": False,
        "role_or_membership_change": False,
        "bypassrls_change": False,
        "body_program_change": False,
        "scenario_change": False,
        "new_authority": False,
    }
