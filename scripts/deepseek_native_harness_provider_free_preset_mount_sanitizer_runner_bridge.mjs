import {
  PRESET_MOUNT_SAFE_CODES,
  sanitizePresetMountError,
} from "./deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs";

const SAFE_CODES = new Set(PRESET_MOUNT_SAFE_CODES);

function exactTerminal(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value) &&
    JSON.stringify(Object.keys(value)) === JSON.stringify(["stage", "code", "detail"]) &&
    value.stage === "preset_mount" &&
    SAFE_CODES.has(value.code) &&
    value.detail === null
  );
}

export async function mountWithSanitizedTerminal({
  mount,
  agentCtx,
  presetId,
  PresetMountError,
}) {
  if (
    typeof mount !== "function" ||
    agentCtx === null ||
    (typeof agentCtx !== "object" && typeof agentCtx !== "function") ||
    typeof presetId !== "string" ||
    presetId.length === 0 ||
    typeof PresetMountError !== "function"
  ) {
    throw new Error("PRESET_MOUNT_BRIDGE_INPUT_INVALID");
  }

  try {
    await mount(agentCtx, presetId);
    return Object.freeze({ passed: true, terminal: null });
  } catch (error) {
    const terminal = sanitizePresetMountError(error, PresetMountError);
    if (!exactTerminal(terminal)) {
      throw new Error("PRESET_MOUNT_BRIDGE_TERMINAL_INVALID");
    }
    return Object.freeze({ passed: false, terminal });
  }
}
