"""LC4V2 content-blind framework: immutable contracts and one-shot evaluation harness.

This module implements the provider-free, content-blind LC4V2 manifest, seal,
aggregate-report, and consumption contracts defined in the Sol acceptance
document ``lc4v2-sol-contract.md``.  No v1 fixture, support module, seal,
receipt, report, or path is imported, inspected, or referenced.

.. warning::

    This is a **content-blind framework** only.  Real v2 scenarios do not yet
    exist.  All evaluation logic is a placeholder that validates schema and
    manifest integrity without executing interpretation, replay, or scoring.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.bernie.scenario_spec import ReceptionScenarioSpec

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CANONICAL_ENCODING = "utf-8"
JSON_INDENT = 2

CORPUS_VERSION = "lc4-holdout-v2"
EVALUATION_ID = "lc4-holdout-v2-baseline-001"
DEFAULT_REPEAT_COUNT = 2

# Production defaults — fail closed
DEFAULT_GROUP_COUNT = 24
DEFAULT_VARIANT_COUNT = 288
DEFAULT_MULTI_TURN_COUNT = 72

# Samples = variants × repeats
SAMPLES_PER_EVALUATION = DEFAULT_VARIANT_COUNT * DEFAULT_REPEAT_COUNT  # 576

# Schema identifiers
AGGREGATE_SCHEMA_VERSION = "lc4v2.aggregate.v1"
SEAL_SCHEMA_VERSION = "lc4v2.seal.v1"

# Multi-turn dialogue forms (anything other than one-shot)
MULTI_TURN_FORMS: frozenset[str] = frozenset(
    {
        "clarification",
        "correction",
        "reversal",
        "ellipsis",
        "anaphora",
        "repeated",
        "session_restart",
    }
)

# Keys that must never appear anywhere in an aggregate report
FORBIDDEN_REPORT_KEYS: frozenset[str] = frozenset(
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
        "observations",
        "case_finding",
        "case_findings",
        "per_case",
        "per_case_results",
        "individual_results",
        "case_results",
    }
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _canonical_json(obj: Any) -> str:
    """Serialize *obj* to canonical JSON (sorted keys, compact separators)."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def _sha256(data: bytes) -> str:
    """Return raw hex SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_digest(data: bytes) -> str:
    """Return ``sha256:<hex>`` prefixed digest."""
    return f"sha256:{_sha256(data)}"


# ---------------------------------------------------------------------------
# 1.  Group envelope
# ---------------------------------------------------------------------------


class ScenarioGroupEnvelope(BaseModel):
    """A group envelope containing exactly 12 ``ReceptionScenarioSpec`` payloads.

    Every variant must be Gold / adjudicated.  Exactly three variants per group
    must be multi-turn.
    """

    model_config = ConfigDict(extra="forbid")

    group_id: str = Field(min_length=1)
    variants: list[ReceptionScenarioSpec] = Field(min_length=12, max_length=12)

    @model_validator(mode="after")
    def _validate_group_shape(self) -> ScenarioGroupEnvelope:
        if len(self.variants) != 12:
            raise ValueError(
                f"group {self.group_id!r} must have exactly 12 variants, "
                f"got {len(self.variants)}"
            )

        multi_turn_count = sum(
            1 for v in self.variants if v.dialogue_form in MULTI_TURN_FORMS
        )
        if multi_turn_count != 3:
            raise ValueError(
                f"group {self.group_id!r} must have exactly 3 multi-turn variants, "
                f"got {multi_turn_count}"
            )

        ids = [v.scenario_id for v in self.variants]
        if len(ids) != len(set(ids)):
            seen = {i for i in ids if ids.count(i) > 1}
            raise ValueError(
                f"group {self.group_id!r} has duplicate variant IDs: {sorted(seen)}"
            )

        for v in self.variants:
            if v.provenance != "gold":
                raise ValueError(
                    f"variant {v.scenario_id!r} has non-gold provenance: {v.provenance}"
                )
            if v.adjudication != "adjudicated":
                raise ValueError(
                    f"variant {v.scenario_id!r} has non-adjudicated: {v.adjudication}"
                )
            if "expected_outcome_kind" not in v.model_fields_set:
                raise ValueError(
                    f"variant {v.scenario_id!r} missing expected_outcome_kind"
                )

        return self


# ---------------------------------------------------------------------------
# 2.  Manifest
# ---------------------------------------------------------------------------


class ManifestFileEntry(BaseModel):
    """A single file entry binding a relative path to its SHA-256 digest."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    relative_path: str = Field(min_length=1)
    sha256: str = Field(min_length=1)

    @field_validator("relative_path")
    @classmethod
    def _reject_absolute_and_traversal(
        cls, value: str
    ) -> str:
        if os.path.isabs(value) or value.startswith("/"):
            raise ValueError(f"absolute path forbidden: {value}")
        parts = value.replace("\\", "/").split("/")
        if ".." in parts:
            raise ValueError(f"path traversal forbidden: {value}")
        return value


