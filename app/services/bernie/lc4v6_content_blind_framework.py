"""Content-blind framework for the fresh LC4V6 one-shot certification.

The module contains schema, aggregation, validation, and fail-closed state
machinery only. It contains no V6 utterance, expected semantic value, corpus,
manifest instance, seal, or acceptance threshold.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence


SCHEMA_VERSION = "lc4v6.content_blind_framework.v1"
MANIFEST_SCHEMA_VERSION = "lc4v6.manifest.v1"
AGGREGATE_SCHEMA_VERSION = "lc4v6.aggregate_report.v1"
SEAL_SCHEMA_VERSION = "lc4v6.source_seal.v1"
ATTEMPT_ID = "lc4v6-fresh-attempt-001"

GROUP_COUNT = 24
SCENARIO_COUNT = 288
MULTI_TURN_COUNT = 72
ONE_SHOT_COUNT = 216
REPEATS = 2
SAMPLE_COUNT = SCENARIO_COUNT * REPEATS

ACTIONS = frozenset(
    {"create", "move", "resize", "cancel", "status_change", "explain_schedule"}
)
DIMENSIONS = (
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
FAILURE_LAYERS = ("interpretation", "policy", "integration", "safety")
REQUIRED_SLICE_CATEGORIES = frozenset(
    {"family", "language_form", "dialogue_form", "temporal_relation", "provenance", "adjudication"}
)
FORBIDDEN_AGGREGATE_KEYS = frozenset(
    {
        "scenario_id",
        "scenario_ids",
        "utterance",
        "utterances",
        "expected",
        "expected_values",
        "source_span",
        "source_spans",
        "normalized_turn",
        "normalized_turns",
        "label",
        "labels",
        "failure_id",
        "failure_ids",
        "failure_selection",
        "case",
        "cases",
    }
)


def canonical_json(payload: Any) -> str:
    """Return deterministic UTF-8 JSON without incidental whitespace."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def sha256_payload(payload: Any) -> str:
    return sha256_text(canonical_json(payload))


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    digest = value.removeprefix("sha256:")
    return len(digest) == 64 and all(char in "0123456789abcdef" for char in digest)


@dataclass(frozen=True)
class BoundHashes:
    source: str
    corpus: str
    manifest: str
    framework: str
    evaluator: str

    def valid(self) -> bool:
        return all(_is_sha256(value) for value in asdict(self).values())


@dataclass(frozen=True)
class ScenarioContract:
    """Internal future scenario schema; the framework supplies no instances."""

    scenario_id: str
    group: str
    coverage_cell: str
    action: str
    utterances: tuple[str, ...]
    reference_date: str
    expected: Mapping[str, Any]
    slices: Mapping[str, str]

    @property
    def is_multi_turn(self) -> bool:
        return len(self.utterances) > 1


@dataclass(frozen=True)
class TypedObservation:
    """Internal typed result. Case identity is discarded by aggregation."""

    scenario_id: str
    repeat_index: int
    dimension_passes: Mapping[str, bool]
    safe: bool
    failure_layers: Mapping[str, bool]
    slices: Mapping[str, str]

    @property
    def complete(self) -> bool:
        return all(self.dimension_passes.get(name) is True for name in DIMENSIONS)


class ScenarioEvaluator(Protocol):
    def __call__(self, scenario: ScenarioContract, repeat_index: int) -> TypedObservation:
        ...


@dataclass(frozen=True)
class EvaluationContext:
    evaluator: ScenarioEvaluator

    def evaluate(self, scenarios: Sequence[ScenarioContract]) -> tuple[TypedObservation, ...]:
        return tuple(
            self.evaluator(scenario, repeat_index)
            for scenario in scenarios
            for repeat_index in range(REPEATS)
        )


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()


