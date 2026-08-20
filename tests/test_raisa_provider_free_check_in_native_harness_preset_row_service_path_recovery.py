from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    raisa_provider_free_check_in_native_harness_preset_row_service_path_recovery
    as recovery,
)


def test_contract_and_exact_retained_sources_pass() -> None:
    contract = recovery.load_contract()
    evidence = recovery.build_static_evidence(contract)

    assert evidence["result"] == "pass"
    assert evidence["shipped_roster"] == {
        "ids": recovery.SHIPPED_IDS,
        "emr4_present": False,
    }
    assert evidence["root_transformation"]["predecessor_effective_roots"] == [
        {"role": "shipped", "trust": "system"}
    ]
    assert evidence["root_transformation"]["corrected_effective_roots"] == [
        {"role": "shipped", "trust": "system"},
        {"role": "derived_user", "trust": "user"},
    ]
    assert set(evidence["source_checks"].values()) == {True}


def test_effective_root_roles_are_closed_and_ordered() -> None:
    assert recovery.effective_root_roles(False) == [
        {"role": "shipped", "trust": "system"}
    ]
    assert recovery.effective_root_roles(True) == [
        {"role": "shipped", "trust": "system"},
        {"role": "derived_user", "trust": "user"},
    ]


def test_package_runner_is_no_agent_and_provider_free() -> None:
    result = recovery.validate_runner_source(recovery.PACKAGE_RUNNER.encode("utf-8"))

    assert result["single_discovery_call"] is True
    assert result["no_agent_create"] is True
    assert result["no_preset_mount"] is True
    assert result["no_session_or_turn"] is True
    assert result["no_provider"] is True
    assert result["no_raw_error"] is True


def test_corrected_native_candidate_enables_only_derived_user_root() -> None:
    candidate = recovery.validate_native_candidate(
        Path("C:/emr4-service-path-native-candidate").resolve()
    )

    assert candidate["profile"]["include_user_root"] is True
    assert candidate["profile"]["runner_inject"] == ["agentPresets"]
    assert candidate["runner"]["single_service_list"] is True
    assert candidate["runner"]["exact_root_count"] is True
    assert candidate["runner"]["emr4_row_user_trust"] is True
    assert candidate["runner"]["no_agent_create"] is True
    assert candidate["runner"]["no_preset_mount"] is True


