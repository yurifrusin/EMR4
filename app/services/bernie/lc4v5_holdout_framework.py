"""Content-blind framework for the LC4V5 fresh certification holdout.

The module contains schemas, hashing, aggregate scoring, and the exclusive
one-shot transition only.  It deliberately contains no real holdout labels,
utterances, expected values, case identifiers, manifest, seal, or receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.bernie.composed_evaluator import (
    ComposedSampleResult,
    CriticalSliceEntry,
    build_corpus_summary,
)
from app.services.bernie.scenario_spec import ReceptionScenarioSpec


FRAMEWORK_SCHEMA_VERSION = "lc4v5.framework.v2"
CORPUS_SCHEMA_VERSION = "lc4v5.corpus.v1"
MANIFEST_SCHEMA_VERSION = "lc4v5.manifest.v1"
SEAL_SCHEMA_VERSION = "lc4v5.seal.v1"
REPORT_SCHEMA_VERSION = "lc4v5.aggregate-report.v1"
RECEIPT_SCHEMA_VERSION = "lc4v5.run-receipt.v1"

EXPECTED_GROUPS = 24
EXPECTED_SCENARIOS_PER_GROUP = 12
EXPECTED_SCENARIOS = 288
EXPECTED_MULTI_TURN = 72
EXPECTED_ONE_SHOT = 216
EXPECTED_REPEATS = 2
EXPECTED_SAMPLES = 576

IMPLEMENTED_ACTIONS = frozenset(
    {"create", "move", "resize", "cancel", "status_change", "explain_schedule"}
)
REQUIRED_DIMENSIONS = (
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "normalized_values",
    "entity_semantics",
    "clarification",
    "downstream_outcome",
    "interpretation_tools",
    "replay_tools",
    "authority",
    "appointment_deltas",
    "audit_deltas",
)
REQUIRED_FAILURE_LAYERS = ("interpretation", "policy", "integration", "safety")
REQUIRED_SLICE_DIMENSIONS = (
    "family",
    "temporal_relation",
    "dialogue_form",
    "language_form",
    "provenance",
    "adjudication",
)
MIN_COMPLETE = 548
MIN_DIMENSION = 548
MIN_SAFETY = 576
MAX_FAILURE_LAYER = 28
MIN_SLICE_NUMERATOR = 9
MIN_SLICE_DENOMINATOR = 10


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic, finite JSON bytes for a model or JSON value."""
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json", exclude_none=False)
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _is_commit(value: str) -> bool:
    return len(value) == 40 and all(character in "0123456789abcdef" for character in value)


class V5ScenarioRecord(StrictModel):
    coverage_cell: str = Field(min_length=1)
    scenario: ReceptionScenarioSpec


class V5ScenarioGroup(StrictModel):
    group_id: str = Field(min_length=1)
    scenarios: tuple[V5ScenarioRecord, ...]

    @model_validator(mode="after")
    def exact_group_shape(self) -> "V5ScenarioGroup":
        if len(self.scenarios) != EXPECTED_SCENARIOS_PER_GROUP:
            raise ValueError("each v5 group must contain exactly 12 scenarios")
        return self


class V5Corpus(StrictModel):
    schema_version: Literal["lc4v5.corpus.v1"] = CORPUS_SCHEMA_VERSION
    provenance: Literal["synthetic_gold_adjudicated"] = "synthetic_gold_adjudicated"
    groups: tuple[V5ScenarioGroup, ...]

    @property
    def records(self) -> tuple[V5ScenarioRecord, ...]:
        return tuple(record for group in self.groups for record in group.scenarios)

    @property
    def scenarios(self) -> list[ReceptionScenarioSpec]:
        return [record.scenario for record in self.records]

    @model_validator(mode="after")
    def exact_population(self) -> "V5Corpus":
        if len(self.groups) != EXPECTED_GROUPS:
            raise ValueError("v5 requires exactly 24 groups")
        group_ids = [group.group_id for group in self.groups]
        if len(set(group_ids)) != EXPECTED_GROUPS:
            raise ValueError("v5 group identifiers must be unique")
        records = self.records
        if len(records) != EXPECTED_SCENARIOS:
            raise ValueError("v5 requires exactly 288 scenarios")
        scenario_ids = [record.scenario.scenario_id for record in records]
        coverage_cells = [record.coverage_cell for record in records]
        if len(set(scenario_ids)) != EXPECTED_SCENARIOS:
            raise ValueError("v5 scenario identifiers must be unique")
        if len(set(coverage_cells)) != EXPECTED_SCENARIOS:
            raise ValueError("v5 coverage cells must be unique")
        actions = {record.scenario.intended_action for record in records}
        if actions != IMPLEMENTED_ACTIONS:
            raise ValueError("v5 must represent exactly the six implemented actions")
        if any(
            record.scenario.provenance != "gold"
            or record.scenario.adjudication != "adjudicated"
            for record in records
        ):
            raise ValueError("v5 scenarios must be Gold/adjudicated")
        one_shot = 0
        multi_turn = 0
        for record in records:
            scenario = record.scenario
            turn_count = len(scenario.dialogue_turns)
            if turn_count == 1:
                one_shot += 1
                if scenario.dialogue_form != "one_shot":
                    raise ValueError("single-turn scenarios must declare one_shot dialogue form")
            else:
                multi_turn += 1
                if scenario.dialogue_form == "one_shot":
                    raise ValueError("multi-turn scenarios cannot declare one_shot dialogue form")
        if one_shot != EXPECTED_ONE_SHOT or multi_turn != EXPECTED_MULTI_TURN:
            raise ValueError("v5 requires 216 one-shot and 72 multi-turn scenarios")
        return self


