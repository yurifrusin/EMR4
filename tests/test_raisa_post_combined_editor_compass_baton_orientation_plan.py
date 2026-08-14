from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-post-combined-editor-compass-baton-orientation-plan.md"
THREAT = ROOT / "docs/security/raisa-post-combined-editor-compass-baton-orientation-threat-model-delta.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_is_read_only_timestamped_and_exact_head_bound() -> None:
    plan = _text(PLAN)
    head = "\n".join(plan.splitlines()[:18])
    assert "Date: 2026-08-15" in head
    assert "Timestamp: 2026-08-15T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "aa2b34573d47e0a81ae689cb20b0461b3585c221" in head
    assert "frozen_for_read_only_execution" in head


def test_plan_covers_the_full_programme_fork_without_opening_it() -> None:
    plan = _text(PLAN).lower()
    for phrase in (
        "cancellation/delete-family direction",
        "check-in/waiting-area composition",
        "first external patient channel",
        "representative stage 3b sessions",
        "another typed diary event family",
        "operational durable-cue delivery",
        "visual polish",
        "genuine user-attention fork",
    ):
        assert phrase in plan
    assert "do not open one by analogy" in plan


def test_revocation_and_committed_reversal_are_distinct() -> None:
    corpus = (_text(PLAN) + _text(THREAT)).lower()
    assert "revocable for future acts" in corpus
    assert "already committed appointment" in corpus
    assert "separately authorised cancellation or rescheduling command" in corpus


def test_parallelism_is_explicitly_assessed() -> None:
    plan = _text(PLAN)
    assert "DeepSeek V4 Flash/high — declined" in plan
    assert "Gemini 3.6 Flash/high — reserved" in plan
    assert "Native subagents — declined" in plan
