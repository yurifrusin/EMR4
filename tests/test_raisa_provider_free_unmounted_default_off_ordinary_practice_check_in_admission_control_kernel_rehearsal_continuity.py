from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal"
)
PARENT = (
    "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture"
)
SOURCE_HEAD = "4204ec6348abb0f92b1a30314699d4a469fa860a"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_kernel_is_current_without_enablement() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 326
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 308
    assert compass["source_graph_revision"] == 326
    assert compass["current_position"]["node_id"] == NODE_ID
    node = graph["nodes"][-1]
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert "zero active ordinary records" in " ".join(node["authority"]["notes"])
    assert "clock and DeepSeek broker gear remain shadow-only" in " ".join(
        node["unresolved_gates"]
    )


def test_compass_names_shadow_clockwork_gear_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert "shadow Ariadne and DeepSeek broker clockwork gear" in current["strategic_role"]
    assert SOURCE_HEAD in current["why_now"]
    assert "digest-linked causal tick/result protocol" in current["outcome"]
    closed = " ".join(current["does_not_solve"])
    assert "No current control is retired" in closed
    assert "No occupied DeepSeek" in closed
    assert "No product, patient, clinical" in closed
    assert "Continuity 326 / Compass 308" in compass["orientation_statement"]


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/raisa-check-in-admission-control-kernel-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-19--unmounted-check-in-admission-control-kernel-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = (
        ROOT
        / "scripts/raisa_provider_free_unmounted_default_off_ordinary_practice_check_in_admission_control_kernel_rehearsal_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_resolution = resolve_commit_source" in source
