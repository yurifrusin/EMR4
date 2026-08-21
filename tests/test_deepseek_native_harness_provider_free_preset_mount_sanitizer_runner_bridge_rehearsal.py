from __future__ import annotations

import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitizer_runner_bridge_rehearsal
    as subject,
)


def test_contract_and_deterministic_check_pass_without_outputs() -> None:
    contract = subject.load_contract()
    assert contract["closed_codes"] == subject.EXPECTED_CODES
    assert contract["execution"] == {
        "attempt_id": "attempt-001",
        "pure_node_fixture_process_count": 1,
        "native_harness_process_count": 0,
        "automatic_retry": False,
        "manual_retry": False,
    }
    reading = subject.deterministic_check()
    assert reading["status"] == "passed"
    expected_state = (
        "accepted" if all(path.is_file() for path in subject.OUTPUT_PATHS) else "fresh"
    )
    assert reading["artifact_state"] == expected_state
    assert reading["bridge_check_count"] == 13
    assert reading["native_harness_process_count"] == 0
    assert reading["dsh_import_count"] == 0
    if expected_state == "accepted":
        assert reading["node_process_count"] == 1
        assert reading["runner_bridge_deterministically_admitted"] is True


def test_source_derivation_is_exact_hash_bound_and_deterministic() -> None:
    contract = subject.load_contract()
    first = subject.validate_source_derivation(contract)
    second = subject.validate_source_derivation(contract)
    assert first == second
    assert first["source_sha256"] == contract["source_sha256"]
    assert all(first["bridge_checks"].values())
    assert subject.sha256_bytes(subject.build_runner_source()) == contract[
        "source_sha256"
    ]["derived_runner_sha256"]
    assert subject.sha256_bytes(subject.build_guard_source()) == contract[
        "source_sha256"
    ]["derived_guard_sha256"]


def test_pure_bridge_has_one_exact_mount_boundary_and_no_dynamic_projection() -> None:
    source = subject.BRIDGE_PATH.read_text(encoding="utf-8")
    assert source.count("sanitizePresetMountError(") == 1
    assert source.count("await mount(agentCtx, presetId)") == 1
    assert source.count(
        'from "./deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs"'
    ) == 1
    assert 'JSON.stringify(["stage", "code", "detail"])' in source
    for token in (
        "error.stack",
        "error.cause",
        "String(error)",
        "error.path",
        "error.prompt",
        "error.response",
        "process.env",
    ):
        assert token not in source


def test_derived_guard_uses_bridge_instead_of_broad_mount_catch() -> None:
    source = subject.build_guard_source().decode("utf-8")
    assert source.count(
        'import { mountWithSanitizedTerminal } from "./preset-mount-sanitizer-runner-bridge.mjs";'
    ) == 1
    assert source.count("await mountWithSanitizedTerminal(") == 1
    assert source.count(
        "agentCtx.agentPresets.mount.bind(agentCtx.agentPresets)"
    ) == 1
    assert "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED" in source
    assert 'fail("EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED")' not in source
    assert source.count("PresetMountSanitizedTerminalError") == 3


def test_derived_runner_gives_preset_terminal_precedence_over_broad_fallback() -> None:
    source = subject.build_runner_source().decode("utf-8")
    preset = source.index("error instanceof PresetMountSanitizedTerminalError")
    broad = source.index("sanitizeEffectiveToolTerminal(error)")
    assert preset < broad
    assert source.count('emit("preset_mount_failure_attributed", null)') == 1
    assert source.count('emit("preset_composition_failure_attributed", null)') == 1
    assert source.count("preset_mount_terminal: observed.presetMountTerminal") == 1
    assert source.count("safe_guard_coordinate: observed.safeGuardCoordinate") == 1


def test_fixture_is_provider_free_and_has_exact_closed_scenario_order() -> None:
    source = subject.FIXTURE_PATH.read_text(encoding="utf-8")
    assert "@deepseek-ai/" not in source
    assert "process.env" not in source
    assert "node:" not in source
    assert [row["scenario"] for row in subject.EXPECTED_RESULTS] == [
        "success",
        "agent_scope_absent",
        "composition_stamp_unreadable",
        "row_import_or_apply_rejected",
        "subtree_publication_absent",
        "row_inactive_after_await",
        "root_service_leak",
        "unclassified",
    ]
    assert {
        row["terminal"]["code"]
        for row in subject.EXPECTED_RESULTS
        if row["terminal"] is not None
    } == set(subject.EXPECTED_CODES)


def test_run_fixture_once_projects_five_keys_and_writes_envelope_before_admission(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    envelope_path = tmp_path / "attempt-001-process-envelope.json"
    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps(subject.EXPECTED_RESULTS) + "\n",
            stderr="",
        )

    monkeypatch.setattr(subject, "PROCESS_ENVELOPE_PATH", envelope_path)
    monkeypatch.setattr(
        subject.accepted_sanitizer,
        "_resolved_node_executable",
        lambda: Path("C:/fixture/node.exe"),
    )
    projected = {
        "SystemRoot": "fixture-system",
        "WINDIR": "fixture-windir",
        "ComSpec": "fixture-comspec",
        "TEMP": "fixture-temp",
        "TMP": "fixture-tmp",
    }
    monkeypatch.setattr(
        subject.accepted_sanitizer,
        "minimum_windows_environment",
        lambda: projected,
    )
    monkeypatch.setattr(subject.subprocess, "run", fake_run)

    results, envelope = subject.run_fixture_once("a" * 40)

    assert results == subject.EXPECTED_RESULTS
    assert len(calls) == 1
    assert calls[0][1]["env"] == projected
    assert set(calls[0][1]["env"]) == {
        "SystemRoot",
        "WINDIR",
        "ComSpec",
        "TEMP",
        "TMP",
    }
    assert envelope["node_process_count"] == 1
    assert envelope["native_harness_process_count"] == 0
    assert envelope["dsh_import_count"] == 0
    assert envelope["further_process_authorized"] is False
    assert envelope_path.is_file()


def test_process_envelope_and_evidence_schemas_reject_dynamic_detail() -> None:
    contract = subject.load_contract()
    derivation = subject.validate_source_derivation(contract)
    envelope = subject.build_process_envelope(
        candidate_source="b" * 40,
        returncode=0,
        stdout=json.dumps(subject.EXPECTED_RESULTS) + "\n",
        stderr="",
    )
    evidence = subject.build_evidence(
        candidate_source="b" * 40,
        contract=contract,
        derivation=derivation,
        results=subject.EXPECTED_RESULTS,
        envelope=envelope,
    )
    subject.validate_evidence(evidence)

    invalid = json.loads(json.dumps(evidence))
    invalid["fixture_results"][1]["terminal"]["detail"] = "raw detail"
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(invalid)


def test_execution_path_contains_one_node_fixture_subprocess_call() -> None:
    source = inspect.getsource(subject.run_fixture_once)
    assert source.count("subprocess.run(") == 1
    assert "native" not in source.lower()
    assert "dsh" not in source.lower()


def test_plan_and_threat_freeze_no_native_harness_process() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    assert "No DSH import and no native Harness process are authorised" in normalized
    assert "exact process count frozen before execution" in normalized
    assert "no native Harness process" in threat
    assert "No native Harness execution" in normalized
