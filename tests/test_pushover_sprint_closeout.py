from __future__ import annotations

import sys
from pathlib import Path

from scripts import notify_sprint_closeout


ROOT = Path(__file__).resolve().parents[1]


def test_closeout_message_states_continuing_or_paused():
    continuing = notify_sprint_closeout.build_closeout_message(
        sprint="T3R2",
        checks="approval gate passed",
        engine_state="continuing",
        next_or_reason="adapter contract work",
    )
    paused = notify_sprint_closeout.build_closeout_message(
        sprint="T3R2",
        checks="approval gate passed",
        engine_state="paused",
        next_or_reason="explicit Yuri approval",
    )

    assert "Sprint engine continuing with adapter contract work" in continuing
    assert "Sprint engine paused for explicit Yuri approval" in paused
    assert continuing.endswith("Open Codex for details.")
    assert paused.endswith("Open Codex for details.")


def test_closeout_cli_forces_pushover_and_supports_redacted_dry_run(monkeypatch):
    captured: list[str] = []

    def fake_notify(argv: list[str]) -> int:
        captured.extend(argv)
        return 0

    monkeypatch.setattr(notify_sprint_closeout, "notify_yuri_main", fake_notify)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "notify_sprint_closeout.py",
            "--sprint",
            "T3R2",
            "--checks",
            "tests green",
            "--paused",
            "explicit approval",
            "--dry-run",
        ],
    )

    assert notify_sprint_closeout.main() == 0
    assert captured[0:2] == ["--provider", "pushover"]
    assert "--dry-run" in captured
    assert any("Sprint engine paused for explicit approval" in item for item in captured)


def test_live_handover_requires_pushover_after_ref_alignment():
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "send the non-PHI Pushover closeout ping" in handover
    assert "scripts/notify_sprint_closeout.py" in handover
    assert "If delivery" in handover
    assert "fails, report that explicitly" in handover
