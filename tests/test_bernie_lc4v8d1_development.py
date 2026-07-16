"""Fail-closed tests for the LC4V8D1 development evidence runner.

Tests cover exact fixture hash, fail-closed validation for every structural
gate, exact two-repeat accounting, zero variance, classification accounting,
selection/report hash determinism, safety invariants, and absence of probe-ID
branching in observation and projection functions.

No assertion assumes baseline gaps pass; the runner discovers them.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import json

import pytest

import app.services.bernie.lc4v8d1_development_evidence as evidence_module
from app.services.bernie.lc4v8d1_development_evidence import (
    EXPECTED_FAMILY_COUNTS,
    TOTAL_EXPECTED,
    CLASSIFICATIONS,
    PROJECTION_FIELDS,
    compute_fixture_hash,
    compute_raw_fixture_hash,
    load_fixture,
    run_lc4v8d1_evidence,
    validate_fixture,
)

FIXTURE = load_fixture()
EVIDENCE = run_lc4v8d1_evidence()


# ---------------------------------------------------------------------------
# Fixture integrity
# ---------------------------------------------------------------------------


def test_fixture_is_exact_and_frozen() -> None:
    errors = validate_fixture(FIXTURE)
    assert not errors, f"Fixture validation errors: {errors}"
    assert len(FIXTURE["cases"]) == TOTAL_EXPECTED
    assert EVIDENCE["fixture_valid"] is True
    assert EVIDENCE["fixture_hash"] == compute_fixture_hash(FIXTURE)


def test_raw_fixture_hash_matches_authorship() -> None:
    """Confirm the raw file bytes match the authorship-test frozen hash."""
    from app.services.bernie.lc4v8d1_development_evidence import FIXTURE_PATH
    digest = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
    assert (
        f"sha256:{digest}"
        == "sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c"
    )
    assert compute_raw_fixture_hash() == EVIDENCE["fixture_raw_hash"]


# ---------------------------------------------------------------------------
# Fail-closed validation mutations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        (lambda d: d.update({"schema_version": "wrong"}), "schema_version"),
        (lambda d: d.update({"reference_date": "2026-07-17"}), "reference_date"),
        (lambda d: d.update({"provenance": "unknown"}), "provenance"),
        (lambda d: d["cases"].pop(), "case population"),
        (
            lambda d: d["cases"][1].update(
                {"probe_id": FIXTURE["cases"][0]["probe_id"]}
            ),
            "unique",
        ),
        (lambda d: d["cases"][0].pop("expected"), "field population"),
        (
            lambda d: d["cases"][0]["expected"].pop("intended_action"),
            "expected field population",
        ),
        (
            lambda d: d["cases"][0]["expected"]["normalization_time_forms"]
            .append({"bad": "data"}),
            "normalization_time_forms",
        ),
        (
            lambda d: d["cases"][0]["expected"]["normalization_time_forms"][0]
            .update(turn_index=-1),
            "turn_index",
        ),
        (
            lambda d: d["cases"][0]["expected"]["normalization_time_forms"][0]
            .update(canonical="25:90"),
            "canonical",
        ),
        (lambda d: d["cases"][0].pop("family"), "field population"),
        (lambda d: d["cases"][0].update({"diary_state": "invalid"}), "diary_state"),
        (
            lambda d: d["cases"][0]["expected"]["policy_semantics"]
            .update({"resolution": "invalid"}),
            "resolution",
        ),
        (
            lambda d: d["cases"][0]["expected"]["policy_resolution"]
            .update({"appointment_delta_count": -1}),
            "appointment_delta_count",
        ),
        (
            lambda d: d["cases"][0]["expected"]["policy_semantics"]
            .update({"mutation_allowed": False}),
            "semantics and projection contradict",
        ),
        (
            lambda d: d["cases"][6]["expected"]["policy_resolution"]
            .update({"simulated_write": True}),
            "semantics and projection contradict",
        ),
        (
            lambda d: d["cases"][0]["expected"]["policy_resolution"]
            .update({"entity_semantics_unchanged": False}),
            "entity_semantics_unchanged",
        ),
        (
            lambda d: d["cases"][0]["expected"].update({"latest_time": None}),
            "temporal relation and bounds contradict",
        ),
        (
            lambda d: d["cases"][0]["diary_appointments"].append({}),
            "empty diary_state requires no appointments",
        ),
        (
            lambda d: d["cases"][11]["expected"]["policy_resolution"]
            .update({"conflicting_fields": []}),
            "field_conflict Gold is incomplete",
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


def test_family_counts_in_report() -> None:
    assert EVIDENCE["family_counts"] == EXPECTED_FAMILY_COUNTS


# ---------------------------------------------------------------------------
# Aggregate integrity
# ---------------------------------------------------------------------------


def test_aggregate_totals() -> None:
    assert EVIDENCE["fixture_valid"] is True
    agg = EVIDENCE["aggregate"]
    assert agg["total"] == 24
    assert agg["variance"] == 0


def test_classification_accounting() -> None:
    """Every case has exactly one classification from the allowed set."""
    for item in EVIDENCE["cases"]:
        assert item["classification"] in CLASSIFICATIONS


def test_classification_counts_sum_to_total() -> None:
    total = sum(EVIDENCE["classifications"].values())
    assert total == TOTAL_EXPECTED


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
    """Every case has consistent mismatch tuples and classification."""
    assert isinstance(item["normalization_mismatches"], tuple)
    assert isinstance(item["extraction_mismatches"], tuple)
    assert isinstance(item["policy_behavior_mismatches"], tuple)
    assert isinstance(item["policy_projection_mismatches"], tuple)

    if item["classification"] == "pass":
        assert not item["normalization_mismatches"]
        assert not item["extraction_mismatches"]
        assert not item["policy_behavior_mismatches"]
        assert not item["policy_projection_mismatches"]
    elif item["classification"] == "normalization_gap":
        assert item["normalization_mismatches"]
    elif item["classification"] == "parser_gap":
        assert not item["normalization_mismatches"]
        assert item["extraction_mismatches"]
    elif item["classification"] == "policy_behavior_gap":
        assert not item["normalization_mismatches"]
        assert not item["extraction_mismatches"]
        assert item["policy_behavior_mismatches"]
    elif item["classification"] == "policy_projection_gap":
        assert not item["normalization_mismatches"]
        assert not item["extraction_mismatches"]
        assert not item["policy_behavior_mismatches"]
        assert item["policy_projection_mismatches"]


# ---------------------------------------------------------------------------
# Family-specific checks
# ---------------------------------------------------------------------------


def test_canonical_policy_actions_classification() -> None:
    cases = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "canonical_policy_actions"
    ]
    assert len(cases) == 6
    for item in cases:
        assert item["normalization_mismatches"] == ()
        assert item["extraction_mismatches"] == ()
        assert item["policy_behavior_mismatches"] == ()
        assert item["policy_projection_mismatches"] == ()


def test_policy_boundaries_classification() -> None:
    cases = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "policy_boundaries"
    ]
    assert len(cases) == 6


def test_time_surface_forms_classification() -> None:
    cases = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "time_surface_forms"
    ]
    assert len(cases) == 6


def test_time_relation_composition_classification() -> None:
    cases = [
        item for item in EVIDENCE["cases"]
        if item["family"] == "time_relation_composition"
    ]
    assert len(cases) == 6


def test_family_specific_classifications() -> None:
    """Every case has a valid family with correct counts."""
    family_classifications: dict[str, dict[str, int]] = {}
    for item in EVIDENCE["cases"]:
        family_classifications.setdefault(item["family"], {})
        cls = item["classification"]
        family_classifications[item["family"]][cls] = (
            family_classifications[item["family"]].get(cls, 0) + 1
        )
    # Sum of all classifications per family must be 6
    for family, cls_counts in family_classifications.items():
        assert sum(cls_counts.values()) == 6


# ---------------------------------------------------------------------------
# Safety invariants
# ---------------------------------------------------------------------------


def test_safety_invariants() -> None:
    """Check per-case safety counts from the derived semantics."""
    for item in EVIDENCE["cases"]:
        assert isinstance(item["safe"], bool)
        # safe must be True for all cases in this fixture
        assert item["safe"] is True, (
            f"{item['probe_id']} safety invariant violated"
        )


# ---------------------------------------------------------------------------
# Hash determinism
# ---------------------------------------------------------------------------


def test_selection_and_report_hashes_are_deterministic() -> None:
    """Running twice produces identical hashes."""
    second = run_lc4v8d1_evidence()
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
    recomputed = "sha256:" + hashlib.sha256(encoded).hexdigest()
    assert reported_hash == recomputed


# ---------------------------------------------------------------------------
# No probe-ID branching
# ---------------------------------------------------------------------------


def test_runner_never_branches_on_probe_identity() -> None:
    """The evidence module must not contain ``if probe_id`` branches."""
    source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v8d1_development_evidence",
            fromlist=["run_lc4v8d1_evidence"],
        )
    )
    assert "if probe_id" not in source
    assert "probe_id ==" not in source


def test_observe_never_passes_expected_values() -> None:
    """The ``_observe`` function must not reference ``expected``."""
    observe_source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v8d1_development_evidence",
            fromlist=["_observe"],
        )._observe
    )
    assert "expected" not in observe_source
    assert "probe_id" not in observe_source


def test_project_policy_never_branches_on_identity() -> None:
    """The projection function must not contain probe-ID or expected branches."""
    source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v8d1_development_evidence",
            fromlist=["_project_policy"],
        )._project_policy
    )
    assert "expected" not in source
    assert "probe_id" not in source
    assert "probe_id ==" not in source


# ---------------------------------------------------------------------------
# Authoring-invalid guard
# ---------------------------------------------------------------------------


def test_validation_invalid_returns_authoring_invalid_without_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A broken fixture must return all cases as authoring_invalid."""
    calls = {"extract": 0, "policy": 0}

    def forbidden_extract(*args, **kwargs):
        calls["extract"] += 1
        raise AssertionError("extraction executed for invalid fixture")

    def forbidden_policy(*args, **kwargs):
        calls["policy"] += 1
        raise AssertionError("policy executed for invalid fixture")

    monkeypatch.setattr(evidence_module, "extract_semantics", forbidden_extract)
    monkeypatch.setattr(evidence_module, "resolve_policy", forbidden_policy)
    broken = copy.deepcopy(FIXTURE)
    broken["schema_version"] = "bad"
    result = run_lc4v8d1_evidence(broken)
    assert result["fixture_valid"] is False
    assert result["aggregate"]["total"] == 0
    assert result["cases"] == ()
    assert result["classifications"]["authoring_invalid"] == TOTAL_EXPECTED
    assert all(
        count == 0
        for name, count in result["classifications"].items()
        if name != "authoring_invalid"
    )
    assert calls == {"extract": 0, "policy": 0}
    assert result["selection"]["non_pass_count"] == TOTAL_EXPECTED
    assert result["selection"]["selection_hash"].startswith("sha256:")
    payload = copy.deepcopy(result)
    reported_hash = payload.pop("report_hash")
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert reported_hash == "sha256:" + hashlib.sha256(encoded).hexdigest()


