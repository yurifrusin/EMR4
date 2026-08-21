from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

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