def test_native_stage_fails_before_process_without_checkpoint(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    missing = tmp_path / "missing-checkpoint.json"
    consumed = tmp_path / "consumed.json"
    terminal = tmp_path / "terminal.json"
    monkeypatch.setattr(recovery, "NATIVE_CHECKPOINT_PATH", missing)
    monkeypatch.setattr(recovery, "NATIVE_CONSUMED_PATH", consumed)
    monkeypatch.setattr(recovery, "NATIVE_TERMINAL_PATH", terminal)

    with pytest.raises(FileNotFoundError):
        recovery.execute_native_service_confirmation()

    assert not consumed.exists()
    assert not terminal.exists()


def test_native_terminal_schema_rejects_broadened_success() -> None:
    schema = json.loads(recovery.NATIVE_SCHEMA_PATH.read_text(encoding="utf-8"))
    terminal = {
        "schema_version": recovery.NATIVE_TERMINAL_SCHEMA,
        "operation_id": recovery.OPERATION_ID,
        "attempt_id": recovery.NATIVE_ATTEMPT_ID,
        "result": "pass",
        "terminal_coordinate": recovery.NATIVE_MARKERS[-1],
        "markers": recovery.NATIVE_MARKERS,
        "package": {
            "installation_id": "deepseek-check-in-attachment-observability-native-001",
            "name": "@deepseek-ai/dsh",
            "version": "0.1.0-rc.7",
            "package_lock_sha256": "a89defcd8a2c5aae4a54c03bda98e2585711fce881b4b08c90ca4808d45555f4",
        },
        "launch": {
            "duration_ms": 1,
            "exit_code": 0,
            "stdout_bytes": 0,
            "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "stderr_bytes": 0,
            "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "raw_logs_retained": False,
            "credential_environment_names_removed_count": 0,
        },
        "counts": {
            "native_processes": 1,
            "automatic_retries": 0,
            "agent_sessions": 0,
            "turns": 0,
            "broker_requests": 0,
            "model_requests": 0,
            "provider_requests": 0,
            "network_attempts": 0,
            "docker_invocations": 0,
            "database_invocations": 0,
        },
        "cleanup": {"process_absent": True, "disposable_root_absent": True},
        "runner_terminal_valid": True,
        "network_ledger_valid": True,
        "claim_boundary": "provider_disabled_native_preset_row_service_confirmation_only_no_agent_mount_deepseek_database_or_product_claim",
    }
    jsonschema.Draft202012Validator(schema).validate(terminal)

    broadened = copy.deepcopy(terminal)
    broadened["counts"]["agent_sessions"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(broadened)

    retried = copy.deepcopy(terminal)
    retried["counts"]["automatic_retries"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(retried)


def test_provider_free_service_input_fixture_passes() -> None:
    evidence = recovery.run_fixture_characterization(recovery.load_contract())

    assert evidence["result"] == "pass"
    assert evidence["process_boundary"] == {
        "package_only_node_processes": 1,
        "native_harness_processes": 0,
        "agent_sessions": 0,
        "turns": 0,
        "broker_requests": 0,
        "model_requests": 0,
        "provider_requests": 0,
        "network_attempts": 0,
        "docker_invocations": 0,
        "database_invocations": 0,
    }
    assert evidence["cleanup"] == {
        "package_process_absent": True,
        "disposable_root_absent": True,
    }
    corrected = evidence["scenarios"][1]
    assert corrected["decision"] == "accepted_exact_user_row"
    assert corrected["row"] == {
        "trust": "user",
        "source_role": "derived_user",
        "broken_absent": True,
        "bytes": recovery.PRESET_BYTES,
        "sha256": recovery.PRESET_SHA256,
    }
    assert evidence["scenarios"][3]["decision"] == "rejected_shadowed"
    assert evidence["native_process_checkpoint_admitted"] is False


def test_fixture_schema_rejects_broadened_or_mislabelled_evidence() -> None:
    evidence = recovery.run_fixture_characterization(recovery.load_contract())
    schema = json.loads(recovery.FIXTURE_SCHEMA_PATH.read_text(encoding="utf-8"))

    broadened = copy.deepcopy(evidence)
    broadened["provider_request"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(broadened)

    wrong_trust = copy.deepcopy(evidence)
    wrong_trust["scenarios"][1]["row"]["trust"] = "system"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(wrong_trust)

    native_started = copy.deepcopy(evidence)
    native_started["process_boundary"]["native_harness_processes"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(native_started)


def test_report_keeps_claim_boundary_narrow() -> None:
    report = recovery.render_report(
        recovery.run_fixture_characterization(recovery.load_contract())
    )

    assert "provider-free package/service-input evidence" in report
    assert "does not prove a\nnative Harness process" in report
    assert "does not prove" in report
    assert "DeepSeek request" in report


def test_cli_writes_schema_valid_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    static_path = tmp_path / "static.json"
    fixture_path = tmp_path / "fixture.json"
    report_path = tmp_path / "report.md"
    monkeypatch.setattr(recovery, "STATIC_EVIDENCE_PATH", static_path)
    monkeypatch.setattr(recovery, "FIXTURE_EVIDENCE_PATH", fixture_path)
    monkeypatch.setattr(recovery, "REPORT_PATH", report_path)
    monkeypatch.setattr("sys.argv", ["recovery", "--stage", "all"])

    assert recovery.main() == 0
    static = json.loads(static_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        json.loads(recovery.STATIC_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(static)
    jsonschema.Draft202012Validator(
        json.loads(recovery.FIXTURE_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(fixture)
    assert report_path.read_text(encoding="utf-8").startswith(
        "# Native Harness preset-row service-path fixture report"
    )