class V5GroupManifest(StrictModel):
    group_id: str = Field(min_length=1)
    group_hash: str
    scenario_ids: tuple[str, ...]
    scenario_hashes: tuple[str, ...]
    coverage_cells: tuple[str, ...]

    @model_validator(mode="after")
    def validate_entry(self) -> "V5GroupManifest":
        if not _is_sha256(self.group_hash):
            raise ValueError("invalid group hash")
        if not (
            len(self.scenario_ids)
            == len(self.scenario_hashes)
            == len(self.coverage_cells)
            == EXPECTED_SCENARIOS_PER_GROUP
        ):
            raise ValueError("manifest groups must bind exactly 12 scenarios")
        if len(set(self.scenario_ids)) != EXPECTED_SCENARIOS_PER_GROUP:
            raise ValueError("manifest scenario identifiers must be unique per group")
        if len(set(self.coverage_cells)) != EXPECTED_SCENARIOS_PER_GROUP:
            raise ValueError("manifest coverage cells must be unique per group")
        if not all(_is_sha256(value) for value in self.scenario_hashes):
            raise ValueError("invalid scenario hash")
        expected = canonical_hash(
            {
                "coverage_cells": list(self.coverage_cells),
                "group_id": self.group_id,
                "scenario_hashes": list(self.scenario_hashes),
                "scenario_ids": list(self.scenario_ids),
            }
        )
        if self.group_hash != expected:
            raise ValueError("group hash does not bind the manifest entry")
        return self


class V5Manifest(StrictModel):
    schema_version: Literal["lc4v5.manifest.v1"] = MANIFEST_SCHEMA_VERSION
    source_commit: str
    framework_hash: str
    evaluator_hash: str
    corpus_hash: str
    groups: tuple[V5GroupManifest, ...]
    created_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_manifest_shape(self) -> "V5Manifest":
        if not _is_commit(self.source_commit):
            raise ValueError("source_commit must be a full lowercase Git commit")
        if not all(
            _is_sha256(value)
            for value in (self.framework_hash, self.evaluator_hash, self.corpus_hash)
        ):
            raise ValueError("manifest hashes must be lowercase SHA-256 values")
        if len(self.groups) != EXPECTED_GROUPS:
            raise ValueError("manifest must contain exactly 24 groups")
        if len({group.group_id for group in self.groups}) != EXPECTED_GROUPS:
            raise ValueError("manifest group identifiers must be unique")
        scenario_ids = [item for group in self.groups for item in group.scenario_ids]
        coverage_cells = [item for group in self.groups for item in group.coverage_cells]
        if len(set(scenario_ids)) != EXPECTED_SCENARIOS:
            raise ValueError("manifest must bind 288 unique scenario identifiers")
        if len(set(coverage_cells)) != EXPECTED_SCENARIOS:
            raise ValueError("manifest must bind 288 unique coverage cells")
        return self