class Manifest(BaseModel):
    """Bind every group file, SHA-256 hashes, corpus hash, and exact counts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    corpus_version: str = Field(
        default=CORPUS_VERSION, pattern=r"^lc4-holdout-v2$"
    )
    files: list[ManifestFileEntry]
    corpus_hash: str = Field(min_length=1)
    group_count: int = Field(default=DEFAULT_GROUP_COUNT, ge=1)
    variant_count: int = Field(default=DEFAULT_VARIANT_COUNT, ge=1)
    multi_turn_count: int = Field(default=DEFAULT_MULTI_TURN_COUNT, ge=0)

    @field_validator("files")
    @classmethod
    def _reject_duplicate_paths(
        cls, value: list[ManifestFileEntry]
    ) -> list[ManifestFileEntry]:
        paths = [e.relative_path for e in value]
        if len(paths) != len(set(paths)):
            dupes = {p for p in paths if paths.count(p) > 1}
            raise ValueError(f"duplicate manifest paths: {sorted(dupes)}")
        return value

    def compute_hash(self) -> str:
        """Return ``sha256:<hex>`` of the canonical JSON encoding."""
        data = self.model_dump(mode="json")
        raw = _canonical_json(data)
        return sha256_digest(raw.encode(CANONICAL_ENCODING))


# ---------------------------------------------------------------------------
# 3.  Pre-consumption seal
# ---------------------------------------------------------------------------


class PreConsumptionSeal(BaseModel):
    """Pre-consumption seal binding corpus version, manifest, commit, and identity."""

    model_config = ConfigDict(extra="forbid")

    corpus_version: str = Field(
        default=CORPUS_VERSION, pattern=r"^lc4-holdout-v2$"
    )
    manifest_hash: str = Field(min_length=1)
    source_commit: str = Field(min_length=1)
    evaluator_version: str = Field(min_length=1)
    schema_version: str = Field(default=SEAL_SCHEMA_VERSION, min_length=1)
    evaluation_id: str = Field(
        default=EVALUATION_ID, pattern=r"^lc4-holdout-v2-baseline-001$"
    )
    repeat_count: int = Field(default=DEFAULT_REPEAT_COUNT, ge=1)
    state: Literal["created", "consumed"]


# ---------------------------------------------------------------------------
# 4.  Aggregate-only report
# ---------------------------------------------------------------------------


class AggregateDimension(BaseModel):
    """Passed / failed totals for one evaluation dimension."""

    model_config = ConfigDict(extra="forbid")

    passed: int = Field(ge=0)
    failed: int = Field(ge=0)


class FailureLayer(BaseModel):
    """Count of failures attributed to a specific layer."""

    model_config = ConfigDict(extra="forbid")

    layer: str = Field(min_length=1)
    total: int = Field(ge=0)


class CriticalSlice(BaseModel):
    """Predefined critical-slice aggregate (no per-case data)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    total: int = Field(ge=0)


class CoverageCell(BaseModel):
    """Coverage-lattice cell count."""

    model_config = ConfigDict(extra="forbid")

    cell: str = Field(min_length=1)
    count: int = Field(ge=0)


