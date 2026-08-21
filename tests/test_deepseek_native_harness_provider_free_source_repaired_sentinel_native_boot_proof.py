from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_source_repaired_sentinel_native_boot_proof
    as subject,
)


def test_fresh_attempt_identity_and_paths_are_disjoint() -> None:
    subject.configure_engine()
    contract = subject.engine.load_contract()

    assert contract["attempt"]["attempt_id"] == subject.ATTEMPT_ID
    assert contract["attempt"]["native_process_limit"] == 1
    assert all(contract["attempt"][key] is False for key in ("automatic_retry", "manual_retry", "resume", "fallback", "reclassification"))
    assert subject.CONSUMED_PATH.parent == subject.CONTINUITY_ROOT
    assert "source-repaired" in subject.CONSUMED_PATH.as_posix()


def test_deterministic_check_binds_source_repair_without_node() -> None:
    projection = subject.deterministic_check()

    assert projection["native_process_count"] == 0
    assert projection["profile"]["runner_row_count"] == 0
    assert projection["command"][-2:] == ["--profile", "headless"]
    assert projection["sentinel_sha256"] == "8b53bc7fb781d29d87310ee2d3425ca159a62fed4893a3e4db94069d63cd60bd"
    assert projection["disposable_root_prefix"] == "dsh-source-repaired-sentinel-boot-"
    assert subject.engine.tempfile.mkdtemp is subject._source_repaired_mkdtemp


def test_source_repair_lineage_binds_all_components() -> None:
    subject.configure_engine()
    contract = subject.engine.load_contract()
    lineage = subject._source_repair_lineage(contract)

    assert len(lineage["sources"]) == 4
    assert len(lineage["components"]) == 7


def test_reusable_controller_still_has_one_popen_and_no_retry() -> None:
    subject.configure_engine()
    checks = subject.engine.validate_controller_source()

    assert checks["single_popen"] is True
    assert checks["single_popen_module"] is True
    assert checks["no_retry_loop"] is True


def test_direct_script_check_bootstraps_and_starts_no_native_process() -> None:
    completed = subprocess.run(
        [sys.executable, str(Path(subject.__file__).resolve()), "--check"],
        cwd=subject.REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["status"] == "passed"
    assert output["native_processes"] == 0


def test_contract_keeps_every_non_sentinel_surface_closed() -> None:
    subject.configure_engine()
    contract = subject.engine.load_contract()

    assert contract["profile"]["runner_row_count"] == 0
    assert contract["profile"]["runner_file_count"] == 0
    assert contract["launch"]["task_arguments"] == []
    assert set(contract["zero_activity"]) >= {"broker_processes", "worker_sessions", "model_requests", "provider_requests", "network_attempts"}


def test_retained_failed_closed_terminal_is_exact_and_cleaned() -> None:
    subject.configure_engine()
    consumed = subject.engine._load_json(subject.CONSUMED_PATH)
    terminal = subject.engine._load_json(subject.EVIDENCE_PATH)

    jsonschema.validate(
        terminal,
        subject.engine._load_json(subject.EVIDENCE_SCHEMA_PATH),
    )
    assert consumed["state"] == "consumed"
    assert consumed["attempt_id"] == subject.ATTEMPT_ID
    assert consumed["candidate_source"] == terminal["candidate_source"]
    assert len(terminal["candidate_source"]) == 40
    assert terminal["result"] == "failed_closed"
    assert terminal["failure_coordinate"] == "native_process_exited_before_readiness"
    assert terminal["hmr_events"] == ["sentinel_activated"]
    assert terminal["launch"]["launch_attempt_count"] == 1
    assert terminal["launch"]["native_process_count"] == 1
    assert terminal["launch"]["retry_count"] == 0
    assert all(
        terminal["provider_boundary"][key] == 0
        for key in (
            "broker_processes",
            "worker_sessions",
            "model_requests",
            "provider_requests",
            "network_attempts",
            "docker_invocations",
            "database_invocations",
        )
    )
    assert terminal["streams"]["raw_retained"] is False
    assert terminal["cleanup"] == {
        "process_absent": True,
        "disposable_root_absent": True,
        "raw_streams_retained": False,
        "raw_environment_retained": False,
        "copied_package_tree_retained": False,
    }
    report = subject.REPORT_PATH.read_text(encoding="utf-8")
    assert "did not reach readiness" in report
    assert not any(
        subject.engine.DISPOSABLE_PARENT.glob(subject.DISPOSABLE_PREFIX + "*")
    )