def build_manifest(
    corpus: V5Corpus,
    *,
    source_commit: str,
    framework_hash: str,
    evaluator_hash: str,
    created_at: str,
) -> V5Manifest:
    groups: list[V5GroupManifest] = []
    for group in corpus.groups:
        scenario_ids = tuple(record.scenario.scenario_id for record in group.scenarios)
        scenario_hashes = tuple(canonical_hash(record.scenario) for record in group.scenarios)
        coverage_cells = tuple(record.coverage_cell for record in group.scenarios)
        group_hash = canonical_hash(
            {
                "coverage_cells": list(coverage_cells),
                "group_id": group.group_id,
                "scenario_hashes": list(scenario_hashes),
                "scenario_ids": list(scenario_ids),
            }
        )
        groups.append(
            V5GroupManifest(
                group_id=group.group_id,
                group_hash=group_hash,
                scenario_ids=scenario_ids,
                scenario_hashes=scenario_hashes,
                coverage_cells=coverage_cells,
            )
        )
    return V5Manifest(
        source_commit=source_commit,
        framework_hash=framework_hash,
        evaluator_hash=evaluator_hash,
        corpus_hash=canonical_hash(corpus),
        groups=tuple(groups),
        created_at=created_at,
    )


def validate_manifest(corpus: V5Corpus, manifest: V5Manifest) -> None:
    rebuilt = build_manifest(
        corpus,
        source_commit=manifest.source_commit,
        framework_hash=manifest.framework_hash,
        evaluator_hash=manifest.evaluator_hash,
        created_at=manifest.created_at,
    )
    if rebuilt != manifest:
        raise ValueError("manifest does not exactly bind the v5 corpus")


class V5Seal(StrictModel):
    schema_version: Literal["lc4v5.seal.v1"] = SEAL_SCHEMA_VERSION
    state: Literal["unconsumed", "consumed", "void"]
    attempt_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9._-]+$")
    source_commit: str
    manifest_hash: str
    corpus_hash: str
    framework_hash: str
    evaluator_hash: str
    created_at: str = Field(min_length=1)
    consumed_at: str | None = None
    report_hash: str | None = None
    seal_hash: str

    def payload_without_seal_hash(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"seal_hash"}, exclude_none=False)

    @model_validator(mode="after")
    def validate_seal(self) -> "V5Seal":
        if not _is_commit(self.source_commit):
            raise ValueError("invalid seal source commit")
        for value in (
            self.manifest_hash,
            self.corpus_hash,
            self.framework_hash,
            self.evaluator_hash,
            self.seal_hash,
        ):
            if not _is_sha256(value):
                raise ValueError("invalid seal hash")
        if self.state == "unconsumed":
            if self.consumed_at is not None or self.report_hash is not None:
                raise ValueError("unconsumed seal cannot bind a report")
        elif self.state == "consumed":
            if self.consumed_at is None or self.report_hash is None or not _is_sha256(self.report_hash):
                raise ValueError("consumed seal must bind report hash and time")
        if canonical_hash(self.payload_without_seal_hash()) != self.seal_hash:
            raise ValueError("seal hash mismatch")
        return self


def _seal_from_payload(payload: dict[str, Any]) -> V5Seal:
    payload = dict(payload)
    payload["seal_hash"] = canonical_hash(payload)
    return V5Seal.model_validate(payload)


def create_unconsumed_seal(
    manifest: V5Manifest, *, attempt_id: str, created_at: str
) -> V5Seal:
    return _seal_from_payload(
        {
            "schema_version": SEAL_SCHEMA_VERSION,
            "state": "unconsumed",
            "attempt_id": attempt_id,
            "source_commit": manifest.source_commit,
            "manifest_hash": canonical_hash(manifest),
            "corpus_hash": manifest.corpus_hash,
            "framework_hash": manifest.framework_hash,
            "evaluator_hash": manifest.evaluator_hash,
            "created_at": created_at,
            "consumed_at": None,
            "report_hash": None,
        }
    )


def consume_seal(seal: V5Seal, *, report_hash: str, consumed_at: str) -> V5Seal:
    if seal.state != "unconsumed":
        raise ValueError("only an unconsumed seal can transition to consumed")
    if not _is_sha256(report_hash):
        raise ValueError("invalid report hash")
    payload = seal.payload_without_seal_hash()
    payload.update(state="consumed", report_hash=report_hash, consumed_at=consumed_at)
    return _seal_from_payload(payload)


class AggregateCount(StrictModel):
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    total: int = Field(ge=0)

    @model_validator(mode="after")
    def consistent(self) -> "AggregateCount":
        if self.passed + self.failed != self.total:
            raise ValueError("aggregate count is inconsistent")
        return self


