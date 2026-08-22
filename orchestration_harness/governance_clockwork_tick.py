"""Generic pointer-last ticks for the live Ariadne governance clockwork."""

from __future__ import annotations

import copy
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, NoReturn

from jsonschema.exceptions import SchemaError, ValidationError

from orchestration_harness import transactional_closeout as tc
from orchestration_harness.active_operation import validate_active_operation
from orchestration_harness.governance_live_adoption import (
    AdoptionRejection,
    CANONICAL_KEYS,
    COMMAND_VERSION,
    METADATA_NAMES,
    WRITER,
    _all_keys,
    _assert_git_state,
    _canonical_paths_match_source,
    _exact,
    _git_bytes,
    _hash_bytes,
    _hash_json,
    _json_text,
    _load,
    _paths_match_source,
    _safe_path,
    _source_bytes,
    _write_temp,
    validate_contract,
    validate_live_state,
)
from scripts import ariadne_compass
from scripts.ariadne_agent_error_register import (
    EXPECTED_ORIGIN_BY_CATEGORY,
    build_pattern_report_from_payload,
)


TICK_INTENT_VERSION = "ariadne.governance_live_tick_intent.v1"
TICK_INCIDENT_INTENT_VERSION = "ariadne.governance_live_tick_intent.v2"
BLOCKED_INTENT_VERSION = "ariadne.governance_live_blocked_transition_intent.v1"
USER_DECISION_INTENT_VERSION = (
    "ariadne.governance_live_user_decision_transition_intent.v1"
)
USER_DECISION_SELECTED_OUTCOMES = frozenset(
    {
        "replace_with_newly_frozen_descendant",
        "replace_with_newly_frozen_transport_redesign",
    }
)
CHECKPOINT_INTENT_VERSION = "ariadne.governance_live_checkpoint_transition_intent.v1"
PREPARED_VERSION = "ariadne.governance_live_tick_prepared_generation.v1"
GENERATION_VERSION = "ariadne.governance_live_tick_generation.v1"
TRANSACTION_VERSION = "ariadne.governance_live_tick_transaction.v1"
POINTER_NAME = "current.json"
GENERATION_NAME = "generation-manifest.json"
PREDECESSOR_METADATA_NAMES = (*METADATA_NAMES, GENERATION_NAME)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
INCIDENT_TRANCHE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
INCIDENT_RESOURCE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
INCIDENT_TRANSPORT = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
INCIDENT_RECURRENCE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
INCIDENT_ROLES = frozenset(
    {"orchestrator", "implementer", "verifier", "integration_reviewer"}
)
INCIDENT_STAGES = frozenset(
    {
        "dispatch",
        "implementation",
        "deterministic_verification",
        "independent_review",
        "acceptance",
        "integration",
        "closeout",
    }
)
INCIDENT_SEVERITIES = frozenset({"low", "moderate", "material"})
INCIDENT_CANDIDATE_STATES = frozenset(
    {"canonical_unchanged", "untrusted_partial_worktree", "accepted_candidate_changed"}
)
INCIDENT_WORKFLOW_DISPOSITIONS = frozenset(
    {
        "review_rejected",
        "revision_required",
        "attempt_rejected_and_escalated",
        "recovery_lease_invoked",
    }
)
INCIDENT_CORRECTION_STATUSES = frozenset(
    {
        "corrected_fresh_attempt",
        "contained_then_escalated",
        "recovery_lease_applied",
        "control_added",
        "control_implemented_pending_acceptance",
    }
)
INCIDENT_CAUSAL_CLAIM_LEVEL = "observation_only"
INCIDENT_REVISION_PREFIX = "docs/ariadne-agent-error-correction-register-revision-"
BATON_INDEX_MANIFEST_PATH = Path(
    "docs/handover-ledgers/current-baton-acceptance-index.manifest.json"
)
BATON_INDEX_SCHEMA_VERSION = "emr4.current_baton_acceptance_index_manifest.v1"
BATON_TABLE_HEADING = "## 3. Current Baton"
BATON_TABLE_HEADER = "| Item | Current value |"
BATON_TABLE_END = "### Compact historical evaluation and transition state"
BATON_INDEX_LABEL = "Current Baton acceptance index"
BATON_MAX_BYTES = 80_000
BATON_MAX_LINES = 500

DERIVED_INPUT_KEYS = {
    "source_commit",
    "source_head",
    "graph_revision",
    "map_revision",
    "register_revision",
    "incident_population",
    "latest_incident_id",
    "transaction_id",
    "generation_id",
    "lease_id",
    "output_path",
    "bundle_sha256",
    "selected_generation_id",
    "selected_bundle_sha256",
    "previous_generation_id",
    "previous_source_commit",
    "lease_sequence",
    "canonical_sha256s",
    "metadata_sha256s",
    "projection_sha256s",
}

REQUIRED_NEXT_BOUNDARIES = {
    "local_origin_master_and_handoff_current_remain_2e34bdad732fdab32fbf778280b3d3c70d66d602",
    "no_production_runtime_deployment_release_or_pages",
    "no_protected_evidence_access_or_protected_ref_movement",
    "docs_branding_and_all_unrelated_untracked_files_preserved",
    "explicit_path_staging_only",
}

TRANSACTION_KEYS = {
    "schema_version",
    "operation_id",
    "transaction_id",
    "source_commit",
    "previous_source_commit",
    "previous_generation_id",
    "previous_bundle_sha256",
    "previous_canonical_sha256s",
    "previous_metadata_sha256s",
    "projection_sha256s",
    "journal",
    "publication_mode",
    "event_kind",
    "next_boundaries_sha256",
    "register_bytes_preserved",
    "pattern_bytes_preserved",
}


class ClockworkTickRejection(AdoptionRejection):
    """A generic tick failed before the pointer commit."""


class CommittedClockworkTick(RuntimeError):
    """An injected exception occurred after a complete pointer commit."""


def _reject(rule: str) -> NoReturn:
    raise ClockworkTickRejection(rule)


def _text(value: object, rule: str, maximum: int = 1000) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\r" in value
        or "\n" in value
        or len(value) > maximum
    ):
        _reject(rule)
    return value


def _strings(value: object, rule: str, *, maximum: int = 500) -> list[str]:
    if not isinstance(value, list) or not value:
        _reject(rule)
    result = [_text(item, rule, maximum) for item in value]
    if len(result) != len(set(result)):
        _reject(rule)
    return result


def _validate_commands(value: object) -> dict[str, Any]:
    row = _exact(value, {"schema_version", "commands"}, "tick_commands_keys")
    if row["schema_version"] != COMMAND_VERSION or not isinstance(row["commands"], list) or not row["commands"]:
        _reject("tick_commands_version")
    commands: list[dict[str, Any]] = []
    ids: list[str] = []
    for value in row["commands"]:
        command = _exact(
            value,
            {"command_id", "executable", "arguments", "completion_contract"},
            "tick_command_keys",
        )
        command_id = _text(command["command_id"], "tick_command_id", 128)
        if IDENTIFIER.fullmatch(command_id) is None:
            _reject("tick_command_id")
        executable = _text(command["executable"], "tick_command_executable", 300)
        arguments = command["arguments"]
        if (
            executable != ".venv/Scripts/python.exe"
            or not isinstance(arguments, list)
            or not arguments
            or arguments[0] != "-m"
            or any(
                not isinstance(item, str)
                or not item
                or any(mark in item for mark in "*?[];&|`$<>")
                for item in arguments
            )
            or command["completion_contract"] != "final_exit_code_zero_required"
        ):
            _reject("tick_command_contract")
        ids.append(command_id)
        commands.append(copy.deepcopy(command))
    if len(ids) != len(set(ids)):
        _reject("tick_command_duplicate")
    return {"schema_version": COMMAND_VERSION, "commands": commands}


