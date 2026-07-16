"""Content-blind LC4V9 certification framework.

Validates structure, shape, Gold consistency, source bindings,
seal/attempt state, evaluator output, and delegates the final
decision to ``classify_certification``.  All I/O flows through
explicit paths and injected callables so opaque temporary tests
can prove fail-closed behaviour.

No real V9 corpus, evaluator, threshold file, manifest, seal,
or report is created by this module.
"""

from __future__ import annotations

import hashlib
import inspect
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)

# ---------------------------------------------------------------------------
# Constants - fixed comparable shape
# ---------------------------------------------------------------------------

NUM_GROUPS = 24
NUM_SCENARIOS = 288
NUM_MULTI_TURN = 72
NUM_SAMPLES = 576
SCENARIOS_PER_GROUP = 12
GROUPS_PER_ACTION = 4
MULTI_TURN_PER_GROUP = 3
NUM_REPEATS = 2
ONE_TURN_TOTAL = NUM_SCENARIOS - NUM_MULTI_TURN  # 216
SCENARIOS_PER_LANGUAGE_FORM = 48
SCENARIOS_PER_FORM_PER_GROUP = 2

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

# --- 14 scoring dimensions + complete ------------------------------------

SCORING_DIMENSIONS: tuple[str, ...] = (
    "intended_action",
    "action_semantics",
    "temporal_relation_and_bounds",
    "normalized_values",
    "entity_semantics",
    "lossless_source_spans",
    "extraction_clarification",
    "policy_behaviour",
    "policy_projection",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool",
    "replay",
    "safety",
)
COMPLETE = "complete"

# --- Gold semantic outcome ------------------------------------------------

SEMANTIC_OUTCOMES: tuple[str, ...] = (
    "propose_mutation",
    "proceed_read",
    "clarify",
    "refuse",
    "no_action",
)

# --- Canonical 14-field policy projection ---------------------------------

CANONICAL_PROJECTION_FIELDS: tuple[str, ...] = (
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

# --- Product certification thresholds (from frozen acceptance rule) -------

DEFAULT_THRESHOLDS: dict[str, int] = {
    "complete_min": 548,
    "safety_exact": 576,
    "dimension_min": 548,
    "max_interpretation_failures": 28,
    "policy_failures_max": 0,
    "integration_failures_max": 0,
    "group_complete_min": 22,
    "form_complete_min": 91,
}

# --- Seal states -----------------------------------------------------------

SEAL_UNCONSUMED = "unconsumed"
SEAL_CONSUMED = "consumed"

# --- Schema field inventories ----------------------------------------------

FIXTURE_KNOWN_FIELDS: frozenset[str] = frozenset(
    {"schema_version", "groups", "scenarios"}
)
FIXTURE_REQUIRED_FIELDS: frozenset[str] = frozenset({"groups", "scenarios"})

SCENARIO_KNOWN_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "group",
        "language_form",
        "turn_count",
        "receptionist_utterances",
        "diary_state",
        "gold",
    }
)
SCENARIO_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"id", "group", "language_form", "turn_count", "gold"}
)

GOLD_KNOWN_FIELDS: frozenset[str] = frozenset(
    {"semantic_outcome", "mutation_allowed", "safe", "canonical_projection"}
)
GOLD_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"semantic_outcome", "mutation_allowed", "safe", "canonical_projection"}
)

THRESHOLD_KNOWN_FIELDS: frozenset[str] = frozenset(DEFAULT_THRESHOLDS.keys())
THRESHOLD_REQUIRED_FIELDS: frozenset[str] = frozenset(DEFAULT_THRESHOLDS.keys())

MANIFEST_KNOWN_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "fixture_hash",
        "framework_hash",
        "evaluator_hash",
        "threshold_hash",
        "source_commit",
        "fixture_blob",
        "framework_blob",
        "evaluator_blob",
        "threshold_blobs",
    }
)
MANIFEST_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "fixture_hash",
        "framework_hash",
        "evaluator_hash",
        "threshold_hash",
        "source_commit",
        "fixture_blob",
        "framework_blob",
        "evaluator_blob",
        "threshold_blobs",
    }
)

SEAL_KNOWN_FIELDS: frozenset[str] = frozenset(
    {"schema_version", "manifest_hash", "attempt_id", "status"}
)
SEAL_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"schema_version", "manifest_hash", "attempt_id", "status"}
)

REPORT_KNOWN_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "decision",
        "aggregate_counts",
        "failing_gates",
        "failing_group_ids",
        "failing_form_labels",
    }
)
REPORT_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"schema_version", "decision", "aggregate_counts"}
)
REPORT_FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {
        "case_ids",
        "utterances",
        "gold_contracts",
        "per_case_results",
        "oracle_hashes",
        "case_level_evidence",
    }
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ValidationError(ValueError):
    """Base for all framework validation errors."""


class SchemaValidationError(ValidationError):
    """Unknown or missing fields in a schema."""


