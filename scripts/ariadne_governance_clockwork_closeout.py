"""Run one interpreter-bound governance closeout sequence and emit stage paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.governance_clockwork_tick import (
    SEMANTIC_TICK_INTENT_VERSION,
    admit_tick_intent,
)
from orchestration_harness.governance_live_adoption import validate_contract


CONTRACT = (
    ROOT
    / "orchestration/continuity/"
    "ariadne-provider-free-clockwork-live-canonical-adoption-retirement/contract.json"
)
RESULT_VERSION = "ariadne.governance_bound_closeout_driver_result.v1"
STAGE_MANIFEST_VERSION = "ariadne.governance_explicit_stage_manifest.v1"
POSTPUBLICATION_TESTS = (
    "tests/test_current_baton_consistency.py",
    "tests/test_ariadne_active_operation_latch.py",
    "tests/test_ariadne_governance_clockwork_tick.py",
    "tests/test_ariadne_transactional_closeout.py",
    "tests/test_ariadne_orchestrator_preflight.py",
)
CLOCKWORK_METADATA_NAMES = (
    "command-manifest.json",
    "current.json",
    "generation-manifest.json",
    "ownership.json",
    "transaction.json",
)
HEX40 = re.compile(r"[0-9a-f]{40}")
Runner = Callable[..., subprocess.CompletedProcess[str]]


class CloseoutDriverRejection(RuntimeError):
    """The bound closeout driver failed closed before a valid result."""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CloseoutDriverRejection(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise CloseoutDriverRejection(f"json_object_required:{path.name}")
    return value


def _relative_path(repo_root: Path, raw: str, *, reason: str) -> str:
    if (
        not isinstance(raw, str)
        or not raw
        or "\\" in raw
        or Path(raw).is_absolute()
        or any(part in {"", ".", ".."} for part in raw.split("/"))
    ):
        raise CloseoutDriverRejection(reason)
    path = (repo_root / raw).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError as error:
        raise CloseoutDriverRejection(reason) from error
    return path.relative_to(repo_root.resolve()).as_posix()


def _intent_path(repo_root: Path, raw: Path) -> Path:
    path = (repo_root / raw).resolve() if not raw.is_absolute() else raw.resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError as error:
        raise CloseoutDriverRejection("intent_path_escape") from error
    if not path.is_file() or path.name != "closeout-intent.json":
        raise CloseoutDriverRejection("semantic_closeout_intent_required")
    return path


def _run_text(
    command: Sequence[str],
    *,
    repo_root: Path,
    runner: Runner = subprocess.run,
    timeout: int = 900,
) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            list(command),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise CloseoutDriverRejection("subprocess_start_or_timeout") from error


def resolve_repository_interpreter(
    repo_root: Path, *, runner: Runner = subprocess.run
) -> tuple[Path, str]:
    """Resolve and attest the interpreter without trusting the caller's Python."""

    interpreter = (repo_root / ".venv/Scripts/python.exe").resolve()
    if not interpreter.is_file():
        raise CloseoutDriverRejection("repository_interpreter_missing")
    completed = _run_text(
        [
            str(interpreter),
            "-c",
            "import pathlib,sys;print(pathlib.Path(sys.executable).resolve())",
        ],
        repo_root=repo_root,
        runner=runner,
        timeout=30,
    )
    if completed.returncode != 0:
        raise CloseoutDriverRejection("repository_interpreter_attestation_failed")
    reported = completed.stdout.strip()
    if not reported or Path(reported).resolve() != interpreter:
        raise CloseoutDriverRejection("repository_interpreter_attestation_mismatch")
    return interpreter, reported


def resolve_full_head(
    repo_root: Path, *, runner: Runner = subprocess.run
) -> str:
    """Return the machine-resolved full HEAD; no caller-authored Git ID exists."""

    completed = _run_text(
        ["git", "rev-parse", "--verify", "HEAD"],
        repo_root=repo_root,
        runner=runner,
        timeout=30,
    )
    head = completed.stdout.strip()
    if completed.returncode != 0 or HEX40.fullmatch(head) is None:
        raise CloseoutDriverRejection("full_head_resolution_failed")
    return head


def _tracked_status(
    repo_root: Path, *, runner: Runner = subprocess.run
) -> str:
    completed = _run_text(
        ["git", "status", "--porcelain=v1", "--untracked-files=no"],
        repo_root=repo_root,
        runner=runner,
        timeout=30,
    )
    if completed.returncode != 0:
        raise CloseoutDriverRejection("tracked_status_failed")
    return completed.stdout