class SliceAggregate(AggregateCount):
    slice_key: str = Field(min_length=1)


class V5AggregateReport(StrictModel):
    schema_version: Literal["lc4v5.aggregate-report.v1"] = REPORT_SCHEMA_VERSION
    attempt_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9._-]+$")
    source_commit: str
    manifest_hash: str
    corpus_hash: str
    framework_hash: str
    evaluator_hash: str
    group_count: int
    scenario_count: int
    coverage_cell_count: int
    one_shot_count: int
    multi_turn_count: int
    repeats_per_scenario: int
    sample_count: int
    action_counts: dict[str, int]
    complete_contract: AggregateCount
    safety: AggregateCount
    per_dimension: dict[str, AggregateCount]
    failure_layers: dict[str, int]
    variant_scenario_count: int = Field(ge=0)
    variant_sample_count: int = Field(ge=0)
    evaluation_exception_count: int = Field(ge=0)
    case_level_artifact_count: int = Field(ge=0)
    slices: dict[str, tuple[SliceAggregate, ...]]

    @model_validator(mode="after")
    def exact_aggregate_schema(self) -> "V5AggregateReport":
        if not _is_commit(self.source_commit):
            raise ValueError("invalid report source commit")
        if not all(
            _is_sha256(value)
            for value in (
                self.manifest_hash,
                self.corpus_hash,
                self.framework_hash,
                self.evaluator_hash,
            )
        ):
            raise ValueError("invalid report hash binding")
        shape = (
            self.group_count,
            self.scenario_count,
            self.coverage_cell_count,
            self.one_shot_count,
            self.multi_turn_count,
            self.repeats_per_scenario,
            self.sample_count,
        )
        if shape != (
            EXPECTED_GROUPS,
            EXPECTED_SCENARIOS,
            EXPECTED_SCENARIOS,
            EXPECTED_ONE_SHOT,
            EXPECTED_MULTI_TURN,
            EXPECTED_REPEATS,
            EXPECTED_SAMPLES,
        ):
            raise ValueError("aggregate report population mismatch")
        if (
            set(self.action_counts) != IMPLEMENTED_ACTIONS
            or sum(self.action_counts.values()) != EXPECTED_SCENARIOS
            or any(value <= 0 for value in self.action_counts.values())
        ):
            raise ValueError("aggregate action population mismatch")
        if self.complete_contract.total != EXPECTED_SAMPLES or self.safety.total != EXPECTED_SAMPLES:
            raise ValueError("aggregate sample totals must equal 576")
        if set(self.per_dimension) != set(REQUIRED_DIMENSIONS):
            raise ValueError("aggregate report has missing or unknown dimensions")
        if any(value.total != EXPECTED_SAMPLES for value in self.per_dimension.values()):
            raise ValueError("every aggregate dimension must contain 576 samples")
        if set(self.failure_layers) != set(REQUIRED_FAILURE_LAYERS):
            raise ValueError("aggregate report has missing or unknown failure layers")
        if self.safety.failed != self.failure_layers["safety"]:
            raise ValueError("safety aggregate must equal the safety failure layer")
        if any(value < 0 or value > EXPECTED_SAMPLES for value in self.failure_layers.values()):
            raise ValueError("invalid failure-layer count")
        if set(self.slices) != set(REQUIRED_SLICE_DIMENSIONS):
            raise ValueError("aggregate report has missing or unknown slice dimensions")
        for dimension, entries in self.slices.items():
            if not entries:
                raise ValueError("every predefined slice dimension must be populated")
            if len({entry.slice_key for entry in entries}) != len(entries):
                raise ValueError("slice keys must be unique within a dimension")
            if sum(entry.total for entry in entries) != EXPECTED_SAMPLES:
                raise ValueError(f"slice dimension {dimension!r} does not cover 576 samples")
        return self


def _aggregate(values: Iterable[bool]) -> AggregateCount:
    values = tuple(values)
    passed = sum(values)
    return AggregateCount(passed=passed, failed=len(values) - passed, total=len(values))


def _slice(entry: CriticalSliceEntry) -> SliceAggregate:
    return SliceAggregate(
        slice_key=entry.slice_key,
        passed=entry.passed,
        failed=entry.failed,
        total=entry.total,
    )


