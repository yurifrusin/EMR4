"""Run declarative Access AI setup paths.

Setup paths are YAML documents that describe a goal, shared properties, and a
sequence of executable steps. The runner resolves `${...}` references from the
document and executes each step only when `--execute` is supplied. Dry-run is
the default because these paths can change IAM, enable APIs, or alter local ADC.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


REFERENCE_RE = re.compile(r"\$\{([^}]+)\}")
ALLOWED_EXECUTABLES = {
    "gcloud",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
    "python",
    "python.exe",
}


class SetupPathError(RuntimeError):
    """Raised when a setup path cannot be resolved or executed safely."""


@dataclass(frozen=True)
class CommandSpec:
    executable: str
    args: tuple[str, ...]
    env: dict[str, str]

    @property
    def argv(self) -> tuple[str, ...]:
        return (self.executable, *self.args)


@dataclass(frozen=True)
class StepResult:
    step_id: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    dry_run: bool


def load_setup_path(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SetupPathError("Setup path must be a YAML mapping.")
    if not data.get("goal"):
        raise SetupPathError("Setup path must define a non-empty 'goal'.")
    if not isinstance(data.get("steps"), list) or not data["steps"]:
        raise SetupPathError("Setup path must define at least one step.")
    return data


def get_value_by_path(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise SetupPathError(f"Unknown setup path reference: {dotted_path}")
    return current


def resolve_value(value: Any, root: dict[str, Any]) -> Any:
    if isinstance(value, str):
        full_match = REFERENCE_RE.fullmatch(value)
        if full_match:
            resolved = get_value_by_path(root, full_match.group(1).strip())
            return resolved

        def replace(match: re.Match[str]) -> str:
            resolved = get_value_by_path(root, match.group(1).strip())
            return str(resolved)

        return REFERENCE_RE.sub(replace, value)
    if isinstance(value, list):
        return [resolve_value(item, root) for item in value]
    if isinstance(value, dict):
        return {key: resolve_value(item, root) for key, item in value.items()}
    return value


def resolve_document(data: dict[str, Any]) -> dict[str, Any]:
    return resolve_value(data, data)


def _stringify_args(args: Iterable[Any]) -> tuple[str, ...]:
    return tuple(str(arg) for arg in args)


def _validate_executable(executable: str) -> None:
    normalized = executable.lower()
    if normalized in ALLOWED_EXECUTABLES:
        return
    if executable.startswith("scripts/") or executable.startswith("scripts\\"):
        return
    raise SetupPathError(
        f"Executable {executable!r} is not allowed. Use a small wrapper under "
        "scripts/ or one of: " + ", ".join(sorted(ALLOWED_EXECUTABLES))
    )


def build_command(step: dict[str, Any], *, repo_root: Path) -> CommandSpec:
    executable = step.get("executable")
    if not isinstance(executable, str) or not executable:
        raise SetupPathError(f"Step {step.get('id')!r} must define executable.")
    _validate_executable(executable)

    args = step.get("args", [])
    if not isinstance(args, list):
        raise SetupPathError(f"Step {step.get('id')!r} args must be a list.")

    env = step.get("env", {})
    if not isinstance(env, dict):
        raise SetupPathError(f"Step {step.get('id')!r} env must be a mapping.")

    resolved_executable = executable
    if executable.startswith("scripts/") or executable.startswith("scripts\\"):
        resolved_executable = str(repo_root / executable)

    return CommandSpec(
        executable=resolved_executable,
        args=_stringify_args(args),
        env={str(key): str(value) for key, value in env.items()},
    )


def run_command(
    step_id: str,
    command: CommandSpec,
    *,
    cwd: Path,
    dry_run: bool,
) -> StepResult:
    if dry_run:
        return StepResult(
            step_id=step_id,
            command=command.argv,
            returncode=0,
            stdout="",
            stderr="",
            dry_run=True,
        )

    env = os.environ.copy()
    env.update(command.env)
    completed = subprocess.run(
        command.argv,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return StepResult(
        step_id=step_id,
        command=command.argv,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        dry_run=False,
    )


def verify_step(
    step_id: str,
    verify: dict[str, Any] | None,
    *,
    repo_root: Path,
    cwd: Path,
    dry_run: bool,
) -> StepResult | None:
    if not verify:
        return None
    command = build_command(verify, repo_root=repo_root)
    result = run_command(f"{step_id}:verify", command, cwd=cwd, dry_run=dry_run)
    if dry_run:
        return result
    if result.returncode != 0:
        raise SetupPathError(f"Verification failed for {step_id}: {result.stderr or result.stdout}")
    expected = verify.get("expect_contains")
    if expected is not None and str(expected) not in result.stdout:
        raise SetupPathError(
            f"Verification for {step_id} did not contain {expected!r}. "
            f"stdout was: {result.stdout!r}"
        )
    return result


def run_setup_path(
    data: dict[str, Any],
    *,
    repo_root: Path,
    execute: bool = False,
) -> list[StepResult]:
    resolved = resolve_document(data)
    results: list[StepResult] = []
    dry_run = not execute

    for raw_step in resolved["steps"]:
        if not isinstance(raw_step, dict):
            raise SetupPathError("Each setup path step must be a mapping.")
        step_id = raw_step.get("id")
        if not isinstance(step_id, str) or not step_id:
            raise SetupPathError("Each setup path step must define a non-empty id.")

        command = build_command(raw_step, repo_root=repo_root)
        result = run_command(step_id, command, cwd=repo_root, dry_run=dry_run)
        results.append(result)
        if not dry_run and result.returncode != 0:
            raise SetupPathError(
                f"Step {step_id} failed with exit code {result.returncode}: "
                f"{result.stderr or result.stdout}"
            )

        verify_result = verify_step(
            step_id,
            raw_step.get("verify"),
            repo_root=repo_root,
            cwd=repo_root,
            dry_run=dry_run,
        )
        if verify_result:
            results.append(verify_result)

    return results


def result_to_dict(result: StepResult) -> dict[str, Any]:
    return {
        "step_id": result.step_id,
        "command": list(result.command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "dry_run": result.dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an Access AI setup path.")
    parser.add_argument("path", type=Path, help="YAML setup path to run.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute commands. Without this flag the runner only prints a dry-run plan.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    try:
        data = load_setup_path(args.path)
        results = run_setup_path(data, repo_root=repo_root, execute=args.execute)
    except SetupPathError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([result_to_dict(result) for result in results], indent=2))
    else:
        mode = "EXECUTE" if args.execute else "DRY RUN"
        print(f"Access AI setup path: {data['goal']} ({mode})")
        for result in results:
            print(f"- {result.step_id}: {' '.join(result.command)}")
            if args.execute and result.stdout.strip():
                print(result.stdout.strip())
            if args.execute and result.stderr.strip():
                print(result.stderr.strip(), file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

