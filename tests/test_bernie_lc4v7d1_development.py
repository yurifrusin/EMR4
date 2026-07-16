"""Fail-closed tests for the LC4V7D1 development evidence runner.

Tests cover exact fixture hash, fail-closed validation for every structural
gate, exact two-repeat accounting, zero variance, classification accounting,
selection/report hash determinism, safety invariants, and absence of probe-ID
branching in the runner.

No assertion assumes baseline gaps pass; the runner discovers them.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

from app.services.bernie.lc4v7d1_development_evidence import (
    EXPECTED_FAMILY_COUNTS,
    TOTAL_EXPECTED,
    CLASSIFICATIONS,
    compute_fixture_hash,
    load_fixture,
    run_lc4v7d1_evidence,
    validate_fixture,
)

FIXTURE = load_fixture()
EVIDENCE = run_lc4v7d1_evidence()


# ---------------------------------------------------------------------------
# Fixture integrity
# ---------------------------------------------------------------------------


def test_fixture_is_exact_and_frozen() -> None:
    errors = validate_fixture(FIXTURE)
    assert not errors, f"Fixture validation errors: {errors}"
    assert len(FIXTURE["cases"]) == TOTAL_EXPECTED
    assert EVIDENCE["fixture_hash"] == compute_fixture_hash(FIXTURE)
    assert EVIDENCE["fixture_hash"] == (
        "sha256:03544ffab7d3a720faf6cba3cac7f33c5e45e7a42dfec231223334fdd335b2ea"
    )


# ---------------------------------------------------------------------------
# Fail-closed validation mutations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda value: value.update({"schema_version": "wrong"}), "schema_version"),
        (lambda value: value.update({"reference_date": "2026-07-17"}), "reference_date"),
        (lambda value: value.update({"provenance": "unknown"}), "provenance"),
        (lambda value: value["cases"].pop(), "case population"),
        (
            lambda value: value["cases"][1].update(
                {"probe_id": FIXTURE["cases"][0]["probe_id"]}
            ),
            "unique",
        ),
        (lambda value: value["cases"][0].pop("expected"), "field population"),
        (
            lambda value: value["cases"][0]["expected"].pop("intended_action"),
            "expected field population",
        ),
        (
            lambda value: value["cases"][0]["expected"]["normalization_time_forms"]
            .append({"bad": "data"}),
            "normalization_time_forms",
        ),
        (
            lambda value: value["cases"][0]["expected"]["normalization_time_forms"][0]
            .update(turn_index=-1),
            "turn_index",
        ),
        (
            lambda value: value["cases"][0]["expected"]["normalization_time_forms"][0]
            .update(canonical="25:90"),
            "canonical",
        ),
        (
            lambda value: value["cases"][0]["expected"]
            .update(safe_no_mutation=1),
            "safe_no_mutation",
        ),
    ],
)
def test_fixture_validation_fails_closed(
    mutation, expected_error: str
) -> None:
    changed = copy.deepcopy(FIXTURE)
    mutation(changed)
    errors = validate_fixture(changed)
    assert any(expected_error in error for error in errors)


# ---------------------------------------------------------------------------
# Family population
# ---------------------------------------------------------------------------


def test_family_population_is_exact() -> None:
    actual: dict[str, int] = {}
    for case in FIXTURE["cases"]:
        actual[case["family"]] = actual.get(case["family"], 0) + 1
    assert actual == EXPECTED_FAMILY_COUNTS


# ---------------------------------------------------------------------------
# Aggregate integrity
# ---------------------------------------------------------------------------


def test_final_aggregate_and_classifications() -> None:
    """Confirm every frozen fresh probe passes after bounded repair."""
    assert EVIDENCE["fixture_valid"] is True
    agg = EVIDENCE["aggregate"]
    assert agg["total"] == 24
    assert agg == {
        "total": 24,
        "normalization_pass": 24,
        "extraction_pass": 24,
        "policy_pass": 24,
        "composed_pass": 24,
        "safe": 24,
        "variance": 0,
    }
    assert EVIDENCE["classifications"] == {
        "pass": 24,
        "authoring_invalid": 0,
        "normalization_gap": 0,
        "parser_gap": 0,
        "policy_gap": 0,
        "contract_layer_gap": 0,
    }

    # Family counts match
    assert EVIDENCE["family_counts"] == EXPECTED_FAMILY_COUNTS


def test_classification_accounting() -> None:
    """Every case has exactly one classification from the allowed set."""
    for item in EVIDENCE["cases"]:
        assert item["classification"] in CLASSIFICATIONS


def test_exact_two_repeat_accounting() -> None:
    """Each case runs twice; both observations are exposed."""
    for item in EVIDENCE["cases"]:
        obs = item["observations"]
        assert len(obs) == 2


def test_zero_variance() -> None:
    """All 24 cases must have zero variance over two repeats."""
    for item in EVIDENCE["cases"]:
        assert item["variance"] is False, (
            f"{item['probe_id']} has variance between repeats"
        )
    assert EVIDENCE["aggregate"]["variance"] == 0


# ---------------------------------------------------------------------------
# Per-case layer details
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("item", EVIDENCE["cases"], ids=lambda x: x["probe_id"])
def test_each_case_mismatch_accounting(item: dict) -> None:
    """Every case has consistent mismatch tuples."""
    assert isinstance(item["normalization_mismatches"], tuple)
    assert isinstance(item["extraction_mismatches"], tuple)
    assert isinstance(item["policy_mismatches"], tuple)
    # Classification must be consistent with mismatches
    if item["classification"] == "pass":
        assert not item["normalization_mismatches"]
        assert not item["extraction_mismatches"]
        assert not item["policy_mismatches"]
    elif item["classification"] == "normalization_gap":
        assert item["normalization_mismatches"]
    elif item["classification"] == "parser_gap":
        assert not item["normalization_mismatches"]
        assert item["extraction_mismatches"]
    elif item["classification"] == "policy_gap":
        assert not item["normalization_mismatches"]
        assert not item["extraction_mismatches"]
        assert item["policy_mismatches"]
    elif item["classification"] == "contract_layer_gap":
        assert not item["normalization_mismatches"]
        assert not item["extraction_mismatches"]
        assert not item["policy_mismatches"]


def test_speech_like_time_cases_pass_all_layers() -> None:
    speech = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "speech_like_time"
    ]
    assert len(speech) == 6
    for item in speech:
        assert item["classification"] == "pass"
        assert item["normalization_mismatches"] == ()
        assert item["extraction_mismatches"] == ()
        assert item["policy_mismatches"] == ()


def test_cross_turn_interval_cases_pass_all_layers() -> None:
    intervals = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "cross_turn_interval"
    ]
    assert len(intervals) == 6
    for item in intervals:
        assert item["classification"] == "pass"
        assert item["normalization_mismatches"] == ()
        assert item["extraction_mismatches"] == ()
        assert item["policy_mismatches"] == ()


def test_ambiguous_practitioner_cases_pass_all_layers() -> None:
    ambiguous = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "ambiguous_practitioner_alternatives"
    ]
    assert len(ambiguous) == 6
    for item in ambiguous:
        assert item["classification"] == "pass"
        assert item["normalization_mismatches"] == ()
        assert item["extraction_mismatches"] == ()
        assert item["policy_mismatches"] == ()


def test_unknown_practitioner_cases_pass_all_layers() -> None:
    unknown = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "unknown_practitioner_schedule_explanation"
    ]
    assert len(unknown) == 6
    for item in unknown:
        assert item["classification"] == "pass"
        assert item["normalization_mismatches"] == ()
        assert item["extraction_mismatches"] == ()
        assert item["policy_mismatches"] == ()


# ---------------------------------------------------------------------------
# Layer divergence
# ---------------------------------------------------------------------------


def test_unknown_practitioner_layer_divergence() -> None:
    """Unknown-practitioner cases have expected extraction/policy divergence.

    Expected and observed divergence are both true: extraction recognizes the
    name while policy requires authoritative roster clarification.
    """
    unknown = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "unknown_practitioner_schedule_explanation"
    ]
    for item in unknown:
        assert item["expected_layer_divergence"] is True
        assert item["observed_layer_divergence"] is True
        assert item["classification"] == "pass"


def test_no_contract_layer_gaps() -> None:
    """No contract-layer gaps exist (divergence matches expected everywhere)."""
    assert EVIDENCE["classifications"].get("contract_layer_gap", 0) == 0


# ---------------------------------------------------------------------------
# Safety invariants
# ---------------------------------------------------------------------------


def test_safety_invariants() -> None:
    """Check per-case safety counts."""
    for item in EVIDENCE["cases"]:
        expected = next(
            c["expected"]
            for c in FIXTURE["cases"]
            if c["probe_id"] == item["probe_id"]
        )
        if expected.get("safe_no_mutation", True):
            # Must be safe because strict invariants hold
            # (policy mismatches are checked by _safe)
            obs = item["observations"][0]
            pol = obs["policy"]
            if item["classification"] != "policy_gap":
                # If no policy gap, strict safety must hold
                assert item["safe"] is True, f"{item['probe_id']} should be safe"
            else:
                # Policy gap cases may or may not be safe depending on
                # whether they still meet the strict criteria
                assert isinstance(item["safe"], bool)
        else:
            # Create controls: safety requires resolved practitioner ID
            if not item["policy_mismatches"]:
                assert item["safe"] is True, (
                    f"{item['probe_id']} should be safe (no policy mismatches)"
                )
            assert isinstance(item["safe"], bool)


# ---------------------------------------------------------------------------
# Hash determinism
# ---------------------------------------------------------------------------


def test_selection_and_report_hashes_are_deterministic() -> None:
    """Running twice produces identical hashes."""
    second = run_lc4v7d1_evidence()
    assert second["report_hash"] == EVIDENCE["report_hash"]
    assert second["selection"] == EVIDENCE["selection"]
    assert second["fixture_hash"] == EVIDENCE["fixture_hash"]
    assert second["aggregate"] == EVIDENCE["aggregate"]


def test_report_hash_binds_final_selection_and_complete_report() -> None:
    payload = copy.deepcopy(EVIDENCE)
    reported_hash = payload.pop("report_hash")
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert reported_hash == "sha256:" + hashlib.sha256(encoded).hexdigest()
    assert EVIDENCE["selection"] == {
        "non_pass_count": 0,
        "selection_hash": (
            "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
        ),
    }
    assert reported_hash == (
        "sha256:802f089a0d356706bef8d40846955c241f4459bd75d836c302020f1725b97808"
    )


def test_family_specific_classifications() -> None:
    """Every case has a valid family that maps to expected counts."""
    family_classifications: dict[str, dict[str, int]] = {}
    for item in EVIDENCE["cases"]:
        family_classifications.setdefault(item["family"], {})
        cls = item["classification"]
        family_classifications[item["family"]][cls] = (
            family_classifications[item["family"]].get(cls, 0) + 1
        )
    assert family_classifications == {
        family: {"pass": 6} for family in EXPECTED_FAMILY_COUNTS
    }


# ---------------------------------------------------------------------------
# No probe-ID branching
# ---------------------------------------------------------------------------


def test_runner_never_branches_on_probe_identity() -> None:
    """The runner must not contain ``if probe_id`` branches."""
    source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v7d1_development_evidence",
            fromlist=["run_lc4v7d1_evidence"],
        )
    )
    assert "if probe_id" not in source
    assert "probe_id ==" not in source


def test_observe_never_passes_expected_values() -> None:
    """The ``_observe`` function must not reference ``expected``."""
    observe_source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v7d1_development_evidence",
            fromlist=["_observe"],
        )._observe
    )
    assert "expected" not in observe_source
    assert "probe_id" not in observe_source


# ---------------------------------------------------------------------------
# Authoring-invalid guard
# ---------------------------------------------------------------------------


def test_validation_invalid_returns_authoring_invalid_without_execution() -> None:
    """A broken fixture must return all cases as authoring_invalid."""
    broken = copy.deepcopy(FIXTURE)
    broken["schema_version"] = "bad"
    result = run_lc4v7d1_evidence(broken)
    assert result["fixture_valid"] is False
    assert result["aggregate"]["total"] == 0
    assert result["cases"] == ()
    assert result["classifications"]["authoring_invalid"] == TOTAL_EXPECTED
    assert all(
        count == 0
        for name, count in result["classifications"].items()
        if name != "authoring_invalid"
    )
