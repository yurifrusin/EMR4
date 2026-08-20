"""Deterministic and occupied controls for one native Harness synthetic edit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import secrets
import shutil
import stat
import subprocess
import threading
import time
from typing import Any

import jsonschema
import yaml

from orchestration_harness.transactional_closeout import (
    sha256 as canonical_object_sha256,
)
from orchestration_harness import native_startup_terminal as startup_terminal

from scripts import (
    deepseek_native_harness_provider_free_effective_tool_composition_guard as guard,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as projection,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
)
ATTEMPT_TWO_OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-002"
)
ATTEMPT_THREE_OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-003"
)
EXECUTION_OPERATION_ID = OPERATION_ID
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "deterministic-evidence.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "deterministic-evidence.schema.json"
REPORT_PATH = CONTINUITY_ROOT / "deterministic-report.md"
CHECKPOINT_PATH = CONTINUITY_ROOT / "occupied-preexecution-checkpoint.json"
PREPARATION_PATH = CONTINUITY_ROOT / "occupied-attempt-preparation.json"
WORK_ORDER_PATH = CONTINUITY_ROOT / "work-order-v2.json"
AUTHORITY_PATH = CONTINUITY_ROOT / "worker-authority.json"
FORBIDDEN_PATH = CONTINUITY_ROOT / "forbidden-surfaces.json"
COMMAND_MANIFEST_PATH = CONTINUITY_ROOT / "command-manifest.json"
NO_DATABASE_ADMISSION_PATH = CONTINUITY_ROOT / "provider-free-no-database-admission.json"
CONSUMED_PATH = CONTINUITY_ROOT / "occupied-attempt-consumed.json"
TERMINAL_PATH = CONTINUITY_ROOT / "occupied-terminal.json"
TERMINAL_SCHEMA_PATH = CONTINUITY_ROOT / "occupied-terminal.schema.json"
NATIVE_REPORT_PATH = CONTINUITY_ROOT / "occupied-report.md"
PRE_HMR_TERMINAL_PATH = CONTINUITY_ROOT / "pre-hmr-startup-terminal.json"
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
BROKER_PATH = REPO_ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs"
MATERIALIZATION_ROOT = projection.MATERIALIZATION_SOURCE_ROOT
WORK_ORDER_SCHEMA_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-provider-free-no-database-manifest-runner-admission-repair"
    / "work-order-v2.schema.json"
)
TRANSACTION_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-governance-clockwork"
    / "transaction.json"
)
LATCH_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-active-operation-latch"
    / "current.json"
)
ATTEMPT_ROOT = Path(
    "C:/Users/sarashera/EMR4-worktrees/deepseek-native-synthetic-window-worker-001"
)
ATTEMPT_ID = "deepseek-native-synthetic-window-worker-001"
WORK_ORDER_ID = "wo-synthetic-native-window-worker-001"
LEASE_ID = "lease-synthetic-native-window-worker-001"

CONTRACT_SCHEMA = "ariadne.synthetic_native_worker_contract.v1"
EVIDENCE_SCHEMA = "ariadne.synthetic_native_worker_deterministic_evidence.v1"
TERMINAL_SCHEMA = "ariadne.synthetic_native_worker_occupied_terminal.v1"
EXPECTED_TOOLS = ["edit", "glob", "read"]
SYNTHETIC_PATH = "synthetic_window_coalescer.py"
SUCCESS_COORDINATE = "ONE_REQUEST_SYNTHETIC_EDIT_ADMITTED"
FAILURE_COORDINATES = [
    "TOOL_BATCH_EMPTY",
    "TOOL_BATCH_MULTIPLE",
    "TOOL_NOT_EDIT",
    "TOOL_CALL_NESTED",
    "TOOL_PATH_MISMATCH",
    "TOOL_ARGUMENT_SHAPE_MISMATCH",
    "TOOL_RESULT_FAILED",
    "TOOL_POST_DECISION_NOT_ACCEPTED",
]
FULL_OID = re.compile(r"^[0-9a-f]{40}$")

BASELINE_SOURCE = '''"""Authored-synthetic maintenance-window coalescer."""


def coalesce_windows(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return sorted touching or overlapping windows as non-overlapping spans."""
    if not windows:
        return []
    ordered = sorted(windows)
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        current = merged[-1]
        if start <= current[1]:
            # Extend to the incoming boundary when windows overlap.
            current[1] = end
        else:
            merged.append([start, end])
    return [tuple(window) for window in merged]


CASES = {
    "disjoint": ([(0, 2), (4, 6)], [(0, 2), (4, 6)]),
    "overlap": ([(0, 4), (2, 6)], [(0, 6)]),
    "touching": ([(0, 2), (2, 4)], [(0, 4)]),
}


if __name__ == "__main__":
    for name, (windows, expected) in CASES.items():
        actual = coalesce_windows(windows)
        if actual != expected:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
'''

EXPECTED_SOURCE = '''"""Authored-synthetic maintenance-window coalescer."""


