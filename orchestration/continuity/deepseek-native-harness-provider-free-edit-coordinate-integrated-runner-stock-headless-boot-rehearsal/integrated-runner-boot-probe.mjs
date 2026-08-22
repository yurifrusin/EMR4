import { closeSync, openSync, writeFileSync } from "node:fs";
import * as integratedRunner from "./integrated-future-runner.mjs";

export const name = "provider-free-integrated-runner-boot-probe";
export const inject = ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"];

const EXPECTED_EXPORTS = Object.freeze([
  "apply",
  "classifyEditArgumentResult",
  "classifyToolLifecycle",
  "preflightEditArguments",
]);

function writeControlLoad(path) {
  const descriptor = openSync(path, "wx");
  try {
    writeFileSync(
      descriptor,
      JSON.stringify({
        schema_version: "ariadne.native_harness_integrated_edit_controls_loaded.v1",
        coordinate: "integrated_edit_controls_loaded",
        exports: EXPECTED_EXPORTS,
        apply_loaded: true,
        preflight_edit_arguments_loaded: true,
        classify_edit_argument_result_loaded: true,
      }) + "\n",
      "utf8",
    );
  } finally {
    closeSync(descriptor);
  }
}

export function apply(ctx, config) {
  if (
    JSON.stringify(Object.keys(integratedRunner).sort()) !== JSON.stringify(EXPECTED_EXPORTS) ||
    !EXPECTED_EXPORTS.every((key) => typeof integratedRunner[key] === "function")
  ) {
    throw new Error("INTEGRATED_RUNNER_EXPORT_SURFACE_INVALID");
  }
  writeControlLoad(config.controlLoadPath);
  return integratedRunner.apply(ctx, config);
}
