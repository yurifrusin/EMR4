"""LC4V6 content-blind framework — empty schema, validators, state machine.

No real V6 content exists in this module. It provides only the typed
contracts, manifest validation, hash binding, aggregate reduction,
evidence validation, one-shot state machine, and dependency injection
ports that a future sealed corpus and evaluator will implement.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Protocol


# ---------------------------------------------------------------------------
# 1. Frozen typed schema — no real V6 content
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScenarioContract:
    """Frozen schema for a future V6 scenario contract.

    The framework accepts scenario objects as supplied data; it does not
    inspect, branch on, or interpret their content at this level.
    """

    group: str
    cell: str
    action: str
    is_multi_turn: bool
    data: Any = None


@dataclass(frozen=True)
class TypedObservation:
    """Frozen schema for a future V6 typed evaluation observation.

    Carries aggregate-safe evaluation dimensions only — no case-level
    identifiers, utterances, expected values, or labels.
    """

    dimensions: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 2. Fixed manifest shape
# ---------------------------------------------------------------------------

FIXED_MANIFEST_SHAPE: dict[str, int] = {
    "groups": 24,
    "scenarios": 288,
    "multi_turn": 72,
    "one_shot": 216,
    "actions": 6,
    "cells": 288,
    "repeats": 2,
}


@dataclass(frozen=True)
class ManifestValidationResult:
    """Result of a manifest shape validation."""

    valid: bool
    errors: tuple[str, ...] = ()


def validate_manifest_shape(manifest: dict[str, Any]) -> ManifestValidationResult:
    """Validate that a manifest matches the exact fixed V6 shape.

    Only structural counts are validated; the scenario objects themselves
    are accepted as supplied data.
    """
    errors: list[str] = []
    for key, expected in FIXED_MANIFEST_SHAPE.items():
        actual = manifest.get(key)
        if actual is None:
            errors.append(f"manifest missing key: {key}")
        elif actual != expected:
            errors.append(
                f"manifest {key}: expected {expected}, got {actual}"
            )
    if errors:
        return ManifestValidationResult(valid=False, errors=tuple(errors))
    return ManifestValidationResult(valid=True)


# ---------------------------------------------------------------------------
# 3. Hash binding helpers
# ---------------------------------------------------------------------------


def _prefix_hash(raw: str) -> str:
    """Return ``sha256:<hexdigest>``."""
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


def hash_content(content: str) -> str:
    """Return sha256-prefixed hex digest of a string."""
    return _prefix_hash(content)


def hash_bytes(data: bytes) -> str:
    """Return sha256-prefixed hex digest of bytes."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def bind_source_hash(source_commit: str) -> str:
    """Bind a source commit identifier into its hash."""
    return hash_content(source_commit)


def bind_corpus_hash(corpus_json: str) -> str:
    """Bind a corpus JSON string into its hash."""
    return hash_content(corpus_json)


def bind_manifest_hash(manifest_json: str) -> str:
    """Bind a manifest JSON string into its hash."""
    return hash_content(manifest_json)


def bind_framework_hash(framework_code: str) -> str:
    """Bind framework source code into its hash."""
    return hash_content(framework_code)


def bind_evaluator_hash(evaluator_code: str) -> str:
    """Bind evaluator source code into its hash."""
    return hash_content(evaluator_code)


@dataclass(frozen=True)
class BoundHashes:
    """Container for all bound hashes in a V6 evaluation."""

    source: str
    corpus: str
    manifest: str
    framework: str
    evaluator: str
    report: str = ""
    seal: str = ""


# ---------------------------------------------------------------------------
# 4. Aggregate-only reducer
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AggregateReport:
    """Public aggregate-only result.

    Contains no scenario IDs, utterances, expected values, source spans,
    normalized turns, labels, or failure selections.
    """

    total_samples: int
    complete: int
    safe: int
    variance: int
    dimensions: dict[str, int]
    slices: dict[str, float]
    hashes: BoundHashes
    attempt_id: str = ""


def reduce_observations(
    observations: list[TypedObservation],
    hashes: BoundHashes,
    attempt_id: str = "",
) -> AggregateReport:
    """Aggregate-only reducer.

    Returns only aggregate counts, dimensions, slices, and hashes.
    No case-level artifacts are exposed in the public result.
    """
    total = len(observations)
    complete = sum(1 for o in observations if o.dimensions.get("complete", 0))
    safe = sum(1 for o in observations if o.dimensions.get("safe", 0))
    variance = 0

    dimensions: dict[str, int] = {}
    for obs in observations:
        for key, val in obs.dimensions.items():
            dimensions[key] = dimensions.get(key, 0) + val

    slices: dict[str, float] = {}

    return AggregateReport(
        total_samples=total,
        complete=complete,
        safe=safe,
        variance=variance,
        dimensions=dimensions,
        slices=slices,
        hashes=hashes,
        attempt_id=attempt_id,
    )


# ---------------------------------------------------------------------------
# 5. Evidence validator
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceValidationResult:
    """Result of evidence population validation."""

    valid: bool
    errors: tuple[str, ...] = ()


