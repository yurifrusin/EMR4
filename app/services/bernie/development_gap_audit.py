"""Development-only candidate-quality firewall for LC4R2.

Separates replay/interpretation failures into four deterministic categories:

- ``aligned_pass``: surface evidence supports the candidate contract and the
  interpreter/replay agrees (all dimensions pass).
- ``aligned_failure``: surface evidence supports the candidate contract but the
  interpreter/replay still disagrees (a genuine gap).
- ``surface_contract_conflict``: explicit action, temporal operator, point/bound,
  duration, correction, or negation evidence contradicts the Silver label.
- ``unsupported_or_ambiguous_surface``: the bounded parser cannot establish
  which side is correct.

Every conflict record carries a deterministic rule ID, uses only bounded
development case IDs, and emits safe authored-synthetic excerpts (capped).

The audit never feeds labels back into interpretation or replay.  Aggregate
counts are stable under shuffled input.

No protected holdout, provider, route, database, or write surface is accessed.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal, Union

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    InterpretationObservation,
    ReplayObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.corpus_tier import CorpusCandidate
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Audit category literals
# ---------------------------------------------------------------------------

AuditCategory = Literal[
    "aligned_pass",
    "aligned_failure",
    "surface_contract_conflict",
    "unsupported_or_ambiguous_surface",
]

# ---------------------------------------------------------------------------
# Deterministic rule IDs
# ---------------------------------------------------------------------------

RULE_ACTION_MISMATCH = "CONFLICT-ACT-001"
RULE_TEMPORAL_MISMATCH = "CONFLICT-TMP-001"
RULE_NEGATION_MISMATCH = "CONFLICT-NEG-001"
RULE_CORRECTION_MISMATCH = "CONFLICT-COR-001"
RULE_DURATION_MISMATCH = "CONFLICT-DUR-001"
RULE_ENTITY_MISMATCH = "CONFLICT-ENT-001"
RULE_CLARIFICATION_MISMATCH = "CONFLICT-CLR-001"
RULE_AUTHORITY_MISMATCH = "CONFLICT-AUT-001"
RULE_AMBIGUOUS_SURFACE = "CONFLICT-AMB-001"

# ---------------------------------------------------------------------------
# Audit category literals
# ---------------------------------------------------------------------------

# A candidate can be either a CorpusCandidate wrapper or a bare ReceptionScenarioSpec.
CandidateInput = Union[CorpusCandidate, ReceptionScenarioSpec]

# Dimensions for which we compute per-dimension attribution.
ATTRIBUTION_DIMENSIONS: tuple[str, ...] = (
    "downstream_outcome",
    "tool_sequence",
    "appointment_deltas",
    "audit_deltas",
)

# ---------------------------------------------------------------------------
# Audit record types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConflictRecord:
    """One deterministic conflict record from the candidate-quality audit."""

    rule_id: str
    candidate_id: str
    category: AuditCategory
    observed_value: str | None
    expected_value: str | None
    evidence_excerpt: str = ""


@dataclass(frozen=True)
class DimensionAttribution:
    """Per-dimension failure attribution."""

    total: int
    passed: int
    failed: int
    surface_contract_conflict: int = 0
    unsupported_or_ambiguous_surface: int = 0
    aligned_failure: int = 0


@dataclass(frozen=True)
class AuditResult:
    """Aggregate result of one candidate-quality audit pass."""

    total_candidates: int
    total_samples: int

    aligned_pass_count: int
    aligned_failure_count: int
    surface_contract_conflict_count: int
    unsupported_or_ambiguous_surface_count: int

    conflict_records: tuple[ConflictRecord, ...]

    corpus_hash: str

    per_rule_counts: dict[str, int] = field(default_factory=dict)

    dimension_attribution: dict[str, DimensionAttribution] = field(default_factory=dict)

    variance_count: int = 0

    provenance: str = "silver"
    adjudication: str = "pending"

    def category_counts(self) -> dict[str, int]:
        return {
            "aligned_pass": self.aligned_pass_count,
            "aligned_failure": self.aligned_failure_count,
            "surface_contract_conflict": self.surface_contract_conflict_count,
            "unsupported_or_ambiguous_surface": self.unsupported_or_ambiguous_surface_count,
        }

    def aligned_subset_scores(self) -> dict[str, int]:
        aligned_total = self.aligned_pass_count + self.aligned_failure_count
        return {
            "aligned_total": aligned_total,
            "aligned_passed": self.aligned_pass_count,
            "aligned_failed": self.aligned_failure_count,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_excerpt(text: str, max_chars: int = 60) -> str:
    """Safe capped excerpt from utterance text for evidence display."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def _extract_utterances(scenario: ReceptionScenarioSpec) -> list[str]:
    return [
        turn.get("utterance", "")
        for turn in scenario.dialogue_turns
        if isinstance(turn.get("utterance"), str)
    ]


