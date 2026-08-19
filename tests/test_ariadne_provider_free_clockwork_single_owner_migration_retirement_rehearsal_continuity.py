from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_clockwork_migration_is_current_accepted_continuity() -> None:
    graph = _json("orchestration/continuity/emr4-continuity-graph.json")
    compass = _json("orchestration/continuity/emr4-compass.json")
    node = graph["nodes"][-1]

    assert graph["graph_revision"] == 330
    assert compass["map_revision"] == 312
    assert compass["source_graph_revision"] == 330
    assert node["id"] == "ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal"
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == "d03cc6386fdf3e2714881089514380d93824e160"
    assert compass["current_position"]["node_id"] == node["id"]
    assert compass["journey"][-1]["node_id"] == node["id"]


def test_clockwork_migration_claims_and_boundaries_are_exact() -> None:
    graph = _json("orchestration/continuity/emr4-continuity-graph.json")
    compass = _json("orchestration/continuity/emr4-compass.json")
    node = graph["nodes"][-1]
    claims = "\n".join(node["claim_scope"])
    gates = "\n".join(node["unresolved_gates"])
    closed = "\n".join(compass["current_position"]["does_not_solve"])

    assert "ten mirror surfaces" in claims
    assert "twenty-three fault checkpoints" in claims
    assert "twenty-five reruns" in claims
    assert "live canonical adoption/retirement" in gates
    assert "does not activate" in closed
    assert "No DeepSeek Harness" in closed
    assert "Continuity 330 / Compass 312" in compass["orientation_statement"]


def test_all_bound_evidence_exists() -> None:
    compass = _json("orchestration/continuity/emr4-compass.json")
    missing = [path for path in compass["journey"][-1]["evidence"] if not (ROOT / path).exists()]
    assert missing == []


def test_closeout_records_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-19--clockwork-single-owner-migration-retirement-rehearsal.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_updater_validates_prospective_state_before_canonical_writes() -> None:
    path = ROOT / "scripts/ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal_continuity_update.py"
    source = path.read_text(encoding="utf-8")
    validation = source.index("report = ariadne_compass.build_compass_report")
    rejection = source.index('if report["status"] != "passed"')
    graph_write = source.index("_write(GRAPH, graph)")
    compass_write = source.index("_write(COMPASS, compass)")
    assert validation < rejection < graph_write < compass_write
    assert "source_head = resolve_commit_source" in source
