"""Sol recovery regressions for the LC4R4 evidence report."""

from scripts.bernie_lc4r4_report import build_report


def test_full_partition_effects_are_distinct_from_aligned_target() -> None:
    report = build_report()
    effects = report["full_partition_entity_effects"]

    assert effects["aligned_target_records"] == 83
    assert effects["matching_someone_surfaces"] == 126
    assert effects["matching_additive_resolution_surfaces"] == 16
    assert effects["matching_someone_surface_hash"] == "b4a228c2c4339b53"
    assert effects["matching_additive_resolution_surface_hash"] == "1d1cc5fd9eba83ff"


def test_safety_uses_one_repeat_scenario_denominator() -> None:
    report = build_report()

    assert report["safety"] == {
        "all_safe": True,
        "passed": 1152,
        "total": 1152,
    }
    assert report["repeat_variance"]["sample_count"] == 2304
