from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review"
)
SOURCE_HEAD = "3bed3eb32dd1b8723bf5aa6218963b757ebc0e3d"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_convergence_review_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 315
    assert compass["map_revision"] >= 297
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_compass_selects_dedicated_check_in_without_runtime_opening() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "unmounted product adapter" in compass["current_position"]["outcome"]
    assert "No A5.1 feature flag" in " ".join(
        compass["current_position"]["does_not_solve"]
    )
    assert "Continuity 315 / Compass 297" in compass["orientation_statement"]


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review-closeout.md",
        "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--arrival-check-in-command-family-convergence-review.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head
