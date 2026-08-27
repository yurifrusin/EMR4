"""Fail-closed stock-Git execution and physical repository attestation.

The controller never trusts caller-selected Git administration paths.  Every
Git subprocess uses one resolved stock executable and a closed environment;
repository identities and authority-bearing bytes are then bound to the real
worktree, Git directories, index, and index blobs.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence


class TrustedGitError(ValueError):
    """A caller environment or repository substrate failed closed."""

    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


_HIGH_RISK_EXACT = {
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
_HIGH_RISK_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
_PASSTHROUGH_ENVIRONMENT = {
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
_REPARSE_FLAG = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
TRUSTED_GIT_COMMAND_OVERRIDES = (
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.ignoreStat=false",
)
_IDENTITY_COMMAND_OVERRIDES = (
    "core.fsmonitor=false",
    "core.ignoreStat=false",
)
_VISIBILITY_CONFIGURATION_KEYS = (
    "core.fsmonitor",
    "core.fsmonitorHookVersion",
    "core.ignoreStat",
)


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: object) -> str:
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def reject_high_risk_environment(environment: dict[str, str] | None = None) -> None:
    """Reject caller-controlled Git redirection/configuration before Git runs."""
    source = os.environ if environment is None else environment
    for name in source:
        upper = name.upper()
        if upper in _HIGH_RISK_EXACT or upper.startswith(_HIGH_RISK_PREFIXES):
            raise TrustedGitError("trusted_git_environment_forbidden")


def closed_git_environment(
    environment: dict[str, str] | None = None,
) -> dict[str, str]:
    """Return the only environment inherited by trusted Git subprocesses."""
    source = os.environ if environment is None else environment
    reject_high_risk_environment(source)
    closed = {
        name: value
        for name, value in source.items()
        if name.upper() in _PASSTHROUGH_ENVIRONMENT
    }
    closed.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "LC_ALL": "C",
        }
    )
    return closed


def resolve_stock_git() -> Path:
    """Resolve Git without consulting caller PATH ordering."""
    candidates = (
        Path("C:/Program Files/Git/cmd/git.exe"),
        Path("C:/Program Files/Git/bin/git.exe"),
        Path("C:/Program Files (x86)/Git/cmd/git.exe"),
        Path("/usr/bin/git"),
        Path("/usr/local/bin/git"),
    )
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
            observed = resolved.lstat()
        except OSError:
            continue
        if stat.S_ISREG(observed.st_mode) and not _is_reparse(observed):
            return resolved
    raise TrustedGitError("trusted_git_executable_unavailable")


def _is_reparse(observed: os.stat_result) -> bool:
    return bool(getattr(observed, "st_file_attributes", 0) & _REPARSE_FLAG)


def _validate_path_components(path: Path) -> None:
    resolved = path.absolute()
    parts = resolved.parts
    if not parts:
        raise TrustedGitError("trusted_git_path_invalid")
    current = Path(parts[0])
    for part in parts[1:]:
        current /= part
        try:
            observed = current.lstat()
        except OSError as error:
            raise TrustedGitError("trusted_git_path_missing") from error
        if current.is_symlink() or _is_reparse(observed):
            raise TrustedGitError("trusted_git_reparse_forbidden")


def _path_identity(path: Path, *, directory: bool | None = None) -> dict[str, Any]:
    _validate_path_components(path)
    try:
        resolved = path.resolve(strict=True)
        observed = resolved.lstat()
    except OSError as error:
        raise TrustedGitError("trusted_git_path_missing") from error
    if directory is True and not stat.S_ISDIR(observed.st_mode):
        raise TrustedGitError("trusted_git_path_type_invalid")
    if directory is False and not stat.S_ISREG(observed.st_mode):
        raise TrustedGitError("trusted_git_path_type_invalid")
    return {
        "resolved_path": resolved.as_posix(),
        "device": int(observed.st_dev),
        "inode": int(observed.st_ino),
        "mode": int(observed.st_mode),
        "size": int(observed.st_size),
        "modified_ns": int(observed.st_mtime_ns),
    }


def _stable_path_identity(
    path: Path, *, directory: bool | None = None
) -> dict[str, Any]:
    identity = _path_identity(path, directory=directory)
    return {key: identity[key] for key in ("resolved_path", "device", "inode", "mode")}


def _run(
    root: Path,
    args: Sequence[str],
    *,
    binary: bool,
    allow_failure: bool = False,
    timeout: int = 30,
) -> subprocess.CompletedProcess[Any]:
    git = resolve_stock_git()
    environment = closed_git_environment()
    try:
        completed = subprocess.run(  # noqa: S603
            [str(git), *TRUSTED_GIT_COMMAND_OVERRIDES, *args],
            cwd=root,
            env=environment,
            check=False,
            capture_output=True,
            text=not binary,
            encoding=None if binary else "utf-8",
            errors=None if binary else "replace",
            shell=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise TrustedGitError("trusted_git_execution_failed") from error
    if completed.returncode != 0 and not allow_failure:
        stderr = completed.stderr
        diagnostic = (
            stderr.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes)
            else str(stderr)
        ).casefold()
        if "bad boolean config value" in diagnostic and any(
            f"for '{key.casefold()}'" in diagnostic
            for key in _VISIBILITY_CONFIGURATION_KEYS
        ):
            raise TrustedGitError("trusted_git_configuration_forbidden")
        raise TrustedGitError("trusted_git_observation_failed")
    return completed


def run_git(root: Path, *args: str, timeout: int = 30) -> str:
    """Run Git through the trusted substrate and return stripped UTF-8 text."""
    return str(_run(root, args, binary=False, timeout=timeout).stdout).strip()


def run_git_bytes(root: Path, *args: str, timeout: int = 30) -> bytes:
    """Run Git through the trusted substrate without losing NUL delimiters."""
    return bytes(_run(root, args, binary=True, timeout=timeout).stdout)


def run_git_optional_bytes(
    root: Path, *args: str, timeout: int = 30
) -> tuple[int, bytes]:
    """Run a trusted Git command whose exit status is part of the observation."""
    completed = _run(
        root,
        args,
        binary=True,
        allow_failure=True,
        timeout=timeout,
    )
    return completed.returncode, bytes(completed.stdout)


def _optional_git(root: Path, *args: str) -> tuple[int, str]:
    completed = _run(root, args, binary=False, allow_failure=True)
    return completed.returncode, str(completed.stdout).strip()


def _absolute_git_path(root: Path, *args: str) -> Path:
    value = run_git(root, "rev-parse", "--path-format=absolute", *args)
    path = Path(value)
    if not path.is_absolute():
        raise TrustedGitError("trusted_git_administration_path_invalid")
    return path.resolve(strict=True)


def _parse_tagged_paths(payload: bytes) -> list[tuple[str, str]]:
    if not payload:
        return []
    fields = payload.split(b"\0")
    if fields[-1] != b"":
        raise TrustedGitError("trusted_git_index_inventory_invalid")
    rows: list[tuple[str, str]] = []
    for field in fields[:-1]:
        if len(field) < 3 or field[1:2] != b" ":
            raise TrustedGitError("trusted_git_index_inventory_invalid")
        try:
            rows.append((chr(field[0]), field[2:].decode("utf-8")))
        except UnicodeDecodeError as error:
            raise TrustedGitError("trusted_git_index_inventory_invalid") from error
    return rows


def _nul_config_values(payload: bytes) -> list[str]:
    fields = payload.split(b"\0")
    if fields[-1] != b"":
        raise TrustedGitError("trusted_git_configuration_forbidden")
    try:
        return [field.decode("utf-8") for field in fields[:-1]]
    except UnicodeDecodeError as error:
        raise TrustedGitError("trusted_git_configuration_forbidden") from error


def _repository_visibility_configuration(root: Path) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    worktree_extension = _run(
        root,
        (
            "config",
            "--local",
            "--type=bool",
            "--get",
            "extensions.worktreeConfig",
        ),
        binary=False,
        allow_failure=True,
    )
    if worktree_extension.returncode == 1:
        worktree_configuration_active = False
    elif worktree_extension.returncode == 0:
        extension_value = str(worktree_extension.stdout).strip()
        if extension_value not in {"true", "false"}:
            raise TrustedGitError("trusted_git_configuration_forbidden")
        worktree_configuration_active = extension_value == "true"
    else:
        raise TrustedGitError("trusted_git_configuration_forbidden")
    for scope in ("local", "worktree"):
        scoped: dict[str, Any] = {}
        for key in _VISIBILITY_CONFIGURATION_KEYS:
            if scope == "worktree" and not worktree_configuration_active:
                scoped[key] = {
                    "values": [],
                    "normalised_boolean_values": [],
                    "admitted": True,
                }
                continue
            raw = _run(
                root,
                ("config", f"--{scope}", "--includes", "--null", "--get-all", key),
                binary=True,
                allow_failure=True,
            )
            if raw.returncode == 1:
                values: list[str] = []
                normalised: list[str] = []
            elif raw.returncode == 0:
                values = _nul_config_values(bytes(raw.stdout))
                typed = _run(
                    root,
                    (
                        "config",
                        f"--{scope}",
                        "--includes",
                        "--type=bool",
                        "--null",
                        "--get-all",
                        key,
                    ),
                    binary=True,
                    allow_failure=True,
                )
                if typed.returncode != 0:
                    raise TrustedGitError("trusted_git_configuration_forbidden")
                normalised = _nul_config_values(bytes(typed.stdout))
                if len(normalised) != len(values) or any(
                    value != "false" for value in normalised
                ):
                    raise TrustedGitError("trusted_git_configuration_forbidden")
            else:
                raise TrustedGitError("trusted_git_configuration_forbidden")
            scoped[key] = {
                "values": values,
                "normalised_boolean_values": normalised,
                "admitted": True,
            }
        observed[scope] = scoped
    observed["worktree_configuration_active"] = worktree_configuration_active
    return observed


def _reject_index_visibility_controls(root: Path) -> dict[str, Any]:
    fsmonitor = _parse_tagged_paths(run_git_bytes(root, "ls-files", "-f", "-z"))
    verbose = _parse_tagged_paths(run_git_bytes(root, "ls-files", "-v", "-z"))
    typed = _parse_tagged_paths(run_git_bytes(root, "ls-files", "-t", "-z"))
    if (
        any(tag.islower() for tag, _path in fsmonitor)
        or any(tag.islower() for tag, _path in verbose)
        or any(tag == "S" for tag, _path in typed)
    ):
        raise TrustedGitError("trusted_git_index_flags_forbidden")
    sparse_status, sparse = _optional_git(
        root, "config", "--type=bool", "--get", "core.sparseCheckout"
    )
    if sparse_status == 0 and sparse == "true":
        raise TrustedGitError("trusted_git_sparse_index_forbidden")
    if sparse_status not in {0, 1}:
        raise TrustedGitError("trusted_git_index_observation_failed")
    split = run_git(root, "rev-parse", "--shared-index-path")
    if split:
        raise TrustedGitError("trusted_git_split_index_forbidden")
    rows = sorted(path for _tag, path in typed)
    return {
        "entry_count": len(rows),
        "tracked_paths_sha256": _canonical_digest(rows),
        "assume_unchanged_count": 0,
        "fsmonitor_valid_count": 0,
        "skip_worktree_count": 0,
        "sparse_checkout": False,
        "split_index": False,
    }


def _normalise_relative(path: str | Path) -> str:
    text = path.as_posix() if isinstance(path, Path) else path.replace("\\", "/")
    pure = PurePosixPath(text)
    if (
        pure.is_absolute()
        or not pure.parts
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise TrustedGitError("trusted_git_attested_path_invalid")
    return pure.as_posix()


def _index_entry(root: Path, relative: str) -> tuple[str, str]:
    payload = run_git_bytes(root, "ls-files", "--stage", "-z", "--", relative)
    fields = payload.split(b"\0")
    if len(fields) != 2 or fields[-1] != b"" or b"\t" not in fields[0]:
        raise TrustedGitError("trusted_git_index_entry_missing")
    header, raw_path = fields[0].split(b"\t", 1)
    try:
        mode, object_id, stage = header.decode("ascii").split(" ")
        observed_path = raw_path.decode("utf-8").replace("\\", "/")
    except (UnicodeDecodeError, ValueError) as error:
        raise TrustedGitError("trusted_git_index_entry_invalid") from error
    if stage != "0" or observed_path != relative or mode not in {"100644", "100755"}:
        raise TrustedGitError("trusted_git_index_entry_invalid")
    return mode, object_id


def _tree_entry(root: Path, commit: str, relative: str) -> tuple[str, str]:
    payload = run_git_bytes(root, "ls-tree", "-z", commit, "--", relative)
    fields = payload.split(b"\0")
    if len(fields) != 2 or fields[-1] != b"" or b"\t" not in fields[0]:
        raise TrustedGitError("trusted_git_tree_entry_missing")
    header, raw_path = fields[0].split(b"\t", 1)
    try:
        mode, object_type, object_id = header.decode("ascii").split(" ")
        observed_path = raw_path.decode("utf-8").replace("\\", "/")
    except (UnicodeDecodeError, ValueError) as error:
        raise TrustedGitError("trusted_git_tree_entry_invalid") from error
    if object_type != "blob" or observed_path != relative:
        raise TrustedGitError("trusted_git_tree_entry_invalid")
    return mode, object_id


def _index_entries(root: Path, paths: Sequence[str]) -> dict[str, tuple[str, str]]:
    payload = run_git_bytes(root, "ls-files", "--stage", "-z", "--", *paths)
    fields = payload.split(b"\0")
    if fields[-1] != b"":
        raise TrustedGitError("trusted_git_index_entry_invalid")
    result: dict[str, tuple[str, str]] = {}
    for field in fields[:-1]:
        if b"\t" not in field:
            raise TrustedGitError("trusted_git_index_entry_invalid")
        header, raw_path = field.split(b"\t", 1)
        try:
            mode, object_id, stage = header.decode("ascii").split(" ")
            relative = raw_path.decode("utf-8").replace("\\", "/")
        except (UnicodeDecodeError, ValueError) as error:
            raise TrustedGitError("trusted_git_index_entry_invalid") from error
        if stage != "0" or mode not in {"100644", "100755"} or relative in result:
            raise TrustedGitError("trusted_git_index_entry_invalid")
        result[relative] = (mode, object_id)
    if set(result) != set(paths):
        raise TrustedGitError("trusted_git_index_entry_missing")
    return result


def _tree_entries(
    root: Path, commit: str, paths: Sequence[str]
) -> dict[str, tuple[str, str]]:
    payload = run_git_bytes(root, "ls-tree", "-r", "-z", commit, "--", *paths)
    fields = payload.split(b"\0")
    if fields[-1] != b"":
        raise TrustedGitError("trusted_git_tree_entry_invalid")
    result: dict[str, tuple[str, str]] = {}
    for field in fields[:-1]:
        if b"\t" not in field:
            raise TrustedGitError("trusted_git_tree_entry_invalid")
        header, raw_path = field.split(b"\t", 1)
        try:
            mode, object_type, object_id = header.decode("ascii").split(" ")
            relative = raw_path.decode("utf-8").replace("\\", "/")
        except (UnicodeDecodeError, ValueError) as error:
            raise TrustedGitError("trusted_git_tree_entry_invalid") from error
        if object_type != "blob" or relative in result:
            raise TrustedGitError("trusted_git_tree_entry_invalid")
        result[relative] = (mode, object_id)
    if set(result) != set(paths):
        raise TrustedGitError("trusted_git_tree_entry_missing")
    return result


def _git_blob_object_id(payload: bytes, object_format: str) -> str:
    framed = b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
    if object_format == "sha1":
        return hashlib.sha1(framed, usedforsecurity=False).hexdigest()  # noqa: S324
    if object_format == "sha256":
        return hashlib.sha256(framed).hexdigest()
    raise TrustedGitError("trusted_git_object_format_invalid")


def _attest_paths(
    root: Path, paths: Iterable[str | Path], *, expected_commit: str | None
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    relative_paths = sorted({_normalise_relative(path) for path in paths})
    index_entries = _index_entries(root, relative_paths)
    tree_entries = (
        _tree_entries(root, expected_commit, relative_paths)
        if expected_commit is not None
        else None
    )
    object_format = run_git(root, "rev-parse", "--show-object-format")
    for relative in relative_paths:
        mode, object_id = index_entries[relative]
        if tree_entries is not None and tree_entries[relative] != (mode, object_id):
            raise TrustedGitError("trusted_git_index_tree_binding_failed")
        physical = root / Path(*PurePosixPath(relative).parts)
        _validate_path_components(physical)
        try:
            observed = physical.lstat()
            payload = physical.read_bytes()
        except OSError as error:
            raise TrustedGitError("trusted_git_physical_source_missing") from error
        if (
            not stat.S_ISREG(observed.st_mode)
            or physical.is_symlink()
            or _is_reparse(observed)
        ):
            raise TrustedGitError("trusted_git_physical_source_not_regular")
        if _git_blob_object_id(payload, object_format) != object_id:
            raise TrustedGitError("trusted_git_physical_bytes_mismatch")
        rows.append(
            {
                "path": relative,
                "mode": mode,
                "object_id": object_id,
                "physical_sha256": _sha256_bytes(payload),
                "size": len(payload),
            }
        )
    return {
        "path_count": len(rows),
        "paths": rows,
        "attested_paths_sha256": _canonical_digest(rows),
    }


def indexed_paths_under(root: Path, prefixes: Iterable[str | Path]) -> list[str]:
    """List index paths under closed authority roots without filesystem globs."""
    paths: set[str] = set()
    for prefix in prefixes:
        normalised = _normalise_relative(prefix)
        payload = run_git_bytes(root, "ls-files", "--cached", "-z", "--", normalised)
        fields = payload.split(b"\0")
        if fields[-1] != b"":
            raise TrustedGitError("trusted_git_index_inventory_invalid")
        try:
            paths.update(
                field.decode("utf-8").replace("\\", "/") for field in fields[:-1]
            )
        except UnicodeDecodeError as error:
            raise TrustedGitError("trusted_git_index_inventory_invalid") from error
    return sorted(paths)


def attest_repository(
    root: Path,
    *,
    attested_paths: Iterable[str | Path],
    expected_commit: str | None = None,
) -> dict[str, Any]:
    """Bind a real worktree, Git administration, index, and physical bytes."""
    reject_high_risk_environment()
    _validate_path_components(root.absolute())
    requested = root.resolve(strict=True)
    worktree = Path(run_git(requested, "rev-parse", "--show-toplevel")).resolve(
        strict=True
    )
    if requested != worktree:
        raise TrustedGitError("trusted_git_worktree_mismatch")
    gitdir = _absolute_git_path(worktree, "--git-dir")
    commondir = _absolute_git_path(worktree, "--git-common-dir")
    index = _absolute_git_path(worktree, "--git-path", "index")
    repository_configuration = _repository_visibility_configuration(worktree)
    flags = _reject_index_visibility_controls(worktree)
    head = run_git(worktree, "rev-parse", "HEAD")
    head_tree = run_git(worktree, "rev-parse", "HEAD^{tree}")
    index_tree = run_git(worktree, "write-tree")
    if expected_commit is not None and head != expected_commit:
        raise TrustedGitError("trusted_git_expected_commit_mismatch")
    git = resolve_stock_git()
    executable_payload = git.read_bytes()
    admin_files: list[dict[str, Any]] = []
    for candidate in (commondir / "config", gitdir / "config.worktree"):
        if candidate.exists():
            identity = _stable_path_identity(candidate, directory=False)
            identity["sha256"] = _sha256_bytes(candidate.read_bytes())
            admin_files.append(identity)
    attestation = _attest_paths(
        worktree, attested_paths, expected_commit=expected_commit
    )
    identity: dict[str, Any] = {
        "schema_version": "ariadne.trusted_git_identity.v1",
        "git_executable": {
            **_stable_path_identity(git, directory=False),
            "size": len(executable_payload),
            "sha256": _sha256_bytes(executable_payload),
        },
        "worktree": _stable_path_identity(worktree, directory=True),
        "gitdir": _stable_path_identity(gitdir, directory=True),
        "commondir": _stable_path_identity(commondir, directory=True),
        "index": {
            key: value
            for key, value in _stable_path_identity(index, directory=False).items()
            if key in {"resolved_path", "mode"}
        },
        "head": head,
        "head_tree": head_tree,
        "index_tree": index_tree,
        "index_visibility": flags,
        "command_overrides": list(_IDENTITY_COMMAND_OVERRIDES),
        "repository_configuration": repository_configuration,
        "git_administration_files": admin_files,
        "physical_attestation": attestation,
        "no_replace_objects": True,
        "closed_environment": True,
        "trusted_git_identity_sha256": "",
    }
    identity["trusted_git_identity_sha256"] = _canonical_digest(identity)
    return identity
