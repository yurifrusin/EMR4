/**
 * Provider-free, unmounted, browserless client reconciliation boundary for the
 * accepted fixed native-Diary practitioner read.
 *
 * This is a pure JavaScript latest-read-wins state machine. Trusted composition
 * code establishes one positive monotonically increasing ``sessionGeneration``.
 * Every read is bound to that generation plus a monotonically increasing
 * ``requestRevision`` through an opaque, instance-bound, frozen ticket. A
 * result may reach a render callback only when its ticket is genuine, pending,
 * generated under the exact current session generation, still the latest read,
 * and carrying exactly one strictly admitted fixed-read result.
 *
 * The ``sessionGeneration`` is freshness/suppression metadata only. It is never
 * authentication, authorization, audit or command authority. This module
 * performs no fetch, HTTP, browser, DOM, database, provider, model, memory,
 * command, event, write or audit action. It consumes only the already accepted
 * fixed read result supplied by trusted composition code.
 */

export const REJECTION_REASONS = Object.freeze([
  'session_inactive',
  'session_generation_stale',
  'request_superseded',
  'ticket_unknown',
  'ticket_replayed',
  'response_not_admissible',
]);

const ENVELOPE_KEYS = Object.freeze(['status', 'rows']);
const ROW_KEYS = Object.freeze([
  'id',
  'displayName',
  'roleLabel',
  'active',
  'defaultLocation',
]);
const LOCATION_KEYS = Object.freeze(['id', 'name']);

function _exactKeys(value, expected) {
  const keys = Object.keys(value);
  return keys.length === expected.length && expected.every((key) => keys.includes(key));
}

function _isNonEmptyString(value) {
  return typeof value === 'string' && value.length > 0;
}

function _isNullableNonEmptyString(value) {
  return value === null || _isNonEmptyString(value);
}

function _isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function _admitLocation(location) {
  if (location === null) {
    return true;
  }
  if (!_isPlainObject(location) || !_exactKeys(location, LOCATION_KEYS)) {
    return false;
  }
  return _isNonEmptyString(location.id) && _isNonEmptyString(location.name);
}

function _admitRow(row) {
  if (!_isPlainObject(row) || !_exactKeys(row, ROW_KEYS)) {
    return false;
  }
  if (
    !_isNonEmptyString(row.id) ||
    !_isNonEmptyString(row.displayName) ||
    !_isNullableNonEmptyString(row.roleLabel) ||
    row.active !== true
  ) {
    return false;
  }
  return _admitLocation(row.defaultLocation);
}

/**
 * Strict minimal admission for one successful fixed-read result.
 *
 * The accepted envelope carries a successful fixed-read status plus
 * display-safe practitioner rows already validated by the accepted server
 * contract. Unknown fields, non-array rows, malformed rows, authority/session
 * fields and unsuccessful results all fail closed. No row is retained here;
 * the returned rows array is a projection for the caller's render callback.
 *
 * @param {unknown} returnedResult
 * @returns {{ok: true, rows: object[]} | {ok: false, reason: string}}
 */
export function admitFixedReadResult(returnedResult) {
  if (!_isPlainObject(returnedResult) || !_exactKeys(returnedResult, ENVELOPE_KEYS)) {
    return { ok: false, reason: 'response_not_admissible' };
  }
  if (returnedResult.status !== 'success') {
    return { ok: false, reason: 'response_not_admissible' };
  }
  if (!Array.isArray(returnedResult.rows)) {
    return { ok: false, reason: 'response_not_admissible' };
  }
  for (const row of returnedResult.rows) {
    if (!_admitRow(row)) {
      return { ok: false, reason: 'response_not_admissible' };
    }
  }
  return { ok: true, rows: returnedResult.rows };
}

/**
 * Create a provider-free client reconciler bound to one trusted lifecycle
 * session generation.
 *
 * @param {{initialSessionGeneration: number}} options
 * @returns {Readonly<{
 *   beginRead(): object,
 *   invalidateSession(): void,
 *   advanceSessionGeneration(number): boolean,
 *   reconcileAndRender(object, unknown, (rows: object[]) => void): {ok: boolean, reason: string},
 *   snapshot(): object,
 * }>}
 */
