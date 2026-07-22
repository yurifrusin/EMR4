#!/usr/bin/env python3
"""Run the finite, authored-synthetic Ariadne work-cell rehearsal in memory."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_bounded_cognitive_work_cell as work_cell
except ModuleNotFoundError:  # pragma: no cover - direct script invocation
    import ariadne_bounded_cognitive_work_cell as work_cell


SCHEMA_VERSION = "ariadne.scripted_cognitive_work_cell_rehearsal.v1"
EVIDENCE_VERSION = "ariadne.scripted_cognitive_work_cell_rehearsal_evidence.v1"
RESULT = "ariadne_scripted_cognitive_work_cell_rehearsal_pass"
DEFAULT_SCRIPT_RELATIVE = Path(
    "orchestration/continuity/"
    "ariadne-scripted-cognitive-work-cell-rehearsal-example.json"
)
DEFAULT_PROTOCOL_RELATIVE = Path(
    "orchestration/continuity/ariadne-bounded-cognitive-work-cell-example.json"
)

ALLOWED_ACTIONS = (
    "submit-attempt",
    "verify-drafts",
    "apply-verdict-disposition",
    "record-verified-release",
    "record-human-gate-delivery",
    "record-bounded-correction-request",
    "bind-inert-fresh-read-grant",
    "supersede-declared-attempt",
    "reject-stale-completion",
    "abort-declared-edge",
    "finish-scenario",
)

HARD_LIMITS = {
    "max_scenarios": 8,
    "max_steps_per_scenario": 32,
    "max_total_steps": 256,
}

REQUIRED_CLOSED_CONNECTIONS = frozenset(
    {
        *work_cell.REQUIRED_CLOSED_BOUNDARIES,
        "adaptive-agent",
        "concurrency",
        "filesystem-write",
        "network",
        "persistence",
        "subprocess",
        "thread-timer-scheduler",
    }
)

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "rehearsal_id",
        "revision",
        "title",
        "as_of",
        "source_protocol",
        "authority",
        "limits",
        "step_vocabulary",
        "scenarios",
        "evidence",
    }
)

BASE_STEP_FIELDS = frozenset(
    {"sequence", "action", "from_state", "to_state"}
)
ACTION_REQUIRED_FIELDS = {
    "submit-attempt": frozenset({"attempt_id"}),
    "verify-drafts": frozenset(
        {"verification_case_id", "expected_disposition"}
    ),
    "apply-verdict-disposition": frozenset({"expected_disposition"}),
    "record-verified-release": frozenset({"draft_ids"}),
    "record-human-gate-delivery": frozenset({"draft_ids"}),
    "record-bounded-correction-request": frozenset({"draft_ids"}),
    "bind-inert-fresh-read-grant": frozenset({"fresh_read_grant_id"}),
    "supersede-declared-attempt": frozenset({"retry_trace_id"}),
    "reject-stale-completion": frozenset({"retry_trace_id"}),
    "abort-declared-edge": frozenset({"draft_ids"}),
    "finish-scenario": frozenset(),
}
ACTION_OPTIONAL_FIELDS = {
    "record-bounded-correction-request": frozenset(
        {"retry_trace_id", "expected_to_attempt_id"}
    )
}

ALLOWED_STATE_TRANSITIONS = {
    "submit-attempt": {
        ("ready", "attempt-submitted"),
        ("correction-requested", "attempt-submitted"),
    },
    "verify-drafts": {("attempt-submitted", "verdict-computed")},
    "apply-verdict-disposition": {
        ("verdict-computed", "disposition-applied")
    },
    "record-verified-release": {
        ("disposition-applied", "release-recorded")
    },
    "record-human-gate-delivery": {
        ("release-recorded", "human-gate-recorded")
    },
    "record-bounded-correction-request": {
        ("disposition-applied", "correction-requested")
    },
    "bind-inert-fresh-read-grant": {
        ("disposition-applied", "fresh-read-grant-bound")
    },
    "supersede-declared-attempt": {
        ("fresh-read-grant-bound", "attempt-superseded")
    },
    "reject-stale-completion": {
        ("attempt-superseded", "stale-completion-rejected")
    },
    "abort-declared-edge": {("disposition-applied", "edge-aborted")},
    "finish-scenario": {
        ("release-recorded", "completed"),
        ("human-gate-recorded", "awaiting-human-authority"),
        ("edge-aborted", "aborted"),
        ("stale-completion-rejected", "awaiting-fresh-context"),
        ("correction-requested", "correction-requested"),
    },
}

ACTIVE_ACTUATOR_KEYS = frozenset(
    {
        "callback",
        "command",
        "condition",
        "container_image",
        "credential",
        "delay",
        "dsn",
        "endpoint",
        "goto",
        "loop",
        "model",
        "mutation",
        "provider",
        "query",
        "secret",
        "sleep",
        "thread",
        "timer",
        "topic",
        "url",
    }
)


class ScriptedRehearsalError(ValueError):
    """Raised when the finite rehearsal tape fails closed."""


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def canonical_sha256(payload: Any) -> str:
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def default_script_path(repo_root: Path) -> Path:
    return repo_root / DEFAULT_SCRIPT_RELATIVE


def default_protocol_path(repo_root: Path) -> Path:
    return repo_root / DEFAULT_PROTOCOL_RELATIVE


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ScriptedRehearsalError(f"document_unreadable:{path.name}") from error
    if not isinstance(payload, dict):
        raise ScriptedRehearsalError(f"document_must_be_object:{path.name}")
    return payload


def _index(
    items: Any, *, label: str
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if not isinstance(items, list):
        return {}, [f"{label}_collection_must_be_array"]
    result: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append(f"{label}_must_have_string_id")
            continue
        item_id = item["id"]
        if item_id in result:
            errors.append(f"{label}_duplicate:{item_id}")
        result[item_id] = item
    return result, errors


def _active_actuator_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key.lower() in ACTIVE_ACTUATOR_KEYS and child not in (
                None,
                False,
                "",
                [],
                {},
            ):
                errors.append(f"active_actuator_field_forbidden:{child_path}")
            errors.extend(_active_actuator_errors(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_active_actuator_errors(child, f"{path}[{index}]"))
    return errors


def _protocol_context(
    protocol: dict[str, Any], *, repo_root: Path
) -> tuple[dict[str, Any], list[str]]:
    errors = work_cell.validate_document(protocol, repo_root=repo_root)
    attempts, attempt_errors = _index(
        protocol.get("work_cell_attempts", []), label="protocol_attempt"
    )
    drafts, draft_errors = _index(
        protocol.get("draft_frames", []), label="protocol_draft"
    )
    cases, case_errors = _index(
        protocol.get("verification_cases", []), label="protocol_case"
    )
    traces, trace_errors = _index(
        protocol.get("retry_traces", []), label="protocol_retry_trace"
    )
    grants, grant_errors = _index(
        protocol.get("fresh_read_grants", []), label="protocol_fresh_read_grant"
    )
    errors.extend(
        attempt_errors + draft_errors + case_errors + trace_errors + grant_errors
    )
    verification_by_case: dict[str, dict[str, Any]] = {}
    if not errors:
        verification = work_cell.build_verification(
            protocol, repo_root=repo_root
        )
        verification_by_case = {
            item["case_id"]: item for item in verification["case_results"]
        }
    return {
        "attempts": attempts,
        "drafts": drafts,
        "cases": cases,
        "traces": traces,
        "grants": grants,
        "verification_by_case": verification_by_case,
    }, errors


def _step_field_errors(step: Any, scenario_id: str) -> list[str]:
    if not isinstance(step, dict):
        return [f"step_must_be_object:{scenario_id}"]
    action = step.get("action")
    if action not in ALLOWED_ACTIONS:
        return [f"step_action_unknown:{scenario_id}:{action}"]
    required = BASE_STEP_FIELDS | ACTION_REQUIRED_FIELDS[action]
    allowed = required | ACTION_OPTIONAL_FIELDS.get(action, frozenset())
    missing = sorted(required - set(step))
    unknown = sorted(set(step) - allowed)
    errors = [f"step_field_missing:{scenario_id}:{action}:{name}" for name in missing]
    errors.extend(
        f"step_field_unknown:{scenario_id}:{action}:{name}" for name in unknown
    )
    if (step.get("from_state"), step.get("to_state")) not in (
        ALLOWED_STATE_TRANSITIONS.get(action, set())
    ):
        errors.append(
            "step_state_transition_forbidden:"
            f"{scenario_id}:{action}:{step.get('from_state')}:{step.get('to_state')}"
        )
    return errors


def _draft_ids(step: dict[str, Any], scenario_id: str) -> tuple[set[str], list[str]]:
    values = step.get("draft_ids")
    if not isinstance(values, list) or not values or not all(
        isinstance(item, str) for item in values
    ):
        return set(), [f"step_draft_ids_invalid:{scenario_id}:{step.get('sequence')}" ]
    if len(values) != len(set(values)):
        return set(values), [
            f"step_draft_ids_duplicate:{scenario_id}:{step.get('sequence')}"
        ]
    return set(values), []


def _validate_scenario(
    scenario: Any,
    *,
    context: dict[str, Any],
    max_steps: int,
) -> list[str]:
    if not isinstance(scenario, dict):
        return ["scenario_must_be_object"]
    scenario_id = scenario.get("id", "unknown")
    required_fields = {
        "id",
        "purpose_code",
        "initial_state",
        "terminal_state",
        "steps",
    }
    errors: list[str] = []
    if set(scenario) != required_fields:
        for name in sorted(required_fields - set(scenario)):
            errors.append(f"scenario_field_missing:{scenario_id}:{name}")
        for name in sorted(set(scenario) - required_fields):
            errors.append(f"scenario_field_unknown:{scenario_id}:{name}")
    if not isinstance(scenario_id, str) or not scenario_id:
        errors.append("scenario_id_invalid")
    if scenario.get("initial_state") != "ready":
        errors.append(f"scenario_initial_state_invalid:{scenario_id}")
    steps = scenario.get("steps")
    if not isinstance(steps, list) or not steps:
        return errors + [f"scenario_steps_invalid:{scenario_id}"]
    if len(steps) > max_steps:
        errors.append(f"scenario_step_limit_exceeded:{scenario_id}")

    attempts = context["attempts"]
    cases = context["cases"]
    traces = context["traces"]
    grants = context["grants"]
    verification_by_case = context["verification_by_case"]

    expected_state = scenario.get("initial_state")
    current_attempt_id: str | None = None
    submitted_attempts: set[str] = set()
    current_case: dict[str, Any] | None = None
    current_result: dict[str, Any] | None = None
    disposition_applied = False
    expected_retry_target: str | None = None
    bound_grant_id: str | None = None
    supersession_trace_id: str | None = None

    for index, step in enumerate(steps, start=1):
        errors.extend(_step_field_errors(step, str(scenario_id)))
        if not isinstance(step, dict):
            continue
        action = step.get("action")
        if step.get("sequence") != index:
            errors.append(f"step_sequence_invalid:{scenario_id}:{index}")
        if step.get("from_state") != expected_state:
            errors.append(
                f"step_state_chain_broken:{scenario_id}:{index}:{expected_state}"
            )
        expected_state = step.get("to_state")

        if action == "submit-attempt":
            attempt_id = step.get("attempt_id")
            attempt = attempts.get(attempt_id)
            if attempt is None:
                errors.append(f"attempt_unknown:{scenario_id}:{attempt_id}")
            if attempt_id in submitted_attempts:
                errors.append(f"attempt_repeated:{scenario_id}:{attempt_id}")
            if expected_retry_target is not None and attempt_id != expected_retry_target:
                errors.append(
                    f"retry_target_mismatch:{scenario_id}:{attempt_id}:{expected_retry_target}"
                )
            if current_attempt_id is not None and expected_retry_target is None:
                errors.append(f"attempt_without_declared_retry:{scenario_id}:{attempt_id}")
            current_attempt_id = attempt_id
            submitted_attempts.add(attempt_id)
            expected_retry_target = None
            current_case = None
            current_result = None
            disposition_applied = False

        elif action == "verify-drafts":
            case_id = step.get("verification_case_id")
            current_case = cases.get(case_id)
            current_result = verification_by_case.get(case_id)
            if current_attempt_id is None:
                errors.append(f"verify_without_attempt:{scenario_id}:{case_id}")
            elif current_case is None or current_result is None:
                errors.append(f"verification_case_unknown:{scenario_id}:{case_id}")
            else:
                attempt = attempts.get(current_attempt_id, {})
                if set(current_case.get("draft_ids", [])) != set(
                    attempt.get("emitted_draft_ids", [])
                ):
                    errors.append(
                        f"case_attempt_draft_mismatch:{scenario_id}:{case_id}:{current_attempt_id}"
                    )
                if step.get("expected_disposition") != current_result.get(
                    "disposition"
                ):
                    errors.append(
                        f"proofreader_disposition_override:{scenario_id}:{case_id}"
                    )
            disposition_applied = False

        elif action == "apply-verdict-disposition":
            if current_result is None:
                errors.append(f"apply_without_verdict:{scenario_id}:{index}")
            elif step.get("expected_disposition") != current_result.get(
                "disposition"
            ):
                errors.append(
                    f"applied_disposition_mismatch:{scenario_id}:{index}"
                )
            disposition_applied = True

        elif action == "record-verified-release":
            ids, id_errors = _draft_ids(step, str(scenario_id))
            errors.extend(id_errors)
            if not disposition_applied or current_result is None:
                errors.append(f"release_without_applied_verdict:{scenario_id}:{index}")
            else:
                expected_ids = {
                    edge["source_draft_id"]
                    for edge in current_result.get("released_edges", [])
                }
                if ids != expected_ids:
                    errors.append(f"release_set_mismatch:{scenario_id}:{index}")

        elif action == "record-human-gate-delivery":
            ids, id_errors = _draft_ids(step, str(scenario_id))
            errors.extend(id_errors)
            if current_result is None:
                errors.append(f"human_gate_without_verdict:{scenario_id}:{index}")
            else:
                expected_ids = {
                    edge["source_draft_id"]
                    for edge in current_result.get("released_edges", [])
                    if edge["kind"] == "verified-human-gate-frame"
                }
                if ids != expected_ids or not ids:
                    errors.append(f"human_gate_set_mismatch:{scenario_id}:{index}")

        elif action == "record-bounded-correction-request":
            ids, id_errors = _draft_ids(step, str(scenario_id))
            errors.extend(id_errors)
            if (
                not disposition_applied
                or current_result is None
                or current_result.get("disposition") != "request-new-attempt"
            ):
                errors.append(
                    f"correction_request_without_retry_verdict:{scenario_id}:{index}"
                )
            elif current_case is not None and ids != set(
                current_case.get("draft_ids", [])
            ):
                errors.append(f"correction_request_set_mismatch:{scenario_id}:{index}")
            trace_id = step.get("retry_trace_id")
            target_id = step.get("expected_to_attempt_id")
            if trace_id is not None or target_id is not None:
                trace = traces.get(trace_id)
                if trace is None:
                    errors.append(f"retry_trace_unknown:{scenario_id}:{trace_id}")
                elif (
                    trace.get("from_attempt_id") != current_attempt_id
                    or trace.get("to_attempt_id") != target_id
                ):
                    errors.append(f"retry_trace_lineage_mismatch:{scenario_id}:{trace_id}")
                else:
                    target = attempts.get(str(target_id), {})
                    if target.get("retry_of") != current_attempt_id:
                        errors.append(
                            f"retry_attempt_lineage_mismatch:{scenario_id}:{target_id}"
                        )
                    expected_retry_target = str(target_id)

        elif action == "bind-inert-fresh-read-grant":
            grant_id = step.get("fresh_read_grant_id")
            grant = grants.get(grant_id)
            if (
                not disposition_applied
                or current_result is None
                or current_result.get("disposition") != "fresh-read-and-supersede"
            ):
                errors.append(f"grant_without_stale_verdict:{scenario_id}:{index}")
            if grant is None:
                errors.append(f"fresh_read_grant_unknown:{scenario_id}:{grant_id}")
            elif grant.get("execution_enabled") is not False or grant.get(
                "returns_data"
            ) is not False:
                errors.append(f"fresh_read_grant_not_inert:{scenario_id}:{grant_id}")
            bound_grant_id = grant_id

        elif action == "supersede-declared-attempt":
            trace_id = step.get("retry_trace_id")
            trace = traces.get(trace_id)
            if trace is None:
                errors.append(f"supersession_trace_unknown:{scenario_id}:{trace_id}")
            elif (
                trace.get("kind") != "fresh-context-supersession"
                or trace.get("from_attempt_id") != current_attempt_id
                or trace.get("fresh_read_grant_id") != bound_grant_id
            ):
                errors.append(f"supersession_lineage_mismatch:{scenario_id}:{trace_id}")
            else:
                target_id = trace.get("to_attempt_id")
                target = attempts.get(target_id, {})
                if target.get("superseded_from") != current_attempt_id:
                    errors.append(
                        f"supersession_attempt_mismatch:{scenario_id}:{target_id}"
                    )
                current_attempt_id = target_id
                supersession_trace_id = trace_id

        elif action == "reject-stale-completion":
            trace_id = step.get("retry_trace_id")
            trace = traces.get(trace_id)
            if trace_id != supersession_trace_id or trace is None:
                errors.append(f"stale_rejection_trace_mismatch:{scenario_id}:{trace_id}")
            elif trace.get("stale_completion_disposition") != (
                "rejected-stale-generation"
            ):
                errors.append(f"stale_completion_not_rejected:{scenario_id}:{trace_id}")

        elif action == "abort-declared-edge":
            ids, id_errors = _draft_ids(step, str(scenario_id))
            errors.extend(id_errors)
            if (
                not disposition_applied
                or current_result is None
                or current_result.get("disposition") != "abort-edge"
            ):
                errors.append(f"abort_without_abort_verdict:{scenario_id}:{index}")
            elif current_case is not None and ids != set(
                current_case.get("draft_ids", [])
            ):
                errors.append(f"abort_set_mismatch:{scenario_id}:{index}")

        elif action == "finish-scenario" and index != len(steps):
            errors.append(f"finish_not_last:{scenario_id}:{index}")

    if steps[-1].get("action") != "finish-scenario":
        errors.append(f"scenario_missing_finish:{scenario_id}")
    if expected_state != scenario.get("terminal_state"):
        errors.append(f"scenario_terminal_state_mismatch:{scenario_id}")
    return errors


def validate_document(
    document: dict[str, Any],
    *,
    protocol: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    """Return deterministic safety, reference and state-machine errors."""

    errors = _active_actuator_errors(document)
    if set(document) != TOP_LEVEL_FIELDS:
        errors.extend(
            f"top_level_field_missing:{name}"
            for name in sorted(TOP_LEVEL_FIELDS - set(document))
        )
        errors.extend(
            f"top_level_field_unknown:{name}"
            for name in sorted(set(document) - TOP_LEVEL_FIELDS)
        )
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_invalid")
    if not isinstance(document.get("revision"), int) or document.get("revision", 0) < 1:
        errors.append("revision_invalid")

    source = document.get("source_protocol")
    if not isinstance(source, dict):
        errors.append("source_protocol_invalid")
    else:
        expected_source_fields = {"path", "canonical_sha256", "required_result"}
        if set(source) != expected_source_fields:
            errors.append("source_protocol_fields_invalid")
        if source.get("path") != DEFAULT_PROTOCOL_RELATIVE.as_posix():
            errors.append("source_protocol_path_not_frozen")
        if source.get("canonical_sha256") != work_cell.canonical_sha256(protocol):
            errors.append("source_protocol_hash_mismatch")
        if source.get("required_result") != (
            "ariadne_bounded_cognitive_work_cell_protocol_pass"
        ):
            errors.append("source_protocol_result_invalid")

    authority = document.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority_invalid")
    else:
        required_authority = {
            "evidence_label": "authored_synthetic_repository_local_in_memory_rehearsal",
            "rehearsal_execution_enabled": True,
            "external_effects_enabled": False,
            "adaptive_agent_attached": False,
            "container_started": False,
            "persistence_enabled": False,
            "human_action_performed": False,
            "command_authority": False,
        }
        for key, expected in required_authority.items():
            if authority.get(key) != expected:
                errors.append(f"authority_posture_invalid:{key}")
        closed = authority.get("closed_connections")
        if not isinstance(closed, list) or set(closed) != set(
            REQUIRED_CLOSED_CONNECTIONS
        ):
            errors.append("closed_connections_invalid")

    limits = document.get("limits")
    if not isinstance(limits, dict) or set(limits) != set(HARD_LIMITS):
        errors.append("limits_invalid")
        limits = HARD_LIMITS
    else:
        for key, hard_limit in HARD_LIMITS.items():
            value = limits.get(key)
            if not isinstance(value, int) or value < 1 or value > hard_limit:
                errors.append(f"limit_out_of_bounds:{key}")

    if document.get("step_vocabulary") != list(ALLOWED_ACTIONS):
        errors.append("step_vocabulary_not_frozen")

    evidence = document.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence_invalid")
    else:
        for reference in evidence:
            if not isinstance(reference, str) or reference.startswith(("/", "\\")):
                errors.append(f"evidence_reference_unsafe:{reference}")
                continue
            path = Path(reference)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"evidence_reference_unsafe:{reference}")
            elif not (repo_root / path).is_file():
                errors.append(f"evidence_reference_invalid:{reference}")

    context, protocol_errors = _protocol_context(protocol, repo_root=repo_root)
    errors.extend(f"source_protocol_invalid:{error}" for error in protocol_errors)

    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("scenarios_invalid")
        return sorted(set(errors))
    if len(scenarios) > limits.get("max_scenarios", 0):
        errors.append("scenario_limit_exceeded")
    scenario_ids: set[str] = set()
    total_steps = 0
    for scenario in scenarios:
        if isinstance(scenario, dict):
            scenario_id = scenario.get("id")
            if scenario_id in scenario_ids:
                errors.append(f"scenario_duplicate:{scenario_id}")
            if isinstance(scenario_id, str):
                scenario_ids.add(scenario_id)
            steps = scenario.get("steps")
            if isinstance(steps, list):
                total_steps += len(steps)
        errors.extend(
            _validate_scenario(
                scenario,
                context=context,
                max_steps=limits.get("max_steps_per_scenario", 0),
            )
        )
    if total_steps > limits.get("max_total_steps", 0):
        errors.append("total_step_limit_exceeded")
    return sorted(set(errors))


def _step_references(step: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(value)
        for key, value in step.items()
        if key not in {"sequence", "action", "from_state", "to_state"}
    }


def build_rehearsal(
    document: dict[str, Any],
    *,
    protocol: dict[str, Any],
    repo_root: Path,
    validate: bool = True,
) -> dict[str, Any]:
    """Return the deterministic in-memory rehearsal evidence."""

    if validate:
        errors = validate_document(document, protocol=protocol, repo_root=repo_root)
        if errors:
            raise ScriptedRehearsalError("document_invalid:" + "|".join(errors))

    verification = work_cell.build_verification(protocol, repo_root=repo_root)
    verification_by_case = {
        item["case_id"]: item for item in verification["case_results"]
    }
    transitions: list[dict[str, Any]] = []
    scenario_results: list[dict[str, Any]] = []
    previous_hash = canonical_sha256(
        {
            "script_sha256": canonical_sha256(document),
            "protocol_sha256": work_cell.canonical_sha256(protocol),
        }
    )
    global_sequence = 0

    for scenario in document["scenarios"]:
        released_edge_count = 0
        human_gate_delivery_count = 0
        repair_receipt_count = 0
        correction_request_count = 0
        aborted_edge_count = 0
        supersession_count = 0
        stale_completion_rejection_count = 0
        current_result: dict[str, Any] | None = None
        scenario_first = len(transitions)

        for step in scenario["steps"]:
            action = step["action"]
            if action == "verify-drafts":
                current_result = verification_by_case[step["verification_case_id"]]
            elif action == "record-verified-release" and current_result is not None:
                released_edge_count += len(current_result["released_edges"])
                repair_receipt_count += len(current_result["repair_receipts"])
            elif action == "record-human-gate-delivery":
                human_gate_delivery_count += len(step["draft_ids"])
            elif action == "record-bounded-correction-request":
                correction_request_count += 1
            elif action == "abort-declared-edge":
                aborted_edge_count += len(step["draft_ids"])
            elif action == "supersede-declared-attempt":
                supersession_count += 1
            elif action == "reject-stale-completion":
                stale_completion_rejection_count += 1

            global_sequence += 1
            transition = {
                "sequence": global_sequence,
                "scenario_id": scenario["id"],
                "step_sequence": step["sequence"],
                "action": action,
                "from_state": step["from_state"],
                "to_state": step["to_state"],
                "reference_sha256": canonical_sha256(_step_references(step)),
                "previous_transition_sha256": previous_hash,
            }
            transition["transition_sha256"] = canonical_sha256(transition)
            previous_hash = transition["transition_sha256"]
            transitions.append(transition)

        scenario_results.append(
            {
                "scenario_id": scenario["id"],
                "purpose_code": scenario["purpose_code"],
                "terminal_state": scenario["terminal_state"],
                "transition_count": len(transitions) - scenario_first,
                "released_edge_count": released_edge_count,
                "human_gate_delivery_count": human_gate_delivery_count,
                "repair_receipt_count": repair_receipt_count,
                "correction_request_count": correction_request_count,
                "aborted_edge_count": aborted_edge_count,
                "supersession_count": supersession_count,
                "stale_completion_rejection_count": (
                    stale_completion_rejection_count
                ),
                "last_transition_sha256": previous_hash,
            }
        )

    totals = {
        "scenario_count": len(scenario_results),
        "transition_count": len(transitions),
        "released_edge_count": sum(
            item["released_edge_count"] for item in scenario_results
        ),
        "human_gate_delivery_count": sum(
            item["human_gate_delivery_count"] for item in scenario_results
        ),
        "repair_receipt_count": sum(
            item["repair_receipt_count"] for item in scenario_results
        ),
        "correction_request_count": sum(
            item["correction_request_count"] for item in scenario_results
        ),
        "aborted_edge_count": sum(
            item["aborted_edge_count"] for item in scenario_results
        ),
        "supersession_count": sum(
            item["supersession_count"] for item in scenario_results
        ),
        "stale_completion_rejection_count": sum(
            item["stale_completion_rejection_count"] for item in scenario_results
        ),
    }
    return {
        "schema_version": EVIDENCE_VERSION,
        "result": RESULT,
        "evidence_label": document["authority"]["evidence_label"],
        "script_sha256": canonical_sha256(document),
        "source_protocol_sha256": work_cell.canonical_sha256(protocol),
        "execution_posture": {
            "rehearsal_execution_enabled": True,
            "in_memory_only": True,
            "external_effects_enabled": False,
            "adaptive_agent_attached": False,
            "container_started": False,
            "persistence_enabled": False,
            "human_action_performed": False,
            "command_authority": False,
        },
        "scenario_results": scenario_results,
        "totals": totals,
        "transitions": transitions,
        "transition_chain_sha256": previous_hash,
        "closed_connections": sorted(REQUIRED_CLOSED_CONNECTIONS),
    }


def render_markdown(evidence: dict[str, Any]) -> str:
    totals = evidence["totals"]
    lines = [
        "# Ariadne Scripted Cognitive Work Cell - In-Memory Rehearsal",
        "",
        "Rehearsal execution enabled: **yes, finite in-memory tape only**",
        "",
        "External effects enabled: **no**",
        "",
        "The runner consumes only pre-authored synthetic attempts and drafts,",
        "reuses the deterministic proofreader and records a forward-only hash chain.",
        "It generates no draft and calls no model, container, database, API, mailbox",
        "or command.",
        "",
        "## Aggregate evidence",
        "",
        f"- Scenarios: **{totals['scenario_count']}**",
        f"- Transitions: **{totals['transition_count']}**",
        f"- Verified releases: **{totals['released_edge_count']}**",
        f"- Inert human-gate deliveries: **{totals['human_gate_delivery_count']}**",
        f"- Canonical repairs observed: **{totals['repair_receipt_count']}**",
        f"- Bounded correction requests: **{totals['correction_request_count']}**",
        f"- Aborted edges: **{totals['aborted_edge_count']}**",
        f"- Supersessions: **{totals['supersession_count']}**",
        "",
        "## Authority stop",
        "",
        "All releases remain process-local envelopes. Human routing performs no",
        "human action, and no transition can read, persist, confirm, write or invoke",
        "an EMR command.",
        "",
    ]
    return "\n".join(lines)


def build_evidence_projection(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return the committed deterministic projection without the full tape."""

    return {
        "schema_version": evidence["schema_version"],
        "result": evidence["result"],
        "evidence_label": evidence["evidence_label"],
        "script_sha256": evidence["script_sha256"],
        "source_protocol_sha256": evidence["source_protocol_sha256"],
        "execution_posture": copy.deepcopy(evidence["execution_posture"]),
        "scenario_results": copy.deepcopy(evidence["scenario_results"]),
        "totals": copy.deepcopy(evidence["totals"]),
        "transition_chain_sha256": evidence["transition_chain_sha256"],
        "closed_connections": copy.deepcopy(evidence["closed_connections"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the finite authored-synthetic Ariadne work-cell rehearsal."
        )
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("validate", help="Validate the frozen rehearsal tape.")
    subparsers.add_parser("rehearse", help="Run the tape in process memory.")
    subparsers.add_parser("trace", help="Render a fixed aggregate trace.")
    return parser


def _public_summary(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_VERSION,
        "status": "passed",
        "result": RESULT,
        "in_memory_only": True,
        "external_effects_enabled": False,
        "scenario_count": evidence["totals"]["scenario_count"],
        "transition_count": evidence["totals"]["transition_count"],
        "released_edge_count": evidence["totals"]["released_edge_count"],
        "human_gate_delivery_count": evidence["totals"][
            "human_gate_delivery_count"
        ],
        "aborted_edge_count": evidence["totals"]["aborted_edge_count"],
        "supersession_count": evidence["totals"]["supersession_count"],
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    try:
        document = load_json(default_script_path(repo_root))
        protocol = load_json(default_protocol_path(repo_root))
        if args.action == "validate":
            errors = validate_document(
                document, protocol=protocol, repo_root=repo_root
            )
            payload = {
                "schema_version": SCHEMA_VERSION,
                "status": "passed" if not errors else "revision_required",
                "in_memory_only": True,
                "external_effects_enabled": False,
                "error_count": len(errors),
            }
            print(canonical_json(payload), end="")
            return 0 if not errors else 2
        evidence = build_rehearsal(
            document, protocol=protocol, repo_root=repo_root
        )
        if args.action == "rehearse":
            print(canonical_json(_public_summary(evidence)), end="")
            return 0
        if args.action == "trace":
            print(render_markdown(evidence), end="")
            return 0
    except ScriptedRehearsalError:
        print(
            canonical_json(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": "revision_required",
                    "in_memory_only": True,
                    "external_effects_enabled": False,
                }
            ),
            end="",
        )
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
