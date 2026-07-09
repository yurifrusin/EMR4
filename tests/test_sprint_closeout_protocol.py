from pathlib import Path


PROTOCOL_ALERTS = Path("orchestration/protocol_alerts.md")
SPRINT_CLOSEOUT = Path("orchestration/sprint_closeout.md")
AGENTS = Path("AGENTS.md")
SPRINT_257_BLOCK = Path("orchestration/sprint_257_practitioner_directory_worker_readiness_block.md")
SPRINT_257_CLAUDE = Path("orchestration/agent_inbox/claude/claude-sprint257-practitioner-readiness-veto.md")
SPRINT_257_ANTIGRAVITY = Path(
    "orchestration/agent_inbox/antigravity/antigravity-sprint257-practitioner-consumer-boundary.md"
)
SPRINT_257_DEEPSEEK = Path("orchestration/agent_inbox/codex/codex-sprint257-deepseek-mechanical-sweep.md")


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

    assert "Sprint 156 status/delete confirm client header emission" in text
    assert "Sprint 139 update-confirm idempotency preflight completed locally" not in text
    assert "Sprint 140 update-confirm idempotency route-test contract completed locally" not in text


def test_diary_ui_evidence_prefers_committed_playwright_harnesses():
    agent_text = AGENTS.read_text(encoding="utf-8", errors="replace")
    alert_text = PROTOCOL_ALERTS.read_text(encoding="utf-8", errors="replace")
    combined = f"{agent_text}\n{alert_text}"

    assert "review/test_diary_smoke.py" in combined
    assert "Playwright/pytest harnesses" in combined
    assert "route-intercepted checks" in combined
    assert "Browser plugin is supplemental" in combined
    assert "replace committed" in combined
    assert "Playwright regression evidence" in combined


def test_worker_enumeration_requires_distinct_artifacts_or_veto_surfaces():
    agent_text = AGENTS.read_text(encoding="utf-8", errors="replace")
    alert_text = PROTOCOL_ALERTS.read_text(encoding="utf-8", errors="replace")
    combined = f"{agent_text}\n{alert_text}"

    assert "Worker enumeration is not itself evidence" in combined
    assert "empty ritual" in combined
    assert "distinct artifact or veto surface" in combined
    assert "implementation owner" in combined
    assert "independent review/veto" in combined
    assert "consumer/product review" in combined
    assert "mechanical safety sweep" in combined
    assert "intentionally stood down" in combined
    assert "combine related" in combined
    assert "micro-sprints into one evidence/review block" in combined
    assert "split broad sprints" in combined
    assert "Ariadne-local" in combined


def test_sprint_257_worker_readiness_block_is_prepared():
    text = SPRINT_257_BLOCK.read_text(encoding="utf-8", errors="replace")

    assert "Sprint 257 Practitioner Directory Worker Readiness Block" in text
    assert "one multi-worker go/no-go decision block" in text
    assert "distinct artifact or veto surface" in text
    assert "Claude" in text
    assert "Antigravity" in text
    assert "DeepSeek" in text
    assert "rest_route_ready=true" in text
    assert "must not flip the readiness flag by itself" in text
    assert "Yuri approval" in text


def test_sprint_257_worker_packets_have_distinct_roles():
    claude = SPRINT_257_CLAUDE.read_text(encoding="utf-8", errors="replace")
    antigravity = SPRINT_257_ANTIGRAVITY.read_text(encoding="utf-8", errors="replace")
    deepseek = SPRINT_257_DEEPSEEK.read_text(encoding="utf-8", errors="replace")

    assert "readiness/safety veto packet" in claude
    assert "maps findings to Sprint 255 readiness criteria" in claude
    assert "consumer/API ergonomics and external-client boundary" in antigravity
    assert "external exposure concern" in antigravity
    assert "mechanical static sweep" in deepseek
    assert "readiness flag flips" in deepseek
    assert "No readiness flag change" in deepseek