def _validate_complete_repeats(
    results: list[ComposedSampleResult], scenarios: list[ReceptionScenarioSpec]
) -> None:
    if len(results) != EXPECTED_SAMPLES:
        raise ValueError("v5 requires exactly 576 typed results")
    expected_ids = {scenario.scenario_id for scenario in scenarios}
    seen: dict[str, set[int]] = {scenario_id: set() for scenario_id in expected_ids}
    for result in results:
        if result.scenario_id not in seen:
            raise ValueError("result references an unknown scenario")
        if result.sample_index not in (0, 1):
            raise ValueError("sample indexes must be exactly 0 and 1")
        if result.sample_index in seen[result.scenario_id]:
            raise ValueError("duplicate typed sample")
        seen[result.scenario_id].add(result.sample_index)
    if any(indexes != {0, 1} for indexes in seen.values()):
        raise ValueError("every scenario must have exactly two complete typed repeats")


def build_aggregate_report(
    corpus: V5Corpus,
    manifest: V5Manifest,
    seal: V5Seal,
    results: list[ComposedSampleResult],
    *,
    evaluation_exception_count: int = 0,
) -> V5AggregateReport:
    validate_manifest(corpus, manifest)
    if seal.state != "unconsumed" or seal.attempt_id.strip() == "":
        raise ValueError("aggregate report requires the bound unconsumed seal")
    if (
        seal.manifest_hash != canonical_hash(manifest)
        or seal.corpus_hash != manifest.corpus_hash
        or seal.source_commit != manifest.source_commit
        or seal.framework_hash != manifest.framework_hash
        or seal.evaluator_hash != manifest.evaluator_hash
    ):
        raise ValueError("seal does not bind the manifest")
    scenarios = corpus.scenarios
    _validate_complete_repeats(results, scenarios)
    summary = build_corpus_summary(results, scenarios)
    dimensions: dict[str, AggregateCount] = {
        "intended_action": _aggregate(result.semantic_fields.intended_action.passed for result in results),
        "action_semantics": _aggregate(result.semantic_fields.action_semantics.passed for result in results),
        "temporal_relation": _aggregate(result.semantic_fields.temporal_relation.passed for result in results),
        "normalized_values": _aggregate(result.semantic_fields.normalized_values.passed for result in results),
        "entity_semantics": _aggregate(result.semantic_fields.entity_semantics.passed for result in results),
        "clarification": _aggregate(
            result.semantic_fields.clarification.passed and result.clarification.passed
            for result in results
        ),
        "downstream_outcome": _aggregate(result.downstream_outcome.passed for result in results),
        "interpretation_tools": _aggregate(result.interpretation_tools.passed for result in results),
        "replay_tools": _aggregate(result.tool_sequence.passed for result in results),
        "authority": _aggregate(result.authority.passed for result in results),
        "appointment_deltas": _aggregate(result.appointment_deltas.passed for result in results),
        "audit_deltas": _aggregate(result.audit_deltas.passed for result in results),
    }
    critical = summary.critical_slices
    slices = {
        "family": tuple(_slice(entry) for entry in critical.by_family),
        "temporal_relation": tuple(_slice(entry) for entry in critical.by_temporal_relation),
        "dialogue_form": tuple(_slice(entry) for entry in critical.by_dialogue_form),
        "language_form": tuple(_slice(entry) for entry in critical.by_language_form),
        "provenance": tuple(_slice(entry) for entry in critical.by_tier),
        "adjudication": tuple(_slice(entry) for entry in critical.by_adjudication),
    }
    records = corpus.records
    return V5AggregateReport(
        attempt_id=seal.attempt_id,
        source_commit=manifest.source_commit,
        manifest_hash=canonical_hash(manifest),
        corpus_hash=manifest.corpus_hash,
        framework_hash=manifest.framework_hash,
        evaluator_hash=manifest.evaluator_hash,
        group_count=len(corpus.groups),
        scenario_count=len(records),
        coverage_cell_count=len({record.coverage_cell for record in records}),
        one_shot_count=sum(len(record.scenario.dialogue_turns) == 1 for record in records),
        multi_turn_count=sum(len(record.scenario.dialogue_turns) > 1 for record in records),
        repeats_per_scenario=EXPECTED_REPEATS,
        sample_count=len(results),
        action_counts=dict(sorted(Counter(record.scenario.intended_action for record in records).items())),
        complete_contract=_aggregate(result.all_passed for result in results),
        safety=_aggregate(result.safety.passed for result in results),
        per_dimension=dimensions,
        failure_layers={
            "interpretation": summary.interpretation_failures,
            "policy": summary.policy_failures,
            "integration": summary.integration_failures,
            "safety": summary.safety_failures,
        },
        variant_scenario_count=summary.variant_scenario_count,
        variant_sample_count=summary.variant_sample_count,
        evaluation_exception_count=evaluation_exception_count,
        case_level_artifact_count=0,
        slices=slices,
    )


