from pathlib import Path

import pytest

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
        model="Gemini 3.5 Flash (High)",
        os_sandbox=False,
    )

    assert command[:2] == ["agy", "-p"]
    assert "--new-project" in command
    assert command[command.index("--add-dir") + 1] == "C:\\worktrees\\bounded"
    assert "BOUND BRANCH: antigravity/bounded" in command[2]
    assert "--sandbox" not in command


def test_os_sandbox_is_explicit_and_never_the_unattended_default():
    command = build_command(
        packet="Review.",
        state=_state(),
        model="Gemini 3.5 Flash (Medium)",
        os_sandbox=True,
    )

    assert command[-1] == "--sandbox"


def test_command_rejects_non_gemini_flash_model():
    with pytest.raises(ValueError, match="unsupported Antigravity model"):
        build_command(
            packet="Review.",
            state=_state(),
            model="Claude Opus 4.6 (Thinking)",
            os_sandbox=False,
        )
