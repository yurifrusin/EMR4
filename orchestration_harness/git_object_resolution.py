"""Read-only exact Git commit resolution for Ariadne continuation receipts."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Sequence


SCHEMA_VERSION = "ariadne.git_object_resolution.v1"
_FULL_OBJECT_ID = re.compile(r"^[0-9a-f]{40}$")


class GitObjectResolutionError(RuntimeError):
    """Closed Git resolution failure carrying one stable reason code."""

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
    if (
        not isinstance(arguments, (tuple, list))
        or not arguments
        or any(not isinstance(item, str) or not item for item in arguments)
    ):
        raise GitObjectResolutionError("git_object_command_invalid")
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
    except FileNotFoundError as exc:
        raise GitObjectResolutionError("git_executable_unavailable") from exc
    except subprocess.TimeoutExpired as exc:
        raise GitObjectResolutionError("git_object_resolution_timeout") from exc
    except (OSError, UnicodeError) as exc:
        raise GitObjectResolutionError("git_object_resolution_unavailable") from exc
    if result.returncode not in admitted_returncodes:
        raise GitObjectResolutionError("git_object_command_failed")
    return result


def _single_line(result: subprocess.CompletedProcess[str], reason_code: str) -> str:
    value = result.stdout.strip()
    if not value or "\r" in value or "\n" in value:
        raise GitObjectResolutionError(reason_code)
    return value


def resolve_commit_source(
    *,
    repo_root: Path,
    source_head: str,
    timeout_seconds: int = 5,
    require_ancestor_of_head: bool = True,
) -> dict[str, Any]:
    """Resolve one validated literal source object and compare it with HEAD.

    Only fixed read-only Git commands are executed. ``source_head`` is accepted
    solely as a literal forty-character object ID and cannot select a ref, path
    or revision expression.
    """
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 30:
        raise GitObjectResolutionError("git_object_timeout_policy_invalid")
    if not isinstance(require_ancestor_of_head, bool):
        raise GitObjectResolutionError("git_object_ancestor_policy_invalid")
    if (
        not isinstance(source_head, str)
        or _FULL_OBJECT_ID.fullmatch(source_head) is None
    ):
        raise GitObjectResolutionError("git_object_id_not_full_lowercase_hex")
    root = repo_root.resolve()
    if not root.is_dir():
        raise GitObjectResolutionError("git_repository_root_unavailable")

    top_level = _single_line(
        _run_git(
            root, ("rev-parse", "--show-toplevel"), timeout_seconds=timeout_seconds
        ),
        "git_repository_root_malformed",
    )
    if _normalized_path(top_level) != _normalized_path(root):
        raise GitObjectResolutionError("git_repository_root_mismatch")

    resolved = _single_line(
        _run_git(
            root,
            ("rev-parse", "--verify", f"{source_head}^{{commit}}"),
            timeout_seconds=timeout_seconds,
        ),
        "git_resolved_commit_malformed",
    )
    if _FULL_OBJECT_ID.fullmatch(resolved) is None or resolved != source_head:
        raise GitObjectResolutionError("git_resolved_commit_mismatch")

    object_type = _single_line(
        _run_git(
            root, ("cat-file", "-t", source_head), timeout_seconds=timeout_seconds
        ),
        "git_object_type_malformed",
    )
    if object_type != "commit":
        raise GitObjectResolutionError("git_object_is_not_commit")

    observed_head = _single_line(
        _run_git(
            root, ("rev-parse", "--verify", "HEAD"), timeout_seconds=timeout_seconds
        ),
        "git_observed_head_malformed",
    )
    if _FULL_OBJECT_ID.fullmatch(observed_head) is None:
        raise GitObjectResolutionError("git_observed_head_malformed")

    ancestor = True
    if require_ancestor_of_head:
        result = _run_git(
            root,
            ("merge-base", "--is-ancestor", source_head, observed_head),
            timeout_seconds=timeout_seconds,
            admitted_returncodes=frozenset({0, 1}),
        )
        ancestor = result.returncode == 0
        if not ancestor:
            raise GitObjectResolutionError("git_source_not_ancestor_of_head")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "source_field": "active_operation.source_head",
        "supplied_object_id": source_head,
        "resolved_commit": resolved,
        "observed_head": observed_head,
        "source_is_ancestor_of_head": ancestor,
        "reason_codes": [],
    }


def failure_projection(*, source_head: object, reason_code: str) -> dict[str, Any]:
    """Return one closed non-authoritative failure projection."""
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "revision_required",
        "source_field": "active_operation.source_head",
        "supplied_object_id": source_head if isinstance(source_head, str) else None,
        "resolved_commit": None,
        "observed_head": None,
        "source_is_ancestor_of_head": None,
        "reason_codes": [reason_code],
    }