def _validate_incident_observations(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _reject("tick_incident_observations")
    observations: list[dict[str, Any]] = []
    attempt_keys: list[str] = []
    for item in value:
        try:
            row = _exact(
                item,
                {
                    "attempt_key",
                    "observed_on",
                    "tranche",
                    "role",
                    "resource_id",
                    "model",
                    "reasoning_level",
                    "transport",
                    "stage",
                    "category",
                    "process_severity",
                    "expected_invariant",
                    "observed_error",
                    "detection_method",
                    "evidence_paths",
                    "candidate_state",
                    "workflow_disposition",
                    "recurrence_signature",
                    "causal_claim_level",
                    "correction",
                    "baton_summary",
                },
                "tick_incident_observation_keys",
            )
        except AdoptionRejection as error:
            raise ClockworkTickRejection(
                "tick_incident_observation_keys"
            ) from error
        attempt_key = _text(row["attempt_key"], "tick_incident_attempt_key", 128)
        if IDENTIFIER.fullmatch(attempt_key) is None:
            _reject("tick_incident_attempt_key")
        attempt_keys.append(attempt_key)
        category = _text(row["category"], "tick_incident_category", 80)
        if category not in EXPECTED_ORIGIN_BY_CATEGORY:
            _reject("tick_incident_category")
        observed_on = _text(row["observed_on"], "tick_incident_observed_on", 10)
        try:
            if date.fromisoformat(observed_on).isoformat() != observed_on:
                _reject("tick_incident_observed_on")
        except ValueError:
            _reject("tick_incident_observed_on")
        tranche = _text(row["tranche"], "tick_incident_tranche", 120)
        if INCIDENT_TRANCHE.fullmatch(tranche) is None:
            _reject("tick_incident_tranche")
        role = _text(row["role"], "tick_incident_role", 80)
        if role not in INCIDENT_ROLES:
            _reject("tick_incident_role")
        resource_id = _text(
            row["resource_id"], "tick_incident_resource_id", 120
        )
        if INCIDENT_RESOURCE.fullmatch(resource_id) is None:
            _reject("tick_incident_resource_id")
        transport = _text(row["transport"], "tick_incident_transport", 120)
        if INCIDENT_TRANSPORT.fullmatch(transport) is None:
            _reject("tick_incident_transport")
        stage = _text(row["stage"], "tick_incident_stage", 120)
        if stage not in INCIDENT_STAGES:
            _reject("tick_incident_stage")
        process_severity = _text(
            row["process_severity"], "tick_incident_severity", 40
        )
        if process_severity not in INCIDENT_SEVERITIES:
            _reject("tick_incident_severity")
        candidate_state = _text(
            row["candidate_state"], "tick_incident_candidate_state", 80
        )
        if candidate_state not in INCIDENT_CANDIDATE_STATES:
            _reject("tick_incident_candidate_state")
        workflow_disposition = _text(
            row["workflow_disposition"],
            "tick_incident_workflow_disposition",
            120,
        )
        if workflow_disposition not in INCIDENT_WORKFLOW_DISPOSITIONS:
            _reject("tick_incident_workflow_disposition")
        recurrence_signature = _text(
            row["recurrence_signature"],
            "tick_incident_recurrence_signature",
            120,
        )
        if INCIDENT_RECURRENCE.fullmatch(recurrence_signature) is None:
            _reject("tick_incident_recurrence_signature")
        causal_claim_level = _text(
            row["causal_claim_level"], "tick_incident_causal_claim", 80
        )
        if causal_claim_level != INCIDENT_CAUSAL_CLAIM_LEVEL:
            _reject("tick_incident_causal_claim")
        model = row["model"]
        if model is not None:
            model = _text(model, "tick_incident_model", 120)
        try:
            correction = _exact(
                row["correction"],
                {"status", "action", "prevention_control", "evidence_paths"},
                "tick_incident_correction_keys",
            )
        except AdoptionRejection as error:
            raise ClockworkTickRejection(
                "tick_incident_correction_keys"
            ) from error
        correction_status = _text(
            correction["status"], "tick_incident_correction_status", 80
        )
        if correction_status not in INCIDENT_CORRECTION_STATUSES:
            _reject("tick_incident_correction_status")
        evidence_paths = _strings(
            row["evidence_paths"], "tick_incident_evidence_paths"
        )
        correction_paths = _strings(
            correction["evidence_paths"], "tick_incident_correction_paths"
        )
        for path in [*evidence_paths, *correction_paths]:
            try:
                _safe_path(path, "tick_incident_evidence_path")
            except AdoptionRejection as error:
                raise ClockworkTickRejection(
                    "tick_incident_evidence_path"
                ) from error
        observations.append(
            {
                "attempt_key": attempt_key,
                "observed_on": observed_on,
                "tranche": tranche,
                "role": role,
                "resource_id": resource_id,
                "model": model,
                "reasoning_level": _text(
                    row["reasoning_level"], "tick_incident_reasoning_level", 80
                ),
                "transport": transport,
                "stage": stage,
                "category": category,
                "process_severity": process_severity,
                "expected_invariant": _text(
                    row["expected_invariant"], "tick_incident_expected", 1000
                ),
                "observed_error": _text(
                    row["observed_error"], "tick_incident_observed", 1000
                ),
                "detection_method": _text(
                    row["detection_method"], "tick_incident_detection", 1000
                ),
                "evidence_paths": evidence_paths,
                "candidate_state": candidate_state,
                "workflow_disposition": workflow_disposition,
                "recurrence_signature": recurrence_signature,
                "causal_claim_level": causal_claim_level,
                "correction": {
                    "status": correction_status,
                    "action": _text(
                        correction["action"], "tick_incident_correction_action", 1000
                    ),
                    "prevention_control": _text(
                        correction["prevention_control"],
                        "tick_incident_prevention_control",
                        1000,
                    ),
                    "evidence_paths": correction_paths,
                },
                "baton_summary": _text(
                    row["baton_summary"], "tick_incident_baton_summary", 300
                ),
            }
        )
    if len(attempt_keys) != len(set(attempt_keys)):
        _reject("tick_incident_attempt_key_duplicate")
    return observations


def validate_tick_intent(value: object, contract_value: object) -> dict[str, Any]:
    """Validate semantic caller input and reject every derived binding."""

    contract = validate_contract(contract_value)
    if not isinstance(value, dict):
        _reject("tick_intent_keys")
    version = value.get("schema_version")
    keys = {
        "schema_version",
        "transaction_manifest",
        "command_manifest",
        "baton_acceptance",
        "next_operation_protected_boundaries",
    }
    if version == TICK_INCIDENT_INTENT_VERSION:
        keys.add("agent_error_observations")
    row = _exact(value, keys, "tick_intent_keys")
    if version not in {TICK_INTENT_VERSION, TICK_INCIDENT_INTENT_VERSION}:
        _reject("tick_intent_version")
    if _all_keys(row) & DERIVED_INPUT_KEYS:
        _reject("caller_authored_derived_binding")
    try:
        manifest = tc.validate_manifest(row["transaction_manifest"])
    except ValueError as error:
        raise ClockworkTickRejection("tick_transaction_manifest") from error
    if manifest["broker"] != {"enabled": False, "posture": "provider_free_shadow"}:
        _reject("tick_broker_authority")
    commands = _validate_commands(row["command_manifest"])
    acceptance = _exact(
        row["baton_acceptance"], {"label", "paths"}, "tick_baton_acceptance_keys"
    )
    label = _text(acceptance["label"], "tick_baton_label", 200)
    if "|" in label:
        _reject("tick_baton_label")
    paths = _strings(acceptance["paths"], "tick_baton_paths")
    for path in paths:
        try:
            _safe_path(path, "tick_baton_path")
        except AdoptionRejection as error:
            raise ClockworkTickRejection("tick_baton_path") from error
        if path in contract["canonical_paths"].values() or path.startswith(
            contract["clockwork_root"] + "/"
        ):
            _reject("tick_baton_path_owned")
    boundaries = _strings(
        row["next_operation_protected_boundaries"], "tick_next_boundaries"
    )
    if not REQUIRED_NEXT_BOUNDARIES.issubset(boundaries):
        _reject("tick_next_boundaries_floor")
    result = {
        "schema_version": version,
        "transaction_manifest": manifest,
        "command_manifest": commands,
        "baton_acceptance": {"label": label, "paths": paths},
        "next_operation_protected_boundaries": boundaries,
    }
    if version == TICK_INCIDENT_INTENT_VERSION:
        result["agent_error_observations"] = _validate_incident_observations(
            row["agent_error_observations"]
        )
    return result


def validate_blocked_tick_intent(
    value: object, contract_value: object
) -> dict[str, Any]:
    """Validate a terminal blocked transition without accepting a closeout."""

    validate_contract(contract_value)
    try:
        row = _exact(
            value,
            {
                "schema_version",
                "operation_id",
                "completed_stage",
                "user_attention_reason",
                "terminal_reason",
                "command_manifest",
            },
            "blocked_tick_intent_keys",
        )
    except AdoptionRejection as error:
        raise ClockworkTickRejection("blocked_tick_intent_keys") from error
    if row["schema_version"] != BLOCKED_INTENT_VERSION:
        _reject("blocked_tick_intent_version")
    if _all_keys(row) & DERIVED_INPUT_KEYS:
        _reject("caller_authored_derived_binding")
    operation_id = _text(row["operation_id"], "blocked_tick_operation_id", 128)
    if IDENTIFIER.fullmatch(operation_id) is None:
        _reject("blocked_tick_operation_id")
    return {
        "schema_version": BLOCKED_INTENT_VERSION,
        "operation_id": operation_id,
        "completed_stage": _text(
            row["completed_stage"], "blocked_tick_completed_stage", 500
        ),
        "user_attention_reason": _text(
            row["user_attention_reason"], "blocked_tick_attention_reason", 500
        ),
        "terminal_reason": _text(
            row["terminal_reason"], "blocked_tick_terminal_reason", 500
        ),
        "command_manifest": _validate_commands(row["command_manifest"]),
    }


def validate_user_decision_tick_intent(
    value: object, contract_value: object
) -> dict[str, Any]:
    """Validate a blocked-operation replacement chosen by the user."""

    validate_contract(contract_value)
    try:
        row = _exact(
            value,
            {
                "schema_version",
                "blocked_operation_id",
                "selected_outcome",
                "next_operation",
                "next_operation_protected_boundaries",
                "command_manifest",
            },
            "user_decision_tick_intent_keys",
        )
    except AdoptionRejection as error:
        raise ClockworkTickRejection("user_decision_tick_intent_keys") from error
    if row["schema_version"] != USER_DECISION_INTENT_VERSION:
        _reject("user_decision_tick_intent_version")
    if _all_keys(row) & DERIVED_INPUT_KEYS:
        _reject("caller_authored_derived_binding")
    blocked_operation_id = _text(
        row["blocked_operation_id"], "user_decision_blocked_operation_id", 128
    )
    if IDENTIFIER.fullmatch(blocked_operation_id) is None:
        _reject("user_decision_blocked_operation_id")
    if row["selected_outcome"] not in USER_DECISION_SELECTED_OUTCOMES:
        _reject("user_decision_selected_outcome")
    next_operation = _exact(
        row["next_operation"],
        {
            "operation_id",
            "active_tranche",
            "objective",
            "authority_source",
            "completed_stage",
            "next_executable_stage",
        },
        "user_decision_next_operation_keys",
    )
    operation_id = _text(
        next_operation["operation_id"], "user_decision_next_operation_id", 128
    )
    if (
        IDENTIFIER.fullmatch(operation_id) is None
        or operation_id == blocked_operation_id
    ):
        _reject("user_decision_next_operation_id")
    boundaries = _strings(
        row["next_operation_protected_boundaries"],
        "user_decision_next_boundaries",
    )
    if not REQUIRED_NEXT_BOUNDARIES.issubset(boundaries):
        _reject("user_decision_next_boundaries_floor")
    return {
        "schema_version": USER_DECISION_INTENT_VERSION,
        "blocked_operation_id": blocked_operation_id,
        "selected_outcome": row["selected_outcome"],
        "next_operation": {
            "operation_id": operation_id,
            "active_tranche": _text(
                next_operation["active_tranche"],
                "user_decision_active_tranche",
                240,
            ),
            "objective": _text(
                next_operation["objective"], "user_decision_objective", 1000
            ),
            "authority_source": _text(
                next_operation["authority_source"],
                "user_decision_authority_source",
                500,
            ),
            "completed_stage": _text(
                next_operation["completed_stage"],
                "user_decision_completed_stage",
                500,
            ),
            "next_executable_stage": _text(
                next_operation["next_executable_stage"],
                "user_decision_next_executable_stage",
                500,
            ),
        },
        "next_operation_protected_boundaries": boundaries,
        "command_manifest": _validate_commands(row["command_manifest"]),
    }


def validate_checkpoint_tick_intent(
    value: object, contract_value: object
) -> dict[str, Any]:
    """Validate semantic progress for the currently in-progress operation."""

    validate_contract(contract_value)
    try:
        row = _exact(
            value,
            {
                "schema_version",
                "operation_id",
                "completed_stage",
                "next_executable_stage",
                "command_manifest",
            },
            "checkpoint_tick_intent_keys",
        )
    except AdoptionRejection as error:
        raise ClockworkTickRejection("checkpoint_tick_intent_keys") from error
    if row["schema_version"] != CHECKPOINT_INTENT_VERSION:
        _reject("checkpoint_tick_intent_version")
    if _all_keys(row) & DERIVED_INPUT_KEYS:
        _reject("caller_authored_derived_binding")
    operation_id = _text(row["operation_id"], "checkpoint_tick_operation_id", 128)
    if IDENTIFIER.fullmatch(operation_id) is None:
        _reject("checkpoint_tick_operation_id")
    return {
        "schema_version": CHECKPOINT_INTENT_VERSION,
        "operation_id": operation_id,
        "completed_stage": _text(
            row["completed_stage"], "checkpoint_tick_completed_stage", 500
        ),
        "next_executable_stage": _text(
            row["next_executable_stage"], "checkpoint_tick_next_stage", 500
        ),
        "command_manifest": _validate_commands(row["command_manifest"]),
    }


def _validate_any_intent(
    value: object, contract: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _reject("tick_intent_object")
    if value.get("schema_version") in {
        TICK_INTENT_VERSION,
        TICK_INCIDENT_INTENT_VERSION,
    }:
        return validate_tick_intent(value, contract)
    if value.get("schema_version") == BLOCKED_INTENT_VERSION:
        return validate_blocked_tick_intent(value, contract)
    if value.get("schema_version") == USER_DECISION_INTENT_VERSION:
        return validate_user_decision_tick_intent(value, contract)
    if value.get("schema_version") == CHECKPOINT_INTENT_VERSION:
        return validate_checkpoint_tick_intent(value, contract)
    _reject("tick_intent_version")


def _intent_operation_id(intent: dict[str, Any]) -> str:
    if intent["schema_version"] in {
        TICK_INTENT_VERSION,
        TICK_INCIDENT_INTENT_VERSION,
    }:
        return intent["transaction_manifest"]["operation_id"]
    if intent["schema_version"] == BLOCKED_INTENT_VERSION:
        return intent["operation_id"]
    if intent["schema_version"] == USER_DECISION_INTENT_VERSION:
        return intent["next_operation"]["operation_id"]
    return intent["operation_id"]


def _reject_recorded_next_operation(
    graph: dict[str, Any], operation_id: str
) -> None:
    """Keep an immutable operation identity out of every successor latch."""

    if any(node.get("id") == operation_id for node in graph["nodes"]):
        _reject("tick_next_operation_already_recorded")


def _derive_blocked_latch(
    latch: dict[str, Any], intent: dict[str, Any]
) -> dict[str, Any]:
    if latch["status"] != "in_progress" or latch["operation_id"] != intent["operation_id"]:
        _reject("blocked_tick_active_operation")
    result = copy.deepcopy(latch)
    result["status"] = "blocked"
    result["checkpoint"]["completed_stage"] = intent["completed_stage"]
    result["checkpoint"]["next_executable_stage"] = None
    result["checkpoint"]["retry_counters"]["verification"] += 1
    result["user_attention"] = {
        "required": True,
        "reason": intent["user_attention_reason"],
    }
    result["terminal_response"] = {
        "permitted": True,
        "reason": intent["terminal_reason"],
    }
    return validate_active_operation(result)


def _derive_user_decision_latch(
    latch: dict[str, Any], intent: dict[str, Any], source: str
) -> dict[str, Any]:
    if (
        latch["status"] != "blocked"
        or latch["operation_id"] != intent["blocked_operation_id"]
        or not latch["user_attention"]["required"]
        or not latch["terminal_response"]["permitted"]
    ):
        _reject("user_decision_active_operation")
    next_operation = intent["next_operation"]
    result = {
        "schema_version": latch["schema_version"],
        "operation_id": next_operation["operation_id"],
        "active_tranche": next_operation["active_tranche"],
        "objective": next_operation["objective"],
        "status": "in_progress",
        "source_head": source,
        "authority_source": next_operation["authority_source"],
        "checkpoint": {
            "completed_stage": next_operation["completed_stage"],
            "next_executable_stage": next_operation["next_executable_stage"],
            "retry_counters": {
                "planning": 0,
                "implementation": 0,
                "review": 0,
                "verification": 0,
            },
            "settings_fingerprint": latch["checkpoint"]["settings_fingerprint"],
        },
        "interruption_policy": copy.deepcopy(latch["interruption_policy"]),
        "resume_after_compaction": True,
        "user_attention": {"required": False, "reason": None},
        "terminal_response": {
            "permitted": False,
            "reason": "unfinished_authorized_operation",
        },
        "protected_boundaries": list(
            intent["next_operation_protected_boundaries"]
        ),
    }
    return validate_active_operation(result)


def _derive_checkpoint_latch(
    latch: dict[str, Any], intent: dict[str, Any], source: str
) -> dict[str, Any]:
    if (
        latch["status"] != "in_progress"
        or latch["operation_id"] != intent["operation_id"]
    ):
        _reject("checkpoint_tick_active_operation")
    if (
        latch["checkpoint"]["completed_stage"] == intent["completed_stage"]
        or latch["checkpoint"]["next_executable_stage"]
        == intent["next_executable_stage"]
    ):
        _reject("checkpoint_tick_no_progress")
    result = copy.deepcopy(latch)
    result["source_head"] = source
    result["checkpoint"]["completed_stage"] = intent["completed_stage"]
    result["checkpoint"]["next_executable_stage"] = intent[
        "next_executable_stage"
    ]
    return validate_active_operation(result)


def _clockwork_root(repo_root: Path, contract: dict[str, Any]) -> Path:
    return repo_root / contract["clockwork_root"]


def _metadata_paths(contract: dict[str, Any]) -> dict[str, str]:
    root = contract["clockwork_root"]
    return {name: f"{root}/{name}" for name in PREDECESSOR_METADATA_NAMES}


def _source_metadata(
    repo_root: Path, contract: dict[str, Any], source: str
) -> dict[str, bytes]:
    return {
        name: _git_bytes(repo_root, source, relative)
        for name, relative in _metadata_paths(contract).items()
    }


def _source_pointer(
    repo_root: Path, contract: dict[str, Any], source: str
) -> dict[str, Any]:
    raw = _git_bytes(
        repo_root, source, f"{contract['clockwork_root']}/{POINTER_NAME}"
    )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ClockworkTickRejection("tick_source_pointer") from error
    if not isinstance(value, dict):
        _reject("tick_source_pointer")
    return value


def _assert_clean_predecessor(
    repo_root: Path, contract: dict[str, Any], source: str
) -> tuple[
    dict[str, bytes], dict[str, bytes], dict[str, Any]
]:
    if not _canonical_paths_match_source(repo_root, contract, source):
        _reject("tick_canonical_not_at_source")
    source_canonical = _source_bytes(repo_root, contract, source)
    source_metadata = _source_metadata(repo_root, contract, source)
    source_pointer = _source_pointer(repo_root, contract, source)
    if not _paths_match_source(
        repo_root, source, list(_metadata_paths(contract).values())
    ):
        _reject("tick_metadata_not_at_source")
    pointer = _load(_clockwork_root(repo_root, contract) / POINTER_NAME)
    if pointer != source_pointer:
        _reject("tick_pointer_physical_drift")
    return source_canonical, source_metadata, source_pointer


def _project_incident_register(
    repo_root: Path,
    contract: dict[str, Any],
    current: dict[str, bytes],
    observations: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        register = json.loads(current["error_register"].decode("utf-8"))
        schema_path = (
            repo_root / contract["canonical_paths"]["error_register"]
        ).with_name("agent-error-register.schema.json")
        schema = _load(schema_path)
        next_number = int(register["incidents"][-1]["incident_id"].split("-")[1])
    except (KeyError, IndexError, TypeError, ValueError, UnicodeDecodeError) as error:
        raise ClockworkTickRejection("tick_incident_register_source") from error

    prospective = copy.deepcopy(register)
    generated: list[dict[str, Any]] = []
    attempt_identity_by_key: dict[str, dict[str, Any]] = {}
    for offset, observation in enumerate(observations, start=1):
        stable = {
            key: observation[key]
            for key in (
                "observed_on",
                "tranche",
                "role",
                "resource_id",
                "model",
                "reasoning_level",
                "transport",
                "stage",
            )
        }
        attempt_key = observation["attempt_key"]
        previous_stable = attempt_identity_by_key.setdefault(attempt_key, stable)
        if previous_stable != stable:
            _reject("tick_incident_attempt_identity")
        incident = {
            key: copy.deepcopy(value)
            for key, value in observation.items()
            if key not in {"attempt_key", "baton_summary"}
        }
        incident.update(
            {
                "incident_id": f"AER-{next_number + offset:04d}",
                "attempt_id": "clock-"
                + _hash_json({"attempt_key": attempt_key, "stable": stable})[:24],
                "origin": EXPECTED_ORIGIN_BY_CATEGORY[incident["category"]],
                "related_incident_ids": [],
                "status": "corrected",
            }
        )
        generated.append(incident)
    by_attempt: dict[str, list[dict[str, Any]]] = {}
    for incident in generated:
        by_attempt.setdefault(incident["attempt_id"], []).append(incident)
    for incident in generated:
        incident["related_incident_ids"] = sorted(
            peer["incident_id"]
            for peer in by_attempt[incident["attempt_id"]]
            if peer is not incident
        )

    prospective["incidents"].extend(generated)
    prospective["register_revision"] += 1
    prospective["scope"]["source_cutoff_on"] = max(
        prospective["scope"]["source_cutoff_on"],
        *(observation["observed_on"] for observation in observations),
    )
    try:
        pattern = build_pattern_report_from_payload(
            prospective, schema, root=repo_root
        )
    except (ValueError, TypeError, SchemaError, ValidationError) as error:
        raise ClockworkTickRejection("tick_incident_register_projection") from error
    return prospective, pattern


def _validate_incident_revision_artifact(
    repo_root: Path,
    acceptance_paths: list[str],
    register: dict[str, Any],
    observation_count: int,
) -> None:
    """Bind the human revision note to the complete prospective machine reading."""

    revision = register["register_revision"]
    expected_path = f"{INCIDENT_REVISION_PREFIX}{revision}.md"
    matching = [
        path for path in acceptance_paths if path.startswith(INCIDENT_REVISION_PREFIX)
    ]
    if matching != [expected_path]:
        _reject("tick_incident_revision_path")
    try:
        document = (repo_root / expected_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ClockworkTickRejection("tick_incident_revision_reading") from error
    incident_ids = [
        item["incident_id"] for item in register["incidents"][-observation_count:]
    ]
    open_count = sum(item["status"] == "open" for item in register["incidents"])
    reading = "\n".join(
        [
            "<!-- ariadne-agent-error-register-reading",
            f"revision: {revision}",
            f"incident_count: {len(register['incidents'])}",
            f"new_incident_ids: {','.join(incident_ids)}",
            f"open_incident_count: {open_count}",
            "-->",
        ]
    )
    headings = re.findall(r"^## (AER-[0-9]{4})(?:\s|$)", document, re.MULTILINE)
    if document.count(reading) != 1 or headings != incident_ids:
        _reject("tick_incident_revision_reading")


def _baton_row_label(line: str) -> str:
    if not line.startswith("| "):
        _reject("tick_baton_compaction_row")
    return line.split("|", 2)[1].strip()


def _load_baton_compaction_manifest(repo_root: Path) -> dict[str, Any]:
    """Read the hash-bound historical index used by the clockwork projection."""

    try:
        manifest = json.loads(
            (repo_root / BATON_INDEX_MANIFEST_PATH).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ClockworkTickRejection("tick_baton_compaction_manifest") from error
    expected_keys = {
        "active_labels",
        "generated_date",
        "ledger_byte_count",
        "ledger_line_count",
        "ledger_path",
        "ledger_sha256",
        "moved_labels",
        "moved_row_count",
        "schema_version",
        "source_agents_byte_count",
        "source_agents_git_blob_sha1",
        "source_agents_line_count",
        "source_agents_path",
        "source_agents_sha256",
        "source_git_head",
    }
    if not isinstance(manifest, dict) or set(manifest) != expected_keys:
        _reject("tick_baton_compaction_manifest")
    if manifest["schema_version"] != BATON_INDEX_SCHEMA_VERSION:
        _reject("tick_baton_compaction_manifest")
    active = manifest["active_labels"]
    moved = manifest["moved_labels"]
    if (
        not isinstance(active, list)
        or not active
        or not all(isinstance(label, str) and label for label in active)
        or len(active) != len(set(active))
        or not isinstance(moved, list)
        or not all(isinstance(label, str) and label for label in moved)
        or len(moved) != len(set(moved))
        or set(active).intersection(moved)
        or BATON_INDEX_LABEL in active
        or BATON_INDEX_LABEL in moved
        or manifest["moved_row_count"] != len(moved)
        or manifest["ledger_path"]
        != "docs/handover-ledgers/current-baton-acceptance-index.md"
        or manifest["source_agents_path"] != "AGENTS.md"
        or not isinstance(manifest["ledger_byte_count"], int)
        or manifest["ledger_byte_count"] <= 0
        or not isinstance(manifest["ledger_line_count"], int)
        or manifest["ledger_line_count"] <= 0
        or not HEX64.fullmatch(manifest["ledger_sha256"])
        or not HEX40.fullmatch(manifest["source_agents_git_blob_sha1"])
        or not HEX64.fullmatch(manifest["source_agents_sha256"])
        or not HEX40.fullmatch(manifest["source_git_head"])
    ):
        _reject("tick_baton_compaction_manifest")
    try:
        ledger = (repo_root / manifest["ledger_path"]).read_bytes()
        ledger_text = ledger.decode("utf-8")
        ledger_lines = ledger_text.splitlines()
        ledger_header = ledger_lines.index("| Item | Indexed acceptance artifacts |")
    except (OSError, UnicodeError, ValueError) as error:
        raise ClockworkTickRejection("tick_baton_compaction_ledger") from error
    ledger_labels = [
        _baton_row_label(line)
        for line in ledger_lines[ledger_header + 2 :]
        if line.startswith("| ")
    ]
    # Historical replay fixtures predate the rolling slot and retain a known
    # two-byte Git-normalisation difference. Their closed label roster remains
    # replayable; the migrated rolling-slot manifest requires exact bytes/hash.
    strict_binding = "Current DeepSeek native Harness acceptance" in active
    if ledger_labels != moved or (
        strict_binding
        and (
            len(ledger) != manifest["ledger_byte_count"]
            or len(ledger_lines) != manifest["ledger_line_count"]
            or _hash_bytes(ledger) != manifest["ledger_sha256"]
        )
    ):
        _reject("tick_baton_compaction_ledger")
    return manifest


def _compact_rendered_baton(
    current: str,
    manifest: dict[str, Any],
    *,
    acceptance_label: str,
) -> str:
    """Project the live Baton from closed labels after all tick-owned edits."""

    lines = current.splitlines(keepends=True)
    try:
        section = next(
            index
            for index, line in enumerate(lines)
            if line.rstrip("\r\n") == BATON_TABLE_HEADING
        )
        header = next(
            index
            for index in range(section + 1, len(lines))
            if lines[index].rstrip("\r\n") == BATON_TABLE_HEADER
        )
        end = next(
            index
            for index in range(header + 2, len(lines))
            if lines[index].rstrip("\r\n") == BATON_TABLE_END
        )
    except StopIteration as error:
        raise ClockworkTickRejection("tick_baton_compaction_markers") from error
    rows = [line for line in lines[header + 2 : end] if line.startswith("| ")]
    labels = [_baton_row_label(row) for row in rows]
    if len(labels) != len(set(labels)):
        _reject("tick_baton_compaction_duplicate")
    # The validated tick acceptance is clockwork-owned active state. Older replay
    # fixtures predate the rolling acceptance slot and the clockwork-relation row,
    # so both are explicit derived active rows rather than caller-authored labels.
    if acceptance_label not in manifest["active_labels"]:
        _reject("tick_baton_compaction_unindexed")
    active = set(manifest["active_labels"]).union(
        {acceptance_label, "Current clockwork relation"}
    )
    missing = active.difference(labels)
    if missing or labels.count(BATON_INDEX_LABEL) != 1:
        _reject("tick_baton_compaction_active")
    unindexed = set(labels).difference(active, {BATON_INDEX_LABEL}).difference(
        manifest["moved_labels"]
    )
    if unindexed and "Current DeepSeek native Harness acceptance" in active:
        _reject("tick_baton_compaction_unindexed")
    kept = [
        row
        for row in rows
        if _baton_row_label(row) in active
        or _baton_row_label(row) == BATON_INDEX_LABEL
    ]
    compacted = "".join(
        [*lines[: header + 2], *kept, *lines[end:]]
    )
    if (
        len(compacted.encode("utf-8")) >= BATON_MAX_BYTES
        or len(compacted.splitlines()) >= BATON_MAX_LINES
    ):
        _reject("tick_baton_compaction_budget")
    return compacted


def _render_baton(
    current: str,
    *,
    manifest: dict[str, Any],
    acceptance: dict[str, Any],
    graph: dict[str, Any],
    compass: dict[str, Any],
    source: str,
    compaction_manifest: dict[str, Any],
    register: dict[str, Any] | None = None,
    incident_summaries: list[str] | None = None,
) -> str:
    def replace_row(text: str, label: str, value: str) -> str:
        prefix = f"| {label} |"
        matches = [line for line in text.splitlines() if line.startswith(prefix)]
        if len(matches) != 1:
            _reject("tick_baton_row")
        return text.replace(matches[0], f"| {label} | {value} |", 1)

    outcome = manifest["current_position"]["outcome"]
    result = (
        f"At Continuity {graph['graph_revision']} / Compass {compass['map_revision']}, "
        f"{manifest['title']} is accepted at exact reviewed source `{source}`. {outcome}"
    )
    successor = manifest["next_operation"]
    next_value = (
        f"Proceed under standing authority with `{successor['operation_id']}`: "
        f"{successor['objective']} The active latch is the exact authority boundary. "
        "Protected refs remain closed; preserve `docs/branding/` and stage explicit paths only."
    )
    current = replace_row(current, "Current result", result)
    current = replace_row(current, "Next implementation", next_value)
    relation = (
        f"The live repository-governance clockwork has published through exact reviewed source `{source}` "
        f"at Continuity {graph['graph_revision']} / Compass {compass['map_revision']}. One clockwork writer owns "
        "all ten surfaces, historical direct writers remain retired, and the immediately previous generation is "
        "full-Git-bound and byte-recoverable. This opens no protected-ref, deployment, release or Pages authority."
    )
    current = replace_row(current, "Current clockwork relation", relation)
    if register is not None:
        incidents = register["incidents"]
        open_count = sum(item["status"] == "open" for item in incidents)
        open_text = "none open" if open_count == 0 else f"{open_count} open"
        summaries_list = incident_summaries or []
        generated = incidents[-len(summaries_list) :] if summaries_list else []
        summaries = " ".join(
            f"{incident['incident_id']} {summary}"
            for incident, summary in zip(generated, summaries_list, strict=True)
        )
        register_value = (
            f"Revision {register['register_revision']}: "
            "`docs/ariadne-agent-error-correction-register-revision-"
            f"{register['register_revision']}.md`; {len(incidents)} bounded incidents, "
            f"all corrected/contained and {open_text}. {summaries} Durable state: "
            "`orchestration/continuity/ariadne-agent-error-register/`."
        )
        current = replace_row(
            current,
            "Ariadne agent error and correction register acceptance",
            register_value,
        )
    label = acceptance["label"]
    row = f"| {label} | " + ", ".join(f"`{path}`" for path in acceptance["paths"]) + " |"
    prefix = f"| {label} |"
    existing = [line for line in current.splitlines() if line.startswith(prefix)]
    if existing:
        if len(existing) != 1:
            _reject("tick_baton_acceptance_row")
        current = current.replace(existing[0], row, 1)
    else:
        marker = "| Current result |"
        index = current.find(marker)
        if index < 0:
            _reject("tick_baton_acceptance_insert")
        current = current[:index] + row + "\n" + current[index:]
    return _compact_rendered_baton(
        current,
        compaction_manifest,
        acceptance_label=acceptance["label"],
    )


def _render_user_decision_baton(
    current: str,
    *,
    intent: dict[str, Any],
    graph: dict[str, Any],
    compass: dict[str, Any],
    source: str,
) -> str:
    def replace_row(text: str, label: str, value: str) -> str:
        prefix = f"| {label} |"
        matches = [line for line in text.splitlines() if line.startswith(prefix)]
        if len(matches) != 1:
            _reject("user_decision_baton_row")
        return text.replace(matches[0], f"| {label} | {value} |", 1)

    next_operation = intent["next_operation"]
    next_value = (
        "Proceed under Yuri's explicit user-selected replacement with "
        f"`{next_operation['operation_id']}`: {next_operation['objective']} "
        "The active latch is the exact authority boundary. Protected refs remain closed; "
        "preserve `docs/branding/` and stage explicit paths only."
    )
    relation = (
        "The live repository-governance clockwork last published a user-decision "
        f"transition from exact full Git source `{source}` while Continuity "
        f"{graph['graph_revision']} / Compass {compass['map_revision']} and the last "
        "accepted product result remained unchanged. One clockwork writer owns all ten "
        "surfaces, historical direct writers remain retired, and the immediately previous "
        "generation is full-Git-bound and byte-recoverable. This opens no protected-ref, "
        "deployment, release or Pages authority."
    )
    current = replace_row(current, "Next implementation", next_value)
    return replace_row(current, "Current clockwork relation", relation)


def _render_checkpoint_baton(
    current: str,
    *,
    graph: dict[str, Any],
    compass: dict[str, Any],
    source: str,
) -> str:
    prefix = "| Current clockwork relation |"
    matches = [line for line in current.splitlines() if line.startswith(prefix)]
    if len(matches) != 1:
        _reject("checkpoint_tick_baton_row")
    relation = (
        "The live repository-governance clockwork last published an in-progress "
        f"checkpoint from exact full Git source `{source}` while Continuity "
        f"{graph['graph_revision']} / Compass {compass['map_revision']} and the last "
        "accepted product result remained unchanged. One clockwork writer owns all ten "
        "surfaces, historical direct writers remain retired, and the immediately previous "
        "generation is full-Git-bound and byte-recoverable. This opens no protected-ref, "
        "deployment, release or Pages authority."
    )
    return current.replace(matches[0], f"{prefix} {relation} |", 1)


def build_tick_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Derive a complete next generation from the current live reading."""

    contract = validate_contract(contract_value)
    intent = validate_tick_intent(intent_value, contract)
    live = validate_live_state(repo_root, contract)
    source = _assert_git_state(repo_root, contract)
    current, prior_metadata, base_pointer = _assert_clean_predecessor(
        repo_root, contract, source
    )
    baton_compaction_manifest = _load_baton_compaction_manifest(repo_root)
    prior_generation = json.loads(prior_metadata[GENERATION_NAME].decode("utf-8"))
    if (
        base_pointer.get("phase") != "clockwork_active"
        or base_pointer.get("writer") != WRITER
        or base_pointer.get("selected_generation_id") != live["generation_id"]
        or base_pointer.get("selected_bundle_sha256") != live["bundle_sha256"]
        or prior_generation.get("generation_id") != live["generation_id"]
    ):
        _reject("tick_predecessor_identity")
    manifest = intent["transaction_manifest"]
    latch = json.loads(current["active_latch"].decode("utf-8"))
    if latch.get("operation_id") != manifest["operation_id"]:
        _reject("tick_active_operation")
    graph = json.loads(current["continuity"].decode("utf-8"))
    compass = json.loads(current["compass"].decode("utf-8"))
    _reject_recorded_next_operation(
        graph, manifest["next_operation"]["operation_id"]
    )
    try:
        bundle = tc.prepare_transaction(
            manifest,
            repo_root=repo_root,
            graph=graph,
            compass=compass,
            active_latch=latch,
        )
    except ValueError as error:
        raise ClockworkTickRejection("tick_transaction_prepare") from error
    bundle["projections"]["latch"]["protected_boundaries"] = list(
        intent["next_operation_protected_boundaries"]
    )
    validate_active_operation(bundle["projections"]["latch"])
    bundle["projection_sha256s"] = {
        key: tc.sha256(value) for key, value in bundle["projections"].items()
    }
    tc.validate_bundle(bundle, repo_root=repo_root)
    report = ariadne_compass.build_compass_report(
        bundle["projections"]["compass"],
        bundle["projections"]["graph"],
        repo_root=repo_root,
        require_evidence_files=False,
    )
    if report["status"] != "passed":
        _reject("tick_full_compass:" + ",".join(report["reasons"]))
    incident_register: dict[str, Any] | None = None
    incident_pattern: dict[str, Any] | None = None
    if intent["schema_version"] == TICK_INCIDENT_INTENT_VERSION:
        incident_register, incident_pattern = _project_incident_register(
            repo_root,
            contract,
            current,
            intent["agent_error_observations"],
        )
        _validate_incident_revision_artifact(
            repo_root,
            intent["baton_acceptance"]["paths"],
            incident_register,
            len(intent["agent_error_observations"]),
        )
    canonical = {
        "continuity": _json_text(bundle["projections"]["graph"]).encode("utf-8"),
        "compass": _json_text(bundle["projections"]["compass"]).encode("utf-8"),
        "compass_markdown": ariadne_compass.render_markdown(report).encode("utf-8"),
        "active_latch": _json_text(bundle["projections"]["latch"]).encode("utf-8"),
        "error_register": (
            _json_text(incident_register).encode("utf-8")
            if incident_register is not None
            else current["error_register"]
        ),
        "pattern_report": (
            _json_text(incident_pattern).encode("utf-8")
            if incident_pattern is not None
            else current["pattern_report"]
        ),
        "current_baton": _render_baton(
            current["current_baton"].decode("utf-8"),
            manifest=manifest,
            acceptance=intent["baton_acceptance"],
            graph=bundle["projections"]["graph"],
            compass=bundle["projections"]["compass"],
            source=source,
            compaction_manifest=baton_compaction_manifest,
            register=incident_register,
            incident_summaries=[
                item["baton_summary"]
                for item in intent.get("agent_error_observations", [])
            ],
        ).encode("utf-8"),
    }
    ownership = json.loads(prior_metadata["ownership.json"].decode("utf-8"))
    transaction = {
        "schema_version": TRANSACTION_VERSION,
        "operation_id": manifest["operation_id"],
        "transaction_id": bundle["transaction_id"],
        "source_commit": source,
        "previous_source_commit": source,
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_bundle_sha256": base_pointer["selected_bundle_sha256"],
        "previous_canonical_sha256s": {
            key: _hash_bytes(value) for key, value in current.items()
        },
        "previous_metadata_sha256s": {
            key: _hash_bytes(value) for key, value in prior_metadata.items()
        },
        "projection_sha256s": bundle["projection_sha256s"],
        "journal": bundle["journal"],
        "publication_mode": "lease_bound_pointer_last_live_tick",
        "event_kind": "clean_closeout",
        "next_boundaries_sha256": tc.sha256(
            intent["next_operation_protected_boundaries"]
        ),
        "register_bytes_preserved": canonical["error_register"]
        == current["error_register"],
        "pattern_bytes_preserved": canonical["pattern_report"]
        == current["pattern_report"],
    }
    metadata = {
        "command-manifest.json": _json_text(intent["command_manifest"]).encode(
            "utf-8"
        ),
        "transaction.json": _json_text(transaction).encode("utf-8"),
        "ownership.json": _json_text(ownership).encode("utf-8"),
    }
    canonical_sha256s = {
        key: _hash_bytes(value) for key, value in canonical.items()
    }
    metadata_sha256s = {key: _hash_bytes(value) for key, value in metadata.items()}
    bundle_sha256 = _hash_json(
        {"canonical": canonical_sha256s, "metadata": metadata_sha256s}
    )
    generation = {
        "schema_version": GENERATION_VERSION,
        "generation_id": "gen-" + bundle_sha256,
        "bundle_sha256": bundle_sha256,
        "source_commit": source,
        "previous_generation": {
            "generation_id": base_pointer["selected_generation_id"],
            "source_commit": source,
            "bundle_sha256": base_pointer["selected_bundle_sha256"],
            "canonical_sha256s": {
                key: _hash_bytes(value) for key, value in current.items()
            },
            "metadata_sha256s": {
                key: _hash_bytes(value) for key, value in prior_metadata.items()
            },
            "pointer_sha256": _hash_bytes(
                _git_bytes(
                    repo_root,
                    source,
                    f"{contract['clockwork_root']}/{POINTER_NAME}",
                )
            ),
        },
        "canonical_sha256s": canonical_sha256s,
        "metadata_sha256s": metadata_sha256s,
    }
    pointer = {
        "schema_version": base_pointer["schema_version"],
        "phase": "clockwork_active",
        "selected_generation_id": generation["generation_id"],
        "selected_bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_source_commit": source,
        "lease_sequence": base_pointer["lease_sequence"] + 1,
        "writer": WRITER,
    }
    prepared = {
        "schema_version": PREPARED_VERSION,
        "contract": contract,
        "intent": intent,
        "source_commit": source,
        "base_pointer": base_pointer,
        "canonical": canonical,
        "metadata": metadata,
        "generation_manifest": generation,
        "pointer": pointer,
    }
    validate_prepared_tick(repo_root, prepared)
    return prepared


def build_user_decision_tick_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Replace one blocked latch after an explicit user-selected outcome."""

    contract = validate_contract(contract_value)
    intent = validate_user_decision_tick_intent(intent_value, contract)
    live = validate_live_state(repo_root, contract)
    source = _assert_git_state(repo_root, contract)
    current, prior_metadata, base_pointer = _assert_clean_predecessor(
        repo_root, contract, source
    )
    prior_generation = json.loads(prior_metadata[GENERATION_NAME].decode("utf-8"))
    if (
        base_pointer.get("phase") != "clockwork_active"
        or base_pointer.get("writer") != WRITER
        or base_pointer.get("selected_generation_id") != live["generation_id"]
        or base_pointer.get("selected_bundle_sha256") != live["bundle_sha256"]
        or prior_generation.get("generation_id") != live["generation_id"]
    ):
        _reject("tick_predecessor_identity")

    source_latch = validate_active_operation(
        json.loads(current["active_latch"].decode("utf-8"))
    )
    graph = json.loads(current["continuity"].decode("utf-8"))
    compass = json.loads(current["compass"].decode("utf-8"))
    _reject_recorded_next_operation(
        graph, intent["next_operation"]["operation_id"]
    )
    next_latch = _derive_user_decision_latch(source_latch, intent, source)
    baton = _render_user_decision_baton(
        current["current_baton"].decode("utf-8"),
        intent=intent,
        graph=graph,
        compass=compass,
        source=source,
    )
    canonical = dict(current)
    canonical["active_latch"] = _json_text(next_latch).encode("utf-8")
    canonical["current_baton"] = baton.encode("utf-8")

    intent_sha256 = tc.sha256(intent)
    transaction_id = "txn-" + tc.sha256(
        {"user_decision_intent": intent_sha256, "head": source}
    )[7:31]
    journal_id = "journal-" + transaction_id[4:]
    events: list[dict[str, Any]] = []
    previous = tc.ZERO_DIGEST
    for event_type, payload in (
        (
            "user-decision-intent-accepted",
            {
                "intent_sha256": intent_sha256,
                "previous_operation_id": source_latch["operation_id"],
                "selected_outcome": intent["selected_outcome"],
            },
        ),
        ("git-source-resolved", {"source_commit": source}),
        (
            "active-operation-replaced",
            {
                "previous_operation_id": source_latch["operation_id"],
                "next_operation_id": next_latch["operation_id"],
            },
        ),
        (
            "replacement-latch-validated",
            {
                "status": "in_progress",
                "user_attention_required": False,
                "terminal_response_permitted": False,
            },
        ),
        (
            "transaction-prepared",
            {"publication_mode": "lease_bound_pointer_last_live_tick"},
        ),
    ):
        event = tc._event(
            journal_id=journal_id,
            transaction_id=transaction_id,
            operation_id=next_latch["operation_id"],
            sequence=len(events) + 1,
            previous=previous,
            event_type=event_type,
            payload=payload,
        )
        events.append(event)
        previous = event["event_sha256"]
    tc.validate_event_chain(events)

    projection_sha256s = {
        "latch": tc.sha256(next_latch),
        "current_baton": tc.sha256(baton),
    }
    transaction = {
        "schema_version": TRANSACTION_VERSION,
        "operation_id": next_latch["operation_id"],
        "transaction_id": transaction_id,
        "source_commit": source,
        "previous_source_commit": source,
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_bundle_sha256": base_pointer["selected_bundle_sha256"],
        "previous_canonical_sha256s": {
            key: _hash_bytes(value) for key, value in current.items()
        },
        "previous_metadata_sha256s": {
            key: _hash_bytes(value) for key, value in prior_metadata.items()
        },
        "projection_sha256s": projection_sha256s,
        "journal": events,
        "publication_mode": "lease_bound_pointer_last_live_tick",
        "event_kind": "user_decision_transition",
        "next_boundaries_sha256": tc.sha256(
            next_latch["protected_boundaries"]
        ),
        "register_bytes_preserved": True,
        "pattern_bytes_preserved": True,
    }
    ownership = json.loads(prior_metadata["ownership.json"].decode("utf-8"))
    metadata = {
        "command-manifest.json": _json_text(intent["command_manifest"]).encode(
            "utf-8"
        ),
        "transaction.json": _json_text(transaction).encode("utf-8"),
        "ownership.json": _json_text(ownership).encode("utf-8"),
    }
    canonical_sha256s = {
        key: _hash_bytes(value) for key, value in canonical.items()
    }
    metadata_sha256s = {
        key: _hash_bytes(value) for key, value in metadata.items()
    }
    bundle_sha256 = _hash_json(
        {"canonical": canonical_sha256s, "metadata": metadata_sha256s}
    )
    generation = {
        "schema_version": GENERATION_VERSION,
        "generation_id": "gen-" + bundle_sha256,
        "bundle_sha256": bundle_sha256,
        "source_commit": source,
        "previous_generation": {
            "generation_id": base_pointer["selected_generation_id"],
            "source_commit": source,
            "bundle_sha256": base_pointer["selected_bundle_sha256"],
            "canonical_sha256s": {
                key: _hash_bytes(value) for key, value in current.items()
            },
            "metadata_sha256s": {
                key: _hash_bytes(value) for key, value in prior_metadata.items()
            },
            "pointer_sha256": _hash_bytes(
                _git_bytes(
                    repo_root,
                    source,
                    f"{contract['clockwork_root']}/{POINTER_NAME}",
                )
            ),
        },
        "canonical_sha256s": canonical_sha256s,
        "metadata_sha256s": metadata_sha256s,
    }
    pointer = {
        "schema_version": base_pointer["schema_version"],
        "phase": "clockwork_active",
        "selected_generation_id": generation["generation_id"],
        "selected_bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_source_commit": source,
        "lease_sequence": base_pointer["lease_sequence"] + 1,
        "writer": WRITER,
    }
    prepared = {
        "schema_version": PREPARED_VERSION,
        "contract": contract,
        "intent": intent,
        "source_commit": source,
        "base_pointer": base_pointer,
        "canonical": canonical,
        "metadata": metadata,
        "generation_manifest": generation,
        "pointer": pointer,
    }
    validate_prepared_tick(repo_root, prepared)
    return prepared


def build_checkpoint_tick_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Advance one in-progress checkpoint without accepting a graph node."""

    contract = validate_contract(contract_value)
    intent = validate_checkpoint_tick_intent(intent_value, contract)
    live = validate_live_state(repo_root, contract)
    source = _assert_git_state(repo_root, contract)
    current, prior_metadata, base_pointer = _assert_clean_predecessor(
        repo_root, contract, source
    )
    prior_generation = json.loads(prior_metadata[GENERATION_NAME].decode("utf-8"))
    if (
        base_pointer.get("phase") != "clockwork_active"
        or base_pointer.get("writer") != WRITER
        or base_pointer.get("selected_generation_id") != live["generation_id"]
        or base_pointer.get("selected_bundle_sha256") != live["bundle_sha256"]
        or prior_generation.get("generation_id") != live["generation_id"]
    ):
        _reject("tick_predecessor_identity")

    source_latch = validate_active_operation(
        json.loads(current["active_latch"].decode("utf-8"))
    )
    next_latch = _derive_checkpoint_latch(source_latch, intent, source)
    graph = json.loads(current["continuity"].decode("utf-8"))
    compass = json.loads(current["compass"].decode("utf-8"))
    baton = _render_checkpoint_baton(
        current["current_baton"].decode("utf-8"),
        graph=graph,
        compass=compass,
        source=source,
    )
    canonical = dict(current)
    canonical["active_latch"] = _json_text(next_latch).encode("utf-8")
    canonical["current_baton"] = baton.encode("utf-8")

    intent_sha256 = tc.sha256(intent)
    transaction_id = "txn-" + tc.sha256(
        {"checkpoint_intent": intent_sha256, "head": source}
    )[7:31]
    journal_id = "journal-" + transaction_id[4:]
    events: list[dict[str, Any]] = []
    previous = tc.ZERO_DIGEST
    for event_type, payload in (
        (
            "checkpoint-intent-accepted",
            {
                "intent_sha256": intent_sha256,
                "previous_next_executable_stage": source_latch["checkpoint"][
                    "next_executable_stage"
                ],
            },
        ),
        ("git-source-resolved", {"source_commit": source}),
        (
            "active-operation-checkpoint-advanced",
            {
                "operation_id": next_latch["operation_id"],
                "next_executable_stage": next_latch["checkpoint"][
                    "next_executable_stage"
                ],
            },
        ),
        (
            "checkpoint-latch-validated",
            {"status": "in_progress", "terminal_response_permitted": False},
        ),
        (
            "transaction-prepared",
            {"publication_mode": "lease_bound_pointer_last_live_tick"},
        ),
    ):
        event = tc._event(
            journal_id=journal_id,
            transaction_id=transaction_id,
            operation_id=next_latch["operation_id"],
            sequence=len(events) + 1,
            previous=previous,
            event_type=event_type,
            payload=payload,
        )
        events.append(event)
        previous = event["event_sha256"]
    tc.validate_event_chain(events)

    projection_sha256s = {
        "latch": tc.sha256(next_latch),
        "current_baton": tc.sha256(baton),
    }
    transaction = {
        "schema_version": TRANSACTION_VERSION,
        "operation_id": next_latch["operation_id"],
        "transaction_id": transaction_id,
        "source_commit": source,
        "previous_source_commit": source,
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_bundle_sha256": base_pointer["selected_bundle_sha256"],
        "previous_canonical_sha256s": {
            key: _hash_bytes(value) for key, value in current.items()
        },
        "previous_metadata_sha256s": {
            key: _hash_bytes(value) for key, value in prior_metadata.items()
        },
        "projection_sha256s": projection_sha256s,
        "journal": events,
        "publication_mode": "lease_bound_pointer_last_live_tick",
        "event_kind": "checkpoint_transition",
        "next_boundaries_sha256": tc.sha256(
            next_latch["protected_boundaries"]
        ),
        "register_bytes_preserved": True,
        "pattern_bytes_preserved": True,
    }
    ownership = json.loads(prior_metadata["ownership.json"].decode("utf-8"))
    metadata = {
        "command-manifest.json": _json_text(intent["command_manifest"]).encode(
            "utf-8"
        ),
        "transaction.json": _json_text(transaction).encode("utf-8"),
        "ownership.json": _json_text(ownership).encode("utf-8"),
    }
    canonical_sha256s = {
        key: _hash_bytes(value) for key, value in canonical.items()
    }
    metadata_sha256s = {
        key: _hash_bytes(value) for key, value in metadata.items()
    }
    bundle_sha256 = _hash_json(
        {"canonical": canonical_sha256s, "metadata": metadata_sha256s}
    )
    generation = {
        "schema_version": GENERATION_VERSION,
        "generation_id": "gen-" + bundle_sha256,
        "bundle_sha256": bundle_sha256,
        "source_commit": source,
        "previous_generation": {
            "generation_id": base_pointer["selected_generation_id"],
            "source_commit": source,
            "bundle_sha256": base_pointer["selected_bundle_sha256"],
            "canonical_sha256s": {
                key: _hash_bytes(value) for key, value in current.items()
            },
            "metadata_sha256s": {
                key: _hash_bytes(value) for key, value in prior_metadata.items()
            },
            "pointer_sha256": _hash_bytes(
                _git_bytes(
                    repo_root,
                    source,
                    f"{contract['clockwork_root']}/{POINTER_NAME}",
                )
            ),
        },
        "canonical_sha256s": canonical_sha256s,
        "metadata_sha256s": metadata_sha256s,
    }
    pointer = {
        "schema_version": base_pointer["schema_version"],
        "phase": "clockwork_active",
        "selected_generation_id": generation["generation_id"],
        "selected_bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_source_commit": source,
        "lease_sequence": base_pointer["lease_sequence"] + 1,
        "writer": WRITER,
    }
    prepared = {
        "schema_version": PREPARED_VERSION,
        "contract": contract,
        "intent": intent,
        "source_commit": source,
        "base_pointer": base_pointer,
        "canonical": canonical,
        "metadata": metadata,
        "generation_manifest": generation,
        "pointer": pointer,
    }
    validate_prepared_tick(repo_root, prepared)
    return prepared


def build_blocked_tick_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Derive one pointer-last blocked latch transition with no acceptance."""

    contract = validate_contract(contract_value)
    intent = validate_blocked_tick_intent(intent_value, contract)
    live = validate_live_state(repo_root, contract)
    source = _assert_git_state(repo_root, contract)
    current, prior_metadata, base_pointer = _assert_clean_predecessor(
        repo_root, contract, source
    )
    prior_generation = json.loads(prior_metadata[GENERATION_NAME].decode("utf-8"))
    if (
        base_pointer.get("phase") != "clockwork_active"
        or base_pointer.get("writer") != WRITER
        or base_pointer.get("selected_generation_id") != live["generation_id"]
        or base_pointer.get("selected_bundle_sha256") != live["bundle_sha256"]
        or prior_generation.get("generation_id") != live["generation_id"]
    ):
        _reject("tick_predecessor_identity")

    source_latch = validate_active_operation(
        json.loads(current["active_latch"].decode("utf-8"))
    )
    blocked_latch = _derive_blocked_latch(source_latch, intent)
    canonical = dict(current)
    canonical["active_latch"] = _json_text(blocked_latch).encode("utf-8")

    intent_sha256 = tc.sha256(intent)
    transaction_id = "txn-" + tc.sha256(
        {"blocked_intent": intent_sha256, "head": source}
    )[7:31]
    journal_id = "journal-" + transaction_id[4:]
    events: list[dict[str, Any]] = []
    previous = tc.ZERO_DIGEST
    for event_type, payload in (
        (
            "blocked-transition-intent-accepted",
            {"intent_sha256": intent_sha256},
        ),
        ("git-source-resolved", {"source_commit": source}),
        (
            "blocked-latch-reduced",
            {
                "status": "blocked",
                "verification_counter": blocked_latch["checkpoint"][
                    "retry_counters"
                ]["verification"],
            },
        ),
        (
            "blocked-latch-validated",
            {"user_attention_required": True, "terminal_response_permitted": True},
        ),
        (
            "transaction-prepared",
            {"publication_mode": "lease_bound_pointer_last_live_tick"},
        ),
    ):
        event = tc._event(
            journal_id=journal_id,
            transaction_id=transaction_id,
            operation_id=intent["operation_id"],
            sequence=len(events) + 1,
            previous=previous,
            event_type=event_type,
            payload=payload,
        )
        events.append(event)
        previous = event["event_sha256"]
    tc.validate_event_chain(events)

    transaction = {
        "schema_version": TRANSACTION_VERSION,
        "operation_id": intent["operation_id"],
        "transaction_id": transaction_id,
        "source_commit": source,
        "previous_source_commit": source,
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_bundle_sha256": base_pointer["selected_bundle_sha256"],
        "previous_canonical_sha256s": {
            key: _hash_bytes(value) for key, value in current.items()
        },
        "previous_metadata_sha256s": {
            key: _hash_bytes(value) for key, value in prior_metadata.items()
        },
        "projection_sha256s": {"latch": tc.sha256(blocked_latch)},
        "journal": events,
        "publication_mode": "lease_bound_pointer_last_live_tick",
        "event_kind": "blocked_transition",
        "next_boundaries_sha256": tc.sha256(
            blocked_latch["protected_boundaries"]
        ),
        "register_bytes_preserved": True,
        "pattern_bytes_preserved": True,
    }
    ownership = json.loads(prior_metadata["ownership.json"].decode("utf-8"))
    metadata = {
        "command-manifest.json": _json_text(intent["command_manifest"]).encode(
            "utf-8"
        ),
        "transaction.json": _json_text(transaction).encode("utf-8"),
        "ownership.json": _json_text(ownership).encode("utf-8"),
    }
    canonical_sha256s = {
        key: _hash_bytes(value) for key, value in canonical.items()
    }
    metadata_sha256s = {
        key: _hash_bytes(value) for key, value in metadata.items()
    }
    bundle_sha256 = _hash_json(
        {"canonical": canonical_sha256s, "metadata": metadata_sha256s}
    )
    generation = {
        "schema_version": GENERATION_VERSION,
        "generation_id": "gen-" + bundle_sha256,
        "bundle_sha256": bundle_sha256,
        "source_commit": source,
        "previous_generation": {
            "generation_id": base_pointer["selected_generation_id"],
            "source_commit": source,
            "bundle_sha256": base_pointer["selected_bundle_sha256"],
            "canonical_sha256s": {
                key: _hash_bytes(value) for key, value in current.items()
            },
            "metadata_sha256s": {
                key: _hash_bytes(value) for key, value in prior_metadata.items()
            },
            "pointer_sha256": _hash_bytes(
                _git_bytes(
                    repo_root,
                    source,
                    f"{contract['clockwork_root']}/{POINTER_NAME}",
                )
            ),
        },
        "canonical_sha256s": canonical_sha256s,
        "metadata_sha256s": metadata_sha256s,
    }
    pointer = {
        "schema_version": base_pointer["schema_version"],
        "phase": "clockwork_active",
        "selected_generation_id": generation["generation_id"],
        "selected_bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": base_pointer["selected_generation_id"],
        "previous_source_commit": source,
        "lease_sequence": base_pointer["lease_sequence"] + 1,
        "writer": WRITER,
    }
    prepared = {
        "schema_version": PREPARED_VERSION,
        "contract": contract,
        "intent": intent,
        "source_commit": source,
        "base_pointer": base_pointer,
        "canonical": canonical,
        "metadata": metadata,
        "generation_manifest": generation,
        "pointer": pointer,
    }
    validate_prepared_tick(repo_root, prepared)
    return prepared


def validate_prepared_tick(
    repo_root: Path, value: object
) -> dict[str, Any]:
    row = _exact(
        value,
        {
            "schema_version",
            "contract",
            "intent",
            "source_commit",
            "base_pointer",
            "canonical",
            "metadata",
            "generation_manifest",
            "pointer",
        },
        "tick_prepared_keys",
    )
    if row["schema_version"] != PREPARED_VERSION:
        _reject("tick_prepared_version")
    contract = validate_contract(row["contract"])
    intent = _validate_any_intent(row["intent"], contract)
    source = row["source_commit"]
    generation = row["generation_manifest"]
    pointer = row["pointer"]
    base_pointer = row["base_pointer"]
    if (
        not isinstance(source, str)
        or HEX40.fullmatch(source) is None
        or generation.get("schema_version") != GENERATION_VERSION
        or pointer.get("writer") != WRITER
        or pointer.get("phase") != "clockwork_active"
        or pointer.get("selected_generation_id") != generation.get("generation_id")
        or pointer.get("selected_bundle_sha256") != generation.get("bundle_sha256")
        or not isinstance(generation.get("bundle_sha256"), str)
        or HEX64.fullmatch(generation["bundle_sha256"]) is None
        or generation.get("generation_id") != "gen-" + generation["bundle_sha256"]
        or pointer.get("previous_generation_id")
        != base_pointer.get("selected_generation_id")
        or pointer.get("previous_source_commit") != source
        or pointer.get("lease_sequence") != base_pointer.get("lease_sequence") + 1
    ):
        _reject("tick_prepared_identity")
    if set(row["canonical"]) != set(CANONICAL_KEYS) or set(row["metadata"]) != set(
        METADATA_NAMES
    ):
        _reject("tick_prepared_files")
    canonical_sha256s = {
        key: _hash_bytes(value) for key, value in row["canonical"].items()
    }
    metadata_sha256s = {
        key: _hash_bytes(value) for key, value in row["metadata"].items()
    }
    if (
        generation.get("canonical_sha256s") != canonical_sha256s
        or generation.get("metadata_sha256s") != metadata_sha256s
        or generation.get("bundle_sha256")
        != _hash_json(
            {"canonical": canonical_sha256s, "metadata": metadata_sha256s}
        )
    ):
        _reject("tick_prepared_digest")
    prior = generation.get("previous_generation")
    source_canonical = _source_bytes(repo_root, contract, source)
    source_metadata = _source_metadata(repo_root, contract, source)
    source_pointer_bytes = _git_bytes(
        repo_root, source, f"{contract['clockwork_root']}/{POINTER_NAME}"
    )
    if (
        not isinstance(prior, dict)
        or prior.get("generation_id") != base_pointer.get("selected_generation_id")
        or prior.get("bundle_sha256") != base_pointer.get("selected_bundle_sha256")
        or prior.get("source_commit") != source
        or prior.get("canonical_sha256s")
        != {key: _hash_bytes(value) for key, value in source_canonical.items()}
        or prior.get("metadata_sha256s")
        != {key: _hash_bytes(value) for key, value in source_metadata.items()}
        or prior.get("pointer_sha256") != _hash_bytes(source_pointer_bytes)
    ):
        _reject("tick_predecessor_digest")
    graph = json.loads(row["canonical"]["continuity"].decode("utf-8"))
    compass = json.loads(row["canonical"]["compass"].decode("utf-8"))
    latch = json.loads(row["canonical"]["active_latch"].decode("utf-8"))
    ownership = json.loads(row["metadata"]["ownership.json"].decode("utf-8"))
    command_manifest = json.loads(
        row["metadata"]["command-manifest.json"].decode("utf-8")
    )
    transaction = _exact(
        json.loads(row["metadata"]["transaction.json"].decode("utf-8")),
        TRANSACTION_KEYS,
        "tick_prepared_transaction_keys",
    )
    if (
        set(ownership.get("surface_owners", {}).values()) != {WRITER}
        or len(ownership.get("surface_owners", {})) != 10
        or set(ownership.get("legacy_writers", {}).values()) != {"retired"}
        or command_manifest != intent["command_manifest"]
        or transaction["schema_version"] != TRANSACTION_VERSION
        or transaction["operation_id"] != _intent_operation_id(intent)
        or transaction["source_commit"] != source
        or transaction["previous_source_commit"] != source
        or transaction["previous_generation_id"]
        != base_pointer["selected_generation_id"]
        or transaction["previous_bundle_sha256"]
        != base_pointer["selected_bundle_sha256"]
        or transaction["previous_canonical_sha256s"]
        != prior["canonical_sha256s"]
        or transaction["previous_metadata_sha256s"]
        != prior["metadata_sha256s"]
    ):
        _reject("tick_prepared_semantics")
    if intent["schema_version"] in {
        TICK_INTENT_VERSION,
        TICK_INCIDENT_INTENT_VERSION,
    }:
        manifest = intent["transaction_manifest"]
        if (
            graph["nodes"][-1]["id"] != manifest["operation_id"]
            or compass["current_position"]["node_id"] != manifest["operation_id"]
            or latch["operation_id"]
            != manifest["next_operation"]["operation_id"]
            or latch["protected_boundaries"]
            != intent["next_operation_protected_boundaries"]
            or transaction["event_kind"] != "clean_closeout"
            or transaction["next_boundaries_sha256"]
            != tc.sha256(intent["next_operation_protected_boundaries"])
        ):
            _reject("tick_prepared_semantics")
    elif intent["schema_version"] == BLOCKED_INTENT_VERSION:
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        expected_latch = _derive_blocked_latch(source_latch, intent)
        preserved = set(CANONICAL_KEYS) - {"active_latch"}
        if (
            any(
                row["canonical"][key] != source_canonical[key]
                for key in preserved
            )
            or latch != expected_latch
            or transaction["event_kind"] != "blocked_transition"
            or transaction["projection_sha256s"]
            != {"latch": tc.sha256(expected_latch)}
            or transaction["next_boundaries_sha256"]
            != tc.sha256(source_latch["protected_boundaries"])
            or not transaction["register_bytes_preserved"]
            or not transaction["pattern_bytes_preserved"]
        ):
            _reject("blocked_tick_prepared_semantics")
    elif intent["schema_version"] == USER_DECISION_INTENT_VERSION:
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        expected_latch = _derive_user_decision_latch(source_latch, intent, source)
        expected_baton = _render_user_decision_baton(
            source_canonical["current_baton"].decode("utf-8"),
            intent=intent,
            graph=json.loads(source_canonical["continuity"].decode("utf-8")),
            compass=json.loads(source_canonical["compass"].decode("utf-8")),
            source=source,
        ).encode("utf-8")
        preserved = set(CANONICAL_KEYS) - {"active_latch", "current_baton"}
        expected_projection_sha256s = {
            "latch": tc.sha256(expected_latch),
            "current_baton": tc.sha256(expected_baton.decode("utf-8")),
        }
        if (
            any(row["canonical"][key] != source_canonical[key] for key in preserved)
            or latch != expected_latch
            or row["canonical"]["current_baton"] != expected_baton
            or transaction["event_kind"] != "user_decision_transition"
            or transaction["projection_sha256s"] != expected_projection_sha256s
            or transaction["next_boundaries_sha256"]
            != tc.sha256(expected_latch["protected_boundaries"])
            or not transaction["register_bytes_preserved"]
            or not transaction["pattern_bytes_preserved"]
        ):
            _reject("user_decision_tick_prepared_semantics")
    else:
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        expected_latch = _derive_checkpoint_latch(source_latch, intent, source)
        expected_baton = _render_checkpoint_baton(
            source_canonical["current_baton"].decode("utf-8"),
            graph=json.loads(source_canonical["continuity"].decode("utf-8")),
            compass=json.loads(source_canonical["compass"].decode("utf-8")),
            source=source,
        ).encode("utf-8")
        preserved = set(CANONICAL_KEYS) - {"active_latch", "current_baton"}
        expected_projection_sha256s = {
            "latch": tc.sha256(expected_latch),
            "current_baton": tc.sha256(expected_baton.decode("utf-8")),
        }
        if (
            any(row["canonical"][key] != source_canonical[key] for key in preserved)
            or latch != expected_latch
            or row["canonical"]["current_baton"] != expected_baton
            or transaction["event_kind"] != "checkpoint_transition"
            or transaction["projection_sha256s"] != expected_projection_sha256s
            or transaction["next_boundaries_sha256"]
            != tc.sha256(expected_latch["protected_boundaries"])
            or not transaction["register_bytes_preserved"]
            or not transaction["pattern_bytes_preserved"]
        ):
            _reject("checkpoint_tick_prepared_semantics")
    if intent["schema_version"] == TICK_INCIDENT_INTENT_VERSION:
        expected_register, expected_pattern = _project_incident_register(
            repo_root,
            contract,
            source_canonical,
            intent["agent_error_observations"],
        )
        if (
            row["canonical"]["error_register"]
            != _json_text(expected_register).encode("utf-8")
            or row["canonical"]["pattern_report"]
            != _json_text(expected_pattern).encode("utf-8")
            or transaction["register_bytes_preserved"]
            or transaction["pattern_bytes_preserved"]
        ):
            _reject("tick_incident_projection_changed")
    elif (
        row["canonical"]["error_register"] != source_canonical["error_register"]
        or row["canonical"]["pattern_report"] != source_canonical["pattern_report"]
    ):
        _reject("tick_register_pattern_changed")
    return row


def validate_tick_live_state(
    repo_root: Path, contract_value: object
) -> dict[str, Any]:
    contract = validate_contract(contract_value)
    base = validate_live_state(repo_root, contract)
    root = _clockwork_root(repo_root, contract)
    generation = _load(root / GENERATION_NAME)
    pointer = _load(root / POINTER_NAME)
    transaction = _exact(
        _load(root / "transaction.json"),
        TRANSACTION_KEYS,
        "tick_live_transaction_keys",
    )
    graph = _load(repo_root / contract["canonical_paths"]["continuity"])
    latch = validate_active_operation(
        _load(repo_root / contract["canonical_paths"]["active_latch"])
    )
    event_kind = transaction.get("event_kind")
    if (
        generation.get("schema_version") != GENERATION_VERSION
        or transaction.get("schema_version") != TRANSACTION_VERSION
        or transaction.get("source_commit") != generation.get("source_commit")
        or transaction.get("previous_source_commit")
        != pointer.get("previous_source_commit")
        or transaction.get("previous_generation_id")
        != pointer.get("previous_generation_id")
        or transaction.get("next_boundaries_sha256")
        != tc.sha256(latch["protected_boundaries"])
    ):
        _reject("tick_live_metadata")
    if event_kind == "clean_closeout":
        if transaction.get("operation_id") != graph["nodes"][-1]["id"]:
            _reject("tick_live_operation")
    elif event_kind == "blocked_transition":
        if (
            transaction.get("operation_id") != latch["operation_id"]
            or latch["status"] != "blocked"
            or transaction.get("projection_sha256s")
            != {"latch": tc.sha256(latch)}
        ):
            _reject("tick_live_blocked_operation")
    elif event_kind == "user_decision_transition":
        if (
            transaction.get("operation_id") != latch["operation_id"]
            or latch["status"] != "in_progress"
            or transaction.get("projection_sha256s")
            != {
                "latch": tc.sha256(latch),
                "current_baton": tc.sha256(
                    (repo_root / contract["canonical_paths"]["current_baton"])
                    .read_text(encoding="utf-8")
                ),
            }
        ):
            _reject("tick_live_user_decision_operation")
    elif event_kind == "checkpoint_transition":
        if (
            transaction.get("operation_id") != latch["operation_id"]
            or latch["status"] != "in_progress"
            or latch["source_head"] != transaction.get("source_commit")
            or transaction.get("projection_sha256s")
            != {
                "latch": tc.sha256(latch),
                "current_baton": tc.sha256(
                    (repo_root / contract["canonical_paths"]["current_baton"])
                    .read_text(encoding="utf-8")
                ),
            }
        ):
            _reject("tick_live_checkpoint_operation")
    else:
        _reject("tick_live_event_kind")
    prior = generation.get("previous_generation")
    source = pointer.get("previous_source_commit")
    if not isinstance(source, str) or HEX40.fullmatch(source) is None:
        _reject("tick_live_predecessor_source")
    source_canonical = _source_bytes(repo_root, contract, source)
    source_metadata = _source_metadata(repo_root, contract, source)
    source_pointer = _source_pointer(repo_root, contract, source)
    if (
        not isinstance(prior, dict)
        or prior.get("generation_id") != pointer.get("previous_generation_id")
        or prior.get("generation_id") != source_pointer.get("selected_generation_id")
        or prior.get("bundle_sha256")
        != source_pointer.get("selected_bundle_sha256")
        or transaction.get("previous_bundle_sha256")
        != prior.get("bundle_sha256")
        or prior.get("canonical_sha256s")
        != {key: _hash_bytes(value) for key, value in source_canonical.items()}
        or prior.get("metadata_sha256s")
        != {key: _hash_bytes(value) for key, value in source_metadata.items()}
        or prior.get("pointer_sha256")
        != _hash_bytes(
            _git_bytes(
                repo_root, source, f"{contract['clockwork_root']}/{POINTER_NAME}"
            )
        )
    ):
        _reject("tick_live_predecessor_drift")
    if event_kind == "blocked_transition":
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        preserved = set(CANONICAL_KEYS) - {"active_latch"}
        if (
            source_latch["status"] != "in_progress"
            or source_latch["operation_id"] != latch["operation_id"]
            or any(
                (repo_root / contract["canonical_paths"][key]).read_bytes()
                != source_canonical[key]
                for key in preserved
            )
        ):
            _reject("tick_live_blocked_preservation")
    elif event_kind == "user_decision_transition":
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        preserved = set(CANONICAL_KEYS) - {"active_latch", "current_baton"}
        journal = transaction.get("journal")
        first_payload = (
            journal[0].get("payload", {})
            if isinstance(journal, list) and journal
            else {}
        )
        if (
            source_latch["status"] != "blocked"
            or source_latch["operation_id"]
            != first_payload.get("previous_operation_id")
            or source_latch["operation_id"] == latch["operation_id"]
            or any(
                (repo_root / contract["canonical_paths"][key]).read_bytes()
                != source_canonical[key]
                for key in preserved
            )
        ):
            _reject("tick_live_user_decision_preservation")
    elif event_kind == "checkpoint_transition":
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        preserved = set(CANONICAL_KEYS) - {"active_latch", "current_baton"}
        journal = transaction.get("journal")
        first_payload = (
            journal[0].get("payload", {})
            if isinstance(journal, list) and journal
            else {}
        )
        if (
            source_latch["status"] != "in_progress"
            or source_latch["operation_id"] != latch["operation_id"]
            or source_latch["checkpoint"]["next_executable_stage"]
            != first_payload.get("previous_next_executable_stage")
            or source_latch["checkpoint"]["next_executable_stage"]
            == latch["checkpoint"]["next_executable_stage"]
            or any(
                (repo_root / contract["canonical_paths"][key]).read_bytes()
                != source_canonical[key]
                for key in preserved
            )
        ):
            _reject("tick_live_checkpoint_preservation")
    return {
        **base,
        "schema_version": "ariadne.governance_live_tick_state.v1",
        "operation_id": transaction["operation_id"],
        "event_kind": event_kind,
        "previous_generation_id": prior["generation_id"],
        "previous_metadata_files": len(source_metadata),
    }


def _write_lease(path: Path, *, operation_id: str, source: str, pointer: dict[str, Any]) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError as error:
        raise ClockworkTickRejection("tick_lease_occupied") from error
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as lease:
        lease.write(
            _json_text(
                {
                    "schema_version": "ariadne.governance_live_lease.v1",
                    "operation_id": operation_id,
                    "source_commit": source,
                    "previous_generation_id": pointer["previous_generation_id"],
                    "sequence": pointer["lease_sequence"],
                }
            )
        )


def publish_tick_generation(
    repo_root: Path,
    prepared_value: object,
    *,
    writer_id: str,
    fail_at: str | None = None,
) -> dict[str, Any]:
    """Publish one prepared tick, committing only when the pointer is replaced."""

    prepared = validate_prepared_tick(repo_root, prepared_value)
    contract = prepared["contract"]
    if writer_id != WRITER:
        _reject("tick_writer_not_clockwork")
    _assert_git_state(repo_root, contract, prepared["source_commit"])
    root = _clockwork_root(repo_root, contract)
    pointer_path = root / POINTER_NAME
    current_pointer = _load(pointer_path)
    if current_pointer.get("selected_generation_id") == prepared["pointer"][
        "selected_generation_id"
    ]:
        return validate_tick_live_state(repo_root, contract)
    if current_pointer != prepared["base_pointer"]:
        _reject("tick_stale_predecessor")
    _assert_clean_predecessor(repo_root, contract, prepared["source_commit"])
    lease_path = root / "writer.lock"
    _write_lease(
        lease_path,
        operation_id=_intent_operation_id(prepared["intent"]),
        source=prepared["source_commit"],
        pointer=prepared["pointer"],
    )
    canonical_targets = {
        key: repo_root / relative for key, relative in contract["canonical_paths"].items()
    }
    metadata_values = {
        **prepared["metadata"],
        GENERATION_NAME: _json_text(prepared["generation_manifest"]).encode("utf-8"),
    }
    metadata_targets = {name: root / name for name in metadata_values}
    original_canonical = {key: path.read_bytes() for key, path in canonical_targets.items()}
    original_metadata = {name: path.read_bytes() for name, path in metadata_targets.items()}
    original_pointer = pointer_path.read_bytes()
    staged: dict[str, Path] = {}
    committed = False
    try:
        for key, target in canonical_targets.items():
            staged[f"canonical:{key}"] = _write_temp(target, prepared["canonical"][key])
        for name, target in metadata_targets.items():
            staged[f"metadata:{name}"] = _write_temp(target, metadata_values[name])
        staged["pointer"] = _write_temp(
            pointer_path, _json_text(prepared["pointer"]).encode("utf-8")
        )
        for key in CANONICAL_KEYS:
            if fail_at == f"before:{key}":
                raise OSError("injected_tick_precommit_failure")
            os.replace(staged.pop(f"canonical:{key}"), canonical_targets[key])
            if fail_at == f"after:{key}":
                raise OSError("injected_tick_precommit_failure")
        for name in metadata_values:
            if fail_at == f"before:{name}":
                raise OSError("injected_tick_precommit_failure")
            os.replace(staged.pop(f"metadata:{name}"), metadata_targets[name])
            if fail_at == f"after:{name}":
                raise OSError("injected_tick_precommit_failure")
        if fail_at == "before_pointer_replace":
            raise OSError("injected_tick_precommit_failure")
        os.replace(staged.pop("pointer"), pointer_path)
        committed = True
        state = validate_tick_live_state(repo_root, contract)
        if fail_at == "after_pointer_replace":
            raise CommittedClockworkTick("injected_tick_postcommit_failure")
        return state
    except BaseException:
        if not committed:
            for key, target in canonical_targets.items():
                target.write_bytes(original_canonical[key])
            for name, target in metadata_targets.items():
                target.write_bytes(original_metadata[name])
            pointer_path.write_bytes(original_pointer)
            if (
                {key: path.read_bytes() for key, path in canonical_targets.items()}
                != original_canonical
                or {name: path.read_bytes() for name, path in metadata_targets.items()}
                != original_metadata
                or pointer_path.read_bytes() != original_pointer
            ):
                _reject("tick_rollback_reread")
        raise
    finally:
        for path in staged.values():
            path.unlink(missing_ok=True)
        lease_path.unlink(missing_ok=True)


def rollback_tick_generation(
    repo_root: Path, contract_value: object, *, writer_id: str
) -> dict[str, Any]:
    """Restore the immediately previous active clockwork generation."""

    contract = validate_contract(contract_value)
    if writer_id != WRITER:
        _reject("tick_writer_not_clockwork")
    state = validate_tick_live_state(repo_root, contract)
    root = _clockwork_root(repo_root, contract)
    pointer_path = root / POINTER_NAME
    pointer = _load(pointer_path)
    source = pointer["previous_source_commit"]
    previous_canonical = _source_bytes(repo_root, contract, source)
    previous_metadata = _source_metadata(repo_root, contract, source)
    previous_pointer = _source_pointer(repo_root, contract, source)
    restored_pointer = {
        **previous_pointer,
        "lease_sequence": pointer["lease_sequence"] + 1,
    }
    lease_path = root / "writer.lock"
    _write_lease(
        lease_path,
        operation_id=state["operation_id"],
        source=source,
        pointer={**restored_pointer, "previous_generation_id": previous_pointer["selected_generation_id"]},
    )
    canonical_targets = {
        key: repo_root / relative for key, relative in contract["canonical_paths"].items()
    }
    metadata_targets = {name: root / name for name in PREDECESSOR_METADATA_NAMES}
    current_canonical = {key: path.read_bytes() for key, path in canonical_targets.items()}
    current_metadata = {name: path.read_bytes() for name, path in metadata_targets.items()}
    current_pointer = pointer_path.read_bytes()
    committed = False
    try:
        for key, target in canonical_targets.items():
            os.replace(_write_temp(target, previous_canonical[key]), target)
        for name, target in metadata_targets.items():
            os.replace(_write_temp(target, previous_metadata[name]), target)
        os.replace(
            _write_temp(pointer_path, _json_text(restored_pointer).encode("utf-8")),
            pointer_path,
        )
        committed = True
        restored = validate_live_state(repo_root, contract)
        return {
            "schema_version": "ariadne.governance_live_tick_rollback.v1",
            "status": "passed",
            "rolled_back_from_generation_id": state["generation_id"],
            "selected_generation_id": restored["generation_id"],
            "previous_source_commit": source,
            "lease_sequence": restored_pointer["lease_sequence"],
            "byte_exact": True,
        }
    except BaseException:
        if not committed:
            for key, target in canonical_targets.items():
                target.write_bytes(current_canonical[key])
            for name, target in metadata_targets.items():
                target.write_bytes(current_metadata[name])
            pointer_path.write_bytes(current_pointer)
        raise
    finally:
        lease_path.unlink(missing_ok=True)
