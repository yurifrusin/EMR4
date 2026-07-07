import pytest

from scripts.appointment_route_inventory_preflight import (
    APPOINTMENT_PREFIX,
    REPORT_SCHEMA_VERSION,
    assert_appointment_route_inventory_preflight_safety,
    build_appointment_route_inventory_preflight,
)


def test_appointment_route_inventory_preflight_is_safe_aggregate_status():
    report = build_appointment_route_inventory_preflight()

    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["source"] == "static_fastapi_route_table"
    assert report["appointment_prefix"] == APPOINTMENT_PREFIX
    assert report["route_table_scope"] == "mounted_appointment_apiroutes"
    assert report["contract_scope"] == "diary_action_route_contract_paths"
    assert report["appointment_route_count"] >= 30
    assert report["appointment_distinct_path_count"] >= 25
    assert report["contract_documented_path_count"] >= 15
    assert report["contract_covered_route_count"] >= 15
    assert report["grammar_authority_route_count"] > 0
    assert report["grammar_authority_route_count"] < report["contract_covered_route_count"]
    assert report["raw_adjacent_route_count"] > 0
    assert report["out_of_contract_route_count"] > 0
    assert report["out_of_contract_route_count"] < report["appointment_route_count"]
    assert report["out_of_contract_documented_path_method_count"] >= 0
    assert report["out_of_contract_documented_path_method_count"] <= 5
    assert (
        report["out_of_contract_documented_path_method_count"]
        < report["out_of_contract_undocumented_path_method_count"]
    )
    assert (
        report["out_of_contract_documented_path_method_count"]
        + report["out_of_contract_undocumented_path_method_count"]
        == report["out_of_contract_route_method_count"]
    )
    assert (
        report["out_of_contract_documented_path_count"]
        + report["out_of_contract_undocumented_path_count"]
        == report["out_of_contract_distinct_path_count"]
    )
    assert report["out_of_contract_by_method_family"]["read_get"] > 0
    assert report["out_of_contract_by_method_family"]["query_or_command_post"] > 0
    assert report["out_of_contract_by_category"]["slot_search"] > 0
    assert report["out_of_contract_by_category"]["bernie_session"] > 0
    assert report["out_of_contract_by_category"]["bernie_proposal_support"] > 0
    assert report["out_of_contract_post_route_method_count"] == (
        report["out_of_contract_by_method_family"]["query_or_command_post"]
    )
    assert report["out_of_contract_post_route_method_count"] > 0
    assert (
        sum(report["out_of_contract_post_by_sub_family"].values())
        == report["out_of_contract_post_route_method_count"]
    )
    assert report["out_of_contract_post_by_sub_family"]["proposal_support_post"] > 0
    assert report["out_of_contract_post_by_sub_family"]["state_tracking_post"] > 0
    assert report["out_of_contract_post_rows_are_grammar_dispatch_authority"] is False
    assert report["post_sub_family_classifier"] == "fixed_static_path_patterns"
    assert report["all_contract_paths_mounted"] is True
    assert report["contract_is_complete_router_catalogue"] is False
    assert report["raw_adjacent_routes_are_grammar_dispatch_authority"] is False
    assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_has_closed_runtime_posture():
    report = build_appointment_route_inventory_preflight()

    for field in (
        "runtime_or_provider_wiring_ready",
        "provider_calls_performed",
        "http_requests_performed",
        "route_handlers_executed",
        "database_access_performed",
        "memory_or_rag_access_performed",
        "historical_diary_material_access_performed",
        "h15_or_h_series_runtime_imports_performed",
        "graphql_access_performed",
        "writes_performed",
    ):
        assert report[field] is False


@pytest.mark.parametrize(
    "field",
    [
        "runtime_or_provider_wiring_ready",
        "provider_calls_performed",
        "http_requests_performed",
        "route_handlers_executed",
        "database_access_performed",
        "memory_or_rag_access_performed",
        "historical_diary_material_access_performed",
        "h15_or_h_series_runtime_imports_performed",
        "graphql_access_performed",
        "writes_performed",
        "contract_is_complete_router_catalogue",
        "raw_adjacent_routes_are_grammar_dispatch_authority",
        "documented_path_out_of_contract_rows_are_grammar_authority",
        "out_of_contract_post_rows_are_grammar_dispatch_authority",
    ],
)
def test_appointment_route_inventory_preflight_rejects_opened_boundaries(field):
    report = build_appointment_route_inventory_preflight()
    report[field] = True

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_rejects_missing_contract_mounts():
    report = build_appointment_route_inventory_preflight()
    report["all_contract_paths_mounted"] = False

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_rejects_collapsed_coverage_split():
    report = build_appointment_route_inventory_preflight()
    report["grammar_authority_route_count"] = report["contract_covered_route_count"] + 1

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_rejects_uncovered_partition_drift():
    report = build_appointment_route_inventory_preflight()
    report["out_of_contract_undocumented_path_method_count"] += 1

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_rejects_post_count_drift():
    report = build_appointment_route_inventory_preflight()
    report["out_of_contract_post_route_method_count"] += 1

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_rejects_post_sub_family_drift():
    report = build_appointment_route_inventory_preflight()
    report["out_of_contract_post_by_sub_family"]["ambiguous_post"] = 1

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_rejects_unknown_post_sub_family():
    report = build_appointment_route_inventory_preflight()
    report["out_of_contract_post_by_sub_family"]["confirm_post"] = 1

    with pytest.raises(AssertionError):
        assert_appointment_route_inventory_preflight_safety(report)


def test_appointment_route_inventory_preflight_does_not_emit_route_paths():
    report = build_appointment_route_inventory_preflight()
    rendered = repr(report)

    assert "/api/v1/appointments/" not in rendered
    assert "appointment_id" not in rendered
    assert "practitioner_id" not in rendered
    assert "session_id" not in rendered
    assert "slot-search" not in rendered
    assert "events" not in rendered
