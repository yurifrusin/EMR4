from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"
PARENT = (
    "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal"
)
SOURCE_HEAD = "f6cbd33fd3322754e06ac6dafa1503f5200e0803"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_shadow_clockwork_architecture_is_current_without_live_adoption() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 327
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert "sole source of causal bureaucratic time" in " ".join(
        node["authority"]["notes"]
    )
    assert "Live clock adoption" in " ".join(node["unresolved_gates"])


def test_compass_names_provider_free_shadow_gear_rehearsal_successor() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    assert "Freeze one causal clock" in journey["strategic_role"]
    assert "Architecture accepted" in journey["outcome"]
    assert any(path.endswith("architecture-report.md") for path in journey["evidence"])


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-gear-architecture-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-19--shadow-clockwork-deepseek-broker-gear-architecture.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = (
        ROOT
        / "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_architecture_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_resolution = resolve_commit_source" in source
