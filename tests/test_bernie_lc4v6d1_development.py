"""Focused serial tests for LC4V6D1 fresh development evidence runner.

Runs all 24 probes twice, validates fixture integrity, layer-separated
extraction/policy comparison, safety, repeat-variance, and the deliberate
contract that unknown practitioner text is exact at extraction but becomes
clarification at policy when no ID maps.
"""

from __future__ import annotations

import json

import pytest

from app.services.bernie.lc4v4d3_policy_resolution import (
    map_practitioner_id,
    resolve_policy,
)
from app.services.bernie.lc4v6d1_development_evidence import (
    EXPECTED_FAMILY_COUNTS,
    FIXTURE_PATH,
    REFERENCE_DATE,
    SCHEMA_VERSION,
    TOTAL_EXPECTED,
    compute_fixture_hash,
    load_fixture,
    run_lc4v6d1_evidence,
    validate_fixture,
)
from app.services.bernie.semantic_extraction import extract_semantics

# ---------------------------------------------------------------------------
# Module-level fixture — shared integration Python path, serial execution
# ---------------------------------------------------------------------------

_fixture = load_fixture()
_evidence = run_lc4v6d1_evidence()


# ---------------------------------------------------------------------------
# Fixture validation
# ---------------------------------------------------------------------------


class TestFixtureValidation:
    """Validate fixture schema, population, counts, IDs, required fields."""

    def test_schema_version(self) -> None:
        assert _fixture["schema_version"] == SCHEMA_VERSION

    def test_reference_date(self) -> None:
        assert _fixture["reference_date"] == REFERENCE_DATE

    def test_population_count(self) -> None:
        cases = _fixture["cases"]
        assert len(cases) == TOTAL_EXPECTED

    def test_family_counts(self) -> None:
        actual: dict[str, int] = {}
        for case in _fixture["cases"]:
            family = case.get("family", "")
            actual[family] = actual.get(family, 0) + 1
        assert actual == EXPECTED_FAMILY_COUNTS

    def test_unique_probe_ids(self) -> None:
        ids = [case["probe_id"] for case in _fixture["cases"]]
        assert len(ids) == len(set(ids)), f"duplicate IDs: {ids}"

    def test_required_fields_present(self) -> None:
        required = ("probe_id", "family", "utterances", "extraction", "policy")
        for case in _fixture["cases"]:
            for field in required:
                assert field in case, (
                    f"case {case.get('probe_id', '?')} missing {field!r}"
                )

    def test_utterances_are_non_empty_lists(self) -> None:
        for case in _fixture["cases"]:
            utts = case.get("utterances", [])
            assert isinstance(utts, list) and len(utts) > 0, (
                f"case {case['probe_id']} utterances invalid"
            )

    def test_extraction_has_required_keys(self) -> None:
        required = (
            "intended_action",
            "action_semantics",
            "temporal_relation",
            "earliest_time",
            "latest_time",
            "practitioner_semantics",
            "requires_clarification",
            "clarification_choices",
            "authority",
            "tools",
            "action_negated",
        )
        for case in _fixture["cases"]:
            ext = case.get("extraction", {})
            for key in required:
                assert key in ext, (
                    f"case {case['probe_id']} extraction missing {key!r}"
                )

    def test_policy_has_required_keys(self) -> None:
        required = (
            "requires_clarification",
            "clarification_choices",
            "authority",
            "tools",
            "downstream_outcome",
            "resolved_practitioner_id",
            "appointment_delta_count",
            "audit_delta_count",
            "simulated_write",
        )
        for case in _fixture["cases"]:
            pol = case.get("policy", {})
            for key in required:
                assert key in pol, (
                    f"case {case['probe_id']} policy missing {key!r}"
                )

    def test_validate_fixture_returns_no_errors(self) -> None:
        errors = validate_fixture(_fixture)
        assert errors == [], f"fixture validation errors: {errors}"


# ---------------------------------------------------------------------------
# Deterministic fixture hash
# ---------------------------------------------------------------------------


