import json
from copy import deepcopy
from pathlib import Path

from tests.test_api_spine_legacy_compatibility_write_deprecation_map import (
    EXPECTED_COMPATIBILITY_WRITES,
)


ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "docs" / "api-spine" / "raw-compat-header-rollout-gate.json"
READINESS_PATH = ROOT / "docs" / "api-spine" / "raw-compat-consumer-signal-readiness.md"
CONFIG_PATH = ROOT / "app" / "config.py"

EXPECTED_FORBIDDEN = {
    "any_environment_defaulting_appointment_raw_compat_mode_to_header",
    "user_facing_deprecation_ui_without_review",
    "removing_or_blocking_raw_compat_routes",
    "idempotency_enforcement_on_raw_compat_routes",
    "provider_or_dry_run_wiring",
    "memory_rag_or_graphrag_runtime_wiring",
    "h15_or_h_series_runtime_imports",
    "historical_diary_material_access",
    "external_patient_or_fga_client_consumers",
    "graphql_mutations",
    "model_to_database_writes_outside_rest_command_handlers",
}

EXPECTED_PAUSE_TRIGGERS = {
    "decision_changes_from_blocked",
    "any_environment_appears_in_environments_can_default_header",
    "required_before_unblocking_changes",
    "forbidden_current_uses_changes",
}


def _gate() -> dict:
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def _pause_required(gate: dict) -> bool:
    if gate["decision"] != "blocked":
        return True
    if gate["rollout_surface"]["environments_can_default_header"]:
        return True
    if set(gate["required_before_unblocking"]) != set(_gate()["required_before_unblocking"]):
        return True
    if set(gate["forbidden_current_uses"]) != set(_gate()["forbidden_current_uses"]):
        return True
    return False


def test_rollout_gate_is_blocked_by_default():
    gate = _gate()

    assert gate["schema_version"] == "appointment.raw_compat_header_rollout_gate.v1"
    assert gate["decision"] == "blocked"
    assert gate["reviewer"] == ""
    assert gate["reviewed_on"] == ""
    assert gate["rollout_surface"]["environments_can_default_header"] == []
    assert gate["rollout_surface"]["user_facing_ui_consumers"] == []
    assert gate["rollout_surface"]["known_frontend_consumers"] == [
        "docs/diary/diary.js apiFetch console.warn"
    ]


def test_rollout_gate_route_inventory_matches_deprecation_map():
    gate_routes = set(_gate()["rollout_surface"]["routes"])
    expected_routes = {
        f"{public_route} ({raw_compat_tag})"
        for public_route, _handler, raw_compat_tag, _proposals, _confirms
        in EXPECTED_COMPATIBILITY_WRITES
    }

    assert gate_routes == expected_routes
    assert _gate()["rollout_surface"]["backend_site"] == (
        "app.routers.appointments._raw_compat_evidence_and_headers()"
    )


def test_rollout_gate_observability_is_still_unblocked_false():
    signals = _gate()["observability_and_audit_signals"]

    assert signals["already_proven_before_header_default"]
    assert all(signals["already_proven_before_header_default"].values())
    assert signals["required_before_unblocking_any_environment"]
    assert not any(signals["required_before_unblocking_any_environment"].values())


def test_rollout_gate_keeps_header_mode_out_of_current_environments():
    config = CONFIG_PATH.read_text(encoding="utf-8")
    readiness = READINESS_PATH.read_text(encoding="utf-8")
    gate = _gate()

    assert 'appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"' in config
    assert "keep_audit_mode" in readiness
    assert "raw-compat-header-rollout-gate.json" in readiness
    assert "any_environment_defaulting_appointment_raw_compat_mode_to_header" in gate[
        "forbidden_current_uses"
    ]


def test_rollout_gate_forbidden_uses_and_pause_triggers_are_complete():
    gate = _gate()

    assert set(gate["forbidden_current_uses"]) == EXPECTED_FORBIDDEN
    assert set(gate["sprint_engine_pause_required_if"]) == EXPECTED_PAUSE_TRIGGERS


def test_rollout_gate_mutations_require_pause():
    baseline = _gate()
    assert not _pause_required(baseline)

    decision_mutation = deepcopy(baseline)
    decision_mutation["decision"] = "approved"
    assert _pause_required(decision_mutation)

    environment_mutation = deepcopy(baseline)
    environment_mutation["rollout_surface"]["environments_can_default_header"].append("production")
    assert _pause_required(environment_mutation)

    required_mutation = deepcopy(baseline)
    required_mutation["required_before_unblocking"].append("new_requirement")
    assert _pause_required(required_mutation)

    forbidden_mutation = deepcopy(baseline)
    forbidden_mutation["forbidden_current_uses"].remove(
        "any_environment_defaulting_appointment_raw_compat_mode_to_header"
    )
    assert _pause_required(forbidden_mutation)
