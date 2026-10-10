"""Build and run only a reviewed literal ordinary verification selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).absolute().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.python_source_state import (  # noqa: E402
    COMPLETE_PROFILES,
    SourceStateError,
    load_complete_context,
    load_complete_selection,
    load_source_state,
    validate_selection,
)
from scripts.verification_runtime import (  # noqa: E402
    LAUNCHER_TIMEOUT_EXIT,
    TIMEOUT_SECONDS,
    VerificationCommand,
    run_commands,
)


PROFILES = ("ci-correctness", "ci-lint", "ci-bandit", "ci-security")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def build_commands(profile: str, state: dict) -> list[VerificationCommand]:
    """Build exact argv only; source bytes were authenticated by the loader."""
    if profile not in PROFILES:
        raise SourceStateError("unsupported_verification_profile")
    validated = validate_selection({
        key: value for key, value in state.items()
        if key not in {"selected_bytes", "selection_path", "selection_sha256"}
    })
    selection = state.get("selection_path")
    digest = state.get("selection_sha256")
    if (type(selection) is not str or not selection
            or not Path(selection).is_absolute()
            or any(part in {".", ".."} for part in Path(selection).parts)
            or type(digest) is not str
            or HEX64.fullmatch(digest) is None):
        raise SourceStateError("unbound_verification_selection")
    python = sys.executable
    common = ["--selection", selection, "--selection-sha256", digest]
    phases = validated["phases"]
    configs = validated["configs"]
    compile_command = VerificationCommand(
        "selected Python 3.11 compilation",
        [python, "-B", "scripts/python_source_state.py", *common,
         "--require-target-runtime"],
        TIMEOUT_SECONDS["tool"],
    )
    ruff = VerificationCommand(
        "selected Ruff E9/F401",
        [python, "-B", "-m", "ruff", "check", "--config", configs["ruff"],
         "--no-cache", *phases["ruff"]],
        TIMEOUT_SECONDS["tool"],
    )
    leakage = VerificationCommand(
        "selected historical diary leakage lint",
        [python, "-B", "scripts/historical_diary_leakage_lint.py", *common],
        TIMEOUT_SECONDS["tool"],
    )
    bandit = VerificationCommand(
        "selected Bandit report and review gate",
        [python, "-B", "scripts/security_bandit_gate.py", *common],
        TIMEOUT_SECONDS["tool"],
    )
    pytest = VerificationCommand(
        "selected ordinary correctness nodes",
        [python, "-B", "-m", "pytest", "--noconftest", "-c", configs["pytest"],
         "-o", "addopts=", "-p", "no:cacheprovider", *phases["tests"]],
        TIMEOUT_SECONDS["focused_tests"],
    )
    if profile == "ci-correctness":
        return [compile_command, ruff, leakage, pytest]
    if profile == "ci-lint":
        return [ruff, leakage]
    if profile == "ci-bandit":
        return [bandit]
    return [ruff, leakage, bandit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=(*PROFILES, "ci-complete"), required=True)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--selection-sha256", required=True)
    parser.add_argument("--trusted-context")
    parser.add_argument("--trusted-context-sha256")
    parser.add_argument(
        "--require-complete", action="store_true",
        help="Refuse bounded coverage before reading selected sources or running checks",
    )
    args = parser.parse_args(argv)
    coverage = None
    try:
        if args.profile == "ci-complete":
            if (not args.require_complete or not args.trusted_context
                    or not args.trusted_context_sha256):
                raise SourceStateError("complete_trusted_context_required")
            trusted = load_complete_context(
                args.trusted_context, sha256=args.trusted_context_sha256,
                repo_root=REPO_ROOT,
            )
            loaded = load_complete_selection(
                args.selection, selection_sha256=args.selection_sha256,
                trusted_context=trusted, repo_root=REPO_ROOT,
            )
            state, coverage = loaded["bounded_state"], loaded["coverage"]
            commands = [command for profile in COMPLETE_PROFILES
                        for command in build_commands(profile, state)]
        else:
            if args.trusted_context or args.trusted_context_sha256:
                raise SourceStateError("trusted_context_requires_complete_profile")
            state = load_source_state(args.selection,
                                      manifest_sha256=args.selection_sha256,
                                      repo_root=REPO_ROOT,
                                      require_complete=args.require_complete)
            commands = build_commands(args.profile, state)
    except SourceStateError as exc:
        print(f"[verification_selection_failure] {exc}", file=sys.stderr)
        return 2
    # The reviewed parent supervisor must supply the clean base environment.
    # These overlays close the named pytest/cache defaults within that boundary.
    clean_overlays = {
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "PYTEST_ADDOPTS": "",
        "PYTHONPATH": "",
        "PYTHONDONTWRITEBYTECODE": "1",
        "RUFF_NO_CACHE": "1",
    }
    if coverage is None:
        return run_commands(commands, cwd=REPO_ROOT, env=clean_overlays)

    # Full proof precedes dispatch. Continue finished-child failures only
    # within the admitted effect boundary; return124 or runner uncertainty
    # stops dispatch and leaves final cleanup/quiescence to the reviewed parent.
    result = 0
    outcomes = []
    stop_reason = None
    for index, command in enumerate(commands):
        try:
            command_result = run_commands([command], cwd=REPO_ROOT,
                                          env=clean_overlays)
            outcome = ("returned_124" if command_result == LAUNCHER_TIMEOUT_EXIT else
                       "passed" if command_result == 0 else "failed")
            if command_result == LAUNCHER_TIMEOUT_EXIT:
                # A child may itself exit124. Preserve the raw return and
                # diagnostics without claiming launcher-timeout provenance.
                stop_reason = "return124_cleanup_unresolved"
        except OSError as exc:
            command_result = 2
            outcome = "runner_oserror"
            stop_reason = "runner_oserror_cleanup_unresolved"
            print(f"[runner_failure] {command.label}: {type(exc).__name__}",
                  file=sys.stderr, flush=True)
        outcomes.append({"label": command.label, "exit_code": command_result,
                         "outcome": outcome})
        if result == 0 and command_result != 0:
            result = command_result
        if stop_reason is not None:
            skipped = ("not_attempted_after_return124"
                       if command_result == LAUNCHER_TIMEOUT_EXIT else
                       "not_attempted_after_runner_oserror")
            outcomes.extend({"label": remaining.label, "exit_code": None,
                             "outcome": skipped}
                            for remaining in commands[index + 1:])
            break
    print(json.dumps({"status": "complete_required_command_outcomes",
                      "aggregate_exit_code": result,
                      "stop_reason": stop_reason,
                      "commands": outcomes}, sort_keys=True), flush=True)
    if result == 0:
        print(json.dumps({"status": "complete_required_verification_passed",
                          "coverage": coverage}, sort_keys=True))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
