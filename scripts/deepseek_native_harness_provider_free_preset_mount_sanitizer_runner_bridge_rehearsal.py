"""Derive and prove the preset-mount sanitizer runner bridge without DSH."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_effective_tool_composition_guard
    as accepted_guard,
)
from scripts import (
    deepseek_native_harness_provider_free_preset_composition_safe_terminal_bridge_rehearsal
    as accepted_runner,
)
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitizer_windows_minimum_environment_recovery
    as accepted_sanitizer,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-sanitizer-runner-"
    "bridge-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
PROCESS_ENVELOPE_SCHEMA_PATH = OPERATION_ROOT / "process-envelope.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "runner-bridge-evidence.json"
REPORT_PATH = OPERATION_ROOT / "runner-bridge-report.md"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "attempt-001-process-envelope.json"
BRIDGE_PATH = (
    REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_preset_mount_sanitizer_runner_bridge.mjs"
)
FIXTURE_PATH = (
    REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_preset_mount_sanitizer_runner_bridge_fixture.mjs"
)
SANITIZER_PATH = (
    REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs"
)
ACCEPTED_RUNNER_GENERATOR_PATH = Path(accepted_runner.__file__).resolve()
ACCEPTED_GUARD_GENERATOR_PATH = Path(accepted_guard.__file__).resolve()
ACCEPTED_EVIDENCE_PATH = accepted_sanitizer.EVIDENCE_PATH
CONTRACT_SCHEMA_VERSION = "ariadne.native_harness_preset_mount_runner_bridge_contract.v1"
EVIDENCE_SCHEMA_VERSION = "ariadne.native_harness_preset_mount_runner_bridge_evidence.v1"
PROCESS_ENVELOPE_SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_runner_bridge_process_envelope.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_CODES = [
    "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
    "PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE",
    "PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED",
    "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
    "PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT",
    "PRESET_MOUNT_ROOT_SERVICE_LEAK",
    "PRESET_MOUNT_UNCLASSIFIED",
]
EXPECTED_RESULTS = [
    {"scenario": "success", "passed": True, "terminal": None},
    {
        "scenario": "agent_scope_absent",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
            "detail": None,
        },
    },
    {
        "scenario": "composition_stamp_unreadable",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE",
            "detail": None,
        },
    },
    {
        "scenario": "row_import_or_apply_rejected",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED",
            "detail": None,
        },
    },
    {
        "scenario": "subtree_publication_absent",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
            "detail": None,
        },
    },
    {
        "scenario": "row_inactive_after_await",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT",
            "detail": None,
        },
    },
    {
        "scenario": "root_service_leak",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_ROOT_SERVICE_LEAK",
            "detail": None,
        },
    },
    {
        "scenario": "unclassified",
        "passed": False,
        "terminal": {
            "stage": "preset_mount",
            "code": "PRESET_MOUNT_UNCLASSIFIED",
            "detail": None,
        },
    },
]
OUTPUT_PATHS = (EVIDENCE_PATH, REPORT_PATH, PROCESS_ENVELOPE_PATH)


class RunnerBridgeError(RuntimeError):
    """Fail-closed error carrying one closed diagnostic code."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RunnerBridgeError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise RunnerBridgeError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: dict[str, Any], code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise RunnerBridgeError(code) from error


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if completed.returncode != 0:
        raise RunnerBridgeError("git_resolution_failed")
    return completed.stdout.strip()


def _replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise RunnerBridgeError("source_rewrite_anchor_invalid")
    return source.replace(old, new)


