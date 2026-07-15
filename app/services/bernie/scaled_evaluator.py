"""Provider-free generic LC4 scaled evaluator for development corpus.

Reuses the LC3 deterministic interpretation, replay, and scorer public APIs
without copying expected scenario fields into observations.  Evaluates exactly
1,152 development variants with two deterministic repeats each (2,304 samples),
preserving the 288-trajectory subset and all Silver/pending metadata.

Strict generic sealed-holdout interface using only miniature dummy records in
tests.  The actual 24-group holdout is authored by Sol separately after all
DeepSeek and Gemini work ends.

Development evidence includes bounded per-case findings for repair.  Holdout
reports are aggregate-only and reject any payload that exposes scenario/group/
variant IDs, utterances, dialogue turns, expected labels/outcomes/tools/deltas,
source spans, normalized values, case findings, or per-case failures.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
    score_interpretation_replay_pair,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    CorpusSummary,
    CriticalSliceEntry,
    CriticalSliceReport,
    FailureLayer,
    build_corpus_summary,
)
from app.services.bernie.scale_corpus import (
    ALL_ACTIONS,
    ALL_DIALOGUE_FORMS,
    ALL_ENTITY_SEMANTICS,
    ALL_LANGUAGE_FORMS,
    ALL_TEMPORAL_RELATIONS,
    DEVELOPMENT_GROUP_COUNT,
    DEV_GROUP_PREFIX,
    DEV_MT_PREFIX,
    DEV_VARIANT_PREFIX,
    MULTI_TURN_VARIANTS_PER_GROUP,
    SURFACE_VARIANTS_PER_GROUP,
    TOTAL_INDIVIDUAL_RECORDS,
    TOTAL_TRAJECTORIES,
    DevelopmentOnlyLoader,
    ScaleCorpus,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LC4_SCALED_REPORT_SCHEMA_VERSION = "lc4.scaled_evaluation.v1"
EXPECTED_REPEATS = 2
EXPECTED_TOTAL_SAMPLES = TOTAL_INDIVIDUAL_RECORDS * EXPECTED_REPEATS  # 2304

# LC1 Gold scenario count preserved from LC3
EXPECTED_LC1_GOLD_CELLS = 3
# Adjudicated gap count preserved from LC3 report
EXPECTED_ADJUDICATED_GAPS = 152061


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------

def _stable_hash(content: str) -> str:
    """Deterministic SHA-256 hex digest from stable JSON encoding."""
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Stable JSON without whitespace, sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Sealed holdout interface (generic — test only with dummy records)
# ---------------------------------------------------------------------------

# The only permitted purpose for a sealed holdout evaluation
_SEALED_HOLDOUT_PURPOSE = "sealed_baseline_evaluation"
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_IDENTITY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass(frozen=True)
class SealedHoldoutReceipt:
    """Receipt metadata for a sealed holdout evaluation.

    This is a generic interface only.  The actual 24-group holdout is
    authored by Sol after all DeepSeek and Gemini work ends.
    Test only with miniature dummy records.

    The purpose is fixed to ``sealed_baseline_evaluation`` and cannot
    be caller-configured to another matching string.
    """

    manifest_hash: str
    evaluator_identity: str
    evaluation_id: str
    is_sealed: bool = False

    purpose: str = _SEALED_HOLDOUT_PURPOSE

    def __post_init__(self) -> None:
        """Validate that no field is blank or malformed."""
        if not isinstance(self.manifest_hash, str) or not _SHA256_RE.fullmatch(self.manifest_hash):
            raise ValueError("manifest_hash must be a lowercase sha256 digest")
        if not isinstance(self.evaluator_identity, str) or not _IDENTITY_RE.fullmatch(self.evaluator_identity):
            raise ValueError("evaluator_identity must be a non-blank stable identifier")
        if not isinstance(self.evaluation_id, str) or not _IDENTITY_RE.fullmatch(self.evaluation_id):
            raise ValueError("evaluation_id must be a non-blank stable identifier")
        if self.purpose != _SEALED_HOLDOUT_PURPOSE:
            raise ValueError(
                f"purpose must be {_SEALED_HOLDOUT_PURPOSE!r}, "
                f"got {self.purpose!r}"
            )

    def validate_access(
        self,
        manifest_hash: str,
        purpose: str,
        *,
        evaluator_identity: str,
        evaluation_id: str,
    ) -> bool:
        """Fail-closed: wrong or reused credentials are rejected.

        The supplied expected evaluator_identity and evaluation_id must
        match the sealed receipt as well as the manifest hash and purpose.
        """
        if not self.is_sealed:
            return False
        if manifest_hash != self.manifest_hash:
            return False
        if purpose != self.purpose:
            return False
        if evaluator_identity != self.evaluator_identity:
            return False
        if evaluation_id != self.evaluation_id:
            return False
        return True


@dataclass(frozen=True)
class SingleUseLedger:
    """Single-use in-memory ledger for sealed holdout access.

    Tracks whether the capability has already been consumed.
    """
    capability: SealedHoldoutReceipt
    _consumed: bool = False

    def consume(
        self,
        manifest_hash: str,
        purpose: str,
        *,
        evaluator_identity: str,
        evaluation_id: str,
    ) -> bool:
        """Attempt to consume the capability once.

        Single use is consumed only after *every* credential check passes
        (manifest hash, purpose, evaluator identity, and evaluation ID).
        Returns True if access is granted.  Subsequent attempts fail.
        """
        if self._consumed:
            return False
        if not self.capability.validate_access(
            manifest_hash,
            purpose,
            evaluator_identity=evaluator_identity,
            evaluation_id=evaluation_id,
        ):
            return False
        object.__setattr__(self, "_consumed", True)
        return True

    @property
    def is_consumed(self) -> bool:
        return self._consumed


# ---------------------------------------------------------------------------
# Aggregate-only holdout sanitizer / report builder
# ---------------------------------------------------------------------------

# Prohibited key aliases (checked case-insensitively) in holdout report content.
# Covers identifier, utterance, expected, observed, tool, delta, span,
# normalized, finding, and per-case aliases at any nesting depth.
_PROHIBITED_HOLDOUT_KEYS: frozenset[str] = frozenset({
    # scenario / variant / group identifiers
    "scenario_id", "scenario", "group_id", "variant_id", "variant",
    # utterances and dialogue
    "utterance", "utterance_text", "dialogue_turn", "turn_text", "turn",
    "observation_text", "receptionist_text", "patient_text",
    # expected / observed outcome labels
    "expected_outcome", "expected", "expected_label", "observed",
    "observed_outcome", "actual_outcome", "actual",
    # expected tools / tool sequences
    "expected_tool", "expected_tool_sequence", "tool_sequence",
    "expected_delta", "appointment_delta", "delta",
    # source spans
    "source_span", "source_spans", "span", "span_text",
    # normalized values
    "normalized_value", "normalized",
    # case findings / per-case results
    "case_finding", "case_findings", "finding", "findings",
    "per_case_result", "per_case", "result", "per_sample",
    # forbidden content
    "forbidden_outcome", "forbidden_tool",
})


def sanitize_holdout_report(report: dict[str, Any]) -> dict[str, Any]:
    """Sanitize a holdout report, rejecting prohibited keys/values.

    Only aggregate/slice counts, fractions, partition/corpus/report hashes,
    version, repeat count, and sealed receipt metadata are allowed.

    Uses a strict recursive allowlist/schema.  Rejects unknown nested keys,
    non-aggregate nested structures, identifier/utterance/expected/observed/
    tool/delta/span/normalized/finding/per-case key aliases case-insensitively,
    and forbidden strings at any nesting depth including tuple/list values.

    Raises ValueError if any prohibited content is found.
    """
    # Strict recursive check at every nesting depth including tuple values
    _check_holdout_structure(report)

    allowed_top_keys = {
        "schema_version", "sealed_receipt", "partition",
        "corpus_hash", "manifest_hash", "report_hash",
        "total_groups", "total_variants", "total_trajectories",
        "total_samples", "repeat_count",
        "aggregate", "critical_slices", "per_dimension", "variance",
        "coverage_lattice",
    }

    # Enforce top-level structure
    for key in report:
        if key not in allowed_top_keys:
            raise ValueError(
                f"Holdout report contains prohibited top-level key: {key!r}"
            )

    _check_holdout_top_level_values(report)

    # Check aggregate section
    if "aggregate" in report:
        agg = report["aggregate"]
        if not isinstance(agg, dict):
            raise ValueError(
                f"Holdout aggregate must be a dict, got {type(agg).__name__}"
            )
        for agg_key in agg:
            if agg_key not in ("passed", "failed", "total", "pass_fraction"):
                raise ValueError(
                    f"Holdout aggregate contains prohibited key: {agg_key!r}"
                )
            val = agg[agg_key]
            if not isinstance(val, (int, float)):
                raise ValueError(
                    f"Holdout aggregate.{agg_key} must be numeric, "
                    f"got {type(val).__name__}"
                )

    # Check per_dimension section
    if "per_dimension" in report:
        _check_dimension_section(report["per_dimension"])

    # Check critical_slices section
    if "critical_slices" in report:
        _check_slice_section(report["critical_slices"])

    return report


def _check_holdout_structure(obj: Any, path: str = "") -> None:
    """Recursively check for prohibited key aliases at every nesting depth.

    Checks dict keys case-insensitively, string values for forbidden patterns,
    and also iterates through tuple values for string content.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = key.lower()
            for prohibited in _PROHIBITED_HOLDOUT_KEYS:
                if prohibited == key_lower:
                    raise ValueError(
                        f"Holdout report contains prohibited key {key!r}"
                        f" at {path}"
                    )
            _check_holdout_structure(value, f"{path}.{key}")
            if isinstance(value, str):
                _check_holdout_string_value(value, f"{path}.{key}")
            elif isinstance(value, (list, tuple)):
                _check_holdout_sequence(value, f"{path}.{key}")
    elif isinstance(obj, (list, tuple)):
        _check_holdout_sequence(obj, path)


