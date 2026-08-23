import json
from pathlib import Path
import subprocess

import pytest
from pydantic import ValidationError

from orchestration_harness import historical_diary_local_measured_privacy_probe as probe
from scripts import historical_diary_authored_synthetic_word_coordinate_recovery as recovery


PLAN = Path(
    "docs/raisa-provider-free-authored-synthetic-historical-diary-word-coordinate-timeout-containment-throughput-recovery-plan.md"
)
THREAT = Path(
    "docs/security/raisa-provider-free-authored-synthetic-historical-diary-word-coordinate-timeout-containment-throughput-recovery-threat-model-delta.md"
)
CLEANUP_SCRIPT = Path("scripts/historical_diary_owned_word_cleanup.ps1")
EXTRACTOR = Path("scripts/historical_diary_local_measured_privacy_probe.ps1")


def _control_payload() -> dict[str, object]:
    return {
        "schema_version": "historical_diary.owned_word_process_control.v1",
        "process_id": 1234,
        "process_class": "WINWORD",
        "process_start_utc_ticks": 638600000000000000,
    }


def _cleanup_payload(*, passed: bool) -> bytes:
    return json.dumps(
        {
            "schema_version": "historical_diary.owned_word_cleanup_result.v1",
            "status": "passed" if passed else "blocked",
            "reason_code": "owned_process_removed" if passed else "owned_process_remains",
            "exact_owned_process_absent": passed,
            "broad_process_name_stop_used": False,
            "source_value_emitted": False,
        }
    ).encode()


def _timeout_runner(*_args, **_kwargs):
    raise subprocess.TimeoutExpired(cmd="synthetic", timeout=2)


def test_plan_freezes_two_synthetic_proofs_and_absolute_historical_denial():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "two local Word process proofs" in plan
    assert "at least 2,000 segment" in plan
    assert "at least 250 explicit story anchors" in plan
    assert "300-second ceiling" in plan
    assert "may not inspect or reuse any historical document" in plan
    assert "Broad process-name stopping" in threat


def test_owned_process_control_and_cleanup_models_are_strict_and_paired():
    assert probe.OwnedWordProcessControl.model_validate(_control_payload()).process_id == 1234
    invalid = _control_payload()
    invalid["process_class"] = "notepad"
    with pytest.raises(ValidationError):
        probe.OwnedWordProcessControl.model_validate(invalid)
    with pytest.raises(ValidationError, match="word_cleanup_disposition_invalid"):
        probe.OwnedWordCleanupResult(
            schema_version="historical_diary.owned_word_cleanup_result.v1",
            status="passed",
            reason_code="owned_process_remains",
            exact_owned_process_absent=False,
            broad_process_name_stop_used=False,
            source_value_emitted=False,
        )


def test_progress_schema_is_count_only_bounded_and_consistent():
    payload = {
        "schema_version": "historical_diary.word_extraction_progress.v1",
        "stage": "document_completed",
        "total_document_count": 12,
        "completed_document_count": 1,
        "table_cell_count": 14,
        "structural_segment_count": 168,
        "coordinate_attempt_count": 168,
        "explicit_story_anchor_count": 24,
        "elapsed_bucket": "under_30_seconds",
        "coordinate_rate_floor_bucket": "8_to_15_per_second",
        "source_value_emitted": False,
    }
    assert probe.WordExtractionProgress.model_validate(payload).table_cell_count == 14
    payload["coordinate_attempt_count"] = 169
    with pytest.raises(ValidationError, match="word_progress_coordinate_count_invalid"):
        probe.WordExtractionProgress.model_validate(payload)
    payload["coordinate_attempt_count"] = 168
    payload["raw_filename"] = "forbidden.docx"
    with pytest.raises(ValidationError):
        probe.WordExtractionProgress.model_validate(payload)


def test_missing_control_blocks_without_launching_cleanup(tmp_path):
    def forbidden_runner(*_args, **_kwargs):
        pytest.fail("cleanup process must not launch without a control identity")

    result = probe.cleanup_owned_word_process(
        control_path=tmp_path / "missing.json",
        receipt_path=tmp_path / "receipt.json",
        cleanup_script_path=CLEANUP_SCRIPT,
        runner=forbidden_runner,
    )

    assert result.reason_code == "control_file_absent"
    assert result.status == "blocked"
    assert result.exact_owned_process_absent is False

    safe_after_completed_child = probe.cleanup_owned_word_process(
        control_path=tmp_path / "missing.json",
        receipt_path=tmp_path / "completed-child-receipt.json",
        cleanup_script_path=CLEANUP_SCRIPT,
        runner=forbidden_runner,
        control_absence_is_safe=True,
    )
    assert safe_after_completed_child.status == "passed"
    assert safe_after_completed_child.exact_owned_process_absent is True


def test_invalid_control_blocks_without_process_name_fallback(tmp_path):
    control = tmp_path / "control.json"
    control.write_text('{"schema_version":"wrong"}', encoding="utf-8")
    result = probe.cleanup_owned_word_process(
        control_path=control,
        receipt_path=tmp_path / "receipt.json",
        cleanup_script_path=CLEANUP_SCRIPT,
    )

    assert result.status == "blocked"
    assert result.reason_code == "control_file_invalid"
    assert result.broad_process_name_stop_used is False


