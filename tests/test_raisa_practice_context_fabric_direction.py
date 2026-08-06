from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_context_fabric_is_durable_and_unmounted_lifecycle_is_accepted() -> None:
    direction = (ROOT / "docs/raisa-practice-context-fabric-direction.md").read_text(
        encoding="utf-8"
    )
    implementation_plan = (ROOT / "implementation_plan.md").read_text(
        encoding="utf-8"
    )
    interaction_model = (
        ROOT / "orchestration/bernie_interaction_model.md"
    ).read_text(encoding="utf-8")
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert (
        "Status: accepted direction through the unmounted Rayleen fresh generation"
        in direction
    )
    assert "ContextNeed" in direction
    assert "ContextScopeGrant" in direction
    assert "ContextFrameSet" in direction
    assert "ContextWeaveTrace" in direction
    assert "Bureau Memory Bank" in direction
    assert "never queries or receives raw audit records" in direction
    assert "command_authority: false" in direction
    assert "not a single prompt, vector store, global transcript or" in direction
    assert "No patient, product, provider, historical-PHI, clinical" in direction
    assert "### 2.11 Raisa Practice Context Fabric" in implementation_plan
    assert "### Raisa Practice Context Fabric" in interaction_model
    assert "| Raisa Practice Context Fabric direction |" in handover


def test_context_fabric_compass_horizon_is_active_without_boundary_opening() -> None:
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

    assert compass["map_revision"] == 207
    assert compass["source_graph_revision"] == 225
    assert item["status"] == "active"
    assert item["boundary_changes"] == []
    assert "docs/raisa-practice-context-fabric-direction.md" in item["evidence"]
    assert any(
        "Separately gate every real source/event family" in value
        for value in item["prerequisites"]
    )

    rendered = (ROOT / "docs/ariadne-compass-current.md").read_text(
        encoding="utf-8"
    )
    assert "### Raisa Practice Context Fabric" in rendered
    assert "active" in rendered
    assert "_Compass map revision 207; continuity graph revision 225._" in rendered


def test_branded_workspaces_do_not_become_authority_boundaries() -> None:
    direction = (ROOT / "docs/raisa-practice-context-fabric-direction.md").read_text(
        encoding="utf-8"
    )
    implementation_plan = (ROOT / "implementation_plan.md").read_text(
        encoding="utf-8"
    )
    bureau_architecture = (
        ROOT
        / "docs/emr4-model-required-deterministic-authority-bureau-architecture.md"
    ).read_text(encoding="utf-8")

    for text in (direction, implementation_plan, bureau_architecture):
        lowered = text.lower()
        assert "clinician one" in lowered
        assert "requests" in lowered
        assert "referral" in lowered
        assert "prescri" in lowered
        assert "billing" in lowered
        assert "command" in lowered

    assert "not authorisation domains" in direction
    assert "Atomic backend capability grants" in implementation_plan
    assert "Branded workspaces are not authority boundaries" in bureau_architecture
    assert "brand, screen or occupational label grants nothing" in direction
