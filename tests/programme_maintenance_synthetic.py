"""Complete, newly authored Git fixtures for maintenance-core tests.

Only caller-supplied bytes enter these repositories.  This helper neither loads
EMR4 policy nor reproduces its historical authority graph.  Its Git operations
are real; admission and whole-source attestation belong to the calling tests.
"""

from __future__ import annotations

import os
import re
import stat
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


_SHA1 = re.compile(r"[0-9a-f]{40}\Z")
_BRANCH = re.compile(r"[a-z][a-z0-9_-]*(?:/[a-z][a-z0-9_-]*)*\Z")
_DATE = "2001-01-01T00:00:00+00:00"
_ZERO_SHA = "0" * 40
_REPARSE_FLAG = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_DEVICE_NAME = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?\Z", re.I)


class SyntheticGitError(ValueError):
    """An authored fixture failed its explicit path or Git invariant."""


def _validated_files(files: Mapping[str, bytes]) -> dict[str, bytes]:
    if not isinstance(files, Mapping) or not files:
        raise SyntheticGitError("synthetic_file_map_required")
    result: dict[str, bytes] = {}
    spellings: dict[str, str] = {}
    directories: set[str] = set()
    for relative, payload in files.items():
        if not isinstance(relative, str) or not relative or type(payload) is not bytes:
            raise SyntheticGitError("synthetic_file_entry_invalid")
        if "\\" in relative or relative.startswith("/"):
            raise SyntheticGitError("synthetic_path_not_relative_posix")
        parts = relative.split("/")
        for index, part in enumerate(parts, 1):
            if (
                part in {"", ".", ".."}
                or part.casefold() == ".git"
                or part.endswith((".", " "))
                or any(
                    ord(character) < 32 or character in '<>:"|?*' for character in part
                )
                or _DEVICE_NAME.fullmatch(part)
            ):
                raise SyntheticGitError("synthetic_path_component_invalid")
            prefix = "/".join(parts[:index])
            prior = spellings.setdefault(prefix.casefold(), prefix)
            if prior != prefix:
                raise SyntheticGitError("synthetic_path_case_alias")
            if index < len(parts):
                directories.add(prefix)
        result[relative] = payload
    if directories.intersection(result):
        raise SyntheticGitError("synthetic_file_directory_collision")
    return result


def _plain_path(path: Path, *, directory: bool) -> None:
    """Check explicit components without following a substituted link."""
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        observed = current.lstat()
        if stat.S_ISLNK(observed.st_mode) or (
            getattr(observed, "st_file_attributes", 0) & _REPARSE_FLAG
        ):
            raise SyntheticGitError("synthetic_link_or_reparse_forbidden")
    observed = path.lstat()
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected(observed.st_mode):
        raise SyntheticGitError("synthetic_path_type_invalid")


def _new_directory(path: Path) -> Path:
    absolute = path.absolute()
    _plain_path(absolute.parent, directory=True)
    absolute.mkdir(exist_ok=False)
    _plain_path(absolute, directory=True)
    return absolute


def _stock_git() -> Path:
    candidates = (
        (
            Path("C:/Program Files/Git/cmd/git.exe"),
            Path("C:/Program Files/Git/bin/git.exe"),
        )
        if os.name == "nt"
        else (Path("/usr/bin/git"), Path("/usr/local/bin/git"))
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve(strict=True)
    raise SyntheticGitError("synthetic_stock_git_unavailable")


def _environment() -> dict[str, str]:
    allowed = {
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "TEMP",
        "TMP",
        "TMPDIR",
        "SYSTEMDRIVE",
    }
    environment = {
        key: value for key, value in os.environ.items() if key.upper() in allowed
    }
    environment.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "Authored Synthetic Fixture",
            "GIT_AUTHOR_EMAIL": "synthetic@example.invalid",
            "GIT_COMMITTER_NAME": "Authored Synthetic Fixture",
            "GIT_COMMITTER_EMAIL": "synthetic@example.invalid",
            "GIT_AUTHOR_DATE": _DATE,
            "GIT_COMMITTER_DATE": _DATE,
            "LC_ALL": "C",
        }
    )
    return environment