def _git_paths(repo_root: Path, arguments: Sequence[str]) -> set[str]:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=repo_root,
            check=False,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise CloseoutDriverRejection("git_path_inventory_failed") from error
    if completed.returncode != 0:
        raise CloseoutDriverRejection("git_path_inventory_failed")
    try:
        values = completed.stdout.decode("utf-8").split("\0")
    except UnicodeDecodeError as error:
        raise CloseoutDriverRejection("git_path_inventory_not_utf8") from error
    return {value for value in values if value}


def _publication_surface(repo_root: Path, contract: dict[str, Any]) -> dict[str, str]:
    paths = [*contract["canonical_paths"].values()]
    clockwork_root = contract["clockwork_root"]
    paths.extend(f"{clockwork_root}/{name}" for name in CLOCKWORK_METADATA_NAMES)
    reading: dict[str, str] = {}
    for raw in paths:
        relative = _relative_path(
            repo_root, raw, reason="publication_surface_path_invalid"
        )
        path = repo_root / relative
        try:
            reading[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            raise CloseoutDriverRejection("publication_surface_unreadable") from error
    return reading


def _parse_tick_result(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    if completed.returncode != 0:
        raise CloseoutDriverRejection("clockwork_tick_failed")
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise CloseoutDriverRejection("clockwork_tick_result_invalid") from error
    if not isinstance(result, dict):
        raise CloseoutDriverRejection("clockwork_tick_result_invalid")
    return result


def capture_tick_reading(
    result: dict[str, Any],
    *,
    mode: str,
    semantic_command_count: int,
) -> dict[str, Any]:
    """Validate a tick result and capture its publication-owned live reading."""

    if result.get("status") != "passed":
        raise CloseoutDriverRejection("clockwork_tick_not_passed")
    facts = result.get("transaction_facts")
    verification = result.get("verification_facts")
    if not isinstance(facts, dict) or not isinstance(verification, dict):
        raise CloseoutDriverRejection("clockwork_tick_facts_missing")
    expected_verification = {
        "disposition": "verification_passed",
        "command_count": semantic_command_count,
        "executed_command_count": semantic_command_count,
        "passed_command_count": semantic_command_count,
        "tracked_drift": 0,
    }
    if any(verification.get(key) != value for key, value in expected_verification.items()):
        raise CloseoutDriverRejection("semantic_verification_incomplete")
    common = {
        "source_commit": result.get("source_commit"),
        "generation_id": result.get("generation_id"),
        "lease_sequence": result.get("lease_sequence"),
    }
    if HEX40.fullmatch(str(common["source_commit"])) is None:
        raise CloseoutDriverRejection("tick_source_not_full_git_id")
    if not isinstance(common["generation_id"], str) or not common[
        "generation_id"
    ].startswith("gen-"):
        raise CloseoutDriverRejection("tick_generation_invalid")
    if not isinstance(common["lease_sequence"], int) or common["lease_sequence"] < 1:
        raise CloseoutDriverRejection("tick_lease_invalid")
    if mode == "rehearse":
        if (
            facts.get("command_disposition") != "dry_preparation"
            or facts.get("published_generations") != 0
            or facts.get("committed_lease_advance") != 0
            or result.get("live_publication_count") != 0
        ):
            raise CloseoutDriverRejection("rehearsal_publication_forbidden")
        return {
            "status": "not_executed_rehearsal",
            "captured_from": "verified_dry_preparation",
            **common,
        }
    if mode != "publish":
        raise CloseoutDriverRejection("driver_mode_invalid")
    if (
        facts.get("command_disposition") != "publication_committed"
        or facts.get("published_generations") != 1
        or facts.get("committed_lease_advance") != 1
        or result.get("live_publication_count") != 1
    ):
        raise CloseoutDriverRejection("committed_publication_result_required")
    return {
        "status": "passed",
        "captured_from": "tick_publish_return_after_validate_tick_live_state",
        **common,
    }


def _evidence_paths(admitted: dict[str, Any]) -> set[str]:
    manifest = admitted["transaction_manifest"]
    paths: set[str] = set(admitted["baton_acceptance"]["paths"])
    for section in (
        manifest["node"]["evidence"],
        manifest["journey"],
        manifest["current_position"],
    ):
        for value in section.values():
            if isinstance(value, list):
                paths.update(item for item in value if isinstance(item, str))
    paths.update(
        decision["source"]
        for decision in manifest["node"]["decisions"]
        if isinstance(decision, dict) and isinstance(decision.get("source"), str)
    )
    return paths


def derive_allowlist(
    repo_root: Path,
    *,
    intent_path: Path,
    admitted: dict[str, Any],
    contract: dict[str, Any],
) -> set[str]:
    """Derive the only paths eligible for the explicit stage manifest."""

    intent_relative = intent_path.relative_to(repo_root.resolve()).as_posix()
    topic = intent_relative.rsplit("/", 1)[0]
    raw_paths = {
        intent_relative,
        *_evidence_paths(admitted),
        *contract["canonical_paths"].values(),
        *(f"{contract['clockwork_root']}/{name}" for name in CLOCKWORK_METADATA_NAMES),
        f"{topic}/clockwork-tick-evidence.json",
        f"{topic}/clockwork-tick-report.md",
        f"{topic}/closeout-driver-result.json",
        f"{topic}/explicit-stage-manifest.json",
    }
    allowlist = {
        _relative_path(repo_root, raw, reason="stage_allowlist_path_invalid")
        for raw in raw_paths
    }
    if any(path == "docs/branding" or path.startswith("docs/branding/") for path in allowlist):
        raise CloseoutDriverRejection("branding_path_forbidden")
    return allowlist


def build_stage_manifest(
    repo_root: Path,
    *,
    head: str,
    allowlist: set[str],
    result_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Intersect machine Git state with the allowlist without touching the index."""

    worktree_tracked = _git_paths(repo_root, ["diff", "--name-only", "-z"])
    index_tracked = _git_paths(
        repo_root, ["diff", "--cached", "--name-only", "-z"]
    )
    untracked = _git_paths(
        repo_root, ["ls-files", "--others", "--exclude-standard", "-z"]
    )
    tracked = worktree_tracked | index_tracked
    unexpected_tracked = sorted(tracked - allowlist)
    if unexpected_tracked:
        raise CloseoutDriverRejection("unexpected_tracked_stage_path")
    fixed_outputs = {
        result_path.relative_to(repo_root.resolve()).as_posix(),
        manifest_path.relative_to(repo_root.resolve()).as_posix(),
    }
    paths = sorted(((tracked | untracked) & allowlist) | fixed_outputs)
    for relative in paths:
        if relative == "docs/branding" or relative.startswith("docs/branding/"):
            raise CloseoutDriverRejection("branding_path_forbidden")
        path = repo_root / relative
        if relative not in fixed_outputs and (not path.exists() or path.is_dir()):
            raise CloseoutDriverRejection("stage_path_not_existing_file")
    return {
        "schema_version": STAGE_MANIFEST_VERSION,
        "status": "passed",
        "source_head": head,
        "derivation": "admitted_intent_clockwork_contract_intersect_git_inventory",
        "paths": paths,
        "path_count": len(paths),
        "allowlist_path_count": len(allowlist),
        "tracked_path_count": len(tracked),
        "allowlisted_untracked_path_count": len(untracked & allowlist),
        "excluded_untracked_path_count": len(untracked - allowlist),
        "unexpected_tracked_paths": [],
        "git_add_invocations": 0,
        "git_index_mutations": 0,
        "docs_branding_included": False,
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_bound_closeout(
    repo_root: Path,
    *,
    intent_raw: Path,
    mode: str,
    runner: Runner = subprocess.run,
) -> dict[str, Any]:
    """Run the fixed closeout sequence; rehearsal is the only occupied use here."""

    repo_root = repo_root.resolve()
    intent_path = _intent_path(repo_root, intent_raw)
    intent = _load(intent_path)
    if intent.get("schema_version") != SEMANTIC_TICK_INTENT_VERSION:
        raise CloseoutDriverRejection("semantic_closeout_intent_required")
    contract = validate_contract(_load(CONTRACT))
    admitted = admit_tick_intent(repo_root, intent, contract)
    semantic_commands = admitted["command_manifest"]["commands"]
    head = resolve_full_head(repo_root, runner=runner)
    interpreter, attested = resolve_repository_interpreter(repo_root, runner=runner)
    index_before = _git_paths(
        repo_root, ["diff", "--cached", "--name-only", "-z"]
    )
    if index_before:
        raise CloseoutDriverRejection("clean_git_index_required")
    surface_before = _publication_surface(repo_root, contract)
    tick_flag = "--verify" if mode == "rehearse" else "--publish"
    if mode not in {"rehearse", "publish"}:
        raise CloseoutDriverRejection("driver_mode_invalid")
    relative_intent = intent_path.relative_to(repo_root).as_posix()
    tick_completed = _run_text(
        [
            str(interpreter),
            "-m",
            "scripts.ariadne_governance_clockwork_tick",
            tick_flag,
            "--intent",
            relative_intent,
        ],
        repo_root=repo_root,
        runner=runner,
    )
    tick_result = _parse_tick_result(tick_completed)
    inline_reading = capture_tick_reading(
        tick_result,
        mode=mode,
        semantic_command_count=len(semantic_commands),
    )
    surface_after_tick = _publication_surface(repo_root, contract)
    if mode == "rehearse" and surface_after_tick != surface_before:
        raise CloseoutDriverRejection("rehearsal_publication_surface_changed")
    tracked_before_tests = _tracked_status(repo_root, runner=runner)
    postpublication_command = [
        str(interpreter),
        "-m",
        "scripts.ariadne_provider_free_pytest",
        "--repo-root",
        repo_root.as_posix(),
        *POSTPUBLICATION_TESTS,
    ]
    tests = _run_text(
        postpublication_command,
        repo_root=repo_root,
        runner=runner,
    )
    if tests.returncode != 0:
        raise CloseoutDriverRejection("postpublication_tests_failed")
    tracked_after_tests = _tracked_status(repo_root, runner=runner)
    if tracked_after_tests != tracked_before_tests:
        raise CloseoutDriverRejection("postpublication_tests_created_tracked_drift")
    index_after_tests = _git_paths(
        repo_root, ["diff", "--cached", "--name-only", "-z"]
    )
    if index_after_tests != index_before:
        raise CloseoutDriverRejection("git_index_changed")

    topic = intent_path.parent
    result_path = topic / "closeout-driver-result.json"
    manifest_path = topic / "explicit-stage-manifest.json"
    result: dict[str, Any] = {
        "schema_version": RESULT_VERSION,
        "status": "passed",
        "mode": mode,
        "source_head": head,
        "interpreter": {
            "selected": interpreter.as_posix(),
            "attested": Path(attested).as_posix(),
            "caller_interpreter_ignored": True,
        },
        "semantic_verification": {
            "command_ids": [command["command_id"] for command in semantic_commands],
            "command_count": len(semantic_commands),
            "executed_command_count": tick_result["verification_facts"][
                "executed_command_count"
            ],
            "passed_command_count": tick_result["verification_facts"][
                "passed_command_count"
            ],
        },
        "inline_live_validation": inline_reading,
        "postpublication_verification": {
            "test_paths": list(POSTPUBLICATION_TESTS),
            "test_file_count": len(POSTPUBLICATION_TESTS),
            "exit_code": tests.returncode,
            "stdout_sha256": hashlib.sha256(tests.stdout.encode("utf-8")).hexdigest(),
            "stderr_sha256": hashlib.sha256(tests.stderr.encode("utf-8")).hexdigest(),
            "tracked_drift": 0,
        },
        "publication_surface_changed_file_count": sum(
            surface_before[path] != surface_after_tick[path] for path in surface_before
        ),
        "stage_manifest": manifest_path.relative_to(repo_root).as_posix(),
        "git_add_invocations": 0,
        "git_index_mutations": 0,
    }
    _write_json(result_path, result)
    allowlist = derive_allowlist(
        repo_root,
        intent_path=intent_path,
        admitted=admitted,
        contract=contract,
    )
    stage_manifest = build_stage_manifest(
        repo_root,
        head=head,
        allowlist=allowlist,
        result_path=result_path,
        manifest_path=manifest_path,
    )
    _write_json(manifest_path, stage_manifest)
    index_after_outputs = _git_paths(
        repo_root, ["diff", "--cached", "--name-only", "-z"]
    )
    if index_after_outputs != index_before:
        raise CloseoutDriverRejection("git_index_changed")
    result["stage_manifest_path_count"] = stage_manifest["path_count"]
    result["stage_manifest_sha256"] = hashlib.sha256(
        manifest_path.read_bytes()
    ).hexdigest()
    _write_json(result_path, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--rehearse", action="store_true")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--intent", required=True, type=Path)
    arguments = parser.parse_args(argv)
    result = run_bound_closeout(
        ROOT,
        intent_raw=arguments.intent,
        mode="rehearse" if arguments.rehearse else "publish",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cli(argv: list[str] | None = None) -> int:
    try:
        return main(argv)
    except CloseoutDriverRejection as error:
        print(
            json.dumps(
                {
                    "schema_version": RESULT_VERSION,
                    "status": "revision_required",
                    "reason": str(error),
                    "git_add_invocations": 0,
                },
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
