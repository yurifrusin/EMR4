from pathlib import Path

import pytest

from scripts import ariadne_verifier_worktree_preflight as preflight
from scripts.ariadne_antigravity import WorktreeState

HEAD = "a" * 40
OTHER_HEAD = "b" * 40

def _state(*, branch: str = "codex/review-gate", head: str = HEAD) -> WorktreeState:
    return WorktreeState(
        root=Path("C:/worktrees/review-gate"),
        branch=branch,
        head=head,
        dirty=False,
    )


def test_exact_clean_review_branch_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight, "inspect_worktree", lambda *_a, **_k: _state())

    evidence = preflight.build_preflight(
        cwd=Path("C:/worktrees/review-gate"),
        expected_head=HEAD,
    )

    assert evidence["status"] == "passed"
    assert evidence["branch"] == "codex/review-gate"
    assert evidence["provider_or_model_calls"] == 0


def test_wrong_head_fails_before_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight, "inspect_worktree", lambda *_a, **_k: _state())

    with pytest.raises(ValueError, match="HEAD mismatch"):
        preflight.build_preflight(
            cwd=Path("C:/worktrees/review-gate"),
            expected_head=OTHER_HEAD,
        )


@pytest.mark.parametrize("branch", ["review-gate", "codex/work", "master", ""])
def test_non_review_branch_fails_before_receipt(
    branch: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _state(branch=branch),
    )

    with pytest.raises(ValueError, match="review prefix"):
        preflight.build_preflight(
            cwd=Path("C:/worktrees/review-gate"),
            expected_head=HEAD,
        )


def _real_state(root: Path) -> preflight.WorktreeState:
    return preflight.WorktreeState(
        root=root,
        branch="codex/review-gate",
        head=HEAD,
        dirty=False,
    )


def _manifest(*, id_: str = "CMD", argv: list[str] | None = None) -> dict[str, object]:
    return {
        "schema_version": "ariadne.verifier-command-manifest.v1",
        "commands": [
            {"id": id_, "argv": argv if argv is not None else ["pytest", "--collect-only", "-q"]}
        ],
    }


def test_command_manifest_is_validated_and_digested(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _real_state(tmp_path),
    )
    evidence = preflight.build_preflight(
        cwd=tmp_path,
        expected_head=HEAD,
        command_manifest=_manifest(),
    )
    assert evidence["command_count"] == 1
    digest = evidence["command_manifest_sha256"]
    assert isinstance(digest, str) and len(digest) == 64
    assert set(digest) <= set("0123456789abcdef")
    assert evidence["status"] == "passed"


def test_command_manifest_shell_wrapper_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _real_state(tmp_path),
    )
    with pytest.raises(ValueError, match="shell wrappers are forbidden"):
        preflight.build_preflight(
            cwd=tmp_path,
            expected_head=HEAD,
            command_manifest=_manifest(argv=["sh", "-c", "echo boom"]),
        )


def test_repository_path_bindings_validate_existence_kind_and_containment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worktree = tmp_path / "review-gate"
    (worktree / "tests").mkdir(parents=True)
    (worktree / "tests" / "conftest.py").write_text("# conftest", encoding="utf-8")
    (worktree / "tools").mkdir()
    (worktree / "tools" / "runner.py").write_text("# runner", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _real_state(worktree),
    )
    evidence = preflight.build_preflight(
        cwd=worktree,
        expected_head=HEAD,
        repository_paths=[
            {"path": "tests/conftest.py", "kind": "file", "required": True, "scope": "worktree"},
            {"path": "tools/runner.py", "kind": "file", "required": True, "scope": "external"},
        ],
    )
    assert evidence["repository_paths"][0]["exists"] is True
    assert evidence["repository_paths"][1]["scope"] == "external"


