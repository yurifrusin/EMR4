/**
 * Default-off Rayleen waiting-room read reconciler.
 *
 * Trusted composition owns the fixed GraphQL transport. This module owns only
 * closed response admission and latest-read-wins lifecycle suppression. It has
 * no DOM, storage, fetch, provider, command, write, event, or audit capability.
 */

export const RAYLEEN_WAITING_ROOM_BOOTSTRAP_GLOBAL =
  '__EMR4_RAYLEEN_WAITING_ROOM__';

const BOOTSTRAP_KEYS = Object.freeze([
  'enabled',
  'practiceId',
  'readFixedWaitingRoom',
  'sessionGeneration',
]);
const REQUEST_KEYS = Object.freeze([
  'locationId',
  'projectionKind',
  'practitionerId',
  'waitingAreaId',
  'focusAppointmentId',
]);
const FRAME_KEYS = Object.freeze([
  'schemaVersion',
  'frameId',
  'practiceId',
  'locationId',
  'contextRevision',
  'generatedAt',
  'expiresAt',
  'reader',
  'excludedFieldClasses',
  'projection',
  'backendFacts',
  'derivedSignals',
]);
const PROJECTION_KEYS = Object.freeze([
  'kind',
  'selectedCount',
  'practitionerId',
  'waitingAreaId',
  'focusAppointmentId',
  'selectorProvenance',
  'authorityCeiling',
  'writesAuthorized',
]);
const FACT_KEYS = Object.freeze([
  'appointmentId',
  'patientDisplayToken',
  'practitionerId',
  'status',
  'scheduledAt',
  'waitingAreaId',
  'arrivedAt',
  'label',
]);
const SIGNAL_KEYS = Object.freeze([
  'kind',
  'appointmentId',
  'integerValue',
  'textValue',
  'booleanValue',
  'derivedBy',
  'label',
]);
const LABEL_KEYS = Object.freeze([
  'sourceIds',
  'integrityPrincipals',
  'confidentialityReaders',
  'observedAt',
  'expiresAt',
  'freshnessState',
  'authorityCeiling',
]);
const PROJECTION_KINDS = Object.freeze([
  'FULL_QUEUE',
  'PRACTITIONER_GROUP',
  'WAITING_AREA_GROUP',
  'LONGEST_WAIT',
]);
const STATUS_VALUES = Object.freeze([
  'booked',
  'confirmed',
  'arrived',
  'in_consult',
]);
const SIGNAL_KINDS = Object.freeze([
  'elapsed_wait_minutes',
  'threshold_band',
  'longest_wait_rank',
  'flow_exception',
]);
const SELECTOR_PROVENANCE = Object.freeze([
  'deterministic_product_read',
  'model_selected_proofreader_admitted',
]);
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function hasExactKeys(value, expected) {
  if (!isPlainObject(value)) return false;
  const keys = Object.keys(value);
  return keys.length === expected.length && expected.every((key) => keys.includes(key));
}

function isNonEmptyString(value) {
  return typeof value === 'string' && value.length > 0;
}

function isUuid(value) {
  return typeof value === 'string' && UUID_PATTERN.test(value);
}

function isNullableUuid(value) {
  return value === null || isUuid(value);
}

function isDateTime(value) {
  return isNonEmptyString(value) && Number.isFinite(Date.parse(value));
}

function isStringArray(value, { nonEmpty = false } = {}) {
  return Array.isArray(value)
    && (!nonEmpty || value.length > 0)
    && value.every(isNonEmptyString);
}

function admitLabel(label) {
  return hasExactKeys(label, LABEL_KEYS)
    && isStringArray(label.sourceIds, { nonEmpty: true })
    && label.sourceIds.every((value) => value.startsWith('backend:appointment:'))
    && isStringArray(label.integrityPrincipals, { nonEmpty: true })
    && label.integrityPrincipals.every((value) => value === 'backend_truth')
    && isStringArray(label.confidentialityReaders, { nonEmpty: true })
    && label.confidentialityReaders.every(
      (value) => value === 'authorized_reception_surface',
    )
    && isDateTime(label.observedAt)
    && isDateTime(label.expiresAt)
    && label.freshnessState === 'fresh'
    && label.authorityCeiling === 'data_only';
}