def coalesce_windows(windows: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return sorted touching or overlapping windows as non-overlapping spans."""
    if not windows:
        return []
    ordered = sorted(windows)
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        current = merged[-1]
        if start <= current[1]:
            # Preserve the furthest boundary when windows overlap or nest.
            current[1] = max(current[1], end)
        else:
            merged.append([start, end])
    return [tuple(window) for window in merged]


CASES = {
    "disjoint": ([(0, 2), (4, 6)], [(0, 2), (4, 6)]),
    "overlap": ([(0, 4), (2, 6)], [(0, 6)]),
    "touching": ([(0, 2), (2, 4)], [(0, 4)]),
    "nested": ([(0, 10), (2, 3)], [(0, 10)]),
}


if __name__ == "__main__":
    for name, (windows, expected) in CASES.items():
        actual = coalesce_windows(windows)
        if actual != expected:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
'''


class RehearsalError(RuntimeError):
    """A frozen rehearsal invariant failed closed."""


def attempt_two_configuration() -> dict[str, Any]:
    """Return the exact attempt-002 identity without touching attempt-001 evidence."""

    evidence_root = CONTINUITY_ROOT / "attempt-002"
    attempt_id = "deepseek-native-synthetic-window-worker-002"
    return {
        "operation_id": ATTEMPT_TWO_OPERATION_ID,
        "attempt_id": attempt_id,
        "attempt_root": Path(f"C:/Users/sarashera/EMR4-worktrees/{attempt_id}"),
        "checkpoint_path": evidence_root / "occupied-preexecution-checkpoint.json",
        "preparation_path": evidence_root / "occupied-attempt-preparation.json",
        "work_order_path": evidence_root / "work-order-v2.json",
        "authority_path": evidence_root / "worker-authority.json",
        "forbidden_path": evidence_root / "forbidden-surfaces.json",
        "command_manifest_path": evidence_root / "command-manifest.json",
        "no_database_admission_path": evidence_root
        / "provider-free-no-database-admission.json",
        "consumed_path": evidence_root / "occupied-attempt-consumed.json",
        "terminal_path": evidence_root / "occupied-terminal.json",
        "terminal_schema_path": evidence_root / "occupied-terminal.schema.json",
        "native_report_path": evidence_root / "occupied-report.md",
        "pre_hmr_terminal_path": evidence_root / "pre-hmr-startup-terminal.json",
        "work_order_id": "wo-synthetic-native-window-worker-002",
        "lease_id": "lease-synthetic-native-window-worker-002",
    }


def attempt_three_configuration() -> dict[str, Any]:
    """Return the new attempt-003 identity without touching earlier evidence."""

    evidence_root = CONTINUITY_ROOT / "attempt-003"
    attempt_id = "deepseek-native-synthetic-window-worker-003"
    return {
        "operation_id": ATTEMPT_THREE_OPERATION_ID,
        "attempt_id": attempt_id,
        "attempt_root": Path(f"C:/Users/sarashera/EMR4-worktrees/{attempt_id}"),
        "checkpoint_path": evidence_root / "occupied-preexecution-checkpoint.json",
        "preparation_path": evidence_root / "occupied-attempt-preparation.json",
        "work_order_path": evidence_root / "work-order-v2.json",
        "authority_path": evidence_root / "worker-authority.json",
        "forbidden_path": evidence_root / "forbidden-surfaces.json",
        "command_manifest_path": evidence_root / "command-manifest.json",
        "no_database_admission_path": evidence_root
        / "provider-free-no-database-admission.json",
        "consumed_path": evidence_root / "occupied-attempt-consumed.json",
        "terminal_path": evidence_root / "occupied-terminal.json",
        "terminal_schema_path": evidence_root / "occupied-terminal.schema.json",
        "native_report_path": evidence_root / "occupied-report.md",
        "pre_hmr_terminal_path": evidence_root / "pre-hmr-startup-terminal.json",
        "work_order_id": "wo-synthetic-native-window-worker-003",
        "lease_id": "lease-synthetic-native-window-worker-003",
    }


def configure_attempt_two() -> None:
    """Select the separately authorised attempt-002 runtime surfaces."""

    global EXECUTION_OPERATION_ID
    global CHECKPOINT_PATH, PREPARATION_PATH, WORK_ORDER_PATH
    global AUTHORITY_PATH, FORBIDDEN_PATH, COMMAND_MANIFEST_PATH
    global NO_DATABASE_ADMISSION_PATH, CONSUMED_PATH, TERMINAL_PATH
    global TERMINAL_SCHEMA_PATH, NATIVE_REPORT_PATH, PRE_HMR_TERMINAL_PATH
    global ATTEMPT_ROOT, ATTEMPT_ID, WORK_ORDER_ID, LEASE_ID

    value = attempt_two_configuration()
    EXECUTION_OPERATION_ID = value["operation_id"]
    CHECKPOINT_PATH = value["checkpoint_path"]
    PREPARATION_PATH = value["preparation_path"]
    WORK_ORDER_PATH = value["work_order_path"]
    AUTHORITY_PATH = value["authority_path"]
    FORBIDDEN_PATH = value["forbidden_path"]
    COMMAND_MANIFEST_PATH = value["command_manifest_path"]
    NO_DATABASE_ADMISSION_PATH = value["no_database_admission_path"]
    CONSUMED_PATH = value["consumed_path"]
    TERMINAL_PATH = value["terminal_path"]
    TERMINAL_SCHEMA_PATH = value["terminal_schema_path"]
    NATIVE_REPORT_PATH = value["native_report_path"]
    PRE_HMR_TERMINAL_PATH = value["pre_hmr_terminal_path"]
    ATTEMPT_ROOT = value["attempt_root"]
    ATTEMPT_ID = value["attempt_id"]
    WORK_ORDER_ID = value["work_order_id"]
    LEASE_ID = value["lease_id"]


def configure_attempt_three() -> None:
    """Select Yuri's separately authorised attempt-003 runtime surfaces."""

    global EXECUTION_OPERATION_ID
    global CHECKPOINT_PATH, PREPARATION_PATH, WORK_ORDER_PATH
    global AUTHORITY_PATH, FORBIDDEN_PATH, COMMAND_MANIFEST_PATH
    global NO_DATABASE_ADMISSION_PATH, CONSUMED_PATH, TERMINAL_PATH
    global TERMINAL_SCHEMA_PATH, NATIVE_REPORT_PATH, PRE_HMR_TERMINAL_PATH
    global ATTEMPT_ROOT, ATTEMPT_ID, WORK_ORDER_ID, LEASE_ID

    value = attempt_three_configuration()
    EXECUTION_OPERATION_ID = value["operation_id"]
    CHECKPOINT_PATH = value["checkpoint_path"]
    PREPARATION_PATH = value["preparation_path"]
    WORK_ORDER_PATH = value["work_order_path"]
    AUTHORITY_PATH = value["authority_path"]
    FORBIDDEN_PATH = value["forbidden_path"]
    COMMAND_MANIFEST_PATH = value["command_manifest_path"]
    NO_DATABASE_ADMISSION_PATH = value["no_database_admission_path"]
    CONSUMED_PATH = value["consumed_path"]
    TERMINAL_PATH = value["terminal_path"]
    TERMINAL_SCHEMA_PATH = value["terminal_schema_path"]
    NATIVE_REPORT_PATH = value["native_report_path"]
    PRE_HMR_TERMINAL_PATH = value["pre_hmr_terminal_path"]
    ATTEMPT_ROOT = value["attempt_root"]
    ATTEMPT_ID = value["attempt_id"]
    WORK_ORDER_ID = value["work_order_id"]
    LEASE_ID = value["lease_id"]


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def canonical_pretty_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def tracked_git_blob_sha256(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as error:
        raise RehearsalError("git_blob_path_outside_repository") from error
    for staged in (False, True):
        args = ["git", "-C", str(REPO_ROOT), "diff"]
        if staged:
            args.append("--cached")
        args.extend(["--quiet", "--", relative])
        clean = subprocess.run(
            args,
            check=False,
            capture_output=True,
            timeout=15,
        )
        if clean.returncode != 0:
            raise RehearsalError("bound_predecessor_not_tracked_clean")
    blob = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", f"HEAD:{relative}"],
        check=False,
        capture_output=True,
        timeout=15,
    )
    if blob.returncode != 0:
        raise RehearsalError("bound_predecessor_git_blob_unavailable")
    return sha256_bytes(blob.stdout)


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if completed.returncode != 0:
        raise RehearsalError("git_object_resolution_failed")
    return completed.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalError("json_object_required")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


def write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_json(value))


def _clear_readonly_then_retry(
    function: Any, path: str, _error: BaseException
) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def remove_exact_attempt_root(root: Path, parent: Path) -> bool:
    resolved_root = root.resolve()
    resolved_parent = parent.resolve()
    if (
        resolved_root.parent != resolved_parent
        or resolved_root.name != ATTEMPT_ROOT.name
        or resolved_root.is_symlink()
    ):
        raise RehearsalError("attempt_cleanup_scope_invalid")
    for attempt in range(26):
        try:
            if resolved_root.exists():
                shutil.rmtree(resolved_root, onexc=_clear_readonly_then_retry)
            return not resolved_root.exists()
        except OSError:
            if attempt == 25:
                return False
            time.sleep(0.2)
    return False


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = load_json(path)
    jsonschema.Draft202012Validator(load_json(CONTRACT_SCHEMA_PATH)).validate(value)
    if value.get("schema_version") != CONTRACT_SCHEMA:
        raise RehearsalError("contract_schema_mismatch")
    if value.get("operation_id") != OPERATION_ID:
        raise RehearsalError("contract_operation_mismatch")
    if value.get("allowed_tool_names") != EXPECTED_TOOLS:
        raise RehearsalError("contract_tool_view_mismatch")
    source = value.get("planning_source")
    if not isinstance(source, str) or FULL_OID.fullmatch(source) is None:
        raise RehearsalError("planning_source_not_full_git_oid")
    if git("rev-parse", "--verify", f"{source}^{{commit}}") != source:
        raise RehearsalError("planning_source_not_resolved_exact_commit")
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if git("log", "-1", "--format=%H", "--", plan_relative) != source:
        raise RehearsalError("planning_source_not_plan_commit")
    ancestry = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", source, "HEAD"],
        check=False,
        capture_output=True,
        timeout=15,
    )
    if ancestry.returncode != 0:
        raise RehearsalError("planning_source_not_ancestor_of_head")
    package = value.get("work_package", {})
    if package.get("path") != SYNTHETIC_PATH:
        raise RehearsalError("work_package_path_mismatch")
    if package.get("baseline_sha256") != sha256_bytes(BASELINE_SOURCE.encode()):
        raise RehearsalError("baseline_digest_mismatch")
    if package.get("expected_sha256") != sha256_bytes(EXPECTED_SOURCE.encode()):
        raise RehearsalError("expected_digest_mismatch")
    return value


def bind_predecessors(contract: dict[str, Any]) -> list[dict[str, Any]]:
    bound: list[dict[str, Any]] = []
    roles: set[str] = set()
    for row in contract["predecessor_files"]:
        if set(row) != {"role", "path", "sha256"}:
            raise RehearsalError("predecessor_shape_mismatch")
        role = row["role"]
        path = (REPO_ROOT / row["path"]).resolve()
        if role in roles or REPO_ROOT.resolve() not in path.parents or not path.is_file():
            raise RehearsalError("predecessor_path_invalid")
        if tracked_git_blob_sha256(path) != row["sha256"]:
            raise RehearsalError("predecessor_digest_mismatch")
        roles.add(role)
        bound.append({"role": role, "sha256": row["sha256"]})
    return bound


def task_text(target_path: str) -> str:
    return f"""You are one bounded DeepSeek worker in an authored-synthetic, non-product rehearsal. The workspace contains only {SYNTHETIC_PATH}. Make exactly one model-requested tool call and it must be `edit` on `{target_path}`. Do not call read or glob, do not create files, and do not provide a later summary. The complete baseline is below, so no inspection turn is needed.

Repair the nested-window defect: overlapping or nested windows must preserve the furthest current end, update the adjacent explanatory comment accurately, and append exactly one `nested` regression row for input [(0, 10), (2, 3)] with expected [(0, 10)]. Preserve every other byte and contract. Use one literal edit that spans both required changes.

--- baseline ---
{BASELINE_SOURCE}--- end baseline ---
"""


def classify_tool_batch(calls: list[dict[str, Any]]) -> str:
    if not calls:
        return "TOOL_BATCH_EMPTY"
    if len(calls) != 1:
        return "TOOL_BATCH_MULTIPLE"
    call = calls[0]
    if call.get("name") != "edit":
        return "TOOL_NOT_EDIT"
    if call.get("direct") is not True:
        return "TOOL_CALL_NESTED"
    if call.get("path") != SYNTHETIC_PATH:
        return "TOOL_PATH_MISMATCH"
    if call.get("argument_shape") != "literal_single_replace":
        return "TOOL_ARGUMENT_SHAPE_MISMATCH"
    if call.get("is_error") is not False:
        return "TOOL_RESULT_FAILED"
    if call.get("post_decision") != "accept":
        return "TOOL_POST_DECISION_NOT_ACCEPTED"
    return SUCCESS_COORDINATE


