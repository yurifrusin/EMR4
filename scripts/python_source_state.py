"""Validate and compile the explicit maintained EMR4 Python source selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "orchestration/harness_settings/python_source_state.json"
EXPECTED_SCHEMA = "emr4.python_source_state.v1"
ENTRY_MODES = {"file", "recursive", "top_level"}


class SourceStateError(ValueError):
    """Raised when source-state policy is incomplete or unsafe."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceStateError(f"source-state manifest is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise SourceStateError("source-state manifest must be a JSON object")
    return value


def _relative_path(raw: object) -> PurePosixPath:
    if not isinstance(raw, str) or not raw:
        raise SourceStateError("source-state paths must be non-empty strings")
    if "\\" in raw or ":" in raw:
        raise SourceStateError(f"source-state path is not repository-relative POSIX: {raw}")
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SourceStateError(f"source-state path escapes or is not normalized: {raw}")
    if path.as_posix() != raw:
        raise SourceStateError(f"source-state path escapes or is not normalized: {raw}")
    return path


def _is_within(path: PurePosixPath, root: PurePosixPath) -> bool:
    return path == root or root in path.parents


def _contains_forbidden_token(path: PurePosixPath, tokens: list[str]) -> bool:
    return any(
        token.lower() in part.lower()
        for part in path.parts
        for token in tokens
    )


