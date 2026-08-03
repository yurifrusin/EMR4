from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from scripts.ariadne_serial_pytest import (
    LOCK_PATH,
    LOCK_TIMEOUT_ENV,
    ROOT,
    SerialPytestLockTimeout,
    build_pytest_command,
    build_pytest_environment,
    serial_pytest_lock,
)


def test_default_lock_is_outside_repository_and_command_is_shell_free() -> None:
    assert ROOT != LOCK_PATH
    assert ROOT not in LOCK_PATH.parents
    assert build_pytest_command(["--", "tests/test_example.py::test_case", "-q"]) == [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_example.py::test_case",
        "-q",
    ]
    with pytest.raises(ValueError, match="explicit_pytest_arguments_required"):
        build_pytest_command([])
    environment = build_pytest_environment(12.5)
    assert environment[LOCK_TIMEOUT_ENV] == "12.5"
    with pytest.raises(ValueError, match="timeout_seconds_must_be_positive"):
        build_pytest_environment(0)


def test_lock_fails_closed_during_cross_process_contention(tmp_path: Path) -> None:
    lock_path = (tmp_path / "shared.lock").resolve()
    code = (
        "import time\n"
        "from pathlib import Path\n"
        "from scripts.ariadne_serial_pytest import serial_pytest_lock\n"
        f"with serial_pytest_lock(timeout_seconds=2, lock_path=Path({str(lock_path)!r})):\n"
        "    print('LOCKED', flush=True)\n"
        "    time.sleep(1)\n"
    )
    holder = subprocess.Popen(
        [sys.executable, "-c", code],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "LOCKED"
        with pytest.raises(SerialPytestLockTimeout, match="shared_pytest_lock_timeout"):
            with serial_pytest_lock(timeout_seconds=0.1, lock_path=lock_path):
                raise AssertionError("contended lock was acquired")
    finally:
        stdout, stderr = holder.communicate(timeout=5)
        assert holder.returncode == 0, stdout + stderr

    with serial_pytest_lock(timeout_seconds=1, lock_path=lock_path) as waited:
        assert waited < 1


def test_worker_policies_require_the_serial_launcher() -> None:
    settings = ROOT / "orchestration/harness_settings"
    verifier = yaml.safe_load(
        (settings / "verifier_execution_policy.yaml").read_text(encoding="utf-8")
    )
    sprint = yaml.safe_load(
        (settings / "sprint_worker_policy.yaml").read_text(encoding="utf-8")
    )

    expected = "../../scripts/ariadne_serial_pytest.py"
    assert verifier["test_execution"]["required_pytest_launcher"] == expected
    assert sprint["test_execution"]["shared_postgresql_schema"][
        "required_launcher"
    ] == expected
    assert sprint["test_execution"]["shared_postgresql_schema"][
        "instruction_only_serialization"
    ] is False
    assert verifier["test_execution"]["conftest_enforcement"] == (
        "../../tests/conftest.py"
    )
    assert sprint["test_execution"]["shared_postgresql_schema"][
        "direct_pytest_bypass"
    ] == "serialized_by_repository_conftest"


def test_direct_pytest_entry_cannot_bypass_outer_repository_lock() -> None:
    environment = os.environ.copy()
    environment[LOCK_TIMEOUT_ENV] = "0.1"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "tests/test_ariadne_verifier_execution_policy.py",
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    combined = completed.stdout + completed.stderr
    assert completed.returncode != 0
    assert "shared_pytest_lock_timeout" in combined