# ---------------------------------------------------------------------------
# Conflict detection rules
# ---------------------------------------------------------------------------


def _check_action_conflict(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    utterances: list[str],
) -> ConflictRecord | None:
    """Rule CONFLICT-ACT-001: parser detects a different intended action."""
    from app.services.bernie.semantic_extraction import _detect_intended_action

    primary = utterances[0] if utterances else ""
    detected = _detect_intended_action(primary)
    if detected is not None and detected != scenario.intended_action:
        return ConflictRecord(
            rule_id=RULE_ACTION_MISMATCH,
            candidate_id=scenario.scenario_id,
            category="surface_contract_conflict",
            observed_value=detected,
            expected_value=scenario.intended_action,
            evidence_excerpt=_safe_excerpt(primary),
        )
    return None


def _check_temporal_conflict(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    utterances: list[str],
) -> ConflictRecord | None:
    """Rule CONFLICT-TMP-001: parser detects different temporal relation."""
    from app.services.bernie.semantic_extraction import _extract_temporal

    primary = utterances[0] if utterances else ""
    detected_relation, detected_earliest, detected_latest = _extract_temporal(primary)
    if detected_relation == "unspecified":
        return None
    if detected_relation != scenario.temporal_relation:
        return ConflictRecord(
            rule_id=RULE_TEMPORAL_MISMATCH,
            candidate_id=scenario.scenario_id,
            category="surface_contract_conflict",
            observed_value=detected_relation,
            expected_value=scenario.temporal_relation,
            evidence_excerpt=_safe_excerpt(primary),
        )
    return None


def _check_duration_conflict(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    utterances: list[str],
) -> ConflictRecord | None:
    """Rule CONFLICT-DUR-001: parser detects different duration."""
    from app.services.bernie.semantic_extraction import _extract_duration

    primary = utterances[0] if utterances else ""
    detected_dur, detected_sem = _extract_duration(primary)
    if detected_sem == "omitted":
        return None
    if detected_sem == "exact" and detected_dur is not None:
        expected_dur = scenario.normalized_values.get("duration_minutes")
        if expected_dur is not None and detected_dur != expected_dur:
            return ConflictRecord(
                rule_id=RULE_DURATION_MISMATCH,
                candidate_id=scenario.scenario_id,
                category="surface_contract_conflict",
                observed_value=str(detected_dur),
                expected_value=str(expected_dur),
                evidence_excerpt=_safe_excerpt(primary),
            )
    return None


def _check_entity_conflict(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    utterances: list[str],
) -> ConflictRecord | None:
    """Rule CONFLICT-ENT-001: parser detects different entity state."""
    from app.services.bernie.semantic_extraction import _extract_entity_semantics

    detected = _extract_entity_semantics(utterances)
    if detected.get("practitioner") in ("exact",):
        if scenario.practitioner_semantics not in ("exact", "corrected"):
            return ConflictRecord(
                rule_id=RULE_ENTITY_MISMATCH,
                candidate_id=scenario.scenario_id,
                category="surface_contract_conflict",
                observed_value=detected.get("practitioner", "?"),
                expected_value=scenario.practitioner_semantics,
                evidence_excerpt="practitioner",
            )
    if detected.get("patient") in ("exact",):
        if scenario.patient_semantics not in ("exact", "corrected"):
            return ConflictRecord(
                rule_id=RULE_ENTITY_MISMATCH,
                candidate_id=scenario.scenario_id,
                category="surface_contract_conflict",
                observed_value=detected.get("patient", "?"),
                expected_value=scenario.patient_semantics,
                evidence_excerpt="patient",
            )
    return None


