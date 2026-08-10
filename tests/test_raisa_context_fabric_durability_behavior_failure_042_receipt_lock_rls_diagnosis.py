from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / (
    "scripts/"
    "raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py"
)
EVIDENCE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-042.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("failure_042_diagnosis", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_042_diagnosis_is_deterministic_and_bounded(tmp_path: Path) -> None:
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

    assert expected["parent_failure"]["function_line"] == 210
    assert expected["parent_failure"]["mapped_sql_line"] == 1171
    assert expected["diagnosis"]["lock_mode"] == "FOR_UPDATE"
    assert expected["diagnosis"]["missing_lock_policy_id"] == ("pol_cf_09_update_lock")
    assert expected["diagnosis"]["additional_container_runs"] == 0


def test_failure_042_repair_preserves_append_only_and_authority_boundaries() -> None:
    module = _load_module()
    repair = module.build_evidence()["bounded_repair"]
    assert repair["using_capabilities"] == ["COORDINATOR"]
    assert repair["with_check_sql"].endswith(" AND FALSE")
    assert repair["coordinator_direct_table_dml_remains_empty"]
    assert repair["append_only_invariant_unchanged"]
    assert repair["entry_point_execute_grants_unchanged"]
    assert repair["body_program_change"] is False
    assert repair["scenario_population_change"] is False
    assert repair["new_external_authority"] is False


def test_failure_042_diagnosis_allows_clean_checkout_without_mutable_alias(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "MUTABLE_PATH", tmp_path / "absent-mutable.json")
    assert module.build_evidence()["parent_failure"]["run_sequence"] == 42


def test_failure_042_diagnosis_rejects_wrong_mutable_alias_when_present(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_module()
    mutable = tmp_path / "wrong-mutable.json"
    mutable.write_bytes(b"wrong\n")
    monkeypatch.setattr(module, "MUTABLE_PATH", mutable)
    with pytest.raises(RuntimeError, match="protected_mutable_evidence_not_restored"):
        module.build_evidence()
