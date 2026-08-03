/**
 * Default-off native-Diary composition for one trusted application-session
 * practitioner-directory read.
 *
 * The injected reader owns all HTTP, cookie, origin, CSRF, authentication,
 * authorization and audit details. This module passes it no arguments and
 * accepts no caller-selected practice, principal, role, policy, action,
 * resource, query or field selection. The accepted reconciler is the only row
 * egress. Client generation is suppression metadata, never authority.
 */

import {
  createNativeDiaryClientReconciler,
} from './application-session-practitioner-reconciler.mjs';

export const APPLICATION_SESSION_PRACTITIONER_BOOTSTRAP_GLOBAL =
  '__EMR4_NATIVE_DIARY_APPLICATION_SESSION_PRACTITIONERS__';

const BOOTSTRAP_KEYS = Object.freeze([
  'enabled',
  'readFixedPractitionerDirectory',
  'sessionGeneration',
]);

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function hasExactKeys(value, expected) {
  const keys = Object.keys(value);
  return keys.length === expected.length && expected.every((key) => keys.includes(key));
}

/**
 * Only an exact boolean true opts into the application-session path. Missing,
 * false, non-object and non-boolean values are feature-off states.
 */
export function isApplicationSessionPractitionerDirectoryEnabled(bootstrap) {
  return isPlainObject(bootstrap) && bootstrap.enabled === true;
}

export function assertApplicationSessionPractitionerBootstrap(bootstrap) {
  if (!isApplicationSessionPractitionerDirectoryEnabled(bootstrap)) {
    throw new Error('application_session_practitioner_directory_not_enabled');
  }
  if (
    !hasExactKeys(bootstrap, BOOTSTRAP_KEYS)
    || typeof bootstrap.readFixedPractitionerDirectory !== 'function'
    || !Number.isSafeInteger(bootstrap.sessionGeneration)
    || bootstrap.sessionGeneration <= 0
  ) {
    throw new Error('application_session_practitioner_directory_bootstrap_invalid');
  }
  return true;
}

/**
 * Create one long-lived, provider-free composition around one fixed reader.
 * Enabled but incomplete or authority-bearing bootstrap objects fail closed
 * before the reader can be invoked.
 */
export function createApplicationSessionPractitionerDirectory(bootstrap) {
  assertApplicationSessionPractitionerBootstrap(bootstrap);

  const readFixedPractitionerDirectory = bootstrap.readFixedPractitionerDirectory;
  const reconciler = createNativeDiaryClientReconciler({
    initialSessionGeneration: bootstrap.sessionGeneration,
  });

  async function readAndRender(synchronousRender) {
    if (typeof synchronousRender !== 'function') {
      throw new Error('synchronous_render_required');
    }
    const ticket = reconciler.beginRead();
    let returnedResult;
    try {
      returnedResult = await readFixedPractitionerDirectory();
    } catch (_error) {
      reconciler.reconcileAndRender(ticket, undefined, () => {});
      return Object.freeze({ ok: false, reason: 'fixed_read_failed' });
    }
    return Object.freeze(
      reconciler.reconcileAndRender(ticket, returnedResult, synchronousRender),
    );
  }

  function invalidateSession() {
    reconciler.invalidateSession();
  }

  function advanceSessionGeneration(newGeneration) {
    return reconciler.advanceSessionGeneration(newGeneration);
  }

  function snapshot() {
    const current = reconciler.snapshot();
    return Object.freeze({
      ...current,
      rejectionCounts: Object.freeze({ ...current.rejectionCounts }),
    });
  }

  return Object.freeze({
    readAndRender,
    invalidateSession,
    advanceSessionGeneration,
    snapshot,
  });
}