def build_guard_source() -> bytes:
    source = accepted_guard.build_guard_source().decode("utf-8")
    source = _replace_once(
        source,
        'import { scopeOf } from "@deepseek-ai/dsh-scope";',
        'import { scopeOf } from "@deepseek-ai/dsh-scope";\n'
        'import { PresetMountError } from "@deepseek-ai/dsh-agent-presets";\n'
        'import { mountWithSanitizedTerminal } from "./preset-mount-sanitizer-runner-bridge.mjs";',
    )
    source = _replace_once(
        source,
        "function fail(code, names = []) {\n"
        "  throw new EffectiveToolCompositionError(code, names);\n"
        "}",
        "export class PresetMountSanitizedTerminalError extends Error {\n"
        "  constructor(terminal) {\n"
        '    super("PRESET_MOUNT_SANITIZED_TERMINAL");\n'
        '    this.name = "PresetMountSanitizedTerminalError";\n'
        "    this.terminal = terminal;\n"
        "  }\n"
        "}\n\n"
        "function fail(code, names = []) {\n"
        "  throw new EffectiveToolCompositionError(code, names);\n"
        "}",
    )
    source = _replace_once(
        source,
        "  try {\n"
        "    await agentCtx.agentPresets.mount(agentCtx, presetId);\n"
        "  } catch {\n"
        '    fail("EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED");\n'
        "  }",
        "  const mountReading = await mountWithSanitizedTerminal({\n"
        "    mount: agentCtx.agentPresets.mount.bind(agentCtx.agentPresets),\n"
        "    agentCtx,\n"
        "    presetId,\n"
        "    PresetMountError,\n"
        "  });\n"
        "  if (!mountReading.passed) {\n"
        "    throw new PresetMountSanitizedTerminalError(mountReading.terminal);\n"
        "  }",
    )
    return source.encode("utf-8")


def build_runner_source() -> bytes:
    source = accepted_runner.runner_source().decode("utf-8")
    source = _replace_once(
        source,
        'export const name = "provider-free-preset-composition-safe-terminal-runner";',
        'export const name = "provider-free-preset-mount-sanitizer-runner-bridge";',
    )
    source = _replace_once(
        source,
        "    safeGuardDetail: null,",
        "    safeGuardDetail: null,\n    presetMountTerminal: null,",
    )
    source = _replace_once(
        source,
        "      safe_guard_detail: observed.safeGuardDetail,",
        "      safe_guard_detail: observed.safeGuardDetail,\n"
        "      preset_mount_terminal: observed.presetMountTerminal,",
    )
    source = _replace_once(
        source,
        "    const sanitizeEffectiveToolTerminal = guardModule.sanitizeEffectiveToolTerminal;",
        "    const sanitizeEffectiveToolTerminal = guardModule.sanitizeEffectiveToolTerminal;\n"
        "    const PresetMountSanitizedTerminalError = guardModule.PresetMountSanitizedTerminalError;",
    )
    source = _replace_once(
        source,
        '    if (typeof installModelSelection !== "function" || typeof SessionId !== "function" || typeof assertEffectiveToolComposition !== "function" || typeof sanitizeEffectiveToolTerminal !== "function") throw new Error("REQUIRED_SERVICE_MISSING");',
        '    if (typeof installModelSelection !== "function" || typeof SessionId !== "function" || typeof assertEffectiveToolComposition !== "function" || typeof sanitizeEffectiveToolTerminal !== "function" || typeof PresetMountSanitizedTerminalError !== "function") throw new Error("REQUIRED_SERVICE_MISSING");',
    )
    old = (
        "          } catch (error) {\n"
        "            const safe = sanitizeEffectiveToolTerminal(error);\n"
        '            if (!safe || safe.stage !== "pre_provider_tool_composition" || !SAFE_GUARD_COORDINATES.has(safe.code) || !(safe.detail === null || (typeof safe.detail === "string" && SAFE_GUARD_DETAIL.test(safe.detail)))) throw new Error("SAFE_TERMINAL_INVALID");\n'
        '            const names = safe.detail === null ? [] : safe.detail.split(",");\n'
        '            if (new Set(names).size !== names.length || JSON.stringify(names) !== JSON.stringify([...names].sort())) throw new Error("SAFE_TERMINAL_INVALID");\n'
        "            observed.safeGuardCoordinate = safe.code;\n"
        "            observed.safeGuardDetail = safe.detail;\n"
        '            emit("preset_composition_failure_attributed", null);\n'
        "            throw new Error(ATTRIBUTED_STOP);\n"
        "          }"
    )
    new = (
        "          } catch (error) {\n"
        "            if (error instanceof PresetMountSanitizedTerminalError) {\n"
        "              const terminal = error.terminal;\n"
        '              if (!terminal || JSON.stringify(Object.keys(terminal)) !== JSON.stringify(["stage", "code", "detail"]) || terminal.stage !== "preset_mount" || !terminal.code.startsWith("PRESET_MOUNT_") || terminal.detail !== null) throw new Error("SAFE_TERMINAL_INVALID");\n'
        "              observed.presetMountTerminal = terminal;\n"
        '              emit("preset_mount_failure_attributed", null);\n'
        "              throw new Error(ATTRIBUTED_STOP);\n"
        "            }\n"
        "            const safe = sanitizeEffectiveToolTerminal(error);\n"
        '            if (!safe || safe.stage !== "pre_provider_tool_composition" || !SAFE_GUARD_COORDINATES.has(safe.code) || !(safe.detail === null || (typeof safe.detail === "string" && SAFE_GUARD_DETAIL.test(safe.detail)))) throw new Error("SAFE_TERMINAL_INVALID");\n'
        '            const names = safe.detail === null ? [] : safe.detail.split(",");\n'
        '            if (new Set(names).size !== names.length || JSON.stringify(names) !== JSON.stringify([...names].sort())) throw new Error("SAFE_TERMINAL_INVALID");\n'
        "            observed.safeGuardCoordinate = safe.code;\n"
        "            observed.safeGuardDetail = safe.detail;\n"
        '            emit("preset_composition_failure_attributed", null);\n'
        "            throw new Error(ATTRIBUTED_STOP);\n"
        "          }"
    )
    source = _replace_once(source, old, new)
    return source.encode("utf-8")


