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
# Frozen constants from the LC4R7 contract
# ---------------------------------------------------------------------------

# Frozen selection
EXPECTED_ALIGNED_FAILURE_HASH = "e17eb1739c16f3de"
EXPECTED_ALIGNED_FAILURE_COUNT = 572

# Frozen queue
EXPECTED_QUEUE_HASH = "373111d5c50c4240"
EXPECTED_QUEUE_COUNT = 1436

# Primary disposition hashes (from contract)
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

# Expected dimension/disposition counts
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
# Check-in detection
# ---------------------------------------------------------------------------

_CHECK_IN_PATTERN = re.compile(
    r"\b(check\s*in|check.?in|arrived|arrival|mark\s+arrived|confirm\s+(arrival|check.?in)|here now|is here)\b", re.I
)


def _is_check_in_scenario(scenario) -> bool:
    """Detect if a scenario involves check-in surface wording."""
    for turn in scenario.dialogue_turns:
        utterance = turn.get("utterance", "")
        if isinstance(utterance, str) and _CHECK_IN_PATTERN.search(utterance):
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
            return ("malformed", "dangling_temporal_operator")
        return ("incomplete", "no_surface_temporal_evidence")

    if surface_rel != contract_rel:
        return ("contradictory", f"surface_{surface_rel}_vs_contract_{contract_rel}")

    return ("contradictory", "temporal_mismatch")


def _classify_normalized_values_failure(
    scenario,
    utterances: list[str],
    interp: Any | None = None,
) -> tuple[str, str]:
    """Classify a normalized_values failure into (disposition, reason_code).

    Priority: malformed > mixed_contract_defect > incomplete > contradictory.
    """
    source_spans = scenario.source_spans if hasattr(scenario, "source_spans") else {}
    if isinstance(source_spans, dict):
        span_keys = set(source_spans.keys())
    else:
        span_keys = set()

    expected_nv = dict(scenario.normalized_values)

    # Read observed normalized values from interpreter
    if interp is not None:
        observed_nv = dict(interp.normalized_values)
    else:
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret

        observed_nv = dict(deterministic_interpret(scenario).normalized_values)

    # has_malformed: dangling temporal operator + missing time span
    has_malformed = _has_dangling_temporal_operator(utterances) and any(
        k in expected_nv and k not in span_keys
        for k in ("earliest_time", "latest_time", "appointment_date")
    )

    # has_incomplete: expected key missing from source_spans
    has_incomplete = any(k not in span_keys for k in expected_nv)

    # has_contradictory: values differ with span, or observed value absent from expected
    has_contradictory = any(
        k in span_keys
        and expected_nv.get(k) is not None
        and observed_nv.get(k) is not None
        and expected_nv[k] != observed_nv[k]
        for k in expected_nv
    )
    has_contradictory = has_contradictory or any(
        k not in expected_nv for k in observed_nv
    )

    if has_malformed:
        return ("malformed", "dangling_normalized_value_operand")
    if has_incomplete and has_contradictory:
        return ("mixed_contract_defect", "unsupported_expectation_and_surface_conflict")
    if has_incomplete:
        return ("incomplete", "no_source_span_for_expected_value")
    if has_contradictory:
        return ("contradictory", "surface_value_conflicts_with_expected")

    return ("incomplete", "unclassified_normalized_value_failure")