def test_timeout_is_typed_and_parent_cleanup_result_controls_disposition(tmp_path):
    control = tmp_path / "control.json"
    receipt = tmp_path / "receipt.json"
    control.write_text(json.dumps(_control_payload()), encoding="utf-8")

    def cleanup_runner(*_args, **_kwargs):
        return subprocess.CompletedProcess([], 0, stdout=_cleanup_payload(passed=True), stderr=b"")

    with pytest.raises(probe.ProbeError, match="^word_extractor_timeout$"):
        probe.run_owned_word_subprocess(
            ["synthetic"],
            timeout_seconds=2,
            control_path=control,
            cleanup_receipt_path=receipt,
            cleanup_script_path=CLEANUP_SCRIPT,
            runner=_timeout_runner,
            cleanup_runner=cleanup_runner,
        )
    assert json.loads(receipt.read_text())["exact_owned_process_absent"] is True


def test_timeout_cleanup_failure_is_distinct_and_blocking(tmp_path):
    control = tmp_path / "control.json"
    control.write_text(json.dumps(_control_payload()), encoding="utf-8")

    def cleanup_runner(*_args, **_kwargs):
        return subprocess.CompletedProcess([], 2, stdout=_cleanup_payload(passed=False), stderr=b"")

    with pytest.raises(probe.ProbeError, match="word_extractor_timeout_cleanup_failed"):
        probe.run_owned_word_subprocess(
            ["synthetic"],
            timeout_seconds=2,
            control_path=control,
            cleanup_receipt_path=tmp_path / "receipt.json",
            cleanup_script_path=CLEANUP_SCRIPT,
            runner=_timeout_runner,
            cleanup_runner=cleanup_runner,
        )


def test_abnormal_exit_invokes_exact_cleanup_but_success_does_not(tmp_path):
    control = tmp_path / "control.json"
    control.write_text(json.dumps(_control_payload()), encoding="utf-8")
    calls = 0

    def cleanup_runner(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess([], 0, stdout=_cleanup_payload(passed=True), stderr=b"")

    with pytest.raises(probe.ProbeError, match="^word_extractor_failed$"):
        probe.run_owned_word_subprocess(
            ["synthetic"],
            timeout_seconds=2,
            control_path=control,
            cleanup_receipt_path=tmp_path / "failed.json",
            cleanup_script_path=CLEANUP_SCRIPT,
            runner=lambda *_args, **_kwargs: subprocess.CompletedProcess(
                [], 1, stdout=b"", stderr=b""
            ),
            cleanup_runner=cleanup_runner,
        )
    assert calls == 1

    result = probe.run_owned_word_subprocess(
        ["synthetic"],
        timeout_seconds=2,
        control_path=control,
        cleanup_receipt_path=tmp_path / "passed.json",
        cleanup_script_path=CLEANUP_SCRIPT,
        runner=lambda *_args, **_kwargs: subprocess.CompletedProcess(
            [], 0, stdout=b"{}", stderr=b""
        ),
        cleanup_runner=lambda *_args, **_kwargs: pytest.fail(
            "cleanup must remain child-owned after success"
        ),
    )
    assert result.returncode == 0


def test_cleanup_script_has_exact_identity_stop_and_no_name_kill():
    source = CLEANUP_SCRIPT.read_text(encoding="utf-8")

    assert "Get-Process -Id $processId" in source
    assert "$process.StartTime.ToUniversalTime().Ticks" in source
    assert "Stop-Process -Id $processId" in source
    assert "Stop-Process -Name" not in source
    assert "Get-Process -Name" not in source
    assert "broad_process_name_stop_used = $false" in source


def test_extractor_profiles_bind_literal_control_progress_and_synthetic_roots():
    source = EXTRACTOR.read_text(encoding="utf-8")

    assert 'ValidateSet("HistoricalMeasuredProbe", "AuthoredSyntheticRecovery")' in source
    assert "local_data\\authored-synthetic-diary-word-coordinate-recovery\\run-v1" in source
    assert "Write-ClosedProgress -Stage \"document_completed\"" in source
    assert "process_start_utc_ticks" in source
    assert "historical_diary.word_extraction_progress.v1" in source


def test_synthetic_driver_has_exact_volume_and_no_historical_binding_import():
    assert recovery.DOCUMENT_COUNT == 12
    assert recovery.TABLE_ROWS * recovery.TABLE_COLUMNS * recovery.SEGMENTS_PER_CELL * 12 >= 2000
    assert recovery.STORY_ANCHORS_PER_DOCUMENT * recovery.DOCUMENT_COUNT >= 250
    assert "historical-diary-trove" not in recovery.RUN_ROOT.as_posix()
    source = Path(recovery.__file__).read_text(encoding="utf-8")
    assert "probe.BOUND_ROOT" not in source
    assert "timeout_seconds=300" in source
    assert '"historical_archive_enumerations": 0' in source


def test_first_use_gate_remains_closed_for_authored_synthetic_recovery():
    contract = json.loads(
        Path(
            "orchestration/continuity/raisa-local-only-historical-diary-document-story-time-coordinate-recovery-rehearsal/next-tranche-contract.json"
        ).read_text(encoding="utf-8")
    )

    assert contract["first_use_gate"] == {
        "status": "closed_pending_candidate_specific_evaluation",
        "opened_by_this_recovery": False,
        "applies_to_wholly_authored_synthetic_tests": False,
    }
    assert contract["authority_ceiling"]["new_historical_content_run"] is False