def validate_source_derivation(contract: dict[str, Any]) -> dict[str, Any]:
    accepted_runner_source = accepted_runner.runner_source()
    accepted_guard_source = accepted_guard.build_guard_source()
    bridge_source = BRIDGE_PATH.read_bytes()
    fixture_source = FIXTURE_PATH.read_bytes()
    runner_source = build_runner_source()
    guard_source = build_guard_source()
    bindings = {
        "accepted_runner_generator_sha256": sha256_file(
            ACCEPTED_RUNNER_GENERATOR_PATH
        ),
        "accepted_runner_source_sha256": sha256_bytes(accepted_runner_source),
        "accepted_guard_generator_sha256": sha256_file(ACCEPTED_GUARD_GENERATOR_PATH),
        "accepted_guard_source_sha256": sha256_bytes(accepted_guard_source),
        "accepted_minimum_environment_evidence_sha256": sha256_file(
            ACCEPTED_EVIDENCE_PATH
        ),
        "sanitizer_sha256": sha256_file(SANITIZER_PATH),
        "bridge_sha256": sha256_bytes(bridge_source),
        "fixture_sha256": sha256_bytes(fixture_source),
        "derived_runner_sha256": sha256_bytes(runner_source),
        "derived_guard_sha256": sha256_bytes(guard_source),
    }
    if bindings != contract["source_sha256"]:
        raise RunnerBridgeError("source_binding_mismatch")

    bridge_text = bridge_source.decode("utf-8")
    guard_text = guard_source.decode("utf-8")
    runner_text = runner_source.decode("utf-8")
    runner_projection = accepted_runner.validate_runner_source(runner_source)
    bridge_checks = {
        "sanitizer_import_once": bridge_text.count(
            'from "./deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs"'
        )
        == 1,
        "sanitizer_call_once": bridge_text.count("sanitizePresetMountError(") == 1,
        "mount_await_once": bridge_text.count("await mount(agentCtx, presetId)") == 1,
        "exact_terminal_shape": 'JSON.stringify(["stage", "code", "detail"])'
        in bridge_text,
        "guard_bridge_import_once": guard_text.count(
            'from "./preset-mount-sanitizer-runner-bridge.mjs"'
        )
        == 1,
        "guard_mount_bridge_call_once": guard_text.count(
            "await mountWithSanitizedTerminal("
        )
        == 1,
        "guard_native_mount_binding_once": guard_text.count(
            "agentCtx.agentPresets.mount.bind(agentCtx.agentPresets)"
        )
        == 1,
        "runner_preset_terminal_branch_once": runner_text.count(
            "error instanceof PresetMountSanitizedTerminalError"
        )
        == 1,
        "runner_preset_terminal_emit_once": runner_text.count(
            'emit("preset_mount_failure_attributed", null)'
        )
        == 1,
        "runner_broader_fallback_once": runner_text.count(
            "sanitizeEffectiveToolTerminal(error)"
        )
        == 1,
        "preset_precedes_broader_fallback": runner_text.index(
            "error instanceof PresetMountSanitizedTerminalError"
        )
        < runner_text.index("sanitizeEffectiveToolTerminal(error)"),
        "no_raw_dynamic_projection": all(
            token not in bridge_text + guard_text + runner_text
            for token in (
                "error.stack",
                "error.cause",
                "String(error)",
                "error.path",
                "error.prompt",
                "error.response",
                "process.env",
            )
        ),
        "no_fixture_dsh_import": "@deepseek-ai/" not in fixture_source.decode("utf-8"),
    }
    if not all(bridge_checks.values()):
        failed = sorted(key for key, value in bridge_checks.items() if not value)
        raise RunnerBridgeError("bridge_shape_rejected:" + ",".join(failed))
    return {
        "source_sha256": bindings,
        "bridge_checks": bridge_checks,
        "accepted_runner_projection": runner_projection,
        "derived_runner_bytes": len(runner_source),
        "derived_guard_bytes": len(guard_source),
    }


