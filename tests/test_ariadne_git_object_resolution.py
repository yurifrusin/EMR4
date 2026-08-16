from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from orchestration_harness.git_object_resolution import (
    GitObjectResolutionError,
    resolve_commit_source,
)


ROOT = Path(__file__).resolve().parents[1]
KNOWN_ANCESTOR = "17add9baf2cc3616f7ee4fb8eda3481e2eb13715"


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )
    return result.stdout.strip()


def _commit(repo: Path, name: str, value: str) -> str:
    (repo / name).write_text(value, encoding="utf-8")
    _git(repo, "add", name)
    _git(
        repo,
        "-c",
        "user.name=Ariadne Test",
        "-c",
        "user.email=ariadne@example.invalid",
        "commit",
        "-m",
        f"commit {name}",
    )
    return _git(repo, "rev-parse", "HEAD")


def test_known_full_commit_is_machine_resolved_and_ancestral() -> None:
    result = resolve_commit_source(repo_root=ROOT, source_head=KNOWN_ANCESTOR)

    assert result["status"] == "passed"
    assert result["supplied_object_id"] == KNOWN_ANCESTOR
    assert result["resolved_commit"] == KNOWN_ANCESTOR
    assert len(result["observed_head"]) == 40
    assert result["source_is_ancestor_of_head"] is True


@pytest.mark.parametrize("source_head", ["abc", "A" * 40, "f" * 39, "f" * 41])
def test_non_exact_object_id_is_rejected_before_git(source_head: str) -> None:
    with pytest.raises(
        GitObjectResolutionError,
        match="git_object_id_not_full_lowercase_hex",
    ):
        resolve_commit_source(repo_root=ROOT, source_head=source_head)


def test_nonexistent_full_object_fails_closed() -> None:
    with pytest.raises(GitObjectResolutionError, match="git_object_command_failed"):
        resolve_commit_source(repo_root=ROOT, source_head="f" * 40)


def test_blob_cannot_be_relabelled_as_commit() -> None:
    blob = _git(ROOT, "rev-parse", "HEAD:AGENTS.md")

    with pytest.raises(GitObjectResolutionError, match="git_object_command_failed"):
        resolve_commit_source(repo_root=ROOT, source_head=blob)


def test_valid_nonancestor_commit_fails_closed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    first = _commit(repo, "base.txt", "base")
    _git(repo, "branch", "other", first)
    main_head = _commit(repo, "main.txt", "main")
    _git(repo, "checkout", "other")
    other_head = _commit(repo, "other.txt", "other")
    _git(repo, "checkout", "main")
    assert _git(repo, "rev-parse", "HEAD") == main_head

    with pytest.raises(
        GitObjectResolutionError,
        match="git_source_not_ancestor_of_head",
    ):
        resolve_commit_source(repo_root=repo, source_head=other_head)


def test_nonrepository_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(GitObjectResolutionError, match="git_object_command_failed"):
        resolve_commit_source(repo_root=tmp_path, source_head=KNOWN_ANCESTOR)


def test_resolver_uses_only_fixed_read_only_argv_and_no_shell(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = "1" * 40
    calls: list[tuple[list[str], dict]] = []
    outputs = iter(
        [
            (0, str(tmp_path)),
            (0, source),
            (0, "commit"),
            (0, source),
            (0, ""),
        ]
    )

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((argv, dict(kwargs)))
        returncode, stdout = next(outputs)
        return subprocess.CompletedProcess(
            argv, returncode, stdout=f"{stdout}\n", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = resolve_commit_source(repo_root=tmp_path, source_head=source)

    assert result["status"] == "passed"
    assert all(argv[0] == "git" for argv, _ in calls)
    assert all(kwargs["shell"] is False for _, kwargs in calls)
    assert [argv[1:3] for argv, _ in calls] == [
        ["rev-parse", "--show-toplevel"],
        ["rev-parse", "--verify"],
        ["cat-file", "-t"],
        ["rev-parse", "--verify"],
        ["merge-base", "--is-ancestor"],
    ]
    forbidden = {"add", "commit", "checkout", "reset", "update-ref", "fetch", "push"}
    assert all(not forbidden.intersection(argv) for argv, _ in calls)
