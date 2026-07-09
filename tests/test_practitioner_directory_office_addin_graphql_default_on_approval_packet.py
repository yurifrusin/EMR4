import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-default-on-approval-packet.json"
PACKET_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-default-on-approval-packet.md"
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
SPRINT279 = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-switch-route-intercepted-evidence.json"


def _packet() -> dict:
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_default_on_packet_records_yuri_approval():
    payload = _packet()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_default_on_approval_packet.v1"
    )
    assert payload["sprint"] == 280
    assert payload["decision"] == "approved_for_office_addin_graphql_practitioner_selector_default_on"
    assert payload["approval_required_before_code"] is True
    assert payload["yuri_approval_record"] == {
        "statement": "I approve the default-on packet.",
        "recorded_on": "2026-07-09",
        "approved_scope": "Office add-in diary practitioner selector GraphQL default-on only",
        "approval_expires_on": "2026-08-06",
    }
    assert payload["current_release_boundary_expires_on"] == "2026-08-06"
    assert payload["proposed_default_on_approval_expires_on"] == "2026-08-06"


def test_default_on_packet_authorizes_only_single_runtime_default_flip_now():
    payload = _packet()

    assert payload["authorized_now"] == {
        "change_enable_graphql_practitioners_default_to_true": True,
        "send_office_addin_live_graphql_traffic_by_default": True,
        "remove_rest_fallback": False,
        "add_runtime_user_override": False,
        "add_server_config_endpoint": False,
        "add_telemetry_endpoint": False,
        "claim_deployment_or_production_readiness": False,
    }
    assert all(value is False for value in payload["must_remain_false"].values())


def test_default_on_packet_scope_is_single_consumer_read_only_graphql():
    scope = _packet()["default_on_scope"]

    assert scope["consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert scope["audience"] == "authenticated_internal_staff_only"
    assert scope["practice_scoped"] is True
    assert scope["external_or_patient_client"] is False
    assert scope["graphql_operation"] == "query"
    assert scope["mutations_allowed"] is False
    assert scope["subscriptions_allowed"] is False
    assert scope["other_graphql_roots_allowed"] is False
    assert scope["default_render_source_if_approved"] == "GraphQL"
    assert scope["fallback_render_source"] == "REST"
    assert scope["rest_route_retained"] == "GET /api/v1/practice/practitioners?activeOnly=true&limit=200"


def test_default_on_packet_depends_on_sprint279_evidence_and_runtime_is_now_approved_true():
    payload = _packet()
    evidence = json.loads(SPRINT279.read_text(encoding="utf-8"))
    source = DIARY_JS.read_text(encoding="utf-8", errors="replace")

    assert payload["source_route_intercepted_evidence"].endswith(
        "practitioner-directory-office-addin-graphql-switch-route-intercepted-evidence.json"
    )
    assert evidence["sprint"] == 279
    assert evidence["browser_evidence"]["default_off_observed"]["graphql_requests"] == 0
    assert evidence["browser_evidence"]["enabled_fallback_observed"]["graphql_forbidden_then_rest_fallback"] is True
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" in source
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = false;" not in source


def test_default_on_packet_preserves_projection_and_fallback_contract():
    payload = _packet()

    assert payload["approved_projection"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation.id",
        "defaultLocation.name",
    ]
    behavior = payload["required_runtime_behavior_if_approved"]
    assert behavior["http_401"] == "existing_apiFetch_logout_and_no_rest_fallback_retry_loop"
    assert behavior["http_non_401_or_network_timeout"] == "fall_back_to_rest_once"
    assert behavior["graphql_forbidden"] == "fall_back_to_rest_once_without_logout"
    assert behavior["graphql_bad_user_input"] == "fall_back_to_rest_once_without_logout"
    assert behavior["practice_null"] == "empty_rows_without_rest_fallback"
    assert behavior["default_location_null"] == "preserve_row_with_empty_location_shape"
    assert behavior["unknown_fields"] == "not_bound_by_normalizePractitionerDirectory"


def test_default_on_packet_template_and_markdown_force_stop_point():
    payload = _packet()
    text = " ".join(PACKET_MD.read_text(encoding="utf-8").split())

    assert payload["yuri_approval_payload_template"]["decision"] == (
        "approved_for_office_addin_graphql_practitioner_selector_default_on"
    )
    assert payload["yuri_approval_payload_template"]["approval_expires_on"] == "2026-08-06"
    assert payload["next_recommended_work"].startswith("Stop for Yuri approval")
    assert "Yuri approved that packet on 2026-07-09" in text
    assert "Stop before any expansion beyond this one selector" in text
    assert "REST fallback must remain" in text
