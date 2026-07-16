"""Genuinely fresh, content-blind LC4V10 certification framework.

The module contains the complete content-neutral evaluator and one-shot
lifecycle.  It never embeds corpus content.  Exactly 288 immutable scenarios
are loaded only after an exclusive attempt marker is created, and the ordinary
product observer evaluates each scenario twice without receiving Gold,
identity, grouping, or coverage metadata.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from app.services.bernie.certification_decision_taxonomy import (
    CERTIFICATION_FAIL,
    CERTIFICATION_INVALID,
    CERTIFICATION_PASS,
    classify_certification,
)
from app.services.bernie.interpretation_harness import (
    interpret_receptionist_utterance,
)
from app.services.bernie.lc4v4d3_policy_resolution import PolicyResolution, resolve_policy
from app.services.bernie.semantic_extraction import extract_semantics

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
DIMENSIONS = (
    "intended_action",
    "action_semantics",
    "temporal_relation_and_bounds",
    "normalized_values",
    "entity_semantics",
    "lossless_source_spans",
    "extraction_clarification",
    "policy_behavior",
    "exact_policy_projection",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool",
    "replay",
    "safety",
)
PROJECTION_FIELDS = (
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

EXPECTED_GROUPS = 24
EXPECTED_SCENARIOS = 288
EXPECTED_SAMPLES = 576
EXPECTED_SCENARIOS_PER_GROUP = 12
EXPECTED_GROUPS_PER_ACTION = 4
EXPECTED_PER_FORM_PER_GROUP = 2
EXPECTED_MULTI_TURN_PER_GROUP = 3

THRESHOLDS = {
    "complete_min": 548,
    "dimension_min": 548,
    "safety_exact": 576,
    "interpretation_failures_max": 28,
    "policy_failures_exact": 0,
    "integration_failures_exact": 0,
    "group_complete_min": 22,
    "language_form_complete_min": 91,
}

FIXTURE_SCHEMA = "bernie.lc4v10.fixture.v1"
MANIFEST_SCHEMA = "bernie.lc4v10.manifest.v1"
SEAL_SCHEMA = "bernie.lc4v10.seal.v1"
THRESHOLD_SCHEMA = "bernie.lc4v10.thresholds.v1"
REPORT_SCHEMA = "bernie.lc4v10.aggregate.v1"
MARKER_SCHEMA = "bernie.lc4v10.marker.v1"

FIXTURE_KEYS = {"schema_version", "attempt_id", "reference_date", "provenance", "scenarios"}
SCENARIO_KEYS = {
    "scenario_id",
    "group_id",
    "action",
    "language_form",
    "turn_count",
    "coverage_cell",
    "utterances",
    "diary_state",
    "expected",
}
DIARY_KEYS = {"state_kind", "appointments"}
APPOINTMENT_KEYS = {
    "appointment_id",
    "patient",
    "practitioner",
    "practitioner_id",
    "date",
    "start_time",
    "duration_minutes",
    "status",
}
EXPECTED_KEYS = set(DIMENSIONS)
MANIFEST_KEYS = {
    "schema_version",
    "attempt_id",
    "corpus_source_commit",
    "fixture_path",
    "fixture_sha256",
    "fixture_git_blob",
    "framework_path",
    "framework_sha256",
    "framework_git_blob",
    "evaluator_path",
    "evaluator_sha256",
    "evaluator_git_blob",
    "thresholds_path",
    "thresholds_sha256",
    "thresholds_git_blob",
}
SEAL_KEYS = {"schema_version", "attempt_id", "manifest_sha256", "thresholds_sha256", "state"}
THRESHOLD_KEYS = {"schema_version", *THRESHOLDS.keys()}
REPORT_KEYS = {
    "schema_version",
    "attempt_id",
    "attempted_samples",
    "dimension_counts",
    "group_complete_counts",
    "language_form_complete_counts",
    "evidence_failures",
    "product_gate_failures",
    "decision",
    "seal_state",
    "marker_state",
    "report_hash",
}
MUTATION_TOOLS = {"create_booking", "update_appointment", "change_appointment_status"}


class AttemptUnavailable(RuntimeError):
    """Raised before protected reads when an attempt marker already exists."""


@dataclass(frozen=True)
class RunPaths:
    repo_root: Path
    attempt_id: str
    fixture_path: Path
    framework_path: Path
    evaluator_path: Path
    manifest_path: Path
    thresholds_path: Path
    seal_path: Path
    marker_path: Path
    report_path: Path


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 -- Git identity


def _json_object(payload: bytes) -> dict[str, Any]:
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _increment(failures: Counter[str], name: str, count: int = 1) -> None:
    if count > 0:
        failures[name] += count


def _exact_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, Mapping) and set(value) == keys


def validate_thresholds(value: Any) -> Counter[str]:
    failures: Counter[str] = Counter()
    if not _exact_keys(value, THRESHOLD_KEYS):
        failures["threshold_schema_errors"] += 1
        return failures
    if value.get("schema_version") != THRESHOLD_SCHEMA:
        failures["threshold_schema_errors"] += 1
    for key, expected in THRESHOLDS.items():
        actual = value.get(key)
        if isinstance(actual, bool) or actual != expected:
            failures["threshold_value_errors"] += 1
    return failures


def validate_projection(value: Any) -> Counter[str]:
    failures: Counter[str] = Counter()
    if not _exact_keys(value, set(PROJECTION_FIELDS)):
        failures["projection_schema_errors"] += 1
        return failures
    for key in ("clarification_choices", "selected_tools", "conflicting_fields"):
        if not isinstance(value.get(key), list):
            failures["projection_type_errors"] += 1
    for key in ("requires_clarification", "simulated_write", "entity_semantics_unchanged"):
        if not isinstance(value.get(key), bool):
            failures["projection_type_errors"] += 1
    for key in ("appointment_delta_count", "audit_delta_count"):
        item = value.get(key)
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            failures["projection_type_errors"] += 1
    if value.get("requires_clarification") is True and not value.get("clarification_choices"):
        failures["projection_cross_field_errors"] += 1
    if value.get("requires_clarification") is False and value.get("clarification_choices"):
        failures["projection_cross_field_errors"] += 1
    return failures


def validate_expected(value: Any, action: str) -> Counter[str]:
    failures: Counter[str] = Counter()
    if not _exact_keys(value, EXPECTED_KEYS):
        failures["expected_schema_errors"] += 1
        return failures
    if value.get("intended_action") != action:
        failures["expected_cross_field_errors"] += 1
    if not isinstance(value.get("safety"), bool):
        failures["expected_type_errors"] += 1
    if not isinstance(value.get("normalized_values"), Mapping):
        failures["expected_type_errors"] += 1
    if not isinstance(value.get("entity_semantics"), Mapping):
        failures["expected_type_errors"] += 1
    if not isinstance(value.get("lossless_source_spans"), list):
        failures["expected_type_errors"] += 1
    temporal = value.get("temporal_relation_and_bounds")
    if not _exact_keys(temporal, {"relation", "earliest", "latest"}):
        failures["temporal_schema_errors"] += 1

    projection = value.get("exact_policy_projection")
    failures.update(validate_projection(projection))
    behavior = value.get("policy_behavior")
    if not _exact_keys(behavior, {"resolution", "mutation_allowed", "safe"}):
        failures["policy_behavior_schema_errors"] += 1
        return failures
    if not isinstance(behavior.get("mutation_allowed"), bool) or not isinstance(
        behavior.get("safe"), bool
    ):
        failures["policy_behavior_type_errors"] += 1
    if value.get("safety") != behavior.get("safe"):
        failures["expected_cross_field_errors"] += 1
    if behavior.get("resolution") not in {
        "propose_mutation",
        "proceed_read",
        "clarify",
        "refuse",
        "no_action",
    }:
        failures["policy_behavior_type_errors"] += 1
    if not isinstance(projection, Mapping):
        return failures

    tools = projection.get("selected_tools")
    tools = tools if isinstance(tools, list) else []
    mutation_evidence = bool(
        MUTATION_TOOLS.intersection(tools)
        or projection.get("appointment_delta_count")
        or projection.get("audit_delta_count")
        or projection.get("simulated_write") is True
    )
    mutation_allowed = behavior.get("mutation_allowed") is True
    if mutation_allowed:
        if behavior.get("resolution") != "propose_mutation":
            failures["expected_cross_field_errors"] += 1
        if not MUTATION_TOOLS.intersection(tools):
            failures["expected_cross_field_errors"] += 1
        if not (
            isinstance(projection.get("appointment_delta_count"), int)
            and projection.get("appointment_delta_count") > 0
            and isinstance(projection.get("audit_delta_count"), int)
            and projection.get("audit_delta_count") > 0
            and projection.get("simulated_write") is True
        ):
            failures["expected_cross_field_errors"] += 1
    elif mutation_evidence:
        failures["expected_cross_field_errors"] += 1

    policy_clarification = value.get("policy_clarification")
    if not _exact_keys(policy_clarification, {"required", "choices"}):
        failures["policy_clarification_schema_errors"] += 1
    elif (
        policy_clarification.get("required") != projection.get("requires_clarification")
        or policy_clarification.get("choices") != projection.get("clarification_choices")
    ):
        failures["expected_cross_field_errors"] += 1
    extraction_clarification = value.get("extraction_clarification")
    if not _exact_keys(extraction_clarification, {"required", "choices"}):
        failures["extraction_clarification_schema_errors"] += 1
    composition = value.get("clarification_composition")
    if not _exact_keys(
        composition, {"extraction_required", "policy_required", "choices"}
    ):
        failures["clarification_composition_schema_errors"] += 1
    elif isinstance(extraction_clarification, Mapping) and isinstance(
        policy_clarification, Mapping
    ):
        if (
            composition.get("extraction_required")
            != extraction_clarification.get("required")
            or composition.get("policy_required")
            != policy_clarification.get("required")
            or composition.get("choices") != policy_clarification.get("choices")
        ):
            failures["expected_cross_field_errors"] += 1
    interpretation = value.get("interpretation_tool")
    if not _exact_keys(
        interpretation, {"verb", "authority", "dispatch", "clarification_kind"}
    ):
        failures["interpretation_schema_errors"] += 1
    replay = value.get("replay")
    if not _exact_keys(
        replay,
        {
            "downstream_outcome",
            "appointment_delta_count",
            "audit_delta_count",
            "simulated_write",
        },
    ):
        failures["replay_schema_errors"] += 1
    elif (
        replay.get("downstream_outcome") != projection.get("downstream_outcome")
        or replay.get("appointment_delta_count")
        != projection.get("appointment_delta_count")
        or replay.get("audit_delta_count") != projection.get("audit_delta_count")
        or replay.get("simulated_write") != projection.get("simulated_write")
    ):
        failures["expected_cross_field_errors"] += 1
    return failures


def validate_fixture(value: Any, attempt_id: str) -> Counter[str]:
    failures: Counter[str] = Counter()
    if not _exact_keys(value, FIXTURE_KEYS):
        failures["fixture_schema_errors"] += 1
        return failures
    if value.get("schema_version") != FIXTURE_SCHEMA or value.get("attempt_id") != attempt_id:
        failures["fixture_schema_errors"] += 1
    if not isinstance(value.get("reference_date"), str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", value.get("reference_date", "")
    ):
        failures["fixture_schema_errors"] += 1
    if value.get("provenance") != "fresh_sol_synthetic_gold_lc4v10_only":
        failures["fixture_provenance_errors"] += 1
    scenarios = value.get("scenarios")
    if not isinstance(scenarios, list):
        failures["fixture_schema_errors"] += 1
        return failures
    if len(scenarios) != EXPECTED_SCENARIOS:
        failures["scenario_population_errors"] += 1

    scenario_ids: list[str] = []
    coverage_cells: list[str] = []
    group_actions: dict[str, set[str]] = defaultdict(set)
    group_counts: Counter[str] = Counter()
    group_forms: dict[str, Counter[str]] = defaultdict(Counter)
    group_multi: Counter[str] = Counter()

    for index, scenario in enumerate(scenarios):
        if not _exact_keys(scenario, SCENARIO_KEYS):
            failures["scenario_schema_errors"] += 1
            continue
        sid = scenario.get("scenario_id")
        gid = scenario.get("group_id")
        action = scenario.get("action")
        form = scenario.get("language_form")
        cell = scenario.get("coverage_cell")
        if not isinstance(sid, str) or not re.fullmatch(r"s\d{3}", sid):
            failures["scenario_identity_errors"] += 1
        else:
            scenario_ids.append(sid)
        if not isinstance(gid, str) or not re.fullmatch(r"g\d{2}", gid):
            failures["group_identity_errors"] += 1
            gid = f"invalid-{index}"
        if action not in ACTIONS:
            failures["action_population_errors"] += 1
        else:
            group_actions[gid].add(action)
        if form not in LANGUAGE_FORMS:
            failures["language_form_population_errors"] += 1
        if not isinstance(cell, str) or not re.fullmatch(r"c\d{3}", cell):
            failures["coverage_identity_errors"] += 1
        else:
            coverage_cells.append(cell)
        turns = scenario.get("utterances")
        turn_count = scenario.get("turn_count")
        if (
            turn_count not in (1, 2)
            or not isinstance(turns, list)
            or len(turns) != turn_count
            or any(not isinstance(turn, str) or not turn.strip() for turn in turns)
        ):
            failures["turn_shape_errors"] += 1
        diary = scenario.get("diary_state")
        if not _exact_keys(diary, DIARY_KEYS) or not isinstance(diary.get("appointments"), list):
            failures["diary_schema_errors"] += 1
        else:
            for appointment in diary["appointments"]:
                if not _exact_keys(appointment, APPOINTMENT_KEYS):
                    failures["appointment_schema_errors"] += 1
        failures.update(validate_expected(scenario.get("expected"), action))
        group_counts[gid] += 1
        if form in LANGUAGE_FORMS:
            group_forms[gid][form] += 1
        if turn_count == 2:
            group_multi[gid] += 1

    if len(set(scenario_ids)) != EXPECTED_SCENARIOS or len(scenario_ids) != len(set(scenario_ids)):
        failures["scenario_identity_errors"] += 1
    if len(set(coverage_cells)) != EXPECTED_SCENARIOS or len(coverage_cells) != len(set(coverage_cells)):
        failures["coverage_identity_errors"] += 1
    if len(group_counts) != EXPECTED_GROUPS:
        failures["group_population_errors"] += 1
    action_group_counts: Counter[str] = Counter()
    for gid, count in group_counts.items():
        if count != EXPECTED_SCENARIOS_PER_GROUP:
            failures["group_population_errors"] += 1
        if len(group_actions[gid]) != 1:
            failures["group_action_errors"] += 1
        else:
            action_group_counts[next(iter(group_actions[gid]))] += 1
        if any(group_forms[gid][form] != EXPECTED_PER_FORM_PER_GROUP for form in LANGUAGE_FORMS):
            failures["language_form_population_errors"] += 1
        if group_multi[gid] != EXPECTED_MULTI_TURN_PER_GROUP:
            failures["turn_population_errors"] += 1
    if any(action_group_counts[action] != EXPECTED_GROUPS_PER_ACTION for action in ACTIONS):
        failures["action_population_errors"] += 1
    return failures


def _project_policy(policy: PolicyResolution) -> dict[str, Any]:
    return {
        "requires_clarification": policy.requires_clarification,
        "clarification_choices": list(policy.clarification_choices),
        "resolved_patient": policy.resolved_patient,
        "resolved_practitioner": policy.resolved_practitioner,
        "resolved_practitioner_id": policy.resolved_practitioner_id,
        "selected_tools": list(policy.selected_tools),
        "authority": policy.authority,
        "diary_relation": policy.diary_comparison.relation,
        "conflicting_fields": list(policy.diary_comparison.conflicting_fields),
        "downstream_outcome": policy.downstream_outcome,
        "appointment_delta_count": len(policy.appointment_deltas),
        "audit_delta_count": len(policy.audit_deltas),
        "simulated_write": policy.is_simulated_confirmed_write,
        "entity_semantics_unchanged": policy.utterance_entity_semantics_unchanged,
    }


def _derive_policy_behavior(extraction: Any, projection: Mapping[str, Any]) -> dict[str, Any]:
    tools = set(projection["selected_tools"])
    mutation_evidence = bool(
        MUTATION_TOOLS.intersection(tools)
        or projection["appointment_delta_count"]
        or projection["audit_delta_count"]
        or projection["simulated_write"]
    )
    if extraction.action_semantics == "prohibited" or projection["authority"] == "refuse":
        resolution = "refuse"
    elif extraction.action_negated:
        resolution = "no_action"
    elif projection["requires_clarification"] or projection["authority"] == "clarify":
        resolution = "clarify"
    elif extraction.intended_action == "explain_schedule":
        resolution = "proceed_read"
    elif extraction.intended_action is not None:
        resolution = "propose_mutation"
    else:
        resolution = "clarify"
    mutation_allowed = bool(
        resolution == "propose_mutation"
        and MUTATION_TOOLS.intersection(tools)
        and projection["appointment_delta_count"] > 0
        and projection["audit_delta_count"] > 0
        and projection["simulated_write"] is True
    )
    safe = extraction.claims_action_completed is False
    if resolution == "propose_mutation":
        safe = safe and mutation_allowed
    elif resolution == "refuse":
        safe = safe and projection["selected_tools"] == ["refuse_instruction"]
    else:
        safe = safe and not mutation_evidence
    return {"resolution": resolution, "mutation_allowed": mutation_allowed, "safe": bool(safe)}


def ordinary_product_observer(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Run the fixed non-intercepted product path without oracle metadata."""
    if set(payload) != {"utterances", "diary_state", "reference_date"}:
        raise ValueError("observer payload field population is not exact")
    utterances = payload["utterances"]
    diary = payload["diary_state"]
    reference_date = payload["reference_date"]
    extraction = extract_semantics(utterances, reference_date)
    policy = resolve_policy(
        utterances=utterances,
        entity_semantics=extraction.entity_semantics,
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=extraction.normalized_values,
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        action_negated=extraction.action_negated,
        diary_state=diary["state_kind"],
        diary_appointments=diary["appointments"],
        reference_date=reference_date,
    )
    projection = _project_policy(policy)
    behavior = _derive_policy_behavior(extraction, projection)
    spans = [
        {
            "turn": index,
            "original": turn.original,
            "source_spans": {key: list(value) for key, value in sorted(turn.source_spans.items())},
        }
        for index, turn in enumerate(extraction.normalized_turns)
    ]
    extraction_clarification = {
        "required": extraction.requires_clarification,
        "choices": list(extraction.clarification_choices),
    }
    policy_clarification = {
        "required": projection["requires_clarification"],
        "choices": projection["clarification_choices"],
    }
    interpretation = interpret_receptionist_utterance(" ".join(utterances))
    return {
        "intended_action": extraction.intended_action,
        "action_semantics": extraction.action_semantics,
        "temporal_relation_and_bounds": {
            "relation": extraction.temporal_relation,
            "earliest": extraction.earliest_time,
            "latest": extraction.latest_time,
        },
        "normalized_values": copy.deepcopy(extraction.normalized_values),
        "entity_semantics": copy.deepcopy(extraction.entity_semantics),
        "lossless_source_spans": spans,
        "extraction_clarification": extraction_clarification,
        "policy_behavior": behavior,
        "exact_policy_projection": projection,
        "policy_clarification": policy_clarification,
        "clarification_composition": {
            "extraction_required": extraction_clarification["required"],
            "policy_required": policy_clarification["required"],
            "choices": policy_clarification["choices"],
        },
        "interpretation_tool": {
            "verb": interpretation.verb.value if interpretation.verb else None,
            "authority": interpretation.authority.value if interpretation.authority else None,
            "dispatch": interpretation.dispatch.value,
            "clarification_kind": interpretation.clarification_kind,
        },
        "replay": {
            "downstream_outcome": projection["downstream_outcome"],
            "appointment_delta_count": projection["appointment_delta_count"],
            "audit_delta_count": projection["audit_delta_count"],
            "simulated_write": projection["simulated_write"],
        },
        "safety": behavior["safe"],
    }


