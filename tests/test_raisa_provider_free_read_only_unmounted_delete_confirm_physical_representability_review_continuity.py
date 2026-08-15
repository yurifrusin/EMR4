from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review"
)
OPERATION_ID = "raisa-reception-one-delete-confirm-physical-representability-review"
SOURCE_HEAD = "bc066a1b639c5c57cc72f2697c063c5842511840"
NEXT_HORIZON = "reception-one-delete-confirm-physical-design-architecture"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_representability_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 297
    assert compass["map_revision"] >= 279
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_claim_scope_preserves_verdict_calibration_and_closed_runtime() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in (
        "twenty-six line-bound observations",
        "positive monotonic version",
        "representable with additive change",
        "implementation remains not admitted",
        "current mounted route remains unadmitted",
        "postgresql",
        "reception one cancellation composition remain closed",
    ):
        assert phrase in joined


def test_compass_advances_only_to_unmounted_physical_design() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    horizon = next(
        item for item in compass["decision_horizon"] if item["id"] == NEXT_HORIZON
    )
    assert horizon["status"] == "active"
    assert horizon["boundary_changes"] == []
    joined = " ".join(horizon["prerequisites"]).lower()
    assert "declarative and unmounted" in joined
    assert "current-authority non-disclosure" in joined
    assert all(
        item["id"] != "reception-one-delete-confirm-physical-representability"
        for item in compass["decision_horizon"]
    )


def test_latch_completes_without_user_attention() -> None:
    latch = _load("orchestration/continuity/ariadne-active-operation-latch/current.json")
    assert latch["operation_id"] == OPERATION_ID
    assert latch["status"] == "complete"
    assert latch["source_head"] == SOURCE_HEAD
    assert latch["checkpoint"]["next_executable_stage"] is None
    assert latch["resume_after_compaction"] is False
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is True


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review-closeout.md",
        "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-representability-review-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--delete-confirm-physical-representability-review.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_name_result_and_next_closed_gate() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = " ".join((ROOT / "implementation_plan.md").read_text(encoding="utf-8").split())
    for text in (handover, plan):
        assert SOURCE_HEAD in text
        assert "physical-design architecture" in text.lower()
        assert "current mounted" in text.lower()
    assert "Continuity 297 / Compass 279" in handover
    assert (
        "raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass"
        in handover
    )
