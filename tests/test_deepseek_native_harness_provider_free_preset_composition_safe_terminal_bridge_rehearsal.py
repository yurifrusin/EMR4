from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_composition_safe_terminal_bridge_rehearsal as subject,
)


def _contract_projection() -> dict:
    return {
        "source_bindings": {
            "diagnostic_runner_sha256": "1" * 64,
            "effective_tool_guard_sha256": "2" * 64,
        },
        "preset": {"sha256": "3" * 64},
    }


def _sidecar(*, coordinate: str | None = None, detail: str | None = None) -> dict:
    return {
        "schema_version": subject.SIDECAR_SCHEMA,
        "operation_id": subject.OPERATION_ID,
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": "a" * 40,
        "result": "preset_composition_failure_attributed",
        "last_admitted_stage": "private_identity_admitted",
        "error_class": None,
        "safe_guard_coordinate": coordinate
        or "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
        "safe_guard_detail": detail,
        "runner_sha256": "1" * 64,
        "effective_tool_guard_sha256": "2" * 64,
        "preset_sha256": "3" * 64,
        "fixed_identity_sha256": subject.sha256_bytes(
            subject.PRIVATE_SESSION_ID.encode()
        ),
        "target_path_sha256": subject.sha256_bytes(subject.TARGET_PATH.encode()),
        "agent_create_invocation_count": 1,
        "private_agent_preparation_count": 1,
        "private_session_preparation_count": 1,
        "live_agent_count": 0,
        "live_session_count": 0,
        "session_created_event_count": 0,
        "agent_created_event_count": 0,
        "agent_session_start_event_count": 0,
        "preset_mounted": False,
        "model_selection_installed": False,
        "veto_exact": False,
        "veto_rejected": False,
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


def _read(tmp_path: Path, value: dict) -> dict:
    root = tmp_path.resolve()
    path = root / "safe-terminal.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return subject.read_sidecar(
        path,
        disposable_root=root,
        contract=_contract_projection(),
        candidate_source="a" * 40,
    )


def test_plan_and_threat_freeze_exact_safe_bridge() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    assert "Status: **frozen before implementation or execution**" in plan
    assert "sanitizeEffectiveToolTerminal" in plan
    assert "at most one distinct provider-free rc.7 process" in plan
    assert "Raw guard errors escape" in threat
    for coordinate in subject.SAFE_GUARD_COORDINATES:
        assert plan.count(f"`{coordinate}`") == 1


def test_closed_vocabularies_are_exact_and_finite() -> None:
    assert len(subject.STAGES) == 16
    assert len(subject.ERROR_CLASSES) == 21
    assert len(subject.SAFE_GUARD_COORDINATES) == 9
    assert len(set(subject.SAFE_GUARD_COORDINATES)) == 9
    assert subject.TERMINALS == [
        "closed_subcoordinate_failure",
        "preset_composition_failure_attributed",
        "prepublication_veto_diagnosed",
        "runner_link_or_apply_absence",
    ]


def test_runner_derives_from_accepted_source_and_admits_sanitizer_once() -> None:
    source = subject.runner_source()
    projection = subject.validate_runner_source(source)
    text = source.decode("utf-8")
    assert projection["safe_terminal_checks"]["sanitizer_called_once"]
    assert text.count('await import("./effective-tool-guard.mjs")') == 1
    assert text.count("sanitizeEffectiveToolTerminal(error)") == 1
    assert text.count('emit("preset_composition_failure_attributed", null)') == 1
    assert subject.PRIVATE_SESSION_ID in text
    assert subject._ACCEPTED_PRIVATE_SESSION_ID not in text


def test_runner_exposes_only_safe_coordinate_and_detail() -> None:
    text = subject.runner_source().decode("utf-8")
    assert text.count("safe_guard_coordinate") == 1
    assert text.count("safe_guard_detail") == 1
    for forbidden in (
        "error.stack",
        "error.cause",
        "String(error)",
        "error.prompt",
        "error.response",
    ):
        assert forbidden not in text
    for coordinate in subject.SAFE_GUARD_COORDINATES:
        assert text.count(json.dumps(coordinate)) == 1


