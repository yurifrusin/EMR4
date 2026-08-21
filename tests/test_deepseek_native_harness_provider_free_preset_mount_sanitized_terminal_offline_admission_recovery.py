from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitized_terminal_offline_admission_recovery
    as recovery,
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sidecar(contract: dict[str, object]) -> dict[str, object]:
    hashes = contract["source_hashes"]
    terminal = contract["expected_terminal"]
    value: dict[str, object] = {
        "schema_version": contract["input_bindings"]["observed_sidecar_schema"],
        "operation_id": contract["consumed_operation_id"],
        "execution_attempt_id": contract["execution_attempt_id"],
        "candidate_source": contract["consumed_candidate_source"],
        "runner_sha256": hashes["runner_sha256"],
        "effective_tool_guard_sha256": hashes["effective_tool_guard_sha256"],
        "preset_sha256": hashes["preset_sha256"],
        "fixed_identity_sha256": hashes["fixed_identity_sha256"],
        "target_path_sha256": hashes["target_path_sha256"],
        **terminal,
        "preset_mounted": False,
        "model_selection_installed": False,
        "veto_exact": False,
        "veto_rejected": False,
        "agent_create_invocation_count": 1,
        "private_agent_preparation_count": 1,
        "private_session_preparation_count": 1,
        "target_created": False,
        "target_used": False,
        "raw_error_retained": False,
    }
    for key in contract["required_zero_fields"]:
        value[key] = 0
    return value


def test_contract_schema_is_valid_and_contract_passes() -> None:
    schema = _load(recovery.CONTRACT_SCHEMA_PATH)
    contract = _load(recovery.CONTRACT_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)


def test_retained_sidecar_schema_is_valid() -> None:
    schema = _load(recovery.SIDECAR_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)


def test_synthetic_observed_sidecar_passes_schema() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    schema = _load(recovery.SIDECAR_SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(_sidecar(contract))


def test_successor_schema_token_is_rejected_as_rewritten_history() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    value = _sidecar(contract)
    value["schema_version"] = contract["input_bindings"]["intended_sidecar_schema"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(_load(recovery.SIDECAR_SCHEMA_PATH)).validate(value)


def test_terminal_is_exact_broader_composition_failure() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    assert contract["expected_terminal"] == {
        "result": "preset_composition_failure_attributed",
        "last_admitted_stage": "private_identity_admitted",
        "error_class": None,
        "safe_guard_coordinate": "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED",
        "safe_guard_detail": None,
        "preset_mount_terminal": None,
    }


def test_only_preset_mount_failure_could_prove_new_bridge() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    assert contract["expected_terminal"]["result"] != "preset_mount_failure_attributed"


def test_admitted_projection_preserves_schema_mismatch() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    projection = recovery.admitted_projection(_sidecar(contract), contract)
    assert projection["observed_schema_version"] != projection["intended_schema_version"]
    assert projection["schema_token_mismatch_preserved"] is True
    assert projection["retry_authorized"] is False


def test_admitted_projection_has_only_closed_fields() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    projection = recovery.admitted_projection(_sidecar(contract), contract)
    jsonschema.Draft202012Validator(_load(recovery.ADMITTED_SCHEMA_PATH)).validate(projection)
    serialized = recovery._canonical(projection)
    for forbidden in (b"stack", b"message", b"credential", b"stdout", b"stderr"):
        assert forbidden not in serialized


def test_required_recovery_process_budget_is_zero() -> None:
    budget = _load(recovery.CONTRACT_PATH)["recovery_process_budget"]
    assert set(budget.values()) == {0}


def test_controller_has_no_native_process_launch_api() -> None:
    source = Path(recovery.__file__).read_text(encoding="utf-8")
    assert "subprocess.Popen" not in source
    assert "--execute" not in source.split("def _owned_node_process_count", 1)[1].split("def _bundle_root", 1)[0]


def test_exact_cleanup_requires_one_prefix_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    contract = _load(recovery.CONTRACT_PATH)
    monkeypatch.setattr(recovery, "disposable_parent", lambda: tmp_path.resolve())
    with pytest.raises(recovery.OfflineRecoveryError, match="retained_root_inventory_mismatch"):
        recovery.find_retained_root(contract)
    root = tmp_path / f"{contract['retained_layout']['root_prefix']}fixture"
    root.mkdir()
    assert recovery.find_retained_root(contract) == root.resolve()


def test_root_escape_or_symlink_is_not_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    contract = _load(recovery.CONTRACT_PATH)
    monkeypatch.setattr(recovery, "disposable_parent", lambda: tmp_path.resolve())
    target = tmp_path / "elsewhere"
    target.mkdir()
    link = tmp_path / f"{contract['retained_layout']['root_prefix']}link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink unavailable")
    with pytest.raises(recovery.OfflineRecoveryError, match="retained_root_boundary_rejected"):
        recovery.find_retained_root(contract)


def test_build_evidence_marks_unavailable_launch_fields() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    projection = recovery.admitted_projection(_sidecar(contract), contract)
    evidence = recovery.build_evidence(
        contract=contract,
        recovery_candidate="a" * 40,
        projection=projection,
        context={"readiness_events": contract["expected_readiness"], "network_attempt_count": 0},
        root_absent=True,
    )
    assert set(evidence["unavailable_launch_observations"].values()) == {False}
    assert evidence["new_bridge_runtime_path_proved"] is False
    assert evidence["claim_boundary"]["native_attempt_passed"] is False


def test_report_states_recovered_not_passed_native_attempt() -> None:
    contract = _load(recovery.CONTRACT_PATH)
    projection = recovery.admitted_projection(_sidecar(contract), contract)
    evidence = recovery.build_evidence(
        contract=contract,
        recovery_candidate="b" * 40,
        projection=projection,
        context={},
        root_absent=True,
    )
    report = recovery.render_report(evidence, "2026-08-22T00:00:00+10:00")
    assert "recovered finite terminal" in report
    assert "does **not** prove the new preset-mount bridge runtime path" in report
    assert "No retry" in report


def test_plans_freeze_zero_process_no_retry_boundary() -> None:
    text = recovery.PLAN_PATH.read_text(encoding="utf-8")
    threat = recovery.THREAT_PATH.read_text(encoding="utf-8")
    assert "entirely offline" in text
    assert "No retry or resume is" in text
    assert "launches no" in threat and "provider process" in threat
