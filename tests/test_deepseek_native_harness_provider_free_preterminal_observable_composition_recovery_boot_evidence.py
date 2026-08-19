from __future__ import annotations

import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from scripts.deepseek_native_harness_provider_free_preterminal_observable_composition_recovery_boot import (
    EVIDENCE_PATH,
    EVIDENCE_SCHEMA_PATH,
    REPORT_PATH,
    RecoveryBootError,
    execute_boot,
)


def _evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def test_consumed_attempt_is_schema_valid_and_distinct() -> None:
    evidence = _evidence()
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))

    jsonschema.validate(evidence, schema)
    assert evidence["attempt_id"] == (
        "preterminal-observable-composition-recovery-boot-attempt-001"
    )
    assert evidence["attempt_id"] != "native-composition-attempt-001"
    assert evidence["result"] == "fail"
    assert evidence["failure_classification"] == "SERVICES_UNAVAILABLE"


def test_consumed_attempt_has_exact_bounded_terminal_and_reliable_timing() -> None:
    evidence = _evidence()

    assert evidence["readiness"] == {
        "events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "ledger_valid": True,
        "exact_expected_order": True,
        "writer": "provider-free-effective-tool-hmr-sentinel",
    }
    assert evidence["activation"]["coordinates"] == [
        "BOOTSTRAP_APPLY_ENTERED",
        "SERVICES_UNAVAILABLE",
        "EXIT_REQUESTED",
    ]
    assert evidence["terminal"]["code"] == "SERVICES_UNAVAILABLE"
    assert evidence["terminal"]["effective_tool_names"] == []
    assert evidence["launch"]["duration_ms"] > 0
    assert evidence["launch"]["duration_source"] == (
        "finally_before_termination_and_cleanup"
    )
    assert evidence["launch"]["exit_code"] == 2


def test_consumed_attempt_has_one_process_zero_retry_and_zero_prohibited_calls() -> (
    None
):
    evidence = _evidence()

    assert evidence["launch"]["native_process_count"] == 1
    assert evidence["launch"]["retry_count"] == 0
    boundary = evidence["provider_boundary"]
    assert boundary["network_ledger_valid"] is True
    assert all(
        boundary[field] == 0
        for field in (
            "network_attempt_count",
            "agent_session_count",
            "turn_count",
            "broker_request_count",
            "model_request_count",
            "provider_request_count",
            "occupied_worker_count",
            "docker_invocation_count",
            "database_invocation_count",
        )
    )


def test_consumed_attempt_cleanup_and_nonretry_latch_are_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _evidence()

    assert evidence["cleanup"]["process_absent"] is True
    assert evidence["cleanup"]["disposable_root_absent"] is True

    def reject_popen(*args: object, **kwargs: object) -> None:
        raise AssertionError("consumed attempt must reject before process launch")

    monkeypatch.setattr(subprocess, "Popen", reject_popen)
    with pytest.raises(
        RecoveryBootError, match="canonical_attempt_output_already_exists"
    ):
        execute_boot()


def test_report_states_the_narrow_claim_and_cleanup() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")

    for phrase in (
        "`SERVICES_UNAVAILABLE`",
        "Reliable duration: `10025 ms`",
        "Process absent: `true`",
        "Disposable root absent: `true`",
        "It is not an occupied worker",
    ):
        assert phrase in report
    assert Path("docs/branding").is_dir()
