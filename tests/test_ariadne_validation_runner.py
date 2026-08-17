from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
from scripts.ariadne_validation_runner import (
    run_validation,
    validate_execution_manifest,
)


def _manifest(*commands: tuple[str, list[str]]) -> dict[str, object]:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {"id": command_id, "argv": argv} for command_id, argv in commands
        ],
    }


def _test_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)
    (tests / "conftest.py").write_text("# synthetic\n", encoding="utf-8")
    (tests / "test_present.py").write_text(
        "def test_present(): pass\n", encoding="utf-8"
    )
    return repo


def test_runner_stops_on_first_failure_and_persists_only_output_digests(
    tmp_path: Path,
) -> None:
    repo = _test_repo(tmp_path)
    marker = repo / "must-not-run.txt"
    receipt = repo / "validation.json"
    terminal_only = "terminal-only-secret"
    manifest = _manifest(
        (
            "ONE",
            [
                sys.executable,
                "-c",
                f"print(bytes.fromhex('{terminal_only.encode().hex()}').decode())",
            ],
        ),
        ("TWO", [sys.executable, "-c", "import sys; sys.exit(7)"]),
        (
            "THREE",
            [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')",
            ],
        ),
    )

    result = run_validation(
        manifest=manifest,
        repo_root=repo,
        receipt_path=receipt,
    )

    durable = json.loads(receipt.read_text(encoding="utf-8"))
    assert result == durable
    assert durable["status"] == "failed"
    assert durable["failure_command_id"] == "TWO"
    assert [row["status"] for row in durable["results"]] == [
        "passed",
        "failed",
        "pending",
    ]
    assert durable["results"][0]["stdout_bytes"] in {
        len((terminal_only + "\r\n").encode()),
        len((terminal_only + "\n").encode()),
    }
    assert terminal_only not in receipt.read_text(encoding="utf-8")
    assert not marker.exists()


@pytest.mark.parametrize(
    ("argv", "reason"),
    [
        ([sys.executable, "-m", "pytest", "-q"], "direct_pytest_forbidden"),
        (
            [
                sys.executable,
                "-m",
                "scripts.ariadne_serial_pytest",
                "--",
                "--noconftest",
                "tests/test_present.py",
            ],
            "serial_pytest_noconftest_forbidden",
        ),
        (
            [
                sys.executable,
                "-m",
                "scripts.ariadne_serial_pytest",
                "--",
                "tests/test_absent.py",
            ],
            "selected_test_path_missing",
        ),
        (
            [
                sys.executable,
                "-m",
                "scripts.ariadne_serial_pytest",
                "--",
                "tests/test_present.py",
                ";",
                "echo",
            ],
            "compound shell tokens are forbidden",
        ),
    ],
)
def test_runner_rejects_unsafe_pytest_envelopes(
    tmp_path: Path, argv: list[str], reason: str
) -> None:
    repo = _test_repo(tmp_path)
    with pytest.raises(ValueError, match=reason):
        validate_execution_manifest(_manifest(("TEST", argv)), repo_root=repo)


def test_runner_binds_provider_free_paths_to_exact_repo(tmp_path: Path) -> None:
    repo = _test_repo(tmp_path)
    admitted = validate_execution_manifest(
        _manifest(
            (
                "PF",
                [
                    sys.executable,
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    str(repo),
                    "tests/test_present.py",
                ],
            )
        ),
        repo_root=repo,
    )
    assert admitted["commands"][0]["id"] == "PF"


def test_interrupted_run_is_durably_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _test_repo(tmp_path)
    receipt = repo / "interrupted.json"

    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "scripts.ariadne_validation_runner.subprocess.run",
        interrupt,
    )
    result = run_validation(
        manifest=_manifest(("INT", [sys.executable, "-c", "print('never')"])),
        repo_root=repo,
        receipt_path=receipt,
    )

    durable = json.loads(receipt.read_text(encoding="utf-8"))
    assert result["status"] == "interrupted"
    assert durable["status"] == "interrupted"
    assert durable["results"][0]["status"] == "interrupted"
    assert durable["results"][0]["exit_code"] is None
