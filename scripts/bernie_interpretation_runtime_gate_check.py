"""Validate the Bernie interpretation harness runtime/provider gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GATE_SCHEMA_VERSION = "bernie.interpretation_harness_runtime_gate.v1"
DEFAULT_GATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "bernie-interpretation-harness-runtime-gate.json"
)

REQUIRED_BLOCKED_SCOPE = {
    "interpretation_harness_runtime_wiring",
    "provider_dry_run_wiring",
    "route_integration",
    "database_access",
    "memory_or_rag_access",
    "historical_diary_material_access",
}

REQUIRED_UNBLOCK_REVIEWS = {
    "explicit_yuri_approval",
    "bounded_no_write_runtime_plan",
    "provider_privacy_and_cost_review",
    "route_authority_review",
    "staff_confirmation_affordance_review",
    "audit_and_observability_plan",
    "rollback_or_kill_switch_plan",
    "focused_tests_and_manual_review_plan",
}

REQUIRED_ALLOWED_USES = {
    "provider_free_fixture_tests",
    "safe_aggregate_report",
    "contract_validation",
    "bounded_review_artifacts",
}

REQUIRED_FORBIDDEN_USES = {
    "runtime_route_calls",
    "live_or_fake_provider_prompt_wiring",
    "database_reads_or_writes",
    "appointment_or_audit_mutations",
    "patient_matching",
    "raw_trove_processing",
    "h15_or_h_series_runtime_imports",
    "rag_or_graphrag_memory",
}

REQUIRED_PAUSE_TRIGGERS = {
    "decision_changes_from_blocked",
    "any_scope_value_changes_to_true",
    "required_before_unblocking_changes",
    "forbidden_current_uses_changes",
}


def load_runtime_gate(path: Path = DEFAULT_GATE_PATH) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Runtime gate file does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def assert_runtime_gate_blocked(gate: dict[str, Any]) -> None:
    """Assert the runtime/provider gate remains blocked and review-gated."""

    assert gate.get("schema_version") == GATE_SCHEMA_VERSION
    assert gate.get("decision") == "blocked"
    assert gate.get("reviewer") == ""
    assert gate.get("reviewed_on") == ""

    scope = gate.get("scope")
    assert isinstance(scope, dict)
    assert set(scope) == REQUIRED_BLOCKED_SCOPE
    assert all(value is False for value in scope.values())

    assert set(gate.get("required_before_unblocking", [])) == REQUIRED_UNBLOCK_REVIEWS
    assert set(gate.get("allowed_current_uses", [])) == REQUIRED_ALLOWED_USES
    assert set(gate.get("forbidden_current_uses", [])) == REQUIRED_FORBIDDEN_USES
    assert set(gate.get("sprint_engine_pause_required_if", [])) == REQUIRED_PAUSE_TRIGGERS


def build_runtime_gate_status(path: Path = DEFAULT_GATE_PATH) -> dict[str, Any]:
    gate = load_runtime_gate(path)
    assert_runtime_gate_blocked(gate)
    return {
        "schema_version": "bernie.interpretation_harness_runtime_gate_status.v1",
        "gate_schema_version": gate["schema_version"],
        "decision": gate["decision"],
        "blocked_scope_count": len(gate["scope"]),
        "required_review_count": len(gate["required_before_unblocking"]),
        "forbidden_use_count": len(gate["forbidden_current_uses"]),
        "pause_trigger_count": len(gate["sprint_engine_pause_required_if"]),
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Bernie interpretation harness runtime gate."
    )
    parser.add_argument(
        "--gate",
        type=Path,
        default=DEFAULT_GATE_PATH,
        help="Path to the runtime gate JSON file.",
    )
    args = parser.parse_args()
    status = build_runtime_gate_status(args.gate)
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