def validate_manifest(
    manifest: Mapping[str, Any], scenarios: Sequence[ScenarioContract]
) -> ValidationResult:
    errors: list[str] = []
    exact_counts = {
        "group_count": GROUP_COUNT,
        "scenario_count": SCENARIO_COUNT,
        "multi_turn_count": MULTI_TURN_COUNT,
        "one_shot_count": ONE_SHOT_COUNT,
        "action_count": len(ACTIONS),
        "coverage_cell_count": SCENARIO_COUNT,
        "repeats": REPEATS,
    }
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append("manifest schema_version is not exact")
    if manifest.get("attempt_id") != ATTEMPT_ID:
        errors.append("manifest attempt_id is not exact")
    for field_name, expected in exact_counts.items():
        if manifest.get(field_name) != expected:
            errors.append(f"manifest {field_name} must equal {expected}")
    if len(scenarios) != SCENARIO_COUNT:
        errors.append(f"scenario population must equal {SCENARIO_COUNT}")
        return ValidationResult(False, tuple(errors))

    scenario_ids = [scenario.scenario_id for scenario in scenarios]
    groups = [scenario.group for scenario in scenarios]
    cells = [scenario.coverage_cell for scenario in scenarios]
    actions = {scenario.action for scenario in scenarios}
    multi_turn = sum(scenario.is_multi_turn for scenario in scenarios)
    group_counts = {group: groups.count(group) for group in set(groups)}
    group_multi_counts = {
        group: sum(scenario.is_multi_turn for scenario in scenarios if scenario.group == group)
        for group in set(groups)
    }

    if len(set(scenario_ids)) != SCENARIO_COUNT or any(not item for item in scenario_ids):
        errors.append("scenario IDs must be non-empty and unique")
    if len(group_counts) != GROUP_COUNT or any(count != 12 for count in group_counts.values()):
        errors.append("groups must be exactly 24 populations of 12")
    if any(count != 3 for count in group_multi_counts.values()):
        errors.append("every group must contain exactly three multi-turn scenarios")
    if len(set(cells)) != SCENARIO_COUNT or any(not item for item in cells):
        errors.append("coverage cells must be non-empty and unique")
    if actions != ACTIONS:
        errors.append("action population is not exact")
    if multi_turn != MULTI_TURN_COUNT:
        errors.append(f"multi-turn population must equal {MULTI_TURN_COUNT}")
    if sum(not scenario.is_multi_turn for scenario in scenarios) != ONE_SHOT_COUNT:
        errors.append(f"one-shot population must equal {ONE_SHOT_COUNT}")
    if any(not scenario.utterances or not scenario.reference_date for scenario in scenarios):
        errors.append("scenario utterances and reference date must be present")
    return ValidationResult(not errors, tuple(errors))


def _slice_rows(observations: Sequence[TypedObservation]) -> dict[str, list[dict[str, Any]]]:
    categories = sorted({category for item in observations for category in item.slices})
    result: dict[str, list[dict[str, Any]]] = {}
    for category in categories:
        keys = sorted({item.slices[category] for item in observations if category in item.slices})
        rows: list[dict[str, Any]] = []
        for key in keys:
            selected = [item for item in observations if item.slices.get(category) == key]
            passed = sum(item.complete for item in selected)
            rows.append(
                {"slice_key": key, "passed": passed, "failed": len(selected) - passed, "total": len(selected)}
            )
        result[category] = rows
    return result


def _repeat_variance(observations: Sequence[TypedObservation]) -> int:
    by_scenario: dict[str, list[TypedObservation]] = {}
    for observation in observations:
        by_scenario.setdefault(observation.scenario_id, []).append(observation)
    variance = 0
    for repeats in by_scenario.values():
        signatures = {
            canonical_json(
                {
                    "dimensions": dict(item.dimension_passes),
                    "safe": item.safe,
                    "layers": dict(item.failure_layers),
                }
            )
            for item in repeats
        }
        variance += len(signatures) != 1
    return variance


def validate_observations(
    observations: Sequence[TypedObservation], scenarios: Sequence[ScenarioContract]
) -> ValidationResult:
    errors: list[str] = []
    scenario_ids = {scenario.scenario_id for scenario in scenarios}
    if len(observations) != SAMPLE_COUNT:
        errors.append(f"observation population must equal {SAMPLE_COUNT}")
    if {item.scenario_id for item in observations} != scenario_ids:
        errors.append("observation scenario population does not match manifest")
    by_scenario: dict[str, list[TypedObservation]] = {}
    for observation in observations:
        by_scenario.setdefault(observation.scenario_id, []).append(observation)
        if set(observation.dimension_passes) != set(DIMENSIONS):
            errors.append("observation dimension population is not exact")
        if set(observation.failure_layers) != set(FAILURE_LAYERS):
            errors.append("observation failure-layer population is not exact")
        if observation.safe == (observation.failure_layers.get("safety") is True):
            errors.append("observation safety and safety-layer evidence disagree")
        matching = next(
            (scenario for scenario in scenarios if scenario.scenario_id == observation.scenario_id),
            None,
        )
        if matching is not None and dict(observation.slices) != dict(matching.slices):
            errors.append("observation slices do not match the scenario contract")
    if any(
        len(repeats) != REPEATS
        or {item.repeat_index for item in repeats} != set(range(REPEATS))
        for repeats in by_scenario.values()
    ):
        errors.append("every scenario must have exact repeat indexes 0 and 1")
    return ValidationResult(not errors, tuple(dict.fromkeys(errors)))