def load_contract() -> dict[str, Any]:
    contract = _load_object(CONTRACT_PATH)
    _validate(CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected")
    if (
        contract["schema_version"] != CONTRACT_SCHEMA_VERSION
        or contract["operation_id"] != OPERATION_ID
        or contract["plan_sha256"] != sha256_file(PLAN_PATH)
        or contract["threat_model_sha256"] != sha256_file(THREAT_PATH)
        or contract["accepted_minimum_environment_evidence"]
        != ACCEPTED_EVIDENCE_PATH.relative_to(REPO_ROOT).as_posix()
        or contract["accepted_runner_generator"]
        != ACCEPTED_RUNNER_GENERATOR_PATH.relative_to(REPO_ROOT).as_posix()
        or contract["accepted_guard_generator"]
        != ACCEPTED_GUARD_GENERATOR_PATH.relative_to(REPO_ROOT).as_posix()
        or contract["sanitizer"] != SANITIZER_PATH.relative_to(REPO_ROOT).as_posix()
        or contract["bridge"] != BRIDGE_PATH.relative_to(REPO_ROOT).as_posix()
        or contract["fixture"] != FIXTURE_PATH.relative_to(REPO_ROOT).as_posix()
        or contract["closed_codes"] != EXPECTED_CODES
        or contract["expected_fixture_results"] != EXPECTED_RESULTS
        or contract["execution"]
        != {
            "attempt_id": "attempt-001",
            "pure_node_fixture_process_count": 1,
            "native_harness_process_count": 0,
            "automatic_retry": False,
            "manual_retry": False,
        }
    ):
        raise RunnerBridgeError("contract_semantics_rejected")
    if contract["required_zero_counters"] != [
        "native_harness_process_count",
        "dsh_import_count",
        "turn_count",
        "request_count",
        "broker_process_count",
        "broker_request_count",
        "occupied_worker_count",
        "model_request_count",
        "provider_request_count",
        "network_attempt_count",
        "database_invocation_count",
        "docker_invocation_count",
        "target_creation_count",
        "target_use_count",
    ]:
        raise RunnerBridgeError("required_zero_counters_rejected")
    planning_source = contract["planning_source"]
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        FULL_OID.fullmatch(planning_source) is None
        or planning_source
        != _git("rev-parse", "--verify", f"{planning_source}^{{commit}}")
        or planning_source != _git("log", "-1", "--format=%H", "--", plan_relative)
    ):
        raise RunnerBridgeError("planning_source_rejected")
    accepted = _load_object(ACCEPTED_EVIDENCE_PATH)
    if (
        accepted.get("result") != "pass"
        or accepted.get("candidate_source")
        != contract["accepted_minimum_environment_execution_source"]
        or accepted.get("claim_boundary", {}).get("sanitizer_admitted") is not True
        or accepted.get("claim_boundary", {}).get("runner_integrated") is not False
    ):
        raise RunnerBridgeError("accepted_sanitizer_evidence_rejected")
    validate_source_derivation(contract)
    return contract


