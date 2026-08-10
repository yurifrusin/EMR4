from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / (
    "scripts/"
    "raisa_context_fabric_durability_behavior_failure_040_obligation_scope_diagnosis.py"
)
EVIDENCE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-040.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("failure_040_diagnosis", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_failure_040_diagnosis_is_deterministic_and_value_free(tmp_path: Path) -> None:
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

    assert expected["parent_failure"]["failed_probe_indexes"] == [5]
    assert expected["diagnosis"]["probe_semantic"] == (
        "one_pending_reassembly_obligation"
    )
    assert expected["diagnosis"]["logical_matching_rows"] == 2
    assert expected["diagnosis"]["database_body_defect_indicated"] is False
    assert expected["diagnosis"]["additional_container_runs"] == 0
    assert expected["diagnosis"]["raw_postgresql_values_persisted"] is False
    assert all("raw" not in key for key in expected["parent_failure"])


def test_failure_040_repair_changes_only_obligation_probe_scope() -> None:
    module = _load_module()
    evidence = module.build_evidence()
    repair = evidence["bounded_repair"]

    assert repair == {
        "allowed_digest_changes_unchanged": True,
        "behavior_contract_unchanged": True,
        "database_artifact_unchanged": True,
        "fresh_exact_head_veto_before_characterization": True,
        "next_run_must_be_single_owned_disposable_attempt": True,
        "scenario_population_unchanged": True,
        "scope_btr_e04_and_i03_obligation_probes_to_practice_alpha": True,
        "scope_btr_e04_and_i03_obligation_probes_to_stream_alpha": True,
    }