def _ensure_within_repo(path: Path, repo_root: Path) -> None:
    try:
        path.resolve(strict=False).relative_to(repo_root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise SourceStateError(f"source-state path resolves outside repository: {path}") from exc


def _expand_entry(repo_root: Path, entry: dict[str, Any]) -> list[Path]:
    path = _relative_path(entry.get("path"))
    mode = entry.get("mode")
    absolute = repo_root.joinpath(*path.parts)
    _ensure_within_repo(absolute, repo_root)
    if mode == "file":
        if not absolute.is_file() or absolute.suffix != ".py":
            raise SourceStateError(f"selected Python file is absent: {path.as_posix()}")
        return [absolute]
    if mode not in {"recursive", "top_level"}:
        raise SourceStateError(f"unsupported source-state mode for {path}: {mode!r}")
    if not absolute.is_dir():
        raise SourceStateError(f"selected Python directory is absent: {path.as_posix()}")
    iterator: Iterable[Path]
    iterator = absolute.rglob("*.py") if mode == "recursive" else absolute.glob("*.py")
    files = sorted(candidate for candidate in iterator if candidate.is_file())
    if not files:
        raise SourceStateError(f"selected Python directory is empty: {path.as_posix()}")
    for candidate in files:
        _ensure_within_repo(candidate, repo_root)
    return files


def load_source_state(
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    repo_root: Path = ROOT,
) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    required = {
        "schema_version",
        "target_python",
        "allowed_states",
        "forbidden_path_tokens",
        "forbidden_recursive_roots",
        "source_entries",
        "verification_paths",
    }
    if set(manifest) != required:
        raise SourceStateError(
            "source-state manifest keys must be exact; missing="
            f"{sorted(required - set(manifest))}, extra={sorted(set(manifest) - required)}"
        )
    if manifest["schema_version"] != EXPECTED_SCHEMA:
        raise SourceStateError("unexpected source-state schema version")
    if manifest["target_python"] != "3.11":
        raise SourceStateError("EMR4 maintained source target must remain Python 3.11")

    allowed_states = manifest["allowed_states"]
    if allowed_states != [
        "mounted_current",
        "mounted_default_off",
        "accepted_unmounted",
    ]:
        raise SourceStateError("allowed maintained source states are not exact")
    forbidden_tokens = manifest["forbidden_path_tokens"]
    if not isinstance(forbidden_tokens, list) or not all(
        isinstance(item, str) and item for item in forbidden_tokens
    ):
        raise SourceStateError("forbidden_path_tokens must be non-empty strings")
    forbidden_roots = [
        _relative_path(item) for item in manifest["forbidden_recursive_roots"]
    ]

    entries = manifest["source_entries"]
    if not isinstance(entries, list) or not entries:
        raise SourceStateError("source_entries must be a non-empty array")
    selected: list[Path] = []
    ruff_paths: list[str] = []
    entry_paths: set[str] = set()
    selected_paths: set[str] = set()

    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "mode", "state"}:
            raise SourceStateError("each source entry must contain exact path/mode/state")
        path = _relative_path(entry["path"])
        path_text = path.as_posix()
        if path_text in entry_paths:
            raise SourceStateError(f"duplicate source entry: {path_text}")
        entry_paths.add(path_text)
        if entry["mode"] not in ENTRY_MODES:
            raise SourceStateError(f"unsupported source-state mode: {entry['mode']!r}")
        if entry["state"] not in allowed_states:
            raise SourceStateError(f"unsupported maintained source state: {entry['state']!r}")
        if _contains_forbidden_token(path, forbidden_tokens):
            raise SourceStateError(f"forbidden source-state path token: {path_text}")
        if entry["mode"] == "recursive" and any(
            _is_within(root, path) or _is_within(path, root) for root in forbidden_roots
        ):
            raise SourceStateError(f"recursive selection reaches a closed root: {path_text}")

        expanded = _expand_entry(repo_root, entry)
        for absolute in expanded:
            relative = absolute.relative_to(repo_root).as_posix()
            if _contains_forbidden_token(PurePosixPath(relative), forbidden_tokens):
                raise SourceStateError(f"expanded selection contains forbidden token: {relative}")
            if relative in selected_paths:
                raise SourceStateError(f"duplicate selected Python source: {relative}")
            selected_paths.add(relative)
            selected.append(absolute)
        if entry["mode"] == "top_level":
            ruff_paths.extend(
                absolute.relative_to(repo_root).as_posix() for absolute in expanded
            )
        else:
            ruff_paths.append(path_text)

    verification_paths = []
    for raw in manifest["verification_paths"]:
        path = _relative_path(raw)
        absolute = repo_root.joinpath(*path.parts)
        _ensure_within_repo(absolute, repo_root)
        if not absolute.is_file() or absolute.suffix != ".py":
            raise SourceStateError(f"verification Python file is absent: {path.as_posix()}")
        if _contains_forbidden_token(path, forbidden_tokens):
            raise SourceStateError(f"verification path contains forbidden token: {path}")
        verification_paths.append(path.as_posix())

    return {
        "schema_version": EXPECTED_SCHEMA,
        "target_python": manifest["target_python"],
        "source_files": sorted(selected, key=lambda item: item.as_posix()),
        "ruff_paths": [*ruff_paths, *verification_paths],
        "entry_count": len(entries),
        "verification_count": len(verification_paths),
    }


def require_target_runtime(target: str, *, version: tuple[int, int] | None = None) -> None:
    observed = version or (sys.version_info.major, sys.version_info.minor)
    expected = tuple(int(part) for part in target.split("."))
    if observed != expected:
        raise SourceStateError(
            f"Python target runtime mismatch: expected {target}, observed {observed[0]}.{observed[1]}"
        )


def compile_selected_sources(state: dict[str, Any]) -> None:
    for path in state["source_files"]:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
        except (OSError, UnicodeError, SyntaxError) as exc:
            raise SourceStateError(f"maintained Python source did not compile: {path}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--require-target-runtime", action="store_true")
    args = parser.parse_args()
    try:
        state = load_source_state(args.manifest)
        if args.require_target_runtime:
            require_target_runtime(state["target_python"])
        compile_selected_sources(state)
    except SourceStateError as exc:
        print(f"[source_state_failure] {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "passed",
                "schema_version": state["schema_version"],
                "target_python": state["target_python"],
                "host_python": f"{sys.version_info.major}.{sys.version_info.minor}",
                "source_file_count": len(state["source_files"]),
                "verification_file_count": state["verification_count"],
                "protected_paths_enumerated": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
