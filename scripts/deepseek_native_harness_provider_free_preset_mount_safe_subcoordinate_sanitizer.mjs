const CODES = Object.freeze({
  agentScopeAbsent: "PRESET_MOUNT_AGENT_SCOPE_ABSENT",
  compositionStampUnreadable: "PRESET_MOUNT_COMPOSITION_STAMP_UNREADABLE",
  rowImportOrApplyRejected: "PRESET_MOUNT_ROW_IMPORT_OR_APPLY_REJECTED",
  subtreePublicationAbsent: "PRESET_MOUNT_SUBTREE_PUBLICATION_ABSENT",
  rowInactiveAfterAwait: "PRESET_MOUNT_ROW_INACTIVE_AFTER_AWAIT",
  rootServiceLeak: "PRESET_MOUNT_ROOT_SERVICE_LEAK",
  unclassified: "PRESET_MOUNT_UNCLASSIFIED",
});

const AGENT_SCOPE_MESSAGE =
  "agent-presets: refusing to compose an unscoped context; the scope key is what joins an agent to its preset";
const STAMP_PREFIX = "composition file is unreadable: ";
const SUBTREE_PREFIX = "mounted subtree did not publish its entry tree (";
const INACTIVE_PATTERN = /^[1-9][0-9]* row\(s\) did not activate:\n[\s\S]+ \([^\r\n]+\)$/;
const ROOT_LEAK_PREFIX = "row(s) published process-global service(s) [";
const MOUNT_WRAPPER_PATTERN = /^[\s\S]+ \([^\r\n]+\)$/;

function terminal(code) {
  return Object.freeze({ stage: "preset_mount", code, detail: null });
}

function isExactPlainError(value) {
  return value instanceof Error && value.constructor === Error;
}

function isExactPresetMountError(value, PresetMountError) {
  return (
    typeof PresetMountError === "function" &&
    value instanceof PresetMountError &&
    value.constructor === PresetMountError &&
    typeof value.reason === "string"
  );
}

export function sanitizePresetMountError(error, PresetMountError) {
  if (isExactPlainError(error) && error.message === AGENT_SCOPE_MESSAGE) {
    return terminal(CODES.agentScopeAbsent);
  }

  if (!isExactPresetMountError(error, PresetMountError)) {
    return terminal(CODES.unclassified);
  }

  const reason = error.reason;
  if (reason.startsWith(STAMP_PREFIX) && reason.length > STAMP_PREFIX.length) {
    return terminal(CODES.compositionStampUnreadable);
  }
  if (reason.startsWith(SUBTREE_PREFIX) && reason.endsWith(")")) {
    return terminal(CODES.subtreePublicationAbsent);
  }
  if (INACTIVE_PATTERN.test(reason)) {
    return terminal(CODES.rowInactiveAfterAwait);
  }
  if (reason.startsWith(ROOT_LEAK_PREFIX) && reason.endsWith(")")) {
    return terminal(CODES.rootServiceLeak);
  }
  if (MOUNT_WRAPPER_PATTERN.test(reason)) {
    return terminal(CODES.rowImportOrApplyRejected);
  }
  return terminal(CODES.unclassified);
}

export const PRESET_MOUNT_SAFE_CODES = Object.freeze(Object.values(CODES));
