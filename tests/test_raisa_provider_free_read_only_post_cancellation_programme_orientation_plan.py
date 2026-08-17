from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-post-cancellation-programme-orientation-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-read-only-post-cancellation-programme-orientation-threat-model-delta.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_is_timestamped_exact_head_bound_and_read_only() -> None:
    plan = _text(PLAN)
    head = "\n".join(plan.splitlines()[:18])
    assert "Date: 2026-08-18" in head
    assert "Timestamp: 2026-08-18T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "5981b6cacdd3d488462803748c0d86f1e9bc2457" in head
    assert "frozen_for_read_only_execution" in head
    assert "Reasoning level: Extra High" in plan


def test_plan_requires_full_command_and_consumer_matrix() -> None:
    plan = _text(PLAN)
    for phrase in (
        "create/slot selection",
        "update/reschedule",
        "status",
        "waiting-area movement",
        "delete/cancel",
        "dedicated check-in",
        "patient linking",
        "ordinary Diary consumer posture",
        "Reception One consumer posture",
    ):
        assert phrase in plan


def test_plan_and_threat_keep_default_off_route_distinct_from_admission() -> None:
    corpus = (_text(PLAN) + _text(THREAT)).lower()
    for phrase in (
        "default-off authored-synthetic route",
        "generally admitted product command",
        "route existence as product admission",
        "static grammar and route-contract files remain read-only",
        "events remain acceleration hints",
    ):
        assert phrase in corpus


def test_parallelism_and_closed_surfaces_are_explicit() -> None:
    plan = _text(PLAN)
    assert "DeepSeek V4 Flash/high — declined" in plan
    assert "Gemini 3.7 Flash/high — reserved" in plan
    assert "Native subagents — declined" in plan
    assert "No product behavior" in plan
    assert "explicit-path staging only" in plan