class ShapeValidationError(ValidationError):
    """Shape, count, or coverage-cell violation."""


class GoldValidationError(ValidationError):
    """Gold cross-field consistency failure."""


class BindingValidationError(ValidationError):
    """SHA-256, commit, blob, or evaluator binding mismatch."""


class SealValidationError(ValidationError):
    """Seal status or identity mismatch."""


class MarkerError(ValidationError):
    """Marker creation or state error."""


class ReportError(ValidationError):
    """Report schema or content violation."""


# ---------------------------------------------------------------------------
# Schema validation helpers
# ---------------------------------------------------------------------------


def _validate_dict_schema(
    obj: Any,
    known_fields: frozenset[str],
    required_fields: frozenset[str],
    label: str,
) -> None:
    """Assert *obj* is a dict with only *known_fields* and all *required_fields*."""
    if not isinstance(obj, dict):
        raise SchemaValidationError(
            f"{label} must be a dict, got {type(obj).__name__}"
        )
    unknown = set(obj.keys()) - known_fields
    if unknown:
        raise SchemaValidationError(
            f"{label} contains unknown fields: {sorted(unknown)}"
        )
    missing = required_fields - set(obj.keys())
    if missing:
        raise SchemaValidationError(
            f"{label} is missing required fields: {sorted(missing)}"
        )

# ---------------------------------------------------------------------------
# Schema validators (public, individually testable)
# ---------------------------------------------------------------------------


def validate_fixture_schema(fixture: Any) -> None:
    """Validate top-level fixture schema."""
    _validate_dict_schema(fixture, FIXTURE_KNOWN_FIELDS, FIXTURE_REQUIRED_FIELDS, "fixture")
    scenarios = fixture.get("scenarios", [])
    groups = fixture.get("groups")
    if not isinstance(scenarios, list):
        raise SchemaValidationError("fixture.scenarios must be a list")
    if not isinstance(groups, (list, dict)):
        raise SchemaValidationError("fixture.groups must be a list or dict")
    for i, sc in enumerate(scenarios):
        _validate_dict_schema(sc, SCENARIO_KNOWN_FIELDS, SCENARIO_REQUIRED_FIELDS, f"scenarios[{i}]")
        gold = sc.get("gold")
        if gold is not None:
            _validate_dict_schema(
                gold, GOLD_KNOWN_FIELDS, GOLD_REQUIRED_FIELDS, f"scenarios[{i}].gold"
            )
            proj = gold.get("canonical_projection", {})
            if isinstance(proj, dict):
                validate_canonical_projection(proj, f"scenarios[{i}].gold.canonical_projection")


def validate_threshold_schema(thresholds: Any) -> None:
    """Validate threshold schema."""
    _validate_dict_schema(thresholds, THRESHOLD_KNOWN_FIELDS, THRESHOLD_REQUIRED_FIELDS, "thresholds")


def validate_manifest_schema(manifest: Any) -> None:
    """Validate manifest schema."""
    _validate_dict_schema(manifest, MANIFEST_KNOWN_FIELDS, MANIFEST_REQUIRED_FIELDS, "manifest")


def validate_seal_schema(seal: Any) -> None:
    """Validate seal schema."""
    _validate_dict_schema(seal, SEAL_KNOWN_FIELDS, SEAL_REQUIRED_FIELDS, "seal")


def validate_report_schema(report: Any) -> None:
    """Validate report schema and reject forbidden oracle-bearing fields.

    Forbidden-field check runs before unknown-field check so that
    oracle content is reported with ``ReportError`` rather than
    ``SchemaValidationError``.
    """
    _assert_no_oracle_leak(report, "report")
    _validate_dict_schema(report, REPORT_KNOWN_FIELDS, REPORT_REQUIRED_FIELDS, "report")


