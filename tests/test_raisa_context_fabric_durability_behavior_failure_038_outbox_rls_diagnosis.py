from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_038_outbox_rls_diagnosis as diagnosis,
)


def test_failure_038_is_immutable_and_cleanup_verified() -> None:
    failure_bytes = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(failure_bytes).hexdigest() == diagnosis.EXPECTED_FAILURE_SHA256
    failure = json.loads(failure_bytes)
    assert failure["attempt_id"] == "2171447fafa976485041ae03"
    assert failure["cleanup"] == {
        "absence_verified": True,
        "container_id": "cfe41d7cc96fd2d9d007a3b02164157aeeb91af3caf4323dde3761551959f20a",
        "removed": True,
        "status": "cleanup_verified",
    }


def test_diagnosis_is_deterministic_and_matches_receipt() -> None:
    assert diagnosis.diagnose() == json.loads(diagnosis.RECEIPT_PATH.read_bytes())


def test_diagnosis_proves_coordinator_outbox_select_policy_gap() -> None:
    result = diagnosis.diagnose()
    assert result["status"] == (
        "deterministic_coordinator_outbox_select_policy_gap_proven_cleanup_verified"
    )
    assert result["parent_failure"]["scenario_id"] == "BTR-E04"
    assert result["parent_failure"]["changed_relation"] == (
        "emr4_context_fabric.context_observer_generation"
    )
    assert result["diagnosis"]["forced_rls_relation"] == (
        "emr4_context_fabric.diary_context_observation_outbox_v1"
    )
    assert result["diagnosis"]["present_select_capabilities"] == [
        "PRODUCER",
        "OBSERVER",
        "RETENTION",
    ]
    assert result["diagnosis"]["missing_required_capability"] == "COORDINATOR"
    assert result["diagnosis"]["resulting_transition_kind"] == "REBASE_APPLIED"
    assert result["bounded_repair"]["repaired_capabilities"] == [
        "PRODUCER",
        "OBSERVER",
        "COORDINATOR",
        "RETENTION",
    ]
    assert result["bounded_repair"]["direct_relation_grants_unchanged"] is True
    assert result["bounded_repair"]["function_body_semantics_unchanged"] is True
    assert result["bounded_repair"]["new_external_authority"] is False