def _check_holdout_sequence(items: list | tuple, path: str) -> None:
    for idx, item in enumerate(items):
        item_path = f"{path}[{idx}]"
        if isinstance(item, str):
            _check_holdout_string_value(item, item_path)
        elif isinstance(item, dict):
            _check_holdout_structure(item, item_path)
        elif isinstance(item, (list, tuple)):
            _check_holdout_sequence(item, item_path)


def _check_holdout_string_value(value: str, path: str) -> None:
    """Check a string value against prohibited patterns (generic dummy names)."""
    lower = value.lower()
    # Generic dummy-dev patterns that should never appear in holdout reports
    prohibited_patterns = [
        "lc4_dw1_dev_group", "lc4_dw1_dev_var", "lc4_dw1_dev_mt",
        "margaret thompson", "dr shera", "dr patel",
        "appointment for", "book margaret", "cancel margaret",
    ]
    for pattern in prohibited_patterns:
        if pattern in lower:
            raise ValueError(
                f"Holdout report contains prohibited pattern {pattern!r}"
                f" in value at {path}"
            )


def _check_dimension_section(dim: dict[str, Any]) -> None:
    """Check per_dimension section for prohibited content."""
    if not isinstance(dim, dict):
        raise ValueError(
            f"Holdout per_dimension must be a dict, "
            f"got {type(dim).__name__}"
        )
    allowed_dim_keys = {
        "scenario_count", "sample_count", "repeats_per_scenario",
        "aggregate", "semantic_fields", "downstream_outcome",
        "interpretation_tools", "replay_tool_sequence", "clarification",
        "authority", "appointment_deltas", "audit_deltas", "safety",
        "interpretation_failures", "policy_failures",
        "integration_failures", "safety_failures",
        "simultaneous_layers",
    }
    for key in dim:
        if key not in allowed_dim_keys:
            raise ValueError(
                f"Holdout per_dimension contains prohibited key: {key!r}"
            )

    count_keys = {
        "scenario_count", "sample_count", "repeats_per_scenario",
        "interpretation_failures", "policy_failures",
        "integration_failures", "safety_failures",
    }
    score_keys = {
        "aggregate", "downstream_outcome", "interpretation_tools",
        "replay_tool_sequence", "clarification", "appointment_deltas",
        "audit_deltas", "safety",
    }
    for key in count_keys & dim.keys():
        _require_nonnegative_int(dim[key], f"per_dimension.{key}")
    for key in score_keys & dim.keys():
        _check_score_counts(dim[key], f"per_dimension.{key}")

    if "semantic_fields" in dim:
        fields = dim["semantic_fields"]
        if not isinstance(fields, dict):
            raise ValueError("Holdout semantic_fields must be a dict")
        allowed_fields = {
            "intended_action", "action_semantics", "temporal_relation",
            "normalized_values", "entity_semantics", "requires_clarification",
        }
        _reject_unknown_keys(fields, allowed_fields, "per_dimension.semantic_fields")
        for key, value in fields.items():
            _check_score_counts(value, f"per_dimension.semantic_fields.{key}")

    if "authority" in dim:
        authority = dim["authority"]
        if not isinstance(authority, dict):
            raise ValueError("Holdout authority must be a dict")
        allowed_authority = {
            "passed", "failed", "total", "authority_correct",
            "authority_incorrect", "safety_violations",
        }
        _reject_unknown_keys(authority, allowed_authority, "per_dimension.authority")
        for key, value in authority.items():
            _require_nonnegative_int(value, f"per_dimension.authority.{key}")

    if "simultaneous_layers" in dim:
        layers = dim["simultaneous_layers"]
        if not isinstance(layers, dict):
            raise ValueError("Holdout simultaneous_layers must be a dict")
        allowed_layers = {
            "safety_only", "interpretation_only", "policy_only",
            "integration_only", "interpretation_and_policy",
            "interpretation_and_integration", "multiple_layers",
        }
        _reject_unknown_keys(layers, allowed_layers, "per_dimension.simultaneous_layers")
        for key, value in layers.items():
            _require_nonnegative_int(value, f"per_dimension.simultaneous_layers.{key}")


