"""Exercise one real rc.7 agent factory transaction and veto publication."""

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
    deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof as native_composition,
)
from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_rebound_future_runner_stock_headless_hmr_boot_proof as predecessor,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-rebound-future-runner-agent-creation-"
    "boundary-rehearsal"
)
EXECUTION_ATTEMPT_ID = "rebound-agent-creation-boundary-attempt-001"
PRIVATE_SESSION_ID = "session-emr4-agent-creation-boundary-001"
PUBLICATION_STOP = "EMR4_AGENT_PUBLICATION_STOP"
PRESET_ID = "emr4-bounded-worker"
EXPECTED_TOOLS = ["edit", "glob", "read"]
TARGET_PATH = "workspace/authored_synthetic_control_probe.py"
SIDECAR_COORDINATE = "agent_create_prepublication_veto_passed"
CONTROLLER_COORDINATE = "post_hmr_agent_create_prepublication_stop"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
SIDECAR_SCHEMA_PATH = OPERATION_ROOT / "agent-created-sidecar.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "native-agent-creation-boundary-evidence.json"
REPORT_PATH = OPERATION_ROOT / "native-agent-creation-boundary-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
ATTEMPT_CONSUMED_PATH = OPERATION_ROOT / "native-attempt-consumed.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_rebound_future_runner_agent_creation_boundary_rehearsal.py"
)
ACCEPTED_CONTROLLER_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_controller.py"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
SIDECAR_SCHEMA = "ariadne.native_harness_agent_creation_boundary_sidecar.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_agent_creation_boundary_evidence.v1"
REPORT_TIMESTAMP = "2026-08-22T02:11:00+10:00"
MAX_SIDECAR_BYTES = 8_192


class AgentCreationBoundaryError(RuntimeError):
    """The native agent-creation boundary did not satisfy its closed contract."""


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
        raise AgentCreationBoundaryError("git_resolution_failed")
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
        != "ariadne.native_harness_agent_creation_boundary_contract.v1"
        or contract["operation_id"] != OPERATION_ID
        or contract["planning_source"]
        != _git("rev-parse", "--verify", f"{contract['planning_source']}^{{commit}}")
        or contract["planning_source"]
        != _git("log", "-1", "--format=%H", "--", plan_relative)
    ):
        raise AgentCreationBoundaryError("contract_identity_or_planning_source_invalid")
    if contract["execution_attempt"] != {
        "attempt_id": EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }:
        raise AgentCreationBoundaryError("one_process_latch_invalid")
    if contract["factory_boundary"] != {
        "private_session_id": PRIVATE_SESSION_ID,
        "publication_stop": PUBLICATION_STOP,
        "agents_create_invocations": 1,
        "private_agent_preparations": 1,
        "private_session_preparations": 1,
        "published_agents": 0,
        "published_sessions": 0,
    }:
        raise AgentCreationBoundaryError("factory_boundary_invalid")
    if contract["selection"] != {
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "max_tokens": 4096,
    }:
        raise AgentCreationBoundaryError("selection_invalid")
    if contract["expected_terminal"] != {
        "coordinate": CONTROLLER_COORDINATE,
        "diagnostic_accepted": True,
        "factory_construction_supported": True,
        "publication_zero": True,
        "broker_zero": True,
        "pre_request_supported": True,
        "occupied_launch_authorized": False,
    }:
        raise AgentCreationBoundaryError("expected_terminal_invalid")
    return contract


