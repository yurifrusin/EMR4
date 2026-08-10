from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / (
    "scripts/"
    "raisa_context_fabric_durability_behavior_failure_041_rejection_precedence_diagnosis.py"
)
EVIDENCE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-041.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("failure_041_diagnosis", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_041_diagnosis_is_deterministic_and_bounded(tmp_path: Path) -> None:
    module = _load_module()
    expected = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert module.build_evidence() == expected

    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    module.write_json_lf(first, expected)
    module.write_json_lf(second, module.build_evidence())
    assert first.read_bytes() == second.read_bytes()
    assert first.read_bytes().endswith(b"\n")
    assert b"\r\n" not in first.read_bytes()

    assert expected["parent_failure"]["scenario_id"] == "BTR-I03"
    assert expected["diagnosis"][
        "parent_called_marker_parser_before_rejection_classifier"
    ]
    assert expected["diagnosis"]["underlying_psql_outcome_not_persisted"]
    assert expected["diagnosis"]["database_body_defect_indicated"] is False
    assert expected["diagnosis"]["additional_container_runs"] == 0
    assert expected["diagnosis"]["raw_stderr_persisted"] is False


def test_failure_041_repair_retains_marker_gate_after_transport_admission() -> None:
    module = _load_module()
    repair = module.build_evidence()["bounded_repair"]
    assert repair["classify_unexpected_rejection_before_success_marker"]
    assert repair["classify_sqlstate_mismatch_before_expected_failure_marker"]
    assert repair["retain_marker_requirement_after_transport_admission"]
    assert repair["database_artifact_unchanged"]
    assert repair["behavior_contract_unchanged"]
    assert repair["scenario_population_unchanged"]