def compute_sanitized_holdout_hash(report: dict[str, Any]) -> str:
    """Compute SHA-256 over a sanitized holdout aggregate report.

    Removes report_hash first (if present), computes canonical JSON,
    and returns the SHA-256 hex digest with ``sha256:`` prefix.
    The report must pass sanitize_holdout_report first.
    """
    # Sanitize first to reject prohibited content
    sanitize_holdout_report(report)

    report_copy = dict(report)
    report_copy.pop("report_hash", None)
    return _stable_hash(_canonical_json(report_copy))


def _check_slice_section(slices: dict[str, Any]) -> None:
    """Check critical_slices section."""
    if not isinstance(slices, dict):
        raise ValueError("Holdout critical_slices must be a dict")
    allowed_slice_keys = {
        "worst_slice", "by_action", "by_temporal_relation",
        "by_dialogue_form", "by_language_form", "by_diary_state",
        "by_entity_state", "by_gap_target", "by_trajectory_type",
        "by_tier", "by_adjudication",
    }
    for key in slices:
        if key not in allowed_slice_keys:
            raise ValueError(
                f"Holdout critical_slices contains prohibited key: {key!r}"
            )
        value = slices[key]
        if key == "worst_slice":
            if value is not None:
                _check_slice_entry(value, f"critical_slices.{key}")
        else:
            if not isinstance(value, list):
                raise ValueError(f"Holdout critical_slices.{key} must be a list")
            for index, entry in enumerate(value):
                _check_slice_entry(entry, f"critical_slices.{key}[{index}]")


def _check_holdout_top_level_values(report: dict[str, Any]) -> None:
    """Validate every allowed top-level value using an explicit schema."""
    string_keys = {"schema_version", "partition"}
    for key in string_keys & report.keys():
        if not isinstance(report[key], str) or not report[key].strip():
            raise ValueError(f"Holdout {key} must be a non-blank string")
    for key in {"corpus_hash", "manifest_hash", "report_hash"} & report.keys():
        if not isinstance(report[key], str) or not _SHA256_RE.fullmatch(report[key]):
            raise ValueError(f"Holdout {key} must be a lowercase sha256 digest")
    for key in {
        "total_groups", "total_variants", "total_trajectories",
        "total_samples", "repeat_count",
    } & report.keys():
        _require_nonnegative_int(report[key], key)

    if "sealed_receipt" in report:
        receipt = report["sealed_receipt"]
        if not isinstance(receipt, dict):
            raise ValueError("Holdout sealed_receipt must be a dict")
        allowed_receipt = {
            "manifest_hash", "purpose", "evaluator_identity",
            "evaluation_id", "is_sealed",
        }
        _reject_unknown_keys(receipt, allowed_receipt, "sealed_receipt")
        if set(receipt) != allowed_receipt:
            raise ValueError("Holdout sealed_receipt is missing required metadata")
        if not isinstance(receipt["manifest_hash"], str) or not _SHA256_RE.fullmatch(receipt["manifest_hash"]):
            raise ValueError("Holdout sealed_receipt.manifest_hash is malformed")
        if receipt["purpose"] != _SEALED_HOLDOUT_PURPOSE:
            raise ValueError("Holdout sealed_receipt purpose is invalid")
        if not isinstance(receipt["evaluator_identity"], str) or not _IDENTITY_RE.fullmatch(receipt["evaluator_identity"]):
            raise ValueError("Holdout sealed_receipt evaluator_identity is invalid")
        if not isinstance(receipt["evaluation_id"], str) or not _IDENTITY_RE.fullmatch(receipt["evaluation_id"]):
            raise ValueError("Holdout sealed_receipt evaluation_id is invalid")
        if receipt["is_sealed"] is not True:
            raise ValueError("Holdout sealed_receipt must be sealed")

    if "variance" in report:
        variance = report["variance"]
        if not isinstance(variance, dict):
            raise ValueError("Holdout variance must be a dict")
        allowed_variance = {
            "variant_scenario_count", "variant_sample_count",
            "total_repeats", "all_samples_deterministic",
        }
        _reject_unknown_keys(variance, allowed_variance, "variance")
        for key in {
            "variant_scenario_count", "variant_sample_count", "total_repeats",
        } & variance.keys():
            _require_nonnegative_int(variance[key], f"variance.{key}")
        if "all_samples_deterministic" in variance and not isinstance(
            variance["all_samples_deterministic"], bool
        ):
            raise ValueError("Holdout variance determinism flag must be boolean")

    if "coverage_lattice" in report:
        lattice = report["coverage_lattice"]
        if not isinstance(lattice, dict):
            raise ValueError("Holdout coverage_lattice must be a dict")
        allowed_lattice = {
            "total_lattice_cells", "prior_adjudicated_covered_cell_count",
            "holdout_covered_cell_count", "holdout_new_cell_count",
            "combined_adjudicated_covered_cell_count",
            "combined_adjudicated_empty_cell_count",
        }
        _reject_unknown_keys(lattice, allowed_lattice, "coverage_lattice")
        for key, value in lattice.items():
            _require_nonnegative_int(value, f"coverage_lattice.{key}")