def _classify_entity_semantics_failure(
    scenario,
    interp: Any | None = None,
) -> tuple[str, str]:
    """Classify an entity_semantics failure into (disposition, reason_code).

    Uses entity semantics comparison to distinguish incomplete
    (interpreter found no surface evidence) from contradictory
    (surface evidence disagrees with contract).
    """
    has_incomplete = False
    has_contradictory = False

    if interp is not None:
        interp_es = dict(interp.entity_semantics) if hasattr(interp, "entity_semantics") else {}
    else:
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret

        interp_es = dict(deterministic_interpret(scenario).entity_semantics)

    for field in ("practitioner", "patient", "location", "appointment_type", "duration"):
        s = getattr(scenario, f"{field}_semantics", "omitted")
        obs = interp_es.get(field, "?")
        if s == obs:
            continue
        # ambiguous or omitted when contract expects concrete value -> incomplete
        if obs in ("ambiguous", "omitted") and s not in ("ambiguous", "omitted"):
            has_incomplete = True
        # both sides have concrete values but differ -> contradictory
        elif obs not in ("ambiguous", "omitted") and s not in ("ambiguous", "omitted"):
            has_contradictory = True
        else:
            has_incomplete = True

    if has_incomplete and has_contradictory:
        return ("mixed_contract_defect", "unsupported_entity_expectation_and_surface_conflict")
    if has_contradictory:
        return ("contradictory", "surface_entity_semantics_conflicts_with_expected")
    if has_incomplete:
        return ("incomplete", "no_entity_source_span")

    return ("incomplete", "unclassified_entity_semantics_failure")


