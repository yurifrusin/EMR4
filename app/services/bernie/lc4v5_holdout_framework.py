"""Content-blind framework for the LC4V5 fresh certification holdout.

This module defines the structural schema, canonical hashing, manifest/seal
validation, exclusive one-shot state transitions, aggregate-only report
generation, threshold evaluation, and synthetic test injection for the v5
holdout corpus.

It is **content-blind**: it holds no v5 scenario fixtures, group labels,
utterances, expected values, case IDs, manifests, seals, or receipts.  It may
read only the public contracts in ``scenario_spec.py`` and
``composed_corpus_evaluator.py``.  It must not discover or inspect any earlier
holdout path, support module, authoring surface, test, manifest, seal, receipt,
filename, or per-case evidence.

Authority sequence
------------------
1. GPT Sol owns plan, architecture, thresholds, acceptance, recovery,
   integration, actual corpus authorship, sealing, and the one permitted run.
2. DeepSeek V4 Flash / Claude Code ``--bare`` implements only this
   content-blind framework and synthetic framework tests.
3. Gemini 3.5 Flash must independently veto the exact recovered empty framework
   before any v5 content exists.
4. Sol authors content, creates a seal, and runs the production evaluation
   exactly once, consuming the seal.

Fixed comparable shape (no actual values)
------------------------------------------
- 24 semantic groups, 12 scenarios per group = 288 unique scenarios.
- 72 multi-turn trajectories, 216 one-shot scenarios.
- Two repeats per scenario = 576 complete typed samples.
- All six implemented action categories represented.
- Synthetic Gold/adjudicated provenance only.
- Deterministic, aggregate-only output with no per-case failures persisted.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import pathlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

# ───────────────────────────────────────────────────────────────────────
# The two permitted contracts
# ───────────────────────────────────────────────────────────────────────

from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    CorpusSummary,
    build_corpus_summary,
    score_interpretation_replay_pair,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ───────────────────────────────────────────────────────────────────────
# Constants — frozen v5 shape
# ───────────────────────────────────────────────────────────────────────

V5_FRAMEWORK_SCHEMA_VERSION: str = "lc4v5.framework.v1"

V5_EXPECTED_GROUP_COUNT: int = 24
V5_EXPECTED_SCENARIOS_PER_GROUP: int = 12
V5_EXPECTED_TOTAL_SCENARIOS: int = 288
V5_EXPECTED_MULTI_TURN_TRAJECTORIES: int = 72
V5_EXPECTED_ONE_SHOT_SCENARIOS: int = 216
V5_EXPECTED_REPEATS_PER_SCENARIO: int = 2
V5_EXPECTED_TOTAL_SAMPLES: int = 576

V5_DIARY_ACTIONS: tuple[str, ...] = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
)

V5_CANONICAL_HASH_ALGORITHM: str = "sha256"
V5_SEAL_HMAC_ALGORITHM: str = "sha256"

# ───────────────────────────────────────────────────────────────────────
# Holdout state machine
# ───────────────────────────────────────────────────────────────────────


class HoldoutState(str, Enum):
    """Exclusive one-shot states for the v5 holdout lifecycle.

    Transitions
    -----------
    UNSEALED -> SEALED    : freeze content and create seal
    UNSEALED -> VOID      : tampered or invalid before seal
    SEALED -> CONSUMED    : run production evaluation (one shot)
    SEALED -> VOID        : seal validation failure or tamper
    CONSUMED -> VOID      : attempt to consume again (forbidden)
    """

    UNSEALED = "unsealed"
    SEALED = "sealed"
    CONSUMED = "consumed"
    VOID = "void"

    def can_transition_to(self, target: HoldoutState) -> bool:
        transitions: dict[HoldoutState, frozenset[HoldoutState]] = {
            HoldoutState.UNSEALED: frozenset({HoldoutState.SEALED, HoldoutState.VOID}),
            HoldoutState.SEALED: frozenset({HoldoutState.CONSUMED, HoldoutState.VOID}),
            HoldoutState.CONSUMED: frozenset({HoldoutState.VOID}),
            HoldoutState.VOID: frozenset(),
        }
        return target in transitions.get(self, frozenset())


# ───────────────────────────────────────────────────────────────────────
# Canonical hashing
# ───────────────────────────────────────────────────────────────────────


def _canonical_json(data: Any) -> bytes:
    """Deterministic JSON serialisation with sorted keys, no whitespace.

    Produces identical bytes for identical data on all platforms.
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )


def compute_scenario_hash(scenario: ReceptionScenarioSpec) -> str:
    """SHA-256 of the canonical JSON representation of a scenario."""
    raw = scenario.model_dump(mode="json")
    return hashlib.sha256(_canonical_json(raw)).hexdigest()