class TestFixtureHash:
    """Deterministic canonical fixture hash."""

    def test_hash_is_string(self) -> None:
        h = compute_fixture_hash(_fixture)
        assert isinstance(h, str)
        assert h.startswith("sha256:")

    def test_hash_is_deterministic(self) -> None:
        h1 = compute_fixture_hash(_fixture)
        h2 = compute_fixture_hash(load_fixture())
        assert h1 == h2

    def test_hash_is_recorded_in_evidence(self) -> None:
        assert _evidence["fixture_hash"] == compute_fixture_hash(_fixture)


# ---------------------------------------------------------------------------
# Evidence integrity
# ---------------------------------------------------------------------------


class TestEvidenceIntegrity:
    """Overall evidence structure and aggregate counts."""

    def test_fixture_valid_flag(self) -> None:
        assert _evidence["fixture_valid"] is True
        assert _evidence["fixture_validation_errors"] == []

    def test_schema_version_matches(self) -> None:
        assert _evidence["schema_version"] == SCHEMA_VERSION

    def test_total_cases(self) -> None:
        assert _evidence["aggregate"]["total"] == TOTAL_EXPECTED

    def test_all_cases_are_included(self) -> None:
        fixture_ids = {c["probe_id"] for c in _fixture["cases"]}
        evidence_ids = {c["probe_id"] for c in _evidence["cases"]}
        assert evidence_ids == fixture_ids

    def test_every_case_has_classification(self) -> None:
        classifications = {c["classification"] for c in _evidence["cases"]}
        valid = {"pass", "parser_gap", "policy_gap", "contract_layer_gap",
                 "authoring_invalid"}
        for c in classifications:
            assert c in valid, f"unexpected classification: {c}"

    def test_classification_counts_sum_to_total(self) -> None:
        total_classified = sum(_evidence["classifications"].values())
        assert total_classified == TOTAL_EXPECTED


# ---------------------------------------------------------------------------
# Extraction layer — per-probe comparison
# ---------------------------------------------------------------------------


def _get_expected(case: dict) -> dict:
    return case["extraction"]


class TestExtractionLayer:
    """Extraction layer matches fixture extraction expectations."""

    @pytest.mark.parametrize(
        "case",
        _fixture["cases"],
        ids=lambda c: c["probe_id"],
    )
    def test_extraction_matches_fixture(self, case: dict) -> None:
        utterances = case["utterances"]
        expected = case["extraction"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)

        assert extraction.intended_action == expected["intended_action"], (
            f"intended_action: expected {expected['intended_action']!r}, "
            f"got {extraction.intended_action!r}"
        )
        assert extraction.action_semantics == expected["action_semantics"], (
            f"action_semantics: expected {expected['action_semantics']!r}, "
            f"got {extraction.action_semantics!r}"
        )
        assert extraction.temporal_relation == expected["temporal_relation"], (
            f"temporal_relation: expected {expected['temporal_relation']!r}, "
            f"got {extraction.temporal_relation!r}"
        )
        assert extraction.earliest_time == expected["earliest_time"], (
            f"earliest_time: expected {expected['earliest_time']!r}, "
            f"got {extraction.earliest_time!r}"
        )
        assert extraction.latest_time == expected["latest_time"], (
            f"latest_time: expected {expected['latest_time']!r}, "
            f"got {extraction.latest_time!r}"
        )
        assert (
            extraction.entity_semantics.get("practitioner")
            == expected["practitioner_semantics"]
        ), (
            f"practitioner_semantics: expected {expected['practitioner_semantics']!r}, "
            f"got {extraction.entity_semantics.get('practitioner')!r}"
        )
        assert (
            extraction.requires_clarification == expected["requires_clarification"]
        ), (
            f"extraction requires_clarification: "
            f"expected {expected['requires_clarification']}, "
            f"got {extraction.requires_clarification}"
        )
        assert (
            extraction.clarification_choices
            == tuple(expected.get("clarification_choices", []))
        ), (
            f"extraction clarification_choices: "
            f"expected {expected.get('clarification_choices')!r}, "
            f"got {extraction.clarification_choices!r}"
        )
        assert extraction.authority_claim == expected["authority"], (
            f"extraction authority: expected {expected['authority']!r}, "
            f"got {extraction.authority_claim!r}"
        )
        assert (
            extraction.selected_tool_sequence == tuple(expected.get("tools", []))
        ), (
            f"extraction tools: expected {expected.get('tools')!r}, "
            f"got {extraction.selected_tool_sequence!r}"
        )
        assert extraction.action_negated == expected.get("action_negated", False), (
            f"action_negated: expected {expected.get('action_negated', False)}, "
            f"got {extraction.action_negated}"
        )
        assert extraction.claims_action_completed is False