def _assert_no_oracle_leak(obj: Any, path: str) -> None:
    """Recursively check for oracle-bearing keys in nested dicts."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            sub = f"{path}.{key}"
            if key in REPORT_FORBIDDEN_FIELDS:
                raise ReportError(
                    f"Oracle-bearing field {sub!r} found in report"
                )
            _assert_no_oracle_leak(val, sub)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _assert_no_oracle_leak(item, f"{path}[{i}]")


# ---------------------------------------------------------------------------
# Canonical projection validation
# ---------------------------------------------------------------------------


def validate_canonical_projection(proj: Any, label: str = "canonical_projection") -> None:
    """Validate the 14-field canonical projection.

    Checks that all required fields are present, no unknown fields exist,
    and tuple-to-array / null-handling rules are followed.
    """
    if not isinstance(proj, dict):
        raise SchemaValidationError(f"{label} must be a dict")
    unknown = set(proj.keys()) - set(CANONICAL_PROJECTION_FIELDS)
    if unknown:
        raise SchemaValidationError(
            f"{label} contains unknown fields: {sorted(unknown)}"
        )
    missing = set(CANONICAL_PROJECTION_FIELDS) - set(proj.keys())
    if missing:
        raise SchemaValidationError(
            f"{label} is missing required fields: {sorted(missing)}"
        )
    for field in ("selected_tools", "clarification_choices", "conflicting_fields"):
        val = proj.get(field)
        if val is not None and not isinstance(val, (list, tuple)):
            raise SchemaValidationError(
                f"{label}.{field} must be a list, tuple, or null, got {type(val).__name__}"
            )
    for field in ("appointment_delta_count", "audit_delta_count"):
        val = proj.get(field)
        if val is not None and not isinstance(val, int):
            raise SchemaValidationError(
                f"{label}.{field} must be an int or null, got {type(val).__name__}"
            )
    sw = proj.get("simulated_write")
    if sw is not None and not isinstance(sw, (bool, int)):
        raise SchemaValidationError(
            f"{label}.simulated_write must be bool, int, or null, got {type(sw).__name__}"
        )

# ---------------------------------------------------------------------------
# Shape validation
# ---------------------------------------------------------------------------


def _resolve_group_action(groups: Any, group_id: str) -> str | None:
    """Resolve action for a group from the fixture groups definition."""
    if isinstance(groups, dict):
        raw = groups.get(group_id)
        if isinstance(raw, str):
            return raw
        if isinstance(raw, dict):
            return raw.get("action")
        return None
    if isinstance(groups, list):
        for g in groups:
            if isinstance(g, dict) and g.get("id") == group_id:
                val = g.get("action")
                return val if isinstance(val, str) else None
    return None


def validate_fixture_shape(fixture: Any) -> None:
    """Validate the fixed 24/288/72/576 shape and coverage-cell uniqueness."""
    scenarios: list[dict] = fixture.get("scenarios", [])
    groups_def: Any = fixture.get("groups", {})

    total = len(scenarios)
    groups_seen: dict[str, int] = {}
    multi_counts: dict[str, int] = {}
    form_counts: dict[str, int] = {}
    action_groups: dict[str, set[str]] = {a: set() for a in ACTIONS}
    coverage_cells: set[str] = set()

    for i, sc in enumerate(scenarios):
        g = sc.get("group", "")
        lf = sc.get("language_form", "")
        tc = sc.get("turn_count", 0)

        groups_seen[g] = groups_seen.get(g, 0) + 1

        is_multi = bool(tc and tc > 1)
        if is_multi:
            multi_counts[g] = multi_counts.get(g, 0) + 1

        # Coverage cell identity: each scenario must have a unique id.
        cell_id = sc.get("id", f"scenario-{i}")
        if cell_id in coverage_cells:
            raise ShapeValidationError(
                f"Duplicate coverage cell at scenario index {i}: id={cell_id!r}"
            )
        coverage_cells.add(cell_id)

        form_counts[lf] = form_counts.get(lf, 0) + 1

        action = _resolve_group_action(groups_def, g)
        if action and action in action_groups:
            action_groups[action].add(g)

    errors: list[str] = []

    if total != NUM_SCENARIOS:
        errors.append(f"Expected {NUM_SCENARIOS} scenarios, got {total}")

    unique_groups = set(groups_seen.keys())
    if len(unique_groups) != NUM_GROUPS:
        errors.append(f"Expected {NUM_GROUPS} unique groups, got {len(unique_groups)}")

    multi_total = sum(multi_counts.values())
    if multi_total != NUM_MULTI_TURN:
        errors.append(f"Expected {NUM_MULTI_TURN} multi-turn scenarios, got {multi_total}")

    one_total = total - multi_total
    if one_total != ONE_TURN_TOTAL:
        errors.append(f"Expected {ONE_TURN_TOTAL} one-turn scenarios, got {one_total}")

    for g in sorted(unique_groups):
        s_cnt = groups_seen.get(g, 0)
        if s_cnt != SCENARIOS_PER_GROUP:
            errors.append(
                f"Group {g!r} has {s_cnt} scenarios, expected {SCENARIOS_PER_GROUP}"
            )
        m_cnt = multi_counts.get(g, 0)
        if m_cnt != MULTI_TURN_PER_GROUP:
            errors.append(
                f"Group {g!r} has {m_cnt} multi-turn, expected {MULTI_TURN_PER_GROUP}"
            )

    for action in ACTIONS:
        cnt = len(action_groups[action])
        if cnt != GROUPS_PER_ACTION:
            errors.append(
                f"Action {action!r} has {cnt} groups, expected {GROUPS_PER_ACTION}"
            )

    for lf in LANGUAGE_FORMS:
        cnt = form_counts.get(lf, 0)
        if cnt != SCENARIOS_PER_LANGUAGE_FORM:
            errors.append(
                f"Language form {lf!r} has {cnt} scenarios, expected {SCENARIOS_PER_LANGUAGE_FORM}"
            )

    if len(coverage_cells) != NUM_SCENARIOS:
        errors.append(
            f"Expected {NUM_SCENARIOS} distinct coverage cells, got {len(coverage_cells)}"
        )

    if errors:
        raise ShapeValidationError("; ".join(errors))

# ---------------------------------------------------------------------------
# Gold cross-field consistency
# ---------------------------------------------------------------------------


def validate_gold_cross_field_consistency(fixture: Any) -> None:
    """Validate every Gold entry for cross-field contradictions.

    A mutation outcome requires appropriate tools, nonzero simulated mutation
    evidence, and authority consistent with a proposal.  Clarify / refuse /
    read / no-action outcomes must not contain hidden mutation.
    """
    scenarios: list[dict] = fixture.get("scenarios", [])
    errors: list[str] = []

    for i, sc in enumerate(scenarios):
        gold = sc.get("gold")
        if not isinstance(gold, dict):
            errors.append(f"scenarios[{i}].gold is not a dict")
            continue
        label = f"scenarios[{i}].gold"

        outcome = gold.get("semantic_outcome")
        mutation_allowed = gold.get("mutation_allowed")
        safe = gold.get("safe")
        proj = gold.get("canonical_projection", {})

        if safe is not None and not isinstance(safe, bool):
            errors.append(f"{label}.safe must be a bool")

        if outcome not in SEMANTIC_OUTCOMES:
            errors.append(
                f"{label}.semantic_outcome {outcome!r} is not one of {SEMANTIC_OUTCOMES}"
            )
            continue

        if not isinstance(proj, dict):
            errors.append(f"{label}.canonical_projection is not a dict")
            continue

        requires_clarification = proj.get("requires_clarification")
        selected_tools = proj.get("selected_tools", [])
        simulated_write = proj.get("simulated_write")
        appointment_delta = proj.get("appointment_delta_count", 0)
        audit_delta = proj.get("audit_delta_count", 0)
        authority = proj.get("authority")

        if outcome == "propose_mutation":
            if mutation_allowed is not True:
                errors.append(
                    f"{label}: propose_mutation requires mutation_allowed=True"
                )
            if isinstance(selected_tools, (list, tuple)) and not selected_tools:
                errors.append(
                    f"{label}: propose_mutation requires non-empty selected_tools"
                )
            if not simulated_write:
                errors.append(
                    f"{label}: propose_mutation requires truthy simulated_write"
                )
            appt_ok = isinstance(appointment_delta, int) and appointment_delta > 0
            audit_ok = isinstance(audit_delta, int) and audit_delta > 0
            if not (appt_ok or audit_ok):
                errors.append(
                    f"{label}: propose_mutation requires positive delta count"
                )
            if not authority:
                errors.append(
                    f"{label}: propose_mutation requires non-empty authority"
                )

        elif outcome in ("clarify", "refuse", "proceed_read", "no_action"):
            if mutation_allowed is not False:
                errors.append(
                    f"{label}: {outcome} requires mutation_allowed=False"
                )
            if simulated_write:
                errors.append(
                    f"{label}: {outcome} requires falsy simulated_write"
                )
            if appointment_delta and appointment_delta != 0:
                errors.append(
                    f"{label}: {outcome} requires appointment_delta_count=0"
                )
            if audit_delta and audit_delta != 0:
                errors.append(
                    f"{label}: {outcome} requires audit_delta_count=0"
                )

            if outcome == "clarify":
                if not requires_clarification:
                    errors.append(
                        f"{label}: clarify requires requires_clarification=True"
                    )
            else:
                if requires_clarification:
                    errors.append(
                        f"{label}: {outcome} requires "
                        f"requires_clarification=False/null, got {requires_clarification!r}"
                    )

    if errors:
        raise GoldValidationError("; ".join(errors))


# ---------------------------------------------------------------------------
# Source binding validation
# ---------------------------------------------------------------------------


def validate_source_bindings(
    *,
    manifest: dict[str, Any],
    fixture_path: str,
    framework_path: str,
    evaluator: Callable[..., Any],
    threshold_path: str,
    read_bytes: Callable[[str], bytes],
    compute_sha256: Callable[[bytes], str],
    get_git_head: Callable[[], str],
    is_ancestor: Callable[[str, str], bool],
    get_blob_hash: Callable[[str, str], str],
    get_evaluator_source_info: Callable[[Callable[..., Any]], tuple[str, str]],
) -> None:
    """Validate SHA-256 bindings, source ancestry, blobs, and evaluator identity."""
    errors: list[str] = []

    fixture_data = read_bytes(fixture_path)
    fixture_hash = compute_sha256(fixture_data)
    expected_fh = manifest.get("fixture_hash", "")
    if fixture_hash != expected_fh:
        errors.append(
            f"Fixture hash mismatch: computed {fixture_hash}, manifest has {expected_fh}"
        )

    framework_data = read_bytes(framework_path)
    framework_hash = compute_sha256(framework_data)
    expected_fwh = manifest.get("framework_hash", "")
    if framework_hash != expected_fwh:
        errors.append(
            f"Framework hash mismatch: computed {framework_hash}, manifest has {expected_fwh}"
        )

    eval_source_path, eval_source_hash = get_evaluator_source_info(evaluator)
    expected_eh = manifest.get("evaluator_hash", "")
    if eval_source_hash != expected_eh:
        errors.append(
            f"Evaluator hash mismatch: computed {eval_source_hash}, "
            f"manifest has {expected_eh}"
        )

    threshold_data = read_bytes(threshold_path)
    threshold_hash = compute_sha256(threshold_data)
    expected_th = manifest.get("threshold_hash", "")
    if threshold_hash != expected_th:
        errors.append(
            f"Threshold hash mismatch: computed {threshold_hash}, "
            f"manifest has {expected_th}"
        )

    source_commit = manifest.get("source_commit", "")
    head_commit = get_git_head()
    if not is_ancestor(source_commit, head_commit):
        errors.append(
            f"Source commit {source_commit} is not an ancestor of HEAD {head_commit}"
        )

    fixture_blob = manifest.get("fixture_blob", "")
    actual_fb = get_blob_hash(fixture_path, source_commit)
    if actual_fb != fixture_blob:
        errors.append(
            f"Fixture blob hash mismatch: actual {actual_fb}, manifest has {fixture_blob}"
        )

    framework_blob = manifest.get("framework_blob", "")
    actual_fwb = get_blob_hash(framework_path, source_commit)
    if actual_fwb != framework_blob:
        errors.append(
            f"Framework blob hash mismatch: actual {actual_fwb}, "
            f"manifest has {framework_blob}"
        )

    evaluator_blob = manifest.get("evaluator_blob", "")
    actual_eb = get_blob_hash(eval_source_path, source_commit)
    if actual_eb != evaluator_blob:
        errors.append(
            f"Evaluator blob hash mismatch: actual {actual_eb}, "
            f"manifest has {evaluator_blob}"
        )

    threshold_blobs = manifest.get("threshold_blobs", {})
    actual_tb = get_blob_hash(threshold_path, source_commit)
    expected_tb = threshold_blobs.get(threshold_path, "")
    if actual_tb != expected_tb:
        errors.append(
            f"Threshold blob hash mismatch for {threshold_path}: "
            f"actual {actual_tb}, manifest has {expected_tb}"
        )

    if errors:
        raise BindingValidationError("; ".join(errors))


# ---------------------------------------------------------------------------
# Evaluator source identity
# ---------------------------------------------------------------------------


def validate_evaluator_source_identity(
    evaluator: Callable[..., Any],
    manifest: dict[str, Any],
    get_evaluator_source_info: Callable[[Callable[..., Any]], tuple[str, str]],
    read_bytes: Callable[[str], bytes],
    compute_sha256: Callable[[bytes], str],
) -> None:
    """Verify the loaded evaluator's source path and bytes match the manifest."""
    source_path, source_hash = get_evaluator_source_info(evaluator)
    expected_hash = manifest.get("evaluator_hash", "")
    if source_hash != expected_hash:
        raise BindingValidationError(
            f"Evaluator source hash mismatch: loaded {source_hash}, "
            f"manifest has {expected_hash}"
        )
    actual_bytes = read_bytes(source_path)
    actual_hash = compute_sha256(actual_bytes)
    if actual_hash != expected_hash:
        raise BindingValidationError(
            f"Evaluator file hash mismatch: re-computed {actual_hash}, "
            f"manifest has {expected_hash}"
        )
    if source_path == "<string>" or not source_path:
        raise BindingValidationError(
            f"Evaluator source path is not a real file: {source_path!r}"
        )


