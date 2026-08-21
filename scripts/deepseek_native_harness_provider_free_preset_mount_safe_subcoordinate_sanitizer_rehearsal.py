"""Admit one pure preset-mount sanitizer fixture without starting the Harness."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-safe-subcoordinate-"
    "sanitizer-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "safe-subcoordinate-sanitizer-evidence.json"
REPORT_PATH = OPERATION_ROOT / "safe-subcoordinate-sanitizer-report.md"
SAFE_VECTOR_REJECTION_PATH = OPERATION_ROOT / "attempt-002-safe-vector-rejection.json"
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_safe_subcoordinate_sanitizer_evidence.v1"
)
CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_safe_subcoordinate_sanitizer_contract.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_FIXTURE_DETAIL = "HOSTILE_FIXTURE_DETAIL_NEVER_RELEASE"


class SanitizerRehearsalError(RuntimeError):
    """Fail-closed error carrying only a schema-owned diagnostic code."""


class SafeVectorMismatch(SanitizerRehearsalError):
    """A structurally safe closed-code vector differs from the contract."""

    def __init__(self, observed_codes: list[str], first_mismatch_index: int) -> None:
        super().__init__("node_fixture_safe_vector_mismatch")
        self.observed_codes = observed_codes
        self.first_mismatch_index = first_mismatch_index


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SanitizerRehearsalError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise SanitizerRehearsalError(f"json_object_required:{path.name}")
    return value


def load_contract() -> dict[str, Any]:
    contract = _load_object(CONTRACT_PATH)
    schema = _load_object(CONTRACT_SCHEMA_PATH)
    try:
        jsonschema.Draft202012Validator(schema).validate(contract)
    except jsonschema.ValidationError as error:
        raise SanitizerRehearsalError("contract_schema_rejected") from error
    if contract["schema_version"] != CONTRACT_SCHEMA_VERSION:
        raise SanitizerRehearsalError("contract_schema_version_mismatch")
    if contract["operation_id"] != OPERATION_ID:
        raise SanitizerRehearsalError("contract_operation_mismatch")
    return contract


def _safe_repo_path(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise SanitizerRehearsalError("repository_path_unsafe")
    path = REPO_ROOT.joinpath(*pure.parts).resolve()
    try:
        path.relative_to(REPO_ROOT.resolve())
    except ValueError as error:
        raise SanitizerRehearsalError("repository_path_escape") from error
    if not path.is_file() or path.is_symlink():
        raise SanitizerRehearsalError("repository_file_missing_or_unsafe")
    return path


def _default_cache_root() -> Path:
    profile = os.environ.get("USERPROFILE")
    if not profile:
        raise SanitizerRehearsalError("userprofile_missing")
    return Path(profile) / ".cache" / "emr4-native-harness"


def _safe_upstream_path(source_root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise SanitizerRehearsalError("upstream_path_unsafe")
    path = source_root.joinpath(*pure.parts).resolve()
    try:
        path.relative_to(source_root.resolve())
    except ValueError as error:
        raise SanitizerRehearsalError("upstream_path_escape") from error
    if not path.is_file() or path.is_symlink():
        raise SanitizerRehearsalError("upstream_file_missing_or_unsafe")
    return path


def verify_upstream_source(contract: dict[str, Any]) -> dict[str, Any]:
    predecessor_path = _safe_repo_path(contract["accepted_source_contract"])
    predecessor = _load_object(predecessor_path)
    if predecessor.get("seed_relative_path") != contract["seed_relative_path"]:
        raise SanitizerRehearsalError("accepted_seed_relative_path_mismatch")
    upstream = contract["upstream_source"]
    predecessor_rows = {
        row.get("path"): row
        for row in predecessor.get("source_files", [])
        if isinstance(row, dict)
    }
    predecessor_row = predecessor_rows.get(upstream["path"])
    if predecessor_row is None:
        raise SanitizerRehearsalError("accepted_upstream_row_absent")
    for field in ("bytes", "sha256"):
        if predecessor_row.get(field) != upstream[field]:
            raise SanitizerRehearsalError(f"accepted_upstream_{field}_mismatch")
    if predecessor.get("package_version") != upstream["package_version"]:
        raise SanitizerRehearsalError("accepted_upstream_version_mismatch")

    configured = PurePosixPath(contract["seed_relative_path"])
    if not configured.parts or configured.parts[0] != "emr4-native-harness":
        raise SanitizerRehearsalError("seed_relative_path_mismatch")
    cache_root = _default_cache_root()
    source_root = cache_root.parent.joinpath(*configured.parts).resolve()
    if source_root.is_symlink() or not source_root.is_dir():
        raise SanitizerRehearsalError("source_root_missing_or_unsafe")
    source_path = _safe_upstream_path(source_root, upstream["path"])
    payload = source_path.read_bytes()
    if len(payload) != upstream["bytes"]:
        raise SanitizerRehearsalError("upstream_source_bytes_mismatch")
    if sha256_bytes(payload) != upstream["sha256"]:
        raise SanitizerRehearsalError("upstream_source_sha256_mismatch")
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise SanitizerRehearsalError("upstream_source_not_utf8") from error
    if not all(anchor in source for anchor in contract["upstream_source_anchors"]):
        raise SanitizerRehearsalError("upstream_source_anchor_missing")
    return {**upstream, "passed": True}


def verify_repository_bindings(contract: dict[str, Any]) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    payloads: dict[str, str] = {}
    for row in contract["repository_files"]:
        path = _safe_repo_path(row["path"])
        payload = path.read_bytes()
        if len(payload) != row["bytes"]:
            raise SanitizerRehearsalError("repository_source_bytes_mismatch")
        if sha256_bytes(payload) != row["sha256"]:
            raise SanitizerRehearsalError("repository_source_sha256_mismatch")
        try:
            payloads[row["path"]] = payload.decode("utf-8")
        except UnicodeError as error:
            raise SanitizerRehearsalError("repository_source_not_utf8") from error
        bindings.append({**row, "passed": True})

    sanitizer_path = next(
        path for path in payloads if path.endswith("safe_subcoordinate_sanitizer.mjs")
    )
    fixture_path = next(path for path in payloads if path.endswith("sanitizer_fixture.mjs"))
    sanitizer = payloads[sanitizer_path]
    fixture = payloads[fixture_path]
    if re.search(r"(^|\n)\s*import(?:\s|\()", sanitizer):
        raise SanitizerRehearsalError("sanitizer_import_present")
    required_sanitizer_anchors = [
        "export function sanitizePresetMountError(error, PresetMountError)",
        "value.constructor === PresetMountError",
        "error.message === AGENT_SCOPE_MESSAGE",
        "return terminal(CODES.unclassified);",
        "detail: null",
    ]
    if not all(anchor in sanitizer for anchor in required_sanitizer_anchors):
        raise SanitizerRehearsalError("sanitizer_source_anchor_missing")

    imports = re.findall(r'(^|\n)\s*import[\s\S]*?from\s+"([^"]+)";', fixture)
    expected_import = (
        "./deepseek_native_harness_provider_free_preset_mount_safe_"
        "subcoordinate_sanitizer.mjs"
    )
    if len(imports) != 1 or imports[0][1] != expected_import:
        raise SanitizerRehearsalError("fixture_import_boundary_rejected")
    forbidden_tokens = [
        "@deepseek-ai/dsh",
        "child_process",
        "node:fs",
        "node:http",
        "node:https",
        "process.env",
        "import(",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
    ]
    if any(token in fixture or token in sanitizer for token in forbidden_tokens):
        raise SanitizerRehearsalError("repository_effect_boundary_rejected")
    if fixture.count("process.stdout.write(") != 1:
        raise SanitizerRehearsalError("fixture_stdout_boundary_rejected")
    return bindings


def expected_results(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"stage": "preset_mount", "code": code, "detail": None}
        for code in contract["expected_result_codes"]
    ]


def expected_stdout(contract: dict[str, Any]) -> str:
    return json.dumps(expected_results(contract), separators=(",", ":")) + "\n"


def validate_fixture_result(
    *, stdout: str, stderr: str, returncode: int, contract: dict[str, Any]
) -> list[dict[str, Any]]:
    if returncode != 0:
        raise SanitizerRehearsalError("node_fixture_exit_nonzero")
    if stderr:
        raise SanitizerRehearsalError("node_fixture_stderr_nonempty")
    if FORBIDDEN_FIXTURE_DETAIL in stdout or FORBIDDEN_FIXTURE_DETAIL in stderr:
        raise SanitizerRehearsalError("node_fixture_detail_leak")
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise SanitizerRehearsalError("node_fixture_stdout_not_json") from error
    if not isinstance(value, list) or len(value) != len(contract["expected_result_codes"]):
        raise SanitizerRehearsalError("node_fixture_result_shape_mismatch")
    closed_codes = set(contract["closed_codes"])
    for row in value:
        if not isinstance(row, dict) or list(row) != ["stage", "code", "detail"]:
            raise SanitizerRehearsalError("node_fixture_result_shape_mismatch")
        if (
            row["stage"] != "preset_mount"
            or row["code"] not in closed_codes
            or row["detail"] is not None
        ):
            raise SanitizerRehearsalError("node_fixture_result_shape_mismatch")
    expected = expected_results(contract)
    if stdout != expected_stdout(contract) or value != expected:
        observed_codes = [row["code"] for row in value]
        expected_codes = contract["expected_result_codes"]
        mismatch = next(
            index
            for index, (observed, wanted) in enumerate(
                zip(observed_codes, expected_codes, strict=True)
            )
            if observed != wanted
        ) if observed_codes != expected_codes else -1
        raise SafeVectorMismatch(observed_codes, mismatch)
    return value


def write_safe_vector_rejection(
    *, candidate_source: str, contract: dict[str, Any], error: SafeVectorMismatch
) -> None:
    payload = {
        "schema_version": "ariadne.native_harness_preset_mount_safe_vector_rejection.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-002",
        "candidate_source": candidate_source,
        "result": "safe_vector_mismatch",
        "first_mismatch_index": error.first_mismatch_index,
        "expected_codes": contract["expected_result_codes"],
        "observed_codes": error.observed_codes,
        "detail_retained": False,
        "stderr_bytes": 0,
        "node_process_count": 1,
        "cumulative_node_process_count": 2,
        "third_process_authorized": False,
    }
    SAFE_VECTOR_REJECTION_PATH.write_bytes(canonical_bytes(payload))


def run_fixture_once(contract: dict[str, Any]) -> list[dict[str, Any]]:
    node = shutil.which("node")
    if not node:
        raise SanitizerRehearsalError("node_executable_unavailable")
    fixture_path = next(
        _safe_repo_path(row["path"])
        for row in contract["repository_files"]
        if row["path"].endswith("sanitizer_fixture.mjs")
    )
    try:
        completed = subprocess.run(
            [node, str(fixture_path)],
            cwd=REPO_ROOT,
            env={},
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError, UnicodeError) as error:
        raise SanitizerRehearsalError("node_fixture_process_failed") from error
    return validate_fixture_result(
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
        contract=contract,
    )


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if completed.returncode != 0 or completed.stderr.strip():
        raise SanitizerRehearsalError("git_snapshot_failed")
    return completed.stdout.strip()


def verify_execution_git_snapshot() -> str:
    head = _git("rev-parse", "HEAD")
    upstream = _git("rev-parse", "@{upstream}")
    if not FULL_OID.fullmatch(head) or head != upstream:
        raise SanitizerRehearsalError("candidate_origin_alignment_rejected")
    tracked = _git("status", "--porcelain", "--untracked-files=no")
    if tracked:
        raise SanitizerRehearsalError("tracked_worktree_dirty")
    return head


def build_evidence(
    *,
    contract: dict[str, Any],
    candidate_source: str,
    upstream_binding: dict[str, Any],
    repository_bindings: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(row["code"] for row in results)
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "candidate_source": candidate_source,
        "result": "pass",
        "upstream_source_binding": upstream_binding,
        "repository_bindings": repository_bindings,
        "source_anchor_count": len(contract["upstream_source_anchors"]),
        "closed_codes": contract["closed_codes"],
        "fixture": {
            "authored_synthetic": True,
            "attempt_id": "attempt-002",
            "node_process_count": 1,
            "prior_consumed_node_process_count": 1,
            "cumulative_node_process_count": 2,
            "result_count": len(results),
            "stdout_exact": True,
            "stderr_bytes": 0,
            "forbidden_detail_absent": True,
            "native_harness_import_count": 0,
            "child_process_count": 0,
            "environment_read_count": 0,
            "filesystem_api_count": 0,
            "network_api_count": 0,
        },
        "code_counts": {code: counts.get(code, 0) for code in contract["closed_codes"]},
        "zero_counters": {name: 0 for name in contract["required_zero_counters"]},
        "claim_boundary": {
            "safe_reduction_only": True,
            "raw_runtime_detail_retained": False,
            "runner_integrated": False,
            "repair_selected": False,
            "retry_authorized": False,
            "worker_launch_authorized": False,
            "occupied_model_launch_authorized": False,
        },
    }
    validate_evidence(evidence)
    return evidence


def validate_evidence(evidence: dict[str, Any]) -> None:
    schema = _load_object(EVIDENCE_SCHEMA_PATH)
    try:
        jsonschema.Draft202012Validator(schema).validate(evidence)
    except jsonschema.ValidationError as error:
        raise SanitizerRehearsalError("evidence_schema_rejected") from error
    serialized = canonical_bytes(evidence)
    if FORBIDDEN_FIXTURE_DETAIL.encode("utf-8") in serialized:
        raise SanitizerRehearsalError("evidence_detail_leak")


def render_report(*, evidence: dict[str, Any], timestamp: str) -> str:
    counts = evidence["code_counts"]
    lines = [
        "# Native Harness preset-mount safe-subcoordinate sanitizer report",
        "",
        "Date: 2026-08-22",
        "",
        f"Timestamp: {timestamp} (Australia/Brisbane)",
        "",
        f"Candidate source: `{evidence['candidate_source']}`",
        "",
        "Result: **pass**",
        "",
        "One authored-synthetic local Node process exercised fifteen fixed inputs.",
        "Every result contained exactly `stage`, `code` and null `detail`; stdout",
        "matched the frozen JSON byte-for-byte and stderr was empty.",
        "",
        "Safe code counts:",
        "",
    ]
    lines.extend(f"- `{code}`: {counts[code]}" for code in evidence["closed_codes"])
    lines.extend(
        [
            "",
            "The pinned rc.7 source, repository sanitizer and fixture hashes pass.",
            "No fixture detail was retained. The fixture imported no DSH package and",
            "made no child-process, environment, filesystem or network API call.",
            "",
            "This proves only the pure safe reduction. It does not connect a runner,",
            "select a repair, authorise a retry, start the native Harness, launch a",
            "worker/model/provider request or perform any product or data action.",
            "",
        ]
    )
    return "\n".join(lines)


def execute() -> dict[str, Any]:
    contract = load_contract()
    if not PLAN_PATH.is_file() or not THREAT_PATH.is_file():
        raise SanitizerRehearsalError("plan_or_threat_missing")
    upstream_binding = verify_upstream_source(contract)
    repository_bindings = verify_repository_bindings(contract)
    candidate_source = verify_execution_git_snapshot()
    try:
        results = run_fixture_once(contract)
    except SafeVectorMismatch as error:
        write_safe_vector_rejection(
            candidate_source=candidate_source, contract=contract, error=error
        )
        raise
    evidence = build_evidence(
        contract=contract,
        candidate_source=candidate_source,
        upstream_binding=upstream_binding,
        repository_bindings=repository_bindings,
        results=results,
    )
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(
        render_report(evidence=evidence, timestamp=timestamp), encoding="utf-8"
    )
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    upstream_binding = verify_upstream_source(contract)
    repository_bindings = verify_repository_bindings(contract)
    evidence = _load_object(EVIDENCE_PATH)
    validate_evidence(evidence)
    if evidence["upstream_source_binding"] != upstream_binding:
        raise SanitizerRehearsalError("evidence_upstream_binding_mismatch")
    if evidence["repository_bindings"] != repository_bindings:
        raise SanitizerRehearsalError("evidence_repository_binding_mismatch")
    if evidence["closed_codes"] != contract["closed_codes"]:
        raise SanitizerRehearsalError("evidence_code_vocabulary_mismatch")
    expected_counts = Counter(contract["expected_result_codes"])
    if evidence["code_counts"] != {
        code: expected_counts.get(code, 0) for code in contract["closed_codes"]
    }:
        raise SanitizerRehearsalError("evidence_code_counts_mismatch")
    if evidence["zero_counters"] != {
        name: 0 for name in contract["required_zero_counters"]
    }:
        raise SanitizerRehearsalError("evidence_zero_counters_mismatch")
    candidate = evidence["candidate_source"]
    if not FULL_OID.fullmatch(candidate):
        raise SanitizerRehearsalError("evidence_candidate_source_invalid")
    if _git("merge-base", "--is-ancestor", candidate, "HEAD"):
        raise SanitizerRehearsalError("unexpected_git_ancestor_output")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if f"Candidate source: `{candidate}`" not in report:
        raise SanitizerRehearsalError("report_candidate_binding_missing")
    if FORBIDDEN_FIXTURE_DETAIL in report:
        raise SanitizerRehearsalError("report_detail_leak")
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evidence = execute() if args.execute else check()
    except SanitizerRehearsalError as error:
        raise SystemExit(str(error)) from None
    print(
        json.dumps(
            {
                "operation_id": OPERATION_ID,
                "status": "passed",
                "candidate_source": evidence["candidate_source"],
                "node_process_count": evidence["fixture"]["node_process_count"],
                "cumulative_node_process_count": evidence["fixture"][
                    "cumulative_node_process_count"
                ],
                "native_harness_process_count": evidence["zero_counters"][
                    "native_harness_process_count"
                ],
                "runner_integrated": evidence["claim_boundary"]["runner_integrated"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
