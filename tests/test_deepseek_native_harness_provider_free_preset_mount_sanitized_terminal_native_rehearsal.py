from __future__ import annotations

import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitized_terminal_native_rehearsal as subject,
)


def _head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=subject.REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def _sidecar(contract: dict, *, result: str) -> dict:
    private_reached = result in {
        "preset_mount_failure_attributed",
        "preset_composition_failure_attributed",
        "prepublication_veto_diagnosed",
    }
    success = result == "prepublication_veto_diagnosed"
    preset_mount = result == "preset_mount_failure_attributed"
    broader = result == "preset_composition_failure_attributed"
    return {
        "schema_version": subject.SIDECAR_SCHEMA,
        "operation_id": subject.OPERATION_ID,
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": _head(),
        "result": result,
        "last_admitted_stage": (
            "postrollback_registries_empty"
            if success
            else (
                "private_identity_admitted"
                if private_reached
                else "loader_ready"
            )
        ),
        "error_class": None if private_reached else "package_import_rejected",
        "safe_guard_coordinate": (
            "EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING" if broader else None
        ),
        "safe_guard_detail": None,
        "preset_mount_terminal": (
            {
                "stage": "preset_mount",
                "code": "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
                "detail": None,
            }
            if preset_mount
            else None
        ),
        "runner_sha256": contract["source_bindings"]["diagnostic_runner_sha256"],
        "effective_tool_guard_sha256": contract["source_bindings"][
            "effective_tool_guard_sha256"
        ],
        "preset_sha256": contract["preset"]["sha256"],
        "fixed_identity_sha256": subject.sha256_bytes(
            subject.PRIVATE_SESSION_ID.encode()
        ),
        "target_path_sha256": subject.sha256_bytes(subject.TARGET_PATH.encode()),
        "agent_create_invocation_count": 1 if private_reached else 0,
        "private_agent_preparation_count": 1 if private_reached else 0,
        "private_session_preparation_count": 1 if private_reached else 0,
        "live_agent_count": 0,
        "live_session_count": 0,
        "session_created_event_count": 0,
        "agent_created_event_count": 0,
        "agent_session_start_event_count": 0,
        "preset_mounted": success,
        "model_selection_installed": success,
        "veto_exact": success,
        "veto_rejected": success,
        "raw_error_retained": False,
        "target_created": False,
        "target_used": False,
        "turn_count": 0,
        "request_count": 0,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "occupied_worker_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
    }


def test_contract_and_exact_source_derivation_pass() -> None:
    contract = subject.load_contract()
    _, _, guard, _, bindings = subject.source_payloads(contract)
    runner = subject.runner_source()
    projection = subject.validate_runner_source(runner)
    assert bindings == contract["source_bindings"]
    assert subject.sha256_bytes(runner) == bindings["diagnostic_runner_sha256"]
    assert subject.sha256_bytes(guard) == bindings["effective_tool_guard_sha256"]
    assert all(projection["sanitized_terminal_checks"].values())


def test_deterministic_check_starts_no_native_process() -> None:
    result = subject.deterministic_check()
    expected_state = (
        "consumed" if all(path.exists() for path in subject.OUTPUT_PATHS) else "fresh"
    )
    assert result["artifact_state"] == expected_state
    assert result["native_process_count"] == (1 if expected_state == "consumed" else 0)


def test_runner_terminal_precedes_broader_composition_fallback() -> None:
    source = subject.runner_source().decode("utf-8")
    preset = source.index("error instanceof PresetMountSanitizedTerminalError")
    broader = source.index("sanitizeEffectiveToolTerminal(error)")
    assert preset < broader
    assert source.count('emit("preset_mount_failure_attributed", null)') == 1
    assert source.count('emit("preset_composition_failure_attributed", null)') == 1


def test_guard_imports_exact_materialized_modules() -> None:
    source = subject.guard_source().decode("utf-8")
    assert source.count(f'from "./{subject.BRIDGE_MATERIALIZED_NAME}"') == 1
    bridge = subject.BRIDGE_PATH.read_text(encoding="utf-8")
    assert bridge.count(f'from "./{subject.SANITIZER_MATERIALIZED_NAME}"') == 1


@pytest.mark.parametrize(
    "result",
    [
        "preset_mount_failure_attributed",
        "preset_composition_failure_attributed",
        "prepublication_veto_diagnosed",
        "closed_subcoordinate_failure",
    ],
)
def test_sidecar_is_enveloped_before_semantic_admission(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    result: str,
) -> None:
    contract = subject.load_contract()
    root = tmp_path / "disposable"
    root.mkdir()
    sidecar_path = root / "sidecar.json"
    sidecar = _sidecar(contract, result=result)
    sidecar_path.write_text(json.dumps(sidecar), encoding="utf-8")
    envelope_path = tmp_path / "outer-process-envelope.json"
    monkeypatch.setattr(subject, "PROCESS_ENVELOPE_PATH", envelope_path)
    observed = subject.read_sidecar(
        sidecar_path,
        disposable_root=root,
        contract=contract,
        candidate_source=_head(),
    )
    envelope = json.loads(envelope_path.read_bytes())
    assert observed == sidecar
    assert envelope["sidecar_file_seen"] is True
    assert envelope["sidecar_semantics_interpreted"] is False
    assert envelope["stream_content_retained"] is False
    assert envelope["sidecar_sha256"] == subject.sha256_bytes(
        sidecar_path.read_bytes()
    )


