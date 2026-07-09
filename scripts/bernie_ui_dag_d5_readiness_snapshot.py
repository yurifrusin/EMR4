"""Safe aggregate readiness snapshot for Bernie UI DAG D5 delivery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_SCHEMA_VERSION = "bernie.ui_dag.d5_readiness_snapshot.v1"
DEFAULT_GATE_PATH = (
    REPO_ROOT / "docs" / "bernie-ui-derived-state-dag-d5-response-delivery-gate.json"
)
DEFAULT_APPROVAL_DRAFT_PATH = (
    REPO_ROOT / "docs" / "bernie-ui-derived-state-dag-d5-approval-decision-draft.json"
)
DEFAULT_TEST_PLAN_PATH = (
    REPO_ROOT / "docs" / "bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.json"
)
DEFAULT_BLOCKED_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "bernie_ui_dag_d5"
    / "blocked_readiness_snapshot.json"
)

GATE_FALSE_FIELDS = (
    "backend_response_delivery_approved",
    "rest_or_fastapi_route_change_approved",
    "graphql_delivery_approved",
    "provider_or_live_provider_wiring_approved",
    "memory_or_rag_wiring_approved",
    "h15_or_h_series_runtime_input_approved",
    "appointment_write_behavior_change_approved",
    "model_to_database_write_approved",
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Required D5 readiness artifact does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_expected_values(values: list[str]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Expected readiness value must be key=value: {value}")
        key, raw = value.split("=", 1)
        if raw == "true":
            parsed[key] = True
        elif raw == "false":
            parsed[key] = False
        else:
            parsed[key] = raw
    return parsed


def build_d5_readiness_snapshot(
    gate_path: Path = DEFAULT_GATE_PATH,
    approval_draft_path: Path = DEFAULT_APPROVAL_DRAFT_PATH,
    test_plan_path: Path = DEFAULT_TEST_PLAN_PATH,
) -> dict[str, object]:
    gate = _load_json(gate_path)
    approval_draft = _load_json(approval_draft_path)
    test_plan = _load_json(test_plan_path)

    gate_expected = _parse_expected_values(gate["expected_pre_d5_values"])
    plan_expected = _parse_expected_values(test_plan["expected_preflight_values"])
    if gate_expected != plan_expected:
        raise ValueError("D5 gate and backend delivery test plan readiness values differ")

    approval_scope = approval_draft["approval_scope"]
    closed_gate_scope_count = sum(gate[field] is False for field in GATE_FALSE_FIELDS)
    approval_scope_true_count = sum(value is True for value in approval_scope.values())

    snapshot = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "source": "committed_bernie_ui_dag_d5_artifacts",
        "d5_gate_decision": gate["decision"],
        "approval_decision": approval_draft["decision"],
        "test_plan_status": test_plan["status"],
        "ui_consumer_ready": gate["ui_consumer_first_slice_integrated"],
        "route_intercepted_ui_evidence_only": gate["route_intercepted_ui_evidence_only"],
        "backend_response_delivery_ready": True,
        "backend_response_delivery_approved": gate["backend_response_delivery_approved"],
        "implementation_authorized": test_plan["implementation_authorized"],
        "approval_scope_true_count": approval_scope_true_count,
        "approval_scope_count": len(approval_scope),
        "closed_gate_scope_count": closed_gate_scope_count,
        "preflight_command_count": len(test_plan["preflight_commands"]),
        "preflight_expected_value_count": len(gate_expected),
        "required_future_test_count": len(test_plan["required_test_ids"]),
        "test_group_count": len(test_plan["test_groups"]),
        "forbidden_future_scope_count": len(
            approval_draft["forbidden_even_if_future_first_slice_is_approved"]
        ),
        "forbidden_test_expansion_count": len(
            test_plan["forbidden_test_plan_expansions_without_separate_review"]
        ),
        "stop_condition_count": len(test_plan["stop_conditions"]),
        "pause_trigger_count": len(gate["pause_triggers"])
        + len(approval_draft["pause_triggers"]),
        "runtime_or_provider_wiring_ready": gate_expected[
            "runtime_or_provider_wiring_ready"
        ],
        "raw_trove_access_ready": gate_expected["raw_trove_access_ready"],
        "runtime_gate_decision": gate_expected["runtime_gate_decision"],
        "default_provider": gate_expected["default_provider"],
        "live_provider_enabled": gate_expected["live_provider_enabled"],
        "provider_calls_performed": gate_expected["provider_calls_performed"],
        "write_authority_ready": False,
        "external_patient_client_ready": False,
        "readiness_label": "d5_first_slice_ready_provider_write_gates_closed",
        "next_required_decision": "separate_review_for_any_scope_expansion",
    }
    assert_d5_readiness_snapshot_safety(snapshot)
    return snapshot


def assert_d5_readiness_snapshot_safety(snapshot: dict[str, object]) -> None:
    assert snapshot["schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert snapshot["source"] == "committed_bernie_ui_dag_d5_artifacts"
    assert snapshot["d5_gate_decision"] == "approved_for_backend_response_delivery_first_slice"
    assert snapshot["approval_decision"] == "approved_for_backend_response_delivery_first_slice"
    assert snapshot["test_plan_status"] == "approved_first_slice_test_plan"
    assert snapshot["ui_consumer_ready"] is True
    assert snapshot["route_intercepted_ui_evidence_only"] is False
    assert snapshot["backend_response_delivery_ready"] is True
    assert snapshot["backend_response_delivery_approved"] is True
    assert snapshot["implementation_authorized"] is True
    assert snapshot["approval_scope_true_count"] == 5
    assert snapshot["approval_scope_count"] >= 16
    assert snapshot["closed_gate_scope_count"] == len(GATE_FALSE_FIELDS) - 2
    assert snapshot["preflight_command_count"] == 2
    assert snapshot["preflight_expected_value_count"] == 6
    assert snapshot["required_future_test_count"] >= 18
    assert snapshot["test_group_count"] >= 5
    assert snapshot["forbidden_future_scope_count"] >= 10
    assert snapshot["forbidden_test_expansion_count"] >= 10
    assert snapshot["stop_condition_count"] >= 6
    assert snapshot["pause_trigger_count"] >= 18
    assert snapshot["runtime_or_provider_wiring_ready"] is False
    assert snapshot["raw_trove_access_ready"] is False
    assert snapshot["runtime_gate_decision"] == "blocked"
    assert snapshot["default_provider"] == "disabled"
    assert snapshot["live_provider_enabled"] is False
    assert snapshot["provider_calls_performed"] is False
    assert snapshot["write_authority_ready"] is False
    assert snapshot["external_patient_client_ready"] is False
    assert snapshot["readiness_label"] == "d5_first_slice_ready_provider_write_gates_closed"
    assert snapshot["next_required_decision"] == "separate_review_for_any_scope_expansion"

    serialized = json.dumps(snapshot, sort_keys=True).casefold()
    forbidden_fragments = [
        "/api/",
        "supervised-booking",
        "confirm_payload",
        "appointment_id",
        "patient_id",
        "practitioner_id",
        "local_data",
        "raw diary",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in serialized


def load_blocked_d5_readiness_snapshot(
    snapshot_path: Path = DEFAULT_BLOCKED_SNAPSHOT_PATH,
) -> dict[str, object]:
    return _load_json(snapshot_path)


def assert_matches_blocked_d5_readiness_snapshot(
    snapshot: dict[str, object],
    snapshot_path: Path = DEFAULT_BLOCKED_SNAPSHOT_PATH,
) -> None:
    assert snapshot == load_blocked_d5_readiness_snapshot(snapshot_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate Bernie UI DAG D5 readiness snapshot."
    )
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE_PATH)
    parser.add_argument(
        "--approval-draft", type=Path, default=DEFAULT_APPROVAL_DRAFT_PATH
    )
    parser.add_argument("--test-plan", type=Path, default=DEFAULT_TEST_PLAN_PATH)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_BLOCKED_SNAPSHOT_PATH)
    args = parser.parse_args()

    snapshot = build_d5_readiness_snapshot(
        args.gate,
        args.approval_draft,
        args.test_plan,
    )
    assert_matches_blocked_d5_readiness_snapshot(snapshot, args.snapshot)
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
