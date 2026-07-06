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
    "center_transition",
    "center_transition_index",
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
    "edge_count",
    "edge_id",
    "edge_kind",
    "edges",
    "error_count",
    "event_class",
    "event_class_distribution",
    "event_model",
    "generated_at_utc",
    "graph",
    "inferred_time_interval_mode_minutes",
    "inferred_time_interval_mode_minutes_distribution",
    "macro_security_forced_disabled",
    "large_delta_triage",
    "max",
    "min",
    "neutral_signature",
    "neutral_signature_distribution",
    "node_count",
    "node_id",
    "node_kind",
    "nodes",
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
    "queries",
    "query_id",
    "relative_offset",
    "requested_sample_size",
    "root_count",
    "root_label",
    "root_match_count",
    "roots",
    "result_count",
    "runtime_report",
    "sample_only",
    "sampled_count",
    "sequence_index",
    "source_node_id",
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
    "target_node_id",
    "time_like_token_count",
    "time_like_token_count_abs_delta_range",
    "time_like_token_count_range",
    "transition_count",
    "transition_count_delta",
    "transition_index",
    "transition_neighborhoods",
    "triaged_transition_count",
    "neighborhood_count",
    "neighbor_transitions",
    "total_error_count",
    "total_opened_count",
    "total_sampled_count",
    "unique_time_like_token_count",
    "unique_time_like_token_count_range",
    "value",
    "version",
    "word",
}

SAFE_HISTORICAL_DIARY_SEMANTIC_OUTPUT_KEYS = SAFE_HISTORICAL_DIARY_OUTPUT_KEYS | {
    "action_name",
    "allowed_action_names",
    "approval_expires_on",
    "bucket_flags",
    "confidence_label",
    "date_policy",
    "date_shift_days",
    "date_shifted_day_index",
    "expires_on",
    "fixture_family",
    "fixtures",
    "local_raw_processing_only",
    "raw_data_external_provider_allowed",
    "relative_day_index",
    "schema_version",
    "semantic_fixture",
    "semantic_scope",
    "source",
    "synthetic_event_id",
    "synthetic_resource_id",
    "time_of_day",
    "duration_minutes",
    "status_categories",
    "transition_label",
}

