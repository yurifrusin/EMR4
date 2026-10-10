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
                      repo_root: Path = ROOT,
                      require_complete: bool = False) -> dict[str, Any]:
    """Authenticate the manifest and coverage before reading selected bytes."""
    _digest(manifest_sha256, "manifest_digest")
    relative = _manifest_relative(manifest_path, repo_root)
    raw = read_selected_bytes(repo_root, relative, manifest_sha256)
    manifest = _strict_json(raw)
    state = validate_selection(manifest)
    if require_complete and (
        state["completeness"]["repository_wide"] is not True
        or state["completeness"]["pending"]
    ):
        raise SourceStateError("complete_ci_coverage_required")
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


OBLIGATION_POPULATION_SCHEMA = "emr4.ordinary_obligation_population.v1"
OBLIGATION_EVIDENCE_SCHEMA = "emr4.ordinary_obligation_evidence.v1"
OBLIGATION_REVIEWS_SCHEMA = "emr4.ordinary_obligation_review_bindings.v1"
OBLIGATION_RESULT_SCHEMA = "emr4.obligation_accounting_consistency.v1"
OBLIGATION_MAX_BYTES = 16 * 1024 * 1024
OBLIGATION_ID = re.compile(r"[A-Za-z][A-Za-z0-9_.:/\-\[\]]{0,319}\Z")


def _obligation_json(raw: bytes, label: str) -> dict[str, Any]:
    _need(type(raw) is bytes and 0 < len(raw) <= OBLIGATION_MAX_BYTES,
          f"{label}_bytes_invalid")

    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            _need(key not in result, f"{label}_duplicate_json_key")
            result[key] = value
        return result

    def nonfinite(_: str) -> None:
        raise SourceStateError(f"{label}_nonfinite_json")

    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                            parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SourceStateError(f"{label}_malformed_json") from exc
    _need(type(parsed) is dict, f"{label}_object_required")
    return parsed


def _obligation_id(value: object, label: str) -> str:
    _need(type(value) is str and OBLIGATION_ID.fullmatch(value) is not None,
          f"{label}_invalid")
    return value


def _obligation_ids(value: object, label: str) -> list[str]:
    _need(type(value) is list and bool(value), f"{label}_invalid")
    result = [_obligation_id(item, label) for item in value]
    _need(len(set(result)) == len(result), f"{label}_duplicate")
    _need(len({item.casefold() for item in result}) == len(result),
          f"{label}_case_alias")
    return result


def _same_obligation_ids(expected: set[str], observed: set[str], label: str) -> None:
    folded = {item.casefold(): item for item in expected}
    _need(not any(item.casefold() in folded and folded[item.casefold()] != item
                  for item in observed), f"{label}_case_alias")
    _need(not (expected - observed), f"{label}_missing")
    _need(not (observed - expected), f"{label}_extra")


