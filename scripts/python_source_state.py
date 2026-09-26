"""Authenticate one literal ordinary verification selection before reading its files."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any


# These are lexical constants. Importing this module performs no source discovery.
ROOT = Path(__file__).absolute().parents[1]
DEFAULT_MANIFEST = ROOT / "orchestration/harness_settings/python_source_state.json"
EXPECTED_SCHEMA = "emr4.python_source_state.v2"
SCOPE = "bounded_ordinary_verification"
KINDS = frozenset({"source", "test", "config", "data", "import"})
PHASES = ("compile", "ruff", "bandit", "leakage", "tests")
CONFIGS = ("ruff", "bandit", "pytest")
FORBIDDEN_TOKENS = ("holdout", "local_data", "historical-diary-trove")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
COMPONENT = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_. -]*\Z")
NODE_PART = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
DEVICE_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{number}" for number in range(1, 10)}
    | {f"LPT{number}" for number in range(1, 10)}
)
MAX_BYTES = 4 * 1024 * 1024


class SourceStateError(ValueError):
    """The literal selection or one authenticated input is invalid."""


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise SourceStateError(reason)


def _keys(value: object, expected: set[str], reason: str) -> dict[str, Any]:
    _need(type(value) is dict and set(value) == expected, reason)
    return value


def _strict_json(raw: bytes) -> Any:
    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            _need(key not in result, "duplicate_selection_json_key")
            result[key] = value
        return result

    def nonfinite(_: str) -> None:
        raise SourceStateError("nonfinite_selection_json")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SourceStateError("malformed_selection_json") from exc


def _digest(value: object, reason: str) -> str:
    _need(type(value) is str and HEX64.fullmatch(value) is not None, reason)
    return value


def _literal_path(value: object) -> str:
    _need(type(value) is str and 0 < len(value) <= 240, "invalid_literal_path")
    _need(not value.startswith(("/", "-")) and "\\" not in value and ":" not in value,
          "invalid_literal_path")
    parts = value.split("/")
    _need(all(
        part not in {"", ".", ".."}
        and COMPONENT.fullmatch(part) is not None
        and not part.startswith("-")
        and not part.endswith((" ", "."))
        and "~" not in part
        and part.split(".", 1)[0].rstrip(" .").upper() not in DEVICE_NAMES
        and not any(token in part.casefold() for token in FORBIDDEN_TOKENS)
        for part in parts
    ), "invalid_literal_path")
    return value


def _test_node(value: object) -> tuple[str, str]:
    _need(type(value) is str and len(value) <= 320, "invalid_test_node")
    parts = value.split("::")
    _need(len(parts) >= 2 and all(NODE_PART.fullmatch(part) for part in parts[1:])
          and parts[-1].startswith("test_"), "invalid_test_node")
    path = _literal_path(parts[0])
    _need(path.startswith("tests/") and path.endswith(".py"), "invalid_test_node")
    return path, value


def _scope_sha256(files: dict[str, dict[str, str]], bandit_paths: list[str]) -> str:
    pairs = [[path, files[path]["sha256"]] for path in sorted(bandit_paths)]
    raw = json.dumps(pairs, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_selection(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate all rows and references without touching the filesystem."""
    m = _keys(manifest, {
        "schema_version", "target_python", "scope", "source_commit", "source_tree",
        "completeness", "files", "phases", "configs", "bandit_review",
    }, "selection_keys")
    _need(m["schema_version"] == EXPECTED_SCHEMA and m["target_python"] == "3.11"
          and m["scope"] == SCOPE, "selection_identity")
    _need(type(m["source_commit"]) is str and HEX40.fullmatch(m["source_commit"]) is not None
          and type(m["source_tree"]) is str and HEX40.fullmatch(m["source_tree"]) is not None,
          "selection_source_identity")
    completeness = _keys(m["completeness"], {"repository_wide", "pending"},
                         "completeness_keys")
    pending = completeness["pending"]
    _need(completeness["repository_wide"] is False and type(pending) is list and pending
          and all(type(item) is str and 0 < len(item.strip()) <= 300 for item in pending)
          and len({item.casefold() for item in pending}) == len(pending),
          "bounded_completeness_required")

    rows = m["files"]
    _need(type(rows) is list and rows, "empty_file_selection")
    files: dict[str, dict[str, str]] = {}
    folded_paths: set[str] = set()
    for row in rows:
        item = _keys(row, {"path", "sha256", "kind"}, "file_row_keys")
        path = _literal_path(item["path"])
        digest = _digest(item["sha256"], "file_digest")
        _need(type(item["kind"]) is str and item["kind"] in KINDS
              and path.casefold() not in folded_paths,
              "duplicate_or_unclassified_file")
        folded_paths.add(path.casefold())
        files[path] = {"path": path, "sha256": digest, "kind": item["kind"]}
    prefixes: dict[str, str] = {}
    for path in files:
        parts = path.split("/")
        for index in range(1, len(parts) + 1):
            spelling = "/".join(parts[:index])
            prior = prefixes.setdefault(spelling.casefold(), spelling)
            _need(prior == spelling, "windows_component_alias")
            if index < len(parts):
                _need(spelling.casefold() not in folded_paths,
                      "file_directory_collision")

    phases = _keys(m["phases"], set(PHASES), "phase_keys")
    phase_paths: dict[str, list[str]] = {}
    test_nodes: list[str] = []
    for phase in PHASES:
        values = phases[phase]
        _need(type(values) is list and values, "empty_phase")
        seen: set[str] = set()
        checked: list[str] = []
        for value in values:
            if phase == "tests":
                path, node = _test_node(value)
                checked.append(path)
                test_nodes.append(node)
                spelling = node
            else:
                spelling = _literal_path(value)
                checked.append(spelling)
            _need(spelling.casefold() not in seen, "duplicate_phase_entry")
            seen.add(spelling.casefold())
        phase_paths[phase] = checked

    configs = _keys(m["configs"], set(CONFIGS), "config_keys")
    config_paths = {key: _literal_path(configs[key]) for key in CONFIGS}
    review = _keys(m["bandit_review"],
                   {"status", "scope_sha256", "reviewed_findings"}, "bandit_review_keys")
    _need(type(review["status"]) is str
          and review["status"] in {"pending", "reviewed"}, "bandit_review_status")
    _digest(review["scope_sha256"], "bandit_scope_digest")
    findings = review["reviewed_findings"]
    _need(type(findings) is list, "reviewed_findings")
    fingerprints: set[tuple[str, str, int, str]] = set()
    for row in findings:
        item = _keys(row, {"path", "test_id", "line_number", "code_sha256"},
                     "reviewed_finding_keys")
        path = _literal_path(item["path"])
        _need(type(item["test_id"]) is str and
              re.fullmatch(r"B[0-9]{3}", item["test_id"]) is not None
              and type(item["line_number"]) is int and item["line_number"] > 0,
              "reviewed_finding_identity")
        digest = _digest(item["code_sha256"], "reviewed_finding_digest")
        fingerprint = (path, item["test_id"], item["line_number"], digest)
        _need(fingerprint not in fingerprints, "duplicate_reviewed_finding")
        fingerprints.add(fingerprint)

    # Only after every lexical row is checked may relationships be checked.
    used: set[str] = set(config_paths.values())
    for phase, paths in phase_paths.items():
        for path in paths:
            _need(path in files, "unknown_phase_path")
            if phase in {"compile", "ruff", "bandit"}:
                _need(path.endswith(".py")
                      and files[path]["kind"] in {"source", "test", "import"},
                      "invalid_python_phase_path")
            elif phase == "tests":
                _need(files[path]["kind"] == "test", "invalid_test_phase_path")
            else:
                _need(Path(path).suffix.lower() in
                      {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt"},
                      "invalid_text_phase_path")
            used.add(path)
    _need(all(path in files and files[path]["kind"] == "config"
              for path in config_paths.values()), "invalid_config_reference")
    _need(all(path in used or row["kind"] in {"import", "data"}
              for path, row in files.items()), "unclassified_unused_file")
    _need(all(row["path"] in phase_paths["bandit"] for row in findings),
          "reviewed_finding_outside_scope")
    _need(review["scope_sha256"] == _scope_sha256(files, phase_paths["bandit"]),
          "bandit_scope_mismatch")
    return copy.deepcopy(m)


def _identity(path: Path, *, directory: bool) -> tuple[int, ...]:
    try:
        row = path.lstat()
    except OSError as exc:
        raise SourceStateError("missing_selected_component") from exc
    redirected = getattr(row, "st_file_attributes", 0) & 0x400
    _need(not stat.S_ISLNK(row.st_mode) and not redirected,
          "selected_path_redirection")
    _need(stat.S_ISDIR(row.st_mode) if directory else stat.S_ISREG(row.st_mode),
          "selected_path_not_regular")
    return (row.st_dev, row.st_ino, row.st_mode, row.st_nlink, row.st_size,
            row.st_mtime_ns, row.st_ctime_ns,
            getattr(row, "st_file_attributes", 0),
            getattr(row, "st_reparse_tag", 0))


def read_selected_bytes(repo_root: Path, relative_path: str,
                        expected_sha256: str) -> bytes:
    """Read one literal regular file through stable, non-redirected components."""
    path = _literal_path(relative_path)
    digest = _digest(expected_sha256, "selected_digest")
    root = Path(repo_root).absolute()
    parts = [*reversed(root.parents), root]
    selected = root
    for part in path.split("/"):
        selected = selected / part
        parts.append(selected)
    before = [_identity(item, directory=index < len(parts) - 1)
              for index, item in enumerate(parts)]
    _need(before[-1][4] <= MAX_BYTES, "selected_file_too_large")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(selected, flags)
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            _need((opened.st_dev, opened.st_ino, opened.st_mode, opened.st_size)
                  == (before[-1][0], before[-1][1], before[-1][2], before[-1][4]),
                  "selected_file_replaced")
            raw = handle.read(MAX_BYTES + 1)
    except OSError as exc:
        raise SourceStateError("selected_file_unreadable") from exc
    after = [_identity(item, directory=index < len(parts) - 1)
             for index, item in enumerate(parts)]
    _need(before == after and len(raw) == before[-1][4],
          "selected_file_replaced")
    _need(hashlib.sha256(raw).hexdigest() == digest, "selected_digest_mismatch")
    return raw


def _manifest_relative(manifest_path: str | Path, repo_root: Path) -> str:
    root = Path(repo_root).absolute()
    # Validate the supplied spelling before Path can normalize components or
    # any lstat/open occurs. Absolute Windows paths are allowed only beneath root.
    try:
        supplied = os.fspath(manifest_path)
    except TypeError as exc:
        raise SourceStateError("invalid_manifest_argument") from exc
    _need(type(supplied) is str and supplied and not supplied.startswith("\\\\"),
          "invalid_manifest_argument")
    raw = supplied.replace("\\", "/")
    _need(not raw.startswith("//")
          and not any(token in part.casefold()
                      for part in raw.split("/") for token in FORBIDDEN_TOKENS),
          "invalid_manifest_argument")
    if re.match(r"[A-Za-z]:/", raw) or raw.startswith("/"):
        prefix = root.as_posix().rstrip("/") + "/"
        _need(raw.startswith(prefix), "manifest_outside_repository")
        # Validate the exact suffix supplied by the caller before Path can
        # collapse dot components or repeated separators.
        return _literal_path(raw[len(prefix):])
    _need("\\" not in supplied, "invalid_manifest_argument")
    return _literal_path(raw)


def load_source_state(manifest_path: str | Path, *, manifest_sha256: str,
                      repo_root: Path = ROOT) -> dict[str, Any]:
    """Authenticate the manifest, validate all rows, then read selected bytes."""
    _digest(manifest_sha256, "manifest_digest")
    relative = _manifest_relative(manifest_path, repo_root)
    raw = read_selected_bytes(repo_root, relative, manifest_sha256)
    manifest = _strict_json(raw)
    state = validate_selection(manifest)
    state["selection_path"] = str(Path(repo_root).absolute() / relative)
    state["selection_sha256"] = manifest_sha256
    state["selected_bytes"] = {
        row["path"]: read_selected_bytes(repo_root, row["path"], row["sha256"])
        for row in state["files"]
    }
    return state


def require_target_runtime(target: str, *, version: tuple[int, int] | None = None) -> None:
    observed = version or (sys.version_info.major, sys.version_info.minor)
    expected = tuple(int(part) for part in target.split("."))
    if observed != expected:
        raise SourceStateError(
            f"Python target runtime mismatch: expected {target}, observed "
            f"{observed[0]}.{observed[1]}"
        )


def compile_selected_sources(state: dict[str, Any]) -> None:
    authenticated = state["selected_bytes"]
    for path in state["phases"]["compile"]:
        try:
            compile(authenticated[path], path, "exec", dont_inherit=True)
        except (KeyError, SyntaxError, ValueError) as exc:
            raise SourceStateError(f"selected Python source did not compile: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--selection-sha256", required=True)
    parser.add_argument("--require-target-runtime", action="store_true")
    args = parser.parse_args(argv)
    try:
        state = load_source_state(args.selection,
                                  manifest_sha256=args.selection_sha256)
        if args.require_target_runtime:
            require_target_runtime(state["target_python"])
        compile_selected_sources(state)
    except SourceStateError as exc:
        print(f"[source_state_failure] {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": "passed",
        "schema_version": state["schema_version"],
        "scope": state["scope"],
        "target_python": state["target_python"],
        "selected_compile_count": len(state["phases"]["compile"]),
        "repository_wide": False,
        "pending": state["completeness"]["pending"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