SEMANTIC_FIXTURE_SCHEMA_VERSION = "historical_diary.semantic_fixture.v1"
SEMANTIC_FIXTURE_SOURCE = "approved_h15_review_payload"
ALLOWED_SEMANTIC_ACTION_NAMES = {
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "check_in",
    "waiting_area_move",
    "link_patient",
    "slot_search",
    "explain_schedule",
    "handoff",
}
ALLOWED_SEMANTIC_DATE_POLICIES = {
    "relative_day_index_only",
    "date_shifted",
}
ALLOWED_CONFIDENCE_LABELS = {
    "high",
    "medium",
    "low",
    "unknown",
}
ALLOWED_STATUS_CATEGORIES = {
    "candidate",
    "confirmed",
    "cancelled",
    "status_changed",
    "unknown",
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
LIKELY_BOOKING_SEMANTIC_RE = re.compile(
    r"\b("
    r"booked|booking burst|cancelled appointment|moved appointment|"
    r"patient arrived|normal surgery day|patient checked in|waiting room"
    r")\b",
    re.IGNORECASE,
)


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


def validate_historical_diary_semantic_fixture_output(payload: Any) -> None:
    """Validate a reviewed semantic fixture payload without weakening neutral safety.

    This is for post-H15 review payloads only. It still rejects raw text,
    identifiers, paths, timestamps, and unsupported grammar actions.
    """
    issues: list[SafetyIssue] = []
    _validate_node_with_allowed(
        payload,
        "$",
        issues,
        allowed_keys=SAFE_HISTORICAL_DIARY_SEMANTIC_OUTPUT_KEYS,
    )

    if not isinstance(payload, dict):
        issues.append(SafetyIssue("$", "semantic fixture payload must be an object"))
    else:
        if payload.get("schema_version") != SEMANTIC_FIXTURE_SCHEMA_VERSION:
            issues.append(
                SafetyIssue(
                    "$.schema_version",
                    f"must be {SEMANTIC_FIXTURE_SCHEMA_VERSION!r}",
                )
            )
        if payload.get("source") != SEMANTIC_FIXTURE_SOURCE:
            issues.append(
                SafetyIssue("$.source", f"must be {SEMANTIC_FIXTURE_SOURCE!r}")
            )
        _validate_semantic_privacy(payload.get("privacy"), issues)
        _validate_semantic_scope(payload.get("semantic_scope"), issues)
        _validate_semantic_fixtures(payload.get("fixtures"), issues)

    if issues:
        raise HistoricalDiaryOutputSafetyError(issues)


def _validate_node(node: Any, path: str, issues: list[SafetyIssue]) -> None:
    _validate_node_with_allowed(
        node,
        path,
        issues,
        allowed_keys=SAFE_HISTORICAL_DIARY_OUTPUT_KEYS,
    )


def _validate_node_with_allowed(
    node: Any,
    path: str,
    issues: list[SafetyIssue],
    *,
    allowed_keys: set[str],
) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            key_path = f"{path}.{key}"
            _validate_key(key, key_path, issues, allowed_keys=allowed_keys)
            _validate_node_with_allowed(value, key_path, issues, allowed_keys=allowed_keys)
        return

    if isinstance(node, list):
        for index, value in enumerate(node):
            _validate_node_with_allowed(value, f"{path}[{index}]", issues, allowed_keys=allowed_keys)
        return

    if isinstance(node, str):
        _validate_string(node, path, issues)


def _validate_key(
    key: str,
    path: str,
    issues: list[SafetyIssue],
    *,
    allowed_keys: set[str],
) -> None:
    if key not in allowed_keys:
        issues.append(SafetyIssue(path, "key is not in the committed-output allowlist"))
    for pattern in UNSAFE_KEY_PATTERNS:
        if pattern.search(key) and key not in {
            "emits_document_text",
            "emits_exact_document_timestamps",
            "emits_filenames",
            "emits_patient_or_staff_labels",
            "emits_raw_paths",
            "local_raw_processing_only",
            "raw_data_external_provider_allowed",
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
    if LIKELY_BOOKING_SEMANTIC_RE.search(value):
        issues.append(SafetyIssue(path, "string looks like raw booking semantics"))


def _validate_semantic_privacy(value: Any, issues: list[SafetyIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(SafetyIssue("$.privacy", "semantic fixture privacy must be an object"))
        return

    required = {
        "local_raw_processing_only": True,
        "raw_data_external_provider_allowed": False,
        "emits_document_text": False,
        "emits_filenames": False,
        "emits_raw_paths": False,
        "emits_exact_document_timestamps": False,
        "emits_patient_or_staff_labels": False,
    }
    for key, expected in required.items():
        if value.get(key) is not expected:
            issues.append(SafetyIssue(f"$.privacy.{key}", f"must be {expected!r}"))


def _validate_semantic_scope(value: Any, issues: list[SafetyIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(SafetyIssue("$.semantic_scope", "semantic scope must be an object"))
        return

    if value.get("date_policy") not in ALLOWED_SEMANTIC_DATE_POLICIES:
        issues.append(SafetyIssue("$.semantic_scope.date_policy", "date policy is not allowed"))
    if value.get("date_policy") == "date_shifted" and not isinstance(
        value.get("date_shift_days"),
        int,
    ):
        issues.append(
            SafetyIssue(
                "$.semantic_scope.date_shift_days",
                "date_shifted policy requires integer date_shift_days",
            )
        )
    if not value.get("fixture_family"):
        issues.append(SafetyIssue("$.semantic_scope.fixture_family", "fixture family is required"))
    if not value.get("approval_expires_on"):
        issues.append(
            SafetyIssue("$.semantic_scope.approval_expires_on", "approval expiry is required")
        )

    allowed_actions = value.get("allowed_action_names")
    if not isinstance(allowed_actions, list) or not allowed_actions:
        issues.append(
            SafetyIssue("$.semantic_scope.allowed_action_names", "allowed actions are required")
        )
        return
    unsupported = sorted(set(allowed_actions) - ALLOWED_SEMANTIC_ACTION_NAMES)
    if unsupported:
        issues.append(
            SafetyIssue(
                "$.semantic_scope.allowed_action_names",
                f"unsupported action name(s): {unsupported}",
            )
        )


def _validate_semantic_fixtures(value: Any, issues: list[SafetyIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(SafetyIssue("$.fixtures", "semantic fixtures must be a non-empty list"))
        return

    for index, fixture in enumerate(value):
        path = f"$.fixtures[{index}]"
        if not isinstance(fixture, dict):
            issues.append(SafetyIssue(path, "semantic fixture must be an object"))
            continue
        for required in ("synthetic_event_id", "synthetic_resource_id", "action_name"):
            if not fixture.get(required):
                issues.append(SafetyIssue(f"{path}.{required}", "field is required"))
        action_name = fixture.get("action_name")
        if action_name not in ALLOWED_SEMANTIC_ACTION_NAMES:
            issues.append(SafetyIssue(f"{path}.action_name", "unsupported action name"))
        if "confidence_label" in fixture and fixture["confidence_label"] not in ALLOWED_CONFIDENCE_LABELS:
            issues.append(SafetyIssue(f"{path}.confidence_label", "confidence label is not allowed"))
        if "status_categories" in fixture:
            categories = fixture["status_categories"]
            if not isinstance(categories, list) or not set(categories).issubset(ALLOWED_STATUS_CATEGORIES):
                issues.append(SafetyIssue(f"{path}.status_categories", "status category is not allowed"))


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
