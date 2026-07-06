import pytest

from scripts.bernie_provider_boundary_readiness_report import (
    REPORT_SCHEMA_VERSION,
    assert_provider_boundary_report_safety,
    build_provider_boundary_report,
)


def test_provider_boundary_report_is_safe_aggregate_status():
    report = build_provider_boundary_report()

    assert report == {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": "static_provider_boundary",
        "provider_metadata_count": 3,
        "declared_provider_count": 3,
        "live_alias_count": 4,
        "live_provider_count": 1,
        "non_live_provider_count": 2,
        "canonical_live_provider_count": 1,
        "provider_metadata_unique": True,
        "all_metadata_providers_schema_declared": True,
        "non_live_providers_outside_live_allowlist": True,
        "live_providers_inside_live_allowlist": True,
        "live_aliases_resolve_to_canonical_provider": True,
        "default_provider": "disabled",
        "runtime_or_provider_wiring_ready": False,
        "live_provider_enabled": False,
        "provider_calls_performed": False,
        "route_behavior_changed": False,
        "database_access_performed": False,
        "memory_or_rag_access_performed": False,
        "historical_diary_material_access_performed": False,
    }
    assert_provider_boundary_report_safety(report)


@pytest.mark.parametrize(
    ("field", "unsafe_value"),
    [
        ("runtime_or_provider_wiring_ready", True),
        ("live_provider_enabled", True),
        ("provider_calls_performed", True),
        ("route_behavior_changed", True),
        ("database_access_performed", True),
        ("memory_or_rag_access_performed", True),
        ("historical_diary_material_access_performed", True),
    ],
)
def test_provider_boundary_report_rejects_opened_runtime_posture(
    field,
    unsafe_value,
):
    report = build_provider_boundary_report()
    report[field] = unsafe_value

    with pytest.raises(AssertionError):
        assert_provider_boundary_report_safety(report)


def test_provider_boundary_report_rejects_alias_or_metadata_drift():
    report = build_provider_boundary_report()
    report["live_aliases_resolve_to_canonical_provider"] = False

    with pytest.raises(AssertionError):
        assert_provider_boundary_report_safety(report)


def test_provider_boundary_report_rejects_non_aggregate_source():
    report = build_provider_boundary_report()
    report["source"] = "runtime_provider_probe"

    with pytest.raises(AssertionError):
        assert_provider_boundary_report_safety(report)
