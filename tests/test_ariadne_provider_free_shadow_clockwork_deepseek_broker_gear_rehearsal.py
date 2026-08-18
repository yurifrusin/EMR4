from __future__ import annotations

import copy
import inspect
from pathlib import Path

import pytest

from orchestration_harness import shadow_clockwork as clock


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration/continuity/"
    "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
)
CONTRACT = BASE / "contract.json"
GAUGES = BASE / "frozen-failure-gauges.json"


@pytest.fixture(scope="module")
def reading() -> tuple[dict[str, object], dict[str, object], list[dict[str, str]]]:
    return clock.build_generation(ROOT, CONTRACT, GAUGES)


def _accepted_publication_reading(reading):
    _, contract, _ = reading
    latch = clock.load_json(
        ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    latch["checkpoint"]["retry_counters"] = {
        key: 0 for key in latch["checkpoint"]["retry_counters"]
    }
    bindings = clock.verify_source_bindings(ROOT, contract)
    gauges = clock.validate_failure_gauges(clock.load_json(GAUGES))
    generation = clock._derive_generation(ROOT, contract, latch, bindings, gauges)
    gauge_results = clock.exercise_failure_gauges(generation, gauges)
    efficacy = clock.calculate_efficacy(
        contract,
        generation,
        gauge_results,
        line_growth={"total": 1},
        clean_run_overhead_ms=0.0,
    )
    assert efficacy["accepted"] is True
    return generation, contract, gauge_results, efficacy


def test_engine_derives_one_complete_provider_free_tick(reading) -> None:
    generation, contract, gauge_results = reading
    assert [event["kind"] for event in generation["journal"]] == list(clock.EXPECTED_EVENT_KINDS)
    assert [event["writer"] for event in generation["journal"]] == [
        "ariadne",
        "ariadne",
        "deepseek_broker",
        "ariadne",
    ]
    assert generation["terminal_result"]["provider_call_count"] == 0
    assert generation["work_order"]["occupied_enabled"] is False
    assert generation["acknowledgement"]["lease_to"] == "ariadne"
    assert len(gauge_results) == 14
    counters = generation["readings"]["workflow_retry_counters"]
    request = generation["journal"][0]["payload"]
    assert request["workflow_retry_counters_sha256"] == clock.digest(counters)
    assert request["attempt_ordinal"] == sum(counters.values()) + 1
    assert all(item["result"] == "rejected_before_publication" for item in gauge_results)
    clock.validate_generation(generation, contract)


def test_public_builder_has_no_binding_field_parameters() -> None:
    assert list(inspect.signature(clock.build_generation).parameters) == [
        "repo_root",
        "contract_path",
        "gauges_path",
    ]
    contract = clock.load_json(CONTRACT)
    assert contract["caller_supplied_binding_fields"] == []
    assert len(contract["engine_owned_fields"]) == 15


def test_every_git_binding_is_full_length_and_protected_refs_are_exact(reading) -> None:
    generation, contract, _ = reading
    git = generation["readings"]["git"]
    assert clock.GIT_OID.fullmatch(git["refs"]["head"])
    for name in ("master", "origin_master", "handoff_current", "origin_handoff_current"):
        assert git["refs"][name] == contract["protected_ref_oid"]


def test_all_fourteen_failure_gauges_reject_in_the_declared_phase(reading) -> None:
    _, _, gauge_results = reading
    gauges = clock.validate_failure_gauges(clock.load_json(GAUGES))
    expected = {(item["id"], item["rejection_rule"], item["expected_phase"]) for item in gauges}
    actual = {(item["id"], item["rule"], item["phase"]) for item in gauge_results}
    assert actual == expected


def test_efficacy_is_calculated_against_the_frozen_threshold(reading) -> None:
    generation, contract, gauge_results = reading
    result = clock.calculate_efficacy(
        contract,
        generation,
        gauge_results,
        line_growth={"engine": 1, "total": 1},
        clean_run_overhead_ms=1.25,
    )
    assert result["comparator_failure_induced_reruns"] == 14
    candidate = sum(generation["readings"]["workflow_retry_counters"].values())
    assert result["candidate_failure_induced_reruns"] == candidate
    assert result["failure_induced_rerun_reduction_percent"] == pytest.approx(
        ((14 - result["candidate_failure_induced_reruns"]) / 14) * 100,
        abs=0.001,
    )
    assert result["failure_gauges_covered"] == 14
    assert result["caller_supplied_derived_fields"] == 0
    assert result["new_mutable_current_fixtures"] == 0
    assert result["partial_publications"] == 0
    assert result["uncaught_escapes"] == 0
    assert result["coverage_loss"] is False
    assert result["timing_acceptance_relevant"] is False
    assert result["accepted"] is (candidate <= 7)


@pytest.mark.parametrize(
    ("mutation", "rule"),
    [
        (lambda value: value["journal"].__setitem__(1, copy.deepcopy(value["journal"][0])), "sequence_gap"),
        (lambda value: value["journal"][2].__setitem__("writer", "ariadne"), "concurrent_writer"),
        (lambda value: value["journal"][2].__setitem__("previous_event_sha256", "f" * 64), "stale_parent"),
        (lambda value: value["terminal_result"].__setitem__("provider_call_count", 1), "provider_call"),
        (lambda value: value["terminal_result"].__setitem__("worker_self_accepted", True), "worker_self_acceptance"),
        (lambda value: value["acknowledgement"].__setitem__("lease_to", "deepseek_broker"), "lease_not_returned"),
        (lambda value: value["projections"]["compass"].__setitem__("acknowledged_tip_sha256", "0" * 64), "projection_tip"),
    ],
)
def test_hostile_gear_mutations_fail_closed(reading, mutation, rule: str) -> None:
    generation, contract, _ = reading
    hostile = copy.deepcopy(generation)
    mutation(hostile)
    with pytest.raises(clock.ClockworkRejection, match=rule):
        clock.validate_generation(hostile, contract)


def test_abbreviated_latch_source_is_rejected_without_a_rerun() -> None:
    contract = clock.validate_contract(clock.load_json(CONTRACT))
    latch = clock.load_json(ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json")
    latch["source_head"] = latch["source_head"][:7]
    with pytest.raises(clock.ClockworkRejection, match="latch_full_source_oid"):
        clock.validate_latch(latch, contract)


def test_atomic_publication_success_and_readback(tmp_path: Path, reading) -> None:
    generation, contract, gauge_results, efficacy = _accepted_publication_reading(
        reading
    )
    target = tmp_path / "private-shadow-generation"
    clock.publish_private_shadow(generation, contract, gauge_results, efficacy, target)
    assert set(path.name for path in target.iterdir()) == set(contract["publication"]["authoritative_files"])
    assert clock.SHA256.fullmatch(clock.authoritative_manifest_digest(target))


def test_injected_publication_failure_leaves_no_partial_generation(tmp_path: Path, reading) -> None:
    generation, contract, gauge_results, efficacy = _accepted_publication_reading(
        reading
    )
    target = tmp_path / "private-shadow-generation"
    with pytest.raises(OSError, match="injected publication failure"):
        clock.publish_private_shadow(
            generation,
            contract,
            gauge_results,
            efficacy,
            target,
            fail_after_write=3,
        )
    assert not target.exists()
    assert not list(tmp_path.glob(".private-shadow-generation.staging-*"))


def test_authoritative_tick_is_deterministic_and_timing_free(reading) -> None:
    first, contract, _ = reading
    second, _, _ = clock.build_generation(ROOT, CONTRACT, GAUGES)
    assert clock.digest(first) == clock.digest(second)
    assert "clean_run_overhead" not in str(first)
    assert contract["efficacy"]["timing_acceptance_relevant"] is False


def test_retry_counter_change_moves_the_causal_tick(reading) -> None:
    generation, contract, _ = reading
    hostile = copy.deepcopy(generation)
    hostile["readings"]["workflow_retry_counters"]["verification"] += 1
    with pytest.raises(clock.ClockworkRejection, match="retry_counter_binding"):
        clock.validate_generation(hostile, contract)


def test_authoritative_manifest_binds_efficacy_but_excludes_only_timing(tmp_path: Path, reading) -> None:
    generation, contract, gauge_results, _ = _accepted_publication_reading(reading)
    first = clock.calculate_efficacy(
        contract,
        generation,
        gauge_results,
        line_growth={"total": 1},
        clean_run_overhead_ms=1.0,
    )
    second = {**first, "clean_run_overhead_ms_median": 999.0}
    first_target = tmp_path / "one" / "private-shadow-generation"
    second_target = tmp_path / "two" / "private-shadow-generation"
    first_target.parent.mkdir()
    second_target.parent.mkdir()
    clock.publish_private_shadow(generation, contract, gauge_results, first, first_target)
    clock.publish_private_shadow(generation, contract, gauge_results, second, second_target)
    assert clock.authoritative_manifest_digest(first_target) == clock.authoritative_manifest_digest(second_target)

    changed = {**first, "candidate_failure_induced_reruns": 7}
    third_target = tmp_path / "three" / "private-shadow-generation"
    third_target.parent.mkdir()
    with pytest.raises(clock.ClockworkRejection, match="efficacy_integrity"):
        clock.publish_private_shadow(
            generation, contract, gauge_results, changed, third_target
        )
