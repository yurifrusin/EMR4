from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import pytest

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as startup_terminal
from scripts import (
    deepseek_native_harness_provider_free_structured_diagnostic_native_boot_observability_rehearsal
    as rehearsal,
)


CANDIDATE = "a61c558e14090935ded48c5c655eafc902ed89e0"


def _stream(payload: bytes = b"") -> dict[str, object]:
    return {
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "classification_bytes": payload,
        "limit_exceeded": False,
    }


def _structured_terminal() -> dict[str, object]:
    contract = rehearsal.load_contract()
    safe = rehearsal._expected_diagnostic(contract, CANDIDATE)
    return diagnostic.build_structured_pre_hmr_terminal(
        operation_id=rehearsal.OPERATION_ID,
        attempt_id=rehearsal.ATTEMPT_ID,
        candidate_source=CANDIDATE,
        native_process_started=True,
        exit_code=1,
        controller_coordinate="native_process_exited_nonzero",
        hmr_events=[],
        stdout=_stream(),
        stderr=_stream(b"authored local failure"),
        structured_diagnostic=safe,
    )


def test_contract_and_predecessors_validate_without_native_process() -> None:
    projection = rehearsal.deterministic_check(CANDIDATE)
    assert projection["native_process_count"] == 0
    assert projection["command"] == [
        "node.exe",
        "--expose-internals",
        "C:\\deterministic\\structured-diagnostic-native-boot\\entrypoint-wrapper.mjs",
        "--profile",
        "emr4-diagnostic-observability-missing",
    ]
    assert projection["wrapper"]["checks"]["canonical_json_serializer"] is True
    assert projection["predecessor"]["immutable_artifact_count"] == 7


def test_short_candidate_is_rejected_before_any_native_process() -> None:
    with pytest.raises(rehearsal.NativeBootObservabilityError) as caught:
        rehearsal.deterministic_check("a61c558")
    assert str(caught.value) == "candidate_source_invalid"


def test_expected_diagnostic_is_exact_closed_coordinate() -> None:
    value = rehearsal._expected_diagnostic(rehearsal.load_contract(), CANDIDATE)
    assert value["cause_chain"] == [
        {
            "position": 0,
            "error_kind": "error",
            "code_coordinate": "none",
            "config_stage": "none",
            "message_coordinate": "none",
            "aggregate_shape": "none",
        }
    ]
    assert value["raw_error_message_retained"] is False
    assert value["raw_stack_retained"] is False
    assert value["raw_paths_retained"] is False


def test_structured_terminal_exclusive_write_and_readback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence_root = tmp_path / "evidence"
    disposable_root = tmp_path / "disposable"
    evidence_root.mkdir()
    disposable_root.mkdir()
    monkeypatch.setattr(rehearsal, "CONTINUITY_ROOT", evidence_root)
    path = evidence_root / "terminal.json"
    terminal = _structured_terminal()
    digest = rehearsal._write_terminal_exclusive(
        path=path, terminal=terminal, disposable_root=disposable_root
    )
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert json.loads(path.read_bytes()) == terminal
    with pytest.raises(rehearsal.NativeBootObservabilityError):
        rehearsal._write_terminal_exclusive(
            path=path, terminal=terminal, disposable_root=disposable_root
        )


def test_terminal_inside_disposable_root_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    disposable_root = tmp_path / "disposable"
    disposable_root.mkdir()
    monkeypatch.setattr(rehearsal, "CONTINUITY_ROOT", disposable_root)
    with pytest.raises(rehearsal.NativeBootObservabilityError) as caught:
        rehearsal._write_terminal_exclusive(
            path=disposable_root / "terminal.json",
            terminal=_structured_terminal(),
            disposable_root=disposable_root,
        )
    assert str(caught.value) == "terminal_inside_disposable_root"


def test_v1_fallback_bytes_remain_supported() -> None:
    fallback = startup_terminal.build_pre_hmr_terminal(
        operation_id=rehearsal.OPERATION_ID,
        attempt_id=rehearsal.ATTEMPT_ID,
        candidate_source=CANDIDATE,
        native_process_started=True,
        exit_code=1,
        controller_coordinate="native_process_exited_nonzero",
        hmr_events=[],
        stdout=_stream(),
        stderr=_stream(b"unclassified authored local failure"),
    )
    payload = rehearsal._terminal_payload(fallback)
    assert json.loads(payload) == fallback
    assert fallback["schema_version"] == startup_terminal.SCHEMA_VERSION


def test_controller_source_has_one_process_and_fallback_before_cleanup() -> None:
    checks = rehearsal.validate_controller_source()
    assert all(checks.values())
    source = inspect.getsource(rehearsal.execute_boot)
    assert source.index("terminal = fallback") < source.index(
        "safe_diagnostic = diagnostic.read_structured_diagnostic("
    )
    assert source.index("terminal_digest = _write_terminal_exclusive(") < source.index(
        "shutil.rmtree(root)"
    )


def test_existing_output_refuses_before_deterministic_or_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence = tmp_path / "evidence.json"
    terminal = tmp_path / "terminal.json"
    report = tmp_path / "report.md"
    evidence.write_text("occupied", encoding="utf-8")
    monkeypatch.setattr(rehearsal, "EVIDENCE_PATH", evidence)
    monkeypatch.setattr(rehearsal, "TERMINAL_PATH", terminal)
    monkeypatch.setattr(rehearsal, "REPORT_PATH", report)
    monkeypatch.setattr(
        rehearsal,
        "deterministic_check",
        lambda *_: pytest.fail("deterministic check must not run after stale output"),
    )
    with pytest.raises(rehearsal.NativeBootObservabilityError) as caught:
        rehearsal.execute_boot(CANDIDATE)
    assert str(caught.value) == "canonical_attempt_output_already_exists"


def test_evidence_schema_accepts_only_closed_top_level_shape() -> None:
    schema = rehearsal._load_json(rehearsal.EVIDENCE_SCHEMA_PATH)
    assert schema["additionalProperties"] is False
    assert "structured_diagnostic" in schema["required"]
    assert "provider_boundary" in schema["required"]
    assert "cleanup" in schema["required"]
