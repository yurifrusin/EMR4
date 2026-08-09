from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-034.json"
)


def test_failure_034_is_preserved_and_mutable_evidence_is_restored() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(failure_bytes).hexdigest() == (
        diagnosis.EXPECTED_FAILURE_SHA256
    )
    failure = json.loads(failure_bytes)
    mutable = (
        diagnosis.BEHAVIOR_DIR / "provider-free-behavior-transaction-evidence.json"
    )
    assert json.loads(mutable.read_bytes()).get("attempt_id") != failure.get(
        "attempt_id"
    )
    assert hashlib.sha256(mutable.read_bytes()).hexdigest() == (
        "09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b"
    )


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(RECEIPT.read_bytes())


def test_diagnosis_proves_row_shape_and_null_reload_contradictions() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_body_to_admission_check_contradiction_proven_cleanup_verified"
    )
    assert result["diagnosis"]["constraint"] == "ck_cf_04_02"
    assert result["diagnosis"]["null_equality_winners"] == (
        diagnosis.EXPECTED_NULL_EQ_WINNERS
    )
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "primary_row_shape": (
            "outcome_fields_present_attempted_digest_null_conflict_reason_null"
        ),
        "conflict_row_shape": (
            "outcome_fields_null_attempted_digest_present_conflict_reason_present"
        ),
        "null_reload_comparison": "is_null_for_typed_null_bindings",
        "body_program_change": True,
        "inert_artifact_regeneration": True,
        "parse_catalogue_rebind_required": True,
        "behavior_parent_rebind_required": True,
        "scenario_population_change": False,
        "principal_or_sqlstate_change": False,
        "authority_change": False,
    }
