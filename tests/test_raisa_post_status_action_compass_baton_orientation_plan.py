from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-post-status-action-compass-baton-orientation-plan.md"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def test_plan_freezes_truth_parity_orientation_without_product_authority() -> None:
    text = PLAN.read_text(encoding="utf-8")
    head = "\n".join(text.splitlines()[:16])
    assert "Date: 2026-08-13" in head
    assert "Timestamp: 2026-08-13T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "Reasoning level: Extra High" in text
    for phrase in (
        "**truth\n  parity**",
        "not yet feature parity",
        "kernel, not any visual",
        "projection-neutral truth-parity contract",
        "another already-existing Diary command",
        "representative Stage 3B",
        "external patient channel",
        "another event family",
        "general visual polish",
        "No product behavior, FastAPI, GraphQL, OpenAPI, database",
    ):
        assert phrase in text


def test_active_latch_holds_read_only_orientation_open() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    assert latch["operation_id"] == "raisa-post-status-action-compass-baton-orientation"
    assert latch["status"] == "in_progress"
    assert latch["source_head"] == "aefe6938002eae2b7c420e973912fa7973a5d901"
    assert latch["resume_after_compaction"] is True
    assert latch["user_attention"] == {"required": False, "reason": None}
    assert latch["terminal_response"] == {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    assert "orientation_read_only_no_product_behavior" in latch["protected_boundaries"]
