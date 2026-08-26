"""Isolated stdlib bootstrap for the transition-pinned programme gatekeeper.

Invoke only as ``python -I -B <this-file> <evaluate|commit|push> ...``.  No
repository-local module is imported until this bootstrap proves that its own
Git source is exact and contains zero ordinary or ignored additions.
"""

from __future__ import annotations

import json
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath


def _blocked(reason: str) -> int:
    print(
        json.dumps(
            {
                "schema_version": "ariadne.pinned_programme_gatekeeper_decision.v1",
                "admitted": False,
                "reason_codes": [reason],
                "bootstrap_isolated": bool(sys.flags.isolated),
                "bootstrap_no_bytecode": bool(sys.dont_write_bytecode),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 2


def _git(root: Path, *args: str) -> bytes:
    completed = subprocess.run(  # noqa: S603
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        shell=False,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError("git observation failed")
    return completed.stdout


def _nul_paths(payload: bytes) -> list[str]:
    if not payload:
        return []
    fields = payload.split(b"\0")
    if fields[-1] != b"":
        raise RuntimeError("NUL inventory invalid")
    return [field.decode("utf-8").replace("\\", "/") for field in fields[:-1]]


def _validate_components(root: Path, path: str) -> None:
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    candidate = root
    for component in PurePosixPath(path).parts:
        candidate = candidate / component
        observed = candidate.lstat()
        if candidate.is_symlink() or (
            getattr(observed, "st_file_attributes", 0) & reparse_flag
        ):
            raise RuntimeError("reparse component")


def _argument_value(name: str) -> str:
    try:
        return sys.argv[sys.argv.index(name) + 1]
    except (ValueError, IndexError) as error:
        raise RuntimeError(f"missing {name}") from error


def _bootstrap_source() -> tuple[Path, str, str]:
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError("bootstrap flags invalid")
    script = Path(__file__).absolute()
    gatekeeper_root = script.parents[1]
    _validate_components(
        gatekeeper_root, script.relative_to(gatekeeper_root).as_posix()
    )
    tracked_dirty = _git(
        gatekeeper_root, "status", "--porcelain", "--untracked-files=no"
    )
    ordinary = _git(gatekeeper_root, "ls-files", "--others", "--exclude-standard", "-z")
    ignored = _git(
        gatekeeper_root,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
    )
    if tracked_dirty or ordinary or ignored:
        raise RuntimeError("source not clean")
    for path in _nul_paths(_git(gatekeeper_root, "ls-files", "--cached", "-z")):
        candidate = gatekeeper_root / Path(*PurePosixPath(path).parts)
        if candidate.exists() or candidate.is_symlink():
            _validate_components(gatekeeper_root, path)
    source_commit = _git(gatekeeper_root, "rev-parse", "HEAD").decode().strip()
    source_tree = _git(gatekeeper_root, "rev-parse", "HEAD^{tree}").decode().strip()
    expected_commit = _argument_value("--expected-source-commit")
    expected_tree = _argument_value("--expected-source-tree")
    if expected_commit != source_commit or expected_tree != source_tree:
        raise RuntimeError("source not transition pinned")
    return gatekeeper_root, source_commit, source_tree


def _remove_bootstrap_bindings() -> None:
    for name in ("--expected-source-commit", "--expected-source-tree"):
        offset = sys.argv.index(name)
        del sys.argv[offset : offset + 2]


def main() -> int:
    try:
        gatekeeper_root, _source_commit, _source_tree = _bootstrap_source()
    except (
        OSError,
        UnicodeError,
        ValueError,
        RuntimeError,
        subprocess.TimeoutExpired,
    ) as error:
        reason = {
            "bootstrap flags invalid": "gatekeeper_bootstrap_flags_invalid",
            "source not clean": "gatekeeper_bootstrap_source_not_clean",
            "source not transition pinned": "gatekeeper_bootstrap_source_not_transition_pinned",
        }.get(str(error), "gatekeeper_bootstrap_validation_failed")
        return _blocked(reason)
    _remove_bootstrap_bindings()
    sys.path.insert(0, str(gatekeeper_root))
    try:
        from orchestration_harness.programme_admission import ProgrammeAdmissionError
        from scripts.raisa_ariadne_pinned_gatekeeper import main as gatekeeper_main

        return gatekeeper_main()
    except ProgrammeAdmissionError as error:
        return _blocked(error.reason_code)


if __name__ == "__main__":
    raise SystemExit(main())
