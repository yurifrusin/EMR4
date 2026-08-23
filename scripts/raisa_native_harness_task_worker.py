"""Run one parameterized, bounded native-Harness implementation task.

The coordinator is the single task-coupled adapter allowed by the pragmatic
real-work policy. It keeps the accepted rc.7 stock headless entry point, waits
for its HMR surface, then loads a custom runner with exactly read/glob/edit.
It does not interpret model prose or accept a candidate.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import queue
import re
import secrets
import shutil
import subprocess
import threading
import time
from typing import Any

from scripts import (
    deepseek_native_harness_provider_free_effective_tool_composition_guard as guard,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as projection,
)
from scripts.raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal import (
    sentinel_source,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKTREE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
BROKER_PATH = REPO_ROOT / "scripts/ariadne_deepseek_native_harness_broker.mjs"
TRANSACTION_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-governance-clockwork"
    / "transaction.json"
)
PACKAGE_VERSION = "0.1.0-rc.7"
MODEL_ID = "deepseek-v4-flash"
TOOLS = ["edit", "glob", "read"]
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
CONFIG_SCHEMA = "ariadne.native_harness_task_worker_config.v1"
PROTECTED_PACKET_PREFIXES = (
    ".env",
    "orchestration/protected",
    "orchestration/secure",
    "secrets/",
)
WORKER_ENVIRONMENT_ALLOWLIST = {
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "WINDIR",
    "COMSPEC",
}
PROVIDER_ENVIRONMENT_NAMES = {
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_API_KEY",
}


class TaskWorkerError(RuntimeError):
    """The task-worker boundary failed closed."""


def canonical_bytes(value: Any, *, pretty: bool = False) -> bytes:
    separators = None if pretty else (",", ":")
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2 if pretty else None,
            separators=separators,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TaskWorkerError(f"json_object_required:{path.name}")
    return value


def write_json(path: Path, value: Any, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if exclusive else "wb"
    with path.open(mode) as stream:
        stream.write(canonical_bytes(value, pretty=True))


def run_checked(
    argv: list[str], *, cwd: Path = REPO_ROOT, timeout: int = 120
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if completed.returncode != 0:
        raise TaskWorkerError(f"command_failed:{argv[0]}:{completed.returncode}")
    return completed


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    return run_checked(["git", *args], cwd=cwd).stdout.strip()


def _relative_path(value: Any) -> str:
    if type(value) is not str or not value or "\\" in value:
        raise TaskWorkerError("repository_path_invalid")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != value:
        raise TaskWorkerError("repository_path_invalid")
    return value


def validate_config(value: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version",
        "operation_id",
        "attempt_id",
        "attempt_root",
        "evidence_root",
        "owned_paths",
        "read_only_packet_paths",
        "focused_test_paths",
        "task",
        "maximum_wall_clock_seconds",
    }
    if set(value) != expected or value.get("schema_version") != CONFIG_SCHEMA:
        raise TaskWorkerError("config_shape_invalid")
    for field in ("operation_id", "attempt_id"):
        item = value.get(field)
        if type(item) is not str or not re.fullmatch(r"[a-z0-9][a-z0-9-]{7,127}", item):
            raise TaskWorkerError(f"config_{field}_invalid")
    task = value.get("task")
    if (
        type(task) is not str
        or not 200 <= len(task) <= 20_000
        or task.count("{source_commit}") != 1
    ):
        raise TaskWorkerError("config_task_invalid")
    if value.get("maximum_wall_clock_seconds") != 900:
        raise TaskWorkerError("config_wall_clock_invalid")
    for field, minimum, maximum in (
        ("owned_paths", 2, 4),
        ("read_only_packet_paths", 3, 24),
        ("focused_test_paths", 1, 8),
    ):
        rows = value.get(field)
        if (
            type(rows) is not list
            or not minimum <= len(rows) <= maximum
            or len(rows) != len(set(rows))
        ):
            raise TaskWorkerError(f"config_{field}_invalid")
        value[field] = [_relative_path(row) for row in rows]
    if set(value["focused_test_paths"]) - set(value["owned_paths"] + value["read_only_packet_paths"]):
        raise TaskWorkerError("focused_test_outside_packet")
    if set(value["owned_paths"]) & set(value["read_only_packet_paths"]):
        raise TaskWorkerError("owned_read_only_overlap")
    if any(
        path.lower().startswith(PROTECTED_PACKET_PREFIXES)
        for path in value["owned_paths"] + value["read_only_packet_paths"]
    ):
        raise TaskWorkerError("protected_packet_path_forbidden")
    attempt_root = Path(value.get("attempt_root", "")).resolve()
    if attempt_root.parent != WORKTREE_PARENT.resolve() or attempt_root.is_symlink():
        raise TaskWorkerError("attempt_root_invalid")
    evidence_root = (REPO_ROOT / _relative_path(value.get("evidence_root"))).resolve()
    expected_evidence_root = (
        REPO_ROOT / "orchestration" / "continuity" / value["operation_id"]
    ).resolve()
    if evidence_root != expected_evidence_root:
        raise TaskWorkerError("evidence_root_invalid")
    return value


def full_source(source: str) -> str:
    if type(source) is not str or FULL_OID.fullmatch(source) is None:
        raise TaskWorkerError("source_not_full_git_object")
    resolved = git("rev-parse", "--verify", f"{source}^{{commit}}")
    if FULL_OID.fullmatch(resolved) is None:
        raise TaskWorkerError("source_not_full_git_object")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", resolved, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    ).returncode != 0:
        raise TaskWorkerError("source_not_ancestor_of_head")
    return resolved


def runner_source() -> bytes:
    return r'''import { createHash, randomUUID } from "node:crypto";
import { closeSync, openSync, writeFileSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { installModelSelection } from "@deepseek-ai/dsh-agent";
import { createUserMessage } from "@deepseek-ai/dsh-llm";
import { SessionId } from "@deepseek-ai/dsh-session";
import { assertEffectiveToolComposition } from "./effective-tool-guard.mjs";

export const name = "emr4-task-worker-runner";
export const inject = ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"];
const TOOLS = Object.freeze(["edit", "glob", "read"]);

function digest(value) { return "sha256:" + createHash("sha256").update(value).digest("hex"); }
function writeTerminal(path, value) {
  const descriptor = openSync(path, "wx");
  try { writeFileSync(descriptor, JSON.stringify(value) + "\n", "utf8"); }
  finally { closeSync(descriptor); }
}
function normalized(path) { return resolve(process.cwd(), path).toLowerCase(); }
function summarize(events, firstSeq) {
  const toolNames = [];
  let requestCount = 0;
  let toolResultCount = 0;
  let turnKind = null;
  for (const event of events) {
    if (event.seq < firstSeq) continue;
    if (event.type === "request/header") requestCount += 1;
    if (event.type === "tool/call") toolNames.push(typeof event.data?.name === "string" ? event.data.name : "unknown");
    if (event.type === "tool/result") toolResultCount += 1;
    if (event.type === "turn/end") turnKind = event.data?.reason?.kind ?? "unknown";
  }
  return { request_count: requestCount, tool_names: toolNames, tool_result_count: toolResultCount, turn_kind: turnKind };
}

async function run(ctx, config) {
  await ctx.get("loader")?.await();
  const agents = ctx.get("agents");
  const sessions = ctx.get("sessions");
  const presets = ctx.get("agentPresets");
  if (!agents || !sessions || !presets) throw new Error("REQUIRED_SERVICE_MISSING");
  if (!Array.isArray(presets.roots) || presets.roots.length !== 2 || resolve(presets.roots[0].path) !== resolve(config.shippedRoot) || presets.roots[0].trust !== "system" || resolve(presets.roots[1].path) !== resolve(config.userRoot) || presets.roots[1].trust !== "user") throw new Error("PRESET_ROOT_ROSTER_MISMATCH");
  if (!Array.isArray(config.ownedPaths) || config.ownedPaths.length < 2 || config.ownedPaths.length > 4) throw new Error("OWNED_PATHS_INVALID");
  const owned = new Set(config.ownedPaths.map(normalized));
  const sessionText = `session-${randomUUID()}`;
  const selection = { provider: "deepseek-official", model: "deepseek-v4-flash", reasoningEffort: "high" };
  const { agent } = await agents.create({
    sessionId: SessionId(sessionText),
    meta: { cwd: process.cwd() },
    agentOptions: { provider: selection.provider, model: selection.model, maxTokens: 4096 },
    setup: async (agentCtx) => {
      await assertEffectiveToolComposition(agentCtx, "emr4-bounded-worker", TOOLS);
      installModelSelection(agentCtx, { current: selection, assembled: undefined });
      agentCtx.on("tools/pre-execute", async (exec, next) => {
        if (!TOOLS.includes(exec.name) || exec.parent !== undefined) return { kind: "deny", reason: "TOOL_BOUNDARY_MISMATCH" };
        if (exec.name === "edit") {
          const args = exec.arguments;
          if (!args || typeof args !== "object" || typeof args.file_path !== "string" || typeof args.old_string !== "string" || typeof args.new_string !== "string" || args.old_string.length === 0 || args.old_string === args.new_string || args.replace_all === true || !owned.has(normalized(args.file_path))) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" };
        }
        return next();
      });
    },
  });
  await agent.whenIdle();
  const firstSeq = agent.session.seq;
  agent.followup(createUserMessage({ content: [{ type: "text", text: config.task }], source: { kind: "user" } }));
  await agent.whenIdle();
  await sessions.flush(agent.session);
  const summary = summarize(agent.session.events, firstSeq);
  const completed = summary.request_count >= 1 && summary.turn_kind === "completed";
  writeTerminal(config.terminalPath, {
    schema_version: "ariadne.native_harness_task_runner_terminal.v1",
    status: completed ? "completed" : "failed",
    session_id_sha256: digest(sessionText),
    provider: selection.provider,
    model: selection.model,
    reasoning_effort: selection.reasoningEffort,
    allowed_tool_names: TOOLS,
    ...summary,
  });
  ctx.get("appExit")(completed ? 0 : 1);
}

export function apply(ctx, config) {
  run(ctx, config).catch(() => {
    writeTerminal(config.terminalPath, {
      schema_version: "ariadne.native_harness_task_runner_terminal.v1",
      status: "failed",
      failure_code: "CUSTOM_RUNNER_FAILURE",
      request_count: 0,
      tool_names: [],
      tool_result_count: 0,
      turn_kind: null,
      allowed_tool_names: TOOLS,
    });
    ctx.get("appExit")(1);
  });
}
'''.encode("utf-8")


def profile_patch(root: Path, port: int, *, runner: bool) -> bytes:
    home = root / "home"
    profile_dir = home / "profiles" / "headless"
    quoted = lambda path: json.dumps(str(path.resolve()))
    disabled = [
        "headless-runner",
        "code-runtime",
        "session-telemetry-otel",
        "session-title-llm",
        "compaction-basic",
        "command-compact",
        "llm-pi-ai",
        "llm-retry",
        "tool-bash",
        "tool-pwsh",
        "tool-jobs",
        "tool-skill",
        "tool-goal",
        "tool-ralph",
        "tool-subagent",
        "tool-subagent-fork",
        "tool-subagent-control",
        "tool-subagent-list-agents",
        "tool-subagent-report",
        "tool-workflow",
        "tool-todo",
        "tool-web",
        "web-search-deepseek",
        "tool-str-replace-editor",
    ]
    rows = "".join(f"- id: {item}\n  disabled: true\n" for item in disabled)
    rows += f'''- id: session-persistence-jsonl
  config:
    root: {quoted(root / "raw-sessions")}
    compression: none
- id: sandbox-policy
  config:
    mode: workspace-write
    workspaceRoot: {quoted(root / "workspace")}
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
    cwd: {quoted(root / "workspace")}
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
          - path: {quoted(home / ".agent-presets")}
            trust: system
        includeUserRoot: true
    - id: emr4-task-worker-hmr-sentinel
      name: ../../../installation/proof/sentinel.mjs
      config:
        eventPath: {quoted(root / "hmr-events.jsonl")}
        watchedPaths:
          - {quoted(profile_dir / "cordis.patch.yml")}
          - {quoted(home / "cordis.patch.yml")}
'''
    if runner:
        owned_rows = "".join(
            f"          - {quoted(root / 'workspace' / path)}\n"
            for path in load_json(root / "task-config.json")["owned_paths"]
        )
        rows += f'''    - id: emr4-task-worker-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, headlessStartup, agents, sessions, agentPresets]
      config:
        task: !!js ctx.headlessStartup.task
        terminalPath: {quoted(root / "runner-terminal.json")}
        shippedRoot: {quoted(root / "installation" / "node_modules" / "@deepseek-ai" / "dsh" / "config" / "agent-presets")}
        userRoot: {quoted(home / ".agent-presets")}
        ownedPaths:
{owned_rows}'''
    return rows.encode("utf-8")


def validate_runner_and_profile(root: Path) -> dict[str, Any]:
    source = runner_source().decode("utf-8")
    initial = profile_patch(root, 43123, runner=False).decode("utf-8")
    changed = profile_patch(root, 43123, runner=True).decode("utf-8")
    checks = {
        "exact_tools": 'Object.freeze(["edit", "glob", "read"])' in source,
        "no_conclude_turn": "concludeTurn" not in source,
        "owned_edit_gate": "owned.has(normalized(args.file_path))" in source,
        "multi_request_allowed": "summary.request_count >= 1" in source,
        "stock_runner_disabled": "- id: headless-runner\n  disabled: true" in initial,
        "custom_runner_absent_initially": "- id: emr4-task-worker-runner" not in initial,
        "custom_runner_hmr_inserted": changed.count("- id: emr4-task-worker-runner") == 1,
        "one_tool_at_a_time": "maxParallelToolCalls: 1" in changed,
        "zero_retry": "maxRetries: 0" in changed,
        "approval_never": "policy: never" in changed,
        "no_model_shell": all(token not in source for token in ("child_process", "spawn(", "exec(")),
    }
    if not all(checks.values()):
        raise TaskWorkerError(
            "effective_tool_preflight_failed:"
            + ",".join(sorted(key for key, passed in checks.items() if not passed))
        )
    return checks


def _materialize_profile(root: Path) -> dict[str, Any]:
    package_root, copied = projection.materialize_accepted_node_modules(
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
    preset = projection.native_predecessor.build_preset_source(
        projection.native_predecessor.load_contract()
    )
    (preset_dir / "agent.cordis.yml").write_bytes(preset)
    (proof / "effective-tool-guard.mjs").write_bytes(guard.build_guard_source())
    (proof / "runner.mjs").write_bytes(runner_source())
    (proof / "sentinel.mjs").write_bytes(sentinel_source())
    package = load_json(package_root / "package.json")
    if package.get("name") != "@deepseek-ai/dsh" or package.get("version") != PACKAGE_VERSION:
        raise TaskWorkerError("package_identity_mismatch")
    for path in proof.glob("*.mjs"):
        run_checked(["node", "--check", str(path)])
    return {
        "package_root": package_root.as_posix(),
        "package_json_sha256": sha256_file(package_root / "package.json"),
        "preset_sha256": sha256_bytes(preset),
        "guard_sha256": sha256_file(proof / "effective-tool-guard.mjs"),
        "runner_sha256": sha256_file(proof / "runner.mjs"),
        "sentinel_sha256": sha256_file(proof / "sentinel.mjs"),
        "materialized_package_count": len(copied),
    }


def _prepare_command_boundary(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
    from scripts.ariadne_validation_runner import validate_execution_manifest_with_admission

    python = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    manifest = {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {
                "id": "PF_NATIVE_TASK_FOCUSED_TESTS",
                "argv": [
                    str(python),
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    str(REPO_ROOT),
                    *config["focused_test_paths"],
                ],
            }
        ],
    }
    admitted, admission = validate_execution_manifest_with_admission(
        manifest, repo_root=REPO_ROOT, require_provider_free=True
    )
    if admission is None or admission.get("status") != "passed":
        raise TaskWorkerError("provider_free_command_admission_failed")
    return admitted, admission


def prepare(config_path: Path, source: str) -> dict[str, Any]:
    config = validate_config(load_json(config_path))
    source = full_source(source)
    root = Path(config["attempt_root"]).resolve()
    workspace = root / "workspace"
    evidence_root = (REPO_ROOT / config["evidence_root"]).resolve()
    prepared_path = evidence_root / "native-harness-prepared.json"
    if root.exists() or prepared_path.exists():
        raise TaskWorkerError("attempt_not_fresh")
    root.mkdir(parents=True)
    try:
        write_json(root / "task-config.json", config)
        run_checked(["git", "worktree", "add", "--detach", "--no-checkout", str(workspace), source])
        run_checked(["git", "sparse-checkout", "init", "--no-cone"], cwd=workspace)
        sparse_paths = list(dict.fromkeys(config["read_only_packet_paths"] + config["owned_paths"]))
        run_checked(["git", "sparse-checkout", "set", "--no-cone", "--", *sparse_paths], cwd=workspace)
        run_checked(["git", "checkout", "--detach", source], cwd=workspace)
        if git("rev-parse", "HEAD", cwd=workspace) != source:
            raise TaskWorkerError("worktree_source_mismatch")
        for relative in sparse_paths:
            if not (workspace / relative).is_file():
                raise TaskWorkerError(f"sparse_packet_missing:{relative}")
        for relative in config["read_only_packet_paths"]:
            (workspace / relative).chmod(0o444)
        preflight = validate_runner_and_profile(root)
        profile = _materialize_profile(root)
        manifest, admission = _prepare_command_boundary(config)
        transaction = load_json(TRANSACTION_PATH)
        journal = transaction.get("journal")
        if not isinstance(journal, list) or not journal:
            raise TaskWorkerError("clockwork_journal_missing")
        tip = journal[-1]
        rendered_task = config["task"].replace("{source_commit}", source)
        authority = {
            "operation_id": config["operation_id"],
            "attempt_id": config["attempt_id"],
            "source_commit": source,
            "provider": "deepseek-official",
            "model": MODEL_ID,
            "reasoning_effort": "high",
            "maximum_wall_clock_seconds": 900,
            "maximum_parallel_tool_calls": 1,
            "automatic_retries": 0,
            "fallbacks": 0,
            "auxiliary_model_calls": 0,
            "allowed_tool_names": TOOLS,
            "owned_paths": config["owned_paths"],
            "prompt_sha256": sha256_bytes(rendered_task.encode("utf-8")),
        }
        forbidden = {
            "forbidden_surfaces": [
                "non_owned_path_edit",
                "shell_test_git_web_subagent_or_workflow_tool",
                "worker_provider_credential_or_direct_egress",
                "automatic_retry_fallback_or_auxiliary_model",
                "environment_configuration_secret_database_product_data_or_protected_evidence",
                "route_api_client_runtime_deployment_pages_or_protected_ref",
                "model_or_broker_canonical_clockwork_write",
            ]
        }
        write_json(root / "authority.json", authority)
        write_json(root / "forbidden-surfaces.json", forbidden)
        write_json(root / "command-manifest.json", manifest)
        write_json(root / "provider-free-no-database-admission.json", admission)
        work_order = {
            "schema_version": "ariadne.deepseek_work_order.v2",
            "work_order_id": f"wo-{config['attempt_id']}",
            "transaction_id": transaction["transaction_id"],
            "operation_id": config["operation_id"],
            "lease_id": f"lease-{config['attempt_id']}",
            "journal_id": tip["journal_id"],
            "source_commit": source,
            "authority_sha256": "sha256:" + sha256_bytes(canonical_bytes(authority).rstrip(b"\n")),
            "forbidden_surfaces_sha256": "sha256:" + sha256_bytes(canonical_bytes(forbidden).rstrip(b"\n")),
            "command_manifest_sha256": "sha256:" + sha256_bytes(canonical_bytes(manifest, pretty=True)),
            "provider_free_no_database_admission_sha256": "sha256:" + sha256_bytes(canonical_bytes(admission, pretty=True)),
            "branch": "detached-native-harness-worker",
            "worktree": workspace.as_posix(),
            "allowed_tool_names": TOOLS,
            "posture": "provider_free_shadow",
            "next_sequence": tip["sequence"] + 1,
            "previous_event_sha256": tip["event_sha256"],
        }
        write_json(root / "work-order-v2.json", work_order)
        prepared = {
            "schema_version": "ariadne.native_harness_task_prepared.v1",
            "operation_id": config["operation_id"],
            "attempt_id": config["attempt_id"],
            "reading": "prepared",
            "status": "passed",
            "source_commit": source,
            "owned_paths": config["owned_paths"],
            "read_only_packet_paths": config["read_only_packet_paths"],
            "effective_tools": TOOLS,
            "provider_calls": 0,
            "worker_sessions": 0,
            "profile": profile,
            "effective_tool_preflight": preflight,
            "work_order_sha256": sha256_bytes(canonical_bytes(work_order).rstrip(b"\n")),
            "prompt_sha256": authority["prompt_sha256"],
        }
        write_json(root / "preparation.json", prepared)
        write_json(prepared_path, prepared, exclusive=True)
        return prepared
    except Exception:
        if workspace.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(workspace)],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
            )
        if root.exists():
            shutil.rmtree(root)
        raise


def _worker_environment(root: Path, port: int, token: str) -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in WORKER_ENVIRONMENT_ALLOWLIST
        if name in os.environ
    }
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
    if PROVIDER_ENVIRONMENT_NAMES.intersection(environment):
        raise TaskWorkerError("worker_provider_credential_present")
    return environment


def _broker_environment(root: Path, token: str) -> dict[str, str]:
    provider_key = os.environ.get("DEEPSEEK_API_KEY")
    if not provider_key:
        raise TaskWorkerError("provider_key_missing")
    work_order = load_json(root / "work-order-v2.json")
    environment = dict(os.environ)
    environment.update(
        {
            "EMR4_BROKER_TEST_MODE": "1",
            "EMR4_BROKER_LISTEN_HOST": "127.0.0.1",
            "EMR4_BROKER_LISTEN_PORT": "0",
            "EMR4_BROKER_TEST_UPSTREAM_URL": "https://api.deepseek.com/chat/completions",
            "DSH_EMR4_BROKER_TOKEN": token,
            "DEEPSEEK_API_KEY": provider_key,
            "EMR4_BROKER_WORK_ORDER_PATH": str(root / "work-order-v2.json"),
            "EMR4_BROKER_WORK_ORDER_SHA256": "sha256:" + sha256_bytes(canonical_bytes(work_order).rstrip(b"\n")),
            "EMR4_BROKER_COMMAND_MANIFEST_PATH": str(root / "command-manifest.json"),
            "EMR4_BROKER_NO_DATABASE_ADMISSION_PATH": str(root / "provider-free-no-database-admission.json"),
        }
    )
    environment.pop("EMR4_BROKER_MAX_PROVIDER_CALLS", None)
    return environment


def _collect_lines(stream: Any, channel: queue.Queue[str], retained: list[str]) -> None:
    for line in stream:
        retained.append(line)
        channel.put(line)


def _terminate(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _hmr_events(path: Path) -> list[str]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        if isinstance(value, dict) and isinstance(value.get("event"), str):
            events.append(value["event"])
    return events


def _session_reading(root: Path) -> dict[str, Any]:
    files = sorted((root / "raw-sessions").rglob("session.jsonl"))
    if len(files) != 1:
        return {"file_count": len(files), "trace_complete": False}
    path = files[0]
    requests = 0
    tools: list[str] = []
    results = 0
    terminal = None
    usage: list[dict[str, int]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw:
            continue
        row = json.loads(raw)
        data = row.get("data") if isinstance(row.get("data"), dict) else {}
        if row.get("type") == "request/header":
            requests += 1
        elif row.get("type") == "tool/call":
            tools.append(data.get("name") if isinstance(data.get("name"), str) else "unknown")
        elif row.get("type") == "tool/result":
            results += 1
        elif row.get("type") == "turn/end":
            reason = data.get("reason") if isinstance(data.get("reason"), dict) else {}
            terminal = reason.get("kind")
        row_usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
        if row_usage:
            usage.append(
                {
                    key: item
                    for key, item in row_usage.items()
                    if isinstance(item, int) and item >= 0
                }
            )
    return {
        "file_count": 1,
        "session_sha256": sha256_file(path),
        "trace_complete": terminal is not None,
        "request_count": requests,
        "tool_sequence": tools,
        "tool_result_count": results,
        "terminal_kind": terminal,
        "usage": usage,
    }


def execute(config_path: Path) -> dict[str, Any]:
    config = validate_config(load_json(config_path))
    root = Path(config["attempt_root"]).resolve()
    workspace = root / "workspace"
    evidence_root = (REPO_ROOT / config["evidence_root"]).resolve()
    terminal_path = evidence_root / "native-harness-terminal.json"
    preparation = load_json(root / "preparation.json")
    source = preparation.get("source_commit")
    if source != git("rev-parse", "HEAD", cwd=workspace):
        raise TaskWorkerError("prepared_source_drift")
    if git("status", "--porcelain=v1", "--untracked-files=all", cwd=workspace):
        raise TaskWorkerError("prepared_worktree_not_clean")
    write_json(
        root / "consumed.json",
        {
            "schema_version": "ariadne.native_harness_task_consumed.v1",
            "attempt_id": config["attempt_id"],
            "state": "consumed",
            "automatic_retry_count": 0,
        },
        exclusive=True,
    )
    token = secrets.token_urlsafe(48)
    broker: subprocess.Popen[str] | None = None
    harness: subprocess.Popen[bytes] | None = None
    broker_lines: list[str] = []
    broker_queue: queue.Queue[str] = queue.Queue()
    broker_thread: threading.Thread | None = None
    broker_ready: dict[str, Any] = {}
    runner_terminal: dict[str, Any] = {}
    failure: str | None = None
    exit_code: int | None = None
    timed_out = False
    started_at = datetime.now(timezone.utc)
    started = time.monotonic()
    try:
        with (root / "broker-stderr.raw").open("wb") as broker_stderr:
            broker = subprocess.Popen(
                ["node", str(BROKER_PATH)],
                cwd=REPO_ROOT,
                env=_broker_environment(root, token),
                stdout=subprocess.PIPE,
                stderr=broker_stderr,
                text=True,
                encoding="utf-8",
            )
            if broker.stdout is None:
                raise TaskWorkerError("broker_stdout_missing")
            broker_thread = threading.Thread(
                target=_collect_lines,
                args=(broker.stdout, broker_queue, broker_lines),
                daemon=True,
            )
            broker_thread.start()
            try:
                broker_ready = json.loads(broker_queue.get(timeout=15))
            except (queue.Empty, json.JSONDecodeError) as error:
                raise TaskWorkerError("broker_ready_invalid") from error
            if (
                broker_ready.get("event") != "broker-ready"
                or broker_ready.get("allowed_tool_names") != TOOLS
                or broker_ready.get("maximum_provider_calls") is not None
                or broker_ready.get("model_id") != MODEL_ID
            ):
                raise TaskWorkerError("broker_ready_contract_mismatch")
            port = broker_ready.get("listen_port")
            if not isinstance(port, int) or not 1 <= port <= 65535:
                raise TaskWorkerError("broker_port_invalid")
            profile_path = root / "home/profiles/headless/cordis.patch.yml"
            initial = profile_patch(root, port, runner=False)
            changed = profile_patch(root, port, runner=True)
            profile_path.write_bytes(initial)
            rendered_task = config["task"].replace("{source_commit}", str(source))
            command = [
                "node",
                "--expose-internals",
                str(root / "installation/node_modules/@deepseek-ai/dsh/lib/bin.js"),
                "--profile",
                "headless",
                rendered_task,
            ]
            with (root / "harness-stdout.raw").open("wb") as stdout, (
                root / "harness-stderr.raw"
            ).open("wb") as stderr:
                harness = subprocess.Popen(
                    command,
                    cwd=workspace,
                    env=_worker_environment(root, port, token),
                    stdout=stdout,
                    stderr=stderr,
                )
                deadline = time.monotonic() + config["maximum_wall_clock_seconds"]
                mutated = False
                while harness.poll() is None:
                    events = _hmr_events(root / "hmr-events.jsonl")
                    if "stock_headless_hmr_ready" in events and not mutated:
                        profile_path.write_bytes(changed)
                        mutated = True
                    if time.monotonic() >= deadline:
                        timed_out = True
                        raise TaskWorkerError("native_worker_timeout")
                    time.sleep(0.05)
                exit_code = harness.wait(timeout=10)
            if (root / "runner-terminal.json").exists():
                runner_terminal = load_json(root / "runner-terminal.json")
            if exit_code != 0:
                raise TaskWorkerError("native_harness_terminal_failure")
    except (TaskWorkerError, OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError) as error:
        failure = str(error) if isinstance(error, TaskWorkerError) else "unexpected_controller_failure"
    finally:
        _terminate(harness)
        _terminate(broker)
        if broker_thread is not None:
            broker_thread.join(timeout=10)
    broker_events = []
    for line in broker_lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            broker_events.append(value)
    started_calls = sum(row.get("event") == "provider-call-started" for row in broker_events)
    completed_calls = sum(row.get("event") == "provider-call-completed" for row in broker_events)
    failed_calls = sum(row.get("event") == "provider-call-failed" for row in broker_events)
    if started_calls == 0:
        provider = "not_reached"
    elif completed_calls:
        provider = "reached_completed"
    else:
        provider = "reached_failed"
    status_rows = [
        row
        for row in git("status", "--porcelain=v1", "--untracked-files=all", cwd=workspace).splitlines()
        if row
    ]
    changed_paths = [row[3:].replace("\\", "/") for row in status_rows]
    scope_integrity = all(path in config["owned_paths"] for path in changed_paths)
    candidate = (
        "none"
        if not changed_paths
        else "complete"
        if set(changed_paths) == set(config["owned_paths"]) and runner_terminal.get("status") == "completed"
        else "partial"
    )
    runner_completed = runner_terminal.get("status") == "completed"
    hmr_complete = _hmr_events(root / "hmr-events.jsonl") == [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]
    if failure is None and scope_integrity and runner_completed and hmr_complete:
        failure_stage = "none"
    elif provider == "not_reached":
        failure_stage = "pre_provider_envelope"
    elif provider == "reached_failed":
        failure_stage = "provider_transport"
    else:
        failure_stage = "agent_execution"
    terminal = {
        "schema_version": "ariadne.native_harness_task_terminal.v1",
        "operation_id": config["operation_id"],
        "attempt_id": config["attempt_id"],
        "reading": "terminal",
        "source_commit": source,
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "ended_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "duration_ms": round((time.monotonic() - started) * 1000),
        "provider": provider,
        "candidate": candidate,
        "failure_stage": failure_stage,
        "failure_code": failure,
        "process": {
            "exit_code": exit_code,
            "timed_out": timed_out,
            "automatic_retries": 0,
            "fallbacks": 0,
            "auxiliary_model_calls": 0,
        },
        "broker": {
            "ready": broker_ready.get("event") == "broker-ready",
            "provider_call_started": started_calls,
            "provider_call_completed": completed_calls,
            "provider_call_failed": failed_calls,
        },
        "runner": runner_terminal,
        "hmr_complete": hmr_complete,
        "session": _session_reading(root),
        "changed_paths": changed_paths,
        "scope_integrity": scope_integrity,
        "cleanup": {
            "broker_absent": broker is None or broker.poll() is not None,
            "worker_absent": harness is None or harness.poll() is not None,
            "raw_material_retained_pending_sol_review": True,
        },
    }
    write_json(root / "terminal.json", terminal, exclusive=True)
    write_json(terminal_path, terminal, exclusive=True)
    return terminal


def cleanup(config_path: Path) -> dict[str, Any]:
    config = validate_config(load_json(config_path))
    root = Path(config["attempt_root"]).resolve()
    if root.parent != WORKTREE_PARENT.resolve() or not root.exists() or root.is_symlink():
        raise TaskWorkerError("cleanup_root_invalid")
    workspace = root / "workspace"
    if workspace.exists():
        run_checked(["git", "worktree", "remove", "--force", str(workspace)])
    shutil.rmtree(root)
    return {
        "schema_version": "ariadne.native_harness_task_cleanup.v1",
        "operation_id": config["operation_id"],
        "attempt_id": config["attempt_id"],
        "attempt_root_absent": not root.exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", metavar="SOURCE")
    group.add_argument("--execute", action="store_true")
    group.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare:
            result = prepare(args.config, args.prepare)
        elif args.execute:
            result = execute(args.config)
        else:
            result = cleanup(args.config)
    except (TaskWorkerError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(json.dumps({"status": "failed", "reason": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