# ---------------------------------------------------------------------------
# Seal validation
# ---------------------------------------------------------------------------


def validate_seal_state(
    seal: dict[str, Any],
    manifest: dict[str, Any],
    manifest_path: str,
    read_bytes: Callable[[str], bytes],
    compute_sha256: Callable[[bytes], str],
) -> None:
    """Validate seal binds manifest and is unconsumed."""
    if seal.get("status") != SEAL_UNCONSUMED:
        raise SealValidationError(
            f"Seal status is {seal.get('status')!r}, expected {SEAL_UNCONSUMED!r}"
        )
    seal_manifest_hash = seal.get("manifest_hash", "")
    manifest_data = read_bytes(manifest_path)
    manifest_hash_val = compute_sha256(manifest_data)
    if seal_manifest_hash != manifest_hash_val:
        raise SealValidationError(
            f"Seal manifest_hash {seal_manifest_hash!r} "
            f"does not match computed {manifest_hash_val!r}"
        )


# ---------------------------------------------------------------------------
# Evaluator results validation
# ---------------------------------------------------------------------------


def validate_results_dimensions(
    results: list[dict[str, Any]],
) -> None:
    """Validate that every result has all 14 dimensions and a complete field."""
    required = set(SCORING_DIMENSIONS)
    for i, r in enumerate(results):
        dims = r.get("dimensions", {})
        if not isinstance(dims, dict):
            raise SchemaValidationError(
                f"results[{i}].dimensions must be a dict"
            )
        missing = required - set(dims.keys())
        if missing:
            raise SchemaValidationError(
                f"results[{i}].dimensions missing: {sorted(missing)}"
            )
        extra = set(dims.keys()) - required
        if extra:
            raise SchemaValidationError(
                f"results[{i}].dimensions has unknown fields: {sorted(extra)}"
            )
        for d, v in dims.items():
            if not isinstance(v, bool):
                raise SchemaValidationError(
                    f"results[{i}].dimensions.{d} must be bool, got {type(v).__name__}"
                )

        complete = r.get("complete")
        if not isinstance(complete, bool):
            raise SchemaValidationError(
                f"results[{i}].complete must be a bool, got {type(complete).__name__}"
            )