def validate_obligation_accounting(
    population_bytes: bytes,
    evidence_bytes: bytes,
    review_bindings_bytes: bytes,
    *,
    expected_population_sha256: str,
    expected_evidence_sha256: str,
    expected_review_bindings_sha256: str,
    expected_plan_sha256: str,
    expected_authority_sha256: str,
    expected_source_sha256: str,
    expected_config_sha256: str,
    expected_runtime_sha256: str,
) -> dict[str, Any]:
    """Check accounting against caller-authenticated anchors, without I/O.

    The caller must independently authenticate population authority, exclusions,
    source/runtime relevance and the separate accepted review-bindings document.
    A consistent return is neither complete-CI nor G2 acceptance.
    """
    anchors = {
        "population": _digest(expected_population_sha256, "population_anchor_invalid"),
        "evidence": _digest(expected_evidence_sha256, "evidence_anchor_invalid"),
        "reviews": _digest(expected_review_bindings_sha256, "reviews_anchor_invalid"),
        "plan": _digest(expected_plan_sha256, "plan_anchor_invalid"),
        "authority": _digest(expected_authority_sha256, "authority_anchor_invalid"),
        "source": _digest(expected_source_sha256, "source_anchor_invalid"),
        "config": _digest(expected_config_sha256, "config_anchor_invalid"),
        "runtime": _digest(expected_runtime_sha256, "runtime_anchor_invalid"),
    }
    for label, raw in (("population", population_bytes), ("evidence", evidence_bytes),
                       ("reviews", review_bindings_bytes)):
        _need(type(raw) is bytes and 0 < len(raw) <= OBLIGATION_MAX_BYTES,
              f"{label}_bytes_invalid")
    _need(hashlib.sha256(population_bytes).hexdigest() == anchors["population"],
          "population_digest_mismatch")
    _need(hashlib.sha256(evidence_bytes).hexdigest() == anchors["evidence"],
          "evidence_digest_mismatch")
    _need(hashlib.sha256(review_bindings_bytes).hexdigest() == anchors["reviews"],
          "reviews_digest_mismatch")
    population = _keys(_obligation_json(population_bytes, "population"), {
        "schema_version", "plan_sha256", "authority_sha256", "source_sha256",
        "config_sha256", "runtime_sha256", "required_test_ids",
        "required_contribution_kinds", "obligations",
    }, "population_keys")
    evidence = _keys(_obligation_json(evidence_bytes, "evidence"), {
        "schema_version", "population_sha256", "plan_sha256", "authority_sha256",
        "source_sha256", "config_sha256", "runtime_sha256", "collection",
        "dispositions",
    }, "evidence_keys")
    reviews = _keys(_obligation_json(review_bindings_bytes, "reviews"), {
        "schema_version", "population_sha256", "plan_sha256", "authority_sha256",
        "source_sha256", "config_sha256", "runtime_sha256", "bindings",
    }, "reviews_keys")
    _need(population["schema_version"] == OBLIGATION_POPULATION_SCHEMA and
          evidence["schema_version"] == OBLIGATION_EVIDENCE_SCHEMA and
          reviews["schema_version"] == OBLIGATION_REVIEWS_SCHEMA,
          "obligation_schema_invalid")
    for key in ("plan", "authority", "source", "config", "runtime"):
        field = f"{key}_sha256"
        _need(population[field] == anchors[key] and evidence[field] == anchors[key]
              and reviews[field] == anchors[key],
              f"{key}_identity_mismatch")
    _need(evidence["population_sha256"] == anchors["population"] and
          reviews["population_sha256"] == anchors["population"],
          "evidence_population_mismatch")
    tests = _obligation_ids(population["required_test_ids"], "required_test_ids")
    kinds = _obligation_ids(population["required_contribution_kinds"],
                            "required_contribution_kinds")
    test_set, kind_set = set(tests), set(kinds)
    _need(type(population["obligations"]) is list and population["obligations"],
          "obligations_invalid")
    required: dict[str, tuple[str, str]] = {}
    required_folded: set[str] = set()
    for row in population["obligations"]:
        r = _keys(row, {"id", "test_id", "kind"}, "obligation_row_keys")
        oid = _obligation_id(r["id"], "obligation_id")
        test_id = _obligation_id(r["test_id"], "obligation_test_id")
        kind = _obligation_id(r["kind"], "obligation_kind")
        _need(oid not in required, "obligation_duplicate")
        _need(oid.casefold() not in required_folded, "obligation_case_alias")
        _need(test_id in test_set and kind in kind_set, "obligation_reference_invalid")
        required[oid] = (test_id, kind)
        required_folded.add(oid.casefold())
    _same_obligation_ids(test_set,
                         {test_id for test_id, _ in required.values()},
                         "required_test_coverage")
    _same_obligation_ids(kind_set, {kind for _, kind in required.values()},
                         "required_kind_coverage")
    _need(type(reviews["bindings"]) is list and reviews["bindings"],
          "review_bindings_invalid")
    bound_reviews: dict[str, tuple[str, str, str | None, str | None]] = {}
    bound_review_folded: set[str] = set()
    for row in reviews["bindings"]:
        r = _keys(row, {"obligation_id", "result_review_sha256",
                        "receipt_sha256", "relevance_review_sha256",
                        "prior_result_sha256"}, "review_binding_keys")
        oid = _obligation_id(r["obligation_id"], "review_binding_id")
        _need(oid not in bound_reviews, "review_binding_duplicate")
        _need(oid.casefold() not in bound_review_folded, "review_binding_case_alias")
        result_review = _digest(r["result_review_sha256"],
                                "result_review_binding_invalid")
        receipt = _digest(r["receipt_sha256"], "receipt_binding_invalid")
        relevance = r["relevance_review_sha256"]
        prior_result = r["prior_result_sha256"]
        _need(relevance is None or
              (type(relevance) is str and HEX64.fullmatch(relevance) is not None),
              "relevance_review_binding_invalid")
        _need(prior_result is None or
              (type(prior_result) is str and HEX64.fullmatch(prior_result) is not None),
              "prior_result_binding_invalid")
        _need((relevance is None) == (prior_result is None),
              "reuse_binding_incomplete")
        bound_reviews[oid] = (result_review, receipt, relevance, prior_result)
        bound_review_folded.add(oid.casefold())
    _same_obligation_ids(set(required), set(bound_reviews), "review_bindings")
    collection = _keys(evidence["collection"], {"verdict", "test_ids"},
                       "collection_keys")
    _need(collection["verdict"] == "passed", "collection_not_passed")
    collected = _obligation_ids(collection["test_ids"], "collection_test_ids")
    _same_obligation_ids(test_set, set(collected), "collection")
    _need(type(evidence["dispositions"]) is list and evidence["dispositions"],
          "dispositions_invalid")
    observed: dict[str, tuple[str, str]] = {}
    observed_folded: set[str] = set()
    for row in evidence["dispositions"]:
        r = _keys(row, {
            "obligation_id", "test_id", "kind", "source_sha256",
            "config_sha256", "runtime_sha256", "verdict", "disposition",
            "receipt_sha256", "review_sha256", "reuse",
        }, "disposition_row_keys")
        oid = _obligation_id(r["obligation_id"], "disposition_id")
        test_id = _obligation_id(r["test_id"], "disposition_test_id")
        kind = _obligation_id(r["kind"], "disposition_kind")
        _need(oid not in observed, "disposition_duplicate")
        _need(oid.casefold() not in observed_folded, "disposition_case_alias")
        _need(not (oid not in required and oid.casefold() in required_folded),
              "disposition_case_alias")
        _need(oid in required, "disposition_extra")
        _need(r["verdict"] == "passed", "disposition_not_passed")
        _need(r["disposition"] in ("current", "reused"),
              "disposition_unresolved")
        for key in ("source", "config", "runtime"):
            _need(r[f"{key}_sha256"] == anchors[key],
                  f"disposition_{key}_stale")
        _digest(r["receipt_sha256"], "disposition_receipt_invalid")
        _digest(r["review_sha256"], "disposition_review_invalid")
        _need(oid in bound_reviews and r["review_sha256"] == bound_reviews[oid][0],
              "disposition_review_unbound")
        _need(r["receipt_sha256"] == bound_reviews[oid][1],
              "disposition_receipt_unbound")
        if r["disposition"] == "current":
            _need(r["reuse"] is None, "current_disposition_has_reuse")
            _need(bound_reviews[oid][2] is None, "current_has_reuse_review")
        else:
            reuse = _keys(r["reuse"], {
                "relevance_review_sha256", "prior_result_sha256",
                "plan_sha256", "population_sha256", "source_sha256",
                "config_sha256", "runtime_sha256",
            }, "reuse_binding_keys")
            _digest(reuse["relevance_review_sha256"],
                    "reuse_relevance_review_invalid")
            _digest(reuse["prior_result_sha256"], "reuse_prior_result_invalid")
            _need(reuse["relevance_review_sha256"] == bound_reviews[oid][2] and
                  reuse["prior_result_sha256"] == bound_reviews[oid][3],
                  "reuse_relevance_unbound")
            for key in ("plan", "population", "source", "config", "runtime"):
                _need(reuse[f"{key}_sha256"] == anchors[key],
                      f"reuse_{key}_stale")
        observed[oid] = (test_id, kind)
        observed_folded.add(oid.casefold())
    missing_kinds = sorted(kind_set -
                           {kind for _, kind in observed.values()})
    _need(not missing_kinds, f"evidence_kind_missing:{missing_kinds[0]}"
          if missing_kinds else "evidence_kind_missing")
    _same_obligation_ids(set(required), set(observed), "obligations")
    _need(all(observed[oid] == expected for oid, expected in required.items()),
          "disposition_reference_mismatch")
    return {
        "schema_version": OBLIGATION_RESULT_SCHEMA,
        "status": "accounting_consistent_with_supplied_anchors",
        "population_sha256": anchors["population"],
        "evidence_sha256": anchors["evidence"],
        "review_bindings_sha256": anchors["reviews"],
        "obligations_accounted": len(required),
        "required_test_identities": len(tests),
        "required_contribution_kinds": len(kinds),
    }