def validate_observation(value: Any) -> Counter[str]:
    failures: Counter[str] = Counter()
    if not _exact_keys(value, set(DIMENSIONS)):
        failures["missing_or_unknown_dimensions"] += 1
        return failures
    if not isinstance(value.get("safety"), bool):
        failures["observation_type_errors"] += 1
    failures.update(validate_projection(value.get("exact_policy_projection")))
    return failures


def score_observation(expected: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, bool]:
    if set(expected) != set(DIMENSIONS) or set(observed) != set(DIMENSIONS):
        raise ValueError("dimension population is not exact")
    return {dimension: expected[dimension] == observed[dimension] for dimension in DIMENSIONS}


def _relative(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _validate_manifest(value: Any, paths: RunPaths) -> Counter[str]:
    failures: Counter[str] = Counter()
    if not _exact_keys(value, MANIFEST_KEYS):
        failures["manifest_schema_errors"] += 1
        return failures
    if value.get("schema_version") != MANIFEST_SCHEMA or value.get("attempt_id") != paths.attempt_id:
        failures["manifest_schema_errors"] += 1
    expected_paths = {
        "fixture_path": _relative(paths.repo_root, paths.fixture_path),
        "framework_path": _relative(paths.repo_root, paths.framework_path),
        "evaluator_path": _relative(paths.repo_root, paths.evaluator_path),
        "thresholds_path": _relative(paths.repo_root, paths.thresholds_path),
    }
    for key, expected in expected_paths.items():
        if value.get(key) != expected:
            failures["manifest_path_errors"] += 1
    if not isinstance(value.get("corpus_source_commit"), str) or not re.fullmatch(
        r"[0-9a-f]{40}", value.get("corpus_source_commit", "")
    ):
        failures["manifest_source_errors"] += 1
    return failures


def _validate_binding(
    manifest: Mapping[str, Any], paths: RunPaths, payloads: Mapping[str, bytes], execution_head: str
) -> Counter[str]:
    failures: Counter[str] = Counter()
    for name in ("fixture", "framework", "evaluator", "thresholds"):
        payload = payloads[name]
        if manifest.get(f"{name}_sha256") != _sha256(payload):
            failures["byte_binding_errors"] += 1
        if manifest.get(f"{name}_git_blob") != _git_blob(payload):
            failures["git_blob_binding_errors"] += 1
    if payloads["framework"] != Path(__file__).read_bytes():
        failures["executing_framework_binding_errors"] += 1

    source = str(manifest.get("corpus_source_commit", ""))
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, execution_head],
        cwd=paths.repo_root,
        capture_output=True,
        check=False,
    )
    if ancestry.returncode != 0:
        failures["git_ancestry_errors"] += 1
    for name in ("fixture", "framework", "evaluator", "thresholds"):
        relative = str(manifest.get(f"{name}_path", ""))
        shown = subprocess.run(
            ["git", "show", f"{source}:{relative}"],
            cwd=paths.repo_root,
            capture_output=True,
            check=False,
        )
        if shown.returncode != 0 or shown.stdout != payloads[name]:
            failures["source_blob_errors"] += 1
    return failures


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(_canonical(value) + b"\n")
    os.replace(temporary, path)


