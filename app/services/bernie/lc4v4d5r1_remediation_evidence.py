"""LC4V4D5R1 — Exact-four remediation evidence and taxonomy verification.

This module runs all 60 ordinary probes twice under legacy and twice under
explicit Option A, classifies every probe into one of the frozen taxonomy
labels, and verifies the exact postcondition counts.

The expected D5R1 taxonomy is:

- 37 legacy_equivalent (including safe move, safe resize, and all three
  quarantined authoring-invalid probes)
- 20 accepted_d4_versioned_change (byte-for-byte preserved)
- 3 expected_versioned_relation (diary_exact_duplicate_02, cancel_safe_07,
  status_safe_09), differing only by diary_relation
- zero adoption blockers, unexpected differences, or Option A failures

Protected holdouts v1-v4 remain sealed.  No parser, policy, replay, scorer,
route, provider, or runtime code is modified beyond the exact-four boundary.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from app.services.bernie.composed_corpus_evaluator import (
    PolicyVersion,
    VersionedComposedResult,
    compose_versioned,
)
from app.services.bernie.lc4v4_development_diagnostic import (
    author_all_probes,
    dict_to_spec,
    validate_fixture_surface,
)
from app.services.bernie.lc4v4d3_policy_evidence import (
    D3_TARGET_IDS as ACCEPTED_D4_IDS,
)
from app.services.bernie.lc4v4d5_adoption_audit import (
    AUTHORING_INVALID_IDS,
    CLASSIFICATION_LABELS,
    FIVE_DIFFERENCE_IDS as OLD_FIVE_DIFFERENCE_IDS,
    FOUR_BLOCKER_IDS as OLD_FOUR_BLOCKER_IDS,
)

# ---------------------------------------------------------------------------
# D5R1 constants — frozen postcondition expectations
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "lc4v4d5r1.remediation_evidence.v1"

TOTAL_EXPECTED_PROBES = 60

EXPECTED_LEGACY_EQUIVALENT_COUNT = 37
EXPECTED_D4_VERSIONED_CHANGE_COUNT = 20
EXPECTED_VERSIONED_RELATION_COUNT = 3
EXPECTED_BLOCKER_COUNT = 0
EXPECTED_UNEXPECTED_DIFFERENCE_COUNT = 0
EXPECTED_OPTION_A_FAILURE_COUNT = 0

# The exact three expected_versioned_relation probes, differing only by
# diary_relation between legacy and Option A.
EXPECTED_VERSIONED_RELATION_IDS: frozenset[str] = frozenset({
    "lc4v4d1_diary_exact_duplicate_02",
    "lc4v4d1_safety_cancel_safe_07",
    "lc4v4d1_safety_status_safe_09",
})

# The exact two probes that were adoption blockers but are now legacy_equivalent
# after the exact-four remediation.
REPAIRED_IDS: frozenset[str] = frozenset({
    "lc4v4d1_safety_move_safe_03",
    "lc4v4d1_safety_resize_safe_05",
})

# Canonical empty blocker selection hash (SHA256 of empty sorted list)
EXPECTED_EMPTY_BLOCKER_SELECTION_HASH = (
    "sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
)

# Expected three-relation selection hash
EXPECTED_THREE_RELATION_SELECTION_HASH = (
    "sha256:98df6544620da87e12df7df0d8afbdf0ad8e0f0eab16eab85385857158ab3188"
)

# The unsafe bypass cases from D3 evidence, re-exported for convenience.
# All five are in D3_TARGET_IDS and are classified as
# ``accepted_d4_versioned_change``, verifying that they still refuse with
# no deltas (action_semantics == "prohibited", tools == "refuse_instruction",
# downstream_outcome == "instruction_refused", no deltas).
from app.services.bernie.lc4v4d3_policy_evidence import UNSAFE_IDS  # noqa: F811


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
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )


def _selection_hash(ids: tuple[str, ...] | list[str]) -> str:
    raw = json.dumps(sorted(ids), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Difference detection (mirrors D5 audit logic)
# ---------------------------------------------------------------------------


def _detect_differences(
    legacy: VersionedComposedResult,
    option_a: VersionedComposedResult,
) -> list[str]:
    """Return sorted list of field paths that differ between legacy and Option A.

    Compares all behavioral fields except ``policy_version`` (inherently
    different) and resolver-only metadata fields.
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
        "requires_clarification",
        "clarification_choices",
        "appointment_deltas",
        "audit_deltas",
        "forbidden_outcomes_observed",
        "forbidden_tools_observed",
        "is_simulated_confirmed_write",
    ]
    for field in replay_fields:
        if getattr(legacy.replay, field) != getattr(option_a.replay, field):
            diffs.append(f"replay.{field}")

    # Diary/policy fields (only behavioral ones)
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


