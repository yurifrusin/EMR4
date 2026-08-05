from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_context_fabric_is_durable_but_unimplemented_direction() -> None:
    direction = (ROOT / "docs/raisa-practice-context-fabric-direction.md").read_text(
        encoding="utf-8"
    )
    implementation_plan = (ROOT / "implementation_plan.md").read_text(encoding="utf-8")
    interaction_model = (
        ROOT / "orchestration/bernie_interaction_model.md"
    ).read_text(encoding="utf-8")
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Status: accepted strategic architecture direction; implementation unstarted" in direction
    assert "ContextNeed" in direction
    assert "ContextScopeGrant" in direction
    assert "ContextFrameSet" in direction
    assert "ContextWeaveTrace" in direction
    assert "command_authority: false" in direction
    assert "not a single prompt, vector store, global transcript or" in direction
    assert "No patient, product, provider, historical-PHI, clinical" in direction
    assert "### 2.11 Raisa Practice Context Fabric" in implementation_plan
    assert "### Raisa Practice Context Fabric" in interaction_model
    assert "| Raisa Practice Context Fabric direction |" in handover


def test_context_fabric_compass_horizon_is_candidate_without_boundary_opening() -> None:
    compass = json.loads(
        (ROOT / "orchestration/continuity/emr4-compass.json").read_text(
            encoding="utf-8"
        )
    )
    item = next(
        row
        for row in compass["programme_support_horizon"]
        if row["id"] == "raisa-practice-context-fabric"
    )

    assert compass["map_revision"] == 196
    assert compass["source_graph_revision"] == 214
    assert item["status"] == "candidate"
    assert item["boundary_changes"] == []
    assert "docs/raisa-practice-context-fabric-direction.md" in item["evidence"]
    assert any("Separately gate every patient" in value for value in item["prerequisites"])

    rendered = (ROOT / "docs/ariadne-compass-current.md").read_text(encoding="utf-8")
    assert "### Raisa Practice Context Fabric — candidate" in rendered
    assert "_Compass map revision 196; continuity graph revision 214._" in rendered
