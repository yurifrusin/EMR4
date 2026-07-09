from pathlib import Path


AGENTS = Path("AGENTS.md")
SPRINT_CLOSEOUT = Path("orchestration/sprint_closeout.md")
INTEGRATION_LOG = Path("orchestration/integration_log.md")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_sprint285_publication_state_is_not_left_pending():
    agent_text = _text(AGENTS)
    closeout = _text(SPRINT_CLOSEOUT)
    log = _text(INTEGRATION_LOG)

    assert "2c6cd5146b1c8c9538873f4a3f2e3a2970191077" in agent_text
    assert "| Status | Published to `origin/master` and `handoff/current`; worktree clean |" in closeout
    assert "| Commit | `2c6cd5146b1c8c9538873f4a3f2e3a2970191077` |" in closeout
    assert "| Push | `master` and `handoff/current` pushed successfully |" in closeout
    assert "| Final status | `## master...origin/master` |" in closeout
    assert "| `2c6cd514` | integrated and pushed |" in log

    current_block = closeout.split("## Current Closeout", 1)[1].split(
        "## Previous Closeout - Sprint 284", 1
    )[0]
    assert "pending commit/push" not in current_block.lower()
    assert "pending push" not in current_block.lower()
    assert "pending worker review" not in agent_text.lower()
