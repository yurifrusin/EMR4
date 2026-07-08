"""Validate the raw compatibility header rollout gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GATE_SCHEMA_VERSION = "appointment.raw_compat_header_rollout_gate.v1"
STATUS_SCHEMA_VERSION = "appointment.raw_compat_header_rollout_gate_status.v1"
DEFAULT_GATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "api-spine"
    / "raw-compat-header-rollout-gate.json"
)

REQUIRED_ROUTES = {
    "POST /api/v1/appointments (raw_compat_create)",
    "PUT /api/v1/appointments/{appointment_id} (raw_compat_update)",
    "PATCH /api/v1/appointments/{appointment_id}/status (raw_compat_status)",
    "DELETE /api/v1/appointments/{appointment_id} (raw_compat_delete)",
}

REQUIRED_PROVEN_SIGNALS = {
    "all_routes_use_raw_compat_evidence_and_headers",
    "cors_exposes_deprecation_header",
    "frontend_shared_consumer_proven",
    "header_mode_test_coverage",
    "off_mode_test_coverage",
    "no_production_reassignment_of_mode",
    "readiness_doc_agrees_keep_audit_mode",
    "deprecation_map_agrees_map_only",
}

REQUIRED_UNBLOCKING_SIGNALS = {
    "operational_telemetry_ready",
    "per_environment_header_mode_observability",
    "planned_header_toggle_window_and_rollback",
    "metrics_on_deprecation_signal_volume",
    "staff_notification_impact_assessed",
    "external_consumer_impact_audited",
    "proposal_confirm_parity_asserted_for_affected_routes",
    "sprint_engine_review_artifact_documented",
}

REQUIRED_UNBLOCK_REVIEWS = {
    "explicit_sprint_engine_pause_and_review",
    "per_environment_rollout_plan_with_rollback",
    "observability_metrics_defined_for_header_signal_volume",
    "staff_impact_notification_plan",
    "external_consumer_impact_audit_for_affected_deployments",
    "proposal_confirm_parity_review_for_each_affected_route",
    "audit_evidence_continuity_check_for_header_mode_writes",
    "staged_environment_rollout_not_global_toggle",
}

REQUIRED_ALLOWED_USES = {
    "existing_audit_mode_evidence_tags",
    "existing_header_mode_test_coverage",
    "existing_off_mode_test_coverage",
    "frontend_console_deprecation_consumer_test",
    "readiness_preflight_and_gate_doc_maintenance",
}

REQUIRED_FORBIDDEN_USES = {
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

REQUIRED_PAUSE_TRIGGERS = {
    "decision_changes_from_blocked",
    "any_environment_appears_in_environments_can_default_header",
    "required_before_unblocking_changes",
    "forbidden_current_uses_changes",
}


def load_rollout_gate(path: Path = DEFAULT_GATE_PATH) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Raw compat header rollout gate file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def assert_rollout_gate_blocked(gate: dict[str, Any]) -> None:
    assert gate.get("schema_version") == GATE_SCHEMA_VERSION
    assert gate.get("decision") == "blocked"
    assert gate.get("reviewer") == ""
    assert gate.get("reviewed_on") == ""

    rollout_surface = gate.get("rollout_surface")
    assert isinstance(rollout_surface, dict)
    assert set(rollout_surface.get("routes", [])) == REQUIRED_ROUTES
    assert rollout_surface.get("backend_site") == (
        "app.routers.appointments._raw_compat_evidence_and_headers()"
    )
    assert rollout_surface.get("environments_can_default_header") == []
    assert rollout_surface.get("known_frontend_consumers") == [
        "docs/diary/diary.js apiFetch console.warn"
    ]
    assert rollout_surface.get("user_facing_ui_consumers") == []

    signals = gate.get("observability_and_audit_signals")
    assert isinstance(signals, dict)
    proven = signals.get("already_proven_before_header_default")
    blocked = signals.get("required_before_unblocking_any_environment")
    assert isinstance(proven, dict)
    assert set(proven) == REQUIRED_PROVEN_SIGNALS
    assert all(value is True for value in proven.values())
    assert isinstance(blocked, dict)
    assert set(blocked) == REQUIRED_UNBLOCKING_SIGNALS
    assert all(value is False for value in blocked.values())

    assert set(gate.get("required_before_unblocking", [])) == REQUIRED_UNBLOCK_REVIEWS
    assert set(gate.get("allowed_current_uses", [])) == REQUIRED_ALLOWED_USES
    assert set(gate.get("forbidden_current_uses", [])) == REQUIRED_FORBIDDEN_USES
    assert set(gate.get("sprint_engine_pause_required_if", [])) == REQUIRED_PAUSE_TRIGGERS


def build_rollout_gate_status(path: Path = DEFAULT_GATE_PATH) -> dict[str, Any]:
    gate = load_rollout_gate(path)
    assert_rollout_gate_blocked(gate)
    rollout_surface = gate["rollout_surface"]
    signals = gate["observability_and_audit_signals"]
    blocked_signals = signals["required_before_unblocking_any_environment"]
    observability_ready = any(value is True for value in blocked_signals.values())
    rollout_ready = bool(rollout_surface["environments_can_default_header"])
    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "gate_schema_version": gate["schema_version"],
        "decision": gate["decision"],
        "environment_count": len(rollout_surface["environments_can_default_header"]),
        "required_review_count": len(gate["required_before_unblocking"]),
        "allowed_current_uses_count": len(gate["allowed_current_uses"]),
        "forbidden_use_count": len(gate["forbidden_current_uses"]),
        "pause_trigger_count": len(gate["sprint_engine_pause_required_if"]),
        "observability_ready": observability_ready,
        "rollout_ready": rollout_ready,
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the raw compatibility header rollout gate."
    )
    parser.add_argument(
        "--gate",
        type=Path,
        default=DEFAULT_GATE_PATH,
        help="Path to the raw compatibility header rollout gate JSON file.",
    )
    args = parser.parse_args()
    print(json.dumps(build_rollout_gate_status(args.gate), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
