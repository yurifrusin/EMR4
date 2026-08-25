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
TRANSITION_MANIFEST_VERSION = "ariadne.programme_gate_transition_manifest.v1"
DECISION_VERSION = "ariadne.programme_admission_decision.v1"
SCOPE_VERSION = "ariadne.programme_scope_decision.v1"
ADMITTED_TASK_CLASS = "g0_2_controller_maintenance"
ADMITTED_PROGRAMME_GATE = "G0.2"
TRANSITION_TASK_CLASS = "g0_to_g1a_gate_transition"
TRANSITION_FROM_GATE = "G0"
TRANSITION_TO_GATE = "G1A"
TRANSITION_REVIEW_ROOT = "orchestration/programme/external-reviews"

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

TRANSITION_MANIFEST_KEYS = {
    "schema_version",
    "transition_id",
    "from_gate",
    "to_gate",
    "reviewed_commit",
    "reviewed_tree",
    "transition_parent",
    "external_review_verdict",
    "external_review_record_sha256",
    "blocking_finding_count",
    "reviewer_surface",
    "state_digest_before",
    "policy_digest_before",
    "allowed_transition_paths",
    "forbidden_effect_classes",
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
TRANSITION_FORBIDDEN_EFFECTS = {
    "dependency_change",
    "deployment",
    "implementation_change",
    "integration",
    "migration_change",
    "pages",
    "product_behavior_change",
    "protected_ref_movement",
    "provider_invocation",
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
    "tests/test_ariadne_antigravity.py",
    "tests/test_ariadne_deepseek_claude.py",
    "tests/test_ariadne_governance_clockwork_tick.py",
    "tests/test_ariadne_orchestrator_preflight.py",
    "tests/test_programme_admission.py",
    "tests/test_raisa_ariadne_recovery_preflight.py",
}
G0_G02_ALLOWED_PATHS = G0_G01_ALLOWED_PATHS
TRANSITION_FIXED_ALLOWED_PATHS = {
    "AGENTS.md",
    "orchestration/continuity/ariadne-active-operation-latch/current.json",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/gates.yaml",
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


def _run_git_bytes(root: Path, *args: str) -> bytes:
    """Run a read-only Git observation without losing NUL path delimiters."""
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProgrammeAdmissionError("git_observation_failed") from error
    if completed.returncode != 0:
        raise ProgrammeAdmissionError("git_observation_failed")
    return completed.stdout


@dataclass(frozen=True)
class GitPathChange:
    status: str
    path: str
    old_mode: str
    new_mode: str


_RAW_DIFF_HEADER = re.compile(
    rb"^:([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40,64}) ([0-9a-f]{40,64}) ([A-Z])$"
)


def _parse_raw_diff_z(payload: bytes) -> list[GitPathChange]:
    """Parse `git diff --raw -z --no-renames` as metadata/path pairs."""
    if not payload:
        return []
    fields = payload.split(b"\0")
    if fields[-1] != b"" or len(fields) % 2 != 1:
        raise ProgrammeAdmissionError("scope_raw_diff_invalid")
    changes: list[GitPathChange] = []
    for offset in range(0, len(fields) - 1, 2):
        header = fields[offset]
        raw_path = fields[offset + 1]
        matched = _RAW_DIFF_HEADER.fullmatch(header)
        if matched is None or not raw_path:
            raise ProgrammeAdmissionError("scope_raw_diff_invalid")
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ProgrammeAdmissionError("scope_path_encoding_invalid") from error
        path = path.replace("\\", "/")
        pure = PurePosixPath(path)
        if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
            raise ProgrammeAdmissionError("scope_path_invalid")
        changes.append(
            GitPathChange(
                status=matched.group(5).decode("ascii"),
                path=path,
                old_mode=matched.group(1).decode("ascii"),
                new_mode=matched.group(2).decode("ascii"),
            )
        )
    return changes


def git_change_inventory(root: Path, *diff_arguments: str) -> list[GitPathChange]:
    """Return a rename-disabled, mode-aware, NUL-delimited Git inventory."""
    return _parse_raw_diff_z(
        _run_git_bytes(
            root,
            "diff",
            "--raw",
            "-z",
            "--no-renames",
            "--abbrev=40",
            *diff_arguments,
        )
    )


def _change_inventory_reasons(changes: Sequence[GitPathChange]) -> list[str]:
    reasons: list[str] = []
    for change in changes:
        if change.status not in {"A", "M", "D"}:
            reasons.append("scope_change_status_forbidden")
        modes = {change.old_mode, change.new_mode} - {"000000"}
        if modes & {"120000"}:
            reasons.append("scope_symlink_mode_forbidden")
        if modes & {"160000"}:
            reasons.append("scope_gitlink_mode_forbidden")
        if any(mode not in {"100644", "100755"} for mode in modes):
            reasons.append("scope_file_type_forbidden")
        if (
            change.old_mode != "000000"
            and change.new_mode != "000000"
            and change.old_mode[:3] != change.new_mode[:3]
        ):
            reasons.append("scope_type_change_forbidden")
        if change.status == "M" and change.old_mode != change.new_mode:
            reasons.append("scope_mode_change_forbidden")
        if change.status == "A" and change.new_mode != "100644":
            reasons.append("scope_added_mode_forbidden")
        if change.status == "D" and change.new_mode != "000000":
            reasons.append("scope_deleted_mode_invalid")
    return list(dict.fromkeys(reasons))


def _git_object_bytes(root: Path, object_spec: str) -> bytes:
    return _run_git_bytes(root, "show", object_spec)


def _digest_paths_at(root: Path, commit: str, paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for relative in paths:
        payload = _git_object_bytes(root, f"{commit}:{relative.as_posix()}")
        label = relative.as_posix().encode("utf-8")
        digest.update(len(label).to_bytes(4, "big"))
        digest.update(label)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return "sha256:" + digest.hexdigest()


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
            "active_correction",
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
            "g0_2_correction",
            "gate_transition",
        },
        "programme_state_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.programme-state.v1"
        or value["programme_mode"] != "recovery"
        or value["machine_authoritative"] is not True
        or value["feature_work_eligible"] is not False
    ):
        raise ProgrammeAdmissionError("programme_state_not_fail_closed")

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
    _bounded_text(selection["admission_command"], "admission_command_invalid", 500)
    phase = value["active_correction"]
    if phase not in {ADMITTED_PROGRAMME_GATE, "gate_transition"}:
        raise ProgrammeAdmissionError("programme_phase_invalid")
    expected_task_class = (
        ADMITTED_TASK_CLASS if phase == ADMITTED_PROGRAMME_GATE else TRANSITION_TASK_CLASS
    )
    expected_gate = "G0" if phase == ADMITTED_PROGRAMME_GATE else TRANSITION_TO_GATE
    expected_status = "revision_required" if phase == ADMITTED_PROGRAMME_GATE else "gate_transition"
    if (
        selection["autonomous_selection_enabled"] is not False
        or selection["allowed_task_kinds"] != [expected_task_class]
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
        or selection["next_eligible_tranche"]
        != (ADMITTED_PROGRAMME_GATE if phase == ADMITTED_PROGRAMME_GATE else TRANSITION_TO_GATE)
        or selection["next_eligible_now"] is not True
        or selection["next_tranche_started"] is not (phase == ADMITTED_PROGRAMME_GATE)
        or selection["next_tranche_admission_requires_state_transition"]
        is not (phase == ADMITTED_PROGRAMME_GATE)
        or value["current_gate"] != expected_gate
        or value["current_gate_status"] != expected_status
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
        or correction["external_review_status"]
        not in {"not_started", "pending", "revision_required"}
        or correction["g1a_authorized"] is not False
    ):
        raise ProgrammeAdmissionError("g0_1_correction_not_fail_closed")

    correction_g02 = _exact_keys(
        value["g0_2_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_1_tree",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_2_correction_schema_invalid",
    )
    for field in ("authorized_parent_commit", "reviewed_g0_1_tree"):
        if not isinstance(correction_g02[field], str) or _SHA1.fullmatch(
            correction_g02[field]
        ) is None:
            raise ProgrammeAdmissionError("g0_2_correction_binding_invalid")
    if correction_g02["candidate_commit_limit"] != 1:
        raise ProgrammeAdmissionError("g0_2_correction_limit_invalid")
    if phase == ADMITTED_PROGRAMME_GATE:
        if (
            correction_g02["status"] not in {"in_progress", "review_pending"}
            or correction_g02["external_review_status"]
            not in {"not_started", "pending"}
            or correction_g02["g1a_authorized"] is not False
            or value["gate_transition"] is not None
        ):
            raise ProgrammeAdmissionError("g0_2_correction_not_fail_closed")
    else:
        if (
            correction_g02["status"] != "external_review_passed"
            or correction_g02["external_review_status"] != "pass"
            or correction_g02["g1a_authorized"] is not True
        ):
            raise ProgrammeAdmissionError("g0_2_transition_history_invalid")
        transition = _exact_keys(
            value["gate_transition"],
            {
                "status",
                "transition_id",
                "from_gate",
                "to_gate",
                "reviewed_commit",
                "reviewed_tree",
                "external_review_status",
                "blocking_finding_count",
                "reviewer_surface",
                "g1a_authorized",
                "next_action",
            },
            "gate_transition_state_schema_invalid",
        )
        if (
            transition["status"] != "gate_transition"
            or transition["from_gate"] != TRANSITION_FROM_GATE
            or transition["to_gate"] != TRANSITION_TO_GATE
            or transition["external_review_status"] != "pass"
            or transition["blocking_finding_count"] != 0
            or transition["g1a_authorized"] is not True
        ):
            raise ProgrammeAdmissionError("gate_transition_state_invalid")
        if _IDENTIFIER.fullmatch(
            _bounded_text(transition["transition_id"], "transition_id_invalid", 128)
        ) is None:
            raise ProgrammeAdmissionError("transition_id_invalid")
        _bounded_text(transition["reviewer_surface"], "reviewer_surface_invalid", 256)
        for field in ("reviewed_commit", "reviewed_tree"):
            if not isinstance(transition[field], str) or _SHA1.fullmatch(
                transition[field]
            ) is None:
                raise ProgrammeAdmissionError("gate_transition_binding_invalid")

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
        or programme["next_eligible_tranche"]
        != (
            ADMITTED_PROGRAMME_GATE
            if state["active_correction"] == ADMITTED_PROGRAMME_GATE
            else TRANSITION_TO_GATE
        )
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
    if state["active_correction"] == ADMITTED_PROGRAMME_GATE:
        current_statuses = {
            "G0": "revision_required_g0_2",
            "G0.1": "superseded_revision_required",
            "G0.2": state["g0_2_correction"]["status"],
            "G1A": "blocked_by_external_G0_review",
        }
    else:
        current_statuses = {
            "G0": "passed",
            "G0.1": "superseded_revision_required",
            "G0.2": "external_review_passed",
            "G1A": "gate_transition_open",
        }
    expected_statuses = {
        **current_statuses,
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
    if state["active_correction"] == ADMITTED_PROGRAMME_GATE:
        if by_id.get("G1A", {}).get("status") != "blocked_by_external_G0_review":
            raise ProgrammeAdmissionError("g1a_not_closed")
    elif by_id.get("G1A", {}).get("status") != "gate_transition_open":
        raise ProgrammeAdmissionError("g1a_transition_not_open")


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
        or value["current_gate"] != "G0"
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
            "scope_policy", "transition_policy", "gated_entrypoints", "missing_or_invalid_state", "reversibility",
        },
        "recovery_overlay_schema_invalid",
    )
    if (
        value["schema_version"] != "ariadne.programme_recovery.v3"
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
    phase = state["active_correction"]
    expected_task_class = (
        ADMITTED_TASK_CLASS if phase == ADMITTED_PROGRAMME_GATE else TRANSITION_TASK_CLASS
    )
    if (
        recovery["expected_programme_mode"] != state["programme_mode"]
        or recovery["expected_current_gate"] != state["current_gate"]
        or recovery["expected_gate_status"] != state["current_gate_status"]
        or recovery["active_correction"] != phase
        or recovery["autonomous_task_selection"] is not False
        or recovery["admitted_task_classes"] != [expected_task_class]
        or any(recovery[key] is not False for key in ("feature_work_eligible", "provider_calls_eligible", "deployment_eligible", "protected_ref_movement_eligible"))
        or recovery["g1a_eligible"] is not (phase == "gate_transition")
    ):
        raise ProgrammeAdmissionError("recovery_mode_not_fail_closed")
    scope = _exact_keys(
        value["scope_policy"],
        {"expected_branch", "frozen_recovery_base", "authorized_parent_commit", "candidate_commit_limit", "allowed_paths"},
        "scope_policy_schema_invalid",
    )
    expected_parent = (
        state["g0_2_correction"]["authorized_parent_commit"]
        if phase == ADMITTED_PROGRAMME_GATE
        else state["gate_transition"]["reviewed_commit"]
    )
    if (
        scope["expected_branch"] != state["recovery_baton"]["branch"]
        or scope["frozen_recovery_base"] != state["recovery_baton"]["base_sha"]
        or scope["authorized_parent_commit"] != expected_parent
        or scope["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("scope_policy_state_disagreement")
    allowed_paths = _unique_text_list(scope["allowed_paths"], "scope_allowed_paths_invalid")
    if phase == ADMITTED_PROGRAMME_GATE:
        if set(allowed_paths) != G0_G02_ALLOWED_PATHS:
            raise ProgrammeAdmissionError("scope_allowed_paths_not_exact")
    else:
        review_path = (
            f"{TRANSITION_REVIEW_ROOT}/{state['gate_transition']['transition_id']}.json"
        )
        if set(allowed_paths) != TRANSITION_FIXED_ALLOWED_PATHS | {review_path}:
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
        if entrypoint_path not in G0_G02_ALLOWED_PATHS or not (
            root / entrypoint_path
        ).is_file():
            raise ProgrammeAdmissionError("gated_entrypoint_path_invalid")
    if observed != ENTRYPOINTS:
        raise ProgrammeAdmissionError("recovery_entrypoint_coverage_incomplete")

    transition = _exact_keys(
        value["transition_policy"],
        {
            "manifest_schema_version",
            "task_class",
            "from_gate",
            "to_gate",
            "transition_status",
            "external_review_record_root",
            "candidate_commit_limit",
            "fixed_allowed_paths",
            "forbidden_effect_classes",
        },
        "transition_policy_schema_invalid",
    )
    if (
        transition["manifest_schema_version"] != TRANSITION_MANIFEST_VERSION
        or transition["task_class"] != TRANSITION_TASK_CLASS
        or transition["from_gate"] != TRANSITION_FROM_GATE
        or transition["to_gate"] != TRANSITION_TO_GATE
        or transition["transition_status"] != "gate_transition"
        or transition["external_review_record_root"] != TRANSITION_REVIEW_ROOT
        or transition["candidate_commit_limit"] != 1
        or set(
            _unique_text_list(
                transition["fixed_allowed_paths"],
                "transition_fixed_paths_invalid",
            )
        )
        != TRANSITION_FIXED_ALLOWED_PATHS
        or set(
            _unique_text_list(
                transition["forbidden_effect_classes"],
                "transition_forbidden_effects_invalid",
            )
        )
        != TRANSITION_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("transition_policy_invalid")
    return allowed_paths


def _validate_precedence(
    project: dict[str, Any],
    continuation: dict[str, Any],
    agents_text: str,
    state: dict[str, Any],
) -> None:
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
    phase_token = (
        "Gate G0.2 is the only authorised correction; G1A is"
        if state["active_correction"] == ADMITTED_PROGRAMME_GATE
        else "The reviewed state-only G0 to G1A transition is complete; Gate G1A is"
    )
    required_header = (
        "# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE",
        phase_token,
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
    full_range_allowed_paths: tuple[str, ...]


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
    _validate_precedence(project, continuation, agents_text, state)
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
        full_range_allowed_paths=tuple(
            allowed_paths
            if state["active_correction"] == ADMITTED_PROGRAMME_GATE
            else sorted(G0_G02_ALLOWED_PATHS | set(allowed_paths))
        ),
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
    if base != policy.state["g0_2_correction"]["authorized_parent_commit"]:
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


def _validate_transition_manifest(
    value: object, *, policy: ProgrammePolicy
) -> tuple[dict[str, Any], list[str]]:
    manifest = _exact_keys(
        value, TRANSITION_MANIFEST_KEYS, "transition_manifest_schema_invalid"
    )
    if manifest["schema_version"] != TRANSITION_MANIFEST_VERSION:
        raise ProgrammeAdmissionError("transition_manifest_version_invalid")
    transition_id = _bounded_text(
        manifest["transition_id"], "transition_id_invalid", 128
    )
    if _IDENTIFIER.fullmatch(transition_id) is None:
        raise ProgrammeAdmissionError("transition_id_invalid")
    if (
        manifest["from_gate"] != TRANSITION_FROM_GATE
        or manifest["to_gate"] != TRANSITION_TO_GATE
    ):
        raise ProgrammeAdmissionError("transition_gate_invalid")
    for field in ("reviewed_commit", "reviewed_tree", "transition_parent"):
        if not isinstance(manifest[field], str) or _SHA1.fullmatch(manifest[field]) is None:
            raise ProgrammeAdmissionError("transition_git_binding_invalid")
    if manifest["transition_parent"] != manifest["reviewed_commit"]:
        raise ProgrammeAdmissionError("transition_parent_invalid")
    if manifest["external_review_verdict"] != "PASS":
        raise ProgrammeAdmissionError("transition_review_verdict_not_pass")
    if (
        isinstance(manifest["blocking_finding_count"], bool)
        or manifest["blocking_finding_count"] != 0
    ):
        raise ProgrammeAdmissionError("transition_blocking_findings_present")
    _bounded_text(manifest["reviewer_surface"], "reviewer_surface_invalid", 256)
    for field in (
        "external_review_record_sha256",
        "state_digest_before",
        "policy_digest_before",
    ):
        if not isinstance(manifest[field], str) or _SHA256.fullmatch(manifest[field]) is None:
            raise ProgrammeAdmissionError(f"transition_{field}_invalid")
    review_path = f"{TRANSITION_REVIEW_ROOT}/{transition_id}.json"
    allowed_paths = _unique_text_list(
        manifest["allowed_transition_paths"], "transition_allowed_paths_invalid"
    )
    expected_paths = TRANSITION_FIXED_ALLOWED_PATHS | {review_path}
    if set(allowed_paths) != expected_paths or set(allowed_paths) != set(
        policy.allowed_paths
    ):
        raise ProgrammeAdmissionError("transition_allowed_paths_not_exact")
    if set(
        _unique_text_list(
            manifest["forbidden_effect_classes"],
            "transition_forbidden_effects_invalid",
        )
    ) != TRANSITION_FORBIDDEN_EFFECTS:
        raise ProgrammeAdmissionError("transition_forbidden_effects_incomplete")
    if policy.state["active_correction"] != "gate_transition":
        raise ProgrammeAdmissionError("transition_phase_not_active")
    state_transition = policy.state["gate_transition"]
    if (
        state_transition["transition_id"] != transition_id
        or state_transition["from_gate"] != manifest["from_gate"]
        or state_transition["to_gate"] != manifest["to_gate"]
        or state_transition["reviewed_commit"] != manifest["reviewed_commit"]
        or state_transition["reviewed_tree"] != manifest["reviewed_tree"]
        or state_transition["blocking_finding_count"]
        != manifest["blocking_finding_count"]
        or state_transition["reviewer_surface"] != manifest["reviewer_surface"]
        or state_transition["g1a_authorized"] is not True
    ):
        raise ProgrammeAdmissionError("transition_manifest_state_disagreement")
    return manifest, allowed_paths


def _manifest_task_class(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    if value.get("schema_version") == TRANSITION_MANIFEST_VERSION:
        return TRANSITION_TASK_CLASS
    task_class = value.get("task_class")
    return task_class if isinstance(task_class, str) else None


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
    task_class = _manifest_task_class(manifest)
    try:
        if isinstance(manifest, dict) and manifest.get("schema_version") == TRANSITION_MANIFEST_VERSION:
            normalized, _ = _validate_transition_manifest(manifest, policy=policy)
            normalized_task_class = TRANSITION_TASK_CLASS
        else:
            normalized, _ = _validate_manifest(
                manifest, policy=policy, repo_root=repo_root.resolve()
            )
            normalized_task_class = normalized["task_class"]
    except ProgrammeAdmissionError as error:
        return _decision(admitted=False, reasons=[error.reason_code], policy=policy, task_class=task_class)
    if entrypoint in ENTRYPOINTS_CLOSED_IN_G0:
        return _decision(admitted=False, reasons=[f"{entrypoint}_closed_in_g0"], policy=policy, task_class=normalized_task_class)
    if normalized_task_class != TRANSITION_TASK_CLASS:
        required_effect = ENTRYPOINT_REQUIRED_EFFECT[entrypoint]
        if required_effect not in normalized["intended_side_effect_classes"]:
            return _decision(admitted=False, reasons=["task_manifest_required_effect_missing"], policy=policy, task_class=normalized_task_class)
    return _decision(admitted=True, reasons=[], policy=policy, task_class=normalized_task_class)


def _scope_change_inventories(
    root: Path, *, frozen_base: str, tranche_base: str
) -> tuple[list[GitPathChange], list[GitPathChange]]:
    working = git_change_inventory(root)
    staged = git_change_inventory(root, "--cached")
    full = [
        *git_change_inventory(root, f"{frozen_base}..HEAD"),
        *working,
        *staged,
    ]
    tranche = [
        *git_change_inventory(root, f"{tranche_base}..HEAD"),
        *working,
        *staged,
    ]
    return full, tranche


def _strict_json_payload(payload: bytes, reason: str) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_json
        )
    except ProgrammeAdmissionError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProgrammeAdmissionError(reason) from error
    if not isinstance(value, dict):
        raise ProgrammeAdmissionError(reason)
    return value


def _strict_yaml_payload(payload: bytes, reason: str) -> dict[str, Any]:
    try:
        value = yaml.load(payload.decode("utf-8"), Loader=_UniqueKeyLoader)
    except ProgrammeAdmissionError:
        raise
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise ProgrammeAdmissionError(reason) from error
    if not isinstance(value, dict):
        raise ProgrammeAdmissionError(reason)
    return value


def _fresh_origin_head(root: Path, branch: str) -> str | None:
    try:
        row = _run_git(
            root, "ls-remote", "--heads", "origin", f"refs/heads/{branch}"
        )
    except ProgrammeAdmissionError:
        return None
    fields = row.split()
    if (
        len(fields) != 2
        or fields[1] != f"refs/heads/{branch}"
        or _SHA1.fullmatch(fields[0]) is None
    ):
        return None
    return fields[0]


def _transition_scope_reasons(
    *,
    root: Path,
    policy: ProgrammePolicy,
    manifest: dict[str, Any],
    phase: str,
    branch: str,
    head: str,
    commit_count: int,
    tranche_changes: Sequence[GitPathChange],
) -> tuple[list[str], str | None]:
    reasons: list[str] = []
    reviewed = manifest["reviewed_commit"]
    if manifest["transition_parent"] != reviewed:
        reasons.append("transition_parent_invalid")
    try:
        reviewed_tree = _run_git(root, "rev-parse", f"{reviewed}^{{tree}}")
    except ProgrammeAdmissionError:
        reviewed_tree = ""
    if reviewed_tree != manifest["reviewed_tree"]:
        reasons.append("transition_reviewed_tree_mismatch")
    if head == reviewed:
        if phase != "development" or commit_count != 0:
            reasons.append("transition_commit_missing")
    else:
        try:
            parent_row = _run_git(root, "rev-list", "--parents", "-n", "1", head)
        except ProgrammeAdmissionError:
            parent_row = ""
        parents = parent_row.split()
        if commit_count != 1 or len(parents) != 2 or parents[1] != reviewed:
            reasons.append("transition_exact_parent_required")

    before_state_payload = _git_object_bytes(
        root, f"{reviewed}:{STATE_PATH.as_posix()}"
    )
    if _sha256_bytes(before_state_payload) != manifest["state_digest_before"]:
        reasons.append("transition_state_digest_before_mismatch")
    policy_paths = (
        GATES_PATH,
        RISK_PATH,
        INVENTORY_PATH,
        OVERLAY_PATH,
        PROJECT_PATH,
        CONTINUATION_PATH,
        LATCH_PATH,
        AGENTS_PATH,
    )
    if _digest_paths_at(root, reviewed, policy_paths) != manifest["policy_digest_before"]:
        reasons.append("transition_policy_digest_before_mismatch")
    prior_state = _strict_json_payload(
        before_state_payload, "transition_prior_state_invalid"
    )
    prior_g02 = prior_state.get("g0_2_correction")
    if (
        prior_state.get("programme_mode") != "recovery"
        or prior_state.get("current_gate") != TRANSITION_FROM_GATE
        or prior_state.get("current_gate_status") != "revision_required"
        or prior_state.get("active_correction") != ADMITTED_PROGRAMME_GATE
        or not isinstance(prior_g02, dict)
        or prior_g02.get("status") != "review_pending"
        or prior_g02.get("g1a_authorized") is not False
        or prior_state.get("gate_transition") is not None
    ):
        reasons.append("transition_g1a_not_previously_closed")
    prior_gates = _strict_yaml_payload(
        _git_object_bytes(root, f"{reviewed}:{GATES_PATH.as_posix()}"),
        "transition_prior_gates_invalid",
    )
    prior_gate_rows = {
        row.get("id"): row
        for row in prior_gates.get("gates", [])
        if isinstance(row, dict)
    }
    if prior_gate_rows.get(TRANSITION_TO_GATE, {}).get("status") != (
        "blocked_by_external_G0_review"
    ):
        reasons.append("transition_g1a_not_previously_closed")

    review_path = f"{TRANSITION_REVIEW_ROOT}/{manifest['transition_id']}.json"
    record_entries = [row for row in tranche_changes if row.path == review_path]
    if len(record_entries) != 1 or record_entries[0].status != "A":
        reasons.append("transition_review_record_not_immutable_addition")
    try:
        review_payload = (root / review_path).read_bytes()
    except OSError:
        review_payload = b""
        reasons.append("transition_review_record_missing")
    if _sha256_bytes(review_payload) != manifest["external_review_record_sha256"]:
        reasons.append("transition_review_record_digest_mismatch")
    if review_payload:
        record = _strict_json_payload(
            review_payload, "transition_review_record_invalid"
        )
        expected_record_keys = {
            "schema_version",
            "review_id",
            "recorded_at",
            "reviewed_commit",
            "reviewed_tree",
            "verdict",
            "blocking_finding_count",
            "reviewer_surface",
        }
        if set(record) != expected_record_keys:
            reasons.append("transition_review_record_schema_invalid")
        elif (
            record["schema_version"] != "raisa-ariadne.external-g0-review.v1"
            or record["review_id"] != manifest["transition_id"]
            or record["reviewed_commit"] != reviewed
            or record["reviewed_tree"] != manifest["reviewed_tree"]
            or record["verdict"] != manifest["external_review_verdict"]
            or record["blocking_finding_count"]
            != manifest["blocking_finding_count"]
            or record["reviewer_surface"] != manifest["reviewer_surface"]
        ):
            reasons.append("transition_review_record_binding_mismatch")

    changed_paths = {row.path for row in tranche_changes}
    required_paths = {
        AGENTS_PATH.as_posix(),
        STATE_PATH.as_posix(),
        GATES_PATH.as_posix(),
        OVERLAY_PATH.as_posix(),
        review_path,
    }
    if not required_paths.issubset(changed_paths):
        reasons.append("transition_required_state_paths_missing")
    if any(path.endswith(".py") for path in changed_paths):
        reasons.append("transition_python_implementation_forbidden")

    expected_protected = policy.state["protected_refs"]["expected_sha"]
    try:
        protected_ok = all(
            _run_git(root, "rev-parse", ref) == expected_protected
            for ref in policy.state["protected_refs"]["refs"]
        )
    except ProgrammeAdmissionError:
        protected_ok = False
    if not protected_ok:
        reasons.append("transition_protected_refs_changed")

    origin_head = _fresh_origin_head(root, branch)
    expected_origin = head if phase == "post-push" else reviewed
    if origin_head is None:
        reasons.append("scope_fresh_origin_observation_invalid")
    elif origin_head != expected_origin:
        reasons.append(
            "scope_origin_head_mismatch"
            if phase == "post-push"
            else "transition_origin_not_reviewed_candidate"
        )
    return list(dict.fromkeys(reasons)), origin_head


def evaluate_committed_scope(
    *,
    repo_root: Path,
    manifest: object | None,
    phase: str,
) -> ScopeDecision:
    """Bind correction/transition scope with rename-safe path and mode evidence."""
    if phase not in {"development", "pre-push", "post-push"}:
        return ScopeDecision(SCOPE_VERSION, False, ["scope_phase_invalid"], phase, None, None, None, None, None, [])
    admission = evaluate_programme_admission(repo_root=repo_root, manifest=manifest, entrypoint="recovery_preflight")
    if not admission.admitted:
        return ScopeDecision(SCOPE_VERSION, False, admission.reason_codes, phase, None, None, None, None, None, [])
    root = repo_root.resolve()
    policy = load_programme_policy(root)
    is_transition = (
        isinstance(manifest, dict)
        and manifest.get("schema_version") == TRANSITION_MANIFEST_VERSION
    )
    if is_transition:
        normalized, declared_paths = _validate_transition_manifest(
            manifest, policy=policy
        )
    else:
        normalized, declared_paths = _validate_manifest(
            manifest, policy=policy, repo_root=root
        )
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
    full_changes, tranche_changes = _scope_change_inventories(
        root,
        frozen_base=scope["frozen_recovery_base"],
        tranche_base=parent,
    )
    changed = sorted({item.path for item in full_changes})
    tranche_changed = sorted({item.path for item in tranche_changes})
    reasons.extend(_change_inventory_reasons(full_changes))
    reasons.extend(_change_inventory_reasons(tranche_changes))
    if not set(changed).issubset(policy.full_range_allowed_paths):
        reasons.append("scope_path_outside_policy")
    if not is_transition and not set(changed).issubset(declared_paths):
        reasons.append("scope_path_outside_task_manifest")
    if not set(tranche_changed).issubset(policy.allowed_paths):
        reasons.append("scope_tranche_path_outside_policy")
    if not set(tranche_changed).issubset(declared_paths):
        reasons.append("scope_tranche_path_outside_task_manifest")
    tracked_dirty = bool(_run_git(root, "status", "--porcelain", "--untracked-files=no"))
    if phase in {"pre-push", "post-push"} and tracked_dirty:
        reasons.append("scope_tracked_worktree_dirty")
    origin_head: str | None = None
    if is_transition:
        transition_reasons, origin_head = _transition_scope_reasons(
            root=root,
            policy=policy,
            manifest=normalized,
            phase=phase,
            branch=branch,
            head=head,
            commit_count=commit_count,
            tranche_changes=tranche_changes,
        )
        reasons.extend(transition_reasons)
    elif phase == "pre-push":
        try:
            origin_head = _run_git(root, "rev-parse", f"origin/{branch}")
        except ProgrammeAdmissionError:
            reasons.append("scope_origin_branch_missing")
        if origin_head is not None and origin_head != parent:
            reasons.append("scope_origin_not_authorized_parent_pre_push")
    elif phase == "post-push":
        origin_head = _fresh_origin_head(root, branch)
        if origin_head is None:
            reasons.append("scope_fresh_origin_observation_invalid")
        elif origin_head != head:
            reasons.append("scope_origin_head_mismatch")
    if not is_transition and normalized["candidate_or_current_head"] != head:
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