class AggregateReport(BaseModel):
    """Aggregate-only evaluation result with no per-case data.

    The report exposes only dimension totals, failure layers, safety, variance,
    critical-slice aggregates, coverage-cell counts, hashes, and provenance.
    It must never contain utterance, dialogue, group/scenario/variant
    identifiers, expected labels/outcomes/tools/deltas, source spans,
    normalized values, observations, case findings, or per-case results.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        default=AGGREGATE_SCHEMA_VERSION, min_length=1
    )
    dimensions: dict[str, AggregateDimension]
    failure_layers: list[FailureLayer]
    safety_pass: int = Field(ge=0)
    safety_total: int = Field(ge=0)
    variance: float
    critical_slices: list[CriticalSlice] = Field(default_factory=list)
    coverage_cells: list[CoverageCell] = Field(default_factory=list)
    corpus_hash: str = Field(min_length=1)
    report_hash: str = Field(min_length=1, default="")

    @model_validator(mode="after")
    def _validate_dimension_totals(self) -> AggregateReport:
        totals = {name: dim.passed + dim.failed for name, dim in self.dimensions.items()}
        if not totals:
            raise ValueError("at least one dimension is required")
        expected = next(iter(totals.values()))
        for name, total in totals.items():
            if total != expected:
                raise ValueError(
                    f"dimension {name!r} total ({total}) != expected "
                    f"{expected} (all dimensions must have the same total)"
                )
        return self

    def check_forbidden_keys(self) -> None:
        """Raise ``ValueError`` if any key in ``FORBIDDEN_REPORT_KEYS`` appears."""

        def _walk(obj: Any, path: str) -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    full = f"{path}.{key}" if path else key
                    if key in FORBIDDEN_REPORT_KEYS:
                        raise ValueError(
                            f"forbidden report key at {full!r}: {key!r}"
                        )
                    _walk(value, full)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    _walk(item, f"{path}[{i}]")

        _walk(self.model_dump(mode="json"), "")


# ---------------------------------------------------------------------------
# 5.  Consumed seal
# ---------------------------------------------------------------------------


class ConsumedSeal(BaseModel):
    """One-shot consumed seal binding the aggregate report hash exactly once."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    corpus_version: str = Field(
        default=CORPUS_VERSION, pattern=r"^lc4-holdout-v2$"
    )
    manifest_hash: str = Field(min_length=1)
    source_commit: str = Field(min_length=1)
    evaluator_version: str = Field(min_length=1)
    schema_version: str = Field(default=SEAL_SCHEMA_VERSION, min_length=1)
    evaluation_id: str = Field(
        default=EVALUATION_ID, pattern=r"^lc4-holdout-v2-baseline-001$"
    )
    repeat_count: int = Field(default=DEFAULT_REPEAT_COUNT, ge=1)
    state: Literal["consumed"] = "consumed"
    report_hash: str = Field(min_length=1)
    consumed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )


# ---------------------------------------------------------------------------
# Manifest I/O and verification
# ---------------------------------------------------------------------------


def build_manifest(
    group_dir: Path,
    *,
    group_count: int = DEFAULT_GROUP_COUNT,
    variant_count: int = DEFAULT_VARIANT_COUNT,
    multi_turn_count: int = DEFAULT_MULTI_TURN_COUNT,
) -> Manifest:
    """Build a ``Manifest`` from a directory of group JSON files.

    Count parameters default to production values (24/288/72) and are
    injectable for tiny test fixtures.
    """
    json_files = sorted(
        [f for f in group_dir.iterdir() if f.is_file() and f.suffix == ".json"]
    )
    if not json_files:
        raise ValueError(f"no JSON files found in {group_dir}")

    entries: list[ManifestFileEntry] = []
    all_content: list[bytes] = []

    for f in json_files:
        content = f.read_bytes()
        entries.append(
            ManifestFileEntry(
                relative_path=f.name,
                sha256=sha256_digest(content),
            )
        )
        all_content.append(content)

    # Deterministic concatenation order
    all_content.sort(key=lambda x: x)
    combined = b"".join(all_content)
    corpus_hash = sha256_digest(combined)

    return Manifest(
        corpus_version=CORPUS_VERSION,
        files=entries,
        corpus_hash=corpus_hash,
        group_count=group_count,
        variant_count=variant_count,
        multi_turn_count=multi_turn_count,
    )


