import { mountWithSanitizedTerminal } from "./deepseek_native_harness_provider_free_preset_mount_sanitizer_runner_bridge.mjs";

class FixturePresetMountError extends Error {
  constructor(reason) {
    super(`fixture preset failed to mount: ${reason}`);
    this.reason = reason;
  }
}

const agentCtx = Object.freeze({ fixture: true });
const presetId = "emr4-bounded-worker";
const cases = [
  ["success", null],
  [
    "agent_scope_absent",
    new Error(
      "agent-presets: refusing to compose an unscoped context; the scope key is what joins an agent to its preset",
    ),
  ],
  [
    "composition_stamp_unreadable",
    new FixturePresetMountError("composition file is unreadable: fixture.yml"),
  ],
  [
    "row_import_or_apply_rejected",
    new FixturePresetMountError("fixture apply rejected (fixture-row)"),
  ],
  [
    "subtree_publication_absent",
    new FixturePresetMountError(
      "mounted subtree did not publish its entry tree (fixture-tree)",
    ),
  ],
  [
    "row_inactive_after_await",
    new FixturePresetMountError("1 row(s) did not activate:\nfixture (fixture-row)"),
  ],
  [
    "root_service_leak",
    new FixturePresetMountError(
      "row(s) published process-global service(s) [fixture] (fixture-row)",
    ),
  ],
  ["unclassified", new FixturePresetMountError("fixture-unmapped")],
];

const results = [];
for (const [scenario, failure] of cases) {
  const reading = await mountWithSanitizedTerminal({
    mount: async () => {
      if (failure !== null) throw failure;
    },
    agentCtx,
    presetId,
    PresetMountError: FixturePresetMountError,
  });
  results.push({ scenario, passed: reading.passed, terminal: reading.terminal });
}

console.log(JSON.stringify(results));
