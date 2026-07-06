"""Validate the gate required before historical diary semantic labelling."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_DECISIONS = {
    "blocked",
    "approved_for_neutral_only",
    "approved_for_semantic_fixture_promotion",
}
ALLOWED_DATE_POLICIES = {
    "none",
    "relative_day_index_only",
    "date_shifted",
}
ALLOWED_RESOURCE_POLICIES = {
    "none",
    "synthetic_resource_ids_only",
}
ALLOWED_TEXT_POLICIES = {
    "no_text_export",
    "bucket_flags_only",
}
ALLOWED_FIXTURE_FAMILIES = {
    "action_grammar_candidates",
}
REQUIRED_FORBIDDEN_CATEGORIES = {
    "names",
    "phone_numbers",
    "medicare_numbers",
    "addresses",
    "free_text_notes",
    "staff_labels",
    "original_filenames",
    "exact_source_timestamps",
    "external_raw_uploads",
}
SAFE_ALLOWED_FIELDS = {
    "synthetic_event_ids",
    "relative_sequence_indexes",
    "relative_day_indexes",
    "date_shifted_day_indexes",
    "time_of_day",
    "duration_minutes",
    "synthetic_resource_ids",
    "status_categories",
    "transition_labels",
    "confidence_labels",
    "count_distributions",
    "bucket_flags",
}

WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\")
DOC_PATH_RE = re.compile(r"(?:\\|/)[^\\/\s]+\.docx?\b", re.IGNORECASE)
DATE_TIME_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}")
DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LIKELY_PERSON_NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b")


@dataclass(frozen=True)
class GateIssue:
    path: str
    reason: str


class DeidentificationGateError(ValueError):
    def __init__(self, issues: list[GateIssue]) -> None:
        self.issues = issues
        super().__init__("; ".join(f"{issue.path}: {issue.reason}" for issue in issues))


def validate_deidentification_gate(payload: dict[str, Any]) -> None:
    issues: list[GateIssue] = []
    _scan_strings(payload, "$", issues)

    if payload.get("gate") != "historical_diary_deidentification_gate":
        issues.append(GateIssue("$.gate", "must identify the historical diary gate"))
    if payload.get("version") != 1:
        issues.append(GateIssue("$.version", "must be version 1"))

    decision = payload.get("decision")
    if decision not in ALLOWED_DECISIONS:
        issues.append(GateIssue("$.decision", "decision is not allowed"))

    privacy = _dict(payload, "privacy", issues)
    if privacy:
        _must_be_false(
            privacy,
            "raw_data_external_provider_allowed",
            "$.privacy.raw_data_external_provider_allowed",
            issues,
        )
        _must_be_false(
            privacy,
            "commit_raw_or_extracted_text_allowed",
            "$.privacy.commit_raw_or_extracted_text_allowed",
            issues,
        )
        _must_be_false(
            privacy,
            "commit_identifying_labels_allowed",
            "$.privacy.commit_identifying_labels_allowed",
            issues,
        )
        _must_be_true(
            privacy,
            "local_raw_processing_only",
            "$.privacy.local_raw_processing_only",
            issues,
        )

    policy = _dict(payload, "deidentification_policy", issues)
    if policy:
        if policy.get("date_policy") not in ALLOWED_DATE_POLICIES:
            issues.append(GateIssue("$.deidentification_policy.date_policy", "date policy is not allowed"))
        if policy.get("resource_policy") not in ALLOWED_RESOURCE_POLICIES:
            issues.append(GateIssue("$.deidentification_policy.resource_policy", "resource policy is not allowed"))
        if policy.get("text_policy") not in ALLOWED_TEXT_POLICIES:
            issues.append(GateIssue("$.deidentification_policy.text_policy", "text policy is not allowed"))

    allowed_fields = set(_string_list(payload, "allowed_committed_fields", issues))
    unexpected_allowed = allowed_fields - SAFE_ALLOWED_FIELDS
    if unexpected_allowed:
        issues.append(
            GateIssue(
                "$.allowed_committed_fields",
                f"contains unsafe or unknown committed fields: {sorted(unexpected_allowed)}",
            )
        )

    forbidden = set(_string_list(payload, "forbidden_committed_categories", issues))
    missing_forbidden = REQUIRED_FORBIDDEN_CATEGORIES - forbidden
    if missing_forbidden:
        issues.append(
            GateIssue(
                "$.forbidden_committed_categories",
                f"missing required forbidden categories: {sorted(missing_forbidden)}",
            )
        )

    approval = _dict(payload, "approval", issues)
    if approval:
        reviewer = approval.get("reviewer")
        semantic_ack = approval.get("semantic_labelling_acknowledged")
        if decision == "approved_for_semantic_fixture_promotion":
            if not isinstance(reviewer, str) or reviewer.strip() == "":
                issues.append(GateIssue("$.approval.reviewer", "semantic approval requires reviewer"))
            if semantic_ack is not True:
                issues.append(
                    GateIssue(
                        "$.approval.semantic_labelling_acknowledged",
                        "semantic approval requires explicit acknowledgement",
                    )
                )
            _validate_semantic_scope(approval.get("semantic_scope"), issues)
            approval_expires_on = approval.get("approval_expires_on")
            if not isinstance(approval_expires_on, str) or not DATE_ONLY_RE.fullmatch(
                approval_expires_on
            ):
                issues.append(
                    GateIssue(
                        "$.approval.approval_expires_on",
                        "semantic approval requires YYYY-MM-DD expiry",
                    )
                )
        elif semantic_ack is True:
            issues.append(
                GateIssue(
                    "$.approval.semantic_labelling_acknowledged",
                    "semantic acknowledgement cannot be true unless decision approves semantic promotion",
                )
            )

    if issues:
        raise DeidentificationGateError(issues)


def _validate_semantic_scope(value: Any, issues: list[GateIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(GateIssue("$.approval.semantic_scope", "semantic approval requires scope"))
        return

    fixture_families = value.get("fixture_families")
    if not isinstance(fixture_families, list) or not fixture_families:
        issues.append(
            GateIssue("$.approval.semantic_scope.fixture_families", "fixture families are required")
        )
    else:
        unexpected = sorted(set(fixture_families) - ALLOWED_FIXTURE_FAMILIES)
        if unexpected:
            issues.append(
                GateIssue(
                    "$.approval.semantic_scope.fixture_families",
                    f"unsupported fixture families: {unexpected}",
                )
            )

    if value.get("prototype_slice") != "single_root_single_dense_day_max_80":
        issues.append(
            GateIssue(
                "$.approval.semantic_scope.prototype_slice",
                "prototype slice must be single_root_single_dense_day_max_80",
            )
        )
    if value.get("memory_use") != "prohibited":
        issues.append(GateIssue("$.approval.semantic_scope.memory_use", "memory use must be prohibited"))


def _dict(payload: dict[str, Any], key: str, issues: list[GateIssue]) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        issues.append(GateIssue(f"$.{key}", "must be an object"))
        return {}
    return value


def _string_list(payload: dict[str, Any], key: str, issues: list[GateIssue]) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(GateIssue(f"$.{key}", "must be a string list"))
        return []
    return value


def _must_be_false(
    payload: dict[str, Any],
    key: str,
    path: str,
    issues: list[GateIssue],
) -> None:
    if payload.get(key) is not False:
        issues.append(GateIssue(path, "must be false"))


def _must_be_true(
    payload: dict[str, Any],
    key: str,
    path: str,
    issues: list[GateIssue],
) -> None:
    if payload.get(key) is not True:
        issues.append(GateIssue(path, "must be true"))


def _scan_strings(node: Any, path: str, issues: list[GateIssue]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            _scan_strings(value, f"{path}.{key}", issues)
        return
    if isinstance(node, list):
        for index, value in enumerate(node):
            _scan_strings(value, f"{path}[{index}]", issues)
        return
    if isinstance(node, str):
        if "\n" in node or "\r" in node:
            issues.append(GateIssue(path, "string contains line breaks"))
        if len(node) > 120:
            issues.append(GateIssue(path, "string is too long for a gate value"))
        if WINDOWS_PATH_RE.search(node) or DOC_PATH_RE.search(node):
            issues.append(GateIssue(path, "string looks like a raw file path"))
        if DATE_TIME_RE.search(node):
            issues.append(GateIssue(path, "string looks like an exact source timestamp"))
        if LIKELY_PERSON_NAME_RE.search(node):
            issues.append(GateIssue(path, "string looks like a person or staff label"))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate_json", nargs="+", type=Path)
    args = parser.parse_args()

    for gate_json in args.gate_json:
        payload = load_json(gate_json)
        if not isinstance(payload, dict):
            raise DeidentificationGateError([GateIssue("$", "gate payload must be an object")])
        validate_deidentification_gate(payload)
        print(f"gate safe: {gate_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
