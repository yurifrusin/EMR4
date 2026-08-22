import { closeSync, openSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { Context } from "@deepseek-ai/cordis";
import { AgentRegistry } from "@deepseek-ai/dsh-agent";
import { createScope } from "@deepseek-ai/dsh-scope";
import { apply as applyRunner } from "./integrated-runner.mjs";

export const name = "provider-free-accepted-guard-graph-stock-headless-boot-probe";
export const inject = ["hmr", "headlessStartup"];

const SUCCESS_COORDINATE = "EFFECTIVE_TOOL_COMPOSITION_PASSED";
const PASS_RESULT = "stock_headless_handed_off_to_accepted_guard_graph_runner";
const OLD_COORDINATE = "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID";

function writeExclusive(path, value) {
  const descriptor = openSync(path, "wx");
  try {
    writeFileSync(descriptor, JSON.stringify(value) + "\n", "utf8");
  } finally {
    closeSync(descriptor);
  }
}

export async function apply(ctx, config) {
  const hmr = ctx.get("hmr");
  const stockExit = ctx.get("appExit");
  if (hmr === undefined || !(hmr.configs instanceof Map)) {
    throw new Error("BOOT_PROBE_REQUIRES_ACTIVE_HMR");
  }
  if (typeof stockExit !== "function") {
    throw new Error("BOOT_PROBE_REQUIRES_STOCK_APP_EXIT");
  }
  const observedWatches = new Set(
    [...hmr.configs.keys()].map((value) => resolve(value).toLowerCase()),
  );
  const expectedWatches = config.watchedPaths.map((value) => resolve(value).toLowerCase());
  if (!expectedWatches.every((value) => observedWatches.has(value))) {
    throw new Error("BOOT_PROBE_REQUIRES_BOTH_STOCK_PATCH_WATCHES");
  }

  const toolNames = Object.freeze(["edit", "glob", "read"]);
  const scopeKey = Object.freeze({ fixture: "accepted-guard-graph-stock-headless-boot" });
  let factoryCreateAgentInvocations = 0;
  let setupInvocations = 0;
  let setupResolved = false;
  let structuredCoordinate = null;
  let presetRootReads = 0;
  let presetMountReads = 0;
  let presetMountCalls = 0;
  let toolViewCalls = 0;
  let toolRestrictCalls = 0;
  let toolSchemaCalls = 0;
  let hookInstallations = 0;
  let scopeDisposals = 0;
  let localAppExitCalls = 0;
  let localAppExitCode = null;
  let exitResolve;
  const exitSeen = new Promise((resolveExit) => { exitResolve = resolveExit; });
  const localCtx = new Context();
  const agents = new AgentRegistry(localCtx);
  const sessions = {
    get() { return undefined; },
    list() { return []; },
    async flush() { throw new Error("FLUSH_FORBIDDEN"); },
  };
  const roots = Object.freeze([
    Object.freeze({ trust: "system" }),
    Object.freeze({ trust: "user" }),
  ]);
  const presetService = new Proxy({
    roots,
    async mount(agentCtx, presetId) {
      presetMountCalls += 1;
      if (this !== presetService || presetId !== "emr4-bounded-worker" || agentCtx === null) {
        throw new Error("BOOT_PROBE_MOUNT_BINDING_MISMATCH");
      }
    },
  }, {
    get(target, property, receiver) {
      if (property === "roots") presetRootReads += 1;
      if (property === "mount") presetMountReads += 1;
      return Reflect.get(target, property, receiver);
    },
  });
  localCtx.provide("loader", { async await() {} });
  localCtx.provide("sessions", sessions);
  localCtx.provide("agentPresets", presetService);
  localCtx.provide("appExit", (code) => {
    localAppExitCalls += 1;
    localAppExitCode = code;
    exitResolve(code);
  });
  agents.setFactory({
    async createAgent(ownerCtx, options) {
      factoryCreateAgentInvocations += 1;
      const scoped = createScope(ownerCtx, scopeKey);
      const tools = {
        restricted: false,
        view(observedScope) {
          toolViewCalls += 1;
          if (observedScope !== scopeKey) throw new Error("BOOT_PROBE_SCOPE_MISMATCH");
          return Object.freeze({ knownNames: toolNames, restrictableNames: toolNames });
        },
        restrict(value) {
          toolRestrictCalls += 1;
          if (JSON.stringify(value) !== JSON.stringify({ allow: toolNames })) {
            throw new Error("BOOT_PROBE_RESTRICTION_MISMATCH");
          }
          this.restricted = true;
        },
        schemas(observedScope) {
          toolSchemaCalls += 1;
          if (observedScope !== scopeKey || this.restricted !== true) {
            throw new Error("BOOT_PROBE_SCHEMA_VIEW_MISMATCH");
          }
          return toolNames.map((toolName) => Object.freeze({ name: toolName }));
        },
      };
      const agentCtx = new Proxy(scoped.ctx, {
        get(target, property, receiver) {
          if (property === "tools") return tools;
          if (property === "on") {
            return (...args) => {
              hookInstallations += 1;
              return target.on(...args);
            };
          }
          return Reflect.get(target, property, receiver);
        },
      });
      setupInvocations += 1;
      try {
        await options.setup(agentCtx);
        setupResolved = true;
        structuredCoordinate = SUCCESS_COORDINATE;
        throw new Error("CONTROLLED_POST_GUARD_SENTINEL");
      } finally {
        await scoped.dispose();
        scopeDisposals += 1;
      }
    },
    async resume() { throw new Error("RESUME_FORBIDDEN"); },
  });

  applyRunner(localCtx, {
    terminalPath: config.terminalPath,
    task: "provider-free accepted guard graph stock-headless boot",
  });
  await Promise.race([
    exitSeen,
    new Promise((_, reject) => setTimeout(() => reject(new Error("BOOT_PROBE_TIMEOUT")), 5000)),
  ]);
  const terminal = JSON.parse(readFileSync(config.terminalPath, "utf8"));
  const liveAgentCount = agents.list().length;
  await localCtx.fiber.dispose();
  const result = {
    schema_version: "ariadne.native_harness_stock_headless_custom_runner_observation.v1",
    result: structuredCoordinate === SUCCESS_COORDINATE ? PASS_RESULT : "boot_probe_result_rejected",
    structured_coordinate: structuredCoordinate,
    old_input_invalid_observed: structuredCoordinate === OLD_COORDINATE,
    distinct_preset_root_count: roots.length,
    factory_create_agent_invocations: factoryCreateAgentInvocations,
    setup_invocations: setupInvocations,
    setup_resolved: setupResolved,
    preset_root_reads: presetRootReads,
    preset_mount_reads: presetMountReads,
    preset_mount_calls: presetMountCalls,
    tool_view_calls: toolViewCalls,
    tool_restrict_calls: toolRestrictCalls,
    tool_schema_calls: toolSchemaCalls,
    hook_installations: hookInstallations,
    scope_disposals: scopeDisposals,
    runner_app_exit_code: localAppExitCalls === 1 ? localAppExitCode : null,
    runner_status: terminal.status,
    runner_failure_stage: terminal.failure_stage,
    runner_request_count: terminal.request_count,
    runner_tool_result_count: terminal.tool_result_count,
    runner_turn_kind: terminal.turn_kind,
    runner_conclusion_marked: terminal.conclusion_marked,
    live_agent_count: liveAgentCount,
    raw_error_retained: false,
    cordis_disposed: true,
    stock_app_exit_requested: true,
  };
  writeExclusive(config.observationPath, result);
  stockExit(0);
}