def test_process_envelope_schema_rejects_raw_material() -> None:
    schema = json.loads(subject.PROCESS_ENVELOPE_SCHEMA_PATH.read_bytes())
    envelope = {
        "schema_version": subject.PROCESS_ENVELOPE_SCHEMA,
        "operation_id": subject.OPERATION_ID,
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": _head(),
        "sidecar_file_seen": False,
        "sidecar_bytes": 0,
        "sidecar_sha256": None,
        "numeric_exit_code_observed": False,
        "numeric_exit_code": None,
        "stdout_retained": False,
        "stderr_retained": False,
        "raw_stream_read": False,
        "stream_content_retained": False,
        "sidecar_semantics_interpreted": False,
        "raw_runtime_detail_retained": False,
        "native_process_count": 1,
        "retry_count": 0,
        "resume_count": 0,
        "further_process_authorized": False,
    }
    jsonschema.Draft202012Validator(schema).validate(envelope)
    envelope["raw_message"] = "forbidden"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(envelope)


def test_envelope_persistence_precedes_schema_and_terminal_semantics() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    start = source.index("def read_sidecar(")
    end = source.index("def build_controller_terminal(")
    function = source[start:end]
    assert function.index("_persist_process_envelope(") < function.index(
        "Draft202012Validator(schema).validate(value)"
    )
    assert function.index("_persist_process_envelope(") < function.index(
        'result = value["result"]'
    )


@pytest.mark.parametrize(
    ("terminal", "exit_code"),
    [
        ("preset_mount_failure_attributed", 3),
        ("preset_composition_failure_attributed", 3),
        ("prepublication_veto_diagnosed", 0),
        ("closed_subcoordinate_failure", 2),
        ("runner_link_or_apply_absence", 2),
    ],
)
def test_controller_accepts_only_exact_terminal_exit_pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    terminal: str,
    exit_code: int,
) -> None:
    monkeypatch.setattr(subject, "PROCESS_ENVELOPE_PATH", tmp_path / "envelope.json")
    subject._persist_process_envelope(candidate_source=_head(), sidecar_payload=None)
    value = {
        "result": terminal,
        "factory_boundary": None,
    }
    assert (
        subject._controller_failure(
            process_started=True,
            exit_code=exit_code,
            readiness_valid=True,
            readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
            hmr_mutation_count=1,
            sidecar_file_seen=False,
            sidecar_valid=False,
            terminal=value,
            broker_zero=True,
            network_attempt_count=0,
            network_ledger_valid=True,
            bundle_unchanged=True,
            target_absent=True,
            process_absent=True,
            root_absent=True,
        )
        is None
    )
    assert subject._controller_failure(
        process_started=True,
        exit_code=99,
        readiness_valid=True,
        readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
        hmr_mutation_count=1,
        sidecar_file_seen=False,
        sidecar_valid=False,
        terminal=value,
        broker_zero=True,
        network_attempt_count=0,
        network_ledger_valid=True,
        bundle_unchanged=True,
        target_absent=True,
        process_absent=True,
        root_absent=True,
    ) == "PROCESS_EXIT_REJECTED"


def test_only_preset_mount_terminal_proves_new_bridge() -> None:
    base = {
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": _head(),
        "result": "pass",
    }
    for terminal in subject.TERMINALS:
        evidence = {
            **base,
            "controller_terminal": {
                "result": terminal,
                "preset_mount_terminal": None,
                "safe_guard_coordinate": None,
            },
        }
        reading = subject._efficacy(evidence)
        assert reading["new_bridge_runtime_path_proved"] is (
            terminal == "preset_mount_failure_attributed"
        )


def test_plan_and_threat_model_keep_process_and_authority_closed() -> None:
    text = " ".join((
        subject.PLAN_PATH.read_text(encoding="utf-8")
        + subject.THREAT_PATH.read_text(encoding="utf-8")
    ).lower().split())
    for token in (
        "exactly one",
        "zero turns",
        "model/provider request",
        "no retry",
        "content-free outer process envelope",
        "protected evidence",
    ):
        assert token in text


def test_preplanning_receipt_has_five_sources_and_three_lanes() -> None:
    path = (
        subject.REPO_ROOT
        / "orchestration"
        / "agent_inbox"
        / "codex"
        / "deepseek-native-harness-preset-mount-sanitized-terminal-native-rehearsal-preplanning-receipt.json"
    )
    receipt = json.loads(path.read_bytes())
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert len(receipt["parallelism_assessment"]["lanes"]) == 3
    assert all(
        lane["disposition"] == "declined"
        for lane in receipt["parallelism_assessment"]["lanes"]
    )


def test_no_execute_path_appears_in_deterministic_command_surface() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    check_start = source.index("def deterministic_check(")
    execute_start = source.index("def execute_rehearsal(")
    check_source = source[check_start:execute_start]
    assert "execute_rehearsal(" not in check_source
    assert "subprocess.Popen" not in check_source