COMPLETE_SCHEMA = "emr4.complete_verification_selection.v3"
COMPLETE_CONTEXT_KEYS = {
    "plan_sha256", "authority_sha256", "source_sha256", "config_sha256",
    "runtime_sha256", "verifier_sha256", "result_id",
}
COMPLETE_PROFILES = ("ci-correctness", "ci-bandit")


def _complete_text(value: object, reason: str) -> str:
    _need(type(value) is str and 0 < len(value) <= 2048
          and value == value.strip() and not any(ord(c) < 32 for c in value), reason)
    return value


def _complete_context(value: object) -> dict[str, Any]:
    context = _keys(value, COMPLETE_CONTEXT_KEYS, "complete_context_keys")
    for key in COMPLETE_CONTEXT_KEYS - {"result_id"}:
        _digest(context[key], "complete_context_digest")
    _complete_text(context["result_id"], "complete_result_identity")
    return context


def _complete_at(value: Any, path: object) -> Any:
    """Select inert JSON members only; no expression or file evaluation."""
    _need(type(path) is list and len(path) <= 16, "complete_json_path")
    for part in path:
        if type(part) is str:
            _complete_text(part, "complete_json_path")
            _need(type(value) is dict and part in value, "complete_json_member")
        else:
            _need(type(part) is int and type(value) is list
                  and 0 <= part < len(value), "complete_json_index")
        value = value[part]
    return value