def verify_manifest(
    manifest: Manifest,
    group_dir: Path,
    *,
    expected_group_count: int = DEFAULT_GROUP_COUNT,
    expected_variant_count: int = DEFAULT_VARIANT_COUNT,
    expected_multi_turn_count: int = DEFAULT_MULTI_TURN_COUNT,
) -> None:
    """Verify *manifest* against the actual files in *group_dir*.

    Raises ``ValueError`` on any mismatch (missing / extra files, absolute or
    traversal paths, duplicate paths or IDs, byte or hash drift, wrong corpus
    version, count drift).
    """
    # --- version ---
    if manifest.corpus_version != CORPUS_VERSION:
        raise ValueError(
            f"corpus_version {manifest.corpus_version!r} != {CORPUS_VERSION!r}"
        )

    # --- counts ---
    if manifest.group_count != expected_group_count:
        raise ValueError(
            f"group_count {manifest.group_count} != expected {expected_group_count}"
        )
    if manifest.variant_count != expected_variant_count:
        raise ValueError(
            f"variant_count {manifest.variant_count} != expected {expected_variant_count}"
        )
    if manifest.multi_turn_count != expected_multi_turn_count:
        raise ValueError(
            f"multi_turn_count {manifest.multi_turn_count} != expected {expected_multi_turn_count}"
        )

    # --- file set ---
    actual_names: set[str] = set()
    for f in group_dir.iterdir():
        if f.is_file() and f.suffix == ".json":
            actual_names.add(f.name)

    manifest_paths = {e.relative_path for e in manifest.files}

    missing = manifest_paths - actual_names
    if missing:
        raise ValueError(f"manifest references missing files: {sorted(missing)}")

    extra = actual_names - manifest_paths
    if extra:
        raise ValueError(f"files not listed in manifest: {sorted(extra)}")

    # --- per-file hash + path safety ---
    resolved_group = group_dir.resolve()
    all_content: list[bytes] = []

    for entry in manifest.files:
        file_path = (group_dir / entry.relative_path).resolve()
        if not str(file_path).startswith(str(resolved_group)):
            raise ValueError(
                f"path traversal detected: {entry.relative_path}"
            )
        if not file_path.is_file():
            raise ValueError(
                f"manifest file not found: {entry.relative_path}"
            )
        content = file_path.read_bytes()
        actual_hash = sha256_digest(content)
        if actual_hash != entry.sha256:
            raise ValueError(
                f"hash mismatch for {entry.relative_path!r}: "
                f"expected {entry.sha256}, got {actual_hash}"
            )
        all_content.append(content)

    # --- corpus hash ---
    all_content.sort(key=lambda x: x)
    computed = sha256_digest(b"".join(all_content))
    if computed != manifest.corpus_hash:
        raise ValueError(
            f"corpus hash mismatch: expected {manifest.corpus_hash}, "
            f"computed {computed}"
        )

    # --- validate every group ---
    seen_ids: set[str] = set()
    total_variants = 0
    total_multi_turn = 0

    for entry in manifest.files:
        file_path = group_dir / entry.relative_path
        raw = json.loads(file_path.read_text(CANONICAL_ENCODING))
        envelope = ScenarioGroupEnvelope.model_validate(raw)

        total_variants += len(envelope.variants)
        for v in envelope.variants:
            if v.scenario_id in seen_ids:
                raise ValueError(
                    f"duplicate scenario_id across groups: {v.scenario_id}"
                )
            seen_ids.add(v.scenario_id)
            if v.dialogue_form in MULTI_TURN_FORMS:
                total_multi_turn += 1

    if total_variants != expected_variant_count:
        raise ValueError(
            f"total variants {total_variants} != expected {expected_variant_count}"
        )
    if total_multi_turn != expected_multi_turn_count:
        raise ValueError(
            f"total multi-turn variants {total_multi_turn} != expected "
            f"{expected_multi_turn_count}"
        )


# ---------------------------------------------------------------------------
# Seal creation
# ---------------------------------------------------------------------------


def create_seal(
    manifest: Manifest,
    source_commit: str,
    *,
    evaluator_version: str = "0.1.0",
    schema_version: str = SEAL_SCHEMA_VERSION,
) -> PreConsumptionSeal:
    """Create a pre-consumption seal from a verified manifest."""
    return PreConsumptionSeal(
        corpus_version=CORPUS_VERSION,
        manifest_hash=manifest.compute_hash(),
        source_commit=source_commit,
        evaluator_version=evaluator_version,
        schema_version=schema_version,
        evaluation_id=EVALUATION_ID,
        repeat_count=DEFAULT_REPEAT_COUNT,
        state="created",
    )


# ---------------------------------------------------------------------------
# Aggregate evaluation (content-blind placeholder)
# ---------------------------------------------------------------------------

# When real v2 content exists, use:
#   from app.services.bernie.composed_corpus_evaluator import (
#       deterministic_interpret,
#       deterministic_replay,
#       score_interpretation_replay_pair,
#   )


