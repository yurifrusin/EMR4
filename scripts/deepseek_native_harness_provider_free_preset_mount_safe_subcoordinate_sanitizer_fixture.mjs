import {
  PRESET_MOUNT_SAFE_CODES,
  sanitizePresetMountError,
} from "./deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer.mjs";

class FixturePresetMountError extends Error {
  constructor(presetId, reason, options) {
    super(`agent-presets: preset "${presetId}" failed to mount: ${reason}`, options);
    this.presetId = presetId;
    this.reason = reason;
  }
}

class LookalikePresetMountError extends Error {
  constructor(reason) {
    super("lookalike");
    this.reason = reason;
  }
}

class DerivedPlainError extends Error {}

const syntheticPath = "C:\\authored-synthetic\\emr4-bounded-worker\\cordis.patch.yml";
const hostileDetail = "HOSTILE_FIXTURE_DETAIL_NEVER_RELEASE";
const scopeMessage =
  "agent-presets: refusing to compose an unscoped context; the scope key is what joins an agent to its preset";

const results = [
  sanitizePresetMountError(new Error(scopeMessage), FixturePresetMountError),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `composition file is unreadable: ${syntheticPath}`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `loader entries failed to apply (${syntheticPath})`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `mounted subtree did not publish its entry tree (${syntheticPath})`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `2 row(s) did not activate:\n- edit\n- read (${syntheticPath})`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `row(s) published process-global service(s) [fs] (${syntheticPath})`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError({ message: scopeMessage }, FixturePresetMountError),
  sanitizePresetMountError(
    new Error(`${scopeMessage}${hostileDetail}`),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new DerivedPlainError(scopeMessage),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new LookalikePresetMountError(`composition file is unreadable: ${hostileDetail}`),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError("emr4-bounded-worker", hostileDetail),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `composition file is unreadable? ${hostileDetail}`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError("emr4-bounded-worker", null),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(
    new FixturePresetMountError(
      "emr4-bounded-worker",
      `mounted subtree did not publish its entry tree (${hostileDetail}`,
    ),
    FixturePresetMountError,
  ),
  sanitizePresetMountError(new Error(scopeMessage), null),
];

const expectedCodes = [
  "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
  "PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE",
  "PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED",
  "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
  "PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT",
  "PRESET_MOUNT_ROOT_SERVICE_LEAK",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_UNCLASSIFIED",
  "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
];

const valid =
  PRESET_MOUNT_SAFE_CODES.length === 7 &&
  results.length === expectedCodes.length &&
  results.every(
    (result, index) =>
      Object.keys(result).join(",") === "stage,code,detail" &&
      result.stage === "preset_mount" &&
      result.code === expectedCodes[index] &&
      result.detail === null,
  );

if (!valid) {
  process.exitCode = 2;
} else {
  process.stdout.write(`${JSON.stringify(results)}\n`);
}
