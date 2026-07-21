(function () {
  "use strict";

  const CONTRACT_VERSION = "bernie.meta-grid-projection.v1";
  const MAX_PATIENT_HORIZON_DAYS = 730;
  const DEFAULT_DURATION_MINUTES = 30;
  const EVENT_POLL_INTERVAL_MS = 1800;
  const EVENT_ATTENTION_LIMIT = 100;
  const EVENT_SNOOZE_MS = 5 * 60 * 1000;
  const bridge = window.EMR4DiaryMetaGridBridge;

  if (!bridge) {
    console.error("The functional meta-grid bridge is unavailable.");
    return;
  }

  const elements = {
    host: document.getElementById("bernie-meta-grid"),
    launch: document.getElementById("btn-meta-grid-launch"),
    close: document.getElementById("meta-grid-close"),
    form: document.getElementById("meta-grid-request-form"),
    request: document.getElementById("meta-grid-request"),
    privacy: document.getElementById("meta-grid-privacy"),
    interruptionTest: document.getElementById("meta-grid-interruption-test"),
    privacyBanner: document.getElementById("meta-grid-privacy-banner"),
    back: document.getElementById("meta-grid-back"),
    overview: document.getElementById("meta-grid-overview"),
    explain: document.getElementById("meta-grid-explain"),
    scope: document.getElementById("meta-grid-scope-summary"),
    omissions: document.getElementById("meta-grid-omissions"),
    freshness: document.getElementById("meta-grid-freshness"),
    state: document.getElementById("meta-grid-state"),
    stateLabel: document.getElementById("meta-grid-state-label"),
    stateHeading: document.getElementById("meta-grid-state-heading"),
    stateExplanation: document.getElementById("meta-grid-state-explanation"),
    announcer: document.getElementById("meta-grid-announcer"),
    eventCue: document.getElementById("meta-grid-event-cue"),
    eventCueSummary: document.getElementById("meta-grid-event-cue-summary"),
    eventShow: document.getElementById("meta-grid-event-show"),
    eventDismiss: document.getElementById("meta-grid-event-dismiss"),
    eventSnooze: document.getElementById("meta-grid-event-snooze"),
    eventMute: document.getElementById("meta-grid-event-mute"),
    canvas: document.getElementById("meta-grid-canvas"),
    content: document.getElementById("meta-grid-content"),
    actions: document.getElementById("meta-grid-actions"),
    evidence: document.getElementById("meta-grid-evidence"),
    evidenceHeading: document.getElementById("meta-grid-evidence-heading"),
    evidenceFamily: document.getElementById("meta-grid-evidence-family"),
    evidenceTrigger: document.getElementById("meta-grid-evidence-trigger"),
    evidenceReason: document.getElementById("meta-grid-evidence-reason"),
    evidenceChanges: document.getElementById("meta-grid-evidence-changes"),
    evidenceSource: document.getElementById("meta-grid-evidence-source"),
    evidenceBoundary: document.getElementById("meta-grid-evidence-boundary"),
    rootHistory: document.getElementById("meta-grid-root-history")
  };

  const state = {
    current: null,
    trail: [],
    recentRoots: [],
    selectedItem: null,
    proposalResult: null,
    patientContexts: new Map(),
    private: false,
    interrupted: false,
    comparisonIndex: 0,
    isOpen: false,
    requestSequence: 0,
    eventRuntime: {
      cursor: null,
      enabled: null,
      timer: null,
      inFlight: false,
      deliveredEventIds: new Set(),
      aggregateRevisions: new Map(),
      snoozedUntil: 0,
      muted: false,
      cue: null
    }
  };

  const stateCopy = {
    overview: {
      label: "Overview",
      heading: "Ordinary Diary overview remains the safe fallback",
      explanation: "This summary is read-only. Return to the full Diary whenever spatial context is more useful."
    },
    answer: {
      label: "Answer",
      heading: "Current Diary facts for this request",
      explanation: "The view is a reversible projection over a fresh authorised read."
    },
    selection_only: {
      label: "Selection",
      heading: "A slot is selected; nothing has been booked",
      explanation: "Selection is staff input only. Add a patient to prepare a proposal for review."
    },
    proposal_not_committed: {
      label: "Proposal · not committed",
      heading: "Review the exact proposal before any confirmation handoff",
      explanation: "The meta-grid cannot confirm an appointment. The existing booking review owns that explicit step."
    },
    clarification_required: {
      label: "Clarification needed",
      heading: "One detail needs to be made unambiguous",
      explanation: "No person or command target has been silently selected."
    },
    reconciliation_required: {
      label: "Refresh required",
      heading: "This projection may be stale after an interruption",
      explanation: "Patient details remain hidden and proposal preparation is disabled until a fresh scoped read completes."
    },
    blocked: {
      label: "Blocked",
      heading: "This request cannot be shown safely",
      explanation: "Change the scope, clarify the request or return to the ordinary Diary."
    }
  };

  function createElement(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function secureId(prefix) {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return `${prefix}-${crypto.randomUUID()}`;
    }
    state.requestSequence += 1;
    return `${prefix}-${Date.now()}-${state.requestSequence}`;
  }

  function normaliseText(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[’]/g, "'")
      .replace(/[^a-z0-9:'\-\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function dateFromKey(value) {
    const parts = String(value || "").split("-").map(Number);
    if (parts.length !== 3 || parts.some(part => !Number.isFinite(part))) return null;
    return new Date(parts[0], parts[1] - 1, parts[2]);
  }

  function dateKey(value) {
    const date = value instanceof Date ? value : new Date(value);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function shiftDate(value, days) {
    const date = dateFromKey(value);
    if (!date) return value;
    date.setDate(date.getDate() + days);
    return dateKey(date);
  }

  function dateLabel(value) {
    const date = dateFromKey(value);
    if (!date) return String(value || "date not set");
    return date.toLocaleDateString("en-AU", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  }

  function minutesFromTime(value) {
    const match = String(value || "").match(/^(\d{1,2}):(\d{2})$/);
    if (!match) return null;
    const hours = Number(match[1]);
    const minutes = Number(match[2]);
    if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) return null;
    return hours * 60 + minutes;
  }

  function timeFromMinutes(value) {
    const bounded = Math.max(0, Math.min(24 * 60 - 1, Number(value)));
    return `${String(Math.floor(bounded / 60)).padStart(2, "0")}:${String(bounded % 60).padStart(2, "0")}`;
  }

  function timeLabel(value) {
    const mins = minutesFromTime(String(value || "").slice(0, 5));
    if (mins === null) return String(value || "");
    const date = new Date(2000, 0, 1, Math.floor(mins / 60), mins % 60);
    return date.toLocaleTimeString("en-AU", { hour: "numeric", minute: "2-digit" });
  }

  function addHours(value, durationMinutes) {
    const mins = minutesFromTime(String(value || "").slice(0, 5));
    return mins === null ? "" : timeFromMinutes(mins + Number(durationMinutes || 0));
  }

  function parseClock(text, marker) {
    const pattern = new RegExp(`${marker}\\s+(\\d{1,2})(?::(\\d{2}))?\\s*(am|pm)?`, "i");
    const match = String(text || "").match(pattern);
    if (!match) return null;
    let hour = Number(match[1]);
    const minute = Number(match[2] || 0);
    const meridiem = (match[3] || "").toLowerCase();
    if (meridiem === "pm" && hour < 12) hour += 12;
    if (meridiem === "am" && hour === 12) hour = 0;
    // Reception One is a daytime Diary. In that bounded context an
    // unqualified one-through-six means afternoon; explicit am/pm always wins.
    if (!meridiem && hour >= 1 && hour <= 6) hour += 12;
    if (hour > 23 || minute > 59) return null;
    return `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;
  }

  function resolveDate(text, fallback) {
    const normalised = normaliseText(text);
    if (/\btomorrow\b/.test(normalised)) return shiftDate(fallback, 1);
    if (/\btoday\b/.test(normalised)) return fallback;
    const iso = normalised.match(/\b(20\d{2}-\d{2}-\d{2})\b/);
    if (iso) return iso[1];
    const weekdays = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
    const weekday = weekdays.findIndex(day => normalised.includes(day));
    if (weekday >= 0) {
      const base = dateFromKey(fallback);
      const delta = (weekday - base.getDay() + 7) % 7;
      const add = delta === 0 ? 7 : delta;
      return shiftDate(fallback, normalised.includes(`${weekdays[weekday]} week`) ? add + 7 : add);
    }
    return fallback;
  }

  function parseWindow(text, existing = {}) {
    const normalised = normaliseText(text);
    let from = existing.time_from || "08:00";
    let to = existing.time_to || "17:00";
    const changed = [];
    if (/\bmorning\b/.test(normalised)) {
      from = "08:00";
      to = "12:00";
      changed.push("time_window: morning");
    }
    if (/\bafternoon\b/.test(normalised)) {
      from = "12:00";
      to = "17:00";
      changed.push("time_window: afternoon");
    }
    if (/\b(whole|full) day\b/.test(normalised)) {
      from = "08:00";
      to = "17:00";
      changed.push("time_window: whole day");
    }
    const after = parseClock(normalised, "(?:after|from)");
    if (after) {
      from = after;
      changed.push(`time_from: ${after}`);
    }
    const before = parseClock(normalised, "before");
    if (before) {
      to = before;
      changed.push(`time_to: ${before}`);
    }
    if (minutesFromTime(from) >= minutesFromTime(to)) {
      return { valid: false, from, to, changed };
    }
    return { valid: true, from, to, changed };
  }

  function parseDuration(text, fallback = DEFAULT_DURATION_MINUTES) {
    const source = normaliseText(text);
    let value = null;
    if (/\b(?:a\s+)?half[- ]hour\b/.test(source)) value = 30;
    const minutes = source.match(/\b(\d{1,3})\s*(?:minutes?|mins?)\b/);
    if (minutes) value = Number(minutes[1]);
    if (/\b(?:an|one|1)\s+hour\b/.test(source)) value = 60;
    if (value === null) return { valid: true, value: fallback, changed: [] };
    if (!Number.isInteger(value) || value < 5 || value > 240) {
      return { valid: false, value, changed: ["duration_invalid"] };
    }
    return { valid: true, value, changed: [`duration_minutes: ${value}`] };
  }

  function snapshot() {
    return bridge.getSnapshot();
  }

  function findPractitioners(text) {
    const source = normaliseText(text);
    const rows = snapshot().practitioners || [];
    return rows.filter(row => {
      const name = normaliseText(row.display_name);
      const tokens = name.split(" ").filter(token => !["dr", "doctor", "nurse", "mr", "ms"].includes(token));
      const surname = tokens[tokens.length - 1] || "";
      const firstName = tokens[0] || "";
      return source.includes(name) || (surname.length >= 3 && source.includes(surname)) ||
        (firstName.length >= 4 && source.includes(firstName));
    });
  }

  function patientNameFromRequest(text) {
    const source = String(text || "").replace(/[’]/g, "'");
    const known = snapshot().appointments || [];
    const knownMatches = [...new Set(known.map(item => item.patient_display).filter(Boolean))]
      .filter(name => normaliseText(source).includes(normaliseText(name)));
    if (knownMatches.length === 1) return knownMatches[0];
    const patterns = [
      /(?:appointment|booking|slot)\s+(?:for|with)\s+([a-z][a-z'\-]+\s+[a-z][a-z'\-]+?)(?:\s+(?:after|before|today|tomorrow)|$)/i,
      /(?:show|find|add|book|for)\s+([a-z][a-z'\-]+\s+[a-z][a-z'\-]+?)(?:'s|\s+(?:to|upcoming|appointment|appointments|booking|bookings|slot|today|tomorrow)|$)/i,
      /([a-z][a-z'\-]+\s+[a-z][a-z'\-]+)'s\s+(?:upcoming\s+)?appointments?/i
    ];
    for (const pattern of patterns) {
      const match = source.match(pattern);
      if (match) return match[1].trim();
    }
    return "";
  }

  async function resolvePatient(text) {
    const query = patientNameFromRequest(text);
    if (!query) return { status: "missing", query: "", rows: [] };
    const rows = await bridge.searchPatients(query);
    const exact = rows.filter(row => normaliseText(row.display_name) === normaliseText(query));
    if (exact.length === 1) return { status: "resolved", query, patient: exact[0], rows: exact };
    if (rows.length === 1) return { status: "resolved", query, patient: rows[0], rows };
    return { status: rows.length ? "ambiguous" : "missing", query, rows };
  }

  function rememberPatient(patient) {
    if (!patient?.id || !patient?.display_name) return null;
    const remembered = { id: String(patient.id), display_name: String(patient.display_name) };
    state.patientContexts.set(remembered.id, remembered);
    return remembered;
  }

  function patientForProjection(projection = state.current) {
    const id = projection?.scope?.patient_ids?.[0];
    if (!id) return null;
    const remembered = state.patientContexts.get(String(id));
    if (remembered) return remembered;
    const display = projection.items?.find(item => item.patient_display)?.patient_display;
    return display ? rememberPatient({ id, display_name: display }) : null;
  }

  function baseScope() {
    const current = snapshot();
    return {
      practice_id: "current-authorised-practice",
      timezone: current.timezone || "Australia/Brisbane",
      patient_ids: [],
      practitioner_ids: [],
      date_from: current.date,
      date_to: current.date,
      time_from: "08:00",
      time_to: "17:00",
      location_ids: current.location_id ? [current.location_id] : [],
      status_allowlist: ["Booked", "Arrived", "InConsult", "Completed"],
      duration_minutes: null,
      result_limit: 100
    };
  }

  function newProjection({
    family,
    projectionState,
    scope,
    scopeSummary,
    omissions,
    freshnessSource,
    freshnessReason,
    items,
    affordances,
    operation,
    trigger,
    reason,
    changedDimensions,
    posture,
    operationalCommandAvailable,
    rootIntentId,
    parentProjectionId,
    rootRequest,
    evidenceMode,
    proposalResult = null
  }) {
    return {
      contract_version: CONTRACT_VERSION,
      projection_id: secureId("projection"),
      projection_revision: (state.current?.projection_revision || 0) + 1,
      root_intent_id: rootIntentId || secureId("intent"),
      family,
      state: projectionState,
      scope,
      scope_summary: scopeSummary,
      omissions: omissions || [],
      freshness: {
        source: freshnessSource,
        observed_at: new Date().toISOString(),
        stale: false,
        reason: freshnessReason
      },
      items: items || [],
      affordances: affordances || ["back", "reset", "explain"],
      parent_projection_id: parentProjectionId || null,
      transition: {
        operation,
        trigger,
        reason,
        changed_dimensions: changedDimensions || []
      },
      action_boundary: {
        posture,
        appointment_write_authority: false,
        operational_command_available: Boolean(operationalCommandAvailable),
        required_backend_pattern: operationalCommandAvailable
          ? "Explicit handoff to the existing backend-owned booking review and confirmation path"
          : "No appointment mutation is available from this projection"
      },
      evidence_mode: evidenceMode || snapshot().evidence_mode,
      root_request: rootRequest || "",
      proposal_result: proposalResult
    };
  }

  function rememberRoot() {
    if (!state.current?.root_request) return;
    const existing = state.recentRoots.find(item => item.root_intent_id === state.current.root_intent_id);
    if (existing) return;
    state.recentRoots.unshift({
      root_intent_id: state.current.root_intent_id,
      request: state.current.root_request,
      label: state.current.scope_summary,
      sensitive: Boolean(state.current.scope?.patient_ids?.length)
    });
    state.recentRoots = state.recentRoots.slice(0, 5);
  }

  function setProjection(projection, { newRoot = false, pushCurrent = true, focusCanvas = true } = {}) {
    if (newRoot) {
      rememberRoot();
      state.trail = [];
      state.selectedItem = null;
      state.proposalResult = null;
      state.comparisonIndex = 0;
      state.eventRuntime.cue = null;
    } else if (pushCurrent && state.current) {
      state.trail.push(state.current);
    }
    state.current = projection;
    if (!["selection_only", "proposal_not_committed"].includes(projection.state)) {
      state.selectedItem = null;
    }
    state.proposalResult = projection.proposal_result || null;
    render();
    if (focusCanvas) elements.canvas?.focus();
  }

  function clarificationProjection(message, candidates, rootRequest, { rootIntentId = null, parentProjectionId = null } = {}) {
    const scope = baseScope();
    const items = (candidates || []).map(candidate => ({
      id: candidate.id,
      kind: "clarification_candidate",
      display: candidate.display_name,
      secondary: candidate.date_of_birth ? `Date of birth: ${candidate.date_of_birth}` : "Minimum identity detail only",
      sensitive: true
    }));
    return newProjection({
      family: "clarification",
      projectionState: "clarification_required",
      scope,
      scopeSummary: "Clarification required before a Diary projection can be shown",
      omissions: ["No patient-sensitive Diary facts displayed"],
      freshnessSource: snapshot().evidence_mode,
      freshnessReason: "Minimum authorised identity candidates only",
      items,
      operation: "clarify",
      trigger: "conversation",
      reason: message,
      changedDimensions: ["identity_resolution"],
      posture: "none",
      operationalCommandAvailable: false,
      rootIntentId,
      parentProjectionId,
      rootRequest
    });
  }

  async function buildOverview(rootRequest = "Ordinary overview", context = {}) {
    const current = snapshot();
    const items = (current.appointments || [])
      .filter(item => !["Cancelled", "NoShow", "DNA"].includes(item.status))
      .sort((a, b) => `${a.appointment_date}T${a.start_time_local}`.localeCompare(`${b.appointment_date}T${b.start_time_local}`))
      .slice(0, 12)
      .map(item => ({
        id: item.id,
        kind: "overview_entry",
        display: `${timeLabel(item.start_time_local)} · ${item.practitioner_display}`,
        secondary: `${item.patient_display} · ${item.status}`,
        date: item.appointment_date,
        starts_at: item.start_time_local,
        ends_at: item.end_time_local,
        sensitive: true
      }));
    const scope = baseScope();
    return newProjection({
      family: "ordinary_overview",
      projectionState: "overview",
      scope,
      scopeSummary: `${dateLabel(current.date)} · ${current.location_display} · ordinary overview`,
      omissions: ["Compact summary only; full spatial grid remains available"],
      freshnessSource: current.evidence_mode,
      freshnessReason: "Current loaded Diary read",
      items,
      affordances: ["reset", "explain"],
      operation: context.operation || "reset",
      trigger: context.trigger || "touch",
      reason: context.reason || "User requested the ordinary overview",
      changedDimensions: context.changedDimensions || ["projection_family"],
      posture: "none",
      operationalCommandAvailable: false,
      rootIntentId: context.rootIntentId,
      parentProjectionId: context.parentProjectionId,
      rootRequest
    });
  }

  function appointmentItems(rows) {
    return [...rows]
      .sort((a, b) => `${a.appointment_date}T${a.start_time_local}`.localeCompare(`${b.appointment_date}T${b.start_time_local}`))
      .map(item => ({
        id: item.id,
        kind: "appointment",
        display: `${timeLabel(item.start_time_local)}–${timeLabel(item.end_time_local || addHours(item.start_time_local, item.duration_minutes))}`,
        secondary: `${item.patient_display} · ${item.status}`,
        tertiary: `${item.practitioner_display} · ${item.location_display}`,
        date: item.appointment_date,
        starts_at: item.start_time_local,
        ends_at: item.end_time_local,
        patient_display: item.patient_display,
        practitioner_display: item.practitioner_display,
        location_display: item.location_display,
        status: item.status,
        sensitive: true
      }));
  }

  async function buildFocused(practitioner, requestText, context = {}) {
    const current = snapshot();
    const scope = { ...baseScope() };
    scope.practitioner_ids = [practitioner.id];
    scope.date_from = context.date || resolveDate(requestText, current.date);
    scope.date_to = scope.date_from;
    const window = context.window || parseWindow(requestText, scope);
    if (!window.valid) {
      return clarificationProjection(
        "The requested time window ends before it starts.",
        [],
        requestText,
        { rootIntentId: context.rootIntentId, parentProjectionId: context.parentProjectionId }
      );
    }
    scope.time_from = window.from;
    scope.time_to = window.to;
    const rows = await bridge.readAppointments({
      date_from: scope.date_from,
      date_to: scope.date_to,
      practitioner_id: practitioner.id,
      location_id: current.location_id
    });
    const bounded = rows.filter(item => {
      const start = minutesFromTime(item.start_time_local);
      return start !== null &&
        start >= minutesFromTime(scope.time_from) &&
        start < minutesFromTime(scope.time_to) &&
        !["Cancelled", "NoShow", "DNA"].includes(item.status);
    });
    const items = appointmentItems(bounded);
    return newProjection({
      family: "focused_schedule_lane",
      projectionState: "answer",
      scope,
      scopeSummary: `${practitioner.display_name} · ${dateLabel(scope.date_from)} · ${timeLabel(scope.time_from)}–${timeLabel(scope.time_to)} · ${current.location_display}`,
      omissions: ["Other practitioners hidden", "Cancelled and DNA appointments hidden", "Blank space is not availability"],
      freshnessSource: current.evidence_mode,
      freshnessReason: "Bounded practitioner/date appointment read",
      items,
      affordances: ["refine", "broaden", "back", "reset", "explain"],
      operation: context.operation || "project",
      trigger: context.trigger || "conversation",
      reason: context.reason || "Plain-language practitioner focus",
      changedDimensions: context.changedDimensions || ["practitioner", "date", "time_window"],
      posture: "none",
      operationalCommandAvailable: false,
      rootIntentId: context.rootIntentId,
      parentProjectionId: context.parentProjectionId,
      rootRequest: context.rootRequest || requestText
    });
  }

  async function buildPatientTimeline(patient, requestText, context = {}) {
    const current = snapshot();
    const scope = { ...baseScope() };
    scope.patient_ids = [patient.id];
    scope.date_from = context.dateFrom || current.date;
    scope.date_to = context.dateTo || shiftDate(scope.date_from, MAX_PATIENT_HORIZON_DAYS);
    scope.time_from = null;
    scope.time_to = null;
    const rows = await bridge.readAppointments({
      date_from: scope.date_from,
      date_to: scope.date_to,
      patient_id: patient.id,
      location_id: current.location_id
    });
    const items = appointmentItems(rows.filter(item => !["Cancelled", "NoShow", "DNA"].includes(item.status)));
    return newProjection({
      family: "patient_timeline",
      projectionState: "answer",
      scope,
      scopeSummary: `${patient.display_name} · upcoming appointments · ${current.location_display}`,
      omissions: ["Past, cancelled and DNA appointments hidden", "Future horizon limited to two years"],
      freshnessSource: current.evidence_mode,
      freshnessReason: "Bounded patient appointment read",
      items,
      affordances: ["refine", "broaden", "back", "reset", "explain"],
      operation: context.operation || "project",
      trigger: context.trigger || "conversation",
      reason: context.reason || "Plain-language patient timeline request",
      changedDimensions: context.changedDimensions || ["patient", "future_horizon"],
      posture: "none",
      operationalCommandAvailable: false,
      rootIntentId: context.rootIntentId,
      parentProjectionId: context.parentProjectionId,
      rootRequest: context.rootRequest || requestText
    });
  }

  async function buildAvailability(practitioner, requestText, context = {}) {
    const current = snapshot();
    const scope = { ...baseScope() };
    const patient = context.patient ? rememberPatient(context.patient) : null;
    if (patient) scope.patient_ids = [patient.id];
    scope.practitioner_ids = [practitioner.id];
    scope.date_from = context.date || resolveDate(requestText, current.date);
    scope.date_to = scope.date_from;
    const duration = context.duration !== undefined
      ? {
          valid: Number.isInteger(Number(context.duration)) && Number(context.duration) >= 5 && Number(context.duration) <= 240,
          value: Number(context.duration),
          changed: []
        }
      : parseDuration(requestText, DEFAULT_DURATION_MINUTES);
    if (!duration.valid) {
      return clarificationProjection(
        "Use an appointment duration from 5 to 240 minutes.",
        [],
        requestText,
        { rootIntentId: context.rootIntentId, parentProjectionId: context.parentProjectionId }
      );
    }
    scope.duration_minutes = duration.value;
    const window = context.window || parseWindow(requestText, scope);
    if (!window.valid) {
      return clarificationProjection(
        "The requested availability window ends before it starts.",
        [],
        requestText,
        { rootIntentId: context.rootIntentId, parentProjectionId: context.parentProjectionId }
      );
    }
    scope.time_from = window.from;
    scope.time_to = window.to;
    const proposal = await bridge.readAvailability({
      practitioner_id: practitioner.id,
      date_from: scope.date_from,
      date_to: scope.date_to,
      duration_minutes: scope.duration_minutes,
      location_id: current.location_id || undefined,
      earliest_time: scope.time_from,
      latest_time: scope.time_to,
      limit: 20
    });
    const items = (proposal.candidates || []).map((candidate, index) => ({
      id: candidate.candidate_freshness_id || `${practitioner.id}-${candidate.appointment_date}-${candidate.start_time_local}-${index}`,
      kind: "available_slot",
      display: `${timeLabel(candidate.start_time_local)}–${timeLabel(addHours(candidate.start_time_local, candidate.duration_minutes))}`,
      secondary: `${practitioner.display_name} · ${candidate.duration_minutes} minutes · available at read time`,
      tertiary: (candidate.warnings || []).map(warning => warning.message).filter(Boolean).join(" · "),
      date: candidate.appointment_date,
      starts_at: candidate.start_time_local,
      ends_at: addHours(candidate.start_time_local, candidate.duration_minutes),
      practitioner_id: practitioner.id,
      practitioner_display: practitioner.display_name,
      location_id: current.location_id || practitioner.location_id || null,
      location_display: current.location_display,
      duration_minutes: candidate.duration_minutes,
      patient_display: patient?.display_name || null,
      selectable: true,
      raw_candidate: candidate
    }));
    const projection = newProjection({
      family: "availability_slots",
      projectionState: "answer",
      scope,
      scopeSummary: `${practitioner.display_name} · ${dateLabel(scope.date_from)} · ${timeLabel(scope.time_from)}–${timeLabel(scope.time_to)} · ${scope.duration_minutes} minutes`,
      omissions: ["Only deterministic candidate slots shown", "Selection does not reserve or book"],
      freshnessSource: proposal.evidence_mode || (snapshot().evidence_mode === "authored_synthetic_client_fixture" ? "authored_synthetic_client_fixture" : "live_local_non_mutating_proposal"),
      freshnessReason: "Existing non-mutating slot-search proposal",
      items,
      affordances: ["refine", "broaden", "select", "back", "reset", "explain"],
      operation: context.operation || "project",
      trigger: context.trigger || "conversation",
      reason: context.reason || "Plain-language availability request",
      changedDimensions: context.changedDimensions || ["practitioner", "date", "time_window", "duration"],
      posture: "selection_only",
      operationalCommandAvailable: false,
      rootIntentId: context.rootIntentId,
      parentProjectionId: context.parentProjectionId,
      rootRequest: context.rootRequest || requestText
    });
    if (patient) {
      projection.scope_summary = `${patient.display_name} · ${projection.scope_summary}`;
      projection.omissions.push("Patient is proposal context only; no appointment exists");
      if (!context.reason) {
        projection.transition.reason = "Plain-language combined patient, practitioner, date, time and duration request";
      }
      if (!context.changedDimensions) {
        projection.transition.changed_dimensions = ["patient", ...projection.transition.changed_dimensions];
      }
    }
    return projection;
  }

  async function buildComparison(practitioners, requestText, context = {}) {
    const current = snapshot();
    const scope = { ...baseScope() };
    scope.practitioner_ids = practitioners.map(item => item.id);
    scope.date_from = context.date || resolveDate(requestText, current.date);
    scope.date_to = scope.date_from;
    scope.duration_minutes = context.duration || DEFAULT_DURATION_MINUTES;
    const window = context.window || parseWindow(requestText, scope);
    if (!window.valid) {
      return clarificationProjection(
        "The comparison window ends before it starts.",
        [],
        requestText,
        { rootIntentId: context.rootIntentId, parentProjectionId: context.parentProjectionId }
      );
    }
    scope.time_from = window.from;
    scope.time_to = window.to;
    const results = [];
    for (const practitioner of practitioners) {
      const proposal = await bridge.readAvailability({
        practitioner_id: practitioner.id,
        date_from: scope.date_from,
        date_to: scope.date_to,
        duration_minutes: scope.duration_minutes,
        location_id: current.location_id || undefined,
        earliest_time: scope.time_from,
        latest_time: scope.time_to,
        limit: 8
      });
      (proposal.candidates || []).forEach((candidate, index) => {
        results.push({
          id: candidate.candidate_freshness_id || `${practitioner.id}-${candidate.start_time_local}-${index}`,
          kind: "comparison_slot",
          display: `${timeLabel(candidate.start_time_local)}–${timeLabel(addHours(candidate.start_time_local, candidate.duration_minutes))}`,
          secondary: `${candidate.duration_minutes} minutes · available at read time`,
          date: candidate.appointment_date,
          starts_at: candidate.start_time_local,
          ends_at: addHours(candidate.start_time_local, candidate.duration_minutes),
          practitioner_id: practitioner.id,
          practitioner_display: practitioner.display_name,
          comparison_group: practitioner.display_name,
          duration_minutes: candidate.duration_minutes,
          raw_candidate: candidate,
          selectable: true
        });
      });
    }
    results.sort((a, b) => `${a.starts_at}-${a.practitioner_display}`.localeCompare(`${b.starts_at}-${b.practitioner_display}`));
    return newProjection({
      family: "aligned_comparison",
      projectionState: "answer",
      scope,
      scopeSummary: `${practitioners.map(item => item.display_name).join(" compared with ")} · ${dateLabel(scope.date_from)} · ${timeLabel(scope.time_from)}–${timeLabel(scope.time_to)}`,
      omissions: ["Other practitioners hidden", "Every lane uses the same date, time, location and duration basis"],
      freshnessSource: current.evidence_mode === "authored_synthetic_client_fixture" ? "authored_synthetic_client_fixture" : "live_local_non_mutating_proposal",
      freshnessReason: "Repeated existing slot-search proposals on one aligned basis",
      items: results,
      affordances: ["refine", "broaden", "select", "back", "reset", "explain"],
      operation: context.operation || "compare",
      trigger: context.trigger || "conversation",
      reason: context.reason || "Plain-language aligned practitioner comparison",
      changedDimensions: context.changedDimensions || ["practitioner_set", "comparison_basis"],
      posture: "selection_only",
      operationalCommandAvailable: false,
      rootIntentId: context.rootIntentId,
      parentProjectionId: context.parentProjectionId,
      rootRequest: context.rootRequest || requestText
    });
  }

  function selectionProjection(item, trigger = "touch", sourceProjection = state.current, context = {}) {
    const current = sourceProjection;
    const items = current.items.map(existing => ({ ...existing, selected: existing.id === item.id }));
    return newProjection({
      family: current.family,
      projectionState: "selection_only",
      scope: { ...current.scope },
      scopeSummary: `${current.scope_summary} · ${timeLabel(item.starts_at)} selected`,
      omissions: [...current.omissions, "Nothing is reserved or booked"],
      freshnessSource: current.freshness.source,
      freshnessReason: current.freshness.reason,
      items,
      affordances: ["prepare_proposal", "back", "reset", "explain"],
      operation: "select",
      trigger,
      reason: context.reason || "Staff selected one candidate slot",
      changedDimensions: context.changedDimensions || ["selected_item"],
      posture: "selection_only",
      operationalCommandAvailable: false,
      rootIntentId: current.root_intent_id,
      parentProjectionId: current.projection_id,
      rootRequest: current.root_request,
      evidenceMode: current.evidence_mode
    });
  }

  async function buildProposal(patient, requestText) {
    const selected = state.selectedItem;
    if (!selected) {
      return clarificationProjection("Select one available slot before adding a patient.", [], requestText);
    }
    const availabilityBasis = availabilitySignature(state.current);
    const current = snapshot();
    const result = await bridge.prepareProposal({
      practitioner_id: selected.practitioner_id,
      practitioner_display: selected.practitioner_display,
      patient_id: patient.id,
      patient_display: patient.display_name,
      location_id: selected.location_id || current.location_id,
      reference_date: state.current.scope.date_from || current.date,
      selected_candidate: selected.raw_candidate,
      latest_time: state.current.scope.time_to
    });
    const review = result.staff_review || result.payload?.staff_review || {};
    const scope = { ...state.current.scope, patient_ids: [patient.id] };
    const selectedSlot = review.selected_slot || selected.raw_candidate;
    const items = [{
      id: selected.id,
      kind: "proposal_summary",
      display: `${patient.display_name} · ${selected.practitioner_display}`,
      secondary: `${dateLabel(selectedSlot.appointment_date)} · ${timeLabel(selectedSlot.start_time_local)} · ${selectedSlot.duration_minutes} minutes`,
      tertiary: (review.warning_summary || "No warning summary returned").trim(),
      patient_display: patient.display_name,
      practitioner_display: selected.practitioner_display,
      location_display: selected.location_display || current.location_display,
      sensitive: true
    }];
    const projection = newProjection({
      family: "proposal_review",
      projectionState: "proposal_not_committed",
      scope,
      scopeSummary: `${patient.display_name} · ${selected.practitioner_display} · ${dateLabel(selectedSlot.appointment_date)} · ${timeLabel(selectedSlot.start_time_local)}`,
      omissions: ["No appointment has been created", "Confirmation is not available inside the meta-grid"],
      freshnessSource: result.evidence_mode,
      freshnessReason: result.operational
        ? "Existing supervised-booking proposal envelope"
        : "Authored synthetic proposal review fixture",
      items,
      affordances: result.operational ? ["command_handoff", "back", "reset", "explain"] : ["back", "reset", "explain"],
      operation: "prepare_proposal",
      trigger: "conversation",
      reason: "Patient identity was resolved for the selected slot",
      changedDimensions: ["patient", "proposal_state"],
      posture: "proposal_only",
      operationalCommandAvailable: result.operational,
      rootIntentId: state.current.root_intent_id,
      parentProjectionId: state.current.projection_id,
      rootRequest: state.current.root_request,
      evidenceMode: result.evidence_mode,
      proposalResult: result
    });
    projection.availability_signature = availabilityBasis;
    return projection;
  }

  function isRefinement(text) {
    const source = normaliseText(text);
    return Boolean(state.current) && (
      /^(after|before|from|morning|afternoon|whole day|full day|only booked|show all|broaden|narrow|refine)\b/.test(source) ||
      /^(today|tomorrow)(?:\s+instead)?\b/.test(source) ||
      /^(?:make\s+it\s+)?(?:a\s+)?(?:half[- ]hour|\d{1,3}\s*(?:minutes?|mins?)|(?:an|one|1)\s+hour)\b/.test(source) ||
      /^next\s+\d+\s+days?\b/.test(source)
    );
  }

  async function refineCurrent(text) {
    const current = state.current;
    const window = parseWindow(text, current.scope);
    const duration = parseDuration(text, current.scope.duration_minutes || DEFAULT_DURATION_MINUTES);
    if (!window.valid) {
      return clarificationProjection(
        "The refinement would create an invalid time window.",
        [],
        current.root_request,
        { rootIntentId: current.root_intent_id, parentProjectionId: current.projection_id }
      );
    }
    if (!duration.valid) {
      return clarificationProjection(
        "Use an appointment duration from 5 to 240 minutes.",
        [],
        current.root_request,
        { rootIntentId: current.root_intent_id, parentProjectionId: current.projection_id }
      );
    }
    const directory = snapshot().practitioners || [];
    const practitioners = current.scope.practitioner_ids
      .map(id => directory.find(row => row.id === id))
      .filter(Boolean);
    const dateRequested = /\b(?:today|tomorrow)\b/.test(normaliseText(text));
    const nextDate = dateRequested
      ? resolveDate(text, snapshot().date)
      : current.scope.date_from;
    const changedDimensions = [
      ...window.changed,
      ...duration.changed,
      ...(dateRequested ? [`date: ${nextDate}`] : [])
    ];
    const context = {
      date: nextDate,
      window,
      duration: duration.value,
      patient: patientForProjection(current),
      operation: /\b(whole|full|show all|broaden)\b/.test(normaliseText(text)) ? "broaden" : "refine",
      trigger: "conversation",
      reason: `Plain-language refinement: ${text}`,
      changedDimensions: changedDimensions.length ? [...new Set(changedDimensions)] : ["display_filter"],
      rootIntentId: current.root_intent_id,
      parentProjectionId: current.projection_id,
      rootRequest: current.root_request
    };
    if (current.family === "focused_schedule_lane" && practitioners[0]) {
      return buildFocused(practitioners[0], current.root_request, context);
    }
    if (["availability_slots", "proposal_review"].includes(current.family) && practitioners[0]) {
      return buildAvailability(practitioners[0], current.root_request, context);
    }
    if (current.family === "aligned_comparison" && practitioners.length >= 2) {
      return buildComparison(practitioners, current.root_request, context);
    }
    if (current.family === "patient_timeline") {
      const patientId = current.scope.patient_ids[0];
      const display = current.items[0]?.patient_display || current.scope_summary.split(" · ")[0];
      const daysMatch = normaliseText(text).match(/next\s+(\d+)\s+days/);
      return buildPatientTimeline(
        { id: patientId, display_name: display },
        current.root_request,
        {
          dateFrom: snapshot().date,
          dateTo: daysMatch ? shiftDate(snapshot().date, Math.min(Number(daysMatch[1]), MAX_PATIENT_HORIZON_DAYS)) : current.scope.date_to,
          operation: context.operation,
          trigger: context.trigger,
          reason: context.reason,
          changedDimensions: daysMatch ? ["future_horizon"] : context.changedDimensions,
          rootIntentId: current.root_intent_id,
          parentProjectionId: current.projection_id,
          rootRequest: current.root_request
        }
      );
    }
    return clarificationProjection(
      "That refinement is not available for this projection. Start a new root request or go back.",
      [],
      current.root_request,
      { rootIntentId: current.root_intent_id, parentProjectionId: current.projection_id }
    );
  }

  async function refreshCurrent() {
    const current = state.current;
    if (!current) return;
    const directory = snapshot().practitioners || [];
    const practitioners = current.scope.practitioner_ids
      .map(id => directory.find(row => row.id === id))
      .filter(Boolean);
    let patient = patientForProjection(current);
    if (patient && ["availability_slots", "proposal_review"].includes(current.family)) {
      const refreshedPatient = await resolvePatient(patient.display_name);
      if (refreshedPatient.status !== "resolved") {
        const clarification = clarificationProjection(
          refreshedPatient.status === "ambiguous"
            ? `More than one patient matches ${refreshedPatient.query}. Choose the intended person.`
            : "The patient must be resolved again after the interruption.",
          refreshedPatient.rows,
          current.root_request,
          { rootIntentId: current.root_intent_id, parentProjectionId: current.projection_id }
        );
        state.interrupted = false;
        setProjection(clarification, { newRoot: false, pushCurrent: true });
        return;
      }
      patient = rememberPatient(refreshedPatient.patient);
    }
    const context = {
      date: current.scope.date_from,
      window: { valid: true, from: current.scope.time_from || "08:00", to: current.scope.time_to || "17:00", changed: ["freshness"] },
      duration: current.scope.duration_minutes || DEFAULT_DURATION_MINUTES,
      patient,
      operation: "reconcile",
      trigger: "system_freshness",
      reason: "Fresh scoped read after interruption",
      changedDimensions: ["freshness"],
      rootIntentId: current.root_intent_id,
      parentProjectionId: current.projection_id,
      rootRequest: current.root_request
    };
    let next = null;
    if (current.family === "focused_schedule_lane" && practitioners[0]) {
      next = await buildFocused(practitioners[0], current.root_request, context);
    } else if (current.family === "availability_slots" && practitioners[0]) {
      next = await buildAvailability(practitioners[0], current.root_request, context);
    } else if (current.family === "proposal_review" && practitioners[0]) {
      // Proposal and patient selection are deliberately discarded on
      // interruption. Recover the exact underlying availability scope only
      // after fresh patient resolution and a fresh backend availability read;
      // never reconstruct or retain the stale slot or proposal.
      next = await buildAvailability(practitioners[0], current.root_request, context);
    } else if (current.family === "aligned_comparison" && practitioners.length >= 2) {
      next = await buildComparison(practitioners, current.root_request, context);
    } else if (current.family === "patient_timeline") {
      next = await buildPatientTimeline(
        { id: current.scope.patient_ids[0], display_name: current.scope_summary.split(" · ")[0] },
        current.root_request,
        {
          dateFrom: current.scope.date_from,
          dateTo: current.scope.date_to,
          ...context
        }
      );
    } else {
      next = await buildOverview(current.root_request, context);
    }
    state.interrupted = false;
    setProjection(next, { newRoot: false, pushCurrent: true });
  }

  async function routeRequest(rawText, options = {}) {
    const text = String(rawText || "").trim();
    if (!text) {
      return clarificationProjection("Type the person, practitioner, date or view you need.", [], "");
    }
    const source = normaliseText(text);
    if (/^(back|go back)$/.test(source)) {
      goBack();
      return null;
    }
    if (/\b(ordinary diary|full diary|full grid|overview)\b/.test(source)) {
      return buildOverview(text);
    }
    if (isRefinement(text)) {
      return refineCurrent(text);
    }
    if (state.selectedItem && /\b(add|book|make|prepare)\b/.test(source)) {
      const patient = await resolvePatient(text);
      if (patient.status !== "resolved") {
        return clarificationProjection(
          patient.status === "ambiguous"
            ? `More than one patient matches ${patient.query}. Choose the intended person.`
            : "Name the patient to add to the selected slot.",
          patient.rows,
          state.current?.root_request || text,
          { rootIntentId: state.current?.root_intent_id, parentProjectionId: state.current?.projection_id }
        );
      }
      return buildProposal(patient.patient, text);
    }
    if (/\bupcoming\b/.test(source) || /\bpatient\b.*\bappointments?\b/.test(source) || /'s\s+(?:upcoming\s+)?appointments?\b/.test(source)) {
      const patient = await resolvePatient(text);
      if (patient.status !== "resolved") {
        return clarificationProjection(
          patient.status === "ambiguous"
            ? `More than one patient matches ${patient.query}. Choose the intended person.`
            : "Which patient should I show? Use their full name.",
          patient.rows,
          text
        );
      }
      return buildPatientTimeline(patient.patient, text);
    }
    const practitioners = findPractitioners(text);
    if (/\bcompare\b/.test(source)) {
      if (practitioners.length !== 2) {
        return clarificationProjection(
          practitioners.length > 2
            ? "Choose exactly two practitioners for an aligned comparison."
            : "Name two practitioners to compare on one date and time basis.",
          practitioners.map(item => ({ id: item.id, display_name: item.display_name })),
          text
        );
      }
      return buildComparison(practitioners, text);
    }
    if (/\b(availability|available|free slots?|open slots?)\b/.test(source)) {
      if (practitioners.length !== 1) {
        return clarificationProjection(
          practitioners.length > 1
            ? "Which one practitioner should I search for availability?"
            : "Which practitioner should I search for availability?",
          practitioners.map(item => ({ id: item.id, display_name: item.display_name })),
          text
        );
      }
      const patientQuery = patientNameFromRequest(text);
      let patient = null;
      if (patientQuery) {
        const patientResolution = await resolvePatient(text);
        if (patientResolution.status !== "resolved") {
          return clarificationProjection(
            patientResolution.status === "ambiguous"
              ? `More than one patient matches ${patientResolution.query}. Choose the intended person.`
              : "Which patient is this availability for? Use their full name.",
            patientResolution.rows,
            text
          );
        }
        patient = rememberPatient(patientResolution.patient);
      }
      const duration = parseDuration(text, DEFAULT_DURATION_MINUTES);
      if (!duration.valid) {
        return clarificationProjection("Use an appointment duration from 5 to 240 minutes.", [], text);
      }
      return buildAvailability(practitioners[0], text, {
        patient,
        duration: duration.value
      });
    }
    if (practitioners.length === 1) {
      return buildFocused(practitioners[0], text);
    }
    if (practitioners.length > 1) {
      return clarificationProjection(
        "More than one practitioner matches. Use a full name.",
        practitioners.map(item => ({ id: item.id, display_name: item.display_name })),
        text
      );
    }
    return clarificationProjection(
      "I can show a practitioner window, a patient's upcoming appointments, availability or an aligned comparison. Add the missing person or view.",
      [],
      text
    );
  }

  async function submitRequest(text, { restore = false } = {}) {
    setBusy(true);
    try {
      const projection = await routeRequest(text, { restore });
      if (!projection) return;
      const sameRoot = projection.root_intent_id === state.current?.root_intent_id;
      setProjection(projection, { newRoot: !sameRoot, pushCurrent: sameRoot });
      elements.request.value = "";
    } catch (error) {
      const projection = newProjection({
        family: "clarification",
        projectionState: "blocked",
        scope: baseScope(),
        scopeSummary: "The requested projection could not be completed",
        omissions: ["No partial or stale result displayed"],
        freshnessSource: snapshot().evidence_mode,
        freshnessReason: "Read or proposal surface failed closed",
        items: [],
        operation: "clarify",
        trigger: "system_freshness",
        reason: error.message || "Projection failed",
        changedDimensions: ["failure_state"],
        posture: "none",
        operationalCommandAvailable: false,
        rootRequest: text
      });
      setProjection(projection, { newRoot: true });
    } finally {
      setBusy(false);
    }
  }

  function setBusy(busy) {
    const submit = elements.form?.querySelector('[type="submit"]');
    if (submit) {
      submit.disabled = busy;
      submit.textContent = busy ? "Reading current Diary…" : "Show this view";
    }
  }

  function rememberBoundedSet(set, value) {
    set.add(value);
    while (set.size > EVENT_ATTENTION_LIMIT) {
      set.delete(set.values().next().value);
    }
  }

  function rememberBoundedRevision(aggregateId, revision) {
    const revisions = state.eventRuntime.aggregateRevisions;
    revisions.delete(aggregateId);
    revisions.set(aggregateId, revision);
    while (revisions.size > EVENT_ATTENTION_LIMIT) {
      revisions.delete(revisions.keys().next().value);
    }
  }

  function projectionAppointment(projection, appointmentId) {
    return projection?.items?.find(item => (
      item.kind === "appointment" && String(item.id) === String(appointmentId)
    )) || null;
  }

  function availabilitySlotIdentity(item) {
    if (!item) return null;
    const candidate = item.raw_candidate || {};
    const date = item.date || candidate.appointment_date || "";
    const startsAt = item.starts_at || candidate.start_time_local || "";
    const duration = Number(item.duration_minutes || candidate.duration_minutes || 0);
    const practitionerId = item.practitioner_id || candidate.practitioner_id || "";
    const locationId = item.location_id || candidate.location_id || "";
    if (!date || !startsAt || !duration || !practitionerId) return null;
    return [
      String(practitionerId),
      String(locationId),
      String(date),
      String(startsAt).slice(0, 5),
      String(duration)
    ].join("|");
  }

  function availabilityCandidateMap(projection) {
    const candidates = new Map();
    (projection?.items || []).forEach(item => {
      if (item.kind !== "available_slot") return;
      const identity = availabilitySlotIdentity(item);
      if (identity) candidates.set(identity, item);
    });
    return candidates;
  }

  function availabilitySignature(projection) {
    return [...availabilityCandidateMap(projection).keys()].sort().join("\n");
  }

  function currentAvailabilityProjectionEligible(current) {
    return Boolean(
      current &&
      !state.interrupted &&
      current.state !== "reconciliation_required" &&
      ["availability_slots", "proposal_review"].includes(current.family) &&
      current.scope?.practitioner_ids?.length === 1
    );
  }

  async function freshAvailabilityForCommittedEvent(current) {
    const practitioner = (snapshot().practitioners || [])
      .find(row => row.id === current.scope.practitioner_ids[0]);
    if (!practitioner) return null;
    return buildAvailability(practitioner, current.root_request, {
      date: current.scope.date_from,
      window: {
        valid: true,
        from: current.scope.time_from || "08:00",
        to: current.scope.time_to || "17:00",
        changed: ["freshness"]
      },
      duration: current.scope.duration_minutes || DEFAULT_DURATION_MINUTES,
      patient: patientForProjection(current),
      operation: "reconcile",
      trigger: "committed_event",
      reason: "Fresh availability read after a committed appointment-time change",
      changedDimensions: ["availability", "freshness"],
      rootIntentId: current.root_intent_id,
      parentProjectionId: current.projection_id,
      rootRequest: current.root_request
    });
  }

  async function freshProjectionForCommittedEvent(current) {
    const context = {
      operation: "reconcile",
      trigger: "committed_event",
      reason: "Fresh scoped read after a committed appointment-time change",
      changedDimensions: ["appointment_time", "freshness"],
      rootIntentId: current.root_intent_id,
      parentProjectionId: current.projection_id,
      rootRequest: current.root_request
    };
    if (current.family === "patient_timeline") {
      const patient = patientForProjection(current);
      if (!patient) return null;
      return buildPatientTimeline(patient, current.root_request, {
        dateFrom: current.scope.date_from,
        dateTo: current.scope.date_to,
        ...context
      });
    }
    if (current.family === "focused_schedule_lane") {
      const practitioner = (snapshot().practitioners || [])
        .find(row => row.id === current.scope.practitioner_ids?.[0]);
      if (!practitioner) return null;
      return buildFocused(practitioner, current.root_request, {
        date: current.scope.date_from,
        window: {
          valid: true,
          from: current.scope.time_from || "08:00",
          to: current.scope.time_to || "17:00",
          changed: ["freshness"]
        },
        ...context
      });
    }
    return null;
  }

  function validCommittedEvent(event) {
    if (!event || event.event_type !== "diary.appointment_rescheduled") return false;
    if (event.schema_version !== "diary.appointment_rescheduled.v1") return false;
    if (event.source_system !== "emr4-diary") return false;
    if (!event.event_id || !event.aggregate_id || !Number.isInteger(event.aggregate_revision)) return false;
    if (event.aggregate_revision < 1) return false;
    if (String(event.payload?.appointment_id || "") !== String(event.aggregate_id)) return false;
    return Array.isArray(event.payload?.reason_codes) &&
      event.payload.reason_codes.length === 1 &&
      event.payload.reason_codes[0] === "appointment_time_changed";
  }

  async function consumeCommittedEvent(event) {
    if (!validCommittedEvent(event)) return;
    const eventId = String(event.event_id);
    const aggregateId = String(event.aggregate_id);
    if (state.eventRuntime.deliveredEventIds.has(eventId)) return;
    const previousRevision = state.eventRuntime.aggregateRevisions.get(aggregateId) || 0;
    if (event.aggregate_revision <= previousRevision) {
      rememberBoundedSet(state.eventRuntime.deliveredEventIds, eventId);
      return;
    }
    rememberBoundedSet(state.eventRuntime.deliveredEventIds, eventId);
    rememberBoundedRevision(aggregateId, event.aggregate_revision);

    const current = state.current;
    const initiatingProjectionId = current?.projection_id;
    const previousItem = projectionAppointment(current, aggregateId);
    const availabilityEligible = currentAvailabilityProjectionEligible(current);
    if (!state.isOpen || (!previousItem && !availabilityEligible)) return;

    let freshAppointment;
    try {
      freshAppointment = await bridge.readAppointment(aggregateId);
    } catch (_) {
      return;
    }
    if (!freshAppointment || String(freshAppointment.id) !== aggregateId) return;

    if (
      !state.isOpen ||
      state.interrupted ||
      state.current?.projection_id !== initiatingProjectionId
    ) return;

    if (availabilityEligible && !previousItem) {
      const scopedPractitionerId = String(current.scope.practitioner_ids[0]);
      if (String(freshAppointment.practitioner_id || "") !== scopedPractitionerId) return;

      const previousSelection = state.selectedItem;
      const previousSelectionIdentity = availabilitySlotIdentity(previousSelection);
      const previousSignature = current.family === "proposal_review"
        ? String(current.availability_signature || "")
        : availabilitySignature(current);
      const next = await freshAvailabilityForCommittedEvent(current);
      if (!next) return;
      if (
        !state.isOpen ||
        state.interrupted ||
        state.current?.projection_id !== initiatingProjectionId
      ) return;

      const nextCandidates = availabilityCandidateMap(next);
      const freshSelection = previousSelectionIdentity
        ? nextCandidates.get(previousSelectionIdentity) || null
        : null;
      const nextSignature = availabilitySignature(next);
      const candidateSetChanged = !previousSignature || previousSignature !== nextSignature;
      if (candidateSetChanged) {
        // Earlier projections in this root were built over the superseded
        // candidate set. Do not let Back resurrect a stale selection or
        // non-committing proposal after reconciliation.
        state.trail = [];
      }
      let cueOutcome = null;
      let cueContextProjection = next;
      let cueContextSelection = freshSelection;

      if (previousSelection && freshSelection) {
        state.selectedItem = freshSelection;
        if (current.family === "proposal_review") {
          const preservedProposal = {
            ...current,
            projection_id: secureId("projection"),
            parent_projection_id: current.projection_id,
            created_at: new Date().toISOString(),
            freshness: {
              ...next.freshness,
              reason: "Fresh availability reconciliation confirmed the proposed time remains available"
            },
            transition: {
              operation: "reconcile",
              trigger: "committed_event",
              reason: "The candidate set changed but the proposed time remains available",
              changed_dimensions: ["availability", "freshness"]
            },
            availability_signature: nextSignature
          };
          setProjection(preservedProposal, { newRoot: false, pushCurrent: false, focusCanvas: false });
          if (candidateSetChanged) cueOutcome = "proposal_preserved";
        } else {
          const preservedSelection = selectionProjection(
            freshSelection,
            "committed_event",
            next,
            {
              reason: candidateSetChanged
                ? "The candidate set changed but the selected time remains available"
                : "Fresh availability reconciliation confirmed the selected time remains available",
              changedDimensions: candidateSetChanged
                ? ["availability", "selected_item", "freshness"]
                : ["freshness"]
            }
          );
          setProjection(preservedSelection, { newRoot: false, pushCurrent: false, focusCanvas: false });
          if (candidateSetChanged) cueOutcome = "selection_preserved";
        }
      } else {
        setProjection(next, { newRoot: false, pushCurrent: false, focusCanvas: false });
        if (previousSelection) {
          cueOutcome = current.family === "proposal_review"
            ? "proposal_unavailable"
            : "selection_unavailable";
          cueContextSelection = null;
        } else if (candidateSetChanged) {
          cueOutcome = "availability_changed";
          cueContextSelection = null;
        }
      }

      if (
        !cueOutcome ||
        state.eventRuntime.muted ||
        state.eventRuntime.snoozedUntil > Date.now()
      ) return;

      const existingCue = state.eventRuntime.cue;
      state.eventRuntime.cue = {
        eventId,
        aggregateId,
        kind: "availability_reconciliation",
        outcome: cueOutcome,
        selectedWindow: previousSelection?.display || null,
        contextProjection: cueContextProjection,
        contextSelection: cueContextSelection,
        coalescedCount: existingCue ? existingCue.coalescedCount + 1 : 1
      };
      renderEventCue();
      return;
    }

    const next = await freshProjectionForCommittedEvent(current);
    if (!next) return;
    if (
      !state.isOpen ||
      state.interrupted ||
      state.current?.projection_id !== initiatingProjectionId
    ) return;
    const currentItem = projectionAppointment(next, aggregateId);
    if (!currentItem) return;
    if (
      previousItem.starts_at === currentItem.starts_at &&
      previousItem.ends_at === currentItem.ends_at
    ) return;

    state.interrupted = false;
    setProjection(next, { newRoot: false, pushCurrent: false, focusCanvas: false });
    if (
      state.eventRuntime.muted ||
      state.eventRuntime.snoozedUntil > Date.now()
    ) return;

    const existingCue = state.eventRuntime.cue;
    state.eventRuntime.cue = {
      eventId,
      aggregateId,
      kind: "appointment_time_change",
      oldWindow: previousItem.display,
      newWindow: currentItem.display,
      coalescedCount: existingCue ? existingCue.coalescedCount + 1 : 1
    };
    renderEventCue();
  }

  function stopEventPolling() {
    if (state.eventRuntime.timer !== null) {
      clearTimeout(state.eventRuntime.timer);
      state.eventRuntime.timer = null;
    }
  }

  function scheduleEventPoll(delay = EVENT_POLL_INTERVAL_MS) {
    stopEventPolling();
    if (
      !state.isOpen ||
      document.hidden ||
      state.eventRuntime.enabled === false
    ) return;
    state.eventRuntime.timer = setTimeout(pollCommittedEvents, delay);
  }

  async function pollCommittedEvents() {
    state.eventRuntime.timer = null;
    if (
      state.eventRuntime.inFlight ||
      !state.isOpen ||
      document.hidden ||
      state.eventRuntime.enabled === false
    ) return;
    state.eventRuntime.inFlight = true;
    try {
      const feed = await bridge.readCommittedEvents(state.eventRuntime.cursor, 10);
      state.eventRuntime.enabled = feed?.enabled === true;
      if (!state.eventRuntime.enabled) return;
      if (typeof feed.cursor === "string" && feed.cursor) {
        state.eventRuntime.cursor = feed.cursor;
      }
      for (const event of Array.isArray(feed.events) ? feed.events : []) {
        await consumeCommittedEvent(event);
      }
    } catch (_) {
      // A failed signal read never creates a notice from stale or partial data.
    } finally {
      state.eventRuntime.inFlight = false;
      scheduleEventPoll();
    }
  }

  function startEventPolling() {
    if (state.eventRuntime.enabled === false) return;
    scheduleEventPoll(0);
  }

  function renderEventCue() {
    const cue = state.eventRuntime.cue;
    elements.eventCue?.classList.toggle("hidden", !cue);
    if (!cue) return;
    if (elements.eventCueSummary) {
      if (state.private) {
        elements.eventCueSummary.textContent = cue.kind === "availability_reconciliation"
          ? "The affected time, patient and appointment details are hidden while privacy mode is on."
          : "Time and appointment details are hidden while privacy mode is on.";
      } else if (cue.kind === "availability_reconciliation") {
        const summaries = {
          availability_changed: "Availability in this view changed. Reception One refreshed the current options.",
          selection_preserved: "Availability in this view changed, but your selected time is still available.",
          proposal_preserved: "Availability in this view changed, but your proposed time is still available.",
          selection_unavailable: "That time is no longer available. Reception One refreshed the remaining options.",
          proposal_unavailable: "That proposed time is no longer available. Reception One cleared the proposal and refreshed the remaining options."
        };
        elements.eventCueSummary.textContent = summaries[cue.outcome] || "Reception One refreshed current availability.";
      } else {
        elements.eventCueSummary.textContent = `${cue.oldWindow} changed to ${cue.newWindow}. The current projection now shows the committed time.`;
      }
    }
    if (elements.eventShow) {
      elements.eventShow.disabled = state.private;
      elements.eventShow.textContent = cue.kind === "availability_reconciliation"
        ? "Review current availability"
        : "Show changed appointment";
    }
    if (elements.announcer) {
      elements.announcer.textContent = "An appointment time in the current view changed. Reception One refreshed the view from the current Diary.";
      if (cue.kind === "availability_reconciliation") {
        elements.announcer.textContent = "Availability in the current view changed. Reception One refreshed the view from the current Diary.";
      }
    }
  }

  function dismissEventCue({ restoreFocus = true } = {}) {
    if (!state.eventRuntime.cue) return false;
    state.eventRuntime.cue = null;
    renderEventCue();
    if (restoreFocus) elements.request?.focus();
    return true;
  }

  function showEventContext() {
    const cue = state.eventRuntime.cue;
    if (!cue || state.private) return;
    if (cue.kind === "availability_reconciliation") {
      if (cue.contextProjection && state.current?.family === "proposal_review") {
        const projection = cue.contextSelection
          ? selectionProjection(
              cue.contextSelection,
              "touch",
              cue.contextProjection,
              {
                reason: "Staff chose to review freshly reconciled availability",
                changedDimensions: ["projection_family", "freshness"]
              }
            )
          : cue.contextProjection;
        state.selectedItem = cue.contextSelection || null;
        setProjection(projection, { newRoot: false, pushCurrent: true, focusCanvas: true });
      } else {
        elements.canvas?.focus();
      }
      dismissEventCue({ restoreFocus: false });
      return;
    }
    const row = [...elements.content.querySelectorAll("[data-appointment-id]")]
      .find(item => item.dataset.appointmentId === cue.aggregateId);
    if (!row) return;
    row.classList.add("meta-grid-event-target");
    row.scrollIntoView({ block: "center", inline: "nearest" });
    row.focus({ preventScroll: true });
    setTimeout(() => row.classList.remove("meta-grid-event-target"), 2200);
  }

  function snoozeEventCue() {
    state.eventRuntime.snoozedUntil = Date.now() + EVENT_SNOOZE_MS;
    dismissEventCue();
  }

  function muteEventCue() {
    state.eventRuntime.muted = true;
    dismissEventCue();
  }

  function goBack() {
    const previous = state.trail.pop();
    if (!previous) return;
    state.current = previous;
    state.selectedItem = previous.state === "selection_only"
      ? previous.items.find(item => item.selected) || null
      : null;
    state.proposalResult = previous.proposal_result || null;
    render();
    elements.canvas?.focus();
  }

  function openMetaGrid() {
    state.isOpen = true;
    document.body.classList.add("meta-grid-open");
    elements.host?.classList.remove("hidden");
    document.getElementById("bernie-review-panel")?.classList.add("hidden");
    if (!state.current) {
      buildOverview().then(projection => setProjection(projection, { newRoot: true, focusCanvas: false }));
    } else {
      render();
    }
    startEventPolling();
    setTimeout(() => elements.request?.focus(), 0);
  }

  function closeMetaGrid() {
    state.isOpen = false;
    stopEventPolling();
    state.eventRuntime.cue = null;
    state.selectedItem = null;
    state.proposalResult = null;
    if (state.current && ["selection_only", "proposal_not_committed"].includes(state.current.state)) {
      state.current = null;
      state.trail = [];
    }
    document.body.classList.remove("meta-grid-open");
    elements.host?.classList.add("hidden");
    document.getElementById("diary-grid-container")?.classList.remove("hidden");
    elements.launch?.focus();
  }

  function togglePrivacy(force) {
    const next = typeof force === "boolean" ? force : !state.private;
    state.private = next;
    elements.host?.classList.toggle("is-private", next);
    elements.privacyBanner?.classList.toggle("hidden", !next);
    elements.privacy?.setAttribute("aria-pressed", next ? "true" : "false");
    if (elements.privacy) elements.privacy.textContent = next ? "Show patient details" : "Hide patient details";
    if (next && elements.announcer) {
      elements.announcer.textContent = "Patient-sensitive details are hidden.";
    } else if (!next && state.current && elements.announcer) {
      const copy = stateCopy[state.current.state] || stateCopy.answer;
      elements.announcer.textContent = `${copy.label}. ${state.current.scope_summary}`;
    }
    renderEventCue();
  }

  function markInterrupted() {
    if (!state.isOpen || !state.current || state.current.state === "overview") return;
    togglePrivacy(true);
    if (state.current.state === "reconciliation_required") return;
    state.interrupted = true;
    state.current = {
      ...state.current,
      state: "reconciliation_required",
      items: (state.current.items || []).map(item => ({ ...item, selected: false })),
      freshness: {
        ...state.current.freshness,
        stale: true,
        reason: "Window focus or visibility changed; fresh read required before proposal work"
      },
      action_boundary: {
        posture: "none",
        appointment_write_authority: false,
        operational_command_available: false,
        required_backend_pattern: "Refresh the exact current scope before proposal preparation"
      }
    };
    state.selectedItem = null;
    state.proposalResult = null;
    state.trail = [];
    render();
  }

  function renderRootHistory() {
    elements.rootHistory.replaceChildren();
    if (state.recentRoots.length === 0) {
      elements.rootHistory.appendChild(createElement("li", "", "No earlier root view in this in-memory session."));
      return;
    }
    state.recentRoots.forEach(root => {
      const item = createElement("li");
      const button = createElement("button", "", root.label);
      button.type = "button";
      if (root.sensitive) button.classList.add("meta-grid-sensitive");
      button.addEventListener("click", () => submitRequest(root.request, { restore: true }));
      item.appendChild(button);
      elements.rootHistory.appendChild(item);
    });
  }

  function renderList(projection, className = "meta-grid-list") {
    const list = createElement("ol", className);
    if (projection.items.length === 0) {
      const empty = createElement("li", "meta-grid-empty-copy", "No results were returned for this exact scope. Broaden the time or return to the ordinary Diary.");
      list.appendChild(empty);
      elements.content.appendChild(list);
      return;
    }
    projection.items.forEach(item => {
      const row = createElement("li", className === "meta-grid-timeline" ? "meta-grid-timeline-item" : "meta-grid-item");
      if (item.kind === "appointment" && item.id) {
        row.dataset.appointmentId = String(item.id);
        row.tabIndex = -1;
      }
      if (item.sensitive) row.classList.add("meta-grid-sensitive");
      const heading = createElement("h3", "", item.date && projection.family === "patient_timeline"
        ? `${dateLabel(item.date)} · ${item.display}`
        : item.display);
      row.appendChild(heading);
      if (item.secondary) row.appendChild(createElement("p", "meta-grid-item-meta", item.secondary));
      if (item.tertiary) row.appendChild(createElement("p", "meta-grid-item-meta", item.tertiary));
      list.appendChild(row);
    });
    elements.content.appendChild(list);
  }

  function renderSlots(projection) {
    const list = createElement("div", "meta-grid-slot-list");
    if (projection.items.length === 0) {
      list.appendChild(createElement("p", "meta-grid-empty-copy", "No candidate slots were returned for this exact scope. Try another time or date."));
      elements.content.appendChild(list);
      return;
    }
    projection.items.forEach(item => {
      const button = createElement("button", "meta-grid-slot-button");
      button.type = "button";
      button.setAttribute("aria-pressed", item.selected ? "true" : "false");
      button.setAttribute("data-testid", "meta-grid-slot");
      button.setAttribute("aria-label", `${item.selected ? "Selected" : "Select"} ${item.display} with ${item.practitioner_display || "practitioner"}`);
      button.appendChild(createElement("strong", "", item.display));
      if (item.secondary) button.appendChild(createElement("span", "", item.secondary));
      if (item.tertiary) button.appendChild(createElement("span", "meta-grid-item-warning", item.tertiary));
      const activate = trigger => {
        state.selectedItem = item;
        setProjection(selectionProjection(item, trigger), { newRoot: false, pushCurrent: true });
      };
      button.addEventListener("click", () => activate("touch"));
      button.addEventListener("keydown", event => {
        if (!["Enter", " "].includes(event.key)) return;
        event.preventDefault();
        activate("keyboard");
      });
      list.appendChild(button);
    });
    elements.content.appendChild(list);
  }

  function renderComparison(projection) {
    const wrapper = createElement("div", "meta-grid-comparison");
    wrapper.appendChild(createElement("p", "meta-grid-comparison-basis", `${dateLabel(projection.scope.date_from)} · ${timeLabel(projection.scope.time_from)}–${timeLabel(projection.scope.time_to)} · ${projection.scope.duration_minutes} minutes · same location basis`));
    const groups = [...new Set(projection.items.map(item => item.comparison_group))];
    if (state.comparisonIndex >= groups.length) state.comparisonIndex = 0;
    groups.forEach((group, index) => {
      const lane = createElement("section", "meta-grid-comparison-lane");
      lane.dataset.active = index === state.comparisonIndex ? "true" : "false";
      lane.setAttribute("aria-label", `${group} availability`);
      lane.appendChild(createElement("h3", "", group));
      const items = projection.items.filter(item => item.comparison_group === group);
      if (items.length === 0) {
        lane.appendChild(createElement("p", "meta-grid-empty-copy", "No slots in this aligned window."));
      }
      items.forEach(item => {
        const button = createElement("button", "meta-grid-slot-button", item.display);
        button.type = "button";
        button.setAttribute("data-testid", "meta-grid-comparison-slot");
        button.setAttribute("aria-pressed", item.selected ? "true" : "false");
        const activate = trigger => {
          state.selectedItem = item;
          setProjection(selectionProjection(item, trigger), { newRoot: false, pushCurrent: true });
        };
        button.addEventListener("click", () => activate("touch"));
        button.addEventListener("keydown", event => {
          if (!["Enter", " "].includes(event.key)) return;
          event.preventDefault();
          activate("keyboard");
        });
        lane.appendChild(button);
      });
      wrapper.appendChild(lane);
    });
    const navigation = createElement("div", "meta-grid-comparison-nav");
    const previous = createElement("button", "", "Previous practitioner");
    previous.type = "button";
    previous.disabled = state.comparisonIndex === 0;
    previous.addEventListener("click", () => {
      state.comparisonIndex = Math.max(0, state.comparisonIndex - 1);
      render();
    });
    const next = createElement("button", "", "Next practitioner");
    next.type = "button";
    next.disabled = state.comparisonIndex >= groups.length - 1;
    next.addEventListener("click", () => {
      state.comparisonIndex = Math.min(groups.length - 1, state.comparisonIndex + 1);
      render();
    });
    navigation.append(previous, next);
    wrapper.appendChild(navigation);
    elements.content.appendChild(wrapper);
  }

  function renderClarification(projection) {
    const wrapper = createElement("div", "meta-grid-list");
    if (projection.items.length === 0) {
      wrapper.appendChild(createElement("p", "meta-grid-empty-copy", projection.transition.reason));
    }
    projection.items.forEach(item => {
      const card = createElement("div", "meta-grid-item meta-grid-sensitive");
      card.appendChild(createElement("h3", "", item.display));
      card.appendChild(createElement("p", "meta-grid-item-meta", item.secondary));
      wrapper.appendChild(card);
    });
    elements.content.appendChild(wrapper);
  }

  function renderProposal(projection) {
    const wrapper = createElement("div", "meta-grid-proposal");
    const item = projection.items[0];
    const summary = createElement("div", "meta-grid-proposal-summary meta-grid-sensitive");
    summary.appendChild(createElement("strong", "", item?.display || "Proposal details"));
    if (item?.secondary) summary.appendChild(createElement("span", "", item.secondary));
    if (item?.tertiary) summary.appendChild(createElement("span", "", item.tertiary));
    wrapper.appendChild(summary);
    wrapper.appendChild(createElement("p", "meta-grid-boundary-note", projection.action_boundary.operational_command_available
      ? "Continue only if you want to move into the existing booking review. That separate surface performs current backend checks and requires an explicit staff confirmation before any write."
      : "Authored synthetic fixture mode: no operational booking review or confirmation handoff is available, and no receipt can be produced."));
    elements.content.appendChild(wrapper);
  }

  function renderActions(projection) {
    elements.actions.replaceChildren();
    if (projection.state === "reconciliation_required") {
      const refresh = createElement("button", "meta-grid-primary", "Refresh current view");
      refresh.type = "button";
      refresh.setAttribute("data-testid", "meta-grid-refresh-current");
      refresh.addEventListener("click", refreshCurrent);
      elements.actions.appendChild(refresh);
      return;
    }
    if (projection.state === "selection_only") {
      const patient = patientForProjection(projection);
      const addPatient = createElement(
        "button",
        patient ? "meta-grid-primary meta-grid-sensitive" : "meta-grid-primary",
        patient ? `Prepare proposal for ${patient.display_name}` : "Add a patient to this slot"
      );
      addPatient.type = "button";
      addPatient.setAttribute("data-testid", patient ? "meta-grid-prepare-scoped-proposal" : "meta-grid-add-patient");
      addPatient.addEventListener("click", () => {
        if (patient) {
          submitRequest(`Prepare proposal for ${patient.display_name}`);
        } else {
          elements.request.placeholder = "For example: Add Margaret Thompson to the selected slot";
          elements.request.focus();
        }
      });
      elements.actions.appendChild(addPatient);
    }
    if (projection.state === "proposal_not_committed") {
      const handoff = createElement("button", "meta-grid-primary", "Continue to booking review");
      handoff.type = "button";
      handoff.setAttribute("data-testid", "meta-grid-proposal-handoff");
      handoff.disabled = !projection.action_boundary.operational_command_available;
      handoff.addEventListener("click", () => {
        if (!state.proposalResult || !bridge.handoffProposal(state.proposalResult)) return;
        state.selectedItem = null;
        state.proposalResult = null;
        bridge.showBookingReview();
      });
      elements.actions.appendChild(handoff);
    }
    const fullGrid = createElement("button", "", "Return to full Diary grid");
    fullGrid.type = "button";
    fullGrid.addEventListener("click", closeMetaGrid);
    elements.actions.appendChild(fullGrid);
  }

  function render() {
    const projection = state.current;
    if (!projection) return;
    const copy = stateCopy[projection.state] || stateCopy.answer;
    elements.scope.classList.toggle("meta-grid-sensitive", Boolean(projection.scope?.patient_ids?.length));
    elements.scope.textContent = projection.scope_summary;
    elements.omissions.textContent = projection.omissions.length
      ? `Deliberately left out: ${projection.omissions.join(" · ")}`
      : "No material scope omissions.";
    elements.freshness.textContent = `${projection.freshness.stale ? "Stale" : "As of"} ${new Date(projection.freshness.observed_at).toLocaleTimeString("en-AU", { hour: "numeric", minute: "2-digit" })} · ${projection.freshness.reason}`;
    elements.state.dataset.state = projection.state;
    elements.stateLabel.textContent = copy.label;
    elements.stateHeading.textContent = copy.heading;
    elements.stateExplanation.textContent = projection.state === "selection_only" && patientForProjection(projection)
      ? "Selection is staff input only. The resolved patient remains in scope for proposal preparation; nothing has been booked."
      : copy.explanation;
    elements.announcer.textContent = `${copy.label}. ${projection.scope_summary}`;
    elements.back.disabled = state.trail.length === 0;

    elements.content.replaceChildren();
    if (["availability_slots"].includes(projection.family)) {
      renderSlots(projection);
    } else if (projection.family === "aligned_comparison") {
      renderComparison(projection);
    } else if (projection.family === "clarification") {
      renderClarification(projection);
    } else if (projection.family === "proposal_review") {
      renderProposal(projection);
    } else if (projection.family === "patient_timeline") {
      renderList(projection, "meta-grid-timeline");
    } else if (projection.family === "ordinary_overview") {
      renderList(projection, "meta-grid-overview-list");
    } else {
      renderList(projection);
    }

    renderActions(projection);
    renderEventCue();
    elements.evidenceFamily.textContent = projection.family;
    elements.evidenceTrigger.textContent = projection.transition.trigger;
    elements.evidenceReason.textContent = projection.transition.reason;
    elements.evidenceChanges.textContent = projection.transition.changed_dimensions.join(" · ") || "No scope dimension changed";
    elements.evidenceSource.textContent = `${projection.freshness.source} · ${projection.evidence_mode}`;
    elements.evidenceBoundary.textContent = `${projection.action_boundary.posture}; appointment write authority: false`;
    renderRootHistory();
    togglePrivacy(state.private);
  }

  function updateVisualViewport() {
    if (!window.visualViewport || !elements.host) return;
    const inset = Math.max(0, window.innerHeight - window.visualViewport.height - window.visualViewport.offsetTop);
    elements.host.style.setProperty("--meta-grid-keyboard-inset", `${Math.round(inset)}px`);
  }

  function closeExplanation() {
    if (elements.evidence.hidden) return false;
    elements.evidence.hidden = true;
    elements.explain.setAttribute("aria-expanded", "false");
    elements.explain.focus();
    return true;
  }

  function init() {
    if (!elements.host || !elements.form || !elements.request) return;
    elements.launch?.addEventListener("click", openMetaGrid);
    elements.close?.addEventListener("click", closeMetaGrid);
    elements.back?.addEventListener("click", goBack);
    elements.overview?.addEventListener("click", async () => {
      const projection = await buildOverview("Ordinary overview", {
        rootIntentId: state.current?.root_intent_id,
        parentProjectionId: state.current?.projection_id,
        operation: "reset",
        trigger: "touch",
        reason: "User requested the compact ordinary overview",
        changedDimensions: ["projection_family", "selection_cleared"]
      });
      state.selectedItem = null;
      state.proposalResult = null;
      setProjection(projection, { newRoot: false, pushCurrent: true });
    });
    elements.explain?.addEventListener("click", () => {
      const showing = elements.evidence.hidden;
      elements.evidence.hidden = !showing;
      elements.explain.setAttribute("aria-expanded", showing ? "true" : "false");
      if (showing) elements.evidenceHeading.focus();
    });
    elements.privacy?.addEventListener("click", () => togglePrivacy());
    elements.form.addEventListener("submit", event => {
      event.preventDefault();
      submitRequest(elements.request.value);
    });
    elements.request.addEventListener("keydown", event => {
      if (event.key === "Enter" && !event.shiftKey && !event.ctrlKey && !event.altKey && !event.metaKey) {
        event.preventDefault();
        elements.form.requestSubmit();
      }
    });
    document.addEventListener("keydown", event => {
      if (event.key !== "Escape") return;
      if (dismissEventCue() || closeExplanation()) event.preventDefault();
    });
    elements.eventShow?.addEventListener("click", showEventContext);
    elements.eventDismiss?.addEventListener("click", () => dismissEventCue());
    elements.eventSnooze?.addEventListener("click", snoozeEventCue);
    elements.eventMute?.addEventListener("click", muteEventCue);
    elements.request.addEventListener("focus", () => {
      updateVisualViewport();
      setTimeout(() => elements.request.scrollIntoView({ block: "nearest", inline: "nearest" }), 0);
    });
    document.querySelectorAll("[data-meta-grid-request]").forEach(button => {
      button.addEventListener("click", () => submitRequest(button.getAttribute("data-meta-grid-request")));
    });
    window.addEventListener("blur", markInterrupted);
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stopEventPolling();
        markInterrupted();
      } else {
        startEventPolling();
      }
    });
    window.addEventListener("emr4:diary-read-complete", () => {
      if (state.current?.freshness?.stale) return;
      if (state.current?.family === "ordinary_overview" && state.isOpen) {
        buildOverview(state.current.root_request, {
          rootIntentId: state.current.root_intent_id,
          parentProjectionId: state.current.projection_id,
          operation: "reconcile",
          trigger: "system_freshness",
          reason: "Ordinary overview reconciled after Diary refresh",
          changedDimensions: ["freshness"]
        }).then(projection => setProjection(projection, { newRoot: false, pushCurrent: false, focusCanvas: false }));
      }
    });
    if (window.visualViewport) {
      window.visualViewport.addEventListener("resize", updateVisualViewport);
      window.visualViewport.addEventListener("scroll", updateVisualViewport);
    }
    updateVisualViewport();
    const params = new URLSearchParams(window.location.search);
    if (params.get("smoke") === "true" && params.get("meta_grid_acceptance") === "true") {
      elements.interruptionTest.classList.remove("hidden");
      elements.interruptionTest.addEventListener("click", markInterrupted);
    }
    if (params.get("smoke") === "true") bridge.setLaunchAvailable(true);
    if (params.get("meta_grid_open") === "true") {
      bridge.setLaunchAvailable(true);
      setTimeout(openMetaGrid, 0);
    }
  }

  if (window.Office && typeof window.Office.onReady === "function") {
    window.Office.onReady(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
