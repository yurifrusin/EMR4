import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_JSON = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.json"
PLAN_MD = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.md"
APPROVAL_DRAFT_JSON = (
    ROOT / "docs" / "bernie-ui-derived-state-dag-d5-approval-decision-draft.json"
)


def _load_json_no_duplicate_keys(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")

    def reject_duplicates(pairs):
        counts = Counter(key for key, _ in pairs)
        duplicates = sorted(key for key, count in counts.items() if count > 1)
        assert not duplicates, f"duplicate keys in {path}: {duplicates}"
        return dict(pairs)

    return json.loads(raw, object_pairs_hook=reject_duplicates)


def test_backend_delivery_test_plan_is_blocked_and_requires_approval():
    plan = _load_json_no_duplicate_keys(PLAN_JSON)
    draft = _load_json_no_duplicate_keys(APPROVAL_DRAFT_JSON)

    assert plan["schema_version"] == "bernie.ui_dag.d5_backend_delivery_test_plan.v1"
    assert plan["status"] == "blocked_test_plan_only"
    assert plan["implementation_authorized"] is False
    assert plan["approval_required"] == draft["proposed_decision_if_approved"]
    assert draft["decision"] == "blocked"
    assert draft["approval_scope"]["backend_response_delivery_first_slice_approved"] is False


def test_backend_delivery_test_plan_names_single_candidate_attachment_point():
    plan = _load_json_no_duplicate_keys(PLAN_JSON)

    assert plan["candidate_attachment_point"] == "one_reviewed_bernie_response_assembly_point"
    assert plan["candidate_route"] == (
        "POST /api/v1/appointments/proposals/bernie/supervised-booking"
    )
    assert plan["candidate_response_location"] == "staff_review.bernie.ui_view_model"
    assert plan["evidence_label_after_implementation"] == (
        "backend_response_delivery_synthetic_or_fake_provider"
    )


def test_backend_delivery_test_plan_preserves_preflight_values():
    plan = _load_json_no_duplicate_keys(PLAN_JSON)

    assert plan["preflight_commands"] == [
        ".venv\\Scripts\\python.exe scripts\\bernie_interpretation_readiness_check.py",
        ".venv\\Scripts\\python.exe scripts\\bernie_provider_boundary_readiness_report.py",
    ]
    assert set(plan["expected_preflight_values"]) >= {
        "runtime_or_provider_wiring_ready=false",
        "raw_trove_access_ready=false",
        "runtime_gate_decision=blocked",
        "default_provider=disabled",
        "live_provider_enabled=false",
        "provider_calls_performed=false",
    }


def test_backend_delivery_test_plan_has_required_test_matrix():
    plan = _load_json_no_duplicate_keys(PLAN_JSON)
    required = set(plan["required_test_ids"])

    assert len(required) == len(plan["required_test_ids"])
    assert {
        "test_d5_gate_approved_before_route_delivery",
        "test_supervised_booking_response_includes_ui_view_model_when_server_session_snapshot_exists",
        "test_supervised_booking_response_omits_ui_view_model_without_server_session_snapshot",
        "test_server_delivery_defaults_client_confirmation_request_state_idle",
        "test_backend_confirmed_snapshot_is_only_success_source",
        "test_pressed_awaiting_stale_failed_states_hide_confirm_and_success",
        "test_confirm_payload_serialization_excludes_ui_view_model_fields",
        "test_confirm_payload_still_uses_signed_confirm_endpoint_and_freshness_ids",
        "test_supervised_booking_still_writes_zero_appointments_and_audit_rows_without_confirm",
        "test_non_bernie_routers_do_not_import_ui_view_model_selector",
        "test_provider_memory_graphql_h15_and_trove_import_isolation",
        "test_route_response_evidence_label_is_not_live_provider",
    } <= required

    grouped = {
        test_id
        for group in plan["test_groups"]
        for test_id in group["required_test_ids"]
    }
    assert grouped == required


def test_backend_delivery_test_plan_keeps_expanded_scopes_forbidden():
    plan = _load_json_no_duplicate_keys(PLAN_JSON)

    forbidden = set(plan["forbidden_test_plan_expansions_without_separate_review"])
    assert "graphql_resolver_delivery_tests" in forbidden
    assert "provider_prompt_or_live_provider_tests" in forbidden
    assert "memory_rag_or_graphrag_runtime_tests" in forbidden
    assert "h15_or_h_series_runtime_input_tests" in forbidden
    assert "historical_diary_material_runtime_input_tests" in forbidden
    assert "appointment_write_behavior_change_tests" in forbidden
    assert "external_patient_client_tests" in forbidden

    stop_conditions = set(plan["stop_conditions"])
    assert "test_requires_provider_calls" in stop_conditions
    assert "test_requires_confirm_payload_or_write_behavior_changes" in stop_conditions
    assert "test_requires_broad_router_refactor" in stop_conditions


def test_backend_delivery_test_plan_markdown_is_plan_only():
    text = PLAN_MD.read_text(encoding="utf-8")

    assert "Status: blocked test plan only" in text
    assert "does not authorize implementation" in text
    assert "`approved_for_backend_response_delivery_first_slice`" in text
    assert "`decision: blocked`" in text
    assert "single reviewed Bernie response assembly point" in text
    assert "optional `staff_review.bernie.ui_view_model`" in text
    assert "zero appointment/audit writes" in text
    assert "evidence labeling that remains non-live-provider" in text
