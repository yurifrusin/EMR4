"""Fail-closed programme admission for the EMR4 recovery controller.

This module is deliberately project-neutral at the admission boundary: callers
provide a typed task manifest and an entrypoint class.  The repository policy
files decide whether that task may execute.  Receipts remain evidence and are
never themselves admission tokens.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

import yaml

STATE_PATH = Path("orchestration/programme/current-state.json")
GATES_PATH = Path("orchestration/programme/gates.yaml")
RISK_PATH = Path("orchestration/programme/risk-register.yaml")
INVENTORY_PATH = Path("orchestration/programme/branch-pr-disposition.yaml")
OVERLAY_PATH = Path("orchestration/harness_settings/programme_recovery.yaml")
PROJECT_PATH = Path("orchestration/harness_settings/project.yaml")
CONTINUATION_PATH = Path(
    "orchestration/harness_settings/autonomous_continuation.yaml"
)
LATCH_PATH = Path("orchestration/continuity/ariadne-active-operation-latch/current.json")
AGENTS_PATH = Path("AGENTS.md")

TASK_MANIFEST_VERSION = "ariadne.programme_task_manifest.v1"
DECISION_VERSION = "ariadne.programme_admission_decision.v1"
SCOPE_VERSION = "ariadne.programme_scope_decision.v1"
ADMITTED_TASK_CLASS = "g0_1_controller_maintenance"
ADMITTED_PROGRAMME_GATE = "G0.1"

TASK_MANIFEST_KEYS = {
    "schema_version",
    "task_id",
    "task_class",
    "programme_gate",
    "objective",
    "base_commit",
    "candidate_or_current_head",
    "allowed_path_roots",
    "intended_side_effect_classes",
    "forbidden_side_effect_classes",
    "state_digest",
    "policy_digest",
}

FORBIDDEN_EFFECTS = {
    "autonomous_worker_dispatch",
    "provider_invocation",
    "product_behavior_change",
    "dependency_change",
    "integration",
    "protected_ref_movement",
    "deployment",
    "pages",
    "real_data_access",
}
ALLOWED_MAINTENANCE_EFFECTS = {
    "repository_read",
    "control_plane_edit",
    "task_branch_commit",
    "task_branch_push",
}
ENTRYPOINT_REQUIRED_EFFECT = {
    "task_selection": "repository_read",
    "recovery_preflight": "repository_read",
    "task_branch_commit": "task_branch_commit",
    "task_branch_push": "task_branch_push",
}
ENTRYPOINTS_CLOSED_IN_G0 = {
    "worker_dispatch",
    "provider_invocation",
    "clockwork_tick_mutation",
    "clockwork_closeout_mutation",
    "integration",
    "protected_ref_operation",
    "deployment",
}
ENTRYPOINTS = set(ENTRYPOINT_REQUIRED_EFFECT) | ENTRYPOINTS_CLOSED_IN_G0
G0_G01_ALLOWED_PATHS = {
    "AGENTS.md",
    "docs/architecture/ariadne-clockwork-correction.md",
    "docs/architecture/raisa-projection-native-north-star.md",
    "docs/programme/raisa-ariadne-recovery-programme.md",
    "orchestration/continuity/ariadne-active-operation-latch/current.json",
    "orchestration/harness_settings/autonomous_continuation.yaml",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/harness_settings/project.yaml",
    "orchestration/programme/branch-pr-disposition.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/gates.yaml",
    "orchestration/programme/risk-register.yaml",
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/orchestrator_preflight.py",
    "scripts/agent_worktrees.py",
    "scripts/ariadne_antigravity.py",
    "scripts/ariadne_deepseek_claude.py",
    "scripts/ariadne_governance_clockwork_closeout.py",
    "scripts/ariadne_governance_clockwork_tick.py",
    "scripts/ariadne_orchestrator_preflight.py",
    "scripts/drive_agent_headless.py",
    "scripts/raisa_ariadne_recovery_preflight.py",
    "tests/fixtures/ariadne_harness/orchestrator_runtime_state.json",
    "tests/test_ariadne_governance_clockwork_tick.py",
    "tests/test_ariadne_orchestrator_preflight.py",
    "tests/test_programme_admission.py",
    "tests/test_raisa_ariadne_recovery_preflight.py",
}

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class ProgrammeAdmissionError(ValueError):
    """A programme policy, task manifest, or Git binding failed closed."""

    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise ProgrammeAdmissionError("yaml_mapping_key_invalid") from error
        if duplicate:
            raise ProgrammeAdmissionError("yaml_duplicate_key")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _reject_duplicate_json(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProgrammeAdmissionError("json_duplicate_key")
        value[key] = item
    return value


def _strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_json
        )
    except ProgrammeAdmissionError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ProgrammeAdmissionError("programme_json_missing_or_invalid") from error
    if not isinstance(value, dict):
        raise ProgrammeAdmissionError("programme_json_root_not_object")
    return value


def _strict_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except ProgrammeAdmissionError:
        raise
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ProgrammeAdmissionError("programme_yaml_missing_or_invalid") from error
    if not isinstance(value, dict):
        raise ProgrammeAdmissionError("programme_yaml_root_not_object")
    return value


def strict_json_object(path: Path) -> dict[str, Any]:
    """Public strict JSON loader for gated CLI entrypoints."""
    return _strict_json(path)


def _exact_keys(value: object, expected: set[str], reason: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise ProgrammeAdmissionError(reason)
    return value


def _bounded_text(value: object, reason: str, maximum: int = 1000) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
        or "\r" in value
        or "\n" in value
    ):
        raise ProgrammeAdmissionError(reason)
    return value


def _bool(value: object, expected: bool, reason: str) -> None:
    if value is not expected:
        raise ProgrammeAdmissionError(reason)


def _unique_text_list(
    value: object, reason: str, *, minimum: int = 1, maximum: int = 256
) -> list[str]:
    if (
        not isinstance(value, list)
        or not minimum <= len(value) <= maximum
        or any(not isinstance(item, str) or not item or item != item.strip() for item in value)
        or len(set(value)) != len(value)
    ):
        raise ProgrammeAdmissionError(reason)
    return list(value)


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _digest_paths(root: Path, paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for relative in paths:
        try:
            payload = (root / relative).read_bytes()
        except OSError as error:
            raise ProgrammeAdmissionError("programme_policy_file_missing") from error
        label = relative.as_posix().encode("utf-8")
        digest.update(len(label).to_bytes(4, "big"))
        digest.update(label)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return "sha256:" + digest.hexdigest()


def _run_git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProgrammeAdmissionError("git_observation_failed") from error
    if completed.returncode != 0:
        raise ProgrammeAdmissionError("git_observation_failed")
    return completed.stdout.strip()


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=root,
            check=False,
            capture_output=True,
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProgrammeAdmissionError("git_observation_failed") from error
    if completed.returncode not in {0, 1}:
        raise ProgrammeAdmissionError("git_observation_failed")
    return completed.returncode == 0


def _validate_state(value: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {
            "schema_version",
            "observed_at",
            "programme_name",
            "programme_mode",
            "current_gate",
            "current_gate_status",
            "machine_authoritative",
            "feature_work_eligible",
            "authority",
            "recovery_baton",
            "protected_refs",
            "clockwork_snapshot",
            "repository_inventory",
            "product_path_inventory",
            "workflow_inventory",
            "harness_inventory",
            "global_checks",
            "stop_ship_containment",
            "task_selection",
            "parallelism_efficacy",
            "actions_performed",
            "g0_acceptance",
            "g0_1_correction",
        },
        "programme_state_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.programme-state.v1"
        or value["programme_mode"] != "recovery"
        or value["current_gate"] != "G0"
        or value["current_gate_status"] != "revision_required"
        or value["machine_authoritative"] is not True
        or value["feature_work_eligible"] is not False
    ):
        raise ProgrammeAdmissionError("programme_state_not_fail_closed_g0")

    authority = _exact_keys(
        value["authority"],
        {
            "owner",
            "directive_sha256",
            "structured_state_precedence",
            "narrative_handover_role",
            "missing_or_invalid_state",
        },
        "programme_authority_schema_invalid",
    )
    if (
        authority["owner"] != "Yuri"
        or authority["structured_state_precedence"]
        != "current-state.json then gates.yaml"
        or authority["narrative_handover_role"] != "evidence_and_continuity_only"
        or authority["missing_or_invalid_state"] != "hard_stop"
    ):
        raise ProgrammeAdmissionError("programme_authority_precedence_invalid")

    selection = _exact_keys(
        value["task_selection"],
        {
            "autonomous_selection_enabled",
            "allowed_task_kinds",
            "blocked_task_kinds",
            "admission_command",
            "out_of_gate_result",
            "next_eligible_tranche",
            "next_eligible_now",
            "next_tranche_started",
            "next_tranche_admission_requires_state_transition",
            "next_eligibility_condition",
        },
        "programme_task_selection_schema_invalid",
    )
    blocked_task_kinds = set(
        _unique_text_list(
            selection["blocked_task_kinds"], "blocked_task_kinds_invalid"
        )
    )
    if (
        selection["autonomous_selection_enabled"] is not False
        or selection["allowed_task_kinds"] != [ADMITTED_TASK_CLASS]
        or blocked_task_kinds
        != {
            "product_feature",
            "g1a",
            "integration",
            "provider_call",
            "deployment",
            "protected_ref_operation",
        }
        or selection["out_of_gate_result"] != "blocked"
        or selection["next_eligible_tranche"] != ADMITTED_PROGRAMME_GATE
        or selection["next_tranche_started"] is not False
    ):
        raise ProgrammeAdmissionError("programme_task_selection_not_fail_closed")

    correction = _exact_keys(
        value["g0_1_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_tree",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_1_correction_schema_invalid",
    )
    if (
        correction["status"] not in {"in_progress", "review_pending"}
        or not isinstance(correction["authorized_parent_commit"], str)
        or _SHA1.fullmatch(correction["authorized_parent_commit"]) is None
        or correction["candidate_commit_limit"] != 1
        or correction["external_review_status"] not in {"not_started", "pending"}
        or correction["g1a_authorized"] is not False
    ):
        raise ProgrammeAdmissionError("g0_1_correction_not_fail_closed")

    baton = value.get("recovery_baton")
    if not isinstance(baton, dict):
        raise ProgrammeAdmissionError("recovery_baton_schema_invalid")
    if (
        baton.get("branch") != "codex/raisa-ariadne-recovery-g0"
        or not isinstance(baton.get("base_sha"), str)
        or _SHA1.fullmatch(baton["base_sha"]) is None
    ):
        raise ProgrammeAdmissionError("recovery_baton_invalid")

    protected = value.get("protected_refs")
    if (
        not isinstance(protected, dict)
        or protected.get("movement_authorized") is not False
        or not isinstance(protected.get("expected_sha"), str)
        or _SHA1.fullmatch(protected["expected_sha"]) is None
        or len(_unique_text_list(protected.get("refs"), "protected_refs_invalid")) != 4
    ):
        raise ProgrammeAdmissionError("protected_refs_invalid")
    parallelism = _exact_keys(
        value["parallelism_efficacy"],
        {"deepseek", "gemini", "native_subagent"},
        "parallelism_efficacy_schema_invalid",
    )
    for lane in parallelism.values():
        row = _exact_keys(
            lane,
            {"disposition", "rationale"},
            "parallelism_lane_schema_invalid",
        )
        if row["disposition"] not in {"declined", "reserved", "planned"}:
            raise ProgrammeAdmissionError("parallelism_lane_disposition_invalid")
        _bounded_text(row["rationale"], "parallelism_lane_rationale_invalid", 500)


def _validate_gates(value: dict[str, Any], state: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {"schema_version", "programme", "global_hard_stops", "protected_invariants", "gates"},
        "programme_gates_schema_invalid",
    )
    if value["schema_version"] != "raisa-ariadne.programme-gates.v1":
        raise ProgrammeAdmissionError("programme_gates_version_invalid")
    programme = _exact_keys(
        value["programme"],
        {
            "name",
            "prepared_at",
            "repository",
            "observed_public_master",
            "programme_mode",
            "current_gate",
            "current_gate_status",
            "feature_work_eligible",
            "clockwork_remote_visibility",
            "clockwork_local_state",
            "next_eligible_tranche",
        },
        "programme_gate_header_schema_invalid",
    )
    if (
        programme["programme_mode"] != state["programme_mode"]
        or programme["current_gate"] != state["current_gate"]
        or programme["current_gate_status"] != state["current_gate_status"]
        or programme["feature_work_eligible"] is not False
        or programme["next_eligible_tranche"] != ADMITTED_PROGRAMME_GATE
    ):
        raise ProgrammeAdmissionError("programme_state_gate_disagreement")
    _unique_text_list(value["global_hard_stops"], "global_hard_stops_invalid")
    protected = _exact_keys(
        value["protected_invariants"], {"raisa", "ariadne"}, "protected_invariants_invalid"
    )
    _unique_text_list(protected["raisa"], "raisa_invariants_invalid")
    _unique_text_list(protected["ariadne"], "ariadne_invariants_invalid")
    gates = value["gates"]
    if not isinstance(gates, list) or not gates:
        raise ProgrammeAdmissionError("gate_inventory_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    allowed_gate_keys = {
        "id", "name", "status", "prerequisites", "programme_mode", "allowed_work",
        "prohibited_work", "exit_checks", "next_gate",
    }
    for gate in gates:
        if not isinstance(gate, dict) or not set(gate).issubset(allowed_gate_keys):
            raise ProgrammeAdmissionError("gate_schema_invalid")
        required = {"id", "name", "status", "prerequisites", "programme_mode", "exit_checks", "next_gate"}
        if not required.issubset(gate):
            raise ProgrammeAdmissionError("gate_schema_invalid")
        gate_id = _bounded_text(gate["id"], "gate_id_invalid", 32)
        if gate_id in by_id:
            raise ProgrammeAdmissionError("gate_id_duplicate")
        _unique_text_list(gate["exit_checks"], "gate_exit_checks_invalid")
        if gate["programme_mode"] not in {"recovery", "convergence", "pilot_preparation", "release"}:
            raise ProgrammeAdmissionError("gate_mode_invalid")
        by_id[gate_id] = gate
    expected_statuses = {
        "G0": "revision_required_g0_1",
        "G0.1": state["g0_1_correction"]["status"],
        "G1A": "blocked_by_external_G0_review",
        "G1B": "blocked_by_G1A",
        "G1C": "blocked_by_G1B",
        "G1D": "blocked_by_G1C",
        "G1E": "blocked_by_G1D",
        "G2": "blocked_by_G1",
        "G3": "blocked_by_G2",
        "G4": "blocked_by_G3",
        "G5": "blocked_by_G4",
        "G6": "blocked_by_G5",
        "G7": "blocked_by_G6",
        "G8": "blocked_by_G7",
    }
    if set(by_id) != set(expected_statuses) or any(
        by_id[gate_id]["status"] != status
        for gate_id, status in expected_statuses.items()
    ):
        raise ProgrammeAdmissionError("gate_status_vocabulary_invalid")
    if state["g0_1_correction"]["status"] not in {"in_progress", "review_pending"}:
        raise ProgrammeAdmissionError("g0_1_status_invalid")
    if by_id["G0.1"]["status"] != state["g0_1_correction"]["status"]:
        raise ProgrammeAdmissionError("programme_state_gate_disagreement")
    if by_id.get("G1A", {}).get("status") != "blocked_by_external_G0_review":
        raise ProgrammeAdmissionError("g1a_not_closed")


def _validate_risks(value: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {"schema_version", "observed_at", "programme_mode", "current_gate", "status_vocabulary", "default_g0_control", "risks"},
        "risk_register_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.risk-register.v1"
        or value["programme_mode"] != "recovery"
        or value["current_gate"] != "G0"
    ):
        raise ProgrammeAdmissionError("risk_register_header_invalid")
    vocabulary = set(_unique_text_list(value["status_vocabulary"], "risk_status_vocabulary_invalid"))
    if vocabulary != {
        "observed_unresolved",
        "seeded_requires_verification",
        "contained_by_g0_feature_freeze",
        "closed_with_evidence",
    }:
        raise ProgrammeAdmissionError("risk_status_vocabulary_invalid")
    expected = {*(f"R-{index:03d}" for index in range(1, 14)), *(f"A-{index:03d}" for index in range(1, 11))}
    risks = value["risks"]
    if not isinstance(risks, list) or len(risks) != len(expected):
        raise ProgrammeAdmissionError("risk_inventory_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    for risk in risks:
        item = _exact_keys(
            risk,
            {"id", "risk", "owner", "gate", "status", "evidence", "g0_disposition"},
            "risk_entry_schema_invalid",
        )
        risk_id = _bounded_text(item["id"], "risk_id_invalid", 16)
        if risk_id in by_id:
            raise ProgrammeAdmissionError("risk_id_duplicate")
        for field in ("risk", "owner", "gate", "evidence", "g0_disposition"):
            _bounded_text(item[field], f"risk_{field}_invalid", 1000)
        if item["status"] not in vocabulary:
            raise ProgrammeAdmissionError("risk_status_invalid")
        by_id[risk_id] = item
    if set(by_id) != expected:
        raise ProgrammeAdmissionError("risk_inventory_invalid")
    if "upgrade() executes op.execute" not in by_id["R-001"]["evidence"] or "TRUNCATE TABLE prescriptions" not in by_id["R-001"]["evidence"]:
        raise ProgrammeAdmissionError("risk_r001_evidence_invalid")
    if "static/audio" not in by_id["R-003"]["evidence"] or "app/main.py mounts static at /static" not in by_id["R-003"]["evidence"]:
        raise ProgrammeAdmissionError("risk_r003_evidence_invalid")


def _validate_inventory(value: dict[str, Any], state: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {
            "schema_version", "observed_at", "repository", "programme_mode", "current_gate",
            "mutation_policy", "authoritative_refs", "remote_branch_inventory", "local_topology",
            "ambiguous_current_aliases", "open_pr_inventory", "g0_conclusion",
        },
        "branch_inventory_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.branch-pr-disposition.v1"
        or value["programme_mode"] != state["programme_mode"]
        or value["current_gate"] != state["current_gate"]
    ):
        raise ProgrammeAdmissionError("branch_inventory_header_invalid")
    mutation = _exact_keys(
        value["mutation_policy"],
        {"branch_deletion", "pr_closure", "pr_merge", "feature_rebase", "protected_ref_movement"},
        "mutation_policy_schema_invalid",
    )
    if set(mutation.values()) != {"forbidden"}:
        raise ProgrammeAdmissionError("mutation_policy_not_fail_closed")
    refs = value.get("authoritative_refs")
    if not isinstance(refs, dict) or refs.get("recovery_branch") != state["recovery_baton"]["branch"] or refs.get("recovery_base") != state["recovery_baton"]["base_sha"]:
        raise ProgrammeAdmissionError("branch_inventory_authority_disagreement")
    open_prs = value.get("open_pr_inventory")
    if not isinstance(open_prs, dict) or not isinstance(open_prs.get("prs"), list) or open_prs.get("count") != len(open_prs["prs"]):
        raise ProgrammeAdmissionError("open_pr_inventory_invalid")
    numbers: set[int] = set()
    for pr in open_prs["prs"]:
        if not isinstance(pr, dict) or not set(pr).issubset({"number", "draft", "head", "base", "disposition", "stack_order"}):
            raise ProgrammeAdmissionError("open_pr_entry_schema_invalid")
        if not {"number", "draft", "head", "base", "disposition"}.issubset(pr):
            raise ProgrammeAdmissionError("open_pr_entry_schema_invalid")
        if pr["disposition"] not in {"dependency_update", "quarantine"}:
            raise ProgrammeAdmissionError("open_pr_disposition_invalid")
        number = pr["number"]
        if isinstance(number, bool) or not isinstance(number, int) or number <= 0 or number in numbers:
            raise ProgrammeAdmissionError("open_pr_number_invalid")
        numbers.add(number)


def _validate_overlay(
    value: dict[str, Any], state: dict[str, Any], root: Path
) -> list[str]:
    _exact_keys(
        value,
        {
            "schema_version", "status", "authority_owner", "recorded_at", "state_file", "gates_file",
            "risk_file", "inventory_file", "admission_command", "required_before", "recovery_mode",
            "scope_policy", "gated_entrypoints", "missing_or_invalid_state", "reversibility",
        },
        "recovery_overlay_schema_invalid",
    )
    if (
        value["schema_version"] != "ariadne.programme_recovery.v2"
        or value["status"] != "active_emergency_overlay"
        or value["authority_owner"] != "Yuri"
        or value["state_file"] != STATE_PATH.as_posix()
        or value["gates_file"] != GATES_PATH.as_posix()
        or value["risk_file"] != RISK_PATH.as_posix()
        or value["inventory_file"] != INVENTORY_PATH.as_posix()
        or value["missing_or_invalid_state"] != "hard_stop"
    ):
        raise ProgrammeAdmissionError("recovery_overlay_header_invalid")
    required = set(_unique_text_list(value["required_before"], "recovery_required_before_invalid"))
    if required != ENTRYPOINTS:
        raise ProgrammeAdmissionError("recovery_entrypoint_coverage_incomplete")
    recovery = _exact_keys(
        value["recovery_mode"],
        {
            "expected_programme_mode", "expected_current_gate", "expected_gate_status",
            "active_correction", "autonomous_task_selection", "admitted_task_classes",
            "out_of_gate_result", "feature_work_eligible", "provider_calls_eligible",
            "deployment_eligible", "protected_ref_movement_eligible", "g1a_eligible",
        },
        "recovery_mode_schema_invalid",
    )
    if (
        recovery["expected_programme_mode"] != state["programme_mode"]
        or recovery["expected_current_gate"] != state["current_gate"]
        or recovery["expected_gate_status"] != state["current_gate_status"]
        or recovery["active_correction"] != ADMITTED_PROGRAMME_GATE
        or recovery["autonomous_task_selection"] is not False
        or recovery["admitted_task_classes"] != [ADMITTED_TASK_CLASS]
        or any(recovery[key] is not False for key in ("feature_work_eligible", "provider_calls_eligible", "deployment_eligible", "protected_ref_movement_eligible", "g1a_eligible"))
    ):
        raise ProgrammeAdmissionError("recovery_mode_not_fail_closed")
    scope = _exact_keys(
        value["scope_policy"],
        {"expected_branch", "frozen_recovery_base", "authorized_parent_commit", "candidate_commit_limit", "allowed_paths"},
        "scope_policy_schema_invalid",
    )
    if (
        scope["expected_branch"] != state["recovery_baton"]["branch"]
        or scope["frozen_recovery_base"] != state["recovery_baton"]["base_sha"]
        or scope["authorized_parent_commit"] != state["g0_1_correction"]["authorized_parent_commit"]
        or scope["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("scope_policy_state_disagreement")
    allowed_paths = _unique_text_list(scope["allowed_paths"], "scope_allowed_paths_invalid")
    if set(allowed_paths) != G0_G01_ALLOWED_PATHS:
        raise ProgrammeAdmissionError("scope_allowed_paths_not_exact")
    for raw in allowed_paths:
        path = PurePosixPath(raw)
        if path.is_absolute() or "\\" in raw or any(part in {"", ".", ".."} for part in path.parts):
            raise ProgrammeAdmissionError("scope_allowed_path_invalid")
    entrypoints = value["gated_entrypoints"]
    if not isinstance(entrypoints, list) or not entrypoints:
        raise ProgrammeAdmissionError("gated_entrypoint_inventory_invalid")
    observed: set[str] = set()
    observed_ids: set[str] = set()
    for item in entrypoints:
        row = _exact_keys(item, {"id", "path", "entrypoint"}, "gated_entrypoint_schema_invalid")
        entrypoint = row["entrypoint"]
        entrypoint_id = row["id"]
        if entrypoint not in ENTRYPOINTS or entrypoint_id in observed_ids:
            raise ProgrammeAdmissionError("gated_entrypoint_inventory_invalid")
        observed.add(entrypoint)
        observed_ids.add(entrypoint_id)
        _bounded_text(entrypoint_id, "gated_entrypoint_id_invalid", 128)
        entrypoint_path = _bounded_text(
            row["path"], "gated_entrypoint_path_invalid", 240
        )
        if entrypoint_path not in G0_G01_ALLOWED_PATHS or not (
            root / entrypoint_path
        ).is_file():
            raise ProgrammeAdmissionError("gated_entrypoint_path_invalid")
    if observed != ENTRYPOINTS:
        raise ProgrammeAdmissionError("recovery_entrypoint_coverage_incomplete")
    return allowed_paths


def _validate_precedence(project: dict[str, Any], continuation: dict[str, Any], agents_text: str) -> None:
    _exact_keys(
        project,
        {"schema_version", "project_id", "master_authority", "allocation", "operating_model", "secure_sdlc", "direction_collaboration", "autonomous_continuation", "cost_controls"},
        "project_settings_schema_invalid",
    )
    _exact_keys(
        continuation,
        {"schema_version", "default_posture", "emergency_programme_overlay", "applies_when", "policy_decision", "standing_programme_authority", "architecture_strengthening_choice_policy", "failure_loop", "authority", "execution_limits", "pause_for_user_only_when", "must_not_pause_for", "evidence", "task_lifecycle", "resume_checkpoint", "document_metadata"},
        "continuation_settings_schema_invalid",
    )
    project_overlay = project.get("autonomous_continuation", {}).get("emergency_overlay", {})
    continuation_overlay = continuation.get("emergency_programme_overlay", {})
    if (
        project_overlay != {
            "settings_file": "programme_recovery.yaml",
            "required": True,
            "precedence": "higher_than_standing_continuation",
            "missing_or_invalid": "hard_stop",
        }
        or continuation_overlay != {
            "status": "active",
            "settings_file": "programme_recovery.yaml",
            "precedence": "higher_than_default_posture_and_standing_programme_authority",
            "required_before_task_selection": True,
            "missing_or_invalid": "hard_stop",
        }
    ):
        raise ProgrammeAdmissionError("recovery_precedence_invalid")
    required_header = (
        "# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE",
        "Gate G0.1 is the only authorised correction; G1A is",
        "Missing, malformed, stale, or contradictory programme state is a hard stop.",
    )
    if not agents_text.startswith(required_header[0]) or any(token not in agents_text[:1200] for token in required_header[1:]):
        raise ProgrammeAdmissionError("agents_recovery_precedence_missing")


def _validate_latch(value: dict[str, Any], current_fingerprint: str) -> None:
    from orchestration_harness.active_operation import validate_active_operation

    try:
        latch = validate_active_operation(value)
    except ValueError as error:
        raise ProgrammeAdmissionError("active_operation_latch_invalid") from error
    if (
        latch["status"] != "replaced"
        or latch["resume_after_compaction"] is not False
        or latch["checkpoint"]["next_executable_stage"] is not None
        or latch["terminal_response"]["permitted"] is not True
        or latch["checkpoint"]["settings_fingerprint"] != current_fingerprint
        or "Yuri" not in latch["authority_source"]
        or "G0" not in latch["authority_source"]
    ):
        raise ProgrammeAdmissionError("historical_latch_not_terminally_replaced")


@dataclass(frozen=True)
class ProgrammePolicy:
    state: dict[str, Any]
    gates: dict[str, Any]
    risks: dict[str, Any]
    inventory: dict[str, Any]
    overlay: dict[str, Any]
    project: dict[str, Any]
    continuation: dict[str, Any]
    latch: dict[str, Any]
    state_digest: str
    policy_digest: str
    settings_fingerprint: str
    allowed_paths: tuple[str, ...]


def load_programme_policy(repo_root: Path) -> ProgrammePolicy:
    """Strictly load and cross-check all controlling recovery inputs."""
    root = repo_root.resolve()
    state = _strict_json(root / STATE_PATH)
    gates = _strict_yaml(root / GATES_PATH)
    risks = _strict_yaml(root / RISK_PATH)
    inventory = _strict_yaml(root / INVENTORY_PATH)
    overlay = _strict_yaml(root / OVERLAY_PATH)
    project = _strict_yaml(root / PROJECT_PATH)
    continuation = _strict_yaml(root / CONTINUATION_PATH)
    latch = _strict_json(root / LATCH_PATH)
    try:
        agents_text = (root / AGENTS_PATH).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ProgrammeAdmissionError("agents_handover_missing") from error
    _validate_state(state)
    _validate_gates(gates, state)
    _validate_risks(risks)
    _validate_inventory(inventory, state)
    allowed_paths = _validate_overlay(overlay, state, root)
    _validate_precedence(project, continuation, agents_text)
    from orchestration_harness.settings_fingerprint import settings_fingerprint

    settings_digest = settings_fingerprint(root / "orchestration/harness_settings")
    _validate_latch(latch, settings_digest)
    state_digest = _sha256_bytes((root / STATE_PATH).read_bytes())
    policy_digest = _digest_paths(
        root,
        (
            GATES_PATH,
            RISK_PATH,
            INVENTORY_PATH,
            OVERLAY_PATH,
            PROJECT_PATH,
            CONTINUATION_PATH,
            LATCH_PATH,
            AGENTS_PATH,
        ),
    )
    return ProgrammePolicy(
        state=state,
        gates=gates,
        risks=risks,
        inventory=inventory,
        overlay=overlay,
        project=project,
        continuation=continuation,
        latch=latch,
        state_digest=state_digest,
        policy_digest=policy_digest,
        settings_fingerprint=settings_digest,
        allowed_paths=tuple(allowed_paths),
    )


@dataclass(frozen=True)
class ProgrammeDecision:
    schema_version: str
    admitted: bool
    reason_codes: list[str]
    mode: str | None
    gate: str | None
    task_class: str | None
    state_digest: str | None
    policy_digest: str | None


@dataclass(frozen=True)
class ScopeDecision:
    schema_version: str
    admitted: bool
    reason_codes: list[str]
    phase: str
    branch: str | None
    head: str | None
    origin_head: str | None
    authorized_parent_commit: str | None
    candidate_commit_count: int | None
    changed_paths: list[str]


def _decision(
    *,
    admitted: bool,
    reasons: Sequence[str],
    policy: ProgrammePolicy | None,
    task_class: str | None,
) -> ProgrammeDecision:
    return ProgrammeDecision(
        schema_version=DECISION_VERSION,
        admitted=admitted,
        reason_codes=list(dict.fromkeys(reasons)),
        mode=policy.state["programme_mode"] if policy else None,
        gate=policy.state["current_gate"] if policy else None,
        task_class=task_class,
        state_digest=policy.state_digest if policy else None,
        policy_digest=policy.policy_digest if policy else None,
    )


def _validate_manifest(
    value: object, *, policy: ProgrammePolicy, repo_root: Path
) -> tuple[dict[str, Any], list[str]]:
    manifest = _exact_keys(value, TASK_MANIFEST_KEYS, "task_manifest_schema_invalid")
    if manifest["schema_version"] != TASK_MANIFEST_VERSION:
        raise ProgrammeAdmissionError("task_manifest_version_invalid")
    task_id = _bounded_text(manifest["task_id"], "task_manifest_task_id_invalid", 128)
    if _IDENTIFIER.fullmatch(task_id) is None:
        raise ProgrammeAdmissionError("task_manifest_task_id_invalid")
    _bounded_text(manifest["objective"], "task_manifest_objective_invalid", 1000)
    task_class = manifest["task_class"]
    if task_class != ADMITTED_TASK_CLASS:
        raise ProgrammeAdmissionError("task_class_not_admitted")
    if manifest["programme_gate"] != ADMITTED_PROGRAMME_GATE:
        raise ProgrammeAdmissionError("task_gate_not_admitted")
    base = manifest["base_commit"]
    head = manifest["candidate_or_current_head"]
    if not isinstance(base, str) or _SHA1.fullmatch(base) is None:
        raise ProgrammeAdmissionError("task_manifest_base_invalid")
    if not isinstance(head, str) or _SHA1.fullmatch(head) is None:
        raise ProgrammeAdmissionError("task_manifest_head_invalid")
    if base != policy.state["g0_1_correction"]["authorized_parent_commit"]:
        raise ProgrammeAdmissionError("task_manifest_base_stale")
    actual_head = _run_git(repo_root, "rev-parse", "HEAD")
    if head != actual_head:
        raise ProgrammeAdmissionError("task_manifest_head_stale")
    if manifest["state_digest"] != policy.state_digest:
        raise ProgrammeAdmissionError("task_manifest_state_digest_stale")
    if manifest["policy_digest"] != policy.policy_digest:
        raise ProgrammeAdmissionError("task_manifest_policy_digest_stale")
    paths = _unique_text_list(manifest["allowed_path_roots"], "task_manifest_paths_invalid")
    if not set(paths).issubset(policy.allowed_paths):
        raise ProgrammeAdmissionError("task_manifest_path_outside_policy")
    intended = set(_unique_text_list(manifest["intended_side_effect_classes"], "task_manifest_intended_effects_invalid"))
    forbidden = set(_unique_text_list(manifest["forbidden_side_effect_classes"], "task_manifest_forbidden_effects_invalid"))
    if not intended.issubset(ALLOWED_MAINTENANCE_EFFECTS) or intended & forbidden:
        raise ProgrammeAdmissionError("task_manifest_effects_not_admitted")
    if forbidden != FORBIDDEN_EFFECTS:
        raise ProgrammeAdmissionError("task_manifest_forbidden_effects_incomplete")
    return manifest, paths


def evaluate_programme_admission(
    *,
    repo_root: Path,
    manifest: object | None,
    entrypoint: str,
) -> ProgrammeDecision:
    """Return one structured, fail-closed decision for a gated entrypoint."""
    if entrypoint not in ENTRYPOINTS:
        return _decision(admitted=False, reasons=["entrypoint_unknown"], policy=None, task_class=None)
    try:
        policy = load_programme_policy(repo_root)
    except ProgrammeAdmissionError as error:
        return _decision(admitted=False, reasons=[error.reason_code], policy=None, task_class=None)
    if manifest is None:
        return _decision(admitted=False, reasons=["task_manifest_missing"], policy=policy, task_class=None)
    task_class = manifest.get("task_class") if isinstance(manifest, dict) and isinstance(manifest.get("task_class"), str) else None
    try:
        normalized, _ = _validate_manifest(manifest, policy=policy, repo_root=repo_root.resolve())
    except ProgrammeAdmissionError as error:
        return _decision(admitted=False, reasons=[error.reason_code], policy=policy, task_class=task_class)
    if entrypoint in ENTRYPOINTS_CLOSED_IN_G0:
        return _decision(admitted=False, reasons=[f"{entrypoint}_closed_in_g0"], policy=policy, task_class=normalized["task_class"])
    required_effect = ENTRYPOINT_REQUIRED_EFFECT[entrypoint]
    if required_effect not in normalized["intended_side_effect_classes"]:
        return _decision(admitted=False, reasons=["task_manifest_required_effect_missing"], policy=policy, task_class=normalized["task_class"])
    return _decision(admitted=True, reasons=[], policy=policy, task_class=normalized["task_class"])


def _changed_paths(root: Path, base: str) -> list[str]:
    committed = _run_git(root, "diff", "--name-only", f"{base}..HEAD").splitlines()
    working = _run_git(root, "diff", "--name-only").splitlines()
    staged = _run_git(root, "diff", "--cached", "--name-only").splitlines()
    return sorted({item.replace("\\", "/") for item in committed + working + staged if item})


def evaluate_committed_scope(
    *,
    repo_root: Path,
    manifest: object | None,
    phase: str,
) -> ScopeDecision:
    """Bind G0/G0.1 scope to the exact base..HEAD commit relation and origin."""
    if phase not in {"development", "pre-push", "post-push"}:
        return ScopeDecision(SCOPE_VERSION, False, ["scope_phase_invalid"], phase, None, None, None, None, None, [])
    admission = evaluate_programme_admission(repo_root=repo_root, manifest=manifest, entrypoint="recovery_preflight")
    if not admission.admitted:
        return ScopeDecision(SCOPE_VERSION, False, admission.reason_codes, phase, None, None, None, None, None, [])
    root = repo_root.resolve()
    policy = load_programme_policy(root)
    normalized, declared_paths = _validate_manifest(manifest, policy=policy, repo_root=root)
    scope = policy.overlay["scope_policy"]
    reasons: list[str] = []
    branch = _run_git(root, "branch", "--show-current")
    head = _run_git(root, "rev-parse", "HEAD")
    parent = scope["authorized_parent_commit"]
    if branch != scope["expected_branch"]:
        reasons.append("scope_branch_mismatch")
    if not _is_ancestor(root, scope["frozen_recovery_base"], head):
        reasons.append("scope_frozen_base_not_ancestor")
    if not _is_ancestor(root, parent, head):
        reasons.append("scope_authorized_parent_not_ancestor")
    try:
        commit_count = int(_run_git(root, "rev-list", "--count", f"{parent}..{head}"))
    except ValueError:
        commit_count = -1
        reasons.append("scope_commit_count_invalid")
    if phase == "development":
        if commit_count not in {0, 1}:
            reasons.append("scope_candidate_commit_count_invalid")
    elif commit_count != scope["candidate_commit_limit"]:
        reasons.append("scope_candidate_commit_count_invalid")
    changed = _changed_paths(root, scope["frozen_recovery_base"])
    if not set(changed).issubset(policy.allowed_paths):
        reasons.append("scope_path_outside_policy")
    if not set(changed).issubset(declared_paths):
        reasons.append("scope_path_outside_task_manifest")
    tracked_dirty = bool(_run_git(root, "status", "--porcelain", "--untracked-files=no"))
    if phase in {"pre-push", "post-push"} and tracked_dirty:
        reasons.append("scope_tracked_worktree_dirty")
    origin_head: str | None = None
    if phase == "pre-push":
        try:
            origin_head = _run_git(root, "rev-parse", f"origin/{branch}")
        except ProgrammeAdmissionError:
            reasons.append("scope_origin_branch_missing")
        if origin_head is not None and origin_head != parent:
            reasons.append("scope_origin_not_authorized_parent_pre_push")
    elif phase == "post-push":
        try:
            row = _run_git(root, "ls-remote", "--heads", "origin", f"refs/heads/{branch}")
        except ProgrammeAdmissionError:
            row = ""
        fields = row.split()
        if len(fields) != 2 or fields[1] != f"refs/heads/{branch}" or _SHA1.fullmatch(fields[0]) is None:
            reasons.append("scope_fresh_origin_observation_invalid")
        else:
            origin_head = fields[0]
            if origin_head != head:
                reasons.append("scope_origin_head_mismatch")
    if normalized["candidate_or_current_head"] != head:
        reasons.append("task_manifest_head_stale")
    return ScopeDecision(
        schema_version=SCOPE_VERSION,
        admitted=not reasons,
        reason_codes=list(dict.fromkeys(reasons)),
        phase=phase,
        branch=branch,
        head=head,
        origin_head=origin_head,
        authorized_parent_commit=parent,
        candidate_commit_count=commit_count,
        changed_paths=changed,
    )


def admission_payload(decision: ProgrammeDecision | ScopeDecision) -> dict[str, Any]:
    """Serialize a decision without turning it into an authority token."""
    return asdict(decision)


def require_programme_admission(
    *, repo_root: Path, manifest_path: Path | None, entrypoint: str
) -> ProgrammeDecision:
    """Load a manifest and raise before a gated executable side effect."""
    manifest = strict_json_object(manifest_path) if manifest_path is not None else None
    decision = evaluate_programme_admission(
        repo_root=repo_root, manifest=manifest, entrypoint=entrypoint
    )
    if not decision.admitted:
        reasons = ",".join(decision.reason_codes) or "programme_admission_denied"
        raise ProgrammeAdmissionError(reasons)
    return decision
