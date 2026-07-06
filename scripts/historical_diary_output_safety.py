"""Validate committed-safe historical diary aggregate payloads."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SAFE_HISTORICAL_DIARY_OUTPUT_KEYS = {
    "adjacent_neutral_delta_ranges",
    "after_counts",
    "before_counts",
    "char_count",
    "char_count_abs_delta_range",
    "char_count_range",
    "classifier",
    "com_available",
    "comparison",
    "count",
    "date_like_token_count",
    "date_like_token_count_abs_delta_range",
    "date_like_token_count_range",
    "dense_candidate_count",
    "elapsed_seconds",
    "emits_document_text",
    "emits_exact_document_timestamps",
    "emits_filenames",
    "emits_patient_or_staff_labels",
    "emits_raw_paths",
    "error_count",
    "event_class",
    "event_class_distribution",
    "event_model",
    "generated_at_utc",
    "inferred_time_interval_mode_minutes",
    "inferred_time_interval_mode_minutes_distribution",
    "macro_security_forced_disabled",
    "large_delta_triage",
    "max",
    "min",
    "neutral_signature",
    "neutral_signature_distribution",
    "non_empty_line_count",
    "non_empty_line_count_abs_delta_range",
    "non_empty_line_count_range",
    "non_empty_paragraph_count",
    "non_empty_paragraph_count_range",
    "opened_count",
    "opens_documents_read_only",
    "ordered_neutral_snapshots",
    "output_class",
    "output_byte_count",
    "paragraph_count",
    "paragraph_count_abs_delta_range",
    "paragraph_count_range",
    "paragraph_length_range",
    "privacy",
    "requested_sample_size",
    "root_count",
    "root_label",
    "root_match_count",
    "roots",
    "runtime_report",
    "sample_only",
    "sampled_count",
    "sequence_index",
    "summary_comparison",
    "snapshot_count",
    "snapshot_count_delta",
    "structure_class",
    "structure_class_distribution",
    "tab_count_range",
    "table_cell_count",
    "table_cell_count_range",
    "table_count",
    "table_count_range",
    "table_dimension_signature",
    "table_dimension_signature_distribution",
    "time_like_token_count",
    "time_like_token_count_abs_delta_range",
    "time_like_token_count_range",
    "transition_count",
    "transition_count_delta",
    "transition_index",
    "triaged_transition_count",
    "total_error_count",
    "total_opened_count",
    "total_sampled_count",
    "unique_time_like_token_count",
    "unique_time_like_token_count_range",
    "value",
    "version",
    "word",
}

UNSAFE_KEY_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"file(?:name)?",
        r"path",
        r"document_?text",
        r"raw_?text",
        r"metadata",
        r"last_?write",
        r"modified",
        r"created",
        r"patient",
        r"staff",
        r"provider",
        r"doctor",
        r"appointment_?text",
    )
)

WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\")
DOC_PATH_RE = re.compile(r"(?:\\|/)[^\\/\s]+\.docx?\b", re.IGNORECASE)
DATE_TIME_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}")
LIKELY_PERSON_NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b")


@dataclass(frozen=True)
class SafetyIssue:
    path: str
    reason: str


class HistoricalDiaryOutputSafetyError(ValueError):
    def __init__(self, issues: list[SafetyIssue]) -> None:
        self.issues = issues
        detail = "; ".join(f"{issue.path}: {issue.reason}" for issue in issues)
        super().__init__(detail)


def validate_historical_diary_output(payload: Any) -> None:
    issues: list[SafetyIssue] = []
    _validate_node(payload, "$", issues)
    if issues:
        raise HistoricalDiaryOutputSafetyError(issues)


def _validate_node(node: Any, path: str, issues: list[SafetyIssue]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_path = f"{path}.{key}"
            _validate_key(key, key_path, issues)
            _validate_node(value, key_path, issues)
        return

    if isinstance(node, list):
        for index, value in enumerate(node):
            _validate_node(value, f"{path}[{index}]", issues)
        return

    if isinstance(node, str):
        _validate_string(node, path, issues)


def _validate_key(key: str, path: str, issues: list[SafetyIssue]) -> None:
    if key not in SAFE_HISTORICAL_DIARY_OUTPUT_KEYS:
        issues.append(SafetyIssue(path, "key is not in the committed-output allowlist"))
    for pattern in UNSAFE_KEY_PATTERNS:
        if pattern.search(key) and key not in {
            "emits_document_text",
            "emits_exact_document_timestamps",
            "emits_filenames",
            "emits_patient_or_staff_labels",
            "emits_raw_paths",
        }:
            issues.append(SafetyIssue(path, "key name suggests PHI, raw text, paths, or document metadata"))


def _validate_string(value: str, path: str, issues: list[SafetyIssue]) -> None:
    if "\n" in value or "\r" in value:
        issues.append(SafetyIssue(path, "string contains line breaks"))
    if len(value) > 160:
        issues.append(SafetyIssue(path, "string is too long for an aggregate classifier value"))
    if WINDOWS_PATH_RE.search(value) or DOC_PATH_RE.search(value):
        issues.append(SafetyIssue(path, "string looks like a raw file path"))
    if DATE_TIME_RE.search(value) and not path.endswith(".generated_at_utc"):
        issues.append(SafetyIssue(path, "string looks like an exact document timestamp"))
    if LIKELY_PERSON_NAME_RE.search(value):
        issues.append(SafetyIssue(path, "string looks like a person or staff label"))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", nargs="+", type=Path)
    args = parser.parse_args()

    for json_file in args.json_file:
        validate_historical_diary_output(load_json(json_file))
        print(f"safe: {json_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