def environment_projection() -> dict[str, Any]:
    return accepted_sanitizer.environment_projection()


def build_process_envelope(
    *, candidate_source: str, returncode: int, stdout: str, stderr: str
) -> dict[str, Any]:
    envelope = {
        "schema_version": PROCESS_ENVELOPE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "numeric_exit_code": returncode,
        "stdout_bytes": len(stdout.encode("utf-8")),
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr_bytes": len(stderr.encode("utf-8")),
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "stream_content_retained": False,
        "raw_runtime_detail_retained": False,
        "environment": environment_projection(),
        "node_process_count": 1,
        "native_harness_process_count": 0,
        "dsh_import_count": 0,
        "further_process_authorized": False,
    }
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH,
        envelope,
        "process_envelope_schema_rejected",
    )
    return envelope


def _verify_execution_git_snapshot() -> str:
    head = _git("rev-parse", "HEAD")
    upstream = _git("rev-parse", "@{upstream}")
    if FULL_OID.fullmatch(head) is None or head != upstream:
        raise RunnerBridgeError("execution_head_origin_mismatch")
    if _git("status", "--porcelain=v1", "--untracked-files=no"):
        raise RunnerBridgeError("execution_tracked_worktree_not_clean")
    return head


def _ensure_fresh_output_paths() -> None:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise RunnerBridgeError("runner_bridge_output_already_exists")