def _reject_unknown_keys(obj: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = set(obj) - allowed
    if unknown:
        raise ValueError(f"Holdout {path} contains unknown keys: {sorted(unknown)!r}")


def _require_nonnegative_int(value: Any, path: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Holdout {path} must be a non-negative integer")


def _check_score_counts(score: Any, path: str) -> None:
    if not isinstance(score, dict):
        raise ValueError(f"Holdout {path} must be a score dict")
    allowed = {"passed", "failed", "total", "pass_fraction"}
    _reject_unknown_keys(score, allowed, path)
    for key in {"passed", "failed", "total"} & score.keys():
        _require_nonnegative_int(score[key], f"{path}.{key}")
    if "pass_fraction" in score:
        value = score["pass_fraction"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Holdout {path}.pass_fraction must be numeric")
        if not 0 <= value <= 1:
            raise ValueError(f"Holdout {path}.pass_fraction must be between 0 and 1")


def _check_slice_entry(entry: Any, path: str) -> None:
    if not isinstance(entry, dict):
        raise ValueError(f"Holdout {path} must be a dict")
    allowed = {"dimension", "slice_key", "total", "passed", "failed", "pass_fraction"}
    _reject_unknown_keys(entry, allowed, path)
    for key in {"dimension", "slice_key"} & entry.keys():
        if not isinstance(entry[key], str) or not entry[key].strip():
            raise ValueError(f"Holdout {path}.{key} must be a non-blank string")
    _check_score_counts(
        {key: value for key, value in entry.items() if key not in {"dimension", "slice_key"}},
        path,
    )


# ---------------------------------------------------------------------------
# LC4 scaled evaluator
# ---------------------------------------------------------------------------


def _split_variants_by_type(
    variants: list[ReceptionScenarioSpec],
) -> tuple[list[ReceptionScenarioSpec], list[ReceptionScenarioSpec]]:
    """Split variants into single-turn surface and multi-turn trajectory."""
    single: list[ReceptionScenarioSpec] = []
    multi: list[ReceptionScenarioSpec] = []
    for v in variants:
        if len(v.dialogue_turns) > 1:
            multi.append(v)
        else:
            single.append(v)
    return single, multi


def _attribute_failure_layers(
    result: ComposedSampleResult,
) -> dict[str, bool]:
    """Get boolean flags for all implicated failure layers."""
    return {
        "interpretation": "interpretation" in result.failure_layers,
        "policy": "policy" in result.failure_layers,
        "integration": "integration" in result.failure_layers,
        "safety": "safety" in result.failure_layers,
    }


def _build_per_dimension_scores(
    results: list[ComposedSampleResult],
    total_scenarios: int,
    total_samples: int,
    repeats: int,
) -> dict[str, Any]:
    """Build per-dimension pass/fail scores from results."""

    def _sf_passed(attr: str) -> dict[str, int]:
        passed = sum(
            1 for r in results
            if getattr(r.semantic_fields, attr, object()).passed
        )
        return {"passed": passed, "failed": total_samples - passed, "total": total_samples}

    def _dim_passed(dim: str) -> dict[str, int]:
        passed = sum(1 for r in results if getattr(r, dim, object()).passed)
        return {"passed": passed, "failed": total_samples - passed, "total": total_samples}

    # Simultaneous failure attribution
    layer_counts: dict[str, int] = {
        "interpretation": 0, "policy": 0, "integration": 0, "safety": 0,
    }
    for r in results:
        for layer in layer_counts:
            if layer in r.failure_layers:
                layer_counts[layer] += 1

    return {
        "scenario_count": total_scenarios,
        "sample_count": total_samples,
        "repeats_per_scenario": repeats,
        "aggregate": {
            "passed": sum(1 for r in results if r.all_passed),
            "failed": sum(1 for r in results if not r.all_passed),
            "total": total_samples,
        },
        "semantic_fields": {
            "intended_action": _sf_passed("intended_action"),
            "action_semantics": _sf_passed("action_semantics"),
            "temporal_relation": _sf_passed("temporal_relation"),
            "normalized_values": _sf_passed("normalized_values"),
            "entity_semantics": _sf_passed("entity_semantics"),
            "requires_clarification": _sf_passed("clarification"),
        },
        "downstream_outcome": _dim_passed("downstream_outcome"),
        "interpretation_tools": _dim_passed("interpretation_tools"),
        "replay_tool_sequence": _dim_passed("tool_sequence"),
        "clarification": _dim_passed("clarification"),
        "authority": {
            "passed": sum(1 for r in results if r.authority.passed),
            "failed": sum(1 for r in results if not r.authority.passed),
            "total": total_samples,
            "authority_correct": sum(1 for r in results if r.authority.authority_correct),
            "authority_incorrect": sum(
                1 for r in results
                if not r.authority.authority_correct and not r.authority.is_safety_violation
            ),
            "safety_violations": sum(1 for r in results if not r.safety.passed),
        },
        "appointment_deltas": _dim_passed("appointment_deltas"),
        "audit_deltas": _dim_passed("audit_deltas"),
        "safety": _dim_passed("safety"),
        "interpretation_failures": layer_counts["interpretation"],
        "policy_failures": layer_counts["policy"],
        "integration_failures": layer_counts["integration"],
        "safety_failures": layer_counts["safety"],
        "simultaneous_layers": {
            "safety_only": sum(
                1 for r in results
                if r.failure_layers == ("safety",)
            ),
            "interpretation_only": sum(
                1 for r in results
                if r.failure_layers == ("interpretation",)
            ),
            "policy_only": sum(
                1 for r in results
                if r.failure_layers == ("policy",)
            ),
            "integration_only": sum(
                1 for r in results
                if r.failure_layers == ("integration",)
            ),
            "interpretation_and_policy": sum(
                1 for r in results
                if "interpretation" in r.failure_layers and "policy" in r.failure_layers
            ),
            "interpretation_and_integration": sum(
                1 for r in results
                if "interpretation" in r.failure_layers and "integration" in r.failure_layers
            ),
            "multiple_layers": sum(
                1 for r in results if len(r.failure_layers) > 1
            ),
        },
    }


def _build_slices(
    results: list[ComposedSampleResult],
    scenarios: list[ReceptionScenarioSpec],
    summary: CorpusSummary,
) -> dict[str, Any]:
    """Build critical slices across all required dimensions."""
    scenario_map = {s.scenario_id: s for s in scenarios}

    # Define registry for all slice dimensions
    slice_registry: dict[str, dict[str, dict[str, int]]] = {
        "action": {},
        "temporal_relation": {},
        "diary_state": {},
        "entity_state": {},
        "dialogue_form": {},
        "language_form": {},
        "gap_target": {},
        "trajectory_type": {},
        "tier": {},
        "adjudication": {},
    }

    for r in results:
        sc = scenario_map.get(r.scenario_id)
        if sc is None:
            continue
        _acc(slice_registry, "action", sc.intended_action, r.all_passed)
        _acc(slice_registry, "temporal_relation", sc.temporal_relation, r.all_passed)
        _acc(slice_registry, "diary_state", sc.diary_state, r.all_passed)
        _acc(slice_registry, "entity_state", sc.entity_state, r.all_passed)
        _acc(slice_registry, "dialogue_form", sc.dialogue_form, r.all_passed)
        _acc(slice_registry, "language_form", sc.language_form, r.all_passed)
        _acc(slice_registry, "tier", sc.provenance, r.all_passed)
        _acc(slice_registry, "adjudication", sc.adjudication, r.all_passed)

        # Trajectory type
        tt = "trajectory" if len(sc.dialogue_turns) > 1 else "single_turn"
        _acc(slice_registry, "trajectory_type", tt, r.all_passed)

        # Gap target — use family prefix to determine gap category
        if sc.family:
            family_lower = sc.family.lower()
            for gt in _infer_gap_targets(sc):
                _acc(slice_registry, "gap_target", gt, r.all_passed)

    # Build entry tuples
    slices_dict: dict[str, Any] = {
        "worst_slice": _worst_slice_entry(slice_registry),
        "by_action": _entries_for(slice_registry, "action"),
        "by_temporal_relation": _entries_for(slice_registry, "temporal_relation"),
        "by_diary_state": _entries_for(slice_registry, "diary_state"),
        "by_entity_state": _entries_for(slice_registry, "entity_state"),
        "by_dialogue_form": _entries_for(slice_registry, "dialogue_form"),
        "by_language_form": _entries_for(slice_registry, "language_form"),
        "by_tier": _entries_for(slice_registry, "tier"),
        "by_adjudication": _entries_for(slice_registry, "adjudication"),
        "by_trajectory_type": _entries_for(slice_registry, "trajectory_type"),
        "by_gap_target": _entries_for(slice_registry, "gap_target"),
    }
    return slices_dict


def _infer_gap_targets(scenario: ReceptionScenarioSpec) -> list[str]:
    """Infer gap target categories from scenario fields."""
    targets: list[str] = []
    if scenario.dialogue_form in ("clarification",):
        targets.append("clarification_dialogue")
    if scenario.temporal_relation in ("interval", "unspecified"):
        targets.append("interval_unspecified_temporal")
    if scenario.entity_state in ("ambiguous", "omitted", "corrected"):
        targets.append("entity_ambiguity_omission_correction")
    if scenario.dialogue_form != "one_shot" or scenario.temporal_relation in ("interval", "unspecified"):
        targets.append("interpretation_replay_tool_selection")
    return targets


def _acc(
    registry: dict[str, dict[str, dict[str, int]]],
    dim: str,
    key: str,
    passed: bool,
) -> None:
    bucket = registry.setdefault(dim, {}).setdefault(key, {"total": 0, "passed": 0, "failed": 0})
    bucket["total"] += 1
    if passed:
        bucket["passed"] += 1
    else:
        bucket["failed"] += 1


def _worst_slice_entry(
    registry: dict[str, dict[str, dict[str, int]]],
) -> dict[str, Any] | None:
    """Find the worst-performing slice across all dimensions."""
    best_entry: dict[str, Any] | None = None
    for dim_name, dim_data in registry.items():
        for key, counts in dim_data.items():
            total = counts["total"]
            if total == 0:
                continue
            passed = counts["passed"]
            frac = passed / total
            if best_entry is None or frac < best_entry["pass_fraction"]:
                best_entry = {
                    "dimension": dim_name,
                    "slice_key": key,
                    "total": total,
                    "passed": passed,
                    "failed": counts["failed"],
                    "pass_fraction": round(frac, 4),
                }
            elif frac == best_entry["pass_fraction"] and key < best_entry["slice_key"]:
                best_entry.update({
                    "dimension": dim_name,
                    "slice_key": key,
                    "total": total,
                    "passed": passed,
                    "failed": counts["failed"],
                    "pass_fraction": round(frac, 4),
                })
    return best_entry


def _entries_for(
    registry: dict[str, dict[str, dict[str, int]]],
    dim: str,
) -> list[dict[str, Any]]:
    result = []
    for key in sorted(registry.get(dim, {})):
        counts = registry[dim][key]
        result.append({
            "slice_key": key,
            "total": counts["total"],
            "passed": counts["passed"],
            "failed": counts["failed"],
            "pass_fraction": round(counts["passed"] / counts["total"], 4) if counts["total"] > 0 else 1.0,
        })
    return result


# ---------------------------------------------------------------------------
# Candidate-aware lattice
# ---------------------------------------------------------------------------

# Full coverage lattice dimensions
_DIARY_ACTIONS = [
    "create", "move", "resize", "cancel",
    "status_change", "explain_schedule",
]
_DIARY_STATES = [
    "empty", "exact_duplicate", "overlap", "same_day_distinct",
    "terminal", "stale", "concurrent", "roster_absent",
    "break", "no_slots", "elapsed_window",
]
_ENTITY_STATES = [
    "exact", "omitted", "ambiguous", "corrected",
    "negated", "mismatched",
]
_TEMPORAL_FORMS = [
    "exact", "not_before", "not_after", "interval",
    "approximate", "unspecified",
]
_DIALOGUE_FORMS = [
    "one_shot", "clarification", "correction", "reversal",
    "ellipsis", "anaphora", "repeated", "session_restart",
]
_LANGUAGE_FORMS = [
    "plain", "paraphrase", "filler", "abbreviation",
    "typo", "speech_like", "punctuation_variant", "adversarial",
]
_TOTAL_CELLS = (
    len(_DIARY_ACTIONS) * len(_DIARY_STATES) * len(_ENTITY_STATES)
    * len(_TEMPORAL_FORMS) * len(_DIALOGUE_FORMS) * len(_LANGUAGE_FORMS)
)


def build_candidate_lattice(
    scenarios: list[ReceptionScenarioSpec],
    adjudicated_cells: set[tuple[str, str, str, str, str, str]] | None = None,
) -> dict[str, Any]:
    """Build candidate-aware lattice counts.

    Keeps the three LC1 Gold cells and 152,061 adjudicated gaps unchanged while
    reporting LC4 pending discovery separately.

    Parameters
    ----------
    scenarios :
        All scenarios in the corpus (LC4 development variants).
    adjudicated_cells :
        The three LC1 Gold adjudicated cells.  If None, uses the canonical
        Gold cells from the LC3 composed evaluation.
    """
    if adjudicated_cells is None:
        # The three LC1 Gold adjudicated cells (from LC3 Gold scenarios):
        # These are the canonical Gold cells that define the 152,061 gap count.
        adjudicated_cells = {
            ("create", "exact_duplicate", "exact", "exact", "one_shot", "plain"),
            ("create", "overlap", "exact", "exact", "one_shot", "paraphrase"),
            ("explain_schedule", "empty", "exact", "unspecified", "clarification", "plain"),
        }

    # Candidate-only cells: from LC4 development scenarios
    # (non-overlapping with adjudicated)
    candidate_covered: set[tuple[str, str, str, str, str, str]] = set()
    for s in scenarios:
        cell = (
            s.intended_action, s.diary_state, s.entity_state,
            s.temporal_relation, s.dialogue_form, s.language_form,
        )
        if cell not in adjudicated_cells:
            candidate_covered.add(cell)

    union_covered = adjudicated_cells | candidate_covered
    adjudicated_empty = _TOTAL_CELLS - len(adjudicated_cells)
    union_empty = _TOTAL_CELLS - len(union_covered)

    return {
        "adjudicated_scenario_count": len(adjudicated_cells),
        "adjudicated_covered_cell_count": len(adjudicated_cells),
        "adjudicated_empty_cell_count": adjudicated_empty,
        "expected_adjudicated_gaps_preserved": adjudicated_empty == EXPECTED_ADJUDICATED_GAPS,
        "expected_adjudicated_gaps_note": (
            f"adj_empty={adjudicated_empty}, "
            f"expected={EXPECTED_ADJUDICATED_GAPS}, "
            f"preserved={adjudicated_empty == EXPECTED_ADJUDICATED_GAPS}"
        ),
        "candidate_count_by_tier": {"silver": len(scenarios)},
        "candidate_count_by_adjudication": {"pending": len(scenarios)},
        "candidate_only_cell_count": len(candidate_covered),
        "union_covered_cell_count": len(union_covered),
        "union_empty_cell_count": union_empty,
        "total_lattice_cells": _TOTAL_CELLS,
        "pending_candidates_do_not_reduce_adjudicated_gaps": (
            union_empty <= adjudicated_empty
        ),
        "lc4_pending_discovery_count": len(scenarios),
        "lc4_pending_discovery_separate": True,
    }


# ---------------------------------------------------------------------------
# Variance detection
# ---------------------------------------------------------------------------


def compute_variance(
    results: list[ComposedSampleResult],
) -> dict[str, Any]:
    """Compute repeat variance across samples."""
    scenario_fingerprints: dict[str, set[tuple[Any, ...]]] = {}
    for r in results:
        fp = _semantic_safety_fingerprint(r)
        scenario_fingerprints.setdefault(r.scenario_id, set()).add(fp)

    variant_scenario_count = sum(
        1 for fps in scenario_fingerprints.values() if len(fps) > 1
    )
    variant_sample_count = sum(
        sum(1 for r in results if r.scenario_id == sid and len(fps) > 1)
        for sid, fps in scenario_fingerprints.items()
    )

    return {
        "variant_scenario_count": variant_scenario_count,
        "variant_sample_count": variant_sample_count,
        "total_repeats": EXPECTED_REPEATS,
        "all_samples_deterministic": (
            variant_scenario_count == 0 and variant_sample_count == 0
        ),
    }


def _semantic_safety_fingerprint(result: ComposedSampleResult) -> tuple[Any, ...]:
    """Full canonical fingerprint for variance detection."""
    s = result.semantic_fields

    def _cm(v: Any) -> Any:
        if isinstance(v, dict):
            return tuple(sorted((k, _cm(v2)) for k, v2 in v.items()))
        if isinstance(v, list):
            return tuple(_cm(x) for x in v)
        return v

    return (
        s.intended_action.observed,
        s.action_semantics.observed,
        s.temporal_relation.observed,
        _cm(s.normalized_values.observed),
        _cm(s.entity_semantics.observed),
        result.downstream_outcome.comparison.observed,
        result.tool_sequence.observed,
        result.interpretation_tools.observed,
        result.authority.authority_claim,
        result.clarification.observed_requires,
        result.clarification.observed_choices,
        result.safety.interpretation_safety_violations,
        result.safety.replay_safety_violations,
        result.failure_layers,
    )


# ---------------------------------------------------------------------------
# Bounded case findings
# ---------------------------------------------------------------------------


CASE_FINDINGS_LIMIT = 96


def _finding_from_result(r: ComposedSampleResult) -> dict[str, Any]:
    """Convert a single result to a compact finding dict."""
    return {
        "scenario_id": r.scenario_id,
        "sample_index": r.sample_index,
        "all_passed": r.all_passed,
        "failure_layer": r.failure_layer,
        "failure_layers": list(r.failure_layers),
        "semantic_fields": {
            "passed": r.semantic_fields.passed,
            "failures": r.semantic_fields.failures,
        },
        "downstream_outcome": {
            "passed": r.downstream_outcome.passed,
            "expected": r.downstream_outcome.comparison.expected,
            "observed": r.downstream_outcome.comparison.observed,
        },
        "tool_sequence": r.tool_sequence.passed,
        "interpretation_tools": r.interpretation_tools.passed,
        "authority": {
            "passed": r.authority.passed,
            "claim": r.authority.authority_claim,
            "correct": r.authority.authority_correct,
            "is_safety_violation": r.authority.is_safety_violation,
        },
        "clarification": r.clarification.passed,
        "appointment_deltas": r.appointment_deltas.passed,
        "audit_deltas": r.audit_deltas.passed,
        "safety": r.safety.passed,
    }


def _deduplicate_findings(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Remove duplicate findings from same scenario_id (repeat 0 vs 1)."""
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for f in findings:
        sid = f["scenario_id"]
        if sid not in seen:
            seen.add(sid)
            deduped.append(f)
    return deduped


def _select_deterministic_findings(
    findings: list[dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    """Select up to *limit* findings deterministically, prioritising useful
    failures across failure layers and critical slice dimensions.

    Selection policy (documented in report metadata):
      1. Deduplicate repeats so at most one finding per scenario_id.
      2. Separate into failed (primary and preferred) and passed.
      3. From failed, prioritise by failure-layer depth:
         multi-layer > integration_only > interpretation_only > policy_only.
         Within each depth tier, sort by scenario_id for determinism.
      4. If room remains after filling from failed, fill from passed
         sorted by scenario_id.
      5. Take at most *limit* total.
    """
    deduped = _deduplicate_findings(findings)

    failed = [f for f in deduped if not f["all_passed"]]
    passed = [f for f in deduped if f["all_passed"]]

    def _layer_depth(f: dict[str, Any]) -> int:
        layers = f.get("failure_layers", [])
        if len(layers) > 1:
            return 0  # multi-layer most useful
        if "integration" in layers:
            return 1
        if "interpretation" in layers:
            return 2
        if "policy" in layers:
            return 3
        return 4

    failed.sort(key=lambda f: (_layer_depth(f), f["scenario_id"]))
    passed.sort(key=lambda f: f["scenario_id"])

    selected: list[dict[str, Any]] = []
    selected.extend(failed[:limit])
    remaining = limit - len(selected)
    if remaining > 0:
        selected.extend(passed[:remaining])

    return selected[:limit]


def build_bounded_findings(
    results: list[ComposedSampleResult],
    *,
    limit: int = CASE_FINDINGS_LIMIT,
) -> dict[str, Any]:
    """Build bounded development case findings for repair.

    Returns a dict with:
      - ``findings``: the selected bounded findings list
      - ``findings_limit``: the configured maximum
      - ``findings_included``: how many were included
      - ``findings_omitted``: how many were excluded after dedup
      - ``selection_policy``: documented deterministic selection policy

    Includes scenario_id, all_passed, failure_layer(s), per-field status,
    and observed values for repair.  Does not dump unbounded detail.
    """
    if limit <= 0:
        raise ValueError(f"Case findings limit must be positive, got {limit}")

    all_findings = [
        _finding_from_result(r) for r in results
    ]

    # Track omitted count before selection
    dedup_before = len(_deduplicate_findings(all_findings))
    selected = _select_deterministic_findings(all_findings, limit=limit)
    omitted = dedup_before - len(selected)

    return {
        "findings": selected,
        "findings_limit": limit,
        "findings_included": len(selected),
        "findings_omitted": max(omitted, 0),
        "selection_policy": (
            "deterministic: deduplicate repeats (one per scenario_id), "
            "prioritise multi-layer failures, then integration-only, "
            "interpretation-only, policy-only, sorted by scenario_id; "
            "fill remaining from passed sorted by scenario_id"
        ),
    }


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------


def generate_scaled_evaluation_report(
    fixture_dir: pathlib.Path | None = None,
    repeats: int = EXPECTED_REPEATS,
) -> dict[str, Any]:
    """Generate the complete LC4 scaled evaluation report.

    Loads the development corpus, runs deterministic interpretation + replay
    with *repeats* repetitions, scores every pair, and returns a deterministic
    report dict.

    Parameters
    ----------
    fixture_dir :
        Path to the development fixtures directory.
    repeats :
        Number of deterministic repeats per variant (default 2).

    Returns
    -------
    dict
        The LC4 scaled evaluation report.
    """
    if fixture_dir is None:
        fixture_dir = _default_fixture_dir()

    # 1. Load corpus
    loader = DevelopmentOnlyLoader(fixture_dir)
    corpus: ScaleCorpus = loader.load_all()
    all_scenarios = corpus.all_variants()

    if repeats != EXPECTED_REPEATS:
        raise ValueError(
            f"Expected {EXPECTED_REPEATS} repeats, got {repeats}"
        )

    total_scenarios = len(all_scenarios)
    total_samples = total_scenarios * repeats

    if total_scenarios != TOTAL_INDIVIDUAL_RECORDS:
        raise ValueError(
            f"Expected {TOTAL_INDIVIDUAL_RECORDS} scenarios, got {total_scenarios}"
        )
    if total_samples != EXPECTED_TOTAL_SAMPLES:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL_SAMPLES} samples, got {total_samples}"
        )

    # 2. Count by type
    surface_variants, trajectory_variants = _split_variants_by_type(all_scenarios)

    # 3. Run deterministic interpretation + replay
    results: list[ComposedSampleResult] = []
    for scenario in all_scenarios:
        for sample_idx in range(repeats):
            interp = deterministic_interpret(scenario)
            # Override sample index for this repeat
            interp = interp.__class__(
                scenario_id=interp.scenario_id,
                sample_index=sample_idx,
                intended_action=interp.intended_action,
                action_semantics=interp.action_semantics,
                temporal_relation=interp.temporal_relation,
                normalized_values=interp.normalized_values,
                entity_semantics=interp.entity_semantics,
                requires_clarification=interp.requires_clarification,
                clarification_choices=interp.clarification_choices,
                selected_tool_sequence=interp.selected_tool_sequence,
                authority_claim=interp.authority_claim,
                claims_action_completed=interp.claims_action_completed,
                action_negated=interp.action_negated,
            )
            replay = deterministic_replay(scenario, interp)
            result = score_interpretation_replay_pair(scenario, interp, replay)
            results.append(result)

    # 4. Build corpus summary
    summary: CorpusSummary = build_corpus_summary(results, all_scenarios)

    # 5. Per-dimension scores
    per_dim = _build_per_dimension_scores(results, total_scenarios, total_samples, repeats)

    # 6. Critical slices
    slices = _build_slices(results, all_scenarios, summary)

    # 7. Variance
    variance = compute_variance(results)

    # 8. Bounded findings — returns dict with findings list + metadata
    findings_container = build_bounded_findings(results)

    # 9. Candidate-aware lattice
    lattice = build_candidate_lattice(all_scenarios)

    # Build report without report_hash first, so the hash covers the
    # canonical complete report payload including all sections.
    report_no_hash: dict[str, Any] = {
        "schema_version": LC4_SCALED_REPORT_SCHEMA_VERSION,
        "corpus_hash": corpus.corpus_hash,
        "partition": {
            "schema_version": "lc4.partition.v1",
            "development_group_count": DEVELOPMENT_GROUP_COUNT,
            "surface_variants_per_group": SURFACE_VARIANTS_PER_GROUP,
            "multi_turn_per_group": MULTI_TURN_VARIANTS_PER_GROUP,
            "total_groups": DEVELOPMENT_GROUP_COUNT,
            "total_variants": TOTAL_INDIVIDUAL_RECORDS,
            "total_trajectories": TOTAL_TRAJECTORIES,
            "holdout_group_count": 0,
            "holdout_total_variants": 0,
        },
        "manifest": {
            "development_groups": len(corpus.groups),
            "surface_variant_count": len(surface_variants),
            "trajectory_count": len(trajectory_variants),
            "total_scenarios": total_scenarios,
            "total_samples": total_samples,
            "repeats": repeats,
            "provenance": "silver",
            "adjudication": "pending",
        },
        "per_dimension": per_dim,
        "critical_slices": slices,
        "variance": variance,
        "case_findings": findings_container["findings"],
        "case_findings_limit": findings_container["findings_limit"],
        "case_findings_included": findings_container["findings_included"],
        "case_findings_omitted": findings_container["findings_omitted"],
        "case_findings_selection_policy": findings_container["selection_policy"],
        "candidate_aware_lattice": lattice,
    }

    # Compute authority-bearing hash over the canonical complete report payload
    report_hash = _stable_hash(_canonical_json(report_no_hash))
    report_no_hash["report_hash"] = report_hash

    return report_no_hash


def validate_report_hash(report: dict[str, Any]) -> bool:
    """Recompute the report hash and reject if mismatched.

    Removes report_hash from a copy of the report, recomputes SHA-256
    over the canonical JSON, and returns True only on exact match.
    """
    if "report_hash" not in report:
        raise ValueError("Report missing report_hash field")
    claimed = report["report_hash"]
    report_copy = dict(report)
    del report_copy["report_hash"]
    computed = _stable_hash(_canonical_json(report_copy))
    return computed == claimed


def _default_fixture_dir() -> pathlib.Path:
    """Return the default development fixture directory."""
    here = pathlib.Path(__file__).resolve().parent.parent.parent.parent
    return here / "tests" / "fixtures" / "bernie_lc4_development"


def generate_report_json(
    fixture_dir: pathlib.Path | None = None,
    repeats: int = EXPECTED_REPEATS,
) -> str:
    """Generate the deterministic LC4 report as a JSON string."""
    report = generate_scaled_evaluation_report(fixture_dir, repeats)
    return json.dumps(report, indent=2, default=str) + "\n"


# ---------------------------------------------------------------------------
# Import isolation guard
# ---------------------------------------------------------------------------

_PROHIBITED_IMPORT_PREFIXES = (
    "app.routers",
    "app.models",
    "app.db",
    "app.services.ai.providers",
    "sqlalchemy",
    "alembic",
)


def validate_scaled_evaluator_isolation() -> None:
    """Assert that this module cannot reach providers, routes, or storage."""
    import ast

    tree = ast.parse(
        pathlib.Path(__file__).read_text(encoding="utf-8")
    )
    for node in ast.walk(tree):
        imported: tuple[str, ...] = ()
        if isinstance(node, ast.Import):
            imported = tuple(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported = (node.module,)
        for module_name in imported:
            if module_name.startswith(_PROHIBITED_IMPORT_PREFIXES):
                raise RuntimeError(
                    f"Scaled evaluator imports prohibited module: {module_name}"
                )


def validate_holdout_import_isolation() -> list[str]:
    """Prove product/runtime/provider/route/DB/T3 modules do not import
    holdout capabilities or test fixtures.

    Scans the project's Python source tree for prohibited imports of
    holdout-related types or test fixtures from product modules.

    Returns a list of violation messages (empty if clean).
    """
    import ast

    violations: list[str] = []

    # Project src root
    src_root = pathlib.Path(__file__).resolve().parent.parent.parent
    if not src_root.exists():
        return violations

    # Modules that are allowed to reference holdout capabilities
    allowed_modules = {
        "app.services.bernie.scaled_evaluator",
        "tests.test_bernie_lc4_scaled_evaluator",
        "scripts.bernie_lc4_scaled_evaluation",
    }

    # Prohibited import targets (holdout capabilities)
    prohibited_imports = {
        "SealedHoldoutReceipt",
        "SingleUseLedger",
        "sanitize_holdout_report",
    }

    # Walk all Python files under src root
    for py_file in src_root.rglob("*.py"):
        # Skip tests
        if "tests" in py_file.parts:
            continue
        # Skip scripts
        if "scripts" in py_file.parts:
            continue
        # Skip the evaluator itself
        if py_file.name == "scaled_evaluator.py":
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in prohibited_imports:
                        violations.append(
                            f"{py_file}: imports {alias.name!r}"
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    if alias.name in prohibited_imports:
                        violations.append(
                            f"{py_file}: imports {alias.name!r} from {node.module}"
                        )

    return violations


__all__ = [
    "LC4_SCALED_REPORT_SCHEMA_VERSION",
    "CASE_FINDINGS_LIMIT",
    "EXPECTED_REPEATS",
    "EXPECTED_TOTAL_SAMPLES",
    "EXPECTED_LC1_GOLD_CELLS",
    "EXPECTED_ADJUDICATED_GAPS",
    "SealedHoldoutReceipt",
    "SingleUseLedger",
    "sanitize_holdout_report",
    "generate_scaled_evaluation_report",
    "generate_report_json",
    "build_candidate_lattice",
    "compute_variance",
    "build_bounded_findings",
    "validate_report_hash",
    "compute_sanitized_holdout_hash",
    "validate_scaled_evaluator_isolation",
    "validate_holdout_import_isolation",
]
