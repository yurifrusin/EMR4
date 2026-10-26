"""Generic pointer-last ticks for the live Ariadne governance clockwork."""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, NoReturn

from jsonschema.exceptions import SchemaError, ValidationError

from orchestration_harness import transactional_closeout as tc
from orchestration_harness.active_operation import validate_active_operation
from orchestration_harness.governance_live_adoption import (
    AdoptionRejection,
    CANONICAL_KEYS,
    COMMAND_VERSION,
    GENERATION_VERSION,
    METADATA_NAMES,
    OWNERSHIP_VERSION,
    POINTER_VERSION,
    WRITER,
    _all_keys,
    _assert_git_state,
    _canonical_paths_match_source,
    _exact,
    _git,
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
from orchestration_harness.verification_envelope import (
    validate_database_authority,
    validate_phase_order,
    validate_runner_for_authority,
    validate_verification_phase,
)


TICK_INTENT_VERSION = "ariadne.governance_live_tick_intent.v1"
GOVERNANCE_COMMAND_VERSION_V2 = "ariadne.governance_command_manifest.v2"
TICK_INCIDENT_INTENT_VERSION = "ariadne.governance_live_tick_intent.v2"
SEMANTIC_TICK_INTENT_VERSION = "ariadne.governance_semantic_closeout_intent.v1"
SEMANTIC_PROFILE = "provider_free_governance_tooling_v1"
SEMANTIC_BATON_SLOT = "current_deepseek_native_harness_acceptance"
SEMANTIC_VERIFICATION_PROFILE = "governance_clockwork_core_v1"
SEMANTIC_BATON_LABEL = "Current DeepSeek native Harness acceptance"
SEMANTIC_MATERIALIZATION_VERSION = (
    "ariadne.governance_semantic_evidence_materialization.v1"
)
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
PAUSE_INTENT_VERSION = "ariadne.governance_live_pause_transition_intent.v1"
PAUSE_TERMINAL_REASON = "explicit_user_pause"
PREPARED_VERSION = "ariadne.governance_live_tick_prepared_generation.v1"
GENERATION_VERSION = "ariadne.governance_live_tick_generation.v1"
TRANSACTION_VERSION = "ariadne.governance_live_tick_transaction.v1"
G4_ORIENTATION_INTENT_VERSION = "ariadne.g4_emr4_compass_orientation_intent.v1"
GOAL_UPDATE_INTENT_VERSION = "ariadne.governance_goal_only_intent.v1"
G4_ORIENTATION_EVENT = "g4_reorientation"
G4_ORIENTATION_OPERATION = "g4-emr4-compass-reconnection"
G4_ORIENTATION_NODE = "g4-emr4-recovery-orientation"
G4_ORIENTATION_HEAD = "6bdf6a2fcd69dc937f1844c59a4296d0c1b8bde9"
G4_ORIENTATION_TREE = "68a0bb411e430ed0571b6f39b00d99b7010823d7"
G4_STATE_SHA256 = "f32ea528d9efab7e45df9d4ce4770dc9094483641d332ebee052ec436634388b"
G4_GATES_SHA256 = "16206eaa4ee6af4785d9c2bff9e68c9e277da88eda714fc85b5227394d03228d"
G4_ORIENTATION_ACCEPTANCE = (
    "orchestration/agent_inbox/codex/g4-emr4-compass-reconnection-acceptance.md"
)
G4_OLD_CANONICAL_SHA256S = {
    "continuity": "3afcbe15dcdc92d47f6ecf20e2dbe941e74fe57938c73be6bf52c13239889275",
    "compass": "a524fee81c1d7f2aed2a1d81fbb857e6396b4a3c93a02f6091a54e023f9f8584",
    "compass_markdown": "d1d1c2318be7eb3adc58277a700955b231727fed6b3bf3013b4b50ed1b2b8671",
    "active_latch": "69ab7808aac16ba84b6c385b3378483e17fb7b665f84a3d60d1e3054bdba0366",
    "error_register": "be85e1a14b5c1947dd548320edc7923462c0791ba96c9c54e6cb79ba4aca6165",
    "pattern_report": "6fcd53a0a99a03222c7cdeeff607355b6f0cf382b0b47d306f56b14cd14fb7fc",
    "current_baton": "9426913facc3809dee4230820695c3ab067e1adafa3931ca09fb27e890e047ba",
}
G4_ACTUAL_CANONICAL_SHA256S = {
    **G4_OLD_CANONICAL_SHA256S,
    "active_latch": "f1bc5b3545293834365b7992882ebc09e6c83ccd63687c28fd443ac049e2e437",
    "current_baton": "f2c078d3877ac8a7659a614a049021df6d211d7a61934be927268f56b4b36a62",
}
G4_OLD_METADATA_SHA256S = {
    "command-manifest.json": "305d31d03e34deee606abee94a436ffd30ca2b4d8a7817ec71b61908ec29c1ec",
    "transaction.json": "28023f3c35a2e3a141adc7a8fd74dd3221a7a1d3126010ca81cec771b7ef1df6",
    "ownership.json": "e78320a1b0d2f61041cd9d8cac1ed4f98d2bbdf7c3b94891a48d123589d8dee9",
}
G4_OLD_GENERATION_SHA256 = "57d4208fdcc92c28f3abf15610af76daf0aae71f5e95b8a96f7f420c6cdb261b"
G4_OLD_POINTER_SHA256 = "30bbd710351c5e72391f339e83e4bff95c6000ae231ecd8ebd4032d080a30ab5"
G4_OLD_GENERATION_ID = "gen-1f0a9311721de5c258d2cefc8c1f73ab753c94eacd06513aa87bc50f043c1206"
POINTER_NAME = "current.json"
GENERATION_NAME = "generation-manifest.json"
PREDECESSOR_METADATA_NAMES = (*METADATA_NAMES, GENERATION_NAME)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
G4_ABSENT_LOCAL_REFS = (
    "refs/heads/master",
    "refs/heads/handoff/current",
    "refs/remotes/origin/master",
    "refs/remotes/origin/handoff/current",
)
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
CURRENT_NODE_HUMAN_EVIDENCE_CATEGORIES = ("plans", "closeouts", "acceptances")
BRISBANE_TIMESTAMP_SUFFIX = " (Australia/Brisbane)"

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
    "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting",
    "no_production_runtime_deployment_release_or_pages",
    "no_protected_evidence_access_or_protected_ref_movement",
    "docs_branding_and_all_unrelated_untracked_files_preserved",
    "explicit_path_staging_only",
}

LEGACY_FULL_DATA_DENIAL_BOUNDARY = (
    "no_product_patient_appointment_clinical_historical_or_protected_data"
)
TYPED_PRODUCT_DATA_DENIAL_BOUNDARY = (
    "no_product_patient_appointment_clinical_or_protected_data"
)
TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY = "no_historical_data_access"
HISTORICAL_DIARY_ACCESS_BOUNDARY = (
    "allow_local_only_historical_diary_snapshot_measured_privacy_probe"
)
HISTORICAL_DIARY_SUBGATE_BOUNDARIES = frozenset(
    {
        HISTORICAL_DIARY_ACCESS_BOUNDARY,
        "historical_diary_privacy_subgate_contract_sha256_"
        "e312d58d7743b9b4d79d8a947b765732eea142f47586e0bd1f4e738047802615",
        "historical_diary_access_one_leaf_root_one_dense_day_nonrecursive_"
        "maximum_80_files",
        "historical_diary_access_maximum_134217728_total_bytes_and_"
        "8388608_per_file",
        "historical_diary_access_read_only_no_symlink_or_reparse_traversal",
        "historical_diary_access_new_ignored_output_root_ephemeral_in_memory_"
        "key_and_failure_cleanup",
        "historical_diary_access_no_network_provider_model_prompt_telemetry_"
        "clipboard_or_external_release",
        "historical_diary_access_no_raw_text_identity_filename_timestamp_key_"
        "or_mapping_commit",
        "historical_diary_access_strongest_result_locally_restricted_candidate_"
        "without_downstream_authority",
        "historical_diary_access_no_fixture_memory_rag_product_runtime_route_"
        "api_client_database_or_configuration",
    }
)
HISTORICAL_FIRST_USE_MATERIALISATION_ACCESS_BOUNDARY = (
    "allow_local_only_historical_derived_first_use_materialisation_after_"
    "exact_candidate_gate"
)
HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES = frozenset(
    {
        HISTORICAL_FIRST_USE_MATERIALISATION_ACCESS_BOUNDARY,
        "historical_first_use_materialisation_subgate_contract_sha256_"
        "93b6a177b73176518dcd94e31e9dfba90c26dca9a4c4a1851e2e858dc7393a1e",
        "historical_first_use_candidate_gate_source_"
        "abcd4206a363b0c565c070e0f2cb9c54d627b3b3",
        "historical_first_use_exact_digest_bound_gate_receipt_required_"
        "before_write",
        "historical_first_use_maximum_one_minimised_structural_scenario_"
        "fixture",
        "historical_first_use_non_admission_or_revision_writes_nothing",
        "historical_first_use_written_bytes_must_match_admitted_candidate_"
        "digest",
        "historical_first_use_authority_non_transitive",
    }
)
HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_ACCESS_BOUNDARY = (
    "allow_local_only_historical_derived_minimised_scenario_exact_digest_"
    "bound_test_consumption"
)
HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES = frozenset(
    {
        HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_ACCESS_BOUNDARY,
        "historical_derived_minimised_scenario_consumption_subgate_contract_"
        "sha256_da2507056f37482016125c3ccad909573c0495d86cdc135cd5b13714bc7c93ac",
        "historical_derived_minimised_scenario_consumption_first_use_source_"
        "4740813d53ebbc4872fe8c0c08ce2578b1982770",
        "historical_derived_minimised_scenario_consumption_fixture_sha256_"
        "2205ab83cec7c5639d39cc563cee80eec825ac33f17571151571d325e74f2dfe",
        "historical_derived_minimised_scenario_consumption_maximum_one_ignored_"
        "local_fixture_read",
        "historical_derived_minimised_scenario_consumption_no_historical_"
        "archive_read",
        "historical_derived_minimised_scenario_consumption_local_provider_free_"
        "authored_synthetic_test_context_only",
        "historical_derived_minimised_scenario_consumption_no_provider_product_"
        "database_route_client_runtime_configuration_or_ordinary_practice",
        "historical_derived_minimised_scenario_consumption_authority_non_"
        "transitive",
    }
)
HISTORICAL_DATA_BOUNDARY_VOCABULARY = frozenset(
    {
        LEGACY_FULL_DATA_DENIAL_BOUNDARY,
        TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY,
        *HISTORICAL_DIARY_SUBGATE_BOUNDARIES,
        *HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES,
        *HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES,
    }
)

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


def _optional_strings(value: object, rule: str, *, maximum: int = 500) -> list[str]:
    if not isinstance(value, list):
        _reject(rule)
    result = [_text(item, rule, maximum) for item in value]
    if len(result) != len(set(result)):
        _reject(rule)
    return result


