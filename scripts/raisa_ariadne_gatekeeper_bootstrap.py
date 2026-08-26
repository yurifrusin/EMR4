"""Isolated stdlib bootstrap for the transition-pinned programme gatekeeper.

Invoke only as ``python -I -B <this-file> <evaluate|commit|push> ...``.  No
repository-local module is imported until this bootstrap proves that its own
Git source is exact and contains zero ordinary or ignored additions.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath


_HIGH_RISK_GIT_ENV = {
    "GIT_DIR",
    "GIT_COMMON_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_REPLACE_REF_BASE",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS",
    "GIT_EXEC_PATH",
    "GIT_SHALLOW_FILE",
    "GIT_SSL_NO_VERIFY",
}
_HIGH_RISK_GIT_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
_SAFE_ENV = {
    "ALL_PROXY",
    "APPDATA",
    "COMSPEC",
    "HOMEDRIVE",
    "HOMEPATH",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "LOCALAPPDATA",
    "NO_PROXY",
    "PATH",
    "PATHEXT",
    "PROGRAMDATA",
    "SYSTEMDRIVE",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
    "USERDOMAIN",
    "USERNAME",
    "USERPROFILE",
    "WINDIR",
}
_SOURCE_MODULES = (
    "orchestration_harness/__init__.py",
    "orchestration_harness/trusted_git.py",
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
    "scripts/raisa_ariadne_pinned_gatekeeper.py",
)


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


def _reject_high_risk_environment() -> None:
    for name in os.environ:
        upper = name.upper()
        if upper in _HIGH_RISK_GIT_ENV or upper.startswith(_HIGH_RISK_GIT_PREFIXES):
            raise RuntimeError("trusted Git environment forbidden")


def _stock_git() -> Path:
    candidates = (
        Path("C:/Program Files/Git/cmd/git.exe"),
        Path("C:/Program Files/Git/bin/git.exe"),
        Path("C:/Program Files (x86)/Git/cmd/git.exe"),
        Path("/usr/bin/git"),
        Path("/usr/local/bin/git"),
    )
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
            observed = resolved.lstat()
        except OSError:
            continue
        if stat.S_ISREG(observed.st_mode) and not (
            getattr(observed, "st_file_attributes", 0) & reparse_flag
        ):
            return resolved
    raise RuntimeError("stock Git unavailable")


def _git_environment() -> dict[str, str]:
    _reject_high_risk_environment()
    environment = {
        name: value for name, value in os.environ.items() if name.upper() in _SAFE_ENV
    }
    environment.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "LC_ALL": "C",
        }
    )
    return environment


def _git(root: Path, *args: str, allow_failure: bool = False) -> bytes:
    completed = subprocess.run(  # noqa: S603
        [str(_stock_git()), *args],
        cwd=root,
        env=_git_environment(),
        check=False,
        capture_output=True,
        shell=False,
        timeout=30,
    )
    if completed.returncode != 0 and not allow_failure:
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


def _reject_index_visibility_controls(root: Path) -> None:
    for mode in ("-v", "-t"):
        payload = _git(root, "ls-files", mode, "-z")
        fields = payload.split(b"\0")
        if fields[-1] != b"":
            raise RuntimeError("index inventory invalid")
        for field in fields[:-1]:
            if len(field) < 3 or field[1:2] != b" ":
                raise RuntimeError("index inventory invalid")
            tag = chr(field[0])
            if (mode == "-v" and tag.islower()) or (mode == "-t" and tag == "S"):
                raise RuntimeError("index visibility flags forbidden")
    sparse = (
        _git(
            root,
            "config",
            "--type=bool",
            "--get",
            "core.sparseCheckout",
            allow_failure=True,
        )
        .decode()
        .strip()
    )
    if sparse == "true":
        raise RuntimeError("sparse index forbidden")
    if _git(root, "rev-parse", "--shared-index-path").strip():
        raise RuntimeError("split index forbidden")


def _attest_source_module(root: Path, expected_commit: str, relative: str) -> None:
    _validate_components(root, relative)
    stage = _git(root, "ls-files", "--stage", "-z", "--", relative)
    tree = _git(root, "ls-tree", "-z", expected_commit, "--", relative)
    stage_fields = stage.split(b"\0")
    tree_fields = tree.split(b"\0")
    if (
        len(stage_fields) != 2
        or stage_fields[-1] != b""
        or len(tree_fields) != 2
        or tree_fields[-1] != b""
        or b"\t" not in stage_fields[0]
        or b"\t" not in tree_fields[0]
    ):
        raise RuntimeError("source index binding invalid")
    stage_header, stage_path = stage_fields[0].split(b"\t", 1)
    tree_header, tree_path = tree_fields[0].split(b"\t", 1)
    stage_parts = stage_header.decode("ascii").split(" ")
    tree_parts = tree_header.decode("ascii").split(" ")
    if (
        len(stage_parts) != 3
        or len(tree_parts) != 3
        or stage_parts[2] != "0"
        or tree_parts[1] != "blob"
        or stage_parts[:2] != [tree_parts[0], tree_parts[2]]
        or stage_path.decode("utf-8").replace("\\", "/") != relative
        or tree_path.decode("utf-8").replace("\\", "/") != relative
    ):
        raise RuntimeError("source index binding invalid")
    physical = (root / Path(*PurePosixPath(relative).parts)).read_bytes()
    blob = _git(root, "cat-file", "blob", stage_parts[1])
    if physical != blob:
        raise RuntimeError("source physical bytes mismatch")


def _bootstrap_source() -> tuple[Path, str, str]:
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError("bootstrap flags invalid")
    _reject_high_risk_environment()
    script = Path(__file__).absolute()
    gatekeeper_root = script.parents[1]
    _validate_components(
        gatekeeper_root, script.relative_to(gatekeeper_root).as_posix()
    )
    observed_root = Path(
        _git(gatekeeper_root, "rev-parse", "--show-toplevel").decode().strip()
    ).resolve(strict=True)
    if observed_root != gatekeeper_root.resolve(strict=True):
        raise RuntimeError("worktree mismatch")
    _reject_index_visibility_controls(gatekeeper_root)
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
    for relative in _SOURCE_MODULES:
        _attest_source_module(gatekeeper_root, expected_commit, relative)
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
            "trusted Git environment forbidden": "trusted_git_environment_forbidden",
            "index visibility flags forbidden": "trusted_git_index_flags_forbidden",
            "sparse index forbidden": "trusted_git_sparse_index_forbidden",
            "split index forbidden": "trusted_git_split_index_forbidden",
            "source physical bytes mismatch": "trusted_git_physical_bytes_mismatch",
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
