from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-reception-one-selected-appointment-duration-composition-plan.md"
THREAT = ROOT / "docs/security/raisa-reception-one-selected-appointment-duration-composition-threat-model-delta.md"


def test_plan_and_threat_freeze_duration_only_existing_command_composition() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for document in (plan, threat):
        head = "\n".join(document.splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
    for phrase in (
        "Task baseline: `268e90316c3ef248385ec19d25768c20aed2f3fe`",
        "Only mutable meaning:** `duration_minutes`",
        "whole 15-minute deltas",
        "15 through 480 minutes",
        "fixes\n   `deltaStart` at zero",
        "DeepSeek V4 Flash/high — planned",
        "Native subagent — planned",
        "Gemini 3.6 Flash/high — reserved",
        "No FastAPI, GraphQL, OpenAPI, database/migration/RLS",
    ):
        assert phrase in plan
    for phrase in (
        "supplies literal zero `deltaStart`",
        "integer 15..480 targets",
        "delta is divisible by 15",
        "GraphQL is read-only",
        "zero raw `PUT`",
    ):
        assert phrase in threat