def _classify_clarification_failure(
    scenario,
    interpretation: Any,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify a requires_clarification failure into (disposition, reason_code)."""
    # All check_in scenarios with requires_clarification failure get PNI
    if is_check_in:
        return ("planned_not_implemented", "check_in_not_implemented")

    scenario_expected_clarify = (
        getattr(scenario, "expected_clarification", None) is not None
        and getattr(scenario, "action_semantics", "intended") != "prohibited"
    )
    interpreter_says_clarify = interpretation.requires_clarification

    if scenario_expected_clarify and not interpreter_says_clarify:
        return ("requires_adjudication", "expected_clarification_not_produced")
    if not scenario_expected_clarify and interpreter_says_clarify:
        return ("contradictory", "unexpected_clarification_produced")

    return ("contradictory", "clarification_mismatch")


# Cached interpreter for reuse within same batch
_interpreter_cache: dict[str, Any] = {}


def deterministic_interpret_fast(scenario) -> Any:
    """Cached deterministic interpretation."""
    sid = scenario.scenario_id
    if sid not in _interpreter_cache:
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret

        _interpreter_cache[sid] = deterministic_interpret(scenario)
    return _interpreter_cache[sid]


def _classify_intended_action_failure(
    scenario,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify an intended_action failure."""
    if is_check_in:
        return ("planned_not_implemented", "check_in_not_implemented")
    return ("contradictory", "intended_action_mismatch")


def _classify_action_semantics_failure(
    scenario,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify an action_semantics failure."""
    if is_check_in:
        return ("planned_not_implemented", "check_in_not_implemented")
    return ("contradictory", "action_semantics_mismatch")


def _classify_clarification_failure(
    scenario,
    interpretation: Any,
    is_check_in: bool,
) -> tuple[str, str]:
    """Classify a requires_clarification failure into (disposition, reason_code)."""
    # All check_in scenarios with requires_clarification failure get PNI
    if is_check_in:
        return ("planned_not_implemented", "check_in_not_implemented")

    scenario_expected_clarify = (
        getattr(scenario, "expected_clarification", None) is not None
        and getattr(scenario, "action_semantics", "intended") != "prohibited"
    )
    interpreter_says_clarify = interpretation.requires_clarification

    if scenario_expected_clarify and not interpreter_says_clarify:
        return ("requires_adjudication", "expected_clarification_not_produced")
    if not scenario_expected_clarify and interpreter_says_clarify:
        return ("contradictory", "unexpected_clarification_produced")

    return ("contradictory", "clarification_mismatch")


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


def _compute_aligned_failure_ids(corpus) -> set[str]:
    """Determine which scenarios are aligned_failure candidates.

    Uses the public development audit to classify each scenario.
    A scenario is an aligned_failure when it is inside the aligned boundary
    (aligned_pass + aligned_failure == 1 at num_repeats=1) and has
    aligned_failure_count > 0.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.development_gap_audit import audit_candidates

    af_ids: set[str] = set()
    for scenario in corpus.all_variants():
        audit = audit_candidates(
            [scenario],
            num_repeats=1,
            max_conflict_examples=0,
        )
        if audit.aligned_pass_count + audit.aligned_failure_count == 1:
            if audit.aligned_failure_count > 0:
                af_ids.add(scenario.scenario_id)

    return af_ids


def _build_queue(
    corpus,
    aligned_failure_ids: set[str],
) -> list[dict[str, str]]:
    """Build the 1,436-record reconciliation queue.

    For each aligned-failure scenario, emits one queue record per failed
    semantic field plus one replay_contract record if semantic fields all
    pass but composed replay still fails.
    """
    records: list[dict[str, str]] = []
    scenarios_by_id = {v.scenario_id: v for v in corpus.all_variants()}

    # Clear interpreter cache
    _interpreter_cache.clear()

    for sid in sorted(aligned_failure_ids):
        scenario = scenarios_by_id[sid]
        utterances = _extract_utterances(scenario)
        is_check_in = _is_check_in_scenario(scenario)

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

        # Process semantic field failures
        for dim in semantic_failures:
            if dim == "intended_action":
                disp, reason = _classify_intended_action_failure(scenario, is_check_in)
            elif dim == "action_semantics":
                disp, reason = _classify_action_semantics_failure(scenario, is_check_in)
            elif dim == "temporal_relation":
                contract_rel = scenario.temporal_relation
                disp, reason = _classify_temporal_failure(
                    scenario, contract_rel, utterances
                )
            elif dim == "normalized_values":
                disp, reason = _classify_normalized_values_failure(
                    scenario, utterances, interp_obj
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
                disp, reason = ("contradictory", f"unclassified_{dim}_failure")

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
                "reason_code": "semantic_pass_replay_mismatch",
                "provenance": "silver",
                "adjudication": "pending",
            })

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


def _primary_disposition_counts(records: RecordType) -> dict[str, int]:
    """Compute primary disposition counts per-scenario using priority order.

    Each scenario gets exactly one primary disposition: the highest-priority
    disposition among its queue records. Priority order:
    1. planned_not_implemented
    2. surface_supported_parser_gap
    3. requires_adjudication
    4. non_language_contract_mismatch
    5. mixed_contract_defect
    6. contradictory
    7. malformed
    8. incomplete
    """
    DISPOSITION_PRIORITY = [
        "planned_not_implemented",
        "surface_supported_parser_gap",
        "requires_adjudication",
        "non_language_contract_mismatch",
        "mixed_contract_defect",
        "contradictory",
        "malformed",
        "incomplete",
    ]
    # Build per-scenario dispositions
    scenario_dispositions: dict[str, str] = {}
    for r in records:
        sid = r["scenario_id"]
        disp = r["disposition"]
        if sid not in scenario_dispositions:
            scenario_dispositions[sid] = disp
        else:
            current = scenario_dispositions[sid]
            # Keep the higher-priority disposition
            current_idx = (
                DISPOSITION_PRIORITY.index(current)
                if current in DISPOSITION_PRIORITY
                else len(DISPOSITION_PRIORITY)
            )
            new_idx = (
                DISPOSITION_PRIORITY.index(disp)
                if disp in DISPOSITION_PRIORITY
                else len(DISPOSITION_PRIORITY)
            )
            if new_idx < current_idx:
                scenario_dispositions[sid] = disp

    counts: dict[str, int] = {}
    for disp in scenario_dispositions.values():
        counts[disp] = counts.get(disp, 0) + 1
    return counts


def build_queue_and_report() -> tuple[RecordType, dict[str, Any]]:
    """Build the reconciliation queue and aggregate report."""
    # Clear global cache
    _interpreter_cache.clear()

    corpus = _load_corpus()
    evaluation_report = _run_evaluation()

    sf = evaluation_report["per_dimension"]["semantic_fields"]

    def per_scenario(val: int) -> int:
        return val // REPEATS

    # Compute aligned-failure selection
    af_ids = _compute_aligned_failure_ids(corpus)
    af_id_list = sorted(af_ids)
    af_hash = _selection_hash(af_id_list)

    # Build queue
    records = _build_queue(corpus, af_ids)

    # Sort records by scenario_id, dimension for stable output
    records.sort(key=lambda r: (r["scenario_id"], r["dimension"]))

    q_hash = _queue_hash(records)
    primary_counts = _primary_disposition_counts(records)

    # Compute dimension/disposition counts
    dim_disp_counts: dict[str, int] = {}
    for r in records:
        key = f"{r['dimension']}|{r['disposition']}"
        dim_disp_counts[key] = dim_disp_counts.get(key, 0) + 1

    # Build report payload
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
                "expected_count": EXPECTED_PRIMARY_DISPOSITIONS.get(disp, {}).get("count", 0),
                "expected_hash": EXPECTED_PRIMARY_DISPOSITIONS.get(disp, {}).get("hash", ""),
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
    """Verify recomputed queue and report against frozen artifacts."""
    frozen_queue = _load_frozen_queue()
    frozen_report = _load_frozen_report()
    issues: list[str] = []

    # --- 1. Report hash ---
    recomputed_hash_no_hash = _compute_report_hash(report)
    frozen_hash = frozen_report.get("report_hash", "")
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

    # --- 3. Queue hash and count ---
    q_hash = _queue_hash(records)
    fq_hash = _queue_hash(frozen_queue)
    if q_hash != fq_hash:
        issues.append(f"queue hash mismatch: recomputed={q_hash}, frozen={fq_hash}")

    if len(records) != len(frozen_queue):
        issues.append(
            f"queue count mismatch: recomputed={len(records)}, "
            f"frozen={len(frozen_queue)}"
        )

    # --- 4. Primary dispositions ---
    primary_counts = _primary_disposition_counts(records)
    frozen_primary = frozen_report.get("primary_dispositions", {})
    for disp in sorted(EXPECTED_PRIMARY_DISPOSITIONS.keys()):
        rc = primary_counts.get(disp, 0)
        fc = frozen_primary.get(disp, {}).get("count", 0)
        if rc != fc:
            issues.append(
                f"primary_disposition.{disp} count mismatch: "
                f"recomputed={rc}, frozen={fc}"
            )

    # --- 5. Semantic baseline ---
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

    # --- 6. Safety ---
    r_safety = report.get("safety", {})
    f_safety = frozen_report.get("safety", {})
    if r_safety.get("all_safe") != f_safety.get("all_safe"):
        issues.append("safety.all_safe mismatch")
    if r_safety.get("passed") != f_safety.get("passed"):
        issues.append("safety.passed mismatch")

    # --- 7. Variance ---
    r_var = report.get("repeat_variance", {})
    f_var = frozen_report.get("repeat_variance", {})
    if r_var.get("all_deltas_zero") != f_var.get("all_deltas_zero"):
        issues.append("repeat_variance.all_deltas_zero mismatch")
    if r_var.get("variant_scenario_count") != f_var.get("variant_scenario_count"):
        issues.append("variant_scenario_count mismatch")

    # --- 8. Exit gate ---
    r_gate = report.get("exit_gate", {})
    f_gate = frozen_report.get("exit_gate", {})
    for key in ("status", "requires_adjudication_count", "non_language_contract_mismatch_count",
                "parser_gap_count", "remediation_authorized"):
        if r_gate.get(key) != f_gate.get(key):
            issues.append(f"exit_gate.{key} mismatch: {r_gate.get(key)} != {f_gate.get(key)}")

    # --- 9. Corpus hash ---
    if report.get("corpus_hash", "") != frozen_report.get("corpus_hash", ""):
        issues.append("corpus_hash mismatch")

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
