from scripts.raisa_provider_free_compatibility_conformance_harness_readiness_repair import (
    BASELINE,
    OWNED_TESTS,
    build_evidence,
)


def test_structural_repair_is_exactly_test_only() -> None:
    evidence = build_evidence()

    assert evidence["baseline_head"] == BASELINE
    assert evidence["application_tree_unchanged"] is True
    assert evidence["owned_test_files"] == list(OWNED_TESTS)
    assert evidence["changed_test_file_count"] == 8
    assert evidence["status_assertions_unchanged"] is True
    assert evidence["runtime_or_command_authority_granted"] is False
    assert evidence["status"] == "structural_repair_pass"


def test_repair_counts_match_the_frozen_failure_census() -> None:
    evidence = build_evidence()

    assert evidence["same_day_clock_fixture_count"] == 2
    assert evidence["future_weekday_fixture_count"] == 4
    assert evidence["proposal_header_source_sites"] == 3
    assert evidence["proposal_header_exercised_cases"] == 12
    assert evidence["pre_repair_test_result"] == {"passed": 266, "failed": 45}
    assert evidence["frozen_failure_classification"] == {
        "past_or_elapsed_time_fixture": 33,
        "missing_required_proposal_idempotency_header": 12,
    }
