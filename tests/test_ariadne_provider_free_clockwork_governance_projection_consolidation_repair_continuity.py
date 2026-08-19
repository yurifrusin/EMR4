from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-provider-free-clockwork-governance-projection-consolidation-repair"
PARENT = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
SOURCE_HEAD = "a0bb86b78bfc011066142740c82d5c25cab7b9c8"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_private_shadow_repair_is_current_and_live_adoption_is_closed() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 329
    assert compass["map_revision"] == 311
    assert compass["source_graph_revision"] == 329
    node = graph["nodes"][-1]
    assert node["id"] == NODE_ID and node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["authority"]["authorized_openings"] == []
    assert node["decisions"][0]["status"] == "accepted"
    assert "live migration-and-retirement" in " ".join(node["unresolved_gates"])
    assert compass["current_position"]["node_id"] == NODE_ID


def test_compass_records_metrics_and_user_attention_gate() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert SOURCE_HEAD in current["why_now"]
    assert "sixty percent" in current["why_now"]
    assert "two repair-only closeouts" in current["why_now"]
    assert "Yuri chooses either" in current["outcome"]
    closed = " ".join(current["does_not_solve"])
    assert "does not authorize live adoption" in closed
    assert "No DeepSeek Harness" in closed
    assert "No product, practice, data, Git" in closed
    assert "Continuity 329 / Compass 311" in compass["orientation_statement"]


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-provider-free-clockwork-governance-projection-consolidation-repair-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-consolidation-repair-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-19--clockwork-governance-projection-consolidation-repair.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = (
        ROOT
        / "scripts/ariadne_provider_free_clockwork_governance_projection_consolidation_repair_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_head = resolve_commit_source" in source