def run_aggregate_evaluation(
    manifest: Manifest,
    seal: PreConsumptionSeal,
    group_dir: Path,
    *,
    sample_size: int = SAMPLES_PER_EVALUATION,
    expected_group_count: int = DEFAULT_GROUP_COUNT,
    expected_variant_count: int = DEFAULT_VARIANT_COUNT,
    expected_multi_turn_count: int = DEFAULT_MULTI_TURN_COUNT,
) -> AggregateReport:
    """Run a deterministic aggregate evaluation.

    This is a **content-blind placeholder**.  It validates the manifest and
    returns a zero-failure aggregate report.  When real v2 content exists, Sol
    will replace this with real interpretation, replay, and scoring calls.

    The function never serialises utterances, IDs, expected
    labels/outcomes/tools/deltas, source spans, normalised values,
    observations, case findings, or per-case results.
    """
    verify_manifest(
        manifest,
        group_dir,
        expected_group_count=expected_group_count,
        expected_variant_count=expected_variant_count,
        expected_multi_turn_count=expected_multi_turn_count,
    )

    dims = {
        "interpretation": AggregateDimension(passed=sample_size, failed=0),
        "replay": AggregateDimension(passed=sample_size, failed=0),
        "composed_score": AggregateDimension(passed=sample_size, failed=0),
        "outcome_match": AggregateDimension(passed=sample_size, failed=0),
        "tool_sequence": AggregateDimension(passed=sample_size, failed=0),
        "delta_match": AggregateDimension(passed=sample_size, failed=0),
    }

    report_data: dict[str, Any] = {
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "dimensions": {k: v.model_dump() for k, v in dims.items()},
        "failure_layers": [],
        "safety_pass": sample_size,
        "safety_total": sample_size,
        "variance": 0.0,
        "critical_slices": [
            {"name": "negation", "passed": 24, "failed": 0, "total": 24},
            {"name": "correction", "passed": 24, "failed": 0, "total": 24},
            {"name": "multi_turn", "passed": 72, "failed": 0, "total": 72},
        ],
        "coverage_cells": [
            {"cell": "create", "count": 72},
            {"cell": "move", "count": 72},
            {"cell": "resize", "count": 72},
            {"cell": "cancel", "count": 72},
        ],
        "corpus_hash": manifest.corpus_hash,
    }

    raw = _canonical_json(report_data)
    report_data["report_hash"] = sha256_digest(raw.encode(CANONICAL_ENCODING))

    report = AggregateReport.model_validate(report_data)
    report.check_forbidden_keys()
    return report


# ---------------------------------------------------------------------------
# One-shot consumption
# ---------------------------------------------------------------------------


def consume_report(
    seal: PreConsumptionSeal,
    report: AggregateReport,
    source_commit: str,
) -> ConsumedSeal:
    """Consume a validated aggregate report, producing a one-shot consumed seal.

    Marks *seal.state* as ``"consumed"`` in-place after successful validation.
    Raises ``ValueError`` if the seal is already consumed, the source commit
    does not match, or the report hash is invalid.
    """
    if seal.state == "consumed":
        raise ValueError("seal is already consumed")

    if seal.source_commit != source_commit:
        raise ValueError(
            f"source commit mismatch: seal has {seal.source_commit}, "
            f"got {source_commit}"
        )

    # Re-compute report hash
    report_data = report.model_dump(mode="json", exclude={"report_hash"})
    expected_hash = sha256_digest(
        _canonical_json(report_data).encode(CANONICAL_ENCODING)
    )
    if report.report_hash != expected_hash:
        raise ValueError(
            f"report hash mismatch: expected {expected_hash}, "
            f"got {report.report_hash}"
        )

    # One-way: mark the seal as consumed
    seal.state = "consumed"

    return ConsumedSeal(
        corpus_version=seal.corpus_version,
        manifest_hash=seal.manifest_hash,
        source_commit=seal.source_commit,
        evaluator_version=seal.evaluator_version,
        schema_version=seal.schema_version,
        evaluation_id=seal.evaluation_id,
        repeat_count=seal.repeat_count,
        state="consumed",
        report_hash=report.report_hash,
    )


__all__ = [
    "AGGREGATE_SCHEMA_VERSION",
    "AggregateDimension",
    "AggregateReport",
    "CANONICAL_ENCODING",
    "CORPUS_VERSION",
    "ConsumedSeal",
    "CoverageCell",
    "CriticalSlice",
    "DEFAULT_GROUP_COUNT",
    "DEFAULT_MULTI_TURN_COUNT",
    "DEFAULT_REPEAT_COUNT",
    "DEFAULT_VARIANT_COUNT",
    "EVALUATION_ID",
    "FORBIDDEN_REPORT_KEYS",
    "FailureLayer",
    "JSON_INDENT",
    "Manifest",
    "ManifestFileEntry",
    "MULTI_TURN_FORMS",
    "PreConsumptionSeal",
    "SAMPLES_PER_EVALUATION",
    "SEAL_SCHEMA_VERSION",
    "ScenarioGroupEnvelope",
    "build_manifest",
    "consume_report",
    "create_seal",
    "run_aggregate_evaluation",
    "sha256_digest",
    "verify_manifest",
]
