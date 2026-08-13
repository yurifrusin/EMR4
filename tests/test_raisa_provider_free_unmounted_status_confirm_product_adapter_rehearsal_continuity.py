import copy
import json
from pathlib import Path

from scripts import (
    raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal_continuity_update as continuity,
)


ROOT = Path(__file__).resolve().parents[1]


def test_continuity_update_matches_accepted_result() -> None:
    graph = json.loads(
        (ROOT / "orchestration/continuity/emr4-continuity-graph.json").read_text(
            encoding="utf-8"
        )
    )
    compass = json.loads(
        (ROOT / "orchestration/continuity/emr4-compass.json").read_text(encoding="utf-8")
    )

    assert graph["graph_revision"] == 271
    assert compass["map_revision"] == 253
    node = next(node for node in graph["nodes"] if node["id"] == continuity.NODE_ID)
    assert node["coordinates"]["source_head"] == continuity.SOURCE_HEAD
    assert compass["current_position"]["node_id"] == continuity.NODE_ID
    assert "product adapter passes" in compass["orientation_statement"]
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Continuity 271 / Compass 253" in agents
    assert continuity.RESULT in agents


def test_update_rejects_wrong_baseline_or_duplicate() -> None:
    graph = json.loads(
        (ROOT / "orchestration/continuity/emr4-continuity-graph.json").read_text(
            encoding="utf-8"
        )
    )
    compass = json.loads(
        (ROOT / "orchestration/continuity/emr4-compass.json").read_text(encoding="utf-8")
    )
    graph["graph_revision"] = 270
    graph["nodes"] = [node for node in graph["nodes"] if node["id"] != continuity.NODE_ID]
    compass["map_revision"] = 252
    updated_graph, _ = continuity.update(copy.deepcopy(graph), copy.deepcopy(compass))
    assert updated_graph["graph_revision"] == 271

    wrong = copy.deepcopy(graph)
    wrong["graph_revision"] = 269
    try:
        continuity.update(wrong, copy.deepcopy(compass))
    except ValueError as exc:
        assert "baseline" in str(exc)
    else:
        raise AssertionError("wrong baseline admitted")