# ---------------------------------------------------------------------------
# Policy layer — per-probe comparison
# ---------------------------------------------------------------------------


class TestPolicyLayer:
    """Policy layer matches fixture policy expectations."""

    def _run_policy(self, case: dict) -> dict:
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        policy = resolve_policy(
            utterances=utterances,
            entity_semantics=extraction.entity_semantics,
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=extraction.normalized_values,
            temporal_relation=extraction.temporal_relation,
            earliest_time=extraction.earliest_time,
            latest_time=extraction.latest_time,
            action_negated=extraction.action_negated,
            diary_state="empty",
            diary_appointments=[],
            reference_date=REFERENCE_DATE,
        )
        return {
            "requires_clarification": policy.requires_clarification,
            "clarification_choices": policy.clarification_choices,
            "authority": policy.authority,
            "tools": policy.selected_tools,
            "downstream_outcome": policy.downstream_outcome,
            "resolved_practitioner_id": policy.resolved_practitioner_id,
            "appointment_delta_count": len(policy.appointment_deltas),
            "audit_delta_count": len(policy.audit_deltas),
            "simulated_write": policy.is_simulated_confirmed_write,
        }

    @pytest.mark.parametrize(
        "case",
        _fixture["cases"],
        ids=lambda c: c["probe_id"],
    )
    def test_policy_matches_fixture(self, case: dict) -> None:
        expected = case["policy"]
        actual = self._run_policy(case)

        assert (
            actual["requires_clarification"] == expected["requires_clarification"]
        ), (
            f"policy requires_clarification: "
            f"expected {expected['requires_clarification']}, "
            f"got {actual['requires_clarification']}"
        )
        assert (
            actual["clarification_choices"]
            == tuple(expected.get("clarification_choices", []))
        ), (
            f"policy clarification_choices: "
            f"expected {expected.get('clarification_choices')!r}, "
            f"got {actual['clarification_choices']!r}"
        )
        assert actual["authority"] == expected["authority"], (
            f"policy authority: expected {expected['authority']!r}, "
            f"got {actual['authority']!r}"
        )
        assert actual["tools"] == tuple(expected.get("tools", [])), (
            f"policy tools: expected {expected.get('tools')!r}, "
            f"got {actual['tools']!r}"
        )
        assert (
            actual["downstream_outcome"] == expected["downstream_outcome"]
        ), (
            f"downstream_outcome: expected {expected['downstream_outcome']!r}, "
            f"got {actual['downstream_outcome']!r}"
        )
        assert (
            actual["resolved_practitioner_id"]
            == expected["resolved_practitioner_id"]
        ), (
            f"resolved_practitioner_id: "
            f"expected {expected['resolved_practitioner_id']!r}, "
            f"got {actual['resolved_practitioner_id']!r}"
        )
        assert (
            actual["appointment_delta_count"]
            == expected["appointment_delta_count"]
        ), (
            f"appointment_delta_count: "
            f"expected {expected['appointment_delta_count']}, "
            f"got {actual['appointment_delta_count']}"
        )
        assert (
            actual["audit_delta_count"] == expected["audit_delta_count"]
        ), (
            f"audit_delta_count: expected {expected['audit_delta_count']}, "
            f"got {actual['audit_delta_count']}"
        )
        assert (
            actual["simulated_write"] == expected["simulated_write"]
        ), (
            f"simulated_write: expected {expected['simulated_write']}, "
            f"got {actual['simulated_write']}"
        )


# ---------------------------------------------------------------------------
# Unknown practitioner contract — extraction exact, policy clarification
# ---------------------------------------------------------------------------