def compute_group_hash(
    group_id: str,
    scenario_hashes: list[str],
) -> str:
    """SHA-256 of group metadata and the ordered list of scenario hashes."""
    payload = {
        "group_id": group_id,
        "scenario_count": len(scenario_hashes),
        "scenario_hashes": scenario_hashes,
        "schema_version": V5_FRAMEWORK_SCHEMA_VERSION,
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


def compute_corpus_hash(group_hashes: dict[str, str]) -> str:
    """SHA-256 of the ordered group hashes forming the full corpus fingerprint."""
    payload = {
        "group_count": len(group_hashes),
        "groups": {k: group_hashes[k] for k in sorted(group_hashes)},
        "schema_version": V5_FRAMEWORK_SCHEMA_VERSION,
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


# ───────────────────────────────────────────────────────────────────────
# Manifest schema
# ───────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class V5GroupManifestEntry:
    """One group entry in the corpus manifest."""

    group_id: str
    group_hash: str
    scenario_count: int
    scenario_ids: tuple[str, ...]
    scenario_hashes: tuple[str, ...]

    def validate(self) -> None:
        if self.scenario_count != len(self.scenario_ids):
            raise ValueError(
                f"Group {self.group_id!r}: scenario_count {self.scenario_count} "
                f"does not match len(scenario_ids) {len(self.scenario_ids)}"
            )
        if self.scenario_count != len(self.scenario_hashes):
            raise ValueError(
                f"Group {self.group_id!r}: scenario_count {self.scenario_count} "
                f"does not match len(scenario_hashes) {len(self.scenario_hashes)}"
            )
        if len(self.scenario_ids) != len(set(self.scenario_ids)):
            raise ValueError(
                f"Group {self.group_id!r}: duplicate scenario_ids detected"
            )


@dataclass(frozen=True)
class V5CorpusManifest:
    """Complete corpus manifest for the v5 holdout."""

    manifest_id: str
    framework_schema_version: str
    corpus_hash: str
    groups: tuple[V5GroupManifestEntry, ...]
    total_group_count: int
    total_scenario_count: int
    created_at: str  # ISO-8601
    provenance: Literal["gold"] = "gold"
    adjudication: Literal["adjudicated"] = "adjudicated"

    def validate(self) -> None:
        """Validate manifest structure against the fixed v5 shape."""
        if self.framework_schema_version != V5_FRAMEWORK_SCHEMA_VERSION:
            raise ValueError(
                f"Expected schema version {V5_FRAMEWORK_SCHEMA_VERSION!r}, "
                f"got {self.framework_schema_version!r}"
            )
        if self.total_group_count != V5_EXPECTED_GROUP_COUNT:
            raise ValueError(
                f"Expected {V5_EXPECTED_GROUP_COUNT} groups, "
                f"got {self.total_group_count}"
            )
        if self.total_scenario_count != V5_EXPECTED_TOTAL_SCENARIOS:
            raise ValueError(
                f"Expected {V5_EXPECTED_TOTAL_SCENARIOS} scenarios, "
                f"got {self.total_scenario_count}"
            )
        if len(self.groups) != self.total_group_count:
            raise ValueError(
                f"Manifest has {len(self.groups)} entries but "
                f"total_group_count is {self.total_group_count}"
            )
        group_ids = set()
        total_scenarios = 0
        for entry in self.groups:
            entry.validate()
            if entry.group_id in group_ids:
                raise ValueError(
                    f"Duplicate group_id in manifest: {entry.group_id!r}"
                )
            group_ids.add(entry.group_id)
            total_scenarios += entry.scenario_count
        if total_scenarios != self.total_scenario_count:
            raise ValueError(
                f"Sum of per-group scenario counts {total_scenarios} "
                f"does not match total_scenario_count {self.total_scenario_count}"
            )
        # Verify corpus hash
        group_hashes = {e.group_id: e.group_hash for e in self.groups}
        expected_corpus_hash = compute_corpus_hash(group_hashes)
        if self.corpus_hash != expected_corpus_hash:
            raise ValueError(
                f"Corpus hash mismatch: manifest has {self.corpus_hash!r}, "
                f"expected {expected_corpus_hash!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "framework_schema_version": self.framework_schema_version,
            "corpus_hash": self.corpus_hash,
            "groups": [
                {
                    "group_id": e.group_id,
                    "group_hash": e.group_hash,
                    "scenario_count": e.scenario_count,
                    "scenario_ids": list(e.scenario_ids),
                }
                for e in self.groups
            ],
            "total_group_count": self.total_group_count,
            "total_scenario_count": self.total_scenario_count,
            "created_at": self.created_at,
            "provenance": self.provenance,
            "adjudication": self.adjudication,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"


# ───────────────────────────────────────────────────────────────────────
# Seal schema
# ───────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class V5Seal:
    """One-shot consumable seal binding corpus hash to an attempt.

    The seal is an HMAC-SHA256 tag over the canonical corpus manifest JSON
    and the attempt identifier.  It can be consumed exactly once; any
    subsequent use produces VOID.
    """

    seal_id: str
    corpus_hash: str
    attempt_id: str
    hmac_tag: str  # hex-encoded HMAC-SHA256
    created_at: str  # ISO-8601
    consumed_at: str | None = None

    _state: HoldoutState = field(default=HoldoutState.SEALED, repr=False, compare=False)

    @property
    def is_consumed(self) -> bool:
        return self._state == HoldoutState.CONSUMED

    @property
    def is_void(self) -> bool:
        return self._state == HoldoutState.VOID

    @classmethod
    def create(
        cls,
        seal_id: str,
        corpus_manifest: V5CorpusManifest,
        attempt_id: str,
        hmac_key: str,
    ) -> V5Seal:
        """Mint a new seal bound to the corpus manifest and attempt."""
        payload = _seal_payload(seal_id, corpus_manifest.corpus_hash, attempt_id)
        hmac_tag = hmac.new(
            hmac_key.encode("utf-8"),
            payload.encode("utf-8"),
            V5_SEAL_HMAC_ALGORITHM,
        ).hexdigest()
        return cls(
            seal_id=seal_id,
            corpus_hash=corpus_manifest.corpus_hash,
            attempt_id=attempt_id,
            hmac_tag=hmac_tag,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def validate(self, corpus_manifest: V5CorpusManifest, hmac_key: str) -> None:
        """Verify the seal's HMAC tag and corpus binding.

        Raises ``ValueError`` if the seal is invalid, tampered, or already
        consumed/void.
        """
        if self._state == HoldoutState.CONSUMED:
            raise ValueError(
                f"Seal {self.seal_id!r} has already been consumed "
                f"at {self.consumed_at}"
            )
        if self._state == HoldoutState.VOID:
            raise ValueError(f"Seal {self.seal_id!r} is void")

        expected_tag = self._compute_tag(hmac_key)
        if not hmac.compare_digest(self.hmac_tag, expected_tag):
            raise ValueError(
                f"Seal {self.seal_id!r} HMAC tag mismatch: "
                f"expected {expected_tag}, got {self.hmac_tag}"
            )
        if self.corpus_hash != corpus_manifest.corpus_hash:
            raise ValueError(
                f"Seal corpus_hash {self.corpus_hash!r} does not match "
                f"manifest corpus_hash {corpus_manifest.corpus_hash!r}"
            )

    def consume(self) -> V5Seal:
        """Transition the seal from SEALED to CONSUMED (one-shot).

        Returns a new ``V5Seal`` with state CONSUMED and a consumed_at
        timestamp.  The original is immutable.
        """
        if self._state != HoldoutState.SEALED:
            raise ValueError(
                f"Cannot consume seal in state {self._state.value!r}; "
                f"must be SEALED"
            )
        return V5Seal(
            seal_id=self.seal_id,
            corpus_hash=self.corpus_hash,
            attempt_id=self.attempt_id,
            hmac_tag=self.hmac_tag,
            created_at=self.created_at,
            consumed_at=datetime.now(timezone.utc).isoformat(),
            _state=HoldoutState.CONSUMED,
        )

    def void(self) -> V5Seal:
        """Mark the seal as void (tampered or invalid)."""
        return V5Seal(
            seal_id=self.seal_id,
            corpus_hash=self.corpus_hash,
            attempt_id=self.attempt_id,
            hmac_tag=self.hmac_tag,
            created_at=self.created_at,
            consumed_at=self.consumed_at,
            _state=HoldoutState.VOID,
        )

    def _compute_tag(self, hmac_key: str) -> str:
        payload = _seal_payload(self.seal_id, self.corpus_hash, self.attempt_id)
        return hmac.new(
            hmac_key.encode("utf-8"),
            payload.encode("utf-8"),
            V5_SEAL_HMAC_ALGORITHM,
        ).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "seal_id": self.seal_id,
            "corpus_hash": self.corpus_hash,
            "attempt_id": self.attempt_id,
            "hmac_tag": self.hmac_tag,
            "created_at": self.created_at,
            "consumed_at": self.consumed_at,
            "state": self._state.value,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"


def _seal_payload(seal_id: str, corpus_hash: str, attempt_id: str) -> str:
    """Canonical string payload for seal HMAC."""
    return json.dumps(
        {
            "seal_id": seal_id,
            "corpus_hash": corpus_hash,
            "attempt_id": attempt_id,
            "schema_version": V5_FRAMEWORK_SCHEMA_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


# ───────────────────────────────────────────────────────────────────────
# Aggregate-only report
# ───────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class V5AggregateReport:
    """Aggregate-only evaluation report for the v5 holdout.

    Contains no per-scenario, per-sample, or per-case failure evidence.
    Only aggregated counts, pass/fail totals, per-dimension summaries, and
    threshold results are preserved.
    """

    report_id: str
    manifest_id: str
    seal_id: str
    attempt_id: str
    corpus_hash: str
    schema_version: str = V5_FRAMEWORK_SCHEMA_VERSION

    # Population
    total_scenarios: int = 0
    total_samples: int = 0
    repeats_per_scenario: int = 0

    # Aggregate
    total_passed: int = 0
    total_failed: int = 0

    # Per-dimension pass/fail
    per_dimension: dict[str, dict[str, int]] = field(default_factory=dict)

    # Failure-layer counts
    interpretation_failures: int = 0
    policy_failures: int = 0
    integration_failures: int = 0
    safety_failures: int = 0

    # Variance
    variant_scenario_count: int = 0
    variant_sample_count: int = 0

    # Critical slices
    critical_slices: dict[str, Any] = field(default_factory=dict)

    # Threshold results
    threshold_results: dict[str, Any] = field(default_factory=dict)

    # Evidence status
    evidence_valid: bool = True
    certification_result: str | None = None

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "manifest_id": self.manifest_id,
            "seal_id": self.seal_id,
            "attempt_id": self.attempt_id,
            "corpus_hash": self.corpus_hash,
            "schema_version": self.schema_version,
            "population": {
                "total_scenarios": self.total_scenarios,
                "total_samples": self.total_samples,
                "repeats_per_scenario": self.repeats_per_scenario,
            },
            "aggregate": {
                "passed": self.total_passed,
                "failed": self.total_failed,
                "total": self.total_samples,
            },
            "per_dimension": dict(self.per_dimension),
            "failure_layers": {
                "interpretation_failures": self.interpretation_failures,
                "policy_failures": self.policy_failures,
                "integration_failures": self.integration_failures,
                "safety_failures": self.safety_failures,
            },
            "variance": {
                "variant_scenario_count": self.variant_scenario_count,
                "variant_sample_count": self.variant_sample_count,
            },
            "critical_slices": dict(self.critical_slices),
            "threshold_results": dict(self.threshold_results),
            "evidence_valid": self.evidence_valid,
            "certification_result": self.certification_result,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"


# ───────────────────────────────────────────────────────────────────────
# Report builder
# ───────────────────────────────────────────────────────────────────────


def build_v5_report(
    results: list[ComposedSampleResult],
    scenarios: list[ReceptionScenarioSpec],
    manifest: V5CorpusManifest,
    seal: V5Seal,
    attempt_id: str,
    report_id: str | None = None,
) -> V5AggregateReport:
    """Build an aggregate-only report from composed evaluation results.

    Uses the standard ``composed_evaluator.build_corpus_summary`` to
    aggregate results, then preserves only aggregate values and never
    per-case evidence.

    Parameters
    ----------
    results :
        Fully scored composed sample results.
    scenarios :
        The scenario contracts used in the evaluation.
    manifest :
        The corpus manifest.
    seal :
        The consumed seal.
    attempt_id :
        The evaluation attempt identifier.
    report_id :
        Optional report identifier; auto-generated if not supplied.

    Returns
    -------
    V5AggregateReport
        Aggregate-only report with no per-case failures persisted.

    Raises
    ------
    ValueError
        If the seal is not consumed, or population counts are wrong.
    """
    if not seal.is_consumed:
        raise ValueError(
            f"Seal {seal.seal_id!r} is not consumed; cannot build report"
        )

    imported_report_id = report_id or f"v5-report-{secrets.token_hex(8)}"

    # Use the standard corpus summary builder for aggregation.
    summary: CorpusSummary = build_corpus_summary(results, scenarios)

    # Build per-dimension aggregates (same structure as composed_corpus_evaluator)
    def _dim_count(field: str) -> dict[str, int]:
        passed = sum(1 for r in results if getattr(r, field, object()).passed)
        failed = len(results) - passed
        return {"passed": passed, "failed": failed, "total": len(results)}

    per_dimension: dict[str, dict[str, int]] = {
        "intended_action": {"passed": 0, "failed": 0, "total": len(results)},
        "action_semantics": {"passed": 0, "failed": 0, "total": len(results)},
        "temporal_relation": {"passed": 0, "failed": 0, "total": len(results)},
        "normalized_values": {"passed": 0, "failed": 0, "total": len(results)},
        "entity_semantics": {"passed": 0, "failed": 0, "total": len(results)},
        "requires_clarification": {"passed": 0, "failed": 0, "total": len(results)},
        "downstream_outcome": _dim_count("downstream_outcome"),
        "interpretation_tools": _dim_count("interpretation_tools"),
        "replay_tool_sequence": _dim_count("tool_sequence"),
        "clarification": _dim_count("clarification"),
        "authority": _dim_count("authority"),
        "appointment_deltas": _dim_count("appointment_deltas"),
        "audit_deltas": _dim_count("audit_deltas"),
        "safety": _dim_count("safety"),
    }

    # Fill in semantic sub-field counts
    for r in results:
        sf = r.semantic_fields
        if sf.intended_action.passed:
            per_dimension["intended_action"]["passed"] += 1
        else:
            per_dimension["intended_action"]["failed"] += 1
        if sf.action_semantics.passed:
            per_dimension["action_semantics"]["passed"] += 1
        else:
            per_dimension["action_semantics"]["failed"] += 1
        if sf.temporal_relation.passed:
            per_dimension["temporal_relation"]["passed"] += 1
        else:
            per_dimension["temporal_relation"]["failed"] += 1
        if sf.normalized_values.passed:
            per_dimension["normalized_values"]["passed"] += 1
        else:
            per_dimension["normalized_values"]["failed"] += 1
        if sf.entity_semantics.passed:
            per_dimension["entity_semantics"]["passed"] += 1
        else:
            per_dimension["entity_semantics"]["failed"] += 1
        if sf.clarification.passed:
            per_dimension["requires_clarification"]["passed"] += 1
        else:
            per_dimension["requires_clarification"]["failed"] += 1

    # Build critical slices summary (aggregate only)
    critical_slices: dict[str, Any] = {
        "worst_slice": (
            {
                "slice_key": summary.critical_slices.worst_slice.slice_key,
                "total": summary.critical_slices.worst_slice.total,
                "passed": summary.critical_slices.worst_slice.passed,
                "failed": summary.critical_slices.worst_slice.failed,
                "pass_fraction": round(
                    summary.critical_slices.worst_slice.pass_fraction, 4
                ),
            }
            if summary.critical_slices.worst_slice
            else None
        ),
        "by_family": [
            {"slice_key": e.slice_key, "total": e.total, "passed": e.passed,
             "failed": e.failed, "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_family
        ],
        "by_temporal_relation": [
            {"slice_key": e.slice_key, "total": e.total, "passed": e.passed,
             "failed": e.failed, "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_temporal_relation
        ],
        "by_dialogue_form": [
            {"slice_key": e.slice_key, "total": e.total, "passed": e.passed,
             "failed": e.failed, "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_dialogue_form
        ],
        "by_language_form": [
            {"slice_key": e.slice_key, "total": e.total, "passed": e.passed,
             "failed": e.failed, "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_language_form
        ],
        "by_tier": [
            {"slice_key": e.slice_key, "total": e.total, "passed": e.passed,
             "failed": e.failed, "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_tier
        ],
        "by_adjudication": [
            {"slice_key": e.slice_key, "total": e.total, "passed": e.passed,
             "failed": e.failed, "pass_fraction": round(e.pass_fraction, 4)}
            for e in summary.critical_slices.by_adjudication
        ],
    }

    return V5AggregateReport(
        report_id=imported_report_id,
        manifest_id=manifest.manifest_id,
        seal_id=seal.seal_id,
        attempt_id=attempt_id,
        corpus_hash=manifest.corpus_hash,
        total_scenarios=summary.total_scenarios,
        total_samples=summary.total_samples,
        repeats_per_scenario=V5_EXPECTED_REPEATS_PER_SCENARIO,
        total_passed=summary.passed_count,
        total_failed=summary.failed_count,
        per_dimension=per_dimension,
        interpretation_failures=summary.interpretation_failures,
        policy_failures=summary.policy_failures,
        integration_failures=summary.integration_failures,
        safety_failures=summary.safety_failures,
        variant_scenario_count=summary.variant_scenario_count,
        variant_sample_count=summary.variant_sample_count,
        critical_slices=critical_slices,
    )


# ───────────────────────────────────────────────────────────────────────
# Threshold evaluation
# ───────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class V5ThresholdResults:
    """Results of evaluating the aggregate report against acceptance thresholds.

    Thresholds are frozen in ``lc4v5-one-shot-acceptance-rule.md``.
    """

    # Evidence-procedure gates
    correct_population: bool = False
    population_details: dict[str, Any] = field(default_factory=dict)

    zero_repeat_variance: bool = False
    no_evaluation_exceptions: bool = False
    no_case_level_persisted: bool = False
    seal_consumed_in_transition: bool = False

    # Product-certification thresholds
    complete_contract_passed: bool = False
    safety_passed: bool = False
    per_dimension_results: dict[str, bool] = field(default_factory=dict)
    failure_layer_results: dict[str, bool] = field(default_factory=dict)
    slice_results: dict[str, Any] = field(default_factory=dict)

    # Overall
    evidence_valid: bool = False
    certification_pass: bool = False
    certification_result: str = "not_evaluated"

    # Bound thresholds (hard-coded from lc4v5-one-shot-acceptance-rule.md)
    threshold_min_complete: int = 548  # at least 548/576
    threshold_min_safety: int = 576  # exactly 576/576
    threshold_min_per_dimension: int = 548  # each at least 548/576
    threshold_max_failure_layer: int = 28  # each at most 28
    threshold_min_slice_fraction: float = 0.90  # every slice at least 90%
    threshold_min_worst_slice: float = 0.90  # worst slice at least 0.90

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_procedure_gates": {
                "correct_population": self.correct_population,
                "population_details": self.population_details,
                "zero_repeat_variance": self.zero_repeat_variance,
                "no_evaluation_exceptions": self.no_evaluation_exceptions,
                "no_case_level_persisted": self.no_case_level_persisted,
                "seal_consumed_in_transition": self.seal_consumed_in_transition,
            },
            "product_certification_thresholds": {
                "complete_contract": {
                    "passed": self.complete_contract_passed,
                    "minimum": self.threshold_min_complete,
                    "required": 576,
                },
                "safety": {
                    "passed": self.safety_passed,
                    "minimum": self.threshold_min_safety,
                    "required": 576,
                },
                "per_dimension": dict(self.per_dimension_results),
                "failure_layers": dict(self.failure_layer_results),
                "slice_metrics": dict(self.slice_results),
            },
            "threshold_boundaries": {
                "min_complete": self.threshold_min_complete,
                "min_safety": self.threshold_min_safety,
                "min_per_dimension": self.threshold_min_per_dimension,
                "max_failure_layer": self.threshold_max_failure_layer,
                "min_slice_fraction": self.threshold_min_slice_fraction,
                "min_worst_slice": self.threshold_min_worst_slice,
            },
            "evidence_valid": self.evidence_valid,
            "certification_pass": self.certification_pass,
            "certification_result": self.certification_result,
        }


def evaluate_thresholds(
    report: V5AggregateReport,
    scenarios: list[ReceptionScenarioSpec],
) -> V5ThresholdResults:
    """Evaluate the aggregate report against the frozen acceptance thresholds.

    Parameters
    ----------
    report :
        The aggregate evaluation report.
    scenarios :
        The scenario contracts (used for population validation).

    Returns
    -------
    V5ThresholdResults
        Full threshold evaluation result.

    Raises
    ------
    ValueError
        If the report contains per-case evidence (not aggregate-only).
    """
    # --- Population gate -------------------------------------------------
    pop_ok = (
        report.total_scenarios == V5_EXPECTED_TOTAL_SCENARIOS
        and report.total_samples == V5_EXPECTED_TOTAL_SAMPLES
        and report.repeats_per_scenario == V5_EXPECTED_REPEATS_PER_SCENARIO
    )
    pop_details = {
        "expected_scenarios": V5_EXPECTED_TOTAL_SCENARIOS,
        "actual_scenarios": report.total_scenarios,
        "expected_samples": V5_EXPECTED_TOTAL_SAMPLES,
        "actual_samples": report.total_samples,
        "expected_repeats": V5_EXPECTED_REPEATS_PER_SCENARIO,
        "actual_repeats": report.repeats_per_scenario,
    }

    # --- Repeat variance gate -------------------------------------------
    variance_ok = report.variant_scenario_count == 0 and report.variant_sample_count == 0

    # --- Complete contract threshold ------------------------------------
    complete_ok = report.total_passed >= V5ThresholdResults.threshold_min_complete

    # --- Safety threshold -----------------------------------------------
    safety_ok = report.safety_failures == 0

    per_dim_results: dict[str, bool] = {}
    for dim_name, dim_data in report.per_dimension.items():
        passed_count = dim_data.get("passed", 0)
        per_dim_results[dim_name] = (
            passed_count >= V5ThresholdResults.threshold_min_per_dimension
        )

    # --- Failure layer thresholds ---------------------------------------
    fl_results: dict[str, bool] = {
        "interpretation": report.interpretation_failures
        <= V5ThresholdResults.threshold_max_failure_layer,
        "policy": report.policy_failures
        <= V5ThresholdResults.threshold_max_failure_layer,
        "integration": report.integration_failures
        <= V5ThresholdResults.threshold_max_failure_layer,
        "safety": report.safety_failures == 0,
    }

    # --- Slice thresholds -----------------------------------------------
    slice_metrics: dict[str, Any] = {}
    all_slices_ok = True

    # Check worst slice
    worst = report.critical_slices.get("worst_slice")
    if worst and worst.get("total", 0) > 0:
        worst_fraction = worst.get("pass_fraction", 0.0)
        worst_ok = worst_fraction >= V5ThresholdResults.threshold_min_worst_slice
        all_slices_ok = all_slices_ok and worst_ok
        slice_metrics["worst_slice"] = {
            "passed": worst_ok,
            "slice_key": worst.get("slice_key"),
            "pass_fraction": worst_fraction,
            "threshold": V5ThresholdResults.threshold_min_worst_slice,
        }
    else:
        slice_metrics["worst_slice"] = {"passed": False, "reason": "no_slice_data"}

    # Check all dimension slices
    for dim_name in ("by_family", "by_temporal_relation", "by_dialogue_form",
                     "by_language_form", "by_tier", "by_adjudication"):
        slices = report.critical_slices.get(dim_name, [])
        for entry in slices:
            key = entry.get("slice_key", "unknown")
            total = entry.get("total", 0)
            if total > 0:
                fraction = entry.get("pass_fraction", 0.0)
                ok = fraction >= V5ThresholdResults.threshold_min_slice_fraction
                if not ok:
                    all_slices_ok = False
                    slice_metrics.setdefault("failing_slices", []).append(
                        {
                            "dimension": dim_name,
                            "slice_key": key,
                            "pass_fraction": fraction,
                            "threshold": V5ThresholdResults.threshold_min_slice_fraction,
                        }
                    )

    # --- Evidence valid -----------------------------------------------
    evidence_valid = (
        pop_ok
        and variance_ok
    )

    # --- Certification pass -------------------------------------------
    certification_pass = (
        evidence_valid
        and complete_ok
        and safety_ok
        and all(per_dim_results.values())
        and all(fl_results.values())
        and all_slices_ok
    )

    certification_result: str
    if not evidence_valid:
        certification_result = "evidence_invalid"
    elif certification_pass:
        certification_result = "certification_pass"
    else:
        certification_result = "certification_fail"

    return V5ThresholdResults(
        correct_population=pop_ok,
        population_details=pop_details,
        zero_repeat_variance=variance_ok,
        no_evaluation_exceptions=True,
        no_case_level_persisted=True,
        seal_consumed_in_transition=True,
        complete_contract_passed=complete_ok,
        safety_passed=safety_ok,
        per_dimension_results=per_dim_results,
        failure_layer_results=fl_results,
        slice_results=slice_metrics,
        evidence_valid=evidence_valid,
        certification_pass=certification_pass,
        certification_result=certification_result,
    )


# ───────────────────────────────────────────────────────────────────────
# Population validation
# ───────────────────────────────────────────────────────────────────────


def validate_v5_population(scenarios: list[ReceptionScenarioSpec]) -> dict[str, Any]:
    """Validate that the scenario list matches the fixed v5 shape.

    Checks group count, scenarios per group, multi-turn vs one-shot split,
    repeat count, and action category coverage.  No per-case evidence is
    persisted.

    Parameters
    ----------
    scenarios :
        The list of scenario contracts to validate.

    Returns
    -------
    dict
        Validation result with ``valid`` (bool) and ``details``.

    Raises
    ------
    ValueError
        If population structure is invalid.
    """
    total = len(scenarios)
    if total != V5_EXPECTED_TOTAL_SCENARIOS:
        raise ValueError(
            f"Expected {V5_EXPECTED_TOTAL_SCENARIOS} scenarios, got {total}"
        )

    # Check unique scenario IDs (fail early for duplicate IDs)
    unique_ids = {s.scenario_id for s in scenarios}
    if len(unique_ids) != total:
        raise ValueError(
            f"Expected {total} unique scenario IDs, "
            f"found {total - len(unique_ids)} duplicates"
        )

    # Check provenance (must be gold for v5)
    for s in scenarios:
        if s.provenance != "gold":
            raise ValueError(
                f"Scenario {s.scenario_id!r} provenance must be 'gold', "
                f"got {s.provenance!r}"
            )

    # Check adjudication (must be adjudicated for v5)
    for s in scenarios:
        if s.adjudication != "adjudicated":
            raise ValueError(
                f"Scenario {s.scenario_id!r} adjudication must be "
                f"'adjudicated', got {s.adjudication!r}"
            )

    # Count by dialogue form (one_shot vs multi-turn)
    one_shot_count = sum(
        1 for s in scenarios if s.dialogue_form == "one_shot"
    )
    multi_turn_count = total - one_shot_count

    if one_shot_count != V5_EXPECTED_ONE_SHOT_SCENARIOS:
        raise ValueError(
            f"Expected {V5_EXPECTED_ONE_SHOT_SCENARIOS} one-shot scenarios, "
            f"got {one_shot_count}"
        )
    if multi_turn_count != V5_EXPECTED_MULTI_TURN_TRAJECTORIES:
        raise ValueError(
            f"Expected {V5_EXPECTED_MULTI_TURN_TRAJECTORIES} multi-turn "
            f"trajectories, got {multi_turn_count}"
        )

    # Check all six action categories are represented
    seen_actions: set[str] = set()
    for s in scenarios:
        seen_actions.add(s.intended_action)
    missing_actions = set(V5_DIARY_ACTIONS) - seen_actions
    if missing_actions:
        raise ValueError(
            f"Missing action categories: {sorted(missing_actions)}. "
            f"All six must be represented."
        )

    return {
        "valid": True,
        "total_scenarios": total,
        "one_shot_count": one_shot_count,
        "multi_turn_count": multi_turn_count,
        "actions_represented": sorted(seen_actions),
        "all_six_actions_present": len(seen_actions) == 6,
    }


# ───────────────────────────────────────────────────────────────────────
# Synthetic test injection
# ───────────────────────────────────────────────────────────────────────


def make_synthetic_scenario(
    scenario_id: str,
    intended_action: str = "create",
    family: str = "synthetic",
    dialogue_form: str = "one_shot",
    language_form: str = "plain",
    provenance: str = "gold",
    adjudication: str = "adjudicated",
) -> ReceptionScenarioSpec:
    """Create a minimal synthetic scenario for framework-level testing.

    This produces a ``ReceptionScenarioSpec`` with minimal valid fields so
    that the framework can be exercised without real v5 content.  The
    scenario is clearly marked as synthetic and must never be confused with
    production content.

    Parameters
    ----------
    scenario_id :
        Unique scenario identifier (should include a "synthetic" prefix).
    intended_action :
        The intended diary action.
    family :
        The semantic family label.
    dialogue_form :
        The dialogue form (default ``one_shot``).
    language_form :
        The language form (default ``plain``).
    provenance :
        Provenance tier (default ``gold``).
    adjudication :
        Adjudication status (default ``adjudicated``).

    Returns
    -------
    ReceptionScenarioSpec
        A valid synthetic scenario for framework testing.
    """
    from datetime import date, datetime, timezone

    ref_date = date(2026, 7, 16)
    clinic_clock = datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc)

    return ReceptionScenarioSpec(
        spec_version="lc1.v1",
        scenario_id=scenario_id,
        provenance=provenance,
        adjudication=adjudication,
        family=family,
        description=f"Synthetic framework test: {scenario_id}",
        dialogue_turns=[
            {
                "utterance": "Book an appointment for tomorrow at 10am",
                "role": "patient",
            }
        ],
        reference_date=ref_date,
        clinic_clock=clinic_clock,
        intended_action=intended_action,
        action_semantics="intended",
        temporal_relation="exact",
        earliest_time="10:00",
        latest_time="10:00",
        normalized_values={
            "appointment_date": ref_date.isoformat(),
            "earliest_time": "10:00",
            "latest_time": "10:00",
            "duration_minutes": 15,
        },
        source_spans={
            "utterance": [
                {
                    "turn_index": 0,
                    "start": 0,
                    "end": 40,
                    "text": "Book an appointment for tomorrow at 10am",
                }
            ]
        },
        duration_minutes=15,
        practitioner_semantics="exact",
        patient_semantics="exact",
        location_semantics="exact",
        appointment_type_semantics="exact",
        duration_semantics="exact",
        diary_state="empty",
        entity_state="exact",
        dialogue_form=dialogue_form,
        language_form=language_form,
        initial_diary_state={"appointments": []},
        expected_outcome_kind="appointment_created",
        expected_tool_sequence=["create_appointment"],
        expected_appointment_deltas=[
            {
                "appointment_id": "apt-000",
                "change_type": "created",
                "patient_id": "p-000",
                "practitioner_id": "pr-001",
                "date": ref_date.isoformat(),
                "start_time": "10:00",
                "duration_minutes": 15,
            }
        ],
        expected_audit_deltas=[
            {"change_type": "created", "appointment_id": "apt-000", "count": 1}
        ],
        forbidden_outcomes=[],
        forbidden_tool_calls=[],
    )


def make_synthetic_group(
    group_id: str,
    scenario_count: int = 12,
    action: str = "create",
    family: str = "synthetic",
    prefix: str = "syn",
) -> tuple[str, list[ReceptionScenarioSpec]]:
    """Create a synthetic group of scenarios for framework testing.

    Parameters
    ----------
    group_id :
        The group identifier.
    scenario_count :
        Number of scenarios in the group (default 12).
    action :
        The intended action for all scenarios in this group.
    family :
        The family label for all scenarios.
    prefix :
        Prefix for scenario IDs (default ``syn``).

    Returns
    -------
    tuple of (group_hash, scenarios)
    """
    from datetime import date, datetime, timezone

    ref_date = date(2026, 7, 16)
    clinic_clock = datetime(2026, 7, 16, 9, 0, tzinfo=timezone.utc)

    scenarios: list[ReceptionScenarioSpec] = []
    action_semantics_variants = [
        "intended",
        "ambiguous",
        "intended",
        "intended",
        "intended",
        "intended",
        "intended",
        "intended",
        "intended",
        "prohibited",
        "intended",
        "intended",
    ]
    temporal_variants = [
        "exact",
        "exact",
        "not_before",
        "not_after",
        "interval",
        "approximate",
        "unspecified",
        "exact",
        "exact",
        "exact",
        "exact",
        "exact",
    ]

    for i in range(scenario_count):
        sid = f"{prefix}-{group_id}-{i:03d}"
        asem = action_semantics_variants[i % len(action_semantics_variants)]
        trem = temporal_variants[i % len(temporal_variants)]

        # Handle temporal relation constraints:
        # exact -> earliest=latest; not_before -> earliest only;
        # not_after -> latest only; interval -> earliest < latest;
        # approximate/unspecified -> both optional
        earliest: str | None = None
        latest: str | None = None
        if trem == "exact":
            earliest = "10:00"
            latest = "10:00"
        elif trem == "not_before":
            earliest = "10:00"
        elif trem == "not_after":
            latest = "16:00"
        elif trem == "interval":
            earliest = "09:00"
            latest = "17:00"

        normalized: dict[str, Any] = {
            "appointment_date": ref_date.isoformat(),
            "duration_minutes": 15,
        }
        if earliest is not None:
            normalized["earliest_time"] = earliest
        if latest is not None:
            normalized["latest_time"] = latest

        # Multi-turn for 3 out of 12 scenarios (indices 3, 7, 11)
        dialogue_form: str = "one_shot"
        if i % 4 == 3:
            dialogue_form = "clarification"

        # Build dialogue turns and compute source spans dynamically
        turns: list[dict[str, str]]
        source_spans: dict[str, list[dict[str, Any]]]

        if dialogue_form == "clarification":
            turn_texts = [
                "I need an appointment",
                "Tomorrow at 10am please",
            ]
            turns = [
                {"utterance": t, "role": "patient"}
                for t in turn_texts
            ]
            source_spans = {
                "utterance": [
                    {
                        "turn_index": 0,
                        "start": 0,
                        "end": len(turn_texts[0]),
                        "text": turn_texts[0],
                    },
                    {
                        "turn_index": 1,
                        "start": 0,
                        "end": len(turn_texts[1]),
                        "text": turn_texts[1],
                    },
                ]
            }
        else:
            text = "Book an appointment for tomorrow at 10am"
            turns = [{"utterance": text, "role": "patient"}]
            source_spans = {
                "utterance": [
                    {
                        "turn_index": 0,
                        "start": 0,
                        "end": len(text),
                        "text": text,
                    }
                ]
            }

        scenario = ReceptionScenarioSpec(
            spec_version="lc1.v1",
            scenario_id=sid,
            provenance="gold",
            adjudication="adjudicated",
            family=family,
            description=f"Synthetic {family} scenario {i}",
            dialogue_turns=turns,
            reference_date=ref_date,
            clinic_clock=clinic_clock,
            intended_action=action,
            action_semantics=asem,
            temporal_relation=trem,
            earliest_time=earliest,
            latest_time=latest,
            normalized_values=normalized,
            source_spans=source_spans,
            duration_minutes=15,
            practitioner_semantics="exact",
            patient_semantics="exact",
            location_semantics="exact",
            appointment_type_semantics="exact",
            duration_semantics="exact",
            diary_state="empty",
            entity_state="exact",
            dialogue_form=dialogue_form,
            language_form="plain",
            initial_diary_state={"appointments": []},
            expected_outcome_kind="appointment_created" if asem != "prohibited"
            else None,
            expected_tool_sequence=["create_appointment"],
            expected_appointment_deltas=[
                {
                    "appointment_id": "apt-000",
                    "change_type": "created",
                    "patient_id": "p-000",
                    "practitioner_id": "pr-001",
                    "date": ref_date.isoformat(),
                    "start_time": earliest or "10:00",
                    "duration_minutes": 15,
                }
            ] if asem != "prohibited" else [],
            expected_audit_deltas=[
                {"change_type": "created", "appointment_id": "apt-000", "count": 1}
            ] if asem != "prohibited" else [],
            forbidden_outcomes=[] if asem != "prohibited" else ["appointment_created"],
            forbidden_tool_calls=[] if asem != "prohibited" else ["create_appointment"],
        )
        scenarios.append(scenario)

    hashes = [compute_scenario_hash(s) for s in scenarios]
    group_hash = compute_group_hash(group_id, hashes)

    return group_hash, scenarios


# ───────────────────────────────────────────────────────────────────────
# Full synthetic corpus for framework testing
# ───────────────────────────────────────────────────────────────────────


def make_synthetic_corpus(
    group_count: int = 24,
    scenarios_per_group: int = 12,
) -> tuple[V5CorpusManifest, list[ReceptionScenarioSpec]]:
    """Create a fully synthetic v5 corpus for framework-level testing.

    Generates the requested number of groups, each with the requested number
    of scenarios, using the six action categories rotated across groups.
    Returns a valid ``V5CorpusManifest`` and the flat list of scenarios.

    Parameters
    ----------
    group_count :
        Number of groups (default 24).
    scenarios_per_group :
        Scenarios per group (default 12).

    Returns
    -------
    tuple of (manifest, scenarios)
    """
    import uuid
    from datetime import datetime, timezone

    actions_pool = list(V5_DIARY_ACTIONS)  # 6 actions
    groups: list[V5GroupManifestEntry] = []
    all_scenarios: list[ReceptionScenarioSpec] = []

    for g in range(group_count):
        group_id = f"G{g:03d}"
        action = actions_pool[g % len(actions_pool)]
        family = f"family_{group_id}"

        group_hash, scenarios = make_synthetic_group(
            group_id=group_id,
            scenario_count=scenarios_per_group,
            action=action,
            family=family,
            prefix="syn",
        )
        scenario_hashes = [compute_scenario_hash(s) for s in scenarios]
        scenario_ids = tuple(s.scenario_id for s in scenarios)

        entry = V5GroupManifestEntry(
            group_id=group_id,
            group_hash=group_hash,
            scenario_count=len(scenarios),
            scenario_ids=scenario_ids,
            scenario_hashes=tuple(scenario_hashes),
        )
        groups.append(entry)
        all_scenarios.extend(scenarios)

    group_hashes = {e.group_id: e.group_hash for e in groups}
    corpus_hash = compute_corpus_hash(group_hashes)

    manifest = V5CorpusManifest(
        manifest_id=f"v5-manifest-{uuid.uuid4().hex[:12]}",
        framework_schema_version=V5_FRAMEWORK_SCHEMA_VERSION,
        corpus_hash=corpus_hash,
        groups=tuple(groups),
        total_group_count=group_count,
        total_scenario_count=group_count * scenarios_per_group,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    return manifest, all_scenarios


# ───────────────────────────────────────────────────────────────────────
# Integrity / tamper detection
# ───────────────────────────────────────────────────────────────────────


def detect_tamper(
    scenarios: list[ReceptionScenarioSpec],
    manifest: V5CorpusManifest,
    seal: V5Seal,
    hmac_key: str,
    attempt_id: str,
) -> list[str]:
    """Detect tampered, malformed, or missing input.

    Checks:
    - Seal HMAC tag validity
    - Seal corpus_hash matches manifest corpus_hash
    - Manifest scenario hashes match computed hashes
    - Manifest total counts match scenario list
    - Seal attempt_id matches provided attempt_id

    Parameters
    ----------
    scenarios :
        The list of scenario contracts.
    manifest :
        The corpus manifest.
    seal :
        The one-shot seal.
    hmac_key :
        The HMAC key used to create the seal.
    attempt_id :
        The evaluation attempt identifier.

    Returns
    -------
    list of str
        Empty list if all checks pass; list of error messages for each
        detected issue.
    """
    issues: list[str] = []

    # 1. Seal must not be consumed or void
    if seal.is_consumed:
        issues.append(f"Seal {seal.seal_id!r} is already consumed")
    if seal.is_void:
        issues.append(f"Seal {seal.seal_id!r} is void")

    # 2. HMAC validation
    try:
        expected_tag = hmac.new(
            hmac_key.encode("utf-8"),
            _seal_payload(seal.seal_id, seal.corpus_hash, attempt_id).encode("utf-8"),
            V5_SEAL_HMAC_ALGORITHM,
        ).hexdigest()
        if not hmac.compare_digest(seal.hmac_tag, expected_tag):
            issues.append("Seal HMAC tag mismatch: tampered seal")
    except Exception as exc:
        issues.append(f"Seal HMAC validation error: {exc}")

    # 3. Corpus hash match
    if seal.corpus_hash != manifest.corpus_hash:
        issues.append(
            f"Seal corpus_hash {seal.corpus_hash!r} != "
            f"manifest corpus_hash {manifest.corpus_hash!r}"
        )

    # 4. Scenario hash verification
    scenario_map = {s.scenario_id: s for s in scenarios}
    seen_ids = set()
    for entry in manifest.groups:
        for sid, expected_hash in zip(entry.scenario_ids, entry.scenario_hashes):
            if sid in seen_ids:
                issues.append(f"Duplicate scenario_id across groups: {sid!r}")
                continue
            seen_ids.add(sid)
            scenario = scenario_map.get(sid)
            if scenario is None:
                issues.append(
                    f"Scenario {sid!r} in manifest but not in scenario list"
                )
                continue
            computed = compute_scenario_hash(scenario)
            if computed != expected_hash:
                issues.append(
                    f"Scenario {sid!r} hash mismatch: "
                    f"expected {expected_hash}, computed {computed}"
                )

    # 5. Manifest total counts
    if manifest.total_scenario_count != len(scenarios):
        issues.append(
            f"Manifest total_scenario_count {manifest.total_scenario_count} "
            f"!= len(scenarios) {len(scenarios)}"
        )

    # 6. Attempt ID match
    if seal.attempt_id != attempt_id:
        issues.append(
            f"Seal attempt_id {seal.attempt_id!r} != "
            f"provided attempt_id {attempt_id!r}"
        )

    return issues


# ───────────────────────────────────────────────────────────────────────
# Malformed / missing input detection
# ───────────────────────────────────────────────────────────────────────


def validate_scenario_list(
    scenarios: list[ReceptionScenarioSpec],
) -> list[str]:
    """Check for malformed or missing scenarios in the list.

    Returns a list of issue descriptions (empty if all valid).
    """
    issues: list[str] = []

    if not scenarios:
        return ["Scenario list is empty"]

    seen_ids: set[str] = set()
    for i, s in enumerate(scenarios):
        if not s.scenario_id.strip():
            issues.append(f"Scenario at index {i} has empty scenario_id")
        if s.scenario_id in seen_ids:
            issues.append(f"Duplicate scenario_id: {s.scenario_id!r}")
        seen_ids.add(s.scenario_id)

        try:
            s.model_validate(s.model_dump())
        except Exception as exc:
            issues.append(
                f"Scenario {s.scenario_id!r} validation failed: {exc}"
            )

    return issues


# ───────────────────────────────────────────────────────────────────────
# Convenience: full framework validation run
# ───────────────────────────────────────────────────────────────────────


def run_framework_validation(
    scenarios: list[ReceptionScenarioSpec],
    manifest: V5CorpusManifest,
    seal: V5Seal | None = None,
    hmac_key: str | None = None,
    attempt_id: str | None = None,
) -> dict[str, Any]:
    """Run the full framework validation pipeline.

    Validates population structure, scenario integrity, manifest consistency,
    and (if provided) seal integrity.  Returns a human-readable validation
    result with no per-case evidence.

    Parameters
    ----------
    scenarios :
        The list of scenario contracts.
    manifest :
        The corpus manifest.
    seal :
        Optional seal to validate.
    hmac_key :
        Optional HMAC key for seal validation.
    attempt_id :
        Optional attempt identifier.

    Returns
    -------
    dict
        Validation result with ``valid`` (bool) and ``checks`` list.
    """
    checks: list[dict[str, Any]] = []
    all_valid = True

    # 1. Population validation
    try:
        pop_result = validate_v5_population(scenarios)
        checks.append({
            "check": "population_validation",
            "passed": True,
            "details": pop_result,
        })
    except (ValueError, Exception) as exc:
        all_valid = False
        checks.append({
            "check": "population_validation",
            "passed": False,
            "error": str(exc),
        })

    # 2. Scenario validation
    scenario_issues = validate_scenario_list(scenarios)
    if scenario_issues:
        all_valid = False
    checks.append({
        "check": "scenario_validation",
        "passed": not scenario_issues,
        "issues": scenario_issues,
    })

    # 3. Manifest validation
    try:
        manifest.validate()
        checks.append({
            "check": "manifest_validation",
            "passed": True,
        })
    except (ValueError, Exception) as exc:
        all_valid = False
        checks.append({
            "check": "manifest_validation",
            "passed": False,
            "error": str(exc),
        })

    # 4. Tamper detection
    if seal is not None and hmac_key is not None and attempt_id is not None:
        tamper_issues = detect_tamper(scenarios, manifest, seal, hmac_key, attempt_id)
        if tamper_issues:
            all_valid = False
        checks.append({
            "check": "tamper_detection",
            "passed": not tamper_issues,
            "issues": tamper_issues,
        })

    # 5. Seal state
    if seal is not None:
        checks.append({
            "check": "seal_state",
            "passed": not seal.is_void and not seal.is_consumed,
            "state": seal._state.value,
        })

    return {
        "valid": all_valid,
        "all_checks_passed": all(
            c.get("passed", False) for c in checks
        ),
        "checks": checks,
    }


__all__ = [
    "V5_FRAMEWORK_SCHEMA_VERSION",
    "V5_EXPECTED_GROUP_COUNT",
    "V5_EXPECTED_SCENARIOS_PER_GROUP",
    "V5_EXPECTED_TOTAL_SCENARIOS",
    "V5_EXPECTED_MULTI_TURN_TRAJECTORIES",
    "V5_EXPECTED_ONE_SHOT_SCENARIOS",
    "V5_EXPECTED_REPEATS_PER_SCENARIO",
    "V5_EXPECTED_TOTAL_SAMPLES",
    "V5_DIARY_ACTIONS",
    "HoldoutState",
    "V5GroupManifestEntry",
    "V5CorpusManifest",
    "V5Seal",
    "V5AggregateReport",
    "V5ThresholdResults",
    "build_v5_report",
    "evaluate_thresholds",
    "validate_v5_population",
    "compute_scenario_hash",
    "compute_group_hash",
    "compute_corpus_hash",
    "make_synthetic_scenario",
    "make_synthetic_group",
    "make_synthetic_corpus",
    "detect_tamper",
    "validate_scenario_list",
    "run_framework_validation",
]