def fixture_matrix() -> list[dict[str, Any]]:
    valid = {
        "name": "edit",
        "direct": True,
        "path": SYNTHETIC_PATH,
        "argument_shape": "literal_single_replace",
        "is_error": False,
        "post_decision": "accept",
    }
    scenarios: list[tuple[str, list[dict[str, Any]], str]] = [
        ("success", [valid], SUCCESS_COORDINATE),
        ("empty", [], "TOOL_BATCH_EMPTY"),
        ("multiple", [valid, valid], "TOOL_BATCH_MULTIPLE"),
    ]
    mutations = [
        ("wrong_tool", "name", "read", "TOOL_NOT_EDIT"),
        ("nested", "direct", False, "TOOL_CALL_NESTED"),
        ("wrong_path", "path", "other.py", "TOOL_PATH_MISMATCH"),
        ("wrong_shape", "argument_shape", "replace_all", "TOOL_ARGUMENT_SHAPE_MISMATCH"),
        ("failed", "is_error", True, "TOOL_RESULT_FAILED"),
        ("blocked", "post_decision", "block", "TOOL_POST_DECISION_NOT_ACCEPTED"),
    ]
    for name, field, replacement, expected in mutations:
        row = dict(valid)
        row[field] = replacement
        scenarios.append((name, [row], expected))
    results = []
    for name, calls, expected in scenarios:
        observed = classify_tool_batch(calls)
        if observed != expected:
            raise RehearsalError("fixture_classification_mismatch")
        results.append({"scenario": name, "coordinate": observed})
    return results


def source_semantics() -> dict[str, Any]:
    package_root = MATERIALIZATION_ROOT / "node_modules" / "@deepseek-ai"
    tool_source = (package_root / "dsh-tools" / "lib" / "index.js").read_text(
        encoding="utf-8"
    )
    edit_source = (package_root / "dsh-tool-fs" / "lib" / "index.js").read_text(
        encoding="utf-8"
    )
    loop_source = (package_root / "dsh-agent-loop" / "lib" / "index.js").read_text(
        encoding="utf-8"
    )
    checks = {
        "accepted_guard_exact_tools": guard.EXPECTED_TOOLS == ("edit", "glob", "read"),
        "official_edit_registered": 'name: "edit"' in edit_source,
        "official_edit_is_literal": "oldString: input.oldString" in edit_source,
        "official_edit_is_atomic": "ctx.fs.editText(target" in edit_source,
        "runtime_has_conclusion_method": "concludeTurn()" in tool_source,
        "conclusion_uses_execution_identity": "concludingExecutions.add(this)" in tool_source,
        "success_materializes_conclusion": (
            "const concludesTurn = this.concludingExecutions.has(exec);" in tool_source
            and "...concludesTurn ? { concludesTurn: true } : {}" in tool_source
        ),
        "loop_stops_after_concluded_result": (
            'return concluded ? { kind: "completed" } : null;' in loop_source
        ),
        "broker_has_optional_one_request_allowance": (
            "EMR4_BROKER_MAX_PROVIDER_CALLS" in BROKER_PATH.read_text(encoding="utf-8")
            and "provider-call-allowance-exhausted" in BROKER_PATH.read_text(encoding="utf-8")
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, value in checks.items() if not value)
        raise RehearsalError("source_semantics_failed:" + ",".join(failed))
    return {
        "checks": checks,
        "dsh_tools_sha256": file_sha256(package_root / "dsh-tools" / "lib" / "index.js"),
        "dsh_tool_fs_sha256": file_sha256(package_root / "dsh-tool-fs" / "lib" / "index.js"),
        "dsh_agent_loop_sha256": file_sha256(package_root / "dsh-agent-loop" / "lib" / "index.js"),
        "broker_sha256": file_sha256(BROKER_PATH),
        "effective_tool_guard_sha256": sha256_bytes(guard.build_guard_source()),
    }


def runner_source(target_path: str) -> bytes:
    safe_target = json.dumps(target_path)
    return f'''import {{ createHash, randomUUID }} from "node:crypto";
import {{ closeSync, openSync, writeFileSync }} from "node:fs";
import {{ resolve }} from "node:path";
import {{ installModelSelection }} from "@deepseek-ai/dsh-agent";
import {{ createUserMessage }} from "@deepseek-ai/dsh-llm";
import {{ SessionId }} from "@deepseek-ai/dsh-session";
import {{ assertEffectiveToolComposition }} from "./effective-tool-guard.mjs";

export const name = "synthetic-one-request-worker-runner";
export const inject = ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"];
const TARGET_PATH = {safe_target};
const TOOLS = Object.freeze(["edit", "glob", "read"]);

function digest(value) {{ return "sha256:" + createHash("sha256").update(value).digest("hex"); }}
function writeTerminal(path, value) {{
  const descriptor = openSync(path, "wx");
  try {{ writeFileSync(descriptor, JSON.stringify(value) + "\\n", "utf8"); }}
  finally {{ closeSync(descriptor); }}
}}
function summarize(events, firstSeq) {{
  const toolNames = [];
  let requestCount = 0;
  let toolResultCount = 0;
  let turnKind = null;
  for (const event of events) {{
    if (event.seq < firstSeq) continue;
    if (event.type === "request/header") requestCount += 1;
    if (event.type === "tool/call") toolNames.push(typeof event.data?.name === "string" ? event.data.name : "unknown");
    if (event.type === "tool/result") toolResultCount += 1;
    if (event.type === "turn/end") turnKind = event.data?.reason?.kind ?? "unknown";
  }}
  return {{ request_count: requestCount, tool_names: toolNames, tool_result_count: toolResultCount, turn_kind: turnKind }};
}}

async function run(ctx, config) {{
  await ctx.get("loader")?.await();
  const agents = ctx.get("agents");
  const sessions = ctx.get("sessions");
  const presets = ctx.get("agentPresets");
  if (!agents || !sessions || !presets) throw new Error("REQUIRED_SERVICE_MISSING");
  if (!Array.isArray(presets.roots) || presets.roots.length !== 2 || resolve(presets.roots[0].path) !== resolve(config.shippedRoot) || presets.roots[0].trust !== "system" || resolve(presets.roots[1].path) !== resolve(config.userRoot) || presets.roots[1].trust !== "user") throw new Error("PRESET_ROOT_ROSTER_MISMATCH");
  const sessionText = `session-${{randomUUID()}}`;
  const selection = {{ provider: "deepseek-official", model: "deepseek-v4-flash", reasoningEffort: "high" }};
  let observedCalls = 0;
  let conclusionMarked = false;
  const {{ agent }} = await agents.create({{
    sessionId: SessionId(sessionText),
    meta: {{ cwd: process.cwd() }},
    agentOptions: {{ provider: selection.provider, model: selection.model, maxTokens: 4096 }},
    setup: async (agentCtx) => {{
      await assertEffectiveToolComposition(agentCtx, "emr4-bounded-worker", TOOLS);
      installModelSelection(agentCtx, {{ current: selection, assembled: undefined }});
      agentCtx.on("tools/pre-execute", async (exec, next) => {{
        observedCalls += 1;
        if (!TOOLS.includes(exec.name)) return {{ kind: "deny", reason: "TOOL_NOT_ALLOWLISTED" }};
        if (exec.name === "edit") {{
          const args = exec.arguments;
          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return {{ kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" }};
        }}
        return next();
      }});
      agentCtx.on("tools/post-execute", async (exec, result, next) => {{
        const decision = await next();
        const args = exec.arguments;
        if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true && result.isError === false && decision.kind === "accept") {{
          exec.concludeTurn();
          conclusionMarked = true;
        }}
        return decision;
      }});
    }},
  }});
  await agent.whenIdle();
  const firstSeq = agent.session.seq;
  agent.followup(createUserMessage({{ content: [{{ type: "text", text: config.task }}], source: {{ kind: "user" }} }}));
  await agent.whenIdle();
  await sessions.flush(agent.session);
  const summary = summarize(agent.session.events, firstSeq);
  const passed = summary.request_count === 1 && summary.tool_names.length === 1 && summary.tool_names[0] === "edit" && summary.tool_result_count === 1 && summary.turn_kind === "completed" && conclusionMarked;
  writeTerminal(config.terminalPath, {{
    schema_version: "ariadne.synthetic_native_worker_runner_terminal.v1",
    status: passed ? "completed" : "failed",
    session_id_sha256: digest(sessionText),
    provider: selection.provider,
    model: selection.model,
    reasoning_effort: selection.reasoningEffort,
    allowed_tool_names: TOOLS,
    conclusion_marked: conclusionMarked,
    ...summary,
  }});
  ctx.get("appExit")(passed ? 0 : 1);
}}

export function apply(ctx, config) {{
  run(ctx, config).catch(() => {{
    writeTerminal(config.terminalPath, {{
      schema_version: "ariadne.synthetic_native_worker_runner_terminal.v1",
      status: "failed",
      failure_code: "CUSTOM_RUNNER_FAILURE",
      request_count: 0,
      tool_names: [],
      tool_result_count: 0,
      turn_kind: null,
      conclusion_marked: false,
      allowed_tool_names: TOOLS,
    }});
    ctx.get("appExit")(1);
  }});
}}
'''.encode("utf-8")


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    checks = {
        "one_composition_guard": source.count("assertEffectiveToolComposition(agentCtx,") == 1,
        "exact_tool_view": 'Object.freeze(["edit", "glob", "read"])' in source,
        "one_pre_gate": source.count('agentCtx.on("tools/pre-execute"') == 1,
        "one_post_gate": source.count('agentCtx.on("tools/post-execute"') == 1,
        "one_conclusion": source.count("exec.concludeTurn()") == 1,
        "one_followup": source.count("agent.followup(") == 1,
        "exact_root_roster": (
            "presets.roots.length !== 2" in source
            and 'presets.roots[0].trust !== "system"' in source
            and 'presets.roots[1].trust !== "user"' in source
        ),
        "exact_request_success": "summary.request_count === 1" in source,
        "exact_edit_success": 'summary.tool_names[0] === "edit"' in source,
        "no_raw_error": "error.message" not in source and "error.stack" not in source,
        "no_shell_or_subagent": all(token not in source for token in ("pwsh", "bash", "subagent", "workflow")),
    }
    if not all(checks.values()):
        failed = sorted(name for name, value in checks.items() if not value)
        raise RehearsalError("runner_source_invalid:" + ",".join(failed))
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), **checks}


