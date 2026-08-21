"""Run one preset-mount sanitizer fixture with a five-key Windows environment."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Mapping
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer_rehearsal
    as base,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-sanitizer-windows-"
    "minimum-environment-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
PROCESS_ENVELOPE_SCHEMA_PATH = OPERATION_ROOT / "process-envelope.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "minimum-environment-sanitizer-evidence.json"
REPORT_PATH = OPERATION_ROOT / "minimum-environment-sanitizer-report.md"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "attempt-001-process-envelope.json"
SAFE_VECTOR_REJECTION_PATH = OPERATION_ROOT / "attempt-001-safe-vector-rejection.json"
WRAPPER_TERMINAL_PATH = OPERATION_ROOT / "attempt-001-wrapper-terminal.json"
PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-preset-mount-sanitizer-windows-"
    "minimum-environment-recovery-plan.md"
)
THREAT_PATH = (
    REPO_ROOT
    / "docs"
    / "security"
    / "deepseek-native-harness-provider-free-preset-mount-sanitizer-windows-"
    "minimum-environment-recovery-threat-model-delta.md"
)
SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_windows_minimum_environment_evidence.v1"
)
CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_windows_minimum_environment_contract.v1"
)
PROCESS_ENVELOPE_SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_windows_minimum_environment_"
    "process_envelope.v1"
)
WINDOWS_ENVIRONMENT_KEYS = ("SystemRoot", "WINDIR", "ComSpec", "TEMP", "TMP")
FORBIDDEN_ENVIRONMENT_KEYS = frozenset({"PATH", "NODE_OPTIONS"})
OUTPUT_PATHS = (
    EVIDENCE_PATH,
    REPORT_PATH,
    PROCESS_ENVELOPE_PATH,
    SAFE_VECTOR_REJECTION_PATH,
    WRAPPER_TERMINAL_PATH,
)


class MinimumEnvironmentRecoveryError(RuntimeError):
    """Fail-closed error carrying only a schema-owned diagnostic code."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MinimumEnvironmentRecoveryError(
            f"json_unreadable:{path.name}"
        ) from error
    if not isinstance(value, dict):
        raise MinimumEnvironmentRecoveryError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: dict[str, Any], code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.ValidationError as error:
        raise MinimumEnvironmentRecoveryError(code) from error


