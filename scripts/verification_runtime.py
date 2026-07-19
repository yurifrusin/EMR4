"""Shared subprocess semantics for EMR4 verification entry points."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
from typing import Mapping, Sequence


LAUNCHER_TIMEOUT_EXIT = 124
TIMEOUT_SECONDS = {
    "tool": 120,
    "focused_tests": 300,
    "full_tests": 900,
    "migration_step": 300,
}


@dataclass(frozen=True)
class VerificationCommand:
    label: str
    argv: Sequence[str]
    timeout_seconds: int


def run_command(
    command: VerificationCommand,
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
) -> int:
    """Run one gate and distinguish child failure from launcher timeout."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    print(
        f"[verify] {command.label} "
        f"(timeout={command.timeout_seconds}s)",
        flush=True,
    )
    try:
        completed = subprocess.run(
            list(command.argv),
            cwd=cwd,
            env=merged_env,
            check=False,
            timeout=command.timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        print(
            f"[launcher_timeout] {command.label} exceeded "
            f"{command.timeout_seconds}s",
            file=sys.stderr,
            flush=True,
        )
        return LAUNCHER_TIMEOUT_EXIT

    if completed.returncode:
        print(
            f"[child_failure] {command.label} exited "
            f"{completed.returncode}",
            file=sys.stderr,
            flush=True,
        )
        return completed.returncode

    print(f"[pass] {command.label}", flush=True)
    return 0


def run_commands(
    commands: Sequence[VerificationCommand],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
) -> int:
    for command in commands:
        result = run_command(command, cwd=cwd, env=env)
        if result:
            return result
    return 0