def sentinel_source() -> bytes:
    return b'''import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export const name = "synthetic-worker-hmr-sentinel";
export function apply(ctx, config) {
  function emit(event) {
    const rows = existsSync(config.eventPath) ? readFileSync(config.eventPath, "utf8").split(/\r?\n/).filter(Boolean) : [];
    appendFileSync(config.eventPath, JSON.stringify({ schema_version: "ariadne.synthetic_native_worker_hmr_event.v1", sequence: rows.length + 1, event }) + "\n", "utf8");
  }
  emit("sentinel_activated");
  let ready = false;
  const timer = setInterval(() => {
    if (ready) return;
    const hmr = ctx.get("hmr");
    if (hmr === undefined || !(hmr.configs instanceof Map)) return;
    const observed = new Set([...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()));
    const expected = config.watchedPaths.map((value) => resolve(value).toLowerCase());
    if (!expected.every((value) => observed.has(value))) return;
    ready = true;
    clearInterval(timer);
    emit("stock_headless_hmr_ready");
  }, 20);
  ctx.effect(() => () => clearInterval(timer), "synthetic worker HMR sentinel");
}
'''


def profile_patch(root: Path, port: int, *, changed: bool) -> bytes:
    home = root / "home"
    profile_dir = home / "profiles" / "headless"
    workspace = root / "workspace"
    proof = root / "installation" / "proof"
    events = root / "hmr-events.jsonl"
    runner_terminal = root / "runner-terminal.json"
    preset_root = home / ".agent-presets"
    profile_patch_path = profile_dir / "cordis.patch.yml"
    home_patch_path = home / "cordis.patch.yml"

    def quoted(path: Path) -> str:
        return json.dumps(str(path.resolve()))

    rows = f'''- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- id: session-title-llm
  disabled: true
- id: compaction-basic
  disabled: true
- id: command-compact
  disabled: true
- id: llm-pi-ai
  disabled: true
- id: llm-retry
  disabled: true
- id: tool-bash
  disabled: true
- id: tool-pwsh
  disabled: true
- id: tool-jobs
  disabled: true
- id: tool-skill
  disabled: true
- id: tool-goal
  disabled: true
- id: tool-ralph
  disabled: true
- id: tool-subagent
  disabled: true
- id: tool-subagent-fork
  disabled: true
- id: tool-subagent-control
  disabled: true
- id: tool-subagent-list-agents
  disabled: true
- id: tool-subagent-report
  disabled: true
- id: tool-workflow
  disabled: true
- id: tool-todo
  disabled: true
- id: tool-web
  disabled: true
- id: web-search-deepseek
  disabled: true
- id: tool-str-replace-editor
  disabled: true
- id: sandbox-policy
  config:
    mode: workspace-write
    workspaceRoot: {quoted(workspace)}
- id: approval
  config:
    policy: never
- id: permission
  config:
    defaultPreset: emr4-bounded-worker
    presets:
      emr4-bounded-worker:
        sandbox: workspace-write
        approval: never
- id: fs-sandbox
  config:
    cwd: {quoted(workspace)}
- id: agent-loop
  config:
    agents: []
    maxParallelToolCalls: 1
- id: llm-deepseek
  config:
    apiKeyEnv: DSH_EMR4_BROKER_TOKEN
    baseURL: http://127.0.0.1:{port}
    reasoningEffort: high
    maxTokens: 4096
    streamIdleTimeoutMs: 300000
    retryPolicy:
      mode: normal
      maxRetries: 0
      retryableCodes: [TRANSPORT]
      backoff:
        initialDelayMs: 1
        maxDelayMs: 1
        jitterRatio: 0
- insert:
    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: emr4-bounded-worker
        roots:
          - path: {quoted(preset_root)}
            trust: system
        includeUserRoot: true
    - id: synthetic-worker-hmr-sentinel
      name: {quoted(proof / "sentinel.mjs")}
      config:
        eventPath: {quoted(events)}
        watchedPaths:
          - {quoted(profile_patch_path)}
          - {quoted(home_patch_path)}
'''
    if changed:
        rows += f'''    - id: synthetic-one-request-worker-runner
      name: {quoted(proof / "runner.mjs")}
      inject: [hmr, headlessStartup, agents, sessions, agentPresets]
      config:
        task: !!js ctx.headlessStartup.task
        terminalPath: {quoted(runner_terminal)}
        shippedRoot: {quoted(root / "installation" / "node_modules" / "@deepseek-ai" / "dsh" / "config" / "agent-presets")}
        userRoot: {quoted(preset_root)}
'''
    return rows.encode("utf-8")


