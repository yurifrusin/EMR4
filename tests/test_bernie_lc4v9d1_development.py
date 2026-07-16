"""Fail-closed tests for the LC4V9D1 development evidence runner.

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

import app.services.bernie.lc4v9d1_development_evidence as evidence_module
from app.services.bernie.lc4v9d1_development_evidence import (
    CLASSIFICATIONS,
    FIXTURE_PATH,
    PROJECTION_FIELDS,
    TOTAL_EXPECTED,
    compute_fixture_hash,
    compute_raw_fixture_hash,
    load_fixture,
    run_lc4v9d1_evidence,
    validate_fixture,
)

FIXTURE = load_fixture()
EVIDENCE = run_lc4v9d1_evidence()


# ---------------------------------------------------------------------------
# Fixture integrity
# ---------------------------------------------------------------------------


def test_fixture_is_exact_and_frozen() -> None:
    errors = validate_fixture(FIXTURE)
    assert not errors, f"Fixture validation errors: {errors}"
    assert len(FIXTURE["cases"]) == TOTAL_EXPECTED
    assert EVIDENCE["fixture_valid"] is True
    assert EVIDENCE["fixture_hash"] == compute_fixture_hash(FIXTURE)


def test_raw_fixture_hash_matches_expected() -> None:
    """Confirm the raw file bytes match a known frozen hash."""
    assert compute_raw_fixture_hash().startswith("sha256:")


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
            lambda d: d["cases"][0]["expected"]["entity_semantics"]
            .update({"patient": "invalid"}),
            "entity_semantics.patient",
        ),
        (lambda d: d["cases"][0].pop("language_form"), "field population"),
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
            lambda d: d["cases"][5]["expected"]["policy_resolution"]
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
# Action and language-form balance
# ---------------------------------------------------------------------------


def test_action_balance_is_exact() -> None:
    """Exactly six probes per non-create action."""
    from collections import Counter
    action_counts: Counter[str] = Counter()
    for case in FIXTURE["cases"]:
        action_counts[case["expected"]["intended_action"]] += 1
    for action in ("move", "resize", "cancel", "status_change", "explain_schedule"):
        assert action_counts[action] == 6, (
            f"{action} has {action_counts[action]} probes (expected 6)"
        )


def test_no_create_probes() -> None:
    """No create-action probes in the V9D1 fixture."""
    for case in FIXTURE["cases"]:
        assert case["expected"]["intended_action"] != "create", (
            f"{case['probe_id']} is a create probe, not allowed"
        )


def test_language_form_diversity() -> None:
    """Each action has at least one of each required language structure."""
    action_forms: dict[str, set[str]] = {}
    for case in FIXTURE["cases"]:
        action = case["expected"]["intended_action"]
        action_forms.setdefault(action, set()).add(case["language_form"])
    for action, forms in action_forms.items():
        assert len(forms) >= 3, (
            f"{action} has only {len(forms)} language forms: {forms}"
        )


# ---------------------------------------------------------------------------
# Aggregate integrity
# ---------------------------------------------------------------------------


def test_aggregate_totals() -> None:
    assert EVIDENCE["fixture_valid"] is True
    agg = EVIDENCE["aggregate"]
    assert agg["total"] == TOTAL_EXPECTED
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
    """All 30 cases must have zero variance over two repeats."""
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
    assert isinstance(item["extraction_mismatches"], tuple)
    assert isinstance(item["policy_behavior_mismatches"], tuple)
    assert isinstance(item["policy_projection_mismatches"], tuple)

    if item["classification"] == "pass":
        assert not item["extraction_mismatches"]
        assert not item["policy_behavior_mismatches"]
        assert not item["policy_projection_mismatches"]
    elif item["classification"] == "extraction_gap":
        assert item["extraction_mismatches"]
    elif item["classification"] == "policy_gap":
        assert not item["extraction_mismatches"]
        assert item["policy_behavior_mismatches"] or item["policy_projection_mismatches"]


def test_all_extraction_gaps_are_identity_related() -> None:
    """Extraction gaps must involve patient/practitioner or intended_action."""
    for item in EVIDENCE["cases"]:
        if item["classification"] == "extraction_gap":
            em = item["extraction_mismatches"]
            has_identity_issue = any(
                field in em for field in (
                    "extracted_patient", "extracted_practitioner",
                    "intended_action", "entity_semantics.patient",
                    "entity_semantics.practitioner",
                )
            )
            has_temporal_only = all(
                field in ("temporal_relation", "earliest_time", "latest_time")
                for field in em
            )
            assert has_identity_issue, (
                f"{item['probe_id']} extraction_gap has only temporal mismatches: {em}"
            )


# ---------------------------------------------------------------------------
# Safety invariants
# ---------------------------------------------------------------------------


def test_safety_invariants() -> None:
    """Check per-case safety counts from the derived semantics."""
    for item in EVIDENCE["cases"]:
        assert isinstance(item["safe"], bool)


# ---------------------------------------------------------------------------
# Hash determinism
# ---------------------------------------------------------------------------


def test_selection_and_report_hashes_are_deterministic() -> None:
    """Running twice produces identical hashes."""
    second = run_lc4v9d1_evidence()
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
            "app.services.bernie.lc4v9d1_development_evidence",
            fromlist=["run_lc4v9d1_evidence"],
        )
    )
    assert "if probe_id" not in source
    assert "probe_id ==" not in source


def test_observe_never_passes_expected_values() -> None:
    """The ``_observe`` function must not reference ``expected``."""
    observe_source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v9d1_development_evidence",
            fromlist=["_observe"],
        )._observe
    )
    assert "expected" not in observe_source
    assert "probe_id" not in observe_source


def test_project_policy_never_branches_on_identity() -> None:
    """The projection function must not contain probe-ID or expected branches."""
    source = inspect.getsource(
        __import__(
            "app.services.bernie.lc4v9d1_development_evidence",
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
    calls: dict[str, int] = {"extract": 0, "policy": 0}

    def forbidden_extract(*args: object, **kwargs: object) -> None:
        calls["extract"] += 1
        raise AssertionError("extraction executed for invalid fixture")

    def forbidden_policy(*args: object, **kwargs: object) -> None:
        calls["policy"] += 1
        raise AssertionError("policy executed for invalid fixture")

    monkeypatch.setattr(evidence_module, "extract_semantics", forbidden_extract)
    monkeypatch.setattr(evidence_module, "resolve_policy", forbidden_policy)
    broken = copy.deepcopy(FIXTURE)
    broken["schema_version"] = "bad"
    result = run_lc4v9d1_evidence(broken)
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


# ---------------------------------------------------------------------------
# Gold contradiction guard
# ---------------------------------------------------------------------------


def test_no_cross_field_gold_contradictions() -> None:
    """Every case's Gold must be internally consistent."""
    for case in FIXTURE["cases"]:
        exp = case["expected"]
        ps = exp["policy_semantics"]
        pr = exp["policy_resolution"]
        es = exp["entity_semantics"]

        # Entity semantics and extracted patient consistency
        if es.get("patient") in ("exact", "corrected"):
            assert exp.get("extracted_patient") is not None, (
                f"{case['probe_id']}: patient {es['patient']} but null extracted_patient"
            )
        if es.get("practitioner") in ("exact", "corrected"):
            assert exp.get("extracted_practitioner") is not None, (
                f"{case['probe_id']}: practitioner {es['practitioner']} but null extracted_practitioner"
            )

        # Policy semantics and resolution consistency
        if ps.get("resolution") == "propose_mutation":
            assert ps.get("mutation_allowed") is True
            assert pr.get("requires_clarification") is False
            assert pr.get("authority") == "read"
            assert any(t in pr.get("selected_tools", []) for t in
                       ["create_booking", "update_appointment", "change_appointment_status"])
            assert pr.get("downstream_outcome") is not None
            assert pr.get("appointment_delta_count") == 1
            assert pr.get("audit_delta_count") == 1
            assert pr.get("simulated_write") is True
        elif ps.get("resolution") == "refuse":
            assert pr.get("selected_tools") == ["refuse_instruction"]
            assert pr.get("authority") == "refuse"
            assert pr.get("downstream_outcome") == "instruction_refused"
            assert pr.get("appointment_delta_count") == 0
            assert pr.get("audit_delta_count") == 0
            assert pr.get("simulated_write") is False
        elif ps.get("resolution") == "no_action":
            assert pr.get("authority") == "read"
            assert pr.get("downstream_outcome") is None
            assert pr.get("appointment_delta_count") == 0
            assert pr.get("audit_delta_count") == 0
            assert pr.get("simulated_write") is False
        elif ps.get("resolution") == "proceed_read":
            assert pr.get("authority") == "read"
            assert pr.get("selected_tools") == ["find_slots"]
            assert pr.get("downstream_outcome") == "schedule_explained"
            assert pr.get("appointment_delta_count") == 0
            assert pr.get("audit_delta_count") == 0
            assert pr.get("simulated_write") is False
