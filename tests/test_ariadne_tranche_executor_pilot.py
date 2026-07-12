from pathlib import Path

import yaml


SETTINGS = Path(__file__).resolve().parents[1] / "orchestration" / "harness_settings"


def test_terra_pilot_preserves_protected_master_and_conductor_authority():
    pilot = yaml.safe_load((SETTINGS / "tranche_executor_pilot.yaml").read_text(encoding="utf-8"))

    assert pilot["schema_version"] == "ariadne.tranche_executor_pilot.v1"
    assert pilot["pilot_sprints"] == ["S10", "S11", "S12"]
    assert pilot["tranche_gate_owner"] == "gpt-sol"
    denied = set(pilot["executor"]["authority"]["may_not"])
    assert "define_or_reallocate_sprint_work" in denied
    assert "change_scope_or_acceptance_criteria" in denied
    assert "integrate_or_push_protected_master" in denied


def test_luna_is_disabled_for_first_pilot():
    pilot = yaml.safe_load((SETTINGS / "tranche_executor_pilot.yaml").read_text(encoding="utf-8"))

    assert pilot["mechanical_coordinator"]["enabled"] is False
