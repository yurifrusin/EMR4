"""Sol recovery checks for the LC4R3 development-only evidence report."""

from __future__ import annotations

from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from scripts.bernie_lc4r3_report import (
    _compute_report,
    _get_variant_group,
    _get_variant_suffix,
    _is_deferred_bare_arrival,
    _is_deferred_checkin,
    _is_target_cancel,
    _is_target_create,
    _is_target_explain,
    _is_target_status,
)


def _variants():
    return [
        variant
        for group in DevelopmentOnlyLoader().load_all().groups
        for variant in group.all_variants
    ]


def _groups(variants, predicate, suffix: str | None = None) -> set[int]:
    return {
        _get_variant_group(variant.scenario_id)
        for variant in variants
        if predicate(variant)
        and (suffix is None or _get_variant_suffix(variant.scenario_id) == suffix)
    }


def test_frozen_selection_is_the_original_aligned_subset_not_equal_size_substitution():
    variants = _variants()

    assert sum(map(_is_target_create, variants)) == 16
    assert _groups(variants, _is_target_cancel) == {
        49, 50, 51, 52, 53, 54, 55, 56, 57, 61, 62, 63, 64
    }
    assert sum(map(_is_target_explain, variants)) == 80
    assert _groups(variants, _is_target_status, "03") == set(range(65, 81))
    assert _groups(variants, _is_target_status, "06") == {
        65, 66, 67, 68, 69, 70, 71, 72, 73, 77, 78, 79, 80
    }
    assert _groups(variants, _is_target_status, "07") == set(range(65, 81))
    assert _groups(variants, _is_deferred_checkin) == {
        65, 66, 67, 68, 69, 70, 71, 72, 73, 77, 78, 79, 80
    }
    assert _groups(variants, _is_deferred_bare_arrival) == {
        65, 66, 67, 69, 70, 71, 72, 73, 75, 76, 77, 78, 79
    }


def test_report_measures_per_scenario_variance_and_discloses_metadata_incident():
    report = _compute_report()

    assert report["target_family_totals"] == {
        "total": 154,
        "passed": 154,
        "all_passed": True,
    }
    assert report["repeat_variance"] == {
        "measured": 0,
        "all_deltas_zero": True,
        "sample_count": 2304,
        "method": "per-scenario observation and safety fingerprint",
    }
    assert report["protected_evidence"] == {
        "content_opened_or_read": False,
        "evaluated_or_tuned_against": False,
        "metadata_enumeration_incident": True,
        "incident_scope": (
            "Sol orientation command enumerated protected fixture path names; "
            "no semantic content or labels were exposed"
        ),
    }
    for assertion, value in report["assertions"].items():
        if assertion != "intended_action_computed":
            assert value is True, assertion
    assert report["assertions"]["intended_action_computed"] == 880