def runner_source() -> bytes:
    return r"""import { createHash } from "node:crypto";
import { closeSync, openSync, writeFileSync } from "node:fs";
import { isAbsolute, resolve } from "node:path";
import { installModelSelection } from "@deepseek-ai/dsh-agent";
import { SessionId } from "@deepseek-ai/dsh-session";
import { assertEffectiveToolComposition } from "./effective-tool-guard.mjs";

export const name = "provider-free-agent-creation-boundary-runner";
export const inject = ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"];
const PRIVATE_ID = "session-emr4-agent-creation-boundary-001";
const PRESET_ID = "emr4-bounded-worker";
const PUBLICATION_STOP = "EMR4_AGENT_PUBLICATION_STOP";
const TARGET_PATH = "workspace/authored_synthetic_control_probe.py";
const TOOLS = Object.freeze(["edit", "glob", "read"]);
const SELECTION = Object.freeze({ provider: "deepseek-official", model: "deepseek-v4-flash", reasoningEffort: "high" });

function digest(value) { return createHash("sha256").update(value).digest("hex"); }
function writeSidecar(path, value) {
  const descriptor = openSync(path, "wx");
  try { writeFileSync(descriptor, JSON.stringify(value) + "\n", "utf8"); }
  finally { closeSync(descriptor); }
}
function requireEmpty(agents, sessions) {
  if (agents.list().length !== 0 || sessions.list().length !== 0) throw new Error("LIVE_REGISTRY_NOT_EMPTY");
}

async function run(ctx, config) {
  await ctx.get("loader")?.await();
  const agents = ctx.get("agents");
  const sessions = ctx.get("sessions");
  const presets = ctx.get("agentPresets");
  if (!agents || !sessions || !presets) throw new Error("REQUIRED_SERVICE_MISSING");
  if (!Array.isArray(presets.roots) || presets.roots.length !== 2) throw new Error("PRESET_ROOT_COUNT_MISMATCH");
  if (resolve(presets.roots[0].path) !== resolve(config.shippedRoot) || presets.roots[0].trust !== "system") throw new Error("SHIPPED_ROOT_MISMATCH");
  if (resolve(presets.roots[1].path) !== resolve(config.userRoot) || presets.roots[1].trust !== "user") throw new Error("USER_ROOT_MISMATCH");
  const roster = await presets.resolveMountable(PRESET_ID);
  if (roster.id !== PRESET_ID || roster.trust !== "user" || resolve(roster.path) !== resolve(config.presetPath)) throw new Error("PRESET_ROSTER_MISMATCH");
  requireEmpty(agents, sessions);
  const lifecycle = { sessionCreated: 0, agentCreated: 0, agentSessionStart: 0 };
  ctx.on("session/created", () => { lifecycle.sessionCreated += 1; });
  ctx.on("agent/created", () => { lifecycle.agentCreated += 1; });
  ctx.on("agent/session-start", () => { lifecycle.agentSessionStart += 1; });
  const sessionId = SessionId(PRIVATE_ID);
  let createInvocationCount = 0;
  let privateAgentPreparationCount = 0;
  let privateSessionPreparationCount = 0;
  let setupEntered = false;
  let commitEntered = false;
  let presetMounted = false;
  let modelSelectionConfigured = false;
  let effectiveToolNames = [];
  let effectiveToolCount = 0;
  let vetoExact = false;
  let vetoRejected = false;
  createInvocationCount += 1;
  try {
    await agents.create({
      sessionId,
      meta: { cwd: process.cwd() },
      agentOptions: { provider: SELECTION.provider, model: SELECTION.model, maxTokens: 4096 },
      setup: async (agentCtx) => {
        setupEntered = true;
        const privateAgent = agentCtx.agent;
        if (!privateAgent || String(privateAgent.id) !== PRIVATE_ID || String(privateAgent.session.id) !== PRIVATE_ID) throw new Error("PRIVATE_IDENTITY_MISMATCH");
        privateAgentPreparationCount = 1;
        privateSessionPreparationCount = 1;
        if (agents.get(sessionId) !== undefined || sessions.get(sessionId) !== undefined) throw new Error("PRIVATE_OBJECT_PREPUBLISHED");
        const composition = await assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS);
        if (composition.coordinate !== "EFFECTIVE_TOOL_COMPOSITION_PASSED" || composition.presetId !== PRESET_ID || JSON.stringify(composition.effectiveToolNames) !== JSON.stringify(TOOLS) || composition.effectiveToolCount !== 3 || presets.composedPreset(agentCtx) !== PRESET_ID) throw new Error("EFFECTIVE_COMPOSITION_MISMATCH");
        presetMounted = true;
        effectiveToolNames = [...composition.effectiveToolNames];
        effectiveToolCount = composition.effectiveToolCount;
        installModelSelection(agentCtx, { current: SELECTION, assembled: undefined });
        modelSelectionConfigured = true;
        return {
          commit() {
            commitEntered = true;
            if (String(privateAgent.id) !== PRIVATE_ID || String(privateAgent.session.id) !== PRIVATE_ID) throw new Error("COMMIT_IDENTITY_MISMATCH");
            if (agents.get(sessionId) !== undefined || sessions.get(sessionId) !== undefined) throw new Error("COMMIT_PUBLICATION_EARLY");
            if (!presetMounted || presets.composedPreset(agentCtx) !== PRESET_ID || JSON.stringify(effectiveToolNames) !== JSON.stringify(TOOLS) || effectiveToolCount !== 3 || !modelSelectionConfigured) throw new Error("COMMIT_COMPOSITION_MISMATCH");
            vetoExact = true;
            throw new Error(PUBLICATION_STOP);
          },
        };
      },
    });
    throw new Error("AGENT_CREATE_RESOLVED");
  } catch (error) {
    if (!(error instanceof Error) || error.message !== PUBLICATION_STOP || !vetoExact) throw new Error("PUBLICATION_VETO_MISMATCH");
    vetoRejected = true;
  }
  requireEmpty(agents, sessions);
  if (agents.get(sessionId) !== undefined || sessions.get(sessionId) !== undefined) throw new Error("PRIVATE_IDENTITY_RETAINED");
  if (lifecycle.sessionCreated !== 0 || lifecycle.agentCreated !== 0 || lifecycle.agentSessionStart !== 0) throw new Error("LIFECYCLE_EVENT_ESCAPED");
  if (!isAbsolute(process.cwd())) throw new Error("CWD_NOT_ABSOLUTE");
  writeSidecar(config.sidecarPath, {
    agent_create_invocation_count: createInvocationCount,
    agent_created_event_count: lifecycle.agentCreated,
    agent_session_start_event_count: lifecycle.agentSessionStart,
    app_exit_count: 1,
    broker_process_count: 0,
    broker_request_count: 0,
    candidate_source: config.candidateSource,
    commit_entered: commitEntered,
    coordinate: "agent_create_prepublication_veto_passed",
    cwd_absolute: true,
    database_invocation_count: 0,
    docker_invocation_count: 0,
    effective_tool_count: effectiveToolCount,
    effective_tool_guard_sha256: config.guardSha256,
    effective_tool_names: effectiveToolNames,
    execution_attempt_id: config.executionAttemptId,
    fixed_identity_sha256: digest(PRIVATE_ID),
    live_agent_count: agents.list().length,
    live_session_count: sessions.list().length,
    max_tokens: 4096,
    model: SELECTION.model,
    model_request_count: 0,
    model_selection_configured: modelSelectionConfigured,
    occupied_worker_count: 0,
    operation_id: config.operationId,
    preset_bytes: 158,
    preset_id: PRESET_ID,
    preset_mounted: presetMounted,
    preset_sha256: config.presetSha256,
    preset_trust: roster.trust,
    private_agent_preparation_count: privateAgentPreparationCount,
    private_session_preparation_count: privateSessionPreparationCount,
    provider: SELECTION.provider,
    provider_request_count: 0,
    publication_stop: PUBLICATION_STOP,
    raw_error_retained: false,
    reasoning_effort: SELECTION.reasoningEffort,
    request_count: 0,
    runner_sha256: config.runnerSha256,
    schema_version: "ariadne.native_harness_agent_creation_boundary_sidecar.v1",
    session_created_event_count: lifecycle.sessionCreated,
    setup_entered: setupEntered,
    target_created: false,
    target_path_sha256: digest(TARGET_PATH),
    target_used: false,
    turn_count: 0,
    veto_exact: vetoExact,
    veto_rejected: vetoRejected,
  });
  ctx.get("appExit")(0);
}

export function apply(ctx, config) {
  run(ctx, config).catch(() => { ctx.get("appExit")(2); });
}
""".encode()


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    try:
        source = payload.decode("utf-8")
    except UnicodeError as error:
        raise AgentCreationBoundaryError("runner_utf8_invalid") from error
    positions = [
        source.find("await assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)"),
        source.find("installModelSelection(agentCtx"),
        source.find("commit() {"),
        source.find("throw new Error(PUBLICATION_STOP);"),
        source.find("writeSidecar(config.sidecarPath"),
    ]
    checks = {
        "one_factory_invocation": source.count("await agents.create({") == 1,
        "one_setup": source.count("setup: async (agentCtx) => {") == 1,
        "one_commit": source.count("commit() {") == 1,
        "one_exact_veto_throw": source.count("throw new Error(PUBLICATION_STOP);") == 1,
        "one_success_sidecar": source.count("writeSidecar(config.sidecarPath") == 1,
        "ordered_prepublication_path": positions == sorted(positions)
        and all(position >= 0 for position in positions),
        "exact_tools": 'Object.freeze(["edit", "glob", "read"])' in source,
        "exact_route": all(
            token in source
            for token in (
                'provider: "deepseek-official"',
                'model: "deepseek-v4-flash"',
                'reasoningEffort: "high"',
                "maxTokens: 4096",
            )
        ),
        "registries_checked_before_after": source.count(
            "requireEmpty(agents, sessions);"
        )
        == 2,
        "lifecycle_counters_exact": all(
            source.count(f'ctx.on("{event}"') == 1
            for event in ("session/created", "agent/created", "agent/session-start")
        ),
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
        "no_raw_error_projection": all(
            token not in source
            for token in ("error.stack", "error.code", "error.cause", "String(error)")
        ),
        "target_literal_once": source.count(json.dumps(TARGET_PATH)) == 1,
        "no_retry_resume_fallback": all(
            token not in source.lower() for token in ("retry", "resume", "fallback")
        ),
    }
    if not all(checks.values()):
        failed = sorted(key for key, value in checks.items() if not value)
        raise AgentCreationBoundaryError("runner_shape_invalid:" + ",".join(failed))
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), "checks": checks}


