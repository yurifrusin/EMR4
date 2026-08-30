from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from orchestration_harness import trusted_git


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        input=input_text,
    )
    return completed.stdout.strip()


def _repository(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    root.mkdir()
    _git(root, "init", "-b", "candidate")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Trusted Git Tests")
    (root / "alpha.txt").write_bytes(b"alpha\n")
    nested = root / "nested"
    nested.mkdir()
    (nested / "beta.txt").write_bytes(b"beta\n")
    _git(root, "add", "--", "alpha.txt", "nested/beta.txt")
    _git(root, "commit", "--no-verify", "-m", "candidate")
    return root


def _head(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD")


def _assert_configuration_rejected(root: Path) -> None:
    with pytest.raises(
        trusted_git.TrustedGitError,
        match="trusted_git_configuration_forbidden",
    ):
        trusted_git.attest_repository(
            root,
            attested_paths=["alpha.txt"],
            expected_commit=_head(root),
        )


@pytest.mark.parametrize(
    ("key", "value"),
    [("core.checkStat", "minimal"), ("core.trustctime", "false")],
)
@pytest.mark.parametrize("scope", ["local", "worktree", "included"])
def test_stat_cache_weakening_is_rejected_in_every_repository_scope(
    tmp_path: Path, key: str, value: str, scope: str
) -> None:
    root = _repository(tmp_path)
    if scope == "local":
        _git(root, "config", "--local", key, value)
    elif scope == "worktree":
        _git(root, "config", "--local", "extensions.worktreeConfig", "true")
        _git(root, "config", "--worktree", key, value)
    else:
        gitdir = Path(_git(root, "rev-parse", "--absolute-git-dir"))
        included = gitdir / "visibility-policy.inc"
        section, name = key.split(".", 1)
        included.write_text(f"[{section}]\n\t{name} = {value}\n", encoding="utf-8")
        _git(root, "config", "--local", "include.path", included.as_posix())
    _assert_configuration_rejected(root)


@pytest.mark.parametrize(
    ("key", "values"),
    [
        ("core.checkStat", ["minimal", "default"]),
        ("core.checkStat", ["default", "default"]),
        ("core.trustctime", ["true", "false"]),
        ("core.trustctime", ["true", "true"]),
    ],
)
def test_multiple_stat_cache_values_fail_closed(
    tmp_path: Path, key: str, values: list[str]
) -> None:
    root = _repository(tmp_path)
    for value in values:
        _git(root, "config", "--local", "--add", key, value)
    _assert_configuration_rejected(root)


@pytest.mark.parametrize(
    ("check_stat", "trust_ctime"),
    [(None, None), ("default", None), (None, "true"), ("default", "true")],
)
def test_absent_or_canonical_stat_cache_values_are_admitted(
    tmp_path: Path, check_stat: str | None, trust_ctime: str | None
) -> None:
    root = _repository(tmp_path)
    if check_stat is not None:
        _git(root, "config", "--local", "core.checkStat", check_stat)
    if trust_ctime is not None:
        _git(root, "config", "--local", "core.trustctime", trust_ctime)
    identity = trusted_git.attest_repository(
        root,
        attested_paths=["alpha.txt"],
        expected_commit=_head(root),
    )
    assert identity["repository_configuration"]["local"]["core.checkStat"][
        "values"
    ] == ([] if check_stat is None else [check_stat])
    assert identity["repository_configuration"]["local"]["core.trustctime"][
        "values"
    ] == ([] if trust_ctime is None else [trust_ctime])


def _conceal_same_size_restored_mtime(root: Path, *, key: str, value: str) -> None:
    path = root / "alpha.txt"
    _git(root, "config", "--local", key, value)
    fixed_ns = 1_700_000_000_123_456_700
    os.utime(path, ns=(fixed_ns, fixed_ns))
    _git(root, "update-index", "--refresh")
    before = path.stat()
    path.write_bytes(b"omega\n")
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert _git(root, "status", "--porcelain", "--untracked-files=no") == ""
    assert _git(root, "diff", "--raw") == ""


@pytest.mark.parametrize(
    ("key", "value"),
    [("core.checkStat", "minimal"), ("core.trustctime", "false")],
)
def test_complete_attestation_detects_same_size_restored_mtime_drift(
    tmp_path: Path, key: str, value: str
) -> None:
    root = _repository(tmp_path)
    _conceal_same_size_restored_mtime(root, key=key, value=value)
    _git(root, "config", "--local", "--unset-all", key)
    with pytest.raises(
        trusted_git.TrustedGitError,
        match="trusted_git_physical_bytes_mismatch",
    ):
        trusted_git.attest_complete_tracked_tree(root, expected_commit=_head(root))


def test_complete_attestation_binds_every_path_and_is_deterministic(
    tmp_path: Path,
) -> None:
    root = _repository(tmp_path)
    first = trusted_git.attest_complete_tracked_tree(root, expected_commit=_head(root))
    second = trusted_git.attest_complete_tracked_tree(root, expected_commit=_head(root))
    assert first == second
    assert first["schema_version"] == ("ariadne.complete_tracked_tree_attestation.v1")
    assert first["complete_tracked_path_count"] == 2
    assert first["object_format"] in {"sha1", "sha256"}
    assert [row["path"] for row in first["paths"]] == [
        "alpha.txt",
        "nested/beta.txt",
    ]
    assert first["complete_tracked_tree_sha256"] == trusted_git._canonical_digest(
        first["paths"]
    )
    json.dumps(first, sort_keys=True)


@pytest.mark.parametrize("mutation", ["omitted_path", "mode_drift"])
def test_complete_attestation_rejects_index_tree_drift(
    tmp_path: Path, mutation: str
) -> None:
    root = _repository(tmp_path)
    if mutation == "omitted_path":
        _git(root, "rm", "--cached", "--", "nested/beta.txt")
    else:
        _git(root, "update-index", "--chmod=+x", "alpha.txt")
    with pytest.raises(
        trusted_git.TrustedGitError,
        match="trusted_git_index_tree_binding_failed",
    ):
        trusted_git.attest_complete_tracked_tree(root, expected_commit=_head(root))


def test_complete_attestation_rejects_unresolved_index_stage(tmp_path: Path) -> None:
    root = _repository(tmp_path)
    blob = _git(root, "rev-parse", "HEAD:alpha.txt")
    _git(root, "update-index", "--force-remove", "alpha.txt")
    _git(
        root,
        "update-index",
        "--index-info",
        input_text=(f"100644 {blob} 1\talpha.txt\n100644 {blob} 2\talpha.txt\n"),
    )
    with pytest.raises(
        trusted_git.TrustedGitError,
        match=(
            "trusted_git_unresolved_index_stage_forbidden|"
            "trusted_git_index_tree_binding_failed"
        ),
    ):
        trusted_git.attest_complete_tracked_tree(root, expected_commit=_head(root))


@pytest.mark.parametrize("mode", ["120000", "160000"])
def test_complete_attestation_rejects_symlink_and_gitlink_modes(
    tmp_path: Path, mode: str
) -> None:
    root = _repository(tmp_path)
    object_id = (
        _git(root, "rev-parse", "HEAD:alpha.txt") if mode == "120000" else _head(root)
    )
    _git(
        root,
        "update-index",
        "--add",
        "--cacheinfo",
        f"{mode},{object_id},unsupported-entry",
    )
    tree = _git(root, "write-tree")
    commit = _git(root, "commit-tree", tree, "-p", _head(root), "-m", mode)
    _git(root, "update-ref", "HEAD", commit)
    with pytest.raises(
        trusted_git.TrustedGitError,
        match="trusted_git_tracked_mode_forbidden",
    ):
        trusted_git.attest_complete_tracked_tree(root, expected_commit=commit)


def test_complete_index_parser_rejects_duplicate_stage_zero_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _repository(tmp_path)
    original = trusted_git.run_git_bytes
    payload = original(root, "ls-files", "--cached", "--stage", "-z")

    def duplicate(candidate: Path, *args: str, timeout: int = 30) -> bytes:
        if args == ("ls-files", "--cached", "--stage", "-z"):
            return payload[:-1] + b"\0" + payload
        return original(candidate, *args, timeout=timeout)

    monkeypatch.setattr(trusted_git, "run_git_bytes", duplicate)
    with pytest.raises(
        trusted_git.TrustedGitError,
        match="trusted_git_complete_index_invalid",
    ):
        trusted_git._parse_complete_index_entries(root)


def test_complete_attestation_rejects_physical_symlink_or_reparse(
    tmp_path: Path,
) -> None:
    root = _repository(tmp_path)
    physical = root / "alpha.txt"
    target = root / "physical-target.txt"
    target.write_bytes(physical.read_bytes())
    physical.unlink()
    try:
        physical.symlink_to(target)
    except OSError as error:
        pytest.skip(f"symlink creation unavailable: {error}")
    with pytest.raises(
        trusted_git.TrustedGitError,
        match="trusted_git_reparse_forbidden|trusted_git_physical_source_not_regular",
    ):
        trusted_git.attest_complete_tracked_tree(root, expected_commit=_head(root))