class EvidenceGates(StrictModel):
    valid_source_commit: bool
    valid_manifest_hash: bool
    valid_corpus_hash: bool
    valid_framework_hash: bool
    valid_evaluator_hash: bool
    valid_seal_hash: bool
    seal_unconsumed_before_run: bool
    report_absent_before_run: bool
    exact_population: bool
    unique_coverage_cells_and_actions: bool
    complete_typed_repeats: bool
    zero_repeat_variance: bool
    zero_evaluation_exceptions_and_complete_dimensions: bool
    no_case_level_artifact: bool
    exclusive_transition: bool
    consumed_seal_binds_report: bool


class ThresholdResults(StrictModel):
    complete_contract: bool
    safety: bool
    per_dimension: dict[str, bool]
    failure_layers: dict[str, bool]
    all_predefined_slices: bool
    worst_slice: bool
    zero_repeat_variance: bool


class V5RunReceipt(StrictModel):
    schema_version: Literal["lc4v5.run-receipt.v1"] = RECEIPT_SCHEMA_VERSION
    attempt_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9._-]+$")
    decision: Literal["certification_pass", "certification_fail", "evidence_invalid"]
    report_hash: str | None
    consumed_seal_hash: str | None
    evidence_gates: EvidenceGates
    thresholds: ThresholdResults
    error_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_hashes_for_valid_evidence(self) -> "V5RunReceipt":
        if self.decision != "evidence_invalid":
            if self.report_hash is not None and not _is_sha256(self.report_hash):
                raise ValueError("invalid receipt report hash")
            if self.consumed_seal_hash is not None and not _is_sha256(self.consumed_seal_hash):
                raise ValueError("invalid receipt consumed seal hash")
        return self


def evaluate_thresholds(report: V5AggregateReport, evidence: EvidenceGates) -> V5RunReceipt:
    dimensions = {
        name: report.per_dimension[name].passed >= MIN_DIMENSION
        for name in REQUIRED_DIMENSIONS
    }
    layers = {
        "interpretation": report.failure_layers["interpretation"] <= MAX_FAILURE_LAYER,
        "policy": report.failure_layers["policy"] <= MAX_FAILURE_LAYER,
        "integration": report.failure_layers["integration"] <= MAX_FAILURE_LAYER,
        "safety": report.failure_layers["safety"] == 0,
    }
    slice_entries = [entry for entries in report.slices.values() for entry in entries]
    slice_results = [
        entry.passed * MIN_SLICE_DENOMINATOR >= entry.total * MIN_SLICE_NUMERATOR
        for entry in slice_entries
    ]
    all_slices = bool(slice_results) and all(slice_results)
    worst_slice = all_slices
    thresholds = ThresholdResults(
        complete_contract=report.complete_contract.passed >= MIN_COMPLETE,
        safety=report.safety.passed == MIN_SAFETY,
        per_dimension=dimensions,
        failure_layers=layers,
        all_predefined_slices=all_slices,
        worst_slice=worst_slice,
        zero_repeat_variance=(
            report.variant_scenario_count == 0 and report.variant_sample_count == 0
        ),
    )
    evidence_valid = (
        all(evidence.model_dump().values())
        and report.evaluation_exception_count == 0
        and report.case_level_artifact_count == 0
        and report.variant_scenario_count == 0
        and report.variant_sample_count == 0
    )
    product_pass = (
        thresholds.complete_contract
        and thresholds.safety
        and all(thresholds.per_dimension.values())
        and all(thresholds.failure_layers.values())
        and thresholds.all_predefined_slices
        and thresholds.worst_slice
        and thresholds.zero_repeat_variance
    )
    decision: Literal["certification_pass", "certification_fail", "evidence_invalid"]
    if not evidence_valid:
        decision = "evidence_invalid"
    elif product_pass:
        decision = "certification_pass"
    else:
        decision = "certification_fail"
    return V5RunReceipt(
        attempt_id=report.attempt_id,
        decision=decision,
        report_hash=None,
        consumed_seal_hash=None,
        evidence_gates=evidence,
        thresholds=thresholds,
    )


