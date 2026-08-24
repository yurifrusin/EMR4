from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_read_only_historical_derived_check_in_context_adapter_test_utility_gap_review
    as review,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict:
    return json.loads((ROOT / review.CONTRACT_PATH).read_text(encoding="utf-8"))


def test_exact_contract_and_source_reading_pass_without_release() -> None:
    evidence = review.run_review(ROOT, release=False)

    assert evidence["decision"] == "accepted_read_only_utility_gap_review"
    assert evidence["coverage"]["historical_derived_incremental_branch_count"] == 0
    assert evidence["coverage"]["new_business_rule_count"] == 0
    assert evidence["source_reading"]["direct_structural_selector_keys"] == [
        "relative_minute_span"
    ]
    assert evidence["successor_axis_family_count"] == 3
    assert evidence["hostile_contract_mutations_rejected"] >= 60


def test_structural_axes_have_one_closed_utility_label_each() -> None:
    evidence = review.run_review(ROOT, release=False)
    reading = {item["id"]: item["utility"] for item in evidence["structural_influence"]}

    assert reading == {
        "event_count": "digest_only_provenance",
        "distinct_relative_minutes": "digest_only_provenance",
        "relative_minute_span": "synthetic_time_parameter_only",
        "distinct_event_kinds": "digest_only_provenance",
        "synthetic_subject_slots": "digest_only_provenance",
        "resource_slots": "digest_only_provenance",
    }
    assert "independent_behavior_selector" not in reading.values()


def test_occupied_branch_is_already_covered_not_incremental() -> None:
    evidence = review.run_review(ROOT, release=False)
    branch = evidence["coverage"]["occupied_branch"]

    assert branch == review.OCCUPIED_BRANCH
    assert branch["expected_coverage"] == "already_covered_product_contract"
    assert evidence["source_reading"]["existing_adapter_success_matrix_cases"] == 6
    assert evidence["source_reading"]["existing_hostile_contract_mutations"] >= 60


def test_successor_is_three_time_ordered_authored_synthetic_axis_families() -> None:
    successor = review.build_successor(_contract())

    assert successor["status"] == "frozen_authored_synthetic_axes_no_execution_authority"
    assert len(successor["axis_families"]) == 3
    assert successor["composition_rule"]["full_cross_product_required"] is False
    assert successor["authority"] == {
        "authored_synthetic_only": True,
        "historical_fixture_control_archive_or_local_data_access": False,
        "product_adapter_route_database_client_runtime_or_configuration_change": False,
        "provider_model_network_or_external_release": False,
        "ordinary_practice_activation": False,
        "execution_authorized_by_this_contract": False,
    }


def test_local_data_path_is_rejected_before_filesystem_read() -> None:
    with pytest.raises(review.ReviewError, match="path not allowlisted"):
        review.canonical_text(ROOT, "local_data/historical-diary-trove/anything.json")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("planning_source", review.PLANNING_SOURCE[:7]),
        ("utility_labels", ["free_form"]),
        ("coverage_labels", ["free_form"]),
        ("occupied_branch", {}),
        ("closed_boundaries", []),
    ],
)
def test_contract_drift_fails_closed(field: str, value: object) -> None:
    contract = _contract()
    contract[field] = value

    with pytest.raises(review.ReviewError):
        review.validate_contract(contract, ROOT, check_git=False)


def test_abbreviated_and_plausible_full_git_ids_fail_closed() -> None:
    for value in (review.PLANNING_SOURCE[:7], "0" * 40):
        contract = _contract()
        contract["accepted_git_objects"]["occupied_candidate"] = value
        with pytest.raises(review.ReviewError):
            review.validate_contract(contract, ROOT, check_git=False)


def test_digest_only_axis_cannot_be_promoted_to_behavior_selector() -> None:
    contract = _contract()
    contract["structural_axes"][0]["expected_utility"] = (
        "independent_behavior_selector"
    )

    with pytest.raises(review.ReviewError, match="structural axes changed"):
        review.validate_contract(contract, ROOT, check_git=False)


def test_release_outputs_are_exact_and_contain_no_local_material(tmp_path: Path) -> None:
    evidence = review.run_review(ROOT, release=False)
    report = review.render_report(evidence)
    successor = review.build_successor(_contract())
    serialized = json.dumps({"evidence": evidence, "successor": successor}) + report

    assert "local_data/historical-diary-trove" not in serialized
    assert '"synthetic_subject_slot":' not in serialized
    assert '"resource_slot":' not in serialized
    assert "accepted_read_only_utility_gap_review" in report
    assert "zero incremental adapter branches" in report
    assert tmp_path.exists()
