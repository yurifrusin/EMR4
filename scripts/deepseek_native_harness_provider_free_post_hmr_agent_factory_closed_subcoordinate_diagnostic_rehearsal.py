"""Attribute the rc.7 post-HMR agent-factory boundary without a model request."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

import jsonschema
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness import (  # noqa: E402
    native_post_hmr_future_attempt_materialisation as base_bundle,
)
from orchestration_harness import (  # noqa: E402
    native_post_hmr_future_attempt_rebinding as rebinding,
)
from orchestration_harness import (  # noqa: E402
    native_post_hmr_pre_request_controller as joined_controller,
)
from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_rebound_future_runner_agent_creation_boundary_rehearsal as predecessor,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-post-hmr-agent-factory-closed-"
    "subcoordinate-diagnostic-rehearsal"
)
EXECUTION_ATTEMPT_ID = "post-hmr-agent-factory-diagnostic-attempt-001"
PRIVATE_SESSION_ID = "session-emr4-agent-factory-diagnostic-001"
PUBLICATION_STOP = "EMR4_AGENT_PUBLICATION_STOP"
PRESET_ID = "emr4-bounded-worker"
EXPECTED_TOOLS = ["edit", "glob", "read"]
TARGET_PATH = "workspace/authored_synthetic_control_probe.py"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
SIDECAR_SCHEMA_PATH = OPERATION_ROOT / "diagnostic-sidecar.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "agent-factory-diagnostic-evidence.json"
REPORT_PATH = OPERATION_ROOT / "agent-factory-diagnostic-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
ATTEMPT_CONSUMED_PATH = OPERATION_ROOT / "native-attempt-consumed.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_post_hmr_agent_factory_closed_subcoordinate_diagnostic_rehearsal.py"
)
ACCEPTED_CONTROLLER_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_controller.py"
)
PREDECESSOR_CLOSEOUT_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-rebound-future-runner-agent-creation-boundary-rehearsal-closeout.md"
)
PREDECESSOR_FAILURE_PATH = (
    predecessor.OPERATION_ROOT / "failure-interpretation.json"
)
PREDECESSOR_REJECTION_PATH = (
    predecessor.OPERATION_ROOT / "rejected-generated-claims.json"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
MAX_SIDECAR_BYTES = 8_192
SIDECAR_SCHEMA = "ariadne.native_harness_agent_factory_diagnostic_sidecar.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_agent_factory_diagnostic_evidence.v1"
REPORT_TIMESTAMP = "2026-08-22T04:15:00+10:00"

STAGES = [
    "runner_apply_entered",
    "loader_ready",
    "package_imports_admitted",
    "services_resolved",
    "preset_roots_admitted",
    "preset_roster_admitted",
    "registries_empty_before_factory",
    "session_identity_constructed",
    "agent_factory_invoked",
    "factory_setup_entered",
    "private_identity_admitted",
    "preset_composition_admitted",
    "model_selection_installed",
    "setup_commit_entered",
    "publication_veto_observed",
    "postrollback_registries_empty",
]
ERROR_CLASSES = [
    "loader_await_rejected",
    "package_import_rejected",
    "required_service_missing",
    "preset_root_count_mismatch",
    "shipped_root_mismatch",
    "user_root_mismatch",
    "preset_roster_mismatch",
    "registry_not_empty",
    "private_identity_mismatch",
    "private_object_prepublished",
    "effective_composition_mismatch",
    "commit_identity_mismatch",
    "commit_publication_early",
    "commit_composition_mismatch",
    "publication_veto_mismatch",
    "factory_resolved_without_veto",
    "private_identity_retained",
    "lifecycle_event_escaped",
    "cwd_not_absolute",
    "unclassified_error",
]
TERMINALS = [
    "closed_subcoordinate_failure",
    "prepublication_veto_diagnosed",
    "runner_link_or_apply_absence",
]


class ClosedSubcoordinateError(RuntimeError):
    """The closed diagnostic did not satisfy its frozen contract."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()


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
        raise ClosedSubcoordinateError("git_resolution_failed")
    return completed.stdout.strip()