def validate_profile_patch(payload: bytes, *, changed: bool) -> dict[str, Any]:
    source = payload.decode("utf-8")
    checks = {
        "default_runner_disabled": "- id: headless-runner\n  disabled: true" in source,
        "retry_plugin_disabled": "- id: llm-retry\n  disabled: true" in source,
        "retry_count_zero": "maxRetries: 0" in source,
        "parallel_width_one": "maxParallelToolCalls: 1" in source,
        "workspace_write_sandbox": "mode: workspace-write" in source,
        "approval_never": "policy: never" in source,
        "accepted_preset": "default: emr4-bounded-worker" in source,
        "derived_user_root_enabled": "includeUserRoot: true" in source,
        "broker_loopback_only": "baseURL: http://127.0.0.1:" in source,
        "surplus_tools_disabled": all(
            f"- id: {name}\n  disabled: true" in source
            for name in ("tool-bash", "tool-pwsh", "tool-web", "tool-subagent")
        ),
        "runner_presence_exact": (
            source.count("- id: synthetic-one-request-worker-runner")
            == (1 if changed else 0)
        ),
        "runner_root_bindings_exact": (
            ("shippedRoot:" in source and "userRoot:" in source)
            if changed
            else ("shippedRoot:" not in source and "userRoot:" not in source)
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, value in checks.items() if not value)
        raise RehearsalError("profile_patch_invalid:" + ",".join(failed))
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), **checks}


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    predecessors = bind_predecessors(contract)
    semantics = source_semantics()
    scenarios = fixture_matrix()
    synthetic_target = "C:/synthetic-native-worker/synthetic_window_coalescer.py"
    runner = validate_runner_source(runner_source(synthetic_target))
    fake_root = Path("C:/synthetic-native-worker")
    initial_profile = validate_profile_patch(
        profile_patch(fake_root, 43123, changed=False), changed=False
    )
    changed_profile = validate_profile_patch(
        profile_patch(fake_root, 43123, changed=True), changed=True
    )
    accepted_preset = projection.native_predecessor.build_preset_source(
        projection.native_predecessor.load_contract()
    )
    if not isinstance(yaml.safe_load(accepted_preset), list):
        raise RehearsalError("accepted_preset_not_array")
    prompt = task_text(synthetic_target).encode("utf-8")
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": "pass",
        "planning_source": contract["planning_source"],
        "predecessors": predecessors,
        "source_semantics": semantics,
        "fixture_matrix": scenarios,
        "runner": runner,
        "profile": {
            "initial": initial_profile,
            "changed": changed_profile,
            "preset_bytes": len(accepted_preset),
            "preset_sha256": sha256_bytes(accepted_preset),
        },
        "work_package": {
            "path": SYNTHETIC_PATH,
            "baseline_bytes": len(BASELINE_SOURCE.encode("utf-8")),
            "baseline_sha256": sha256_bytes(BASELINE_SOURCE.encode("utf-8")),
            "expected_bytes": len(EXPECTED_SOURCE.encode("utf-8")),
            "expected_sha256": sha256_bytes(EXPECTED_SOURCE.encode("utf-8")),
            "prompt_sha256": sha256_bytes(prompt),
            "public_case_count": 4,
            "holdback_case_count": 3,
        },
        "boundary": {
            "native_process_count": 0,
            "agent_session_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "automatic_retry_count": 0,
            "fallback_count": 0,
            "auxiliary_model_call_count": 0,
            "docker_or_database_count": 0,
        },
    }
    jsonschema.Draft202012Validator(load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence


def render_report(value: dict[str, Any]) -> str:
    return f"""# Authored-synthetic native worker deterministic report

- Result: `{value['result']}`
- Source-semantic checks: `{len(value['source_semantics']['checks'])}`
- Hostile/success fixtures: `{len(value['fixture_matrix'])}`
- Effective tools: `edit`, `glob`, `read`
- Work package: `{value['work_package']['path']}`
- Baseline / expected SHA-256: `{value['work_package']['baseline_sha256']}` / `{value['work_package']['expected_sha256']}`
- Native/session/model/provider/Docker/database counts: all `0`

The pinned rc.7 source supports an in-process successful-tool turn conclusion,
and the frozen synthetic task has an exact one-edit success path. This report
does not contain an occupied worker or provider result.
"""


def build_artifacts() -> dict[str, Any]:
    value = deterministic_evidence()
    write_json(EVIDENCE_PATH, value)
    REPORT_PATH.write_text(render_report(value), encoding="utf-8", newline="\n")
    return value


def git_at(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
    )
    if completed.returncode != 0:
        raise RehearsalError("git_readback_failed")
    return completed.stdout.strip()


def validate_authority_boundary() -> None:
    if git("branch", "--show-current") != "codex/ariadne-bernie-davida-parallel-seam":
        raise RehearsalError("task_branch_mismatch")
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    for ref in ("master", "origin/master", "handoff/current", "origin/handoff/current"):
        if git("rev-parse", "--verify", ref) != protected:
            raise RehearsalError("protected_ref_mismatch")
    latch = load_json(LATCH_PATH)
    if (
        latch.get("operation_id") != EXECUTION_OPERATION_ID
        or latch.get("status") != "in_progress"
        or latch.get("user_attention", {}).get("required") is not False
        or latch.get("terminal_response", {}).get("permitted") is not False
    ):
        raise RehearsalError("active_operation_latch_mismatch")


def validate_review_receipt(path: Path, candidate_source: str) -> dict[str, Any]:
    resolved = path.resolve()
    if REPO_ROOT.resolve() not in resolved.parents or not resolved.is_file():
        raise RehearsalError("review_receipt_path_invalid")
    receipt = load_json(resolved)
    decision = receipt.get("decision", receipt.get("status"))
    if decision not in {"pass", "passed", "accepted"}:
        raise RehearsalError("review_receipt_not_passed")
    if receipt.get("head_before") != candidate_source:
        raise RehearsalError("review_head_before_mismatch")
    if receipt.get("head_after") != candidate_source:
        raise RehearsalError("review_head_after_mismatch")
    if receipt.get("dirty_after") is not False:
        raise RehearsalError("review_not_clean")
    return receipt


def resolve_reviewed_candidate_source(path: Path) -> str:
    resolved = path.resolve()
    if REPO_ROOT.resolve() not in resolved.parents or not resolved.is_file():
        raise RehearsalError("review_receipt_path_invalid")
    receipt = load_json(resolved)
    candidate_source = receipt.get("head_before")
    if not isinstance(candidate_source, str) or FULL_OID.fullmatch(candidate_source) is None:
        raise RehearsalError("review_candidate_not_full_git_oid")
    if git("rev-parse", "--verify", f"{candidate_source}^{{commit}}") != candidate_source:
        raise RehearsalError("review_candidate_not_resolved_exact_commit")
    ancestry = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "merge-base",
            "--is-ancestor",
            candidate_source,
            "HEAD",
        ],
        check=False,
        capture_output=True,
        timeout=15,
    )
    if ancestry.returncode != 0:
        raise RehearsalError("review_candidate_not_ancestor_of_head")
    return candidate_source


def initialize_synthetic_workspace(root: Path) -> dict[str, str]:
    workspace = root / "workspace"
    workspace.mkdir(parents=True)
    target = workspace / SYNTHETIC_PATH
    target.write_text(BASELINE_SOURCE, encoding="utf-8", newline="\n")
    commands = [
        ["git", "init", "--initial-branch", "synthetic-baseline", str(workspace)],
        ["git", "-C", str(workspace), "config", "user.name", "EMR4 Synthetic Rehearsal"],
        ["git", "-C", str(workspace), "config", "user.email", "synthetic@invalid.local"],
        ["git", "-C", str(workspace), "add", "--", SYNTHETIC_PATH],
        ["git", "-C", str(workspace), "commit", "-m", "synthetic baseline"],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            timeout=30,
        )
        if completed.returncode != 0:
            raise RehearsalError("synthetic_git_initialization_failed")
    return {
        "baseline_commit": git_at(workspace, "rev-parse", "HEAD"),
        "baseline_sha256": file_sha256(target),
    }


def materialize_profile(root: Path) -> dict[str, str]:
    package_root, _copied = projection.materialize_accepted_node_modules(
        root, projection.load_contract()
    )
    proof = root / "installation" / "proof"
    proof.mkdir(parents=True)
    home = root / "home"
    profile_dir = home / "profiles" / "headless"
    profile_dir.mkdir(parents=True)
    preset_dir = home / ".agent-presets" / "emr4-bounded-worker"
    preset_dir.mkdir(parents=True)
    write_json(
        profile_dir / "package.json",
        {
            "name": "dsh-profile-headless",
            "private": True,
            "dependencies": {},
            "dsh": {
                "profile": {
                    "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
                }
            },
        },
    )
    (profile_dir / "pnpm-workspace.yaml").write_text(
        "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        encoding="utf-8",
        newline="\n",
    )
    accepted_preset = projection.native_predecessor.build_preset_source(
        projection.native_predecessor.load_contract()
    )
    (preset_dir / "agent.cordis.yml").write_bytes(accepted_preset)
    target = (root / "workspace" / SYNTHETIC_PATH).resolve().as_posix()
    (proof / "effective-tool-guard.mjs").write_bytes(guard.build_guard_source())
    (proof / "runner.mjs").write_bytes(runner_source(target))
    (proof / "sentinel.mjs").write_bytes(sentinel_source())
    package = load_json(package_root / "package.json")
    if package.get("name") != "@deepseek-ai/dsh" or package.get("version") != "0.1.0-rc.7":
        raise RehearsalError("materialized_package_identity_mismatch")
    return {
        "package_root": package_root.as_posix(),
        "package_json_sha256": file_sha256(package_root / "package.json"),
        "preset_sha256": sha256_bytes(accepted_preset),
        "guard_sha256": file_sha256(proof / "effective-tool-guard.mjs"),
        "runner_sha256": file_sha256(proof / "runner.mjs"),
        "sentinel_sha256": file_sha256(proof / "sentinel.mjs"),
        "initial_profile_template_sha256": sha256_bytes(
            profile_patch(root, 43123, changed=False)
        ),
        "changed_profile_template_sha256": sha256_bytes(
            profile_patch(root, 43123, changed=True)
        ),
    }