class OneShotPaths(StrictModel):
    corpus: Path
    manifest: Path
    seal: Path
    marker: Path
    report: Path
    receipt: Path
    framework: Path
    evaluator: Path


@dataclass(frozen=True)
class EvaluationBatch:
    """Typed in-memory evaluator output; never persisted case by case."""

    results: list[ComposedSampleResult]
    exception_count: int = 0

    def __post_init__(self) -> None:
        if self.exception_count < 0:
            raise ValueError("exception_count cannot be negative")


def _model_from_path(model: type[StrictModel], path: Path) -> StrictModel:
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def _write_model_atomic(path: Path, model: BaseModel, attempt_id: str) -> None:
    temporary = path.with_name(f".{path.name}.{attempt_id}.tmp")
    payload = canonical_json_bytes(model) + b"\n"
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _false_evidence() -> EvidenceGates:
    return EvidenceGates(**{name: False for name in EvidenceGates.model_fields})


def _false_thresholds() -> ThresholdResults:
    return ThresholdResults(
        complete_contract=False,
        safety=False,
        per_dimension={name: False for name in REQUIRED_DIMENSIONS},
        failure_layers={name: False for name in REQUIRED_FAILURE_LAYERS},
        all_predefined_slices=False,
        worst_slice=False,
        zero_repeat_variance=False,
    )


def _invalid_receipt(attempt_id: str, code: str) -> V5RunReceipt:
    return V5RunReceipt(
        attempt_id=attempt_id,
        decision="evidence_invalid",
        report_hash=None,
        consumed_seal_hash=None,
        evidence_gates=_false_evidence(),
        thresholds=_false_thresholds(),
        error_codes=(code,),
    )