def aggregate_observations(
    observations: Sequence[TypedObservation],
    hashes: BoundHashes,
    *,
    evaluation_exception_count: int = 0,
    case_level_artifact_count: int = 0,
) -> dict[str, Any]:
    """Reduce internal observations to the only committable aggregate shape."""
    complete = sum(item.complete for item in observations)
    safe = sum(item.safe for item in observations)
    per_dimension = {
        name: {
            "passed": sum(item.dimension_passes.get(name) is True for item in observations),
            "failed": sum(item.dimension_passes.get(name) is not True for item in observations),
            "total": len(observations),
        }
        for name in DIMENSIONS
    }
    failure_layers = {
        layer: sum(item.failure_layers.get(layer) is True for item in observations)
        for layer in FAILURE_LAYERS
    }
    action_counts = {
        action: sum(item.slices.get("action") == action for item in observations)
        for action in sorted(ACTIONS)
    }
    return {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "attempt_id": ATTEMPT_ID,
        "group_count": GROUP_COUNT,
        "scenario_count": SCENARIO_COUNT,
        "multi_turn_count": MULTI_TURN_COUNT,
        "one_shot_count": ONE_SHOT_COUNT,
        "coverage_cell_count": SCENARIO_COUNT,
        "repeats_per_scenario": REPEATS,
        "sample_count": len(observations),
        "complete_contract": {"passed": complete, "failed": len(observations) - complete, "total": len(observations)},
        "safety": {"passed": safe, "failed": len(observations) - safe, "total": len(observations)},
        "per_dimension": per_dimension,
        "failure_layers": failure_layers,
        "action_counts": action_counts,
        "slices": _slice_rows(observations),
        "evaluation_exception_count": evaluation_exception_count,
        "missing_dimension_count": sum(
            set(item.dimension_passes) != set(DIMENSIONS) for item in observations
        ),
        "case_level_artifact_count": case_level_artifact_count,
        "repeat_variance_count": _repeat_variance(observations),
        "hashes": asdict(hashes),
    }


def _find_forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in FORBIDDEN_AGGREGATE_KEYS:
                found.add(lowered)
            found.update(_find_forbidden_keys(nested))
    elif isinstance(value, (list, tuple)):
        for nested in value:
            found.update(_find_forbidden_keys(nested))
    return found