export function createNativeDiaryClientReconciler({ initialSessionGeneration } = {}) {
  if (!Number.isSafeInteger(initialSessionGeneration) || initialSessionGeneration <= 0) {
    throw new Error('invalid_initial_session_generation');
  }

  let active = true;
  let sessionGeneration = initialSessionGeneration;
  let nextRequestRevision = 1;
  let latestRequestRevision = 0;
  // WeakMap<frozenTicket, {sessionGeneration, requestRevision, pending,
  // consumed}>. The reconciler does not retain returned rows or keep an
  // unbounded strong-reference ticket history. A caller-held consumed ticket
  // remains recognizable as replayed.
  const tickets = new WeakMap();
  let latestPendingRecord = null;

  let pendingTicketCount = 0;
  let totalReadsBegun = 0;
  let totalReconcileAttempts = 0;
  let totalRenders = 0;
  let renderCallbackExceptionCount = 0;
  const rejectionCounts = new Map(REJECTION_REASONS.map((reason) => [reason, 0]));

  function _isKnownTicket(ticket) {
    return _isPlainObject(ticket) && tickets.has(ticket);
  }

  function _consume(record) {
    if (!record.consumed) {
      record.consumed = true;
      if (record.pending) {
        record.pending = false;
        pendingTicketCount -= 1;
      }
      if (latestPendingRecord === record) {
        latestPendingRecord = null;
      }
    }
  }

  function _supersedeLatestPending() {
    if (latestPendingRecord !== null && latestPendingRecord.pending) {
      latestPendingRecord.pending = false;
      pendingTicketCount -= 1;
      latestPendingRecord = null;
    }
  }

  /**
   * Begin a new read. Returns an opaque, instance-bound, frozen ticket carrying
   * only the current session generation and a monotonically increasing request
   * revision. Every newer read immediately supersedes the earlier ticket.
   *
   * @returns {Readonly<{sessionGeneration: number, requestRevision: number}>}
   */
  function beginRead() {
    if (!active) {
      throw new Error('session_inactive');
    }
    _supersedeLatestPending();
    const requestRevision = nextRequestRevision;
    nextRequestRevision += 1;
    const record = {
      sessionGeneration,
      requestRevision,
      pending: true,
      consumed: false,
    };
    const ticket = Object.freeze({ sessionGeneration, requestRevision });
    tickets.set(ticket, record);
    pendingTicketCount += 1;
    latestPendingRecord = record;
    latestRequestRevision = requestRevision;
    totalReadsBegun += 1;
    return ticket;
  }

  /**
   * Invalidate every outstanding ticket and deactivate the session. A later
   * session must be established explicitly with `advanceSessionGeneration`; no
   * result from the invalidated generation may render.
   */
  function invalidateSession() {
    _supersedeLatestPending();
    active = false;
  }

  /**
   * Advance the session generation. Requires a strict integer increase over
   * the current generation and invalidates every outstanding ticket. Equal,
   * lower, non-integer or otherwise invalid generation values fail closed and
   * leave all state unchanged.
   *
   * @param {number} newGeneration
   * @returns {true}
   */
  function advanceSessionGeneration(newGeneration) {
    if (!Number.isSafeInteger(newGeneration) || newGeneration <= 0) {
      throw new Error('invalid_generation_advance');
    }
    if (newGeneration <= sessionGeneration) {
      throw new Error('invalid_generation_advance');
    }
    _supersedeLatestPending();
    sessionGeneration = newGeneration;
    active = true;
    return true;
  }

  /**
   * Sole egress. Rechecks ticket provenance, active session, exact current
   * generation, exact latest request revision, pending/one-use state and one
   * strictly admitted fixed-read result. Consumes the ticket before invoking
   * the synchronous render callback; a callback exception can never make the
   * ticket replayable.
   *
   * @param {unknown} ticket
   * @param {unknown} returnedResult
   * @param {(rows: object[]) => void} synchronousRender
   * @returns {{ok: true, reason: 'rendered'} | {ok: false, reason: string}}
   */
  function reconcileAndRender(ticket, returnedResult, synchronousRender) {
    if (typeof synchronousRender !== 'function') {
      throw new Error('synchronous_render_required');
    }
    totalReconcileAttempts += 1;

    if (!_isKnownTicket(ticket)) {
      rejectionCounts.set('ticket_unknown', rejectionCounts.get('ticket_unknown') + 1);
      return { ok: false, reason: 'ticket_unknown' };
    }

    const record = tickets.get(ticket);
    if (record.consumed) {
      rejectionCounts.set('ticket_replayed', rejectionCounts.get('ticket_replayed') + 1);
      return { ok: false, reason: 'ticket_replayed' };
    }

    if (!active) {
      _consume(record);
      rejectionCounts.set('session_inactive', rejectionCounts.get('session_inactive') + 1);
      return { ok: false, reason: 'session_inactive' };
    }

    if (record.sessionGeneration !== sessionGeneration) {
      _consume(record);
      rejectionCounts.set('session_generation_stale', rejectionCounts.get('session_generation_stale') + 1);
      return { ok: false, reason: 'session_generation_stale' };
    }

    if (record.requestRevision !== latestRequestRevision) {
      _consume(record);
      rejectionCounts.set('request_superseded', rejectionCounts.get('request_superseded') + 1);
      return { ok: false, reason: 'request_superseded' };
    }

    const admission = admitFixedReadResult(returnedResult);
    if (!admission.ok) {
      _consume(record);
      rejectionCounts.set('response_not_admissible', rejectionCounts.get('response_not_admissible') + 1);
      return { ok: false, reason: 'response_not_admissible' };
    }

    // Consume before invoking the synchronous callback.
    _consume(record);
    totalRenders += 1;
    try {
      synchronousRender(admission.rows);
    } catch (error) {
      renderCallbackExceptionCount += 1;
      throw error;
    }
    return { ok: true, reason: 'rendered' };
  }

  /**
   * Bounded observability snapshot. Contains only active-session state,
   * generation/revision metadata and bounded counters; never response rows,
   * session identifiers, principal or practice values.
   *
   * @returns {object}
   */
  function snapshot() {
    return {
      activeSession: active,
      sessionGeneration,
      latestRequestRevision,
      outstandingTicketCount: pendingTicketCount,
      totalReadsBegun,
      totalReconcileAttempts,
      totalRenders,
      renderCallbackExceptionCount,
      rejectionCounts: Object.fromEntries(rejectionCounts),
    };
  }

  return Object.freeze({
    beginRead,
    invalidateSession,
    advanceSessionGeneration,
    reconcileAndRender,
    snapshot,
  });
}