def source_payloads(
    contract: dict[str, Any],
) -> tuple[bytes, bytes, bytes, bytes, dict[str, str]]:
    runner = runner_source()
    predecessor_contract = predecessor.load_contract()
    _, helper, guard, sentinel, _ = predecessor.source_payloads(predecessor_contract)
    validate_runner_source(runner)
    observed = {
        "future_runner_sha256": sha256_bytes(runner),
        "generated_helper_sha256": sha256_bytes(helper),
        "controller_module_sha256": sha256_file(ACCEPTED_CONTROLLER_PATH),
        "effective_tool_guard_sha256": sha256_bytes(guard),
        "readiness_sentinel_sha256": sha256_bytes(sentinel),
    }
    if observed != contract["source_bindings"]:
        raise AgentCreationBoundaryError("source_binding_mismatch")
    return runner, helper, guard, sentinel, observed


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    value = yaml.safe_load(payload)
    if not isinstance(value, list):
        raise AgentCreationBoundaryError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in value:
        if not isinstance(row, dict):
            raise AgentCreationBoundaryError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise AgentCreationBoundaryError("patch_insert_invalid")
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
        + f"""    - id: provider-free-agent-creation-boundary-runner
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
        runnerSha256: {source_bindings["future_runner_sha256"]}
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
        raise AgentCreationBoundaryError("disabled_patch_rows_invalid")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
    ]:
        raise AgentCreationBoundaryError("initial_patch_invalid")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
        "provider-free-agent-creation-boundary-runner",
    ] or changed_inserted[:2] != initial_inserted:
        raise AgentCreationBoundaryError("changed_patch_roster_invalid")
    if changed_inserted[1] != {
        "id": "agent-presets",
        "name": "@deepseek-ai/dsh-agent-presets",
        "config": {
            "default": PRESET_ID,
            "roots": [{"path": str(shipped_root.resolve()), "trust": "system"}],
            "includeUserRoot": True,
        },
    }:
        raise AgentCreationBoundaryError("agent_presets_row_invalid")
    runner = changed_inserted[2]
    if runner != {
        "id": "provider-free-agent-creation-boundary-runner",
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
            "runnerSha256": source_bindings["future_runner_sha256"],
            "guardSha256": source_bindings["effective_tool_guard_sha256"],
            "presetSha256": "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1",
        },
    }:
        raise AgentCreationBoundaryError("runner_patch_row_invalid")


def _package_member_path(package_root: Path, member: str) -> Path:
    prefix = "@deepseek-ai/"
    if not member.startswith(prefix):
        raise AgentCreationBoundaryError("package_member_path_invalid")
    package, *parts = member[len(prefix) :].split("/")
    if not package or not parts or any(part in {"", ".", ".."} for part in parts):
        raise AgentCreationBoundaryError("package_member_path_invalid")
    return package_root.parent / package / Path(*parts)


def verify_package_members(
    package_root: Path, contract: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for member, expected in contract["package_source_members"].items():
        path = _package_member_path(package_root, member)
        package_manifest = path.parents[len(Path(member).parts) - 3] / "package.json"
        if not path.is_file() or path.is_symlink():
            raise AgentCreationBoundaryError("package_member_missing")
        value = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "version": json.loads(package_manifest.read_bytes())["version"],
        }
        if value != expected:
            raise AgentCreationBoundaryError("package_member_binding_mismatch")
        observed[member] = value
    return observed


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    accepted_sources = {
        "planning_source": contract["planning_source"],
        **contract["accepted_sources"],
    }
    if any(not _ancestor(value) for value in accepted_sources.values()):
        raise AgentCreationBoundaryError("accepted_source_missing_or_not_ancestor")
    predecessor_paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_boot_contract_sha256": predecessor.CONTRACT_PATH,
        "accepted_boot_evidence_sha256": predecessor.EVIDENCE_PATH,
        "accepted_boot_controller_sha256": Path(predecessor.__file__).resolve(),
        "accepted_preset_native_terminal_sha256": (
            REPO_ROOT
            / "orchestration"
            / "continuity"
            / "raisa-provider-free-check-in-native-harness-preset-mount-effective-tool-projection-rehearsal"
            / "native-terminal-attempt-003.json"
        ),
    }
    observed = {key: sha256_file(path) for key, path in predecessor_paths.items()}
    if observed != contract["predecessor_bytes"]:
        raise AgentCreationBoundaryError("predecessor_digest_mismatch")
    implementation = {
        "execution_controller_sha256": sha256_file(Path(__file__).resolve()),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "contract_schema_sha256": sha256_file(CONTRACT_SCHEMA_PATH),
        "sidecar_schema_sha256": sha256_file(SIDECAR_SCHEMA_PATH),
        "evidence_schema_sha256": sha256_file(EVIDENCE_SCHEMA_PATH),
    }
    if implementation != contract["implementation_bytes"]:
        raise AgentCreationBoundaryError("implementation_digest_mismatch")
    return {
        "accepted_sources": accepted_sources,
        "predecessor_sha256": observed,
        "implementation_sha256": implementation,
    }


def expected_sidecar(contract: dict[str, Any], candidate_source: str) -> dict[str, Any]:
    selection = contract["selection"]
    return {
        "agent_create_invocation_count": 1,
        "agent_created_event_count": 0,
        "agent_session_start_event_count": 0,
        "app_exit_count": 1,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "candidate_source": candidate_source,
        "commit_entered": True,
        "coordinate": SIDECAR_COORDINATE,
        "cwd_absolute": True,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
        "effective_tool_count": 3,
        "effective_tool_guard_sha256": contract["source_bindings"][
            "effective_tool_guard_sha256"
        ],
        "effective_tool_names": EXPECTED_TOOLS,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "fixed_identity_sha256": sha256_bytes(PRIVATE_SESSION_ID.encode()),
        "live_agent_count": 0,
        "live_session_count": 0,
        "max_tokens": selection["max_tokens"],
        "model": selection["model"],
        "model_request_count": 0,
        "model_selection_configured": True,
        "occupied_worker_count": 0,
        "operation_id": OPERATION_ID,
        "preset_bytes": contract["preset"]["bytes"],
        "preset_id": contract["preset"]["id"],
        "preset_mounted": True,
        "preset_sha256": contract["preset"]["sha256"],
        "preset_trust": contract["preset"]["trust"],
        "private_agent_preparation_count": 1,
        "private_session_preparation_count": 1,
        "provider": selection["provider"],
        "provider_request_count": 0,
        "publication_stop": PUBLICATION_STOP,
        "raw_error_retained": False,
        "reasoning_effort": selection["reasoning_effort"],
        "request_count": 0,
        "runner_sha256": contract["source_bindings"]["future_runner_sha256"],
        "schema_version": SIDECAR_SCHEMA,
        "session_created_event_count": 0,
        "setup_entered": True,
        "target_created": False,
        "target_path_sha256": sha256_bytes(TARGET_PATH.encode()),
        "target_used": False,
        "turn_count": 0,
        "veto_exact": True,
        "veto_rejected": True,
    }


def read_sidecar(
    path: Path,
    *,
    disposable_root: Path,
    contract: dict[str, Any],
    candidate_source: str,
) -> dict[str, Any]:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise AgentCreationBoundaryError("sidecar_paths_must_be_absolute")
    if (
        disposable_root.is_symlink()
        or not disposable_root.is_dir()
        or path.is_symlink()
    ):
        raise AgentCreationBoundaryError("sidecar_path_invalid")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(disposable_root.resolve())
    except (OSError, ValueError) as error:
        raise AgentCreationBoundaryError(
            "sidecar_path_outside_disposable_root"
        ) from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_SIDECAR_BYTES:
        raise AgentCreationBoundaryError("sidecar_file_invalid")
    try:
        value = json.loads(resolved.read_bytes())
    except (UnicodeError, json.JSONDecodeError) as error:
        raise AgentCreationBoundaryError("sidecar_json_invalid") from error
    schema = json.loads(SIDECAR_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(value)
    if value != expected_sidecar(contract, candidate_source):
        raise AgentCreationBoundaryError("sidecar_semantic_mismatch")
    return value


def build_controller_terminal(sidecar: dict[str, Any]) -> dict[str, Any]:
    return {
        "coordinate": CONTROLLER_COORDINATE,
        "diagnostic_accepted": True,
        "factory_construction_supported": True,
        "publication_zero": True,
        "broker_zero": True,
        "pre_request_supported": True,
        "occupied_launch_authorized": False,
        "agent_create_invocation_count": sidecar["agent_create_invocation_count"],
        "private_agent_preparation_count": sidecar["private_agent_preparation_count"],
        "private_session_preparation_count": sidecar[
            "private_session_preparation_count"
        ],
        "live_agent_count": sidecar["live_agent_count"],
        "live_session_count": sidecar["live_session_count"],
        "session_created_event_count": sidecar["session_created_event_count"],
        "agent_created_event_count": sidecar["agent_created_event_count"],
        "agent_session_start_event_count": sidecar["agent_session_start_event_count"],
        "turn_count": sidecar["turn_count"],
        "request_count": sidecar["request_count"],
        "model_request_count": sidecar["model_request_count"],
        "provider_request_count": sidecar["provider_request_count"],
    }


def _safe_readiness(
    path: Path, contract: dict[str, Any]
) -> tuple[list[dict[str, Any]], bool]:
    return predecessor._safe_readiness(path, contract)


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
    except (AgentCreationBoundaryError, OSError, jsonschema.ValidationError):
        return None, False


def _failure_coordinate(
    *,
    process_started: bool,
    exit_code: int | None,
    exit_mode: str | None,
    readiness_valid: bool,
    readiness_events: list[str],
    mutated: bool,
    sidecar: dict[str, Any] | None,
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
    if exit_code != 0 or exit_mode != "self_exited_after_typed_sidecar":
        return "PROCESS_EXIT_REJECTED"
    if not network_ledger_valid or network_attempt_count:
        return "NETWORK_BOUNDARY_REJECTED"
    if not readiness_valid or readiness_events != [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]:
        return "READINESS_REJECTED"
    if not mutated:
        return "HMR_MUTATION_REJECTED"
    if sidecar is None:
        return "TYPED_SIDECAR_REJECTED"
    if terminal is None or terminal["coordinate"] != CONTROLLER_COORDINATE:
        return "CONTROLLER_TERMINAL_REJECTED"
    if not broker_zero:
        return "BROKER_BOUNDARY_REJECTED"
    if not bundle_unchanged:
        return "CANONICAL_BUNDLE_MUTATED"
    if not target_absent:
        return "TARGET_BOUNDARY_REJECTED"
    if not process_absent or not root_absent:
        return "CLEANUP_REJECTED"
    return None


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessors = validate_predecessors(contract)
    runner, helper, guard, sentinel, bindings = source_payloads(contract)
    resolved_cache = (cache_root or predecessor._default_cache_root()).resolve()
    _, cached = predecessor.verify_cached_packages(contract, resolved_cache)
    seed = predecessor._verify_package_seed(contract)
    package_root = (
        predecessor.PACKAGE_SEED_ROOT / "node_modules" / "@deepseek-ai" / "dsh"
    )
    package_members = verify_package_members(package_root, contract)
    root = Path("C:/deterministic/rebound-agent-creation-boundary").resolve()
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
        "native_process_count": 0,
    }


def _render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["controller_terminal"] or {}
    return f"""# Native agent-creation boundary rehearsal report

