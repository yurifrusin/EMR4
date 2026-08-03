from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import ariadne_antigravity
from scripts.ariadne_antigravity import WorktreeState, build_command


def _state(branch: str = "antigravity/bounded") -> WorktreeState:
    return WorktreeState(
        root=Path("C:/worktrees/bounded"),
        branch=branch,
        head="abc123",
        dirty=False,
    )


def test_command_always_binds_a_fresh_project_and_exact_worktree():
    command = build_command(
        packet="Review the change.",
        state=_state(),
        model="gemini-3.6-flash-high",
        os_sandbox=False,
    )

    assert command[:2] == ["agy", "-p"]
    assert "--new-project" in command
    assert command[command.index("--add-dir") + 1] == "C:\\worktrees\\bounded"
    assert command[command.index("--model") + 1] == "gemini-3.6-flash-high"
    assert command[command.index("--effort") + 1] == "high"
    assert command[command.index("--mode") + 1] == "plan"
    assert "BOUND BRANCH: antigravity/bounded" in command[2]
    assert "--sandbox" not in command


def test_os_sandbox_is_explicit_and_never_the_unattended_default():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="gemini-3.6-flash-medium",
        os_sandbox=True,
    )

    assert command[-1] == "--sandbox"


def test_legacy_model_alias_is_canonicalized_with_explicit_effort():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="Gemini 3.5 Flash (High)",
        os_sandbox=False,
    )

    assert command[command.index("--model") + 1] == "gemini-3.5-flash-high"
    assert command[command.index("--effort") + 1] == "high"


def test_command_rejects_non_gemini_flash_model():
    with pytest.raises(ValueError, match="unsupported Antigravity model"):
        build_command(
            packet="Review.",
            state=_state(),
            model="Claude Opus 4.6 (Thinking)",
            os_sandbox=False,
        )


def test_run_worker_records_canonical_high_model_and_read_only_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    state = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    states = iter([state, state])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout="DECISION: pass", stderr=""
        ),
    )

    receipt = ariadne_antigravity.run_worker(
        packet_path=packet,
        cwd=tmp_path,
        output_path=output,
        model="gemini-3.6-flash-high",
        os_sandbox=False,
    )

    assert receipt["model"] == "gemini-3.6-flash-high"
    assert receipt["reasoning_effort"] == "high"
    assert receipt["transport"] == (
        "antigravity_new_project_bound_readonly_worktree"
    )
    assert output.is_file()


def test_run_worker_fails_if_verifier_modifies_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    packet = tmp_path / "packet.md"
    packet.write_text("Review only.", encoding="utf-8")
    output = tmp_path / "receipt.json"
    before = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=False,
    )
    after = WorktreeState(
        root=tmp_path,
        branch="codex/verifier-candidate",
        head="abc123",
        dirty=True,
    )
    states = iter([before, after])
    monkeypatch.setattr(
        ariadne_antigravity,
        "inspect_worktree",
        lambda *_args, **_kwargs: next(states),
    )
    monkeypatch.setattr(
        ariadne_antigravity.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout="DECISION: pass", stderr=""
        ),
    )

    with pytest.raises(RuntimeError, match="modified its read-only candidate"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=tmp_path,
            output_path=output,
            model="gemini-3.6-flash-high",
            os_sandbox=False,
        )

    assert not output.exists()