def _check_clarification_conflict(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    utterances: list[str],
) -> ConflictRecord | None:
    """Rule CONFLICT-CLR-001: parser/label clarification disagreement.

    This is an ordinary disagreement — the interpreter output does not match
    the Silver label.  It is classified as ``aligned_failure`` rather than
    ``surface_contract_conflict`` because the interpretation result alone
    does not independently contradict the label's surface evidence.
    """
    if scenario.action_semantics == "prohibited":
        return None
    scenario_expects_clarify = scenario.expected_clarification is not None
    parser_says_clarify = interpretation.requires_clarification
    if parser_says_clarify != scenario_expects_clarify:
        primary = utterances[0] if utterances else ""
        return ConflictRecord(
            rule_id=RULE_CLARIFICATION_MISMATCH,
            candidate_id=scenario.scenario_id,
            category="aligned_failure",
            observed_value=str(parser_says_clarify),
            expected_value=str(scenario_expects_clarify),
            evidence_excerpt=_safe_excerpt(primary),
        )
    return None


def _check_authority_conflict(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
) -> ConflictRecord | None:
    """Rule CONFLICT-AUT-001: parser claims different authority.

    This is an ordinary disagreement — the interpreter authority claim does
    not match the label's expected authority.  It is classified as
    ``aligned_failure`` rather than ``surface_contract_conflict`` because
    the interpretation result alone does not independently contradict the
    label's surface evidence.
    """
    if scenario.action_semantics == "prohibited":
        expected = "refuse"
    elif scenario.action_semantics == "ambiguous" or scenario.expected_clarification is not None:
        expected = "clarify"
    else:
        expected = "read"
    observed = interpretation.authority_claim
    if observed != expected and observed is not None:
        return ConflictRecord(
            rule_id=RULE_AUTHORITY_MISMATCH,
            candidate_id=scenario.scenario_id,
            category="aligned_failure",
            observed_value=observed,
            expected_value=expected,
            evidence_excerpt="",
        )
    return None


# Surface patterns that indicate genuinely ambiguous utterances
# (examined from text alone, not from interpretation output).
_AMBIGUOUS_SURFACE_PHRASES: list[re.Pattern[str]] = [
    re.compile(r"\bsometime\b", re.I),
    re.compile(r"\bmaybe\b", re.I),
    re.compile(r"\bnot sure\b", re.I),
    re.compile(r"\beither\b", re.I),
    re.compile(r"\bwhatever\b", re.I),
    re.compile(r"\bi don'?t know\b", re.I),
]


def _check_ambiguous_surface(
    scenario: ReceptionScenarioSpec,
    interpretation: InterpretationObservation,
    utterances: list[str],
) -> ConflictRecord | None:
    """Rule CONFLICT-AMB-001: surface text is genuinely ambiguous.

    Checks utterance text directly for ambiguous phrases — does not use
    the interpretation result as evidence.  When the bounded surface check
    cannot decide, returns ``unsupported_or_ambiguous_surface``.
    """
    for u in utterances:
        for pat in _AMBIGUOUS_SURFACE_PHRASES:
            if pat.search(u):
                return ConflictRecord(
                    rule_id=RULE_AMBIGUOUS_SURFACE,
                    candidate_id=scenario.scenario_id,
                    category="unsupported_or_ambiguous_surface",
                    observed_value="ambiguous_surface_text",
                    expected_value=scenario.intended_action,
                    evidence_excerpt=_safe_excerpt(u),
                )
    return None


# ---------------------------------------------------------------------------
# Negation detection for surface conflict
# ---------------------------------------------------------------------------

_NEGATED_PHRASES = frozenset({
    "never mind", "not needed", "no need",
    "leave it", "forget it", "scrap that",
})


def _detect_surface_negation(utterances: list[str]) -> bool:
    """Detect whether any utterance contains a negation/reversal pattern."""
    for u in utterances:
        lower = u.lower()
        for phrase in _NEGATED_PHRASES:
            if phrase in lower:
                return True
        if re.search(r"\b(do not|don't|not|no)\s+", lower):
            return True
    return False


# ---------------------------------------------------------------------------
# Corpus hash
# ---------------------------------------------------------------------------


def _to_scenario(candidate: CandidateInput) -> ReceptionScenarioSpec:
    """Extract the scenario from either a CorpusCandidate or bare spec."""
    if isinstance(candidate, CorpusCandidate):
        return candidate.scenario
    return candidate


