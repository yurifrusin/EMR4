from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal"
)
PARENT = (
    "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review"
)
SOURCE_HEAD = "762cd8fd1a6493f4d4b82e24f97d851531b6f7f0"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_shadow_clockwork_is_current_without_live_adoption() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 324
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 306
    assert compass["source_graph_revision"] == 324
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert "shadow-only" in " ".join(node["authority"]["notes"])
    assert "Live control-plane adoption" in " ".join(node["unresolved_gates"])


def test_compass_names_default_off_admission_architecture_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "default-off ordinary-practice" in current["strategic_role"]
    assert "three blocking controls" in current["why_now"]
    assert "default denial remains exact" in current["outcome"]
    closed = " ".join(current["does_not_solve"])
    assert "No ordinary practice is enabled" in closed
    assert "No product route" in closed
    assert "No live clockwork adoption" in closed
    assert "Continuity 324 / Compass 306" in compass["orientation_statement"]


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-19--ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = (
        ROOT
        / "scripts/ariadne_transactional_closeout_control_plane_consolidation_efficacy_rehearsal_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_resolution = resolve_commit_source" in source
