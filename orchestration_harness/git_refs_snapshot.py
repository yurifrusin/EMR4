"""Read-only machine snapshot of Ariadne Git refs and worktree state."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Sequence


SCHEMA_VERSION = "ariadne.git_refs_snapshot.v1"
_FULL_COMMIT_ID = re.compile(r"^[0-9a-f]{40}$")


class GitRefsSnapshotError(RuntimeError):
    """Closed snapshot failure carrying one stable reason code."""

    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def _normalized_path(value: str | Path) -> str:
    return os.path.normcase(str(Path(value).resolve()))


def _run_git(
    repo_root: Path,
    arguments: Sequence[str],
    *,
    timeout_seconds: int,
    admitted_returncodes: frozenset[int] = frozenset({0}),
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout_seconds,
            shell=False,
        )
    except FileNotFoundError as error:
        raise GitRefsSnapshotError("git_executable_unavailable") from error
    except subprocess.TimeoutExpired as error:
        raise GitRefsSnapshotError("git_refs_snapshot_timeout") from error
    except (OSError, UnicodeError) as error:
        raise GitRefsSnapshotError("git_refs_snapshot_unavailable") from error
    if result.returncode not in admitted_returncodes:
        raise GitRefsSnapshotError("git_refs_snapshot_command_failed")
    return result


def _single_line(result: subprocess.CompletedProcess[str], reason_code: str) -> str:
    value = result.stdout.strip()
    if not value or "\r" in value or "\n" in value:
        raise GitRefsSnapshotError(reason_code)
    return value


def _resolve_ref(
    repo_root: Path, ref: str, *, timeout_seconds: int, required: bool
) -> str | None:
    result = _run_git(
        repo_root,
        ("rev-parse", "--verify", f"{ref}^{{commit}}"),
        timeout_seconds=timeout_seconds,
        admitted_returncodes=frozenset({0, 128}),
    )
    if result.returncode == 128:
        if required:
            raise GitRefsSnapshotError("git_refs_snapshot_required_ref_missing")
        return None
    value = _single_line(result, "git_refs_snapshot_ref_malformed")
    if _FULL_COMMIT_ID.fullmatch(value) is None:
        raise GitRefsSnapshotError("git_refs_snapshot_ref_malformed")
    return value


def build_git_refs_snapshot(
    *,
    repo_root: Path,
    expected_protected_commit: str,
    protected_refs: Sequence[str],
    preserved_untracked_paths: Sequence[str] = ("docs/branding",),
    timeout_seconds: int = 5,
) -> dict[str, Any]:
    """Return an exact snapshot without accepting caller-supplied ref values."""
    if _FULL_COMMIT_ID.fullmatch(expected_protected_commit) is None:
        raise GitRefsSnapshotError("git_refs_snapshot_expected_commit_invalid")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 30:
        raise GitRefsSnapshotError("git_refs_snapshot_timeout_policy_invalid")
    if (
        not protected_refs
        or len(set(protected_refs)) != len(protected_refs)
        or any(not isinstance(ref, str) or not ref for ref in protected_refs)
    ):
        raise GitRefsSnapshotError("git_refs_snapshot_protected_refs_invalid")
    if len(set(preserved_untracked_paths)) != len(preserved_untracked_paths):
        raise GitRefsSnapshotError("git_refs_snapshot_preserved_paths_invalid")

    root = repo_root.resolve()
    top_level = _single_line(
        _run_git(
            root, ("rev-parse", "--show-toplevel"), timeout_seconds=timeout_seconds
        ),
        "git_refs_snapshot_repository_root_malformed",
    )
    if _normalized_path(top_level) != _normalized_path(root):
        raise GitRefsSnapshotError("git_refs_snapshot_repository_root_mismatch")

    head = _resolve_ref(root, "HEAD", timeout_seconds=timeout_seconds, required=True)
    branch_result = _run_git(
        root,
        ("symbolic-ref", "--short", "-q", "HEAD"),
        timeout_seconds=timeout_seconds,
        admitted_returncodes=frozenset({0, 1}),
    )
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    if branch is not None and (not branch or "\r" in branch or "\n" in branch):
        raise GitRefsSnapshotError("git_refs_snapshot_branch_malformed")

    resolved_protected = {
        ref: _resolve_ref(root, ref, timeout_seconds=timeout_seconds, required=True)
        for ref in protected_refs
    }
    protected_match = all(
        commit == expected_protected_commit for commit in resolved_protected.values()
    )

    branch_ref = f"refs/heads/{branch}" if branch is not None else None
    origin_branch_ref = (
        f"refs/remotes/origin/{branch}" if branch is not None else None
    )
    branch_commit = (
        _resolve_ref(root, branch_ref, timeout_seconds=timeout_seconds, required=True)
        if branch_ref is not None
        else None
    )
    origin_branch_commit = (
        _resolve_ref(
            root,
            origin_branch_ref,
            timeout_seconds=timeout_seconds,
            required=False,
        )
        if origin_branch_ref is not None
        else None
    )

    tracked_status = _run_git(
        root,
        ("status", "--porcelain=v1", "--untracked-files=no"),
        timeout_seconds=timeout_seconds,
    ).stdout
    all_status = _run_git(
        root,
        ("status", "--porcelain=v1", "--untracked-files=all"),
        timeout_seconds=timeout_seconds,
    ).stdout
    status_lines = [line for line in all_status.splitlines() if line]
    untracked_count = sum(line.startswith("?? ") for line in status_lines)

    preserved: dict[str, bool] = {}
    for raw_path in preserved_untracked_paths:
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise GitRefsSnapshotError("git_refs_snapshot_preserved_paths_invalid")
        candidate = (root / raw_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            raise GitRefsSnapshotError(
                "git_refs_snapshot_preserved_path_outside_repository"
            ) from error
        prefix = raw_path.replace("\\", "/").rstrip("/") + "/"
        preserved[raw_path] = candidate.exists() and any(
            line.startswith("?? ")
            and (
                line[3:].replace("\\", "/") == raw_path.replace("\\", "/")
                or line[3:].replace("\\", "/").startswith(prefix)
            )
            for line in status_lines
        )

    reasons = [] if protected_match else ["git_refs_snapshot_protected_ref_mismatch"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed" if protected_match else "revision_required",
        "head": head,
        "branch": branch,
        "branch_commit": branch_commit,
        "origin_branch_commit": origin_branch_commit,
        "branch_origin_aligned": (
            branch_commit == origin_branch_commit
            if origin_branch_commit is not None
            else None
        ),
        "protected_expected_commit": expected_protected_commit,
        "protected_refs": resolved_protected,
        "protected_refs_aligned": protected_match,
        "tracked_worktree_clean": not tracked_status.strip(),
        "untracked_path_count": untracked_count,
        "preserved_untracked_paths": preserved,
        "reason_codes": reasons,
    }


def failure_projection(reason_code: str) -> dict[str, Any]:
    """Return a closed snapshot failure without guessed Git values."""
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "revision_required",
        "head": None,
        "branch": None,
        "branch_commit": None,
        "origin_branch_commit": None,
        "branch_origin_aligned": None,
        "protected_expected_commit": None,
        "protected_refs": {},
        "protected_refs_aligned": False,
        "tracked_worktree_clean": None,
        "untracked_path_count": None,
        "preserved_untracked_paths": {},
        "reason_codes": [reason_code],
    }
