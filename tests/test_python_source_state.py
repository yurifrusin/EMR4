"""Synthetic acceptance cases for the bounded CI-A source selection.

This file is a source-only candidate. Run it only in the reviewed isolated capsule.
"""

from __future__ import annotations

import copy
from contextlib import contextmanager
import builtins
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Iterator

import pytest


SCHEMA = "emr4.python_source_state.v2"
SELECTION = "config/selection.json"
GOOD_SOURCE = b"VALUE = 1\n"
GOOD_TEST = b"def test_synthetic():\n    assert True\n"
GOOD_NOTE = b"A synthetic ordinary note.\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _scope_digest(manifest: dict) -> str:
    by_path = {row["path"]: row["sha256"] for row in manifest["files"]}
    pairs = [[path, by_path[path]] for path in sorted(manifest["phases"]["bandit"])]
    return _sha(json.dumps(pairs, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def _write_manifest(root: Path, manifest: dict) -> tuple[Path, str]:
    path = root / SELECTION
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    path.write_bytes(data)
    return path, _sha(data)


def _selection(tmp_path: Path) -> tuple[Path, Path, str, dict]:
    root = tmp_path / "ordinary_repo"
    content = {
        "safe.py": GOOD_SOURCE,
        "tests/test_safe.py": GOOD_TEST,
        "docs/note.md": GOOD_NOTE,
        "config/ruff.toml": b"target-version = 'py311'\n",
        "config/bandit.json": b"{}\n",
        "config/pytest.ini": b"[pytest]\n",
    }
    for relative, data in content.items():
        path = root.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    kinds = {
        "safe.py": "source",
        "tests/test_safe.py": "test",
        "docs/note.md": "data",
        "config/ruff.toml": "config",
        "config/bandit.json": "config",
        "config/pytest.ini": "config",
    }
    manifest = {
        "schema_version": SCHEMA,
        "target_python": "3.11",
        "scope": "bounded_ordinary_verification",
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "completeness": {
            "repository_wide": False,
            "pending": ["synthetic ordinary population is intentionally bounded"],
        },
        "files": [
            {"path": path, "sha256": _sha(data), "kind": kinds[path]}
            for path, data in content.items()
        ],
        "phases": {
            "compile": ["safe.py", "tests/test_safe.py"],
            "ruff": ["safe.py", "tests/test_safe.py"],
            "bandit": ["safe.py"],
            "leakage": ["docs/note.md"],
            "tests": ["tests/test_safe.py::test_synthetic"],
        },
        "configs": {
            "ruff": "config/ruff.toml",
            "bandit": "config/bandit.json",
            "pytest": "config/pytest.ini",
        },
        "bandit_review": {
            "status": "pending",
            "scope_sha256": "",
            "reviewed_findings": [],
        },
    }
    manifest["bandit_review"]["scope_sha256"] = _scope_digest(manifest)
    path, digest = _write_manifest(root, manifest)
    return root, path, digest, manifest


def _load(root: Path, path: Path, digest: str) -> dict:
    from scripts.python_source_state import load_source_state

    return load_source_state(path, manifest_sha256=digest, repo_root=root)


def _assert_valid_control(root: Path, path: Path, digest: str) -> None:
    state = _load(root, path, digest)
    assert state["schema_version"] == SCHEMA
    assert state["selection_sha256"] == digest


def _allow_only_manifest_read(
    monkeypatch: pytest.MonkeyPatch, source_state, root: Path, external_digest: str
) -> None:
    """Preserve the loader's authenticated manifest read, never a selected target."""

    real_read = source_state.read_selected_bytes

    def manifest_only(repo_root: Path, relative_path: str, expected_sha256: str) -> bytes:
        if (
            Path(repo_root) != root
            or str(relative_path) != SELECTION
            or expected_sha256 != external_digest
        ):
            raise AssertionError("selected target read before manifest validation")
        return real_read(repo_root, relative_path, expected_sha256)

    monkeypatch.setattr(source_state, "read_selected_bytes", manifest_only)


@contextmanager
def _block_fixture_target_observation(
    monkeypatch: pytest.MonkeyPatch, root: Path, manifest_path: Path
) -> Iterator[None]:
    """Allow the one manifest read, but catch any premature fixture-target I/O."""

    allowed = {root, manifest_path, *manifest_path.parents}

    def fixture_path(candidate: object) -> Path | None:
        try:
            raw = os.fspath(candidate)
        except TypeError:
            return None
        if isinstance(raw, bytes):
            raw = os.fsdecode(raw)
        path = Path(raw)
        if not path.is_absolute():
            path = Path.cwd() / path
        try:
            path.relative_to(root)
        except ValueError:
            return None
        return path

    def guard(original, *, directory_listing: bool = False):
        def wrapped(candidate, *args, **kwargs):
            path = fixture_path(candidate)
            if path is not None and (directory_listing or path not in allowed):
                raise AssertionError(f"selected target observed before validation: {candidate}")
            return original(candidate, *args, **kwargs)
        return wrapped

    with monkeypatch.context() as patch:
        for owner, names in (
            (Path, ("resolve", "stat", "lstat", "open", "read_bytes", "read_text",
                    "iterdir", "glob", "rglob")),
            (os, ("stat", "lstat", "open", "scandir", "listdir")),
            (builtins, ("open",)),
            (io, ("open",)),
        ):
            for name in names:
                patch.setattr(
                    owner, name,
                    guard(getattr(owner, name), directory_listing=name in
                          {"iterdir", "glob", "rglob", "scandir", "listdir"}),
                )
        yield


@contextmanager
def _block_all_observation(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Prove the structural validator needs no filesystem or process effects."""

    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("pure selection validation observed external state")

    with monkeypatch.context() as patch:
        for owner, names in (
            (Path, ("resolve", "stat", "lstat", "open", "read_bytes", "read_text",
                    "iterdir", "glob", "rglob")),
            (os, ("stat", "lstat", "open", "scandir", "listdir", "getcwd")),
            (builtins, ("open",)),
            (io, ("open",)),
            (subprocess, ("run", "Popen")),
        ):
            for name in names:
                patch.setattr(owner, name, forbidden)
        yield


def test_valid_v2_selection_compiles_authenticated_bytes_after_disk_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    state = _load(root, path, digest)
    assert state["selection_path"] == str(path.absolute())
    assert state["selection_sha256"] == digest
    assert state["schema_version"] == SCHEMA
    assert state["target_python"] == "3.11"
    assert state["completeness"]["repository_wide"] is False
    assert source_state.read_selected_bytes(root, "safe.py", _sha(GOOD_SOURCE)) == GOOD_SOURCE

    # A later disk mutation cannot replace the bytes that were authenticated.
    (root / "safe.py").write_bytes(b"def changed(:\n")
    def forbidden_second_read(*_args: object, **_kwargs: object) -> bytes:
        raise AssertionError("compilation reread a selected disk path")

    monkeypatch.setattr(source_state, "read_selected_bytes", forbidden_second_read)
    source_state.compile_selected_sources(state)
    assert not (root / "__pycache__").exists()
    assert not (root / "tests/__pycache__").exists()


def test_validate_selection_is_pure_for_valid_and_invalid_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import python_source_state as source_state

    _, _, _, manifest = _selection(tmp_path)
    invalid = copy.deepcopy(manifest)
    invalid["files"][-1]["path"] = "pkg/*.py"
    invalid["configs"]["pytest"] = "pkg/*.py"
    with _block_all_observation(monkeypatch):
        validated = source_state.validate_selection(copy.deepcopy(manifest))
        assert isinstance(validated, dict)
        assert validated["schema_version"] == SCHEMA
        with pytest.raises(source_state.SourceStateError, match="invalid_literal_path"):
            source_state.validate_selection(invalid)


def test_authenticated_invalid_syntax_rejects_without_executing_source(
    tmp_path: Path,
) -> None:
    from scripts import python_source_state as source_state

    root, base_path, base_digest, manifest = _selection(tmp_path)
    _assert_valid_control(root, base_path, base_digest)
    source_state.compile_selected_sources(_load(root, base_path, base_digest))
    marker = root / "executed.marker"
    unsafe_syntax = (
        f"open({str(marker)!r}, 'w').write('executed')\n"
        "def broken(:\n"
    ).encode("utf-8")
    (root / "safe.py").write_bytes(unsafe_syntax)
    next(row for row in manifest["files"] if row["path"] == "safe.py")["sha256"] = _sha(unsafe_syntax)
    manifest["bandit_review"]["scope_sha256"] = _scope_digest(manifest)
    path, digest = _write_manifest(root, manifest)
    state = _load(root, path, digest)
    with pytest.raises(source_state.SourceStateError,
                       match="selected Python source did not compile"):
        source_state.compile_selected_sources(state)
    assert not marker.exists()


def test_authenticated_valid_source_is_compiled_but_never_executed(tmp_path: Path) -> None:
    from scripts import python_source_state as source_state

    root, _, _, manifest = _selection(tmp_path)
    marker = root / "executed.marker"
    executable_source = f"open({str(marker)!r}, 'w').write('executed')\n".encode("utf-8")
    (root / "safe.py").write_bytes(executable_source)
    next(row for row in manifest["files"] if row["path"] == "safe.py")["sha256"] = _sha(executable_source)
    manifest["bandit_review"]["scope_sha256"] = _scope_digest(manifest)
    path, digest = _write_manifest(root, manifest)
    source_state.compile_selected_sources(_load(root, path, digest))
    assert not marker.exists()
    assert not (root / "__pycache__").exists()


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        pytest.param("path", "../escape.py", id="parent-escape"),
        pytest.param("path", "/absolute.py", id="absolute"),
        pytest.param("path", "safe\\module.py", id="backslash"),
        pytest.param("path", "pkg/*.py", id="glob"),
        pytest.param("path", "-r.py", id="option-like"),
        pytest.param("path", "aux.py", id="windows-device"),
        pytest.param("path", "safe.py.", id="trailing-dot"),
        pytest.param("path", "safe.py ", id="trailing-space"),
        pytest.param("path", "synthetic-holdout.py", id="prohibited-token"),
        pytest.param("digest", "malformed-digest", id="malformed-digest"),
        pytest.param("kind", "unknown", id="unknown-kind"),
    ],
)
def test_invalid_file_rows_reject_before_any_selected_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
    value: str,
) -> None:
    from scripts import python_source_state as source_state

    root, base_path, base_digest, base = _selection(tmp_path)
    _assert_valid_control(root, base_path, base_digest)
    manifest = copy.deepcopy(base)
    row = copy.deepcopy(manifest["files"][0])
    row["path"] = "late_extra.py"
    row[{"path": "path", "digest": "sha256", "kind": "kind"}[mutation]] = value
    manifest["files"].append(row)  # Deliberately late: all rows precede every target read.
    path, digest = _write_manifest(root, manifest)

    _allow_only_manifest_read(monkeypatch, source_state, root, digest)
    expected_reason = {
        "path": "invalid_literal_path",
        "digest": "file_digest",
        "kind": "duplicate_or_unclassified_file",
    }[mutation]
    with _block_fixture_target_observation(monkeypatch, root, path):
        with pytest.raises(source_state.SourceStateError, match=expected_reason):
            source_state.load_source_state(path, manifest_sha256=digest, repo_root=root)


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("duplicate_file", id="duplicate-file"),
        pytest.param("case_alias", id="case-alias"),
        pytest.param("duplicate_phase", id="duplicate-phase"),
        pytest.param("unknown_phase_path", id="unknown-phase-path"),
        pytest.param("empty_phase", id="empty-phase"),
        pytest.param("unclassified_source", id="unclassified-source"),
        pytest.param("unknown_config", id="unknown-config"),
        pytest.param("duplicate_test_node", id="duplicate-test-node"),
        pytest.param("option_test_node", id="option-test-node"),
    ],
)
def test_cross_references_reject_before_any_selected_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    from scripts import python_source_state as source_state

    root, base_path, base_digest, base = _selection(tmp_path)
    _assert_valid_control(root, base_path, base_digest)
    manifest = copy.deepcopy(base)
    if mutation == "duplicate_file":
        manifest["files"].append(copy.deepcopy(manifest["files"][0]))
    elif mutation == "case_alias":
        alias = copy.deepcopy(manifest["files"][0])
        alias["path"] = "SAFE.py"
        manifest["files"].append(alias)
    elif mutation == "duplicate_phase":
        manifest["phases"]["ruff"].append("safe.py")
    elif mutation == "unknown_phase_path":
        manifest["phases"]["ruff"].append("missing.py")
    elif mutation == "empty_phase":
        manifest["phases"]["ruff"] = []
    elif mutation == "unclassified_source":
        manifest["phases"]["ruff"].remove("safe.py")
        manifest["phases"]["compile"].remove("safe.py")
        manifest["phases"]["bandit"].remove("safe.py")
        manifest["phases"]["bandit"] = ["tests/test_safe.py"]
        manifest["bandit_review"]["scope_sha256"] = _scope_digest(manifest)
    elif mutation == "unknown_config":
        manifest["files"] = [
            row for row in manifest["files"] if row["path"] != "config/ruff.toml"
        ]
        manifest["configs"]["ruff"] = "missing.toml"
    elif mutation == "duplicate_test_node":
        manifest["phases"]["tests"].append("tests/test_safe.py::test_synthetic")
    elif mutation == "option_test_node":
        manifest["phases"]["tests"] = ["tests/test_safe.py::-k"]
    path, digest = _write_manifest(root, manifest)

    _allow_only_manifest_read(monkeypatch, source_state, root, digest)
    expected_reason = {
        "duplicate_file": "duplicate_or_unclassified_file",
        "case_alias": "duplicate_or_unclassified_file",
        "duplicate_phase": "duplicate_phase_entry",
        "unknown_phase_path": "unknown_phase_path",
        "empty_phase": "empty_phase",
        "unclassified_source": "unclassified_unused_file",
        "unknown_config": "invalid_config_reference",
        "duplicate_test_node": "duplicate_phase_entry",
        "option_test_node": "invalid_test_node",
    }[mutation]
    with _block_fixture_target_observation(monkeypatch, root, path):
        with pytest.raises(source_state.SourceStateError, match=expected_reason):
            source_state.load_source_state(path, manifest_sha256=digest, repo_root=root)


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("schema", id="schema"),
        pytest.param("missing_key", id="missing-key"),
        pytest.param("extra_key", id="extra-key"),
        pytest.param("source_commit", id="source-commit"),
        pytest.param("source_tree", id="source-tree"),
        pytest.param("repository_wide", id="repository-wide"),
        pytest.param("empty_pending", id="empty-pending"),
        pytest.param("scope_digest", id="scope-digest"),
    ],
)
def test_schema_and_provenance_reject_before_selected_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str
) -> None:
    from scripts import python_source_state as source_state

    root, base_path, base_digest, base = _selection(tmp_path)
    _assert_valid_control(root, base_path, base_digest)
    manifest = copy.deepcopy(base)
    if mutation == "schema":
        manifest["schema_version"] = "emr4.python_source_state.v1"
    elif mutation == "missing_key":
        del manifest["scope"]
    elif mutation == "extra_key":
        manifest["allow_recursive"] = True
    elif mutation == "source_commit":
        manifest["source_commit"] = "not-a-commit"
    elif mutation == "source_tree":
        manifest["source_tree"] = "A" * 40
    elif mutation == "repository_wide":
        manifest["completeness"]["repository_wide"] = True
    elif mutation == "empty_pending":
        manifest["completeness"]["pending"] = []
    elif mutation == "scope_digest":
        manifest["bandit_review"]["scope_sha256"] = "0" * 64
    path, digest = _write_manifest(root, manifest)

    _allow_only_manifest_read(monkeypatch, source_state, root, digest)
    expected_reason = {
        "schema": "selection_identity",
        "missing_key": "selection_keys",
        "extra_key": "selection_keys",
        "source_commit": "selection_source_identity",
        "source_tree": "selection_source_identity",
        "repository_wide": "bounded_completeness_required",
        "empty_pending": "bounded_completeness_required",
        "scope_digest": "bandit_scope_mismatch",
    }[mutation]
    with _block_fixture_target_observation(monkeypatch, root, path):
        with pytest.raises(source_state.SourceStateError, match=expected_reason):
            source_state.load_source_state(path, manifest_sha256=digest, repo_root=root)


def test_manifest_digest_mismatch_rejects_before_target_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    _allow_only_manifest_read(monkeypatch, source_state, root, "0" * 64)
    with _block_fixture_target_observation(monkeypatch, root, path):
        with pytest.raises(source_state.SourceStateError, match="selected_digest_mismatch"):
            source_state.load_source_state(path, manifest_sha256="0" * 64, repo_root=root)


def test_malformed_authenticated_manifest_is_rejected(tmp_path: Path) -> None:
    from scripts.python_source_state import SourceStateError

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    malformed = b'{"schema_version":'
    path.write_bytes(malformed)
    with pytest.raises(SourceStateError, match="malformed_selection_json"):
        _load(root, path, _sha(malformed))


@pytest.mark.parametrize(
    ("malformed", "reason"),
    [
        pytest.param(b'{"schema_version":1,"schema_version":2}',
                     "duplicate_selection_json_key", id="duplicate-key"),
        pytest.param(b'{"schema_version":NaN}',
                     "nonfinite_selection_json", id="nonfinite"),
    ],
)
def test_authenticated_json_rejects_ambiguous_or_nonfinite_values(
    tmp_path: Path, malformed: bytes, reason: str
) -> None:
    from scripts.python_source_state import SourceStateError

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    path.write_bytes(malformed)
    with pytest.raises(SourceStateError, match=reason):
        _load(root, path, _sha(malformed))


@pytest.mark.parametrize(
    "manifest_type",
    [pytest.param("missing", id="missing"), pytest.param("directory", id="directory")],
)
def test_missing_or_directory_manifest_is_rejected(
    tmp_path: Path, manifest_type: str
) -> None:
    from scripts.python_source_state import SourceStateError

    root, base_path, base_digest, _ = _selection(tmp_path)
    _assert_valid_control(root, base_path, base_digest)
    path = root / ("config/missing.json" if manifest_type == "missing" else "config")
    expected_reason = (
        "missing_selected_component" if manifest_type == "missing"
        else "selected_path_not_regular"
    )
    with pytest.raises(SourceStateError, match=expected_reason):
        _load(root, path, "0" * 64)


@pytest.mark.parametrize(
    "relative",
    [
        pytest.param("synthetic-holdout/selection.json", id="prohibited-token"),
        pytest.param("aux.json", id="windows-device"),
        pytest.param("config/selection.json.", id="trailing-dot"),
        pytest.param("config/../escape.json", id="parent-escape"),
        pytest.param("config/*.json", id="glob"),
    ],
)
def test_manifest_argument_rejects_before_any_physical_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    from scripts import python_source_state as source_state

    root, base_path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, base_path, digest)
    bad = root.joinpath(*relative.split("/"))
    expected_reason = (
        "invalid_manifest_argument"
        if relative == "synthetic-holdout/selection.json"
        else "invalid_literal_path"
    )

    with _block_all_observation(monkeypatch):
        with pytest.raises(source_state.SourceStateError, match=expected_reason):
            source_state.load_source_state(bad, manifest_sha256=digest, repo_root=root)


@pytest.mark.parametrize(
    "bad_digest",
    [
        pytest.param("", id="empty"),
        pytest.param("A" * 64, id="uppercase"),
        pytest.param("0" * 63, id="short"),
        pytest.param("not-a-digest", id="nondigest"),
    ],
)
def test_manifest_digest_argument_rejects_before_manifest_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_digest: str
) -> None:
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)

    with _block_all_observation(monkeypatch):
        with pytest.raises(source_state.SourceStateError, match="manifest_digest"):
            source_state.load_source_state(path, manifest_sha256=bad_digest, repo_root=root)


@pytest.mark.parametrize(
    "relative",
    [
        pytest.param("missing.py", id="missing"),
        pytest.param("docs", id="directory"),
    ],
)
def test_selected_read_rejects_missing_or_directory_target(
    tmp_path: Path, relative: str
) -> None:
    from scripts.python_source_state import SourceStateError, read_selected_bytes

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    expected_reason = (
        "missing_selected_component" if relative == "missing.py"
        else "selected_path_not_regular"
    )
    with pytest.raises(SourceStateError, match=expected_reason):
        read_selected_bytes(root, relative, _sha(GOOD_SOURCE))


@pytest.mark.parametrize(
    "relative",
    [
        pytest.param("pkg/*.py", id="glob"),
        pytest.param("../outside.py", id="escape"),
        pytest.param("aux.py", id="device"),
        pytest.param("safe.py.", id="trailing-dot"),
        pytest.param("-r.py", id="option-like"),
    ],
)
def test_selected_read_rejects_invalid_literal_before_physical_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    from scripts.python_source_state import SourceStateError, read_selected_bytes

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)

    with _block_all_observation(monkeypatch):
        with pytest.raises(SourceStateError, match="invalid_literal_path"):
            read_selected_bytes(root, relative, _sha(GOOD_SOURCE))


def test_selected_read_rejects_changed_digest(tmp_path: Path) -> None:
    from scripts.python_source_state import SourceStateError, read_selected_bytes

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    with pytest.raises(SourceStateError, match="selected_digest_mismatch"):
        read_selected_bytes(root, "safe.py", "0" * 64)


@pytest.mark.parametrize(
    "redirect", [pytest.param("leaf", id="leaf"), pytest.param("parent", id="parent")]
)
def test_selected_read_rejects_component_redirection(tmp_path: Path, redirect: str) -> None:
    from scripts.python_source_state import SourceStateError, read_selected_bytes

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    if redirect == "leaf":
        os.symlink(root / "safe.py", root / "alias.py")
        relative = "alias.py"
    else:
        os.symlink(root / "tests", root / "alias_tests", target_is_directory=True)
        relative = "alias_tests/test_safe.py"
    with pytest.raises(SourceStateError, match="selected_path_redirection"):
        read_selected_bytes(root, relative, _sha(GOOD_SOURCE if redirect == "leaf" else GOOD_TEST))


def test_target_runtime_keeps_exact_311_contract() -> None:
    from scripts.python_source_state import SourceStateError, require_target_runtime

    require_target_runtime("3.11", version=(3, 11))
    with pytest.raises(SourceStateError, match="target runtime mismatch"):
        require_target_runtime("3.11", version=(3, 12))


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param([], id="both-missing"),
        pytest.param(["--selection", "selection.json"], id="digest-missing"),
        pytest.param(["--selection-sha256", "0" * 64], id="path-missing"),
    ],
)
def test_compiler_cli_rejects_unbound_selection_before_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, arguments: list[str]
) -> None:
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("compiler CLI attempted to load an unbound selection")

    monkeypatch.setattr(source_state, "load_source_state", forbidden)
    with pytest.raises(SystemExit) as failure:
        source_state.main(arguments)
    assert failure.value.code == 2


def test_compiler_cli_bad_digest_fails_before_physical_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import argparse

    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    monkeypatch.setattr(source_state, "ROOT", root)
    with monkeypatch.context() as parser_patch, _block_all_observation(monkeypatch):
        # Keep real parsing while preventing only parser locale-catalog discovery.
        parser_patch.setattr(argparse, "_", lambda message: message)
        with pytest.raises(
            AssertionError, match="pure selection validation observed external state"
        ):
            path.stat()
        assert source_state.main(["--selection", str(path),
                                  "--selection-sha256", "bad"]) == 1
    assert "manifest_digest" in capsys.readouterr().err


def test_imports_use_prefetched_code_without_observing_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Prefetch only the four changed ordinary modules before installing tripwires.
    import argparse
    import dataclasses
    import shutil
    import typing
    import scripts
    import scripts.verification_runtime

    assert argparse and dataclasses and shutil and typing

    filenames = (
        "python_source_state.py",
        "verify_repository.py",
        "security_bandit_gate.py",
        "historical_diary_leakage_lint.py",
    )
    scripts_root = Path(__file__).parent.parent / "scripts"
    modules: dict[str, ModuleType] = {}
    prefetched_code = {}
    for filename in filenames:
        path = scripts_root / filename
        name = path.stem
        module = ModuleType(f"scripts.{name}")
        module.__file__ = str(path)
        module.__package__ = "scripts"
        modules[name] = module
        prefetched_code[name] = compile(path.read_bytes(), str(path), "exec")

    def forbidden_observation(*_args: object, **_kwargs: object):
        raise AssertionError("module import observed a filesystem path")

    with monkeypatch.context() as patch:
        for name, module in modules.items():
            patch.setitem(sys.modules, f"scripts.{name}", module)
            patch.setattr(scripts, name, module, raising=False)
        for method in (
            "resolve", "stat", "lstat", "open", "read_bytes", "read_text",
            "iterdir", "glob", "rglob",
        ):
            patch.setattr(Path, method, forbidden_observation)
        for method in ("stat", "lstat", "open", "scandir", "listdir"):
            patch.setattr(os, method, forbidden_observation)
        patch.setattr(builtins, "open", forbidden_observation)
        patch.setattr(io, "open", forbidden_observation)
        patch.setattr(subprocess, "run", forbidden_observation)
        patch.setattr(subprocess, "Popen", forbidden_observation)
        for filename in filenames:
            name = Path(filename).stem
            exec(prefetched_code[name], modules[name].__dict__)


def test_profile_commands_are_exact_pure_selected_argv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import verify_repository as verification
    from scripts import python_source_state as source_state
    from scripts.verification_runtime import TIMEOUT_SECONDS

    root, path, digest, manifest = _selection(tmp_path)
    state = _load(root, path, digest)
    absolute = str(path.absolute())
    configs = manifest["configs"]
    phases = manifest["phases"]
    python = sys.executable
    compile_argv = [python, "-B", "scripts/python_source_state.py", "--selection", absolute,
                    "--selection-sha256", digest, "--require-target-runtime"]
    ruff_argv = [python, "-B", "-m", "ruff", "check", "--config", configs["ruff"],
                 "--no-cache", *phases["ruff"]]
    leakage_argv = [python, "-B", "scripts/historical_diary_leakage_lint.py", "--selection",
                    absolute, "--selection-sha256", digest]
    bandit_argv = [python, "-B", "scripts/security_bandit_gate.py", "--selection", absolute,
                   "--selection-sha256", digest]
    pytest_argv = [python, "-B", "-m", "pytest", "--noconftest", "-c", configs["pytest"],
                   "-o", "addopts=", "-p", "no:cacheprovider", *phases["tests"]]
    expected = {
        "ci-correctness": [compile_argv, ruff_argv, leakage_argv, pytest_argv],
        "ci-lint": [ruff_argv, leakage_argv],
        "ci-bandit": [bandit_argv],
        "ci-security": [ruff_argv, leakage_argv, bandit_argv],
    }
    expected_timeouts = {
        "ci-correctness": ["tool", "tool", "tool", "focused_tests"],
        "ci-lint": ["tool", "tool"],
        "ci-bandit": ["tool"],
        "ci-security": ["tool", "tool", "tool"],
    }

    def no_load(*_args: object, **_kwargs: object):
        raise AssertionError("pure command construction reloaded selection")

    monkeypatch.setattr(source_state, "read_selected_bytes", no_load)
    monkeypatch.setattr(source_state, "load_source_state", no_load)
    monkeypatch.setattr(verification, "load_source_state", no_load, raising=False)
    with _block_all_observation(monkeypatch):
        for profile, expected_argv in expected.items():
            first = verification.build_commands(profile, state)
            second = verification.build_commands(profile, state)
            assert [command.argv for command in first] == expected_argv
            assert [command.argv for command in second] == expected_argv
            assert [command.timeout_seconds for command in first] == [
                TIMEOUT_SECONDS[name] for name in expected_timeouts[profile]
            ]
            assert all("-r" not in command.argv and "git" not in command.argv for command in first)


def test_command_builder_rejects_missing_provenance_and_unsupported_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import verify_repository as verification
    from scripts.python_source_state import SourceStateError

    root, path, digest, _ = _selection(tmp_path)
    state = _load(root, path, digest)
    unbound = copy.deepcopy(state)
    del unbound["selection_sha256"]
    with _block_all_observation(monkeypatch):
        with pytest.raises(SourceStateError, match="unbound_verification_selection"):
            verification.build_commands("ci-lint", unbound)
        with pytest.raises(SourceStateError, match="unsupported_verification_profile"):
            verification.build_commands("migration", state)


@pytest.mark.parametrize(
    "profile",
    [
        pytest.param("fast", id="fast"),
        pytest.param("migration", id="migration"),
        pytest.param("unknown", id="unknown"),
    ],
)
def test_unbound_profiles_fail_before_selection_or_command_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, profile: str
) -> None:
    from scripts import verify_repository as verification
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("invalid profile attempted selection or execution")

    monkeypatch.setattr(source_state, "load_source_state", forbidden)
    monkeypatch.setattr(verification, "load_source_state", forbidden, raising=False)
    monkeypatch.setattr(verification, "run_commands", forbidden)
    with pytest.raises(SystemExit) as failure:
        verification.main(["--profile", profile, "--selection", str(path),
                           "--selection-sha256", digest])
    assert failure.value.code == 2


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(["--profile", "ci-lint"], id="both-missing"),
        pytest.param(["--profile", "ci-lint", "--selection", "selection.json"], id="digest-missing"),
        pytest.param(["--profile", "ci-lint", "--selection-sha256", "0" * 64], id="path-missing"),
    ],
)
def test_cli_missing_selection_binding_fails_before_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, arguments: list[str]
) -> None:
    from scripts import verify_repository as verification
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("invalid CLI binding attempted selection or execution")

    monkeypatch.setattr(source_state, "load_source_state", forbidden)
    monkeypatch.setattr(verification, "load_source_state", forbidden, raising=False)
    monkeypatch.setattr(verification, "run_commands", forbidden)
    with pytest.raises(SystemExit) as failure:
        verification.main(arguments)
    assert failure.value.code == 2


def test_cli_bad_digest_fails_before_physical_observation_or_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import argparse

    from scripts import verify_repository as verification
    from scripts import python_source_state as source_state

    root, path, digest, _ = _selection(tmp_path)
    _assert_valid_control(root, path, digest)
    monkeypatch.setattr(source_state, "ROOT", root)
    monkeypatch.setattr(verification, "REPO_ROOT", root)

    def forbidden_execution(*_args: object, **_kwargs: object):
        raise AssertionError("invalid selection launched verification tools")

    monkeypatch.setattr(verification, "run_commands", forbidden_execution)
    with monkeypatch.context() as parser_patch, _block_all_observation(monkeypatch):
        # Keep real parsing while preventing only parser locale-catalog discovery.
        parser_patch.setattr(argparse, "_", lambda message: message)
        with pytest.raises(
            AssertionError, match="pure selection validation observed external state"
        ):
            path.stat()
        assert verification.main(["--profile", "ci-lint", "--selection", str(path),
                                  "--selection-sha256", "bad"]) == 2
    assert "manifest_digest" in capsys.readouterr().err