class TestUnknownPractitionerContract:
    """Unknown practitioner text is exact at extraction, clarification at policy.

    This is the deliberate contract-layer distinction. Extraction losslessly
    recognizes practitioner text; policy owns roster lookup and fails closed
    with clarification when no ID maps.
    """

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_unknown_practitioner"],
        ids=lambda c: c["probe_id"],
    )
    def test_extraction_sees_exact_practitioner(self, case: dict) -> None:
        """Extraction recognizes unknown practitioner text as exact mention."""
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        assert (
            extraction.entity_semantics.get("practitioner") == "exact"
        ), f"expected exact practitioner semantics, got {extraction.entity_semantics.get('practitioner')!r}"

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_unknown_practitioner"],
        ids=lambda c: c["probe_id"],
    )
    def test_extraction_does_not_require_clarification(self, case: dict) -> None:
        """Extraction does not flag unknown practitioner as needing clarification."""
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        assert extraction.requires_clarification is False

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_unknown_practitioner"],
        ids=lambda c: c["probe_id"],
    )
    def test_policy_requires_clarification(self, case: dict) -> None:
        """Policy fails closed with clarification when practitioner ID is unknown."""
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        policy = resolve_policy(
            utterances=utterances,
            entity_semantics=extraction.entity_semantics,
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=extraction.normalized_values,
            temporal_relation=extraction.temporal_relation,
            earliest_time=extraction.earliest_time,
            latest_time=extraction.latest_time,
            action_negated=extraction.action_negated,
            diary_state="empty",
            diary_appointments=[],
            reference_date=REFERENCE_DATE,
        )
        assert policy.requires_clarification is True

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_unknown_practitioner"],
        ids=lambda c: c["probe_id"],
    )
    def test_no_resolved_practitioner_id(self, case: dict) -> None:
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        policy = resolve_policy(
            utterances=utterances,
            entity_semantics=extraction.entity_semantics,
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=extraction.normalized_values,
            temporal_relation=extraction.temporal_relation,
            earliest_time=extraction.earliest_time,
            latest_time=extraction.latest_time,
            action_negated=extraction.action_negated,
            diary_state="empty",
            diary_appointments=[],
            reference_date=REFERENCE_DATE,
        )
        assert policy.resolved_practitioner_id is None
        # Verify the practitioner name is not in the known map
        practitioner_name = extraction.entity_semantics.get("practitioner_name")
        if practitioner_name:
            assert map_practitioner_id(practitioner_name) is None

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_unknown_practitioner"],
        ids=lambda c: c["probe_id"],
    )
    def test_no_mutation_tools_at_policy(self, case: dict) -> None:
        """Policy selects only request_clarification, no mutation tools."""
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        policy = resolve_policy(
            utterances=utterances,
            entity_semantics=extraction.entity_semantics,
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=extraction.normalized_values,
            temporal_relation=extraction.temporal_relation,
            earliest_time=extraction.earliest_time,
            latest_time=extraction.latest_time,
            action_negated=extraction.action_negated,
            diary_state="empty",
            diary_appointments=[],
            reference_date=REFERENCE_DATE,
        )
        assert policy.selected_tools == ("request_clarification",)

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_unknown_practitioner"],
        ids=lambda c: c["probe_id"],
    )
    def test_no_deltas_or_simulated_write(self, case: dict) -> None:
        """No appointment deltas, audit deltas, or simulated write."""
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        policy = resolve_policy(
            utterances=utterances,
            entity_semantics=extraction.entity_semantics,
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=extraction.normalized_values,
            temporal_relation=extraction.temporal_relation,
            earliest_time=extraction.earliest_time,
            latest_time=extraction.latest_time,
            action_negated=extraction.action_negated,
            diary_state="empty",
            diary_appointments=[],
            reference_date=REFERENCE_DATE,
        )
        assert policy.appointment_deltas == ()
        assert policy.audit_deltas == ()
        assert policy.is_simulated_confirmed_write is False


# ---------------------------------------------------------------------------
# Known practitioner controls — both layers resolve
# ---------------------------------------------------------------------------


