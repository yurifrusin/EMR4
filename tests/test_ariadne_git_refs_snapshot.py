from __future__ import annotations

import subprocess
from pathlib import Path

from orchestration_harness.git_refs_snapshot import build_git_refs_snapshot


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _repository(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "--initial-branch=master")
    _git(repo, "config", "user.email", "synthetic@example.invalid")
    _git(repo, "config", "user.name", "Synthetic")
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "baseline")
    commit = _git(repo, "rev-parse", "HEAD")
    for ref in (
        "refs/remotes/origin/master",
        "refs/heads/handoff/current",
        "refs/remotes/origin/handoff/current",
    ):
        _git(repo, "update-ref", ref, commit)
    _git(repo, "checkout", "-q", "-b", "codex/test-snapshot")
    _git(repo, "update-ref", "refs/remotes/origin/codex/test-snapshot", commit)
    branding = repo / "docs" / "branding"
    branding.mkdir(parents=True)
    (branding / "logo.txt").write_text("synthetic\n", encoding="utf-8")
    return repo, commit


def test_snapshot_machine_populates_refs_and_preserved_untracked_state(
    tmp_path: Path,
) -> None:
    repo, commit = _repository(tmp_path)

    snapshot = build_git_refs_snapshot(
        repo_root=repo,
        expected_protected_commit=commit,
        protected_refs=(
            "refs/heads/master",
            "refs/remotes/origin/master",
            "refs/heads/handoff/current",
            "refs/remotes/origin/handoff/current",
        ),
    )

    assert snapshot["status"] == "passed"
    assert snapshot["head"] == commit
    assert snapshot["branch"] == "codex/test-snapshot"
    assert snapshot["branch_origin_aligned"] is True
    assert snapshot["protected_refs_aligned"] is True
    assert snapshot["tracked_worktree_clean"] is True
    assert snapshot["untracked_path_count"] == 1
    assert snapshot["preserved_untracked_paths"] == {"docs/branding": True}


def test_snapshot_fails_closed_on_protected_ref_mismatch(tmp_path: Path) -> None:
    repo, commit = _repository(tmp_path)
    (repo / "tracked.txt").write_text("second\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "second")
    second = _git(repo, "rev-parse", "HEAD")
    _git(repo, "update-ref", "refs/remotes/origin/master", second)

    snapshot = build_git_refs_snapshot(
        repo_root=repo,
        expected_protected_commit=commit,
        protected_refs=(
            "refs/heads/master",
            "refs/remotes/origin/master",
            "refs/heads/handoff/current",
            "refs/remotes/origin/handoff/current",
        ),
    )

    assert snapshot["status"] == "revision_required"
    assert snapshot["protected_refs_aligned"] is False
    assert snapshot["reason_codes"] == ["git_refs_snapshot_protected_ref_mismatch"]