def _ancestor(object_id: str) -> bool:
    return (
        FULL_OID.fullmatch(object_id) is not None
        and subprocess.run(
            ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["schema_version"]
        != "ariadne.native_harness_agent_factory_diagnostic_contract.v1"
        or contract["operation_id"] != OPERATION_ID
        or contract["planning_source"]
        != _git("rev-parse", "--verify", f"{contract['planning_source']}^{{commit}}")
        or contract["planning_source"]
        != _git("log", "-1", "--format=%H", "--", plan_relative)
    ):
        raise ClosedSubcoordinateError("contract_identity_or_planning_source_invalid")
    if contract["execution_attempt"] != {
        "attempt_id": EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }:
        raise ClosedSubcoordinateError("one_process_latch_invalid")
    if contract["closed_vocabulary"] != {
        "stages": STAGES,
        "error_classes": ERROR_CLASSES,
        "terminals": TERMINALS,
    }:
        raise ClosedSubcoordinateError("closed_vocabulary_invalid")
    if contract["factory_boundary"] != {
        "private_session_id": PRIVATE_SESSION_ID,
        "publication_stop": PUBLICATION_STOP,
        "agents_create_invocations_max": 1,
        "published_agents": 0,
        "published_sessions": 0,
    }:
        raise ClosedSubcoordinateError("factory_boundary_invalid")
    if contract["selection"] != {
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "max_tokens": 4096,
    }:
        raise ClosedSubcoordinateError("selection_invalid")
    return contract


def runner_source() -> bytes:
    return r'''import { createHash } from "node:crypto";
import { closeSync, openSync, writeFileSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";

export const name = "provider-free-agent-factory-closed-subcoordinate-runner";
export const inject = ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"];
const PRIVATE_ID = "session-emr4-agent-factory-diagnostic-001";
const PRESET_ID = "emr4-bounded-worker";
const PUBLICATION_STOP = "EMR4_AGENT_PUBLICATION_STOP";
const TARGET_PATH = "workspace/authored_synthetic_control_probe.py";
const TOOLS = Object.freeze(["edit", "glob", "read"]);
const SELECTION = Object.freeze({ provider: "deepseek-official", model: "deepseek-v4-flash", reasoningEffort: "high" });
const KNOWN_ERRORS = Object.freeze({
  REQUIRED_SERVICE_MISSING: "required_service_missing",
  PRESET_ROOT_COUNT_MISMATCH: "preset_root_count_mismatch",
  SHIPPED_ROOT_MISMATCH: "shipped_root_mismatch",
  USER_ROOT_MISMATCH: "user_root_mismatch",
  PRESET_ROSTER_MISMATCH: "preset_roster_mismatch",
  LIVE_REGISTRY_NOT_EMPTY: "registry_not_empty",
  PRIVATE_IDENTITY_MISMATCH: "private_identity_mismatch",
  PRIVATE_OBJECT_PREPUBLISHED: "private_object_prepublished",
  EFFECTIVE_COMPOSITION_MISMATCH: "effective_composition_mismatch",
  COMMIT_IDENTITY_MISMATCH: "commit_identity_mismatch",
  COMMIT_PUBLICATION_EARLY: "commit_publication_early",
  COMMIT_COMPOSITION_MISMATCH: "commit_composition_mismatch",
  PUBLICATION_VETO_MISMATCH: "publication_veto_mismatch",
  AGENT_CREATE_RESOLVED: "factory_resolved_without_veto",
  PRIVATE_IDENTITY_RETAINED: "private_identity_retained",
  LIFECYCLE_EVENT_ESCAPED: "lifecycle_event_escaped",
  CWD_NOT_ABSOLUTE: "cwd_not_absolute",
});

function digest(value) { return createHash("sha256").update(value).digest("hex"); }
function writeExclusive(path, value) {
  const descriptor = openSync(path, "wx");
  try { writeFileSync(descriptor, JSON.stringify(value) + "\n", "utf8"); }
  finally { closeSync(descriptor); }
}
function requireEmpty(agents, sessions) {
  if (agents.list().length !== 0 || sessions.list().length !== 0) throw new Error("LIVE_REGISTRY_NOT_EMPTY");
}
function classify(error, lastStage) {
  if (error instanceof Error && Object.hasOwn(KNOWN_ERRORS, error.message)) return KNOWN_ERRORS[error.message];
  if (lastStage === "runner_apply_entered") return "loader_await_rejected";
  if (lastStage === "loader_ready") return "package_import_rejected";
  return "unclassified_error";
}

export function apply(ctx, config) {
  let lastStage = "runner_apply_entered";
  let terminalWritten = false;
  const lifecycle = { sessionCreated: 0, agentCreated: 0, agentSessionStart: 0 };
  const observed = {
    agentCreateInvocationCount: 0,
    privateAgentPreparationCount: 0,
    privateSessionPreparationCount: 0,
    presetMounted: false,
    modelSelectionInstalled: false,
    vetoExact: false,
    vetoRejected: false,
  };
  let agents;
  let sessions;
  function advance(stage) { lastStage = stage; }
  function emit(result, errorClass) {
    if (terminalWritten) throw new Error("SECOND_TERMINAL_WRITE");
    terminalWritten = true;
    writeExclusive(config.sidecarPath, {
      agent_create_invocation_count: observed.agentCreateInvocationCount,
      agent_created_event_count: lifecycle.agentCreated,
      agent_session_start_event_count: lifecycle.agentSessionStart,
      broker_process_count: 0,
      broker_request_count: 0,
      candidate_source: config.candidateSource,
      database_invocation_count: 0,
      docker_invocation_count: 0,
      effective_tool_guard_sha256: config.guardSha256,
      error_class: errorClass,
      execution_attempt_id: config.executionAttemptId,
      fixed_identity_sha256: digest(PRIVATE_ID),
      last_admitted_stage: lastStage,
      live_agent_count: agents ? agents.list().length : 0,
      live_session_count: sessions ? sessions.list().length : 0,
      model_request_count: 0,
      model_selection_installed: observed.modelSelectionInstalled,
      occupied_worker_count: 0,
      operation_id: config.operationId,
      preset_mounted: observed.presetMounted,
      preset_sha256: config.presetSha256,
      private_agent_preparation_count: observed.privateAgentPreparationCount,
      private_session_preparation_count: observed.privateSessionPreparationCount,
      provider_request_count: 0,
      raw_error_retained: false,
      request_count: 0,
      result,
      runner_sha256: config.runnerSha256,
      schema_version: "ariadne.native_harness_agent_factory_diagnostic_sidecar.v1",
      session_created_event_count: lifecycle.sessionCreated,
      target_created: false,
      target_path_sha256: digest(TARGET_PATH),
      target_used: false,
      turn_count: 0,
      veto_exact: observed.vetoExact,
      veto_rejected: observed.vetoRejected,
    });
  }
  async function run() {
    await ctx.get("loader")?.await();
    advance("loader_ready");
    const agentModule = await import("@deepseek-ai/dsh-agent");
    const sessionModule = await import("@deepseek-ai/dsh-session");
    const guardModule = await import("./effective-tool-guard.mjs");
    const installModelSelection = agentModule.installModelSelection;
    const SessionId = sessionModule.SessionId;
    const assertEffectiveToolComposition = guardModule.assertEffectiveToolComposition;
    if (typeof installModelSelection !== "function" || typeof SessionId !== "function" || typeof assertEffectiveToolComposition !== "function") throw new Error("REQUIRED_SERVICE_MISSING");
    advance("package_imports_admitted");
    agents = ctx.get("agents");
    sessions = ctx.get("sessions");
    const presets = ctx.get("agentPresets");
    if (!agents || !sessions || !presets) throw new Error("REQUIRED_SERVICE_MISSING");
    advance("services_resolved");
    if (!Array.isArray(presets.roots) || presets.roots.length !== 2) throw new Error("PRESET_ROOT_COUNT_MISMATCH");
    if (resolve(presets.roots[0].path) !== resolve(config.shippedRoot) || presets.roots[0].trust !== "system") throw new Error("SHIPPED_ROOT_MISMATCH");
    if (resolve(presets.roots[1].path) !== resolve(config.userRoot) || presets.roots[1].trust !== "user") throw new Error("USER_ROOT_MISMATCH");
    advance("preset_roots_admitted");
    const roster = await presets.resolveMountable(PRESET_ID);
    if (roster.id !== PRESET_ID || roster.trust !== "user" || resolve(roster.path) !== resolve(config.presetPath)) throw new Error("PRESET_ROSTER_MISMATCH");
    advance("preset_roster_admitted");
    requireEmpty(agents, sessions);
    advance("registries_empty_before_factory");
    ctx.on("session/created", () => { lifecycle.sessionCreated += 1; });
    ctx.on("agent/created", () => { lifecycle.agentCreated += 1; });
    ctx.on("agent/session-start", () => { lifecycle.agentSessionStart += 1; });
    const sessionId = SessionId(PRIVATE_ID);
    advance("session_identity_constructed");
    observed.agentCreateInvocationCount = 1;
    advance("agent_factory_invoked");
    try {
      await agents.create({
        sessionId,
        meta: { cwd: process.cwd() },
        agentOptions: { provider: SELECTION.provider, model: SELECTION.model, maxTokens: 4096 },
        setup: async (agentCtx) => {
          advance("factory_setup_entered");
          const privateAgent = agentCtx.agent;
          if (!privateAgent || String(privateAgent.id) !== PRIVATE_ID || String(privateAgent.session.id) !== PRIVATE_ID) throw new Error("PRIVATE_IDENTITY_MISMATCH");
          observed.privateAgentPreparationCount = 1;
          observed.privateSessionPreparationCount = 1;
          if (agents.get(sessionId) !== undefined || sessions.get(sessionId) !== undefined) throw new Error("PRIVATE_OBJECT_PREPUBLISHED");
          advance("private_identity_admitted");
          const composition = await assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS);
          if (composition.coordinate !== "EFFECTIVE_TOOL_COMPOSITION_PASSED" || composition.presetId !== PRESET_ID || JSON.stringify(composition.effectiveToolNames) !== JSON.stringify(TOOLS) || composition.effectiveToolCount !== 3 || presets.composedPreset(agentCtx) !== PRESET_ID) throw new Error("EFFECTIVE_COMPOSITION_MISMATCH");
          observed.presetMounted = true;
          advance("preset_composition_admitted");
          installModelSelection(agentCtx, { current: SELECTION, assembled: undefined });
          observed.modelSelectionInstalled = true;
          advance("model_selection_installed");
          return {
            commit() {
              advance("setup_commit_entered");
              if (String(privateAgent.id) !== PRIVATE_ID || String(privateAgent.session.id) !== PRIVATE_ID) throw new Error("COMMIT_IDENTITY_MISMATCH");
              if (agents.get(sessionId) !== undefined || sessions.get(sessionId) !== undefined) throw new Error("COMMIT_PUBLICATION_EARLY");
              if (!observed.presetMounted || presets.composedPreset(agentCtx) !== PRESET_ID || !observed.modelSelectionInstalled) throw new Error("COMMIT_COMPOSITION_MISMATCH");
              observed.vetoExact = true;
              throw new Error(PUBLICATION_STOP);
            },
          };
        },
      });
      throw new Error("AGENT_CREATE_RESOLVED");
    } catch (error) {
      if (!(error instanceof Error) || error.message !== PUBLICATION_STOP || !observed.vetoExact) throw error;
      observed.vetoRejected = true;
      advance("publication_veto_observed");
    }
    requireEmpty(agents, sessions);
    if (agents.get(sessionId) !== undefined || sessions.get(sessionId) !== undefined) throw new Error("PRIVATE_IDENTITY_RETAINED");
    if (lifecycle.sessionCreated !== 0 || lifecycle.agentCreated !== 0 || lifecycle.agentSessionStart !== 0) throw new Error("LIFECYCLE_EVENT_ESCAPED");
    advance("postrollback_registries_empty");
    if (!isAbsolute(process.cwd())) throw new Error("CWD_NOT_ABSOLUTE");
    emit("prepublication_veto_diagnosed", null);
    ctx.get("appExit")(0);
  }
  run().catch((error) => {
    try { emit("closed_subcoordinate_failure", classify(error, lastStage)); }
    finally { ctx.get("appExit")(2); }
  });
}
'''.encode()


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise ClosedSubcoordinateError("runner_utf8_invalid") from error
    stage_positions = [source.find(f'advance("{stage}")') for stage in STAGES[1:]]
    checks = {
        "only_node_builtins_static": source.count("import {") == 3
        and 'from "node:crypto"' in source
        and 'from "node:fs"' in source
        and 'from "node:path"' in source,
        "package_imports_dynamic": all(
            source.count(token) == 1
            for token in (
                'await import("@deepseek-ai/dsh-agent")',
                'await import("@deepseek-ai/dsh-session")',
                'await import("./effective-tool-guard.mjs")',
            )
        ),
        "one_apply": source.count("export function apply(ctx, config)") == 1,
        "one_factory_invocation": source.count("await agents.create({") == 1,
        "one_exclusive_writer": source.count('openSync(path, "wx")') == 1,
        "sidecar_only_file_write": source.count("openSync(") == 1
        and source.count("writeFileSync(") == 1,
        "one_success_terminal": source.count(
            'emit("prepublication_veto_diagnosed", null)'
        )
        == 1,
        "one_failure_terminal": source.count(
            'emit("closed_subcoordinate_failure", classify(error, lastStage))'
        )
        == 1,
        "finite_stage_order": all(position >= 0 for position in stage_positions)
        and stage_positions == sorted(stage_positions),
        "apply_stage_literal": 'let lastStage = "runner_apply_entered"' in source,
        "finite_error_projection": 'return "unclassified_error"' in source
        and "error.stack" not in source
        and "error.code" not in source
        and "error.cause" not in source
        and "String(error)" not in source,
        "exact_tools": 'Object.freeze(["edit", "glob", "read"])' in source,
        "target_literal_once": source.count(json.dumps(TARGET_PATH)) == 1,
        "no_drive_or_request": all(
            token not in source
            for token in (
                ".followup(",
                "createUserMessage",
                ".whenIdle(",
                'ctx.get("broker")',
                'ctx.get("models")',
                'ctx.get("providers")',
            )
        ),
        "no_retry_resume_fallback": all(
            token not in source.lower() for token in ("retry", "resume", "fallback")
        ),
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise ClosedSubcoordinateError("runner_shape_invalid:" + ",".join(failed))
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), "checks": checks}