class TestKnownPractitionerControls:
    """Known-practitioner probes resolve at both layers."""

    @pytest.mark.parametrize(
        "case",
        [c for c in _fixture["cases"]
         if c["family"] == "move_known_practitioner_control"],
        ids=lambda c: c["probe_id"],
    )
    def test_known_practitioner_resolves(self, case: dict) -> None:
        utterances = case["utterances"]
        extraction = extract_semantics(utterances, REFERENCE_DATE)
        policy = resolve_policy(
            utterances=utterances,
            entity_semantics=extraction.entity_semantics,
            requires_clarification=extraction.requires_clarification,
            clarification_choices=extraction.clarification_choices,
            intended_action=extraction.intended_action,
            action_semantics=extraction.action_semantics,
            authority_claim=extraction.authority_claim,
            selected_tool_sequence=extraction.selected_tool_sequence,
            normalized_values=extraction.normalized_values,
            temporal_relation=extraction.temporal_relation,
            earliest_time=extraction.earliest_time,
            latest_time=extraction.latest_time,
            action_negated=extraction.action_negated,
            diary_state="empty",
            diary_appointments=[],
            reference_date=REFERENCE_DATE,
        )
        expected_id = case["policy"]["resolved_practitioner_id"]
        assert policy.resolved_practitioner_id == expected_id, (
            f"expected practitioner ID {expected_id!r}, "
            f"got {policy.resolved_practitioner_id!r}"
        )
        assert policy.requires_clarification is False
        assert policy.downstream_outcome == "appointment_moved"
        assert policy.is_simulated_confirmed_write is True


# ---------------------------------------------------------------------------
# Two-repeat variance
# ---------------------------------------------------------------------------


class TestRepeatVariance:
    """All probes must produce identical results on second repeat."""

    def test_zero_variance(self) -> None:
        assert _evidence["aggregate"]["variance"] == 0, (
            f"variance detected in probes: "
            f"{_evidence['layer_ids']['variance']}"
        )

    def test_every_case_has_two_observations(self) -> None:
        for case_result in _evidence["cases"]:
            obs = case_result["observations"]
            assert len(obs) == 2, (
                f"case {case_result['probe_id']} has {len(obs)} observations"
            )


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------


class TestSafety:
    """Safety invariants across all probes."""

    def test_no_claims_action_completed(self) -> None:
        for case_result in _evidence["cases"]:
            for obs in case_result["observations"]:
                assert obs["extraction_claims_completed"] is False, (
                    f"case {case_result['probe_id']} claims action completed"
                )

    def test_unknown_practitioner_safety(self) -> None:
        """All unknown-practitioner probes are classified as safe."""
        unknown_ids = {
            c["probe_id"] for c in _fixture["cases"]
            if c["family"] == "move_unknown_practitioner"
        }
        safe_ids = set(_evidence["layer_ids"]["safe"])
        assert unknown_ids.issubset(safe_ids), (
            f"unsafe unknown-practitioner probes: {unknown_ids - safe_ids}"
        )


# ---------------------------------------------------------------------------
# Composed (aggregate) counts
# ---------------------------------------------------------------------------


class TestComposedCounts:
    """Aggregate layer and composed counts."""

    def test_extraction_pass_count(self) -> None:
        assert _evidence["aggregate"]["extraction_pass"] == TOTAL_EXPECTED

    def test_policy_pass_count(self) -> None:
        assert _evidence["aggregate"]["policy_pass"] == TOTAL_EXPECTED

    def test_composed_pass_count(self) -> None:
        assert _evidence["aggregate"]["composed_pass"] == TOTAL_EXPECTED

    def test_safe_count(self) -> None:
        assert _evidence["aggregate"]["safe"] == TOTAL_EXPECTED


# ---------------------------------------------------------------------------
# Contract-layer gap: extraction and policy deliberately differ for
# unknown practitioners
# ---------------------------------------------------------------------------


