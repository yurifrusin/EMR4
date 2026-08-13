from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal_continuity_update
    as continuity,
)


ROOT = Path(__file__).resolve().parents[1]


def test_continuity_update_matches_accepted_result() -> None:
    graph = json.loads(continuity.GRAPH_PATH.read_text(encoding="utf-8"))
    compass = json.loads(continuity.COMPASS_PATH.read_text(encoding="utf-8"))
    assert graph["graph_revision"] == 272
    assert compass["map_revision"] == 254
    node = next(node for node in graph["nodes"] if node["id"] == continuity.NODE_ID)
    assert node["coordinates"]["source_head"] == continuity.SOURCE_HEAD
    assert compass["current_position"]["node_id"] == continuity.NODE_ID
    assert "route convergence remains closed" in compass["orientation_statement"]
    agents = continuity.AGENTS_PATH.read_text(encoding="utf-8")
    assert "Continuity 272 / Compass 254" in agents
    assert continuity.RESULT in agents
    assert len(agents.encode("utf-8")) <= 75_000


def test_update_rejects_wrong_baseline_or_duplicate() -> None:
    graph = json.loads(continuity.GRAPH_PATH.read_text(encoding="utf-8"))
    compass = json.loads(continuity.COMPASS_PATH.read_text(encoding="utf-8"))
    graph["graph_revision"] = 271
    graph["nodes"] = [node for node in graph["nodes"] if node["id"] != continuity.NODE_ID]
    compass["map_revision"] = 253
    updated, _ = continuity.update(copy.deepcopy(graph), copy.deepcopy(compass))
    assert updated["graph_revision"] == 272
    wrong = copy.deepcopy(graph)
    wrong["graph_revision"] = 270
    try:
        continuity.update(wrong, copy.deepcopy(compass))
    except ValueError as exc:
        assert "baseline" in str(exc)
    else:
        raise AssertionError("wrong baseline admitted")
