#!/usr/bin/env python3
"""Run repository pytest with its mandatory shared-schema lock configuration.

EMR4's repository ``tests/conftest.py`` owns one disposable PostgreSQL schema.
Parallel pytest processes can therefore drop or truncate tables underneath one
another. The repository conftest acquires the OS lock for every normal pytest
entry point; this launcher supplies its bounded timeout without shell
interpolation or repository-local lock residue.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Sequence


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = Path(tempfile.gettempdir()) / "emr4-ariadne-shared-pytest-v1.lock"
LOCK_TIMEOUT_ENV = "EMR4_ARIADNE_SERIAL_PYTEST_TIMEOUT_SECONDS"


class SerialPytestLockTimeout(RuntimeError):
    """The shared pytest lock could not be acquired inside the bound wait."""


def _try_lock(handle) -> bool:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return False
        return True

    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return False
    return True


def _unlock(handle) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def serial_pytest_lock(
    *,
    timeout_seconds: float,
    lock_path: Path = LOCK_PATH,
) -> Iterator[float]:
    """Acquire the shared pytest lock and yield the measured wait in seconds."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds_must_be_positive")
    lock_path = lock_path.resolve()
    if ROOT == lock_path or ROOT in lock_path.parents:
        raise ValueError("lock_path_must_be_outside_repository")
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()

        while not _try_lock(handle):
            waited = time.monotonic() - started
            if waited >= timeout_seconds:
                raise SerialPytestLockTimeout(
                    f"shared_pytest_lock_timeout_after_{timeout_seconds:g}_seconds"
                )
            time.sleep(min(0.1, timeout_seconds - waited))

        try:
            yield time.monotonic() - started
        finally:
            _unlock(handle)


def build_pytest_command(pytest_args: Sequence[str]) -> list[str]:
    args = list(pytest_args)
    if args[:1] == ["--"]:
        args = args[1:]
    if not args:
        raise ValueError("explicit_pytest_arguments_required")
    return [sys.executable, "-m", "pytest", *args]


def build_pytest_environment(timeout_seconds: float) -> dict[str, str]:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds_must_be_positive")
    environment = os.environ.copy()
    environment[LOCK_TIMEOUT_ENV] = f"{timeout_seconds:g}"
    return environment


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run EMR4 pytest under the shared PostgreSQL schema lock."
    )
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        command = build_pytest_command(args.pytest_args)
        environment = build_pytest_environment(args.timeout_seconds)
        completed = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            env=environment,
        )
        return completed.returncode
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