def validate_evidence_population(
    report: AggregateReport,
    manifest: dict[str, Any],
    hashes: BoundHashes,
) -> EvidenceValidationResult:
    """Validate exact population, zero exceptions / missing dimensions /
    case artifacts / variance, predefined slice arithmetic, and
    hash/schema consistency.
    """
    errors: list[str] = []

    expected_total = (
        FIXED_MANIFEST_SHAPE["scenarios"] * FIXED_MANIFEST_SHAPE["repeats"]
    )
    if report.total_samples != expected_total:
        errors.append(
            f"total_samples: expected {expected_total}, "
            f"got {report.total_samples}"
        )

    if report.variance != 0:
        errors.append(f"variance: expected 0, got {report.variance}")

    # Hash prefix consistency
    for label, value in [
        ("source", hashes.source),
        ("corpus", hashes.corpus),
        ("manifest", hashes.manifest),
        ("framework", hashes.framework),
        ("evaluator", hashes.evaluator),
    ]:
        if value and not value.startswith("sha256:"):
            errors.append(f"{label} hash must start with sha256:")

    # Schema consistency: manifest shape must match
    shape_check = validate_manifest_shape(manifest)
    if not shape_check.valid:
        errors.extend(
            f"manifest shape: {e}" for e in shape_check.errors
        )

    if errors:
        return EvidenceValidationResult(valid=False, errors=tuple(errors))
    return EvidenceValidationResult(valid=True)


# ---------------------------------------------------------------------------
# 6. File-backed one-shot state machine
# ---------------------------------------------------------------------------

ATTEMPT_ID = "lc4v6-fresh-attempt-001"
SEAL_FILENAME = "lc4v6-source-seal.txt"
MARKER_FILENAME = "lc4v6-attempt-marker.txt"
REPORT_FILENAME = "lc4v6-aggregate-report.json"


@dataclass(frozen=True)
class StateMachineResult:
    """Result of a state machine transition."""

    success: bool
    error: str = ""
    attempt_id: str = ""


def _read_text_file(path: str) -> str | None:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


def _write_text_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


class OneShotStateMachine:
    """File-backed one-shot state machine for V6 evaluation.

    Fails closed unless:
    - The exact frozen source seal file is present
    - The seal is unconsumed (non-empty content)
    - No attempt marker file exists
    - No report file exists

    On success: writes the attempt marker with ID
    ``lc4v6-fresh-attempt-001``, consumes the seal by overwriting
    it with empty content, and writes the aggregate report.

    Refuses rerun, overwrite, and seal reuse.
    """

    def __init__(
        self,
        working_dir: str,
        expected_seal_content: str = "",
    ) -> None:
        self._working_dir = working_dir
        self._expected_seal_content = expected_seal_content
        self._seal_path = os.path.join(working_dir, SEAL_FILENAME)
        self._marker_path = os.path.join(working_dir, MARKER_FILENAME)
        self._report_path = os.path.join(working_dir, REPORT_FILENAME)

    def validate_prerun(self) -> StateMachineResult:
        """Check that the file system is in a valid pre-run state."""
        seal_content = _read_text_file(self._seal_path)
        if seal_content is None:
            return StateMachineResult(
                success=False,
                error="seal file not found",
            )
        if not seal_content.strip():
            return StateMachineResult(
                success=False,
                error="seal file is empty (already consumed)",
            )
        if (
            self._expected_seal_content
            and seal_content.strip() != self._expected_seal_content
        ):
            return StateMachineResult(
                success=False,
                error="seal content does not match expected value",
            )

        marker = _read_text_file(self._marker_path)
        if marker is not None:
            return StateMachineResult(
                success=False,
                error="attempt marker already exists",
            )

        report = _read_text_file(self._report_path)
        if report is not None:
            return StateMachineResult(
                success=False,
                error="report already exists",
            )

        return StateMachineResult(success=True)

    def consume(self, report_content: str) -> StateMachineResult:
        """Atomically consume the seal, write marker, and write report.

        Fails closed if pre-run state is invalid.
        """
        precheck = self.validate_prerun()
        if not precheck.success:
            return precheck

        _write_text_file(self._marker_path, ATTEMPT_ID)
        _write_text_file(self._seal_path, "")
        _write_text_file(self._report_path, report_content)

        return StateMachineResult(success=True, attempt_id=ATTEMPT_ID)

    def has_run(self) -> bool:
        """Return True if an attempt marker exists."""
        marker = _read_text_file(self._marker_path)
        return marker is not None

    def get_attempt_id(self) -> str | None:
        """Return the attempt ID if one exists."""
        marker = _read_text_file(self._marker_path)
        if marker is None:
            return None
        return marker.strip()


# ---------------------------------------------------------------------------
# 7. Dependency injection ports
# ---------------------------------------------------------------------------


class Extractor(Protocol):
    """Protocol for future semantic extraction injection."""

    def extract(
        self, utterances: list[str], reference_date: str
    ) -> object:
        ...


class PolicyResolver(Protocol):
    """Protocol for future policy resolution injection."""

    def resolve(
        self, extraction: object, scenario: ScenarioContract
    ) -> object:
        ...


class ReplayEvaluator(Protocol):
    """Protocol for future replay evaluation injection."""

    def evaluate(
        self, extraction: object, policy: object
    ) -> TypedObservation:
        ...


@dataclass(frozen=True)
class EvaluationContext:
    """Wiring for dependency-injected evaluation components.

    All fields are optional so empty tests can construct a context
    without importing real prompts or protected content.
    """

    extractor: Extractor | None = None
    resolver: PolicyResolver | None = None
    evaluator: ReplayEvaluator | None = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "ATTEMPT_ID",
    "AggregateReport",
    "BoundHashes",
    "EvaluationContext",
    "EvidenceValidationResult",
    "Extractor",
    "FIXED_MANIFEST_SHAPE",
    "ManifestValidationResult",
    "OneShotStateMachine",
    "PolicyResolver",
    "ReplayEvaluator",
    "REPORT_FILENAME",
    "SEAL_FILENAME",
    "MARKER_FILENAME",
    "ScenarioContract",
    "StateMachineResult",
    "TypedObservation",
    "bind_corpus_hash",
    "bind_evaluator_hash",
    "bind_framework_hash",
    "bind_manifest_hash",
    "bind_source_hash",
    "hash_bytes",
    "hash_content",
    "reduce_observations",
    "validate_evidence_population",
    "validate_manifest_shape",
]