class TestContractLayerGap:
    """Verify the runner correctly preserves separate layer expectations.

    For unknown-practitioner probes, extraction reports no clarification
    but policy requires clarification. The runner must not require
    identical clarification state at both layers.
    """

    def test_unknown_practitioner_extraction_policy_differ(self) -> None:
        """Unknown-practitioner extraction and policy clarification differ."""
        for case in _fixture["cases"]:
            if case["family"] != "move_unknown_practitioner":
                continue
            utterances = case["utterances"]
            extraction = extract_semantics(utterances, REFERENCE_DATE)
            policy = resolve_policy(
                utterances=utterances,
                entity_semantics=extraction.entity_semantics,
                requires_clarification=extraction.requires_clarification,
                clarification_choices=extraction.clarification_choices,
                intended_action=extraction.intended_action,
                action_semantics=extraction.action_semantics,
                authority_claim=extraction.authority_claim,
                selected_tool_sequence=extraction.selected_tool_sequence,
                normalized_values=extraction.normalized_values,
                temporal_relation=extraction.temporal_relation,
                earliest_time=extraction.earliest_time,
                latest_time=extraction.latest_time,
                action_negated=extraction.action_negated,
                diary_state="empty",
                diary_appointments=[],
                reference_date=REFERENCE_DATE,
            )
            assert (
                extraction.requires_clarification is False
                and policy.requires_clarification is True
            ), (
                f"case {case['probe_id']}: extraction clarify={extraction.requires_clarification}, "
                f"policy clarify={policy.requires_clarification} — "
                f"expected extraction=False, policy=True"
            )

    def test_known_practitioner_extraction_policy_same(self) -> None:
        """Known-practitioner probes have same clarification at both layers."""
        for case in _fixture["cases"]:
            if case["family"] not in (
                "move_known_practitioner_control",
                "resize_paraphrase_control",
                "status_paraphrase_control",
            ):
                continue
            utterances = case["utterances"]
            extraction = extract_semantics(utterances, REFERENCE_DATE)
            policy = resolve_policy(
                utterances=utterances,
                entity_semantics=extraction.entity_semantics,
                requires_clarification=extraction.requires_clarification,
                clarification_choices=extraction.clarification_choices,
                intended_action=extraction.intended_action,
                action_semantics=extraction.action_semantics,
                authority_claim=extraction.authority_claim,
                selected_tool_sequence=extraction.selected_tool_sequence,
                normalized_values=extraction.normalized_values,
                temporal_relation=extraction.temporal_relation,
                earliest_time=extraction.earliest_time,
                latest_time=extraction.latest_time,
                action_negated=extraction.action_negated,
                diary_state="empty",
                diary_appointments=[],
                reference_date=REFERENCE_DATE,
            )
            assert (
                extraction.requires_clarification
                == policy.requires_clarification
            ), (
                f"case {case['probe_id']}: extraction clarify={extraction.requires_clarification} "
                f"!= policy clarify={policy.requires_clarification} — "
                f"expected same for known practitioner"
            )


# ---------------------------------------------------------------------------
# Specific fixture cross-checks
# ---------------------------------------------------------------------------


class TestFixtureCrossChecks:
    """Specific fixture-label concerns and cross-checks."""

    def test_all_unknown_practitioners_not_in_map(self) -> None:
        """Verify every unknown practitioner name is genuinely unmapped."""
        names_seen = set()
        for case in _fixture["cases"]:
            if case["family"] != "move_unknown_practitioner":
                continue
            utterances = case["utterances"]
            extraction = extract_semantics(utterances, REFERENCE_DATE)
            prac_name = extraction.entity_semantics.get("practitioner_name")
            if prac_name:
                names_seen.add(prac_name)
                assert map_practitioner_id(prac_name) is None, (
                    f"practitioner {prac_name!r} found in ID map but family is "
                    f"unknown"
                )

    def test_all_known_practitioners_are_in_map(self) -> None:
        """Verify every known-practitioner name is in the ID map."""
        for case in _fixture["cases"]:
            if case["family"] not in (
                "move_known_practitioner_control",
                "resize_paraphrase_control",
                "status_paraphrase_control",
            ):
                continue
            expected_id = case["policy"]["resolved_practitioner_id"]
            assert expected_id is not None, (
                f"case {case['probe_id']} expected resolved ID is None"
            )