def validate_aggregate_structure(
    report: Mapping[str, Any], expected_hashes: BoundHashes
) -> ValidationResult:
    errors: list[str] = []
    if _find_forbidden_keys(report):
        errors.append("aggregate contains forbidden case-level keys")
    if report.get("schema_version") != AGGREGATE_SCHEMA_VERSION:
        errors.append("aggregate schema_version is not exact")
    if report.get("attempt_id") != ATTEMPT_ID:
        errors.append("aggregate attempt_id is not exact")
    sample_count = report.get("sample_count")
    if not isinstance(sample_count, int) or sample_count < 0:
        errors.append("aggregate sample_count is malformed")
        sample_count = 0
    for field_name in (
        "group_count",
        "scenario_count",
        "multi_turn_count",
        "one_shot_count",
        "coverage_cell_count",
        "repeats_per_scenario",
        "evaluation_exception_count",
        "missing_dimension_count",
        "case_level_artifact_count",
        "repeat_variance_count",
    ):
        value = report.get(field_name)
        if not isinstance(value, int) or value < 0:
            errors.append(f"aggregate {field_name} is malformed")
    if not expected_hashes.valid() or report.get("hashes") != asdict(expected_hashes):
        errors.append("aggregate hash bindings are not exact")

    for field_name in ("complete_contract", "safety"):
        counts = report.get(field_name)
        if not isinstance(counts, Mapping) or counts.get("total") != sample_count:
            errors.append(f"aggregate {field_name} total is malformed")
        elif counts.get("passed", -1) + counts.get("failed", -1) != sample_count:
            errors.append(f"aggregate {field_name} arithmetic is invalid")
    dimensions = report.get("per_dimension")
    if not isinstance(dimensions, Mapping) or set(dimensions) != set(DIMENSIONS):
        errors.append("aggregate dimension population is not exact")
    else:
        for name, counts in dimensions.items():
            if (
                not isinstance(counts, Mapping)
                or counts.get("total") != sample_count
                or counts.get("passed", -1) + counts.get("failed", -1) != sample_count
            ):
                errors.append(f"aggregate dimension arithmetic is invalid: {name}")
    layers = report.get("failure_layers")
    if not isinstance(layers, Mapping) or set(layers) != set(FAILURE_LAYERS):
        errors.append("aggregate failure-layer population is not exact")
    elif any(not isinstance(value, int) or value < 0 or value > sample_count for value in layers.values()):
        errors.append("aggregate failure-layer count is invalid")

    action_counts = report.get("action_counts")
    if not isinstance(action_counts, Mapping) or set(action_counts) != ACTIONS:
        errors.append("aggregate action population is not exact")
    elif any(not isinstance(value, int) or value <= 0 for value in action_counts.values()):
        errors.append("aggregate action count is malformed")
    elif sum(action_counts.values()) != sample_count:
        errors.append("aggregate action arithmetic is invalid")

    slices = report.get("slices")
    if not isinstance(slices, Mapping) or not REQUIRED_SLICE_CATEGORIES.issubset(slices):
        errors.append("aggregate slices are missing")
    else:
        for category, rows in slices.items():
            if not isinstance(rows, list) or not rows:
                errors.append(f"slice category is empty: {category}")
                continue
            keys = [row.get("slice_key") for row in rows if isinstance(row, Mapping)]
            if len(keys) != len(rows) or len(set(keys)) != len(keys):
                errors.append(f"slice keys are invalid: {category}")
            total = 0
            for row in rows:
                if not isinstance(row, Mapping):
                    errors.append(f"slice row is malformed: {category}")
                    continue
                passed, failed, row_total = row.get("passed"), row.get("failed"), row.get("total")
                if not all(isinstance(value, int) and value >= 0 for value in (passed, failed, row_total)):
                    errors.append(f"slice count is malformed: {category}")
                elif passed + failed != row_total:
                    errors.append(f"slice arithmetic is invalid: {category}")
                total += row_total if isinstance(row_total, int) else 0
            if total != sample_count:
                errors.append(f"slice category total is malformed: {category}")
    return ValidationResult(not errors, tuple(errors))


def validate_aggregate(
    report: Mapping[str, Any], expected_hashes: BoundHashes
) -> ValidationResult:
    errors = list(validate_aggregate_structure(report, expected_hashes).errors)
    exact_counts = {
        "group_count": GROUP_COUNT,
        "scenario_count": SCENARIO_COUNT,
        "multi_turn_count": MULTI_TURN_COUNT,
        "one_shot_count": ONE_SHOT_COUNT,
        "coverage_cell_count": SCENARIO_COUNT,
        "repeats_per_scenario": REPEATS,
        "sample_count": SAMPLE_COUNT,
        "evaluation_exception_count": 0,
        "missing_dimension_count": 0,
        "case_level_artifact_count": 0,
        "repeat_variance_count": 0,
    }
    for field_name, expected in exact_counts.items():
        if report.get(field_name) != expected:
            errors.append(f"aggregate {field_name} must equal {expected}")
    return ValidationResult(not errors, tuple(dict.fromkeys(errors)))


@dataclass(frozen=True)
class OneShotPaths:
    root: Path
    seal_name: str = "lc4v6-source-seal.json"
    marker_name: str = "lc4v6-attempt-marker.json"
    report_name: str = "lc4v6-aggregate-report.json"
    lock_name: str = "lc4v6-attempt.lock"

    @property
    def seal(self) -> Path:
        return self.root / self.seal_name

    @property
    def marker(self) -> Path:
        return self.root / self.marker_name

    @property
    def report(self) -> Path:
        return self.root / self.report_name

    @property
    def lock(self) -> Path:
        return self.root / self.lock_name


