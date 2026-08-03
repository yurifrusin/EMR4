from pathlib import Path

import pytest

from scripts import ariadne_verifier_worktree_preflight as preflight
from scripts.ariadne_antigravity import WorktreeState


def _state(*, branch: str = "codex/review-gate", head: str = "abc123") -> WorktreeState:
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
        expected_head="abc123",
    )

    assert evidence["status"] == "passed"
    assert evidence["branch"] == "codex/review-gate"
    assert evidence["provider_or_model_calls"] == 0


def test_wrong_head_fails_before_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(preflight, "inspect_worktree", lambda *_a, **_k: _state())

    with pytest.raises(ValueError, match="HEAD mismatch"):
        preflight.build_preflight(
            cwd=Path("C:/worktrees/review-gate"),
            expected_head="different",
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
            expected_head="abc123",
        )