def test_runner_preserves_one_factory_and_zero_drive_surface() -> None:
    text = subject.runner_source().decode("utf-8")
    assert text.count("await agents.create({") == 1
    assert text.count('openSync(path, "wx")') == 1
    for forbidden in (
        ".followup(",
        "createUserMessage",
        ".whenIdle(",
        'ctx.get("broker")',
        'ctx.get("models")',
        'ctx.get("providers")',
    ):
        assert forbidden not in text


def test_all_schemas_are_valid_and_closed_at_top_level() -> None:
    for path in (
        subject.CONTRACT_SCHEMA_PATH,
        subject.SIDECAR_SCHEMA_PATH,
        subject.EVIDENCE_SCHEMA_PATH,
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_attributed_sidecar_accepts_null_detail(tmp_path: Path) -> None:
    observed = _read(tmp_path, _sidecar())
    assert observed["result"] == "preset_composition_failure_attributed"
    assert observed["safe_guard_detail"] is None


def test_attributed_sidecar_accepts_sorted_safe_detail(tmp_path: Path) -> None:
    observed = _read(tmp_path, _sidecar(detail="edit,glob,read"))
    assert observed["safe_guard_detail"] == "edit,glob,read"


@pytest.mark.parametrize(
    "detail",
    ["read,edit", "edit,edit", "Edit", "edit,../read", "edit,,read"],
)
def test_attributed_sidecar_rejects_unsafe_detail(
    tmp_path: Path, detail: str
) -> None:
    with pytest.raises((subject.base.ClosedSubcoordinateError, jsonschema.ValidationError)):
        _read(tmp_path, _sidecar(detail=detail))


def test_sidecar_rejects_unknown_coordinate(tmp_path: Path) -> None:
    with pytest.raises(jsonschema.ValidationError):
        _read(tmp_path, _sidecar(coordinate="DESCRIPTIVE_FREE_FORM_FAILURE"))


def test_controller_absence_projects_no_factory_or_safe_coordinate() -> None:
    terminal = subject.build_controller_terminal(None)
    assert terminal == {
        "result": "runner_link_or_apply_absence",
        "last_admitted_stage": None,
        "error_class": None,
        "safe_guard_coordinate": None,
        "safe_guard_detail": None,
        "factory_boundary": None,
        "raw_runtime_detail_retained": False,
    }


def test_controller_accepts_attributed_exit_three() -> None:
    terminal = subject.build_controller_terminal(_sidecar())
    failure = subject._controller_failure(
        process_started=True,
        exit_code=3,
        readiness_valid=True,
        readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
        hmr_mutation_count=1,
        sidecar_file_seen=True,
        sidecar_valid=True,
        terminal=terminal,
        broker_zero=True,
        network_attempt_count=0,
        network_ledger_valid=True,
        bundle_unchanged=True,
        target_absent=True,
        process_absent=True,
        root_absent=True,
    )
    assert failure is None


def test_controller_rejects_attributed_exit_two() -> None:
    terminal = subject.build_controller_terminal(_sidecar())
    failure = subject._controller_failure(
        process_started=True,
        exit_code=2,
        readiness_valid=True,
        readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
        hmr_mutation_count=1,
        sidecar_file_seen=True,
        sidecar_valid=True,
        terminal=terminal,
        broker_zero=True,
        network_attempt_count=0,
        network_ledger_valid=True,
        bundle_unchanged=True,
        target_absent=True,
        process_absent=True,
        root_absent=True,
    )
    assert failure == "PROCESS_EXIT_REJECTED"


def test_report_timestamp_is_derived_from_typed_launch_time() -> None:
    evidence = {
        "launch": {
            "started_at_utc": "2026-08-21T18:00:00Z",
            "native_process_count": 1,
        },
        "controller_terminal": subject.build_controller_terminal(_sidecar()),
        "result": "pass",
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": "a" * 40,
        "provider_boundary": {"network_attempt_count": 0},
        "cleanup": {"process_absent": True, "disposable_root_absent": True},
    }
    report = subject._render_report(evidence)
    assert "Timestamp: 2026-08-22T04:00:00+10:00 (Australia/Brisbane)" in report


def test_deterministic_check_creates_no_native_process() -> None:
    result = subject.deterministic_check()
    assert result["native_process_count"] == 0
    assert result["verified_cached_package_count"] == 4
    assert result["runner"]["safe_terminal_checks"]["sanitizer_called_once"]
