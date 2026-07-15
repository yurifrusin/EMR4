"""Provider-free contracts for the fresh LC4V2 certification holdout.

The module is deliberately content-blind.  It knows how to validate a new v2
corpus, bind it to a manifest and seal, stream it through the ordinary
deterministic interpreter/replay/scorer, and emit aggregate-only evidence.  It
does not import any earlier protected-holdout support.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    score_interpretation_replay_pair,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

CORPUS_VERSION = "lc4-holdout-v2"
EVALUATION_ID = "lc4-holdout-v2-baseline-001"
MANIFEST_SCHEMA_VERSION = "lc4v2.manifest.v1"
GROUP_SCHEMA_VERSION = "lc4v2.group.v1"
SEAL_SCHEMA_VERSION = "lc4v2.seal.v1"
AGGREGATE_SCHEMA_VERSION = "lc4v2.aggregate.v1"
EVALUATOR_VERSION = "lc4v2.composed.v1"

DIMENSION_NAMES = (
    "complete",
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "normalized_value_match",
    "entity_semantics",
    "clarification",
    "downstream_outcome",
    "tool_sequence",
    "interpretation_tools",
    "authority",
    "appointment_deltas",
    "audit_deltas",
    "safety",
)
FAILURE_LAYER_NAMES = ("interpretation", "policy", "integration", "safety")
SLICE_AXES = (
    "intended_action",
    "temporal_relation",
    "diary_state",
    "entity_state",
    "dialogue_form",
    "language_form",
)
SLICE_VALUES = {
    "intended_action": {"create", "move", "resize", "cancel", "status_change", "explain_schedule"},
    "temporal_relation": {"exact", "not_before", "not_after", "interval", "approximate", "unspecified"},
    "diary_state": {"empty", "exact_duplicate", "overlap", "same_day_distinct", "terminal", "stale", "concurrent", "roster_absent", "break", "no_slots", "elapsed_window"},
    "entity_state": {"exact", "omitted", "ambiguous", "corrected", "negated", "mismatched"},
    "dialogue_form": {"one_shot", "clarification", "correction", "reversal", "ellipsis", "anaphora", "repeated", "session_restart"},
    "language_form": {"plain", "paraphrase", "filler", "abbreviation", "typo", "speech_like", "punctuation_variant", "adversarial"},
}
FORBIDDEN_REPORT_KEYS = frozenset(
    {
        "utterance",
        "utterances",
        "dialogue_turns",
        "scenario_id",
        "group_id",
        "variant_id",
        "expected_outcome",
        "expected_outcome_kind",
        "expected_label",
        "expected_tool_sequence",
        "expected_appointment_deltas",
        "expected_audit_deltas",
        "source_spans",
        "normalized_values",
        "observation",
        "observations",
        "case_finding",
        "case_findings",
        "per_case",
        "per_case_results",
        "individual_results",
        "case_results",
    }
)


@dataclass(frozen=True)
class CorpusProfile:
    """Expected corpus shape; production values are fixed by ``PRODUCTION_PROFILE``."""

    group_count: int
    variants_per_group: int = 12
    multi_turn_per_group: int = 3
    repeat_count: int = 2

    def __post_init__(self) -> None:
        if min(
            self.group_count,
            self.variants_per_group,
            self.repeat_count,
        ) <= 0:
            raise ValueError("profile counts must be positive")
        if not 0 <= self.multi_turn_per_group <= self.variants_per_group:
            raise ValueError("invalid multi-turn count")

    @property
    def variant_count(self) -> int:
        return self.group_count * self.variants_per_group

    @property
    def multi_turn_count(self) -> int:
        return self.group_count * self.multi_turn_per_group

    @property
    def sample_count(self) -> int:
        return self.variant_count * self.repeat_count


PRODUCTION_PROFILE = CorpusProfile(group_count=24)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def sha256_digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _validate_sha256(value: str) -> str:
    if len(value) != 71 or not value.startswith("sha256:"):
        raise ValueError("digest must use sha256:<64 lowercase hex>")
    try:
        int(value[7:], 16)
    except ValueError as error:
        raise ValueError("digest must use sha256:<64 lowercase hex>") from error
    if value != value.lower():
        raise ValueError("digest must use lowercase hex")
    return value


def _validate_commit(value: str) -> str:
    if len(value) != 40:
        raise ValueError("source_commit must be a full 40-character Git SHA")
    try:
        int(value, 16)
    except ValueError as error:
        raise ValueError("source_commit must be hexadecimal") from error
    return value.lower()


class ScenarioGroupEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["lc4v2.group.v1"] = GROUP_SCHEMA_VERSION
    group_id: str = Field(pattern=r"^lc4v2_group_[0-9]{3}$")
    variants: tuple[ReceptionScenarioSpec, ...]

    @model_validator(mode="after")
    def validate_content(self) -> "ScenarioGroupEnvelope":
        if len(self.variants) != 12:
            raise ValueError("each v2 group must contain exactly 12 variants")
        if len({item.scenario_id for item in self.variants}) != 12:
            raise ValueError("scenario IDs must be unique within a group")
        multi_turn = sum(len(item.dialogue_turns) > 1 for item in self.variants)
        if multi_turn != 3:
            raise ValueError("each v2 group must contain exactly 3 multi-turn variants")
        for item in self.variants:
            if item.provenance != "gold" or item.adjudication != "adjudicated":
                raise ValueError("v2 variants must be Gold/adjudicated")
            if not item.scenario_id.startswith(f"{self.group_id}_"):
                raise ValueError("scenario ID must be namespaced by group ID")
            if "expected_outcome_kind" not in item.model_fields_set:
                raise ValueError("expected_outcome_kind must be explicit")
            if not item.source_spans:
                raise ValueError("every v2 scenario must retain source-span evidence")
            if item.initial_diary_state.get("synthetic") is not True:
                raise ValueError("initial diary state must be explicitly synthetic")
        return self


class ManifestFileEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    relative_path: str
    sha256: str

    @field_validator("relative_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if not value or path.is_absolute() or ".." in path.parts:
            raise ValueError("manifest paths must be safe relative POSIX paths")
        if len(path.parts) != 1 or path.suffix != ".json":
            raise ValueError("group entries must be top-level JSON files")
        return path.as_posix()

    @field_validator("sha256")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_sha256(value)


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["lc4v2.manifest.v1"] = MANIFEST_SCHEMA_VERSION
    corpus_version: Literal["lc4-holdout-v2"] = CORPUS_VERSION
    files: tuple[ManifestFileEntry, ...]
    group_count: int = Field(gt=0)
    variant_count: int = Field(gt=0)
    multi_turn_count: int = Field(ge=0)
    corpus_hash: str

    @field_validator("corpus_hash")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_sha256(value)

    @model_validator(mode="after")
    def validate_entries(self) -> "Manifest":
        paths = [entry.relative_path for entry in self.files]
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            raise ValueError("manifest file paths must be sorted and unique")
        if len(paths) != self.group_count:
            raise ValueError("manifest file count must equal group_count")
        return self

    def digest(self) -> str:
        return sha256_digest(canonical_json(self.model_dump(mode="json")).encode())


class PreConsumptionSeal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["lc4v2.seal.v1"] = SEAL_SCHEMA_VERSION
    corpus_version: Literal["lc4-holdout-v2"] = CORPUS_VERSION
    evaluation_id: Literal["lc4-holdout-v2-baseline-001"] = EVALUATION_ID
    state: Literal["sealed"] = "sealed"
    manifest_hash: str
    corpus_hash: str
    source_commit: str
    evaluator_version: Literal["lc4v2.composed.v1"] = EVALUATOR_VERSION
    repeat_count: Literal[2] = 2

    @field_validator("manifest_hash", "corpus_hash")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_sha256(value)

    @field_validator("source_commit")
    @classmethod
    def validate_commit(cls, value: str) -> str:
        return _validate_commit(value)


class AggregateDimension(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    passed: int = Field(ge=0)
    failed: int = Field(ge=0)


class SliceAggregate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    value: str = Field(min_length=1)
    total: int = Field(gt=0)
    complete_passed: int = Field(ge=0)
    safety_passed: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_totals(self) -> "SliceAggregate":
        if self.complete_passed > self.total or self.safety_passed > self.total:
            raise ValueError("slice pass counts cannot exceed total")
        return self


class VarianceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    variant_scenario_count: int = Field(ge=0)
    variant_sample_count: int = Field(ge=0)
    total_samples: int = Field(gt=0)


class CoverageSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    distinct_cells: int = Field(gt=0)
    scenario_count: int = Field(gt=0)


class AggregateReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["lc4v2.aggregate.v1"] = AGGREGATE_SCHEMA_VERSION
    corpus_version: Literal["lc4-holdout-v2"] = CORPUS_VERSION
    evaluation_id: Literal["lc4-holdout-v2-baseline-001"] = EVALUATION_ID
    source_commit: str
    manifest_hash: str
    corpus_hash: str
    evaluator_version: Literal["lc4v2.composed.v1"] = EVALUATOR_VERSION
    repeat_count: Literal[2] = 2
    sample_count: int = Field(gt=0)
    dimensions: dict[str, AggregateDimension]
    failure_layers: dict[str, int]
    variance: VarianceSummary
    critical_slices: dict[str, tuple[SliceAggregate, ...]]
    coverage: CoverageSummary
    report_hash: str

    @field_validator("source_commit")
    @classmethod
    def validate_commit(cls, value: str) -> str:
        return _validate_commit(value)

    @field_validator("manifest_hash", "corpus_hash", "report_hash")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_sha256(value)

    @model_validator(mode="after")
    def validate_aggregates(self) -> "AggregateReport":
        if set(self.dimensions) != set(DIMENSION_NAMES):
            raise ValueError("aggregate report must contain the exact dimensions")
        for dimension in self.dimensions.values():
            if dimension.passed + dimension.failed != self.sample_count:
                raise ValueError("every dimension must total sample_count")
        if set(self.failure_layers) != set(FAILURE_LAYER_NAMES):
            raise ValueError("aggregate report must contain exact failure layers")
        if any(
            value < 0 or value > self.sample_count
            for value in self.failure_layers.values()
        ):
            raise ValueError("failure-layer count cannot exceed sample_count")
        if self.variance.total_samples != self.sample_count:
            raise ValueError("variance total must equal sample_count")
        if self.variance.variant_sample_count > self.sample_count:
            raise ValueError("variant sample count cannot exceed sample_count")
        if set(self.critical_slices) != set(SLICE_AXES):
            raise ValueError("critical slices must contain the exact axes")
        for values in self.critical_slices.values():
            if sum(item.total for item in values) != self.sample_count:
                raise ValueError("each critical-slice axis must total sample_count")
            names = [item.value for item in values]
            if names != sorted(names) or len(names) != len(set(names)):
                raise ValueError("critical-slice values must be sorted and unique")
        for axis, values in self.critical_slices.items():
            if any(item.value not in SLICE_VALUES[axis] for item in values):
                raise ValueError("critical-slice value is outside the canonical lattice")
        if self.coverage.scenario_count * self.repeat_count != self.sample_count:
            raise ValueError("coverage scenario count must bind sample_count")
        if self.coverage.distinct_cells > self.coverage.scenario_count:
            raise ValueError("distinct cells cannot exceed scenario count")
        return self


class ConsumedSeal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["lc4v2.seal.v1"] = SEAL_SCHEMA_VERSION
    corpus_version: Literal["lc4-holdout-v2"] = CORPUS_VERSION
    evaluation_id: Literal["lc4-holdout-v2-baseline-001"] = EVALUATION_ID
    state: Literal["consumed"] = "consumed"
    manifest_hash: str
    corpus_hash: str
    source_commit: str
    evaluator_version: Literal["lc4v2.composed.v1"] = EVALUATOR_VERSION
    repeat_count: Literal[2] = 2
    report_hash: str
    consumed_at: str

    @field_validator("manifest_hash", "corpus_hash", "report_hash")
    @classmethod
    def validate_hash(cls, value: str) -> str:
        return _validate_sha256(value)

    @field_validator("source_commit")
    @classmethod
    def validate_commit(cls, value: str) -> str:
        return _validate_commit(value)

    @field_validator("consumed_at")
    @classmethod
    def validate_timestamp(cls, value: str) -> str:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("consumed_at must be timezone-aware")
        return value


def _load_group(path: Path) -> ScenarioGroupEnvelope:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid group file {path.name}: {error}") from error
    return ScenarioGroupEnvelope.model_validate(raw)


def _group_files(group_dir: Path) -> list[Path]:
    if not group_dir.is_dir():
        raise ValueError("group directory does not exist")
    files = sorted(path for path in group_dir.iterdir() if path.is_file())
    if any(path.suffix != ".json" for path in files):
        raise ValueError("group directory may contain JSON group files only")
    return files


def build_manifest(
    group_dir: Path,
    *,
    profile: CorpusProfile = PRODUCTION_PROFILE,
) -> Manifest:
    files = _group_files(group_dir)
    if len(files) != profile.group_count:
        raise ValueError("group count does not match profile")

    entries: list[ManifestFileEntry] = []
    scenario_ids: set[str] = set()
    variant_count = 0
    multi_turn_count = 0
    for path in files:
        envelope = _load_group(path)
        if path.stem != envelope.group_id:
            raise ValueError("group filename must match group_id")
        if len(envelope.variants) != profile.variants_per_group:
            raise ValueError("variant count per group does not match profile")
        group_multi = sum(len(item.dialogue_turns) > 1 for item in envelope.variants)
        if group_multi != profile.multi_turn_per_group:
            raise ValueError("multi-turn count per group does not match profile")
        for scenario in envelope.variants:
            if scenario.scenario_id in scenario_ids:
                raise ValueError("duplicate scenario ID across groups")
            scenario_ids.add(scenario.scenario_id)
        variant_count += len(envelope.variants)
        multi_turn_count += group_multi
        entries.append(
            ManifestFileEntry(
                relative_path=path.name,
                sha256=sha256_digest(path.read_bytes()),
            )
        )

    binding = [entry.model_dump(mode="json") for entry in entries]
    corpus_hash = sha256_digest(canonical_json(binding).encode())
    return Manifest(
        files=tuple(entries),
        group_count=len(files),
        variant_count=variant_count,
        multi_turn_count=multi_turn_count,
        corpus_hash=corpus_hash,
    )


def verify_manifest(
    manifest: Manifest,
    group_dir: Path,
    *,
    profile: CorpusProfile = PRODUCTION_PROFILE,
) -> tuple[ScenarioGroupEnvelope, ...]:
    rebuilt = build_manifest(group_dir, profile=profile)
    if rebuilt != manifest:
        raise ValueError("manifest does not exactly match corpus content")
    return tuple(_load_group(group_dir / entry.relative_path) for entry in manifest.files)


def create_seal(
    manifest: Manifest,
    group_dir: Path,
    *,
    source_commit: str,
    profile: CorpusProfile = PRODUCTION_PROFILE,
) -> PreConsumptionSeal:
    verify_manifest(manifest, group_dir, profile=profile)
    return PreConsumptionSeal(
        manifest_hash=manifest.digest(),
        corpus_hash=manifest.corpus_hash,
        source_commit=source_commit,
    )


def _result_dimensions(result: ComposedSampleResult) -> dict[str, bool]:
    return {
        "complete": result.all_passed,
        "intended_action": result.semantic_fields.intended_action.passed,
        "action_semantics": result.semantic_fields.action_semantics.passed,
        "temporal_relation": result.semantic_fields.temporal_relation.passed,
        "normalized_value_match": result.semantic_fields.normalized_values.passed,
        "entity_semantics": result.semantic_fields.entity_semantics.passed,
        "clarification": result.clarification.passed,
        "downstream_outcome": result.downstream_outcome.passed,
        "tool_sequence": result.tool_sequence.passed,
        "interpretation_tools": result.interpretation_tools.passed,
        "authority": result.authority.passed,
        "appointment_deltas": result.appointment_deltas.passed,
        "audit_deltas": result.audit_deltas.passed,
        "safety": result.safety.passed,
    }


def _observation_fingerprint(result: ComposedSampleResult) -> str:
    payload = {
        "interpretation": asdict(result.interpretation),
        "replay": asdict(result.replay),
    }
    payload["interpretation"].pop("sample_index", None)
    payload["replay"].pop("sample_index", None)
    payload["interpretation"].pop("scenario_id", None)
    payload["replay"].pop("scenario_id", None)
    return sha256_digest(canonical_json(payload).encode())


def _assert_no_forbidden_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_REPORT_KEYS:
                raise ValueError(f"forbidden aggregate key: {key}")
            _assert_no_forbidden_keys(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _assert_no_forbidden_keys(child)


def validate_aggregate_payload(
    raw: dict[str, Any],
    *,
    profile: CorpusProfile = PRODUCTION_PROFILE,
) -> AggregateReport:
    _assert_no_forbidden_keys(raw)
    report = AggregateReport.model_validate(raw)
    if report.repeat_count != profile.repeat_count:
        raise ValueError("aggregate repeat count does not match profile")
    if report.sample_count != profile.sample_count:
        raise ValueError("aggregate sample count does not match profile")
    if report.coverage.scenario_count != profile.variant_count:
        raise ValueError("aggregate scenario count does not match profile")
    unsigned = report.model_dump(mode="json", exclude={"report_hash"})
    expected = sha256_digest(canonical_json(unsigned).encode())
    if report.report_hash != expected:
        raise ValueError("aggregate report hash mismatch")
    return report


def evaluate_aggregate(
    manifest: Manifest,
    seal: PreConsumptionSeal,
    group_dir: Path,
    *,
    source_commit: str,
    profile: CorpusProfile = PRODUCTION_PROFILE,
) -> AggregateReport:
    if seal.state != "sealed":
        raise ValueError("only a sealed corpus may be evaluated")
    if source_commit != seal.source_commit:
        raise ValueError("evaluation source commit does not match seal")
    groups = verify_manifest(manifest, group_dir, profile=profile)
    if seal.manifest_hash != manifest.digest() or seal.corpus_hash != manifest.corpus_hash:
        raise ValueError("seal does not bind the supplied manifest")
    if seal.repeat_count != profile.repeat_count:
        raise ValueError("seal repeat count does not match profile")

    dimensions = {
        name: {"passed": 0, "failed": 0} for name in DIMENSION_NAMES
    }
    failure_layers = {name: 0 for name in FAILURE_LAYER_NAMES}
    slice_counts: dict[str, dict[str, dict[str, int]]] = {
        axis: {} for axis in SLICE_AXES
    }
    fingerprints: dict[str, list[str]] = {}
    coverage_cells: set[tuple[str, ...]] = set()

    for group in groups:
        for scenario in group.variants:
            coverage_cells.add(tuple(str(getattr(scenario, axis)) for axis in SLICE_AXES))
            for sample_index in range(profile.repeat_count):
                interpretation = replace(
                    deterministic_interpret(scenario),
                    sample_index=sample_index,
                )
                replay = deterministic_replay(scenario, interpretation)
                result = score_interpretation_replay_pair(
                    scenario,
                    interpretation,
                    replay,
                )
                flags = _result_dimensions(result)
                for name, passed in flags.items():
                    dimensions[name]["passed" if passed else "failed"] += 1
                for layer in result.failure_layers:
                    failure_layers[layer] += 1
                fingerprints.setdefault(scenario.scenario_id, []).append(
                    _observation_fingerprint(result)
                )
                for axis in SLICE_AXES:
                    value = str(getattr(scenario, axis))
                    bucket = slice_counts[axis].setdefault(
                        value,
                        {"total": 0, "complete_passed": 0, "safety_passed": 0},
                    )
                    bucket["total"] += 1
                    bucket["complete_passed"] += int(result.all_passed)
                    bucket["safety_passed"] += int(result.safety.passed)

    variant_ids = {
        scenario_id
        for scenario_id, values in fingerprints.items()
        if len(set(values)) > 1
    }
    variant_samples = sum(len(fingerprints[item]) for item in variant_ids)
    critical_slices = {
        axis: tuple(
            SliceAggregate(value=value, **counts)
            for value, counts in sorted(values.items())
        )
        for axis, values in slice_counts.items()
    }
    unsigned: dict[str, Any] = {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "corpus_version": CORPUS_VERSION,
        "evaluation_id": EVALUATION_ID,
        "source_commit": source_commit,
        "manifest_hash": manifest.digest(),
        "corpus_hash": manifest.corpus_hash,
        "evaluator_version": EVALUATOR_VERSION,
        "repeat_count": profile.repeat_count,
        "sample_count": profile.sample_count,
        "dimensions": dimensions,
        "failure_layers": failure_layers,
        "variance": {
            "variant_scenario_count": len(variant_ids),
            "variant_sample_count": variant_samples,
            "total_samples": profile.sample_count,
        },
        "critical_slices": {
            axis: [item.model_dump(mode="json") for item in values]
            for axis, values in critical_slices.items()
        },
        "coverage": {
            "distinct_cells": len(coverage_cells),
            "scenario_count": profile.variant_count,
        },
    }
    _assert_no_forbidden_keys(unsigned)
    raw = dict(unsigned)
    raw["report_hash"] = sha256_digest(canonical_json(unsigned).encode())
    return validate_aggregate_payload(raw, profile=profile)


def consume_report(
    seal: PreConsumptionSeal,
    report: AggregateReport,
    *,
    consumed_at: str | None = None,
    profile: CorpusProfile = PRODUCTION_PROFILE,
) -> ConsumedSeal:
    validate_aggregate_payload(report.model_dump(mode="json"), profile=profile)
    bindings = (
        report.source_commit == seal.source_commit
        and report.manifest_hash == seal.manifest_hash
        and report.corpus_hash == seal.corpus_hash
        and report.repeat_count == seal.repeat_count
        and report.evaluator_version == seal.evaluator_version
    )
    if not bindings:
        raise ValueError("aggregate report does not match pre-consumption seal")
    timestamp = consumed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return ConsumedSeal(
        manifest_hash=seal.manifest_hash,
        corpus_hash=seal.corpus_hash,
        source_commit=seal.source_commit,
        report_hash=report.report_hash,
        consumed_at=timestamp,
    )


__all__ = [
    "AGGREGATE_SCHEMA_VERSION",
    "CORPUS_VERSION",
    "DIMENSION_NAMES",
    "EVALUATION_ID",
    "FAILURE_LAYER_NAMES",
    "FORBIDDEN_REPORT_KEYS",
    "GROUP_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "PRODUCTION_PROFILE",
    "SEAL_SCHEMA_VERSION",
    "SLICE_AXES",
    "AggregateDimension",
    "AggregateReport",
    "ConsumedSeal",
    "CorpusProfile",
    "CoverageSummary",
    "Manifest",
    "ManifestFileEntry",
    "PreConsumptionSeal",
    "ScenarioGroupEnvelope",
    "SliceAggregate",
    "VarianceSummary",
    "build_manifest",
    "canonical_json",
    "consume_report",
    "create_seal",
    "evaluate_aggregate",
    "sha256_digest",
    "validate_aggregate_payload",
    "verify_manifest",
]