Date: 2026-08-22

Timestamp: {REPORT_TIMESTAMP} (Australia/Brisbane)

Result: **{evidence["result"]}**

- Execution attempt: `{evidence["execution_attempt_id"]}`
- Full execution source: `{evidence["candidate_source"]}`
- Native process / retry: `{evidence["launch"]["native_process_count"]}` / `{evidence["launch"]["retry_count"]}`
- Factory invocation / private Agent / private Session: `{evidence["factory_boundary"]["agent_create_invocation_count"]}` / `{evidence["factory_boundary"]["private_agent_preparation_count"]}` / `{evidence["factory_boundary"]["private_session_preparation_count"]}`
- Published Agent / Session: `{evidence["factory_boundary"]["live_agent_count"]}` / `{evidence["factory_boundary"]["live_session_count"]}`
- Lifecycle announcements: `{evidence["factory_boundary"]["session_created_event_count"]} / {evidence["factory_boundary"]["agent_created_event_count"]} / {evidence["factory_boundary"]["agent_session_start_event_count"]}`
- Controller coordinate: `{terminal.get("coordinate")}`
- Broker / model / provider / network: `0 / 0 / 0 / {evidence["provider_boundary"]["network_attempt_count"]}`
- Target created or used: `false / false`
- Process absent / disposable root absent: `{str(evidence["cleanup"]["process_absent"]).lower()} / {str(evidence["cleanup"]["disposable_root_absent"]).lower()}`

