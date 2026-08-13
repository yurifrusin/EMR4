from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-reception-one-selected-appointment-status-action-composition-plan.md"
THREAT = (
    ROOT
    / "docs/security/raisa-reception-one-selected-appointment-status-action-composition-threat-model-delta.md"
)
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_and_threat_delta_freeze_the_narrow_existing_command_composition() -> None:
    plan = _text(PLAN)
    threat = _text(THREAT)
    for document in (plan, threat):
        head = "\n".join(document.splitlines()[:12])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head

    for token in (
        "existing `setAppointmentStatus`",
        "one current\n   non-synthetic-placeholder appointment",
        "no `fetch`, proposal, confirm",
        "discard stale Back history",
        "route_intercepted_browser",
        "authored_synthetic_client_fixture",
        "No FastAPI, GraphQL, OpenAPI, database/migration/RLS",
    ):
        assert token in plan

    for token in (
        "does not\nadd write authority",
        "calls `setAppointmentStatus`",
        "Suppress the workspace-level Escape close",
        "GraphQL remains read-only",
        "Events\nremain optional acceleration hints",
    ):
        assert token in threat


def test_active_latch_holds_execution_open_at_the_frozen_plan_boundary() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    assert latch["operation_id"] == (
        "raisa-reception-one-selected-appointment-status-action-composition"
    )
    assert latch["status"] == "in_progress"
    assert latch["source_head"] == "9a1401665bc6163145bbcbbb53d06ce3f4abd036"
    assert latch["resume_after_compaction"] is True
    assert latch["terminal_response"] == {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    assert "existing_status_vocabulary_and_existing_set_appointment_status_interaction_only" in latch[
        "protected_boundaries"
    ]