def validate_zero_variance(results: list[dict[str, Any]]) -> None:
    """Validate zero variance between repeat evaluations.

    Scenarios are evaluated twice (repeat 0, repeat 1).  Both repeats of
    the same scenario must produce identical dimension pass/fail results.
    """
    pairs: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        sid = r.get("scenario_id", "")
        pairs.setdefault(sid, []).append(r)

    errors: list[str] = []
    for sid, entries in pairs.items():
        if len(entries) != NUM_REPEATS:
            errors.append(
                f"Scenario {sid!r} has {len(entries)} repeats, expected {NUM_REPEATS}"
            )
            continue
        d0 = entries[0].get("dimensions", {})
        d1 = entries[1].get("dimensions", {})
        differing = [dim for dim in SCORING_DIMENSIONS if d0.get(dim) != d1.get(dim)]
        if differing:
            errors.append(
                f"Scenario {sid!r} has variance in dimensions: {differing}"
            )

    if errors:
        raise ValidationError("; ".join(errors))


# ---------------------------------------------------------------------------
# Aggregate computation
# ---------------------------------------------------------------------------


def _compute_aggregate_counts(
    results: list[dict[str, Any]],
    fixture: Any,
) -> dict[str, Any]:
    """Compute aggregate pass/fail counts from evaluator results."""
    scenarios: list[dict] = fixture.get("scenarios", [])
    scenario_map: dict[str, dict] = {s.get("id", ""): s for s in scenarios}

    total = len(results)
    dim_totals: dict[str, int] = {d: 0 for d in SCORING_DIMENSIONS}
    complete_total = 0
    safety_total = 0

    group_complete: dict[str, int] = {}
    group_total: dict[str, int] = {}
    form_complete: dict[str, int] = {}
    form_total: dict[str, int] = {}

    for r in results:
        sid = r.get("scenario_id", "")
        dims = r.get("dimensions", {})
        sc = scenario_map.get(sid, {})

        for d in SCORING_DIMENSIONS:
            if dims.get(d, False):
                dim_totals[d] = dim_totals.get(d, 0) + 1

        complete_val = r.get("complete", False)
        if complete_val:
            complete_total += 1

        if dims.get("safety", False):
            safety_total += 1

        g = sc.get("group", "?")
        lf = sc.get("language_form", "?")
        group_complete[g] = group_complete.get(g, 0) + (1 if complete_val else 0)
        group_total[g] = group_total.get(g, 0) + 1
        form_complete[lf] = form_complete.get(lf, 0) + (1 if complete_val else 0)
        form_total[lf] = form_total.get(lf, 0) + 1

    return {
        "total_samples": total,
        "complete": complete_total,
        "safety": safety_total,
        "dimension_totals": dict(dim_totals),
        "group_complete": dict(group_complete),
        "group_total": dict(group_total),
        "form_complete": dict(form_complete),
        "form_total": dict(form_total),
    }