This proves one pinned local rc.7 factory reached its synchronous unpublished
setup commit with the accepted preset and exact tool projection, then rolled
back under the exact publication veto. It proves no published worker, turn,
model/provider request, target use or product-runtime fitness.
"""


def _efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_agent_creation_boundary_efficacy.v1",
        "operation_id": OPERATION_ID,
        "result": evidence["result"],
        "control_gain": "real_factory_prepublication_commit_is_under_typed_orchestrator_veto",
        "native_process_count": evidence["launch"]["native_process_count"],
        "retry_count": evidence["launch"]["retry_count"],
        "agents_create_invocation_count": evidence["factory_boundary"][
            "agent_create_invocation_count"
        ],
        "published_agent_count": evidence["factory_boundary"]["live_agent_count"],
        "published_session_count": evidence["factory_boundary"]["live_session_count"],
        "model_request_count": evidence["provider_boundary"]["model_request_count"],
        "provider_request_count": evidence["provider_boundary"][
            "provider_request_count"
        ],
        "free_form_finite_control_fields": 0,
        "next_gate": "one_atomic_published_inert_agent_session_pair_only_if_separately_frozen",
    }


def _cleanup_root(root: Path, parent: Path) -> bool:
    if root.parent != parent:
        raise AgentCreationBoundaryError("cleanup_root_escape")
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


def execute_rehearsal(cache_root: Path | None = None) -> dict[str, Any]:
    canonical_outputs = (
        EVIDENCE_PATH,
        REPORT_PATH,
        EFFICACY_PATH,
        ATTEMPT_CONSUMED_PATH,
    )
    if any(path.exists() for path in canonical_outputs):
        raise AgentCreationBoundaryError("canonical_attempt_output_already_exists")
    check = deterministic_check(cache_root)
    contract = check["contract"]
    candidate_source = _git("rev-parse", "HEAD")
    if FULL_OID.fullmatch(candidate_source) is None or not _ancestor(
        contract["planning_source"]
    ):
        raise AgentCreationBoundaryError("execution_candidate_source_invalid")
    if (
        subprocess.run(
            ["git", "diff", "--quiet", "--"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        != 0
    ):
        raise AgentCreationBoundaryError(
            "tracked_worktree_must_be_clean_before_execution"
        )
    identity = contract["bundle_identity"]
    runner, helper, guard, sentinel, bindings = source_payloads(contract)
    materialization_bindings = {
        key: bindings[key]
        for key in (
            "future_runner_sha256",
            "generated_helper_sha256",
            "controller_module_sha256",
        )
    }
    resolved_cache = (cache_root or predecessor._default_cache_root()).resolve()
    cache_blob, cached_packages = predecessor.verify_cached_packages(
        contract, resolved_cache
    )
    parent = predecessor.DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise AgentCreationBoundaryError("disposable_parent_missing")
    root = Path(
        tempfile.mkdtemp(prefix="dsh-agent-create-boundary-", dir=parent)
    ).resolve()
    if root.parent != parent:
        raise AgentCreationBoundaryError("disposable_root_escape")

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
    sidecar_seen = False
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
            target_path=contract["target_binding"]["relative_path"],
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
        target = bundle_root / Path(contract["target_binding"]["relative_path"])
        if target.exists() or target.is_symlink():
            raise AgentCreationBoundaryError("target_must_be_absent_prelaunch")

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
        predecessor._write_exclusive(
            network_guard_path, predecessor.network_guard_source()
        )
        predecessor._write_exclusive(tarball_path, cache_blob.read_bytes())
        package_identity = predecessor.verify_tarball(tarball_path, contract)
        environment, removed_environment_names = predecessor.build_child_environment(
            home, network_guard_path, network_path
        )
        package_root, install_projection = predecessor._materialize_package_seed(
            root, contract
        )
        installed_source = predecessor._verify_installed_source(package_root, contract)
        installed_versions = predecessor.validate_installed_packages(
            package_root, contract
        )
        installed_package_members = verify_package_members(package_root, contract)
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
        predecessor._write_exclusive(
            profile_dir / "package.json", _canonical(profile_manifest)
        )
        predecessor._write_exclusive(
            profile_dir / "pnpm-workspace.yaml",
            b"packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        )
        preset_payload = native_composition.build_preset_source(
            predecessor.load_contract()
        )
        if (
            len(preset_payload) != contract["preset"]["bytes"]
            or sha256_bytes(preset_payload) != contract["preset"]["sha256"]
        ):
            raise AgentCreationBoundaryError("preset_binding_mismatch")
        preset_path = user_root / PRESET_ID / "agent.cordis.yml"
        predecessor._write_exclusive(preset_path, preset_payload)
        predecessor._write_exclusive(proof_dir / "runner.mjs", runner)
        predecessor._write_exclusive(proof_dir / "effective-tool-guard.mjs", guard)
        predecessor._write_exclusive(proof_dir / "sentinel.mjs", sentinel)
        runner_copy_equal = (
            sha256_file(proof_dir / "runner.mjs") == bindings["future_runner_sha256"]
        )
        if not runner_copy_equal:
            raise AgentCreationBoundaryError("execution_copy_digest_mismatch")
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
        predecessor._write_exclusive(patch_path, initial_patch)
        node = shutil.which("node")
        if node is None:
            raise AgentCreationBoundaryError("node_not_found")
        command = [
            node,
            contract["launch"]["node_flag"],
            str(package_root / contract["package"]["bin"]),
            *contract["launch"]["profile_args"],
            "provider-free agent creation prepublication boundary",
        ]
        _write_exclusive(
            ATTEMPT_CONSUMED_PATH,
            _canonical(
                {
                    "schema_version": "ariadne.native_harness_agent_creation_boundary_attempt.v1",
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
        deadline = started + float(contract["launch"]["timeout_seconds"])
        while True:
            readiness_records = predecessor.native_base.parse_readiness(
                readiness_path, contract, allow_incomplete=True
            )
            predecessor.native_base.validate_readiness_prefix(
                readiness_records, contract
            )
            events = [record["event"] for record in readiness_records]
            if events == contract["readiness"]["events"] and hmr_mutation_count == 0:
                predecessor.atomic_write(patch_path, changed_patch)
                hmr_mutation_count = 1
            if sidecar_path.exists():
                sidecar, sidecar_valid = _safe_sidecar(
                    sidecar_path,
                    disposable_root=bundle_root,
                    contract=contract,
                    candidate_source=candidate_source,
                )
                if sidecar_valid:
                    sidecar_seen = True
            if process.poll() is not None:
                exit_mode = (
                    "self_exited_after_typed_sidecar"
                    if sidecar_seen
                    else "self_exited_before_typed_sidecar"
                )
                break
            if time.monotonic() >= deadline:
                exit_mode = "controller_deadline_termination"
                break
            time.sleep(predecessor.POLL_SECONDS)
        if process.poll() is None:
            predecessor._terminate_process(process)
            exit_mode = exit_mode or "controller_terminated_after_typed_sidecar"
        else:
            exit_mode = exit_mode or "self_exited_after_typed_sidecar"
        exit_code = process.returncode
    except (
        AgentCreationBoundaryError,
        predecessor.ReboundNativeBootError,
        predecessor.ProofError,
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
            predecessor._terminate_process(process)
            exit_code = process.returncode
            process_absent = process.poll() is not None
        if bundle_root is not None:
            readiness_records, readiness_valid = _safe_readiness(
                root / "readiness.jsonl", contract
            )
            if sidecar_path is not None:
                sidecar, sidecar_valid = _safe_sidecar(
                    sidecar_path,
                    disposable_root=bundle_root,
                    contract=contract,
                    candidate_source=candidate_source,
                )
            try:
                network_attempt_count = len(
                    predecessor._network_attempts(root / "network.jsonl")
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
            target = bundle_root / Path(contract["target_binding"]["relative_path"])
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
            if sidecar_valid and sidecar is not None and broker_zero:
                terminal = build_controller_terminal(sidecar)
        root_absent = _cleanup_root(root, parent)

    if not process_started:
        raise AgentCreationBoundaryError("prelaunch_validation_failed")
    readiness_events = [record["event"] for record in readiness_records]
    failure = _failure_coordinate(
        process_started=process_started,
        exit_code=exit_code,
        exit_mode=exit_mode,
        readiness_valid=readiness_valid,
        readiness_events=readiness_events,
        mutated=hmr_mutation_count == 1,
        sidecar=sidecar if sidecar_valid else None,
        terminal=terminal,
        broker_zero=broker_zero,
        network_attempt_count=network_attempt_count,
        network_ledger_valid=network_ledger_valid,
        bundle_unchanged=bundle_unchanged,
        target_absent=target_absent,
        process_absent=process_absent,
        root_absent=root_absent,
    )
    if (
        terminal is not None
        and {key: terminal[key] for key in contract["expected_terminal"]}
        != contract["expected_terminal"]
    ):
        failure = "CONTROLLER_TERMINAL_REJECTED"
    if caught_after_launch and failure is None:
        failure = "POSTLAUNCH_CONTROLLER_REJECTED"
    result = "pass" if failure is None else "fail"
    factory = sidecar or {
        "agent_create_invocation_count": 0,
        "private_agent_preparation_count": 0,
        "private_session_preparation_count": 0,
        "live_agent_count": 0,
        "live_session_count": 0,
        "session_created_event_count": 0,
        "agent_created_event_count": 0,
        "agent_session_start_event_count": 0,
    }
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
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
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
            "native_process_count": 1 if process_started else 0,
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
            "effective_tool_names": EXPECTED_TOOLS,
        },
        "readiness": {
            "events": readiness_events,
            "valid": readiness_valid,
            "exact_expected_order": readiness_events == contract["readiness"]["events"],
        },
        "sidecar": sidecar if sidecar_valid else None,
        "factory_boundary": {
            key: factory[key]
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
        "broker_reading": {
            "schema_version": joined_controller.BROKER_SCHEMA_VERSION,
            **{counter: 0 for counter in joined_controller.BROKER_COUNTERS},
            "identity_bound": True,
            "canonical": True,
            "raw_broker_stream_retained": False,
        },
        "controller_terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": network_attempt_count,
            "network_ledger_valid": network_ledger_valid,
            "turn_count": factory.get("turn_count", 0),
            "request_count": factory.get("request_count", 0),
            "broker_process_count": factory.get("broker_process_count", 0),
            "broker_request_count": factory.get("broker_request_count", 0),
            "occupied_worker_count": factory.get("occupied_worker_count", 0),
            "model_request_count": factory.get("model_request_count", 0),
            "provider_request_count": factory.get("provider_request_count", 0),
            "database_invocation_count": factory.get("database_invocation_count", 0),
            "docker_invocation_count": factory.get("docker_invocation_count", 0),
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
    if args.check:
        projection = deterministic_check(args.cache_root)
        print(
            json.dumps(
                {
                    "status": "passed",
                    "execution_attempt_id": EXECUTION_ATTEMPT_ID,
                    "source_bindings": projection["source_bindings"],
                    "native_process_count": 0,
                },
                sort_keys=True,
            )
        )
        return 0
    evidence = execute_rehearsal(args.cache_root)
    print(
        json.dumps(
            {
                "status": evidence["result"],
                "execution_attempt_id": EXECUTION_ATTEMPT_ID,
                "failure_classification": evidence["failure_classification"],
                "controller_coordinate": (evidence["controller_terminal"] or {}).get(
                    "coordinate"
                ),
                "cleanup": evidence["cleanup"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
