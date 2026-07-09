import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-consumer-switch-approval-packet.json"
PACKET_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-consumer-switch-approval-packet.md"
TASKPANE_JS = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"
SNAPSHOT = ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"


def _packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_consumer_switch_packet_is_pending_approval_not_runtime_authority():
    payload = _packet()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_consumer_switch_approval_packet.v1"
    )
    assert payload["sprint"] == 277
    assert payload["decision"] == "pending_yuri_switch_approval"
    assert payload["approval_required_before_code"] is True
    assert payload["current_release_boundary_expires_on"] == "2026-08-06"
    assert payload["proposed_switch_approval_expires_on"] == "2026-08-06"
    assert payload["authorized_now"] == {
        "office_addin_taskpane_runtime_implementation": False,
        "office_addin_live_graphql_traffic": False,
        "taskpane_js_edits_for_graphql": False,
        "feature_gate_added": False,
    }


def test_consumer_switch_packet_names_exact_future_approval_surface():
    payload = _packet()

    assert payload["if_yuri_approves_later"] == {
        "may_edit_taskpane_js_for_one_consumer": True,
        "may_add_default_off_graphql_fetch_wrapper": True,
        "may_add_internal_staff_selector_graphql_path": True,
        "may_send_graphql_traffic_only_when_gate_enabled": True,
        "may_change_backend_routes_or_schema": False,
        "may_add_server_config_endpoint": False,
        "may_add_telemetry_endpoint": False,
        "may_change_readiness_flags": False,
        "may_claim_deployment_or_production_readiness": False,
    }
    assert payload["switch_scope"]["consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["switch_scope"]["audience"] == "authenticated_internal_staff_only"
    assert payload["switch_scope"]["practice_scoped"] is True
    assert payload["switch_scope"]["external_or_patient_client"] is False
    assert payload["switch_scope"]["mutations_allowed"] is False
    assert payload["switch_scope"]["subscriptions_allowed"] is False
    assert payload["switch_scope"]["other_graphql_roots_allowed"] is False


def test_consumer_switch_packet_feature_gate_is_default_off_and_not_user_controlled():
    gate = _packet()["feature_gate"]

    assert gate == {
        "mechanism": "source_controlled_build_time_constant_or_equivalent_static_taskpane_config",
        "default": False,
        "runtime_user_override_allowed": False,
        "local_storage_allowed": False,
        "query_parameter_allowed": False,
        "office_settings_persistence_allowed": False,
        "server_side_config_endpoint_allowed_without_separate_approval": False,
        "expired_or_disabled_gate_behavior": "zero_graphql_fetches_render_from_rest",
    }


def test_consumer_switch_packet_preserves_projection_and_error_contract():
    payload = _packet()
    errors = payload["required_error_and_fallback_contract"]

    assert payload["approved_projection"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation.id",
        "defaultLocation.name",
    ]
    assert payload["projection_drift_behavior"] == "discard_unapproved_fields_before_binding"
    assert errors["http_401"] == "logout_and_do_not_retry_graphql"
    assert errors["http_non_401_or_network_timeout"] == "fall_back_to_rest_and_show_system_retry_copy"
    assert errors["graphql_forbidden"] == "no_logout_access_denied_copy_and_fallback_to_rest"
    assert errors["graphql_bad_user_input"] == "no_logout_invalid_request_copy_and_fallback_to_rest"
    assert errors["practice_null"] == "distinct_no_access_empty_state_not_same_as_empty_filter"
    assert errors["empty_practitioners"] == "ordinary_empty_directory_or_filter_state"
    assert errors["malformed_required_row_field"] == "drop_malformed_row_and_continue_if_any_valid_rows_remain"


def test_consumer_switch_packet_fallback_is_one_shot_without_telemetry():
    fallback = _packet()["fallback_contract"]

    assert fallback == {
        "on_graphql_transport_failure": "attempt_rest_immediately_once",
        "on_graphql_response_body_error": "render_user_safe_message_and_attempt_rest_immediately_once",
        "on_rest_fallback_failure": "show_existing_rest_failure_state",
        "backoff_or_retry_loop": False,
        "telemetry": "none_before_separate_approval",
    }


def test_consumer_switch_packet_keeps_global_readiness_snapshot_blocked():
    payload = _packet()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert all(value is False for value in payload["must_remain_false"].values())
    for key in (
        "graphql_resolver_ready",
        "external_read_model_runtime_ready",
        "runtime_or_memory_ready",
        "write_authority_ready",
        "provider_or_directory_runtime_ready",
    ):
        assert snapshot[key] is False


def test_consumer_switch_packet_records_distinct_worker_reviews_and_approval_template():
    payload = _packet()

    assert payload["worker_reviews"]["antigravity_consumer_ux_release"]["verdict"] == "PASS"
    assert payload["worker_reviews"]["deepseek_static_release"]["verdict"] == "PASS"
    assert payload["worker_reviews"]["claude"]["used"] is False
    assert payload["yuri_approval_payload_template"]["decision"] == (
        "approved_for_default_off_office_addin_graphql_practitioner_selector_switch"
    )
    assert payload["yuri_approval_payload_template"]["approval_expires_on"] == "2026-08-06"
    assert payload["next_recommended_work"].startswith("Stop for Yuri approval")


def test_consumer_switch_packet_markdown_and_taskpane_runtime_remain_unwired():
    text = " ".join(PACKET_MD.read_text(encoding="utf-8").split())
    taskpane = TASKPANE_JS.read_text(encoding="utf-8", errors="replace").lower()

    assert "Decision: `pending_yuri_switch_approval`" in text
    assert "source-controlled build-time constant" in text
    assert "Yuri must explicitly approve" in text
    assert "/api/v1/graphql" not in taskpane
    assert "query getpractitioners" not in taskpane
    assert "practitioners(activeonly" not in taskpane
