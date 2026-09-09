"""Authored-synthetic tests for inert maintenance-candidate comparison."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from orchestration_harness import controller_maintenance_candidate as candidate
from orchestration_harness.controller_maintenance_record import MaintenanceRecordError
from orchestration_harness import trusted_git as git
from programme_maintenance_synthetic import _git, create_synthetic_graph


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _manifest(graph, candidate_tree: str, *, changed, frozen, base_tree=None) -> bytes:
    commit = graph.initial_commit
    assert commit is not None
    value = {
        "schema_version": "ariadne.g1b2_controller_maintenance_manifest.v1",
        "generation_id": "synthetic-candidate-1",
        "base_commit": commit.sha,
        "base_tree": base_tree or commit.tree,
        "source_commit": commit.sha,
        "source_tree": commit.tree,
        "candidate_tree": candidate_tree,
        "destination_ref": "refs/heads/codex/raisa-ariadne-recovery-g0",
        "review_record_sha256": "a" * 64,
        "review_subject_sha256": "b" * 64,
        "changed_files": changed,
        "frozen_files": frozen,
    }
    return json.dumps(value, separators=(",", ":")).encode()


def _row(path, before, after):
    return {
        "path": path,
        "mode": "100644",
        "before_sha256": before,
        "after_sha256": after,
    }


@pytest.fixture
def graph(tmp_path):
    return create_synthetic_graph(
        tmp_path / "graph",
        {"owned.py": b"VALUE = 1\n", "frozen.txt": b"keep\n"},
    )


@pytest.fixture
def guarded_commands(monkeypatch, graph, tmp_path):
    forbidden = {
        "ls-files",
        "ls-tree",
        "status",
        "diff",
        "add",
        "commit",
        "push",
        "update-index",
    }
    original = candidate._command

    def bounded(root: Path, *args: str):
        if root == graph.target.root:
            assert not forbidden.intersection(args)
            assert args[0] in {"rev-parse", "cat-file"}
        else:
            assert root.parent == tmp_path
            assert root.name.startswith("ariadne-delta-")
            assert args[0] in {"init", "update-index", "write-tree"}
        return original(root, *args)

    monkeypatch.setattr(candidate, "_command", bounded)


def _compare(graph, payload, tmp_path):
    return candidate.compare_maintenance_candidate(
        graph.target.root,
        payload,
        expected_manifest_sha256=_sha(payload),
        scratch_parent=tmp_path,
    )


def test_compare_valid_changed_added_and_frozen_files_is_inert(
    graph, tmp_path, guarded_commands
):
    old_owned = graph.target.files["owned.py"]
    new_owned = b"VALUE = 2\n"
    graph.target.stage_files({"owned.py": new_owned, "new.txt": b"new\n"})
    tree = graph.target.index_tree()
    before_index = (graph.target.root / ".git/index").read_bytes()
    before_ref = _git(graph.target.root, "rev-parse", graph.target.branch_ref)
    payload = _manifest(
        graph,
        tree,
        changed=[
            _row("owned.py", _sha(old_owned), _sha(new_owned)),
            _row("new.txt", None, _sha(b"new\n")),
        ],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    head = graph.target.head()
    result = _compare(graph, payload, tmp_path)
    assert result["operation_authority"] is False
    assert result["source_acceptance_verified"] is False
    assert result["review_acceptance_verified"] is False
    assert graph.target.head() == head
    assert _git(graph.target.root, "rev-parse", graph.target.branch_ref) == before_ref
    assert (graph.target.root / ".git/index").read_bytes() == before_index


def test_compare_rejects_extra_staged_unselected_path(
    graph, tmp_path, guarded_commands
):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n", "extra.txt": b"extra\n"})
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", _sha(b"VALUE = 1\n"), _sha(b"VALUE = 2\n"))],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    with pytest.raises(candidate.MaintenanceCandidateError) as error:
        _compare(graph, payload, tmp_path)
    assert error.value.reason_code == "maintenance_undeclared_delta"


def test_compare_rejects_wrong_stated_base_tree(graph, tmp_path, guarded_commands):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n"})
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", _sha(b"VALUE = 1\n"), _sha(b"VALUE = 2\n"))],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
        base_tree="0" * 40,
    )
    with pytest.raises(candidate.MaintenanceCandidateError) as error:
        _compare(graph, payload, tmp_path)
    assert error.value.reason_code == "maintenance_base_tree_mismatch"


@pytest.mark.parametrize("kind", ["before", "after"])
def test_compare_rejects_declared_byte_mismatch(
    graph, tmp_path, guarded_commands, kind
):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n"})
    row = _row(
        "owned.py",
        _sha(b"wrong\n") if kind == "before" else _sha(b"VALUE = 1\n"),
        _sha(b"VALUE = 2\n") if kind == "before" else _sha(b"wrong\n"),
    )
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[row],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    with pytest.raises(candidate.MaintenanceCandidateError) as error:
        _compare(graph, payload, tmp_path)
    assert error.value.reason_code == f"maintenance_{kind}_bytes_mismatch"


def test_compare_rejects_addition_declaration_for_preexisting_file(
    graph, tmp_path, guarded_commands
):
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", None, _sha(b"VALUE = 1\n"))],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    with pytest.raises(candidate.MaintenanceCandidateError) as error:
        _compare(graph, payload, tmp_path)
    assert error.value.reason_code == "maintenance_undeclared_delta"


def test_compare_rejects_undeclared_staged_mode(graph, tmp_path, guarded_commands):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n"})
    _git(graph.target.root, "update-index", "--chmod=+x", "--", "owned.py")
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", _sha(b"VALUE = 1\n"), _sha(b"VALUE = 2\n"))],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    with pytest.raises(candidate.MaintenanceCandidateError) as error:
        _compare(graph, payload, tmp_path)
    assert error.value.reason_code == "maintenance_declared_mode_mismatch"


def test_compare_rejects_index_drift_after_initial_observer(
    graph, tmp_path, monkeypatch, guarded_commands
):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n"})
    original = git.attest_target_index
    calls = 0

    def drift(*args, **kwargs):
        nonlocal calls
        result = original(*args, **kwargs)
        calls += 1
        if calls == 1:
            _git(
                graph.target.root,
                "update-index",
                "--assume-unchanged",
                "--",
                "frozen.txt",
            )
        return result

    monkeypatch.setattr(git, "attest_target_index", drift)
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", _sha(b"VALUE = 1\n"), _sha(b"VALUE = 2\n"))],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    with pytest.raises(candidate.MaintenanceCandidateError) as error:
        _compare(graph, payload, tmp_path)
    assert error.value.reason_code in {
        "maintenance_index_drift",
        "maintenance_candidate_drift",
    }


def test_compare_rejects_invalid_manifest_before_observer(graph, tmp_path, monkeypatch):
    called = False

    def observer(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("observer reached")

    monkeypatch.setattr(git, "attest_target_index", observer)
    payload = b"{}"
    with pytest.raises(MaintenanceRecordError) as error:
        candidate.compare_maintenance_candidate(
            graph.target.root,
            payload,
            expected_manifest_sha256=_sha(payload),
            scratch_parent=tmp_path,
        )
    assert error.value.reason_code == "top_level_shape_invalid"
    assert called is False


@pytest.mark.parametrize("claimed", [b"keep\n", b"changed\n"])
def test_changed_frozen_file_fails_even_if_manifest_claims_new_bytes_are_original(
    graph, tmp_path, guarded_commands, claimed
):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n", "frozen.txt": b"changed\n"})
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", _sha(b"VALUE = 1\n"), _sha(b"VALUE = 2\n"))],
        frozen=[_row("frozen.txt", _sha(claimed), _sha(claimed))],
    )
    reason = (
        "maintenance_after_bytes_mismatch"
        if claimed == b"keep\n"
        else "maintenance_before_bytes_mismatch"
    )
    with pytest.raises(candidate.MaintenanceCandidateError, match=reason):
        _compare(graph, payload, tmp_path)


@pytest.mark.parametrize("replacement", ["directory", "link_to_target"])
def test_scratch_substitution_rejected_before_allocation(
    graph, tmp_path, monkeypatch, replacement
):
    graph.target.stage_files({"owned.py": b"VALUE = 2\n"})
    payload = _manifest(
        graph,
        graph.target.index_tree(),
        changed=[_row("owned.py", _sha(b"VALUE = 1\n"), _sha(b"VALUE = 2\n"))],
        frozen=[_row("frozen.txt", _sha(b"keep\n"), _sha(b"keep\n"))],
    )
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    moved = tmp_path / "original-scratch"
    original = candidate._reconstructed_trees

    # This inventory is only of the newly authored, complete synthetic repo.
    def inventory():
        return {
            p.relative_to(graph.target.root).as_posix(): _sha(p.read_bytes())
            if p.is_file()
            else None
            for p in graph.target.root.rglob("*")
        }

    before = inventory()

    def substitute(index, changes, selected_scratch, **kwargs):
        assert selected_scratch == scratch
        assert scratch.resolve().parent == tmp_path.resolve()
        assert moved.resolve().parent == tmp_path.resolve()
        scratch.rename(moved)
        if replacement == "directory":
            scratch.mkdir()
        elif os.name == "nt":
            result = subprocess.run(
                [
                    os.environ["COMSPEC"],
                    "/c",
                    "mklink",
                    "/J",
                    str(scratch),
                    str(graph.target.root),
                ],
                capture_output=True,
                check=False,
            )
            assert result.returncode == 0
        else:
            scratch.symlink_to(graph.target.root, target_is_directory=True)

        # Any allocation by the comparison after substitution is a failure.
        def forbidden_allocation(*args, **kwargs):
            raise AssertionError("allocation after scratch substitution")

        monkeypatch.setattr(
            candidate.tempfile, "TemporaryDirectory", forbidden_allocation
        )
        return original(index, changes, selected_scratch, **kwargs)

    monkeypatch.setattr(candidate, "_reconstructed_trees", substitute)
    try:
        with pytest.raises(
            (candidate.MaintenanceCandidateError, git.TrustedGitError)
        ) as error:
            candidate.compare_maintenance_candidate(
                graph.target.root,
                payload,
                expected_manifest_sha256=_sha(payload),
                scratch_parent=scratch,
            )
        assert error.value.reason_code in {
            "maintenance_scratch_drift",
            "trusted_git_reparse_forbidden",
        }
        assert inventory() == before
    finally:
        if replacement == "link_to_target" and scratch.exists():
            if os.name == "nt":
                scratch.rmdir()  # Remove this exact authored junction, never its target.
            else:
                scratch.unlink()
