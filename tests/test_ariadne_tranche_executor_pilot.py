from pathlib import Path

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"


def test_terra_pilot_preserves_protected_master_and_conductor_authority():
    pilot = yaml.safe_load((SETTINGS / "tranche_executor_pilot.yaml").read_text(encoding="utf-8"))

    assert pilot["schema_version"] == "ariadne.tranche_executor_pilot.v1"
    assert pilot["status"] == "active_revised_pilot"
    assert pilot["pilot_sprints"] == ["S10", "S11", "S12"]
    assert pilot["executed_sprints"] == ["S10"]
    assert pilot["resumed_sprints"] == ["S11", "S12"]
    assert pilot["tranche_gate_owner"] == "gpt-sol"
    denied = set(pilot["executor"]["authority"]["may_not"])
    assert "change_sol_tranche_direction" in denied
    assert "expand_scope_or_acceptance_authority" in denied
    assert "self_authorize_protected_master_integration" in denied


def test_luna_is_disabled_for_first_pilot():
    pilot = yaml.safe_load((SETTINGS / "tranche_executor_pilot.yaml").read_text(encoding="utf-8"))

    assert pilot["mechanical_coordinator"]["enabled"] is False
