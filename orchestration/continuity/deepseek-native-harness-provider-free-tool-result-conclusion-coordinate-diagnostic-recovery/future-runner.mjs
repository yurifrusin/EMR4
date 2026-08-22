import { createHash, randomUUID } from "node:crypto";
import { closeSync, openSync, writeFileSync } from "node:fs";
const TARGET_PATH = "/synthetic/workspace/orchestration/harness_settings/raisa-check-in-rollout-kill-switch.json";
const TOOLS = Object.freeze(["edit", "glob", "read"]);
const SELECTION = Object.freeze({ provider: "deepseek-official", model: "deepseek-v4-flash", reasoningEffort: "high" });
const STAGES = new Set(["loader", "packages", "services", "roots", "factory", "published", "turn", "flush", "terminal"]);
function digest(value) { return "sha256:" + createHash("sha256").update(value).digest("hex"); }
function writeTerminal(path, value) {
  const descriptor = openSync(path, "wx");
  try { writeFileSync(descriptor, JSON.stringify(value) + "\n", "utf8"); }
  finally { closeSync(descriptor); }
}
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
const TOOL_LIFECYCLE_KEYS = Object.freeze(["authoritative_final_result_kind", "conclusion_request_stage", "input_result_kind", "post_execute_decision_kind", "turn_kind"]);
const TOOL_LIFECYCLE_COORDINATES = Object.freeze({
  "success|accept|pre_execute_after_boundary_accept|success_concluding|completed": "edit_success_accept_concluded",
  "success|accept|post_execute_after_decision|success_nonconcluding|error": "edit_success_accept_late_marker",
  "error|accept|pre_execute_after_boundary_accept|error|error": "edit_error_accept_not_concluded",
  "success|block|pre_execute_after_boundary_accept|error|error": "edit_success_blocked_not_concluded",
  "success|failed|pre_execute_after_boundary_accept|error|error": "post_execute_decision_failed_not_concluded",
});
export function classifyToolLifecycle(observation) {
  if (!observation || typeof observation !== "object" || Array.isArray(observation) || JSON.stringify(Object.keys(observation).sort()) !== JSON.stringify(TOOL_LIFECYCLE_KEYS)) throw new Error("TOOL_LIFECYCLE_KEYS_INVALID");
  const key = [observation.input_result_kind, observation.post_execute_decision_kind, observation.conclusion_request_stage, observation.authoritative_final_result_kind, observation.turn_kind].join("|");
  const value = TOOL_LIFECYCLE_COORDINATES[key];
  if (value === undefined) throw new Error("TOOL_LIFECYCLE_COORDINATE_INVALID");
  return value;
}
export function apply(ctx, config) {
  let stage = "loader";
  let written = false;
  const run = async () => {
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
    const sessionText = `session-${randomUUID()}`;
    let observedCalls = 0;
    let conclusionRequestStage = "not_requested";
    let postExecuteInputResultKind = "unobserved";
    let postExecuteDecisionKind = "unobserved";
    let authoritativeFinalResultKind = "unobserved";
    stage = "factory";
    const { agent } = await agents.create({
      sessionId: SessionId(sessionText),
      meta: { cwd: process.cwd() },
      agentOptions: { provider: SELECTION.provider, model: SELECTION.model, maxTokens: 4096 },
      setup: async (agentCtx) => {
        const composition = await assertEffectiveToolComposition(agentCtx, presets, "emr4-bounded-worker", TOOLS);
        if (!composition || composition.coordinate !== "EFFECTIVE_TOOL_COMPOSITION_PASSED" || JSON.stringify(composition.effectiveToolNames) !== JSON.stringify(TOOLS)) throw new Error("EFFECTIVE_COMPOSITION_MISMATCH");
        installModelSelection(agentCtx, { current: SELECTION, assembled: undefined });
        agentCtx.on("tools/pre-execute", async (exec, next) => {
          observedCalls += 1;
          if (observedCalls !== 1 || exec.name !== "edit") return { kind: "deny", reason: "ONE_EDIT_ONLY" };
          const args = exec.arguments;
          if (exec.parent !== undefined || !args || typeof args !== "object" || args.file_path !== TARGET_PATH || args.replace_all === true) return { kind: "deny", reason: "EDIT_BOUNDARY_MISMATCH" };
          exec.concludeTurn();
          conclusionRequestStage = "pre_execute_after_boundary_accept";
          return next();
        });
        agentCtx.on("tools/post-execute", async (exec, result, next) => {
          postExecuteInputResultKind = result.isError === false ? "success" : "error";
          try {
            const decision = await next();
            if (decision.kind !== "accept" && decision.kind !== "block") throw new Error("POST_EXECUTE_DECISION_INVALID");
            postExecuteDecisionKind = decision.kind;
            return decision;
          } catch {
            postExecuteDecisionKind = "failed";
            throw new Error("POST_EXECUTE_DECISION_FAILED");
          }
        });
        agentCtx.on("tools/result", (exec, result) => {
          const args = exec.arguments;
          if (observedCalls === 1 && exec.name === "edit" && exec.parent === undefined && args && typeof args === "object" && args.file_path === TARGET_PATH && args.replace_all !== true) authoritativeFinalResultKind = result.isError === true ? "error" : result.concludesTurn === true ? "success_concluding" : "success_nonconcluding";
        });
      },
    });
    stage = "published";
    if (!agent || agents.get(agent.session.id) === undefined || sessions.get(agent.session.id) === undefined) throw new Error("AGENT_PUBLICATION_MISSING");
    await agent.whenIdle();
    const firstSeq = agent.session.seq;
    stage = "turn";
    agent.followup(createUserMessage({ content: [{ type: "text", text: config.task }], source: { kind: "user" } }));
    await agent.whenIdle();
    stage = "flush";
    await sessions.flush(agent.session);
    const summary = summarize(agent.session.events, firstSeq);
    let toolLifecycleCoordinate = null;
    try { toolLifecycleCoordinate = classifyToolLifecycle({ input_result_kind: postExecuteInputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: conclusionRequestStage, authoritative_final_result_kind: authoritativeFinalResultKind, turn_kind: summary.turn_kind }); } catch {}
    const passed = summary.request_count === 1 && summary.tool_names.length === 1 && summary.tool_names[0] === "edit" && summary.tool_result_count === 1 && summary.turn_kind === "completed" && toolLifecycleCoordinate === "edit_success_accept_concluded";
    stage = "terminal";
    writeTerminal(config.terminalPath, {
      schema_version: "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1", status: passed ? "completed" : "failed", failure_stage: passed ? null : "terminal", session_id_sha256: digest(sessionText), provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, target_path_sha256: digest(TARGET_PATH), tool_lifecycle: { input_result_kind: postExecuteInputResultKind, post_execute_decision_kind: postExecuteDecisionKind, conclusion_request_stage: conclusionRequestStage, authoritative_final_result_kind: authoritativeFinalResultKind, coordinate: toolLifecycleCoordinate }, ...summary,
    });
    written = true;
    ctx.get("appExit")(passed ? 0 : 1);
  };
  run().catch(() => {
    if (!written) {
      const safeStage = STAGES.has(stage) ? stage : "loader";
      writeTerminal(config.terminalPath, { schema_version: "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1", status: "failed", failure_stage: safeStage, session_id_sha256: null, provider: SELECTION.provider, model: SELECTION.model, reasoning_effort: SELECTION.reasoningEffort, allowed_tool_names: TOOLS, target_path_sha256: digest(TARGET_PATH), tool_lifecycle: { input_result_kind: "unobserved", post_execute_decision_kind: "unobserved", conclusion_request_stage: "not_requested", authoritative_final_result_kind: "unobserved", coordinate: null }, request_count: 0, tool_names: [], tool_result_count: 0, turn_kind: null });
    }
    ctx.get("appExit")(1);
  });
}