@pytest.mark.parametrize(
    ("binding", "match"),
    [
        ({"path": "tests/missing.py", "kind": "file", "required": True, "scope": "worktree"}, "required path is missing"),
        ({"path": "tests", "kind": "file", "required": True, "scope": "worktree"}, "must be a file"),
        ({"path": "tools/runner.py", "kind": "directory", "required": True, "scope": "external"}, "must be a directory"),
        ({"path": "../escape.py", "kind": "file", "required": False, "scope": "worktree"}, "inside the review worktree"),
        ({"path": "tests/conftest.py", "kind": "file", "required": True, "scope": "other"}, "scope is not admitted"),
    ],
)
def test_invalid_repository_path_bindings_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    binding: dict[str, object],
    match: str,
) -> None:
    worktree = tmp_path / "review-gate"
    (worktree / "tests").mkdir(parents=True)
    (worktree / "tests" / "conftest.py").write_text("# conftest", encoding="utf-8")
    (worktree / "tools").mkdir()
    (worktree / "tools" / "runner.py").write_text("# runner", encoding="utf-8")
    (tmp_path / "escape.py").write_text("# escape", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _real_state(worktree),
    )
    with pytest.raises(ValueError, match=match):
        preflight.build_preflight(
            cwd=worktree,
            expected_head=HEAD,
            repository_paths=[binding],
        )


def test_candidate_paths_must_resolve_inside_review_worktree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worktree = tmp_path / "review-gate"
    worktree.mkdir()
    (worktree / "tests").mkdir()
    (worktree / "tests" / "test_candidate.py").write_text("# candidate", encoding="utf-8")
    (tmp_path / "other.py").write_text("# other", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _real_state(worktree),
    )
    evidence = preflight.build_preflight(
        cwd=worktree,
        expected_head=HEAD,
        candidate_paths=["tests/test_candidate.py"],
    )
    assert evidence["candidate_paths"] == [
        (worktree / "tests" / "test_candidate.py").resolve().as_posix()
    ]
    with pytest.raises(ValueError, match="outside the review worktree"):
        preflight.build_preflight(
            cwd=worktree,
            expected_head=HEAD,
            candidate_paths=[str(tmp_path / "other.py")],
        )


def test_external_serial_runner_must_bind_repo_root_exactly_to_review_worktree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    worktree = tmp_path / "review-gate"
    primary = tmp_path / "primary-checkout"
    worktree.mkdir()
    primary.mkdir()
    (worktree / "tests").mkdir()
    (worktree / "tests" / "test_candidate.py").write_text("# candidate", encoding="utf-8")
    monkeypatch.setattr(
        preflight,
        "inspect_worktree",
        lambda *_a, **_k: _real_state(worktree),
    )
    # RWW-013: a serial runner rooted in a different checkout is rejected
    # before dispatch, even for relative candidate tests.
    with pytest.raises(ValueError, match="repo-root exactly"):
        preflight.build_preflight(
            cwd=worktree,
            expected_head=HEAD,
            candidate_paths=["tests/test_candidate.py"],
            serial_repo_root=primary,
        )
    evidence = preflight.build_preflight(
        cwd=worktree,
        expected_head=HEAD,
        candidate_paths=["tests/test_candidate.py"],
        serial_repo_root=worktree,
    )
    assert evidence["serial_repo_root"] == worktree.resolve().as_posix()

    with pytest.raises(ValueError, match="repo-root exactly"):
        preflight.build_preflight(
            cwd=worktree,
            expected_head=HEAD,
            candidate_paths=None,
            serial_repo_root=primary,
        )


def test_preflight_rejects_narrowing_parser_and_configurable_protected_prefix() -> None:
    with pytest.raises(ValueError, match="must be a JSON object"):
        preflight._parse_repository_paths('[{"path":"x"}, "discard-me"]')

    with pytest.raises(ValueError, match="exact non-protected review prefix"):
        preflight.build_preflight(
            cwd=Path("C:/worktrees/review-gate"),
            expected_head=HEAD,
            branch_prefix="master",
        )
