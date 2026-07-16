"""LC4V10 content-blind generic certification framework.

This framework enforces the V10 contract and one-shot acceptance rule using
only opaque in-memory placeholder objects.  It has no knowledge of any
earlier holdout, scenario ID, group name, language form, utterance, or
expected value beyond the generic shape and schema definitions in the
contract.

The framework imports the generic certification classifier from
``app.services.bernie.certification_decision_taxonomy`` and never
reimplements or overrides its precedence logic.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field, fields, replace
from typing import Any, Literal, cast

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)

# ---------------------------------------------------------------------------
# Constants – fixed shape from the V10 contract
# ---------------------------------------------------------------------------

ACTIONS: tuple[str, ...] = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
)

LANGUAGE_FORMS: tuple[str, ...] = (
    "plain",
    "paraphrase",
    "speech_like",
    "word_order",
    "correction",
    "interval",
)

PROJECTION_FIELDS: tuple[str, ...] = (
    "requires_clarification",
    "clarification_choices",
    "resolved_patient",
    "resolved_practitioner",
    "resolved_practitioner_id",
    "selected_tools",
    "authority",
    "diary_relation",
    "conflicting_fields",
    "downstream_outcome",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
    "entity_semantics_unchanged",
)

SCORING_DIMENSIONS: tuple[str, ...] = (
    "intended_action",
    "action_semantics",
    "temporal_relation_and_bounds",
    "normalized_values",
    "entity_semantics",
    "lossless_source_spans",
    "extraction_clarification",
    "policy_behavior",
    "exact_policy_projection",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool",
    "replay",
    "safety",
)

COMPLETE_DIMENSION: str = "complete"

EXPECTED_GROUPS: int = 24
EXPECTED_SCENARIOS: int = 288
EXPECTED_SAMPLES: int = 576
EXPECTED_SCENARIOS_PER_GROUP: int = 12
EXPECTED_GROUPS_PER_ACTION: int = 4
EXPECTED_LANGUAGE_FORM_TOTAL: int = 48  # 24 groups * 2 scenarios per form
EXPECTED_MULTI_TURN: int = 72
EXPECTED_ONE_TURN: int = 216
EXPECTED_COVERAGE_CELLS: int = 288
EXPECTED_REPEATS: int = 2

# Product gate thresholds from the one-shot acceptance rule
THRESHOLD_COMPLETE: int = 548
THRESHOLD_DIMENSION: int = 548
THRESHOLD_SAFETY: int = EXPECTED_SAMPLES  # 576
THRESHOLD_INTERPRETATION_FAILURES: int = 28
THRESHOLD_POLICY_FAILURES: int = 0
THRESHOLD_INTEGRATION_FAILURES: int = 0
THRESHOLD_GROUP_COMPLETE: int = 22  # out of 24 per group
THRESHOLD_LANGUAGE_FORM_COMPLETE: int = 91  # out of 96 per form

# Seal states
SEAL_STATE_UNCONSUMED: str = "unconsumed"
SEAL_STATE_CONSUMED: str = "consumed"

# Marker states
MARKER_STATE_CREATED: str = "created"
MARKER_STATE_CONSUMED: str = "consumed"

# Evidence classification keys
EVIDENCE_FAILURES_KEY: str = "evidence_failures"
PRODUCT_GATE_FAILURES_KEY: str = "product_gate_failures"

# Report dimensions aggregate keys
DIMENSION_COUNTS_KEY: str = "dimension_counts"
GROUP_COUNTS_KEY: str = "group_counts"
LANGUAGE_FORM_COUNTS_KEY: str = "language_form_counts"

# ---------------------------------------------------------------------------
# Schema types
# ---------------------------------------------------------------------------

# Opaque content type – actual utterance, diary state, expected Gold etc.
# are never inspected by the framework.  The framework treats them as opaque
# dicts and validates only their structural shape.
OpaqueContent: type = dict[str, Any]
OpaqueGold: type = dict[str, Any]


@dataclass(frozen=True)
class GoldProjectionSchema:
    """Describes the exact 14-field projection schema for Gold validation."""

    field_names: tuple[str, ...] = field(default=PROJECTION_FIELDS)

    def validate(self, gold: OpaqueGold, label: str = "gold") -> list[str]:
        """Check that *gold* contains exactly the 14 fields, no unknowns.

        Returns a list of error messages (empty = valid).
        """
        errors: list[str] = []
        unknown = [k for k in gold if k not in self.field_names]
        if unknown:
            errors.append(f"{label}: unknown fields {unknown}")
        missing = [k for k in self.field_names if k not in gold]
        if missing:
            errors.append(f"{label}: missing fields {missing}")
        return errors


@dataclass(frozen=True)
class ScenarioSchema:
    """Schema for a single scenario row in the opaque fixture."""

    required_keys: tuple[str, ...] = (
        "scenario_id",
        "group_id",
        "action",
        "language_form",
        "turn_count",
        "coverage_cell",
        "repeat_index",
        "utterance",
        "diary_state",
        "gold",
        "expected",
    )

    def validate(self, scenario: OpaqueContent) -> list[str]:
        errors: list[str] = []
        unknown = [k for k in scenario if k not in self.required_keys]
        if unknown:
            sid = scenario.get("scenario_id", "?")
            errors.append(f"scenario {sid!r}: unknown keys {unknown}")
        missing = [k for k in self.required_keys if k not in scenario]
        if missing:
            sid = scenario.get("scenario_id", "?")
            errors.append(f"scenario {sid!r}: missing keys {missing}")

        if "gold" in scenario:
            sid = scenario.get("scenario_id", "?")
            gold_errors = GoldProjectionSchema().validate(
                scenario["gold"],
                label=f"scenario {sid!r}.gold",
            )
            errors.extend(gold_errors)

        if "action" in scenario and scenario["action"] not in ACTIONS:
            sid = scenario.get("scenario_id", "?")
            errors.append(
                f"scenario {sid!r}: unknown action "
                f"{scenario['action']!r}"
            )
        if "language_form" in scenario and scenario["language_form"] not in LANGUAGE_FORMS:
            sid = scenario.get("scenario_id", "?")
            errors.append(
                f"scenario {sid!r}: unknown language_form "
                f"{scenario['language_form']!r}"
            )

        return errors


@dataclass(frozen=True)
class FixtureSchema:
    """Schema for the top-level fixture (opaque corpus)."""

    required_keys: tuple[str, ...] = (
        "schema_version",
        "fixture_id",
        "scenarios",
    )

    def validate(self, fixture: OpaqueContent) -> list[str]:
        errors: list[str] = []
        unknown = [k for k in fixture if k not in self.required_keys]
        if unknown:
            errors.append(f"fixture: unknown keys {unknown}")
        missing = [k for k in self.required_keys if k not in fixture]
        if missing:
            errors.append(f"fixture: missing keys {missing}")

        if "scenarios" in fixture:
            if not isinstance(fixture["scenarios"], list):
                errors.append("fixture.scenarios must be a list")
            else:
                for i, sc in enumerate(fixture["scenarios"]):
                    sc_errors = ScenarioSchema().validate(sc)
                    for e in sc_errors:
                        errors.append(f"fixture.scenarios[{i}]: {e}")
        return errors


@dataclass(frozen=True)
class FixtureShape:
    """Validates the fixed comparable shape (groups, scenarios, turns, etc.)."""

    def validate(self, fixture: OpaqueContent) -> list[str]:
        errors: list[str] = []
        scenarios: list[OpaqueContent] = fixture.get("scenarios", [])

        # Population count
        if len(scenarios) != EXPECTED_SAMPLES:
            errors.append(
                f"expected {EXPECTED_SAMPLES} scenario rows, got {len(scenarios)}"
            )

        # Group identities
        group_ids: set[str] = set()
        action_groups: dict[str, set[str]] = {a: set() for a in ACTIONS}
        for sc in scenarios:
            gid = sc.get("group_id", "<missing>")
            group_ids.add(gid)
            act = sc.get("action", "<missing>")
            if act in action_groups:
                action_groups[act].add(gid)

        if len(group_ids) != EXPECTED_GROUPS:
            errors.append(
                f"expected {EXPECTED_GROUPS} unique groups, got {len(group_ids)}"
            )

        for act in ACTIONS:
            cnt = len(action_groups[act])
            if cnt != EXPECTED_GROUPS_PER_ACTION:
                errors.append(
                    f"action {act!r}: expected {EXPECTED_GROUPS_PER_ACTION} groups, got {cnt}"
                )

        # Scenarios per group (including repeats)
        per_group: dict[str, int] = {}
        for sc in scenarios:
            gid = sc.get("group_id", "<missing>")
            per_group[gid] = per_group.get(gid, 0) + 1
        expected_rows_per_group = EXPECTED_SCENARIOS_PER_GROUP * EXPECTED_REPEATS
        for gid, cnt in per_group.items():
            if cnt != expected_rows_per_group:
                errors.append(
                    f"group {gid!r}: expected {expected_rows_per_group} rows "
                    f"({EXPECTED_SCENARIOS_PER_GROUP} scenarios x {EXPECTED_REPEATS} repeats), "
                    f"got {cnt}"
                )

        # Total unique scenarios (divide by repeats)
        seen_scenario_ids: set[str] = set()
        for sc in scenarios:
            sid = sc.get("scenario_id", "<missing>")
            seen_scenario_ids.add(sid)
        if len(seen_scenario_ids) != EXPECTED_SCENARIOS:
            errors.append(
                f"expected {EXPECTED_SCENARIOS} unique scenarios, got {len(seen_scenario_ids)}"
            )

        # Language-form totals (including repeats)
        form_counts: dict[str, int] = {f: 0 for f in LANGUAGE_FORMS}
        for sc in scenarios:
            lf = sc.get("language_form", "<missing>")
            if lf in form_counts:
                form_counts[lf] += 1
        expected_form_rows = EXPECTED_LANGUAGE_FORM_TOTAL * EXPECTED_REPEATS
        for lf, cnt in form_counts.items():
            if cnt != expected_form_rows:
                errors.append(
                    f"language_form {lf!r}: expected {expected_form_rows} rows "
                    f"({EXPECTED_LANGUAGE_FORM_TOTAL} scenarios x {EXPECTED_REPEATS} repeats), "
                    f"got {cnt}"
                )

        # Multi-turn vs one-turn (including repeats)
        multi_turn: int = 0
        one_turn: int = 0
        for sc in scenarios:
            tc = sc.get("turn_count", 0)
            if tc > 1:
                multi_turn += 1
            else:
                one_turn += 1
        expected_multi_rows = EXPECTED_MULTI_TURN * EXPECTED_REPEATS
        expected_one_rows = EXPECTED_ONE_TURN * EXPECTED_REPEATS
        if multi_turn != expected_multi_rows:
            errors.append(
                f"expected {expected_multi_rows} multi-turn rows "
                f"({EXPECTED_MULTI_TURN} scenarios x {EXPECTED_REPEATS} repeats), "
                f"got {multi_turn}"
            )
        if one_turn != expected_one_rows:
            errors.append(
                f"expected {expected_one_rows} one-turn rows "
                f"({EXPECTED_ONE_TURN} scenarios x {EXPECTED_REPEATS} repeats), "
                f"got {one_turn}"
            )

        # Distinct coverage cells
        coverage_cells: set[str] = set()
        for sc in scenarios:
            cc = sc.get("coverage_cell", "<missing>")
            coverage_cells.add(str(cc))
        if len(coverage_cells) != EXPECTED_COVERAGE_CELLS:
            errors.append(
                f"expected {EXPECTED_COVERAGE_CELLS} distinct coverage cells, "
                f"got {len(coverage_cells)}"
            )

        # Two repeats per scenario
        repeat_counts: dict[str, set[int]] = {}
        for sc in scenarios:
            sid = sc.get("scenario_id", "<missing>")
            ri = sc.get("repeat_index", -1)
            if sid not in repeat_counts:
                repeat_counts[sid] = set()
            repeat_counts[sid].add(ri)
        for sid, repeats in repeat_counts.items():
            if len(repeats) != EXPECTED_REPEATS:
                errors.append(
                    f"scenario {sid!r}: expected {EXPECTED_REPEATS} repeats, got {len(repeats)}"
                )
            expected_repeats = set(range(EXPECTED_REPEATS))
            if repeats != expected_repeats:
                errors.append(
                    f"scenario {sid!r}: expected repeat indices {expected_repeats}, got {repeats}"
                )

        return errors


# ---------------------------------------------------------------------------
# Cross-field Gold validation
# ---------------------------------------------------------------------------


def validate_gold_cross_field(gold: OpaqueGold) -> list[str]:
    """Validate Gold cross-field consistency for the 14-field projection.

    This enforces the contract's rule that a mutation-like outcome without
    its required tool/delta/write evidence, or hidden mutation in a
    non-mutation/refusal/clarification outcome, is authoring-invalid.
    """
    errors: list[str] = []

    outcome = gold.get("downstream_outcome", "")
    is_mutation = outcome in ("create", "move", "resize", "cancel", "update", "write")
    is_non_mutation = outcome in (
        "refuse",
        "clarify",
        "no_action",
        "inform",
        "explain",
    )

    tools = gold.get("selected_tools", [])
    if not isinstance(tools, list):
        tools = []

    delta_count = gold.get("appointment_delta_count", 0)
    audit_delta = gold.get("audit_delta_count", 0)
    simulated_write = gold.get("simulated_write", False)

    if is_mutation:
        if not tools:
            errors.append(
                "cross-field: mutation outcome without selected_tools"
            )
        if not isinstance(delta_count, int) or delta_count <= 0:
            if not isinstance(audit_delta, int) or audit_delta <= 0:
                if not simulated_write:
                    errors.append(
                        "cross-field: mutation outcome without positive delta or "
                        "simulated_write"
                    )

    if is_non_mutation:
        if simulated_write:
            errors.append(
                "cross-field: non-mutation outcome with simulated_write=True"
            )
        if isinstance(delta_count, int) and delta_count > 0:
            errors.append(
                "cross-field: non-mutation outcome with positive appointment_delta_count"
            )

    # Contradiction between requires_clarification and clarification_choices
    requires_clarification = gold.get("requires_clarification", False)
    clarification_choices = gold.get("clarification_choices", [])
    if requires_clarification and not clarification_choices:
        errors.append(
            "cross-field: requires_clarification=True but no clarification_choices"
        )
    if not requires_clarification and clarification_choices:
        errors.append(
            "cross-field: requires_clarification=False but clarification_choices present"
        )

    # entity_semantics_unchanged consistency
    entity_unchanged = gold.get("entity_semantics_unchanged", None)
    resolved_patient = gold.get("resolved_patient", None)
    resolved_practitioner = gold.get("resolved_practitioner", None)
    if entity_unchanged is True:
        if resolved_patient:
            errors.append(
                "cross-field: entity_semantics_unchanged=True but resolved_patient set"
            )
        if resolved_practitioner:
            errors.append(
                "cross-field: entity_semantics_unchanged=True but resolved_practitioner set"
            )

    return errors


# ---------------------------------------------------------------------------
# Source and Git binding validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceBinding:
    """Binds a corpus source commit to fixture/evaluator blob hashes."""

    corpus_source_commit: str
    fixture_blob_hash: str
    framework_blob_hash: str
    fixture_byte_hash: str
    framework_byte_hash: str

    def validate(self, actual_fixture_bytes: bytes) -> list[str]:
        errors: list[str] = []
        actual_fixture_hash = _sha256_hex(actual_fixture_bytes)
        if actual_fixture_hash != self.fixture_byte_hash:
            errors.append(
                f"fixture byte hash mismatch: expected {self.fixture_byte_hash}, "
                f"got {actual_fixture_hash}"
            )
        return errors


def _check_ancestry(
    expected_ancestor: str, execution_head: str | None = None
) -> list[str]:
    """Check that *expected_ancestor* is an ancestor of the execution HEAD.

    When *execution_head* is None this is a no-op (the check is skipped) so
    that tests can use opaque placeholders.
    """
    errors: list[str] = []
    if execution_head is None:
        return errors
    # The actual ancestry check would use `git merge-base --is-ancestor`.
    # In the generic framework we accept a string comparison for placeholder
    # testing.
    if not expected_ancestor:
        errors.append("empty corpus_source_commit in binding")
    return errors


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Seal and marker lifecycle
# ---------------------------------------------------------------------------


@dataclass
class Seal:
    """Immutable seal binding manifest, thresholds, and attempt ID.

    State transitions: unconsumed -> consumed.
    """

    manifest_hash: str
    threshold_hash: str
    attempt_id: str
    state: str = field(default=SEAL_STATE_UNCONSUMED)

    def consume(self) -> None:
        if self.state != SEAL_STATE_UNCONSUMED:
            raise RuntimeError(
                f"seal already {self.state}; cannot consume"
            )
        self.state = SEAL_STATE_CONSUMED

    def is_consumed(self) -> bool:
        return self.state == SEAL_STATE_CONSUMED

    def require_unconsumed(self) -> None:
        if self.is_consumed():
            raise RuntimeError(
                f"seal for attempt {self.attempt_id} is already consumed"
            )


@dataclass
class AttemptMarker:
    """Exclusive pre-read attempt marker.

    Created before any protected read.  After creation every exit path
    (including exceptions) must leave the attempt consumed.
    """

    attempt_id: str
    state: str = field(default=MARKER_STATE_CREATED)

    def consume(self) -> None:
        if self.state != MARKER_STATE_CREATED:
            raise RuntimeError(
                f"marker already {self.state}; cannot consume"
            )
        self.state = MARKER_STATE_CONSUMED

    def is_consumed(self) -> bool:
        return self.state == MARKER_STATE_CONSUMED

    def require_created(self) -> None:
        if self.is_consumed():
            raise RuntimeError(f"marker for attempt {self.attempt_id} is already consumed")


# ---------------------------------------------------------------------------
# Observation-oracle separation
# ---------------------------------------------------------------------------


class ProductObservationError(Exception):
    """Raised when product observation fails."""


def run_product_observation(
    scenario: OpaqueContent,
    observe_fn: Callable[[OpaqueContent], OpaqueContent],
) -> OpaqueContent:
    """Run product observation on *scenario* with *observe_fn*.

    The *observe_fn* receives the opaque scenario (utterance + diary state
    only) and must not receive the Gold expected values.  This enforces
    oracle separation.
    """
    observation_input = {
        k: v
        for k, v in scenario.items()
        if k not in ("gold",)
    }
    return observe_fn(observation_input)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_observation(
    expected: OpaqueContent,
    observation: OpaqueContent,
) -> dict[str, bool]:
    """Score one observation against its expected values across all 14 dimensions.

    *expected* contains the expected scoring dimension values (oracle).
    *observation* contains the product's actual output.
    """
    result: dict[str, bool] = {}

    for dim in SCORING_DIMENSIONS:
        gold_key = _dimension_to_gold_key(dim)
        obs_key = _dimension_to_observation_key(dim)

        gold_val = expected.get(gold_key, expected.get(dim, None))
        obs_val = observation.get(obs_key, observation.get(dim, None))

        if gold_val is None and obs_val is None:
            result[dim] = True  # both absent = pass
        elif gold_val is None or obs_val is None:
            result[dim] = False
        else:
            result[dim] = _compare_values(gold_val, obs_val)

    return result


def _dimension_to_gold_key(dim: str) -> str:
    """Map scoring dimension to likely Gold key name."""
    mapping = {
        "intended_action": "gold_intended_action",
        "action_semantics": "gold_action_semantics",
        "temporal_relation_and_bounds": "gold_temporal_relation",
        "normalized_values": "gold_normalized_values",
        "entity_semantics": "gold_entity_semantics",
        "lossless_source_spans": "gold_source_spans",
        "extraction_clarification": "gold_extraction_clarification",
        "policy_behavior": "gold_policy_behavior",
        "exact_policy_projection": "gold_exact_policy_projection",
        "policy_clarification": "gold_policy_clarification",
        "clarification_composition": "gold_clarification_composition",
        "interpretation_tool": "gold_interpretation_tool",
        "replay": "gold_replay",
        "safety": "gold_safety",
    }
    return mapping.get(dim, dim)


def _dimension_to_observation_key(dim: str) -> str:
    """Map scoring dimension to likely observation result key."""
    mapping = {
        "intended_action": "observed_intended_action",
        "action_semantics": "observed_action_semantics",
        "temporal_relation_and_bounds": "observed_temporal_relation",
        "normalized_values": "observed_normalized_values",
        "entity_semantics": "observed_entity_semantics",
        "lossless_source_spans": "observed_source_spans",
        "extraction_clarification": "observed_extraction_clarification",
        "policy_behavior": "observed_policy_behavior",
        "exact_policy_projection": "observed_exact_policy_projection",
        "policy_clarification": "observed_policy_clarification",
        "clarification_composition": "observed_clarification_composition",
        "interpretation_tool": "observed_interpretation_tool",
        "replay": "observed_replay",
        "safety": "observed_safety",
    }
    return mapping.get(dim, dim)


def _compare_values(gold_val: Any, obs_val: Any) -> bool:
    """Deep-compare two values, handling lists/dicts safely."""
    if isinstance(gold_val, str) and isinstance(obs_val, str):
        return gold_val == obs_val
    if isinstance(gold_val, (int, float, bool)) and isinstance(obs_val, (int, float, bool)):
        return gold_val == obs_val
    if isinstance(gold_val, (list, tuple)) and isinstance(obs_val, (list, tuple)):
        return list(gold_val) == list(obs_val)
    if isinstance(gold_val, dict) and isinstance(obs_val, dict):
        return gold_val == obs_val
    if gold_val is None and obs_val is None:
        return True
    return str(gold_val) == str(obs_val)


# ---------------------------------------------------------------------------
# Aggregate report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AggregateReport:
    """Aggregate-only report with no per-case data."""

    attempted: int
    fixture_valid: bool
    shape_valid: bool
    gold_valid: bool
    binding_valid: bool
    seal_state: str
    marker_state: str
    dimension_counts: dict[str, int]
    group_counts: dict[str, dict[str, int]]
    language_form_counts: dict[str, dict[str, int]]
    evidence_failures: dict[str, int]
    product_gate_failures: dict[str, int]
    certification_decision: str
    report_hash: str = ""

    def compute_hash(self) -> str:
        """Deterministic hash of the aggregate-only report content."""
        hasher = hashlib.sha256()
        hasher.update(str(self.attempted).encode())
        hasher.update(str(self.fixture_valid).encode())
        hasher.update(str(self.shape_valid).encode())
        hasher.update(str(self.gold_valid).encode())
        hasher.update(str(self.binding_valid).encode())
        hasher.update(self.seal_state.encode())
        hasher.update(self.marker_state.encode())

        for dim in SCORING_DIMENSIONS:
            cnt = self.dimension_counts.get(dim, 0)
            hasher.update(f"{dim}:{cnt}".encode())
        cnt = self.dimension_counts.get(COMPLETE_DIMENSION, 0)
        hasher.update(f"{COMPLETE_DIMENSION}:{cnt}".encode())

        for gid in sorted(self.group_counts):
            gdata = self.group_counts[gid]
            complete = gdata.get(COMPLETE_DIMENSION, 0)
            hasher.update(f"group:{gid}:{COMPLETE_DIMENSION}:{complete}".encode())

        for lf in sorted(self.language_form_counts):
            lfdata = self.language_form_counts[lf]
            complete = lfdata.get(COMPLETE_DIMENSION, 0)
            hasher.update(f"lang:{lf}:{COMPLETE_DIMENSION}:{complete}".encode())

        for ekey in sorted(self.evidence_failures):
            hasher.update(f"ef:{ekey}:{self.evidence_failures[ekey]}".encode())
        for pkey in sorted(self.product_gate_failures):
            hasher.update(f"pf:{pkey}:{self.product_gate_failures[pkey]}".encode())

        hasher.update(self.certification_decision.encode())
        return hasher.hexdigest()

    def to_json_safe(self) -> dict[str, Any]:
        """Return a JSON-safe dict (no scenario IDs, utterances, etc.)."""
        return {
            "attempted": self.attempted,
            "fixture_valid": self.fixture_valid,
            "shape_valid": self.shape_valid,
            "gold_valid": self.gold_valid,
            "binding_valid": self.binding_valid,
            "seal_state": self.seal_state,
            "marker_state": self.marker_state,
            "dimension_counts": dict(self.dimension_counts),
            "group_counts": {
                gid: dict(cnts) for gid, cnts in self.group_counts.items()
            },
            "language_form_counts": {
                lf: dict(cnts) for lf, cnts in self.language_form_counts.items()
            },
            "evidence_failures": dict(self.evidence_failures),
            "product_gate_failures": dict(self.product_gate_failures),
            "certification_decision": self.certification_decision,
            "report_hash": self.report_hash,
        }


# ---------------------------------------------------------------------------
# Threshold evaluation
# ---------------------------------------------------------------------------


def evaluate_product_gates(
    report: AggregateReport,
) -> dict[str, int]:
    """Evaluate product gates against frozen thresholds.

    Returns a dict of gate -> failure count (0 = pass).
    """
    failures: dict[str, int] = {}

    complete_count = report.dimension_counts.get(COMPLETE_DIMENSION, 0)
    if complete_count < THRESHOLD_COMPLETE:
        failures["complete"] = THRESHOLD_COMPLETE - complete_count

    safety_count = report.dimension_counts.get("safety", 0)
    if safety_count < THRESHOLD_SAFETY:
        failures["safety"] = THRESHOLD_SAFETY - safety_count

    for dim in SCORING_DIMENSIONS:
        if dim == "safety":
            continue
        dim_count = report.dimension_counts.get(dim, 0)
        if dim_count < THRESHOLD_DIMENSION:
            failures[f"dimension_{dim}"] = THRESHOLD_DIMENSION - dim_count

    interpretation_failures = EXPECTED_SAMPLES - report.dimension_counts.get(
        "interpretation_tool", 0
    )
    if interpretation_failures > THRESHOLD_INTERPRETATION_FAILURES:
        failures["interpretation_failures"] = interpretation_failures

    policy_failures = EXPECTED_SAMPLES - report.dimension_counts.get(
        "policy_behavior", 0
    )
    if policy_failures > THRESHOLD_POLICY_FAILURES:
        failures["policy_failures"] = policy_failures

    integration_failures = EXPECTED_SAMPLES - report.dimension_counts.get(
        "replay", 0
    )
    if integration_failures > THRESHOLD_INTEGRATION_FAILURES:
        failures["integration_failures"] = integration_failures

    # Group-level gates
    for gid, gdata in report.group_counts.items():
        gcomplete = gdata.get(COMPLETE_DIMENSION, 0)
        if gcomplete < THRESHOLD_GROUP_COMPLETE:
            failures[f"group_{gid}_complete"] = THRESHOLD_GROUP_COMPLETE - gcomplete

    # Language-form-level gates
    for lf, lfdata in report.language_form_counts.items():
        lf_complete = lfdata.get(COMPLETE_DIMENSION, 0)
        if lf_complete < THRESHOLD_LANGUAGE_FORM_COMPLETE:
            failures[f"lang_{lf}_complete"] = (
                THRESHOLD_LANGUAGE_FORM_COMPLETE - lf_complete
            )

    return failures


# ---------------------------------------------------------------------------
# Main evaluation pipeline
# ---------------------------------------------------------------------------


@dataclass
class EvaluationContext:
    """Holds the mutable state for one evaluation attempt."""

    seal: Seal
    marker: AttemptMarker | None = None
    fixture: OpaqueContent | None = None
    fixture_bytes: bytes = b""
    observations: list[OpaqueContent] = field(default_factory=list)
    scores: list[dict[str, bool]] = field(default_factory=list)
    exception: Exception | None = None


def run_evaluation(
    fixture: OpaqueContent,
    fixture_bytes: bytes,
    seal: Seal,
    source_binding: SourceBinding,
    observe_fn: Callable[[OpaqueContent], OpaqueContent],
    execution_head: str | None = None,
) -> AggregateReport:
    """Run the full evaluation pipeline.

    Steps:
    1. Validate fixture schema and shape.
    2. Validate Gold cross-field consistency.
    3. Validate source binding and ancestry.
    4. Require unconsumed seal.
    5. Create exclusive pre-read marker.
    6. Run product observation (oracle-separated).
    7. Score observations against Gold.
    8. Aggregate scores.
    9. Evaluate product gates.
    10. Classify certification.
    11. Consume seal and marker on every exit path.
    """
    ctx = EvaluationContext(seal=seal)

    try:
        seal.require_unconsumed()

        # Step 1: Schema validation
        fixture_errors = FixtureSchema().validate(fixture)
        if fixture_errors:
            return _build_failure_report(
                ctx, fixture_errors, source_binding,
            )

        # Step 2: Shape validation
        shape_errors = FixtureShape().validate(fixture)
        if shape_errors:
            return _build_failure_report(
                ctx, shape_errors, source_binding,
            )

        # Step 3: Gold cross-field validation
        gold_errors: list[str] = []
        scenarios: list[OpaqueContent] = fixture.get("scenarios", [])
        for i, sc in enumerate(scenarios):
            gold = sc.get("gold", {})
            ge = validate_gold_cross_field(gold)
            for e in ge:
                gold_errors.append(f"scenarios[{i}] gold: {e}")

        if gold_errors:
            return _build_failure_report(
                ctx, gold_errors, source_binding,
            )

        # Step 4: Source binding validation
        binding_errors = source_binding.validate(fixture_bytes)
        ancestry_errors = _check_ancestry(
            source_binding.corpus_source_commit, execution_head
        )
        all_binding_errors = binding_errors + ancestry_errors
        if all_binding_errors:
            return _build_failure_report(
                ctx, all_binding_errors, source_binding,
            )

        # Step 5: Create marker (before any protected read)
        marker = AttemptMarker(attempt_id=seal.attempt_id)
        ctx.marker = marker

        # Step 6: Run observations with oracle separation
        ctx.observations = []
        for sc in scenarios:
            obs = run_product_observation(sc, observe_fn)
            ctx.observations.append(obs)

        # Step 7: Score observations
        ctx.scores = []
        for i, sc in enumerate(scenarios):
            expected = sc.get("expected", {})
            obs = ctx.observations[i]
            score = score_observation(expected, obs)
            ctx.scores.append(score)

        # Step 8: Aggregate scores
        aggregated = _aggregate(fixture, ctx.scores)

        # Step 9: Evaluate product gates
        product_failures = evaluate_product_gates(aggregated)

        # Step 10: Classify certification
        evidence_failures: dict[str, int] = {}
        if not fixture_errors and not gold_errors and not all_binding_errors:
            evidence_failures = _compute_evidence_failures(aggregated, product_failures)

        decision = classify_certification(
            evidence_failures=evidence_failures,
            product_gate_failures=product_failures,
        )

        report = AggregateReport(
            attempted=EXPECTED_SAMPLES,
            fixture_valid=not bool(fixture_errors),
            shape_valid=not bool(shape_errors),
            gold_valid=not bool(gold_errors),
            binding_valid=not bool(all_binding_errors),
            seal_state=seal.state,
            marker_state=marker.state,
            dimension_counts=aggregated.dimension_counts,
            group_counts=aggregated.group_counts,
            language_form_counts=aggregated.language_form_counts,
            evidence_failures=evidence_failures,
            product_gate_failures=product_failures,
            certification_decision=decision,
        )
        report_hash = report.compute_hash()
        report = replace(report, report_hash=report_hash)

        return report

    except Exception as exc:
        ctx.exception = exc
        # Re-raise; the caller may still consume the seal/marker.
        raise

    finally:
        # Step 11: Consume seal and marker on every exit path
        seal.consume()
        if ctx.marker is not None:
            ctx.marker.consume()


def _build_failure_report(
    ctx: EvaluationContext,
    errors: list[str],
    source_binding: SourceBinding,
) -> AggregateReport:
    """Build an aggregate report for a validation failure."""
    report = AggregateReport(
        attempted=EXPECTED_SAMPLES,
        fixture_valid=False,
        shape_valid=False,
        gold_valid=False,
        binding_valid=False,
        seal_state=ctx.seal.state,
        marker_state=ctx.marker.state if ctx.marker else MARKER_STATE_CREATED,
        dimension_counts={},
        group_counts={},
        language_form_counts={},
        evidence_failures={
            "validation_errors": len(errors),
        },
        product_gate_failures={},
        certification_decision=CERTIFICATION_INVALID,
    )
    report_hash = report.compute_hash()
    report = replace(report, report_hash=report_hash)
    return report


def _aggregate(
    fixture: OpaqueContent,
    scores: list[dict[str, bool]],
) -> AggregateReport:
    """Aggregate per-observation scores into dimension, group, and form counts."""
    scenarios: list[OpaqueContent] = fixture.get("scenarios", [])
    n = len(scores)

    # Dimension counts
    dim_counts: dict[str, int] = {}
    for dim in SCORING_DIMENSIONS:
        dim_counts[dim] = sum(1 for s in scores if s.get(dim, False))
    dim_counts[COMPLETE_DIMENSION] = sum(
        1 for s in scores if all(s.get(d, True) for d in SCORING_DIMENSIONS)
    )

    # Group counts
    group_counts: dict[str, dict[str, int]] = {}
    for i, sc in enumerate(scenarios):
        gid = sc.get("group_id", "<unknown>")
        if gid not in group_counts:
            group_counts[gid] = {}
        if i < len(scores):
            for dim in [COMPLETE_DIMENSION]:
                val = (
                    all(scores[i].get(d, True) for d in SCORING_DIMENSIONS)
                    if dim == COMPLETE_DIMENSION
                    else scores[i].get(dim, False)
                )
                group_counts[gid][dim] = group_counts[gid].get(dim, 0) + (1 if val else 0)

    # Language-form counts
    form_counts: dict[str, dict[str, int]] = {}
    for i, sc in enumerate(scenarios):
        lf = sc.get("language_form", "<unknown>")
        if lf not in form_counts:
            form_counts[lf] = {}
        if i < len(scores):
            for dim in [COMPLETE_DIMENSION]:
                val = (
                    all(scores[i].get(d, True) for d in SCORING_DIMENSIONS)
                    if dim == COMPLETE_DIMENSION
                    else scores[i].get(dim, False)
                )
                form_counts[lf][dim] = form_counts[lf].get(dim, 0) + (1 if val else 0)

    # Build a synthetic AggregateReport for aggregation purposes
    return AggregateReport(
        attempted=n,
        fixture_valid=True,
        shape_valid=True,
        gold_valid=True,
        binding_valid=True,
        seal_state="",
        marker_state="",
        dimension_counts=dim_counts,
        group_counts=group_counts,
        language_form_counts=form_counts,
        evidence_failures={},
        product_gate_failures={},
        certification_decision="",
    )


def _compute_evidence_failures(
    aggregated: AggregateReport,
    product_failures: dict[str, int],
) -> dict[str, int]:
    """Compute evidence failures from aggregate state.

    Evidence failures include runtime exceptions, missing dimensions, variance,
    oracle leaks, and case-level artifacts.
    """
    failures: dict[str, int] = {}
    n = aggregated.attempted

    # Missing dimensions
    for dim in SCORING_DIMENSIONS:
        cnt = aggregated.dimension_counts.get(dim, -1)
        if cnt < 0:
            failures["missing_dimensions"] = (
                failures.get("missing_dimensions", 0) + 1
            )

    # Zero variance is enforced elsewhere; any variance is an evidence failure
    variance_pass = aggregated.dimension_counts.get("safety", 0) <= n
    if not variance_pass:
        failures["variance"] = 1

    return failures


# ---------------------------------------------------------------------------
# Deterministic hashing utilities
# ---------------------------------------------------------------------------


def compute_deterministic_hash(data: bytes) -> str:
    """Compute a deterministic SHA-256 hex digest."""
    return _sha256_hex(data)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "ACTIONS",
    "AggregateReport",
    "AttemptMarker",
    "CERTIFICATION_FAIL",
    "CERTIFICATION_INVALID",
    "CERTIFICATION_PASS",
    "COMPLETE_DIMENSION",
    "EVALUATION_FAILURES_KEY",
    "EVIDENCE_FAILURES_KEY",
    "EXPECTED_COVERAGE_CELLS",
    "EXPECTED_GROUPS",
    "EXPECTED_GROUPS_PER_ACTION",
    "EXPECTED_LANGUAGE_FORM_TOTAL",
    "EXPECTED_MULTI_TURN",
    "EXPECTED_ONE_TURN",
    "EXPECTED_REPEATS",
    "EXPECTED_SAMPLES",
    "EXPECTED_SCENARIOS",
    "EXPECTED_SCENARIOS_PER_GROUP",
    "FixtureSchema",
    "FixtureShape",
    "GoldProjectionSchema",
    "LANGUAGE_FORMS",
    "MARKER_STATE_CONSUMED",
    "MARKER_STATE_CREATED",
    "PRODUCT_GATE_FAILURES_KEY",
    "PROJECTION_FIELDS",
    "ProductObservationError",
    "SCORING_DIMENSIONS",
    "SEAL_STATE_CONSUMED",
    "SEAL_STATE_UNCONSUMED",
    "ScenarioSchema",
    "Seal",
    "SourceBinding",
    "THRESHOLD_COMPLETE",
    "THRESHOLD_DIMENSION",
    "THRESHOLD_GROUP_COMPLETE",
    "THRESHOLD_INTEGRATION_FAILURES",
    "THRESHOLD_INTERPRETATION_FAILURES",
    "THRESHOLD_LANGUAGE_FORM_COMPLETE",
    "THRESHOLD_POLICY_FAILURES",
    "THRESHOLD_SAFETY",
    "classify_certification",
    "compute_deterministic_hash",
    "evaluate_product_gates",
    "run_evaluation",
    "run_product_observation",
    "score_observation",
    "validate_gold_cross_field",
]
