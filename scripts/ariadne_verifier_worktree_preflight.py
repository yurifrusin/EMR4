"""Validate an exact verifier worktree before a pre-verifier receipt is issued."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ariadne_antigravity import WorktreeState, inspect_worktree
from scripts.ariadne_evidence_gate import (
    command_manifest_sha256,
    validate_command_manifest,
)


SCHEMA_VERSION = "ariadne.verifier-worktree-preflight.v1"
DEFAULT_BRANCH_PREFIX = "codex/review-"


def _object(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _validate_repository_paths(
    entries: Sequence[dict[str, object]] | None,
    *,
    worktree_root: Path,
) -> list[dict[str, object]]:
    """Validate typed repository-path bindings without executing anything."""
    if entries is None:
        return []
    normalized: list[dict[str, object]] = []
    for index, raw in enumerate(entries):
        entry = _object(raw, label=f"repository_paths[{index}]")
        if set(entry) != {"path", "kind", "required", "scope"}:
            raise ValueError(
                f"repository_paths[{index}] keys must be exactly "
                "path/kind/required/scope"
            )
        raw_path = entry["path"]
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"repository_paths[{index}].path must be non-empty")
        kind = entry["kind"]
        if kind not in {"file", "directory"}:
            raise ValueError(f"repository_paths[{index}].kind is not admitted")
        required = entry["required"]
        if not isinstance(required, bool):
            raise ValueError(f"repository_paths[{index}].required must be a boolean")
        scope = entry["scope"]
        if scope not in {"worktree", "external"}:
            raise ValueError(f"repository_paths[{index}].scope is not admitted")

        candidate = Path(raw_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (worktree_root / candidate).resolve()
        exists = resolved.exists()
        if required and not exists:
            raise ValueError(
                f"repository_paths[{index}] required path is missing: {resolved}"
            )
        if exists:
            if kind == "file" and not resolved.is_file():
                raise ValueError(
                    f"repository_paths[{index}] must be a file: {resolved}"
                )
            if kind == "directory" and not resolved.is_dir():
                raise ValueError(
                    f"repository_paths[{index}] must be a directory: {resolved}"
                )
        if scope == "worktree":
            try:
                resolved.relative_to(worktree_root.resolve())
            except ValueError as error:
                raise ValueError(
                    f"repository_paths[{index}] with scope=worktree must resolve "
                    f"inside the review worktree: {resolved}"
                ) from error
        normalized.append(
            {
                "path": resolved.as_posix(),
                "kind": kind,
                "required": required,
                "scope": scope,
                "exists": exists,
            }
        )
    return normalized


def _resolve_candidate_paths(
    candidate_paths: Sequence[str | Path] | None,
    *,
    worktree_root: Path,
    serial_repo_root: Path | None,
) -> list[str]:
    """Resolve candidate test paths strictly inside the review worktree.

    A serial runner outside the review worktree must bind ``--repo-root``
    exactly to the review worktree; otherwise relative candidate tests behind a
    different checkout are rejected.
    """
    if candidate_paths is None:
        return []
    worktree = worktree_root.resolve()
    resolved_paths: list[str] = []
    if serial_repo_root is not None and serial_repo_root.resolve() != worktree:
        raise ValueError(
            "external serial runner must bind --repo-root exactly to the "
            "review worktree"
        )
    for index, raw in enumerate(candidate_paths):
        candidate = Path(raw)
        resolved = (
            candidate.resolve()
            if candidate.is_absolute()
            else (worktree / candidate).resolve()
        )
        try:
            resolved.relative_to(worktree)
        except ValueError as error:
            raise ValueError(
                f"candidate_paths[{index}] resolves outside the review "
                f"worktree: {resolved}"
            ) from error
        resolved_paths.append(resolved.as_posix())
    return resolved_paths


def build_preflight(
    *,
    cwd: Path,
    expected_head: str,
    branch_prefix: str = DEFAULT_BRANCH_PREFIX,
    command_manifest: dict[str, object] | None = None,
    repository_paths: Sequence[dict[str, object]] | None = None,
    candidate_paths: Sequence[str | Path] | None = None,
    serial_repo_root: Path | None = None,
) -> dict[str, object]:
    state: WorktreeState = inspect_worktree(cwd, require_clean=True)
    if state.head != expected_head:
        raise ValueError(
            f"verifier worktree HEAD mismatch: {state.head}!={expected_head}"
        )
    if not state.branch.startswith(branch_prefix):
        raise ValueError(
            "verifier branch must use the non-protected review prefix: "
            f"{state.branch!r}"
        )
    manifest_sha: str | None = None
    manifest_command_count: int | None = None
    if command_manifest is not None:
        normalized_manifest = validate_command_manifest(command_manifest)
        manifest_sha = command_manifest_sha256(normalized_manifest)
        manifest_command_count = len(normalized_manifest["commands"])

    normalized_repository_paths = _validate_repository_paths(
        repository_paths, worktree_root=state.root
    )
    normalized_candidate_paths = _resolve_candidate_paths(
        candidate_paths,
        worktree_root=state.root,
        serial_repo_root=serial_repo_root,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "passed",
        "worktree": state.root.as_posix(),
        "branch": state.branch,
        "head": state.head,
        "expected_head": expected_head,
        "clean": not state.dirty,
        "branch_prefix": branch_prefix,
        "command_manifest_sha256": manifest_sha,
        "command_count": manifest_command_count,
        "repository_paths": normalized_repository_paths,
        "candidate_paths": normalized_candidate_paths,
        "serial_repo_root": (
            serial_repo_root.resolve().as_posix()
            if serial_repo_root is not None
            else None
        ),
        "provider_or_model_calls": 0,
        "authority_boundary": "local_read_only_pre_dispatch_check",
    }


def _load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"{label} could not be read: {error}") from error
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} must be valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _parse_repository_paths(value: str) -> list[dict[str, object]]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("--repository-paths must be valid JSON") from error
    if not isinstance(parsed, list):
        raise ValueError("--repository-paths must be a JSON array")
    return [item for item in parsed if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--branch-prefix", default=DEFAULT_BRANCH_PREFIX)
    parser.add_argument("--command-manifest", type=Path)
    parser.add_argument("--repository-paths", type=str)
    parser.add_argument("--candidate-path", action="append", default=[])
    parser.add_argument("--serial-repo-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        command_manifest = (
            _load_json_object(args.command_manifest, label="command manifest")
            if args.command_manifest is not None
            else None
        )
        repository_paths = (
            _parse_repository_paths(args.repository_paths)
            if args.repository_paths is not None
            else None
        )
        evidence = build_preflight(
            cwd=args.cwd,
            expected_head=args.expected_head,
            branch_prefix=args.branch_prefix,
            command_manifest=command_manifest,
            repository_paths=repository_paths,
            candidate_paths=args.candidate_path,
            serial_repo_root=args.serial_repo_root,
        )
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 2
    rendered = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
