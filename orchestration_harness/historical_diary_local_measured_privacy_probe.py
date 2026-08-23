"""Fail-closed local measurement for one bounded historical Diary slice.

Raw names, paths, timestamps and Word cell text are admitted only in local
memory or the ignored binding manifest.  Public stdout and repository-eligible
evidence contain aggregate counts and closed vocabularies only.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUND_ROOT = REPO_ROOT / "local_data/historical-diary-trove/raw/pilot_01"
ATTEMPT_ROOT = (
    REPO_ROOT
    / "local_data/historical-diary-trove/measured-probes/2026-08-24-boundary-v1"
)
MANIFEST_PATH = ATTEMPT_ROOT / "private-binding-manifest.json"
PRIVATE_PROJECTION_PATH = ATTEMPT_ROOT / "private-derived-projection.json"
AGGREGATE_PATH = ATTEMPT_ROOT / "aggregate-reading.json"
CLEANUP_PATH = ATTEMPT_ROOT / "cleanup-receipt.json"
EXTRACTOR_PATH = REPO_ROOT / "scripts/historical_diary_local_measured_privacy_probe.ps1"
CORE_PATH = Path(__file__).resolve()

MAX_FILES = 80
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MIN_FILE_BYTES = 4096
MAX_PRIVATE_PIPE_BYTES = 64 * 1024 * 1024
POLL_INTERVAL_SECONDS = 30
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

TIME_TOKEN = re.compile(
    r"^(?P<hour>[01]?\d|2[0-3])[:.](?P<minute>[0-5]\d)(?:\s*(?P<ampm>[AaPp][Mm]))?$"
)
DATE_TOKEN = re.compile(r"^\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?$")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?61[\s().-]*|0)[2-478](?:[\s().-]*\d){8}(?!\d)")
MEDICARE = re.compile(r"(?<!\d)\d{4}[\s-]?\d{5}[\s-]?\d(?!\d)")
ADDRESS = re.compile(
    r"\b\d{1,5}\s+[A-Za-z][A-Za-z .'-]{2,}\s+"
    r"(?:street|st|road|rd|avenue|ave|drive|dr|court|ct|lane|ln|place|pl)\b",
    re.IGNORECASE,
)
LIKELY_NAME = re.compile(r"\b[A-Z][a-z]{2,}[ '\-][A-Z][A-Za-z'\-]{2,}\b")
SENSITIVE_NOTE = re.compile(
    r"\b(?:diagnos|cancer|pregnan|mental|suicid|hiv|hepat|biopsy|"
    r"pathology|radiology|urgent|medication|prescription)\w*\b",
    re.IGNORECASE,
)


class ProbeError(ValueError):
    """Closed failure carrying no source-derived value."""


class StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Decision(str, Enum):
    BLOCKED = "blocked"
    REVISION_REQUIRED = "revision_required"
    LOCALLY_RESTRICTED_CANDIDATE = "locally_restricted_candidate"


class PrivateCell(StrictFrozenModel):
    table_index: int = Field(ge=1, le=128)
    row_index: int = Field(ge=1, le=4096)
    column_index: int = Field(ge=1, le=512)
    text: str = Field(max_length=65536)
    shading: int = Field(ge=-1, le=16_777_215)
    font_color: int = Field(ge=-1, le=16_777_215)
    bold: bool
    italic: bool


class PrivateSnapshot(StrictFrozenModel):
    sequence_index: int = Field(ge=0, lt=MAX_FILES)
    observation_offset_seconds: int = Field(ge=0, le=172800)
    cells: tuple[PrivateCell, ...]
    error_code: Literal["document_open_failed", "document_structure_failed"] | None


class PrivateExtraction(StrictFrozenModel):
    schema_version: Literal["historical_diary.private_word_cell_extraction.v1"]
    status: Literal["passed", "revision_required"]
    reason_code: Literal[
        "passed",
        "word_automation_unavailable",
        "word_process_isolation_unavailable",
        "macro_security_unavailable",
        "private_text_limit_exceeded",
        "manifest_invalid",
        "document_errors_present",
    ]
    word_invisible: bool
    alerts_disabled: bool
    macro_security_forced_disabled: bool
    link_updates_disabled: bool
    documents_opened_read_only: bool
    word_cleanup_completed: bool
    snapshots: tuple[PrivateSnapshot, ...]

    @model_validator(mode="after")
    def validate_sequence(self) -> "PrivateExtraction":
        indexes = [item.sequence_index for item in self.snapshots]
        if indexes != list(range(len(indexes))):
            raise ValueError("snapshot_sequence_invalid")
        offsets = [item.observation_offset_seconds for item in self.snapshots]
        if offsets != sorted(offsets) or len(offsets) != len(set(offsets)):
            raise ValueError("snapshot_offsets_invalid")
        return self


class BoundFile(StrictFrozenModel):
    sequence_index: int = Field(ge=0, lt=MAX_FILES)
    absolute_path: str = Field(min_length=1, max_length=1000)
    observation_timestamp: str = Field(min_length=19, max_length=32)
    observation_offset_seconds: int = Field(ge=0, le=172800)
    size_bytes: int = Field(ge=MIN_FILE_BYTES + 1, le=MAX_FILE_BYTES)
    modified_time_ns: int = Field(ge=1)


class BindingManifest(StrictFrozenModel):
    schema_version: Literal["historical_diary.private_binding_manifest.v1"]
    root: str
    attempt_root: str
    selected_source_day: str
    selector: Literal["densest_filename_timestamp_day_first_80_chronological"]
    core_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    extractor_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    total_bytes: int = Field(ge=1, le=MAX_TOTAL_BYTES)
    files: tuple[BoundFile, ...] = Field(min_length=2, max_length=MAX_FILES)


class ProjectedCell(StrictFrozenModel):
    cell_token: str = Field(pattern=r"^cell_[0-9a-f]{32}$")
    content_token: str = Field(pattern=r"^content_[0-9a-f]{32}$")
    sequence_index: int = Field(ge=0, lt=MAX_FILES)
    observation_interval_start_seconds: int = Field(ge=0)
    observation_interval_end_seconds: int = Field(gt=0)
    table_index: int = Field(ge=1)
    row_index: int = Field(ge=1)
    column_index: int = Field(ge=1)
    resource_ordinal: str = Field(pattern=r"^resource_[0-9]+_[0-9]+$")
    time_minute: int | None = Field(default=None, ge=0, le=1439)
    format_bucket: str = Field(pattern=r"^format_[0-9]+$")
    length_bucket: Literal["short", "medium", "long", "very_long"]
    content_bucket: Literal["structural_text", "identifier_like", "sensitive_note_like"]
    detector_categories: tuple[
        Literal["address", "email", "likely_name", "medicare", "phone", "sensitive_note"],
        ...,
    ]


class ProjectedSnapshot(StrictFrozenModel):
    sequence_index: int
    observation_interval_start_seconds: int
    observation_interval_end_seconds: int
    cells: tuple[ProjectedCell, ...]


class PrivateProjection(StrictFrozenModel):
    schema_version: Literal["historical_diary.private_derived_grid_projection.v1"]
    evidence_label: Literal["private_derived_ignored_local_only"]
    source_day_policy: Literal["relative_day_zero_only"]
    source_filename_or_path_emitted: Literal[False]
    exact_source_timestamp_emitted: Literal[False]
    key_or_mapping_emitted: Literal[False]
    snapshots: tuple[ProjectedSnapshot, ...]


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_reparse(path: Path) -> bool:
    stat = path.lstat()
    return path.is_symlink() or bool(
        getattr(stat, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT
    )


def _parse_datetime_digits(value: str) -> datetime | None:
    candidates: set[datetime] = set()
    numeric_tokens = re.findall(r"\d+", value)
    for length, parsers in (
        (
            14,
            (
                lambda part: (part[0:4], part[4:6], part[6:8], part[8:10], part[10:12], part[12:14]),
                lambda part: (part[4:8], part[2:4], part[0:2], part[8:10], part[10:12], part[12:14]),
            ),
        ),
    ):
        for part in (token for token in numeric_tokens if len(token) == length):
            for parser in parsers:
                try:
                    year, month, day, hour, minute, second = map(int, parser(part))
                    candidate = datetime(year, month, day, hour, minute, second)
                except ValueError:
                    continue
                if 2000 <= candidate.year <= 2035:
                    candidates.add(candidate)
    if len(candidates) != 1:
        return None
    return next(iter(candidates))


def parse_observation_timestamp(filename: str) -> datetime | None:
    """Parse a closed numeric timestamp family without ever returning a name."""

    if not filename or len(filename) > 260 or "\x00" in filename:
        return None
    return _parse_datetime_digits(Path(filename).stem)


def filename_shape(filename: str) -> str:
    """Return a coarse non-identifying shape for aggregate diagnostics."""

    stem = Path(filename).stem
    classes: list[str] = []
    for character in stem:
        value = "d" if character.isdigit() else "a" if character.isalpha() else "s"
        if not classes or classes[-1] != value:
            classes.append(value)
    return "".join(classes)[:24] or "empty"


def _safe_public_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_binding_manifest() -> tuple[BindingManifest, dict[str, Any]]:
    root = BOUND_ROOT.resolve(strict=True)
    expected = BOUND_ROOT.resolve()
    ignored = (REPO_ROOT / "local_data/historical-diary-trove").resolve()
    if root != expected or not root.is_relative_to(ignored) or _is_reparse(BOUND_ROOT):
        raise ProbeError("root_boundary_invalid")
    if ATTEMPT_ROOT.exists():
        raise ProbeError("attempt_root_already_exists")

    parsed: list[tuple[Path, os.stat_result, datetime]] = []
    shapes: Counter[str] = Counter()
    admitted_file_count = 0
    below_minimum_file_count = 0
    above_maximum_file_count = 0
    timestamp_parse_failures = 0
    for path in root.iterdir():
        shapes[filename_shape(path.name)] += 1
        if _is_reparse(path):
            raise ProbeError("selected_reparse_forbidden")
        if not path.is_file() or path.suffix.lower() != ".doc":
            continue
        stat = path.stat()
        if stat.st_size <= MIN_FILE_BYTES:
            below_minimum_file_count += 1
            continue
        if stat.st_size > MAX_FILE_BYTES:
            above_maximum_file_count += 1
            continue
        admitted_file_count += 1
        timestamp = parse_observation_timestamp(path.name)
        if timestamp is None:
            timestamp_parse_failures += 1
            continue
        parsed.append((path.resolve(), stat, timestamp))

    if admitted_file_count == 0:
        raise ProbeError("no_candidate_documents")
    if timestamp_parse_failures or len(parsed) != admitted_file_count:
        diagnostic = {
            "schema_version": "historical_diary.safe_binding_diagnostic.v1",
            "status": Decision.REVISION_REQUIRED.value,
            "candidate_document_count": admitted_file_count,
            "below_minimum_file_count": below_minimum_file_count,
            "above_maximum_file_count": above_maximum_file_count,
            "timestamp_parse_success_count": len(parsed),
            "timestamp_parse_failure_count": timestamp_parse_failures,
            "filename_shape_distribution": dict(sorted(shapes.items())),
            "archive_content_reads": 0,
        }
        raise ProbeError("timestamp_binding_revision_required:" + json.dumps(diagnostic, sort_keys=True))

    per_day: defaultdict[str, list[tuple[Path, os.stat_result, datetime]]] = defaultdict(list)
    for item in parsed:
        per_day[item[2].date().isoformat()].append(item)
    selected_day = sorted(per_day, key=lambda day: (-len(per_day[day]), day))[0]
    selected = sorted(per_day[selected_day], key=lambda item: (item[2], item[0].name))[:MAX_FILES]
    if len(selected) != MAX_FILES:
        raise ProbeError("insufficient_dense_day_observations")
    timestamps = [item[2] for item in selected]
    if len(timestamps) != len(set(timestamps)):
        raise ProbeError("duplicate_observation_timestamp")
    total_bytes = sum(item[1].st_size for item in selected)
    if total_bytes > MAX_TOTAL_BYTES:
        raise ProbeError("total_byte_cap_exceeded")

    first = timestamps[0]
    files = tuple(
        BoundFile(
            sequence_index=index,
            absolute_path=str(path),
            observation_timestamp=timestamp.isoformat(),
            observation_offset_seconds=int((timestamp - first).total_seconds()),
            size_bytes=stat.st_size,
            modified_time_ns=stat.st_mtime_ns,
        )
        for index, (path, stat, timestamp) in enumerate(selected)
    )
    manifest = BindingManifest(
        schema_version="historical_diary.private_binding_manifest.v1",
        root=str(root),
        attempt_root=str(ATTEMPT_ROOT.resolve()),
        selected_source_day=selected_day,
        selector="densest_filename_timestamp_day_first_80_chronological",
        core_sha256=_sha256_path(CORE_PATH),
        extractor_sha256=_sha256_path(EXTRACTOR_PATH),
        total_bytes=total_bytes,
        files=files,
    )
    public = {
        "schema_version": "historical_diary.safe_binding_reading.v1",
        "status": "passed",
        "root_count": 1,
        "dense_day_count": 1,
        "candidate_document_count": admitted_file_count,
        "below_minimum_file_count": below_minimum_file_count,
        "above_maximum_file_count": above_maximum_file_count,
        "timestamp_parse_success_count": len(parsed),
        "timestamp_parse_failure_count": 0,
        "selected_file_count": len(files),
        "selected_total_bytes": total_bytes,
        "maximum_file_bytes": max(item.size_bytes for item in files),
        "relative_observation_span_seconds": files[-1].observation_offset_seconds,
        "filename_shape_class_count": len(shapes),
        "archive_content_reads": 0,
        "raw_filename_path_or_timestamp_emitted": False,
    }
    return manifest, public


def bind() -> dict[str, Any]:
    manifest, public = build_binding_manifest()
    ATTEMPT_ROOT.mkdir(parents=True, exist_ok=False)
    _safe_public_write(MANIFEST_PATH, manifest.model_dump(mode="json"))
    _safe_public_write(ATTEMPT_ROOT / "safe-binding-reading.json", public)
    return public


def _load_manifest() -> BindingManifest:
    try:
        manifest = BindingManifest.model_validate_json(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ProbeError("binding_manifest_invalid") from error
    if (
        Path(manifest.root) != BOUND_ROOT.resolve()
        or Path(manifest.attempt_root) != ATTEMPT_ROOT.resolve()
        or manifest.core_sha256 != _sha256_path(CORE_PATH)
        or manifest.extractor_sha256 != _sha256_path(EXTRACTOR_PATH)
        or len(manifest.files) != MAX_FILES
    ):
        raise ProbeError("binding_parser_or_path_drift")
    total = 0
    for expected_index, item in enumerate(manifest.files):
        path = Path(item.absolute_path)
        if item.sequence_index != expected_index or path.parent != BOUND_ROOT.resolve():
            raise ProbeError("binding_manifest_scope_invalid")
        if _is_reparse(path):
            raise ProbeError("binding_reparse_drift")
        if not path.is_file() or path.suffix.lower() != ".doc":
            raise ProbeError("binding_file_type_drift")
        stat = path.stat()
        if stat.st_size != item.size_bytes or stat.st_mtime_ns != item.modified_time_ns:
            raise ProbeError("binding_file_metadata_drift")
        total += stat.st_size
    if total != manifest.total_bytes or total > MAX_TOTAL_BYTES:
        raise ProbeError("binding_total_byte_drift")
    timestamps = [datetime.fromisoformat(item.observation_timestamp) for item in manifest.files]
    if (
        any(value.date().isoformat() != manifest.selected_source_day for value in timestamps)
        or timestamps != sorted(timestamps)
        or len(timestamps) != len(set(timestamps))
    ):
        raise ProbeError("binding_timestamp_drift")
    first = timestamps[0]
    if any(
        item.observation_offset_seconds != int((timestamp - first).total_seconds())
        for item, timestamp in zip(manifest.files, timestamps, strict=True)
    ):
        raise ProbeError("binding_offset_drift")
    return manifest


def _clean_cell_text(value: str) -> str:
    return value.replace("\r\x07", "").replace("\x07", "").strip()


def _time_minute(value: str) -> int | None:
    match = TIME_TOKEN.fullmatch(value.strip())
    if match is None:
        return None
    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    ampm = (match.group("ampm") or "").lower()
    if ampm == "pm" and hour < 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return hour * 60 + minute


def _detectors(value: str) -> tuple[str, ...]:
    found: list[str] = []
    for label, pattern in (
        ("address", ADDRESS),
        ("email", EMAIL),
        ("likely_name", LIKELY_NAME),
        ("medicare", MEDICARE),
        ("phone", PHONE),
        ("sensitive_note", SENSITIVE_NOTE),
    ):
        if pattern.search(value):
            found.append(label)
    return tuple(found)


def _length_bucket(value: str) -> str:
    length = len(value)
    if length <= 24:
        return "short"
    if length <= 80:
        return "medium"
    if length <= 240:
        return "long"
    return "very_long"


def _token(prefix: str, domain: str, value: str, key: bytes) -> str:
    digest = hmac.new(key, f"historical-diary:{domain}:{value}".encode(), hashlib.sha256)
    return f"{prefix}_{digest.hexdigest()[:32]}"


def _ratio(successes: int, trials: int) -> dict[str, int | float | None]:
    if trials < 0 or successes < 0 or successes > trials:
        raise ProbeError("risk_denominator_invalid")
    return {
        "successes": successes,
        "trials": trials,
        "rate": None if trials == 0 else successes / trials,
    }


def project_and_measure(extraction: PrivateExtraction) -> tuple[PrivateProjection, dict[str, Any]]:
    if (
        extraction.status != "passed"
        or not extraction.word_invisible
        or not extraction.alerts_disabled
        or not extraction.macro_security_forced_disabled
        or not extraction.link_updates_disabled
        or not extraction.documents_opened_read_only
        or not extraction.word_cleanup_completed
    ):
        raise ProbeError("word_extraction_boundary_failed")
    if len(extraction.snapshots) < 2 or len(extraction.snapshots) > MAX_FILES:
        raise ProbeError("snapshot_count_invalid")
    if any(snapshot.error_code is not None for snapshot in extraction.snapshots):
        raise ProbeError("snapshot_parse_error")

    key = secrets.token_bytes(32)
    second_key = secrets.token_bytes(32)
    detector_counts: Counter[str] = Counter()
    source_occupancy_values: set[str] = set()
    format_values = sorted(
        {
            (cell.shading, cell.font_color, cell.bold, cell.italic)
            for snapshot in extraction.snapshots
            for cell in snapshot.cells
        }
    )
    formats = {value: f"format_{index}" for index, value in enumerate(format_values)}
    projected_snapshots: list[ProjectedSnapshot] = []
    token_sequences: defaultdict[str, list[tuple[int, str, int | None, str]]] = defaultdict(list)
    second_token_sequences: defaultdict[str, list[tuple[int, str, int | None, str]]] = defaultdict(list)
    source_cell_count = 0
    mapped_time_count = 0

    for snapshot in extraction.snapshots:
        row_times: dict[tuple[int, int], int] = {}
        cleaned: list[tuple[PrivateCell, str]] = []
        for cell in snapshot.cells:
            text = _clean_cell_text(cell.text)
            if not text:
                continue
            cleaned.append((cell, text))
            minute = _time_minute(text)
            if minute is not None:
                row_times[(cell.table_index, cell.row_index)] = minute

        occurrences: Counter[str] = Counter()
        projected_cells: list[ProjectedCell] = []
        for cell, text in cleaned:
            if _time_minute(text) is not None or DATE_TOKEN.fullmatch(text):
                continue
            source_cell_count += 1
            normalized = " ".join(text.casefold().split())
            if not normalized:
                continue
            source_occupancy_values.add(normalized)
            categories = _detectors(text)
            detector_counts.update(categories)
            occurrence = occurrences[normalized]
            occurrences[normalized] += 1
            content_token = _token("content", "content", normalized, key)
            cell_token = _token("cell", "cell", f"{normalized}|{occurrence}", key)
            second_cell_token = _token(
                "cell", "cell", f"{normalized}|{occurrence}", second_key
            )
            resource = f"resource_{cell.table_index}_{cell.column_index}"
            minute = row_times.get((cell.table_index, cell.row_index))
            if minute is not None:
                mapped_time_count += 1
            format_bucket = formats[(cell.shading, cell.font_color, cell.bold, cell.italic)]
            content_bucket = (
                "sensitive_note_like"
                if "sensitive_note" in categories
                else "identifier_like"
                if categories
                else "structural_text"
            )
            projected = ProjectedCell(
                cell_token=cell_token,
                content_token=content_token,
                sequence_index=snapshot.sequence_index,
                observation_interval_start_seconds=(
                    snapshot.observation_offset_seconds // POLL_INTERVAL_SECONDS
                )
                * POLL_INTERVAL_SECONDS,
                observation_interval_end_seconds=(
                    snapshot.observation_offset_seconds // POLL_INTERVAL_SECONDS + 1
                )
                * POLL_INTERVAL_SECONDS,
                table_index=cell.table_index,
                row_index=cell.row_index,
                column_index=cell.column_index,
                resource_ordinal=resource,
                time_minute=minute,
                format_bucket=format_bucket,
                length_bucket=_length_bucket(text),
                content_bucket=content_bucket,
                detector_categories=categories,
            )
            projected_cells.append(projected)
            signature = (snapshot.sequence_index, resource, minute, format_bucket)
            token_sequences[cell_token].append(signature)
            second_token_sequences[second_cell_token].append(signature)
        projected_snapshots.append(
            ProjectedSnapshot(
                sequence_index=snapshot.sequence_index,
                observation_interval_start_seconds=(
                    snapshot.observation_offset_seconds // POLL_INTERVAL_SECONDS
                )
                * POLL_INTERVAL_SECONDS,
                observation_interval_end_seconds=(
                    snapshot.observation_offset_seconds // POLL_INTERVAL_SECONDS + 1
                )
                * POLL_INTERVAL_SECONDS,
                cells=tuple(projected_cells),
            )
        )

    projection = PrivateProjection(
        schema_version="historical_diary.private_derived_grid_projection.v1",
        evidence_label="private_derived_ignored_local_only",
        source_day_policy="relative_day_zero_only",
        source_filename_or_path_emitted=False,
        exact_source_timestamp_emitted=False,
        key_or_mapping_emitted=False,
        snapshots=tuple(projected_snapshots),
    )

    changes: Counter[str] = Counter()
    for previous, current in zip(projection.snapshots, projection.snapshots[1:]):
        previous_by_token = {cell.cell_token: cell for cell in previous.cells}
        current_by_token = {cell.cell_token: cell for cell in current.cells}
        previous_positions = {
            (cell.table_index, cell.row_index, cell.column_index): cell for cell in previous.cells
        }
        current_positions = {
            (cell.table_index, cell.row_index, cell.column_index): cell for cell in current.cells
        }
        changes["added"] += len(current_by_token.keys() - previous_by_token.keys())
        changes["removed"] += len(previous_by_token.keys() - current_by_token.keys())
        for token in previous_by_token.keys() & current_by_token.keys():
            before = previous_by_token[token]
            after = current_by_token[token]
            if (before.table_index, before.row_index, before.column_index) != (
                after.table_index,
                after.row_index,
                after.column_index,
            ):
                changes["moved"] += 1
            if before.format_bucket != after.format_bucket:
                changes["format_changed"] += 1
        for position in previous_positions.keys() & current_positions.keys():
            if previous_positions[position].content_token != current_positions[position].content_token:
                changes["same_position_replaced"] += 1

    representatives: dict[str, ProjectedCell] = {}
    for snapshot in projection.snapshots:
        for cell in snapshot.cells:
            representatives.setdefault(cell.cell_token, cell)
    equivalence: Counter[tuple[Any, ...]] = Counter(
        (
            cell.resource_ordinal,
            cell.time_minute,
            cell.format_bucket,
            cell.length_bucket,
            cell.content_bucket,
        )
        for cell in representatives.values()
    )
    record_unique = sum(equivalence[
        (
            cell.resource_ordinal,
            cell.time_minute,
            cell.format_bucket,
            cell.length_bucket,
            cell.content_bucket,
        )
    ] == 1 for cell in representatives.values())
    trajectories = Counter(tuple(values) for values in token_sequences.values())
    trajectory_unique = sum(trajectories[tuple(values)] == 1 for values in token_sequences.values())
    rare_trajectories = sum(trajectories[tuple(values)] < 2 for values in token_sequences.values())
    second_trajectories = Counter(tuple(values) for values in second_token_sequences.values())
    cross_key_unique = sum(
        second_trajectories[tuple(values)] == 1 for values in second_token_sequences.values()
    )
    stable_linkage = sum(len(values) > 1 for values in token_sequences.values())
    total_changes = sum(changes.values())
    output_text = projection.model_dump_json()
    source_leakage = sum(
        1
        for value in source_occupancy_values
        if len(value) >= 5 and any(character.isalpha() for character in value) and value in output_text.casefold()
    )
    record_trials = len(representatives)
    trajectory_trials = len(token_sequences)
    mapped_ratio = 0 if source_cell_count == 0 else mapped_time_count / source_cell_count

    if source_leakage:
        decision = Decision.BLOCKED
        reasons = ["source_value_detected_in_projection"]
    elif not representatives or stable_linkage == 0 or total_changes == 0 or mapped_ratio < 0.25:
        decision = Decision.REVISION_REQUIRED
        reasons = [
            reason
            for condition, reason in (
                (not representatives, "no_structural_occupancy_records"),
                (stable_linkage == 0, "no_stable_linkage"),
                (total_changes == 0, "no_adjacent_changes"),
                (mapped_ratio < 0.25, "insufficient_time_mapping"),
            )
            if condition
        ]
    else:
        decision = Decision.LOCALLY_RESTRICTED_CANDIDATE
        reasons = []

    aggregate = {
        "schema_version": "historical_diary.measured_privacy_reading.v1",
        "evidence_label": "private_derived_aggregate_non_phi",
        "decision": decision.value,
        "reason_codes": reasons,
        "scope": {
            "root_count": 1,
            "dense_day_count": 1,
            "snapshot_count": len(projection.snapshots),
            "opened_snapshot_count": len(extraction.snapshots),
            "parsed_snapshot_count": len(projection.snapshots),
            "rejected_snapshot_count": 0,
            "source_day_policy": "relative_day_zero_only",
        },
        "privacy": {
            "source_filename_path_or_timestamp_emitted": False,
            "source_text_emitted": False,
            "key_or_mapping_emitted": False,
            "source_value_leakage_count": source_leakage,
            "detector_category_counts": dict(sorted(detector_counts.items())),
        },
        "utility": {
            "source_cell_observations": source_cell_count,
            "projected_cell_observations": sum(len(item.cells) for item in projection.snapshots),
            "distinct_structural_records": record_trials,
            "mapped_time_observations": mapped_time_count,
            "stable_linkage_records": stable_linkage,
            "adjacent_transition_count": len(projection.snapshots) - 1,
            "change_counts": dict(sorted(changes.items())),
            "total_changes": total_changes,
        },
        "risk": {
            "equivalence_class_sizes": sorted(equivalence.values()),
            "record_uniqueness": _ratio(record_unique, record_trials),
            "trajectory_uniqueness": _ratio(trajectory_unique, trajectory_trials),
            "rare_trajectories": _ratio(rare_trajectories, trajectory_trials),
            "record_linkage_attack": _ratio(record_unique, record_trials),
            "trajectory_linkage_attack": _ratio(trajectory_unique, trajectory_trials),
            "cross_key_structural_differencing": _ratio(cross_key_unique, trajectory_trials),
            "universal_reidentification_probability_claimed": False,
        },
        "authority": {
            "strongest_meaning": "ignored_local_research_retention_only_no_downstream_authority",
            "fixture_provider_model_memory_product_or_publication_allowed": False,
        },
    }
    return projection, aggregate


def _cleanup_private_outputs(*, retained: bool, decision: str, word_cleanup: bool) -> dict[str, Any]:
    removed: list[str] = []
    if not retained:
        for path, label in (
            (PRIVATE_PROJECTION_PATH, "private_projection"),
            (MANIFEST_PATH, "private_manifest"),
        ):
            if path.exists():
                path.unlink()
                removed.append(label)
    receipt = {
        "schema_version": "historical_diary.local_cleanup_receipt.v1",
        "decision": decision,
        "private_projection_retained": retained,
        "ephemeral_key_persisted": False,
        "mapping_persisted": False,
        "word_cleanup_completed": word_cleanup,
        "removed_private_artifact_classes": removed,
        "provider_network_model_calls": 0,
    }
    _safe_public_write(CLEANUP_PATH, receipt)
    return receipt


def execute() -> dict[str, Any]:
    manifest = _load_manifest()
    command = [
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(EXTRACTOR_PATH),
        "-Manifest",
        str(MANIFEST_PATH),
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        timeout=900,
    )
    if len(completed.stdout) > MAX_PRIVATE_PIPE_BYTES:
        raise ProbeError("private_pipe_byte_cap_exceeded")
    if completed.returncode != 0:
        raise ProbeError("word_extractor_failed")
    try:
        extraction = PrivateExtraction.model_validate_json(completed.stdout)
    except ValueError as error:
        raise ProbeError("private_extraction_invalid") from error
    if len(extraction.snapshots) != len(manifest.files):
        raise ProbeError("extraction_manifest_count_mismatch")

    projection, aggregate = project_and_measure(extraction)
    _safe_public_write(AGGREGATE_PATH, aggregate)
    retained = aggregate["decision"] == Decision.LOCALLY_RESTRICTED_CANDIDATE.value
    if retained:
        _safe_public_write(PRIVATE_PROJECTION_PATH, projection.model_dump(mode="json"))
    cleanup = _cleanup_private_outputs(
        retained=retained,
        decision=aggregate["decision"],
        word_cleanup=extraction.word_cleanup_completed,
    )
    return {
        **aggregate,
        "cleanup": cleanup,
        "private_output_location_emitted": False,
    }


def _failure(code: str, *, phase: str) -> dict[str, Any]:
    decision = (
        Decision.REVISION_REQUIRED.value
        if code in {
            "timestamp_binding_revision_required",
            "insufficient_dense_day_observations",
            "word_extractor_failed",
            "private_extraction_invalid",
            "word_extraction_boundary_failed",
            "snapshot_parse_error",
        }
        else Decision.BLOCKED.value
    )
    public = {
        "schema_version": "historical_diary.measured_privacy_failure.v1",
        "phase": phase,
        "decision": decision,
        "reason_code": code,
        "source_value_emitted": False,
        "archive_content_retry_authorized": False,
    }
    if ATTEMPT_ROOT.exists():
        _safe_public_write(AGGREGATE_PATH, public)
        public["cleanup"] = _cleanup_private_outputs(
            retained=False, decision=decision, word_cleanup=False
        )
    return public


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument("--bind", action="store_true")
    phase.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    phase_name = "bind" if arguments.bind else "execute"
    try:
        result = bind() if arguments.bind else execute()
    except ProbeError as error:
        raw_code = str(error)
        if raw_code.startswith("timestamp_binding_revision_required:"):
            diagnostic = json.loads(raw_code.partition(":")[2])
            print(json.dumps(diagnostic, indent=2, sort_keys=True))
            return 2
        result = _failure(raw_code, phase=phase_name)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    except (OSError, subprocess.SubprocessError, ValueError):
        result = _failure("internal_local_probe_failure", phase=phase_name)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