def load_complete_context(path: str, *, sha256: str,
                          repo_root: Path = ROOT) -> dict[str, Any]:
    """Read caller-pinned context; the reviewed parent establishes its truth.

    In particular the parent authenticates verifier/import code, the current
    immutable source/configuration snapshot, and native reviewer independence.
    Computing this pin from the candidate is not a supported trust boundary.
    """
    _digest(sha256, "trusted_context_digest")
    relative = _manifest_relative(path, repo_root)
    context = _keys(_strict_json(read_selected_bytes(repo_root, relative, sha256)),
                    {"schema_version", "context", "reviewers", "implementers"},
                    "trusted_context_keys")
    _need(context["schema_version"] == "emr4.trusted_verification_context.v1",
          "trusted_context_schema")
    _complete_context(context["context"])
    reviewers = _obligation_ids(context["reviewers"], "trusted_reviewers")
    implementers = _obligation_ids(context["implementers"], "trusted_implementers")
    _need(not ({v.casefold() for v in reviewers} &
               {v.casefold() for v in implementers}), "reviewer_not_independent")
    return context


def load_complete_selection(path: str, *, selection_sha256: str,
                            trusted_context: dict[str, Any],
                            repo_root: Path = ROOT) -> dict[str, Any]:
    """Authenticate already accepted complete proof, then bounded targets.

    The caller-pinned acceptance document normalizes independent judgments of
    original result/cleanup/relevance receipts, which retain their own bytes and
    historical contexts. It is not a new execution receipt or a signature check.
    No contribution can be filled by a command that has yet to run.
    """
    trusted = _keys(trusted_context,
                    {"schema_version", "context", "reviewers", "implementers"},
                    "trusted_context_keys")
    _need(trusted["schema_version"] == "emr4.trusted_verification_context.v1",
          "trusted_context_schema")
    context = _complete_context(trusted["context"])
    reviewers = set(_obligation_ids(trusted["reviewers"], "trusted_reviewers"))
    implementers = set(_obligation_ids(trusted["implementers"], "trusted_implementers"))
    _need(not ({v.casefold() for v in reviewers} &
               {v.casefold() for v in implementers}), "reviewer_not_independent")
    relative = _manifest_relative(path, repo_root)
    raw = read_selected_bytes(repo_root, relative,
                              _digest(selection_sha256, "manifest_digest"))
    wrapper = _keys(_strict_json(raw), {
        "schema_version", "context", "bounded_selection", "plan", "population",
        "evidence", "review_bindings", "test_identity_map", "acceptance",
        "required_checks", "artifacts",
    }, "complete_selection_keys")
    _need(wrapper["schema_version"] == COMPLETE_SCHEMA, "complete_selection_schema")
    _need(_complete_context(wrapper["context"]) == context, "stale_trusted_context")
    roles = {"selection", "plan", "population", "evidence", "review_bindings",
             "test_identity_map", "acceptance", "support"}
    _need(type(wrapper["artifacts"]) is list
          and 0 < len(wrapper["artifacts"]) <= 256, "complete_artifact_count")
    artifacts: dict[str, dict[str, Any]] = {}
    names: set[str] = set()
    paths: set[str] = {relative.casefold()}
    total = 0
    for row in wrapper["artifacts"]:
        item = _keys(row, {"id", "path", "bytes", "sha256", "role"},
                     "complete_artifact_keys")
        aid = _obligation_id(item["id"], "complete_artifact_id")
        literal = _literal_path(item["path"])
        _digest(item["sha256"], "complete_artifact_digest")
        _need(type(item["bytes"]) is int and 0 < item["bytes"] <= MAX_BYTES,
              "complete_artifact_size")
        _need(type(item["role"]) is str and item["role"] in roles,
              "complete_artifact_role")
        _need(aid.casefold() not in names and literal.casefold() not in paths,
              "complete_artifact_alias")
        names.add(aid.casefold())
        paths.add(literal.casefold())
        total += item["bytes"]
        artifacts[aid] = item
    _need(total <= 32 * 1024 * 1024, "complete_artifact_total_size")
    used: set[str] = set()

    def reference(aid: object, role: str) -> dict[str, Any]:
        _need(type(aid) is str and aid in artifacts
              and artifacts[aid]["role"] == role, "complete_artifact_reference")
        used.add(aid)
        return artifacts[aid]

    for key in ("plan", "population", "evidence", "review_bindings",
                "test_identity_map", "acceptance"):
        reference(wrapper[key], key)
    bounded = reference(wrapper["bounded_selection"], "selection")
    _need(type(wrapper["required_checks"]) is list and wrapper["required_checks"],
          "complete_checks_empty")
    checks: dict[str, dict[str, Any]] = {}
    for row in wrapper["required_checks"]:
        check = _keys(row, {"id", "receipt", "result", "cleanup", "result_review",
                           "prior_result", "relevance_review"}, "complete_check_keys")
        cid = _obligation_id(check["id"], "complete_check_id")
        _need(cid.casefold() not in {k.casefold() for k in checks},
              "complete_check_alias")
        for key in ("receipt", "result", "cleanup", "result_review"):
            reference(check[key], "support")
        _need((check["prior_result"] is None) ==
              (check["relevance_review"] is None), "complete_reuse_incomplete")
        if check["prior_result"] is not None:
            reference(check["prior_result"], "support")
            reference(check["relevance_review"], "support")
        checks[cid] = check

    # Only the bounded command manifest is read before all selected-target
    # collisions can be rejected. No selected product source is read here.
    bounded_raw = read_selected_bytes(repo_root, bounded["path"], bounded["sha256"])
    _need(len(bounded_raw) == bounded["bytes"], "complete_artifact_length")
    bounded_manifest = validate_selection(_strict_json(bounded_raw))
    targets = {row["path"].casefold() for row in bounded_manifest["files"]}
    _need(not (targets & paths), "proof_target_collision")
    payloads: dict[str, bytes] = {wrapper["bounded_selection"]: bounded_raw}
    for aid, item in artifacts.items():
        if aid not in payloads:
            payloads[aid] = read_selected_bytes(repo_root, item["path"], item["sha256"])
            _need(len(payloads[aid]) == item["bytes"], "complete_artifact_length")

    def document(aid: str) -> Any:
        return _strict_json(payloads[aid])

    plan = _keys(document(wrapper["plan"]), {
        "schema_version", "authority_sha256", "source_sha256", "config_sha256",
        "runtime_sha256", "verifier_sha256", "result_id", "profiles", "checks",
    }, "complete_plan_keys")
    _need(plan["schema_version"] == "emr4.required_verification_plan.v1",
          "complete_plan_schema")
    _need(artifacts[wrapper["plan"]]["sha256"] == context["plan_sha256"],
          "complete_plan_unbound")
    _need(all(plan[k] == context[k] for k in COMPLETE_CONTEXT_KEYS - {"plan_sha256"}),
          "complete_plan_context")
    _need(plan["profiles"] == list(COMPLETE_PROFILES), "complete_required_profiles")
    _need(type(plan["checks"]) is list and plan["checks"], "complete_plan_checks")
    planned: dict[str, dict[str, Any]] = {}
    for row in plan["checks"]:
        check = _keys(row, {"id", "type", "kind", "test_ids"}, "complete_plan_check_keys")
        cid = _obligation_id(check["id"], "complete_check_id")
        _obligation_id(check["kind"], "complete_check_kind")
        _need(cid.casefold() not in {k.casefold() for k in planned}, "complete_plan_alias")
        _need(check["type"] in ("test-linked", "standalone"), "complete_check_type")
        if check["type"] == "test-linked":
            _obligation_ids(check["test_ids"], "complete_check_test_ids")
        else:
            _need(check["test_ids"] == [], "standalone_invented_test")
        planned[cid] = check
    _same_obligation_ids(set(planned), set(checks), "complete_required_checks")
    accounting = validate_obligation_accounting(
        payloads[wrapper["population"]], payloads[wrapper["evidence"]],
        payloads[wrapper["review_bindings"]],
        expected_population_sha256=artifacts[wrapper["population"]]["sha256"],
        expected_evidence_sha256=artifacts[wrapper["evidence"]]["sha256"],
        expected_review_bindings_sha256=artifacts[wrapper["review_bindings"]]["sha256"],
        **{f"expected_{key}_sha256": context[f"{key}_sha256"]
           for key in ("plan", "authority", "source", "config", "runtime")},
    )
    population = document(wrapper["population"])
    dispositions = document(wrapper["evidence"])["dispositions"]
    linked = [(tid, row["kind"]) for row in planned.values()
              if row["type"] == "test-linked" for tid in row["test_ids"]]
    _need(len(set(linked)) == len(linked) and set(linked) ==
          {(row["test_id"], row["kind"]) for row in population["obligations"]},
          "complete_test_linkage")
    for cid, planned_check in planned.items():
        if planned_check["type"] != "test-linked":
            continue
        check = checks[cid]
        for row in dispositions:
            if row["test_id"] not in planned_check["test_ids"] or row["kind"] != planned_check["kind"]:
                continue
            _need(row["receipt_sha256"] == artifacts[check["receipt"]]["sha256"]
                  and row["review_sha256"] == artifacts[check["result_review"]]["sha256"],
                  "complete_test_receipt_unbound")
            reused = check["prior_result"] is not None
            _need(row["disposition"] == ("reused" if reused else "current"),
                  "complete_test_disposition_mismatch")
            if reused:
                _need(row["reuse"]["prior_result_sha256"] ==
                      artifacts[check["prior_result"]]["sha256"]
                      and row["reuse"]["relevance_review_sha256"] ==
                      artifacts[check["relevance_review"]]["sha256"],
                      "complete_test_relevance_unbound")
    identities = _keys(document(wrapper["test_identity_map"]),
                       {"schema_version", "rows", "cohorts"}, "complete_identity_keys")
    _need(identities["schema_version"] == "emr4.collected_test_identity_map.v1",
          "complete_identity_schema")
    _need(type(identities["rows"]) is list and type(identities["cohorts"]) is list
          and identities["rows"] and identities["cohorts"], "complete_identity_empty")
    mapped: dict[str, tuple[str, str]] = {}
    mapped_pairs: set[tuple[str, str]] = set()
    for row in identities["rows"]:
        item = _keys(row, {"id", "nodeid", "cohort_id"}, "complete_identity_row_keys")
        tid = _obligation_id(item["id"], "complete_test_id")
        node = _complete_text(item["nodeid"], "complete_nodeid")
        cohort = _obligation_id(item["cohort_id"], "complete_cohort_id")
        pair = (cohort.casefold(), node.casefold())
        _need(tid.casefold() not in {k.casefold() for k in mapped}
              and pair not in mapped_pairs, "complete_identity_alias")
        mapped[tid] = (cohort, node)
        mapped_pairs.add(pair)
    _same_obligation_ids(set(population["required_test_ids"]), set(mapped),
                         "complete_mapped_tests")
    seen_cohorts: set[str] = set()
    cohort_result_artifacts: dict[str, str] = {}
    for row in identities["cohorts"]:
        cohort = _keys(row, {
            "id", "collection_artifact", "collection_path", "collection_node_key",
            "result_artifact", "result_path", "result_layout", "result_node_key",
            "result_phase_key", "result_outcome_key",
        }, "complete_cohort_keys")
        cid = _obligation_id(cohort["id"], "complete_cohort_id")
        _need(cid.casefold() not in {v.casefold() for v in seen_cohorts},
              "complete_cohort_alias")
        seen_cohorts.add(cid)
        cohort_result_artifacts[cid] = cohort["result_artifact"]
        for key in ("collection_artifact", "result_artifact"):
            reference(cohort[key], "support")
        collected_rows = _complete_at(document(cohort["collection_artifact"]),
                                      cohort["collection_path"])
        _need(type(collected_rows) is list, "complete_collection_rows")
        key = cohort["collection_node_key"]
        if key is not None:
            _complete_text(key, "complete_collection_key")
        collected = [_complete_text(_complete_at(row, [key]) if key is not None else row,
                                    "complete_collected_node") for row in collected_rows]
        expected = {node for group, node in mapped.values() if group == cid}
        _need(expected and len(set(collected)) == len(collected)
              and set(collected) == expected, "complete_collection_mismatch")
        result_rows = _complete_at(document(cohort["result_artifact"]), cohort["result_path"])
        _need(type(result_rows) is list, "complete_result_rows")
        _need(cohort["result_layout"] in ("phase-rows", "nested-phases"),
              "complete_result_layout")
        nk = _complete_text(cohort["result_node_key"], "complete_result_key")
        ok = _complete_text(cohort["result_outcome_key"], "complete_result_key")
        phases: set[tuple[str, str]] = set()
        for result_row in result_rows:
            node = _complete_text(_complete_at(result_row, [nk]), "complete_result_node")
            if cohort["result_layout"] == "phase-rows":
                pk = _complete_text(cohort["result_phase_key"], "complete_result_key")
                outcomes = [(_complete_at(result_row, [pk]),
                             _complete_at(result_row, [ok]))]
            else:
                _need(cohort["result_phase_key"] is None, "complete_nested_phase_key")
                outcomes = [(phase, _complete_at(result_row, [phase, ok]))
                            for phase in ("setup", "call", "teardown")]
            for phase, outcome in outcomes:
                _need(node in expected and phase in ("setup", "call", "teardown")
                      and outcome == "passed", "complete_test_phase_not_passed")
                _need((node, phase) not in phases, "complete_test_phase_duplicate")
                phases.add((node, phase))
        _need(phases == {(node, phase) for node in expected
                         for phase in ("setup", "call", "teardown")},
              "complete_test_phase_missing")
    _need(seen_cohorts == {group for group, _ in mapped.values()}, "complete_cohort_mismatch")
    for cid, check in planned.items():
        if check["type"] == "test-linked":
            _need(all(cohort_result_artifacts[mapped[tid][0]] == checks[cid]["result"]
                      for tid in check["test_ids"]), "complete_test_result_unbound")

    acceptance = _keys(document(wrapper["acceptance"]), {
        "schema_version", "context", "verdict", "reviewer_id", "implementer_ids",
        "population_sha256", "test_identity_map_sha256", "pending", "bindings",
    }, "complete_acceptance_keys")
    _need(acceptance["schema_version"] == "emr4.complete_evidence_acceptance.v1"
          and acceptance["verdict"] == "accepted" and acceptance["pending"] == [],
          "complete_evidence_not_accepted")
    _need(_complete_context(acceptance["context"]) == context, "complete_acceptance_context")
    reviewer = _obligation_id(acceptance["reviewer_id"], "complete_acceptance_reviewer")
    _need(reviewer in reviewers
          and set(_obligation_ids(acceptance["implementer_ids"], "acceptance_implementers"))
          == implementers, "complete_acceptance_independence")
    for key in ("population", "test_identity_map"):
        _need(acceptance[f"{key}_sha256"] == artifacts[wrapper[key]]["sha256"],
              "complete_acceptance_subject")
    _need(type(acceptance["bindings"]) is list, "complete_acceptance_bindings")
    accepted: set[str] = set()
    for row in acceptance["bindings"]:
        decision = _keys(row, {
            "id", "verdict", "cleanup_verdict", "disposition", "receipt_sha256",
            "result_sha256", "cleanup_sha256", "result_review_sha256",
            "prior_result_sha256", "relevance_review_sha256", "historical_source_sha256",
            "historical_config_sha256", "historical_runtime_sha256",
        }, "complete_acceptance_binding_keys")
        cid = _obligation_id(decision["id"], "complete_check_id")
        _need(cid in checks and cid not in accepted, "complete_acceptance_check")
        _need(decision["verdict"] == "passed" and decision["cleanup_verdict"] == "accepted",
              "complete_check_not_passed")
        check = checks[cid]
        for key in ("receipt", "result", "cleanup", "result_review", "prior_result",
                    "relevance_review"):
            expected_digest = artifacts[check[key]]["sha256"] if check[key] is not None else None
            _need(decision[f"{key}_sha256"] == expected_digest, "complete_check_receipt_unbound")
        _need(decision["disposition"] ==
              ("reused" if check["prior_result"] is not None else "current"),
              "complete_disposition_mismatch")
        for key in ("source", "config", "runtime"):
            historical = _digest(decision[f"historical_{key}_sha256"],
                                  "complete_historical_context")
            if decision["disposition"] == "current":
                _need(historical == context[f"{key}_sha256"], "complete_current_context_stale")
        accepted.add(cid)
    _same_obligation_ids(set(planned), accepted, "complete_accepted_checks")
    _need(used == set(artifacts), "complete_unused_artifact")
    # Authenticate selected sources only after the complete proof has passed.
    bounded_state = load_source_state(bounded["path"], manifest_sha256=bounded["sha256"],
                                      repo_root=repo_root)
    return {
        "bounded_state": bounded_state,
        "coverage": {"status": "authenticated_accepted_complete_evidence",
                     "result_id": context["result_id"], "selection_sha256": selection_sha256,
                     "test_identities": len(mapped), "cohorts": len(seen_cohorts),
                     "standalone_checks": sum(row["type"] == "standalone"
                                              for row in planned.values()),
                     "collection_basis": "accepted_union_of_collections",
                     "accounting": accounting, "required_profiles": list(COMPLETE_PROFILES)},
    }


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
