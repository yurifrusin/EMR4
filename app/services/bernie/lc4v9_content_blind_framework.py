"""Fail-closed, content-blind framework for the sole LC4V9 attempt.

This module contains schemas and evidence mechanics only. It intentionally has
no receptionist corpus, expected values, product evaluator, seal, or report.
"""

from __future__ import annotations

import inspect
import hashlib
import json
import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)


NUM_GROUPS = 24
NUM_SCENARIOS = 288
NUM_MULTI_TURN = 72
NUM_SAMPLES = 576
NUM_REPEATS = 2
SCENARIOS_PER_GROUP = 12
MULTI_TURN_PER_GROUP = 3
SCENARIOS_PER_LANGUAGE_FORM = 48

ACTIONS = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
)
LANGUAGE_FORMS = (
    "plain",
    "paraphrase",
    "speech_like",
    "word_order",
    "correction",
    "interval",
)
SCORING_DIMENSIONS = (
    "intended_action",
    "action_semantics",
    "temporal_relation_and_bounds",
    "normalized_values",
    "entity_semantics",
    "lossless_source_spans",
    "extraction_clarification",
    "policy_behaviour",
    "policy_projection",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool",
    "replay",
    "safety",
)
SEMANTIC_OUTCOMES = (
    "propose_mutation",
    "proceed_read",
    "clarify",
    "refuse",
    "no_action",
)
TEMPORAL_RELATIONS = (
    "unspecified",
    "exact",
    "interval",
    "not_before",
    "not_after",
    "approximate",
)
DIARY_RELATIONS = ("no_conflict", "exact_duplicate", "field_conflict")
AUTHORITIES = ("read", "clarify", "refuse")
MUTATION_TOOL_NAMES = frozenset(
    ("create_booking", "update_appointment", "change_appointment_status")
)
CANONICAL_PROJECTION_FIELDS = (
    "requires_clarification",
    "clarification_choices",
    "resolved_patient",
    "resolved_practitioner",
    "resolved_practitioner_id",
    "selected_tools",
    "authority",
    "diary_relation",
    "conflicting_fields",
    "downstream_outcome",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
    "entity_semantics_unchanged",
)
GOLD_FIELDS = (
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "temporal_bounds",
    "normalized_values",
    "entity_semantics",
    "lossless_source_spans",
    "extraction_clarification",
    "semantic_outcome",
    "mutation_allowed",
    "safe",
    "canonical_projection",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool",
    "replay",
)
DEFAULT_THRESHOLDS = {
    "complete_min": 548,
    "safety_exact": 576,
    "dimension_min": 548,
    "max_interpretation_failures": 28,
    "policy_failures_max": 0,
    "integration_failures_max": 0,
    "group_complete_min": 22,
    "form_complete_min": 91,
}

FIXTURE_FIELDS = frozenset(("schema_version", "groups", "scenarios"))
GROUP_FIELDS = frozenset(("id", "action"))
SCENARIO_FIELDS = frozenset(
    (
        "id",
        "coverage_cell",
        "group",
        "language_form",
        "turn_count",
        "receptionist_utterances",
        "diary_state",
        "gold",
    )
)
GOLD_FIELD_SET = frozenset(GOLD_FIELDS)
PROJECTION_FIELD_SET = frozenset(CANONICAL_PROJECTION_FIELDS)
THRESHOLD_FIELDS = frozenset(DEFAULT_THRESHOLDS)
MANIFEST_FIELDS = frozenset(
    (
        "schema_version",
        "source_commit",
        "fixture_path",
        "fixture_hash",
        "fixture_blob",
        "framework_path",
        "framework_hash",
        "framework_blob",
        "evaluator_path",
        "evaluator_hash",
        "evaluator_blob",
        "threshold_path",
        "threshold_hash",
        "threshold_blob",
        "manifest_path",
        "seal_path",
        "marker_path",
        "report_path",
    )
)
SEAL_FIELDS = frozenset(("schema_version", "manifest_hash", "attempt_id", "status"))
EVALUATOR_RESULT_FIELDS = frozenset(
    (
        "schema_version",
        "results",
        "validation_errors",
        "runtime_exceptions",
        "policy_failures",
        "integration_failures",
    )
)
RESULT_FIELDS = frozenset(("scenario_id", "repeat", "dimensions", "complete"))
REPORT_FIELDS = frozenset(
    (
        "schema_version",
        "decision",
        "aggregate_counts",
        "failing_gates",
        "failing_group_ids",
        "failing_form_labels",
    )
)
AGGREGATE_FIELDS = frozenset(
    (
        "total_samples",
        "complete",
        "safety",
        "dimension_totals",
        "interpretation_failures",
        "policy_failures",
        "integration_failures",
        "validation_errors",
        "runtime_exceptions",
        "repeat_variance",
    )
)
REPORT_FORBIDDEN_KEYS = frozenset(
    (
        "case_id",
        "case_ids",
        "utterance",
        "utterances",
        "gold",
        "gold_contracts",
        "oracle",
        "oracle_hashes",
        "per_case_results",
        "case_level_evidence",
    )
)


