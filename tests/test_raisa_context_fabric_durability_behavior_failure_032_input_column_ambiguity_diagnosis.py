from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_032_input_column_ambiguity_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-032.json"
)


def test_failure_032_is_preserved_byte_identically() -> None:
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


def test_diagnosis_proves_exact_input_column_ambiguities_without_authority_change() -> (
    None
):
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_select_input_column_ambiguity_proven_cleanup_verified"
    )
    assert result["diagnosis"]["collision_nodes"] == diagnosis.EXPECTED_COLLISION_NODES
    assert result["diagnosis"]["artifact_body_predicate_lines"] == {
        "36": 1,
        "39": 1,
        "42": 1,
    }
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "input_parameter_physical_prefix": "cf_arg_",
        "input_reference_rendering": "same_prefixed_physical_parameter",
        "support_function_input_change": False,
        "body_program_change": False,
        "scenario_change": False,
        "authority_change": False,
    }
