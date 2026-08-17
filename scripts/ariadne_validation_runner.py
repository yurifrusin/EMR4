"""Run one admitted Ariadne validation manifest with durable lifecycle evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from scripts.ariadne_evidence_gate import (
    command_manifest_sha256,
    load_command_manifest,
    validate_command_manifest,
)
from scripts.ariadne_serial_pytest import validate_pytest_arguments


SCHEMA_VERSION = "ariadne.validation_run.v1"
SERIAL_PYTEST_MODULE = "scripts.ariadne_serial_pytest"
PROVIDER_FREE_PYTEST_MODULE = "scripts.ariadne_provider_free_pytest"
PYTEST_EXECUTABLES = frozenset({"pytest", "pytest.exe", "py.test", "py.test.exe"})


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _python_module(argv: Sequence[str]) -> str | None:
    executable = Path(argv[0]).name.casefold()
    if not (
        executable in {"python", "python.exe", "python3", "python3.exe"}
        or executable.startswith("python3.")
    ):
        return None
    if len(argv) >= 3 and argv[1] == "-m":
        return argv[2]
    return None


def _bound_repo_root(arguments: list[str], repo_root: Path) -> list[str]:
    args = list(arguments)
    if "--repo-root" not in args:
        return args
    index = args.index("--repo-root")
    if index + 1 >= len(args):
        raise ValueError("pytest_repo_root_value_missing")
    supplied = Path(args[index + 1])
    if not supplied.is_absolute():
        supplied = repo_root / supplied
    if supplied.resolve() != repo_root:
        raise ValueError("pytest_repo_root_mismatch")
    del args[index : index + 2]
    return args


def _validate_provider_free_arguments(
    arguments: Sequence[str], *, repo_root: Path
) -> None:
    args = _bound_repo_root(list(arguments), repo_root)
    if args[:1] == ["--"]:
        args = args[1:]
    if not args:
        raise ValueError("provider_free_test_paths_required")
    for token in args:
        if token.startswith("-") or "::" in token:
            raise ValueError("provider_free_test_selector_invalid")
        normalized = token.replace("\\", "/")
        if not normalized.startswith("tests/") or not normalized.endswith(".py"):
            raise ValueError("provider_free_test_selector_invalid")
        candidate = (repo_root / Path(token)).resolve()
        try:
            candidate.relative_to(repo_root)
        except ValueError as error:
            raise ValueError("selected_test_path_outside_repository") from error
        if not candidate.is_file():
            raise ValueError(f"selected_test_path_missing:{normalized}")


def _validate_serial_arguments(arguments: Sequence[str], *, repo_root: Path) -> None:
    args = _bound_repo_root(list(arguments), repo_root)
    try:
        separator = args.index("--")
    except ValueError as error:
        raise ValueError("serial_pytest_separator_required") from error
    launcher_args = args[:separator]
    if launcher_args:
        if len(launcher_args) != 2 or launcher_args[0] != "--timeout-seconds":
            raise ValueError("serial_pytest_launcher_arguments_invalid")
        try:
            if float(launcher_args[1]) <= 0:
                raise ValueError
        except ValueError as error:
            raise ValueError("serial_pytest_timeout_invalid") from error
    validate_pytest_arguments(args[separator:], repo_root=repo_root)


def validate_execution_manifest(
    manifest: object, *, repo_root: Path
) -> dict[str, Any]:
    """Admit exact argv and fail closed around repository pytest entry points."""
    root = repo_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("repo_root_must_be_directory")
    admitted = validate_command_manifest(manifest)
    for index, command in enumerate(admitted["commands"]):
        argv = command["argv"]
        executable = Path(argv[0]).name.casefold()
        module = _python_module(argv)
        if executable in PYTEST_EXECUTABLES or module == "pytest":
            raise ValueError(f"command[{index}] direct_pytest_forbidden")
        if module == SERIAL_PYTEST_MODULE:
            _validate_serial_arguments(argv[3:], repo_root=root)
        elif module == PROVIDER_FREE_PYTEST_MODULE:
            _validate_provider_free_arguments(argv[3:], repo_root=root)
    return admitted


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _terminal_write(stream: Any, payload: bytes) -> None:
    binary = getattr(stream, "buffer", None)
    if binary is not None:
        binary.write(payload)
        binary.flush()
        return
    stream.write(payload.decode("utf-8", errors="replace"))
    stream.flush()


def _pending_result(command: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": command["id"],
        "argv": command["argv"],
        "status": "pending",
        "exit_code": None,
        "elapsed_ms": None,
        "stdout_sha256": None,
        "stdout_bytes": None,
        "stderr_sha256": None,
        "stderr_bytes": None,
        "error_code": None,
    }


def run_validation(
    *, manifest: object, repo_root: Path, receipt_path: Path
) -> dict[str, Any]:
    root = repo_root.resolve(strict=True)
    admitted = validate_execution_manifest(manifest, repo_root=root)
    receipt = receipt_path.resolve()
    if receipt.exists():
        raise ValueError("validation_receipt_already_exists")
    lifecycle: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "in_progress",
        "repo_root": str(root),
        "command_manifest_sha256": command_manifest_sha256(admitted),
        "commands": admitted["commands"],
        "started_at": _timestamp(),
        "ended_at": None,
        "failure_command_id": None,
        "results": [_pending_result(command) for command in admitted["commands"]],
    }
    _atomic_write(receipt, lifecycle)

    for index, command in enumerate(admitted["commands"]):
        lifecycle["results"][index]["status"] = "in_progress"
        _atomic_write(receipt, lifecycle)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command["argv"],
                cwd=root,
                check=False,
                capture_output=True,
                shell=False,
            )
        except KeyboardInterrupt:
            lifecycle["results"][index]["status"] = "interrupted"
            lifecycle["results"][index]["elapsed_ms"] = round(
                (time.monotonic() - started) * 1000
            )
            lifecycle["status"] = "interrupted"
            lifecycle["failure_command_id"] = command["id"]
            lifecycle["ended_at"] = _timestamp()
            _atomic_write(receipt, lifecycle)
            return lifecycle
        except OSError:
            lifecycle["results"][index]["status"] = "failed"
            lifecycle["results"][index]["elapsed_ms"] = round(
                (time.monotonic() - started) * 1000
            )
            lifecycle["results"][index]["error_code"] = "process_launch_failed"
            lifecycle["status"] = "failed"
            lifecycle["failure_command_id"] = command["id"]
            lifecycle["ended_at"] = _timestamp()
            _atomic_write(receipt, lifecycle)
            return lifecycle

        stdout = completed.stdout or b""
        stderr = completed.stderr or b""
        _terminal_write(sys.stdout, stdout)
        _terminal_write(sys.stderr, stderr)
        result = lifecycle["results"][index]
        result.update(
            {
                "status": "passed" if completed.returncode == 0 else "failed",
                "exit_code": completed.returncode,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
                "stdout_bytes": len(stdout),
                "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
                "stderr_bytes": len(stderr),
            }
        )
        if completed.returncode != 0:
            lifecycle["status"] = "failed"
            lifecycle["failure_command_id"] = command["id"]
            lifecycle["ended_at"] = _timestamp()
            _atomic_write(receipt, lifecycle)
            return lifecycle
        _atomic_write(receipt, lifecycle)

    lifecycle["status"] = "passed"
    lifecycle["ended_at"] = _timestamp()
    _atomic_write(receipt, lifecycle)
    return lifecycle


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one shell-free validation manifest with durable evidence."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        manifest = load_command_manifest(args.manifest.resolve(strict=True))
        result = run_validation(
            manifest=manifest,
            repo_root=args.repo_root,
            receipt_path=args.receipt,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Ariadne validation runner failed: {error}", file=sys.stderr)
        return 2
    if result["status"] == "passed":
        return 0
    if result["status"] == "interrupted":
        return 130
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