def source_payloads(
    contract: dict[str, Any],
) -> tuple[bytes, bytes, bytes, bytes, dict[str, str]]:
    runner = runner_source()
    base_contract = predecessor.load_contract()
    _, helper, guard, sentinel, _ = predecessor.source_payloads(base_contract)
    validate_runner_source(runner)
    observed = {
        "diagnostic_runner_sha256": sha256_bytes(runner),
        "generated_helper_sha256": sha256_bytes(helper),
        "controller_module_sha256": sha256_file(ACCEPTED_CONTROLLER_PATH),
        "effective_tool_guard_sha256": sha256_bytes(guard),
        "readiness_sentinel_sha256": sha256_bytes(sentinel),
    }
    if observed != contract["source_bindings"]:
        raise ClosedSubcoordinateError("source_binding_mismatch")
    return runner, helper, guard, sentinel, observed


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    value = yaml.safe_load(payload)
    if not isinstance(value, list):
        raise ClosedSubcoordinateError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in value:
        if not isinstance(row, dict):
            raise ClosedSubcoordinateError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise ClosedSubcoordinateError("patch_insert_invalid")
            inserted.extend(row["insert"])
        else:
            direct.append(row)
    return direct, inserted


def build_patch_pair(
    *,
    profile_dir: Path,
    readiness_path: Path,
    sidecar_path: Path,
    shipped_root: Path,
    user_root: Path,
    preset_path: Path,
    candidate_source: str,
    source_bindings: dict[str, str],
) -> tuple[bytes, bytes]:
    profile_patch = profile_dir / "cordis.patch.yml"
    home_patch = profile_dir.parents[1] / "cordis.patch.yml"
    common = f"""- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- insert:
    - id: provider-free-rebound-hmr-sentinel
      name: ../../../installation/proof/sentinel.mjs
      config:
        eventPath: {_yaml_path(readiness_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: {PRESET_ID}
        roots:
          - path: {_yaml_path(shipped_root)}
            trust: system
        includeUserRoot: true
"""
    changed = (
        common
        + f"""    - id: provider-free-agent-factory-closed-subcoordinate-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, headlessStartup, agents, sessions, agentPresets]
      config:
        sidecarPath: {_yaml_path(sidecar_path)}
        shippedRoot: {_yaml_path(shipped_root)}
        userRoot: {_yaml_path(user_root)}
        presetPath: {_yaml_path(preset_path)}
        candidateSource: {candidate_source}
        operationId: {OPERATION_ID}
        executionAttemptId: {EXECUTION_ATTEMPT_ID}
        runnerSha256: {source_bindings["diagnostic_runner_sha256"]}
        guardSha256: {source_bindings["effective_tool_guard_sha256"]}
        presetSha256: 3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1
"""
    )
    initial, changed_bytes = common.encode(), changed.encode()
    validate_patch_pair(
        initial,
        changed_bytes,
        sidecar_path=sidecar_path,
        shipped_root=shipped_root,
        user_root=user_root,
        preset_path=preset_path,
        candidate_source=candidate_source,
        source_bindings=source_bindings,
    )
    return initial, changed_bytes