function admitFact(fact) {
  return hasExactKeys(fact, FACT_KEYS)
    && isUuid(fact.appointmentId)
    && /^synthetic:patient-[0-9a-f]{12}$/i.test(fact.patientDisplayToken)
    && isUuid(fact.practitionerId)
    && STATUS_VALUES.includes(fact.status)
    && isDateTime(fact.scheduledAt)
    && isNullableUuid(fact.waitingAreaId)
    && (fact.arrivedAt === null || isDateTime(fact.arrivedAt))
    && admitLabel(fact.label);
}

function signalValueCount(signal) {
  return [signal.integerValue, signal.textValue, signal.booleanValue]
    .filter((value) => value !== null).length;
}

function admitSignal(signal, factIds) {
  if (
    !hasExactKeys(signal, SIGNAL_KEYS)
    || !SIGNAL_KINDS.includes(signal.kind)
    || !isUuid(signal.appointmentId)
    || !factIds.has(signal.appointmentId)
    || signal.derivedBy !== 'deterministic_projection_engine'
    || !admitLabel(signal.label)
    || signalValueCount(signal) !== 1
  ) {
    return false;
  }
  if (signal.kind === 'elapsed_wait_minutes' || signal.kind === 'longest_wait_rank') {
    return Number.isSafeInteger(signal.integerValue) && signal.integerValue >= 0;
  }
  if (signal.kind === 'threshold_band' || signal.kind === 'flow_exception') {
    return isNonEmptyString(signal.textValue);
  }
  return false;
}

function admitProjection(projection, facts) {
  if (
    !hasExactKeys(projection, PROJECTION_KEYS)
    || !PROJECTION_KINDS.includes(projection.kind)
    || !Number.isSafeInteger(projection.selectedCount)
    || projection.selectedCount !== facts.length
    || !isNullableUuid(projection.practitionerId)
    || !isNullableUuid(projection.waitingAreaId)
    || !isNullableUuid(projection.focusAppointmentId)
    || !SELECTOR_PROVENANCE.includes(projection.selectorProvenance)
    || projection.authorityCeiling !== 'data_only'
    || projection.writesAuthorized !== false
  ) {
    return false;
  }
  const factIds = new Set(facts.map((fact) => fact.appointmentId));
  const practitionerIds = new Set(facts.map((fact) => fact.practitionerId));
  const waitingAreaIds = new Set(
    facts.map((fact) => fact.waitingAreaId).filter((value) => value !== null),
  );
  if (projection.focusAppointmentId !== null && !factIds.has(projection.focusAppointmentId)) {
    return false;
  }
  if (
    projection.kind === 'PRACTITIONER_GROUP'
    && (
      projection.practitionerId === null
      || !practitionerIds.has(projection.practitionerId)
      || facts.some((fact) => fact.practitionerId !== projection.practitionerId)
    )
  ) {
    return false;
  }
  if (
    projection.kind === 'WAITING_AREA_GROUP'
    && (
      projection.waitingAreaId === null
      || !waitingAreaIds.has(projection.waitingAreaId)
      || facts.some((fact) => fact.waitingAreaId !== projection.waitingAreaId)
    )
  ) {
    return false;
  }
  return true;
}

function freezeFrame(frame) {
  frame.backendFacts.forEach((fact) => {
    Object.freeze(fact.label.sourceIds);
    Object.freeze(fact.label.integrityPrincipals);
    Object.freeze(fact.label.confidentialityReaders);
    Object.freeze(fact.label);
    Object.freeze(fact);
  });
  frame.derivedSignals.forEach((signal) => {
    Object.freeze(signal.label.sourceIds);
    Object.freeze(signal.label.integrityPrincipals);
    Object.freeze(signal.label.confidentialityReaders);
    Object.freeze(signal.label);
    Object.freeze(signal);
  });
  Object.freeze(frame.excludedFieldClasses);
  Object.freeze(frame.backendFacts);
  Object.freeze(frame.derivedSignals);
  Object.freeze(frame.projection);
  return Object.freeze(frame);
}