def _git(root: Path, *args: str, payload: bytes | None = None) -> bytes:
    _plain_path(root, directory=True)
    environment = _environment()
    # A damaged fixture must never make Git discover a repository above it.
    environment["GIT_CEILING_DIRECTORIES"] = str(root.parent)
    completed = subprocess.run(
        [
            str(_stock_git()),
            "--literal-pathspecs",
            "-c",
            "protocol.allow=never",
            "-c",
            "protocol.file.allow=always",
            "-c",
            "core.autocrlf=false",
            "-c",
            "core.fsmonitor=false",
            "-c",
            "commit.gpgSign=false",
            "-c",
            "push.gpgSign=false",
            "-c",
            "push.recurseSubmodules=no",
            *args,
        ],
        cwd=root,
        env=environment,
        input=payload,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if completed.returncode:
        # Keep supplied source bytes and arbitrary Git stderr out of diagnostics.
        raise SyntheticGitError(
            f"synthetic_git_failed:{args[0]}:{completed.returncode}"
        )
    return completed.stdout


def _oid(payload: bytes) -> str:
    value = payload.decode("ascii").strip()
    if _SHA1.fullmatch(value) is None:
        raise SyntheticGitError("synthetic_git_object_id_invalid")
    return value


def _initialize(path: Path, branch: str, *, bare: bool = False) -> Path:
    root = _new_directory(path)
    args = ["init", "--quiet", "--template=", "--object-format=sha1", "-b", branch]
    if bare:
        args.append("--bare")
    _git(root, *args)
    administration = root if bare else root / ".git"
    _plain_path(administration, directory=True)
    if (administration / "hooks").exists():
        raise SyntheticGitError("synthetic_hooks_not_absent")
    # These settings belong only to the repository just created above.
    for key, value in (
        ("user.name", "Authored Synthetic Fixture"),
        ("user.email", "synthetic@example.invalid"),
        ("core.autocrlf", "false"),
        ("core.fileMode", "false"),
        ("commit.gpgSign", "false"),
    ):
        _git(root, "config", "--local", key, value)
    return root


@dataclass(frozen=True)
class SyntheticCommit:
    sha: str
    tree: str
    parent: str | None


@dataclass
class SyntheticRepository:
    """A complete fixture created by ``create_synthetic_repository``."""

    root: Path
    branch: str
    files: dict[str, bytes]
    initial_commit: SyntheticCommit | None = None
    origin: Path | None = None

    @property
    def branch_ref(self) -> str:
        return f"refs/heads/{self.branch}"

    def head(self) -> str:
        return _oid(_git(self.root, "rev-parse", "--verify", "HEAD"))

    def index_tree(self) -> str:
        return _oid(_git(self.root, "write-tree"))

    def assert_file_inventory(self) -> None:
        """Compare only this new fixture's complete physical/index inventory."""
        _plain_path(self.root / ".git", directory=True)
        expected = {path.encode("utf-8") for path in self.files}
        tracked = set(_git(self.root, "ls-files", "--cached", "-z").split(b"\0")) - {
            b""
        }
        if tracked != expected or _git(self.root, "ls-files", "--others", "-z"):
            raise SyntheticGitError("synthetic_file_inventory_mismatch")
        for relative, payload in self.files.items():
            physical = self.root.joinpath(*relative.split("/"))
            _plain_path(physical, directory=False)
            if physical.read_bytes() != payload:
                raise SyntheticGitError("synthetic_physical_bytes_mismatch")
            if _git(self.root, "show", f":{relative}") != payload:
                raise SyntheticGitError("synthetic_index_bytes_mismatch")

    def stage_files(self, changes: Mapping[str, bytes]) -> str:
        """Add or replace explicit regular files; return the real staged tree."""
        selected = _validated_files(changes)
        combined = _validated_files({**self.files, **selected})
        for relative, payload in selected.items():
            destination = self.root.joinpath(*relative.split("/"))
            current = self.root
            _plain_path(current, directory=True)
            for part in relative.split("/")[:-1]:
                current /= part
                current.mkdir(exist_ok=True)
                _plain_path(current, directory=True)
            if destination.exists() or destination.is_symlink():
                _plain_path(destination, directory=False)
            destination.write_bytes(payload)
        _git(self.root, "add", "--force", "--", *sorted(selected))
        self.files = combined
        self.assert_file_inventory()
        return self.index_tree()

    def commit_exact_index(
        self, *, expected_head: str | None, expected_tree: str, message: str
    ) -> SyntheticCommit:
        """Commit one explicitly observed index tree and compare-and-swap its ref."""
        if (
            _SHA1.fullmatch(expected_tree) is None
            or (expected_head is not None and _SHA1.fullmatch(expected_head) is None)
            or not isinstance(message, str)
            or not message.strip()
            or "\0" in message
        ):
            raise SyntheticGitError("synthetic_commit_binding_invalid")
        self.assert_file_inventory()
        if self.index_tree() != expected_tree:
            raise SyntheticGitError("synthetic_index_tree_drift")
        if expected_head is not None and self.head() != expected_head:
            raise SyntheticGitError("synthetic_head_drift")
        args = ["commit-tree", expected_tree]
        if expected_head is not None:
            args.extend(("-p", expected_head))
        sha = _oid(
            _git(self.root, *args, payload=(message.rstrip() + "\n").encode("utf-8"))
        )
        _git(self.root, "update-ref", self.branch_ref, sha, expected_head or _ZERO_SHA)
        if self.head() != sha or self.index_tree() != expected_tree:
            raise SyntheticGitError("synthetic_commit_readback_mismatch")
        if _oid(_git(self.root, "rev-parse", f"{sha}^{{tree}}")) != expected_tree:
            raise SyntheticGitError("synthetic_commit_tree_mismatch")
        parents = (
            _git(self.root, "rev-list", "--parents", "-n", "1", sha).decode().split()
        )
        if parents != [sha, *([expected_head] if expected_head is not None else [])]:
            raise SyntheticGitError("synthetic_commit_parent_mismatch")
        return SyntheticCommit(sha=sha, tree=expected_tree, parent=expected_head)

    def remote_head(self) -> str | None:
        if self.origin is None:
            raise SyntheticGitError("synthetic_local_origin_missing")
        _plain_path(self.origin, directory=True)
        output = _git(
            self.root, "ls-remote", "--refs", self.origin.as_posix(), self.branch_ref
        )
        if not output:
            return None
        fields = output.decode("ascii").strip().split("\t")
        if len(fields) != 2 or fields[1] != self.branch_ref:
            raise SyntheticGitError("synthetic_remote_readback_invalid")
        return _oid(fields[0].encode("ascii"))

    def push_exact_sha(self, sha: str, *, expected_remote_head: str | None) -> str:
        """Push to the newly authored local bare origin and read back its exact ref."""
        if self.origin is None or _SHA1.fullmatch(sha) is None:
            raise SyntheticGitError("synthetic_push_binding_invalid")
        if (
            expected_remote_head is not None
            and _SHA1.fullmatch(expected_remote_head) is None
        ):
            raise SyntheticGitError("synthetic_remote_binding_invalid")
        self.assert_file_inventory()
        if self.head() != sha or self.index_tree() != _oid(
            _git(self.root, "rev-parse", f"{sha}^{{tree}}")
        ):
            raise SyntheticGitError("synthetic_push_source_drift")
        if self.remote_head() != expected_remote_head:
            raise SyntheticGitError("synthetic_remote_head_drift")
        _git(
            self.root,
            "push",
            "--porcelain",
            f"--force-with-lease={self.branch_ref}:{expected_remote_head or ''}",
            self.origin.as_posix(),
            f"{sha}:{self.branch_ref}",
        )
        if self.remote_head() != sha:
            raise SyntheticGitError("synthetic_push_readback_mismatch")
        return sha


@dataclass(frozen=True)
class SyntheticGraph:
    root: Path
    target: SyntheticRepository
    origin: Path
    initial_commit: SyntheticCommit


def create_synthetic_repository(
    path: Path, files: Mapping[str, bytes], *, branch: str = "synthetic/maintenance"
) -> SyntheticRepository:
    """Create a new complete repository from an explicit, nonempty byte map."""
    selected = _validated_files(files)
    if not isinstance(branch, str) or _BRANCH.fullmatch(branch) is None:
        raise SyntheticGitError("synthetic_branch_invalid")
    root = _initialize(path, branch)
    repository = SyntheticRepository(root=root, branch=branch, files={})
    tree = repository.stage_files(selected)
    repository.initial_commit = repository.commit_exact_index(
        expected_head=None,
        expected_tree=tree,
        message="authored synthetic fixture root",
    )
    return repository


def create_synthetic_graph(
    path: Path, files: Mapping[str, bytes], *, branch: str = "synthetic/maintenance"
) -> SyntheticGraph:
    """Create a complete target plus a new, initially empty local bare origin."""
    selected = _validated_files(files)
    if not isinstance(branch, str) or _BRANCH.fullmatch(branch) is None:
        raise SyntheticGitError("synthetic_branch_invalid")
    root = _new_directory(path)
    target = create_synthetic_repository(root / "target", selected, branch=branch)
    origin = _initialize(root / "origin.git", branch, bare=True)
    _git(target.root, "remote", "add", "origin", origin.as_posix())
    target.origin = origin
    assert target.initial_commit is not None
    return SyntheticGraph(root, target, origin, target.initial_commit)