def build_unconsumed_seal(source_commit: str, hashes: BoundHashes) -> dict[str, Any]:
    return {
        "schema_version": SEAL_SCHEMA_VERSION,
        "attempt_id": ATTEMPT_ID,
        "source_commit": source_commit,
        "hashes": asdict(hashes),
        "consumed": False,
    }


class OneShotStateMachine:
    """Fail-closed one-shot transition with an exclusive durable lock.

    Multiple-file replacement cannot be globally atomic. The exclusive lock is
    intentionally retained: any interruption leaves state non-rerunnable and
    therefore fails closed instead of silently authorizing a second evaluation.
    """

    def __init__(self, paths: OneShotPaths, source_commit: str, hashes: BoundHashes):
        self.paths = paths
        self.source_commit = source_commit
        self.hashes = hashes

    def _read_json(self, path: Path) -> Mapping[str, Any] | None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return payload if isinstance(payload, Mapping) else None

    def validate_prerun(self) -> ValidationResult:
        errors: list[str] = []
        expected = build_unconsumed_seal(self.source_commit, self.hashes)
        seal = self._read_json(self.paths.seal)
        if seal != expected:
            errors.append("source seal is absent, malformed, consumed, or drifted")
        for path, label in (
            (self.paths.marker, "attempt marker"),
            (self.paths.report, "aggregate report"),
            (self.paths.lock, "attempt lock"),
        ):
            if path.exists():
                errors.append(f"{label} already exists")
        return ValidationResult(not errors, tuple(errors))

    @staticmethod
    def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        encoded = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        with temporary.open("xb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def consume(self, report: Mapping[str, Any]) -> ValidationResult:
        preflight = self.validate_prerun()
        if not preflight.valid:
            return preflight
        report_validation = validate_aggregate_structure(report, self.hashes)
        if not report_validation.valid:
            return report_validation
        self.paths.root.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(self.paths.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return ValidationResult(False, ("attempt lock already exists",))
        with os.fdopen(descriptor, "w", encoding="utf-8") as lock:
            lock.write(ATTEMPT_ID + "\n")
            lock.flush()
            os.fsync(lock.fileno())

        report_hash = sha256_payload(report)
        consumed_seal = {
            **build_unconsumed_seal(self.source_commit, self.hashes),
            "consumed": True,
            "report_hash": report_hash,
        }
        consumed_seal_hash = sha256_payload(consumed_seal)
        marker = {
            "schema_version": "lc4v6.attempt_marker.v1",
            "attempt_id": ATTEMPT_ID,
            "report_hash": report_hash,
            "consumed_seal_hash": consumed_seal_hash,
        }
        try:
            self._atomic_json(self.paths.report, report)
            self._atomic_json(self.paths.seal, consumed_seal)
            self._atomic_json(self.paths.marker, marker)
        except OSError as error:
            return ValidationResult(False, (f"one-shot transition failed closed: {error}",))
        return ValidationResult(True)


__all__ = [
    "ACTIONS",
    "AGGREGATE_SCHEMA_VERSION",
    "ATTEMPT_ID",
    "BoundHashes",
    "DIMENSIONS",
    "EvaluationContext",
    "FAILURE_LAYERS",
    "GROUP_COUNT",
    "MANIFEST_SCHEMA_VERSION",
    "MULTI_TURN_COUNT",
    "ONE_SHOT_COUNT",
    "OneShotPaths",
    "OneShotStateMachine",
    "REPEATS",
    "REQUIRED_SLICE_CATEGORIES",
    "SAMPLE_COUNT",
    "SCENARIO_COUNT",
    "SCHEMA_VERSION",
    "SEAL_SCHEMA_VERSION",
    "ScenarioContract",
    "TypedObservation",
    "ValidationResult",
    "aggregate_observations",
    "build_unconsumed_seal",
    "canonical_json",
    "sha256_bytes",
    "sha256_payload",
    "sha256_text",
    "validate_aggregate",
    "validate_aggregate_structure",
    "validate_manifest",
    "validate_observations",
]