def validate_next_operation_protected_boundaries(
    value: object, *, rule: str = "tick_next_boundaries"
) -> list[str]:
    """Admit one closed historical-data mode alongside the stable safety floor."""

    boundaries = _strings(value, rule)
    boundary_set = set(boundaries)
    if not REQUIRED_NEXT_BOUNDARIES.issubset(boundary_set):
        _reject(rule + "_floor")

    unknown_allowances = {
        item
        for item in boundary_set
        if item.startswith("allow_")
        and item
        not in {
            HISTORICAL_DIARY_ACCESS_BOUNDARY,
            HISTORICAL_FIRST_USE_MATERIALISATION_ACCESS_BOUNDARY,
            HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_ACCESS_BOUNDARY,
        }
    }
    if unknown_allowances:
        _reject(rule + "_access_vocabulary")

    historical_boundaries = {
        item for item in boundary_set if "historical" in item
    }
    if not historical_boundaries.issubset(HISTORICAL_DATA_BOUNDARY_VOCABULARY):
        _reject(rule + "_historical_vocabulary")

    if LEGACY_FULL_DATA_DENIAL_BOUNDARY in historical_boundaries:
        if historical_boundaries != {LEGACY_FULL_DATA_DENIAL_BOUNDARY}:
            _reject(rule + "_historical_mode_conflict")
        return boundaries

    if TYPED_PRODUCT_DATA_DENIAL_BOUNDARY not in boundary_set:
        _reject(rule + "_product_data_floor")

    if TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY in historical_boundaries:
        if historical_boundaries != {TYPED_HISTORICAL_DATA_DENIAL_BOUNDARY}:
            _reject(rule + "_historical_mode_conflict")
        return boundaries

    allowance_modes = (
        HISTORICAL_DIARY_SUBGATE_BOUNDARIES,
        HISTORICAL_FIRST_USE_MATERIALISATION_SUBGATE_BOUNDARIES,
        HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES,
    )
    touched_modes = [
        mode for mode in allowance_modes if historical_boundaries & mode
    ]
    if len(touched_modes) > 1:
        _reject(rule + "_historical_mode_conflict")
    if any(historical_boundaries == mode for mode in allowance_modes):
        return boundaries
    if touched_modes:
        _reject(rule + "_historical_subgate_incomplete")
    _reject(rule + "_historical_mode_missing")


def _semantic_exact(value: object, keys: set[str], rule: str) -> dict[str, Any]:
    try:
        return _exact(value, keys, rule)
    except AdoptionRejection as error:
        raise ClockworkTickRejection(rule) from error


def semantic_scalar_leaf_count(value: object) -> int:
    """Count caller-authored scalar leaves without treating container keys as input."""

    if isinstance(value, dict):
        return sum(semantic_scalar_leaf_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(semantic_scalar_leaf_count(item) for item in value)
    return 1


def prospective_human_evidence_header_errors(
    text: str, *, evidence_path: str
) -> tuple[str, ...]:
    """Return every Brisbane Date/Timestamp header defect in stable order."""

    prefix = f"{evidence_path}:"
    header = text.splitlines()[:12]
    date_lines = [line for line in header if line.startswith("Date:")]
    timestamp_lines = [line for line in header if line.startswith("Timestamp:")]
    errors: list[str] = []
    declared_date: date | None = None
    instant: datetime | None = None

    if len(date_lines) != 1:
        errors.append(prefix + "date_count")
    else:
        date_text = date_lines[0].removeprefix("Date:").strip()
        try:
            declared_date = date.fromisoformat(date_text)
        except ValueError:
            errors.append(prefix + "date_invalid")

    if len(timestamp_lines) != 1:
        errors.append(prefix + "timestamp_count")
    else:
        timestamp_text = timestamp_lines[0].removeprefix("Timestamp:").strip()
        match = re.fullmatch(r"(.+) \(([^()]*)\)", timestamp_text)
        if match is None:
            errors.append(prefix + "timezone_name")
            iso_text = timestamp_text
        else:
            iso_text, timezone_name = match.groups()
            if timezone_name != "Australia/Brisbane":
                errors.append(prefix + "timezone_name")
        try:
            instant = datetime.fromisoformat(iso_text)
        except ValueError:
            errors.append(prefix + "timestamp_invalid")
        else:
            if instant.tzinfo is None:
                errors.append(prefix + "offset_required")
            elif instant.utcoffset() != timedelta(hours=10):
                errors.append(prefix + "offset_not_brisbane")

    if (
        declared_date is not None
        and instant is not None
        and instant.date() != declared_date
    ):
        errors.append(prefix + "calendar_date_mismatch")
    return tuple(errors)


def prospective_current_node_human_evidence_errors(
    repo_root: Path, node_value: object
) -> tuple[str, ...]:
    """Collect all prospective plan/closeout/acceptance defects before projection."""

    if not isinstance(node_value, dict):
        return ("node:object_required",)
    evidence = node_value.get("evidence")
    if not isinstance(evidence, dict):
        return ("evidence:object_required",)

    errors: list[str] = []
    seen_paths: set[str] = set()
    repository_root = repo_root.resolve()
    for category in CURRENT_NODE_HUMAN_EVIDENCE_CATEGORIES:
        values = evidence.get(category)
        if not isinstance(values, list) or not values:
            errors.append(f"{category}:nonempty_list_required")
            continue
        for index, raw_path in enumerate(values):
            label = f"{category}[{index}]"
            if not isinstance(raw_path, str) or not raw_path:
                errors.append(label + ":path_string_required")
                continue
            if raw_path in seen_paths:
                errors.append(label + ":duplicate_path")
            else:
                seen_paths.add(raw_path)
            if not raw_path.endswith(".md"):
                errors.append(label + ":markdown_path_required")
            relative = Path(raw_path)
            if (
                "\\" in raw_path
                or relative.is_absolute()
                or ".." in relative.parts
                or raw_path.startswith("docs/branding/")
            ):
                errors.append(label + ":unsafe_path")
                continue
            resolved = (repo_root / relative).resolve()
            if not resolved.is_relative_to(repository_root):
                errors.append(label + ":unsafe_path")
                continue
            if not raw_path.endswith(".md"):
                continue
            if not resolved.is_file():
                errors.append(label + ":file_missing")
                continue
            try:
                text = resolved.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(label + ":file_unreadable")
                continue
            errors.extend(
                prospective_human_evidence_header_errors(
                    text, evidence_path=raw_path
                )
            )
    return tuple(errors)


def _semantic_recorded_at(value: object) -> tuple[str, datetime]:
    recorded_at = _text(value, "tick_semantic_recorded_at", 64)
    if "T" not in recorded_at or " " in recorded_at:
        _reject("tick_semantic_recorded_at")
    try:
        instant = datetime.fromisoformat(recorded_at)
    except ValueError:
        _reject("tick_semantic_recorded_at")
    if instant.tzinfo is None or instant.utcoffset() != timedelta(hours=10):
        _reject("tick_semantic_recorded_at")
    return recorded_at, instant


def _semantic_path(value: object, rule: str) -> str:
    path = _text(value, rule, 500)
    try:
        _safe_path(path, rule)
    except AdoptionRejection as error:
        raise ClockworkTickRejection(rule) from error
    if "\\" in path or path.startswith("docs/branding/"):
        _reject(rule)
    return path


def _semantic_paths(repo_root: Path, operation_id: str, artifact_slug: str, day: str) -> dict[str, Any]:
    topic = f"orchestration/continuity/{operation_id}"
    inbox = "orchestration/agent_inbox/codex"
    plan = f"docs/{artifact_slug}-plan.md"
    threat = f"docs/security/{artifact_slug}-threat-model-delta.md"
    evidence = f"{topic}/evidence.json"
    report = f"{topic}/report.md"
    efficacy = f"{topic}/efficacy-reading.json"
    closeout = f"docs/{artifact_slug}-closeout.md"
    yuri = f"orchestration/human_inbox/yuri/{day}--{artifact_slug}.md"
    acceptance = f"{inbox}/{artifact_slug}-sol-acceptance.md"
    preplanning = f"{inbox}/{artifact_slug}-preplanning-receipt.json"
    pre_verifier = f"{inbox}/{artifact_slug}-pre-verifier-receipt.json"
    values = {
        "plans": [plan, threat],
        "findings": [evidence, report, efficacy],
        "closeouts": [closeout, yuri],
        "acceptances": [acceptance],
        "receipts": [preplanning, pre_verifier],
        "report": report,
        "efficacy": efficacy,
        "closeout": closeout,
        "acceptance": acceptance,
        "evidence": evidence,
        "plan": plan,
    }
    for path in {
        item
        for value in values.values()
        for item in (value if isinstance(value, list) else [value])
    }:
        _semantic_path(path, "tick_semantic_derived_path")
        if not (repo_root / path).resolve().is_relative_to(repo_root.resolve()):
            _reject("tick_semantic_derived_path")
    return values


def _semantic_command_profile(repo_root: Path, evidence_path: str) -> dict[str, Any]:
    implementation_paths = [
        "orchestration_harness/governance_clockwork_tick.py",
        "scripts/ariadne_governance_clockwork_closeout.py",
        "scripts/ariadne_governance_clockwork_tick.py",
        "tests/test_ariadne_governance_clockwork_tick.py",
    ]
    test_paths = [
        "tests/test_current_baton_consistency.py",
        "tests/test_ariadne_active_operation_latch.py",
        "tests/test_ariadne_governance_clockwork_tick.py",
        "tests/test_ariadne_transactional_closeout.py",
    ]
    manifest = {
        "schema_version": COMMAND_VERSION,
        "commands": [
            {
                "command_id": "semantic-closeout-evidence-json",
                "executable": ".venv/Scripts/python.exe",
                "arguments": ["-m", "json.tool", evidence_path],
                "completion_contract": "final_exit_code_zero_required",
            },
            {
                "command_id": "semantic-closeout-ruff",
                "executable": ".venv/Scripts/python.exe",
                "arguments": ["-m", "ruff", "check", *implementation_paths],
                "completion_contract": "final_exit_code_zero_required",
            },
            {
                "command_id": "semantic-closeout-governance-tests",
                "executable": ".venv/Scripts/python.exe",
                "arguments": [
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    repo_root.resolve().as_posix(),
                    *test_paths,
                ],
                "completion_contract": "final_exit_code_zero_required",
            },
        ],
    }
    return {
        "manifest": _validate_commands(manifest),
        "implementation_paths": implementation_paths,
        "test_paths": test_paths,
    }


def _semantic_decisions(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        _reject("tick_semantic_decisions")
    decisions: list[dict[str, str]] = []
    identifiers: list[str] = []
    for item in value:
        row = _semantic_exact(
            item, {"id", "source", "summary"}, "tick_semantic_decision_keys"
        )
        identifier = _text(row["id"], "tick_semantic_decision_id", 128)
        if IDENTIFIER.fullmatch(identifier) is None:
            _reject("tick_semantic_decision_id")
        identifiers.append(identifier)
        decisions.append(
            {
                "id": identifier,
                "source": _semantic_path(
                    row["source"], "tick_semantic_decision_source"
                ),
                "status": "accepted",
                "summary": _text(
                    row["summary"], "tick_semantic_decision_summary", 1000
                ),
            }
        )
    if len(identifiers) != len(set(identifiers)):
        _reject("tick_semantic_decision_id_duplicate")
    return decisions


def expand_semantic_tick_intent(
    repo_root: Path, value: object, contract_value: object
) -> dict[str, Any]:
    """Compile one compact, typed tooling closeout into the admitted legacy intent."""

    contract = validate_contract(contract_value)
    if semantic_scalar_leaf_count(value) > 100:
        _reject("tick_semantic_scalar_leaf_budget")
    if not isinstance(value, dict):
        _reject("tick_semantic_intent_keys")
    semantic_row = dict(value)
    observations_value = semantic_row.pop("agent_error_observations", None)
    row = _semantic_exact(
        semantic_row,
        {
            "schema_version",
            "profile",
            "artifact_slug",
            "recorded_at",
            "closeout",
            "verification_profile",
            "baton_slot",
            "next_operation_protected_boundaries",
        },
        "tick_semantic_intent_keys",
    )
    row["agent_error_observations"] = observations_value
    if row["schema_version"] != SEMANTIC_TICK_INTENT_VERSION:
        _reject("tick_semantic_intent_version")
    if row["profile"] != SEMANTIC_PROFILE:
        _reject("tick_semantic_profile")
    if row["verification_profile"] != SEMANTIC_VERIFICATION_PROFILE:
        _reject("tick_semantic_verification_profile")
    if row["baton_slot"] != SEMANTIC_BATON_SLOT:
        _reject("tick_semantic_baton_slot")
    if _all_keys(row) & DERIVED_INPUT_KEYS:
        _reject("caller_authored_derived_binding")

    artifact_slug = _text(row["artifact_slug"], "tick_semantic_artifact_slug", 120)
    if IDENTIFIER.fullmatch(artifact_slug) is None:
        _reject("tick_semantic_artifact_slug")
    recorded_at, instant = _semantic_recorded_at(row["recorded_at"])
    closeout = _semantic_exact(
        row["closeout"],
        {
            "operation_id",
            "title",
            "builds_on",
            "authority_notes",
            "decisions",
            "claim_scope",
            "additional_receipts",
            "additional_artifacts",
            "unresolved_gates",
            "journey",
            "current_position",
            "next_operation",
        },
        "tick_semantic_closeout_keys",
    )
    operation_id = _text(
        closeout["operation_id"], "tick_semantic_operation_id", 128
    )
    if IDENTIFIER.fullmatch(operation_id) is None:
        _reject("tick_semantic_operation_id")
    title = _text(closeout["title"], "tick_semantic_title", 300)
    parents = _strings(closeout["builds_on"], "tick_semantic_builds_on", maximum=128)
    if any(IDENTIFIER.fullmatch(parent) is None for parent in parents):
        _reject("tick_semantic_builds_on")
    paths = _semantic_paths(
        repo_root, operation_id, artifact_slug, instant.date().isoformat()
    )
    command_profile = _semantic_command_profile(repo_root, paths["evidence"])
    receipts = [
        *paths["receipts"],
        *[
            _semantic_path(path, "tick_semantic_additional_receipt")
            for path in _optional_strings(
                closeout["additional_receipts"],
                "tick_semantic_additional_receipts",
            )
        ],
    ]
    receipts = list(dict.fromkeys(receipts))
    artifacts = [
        *command_profile["implementation_paths"],
        *[
            _semantic_path(path, "tick_semantic_additional_artifact")
            for path in _optional_strings(
                closeout["additional_artifacts"],
                "tick_semantic_additional_artifacts",
            )
        ],
    ]
    artifacts = list(dict.fromkeys(artifacts))
    journey = _semantic_exact(
        closeout["journey"],
        {"strategic_role", "outcome"},
        "tick_semantic_journey_keys",
    )
    current_position = _semantic_exact(
        closeout["current_position"],
        {
            "strategic_role",
            "why_now",
            "outcome",
            "unlocks",
            "does_not_solve",
            "orientation_statement",
        },
        "tick_semantic_current_position_keys",
    )
    observations: list[dict[str, Any]] = []
    if observations_value is not None:
        observations = _validate_incident_observations(observations_value)
    node_incidents = [
        {
            "incident_id": observation["attempt_key"],
            "source_id": observation["attempt_key"],
            "peers": [],
        }
        for observation in observations
    ]
    baton_paths = [
        paths["report"],
        paths["efficacy"],
    ]
    if observations:
        try:
            register_path = repo_root / contract["canonical_paths"]["error_register"]
            revision = json.loads(register_path.read_text(encoding="utf-8"))[
                "register_revision"
            ] + 1
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ClockworkTickRejection("tick_semantic_register_revision") from error
        baton_paths.append(f"{INCIDENT_REVISION_PREFIX}{revision}.md")
    baton_paths.extend([paths["closeout"], paths["acceptance"]])
    manifest = {
        "schema_version": "ariadne.transactional_closeout_manifest.v1",
        "operation_id": operation_id,
        "title": title,
        "source_anchor": "current_head",
        "recorded_at": recorded_at,
        "node": {
            "id": operation_id,
            "title": title,
            "kind": "tooling",
            "relationships": [
                {"node_id": parent, "relation": "builds_on"} for parent in parents
            ],
            "authority": {
                "authorized_openings": [],
                "notes": _strings(
                    closeout["authority_notes"], "tick_semantic_authority_notes"
                ),
            },
            "decisions": _semantic_decisions(closeout["decisions"]),
            "claim_scope": _strings(
                closeout["claim_scope"], "tick_semantic_claim_scope"
            ),
            "contract_evidence": [],
            "evidence": {
                "plans": paths["plans"],
                "findings": paths["findings"],
                "closeouts": paths["closeouts"],
                "acceptances": paths["acceptances"],
                "receipts": receipts,
                "tests": command_profile["test_paths"],
                "artifacts": artifacts,
            },
            "unresolved_gates": _strings(
                closeout["unresolved_gates"], "tick_semantic_unresolved_gates"
            ),
        },
        "journey": {
            "strategic_role": _text(
                journey["strategic_role"], "tick_semantic_journey_role", 1000
            ),
            "outcome": _text(
                journey["outcome"], "tick_semantic_journey_outcome", 1000
            ),
            "evidence": [paths["plan"], paths["report"]],
        },
        "current_position": {
            "strategic_role": _text(
                current_position["strategic_role"],
                "tick_semantic_current_role",
                1000,
            ),
            "why_now": _text(
                current_position["why_now"], "tick_semantic_why_now", 1000
            ),
            "outcome": _text(
                current_position["outcome"], "tick_semantic_current_outcome", 1000
            ),
            "unlocks": _strings(
                current_position["unlocks"], "tick_semantic_unlocks"
            ),
            "does_not_solve": _strings(
                current_position["does_not_solve"],
                "tick_semantic_does_not_solve",
            ),
            "evidence": [
                paths["evidence"],
                paths["report"],
                paths["closeout"],
                paths["acceptance"],
            ],
            "orientation_statement": _text(
                current_position["orientation_statement"],
                "tick_semantic_orientation",
                1000,
            ),
        },
        "next_operation": closeout["next_operation"],
        "incidents": node_incidents,
        "broker": {"enabled": False, "posture": "provider_free_shadow"},
    }
    legacy: dict[str, Any] = {
        "schema_version": (
            TICK_INCIDENT_INTENT_VERSION if observations else TICK_INTENT_VERSION
        ),
        "transaction_manifest": manifest,
        "command_manifest": command_profile["manifest"],
        "baton_acceptance": {
            "label": SEMANTIC_BATON_LABEL,
            "paths": baton_paths,
        },
        "next_operation_protected_boundaries": row[
            "next_operation_protected_boundaries"
        ],
    }
    if observations:
        legacy["agent_error_observations"] = observations
    return validate_tick_intent(legacy, contract)


def admit_tick_intent(
    repo_root: Path, value: object, contract_value: object
) -> dict[str, Any]:
    if isinstance(value, dict) and value.get("schema_version") == SEMANTIC_TICK_INTENT_VERSION:
        return expand_semantic_tick_intent(repo_root, value, contract_value)
    return validate_tick_intent(value, contract_value)


def materialize_semantic_evidence_headers(
    repo_root: Path,
    value: object,
    contract_value: object,
    *,
    fail_at: str | None = None,
) -> dict[str, Any]:
    """Insert one derived Date/Timestamp pair into every prospective human document."""

    if not isinstance(value, dict) or value.get("schema_version") != SEMANTIC_TICK_INTENT_VERSION:
        _reject("tick_semantic_materialization_intent")
    admitted = expand_semantic_tick_intent(repo_root, value, contract_value)
    recorded_at, instant = _semantic_recorded_at(value["recorded_at"])
    date_line = f"Date: {instant.date().isoformat()}"
    timestamp_line = f"Timestamp: {recorded_at}{BRISBANE_TIMESTAMP_SUFFIX}"
    evidence = admitted["transaction_manifest"]["node"]["evidence"]
    paths = [
        path
        for category in CURRENT_NODE_HUMAN_EVIDENCE_CATEGORIES
        for path in evidence[category]
    ]
    errors: list[str] = []
    original: dict[Path, bytes] = {}
    prepared: dict[Path, bytes] = {}
    unchanged: list[str] = []
    for relative in paths:
        target = repo_root / relative
        if not target.is_file():
            errors.append(f"{relative}:file_missing")
            continue
        try:
            raw = target.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeError):
            errors.append(f"{relative}:file_unreadable")
            continue
        lines = text.splitlines()
        if not lines or not lines[0].startswith("# "):
            errors.append(f"{relative}:h1_required")
            continue
        header = lines[:12]
        date_lines = [line for line in header if line.startswith("Date:")]
        timestamp_lines = [line for line in header if line.startswith("Timestamp:")]
        if date_lines == [date_line] and timestamp_lines == [timestamp_line]:
            unchanged.append(relative)
            continue
        if date_lines or timestamp_lines:
            errors.append(f"{relative}:derived_header_conflict")
            continue
        newline = "\r\n" if b"\r\n" in raw else "\n"
        remainder = lines[1:]
        while remainder and not remainder[0].strip():
            remainder.pop(0)
        rendered = (
            lines[0]
            + newline
            + newline
            + date_line
            + newline
            + newline
            + timestamp_line
            + newline
            + newline
            + newline.join(remainder)
        )
        if text.endswith(("\n", "\r")):
            rendered += newline
        original[target] = raw
        prepared[target] = rendered.encode("utf-8")
    if errors:
        _reject("tick_semantic_evidence_materialization:" + ",".join(errors))

    staged: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for target, content in prepared.items():
            staged[target] = _write_temp(target, content)
        for index, (target, temporary) in enumerate(staged.items(), start=1):
            os.replace(temporary, target)
            replaced.append(target)
            if fail_at == f"after_replace_{index}":
                raise OSError("injected_semantic_materialization_failure")
        for target, content in prepared.items():
            if target.read_bytes() != content:
                raise OSError("semantic_materialization_reread")
    except OSError as error:
        try:
            for target in reversed(replaced):
                os.replace(_write_temp(target, original[target]), target)
        except OSError as rollback_error:
            raise ClockworkTickRejection(
                "tick_semantic_materialization_rollback"
            ) from rollback_error
        raise ClockworkTickRejection("tick_semantic_materialization_write") from error
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)

    return {
        "schema_version": SEMANTIC_MATERIALIZATION_VERSION,
        "status": "passed",
        "operation_id": admitted["transaction_manifest"]["operation_id"],
        "recorded_at": recorded_at,
        "document_count": len(paths),
        "materialized_documents": [
            path for path in paths if (repo_root / path) in prepared
        ],
        "unchanged_documents": unchanged,
        "derived_header_scalar_values": len(paths) * 2,
        "caller_timestamp_values": 1,
    }


