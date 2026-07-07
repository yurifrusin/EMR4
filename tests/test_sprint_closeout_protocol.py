from pathlib import Path


PROTOCOL_ALERTS = Path("orchestration/protocol_alerts.md")
SPRINT_CLOSEOUT = Path("orchestration/sprint_closeout.md")
AGENTS = Path("AGENTS.md")


def test_protocol_alerts_require_committed_pushed_clean_sprint_closeout():
    text = PROTOCOL_ALERTS.read_text(encoding="utf-8", errors="replace")

    assert "Sprint closeout is not complete" in text
    assert "committed, pushed, and the integration worktree is clean" in text
    assert "git status --short --branch" in text
    assert "git commit" in text
    assert "git push origin master" in text
    assert "local-only" in text
    assert "pending commit" in text
    assert "pending push" in text


def test_sprint_closeout_template_records_publication_state():
    text = SPRINT_CLOSEOUT.read_text(encoding="utf-8", errors="replace")

    assert "Closeout Completeness Rule" in text
    assert "committed" in text
    assert "pushed to `origin/master`" in text
    assert "integration commit SHA" in text
    assert "push result or explicit push blocker" in text
    assert "final `git status --short --branch`" in text


def test_current_baton_no_longer_describes_sprint_139_as_local_only():
    text = AGENTS.read_text(encoding="utf-8", errors="replace")

    assert "Sprint 152 create-proposal `minLength: 8` readiness decision" in text
    assert "Sprint 139 update-confirm idempotency preflight completed locally" not in text
    assert "Sprint 140 update-confirm idempotency route-test contract completed locally" not in text