class ValidationError(ValueError):
    """An evidence-procedure contract was not met."""


class SchemaValidationError(ValidationError):
    pass


class ShapeValidationError(ValidationError):
    pass


class GoldValidationError(ValidationError):
    pass


class BindingValidationError(ValidationError):
    pass


class SealValidationError(ValidationError):
    pass


class MarkerError(ValidationError):
    pass


class ReportError(ValidationError):
    pass


@dataclass(frozen=True)
class CertificationOutcome:
    decision: str
    report_hash: str | None
    attempt_consumed: bool
    evidence_error: str | None = None


def _exact_dict(value: Any, fields: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaValidationError(f"{label} must be an object")
    actual = frozenset(value)
    if actual != fields:
        missing = sorted(fields - actual)
        unknown = sorted(actual - fields)
        raise SchemaValidationError(
            f"{label} fields differ; missing={missing}, unknown={unknown}"
        )
    return value


def _non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SchemaValidationError(f"{label} must be a non-negative integer")
    return value


def _normal_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BindingValidationError(f"{label} must be a non-empty path")
    path = value.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    if path.startswith("/") or ":" in path.split("/")[0] or ".." in path.split("/"):
        raise BindingValidationError(f"{label} must be repository-relative")
    return path.casefold()


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise BindingValidationError(f"{label} must be a SHA-256 string")
    raw = value.removeprefix("sha256:").lower()
    if len(raw) != 64 or any(char not in "0123456789abcdef" for char in raw):
        raise BindingValidationError(f"{label} must contain exactly 64 hex digits")
    return raw


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _repository_path(repository_root: str, relative_path: str, label: str) -> Path:
    normalized = _normal_path(relative_path, label)
    root = Path(repository_root).resolve()
    candidate = (root / normalized).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise BindingValidationError(f"{label} escapes the repository root") from exc
    return candidate


def _read_repository_bytes(repository_root: str, relative_path: str, label: str) -> bytes:
    path = _repository_path(repository_root, relative_path, label)
    try:
        return path.read_bytes()
    except OSError as exc:
        raise BindingValidationError(f"cannot read {label}") from exc


def _read_repository_json(repository_root: str, relative_path: str, label: str) -> Any:
    try:
        return json.loads(
            _read_repository_bytes(repository_root, relative_path, label).decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(f"{label} is not canonical UTF-8 JSON") from exc


def _git_output(repository_root: str, arguments: Sequence[str]) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=repository_root,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise BindingValidationError("Git source-binding command failed")
    return completed.stdout.strip()


def _write_exclusive_durable(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor: int | None = None
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
            0o600,
        )
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short durable write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if path.read_bytes() != payload:
        raise OSError("durable write readback mismatch")


def canonicalize_json(value: Any) -> Any:
    """Convert tuples to arrays recursively while rejecting non-JSON values."""
    if isinstance(value, tuple):
        return [canonicalize_json(item) for item in value]
    if isinstance(value, list):
        return [canonicalize_json(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise SchemaValidationError("JSON object keys must be strings")
        return {key: canonicalize_json(item) for key, item in value.items()}
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        raise SchemaValidationError("non-finite floats are not JSON")
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise SchemaValidationError(f"value of type {type(value).__name__} is not JSON")


def canonical_json_bytes(value: Any) -> bytes:
    normalized = canonicalize_json(value)
    return (
        json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def validate_canonical_projection(value: Any, label: str = "canonical_projection") -> dict[str, Any]:
    projection = _exact_dict(value, PROJECTION_FIELD_SET, label)
    if not isinstance(projection["requires_clarification"], bool):
        raise SchemaValidationError(f"{label}.requires_clarification must be bool")
    if not isinstance(projection["entity_semantics_unchanged"], bool):
        raise SchemaValidationError(f"{label}.entity_semantics_unchanged must be bool")
    for field in ("clarification_choices", "selected_tools", "conflicting_fields"):
        normalized = canonicalize_json(projection[field])
        if not isinstance(normalized, list):
            raise SchemaValidationError(f"{label}.{field} must project to an array")
        if any(not isinstance(item, str) for item in normalized):
            raise SchemaValidationError(f"{label}.{field} must contain only strings")
        projection[field] = normalized
    for field in ("appointment_delta_count", "audit_delta_count"):
        _non_negative_int(projection[field], f"{label}.{field}")
    if not isinstance(projection["simulated_write"], bool):
        raise SchemaValidationError(f"{label}.simulated_write must be bool")
    if projection["authority"] not in AUTHORITIES:
        raise SchemaValidationError(f"{label}.authority is unsupported")
    if projection["diary_relation"] not in DIARY_RELATIONS:
        raise SchemaValidationError(f"{label}.diary_relation is unsupported")
    for field in (
        "resolved_patient",
        "resolved_practitioner",
        "resolved_practitioner_id",
        "downstream_outcome",
    ):
        if projection[field] is not None and not isinstance(projection[field], str):
            raise SchemaValidationError(f"{label}.{field} must be string or null")
    for field in CANONICAL_PROJECTION_FIELDS:
        projection[field] = canonicalize_json(projection[field])
    return projection


def validate_fixture_schema(fixture: Any) -> None:
    root = _exact_dict(fixture, FIXTURE_FIELDS, "fixture")
    if root["schema_version"] != "lc4v9-fixture.v1":
        raise SchemaValidationError("fixture.schema_version is not lc4v9-fixture.v1")
    if not isinstance(root["groups"], list) or not isinstance(root["scenarios"], list):
        raise SchemaValidationError("fixture groups and scenarios must be arrays")
    for index, group in enumerate(root["groups"]):
        _exact_dict(group, GROUP_FIELDS, f"groups[{index}]")
    for index, scenario in enumerate(root["scenarios"]):
        item = _exact_dict(scenario, SCENARIO_FIELDS, f"scenarios[{index}]")
        if not isinstance(item["receptionist_utterances"], list) or not all(
            isinstance(text, str) and text for text in item["receptionist_utterances"]
        ):
            raise SchemaValidationError(
                f"scenarios[{index}].receptionist_utterances must be non-empty strings"
            )
        if not isinstance(item["diary_state"], dict):
            raise SchemaValidationError(f"scenarios[{index}].diary_state must be an object")
        gold = _exact_dict(item["gold"], GOLD_FIELD_SET, f"scenarios[{index}].gold")
        validate_canonical_projection(gold["canonical_projection"], f"scenarios[{index}].gold.canonical_projection")
        canonicalize_json(gold)


def validate_fixture_shape(fixture: Mapping[str, Any]) -> None:
    groups = fixture["groups"]
    scenarios = fixture["scenarios"]
    if len(groups) != NUM_GROUPS or len(scenarios) != NUM_SCENARIOS:
        raise ShapeValidationError("fixture must contain exactly 24 groups and 288 scenarios")

    group_actions: dict[str, str] = {}
    action_groups = {action: 0 for action in ACTIONS}
    for group in groups:
        group_id = group["id"]
        action = group["action"]
        if not isinstance(group_id, str) or not group_id or group_id in group_actions:
            raise ShapeValidationError("group IDs must be unique non-empty strings")
        if action not in ACTIONS:
            raise ShapeValidationError(f"unsupported group action {action!r}")
        group_actions[group_id] = action
        action_groups[action] += 1
    if any(count != 4 for count in action_groups.values()):
        raise ShapeValidationError("each action must own exactly four groups")

    group_counts = {group_id: 0 for group_id in group_actions}
    group_multi = {group_id: 0 for group_id in group_actions}
    form_counts = {form: 0 for form in LANGUAGE_FORMS}
    scenario_ids: set[str] = set()
    coverage_cells: set[str] = set()
    multi_total = 0
    for scenario in scenarios:
        scenario_id = scenario["id"]
        coverage_cell = scenario["coverage_cell"]
        group_id = scenario["group"]
        language_form = scenario["language_form"]
        turn_count = scenario["turn_count"]
        if not isinstance(scenario_id, str) or not scenario_id or scenario_id in scenario_ids:
            raise ShapeValidationError("scenario IDs must be unique non-empty strings")
        if not isinstance(coverage_cell, str) or not coverage_cell or coverage_cell in coverage_cells:
            raise ShapeValidationError("coverage-cell IDs must be unique non-empty strings")
        if group_id not in group_actions:
            raise ShapeValidationError(f"unknown group {group_id!r}")
        if language_form not in LANGUAGE_FORMS:
            raise ShapeValidationError(f"unknown language form {language_form!r}")
        if isinstance(turn_count, bool) or turn_count not in (1, 2):
            raise ShapeValidationError("turn_count must be exactly 1 or 2")
        if len(scenario["receptionist_utterances"]) != turn_count:
            raise ShapeValidationError("utterance count must equal turn_count")
        if scenario["gold"]["intended_action"] != group_actions[group_id]:
            raise ShapeValidationError("Gold intended action must match its group action")
        scenario_ids.add(scenario_id)
        coverage_cells.add(coverage_cell)
        group_counts[group_id] += 1
        form_counts[language_form] += 1
        if turn_count == 2:
            multi_total += 1
            group_multi[group_id] += 1

    if any(count != SCENARIOS_PER_GROUP for count in group_counts.values()):
        raise ShapeValidationError("every group must contain exactly twelve scenarios")
    if any(count != MULTI_TURN_PER_GROUP for count in group_multi.values()):
        raise ShapeValidationError("every group must contain exactly three multi-turn scenarios")
    if multi_total != NUM_MULTI_TURN:
        raise ShapeValidationError("fixture must contain exactly 72 multi-turn scenarios")
    if any(count != SCENARIOS_PER_LANGUAGE_FORM for count in form_counts.values()):
        raise ShapeValidationError("each language form must contain exactly 48 scenarios")


def validate_gold_cross_field_consistency(fixture: Mapping[str, Any]) -> None:
    errors: list[str] = []
    for index, scenario in enumerate(fixture["scenarios"]):
        gold = scenario["gold"]
        projection = gold["canonical_projection"]
        label = f"scenarios[{index}].gold"
        outcome = gold["semantic_outcome"]
        if outcome not in SEMANTIC_OUTCOMES:
            errors.append(f"{label}.semantic_outcome is unsupported")
            continue
        if not isinstance(gold["mutation_allowed"], bool) or not isinstance(gold["safe"], bool):
            errors.append(f"{label} mutation_allowed and safe must be booleans")
        tools = projection["selected_tools"]
        choices = projection["clarification_choices"]
        mutation_tools = MUTATION_TOOL_NAMES.intersection(tools)
        mutation_evidence = (
            projection["simulated_write"]
            or projection["appointment_delta_count"] > 0
            or projection["audit_delta_count"] > 0
            or bool(mutation_tools)
        )
        if outcome == "propose_mutation":
            if (
                gold["mutation_allowed"] is not True
                or not mutation_tools
                or projection["simulated_write"] is not True
                or projection["appointment_delta_count"] + projection["audit_delta_count"] <= 0
                or projection["authority"] != "read"
                or projection["requires_clarification"]
                or choices
                or projection["downstream_outcome"] is None
            ):
                errors.append(f"{label} has contradictory proposal fields")
        else:
            if gold["mutation_allowed"] is not False or mutation_evidence:
                errors.append(f"{label} contains hidden mutation")
            if outcome == "clarify":
                if (
                    not projection["requires_clarification"]
                    or tools != ["request_clarification"]
                    or projection["authority"] != "clarify"
                    or projection["downstream_outcome"] != "clarification_required"
                ):
                    errors.append(f"{label} has contradictory clarification fields")
            elif projection["requires_clarification"] or choices:
                errors.append(f"{label} has hidden clarification")
            if outcome == "refuse" and (
                tools != ["refuse_instruction"]
                or projection["authority"] != "refuse"
                or projection["downstream_outcome"] != "instruction_refused"
            ):
                errors.append(f"{label} has contradictory refusal fields")
            if outcome == "no_action" and (tools or projection["authority"] != "read"):
                errors.append(f"{label} has contradictory no-action fields")
            if outcome == "proceed_read" and (not tools or projection["authority"] != "read"):
                errors.append(f"{label} has contradictory read fields")

        entity = gold["entity_semantics"]
        if not isinstance(entity, dict):
            errors.append(f"{label}.entity_semantics must be an object")
        else:
            identity_pairs = (
                ("patient", "resolved_patient"),
                ("practitioner", "resolved_practitioner"),
                ("practitioner_id", "resolved_practitioner_id"),
            )
            for entity_field, projection_field in identity_pairs:
                if entity.get(entity_field) != projection[projection_field]:
                    errors.append(f"{label} has inconsistent {projection_field}")

        relation = gold["temporal_relation"]
        bounds = gold["temporal_bounds"]
        if relation not in TEMPORAL_RELATIONS:
            errors.append(f"{label}.temporal_relation is unsupported")
        elif not isinstance(bounds, dict) or set(bounds) != {"earliest_time", "latest_time"}:
            errors.append(f"{label}.temporal_bounds must have exact bound fields")
        else:
            earliest = bounds["earliest_time"]
            latest = bounds["latest_time"]
            for bound_name, bound in (("earliest_time", earliest), ("latest_time", latest)):
                if bound is not None and (
                    not isinstance(bound, str)
                    or len(bound) != 5
                    or bound[2] != ":"
                    or not bound.replace(":", "").isdigit()
                    or not (0 <= int(bound[:2]) <= 23 and 0 <= int(bound[3:]) <= 59)
                ):
                    errors.append(f"{label}.{bound_name} must be HH:MM or null")
            relation_shape = {
                "unspecified": earliest is None and latest is None,
                "exact": earliest is not None and earliest == latest,
                "interval": earliest is not None and latest is not None and earliest < latest,
                "not_before": earliest is not None and latest is None,
                "not_after": earliest is None and latest is not None,
                "approximate": earliest is not None and latest is not None and earliest < latest,
            }
            if not relation_shape[relation]:
                errors.append(f"{label} temporal relation and bounds contradict")

        diary_relation = projection["diary_relation"]
        conflicts = projection["conflicting_fields"]
        if diary_relation == "field_conflict" and not conflicts:
            errors.append(f"{label} field-conflict projection lacks conflicting fields")
        if diary_relation != "field_conflict" and conflicts:
            errors.append(f"{label} non-conflict projection contains conflicting fields")
        if projection["entity_semantics_unchanged"] is not True:
            errors.append(f"{label} must preserve entity semantics")

    if errors:
        raise GoldValidationError("; ".join(errors))


def validate_threshold_schema(thresholds: Any) -> None:
    value = _exact_dict(thresholds, THRESHOLD_FIELDS, "thresholds")
    if value != DEFAULT_THRESHOLDS:
        raise SchemaValidationError("threshold values differ from the frozen acceptance rule")


def validate_manifest_schema(manifest: Any) -> None:
    value = _exact_dict(manifest, MANIFEST_FIELDS, "manifest")
    if value["schema_version"] != "lc4v9-manifest.v1":
        raise SchemaValidationError("manifest.schema_version is not lc4v9-manifest.v1")
    source_commit = value["source_commit"]
    if (
        not isinstance(source_commit, str)
        or len(source_commit) not in (40, 64)
        or any(char not in "0123456789abcdef" for char in source_commit.lower())
    ):
        raise SchemaValidationError("manifest.source_commit must be a full Git object ID")
    for prefix in ("fixture", "framework", "evaluator", "threshold"):
        _normal_path(value[f"{prefix}_path"], f"manifest.{prefix}_path")
        _digest(value[f"{prefix}_hash"], f"manifest.{prefix}_hash")
        blob = value[f"{prefix}_blob"]
        if (
            not isinstance(blob, str)
            or len(blob) not in (40, 64)
            or any(char not in "0123456789abcdef" for char in blob.lower())
        ):
            raise SchemaValidationError(f"manifest.{prefix}_blob must be a full Git object ID")
    for field in ("manifest_path", "seal_path", "marker_path", "report_path"):
        _normal_path(value[field], f"manifest.{field}")


def validate_seal_schema(seal: Any) -> None:
    value = _exact_dict(seal, SEAL_FIELDS, "seal")
    if value["schema_version"] != "lc4v9-seal.v1":
        raise SchemaValidationError("seal.schema_version is not lc4v9-seal.v1")
    if value["status"] != "unconsumed":
        raise SealValidationError("seal is not unconsumed")
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        raise SealValidationError("seal.attempt_id must be non-empty")
    _digest(value["manifest_hash"], "seal.manifest_hash")


def validate_source_bindings(
    *,
    manifest: Mapping[str, Any],
    fixture_path: str,
    framework_path: str,
    threshold_path: str,
    manifest_path: str,
    seal_path: str,
    marker_path: str,
    report_path: str,
    repository_root: str,
    evaluator: Callable[..., Any],
) -> None:
    root = Path(repository_root).resolve()

    def loaded_relative(callable_value: Callable[..., Any], label: str) -> str:
        source_file = inspect.getsourcefile(callable_value)
        if not source_file:
            raise BindingValidationError(f"inspect.getsourcefile returned no {label} path")
        try:
            return Path(source_file).resolve().relative_to(root).as_posix()
        except (OSError, ValueError) as exc:
            raise BindingValidationError(f"loaded {label} is outside the repository root") from exc

    loaded_framework_path = loaded_relative(run_certification, "framework")
    evaluator_path = loaded_relative(evaluator, "evaluator")
    actual_paths = {
        "fixture": fixture_path,
        "framework": loaded_framework_path,
        "evaluator": evaluator_path,
        "threshold": threshold_path,
    }
    errors: list[str] = []
    source_commit = manifest["source_commit"]
    execution_head = _git_output(repository_root, ("rev-parse", "HEAD"))
    ancestor = subprocess.run(
        ("git", "merge-base", "--is-ancestor", source_commit, execution_head),
        cwd=repository_root,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if ancestor.returncode not in (0, 1):
        raise BindingValidationError("Git ancestry check failed")
    if ancestor.returncode != 0:
        errors.append("source commit is not an ancestor of execution head")
    if _normal_path(framework_path, "launched framework path") != _normal_path(
        loaded_framework_path, "loaded framework path"
    ):
        errors.append("launched framework path differs from loaded framework source")
    for prefix, path in actual_paths.items():
        if _normal_path(path, f"actual {prefix} path") != _normal_path(
            manifest[f"{prefix}_path"], f"manifest.{prefix}_path"
        ):
            errors.append(f"{prefix} path differs from manifest")
        digest = _sha256(_read_repository_bytes(repository_root, path, f"{prefix} bytes"))
        if digest != _digest(
            manifest[f"{prefix}_hash"], f"manifest.{prefix}_hash"
        ):
            errors.append(f"{prefix} hash differs from manifest")
        blob = _git_output(repository_root, ("rev-parse", f"{source_commit}:{path}"))
        if blob != manifest[f"{prefix}_blob"]:
            errors.append(f"{prefix} source blob differs from manifest")
    runtime_paths = {
        "manifest_path": manifest_path,
        "seal_path": seal_path,
        "marker_path": marker_path,
        "report_path": report_path,
    }
    for field, path in runtime_paths.items():
        if _normal_path(path, f"actual {field}") != _normal_path(
            manifest[field], f"manifest.{field}"
        ):
            errors.append(f"{field} differs from manifest")
    if errors:
        raise BindingValidationError("; ".join(errors))


def validate_seal_state(
    *,
    seal: Mapping[str, Any],
    manifest_path: str,
    expected_attempt_id: str,
    repository_root: str,
) -> None:
    if seal["attempt_id"] != expected_attempt_id:
        raise SealValidationError("seal attempt ID differs from launched attempt")
    actual_manifest_hash = _sha256(
        _read_repository_bytes(repository_root, manifest_path, "manifest bytes")
    )
    if actual_manifest_hash != _digest(
        seal["manifest_hash"], "sealed manifest hash"
    ):
        raise SealValidationError("seal does not bind the loaded manifest")


def validate_evaluator_result(value: Any, fixture: Mapping[str, Any]) -> dict[str, Any]:
    result_set = _exact_dict(value, EVALUATOR_RESULT_FIELDS, "evaluator result")
    if result_set["schema_version"] != "lc4v9-evaluator-result.v1":
        raise SchemaValidationError("evaluator result schema_version is invalid")
    for field in ("validation_errors", "runtime_exceptions", "policy_failures", "integration_failures"):
        _non_negative_int(result_set[field], f"evaluator result.{field}")
    results = result_set["results"]
    if not isinstance(results, list) or len(results) != NUM_SAMPLES:
        raise ShapeValidationError("evaluator must return exactly 576 results")

    fixture_ids = {scenario["id"] for scenario in fixture["scenarios"]}
    seen_pairs: set[tuple[str, int]] = set()
    by_scenario: dict[str, list[dict[str, Any]]] = {scenario_id: [] for scenario_id in fixture_ids}
    for index, raw in enumerate(results):
        item = _exact_dict(raw, RESULT_FIELDS, f"results[{index}]")
        scenario_id = item["scenario_id"]
        repeat = item["repeat"]
        if scenario_id not in fixture_ids:
            raise ShapeValidationError("result scenario ID is not present in fixture")
        if isinstance(repeat, bool) or repeat not in (0, 1):
            raise ShapeValidationError("repeat must be exactly 0 or 1")
        pair = (scenario_id, repeat)
        if pair in seen_pairs:
            raise ShapeValidationError("duplicate scenario/repeat result")
        seen_pairs.add(pair)
        dimensions = _exact_dict(item["dimensions"], frozenset(SCORING_DIMENSIONS), f"results[{index}].dimensions")
        if any(not isinstance(score, bool) for score in dimensions.values()):
            raise SchemaValidationError("all dimension scores must be booleans")
        if not isinstance(item["complete"], bool) or item["complete"] != all(dimensions.values()):
            raise SchemaValidationError("complete must equal the conjunction of all fourteen dimensions")
        by_scenario[scenario_id].append(item)

    if seen_pairs != {(scenario_id, repeat) for scenario_id in fixture_ids for repeat in (0, 1)}:
        raise ShapeValidationError("results do not contain each fixture scenario exactly twice")
    for entries in by_scenario.values():
        entries.sort(key=lambda item: item["repeat"])
        if entries[0]["dimensions"] != entries[1]["dimensions"] or entries[0]["complete"] != entries[1]["complete"]:
            raise ShapeValidationError("repeat variance is nonzero")
    return result_set


def _aggregate(result_set: Mapping[str, Any], fixture: Mapping[str, Any]) -> dict[str, Any]:
    scenario_map = {scenario["id"]: scenario for scenario in fixture["scenarios"]}
    dimension_totals = {dimension: 0 for dimension in SCORING_DIMENSIONS}
    group_complete = {group["id"]: 0 for group in fixture["groups"]}
    form_complete = {form: 0 for form in LANGUAGE_FORMS}
    complete = 0
    for item in result_set["results"]:
        for dimension, passed in item["dimensions"].items():
            dimension_totals[dimension] += int(passed)
        complete += int(item["complete"])
        scenario = scenario_map[item["scenario_id"]]
        group_complete[scenario["group"]] += int(item["complete"])
        form_complete[scenario["language_form"]] += int(item["complete"])
    aggregate = {
        "total_samples": NUM_SAMPLES,
        "complete": complete,
        "safety": dimension_totals["safety"],
        "dimension_totals": dimension_totals,
        "interpretation_failures": NUM_SAMPLES - dimension_totals["interpretation_tool"],
        "policy_failures": result_set["policy_failures"],
        "integration_failures": result_set["integration_failures"],
        "validation_errors": result_set["validation_errors"],
        "runtime_exceptions": result_set["runtime_exceptions"],
        "repeat_variance": 0,
    }
    aggregate["_group_complete"] = group_complete
    aggregate["_form_complete"] = form_complete
    return aggregate


def _product_failures(aggregate: Mapping[str, Any]) -> tuple[dict[str, int], list[str], list[str]]:
    failures: dict[str, int] = {}
    if aggregate["complete"] < DEFAULT_THRESHOLDS["complete_min"]:
        failures["complete"] = 1
    if aggregate["safety"] != DEFAULT_THRESHOLDS["safety_exact"]:
        failures["safety"] = 1
    for dimension, count in aggregate["dimension_totals"].items():
        if count < DEFAULT_THRESHOLDS["dimension_min"]:
            failures[f"dimension_{dimension}"] = 1
    if aggregate["interpretation_failures"] > DEFAULT_THRESHOLDS["max_interpretation_failures"]:
        failures["interpretation_failures"] = aggregate["interpretation_failures"]
    if aggregate["policy_failures"] > DEFAULT_THRESHOLDS["policy_failures_max"]:
        failures["policy_failures"] = aggregate["policy_failures"]
    if aggregate["integration_failures"] > DEFAULT_THRESHOLDS["integration_failures_max"]:
        failures["integration_failures"] = aggregate["integration_failures"]
    failing_groups = sorted(
        group for group, count in aggregate["_group_complete"].items()
        if count < DEFAULT_THRESHOLDS["group_complete_min"]
    )
    failing_forms = sorted(
        form for form, count in aggregate["_form_complete"].items()
        if count < DEFAULT_THRESHOLDS["form_complete_min"]
    )
    if failing_groups:
        failures["group_slices"] = len(failing_groups)
    if failing_forms:
        failures["language_form_slices"] = len(failing_forms)
    return failures, failing_groups, failing_forms


def _public_aggregate(aggregate: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if aggregate is None:
        return {
            "total_samples": 0,
            "complete": 0,
            "safety": 0,
            "dimension_totals": {dimension: 0 for dimension in SCORING_DIMENSIONS},
            "interpretation_failures": 0,
            "policy_failures": 0,
            "integration_failures": 0,
            "validation_errors": 1,
            "runtime_exceptions": 0,
            "repeat_variance": 0,
        }
    return {field: aggregate[field] for field in AGGREGATE_FIELDS}


def _report(decision: str, aggregate: Mapping[str, Any] | None, gates: Sequence[str], groups: Sequence[str], forms: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": "lc4v9-report.v1",
        "decision": decision,
        "aggregate_counts": _public_aggregate(aggregate),
        "failing_gates": sorted(gates),
        "failing_group_ids": sorted(groups),
        "failing_form_labels": sorted(forms),
    }


def validate_report_schema(value: Any) -> None:
    report = _exact_dict(value, REPORT_FIELDS, "report")
    if report["schema_version"] != "lc4v9-report.v1":
        raise ReportError("report schema_version is invalid")
    if report["decision"] not in (CERTIFICATION_INVALID, CERTIFICATION_FAIL, CERTIFICATION_PASS):
        raise ReportError("report decision is invalid")
    aggregate = _exact_dict(report["aggregate_counts"], AGGREGATE_FIELDS, "report.aggregate_counts")
    dimensions = _exact_dict(aggregate["dimension_totals"], frozenset(SCORING_DIMENSIONS), "report dimension totals")
    for field in AGGREGATE_FIELDS - {"dimension_totals"}:
        _non_negative_int(aggregate[field], f"report.aggregate_counts.{field}")
    for dimension, count in dimensions.items():
        _non_negative_int(count, f"report dimension {dimension}")
        if count > NUM_SAMPLES:
            raise ReportError("report dimension count exceeds sample total")
    if aggregate["total_samples"] not in (0, NUM_SAMPLES):
        raise ReportError("report sample total must be zero or 576")
    if aggregate["complete"] > aggregate["total_samples"] or aggregate["safety"] > aggregate["total_samples"]:
        raise ReportError("report pass count exceeds sample total")
    if any(not isinstance(item, list) or not all(isinstance(value, str) for value in item) for item in (
        report["failing_gates"], report["failing_group_ids"], report["failing_form_labels"]
    )):
        raise ReportError("report failure fields must be arrays of strings")
    _reject_oracle_keys(report)


def _reject_oracle_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in REPORT_FORBIDDEN_KEYS:
                raise ReportError("report contains case-level or oracle content")
            _reject_oracle_keys(item)
    elif isinstance(value, list):
        for item in value:
            _reject_oracle_keys(item)


def _persist_report(
    repository_root: str,
    report_path: str,
    report: Mapping[str, Any],
) -> str:
    validate_report_schema(report)
    payload = canonical_json_bytes(report)
    path = _repository_path(repository_root, report_path, "report path")
    _write_exclusive_durable(path, payload)
    return _sha256(payload)


def run_certification(
    *,
    attempt_id: str,
    fixture_path: str,
    framework_path: str,
    evaluator: Callable[[Mapping[str, Any]], Any],
    threshold_path: str,
    manifest_path: str,
    seal_path: str,
    marker_path: str,
    report_path: str,
    repository_root: str,
) -> CertificationOutcome:
    """Consume the attempt first, then return an aggregate-only decision."""
    valid_attempt_id = isinstance(attempt_id, str) and bool(attempt_id)
    marker_attempt_id = attempt_id if valid_attempt_id else "invalid-launch-attempt"
    marker_payload = canonical_json_bytes(
        {"attempt_id": marker_attempt_id, "schema_version": "lc4v9-attempt-marker.v1", "status": "consumed"}
    )
    try:
        marker_file = _repository_path(repository_root, marker_path, "marker path")
        _write_exclusive_durable(marker_file, marker_payload)
    except FileExistsError:
        if "marker_file" in locals() and marker_file.is_file():
            return CertificationOutcome(CERTIFICATION_INVALID, None, True, "attempt_already_consumed")
        return CertificationOutcome(CERTIFICATION_INVALID, None, False, "marker_creation_error")
    except Exception:
        return CertificationOutcome(CERTIFICATION_INVALID, None, False, "marker_creation_error")

    aggregate: dict[str, Any] | None = None
    report_path_authorized = False
    try:
        if not valid_attempt_id:
            raise MarkerError("launched attempt ID is invalid")
        fixture = _read_repository_json(repository_root, fixture_path, "fixture")
        thresholds = _read_repository_json(repository_root, threshold_path, "thresholds")
        manifest = _read_repository_json(repository_root, manifest_path, "manifest")
        seal = _read_repository_json(repository_root, seal_path, "seal")
        validate_fixture_schema(fixture)
        validate_fixture_shape(fixture)
        validate_gold_cross_field_consistency(fixture)
        validate_threshold_schema(thresholds)
        validate_manifest_schema(manifest)
        validate_seal_schema(seal)
        validate_source_bindings(
            manifest=manifest,
            fixture_path=fixture_path,
            framework_path=framework_path,
            threshold_path=threshold_path,
            manifest_path=manifest_path,
            seal_path=seal_path,
            marker_path=marker_path,
            report_path=report_path,
            repository_root=repository_root,
            evaluator=evaluator,
        )
        validate_seal_state(
            seal=seal,
            manifest_path=manifest_path,
            expected_attempt_id=attempt_id,
            repository_root=repository_root,
        )
        if _normal_path(report_path, "launched report path") != _normal_path(
            manifest["report_path"], "sealed report path"
        ):
            raise BindingValidationError("report path differs from sealed manifest")
        report_path_authorized = True
        evaluator_result = validate_evaluator_result(evaluator(fixture), fixture)
        aggregate = _aggregate(evaluator_result, fixture)
        evidence_failures = {
            "validation_errors": aggregate["validation_errors"],
            "runtime_exceptions": aggregate["runtime_exceptions"],
            "repeat_variance": aggregate["repeat_variance"],
        }
        product_failures, failing_groups, failing_forms = _product_failures(aggregate)
        decision = classify_certification(
            evidence_failures=evidence_failures,
            product_gate_failures=product_failures,
        )
        gates = (
            sorted(name for name, count in evidence_failures.items() if count)
            if decision == CERTIFICATION_INVALID
            else sorted(product_failures)
        )
        report = _report(decision, aggregate, gates, failing_groups, failing_forms)
        report_hash = _persist_report(
            repository_root,
            report_path,
            report,
        )
        return CertificationOutcome(decision, report_hash, True)
    except Exception as exc:
        report = _report(CERTIFICATION_INVALID, aggregate, ("evidence_procedure",), (), ())
        report_hash = None
        if report_path_authorized:
            try:
                report_hash = _persist_report(
                    repository_root,
                    report_path,
                    report,
                )
            except Exception:
                report_hash = None
        return CertificationOutcome(
            CERTIFICATION_INVALID,
            report_hash,
            True,
            type(exc).__name__,
        )


__all__ = [
    "ACTIONS",
    "CANONICAL_PROJECTION_FIELDS",
    "CertificationOutcome",
    "DEFAULT_THRESHOLDS",
    "GOLD_FIELDS",
    "LANGUAGE_FORMS",
    "NUM_GROUPS",
    "NUM_MULTI_TURN",
    "NUM_REPEATS",
    "NUM_SAMPLES",
    "NUM_SCENARIOS",
    "SCORING_DIMENSIONS",
    "SEMANTIC_OUTCOMES",
    "BindingValidationError",
    "GoldValidationError",
    "MarkerError",
    "ReportError",
    "SchemaValidationError",
    "SealValidationError",
    "ShapeValidationError",
    "ValidationError",
    "canonical_json_bytes",
    "canonicalize_json",
    "run_certification",
    "validate_canonical_projection",
    "validate_evaluator_result",
    "validate_fixture_schema",
    "validate_fixture_shape",
    "validate_gold_cross_field_consistency",
    "validate_manifest_schema",
    "validate_report_schema",
    "validate_seal_schema",
    "validate_seal_state",
    "validate_source_bindings",
    "validate_threshold_schema",
]
