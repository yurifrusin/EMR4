"""Control one native-Harness DeepSeek edit of a default-off Raisa runbook."""

from __future__ import annotations

import argparse
from datetime import datetime
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
from zoneinfo import ZoneInfo

import jsonschema

from orchestration_harness import check_in_rollout_runbook as runbook
from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as startup_terminal
from orchestration_harness.transactional_closeout import (
    sha256 as canonical_object_sha256,
)
from scripts import (
    deepseek_native_harness_provider_free_complete_package_unloaded_runner_evaluation_rehearsal
    as accepted_complete,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_worker,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = "raisa-native-harness-bounded-occupied-useful-worker-rehearsal"
ATTEMPT_ID = "deepseek-native-check-in-runbook-worker-001"
WORK_ORDER_ID = "wo-deepseek-native-check-in-runbook-worker-001"
LEASE_ID = "lease-deepseek-native-check-in-runbook-worker-001"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
ATTEMPT_EVIDENCE_ROOT = OPERATION_ROOT / "attempt-001"
ATTEMPT_ROOT = Path(f"C:/Users/sarashera/EMR4-worktrees/{ATTEMPT_ID}")
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
CANDIDATE_SCHEMA_PATH = OPERATION_ROOT / "worker-candidate.schema.json"
TERMINAL_SCHEMA_PATH = OPERATION_ROOT / "occupied-terminal.schema.json"
PREPARATION_PATH = ATTEMPT_EVIDENCE_ROOT / "occupied-attempt-preparation.json"
WORK_ORDER_PATH = ATTEMPT_EVIDENCE_ROOT / "work-order.json"
AUTHORITY_PATH = ATTEMPT_EVIDENCE_ROOT / "worker-authority.json"
FORBIDDEN_PATH = ATTEMPT_EVIDENCE_ROOT / "forbidden-surfaces.json"
COMMAND_MANIFEST_PATH = ATTEMPT_EVIDENCE_ROOT / "command-manifest.json"
NO_DATABASE_ADMISSION_PATH = (
    ATTEMPT_EVIDENCE_ROOT / "provider-free-no-database-admission.json"
)
CHECKPOINT_PATH = ATTEMPT_EVIDENCE_ROOT / "occupied-preexecution-checkpoint.json"
CONSUMED_PATH = ATTEMPT_EVIDENCE_ROOT / "occupied-attempt-consumed.json"
TERMINAL_PATH = ATTEMPT_EVIDENCE_ROOT / "occupied-terminal.json"
CANDIDATE_OUTPUT_PATH = ATTEMPT_EVIDENCE_ROOT / "admitted-worker-candidate.json"
REPORT_PATH = ATTEMPT_EVIDENCE_ROOT / "occupied-report.md"
PRE_HMR_TERMINAL_PATH = ATTEMPT_EVIDENCE_ROOT / "pre-hmr-startup-terminal.json"
BROKER_PATH = REPO_ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs"
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
TARGET_RELATIVE_PATH = runbook.TARGET_RELATIVE_PATH
EXPECTED_TOOLS = ["edit", "glob", "read"]
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
TERMINAL_SCHEMA_VERSION = "ariadne.native_harness_useful_worker_terminal.v1"
RUNNER_TERMINAL_SCHEMA_VERSION = (
    "ariadne.native_harness_useful_worker_runner_terminal.v1"
)


class UsefulWorkerError(RuntimeError):
    """A bounded useful-worker invariant failed closed."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise UsefulWorkerError(f"json_root_invalid:{path.name}")
    return value


def write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(canonical_bytes(value))


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
        raise UsefulWorkerError("attempt_cleanup_scope_invalid")
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


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if completed.returncode != 0:
        raise UsefulWorkerError("git_command_failed")
    return completed.stdout.strip()


def git_at(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if completed.returncode != 0:
        raise UsefulWorkerError("disposable_git_command_failed")
    return completed.stdout.strip()


def _runbook_member_text() -> str:
    lines = canonical_bytes({"runbook": runbook.REQUIRED_RUNBOOK}).decode().splitlines()
    member = "\n".join(lines[1:-1])
    return member + ","


def task_text(target_path: str) -> str:
    return f"""You are one bounded DeepSeek worker editing one declarative, unmounted, default-off Raisa API Spine manifest. Make exactly one model-requested tool call: a direct literal `edit` on `{target_path}`. Do not call read or glob, do not create or delete files, and do not provide a later summary.

Replace exactly this one baseline member:

```json
  \"runbook\": null,
```

with exactly this closed-form member, preserving every other byte:

```json
{_runbook_member_text()}
```

This is a typed box-filling exercise. Do not add prose, keys, values, stages or authority. Ordinary practice, feature flags, allowlists, routes and runtime must remain disabled.
"""


def runner_source(target_path: str) -> bytes:
    target = json.dumps(target_path)
    return f'''import {{ createHash, randomUUID }} from "node:crypto";
import {{ closeSync, openSync, writeFileSync }} from "node:fs";
const TARGET_PATH = {target};
const TOOLS = Object.freeze(["edit", "glob", "read"]);
const SELECTION = Object.freeze({{ provider: "deepseek-official", model: "deepseek-v4-flash", reasoningEffort: "high" }});
const STAGES = new Set(["loader", "packages", "services", "roots", "factory", "published", "turn", "flush", "terminal"]);
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
export function apply(ctx, config) {{
  let stage = "loader";
  let written = false;
  const run = async () => {{
    await ctx.get("loader")?.await();
    stage = "packages";
    const agentModule = await import("@deepseek-ai/dsh-agent");
    const llmModule = await import("@deepseek-ai/dsh-llm");
    const sessionModule = await import("@deepseek-ai/dsh-session");
    const guardModule = await import("./effective-tool-guard.mjs");
    const installModelSelection = agentModule.installModelSelection;
    const createUserMessage = llmModule.createUserMessage;
    const SessionId = sessionModule.SessionId;
    const assertEffectiveToolComposition = guardModule.assertEffectiveToolComposition;
    if (![installModelSelection, createUserMessage, SessionId, assertEffectiveToolComposition].every((value) => typeof value === "function")) throw new Error("PACKAGE_SURFACE_INVALID");
    stage = "services";
    const agents = ctx.get("agents");
    const sessions = ctx.get("sessions");
    const presets = ctx.get("agentPresets");
    if (!agents || !sessions || !presets) throw new Error("REQUIRED_SERVICE_MISSING");
    stage = "roots";
    if (!Array.isArray(presets.roots) || presets.roots.length !== 2 || presets.roots[0].trust !== "system" || presets.roots[1].trust !== "user") throw new Error("PRESET_ROOT_ROSTER_MISMATCH");
    const sessionText = `session-${{randomUUID()}}`;
    let observedCalls = 0;
    let conclusionMarked = false;
    stage = "factory";
    const {{ agent }} = await agents.create({{
      sessionId: SessionId(sessionText),
      meta: {{ cwd: process.cwd() }},
      agentOptions: {{ provider: SELECTION.provider, model: SELECTION.model, maxTokens: 4096 }},
      setup: async (agentCtx) => {{
        const composition = await assertEffectiveToolComposition(agentCtx, presets, "emr4-bounded-worker", TOOLS);
        if (!composition || composition.coordinate !== "EFFECTIVE_TOOL_COMPOSITION_PASSED" || JSON.stringify(composition.effectiveToolNames) !== JSON.stringify(TOOLS)) throw new Error("EFFECTIVE_COMPOSITION_MISMATCH");
        installModelSelection(agentCtx, {{ current: SELECTION, assembled: undefined }});
        agentCtx.on("tools/pre-execute", async (exec, next) => {{
          observedCalls += 1;
          if (observedCalls !== 1 || exec.name !== "edit") return {{ kind: "deny", reason: "ONE_EDIT_ONLY" }};
          const args = exec.arguments;
          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return {{ kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" }};
          return next();
        }});
        agentCtx.on("tools/post-execute", async (exec, result, next) => {{
          const decision = await next();
          const args = exec.arguments;
          if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true && result.isError === false && decision.kind === "accept") {{ exec.concludeTurn(); conclusionMarked = true; }}
          return decision;
        }});
      }},
    }});
    stage = "published";
    if (!agent || agents.get(agent.session.id) === undefined || sessions.get(agent.session.id) === undefined) throw new Error("AGENT_PUBLICATION_MISSING");
    await agent.whenIdle();
    const firstSeq = agent.session.seq;
    stage = "turn";
    agent.followup(createUserMessage({{ content: [{{ type: "text", text: config.task }}], source: {{ kind: "user" }} }}));
    await agent.whenIdle();
    stage = "flush";
    await sessions.flush(agent.session);
    const summary = summarize(agent.session.events, firstSeq);
    const passed = summary.request_count === 1 && summary.tool_names.length === 1 && summary.tool_names[0] === "edit" && summary.tool_result_count === 1 && summary.turn_kind === "completed" && conclusionMarked;
    stage = "terminal";
    writeTerminal(config.terminalPath, {{
      schema_version: "{RUNNER_TERMINAL_SCHEMA_VERSION}", status: passed ? "completed" : "failed", failure_stage: passed ? null : "terminal", session_id_sha256: digest(sessionText), provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, conclusion_marked: conclusionMarked, target_path_sha256: digest(TARGET_PATH), ...summary,
    }});
    written = true;
    ctx.get("appExit")(passed ? 0 : 1);
  }};
  run().catch(() => {{
    if (!written) {{
      const safeStage = STAGES.has(stage) ? stage : "loader";
      writeTerminal(config.terminalPath, {{ schema_version: "{RUNNER_TERMINAL_SCHEMA_VERSION}", status: "failed", failure_stage: safeStage, session_id_sha256: null, provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, conclusion_marked: false, target_path_sha256: digest(TARGET_PATH), request_count: 0, tool_names: [], tool_result_count: 0, turn_kind: null }});
    }}
    ctx.get("appExit")(1);
  }});
}}
'''.encode("utf-8")


def validate_runner_source(payload: bytes, target_path: str) -> dict[str, Any]:
    source = payload.decode("utf-8")
    checks = {
        "target_once": source.count(json.dumps(target_path)) == 1,
        "exact_tools": 'Object.freeze(["edit", "glob", "read"])' in source,
        "one_factory": source.count("await agents.create(") == 1,
        "one_followup": source.count("agent.followup(") == 1,
        "one_pre_hook": source.count('agentCtx.on("tools/pre-execute"') == 1,
        "one_post_hook": source.count('agentCtx.on("tools/post-execute"') == 1,
        "one_conclusion": source.count("exec.concludeTurn()") == 1,
        "one_request_success": "summary.request_count === 1" in source,
        "one_edit_success": 'summary.tool_names[0] === "edit"' in source,
        "root_service_forwarded": "assertEffectiveToolComposition(agentCtx, presets," in source,
        "model_high": 'reasoningEffort: "high"' in source,
        "no_raw_error": all(token not in source for token in ("error.message", "error.stack", "String(error)")),
        "no_retry_shell_subagent": all(token not in source.lower() for token in ("retry(", "pwsh", "bash", "subagent")),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise UsefulWorkerError("runner_source_invalid:" + ",".join(failed))
    return {"bytes": len(payload), "sha256": sha256_bytes(payload), "checks": checks}


def _documentation_bindings() -> dict[str, str]:
    return {
        "plan_sha256": sha256_file(PLAN_PATH),
        "threat_model_sha256": sha256_file(THREAT_PATH),
    }


def _source_bindings() -> dict[str, Any]:
    accepted, inventory = accepted_complete.accepted_module_sources()
    if inventory != accepted_complete.EXPECTED_SOURCE_INVENTORY:
        raise UsefulWorkerError("accepted_complete_source_mismatch")
    target_fixture = (ATTEMPT_ROOT / "workspace" / TARGET_RELATIVE_PATH).as_posix()
    runner = runner_source(target_fixture)
    return {
        "accepted_complete_sources": inventory,
        "occupied_runner": {
            "bytes": len(runner),
            "sha256": sha256_bytes(runner),
        },
        "baseline": {
            "bytes": len(runbook.baseline_bytes()),
            "sha256": sha256_bytes(runbook.baseline_bytes()),
        },
        "required_candidate": {
            "bytes": len(runbook.required_candidate_bytes()),
            "sha256": sha256_bytes(runbook.required_candidate_bytes()),
        },
        "candidate_schema_sha256": sha256_file(CANDIDATE_SCHEMA_PATH),
        "accepted_source_total": sum(row["bytes"] for row in inventory.values()),
        "accepted_sources": accepted,
    }


def contract_value() -> dict[str, Any]:
    bindings = _source_bindings()
    return {
        "schema_version": "ariadne.native_harness_useful_worker_contract.v1",
        "operation_id": OPERATION_ID,
        "attempt": {
            "attempt_id": ATTEMPT_ID,
            "work_order_id": WORK_ORDER_ID,
            "lease_id": LEASE_ID,
            "disposable_root": ATTEMPT_ROOT.as_posix(),
            "evidence_namespace": ATTEMPT_EVIDENCE_ROOT.relative_to(REPO_ROOT).as_posix(),
        },
        "work_package": {
            "target_relative_path": TARGET_RELATIVE_PATH,
            "baseline": bindings["baseline"],
            "required_candidate": bindings["required_candidate"],
            "candidate_schema_sha256": bindings["candidate_schema_sha256"],
            "worker_owned_paths": [TARGET_RELATIVE_PATH],
            "claim": "runbook_contract_present_default_off",
        },
        "occupied_envelope": {
            "provider": "deepseek-official",
            "model": "deepseek-v4-flash",
            "reasoning_effort": "high",
            "maximum_output_tokens": 4096,
            "native_process_limit": 1,
            "provider_request_limit": 1,
            "parallel_tool_call_limit": 1,
            "allowed_tool_names": EXPECTED_TOOLS,
            "admitted_tool_names": ["edit"],
            "automatic_retry_limit": 0,
            "manual_retry_limit": 0,
            "resume_limit": 0,
            "fallback_limit": 0,
            "auxiliary_model_call_limit": 0,
            "upstream_seconds": 300,
            "native_seconds": 420,
        },
        "source_bindings": {
            "accepted_complete_sources": bindings["accepted_complete_sources"],
            "occupied_runner": bindings["occupied_runner"],
        },
        "documentation_bindings": _documentation_bindings(),
        "protected_boundaries": {
            "ordinary_practice_enabled": False,
            "feature_flag_or_allowlist_changed": False,
            "product_or_patient_data_used": False,
            "live_runtime_deployment_release_pages": False,
            "protected_ref_movement": False,
            "raw_prompt_response_reasoning_retained": False,
        },
    }


def write_contract() -> dict[str, Any]:
    value = contract_value()
    jsonschema.Draft202012Validator(load_json(CONTRACT_SCHEMA_PATH)).validate(value)
    payload = canonical_bytes(value)
    CONTRACT_PATH.write_bytes(payload)
    return {"status": "passed", "sha256": sha256_bytes(payload)}


def validate_contract() -> dict[str, Any]:
    value = load_json(CONTRACT_PATH)
    jsonschema.Draft202012Validator(load_json(CONTRACT_SCHEMA_PATH)).validate(value)
    if value != contract_value() or CONTRACT_PATH.read_bytes() != canonical_bytes(value):
        raise UsefulWorkerError("contract_binding_mismatch")
    return value


def validate_authority_boundary() -> None:
    if git("branch", "--show-current") != "codex/ariadne-bernie-davida-parallel-seam":
        raise UsefulWorkerError("task_branch_mismatch")
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    for ref in ("master", "origin/master", "handoff/current", "origin/handoff/current"):
        if git("rev-parse", "--verify", ref) != protected:
            raise UsefulWorkerError("protected_ref_mismatch")
    latch = load_json(LATCH_PATH)
    if (
        latch.get("operation_id") != OPERATION_ID
        or latch.get("status") != "in_progress"
        or latch.get("user_attention", {}).get("required") is not False
        or latch.get("terminal_response", {}).get("permitted") is not False
    ):
        raise UsefulWorkerError("active_operation_latch_mismatch")


def provider_free_check() -> dict[str, Any]:
    contract = validate_contract()
    validate_authority_boundary()
    schema = load_json(CANDIDATE_SCHEMA_PATH)
    if schema.get("const") != runbook.REQUIRED_CANDIDATE:
        raise UsefulWorkerError("candidate_schema_closed_form_mismatch")
    jsonschema.Draft202012Validator(schema).validate(runbook.REQUIRED_CANDIDATE)
    projection = runbook.validate_candidate_bytes(runbook.required_candidate_bytes())
    target = (ATTEMPT_ROOT / "workspace" / TARGET_RELATIVE_PATH).as_posix()
    runner = validate_runner_source(runner_source(target), target)
    node_check = subprocess.run(
        ["node", "--check", str(BROKER_PATH)],
        check=False,
        capture_output=True,
        timeout=30,
    )
    if node_check.returncode != 0:
        raise UsefulWorkerError("broker_syntax_invalid")
    return {
        "schema_version": "ariadne.native_harness_useful_worker_provider_free_check.v1",
        "status": "passed",
        "operation_id": OPERATION_ID,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "runner": runner,
        "candidate": {
            "canonical_sha256": projection["canonical_sha256"],
            "claim": projection["claim"],
        },
        "native_process_count": 0,
        "provider_request_count": 0,
    }


def _initialize_workspace(root: Path) -> dict[str, Any]:
    workspace = root / "workspace"
    target = workspace / TARGET_RELATIVE_PATH
    target.parent.mkdir(parents=True)
    target.write_bytes(runbook.baseline_bytes())
    git_at(workspace, "init", "--quiet")
    git_at(workspace, "config", "user.name", "EMR4 Disposable Worker")
    git_at(workspace, "config", "user.email", "worker@invalid.local")
    git_at(workspace, "add", "--", TARGET_RELATIVE_PATH)
    git_at(workspace, "commit", "--quiet", "-m", "freeze default-off runbook baseline")
    return {
        "workspace": workspace.as_posix(),
        "baseline_commit": git_at(workspace, "rev-parse", "HEAD"),
        "baseline_sha256": sha256_file(target),
    }


def _materialize_profile(root: Path, target_path: str) -> dict[str, Any]:
    package_root, _copied = accepted_worker.projection.materialize_accepted_node_modules(
        root, accepted_worker.projection.load_contract()
    )
    proof = root / "installation" / "proof"
    proof.mkdir(parents=True)
    home = root / "home"
    profile_dir = home / "profiles" / "headless"
    profile_dir.mkdir(parents=True)
    preset_dir = home / ".agent-presets" / "emr4-bounded-worker"
    preset_dir.mkdir(parents=True)
    (profile_dir / "package.json").write_bytes(
        canonical_bytes(
            {
                "name": "dsh-profile-headless",
                "private": True,
                "dependencies": {},
                "dsh": {
                    "profile": {
                        "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
                    }
                },
            }
        )
    )
    (profile_dir / "pnpm-workspace.yaml").write_text(
        "packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        encoding="utf-8",
        newline="\n",
    )
    preset = accepted_worker.projection.native_predecessor.build_preset_source(
        accepted_worker.projection.native_predecessor.load_contract()
    )
    (preset_dir / "agent.cordis.yml").write_bytes(preset)
    accepted_sources, _inventory = accepted_complete.accepted_module_sources()
    (proof / "effective-tool-guard.mjs").write_bytes(accepted_sources["derived_guard"])
    (proof / "preset-mount-sanitizer-runner-bridge.mjs").write_bytes(
        accepted_sources["derived_bridge"]
    )
    (proof / "deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs").write_bytes(
        accepted_sources["accepted_sanitizer"]
    )
    occupied_runner = runner_source(target_path)
    (proof / "runner.mjs").write_bytes(occupied_runner)
    (proof / "sentinel.mjs").write_bytes(accepted_worker.sentinel_source())
    package = load_json(package_root / "package.json")
    if package.get("name") != "@deepseek-ai/dsh" or package.get("version") != "0.1.0-rc.7":
        raise UsefulWorkerError("materialized_package_identity_mismatch")
    return {
        "package_root": package_root.as_posix(),
        "package_json_sha256": sha256_file(package_root / "package.json"),
        "preset_sha256": sha256_bytes(preset),
        "guard_sha256": sha256_file(proof / "effective-tool-guard.mjs"),
        "bridge_sha256": sha256_file(proof / "preset-mount-sanitizer-runner-bridge.mjs"),
        "sanitizer_sha256": sha256_file(
            proof
            / "deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs"
        ),
        "runner_sha256": sha256_bytes(occupied_runner),
        "sentinel_sha256": sha256_file(proof / "sentinel.mjs"),
    }


def _review_candidate_source(path: Path) -> str:
    receipt = load_json(path)
    if receipt.get("schema_version") == "ariadne.validation_run.v1":
        from scripts.ariadne_evidence_gate import command_manifest_sha256

        commands = receipt.get("commands")
        results = receipt.get("results")
        manifest = {
            "schema_version": "ariadne.verifier-command-manifest.v1",
            "commands": commands,
        }
        if (
            receipt.get("status") != "passed"
            or receipt.get("failure_command_id") is not None
            or receipt.get("repo_root") != str(REPO_ROOT.resolve())
            or not isinstance(commands, list)
            or not isinstance(results, list)
            or len(commands) != len(results)
            or receipt.get("command_manifest_sha256")
            != command_manifest_sha256(manifest)
        ):
            raise UsefulWorkerError("deterministic_admission_receipt_invalid")
        result_by_id = {
            result.get("id"): result
            for result in results
            if isinstance(result, dict) and isinstance(result.get("id"), str)
        }
        command_by_id = {
            command.get("id"): command
            for command in commands
            if isinstance(command, dict) and isinstance(command.get("id"), str)
        }
        if len(result_by_id) != len(results) or len(command_by_id) != len(commands):
            raise UsefulWorkerError("deterministic_admission_receipt_invalid")
        for command_id, command in command_by_id.items():
            result = result_by_id.get(command_id)
            if (
                not isinstance(result, dict)
                or result.get("argv") != command.get("argv")
                or result.get("status") != "passed"
                or result.get("exit_code") != 0
                or result.get("error_code") is not None
            ):
                raise UsefulWorkerError("deterministic_admission_receipt_invalid")
        source_result = result_by_id.get("C02")
        tracked_clean_result = result_by_id.get("C07")
        if (
            not isinstance(source_result, dict)
            or not isinstance(tracked_clean_result, dict)
            or command_by_id.get("C02")
            != {"id": "C02", "argv": ["git", "rev-parse", "HEAD"]}
            or command_by_id.get("C07")
            != {
                "id": "C07",
                "argv": ["git", "diff", "--exit-code", "HEAD", "--"],
            }
            or source_result.get("stdout_bytes") != 41
            or source_result.get("stderr_bytes") != 0
            or source_result.get("stderr_sha256") != sha256_bytes(b"")
            or tracked_clean_result.get("stdout_bytes") != 0
            or tracked_clean_result.get("stderr_bytes") != 0
            or tracked_clean_result.get("stdout_sha256") != sha256_bytes(b"")
            or tracked_clean_result.get("stderr_sha256") != sha256_bytes(b"")
        ):
            raise UsefulWorkerError("deterministic_admission_receipt_invalid")
        matching_sources = [
            candidate
            for candidate in git("rev-list", "HEAD").splitlines()
            if FULL_OID.fullmatch(candidate) is not None
            and sha256_bytes(f"{candidate}\n".encode("ascii"))
            == source_result.get("stdout_sha256")
        ]
        if len(matching_sources) != 1:
            raise UsefulWorkerError("deterministic_admission_receipt_invalid")
        return matching_sources[0]
    source = receipt.get("head_before")
    if (
        receipt.get("status", receipt.get("decision")) not in {"passed", "pass", "accepted"}
        or not isinstance(source, str)
        or FULL_OID.fullmatch(source) is None
        or receipt.get("head_after") != source
        or receipt.get("dirty_after") is not False
        or git("rev-parse", "--verify", f"{source}^{{commit}}") != source
    ):
        raise UsefulWorkerError("deterministic_admission_receipt_invalid")
    if subprocess.run(
        ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", source, "HEAD"],
        check=False,
        capture_output=True,
        timeout=15,
    ).returncode != 0:
        raise UsefulWorkerError("reviewed_source_not_ancestor")
    return source


def prepare_attempt(review_receipt: Path) -> dict[str, Any]:
    provider_free_check()
    if ATTEMPT_ROOT.exists() or any(
        path.exists()
        for path in (
            PREPARATION_PATH,
            WORK_ORDER_PATH,
            AUTHORITY_PATH,
            FORBIDDEN_PATH,
            COMMAND_MANIFEST_PATH,
            NO_DATABASE_ADMISSION_PATH,
            CHECKPOINT_PATH,
            CONSUMED_PATH,
            TERMINAL_PATH,
            CANDIDATE_OUTPUT_PATH,
            PRE_HMR_TERMINAL_PATH,
        )
    ):
        raise UsefulWorkerError("attempt_identity_not_fresh")
    source = _review_candidate_source(review_receipt.resolve())
    parent = Path("C:/Users/sarashera/EMR4-worktrees").resolve()
    root = ATTEMPT_ROOT.resolve()
    if root.parent != parent or root.is_symlink():
        raise UsefulWorkerError("attempt_root_invalid")
    root.mkdir(parents=False)
    try:
        workspace = _initialize_workspace(root)
        target = (root / "workspace" / TARGET_RELATIVE_PATH).resolve().as_posix()
        profile = _materialize_profile(root, target)
        from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
        from scripts.ariadne_validation_runner import (
            validate_execution_manifest_with_admission,
        )

        python = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
        manifest = {
            "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
            "commands": [
                {
                    "id": "PF_NATIVE_USEFUL_WORKER",
                    "argv": [
                        str(python),
                        "-m",
                        "scripts.ariadne_provider_free_pytest",
                        "--repo-root",
                        str(REPO_ROOT),
                        "tests/test_raisa_native_harness_bounded_occupied_useful_worker_rehearsal.py",
                        "tests/test_ariadne_deepseek_native_harness_broker.py",
                    ],
                }
            ],
        }
        admitted_manifest, admission = validate_execution_manifest_with_admission(
            manifest, repo_root=REPO_ROOT, require_provider_free=True
        )
        if admission is None or admission.get("status") != "passed":
            raise UsefulWorkerError("provider_free_command_admission_failed")
        authority = {
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "candidate_source": source,
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
            "manual_retries": 0,
            "fallbacks": 0,
            "auxiliary_model_calls": 0,
            "allowed_tool_names": EXPECTED_TOOLS,
            "admitted_tool_names": ["edit"],
            "owned_path": TARGET_RELATIVE_PATH,
            "prompt_sha256": sha256_bytes(task_text(target).encode("utf-8")),
        }
        forbidden = {
            "forbidden_surfaces": [
                "second_worker_retry_resume_or_fallback",
                "read_glob_shell_git_docker_database_network_or_subagent_tool",
                "unowned_file_creation_change_delete_or_rename",
                "ordinary_practice_feature_flag_allowlist_or_command_mounting",
                "generic_status_arrived_grammar_client_or_waiting_area_change",
                "product_patient_appointment_clinical_historical_or_protected_data",
                "production_deployment_release_pages_or_protected_refs",
                "raw_prompt_response_reasoning_stream_session_environment_or_credential_retention",
            ]
        }
        transaction = load_json(TRANSACTION_PATH)
        journal = transaction.get("journal")
        if not isinstance(journal, list) or not journal:
            raise UsefulWorkerError("clockwork_journal_missing")
        tip = journal[-1]
        manifest_digest = sha256_bytes(canonical_bytes(admitted_manifest))
        admission_digest = sha256_bytes(canonical_bytes(admission))
        work_order = {
            "schema_version": "ariadne.deepseek_work_order.v2",
            "work_order_id": WORK_ORDER_ID,
            "transaction_id": transaction["transaction_id"],
            "operation_id": OPERATION_ID,
            "lease_id": LEASE_ID,
            "journal_id": tip["journal_id"],
            "source_commit": source,
            "authority_sha256": "sha256:" + sha256_bytes(compact_bytes(authority)),
            "forbidden_surfaces_sha256": "sha256:" + sha256_bytes(compact_bytes(forbidden)),
            "command_manifest_sha256": "sha256:" + manifest_digest,
            "provider_free_no_database_admission_sha256": "sha256:" + admission_digest,
            "branch": git("branch", "--show-current"),
            "worktree": (root / "workspace").resolve().as_posix(),
            "allowed_tool_names": EXPECTED_TOOLS,
            "posture": "provider_free_shadow",
            "next_sequence": tip["sequence"] + 1,
            "previous_event_sha256": tip["event_sha256"],
        }
        jsonschema.Draft202012Validator(load_json(WORK_ORDER_SCHEMA_PATH)).validate(work_order)
        write_json_exclusive(AUTHORITY_PATH, authority)
        write_json_exclusive(FORBIDDEN_PATH, forbidden)
        write_json_exclusive(COMMAND_MANIFEST_PATH, admitted_manifest)
        write_json_exclusive(NO_DATABASE_ADMISSION_PATH, admission)
        write_json_exclusive(WORK_ORDER_PATH, work_order)
        receipt_relative = review_receipt.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        preparation = {
            "schema_version": "ariadne.native_harness_useful_worker_preparation.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "status": "passed",
            "candidate_source": source,
            "review_receipt": receipt_relative,
            "review_receipt_sha256": sha256_file(review_receipt),
            "attempt_root": root.as_posix(),
            "workspace": workspace,
            "profile": profile,
            "work_order_sha256": sha256_file(WORK_ORDER_PATH),
            "authority_sha256": sha256_file(AUTHORITY_PATH),
            "forbidden_sha256": sha256_file(FORBIDDEN_PATH),
            "command_manifest_sha256": sha256_file(COMMAND_MANIFEST_PATH),
            "no_database_admission_sha256": sha256_file(NO_DATABASE_ADMISSION_PATH),
            "native_process_count": 0,
            "provider_request_count": 0,
            "checkpoint_admitted": False,
        }
        write_json_exclusive(PREPARATION_PATH, preparation)
        return preparation
    except Exception:
        remove_exact_attempt_root(root, parent)
        raise


def _admit_checkpoint_source(preparation: dict[str, Any], tick: dict[str, Any]) -> str:
    candidate_source = preparation.get("candidate_source")
    checkpoint_source = tick.get("source_commit")
    review_receipt = preparation.get("review_receipt")
    if (
        not isinstance(candidate_source, str)
        or FULL_OID.fullmatch(candidate_source) is None
        or not isinstance(checkpoint_source, str)
        or FULL_OID.fullmatch(checkpoint_source) is None
        or not isinstance(review_receipt, str)
        or git("rev-parse", "--verify", f"{checkpoint_source}^{{commit}}")
        != checkpoint_source
        or subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "merge-base",
                "--is-ancestor",
                candidate_source,
                checkpoint_source,
            ],
            check=False,
            capture_output=True,
            timeout=15,
        ).returncode
        != 0
    ):
        raise UsefulWorkerError("clockwork_checkpoint_source_invalid")
    evidence_delta = git(
        "diff", "--name-only", f"{candidate_source}..{checkpoint_source}", "--"
    ).splitlines()
    if evidence_delta != [review_receipt]:
        raise UsefulWorkerError("clockwork_checkpoint_source_delta_invalid")
    return checkpoint_source


def admit_checkpoint(clockwork_evidence: Path) -> dict[str, Any]:
    if CHECKPOINT_PATH.exists() or CONSUMED_PATH.exists():
        raise UsefulWorkerError("checkpoint_identity_not_fresh")
    preparation = load_json(PREPARATION_PATH)
    tick = load_json(clockwork_evidence)
    if (
        tick.get("status") != "passed"
        or tick.get("operation_id") != OPERATION_ID
        or tick.get("event_kind") != "checkpoint_transition"
    ):
        raise UsefulWorkerError("clockwork_checkpoint_invalid")
    checkpoint_source = _admit_checkpoint_source(preparation, tick)
    authority = load_json(AUTHORITY_PATH)
    checkpoint = {
        "schema_version": "ariadne.native_harness_useful_worker_checkpoint.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "status": "admitted",
        "candidate_source": preparation["candidate_source"],
        "checkpoint_source": checkpoint_source,
        "review_receipt": preparation["review_receipt"],
        "review_receipt_sha256": preparation["review_receipt_sha256"],
        "preparation_sha256": sha256_file(PREPARATION_PATH),
        "work_order_sha256": sha256_file(WORK_ORDER_PATH),
        "runner_sha256": preparation["profile"]["runner_sha256"],
        "prompt_sha256": authority["prompt_sha256"],
        "clockwork_checkpoint_sha256": sha256_file(clockwork_evidence),
        "attempt_root": ATTEMPT_ROOT.resolve().as_posix(),
        "native_process_limit": 1,
        "provider_request_limit": 1,
        "automatic_retry_limit": 0,
        "fallback_limit": 0,
        "auxiliary_model_call_limit": 0,
        "expected_tool_names": ["edit"],
        "expected_changed_paths": [TARGET_RELATIVE_PATH],
        "checkpoint_admitted": True,
    }
    write_json_exclusive(CHECKPOINT_PATH, checkpoint)
    return checkpoint


def _load_checkpoint() -> dict[str, Any]:
    value = load_json(CHECKPOINT_PATH)
    preparation = load_json(PREPARATION_PATH)
    authority = load_json(AUTHORITY_PATH)
    checkpoint_source = _admit_checkpoint_source(
        preparation, {"source_commit": value.get("checkpoint_source")}
    )
    expected = {
        "schema_version": "ariadne.native_harness_useful_worker_checkpoint.v1",
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "status": "admitted",
        "candidate_source": preparation["candidate_source"],
        "checkpoint_source": checkpoint_source,
        "review_receipt": preparation["review_receipt"],
        "review_receipt_sha256": preparation["review_receipt_sha256"],
        "preparation_sha256": sha256_file(PREPARATION_PATH),
        "work_order_sha256": sha256_file(WORK_ORDER_PATH),
        "runner_sha256": preparation["profile"]["runner_sha256"],
        "prompt_sha256": authority["prompt_sha256"],
        "clockwork_checkpoint_sha256": value.get("clockwork_checkpoint_sha256"),
        "attempt_root": ATTEMPT_ROOT.resolve().as_posix(),
        "native_process_limit": 1,
        "provider_request_limit": 1,
        "automatic_retry_limit": 0,
        "fallback_limit": 0,
        "auxiliary_model_call_limit": 0,
        "expected_tool_names": ["edit"],
        "expected_changed_paths": [TARGET_RELATIVE_PATH],
        "checkpoint_admitted": True,
    }
    if value != expected or not isinstance(value.get("clockwork_checkpoint_sha256"), str):
        raise UsefulWorkerError("checkpoint_binding_mismatch")
    return value


def _worker_environment(root: Path, port: int, token: str) -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in ("PATH", "PATHEXT", "SYSTEMROOT", "TEMP", "TMP", "WINDIR", "COMSPEC")
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
    if any(key in environment for key in ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY")):
        raise UsefulWorkerError("worker_provider_credential_present")
    return environment


def _broker_environment(token: str) -> dict[str, str]:
    provider_key = os.environ.get("DEEPSEEK_API_KEY")
    if not provider_key:
        raise UsefulWorkerError("provider_key_missing")
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
        "EMR4_BROKER_WORK_ORDER_SHA256": canonical_object_sha256(load_json(WORK_ORDER_PATH)),
        "EMR4_BROKER_COMMAND_MANIFEST_PATH": str(COMMAND_MANIFEST_PATH),
        "EMR4_BROKER_NO_DATABASE_ADMISSION_PATH": str(NO_DATABASE_ADMISSION_PATH),
    }


def _collect_lines(stream: Any, output: queue.Queue[str], retained: list[str]) -> None:
    for line in stream:
        value = line.rstrip("\r\n")
        retained.append(value)
        output.put(value)


def _wait_json_line(lines: queue.Queue[str], timeout: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = json.loads(lines.get(timeout=0.1))
        except queue.Empty:
            continue
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise UsefulWorkerError("broker_ready_timeout")


def _hmr_events(path: Path) -> list[str]:
    if not path.exists():
        return []
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        if isinstance(value, dict) and isinstance(value.get("event"), str):
            names.append(value["event"])
    return names


def _terminate(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _stream_reading(path: Path) -> dict[str, Any]:
    try:
        return startup_terminal.read_startup_stream(path)
    except startup_terminal.StartupTerminalError:
        return {"byte_count": 0, "sha256": sha256_bytes(b"")}


def execute_native() -> dict[str, Any]:
    checkpoint = _load_checkpoint()
    validate_authority_boundary()
    if any(path.exists() for path in (CONSUMED_PATH, TERMINAL_PATH, CANDIDATE_OUTPUT_PATH, PRE_HMR_TERMINAL_PATH)):
        raise UsefulWorkerError("occupied_attempt_already_consumed")
    root = ATTEMPT_ROOT.resolve()
    parent = Path("C:/Users/sarashera/EMR4-worktrees").resolve()
    if root.parent != parent or not root.is_dir() or root.is_symlink():
        raise UsefulWorkerError("prepared_attempt_root_invalid")
    write_json_exclusive(
        CONSUMED_PATH,
        {
            "schema_version": "ariadne.native_harness_useful_worker_consumed.v1",
            "operation_id": OPERATION_ID,
            "attempt_id": ATTEMPT_ID,
            "state": "consumed",
            "candidate_source": checkpoint["candidate_source"],
            "automatic_retry_count": 0,
            "resume_permitted": False,
        },
    )
    broker: subprocess.Popen[str] | None = None
    harness: subprocess.Popen[bytes] | None = None
    broker_lines: list[str] = []
    broker_queue: queue.Queue[str] = queue.Queue()
    broker_thread: threading.Thread | None = None
    failure: str | None = None
    harness_exit: int | None = None
    native_started = False
    start = time.monotonic()
    root_workspace = root / "workspace"
    target = root_workspace / TARGET_RELATIVE_PATH
    stdout_path = root / "harness-stdout.raw"
    stderr_path = root / "harness-stderr.raw"
    broker_stderr_path = root / "broker-stderr.raw"
    runner_terminal_path = root / "runner-terminal.json"
    event_path = root / "hmr-events.jsonl"
    profile_path = root / "home" / "profiles" / "headless" / "cordis.patch.yml"
    runner: dict[str, Any] = {}
    hmr_names: list[str] = []
    candidate_projection: dict[str, Any] | None = None
    candidate_bytes: bytes | None = None
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
                raise UsefulWorkerError("broker_stdout_missing")
            broker_thread = threading.Thread(
                target=_collect_lines,
                args=(broker.stdout, broker_queue, broker_lines),
                daemon=True,
            )
            broker_thread.start()
            ready = _wait_json_line(broker_queue, 15)
            if (
                ready.get("event") != "broker-ready"
                or ready.get("allowed_tool_names") != EXPECTED_TOOLS
                or ready.get("maximum_provider_calls") != 1
                or ready.get("model_id") != "deepseek-v4-flash"
            ):
                raise UsefulWorkerError("broker_ready_contract_mismatch")
            port = ready.get("listen_port")
            if not isinstance(port, int) or not 1 <= port <= 65535:
                raise UsefulWorkerError("broker_port_invalid")
            initial = accepted_worker.profile_patch(root, port, changed=False)
            changed = accepted_worker.profile_patch(root, port, changed=True)
            accepted_worker.validate_profile_patch(initial, changed=False)
            accepted_worker.validate_profile_patch(changed, changed=True)
            profile_path.write_bytes(initial)
            package_root = root / "installation" / "node_modules" / "@deepseek-ai" / "dsh"
            wrapper_path = root / "entrypoint-wrapper.mjs"
            diagnostic_path = root / "pre-hmr-structured-diagnostic.json"
            wrapper = diagnostic.build_entrypoint_wrapper_source(
                package_root=package_root.resolve(strict=True),
                wrapper_path=wrapper_path,
                diagnostic_path=diagnostic_path,
                disposable_root=root,
                operation_id=OPERATION_ID,
                attempt_id=ATTEMPT_ID,
                candidate_source=checkpoint["candidate_source"],
                canonical_json=True,
            )
            wrapper_path.write_bytes(wrapper)
            command = diagnostic.build_launch_command(
                node_executable="node",
                wrapper_path=wrapper_path,
                profile="headless",
                task=task_text(target.resolve().as_posix()),
            )
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                harness = subprocess.Popen(
                    command,
                    cwd=root_workspace,
                    env=_worker_environment(root, port, token),
                    stdout=stdout,
                    stderr=stderr,
                )
                native_started = True
                deadline = time.monotonic() + 420
                changed_profile = False
                while harness.poll() is None:
                    hmr_names = _hmr_events(event_path)
                    if "stock_headless_hmr_ready" in hmr_names and not changed_profile:
                        profile_path.write_bytes(changed)
                        changed_profile = True
                    if time.monotonic() >= deadline:
                        failure = "native_worker_timeout"
                        _terminate(harness)
                        break
                    time.sleep(0.05)
                harness_exit = harness.poll()
            time.sleep(0.25)
            hmr_names = _hmr_events(event_path)
            if runner_terminal_path.is_file():
                runner = load_json(runner_terminal_path)
            if harness_exit != 0 and failure is None:
                failure = "native_harness_terminal_failure"
    except (UsefulWorkerError, OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError):
        if failure is None:
            failure = "occupied_transport_failure"
    finally:
        _terminate(harness)
        _terminate(broker)
        if broker_thread is not None:
            broker_thread.join(timeout=10)

    changed_paths = sorted(
        line[3:].replace("\\", "/")
        for line in git_at(root_workspace, "status", "--porcelain=v1").splitlines()
        if len(line) >= 4
    )
    try:
        if target.is_file():
            candidate_bytes = target.read_bytes()
            candidate_projection = runbook.validate_candidate_bytes(candidate_bytes)
            jsonschema.Draft202012Validator(load_json(CANDIDATE_SCHEMA_PATH)).validate(
                candidate_projection["value"]
            )
    except (
        OSError,
        runbook.RunbookValidationError,
        jsonschema.ValidationError,
    ):
        candidate_projection = None

    broker_events: list[dict[str, Any]] = []
    for line in broker_lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            broker_events.append(value)
    broker_counts = {
        "provider_call_started": sum(row.get("event") == "provider-call-started" for row in broker_events),
        "provider_call_completed": sum(row.get("event") == "provider-call-completed" for row in broker_events),
        "provider_call_failed": sum(row.get("event") == "provider-call-failed" for row in broker_events),
        "request_rejected": sum(row.get("event") == "broker-request-rejected" for row in broker_events),
    }
    runner_passed = (
        runner.get("schema_version") == RUNNER_TERMINAL_SCHEMA_VERSION
        and runner.get("status") == "completed"
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
        and changed_paths == [TARGET_RELATIVE_PATH]
        and candidate_projection is not None
    )
    if not success and failure is None:
        failure = (
            "useful_worker_candidate_rejected"
            if candidate_projection is None
            else "occupied_acceptance_mismatch"
        )
    stream_readings = {
        "stdout": _stream_reading(stdout_path),
        "stderr": _stream_reading(stderr_path),
        "broker_stderr": _stream_reading(broker_stderr_path),
    }
    cleanup_passed = remove_exact_attempt_root(root, parent)
    root_absent = not root.exists()
    if not cleanup_passed or not root_absent:
        success = False
        failure = "attempt_root_cleanup_failed"
        candidate_projection = None
        candidate_bytes = None
    if success and candidate_projection is not None:
        CANDIDATE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(CANDIDATE_OUTPUT_PATH, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(candidate_projection["canonical_bytes"])
    terminal_class = (
        "useful_worker_pass"
        if success
        else (
            "useful_worker_candidate_rejected"
            if failure == "useful_worker_candidate_rejected"
            else "useful_worker_transport_terminal"
        )
    )
    terminal = {
        "schema_version": TERMINAL_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "candidate_source": checkpoint["candidate_source"],
        "result": "pass" if success else "failed_closed",
        "terminal_class": terminal_class,
        "failure_coordinate": None if success else failure,
        "process": {
            "native_process_count": 1 if native_started else 0,
            "harness_exit_code": harness_exit,
            "wall_clock_ms": round((time.monotonic() - start) * 1000),
            "stdout_bytes": stream_readings["stdout"]["byte_count"],
            "stdout_sha256": stream_readings["stdout"]["sha256"],
            "stderr_bytes": stream_readings["stderr"]["byte_count"],
            "stderr_sha256": stream_readings["stderr"]["sha256"],
            "broker_stderr_bytes": stream_readings["broker_stderr"]["byte_count"],
            "broker_stderr_sha256": stream_readings["broker_stderr"]["sha256"],
        },
        "hmr_events": hmr_names,
        "runner": runner,
        "broker": broker_counts,
        "candidate": {
            "changed_paths": changed_paths,
            "admitted": candidate_projection is not None,
            "canonical_byte_count": (
                candidate_projection["canonical_byte_count"]
                if candidate_projection is not None
                else None
            ),
            "canonical_sha256": (
                candidate_projection["canonical_sha256"]
                if candidate_projection is not None
                else None
            ),
            "retained_path": (
                CANDIDATE_OUTPUT_PATH.relative_to(REPO_ROOT).as_posix()
                if success
                else None
            ),
            "claim": candidate_projection["claim"] if success else None,
        },
        "automatic_retry_count": 0,
        "manual_retry_count": 0,
        "resume_count": 0,
        "fallback_count": 0,
        "auxiliary_model_call_count": 0,
        "cleanup": {
            "harness_absent": harness is None or harness.poll() is not None,
            "broker_absent": broker is None or broker.poll() is not None,
            "attempt_root_absent": root_absent,
            "raw_logs_retained": False,
            "raw_session_retained": False,
            "raw_prompt_response_reasoning_retained": False,
            "provider_key_present_in_worker_environment": False,
        },
    }
    jsonschema.Draft202012Validator(load_json(TERMINAL_SCHEMA_PATH)).validate(terminal)
    write_json_exclusive(TERMINAL_PATH, terminal)
    REPORT_PATH.write_text(render_report(terminal), encoding="utf-8", newline="\n")
    if not success:
        raise UsefulWorkerError("occupied_attempt_failed_closed:" + str(failure))
    return terminal


def render_report(terminal: dict[str, Any]) -> str:
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    return f"""# Native Harness useful-worker occupied report

Date: {timestamp[:10]}

Timestamp: {timestamp} (Australia/Brisbane)

Result: `{terminal['result']}`

Terminal class: `{terminal['terminal_class']}`

- Attempt: `{terminal['attempt_id']}`
- Native process count: `{terminal['process']['native_process_count']}`
- Provider calls started/completed: `{terminal['broker']['provider_call_started']}` / `{terminal['broker']['provider_call_completed']}`
- Candidate admitted: `{str(terminal['candidate']['admitted']).lower()}`
- Retry/resume/fallback/auxiliary model: `0 / 0 / 0 / 0`
- Disposable root absent: `{str(terminal['cleanup']['attempt_root_absent']).lower()}`

The result applies only to one declarative default-off runbook candidate. It
does not enable ordinary practice or prove general Harness reliability.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--write-contract", action="store_true")
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--prepare-attempt", action="store_true")
    actions.add_argument("--admit-checkpoint", action="store_true")
    actions.add_argument("--native", action="store_true")
    parser.add_argument("--review-receipt", type=Path)
    parser.add_argument("--clockwork-evidence", type=Path)
    args = parser.parse_args()
    try:
        if args.write_contract:
            value = write_contract()
        elif args.check:
            value = provider_free_check()
        elif args.prepare_attempt:
            if args.review_receipt is None:
                raise UsefulWorkerError("review_receipt_required")
            value = prepare_attempt(args.review_receipt)
        elif args.admit_checkpoint:
            if args.clockwork_evidence is None:
                raise UsefulWorkerError("clockwork_evidence_required")
            value = admit_checkpoint(args.clockwork_evidence)
        else:
            value = execute_native()
        print(json.dumps({"status": value.get("status", value.get("result")), "operation_id": OPERATION_ID}))
        return 0
    except (
        UsefulWorkerError,
        runbook.RunbookValidationError,
        jsonschema.ValidationError,
        OSError,
        ValueError,
    ) as error:
        print(json.dumps({"status": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
