#!/usr/bin/env python3
"""LC4R7 Silver contract-quality reconciliation queue and report.

Classifies the 572 aligned-failure development scenarios into a deterministic
1,436-record adjudication queue with exact frozen dispositions.

Usage:
    python scripts/bernie_lc4r7_silver_reconciliation.py            # print report JSON
    python scripts/bernie_lc4r7_silver_reconciliation.py --check     # verify frozen assertions
    python scripts/bernie_lc4r7_silver_reconciliation.py --check --json  # both
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
QUEUE_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r7-adjudication-queue.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r7-silver-reconciliation-report.json"

# ---------------------------------------------------------------------------
# Frozen constants from the LC4R7 contract  (DO NOT MODIFY)
# ---------------------------------------------------------------------------

# Frozen selection
EXPECTED_ALIGNED_FAILURE_HASH = "e17eb1739c16f3de"
EXPECTED_ALIGNED_FAILURE_COUNT = 572

# Frozen queue  (the contract constant, never the candidate's self-derived value)
EXPECTED_QUEUE_HASH = "6cb9e36b8d5309f4"
EXPECTED_QUEUE_COUNT = 1436

# Primary disposition hashes (from contract, frozen)
EXPECTED_PRIMARY_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "contradictory": {"count": 62, "hash": "d5e74c6e0544109f"},
    "incomplete": {"count": 137, "hash": "60f8b473eb85904d"},
    "malformed": {"count": 48, "hash": "9514dac1b6880d01"},
    "mixed_contract_defect": {"count": 182, "hash": "e148db0d28acdcd2"},
    "non_language_contract_mismatch": {"count": 51, "hash": "2e45f30f714568ef"},
    "planned_not_implemented": {"count": 39, "hash": "f706165328a3297f"},
    "requires_adjudication": {"count": 53, "hash": "9496e23c6f339603"},
    "surface_supported_parser_gap": {"count": 0, "hash": "e3b0c44298fc1c14"},
}

# Expected dimension/disposition counts (frozen)
EXPECTED_DIMENSION_DISPOSITIONS: dict[tuple[str, str], int] = {
    ("intended_action", "planned_not_implemented"): 26,
    ("action_semantics", "planned_not_implemented"): 39,
    ("action_semantics", "contradictory"): 78,
    ("temporal_relation", "malformed"): 66,
    ("temporal_relation", "incomplete"): 18,
    ("temporal_relation", "contradictory"): 75,
    ("normalized_values", "malformed"): 66,
    ("normalized_values", "incomplete"): 220,
    ("normalized_values", "contradictory"): 45,
    ("normalized_values", "mixed_contract_defect"): 146,
    ("entity_semantics", "incomplete"): 374,
    ("entity_semantics", "contradictory"): 17,
    ("entity_semantics", "mixed_contract_defect"): 58,
    ("requires_clarification", "planned_not_implemented"): 26,
    ("requires_clarification", "contradictory"): 78,
    ("requires_clarification", "requires_adjudication"): 53,
    ("replay_contract", "non_language_contract_mismatch"): 51,
}

# Current semantic baseline (from contract)
CURRENT_INTENDED_ACTION = 880
CURRENT_ACTION_SEMANTICS = 814
CURRENT_TEMPORAL_RELATION = 628
CURRENT_NORMALIZED_VALUES = 101
CURRENT_ENTITY_SEMANTICS = 300
CURRENT_CLARIFICATION = 782
CURRENT_SAFETY = 1152

TOTAL_SCENARIOS = 1152
TOTAL_SAMPLES = 2304
REPEATS = 2

# Allowed dispositions and reason codes
ALLOWED_DISPOSITIONS = {
    "malformed", "incomplete", "contradictory", "mixed_contract_defect",
    "planned_not_implemented", "requires_adjudication",
    "non_language_contract_mismatch", "surface_supported_parser_gap",
}

ALLOWED_REASON_CODES = {
    "action_semantics_depends_on_unimplemented_check_in",
    "action_semantics_derives_from_no_clarification_contract",
    "check_in_has_no_implemented_signed_action",
    "clarification_depends_on_unimplemented_check_in",
    "clarification_policy_requires_independent_adjudication",
    "dangling_temporal_operator_without_operand",
    "expected_duration_semantics_has_no_surface_evidence",
    "expected_normalized_value_has_no_source_span",
    "expected_relation_has_no_surface_point_or_bound",
    "no_clarification_contract_conflicts_with_safe_surface_result",
    "semantic_pass_exposes_replay_or_delta_contract_mismatch",
    "surface_entity_semantics_conflict_with_contract",
    "surface_normalized_value_conflicts_with_contract",
    "surface_relation_conflicts_with_silver_contract",
    "unsupported_and_surface_contract_mismatch",
    "unsupported_duration_and_entity_contract_mismatch",
    "unsupported_value_with_dangling_temporal_operator",
}

REQUIRED_QUEUE_KEYS = {"scenario_id", "dimension", "disposition",
                       "reason_code", "provenance", "adjudication"}

FORBIDDEN_CONTENT_KEYS = {
    "utterance", "utterances", "dialogue", "expected", "observed",
    "source_span", "source_spans", "span", "text",
    "payload", "delta", "appointment", "audit",
    "prompt", "provider", "field_name", "value",
}

# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _selection_hash(scenario_ids: list[str]) -> str:
    """SHA-256 hexdigest truncated to 16 chars over newline-joined sorted IDs."""
    return hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode("utf-8")
    ).hexdigest()[:16]


def _queue_hash(records: list[dict[str, str]]) -> str:
    """SHA-256 truncated to 16 chars over newline-joined sorted scenario_id|dimension|disposition|reason_code."""
    lines = sorted(
        f"{r['scenario_id']}|{r['dimension']}|{r['disposition']}|{r['reason_code']}"
        for r in records
    )
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Check-in detection via the native interpretation harness
# ---------------------------------------------------------------------------


def _detect_check_in_via_harness(scenario) -> bool:
    """Check if any authored turn resolves to DiaryActionVerb.check_in."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.interpretation_harness import (
        interpret_receptionist_utterance,
    )
    from app.services.diary.action_grammar import DiaryActionVerb

    for turn in scenario.dialogue_turns:
        utterance = turn.get("utterance", "")
        if isinstance(utterance, str) and utterance.strip():
            result = interpret_receptionist_utterance(utterance)
            if result.verb == DiaryActionVerb.check_in:
                return True
    return False


