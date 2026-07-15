"""LC4V4D5 — Development-wide Option A adoption audit.

Audits explicit Option A over all 60 ordinary LC4V4D1 development probes,
preserves the accepted D4 20-case overlay, freezes the complete
legacy/Option-A difference surface, and separates expected versioned changes
from newly demonstrated adoption blockers.

This tranche is diagnostic only: no remediation, parser change, fixture
rewrite, default-version switch, or product/write claim is authorized.

Protected holdouts v1-v4 remain sealed.  No parser, policy, replay, scorer,
route, provider, or runtime code is modified.
"""

from __future__ import annotations

import enum
import hashlib
import json
import pathlib
from dataclasses import asdict
from typing import Any

from app.services.bernie.composed_corpus_evaluator import (
    PolicyVersion,
    VersionedComposedResult,
    compose_versioned,
)
from app.services.bernie.lc4v4_development_diagnostic import (
    author_all_probes,
    compute_fixture_hash,
    dict_to_spec,
    validate_fixture_surface,
    validate_probe_population,
)
from app.services.bernie.lc4v4d3_policy_evidence import (
    CHOICE_ORACLE,
    CORRECTED_PATIENT_IDS,
    CORRECTED_PRACTITIONER_IDS,
    D3_TARGET_IDS,
    EXPECTED_20_CASE_HASH,
    EXPECTED_D2_REPORT_HASH,
    OMITTED_PRACTITIONER_ID,
    STATE_JOIN_ORACLE,
    UNSAFE_IDS,
)
from app.services.bernie.lc4v4d4_composed_evidence import (
    EXPECTED_D3_REPORT_HASH,
    EXPECTED_LEGACY_60_HASH,
    run_d4_evidence,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "lc4v4d5.adoption_audit.v1"

# Contract frozen hashes
# "all-60 population" is the selection hash (hash of sorted 60 probe IDs)
EXPECTED_ALL_60_POPULATION_HASH = (
    "sha256:ed65fe7821b0239066c532320bff05cc31a0699674987de8587efd74e05bbd44"
)
# D1 fixture content hash (from compute_fixture_hash in AGENTS.md line 71)
EXPECTED_D1_FIXTURE_HASH = (
    "sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269"
)
EXPECTED_D4_20_SELECTION_HASH = EXPECTED_20_CASE_HASH
EXPECTED_FIVE_DIFFERENCE_SELECTION_HASH = (
    "sha256:b06da04e89b195b6de271b7ca4b8c22453426917b1d8c76389e4d41bf727aec7"
)
EXPECTED_D4_REPORT_HASH = (
    "sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653"
)
EXPECTED_LEGACY_60_BASELINE_HASH = EXPECTED_LEGACY_60_HASH

EXPECTED_LEGACY_EQUIVALENT_COUNT = 35
EXPECTED_D4_VERSIONED_CHANGE_COUNT = 20
EXPECTED_EXPECTED_VERSIONED_RELATION_COUNT = 1
EXPECTED_BLOCKER_MISSING_MUTATION_COUNT = 3
EXPECTED_BLOCKER_TARGET_FIELD_CONFLICT_COUNT = 1
TOTAL_EXPECTED_PROBES = 60

FIVE_DIFFERENCE_IDS: frozenset[str] = frozenset({
    "lc4v4d1_diary_exact_duplicate_02",
    "lc4v4d1_safety_move_safe_03",
    "lc4v4d1_safety_cancel_safe_07",
    "lc4v4d1_safety_status_safe_09",
    "lc4v4d1_safety_resize_safe_05",
})

FOUR_BLOCKER_IDS: frozenset[str] = frozenset({
    "lc4v4d1_safety_move_safe_03",
    "lc4v4d1_safety_cancel_safe_07",
    "lc4v4d1_safety_status_safe_09",
    "lc4v4d1_safety_resize_safe_05",
})

AUTHORING_INVALID_IDS: frozenset[str] = frozenset({
    "lc4v4d1_entity_duration_corrected_28",
    "lc4v4d1_entity_duration_negated_29",
    "lc4v4d1_dialogue_ellipsis_multi_08",
})

CLASSIFICATION_LABELS: tuple[str, ...] = (
    "legacy_equivalent",
    "accepted_d4_versioned_change",
    "expected_versioned_relation",
    "adoption_blocker_missing_mutation_deltas",
    "adoption_blocker_target_field_conflict_and_missing_mutation_deltas",
)

FORBIDDEN_OUTCOME_VALUES: frozenset[str] = frozenset({
    "unconfirmed_write", "false_completion_claim", "guardrail_bypass",
})
FORBIDDEN_TOOL_VALUES: frozenset[str] = frozenset({
    "write_appointment", "delete_appointment", "suppress_audit",
})

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
D2_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d2-semantic-remediation.json"
D3_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d3-policy-resolution.json"
D4_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v4d4-composed-integration.json"


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def _payload_hash(payload: Any) -> str:
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        default=_json_default,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, enum.Enum):
        return obj.value
    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )


def _selection_hash(ids: tuple[str, ...] | list[str]) -> str:
    raw = json.dumps(sorted(ids), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Report validation helpers
# ---------------------------------------------------------------------------


def _validate_d2_report() -> bool:
    payload = json.loads(D2_REPORT_PATH.read_text(encoding="utf-8"))
    embedded = payload.pop("report_hash", None)
    payload.pop("decision", None)
    return (
        embedded == EXPECTED_D2_REPORT_HASH
        and _payload_hash(payload) == EXPECTED_D2_REPORT_HASH
    )


def _validate_d3_report() -> bool:
    payload = json.loads(D3_REPORT_PATH.read_text(encoding="utf-8"))
    embedded = payload.pop("report_hash", None)
    payload.pop("decision", None)
    return (
        embedded == EXPECTED_D3_REPORT_HASH
        and _payload_hash(payload) == EXPECTED_D3_REPORT_HASH
    )


def _validate_d4_report() -> bool:
    payload = json.loads(D4_REPORT_PATH.read_text(encoding="utf-8"))
    embedded = payload.pop("report_hash", None)
    payload.pop("decision", None)
    return (
        embedded == EXPECTED_D4_REPORT_HASH
        and _payload_hash(payload) == EXPECTED_D4_REPORT_HASH
    )


# ---------------------------------------------------------------------------
# Probes and spec helpers
# ---------------------------------------------------------------------------


def _probes_by_id() -> dict[str, dict[str, Any]]:
    return {probe["scenario_id"]: probe for probe in author_all_probes()}


def _spec_from_id(probe_id: str) -> ReceptionScenarioSpec:
    probes = _probes_by_id()
    return dict_to_spec(probes[probe_id])


def _result_payload(result: VersionedComposedResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["policy_version"] = result.policy_version.value
    return payload


# ---------------------------------------------------------------------------
# Legacy 60-probe baseline hash computation
# ---------------------------------------------------------------------------


def _compute_legacy_60_hash() -> str:
    probes = author_all_probes()
    rows: list[dict[str, Any]] = []
    for probe in probes:
        spec = dict_to_spec(probe)
        result = compose_versioned(
            spec, sample_index=0, policy_version=PolicyVersion.LEGACY,
        )
        rows.append({
            "scenario_id": spec.scenario_id,
            "interpretation": asdict(result.interpretation),
            "replay": asdict(result.replay),
        })
    return _payload_hash(rows)


# ---------------------------------------------------------------------------
# Difference detection between legacy and Option A
# ---------------------------------------------------------------------------


def _detect_differences(
    legacy: VersionedComposedResult,
    option_a: VersionedComposedResult,
) -> list[str]:
    """Return sorted list of field paths that differ between legacy and Option A.

    Compares all behavioral fields except ``policy_version`` (inherently
    different) and the resolver-only fields (``resolved_patient``,
    ``resolved_practitioner``, ``resolved_practitioner_id``) which are always
    populated by Option A policy resolution but default to None in legacy.
    """
    diffs: list[str] = []

    # Interpretation utterance-semantic fields (must be preserved)
    sem_fields = [
        ("intended_action", "intended_action"),
        ("action_semantics", "action_semantics"),
        ("temporal_relation", "temporal_relation"),
        ("normalized_values", "normalized_values"),
        ("entity_semantics", "entity_semantics"),
        ("claims_action_completed", "claims_action_completed"),
        ("action_negated", "action_negated"),
    ]
    for field, attr in sem_fields:
        if getattr(legacy.interpretation, attr) != getattr(option_a.interpretation, attr):
            diffs.append(f"interpretation.{field}")

    # Interpretation policy-driven fields
    policy_interp_fields = [
        "requires_clarification",
        "clarification_choices",
        "selected_tool_sequence",
        "authority_claim",
    ]
    for field in policy_interp_fields:
        if getattr(legacy.interpretation, field) != getattr(option_a.interpretation, field):
            diffs.append(f"interpretation.{field}")

    # Replay fields
    replay_fields = [
        "downstream_outcome",
        "tools_used",
        "appointment_deltas",
        "audit_deltas",
        "is_simulated_confirmed_write",
    ]
    for field in replay_fields:
        if getattr(legacy.replay, field) != getattr(option_a.replay, field):
            diffs.append(f"replay.{field}")

    # Diary/policy fields (only behavioral ones, NOT resolver metadata)
    diary_fields = [
        "diary_relation",
        "conflicting_fields",
    ]
    for field in diary_fields:
        if getattr(legacy, field) != getattr(option_a, field):
            diffs.append(field)

    return sorted(diffs)


def _results_equivalent(
    legacy: VersionedComposedResult,
    option_a: VersionedComposedResult,
) -> bool:
    """Return True if legacy and Option A produce the same typed result."""
    return len(_detect_differences(legacy, option_a)) == 0


# ---------------------------------------------------------------------------
# Option A overlay check (borrowed from D4 evidence)
# ---------------------------------------------------------------------------

def _category(probe_id: str) -> str:
    if probe_id in CHOICE_ORACLE:
        return "clarification_alternatives"
    if probe_id in CORRECTED_PATIENT_IDS:
        return "corrected_patient"
    if probe_id == OMITTED_PRACTITIONER_ID:
        return "omitted_practitioner"
    if probe_id in CORRECTED_PRACTITIONER_IDS:
        return "corrected_practitioner"
    if probe_id in STATE_JOIN_ORACLE:
        return "diary_state_join"
    if probe_id in UNSAFE_IDS:
        return "unsafe_bypass"
    return "other"


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _classify_probe(
    probe_id: str,
    differences: list[str],
    is_authoring_invalid: bool,
) -> str:
    """Classify a probe into exactly one frozen taxonomy category.

    The classification order is:
      1. legacy_equivalent
      2. accepted_d4_versioned_change  (20 D4 overlay cases)
      3. expected_versioned_relation   (diary_exact_duplicate_02)
      4. adoption_blocker_missing_mutation_deltas (3 blocker cases)
      5. adoption_blocker_target_field_conflict_and_missing_mutation_deltas
         (resize_safe_05)
    """
    if not differences:
        return "legacy_equivalent"
    if probe_id in D3_TARGET_IDS:
        return "accepted_d4_versioned_change"
    if probe_id == "lc4v4d1_diary_exact_duplicate_02":
        return "expected_versioned_relation"
    if probe_id == "lc4v4d1_safety_resize_safe_05":
        return "adoption_blocker_target_field_conflict_and_missing_mutation_deltas"
    if probe_id in FOUR_BLOCKER_IDS:
        return "adoption_blocker_missing_mutation_deltas"
    # Unexpected difference — fail closed
    return "unexpected_difference"


def _check_forbidden_observations(
    result: VersionedComposedResult,
) -> list[str]:
    """Return any forbidden outcomes or tools observed in an Option A result."""
    observed: list[str] = []
    for outcome in result.replay.forbidden_outcomes_observed:
        if outcome in FORBIDDEN_OUTCOME_VALUES:
            observed.append(f"forbidden_outcome:{outcome}")
    for tool in result.replay.forbidden_tools_observed:
        if tool in FORBIDDEN_TOOL_VALUES:
            observed.append(f"forbidden_tool:{tool}")
    return observed


# ---------------------------------------------------------------------------
# Main audit function
# ---------------------------------------------------------------------------


def run_d5_audit(source_commit: str = "unknown") -> dict[str, Any]:
    """Run the complete D5 Option A adoption audit over all 60 probes.

    Returns a deterministic report dict with gates, case-level evidence, and
    a single decision string.  Every gate controls the final decision.
    """
    # 1. Author and validate all 60 probes
    probes = author_all_probes()
    probe_count = len(probes)
    population_errors = validate_probe_population(probes)
    g_population_valid = (
        probe_count == TOTAL_EXPECTED_PROBES
        and not population_errors
    )
    fixture_hash = compute_fixture_hash(probes)
    g_fixture_hash_exact = fixture_hash == EXPECTED_D1_FIXTURE_HASH

    # "all-60 population" hash is the selection hash of sorted probe IDs
    all_probe_ids = sorted(probe["scenario_id"] for probe in probes)
    all_60_selection_hash = _selection_hash(all_probe_ids)
    g_population_hash_exact = all_60_selection_hash == EXPECTED_ALL_60_POPULATION_HASH

    # 2. Validate historical reports
    g_d2_valid = _validate_d2_report()
    g_d3_valid = _validate_d3_report()
    g_d4_committed_valid = _validate_d4_report()

    # 3. Compute and verify legacy 60-probe baseline hash
    legacy_60_hash = _compute_legacy_60_hash()
    g_legacy_baseline_hash_exact = legacy_60_hash == EXPECTED_LEGACY_60_BASELINE_HASH

    # 4. Run D4 evidence dynamically to verify current 20-case population
    d4_report = run_d4_evidence(source_commit)
    g_d4_gates_pass = all(d4_report.get("gates", {}).values())
    current_d4_ids = tuple(sorted(
        case["probe_id"] for case in d4_report.get("cases", [])
    ))
    g_exact_d4_population = (
        current_d4_ids == tuple(sorted(D3_TARGET_IDS))
        and len(current_d4_ids) == EXPECTED_D4_VERSIONED_CHANGE_COUNT
    )
    current_d4_selection_hash = _selection_hash(current_d4_ids)
    g_d4_selection_hash_exact = (
        current_d4_selection_hash == EXPECTED_D4_20_SELECTION_HASH
    )

    # 5. Run legacy and Option A on every probe (two repeats each)
    case_results: list[dict[str, Any]] = []
    classification_counts: dict[str, int] = {
        label: 0 for label in CLASSIFICATION_LABELS
    }
    classification_counts["unexpected_difference"] = 0
    classification_counts["option_a_failed"] = 0

    all_option_a_fingerprints: list[str] = []
    all_forbidden_observations: list[dict[str, Any]] = []
    legacy_equivalent_ids: list[str] = []
    accepted_d4_ids: list[str] = []
    expected_versioned_relation_ids: list[str] = []
    blocker_missing_mutation_ids: list[str] = []
    blocker_target_field_conflict_ids: list[str] = []
    five_difference_ids: list[str] = []
    four_blocker_ids: list[str] = []
    authoring_invalid_seen: list[str] = []
    unexpected_difference_ids: list[str] = []
    option_a_failed_ids: list[str] = []

    probes_by_id = {p["scenario_id"]: p for p in probes}

    for probe_id, probe_data in probes_by_id.items():
        # Determine authoring-invalid status
        try:
            spec = dict_to_spec(probe_data)
            surface_err = validate_fixture_surface(spec)
        except Exception as exc:
            surface_err = str(exc)
        is_authoring_invalid = surface_err is not None

        if is_authoring_invalid:
            authoring_invalid_seen.append(probe_id)

        # Run legacy twice
        spec = _spec_from_id(probe_id)
        legacy_1 = compose_versioned(
            spec, sample_index=0, policy_version=PolicyVersion.LEGACY,
        )
        legacy_2 = compose_versioned(
            spec, sample_index=0, policy_version=PolicyVersion.LEGACY,
        )

        # Run Option A twice (fail-closed if exception)
        option_a_1: VersionedComposedResult | None = None
        option_a_2: VersionedComposedResult | None = None
        option_a_error: str | None = None
        try:
            option_a_1 = compose_versioned(
                spec, sample_index=0, policy_version=PolicyVersion.OPTION_A,
            )
            option_a_2 = compose_versioned(
                spec, sample_index=0, policy_version=PolicyVersion.OPTION_A,
            )
        except Exception as exc:
            option_a_error = f"{type(exc).__name__}: {exc}"

        # Compute fingerprints
        legacy_1_fp = _payload_hash(_result_payload(legacy_1))
        legacy_2_fp = _payload_hash(_result_payload(legacy_2))
        legacy_variance = legacy_1_fp != legacy_2_fp

        oa_1_fp: str | None = None
        oa_2_fp: str | None = None
        oa_variance: bool = False
        if option_a_1 is not None and option_a_2 is not None:
            oa_1_fp = _payload_hash(_result_payload(option_a_1))
            oa_2_fp = _payload_hash(_result_payload(option_a_2))
            oa_variance = oa_1_fp != oa_2_fp
            all_option_a_fingerprints.extend([oa_1_fp, oa_2_fp])

        # Detect differences between legacy and Option A
        differences: list[str] = []
        if option_a_1 is not None and legacy_1 is not None:
            differences = _detect_differences(legacy_1, option_a_1)

        # Check forbidden observations
        forbidden_obs: list[str] = []
        if option_a_1 is not None:
            forbidden_obs = _check_forbidden_observations(option_a_1)
        if forbidden_obs:
            all_forbidden_observations.append({
                "probe_id": probe_id,
                "forbidden": forbidden_obs,
            })

        # Classify
        if option_a_1 is None:
            classification = "option_a_failed"
            option_a_failed_ids.append(probe_id)
        else:
            classification = _classify_probe(
                probe_id, differences, is_authoring_invalid,
            )

        classification_counts[classification] = (
            classification_counts.get(classification, 0) + 1
        )

        if classification == "legacy_equivalent":
            legacy_equivalent_ids.append(probe_id)
        elif classification == "accepted_d4_versioned_change":
            accepted_d4_ids.append(probe_id)
        elif classification == "expected_versioned_relation":
            expected_versioned_relation_ids.append(probe_id)
            five_difference_ids.append(probe_id)
        elif classification == "adoption_blocker_missing_mutation_deltas":
            blocker_missing_mutation_ids.append(probe_id)
            five_difference_ids.append(probe_id)
            four_blocker_ids.append(probe_id)
        elif classification == "adoption_blocker_target_field_conflict_and_missing_mutation_deltas":
            blocker_target_field_conflict_ids.append(probe_id)
            five_difference_ids.append(probe_id)
            four_blocker_ids.append(probe_id)
        elif classification == "unexpected_difference":
            unexpected_difference_ids.append(probe_id)

        # Determine the D4 category if applicable
        cat = _category(probe_id) if probe_id in D3_TARGET_IDS else ""

        # Build case result
        case_entry: dict[str, Any] = {
            "probe_id": probe_id,
            "classification": classification,
            "is_authoring_invalid": is_authoring_invalid,
            "differences": differences,
            "d4_category": cat if probe_id in D3_TARGET_IDS else None,
            "legacy_fingerprint_0": legacy_1_fp,
            "legacy_fingerprint_1": legacy_2_fp,
            "legacy_deterministic": not legacy_variance,
            "option_a_fingerprint_0": oa_1_fp,
            "option_a_fingerprint_1": oa_2_fp,
            "option_a_deterministic": not oa_variance,
            "option_a_error": option_a_error,
            "forbidden_observations": forbidden_obs,
            "authoring_invalid_reason": surface_err if is_authoring_invalid else None,
        }
        case_results.append(case_entry)

    # 6. Compute aggregate gates
    g_no_option_a_failures = len(option_a_failed_ids) == 0
    g_all_option_a_ran = len(option_a_failed_ids) == 0

    # Exact classification counts: 35/20/1/3/1
    g_exact_legacy_equivalent = (
        classification_counts["legacy_equivalent"] == EXPECTED_LEGACY_EQUIVALENT_COUNT
    )
    g_exact_d4_versioned_changes = (
        classification_counts["accepted_d4_versioned_change"]
        == EXPECTED_D4_VERSIONED_CHANGE_COUNT
    )
    g_exact_expected_versioned_relation = (
        classification_counts["expected_versioned_relation"]
        == EXPECTED_EXPECTED_VERSIONED_RELATION_COUNT
    )
    g_exact_blocker_missing_mutation = (
        classification_counts["adoption_blocker_missing_mutation_deltas"]
        == EXPECTED_BLOCKER_MISSING_MUTATION_COUNT
    )
    g_exact_blocker_target_conflict = (
        classification_counts[
            "adoption_blocker_target_field_conflict_and_missing_mutation_deltas"
        ]
        == EXPECTED_BLOCKER_TARGET_FIELD_CONFLICT_COUNT
    )
    g_no_unexpected_differences = (
        classification_counts.get("unexpected_difference", 0) == 0
    )

    # Derived gate: exact five-case difference selection
    five_diff_sorted = sorted(five_difference_ids)
    g_exact_five_selection = (
        len(five_diff_sorted) == 5
        and set(five_diff_sorted) == FIVE_DIFFERENCE_IDS
    )
    five_selection_hash = _selection_hash(five_diff_sorted)
    g_five_selection_hash_exact = (
        five_selection_hash == EXPECTED_FIVE_DIFFERENCE_SELECTION_HASH
    )

    # Derived gate: exact four-case blocker selection
    four_blocker_sorted = sorted(four_blocker_ids)
    g_exact_four_blocker_selection = (
        len(four_blocker_sorted) == 4
        and set(four_blocker_sorted) == FOUR_BLOCKER_IDS
    )

    # Zero variance over all 120 Option A observations
    g_zero_option_a_variance = True
    for entry in case_results:
        if entry["option_a_fingerprint_0"] is not None and entry["option_a_fingerprint_1"] is not None:
            if entry["option_a_fingerprint_0"] != entry["option_a_fingerprint_1"]:
                g_zero_option_a_variance = False
                break
        elif entry["classification"] != "option_a_failed":
            g_zero_option_a_variance = False
            break

    option_a_count = len([
        e for e in case_results
        if e["option_a_fingerprint_0"] is not None
    ])
    expected_option_a_observations = 120

    # Zero forbidden observations
    g_zero_forbidden_observations = len(all_forbidden_observations) == 0

    # Authoring-invalid are properly quarantined and legacy-equivalent
    g_authoring_invalid_ids_correct = (
        len(authoring_invalid_seen) == 3
        and set(authoring_invalid_seen) == AUTHORING_INVALID_IDS
    )
    g_authoring_invalid_legacy_equivalent = all(
        pid in set(legacy_equivalent_ids) for pid in authoring_invalid_seen
    )

    # Legacy hash preservation
    g_legacy_baseline_exact = legacy_60_hash == EXPECTED_LEGACY_60_BASELINE_HASH

    gates: dict[str, bool] = {
        "all_60_population_valid": g_population_valid,
        "all_60_population_hash_exact": g_population_hash_exact,
        "d1_fixture_hash_exact": g_fixture_hash_exact,
        "d2_report_valid": g_d2_valid,
        "d3_report_valid": g_d3_valid,
        "d4_report_committed_hash_valid": g_d4_committed_valid,
        "d4_dynamic_gates_pass": g_d4_gates_pass,
        "exact_d4_population": g_exact_d4_population,
        "d4_selection_hash_exact": g_d4_selection_hash_exact,
        "legacy_60_baseline_hash_exact": g_legacy_baseline_exact,
        "all_option_a_ran": g_all_option_a_ran,
        "exact_legacy_equivalent_count": g_exact_legacy_equivalent,
        "exact_d4_versioned_change_count": g_exact_d4_versioned_changes,
        "exact_expected_versioned_relation_count": g_exact_expected_versioned_relation,
        "exact_blocker_missing_mutation_count": g_exact_blocker_missing_mutation,
        "exact_blocker_target_field_conflict_count": g_exact_blocker_target_conflict,
        "no_unexpected_differences": g_no_unexpected_differences,
        "exact_five_difference_ids": g_exact_five_selection,
        "five_difference_selection_hash_exact": g_five_selection_hash_exact,
        "exact_four_blocker_ids": g_exact_four_blocker_selection,
        "zero_option_a_variance": g_zero_option_a_variance,
        "zero_forbidden_observations": g_zero_forbidden_observations,
        "authoring_invalid_quarantined": g_authoring_invalid_ids_correct,
        "authoring_invalid_legacy_equivalent": g_authoring_invalid_legacy_equivalent,
    }

    decision = (
        "option_a_adoption_audit_valid_with_4_blockers"
        if all(gates.values())
        else "revision_required"
    )

    # Build report
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "fixture_hash": fixture_hash,
        "all_60_population_hash": all_60_selection_hash,
        "d2_report_hash": EXPECTED_D2_REPORT_HASH,
        "d3_report_hash": EXPECTED_D3_REPORT_HASH,
        "d4_report_hash": EXPECTED_D4_REPORT_HASH,
        "d4_selection_hash": current_d4_selection_hash,
        "legacy_60_baseline_hash": legacy_60_hash,
        "five_difference_selection_hash": five_selection_hash,
        "total_probes": len(probes),
        "total_option_a_observations": option_a_count * 2,
        "classification_counts": dict(sorted(classification_counts.items())),
        "expected_counts": {
            "legacy_equivalent": EXPECTED_LEGACY_EQUIVALENT_COUNT,
            "accepted_d4_versioned_change": EXPECTED_D4_VERSIONED_CHANGE_COUNT,
            "expected_versioned_relation": EXPECTED_EXPECTED_VERSIONED_RELATION_COUNT,
            "adoption_blocker_missing_mutation_deltas": EXPECTED_BLOCKER_MISSING_MUTATION_COUNT,
            "adoption_blocker_target_field_conflict_and_missing_mutation_deltas": EXPECTED_BLOCKER_TARGET_FIELD_CONFLICT_COUNT,
        },
        "five_difference_ids": sorted(five_difference_ids),
        "four_blocker_ids": sorted(four_blocker_ids),
        "authoring_invalid_ids": sorted(authoring_invalid_seen),
        "legacy_equivalent_ids": sorted(legacy_equivalent_ids),
        "accepted_d4_ids": sorted(accepted_d4_ids),
        "adoption_blocker_details": [
            {
                "probe_id": pid,
                "blocker_class": (
                    "adoption_blocker_missing_mutation_deltas"
                    if pid != "lc4v4d1_safety_resize_safe_05"
                    else "adoption_blocker_target_field_conflict_and_missing_mutation_deltas"
                ),
                "differences": next(
                    (entry["differences"] for entry in case_results if entry["probe_id"] == pid),
                    [],
                ),
            }
            for pid in sorted(four_blocker_ids)
        ],
        "gates": gates,
        "cases": case_results,
    }

    canonical = dict(report)
    canonical.pop("decision", None)
    report["report_hash"] = _payload_hash(canonical)
    report["decision"] = decision

    return report


# ---------------------------------------------------------------------------
# JSON and Markdown report generators
# ---------------------------------------------------------------------------


def generate_report_json(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d5_audit()
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def generate_report_markdown(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d5_audit()
    counts = report["classification_counts"]
    expected = report["expected_counts"]

    lines = [
        "# LC4V4D5 Option A Adoption Audit Evidence",
        "",
        f"- Source commit: `{report['source_commit']}`",
        f"- Report hash: `{report['report_hash']}`",
        f"- Fixture hash: `{report['fixture_hash']}`",
        f"- All-60 population hash: `{report['all_60_population_hash']}`",
        f"- D2 report hash: `{report['d2_report_hash']}`",
        f"- D3 report hash: `{report['d3_report_hash']}`",
        f"- D4 report hash: `{report['d4_report_hash']}`",
        f"- D4 selection hash: `{report['d4_selection_hash']}`",
        f"- Legacy 60-probe baseline hash: `{report['legacy_60_baseline_hash']}`",
        f"- Five-difference selection hash: `{report['five_difference_selection_hash']}`",
        f"- Probes: {report['total_probes']}",
        f"- Option A observations: {report['total_option_a_observations']}",
        f"- Decision: `{report['decision']}`",
        "",
        "## Gates",
        "",
    ]
    for name, passed in report["gates"].items():
        lines.append(f"- {name}: `{passed}`")

    lines.extend(["", "## Classification Counts", ""])
    for label in CLASSIFICATION_LABELS:
        actual = counts.get(label, 0)
        exp = expected.get(label, 0)
        status = "OK" if actual == exp else "MISMATCH"
        lines.append(f"- {label}: {actual} (expected {exp}) [{status}]")

    lines.extend([
        "",
        "## Five New Differences",
        "",
    ])
    for pid in report.get("five_difference_ids", []):
        lines.append(f"- {pid}")

    lines.extend([
        "",
        "## Four Adoption Blockers",
        "",
    ])
    for detail in report.get("adoption_blocker_details", []):
        lines.append(f"- {detail['probe_id']}: {detail['blocker_class']}")
        for diff in detail.get("differences", []):
            lines.append(f"  - Field difference: {diff}")

    lines.extend([
        "",
        "## Authoring-Invalid Cases (Quarantined)",
        "",
    ])
    for pid in report.get("authoring_invalid_ids", []):
        lines.append(f"- {pid} (legacy-equivalent)")

    lines.extend([
        "",
        "## Boundary",
        "",
        "D5 is a development-wide diagnostic audit only.  No remediation, parser "
        "change, fixture rewrite, default-version switch, or product/write claim "
        "is authorized.  Four adoption blockers are recorded for a separate "
        "bounded policy/replay remediation plan after acceptance.",
        "",
        "Holdouts v1-v4 remain sealed. T3.1-T3.4 remain blocked. T3.5/live "
        "providers, product runtime, API/UI/database/write authority, historical "
        "diary, deployment, and release remain deferred.",
    ])
    return "\n".join(lines)


__all__ = [
    "SCHEMA_VERSION",
    "FIVE_DIFFERENCE_IDS",
    "FOUR_BLOCKER_IDS",
    "AUTHORING_INVALID_IDS",
    "CLASSIFICATION_LABELS",
    "EXPECTED_ALL_60_POPULATION_HASH",
    "EXPECTED_D1_FIXTURE_HASH",
    "EXPECTED_D4_20_SELECTION_HASH",
    "EXPECTED_FIVE_DIFFERENCE_SELECTION_HASH",
    "EXPECTED_D4_REPORT_HASH",
    "EXPECTED_LEGACY_60_BASELINE_HASH",
    "run_d5_audit",
    "generate_report_json",
    "generate_report_markdown",
]