def validate_patch_pair(
    initial: bytes,
    changed: bytes,
    *,
    sidecar_path: Path,
    shipped_root: Path,
    user_root: Path,
    preset_path: Path,
    candidate_source: str,
    source_bindings: dict[str, str],
) -> None:
    initial_direct, initial_inserted = _patch_rows(initial)
    changed_direct, changed_inserted = _patch_rows(changed)
    expected_direct = [
        {"id": "headless-runner", "disabled": True},
        {"id": "code-runtime", "disabled": True},
        {"id": "session-telemetry-otel", "disabled": True},
    ]
    if initial_direct != expected_direct or changed_direct != expected_direct:
        raise ClosedSubcoordinateError("disabled_patch_rows_invalid")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
    ]:
        raise ClosedSubcoordinateError("initial_patch_invalid")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
        "provider-free-agent-factory-closed-subcoordinate-runner",
    ] or changed_inserted[:2] != initial_inserted:
        raise ClosedSubcoordinateError("changed_patch_roster_invalid")
    expected_runner = {
        "id": "provider-free-agent-factory-closed-subcoordinate-runner",
        "name": "../../../installation/proof/runner.mjs",
        "inject": ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"],
        "config": {
            "sidecarPath": str(sidecar_path.resolve()),
            "shippedRoot": str(shipped_root.resolve()),
            "userRoot": str(user_root.resolve()),
            "presetPath": str(preset_path.resolve()),
            "candidateSource": candidate_source,
            "operationId": OPERATION_ID,
            "executionAttemptId": EXECUTION_ATTEMPT_ID,
            "runnerSha256": source_bindings["diagnostic_runner_sha256"],
            "guardSha256": source_bindings["effective_tool_guard_sha256"],
            "presetSha256": "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1",
        },
    }
    if changed_inserted[2] != expected_runner:
        raise ClosedSubcoordinateError("runner_patch_row_invalid")


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    if not _ancestor(contract["planning_source"]):
        raise ClosedSubcoordinateError("planning_source_not_ancestor")
    base_contract = predecessor.load_contract()
    paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "predecessor_contract_sha256": predecessor.CONTRACT_PATH,
        "predecessor_controller_sha256": Path(predecessor.__file__).resolve(),
        "predecessor_closeout_sha256": PREDECESSOR_CLOSEOUT_PATH,
        "predecessor_failure_interpretation_sha256": PREDECESSOR_FAILURE_PATH,
        "predecessor_rejected_claims_sha256": PREDECESSOR_REJECTION_PATH,
    }
    observed = {key: sha256_file(path) for key, path in paths.items()}
    if observed != contract["predecessor_bytes"]:
        raise ClosedSubcoordinateError("predecessor_digest_mismatch")
    if sha256_file(predecessor.CONTRACT_PATH) != contract["base_contract_sha256"]:
        raise ClosedSubcoordinateError("base_contract_binding_mismatch")
    implementation = {
        "execution_controller_sha256": sha256_file(Path(__file__).resolve()),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "contract_schema_sha256": sha256_file(CONTRACT_SCHEMA_PATH),
        "sidecar_schema_sha256": sha256_file(SIDECAR_SCHEMA_PATH),
        "evidence_schema_sha256": sha256_file(EVIDENCE_SCHEMA_PATH),
    }
    if implementation != contract["implementation_bytes"]:
        raise ClosedSubcoordinateError("implementation_digest_mismatch")
    return {
        "base_contract": base_contract,
        "predecessor_sha256": observed,
        "implementation_sha256": implementation,
    }