/** Strictly admit one fixed GraphQL response and release only its closed frame. */
export function admitRayleenWaitingRoomResponse(
  response,
  { expectedLocationId, expectedPracticeId, now = Date.now() } = {},
) {
  if (!hasExactKeys(response, ['data']) || !hasExactKeys(response.data, ['rayleenWaitingRoom'])) {
    return Object.freeze({ ok: false, reason: 'response_not_admissible' });
  }
  const frame = response.data.rayleenWaitingRoom;
  if (
    !hasExactKeys(frame, FRAME_KEYS)
    || frame.schemaVersion !== 'emr4.waiting_room_context_frame.v1'
    || !isUuid(frame.frameId)
    || !isUuid(frame.practiceId)
    || frame.practiceId !== expectedPracticeId
    || !isUuid(frame.locationId)
    || frame.locationId !== expectedLocationId
    || !Number.isSafeInteger(frame.contextRevision)
    || frame.contextRevision <= 0
    || !isDateTime(frame.generatedAt)
    || !isDateTime(frame.expiresAt)
    || Date.parse(frame.expiresAt) <= now
    || frame.reader !== 'authorized_reception_surface'
    || !Array.isArray(frame.excludedFieldClasses)
    || frame.excludedFieldClasses.length !== 7
    || frame.excludedFieldClasses.join('|') !== [
      'contact_details',
      'national_identifiers',
      'clinical_text',
      'appointment_notes',
      'unrestricted_history',
      'credentials',
      'raw_provider_data',
    ].join('|')
    || !Array.isArray(frame.backendFacts)
    || frame.backendFacts.length > 32
    || !frame.backendFacts.every(admitFact)
    || !Array.isArray(frame.derivedSignals)
    || frame.derivedSignals.length > 64
  ) {
    return Object.freeze({ ok: false, reason: 'response_not_admissible' });
  }
  const factIds = new Set(frame.backendFacts.map((fact) => fact.appointmentId));
  if (
    !frame.derivedSignals.every((signal) => admitSignal(signal, factIds))
    || !admitProjection(frame.projection, frame.backendFacts)
  ) {
    return Object.freeze({ ok: false, reason: 'response_not_admissible' });
  }
  return Object.freeze({ ok: true, frame: freezeFrame(frame) });
}

export function assertRayleenWaitingRoomBootstrap(bootstrap) {
  if (
    !hasExactKeys(bootstrap, BOOTSTRAP_KEYS)
    || bootstrap.enabled !== true
    || !isUuid(bootstrap.practiceId)
    || typeof bootstrap.readFixedWaitingRoom !== 'function'
    || !Number.isSafeInteger(bootstrap.sessionGeneration)
    || bootstrap.sessionGeneration <= 0
  ) {
    throw new Error('rayleen_waiting_room_bootstrap_invalid');
  }
  return true;
}

function assertRequest(request) {
  if (
    !hasExactKeys(request, REQUEST_KEYS)
    || !isUuid(request.locationId)
    || !PROJECTION_KINDS.includes(request.projectionKind)
    || !isNullableUuid(request.practitionerId)
    || !isNullableUuid(request.waitingAreaId)
    || !isNullableUuid(request.focusAppointmentId)
  ) {
    throw new Error('rayleen_waiting_room_request_invalid');
  }
}