def test_default_raw_fixture_drift_fails_before_product_execution(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    drifted = copy.deepcopy(FIXTURE)
    drifted["cases"][0]["language_form"] = "structurally_valid_byte_drift"
    drift_path = tmp_path / "probes.json"
    drift_path.write_text(json.dumps(drifted), encoding="utf-8")
    calls = {"extract": 0, "policy": 0}

    def forbidden_extract(*args, **kwargs):
        calls["extract"] += 1
        raise AssertionError("extraction executed after raw fixture drift")

    def forbidden_policy(*args, **kwargs):
        calls["policy"] += 1
        raise AssertionError("policy executed after raw fixture drift")

    monkeypatch.setattr(evidence_module, "FIXTURE_PATH", drift_path)
    monkeypatch.setattr(evidence_module, "extract_semantics", forbidden_extract)
    monkeypatch.setattr(evidence_module, "resolve_policy", forbidden_policy)
    result = run_lc4v8d1_evidence()
    assert result["fixture_valid"] is False
    assert result["fixture_validation_errors"] == ("raw fixture hash is not exact",)
    assert result["classifications"]["authoring_invalid"] == TOTAL_EXPECTED
    assert calls == {"extract": 0, "policy": 0}


# ---------------------------------------------------------------------------
# Projection completeness
# ---------------------------------------------------------------------------


def test_projection_contains_all_14_fields() -> None:
    """Every observation's policy projection contains exactly 14 fields."""
    for item in EVIDENCE["cases"]:
        for obs in item["observations"]:
            proj = obs["policy"]
            assert set(proj) == set(PROJECTION_FIELDS)
            assert len(proj) == len(PROJECTION_FIELDS)


def test_projection_field_types() -> None:
    """Verify the projected field types match the contract."""
    for item in EVIDENCE["cases"]:
        for obs in item["observations"]:
            p = obs["policy"]
            # Booleans
            assert isinstance(p["requires_clarification"], bool)
            assert isinstance(p["simulated_write"], bool)
            assert isinstance(p["entity_semantics_unchanged"], bool)
            # Lists (tuples converted to arrays)
            assert isinstance(p["clarification_choices"], list)
            assert isinstance(p["selected_tools"], list)
            assert isinstance(p["conflicting_fields"], list)
            # Nullable strings
            assert p["resolved_patient"] is None or isinstance(
                p["resolved_patient"], str
            )
            assert p["resolved_practitioner"] is None or isinstance(
                p["resolved_practitioner"], str
            )
            assert p["resolved_practitioner_id"] is None or isinstance(
                p["resolved_practitioner_id"], str
            )
            assert p["downstream_outcome"] is None or isinstance(
                p["downstream_outcome"], str
            )
            # Strings
            assert isinstance(p["authority"], str)
            assert isinstance(p["diary_relation"], str)
            # Integers
            assert isinstance(p["appointment_delta_count"], int)
            assert isinstance(p["audit_delta_count"], int)
            assert not isinstance(p["appointment_delta_count"], bool)
            assert not isinstance(p["audit_delta_count"], bool)
            assert p["appointment_delta_count"] >= 0
            assert p["audit_delta_count"] >= 0


# ---------------------------------------------------------------------------
# Derived semantics completeness
# ---------------------------------------------------------------------------


def test_derived_semantics_present_in_all_observations() -> None:
    """Every observation must have derived semantic policy invariants."""
    for item in EVIDENCE["cases"]:
        for i, obs in enumerate(item["observations"]):
            assert "derived_semantics" in obs, (
                f"{item['probe_id']} observation[{i}] missing derived_semantics"
            )
            ds = obs["derived_semantics"]
            assert ds["resolution"] in {
                "propose_mutation", "proceed_read", "clarify",
                "refuse", "no_action",
            }
            assert isinstance(ds["mutation_allowed"], bool)
            assert isinstance(ds["safe"], bool)


def test_incomplete_mutation_is_a_policy_behavior_gap() -> None:
    case_result = next(
        item for item in EVIDENCE["cases"]
        if item["probe_id"] == "v8d1-policy-action-001"
    )
    observation = copy.deepcopy(case_result["observations"][0])
    observation["policy"]["selected_tools"] = ["search_patients"]
    observation["policy"]["appointment_delta_count"] = 0
    observation["policy"]["audit_delta_count"] = 0
    observation["policy"]["simulated_write"] = False
    observation["derived_semantics"] = evidence_module._derive_policy_semantics(
        observation
    )
    assert observation["derived_semantics"] == {
        "resolution": "propose_mutation",
        "mutation_allowed": False,
        "safe": False,
    }
    expected = FIXTURE["cases"][0]["expected"]
    assert evidence_module._policy_behavior_mismatches(expected, observation) == (
        "mutation_allowed",
        "safe",
    )


@pytest.mark.parametrize(
    "probe_id",
    [
        "v8d1-policy-boundary-003",
        "v8d1-policy-boundary-004",
        "v8d1-policy-boundary-005",
        "v8d1-policy-action-006",
    ],
)
def test_hidden_mutation_evidence_fails_nonmutation_safety(probe_id: str) -> None:
    case_result = next(item for item in EVIDENCE["cases"] if item["probe_id"] == probe_id)
    observation = copy.deepcopy(case_result["observations"][0])
    observation["policy"]["selected_tools"].append("update_appointment")
    observation["policy"]["appointment_delta_count"] = 1
    observation["policy"]["audit_delta_count"] = 1
    observation["policy"]["simulated_write"] = True
    derived = evidence_module._derive_policy_semantics(observation)
    assert derived["safe"] is False
    assert evidence_module._safe({**observation, "derived_semantics": derived}) is False
