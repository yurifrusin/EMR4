from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-028.json"
)


def test_failure_028_is_preserved_byte_identically() -> None:
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


def test_diagnosis_proves_exact_dml_ambiguities_without_authority_change() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_dml_local_column_ambiguity_proven_cleanup_verified"
    )
    assert result["diagnosis"]["value_name_collisions"] == [
        "aggregate_revision",
        "source_contract_digest",
    ]
    assert result["diagnosis"]["returning_name_collisions"] == [
        "aggregate_revision",
        "source_contract_digest",
    ]
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "outer_block_label": "cf_body",
        "local_reference_rendering": "block_qualified",
        "dml_returning_rendering": "target_relation_qualified",
        "body_program_change": False,
        "scenario_change": False,
        "authority_change": False,
    }