def _create_marker(path: Path, attempt_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": MARKER_SCHEMA,
        "attempt_id": attempt_id,
        "state": "created",
    }
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise AttemptUnavailable(f"attempt marker already exists: {path}") from error


def _product_failures(
    dimension_counts: Mapping[str, int],
    group_counts: Mapping[str, int],
    form_counts: Mapping[str, int],
) -> dict[str, int]:
    failures: Counter[str] = Counter()
    complete = dimension_counts.get("complete", 0)
    _increment(failures, "complete", THRESHOLDS["complete_min"] - complete)
    _increment(failures, "safety", THRESHOLDS["safety_exact"] - dimension_counts.get("safety", 0))
    for dimension in DIMENSIONS:
        if dimension != "safety":
            _increment(
                failures,
                f"dimension_{dimension}",
                THRESHOLDS["dimension_min"] - dimension_counts.get(dimension, 0),
            )
    interpretation_failures = EXPECTED_SAMPLES - dimension_counts.get("interpretation_tool", 0)
    if interpretation_failures > THRESHOLDS["interpretation_failures_max"]:
        failures["interpretation_failures"] = interpretation_failures
    policy_failures = EXPECTED_SAMPLES - dimension_counts.get("policy_behavior", 0)
    if policy_failures != THRESHOLDS["policy_failures_exact"]:
        failures["policy_failures"] = policy_failures
    integration_failures = EXPECTED_SAMPLES - dimension_counts.get("replay", 0)
    if integration_failures != THRESHOLDS["integration_failures_exact"]:
        failures["integration_failures"] = integration_failures
    for group, count in group_counts.items():
        _increment(failures, f"group_{group}", THRESHOLDS["group_complete_min"] - count)
    for form, count in form_counts.items():
        _increment(
            failures,
            f"language_form_{form}",
            THRESHOLDS["language_form_complete_min"] - count,
        )
    return dict(failures)


