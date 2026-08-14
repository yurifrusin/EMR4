from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-reception-one-selected-action-console-consolidation-orientation-plan.md"
ARCHITECTURE = ROOT / "docs" / "raisa-reception-one-selected-action-console-consolidation-architecture.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-reception-one-selected-action-console-consolidation-orientation-threat-model-delta.md"
)
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-reception-one-selected-action-console-consolidation-orientation"
)


def _json(name: str) -> dict[str, object]:
    return json.loads((CONTINUITY / name).read_text(encoding="utf-8"))


def test_orientation_contract_is_schema_valid() -> None:
    schema = _json("selected-action-console-orientation-contract.schema.json")
    contract = _json("selected-action-console-orientation-contract.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)


def test_orientation_keeps_distinct_command_authorities() -> None:
    contract = _json("selected-action-console-orientation-contract.json")
    authority = contract["field_authority"]
    assert isinstance(authority, dict)
    assert authority["status"] == "existing_status_proposal_confirm_via_metaGridSetAppointmentStatus"
    for field in ("time", "duration", "practitioner"):
        assert authority[field] == "existing_update_proposal_confirm_via_handleMoveResize"
    assert len(set(authority.values())) == 2


def test_orientation_is_single_panel_and_fail_closed() -> None:
    contract = _json("selected-action-console-orientation-contract.json")
    state = contract["state_contract"]
    assert isinstance(state, dict)
    assert state == {
        "initial": "no_editor_open",
        "visible_editors_maximum": 1,
        "switch": "idle_only_discard_unsubmitted_outgoing_draft",
        "busy": "palette_transitions_disabled_active_editor_remains_mounted",
        "terminal": "exact_fresh_reconciliation_then_action_specific_feedback_and_focus",
        "intent": "future_editor_activation_only_never_command",
    }


def test_architecture_freezes_accessibility_and_zero_route_choice() -> None:
    source = ARCHITECTURE.read_text(encoding="utf-8")
    normalized = " ".join(source.split())
    for required in (
        "aria-expanded",
        "aria-controls",
        "44-by-44",
        "zero routes on open/collapse/switch",
        "one polite live",
        "active editor stays mounted during confirmation",
        "must not replace them with one generic",
    ):
        assert required in normalized


def test_plan_and_threat_model_keep_orientation_read_only() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    assert "This is an architecture-orientation tranche only" in plan
    assert "No product HTML/CSS/JavaScript/backend edit" in plan
    assert "This tranche changes no product surface" in threat
    assert "Future intent may select an editor only" in threat


def test_next_tranche_is_narrowly_bound() -> None:
    contract = _json("selected-action-console-orientation-contract.json")
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    normalized = " ".join(architecture.split())
    assert contract["next_tranche"] == (
        "raisa_reception_one_selected_action_console_progressive_disclosure_composition"
    )
    for forbidden in (
        "backend_or_database_change",
        "new_route_or_schema",
        "provider_adc_credentials_iam_or_network",
        "protected_ref_movement",
    ):
        assert forbidden in contract["closed_surfaces"]
    assert "may not change a bridge, executor, request payload, route count" in normalized