def prepare_attempt(review_receipt_path: Path) -> dict[str, Any]:
    deterministic_evidence()
    validate_authority_boundary()
    if any(
        path.exists()
        for path in (
            PREPARATION_PATH,
            WORK_ORDER_PATH,
            AUTHORITY_PATH,
            FORBIDDEN_PATH,
            COMMAND_MANIFEST_PATH,
            NO_DATABASE_ADMISSION_PATH,
            CONSUMED_PATH,
            TERMINAL_PATH,
            PRE_HMR_TERMINAL_PATH,
        )
    ):
        raise RehearsalError("attempt_artifact_already_exists")
    root = ATTEMPT_ROOT.resolve()
    parent = Path("C:/Users/sarashera/EMR4-worktrees").resolve()
    if root.parent != parent or root.exists():
        raise RehearsalError("attempt_root_not_fresh_exact_descendant")
    candidate_source = resolve_reviewed_candidate_source(review_receipt_path)
    receipt = validate_review_receipt(review_receipt_path, candidate_source)

    root.mkdir(parents=False)
    try:
        workspace = initialize_synthetic_workspace(root)
        profile = materialize_profile(root)
        sys_python = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
        from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
        from scripts.ariadne_validation_runner import (
            validate_execution_manifest_with_admission,
        )

        manifest = {
            "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
            "commands": [
                {
                    "id": "PF_SYNTHETIC_NATIVE_WORKER",
                    "argv": [
                        str(sys_python),
                        "-m",
                        "scripts.ariadne_provider_free_pytest",
                        "--repo-root",
                        str(REPO_ROOT),
                        "tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py",
                        "tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal_plan.py",
                        "tests/test_ariadne_deepseek_native_harness_broker.py",
                    ],
                }
            ],
        }
        admitted_manifest, admission = validate_execution_manifest_with_admission(
            manifest, repo_root=REPO_ROOT, require_provider_free=True
        )
        if admission is None or admission.get("status") != "passed":
            raise RehearsalError("no_database_admission_failed")
        authority = {
            "operation_id": EXECUTION_OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "candidate_source": candidate_source,
            "provider": "deepseek-official",
            "model": "deepseek-v4-flash",
            "reasoning_effort": "high",
            "maximum_output_tokens": 4096,
            "maximum_provider_calls": 1,
            "maximum_upstream_wall_clock_seconds": 300,
            "maximum_native_wall_clock_seconds": 420,
            "provider_spend_source": "existing_user_controlled_prepaid_balance",
            "broker_currency_cap_enforced": False,
            "provider_balance_top_up_authorized": False,
            "maximum_parallel_tool_calls": 1,
            "automatic_retries": 0,
            "fallbacks": 0,
            "auxiliary_model_calls": 0,
            "allowed_tool_names": EXPECTED_TOOLS,
            "owned_path": SYNTHETIC_PATH,
            "prompt_sha256": sha256_bytes(
                task_text((root / "workspace" / SYNTHETIC_PATH).resolve().as_posix()).encode()
            ),
        }
        forbidden = {
            "forbidden_surfaces": [
                "second_worker_or_retry",
                "shell_or_test_tool",
                "git_tool",
                "docker_database_postgresql_sql_transaction",
                "product_source_configuration_api_schema_route_adapter",
                "ordinary_practice_flag_allowlist_arrived_status_grammar_client_waiting_area",
                "product_patient_appointment_clinical_historical_protected_data",
                "production_deployment_release_pages_protected_refs",
                "raw_prompt_response_reasoning_credential_retention",
            ]
        }
        transaction = load_json(TRANSACTION_PATH)
        journal = transaction.get("journal")
        if not isinstance(journal, list) or not journal:
            raise RehearsalError("clockwork_journal_missing")
        tip = journal[-1]
        if tip.get("sequence") != len(journal) or not isinstance(
            tip.get("event_sha256"), str
        ):
            raise RehearsalError("clockwork_journal_invalid")
        manifest_digest = sha256_bytes(canonical_pretty_json(admitted_manifest))
        admission_digest = sha256_bytes(canonical_pretty_json(admission))
        work_order = {
            "schema_version": "ariadne.deepseek_work_order.v2",
            "work_order_id": WORK_ORDER_ID,
            "transaction_id": transaction["transaction_id"],
            "operation_id": EXECUTION_OPERATION_ID,
            "lease_id": LEASE_ID,
            "journal_id": tip["journal_id"],
            "source_commit": candidate_source,
            "authority_sha256": "sha256:" + sha256_bytes(canonical_json(authority)),
            "forbidden_surfaces_sha256": "sha256:" + sha256_bytes(canonical_json(forbidden)),
            "command_manifest_sha256": "sha256:" + manifest_digest,
            "provider_free_no_database_admission_sha256": "sha256:" + admission_digest,
            "branch": git("branch", "--show-current"),
            "worktree": (root / "workspace").resolve().as_posix(),
            "allowed_tool_names": EXPECTED_TOOLS,
            "posture": "provider_free_shadow",
            "next_sequence": tip["sequence"] + 1,
            "previous_event_sha256": tip["event_sha256"],
        }
        jsonschema.Draft202012Validator(load_json(WORK_ORDER_SCHEMA_PATH)).validate(
            work_order
        )
        write_json(AUTHORITY_PATH, authority)
        write_json(FORBIDDEN_PATH, forbidden)
        COMMAND_MANIFEST_PATH.write_bytes(canonical_pretty_json(admitted_manifest))
        NO_DATABASE_ADMISSION_PATH.write_bytes(canonical_pretty_json(admission))
        write_json(WORK_ORDER_PATH, work_order)
        relative_receipt = review_receipt_path.resolve().relative_to(REPO_ROOT.resolve())
        preparation = {
            "schema_version": "ariadne.synthetic_native_worker_preparation.v1",
            "operation_id": EXECUTION_OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "status": "passed",
            "candidate_source": candidate_source,
            "review_receipt": relative_receipt.as_posix(),
            "review_receipt_sha256": file_sha256(review_receipt_path),
            "attempt_root": root.as_posix(),
            "workspace": workspace,
            "profile": profile,
            "work_order_sha256": sha256_bytes(canonical_json(work_order)),
            "authority_sha256": sha256_bytes(canonical_json(authority)),
            "forbidden_sha256": sha256_bytes(canonical_json(forbidden)),
            "command_manifest_sha256": manifest_digest,
            "no_database_admission_sha256": admission_digest,
            "native_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "checkpoint_admitted": False,
        }
        write_json_exclusive(PREPARATION_PATH, preparation)
        return preparation
    except BaseException:
        if root.parent == parent and root.exists() and not remove_exact_attempt_root(root, parent):
            raise RehearsalError("attempt_preparation_cleanup_failed")
        raise


def load_checkpoint() -> dict[str, Any]:
    value = load_json(CHECKPOINT_PATH)
    required = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "status",
        "candidate_source",
        "review_receipt",
        "review_receipt_sha256",
        "preparation_sha256",
        "work_order_sha256",
        "runner_sha256",
        "prompt_sha256",
        "attempt_root",
        "native_process_limit",
        "provider_request_limit",
        "automatic_retry_limit",
        "fallback_limit",
        "auxiliary_model_call_limit",
        "expected_tool_names",
        "expected_changed_paths",
        "checkpoint_admitted",
    }
    if set(value) != required:
        raise RehearsalError("checkpoint_shape_mismatch")
    if (
        value["schema_version"] != "ariadne.synthetic_native_worker_checkpoint.v1"
        or value["operation_id"] != EXECUTION_OPERATION_ID
        or value["attempt_id"] != ATTEMPT_ID
        or value["status"] != "admitted"
        or value["checkpoint_admitted"] is not True
    ):
        raise RehearsalError("checkpoint_identity_mismatch")
    if (
        value["native_process_limit"] != 1
        or value["provider_request_limit"] != 1
        or value["automatic_retry_limit"] != 0
        or value["fallback_limit"] != 0
        or value["auxiliary_model_call_limit"] != 0
        or value["expected_tool_names"] != ["edit"]
        or value["expected_changed_paths"] != [SYNTHETIC_PATH]
        or value["attempt_root"] != ATTEMPT_ROOT.resolve().as_posix()
    ):
        raise RehearsalError("checkpoint_envelope_mismatch")
    preparation = load_json(PREPARATION_PATH)
    if value["candidate_source"] != preparation.get("candidate_source"):
        raise RehearsalError("checkpoint_candidate_mismatch")
    if value["preparation_sha256"] != file_sha256(PREPARATION_PATH):
        raise RehearsalError("checkpoint_preparation_digest_mismatch")
    if value["work_order_sha256"] != file_sha256(WORK_ORDER_PATH):
        raise RehearsalError("checkpoint_work_order_digest_mismatch")
    if value["runner_sha256"] != preparation.get("profile", {}).get("runner_sha256"):
        raise RehearsalError("checkpoint_runner_digest_mismatch")
    authority = load_json(AUTHORITY_PATH)
    if value["prompt_sha256"] != authority.get("prompt_sha256"):
        raise RehearsalError("checkpoint_prompt_digest_mismatch")
    receipt = REPO_ROOT / value["review_receipt"]
    if (
        value["review_receipt"] != preparation.get("review_receipt")
        or value["review_receipt_sha256"] != file_sha256(receipt)
    ):
        raise RehearsalError("checkpoint_review_digest_mismatch")
    return value


def _worker_environment(root: Path, port: int, token: str) -> dict[str, str]:
    allowed = ["PATH", "PATHEXT", "SYSTEMROOT", "TEMP", "TMP", "WINDIR", "COMSPEC"]
    environment = {name: os.environ[name] for name in allowed if name in os.environ}
    environment.update(
        {
            "DSH_HOME": str(root / "home"),
            "DSH_CWD": str(root / "workspace"),
            "DSH_PERMISSION_MODE": "workspace-write",
            "DSH_TOOLS_MODE": "native",
            "DSH_TELEMETRY_DISABLED": "1",
            "DSH_EMR4_BROKER_TOKEN": token,
            "NO_PROXY": f"127.0.0.1,localhost,127.0.0.1:{port}",
            "NPM_CONFIG_OFFLINE": "true",
            "NPM_CONFIG_AUDIT": "false",
            "NPM_CONFIG_FUND": "false",
            "NPM_CONFIG_IGNORE_SCRIPTS": "true",
        }
    )
    if any(
        name in environment
        for name in ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    ):
        raise RehearsalError("worker_provider_credential_present")
    return environment


def _broker_environment(token: str) -> dict[str, str]:
    provider_key = os.environ.get("DEEPSEEK_API_KEY")
    if not provider_key:
        raise RehearsalError("provider_key_missing")
    work_order = load_json(WORK_ORDER_PATH)
    return {
        **os.environ,
        "EMR4_BROKER_TEST_MODE": "1",
        "EMR4_BROKER_LISTEN_HOST": "127.0.0.1",
        "EMR4_BROKER_LISTEN_PORT": "0",
        "EMR4_BROKER_TEST_UPSTREAM_URL": "https://api.deepseek.com/chat/completions",
        "EMR4_BROKER_MAX_PROVIDER_CALLS": "1",
        "DSH_EMR4_BROKER_TOKEN": token,
        "DEEPSEEK_API_KEY": provider_key,
        "EMR4_BROKER_WORK_ORDER_PATH": str(WORK_ORDER_PATH),
        "EMR4_BROKER_WORK_ORDER_SHA256": canonical_object_sha256(work_order),
        "EMR4_BROKER_COMMAND_MANIFEST_PATH": str(COMMAND_MANIFEST_PATH),
        "EMR4_BROKER_NO_DATABASE_ADMISSION_PATH": str(NO_DATABASE_ADMISSION_PATH),
    }