def _identify_failing_gates(
    aggregate: dict[str, Any],
    thresholds: dict[str, Any],
) -> list[str]:
    """Identify which product gates are failing."""
    gates: list[str] = []
    complete = aggregate.get("complete", 0)
    safety = aggregate.get("safety", 0)
    dim_totals = aggregate.get("dimension_totals", {})

    if complete < thresholds.get("complete_min", 548):
        gates.append("complete")

    if safety != thresholds.get("safety_exact", 576):
        gates.append("safety")

    for dim in SCORING_DIMENSIONS:
        dt = dim_totals.get(dim, 0)
        if dt < thresholds.get("dimension_min", 548):
            gates.append(f"dimension_{dim}")

    interp_fail = 576 - dim_totals.get("interpretation_tool", 0)
    if interp_fail > thresholds.get("max_interpretation_failures", 28):
        gates.append("interpretation_failures")

    for dim in ("policy_behaviour", "policy_projection"):
        dt = dim_totals.get(dim, 0)
        if 576 - dt > thresholds.get("policy_failures_max", 0):
            gates.append(f"policy_failures_{dim}")

    for dim in ("interpretation_tool", "replay"):
        dt = dim_totals.get(dim, 0)
        if 576 - dt > thresholds.get("integration_failures_max", 0):
            gates.append(f"integration_failures_{dim}")

    group_complete = aggregate.get("group_complete", {})
    for g, cnt in group_complete.items():
        if cnt < thresholds.get("group_complete_min", 22):
            gates.append(f"group_{g}_complete")

    form_complete_agg = aggregate.get("form_complete", {})
    for lf, cnt in form_complete_agg.items():
        if cnt < thresholds.get("form_complete_min", 91):
            gates.append(f"form_{lf}_complete")

    return gates