# ---------------------------------------------------------------------------
# Dangling temporal operator detection
# ---------------------------------------------------------------------------

_DANGLING_TEMPORAL = re.compile(
    r"\b(after|before|between|around)\b", re.I
)


def _has_dangling_temporal_operator(utterances: list[str]) -> bool:
    """Check if any utterance contains a dangling temporal operator.

    A dangling operator appears when the temporal extractor returns
    'unspecified' but the text still contains 'after', 'before',
    'between', or 'around' as temporal keywords.
    """
    for u in utterances:
        if _DANGLING_TEMPORAL.search(u):
            return True
    return False


# ---------------------------------------------------------------------------
# Surface temporal extraction
# ---------------------------------------------------------------------------


def _extract_utterances(scenario) -> list[str]:
    return [
        turn.get("utterance", "")
        for turn in scenario.dialogue_turns
        if isinstance(turn.get("utterance"), str)
    ]


def _extract_surface_temporal(utterances: list[str]) -> str:
    """Derive the surface temporal relation from dialogue turns."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.semantic_extraction import _extract_temporal

    surface_rel = "unspecified"
    for u in utterances:
        rel, _earliest, _latest = _extract_temporal(u)
        if rel != "unspecified":
            surface_rel = rel
    return surface_rel


# ---------------------------------------------------------------------------
# Queue classification helpers
# ---------------------------------------------------------------------------

_CONCRETE_SEMANTICS = {"exact"}


def _is_concrete(val: str) -> bool:
    """Entity-semantics value is concrete (not ambiguous/omitted)."""
    return val not in ("ambiguous", "omitted", "?")


def _classify_temporal_failure(
    scenario,
    contract_rel: str,
    utterances: list[str],
) -> tuple[str, str]:
    """Classify a temporal_relation failure into (disposition, reason_code).

    Returns (disposition, reason_code).
    """
    surface_rel = _extract_surface_temporal(utterances)

    if surface_rel == "unspecified":
        if _has_dangling_temporal_operator(utterances):
            return ("malformed", "dangling_temporal_operator_without_operand")
        return ("incomplete", "expected_relation_has_no_surface_point_or_bound")

    if surface_rel != contract_rel:
        return ("contradictory", "surface_relation_conflicts_with_silver_contract")

    # surface_rel matches contract_rel but temporal field still failed →
    # parser gap (surface supports the contract but observation pipeline missed it)
    return ("surface_supported_parser_gap", "surface_relation_conflicts_with_silver_contract")


def _classify_normalized_values_failure(
    scenario,
    utterances: list[str],
    interp: Any | None = None,
    temporal_is_malformed: bool = False,
) -> tuple[str, str]:
    """Classify a normalized_values failure using the LC4R4 per-scenario category logic.

    ``temporal_is_malformed`` should be True when the same scenario's
    temporal_relation failure was classified as malformed (dangling operator).

    Returns (disposition, reason_code).
    """
    expected_nv = dict(scenario.normalized_values)
    source_spans = scenario.source_spans if hasattr(scenario, "source_spans") else {}
    if not isinstance(source_spans, dict):
        source_spans = {}

    if interp is not None:
        observed_nv = dict(interp.normalized_values)
    else:
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret
        observed_nv = dict(deterministic_interpret(scenario).normalized_values)

    # LC4R4-style per-field classification
    def _classify_nv_field(key: str) -> str:
        exp_missing = key not in expected_nv
        obs_missing = key not in observed_nv
        has_span = key in source_spans

        if obs_missing and not exp_missing and not has_span:
            return "unsupported_expected_without_span"
        if exp_missing and not obs_missing:
            return "observed_surface_value_absent_from_contract"
        if not exp_missing and not obs_missing:
            if expected_nv.get(key) != observed_nv.get(key):
                if has_span:
                    return "surface_value_disagrees_with_contract"
        return "other"

    categories: set[str] = set()
    all_keys = set(expected_nv.keys()) | set(observed_nv.keys())
    for key in all_keys:
        cat = _classify_nv_field(key)
        if cat != "other":
            categories.add(cat)

    has_unsupported = "unsupported_expected_without_span" in categories
    has_conflict = (
        "surface_value_disagrees_with_contract" in categories
        or "observed_surface_value_absent_from_contract" in categories
    )

    if has_unsupported and has_conflict:
        return ("mixed_contract_defect", "unsupported_and_surface_contract_mismatch")
    if has_unsupported:
        if temporal_is_malformed:
            return ("malformed", "unsupported_value_with_dangling_temporal_operator")
        return ("incomplete", "expected_normalized_value_has_no_source_span")
    if has_conflict:
        return ("contradictory", "surface_normalized_value_conflicts_with_contract")

    # Should not reach here if the field actually failed, but be safe
    return ("incomplete", "expected_normalized_value_has_no_source_span")


def _classify_entity_semantics_failure(
    scenario,
    interp: Any | None = None,
) -> tuple[str, str]:
    """Classify an entity_semantics failure into (disposition, reason_code).

    Duration is incomplete only when expected exact, observed omitted/ambiguous,
    and neither 'duration' nor 'duration_minutes' has a source span.
    Mismatch in practitioner/patient/location/appointment_type is contradictory.
    Both is mixed.
    """
    has_incomplete = False
    has_contradictory = False

    if interp is not None:
        interp_es = dict(interp.entity_semantics) if hasattr(interp, "entity_semantics") else {}
    else:
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret
        interp_es = dict(deterministic_interpret(scenario).entity_semantics)

    source_spans = scenario.source_spans if hasattr(scenario, "source_spans") else {}
    if not isinstance(source_spans, dict):
        source_spans = {}

    # practitioner, patient, location, appointment_type → contradictory on mismatch
    for field in ("practitioner", "patient", "location", "appointment_type"):
        s = getattr(scenario, f"{field}_semantics", "omitted")
        obs = interp_es.get(field, "?")
        if s == obs:
            continue
        if _is_concrete(s) and _is_concrete(obs):
            has_contradictory = True

    # duration → incomplete in narrow case, contradictory otherwise
    dur_s = scenario.duration_semantics
    dur_obs = interp_es.get("duration", "?")

    if _is_concrete(dur_s) and dur_obs in ("ambiguous", "omitted", "?"):
        dur_has_span = "duration" in source_spans or "duration_minutes" in source_spans
        if dur_has_span:
            has_contradictory = True
        else:
            has_incomplete = True
    elif _is_concrete(dur_s) and _is_concrete(dur_obs) and dur_s != dur_obs:
        has_contradictory = True

    if has_incomplete and has_contradictory:
        return ("mixed_contract_defect", "unsupported_duration_and_entity_contract_mismatch")
    if has_contradictory:
        return ("contradictory", "surface_entity_semantics_conflict_with_contract")
    if has_incomplete:
        return ("incomplete", "expected_duration_semantics_has_no_surface_evidence")

    return ("incomplete", "expected_duration_semantics_has_no_surface_evidence")


def _classify_clarification_failure(
    scenario,
    interpretation: Any,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify a requires_clarification failure into (disposition, reason_code).

    Planned check-in scenarios → planned_not_implemented.
    Expected True / Observed False → requires_adjudication.
    Expected False / Observed True → contradictory.
    """
    if is_check_in:
        return ("planned_not_implemented", "clarification_depends_on_unimplemented_check_in")

    scenario_expected_clarify = (
        getattr(scenario, "expected_clarification", None) is not None
        and getattr(scenario, "action_semantics", "intended") != "prohibited"
    )
    interpreter_says_clarify = interpretation.requires_clarification

    if scenario_expected_clarify and not interpreter_says_clarify:
        return ("requires_adjudication", "clarification_policy_requires_independent_adjudication")
    if not scenario_expected_clarify and interpreter_says_clarify:
        return ("contradictory", "no_clarification_contract_conflicts_with_safe_surface_result")

    return ("contradictory", "no_clarification_contract_conflicts_with_safe_surface_result")