def load_contract() -> dict[str, Any]:
    contract = _load_object(CONTRACT_PATH)
    _validate(CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected")
    if contract["schema_version"] != CONTRACT_SCHEMA_VERSION:
        raise MinimumEnvironmentRecoveryError("contract_schema_version_mismatch")
    if contract["operation_id"] != OPERATION_ID:
        raise MinimumEnvironmentRecoveryError("contract_operation_mismatch")
    return contract


def verify_predecessor_bindings(contract: dict[str, Any]) -> None:
    accepted = base._load_object(base._safe_repo_path(contract["accepted_contract"]))
    if accepted.get("repository_files") != contract["repository_files"]:
        raise MinimumEnvironmentRecoveryError("accepted_repository_bindings_mismatch")
    if accepted.get("upstream_source") != contract["upstream_source"]:
        raise MinimumEnvironmentRecoveryError("accepted_upstream_binding_mismatch")
    if accepted.get("upstream_source_anchors") != contract["upstream_source_anchors"]:
        raise MinimumEnvironmentRecoveryError("accepted_source_anchors_mismatch")
    if accepted.get("closed_codes") != contract["closed_codes"]:
        raise MinimumEnvironmentRecoveryError("accepted_closed_codes_mismatch")
    if accepted.get("expected_result_codes") != contract["expected_result_codes"]:
        raise MinimumEnvironmentRecoveryError("accepted_result_vector_mismatch")
    envelope_path = base._safe_repo_path(
        contract["accepted_negative_process_envelope"]
    )
    envelope = base._load_object(envelope_path)
    if (
        base.sha256_bytes(base.canonical_bytes(envelope))
        != contract["accepted_negative_process_envelope_sha256"]
    ):
        raise MinimumEnvironmentRecoveryError(
            "accepted_negative_process_envelope_mismatch"
        )


def minimum_windows_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    environment = os.environ if source is None else source
    if any(not environment.get(key) for key in WINDOWS_ENVIRONMENT_KEYS):
        raise MinimumEnvironmentRecoveryError("minimum_environment_key_missing")
    result = {key: environment[key] for key in WINDOWS_ENVIRONMENT_KEYS}
    if tuple(result) != WINDOWS_ENVIRONMENT_KEYS:
        raise MinimumEnvironmentRecoveryError("minimum_environment_key_order_mismatch")
    if set(result) & FORBIDDEN_ENVIRONMENT_KEYS or len(result) != 5:
        raise MinimumEnvironmentRecoveryError("minimum_environment_shape_rejected")
    return result


def environment_projection() -> dict[str, Any]:
    return {
        "keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "key_count": 5,
        "values_retained": False,
        "unlisted_key_count": 0,
        "path_present": False,
        "node_options_present": False,
    }


def build_process_envelope(
    *, candidate_source: str, returncode: int, stdout: str, stderr: str
) -> dict[str, Any]:
    stdout_bytes = stdout.encode("utf-8")
    stderr_bytes = stderr.encode("utf-8")
    envelope = {
        "schema_version": PROCESS_ENVELOPE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "numeric_exit_code": returncode,
        "stdout_bytes": len(stdout_bytes),
        "stdout_sha256": base.sha256_bytes(stdout_bytes),
        "stderr_bytes": len(stderr_bytes),
        "stderr_sha256": base.sha256_bytes(stderr_bytes),
        "stream_content_retained": False,
        "raw_runtime_detail_retained": False,
        "environment": environment_projection(),
        "node_process_count": 1,
        "prior_consumed_node_process_count": 3,
        "lineage_cumulative_node_process_count": 4,
        "native_harness_process_count": 0,
        "further_process_authorized": False,
    }
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH,
        envelope,
        "process_envelope_schema_rejected",
    )
    return envelope


def _ensure_fresh_output_paths() -> None:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise MinimumEnvironmentRecoveryError("successor_output_already_exists")


def _resolved_node_executable() -> Path:
    raw = shutil.which("node")
    if not raw:
        raise MinimumEnvironmentRecoveryError("node_executable_unavailable")
    node = Path(raw).resolve()
    if not node.is_absolute() or not node.is_file():
        raise MinimumEnvironmentRecoveryError("node_executable_not_absolute_file")
    return node