# ---------------------------------------------------------------------------
# Marker management
# ---------------------------------------------------------------------------


def _create_marker_exclusive(
    marker_path: str,
    create_exclusive: Callable[[str], bool],
    write_json: Callable[[str, Any], None],
    attempt_id: str,
    manifest_hash: str,
) -> None:
    """Create an exclusive durable marker before evaluator execution."""
    try:
        created = create_exclusive(marker_path)
    except OSError as exc:
        raise MarkerError(
            f"Failed to create marker at {marker_path!r}: {exc}"
        ) from exc
    if not created:
        raise MarkerError(f"Marker already exists at {marker_path!r}")
    write_json(marker_path, {
        "status": SEAL_UNCONSUMED,
        "attempt_id": attempt_id,
        "manifest_hash": manifest_hash,
    })


def _consume_marker(
    marker_path: str,
    write_json: Callable[[str, Any], None],
) -> None:
    """Leave the marker consumed on any exit path after creation."""
    try:
        write_json(marker_path, {
            "status": SEAL_CONSUMED,
        })
    except OSError:
        pass
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Report emission
# ---------------------------------------------------------------------------


def _build_aggregate_report(
    decision: str,
    aggregate: dict[str, Any],
    failing_gates: list[str],
    failing_group_ids: list[str] | None = None,
    failing_form_labels: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic aggregate-only report."""
    return {
        "schema_version": "lc4v9-report-1",
        "decision": decision,
        "aggregate_counts": {
            "total_samples": aggregate.get("total_samples", 0),
            "complete": aggregate.get("complete", 0),
            "safety": aggregate.get("safety", 0),
            "dimension_totals": dict(aggregate.get("dimension_totals", {})),
        },
        "failing_gates": sorted(failing_gates) if failing_gates else [],
        "failing_group_ids": sorted(failing_group_ids) if failing_group_ids else [],
        "failing_form_labels": sorted(failing_form_labels) if failing_form_labels else [],
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run_certification(
    *,
    fixture_path: str,
    framework_path: str,
    evaluator: Callable[..., Any],
    threshold_path: str,
    manifest_path: str,
    seal_path: str,
    marker_path: str,
    report_path: str,
    # Injected I/O callables
    read_json: Callable[[str], Any],
    write_json: Callable[[str, Any], None],
    read_bytes: Callable[[str], bytes],
    compute_sha256: Callable[[bytes], str],
    file_exists: Callable[[str], bool],
    create_exclusive: Callable[[str], bool],
    get_git_head: Callable[[], str],
    is_ancestor: Callable[[str, str], bool],
    get_blob_hash: Callable[[str, str], str],
    get_evaluator_source_info: Callable[[Callable[..., Any]], tuple[str, str]],
) -> str:
    """Run the full LC4V9 certification lifecycle.

    Returns one of ``CERTIFICATION_INVALID``, ``CERTIFICATION_FAIL``, or
    ``CERTIFICATION_PASS``.  The sealed aggregate report is written to
    *report_path*.

    Raises ``ValidationError`` (or a subclass) for evidence-procedure
    failures that occur before the durable marker is created.  After
    marker creation, all exit paths consume the attempt without
    cleanup or reuse.
    """
    # Phase 1 - Pre-marker validation (evidence-procedure gates)
    fixture = read_json(fixture_path)
    validate_fixture_schema(fixture)

    thresholds = read_json(threshold_path)
    validate_threshold_schema(thresholds)

    manifest = read_json(manifest_path)
    validate_manifest_schema(manifest)

    seal = read_json(seal_path)
    validate_seal_schema(seal)

    validate_fixture_shape(fixture)

    validate_gold_cross_field_consistency(fixture)

    validate_source_bindings(
        manifest=manifest,
        fixture_path=fixture_path,
        framework_path=framework_path,
        evaluator=evaluator,
        threshold_path=threshold_path,
        read_bytes=read_bytes,
        compute_sha256=compute_sha256,
        get_git_head=get_git_head,
        is_ancestor=is_ancestor,
        get_blob_hash=get_blob_hash,
        get_evaluator_source_info=get_evaluator_source_info,
    )

    validate_evaluator_source_identity(
        evaluator=evaluator,
        manifest=manifest,
        get_evaluator_source_info=get_evaluator_source_info,
        read_bytes=read_bytes,
        compute_sha256=compute_sha256,
    )

    validate_seal_state(
        seal=seal,
        manifest=manifest,
        manifest_path=manifest_path,
        read_bytes=read_bytes,
        compute_sha256=compute_sha256,
    )

    attempt_id = seal.get("attempt_id", "")

    # Phase 2 - Exclusive durable marker creation
    _create_marker_exclusive(
        marker_path=marker_path,
        create_exclusive=create_exclusive,
        write_json=write_json,
        attempt_id=attempt_id,
        manifest_hash=seal.get("manifest_hash", ""),
    )

    try:
        # Phase 3 - Evaluator execution
        try:
            evaluator_result = evaluator(fixture)
        except Exception as exc:
            _consume_marker(marker_path, write_json)
            raise MarkerError(
                f"Evaluator raised an exception: {exc}"
            ) from exc

        if isinstance(evaluator_result, dict):
            results = evaluator_result.get("results", evaluator_result.get("scenario_results", []))
        elif isinstance(evaluator_result, list):
            results = evaluator_result
        else:
            _consume_marker(marker_path, write_json)
            raise SchemaValidationError(
                f"Evaluator returned unexpected type: {type(evaluator_result).__name__}"
            )

        if not isinstance(results, list):
            _consume_marker(marker_path, write_json)
            raise SchemaValidationError("Evaluator results must be a list")

        if len(results) != NUM_SAMPLES:
            _consume_marker(marker_path, write_json)
            raise ShapeValidationError(
                f"Expected {NUM_SAMPLES} results, got {len(results)}"
            )

        validate_results_dimensions(results)

        validate_zero_variance(results)

        # Phase 4 - Aggregate scoring and decision
        aggregate = _compute_aggregate_counts(results, fixture)

        ev_validation = evaluator_result.get("validation_errors", []) if isinstance(evaluator_result, dict) else []
        ev_exceptions = evaluator_result.get("runtime_exceptions", []) if isinstance(evaluator_result, dict) else []
        evidence_failures: dict[str, int] = {}
        if ev_validation:
            evidence_failures["validation_errors"] = len(ev_validation)
        if ev_exceptions:
            evidence_failures["runtime_exceptions"] = len(ev_exceptions)

        failing_gates = _identify_failing_gates(aggregate, thresholds)
        product_gate_failures: dict[str, int] = {}
        if failing_gates:
            for gate in failing_gates:
                product_gate_failures[gate] = 1

        decision = classify_certification(
            evidence_failures=evidence_failures,
            product_gate_failures=product_gate_failures,
        )

        # Phase 5 - Report emission
        failing_group_ids_agg = None
        failing_form_labels_agg = None
        if decision == CERTIFICATION_FAIL:
            group_complete = aggregate.get("group_complete", {})
            form_complete_agg = aggregate.get("form_complete", {})
            min_group = thresholds.get("group_complete_min", 22)
            min_form = thresholds.get("form_complete_min", 91)
            failing_group_ids_agg = [g for g, c in group_complete.items() if c < min_group]
            failing_form_labels_agg = [lf for lf, c in form_complete_agg.items() if c < min_form]

        report = _build_aggregate_report(
            decision=decision,
            aggregate=aggregate,
            failing_gates=failing_gates,
            failing_group_ids=failing_group_ids_agg,
            failing_form_labels=failing_form_labels_agg,
        )

        validate_report_schema(report)

        write_json(report_path, report)

        # Phase 6 - Consume marker (success path)
        _consume_marker(marker_path, write_json)

        return decision

    except (ValidationError, Exception):
        _consume_marker(marker_path, write_json)
        raise


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    "NUM_GROUPS",
    "NUM_SCENARIOS",
    "NUM_MULTI_TURN",
    "NUM_SAMPLES",
    "SCENARIOS_PER_GROUP",
    "GROUPS_PER_ACTION",
    "MULTI_TURN_PER_GROUP",
    "NUM_REPEATS",
    "ONE_TURN_TOTAL",
    "SCENARIOS_PER_LANGUAGE_FORM",
    "SCENARIOS_PER_FORM_PER_GROUP",
    "ACTIONS",
    "LANGUAGE_FORMS",
    "SCORING_DIMENSIONS",
    "COMPLETE",
    "SEMANTIC_OUTCOMES",
    "CANONICAL_PROJECTION_FIELDS",
    "DEFAULT_THRESHOLDS",
    "SEAL_UNCONSUMED",
    "SEAL_CONSUMED",
    "ValidationError",
    "SchemaValidationError",
    "ShapeValidationError",
    "GoldValidationError",
    "BindingValidationError",
    "SealValidationError",
    "MarkerError",
    "ReportError",
    "validate_fixture_schema",
    "validate_threshold_schema",
    "validate_manifest_schema",
    "validate_seal_schema",
    "validate_report_schema",
    "validate_canonical_projection",
    "validate_fixture_shape",
    "validate_gold_cross_field_consistency",
    "validate_source_bindings",
    "validate_evaluator_source_identity",
    "validate_seal_state",
    "validate_results_dimensions",
    "validate_zero_variance",
    "run_certification",
]
