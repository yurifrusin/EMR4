from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-plan.md"
THREAT = ROOT / "docs/security/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-threat-model-delta.md"


def test_plan_and_threat_freeze_practitioner_only_existing_command_composition() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for document in (plan, threat):
        head = "\n".join(document.splitlines()[:14])
        assert "Date: 2026-08-14" in head
        assert "Timestamp: 2026-08-14T" in head
        assert "+10:00 (Australia/Brisbane)" in head
    for phrase in (
        "Task baseline: `e3015f36a9f93b7fc9382908a16c8a729fefc590`",
        "Only mutable meaning:** `practitioner_id`",
        "`active === true`",
        "literal zero `deltaStart`, literal zero `deltaDuration`",
        "DeepSeek V4 Flash/high -- planned",
        "Native subagent -- planned",
        "Gemini 3.6 Flash/high -- reserved",
        "No FastAPI, GraphQL, OpenAPI, database/migration/RLS",
    ):
        assert phrase in plan
    for phrase in (
        "supplies literal zero `deltaStart` and `deltaDuration`",
        "exactly one matching active row",
        "Template-only rows",
        "GraphQL stays read-only",
        "zero raw `PUT`",
    ):
        assert phrase in threat