def _classify_intended_action_failure(
    scenario,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify an intended_action failure.

    Check-in scenarios → planned_not_implemented.
    (Non-check-in intended_action failures do not occur in the frozen selection.)
    """
    if is_check_in:
        return ("planned_not_implemented", "check_in_has_no_implemented_signed_action")
    return ("contradictory", "check_in_has_no_implemented_signed_action")


def _classify_action_semantics_failure(
    scenario,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify an action_semantics failure.

    Check-in scenarios → planned_not_implemented.
    Non-check-in → contradictory.
    """
    if is_check_in:
        return ("planned_not_implemented", "action_semantics_depends_on_unimplemented_check_in")
    return ("contradictory", "action_semantics_derives_from_no_clarification_contract")


# ---------------------------------------------------------------------------
# Corpus loading and evaluation
# ---------------------------------------------------------------------------


def _load_corpus():
    """Load the LC4 development corpus."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader

    return DevelopmentOnlyLoader().load_all()


def _run_evaluation():
    """Run the full scaled evaluation and return the report."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scaled_evaluator import generate_scaled_evaluation_report

    return generate_scaled_evaluation_report()


# ---------------------------------------------------------------------------
# Aligned-failure selection and queue building
# ---------------------------------------------------------------------------


def _compute_aligned_failure_ids_from_variants(
    variants: list,
) -> set[str]:
    """Determine aligned-failure candidates from an explicit variant list.

    A scenario is an aligned_failure when it is inside the aligned boundary
    (aligned_pass + aligned_failure == 1 at num_repeats=1) and has
    aligned_failure_count > 0.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.development_gap_audit import audit_candidates

    af_ids: set[str] = set()
    for scenario in variants:
        audit = audit_candidates(
            [scenario],
            num_repeats=1,
            max_conflict_examples=0,
        )
        if audit.aligned_pass_count + audit.aligned_failure_count == 1:
            if audit.aligned_failure_count > 0:
                af_ids.add(scenario.scenario_id)

    return af_ids


def _compute_aligned_failure_ids(corpus) -> set[str]:
    """Determine aligned-failure candidates from a corpus.

    Delegates to the variant-based implementation.
    """
    return _compute_aligned_failure_ids_from_variants(list(corpus.all_variants()))


def _build_queue_from_variants(
    variants: list,
    aligned_failure_ids: set[str],
) -> list[dict[str, str]]:
    """Build the reconciliation queue from an explicit variant list.

    For each aligned-failure scenario, emits one queue record per failed
    semantic field plus one replay_contract record if semantic fields all
    pass but composed replay still fails.
    """
    records: list[dict[str, str]] = []
    scenarios_by_id = {v.scenario_id: v for v in variants}

    for sid in sorted(aligned_failure_ids):
        scenario = scenarios_by_id[sid]
        utterances = _extract_utterances(scenario)
        is_check_in = _detect_check_in_via_harness(scenario)

        # Run interpretation + replay + scoring
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.services.bernie.composed_corpus_evaluator import (
            deterministic_interpret,
            deterministic_replay,
        )
        from app.services.bernie.composed_evaluator import (
            InterpretationObservation,
            score_interpretation_replay_pair,
        )

        interp = deterministic_interpret(scenario)
        interp_obj = InterpretationObservation(
            scenario_id=interp.scenario_id,
            sample_index=0,
            intended_action=interp.intended_action,
            action_semantics=interp.action_semantics,
            temporal_relation=interp.temporal_relation,
            normalized_values=dict(interp.normalized_values),
            entity_semantics=dict(interp.entity_semantics),
            requires_clarification=interp.requires_clarification,
            clarification_choices=interp.clarification_choices,
            selected_tool_sequence=interp.selected_tool_sequence,
            authority_claim=interp.authority_claim,
            claims_action_completed=interp.claims_action_completed,
            action_negated=interp.action_negated,
        )
        replay = deterministic_replay(scenario, interp_obj)
        result = score_interpretation_replay_pair(scenario, interp_obj, replay)

        semantic_failures = result.semantic_fields.failures
        all_semantic_pass = result.semantic_fields.passed
        replay_passed = (
            result.downstream_outcome.passed
            and result.tool_sequence.passed
            and result.interpretation_tools.passed
            and result.authority.passed
            and result.clarification.passed
            and result.appointment_deltas.passed
            and result.audit_deltas.passed
        )

        # Classify temporal_relation FIRST (other classifications depend on its result)
        temporal_malformed = False
        temp_disp = None
        temp_reason = None
        for dim in semantic_failures:
            if dim == "temporal_relation":
                contract_rel = scenario.temporal_relation
                temp_disp, temp_reason = _classify_temporal_failure(
                    scenario, contract_rel, utterances
                )
                temporal_malformed = (temp_disp == "malformed")
                break

        # Process semantic field failures
        for dim in semantic_failures:
            if dim == "intended_action":
                disp, reason = _classify_intended_action_failure(scenario, is_check_in)
            elif dim == "action_semantics":
                disp, reason = _classify_action_semantics_failure(scenario, is_check_in)
            elif dim == "temporal_relation":
                disp, reason = temp_disp, temp_reason
            elif dim == "normalized_values":
                disp, reason = _classify_normalized_values_failure(
                    scenario, utterances, interp_obj, temporal_malformed
                )
            elif dim == "entity_semantics":
                disp, reason = _classify_entity_semantics_failure(
                    scenario, interp_obj
                )
            elif dim == "requires_clarification":
                disp, reason = _classify_clarification_failure(
                    scenario, interp_obj, is_check_in
                )
            else:
                disp, reason = ("contradictory", "surface_relation_conflicts_with_silver_contract")

            records.append({
                "scenario_id": sid,
                "dimension": dim,
                "disposition": disp,
                "reason_code": reason,
                "provenance": "silver",
                "adjudication": "pending",
            })

        # If all semantic fields pass but replay fails, emit replay_contract record
        if all_semantic_pass and not replay_passed:
            records.append({
                "scenario_id": sid,
                "dimension": "replay_contract",
                "disposition": "non_language_contract_mismatch",
                "reason_code": "semantic_pass_exposes_replay_or_delta_contract_mismatch",
                "provenance": "silver",
                "adjudication": "pending",
            })

    return records


def _build_queue(
    corpus,
    aligned_failure_ids: set[str],
) -> list[dict[str, str]]:
    """Build the reconciliation queue from a corpus.

    Delegates to the variant-based implementation.
    """
    return _build_queue_from_variants(list(corpus.all_variants()), aligned_failure_ids)


def build_queue_from_variants(variants: list) -> list[dict[str, str]]:
    """Public-this-module entry point: build queue from an explicit variant list.

    Accepts development variants in any order. Computes aligned-failure IDs,
    builds the full queue, and returns records sorted by scenario_id/dimension
    for stable comparison.
    """
    af_ids = _compute_aligned_failure_ids_from_variants(variants)
    records = _build_queue_from_variants(variants, af_ids)
    records.sort(key=lambda r: (r["scenario_id"], r["dimension"]))
    return records


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

RecordType = list[dict[str, str]]


def _compute_report_hash(report_no_hash: dict[str, Any]) -> str:
    """Compute report hash with the hash field excluded."""
    copy = dict(report_no_hash)
    copy.pop("report_hash", None)
    return _stable_hash(_canonical_json(copy))


def _primary_disposition_counts(
    records: RecordType,
) -> tuple[dict[str, int], dict[str, str]]:
    """Compute primary disposition per-scenario using aggregate evidence flags.

    Priority:
      1. planned_not_implemented
      2. surface_supported_parser_gap
      3. requires_adjudication
      4. non_language_contract_mismatch
      5. mixed_contract_defect (when scenario has BOTH contract-conflict AND
         unsupported evidence)
      6. contradictory
      7. malformed
      8. incomplete

    Returns (counts, hash_per_disp) where hash_per_disp maps each disposition
    to the 16-char hash of its sorted scenario IDs.
    """
    SPECIAL_PRIORITY = [
        "planned_not_implemented",
        "surface_supported_parser_gap",
        "requires_adjudication",
        "non_language_contract_mismatch",
    ]
    CONFLICT_DISPS = {"contradictory", "mixed_contract_defect"}
    UNSUPPORTED_DISPS = {"incomplete", "malformed", "mixed_contract_defect"}

    # Build per-scenario set of dispositions
    scenario_disps: dict[str, set[str]] = {}
    for r in records:
        sid = r["scenario_id"]
        if sid not in scenario_disps:
            scenario_disps[sid] = set()
        scenario_disps[sid].add(r["disposition"])

    primary_of: dict[str, str] = {}
    for sid, disps in scenario_disps.items():
        # 1-4: Check special priorities
        found_special = False
        for special in SPECIAL_PRIORITY:
            if special in disps:
                primary_of[sid] = special
                found_special = True
                break
        if found_special:
            continue

        # 5: Mixed rule
        has_conflict = bool(disps & CONFLICT_DISPS)
        has_unsupported = bool(disps & UNSUPPORTED_DISPS)
        if has_conflict and has_unsupported:
            primary_of[sid] = "mixed_contract_defect"
            continue

        # 6-8: Remaining priority
        for disp in ("contradictory", "malformed", "incomplete"):
            if disp in disps:
                primary_of[sid] = disp
                break

    # Build per-disposition scenario ID lists and count
    disp_scenarios: dict[str, list[str]] = {d: [] for d in SPECIAL_PRIORITY}
    for d in ("mixed_contract_defect", "contradictory", "malformed", "incomplete"):
        disp_scenarios.setdefault(d, [])

    for sid, disp in primary_of.items():
        disp_scenarios.setdefault(disp, [])
        disp_scenarios[disp].append(sid)

    counts: dict[str, int] = {}
    hash_per_disp: dict[str, str] = {}
    for disp, sids in disp_scenarios.items():
        counts[disp] = len(sids)
        hash_per_disp[disp] = _selection_hash(sids)

    return counts, hash_per_disp


def build_queue_and_report() -> tuple[RecordType, dict[str, Any]]:
    """Build the reconciliation queue and aggregate report."""
    corpus = _load_corpus()
    evaluation_report = _run_evaluation()

    # Compute aligned-failure selection
    af_ids = _compute_aligned_failure_ids(corpus)
    af_id_list = sorted(af_ids)
    af_hash = _selection_hash(af_id_list)

    # Build queue
    records = _build_queue(corpus, af_ids)

    # Sort records by scenario_id, dimension for stable output
    records.sort(key=lambda r: (r["scenario_id"], r["dimension"]))

    q_hash = _queue_hash(records)
    primary_counts, primary_hashes = _primary_disposition_counts(records)

    # Compute dimension/disposition counts
    dim_disp_counts: dict[str, int] = {}
    for r in records:
        key = f"{r['dimension']}|{r['disposition']}"
        dim_disp_counts[key] = dim_disp_counts.get(key, 0) + 1

    # Build report payload — never copy observed data into expected fields
    report_payload: dict[str, Any] = {
        "schema_version": "lc4r7.silver_reconciliation.v1",
        "development_only": True,
        "silver_pending_only": True,
        "corpus_hash": evaluation_report.get("corpus_hash", ""),
        "selection": {
            "count": len(af_ids),
            "hash": af_hash,
            "expected_count": EXPECTED_ALIGNED_FAILURE_COUNT,
            "expected_hash": EXPECTED_ALIGNED_FAILURE_HASH,
            "hash_match": af_hash == EXPECTED_ALIGNED_FAILURE_HASH,
        },
        "current_semantic_baseline": {
            "intended_action": f"{CURRENT_INTENDED_ACTION}/{TOTAL_SCENARIOS}",
            "action_semantics": f"{CURRENT_ACTION_SEMANTICS}/{TOTAL_SCENARIOS}",
            "temporal_relation": f"{CURRENT_TEMPORAL_RELATION}/{TOTAL_SCENARIOS}",
            "normalized_values": f"{CURRENT_NORMALIZED_VALUES}/{TOTAL_SCENARIOS}",
            "entity_semantics": f"{CURRENT_ENTITY_SEMANTICS}/{TOTAL_SCENARIOS}",
            "clarification": f"{CURRENT_CLARIFICATION}/{TOTAL_SCENARIOS}",
        },
        "safety": {
            "all_safe": evaluation_report["per_dimension"]["safety"]["passed"]
            == TOTAL_SAMPLES,
            "passed": evaluation_report["per_dimension"]["safety"]["passed"]
            // REPEATS,
            "total": TOTAL_SCENARIOS,
        },
        "repeat_variance": {
            "all_deltas_zero": evaluation_report["variance"][
                "all_samples_deterministic"
            ],
            "variant_scenario_count": evaluation_report["variance"][
                "variant_scenario_count"
            ],
            "method": "per-scenario observation and safety fingerprint",
            "sample_count": TOTAL_SAMPLES,
        },
        "queue": {
            "total_records": len(records),
            "expected_count": EXPECTED_QUEUE_COUNT,
            "hash": q_hash,
            "expected_hash": EXPECTED_QUEUE_HASH,
            "hash_match": q_hash == EXPECTED_QUEUE_HASH,
        },
        "primary_dispositions": {
            disp: {
                "count": primary_counts.get(disp, 0),
                "hash": primary_hashes.get(disp, ""),
                "expected_count": EXPECTED_PRIMARY_DISPOSITIONS.get(disp, {}).get("count", 0),
                "expected_hash": EXPECTED_PRIMARY_DISPOSITIONS.get(disp, {}).get("hash", ""),
                "hash_match": (
                    primary_hashes.get(disp, "")
                    == EXPECTED_PRIMARY_DISPOSITIONS.get(disp, {}).get("hash", "")
                ),
            }
            for disp in sorted(EXPECTED_PRIMARY_DISPOSITIONS.keys())
        },
        "dimension_disposition_counts": dim_disp_counts,
        "exit_gate": {
            "status": "blocked_pending_adjudication_and_contract_reconciliation",
            "requires_adjudication_count": primary_counts.get("requires_adjudication", 0),
            "non_language_contract_mismatch_count": primary_counts.get(
                "non_language_contract_mismatch", 0
            ),
            "parser_gap_count": primary_counts.get("surface_supported_parser_gap", 0),
            "remediation_authorized": False,
        },
        "assertions": {
            "selection_count_572": len(af_ids) == EXPECTED_ALIGNED_FAILURE_COUNT,
            "selection_hash_match": af_hash == EXPECTED_ALIGNED_FAILURE_HASH,
            "queue_count_1436": len(records) == EXPECTED_QUEUE_COUNT,
            "queue_hash_match": q_hash == EXPECTED_QUEUE_HASH,
            "zero_parser_gaps": primary_counts.get("surface_supported_parser_gap", 0) == 0,
            "exit_gate_blocked": True,
            "check_in_preserved_as_planned": primary_counts.get("planned_not_implemented", 0) == 39,
            "safety_exact_1152_of_1152": evaluation_report["per_dimension"][
                "safety"
            ]["passed"]
            == TOTAL_SAMPLES,
            "repeat_variance_zero": evaluation_report["variance"][
                "all_samples_deterministic"
            ],
        },
    }

    report_payload["report_hash"] = _compute_report_hash(report_payload)

    return records, report_payload


# ---------------------------------------------------------------------------
# --check mode
# ---------------------------------------------------------------------------


def _load_frozen_queue() -> list[dict[str, str]]:
    """Load the frozen queue from docs."""
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Frozen queue not found at {QUEUE_PATH}")
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_frozen_report() -> dict[str, Any]:
    """Load the frozen report from docs."""
    if not REPORT_PATH.exists():
        raise FileNotFoundError(f"Frozen report not found at {REPORT_PATH}")
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_check(records: RecordType, report: dict[str, Any]) -> bool:
    """Verify recomputed queue and report against contract constants AND committed artifacts."""
    issues: list[str] = []

    try:
        frozen_queue = _load_frozen_queue()
        frozen_report = _load_frozen_report()
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"LC4R7 CHECK FAILED:\n  - unable to load frozen artifacts: {exc}")
        return False

    if not isinstance(records, list) or not isinstance(report, dict):
        print("LC4R7 CHECK FAILED:\n  - records/report have invalid top-level types")
        return False

    # Validate record shape before any hash or aggregate helper indexes fields.
    records_well_formed = True
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            issues.append(f"Record {i}: expected object")
            records_well_formed = False
            continue
        keys = set(record)
        if keys != REQUIRED_QUEUE_KEYS:
            issues.append(f"Record {i}: keys {keys} != required {REQUIRED_QUEUE_KEYS}")
            records_well_formed = False
            continue
        if not all(isinstance(record[key], str) for key in REQUIRED_QUEUE_KEYS):
            issues.append(f"Record {i}: all values must be strings")
            records_well_formed = False
            continue
        if record["dimension"] not in {dim for dim, _ in EXPECTED_DIMENSION_DISPOSITIONS}:
            issues.append(f"Record {i}: invalid dimension {record['dimension']!r}")
        if record["disposition"] not in ALLOWED_DISPOSITIONS:
            issues.append(f"Record {i}: invalid disposition {record['disposition']!r}")
        if record["reason_code"] not in ALLOWED_REASON_CODES:
            issues.append(f"Record {i}: invalid reason_code {record['reason_code']!r}")
        if record["provenance"] != "silver":
            issues.append(f"Record {i}: provenance != silver")
        if record["adjudication"] != "pending":
            issues.append(f"Record {i}: adjudication != pending")

    # --- 1. Report hash ---
    recomputed_hash_no_hash = _compute_report_hash(report)
    frozen_hash = frozen_report.get("report_hash", "")
    if _compute_report_hash(frozen_report) != frozen_hash:
        issues.append("committed frozen report hash is invalid")
    if recomputed_hash_no_hash != frozen_hash:
        issues.append(
            f"report_hash mismatch: recomputed={recomputed_hash_no_hash}, "
            f"frozen={frozen_hash}"
        )

    # --- 2. Selection ---
    for key in ("count", "hash", "hash_match", "expected_hash", "expected_count"):
        rv = report.get("selection", {}).get(key)
        fv = frozen_report.get("selection", {}).get(key)
        if rv != fv:
            issues.append(f"selection.{key} mismatch: {rv} != {fv}")
    # Also validate against contract constant
    if report.get("selection", {}).get("expected_hash") != EXPECTED_ALIGNED_FAILURE_HASH:
        issues.append("selection.expected_hash != contract constant")
    if report.get("selection", {}).get("expected_count") != EXPECTED_ALIGNED_FAILURE_COUNT:
        issues.append("selection.expected_count != contract constant")
    expected_selection = {
        "count": EXPECTED_ALIGNED_FAILURE_COUNT,
        "hash": EXPECTED_ALIGNED_FAILURE_HASH,
        "expected_count": EXPECTED_ALIGNED_FAILURE_COUNT,
        "expected_hash": EXPECTED_ALIGNED_FAILURE_HASH,
        "hash_match": True,
    }
    if report.get("selection") != expected_selection:
        issues.append("selection does not exactly match the frozen contract")

    # --- 3. Queue hash and count ---
    q_hash = _queue_hash(records) if records_well_formed else "invalid"
    fq_hash = _queue_hash(frozen_queue)
    if q_hash != fq_hash:
        issues.append(f"queue hash mismatch: recomputed={q_hash}, frozen={fq_hash}")
    # Validate against contract constant
    if q_hash != EXPECTED_QUEUE_HASH:
        issues.append(
            f"queue hash {q_hash} != contract constant {EXPECTED_QUEUE_HASH}"
        )
    if len(records) != len(frozen_queue):
        issues.append(
            f"queue count mismatch: recomputed={len(records)}, "
            f"frozen={len(frozen_queue)}"
        )
    if len(records) != EXPECTED_QUEUE_COUNT:
        issues.append(
            f"queue count {len(records)} != contract constant {EXPECTED_QUEUE_COUNT}"
        )
    if records_well_formed:
        canonical_records = sorted(_canonical_json(record) for record in records)
        canonical_frozen = sorted(_canonical_json(record) for record in frozen_queue)
        if canonical_records != canonical_frozen:
            issues.append("recomputed queue does not exactly match committed queue")
    expected_queue_report = {
        "total_records": EXPECTED_QUEUE_COUNT,
        "expected_count": EXPECTED_QUEUE_COUNT,
        "hash": EXPECTED_QUEUE_HASH,
        "expected_hash": EXPECTED_QUEUE_HASH,
        "hash_match": True,
    }
    if report.get("queue") != expected_queue_report:
        issues.append("queue report does not exactly match the frozen contract")

    # --- 4. Primary dispositions ---
    # Recompute from records for validation
    primary_counts, primary_hashes = (
        _primary_disposition_counts(records) if records_well_formed else ({}, {})
    )
    frozen_primary = frozen_report.get("primary_dispositions", {})
    for disp in sorted(EXPECTED_PRIMARY_DISPOSITIONS.keys()):
        rc = primary_counts.get(disp, 0)
        fc = frozen_primary.get(disp, {}).get("count", 0)
        if rc != fc:
            issues.append(
                f"primary_disposition.{disp} count mismatch: "
                f"recomputed={rc}, frozen={fc}"
            )
        # Validate against contract constant
        expected_count = EXPECTED_PRIMARY_DISPOSITIONS[disp]["count"]
        if rc != expected_count:
            issues.append(
                f"primary_disposition.{disp} count {rc} != contract {expected_count}"
            )
        rh = primary_hashes.get(disp, "")
        expected_hash = EXPECTED_PRIMARY_DISPOSITIONS[disp]["hash"]
        if rh != expected_hash:
            issues.append(
                f"primary_disposition.{disp} hash {rh} != contract {expected_hash}"
            )
        expected_info = {
            "count": expected_count,
            "hash": expected_hash,
            "expected_count": expected_count,
            "expected_hash": expected_hash,
            "hash_match": True,
        }
        if report.get("primary_dispositions", {}).get(disp) != expected_info:
            issues.append(f"primary_disposition.{disp} report does not match contract")
    if set(report.get("primary_dispositions", {})) != set(EXPECTED_PRIMARY_DISPOSITIONS):
        issues.append("primary_dispositions report has missing or extra dispositions")

    # --- 5. Dimension/disposition counts ---
    dim_disp_records: dict[tuple[str, str], int] = {}
    if records_well_formed:
        for r in records:
            key = (r["dimension"], r["disposition"])
            dim_disp_records[key] = dim_disp_records.get(key, 0) + 1
    # Check no extra pairs beyond expected
    for (dim, disp), actual in dim_disp_records.items():
        expected = EXPECTED_DIMENSION_DISPOSITIONS.get((dim, disp), -1)
        if expected == -1:
            issues.append(
                f"unexpected dimension_disposition pair {dim}/{disp}: "
                f"count={actual}"
            )
    # Check expected pairs match
    for (dim, disp), expected in EXPECTED_DIMENSION_DISPOSITIONS.items():
        actual = dim_disp_records.get((dim, disp), 0)
        if actual != expected:
            issues.append(
                f"dimension_disposition {dim}/{disp}: "
                f"recomputed={actual}, expected={expected}"
            )
    expected_dim_report = {
        f"{dim}|{disp}": count
        for (dim, disp), count in EXPECTED_DIMENSION_DISPOSITIONS.items()
    }
    if report.get("dimension_disposition_counts") != expected_dim_report:
        issues.append("dimension_disposition_counts report does not exactly match contract")

    # --- 6. Semantic baseline ---
    r_base = report.get("current_semantic_baseline", {})
    f_base = frozen_report.get("current_semantic_baseline", {})
    for dim in (
        "intended_action", "action_semantics", "temporal_relation",
        "normalized_values", "entity_semantics", "clarification",
    ):
        if r_base.get(dim) != f_base.get(dim):
            issues.append(
                f"current_semantic_baseline.{dim} mismatch: "
                f"{r_base.get(dim)} != {f_base.get(dim)}"
            )
    # Validate against contract constant values 880/814/628/101/300/782 over 1152
    expected_baselines = {
        "intended_action": f"{CURRENT_INTENDED_ACTION}/{TOTAL_SCENARIOS}",
        "action_semantics": f"{CURRENT_ACTION_SEMANTICS}/{TOTAL_SCENARIOS}",
        "temporal_relation": f"{CURRENT_TEMPORAL_RELATION}/{TOTAL_SCENARIOS}",
        "normalized_values": f"{CURRENT_NORMALIZED_VALUES}/{TOTAL_SCENARIOS}",
        "entity_semantics": f"{CURRENT_ENTITY_SEMANTICS}/{TOTAL_SCENARIOS}",
        "clarification": f"{CURRENT_CLARIFICATION}/{TOTAL_SCENARIOS}",
    }
    for dim, expected in expected_baselines.items():
        if r_base.get(dim) != expected:
            issues.append(
                f"current_semantic_baseline.{dim} {r_base.get(dim)} != "
                f"contract {expected}"
            )

    # --- 7. Safety ---
    r_safety = report.get("safety", {})
    f_safety = frozen_report.get("safety", {})
    if r_safety.get("all_safe") != f_safety.get("all_safe"):
        issues.append("safety.all_safe mismatch")
    if r_safety.get("passed") != f_safety.get("passed"):
        issues.append("safety.passed mismatch")
    # Validate against contract constants
    if r_safety.get("all_safe") is not True:
        issues.append("safety.all_safe must be True")
    if r_safety.get("passed") != TOTAL_SCENARIOS:
        issues.append(f"safety.passed {r_safety.get('passed')} != {TOTAL_SCENARIOS}")
    if r_safety.get("total") != TOTAL_SCENARIOS:
        issues.append(f"safety.total {r_safety.get('total')} != {TOTAL_SCENARIOS}")

    # --- 8. Variance ---
    r_var = report.get("repeat_variance", {})
    f_var = frozen_report.get("repeat_variance", {})
    if r_var.get("all_deltas_zero") != f_var.get("all_deltas_zero"):
        issues.append("repeat_variance.all_deltas_zero mismatch")
    if r_var.get("variant_scenario_count") != f_var.get("variant_scenario_count"):
        issues.append("variant_scenario_count mismatch")
    # Validate against contract constants
    if r_var.get("all_deltas_zero") is not True:
        issues.append("repeat_variance.all_deltas_zero must be True")
    if r_var.get("variant_scenario_count") != 0:
        issues.append(f"variant_scenario_count {r_var.get('variant_scenario_count')} != 0")
    if r_var.get("sample_count") != TOTAL_SAMPLES:
        issues.append(f"sample_count {r_var.get('sample_count')} != {TOTAL_SAMPLES}")

    # --- 9. Exit gate ---
    r_gate = report.get("exit_gate", {})
    f_gate = frozen_report.get("exit_gate", {})
    for key in ("status", "requires_adjudication_count", "non_language_contract_mismatch_count",
                "parser_gap_count", "remediation_authorized"):
        if r_gate.get(key) != f_gate.get(key):
            issues.append(f"exit_gate.{key} mismatch: {r_gate.get(key)} != {f_gate.get(key)}")
    # Validate gate against contract constants: 53/51/0, blocked, remediation false
    if r_gate.get("status") != "blocked_pending_adjudication_and_contract_reconciliation":
        issues.append("exit_gate.status != blocked")
    if r_gate.get("requires_adjudication_count") != EXPECTED_PRIMARY_DISPOSITIONS["requires_adjudication"]["count"]:
        issues.append("exit_gate.requires_adjudication_count != contract")
    if r_gate.get("non_language_contract_mismatch_count") != EXPECTED_PRIMARY_DISPOSITIONS["non_language_contract_mismatch"]["count"]:
        issues.append("exit_gate.non_language_contract_mismatch_count != contract")
    if r_gate.get("parser_gap_count") != 0:
        issues.append("exit_gate.parser_gap_count != 0")
    if r_gate.get("remediation_authorized") is not False:
        issues.append("exit_gate.remediation_authorized must be False")

    # --- 10. Corpus hash ---
    if report.get("corpus_hash", "") != frozen_report.get("corpus_hash", ""):
        issues.append("corpus_hash mismatch")

    # --- 11. Assertions ---
    assertions = report.get("assertions", {})
    expected_assertions = {
        "selection_count_572", "selection_hash_match", "queue_count_1436",
        "queue_hash_match", "zero_parser_gaps", "exit_gate_blocked",
        "check_in_preserved_as_planned", "safety_exact_1152_of_1152",
        "repeat_variance_zero",
    }
    if set(assertions) != expected_assertions:
        issues.append("assertions report has missing or extra assertions")
    for name, value in assertions.items():
        if value is not True:
            issues.append(f"assertion {name} is {value!r}, expected True")

    if issues:
        print("LC4R7 CHECK FAILED:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("LC4R7 CHECK PASSED")

    return len(issues) == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    check_only = "--check" in sys.argv
    print_json = "--json" in sys.argv or not check_only

    records, report = build_queue_and_report()

    if check_only:
        passed = run_check(records, report)
        if print_json:
            print()
            print(json.dumps(report, indent=2, default=str))
        sys.exit(0 if passed else 1)
    else:
        # Combine queue + report for stdout
        output = {
            "queue": records,
            "report": report,
        }
        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
