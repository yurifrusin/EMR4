from __future__ import annotations

import hashlib
import json

from scripts import (
    raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis as diagnosis,
)


def test_failure_039_is_immutable_bounded_and_cleanup_verified() -> None:
    raw = diagnosis.FAILURE_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == diagnosis.EXPECTED_FAILURE_SHA256
    evidence = json.loads(raw)
    assert evidence["attempt_id"] == "5dcf0e6427694521e3a2ca26"
    assert evidence["environment"]["failure"] == {
        "stage": "readback",
        "code": "scenario_probe",
        "detail_digest": (
            "sha256:4071f7a2ec359e5bd9783c5f9909ca0d1898b2d09ce7656dc037b1f41b4b4427"
        ),
    }
    assert evidence["cleanup"]["absence_verified"] is True
    assert evidence["cleanup"]["removed"] is True
    assert evidence["scenario_reconciliation"] == {
        "expected": 20,
        "observed": 0,
        "passed": 0,
    }


def test_failure_039_diagnosis_is_exact_and_runs_no_container() -> None:
    expected = json.loads(diagnosis.DIAGNOSIS_PATH.read_text(encoding="utf-8"))
    observed = diagnosis.diagnose()
    assert observed == expected
    assert observed["parent_failure"]["scenario_id"] == "BTR-E04"
    assert observed["diagnosis"] == {
        "additional_container_runs": 0,
        "scenario_recovered_from_bounded_digest": True,
        "transition_result_marker_admitted_before_probe": True,
        "relation_delta_admitted_before_probe": True,
        "probe_count": 7,
        "failed_probe_index_released": False,
        "raw_postgresql_values_persisted": False,
    }
    assert observed["bounded_repair"]["database_artifact_unchanged"] is True
    assert observed["bounded_repair"]["allowed_digest_changes_unchanged"] is True