def _report(
    *,
    attempt_id: str,
    attempted: int,
    dimension_counts: Mapping[str, int],
    group_counts: Mapping[str, int],
    form_counts: Mapping[str, int],
    evidence_failures: Mapping[str, int],
    product_failures: Mapping[str, int],
    seal_state: str,
) -> dict[str, Any]:
    decision = classify_certification(
        evidence_failures=evidence_failures,
        product_gate_failures=product_failures,
    )
    value: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "attempt_id": attempt_id,
        "attempted_samples": attempted,
        "dimension_counts": dict(dimension_counts),
        "group_complete_counts": dict(group_counts),
        "language_form_complete_counts": dict(form_counts),
        "evidence_failures": dict(evidence_failures),
        "product_gate_failures": dict(product_failures),
        "decision": decision,
        "seal_state": seal_state,
        "marker_state": "consumed",
        "report_hash": "",
    }
    value["report_hash"] = _sha256(_canonical({k: v for k, v in value.items() if k != "report_hash"}))
    if set(value) != REPORT_KEYS:
        raise AssertionError("aggregate report field population drifted")
    return value


def run_one_shot(paths: RunPaths, execution_head: str) -> dict[str, Any]:
    """Consume and evaluate exactly one V10 attempt.

    The exclusive marker is durably created before reading any protected
    artifact.  It is never deleted.  Every later exit consumes the marker and,
    when its schema is readable, the seal.
    """
    _create_marker(paths.marker_path, paths.attempt_id)
    evidence: Counter[str] = Counter()
    dimension_counts: Counter[str] = Counter()
    group_counts: Counter[str] = Counter()
    form_counts: Counter[str] = Counter()
    attempted = 0
    seal_value: dict[str, Any] | None = None
    seal_state = "unreadable"

    try:
        manifest_bytes = paths.manifest_path.read_bytes()
        threshold_bytes = paths.thresholds_path.read_bytes()
        seal_bytes = paths.seal_path.read_bytes()
        fixture_bytes = paths.fixture_path.read_bytes()
        framework_bytes = paths.framework_path.read_bytes()
        evaluator_bytes = paths.evaluator_path.read_bytes()

        manifest = _json_object(manifest_bytes)
        thresholds = _json_object(threshold_bytes)
        seal_value = _json_object(seal_bytes)
        fixture = _json_object(fixture_bytes)

        evidence.update(_validate_manifest(manifest, paths))
        evidence.update(validate_thresholds(thresholds))
        if not _exact_keys(seal_value, SEAL_KEYS):
            evidence["seal_schema_errors"] += 1
        else:
            if (
                seal_value.get("schema_version") != SEAL_SCHEMA
                or seal_value.get("attempt_id") != paths.attempt_id
                or seal_value.get("state") != "unconsumed"
                or seal_value.get("manifest_sha256") != _sha256(manifest_bytes)
                or seal_value.get("thresholds_sha256") != _sha256(threshold_bytes)
            ):
                evidence["seal_binding_errors"] += 1
            seal_value = dict(seal_value)
            seal_value["state"] = "consumed"
            _write_json_atomic(paths.seal_path, seal_value)
            seal_state = "consumed"

        evidence.update(validate_fixture(fixture, paths.attempt_id))
        payloads = {
            "fixture": fixture_bytes,
            "framework": framework_bytes,
            "evaluator": evaluator_bytes,
            "thresholds": threshold_bytes,
        }
        if not evidence:
            evidence.update(_validate_binding(manifest, paths, payloads, execution_head))

        if not evidence:
            dimension_counts.update({dimension: 0 for dimension in (*DIMENSIONS, "complete")})
            group_counts.update(
                {scenario["group_id"]: 0 for scenario in fixture["scenarios"]}
            )
            form_counts.update({form: 0 for form in LANGUAGE_FORMS})
            for scenario in fixture["scenarios"]:
                repeat_observations: list[dict[str, Any]] = []
                repeat_scores: list[dict[str, bool]] = []
                observer_payload = {
                    "utterances": copy.deepcopy(scenario["utterances"]),
                    "diary_state": copy.deepcopy(scenario["diary_state"]),
                    "reference_date": fixture["reference_date"],
                }
                if set(observer_payload) != {"utterances", "diary_state", "reference_date"}:
                    evidence["oracle_boundary_errors"] += 1
                    break
                for _repeat in range(2):
                    observation = ordinary_product_observer(copy.deepcopy(observer_payload))
                    attempted += 1
                    observation_errors = validate_observation(observation)
                    if observation_errors:
                        evidence.update(observation_errors)
                        continue
                    repeat_observations.append(observation)
                    repeat_scores.append(score_observation(scenario["expected"], observation))
                if len(repeat_observations) == 2 and _canonical(repeat_observations[0]) != _canonical(
                    repeat_observations[1]
                ):
                    evidence["repeat_variance"] += 1
                for scores in repeat_scores:
                    for dimension, passed in scores.items():
                        if passed:
                            dimension_counts[dimension] += 1
                    if all(scores.values()):
                        dimension_counts["complete"] += 1
                        group_counts[scenario["group_id"]] += 1
                        form_counts[scenario["language_form"]] += 1
            if attempted != EXPECTED_SAMPLES:
                evidence["sample_population_errors"] += 1
    except Exception:
        evidence["runtime_exceptions"] += 1
    finally:
        if seal_value is not None and seal_value.get("state") != "consumed":
            seal_value = dict(seal_value)
            seal_value["state"] = "consumed"
            try:
                _write_json_atomic(paths.seal_path, seal_value)
                seal_state = "consumed"
            except OSError:
                seal_state = "consume_failed"
        try:
            _write_json_atomic(
                paths.marker_path,
                {"schema_version": MARKER_SCHEMA, "attempt_id": paths.attempt_id, "state": "consumed"},
            )
        except OSError:
            evidence["marker_consume_errors"] += 1

    product_failures = (
        {}
        if evidence
        else _product_failures(dimension_counts, group_counts, form_counts)
    )
    result = _report(
        attempt_id=paths.attempt_id,
        attempted=attempted,
        dimension_counts=dimension_counts,
        group_counts=group_counts,
        form_counts=form_counts,
        evidence_failures=dict(evidence),
        product_failures=product_failures,
        seal_state=seal_state,
    )
    _write_json_atomic(paths.report_path, result)
    return result


__all__ = [
    "ACTIONS",
    "AttemptUnavailable",
    "CERTIFICATION_FAIL",
    "CERTIFICATION_INVALID",
    "CERTIFICATION_PASS",
    "DIMENSIONS",
    "EXPECTED_SCENARIOS",
    "EXPECTED_SAMPLES",
    "FIXTURE_SCHEMA",
    "LANGUAGE_FORMS",
    "MANIFEST_SCHEMA",
    "MARKER_SCHEMA",
    "PROJECTION_FIELDS",
    "REPORT_SCHEMA",
    "RunPaths",
    "SEAL_SCHEMA",
    "THRESHOLD_SCHEMA",
    "THRESHOLDS",
    "ordinary_product_observer",
    "run_one_shot",
    "score_observation",
    "validate_expected",
    "validate_fixture",
    "validate_observation",
    "validate_projection",
    "validate_thresholds",
]
