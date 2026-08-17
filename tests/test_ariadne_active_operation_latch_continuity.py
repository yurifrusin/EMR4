from __future__ import annotations

import json
from pathlib import Path

from orchestration_harness.active_operation import validate_active_operation


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-postcompaction-active-operation-latch"
SOURCE_HEAD = "ac62a6f65612acb624f14b53ba86b1a9dbf72dab"
CURRENT_LATCH = "orchestration/continuity/ariadne-active-operation-latch/current.json"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_latch_is_accepted_without_displacing_product_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert graph["graph_revision"] >= 274
    assert compass["map_revision"] >= 256
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] != NODE_ID
    assert compass["current_position"]["node_id"] in {
        item["node_id"] for item in compass["journey"]
    }
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_current_latch_validly_projects_its_live_operation_state() -> None:
    latch = _load(
        "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    assert validate_active_operation(latch) == latch


def test_arrival_closeout_or_successor_latch_binds_transition_evidence() -> None:
    latch = _load(CURRENT_LATCH)

    if (
        latch["operation_id"]
        == "raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review"
    ):
        assert latch["status"] == "complete"
        completed = latch["checkpoint"]["completed_stage"]
        assert "register revision 365 with 416 incidents" in completed
        assert "404-check closeout packet" in completed
        assert "AER-0413 through AER-0416" in completed
    else:
        assert latch["operation_id"] == (
            "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
            "extraction-rehearsal"
        )
        assert latch["status"] == "in_progress"
        assert len(latch["source_head"]) == 40
        assert all(char in "0123456789abcdef" for char in latch["source_head"])
        completed = latch["checkpoint"]["completed_stage"]
        assert "AER-0419" in completed
        assert "no same-lane retry" in completed
    if latch["status"] == "in_progress":
        assert latch["resume_after_compaction"] is True
        assert latch["checkpoint"]["next_executable_stage"]
        assert latch["user_attention"]["required"] is False
        assert latch["terminal_response"] == {
            "permitted": False,
            "reason": "unfinished_authorized_operation",
        }


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-postcompaction-active-operation-latch-plan.md",
        "docs/security/ariadne-postcompaction-active-operation-latch-threat-model-delta.md",
        "docs/ariadne-postcompaction-active-operation-latch-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-active-operation-latch-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-13--ariadne-postcompaction-active-operation-latch.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_live_handover_names_latch_and_timestamp_rule() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "ariadne-active-operation-latch/current.json" in text
    assert "terminal final response is prohibited" in text
    assert "Australia/Brisbane" in text