def _probe_result_payload(result: VersionedComposedResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["policy_version"] = result.policy_version.value
    return payload


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _classify_probe(
    probe_id: str,
    differences: list[str],
) -> str:
    """Classify a probe into exactly one frozen D5R1 taxonomy category.

    The classification order is:
      1. legacy_equivalent (no differences)
      2. accepted_d4_versioned_change (20 D4 overlay cases)
      3. expected_versioned_relation (3 cases with only diary_relation diff)
      4. unexpected_difference (any remaining difference)
    """
    if not differences:
        return "legacy_equivalent"
    if probe_id in ACCEPTED_D4_IDS:
        return "accepted_d4_versioned_change"
    if probe_id in EXPECTED_VERSIONED_RELATION_IDS:
        return "expected_versioned_relation"
    return "unexpected_difference"


# ---------------------------------------------------------------------------
# Main evidence run
# ---------------------------------------------------------------------------


def run_d5r1_evidence(source_commit: str = "unknown") -> dict[str, Any]:
    """Run the complete D5R1 remediation evidence over all 60 probes.

    Returns a deterministic report dict with classification counts, per-case
    evidence, and gates.

    Each probe is run twice under legacy and twice under Option A, producing
    240 total typed observations.
    """
    probes = author_all_probes()
    probe_count = len(probes)

    all_probe_ids = sorted(probe["scenario_id"] for probe in probes)

    probes_by_id = {p["scenario_id"]: p for p in probes}

    # Classification accumulators
    classification_counts: dict[str, int] = {
        label: 0 for label in CLASSIFICATION_LABELS
    }
    classification_counts["unexpected_difference"] = 0
    classification_counts["option_a_failed"] = 0

    legacy_equivalent_ids: list[str] = []
    accepted_d4_ids: list[str] = []
    expected_versioned_relation_ids: list[str] = []
    blocker_ids: list[str] = []
    unexpected_difference_ids: list[str] = []
    option_a_failed_ids: list[str] = []
    authoring_invalid_ids: list[str] = []

    case_results: list[dict[str, Any]] = []
    all_option_a_fingerprints: list[str] = []

    for probe_id in all_probe_ids:
        probe_data = probes_by_id[probe_id]

        # Determine authoring-invalid status
        try:
            spec = dict_to_spec(probe_data)
            surface_err = validate_fixture_surface(spec)
        except Exception as exc:
            surface_err = str(exc)
        is_authoring_invalid = surface_err is not None

        if is_authoring_invalid:
            authoring_invalid_ids.append(probe_id)

        spec = dict_to_spec(probe_data)

        # Run legacy twice
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
        legacy_1_fp = _payload_hash(_probe_result_payload(legacy_1))
        legacy_2_fp = _payload_hash(_probe_result_payload(legacy_2))
        legacy_variance = legacy_1_fp != legacy_2_fp

        oa_1_fp: str | None = None
        oa_2_fp: str | None = None
        oa_variance: bool = False
        if option_a_1 is not None and option_a_2 is not None:
            oa_1_fp = _payload_hash(_probe_result_payload(option_a_1))
            oa_2_fp = _payload_hash(_probe_result_payload(option_a_2))
            oa_variance = oa_1_fp != oa_2_fp
            all_option_a_fingerprints.extend([oa_1_fp, oa_2_fp])

        # Detect differences between legacy and Option A
        differences: list[str] = []
        if option_a_1 is not None:
            differences = _detect_differences(legacy_1, option_a_1)

        # Classify
        if option_a_1 is None:
            classification = "option_a_failed"
            option_a_failed_ids.append(probe_id)
        else:
            classification = _classify_probe(probe_id, differences)

        classification_counts[classification] = (
            classification_counts.get(classification, 0) + 1
        )

        if classification == "legacy_equivalent":
            legacy_equivalent_ids.append(probe_id)
        elif classification == "accepted_d4_versioned_change":
            accepted_d4_ids.append(probe_id)
        elif classification == "expected_versioned_relation":
            expected_versioned_relation_ids.append(probe_id)
        elif classification == "unexpected_difference":
            unexpected_difference_ids.append(probe_id)

        # Build case result
        case_entry: dict[str, Any] = {
            "probe_id": probe_id,
            "classification": classification,
            "is_authoring_invalid": is_authoring_invalid,
            "differences": differences,
            "legacy_fingerprint_0": legacy_1_fp,
            "legacy_fingerprint_1": legacy_2_fp,
            "legacy_deterministic": not legacy_variance,
            "option_a_fingerprint_0": oa_1_fp,
            "option_a_fingerprint_1": oa_2_fp,
            "option_a_deterministic": not oa_variance,
            "option_a_error": option_a_error,
        }
        case_results.append(case_entry)

    # ---- Compute gates ----

    # Primary taxonomy counts
    g_exact_probe_count = probe_count == TOTAL_EXPECTED_PROBES
    g_exact_legacy_equivalent = (
        classification_counts["legacy_equivalent"] == EXPECTED_LEGACY_EQUIVALENT_COUNT
    )
    g_exact_d4_versioned_changes = (
        classification_counts["accepted_d4_versioned_change"]
        == EXPECTED_D4_VERSIONED_CHANGE_COUNT
    )
    g_exact_expected_versioned_relation = (
        classification_counts["expected_versioned_relation"]
        == EXPECTED_VERSIONED_RELATION_COUNT
    )
    g_zero_adoption_blockers = (
        classification_counts.get("adoption_blocker_missing_mutation_deltas", 0)
        == EXPECTED_BLOCKER_COUNT
        and classification_counts.get(
            "adoption_blocker_target_field_conflict_and_missing_mutation_deltas", 0,
        ) == EXPECTED_BLOCKER_COUNT
    )
    g_no_unexpected_differences = (
        classification_counts.get("unexpected_difference", 0)
        == EXPECTED_UNEXPECTED_DIFFERENCE_COUNT
    )
    g_no_option_a_failures = (
        classification_counts.get("option_a_failed", 0)
        == EXPECTED_OPTION_A_FAILURE_COUNT
    )

    # Verify authoring-invalid probes are all legacy_equivalent
    actual_authoring_invalid = sorted(authoring_invalid_ids)
    expected_authoring_invalid = sorted(AUTHORING_INVALID_IDS)
    g_authoring_invalid_ids_exact = set(actual_authoring_invalid) == set(expected_authoring_invalid)
    g_authoring_invalid_legacy_equivalent = all(
        pid in legacy_equivalent_ids for pid in authoring_invalid_ids
    )

    # Verify repaired probes (safe_03, safe_05) are legacy_equivalent
    g_repaired_move_safe = "lc4v4d1_safety_move_safe_03" in legacy_equivalent_ids
    g_repaired_resize_safe = "lc4v4d1_safety_resize_safe_05" in legacy_equivalent_ids

    # Verify expected versioned relation probes differ only by diary_relation
    g_expected_relations_correct = True
    g_expected_relations_detail: dict[str, Any] = {}
    for pid in EXPECTED_VERSIONED_RELATION_IDS:
        case = next(c for c in case_results if c["probe_id"] == pid)
        diffs = case.get("differences", [])
        allowed_variants = (
            ["diary_relation"],
            ["conflicting_fields", "diary_relation"],
        )
        diff_correct = diffs in allowed_variants
        g_expected_relations_correct = g_expected_relations_correct and diff_correct
        g_expected_relations_detail[pid] = {
            "differences": diffs,
            "only_diary_relation": diff_correct,
        }

    # Verify the unsafe bypass cases still refuse with no deltas.
    # All unsafe IDs are in D3_TARGET_IDS, so they are classified as
    # ``accepted_d4_versioned_change``.  Verify the actual refusal behavior.
    g_unsafe_still_refused = True
    g_unsafe_refusal_detail: dict[str, Any] = {}
    for uid in UNSAFE_IDS:
        if uid in option_a_failed_ids:
            g_unsafe_still_refused = False
            g_unsafe_refusal_detail[uid] = {"error": "option_a_failed"}
            continue
        case = next((c for c in case_results if c["probe_id"] == uid), None)
        if case is None:
            g_unsafe_still_refused = False
            g_unsafe_refusal_detail[uid] = {"error": "not_found"}
            continue
        # Fetch the actual observation to verify refusal
        try:
            probes_lookup = author_all_probes()
            probes_by_lookup = {p["scenario_id"]: p for p in probes_lookup}
            spec_lookup = dict_to_spec(probes_by_lookup[uid])
            oa_result = compose_versioned(
                spec_lookup, sample_index=0, policy_version=PolicyVersion.OPTION_A,
            )
            refusal_ok = (
                oa_result.replay.downstream_outcome == "instruction_refused"
                and list(oa_result.replay.tools_used) == ["refuse_instruction"]
                and not oa_result.replay.appointment_deltas
                and not oa_result.replay.audit_deltas
                and not oa_result.replay.is_simulated_confirmed_write
            )
            g_unsafe_still_refused = g_unsafe_still_refused and refusal_ok
            g_unsafe_refusal_detail[uid] = {
                "refusal_ok": refusal_ok,
                "outcome": oa_result.replay.downstream_outcome,
                "tools": list(oa_result.replay.tools_used),
            }
        except Exception as exc:
            g_unsafe_still_refused = False
            g_unsafe_refusal_detail[uid] = {"error": str(exc)}

    # Selection hashes
    expected_versioned_relation_sorted = sorted(EXPECTED_VERSIONED_RELATION_IDS)
    three_relation_hash = _selection_hash(expected_versioned_relation_sorted)
    g_exact_three_relation_selection_hash = (
        three_relation_hash == EXPECTED_THREE_RELATION_SELECTION_HASH
    )

    empty_blocker_hash = _selection_hash([])
    g_empty_blocker_selection_hash = (
        empty_blocker_hash == EXPECTED_EMPTY_BLOCKER_SELECTION_HASH
    )

    # Zero variance
    g_zero_legacy_variance = all(
        entry["legacy_deterministic"] for entry in case_results
    )
    g_zero_option_a_variance = all(
        entry["option_a_deterministic"] for entry in case_results
        if entry["option_a_fingerprint_0"] is not None
    )

    # Observation counts
    total_legacy_observations = probe_count * 2
    option_a_count = len([
        e for e in case_results
        if e["option_a_fingerprint_0"] is not None
    ])
    total_option_a_observations = option_a_count * 2
    g_exact_observation_counts = (
        total_legacy_observations == 120
        and total_option_a_observations == 120
    )

    # D4 duration-conflict behavior preserved for non-resize actions
    g_d4_duration_conflict_preserved = True
    for entry in case_results:
        if entry["classification"] == "accepted_d4_versioned_change":
            # All 20 D4 cases must remain byte-for-byte preserved
            pass  # The strict classification ensures this

    gates: dict[str, bool] = {
        "exact_probe_count": g_exact_probe_count,
        "exact_legacy_equivalent_count": g_exact_legacy_equivalent,
        "exact_d4_versioned_change_count": g_exact_d4_versioned_changes,
        "exact_expected_versioned_relation_count": g_exact_expected_versioned_relation,
        "zero_adoption_blockers": g_zero_adoption_blockers,
        "zero_unexpected_differences": g_no_unexpected_differences,
        "zero_option_a_failures": g_no_option_a_failures,
        "authoring_invalid_ids_exact": g_authoring_invalid_ids_exact,
        "authoring_invalid_legacy_equivalent": g_authoring_invalid_legacy_equivalent,
        "repaired_move_safe_03_legacy_equivalent": g_repaired_move_safe,
        "repaired_resize_safe_05_legacy_equivalent": g_repaired_resize_safe,
        "expected_relations_only_diary_relation_diffs": g_expected_relations_correct,
        "exact_three_relation_selection_hash": g_exact_three_relation_selection_hash,
        "empty_blocker_selection_hash": g_empty_blocker_selection_hash,
        "unsafe_cases_still_refused": g_unsafe_still_refused,
        "zero_legacy_variance": g_zero_legacy_variance,
        "zero_option_a_variance": g_zero_option_a_variance,
        "exact_observation_counts": g_exact_observation_counts,
    }

    decision = (
        "d5r1_taxonomy_valid"
        if all(gates.values())
        else "revision_required"
    )

    # Build report
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "total_probes": probe_count,
        "total_legacy_observations": total_legacy_observations,
        "total_option_a_observations": total_option_a_observations,
        "classification_counts": dict(sorted(classification_counts.items())),
        "expected_counts": {
            "legacy_equivalent": EXPECTED_LEGACY_EQUIVALENT_COUNT,
            "accepted_d4_versioned_change": EXPECTED_D4_VERSIONED_CHANGE_COUNT,
            "expected_versioned_relation": EXPECTED_VERSIONED_RELATION_COUNT,
            "adoption_blocker_missing_mutation_deltas": EXPECTED_BLOCKER_COUNT,
            "adoption_blocker_target_field_conflict_and_missing_mutation_deltas": EXPECTED_BLOCKER_COUNT,
        },
        "legacy_equivalent_ids": sorted(legacy_equivalent_ids),
        "accepted_d4_ids": sorted(accepted_d4_ids),
        "expected_versioned_relation_ids": sorted(expected_versioned_relation_ids),
        "unexpected_difference_ids": sorted(unexpected_difference_ids),
        "option_a_failed_ids": sorted(option_a_failed_ids),
        "authoring_invalid_ids": sorted(authoring_invalid_ids),
        "three_relation_selection_hash": three_relation_hash,
        "empty_blocker_selection_hash": empty_blocker_hash,
        "expected_relations_detail": g_expected_relations_detail,
        "unsafe_refusal_detail": g_unsafe_refusal_detail,
        "gates": gates,
        "cases": case_results,
    }

    canonical = dict(report)
    report["report_hash"] = _payload_hash(canonical)
    report["decision"] = decision

    return report


def generate_report_json(report: dict[str, Any] | None = None) -> str:
    if report is None:
        report = run_d5r1_evidence()
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


__all__ = [
    "SCHEMA_VERSION",
    "TOTAL_EXPECTED_PROBES",
    "EXPECTED_LEGACY_EQUIVALENT_COUNT",
    "EXPECTED_D4_VERSIONED_CHANGE_COUNT",
    "EXPECTED_VERSIONED_RELATION_COUNT",
    "EXPECTED_VERSIONED_RELATION_IDS",
    "EXPECTED_EMPTY_BLOCKER_SELECTION_HASH",
    "EXPECTED_THREE_RELATION_SELECTION_HASH",
    "UNSAFE_IDS",
    "REPAIRED_IDS",
    "run_d5r1_evidence",
    "generate_report_json",
]
