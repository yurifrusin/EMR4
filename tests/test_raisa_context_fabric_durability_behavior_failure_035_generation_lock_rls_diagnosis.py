from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_035_generation_lock_rls_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-035.json"
)


def test_failure_035_is_preserved_and_mutable_evidence_is_restored() -> None:
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
        assert json.loads(mutable_bytes).get("attempt_id") != failure.get("attempt_id")
        assert hashlib.sha256(mutable_bytes).hexdigest() == (
            "09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b"
        )


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(RECEIPT.read_bytes())


def test_diagnosis_proves_coordinator_generation_rls_mismatch() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_coordinator_generation_update_policy_mismatch_proven_cleanup_verified"
    )
    assert result["diagnosis"]["lock_mode"] == "FOR_UPDATE"
    assert result["diagnosis"]["policy_using_capabilities"] == ["LIFECYCLE"]
    assert result["diagnosis"]["coordinator_generation_update_node_count"] == 10
    assert result["diagnosis"]["coordinator_direct_table_dml"] == []
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "generation_update_policy_using_capabilities": [
            "COORDINATOR",
            "LIFECYCLE",
        ],
        "generation_update_policy_with_check_capabilities": [
            "COORDINATOR",
            "LIFECYCLE",
        ],
        "coordinator_direct_table_dml_remains_empty": True,
        "entry_point_execute_grant_unchanged": True,
        "body_program_change": False,
        "inert_artifact_regeneration": True,
        "parse_catalogue_rebind_required": True,
        "behavior_parent_rebind_required": True,
        "scenario_population_change": False,
        "principal_or_sqlstate_change": False,
        "new_external_authority": False,
    }