def _validate_commands(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        _reject("tick_commands_keys")
    schema_version = value.get("schema_version")
    if schema_version == COMMAND_VERSION:
        row = _exact(value, {"schema_version", "commands"}, "tick_commands_keys")
        database_authority = None
    elif schema_version == GOVERNANCE_COMMAND_VERSION_V2:
        row = _exact(
            value,
            {"schema_version", "database_authority", "commands"},
            "tick_commands_keys",
        )
        try:
            database_authority = validate_database_authority(
                row["database_authority"]
            )
        except ValueError:
            _reject("tick_database_authority")
    else:
        _reject("tick_commands_version")
    if not isinstance(row["commands"], list) or not row["commands"]:
        _reject("tick_commands_version")
    commands: list[dict[str, Any]] = []
    ids: list[str] = []
    phases: list[str] = []
    for value in row["commands"]:
        command_keys = (
            {"command_id", "executable", "arguments", "completion_contract"}
            if schema_version == COMMAND_VERSION
            else {
                "command_id",
                "executable",
                "arguments",
                "completion_contract",
                "verification_phase",
            }
        )
        command = _exact(
            value,
            command_keys,
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
        if database_authority is not None:
            try:
                phase = validate_verification_phase(
                    command["verification_phase"]
                )
                validate_runner_for_authority(
                    [executable, *arguments],
                    database_authority=database_authority,
                )
            except ValueError as error:
                if "pytest_forbidden" in str(error):
                    _reject("tick_database_closed_pytest_runner")
                _reject("tick_verification_phase")
            phases.append(phase)
        ids.append(command_id)
        commands.append(copy.deepcopy(command))
    if len(ids) != len(set(ids)):
        _reject("tick_command_duplicate")
    if database_authority is not None:
        try:
            validate_phase_order(phases)
        except ValueError:
            _reject("tick_verification_phase_order")
        return {
            "schema_version": GOVERNANCE_COMMAND_VERSION_V2,
            "database_authority": database_authority,
            "commands": commands,
        }
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
    boundaries = validate_next_operation_protected_boundaries(
        row["next_operation_protected_boundaries"]
    )
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
    boundaries = validate_next_operation_protected_boundaries(
        row["next_operation_protected_boundaries"],
        rule="user_decision_next_boundaries",
    )
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


def validate_pause_tick_intent(
    value: object, contract_value: object
) -> dict[str, Any]:
    """Validate an explicit user pause without manufacturing a decision fork."""

    validate_contract(contract_value)
    try:
        row = _exact(
            value,
            {
                "schema_version",
                "operation_id",
                "completed_stage",
                "resume_executable_stage",
                "terminal_reason",
                "command_manifest",
            },
            "pause_tick_intent_keys",
        )
    except AdoptionRejection as error:
        raise ClockworkTickRejection("pause_tick_intent_keys") from error
    if row["schema_version"] != PAUSE_INTENT_VERSION:
        _reject("pause_tick_intent_version")
    if _all_keys(row) & DERIVED_INPUT_KEYS:
        _reject("caller_authored_derived_binding")
    operation_id = _text(row["operation_id"], "pause_tick_operation_id", 128)
    if IDENTIFIER.fullmatch(operation_id) is None:
        _reject("pause_tick_operation_id")
    if row["terminal_reason"] != PAUSE_TERMINAL_REASON:
        _reject("pause_tick_terminal_reason")
    return {
        "schema_version": PAUSE_INTENT_VERSION,
        "operation_id": operation_id,
        "completed_stage": _text(
            row["completed_stage"], "pause_tick_completed_stage", 500
        ),
        "resume_executable_stage": _text(
            row["resume_executable_stage"], "pause_tick_resume_stage", 500
        ),
        "terminal_reason": PAUSE_TERMINAL_REASON,
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
    if value.get("schema_version") == PAUSE_INTENT_VERSION:
        return validate_pause_tick_intent(value, contract)
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


def _derive_pause_latch(
    latch: dict[str, Any], intent: dict[str, Any], source: str
) -> dict[str, Any]:
    if (
        latch["status"] != "in_progress"
        or latch["operation_id"] != intent["operation_id"]
    ):
        _reject("pause_tick_active_operation")
    result = copy.deepcopy(latch)
    result["status"] = "paused"
    result["source_head"] = source
    result["checkpoint"]["completed_stage"] = intent["completed_stage"]
    result["checkpoint"]["next_executable_stage"] = intent[
        "resume_executable_stage"
    ]
    result["resume_after_compaction"] = False
    result["user_attention"] = {"required": False, "reason": None}
    result["terminal_response"] = {
        "permitted": True,
        "reason": PAUSE_TERMINAL_REASON,
    }
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


def _render_pause_baton(
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
            _reject("pause_tick_baton_row")
        return text.replace(matches[0], f"| {label} | {value} |", 1)

    next_value = (
        "Paused by Yuri after the accepted current tranche. Do not start "
        f"`{intent['operation_id']}` until Yuri explicitly resumes. On resume, "
        f"continue from `{intent['resume_executable_stage']}`. The active latch is "
        "the exact authority boundary. Protected refs remain closed; preserve "
        "`docs/branding/` and stage explicit paths only."
    )
    relation = (
        "The live repository-governance clockwork last published an explicit user-pause "
        f"transition from exact full Git source `{source}` while Continuity "
        f"{graph['graph_revision']} / Compass {compass['map_revision']} and the last "
        "accepted product result remained unchanged. One clockwork writer owns all ten "
        "surfaces, historical direct writers remain retired, and the immediately previous "
        "generation is full-Git-bound and byte-recoverable. This opens no protected-ref, "
        "deployment, release or Pages authority."
    )
    current = replace_row(current, "Next implementation", next_value)
    return replace_row(current, "Current clockwork relation", relation)


def build_tick_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Derive a complete next generation from the current live reading."""

    contract = validate_contract(contract_value)
    intent = admit_tick_intent(repo_root, intent_value, contract)
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
    prospective_evidence_errors = prospective_current_node_human_evidence_errors(
        repo_root, manifest["node"]
    )
    if prospective_evidence_errors:
        _reject(
            "tick_prospective_current_node_evidence:"
            + ",".join(prospective_evidence_errors)
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


def build_pause_tick_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Derive one pointer-last explicit user-pause transition."""

    contract = validate_contract(contract_value)
    intent = validate_pause_tick_intent(intent_value, contract)
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
    paused_latch = _derive_pause_latch(source_latch, intent, source)
    graph = json.loads(current["continuity"].decode("utf-8"))
    compass = json.loads(current["compass"].decode("utf-8"))
    baton = _render_pause_baton(
        current["current_baton"].decode("utf-8"),
        intent=intent,
        graph=graph,
        compass=compass,
        source=source,
    )
    canonical = dict(current)
    canonical["active_latch"] = _json_text(paused_latch).encode("utf-8")
    canonical["current_baton"] = baton.encode("utf-8")

    intent_sha256 = tc.sha256(intent)
    transaction_id = "txn-" + tc.sha256(
        {"pause_intent": intent_sha256, "head": source}
    )[7:31]
    journal_id = "journal-" + transaction_id[4:]
    events: list[dict[str, Any]] = []
    previous = tc.ZERO_DIGEST
    for event_type, payload in (
        (
            "pause-transition-intent-accepted",
            {
                "intent_sha256": intent_sha256,
                "previous_next_executable_stage": source_latch["checkpoint"][
                    "next_executable_stage"
                ],
            },
        ),
        ("git-source-resolved", {"source_commit": source}),
        (
            "active-operation-paused",
            {
                "operation_id": paused_latch["operation_id"],
                "resume_executable_stage": paused_latch["checkpoint"][
                    "next_executable_stage"
                ],
            },
        ),
        (
            "paused-latch-validated",
            {
                "user_attention_required": False,
                "terminal_response_permitted": True,
                "resume_after_compaction": False,
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
            operation_id=intent["operation_id"],
            sequence=len(events) + 1,
            previous=previous,
            event_type=event_type,
            payload=payload,
        )
        events.append(event)
        previous = event["event_sha256"]
    tc.validate_event_chain(events)

    projection_sha256s = {
        "latch": tc.sha256(paused_latch),
        "current_baton": tc.sha256(baton),
    }
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
        "projection_sha256s": projection_sha256s,
        "journal": events,
        "publication_mode": "lease_bound_pointer_last_live_tick",
        "event_kind": "pause_transition",
        "next_boundaries_sha256": tc.sha256(paused_latch["protected_boundaries"]),
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
    if isinstance(row.get("intent"), dict) and row["intent"].get("schema_version") == GOAL_UPDATE_INTENT_VERSION:
        from orchestration_harness import governance_goal_tick
        return governance_goal_tick.validate_prepared(repo_root, row)
    if isinstance(row.get("intent"), dict) and row["intent"].get("schema_version") == G4_ORIENTATION_INTENT_VERSION:
        return _validate_g4_orientation_prepared(repo_root, row)
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
    elif intent["schema_version"] == PAUSE_INTENT_VERSION:
        source_latch = validate_active_operation(
            json.loads(source_canonical["active_latch"].decode("utf-8"))
        )
        expected_latch = _derive_pause_latch(source_latch, intent, source)
        expected_baton = _render_pause_baton(
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
            or transaction["event_kind"] != "pause_transition"
            or transaction["projection_sha256s"] != expected_projection_sha256s
            or transaction["next_boundaries_sha256"]
            != tc.sha256(expected_latch["protected_boundaries"])
            or not transaction["register_bytes_preserved"]
            or not transaction["pattern_bytes_preserved"]
        ):
            _reject("pause_tick_prepared_semantics")
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


def _validate_g4_selected_live_state(
    repo_root: Path, contract: dict[str, Any], generation: dict[str, Any]
) -> dict[str, Any]:
    """Read the G4-selected surfaces without the legacy updater inventory."""

    head = _assert_g4_git_state(repo_root, contract)
    root = _clockwork_root(repo_root, contract)
    pointer = _exact(_load(root / POINTER_NAME), {
        "schema_version", "phase", "selected_generation_id", "selected_bundle_sha256",
        "previous_generation_id", "previous_source_commit", "lease_sequence", "writer",
    }, "g4_orientation_live_pointer_keys")
    if (
        pointer["schema_version"] != POINTER_VERSION
        or pointer["phase"] != "clockwork_active"
        or pointer["writer"] != WRITER
        or pointer["selected_generation_id"] != generation.get("generation_id")
        or pointer["selected_bundle_sha256"] != generation.get("bundle_sha256")
        or pointer["previous_generation_id"] != G4_OLD_GENERATION_ID
        or pointer["previous_source_commit"] != G4_ORIENTATION_HEAD
        or pointer["lease_sequence"] != 248
        or generation.get("schema_version") != GENERATION_VERSION
        or set(generation) != {
            "schema_version", "generation_id", "bundle_sha256", "source_commit",
            "previous_generation", "canonical_sha256s", "metadata_sha256s",
            "g4_orientation",
        }
        or not isinstance(generation.get("source_commit"), str)
        or HEX40.fullmatch(generation["source_commit"]) is None
        or not isinstance(generation.get("bundle_sha256"), str)
        or HEX64.fullmatch(generation["bundle_sha256"]) is None
        or generation.get("generation_id") != "gen-" + generation["bundle_sha256"]
    ):
        _reject("g4_orientation_live_pointer")
    try:
        _git(repo_root, "merge-base", "--is-ancestor", generation["source_commit"], head)
    except AdoptionRejection:
        _reject("g4_orientation_live_source_not_ancestor")
    canonical = {
        key: (repo_root / relative).read_bytes()
        for key, relative in contract["canonical_paths"].items()
    }
    metadata = {name: (root / name).read_bytes() for name in METADATA_NAMES}
    canonical_sha256s = {key: _hash_bytes(raw) for key, raw in canonical.items()}
    metadata_sha256s = {name: _hash_bytes(raw) for name, raw in metadata.items()}
    if (
        canonical_sha256s != generation.get("canonical_sha256s")
        or metadata_sha256s != generation.get("metadata_sha256s")
        or metadata_sha256s.get("ownership.json")
        != G4_OLD_METADATA_SHA256S["ownership.json"]
        or generation.get("bundle_sha256") != _hash_json({
            "canonical": canonical_sha256s, "metadata": metadata_sha256s,
        })
    ):
        _reject("g4_orientation_live_physical_images")
    ownership = json.loads(metadata["ownership.json"].decode("utf-8"))
    if (
        ownership.get("schema_version") != OWNERSHIP_VERSION
        or ownership.get("phase") != "clockwork_active"
        or not isinstance(ownership.get("surface_owners"), dict)
        or set(ownership["surface_owners"]) != set(CANONICAL_KEYS) | {
            "command_manifest", "transaction", "ownership",
        }
        or set(ownership["surface_owners"].values()) != {WRITER}
        or not isinstance(ownership.get("legacy_writers"), dict)
        or set(ownership["legacy_writers"]) != {
            "bespoke_continuity_updater", "manual_baton_editor",
            "manual_latch_editor", "manual_register_fixture_editor",
        }
        or set(ownership["legacy_writers"].values()) != {"retired"}
    ):
        _reject("g4_orientation_live_ownership")
    return {
        "schema_version": "ariadne.governance_live_state.v1",
        "status": "passed", "head": head,
        "source_commit": generation["source_commit"],
        "generation_id": generation["generation_id"],
        "bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": pointer["previous_generation_id"],
        "previous_source_commit": pointer["previous_source_commit"],
        "clockwork_owned_surfaces": len(ownership["surface_owners"]),
        "dual_owned_surfaces": 0,
        "retired_legacy_writer_classes": len(ownership["legacy_writers"]),
        "canonical_drift": 0, "lease_sequence": pointer["lease_sequence"],
    }


def validate_tick_live_state(
    repo_root: Path, contract_value: object
) -> dict[str, Any]:
    contract = validate_contract(contract_value)
    root = _clockwork_root(repo_root, contract)
    generation = _load(root / GENERATION_NAME)
    if generation.get("goal_update") is not None:
        from orchestration_harness import governance_goal_tick
        return governance_goal_tick.validate_live(repo_root, contract, generation)
    if generation.get("g4_orientation") is not None:
        base = _validate_g4_selected_live_state(repo_root, contract, generation)
        return _validate_g4_orientation_live(repo_root, contract, base, generation)
    base = validate_live_state(repo_root, contract)
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
    elif event_kind == "pause_transition":
        if (
            transaction.get("operation_id") != latch["operation_id"]
            or latch["status"] != "paused"
            or latch["source_head"] != transaction.get("source_commit")
            or latch["resume_after_compaction"]
            or latch["user_attention"]["required"]
            or not latch["terminal_response"]["permitted"]
            or latch["terminal_response"]["reason"] != PAUSE_TERMINAL_REASON
            or transaction.get("projection_sha256s")
            != {
                "latch": tc.sha256(latch),
                "current_baton": tc.sha256(
                    (repo_root / contract["canonical_paths"]["current_baton"])
                    .read_text(encoding="utf-8")
                ),
            }
        ):
            _reject("tick_live_pause_operation")
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
    elif event_kind == "pause_transition":
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
            or any(
                (repo_root / contract["canonical_paths"][key]).read_bytes()
                != source_canonical[key]
                for key in preserved
            )
        ):
            _reject("tick_live_pause_preservation")
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


def _g4_effect_images(
    repo_root: Path, contract: dict[str, Any], canonical: dict[str, bytes],
    metadata: dict[str, bytes], pointer: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str]]:
    root = _clockwork_root(repo_root, contract)
    after_bytes = {
        **{relative: canonical[key] for key, relative in contract["canonical_paths"].items()},
        **{f"{contract['clockwork_root']}/{name}": raw
           for name, raw in metadata.items()},
        f"{contract['clockwork_root']}/{POINTER_NAME}":
            _json_text(pointer).encode("utf-8"),
    }
    if len(after_bytes) != 12:
        _reject("g4_orientation_effect_surface_set")
    before = {relative: _hash_bytes((repo_root / relative).read_bytes())
              for relative in after_bytes}
    after = {relative: _hash_bytes(raw) for relative, raw in after_bytes.items()}
    return before, after


def _verify_g4_effect_manifest_images(
    repo_root: Path, prepared: dict[str, Any], manifest: dict[str, Any]
) -> None:
    contract = prepared["contract"]
    metadata = {
        **prepared["metadata"],
        GENERATION_NAME: _json_text(prepared["generation_manifest"]).encode("utf-8"),
    }
    before, after = _g4_effect_images(repo_root, contract, prepared["canonical"],
        metadata, prepared["pointer"])
    intent_path = repo_root / (
        "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json"
    )
    if (
        manifest.get("before_sha256") != before
        or manifest.get("after_sha256") != after
        or manifest.get("lease_before") != 247
        or manifest.get("lease_after") != 248
        or manifest.get("mode") != "reorient"
        or manifest.get("stage") != "reconcile"
        or manifest.get("operation_id") != G4_ORIENTATION_OPERATION
        or manifest.get("source_commit") != prepared["source_commit"]
        or manifest.get("source_tree") != _git(repo_root, "rev-parse", "HEAD^{tree}")
        or manifest.get("intent_sha256") != _hash_bytes(intent_path.read_bytes())
    ):
        _reject("g4_orientation_effect_manifest_images")


def _verify_g4_rollback_manifest_images(
    repo_root: Path, recovery_prepared: dict[str, Any], manifest: dict[str, Any]
) -> None:
    before, after = _g4_effect_images(
        repo_root, recovery_prepared["contract"], recovery_prepared["canonical"],
        recovery_prepared["metadata"], recovery_prepared["pointer"],
    )
    intent_path = repo_root / (
        "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json"
    )
    if (
        manifest.get("before_sha256") != before
        or manifest.get("after_sha256") != after
        or manifest.get("lease_before") != 248
        or manifest.get("lease_after") != 249
        or manifest.get("mode") != "rollback"
        or manifest.get("stage") != "reconcile"
        or manifest.get("operation_id") != G4_ORIENTATION_OPERATION
        or manifest.get("source_commit") != _git(repo_root, "rev-parse", "HEAD")
        or manifest.get("source_tree") != _git(repo_root, "rev-parse", "HEAD^{tree}")
        or manifest.get("intent_sha256") != _hash_bytes(intent_path.read_bytes())
    ):
        _reject("g4_orientation_rollback_manifest_images")


def _verify_g4_committed_images(
    repo_root: Path, contract: dict[str, Any], manifest: dict[str, Any]
) -> None:
    expected_paths = {
        *contract["canonical_paths"].values(),
        *(f"{contract['clockwork_root']}/{name}"
          for name in PREDECESSOR_METADATA_NAMES),
        f"{contract['clockwork_root']}/{POINTER_NAME}",
    }
    expected = manifest.get("after_sha256")
    if (
        not isinstance(expected, dict)
        or set(expected) != expected_paths
        or len(expected_paths) != 12
        or {relative: _hash_bytes((repo_root / relative).read_bytes())
            for relative in expected_paths} != expected
    ):
        _reject("g4_orientation_committed_image_readback")


def publish_tick_generation(
    repo_root: Path,
    prepared_value: object,
    *,
    writer_id: str,
    fail_at: str | None = None,
    g4_effect_checker: Any = None,
    g4_effect_context: Any = None,
    g4_effect_manifest: dict[str, Any] | None = None,
    goal_effect_checker: Any = None,
    goal_effect_context: Any = None,
    goal_effect_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Publish one prepared tick, committing only when the pointer is replaced."""

    is_goal = (isinstance(prepared_value, dict)
        and isinstance(prepared_value.get("intent"), dict)
        and prepared_value["intent"].get("schema_version") == GOAL_UPDATE_INTENT_VERSION)
    if is_goal:
        from orchestration_harness import governance_goal_tick
        selected_contract = validate_contract(prepared_value["contract"])
        selected = _load(_clockwork_root(repo_root, selected_contract) / POINTER_NAME)
        if selected.get("selected_generation_id") == prepared_value.get("pointer", {}).get("selected_generation_id"):
            return governance_goal_tick.idempotent_readback(repo_root, prepared_value, writer_id)
    prepared = validate_prepared_tick(repo_root, prepared_value)
    contract = prepared["contract"]
    if writer_id != WRITER:
        _reject("tick_writer_not_clockwork")
    is_g4 = prepared["intent"]["schema_version"] == G4_ORIENTATION_INTENT_VERSION
    is_scoped = is_g4 or is_goal
    if is_goal:
        effect_checker, effect_context, effect_manifest = goal_effect_checker, goal_effect_context, goal_effect_manifest
        verify_effect = governance_goal_tick.verify_effect
    else:
        effect_checker, effect_context, effect_manifest = g4_effect_checker, g4_effect_context, g4_effect_manifest
        verify_effect = _verify_g4_effect_manifest_images
    if is_scoped:
        _assert_g4_git_state(repo_root, contract, prepared["source_commit"])
    else:
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
    if is_scoped:
        if not callable(effect_checker) or effect_context is None or effect_manifest is None:
            _reject("goal_update_effect_admission_required" if is_goal else "g4_orientation_effect_admission_required")
        verify_effect(repo_root, prepared, effect_manifest)
        decision = effect_checker(
            context=effect_context, manifest=effect_manifest,
            prepared=prepared, phase="effect"
        )
        if ((is_goal and getattr(decision, "execution_authorized", False) is not True)
                or (not is_goal and not getattr(decision, "execution_authorized", False))):
            _reject("goal_update_effect_not_authorized" if is_goal else "g4_orientation_effect_not_authorized")
    if prepared["intent"]["schema_version"] == G4_ORIENTATION_INTENT_VERSION:
        _g4_orientation_baseline(repo_root, contract, prepared["intent"])
    elif is_goal:
        governance_goal_tick.baseline(repo_root, contract, prepared["source_commit"])
    else:
        _assert_clean_predecessor(repo_root, contract, prepared["source_commit"])
    lease_path = root / "writer.lock"
    canonical_targets = {
        key: repo_root / relative for key, relative in contract["canonical_paths"].items()
    }
    metadata_values = {
        **prepared["metadata"],
        GENERATION_NAME: _json_text(prepared["generation_manifest"]).encode("utf-8"),
    }
    metadata_targets = {name: root / name for name in metadata_values}
    staged: dict[str, Path] = {}
    acquired = False
    snapshots_complete = False
    committed = False
    try:
        _write_lease(
            lease_path,
            operation_id=_intent_operation_id(prepared["intent"]),
            source=prepared["source_commit"],
            pointer=prepared["pointer"],
        )
        acquired = True
        if is_scoped:
            _assert_g4_git_state(repo_root, contract, prepared["source_commit"])
            verify_effect(repo_root, prepared, effect_manifest)
            decision = effect_checker(
                context=effect_context, manifest=effect_manifest,
                prepared=prepared, phase="effect"
            )
            if ((is_goal and getattr(decision, "execution_authorized", False) is not True)
                    or (not is_goal and not getattr(decision, "execution_authorized", False))):
                _reject("goal_update_effect_not_authorized" if is_goal else "g4_orientation_effect_not_authorized")
        original_canonical = {key: path.read_bytes() for key, path in canonical_targets.items()}
        original_metadata = {name: path.read_bytes() for name, path in metadata_targets.items()}
        original_pointer = pointer_path.read_bytes()
        snapshots_complete = True
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
        if is_scoped:
            _verify_g4_committed_images(repo_root, contract, effect_manifest)
        if fail_at == "after_pointer_replace":
            raise CommittedClockworkTick("injected_tick_postcommit_failure")
        return state
    except BaseException:
        if not committed and snapshots_complete:
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
        if acquired:
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
    if _load(root / GENERATION_NAME).get("g4_orientation") is not None:
        _reject("g4_orientation_explicit_rollback_required")
    if _load(root / GENERATION_NAME).get("goal_update") is not None:
        _reject("goal_update_separate_bound_inverse_required")
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


def validate_g4_orientation_intent(value: object) -> dict[str, Any]:
    """Admit only the named, observed two-drift G4 recovery baseline."""

    row = _exact(value, {
        "schema_version", "operation_id", "observed_baseline_commit", "observed_baseline_tree",
        "programme_state_sha256", "programme_gates_sha256",
        "previous_generation_id", "previous_bundle_sha256", "lease_sequence",
        "old_canonical_sha256s", "actual_canonical_sha256s",
        "metadata_sha256s", "generation_manifest_sha256", "pointer_sha256",
        "orientation_date", "acceptance_path",
    }, "g4_orientation_intent_keys")
    if (
        row["schema_version"] != G4_ORIENTATION_INTENT_VERSION
        or row["operation_id"] != G4_ORIENTATION_OPERATION
        or row["observed_baseline_commit"] != G4_ORIENTATION_HEAD
        or row["observed_baseline_tree"] != G4_ORIENTATION_TREE
        or row["programme_state_sha256"] != G4_STATE_SHA256
        or row["programme_gates_sha256"] != G4_GATES_SHA256
        or row["previous_generation_id"] != G4_OLD_GENERATION_ID
        or row["previous_bundle_sha256"] != G4_OLD_GENERATION_ID[4:]
        or row["lease_sequence"] != 247
        or row["old_canonical_sha256s"] != G4_OLD_CANONICAL_SHA256S
        or row["actual_canonical_sha256s"] != G4_ACTUAL_CANONICAL_SHA256S
        or row["metadata_sha256s"] != G4_OLD_METADATA_SHA256S
        or row["generation_manifest_sha256"] != G4_OLD_GENERATION_SHA256
        or row["pointer_sha256"] != G4_OLD_POINTER_SHA256
        or row["acceptance_path"] != G4_ORIENTATION_ACCEPTANCE
        or row["orientation_date"] != "2026-10-25"
    ):
        _reject("g4_orientation_intent_pin")
    return row


def _assert_g4_git_state(
    repo_root: Path, contract: dict[str, Any], expected_source: str | None = None
) -> str:
    """Check the reviewed isolated checkout topology without changing generic policy."""

    source = _git(repo_root, "rev-parse", "HEAD")
    tree = _git(repo_root, "rev-parse", "HEAD^{tree}")
    if (
        HEX40.fullmatch(source) is None
        or HEX40.fullmatch(tree) is None
        or (expected_source is not None and source != expected_source)
    ):
        _reject("g4_orientation_source_head_tree")
    for ref in G4_ABSENT_LOCAL_REFS:
        observed = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", ref],
            cwd=repo_root, capture_output=True, check=False,
        )
        if observed.returncode != 1:
            _reject("g4_orientation_local_protected_ref_topology:" + ref)
    _git(repo_root, "merge-base", "--is-ancestor", contract["required_ancestor"], source)
    _git(repo_root, "merge-base", "--is-ancestor", contract["accepted_rehearsal_source"], source)
    _git(repo_root, "merge-base", "--is-ancestor", G4_ORIENTATION_HEAD, source)
    return source


def _g4_orientation_baseline(
    repo_root: Path, contract: dict[str, Any], intent: dict[str, Any]
) -> tuple[dict[str, bytes], dict[str, bytes], dict[str, Any]]:
    """Require every current preimage, including the two declared divergences."""

    executing_head = _assert_g4_git_state(repo_root, contract)
    if _git(repo_root, "rev-parse", G4_ORIENTATION_HEAD + "^{tree}") != G4_ORIENTATION_TREE:
        _reject("g4_orientation_source_tree")
    for relative, expected in (
        ("orchestration/programme/current-state.json", G4_STATE_SHA256),
        ("orchestration/programme/gates.yaml", G4_GATES_SHA256),
    ):
        if _hash_bytes((repo_root / relative).read_bytes()) != expected:
            _reject("g4_orientation_programme_pin")
    source = _source_bytes(repo_root, contract, G4_ORIENTATION_HEAD)
    if {key: _hash_bytes(raw) for key, raw in source.items()} != G4_ACTUAL_CANONICAL_SHA256S:
        _reject("g4_orientation_source_canonical")
    current = {
        key: (repo_root / relative).read_bytes()
        for key, relative in contract["canonical_paths"].items()
    }
    if current != source:
        _reject("g4_orientation_physical_canonical")
    root = _clockwork_root(repo_root, contract)
    metadata = {name: (root / name).read_bytes() for name in PREDECESSOR_METADATA_NAMES}
    if {name: _hash_bytes(metadata[name]) for name in METADATA_NAMES} != G4_OLD_METADATA_SHA256S:
        _reject("g4_orientation_metadata_third_drift")
    if _hash_bytes(metadata[GENERATION_NAME]) != G4_OLD_GENERATION_SHA256:
        _reject("g4_orientation_generation_drift")
    pointer_raw = (root / POINTER_NAME).read_bytes()
    if _hash_bytes(pointer_raw) != G4_OLD_POINTER_SHA256:
        _reject("g4_orientation_pointer_drift")
    generation = json.loads(metadata[GENERATION_NAME].decode("utf-8"))
    pointer = json.loads(pointer_raw.decode("utf-8"))
    source_pointer = _source_pointer(repo_root, contract, G4_ORIENTATION_HEAD)
    if (
        generation.get("canonical_sha256s") != G4_OLD_CANONICAL_SHA256S
        or generation.get("metadata_sha256s") != G4_OLD_METADATA_SHA256S
        or generation.get("generation_id") != G4_OLD_GENERATION_ID
        or pointer != source_pointer
        or pointer.get("selected_generation_id") != G4_OLD_GENERATION_ID
        or pointer.get("selected_bundle_sha256") != G4_OLD_GENERATION_ID[4:]
        or pointer.get("lease_sequence") != 247
        or pointer.get("phase") != "clockwork_active"
        or pointer.get("writer") != WRITER
    ):
        _reject("g4_orientation_predecessor_identity")
    latch = validate_active_operation(json.loads(current["active_latch"].decode("utf-8")))
    if latch.get("operation_id") != "g1b2-pure-journal-replay-kernel" or latch.get("status") != "in_progress":
        _reject("g4_orientation_latch_identity")
    return current, metadata, pointer


def _g4_orientation_projections(
    repo_root: Path, current: dict[str, bytes], intent: dict[str, Any],
    *, source_head: str,
) -> dict[str, bytes]:
    if not isinstance(source_head, str) or HEX40.fullmatch(source_head) is None:
        _reject("g4_orientation_projection_source_head")
    graph = json.loads(current["continuity"].decode("utf-8"))
    compass = json.loads(current["compass"].decode("utf-8"))
    old_position = compass["current_position"]["node_id"]
    parent = "ariadne-provider-free-clockwork-live-canonical-adoption-retirement"
    if (
        old_position != "raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review"
        or not any(node.get("id") == parent and node.get("status") == "accepted"
                   and node.get("kind") == "foundation" for node in graph["nodes"])
        or not any(step.get("node_id") == parent for step in compass["journey"])
        or graph.get("graph_revision") != 462
        or compass.get("map_revision") != 444
        or any(node.get("id") == G4_ORIENTATION_NODE for node in graph["nodes"])
    ):
        _reject("g4_orientation_graph_baseline")
    stamp = intent["orientation_date"]
    acceptance = intent["acceptance_path"]
    graph = copy.deepcopy(graph)
    compass = copy.deepcopy(compass)
    graph["nodes"].append({
        "id": G4_ORIENTATION_NODE,
        "title": "G4 EMR4 recovery and Compass reorientation",
        "kind": "tooling",
        "relationships": [{"node_id": parent, "relation": "builds_on"}],
        "authority": {"authorized_openings": [], "notes": [
            "Owner redirected accepted governance work to current G4 Stage 1 recovery.",
            "The prior waiting-area node is retained as navigation history, not a product ancestor.",
            "This orientation is not M1 product acceptance or a G1B2 closeout."
        ]},
        "decisions": [{"id": "record-current-g4-recovery-orientation", "source":
            "docs/ariadne-g4-compass-reconnection.md", "status": "accepted",
            "summary": "Reflect qualified G2/G3 acceptance and partial G4 M1 without changing product authority."}],
        "claim_scope": ["Accepted governance orientation only; product M1 remains partial."],
        "contract_evidence": [],
        "evidence": {
            "plans": ["docs/ariadne-g4-compass-reconnection.md"],
            "acceptances": [acceptance], "receipts": [],
            "tests": ["tests/test_ariadne_g4_orientation.py"],
            "closeouts": [], "findings": [
                "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json"
            ],
        },
        "unresolved_gates": ["G4 M1 remains partial; app, database and browser effects require exact finite bindings."],
        "status": "accepted", "created_at": stamp, "updated_at": stamp,
        "coordinates": {"git_ref": "codex/raisa-ariadne-recovery-g0",
            "source_head": source_head, "thread_id": None,
            "worktree_role": "integration"},
    })
    graph["graph_revision"] += 1
    graph["updated_at"] = stamp
    compass["journey"].append({
        "node_id": G4_ORIENTATION_NODE, "lineage_parent": parent,
        "strategic_role": "Reconnect the accepted governance map to current G4 Stage 1 recovery.",
        "outcome": "G2 and G3 remain accepted with qualifications; G4 M1 remains partial.",
        "evidence": ["docs/ariadne-g4-compass-reconnection.md", acceptance],
    })
    compass["current_position"] = {
        "node_id": G4_ORIENTATION_NODE,
        "strategic_role": "Track the current Stage 1 recovery sequence without granting product acceptance.",
        "why_now": "Owner redirected work from the stale G1B2 waiting-area position.",
        "outcome": "Ariadne records accepted governance direction and the partial G4 M1 state.",
        "unlocks": ["Scoped, separately admitted Stage 1 continuation."],
        "does_not_solve": ["M1 product acceptance, protected integration or runtime authority."],
        "evidence": ["docs/ariadne-g4-compass-reconnection.md", acceptance],
    }
    compass["orientation_statement"] = (
        "Current work is G4 Stage 1 recovery: G2 and G3 are accepted with qualifications; "
        "M1 is partial and remains subject to exact admission and independent acceptance."
    )
    compass["programme"] = {
        "id": "raisa-g4-stage1-recovery", "title": "Raisa G4 Stage 1 recovery",
        "master_plan_phase": "G4 Stage 1",
        "summary": "Restore the accepted local synthetic development path while preserving qualified G2/G3 acceptance and unresolved G4 M1.",
        "evidence": ["docs/programme/raisa-ariadne-recovery-programme.md",
            "docs/ariadne-g4-compass-reconnection.md"],
    }
    deferred_reception_decisions = {
        "reception-one-delete-confirm-physical-design-architecture": (
            "The delete-confirm physical design decision remains useful future work; "
            "the current M1 route first proves request, book and same-appointment move."
        ),
        "reception-one-appointment-cancellation-direction": (
            "The cancellation direction remains useful future work; the current M1 route "
            "first proves request, book and same-appointment move."
        ),
    }
    seen_reception_decisions = set()
    for horizon in compass["decision_horizon"]:
        if horizon["id"] in deferred_reception_decisions:
            if horizon["status"] != "active":
                _reject("g4_orientation_horizon_status:" + horizon["id"])
            seen_reception_decisions.add(horizon["id"])
            horizon["status"] = "deferred"
            compass["map_limits"].append(
                horizon["id"] + ": " + deferred_reception_decisions[horizon["id"]]
            )
    if seen_reception_decisions != set(deferred_reception_decisions):
        _reject("g4_orientation_expected_reception_horizons_missing")
    compass["decision_horizon"].append({
        "id": "g4-stage1-m1-integration",
        "title": "G4 Stage 1 appointment journey and shared channel integration",
        "status": "active",
        "strategic_question": (
            "After Compass recovery and review of known capability dispositions, how do the existing "
            "Bureau compose, context and proofreader seams support request, book and same-appointment "
            "move through calm visible Diary and intent projections, a full Diary prompt, and a shared "
            "text/voice lifecycle with independently checked outcome reliability?"
        ),
        "why_it_matters": (
            "G2 and G3 are accepted with qualifications, but G4 M1 is partial. The current compose "
            "route and same-date move client are narrower than the required contextual appointment "
            "journeys; the remaining integration must retain server-owned decisions and human confirmation."
        ),
        "prerequisites": [
            "Complete the reviewed Compass recovery and use the pinned 18-domain capability dispositions as navigation, not product acceptance.",
            "Integrate the existing Bureau compose/context/proofreader seams for request, book and same-appointment move, including the currently missing date-changing move semantics.",
            "Keep Diary and intent projections visible and calm, with a full Diary prompt and the same domain lifecycle for web text and push-to-talk voice.",
            "Check actual commands and outcomes against independently derived expectations, including reliability and accessible non-AI fallback.",
            "Use exact current G4 admission, finite effect bindings and independent acceptance for each product effect.",
            "Keep real data, providers, deployment and protected integration closed.",
        ],
        "boundary_changes": [],
        "evidence": ["docs/ariadne-g4-compass-reconnection.md"],
    })
    compass["map_limits"].append(
        "All other decision and programme-support horizon statuses are preserved, including the active Raisa Practice Context Fabric. The new G4 sequence is navigation only and grants no product acceptance or runtime authority."
    )
    compass["map_revision"] += 1
    compass["source_graph_revision"] = graph["graph_revision"]
    compass["updated_at"] = stamp
    report = ariadne_compass.build_compass_report(
        compass, graph, repo_root=repo_root, require_evidence_files=False
    )
    if report["status"] != "passed":
        _reject("g4_orientation_compass:" + ",".join(report["reasons"]))
    result = dict(current)
    result["continuity"] = _json_text(graph).encode("utf-8")
    result["compass"] = _json_text(compass).encode("utf-8")
    result["compass_markdown"] = ariadne_compass.render_markdown(report).encode("utf-8")
    return result


def build_g4_orientation_generation(
    repo_root: Path, contract_value: object, intent_value: object
) -> dict[str, Any]:
    """Prepare the single G4 recovery generation without moving the G1B2 latch."""

    contract = validate_contract(contract_value)
    intent = validate_g4_orientation_intent(intent_value)
    current, prior_metadata, base_pointer = _g4_orientation_baseline(repo_root, contract, intent)
    executing_head = _assert_g4_git_state(repo_root, contract)
    canonical = _g4_orientation_projections(
        repo_root, current, intent, source_head=executing_head,
    )
    if any(canonical[key] != current[key] for key in (
        "active_latch", "current_baton", "error_register", "pattern_report"
    )):
        _reject("g4_orientation_preservation")
    intent_sha = tc.sha256(intent)
    transaction_id = "txn-" + tc.sha256({
        "g4_orientation_intent": intent_sha, "head": executing_head
    })[7:31]
    journal_id = "journal-" + transaction_id[4:]
    events: list[dict[str, Any]] = []
    previous = tc.ZERO_DIGEST
    for event_type, payload in (
        ("g4-orientation-intent-accepted", {"intent_sha256": intent_sha}),
        ("observed-two-drift-baseline-bound", {
            "old_canonical_sha256s": G4_OLD_CANONICAL_SHA256S,
            "actual_canonical_sha256s": G4_ACTUAL_CANONICAL_SHA256S,
        }),
        ("g4-orientation-projected", {"node_id": G4_ORIENTATION_NODE,
            "g2_g3": "qualified_accepted", "g4_m1": "partial"}),
        ("transaction-prepared", {"publication_mode":
            "lease_bound_pointer_last_live_tick"}),
    ):
        event = tc._event(
            journal_id=journal_id, transaction_id=transaction_id,
            operation_id=G4_ORIENTATION_OPERATION, sequence=len(events) + 1,
            previous=previous, event_type=event_type, payload=payload,
        )
        events.append(event)
        previous = event["event_sha256"]
    tc.validate_event_chain(events)
    source_latch = validate_active_operation(json.loads(current["active_latch"].decode("utf-8")))
    transaction = {
        "schema_version": TRANSACTION_VERSION,
        "operation_id": G4_ORIENTATION_OPERATION,
        "transaction_id": transaction_id,
        "source_commit": executing_head,
        "previous_source_commit": G4_ORIENTATION_HEAD,
        "previous_generation_id": G4_OLD_GENERATION_ID,
        "previous_bundle_sha256": G4_OLD_GENERATION_ID[4:],
        "previous_canonical_sha256s": G4_ACTUAL_CANONICAL_SHA256S,
        "previous_metadata_sha256s": {
            name: _hash_bytes(raw) for name, raw in prior_metadata.items()
        },
        "projection_sha256s": {
            "graph": tc.sha256(json.loads(canonical["continuity"].decode("utf-8"))),
            "compass": tc.sha256(json.loads(canonical["compass"].decode("utf-8"))),
            "latch": tc.sha256(source_latch),
        },
        "journal": events,
        "publication_mode": "lease_bound_pointer_last_live_tick",
        "event_kind": G4_ORIENTATION_EVENT,
        "next_boundaries_sha256": tc.sha256(source_latch["protected_boundaries"]),
        "register_bytes_preserved": True,
        "pattern_bytes_preserved": True,
    }
    command_manifest = {
        "schema_version": "ariadne.g4_emr4_compass_command_manifest.v1",
        "profile": "g4_recovery_governance_orientation_only",
        "operation_id": G4_ORIENTATION_OPERATION,
        "source_commit": executing_head,
        "intent_sha256": intent_sha,
        "effect_boundary": "separately_reviewed_g4_reconcile_binding_required",
    }
    metadata = {
        "command-manifest.json": _json_text(command_manifest).encode("utf-8"),
        "transaction.json": _json_text(transaction).encode("utf-8"),
        "ownership.json": prior_metadata["ownership.json"],
    }
    canonical_sha256s = {key: _hash_bytes(raw) for key, raw in canonical.items()}
    metadata_sha256s = {key: _hash_bytes(raw) for key, raw in metadata.items()}
    bundle_sha = _hash_json({"canonical": canonical_sha256s, "metadata": metadata_sha256s})
    generation = {
        "schema_version": GENERATION_VERSION,
        "generation_id": "gen-" + bundle_sha,
        "bundle_sha256": bundle_sha,
        "source_commit": executing_head,
        "previous_generation": {
            "generation_id": G4_OLD_GENERATION_ID,
            "source_commit": G4_ORIENTATION_HEAD,
            "bundle_sha256": G4_OLD_GENERATION_ID[4:],
            "canonical_sha256s": G4_ACTUAL_CANONICAL_SHA256S,
            "metadata_sha256s": {
                name: _hash_bytes(raw) for name, raw in prior_metadata.items()
            },
            "pointer_sha256": G4_OLD_POINTER_SHA256,
        },
        "canonical_sha256s": canonical_sha256s,
        "metadata_sha256s": metadata_sha256s,
        "g4_orientation": {"intent_sha256": intent_sha,
            "observed_baseline_sha256s": G4_ACTUAL_CANONICAL_SHA256S,
            "recorded_generation_sha256s": G4_OLD_CANONICAL_SHA256S},
    }
    pointer = {
        **base_pointer,
        "selected_generation_id": generation["generation_id"],
        "selected_bundle_sha256": generation["bundle_sha256"],
        "previous_generation_id": G4_OLD_GENERATION_ID,
        "previous_source_commit": G4_ORIENTATION_HEAD,
        "lease_sequence": base_pointer["lease_sequence"] + 1,
    }
    prepared = {
        "schema_version": PREPARED_VERSION,
        "contract": contract, "intent": intent,
        "source_commit": executing_head,
        "base_pointer": base_pointer, "canonical": canonical,
        "metadata": metadata, "generation_manifest": generation,
        "pointer": pointer,
    }
    validate_prepared_tick(repo_root, prepared)
    return prepared


def _validate_g4_orientation_prepared(repo_root: Path, row: dict[str, Any]) -> dict[str, Any]:
    if row["schema_version"] != PREPARED_VERSION:
        _reject("g4_orientation_prepared_version")
    contract = validate_contract(row["contract"])
    intent = validate_g4_orientation_intent(row["intent"])
    current, prior_metadata, base_pointer = _g4_orientation_baseline(repo_root, contract, intent)
    executing_head = _assert_g4_git_state(repo_root, contract)
    if row["source_commit"] != executing_head or row["base_pointer"] != base_pointer:
        _reject("g4_orientation_prepared_source")
    canonical = row["canonical"]
    metadata = row["metadata"]
    if set(canonical) != set(CANONICAL_KEYS) or set(metadata) != set(METADATA_NAMES):
        _reject("g4_orientation_prepared_files")
    if canonical != _g4_orientation_projections(
        repo_root, current, intent, source_head=executing_head,
    ):
        _reject("g4_orientation_prepared_projection")
    generation = row["generation_manifest"]
    pointer = row["pointer"]
    canonical_sha = {key: _hash_bytes(raw) for key, raw in canonical.items()}
    metadata_sha = {key: _hash_bytes(raw) for key, raw in metadata.items()}
    bundle_sha = _hash_json({"canonical": canonical_sha, "metadata": metadata_sha})
    prior = generation.get("previous_generation")
    if (
        generation.get("schema_version") != GENERATION_VERSION
        or generation.get("source_commit") != executing_head
        or generation.get("canonical_sha256s") != canonical_sha
        or generation.get("metadata_sha256s") != metadata_sha
        or generation.get("bundle_sha256") != bundle_sha
        or generation.get("generation_id") != "gen-" + bundle_sha
        or not isinstance(prior, dict)
        or prior.get("generation_id") != G4_OLD_GENERATION_ID
        or prior.get("bundle_sha256") != G4_OLD_GENERATION_ID[4:]
        or prior.get("source_commit") != G4_ORIENTATION_HEAD
        or prior.get("canonical_sha256s") != G4_ACTUAL_CANONICAL_SHA256S
        or prior.get("metadata_sha256s") != {
            name: _hash_bytes(raw) for name, raw in prior_metadata.items()}
        or prior.get("pointer_sha256") != G4_OLD_POINTER_SHA256
        or generation.get("g4_orientation") != {
            "intent_sha256": tc.sha256(intent),
            "observed_baseline_sha256s": G4_ACTUAL_CANONICAL_SHA256S,
            "recorded_generation_sha256s": G4_OLD_CANONICAL_SHA256S,
        }
        or pointer != {
            **base_pointer,
            "selected_generation_id": "gen-" + bundle_sha,
            "selected_bundle_sha256": bundle_sha,
            "previous_generation_id": G4_OLD_GENERATION_ID,
            "previous_source_commit": G4_ORIENTATION_HEAD,
            "lease_sequence": 248,
        }
    ):
        _reject("g4_orientation_prepared_identity")
    transaction = _exact(json.loads(metadata["transaction.json"].decode("utf-8")),
        TRANSACTION_KEYS, "g4_orientation_transaction_keys")
    command = json.loads(metadata["command-manifest.json"].decode("utf-8"))
    latch = validate_active_operation(json.loads(current["active_latch"].decode("utf-8")))
    if (
        metadata["ownership.json"] != prior_metadata["ownership.json"]
        or command != {
            "schema_version": "ariadne.g4_emr4_compass_command_manifest.v1",
            "profile": "g4_recovery_governance_orientation_only",
            "operation_id": G4_ORIENTATION_OPERATION,
            "source_commit": executing_head,
            "intent_sha256": tc.sha256(intent),
            "effect_boundary": "separately_reviewed_g4_reconcile_binding_required",
        }
        or transaction["event_kind"] != G4_ORIENTATION_EVENT
        or transaction["operation_id"] != G4_ORIENTATION_OPERATION
        or transaction["source_commit"] != executing_head
        or transaction["previous_source_commit"] != G4_ORIENTATION_HEAD
        or transaction["previous_generation_id"] != G4_OLD_GENERATION_ID
        or transaction["previous_bundle_sha256"] != G4_OLD_GENERATION_ID[4:]
        or transaction["previous_canonical_sha256s"] != G4_ACTUAL_CANONICAL_SHA256S
        or transaction["previous_metadata_sha256s"] != prior["metadata_sha256s"]
        or transaction["next_boundaries_sha256"] != tc.sha256(latch["protected_boundaries"])
        or transaction["projection_sha256s"] != {
            "graph": tc.sha256(json.loads(canonical["continuity"].decode("utf-8"))),
            "compass": tc.sha256(json.loads(canonical["compass"].decode("utf-8"))),
            "latch": tc.sha256(latch),
        }
        or not transaction["register_bytes_preserved"]
        or not transaction["pattern_bytes_preserved"]
        or transaction["publication_mode"] != "lease_bound_pointer_last_live_tick"
    ):
        _reject("g4_orientation_prepared_semantics")
    tc.validate_event_chain(transaction["journal"])
    if (
        transaction["journal"][0]["payload"].get("intent_sha256") != tc.sha256(intent)
        or transaction["journal"][0]["operation_id"] != G4_ORIENTATION_OPERATION
        or transaction["journal"][-1]["transaction_id"] != transaction["transaction_id"]
    ):
        _reject("g4_orientation_prepared_journal")
    return row


def _assert_g4_orientation_command_bytes(
    raw: bytes, source_commit: str, intent_sha256: str
) -> None:
    expected = {
        "schema_version": "ariadne.g4_emr4_compass_command_manifest.v1",
        "profile": "g4_recovery_governance_orientation_only",
        "operation_id": G4_ORIENTATION_OPERATION,
        "source_commit": source_commit,
        "intent_sha256": intent_sha256,
        "effect_boundary": "separately_reviewed_g4_reconcile_binding_required",
    }
    if raw != _json_text(expected).encode("utf-8"):
        _reject("g4_orientation_live_command_bytes")


def _validate_g4_orientation_live(
    repo_root: Path, contract: dict[str, Any], base: dict[str, Any],
    generation: dict[str, Any],
) -> dict[str, Any]:
    """Read back the committed G4 generation without re-admitting the old latch."""

    root = _clockwork_root(repo_root, contract)
    pointer = _load(root / POINTER_NAME)
    intent = validate_g4_orientation_intent(_load(
        repo_root / "orchestration/continuity/g4-emr4-compass-reconnection/orientation-intent.json"
    ))
    prior = generation.get("previous_generation")
    transaction = _exact(_load(root / "transaction.json"), TRANSACTION_KEYS,
        "g4_orientation_live_transaction_keys")
    _assert_g4_orientation_command_bytes(
        (root / "command-manifest.json").read_bytes(),
        generation["source_commit"], tc.sha256(intent),
    )
    source = _source_bytes(repo_root, contract, G4_ORIENTATION_HEAD)
    canonical = {
        key: (repo_root / relative).read_bytes()
        for key, relative in contract["canonical_paths"].items()
    }
    expected = _g4_orientation_projections(
        repo_root, source, intent, source_head=generation["source_commit"],
    )
    if (
        canonical != expected
        or pointer.get("previous_generation_id") != G4_OLD_GENERATION_ID
        or pointer.get("previous_source_commit") != G4_ORIENTATION_HEAD
        or pointer.get("lease_sequence") != 248
        or generation.get("g4_orientation") != {
            "intent_sha256": tc.sha256(intent),
            "observed_baseline_sha256s": G4_ACTUAL_CANONICAL_SHA256S,
            "recorded_generation_sha256s": G4_OLD_CANONICAL_SHA256S,
        }
        or not isinstance(prior, dict)
        or prior.get("generation_id") != G4_OLD_GENERATION_ID
        or prior.get("source_commit") != G4_ORIENTATION_HEAD
        or prior.get("bundle_sha256") != G4_OLD_GENERATION_ID[4:]
        or prior.get("canonical_sha256s") != G4_ACTUAL_CANONICAL_SHA256S
        or prior.get("metadata_sha256s") != {
            **G4_OLD_METADATA_SHA256S,
            GENERATION_NAME: G4_OLD_GENERATION_SHA256,
        }
        or prior.get("pointer_sha256") != G4_OLD_POINTER_SHA256
        or {key: _hash_bytes(raw) for key, raw in source.items()}
        != G4_ACTUAL_CANONICAL_SHA256S
        or _hash_bytes(_git_bytes(
            repo_root, G4_ORIENTATION_HEAD,
            f"{contract['clockwork_root']}/{POINTER_NAME}",
        )) != G4_OLD_POINTER_SHA256
        or transaction["event_kind"] != G4_ORIENTATION_EVENT
        or transaction["operation_id"] != G4_ORIENTATION_OPERATION
        or transaction["source_commit"] != generation["source_commit"]
        or transaction["previous_source_commit"] != G4_ORIENTATION_HEAD
        or transaction["previous_canonical_sha256s"] != G4_ACTUAL_CANONICAL_SHA256S
        or transaction["previous_metadata_sha256s"] != prior["metadata_sha256s"]
        or transaction["projection_sha256s"] != {
            "graph": tc.sha256(json.loads(canonical["continuity"].decode("utf-8"))),
            "compass": tc.sha256(json.loads(canonical["compass"].decode("utf-8"))),
            "latch": tc.sha256(json.loads(canonical["active_latch"].decode("utf-8"))),
        }
    ):
        _reject("g4_orientation_live_semantics")
    tc.validate_event_chain(transaction["journal"])
    if transaction["journal"][0]["payload"].get("intent_sha256") != tc.sha256(intent):
        _reject("g4_orientation_live_intent")
    return {
        **base, "schema_version": "ariadne.governance_live_tick_state.v1",
        "operation_id": G4_ORIENTATION_OPERATION,
        "event_kind": G4_ORIENTATION_EVENT,
        "previous_generation_id": G4_OLD_GENERATION_ID,
        "previous_metadata_files": len(PREDECESSOR_METADATA_NAMES),
    }


def validate_g4_recovery_baseline(
    repo_root: Path, contract_value: object
) -> dict[str, Any]:
    """Read the contained inverse state without calling it a clean generation."""

    contract = validate_contract(contract_value)
    executing_head = _assert_g4_git_state(repo_root, contract)
    source = _source_bytes(repo_root, contract, G4_ORIENTATION_HEAD)
    metadata = _source_metadata(repo_root, contract, G4_ORIENTATION_HEAD)
    source_pointer = _source_pointer(repo_root, contract, G4_ORIENTATION_HEAD)
    root = _clockwork_root(repo_root, contract)
    pointer = _load(root / POINTER_NAME)
    expected_pointer = {**source_pointer, "phase": "recovery_baseline", "lease_sequence": 249}
    physical_canonical = {
        key: (repo_root / relative).read_bytes()
        for key, relative in contract["canonical_paths"].items()
    }
    physical_metadata = {
        name: (root / name).read_bytes() for name in PREDECESSOR_METADATA_NAMES
    }
    if (
        pointer != expected_pointer
        or physical_canonical != source
        or physical_metadata != metadata
        or {key: _hash_bytes(raw) for key, raw in source.items()}
        != G4_ACTUAL_CANONICAL_SHA256S
        or {name: _hash_bytes(metadata[name]) for name in METADATA_NAMES}
        != G4_OLD_METADATA_SHA256S
        or _hash_bytes(metadata[GENERATION_NAME]) != G4_OLD_GENERATION_SHA256
        or _hash_bytes(_git_bytes(
            repo_root, G4_ORIENTATION_HEAD,
            f"{contract['clockwork_root']}/{POINTER_NAME}",
        )) != G4_OLD_POINTER_SHA256
    ):
        _reject("g4_orientation_recovery_baseline_drift")
    generation = json.loads(metadata[GENERATION_NAME].decode("utf-8"))
    if (
        generation.get("generation_id") != G4_OLD_GENERATION_ID
        or generation.get("canonical_sha256s") != G4_OLD_CANONICAL_SHA256S
        or generation.get("metadata_sha256s") != G4_OLD_METADATA_SHA256S
    ):
        _reject("g4_orientation_recovery_generation_identity")
    return {
        "schema_version": "ariadne.g4_compass_recovery_baseline.v1",
        "status": "contained_recovery_baseline",
        "source_commit": executing_head,
        "observed_baseline_commit": G4_ORIENTATION_HEAD,
        "selected_generation_id": G4_OLD_GENERATION_ID,
        "lease_sequence": 249,
        "byte_exact": True,
        "strict_generation_consistent": False,
        "forward_route": "fresh_reviewed_g4_reconciliation_from_lease_249",
    }


def rollback_g4_orientation_generation(
    repo_root: Path, contract_value: object, *, writer_id: str,
    g4_effect_checker: Any = None, g4_effect_context: Any = None,
    g4_effect_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Restore the observed HEAD baseline, retaining the original two-drift record."""

    contract = validate_contract(contract_value)
    if writer_id != WRITER:
        _reject("tick_writer_not_clockwork")
    state = validate_tick_live_state(repo_root, contract)
    if state["event_kind"] != G4_ORIENTATION_EVENT:
        _reject("g4_orientation_rollback_wrong_generation")
    root = _clockwork_root(repo_root, contract)
    pointer_path = root / POINTER_NAME
    pointer = _load(pointer_path)
    source = G4_ORIENTATION_HEAD
    previous_canonical = _source_bytes(repo_root, contract, source)
    previous_metadata = _source_metadata(repo_root, contract, source)
    previous_pointer = _source_pointer(repo_root, contract, source)
    if (
        {key: _hash_bytes(raw) for key, raw in previous_canonical.items()}
        != G4_ACTUAL_CANONICAL_SHA256S
        or {name: _hash_bytes(previous_metadata[name]) for name in METADATA_NAMES}
        != G4_OLD_METADATA_SHA256S
        or _hash_bytes(previous_metadata[GENERATION_NAME]) != G4_OLD_GENERATION_SHA256
        or pointer["lease_sequence"] != 248
    ):
        _reject("g4_orientation_rollback_baseline")
    restored_pointer = {**previous_pointer, "phase": "recovery_baseline", "lease_sequence": 249}
    recovery_prepared = {
        "contract": contract, "canonical": previous_canonical,
        "metadata": previous_metadata, "pointer": restored_pointer,
    }
    if not callable(g4_effect_checker) or g4_effect_context is None or g4_effect_manifest is None:
        _reject("g4_orientation_rollback_admission_required")
    _verify_g4_rollback_manifest_images(repo_root, recovery_prepared, g4_effect_manifest)
    decision = g4_effect_checker(
        context=g4_effect_context, manifest=g4_effect_manifest,
        prepared=recovery_prepared, phase="rollback"
    )
    if not getattr(decision, "execution_authorized", False):
        _reject("g4_orientation_rollback_not_authorized")
    lease_path = root / "writer.lock"
    canonical_targets = {
        key: repo_root / relative for key, relative in contract["canonical_paths"].items()
    }
    metadata_targets = {name: root / name for name in PREDECESSOR_METADATA_NAMES}
    staged: dict[str, Path] = {}
    acquired = False
    snapshots_complete = False
    committed = False
    try:
        _write_lease(
            lease_path, operation_id=G4_ORIENTATION_OPERATION,
            source=state["source_commit"],
            pointer={**restored_pointer, "previous_generation_id": G4_OLD_GENERATION_ID},
        )
        acquired = True
        _assert_g4_git_state(repo_root, contract, state["head"])
        _verify_g4_rollback_manifest_images(repo_root, recovery_prepared, g4_effect_manifest)
        decision = g4_effect_checker(
            context=g4_effect_context, manifest=g4_effect_manifest,
            prepared=recovery_prepared, phase="rollback"
        )
        if not getattr(decision, "execution_authorized", False):
            _reject("g4_orientation_rollback_not_authorized")
        current_canonical = {key: path.read_bytes() for key, path in canonical_targets.items()}
        current_metadata = {name: path.read_bytes() for name, path in metadata_targets.items()}
        current_pointer = pointer_path.read_bytes()
        snapshots_complete = True
        for key, target in canonical_targets.items():
            staged[f"canonical:{key}"] = _write_temp(target, previous_canonical[key])
        for name, target in metadata_targets.items():
            staged[f"metadata:{name}"] = _write_temp(target, previous_metadata[name])
        staged["pointer"] = _write_temp(pointer_path, _json_text(restored_pointer).encode("utf-8"))
        for key, target in canonical_targets.items():
            os.replace(staged.pop(f"canonical:{key}"), target)
        for name, target in metadata_targets.items():
            os.replace(staged.pop(f"metadata:{name}"), target)
        os.replace(staged.pop("pointer"), pointer_path)
        committed = True
        validated = validate_g4_recovery_baseline(repo_root, contract)
        _verify_g4_committed_images(repo_root, contract, g4_effect_manifest)
        return {
            "schema_version": "ariadne.governance_live_tick_rollback.v1",
            "status": "contained_recovery_baseline",
            "rolled_back_from_generation_id": state["generation_id"],
            "selected_generation_id": G4_OLD_GENERATION_ID,
            "previous_source_commit": source, "lease_sequence": 249,
            "byte_exact": validated["byte_exact"],
            "restored_baseline": "observed_head_two_drift",
            "forward_route": "fresh_reviewed_g4_reconciliation_from_lease_249",
        }
    except BaseException as error:
        if not committed and snapshots_complete:
            for key, target in canonical_targets.items():
                target.write_bytes(current_canonical[key])
            for name, target in metadata_targets.items():
                target.write_bytes(current_metadata[name])
            pointer_path.write_bytes(current_pointer)
            if (
                any(target.read_bytes() != current_canonical[key]
                    for key, target in canonical_targets.items())
                or any(target.read_bytes() != current_metadata[name]
                    for name, target in metadata_targets.items())
                or pointer_path.read_bytes() != current_pointer
            ):
                _reject("g4_orientation_rollback_precommit_restore_failed")
        if committed:
            raise CommittedClockworkTick(
                "g4_orientation_rollback_committed_readback_uncertain"
            ) from error
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        if acquired:
            lease_path.unlink(missing_ok=True)