def run_fixture_once(candidate_source: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    node = accepted_sanitizer._resolved_node_executable()
    child_environment = accepted_sanitizer.minimum_windows_environment()
    try:
        completed = subprocess.run(
            [str(node), str(FIXTURE_PATH)],
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
        raise RunnerBridgeError("pure_fixture_process_failed") from error
    envelope = build_process_envelope(
        candidate_source=candidate_source,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    PROCESS_ENVELOPE_PATH.write_bytes(canonical_bytes(envelope))
    if completed.returncode != 0 or completed.stderr != "":
        raise RunnerBridgeError("pure_fixture_process_rejected")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RunnerBridgeError("pure_fixture_stdout_invalid") from error
    if value != EXPECTED_RESULTS:
        raise RunnerBridgeError("pure_fixture_vector_mismatch")
    return value, envelope


def build_evidence(
    *,
    candidate_source: str,
    contract: dict[str, Any],
    derivation: dict[str, Any],
    results: list[dict[str, Any]],
    envelope: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "candidate_source": candidate_source,
        "result": "pass",
        "source_sha256": derivation["source_sha256"],
        "bridge_checks": derivation["bridge_checks"],
        "derived_runner_bytes": derivation["derived_runner_bytes"],
        "derived_guard_bytes": derivation["derived_guard_bytes"],
        "closed_codes": contract["closed_codes"],
        "fixture_results": results,
        "fixture": {
            "attempt_id": "attempt-001",
            "authored_synthetic": True,
            "node_process_count": 1,
            "native_harness_process_count": 0,
            "dsh_import_count": 0,
            "child_process_count": 0,
            "network_api_count": 0,
            "filesystem_api_count": 0,
            "result_count": len(results),
            "stdout_exact": True,
            "stderr_bytes": 0,
        },
        "environment": environment_projection(),
        "process_envelope_sha256": sha256_bytes(canonical_bytes(envelope)),
        "claim_boundary": {
            "sanitizer_admitted": True,
            "runner_bridge_deterministically_admitted": True,
            "runner_executed": False,
            "native_harness_process_authorized": False,
            "worker_launch_authorized": False,
            "occupied_model_launch_authorized": False,
            "provider_request_authorized": False,
            "retry_authorized": False,
            "raw_runtime_detail_retained": False,
        },
        "zero_counters": {
            "native_harness_process_count": 0,
            "dsh_import_count": 0,
            "turn_count": 0,
            "request_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "occupied_worker_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": 0,
            "database_invocation_count": 0,
            "docker_invocation_count": 0,
            "target_creation_count": 0,
            "target_use_count": 0,
        },
    }


def validate_evidence(evidence: dict[str, Any]) -> None:
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    if evidence["fixture_results"] != EXPECTED_RESULTS:
        raise RunnerBridgeError("evidence_fixture_vector_mismatch")


def _render_report(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    return f"""# Native Harness preset-mount sanitizer runner-bridge report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **passed**

- Candidate source: `{evidence['candidate_source']}`
- Pure Node fixture processes: `1`
- Native Harness processes / DSH imports: `0 / 0`
- Closed fixture results: `{len(evidence['fixture_results'])}`
- Sanitizer admitted: `true`
- Runner bridge deterministically admitted: `true`
- Runner executed: `false`
- Worker/model/provider requests: `0 / 0 / 0`
- Stream content or environment values retained: `false / false`

The exact accepted runner and guard generators now have a deterministic source
descendant that places the admitted stage/code/null-detail sanitizer ahead of
the broader composition fallback at the exact mount boundary. This is source
and pure-fixture evidence only. It does not start DSH or the native Harness and
does not admit a worker, model/provider request, target or product authority.
"""


def deterministic_check() -> dict[str, Any]:
    contract = load_contract()
    derivation = validate_source_derivation(contract)
    existing = [path.exists() for path in OUTPUT_PATHS]
    if any(existing) and not all(existing):
        raise RunnerBridgeError("runner_bridge_partial_output_state")
    result = {
        "status": "passed",
        "operation_id": OPERATION_ID,
        "artifact_state": "fresh",
        "native_harness_process_count": 0,
        "dsh_import_count": 0,
    }
    if all(existing):
        evidence = _load_object(EVIDENCE_PATH)
        envelope = _load_object(PROCESS_ENVELOPE_PATH)
        validate_evidence(evidence)
        _validate(
            PROCESS_ENVELOPE_SCHEMA_PATH,
            envelope,
            "process_envelope_schema_rejected",
        )
        if evidence["process_envelope_sha256"] != sha256_bytes(
            canonical_bytes(envelope)
        ):
            raise RunnerBridgeError("process_envelope_binding_mismatch")
        result.update(
            {
                "artifact_state": "accepted",
                "candidate_source": evidence["candidate_source"],
                "node_process_count": evidence["fixture"]["node_process_count"],
                "runner_bridge_deterministically_admitted": evidence[
                    "claim_boundary"
                ]["runner_bridge_deterministically_admitted"],
            }
        )
    result["bridge_check_count"] = len(derivation["bridge_checks"])
    return result


def execute_rehearsal() -> dict[str, Any]:
    _ensure_fresh_output_paths()
    contract = load_contract()
    derivation = validate_source_derivation(contract)
    candidate_source = _verify_execution_git_snapshot()
    results, envelope = run_fixture_once(candidate_source)
    evidence = build_evidence(
        candidate_source=candidate_source,
        contract=contract,
        derivation=derivation,
        results=results,
        envelope=envelope,
    )
    validate_evidence(evidence)
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(_render_report(evidence), encoding="utf-8", newline="\n")
    return deterministic_check()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        result = execute_rehearsal() if args.execute else deterministic_check()
    except (
        RunnerBridgeError,
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"status": "failed", "error": type(error).__name__}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
