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
import subprocess
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
)

TASK_MANIFEST_VERSION = "ariadne.programme_task_manifest.v1"
TRANSITION_MANIFEST_VERSION = "ariadne.programme_gate_transition_manifest.v1"
DECISION_VERSION = "ariadne.programme_admission_decision.v1"
SCOPE_VERSION = "ariadne.programme_scope_decision.v1"
ADMITTED_TASK_CLASS = "g0_7_controller_maintenance"
ADMITTED_PROGRAMME_GATE = "G0.7"
TRANSITION_TASK_CLASS = "g0_to_g1a_state_transition"
G1A_TASK_CLASS = "g1a_1_verdict_kernel_and_pure_consumers"
G1A2_TASK_CLASS = "g1a_2_antigravity_verdict_adapter"
G0_CONTROLLER_PROFILE = "G0.7_CONTROLLER_MAINTENANCE"
TRANSITION_PROFILE = "G0_TO_G1A_STATE_TRANSITION"
G1A_ACTIVE_PROFILE = "G1A.1_ACTIVE"
TRANSITION_FROM_GATE = "G0"
TRANSITION_TO_GATE = "G1A.1"
TRANSITION_REVIEW_ROOT = "orchestration/programme/external-reviews"
TRANSITION_ARTIFACT_ROOT = "orchestration/programme/gate-transitions"
RETAINED_REVIEW_ROOT = "orchestration/programme/reviews"

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
        completed = subprocess.run(  # noqa: S603
            ["git", "config", "--null", "--get-all", key],
            cwd=root,
            check=False,
            capture_output=True,
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProgrammeAdmissionError("remote_identity_observation_failed") from error
    if completed.returncode not in {0, 1}:
        raise ProgrammeAdmissionError("remote_identity_observation_failed")
    if completed.returncode == 1:
        return []
    try:
        values = completed.stdout.decode("utf-8").split("\0")
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
        completed = subprocess.run(  # noqa: S603
            [
                "git",
                "config",
                "--null",
                "--get-regexp",
                r"^url\..*\.(insteadOf|pushInsteadOf)$",
            ],
            cwd=root,
            check=False,
            capture_output=True,
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProgrammeAdmissionError("remote_identity_observation_failed") from error
    if completed.returncode not in {0, 1}:
        raise ProgrammeAdmissionError("remote_identity_observation_failed")
    if completed.returncode == 1:
        return 0
    return completed.stdout.count(b"\0")


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


def _change_inventory_reasons(changes: Sequence[GitPathChange]) -> list[str]:
    reasons: list[str] = []
    for change in changes:
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
            "g0_1_correction",
            "g0_2_correction",
            "g0_3_correction",
            "g0_4_correction",
            "g0_5_correction",
            "g0_6_correction",
            "g0_7_correction",
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
        _unique_text_list(selection["blocked_task_kinds"], "blocked_task_kinds_invalid")
    )
    _bounded_text(selection["admission_command"], "admission_command_invalid", 500)
    phase = value["active_correction"]
    if phase not in {ADMITTED_PROGRAMME_GATE, TRANSITION_TO_GATE}:
        raise ProgrammeAdmissionError("programme_phase_invalid")
    expected_task_class = (
        ADMITTED_TASK_CLASS if phase == ADMITTED_PROGRAMME_GATE else G1A_TASK_CLASS
    )
    expected_gate = "G0" if phase == ADMITTED_PROGRAMME_GATE else TRANSITION_TO_GATE
    expected_status = (
        "revision_required" if phase == ADMITTED_PROGRAMME_GATE else "active"
    )
    expected_profile = (
        G0_CONTROLLER_PROFILE
        if phase == ADMITTED_PROGRAMME_GATE
        else G1A_ACTIVE_PROFILE
    )
    if (
        selection["autonomous_selection_enabled"] is not False
        or selection["allowed_task_kinds"] != [expected_task_class]
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
        or selection["next_eligible_tranche"]
        != (
            ADMITTED_PROGRAMME_GATE
            if phase == ADMITTED_PROGRAMME_GATE
            else TRANSITION_TO_GATE
        )
        or selection["next_eligible_now"] is not True
        or selection["next_tranche_started"] is not False
        or selection["next_tranche_admission_requires_state_transition"]
        is not (phase == ADMITTED_PROGRAMME_GATE)
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
    if correction_g07["correction_directive_sha256"] != authority["directive_sha256"]:
        raise ProgrammeAdmissionError("decisive_external_review_binding_invalid")
    if phase == ADMITTED_PROGRAMME_GATE and (
        decisive_review["reviewed_commit"] != correction_g07["authorized_parent_commit"]
        or decisive_review["reviewed_tree"] != correction_g07["reviewed_g0_6_tree"]
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
            or correction_g07["status"] not in {"in_progress", "review_pending"}
            or correction_g07["external_review_status"]
            not in {"not_started", "pending"}
            or correction_g07["g1a_authorized"] is not False
            or value["gate_transition"] is not None
        ):
            raise ProgrammeAdmissionError("g0_7_correction_not_fail_closed")
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
            or correction_g07["status"] != "external_review_passed"
            or correction_g07["external_review_status"] != "pass"
            or correction_g07["g1a_authorized"] is not True
        ):
            raise ProgrammeAdmissionError("g0_7_transition_history_invalid")
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
            else TRANSITION_TO_GATE
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
            "G0": "revision_required_g0_7",
            "G0.1": "superseded_revision_required",
            "G0.2": "superseded_revision_required",
            "G0.3": "superseded_revision_required",
            "G0.4": "superseded_revision_required",
            "G0.5": "superseded_revision_required",
            "G0.6": "superseded_revision_required",
            "G0.7": state["g0_7_correction"]["status"],
            "G1A": "subgated_closed",
            "G1A.1": "blocked_by_external_G0_review",
            "G1A.2": "blocked_by_G1A_1_external_review",
            "G1A.3": "deferred_integration_mutation",
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
            "G0.7": "external_review_passed",
            "G1A": "active_subgate_G1A_1",
            "G1A.1": "active",
            "G1A.2": "blocked_by_G1A_1_external_review",
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
    elif by_id.get("G1A.1", {}).get("status") != "active":
        raise ProgrammeAdmissionError("g1a_not_active")


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
        value["schema_version"] != "raisa-ariadne.g1a-verdict-integration-scope.v2"
        or value["status"] != "pre_reviewed_closed_subgates"
        or value["inventory_source_commit"]
        != "4ce17198fad677aed1fe45be4e3bf2b18c713b3b"
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
        g1a1["status"] != "pre_reviewed_closed_scope"
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
        g1a2["status"]
        != "closed_pending_g1a_1_external_acceptance_and_state_transition"
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
        common_keys | {"candidate_paths", "integration_consumers"},
        "g1a_3_scope_schema_invalid",
    )
    if (
        g1a3["status"] != "deferred_no_active_profile"
        or g1a3["task_class"] != "g1a_3_integration_consumer_mutation"
        or g1a3["candidate_paths"] != ["scripts/agent_worktrees.py"]
        or g1a3["allowed_paths"] != []
        or g1a3["allowed_untracked_paths"] != []
        or g1a3["allowed_effects"] != []
        or set(_unique_text_list(g1a3["forbidden_effects"], "g1a_3_forbidden_invalid"))
        != {
            "integration",
            "protected_ref_movement",
            "provider_invocation",
            "deployment",
            "pages",
            "real_data_access",
        }
    ):
        raise ProgrammeAdmissionError("g1a_3_scope_not_deferred")
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
            "pinned_gatekeeper",
            "target_worktree_policy",
            "remote_identity_policy",
            "gated_entrypoints",
            "reversibility",
        },
        "recovery_overlay_schema_invalid",
    )
    if (
        value["schema_version"] != "ariadne.programme_recovery.v8"
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
            "paths": G0_G07_ALLOWED_PATHS,
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
    }
    for name, spec in expected.items():
        row = _exact_keys(
            profiles[name], _PROFILE_KEYS, "recovery_profile_schema_invalid"
        )
        if (
            row["profile_kind"] != spec["profile_kind"]
            or row["expected_programme_mode"] != "recovery"
            or row["expected_current_gate"] != spec["expected_current_gate"]
            or row["expected_gate_status"] != spec["expected_gate_status"]
            or row["active_correction"] != spec["active_correction"]
            or row["programme_gate"] != spec["programme_gate"]
            or row["admitted_task_classes"] != [spec["task_class"]]
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
            or set(_unique_text_list(row["allowed_paths"], "profile_paths_invalid"))
            != spec["paths"]
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
        != state["g0_7_correction"]["authorized_parent_commit"]
        or scope["candidate_commit_limit"] != 1
        or set(_unique_text_list(scope["allowed_paths"], "scope_allowed_paths_invalid"))
        != G0_G07_ALLOWED_PATHS
    ):
        raise ProgrammeAdmissionError("scope_policy_state_disagreement")
    allowed_paths = _unique_text_list(
        active["allowed_paths"], "scope_allowed_paths_invalid"
    )
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
            row["path"] not in G0_G07_ALLOWED_PATHS
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
        "schema_version": "ariadne.pinned_programme_gatekeeper_policy.v4",
        "module": "orchestration_harness/pinned_programme_gatekeeper.py",
        "bootstrap": "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
        "cli": "scripts/raisa_ariadne_gatekeeper_bootstrap.py",
        "operation_cli_module": "scripts/raisa_ariadne_pinned_gatekeeper.py",
        "canonical_operations": ["evaluate", "commit", "push"],
        "operation_receipt_schema": "ariadne.pinned_programme_operation_receipt.v1",
        "source_binding": "expected_commit_tree_plus_trusted_physical_source_bytes",
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
        target_policy["schema_version"] != "ariadne.g1a_target_worktree_policy.v2"
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
        else "The reviewed G0 to G1A.1 transition is complete; Gate G1A.1 is active"
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
    _validate_latch(latch, settings_digest)
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
                G0_G07_ALLOWED_PATHS
                | TRANSITION_FIXED_ALLOWED_PATHS
                | set(allowed_paths)
                | {
                    f"{TRANSITION_REVIEW_ROOT}/{state['gate_transition']['transition_id']}.json",
                    f"{TRANSITION_ARTIFACT_ROOT}/{state['gate_transition']['transition_id']}.json",
                }
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
    if task_class not in active_profile["admitted_task_classes"]:
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
        expected_base = policy.state["g0_7_correction"]["authorized_parent_commit"]
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
    task_class = _manifest_task_class(manifest)
    try:
        if (
            isinstance(manifest, dict)
            and manifest.get("schema_version") == TRANSITION_MANIFEST_VERSION
        ):
            normalized, _ = _validate_transition_manifest(manifest, policy=policy)
            normalized_task_class = TRANSITION_TASK_CLASS
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
    active_profile = policy.overlay["profiles"][policy.overlay["active_profile"]]
    if entrypoint in set(active_profile["closed_entrypoints"]):
        return _decision(
            admitted=False,
            reasons=[f"{entrypoint}_closed_in_active_profile"],
            policy=policy,
            task_class=normalized_task_class,
        )
    if entrypoint in {"task_branch_commit", "task_branch_push"}:
        return _decision(
            admitted=False,
            reasons=["combined_operation_admission_required"],
            policy=policy,
            task_class=normalized_task_class,
        )
    if normalized_task_class != TRANSITION_TASK_CLASS:
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
    "/g0_acceptance/external_review_history/7",
    "/g0_acceptance/next_action",
    "/g0_7_correction/status",
    "/g0_7_correction/external_review_status",
    "/g0_7_correction/g1a_authorized",
    "/g0_7_correction/next_action",
    "/gate_transition",
}
_TRANSITION_GATES_POINTERS = {
    "/programme/prepared_at",
    "/programme/current_gate",
    "/programme/current_gate_status",
    "/programme/next_eligible_tranche",
    "/gates/0/status",
    "/gates/7/status",
    "/gates/8/status",
    "/gates/9/status",
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
        b"successor must not resume. Gate G0.7 is the only authorised correction; G1A is\n"
        b"closed. Missing, malformed, stale, or contradictory programme state is a hard stop.\n\n"
    )
    expected_after = expected_before.replace(
        b"Gate G0.7 is the only authorised correction; G1A is\nclosed.",
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
    prior_g07 = prior_state.get("g0_7_correction")
    if (
        prior_state.get("programme_mode") != "recovery"
        or prior_state.get("current_gate") != TRANSITION_FROM_GATE
        or prior_state.get("current_gate_status") != "revision_required"
        or prior_state.get("active_correction") != ADMITTED_PROGRAMME_GATE
        or prior_state.get("active_profile") != G0_CONTROLLER_PROFILE
        or not isinstance(prior_g07, dict)
        or prior_g07.get("status") != "review_pending"
        or prior_g07.get("g1a_authorized") is not False
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
    if is_transition:
        parent = normalized["reviewed_commit"]
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
    observe_untracked = policy.state["active_correction"] == TRANSITION_TO_GATE
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
    reasons.extend(_change_inventory_reasons(full_changes))
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
            if not set(untracked_paths).issubset(G1A_ALLOWED_UNTRACKED_PATHS):
                reasons.append("scope_untracked_path_outside_development_allowlist")
        elif untracked_paths:
            reasons.append("scope_untracked_files_forbidden")
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
    if manifest.get("schema_version") != TRANSITION_MANIFEST_VERSION:
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
    if policy.state["active_correction"] == TRANSITION_TO_GATE:
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
