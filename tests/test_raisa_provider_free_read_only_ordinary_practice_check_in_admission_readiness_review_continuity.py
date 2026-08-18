from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review"
)
PARENT = "ariadne-post-native-harness-successor-resolution-repair"
SOURCE_HEAD = "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_readiness_review_is_current_and_fail_closed() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 323
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 305
    assert compass["source_graph_revision"] == 323
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert "not ready" in " ".join(node["authority"]["notes"])


def test_compass_names_measured_control_plane_successor_and_default_denial() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "closeout control plane" in current["strategic_role"]
    assert "Yuri explicitly prioritized" in current["why_now"]
    assert "typed closeout manifest" in current["outcome"]
    assert "without coverage loss" in current["outcome"]
    closed = " ".join(current["does_not_solve"])
    assert "No ordinary practice is enabled" in closed
    assert "No product/configuration source" in closed
    assert "No product data" in closed
    assert "Continuity 323 / Compass 305" in compass["orientation_statement"]
    assert "efficacy rehearsal" in compass["orientation_statement"]


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-closeout.md",
        "orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-admission-readiness-review-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-18--ordinary-practice-canonical-check-in-admission-readiness-review.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-18" in head
        assert "Timestamp: 2026-08-18T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = (
        ROOT
        / "scripts/raisa_provider_free_read_only_ordinary_practice_check_in_admission_readiness_review_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_resolution = resolve_commit_source" in source
