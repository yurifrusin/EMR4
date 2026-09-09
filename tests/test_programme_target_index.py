"""Only newly authored index bytes and complete local synthetic repositories."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from programme_maintenance_synthetic import (
    SyntheticGitError,
    _git,
    create_synthetic_graph,
    create_synthetic_repository,
)
from orchestration_harness import trusted_git as git


def _checksum(body: bytes, algorithm: str = "sha1") -> bytes:
    return body + hashlib.new(algorithm, body, usedforsecurity=False).digest()


def _authored_index(
    *, algorithm="sha1", version=2, mode=0o100644, flags=0, extension=b""
):
    oid = hashlib.new(algorithm, b"blob 2\0x\n", usedforsecurity=False).digest()
    name = b"source.py"
    stat_fields = b"\0" * 24 + mode.to_bytes(4, "big") + b"\0" * 12
    entry = stat_fields + oid + (len(name) | flags).to_bytes(2, "big") + name + b"\0"
    entry += b"\0" * (-len(entry) % 8)
    header = b"DIRC" + version.to_bytes(4, "big") + (1).to_bytes(4, "big")
    return _checksum(header + entry + extension, algorithm)


@pytest.mark.parametrize("algorithm", ["sha1", "sha256"])
@pytest.mark.parametrize("version", [2, 3])
def test_metadata_and_uncached_tree_match_authored_git_tree(
    tmp_path, algorithm, version
):
    payload = _authored_index(algorithm=algorithm, version=version)
    metadata, uncached = git._index_metadata(payload, algorithm)
    assert metadata["entry_count"] == 1
    assert metadata["version"] == version
    assert uncached == payload
    blob = hashlib.new(algorithm, b"blob 2\0x\n", usedforsecurity=False).digest()
    body = b"100644 source.py\0" + blob
    expected = hashlib.new(
        algorithm,
        b"tree " + str(len(body)).encode() + b"\0" + body,
        usedforsecurity=False,
    ).hexdigest()
    assert (
        git._derive_uncached_index_tree(
            uncached, object_format=algorithm, scratch_parent=tmp_path
        )
        == expected
    )
    assert list(tmp_path.iterdir()) == []
    assert "source.py" not in json.dumps(metadata)


@pytest.mark.parametrize("flags", [0x8000, 0x4000, 0x1000, 0x2000, 0x3000])
def test_index_flags_and_stages_fail_before_filename_processing(flags):
    reason = (
        "trusted_git_unresolved_index_stage_forbidden"
        if flags & 0x3000
        else "trusted_git_index_flags_forbidden"
    )
    with pytest.raises(git.TrustedGitError, match=reason):
        git._index_metadata(_authored_index(flags=flags), "sha1")


@pytest.mark.parametrize("mode", [0o040000, 0o120000, 0o160000, 0o100600])
def test_nonregular_and_invalid_modes_are_closed(mode):
    with pytest.raises(git.TrustedGitError, match="trusted_git_tracked_mode_forbidden"):
        git._index_metadata(_authored_index(mode=mode), "sha1")


@pytest.mark.parametrize(
    "signature",
    [b"FSMN", b"link", b"sdir", b"UNTR", b"EOIE", b"IEOT", b"REUC", b"XXXX"],
)
def test_every_unreviewed_extension_is_closed(signature):
    extension = signature + (0).to_bytes(4, "big")
    with pytest.raises(
        git.TrustedGitError, match="trusted_git_index_extension_forbidden"
    ):
        git._index_metadata(_authored_index(extension=extension), "sha1")


def test_opaque_tree_cache_is_discarded_completely(tmp_path):
    cache = b"arbitrary cache bytes never parsed as authority"
    payload = _authored_index(extension=b"TREE" + len(cache).to_bytes(4, "big") + cache)
    metadata, uncached = git._index_metadata(payload, "sha1")
    assert uncached == _authored_index()
    assert metadata["extensions_discarded"] == ["TREE"]
    assert metadata["original_index_sha256"] != metadata["extension_free_index_sha256"]
    assert git._derive_uncached_index_tree(
        uncached, object_format="sha1", scratch_parent=tmp_path
    )


def test_tree_and_selected_objects_use_one_owned_snapshot(tmp_path, monkeypatch):
    calls = []
    original = git.subprocess.run

    def record(argv, **kwargs):
        calls.append((tuple(argv), Path(kwargs["cwd"])))
        assert kwargs["stderr"] == git.subprocess.DEVNULL
        return original(argv, **kwargs)

    monkeypatch.setattr(git.subprocess, "run", record)
    tree, objects = git._derive_index_snapshot(
        _authored_index(),
        object_format="sha1",
        scratch_parent=tmp_path,
        attested_paths=("source.py",),
    )
    assert len(tree) == 40
    assert objects == {
        "source.py": hashlib.sha1(b"blob 2\0x\n", usedforsecurity=False).hexdigest()
    }
    assert len({root for _, root in calls}) == 1
    assert all(root.is_relative_to(tmp_path) for _, root in calls)
    assert any("write-tree" in argv for argv, _ in calls)
    assert any(":0:source.py" in argv for argv, _ in calls)
    assert list(tmp_path.iterdir()) == []


def test_physical_index_checked_before_git_canonicalizes_it(
    target, tmp_path, monkeypatch
):
    raw = target.root / ".git/index"
    head, tree = target.head(), target.index_tree()
    original_validate = git._validate_path_components
    git_calls = []

    def reject_raw(path):
        if path == raw:
            raise git.TrustedGitError("trusted_git_reparse_forbidden")
        return original_validate(path)

    def canonical_answer(*args, **kwargs):
        git_calls.append(args)
        return str(tmp_path / "canonical-destination")

    monkeypatch.setattr(git, "_validate_path_components", reject_raw)
    monkeypatch.setattr(git, "run_git", canonical_answer)
    with pytest.raises(git.TrustedGitError, match="trusted_git_reparse_forbidden"):
        git.attest_target_index(
            target.root,
            attested_paths=["owned.py"],
            expected_head=head,
            expected_index_tree=tree,
            scratch_parent=tmp_path,
        )
    assert git_calls == []


def test_linked_authored_worktree_uses_physical_gitfile_and_commondir(target, tmp_path):
    linked = tmp_path / "linked"
    head = target.head()
    _git(target.root, "worktree", "add", "--quiet", "--detach", str(linked), head)
    tree = _git(linked, "write-tree").decode("ascii").strip()
    observation = git.attest_target_index(
        linked,
        attested_paths=["owned.py"],
        expected_head=head,
        expected_index_tree=tree,
        scratch_parent=tmp_path,
    )
    locators = observation["repository"]["physical_locators"]
    assert len(locators) == 2
    assert locators[0]["resolved_path"] == (linked / ".git").as_posix()
    assert locators[1]["resolved_path"].endswith("/commondir")
    assert (
        observation["repository"]["commondir"]["resolved_path"]
        == (target.root / ".git").as_posix()
    )


@pytest.mark.parametrize(
    "payload",
    [
        b"wrong-prefix",
        b"gitdir: \n",
        b"gitdir: a\nb",
        b"gitdir: \xff",
        b"gitdir: " + b"x" * 4096,
    ],
)
def test_malformed_physical_gitfile_fails_without_git(tmp_path, monkeypatch, payload):
    root = tmp_path / "invalid-locator"
    root.mkdir()
    (root / ".git").write_bytes(payload)

    def forbidden(*args, **kwargs):
        raise AssertionError("Git reached through malformed locator")

    monkeypatch.setattr(git, "run_git", forbidden)
    with pytest.raises(git.TrustedGitError):
        git.attest_target_index(
            root,
            attested_paths=["owned.py"],
            expected_head="a" * 40,
            expected_index_tree="b" * 40,
            scratch_parent=tmp_path,
        )


def test_snapshot_size_limit_is_checked_before_open(tmp_path, monkeypatch):
    path = tmp_path / "oversize"
    path.write_bytes(b"x" * 17)

    def forbidden(*args, **kwargs):
        raise AssertionError("oversize index opened")

    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(git.TrustedGitError, match="trusted_git_snapshot_size_exceeded"):
        git._read_regular_snapshot(path, maximum_bytes=16)


@pytest.mark.parametrize(
    "case",
    [
        "checksum",
        "version",
        "count",
        "length",
        "padding",
        "extension_length",
        "duplicate_tree",
        "truncated",
    ],
)
def test_malformed_index_envelopes_fail_closed(case):
    body = bytearray(_authored_index()[:-20])
    if case == "checksum":
        payload = bytes(body) + b"\0" * 20
    else:
        if case == "version":
            body[4:8] = (4).to_bytes(4, "big")
        elif case == "count":
            body[8:12] = (0xFFFFFFFF).to_bytes(4, "big")
        elif case == "length":
            body[72:74] = (1).to_bytes(2, "big")
        elif case == "padding":
            body[-1] = 1
        elif case == "extension_length":
            body.extend(b"TREE" + (0xFFFFFFFF).to_bytes(4, "big"))
        elif case == "duplicate_tree":
            body.extend((b"TREE" + b"\0" * 4) * 2)
        elif case == "truncated":
            body = body[:15]
        payload = _checksum(bytes(body))
    with pytest.raises(git.TrustedGitError):
        git._index_metadata(payload, "sha1")


@pytest.fixture
def target(tmp_path):
    return create_synthetic_repository(
        tmp_path / "target",
        {"owned.py": b"VALUE = 1\n", "unselected/sentinel.txt": b"authored sentinel\n"},
    )


def _observe(target, tmp_path, **changes):
    args = {
        "attested_paths": ("owned.py",),
        "expected_head": target.head(),
        "expected_index_tree": target.index_tree(),
        "scratch_parent": tmp_path,
    }
    args.update(changes)
    return git.attest_target_index(target.root, **args)


def test_target_observation_has_no_name_inventory_or_unselected_reads(
    target, tmp_path, monkeypatch
):
    expected_head = target.head()
    expected_tree = target.index_tree()
    index_before = (target.root / ".git/index").read_bytes()
    commands = []
    original_run = git.run_git
    original_read = Path.read_bytes
    original_open = Path.open
    permitted = {
        target.root / name for name in ("owned.py", ".git/index", ".git/config")
    }

    def bounded_run(root, *args, **kwargs):
        assert not {"ls-files", "ls-tree", "status", "diff", "grep"}.intersection(args)
        assert not any(arg.startswith(":0:") for arg in args)
        commands.append(args)
        return original_run(root, *args, **kwargs)

    def bounded_read(path):
        if path.is_relative_to(target.root):
            assert path in permitted, "unexpected target physical read"
        return original_read(path)

    def bounded_open(path, *args, **kwargs):
        if path.is_relative_to(target.root):
            assert path in permitted, "unexpected target physical open"
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(git, "run_git", bounded_run)
    monkeypatch.setattr(Path, "read_bytes", bounded_read)
    monkeypatch.setattr(Path, "open", bounded_open)
    observation = git.attest_target_index(
        target.root,
        attested_paths=["owned.py"],
        expected_head=expected_head,
        expected_index_tree=expected_tree,
        scratch_parent=tmp_path,
    )
    assert observation["index_tree"] == expected_tree
    assert observation["complete_physical_worktree_attested"] is False
    assert observation["operation_authority"] is False
    assert [row["path"] for row in observation["physical_paths"]] == ["owned.py"]
    assert "sentinel" not in json.dumps(observation)
    assert (target.root / ".git/index").read_bytes() == index_before
    assert commands


@pytest.mark.parametrize(
    "paths",
    [
        [],
        (),
        ["../owned.py"],
        [":(glob)**"],
        ["owned.py", "OWNED.py"],
        [".git/config"],
        ["x/CON.txt"],
        ["owned.py/"],
        ["x\\y"],
        ["/owned.py"],
        "owned.py",
    ],
)
def test_bad_path_contract_rejected_before_any_git(paths, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Git reached for an invalid path contract")

    monkeypatch.setattr(git, "run_git", forbidden)
    with pytest.raises(git.TrustedGitError, match="trusted_git_attested_path_invalid"):
        git.attest_target_index(
            tmp_path,
            attested_paths=paths,
            expected_head="a" * 40,
            expected_index_tree="b" * 40,
            scratch_parent=tmp_path,
        )


@pytest.mark.parametrize(
    "field,reason",
    [
        ("expected_head", "trusted_git_expected_commit_mismatch"),
        ("expected_index_tree", "trusted_git_expected_index_tree_mismatch"),
    ],
)
def test_wrong_expected_identity_is_rejected(target, tmp_path, field, reason):
    with pytest.raises(git.TrustedGitError, match=reason):
        _observe(target, tmp_path, **{field: "0" * 40})


def test_physical_change_is_rejected_even_with_unchanged_index(target, tmp_path):
    (target.root / "owned.py").write_bytes(b"VALUE = 2\n")
    with pytest.raises(
        git.TrustedGitError, match="trusted_git_physical_bytes_mismatch"
    ):
        _observe(target, tmp_path)


def test_target_observation_attests_nested_and_executable_paths(tmp_path):
    target = create_synthetic_repository(
        tmp_path / "target",
        {"owned.py": b"VALUE = 1\n", "nested/runner.sh": b"#!/bin/sh\n"},
    )
    original_tree = target.index_tree()
    _git(target.root, "update-index", "--chmod=+x", "--", "nested/runner.sh")
    executable_tree = target.index_tree()
    assert executable_tree != original_tree
    observation = git.attest_target_index(
        target.root,
        attested_paths=["nested/runner.sh", "owned.py"],
        expected_head=target.head(),
        expected_index_tree=target.index_tree(),
        scratch_parent=tmp_path,
    )
    assert [row["path"] for row in observation["physical_paths"]] == [
        "nested/runner.sh",
        "owned.py",
    ]
    assert observation["index_tree"] == executable_tree


def test_read_regular_snapshot_rejects_nonregular_path(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(git.TrustedGitError, match="trusted_git_path_type_invalid"):
        git._read_regular_snapshot(directory)


def test_read_regular_snapshot_read_error_is_closed(tmp_path, monkeypatch):
    path = tmp_path / "file"
    path.write_bytes(b"payload")

    def fail_read(_path):
        raise OSError("synthetic read failure")

    monkeypatch.setattr(Path, "read_bytes", fail_read)
    with pytest.raises(git.TrustedGitError, match="trusted_git_snapshot_read_failed"):
        git._read_regular_snapshot(path)


@pytest.mark.parametrize("kind", ["identity", "payload"])
def test_read_regular_snapshot_rejects_identity_or_payload_mismatch(
    tmp_path, monkeypatch, kind
):
    path = tmp_path / "file"
    path.write_bytes(b"payload")
    original_identity = git._path_identity
    if kind == "identity":
        calls = 0

        def changed_identity(value, *, directory=None):
            nonlocal calls
            calls += 1
            identity = original_identity(value, directory=directory)
            if calls == 2:
                identity = {**identity, "modified_ns": identity["modified_ns"] + 1}
            return identity

        monkeypatch.setattr(git, "_path_identity", changed_identity)
    else:
        monkeypatch.setattr(Path, "read_bytes", lambda _path: b"different")
    with pytest.raises(git.TrustedGitError, match="trusted_git_snapshot_drift"):
        git._read_regular_snapshot(path)


@pytest.mark.parametrize("path", ["missing.py", "unselected"])
def test_target_observation_rejects_missing_or_directory_selection(
    target, tmp_path, path
):
    with pytest.raises(git.TrustedGitError):
        _observe(target, tmp_path, attested_paths=[path])


def test_target_observation_rejects_sparse_checkout(target, tmp_path):
    _git(target.root, "config", "--local", "core.sparseCheckout", "true")
    with pytest.raises(git.TrustedGitError, match="trusted_git_sparse_index_forbidden"):
        _observe(target, tmp_path)


def test_target_observation_rejects_split_index(target, tmp_path):
    _git(target.root, "update-index", "--split-index")
    with pytest.raises(git.TrustedGitError, match="trusted_git_split_index_forbidden"):
        _observe(target, tmp_path)


@pytest.mark.parametrize("option", ["--assume-unchanged", "--skip-worktree"])
def test_flags_on_unselected_entry_are_rejected(target, tmp_path, option):
    head, tree = target.head(), target.index_tree()
    _git(target.root, "update-index", option, "--", "unselected/sentinel.txt")
    with pytest.raises(git.TrustedGitError, match="trusted_git_index_flags_forbidden"):
        _observe(target, tmp_path, expected_head=head, expected_index_tree=tree)


def test_scratch_inside_target_is_rejected(target, tmp_path):
    with pytest.raises(git.TrustedGitError, match="trusted_git_scratch_not_isolated"):
        _observe(target, tmp_path, scratch_parent=target.root)


@pytest.mark.parametrize("drift", ["index", "physical", "config"])
def test_drift_during_observation_is_rejected(target, tmp_path, monkeypatch, drift):
    original = git._derive_index_snapshot

    def change_after_tree(*args, **kwargs):
        tree = original(*args, **kwargs)
        if drift == "index":
            _git(
                target.root,
                "update-index",
                "--assume-unchanged",
                "--",
                "unselected/sentinel.txt",
            )
        elif drift == "physical":
            (target.root / "owned.py").write_bytes(b"VALUE = 3\n")
        else:
            _git(target.root, "config", "--local", "maintenance.test", "changed")
        return tree

    monkeypatch.setattr(git, "_derive_index_snapshot", change_after_tree)
    with pytest.raises(
        git.TrustedGitError,
        match="trusted_git_(snapshot_drift|physical_bytes_mismatch)",
    ):
        _observe(target, tmp_path)


def test_synthetic_commit_push_and_observation_lifecycle(tmp_path):
    graph = create_synthetic_graph(tmp_path / "graph", {"owned.py": b"VALUE = 1\n"})
    target = graph.target
    _observe(target, tmp_path)
    assert (
        target.push_exact_sha(graph.initial_commit.sha, expected_remote_head=None)
        == graph.initial_commit.sha
    )
    tree = target.stage_files({"owned.py": b"VALUE = 2\n"})
    _observe(target, tmp_path, expected_index_tree=tree)
    child = target.commit_exact_index(
        expected_head=graph.initial_commit.sha,
        expected_tree=tree,
        message="authored maintenance",
    )
    assert child.parent == graph.initial_commit.sha
    _observe(target, tmp_path, expected_head=child.sha)
    assert (
        target.push_exact_sha(child.sha, expected_remote_head=graph.initial_commit.sha)
        == child.sha
    )
    assert target.remote_head() == child.sha
    _observe(target, tmp_path)
    with pytest.raises(SyntheticGitError, match="synthetic_head_drift"):
        target.commit_exact_index(
            expected_head=graph.initial_commit.sha,
            expected_tree=tree,
            message="stale replay",
        )
    with pytest.raises(SyntheticGitError, match="synthetic_remote_head_drift"):
        target.push_exact_sha(child.sha, expected_remote_head=graph.initial_commit.sha)
