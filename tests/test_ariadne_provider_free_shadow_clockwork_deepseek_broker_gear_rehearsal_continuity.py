from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
PARENT = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"
SOURCE_HEAD = "a4044010e9f9319e149660ad889141a32cc8d000"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_rehearsal_evaluation_is_current_and_candidate_is_revision_required() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 328
    assert compass["map_revision"] == 310
    assert compass["source_graph_revision"] == 328
    node = graph["nodes"][-1]
    assert node["id"] == NODE_ID
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]
    assert node["decisions"] == [
        {
            "id": "reject-shadow-clockwork-efficacy-candidate",
            "source": "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-gear-rehearsal-sol-acceptance.md",
            "status": "rejected",
            "summary": "Retain the corrected engine as negative evidence; do not adopt or expand without Yuri's choice.",
        }
    ]
    assert compass["current_position"]["node_id"] == NODE_ID


def test_compass_records_exact_metrics_and_user_attention_fork() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    assert SOURCE_HEAD in current["why_now"]
    assert "thirteen reruns" in current["why_now"]
    assert "maximum-seven" in current["why_now"]
    assert "Yuri chooses either" in current["outcome"]
    closed = " ".join(current["does_not_solve"])
    assert "no automatic repair" in closed
    assert "No DeepSeek Harness" in closed
    assert "No product, practice, data, Git" in closed
    assert "Continuity 328 / Compass 310" in compass["orientation_statement"]
    assert "7.143 percent" in compass["orientation_statement"]


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-gear-rehearsal-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-19--shadow-clockwork-deepseek-broker-gear-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = (
        ROOT
        / "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_rehearsal_continuity_update.py"
    )
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_head = resolve_commit_source" in source
