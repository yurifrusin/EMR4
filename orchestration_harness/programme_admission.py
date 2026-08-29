"""Fail-closed programme admission for the EMR4 recovery controller.

This module is deliberately project-neutral at the admission boundary: callers
provide a typed task manifest and an entrypoint class.  The repository policy
files decide whether that task may execute.  Receipts remain evidence and are
never themselves admission tokens.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import stat
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence
from urllib.parse import urlsplit

import yaml

from orchestration_harness import trusted_git

STATE_PATH = Path("orchestration/programme/current-state.json")
GATES_PATH = Path("orchestration/programme/gates.yaml")
RISK_PATH = Path("orchestration/programme/risk-register.yaml")
INVENTORY_PATH = Path("orchestration/programme/branch-pr-disposition.yaml")
G1A_SCOPE_PATH = Path("orchestration/programme/g1a-verdict-integration-scope.yaml")
OVERLAY_PATH = Path("orchestration/harness_settings/programme_recovery.yaml")
PROJECT_PATH = Path("orchestration/harness_settings/project.yaml")
CONTINUATION_PATH = Path("orchestration/harness_settings/autonomous_continuation.yaml")
LATCH_PATH = Path(
    "orchestration/continuity/ariadne-active-operation-latch/current.json"
)
AGENTS_PATH = Path("AGENTS.md")
AUTHORITY_FIXED_PATHS = (
    STATE_PATH,
    GATES_PATH,
    RISK_PATH,
    INVENTORY_PATH,
    G1A_SCOPE_PATH,
    OVERLAY_PATH,
    PROJECT_PATH,
    CONTINUATION_PATH,
    LATCH_PATH,
    AGENTS_PATH,
)
AUTHORITY_INDEX_ROOTS = (
    Path("orchestration/harness_settings"),
    Path("orchestration/programme/reviews"),
    Path("orchestration/programme/external-reviews"),
    Path("orchestration/programme/gate-transitions"),
    Path("orchestration/programme/owner-dispositions"),
    Path("orchestration/programme/subgate-reviews"),
    Path("orchestration/programme/subgate-implementation-reviews"),
    Path("orchestration/programme/subgate-transition-enablement-reviews"),
    Path("orchestration/programme/subgate-transitions"),
)

TASK_MANIFEST_VERSION = "ariadne.programme_task_manifest.v1"
TRANSITION_MANIFEST_VERSION = "ariadne.programme_gate_transition_manifest.v1"
SUBGATE_TRANSITION_MANIFEST_VERSION = "ariadne.programme_subgate_transition_manifest.v1"
G1A3_TRANSITION_MANIFEST_VERSION = (
    "ariadne.programme_g1a2_to_g1a3_transition_manifest.v1"
)
DECISION_VERSION = "ariadne.programme_admission_decision.v1"
SCOPE_VERSION = "ariadne.programme_scope_decision.v1"
ADMITTED_TASK_CLASS = "g0_8_fsmonitor_closure"
ADMITTED_PROGRAMME_GATE = "G0.8"
TRANSITION_TASK_CLASS = "g0_to_g1a_state_transition"
SUBGATE_TRANSITION_TASK_CLASS = "g1a_1_to_g1a_2_state_transition"
G1A3_TRANSITION_TASK_CLASS = "g1a_2_to_g1a_3_state_transition"
G1A_TASK_CLASS = "g1a_1_verdict_kernel_and_pure_consumers"
G1A2_TASK_CLASS = "g1a_2_antigravity_verdict_adapter"
G1A3_TASK_CLASS = "g1a_3_integration_consumer_mutation"
G0_CONTROLLER_PROFILE = "G0.8_FSMONITOR_CLOSURE"
TRANSITION_PROFILE = "G0_TO_G1A_STATE_TRANSITION"
G1A_ACTIVE_PROFILE = "G1A.1_ACTIVE"
SUBGATE_TRANSITION_PROFILE = "G1A.1_TO_G1A.2_STATE_TRANSITION"
G1A2_ACTIVE_PROFILE = "G1A.2_ACTIVE"
G1A3_ENABLEMENT_PENDING_PROFILE = "G1A.3-E0_REVIEW_PENDING"
G1A3_TRANSITION_PROFILE = "G1A.2_TO_G1A.3_STATE_TRANSITION"
G1A3_ACTIVE_PROFILE = "G1A.3_ACTIVE"
G1A3_RUNTIME_SOURCE_PARSING_CONTRACT = (
    "python_compile_original_bytes_PyCF_ONLY_AST_PyCF_TYPE_COMMENTS_dont_inherit"
)
TRANSITION_FROM_GATE = "G0"
TRANSITION_TO_GATE = "G1A.1"
SUBGATE_TRANSITION_FROM_GATE = "G1A.1"
SUBGATE_TRANSITION_TO_GATE = "G1A.2"
G1A3_TRANSITION_FROM_GATE = "G1A.2"
G1A3_TRANSITION_TO_GATE = "G1A.3"
TRANSITION_REVIEW_ROOT = "orchestration/programme/external-reviews"
TRANSITION_ARTIFACT_ROOT = "orchestration/programme/gate-transitions"
RETAINED_REVIEW_ROOT = "orchestration/programme/reviews"
OWNER_DISPOSITION_ROOT = "orchestration/programme/owner-dispositions"
SUBGATE_REVIEW_ROOT = "orchestration/programme/subgate-reviews"
SUBGATE_IMPLEMENTATION_REVIEW_ROOT = (
    "orchestration/programme/subgate-implementation-reviews"
)
G1A3_TRANSITION_REVIEW_ROOT = (
    "orchestration/programme/subgate-transition-enablement-reviews"
)
SUBGATE_TRANSITION_ARTIFACT_ROOT = "orchestration/programme/subgate-transitions"
OWNER_DISPOSITION_ID = "g1a1-owner-accept-91f1e6e-20260828"
OWNER_DISPOSITION_PATH = f"{OWNER_DISPOSITION_ROOT}/{OWNER_DISPOSITION_ID}.json"

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

SUBGATE_TRANSITION_MANIFEST_KEYS = {
    "schema_version",
    "transition_id",
    "from_gate",
    "to_gate",
    "owner_disposition_id",
    "owner_disposition_record_sha256",
    "enablement_controller_commit",
    "enablement_controller_tree",
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

G1A3_TRANSITION_MANIFEST_KEYS = {
    "schema_version",
    "transition_id",
    "from_gate",
    "to_gate",
    "g1a2_implementation_review_id",
    "g1a2_implementation_review_record_sha256",
    "g1a2_implementation_commit",
    "g1a2_implementation_tree",
    "enablement_review_id",
    "enablement_controller_commit",
    "enablement_controller_tree",
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
    "g1b_work",
    "provider_invocation",
    "product_behavior_change",
    "dependency_change",
    "migration_change",
    "integration",
    "protected_ref_movement",
    "deployment",
    "pages",
    "real_data_access",
}
TRANSITION_FORBIDDEN_EFFECTS = {
    "dependency_change",
    "deployment",
    "g1b_work",
    "implementation_change",
    "integration",
    "migration_change",
    "pages",
    "product_behavior_change",
    "protected_ref_movement",
    "provider_invocation",
    "real_data_access",
}
G1A_FORBIDDEN_EFFECTS = {
    "autonomous_worker_dispatch",
    "closeout_state_transition",
    "controller_policy_change",
    "dependency_change",
    "deployment",
    "gatekeeper_change",
    "g1b_work",
    "integration",
    "migration_change",
    "pages",
    "product_behavior_change",
    "protected_ref_movement",
    "provider_invocation",
    "real_data_access",
    "programme_state_change",
}
ALLOWED_MAINTENANCE_EFFECTS = {
    "repository_read",
    "control_plane_edit",
    "task_branch_commit",
    "task_branch_push",
}
G1A_ALLOWED_EFFECTS = {
    "repository_read",
    "verdict_kernel_edit",
    "task_branch_commit",
    "task_branch_push",
    "external_review_preparation",
}
G1A2_ALLOWED_EFFECTS = {
    "repository_read",
    "provider_verdict_adapter_edit",
    "task_branch_commit",
    "task_branch_push",
    "external_review_preparation",
}
G1A3_ALLOWED_EFFECTS = {
    "repository_read",
    "integration_authority_adapter_edit",
    "task_branch_commit",
    "task_branch_push",
    "external_review_preparation",
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
G0_G03_ALLOWED_PATHS = G0_G02_ALLOWED_PATHS | {
    G1A_SCOPE_PATH.as_posix(),
    "orchestration_harness/deepcode_artifact.py",
    "orchestration_harness/review_acceptance.py",
    "scripts/ariadne_deepcode_liveness.py",
    "scripts/ariadne_review_acceptance.py",
    "tests/test_ariadne_deepcode_runtime_observability.py",
    "tests/test_ariadne_review_acceptance.py",
}
G0_G04_ALLOWED_PATHS = G0_G03_ALLOWED_PATHS | {
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
    "scripts/raisa_ariadne_pinned_gatekeeper.py",
    "tests/test_programme_pinned_gatekeeper.py",
}
G0_RETAINED_REVIEW_PATHS = {
    f"{RETAINED_REVIEW_ROOT}/g0-review-c720aaa-revision-required.json",
    f"{RETAINED_REVIEW_ROOT}/g0-review-087522d-revision-required.json",
    f"{RETAINED_REVIEW_ROOT}/g0-review-7cae4e8-revision-required.json",
    f"{RETAINED_REVIEW_ROOT}/g0-review-2af9278-revision-required.json",
    f"{RETAINED_REVIEW_ROOT}/g0-review-4ce1719-revision-required.json",
    f"{RETAINED_REVIEW_ROOT}/g0-review-71e2c5f-revision-required.json",
}
G0_G06_ALLOWED_PATHS = G0_G04_ALLOWED_PATHS | G0_RETAINED_REVIEW_PATHS
G0_G07_REVIEW_PATH = (
    f"{RETAINED_REVIEW_ROOT}/"
    "g0-review-4a8e71c-independent-20260826-revision-required.json"
)
G0_G07_ALLOWED_PATHS = G0_G06_ALLOWED_PATHS | {
    G0_G07_REVIEW_PATH,
    "orchestration_harness/trusted_git.py",
}
G0_G08_REVIEW_PATH = (
    f"{RETAINED_REVIEW_ROOT}/"
    "g0-review-6e101d1-independent-20260827-revision-required.json"
)
G0_G08_ALLOWED_PATHS = G0_G07_ALLOWED_PATHS | {G0_G08_REVIEW_PATH}
# Compatibility alias for historical tests and transition fixtures.
G0_G05_ALLOWED_PATHS = G0_G06_ALLOWED_PATHS
G1A_ALLOWED_PATHS = {
    "orchestration_harness/verdict.py",
    "orchestration_harness/deepcode_artifact.py",
    "orchestration_harness/review_acceptance.py",
    "scripts/ariadne_deepcode_liveness.py",
    "scripts/ariadne_review_acceptance.py",
    "tests/test_ariadne_deepcode_runtime_observability.py",
    "tests/test_ariadne_review_acceptance.py",
    "tests/test_ariadne_verdict.py",
}
G1A_ALLOWED_UNTRACKED_PATHS = {
    "orchestration_harness/verdict.py",
    "tests/test_ariadne_verdict.py",
}
G1A2_ALLOWED_PATHS = {
    "scripts/ariadne_antigravity.py",
    "tests/test_ariadne_antigravity.py",
}
G1A3_ALLOWED_PATHS = {
    "scripts/agent_worktrees.py",
    "tests/test_agent_worktrees.py",
}
TRANSITION_FIXED_ALLOWED_PATHS = {
    "AGENTS.md",
    "orchestration/continuity/ariadne-active-operation-latch/current.json",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/gates.yaml",
}
SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS = {
    "AGENTS.md",
    "orchestration/continuity/ariadne-active-operation-latch/current.json",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/gates.yaml",
}
G1A3_TRANSITION_FIXED_ALLOWED_PATHS = SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS
G1A2_ENABLEMENT_ALLOWED_PATHS = {
    "AGENTS.md",
    "orchestration/continuity/ariadne-active-operation-latch/current.json",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/g1a-verdict-integration-scope.yaml",
    "orchestration/programme/gates.yaml",
    OWNER_DISPOSITION_PATH,
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_recovery_preflight.py",
    "tests/test_programme_admission.py",
    "tests/test_programme_pinned_gatekeeper.py",
    "tests/test_raisa_ariadne_recovery_preflight.py",
}
G1A2_IMPLEMENTATION_REVIEW_PATH = (
    f"{SUBGATE_IMPLEMENTATION_REVIEW_ROOT}/"
    "g1a2-review-37e2d6f-independent-20260828-pass.json"
)
G1A3_ENABLEMENT_ALLOWED_PATHS = {
    "AGENTS.md",
    "docs/programme/raisa-ariadne-recovery-programme.md",
    "orchestration/continuity/ariadne-active-operation-latch/current.json",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/g1a-verdict-integration-scope.yaml",
    "orchestration/programme/gates.yaml",
    G1A2_IMPLEMENTATION_REVIEW_PATH,
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_recovery_preflight.py",
    "tests/test_programme_admission.py",
    "tests/test_programme_pinned_gatekeeper.py",
    "tests/test_raisa_ariadne_recovery_preflight.py",
}
ACCEPTED_CUMULATIVE_HISTORY_PATHS = {"scripts/ariadne_deepcode_notify.sh"}
ACCEPTED_CUMULATIVE_MODE_CHANGES = {
    ("M", "scripts/ariadne_deepcode_notify.sh", "100755", "100644")
}

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_ISO8601_WITH_TIMEZONE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


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


def _timestamp_with_timezone(value: object, reason: str) -> str:
    timestamp = _bounded_text(value, reason, 64)
    if _ISO8601_WITH_TIMEZONE.fullmatch(timestamp) is None:
        raise ProgrammeAdmissionError(reason)
    return timestamp


def _bool(value: object, expected: bool, reason: str) -> None:
    if value is not expected:
        raise ProgrammeAdmissionError(reason)


def _unique_text_list(
    value: object, reason: str, *, minimum: int = 1, maximum: int = 256
) -> list[str]:
    if (
        not isinstance(value, list)
        or not minimum <= len(value) <= maximum
        or any(
            not isinstance(item, str) or not item or item != item.strip()
            for item in value
        )
        or len(set(value)) != len(value)
    ):
        raise ProgrammeAdmissionError(reason)
    return list(value)


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise ProgrammeAdmissionError("preservation_artifact_unavailable") from error
    return digest.hexdigest()


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
        return trusted_git.run_git(root, *args)
    except trusted_git.TrustedGitError as error:
        if error.reason_code.startswith("trusted_git_"):
            raise ProgrammeAdmissionError(error.reason_code) from error
        raise ProgrammeAdmissionError("git_observation_failed") from error


def _run_git_bytes(root: Path, *args: str) -> bytes:
    """Run a read-only Git observation without losing NUL path delimiters."""
    try:
        return trusted_git.run_git_bytes(root, *args)
    except trusted_git.TrustedGitError as error:
        if error.reason_code.startswith("trusted_git_"):
            raise ProgrammeAdmissionError(error.reason_code) from error
        raise ProgrammeAdmissionError("git_observation_failed") from error


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


def _nul_git_paths(payload: bytes, reason: str) -> list[str]:
    if not payload:
        return []
    fields = payload.split(b"\0")
    if fields[-1] != b"":
        raise ProgrammeAdmissionError(reason)
    paths: list[str] = []
    for raw_path in fields[:-1]:
        if not raw_path:
            raise ProgrammeAdmissionError(reason)
        try:
            path = raw_path.decode("utf-8").replace("\\", "/")
        except UnicodeDecodeError as error:
            raise ProgrammeAdmissionError("scope_path_encoding_invalid") from error
        pure = PurePosixPath(path)
        if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
            raise ProgrammeAdmissionError("scope_path_invalid")
        paths.append(path)
    return paths


def _path_alias_key(path: str) -> str:
    return unicodedata.normalize("NFC", path).casefold()


def _validate_regular_path_components(root: Path, path: str) -> None:
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    candidate = root
    final_stat = None
    for component in PurePosixPath(path).parts:
        candidate = candidate / component
        try:
            observed = candidate.lstat()
        except OSError as error:
            raise ProgrammeAdmissionError(
                "scope_filesystem_observation_failed"
            ) from error
        if candidate.is_symlink() or (
            getattr(observed, "st_file_attributes", 0) & reparse_flag
        ):
            raise ProgrammeAdmissionError("scope_untracked_reparse_forbidden")
        final_stat = observed
    if final_stat is None or not stat.S_ISREG(final_stat.st_mode):
        raise ProgrammeAdmissionError("scope_untracked_nonregular_forbidden")


def git_all_file_inventory(root: Path) -> list[GitPathChange]:
    """Return every non-tracked file, including ignored files, with NUL safety."""
    ordinary = _nul_git_paths(
        _run_git_bytes(root, "ls-files", "--others", "--exclude-standard", "-z"),
        "scope_untracked_inventory_invalid",
    )
    ignored = _nul_git_paths(
        _run_git_bytes(
            root,
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "-z",
        ),
        "scope_ignored_inventory_invalid",
    )
    classified = {path: "?" for path in ordinary}
    for path in ignored:
        if path in classified:
            raise ProgrammeAdmissionError("scope_filesystem_inventory_overlap")
        classified[path] = "!"
    tracked = set(
        _nul_git_paths(
            _run_git_bytes(root, "ls-files", "--cached", "-z"),
            "scope_tracked_inventory_invalid",
        )
    )
    protected_aliases: dict[str, str] = {}
    for path in sorted(tracked | G1A_ALLOWED_UNTRACKED_PATHS):
        alias = _path_alias_key(path)
        prior = protected_aliases.setdefault(alias, path)
        if prior != path:
            raise ProgrammeAdmissionError("scope_protected_path_alias_collision")
    observed_aliases: dict[str, str] = {}
    changes: list[GitPathChange] = []
    for path, status_code in sorted(classified.items()):
        alias = _path_alias_key(path)
        if alias in protected_aliases and protected_aliases[alias] != path:
            raise ProgrammeAdmissionError("scope_protected_path_alias_forbidden")
        prior = observed_aliases.setdefault(alias, path)
        if prior != path:
            raise ProgrammeAdmissionError("scope_filesystem_path_alias_forbidden")
        _validate_regular_path_components(root, path)
        changes.append(
            GitPathChange(
                status=status_code,
                path=path,
                old_mode="000000",
                new_mode="100644",
            )
        )
    return changes


def git_untracked_inventory(root: Path) -> list[GitPathChange]:
    """Compatibility name for the complete untracked-and-ignored inventory."""
    return git_all_file_inventory(root)


_REMOTE_POLICY_KEYS = {
    "schema_version",
    "mode",
    "remote_name",
    "normalized_fetch_url",
    "normalized_push_url",
    "fetch_url_count",
    "push_url_count",
    "explicit_push_url_count",
    "expected_repository_identity",
    "normalization_policy",
    "url_rewrite_policy",
    "url_rewrite_count",
    "remote_identity_sha256",
}
_PRODUCTION_REMOTE_NORMALIZATION = "https_github_owner_repository_lowercase_strip_terminal_dot_git_no_query_fragment_or_userinfo"
_SYNTHETIC_REMOTE_NORMALIZATION = "absolute_local_bare_path_as_posix"
_REMOTE_REWRITE_POLICY = "reject_all_insteadOf_and_pushInsteadOf"


def _canonical_object_digest(payload: dict[str, Any], digest_key: str) -> str:
    bound = {key: value for key, value in payload.items() if key != digest_key}
    return _sha256_bytes(
        json.dumps(bound, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _remote_identity_digest(payload: dict[str, Any]) -> str:
    return _canonical_object_digest(payload, "remote_identity_sha256")


def _git_config_values(root: Path, key: str) -> list[str]:
    try:
        returncode, stdout = trusted_git.run_git_optional_bytes(
            root, "config", "--null", "--get-all", key
        )
    except trusted_git.TrustedGitError as error:
        raise ProgrammeAdmissionError("remote_identity_observation_failed") from error
    if returncode not in {0, 1}:
        raise ProgrammeAdmissionError("remote_identity_observation_failed")
    if returncode == 1:
        return []
    try:
        values = stdout.decode("utf-8").split("\0")
    except UnicodeDecodeError as error:
        raise ProgrammeAdmissionError("remote_identity_encoding_invalid") from error
    if values[-1] != "":
        raise ProgrammeAdmissionError("remote_identity_observation_invalid")
    result = values[:-1]
    if any(not value or "\r" in value or "\n" in value for value in result):
        raise ProgrammeAdmissionError("remote_identity_observation_invalid")
    return result


def _url_rewrite_count(root: Path) -> int:
    try:
        returncode, stdout = trusted_git.run_git_optional_bytes(
            root,
            "config",
            "--null",
            "--get-regexp",
            r"^url\..*\.(insteadOf|pushInsteadOf)$",
        )
    except trusted_git.TrustedGitError as error:
        raise ProgrammeAdmissionError("remote_identity_observation_failed") from error
    if returncode not in {0, 1}:
        raise ProgrammeAdmissionError("remote_identity_observation_failed")
    if returncode == 1:
        return 0
    return stdout.count(b"\0")


def _normalize_production_remote_url(raw: str) -> tuple[str, str]:
    parsed = urlsplit(raw)
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or parsed.hostname.casefold() != "github.com"
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ProgrammeAdmissionError("remote_identity_url_not_closed_https_github")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ProgrammeAdmissionError("remote_identity_repository_path_invalid")
    owner, repository = parts
    if repository.casefold().endswith(".git"):
        repository = repository[:-4]
    if (
        not owner
        or not repository
        or any(part in {".", ".."} for part in (owner, repository))
    ):
        raise ProgrammeAdmissionError("remote_identity_repository_path_invalid")
    identity = f"github.com/{owner.casefold()}/{repository.casefold()}"
    return f"https://{identity}", identity


def _normalize_synthetic_remote_url(raw: str) -> tuple[str, str]:
    candidate = Path(raw)
    if not candidate.is_absolute() or raw.startswith("-") or "://" in raw:
        raise ProgrammeAdmissionError("remote_identity_synthetic_path_invalid")
    normalized = candidate.resolve().as_posix()
    return normalized, f"local-bare:{normalized}"


def build_synthetic_remote_identity_policy(remote_path: Path) -> dict[str, Any]:
    """Build a closed test-only identity policy for one exact local bare repository."""
    normalized, identity = _normalize_synthetic_remote_url(str(remote_path))
    payload: dict[str, Any] = {
        "schema_version": "ariadne.remote_identity_policy.v1",
        "mode": "synthetic_bound_local_bare",
        "remote_name": "origin",
        "normalized_fetch_url": normalized,
        "normalized_push_url": normalized,
        "fetch_url_count": 1,
        "push_url_count": 1,
        "explicit_push_url_count": 0,
        "expected_repository_identity": identity,
        "normalization_policy": _SYNTHETIC_REMOTE_NORMALIZATION,
        "url_rewrite_policy": _REMOTE_REWRITE_POLICY,
        "url_rewrite_count": 0,
        "remote_identity_sha256": "",
    }
    payload["remote_identity_sha256"] = _remote_identity_digest(payload)
    return payload


def _validate_remote_identity_policy(value: object) -> dict[str, Any]:
    policy = _exact_keys(
        value, _REMOTE_POLICY_KEYS, "remote_identity_policy_schema_invalid"
    )
    if (
        policy["schema_version"] != "ariadne.remote_identity_policy.v1"
        or policy["remote_name"] != "origin"
        or policy["fetch_url_count"] != 1
        or policy["push_url_count"] != 1
        or policy["explicit_push_url_count"] != 0
        or policy["url_rewrite_policy"] != _REMOTE_REWRITE_POLICY
        or policy["url_rewrite_count"] != 0
        or policy["remote_identity_sha256"] != _remote_identity_digest(policy)
    ):
        raise ProgrammeAdmissionError("remote_identity_policy_invalid")
    if policy["mode"] == "production":
        expected = {
            "normalized_fetch_url": "https://github.com/yurifrusin/emr4",
            "normalized_push_url": "https://github.com/yurifrusin/emr4",
            "expected_repository_identity": "github.com/yurifrusin/emr4",
            "normalization_policy": _PRODUCTION_REMOTE_NORMALIZATION,
        }
        if any(policy[key] != value for key, value in expected.items()):
            raise ProgrammeAdmissionError("production_remote_identity_policy_not_exact")
    elif policy["mode"] == "synthetic_bound_local_bare":
        normalized, identity = _normalize_synthetic_remote_url(
            policy["normalized_fetch_url"]
        )
        if (
            policy["normalized_fetch_url"] != normalized
            or policy["normalized_push_url"] != normalized
            or policy["expected_repository_identity"] != identity
            or policy["normalization_policy"] != _SYNTHETIC_REMOTE_NORMALIZATION
        ):
            raise ProgrammeAdmissionError("synthetic_remote_identity_policy_not_exact")
    else:
        raise ProgrammeAdmissionError("remote_identity_policy_mode_invalid")
    return policy


def observe_remote_identity(root: Path, policy_value: object) -> dict[str, Any]:
    """Observe and bind one exact fetch/push destination without symbolic remote trust."""
    policy = _validate_remote_identity_policy(policy_value)
    fetch_urls = _git_config_values(root, "remote.origin.url")
    explicit_push_urls = _git_config_values(root, "remote.origin.pushurl")
    effective_push_urls = explicit_push_urls or fetch_urls
    if len(fetch_urls) != 1 or len(effective_push_urls) != 1:
        raise ProgrammeAdmissionError("remote_identity_url_count_invalid")
    if explicit_push_urls:
        raise ProgrammeAdmissionError("remote_identity_explicit_pushurl_forbidden")
    rewrite_count = _url_rewrite_count(root)
    if rewrite_count:
        raise ProgrammeAdmissionError("remote_identity_url_rewrite_forbidden")
    normalizer = (
        _normalize_production_remote_url
        if policy["mode"] == "production"
        else _normalize_synthetic_remote_url
    )
    fetch_url, fetch_identity = normalizer(fetch_urls[0])
    push_url, push_identity = normalizer(effective_push_urls[0])
    observed = {
        **policy,
        "normalized_fetch_url": fetch_url,
        "normalized_push_url": push_url,
        "fetch_url_count": len(fetch_urls),
        "push_url_count": len(effective_push_urls),
        "explicit_push_url_count": len(explicit_push_urls),
        "expected_repository_identity": fetch_identity,
        "url_rewrite_count": rewrite_count,
        "remote_identity_sha256": "",
    }
    if fetch_identity != push_identity:
        raise ProgrammeAdmissionError("remote_identity_fetch_push_disagree")
    observed["remote_identity_sha256"] = _remote_identity_digest(observed)
    if observed != policy:
        raise ProgrammeAdmissionError("remote_identity_policy_mismatch")
    return observed


def observe_git_administrative_identity(root: Path) -> dict[str, Any]:
    """Model the execution-relevant Git administration while rejecting client hooks."""
    if _git_config_values(root, "core.hooksPath"):
        raise ProgrammeAdmissionError("git_administrative_hooks_path_forbidden")
    try:
        common_dir = Path(
            _run_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
        )
        hooks_dir = common_dir / "hooks"
        hook_entries = sorted(hooks_dir.iterdir()) if hooks_dir.is_dir() else []
    except OSError as error:
        raise ProgrammeAdmissionError(
            "git_administrative_observation_failed"
        ) from error
    non_sample_hooks = [
        entry.name for entry in hook_entries if not entry.name.endswith(".sample")
    ]
    if non_sample_hooks:
        raise ProgrammeAdmissionError("git_administrative_client_hook_forbidden")
    payload: dict[str, Any] = {
        "schema_version": "ariadne.git_administrative_identity.v1",
        "administrative_entry": ".git",
        "head_index_objects_and_refs_bound_by_git_operations": True,
        "info_excludes_neutralized_by_complete_inventory": True,
        "core_hooks_path_count": 0,
        "non_sample_client_hook_count": 0,
        "git_administrative_identity_sha256": "",
    }
    payload["git_administrative_identity_sha256"] = _canonical_object_digest(
        payload, "git_administrative_identity_sha256"
    )
    return payload


def _change_inventory_reasons(
    changes: Sequence[GitPathChange], *, cumulative_history: bool = False
) -> list[str]:
    reasons: list[str] = []
    for change in changes:
        row = (change.status, change.path, change.old_mode, change.new_mode)
        if cumulative_history and row in ACCEPTED_CUMULATIVE_MODE_CHANGES:
            continue
        if change.status not in {"A", "M", "D", "?", "!"}:
            reasons.append("scope_change_status_forbidden")
        if PurePosixPath(change.path).name in {
            "sitecustomize.py",
            "usercustomize.py",
        } or change.path.endswith(".pth"):
            reasons.append("scope_import_hook_forbidden")
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
        if change.status in {"A", "?", "!"} and change.new_mode != "100644":
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
        returncode, _stdout = trusted_git.run_git_optional_bytes(
            root, "merge-base", "--is-ancestor", ancestor, descendant
        )
    except trusted_git.TrustedGitError as error:
        raise ProgrammeAdmissionError("git_observation_failed") from error
    if returncode not in {0, 1}:
        raise ProgrammeAdmissionError("git_observation_failed")
    return returncode == 0


def _validate_commit_tree_binding(
    root: Path, *, commit: object, tree: object, reason: str
) -> None:
    if (
        not isinstance(commit, str)
        or _SHA1.fullmatch(commit) is None
        or not isinstance(tree, str)
        or _SHA1.fullmatch(tree) is None
    ):
        raise ProgrammeAdmissionError(reason)
    try:
        actual_tree = _run_git(root, "rev-parse", f"{commit}^{{tree}}")
        resolved_tree = _run_git(root, "rev-parse", f"{tree}^{{tree}}")
    except ProgrammeAdmissionError as error:
        raise ProgrammeAdmissionError(reason) from error
    if actual_tree != tree or resolved_tree != tree:
        raise ProgrammeAdmissionError(reason)


_REVIEW_HISTORY_ENTRY_KEYS = {
    "review_id",
    "review_record_path",
    "reviewed_commit",
    "reviewed_tree",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a_authorized",
    "review_record_sha256",
}
_REVIEW_RECORD_KEYS = {
    "schema_version",
    "review_id",
    "recorded_at",
    "reviewed_commit",
    "reviewed_tree",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a_authorized",
    "source_artifact_sha256",
}

_OWNER_DISPOSITION_RECORD_KEYS = {
    "schema_version",
    "disposition_id",
    "recorded_at",
    "owner",
    "programme_gate",
    "subject_commit",
    "subject_tree",
    "decision",
    "residual_risks",
    "g1a2_transition_enablement_authorized",
    "g1a2_state_transition_authorized",
    "g1a2_implementation_authorized",
    "provider_invocation_authorized",
    "integration_authorized",
}
_OWNER_DISPOSITION_HISTORY_KEYS = {
    "disposition_id",
    "record_path",
    "programme_gate",
    "subject_commit",
    "subject_tree",
    "decision",
    "residual_risk_count",
    "record_sha256",
}
_RESIDUAL_RISK_KEYS = {
    "id",
    "classification",
    "description",
    "accepted_for_progression",
    "must_be_reconsidered_before",
}
_SUBGATE_REVIEW_HISTORY_KEYS = {
    "review_id",
    "review_record_path",
    "reviewed_commit",
    "reviewed_tree",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a2_state_transition_authorized",
    "g1a2_implementation_authorized",
    "provider_invocation_authorized",
    "review_record_sha256",
}
_SUBGATE_REVIEW_RECORD_KEYS = {
    "schema_version",
    "review_id",
    "recorded_at",
    "review_subject",
    "reviewed_commit",
    "reviewed_tree",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a2_state_transition_authorized",
    "g1a2_implementation_authorized",
    "provider_invocation_authorized",
    "source_artifact_sha256",
}
_IMPLEMENTATION_REVIEW_HISTORY_KEYS = {
    "review_id",
    "review_record_path",
    "reviewed_commit",
    "reviewed_tree",
    "reviewed_parent",
    "review_subject",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a3_transition_enablement_authorized",
    "provider_invocation_authorized",
    "integration_authorized",
    "review_record_sha256",
}
_IMPLEMENTATION_REVIEW_RECORD_KEYS = {
    "schema_version",
    "review_id",
    "recorded_at",
    "review_subject",
    "reviewed_commit",
    "reviewed_tree",
    "reviewed_parent",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a3_transition_enablement_authorized",
    "provider_invocation_authorized",
    "integration_authorized",
    "only_next_work",
    "source_artifact_sha256",
}
_G1A3_REVIEW_HISTORY_KEYS = {
    "review_id",
    "review_record_path",
    "reviewed_commit",
    "reviewed_tree",
    "reviewed_parent",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a3_state_transition_authorized",
    "g1a3_implementation_authorized",
    "provider_invocation_authorized",
    "integration_authorized",
    "review_record_sha256",
}
_G1A3_REVIEW_RECORD_KEYS = {
    "schema_version",
    "review_id",
    "recorded_at",
    "review_subject",
    "reviewed_commit",
    "reviewed_tree",
    "reviewed_parent",
    "verdict",
    "blocking_finding_count",
    "reviewer_surface",
    "g1a3_state_transition_authorized",
    "g1a3_implementation_authorized",
    "provider_invocation_authorized",
    "integration_authorized",
    "source_artifact_sha256",
}


def _validate_sole_parent(root: Path, commit: str, parent: str, reason: str) -> None:
    try:
        row = _run_git(root, "rev-list", "--parents", "-n", "1", commit).split()
    except ProgrammeAdmissionError as error:
        raise ProgrammeAdmissionError(reason) from error
    if len(row) != 2 or row != [commit, parent]:
        raise ProgrammeAdmissionError(reason)


def _validate_g1a2_implementation_review(
    authority: dict[str, Any], root: Path
) -> dict[str, Any]:
    history = authority["implementation_review_history"]
    decisive_id = authority["decisive_implementation_review_id"]
    if not isinstance(history, list) or len(history) != 1:
        raise ProgrammeAdmissionError("g1a2_implementation_review_history_invalid")
    entry = _exact_keys(
        history[0],
        _IMPLEMENTATION_REVIEW_HISTORY_KEYS,
        "g1a2_implementation_review_history_entry_invalid",
    )
    review_id = _bounded_text(entry["review_id"], "g1a2_review_id_invalid", 128)
    expected_path = f"{SUBGATE_IMPLEMENTATION_REVIEW_ROOT}/{review_id}.json"
    if (
        review_id != "g1a2-review-37e2d6f-independent-20260828-pass"
        or decisive_id != review_id
        or entry["review_record_path"] != expected_path
        or entry["reviewed_commit"] != "37e2d6f51ebbdb281771f922a5f460fd23e2571b"
        or entry["reviewed_tree"] != "798a2eda11438fe05da2528298006775774ccfc4"
        or entry["reviewed_parent"] != "474d79e0ef918dc8e7fef6780ea34c5c105fe236"
        or entry["review_subject"] != "G1A.2_antigravity_verdict_adapter"
        or entry["verdict"] != "PASS"
        or entry["blocking_finding_count"] != 0
        or entry["reviewer_surface"] != "external_chatgpt_repository_review"
        or entry["g1a3_transition_enablement_authorized"] is not True
        or entry["provider_invocation_authorized"] is not False
        or entry["integration_authorized"] is not False
        or entry["review_record_sha256"]
        != "sha256:bd29a64c591e0cddd9cc47cc2ae4408f63c36acc3e663bd431bc369ee7385fcb"
    ):
        raise ProgrammeAdmissionError("g1a2_implementation_review_binding_invalid")
    try:
        payload = (root / expected_path).read_bytes()
    except OSError as error:
        raise ProgrammeAdmissionError("g1a2_implementation_review_missing") from error
    if _sha256_bytes(payload) != entry["review_record_sha256"]:
        raise ProgrammeAdmissionError("g1a2_implementation_review_digest_mismatch")
    record = _strict_json_payload(payload, "g1a2_implementation_review_invalid")
    _exact_keys(
        record,
        _IMPLEMENTATION_REVIEW_RECORD_KEYS,
        "g1a2_implementation_review_schema_invalid",
    )
    if (
        record["schema_version"] != "ariadne.external_subgate_implementation_review.v1"
        or any(
            record[field] != entry[field]
            for field in (
                "review_id",
                "review_subject",
                "reviewed_commit",
                "reviewed_tree",
                "reviewed_parent",
                "verdict",
                "blocking_finding_count",
                "reviewer_surface",
                "g1a3_transition_enablement_authorized",
                "provider_invocation_authorized",
                "integration_authorized",
            )
        )
        or record["only_next_work"] != "bounded_G1A3_transition_enablement"
        or record["source_artifact_sha256"]
        != "f037d535c952ae19a9e485342e660a1e62a9a5cc1e3bb8f076d00b787cba8337"
    ):
        raise ProgrammeAdmissionError("g1a2_implementation_review_record_invalid")
    _timestamp_with_timezone(
        record["recorded_at"], "g1a2_implementation_review_recorded_at_invalid"
    )
    _validate_commit_tree_binding(
        root,
        commit=record["reviewed_commit"],
        tree=record["reviewed_tree"],
        reason="g1a2_implementation_review_commit_tree_binding_invalid",
    )
    _validate_sole_parent(
        root,
        record["reviewed_commit"],
        record["reviewed_parent"],
        "g1a2_implementation_review_parent_binding_invalid",
    )
    return entry


def _validate_g1a3_enablement_reviews(
    authority: dict[str, Any], root: Path
) -> dict[str, Any] | None:
    history = authority["g1a3_transition_enablement_review_history"]
    decisive_id = authority["decisive_g1a3_transition_enablement_review_id"]
    if not isinstance(history, list) or len(history) > 1:
        raise ProgrammeAdmissionError("g1a3_enablement_review_history_invalid")
    if not history:
        if decisive_id is not None:
            raise ProgrammeAdmissionError("g1a3_decisive_review_invalid")
        return None
    entry = _exact_keys(
        history[0],
        _G1A3_REVIEW_HISTORY_KEYS,
        "g1a3_enablement_review_history_entry_invalid",
    )
    review_id = _bounded_text(entry["review_id"], "g1a3_review_id_invalid", 128)
    expected_path = f"{G1A3_TRANSITION_REVIEW_ROOT}/{review_id}.json"
    if (
        _IDENTIFIER.fullmatch(review_id) is None
        or decisive_id != review_id
        or entry["review_record_path"] != expected_path
        or entry["verdict"] != "PASS"
        or entry["blocking_finding_count"] != 0
        or entry["g1a3_state_transition_authorized"] is not True
        or entry["g1a3_implementation_authorized"] is not False
        or entry["provider_invocation_authorized"] is not False
        or entry["integration_authorized"] is not False
        or not isinstance(entry["review_record_sha256"], str)
        or _SHA256.fullmatch(entry["review_record_sha256"]) is None
    ):
        raise ProgrammeAdmissionError("g1a3_enablement_review_binding_invalid")
    try:
        payload = (root / expected_path).read_bytes()
    except OSError as error:
        raise ProgrammeAdmissionError("g1a3_enablement_review_missing") from error
    if _sha256_bytes(payload) != entry["review_record_sha256"]:
        raise ProgrammeAdmissionError("g1a3_enablement_review_digest_mismatch")
    record = _strict_json_payload(payload, "g1a3_enablement_review_invalid")
    _exact_keys(
        record,
        _G1A3_REVIEW_RECORD_KEYS,
        "g1a3_enablement_review_schema_invalid",
    )
    if (
        record["schema_version"]
        != "ariadne.external_g1a3_transition_enablement_review.v1"
        or record["review_subject"] != "G1A.3_transition_enablement"
        or any(
            record[field] != entry[field]
            for field in _G1A3_REVIEW_HISTORY_KEYS
            if field not in {"review_record_path", "review_record_sha256"}
        )
        or not isinstance(record["source_artifact_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", record["source_artifact_sha256"]) is None
    ):
        raise ProgrammeAdmissionError("g1a3_enablement_review_record_invalid")
    _timestamp_with_timezone(
        record["recorded_at"], "g1a3_enablement_review_recorded_at_invalid"
    )
    _validate_commit_tree_binding(
        root,
        commit=record["reviewed_commit"],
        tree=record["reviewed_tree"],
        reason="g1a3_enablement_review_commit_tree_binding_invalid",
    )
    _validate_sole_parent(
        root,
        record["reviewed_commit"],
        record["reviewed_parent"],
        "g1a3_enablement_review_parent_binding_invalid",
    )
    return entry


def _validate_g1a_subgate_authority(value: object, root: Path) -> dict[str, Any]:
    authority = _exact_keys(
        value,
        {
            "schema_version",
            "owner_disposition_record_root",
            "external_subgate_review_record_root",
            "implementation_review_record_root",
            "g1a3_transition_enablement_review_record_root",
            "subgate_transition_artifact_root",
            "decisive_owner_disposition_id",
            "decisive_transition_enablement_review_id",
            "decisive_implementation_review_id",
            "decisive_g1a3_transition_enablement_review_id",
            "owner_disposition_history",
            "external_review_history",
            "implementation_review_history",
            "g1a3_transition_enablement_review_history",
            "subgates",
        },
        "g1a_subgate_authority_schema_invalid",
    )
    if (
        authority["schema_version"] != "ariadne.g1a_subgate_authority.v2"
        or authority["owner_disposition_record_root"] != OWNER_DISPOSITION_ROOT
        or authority["external_subgate_review_record_root"] != SUBGATE_REVIEW_ROOT
        or authority["implementation_review_record_root"]
        != SUBGATE_IMPLEMENTATION_REVIEW_ROOT
        or authority["g1a3_transition_enablement_review_record_root"]
        != G1A3_TRANSITION_REVIEW_ROOT
        or authority["subgate_transition_artifact_root"]
        != SUBGATE_TRANSITION_ARTIFACT_ROOT
        or authority["decisive_owner_disposition_id"] != OWNER_DISPOSITION_ID
    ):
        raise ProgrammeAdmissionError("g1a_subgate_authority_header_invalid")

    _validate_g1a2_implementation_review(authority, root)
    _validate_g1a3_enablement_reviews(authority, root)

    history = authority["owner_disposition_history"]
    if not isinstance(history, list) or len(history) != 1:
        raise ProgrammeAdmissionError("owner_disposition_history_invalid")
    entry = _exact_keys(
        history[0],
        _OWNER_DISPOSITION_HISTORY_KEYS,
        "owner_disposition_history_entry_invalid",
    )
    if (
        entry["disposition_id"] != OWNER_DISPOSITION_ID
        or entry["record_path"] != OWNER_DISPOSITION_PATH
        or entry["programme_gate"] != "G1A.1"
        or entry["subject_commit"] != "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b"
        or entry["subject_tree"] != "24b92d586061901e7574d511105b21ea66d97f7e"
        or entry["decision"] != "ACCEPT_WITH_RESIDUAL_RISK"
        or entry["residual_risk_count"] != 1
        or not isinstance(entry["record_sha256"], str)
        or _SHA256.fullmatch(entry["record_sha256"]) is None
    ):
        raise ProgrammeAdmissionError("owner_disposition_history_binding_invalid")
    disposition_path = root / OWNER_DISPOSITION_PATH
    try:
        disposition_payload = disposition_path.read_bytes()
    except OSError as error:
        raise ProgrammeAdmissionError("owner_disposition_record_missing") from error
    if _sha256_bytes(disposition_payload) != entry["record_sha256"]:
        raise ProgrammeAdmissionError("owner_disposition_record_digest_mismatch")
    disposition = _strict_json_payload(
        disposition_payload, "owner_disposition_record_invalid"
    )
    _exact_keys(
        disposition,
        _OWNER_DISPOSITION_RECORD_KEYS,
        "owner_disposition_record_schema_invalid",
    )
    risks = disposition["residual_risks"]
    if not isinstance(risks, list) or len(risks) != 1:
        raise ProgrammeAdmissionError("owner_disposition_residual_risks_invalid")
    risk = _exact_keys(
        risks[0], _RESIDUAL_RISK_KEYS, "owner_disposition_residual_risk_invalid"
    )
    if (
        disposition["schema_version"] != "ariadne.owner_subgate_disposition.v1"
        or disposition["disposition_id"] != entry["disposition_id"]
        or disposition["owner"] != "Yuri Frusin"
        or disposition["programme_gate"] != entry["programme_gate"]
        or disposition["subject_commit"] != entry["subject_commit"]
        or disposition["subject_tree"] != entry["subject_tree"]
        or disposition["decision"] != entry["decision"]
        or risk
        != {
            "id": "G1A1-PARSER-MIXED-TAB-001",
            "classification": "parser_robustness_backlog",
            "description": "Mixed space-plus-tab indentation remains an unclosed free-form source-text marker edge case.",
            "accepted_for_progression": True,
            "must_be_reconsidered_before": "future high-trust free-form text integration authority",
        }
        or disposition["g1a2_transition_enablement_authorized"] is not True
        or disposition["g1a2_state_transition_authorized"] is not False
        or disposition["g1a2_implementation_authorized"] is not False
        or disposition["provider_invocation_authorized"] is not False
        or disposition["integration_authorized"] is not False
    ):
        raise ProgrammeAdmissionError("owner_disposition_record_semantics_invalid")
    _timestamp_with_timezone(
        disposition["recorded_at"], "owner_disposition_recorded_at_invalid"
    )
    _validate_commit_tree_binding(
        root,
        commit=disposition["subject_commit"],
        tree=disposition["subject_tree"],
        reason="owner_disposition_commit_tree_binding_invalid",
    )

    reviews = authority["external_review_history"]
    if not isinstance(reviews, list) or len(reviews) > 1:
        raise ProgrammeAdmissionError("subgate_external_review_history_invalid")
    decisive_review_id = authority["decisive_transition_enablement_review_id"]
    if not reviews:
        if decisive_review_id is not None:
            raise ProgrammeAdmissionError("subgate_decisive_review_invalid")
    else:
        review_entry = _exact_keys(
            reviews[0],
            _SUBGATE_REVIEW_HISTORY_KEYS,
            "subgate_external_review_history_entry_invalid",
        )
        review_id = _bounded_text(
            review_entry["review_id"], "subgate_review_id_invalid", 128
        )
        expected_path = f"{SUBGATE_REVIEW_ROOT}/{review_id}.json"
        if (
            _IDENTIFIER.fullmatch(review_id) is None
            or decisive_review_id != review_id
            or review_entry["review_record_path"] != expected_path
            or review_entry["verdict"] != "PASS"
            or review_entry["blocking_finding_count"] != 0
            or review_entry["g1a2_state_transition_authorized"] is not True
            or review_entry["g1a2_implementation_authorized"] is not False
            or review_entry["provider_invocation_authorized"] is not False
            or not isinstance(review_entry["review_record_sha256"], str)
            or _SHA256.fullmatch(review_entry["review_record_sha256"]) is None
        ):
            raise ProgrammeAdmissionError("subgate_external_review_binding_invalid")
        try:
            review_payload = (root / expected_path).read_bytes()
        except OSError as error:
            raise ProgrammeAdmissionError("subgate_external_review_missing") from error
        if _sha256_bytes(review_payload) != review_entry["review_record_sha256"]:
            raise ProgrammeAdmissionError("subgate_external_review_digest_mismatch")
        review = _strict_json_payload(review_payload, "subgate_external_review_invalid")
        _exact_keys(
            review,
            _SUBGATE_REVIEW_RECORD_KEYS,
            "subgate_external_review_schema_invalid",
        )
        if (
            review["schema_version"] != "ariadne.external_subgate_review.v1"
            or review["review_subject"] != "G1A.2_transition_enablement"
            or any(
                review[field] != review_entry[field]
                for field in (
                    "review_id",
                    "reviewed_commit",
                    "reviewed_tree",
                    "verdict",
                    "blocking_finding_count",
                    "reviewer_surface",
                    "g1a2_state_transition_authorized",
                    "g1a2_implementation_authorized",
                    "provider_invocation_authorized",
                )
            )
            or not isinstance(review["source_artifact_sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", review["source_artifact_sha256"]) is None
        ):
            raise ProgrammeAdmissionError("subgate_external_review_record_invalid")
        _timestamp_with_timezone(
            review["recorded_at"], "subgate_review_recorded_at_invalid"
        )
        _validate_commit_tree_binding(
            root,
            commit=review["reviewed_commit"],
            tree=review["reviewed_tree"],
            reason="subgate_review_commit_tree_binding_invalid",
        )
    return authority


def _validate_review_history(acceptance: dict[str, Any], root: Path) -> dict[str, Any]:
    history = acceptance["external_review_history"]
    if not isinstance(history, list) or not history:
        raise ProgrammeAdmissionError("g0_external_review_history_invalid")
    review_ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for raw_entry in history:
        entry = _exact_keys(
            raw_entry,
            _REVIEW_HISTORY_ENTRY_KEYS,
            "g0_external_review_history_entry_invalid",
        )
        review_id = _bounded_text(entry["review_id"], "g0_review_id_invalid", 128)
        if _IDENTIFIER.fullmatch(review_id) is None or review_id in review_ids:
            raise ProgrammeAdmissionError("g0_review_id_invalid")
        review_ids.add(review_id)
        raw_path = _bounded_text(
            entry["review_record_path"], "g0_review_record_path_invalid", 240
        )
        pure = PurePosixPath(raw_path)
        if (
            pure.is_absolute()
            or "\\" in raw_path
            or any(part in {"", ".", ".."} for part in pure.parts)
            or raw_path
            not in {
                f"{RETAINED_REVIEW_ROOT}/{review_id}.json",
                f"{TRANSITION_REVIEW_ROOT}/{review_id}.json",
            }
        ):
            raise ProgrammeAdmissionError("g0_review_record_path_invalid")
        try:
            payload = (root / Path(*pure.parts)).read_bytes()
        except OSError as error:
            raise ProgrammeAdmissionError("g0_review_record_missing") from error
        if entry["review_record_sha256"] != _sha256_bytes(payload):
            raise ProgrammeAdmissionError("g0_review_record_digest_mismatch")
        record = _strict_json_payload(payload, "g0_review_record_invalid")
        _exact_keys(record, _REVIEW_RECORD_KEYS, "g0_review_record_schema_invalid")
        if record["schema_version"] != "raisa-ariadne.external-g0-review.v2":
            raise ProgrammeAdmissionError("g0_review_record_schema_invalid")
        _bounded_text(record["recorded_at"], "g0_review_recorded_at_invalid", 64)
        _bounded_text(record["reviewer_surface"], "reviewer_surface_invalid", 256)
        if (
            not isinstance(record["source_artifact_sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", record["source_artifact_sha256"]) is None
        ):
            raise ProgrammeAdmissionError("g0_review_source_digest_invalid")
        for field in (
            "review_id",
            "reviewed_commit",
            "reviewed_tree",
            "verdict",
            "blocking_finding_count",
            "reviewer_surface",
            "g1a_authorized",
        ):
            if record[field] != entry[field]:
                raise ProgrammeAdmissionError("g0_review_record_binding_mismatch")
        if (
            entry["verdict"] not in {"PASS", "REVISION_REQUIRED"}
            or isinstance(entry["blocking_finding_count"], bool)
            or not isinstance(entry["blocking_finding_count"], int)
            or entry["blocking_finding_count"] < 0
            or entry["g1a_authorized"]
            is not (entry["verdict"] == "PASS" and entry["blocking_finding_count"] == 0)
        ):
            raise ProgrammeAdmissionError("g0_review_verdict_authority_invalid")
        _validate_commit_tree_binding(
            root,
            commit=entry["reviewed_commit"],
            tree=entry["reviewed_tree"],
            reason="g0_review_commit_tree_binding_invalid",
        )
        by_id[review_id] = entry
    decisive_id = _bounded_text(
        acceptance["decisive_review_id"], "g0_decisive_review_id_invalid", 128
    )
    if decisive_id not in by_id:
        raise ProgrammeAdmissionError("g0_decisive_review_missing")
    return by_id[decisive_id]


def _validate_state(value: dict[str, Any], root: Path) -> None:
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
            "active_profile",
            "machine_authoritative",
            "feature_work_eligible",
            "product_work_eligible",
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
            "g1a_subgate_authority",
            "g0_1_correction",
            "g0_2_correction",
            "g0_3_correction",
            "g0_4_correction",
            "g0_5_correction",
            "g0_6_correction",
            "g0_7_correction",
            "g0_8_correction",
            "gate_transition",
        },
        "programme_state_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.programme-state.v1"
        or value["programme_mode"] != "recovery"
        or value["machine_authoritative"] is not True
        or value["feature_work_eligible"] is not False
        or value["product_work_eligible"] is not False
    ):
        raise ProgrammeAdmissionError("programme_state_not_fail_closed")

    subgate_authority = _validate_g1a_subgate_authority(
        value["g1a_subgate_authority"], root
    )
    subgates = _exact_keys(
        subgate_authority["subgates"],
        {"G1A.1", "G1A.2", "G1A.3"},
        "g1a_subgate_state_schema_invalid",
    )
    g1a1_state = _exact_keys(
        subgates["G1A.1"],
        {
            "implementation_status",
            "owner_disposition_id",
            "external_review_status",
            "residual_risk_ids",
        },
        "g1a_1_state_schema_invalid",
    )
    if (
        g1a1_state["implementation_status"] != "accepted_by_owner_with_residual_risk"
        or g1a1_state["owner_disposition_id"] != OWNER_DISPOSITION_ID
        or g1a1_state["external_review_status"]
        != "no_external_pass_owner_disposition_only"
        or g1a1_state["residual_risk_ids"] != ["G1A1-PARSER-MIXED-TAB-001"]
    ):
        raise ProgrammeAdmissionError("g1a_1_owner_acceptance_state_invalid")
    g1a2_state = _exact_keys(
        subgates["G1A.2"],
        {
            "transition_enablement_tranche",
            "transition_enablement_status",
            "state_transition_status",
            "state_transition",
            "implementation_status",
            "implementation_review_id",
            "implementation_authorized",
            "implementation_started",
            "provider_invocation_authorized",
            "next_action",
        },
        "g1a_2_state_schema_invalid",
    )
    g1a3_state = _exact_keys(
        subgates["G1A.3"],
        {
            "status",
            "transition_enablement_tranche",
            "transition_enablement_status",
            "state_transition_status",
            "state_transition",
            "implementation_authorized",
            "implementation_started",
            "integration_execution_authorized",
            "provider_invocation_authorized",
            "protected_ref_movement_authorized",
            "next_action",
            "owner_exception",
        },
        "g1a_3_state_schema_invalid",
    )
    owner_exception = _exact_keys(
        g1a3_state["owner_exception"],
        {
            "task_generation",
            "branch",
            "authorized_parent_commit",
            "candidate_commit_limit",
            "state_transition_authorized",
            "provider_invocation_authorized",
            "integration_authorized",
            "protected_ref_movement_authorized",
        },
        "g1a3_owner_exception_schema_invalid",
    )
    if (
        g1a2_state["transition_enablement_tranche"] != "G1A.2-E0"
        or g1a2_state["transition_enablement_status"] != "external_review_passed"
        or g1a2_state["state_transition_status"] != "complete"
        or not isinstance(g1a2_state["state_transition"], dict)
        or g1a2_state["implementation_status"] != "external_review_passed"
        or g1a2_state["implementation_review_id"]
        != subgate_authority["decisive_implementation_review_id"]
        or g1a2_state["implementation_authorized"] is not False
        or g1a2_state["implementation_started"] is not False
        or g1a2_state["provider_invocation_authorized"] is not False
        or g1a2_state["next_action"]
        != "external_G1A3_transition_enablement_review_only"
        or g1a3_state["transition_enablement_tranche"] != "G1A.3-E0"
        or g1a3_state["implementation_started"] is not False
        or g1a3_state["integration_execution_authorized"] is not False
        or g1a3_state["provider_invocation_authorized"] is not False
        or g1a3_state["protected_ref_movement_authorized"] is not False
        or owner_exception
        != {
            "task_generation": "g1a3-transition-enablement-runtime-source-encoding-replacement-20260829-v1",
            "branch": "codex/raisa-ariadne-recovery-g0",
            "authorized_parent_commit": "37e2d6f51ebbdb281771f922a5f460fd23e2571b",
            "candidate_commit_limit": 1,
            "state_transition_authorized": False,
            "provider_invocation_authorized": False,
            "integration_authorized": False,
            "protected_ref_movement_authorized": False,
        }
    ):
        raise ProgrammeAdmissionError("g1a_subgate_state_not_fail_closed")
    transition = _exact_keys(
        g1a2_state["state_transition"],
        {
            "status",
            "transition_id",
            "from_gate",
            "to_gate",
            "owner_disposition_id",
            "external_review_id",
            "enablement_controller_commit",
            "enablement_controller_tree",
            "external_review_status",
            "blocking_finding_count",
            "reviewer_surface",
            "next_action",
        },
        "g1a_subgate_transition_state_schema_invalid",
    )
    if (
        transition["status"] != "complete"
        or transition["from_gate"] != SUBGATE_TRANSITION_FROM_GATE
        or transition["to_gate"] != SUBGATE_TRANSITION_TO_GATE
        or transition["owner_disposition_id"] != OWNER_DISPOSITION_ID
        or transition["external_review_id"]
        != subgate_authority["decisive_transition_enablement_review_id"]
        or transition["external_review_status"] != "pass"
        or transition["blocking_finding_count"] != 0
    ):
        raise ProgrammeAdmissionError("g1a_subgate_transition_state_invalid")
    _validate_commit_tree_binding(
        root,
        commit=transition["enablement_controller_commit"],
        tree=transition["enablement_controller_tree"],
        reason="g1a_enablement_controller_binding_invalid",
    )

    g1a3_active = g1a3_state["state_transition_status"] == "complete"
    if g1a3_active:
        g1a3_transition = _exact_keys(
            g1a3_state["state_transition"],
            {
                "status",
                "transition_id",
                "from_gate",
                "to_gate",
                "g1a2_implementation_review_id",
                "external_review_id",
                "enablement_controller_commit",
                "enablement_controller_tree",
                "external_review_status",
                "blocking_finding_count",
                "reviewer_surface",
                "next_action",
            },
            "g1a3_state_transition_schema_invalid",
        )
        if (
            g1a3_state["status"] != "active"
            or g1a3_state["transition_enablement_status"] != "external_review_passed"
            or g1a3_state["implementation_authorized"] is not True
            or g1a3_state["next_action"]
            != "begin_bounded_G1A3_integration_consumer_implementation"
            or g1a3_transition["status"] != "complete"
            or g1a3_transition["from_gate"] != G1A3_TRANSITION_FROM_GATE
            or g1a3_transition["to_gate"] != G1A3_TRANSITION_TO_GATE
            or g1a3_transition["g1a2_implementation_review_id"]
            != subgate_authority["decisive_implementation_review_id"]
            or g1a3_transition["external_review_id"]
            != subgate_authority["decisive_g1a3_transition_enablement_review_id"]
            or g1a3_transition["external_review_status"] != "pass"
            or g1a3_transition["blocking_finding_count"] != 0
        ):
            raise ProgrammeAdmissionError("g1a3_state_transition_invalid")
        _validate_commit_tree_binding(
            root,
            commit=g1a3_transition["enablement_controller_commit"],
            tree=g1a3_transition["enablement_controller_tree"],
            reason="g1a3_enablement_controller_binding_invalid",
        )
    elif (
        g1a3_state["status"] != "closed_pending_state_transition"
        or g1a3_state["transition_enablement_status"] != "review_pending"
        or g1a3_state["state_transition_status"] != "not_started"
        or g1a3_state["state_transition"] is not None
        or g1a3_state["implementation_authorized"] is not False
        or g1a3_state["next_action"]
        != "external_G1A3_transition_enablement_review_only"
        or subgate_authority["decisive_g1a3_transition_enablement_review_id"]
        is not None
        or subgate_authority["g1a3_transition_enablement_review_history"] != []
    ):
        raise ProgrammeAdmissionError("g1a3_enablement_candidate_state_invalid")

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
    allowed_task_kinds = selection["allowed_task_kinds"]
    if not isinstance(allowed_task_kinds, list) or any(
        not isinstance(item, str) for item in allowed_task_kinds
    ):
        raise ProgrammeAdmissionError("allowed_task_kinds_invalid")
    blocked_task_kinds = set(
        _unique_text_list(selection["blocked_task_kinds"], "blocked_task_kinds_invalid")
    )
    _bounded_text(selection["admission_command"], "admission_command_invalid", 500)
    phase = value["active_correction"]
    if phase not in {
        ADMITTED_PROGRAMME_GATE,
        TRANSITION_TO_GATE,
        SUBGATE_TRANSITION_TO_GATE,
        G1A3_TRANSITION_TO_GATE,
    }:
        raise ProgrammeAdmissionError("programme_phase_invalid")
    if phase == TRANSITION_TO_GATE and g1a2_state["next_action"] != (
        "external_G1A2_transition_enablement_review_only"
    ):
        raise ProgrammeAdmissionError("g1a_2_next_action_invalid")
    if phase == ADMITTED_PROGRAMME_GATE:
        expected_task_classes = [ADMITTED_TASK_CLASS]
    elif value["active_profile"] == G1A2_ACTIVE_PROFILE:
        expected_task_classes = [G1A2_TASK_CLASS]
    elif value["active_profile"] == G1A3_ACTIVE_PROFILE:
        expected_task_classes = [G1A3_TASK_CLASS]
    else:
        expected_task_classes = []
    expected_gate = "G0" if phase == ADMITTED_PROGRAMME_GATE else phase
    expected_status = (
        "revision_required" if phase == ADMITTED_PROGRAMME_GATE else "active"
    )
    profile = value["active_profile"]
    expected_by_phase = {
        ADMITTED_PROGRAMME_GATE: G0_CONTROLLER_PROFILE,
        TRANSITION_TO_GATE: G1A_ACTIVE_PROFILE,
        SUBGATE_TRANSITION_TO_GATE: profile,
        G1A3_TRANSITION_TO_GATE: G1A3_ACTIVE_PROFILE,
    }
    expected_profile = expected_by_phase[phase]
    if phase == ADMITTED_PROGRAMME_GATE:
        expected_next_tranche = ADMITTED_PROGRAMME_GATE
        expected_next_now = True
        expected_requires_transition = True
    elif profile == G1A3_ENABLEMENT_PENDING_PROFILE:
        expected_next_tranche = G1A3_TRANSITION_TO_GATE
        expected_next_now = False
        expected_requires_transition = True
    elif profile == G1A3_ACTIVE_PROFILE:
        expected_next_tranche = G1A3_TRANSITION_TO_GATE
        expected_next_now = True
        expected_requires_transition = False
    else:
        expected_next_tranche = SUBGATE_TRANSITION_TO_GATE
        expected_next_now = phase != TRANSITION_TO_GATE
        expected_requires_transition = phase == TRANSITION_TO_GATE
    if (
        selection["autonomous_selection_enabled"] is not False
        or allowed_task_kinds != expected_task_classes
        or blocked_task_kinds
        != {
            "product_feature",
            "g1a_untyped_or_out_of_scope",
            "integration",
            "provider_call",
            "deployment",
            "protected_ref_operation",
        }
        or selection["out_of_gate_result"] != "blocked"
        or selection["next_eligible_tranche"] != expected_next_tranche
        or selection["next_eligible_now"] is not expected_next_now
        or selection["next_tranche_started"] is not False
        or selection["next_tranche_admission_requires_state_transition"]
        is not expected_requires_transition
        or value["current_gate"] != expected_gate
        or value["current_gate_status"] != expected_status
        or value["active_profile"] != expected_profile
    ):
        raise ProgrammeAdmissionError("programme_task_selection_not_fail_closed")

    acceptance = _exact_keys(
        value["g0_acceptance"],
        {
            "status",
            "independent_review",
            "decisive_review_id",
            "external_review_history",
            "g0_checks",
            "next_action",
        },
        "g0_acceptance_schema_invalid",
    )
    decisive_review = _validate_review_history(acceptance, root)
    if phase == ADMITTED_PROGRAMME_GATE:
        if (
            acceptance["status"] != "superseded_revision_required"
            or decisive_review["verdict"] != "REVISION_REQUIRED"
            or decisive_review["blocking_finding_count"] <= 0
            or decisive_review["g1a_authorized"] is not False
        ):
            raise ProgrammeAdmissionError("g0_decisive_review_state_invalid")
    elif (
        acceptance["status"] != "passed"
        or decisive_review["verdict"] != "PASS"
        or decisive_review["blocking_finding_count"] != 0
        or decisive_review["g1a_authorized"] is not True
    ):
        raise ProgrammeAdmissionError("g0_decisive_review_state_invalid")

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
        correction["status"]
        not in {"in_progress", "review_pending", "superseded_revision_required"}
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
        if (
            not isinstance(correction_g02[field], str)
            or _SHA1.fullmatch(correction_g02[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_2_correction_binding_invalid")
    if correction_g02["candidate_commit_limit"] != 1:
        raise ProgrammeAdmissionError("g0_2_correction_limit_invalid")
    if (
        correction_g02["status"] != "superseded_revision_required"
        or correction_g02["external_review_status"] != "revision_required"
        or correction_g02["g1a_authorized"] is not False
    ):
        raise ProgrammeAdmissionError("g0_2_correction_history_invalid")

    correction_g03 = _exact_keys(
        value["g0_3_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_2_tree",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_3_correction_schema_invalid",
    )
    for field in ("authorized_parent_commit", "reviewed_g0_2_tree"):
        if (
            not isinstance(correction_g03[field], str)
            or _SHA1.fullmatch(correction_g03[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_3_correction_binding_invalid")
    if correction_g03["candidate_commit_limit"] != 1:
        raise ProgrammeAdmissionError("g0_3_correction_limit_invalid")
    if (
        correction_g03["status"] != "superseded_revision_required"
        or correction_g03["external_review_status"] != "revision_required"
        or correction_g03["g1a_authorized"] is not False
    ):
        raise ProgrammeAdmissionError("g0_3_correction_history_invalid")

    correction_g04 = _exact_keys(
        value["g0_4_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_3_tree",
            "correction_directive_sha256",
            "review_verdict",
            "review_finding_count",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_4_correction_schema_invalid",
    )
    for field in (
        "authorized_parent_commit",
        "reviewed_g0_3_tree",
    ):
        if (
            not isinstance(correction_g04[field], str)
            or _SHA1.fullmatch(correction_g04[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_4_correction_binding_invalid")
    if (
        not isinstance(correction_g04["correction_directive_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", correction_g04["correction_directive_sha256"])
        is None
        or correction_g04["review_verdict"] != "REVISION_REQUIRED"
        or correction_g04["review_finding_count"] != 3
        or correction_g04["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("g0_4_correction_review_invalid")

    correction_g05 = _exact_keys(
        value["g0_5_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_4_tree",
            "correction_directive_sha256",
            "review_verdict",
            "review_finding_count",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_5_correction_schema_invalid",
    )
    for field in ("authorized_parent_commit", "reviewed_g0_4_tree"):
        if (
            not isinstance(correction_g05[field], str)
            or _SHA1.fullmatch(correction_g05[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_5_correction_binding_invalid")
    if (
        not isinstance(correction_g05["correction_directive_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", correction_g05["correction_directive_sha256"])
        is None
        or correction_g05["review_verdict"] != "REVISION_REQUIRED"
        or correction_g05["review_finding_count"] != 3
        or correction_g05["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("g0_5_correction_review_invalid")

    correction_g06 = _exact_keys(
        value["g0_6_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_5_tree",
            "correction_directive_sha256",
            "review_verdict",
            "review_finding_count",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_6_correction_schema_invalid",
    )
    for field in ("authorized_parent_commit", "reviewed_g0_5_tree"):
        if (
            not isinstance(correction_g06[field], str)
            or _SHA1.fullmatch(correction_g06[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_6_correction_binding_invalid")
    if (
        not isinstance(correction_g06["correction_directive_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", correction_g06["correction_directive_sha256"])
        is None
        or correction_g06["review_verdict"] != "REVISION_REQUIRED"
        or correction_g06["review_finding_count"] != 2
        or correction_g06["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("g0_6_correction_review_invalid")

    correction_g07 = _exact_keys(
        value["g0_7_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_6_tree",
            "correction_directive_sha256",
            "review_verdict",
            "review_finding_count",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_7_correction_schema_invalid",
    )
    for field in ("authorized_parent_commit", "reviewed_g0_6_tree"):
        if (
            not isinstance(correction_g07[field], str)
            or _SHA1.fullmatch(correction_g07[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_7_correction_binding_invalid")
    if (
        not isinstance(correction_g07["correction_directive_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", correction_g07["correction_directive_sha256"])
        is None
        or correction_g07["review_verdict"] != "REVISION_REQUIRED"
        or correction_g07["review_finding_count"] != 2
        or correction_g07["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("g0_7_correction_review_invalid")

    correction_g08 = _exact_keys(
        value["g0_8_correction"],
        {
            "status",
            "authorized_parent_commit",
            "reviewed_g0_7_tree",
            "correction_directive_sha256",
            "review_verdict",
            "review_finding_count",
            "candidate_commit_limit",
            "external_review_status",
            "g1a_authorized",
            "next_action",
        },
        "g0_8_correction_schema_invalid",
    )
    for field in ("authorized_parent_commit", "reviewed_g0_7_tree"):
        if (
            not isinstance(correction_g08[field], str)
            or _SHA1.fullmatch(correction_g08[field]) is None
        ):
            raise ProgrammeAdmissionError("g0_8_correction_binding_invalid")
    if (
        not isinstance(correction_g08["correction_directive_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", correction_g08["correction_directive_sha256"])
        is None
        or correction_g08["review_verdict"] != "REVISION_REQUIRED"
        or correction_g08["review_finding_count"] != 1
        or correction_g08["candidate_commit_limit"] != 1
    ):
        raise ProgrammeAdmissionError("g0_8_correction_review_invalid")

    _validate_commit_tree_binding(
        root,
        commit=correction["authorized_parent_commit"],
        tree=correction["reviewed_g0_tree"],
        reason="g0_1_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g02["authorized_parent_commit"],
        tree=correction_g02["reviewed_g0_1_tree"],
        reason="g0_2_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g03["authorized_parent_commit"],
        tree=correction_g03["reviewed_g0_2_tree"],
        reason="g0_3_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g04["authorized_parent_commit"],
        tree=correction_g04["reviewed_g0_3_tree"],
        reason="g0_4_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g05["authorized_parent_commit"],
        tree=correction_g05["reviewed_g0_4_tree"],
        reason="g0_5_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g06["authorized_parent_commit"],
        tree=correction_g06["reviewed_g0_5_tree"],
        reason="g0_6_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g07["authorized_parent_commit"],
        tree=correction_g07["reviewed_g0_6_tree"],
        reason="g0_7_review_tree_binding_invalid",
    )
    _validate_commit_tree_binding(
        root,
        commit=correction_g08["authorized_parent_commit"],
        tree=correction_g08["reviewed_g0_7_tree"],
        reason="g0_8_review_tree_binding_invalid",
    )
    if correction_g08["correction_directive_sha256"] != authority["directive_sha256"]:
        raise ProgrammeAdmissionError("decisive_external_review_binding_invalid")
    if phase == ADMITTED_PROGRAMME_GATE and (
        decisive_review["reviewed_commit"] != correction_g08["authorized_parent_commit"]
        or decisive_review["reviewed_tree"] != correction_g08["reviewed_g0_7_tree"]
    ):
        raise ProgrammeAdmissionError("decisive_external_review_binding_invalid")

    expected_negative_history = [
        (
            "g0-review-c720aaa-revision-required",
            "orchestration/programme/reviews/g0-review-c720aaa-revision-required.json",
            "c720aaa306c449faae879bf9e6192c72b6c3c6a4",
            "c304850067dfe92a02fdb612f2f2155fe1e60551",
            4,
            "sha256:9a0a2dfd8d7651fba1702b651fec958c46ec326d9b9ed638297ff8ceef3fd636",
        ),
        (
            "g0-review-087522d-revision-required",
            "orchestration/programme/reviews/g0-review-087522d-revision-required.json",
            "087522d7b9cf6d5a26056412230f2513530aab1f",
            "a84b040d8146a2ed5bfbddaff3531768801aa3be",
            2,
            "sha256:1bcc14de29066e15c63e1c972405a02049c9190361da3787a7bc13574a03a5c9",
        ),
        (
            "g0-review-7cae4e8-revision-required",
            "orchestration/programme/reviews/g0-review-7cae4e8-revision-required.json",
            "7cae4e88e2f3951e51dcaf1378e52187e191a33d",
            "bbeddb0e467c57970024d14cddf72156bed86947",
            2,
            "sha256:8cb0691dee33fdbef7de062fdd48fef8250137a4b4e67dec1ea4964600393153",
        ),
        (
            "g0-review-2af9278-revision-required",
            "orchestration/programme/reviews/g0-review-2af9278-revision-required.json",
            "2af92789819e8114a1bfe8e956a5742136e4a139",
            "9da62d169d564c86afdd087ec03da270e4989d91",
            3,
            "sha256:5bf11e83d6f1745098b9b1dcc67d8c444e99222d32973670c86b9e9680f2d27e",
        ),
        (
            "g0-review-4ce1719-revision-required",
            "orchestration/programme/reviews/g0-review-4ce1719-revision-required.json",
            "4ce17198fad677aed1fe45be4e3bf2b18c713b3b",
            "e061800df0ae7c5daba6b2db13e8aa774f3eaff9",
            3,
            "sha256:b1e640aad986755642434969c93272fb6d7d2a33f8bb246bcdc3df06ef36105f",
        ),
        (
            "g0-review-71e2c5f-revision-required",
            "orchestration/programme/reviews/g0-review-71e2c5f-revision-required.json",
            "71e2c5f2f586fa4d1ca8fa9787a4906dbbb997f1",
            "ef84162bbc6ef24241678d14e0183b876af3a1e3",
            2,
            "sha256:5762acbb96597d15772b68acf9b111d60cb49c05afd016a936bf15a9952a7830",
        ),
        (
            "g0-review-4a8e71c-independent-20260826-revision-required",
            "orchestration/programme/reviews/g0-review-4a8e71c-independent-20260826-revision-required.json",
            "4a8e71ca98d3af013d51ca6c206932e363cdf174",
            "a23cc914dddd1e17121f7b04083ee1c08338549a",
            2,
            "sha256:50211598382ebcca3138702d51db92a16eab3eefbef87ea771e0c4b3d544f73f",
        ),
        (
            "g0-review-6e101d1-independent-20260827-revision-required",
            "orchestration/programme/reviews/g0-review-6e101d1-independent-20260827-revision-required.json",
            "6e101d15f824f68c3f44d0a3cb44a3aa2afd5b1b",
            "00c1af2f47ceee88c10507809f69058c24c6bd85",
            1,
            "sha256:7f6dd7053d4edf87839127001abbd6842638d287045fcf4fe4a82e18c0ea7f7b",
        ),
    ]
    history = acceptance["external_review_history"]
    if (
        len(history) < len(expected_negative_history)
        or [
            (
                row["review_id"],
                row["review_record_path"],
                row["reviewed_commit"],
                row["reviewed_tree"],
                row["blocking_finding_count"],
                row["review_record_sha256"],
            )
            for row in history[: len(expected_negative_history)]
        ]
        != expected_negative_history
        or any(
            row["verdict"] != "REVISION_REQUIRED" or row["g1a_authorized"] is not False
            for row in history[: len(expected_negative_history)]
        )
    ):
        raise ProgrammeAdmissionError("retained_external_review_history_invalid")

    if phase == ADMITTED_PROGRAMME_GATE:
        if (
            correction_g04["status"] != "superseded_revision_required"
            or correction_g04["external_review_status"] != "revision_required"
            or correction_g04["g1a_authorized"] is not False
            or correction_g05["status"] != "superseded_revision_required"
            or correction_g05["external_review_status"] != "revision_required"
            or correction_g05["g1a_authorized"] is not False
            or correction_g06["status"] != "superseded_revision_required"
            or correction_g06["external_review_status"] != "revision_required"
            or correction_g06["g1a_authorized"] is not False
            or correction_g07["status"] != "superseded_revision_required"
            or correction_g07["external_review_status"] != "revision_required"
            or correction_g07["g1a_authorized"] is not False
            or correction_g08["status"] not in {"in_progress", "review_pending"}
            or correction_g08["external_review_status"]
            not in {"not_started", "pending"}
            or correction_g08["g1a_authorized"] is not False
            or value["gate_transition"] is not None
        ):
            raise ProgrammeAdmissionError("g0_8_correction_not_fail_closed")
    else:
        if (
            correction_g04["status"] != "superseded_revision_required"
            or correction_g04["external_review_status"] != "revision_required"
            or correction_g04["g1a_authorized"] is not False
            or correction_g05["status"] != "superseded_revision_required"
            or correction_g05["external_review_status"] != "revision_required"
            or correction_g05["g1a_authorized"] is not False
            or correction_g06["status"] != "superseded_revision_required"
            or correction_g06["external_review_status"] != "revision_required"
            or correction_g06["g1a_authorized"] is not False
            or correction_g07["status"] != "superseded_revision_required"
            or correction_g07["external_review_status"] != "revision_required"
            or correction_g07["g1a_authorized"] is not False
            or correction_g08["status"] != "external_review_passed"
            or correction_g08["external_review_status"] != "pass"
            or correction_g08["g1a_authorized"] is not True
        ):
            raise ProgrammeAdmissionError("g0_8_transition_history_invalid")
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
            transition["status"] != "complete"
            or transition["from_gate"] != TRANSITION_FROM_GATE
            or transition["to_gate"] != TRANSITION_TO_GATE
            or transition["external_review_status"] != "pass"
            or transition["blocking_finding_count"] != 0
            or transition["g1a_authorized"] is not True
            or transition["transition_id"] != acceptance["decisive_review_id"]
            or transition["reviewed_commit"] != decisive_review["reviewed_commit"]
            or transition["reviewed_tree"] != decisive_review["reviewed_tree"]
            or transition["reviewer_surface"] != decisive_review["reviewer_surface"]
        ):
            raise ProgrammeAdmissionError("gate_transition_state_invalid")
        if (
            _IDENTIFIER.fullmatch(
                _bounded_text(transition["transition_id"], "transition_id_invalid", 128)
            )
            is None
        ):
            raise ProgrammeAdmissionError("transition_id_invalid")
        _bounded_text(transition["reviewer_surface"], "reviewer_surface_invalid", 256)
        for field in ("reviewed_commit", "reviewed_tree"):
            if (
                not isinstance(transition[field], str)
                or _SHA1.fullmatch(transition[field]) is None
            ):
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
        {
            "schema_version",
            "programme",
            "global_hard_stops",
            "protected_invariants",
            "gates",
        },
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
            else (
                G1A3_TRANSITION_TO_GATE
                if state["active_profile"]
                in {G1A3_ENABLEMENT_PENDING_PROFILE, G1A3_ACTIVE_PROFILE}
                else SUBGATE_TRANSITION_TO_GATE
            )
        )
    ):
        raise ProgrammeAdmissionError("programme_state_gate_disagreement")
    _unique_text_list(value["global_hard_stops"], "global_hard_stops_invalid")
    protected = _exact_keys(
        value["protected_invariants"],
        {"raisa", "ariadne"},
        "protected_invariants_invalid",
    )
    _unique_text_list(protected["raisa"], "raisa_invariants_invalid")
    _unique_text_list(protected["ariadne"], "ariadne_invariants_invalid")
    gates = value["gates"]
    if not isinstance(gates, list) or not gates:
        raise ProgrammeAdmissionError("gate_inventory_invalid")
    by_id: dict[str, dict[str, Any]] = {}
    allowed_gate_keys = {
        "id",
        "name",
        "status",
        "prerequisites",
        "programme_mode",
        "allowed_work",
        "prohibited_work",
        "exit_checks",
        "next_gate",
    }
    for gate in gates:
        if not isinstance(gate, dict) or not set(gate).issubset(allowed_gate_keys):
            raise ProgrammeAdmissionError("gate_schema_invalid")
        required = {
            "id",
            "name",
            "status",
            "prerequisites",
            "programme_mode",
            "exit_checks",
            "next_gate",
        }
        if not required.issubset(gate):
            raise ProgrammeAdmissionError("gate_schema_invalid")
        gate_id = _bounded_text(gate["id"], "gate_id_invalid", 32)
        if gate_id in by_id:
            raise ProgrammeAdmissionError("gate_id_duplicate")
        _unique_text_list(gate["exit_checks"], "gate_exit_checks_invalid")
        if gate["programme_mode"] not in {
            "recovery",
            "convergence",
            "pilot_preparation",
            "release",
        }:
            raise ProgrammeAdmissionError("gate_mode_invalid")
        by_id[gate_id] = gate
    if state["active_correction"] == ADMITTED_PROGRAMME_GATE:
        current_statuses = {
            "G0": "revision_required_g0_8",
            "G0.1": "superseded_revision_required",
            "G0.2": "superseded_revision_required",
            "G0.3": "superseded_revision_required",
            "G0.4": "superseded_revision_required",
            "G0.5": "superseded_revision_required",
            "G0.6": "superseded_revision_required",
            "G0.7": "superseded_revision_required",
            "G0.8": state["g0_8_correction"]["status"],
            "G1A": "subgated_closed",
            "G1A.1": "blocked_by_external_G0_review",
            "G1A.2": "blocked_by_G1A_1_external_review",
            "G1A.3": "deferred_integration_mutation",
        }
    elif state["active_correction"] == TRANSITION_TO_GATE:
        current_statuses = {
            "G0": "passed",
            "G0.1": "superseded_revision_required",
            "G0.2": "superseded_revision_required",
            "G0.3": "superseded_revision_required",
            "G0.4": "superseded_revision_required",
            "G0.5": "superseded_revision_required",
            "G0.6": "superseded_revision_required",
            "G0.7": "superseded_revision_required",
            "G0.8": "external_review_passed",
            "G1A": "transition_enablement_review_pending",
            "G1A.1": "accepted_by_owner_with_residual_risk",
            "G1A.2": "closed_pending_transition_enablement_external_review_and_state_transition",
            "G1A.3": "deferred_integration_mutation",
        }
    elif state["active_profile"] == G1A3_ENABLEMENT_PENDING_PROFILE:
        current_statuses = {
            "G0": "passed",
            "G0.1": "superseded_revision_required",
            "G0.2": "superseded_revision_required",
            "G0.3": "superseded_revision_required",
            "G0.4": "superseded_revision_required",
            "G0.5": "superseded_revision_required",
            "G0.6": "superseded_revision_required",
            "G0.7": "superseded_revision_required",
            "G0.8": "external_review_passed",
            "G1A": "g1a3_transition_enablement_review_pending",
            "G1A.1": "accepted_by_owner_with_residual_risk",
            "G1A.2": "external_review_passed",
            "G1A.3": "closed_pending_transition_enablement_external_review_and_state_transition",
        }
    elif state["active_profile"] == G1A3_ACTIVE_PROFILE:
        current_statuses = {
            "G0": "passed",
            "G0.1": "superseded_revision_required",
            "G0.2": "superseded_revision_required",
            "G0.3": "superseded_revision_required",
            "G0.4": "superseded_revision_required",
            "G0.5": "superseded_revision_required",
            "G0.6": "superseded_revision_required",
            "G0.7": "superseded_revision_required",
            "G0.8": "external_review_passed",
            "G1A": "active_subgate_G1A_3",
            "G1A.1": "accepted_by_owner_with_residual_risk",
            "G1A.2": "external_review_passed",
            "G1A.3": "active",
        }
    else:
        current_statuses = {
            "G0": "passed",
            "G0.1": "superseded_revision_required",
            "G0.2": "superseded_revision_required",
            "G0.3": "superseded_revision_required",
            "G0.4": "superseded_revision_required",
            "G0.5": "superseded_revision_required",
            "G0.6": "superseded_revision_required",
            "G0.7": "superseded_revision_required",
            "G0.8": "external_review_passed",
            "G1A": "active_subgate_G1A_2",
            "G1A.1": "accepted_by_owner_with_residual_risk",
            "G1A.2": "active",
            "G1A.3": "deferred_integration_mutation",
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
        if by_id.get("G1A.1", {}).get("status") != "blocked_by_external_G0_review":
            raise ProgrammeAdmissionError("g1a_not_closed")
    elif state["active_correction"] == TRANSITION_TO_GATE:
        if by_id.get("G1A.2", {}).get("status") != (
            "closed_pending_transition_enablement_external_review_and_state_transition"
        ):
            raise ProgrammeAdmissionError("g1a_2_not_closed")
    elif state["active_profile"] == G1A3_ENABLEMENT_PENDING_PROFILE:
        if by_id.get("G1A.3", {}).get("status") != (
            "closed_pending_transition_enablement_external_review_and_state_transition"
        ):
            raise ProgrammeAdmissionError("g1a_3_not_closed")
    elif state["active_profile"] == G1A3_ACTIVE_PROFILE:
        if by_id.get("G1A.3", {}).get("status") != "active":
            raise ProgrammeAdmissionError("g1a_3_not_active")
    elif by_id.get("G1A.2", {}).get("status") != "active":
        raise ProgrammeAdmissionError("g1a_2_not_active")


def _validate_risks(value: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {
            "schema_version",
            "observed_at",
            "programme_mode",
            "current_gate",
            "status_vocabulary",
            "default_g0_control",
            "risks",
        },
        "risk_register_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.risk-register.v1"
        or value["programme_mode"] != "recovery"
        or value["current_gate"] != "G0"
    ):
        raise ProgrammeAdmissionError("risk_register_header_invalid")
    vocabulary = set(
        _unique_text_list(value["status_vocabulary"], "risk_status_vocabulary_invalid")
    )
    if vocabulary != {
        "observed_unresolved",
        "seeded_requires_verification",
        "contained_by_g0_feature_freeze",
        "closed_with_evidence",
    }:
        raise ProgrammeAdmissionError("risk_status_vocabulary_invalid")
    expected = {
        *(f"R-{index:03d}" for index in range(1, 14)),
        *(f"A-{index:03d}" for index in range(1, 11)),
    }
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
    if (
        "upgrade() executes op.execute" not in by_id["R-001"]["evidence"]
        or "TRUNCATE TABLE prescriptions" not in by_id["R-001"]["evidence"]
    ):
        raise ProgrammeAdmissionError("risk_r001_evidence_invalid")
    if (
        "static/audio" not in by_id["R-003"]["evidence"]
        or "app/main.py mounts static at /static" not in by_id["R-003"]["evidence"]
    ):
        raise ProgrammeAdmissionError("risk_r003_evidence_invalid")


def _validate_inventory(value: dict[str, Any], state: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {
            "schema_version",
            "observed_at",
            "repository",
            "programme_mode",
            "current_gate",
            "mutation_policy",
            "authoritative_refs",
            "remote_branch_inventory",
            "local_topology",
            "ambiguous_current_aliases",
            "open_pr_inventory",
            "g0_conclusion",
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
        {
            "branch_deletion",
            "pr_closure",
            "pr_merge",
            "feature_rebase",
            "protected_ref_movement",
        },
        "mutation_policy_schema_invalid",
    )
    if set(mutation.values()) != {"forbidden"}:
        raise ProgrammeAdmissionError("mutation_policy_not_fail_closed")
    refs = value.get("authoritative_refs")
    if (
        not isinstance(refs, dict)
        or refs.get("recovery_branch") != state["recovery_baton"]["branch"]
        or refs.get("recovery_base") != state["recovery_baton"]["base_sha"]
    ):
        raise ProgrammeAdmissionError("branch_inventory_authority_disagreement")
    open_prs = value.get("open_pr_inventory")
    if (
        not isinstance(open_prs, dict)
        or not isinstance(open_prs.get("prs"), list)
        or open_prs.get("count") != len(open_prs["prs"])
    ):
        raise ProgrammeAdmissionError("open_pr_inventory_invalid")
    numbers: set[int] = set()
    for pr in open_prs["prs"]:
        if not isinstance(pr, dict) or not set(pr).issubset(
            {"number", "draft", "head", "base", "disposition", "stack_order"}
        ):
            raise ProgrammeAdmissionError("open_pr_entry_schema_invalid")
        if not {"number", "draft", "head", "base", "disposition"}.issubset(pr):
            raise ProgrammeAdmissionError("open_pr_entry_schema_invalid")
        if pr["disposition"] not in {"dependency_update", "quarantine"}:
            raise ProgrammeAdmissionError("open_pr_disposition_invalid")
        number = pr["number"]
        if (
            isinstance(number, bool)
            or not isinstance(number, int)
            or number <= 0
            or number in numbers
        ):
            raise ProgrammeAdmissionError("open_pr_number_invalid")
        numbers.add(number)


_PROFILE_KEYS = {
    "profile_kind",
    "expected_programme_mode",
    "expected_current_gate",
    "expected_gate_status",
    "active_correction",
    "programme_gate",
    "admitted_task_classes",
    "allowed_effects",
    "forbidden_effects",
    "closed_entrypoints",
    "scope_behavior",
    "allowed_paths",
    "autonomous_task_selection",
    "out_of_gate_result",
    "feature_work_eligible",
    "product_work_eligible",
    "provider_calls_eligible",
    "deployment_eligible",
    "protected_ref_movement_eligible",
    "g1a_eligible",
}


def _validate_g1a_scope_v1_retired(value: dict[str, Any]) -> None:
    _exact_keys(
        value,
        {
            "schema_version",
            "status",
            "prepared_at",
            "inventory_source_commit",
            "task_class",
            "objective",
            "verdict_parsers",
            "review_callers",
            "cli_exit_consumers",
            "integration_consumers",
            "excluded_consumers",
            "allowed_paths",
            "allowed_effects",
            "forbidden_effects",
        },
        "g1a_scope_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.g1a-verdict-integration-scope.v1"
        or value["status"] != "pre_reviewed_closed_scope"
        or value["inventory_source_commit"]
        != "2af92789819e8114a1bfe8e956a5742136e4a139"
        or value["task_class"] != G1A_TASK_CLASS
        or set(_unique_text_list(value["allowed_paths"], "g1a_scope_paths_invalid"))
        != G1A_ALLOWED_PATHS
        or set(_unique_text_list(value["allowed_effects"], "g1a_scope_effects_invalid"))
        != G1A_ALLOWED_EFFECTS
        or set(
            _unique_text_list(value["forbidden_effects"], "g1a_scope_forbidden_invalid")
        )
        != G1A_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("g1a_scope_not_exact")
    parser_rows = value["verdict_parsers"]
    expected_parsers = [
        {
            "id": "review_acceptance_table_parser",
            "path": "orchestration_harness/review_acceptance.py",
            "symbol": "_parse_artifact_marker",
            "disposition": "replace_with_canonical_parser",
        },
        {
            "id": "deepcode_terminal_marker_parser",
            "path": "orchestration_harness/deepcode_artifact.py",
            "symbol": "parse_artifact_marker",
            "disposition": "delegate_to_canonical_parser",
        },
        {
            "id": "antigravity_structured_and_legacy_parser",
            "path": "scripts/ariadne_antigravity.py",
            "symbol": "parse_structured_decision",
            "disposition": "delegate_decision_semantics_to_canonical_parser",
        },
    ]
    if parser_rows != expected_parsers:
        raise ProgrammeAdmissionError("g1a_parser_inventory_invalid")
    expected_callers = [
        {
            "id": "review_acceptance_gate",
            "path": "orchestration_harness/review_acceptance.py",
            "symbol": "accept_review_artifact",
        },
        {
            "id": "review_acceptance_cli",
            "path": "scripts/ariadne_review_acceptance.py",
            "symbol": "main",
        },
        {
            "id": "deepcode_liveness_observer",
            "path": "scripts/ariadne_deepcode_liveness.py",
            "symbol": "_artifact_state",
        },
        {
            "id": "antigravity_worker",
            "path": "scripts/ariadne_antigravity.py",
            "symbol": "run_worker",
        },
    ]
    caller_rows = value["review_callers"]
    if caller_rows != expected_callers:
        raise ProgrammeAdmissionError("g1a_review_caller_inventory_invalid")
    expected_cli = [
        {
            "id": "review_acceptance_exit_mapping",
            "path": "scripts/ariadne_review_acceptance.py",
            "contract": "accepted_exit_0_rejected_exit_1_input_error_exit_2",
        },
        {
            "id": "antigravity_transport_exit_mapping",
            "path": "scripts/ariadne_antigravity.py",
            "contract": "valid_worker_receipt_exit_0_transport_or_contract_failure_exit_2",
        },
    ]
    cli_rows = value["cli_exit_consumers"]
    if cli_rows != expected_cli:
        raise ProgrammeAdmissionError("g1a_cli_consumer_inventory_invalid")
    integration_rows = value["integration_consumers"]
    if integration_rows != [
        {
            "id": "worktree_integration_recording",
            "path": "scripts/agent_worktrees.py",
            "symbol": "record_integration",
            "risk": "free_text_result_must_not_convert_revision_required_to_integration_authority",
            "disposition": "defer_to_separate_pure_adapter_subtranche",
        }
    ]:
        raise ProgrammeAdmissionError("g1a_integration_consumer_inventory_invalid")
    if value["excluded_consumers"] != [
        {
            "id": "evidence_gate_diagnostic_and_command_admission",
            "path": "scripts/ariadne_evidence_gate.py",
            "disposition": "out_of_g1a_verdict_kernel",
            "rationale": "owns diagnostic and command-result admission vocabulary, not external review verdict or integration authority",
        },
        {
            "id": "worktree_integration_mutator",
            "path": "scripts/agent_worktrees.py",
            "disposition": "later_separate_subtranche",
            "rationale": "integration mutation is outside the first immutable G1A verdict-kernel tranche",
        },
    ]:
        raise ProgrammeAdmissionError("g1a_excluded_consumer_inventory_invalid")


def _python_symbol_hashes(payload: bytes) -> dict[str, str]:
    try:
        source = payload.decode("utf-8").replace("\r\n", "\n")
        tree = ast.parse(source)
    except (UnicodeDecodeError, SyntaxError) as error:
        raise ProgrammeAdmissionError("g1a_provider_contract_source_invalid") from error
    hashes: dict[str, str] = {}
    for node in tree.body:
        name = getattr(node, "name", None)
        if isinstance(name, str):
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise ProgrammeAdmissionError("g1a_provider_contract_source_invalid")
            hashes[name] = "sha256:" + hashlib.sha256(segment.encode()).hexdigest()
    return hashes


def _protected_module_ast_hash(payload: bytes, allowed_symbols: set[str]) -> str:
    try:
        source = payload.decode("utf-8").replace("\r\n", "\n")
        tree = ast.parse(source)
    except (UnicodeDecodeError, SyntaxError) as error:
        raise ProgrammeAdmissionError("g1a_provider_contract_source_invalid") from error
    tree.body = [
        ast.Pass() if getattr(node, "name", None) in allowed_symbols else node
        for node in tree.body
    ]
    canonical = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def _runtime_faithful_python_module_ast(payload: bytes) -> ast.Module:
    """Parse original source bytes exactly as Python would, without executing them."""
    try:
        tree = compile(
            payload,
            "<g1a3-integration-consumer>",
            "exec",
            flags=ast.PyCF_ONLY_AST | ast.PyCF_TYPE_COMMENTS,
            dont_inherit=True,
        )
    except (SyntaxError, UnicodeError, ValueError) as error:
        raise ProgrammeAdmissionError(
            "g1a_3_integration_contract_source_invalid"
        ) from error
    if not isinstance(tree, ast.Module):
        raise ProgrammeAdmissionError("g1a_3_integration_contract_source_invalid")
    return tree


def _protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
    payload: bytes, allowed_symbols: set[str]
) -> str:
    """Hash runtime-faithful source while excluding one synchronous function body."""
    if len(allowed_symbols) != 1:
        raise ProgrammeAdmissionError("g1a_3_allowed_function_inventory_invalid")
    tree = _runtime_faithful_python_module_ast(payload)

    allowed_symbol = next(iter(allowed_symbols))
    matches = [
        node for node in tree.body if getattr(node, "name", None) == allowed_symbol
    ]
    if len(matches) != 1:
        raise ProgrammeAdmissionError("g1a_3_allowed_function_count_invalid")
    function = matches[0]
    if not isinstance(function, ast.FunctionDef):
        raise ProgrammeAdmissionError("g1a_3_allowed_function_kind_invalid")

    function.body = [ast.Pass()]
    canonical = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


def _validate_g1a_scope(value: dict[str, Any], root: Path) -> None:
    _exact_keys(
        value,
        {
            "schema_version",
            "status",
            "prepared_at",
            "inventory_source_commit",
            "active_subgate_after_g0_transition",
            "transition_opens_only",
            "objective",
            "subgates",
            "excluded_consumers",
        },
        "g1a_scope_schema_invalid",
    )
    if (
        value["schema_version"] != "raisa-ariadne.g1a-verdict-integration-scope.v3"
        or value["status"] != "g1a3_transition_enablement_review_pending"
        or value["inventory_source_commit"]
        != "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b"
        or value["active_subgate_after_g0_transition"] != TRANSITION_TO_GATE
        or value["transition_opens_only"] != TRANSITION_TO_GATE
    ):
        raise ProgrammeAdmissionError("g1a_scope_not_exact")
    _bounded_text(value["prepared_at"], "g1a_scope_prepared_at_invalid", 64)
    _bounded_text(value["objective"], "g1a_scope_objective_invalid", 1000)
    subgates = value["subgates"]
    if not isinstance(subgates, dict) or list(subgates) != ["G1A.1", "G1A.2", "G1A.3"]:
        raise ProgrammeAdmissionError("g1a_subgate_inventory_invalid")

    common_keys = {
        "status",
        "task_class",
        "objective",
        "allowed_paths",
        "allowed_untracked_paths",
        "allowed_effects",
        "forbidden_effects",
    }
    g1a1 = _exact_keys(
        subgates["G1A.1"],
        common_keys | {"verdict_parsers", "review_callers", "cli_exit_consumers"},
        "g1a_1_scope_schema_invalid",
    )
    if (
        g1a1["status"] != "accepted_by_owner_with_residual_risk_frozen"
        or g1a1["task_class"] != G1A_TASK_CLASS
        or set(_unique_text_list(g1a1["allowed_paths"], "g1a_1_paths_invalid"))
        != G1A_ALLOWED_PATHS
        or set(
            _unique_text_list(
                g1a1["allowed_untracked_paths"], "g1a_1_untracked_paths_invalid"
            )
        )
        != G1A_ALLOWED_UNTRACKED_PATHS
        or set(_unique_text_list(g1a1["allowed_effects"], "g1a_1_effects_invalid"))
        != G1A_ALLOWED_EFFECTS
        or set(_unique_text_list(g1a1["forbidden_effects"], "g1a_1_forbidden_invalid"))
        != G1A_FORBIDDEN_EFFECTS
        or any("antigravity" in path for path in g1a1["allowed_paths"])
    ):
        raise ProgrammeAdmissionError("g1a_1_scope_not_exact")
    expected_g1a1_parsers = [
        {
            "id": "review_acceptance_table_parser",
            "path": "orchestration_harness/review_acceptance.py",
            "symbol": "_parse_artifact_marker",
            "disposition": "replace_with_canonical_parser",
        },
        {
            "id": "deepcode_terminal_marker_parser",
            "path": "orchestration_harness/deepcode_artifact.py",
            "symbol": "parse_artifact_marker",
            "disposition": "delegate_to_canonical_parser",
        },
    ]
    if g1a1["verdict_parsers"] != expected_g1a1_parsers:
        raise ProgrammeAdmissionError("g1a_1_parser_inventory_invalid")

    g1a2 = _exact_keys(
        subgates["G1A.2"],
        common_keys
        | {
            "allowed_mutation_symbols",
            "immutable_provider_contract",
            "verdict_parsers",
            "review_callers",
            "cli_exit_consumers",
        },
        "g1a_2_scope_schema_invalid",
    )
    g1a2_effects = {
        "repository_read",
        "provider_verdict_adapter_edit",
        "task_branch_commit",
        "task_branch_push",
        "external_review_preparation",
    }
    allowed_symbols = set(
        _unique_text_list(
            g1a2["allowed_mutation_symbols"], "g1a_2_mutation_symbols_invalid"
        )
    )
    if (
        g1a2["status"] != "external_review_passed_frozen"
        or g1a2["task_class"] != G1A2_TASK_CLASS
        or set(_unique_text_list(g1a2["allowed_paths"], "g1a_2_paths_invalid"))
        != G1A2_ALLOWED_PATHS
        or g1a2["allowed_untracked_paths"] != []
        or set(_unique_text_list(g1a2["allowed_effects"], "g1a_2_effects_invalid"))
        != g1a2_effects
        or set(_unique_text_list(g1a2["forbidden_effects"], "g1a_2_forbidden_invalid"))
        != G1A_FORBIDDEN_EFFECTS
        or allowed_symbols
        != {
            "structured_decision_schema",
            "_as_structured_decision",
            "parse_structured_decision",
        }
    ):
        raise ProgrammeAdmissionError("g1a_2_scope_not_exact")
    contract = _exact_keys(
        g1a2["immutable_provider_contract"],
        {
            "path",
            "source_commit",
            "hash_semantics",
            "protected_ast_sha256",
            "protected_symbols",
        },
        "g1a_2_provider_contract_schema_invalid",
    )
    if (
        contract["path"] != "scripts/ariadne_antigravity.py"
        or contract["source_commit"] != value["inventory_source_commit"]
        or contract["hash_semantics"]
        != "sha256_of_ast_dump_with_allowed_mutation_symbols_replaced_by_pass"
    ):
        raise ProgrammeAdmissionError("g1a_2_provider_contract_invalid")
    source_payload = _git_object_bytes(
        root, f"{contract['source_commit']}:{contract['path']}"
    )
    if contract["protected_ast_sha256"] != _protected_module_ast_hash(
        source_payload, allowed_symbols
    ):
        raise ProgrammeAdmissionError("g1a_2_provider_ast_digest_invalid")
    symbol_hashes = _python_symbol_hashes(source_payload)
    expected_protected_symbols = {
        "WorktreeState",
        "_git",
        "inspect_worktree",
        "build_command",
        "admit_orchestrator_receipt",
        "_atomic_receipt_write",
        "_output_evidence",
        "run_worker",
        "main",
    }
    if (
        not isinstance(contract["protected_symbols"], dict)
        or set(contract["protected_symbols"]) != expected_protected_symbols
        or any(
            contract["protected_symbols"][name] != symbol_hashes.get(name)
            for name in expected_protected_symbols
        )
    ):
        raise ProgrammeAdmissionError("g1a_2_provider_symbol_digest_invalid")

    g1a3 = _exact_keys(
        subgates["G1A.3"],
        common_keys
        | {
            "allowed_mutation_symbols",
            "immutable_integration_consumer_contract",
            "record_integration_contract",
            "integration_consumers",
        },
        "g1a_3_scope_schema_invalid",
    )
    g1a3_symbols = set(
        _unique_text_list(
            g1a3["allowed_mutation_symbols"], "g1a_3_mutation_symbols_invalid"
        )
    )
    if (
        g1a3["status"]
        != "closed_pending_transition_enablement_external_review_and_state_transition"
        or g1a3["task_class"] != G1A3_TASK_CLASS
        or set(_unique_text_list(g1a3["allowed_paths"], "g1a_3_paths_invalid"))
        != G1A3_ALLOWED_PATHS
        or g1a3["allowed_untracked_paths"] != []
        or set(_unique_text_list(g1a3["allowed_effects"], "g1a_3_effects_invalid"))
        != G1A3_ALLOWED_EFFECTS
        or set(_unique_text_list(g1a3["forbidden_effects"], "g1a_3_forbidden_invalid"))
        != G1A_FORBIDDEN_EFFECTS
        or g1a3_symbols != {"record_integration"}
    ):
        raise ProgrammeAdmissionError("g1a_3_scope_not_exact")
    integration_contract = _exact_keys(
        g1a3["immutable_integration_consumer_contract"],
        {
            "path",
            "source_commit",
            "source_blob",
            "hash_semantics",
            "runtime_source_parsing_contract",
            "protected_ast_sha256",
            "protected_symbols",
        },
        "g1a_3_integration_contract_schema_invalid",
    )
    if (
        integration_contract["path"] != "scripts/agent_worktrees.py"
        or integration_contract["source_commit"]
        != "37e2d6f51ebbdb281771f922a5f460fd23e2571b"
        or integration_contract["source_blob"]
        != "f15d13f60c2c93edef0559b7b30b536b334bb884"
        or integration_contract["hash_semantics"]
        != "sha256_of_ast_dump_with_only_allowed_function_bodies_replaced_by_pass"
        or integration_contract["runtime_source_parsing_contract"]
        != G1A3_RUNTIME_SOURCE_PARSING_CONTRACT
        or _run_git(
            root,
            "rev-parse",
            f"{integration_contract['source_commit']}:{integration_contract['path']}",
        )
        != integration_contract["source_blob"]
    ):
        raise ProgrammeAdmissionError("g1a_3_integration_contract_invalid")
    integration_source = _git_object_bytes(
        root,
        f"{integration_contract['source_commit']}:{integration_contract['path']}",
    )
    if integration_contract["protected_ast_sha256"] != (
        _protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            integration_source, g1a3_symbols
        )
    ):
        raise ProgrammeAdmissionError("g1a_3_integration_ast_digest_invalid")
    integration_symbol_hashes = _python_symbol_hashes(integration_source)
    expected_integration_symbols = {
        "_require_command_admission",
        "append_integration_log",
        "build_parser",
        "main",
        "run_git",
        "push_handoff_refs",
        "handoff",
        "sync",
        "realign",
        "submit",
        "dispatch",
        "ensure_integration_log",
        "integration_log_records",
    }
    if (
        not isinstance(integration_contract["protected_symbols"], dict)
        or set(integration_contract["protected_symbols"])
        != expected_integration_symbols
        or any(
            integration_contract["protected_symbols"][name]
            != integration_symbol_hashes.get(name)
            for name in expected_integration_symbols
        )
    ):
        raise ProgrammeAdmissionError("g1a_3_integration_symbol_digest_invalid")
    expected_record_contract = {
        "review_argument": "immutable_canonical_G1A2_worker_receipt_path",
        "parser": "strict_json_with_duplicate_key_rejection",
        "receipt_schema": "ariadne.worker_receipt.v1",
        "required_status": "completed",
        "required_decision_contract": "schema_constrained_json_v1",
        "legacy_text_receipts": "reject",
        "verdict_authority": "recompute_canonical_verdict_locally",
        "required_pass_envelope": {
            "decision": "pass",
            "artifact_kind": "decision",
            "valid": True,
            "review_verdict": "pass",
            "artifact_integration_authority": True,
            "canonical_marker": "DECISION: PASS",
            "reason": "terminal_marker_observed",
        },
        "rejected_verdicts": [
            "revision_required",
            "malformed",
            "ambiguous",
            "mismatched",
        ],
        "branch_binding": "receipt_branch_equals_cli_branch",
        "integration_commit_binding": "full_commit_sha_and_head_before_equals_head_after_equals_integration_commit",
        "dirty_after": False,
        "command_results": "when_present_agree_with_canonical_envelope_and_top_level_fields",
        "receipt_digest": "sha256_exact_bytes_retained_in_integration_ledger",
        "ledger_result": "derived_from_validated_authority_not_user_supplied_result",
        "preserved_symbols": [
            "append_integration_log",
            "all_git_and_ref_mutating_helpers",
        ],
        "forbidden_git_effects": [
            "merge",
            "reset",
            "branch_movement",
            "protected_ref_update",
        ],
        "integration_entrypoint_during_implementation": "closed",
        "free_text_follow_up": "non_authoritative",
    }
    if g1a3["record_integration_contract"] != expected_record_contract:
        raise ProgrammeAdmissionError("g1a_3_record_integration_contract_invalid")
    if g1a3["integration_consumers"] != [
        {
            "id": "worktree_integration_recording",
            "path": "scripts/agent_worktrees.py",
            "symbol": "record_integration",
            "risk": "free_text_result_must_not_convert_revision_required_to_integration_authority",
            "disposition": "pre_reviewed_for_G1A3_implementation_only_integration_execution_closed",
        }
    ]:
        raise ProgrammeAdmissionError("g1a_3_integration_consumer_invalid")
    if value["excluded_consumers"] != [
        {
            "id": "evidence_gate_diagnostic_and_command_admission",
            "path": "scripts/ariadne_evidence_gate.py",
            "disposition": "out_of_g1a_verdict_kernel",
            "rationale": "owns diagnostic and command-result admission vocabulary, not external review verdict or integration authority",
        }
    ]:
        raise ProgrammeAdmissionError("g1a_excluded_consumer_inventory_invalid")


def g1a2_provider_contract_reasons(repo_root: Path) -> list[str]:
    """Check that only the pre-reviewed pure Antigravity adapter symbols changed."""
    root = repo_root.resolve()
    try:
        scope = _strict_yaml(root / G1A_SCOPE_PATH)
        _validate_g1a_scope(scope, root)
        g1a2 = scope["subgates"]["G1A.2"]
        contract = g1a2["immutable_provider_contract"]
        allowed_symbols = set(g1a2["allowed_mutation_symbols"])
        payload = (root / contract["path"]).read_bytes()
    except (ProgrammeAdmissionError, OSError):
        return ["g1a_2_provider_contract_unavailable"]
    reasons: list[str] = []
    if (
        _protected_module_ast_hash(payload, allowed_symbols)
        != contract["protected_ast_sha256"]
    ):
        reasons.append("g1a_2_nonadapter_provider_code_changed")
    symbol_hashes = _python_symbol_hashes(payload)
    if any(
        symbol_hashes.get(name) != digest
        for name, digest in contract["protected_symbols"].items()
    ):
        reasons.append("g1a_2_protected_provider_symbol_changed")
    return list(dict.fromkeys(reasons))


def g1a3_integration_contract_reasons(repo_root: Path) -> list[str]:
    """Check that only the record_integration body changed from frozen G1A.2."""
    root = repo_root.resolve()
    try:
        scope = _strict_yaml(root / G1A_SCOPE_PATH)
        _validate_g1a_scope(scope, root)
        g1a3 = scope["subgates"]["G1A.3"]
        contract = g1a3["immutable_integration_consumer_contract"]
        allowed_symbols = set(g1a3["allowed_mutation_symbols"])
        payload = (root / contract["path"]).read_bytes()
    except (ProgrammeAdmissionError, OSError):
        return ["g1a_3_integration_contract_unavailable"]
    try:
        protected_hash = _protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            payload, allowed_symbols
        )
        symbol_hashes = _python_symbol_hashes(payload)
    except ProgrammeAdmissionError:
        return ["g1a_3_allowed_function_body_contract_invalid"]
    reasons: list[str] = []
    if protected_hash != contract["protected_ast_sha256"]:
        reasons.append("g1a_3_nonconsumer_code_changed")
    if any(
        symbol_hashes.get(name) != digest
        for name, digest in contract["protected_symbols"].items()
    ):
        reasons.append("g1a_3_protected_integration_symbol_changed")
    return list(dict.fromkeys(reasons))


def _validate_overlay(
    value: dict[str, Any], state: dict[str, Any], root: Path
) -> list[str]:
    _exact_keys(
        value,
        {
            "schema_version",
            "status",
            "authority_owner",
            "recorded_at",
            "state_file",
            "gates_file",
            "risk_file",
            "inventory_file",
            "g1a_scope_file",
            "admission_command",
            "required_before",
            "missing_or_invalid_state",
            "active_profile",
            "profiles",
            "scope_policy",
            "transition_policy",
            "owner_disposition_policy",
            "subgate_transition_policy",
            "g1a3_transition_policy",
            "pinned_gatekeeper",
            "target_worktree_policy",
            "remote_identity_policy",
            "gated_entrypoints",
            "reversibility",
        },
        "recovery_overlay_schema_invalid",
    )
    if (
        value["schema_version"] != "ariadne.programme_recovery.v11"
        or value["status"] != "active_emergency_overlay"
        or value["authority_owner"] != "Yuri"
        or value["state_file"] != STATE_PATH.as_posix()
        or value["gates_file"] != GATES_PATH.as_posix()
        or value["risk_file"] != RISK_PATH.as_posix()
        or value["inventory_file"] != INVENTORY_PATH.as_posix()
        or value["g1a_scope_file"] != G1A_SCOPE_PATH.as_posix()
        or value["missing_or_invalid_state"] != "hard_stop"
    ):
        raise ProgrammeAdmissionError("recovery_overlay_header_invalid")
    if (
        set(
            _unique_text_list(
                value["required_before"], "recovery_required_before_invalid"
            )
        )
        != ENTRYPOINTS
    ):
        raise ProgrammeAdmissionError("recovery_entrypoint_coverage_incomplete")
    profiles = value["profiles"]
    if not isinstance(profiles, dict) or set(profiles) != {
        G0_CONTROLLER_PROFILE,
        TRANSITION_PROFILE,
        G1A_ACTIVE_PROFILE,
        SUBGATE_TRANSITION_PROFILE,
        G1A2_ACTIVE_PROFILE,
        G1A3_ENABLEMENT_PENDING_PROFILE,
        G1A3_TRANSITION_PROFILE,
        G1A3_ACTIVE_PROFILE,
    }:
        raise ProgrammeAdmissionError("recovery_profiles_invalid")
    expected = {
        G0_CONTROLLER_PROFILE: {
            "profile_kind": "controller_maintenance",
            "expected_current_gate": "G0",
            "expected_gate_status": "revision_required",
            "active_correction": ADMITTED_PROGRAMME_GATE,
            "programme_gate": ADMITTED_PROGRAMME_GATE,
            "task_class": ADMITTED_TASK_CLASS,
            "effects": ALLOWED_MAINTENANCE_EFFECTS,
            "forbidden": FORBIDDEN_EFFECTS,
            "behavior": "g0_controller_maintenance",
            "paths": G0_G08_ALLOWED_PATHS,
            "g1a": False,
        },
        TRANSITION_PROFILE: {
            "profile_kind": "state_transition",
            "expected_current_gate": TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": TRANSITION_TO_GATE,
            "programme_gate": "G0_TO_G1A.1",
            "task_class": TRANSITION_TASK_CLASS,
            "effects": ALLOWED_MAINTENANCE_EFFECTS
            | {"external_review_record", "transition_artifact"},
            "forbidden": TRANSITION_FORBIDDEN_EFFECTS,
            "behavior": "semantic_state_transition",
            "paths": TRANSITION_FIXED_ALLOWED_PATHS,
            "g1a": True,
        },
        G1A_ACTIVE_PROFILE: {
            "profile_kind": "active_gate",
            "expected_current_gate": TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": TRANSITION_TO_GATE,
            "programme_gate": TRANSITION_TO_GATE,
            "task_class": G1A_TASK_CLASS,
            "effects": G1A_ALLOWED_EFFECTS,
            "forbidden": G1A_FORBIDDEN_EFFECTS,
            "behavior": "g1a_bounded_repair",
            "paths": G1A_ALLOWED_PATHS,
            "g1a": True,
        },
        SUBGATE_TRANSITION_PROFILE: {
            "profile_kind": "state_transition",
            "expected_current_gate": SUBGATE_TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": SUBGATE_TRANSITION_TO_GATE,
            "programme_gate": "G1A.1_TO_G1A.2",
            "task_class": SUBGATE_TRANSITION_TASK_CLASS,
            "effects": ALLOWED_MAINTENANCE_EFFECTS
            | {"external_review_record", "transition_artifact"},
            "forbidden": TRANSITION_FORBIDDEN_EFFECTS,
            "behavior": "g1a_subgate_semantic_state_transition",
            "paths": SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS,
            "g1a": True,
        },
        G1A2_ACTIVE_PROFILE: {
            "profile_kind": "active_gate",
            "expected_current_gate": SUBGATE_TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": SUBGATE_TRANSITION_TO_GATE,
            "programme_gate": SUBGATE_TRANSITION_TO_GATE,
            "task_class": G1A2_TASK_CLASS,
            "effects": G1A2_ALLOWED_EFFECTS,
            "forbidden": G1A_FORBIDDEN_EFFECTS,
            "behavior": "g1a_bounded_provider_adapter",
            "paths": G1A2_ALLOWED_PATHS,
            "g1a": True,
        },
        G1A3_ENABLEMENT_PENDING_PROFILE: {
            "profile_kind": "review_pending_controller",
            "expected_current_gate": SUBGATE_TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": SUBGATE_TRANSITION_TO_GATE,
            "programme_gate": "G1A.3-E0",
            "task_classes": [],
            "effects": {"repository_read"},
            "forbidden": G1A_FORBIDDEN_EFFECTS,
            "behavior": "external_review_only_no_implementation",
            "paths": set(),
            "g1a": True,
        },
        G1A3_TRANSITION_PROFILE: {
            "profile_kind": "state_transition",
            "expected_current_gate": G1A3_TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": G1A3_TRANSITION_TO_GATE,
            "programme_gate": "G1A.2_TO_G1A.3",
            "task_class": G1A3_TRANSITION_TASK_CLASS,
            "effects": ALLOWED_MAINTENANCE_EFFECTS
            | {"external_review_record", "transition_artifact"},
            "forbidden": TRANSITION_FORBIDDEN_EFFECTS,
            "behavior": "g1a2_to_g1a3_semantic_state_transition",
            "paths": G1A3_TRANSITION_FIXED_ALLOWED_PATHS,
            "g1a": True,
        },
        G1A3_ACTIVE_PROFILE: {
            "profile_kind": "active_gate",
            "expected_current_gate": G1A3_TRANSITION_TO_GATE,
            "expected_gate_status": "active",
            "active_correction": G1A3_TRANSITION_TO_GATE,
            "programme_gate": G1A3_TRANSITION_TO_GATE,
            "task_class": G1A3_TASK_CLASS,
            "effects": G1A3_ALLOWED_EFFECTS,
            "forbidden": G1A_FORBIDDEN_EFFECTS,
            "behavior": "g1a_bounded_integration_authority_consumer",
            "paths": G1A3_ALLOWED_PATHS,
            "g1a": True,
        },
    }
    for name, spec in expected.items():
        row = _exact_keys(
            profiles[name], _PROFILE_KEYS, "recovery_profile_schema_invalid"
        )
        profile_paths = row["allowed_paths"]
        if (
            not isinstance(profile_paths, list)
            or any(not isinstance(path, str) or not path for path in profile_paths)
            or len(profile_paths) != len(set(profile_paths))
        ):
            raise ProgrammeAdmissionError("profile_paths_invalid")
        if (
            row["profile_kind"] != spec["profile_kind"]
            or row["expected_programme_mode"] != "recovery"
            or row["expected_current_gate"] != spec["expected_current_gate"]
            or row["expected_gate_status"] != spec["expected_gate_status"]
            or row["active_correction"] != spec["active_correction"]
            or row["programme_gate"] != spec["programme_gate"]
            or row["admitted_task_classes"]
            != spec.get("task_classes", [spec.get("task_class")])
            or set(_unique_text_list(row["allowed_effects"], "profile_effects_invalid"))
            != spec["effects"]
            or set(
                _unique_text_list(row["forbidden_effects"], "profile_forbidden_invalid")
            )
            != spec["forbidden"]
            or set(
                _unique_text_list(
                    row["closed_entrypoints"], "profile_entrypoints_invalid"
                )
            )
            != ENTRYPOINTS_CLOSED_IN_G0
            or row["scope_behavior"] != spec["behavior"]
            or set(profile_paths) != spec["paths"]
            or row["autonomous_task_selection"] is not False
            or row["out_of_gate_result"] != "blocked"
            or any(
                row[key] is not False
                for key in (
                    "feature_work_eligible",
                    "product_work_eligible",
                    "provider_calls_eligible",
                    "deployment_eligible",
                    "protected_ref_movement_eligible",
                )
            )
            or row["g1a_eligible"] is not spec["g1a"]
        ):
            raise ProgrammeAdmissionError("recovery_profile_not_exact")
    active_profile = value["active_profile"]
    if active_profile != state["active_profile"] or active_profile not in {
        G0_CONTROLLER_PROFILE,
        G1A_ACTIVE_PROFILE,
        G1A2_ACTIVE_PROFILE,
        G1A3_ENABLEMENT_PENDING_PROFILE,
        G1A3_ACTIVE_PROFILE,
    }:
        raise ProgrammeAdmissionError("recovery_active_profile_invalid")
    active = profiles[active_profile]
    if (
        active["expected_programme_mode"] != state["programme_mode"]
        or active["expected_current_gate"] != state["current_gate"]
        or active["expected_gate_status"] != state["current_gate_status"]
        or active["active_correction"] != state["active_correction"]
    ):
        raise ProgrammeAdmissionError("recovery_profile_state_disagreement")
    scope = _exact_keys(
        value["scope_policy"],
        {
            "expected_branch",
            "frozen_recovery_base",
            "authorized_parent_commit",
            "candidate_commit_limit",
            "allowed_paths",
        },
        "scope_policy_schema_invalid",
    )
    if (
        scope["expected_branch"] != state["recovery_baton"]["branch"]
        or scope["frozen_recovery_base"] != state["recovery_baton"]["base_sha"]
        or scope["authorized_parent_commit"]
        != state["g0_8_correction"]["authorized_parent_commit"]
        or scope["candidate_commit_limit"] != 1
        or set(_unique_text_list(scope["allowed_paths"], "scope_allowed_paths_invalid"))
        != G0_G08_ALLOWED_PATHS
    ):
        raise ProgrammeAdmissionError("scope_policy_state_disagreement")
    allowed_paths = active["allowed_paths"]
    if (
        not isinstance(allowed_paths, list)
        or any(not isinstance(path, str) or not path for path in allowed_paths)
        or len(allowed_paths) != len(set(allowed_paths))
    ):
        raise ProgrammeAdmissionError("scope_allowed_paths_invalid")
    for raw in allowed_paths:
        path = PurePosixPath(raw)
        if (
            path.is_absolute()
            or "\\" in raw
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise ProgrammeAdmissionError("scope_allowed_path_invalid")
    entrypoints = value["gated_entrypoints"]
    if not isinstance(entrypoints, list) or not entrypoints:
        raise ProgrammeAdmissionError("gated_entrypoint_inventory_invalid")
    observed: set[str] = set()
    observed_ids: set[str] = set()
    for item in entrypoints:
        row = _exact_keys(
            item, {"id", "path", "entrypoint"}, "gated_entrypoint_schema_invalid"
        )
        if row["entrypoint"] not in ENTRYPOINTS or row["id"] in observed_ids:
            raise ProgrammeAdmissionError("gated_entrypoint_inventory_invalid")
        observed.add(row["entrypoint"])
        observed_ids.add(row["id"])
        if (
            row["path"] not in G0_G08_ALLOWED_PATHS
            or not (root / row["path"]).is_file()
        ):
            raise ProgrammeAdmissionError("gated_entrypoint_path_invalid")
    if observed != ENTRYPOINTS:
        raise ProgrammeAdmissionError("recovery_entrypoint_coverage_incomplete")
    gatekeeper = _exact_keys(
        value["pinned_gatekeeper"],
        {
            "schema_version",
            "module",
            "bootstrap",
            "cli",
            "operation_cli_module",
            "canonical_operations",
            "operation_receipt_schema",
            "source_binding",
            "clean_source_required",
            "target_is_data_only",
            "candidate_controller_execution_forbidden",
            "combined_operation_only",
            "receipt_sink_schema",
            "receipt_argument",
            "receipt_directory_policy",
            "receipt_reservation_policy",
            "operation_binding_fields",
        },
        "pinned_gatekeeper_policy_schema_invalid",
    )
    if gatekeeper != {
        "schema_version": "ariadne.pinned_programme_gatekeeper_policy.v7",
        "module": "orchestration_harness/pinned_programme_gatekeeper.py",
        "bootstrap": "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
        "cli": "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
        "operation_cli_module": "scripts/raisa_ariadne_pinned_gatekeeper.py",
        "canonical_operations": ["evaluate", "commit", "push"],
        "operation_receipt_schema": "ariadne.pinned_programme_operation_receipt.v1",
        "source_binding": "expected_commit_tree_plus_trusted_physical_source_bytes_and_fsmonitor_closed_configuration",
        "clean_source_required": True,
        "target_is_data_only": True,
        "candidate_controller_execution_forbidden": True,
        "combined_operation_only": True,
        "receipt_sink_schema": "ariadne.pinned_receipt_sink.v1",
        "receipt_argument": "preexisting_external_directory_only",
        "receipt_directory_policy": "outside_source_target_git_common_and_preservation_roots_no_reparse_or_alias",
        "receipt_reservation_policy": "internal_name_exclusive_create_identity_stable_no_overwrite_fsync_where_supported",
        "operation_binding_fields": [
            "target_head",
            "index_tree",
            "changed_paths_digest",
            "filesystem_inventory_digest",
            "git_administrative_identity_sha256",
            "trusted_git_identity_sha256",
            "source_trusted_git_identity_sha256",
            "expected_origin_head",
            "remote_identity_sha256",
            "explicit_destination",
            "receipt_sink",
        ],
    }:
        raise ProgrammeAdmissionError("pinned_gatekeeper_policy_invalid")
    target_policy = _exact_keys(
        value["target_worktree_policy"],
        {
            "schema_version",
            "preserved_legacy_worktree",
            "preserved_legacy_worktree_forbidden_as_gatekeeper",
            "preserved_legacy_worktree_forbidden_as_target",
            "separate_clean_target_required",
            "activation_untracked_count_required",
            "development_allowed_untracked_paths",
            "g1a2_development_allowed_untracked_paths",
            "pre_push_untracked_count_required",
            "post_push_untracked_count_required",
            "root_import_hooks_forbidden",
            "nonregular_reparse_symlink_and_junction_forbidden",
            "ignored_and_untracked_inventory_required",
            "protected_path_aliases_forbidden",
            "inventory_command",
            "git_administrative_entry",
            "git_administrative_policy",
        },
        "target_worktree_policy_schema_invalid",
    )
    if (
        target_policy["schema_version"] != "ariadne.g1a_target_worktree_policy.v3"
        or target_policy["preserved_legacy_worktree"]
        != state["repository_inventory"].get("preserved_legacy_worktree")
        or target_policy["preserved_legacy_worktree_forbidden_as_gatekeeper"]
        is not True
        or target_policy["preserved_legacy_worktree_forbidden_as_target"] is not True
        or target_policy["separate_clean_target_required"] is not True
        or target_policy["activation_untracked_count_required"] != 0
        or set(
            _unique_text_list(
                target_policy["development_allowed_untracked_paths"],
                "target_development_untracked_paths_invalid",
            )
        )
        != G1A_ALLOWED_UNTRACKED_PATHS
        or target_policy["g1a2_development_allowed_untracked_paths"] != []
        or target_policy["pre_push_untracked_count_required"] != 0
        or target_policy["post_push_untracked_count_required"] != 0
        or target_policy["root_import_hooks_forbidden"]
        != ["sitecustomize.py", "usercustomize.py", "*.pth"]
        or target_policy["nonregular_reparse_symlink_and_junction_forbidden"]
        is not True
        or target_policy["ignored_and_untracked_inventory_required"] is not True
        or target_policy["protected_path_aliases_forbidden"] is not True
        or target_policy["inventory_command"]
        != "git ls-files --others --exclude-standard -z plus git ls-files --others --ignored --exclude-standard -z"
        or target_policy["git_administrative_entry"] != ".git"
        or target_policy["git_administrative_policy"]
        != "head_index_objects_refs_bound_info_excludes_neutralized_non_sample_hooks_and_core_hooks_path_forbidden"
    ):
        raise ProgrammeAdmissionError("target_worktree_policy_invalid")
    _validate_remote_identity_policy(value["remote_identity_policy"])
    transition = _exact_keys(
        value["transition_policy"],
        {
            "manifest_schema_version",
            "task_class",
            "from_gate",
            "to_gate",
            "transition_status",
            "external_review_record_root",
            "transition_artifact_root",
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
        or transition["transition_status"] != "complete"
        or transition["external_review_record_root"] != TRANSITION_REVIEW_ROOT
        or transition["transition_artifact_root"] != TRANSITION_ARTIFACT_ROOT
        or transition["candidate_commit_limit"] != 1
        or set(
            _unique_text_list(
                transition["fixed_allowed_paths"], "transition_fixed_paths_invalid"
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
    owner_policy = _exact_keys(
        value["owner_disposition_policy"],
        {
            "schema_version",
            "record_schema_version",
            "record_root",
            "current_disposition_id",
            "current_record_path",
            "subject_gate",
            "subject_commit",
            "subject_tree",
            "accepted_decisions",
            "append_only",
            "external_review_separation_required",
            "missing_malformed_rewritten_or_contradictory",
        },
        "owner_disposition_policy_schema_invalid",
    )
    if owner_policy != {
        "schema_version": "ariadne.owner_disposition_policy.v1",
        "record_schema_version": "ariadne.owner_subgate_disposition.v1",
        "record_root": OWNER_DISPOSITION_ROOT,
        "current_disposition_id": OWNER_DISPOSITION_ID,
        "current_record_path": OWNER_DISPOSITION_PATH,
        "subject_gate": "G1A.1",
        "subject_commit": "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b",
        "subject_tree": "24b92d586061901e7574d511105b21ea66d97f7e",
        "accepted_decisions": ["ACCEPT_WITH_RESIDUAL_RISK"],
        "append_only": True,
        "external_review_separation_required": True,
        "missing_malformed_rewritten_or_contradictory": "hard_stop",
    }:
        raise ProgrammeAdmissionError("owner_disposition_policy_invalid")
    subgate_transition = _exact_keys(
        value["subgate_transition_policy"],
        {
            "manifest_schema_version",
            "task_class",
            "transition_profile",
            "resulting_active_profile",
            "from_gate",
            "to_gate",
            "transition_status",
            "owner_disposition_record_root",
            "external_review_record_root",
            "transition_artifact_root",
            "external_review_schema_version",
            "transition_artifact_schema_version",
            "candidate_commit_limit",
            "fixed_allowed_paths",
            "forbidden_effect_classes",
        },
        "subgate_transition_policy_schema_invalid",
    )
    if (
        subgate_transition["manifest_schema_version"]
        != SUBGATE_TRANSITION_MANIFEST_VERSION
        or subgate_transition["task_class"] != SUBGATE_TRANSITION_TASK_CLASS
        or subgate_transition["transition_profile"] != SUBGATE_TRANSITION_PROFILE
        or subgate_transition["resulting_active_profile"] != G1A2_ACTIVE_PROFILE
        or subgate_transition["from_gate"] != SUBGATE_TRANSITION_FROM_GATE
        or subgate_transition["to_gate"] != SUBGATE_TRANSITION_TO_GATE
        or subgate_transition["transition_status"]
        != (
            "complete"
            if state["active_profile"]
            in {
                G1A2_ACTIVE_PROFILE,
                G1A3_ENABLEMENT_PENDING_PROFILE,
                G1A3_ACTIVE_PROFILE,
            }
            else "not_started"
        )
        or subgate_transition["owner_disposition_record_root"] != OWNER_DISPOSITION_ROOT
        or subgate_transition["external_review_record_root"] != SUBGATE_REVIEW_ROOT
        or subgate_transition["transition_artifact_root"]
        != SUBGATE_TRANSITION_ARTIFACT_ROOT
        or subgate_transition["external_review_schema_version"]
        != "ariadne.external_subgate_review.v1"
        or subgate_transition["transition_artifact_schema_version"]
        != "ariadne.g1a1-to-g1a2-transition.v1"
        or subgate_transition["candidate_commit_limit"] != 1
        or set(
            _unique_text_list(
                subgate_transition["fixed_allowed_paths"],
                "subgate_transition_fixed_paths_invalid",
            )
        )
        != SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS
        or set(
            _unique_text_list(
                subgate_transition["forbidden_effect_classes"],
                "subgate_transition_forbidden_effects_invalid",
            )
        )
        != TRANSITION_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("subgate_transition_policy_invalid")
    g1a3_transition = _exact_keys(
        value["g1a3_transition_policy"],
        {
            "manifest_schema_version",
            "task_class",
            "transition_profile",
            "resulting_active_profile",
            "from_gate",
            "to_gate",
            "transition_status",
            "implementation_review_record_root",
            "implementation_review_schema_version",
            "external_review_record_root",
            "external_review_schema_version",
            "transition_artifact_root",
            "transition_artifact_schema_version",
            "candidate_commit_limit",
            "fixed_allowed_paths",
            "forbidden_effect_classes",
        },
        "g1a3_transition_policy_schema_invalid",
    )
    expected_g1a3_transition_status = (
        "complete"
        if state["active_profile"] == G1A3_ACTIVE_PROFILE
        else "review_pending"
    )
    if (
        g1a3_transition["manifest_schema_version"] != G1A3_TRANSITION_MANIFEST_VERSION
        or g1a3_transition["task_class"] != G1A3_TRANSITION_TASK_CLASS
        or g1a3_transition["transition_profile"] != G1A3_TRANSITION_PROFILE
        or g1a3_transition["resulting_active_profile"] != G1A3_ACTIVE_PROFILE
        or g1a3_transition["from_gate"] != G1A3_TRANSITION_FROM_GATE
        or g1a3_transition["to_gate"] != G1A3_TRANSITION_TO_GATE
        or g1a3_transition["transition_status"] != expected_g1a3_transition_status
        or g1a3_transition["implementation_review_record_root"]
        != SUBGATE_IMPLEMENTATION_REVIEW_ROOT
        or g1a3_transition["implementation_review_schema_version"]
        != "ariadne.external_subgate_implementation_review.v1"
        or g1a3_transition["external_review_record_root"] != G1A3_TRANSITION_REVIEW_ROOT
        or g1a3_transition["external_review_schema_version"]
        != "ariadne.external_g1a3_transition_enablement_review.v1"
        or g1a3_transition["transition_artifact_root"]
        != SUBGATE_TRANSITION_ARTIFACT_ROOT
        or g1a3_transition["transition_artifact_schema_version"]
        != "ariadne.g1a2-to-g1a3-transition.v1"
        or g1a3_transition["candidate_commit_limit"] != 1
        or set(
            _unique_text_list(
                g1a3_transition["fixed_allowed_paths"],
                "g1a3_transition_fixed_paths_invalid",
            )
        )
        != G1A3_TRANSITION_FIXED_ALLOWED_PATHS
        or set(
            _unique_text_list(
                g1a3_transition["forbidden_effect_classes"],
                "g1a3_transition_forbidden_effects_invalid",
            )
        )
        != TRANSITION_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("g1a3_transition_policy_invalid")
    reversibility = _exact_keys(
        value["reversibility"],
        {"removal_requires", "default_on_transition_error"},
        "recovery_reversibility_invalid",
    )
    if reversibility != {
        "removal_requires": "accepted_gate_transition_with_updated_current_state_and_tests",
        "default_on_transition_error": "hard_stop",
    }:
        raise ProgrammeAdmissionError("recovery_reversibility_invalid")
    return allowed_paths


def _validate_precedence(
    project: dict[str, Any],
    continuation: dict[str, Any],
    agents_text: str,
    state: dict[str, Any],
) -> None:
    _exact_keys(
        project,
        {
            "schema_version",
            "project_id",
            "master_authority",
            "allocation",
            "operating_model",
            "secure_sdlc",
            "direction_collaboration",
            "autonomous_continuation",
            "cost_controls",
        },
        "project_settings_schema_invalid",
    )
    _exact_keys(
        continuation,
        {
            "schema_version",
            "default_posture",
            "emergency_programme_overlay",
            "applies_when",
            "policy_decision",
            "standing_programme_authority",
            "architecture_strengthening_choice_policy",
            "failure_loop",
            "authority",
            "execution_limits",
            "pause_for_user_only_when",
            "must_not_pause_for",
            "evidence",
            "task_lifecycle",
            "resume_checkpoint",
            "document_metadata",
        },
        "continuation_settings_schema_invalid",
    )
    project_overlay = project.get("autonomous_continuation", {}).get(
        "emergency_overlay", {}
    )
    continuation_overlay = continuation.get("emergency_programme_overlay", {})
    if project_overlay != {
        "settings_file": "programme_recovery.yaml",
        "required": True,
        "precedence": "higher_than_standing_continuation",
        "missing_or_invalid": "hard_stop",
    } or continuation_overlay != {
        "status": "active",
        "settings_file": "programme_recovery.yaml",
        "precedence": "higher_than_default_posture_and_standing_programme_authority",
        "required_before_task_selection": True,
        "missing_or_invalid": "hard_stop",
    }:
        raise ProgrammeAdmissionError("recovery_precedence_invalid")
    phase_token = (
        f"Gate {ADMITTED_PROGRAMME_GATE} is the only authorised correction; G1A is"
        if state["active_correction"] == ADMITTED_PROGRAMME_GATE
        else (
            "Gate G1A.2 implementation is externally accepted. G1A.3 transition enablement"
            if state["active_profile"] == G1A3_ENABLEMENT_PENDING_PROFILE
            else (
                "Gate G1A.3 is active only for its bounded integration-authority consumer"
                if state["active_profile"] == G1A3_ACTIVE_PROFILE
                else (
                    "Gate G1A.2 is active only for its bounded verdict adapter; provider invocation"
                    if state["active_correction"] == SUBGATE_TRANSITION_TO_GATE
                    else "Gate G1A.1 is owner-accepted with residual risk; G1A.2"
                )
            )
        )
    )
    required_header = (
        "# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE",
        phase_token,
        "Missing, malformed, stale, or contradictory programme state is a hard stop.",
    )
    if not agents_text.startswith(required_header[0]) or any(
        token not in agents_text[:1200] for token in required_header[1:]
    ):
        raise ProgrammeAdmissionError("agents_recovery_precedence_missing")


def _validate_latch(
    value: dict[str, Any], current_fingerprint: str, state: dict[str, Any]
) -> None:
    from orchestration_harness.active_operation import validate_active_operation

    try:
        latch = validate_active_operation(value)
    except ValueError as error:
        if state.get("active_profile") == G1A3_ENABLEMENT_PENDING_PROFILE:
            reason = "g1a3_enablement_latch_invalid"
        elif state.get("active_profile") == G1A3_ACTIVE_PROFILE:
            reason = "g1a3_active_latch_invalid"
        else:
            reason = "active_operation_latch_invalid"
        raise ProgrammeAdmissionError(reason) from error
    if latch["checkpoint"]["settings_fingerprint"] != current_fingerprint:
        raise ProgrammeAdmissionError("active_operation_settings_fingerprint_invalid")
    if state["active_correction"] == TRANSITION_TO_GATE:
        if (
            latch["operation_id"] != "g1a2-transition-enablement-20260828-v1"
            or latch["status"] != "paused"
            or latch["resume_after_compaction"] is not False
            or latch["user_attention"]["required"] is not False
            or latch["terminal_response"]["permitted"] is not True
            or latch["source_head"] != "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b"
            or "Yuri Frusin" not in latch["authority_source"]
            or "external g1a.2 transition-enablement review only"
            not in latch["checkpoint"]["next_executable_stage"].lower()
        ):
            raise ProgrammeAdmissionError("g1a2_enablement_latch_invalid")
    elif state["active_profile"] == G1A3_ENABLEMENT_PENDING_PROFILE:
        if (
            latch["operation_id"]
            != "g1a3-transition-enablement-runtime-source-encoding-replacement-20260829-v1"
            or latch["status"] != "paused"
            or latch["resume_after_compaction"] is not False
            or latch["user_attention"]["required"] is not False
            or latch["terminal_response"]["permitted"] is not True
            or latch["source_head"] != "37e2d6f51ebbdb281771f922a5f460fd23e2571b"
            or "external g1a.3 transition-enablement review only"
            not in latch["checkpoint"]["next_executable_stage"].lower()
        ):
            raise ProgrammeAdmissionError("g1a3_enablement_latch_invalid")
    elif state["active_profile"] == G1A3_ACTIVE_PROFILE:
        transition = state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "state_transition"
        ]
        if (
            latch["operation_id"] != "g1a3-integration-consumer-mutation"
            or latch["status"] != "in_progress"
            or latch["resume_after_compaction"] is not True
            or latch["terminal_response"]["permitted"] is not False
            or latch["source_head"] != transition["enablement_controller_commit"]
            or "external" not in latch["authority_source"].lower()
        ):
            raise ProgrammeAdmissionError("g1a3_active_latch_invalid")
    elif state["active_correction"] == SUBGATE_TRANSITION_TO_GATE:
        transition = state["g1a_subgate_authority"]["subgates"]["G1A.2"][
            "state_transition"
        ]
        if (
            latch["operation_id"] != "g1a2-antigravity-verdict-adapter"
            or latch["status"] != "in_progress"
            or latch["resume_after_compaction"] is not True
            or latch["terminal_response"]["permitted"] is not False
            or latch["source_head"] != transition["enablement_controller_commit"]
            or "external" not in latch["authority_source"].lower()
        ):
            raise ProgrammeAdmissionError("g1a2_active_latch_invalid")
    elif (
        latch["status"] != "replaced"
        or latch["resume_after_compaction"] is not False
        or latch["checkpoint"]["next_executable_stage"] is not None
        or latch["terminal_response"]["permitted"] is not True
        or "Yuri" not in latch["authority_source"]
        or "G0" not in latch["authority_source"]
    ):
        raise ProgrammeAdmissionError("historical_latch_not_terminally_replaced")


def attest_programme_authority(repo_root: Path) -> dict[str, Any]:
    """Bind every authority input to the real index before parsing policy."""
    root = repo_root.resolve()
    try:
        dynamic_paths = trusted_git.indexed_paths_under(root, AUTHORITY_INDEX_ROOTS)
        return trusted_git.attest_repository(
            root,
            attested_paths={
                *(path.as_posix() for path in AUTHORITY_FIXED_PATHS),
                *dynamic_paths,
            },
        )
    except trusted_git.TrustedGitError as error:
        raise ProgrammeAdmissionError(error.reason_code) from error


@dataclass(frozen=True)
class ProgrammePolicy:
    state: dict[str, Any]
    gates: dict[str, Any]
    risks: dict[str, Any]
    inventory: dict[str, Any]
    g1a_scope: dict[str, Any]
    overlay: dict[str, Any]
    project: dict[str, Any]
    continuation: dict[str, Any]
    latch: dict[str, Any]
    state_digest: str
    policy_digest: str
    settings_fingerprint: str
    allowed_paths: tuple[str, ...]
    full_range_allowed_paths: tuple[str, ...]
    trusted_git_identity: dict[str, Any]


def load_programme_policy(repo_root: Path) -> ProgrammePolicy:
    """Strictly load and cross-check all controlling recovery inputs."""
    root = repo_root.resolve()
    trusted_git_identity = attest_programme_authority(root)
    state = _strict_json(root / STATE_PATH)
    gates = _strict_yaml(root / GATES_PATH)
    risks = _strict_yaml(root / RISK_PATH)
    inventory = _strict_yaml(root / INVENTORY_PATH)
    g1a_scope = _strict_yaml(root / G1A_SCOPE_PATH)
    overlay = _strict_yaml(root / OVERLAY_PATH)
    project = _strict_yaml(root / PROJECT_PATH)
    continuation = _strict_yaml(root / CONTINUATION_PATH)
    latch = _strict_json(root / LATCH_PATH)
    try:
        agents_text = (root / AGENTS_PATH).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ProgrammeAdmissionError("agents_handover_missing") from error
    _validate_state(state, root)
    _validate_gates(gates, state)
    _validate_risks(risks)
    _validate_inventory(inventory, state)
    _validate_g1a_scope(g1a_scope, root)
    allowed_paths = _validate_overlay(overlay, state, root)
    _validate_precedence(project, continuation, agents_text, state)
    from orchestration_harness.settings_fingerprint import settings_fingerprint

    settings_digest = settings_fingerprint(root / "orchestration/harness_settings")
    _validate_latch(latch, settings_digest, state)
    state_digest = _sha256_bytes((root / STATE_PATH).read_bytes())
    policy_digest = _digest_paths(
        root,
        (
            GATES_PATH,
            RISK_PATH,
            INVENTORY_PATH,
            G1A_SCOPE_PATH,
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
        g1a_scope=g1a_scope,
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
            else sorted(
                G0_G08_ALLOWED_PATHS
                | TRANSITION_FIXED_ALLOWED_PATHS
                | G1A_ALLOWED_PATHS
                | G1A2_ENABLEMENT_ALLOWED_PATHS
                | G1A3_ENABLEMENT_ALLOWED_PATHS
                | ACCEPTED_CUMULATIVE_HISTORY_PATHS
                | set(allowed_paths)
                | {
                    f"{TRANSITION_REVIEW_ROOT}/{state['gate_transition']['transition_id']}.json",
                    f"{TRANSITION_ARTIFACT_ROOT}/{state['gate_transition']['transition_id']}.json",
                    OWNER_DISPOSITION_PATH,
                }
                | (
                    {
                        f"{SUBGATE_REVIEW_ROOT}/{state['g1a_subgate_authority']['decisive_transition_enablement_review_id']}.json",
                        f"{SUBGATE_TRANSITION_ARTIFACT_ROOT}/{state['g1a_subgate_authority']['decisive_transition_enablement_review_id']}.json",
                    }
                    if state["g1a_subgate_authority"][
                        "decisive_transition_enablement_review_id"
                    ]
                    is not None
                    else set()
                )
                | (
                    {
                        f"{G1A3_TRANSITION_REVIEW_ROOT}/{state['g1a_subgate_authority']['decisive_g1a3_transition_enablement_review_id']}.json",
                        f"{SUBGATE_TRANSITION_ARTIFACT_ROOT}/{state['g1a_subgate_authority']['subgates']['G1A.3']['state_transition']['transition_id']}.json",
                    }
                    if state["active_profile"] == G1A3_ACTIVE_PROFILE
                    else set()
                )
            )
        ),
        trusted_git_identity=trusted_git_identity,
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
    index_tree: str | None = None
    changed_paths_digest: str | None = None
    expected_origin_head: str | None = None
    target_cleanliness: dict[str, Any] | None = None
    remote_identity: dict[str, Any] | None = None
    operation_binding: dict[str, Any] | None = None


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
    active_profile = policy.overlay["profiles"][policy.overlay["active_profile"]]
    task_class = manifest["task_class"]
    if (
        task_class not in active_profile["admitted_task_classes"]
        or task_class not in policy.state["task_selection"]["allowed_task_kinds"]
    ):
        raise ProgrammeAdmissionError("task_class_not_admitted")
    if manifest["programme_gate"] != active_profile["programme_gate"]:
        raise ProgrammeAdmissionError("task_gate_not_admitted")
    base = manifest["base_commit"]
    head = manifest["candidate_or_current_head"]
    if not isinstance(base, str) or _SHA1.fullmatch(base) is None:
        raise ProgrammeAdmissionError("task_manifest_base_invalid")
    if not isinstance(head, str) or _SHA1.fullmatch(head) is None:
        raise ProgrammeAdmissionError("task_manifest_head_invalid")
    if policy.state["active_correction"] == ADMITTED_PROGRAMME_GATE:
        expected_base = policy.state["g0_8_correction"]["authorized_parent_commit"]
    elif policy.state["active_profile"] == G1A3_ACTIVE_PROFILE:
        reviewed = policy.state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "state_transition"
        ]["enablement_controller_commit"]
        commits = _run_git(
            repo_root, "rev-list", "--reverse", f"{reviewed}..HEAD"
        ).splitlines()
        expected_base = commits[0] if commits else ""
    elif policy.state["active_correction"] == SUBGATE_TRANSITION_TO_GATE:
        reviewed = policy.state["g1a_subgate_authority"]["subgates"]["G1A.2"][
            "state_transition"
        ]["enablement_controller_commit"]
        commits = _run_git(
            repo_root, "rev-list", "--reverse", f"{reviewed}..HEAD"
        ).splitlines()
        expected_base = commits[0] if commits else ""
    else:
        reviewed = policy.state["gate_transition"]["reviewed_commit"]
        commits = _run_git(
            repo_root, "rev-list", "--reverse", f"{reviewed}..HEAD"
        ).splitlines()
        expected_base = commits[0] if commits else ""
    if base != expected_base:
        raise ProgrammeAdmissionError("task_manifest_base_stale")
    actual_head = _run_git(repo_root, "rev-parse", "HEAD")
    if head != actual_head:
        raise ProgrammeAdmissionError("task_manifest_head_stale")
    if manifest["state_digest"] != policy.state_digest:
        raise ProgrammeAdmissionError("task_manifest_state_digest_stale")
    if manifest["policy_digest"] != policy.policy_digest:
        raise ProgrammeAdmissionError("task_manifest_policy_digest_stale")
    paths = _unique_text_list(
        manifest["allowed_path_roots"], "task_manifest_paths_invalid"
    )
    if not set(paths).issubset(policy.allowed_paths):
        raise ProgrammeAdmissionError("task_manifest_path_outside_policy")
    if task_class == G1A2_TASK_CLASS and set(paths) != G1A2_ALLOWED_PATHS:
        raise ProgrammeAdmissionError("g1a_2_task_manifest_paths_not_exact")
    if task_class == G1A3_TASK_CLASS and set(paths) != G1A3_ALLOWED_PATHS:
        raise ProgrammeAdmissionError("g1a_3_task_manifest_paths_not_exact")
    intended = set(
        _unique_text_list(
            manifest["intended_side_effect_classes"],
            "task_manifest_intended_effects_invalid",
        )
    )
    forbidden = set(
        _unique_text_list(
            manifest["forbidden_side_effect_classes"],
            "task_manifest_forbidden_effects_invalid",
        )
    )
    allowed_effects = set(active_profile["allowed_effects"])
    if not intended.issubset(allowed_effects) or intended & forbidden:
        raise ProgrammeAdmissionError("task_manifest_effects_not_admitted")
    if forbidden != set(active_profile["forbidden_effects"]):
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
        if (
            not isinstance(manifest[field], str)
            or _SHA1.fullmatch(manifest[field]) is None
        ):
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
        if (
            not isinstance(manifest[field], str)
            or _SHA256.fullmatch(manifest[field]) is None
        ):
            raise ProgrammeAdmissionError(f"transition_{field}_invalid")
    review_path = f"{TRANSITION_REVIEW_ROOT}/{transition_id}.json"
    artifact_path = f"{TRANSITION_ARTIFACT_ROOT}/{transition_id}.json"
    allowed_paths = _unique_text_list(
        manifest["allowed_transition_paths"], "transition_allowed_paths_invalid"
    )
    expected_paths = TRANSITION_FIXED_ALLOWED_PATHS | {review_path, artifact_path}
    if set(allowed_paths) != expected_paths:
        raise ProgrammeAdmissionError("transition_allowed_paths_not_exact")
    if (
        set(
            _unique_text_list(
                manifest["forbidden_effect_classes"],
                "transition_forbidden_effects_invalid",
            )
        )
        != TRANSITION_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("transition_forbidden_effects_incomplete")
    if (
        policy.state["active_correction"] != TRANSITION_TO_GATE
        or policy.state["active_profile"] != G1A_ACTIVE_PROFILE
        or policy.overlay["active_profile"] != G1A_ACTIVE_PROFILE
    ):
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


def _validate_subgate_transition_manifest(
    value: object, *, policy: ProgrammePolicy
) -> tuple[dict[str, Any], list[str]]:
    manifest = _exact_keys(
        value,
        SUBGATE_TRANSITION_MANIFEST_KEYS,
        "subgate_transition_manifest_schema_invalid",
    )
    if manifest["schema_version"] != SUBGATE_TRANSITION_MANIFEST_VERSION:
        raise ProgrammeAdmissionError("subgate_transition_manifest_version_invalid")
    transition_id = _bounded_text(
        manifest["transition_id"], "subgate_transition_id_invalid", 128
    )
    if _IDENTIFIER.fullmatch(transition_id) is None:
        raise ProgrammeAdmissionError("subgate_transition_id_invalid")
    if (
        manifest["from_gate"] != SUBGATE_TRANSITION_FROM_GATE
        or manifest["to_gate"] != SUBGATE_TRANSITION_TO_GATE
    ):
        raise ProgrammeAdmissionError("subgate_transition_gate_invalid")
    for field in (
        "enablement_controller_commit",
        "enablement_controller_tree",
        "transition_parent",
    ):
        if (
            not isinstance(manifest[field], str)
            or _SHA1.fullmatch(manifest[field]) is None
        ):
            raise ProgrammeAdmissionError("subgate_transition_git_binding_invalid")
    if manifest["transition_parent"] != manifest["enablement_controller_commit"]:
        raise ProgrammeAdmissionError("subgate_transition_parent_invalid")
    for field in (
        "owner_disposition_record_sha256",
        "external_review_record_sha256",
        "state_digest_before",
        "policy_digest_before",
    ):
        if (
            not isinstance(manifest[field], str)
            or _SHA256.fullmatch(manifest[field]) is None
        ):
            raise ProgrammeAdmissionError(f"subgate_transition_{field}_invalid")
    if (
        manifest["owner_disposition_id"] != OWNER_DISPOSITION_ID
        or manifest["external_review_verdict"] != "PASS"
        or isinstance(manifest["blocking_finding_count"], bool)
        or manifest["blocking_finding_count"] != 0
    ):
        raise ProgrammeAdmissionError("subgate_transition_authority_invalid")
    _bounded_text(manifest["reviewer_surface"], "reviewer_surface_invalid", 256)
    review_path = f"{SUBGATE_REVIEW_ROOT}/{transition_id}.json"
    artifact_path = f"{SUBGATE_TRANSITION_ARTIFACT_ROOT}/{transition_id}.json"
    allowed_paths = _unique_text_list(
        manifest["allowed_transition_paths"],
        "subgate_transition_allowed_paths_invalid",
    )
    if set(allowed_paths) != SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS | {
        review_path,
        artifact_path,
    }:
        raise ProgrammeAdmissionError("subgate_transition_allowed_paths_not_exact")
    if (
        set(
            _unique_text_list(
                manifest["forbidden_effect_classes"],
                "subgate_transition_forbidden_effects_invalid",
            )
        )
        != TRANSITION_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("subgate_transition_forbidden_effects_incomplete")
    if (
        policy.state["active_correction"] != SUBGATE_TRANSITION_TO_GATE
        or policy.state["active_profile"] != G1A2_ACTIVE_PROFILE
        or policy.overlay["active_profile"] != G1A2_ACTIVE_PROFILE
    ):
        raise ProgrammeAdmissionError("subgate_transition_phase_not_active")
    authority = policy.state["g1a_subgate_authority"]
    g1a2_state = authority["subgates"]["G1A.2"]
    transition = g1a2_state["state_transition"]
    owner_entry = authority["owner_disposition_history"][0]
    review_entry = authority["external_review_history"][0]
    if (
        authority["decisive_transition_enablement_review_id"] != transition_id
        or transition["transition_id"] != transition_id
        or transition["enablement_controller_commit"]
        != manifest["enablement_controller_commit"]
        or transition["enablement_controller_tree"]
        != manifest["enablement_controller_tree"]
        or transition["owner_disposition_id"] != manifest["owner_disposition_id"]
        or transition["external_review_id"] != transition_id
        or transition["blocking_finding_count"] != manifest["blocking_finding_count"]
        or transition["reviewer_surface"] != manifest["reviewer_surface"]
        or owner_entry["record_sha256"] != manifest["owner_disposition_record_sha256"]
        or review_entry["review_record_sha256"]
        != manifest["external_review_record_sha256"]
        or review_entry["reviewed_commit"] != manifest["enablement_controller_commit"]
        or review_entry["reviewed_tree"] != manifest["enablement_controller_tree"]
    ):
        raise ProgrammeAdmissionError("subgate_transition_manifest_state_disagreement")
    return manifest, allowed_paths


def _validate_g1a3_transition_manifest(
    value: object, *, policy: ProgrammePolicy
) -> tuple[dict[str, Any], list[str]]:
    manifest = _exact_keys(
        value,
        G1A3_TRANSITION_MANIFEST_KEYS,
        "g1a3_transition_manifest_schema_invalid",
    )
    if manifest["schema_version"] != G1A3_TRANSITION_MANIFEST_VERSION:
        raise ProgrammeAdmissionError("g1a3_transition_manifest_version_invalid")
    transition_id = _bounded_text(
        manifest["transition_id"], "g1a3_transition_id_invalid", 128
    )
    if _IDENTIFIER.fullmatch(transition_id) is None:
        raise ProgrammeAdmissionError("g1a3_transition_id_invalid")
    if (
        manifest["from_gate"] != G1A3_TRANSITION_FROM_GATE
        or manifest["to_gate"] != G1A3_TRANSITION_TO_GATE
    ):
        raise ProgrammeAdmissionError("g1a3_transition_gate_invalid")
    for field in (
        "g1a2_implementation_commit",
        "g1a2_implementation_tree",
        "enablement_controller_commit",
        "enablement_controller_tree",
        "transition_parent",
    ):
        if (
            not isinstance(manifest[field], str)
            or _SHA1.fullmatch(manifest[field]) is None
        ):
            raise ProgrammeAdmissionError("g1a3_transition_git_binding_invalid")
    if manifest["transition_parent"] != manifest["enablement_controller_commit"]:
        raise ProgrammeAdmissionError("g1a3_transition_parent_invalid")
    for field in (
        "g1a2_implementation_review_record_sha256",
        "external_review_record_sha256",
        "state_digest_before",
        "policy_digest_before",
    ):
        if (
            not isinstance(manifest[field], str)
            or _SHA256.fullmatch(manifest[field]) is None
        ):
            raise ProgrammeAdmissionError(f"g1a3_transition_{field}_invalid")
    if (
        manifest["external_review_verdict"] != "PASS"
        or isinstance(manifest["blocking_finding_count"], bool)
        or manifest["blocking_finding_count"] != 0
    ):
        raise ProgrammeAdmissionError("g1a3_transition_authority_invalid")
    _bounded_text(manifest["reviewer_surface"], "reviewer_surface_invalid", 256)
    review_path = (
        f"{G1A3_TRANSITION_REVIEW_ROOT}/{manifest['enablement_review_id']}.json"
    )
    artifact_path = f"{SUBGATE_TRANSITION_ARTIFACT_ROOT}/{transition_id}.json"
    allowed_paths = _unique_text_list(
        manifest["allowed_transition_paths"],
        "g1a3_transition_allowed_paths_invalid",
    )
    if set(allowed_paths) != G1A3_TRANSITION_FIXED_ALLOWED_PATHS | {
        review_path,
        artifact_path,
    }:
        raise ProgrammeAdmissionError("g1a3_transition_allowed_paths_not_exact")
    if (
        set(
            _unique_text_list(
                manifest["forbidden_effect_classes"],
                "g1a3_transition_forbidden_effects_invalid",
            )
        )
        != TRANSITION_FORBIDDEN_EFFECTS
    ):
        raise ProgrammeAdmissionError("g1a3_transition_forbidden_effects_incomplete")
    if (
        policy.state["active_correction"] != G1A3_TRANSITION_TO_GATE
        or policy.state["active_profile"] != G1A3_ACTIVE_PROFILE
        or policy.overlay["active_profile"] != G1A3_ACTIVE_PROFILE
    ):
        raise ProgrammeAdmissionError("g1a3_transition_phase_not_active")
    authority = policy.state["g1a_subgate_authority"]
    g1a3_state = authority["subgates"]["G1A.3"]
    transition = g1a3_state["state_transition"]
    implementation_entry = authority["implementation_review_history"][0]
    review_entry = authority["g1a3_transition_enablement_review_history"][0]
    if (
        manifest["g1a2_implementation_review_id"]
        != authority["decisive_implementation_review_id"]
        or manifest["enablement_review_id"]
        != authority["decisive_g1a3_transition_enablement_review_id"]
        or transition["transition_id"] != transition_id
        or transition["enablement_controller_commit"]
        != manifest["enablement_controller_commit"]
        or transition["enablement_controller_tree"]
        != manifest["enablement_controller_tree"]
        or transition["external_review_id"] != manifest["enablement_review_id"]
        or transition["g1a2_implementation_review_id"]
        != manifest["g1a2_implementation_review_id"]
        or implementation_entry["reviewed_commit"]
        != manifest["g1a2_implementation_commit"]
        or implementation_entry["reviewed_tree"] != manifest["g1a2_implementation_tree"]
        or implementation_entry["review_record_sha256"]
        != manifest["g1a2_implementation_review_record_sha256"]
        or review_entry["review_id"] != manifest["enablement_review_id"]
        or review_entry["reviewed_commit"] != manifest["enablement_controller_commit"]
        or review_entry["reviewed_tree"] != manifest["enablement_controller_tree"]
        or review_entry["review_record_sha256"]
        != manifest["external_review_record_sha256"]
        or review_entry["blocking_finding_count"] != manifest["blocking_finding_count"]
        or review_entry["reviewer_surface"] != manifest["reviewer_surface"]
    ):
        raise ProgrammeAdmissionError("g1a3_transition_manifest_state_disagreement")
    return manifest, allowed_paths


def _manifest_task_class(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    if value.get("schema_version") == TRANSITION_MANIFEST_VERSION:
        return TRANSITION_TASK_CLASS
    if value.get("schema_version") == SUBGATE_TRANSITION_MANIFEST_VERSION:
        return SUBGATE_TRANSITION_TASK_CLASS
    if value.get("schema_version") == G1A3_TRANSITION_MANIFEST_VERSION:
        return G1A3_TRANSITION_TASK_CLASS
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
        return _decision(
            admitted=False, reasons=["entrypoint_unknown"], policy=None, task_class=None
        )
    try:
        policy = load_programme_policy(repo_root)
    except ProgrammeAdmissionError as error:
        return _decision(
            admitted=False, reasons=[error.reason_code], policy=None, task_class=None
        )
    if manifest is None:
        return _decision(
            admitted=False,
            reasons=["task_manifest_missing"],
            policy=policy,
            task_class=None,
        )
    active_profile = policy.overlay["profiles"][policy.overlay["active_profile"]]
    if entrypoint in set(active_profile["closed_entrypoints"]):
        return _decision(
            admitted=False,
            reasons=[f"{entrypoint}_closed_in_active_profile"],
            policy=policy,
            task_class=_manifest_task_class(manifest),
        )
    task_class = _manifest_task_class(manifest)
    try:
        if (
            isinstance(manifest, dict)
            and manifest.get("schema_version") == TRANSITION_MANIFEST_VERSION
        ):
            normalized, _ = _validate_transition_manifest(manifest, policy=policy)
            normalized_task_class = TRANSITION_TASK_CLASS
        elif (
            isinstance(manifest, dict)
            and manifest.get("schema_version") == SUBGATE_TRANSITION_MANIFEST_VERSION
        ):
            normalized, _ = _validate_subgate_transition_manifest(
                manifest, policy=policy
            )
            normalized_task_class = SUBGATE_TRANSITION_TASK_CLASS
        elif (
            isinstance(manifest, dict)
            and manifest.get("schema_version") == G1A3_TRANSITION_MANIFEST_VERSION
        ):
            normalized, _ = _validate_g1a3_transition_manifest(manifest, policy=policy)
            normalized_task_class = G1A3_TRANSITION_TASK_CLASS
        else:
            normalized, _ = _validate_manifest(
                manifest, policy=policy, repo_root=repo_root.resolve()
            )
            normalized_task_class = normalized["task_class"]
    except ProgrammeAdmissionError as error:
        return _decision(
            admitted=False,
            reasons=[error.reason_code],
            policy=policy,
            task_class=task_class,
        )
    if entrypoint in {"task_branch_commit", "task_branch_push"}:
        return _decision(
            admitted=False,
            reasons=["combined_operation_admission_required"],
            policy=policy,
            task_class=normalized_task_class,
        )
    if normalized_task_class not in {
        TRANSITION_TASK_CLASS,
        SUBGATE_TRANSITION_TASK_CLASS,
        G1A3_TRANSITION_TASK_CLASS,
    }:
        required_effect = ENTRYPOINT_REQUIRED_EFFECT[entrypoint]
        if required_effect not in normalized["intended_side_effect_classes"]:
            return _decision(
                admitted=False,
                reasons=["task_manifest_required_effect_missing"],
                policy=policy,
                task_class=normalized_task_class,
            )
    return _decision(
        admitted=True, reasons=[], policy=policy, task_class=normalized_task_class
    )


def _scope_change_inventories(
    root: Path, *, frozen_base: str, tranche_base: str, include_untracked: bool
) -> tuple[list[GitPathChange], list[GitPathChange], list[GitPathChange]]:
    working = git_change_inventory(root)
    staged = git_change_inventory(root, "--cached")
    untracked = git_untracked_inventory(root) if include_untracked else []
    full = [
        *git_change_inventory(root, f"{frozen_base}..HEAD"),
        *working,
        *staged,
        *untracked,
    ]
    tranche = [
        *git_change_inventory(root, f"{tranche_base}..HEAD"),
        *working,
        *staged,
        *untracked,
    ]
    return full, tranche, untracked


def _change_inventory_digest(
    *,
    full_changes: Sequence[GitPathChange],
    tranche_changes: Sequence[GitPathChange],
    untracked_changes: Sequence[GitPathChange],
) -> str:
    def rows(changes: Sequence[GitPathChange]) -> list[dict[str, str]]:
        unique = {(row.status, row.path, row.old_mode, row.new_mode) for row in changes}
        return [
            {
                "status": status,
                "path": path,
                "old_mode": old_mode,
                "new_mode": new_mode,
            }
            for status, path, old_mode, new_mode in sorted(unique)
        ]

    payload = {
        "full": rows(full_changes),
        "tranche": rows(tranche_changes),
        "untracked_and_ignored": rows(untracked_changes),
    }
    return _sha256_bytes(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    )


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


def _fresh_remote_head(root: Path, destination: str, branch: str) -> str | None:
    try:
        row = _run_git(
            root,
            "ls-remote",
            "--refs",
            destination,
            f"refs/heads/{branch}",
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


def _json_pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _semantic_pointers(before: object, after: object, pointer: str = "") -> set[str]:
    if type(before) is not type(after):
        return {pointer or "/"}
    if isinstance(before, dict):
        changed: set[str] = set()
        keys = set(before) | set(after)
        for key in keys:
            child = f"{pointer}/{_json_pointer_escape(str(key))}"
            if key not in before or key not in after:
                changed.add(child)
            else:
                changed.update(_semantic_pointers(before[key], after[key], child))
        return changed
    if isinstance(before, list):
        changed = set()
        for index in range(max(len(before), len(after))):
            child = f"{pointer}/{index}"
            if index >= len(before) or index >= len(after):
                changed.add(child)
            else:
                changed.update(_semantic_pointers(before[index], after[index], child))
        return changed
    return set() if before == after else {pointer or "/"}


_TRANSITION_STATE_POINTERS = {
    "/observed_at",
    "/current_gate",
    "/current_gate_status",
    "/active_correction",
    "/active_profile",
    "/task_selection/allowed_task_kinds/0",
    "/task_selection/next_eligible_tranche",
    "/task_selection/next_tranche_admission_requires_state_transition",
    "/task_selection/next_eligibility_condition",
    "/g0_acceptance/status",
    "/g0_acceptance/decisive_review_id",
    "/g0_acceptance/external_review_history/8",
    "/g0_acceptance/next_action",
    "/g0_8_correction/status",
    "/g0_8_correction/external_review_status",
    "/g0_8_correction/g1a_authorized",
    "/g0_8_correction/next_action",
    "/gate_transition",
}
_TRANSITION_GATES_POINTERS = {
    "/programme/prepared_at",
    "/programme/current_gate",
    "/programme/current_gate_status",
    "/programme/next_eligible_tranche",
    "/gates/0/status",
    "/gates/8/status",
    "/gates/9/status",
    "/gates/10/status",
}
_TRANSITION_OVERLAY_POINTERS = {"/active_profile"}
_TRANSITION_LATCH_POINTERS = {
    "/authority_source",
    "/checkpoint/settings_fingerprint",
}


def _transition_semantic_pointer_map(root: Path, reviewed: str) -> dict[str, list[str]]:
    pairs: tuple[tuple[Path, str], ...] = (
        (STATE_PATH, "json"),
        (GATES_PATH, "yaml"),
        (OVERLAY_PATH, "yaml"),
        (LATCH_PATH, "json"),
    )
    result: dict[str, list[str]] = {}
    for path, kind in pairs:
        before_payload = _git_object_bytes(root, f"{reviewed}:{path.as_posix()}")
        try:
            after_payload = (root / path).read_bytes()
        except OSError as error:
            raise ProgrammeAdmissionError(
                "transition_semantic_input_missing"
            ) from error
        if kind == "json":
            before = _strict_json_payload(
                before_payload, "transition_semantic_before_invalid"
            )
            after = _strict_json_payload(
                after_payload, "transition_semantic_after_invalid"
            )
        else:
            before = _strict_yaml_payload(
                before_payload, "transition_semantic_before_invalid"
            )
            after = _strict_yaml_payload(
                after_payload, "transition_semantic_after_invalid"
            )
        result[path.as_posix()] = sorted(_semantic_pointers(before, after))
    before_agents = _git_object_bytes(
        root, f"{reviewed}:{AGENTS_PATH.as_posix()}"
    ).replace(b"\r\n", b"\n")
    try:
        after_agents = (root / AGENTS_PATH).read_bytes().replace(b"\r\n", b"\n")
    except OSError as error:
        raise ProgrammeAdmissionError("transition_agents_missing") from error
    marker = b"# EMR4 Centaur \xe2\x80\x94 Live Agent Handover"
    if marker not in before_agents or marker not in after_agents:
        raise ProgrammeAdmissionError("transition_agents_marker_missing")
    before_header, before_body = before_agents.split(marker, 1)
    after_header, after_body = after_agents.split(marker, 1)
    if before_body != after_body:
        raise ProgrammeAdmissionError("transition_agents_body_changed")
    expected_before = (
        b"# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n\n"
        b"`orchestration/programme/current-state.json`, `orchestration/programme/gates.yaml`,\n"
        b"and the active recovery admission policy outrank the historical baton below while\n"
        b"the programme is in recovery. The older baton is evidence only and its named\n"
        b"successor must not resume. Gate G0.8 is the only authorised correction; G1A is\n"
        b"closed. Missing, malformed, stale, or contradictory programme state is a hard stop.\n\n"
    )
    expected_after = expected_before.replace(
        b"Gate G0.8 is the only authorised correction; G1A is\nclosed.",
        b"The reviewed G0 to G1A.1 transition is complete; Gate G1A.1 is active\nfor its bounded pure-verdict task only.",
    )
    if before_header != expected_before or after_header != expected_after:
        raise ProgrammeAdmissionError("transition_agents_header_not_exact")
    result[AGENTS_PATH.as_posix()] = (
        ["/emergency_header"] if before_header != after_header else []
    )
    return result


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
    remote_identity: dict[str, Any],
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
        G1A_SCOPE_PATH,
        OVERLAY_PATH,
        PROJECT_PATH,
        CONTINUATION_PATH,
        LATCH_PATH,
        AGENTS_PATH,
    )
    if (
        _digest_paths_at(root, reviewed, policy_paths)
        != manifest["policy_digest_before"]
    ):
        reasons.append("transition_policy_digest_before_mismatch")
    prior_state = _strict_json_payload(
        before_state_payload, "transition_prior_state_invalid"
    )
    prior_g08 = prior_state.get("g0_8_correction")
    if (
        prior_state.get("programme_mode") != "recovery"
        or prior_state.get("current_gate") != TRANSITION_FROM_GATE
        or prior_state.get("current_gate_status") != "revision_required"
        or prior_state.get("active_correction") != ADMITTED_PROGRAMME_GATE
        or prior_state.get("active_profile") != G0_CONTROLLER_PROFILE
        or not isinstance(prior_g08, dict)
        or prior_g08.get("status") != "review_pending"
        or prior_g08.get("g1a_authorized") is not False
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
    artifact_path = f"{TRANSITION_ARTIFACT_ROOT}/{manifest['transition_id']}.json"
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
            "g1a_authorized",
            "source_artifact_sha256",
        }
        if set(record) != expected_record_keys:
            reasons.append("transition_review_record_schema_invalid")
        elif (
            record["schema_version"] != "raisa-ariadne.external-g0-review.v2"
            or record["review_id"] != manifest["transition_id"]
            or record["reviewed_commit"] != reviewed
            or record["reviewed_tree"] != manifest["reviewed_tree"]
            or record["verdict"] != manifest["external_review_verdict"]
            or record["blocking_finding_count"] != manifest["blocking_finding_count"]
            or record["reviewer_surface"] != manifest["reviewer_surface"]
            or record["g1a_authorized"] is not True
            or not isinstance(record["source_artifact_sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", record["source_artifact_sha256"]) is None
        ):
            reasons.append("transition_review_record_binding_mismatch")

    artifact_entries = [row for row in tranche_changes if row.path == artifact_path]
    if len(artifact_entries) != 1 or artifact_entries[0].status != "A":
        reasons.append("transition_artifact_not_immutable_addition")
    try:
        artifact_payload = (root / artifact_path).read_bytes()
    except OSError:
        artifact_payload = b""
        reasons.append("transition_artifact_missing")

    try:
        pointer_map = _transition_semantic_pointer_map(root, reviewed)
    except ProgrammeAdmissionError as error:
        pointer_map = {}
        reasons.append(error.reason_code)
    allowed_pointer_map = {
        STATE_PATH.as_posix(): _TRANSITION_STATE_POINTERS,
        GATES_PATH.as_posix(): _TRANSITION_GATES_POINTERS,
        OVERLAY_PATH.as_posix(): _TRANSITION_OVERLAY_POINTERS,
        LATCH_PATH.as_posix(): _TRANSITION_LATCH_POINTERS,
        AGENTS_PATH.as_posix(): {"/emergency_header"},
    }
    if (
        pointer_map
        and {path: set(pointers) for path, pointers in pointer_map.items()}
        != allowed_pointer_map
    ):
        reasons.append("transition_semantic_pointer_delta_not_exact")

    after_state_digest = _sha256_bytes((root / STATE_PATH).read_bytes())
    after_policy_digest = policy.policy_digest
    manifest_digest = _sha256_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    if artifact_payload:
        artifact = _strict_json_payload(artifact_payload, "transition_artifact_invalid")
        expected_artifact_keys = {
            "schema_version",
            "transition_id",
            "recorded_at",
            "transition_manifest",
            "transition_manifest_sha256",
            "reviewed_commit",
            "reviewed_tree",
            "external_review_record_sha256",
            "state_digest_before",
            "state_digest_after",
            "policy_digest_before",
            "policy_digest_after",
            "changed_semantic_pointers",
            "scope_result",
            "target_cleanliness_contract",
        }
        target_worktree_policy = policy.overlay["target_worktree_policy"]
        expected_target_contract = {
            "schema_version": "ariadne.g1a_target_cleanliness_contract.v2",
            "preserved_legacy_worktree": target_worktree_policy[
                "preserved_legacy_worktree"
            ],
            "separate_clean_target_required": True,
            "activation_untracked_count_required": 0,
            "development_allowed_untracked_paths": sorted(G1A_ALLOWED_UNTRACKED_PATHS),
            "pre_push_untracked_count_required": 0,
            "post_push_untracked_count_required": 0,
            "inventory_includes_ignored": True,
            "protected_path_aliases_forbidden": True,
            "remote_identity_sha256": policy.overlay["remote_identity_policy"][
                "remote_identity_sha256"
            ],
        }
        if set(artifact) != expected_artifact_keys:
            reasons.append("transition_artifact_schema_invalid")
        elif (
            artifact["schema_version"] != "raisa-ariadne.g0-to-g1a-transition.v1"
            or artifact["transition_id"] != manifest["transition_id"]
            or artifact["transition_manifest"] != manifest
            or artifact["transition_manifest_sha256"] != manifest_digest
            or artifact["reviewed_commit"] != reviewed
            or artifact["reviewed_tree"] != manifest["reviewed_tree"]
            or artifact["external_review_record_sha256"]
            != manifest["external_review_record_sha256"]
            or artifact["state_digest_before"] != manifest["state_digest_before"]
            or artifact["state_digest_after"] != after_state_digest
            or artifact["policy_digest_before"] != manifest["policy_digest_before"]
            or artifact["policy_digest_after"] != after_policy_digest
            or artifact["changed_semantic_pointers"] != pointer_map
            or artifact["scope_result"] != {"admitted": True, "phase": "development"}
            or artifact["target_cleanliness_contract"] != expected_target_contract
        ):
            reasons.append("transition_artifact_binding_mismatch")

    changed_paths = {row.path for row in tranche_changes}
    required_paths = {
        AGENTS_PATH.as_posix(),
        STATE_PATH.as_posix(),
        GATES_PATH.as_posix(),
        OVERLAY_PATH.as_posix(),
        review_path,
        artifact_path,
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

    snapshot = policy.state["clockwork_snapshot"]
    try:
        safety_head = _run_git(root, "rev-parse", snapshot["local_safety_ref"])
    except ProgrammeAdmissionError:
        safety_head = ""
    if safety_head != snapshot["frozen_sha"]:
        reasons.append("transition_clockwork_safety_ref_drift")
    for artifact_key in ("git_bundle", "pre_g0_untracked_archive"):
        preservation = snapshot[artifact_key]
        try:
            observed_digest = _sha256_file(Path(preservation["path"]))
        except ProgrammeAdmissionError:
            observed_digest = ""
        if observed_digest != preservation["sha256"]:
            reasons.append("transition_preservation_artifact_drift")

    origin_head = _fresh_remote_head(
        root, remote_identity["normalized_push_url"], branch
    )
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


_SUBGATE_TRANSITION_STATE_POINTERS = {
    "/observed_at",
    "/current_gate",
    "/active_correction",
    "/active_profile",
    "/task_selection/allowed_task_kinds/0",
    "/task_selection/next_eligible_now",
    "/task_selection/next_tranche_admission_requires_state_transition",
    "/task_selection/next_eligibility_condition",
    "/g1a_subgate_authority/decisive_transition_enablement_review_id",
    "/g1a_subgate_authority/external_review_history/0",
    "/g1a_subgate_authority/subgates/G1A.2/transition_enablement_status",
    "/g1a_subgate_authority/subgates/G1A.2/state_transition_status",
    "/g1a_subgate_authority/subgates/G1A.2/state_transition",
    "/g1a_subgate_authority/subgates/G1A.2/implementation_authorized",
    "/g1a_subgate_authority/subgates/G1A.2/next_action",
}
_SUBGATE_TRANSITION_GATES_POINTERS = {
    "/programme/prepared_at",
    "/programme/current_gate",
    "/gates/9/status",
    "/gates/10/next_gate",
    "/gates/11/status",
}
_SUBGATE_TRANSITION_OVERLAY_POINTERS = {
    "/active_profile",
    "/subgate_transition_policy/transition_status",
}
_SUBGATE_TRANSITION_LATCH_POINTERS = {
    "/operation_id",
    "/active_tranche",
    "/objective",
    "/status",
    "/source_head",
    "/authority_source",
    "/checkpoint/completed_stage",
    "/checkpoint/next_executable_stage",
    "/checkpoint/settings_fingerprint",
    "/resume_after_compaction",
    "/terminal_response/permitted",
    "/terminal_response/reason",
    "/protected_boundaries/3",
    "/protected_boundaries/4",
}


def _subgate_transition_semantic_pointer_map(
    root: Path, enablement_commit: str
) -> dict[str, list[str]]:
    pairs: tuple[tuple[Path, str], ...] = (
        (STATE_PATH, "json"),
        (GATES_PATH, "yaml"),
        (OVERLAY_PATH, "yaml"),
        (LATCH_PATH, "json"),
    )
    result: dict[str, list[str]] = {}
    for path, kind in pairs:
        before_payload = _git_object_bytes(
            root, f"{enablement_commit}:{path.as_posix()}"
        )
        try:
            after_payload = (root / path).read_bytes()
        except OSError as error:
            raise ProgrammeAdmissionError(
                "subgate_transition_semantic_input_missing"
            ) from error
        if kind == "json":
            before = _strict_json_payload(
                before_payload, "subgate_transition_semantic_before_invalid"
            )
            after = _strict_json_payload(
                after_payload, "subgate_transition_semantic_after_invalid"
            )
        else:
            before = _strict_yaml_payload(
                before_payload, "subgate_transition_semantic_before_invalid"
            )
            after = _strict_yaml_payload(
                after_payload, "subgate_transition_semantic_after_invalid"
            )
        result[path.as_posix()] = sorted(_semantic_pointers(before, after))

    before_agents = _git_object_bytes(
        root, f"{enablement_commit}:{AGENTS_PATH.as_posix()}"
    ).replace(b"\r\n", b"\n")
    try:
        after_agents = (root / AGENTS_PATH).read_bytes().replace(b"\r\n", b"\n")
    except OSError as error:
        raise ProgrammeAdmissionError("subgate_transition_agents_missing") from error
    marker = b"# EMR4 Centaur \xe2\x80\x94 Live Agent Handover"
    if marker not in before_agents or marker not in after_agents:
        raise ProgrammeAdmissionError("subgate_transition_agents_marker_missing")
    before_header, before_body = before_agents.split(marker, 1)
    after_header, after_body = after_agents.split(marker, 1)
    if before_body != after_body:
        raise ProgrammeAdmissionError("subgate_transition_agents_body_changed")
    expected_before = (
        b"# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n\n"
        b"`orchestration/programme/current-state.json`, `orchestration/programme/gates.yaml`,\n"
        b"and the active recovery admission policy outrank the historical baton below while\n"
        b"the programme is in recovery. The older baton is evidence only and its named\n"
        b"successor must not resume. Gate G1A.1 is owner-accepted with residual risk; G1A.2\n"
        b"transition enablement is review-pending and its state transition, implementation and provider invocation remain closed. Missing, malformed, stale, or contradictory programme state is a hard stop.\n\n"
    )
    expected_after = (
        b"# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n\n"
        b"`orchestration/programme/current-state.json`, `orchestration/programme/gates.yaml`,\n"
        b"and the active recovery admission policy outrank the historical baton below while\n"
        b"the programme is in recovery. The older baton is evidence only and its named\n"
        b"successor must not resume. Gate G1A.2 is active only for its bounded verdict adapter; provider invocation\n"
        b"remains closed. G1A.3 integration and every protected ref remain closed. Missing, malformed, stale, or contradictory programme state is a hard stop.\n\n"
    )
    if before_header != expected_before or after_header != expected_after:
        raise ProgrammeAdmissionError("subgate_transition_agents_header_not_exact")
    result[AGENTS_PATH.as_posix()] = ["/emergency_header"]
    return result


def _subgate_transition_scope_reasons(
    *,
    root: Path,
    policy: ProgrammePolicy,
    manifest: dict[str, Any],
    phase: str,
    branch: str,
    head: str,
    commit_count: int,
    tranche_changes: Sequence[GitPathChange],
    remote_identity: dict[str, Any],
) -> tuple[list[str], str | None]:
    reasons: list[str] = []
    enablement = manifest["enablement_controller_commit"]
    try:
        enablement_tree = _run_git(root, "rev-parse", f"{enablement}^{{tree}}")
    except ProgrammeAdmissionError:
        enablement_tree = ""
    if enablement_tree != manifest["enablement_controller_tree"]:
        reasons.append("subgate_transition_enablement_tree_mismatch")
    if head == enablement:
        if phase != "development" or commit_count != 0:
            reasons.append("subgate_transition_commit_missing")
    else:
        try:
            parent_row = _run_git(root, "rev-list", "--parents", "-n", "1", head)
        except ProgrammeAdmissionError:
            parent_row = ""
        parents = parent_row.split()
        if commit_count != 1 or len(parents) != 2 or parents[1] != enablement:
            reasons.append("subgate_transition_exact_parent_required")

    before_state = _git_object_bytes(root, f"{enablement}:{STATE_PATH.as_posix()}")
    if _sha256_bytes(before_state) != manifest["state_digest_before"]:
        reasons.append("subgate_transition_state_digest_before_mismatch")
    policy_paths = (
        GATES_PATH,
        RISK_PATH,
        INVENTORY_PATH,
        G1A_SCOPE_PATH,
        OVERLAY_PATH,
        PROJECT_PATH,
        CONTINUATION_PATH,
        LATCH_PATH,
        AGENTS_PATH,
    )
    if (
        _digest_paths_at(root, enablement, policy_paths)
        != manifest["policy_digest_before"]
    ):
        reasons.append("subgate_transition_policy_digest_before_mismatch")
    prior = _strict_json_payload(before_state, "subgate_transition_prior_state_invalid")
    prior_g1a2 = (
        prior.get("g1a_subgate_authority", {}).get("subgates", {}).get("G1A.2", {})
    )
    if (
        prior.get("current_gate") != SUBGATE_TRANSITION_FROM_GATE
        or prior.get("active_profile") != G1A_ACTIVE_PROFILE
        or prior_g1a2.get("transition_enablement_status") != "review_pending"
        or prior_g1a2.get("state_transition_status") != "not_started"
        or prior_g1a2.get("implementation_authorized") is not False
        or prior_g1a2.get("implementation_started") is not False
        or prior_g1a2.get("provider_invocation_authorized") is not False
    ):
        reasons.append("subgate_transition_prior_state_not_closed")

    try:
        before_owner = _git_object_bytes(root, f"{enablement}:{OWNER_DISPOSITION_PATH}")
        after_owner = (root / OWNER_DISPOSITION_PATH).read_bytes()
    except (ProgrammeAdmissionError, OSError):
        before_owner = after_owner = b""
        reasons.append("subgate_transition_owner_disposition_unavailable")
    if (
        before_owner != after_owner
        or _sha256_bytes(after_owner) != manifest["owner_disposition_record_sha256"]
    ):
        reasons.append("subgate_transition_owner_disposition_rewritten")

    transition_id = manifest["transition_id"]
    review_path = f"{SUBGATE_REVIEW_ROOT}/{transition_id}.json"
    artifact_path = f"{SUBGATE_TRANSITION_ARTIFACT_ROOT}/{transition_id}.json"
    review_entries = [row for row in tranche_changes if row.path == review_path]
    if len(review_entries) != 1 or review_entries[0].status != "A":
        reasons.append("subgate_transition_review_not_immutable_addition")
    try:
        review_payload = (root / review_path).read_bytes()
    except OSError:
        review_payload = b""
        reasons.append("subgate_transition_review_missing")
    if _sha256_bytes(review_payload) != manifest["external_review_record_sha256"]:
        reasons.append("subgate_transition_review_digest_mismatch")

    artifact_entries = [row for row in tranche_changes if row.path == artifact_path]
    if len(artifact_entries) != 1 or artifact_entries[0].status != "A":
        reasons.append("subgate_transition_artifact_not_immutable_addition")
    try:
        artifact_payload = (root / artifact_path).read_bytes()
    except OSError:
        artifact_payload = b""
        reasons.append("subgate_transition_artifact_missing")

    try:
        pointer_map = _subgate_transition_semantic_pointer_map(root, enablement)
    except ProgrammeAdmissionError as error:
        pointer_map = {}
        reasons.append(error.reason_code)
    expected_pointers = {
        STATE_PATH.as_posix(): _SUBGATE_TRANSITION_STATE_POINTERS,
        GATES_PATH.as_posix(): _SUBGATE_TRANSITION_GATES_POINTERS,
        OVERLAY_PATH.as_posix(): _SUBGATE_TRANSITION_OVERLAY_POINTERS,
        LATCH_PATH.as_posix(): _SUBGATE_TRANSITION_LATCH_POINTERS,
        AGENTS_PATH.as_posix(): {"/emergency_header"},
    }
    if (
        pointer_map
        and {path: set(pointers) for path, pointers in pointer_map.items()}
        != expected_pointers
    ):
        reasons.append("subgate_transition_semantic_pointer_delta_not_exact")

    after_state_digest = _sha256_bytes((root / STATE_PATH).read_bytes())
    manifest_digest = _sha256_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    )
    if artifact_payload:
        artifact = _strict_json_payload(
            artifact_payload, "subgate_transition_artifact_invalid"
        )
        expected_keys = {
            "schema_version",
            "transition_id",
            "recorded_at",
            "transition_manifest",
            "transition_manifest_sha256",
            "owner_disposition_record_sha256",
            "external_review_record_sha256",
            "enablement_controller_commit",
            "enablement_controller_tree",
            "state_digest_before",
            "state_digest_after",
            "policy_digest_before",
            "policy_digest_after",
            "changed_semantic_pointers",
            "scope_result",
            "g1a2_profile_contract",
        }
        expected_profile = {
            "active_profile": G1A2_ACTIVE_PROFILE,
            "task_class": G1A2_TASK_CLASS,
            "allowed_paths": sorted(G1A2_ALLOWED_PATHS),
            "allowed_effects": sorted(G1A2_ALLOWED_EFFECTS),
            "provider_invocation_authorized": False,
            "allowed_mutation_symbols": sorted(
                policy.g1a_scope["subgates"]["G1A.2"]["allowed_mutation_symbols"]
            ),
            "protected_ast_sha256": policy.g1a_scope["subgates"]["G1A.2"][
                "immutable_provider_contract"
            ]["protected_ast_sha256"],
        }
        if set(artifact) != expected_keys:
            reasons.append("subgate_transition_artifact_schema_invalid")
        elif (
            artifact["schema_version"] != "ariadne.g1a1-to-g1a2-transition.v1"
            or artifact["transition_id"] != transition_id
            or artifact["transition_manifest"] != manifest
            or artifact["transition_manifest_sha256"] != manifest_digest
            or artifact["owner_disposition_record_sha256"]
            != manifest["owner_disposition_record_sha256"]
            or artifact["external_review_record_sha256"]
            != manifest["external_review_record_sha256"]
            or artifact["enablement_controller_commit"] != enablement
            or artifact["enablement_controller_tree"]
            != manifest["enablement_controller_tree"]
            or artifact["state_digest_before"] != manifest["state_digest_before"]
            or artifact["state_digest_after"] != after_state_digest
            or artifact["policy_digest_before"] != manifest["policy_digest_before"]
            or artifact["policy_digest_after"] != policy.policy_digest
            or artifact["changed_semantic_pointers"] != pointer_map
            or artifact["scope_result"] != {"admitted": True, "phase": "development"}
            or artifact["g1a2_profile_contract"] != expected_profile
        ):
            reasons.append("subgate_transition_artifact_binding_mismatch")

    changed_paths = {row.path for row in tranche_changes}
    required_paths = SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS | {
        review_path,
        artifact_path,
    }
    if changed_paths != required_paths:
        reasons.append("subgate_transition_changed_paths_not_exact")
    if any(
        path.endswith(".py") or path.startswith(("app/", "tests/"))
        for path in changed_paths
    ):
        reasons.append("subgate_transition_implementation_change_forbidden")
    reasons.extend(g1a2_provider_contract_reasons(root))

    expected_protected = policy.state["protected_refs"]["expected_sha"]
    try:
        protected_ok = all(
            _run_git(root, "rev-parse", ref) == expected_protected
            for ref in policy.state["protected_refs"]["refs"]
        )
    except ProgrammeAdmissionError:
        protected_ok = False
    if not protected_ok:
        reasons.append("subgate_transition_protected_refs_changed")

    origin_head = _fresh_remote_head(
        root, remote_identity["normalized_push_url"], branch
    )
    expected_origin = head if phase == "post-push" else enablement
    if origin_head is None:
        reasons.append("scope_fresh_origin_observation_invalid")
    elif origin_head != expected_origin:
        reasons.append(
            "scope_origin_head_mismatch"
            if phase == "post-push"
            else "subgate_transition_origin_not_enablement_candidate"
        )
    return list(dict.fromkeys(reasons)), origin_head


_G1A3_TRANSITION_STATE_POINTERS = {
    "/observed_at",
    "/current_gate",
    "/active_correction",
    "/active_profile",
    "/task_selection/allowed_task_kinds/0",
    "/task_selection/next_eligible_now",
    "/task_selection/next_tranche_admission_requires_state_transition",
    "/task_selection/next_eligibility_condition",
    "/g1a_subgate_authority/decisive_g1a3_transition_enablement_review_id",
    "/g1a_subgate_authority/g1a3_transition_enablement_review_history/0",
    "/g1a_subgate_authority/subgates/G1A.3/status",
    "/g1a_subgate_authority/subgates/G1A.3/transition_enablement_status",
    "/g1a_subgate_authority/subgates/G1A.3/state_transition_status",
    "/g1a_subgate_authority/subgates/G1A.3/state_transition",
    "/g1a_subgate_authority/subgates/G1A.3/implementation_authorized",
    "/g1a_subgate_authority/subgates/G1A.3/next_action",
}
_G1A3_TRANSITION_GATES_POINTERS = {
    "/programme/prepared_at",
    "/programme/current_gate",
    "/gates/9/status",
    "/gates/12/status",
}
_G1A3_TRANSITION_OVERLAY_POINTERS = {
    "/active_profile",
    "/g1a3_transition_policy/transition_status",
}
_G1A3_TRANSITION_LATCH_POINTERS = {
    "/operation_id",
    "/active_tranche",
    "/objective",
    "/status",
    "/source_head",
    "/authority_source",
    "/checkpoint/completed_stage",
    "/checkpoint/next_executable_stage",
    "/checkpoint/settings_fingerprint",
    "/resume_after_compaction",
    "/terminal_response/permitted",
    "/terminal_response/reason",
    "/protected_boundaries/7",
}


def _g1a3_transition_semantic_pointer_map(
    root: Path, enablement_commit: str
) -> dict[str, list[str]]:
    pairs: tuple[tuple[Path, str], ...] = (
        (STATE_PATH, "json"),
        (GATES_PATH, "yaml"),
        (OVERLAY_PATH, "yaml"),
        (LATCH_PATH, "json"),
    )
    result: dict[str, list[str]] = {}
    for path, kind in pairs:
        before_payload = _git_object_bytes(
            root, f"{enablement_commit}:{path.as_posix()}"
        )
        try:
            after_payload = (root / path).read_bytes()
        except OSError as error:
            raise ProgrammeAdmissionError(
                "g1a3_transition_semantic_input_missing"
            ) from error
        if kind == "json":
            before = _strict_json_payload(
                before_payload, "g1a3_transition_semantic_before_invalid"
            )
            after = _strict_json_payload(
                after_payload, "g1a3_transition_semantic_after_invalid"
            )
        else:
            before = _strict_yaml_payload(
                before_payload, "g1a3_transition_semantic_before_invalid"
            )
            after = _strict_yaml_payload(
                after_payload, "g1a3_transition_semantic_after_invalid"
            )
        result[path.as_posix()] = sorted(_semantic_pointers(before, after))

    before_agents = _git_object_bytes(
        root, f"{enablement_commit}:{AGENTS_PATH.as_posix()}"
    ).replace(b"\r\n", b"\n")
    try:
        after_agents = (root / AGENTS_PATH).read_bytes().replace(b"\r\n", b"\n")
    except OSError as error:
        raise ProgrammeAdmissionError("g1a3_transition_agents_missing") from error
    marker = b"# EMR4 Centaur \xe2\x80\x94 Live Agent Handover"
    if marker not in before_agents or marker not in after_agents:
        raise ProgrammeAdmissionError("g1a3_transition_agents_marker_missing")
    before_header, before_body = before_agents.split(marker, 1)
    after_header, after_body = after_agents.split(marker, 1)
    if before_body != after_body:
        raise ProgrammeAdmissionError("g1a3_transition_agents_body_changed")
    expected_before = (
        b"# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n\n"
        b"`orchestration/programme/current-state.json`, `orchestration/programme/gates.yaml`,\n"
        b"and the active recovery admission policy outrank the historical baton below while\n"
        b"the programme is in recovery. The older baton is evidence only and its named\n"
        b"successor must not resume. Gate G1A.2 implementation is externally accepted. G1A.3 transition enablement\n"
        b"is review-pending as a runtime-faithful source-byte/body-only-AST replacement; its state transition,\n"
        b"implementation, integration entrypoint, provider invocation and every protected ref\n"
        b"remain closed.\n"
        b"Missing, malformed, stale, or contradictory programme state is a hard stop.\n\n"
    )
    expected_after = (
        b"# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n\n"
        b"`orchestration/programme/current-state.json`, `orchestration/programme/gates.yaml`,\n"
        b"and the active recovery admission policy outrank the historical baton below while\n"
        b"the programme is in recovery. The older baton is evidence only and its named\n"
        b"successor must not resume. Gate G1A.3 is active only for its bounded integration-authority consumer;\n"
        b"integration execution, provider invocation and every protected ref remain closed.\n"
        b"Missing, malformed, stale, or contradictory programme state is a hard stop.\n\n"
    )
    if before_header != expected_before or after_header != expected_after:
        raise ProgrammeAdmissionError("g1a3_transition_agents_header_not_exact")
    result[AGENTS_PATH.as_posix()] = ["/emergency_header"]
    return result


def _g1a3_transition_scope_reasons(
    *,
    root: Path,
    policy: ProgrammePolicy,
    manifest: dict[str, Any],
    phase: str,
    branch: str,
    head: str,
    commit_count: int,
    tranche_changes: Sequence[GitPathChange],
    remote_identity: dict[str, Any],
) -> tuple[list[str], str | None]:
    reasons: list[str] = []
    enablement = manifest["enablement_controller_commit"]
    try:
        enablement_tree = _run_git(root, "rev-parse", f"{enablement}^{{tree}}")
        parent_row = _run_git(
            root, "rev-list", "--parents", "-n", "1", enablement
        ).split()
    except ProgrammeAdmissionError:
        enablement_tree = ""
        parent_row = []
    if (
        enablement_tree != manifest["enablement_controller_tree"]
        or len(parent_row) != 2
        or parent_row[1] != manifest["g1a2_implementation_commit"]
    ):
        reasons.append("g1a3_transition_enablement_git_binding_mismatch")
    if head == enablement:
        if phase != "development" or commit_count != 0:
            reasons.append("g1a3_transition_commit_missing")
    else:
        try:
            transition_parents = _run_git(
                root, "rev-list", "--parents", "-n", "1", head
            ).split()
        except ProgrammeAdmissionError:
            transition_parents = []
        if (
            commit_count != 1
            or len(transition_parents) != 2
            or transition_parents[1] != enablement
        ):
            reasons.append("g1a3_transition_exact_parent_required")

    before_state = _git_object_bytes(root, f"{enablement}:{STATE_PATH.as_posix()}")
    if _sha256_bytes(before_state) != manifest["state_digest_before"]:
        reasons.append("g1a3_transition_state_digest_before_mismatch")
    policy_paths = (
        GATES_PATH,
        RISK_PATH,
        INVENTORY_PATH,
        G1A_SCOPE_PATH,
        OVERLAY_PATH,
        PROJECT_PATH,
        CONTINUATION_PATH,
        LATCH_PATH,
        AGENTS_PATH,
    )
    if (
        _digest_paths_at(root, enablement, policy_paths)
        != manifest["policy_digest_before"]
    ):
        reasons.append("g1a3_transition_policy_digest_before_mismatch")
    prior = _strict_json_payload(before_state, "g1a3_transition_prior_state_invalid")
    prior_authority = prior.get("g1a_subgate_authority", {})
    prior_g1a3 = prior_authority.get("subgates", {}).get("G1A.3", {})
    if (
        prior.get("current_gate") != G1A3_TRANSITION_FROM_GATE
        or prior.get("active_profile") != G1A3_ENABLEMENT_PENDING_PROFILE
        or prior_g1a3.get("transition_enablement_status") != "review_pending"
        or prior_g1a3.get("state_transition_status") != "not_started"
        or prior_g1a3.get("implementation_authorized") is not False
        or prior_g1a3.get("implementation_started") is not False
        or prior_g1a3.get("integration_execution_authorized") is not False
        or prior_g1a3.get("provider_invocation_authorized") is not False
        or prior_authority.get("decisive_g1a3_transition_enablement_review_id")
        is not None
        or prior_authority.get("g1a3_transition_enablement_review_history") != []
    ):
        reasons.append("g1a3_transition_prior_state_not_closed")

    implementation_path = G1A2_IMPLEMENTATION_REVIEW_PATH
    try:
        before_implementation = _git_object_bytes(
            root, f"{enablement}:{implementation_path}"
        )
        after_implementation = (root / implementation_path).read_bytes()
    except (ProgrammeAdmissionError, OSError):
        before_implementation = after_implementation = b""
        reasons.append("g1a3_transition_implementation_review_unavailable")
    if (
        before_implementation != after_implementation
        or _sha256_bytes(after_implementation)
        != manifest["g1a2_implementation_review_record_sha256"]
    ):
        reasons.append("g1a3_transition_implementation_review_rewritten")

    review_path = (
        f"{G1A3_TRANSITION_REVIEW_ROOT}/{manifest['enablement_review_id']}.json"
    )
    artifact_path = (
        f"{SUBGATE_TRANSITION_ARTIFACT_ROOT}/{manifest['transition_id']}.json"
    )
    review_entries = [row for row in tranche_changes if row.path == review_path]
    if len(review_entries) != 1 or review_entries[0].status != "A":
        reasons.append("g1a3_transition_review_not_immutable_addition")
    try:
        review_payload = (root / review_path).read_bytes()
    except OSError:
        review_payload = b""
        reasons.append("g1a3_transition_review_missing")
    if _sha256_bytes(review_payload) != manifest["external_review_record_sha256"]:
        reasons.append("g1a3_transition_review_digest_mismatch")
    artifact_entries = [row for row in tranche_changes if row.path == artifact_path]
    if len(artifact_entries) != 1 or artifact_entries[0].status != "A":
        reasons.append("g1a3_transition_artifact_not_immutable_addition")
    try:
        artifact_payload = (root / artifact_path).read_bytes()
    except OSError:
        artifact_payload = b""
        reasons.append("g1a3_transition_artifact_missing")

    try:
        pointer_map = _g1a3_transition_semantic_pointer_map(root, enablement)
    except ProgrammeAdmissionError as error:
        pointer_map = {}
        reasons.append(error.reason_code)
    expected_pointers = {
        STATE_PATH.as_posix(): _G1A3_TRANSITION_STATE_POINTERS,
        GATES_PATH.as_posix(): _G1A3_TRANSITION_GATES_POINTERS,
        OVERLAY_PATH.as_posix(): _G1A3_TRANSITION_OVERLAY_POINTERS,
        LATCH_PATH.as_posix(): _G1A3_TRANSITION_LATCH_POINTERS,
        AGENTS_PATH.as_posix(): {"/emergency_header"},
    }
    if (
        pointer_map
        and {path: set(pointers) for path, pointers in pointer_map.items()}
        != expected_pointers
    ):
        reasons.append("g1a3_transition_semantic_pointer_delta_not_exact")

    after_state_digest = _sha256_bytes((root / STATE_PATH).read_bytes())
    manifest_digest = _sha256_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    )
    if artifact_payload:
        artifact = _strict_json_payload(
            artifact_payload, "g1a3_transition_artifact_invalid"
        )
        expected_keys = {
            "schema_version",
            "transition_id",
            "recorded_at",
            "transition_manifest",
            "transition_manifest_sha256",
            "g1a2_implementation_review_record_sha256",
            "external_review_record_sha256",
            "enablement_controller_commit",
            "enablement_controller_tree",
            "state_digest_before",
            "state_digest_after",
            "policy_digest_before",
            "policy_digest_after",
            "changed_semantic_pointers",
            "scope_result",
            "g1a3_profile_contract",
        }
        g1a3_scope = policy.g1a_scope["subgates"]["G1A.3"]
        integration_contract = g1a3_scope["immutable_integration_consumer_contract"]
        expected_profile = {
            "active_profile": G1A3_ACTIVE_PROFILE,
            "task_class": G1A3_TASK_CLASS,
            "allowed_paths": sorted(G1A3_ALLOWED_PATHS),
            "allowed_effects": sorted(G1A3_ALLOWED_EFFECTS),
            "integration_entrypoint_closed": True,
            "provider_invocation_authorized": False,
            "allowed_mutation_symbols": ["record_integration"],
            "hash_semantics": integration_contract["hash_semantics"],
            "runtime_source_parsing_contract": integration_contract[
                "runtime_source_parsing_contract"
            ],
            "protected_ast_sha256": integration_contract["protected_ast_sha256"],
            "source_blob": integration_contract["source_blob"],
        }
        if set(artifact) != expected_keys:
            reasons.append("g1a3_transition_artifact_schema_invalid")
        elif (
            artifact["schema_version"] != "ariadne.g1a2-to-g1a3-transition.v1"
            or artifact["transition_id"] != manifest["transition_id"]
            or artifact["transition_manifest"] != manifest
            or artifact["transition_manifest_sha256"] != manifest_digest
            or artifact["g1a2_implementation_review_record_sha256"]
            != manifest["g1a2_implementation_review_record_sha256"]
            or artifact["external_review_record_sha256"]
            != manifest["external_review_record_sha256"]
            or artifact["enablement_controller_commit"] != enablement
            or artifact["enablement_controller_tree"]
            != manifest["enablement_controller_tree"]
            or artifact["state_digest_before"] != manifest["state_digest_before"]
            or artifact["state_digest_after"] != after_state_digest
            or artifact["policy_digest_before"] != manifest["policy_digest_before"]
            or artifact["policy_digest_after"] != policy.policy_digest
            or artifact["changed_semantic_pointers"] != pointer_map
            or artifact["scope_result"] != {"admitted": True, "phase": "development"}
            or artifact["g1a3_profile_contract"] != expected_profile
        ):
            reasons.append("g1a3_transition_artifact_binding_mismatch")

    changed_paths = {row.path for row in tranche_changes}
    required_paths = G1A3_TRANSITION_FIXED_ALLOWED_PATHS | {
        review_path,
        artifact_path,
    }
    if changed_paths != required_paths:
        reasons.append("g1a3_transition_changed_paths_not_exact")
    if any(
        path.endswith(".py") or path.startswith(("app/", "tests/"))
        for path in changed_paths
    ):
        reasons.append("g1a3_transition_implementation_change_forbidden")
    try:
        antigravity_blob = _run_git(
            root, "rev-parse", "HEAD:scripts/ariadne_antigravity.py"
        )
        agent_worktrees_blob = _run_git(
            root, "rev-parse", "HEAD:scripts/agent_worktrees.py"
        )
    except ProgrammeAdmissionError:
        antigravity_blob = agent_worktrees_blob = ""
    if antigravity_blob != "ff1c95d9a24fddcba1df3ee6dc10a21b71b89049":
        reasons.append("g1a3_transition_accepted_g1a2_blob_changed")
    if agent_worktrees_blob != "f15d13f60c2c93edef0559b7b30b536b334bb884":
        reasons.append("g1a3_transition_agent_worktrees_blob_changed")
    reasons.extend(g1a3_integration_contract_reasons(root))

    expected_protected = policy.state["protected_refs"]["expected_sha"]
    try:
        protected_ok = all(
            _run_git(root, "rev-parse", ref) == expected_protected
            for ref in policy.state["protected_refs"]["refs"]
        )
    except ProgrammeAdmissionError:
        protected_ok = False
    if not protected_ok:
        reasons.append("g1a3_transition_protected_refs_changed")
    origin_head = _fresh_remote_head(
        root, remote_identity["normalized_push_url"], branch
    )
    expected_origin = head if phase == "post-push" else enablement
    if origin_head is None:
        reasons.append("scope_fresh_origin_observation_invalid")
    elif origin_head != expected_origin:
        reasons.append(
            "scope_origin_head_mismatch"
            if phase == "post-push"
            else "g1a3_transition_origin_not_enablement_candidate"
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
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            ["scope_phase_invalid"],
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    admission = evaluate_programme_admission(
        repo_root=repo_root, manifest=manifest, entrypoint="recovery_preflight"
    )
    if not admission.admitted:
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            admission.reason_codes,
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    root = repo_root.resolve()
    policy = load_programme_policy(root)
    try:
        remote_identity = observe_remote_identity(
            root, policy.overlay["remote_identity_policy"]
        )
        git_administrative_identity = observe_git_administrative_identity(root)
    except ProgrammeAdmissionError as error:
        return ScopeDecision(
            schema_version=SCOPE_VERSION,
            admitted=False,
            reason_codes=[error.reason_code],
            phase=phase,
            branch=None,
            head=None,
            origin_head=None,
            authorized_parent_commit=None,
            candidate_commit_count=None,
            changed_paths=[],
        )
    is_g0_transition = (
        isinstance(manifest, dict)
        and manifest.get("schema_version") == TRANSITION_MANIFEST_VERSION
    )
    is_subgate_transition = (
        isinstance(manifest, dict)
        and manifest.get("schema_version") == SUBGATE_TRANSITION_MANIFEST_VERSION
    )
    is_g1a3_transition = (
        isinstance(manifest, dict)
        and manifest.get("schema_version") == G1A3_TRANSITION_MANIFEST_VERSION
    )
    is_transition = is_g0_transition or is_subgate_transition or is_g1a3_transition
    if is_g0_transition:
        normalized, declared_paths = _validate_transition_manifest(
            manifest, policy=policy
        )
    elif is_subgate_transition:
        normalized, declared_paths = _validate_subgate_transition_manifest(
            manifest, policy=policy
        )
    elif is_g1a3_transition:
        normalized, declared_paths = _validate_g1a3_transition_manifest(
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
    if is_g0_transition:
        parent = normalized["reviewed_commit"]
    elif is_subgate_transition:
        parent = normalized["enablement_controller_commit"]
    elif is_g1a3_transition:
        parent = normalized["enablement_controller_commit"]
    elif policy.state["active_profile"] == G1A3_ACTIVE_PROFILE:
        enablement = policy.state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "state_transition"
        ]["enablement_controller_commit"]
        activation_commits = _run_git(
            root, "rev-list", "--reverse", f"{enablement}..{head}"
        ).splitlines()
        parent = activation_commits[0] if activation_commits else ""
    elif policy.state["active_correction"] == SUBGATE_TRANSITION_TO_GATE:
        enablement = policy.state["g1a_subgate_authority"]["subgates"]["G1A.2"][
            "state_transition"
        ]["enablement_controller_commit"]
        activation_commits = _run_git(
            root, "rev-list", "--reverse", f"{enablement}..{head}"
        ).splitlines()
        parent = activation_commits[0] if activation_commits else ""
    elif policy.state["active_correction"] == TRANSITION_TO_GATE:
        reviewed = policy.state["gate_transition"]["reviewed_commit"]
        activation_commits = _run_git(
            root, "rev-list", "--reverse", f"{reviewed}..{head}"
        ).splitlines()
        parent = activation_commits[0] if activation_commits else ""
    else:
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
    observe_untracked = policy.state["active_correction"] in {
        TRANSITION_TO_GATE,
        SUBGATE_TRANSITION_TO_GATE,
        G1A3_TRANSITION_TO_GATE,
    }
    try:
        full_changes, tranche_changes, untracked_changes = _scope_change_inventories(
            root,
            frozen_base=scope["frozen_recovery_base"],
            tranche_base=parent,
            include_untracked=observe_untracked,
        )
    except ProgrammeAdmissionError as error:
        return ScopeDecision(
            schema_version=SCOPE_VERSION,
            admitted=False,
            reason_codes=[error.reason_code],
            phase=phase,
            branch=branch,
            head=head,
            origin_head=None,
            authorized_parent_commit=parent,
            candidate_commit_count=commit_count,
            changed_paths=[],
        )
    changed = sorted({item.path for item in full_changes})
    tranche_changed = sorted({item.path for item in tranche_changes})
    try:
        for relative_path in changed:
            candidate = root / Path(*PurePosixPath(relative_path).parts)
            if candidate.exists() or candidate.is_symlink():
                _validate_regular_path_components(root, relative_path)
    except ProgrammeAdmissionError as error:
        return ScopeDecision(
            schema_version=SCOPE_VERSION,
            admitted=False,
            reason_codes=[error.reason_code],
            phase=phase,
            branch=branch,
            head=head,
            origin_head=None,
            authorized_parent_commit=parent,
            candidate_commit_count=commit_count,
            changed_paths=changed,
            remote_identity=remote_identity,
        )
    reasons.extend(_change_inventory_reasons(full_changes, cumulative_history=True))
    reasons.extend(_change_inventory_reasons(tranche_changes))
    full_allowed_paths = set(policy.full_range_allowed_paths)
    if is_transition:
        full_allowed_paths.update(declared_paths)
    if not set(changed).issubset(full_allowed_paths):
        reasons.append("scope_path_outside_policy")
    if not is_transition and not set(tranche_changed).issubset(policy.allowed_paths):
        reasons.append("scope_tranche_path_outside_policy")
    if not set(tranche_changed).issubset(declared_paths):
        reasons.append("scope_tranche_path_outside_task_manifest")
    tracked_dirty = bool(
        _run_git(root, "status", "--porcelain", "--untracked-files=no")
    )
    untracked_paths = sorted({item.path for item in untracked_changes})
    target_policy = policy.overlay["target_worktree_policy"]
    legacy_target = (
        str(root).replace("\\", "/").rstrip("/").casefold()
        == str(target_policy["preserved_legacy_worktree"])
        .replace("\\", "/")
        .rstrip("/")
        .casefold()
    )
    if observe_untracked:
        if legacy_target:
            reasons.append("scope_preserved_legacy_worktree_forbidden")
        if phase == "development":
            development_untracked_paths = (
                G1A_ALLOWED_UNTRACKED_PATHS
                if policy.state["active_correction"] == TRANSITION_TO_GATE
                else (
                    set(declared_paths)
                    if is_subgate_transition or is_g1a3_transition
                    else set(target_policy["g1a2_development_allowed_untracked_paths"])
                )
            )
            if not set(untracked_paths).issubset(development_untracked_paths):
                reasons.append("scope_untracked_path_outside_development_allowlist")
        elif untracked_paths:
            reasons.append("scope_untracked_files_forbidden")
    if phase in {"pre-push", "post-push"} and tracked_dirty:
        reasons.append("scope_tracked_worktree_dirty")
    origin_head: str | None = None
    if is_g0_transition:
        transition_reasons, origin_head = _transition_scope_reasons(
            root=root,
            policy=policy,
            manifest=normalized,
            phase=phase,
            branch=branch,
            head=head,
            commit_count=commit_count,
            tranche_changes=tranche_changes,
            remote_identity=remote_identity,
        )
        reasons.extend(transition_reasons)
    elif is_subgate_transition:
        transition_reasons, origin_head = _subgate_transition_scope_reasons(
            root=root,
            policy=policy,
            manifest=normalized,
            phase=phase,
            branch=branch,
            head=head,
            commit_count=commit_count,
            tranche_changes=tranche_changes,
            remote_identity=remote_identity,
        )
        reasons.extend(transition_reasons)
    elif is_g1a3_transition:
        transition_reasons, origin_head = _g1a3_transition_scope_reasons(
            root=root,
            policy=policy,
            manifest=normalized,
            phase=phase,
            branch=branch,
            head=head,
            commit_count=commit_count,
            tranche_changes=tranche_changes,
            remote_identity=remote_identity,
        )
        reasons.extend(transition_reasons)
    elif phase == "pre-push":
        origin_head = _fresh_remote_head(
            root, remote_identity["normalized_push_url"], branch
        )
        if origin_head is None:
            reasons.append("scope_fresh_origin_observation_invalid")
        if origin_head is not None and origin_head != parent:
            reasons.append("scope_origin_not_authorized_parent_pre_push")
    elif phase == "post-push":
        origin_head = _fresh_remote_head(
            root, remote_identity["normalized_push_url"], branch
        )
        if origin_head is None:
            reasons.append("scope_fresh_origin_observation_invalid")
        elif origin_head != head:
            reasons.append("scope_origin_head_mismatch")
    elif not is_transition:
        origin_head = _fresh_remote_head(
            root, remote_identity["normalized_push_url"], branch
        )
        if origin_head is None:
            reasons.append("scope_fresh_origin_observation_invalid")
        if origin_head is not None and origin_head != parent:
            reasons.append("scope_origin_not_authorized_parent_development")
    if not is_transition and policy.state["active_correction"] == (
        SUBGATE_TRANSITION_TO_GATE
    ):
        reasons.extend(g1a2_provider_contract_reasons(root))
    if not is_transition and policy.state["active_profile"] == G1A3_ACTIVE_PROFILE:
        reasons.extend(g1a3_integration_contract_reasons(root))
    if not is_transition and normalized["candidate_or_current_head"] != head:
        reasons.append("task_manifest_head_stale")
    try:
        index_tree = _run_git(root, "write-tree")
    except ProgrammeAdmissionError:
        index_tree = None
        reasons.append("scope_index_tree_observation_failed")
    changed_paths_digest = _change_inventory_digest(
        full_changes=full_changes,
        tranche_changes=tranche_changes,
        untracked_changes=untracked_changes,
    )
    target_cleanliness = {
        "tracked_dirty": tracked_dirty,
        "untracked_count": len(untracked_paths),
        "untracked_paths": untracked_paths,
        "untracked_paths_digest": _sha256_bytes(
            json.dumps(untracked_paths, separators=(",", ":")).encode()
        ),
        "preserved_legacy_worktree": legacy_target,
        "ignored_count": len(
            [item for item in untracked_changes if item.status == "!"]
        ),
        "ignored_paths": sorted(
            {item.path for item in untracked_changes if item.status == "!"}
        ),
        "inventory_includes_ignored": observe_untracked,
        "activation_clean": bool(
            observe_untracked
            and commit_count == 0
            and not tracked_dirty
            and not untracked_paths
        ),
    }
    branch_ref = f"refs/heads/{branch}" if branch else None
    filesystem_inventory_digest = _sha256_bytes(
        json.dumps(
            [
                {"path": item.path, "classification": item.status}
                for item in sorted(
                    untracked_changes, key=lambda row: (row.path, row.status)
                )
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    target_cleanliness["filesystem_inventory_digest"] = filesystem_inventory_digest
    target_cleanliness["git_administrative_identity"] = git_administrative_identity
    target_cleanliness["trusted_git_identity"] = policy.trusted_git_identity
    operation_binding = {
        "target_head": head,
        "index_tree": index_tree,
        "changed_paths_digest": changed_paths_digest,
        "filesystem_inventory_digest": filesystem_inventory_digest,
        "git_administrative_identity_sha256": git_administrative_identity[
            "git_administrative_identity_sha256"
        ],
        "trusted_git_identity_sha256": policy.trusted_git_identity[
            "trusted_git_identity_sha256"
        ],
        "expected_origin_head": origin_head,
        "remote_identity_sha256": remote_identity["remote_identity_sha256"],
        "explicit_destination": remote_identity["normalized_push_url"],
        "branch_ref": branch_ref,
        "exact_push_refspec": f"{head}:{branch_ref}" if branch_ref else None,
        "force_with_lease": (
            f"{branch_ref}:{origin_head}"
            if branch_ref is not None and origin_head is not None
            else None
        ),
    }
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
        index_tree=index_tree,
        changed_paths_digest=changed_paths_digest,
        expected_origin_head=origin_head,
        target_cleanliness=target_cleanliness,
        remote_identity=remote_identity,
        operation_binding=operation_binding,
    )


def admission_payload(decision: ProgrammeDecision | ScopeDecision) -> dict[str, Any]:
    """Serialize a decision without turning it into an authority token."""
    return asdict(decision)


def _evaluate_programme_operation_admission_core(
    *,
    repo_root: Path,
    manifest: object | None,
    entrypoint: str,
    phase: str,
) -> ScopeDecision:
    """Return the one canonical admission-and-scope decision for commit or push."""
    if entrypoint not in {"task_branch_commit", "task_branch_push"}:
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            ["combined_operation_entrypoint_invalid"],
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    admission = evaluate_programme_admission(
        repo_root=repo_root, manifest=manifest, entrypoint="recovery_preflight"
    )
    if not admission.admitted:
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            admission.reason_codes,
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    if not isinstance(manifest, dict):
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            ["task_manifest_missing"],
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    if manifest.get("schema_version") not in {
        TRANSITION_MANIFEST_VERSION,
        SUBGATE_TRANSITION_MANIFEST_VERSION,
        G1A3_TRANSITION_MANIFEST_VERSION,
    }:
        required_effect = ENTRYPOINT_REQUIRED_EFFECT[entrypoint]
        effects = manifest.get("intended_side_effect_classes")
        if not isinstance(effects, list) or required_effect not in effects:
            return ScopeDecision(
                SCOPE_VERSION,
                False,
                ["task_manifest_required_effect_missing"],
                phase,
                None,
                None,
                None,
                None,
                None,
                [],
            )
    return evaluate_committed_scope(repo_root=repo_root, manifest=manifest, phase=phase)


def evaluate_programme_operation_admission(
    *,
    repo_root: Path,
    manifest: object | None,
    entrypoint: str,
    phase: str,
) -> ScopeDecision:
    """Fail closed unless G1A combined operations use the pinned gatekeeper."""
    try:
        policy = load_programme_policy(repo_root)
    except ProgrammeAdmissionError as error:
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            [error.reason_code],
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    if policy.state["active_correction"] in {
        TRANSITION_TO_GATE,
        SUBGATE_TRANSITION_TO_GATE,
        G1A3_TRANSITION_TO_GATE,
    }:
        return ScopeDecision(
            SCOPE_VERSION,
            False,
            ["pinned_gatekeeper_required"],
            phase,
            None,
            None,
            None,
            None,
            None,
            [],
        )
    return _evaluate_programme_operation_admission_core(
        repo_root=repo_root,
        manifest=manifest,
        entrypoint=entrypoint,
        phase=phase,
    )


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


def require_programme_operation_admission(
    *,
    repo_root: Path,
    manifest_path: Path | None,
    entrypoint: str,
    phase: str,
) -> ScopeDecision:
    """Raise unless the canonical combined commit/push decision is admitted."""
    manifest = strict_json_object(manifest_path) if manifest_path is not None else None
    decision = evaluate_programme_operation_admission(
        repo_root=repo_root,
        manifest=manifest,
        entrypoint=entrypoint,
        phase=phase,
    )
    if not decision.admitted:
        reasons = ",".join(decision.reason_codes) or "programme_operation_denied"
        raise ProgrammeAdmissionError(reasons)
    return decision
