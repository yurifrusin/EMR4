from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis as diagnosis,
)


RECEIPT = (
    diagnosis.BEHAVIOR_DIR
    / "provider-free-behavior-transaction-diagnosis-evidence-033.json"
)


def test_failure_033_is_preserved_byte_identically() -> None:
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


def test_diagnosis_proves_exact_fixture_body_contradiction_without_weakening() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_fixture_to_body_source_membership_contradiction_"
        "proven_cleanup_verified"
    )
    assert result["diagnosis"]["accepted_body_source_fields"] == (
        diagnosis.EXPECTED_SOURCE_FIELDS
    )
    assert result["diagnosis"]["additional_container_runs"] == 0
    assert result["bounded_repair"] == {
        "packet_value": "canonical_digest_of_complete_same_locator_outbox_row",
        "readback": (
            "admission_digest_equals_independent_same_locator_full_row_recomputation"
        ),
        "contract_and_schema_rule_change": True,
        "plan_and_design_correction": True,
        "body_program_change": False,
        "inert_artifact_change": False,
        "scenario_population_change": False,
        "principal_or_sqlstate_change": False,
        "authority_change": False,
    }
