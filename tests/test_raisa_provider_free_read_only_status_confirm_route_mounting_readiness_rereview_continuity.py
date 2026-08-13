import copy
import json
from pathlib import Path

from scripts import (
    raisa_provider_free_read_only_status_confirm_route_mounting_readiness_rereview_continuity_update as continuity,
)


ROOT = Path(__file__).resolve().parents[1]


def test_continuity_update_matches_accepted_result() -> None:
    graph = json.loads((ROOT / "orchestration/continuity/emr4-continuity-graph.json").read_text(encoding="utf-8"))
    compass = json.loads((ROOT / "orchestration/continuity/emr4-compass.json").read_text(encoding="utf-8"))

    assert graph["graph_revision"] == 270
    assert compass["map_revision"] == 252
    node = next(node for node in graph["nodes"] if node["id"] == continuity.NODE_ID)
    assert node["coordinates"]["source_head"] == continuity.SOURCE_HEAD
    assert compass["current_position"]["node_id"] == continuity.NODE_ID
    assert "four remaining product-adapter blockers" in compass["orientation_statement"]


def test_update_rejects_wrong_baseline_or_duplicate() -> None:
    graph = json.loads((ROOT / "orchestration/continuity/emr4-continuity-graph.json").read_text(encoding="utf-8"))
    compass = json.loads((ROOT / "orchestration/continuity/emr4-compass.json").read_text(encoding="utf-8"))
    graph["graph_revision"] = 269
    graph["nodes"] = [node for node in graph["nodes"] if node["id"] != continuity.NODE_ID]
    compass["map_revision"] = 251
    updated_graph, _ = continuity.update(copy.deepcopy(graph), copy.deepcopy(compass))
    assert updated_graph["graph_revision"] == 270

    wrong = copy.deepcopy(graph)
    wrong["graph_revision"] = 268
    try:
        continuity.update(wrong, copy.deepcopy(compass))
    except ValueError as exc:
        assert "baseline" in str(exc)
    else:
        raise AssertionError("wrong baseline admitted")
