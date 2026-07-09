import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPROVAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-internal-runtime-consumer-approval.json"
)
APPROVAL_MD = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-internal-runtime-consumer-approval.md"
)
REST_ROUTE_APPROVAL = (
    ROOT / "docs" / "api-spine" / "practitioner-directory-rest-route-readiness-approval.json"
)
BLOCKED_READINESS = (
    ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"
)


def _approval() -> dict:
    return json.loads(APPROVAL.read_text(encoding="utf-8"))


def test_internal_runtime_consumer_approval_shape_is_specific():
    payload = _approval()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_internal_runtime_consumer_approval.v1"
    )
    assert payload["decision"] == "approved_for_single_internal_runtime_consumer"
    assert payload["gate"] == "practitioner_directory_internal_runtime_consumer_gate"
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert payload["reviewer"] == "yuri"
    assert re.fullmatch(r"[0-9a-f]{40}", payload["approved_contract_commit"])
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload["approval_expires_on"])
    assert payload["approval"]["go_no_go_acknowledged"] is True


def test_exactly_one_named_runtime_consumer_is_approved():
    payload = _approval()
    consumers = payload["approved_consumer"]

    assert payload["allows_only_one_runtime_consumer"] is True
    assert payload["authorized_runtime_consumers"] == [
        "office_addin_diary_booking_practitioner_selector"
    ]
    assert len(consumers) == 1
    consumer = consumers[0]
    assert consumer["consumer_id"] == "office_addin_diary_booking_practitioner_selector"
    assert consumer["consumer_surface"] == (
        "Office add-in Command Center SPA Diary booking practitioner selector/list"
    )
    assert consumer["consumption_mode"] == "http_through_existing_route"
    assert consumer["route"] == "GET /api/v1/practice/practitioners"
    assert consumer["default_query"] == {"activeOnly": True}
    assert set(consumer["candidate_files"]) == {"docs/diary/diary.js", "docs/diary/diary.html"}


def test_internal_consumer_scope_reuses_existing_route_auth_and_tenancy():
    scope = _approval()["permitted_scope"]

    assert scope["single_internal_runtime_consumer_allowed"] is True
    assert scope["read_only"] is True
    assert scope["practice_scoped"] is True
    assert scope["authenticated_internal_staff_only"] is True
    assert scope["consumption_mode"] == "http_through_existing_route"
    assert scope["reuse_existing_route_auth_and_tenancy"] is True
    assert scope["client_supplied_practice_scope_allowed"] is False
    assert scope["active_only_false_by_default_allowed"] is False
    assert scope["new_route_or_endpoint_allowed"] is False
    assert scope["direct_database_or_service_bypass_allowed"] is False
    assert scope["public_origin_or_ngrok_header_auth_bypass_allowed"] is False
    assert scope["persist_practitioner_list_outside_active_diary_session_allowed"] is False


def test_readiness_status_boundary_remains_static_only():
    payload = _approval()
    boundary = payload["readiness_status_boundary_unchanged"]

    assert boundary["sprint_261_consumer_boundary_stays_static_only"] is True
    assert boundary["sprint_262_release_check_runtime_consumers_allowed_stays_false"] is True
    assert "route-data runtime consumer" in boundary["reason"]


def test_internal_consumer_does_not_authorize_adjacent_gates():
    payload = _approval()

    assert all(value is False for value in payload["must_remain_false"].values())
    for key in (
        "graphql_resolver_ready",
        "external_read_model_runtime_ready",
        "runtime_or_memory_ready",
        "provider_or_directory_runtime_ready",
        "write_authority_ready",
        "deployment_ready",
        "production_ready",
        "external_patient_client_ready",
        "sdl_changes_allowed",
        "graphql_resolver_allowed",
        "provider_or_memory_trove_allowed",
        "h15_h_series_historical_diary_allowed",
    ):
        assert payload["must_remain_false"][key] is False
        assert payload["permitted_scope"][key] is False


def test_internal_consumer_field_scope_excludes_sensitive_identifiers():
    consumer = _approval()["approved_consumer"][0]

    assert set(consumer["allowed_fields"]) == {"id", "displayName", "defaultLocation"}
    forbidden = set(consumer["must_not_request_fields"])
    assert {
        "provider_number",
        "prescriber_number",
        "ahpra_number",
        "hpi_i",
        "email",
        "phone",
        "address",
    }.issubset(forbidden)


def test_markdown_restates_no_wiring_and_graphql_follow_on_rule():
    text = " ".join(APPROVAL_MD.read_text(encoding="utf-8").split())

    assert "This does not wire the consumer" in text
    assert "route-data consumption only" in text
    assert "readiness-status consumer boundary" in text
    assert "http_through_existing_route" in text
    assert "must not introduce a new route" in text
    assert "must not create public-origin" in text
    assert "must not request, store, or display provider number" in text
    assert "GraphQL is the likely next track only if this REST route proves itself" in text


def test_existing_readiness_artifacts_remain_unchanged_by_internal_consumer_packet():
    route_payload = json.loads(REST_ROUTE_APPROVAL.read_text(encoding="utf-8"))
    blocked = json.loads(BLOCKED_READINESS.read_text(encoding="utf-8"))

    assert route_payload["decision"] == "approved_for_practitioner_directory_rest_route_ready_true"
    assert route_payload["readiness_fixture_change"]["performed_in_this_payload"] is False
    assert blocked["rest_route_ready"] is False
    assert blocked["external_read_model_runtime_ready"] is False
    assert blocked["graphql_resolver_ready"] is False
    assert blocked["write_authority_ready"] is False
