from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / (
    "scripts/"
    "raisa_context_fabric_durability_behavior_failure_043_missing_source_sqlstate_diagnosis.py"
)
EVIDENCE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-043.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("failure_043_diagnosis", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_043_diagnosis_is_deterministic_and_bounded(tmp_path: Path) -> None:
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

    diagnosis = expected["diagnosis"]
    assert diagnosis["deterministic_observed_sqlstate_for_missing_row"] == "CF004"
    assert diagnosis["actual_sqlstate_not_persisted_by_parent_harness"]
    assert diagnosis["behavior_contract_expected_failure_mismatch"]
    assert diagnosis["database_body_defect_indicated"] is False
    assert diagnosis["additional_container_runs"] == 0


def test_failure_043_repair_preserves_database_parents_and_population() -> None:
    repair = _load_module().build_evidence()["bounded_repair"]
    assert repair["btr_e06_expected_failure_id"] == "F_CARDINALITY"
    assert repair["btr_e06_expected_sqlstate"] == "CF004"
    assert repair["persist_scenario_and_expected_observed_sqlstates_on_future_mismatch"]
    assert repair["database_body_contract_unchanged"]
    assert repair["inert_sql_and_parse_evidence_unchanged"]
    assert repair["scenario_population_and_order_unchanged"]
