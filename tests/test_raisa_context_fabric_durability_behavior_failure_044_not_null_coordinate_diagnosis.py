from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / (
    "scripts/"
    "raisa_context_fabric_durability_behavior_failure_044_not_null_coordinate_diagnosis.py"
)
EVIDENCE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-044.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("failure_044_diagnosis", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_044_diagnosis_is_deterministic_and_bounded(tmp_path: Path) -> None:
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
    assert diagnosis["postgresql_failure_class_is_not_null_violation"]
    assert diagnosis["scenario_failure_coordinate_projection_exists"] is False
    assert diagnosis["persisted_relation_or_column_exists"] is False
    assert diagnosis["actual_null_column_determined"] is False
    assert diagnosis["database_body_defect_claimed"] is False
    assert diagnosis["additional_container_runs"] == 0


def test_failure_044_repair_is_telemetry_only_and_fails_closed() -> None:
    repair = _load_module().build_evidence()["bounded_repair"]
    assert repair["reuse_existing_header_and_diagnostic_parsers"]
    assert repair["persist_only_sqlstate_coordinate_status_relation_and_column"]
    assert repair["unlisted_relation_or_column_fails_closed"]
    assert repair["raw_stderr_remains_digest_only"]
    assert repair["database_body_contract_unchanged"]
    assert repair["inert_sql_and_parse_evidence_unchanged"]
    assert repair["behavior_contract_and_scenarios_unchanged"]