def run_fixture_once(
    *, contract: dict[str, Any], candidate_source: str, child_environment: dict[str, str]
) -> list[dict[str, Any]]:
    node = _resolved_node_executable()
    fixture_path = next(
        base._safe_repo_path(row["path"])
        for row in contract["repository_files"]
        if row["path"].endswith("sanitizer_fixture.mjs")
    )
    try:
        completed = subprocess.run(
            [str(node), str(fixture_path)],
            cwd=REPO_ROOT,
            env=child_environment,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError, UnicodeError) as error:
        raise MinimumEnvironmentRecoveryError("node_fixture_process_failed") from error
    envelope = build_process_envelope(
        candidate_source=candidate_source,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    PROCESS_ENVELOPE_PATH.write_bytes(base.canonical_bytes(envelope))
    try:
        return base.validate_fixture_result(
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            contract=contract,
        )
    except base.SafeVectorMismatch as error:
        rejection = {
            "schema_version": (
                "ariadne.native_harness_preset_mount_windows_minimum_environment_"
                "safe_vector_rejection.v1"
            ),
            "operation_id": OPERATION_ID,
            "attempt_id": "attempt-001",
            "candidate_source": candidate_source,
            "result": "safe_vector_mismatch",
            "first_mismatch_index": error.first_mismatch_index,
            "expected_codes": contract["expected_result_codes"],
            "observed_codes": error.observed_codes,
            "detail_retained": False,
            "node_process_count": 1,
            "further_process_authorized": False,
        }
        SAFE_VECTOR_REJECTION_PATH.write_bytes(base.canonical_bytes(rejection))
        raise
    except base.WrapperTerminal as error:
        terminal = {
            "schema_version": (
                "ariadne.native_harness_preset_mount_windows_minimum_environment_"
                "wrapper_terminal.v1"
            ),
            "operation_id": OPERATION_ID,
            "attempt_id": "attempt-001",
            "candidate_source": candidate_source,
            "result": "wrapper_terminal",
            "terminal": {"stage": "fixture_boot", "code": error.code, "detail": None},
            "process_envelope_sha256": base.sha256_bytes(
                base.canonical_bytes(envelope)
            ),
            "raw_runtime_detail_retained": False,
            "further_process_authorized": False,
        }
        WRAPPER_TERMINAL_PATH.write_bytes(base.canonical_bytes(terminal))
        raise


def validate_evidence(evidence: dict[str, Any]) -> None:
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    serialized = base.canonical_bytes(evidence)
    if base.FORBIDDEN_FIXTURE_DETAIL.encode("utf-8") in serialized:
        raise MinimumEnvironmentRecoveryError("evidence_detail_leak")


def build_evidence(
    *,
    contract: dict[str, Any],
    candidate_source: str,
    upstream_binding: dict[str, Any],
    repository_bindings: list[dict[str, Any]],
    results: list[dict[str, Any]],
    process_envelope: dict[str, Any],
) -> dict[str, Any]:
    counts = Counter(row["code"] for row in results)
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "candidate_source": candidate_source,
        "result": "pass",
        "upstream_source_binding": upstream_binding,
        "repository_bindings": repository_bindings,
        "environment": environment_projection(),
        "fixture": {
            "authored_synthetic": True,
            "attempt_id": "attempt-001",
            "node_process_count": 1,
            "prior_consumed_node_process_count": 3,
            "lineage_cumulative_node_process_count": 4,
            "result_count": len(results),
            "stdout_exact": True,
            "stderr_bytes": 0,
            "forbidden_detail_absent": True,
            "native_harness_import_count": 0,
            "child_process_count": 0,
            "fixture_environment_read_count": 0,
            "filesystem_api_count": 0,
            "network_api_count": 0,
        },
        "process_envelope_sha256": base.sha256_bytes(
            base.canonical_bytes(process_envelope)
        ),
        "closed_codes": contract["closed_codes"],
        "code_counts": {
            code: counts.get(code, 0) for code in contract["closed_codes"]
        },
        "zero_counters": {
            name: 0 for name in contract["required_zero_counters"]
        },
        "claim_boundary": {
            "safe_reduction_only": True,
            "sanitizer_admitted": True,
            "minimum_environment_fixture_passed": True,
            "exact_previous_abort_cause_proven": False,
            "raw_runtime_detail_retained": False,
            "environment_values_retained": False,
            "runner_integrated": False,
            "repair_selected": False,
            "retry_authorized": False,
            "worker_launch_authorized": False,
            "occupied_model_launch_authorized": False,
        },
    }
    validate_evidence(evidence)
    return evidence


def render_report(*, evidence: dict[str, Any], timestamp: str) -> str:
    counts = evidence["code_counts"]
    lines = [
        "# Native Harness preset-mount sanitizer Windows minimum-environment report",
        "",
        "Date: 2026-08-22",
        "",
        f"Timestamp: {timestamp} (Australia/Brisbane)",
        "",
        f"Candidate source: `{evidence['candidate_source']}`",
        "",
        "Result: **pass**",
        "",
        "One authored-synthetic local Node process received exactly the five",
        "allowlisted Windows runtime keys. Their values were never persisted.",
        "The unchanged sanitizer/wrapper emitted the exact fifteen-result vector",
        "with zero stderr, and the content-free process envelope was retained",
        "before semantic admission.",
        "",
        "Safe code counts:",
        "",
    ]
    lines.extend(f"- `{code}`: {counts[code]}" for code in evidence["closed_codes"])
    lines.extend(
        [
            "",
            "This admits the pure sanitizer under the five-key local fixture only.",
            "It does not prove the exact cause of the previous exit 134, connect a",
            "runner, select a repair, authorise another process, start the native",
            "Harness, launch a worker/model/provider request or perform product/data",
            "work.",
            "",
        ]
    )
    return "\n".join(lines)