def _compute_corpus_hash(candidates: list[CandidateInput]) -> str:
    """Stable hash over candidate/scenario IDs."""
    ids = sorted(
        c.scenario.scenario_id if isinstance(c, CorpusCandidate) else c.scenario_id
        for c in candidates
    )
    raw = json.dumps(ids, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Main audit function
# ---------------------------------------------------------------------------


def audit_candidates(
    candidates: list[CandidateInput],
    num_repeats: int = 2,
    max_conflict_examples: int = 20,
) -> AuditResult:
    """Run the candidate-quality firewall over Silver/pending candidates.

    Accepts bare ``ReceptionScenarioSpec`` variants directly (the primary use
    for the 1,152 LC4 development partition) or ``CorpusCandidate`` wrappers
    (LC2 compatibility).  Each candidate is interpreted and replayed
    deterministically.  The audit classifies every (candidate, sample) pair
    into one of four categories.

    Parameters
    ----------
    candidates :
        Silver/pending variants or CorpusCandidate wrappers.
    num_repeats :
        Number of deterministic repeats (default 2).
    max_conflict_examples :
        Max conflict records in result (capped for brevity).

    Returns
    -------
    AuditResult
        Aggregated audit counts, uncapped per-rule counts, capped conflict
        records, per-dimension attribution, and measured variance.
    """
    corpus_hash = _compute_corpus_hash(candidates)

    aligned_pass = 0
    aligned_failure = 0
    surface_conflict_count = 0
    ambiguous_count = 0
    total_samples = 0

    conflict_records: list[ConflictRecord] = []
    seen_records: set[str] = set()
    all_rule_counts: dict[str, int] = {}

    # Per-dimension attribution accumulators.
    dim_attribution: dict[str, dict[str, int]] = {
        dim: {"total": 0, "passed": 0, "failed": 0,
              "surface_contract_conflict": 0,
              "unsupported_or_ambiguous_surface": 0,
              "aligned_failure": 0}
        for dim in ATTRIBUTION_DIMENSIONS
    }

    # Variance tracking: store a fingerprint for each (scenario_id, repeat_idx).
    fingerprints: dict[tuple[str, int], str] = {}

    for candidate in candidates:
        scenario = _to_scenario(candidate)
        utterances = _extract_utterances(scenario)

        for sample_idx in range(num_repeats):
            total_samples += 1

            interp = deterministic_interpret(scenario)
            interp = InterpretationObservation(
                scenario_id=interp.scenario_id,
                sample_index=sample_idx,
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
            replay = deterministic_replay(scenario, interp)
            result = score_interpretation_replay_pair(scenario, interp, replay)

            # ---- Compute fingerprint for variance measurement ----
            fp_parts = [
                str(replay.downstream_outcome),
                str(replay.tools_used),
                str(replay.appointment_deltas),
                str(replay.audit_deltas),
                str(replay.is_simulated_confirmed_write),
                str(replay.requires_clarification),
                str(interp.authority_claim),
                str(interp.action_negated),
            ]
            fp = hashlib.sha256("|".join(fp_parts).encode("utf-8")).hexdigest()[:16]
            fingerprints[(scenario.scenario_id, sample_idx)] = fp

            # ---- Conflict detection -- first match wins ----
            detected: ConflictRecord | None = None

            surface_negated = _detect_surface_negation(utterances)
            if surface_negated and not interp.action_negated:
                detected = ConflictRecord(
                    rule_id=RULE_NEGATION_MISMATCH,
                    candidate_id=scenario.scenario_id,
                    category="surface_contract_conflict",
                    observed_value="surface_detected_negation",
                    expected_value="parser_no_negation",
                    evidence_excerpt=_safe_excerpt(utterances[0] if utterances else ""),
                )

            if detected is None:
                detected = _check_action_conflict(scenario, interp, utterances)
            if detected is None:
                detected = _check_temporal_conflict(scenario, interp, utterances)
            if detected is None:
                detected = _check_duration_conflict(scenario, interp, utterances)
            if detected is None:
                detected = _check_entity_conflict(scenario, interp, utterances)
            if detected is None:
                detected = _check_clarification_conflict(scenario, interp, utterances)
            if detected is None:
                detected = _check_authority_conflict(scenario, interp)
            if detected is None:
                detected = _check_ambiguous_surface(scenario, interp, utterances)

            # Determine the audit category for this sample.
            if detected is not None:
                cat = detected.category
            elif result.all_passed:
                cat: AuditCategory = "aligned_pass"
            else:
                cat = "aligned_failure"  # type: ignore[no-redef]

            # ---- Aggregate counts ----
            if cat == "unsupported_or_ambiguous_surface":
                ambiguous_count += 1
            elif cat == "surface_contract_conflict":
                surface_conflict_count += 1
            elif cat == "aligned_failure":
                aligned_failure += 1
            else:  # aligned_pass
                aligned_pass += 1

            # ---- Per-rule counts (uncapped) ----
            if detected is not None:
                all_rule_counts[detected.rule_id] = (
                    all_rule_counts.get(detected.rule_id, 0) + 1
                )
                dedup_key = (
                    f"{detected.rule_id}:{detected.candidate_id}:"
                    f"{detected.observed_value}:{detected.expected_value}"
                )
                if dedup_key not in seen_records and len(conflict_records) < max_conflict_examples:
                    seen_records.add(dedup_key)
                    conflict_records.append(detected)

            # ---- Per-dimension attribution ----
            for dim in ATTRIBUTION_DIMENSIONS:
                dim_attr = dim_attribution[dim]
                dim_attr["total"] += 1
                dim_result = getattr(result, dim, None)
                if dim_result is None:
                    continue
                if dim_result.passed:
                    dim_attr["passed"] += 1
                else:
                    dim_attr["failed"] += 1
                    if cat == "surface_contract_conflict":
                        dim_attr["surface_contract_conflict"] += 1
                    elif cat == "unsupported_or_ambiguous_surface":
                        dim_attr["unsupported_or_ambiguous_surface"] += 1
                    else:
                        dim_attr["aligned_failure"] += 1

    # ---- Compute variance ----
    variance_count = 0
    seen_scenarios: set[str] = set()
    for scenario_id in {s.scenario.scenario_id if isinstance(s, CorpusCandidate) else s.scenario_id for s in candidates}:
        if scenario_id in seen_scenarios:
            continue
        seen_scenarios.add(scenario_id)
        fps = [fingerprints.get((scenario_id, i), "") for i in range(num_repeats)]
        if len(set(fps)) > 1:
            variance_count += 1

    # Build final dimension attribution.
    final_dim_attr: dict[str, DimensionAttribution] = {}
    for dim, counts in dim_attribution.items():
        final_dim_attr[dim] = DimensionAttribution(
            total=counts["total"],
            passed=counts["passed"],
            failed=counts["failed"],
            surface_contract_conflict=counts["surface_contract_conflict"],
            unsupported_or_ambiguous_surface=counts["unsupported_or_ambiguous_surface"],
            aligned_failure=counts["aligned_failure"],
        )

    # Determine provenance/adjudication from input.
    provenance = "silver"
    adjudication = "pending"
    if candidates:
        first = candidates[0]
        if isinstance(first, CorpusCandidate):
            provenance = first.provenance.value
            adjudication = first.adjudication.value

    return AuditResult(
        total_candidates=len(candidates),
        total_samples=total_samples,
        aligned_pass_count=aligned_pass,
        aligned_failure_count=aligned_failure,
        surface_contract_conflict_count=surface_conflict_count,
        unsupported_or_ambiguous_surface_count=ambiguous_count,
        conflict_records=tuple(conflict_records),
        per_rule_counts=all_rule_counts,
        dimension_attribution=final_dim_attr,
        variance_count=variance_count,
        corpus_hash=corpus_hash,
        provenance=provenance,
        adjudication=adjudication,
    )


__all__ = [
    "AuditCategory",
    "AuditResult",
    "ConflictRecord",
    "DimensionAttribution",
    "RULE_ACTION_MISMATCH",
    "RULE_TEMPORAL_MISMATCH",
    "RULE_NEGATION_MISMATCH",
    "RULE_CORRECTION_MISMATCH",
    "RULE_DURATION_MISMATCH",
    "RULE_ENTITY_MISMATCH",
    "RULE_CLARIFICATION_MISMATCH",
    "RULE_AUTHORITY_MISMATCH",
    "RULE_AMBIGUOUS_SURFACE",
    "CandidateInput",
    "ATTRIBUTION_DIMENSIONS",
    "audit_candidates",
]