/** Create one lifecycle-bound, interruption-safe product-read composition. */
export function createRayleenWaitingRoomProjection(bootstrap) {
  assertRayleenWaitingRoomBootstrap(bootstrap);
  const reader = bootstrap.readFixedWaitingRoom;
  let active = true;
  let sessionGeneration = bootstrap.sessionGeneration;
  let latestRequestRevision = 0;
  let activeController = null;
  let totalReads = 0;
  let totalRenders = 0;
  let rejectedReads = 0;
  let expiryTimer = null;
  let expiryWarningTimer = null;

  function clearExpiryTimers() {
    if (expiryTimer !== null) clearTimeout(expiryTimer);
    if (expiryWarningTimer !== null) clearTimeout(expiryWarningTimer);
    expiryTimer = null;
    expiryWarningTimer = null;
  }

  function scheduleExpiry(expiresAt, onExpire) {
    const remaining = Date.parse(expiresAt) - Date.now();
    if (remaining <= 0) {
      onExpire();
      return;
    }
    expiryTimer = setTimeout(
      () => scheduleExpiry(expiresAt, onExpire),
      Math.min(remaining, 2_147_483_647),
    );
    if (typeof expiryTimer?.unref === 'function') expiryTimer.unref();
  }

  function scheduleExpiryWarning(expiresAt, onWarning) {
    const remaining = Date.parse(expiresAt) - Date.now() - 30_000;
    if (remaining <= 0) {
      onWarning();
      return;
    }
    expiryWarningTimer = setTimeout(
      () => scheduleExpiryWarning(expiresAt, onWarning),
      Math.min(remaining, 2_147_483_647),
    );
    if (typeof expiryWarningTimer?.unref === 'function') {
      expiryWarningTimer.unref();
    }
  }

  async function readAndRender(
    request,
    synchronousRender,
    synchronousExpire,
    synchronousExpiryWarning,
  ) {
    assertRequest(request);
    if (typeof synchronousRender !== 'function') {
      throw new Error('synchronous_render_required');
    }
    if (typeof synchronousExpire !== 'function') {
      throw new Error('synchronous_expire_required');
    }
    if (typeof synchronousExpiryWarning !== 'function') {
      throw new Error('synchronous_expiry_warning_required');
    }
    if (!active) return Object.freeze({ ok: false, reason: 'session_inactive' });
    if (activeController !== null) activeController.abort();
    clearExpiryTimers();
    const controller = new AbortController();
    activeController = controller;
    latestRequestRevision += 1;
    const requestRevision = latestRequestRevision;
    const requestGeneration = sessionGeneration;
    totalReads += 1;
    let response;
    try {
      response = await reader(
        Object.freeze({ ...request }),
        Object.freeze({ signal: controller.signal }),
      );
    } catch (error) {
      rejectedReads += 1;
      const interrupted = controller.signal.aborted || error?.name === 'AbortError';
      return Object.freeze({
        ok: false,
        reason: interrupted ? 'request_interrupted' : 'fixed_read_failed',
      });
    }
    if (
      !active
      || controller.signal.aborted
      || requestGeneration !== sessionGeneration
      || requestRevision !== latestRequestRevision
    ) {
      rejectedReads += 1;
      return Object.freeze({ ok: false, reason: 'request_superseded' });
    }
    const admission = admitRayleenWaitingRoomResponse(response, {
      expectedLocationId: request.locationId,
      expectedPracticeId: bootstrap.practiceId,
    });
    if (!admission.ok) {
      rejectedReads += 1;
      return admission;
    }
    totalRenders += 1;
    synchronousRender(admission.frame);
    scheduleExpiryWarning(admission.frame.expiresAt, () => {
      expiryWarningTimer = null;
      if (
        active
        && requestGeneration === sessionGeneration
        && requestRevision === latestRequestRevision
      ) {
        synchronousExpiryWarning();
      }
    });
    scheduleExpiry(admission.frame.expiresAt, () => {
      expiryTimer = null;
      if (
        active
        && requestGeneration === sessionGeneration
        && requestRevision === latestRequestRevision
      ) {
        rejectedReads += 1;
        synchronousExpire();
      }
    });
    return Object.freeze({ ok: true, reason: 'rendered' });
  }

  function invalidateSession() {
    clearExpiryTimers();
    if (activeController !== null) activeController.abort();
    activeController = null;
    active = false;
  }

  function advanceSessionGeneration(newGeneration) {
    if (!Number.isSafeInteger(newGeneration) || newGeneration <= sessionGeneration) {
      throw new Error('rayleen_waiting_room_generation_invalid');
    }
    if (activeController !== null) activeController.abort();
    clearExpiryTimers();
    activeController = null;
    sessionGeneration = newGeneration;
    active = true;
    return true;
  }

  function snapshot() {
    return Object.freeze({
      activeSession: active,
      sessionGeneration,
      latestRequestRevision,
      totalReads,
      totalRenders,
      rejectedReads,
    });
  }

  return Object.freeze({
    readAndRender,
    invalidateSession,
    advanceSessionGeneration,
    snapshot,
  });
}
