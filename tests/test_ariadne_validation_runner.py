from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

from scripts.ariadne_evidence_gate import (
    COMMAND_MANIFEST_SCHEMA_VERSION,
    COMMAND_MANIFEST_SCHEMA_VERSION_V2,
)
from scripts.ariadne_validation_runner import (
    run_validation,
    validate_execution_manifest,
    validate_execution_manifest_with_admission,
)
from scripts.ariadne_provider_free_pytest import EXPECTED_ADMISSION_ENV


def _manifest(*commands: tuple[str, list[str]]) -> dict[str, object]:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {"id": command_id, "argv": argv} for command_id, argv in commands
        ],
    }


def _v2_manifest(
    *commands: tuple[str, list[str], str], database_authority: str = "closed"
) -> dict[str, object]:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION_V2,
        "database_authority": database_authority,
        "commands": [
            {"id": command_id, "argv": argv, "verification_phase": phase}
            for command_id, argv, phase in commands
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


def test_runner_passes_engine_derived_selection_digest_to_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _test_repo(tmp_path)
    receipt = repo / "provider-free-validation.json"
    observed: dict[str, object] = {}

    class Completed:
        returncode = 0
        stdout = b""
        stderr = b""

    def fake_run(argv, *, cwd, env, check, capture_output, shell):
        observed.update(argv=argv, cwd=cwd, env=env)
        return Completed()

    monkeypatch.setattr("scripts.ariadne_validation_runner.subprocess.run", fake_run)
    manifest = _manifest(
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
    )

    result = run_validation(
        manifest=manifest, repo_root=repo, receipt_path=receipt
    )

    assert result["status"] == "passed"
    assert result["provider_free_no_database_admission_sha256"].startswith(
        "sha256:"
    )
    assert observed["env"][EXPECTED_ADMISSION_ENV].startswith("sha256:")


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


@pytest.mark.parametrize(
    ("argv", "reason"),
    [
        ([sys.executable, "-m", "pytest", "tests/test_present.py"], "database_closed_ordinary_pytest_forbidden"),
        ([sys.executable, "-m", "scripts.ariadne_serial_pytest", "--", "tests/test_present.py"], "database_closed_serial_pytest_forbidden"),
    ],
)
def test_v2_database_closed_rejects_ordinary_and_serial_before_launch(
    tmp_path: Path, argv: list[str], reason: str
) -> None:
    repo = _test_repo(tmp_path)
    manifest = _v2_manifest(("TEST", argv, "prepublication"))

    with pytest.raises(ValueError, match=reason):
        validate_execution_manifest(manifest, repo_root=repo)


def test_v2_runner_requires_phase_and_executes_only_selected_partition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _test_repo(tmp_path)
    manifest = _v2_manifest(
        ("PRE", [sys.executable, "-c", "print('pre')"], "prepublication"),
        ("POST", [sys.executable, "-c", "print('post')"], "postpublication"),
    )
    observed: list[list[str]] = []

    class Completed:
        returncode = 0
        stdout = b""
        stderr = b""

    def fake_run(argv, *, cwd, env, check, capture_output, shell):
        observed.append(argv)
        return Completed()

    monkeypatch.setattr("scripts.ariadne_validation_runner.subprocess.run", fake_run)
    with pytest.raises(ValueError, match="verification_phase_required"):
        run_validation(
            manifest=manifest,
            repo_root=repo,
            receipt_path=repo / "missing-phase.json",
        )

    result = run_validation(
        manifest=manifest,
        repo_root=repo,
        receipt_path=repo / "prepublication.json",
        phase="prepublication",
    )

    assert observed == [[sys.executable, "-c", "print('pre')"]]
    assert result["schema_version"] == "ariadne.validation_run.v2"
    assert result["database_authority"] == "closed"
    assert result["verification_phase"] == "prepublication"
    assert [row["id"] for row in result["commands"]] == ["PRE"]


def test_v2_closed_provider_free_selection_retains_exact_admission(
    tmp_path: Path,
) -> None:
    repo = _test_repo(tmp_path)
    manifest = _v2_manifest(
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
            "prepublication",
        )
    )

    admitted, admission = validate_execution_manifest_with_admission(
        manifest, repo_root=repo, require_provider_free=True
    )

    assert admitted["database_authority"] == "closed"
    assert admission is not None
    assert admission["commands"][0]["command_id"] == "PF"