def _collect_lines(
    stream: Any, lines: queue.Queue[str], retained: list[str]
) -> None:
    for line in stream:
        retained.append(line)
        lines.put(line)


def _wait_json_line(lines: queue.Queue[str], timeout: float) -> dict[str, Any]:
    try:
        raw = lines.get(timeout=timeout)
    except queue.Empty as error:
        raise RehearsalError("broker_ready_timeout") from error
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RehearsalError("broker_ready_not_json") from error
    if not isinstance(value, dict):
        raise RehearsalError("broker_ready_not_object")
    return value


def _hmr_events(path: Path) -> list[str]:
    if not path.is_file():
        return []
    events: list[str] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        value = json.loads(line)
        if (
            set(value) != {"schema_version", "sequence", "event"}
            or value["schema_version"] != "ariadne.synthetic_native_worker_hmr_event.v1"
            or value["sequence"] != index
            or value["event"] not in {"sentinel_activated", "stock_headless_hmr_ready"}
        ):
            raise RehearsalError("hmr_event_invalid")
        events.append(value["event"])
    if events != ["sentinel_activated", "stock_headless_hmr_ready"][: len(events)]:
        raise RehearsalError("hmr_event_order_invalid")
    return events


def _terminate(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _run_synthetic_cases(target: Path) -> dict[str, Any]:
    if file_sha256(target) != sha256_bytes(EXPECTED_SOURCE.encode("utf-8")):
        return {"executed": False, "public_passed": 0, "holdback_passed": 0}
    public = subprocess.run(
        [str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"), str(target)],
        check=False,
        capture_output=True,
        timeout=15,
    )
    holdback_code = (
        "import importlib.util,sys;"
        "p=sys.argv[1];s=importlib.util.spec_from_file_location('synthetic_candidate',p);"
        "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
        "cases=[([(0,10),(2,3)],[(0,10)]),"
        "([(0,5),(1,4),(5,8)],[(0,8)]),"
        "([(-4,9),(-2,1),(0,12)],[(-4,12)])];"
        "assert all(m.coalesce_windows(a)==b for a,b in cases)"
    )
    holdback = subprocess.run(
        [
            str(REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
            "-I",
            "-c",
            holdback_code,
            str(target),
        ],
        check=False,
        capture_output=True,
        timeout=15,
    )
    return {
        "executed": True,
        "public_passed": 4 if public.returncode == 0 else 0,
        "holdback_passed": 3 if holdback.returncode == 0 else 0,
    }


def render_native_report(value: dict[str, Any]) -> str:
    return f"""# Authored-synthetic native worker occupied report

- Result: `{value['result']}`
- Failure coordinate: `{value['failure_coordinate']}`
- Native processes / provider requests / retries: `{value['process']['native_process_count']}` / `{value['broker']['provider_call_started']}` / `0`
- Runner requests / tools / results: `{value['runner'].get('request_count', 0)}` / `{len(value['runner'].get('tool_names', []))}` / `{value['runner'].get('tool_result_count', 0)}`
- Changed paths: `{', '.join(value['candidate']['changed_paths'])}`
- Exact candidate bytes: `{str(value['candidate']['exact_expected_bytes']).lower()}`
- Public / holdback cases: `{value['candidate']['cases']['public_passed']}` / `{value['candidate']['cases']['holdback_passed']}`
- Harness / broker / disposable root absent: `{str(value['cleanup']['harness_absent']).lower()}` / `{str(value['cleanup']['broker_absent']).lower()}` / `{str(value['cleanup']['attempt_root_absent']).lower()}`

This is one authored-synthetic non-product native Harness attempt. It does not
admit EMR4 product work, multi-turn reliability or production use.
"""


def execute_native() -> dict[str, Any]:
    checkpoint = load_checkpoint()
    validate_authority_boundary()
    if (
        CONSUMED_PATH.exists()
        or TERMINAL_PATH.exists()
        or PRE_HMR_TERMINAL_PATH.exists()
    ):
        raise RehearsalError("occupied_attempt_already_consumed")
    root = ATTEMPT_ROOT.resolve()
    parent = Path("C:/Users/sarashera/EMR4-worktrees").resolve()
    if root.parent != parent or not root.is_dir() or root.is_symlink():
        raise RehearsalError("prepared_attempt_root_invalid")
    preparation = load_json(PREPARATION_PATH)
    if preparation.get("candidate_source") != checkpoint["candidate_source"]:
        raise RehearsalError("prepared_candidate_mismatch")
    work_order = load_json(WORK_ORDER_PATH)
    if work_order.get("source_commit") != checkpoint["candidate_source"]:
        raise RehearsalError("work_order_candidate_mismatch")
    consumed = {
        "schema_version": "ariadne.synthetic_native_worker_consumed.v1",
        "operation_id": EXECUTION_OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "state": "consumed",
        "candidate_source": checkpoint["candidate_source"],
        "automatic_retry_count": 0,
        "resume_permitted": False,
    }
    write_json_exclusive(CONSUMED_PATH, consumed)

    broker: subprocess.Popen[str] | None = None
    harness: subprocess.Popen[bytes] | None = None
    broker_lines: list[str] = []
    broker_queue: queue.Queue[str] = queue.Queue()
    broker_thread: threading.Thread | None = None
    failure: str | None = None
    broker_ready: dict[str, Any] = {}
    runner: dict[str, Any] = {}
    hmr_names: list[str] = []
    harness_exit: int | None = None
    native_started = False
    native_launch_attempted = False
    controller_coordinate: str | None = None
    pre_hmr_terminal: dict[str, Any] | None = None
    pre_hmr_terminal_sha256: str | None = None
    hmr_observation_valid = True
    start = time.monotonic()
    raw_readings: dict[str, Any] = {}
    runtime_profiles: dict[str, str] = {}
    workspace = root / "workspace"
    target = workspace / SYNTHETIC_PATH
    stdout_path = root / "harness-stdout.raw"
    stderr_path = root / "harness-stderr.raw"
    broker_stderr_path = root / "broker-stderr.raw"
    runner_terminal_path = root / "runner-terminal.json"
    event_path = root / "hmr-events.jsonl"
    try:
        token = secrets.token_urlsafe(48)
        with broker_stderr_path.open("wb") as broker_stderr:
            broker = subprocess.Popen(
                ["node", str(BROKER_PATH)],
                cwd=REPO_ROOT,
                env=_broker_environment(token),
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=broker_stderr,
            )
            if broker.stdout is None:
                raise RehearsalError("broker_stdout_missing")
            broker_thread = threading.Thread(
                target=_collect_lines,
                args=(broker.stdout, broker_queue, broker_lines),
                daemon=True,
            )
            broker_thread.start()
            broker_ready = _wait_json_line(broker_queue, 15)
            if (
                broker_ready.get("event") != "broker-ready"
                or broker_ready.get("allowed_tool_names") != EXPECTED_TOOLS
                or broker_ready.get("maximum_provider_calls") != 1
                or broker_ready.get("model_id") != "deepseek-v4-flash"
            ):
                raise RehearsalError("broker_ready_contract_mismatch")
            port = broker_ready.get("listen_port")
            if not isinstance(port, int) or not 1 <= port <= 65535:
                raise RehearsalError("broker_port_invalid")
            profile_path = root / "home" / "profiles" / "headless" / "cordis.patch.yml"
            initial = profile_patch(root, port, changed=False)
            changed = profile_patch(root, port, changed=True)
            validate_profile_patch(initial, changed=False)
            validate_profile_patch(changed, changed=True)
            profile_path.write_bytes(initial)
            runtime_profiles = {
                "initial_sha256": sha256_bytes(initial),
                "changed_sha256": sha256_bytes(changed),
            }
            package_root = root / "installation" / "node_modules" / "@deepseek-ai" / "dsh"
            command = [
                "node",
                "--expose-internals",
                str(package_root / "lib" / "bin.js"),
                "--profile",
                "headless",
                task_text(target.resolve().as_posix()),
            ]
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                native_launch_attempted = True
                try:
                    harness = subprocess.Popen(
                        command,
                        cwd=workspace,
                        env=_worker_environment(root, port, token),
                        stdout=stdout,
                        stderr=stderr,
                    )
                except OSError as error:
                    controller_coordinate = "native_process_creation_failed"
                    raise RehearsalError("native_process_creation_failed") from error
                native_started = True
                deadline = time.monotonic() + 420
                mutated = False
                while harness.poll() is None:
                    hmr_names = _hmr_events(event_path)
                    if "stock_headless_hmr_ready" in hmr_names and not mutated:
                        profile_path.write_bytes(changed)
                        mutated = True
                    if time.monotonic() >= deadline:
                        controller_coordinate = "native_worker_timeout"
                        raise RehearsalError("native_worker_timeout")
                    time.sleep(0.05)
                harness_exit = harness.wait(timeout=10)
            if broker_thread is not None:
                time.sleep(0.25)
            hmr_names = _hmr_events(event_path)
            if runner_terminal_path.is_file():
                runner = load_json(runner_terminal_path)
            if harness_exit != 0:
                controller_coordinate = "native_process_exited_nonzero"
                raise RehearsalError("native_harness_terminal_failure")
    except RehearsalError as error:
        failure = str(error)
        if native_started and controller_coordinate is None:
            controller_coordinate = "unexpected_controller_failure"
    except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError):
        failure = "unexpected_controller_failure"
        if native_started:
            controller_coordinate = "unexpected_controller_failure"
    finally:
        _terminate(harness)
        _terminate(broker)
        if harness is not None and harness_exit is None:
            harness_exit = harness.poll()
        if broker_thread is not None:
            broker_thread.join(timeout=10)
        if native_launch_attempted:
            try:
                hmr_names = _hmr_events(event_path)
            except (OSError, UnicodeError, json.JSONDecodeError, RehearsalError):
                hmr_observation_valid = False
                failure = (
                    "hmr_observation_invalid"
                    if failure is None
                    else f"{failure}+hmr_observation_invalid"
                )
            stream_readings: dict[str, dict[str, Any]] = {}
            for label, path in (("stdout", stdout_path), ("stderr", stderr_path)):
                try:
                    stream_readings[label] = startup_terminal.read_startup_stream(
                        path
                    )
                except startup_terminal.StartupTerminalError:
                    failure = (
                        "pre_hmr_startup_stream_read_failed"
                        if failure is None
                        else f"{failure}+pre_hmr_startup_stream_read_failed"
                    )
            if (
                failure is not None
                and hmr_observation_valid
                and not hmr_names
                and controller_coordinate is not None
                and set(stream_readings) == {"stdout", "stderr"}
            ):
                try:
                    pre_hmr_terminal = startup_terminal.build_pre_hmr_terminal(
                        operation_id=EXECUTION_OPERATION_ID,
                        attempt_id=ATTEMPT_ID,
                        candidate_source=checkpoint["candidate_source"],
                        native_process_started=native_started,
                        exit_code=harness_exit,
                        controller_coordinate=controller_coordinate,
                        hmr_events=hmr_names,
                        stdout=stream_readings["stdout"],
                        stderr=stream_readings["stderr"],
                    )
                except startup_terminal.StartupTerminalError:
                    failure += "+pre_hmr_terminal_derivation_failed"
        for label, path in (
            ("stdout", stdout_path),
            ("stderr", stderr_path),
            ("broker_stderr", broker_stderr_path),
        ):
            if label in {"stdout", "stderr"} and native_launch_attempted:
                reading = stream_readings.get(label)
            else:
                try:
                    reading = startup_terminal.read_startup_stream(path)
                except startup_terminal.StartupTerminalError:
                    reading = None
            raw_readings[f"{label}_bytes"] = (
                reading["byte_count"] if reading is not None else 0
            )
            raw_readings[f"{label}_sha256"] = (
                reading["sha256"] if reading is not None else sha256_bytes(b"")
            )

    changed_paths = sorted(
        line[3:].replace("\\", "/")
        for line in git_at(workspace, "status", "--porcelain=v1").splitlines()
        if len(line) >= 4
    )
    exact_expected = target.is_file() and file_sha256(target) == sha256_bytes(
        EXPECTED_SOURCE.encode("utf-8")
    )
    final_digest = file_sha256(target) if target.is_file() else None
    cases = _run_synthetic_cases(target)
    broker_events: list[dict[str, Any]] = []
    for line in broker_lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            broker_events.append(value)
    broker_counts = {
        "provider_call_started": sum(
            row.get("event") == "provider-call-started" for row in broker_events
        ),
        "provider_call_completed": sum(
            row.get("event") == "provider-call-completed" for row in broker_events
        ),
        "provider_call_failed": sum(
            row.get("event") == "provider-call-failed" for row in broker_events
        ),
        "request_rejected": sum(
            row.get("event") == "broker-request-rejected" for row in broker_events
        ),
    }
    runner_passed = (
        runner.get("status") == "completed"
        and runner.get("request_count") == 1
        and runner.get("tool_names") == ["edit"]
        and runner.get("tool_result_count") == 1
        and runner.get("turn_kind") == "completed"
        and runner.get("conclusion_marked") is True
        and runner.get("allowed_tool_names") == EXPECTED_TOOLS
    )
    success = (
        failure is None
        and native_started
        and harness_exit == 0
        and hmr_names == ["sentinel_activated", "stock_headless_hmr_ready"]
        and runner_passed
        and broker_counts
        == {
            "provider_call_started": 1,
            "provider_call_completed": 1,
            "provider_call_failed": 0,
            "request_rejected": 0,
        }
        and changed_paths == [SYNTHETIC_PATH]
        and exact_expected
        and cases == {"executed": True, "public_passed": 4, "holdback_passed": 3}
    )
    if not success and failure is None:
        failure = "occupied_acceptance_mismatch"

    if pre_hmr_terminal is not None:
        try:
            pre_hmr_terminal_sha256 = (
                startup_terminal.write_pre_hmr_terminal_exclusive(
                    path=PRE_HMR_TERMINAL_PATH.resolve(),
                    terminal=pre_hmr_terminal,
                    evidence_root=CONTINUITY_ROOT.resolve(),
                    disposable_root=root,
                )
            )
        except startup_terminal.StartupTerminalError:
            success = False
            failure = (
                "pre_hmr_terminalization_failed"
                if failure is None
                else f"{failure}+pre_hmr_terminalization_failed"
            )
    cleanup_passed = remove_exact_attempt_root(root, parent)
    root_absent = not root.exists()
    if not cleanup_passed or not root_absent:
        success = False
        failure = (
            "attempt_root_cleanup_failed"
            if failure is None
            else f"{failure}+attempt_root_cleanup_failed"
        )
    terminal = {
        "schema_version": TERMINAL_SCHEMA,
        "operation_id": EXECUTION_OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "candidate_source": checkpoint["candidate_source"],
        "result": "pass" if success else "failed_closed",
        "failure_coordinate": None if success else failure,
        "pre_hmr_startup_terminal_sha256": pre_hmr_terminal_sha256,
        "work_order_sha256": file_sha256(WORK_ORDER_PATH),
        "process": {
            "native_process_count": 1 if native_started else 0,
            "harness_exit_code": harness_exit,
            "wall_clock_ms": round((time.monotonic() - start) * 1000),
            **raw_readings,
        },
        "profile": runtime_profiles,
        "hmr_events": hmr_names,
        "runner": runner,
        "broker": broker_counts,
        "candidate": {
            "changed_paths": changed_paths,
            "exact_expected_bytes": exact_expected,
            "final_sha256": final_digest,
            "cases": cases,
        },
        "automatic_retry_count": 0,
        "fallback_count": 0,
        "auxiliary_model_call_count": 0,
        "cleanup": {
            "harness_absent": harness is None or harness.poll() is not None,
            "broker_absent": broker is None or broker.poll() is not None,
            "attempt_root_absent": root_absent,
            "raw_logs_retained": False,
            "raw_session_retained": False,
            "provider_key_present_in_worker_environment": False,
        },
    }
    jsonschema.Draft202012Validator(load_json(TERMINAL_SCHEMA_PATH)).validate(terminal)
    write_json_exclusive(TERMINAL_PATH, terminal)
    NATIVE_REPORT_PATH.write_text(
        render_native_report(terminal), encoding="utf-8", newline="\n"
    )
    if not success:
        raise RehearsalError("occupied_attempt_failed_closed:" + str(failure))
    return terminal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--build", action="store_true")
    action.add_argument("--prepare-attempt", action="store_true")
    action.add_argument("--native", action="store_true")
    parser.add_argument("--attempt-number", type=int, choices=(2, 3))
    parser.add_argument("--review-receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.prepare_attempt or args.native:
            if args.attempt_number == 2:
                configure_attempt_two()
            elif args.attempt_number == 3:
                configure_attempt_three()
            else:
                raise RehearsalError("explicit_occupied_attempt_number_required")
        elif args.attempt_number is not None:
            raise RehearsalError("attempt_number_only_valid_for_occupied_lifecycle")
        if args.check:
            value = deterministic_evidence()
        elif args.build:
            value = build_artifacts()
        elif args.prepare_attempt:
            if args.review_receipt is None:
                raise RehearsalError("review_receipt_required")
            value = prepare_attempt(args.review_receipt)
        else:
            if args.review_receipt is not None:
                raise RehearsalError("review_receipt_only_valid_for_preparation")
            value = execute_native()
        print(
            json.dumps(
                {
                    "result": value.get("result", value.get("status")),
                    "operation_id": EXECUTION_OPERATION_ID,
                }
            )
        )
        return 0
    except (RehearsalError, jsonschema.ValidationError, OSError) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