def read_sidecar(
    path: Path,
    *,
    disposable_root: Path,
    contract: dict[str, Any],
    candidate_source: str,
) -> dict[str, Any]:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise ClosedSubcoordinateError("sidecar_paths_must_be_absolute")
    if disposable_root.is_symlink() or not disposable_root.is_dir() or path.is_symlink():
        raise ClosedSubcoordinateError("sidecar_path_invalid")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(disposable_root.resolve())
    except (OSError, ValueError) as error:
        raise ClosedSubcoordinateError("sidecar_path_outside_disposable_root") from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_SIDECAR_BYTES:
        raise ClosedSubcoordinateError("sidecar_file_invalid")
    try:
        value = json.loads(resolved.read_bytes())
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ClosedSubcoordinateError("sidecar_json_invalid") from error
    schema = json.loads(SIDECAR_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(value)
    fixed = {
        "schema_version": SIDECAR_SCHEMA,
        "operation_id": OPERATION_ID,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "candidate_source": candidate_source,
        "runner_sha256": contract["source_bindings"]["diagnostic_runner_sha256"],
        "effective_tool_guard_sha256": contract["source_bindings"][
            "effective_tool_guard_sha256"
        ],
        "preset_sha256": contract["preset"]["sha256"],
        "fixed_identity_sha256": sha256_bytes(PRIVATE_SESSION_ID.encode()),
        "target_path_sha256": sha256_bytes(TARGET_PATH.encode()),
        "raw_error_retained": False,
        "target_created": False,
        "target_used": False,
        "turn_count": 0,
        "request_count": 0,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "occupied_worker_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
    }
    for key, expected in fixed.items():
        if value[key] != expected:
            raise ClosedSubcoordinateError("sidecar_fixed_binding_mismatch")
    stage_index = STAGES.index(value["last_admitted_stage"])
    expected_invocations = 1 if stage_index >= STAGES.index("agent_factory_invoked") else 0
    expected_private = 1 if stage_index >= STAGES.index("private_identity_admitted") else 0
    if value["agent_create_invocation_count"] != expected_invocations:
        raise ClosedSubcoordinateError("sidecar_factory_count_stage_mismatch")
    if value["private_agent_preparation_count"] != expected_private or value[
        "private_session_preparation_count"
    ] != expected_private:
        raise ClosedSubcoordinateError("sidecar_private_count_stage_mismatch")
    if value["result"] == "prepublication_veto_diagnosed":
        if (
            value["last_admitted_stage"] != "postrollback_registries_empty"
            or value["error_class"] is not None
            or not value["preset_mounted"]
            or not value["model_selection_installed"]
            or not value["veto_exact"]
            or not value["veto_rejected"]
        ):
            raise ClosedSubcoordinateError("sidecar_success_semantics_invalid")
    elif value["result"] == "closed_subcoordinate_failure":
        if value["error_class"] is None:
            raise ClosedSubcoordinateError("sidecar_failure_semantics_invalid")
    else:
        raise ClosedSubcoordinateError("sidecar_runner_terminal_invalid")
    return value


def _safe_sidecar(
    path: Path,
    *,
    disposable_root: Path,
    contract: dict[str, Any],
    candidate_source: str,
) -> tuple[dict[str, Any] | None, bool]:
    try:
        return (
            read_sidecar(
                path,
                disposable_root=disposable_root,
                contract=contract,
                candidate_source=candidate_source,
            ),
            True,
        )
    except (ClosedSubcoordinateError, OSError, jsonschema.ValidationError):
        return None, False


def build_controller_terminal(sidecar: dict[str, Any] | None) -> dict[str, Any]:
    if sidecar is None:
        return {
            "result": "runner_link_or_apply_absence",
            "last_admitted_stage": None,
            "error_class": None,
            "factory_boundary": None,
            "raw_runtime_detail_retained": False,
        }
    return {
        "result": sidecar["result"],
        "last_admitted_stage": sidecar["last_admitted_stage"],
        "error_class": sidecar["error_class"],
        "factory_boundary": {
            key: sidecar[key]
            for key in (
                "agent_create_invocation_count",
                "private_agent_preparation_count",
                "private_session_preparation_count",
                "live_agent_count",
                "live_session_count",
                "session_created_event_count",
                "agent_created_event_count",
                "agent_session_start_event_count",
            )
        },
        "raw_runtime_detail_retained": False,
    }


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessors = validate_predecessors(contract)
    base_contract = predecessors["base_contract"]
    runner, helper, guard, sentinel, bindings = source_payloads(contract)
    preset_payload = predecessor._build_bound_preset_payload(base_contract)
    resolved_cache = (cache_root or predecessor.predecessor._default_cache_root()).resolve()
    _, cached = predecessor.predecessor.verify_cached_packages(
        base_contract, resolved_cache
    )
    seed = predecessor.predecessor._verify_package_seed(base_contract)
    package_root = (
        predecessor.predecessor.PACKAGE_SEED_ROOT
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    )
    package_members = predecessor.verify_package_members(package_root, base_contract)
    root = Path("C:/deterministic/post-hmr-agent-factory-diagnostic").resolve()
    profile = root / "home" / "profiles" / "headless"
    user_root = root / "home" / ".agent-presets"
    shipped_root = (
        root
        / "installation"
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
        / "config"
        / "agent-presets"
    )
    preset_path = user_root / PRESET_ID / "agent.cordis.yml"
    initial, changed = build_patch_pair(
        profile_dir=profile,
        readiness_path=root / "readiness.jsonl",
        sidecar_path=root / "bundle" / "control" / "post-hmr-diagnostic.json",
        shipped_root=shipped_root,
        user_root=user_root,
        preset_path=preset_path,
        candidate_source=_git("rev-parse", "HEAD"),
        source_bindings=bindings,
    )
    return {
        "contract": contract,
        "base_contract": base_contract,
        "predecessors": predecessors,
        "source_bindings": bindings,
        "source_bytes": {
            "runner": len(runner),
            "helper": len(helper),
            "guard": len(guard),
            "sentinel": len(sentinel),
        },
        "runner": validate_runner_source(runner),
        "patch_sha256": {
            "initial": sha256_bytes(initial),
            "changed": sha256_bytes(changed),
        },
        "verified_cached_package_count": len(cached),
        "package_seed": seed,
        "package_source_members": package_members,
        "preset_payload": preset_payload,
        "native_process_count": 0,
    }


def _cleanup_root(root: Path, parent: Path) -> bool:
    if root.parent != parent:
        raise ClosedSubcoordinateError("cleanup_root_escape")
    for attempt in range(26):
        try:
            shutil.rmtree(root)
            return not root.exists()
        except PermissionError:
            if attempt == 25:
                return False
            time.sleep(0.2)
        except OSError:
            return False
    return False


def _controller_failure(
    *,
    process_started: bool,
    exit_code: int | None,
    readiness_valid: bool,
    readiness_events: list[str],
    hmr_mutation_count: int,
    sidecar_file_seen: bool,
    sidecar_valid: bool,
    terminal: dict[str, Any] | None,
    broker_zero: bool,
    network_attempt_count: int,
    network_ledger_valid: bool,
    bundle_unchanged: bool,
    target_absent: bool,
    process_absent: bool,
    root_absent: bool,
) -> str | None:
    if not process_started:
        return "PRELAUNCH_REJECTED"
    if not readiness_valid or readiness_events != [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]:
        return "READINESS_REJECTED"
    if hmr_mutation_count != 1:
        return "HMR_MUTATION_REJECTED"
    if sidecar_file_seen and not sidecar_valid:
        return "TYPED_SIDECAR_REJECTED"
    if terminal is None:
        return "CONTROLLER_TERMINAL_REJECTED"
    expected_exit = 0 if terminal["result"] == "prepublication_veto_diagnosed" else 2
    if exit_code != expected_exit:
        return "PROCESS_EXIT_REJECTED"
    factory = terminal["factory_boundary"]
    if factory is not None and any(
        factory[key] != 0
        for key in (
            "live_agent_count",
            "live_session_count",
            "session_created_event_count",
            "agent_created_event_count",
            "agent_session_start_event_count",
        )
    ):
        return "PUBLICATION_BOUNDARY_REJECTED"
    if not broker_zero:
        return "BROKER_BOUNDARY_REJECTED"
    if not network_ledger_valid or network_attempt_count:
        return "NETWORK_BOUNDARY_REJECTED"
    if not bundle_unchanged:
        return "CANONICAL_BUNDLE_MUTATED"
    if not target_absent:
        return "TARGET_BOUNDARY_REJECTED"
    if not process_absent or not root_absent:
        return "CLEANUP_REJECTED"
    return None


def _render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["controller_terminal"] or {}
    factory = terminal.get("factory_boundary")
    factory_text = "unknown" if factory is None else json.dumps(factory, sort_keys=True)
    return f"""# Native agent-factory closed-subcoordinate diagnostic report

Date: 2026-08-22

Timestamp: {REPORT_TIMESTAMP} (Australia/Brisbane)

Result: **{evidence['result']}**

- Execution attempt: `{evidence['execution_attempt_id']}`
- Full execution source: `{evidence['candidate_source']}`
- Diagnostic terminal: `{terminal.get('result')}`
- Last admitted stage: `{terminal.get('last_admitted_stage')}`
- Error class: `{terminal.get('error_class')}`
- Factory boundary: `{factory_text}`
- Native process / retry: `{evidence['launch']['native_process_count']} / 0`
- Broker / model / provider / network: `0 / 0 / 0 / {evidence['provider_boundary']['network_attempt_count']}`
- Target created or used: `false / false`
- Process and disposable root absent: `{str(evidence['cleanup']['process_absent']).lower()} / {str(evidence['cleanup']['disposable_root_absent']).lower()}`

This is finite provider-free diagnostic evidence. A missing sidecar proves only
runner link/apply absence; it never projects factory counts. No worker turn,
model/provider request, target use, product/data action or production authority
is claimed.
"""


def _efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    terminal = evidence["controller_terminal"] or {}
    return {
        "schema_version": "ariadne.native_harness_agent_factory_diagnostic_efficacy.v1",
        "operation_id": OPERATION_ID,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "candidate_source": evidence["candidate_source"],
        "result": evidence["result"],
        "diagnostic_terminal": terminal.get("result"),
        "last_admitted_stage": terminal.get("last_admitted_stage"),
        "error_class": terminal.get("error_class"),
        "factory_boundary_observed": terminal.get("factory_boundary") is not None,
        "control_gain": (
            "finite_post_hmr_subcoordinate_or_exact_link_apply_absence"
            if evidence["result"] == "pass"
            else "none"
        ),
        "worker_launch_authorized": False,
        "occupied_model_launch_authorized": False,
    }


def execute_rehearsal(cache_root: Path | None = None) -> dict[str, Any]:
    canonical_outputs = (EVIDENCE_PATH, REPORT_PATH, EFFICACY_PATH, ATTEMPT_CONSUMED_PATH)
    if any(path.exists() for path in canonical_outputs):
        raise ClosedSubcoordinateError("canonical_attempt_output_already_exists")
    check = deterministic_check(cache_root)
    contract = check["contract"]
    base_contract = check["base_contract"]
    candidate_source = _git("rev-parse", "HEAD")
    if FULL_OID.fullmatch(candidate_source) is None or not _ancestor(
        contract["planning_source"]
    ):
        raise ClosedSubcoordinateError("execution_candidate_source_invalid")
    if subprocess.run(
        ["git", "diff", "--quiet", "--"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode != 0:
        raise ClosedSubcoordinateError("tracked_worktree_must_be_clean_before_execution")

    identity = base_contract["bundle_identity"]
    runner, helper, guard, sentinel, bindings = source_payloads(contract)
    materialization_bindings = {
        "future_runner_sha256": bindings["diagnostic_runner_sha256"],
        "generated_helper_sha256": bindings["generated_helper_sha256"],
        "controller_module_sha256": bindings["controller_module_sha256"],
    }
    resolved_cache = (cache_root or predecessor.predecessor._default_cache_root()).resolve()
    cache_blob, cached_packages = predecessor.predecessor.verify_cached_packages(
        base_contract, resolved_cache
    )
    parent = predecessor.predecessor.DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise ClosedSubcoordinateError("disposable_parent_missing")
    root = Path(tempfile.mkdtemp(prefix="dsh-agent-factory-diagnostic-", dir=parent)).resolve()
    if root.parent != parent:
        raise ClosedSubcoordinateError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    process_absent = True
    started: float | None = None
    launch_started_utc: str | None = None
    duration_ms: int | None = None
    exit_code: int | None = None
    exit_mode: str | None = None
    removed_environment_names = 0
    hmr_mutation_count = 0
    readiness_records: list[dict[str, Any]] = []
    readiness_valid = False
    sidecar: dict[str, Any] | None = None
    sidecar_valid = False
    sidecar_file_seen = False
    terminal: dict[str, Any] | None = None
    broker_zero = False
    network_attempt_count = 0
    network_ledger_valid = True
    bundle_unchanged = False
    bundle_manifest_before = ""
    bundle_manifest_after = ""
    target_absent = False
    runner_copy_equal = False
    package_identity: dict[str, Any] = {}
    install_projection: dict[str, Any] = {}
    installed_source: dict[str, Any] = {}
    installed_versions: dict[str, str] = {}
    installed_package_members: dict[str, dict[str, Any]] = {}
    initial_patch = b""
    changed_patch = b""
    caught_after_launch = False
    bundle_root: Path | None = None
    sidecar_path: Path | None = None
    broker_path: Path | None = None

    try:
        bundle_parent = root / "bundle"
        bundle_parent.mkdir()
        materialized = rebinding.materialize_rebound_future_attempt(
            disposable_parent=bundle_parent,
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            target_path=base_contract["target_binding"]["relative_path"],
            runner_payload=runner,
            helper_payload=helper,
            controller_payload=ACCEPTED_CONTROLLER_PATH.read_bytes(),
            expected_bindings=materialization_bindings,
        )
        bundle_root = materialized["root"]
        manifest_path = base_bundle._path(bundle_root, base_bundle.BUNDLE_RELATIVE_PATH)
        sidecar_path = base_bundle._path(bundle_root, base_bundle.SIDECAR_RELATIVE_PATH)
        broker_path = base_bundle._path(bundle_root, base_bundle.BROKER_RELATIVE_PATH)
        bundle_manifest_before = sha256_file(manifest_path)
        broker = joined_controller.build_broker_reading(
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
        )
        rebinding.write_broker_fixture(bundle_root, broker)
        target = bundle_root / Path(base_contract["target_binding"]["relative_path"])
        if target.exists() or target.is_symlink():
            raise ClosedSubcoordinateError("target_must_be_absent_prelaunch")

        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        user_root = home / ".agent-presets"
        workspace = root / "workspace"
        proof_dir = root / "installation" / "proof"
        network_guard_path = root / "network-guard.mjs"
        network_path = root / "network.jsonl"
        readiness_path = root / "readiness.jsonl"
        tarball_path = root / "dsh-0.1.0-rc.7.tgz"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        user_root.mkdir()
        predecessor.predecessor._write_exclusive(
            network_guard_path, predecessor.predecessor.network_guard_source()
        )
        predecessor.predecessor._write_exclusive(tarball_path, cache_blob.read_bytes())
        package_identity = predecessor.predecessor.verify_tarball(
            tarball_path, base_contract
        )
        environment, removed_environment_names = (
            predecessor.predecessor.build_child_environment(
                home, network_guard_path, network_path
            )
        )
        package_root, install_projection = predecessor.predecessor._materialize_package_seed(
            root, base_contract
        )
        installed_source = predecessor.predecessor._verify_installed_source(
            package_root, base_contract
        )
        installed_versions = predecessor.predecessor.validate_installed_packages(
            package_root, base_contract
        )
        installed_package_members = predecessor.verify_package_members(
            package_root, base_contract
        )
        shipped_root = package_root / "config" / "agent-presets"

        profile_manifest = {
            "name": "dsh-profile-headless",
            "private": True,
            "dependencies": {},
            "dsh": {
                "profile": {
                    "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
                }
            },
        }
        predecessor.predecessor._write_exclusive(
            profile_dir / "package.json", _canonical(profile_manifest)
        )
        predecessor.predecessor._write_exclusive(
            profile_dir / "pnpm-workspace.yaml",
            b"packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        )
        preset_payload = check["preset_payload"]
        preset_path = user_root / PRESET_ID / "agent.cordis.yml"
        predecessor.predecessor._write_exclusive(preset_path, preset_payload)
        predecessor.predecessor._write_exclusive(proof_dir / "runner.mjs", runner)
        predecessor.predecessor._write_exclusive(
            proof_dir / "effective-tool-guard.mjs", guard
        )
        predecessor.predecessor._write_exclusive(proof_dir / "sentinel.mjs", sentinel)
        runner_copy_equal = (
            sha256_file(proof_dir / "runner.mjs")
            == bindings["diagnostic_runner_sha256"]
        )
        if not runner_copy_equal:
            raise ClosedSubcoordinateError("execution_copy_digest_mismatch")
        initial_patch, changed_patch = build_patch_pair(
            profile_dir=profile_dir,
            readiness_path=readiness_path,
            sidecar_path=sidecar_path,
            shipped_root=shipped_root,
            user_root=user_root,
            preset_path=preset_path,
            candidate_source=candidate_source,
            source_bindings=bindings,
        )
        patch_path = profile_dir / "cordis.patch.yml"
        predecessor.predecessor._write_exclusive(patch_path, initial_patch)
        node = shutil.which("node")
        if node is None:
            raise ClosedSubcoordinateError("node_not_found")
        command = [
            node,
            base_contract["launch"]["node_flag"],
            str(package_root / base_contract["package"]["bin"]),
            *base_contract["launch"]["profile_args"],
            "provider-free agent factory closed subcoordinate diagnostic",
        ]
        _write_exclusive(
            ATTEMPT_CONSUMED_PATH,
            _canonical(
                {
                    "schema_version": "ariadne.native_harness_agent_factory_diagnostic_attempt.v1",
                    "operation_id": OPERATION_ID,
                    "execution_attempt_id": EXECUTION_ATTEMPT_ID,
                    "candidate_source": candidate_source,
                    "state": "consumed",
                    "retry_count": 0,
                    "resume_permitted": False,
                }
            ),
        )
        launch_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        started = time.monotonic()
        process = subprocess.Popen(
            command,
            cwd=workspace,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process_started = True
        deadline = started + float(base_contract["launch"]["timeout_seconds"])
        while True:
            readiness_records = predecessor.predecessor.native_base.parse_readiness(
                readiness_path, base_contract, allow_incomplete=True
            )
            predecessor.predecessor.native_base.validate_readiness_prefix(
                readiness_records, base_contract
            )
            events = [record["event"] for record in readiness_records]
            if events == base_contract["readiness"]["events"] and hmr_mutation_count == 0:
                predecessor.predecessor.atomic_write(patch_path, changed_patch)
                hmr_mutation_count = 1
            if sidecar_path.exists():
                sidecar_file_seen = True
                sidecar, sidecar_valid = _safe_sidecar(
                    sidecar_path,
                    disposable_root=bundle_root,
                    contract=contract,
                    candidate_source=candidate_source,
                )
            if process.poll() is not None:
                exit_mode = (
                    "self_exited_after_typed_sidecar"
                    if sidecar_valid
                    else "self_exited_before_typed_sidecar"
                )
                break
            if time.monotonic() >= deadline:
                exit_mode = "controller_deadline_termination"
                break
            time.sleep(predecessor.predecessor.POLL_SECONDS)
        if process.poll() is None:
            predecessor.predecessor._terminate_process(process)
        exit_code = process.returncode
    except (
        ClosedSubcoordinateError,
        predecessor.AgentCreationBoundaryError,
        predecessor.predecessor.ReboundNativeBootError,
        predecessor.predecessor.ProofError,
        rebinding.FutureAttemptRebindingError,
        subprocess.SubprocessError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ):
        caught_after_launch = process_started
    finally:
        if started is not None:
            duration_ms = round((time.monotonic() - started) * 1000)
        if process is not None:
            predecessor.predecessor._terminate_process(process)
            exit_code = process.returncode
            process_absent = process.poll() is not None
        if bundle_root is not None:
            readiness_records, readiness_valid = predecessor._safe_readiness(
                root / "readiness.jsonl", base_contract
            )
            if sidecar_path is not None and sidecar_path.exists():
                sidecar_file_seen = True
                sidecar, sidecar_valid = _safe_sidecar(
                    sidecar_path,
                    disposable_root=bundle_root,
                    contract=contract,
                    candidate_source=candidate_source,
                )
            try:
                network_attempt_count = len(
                    predecessor.predecessor._network_attempts(root / "network.jsonl")
                )
            except (OSError, ValueError, json.JSONDecodeError):
                network_ledger_valid = False
            manifest_path = base_bundle._path(
                bundle_root, base_bundle.BUNDLE_RELATIVE_PATH
            )
            try:
                bundle_manifest_after = sha256_file(manifest_path)
                bundle_unchanged = (
                    bool(bundle_manifest_before)
                    and bundle_manifest_after == bundle_manifest_before
                )
            except OSError:
                bundle_unchanged = False
            target = bundle_root / Path(base_contract["target_binding"]["relative_path"])
            target_absent = not target.exists() and not target.is_symlink()
            if broker_path is not None:
                try:
                    broker_value = json.loads(broker_path.read_bytes())
                    joined_controller.validate_broker_reading(broker_value)
                    broker_zero = all(
                        broker_value[counter] == 0
                        for counter in joined_controller.BROKER_COUNTERS
                    )
                except (
                    OSError,
                    json.JSONDecodeError,
                    joined_controller.PostHmrControllerError,
                ):
                    broker_zero = False
            terminal = build_controller_terminal(sidecar if sidecar_valid else None)
        root_absent = _cleanup_root(root, parent)

    if not process_started:
        raise ClosedSubcoordinateError("prelaunch_validation_failed")
    readiness_events = [record["event"] for record in readiness_records]
    failure = _controller_failure(
        process_started=process_started,
        exit_code=exit_code,
        readiness_valid=readiness_valid,
        readiness_events=readiness_events,
        hmr_mutation_count=hmr_mutation_count,
        sidecar_file_seen=sidecar_file_seen,
        sidecar_valid=sidecar_valid,
        terminal=terminal,
        broker_zero=broker_zero,
        network_attempt_count=network_attempt_count,
        network_ledger_valid=network_ledger_valid,
        bundle_unchanged=bundle_unchanged,
        target_absent=target_absent,
        process_absent=process_absent,
        root_absent=root_absent,
    )
    if caught_after_launch and failure is None:
        failure = "POSTLAUNCH_CONTROLLER_REJECTED"
    result = "pass" if failure is None else "fail"
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "candidate_source": candidate_source,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "result": result,
        "failure_classification": failure,
        "source_bindings": contract["source_bindings"],
        "package": {
            "name": base_contract["package"]["name"],
            "version": base_contract["package"]["version"],
            "bin": base_contract["package"]["bin"],
            **package_identity,
            "offline_install": install_projection,
            "installed_source": installed_source,
            "installed_versions": installed_versions,
            "installed_package_members": installed_package_members,
            "verified_cached_package_count": len(cached_packages),
        },
        "launch": {
            "started_at_utc": launch_started_utc,
            "duration_ms": duration_ms,
            "native_process_count": 1,
            "retry_count": 0,
            "resume_count": 0,
            "hmr_mutation_count": hmr_mutation_count,
            "exit_code": exit_code,
            "exit_mode": exit_mode,
            "stdout_retained": False,
            "stderr_retained": False,
            "raw_stream_read": False,
        },
        "composition": {
            "initial_patch_sha256": sha256_bytes(initial_patch),
            "changed_patch_sha256": sha256_bytes(changed_patch),
            "runner_copy_equal": runner_copy_equal,
            "bundle_manifest_before_sha256": bundle_manifest_before,
            "bundle_manifest_after_sha256": bundle_manifest_after,
            "bundle_manifest_unchanged": bundle_unchanged,
            "preset": contract["preset"],
        },
        "readiness": {
            "events": readiness_events,
            "valid": readiness_valid,
            "exact_expected_order": readiness_events
            == base_contract["readiness"]["events"],
        },
        "sidecar": sidecar if sidecar_valid else None,
        "controller_terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": network_attempt_count,
            "network_ledger_valid": network_ledger_valid,
            "turn_count": 0,
            "request_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "occupied_worker_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "database_invocation_count": 0,
            "docker_invocation_count": 0,
        },
        "target": {
            "file_created": False,
            "used": False,
            "absent_after_process": target_absent,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_environment_retained": False,
            "raw_logs_retained": False,
            "package_seed_unchanged": True,
        },
    }
    evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    _write_exclusive(EVIDENCE_PATH, _canonical(evidence))
    _write_exclusive(REPORT_PATH, _render_report(evidence).encode())
    _write_exclusive(EFFICACY_PATH, _canonical(_efficacy(evidence)))
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        result = (
            execute_rehearsal(args.cache_root)
            if args.execute
            else deterministic_check(args.cache_root)
        )
    except (
        ClosedSubcoordinateError,
        predecessor.AgentCreationBoundaryError,
        predecessor.predecessor.ReboundNativeBootError,
        predecessor.predecessor.ProofError,
        rebinding.FutureAttemptRebindingError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        yaml.YAMLError,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"status": "failed", "error": type(error).__name__}))
        return 1
    print(
        json.dumps(
            {
                "status": "passed",
                "operation_id": OPERATION_ID,
                "native_process_count": result.get("native_process_count", 1),
                "result": result.get("result", "deterministic_check_passed"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