def execute() -> dict[str, Any]:
    contract = load_contract()
    if not PLAN_PATH.is_file() or not THREAT_PATH.is_file():
        raise MinimumEnvironmentRecoveryError("plan_or_threat_missing")
    verify_predecessor_bindings(contract)
    upstream_binding = base.verify_upstream_source(contract)
    repository_bindings = base.verify_repository_bindings(contract)
    child_environment = minimum_windows_environment()
    candidate_source = base.verify_execution_git_snapshot()
    _ensure_fresh_output_paths()
    results = run_fixture_once(
        contract=contract,
        candidate_source=candidate_source,
        child_environment=child_environment,
    )
    process_envelope = _load_object(PROCESS_ENVELOPE_PATH)
    evidence = build_evidence(
        contract=contract,
        candidate_source=candidate_source,
        upstream_binding=upstream_binding,
        repository_bindings=repository_bindings,
        results=results,
        process_envelope=process_envelope,
    )
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    EVIDENCE_PATH.write_bytes(base.canonical_bytes(evidence))
    REPORT_PATH.write_text(
        render_report(evidence=evidence, timestamp=timestamp), encoding="utf-8"
    )
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    verify_predecessor_bindings(contract)
    upstream_binding = base.verify_upstream_source(contract)
    repository_bindings = base.verify_repository_bindings(contract)
    process_envelope = _load_object(PROCESS_ENVELOPE_PATH)
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH,
        process_envelope,
        "process_envelope_schema_rejected",
    )
    evidence = _load_object(EVIDENCE_PATH)
    validate_evidence(evidence)
    if evidence["upstream_source_binding"] != upstream_binding:
        raise MinimumEnvironmentRecoveryError("evidence_upstream_binding_mismatch")
    if evidence["repository_bindings"] != repository_bindings:
        raise MinimumEnvironmentRecoveryError("evidence_repository_binding_mismatch")
    if evidence["environment"] != environment_projection():
        raise MinimumEnvironmentRecoveryError("evidence_environment_mismatch")
    if evidence["process_envelope_sha256"] != base.sha256_bytes(
        base.canonical_bytes(process_envelope)
    ):
        raise MinimumEnvironmentRecoveryError("evidence_process_envelope_mismatch")
    expected_counts = Counter(contract["expected_result_codes"])
    if evidence["code_counts"] != {
        code: expected_counts.get(code, 0) for code in contract["closed_codes"]
    }:
        raise MinimumEnvironmentRecoveryError("evidence_code_counts_mismatch")
    if evidence["zero_counters"] != {
        name: 0 for name in contract["required_zero_counters"]
    }:
        raise MinimumEnvironmentRecoveryError("evidence_zero_counters_mismatch")
    candidate = evidence["candidate_source"]
    if not base.FULL_OID.fullmatch(candidate):
        raise MinimumEnvironmentRecoveryError("evidence_candidate_source_invalid")
    if base._git("merge-base", "--is-ancestor", candidate, "HEAD"):
        raise MinimumEnvironmentRecoveryError("unexpected_git_ancestor_output")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if f"Candidate source: `{candidate}`" not in report:
        raise MinimumEnvironmentRecoveryError("report_candidate_binding_missing")
    if base.FORBIDDEN_FIXTURE_DETAIL in report:
        raise MinimumEnvironmentRecoveryError("report_detail_leak")
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
    except (MinimumEnvironmentRecoveryError, base.SanitizerRehearsalError) as error:
        raise SystemExit(str(error)) from None
    print(
        json.dumps(
            {
                "operation_id": OPERATION_ID,
                "status": "passed",
                "candidate_source": evidence["candidate_source"],
                "node_process_count": evidence["fixture"]["node_process_count"],
                "native_harness_process_count": evidence["zero_counters"][
                    "native_harness_process_count"
                ],
                "sanitizer_admitted": evidence["claim_boundary"][
                    "sanitizer_admitted"
                ],
                "runner_integrated": evidence["claim_boundary"][
                    "runner_integrated"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