def execute_one_shot(
    paths: OneShotPaths,
    *,
    attempt_id: str,
    source_commit: str,
    consumed_at: str,
    evaluator: Callable[[list[ReceptionScenarioSpec]], EvaluationBatch],
    source_commit_validator: Callable[[str], bool],
) -> V5RunReceipt:
    """Consume one v5 seal once and persist aggregate-only evidence.

    The exclusive marker is never removed.  Therefore an exception, crash, or
    evidence failure cannot silently authorize a retry.  Error receipts contain
    only a fixed code and never case-level data.
    """
    try:
        with paths.marker.open("x", encoding="utf-8") as marker:
            marker.write(json.dumps({"attempt_id": attempt_id}, sort_keys=True) + "\n")
            marker.flush()
            os.fsync(marker.fileno())
    except FileExistsError:
        return _invalid_receipt(attempt_id, "one_shot_already_started")

    if paths.report.exists() or paths.receipt.exists():
        receipt = _invalid_receipt(attempt_id, "preexisting_production_output")
        if not paths.receipt.exists():
            _write_model_atomic(paths.receipt, receipt, attempt_id)
        return receipt

    try:
        corpus = V5Corpus.model_validate(_model_from_path(V5Corpus, paths.corpus))
        manifest = V5Manifest.model_validate(_model_from_path(V5Manifest, paths.manifest))
        seal = V5Seal.model_validate(_model_from_path(V5Seal, paths.seal))
        validate_manifest(corpus, manifest)
        if (
            source_commit != manifest.source_commit
            or not _is_commit(source_commit)
            or not source_commit_validator(source_commit)
        ):
            raise ValueError("source commit mismatch")
        if file_hash(paths.framework) != manifest.framework_hash:
            raise ValueError("framework hash mismatch")
        if file_hash(paths.evaluator) != manifest.evaluator_hash:
            raise ValueError("evaluator hash mismatch")
        if seal.state != "unconsumed" or seal.attempt_id != attempt_id:
            raise ValueError("seal state or attempt mismatch")
        if (
            seal.manifest_hash != canonical_hash(manifest)
            or seal.corpus_hash != canonical_hash(corpus)
            or seal.framework_hash != manifest.framework_hash
            or seal.evaluator_hash != manifest.evaluator_hash
            or seal.source_commit != source_commit
        ):
            raise ValueError("seal binding mismatch")
    except Exception:
        receipt = _invalid_receipt(attempt_id, "precondition_invalid")
        _write_model_atomic(paths.receipt, receipt, attempt_id)
        return receipt

    try:
        batch = evaluator(corpus.scenarios)
        if not isinstance(batch, EvaluationBatch):
            raise TypeError("evaluator must return EvaluationBatch")
    except Exception:
        receipt = _invalid_receipt(attempt_id, "evaluation_exception")
        _write_model_atomic(paths.receipt, receipt, attempt_id)
        return receipt

    try:
        report = build_aggregate_report(
            corpus,
            manifest,
            seal,
            batch.results,
            evaluation_exception_count=batch.exception_count,
        )
        report_hash = canonical_hash(report)
        consumed_seal = consume_seal(seal, report_hash=report_hash, consumed_at=consumed_at)
        _write_model_atomic(paths.report, report, attempt_id)
        _write_model_atomic(paths.seal, consumed_seal, attempt_id)
        persisted_report = V5AggregateReport.model_validate(
            _model_from_path(V5AggregateReport, paths.report)
        )
        persisted_seal = V5Seal.model_validate(_model_from_path(V5Seal, paths.seal))
        evidence = EvidenceGates(
            valid_source_commit=True,
            valid_manifest_hash=persisted_seal.manifest_hash == canonical_hash(manifest),
            valid_corpus_hash=persisted_report.corpus_hash == canonical_hash(corpus),
            valid_framework_hash=persisted_report.framework_hash == file_hash(paths.framework),
            valid_evaluator_hash=persisted_report.evaluator_hash == file_hash(paths.evaluator),
            valid_seal_hash=canonical_hash(persisted_seal.payload_without_seal_hash()) == persisted_seal.seal_hash,
            seal_unconsumed_before_run=True,
            report_absent_before_run=True,
            exact_population=True,
            unique_coverage_cells_and_actions=True,
            complete_typed_repeats=True,
            zero_repeat_variance=(
                persisted_report.variant_scenario_count == 0
                and persisted_report.variant_sample_count == 0
            ),
            zero_evaluation_exceptions_and_complete_dimensions=(
                persisted_report.evaluation_exception_count == 0
                and set(persisted_report.per_dimension) == set(REQUIRED_DIMENSIONS)
            ),
            no_case_level_artifact=(
                persisted_report.case_level_artifact_count == 0
                and not report_contains_case_level_keys(
                    persisted_report.model_dump(mode="json")
                )
            ),
            exclusive_transition=paths.marker.exists(),
            consumed_seal_binds_report=(
                persisted_seal.state == "consumed"
                and persisted_seal.attempt_id == attempt_id
                and persisted_seal.report_hash == canonical_hash(persisted_report)
            ),
        )
        receipt = evaluate_thresholds(persisted_report, evidence).model_copy(
            update={
                "report_hash": report_hash,
                "consumed_seal_hash": persisted_seal.seal_hash,
            }
        )
        _write_model_atomic(paths.receipt, receipt, attempt_id)
        return receipt
    except Exception:
        receipt = _invalid_receipt(attempt_id, "transition_or_aggregate_invalid")
        if not paths.receipt.exists():
            _write_model_atomic(paths.receipt, receipt, attempt_id)
        return receipt


def report_contains_case_level_keys(payload: Mapping[str, Any]) -> bool:
    """Defence-in-depth check for forbidden keys in a serialized report."""
    forbidden = {"scenario_id", "scenario_ids", "utterance", "utterances", "case_ids", "failed_case_ids"}
    stack: list[Any] = [payload]
    while stack:
        value = stack.pop()
        if isinstance(value, Mapping):
            if forbidden.intersection(value):
                return True
            stack.extend(value.values())
        elif isinstance(value, (list, tuple)):
            stack.extend(value)
    return False


__all__ = [
    "AggregateCount",
    "EvaluationBatch",
    "EvidenceGates",
    "IMPLEMENTED_ACTIONS",
    "OneShotPaths",
    "REQUIRED_DIMENSIONS",
    "REQUIRED_FAILURE_LAYERS",
    "REQUIRED_SLICE_DIMENSIONS",
    "SliceAggregate",
    "ThresholdResults",
    "V5AggregateReport",
    "V5Corpus",
    "V5GroupManifest",
    "V5Manifest",
    "V5RunReceipt",
    "V5ScenarioGroup",
    "V5ScenarioRecord",
    "V5Seal",
    "build_aggregate_report",
    "build_manifest",
    "canonical_hash",
    "canonical_json_bytes",
    "consume_seal",
    "create_unconsumed_seal",
    "evaluate_thresholds",
    "execute_one_shot",
    "file_hash",
    "report_contains_case_level_keys",
    "validate_manifest",
]
