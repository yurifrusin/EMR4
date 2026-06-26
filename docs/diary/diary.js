// ═══════════════════════════════════════════════════════════
//  EMR Centaur — Diary Grid  v2
//  Launched via displayDialogAsync from the taskpane.
//  No patient required — diary is practice/day-scoped.
//  Auth token delivered via messageChild from taskpane after
//  this page sends { type:"ready" } via messageParent.
//  Falls back to localStorage token while waiting.
// ═══════════════════════════════════════════════════════════

const NGROK_URL   = "https://property-cinch-backfield.ngrok-free.dev";
const BACKEND_URL = (window.location.port === "3000")
  ? "http://localhost:8001"
  : window.location.hostname.includes("ngrok")
    ? window.location.origin
    : NGROK_URL;
const API_BASE = BACKEND_URL + "/api/v1";
const SLOT_HEIGHT_PX = 30;
const APPT_BLOCK_GAP_PX = 2;
const DRAG_START_THRESHOLD_PX = 3;
const MIN_TIME_INCREMENT_MINS = 5;
const GRIDLINE_SNAP_TOLERANCE_MINS = 3;

let activeAppointments = [];
let activeTypes = [];
let ahpraToPractitionerMap = {};
let waitingAreas = [];
const checkinDefaultCache = new Map();

const LOCATION_STORAGE_KEY = "emr4_diary_active_location";
const FLOW_PANEL_OPEN_KEY = "emr4_diary_flow_open";
let activeLocationId = localStorage.getItem(LOCATION_STORAGE_KEY) || null;
let locationOptionsLoaded = false;
let activeDragState = null;
const mockLocations = [
  { id: "loc-1", name: "Main Clinic" },
  { id: "loc-2", name: "North Branch" },
  { id: "loc-3", name: "East Specialty Suite" }
];

function isSmokeMode() {
  return new URLSearchParams(window.location.search).get("smoke") === "true";
}

// ─── DIARY TEMPLATE FALLBACK (embedded — mirrors diary_template.json at repo root)
// Breaks are per-column so each room can have different break windows.
const FALLBACK_TEMPLATE = {
  practice_name: "EMR4 Dev Clinic",
  slot_defaults: { start: "09:00", end: "17:00", interval_minutes: 15 },
  columns: [
    {
      room_label: "Room 1", assignment: "Dr Alex Shera",
      practitioner_ahpra: "MED0001234567", tint: null,
      breaks: [
        { label: "MORNING TEA", from: "10:45", to: "11:00" },
        { label: "LUNCH",       from: "13:00", to: "14:00" },
      ],
    },
    {
      room_label: "Room 2", assignment: "Nurse",
      practitioner_ahpra: null, tint: "FFFF99",
      breaks: [
        { label: "MORNING TEA", from: "10:45", to: "11:00" },
        { label: "LUNCH",       from: "13:00", to: "14:00" },
      ],
    },
    {
      room_label: "Room 3", assignment: "[Available]",
      practitioner_ahpra: null, tint: null,
      breaks: [
        { label: "MORNING TEA", from: "10:45", to: "11:00" },
        { label: "LUNCH",       from: "13:00", to: "14:00" },
      ],
    },
  ],
  footer: ["Messages:", "Phone Consultations:"],
};
let activeTemplate = cloneTemplate(FALLBACK_TEMPLATE);

// ─── SMOKE MODE MOCKS ──────────────────────────────────────
function getMockTemplate() {
  return {
    practice_name: "EMR4 Dev Clinic (Smoke Test)",
    slot_start: "09:00:00",
    slot_end: "17:00:00",
    slot_interval_minutes: 15,
    footer: ["Smoke Test Mode Active", "Click the headers to edit breaks.", "Phone Consultations: 0/3 today"],
    columns: [
      {
        room_label: "Room 1",
        assignment: "Dr Alex Shera",
        practitioner_ahpra: "MED0001234567",
        tint_hex: null,
        breaks: [
          { label: "MORNING TEA", from_time: "10:45:00", to_time: "11:00:00" },
          { label: "LUNCH",       from_time: "13:00:00", to_time: "14:00:00" }
        ]
      },
      {
        room_label: "Room 2",
        assignment: "Nurse",
        practitioner_ahpra: "MED999",
        tint_hex: "FFFF99",
        slot_interval_minutes: 10,
        breaks: [
          { label: "MORNING TEA", from_time: "10:45:00", to_time: "11:00:00" },
          { label: "BRUNCH",      from_time: "11:05:00", to_time: "11:25:00" },
          { label: "LUNCH",       from_time: "13:00:00", to_time: "14:00:00" }
        ]
      },
      {
        room_label: "Room 3",
        assignment: "[Available]",
        practitioner_ahpra: null,
        tint_hex: "FFC7C7",
        breaks: [
          { label: "LUNCH",       from_time: "13:00:00", to_time: "14:00:00" }
        ]
      }
    ]
  };
}

let mockAppointmentsCache = null;
function getMockAppointments() {
  if (!mockAppointmentsCache) {
    mockAppointmentsCache = [
    {
      id: "smoke-appt-1",
      start_time_local: "09:00",
      duration_minutes: 30,
      status: "Booked",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" },
      reason: "Hypertension follow-up",
      appointment_type_id: "smoke-type-1",
      location_id: "loc-1"
    },
    {
      id: "smoke-appt-2",
      start_time_local: "09:15",
      duration_minutes: 15,
      status: "Booked",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Billy", last_name: "Frusin", date_of_birth: "1988-11-12" },
      reason: "Ear ache",
      appointment_type_id: "smoke-type-2",
      location_id: "loc-1"
    },
    {
      id: "smoke-appt-3",
      start_time_local: "10:00",
      duration_minutes: 45,
      status: "Booked",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Margaret", last_name: "Thompson", date_of_birth: "1952-03-14" },
      reason: "Care Plan review",
      appointment_type_id: "smoke-type-1",
      location_id: "loc-2"
    },
    {
      id: "smoke-appt-4",
      start_time_local: "11:30",
      duration_minutes: 30,
      status: "Booked",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Jane", last_name: "Doe", date_of_birth: "1990-05-15" },
      reason: "Flu vaccine",
      appointment_type_id: "smoke-type-2",
      location_id: "loc-2"
    },
    {
      id: "smoke-appt-5",
      start_time_local: "11:45",
      duration_minutes: 15,
      status: "Arrived",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "John", last_name: "Smith", date_of_birth: "1978-08-20" },
      reason: "Script renewal",
      appointment_type_id: "smoke-type-1",
      location_id: "loc-1"
    },
    {
      id: "smoke-appt-6",
      start_time_local: "10:05",
      duration_minutes: 20,
      status: "Booked",
      practitioner: { ahpra_number: "MED999" },
      patient_name_provisional: "Nora Patel",
      patient: null,
      reason: "Dressing change",
      appointment_type_id: "smoke-type-2",
      location_id: "loc-1"
    },
    {
      id: "smoke-appt-7",
      start_time_local: "12:15",
      duration_minutes: 15,
      status: "Cancelled",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Alice", last_name: "Wonderland", date_of_birth: "1995-07-04" },
      reason: "Blood test check",
      cancellation_reason: "Patient had transport issues",
      appointment_type_id: "smoke-type-1",
      location_id: "loc-1"
    }
  ];
  }
  return mockAppointmentsCache;
}

function getMockTypes() {
  return [
    { id: "smoke-type-1", color_hex: "#0050a0" },
    { id: "smoke-type-2", color_hex: "#00B050" }
  ];
}

function getMockAuditEvents(apptId) {
  const baseDate = new Date();
  if (apptId === "smoke-appt-1") {
    return [
      {
        created_at: new Date(baseDate.getTime() - 1000 * 60 * 30).toISOString(),
        action: "status_change",
        status_before: "Booked",
        status_after: "Confirmed",
        confirmed_by_user_id: "Dr. Practice Owner"
      },
      {
        created_at: new Date(baseDate.getTime() - 1000 * 60 * 60).toISOString(),
        action: "create",
        status_after: "Booked",
        confirmed_by_user_id: "11111111-1111-1111-1111-111111111111"
      }
    ];
  } else if (apptId === "smoke-appt-7") {
    return [
      {
        created_at: new Date(baseDate.getTime() - 1000 * 60 * 15).toISOString(),
        action: "delete",
        status_before: "Booked",
        status_after: "Cancelled",
        cancellation_reason: "Patient had transport issues",
        confirmed_by_user_id: "Receptionist Sally"
      },
      {
        created_at: new Date(baseDate.getTime() - 1000 * 60 * 120).toISOString(),
        action: "create",
        status_after: "Booked",
        confirmed_by_user_id: "Receptionist Sally"
      }
    ];
  } else {
    return [
      {
        created_at: new Date(baseDate.getTime() - 1000 * 60 * 10).toISOString(),
        action: "create",
        status_after: "Booked",
        confirmed_by_user_id: "Receptionist Sally"
      }
    ];
  }
}

function formatAuditAction(action) {
  const labels = {
    create: "Created",
    update: "Updated",
    status_change: "Status Changed",
    delete: "Cancelled"
  };
  return labels[action] || String(action || "Event");
}

function formatAuditStatus(status) {
  if (!status) return "";
  const mapping = {
    "Booked": "Booked",
    "Confirmed": "Confirmed",
    "Arrived": "Arrived",
    "InConsult": "In Consult",
    "Completed": "Completed",
    "Cancelled": "Cancelled",
    "NoShow": "Did Not Attend (DNA)",
    "DNA": "Did Not Attend (DNA)"
  };
  return mapping[status] || String(status);
}

function formatAuditActor(evt) {
  const candidate = evt.confirmed_by_display ||
                    evt.confirmed_by_name ||
                    evt.confirmed_by_role ||
                    evt.confirmed_by ||
                    evt.confirmed_by_user_id;
  if (!candidate) return "";

  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (uuidRegex.test(candidate)) {
    return `Staff (${candidate.substring(0, 8)})`;
  }
  return candidate;
}

// ─── BREAK OVERRIDES (per-column, persisted to localStorage) ──────────────────
const BREAKS_KEY = "emr4_diary_breaks_v1";
let breakOverrides = {};   // { room_label: [{label, from, to}, ...] }

function loadBreakOverrides() {
  try { breakOverrides = JSON.parse(localStorage.getItem(BREAKS_KEY) || "{}"); }
  catch { breakOverrides = {}; }
}
function saveBreakOverrides() {
  localStorage.setItem(BREAKS_KEY, JSON.stringify(breakOverrides));
}
function getColumnBreaks(col) {
  return breakOverrides[col.room_label] ?? col.breaks ?? [];
}

// ─── STATE ────────────────────────────────────────────────
let token      = localStorage.getItem("emr4_token");
let currentUserRole = null;
let currentUserRoleToken = null;
let diaryDate  = new Date();
let refreshTimer = null;
const REFRESH_INTERVAL_MS = 60_000;
let editingColIndex = null;  // which column's breaks are being edited
let autoScrolledDateKey = null;

// ─── UTILITIES ────────────────────────────────────────────
function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/"/g, "&quot;")
    .replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function setStatus(msg) {
  const el = document.getElementById("diary-status");
  if (el) el.textContent = msg;
}
function showLoading(on) {
  const el = document.getElementById("diary-loading");
  if (el) el.classList.toggle("hidden", !on);
}
function showError(msg) {
  const err = document.getElementById("diary-error");
  if (err) { err.textContent = msg; err.classList.toggle("hidden", !msg); }
}

// ─── API FETCH ─────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const headers = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true",
    ...(opts.headers || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  if (res.status === 401) {
    setStatus("Session expired — reopen the taskpane to sign in again.");
    throw new Error("401 Unauthorized");
  }
  return res;
}

async function loadAuditHistory(apptId) {
  const listEl = document.getElementById("booking-audit-list");
  if (!listEl) return;
  listEl.innerHTML = '<li class="booking-audit-fallback">Loading audit history...</li>';

  try {
    let auditEvents = [];
    if (isSmokeMode()) {
      auditEvents = getMockAuditEvents(apptId);
    } else {
      const res = await apiFetch(`/appointments/${apptId}/audit`);
      if (res.status === 200) {
        auditEvents = await res.json();
      } else if (res.status === 404 || res.status === 501) {
        listEl.innerHTML = '<li class="booking-audit-fallback">Audit history not supported by backend</li>';
        return;
      } else {
        listEl.innerHTML = `<li class="booking-audit-fallback">Error loading audit history (${res.status})</li>`;
        return;
      }
    }

    if (!auditEvents || auditEvents.length === 0) {
      listEl.innerHTML = '<li class="booking-audit-fallback">No audit history found</li>';
      return;
    }

    listEl.innerHTML = "";
    const sorted = [...auditEvents].sort((a, b) => {
      const dateA = new Date(a.created_at || 0);
      const dateB = new Date(b.created_at || 0);
      return dateB - dateA;
    });

    sorted.forEach(evt => {
      const li = document.createElement("li");
      li.className = "booking-audit-item";

      const timeStr = evt.created_at ? new Date(evt.created_at).toLocaleString() : "Unknown Time";
      const actionStr = formatAuditAction(evt.action);
      const actor = formatAuditActor(evt);
      let userStr = "";
      if (actor) {
        if (actor.toLowerCase().startsWith("by ")) {
          userStr = actor;
        } else {
          userStr = `by ${actor}`;
        }
      }
      
      let details = [];
      const statusTarget = evt.status_target || evt.status_after;
      if (evt.status_before && evt.status_after && evt.status_before !== evt.status_after) {
        details.push(`Changed from <strong>${escHtml(formatAuditStatus(evt.status_before))}</strong> to <strong>${escHtml(formatAuditStatus(evt.status_after))}</strong>`);
      } else if (statusTarget) {
        details.push(`Status set to: <strong>${escHtml(formatAuditStatus(statusTarget))}</strong>`);
      }
      if (evt.cancellation_reason) {
        details.push(`Cancellation Reason: <strong>${escHtml(evt.cancellation_reason)}</strong>`);
      }
      if (evt.confirmed_with_warnings) {
        details.push(`Confirmed with warnings`);
      }
      if (evt.warning_codes) {
        const warnings = Array.isArray(evt.warning_codes) ? evt.warning_codes : [evt.warning_codes];
        if (warnings.length > 0) {
          details.push(`<span class="booking-audit-warnings">Warnings: [${warnings.map(w => escHtml(String(w))).join(", ")}]</span>`);
        }
      }

      li.innerHTML = `
        <div class="booking-audit-meta">
          <span>${escHtml(actionStr)} ${escHtml(userStr)}</span>
          <span class="booking-audit-timestamp">${escHtml(timeStr)}</span>
        </div>
        ${details.length > 0 ? `<div class="booking-audit-details">${details.join(" | ")}</div>` : ""}
      `;
      listEl.appendChild(li);
    });
  } catch (err) {
    console.error("Error loading audit history", err);
    listEl.innerHTML = '<li class="booking-audit-fallback">Audit history not available</li>';
  }
}

function getRoleFromToken(authToken = token) {
  if (!authToken) return null;
  try {
    const parts = authToken.split(".");
    if (parts.length !== 3) return null;
    const payload = JSON.parse(atob(parts[1]));
    return payload.role || payload.user_role || null;
  } catch (_) {
    return null;
  }
}

function isAdminRole(role) {
  const normalized = String(role || "").replace(/[\s_-]/g, "").toLowerCase();
  return normalized === "admin" || normalized === "practiceowner";
}

function updateAdminButtonVisibility() {
  const adminBtn = document.getElementById("btn-admin-panel");
  if (!adminBtn) return;
  adminBtn.classList.remove("hidden");
}

async function ensureCurrentUserRole() {
  if (isSmokeMode()) {
    currentUserRole = "Admin";
    currentUserRoleToken = token;
    updateAdminButtonVisibility();
    return;
  }
  if (!token) {
    currentUserRole = null;
    currentUserRoleToken = null;
    updateAdminButtonVisibility();
    return;
  }

  const decodedRole = getRoleFromToken(token);
  if (decodedRole) {
    currentUserRole = decodedRole;
    currentUserRoleToken = token;
    updateAdminButtonVisibility();
    return;
  }

  if (currentUserRoleToken === token && currentUserRole) {
    updateAdminButtonVisibility();
    return;
  }

  try {
    const res = await apiFetch("/auth/me");
    if (res.ok) {
      const user = await res.json();
      currentUserRole = user.role || null;
      currentUserRoleToken = token;
    }
  } catch (_) {
    currentUserRole = null;
    currentUserRoleToken = null;
  }
  updateAdminButtonVisibility();
}

function cloneTemplate(template) {
  return JSON.parse(JSON.stringify(template));
}

function normalizeTime(value) {
  const match = String(value || "").match(/^(\d{1,2}):(\d{2})/);
  if (!match) return null;
  const h = Number(match[1]);
  const m = Number(match[2]);
  if (!Number.isInteger(h) || !Number.isInteger(m) || h < 0 || h > 23 || m < 0 || m > 59) {
    return null;
  }
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

function normalizeTint(value) {
  const raw = String(value || "").trim().replace(/^#/, "");
  return /^[0-9a-fA-F]{6}$/.test(raw) ? raw.toUpperCase() : null;
}

function normalizeTemplate(raw) {
  if (!raw || typeof raw !== "object") {
    throw new Error("Diary template response was empty");
  }

  const slotStart = normalizeTime(raw.slot_start ?? raw.slot_defaults?.start);
  const slotEnd = normalizeTime(raw.slot_end ?? raw.slot_defaults?.end);
  const interval = Number(raw.slot_interval_minutes ?? raw.slot_defaults?.interval_minutes);
  if (!slotStart || !slotEnd || !Number.isFinite(interval) || interval <= 0 || toMins(slotEnd) <= toMins(slotStart)) {
    throw new Error("Diary template slot defaults are invalid");
  }

  const columns = (Array.isArray(raw.columns) ? raw.columns : [])
    .map(col => {
      const roomLabel = String(col?.room_label || "").trim();
      const rawColumnInterval = Number(col?.slot_interval_minutes ?? col?.slot_interval);
      const columnInterval = Number.isFinite(rawColumnInterval)
        && rawColumnInterval >= MIN_TIME_INCREMENT_MINS
        && rawColumnInterval % MIN_TIME_INCREMENT_MINS === 0
        ? rawColumnInterval
        : null;
      const breaks = (Array.isArray(col?.breaks) ? col.breaks : [])
        .map(b => ({
          label: String(b?.label || "BREAK").trim() || "BREAK",
          from: normalizeTime(b?.from_time ?? b?.from),
          to: normalizeTime(b?.to_time ?? b?.to),
        }))
        .filter(b => b.from && b.to && toMins(b.to) > toMins(b.from));

      return {
        room_label: roomLabel,
        assignment: String(col?.assignment || "").trim(),
        practitioner_id: col?.practitioner_id ? String(col.practitioner_id).trim() : null,
        practitioner_ahpra: col?.practitioner_ahpra ? String(col.practitioner_ahpra).trim() : null,
        tint: normalizeTint(col?.tint_hex ?? col?.tint),
        slot_interval_minutes: columnInterval,
        breaks,
      };
    })
    .filter(col => col.room_label);

  if (!columns.length) {
    throw new Error("Diary template has no usable columns");
  }

  return {
    practice_name: String(raw.practice_name || FALLBACK_TEMPLATE.practice_name || "EMR4 Diary").trim(),
    slot_defaults: {
      start: slotStart,
      end: slotEnd,
      interval_minutes: interval,
    },
    columns,
    footer: Array.isArray(raw.footer) ? raw.footer.map(item => String(item)).filter(Boolean) : [],
  };
}

async function loadDiaryTemplate() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("smoke") === "true") {
    return normalizeTemplate(getMockTemplate());
  }
  try {
    const locationQuery = activeLocationId ? `?location_id=${encodeURIComponent(activeLocationId)}` : "";
    const res = await apiFetch(`/diary/template${locationQuery}`);
    if (!res.ok) throw new Error(`Template: ${res.status} ${await res.text()}`);
    return normalizeTemplate(await res.json());
  } catch (e) {
    console.warn("Using embedded diary template fallback:", e);
    return cloneTemplate(FALLBACK_TEMPLATE);
  }
}

function setActiveTemplate(template) {
  activeTemplate = template;
  const pnEl = document.getElementById("diary-practice-name");
  if (pnEl) pnEl.textContent = template.practice_name || "";
  renderFooter(template);
}

function renderFooter(template) {
  let footer = document.getElementById("diary-footer");
  const items = Array.isArray(template.footer) ? template.footer.filter(Boolean) : [];
  if (!items.length) {
    footer?.remove();
    return;
  }
  if (!footer) {
    footer = document.createElement("div");
    footer.id = "diary-footer";
    document.getElementById("diary-grid-container")?.appendChild(footer);
  }
  footer.textContent = items.join("   ");
}

// ─── TIME HELPERS ──────────────────────────────────────────
function toMins(t) {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}
function fromMins(m) {
  return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
}

function localDateKey(dateValue) {
  const yyyy = dateValue.getFullYear();
  const mm = String(dateValue.getMonth() + 1).padStart(2, "0");
  const dd = String(dateValue.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function timeRangeLabel(startMins, endMins) {
  return `${fromMins(startMins)}-${fromMins(endMins)}`;
}

function appointmentCrossesBreak(ahpra, timeVal, duration) {
  if (!activeTemplate || !activeTemplate.columns) return false;
  const col = activeTemplate.columns.find(c => c.practitioner_ahpra === ahpra);
  const colBreaks = col ? getColumnBreaks(col) : [];
  if (!colBreaks || colBreaks.length === 0) return false;

  const apptStartMins = toMins(timeVal);
  const apptEndMins = apptStartMins + duration;

  for (const b of colBreaks) {
    if (!b.from || !b.to) continue;
    const breakStart = toMins(b.from);
    const breakEnd = toMins(b.to);
    if (apptStartMins < breakEnd && apptEndMins > breakStart) {
      return true;
    }
  }
  return false;
}

function clampMins(value, min, max) {
  return Math.max(min, Math.min(value, max));
}

function snapBookingStartMins(rawMins, start, end, dayStartMins, intervalMins) {
  const latestStart = Math.max(start, end - MIN_TIME_INCREMENT_MINS);
  const nearestGridline = dayStartMins + Math.round((rawMins - dayStartMins) / intervalMins) * intervalMins;

  if (
    nearestGridline >= start
    && nearestGridline <= latestStart
    && Math.abs(rawMins - nearestGridline) <= GRIDLINE_SNAP_TOLERANCE_MINS
  ) {
    return nearestGridline;
  }

  const roundedOffset = Math.floor((rawMins - start) / MIN_TIME_INCREMENT_MINS) * MIN_TIME_INCREMENT_MINS;
  return clampMins(start + roundedOffset, start, latestStart);
}

function bookingGapMinsFromEvent(gap, start, end, dayStartMins, intervalMins, clientY) {
  const rect = gap.getBoundingClientRect();
  const offsetY = Math.max(0, Math.min(clientY - rect.top, rect.height));
  const rawMins = start + (offsetY * intervalMins / SLOT_HEIGHT_PX);
  return snapBookingStartMins(rawMins, start, end, dayStartMins, intervalMins);
}

function isBlockingAppointment(appt) {
  return !["Cancelled", "NoShow", "DNA"].includes(appt.status);
}

function shouldRenderAppointment(appt) {
  return appt.status !== "Cancelled";
}

function isOnMajorGrid(mins, template) {
  const interval = template.slot_defaults.interval_minutes || 15;
  return (mins - toMins(template.slot_defaults.start)) % interval === 0;
}

function isSameClinicDay(a, b) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function nowMins() {
  const now = new Date();
  return now.getHours() * 60 + now.getMinutes();
}

function markerTopPx(mins, template) {
  const dayStartMins = toMins(template.slot_defaults.start);
  const intervalMins = template.slot_defaults.interval_minutes || 15;
  return (mins - dayStartMins) * (SLOT_HEIGHT_PX / intervalMins);
}

function shouldAutoScrollToNow(template) {
  if (!isSameClinicDay(diaryDate, new Date())) return false;
  const todayKey = diaryDate.toISOString().slice(0, 10);
  if (autoScrolledDateKey === todayKey) return false;
  const mins = nowMins();
  return mins >= toMins(template.slot_defaults.start) && mins <= toMins(template.slot_defaults.end);
}

function scrollToTime(mins, template) {
  const body = document.getElementById("diary-grid-container") || document.getElementById("diary-body");
  if (!body) return;
  const top = Math.max(0, markerTopPx(mins, template) - SLOT_HEIGHT_PX * 2);
  body.scrollTo({ top, behavior: "smooth" });
}

function jumpToNow() {
  const today = new Date();
  diaryDate = today;
  updateDateLabel();
  loadDiary(false, { scrollToNow: true });
}

// Extract HH:MM for diary placement. Prefer the canonical clinic-local field;
// fall back to legacy ISO start_time for older API responses.
function apptTimeKey(apptOrIso) {
  if (apptOrIso && typeof apptOrIso === "object" && apptOrIso.start_time_local) {
    const m = String(apptOrIso.start_time_local).match(/^(\d{2}):(\d{2})/);
    return m ? `${m[1]}:${m[2]}` : null;
  }
  const isoStr = typeof apptOrIso === "string" ? apptOrIso : apptOrIso?.start_time;
  if (!isoStr) return null;
  const m = isoStr.match(/T(\d{2}):(\d{2})/);
  return m ? `${m[1]}:${m[2]}` : null;
}

function apptDurationMins(appt, fallbackMins) {
  const explicit = Number(appt?.duration_minutes);
  if (Number.isFinite(explicit) && explicit > 0) {
    return explicit;
  }

  if (appt?.start_time && appt?.end_time) {
    const start = Date.parse(appt.start_time);
    const end = Date.parse(appt.end_time);
    const diff = (end - start) / 60000;
    if (Number.isFinite(diff) && diff > 0) {
      return diff;
    }
  }

  return fallbackMins;
}

// ─── SLOT GENERATION ───────────────────────────────────────
// Generates every time slot from start to end.
// Breaks are per-column and are handled at the cell level.
function generateSlots(template) {
  const { start, end, interval_minutes } = template.slot_defaults;
  const slots = [];
  let cur = toMins(start);
  const endMins = toMins(end);
  while (cur < endMins) {
    slots.push(fromMins(cur));
    cur += interval_minutes;
  }
  return slots;
}

// ─── APPOINTMENT LOOKUP ────────────────────────────────────
// Returns { ahpra: { "09:00": [appt, ...] } }
function buildApptLookup(appointments) {
  const lookup = {};
  appointments.forEach(a => {
    if (!shouldRenderAppointment(a)) return;
    const ahpra = a.practitioner?.ahpra_number || "__none__";
    if (!lookup[ahpra]) lookup[ahpra] = {};
    const key = apptTimeKey(a);
    if (!key) return;
    if (!lookup[ahpra][key]) lookup[ahpra][key] = [];
    lookup[ahpra][key].push(a);
  });
  return lookup;
}

// ─── LIFECYCLE CLASS ───────────────────────────────────────
function apptClass(status) {
  const mappedStatus = status === "Confirmed" ? "Booked" : status;
  switch (mappedStatus) {
    case "Confirmed":  return "appt-confirmed";
    case "Arrived":    return "appt-arrived";
    case "InConsult":  return "appt-inconsult";
    case "Completed":  return "appt-completed";
    case "Cancelled":  return "appt-cancelled";
    case "NoShow":     return "appt-noshow";
    case "DNA":        return "appt-dna";
    default:           return "appt-booked";
  }
}

function getStatusLabel(status) {
  const mappedStatus = status === "Confirmed" ? "Booked" : status;
  switch (mappedStatus) {
    case "Confirmed":  return "Confirmed";
    case "Arrived":    return "Arrived";
    case "InConsult":  return "Consult";
    case "Completed":  return "Done";
    case "Cancelled":  return "CXL";
    case "NoShow":     return "No Show";
    case "DNA":        return "DNA";
    default:           return mappedStatus || "Booked";
  }
}

function provisionalPatientName(appt) {
  return appt.patient_name_provisional || appt.provisional_name || "";
}

function isPatientIdentityUnconfirmed(appt) {
  return !!provisionalPatientName(appt) || !appt.patient_id || !appt.patient;
}

function isClinicalProgressStatus(status) {
  return ["Arrived", "InConsult", "Completed"].includes(status);
}

function showIdentityProgressDialog(appt, newStatus) {
  return new Promise(resolve => {
    const patientName = provisionalPatientName(appt) || "this provisional patient";
    const targetLabel = getStatusLabel(newStatus);
    let step = 1;

    const overlay = document.createElement("div");
    overlay.className = "identity-confirm-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-labelledby", "identity-confirm-title");

    const panel = document.createElement("div");
    panel.className = "identity-confirm-panel";

    const title = document.createElement("h2");
    title.id = "identity-confirm-title";
    title.className = "identity-confirm-title";

    const body = document.createElement("p");
    body.className = "identity-confirm-body";

    const actions = document.createElement("div");
    actions.className = "identity-confirm-actions";

    const cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.className = "btn-secondary";

    const continueBtn = document.createElement("button");
    continueBtn.type = "button";
    continueBtn.className = "btn-danger";

    const close = result => {
      document.removeEventListener("keydown", onKeyDown);
      overlay.remove();
      resolve(result);
    };

    const renderStep = () => {
      actions.innerHTML = "";
      if (step === 1) {
        title.textContent = "Unconfirmed patient identity";
        body.textContent = `This booking is not linked to a confirmed patient record. Continue changing ${patientName} to ${targetLabel}?`;
        cancelBtn.textContent = "Cancel";
        continueBtn.textContent = "Continue";
        cancelBtn.onclick = () => close(false);
        continueBtn.onclick = () => {
          step = 2;
          renderStep();
        };
      } else {
        title.textContent = "Identity not confirmed in EMR";
        body.textContent = "The patient has not been identified in our records. If you continue, the booking will be marked IDENTITY UNCONFIRMED.";
        cancelBtn.textContent = "Go Back";
        continueBtn.textContent = "Mark Identity Unconfirmed";
        cancelBtn.onclick = () => {
          step = 1;
          renderStep();
        };
        continueBtn.onclick = () => close(true);
      }
      actions.append(cancelBtn, continueBtn);
      setTimeout(() => cancelBtn.focus(), 0);
    };

    const onKeyDown = event => {
      if (event.key === "Escape") close(false);
    };

    panel.append(title, body, actions);
    overlay.appendChild(panel);
    document.body.appendChild(overlay);
    document.addEventListener("keydown", onKeyDown);
    renderStep();
  });
}

async function confirmUnidentifiedProgress(appt, newStatus) {
  if (!isPatientIdentityUnconfirmed(appt) || !isClinicalProgressStatus(newStatus)) {
    return true;
  }
  return await showIdentityProgressDialog(appt, newStatus);
}

function appendNowMarker(container, template, showLabel = false) {
  if (!isSameClinicDay(diaryDate, new Date())) return;
  const mins = nowMins();
  if (mins < toMins(template.slot_defaults.start) || mins > toMins(template.slot_defaults.end)) return;

  const marker = document.createElement("div");
  marker.className = showLabel ? "now-marker now-marker-time" : "now-marker";
  marker.style.top = markerTopPx(mins, template) + "px";
  marker.title = `Current time ${fromMins(mins)}`;
  if (showLabel) {
    const label = document.createElement("span");
    label.className = "now-marker-label";
    label.textContent = fromMins(mins);
    marker.appendChild(label);
  }
  container.appendChild(marker);
}

function appendTimeEdges(el, startMins, endMins) {
  const startEdge = document.createElement("span");
  startEdge.className = "time-edge time-edge-start";
  startEdge.dataset.timeLabel = `Start ${fromMins(startMins)}`;
  startEdge.setAttribute("aria-hidden", "true");
  el.appendChild(startEdge);

  const endEdge = document.createElement("span");
  endEdge.className = "time-edge time-edge-end";
  endEdge.dataset.timeLabel = `End ${fromMins(endMins)}`;
  endEdge.setAttribute("aria-hidden", "true");
  el.appendChild(endEdge);
}

// ─── RENDER GRID ───────────────────────────────────────────
function renderGrid(template, slots, apptLookup, typeMap, occupied) {
  const grid = document.getElementById("diary-grid");
  grid.innerHTML = "";

  const columns = template.columns;
  const dayStartMins = toMins(template.slot_defaults.start);
  const dayEndMins = toMins(template.slot_defaults.end);
  const intervalMins = template.slot_defaults.interval_minutes || 15;

  // ── 1. Create Time Column ──────────────────────────────────
  const timeCol = document.createElement("div");
  timeCol.className = "diary-time-column";

  const timeHeader = document.createElement("div");
  timeHeader.className = "diary-column-header";
  timeHeader.textContent = "TIME";
  timeCol.appendChild(timeHeader);

  const timeBody = document.createElement("div");
  timeBody.className = "diary-column-body";

  slots.forEach(slotTime => {
    const label = document.createElement("div");
    label.className = "time-slot-label";
    label.textContent = slotTime;
    timeBody.appendChild(label);
  });
  appendNowMarker(timeBody, template, true);
  timeCol.appendChild(timeBody);
  grid.appendChild(timeCol);

  // ── 2. Create Practitioner/Room Columns ─────────────────────
  columns.forEach((col, colIdx) => {
    const column = document.createElement("div");
    column.className = "diary-column" + (col.practitioner_ahpra ? "" : " col-non-bookable");

    // Header
    const th = document.createElement("div");
    th.className = "diary-column-header";
    if (col.tint) th.style.backgroundColor = `#${col.tint}`;

    const editBtn = document.createElement("button");
    editBtn.className = "break-edit-btn";
    editBtn.title = "Edit breaks for this column";
    editBtn.textContent = "✎";
    editBtn.onclick = e => { e.stopPropagation(); openBreakModal(colIdx); };

    const nameDiv = document.createElement("div");
    nameDiv.className = "col-assignment";
    nameDiv.textContent = col.assignment;

    const roomDiv = document.createElement("div");
    roomDiv.className = "col-room-label";
    const columnInterval = col.slot_interval_minutes || intervalMins;
    roomDiv.textContent = columnInterval === intervalMins
      ? col.room_label
      : `${col.room_label} - ${columnInterval} min`;
    roomDiv.title = `Slot cadence: ${columnInterval} minutes`;

    th.appendChild(nameDiv);
    th.appendChild(roomDiv);
    th.appendChild(editBtn);
    column.appendChild(th);

    // Body
    const columnBody = document.createElement("div");
    columnBody.className = "diary-column-body";
    columnBody.dataset.practitionerAhpra = col.practitioner_ahpra || "";
    columnBody.dataset.colIdx = colIdx;
    if (col.tint) {
      columnBody.style.backgroundColor = `#${col.tint}11`;
    }

    // 2a. Background slots (grid lines + empty chevrons)
    slots.forEach(slotTime => {
      const slotMins = toMins(slotTime);
      const slotDiv = document.createElement("div");
      slotDiv.className = "slot-bg";

      const colBreaks = getColumnBreaks(col);
      const hasBreak = colBreaks.some(
        b => slotMins >= toMins(b.from) && slotMins < toMins(b.to)
      );
      const hasAppt = col.practitioner_ahpra && occupied[col.practitioner_ahpra]?.has(slotTime);

      if (!hasBreak && !hasAppt && col.practitioner_ahpra) {
        const empty = document.createElement("span");
        empty.className = "slot-empty";
        empty.textContent = "»";
        slotDiv.appendChild(empty);

        slotDiv.style.cursor = "pointer";
        slotDiv.title = `Book appointment at ${slotTime} in ${col.room_label}`;
        slotDiv.onclick = (e) => {
          e.stopPropagation();
          openBookingModalForCreate(col, slotTime);
        };
      }

      columnBody.appendChild(slotDiv);
    });

    // 2b. Breaks (absolute positioned)
    const colBreaks = getColumnBreaks(col);
    colBreaks.forEach(b => {
      const bStart = toMins(b.from);
      const bEnd = toMins(b.to);
      const isIrregular = !isOnMajorGrid(bStart, template) || !isOnMajorGrid(bEnd, template);

      const topPx = (bStart - dayStartMins) * (SLOT_HEIGHT_PX / intervalMins);
      const heightPx = (bEnd - bStart) * (SLOT_HEIGHT_PX / intervalMins);

      const breakEl = document.createElement("div");
      breakEl.className = isIrregular ? "break-block break-irregular" : "break-block";
      breakEl.style.top = topPx + "px";
      breakEl.style.height = heightPx + "px";
      breakEl.title = `${b.label || "BREAK"} ${timeRangeLabel(bStart, bEnd)}`;

      if (col.tint) {
        breakEl.style.backgroundColor = `#${col.tint}88`;
      }

      const labelSpan = document.createElement("span");
      labelSpan.className = "break-block-label";
      labelSpan.textContent = b.label || "BREAK";
      breakEl.appendChild(labelSpan);
      if (isIrregular) {
        appendTimeEdges(breakEl, bStart, bEnd);
      }

      columnBody.appendChild(breakEl);
    });

    // 2c. Appointments (absolute positioned by actual time/duration)
    const colAppts = [];
    if (col.practitioner_ahpra && apptLookup[col.practitioner_ahpra]) {
      const practitionerApptObj = apptLookup[col.practitioner_ahpra];
      Object.keys(practitionerApptObj).forEach(timeKey => {
        const apptsAtTime = practitionerApptObj[timeKey] || [];
        colAppts.push(...apptsAtTime);
      });
    }

    // Sort by start time, then duration descending
    colAppts.sort((x, y) => {
      const tX = toMins(apptTimeKey(x));
      const tY = toMins(apptTimeKey(y));
      if (tX !== tY) return tX - tY;

      const dX = apptDurationMins(x, intervalMins);
      const dY = apptDurationMins(y, intervalMins);
      return dY - dX;
    });

    // Transparent hit targets make small free gaps bookable even inside a
    // larger visible grid row. Appointment cards render above these targets.
    const blockers = [];
    colBreaks.forEach(b => {
      blockers.push({ start: toMins(b.from), end: toMins(b.to) });
    });
    colAppts.forEach(a => {
      if (!isBlockingAppointment(a)) return;
      const start = toMins(apptTimeKey(a));
      const duration = Math.max(apptDurationMins(a, intervalMins), MIN_TIME_INCREMENT_MINS);
      blockers.push({ start, end: start + duration });
    });
    blockers.sort((a, b) => a.start - b.start || a.end - b.end);

    let gapStart = dayStartMins;
    blockers.forEach(blocker => {
      const start = Math.max(blocker.start, dayStartMins);
      const end = Math.min(blocker.end, dayEndMins);
      if (start - gapStart >= MIN_TIME_INCREMENT_MINS) {
        appendBookingGapTarget(columnBody, col, gapStart, start, dayStartMins, intervalMins);
      }
      if (end > gapStart) gapStart = end;
    });
    if (dayEndMins - gapStart >= MIN_TIME_INCREMENT_MINS) {
      appendBookingGapTarget(columnBody, col, gapStart, dayEndMins, dayStartMins, intervalMins);
    }

    // Render appointments
    colAppts.forEach(a => {
      const start = toMins(apptTimeKey(a));
      const duration = Math.max(apptDurationMins(a, intervalMins), MIN_TIME_INCREMENT_MINS);
      const end = start + duration;
      const isIrregular = !isOnMajorGrid(start, template) || !isOnMajorGrid(end, template);

      const topPx = (start - dayStartMins) * (SLOT_HEIGHT_PX / intervalMins);
      const heightPx = duration * (SLOT_HEIGHT_PX / intervalMins);
      const visualHeightPx = Math.max(heightPx - APPT_BLOCK_GAP_PX, 10);

      const cls = apptClass(a.status);
      const color = a.appointment_type?.color_hex || (a.appointment_type_id ? typeMap[a.appointment_type_id] : null);

      const span = document.createElement("span");
      span.className = `appt ${cls}`;
      if (duration < intervalMins) {
        span.classList.add("appt-short");
      }
      span.dataset.id = a.id;

      const provisionalName = provisionalPatientName(a);
      const isProvisional = isPatientIdentityUnconfirmed(a);
      span.classList.add(isProvisional ? "appt-provisional" : "appt-linked");
      if (isProvisional && isClinicalProgressStatus(a.status)) {
        span.classList.add("appt-identity-unconfirmed");
      }

      if (color) {
        span.dataset.color = color;
        span.style.setProperty("--appt-color", color);
      }

      span.style.position = "absolute";
      span.style.top = (topPx + 1) + "px";
      span.style.left = "1px";
      span.style.right = "1px";
      span.style.zIndex = "10";
      span.style.height = visualHeightPx + "px";
      span.style.setProperty("--appt-height", visualHeightPx + "px");
      span.tabIndex = 0;

      const patientName = provisionalName || (a.patient ? `${a.patient.first_name} ${a.patient.last_name}`.trim() : "") || "Unknown Patient";
      const timeLabel = timeRangeLabel(start, end);
      span.setAttribute("role", "button");
      span.setAttribute("aria-label", a.reason ? `${patientName}. ${timeLabel}. ${a.reason}` : `${patientName}. ${timeLabel}`);
      span.title = a.reason ? `${patientName} - ${timeLabel} - ${a.reason}` : `${patientName} - ${timeLabel}`;

      const headerDiv = document.createElement("div");
      headerDiv.className = "appt-header";

      const name = document.createElement("span");
      name.className = "appt-name";
      if (isProvisional) {
        name.innerHTML = `<span class="appt-prov-icon" title="Provisional Patient">📝</span> ${escHtml(patientName)}`;
      } else {
        name.innerHTML = `<span class="appt-link-icon" title="Linked Patient Record">🔗</span> ${escHtml(patientName)}`;
      }
      headerDiv.appendChild(name);

      const displayStatus = a.status === "Confirmed" ? "Booked" : a.status;
      const statusLower = (displayStatus || "booked").toLowerCase();
      const statusBadge = document.createElement("span");
      statusBadge.className = `appt-status-badge badge-${statusLower}`;
      statusBadge.textContent = getStatusLabel(displayStatus);
      headerDiv.appendChild(statusBadge);

      if (!isProvisional) {
        const linkedBadge = document.createElement("span");
        linkedBadge.className = "appt-linked-badge";
        linkedBadge.title = "Linked patient record";
        linkedBadge.textContent = "✓";
        headerDiv.appendChild(linkedBadge);
      }

      span.appendChild(headerDiv);

      if (isIrregular) {
        appendTimeEdges(span, start, end);
      }
      if (a.reason && heightPx >= 20) {
        const reason = document.createElement("span");
        reason.className = "appt-reason";
        reason.textContent = a.reason;
        span.appendChild(reason);
      }
      if (isProvisional && isClinicalProgressStatus(a.status) && heightPx >= 32) {
        const warning = document.createElement("span");
        warning.className = "appt-identity-warning";
        warning.textContent = "IDENTITY UNCONFIRMED";
        span.appendChild(warning);
      }

      // Inline compact status changer
      const statusChanger = document.createElement("div");
      statusChanger.className = "appt-status-changer";
      statusChanger.addEventListener("click", e => {
        e.stopPropagation();
      });

      const selectLabel = document.createElement("label");
      selectLabel.className = "status-select-label";
      const statusSelectId = `status-select-${a.id}`;
      selectLabel.htmlFor = statusSelectId;
      selectLabel.textContent = "Status: ";
      statusChanger.appendChild(selectLabel);

      const statusSelect = document.createElement("select");
      statusSelect.className = "status-select";
      statusSelect.id = statusSelectId;
      statusSelect.ariaLabel = "Change appointment status";

      const selectOptions = [
        { value: "Booked", label: "Booked" },
        { value: "Arrived", label: "Arrived" },
        { value: "InConsult", label: "In Consult" },
        { value: "Completed", label: "Done" },
        { value: "Cancelled", label: "Cancelled" },
        { value: "NoShow", label: "No Show" },
        { value: "DNA", label: "DNA" }
      ];

      if (a.status === "Confirmed") {
        selectOptions.splice(1, 0, { value: "Confirmed", label: "Confirmed" });
      }

      selectOptions.forEach(optData => {
        const opt = document.createElement("option");
        opt.value = optData.value;
        opt.textContent = optData.label;
        const currentMappedStatus = a.status === "Confirmed" ? "Booked" : a.status;
        if (currentMappedStatus === optData.value) {
          opt.selected = true;
        }
        statusSelect.appendChild(opt);
      });

      statusSelect.addEventListener("change", async (e) => {
        const newStatus = e.target.value;
        if (newStatus === a.status) return;
        await setAppointmentStatus(a, newStatus, statusSelect);
      });

      statusSelect.addEventListener("keydown", async e => {
        if (!e.altKey || !["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) return;
        e.preventDefault();
        e.stopPropagation();
        let deltaStart = 0;
        let deltaDuration = 0;
        if (e.key === "ArrowUp") {
          deltaStart = -15;
        } else if (e.key === "ArrowDown") {
          deltaStart = 15;
        } else if (e.key === "ArrowLeft") {
          deltaDuration = -15;
        } else if (e.key === "ArrowRight") {
          deltaDuration = 15;
        }
        await handleMoveResize(a, deltaStart, deltaDuration, col);
      }, true);

      statusChanger.appendChild(statusSelect);

      if (isProvisional) {
        const linkBtn = document.createElement("button");
        linkBtn.type = "button";
        linkBtn.className = "btn-link-appt";
        linkBtn.textContent = "Link patient";
        linkBtn.onclick = (e) => {
          e.stopPropagation();
          openBookingModalForPatientLink(a);
        };
        statusChanger.appendChild(linkBtn);
      }

      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "btn-edit-appt";
      editBtn.textContent = "✎ Edit";
      editBtn.onclick = (e) => {
        e.stopPropagation();
        openBookingModalForEdit(a);
      };
      statusChanger.appendChild(editBtn);

      span.appendChild(statusChanger);

      // Create top/bottom resize handles
      const topHandle = document.createElement("div");
      topHandle.className = "appt-resize-handle appt-resize-handle-top";
      const bottomHandle = document.createElement("div");
      bottomHandle.className = "appt-resize-handle appt-resize-handle-bottom";
      span.appendChild(topHandle);
      span.appendChild(bottomHandle);

      span.addEventListener("mousedown", e => {
        if (e.target.closest(".appt-status-changer, button, select, a, input, textarea")) {
          return;
        }
        if (e.target === topHandle) {
          initDragOrResize(e, a, span, "resize-top", col);
        } else if (e.target === bottomHandle) {
          initDragOrResize(e, a, span, "resize-bottom", col);
        } else {
          initDragOrResize(e, a, span, "drag", col);
        }
      });

      span.addEventListener("click", e => {
        e.stopPropagation();
        const wasActive = span.classList.contains("appt-active");
        document.querySelectorAll(".appt-active").forEach(el => el.classList.remove("appt-active"));
        if (!wasActive) span.classList.add("appt-active");
      });

      span.addEventListener("keydown", async e => {
        if (e.altKey && ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
          e.preventDefault();
          e.stopPropagation();
          let deltaStart = 0;
          let deltaDuration = 0;
          if (e.key === "ArrowUp") {
            deltaStart = -15;
          } else if (e.key === "ArrowDown") {
            deltaStart = 15;
          } else if (e.key === "ArrowLeft") {
            deltaDuration = -15;
          } else if (e.key === "ArrowRight") {
            deltaDuration = 15;
          }
          await handleMoveResize(a, deltaStart, deltaDuration, col);
          return;
        }
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          span.click();
        }
      }, true);

      columnBody.appendChild(span);
    });

    appendNowMarker(columnBody, template);
    column.appendChild(columnBody);
    grid.appendChild(column);
  });

  const container = document.getElementById("diary-grid-container") || document.getElementById("diary-grid");
  container.classList.remove("hidden");
  showLoading(false);
  showError("");
}

function appendBookingGapTarget(columnBody, col, start, end, dayStartMins, intervalMins) {
  if (!col.practitioner_ahpra) return;

  const topPx = (start - dayStartMins) * (SLOT_HEIGHT_PX / intervalMins);
  const heightPx = Math.max((end - start) * (SLOT_HEIGHT_PX / intervalMins), 6);
  const gap = document.createElement("button");
  gap.type = "button";
  gap.className = "booking-gap-target";
  gap.style.top = `${topPx}px`;
  gap.style.height = `${heightPx}px`;
  gap.setAttribute("aria-label", `Book appointment at ${fromMins(start)} in ${col.room_label}`);

  const previewLine = document.createElement("span");
  previewLine.className = "booking-gap-preview-line";
  const previewChip = document.createElement("span");
  previewChip.className = "booking-gap-preview-chip";
  previewChip.setAttribute("aria-hidden", "true");
  gap.append(previewLine, previewChip);

  const updatePreview = mins => {
    const y = (mins - start) * (SLOT_HEIGHT_PX / intervalMins);
    gap.style.setProperty("--booking-preview-y", `${y}px`);
    previewChip.textContent = fromMins(mins);
    gap.classList.add("is-previewing");
    gap.setAttribute("aria-label", `Book appointment at ${fromMins(mins)} in ${col.room_label}`);
  };

  gap.addEventListener("pointermove", e => {
    updatePreview(bookingGapMinsFromEvent(gap, start, end, dayStartMins, intervalMins, e.clientY));
  });
  gap.addEventListener("pointerleave", () => gap.classList.remove("is-previewing"));
  gap.addEventListener("focus", () => updatePreview(start));
  gap.addEventListener("blur", () => gap.classList.remove("is-previewing"));

  gap.addEventListener("click", e => {
    e.stopPropagation();
    const clickedMins = bookingGapMinsFromEvent(gap, start, end, dayStartMins, intervalMins, e.clientY);
    openBookingModalForCreate(col, fromMins(clickedMins));
  });
  columnBody.appendChild(gap);
}

// ─── BREAK EDIT MODAL ─────────────────────────────────────
function openBreakModal(colIdx) {
  editingColIndex = colIdx;
  const col = activeTemplate.columns[colIdx];
  document.getElementById("break-modal-title").textContent =
    `Breaks — ${col.assignment} (${col.room_label})`;

  renderBreakRows(getColumnBreaks(col));
  document.getElementById("break-modal").classList.remove("hidden");
}

function closeBreakModal() {
  document.getElementById("break-modal").classList.add("hidden");
  editingColIndex = null;
}

function renderBreakRows(breaks) {
  const body = document.getElementById("break-modal-body");
  body.innerHTML = "";
  (breaks || []).forEach((b, i) => {
    body.appendChild(makeBreakRow(i, b.from, b.to, b.label));
  });
}

function makeBreakRow(idx, from, to, label) {
  const row = document.createElement("div");
  row.className = "break-row-edit";
  row.dataset.idx = idx;
  row.innerHTML = `
    <input class="br-from" type="time" value="${escHtml(from || "")}" title="From" />
    <span class="br-sep">–</span>
    <input class="br-to"   type="time" value="${escHtml(to   || "")}" title="To" />
    <input class="br-label" type="text" value="${escHtml(label || "")}" placeholder="Label (e.g. LUNCH)" />
    <button class="br-del" title="Remove">✕</button>`;
  row.querySelector(".br-del").onclick = () => row.remove();
  return row;
}

function addBreakRow() {
  const body = document.getElementById("break-modal-body");
  const idx  = body.querySelectorAll(".break-row-edit").length;
  body.appendChild(makeBreakRow(idx, "", "", ""));
}

function saveBreaks() {
  if (editingColIndex === null) return;
  const col = activeTemplate.columns[editingColIndex];
  const rows = document.querySelectorAll("#break-modal-body .break-row-edit");
  const breaks = [];
  rows.forEach(row => {
    const from  = row.querySelector(".br-from").value.trim();
    const to    = row.querySelector(".br-to").value.trim();
    const label = row.querySelector(".br-label").value.trim();
    if (from && to) breaks.push({ from, to, label: label || "BREAK" });
  });
  breakOverrides[col.room_label] = breaks;
  saveBreakOverrides();
  closeBreakModal();
  loadDiary(); // re-render with new breaks
}

// ─── LOAD DIARY ────────────────────────────────────────────
async function loadDiary(silent = false, options = {}) {
  const urlParams = new URLSearchParams(window.location.search);
  const isSmokeMode = urlParams.get("smoke") === "true";

  if (!token && !isSmokeMode) {
    setStatus("Waiting for auth token…");
    return;
  }

  await ensureCurrentUserRole();

  if (!silent) {
    showLoading(true);
    const container = document.getElementById("diary-grid-container") || document.getElementById("diary-grid");
    container.classList.add("hidden");
  }
  showError("");

  const dayStart = new Date(diaryDate);
  dayStart.setHours(0, 0, 0, 0);
  const dayEnd = new Date(dayStart);
  dayEnd.setHours(23, 59, 59, 999);

  const yyyy = diaryDate.getFullYear();
  const mm = String(diaryDate.getMonth() + 1).padStart(2, "0");
  const dd = String(diaryDate.getDate()).padStart(2, "0");
  const dateStr = `${yyyy}-${mm}-${dd}`;

  await initLocationSelector();

  const apptParams = new URLSearchParams({
    date_from: dayStart.toISOString(),
    date_to: dayEnd.toISOString(),
  });
  if (!isSmokeMode && activeLocationId) {
    apptParams.set("location_id", activeLocationId);
  }
  const locationQuery = !isSmokeMode && activeLocationId
    ? `&location_id=${encodeURIComponent(activeLocationId)}`
    : "";

  try {
    let template, appointments, types, rosterEntries = [], fetchedWaitingAreas = [];

    if (isSmokeMode) {
      template = normalizeTemplate(getMockTemplate());
      appointments = getMockAppointments().filter(a => {
        const apptLocId = a.location_id || "loc-1";
        return apptLocId === activeLocationId;
      });
      types = getMockTypes();
      waitingAreas = getMockWaitingAreas().filter(wa => !activeLocationId || wa.location_id === activeLocationId);
    } else {
      const [templateRes, apptRes, typeRes, rosterRes, waitingAreasRes] = await Promise.all([
        loadDiaryTemplate(),
        apiFetch(`/appointments?${apptParams.toString()}`),
        apiFetch(`/appointments/types`),
        apiFetch(`/diary/roster?date=${dateStr}${locationQuery}`).catch(err => {
          if (err && err.message === "401 Unauthorized") {
            throw err;
          }
          console.warn("Roster fetch failed:", err);
          return null;
        }),
        apiFetch(`/diary/waiting-areas${activeLocationId ? `?location_id=${encodeURIComponent(activeLocationId)}` : ""}`).catch(err => {
          if (err && err.message === "401 Unauthorized") {
            throw err;
          }
          console.warn("Waiting areas fetch failed:", err);
          return null;
        })
      ]);
      template = templateRes;
      if (!apptRes.ok) throw new Error(`Appointments: ${apptRes.status} ${await apptRes.text()}`);
      if (!typeRes.ok) throw new Error(`Types: ${typeRes.status} ${await typeRes.text()}`);
      appointments = await apptRes.json();
      types        = await typeRes.json();
      if (waitingAreasRes && waitingAreasRes.ok) {
        fetchedWaitingAreas = await waitingAreasRes.json();
      }
      waitingAreas = Array.isArray(fetchedWaitingAreas) ? fetchedWaitingAreas : [];

      rosterEntries = [];
      if (rosterRes && rosterRes.ok) {
        try {
          const rosterData = await rosterRes.json();
          rosterEntries = rosterData?.entries || [];
        } catch (err) {
          console.warn("Failed to parse roster JSON:", err);
        }
      }

      if (rosterEntries.length > 0) {
        const ahpraToAssignment = {};
        template.columns.forEach(col => {
          if (col.practitioner_ahpra && col.assignment) {
            ahpraToAssignment[col.practitioner_ahpra] = col.assignment;
          }
        });

        const mergedColumns = rosterEntries.map(entry => {
          const tmplCol = template.columns.find(
            col => col.room_label.toLowerCase() === entry.room_name.toLowerCase()
          );

          const hasRosterAssignment = !!entry.label || !!entry.practitioner_ahpra || !!entry.practitioner_id;

          if (!hasRosterAssignment && tmplCol) {
            // Reuse matching template column attributes if roster is empty/unassigned for this room
            return {
              room_label: entry.room_name,
              assignment: tmplCol.assignment || "[Available]",
              practitioner_id: tmplCol.practitioner_id || null,
              practitioner_ahpra: tmplCol.practitioner_ahpra || null,
              tint: tmplCol.tint,
              slot_interval_minutes: tmplCol.slot_interval_minutes,
              breaks: tmplCol.breaks || []
            };
          }

          let assignment = "[Available]";
          if (entry.label) {
            assignment = entry.label;
          } else if (entry.practitioner_ahpra) {
            assignment = ahpraToAssignment[entry.practitioner_ahpra] || entry.practitioner_ahpra;
          }

          return {
            room_label: entry.room_name,
            assignment: assignment,
            practitioner_id: entry.practitioner_id || null,
            practitioner_ahpra: entry.practitioner_ahpra || null,
            tint: tmplCol ? tmplCol.tint : null,
            slot_interval_minutes: tmplCol ? tmplCol.slot_interval_minutes : null,
            breaks: tmplCol ? tmplCol.breaks : []
          };
        });

        template.columns = mergedColumns;
      }
    }

    // Update global cache variables
    activeAppointments = appointments;
    activeTypes = types;
    ahpraToPractitionerMap = {};

    // Scan template/roster columns first so blank days can still create bookings.
    template.columns.forEach(col => {
      if (col.practitioner_ahpra && col.practitioner_id) {
        ahpraToPractitionerMap[col.practitioner_ahpra] = {
          id: col.practitioner_id,
          first_name: "",
          last_name: ""
        };
      }
    });

    // Scan appointments to populate richer practitioner AHPRA -> ID map
    appointments.forEach(a => {
      if (a.practitioner && a.practitioner.ahpra_number) {
        ahpraToPractitionerMap[a.practitioner.ahpra_number] = {
          id: a.practitioner.id,
          first_name: a.practitioner.first_name,
          last_name: a.practitioner.last_name
        };
      }
    });

    // Scan roster entries
    if (rosterEntries) {
      rosterEntries.forEach(entry => {
        if (entry.practitioner_ahpra && entry.practitioner_id) {
          if (!ahpraToPractitionerMap[entry.practitioner_ahpra]) {
            ahpraToPractitionerMap[entry.practitioner_ahpra] = {
              id: entry.practitioner_id,
              first_name: "",
              last_name: ""
            };
          }
        }
      });
    }

    // Set mock practitioner IDs in smoke mode
    if (isSmokeMode) {
      ahpraToPractitionerMap["MED0001234567"] = {
        id: "smoke-prac-1",
        first_name: "Alex",
        last_name: "Shera"
      };
      ahpraToPractitionerMap["MED999"] = {
        id: "smoke-prac-2",
        first_name: "Nurse",
        last_name: "Staff"
      };
    }

    // Assign practitioner_id to template columns
    template.columns.forEach(col => {
      if (col.practitioner_ahpra) {
        col.practitioner_id = col.practitioner_id || ahpraToPractitionerMap[col.practitioner_ahpra]?.id || null;
      } else {
        col.practitioner_id = null;
      }
    });

    setActiveTemplate(template);

    const typeMap    = {};
    types.forEach(t => { typeMap[t.id] = t.color_hex; });

    const slots      = generateSlots(activeTemplate);
    const visibleAppointments = appointments.filter(shouldRenderAppointment);
    const apptLookup = buildApptLookup(visibleAppointments);

    // Build occupied lookup to hide chevrons in spanned slots
    const occupied = {};
    visibleAppointments.forEach(a => {
      const ahpra = a.practitioner?.ahpra_number;
      if (!ahpra) return;
      if (!occupied[ahpra]) occupied[ahpra] = new Set();
      const startKey = apptTimeKey(a);
      if (!startKey) return;
      const startMins = toMins(startKey);
      const duration = apptDurationMins(a, activeTemplate.slot_defaults.interval_minutes);
      const endMins = startMins + duration;

      slots.forEach(slotTime => {
        const slotStart = toMins(slotTime);
        const slotEnd = slotStart + activeTemplate.slot_defaults.interval_minutes;
        if (startMins < slotEnd && endMins > slotStart) {
          occupied[ahpra].add(slotTime);
        }
      });
    });

    const autoScroll = shouldAutoScrollToNow(activeTemplate);
    renderGrid(activeTemplate, slots, apptLookup, typeMap, occupied);

    // Load today's appointments for flow sidebar in background
    await loadTodayAppointments();

    if (options.scrollToApptId) {
      setTimeout(() => scrollToAppointment(options.scrollToApptId), 100);
    } else if (options.scrollToNow || autoScroll) {
      scrollToTime(nowMins(), activeTemplate);
      autoScrolledDateKey = diaryDate.toISOString().slice(0, 10);
    }

    // Refresh flow panel if it's currently open, else update badge count
    if (localStorage.getItem(FLOW_PANEL_OPEN_KEY) === "true") {
      setFlowPanelVisibility(true, false);
      await updateFlowPanel();
    } else {
      setFlowPanelVisibility(false, false);
      updateFlowBadgeCount();
    }

    const total = visibleAppointments.length;
    setStatus(`${total} appointment${total !== 1 ? "s" : ""} · ${formatDateLabel(diaryDate)}${isSmokeMode ? " [SMOKE MODE]" : ""}`);
  } catch (e) {
    if (!silent) {
      showLoading(false);
      showError("Failed to load diary: " + (e.message || String(e)));
    }
    setStatus("Refresh failed — " + (e.message || String(e)));
  }
}

// ─── DATE NAVIGATION ───────────────────────────────────────
function formatDateLabel(d) {
  return d.toLocaleDateString("en-AU", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });
}
function updateDateLabel() {
  document.getElementById("diary-date-label").textContent = formatDateLabel(diaryDate);
  const yyyy = diaryDate.getFullYear();
  const mm = String(diaryDate.getMonth() + 1).padStart(2, "0");
  const dd = String(diaryDate.getDate()).padStart(2, "0");
  const picker = document.getElementById("diary-date-picker");
  if (picker) picker.value = `${yyyy}-${mm}-${dd}`;
}
function shiftDay(delta) {
  diaryDate = new Date(diaryDate);
  diaryDate.setDate(diaryDate.getDate() + delta);
  updateDateLabel();
  loadDiary();
}

// ─── AUTO-REFRESH ──────────────────────────────────────────
function scheduleRefresh() {
  if (refreshTimer) clearTimeout(refreshTimer);
  refreshTimer = setTimeout(() => { loadDiary(true); scheduleRefresh(); }, REFRESH_INTERVAL_MS);
}
function doRefresh() { loadDiary(); scheduleRefresh(); }

function focusDiaryWindow() {
  try { window.focus(); } catch (_) {}
  try {
    if (window.screen?.availWidth && window.screen?.availHeight) {
      window.moveTo(0, 0);
      window.resizeTo(window.screen.availWidth, window.screen.availHeight);
    }
  } catch (_) {}
}

// ─── INIT ──────────────────────────────────────────────────
Office.onReady(() => {
  loadBreakOverrides();

  setActiveTemplate(activeTemplate);

  document.getElementById("btn-prev-day").onclick  = () => shiftDay(-1);
  document.getElementById("btn-next-day").onclick  = () => shiftDay(+1);
  document.getElementById("btn-today").onclick     = () => {
    diaryDate = new Date(); updateDateLabel(); loadDiary();
  };
  document.getElementById("btn-now").onclick       = jumpToNow;
  document.getElementById("btn-refresh").onclick   = doRefresh;
  document.getElementById("btn-modal-add").onclick = addBreakRow;
  document.getElementById("btn-modal-save").onclick = saveBreaks;
  document.getElementById("btn-modal-close").onclick = closeBreakModal;

  document.getElementById("btn-booking-close").onclick = closeBookingModal;
  document.getElementById("btn-booking-delete").onclick = deleteBooking;
  document.getElementById("btn-booking-save").onclick = saveBooking;

  // Reset proposal confirmation on field change
  ["booking-practitioner", "booking-type", "booking-date", "booking-time", "booking-duration", "booking-status"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", resetProposalConfirmation);
  });
  ["booking-date", "booking-time", "booking-duration", "booking-reason"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", resetProposalConfirmation);
  });

  const bookingForm = document.getElementById("booking-form");
  if (bookingForm) {
    bookingForm.addEventListener("submit", e => {
      e.preventDefault();
      saveBooking();
    });
    bookingForm.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
        e.preventDefault();
        saveBooking();
      }
    });
  }

  const bookingTypeSelect = document.getElementById("booking-type");
  if (bookingTypeSelect) {
    bookingTypeSelect.addEventListener("change", e => {
      const typeId = e.target.value;
      if (typeId && activeTypes) {
        const found = activeTypes.find(t => t.id === typeId);
        if (found && found.default_duration) {
          document.getElementById("booking-duration").value = found.default_duration;
        }
      }
    });
  }

  document.getElementById("booking-modal").addEventListener("click", e => {
    if (e.target === e.currentTarget) closeBookingModal();
  });

  const auditHeader = document.getElementById("booking-audit-header");
  if (auditHeader) {
    auditHeader.addEventListener("click", () => {
      const content = document.getElementById("booking-audit-content");
      const icon = document.getElementById("booking-audit-toggle-icon");
      if (content && icon) {
        const isCollapsed = content.classList.contains("hidden");
        if (isCollapsed) {
          content.classList.remove("hidden");
          icon.classList.add("expanded");
          icon.textContent = "▼";
        } else {
          content.classList.add("hidden");
          icon.classList.remove("expanded");
          icon.textContent = "▶";
        }
      }
    });
  }

  let searchTimeout = null;
  const patientSearchInput = document.getElementById("booking-patient-search");
  if (patientSearchInput) {
    patientSearchInput.addEventListener("input", e => {
      const val = e.target.value.trim();
      clearTimeout(searchTimeout);
      if (val.length < 2) {
        document.getElementById("patient-search-results").innerHTML = "";
        document.getElementById("patient-search-results").classList.add("hidden");
        return;
      }

      searchTimeout = setTimeout(async () => {
        try {
          let results = [];
          if (isSmokeMode()) {
            results = searchMockPatients(val);
          } else {
            const res = await apiFetch(`/patients/search?q=${encodeURIComponent(val)}`);
            if (!res.ok) throw new Error("Search failed");
            results = await res.json();
          }
          renderSearchResults(results);
        } catch (err) {
          console.error(err);
        }
      }, 250);
    });
  }

  const btnClearPatient = document.getElementById("btn-clear-patient");
  if (btnClearPatient) {
    btnClearPatient.onclick = () => {
      selectedPatient = null;
      provisionalName = null;
      document.getElementById("selected-patient-display").classList.add("hidden");
      document.getElementById("btn-link-patient").classList.add("hidden");
      document.getElementById("booking-patient-search").value = "";
      document.getElementById("booking-patient-search").classList.remove("hidden");
      document.getElementById("booking-patient-search").focus();
      resetProposalConfirmation();
    };
  }

  const btnLinkPatient = document.getElementById("btn-link-patient");
  if (btnLinkPatient) {
    btnLinkPatient.onclick = () => {
      const search = document.getElementById("booking-patient-search");
      search.value = "";
      search.classList.remove("hidden");
      document.getElementById("patient-search-results").classList.add("hidden");
      search.focus();
    };
  }

  const dateWrapper = document.querySelector(".date-picker-wrapper");
  const datePicker = document.getElementById("diary-date-picker");
  if (dateWrapper && datePicker) {
    dateWrapper.onclick = () => {
      try {
        datePicker.showPicker();
      } catch (_) {
        datePicker.click();
      }
    };
    datePicker.onchange = (e) => {
      if (e.target.value) {
        const parts = e.target.value.split("-");
        diaryDate = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
        updateDateLabel();
        loadDiary();
      }
    };
  }

  document.getElementById("diary-grid").addEventListener("click", () => {
    document.querySelectorAll(".appt-active").forEach(el => el.classList.remove("appt-active"));
  });

  // Close modal on backdrop click
  document.getElementById("break-modal").addEventListener("click", e => {
    if (e.target === e.currentTarget) closeBreakModal();
  });

  // Patient Flow toggle hooks
  const btnToggleFlow = document.getElementById("btn-toggle-flow");
  if (btnToggleFlow) btnToggleFlow.onclick = toggleFlowPanel;

  const btnCloseFlow = document.getElementById("btn-close-flow");
  if (btnCloseFlow) btnCloseFlow.onclick = closeFlowPanel;

  const flowOpen = localStorage.getItem(FLOW_PANEL_OPEN_KEY);
  if (flowOpen === "true") {
    setFlowPanelVisibility(true, false);
  } else {
    setFlowPanelVisibility(false, false);
  }

  // Collapsible section title listeners
  document.querySelectorAll(".flow-section-title").forEach(titleEl => {
    titleEl.addEventListener("click", () => {
      const sectionEl = titleEl.closest(".flow-section");
      if (sectionEl) {
        toggleSectionCollapse(sectionEl.id);
      }
    });
  });

  restoreSectionCollapseStates();

  initLocationSelector();

  updateDateLabel();

  if (Office.context?.ui?.addHandlerAsync) {
    Office.context.ui.addHandlerAsync(
      Office.EventType.DialogParentMessageReceived,
      arg => {
        try {
          const msg = JSON.parse(arg.message);
          if (msg.type === "auth" && msg.token) {
            token = msg.token;
            currentUserRole = getRoleFromToken(token);
            currentUserRoleToken = currentUserRole ? token : null;
            localStorage.setItem("emr4_token", token);
            updateAdminButtonVisibility();
            loadDiary();
            scheduleRefresh();
          } else if (msg.type === "focus") {
            focusDiaryWindow();
          }
        } catch (_) {}
      }
    );
  }

  initAdminPanel();
  try { Office.context?.ui?.messageParent(JSON.stringify({ type: "ready" })); } catch (_) {}

  const urlParams = new URLSearchParams(window.location.search);
  const isSmoke = urlParams.get("smoke") === "true";
  if (token || isSmoke) { loadDiary(); scheduleRefresh(); }
});

// ─── BOOKING MODAL LOGIC ───────────────────────────────────
let selectedPatient = null;
let provisionalName = null;
let editingAppointmentId = null;

function searchMockPatients(q) {
  const query = q.toLowerCase();
  const allMocks = [
    { id: "smoke-pat-1", first_name: "Margaret", last_name: "Thompson", date_of_birth: "1955-03-24", medicare_number: "12345678901" },
    { id: "smoke-pat-2", first_name: "Billy", last_name: "Frusin", date_of_birth: "1988-11-12", medicare_number: "22345678902" },
    { id: "smoke-pat-3", first_name: "Jane", last_name: "Doe", date_of_birth: "1990-05-15", medicare_number: "32345678903" },
    { id: "smoke-pat-4", first_name: "John", last_name: "Smith", date_of_birth: "1978-08-20", medicare_number: "42345678904" },
    { id: "smoke-pat-5", first_name: "Nora", last_name: "Patel", date_of_birth: "1982-04-10", medicare_number: "52345678905" }
  ];
  return allMocks.filter(p =>
    p.first_name.toLowerCase().includes(query) ||
    p.last_name.toLowerCase().includes(query) ||
    p.medicare_number.includes(query)
  );
}

function prepareStatusDropdown(currentStatus) {
  const select = document.getElementById("booking-status");
  select.innerHTML = "";

  const options = [
    { value: "Booked", label: "Booked" },
    { value: "Arrived", label: "Arrived" },
    { value: "InConsult", label: "In Consult" },
    { value: "Completed", label: "Done" },
    { value: "Cancelled", label: "Cancelled" },
    { value: "NoShow", label: "No Show" },
    { value: "DNA", label: "DNA" }
  ];

  options.forEach(opt => {
    const el = document.createElement("option");
    el.value = opt.value;
    el.textContent = opt.label;
    select.appendChild(el);
  });
}

function openBookingModalForCreate(col, slotTime) {
  resetProposalConfirmation();
  editingAppointmentId = null;
  selectedPatient = null;
  provisionalName = null;
  const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
  if (cancelReasonContainer) cancelReasonContainer.classList.add("hidden");
  const cancelReasonInput = document.getElementById("booking-cancel-reason");
  if (cancelReasonInput) cancelReasonInput.value = "";
  document.getElementById("booking-modal-title").textContent = "New Appointment";
  document.getElementById("btn-booking-delete").classList.add("hidden");

  document.getElementById("booking-patient-search").value = "";
  document.getElementById("booking-patient-search").classList.remove("hidden");
  document.getElementById("patient-search-results").innerHTML = "";
  document.getElementById("patient-search-results").classList.add("hidden");
  document.getElementById("selected-patient-display").classList.add("hidden");
  document.getElementById("btn-link-patient").classList.add("hidden");

  populatePractitionerDropdown(col.practitioner_ahpra);
  populateTypeDropdown();

  const yyyy = diaryDate.getFullYear();
  const mm = String(diaryDate.getMonth() + 1).padStart(2, "0");
  const dd = String(diaryDate.getDate()).padStart(2, "0");
  document.getElementById("booking-date").value = `${yyyy}-${mm}-${dd}`;
  document.getElementById("booking-time").value = slotTime;

  const defaultDuration = col.slot_interval_minutes || activeTemplate.slot_defaults.interval_minutes || 15;
  document.getElementById("booking-duration").value = defaultDuration;

  prepareStatusDropdown("Booked");
  document.getElementById("booking-status").value = "Booked";
  document.getElementById("booking-reason").value = "";
  document.getElementById("booking-error").classList.add("hidden");

  const auditSection = document.getElementById("booking-audit-section");
  if (auditSection) auditSection.classList.add("hidden");

  document.getElementById("booking-modal").classList.remove("hidden");
}

function openBookingModalForEdit(appt) {
  resetProposalConfirmation();
  editingAppointmentId = appt.id;
  const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
  if (cancelReasonContainer) cancelReasonContainer.classList.add("hidden");
  const cancelReasonInput = document.getElementById("booking-cancel-reason");
  if (cancelReasonInput) cancelReasonInput.value = "";

  const provisionalPatientName = appt.patient_name_provisional || appt.provisional_name || "";
  const isProvisional = !!provisionalPatientName || !appt.patient_id || !appt.patient;

  if (isProvisional) {
    selectedPatient = null;
    provisionalName = provisionalPatientName || (appt.patient ? `${appt.patient.first_name} ${appt.patient.last_name}`.trim() : "") || "Provisional Patient";
  } else {
    selectedPatient = appt.patient;
    provisionalName = null;
  }

  document.getElementById("booking-modal-title").textContent = "Edit Appointment";
  const cancelBtn = document.getElementById("btn-booking-delete");
  cancelBtn.classList.remove("hidden");
  cancelBtn.dataset.confirming = "";
  cancelBtn.textContent = "Cancel Appointment";

  document.getElementById("booking-patient-search").classList.add("hidden");
  document.getElementById("patient-search-results").classList.add("hidden");
  document.getElementById("selected-patient-display").classList.remove("hidden");

  const textEl = document.getElementById("selected-patient-text");
  if (isProvisional) {
    textEl.innerHTML = `<span class="appt-prov-icon">📝</span> ${escHtml(provisionalName)} <span style="font-size:10px; color:var(--grey-3); font-style:italic;">(Provisional)</span>`;
  } else {
    textEl.innerHTML = `<span class="appt-link-icon">🔗</span> ${escHtml(selectedPatient.first_name + " " + selectedPatient.last_name)} (DOB: ${selectedPatient.date_of_birth || 'N/A'})`;
  }

  document.getElementById("btn-link-patient").classList.toggle("hidden", !isProvisional);

  if (isProvisional) {
    document.getElementById("btn-clear-patient").classList.remove("hidden");
  } else {
    document.getElementById("btn-clear-patient").classList.add("hidden");
  }

  populatePractitionerDropdown(appt.practitioner?.ahpra_number);
  populateTypeDropdown(appt.appointment_type_id || appt.appointment_type?.id);

  let dateStr = appt.appointment_date;
  if (dateStr && dateStr.includes("T")) dateStr = dateStr.split("T")[0];
  document.getElementById("booking-date").value = dateStr;

  let timeStr = appt.start_time_local;
  if (timeStr && timeStr.length > 5) timeStr = timeStr.slice(0, 5);
  document.getElementById("booking-time").value = timeStr;

  document.getElementById("booking-duration").value = appt.duration_minutes || 15;

  const displayStatus = appt.status === "Confirmed" ? "Booked" : (appt.status || "Booked");
  prepareStatusDropdown(appt.status);
  document.getElementById("booking-status").value = displayStatus;

  document.getElementById("booking-reason").value = appt.reason || "";
  document.getElementById("booking-error").classList.add("hidden");

  const auditSection = document.getElementById("booking-audit-section");
  if (auditSection) {
    auditSection.classList.remove("hidden");
    const content = document.getElementById("booking-audit-content");
    const icon = document.getElementById("booking-audit-toggle-icon");
    if (content) content.classList.add("hidden");
    if (icon) {
      icon.classList.remove("expanded");
      icon.textContent = "▶";
    }
    loadAuditHistory(appt.id);
  }

  document.getElementById("booking-modal").classList.remove("hidden");
}

function openBookingModalForPatientLink(appt) {
  openBookingModalForEdit(appt);
  const search = document.getElementById("booking-patient-search");
  search.value = "";
  search.classList.remove("hidden");
  document.getElementById("patient-search-results").classList.add("hidden");
  document.getElementById("btn-link-patient").classList.remove("hidden");
  search.focus();
}

function closeBookingModal() {
  document.getElementById("booking-modal").classList.add("hidden");
  editingAppointmentId = null;
  selectedPatient = null;
  provisionalName = null;
  const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
  if (cancelReasonContainer) cancelReasonContainer.classList.add("hidden");
  const cancelReasonInput = document.getElementById("booking-cancel-reason");
  if (cancelReasonInput) cancelReasonInput.value = "";
  resetProposalConfirmation();
}

function populatePractitionerDropdown(selectedAhpra) {
  const select = document.getElementById("booking-practitioner");
  select.innerHTML = "";

  activeTemplate.columns.forEach(col => {
    if (col.practitioner_ahpra) {
      const opt = document.createElement("option");
      opt.value = col.practitioner_ahpra;
      opt.textContent = `${col.assignment} (${col.room_label})`;
      if (col.practitioner_ahpra === selectedAhpra) {
        opt.selected = true;
      }
      select.appendChild(opt);
    }
  });
}

function populateTypeDropdown(selectedTypeId) {
  const select = document.getElementById("booking-type");
  select.innerHTML = "";

  const emptyOpt = document.createElement("option");
  emptyOpt.value = "";
  emptyOpt.textContent = "— Select Type —";
  select.appendChild(emptyOpt);

  activeTypes.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = `${t.name} (${t.default_duration} mins)`;
    if (t.id === selectedTypeId) {
      opt.selected = true;
    }
    select.appendChild(opt);
  });
}

function renderSearchResults(results) {
  const dropdown = document.getElementById("patient-search-results");
  dropdown.innerHTML = "";

  const typedVal = document.getElementById("booking-patient-search").value.trim();

  if (results.length > 0) {
    results.forEach(p => {
      const item = document.createElement("div");
      item.className = "search-result-item";
      item.textContent = `${p.first_name} ${p.last_name} (DOB: ${p.date_of_birth})`;
      item.onclick = () => selectPatientForBooking(p);
      dropdown.appendChild(item);
    });
  } else {
    const item = document.createElement("div");
    item.className = "search-result-item";
    item.style.color = "var(--grey-3)";
    item.textContent = "No registered patients found.";
    dropdown.appendChild(item);
  }

  if (!editingAppointmentId && typedVal.length >= 2) {
    const provItem = document.createElement("div");
    provItem.className = "search-result-item search-result-provisional";
    provItem.style.borderTop = "1px dashed var(--grey-2)";
    provItem.style.fontWeight = "600";
    provItem.style.color = "var(--blue-mid)";
    provItem.innerHTML = `<span class="appt-prov-icon">📝</span> Book as provisional: "${escHtml(typedVal)}"`;
    provItem.onclick = () => selectProvisionalPatient(typedVal);
    dropdown.appendChild(provItem);
  }

  dropdown.classList.remove("hidden");
}

function selectPatientForBooking(patient) {
  selectedPatient = patient;
  provisionalName = null;
  document.getElementById("booking-patient-search").classList.add("hidden");
  document.getElementById("patient-search-results").classList.add("hidden");
  document.getElementById("selected-patient-display").classList.remove("hidden");
  document.getElementById("btn-link-patient").classList.add("hidden");
  document.getElementById("selected-patient-text").innerHTML =
    `<span class="appt-link-icon">🔗</span> ${escHtml(patient.first_name + " " + patient.last_name)} (DOB: ${patient.date_of_birth})`;
  document.getElementById("btn-clear-patient").classList.remove("hidden");
  resetProposalConfirmation();
}

function selectProvisionalPatient(name) {
  selectedPatient = null;
  provisionalName = name;
  document.getElementById("booking-patient-search").classList.add("hidden");
  document.getElementById("patient-search-results").classList.add("hidden");
  document.getElementById("selected-patient-display").classList.remove("hidden");
  document.getElementById("btn-link-patient").classList.remove("hidden");
  document.getElementById("selected-patient-text").innerHTML =
    `<span class="appt-prov-icon">📝</span> ${escHtml(name)} <span style="font-size:10px; color:var(--grey-3); font-style:italic;">(Provisional)</span>`;
  document.getElementById("btn-clear-patient").classList.remove("hidden");
  resetProposalConfirmation();
}

async function apiErrorMessage(res, action) {
  const text = await res.text();
  try {
    const data = JSON.parse(text);
    const detail = data.detail || data;
    if (res.status === 409 && detail && typeof detail === "object") {
      const start = detail.conflicting_start_time ? new Date(detail.conflicting_start_time) : null;
      const end = detail.conflicting_end_time ? new Date(detail.conflicting_end_time) : null;
      const range = start && end && !Number.isNaN(start.valueOf()) && !Number.isNaN(end.valueOf())
        ? ` ${String(start.getHours()).padStart(2, "0")}:${String(start.getMinutes()).padStart(2, "0")}-${String(end.getHours()).padStart(2, "0")}:${String(end.getMinutes()).padStart(2, "0")}`
        : "";
      return `${action} failed: appointment conflicts with an existing booking${range}.`;
    }
    if (typeof detail === "string") return `${action} failed: ${detail}`;
    if (detail?.message) return `${action} failed: ${detail.message}`;
  } catch (_) {
    // Use the raw response text below.
  }
  return `${action} failed: ${res.status}${text ? ` ${text}` : ""}`;
}

function resetProposalConfirmation() {
  const saveBtn = document.getElementById("btn-booking-save");
  if (saveBtn) {
    saveBtn.dataset.confirmed = "false";
    saveBtn.textContent = "Save Booking";
    saveBtn.classList.remove("btn-warning-action");
  }
  const warningEl = document.getElementById("booking-warnings");
  if (warningEl) {
    warningEl.innerHTML = "";
    warningEl.classList.add("hidden");
  }
  const errorEl = document.getElementById("booking-error");
  if (errorEl) {
    errorEl.textContent = "";
    errorEl.classList.add("hidden");
  }
}

function simulateProposal(payload) {
  const blocks = [];
  const warnings = [];

  let targetAhpra = null;
  for (const ahpra in ahpraToPractitionerMap) {
    if (ahpraToPractitionerMap[ahpra].id === payload.practitioner_id) {
      targetAhpra = ahpra;
      break;
    }
  }

  if (targetAhpra && mockAppointmentsCache) {
    const payloadDate = payload.appointment_date;
    const payloadStart = toMins(payload.start_time_local);
    const payloadEnd = payloadStart + payload.duration_minutes;

    const hasConflict = mockAppointmentsCache.some(appt => {
      if (editingAppointmentId && appt.id === editingAppointmentId) return false;
      if (appt.practitioner.ahpra_number !== targetAhpra) return false;
      if (["Cancelled", "NoShow", "DNA"].includes(appt.status)) return false;

      const apptDate = appt.appointment_date || document.getElementById("booking-date").value;
      if (apptDate !== payloadDate) return false;

      const apptStart = toMins(appt.start_time_local);
      const apptEnd = apptStart + (appt.duration_minutes || 15);

      return payloadStart < apptEnd && payloadEnd > apptStart;
    });

    if (hasConflict) {
      blocks.push({
        code: "appointment_conflict",
        severity: "blocked",
        message: "This appointment overlaps an existing booking (Mock)."
      });
    }
  }

  if (targetAhpra && appointmentCrossesBreak(targetAhpra, payload.start_time_local, payload.duration_minutes)) {
    warnings.push({
      code: "break_overlap",
      severity: "warning",
      message: "This appointment overlaps with a scheduled break block (Mock)."
    });
  }

  if (!payload.patient_id) {
    warnings.push({
      code: "provisional_patient",
      severity: "warning",
      message: "This booking is not linked to a verified patient record yet (Mock)."
    });
  }

  return {
    safe: blocks.length === 0,
    requires_confirmation: true,
    autonomy_tier: blocks.length > 0 ? "blocked" : "proposal",
    summary: "Mock proposal summary.",
    warnings: warnings,
    blocks: blocks
  };
}

function simulateStatusProposal(appt, payload) {
  const blocks = [];
  const warnings = [];

  const TERMINAL_STATUSES = ["Completed", "Cancelled", "NoShow", "DNA"];

  if (payload.status === appt.status) {
    blocks.push({
      code: "already_in_status",
      severity: "blocked",
      message: `This appointment is already ${appt.status}.`
    });
  }

  if (TERMINAL_STATUSES.includes(appt.status) && payload.status !== appt.status) {
    warnings.push({
      code: "already_terminal",
      severity: "warning",
      message: `This appointment is already ${appt.status}. Re-transitioning is unusual.`
    });
  }

  const clearsWaitingArea = (
    TERMINAL_STATUSES.includes(payload.status) &&
    appt.waiting_area_id !== null &&
    payload.waiting_area_id === null
  );
  if (clearsWaitingArea) {
    warnings.push({
      code: "waiting_area_cleared",
      severity: "warning",
      message: "This status change will remove the patient from the waiting area."
    });
  }

  if (TERMINAL_STATUSES.includes(payload.status) && payload.waiting_area_id !== null) {
    warnings.push({
      code: "waiting_area_assigned_on_terminal",
      severity: "warning",
      message: `Assigning a waiting area while marking the appointment as ${payload.status} is contradictory; the area will be set but the appointment will be closed.`
    });
  }

  const safe = blocks.length === 0;
  let autonomy_tier = "execute_with_report";
  if (!safe) {
    autonomy_tier = "blocked";
  } else if (warnings.length > 0 || TERMINAL_STATUSES.includes(payload.status)) {
    autonomy_tier = "proposal";
  }

  const patientName = provisionalPatientName(appt) || (appt.patient ? `${appt.patient.first_name} ${appt.patient.last_name}`.trim() : "") || "patient";
  let summary = `Change ${patientName}'s appointment status from ${appt.status} to ${payload.status}.`;
  if (!safe) {
    summary += " Blocked — see issues.";
  } else if (warnings.length > 0) {
    summary += " Confirmation recommended.";
  }

  return {
    safe,
    requires_confirmation: true,
    autonomy_tier,
    summary,
    warnings,
    blocks
  };
}

function simulateWaitingAreaProposal(appt, payload) {
  const blocks = [];
  const warnings = [];

  if (payload.waiting_area_id === appt.waiting_area_id) {
    blocks.push({
      code: "already_in_area",
      severity: "blocked",
      message: payload.waiting_area_id !== null
        ? "The appointment is already in this waiting area."
        : "The appointment is not currently in any waiting area."
    });
  }

  const clearsWaitingArea = (payload.waiting_area_id === null && appt.waiting_area_id !== null);
  if (clearsWaitingArea) {
    warnings.push({
      code: "waiting_area_cleared",
      severity: "warning",
      message: "This will remove the patient from the waiting area."
    });
  }

  const safe = blocks.length === 0;
  let autonomy_tier = "execute_with_report";
  if (!safe) {
    autonomy_tier = "blocked";
  } else if (warnings.length > 0) {
    autonomy_tier = "proposal";
  }

  const patientName = provisionalPatientName(appt) || (appt.patient ? `${appt.patient.first_name} ${appt.patient.last_name}`.trim() : "") || "patient";
  let summary = "";
  if (payload.waiting_area_id !== null) {
    summary = `Move ${patientName} to a different waiting area.`;
  } else if (clearsWaitingArea) {
    summary = `Remove ${patientName} from the waiting area.`;
  } else {
    summary = `No waiting-area change for ${patientName}.`;
  }

  if (!safe) {
    summary += " Blocked — see issues.";
  } else if (warnings.length > 0) {
    summary += " Confirmation recommended.";
  }

  return {
    safe,
    requires_confirmation: true,
    autonomy_tier,
    summary,
    warnings,
    blocks
  };
}

function showStatusProposalDialog(proposal) {
  return new Promise(resolve => {
    const overlay = document.createElement("div");
    overlay.className = "identity-confirm-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");

    const panel = document.createElement("div");
    panel.className = "identity-confirm-panel";

    const title = document.createElement("h2");
    title.className = "identity-confirm-title";

    const body = document.createElement("div");
    body.className = "identity-confirm-body";
    body.style.whiteSpace = "pre-wrap";
    body.style.marginBottom = "15px";

    const actions = document.createElement("div");
    actions.className = "identity-confirm-actions";

    const close = result => {
      document.removeEventListener("keydown", onKeyDown);
      overlay.remove();
      resolve(result);
    };

    const onKeyDown = event => {
      if (event.key === "Escape") close(false);
    };

    if (proposal.blocks && proposal.blocks.length > 0) {
      title.textContent = "Action Blocked";
      
      const msgList = proposal.blocks.map(b => b.message).join("\n\n");
      body.textContent = msgList;

      const okBtn = document.createElement("button");
      okBtn.type = "button";
      okBtn.className = "btn-secondary";
      okBtn.textContent = "Close";
      okBtn.onclick = () => close(false);
      actions.appendChild(okBtn);
      setTimeout(() => okBtn.focus(), 0);
    } else {
      title.textContent = "Confirm Status Change";
      
      let text = proposal.summary || "Are you sure you want to change the status?";
      if (proposal.warnings && proposal.warnings.length > 0) {
        text += "\n\nWarnings:\n" + proposal.warnings.map(w => `• ${w.message}`).join("\n");
      }
      body.textContent = text;

      const cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      cancelBtn.className = "btn-secondary";
      cancelBtn.textContent = "Cancel";
      cancelBtn.onclick = () => close(false);

      const confirmBtn = document.createElement("button");
      confirmBtn.type = "button";
      confirmBtn.className = proposal.warnings && proposal.warnings.length > 0 ? "btn-danger" : "btn-primary";
      confirmBtn.textContent = "Confirm & Save";
      confirmBtn.onclick = () => close(true);

      actions.append(cancelBtn, confirmBtn);
      setTimeout(() => cancelBtn.focus(), 0);
    }

    panel.append(title, body, actions);
    overlay.appendChild(panel);
    document.body.appendChild(overlay);
    document.addEventListener("keydown", onKeyDown);
  });
}

async function saveBooking() {
  const errorEl = document.getElementById("booking-error");
  errorEl.classList.add("hidden");
  errorEl.textContent = "";

  const warningEl = document.getElementById("booking-warnings");
  if (warningEl) {
    warningEl.innerHTML = "";
    warningEl.classList.add("hidden");
  }

  if (!selectedPatient && !provisionalName) {
    errorEl.textContent = "Please select a patient or book as provisional.";
    errorEl.classList.remove("hidden");
    return;
  }

  const ahpra = document.getElementById("booking-practitioner").value;
  const practitioner = ahpraToPractitionerMap[ahpra];
  if (!practitioner || !practitioner.id) {
    errorEl.textContent = "Practitioner ID not found. Verify practitioner column data.";
    errorEl.classList.remove("hidden");
    return;
  }

  const typeId = document.getElementById("booking-type").value || null;
  const dateVal = document.getElementById("booking-date").value;
  const timeVal = document.getElementById("booking-time").value;
  const duration = parseInt(document.getElementById("booking-duration").value, 10);
  const statusVal = document.getElementById("booking-status").value;
  const reason = document.getElementById("booking-reason").value.trim();

  if (!dateVal || !timeVal || isNaN(duration)) {
    errorEl.textContent = "Date, time, and duration are required.";
    errorEl.classList.remove("hidden");
    return;
  }

  const saveBtn = document.getElementById("btn-booking-save");
  saveBtn.disabled = true;

  try {
    const isSmokeMode = new URLSearchParams(window.location.search).get("smoke") === "true";
    const statusToSend = statusVal;

    const isConfirmed = saveBtn.dataset.confirmed === "true";
    if (!isConfirmed) {
      const payload = {
        practitioner_id: practitioner.id,
        appointment_type_id: typeId,
        appointment_date: dateVal,
        start_time_local: timeVal,
        duration_minutes: duration,
        reason: reason,
      };
      if (activeLocationId) {
        payload.location_id = activeLocationId;
      }
      if (selectedPatient) {
        payload.patient_id = selectedPatient.id;
        payload.patient_name_provisional = null;
      } else {
        payload.patient_id = null;
        payload.patient_name_provisional = provisionalName;
      }

      let proposal;
      if (isSmokeMode) {
        proposal = simulateProposal(payload);
      } else {
        const url = editingAppointmentId
          ? `/appointments/proposals/update/${editingAppointmentId}`
          : "/appointments/proposals/create";
        const propRes = await apiFetch(url, {
          method: "POST",
          body: JSON.stringify(payload)
        });
        if (!propRes.ok) {
          throw new Error(await apiErrorMessage(propRes, "Proposal check"));
        }
        proposal = await propRes.json();
      }

      if (proposal.blocks && proposal.blocks.length > 0) {
        errorEl.textContent = proposal.blocks.map(b => b.message).join(" ");
        errorEl.classList.remove("hidden");
        saveBtn.disabled = false;
        return;
      }

      if (proposal.warnings && proposal.warnings.length > 0) {
        if (warningEl) {
          const warningTitle = document.createElement("div");
          warningTitle.style.fontWeight = "bold";
          warningTitle.textContent = "Warning: Please review before saving:";
          warningEl.appendChild(warningTitle);

          const list = document.createElement("ul");
          proposal.warnings.forEach(w => {
            const item = document.createElement("li");
            item.textContent = w.message;
            list.appendChild(item);
          });
          warningEl.appendChild(list);
          warningEl.classList.remove("hidden");
        }

        saveBtn.textContent = "Confirm & Save";
        saveBtn.classList.add("btn-warning-action");
        saveBtn.dataset.confirmed = "true";
        saveBtn.disabled = false;
        return;
      }
    }

    const skipLocalWarnings = saveBtn.dataset.confirmed === "true";

    if (!skipLocalWarnings) {
      if (appointmentCrossesBreak(ahpra, timeVal, duration)) {
        if (!confirm("Warning: This appointment overlaps with a scheduled break block. Proceed?")) {
          saveBtn.disabled = false;
          return;
        }
      }

      const apptToCheck = {
        patient_id: selectedPatient ? selectedPatient.id : null,
        patient: selectedPatient,
        patient_name_provisional: provisionalName,
        provisional_name: provisionalName
      };
      if (!await confirmUnidentifiedProgress(apptToCheck, statusVal)) {
        saveBtn.disabled = false;
        return;
      }
    }

    if (editingAppointmentId) {
      if (isSmokeMode) {
        const appt = mockAppointmentsCache.find(x => x.id === editingAppointmentId);
        if (appt) {
          appt.start_time_local = timeVal;
          appt.duration_minutes = duration;
          appt.status = statusToSend;
          appt.practitioner.ahpra_number = ahpra;
          appt.reason = reason;
          appt.appointment_type_id = typeId;
          const foundType = activeTypes.find(t => t.id === typeId);
          appt.appointment_type = foundType || null;
          if (selectedPatient) {
            appt.patient_id = selectedPatient.id;
            appt.patient = selectedPatient;
            appt.patient_name_provisional = null;
          } else {
            appt.patient_id = null;
            appt.patient = null;
            appt.patient_name_provisional = provisionalName;
          }
        }
      } else {
        const updatePayload = {
          practitioner_id: practitioner.id,
          appointment_type_id: typeId,
          appointment_date: dateVal,
          start_time_local: timeVal,
          duration_minutes: duration,
          reason: reason,
        };
        if (selectedPatient) {
          updatePayload.patient_id = selectedPatient.id;
          updatePayload.patient_name_provisional = null;
        } else {
          updatePayload.patient_id = null;
          updatePayload.patient_name_provisional = provisionalName;
        }
        const updateRes = await apiFetch(`/appointments/${editingAppointmentId}`, {
          method: "PUT",
          body: JSON.stringify(updatePayload)
        });
        if (!updateRes.ok) {
          throw new Error(await apiErrorMessage(updateRes, "Update"));
        }

        const statusRes = await apiFetch(`/appointments/${editingAppointmentId}/status`, {
          method: "PATCH",
          body: JSON.stringify({ status: statusToSend })
        });
        if (!statusRes.ok) {
          throw new Error(await apiErrorMessage(statusRes, "Status update"));
        }
      }
      setStatus("Booking updated successfully.");
    } else {
      if (isSmokeMode) {
        const newAppt = {
          id: "smoke-appt-" + (mockAppointmentsCache.length + 1),
          appointment_date: dateVal,
          start_time_local: timeVal,
          duration_minutes: duration,
          status: statusToSend,
          practitioner: { ahpra_number: ahpra, id: practitioner.id, first_name: practitioner.first_name, last_name: practitioner.last_name },
          patient: selectedPatient,
          patient_name_provisional: provisionalName,
          reason: reason,
          appointment_type_id: typeId,
          appointment_type: activeTypes.find(t => t.id === typeId) || null,
          location_id: activeLocationId || "loc-1"
        };
        mockAppointmentsCache.push(newAppt);
      } else {
        const createPayload = {
          practitioner_id: practitioner.id,
          appointment_type_id: typeId,
          appointment_date: dateVal,
          start_time_local: timeVal,
          duration_minutes: duration,
          reason: reason,
        };
        if (activeLocationId) {
          createPayload.location_id = activeLocationId;
        }
        if (selectedPatient) {
          createPayload.patient_id = selectedPatient.id;
        } else {
          createPayload.patient_id = null;
          createPayload.patient_name_provisional = provisionalName;
        }

        const createRes = await apiFetch(`/appointments`, {
          method: "POST",
          body: JSON.stringify(createPayload)
        });
        if (!createRes.ok) {
          throw new Error(await apiErrorMessage(createRes, "Create"));
        }
        const newApptObj = await createRes.json();

        if (statusToSend !== "Booked") {
          const statusRes = await apiFetch(`/appointments/${newApptObj.id}/status`, {
            method: "PATCH",
            body: JSON.stringify({ status: statusToSend })
          });
          if (!statusRes.ok) {
            throw new Error(await apiErrorMessage(statusRes, "Set status"));
          }
        }
      }
      setStatus("Booking created successfully.");
    }

    closeBookingModal();
    await loadDiary(true);
  } catch (err) {
    console.error(err);
    errorEl.textContent = err.message || "An error occurred while saving the booking.";
    errorEl.classList.remove("hidden");
  } finally {
    saveBtn.disabled = false;
  }
}

async function deleteBooking() {
  if (!editingAppointmentId) return;

  const deleteBtn = document.getElementById("btn-booking-delete");
  const errorEl = document.getElementById("booking-error");
  if (deleteBtn.dataset.confirming !== "true") {
    deleteBtn.dataset.confirming = "true";
    deleteBtn.textContent = "Confirm Cancel";
    errorEl.textContent = "This will cancel the whole appointment, not just close the editor. Click Confirm Cancel to continue.";
    errorEl.classList.remove("hidden");
    const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
    if (cancelReasonContainer) cancelReasonContainer.classList.remove("hidden");
    const cancelReasonInput = document.getElementById("booking-cancel-reason");
    if (cancelReasonInput) {
      cancelReasonInput.value = "";
      cancelReasonInput.focus();
    }
    return;
  }

  errorEl.classList.add("hidden");
  deleteBtn.disabled = true;

  try {
    const isSmokeMode = new URLSearchParams(window.location.search).get("smoke") === "true";
    const appt = isSmokeMode
      ? mockAppointmentsCache.find(x => x.id === editingAppointmentId)
      : todayAppointments.find(x => x.id === editingAppointmentId);

    if (!appt) {
      throw new Error("Target appointment not found.");
    }

    const cancelReasonInput = document.getElementById("booking-cancel-reason");
    const cancellation_reason = cancelReasonInput ? cancelReasonInput.value.trim() : "";

    let proposal;
    if (isSmokeMode) {
      proposal = simulateStatusProposal(appt, { status: "Cancelled", waiting_area_id: null });
    } else {
      try {
        const propRes = await apiFetch(`/appointments/proposals/delete/${editingAppointmentId}`, {
          method: "POST",
          body: JSON.stringify({ intent: "delete_appointment", cancellation_reason })
        });
        if (propRes.status === 404) {
          throw new Error("404");
        }
        if (!propRes.ok) {
          throw new Error(await apiErrorMessage(propRes, "Delete proposal check"));
        }
        proposal = await propRes.json();
      } catch (err) {
        if (err.message === "404" || (err.message && err.message.includes("404"))) {
          // Fallback to status proposal (omitting cancellation_reason)
          const propRes = await apiFetch(`/appointments/proposals/status/${editingAppointmentId}`, {
            method: "POST",
            body: JSON.stringify({ status: "Cancelled", waiting_area_id: null })
          });
          if (!propRes.ok) {
            throw new Error(await apiErrorMessage(propRes, "Status proposal check"));
          }
          proposal = await propRes.json();
        } else {
          throw err;
        }
      }
    }

    if (!proposal.safe || (proposal.warnings && proposal.warnings.length > 0) || proposal.autonomy_tier === "proposal") {
      const confirmed = await showStatusProposalDialog(proposal);
      if (!confirmed) {
        deleteBtn.dataset.confirming = "";
        deleteBtn.textContent = "Cancel Appointment";
        errorEl.classList.add("hidden");
        const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
        if (cancelReasonContainer) cancelReasonContainer.classList.add("hidden");
        if (cancelReasonInput) cancelReasonInput.value = "";
        deleteBtn.disabled = false;
        return;
      }
    }

    if (isSmokeMode) {
      mockAppointmentsCache = mockAppointmentsCache.filter(x => x.id !== editingAppointmentId);
      setStatus("Booking cancelled (Mock).");
    } else {
      const res = await apiFetch(`/appointments/${editingAppointmentId}`, {
        method: "DELETE",
        body: JSON.stringify({ cancellation_reason })
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Delete failed: ${res.status} ${text}`);
      }
      setStatus("Booking cancelled successfully.");
    }
    const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
    if (cancelReasonContainer) cancelReasonContainer.classList.add("hidden");
    if (cancelReasonInput) cancelReasonInput.value = "";
    closeBookingModal();
    await loadDiary(true);
  } catch (err) {
    console.error(err);
    errorEl.textContent = err.message || "An error occurred while cancelling the booking.";
    errorEl.classList.remove("hidden");
    deleteBtn.dataset.confirming = "";
    deleteBtn.textContent = "Cancel Appointment";
    const cancelReasonContainer = document.getElementById("booking-cancel-reason-container");
    if (cancelReasonContainer) cancelReasonContainer.classList.add("hidden");
    if (cancelReasonInput) cancelReasonInput.value = "";
  } finally {
    deleteBtn.disabled = false;
  }
}

// ─── PATIENT FLOW WORKBENCH & WAITING ROOM LOGIC ───────────
let todayAppointments = [];
let selectedWaitingAreaTab = "all";

function setFlowPanelVisibility(isOpen, persist = true) {
  const panel = document.getElementById("diary-flow-panel");
  const toggleBtn = document.getElementById("btn-toggle-flow");
  if (panel) {
    panel.classList.toggle("hidden", !isOpen);
  }
  if (toggleBtn) {
    toggleBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    toggleBtn.classList.toggle("active", isOpen);
  }
  if (persist) {
    localStorage.setItem(FLOW_PANEL_OPEN_KEY, isOpen ? "true" : "false");
  }
}

function initDragOrResize(e, appt, span, type, col) {
  e.preventDefault();
  e.stopPropagation();

  const rect = span.getBoundingClientRect();
  const columnBody = span.closest(".diary-column-body");
  const columnBodyRect = columnBody.getBoundingClientRect();

  const startTopPx = parseFloat(span.style.top) || 0;
  const startHeightPx = parseFloat(span.style.height) || rect.height;

  const startStartMins = toMins(appt.start_time_local);
  const startDuration = appt.duration_minutes || 15;
  const startColIdx = parseInt(columnBody.dataset.colIdx, 10);

  const mouseOffsetY = e.clientY - rect.top;

  activeDragState = {
    appt,
    span,
    type,
    col,
    startTopPx,
    startHeightPx,
    startStartMins,
    startDuration,
    startColIdx,
    startClientX: e.clientX,
    startClientY: e.clientY,
    mouseOffsetY,
    hasMoved: false,
    currentColIdx: startColIdx,
    currentStartMins: startStartMins,
    currentDuration: startDuration,
    ghostEl: null,
    columnBodyRect
  };

  document.addEventListener("mousemove", handleGlobalMouseMove);
  document.addEventListener("mouseup", handleGlobalMouseUp);
}

function handleGlobalMouseMove(e) {
  if (!activeDragState) return;

  const template = activeTemplate;
  const slotDefaults = template?.slot_defaults;
  if (!slotDefaults) return;
  const pointerDelta = Math.max(
    Math.abs(e.clientX - activeDragState.startClientX),
    Math.abs(e.clientY - activeDragState.startClientY)
  );
  if (!activeDragState.hasMoved && pointerDelta < DRAG_START_THRESHOLD_PX) return;
  activeDragState.hasMoved = true;

  const intervalMins = template?.slot_defaults?.interval_minutes || 15;
  const dayStartMins = toMins(slotDefaults.start);

  if (!activeDragState.ghostEl) {
    const initialColumnBody = activeDragState.span.closest(".diary-column-body");
    const ghost = document.createElement("div");
    ghost.className = "appt-ghost-preview";
    ghost.style.position = "absolute";
    ghost.style.left = "1px";
    ghost.style.right = "1px";
    ghost.style.top = activeDragState.span.style.top;
    ghost.style.height = activeDragState.span.style.height;
    initialColumnBody.appendChild(ghost);
    activeDragState.ghostEl = ghost;
  }

  const columnBody = activeDragState.ghostEl.closest(".diary-column-body");
  const columnBodyRect = columnBody.getBoundingClientRect();

  let newStartMins = activeDragState.startStartMins;
  let newDuration = activeDragState.startDuration;

  if (activeDragState.type === "drag") {
    const hoverEl = document.elementFromPoint(e.clientX, e.clientY);
    const colBody = hoverEl?.closest(".diary-column-body");
    if (colBody && colBody.dataset.colIdx !== undefined) {
      const colIdx = parseInt(colBody.dataset.colIdx, 10);
      const col = template.columns[colIdx];
      if (col && col.practitioner_ahpra) {
        if (activeDragState.currentColIdx !== colIdx) {
          activeDragState.currentColIdx = colIdx;
          colBody.appendChild(activeDragState.ghostEl);
        }
      }
    }

    const currentColumnBody = activeDragState.ghostEl.closest(".diary-column-body");
    const currentColumnBodyRect = currentColumnBody.getBoundingClientRect();
    const relativeY = e.clientY - currentColumnBodyRect.top;
    const topPx = relativeY - activeDragState.mouseOffsetY;
    const rawMins = dayStartMins + (topPx * intervalMins / SLOT_HEIGHT_PX);
    newStartMins = Math.max(0, Math.min(1425, Math.round(rawMins / intervalMins) * intervalMins));

  } else if (activeDragState.type === "resize-top") {
    const relativeY = e.clientY - columnBodyRect.top;
    const rawStartMins = dayStartMins + (relativeY * intervalMins / SLOT_HEIGHT_PX);
    const maxStartMins = activeDragState.startStartMins + activeDragState.startDuration - 15;
    newStartMins = Math.max(0, Math.min(maxStartMins, Math.round(rawStartMins / intervalMins) * intervalMins));
    newDuration = (activeDragState.startStartMins + activeDragState.startDuration) - newStartMins;

  } else if (activeDragState.type === "resize-bottom") {
    const relativeY = e.clientY - columnBodyRect.top;
    const heightPx = relativeY - activeDragState.startTopPx;
    const duration = heightPx * intervalMins / SLOT_HEIGHT_PX;
    newDuration = Math.max(15, Math.round(duration / intervalMins) * intervalMins);
  }

  activeDragState.currentStartMins = newStartMins;
  activeDragState.currentDuration = newDuration;

  const finalTopPx = (newStartMins - dayStartMins) * (SLOT_HEIGHT_PX / intervalMins);
  const finalHeightPx = newDuration * (SLOT_HEIGHT_PX / intervalMins);

  activeDragState.ghostEl.style.top = `${finalTopPx + 1}px`;
  activeDragState.ghostEl.style.height = `${Math.max(finalHeightPx - APPT_BLOCK_GAP_PX, 10)}px`;
}

async function handleGlobalMouseUp(e) {
  if (!activeDragState) return;

  document.removeEventListener("mousemove", handleGlobalMouseMove);
  document.removeEventListener("mouseup", handleGlobalMouseUp);

  const state = activeDragState;
  activeDragState = null;

  if (state.ghostEl) {
    state.ghostEl.remove();
  }

  if (!state.hasMoved) {
    return;
  }

  const appt = state.appt;
  const hasStartTimeChange = (state.currentStartMins !== state.startStartMins);
  const hasDurationChange = (state.currentDuration !== state.startDuration);
  const hasColumnChange = (state.currentColIdx !== state.startColIdx);

  if (!hasStartTimeChange && !hasDurationChange && !hasColumnChange) {
    return;
  }

  const targetCol = activeTemplate.columns[state.currentColIdx];
  const deltaStart = state.currentStartMins - state.startStartMins;
  const deltaDuration = state.currentDuration - state.startDuration;

  await handleMoveResize(appt, deltaStart, deltaDuration, targetCol);
}

async function handleMoveResize(appt, deltaStart, deltaDuration, column = null) {
  const currentStartMins = toMins(appt.start_time_local);
  const newStartMins = Math.max(0, Math.min(1425, currentStartMins + deltaStart));
  const newDuration = Math.max(15, (appt.duration_minutes || 15) + deltaDuration);

  const targetPractitioner = column ? ahpraToPractitionerMap[column.practitioner_ahpra] : null;
  const newPractitionerId = targetPractitioner ? targetPractitioner.id : (appt.practitioner?.id || appt.practitioner_id);

  if (newStartMins === currentStartMins && newDuration === (appt.duration_minutes || 15) && (!column || newPractitionerId === (appt.practitioner?.id || appt.practitioner_id))) {
    return;
  }

  const newStartTimeString = fromMins(newStartMins);
  const provisionalPatientName = appt.patient_name_provisional || appt.provisional_name || "";
  const isProvisional = !!provisionalPatientName || !appt.patient_id || !appt.patient;

  const payload = {
    practitioner_id: newPractitionerId,
    appointment_type_id: appt.appointment_type_id || appt.appointment_type?.id || null,
    appointment_date: appt.appointment_date || localDateKey(diaryDate),
    start_time_local: newStartTimeString,
    duration_minutes: newDuration,
    reason: appt.reason || "",
  };

  if (appt.location_id) {
    payload.location_id = appt.location_id;
  } else if (activeLocationId) {
    payload.location_id = activeLocationId;
  }

  if (!isProvisional) {
    payload.patient_id = appt.patient_id || appt.patient?.id;
    payload.patient_name_provisional = null;
  } else {
    payload.patient_id = null;
    payload.patient_name_provisional = provisionalPatientName || (appt.patient ? `${appt.patient.first_name} ${appt.patient.last_name}`.trim() : "") || "Provisional Patient";
  }

  try {
    let proposal;
    if (isSmokeMode()) {
      const origEditingId = editingAppointmentId;
      editingAppointmentId = appt.id;
      try {
        proposal = simulateProposal(payload);
      } finally {
        editingAppointmentId = origEditingId;
      }
    } else {
      const propRes = await apiFetch(`/appointments/proposals/update/${appt.id}`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      if (!propRes.ok) {
        throw new Error(await apiErrorMessage(propRes, "Proposal check"));
      }
      proposal = await propRes.json();
    }

    if (!proposal.safe || (proposal.warnings && proposal.warnings.length > 0) || proposal.autonomy_tier === "proposal") {
      const confirmed = await showStatusProposalDialog(proposal);
      if (!confirmed) {
        await loadDiary(true);
        return;
      }
    }

    if (isSmokeMode()) {
      const cachedAppt = mockAppointmentsCache?.find(item => item.id === appt.id) || appt;
      cachedAppt.start_time_local = newStartTimeString;
      cachedAppt.duration_minutes = newDuration;
      if (column && targetPractitioner) {
        cachedAppt.practitioner = {
          id: targetPractitioner.id,
          ahpra_number: column.practitioner_ahpra,
          first_name: targetPractitioner.first_name,
          last_name: targetPractitioner.last_name
        };
        appt.practitioner = cachedAppt.practitioner;
      }
      appt.start_time_local = newStartTimeString;
      appt.duration_minutes = newDuration;
      setStatus("Booking moved/resized (Mock)");
      await loadDiary(true);
      scrollToAppointment(appt.id);
    } else {
      setStatus("Updating appointment...");
      const updateRes = await apiFetch(`/appointments/${appt.id}`, {
        method: "PUT",
        body: JSON.stringify(payload)
      });
      if (!updateRes.ok) {
        throw new Error(await apiErrorMessage(updateRes, "Update"));
      }
      setStatus("Booking updated successfully.");
      await loadDiary(true);
      scrollToAppointment(appt.id);
    }
  } catch (err) {
    console.error(err);
    alert(err.message || "An error occurred while rescheduling the appointment.");
    await loadDiary(true);
  }
}

async function setAppointmentStatus(appt, newStatus, selectEl = null, waitingAreaId = null) {
  const isStatusChange = (newStatus !== appt.status);
  const isWaitingAreaChangeOnly = (!isStatusChange && waitingAreaId !== null && waitingAreaId !== appt.waiting_area_id);

  if (!isStatusChange && !isWaitingAreaChangeOnly) {
    return true;
  }

  if (selectEl) selectEl.disabled = true;

  try {
    // 1. Proposal check
    const payload = {
      status: newStatus,
      waiting_area_id: waitingAreaId !== null ? (waitingAreaId || null) : (appt.waiting_area_id || null)
    };

    let proposal;
    if (isSmokeMode()) {
      if (isWaitingAreaChangeOnly) {
        proposal = simulateWaitingAreaProposal(appt, payload);
      } else {
        proposal = simulateStatusProposal(appt, payload);
      }
    } else {
      if (isWaitingAreaChangeOnly) {
        const propRes = await apiFetch(`/appointments/proposals/waiting-area/${appt.id}`, {
          method: "POST",
          body: JSON.stringify({ waiting_area_id: payload.waiting_area_id })
        });
        if (!propRes.ok) {
          throw new Error(await apiErrorMessage(propRes, "Waiting-area proposal check"));
        }
        proposal = await propRes.json();
      } else {
        const propRes = await apiFetch(`/appointments/proposals/status/${appt.id}`, {
          method: "POST",
          body: JSON.stringify(payload)
        });
        if (!propRes.ok) {
          throw new Error(await apiErrorMessage(propRes, "Status proposal check"));
        }
        proposal = await propRes.json();
      }
    }

    // 2. Proposal confirmation check
    const TERMINAL_STATUSES = ["Completed", "Cancelled", "NoShow", "DNA"];
    const needsConfirm = (
      !proposal.safe ||
      (proposal.warnings && proposal.warnings.length > 0) ||
      proposal.autonomy_tier === "proposal" ||
      (isStatusChange && TERMINAL_STATUSES.includes(newStatus))
    );

    if (needsConfirm) {
      const confirmed = await showStatusProposalDialog(proposal);
      if (!confirmed) {
        if (selectEl) {
          if (isWaitingAreaChangeOnly) {
            selectEl.value = appt.waiting_area_id || "";
          } else {
            selectEl.value = appt.status === "Confirmed" ? "Booked" : appt.status;
          }
        }
        return false;
      }
    }

    // 3. Keep original patient identity confirmation check
    if (!await confirmUnidentifiedProgress(appt, newStatus)) {
      if (selectEl) {
        if (isWaitingAreaChangeOnly) {
          selectEl.value = appt.waiting_area_id || "";
        } else {
          selectEl.value = appt.status === "Confirmed" ? "Booked" : appt.status;
        }
      }
      return false;
    }

    // 4. Actual save operation (mutation)
    setStatus("Updating status...");
    if (isSmokeMode()) {
      appt.status = newStatus;
      if (waitingAreaId !== null) {
        appt.waiting_area_id = waitingAreaId || null;
      }
      setStatus("Status updated (Mock)");
      await loadDiary(true);
      const el = document.querySelector(`.appt[data-id="${appt.id}"]`);
      if (el) el.classList.add("appt-active");
    } else {
      const bodyPayload = { status: newStatus };
      if (waitingAreaId !== null) {
        bodyPayload.waiting_area_id = waitingAreaId || null;
      }
      const res = await apiFetch(`/appointments/${appt.id}/status`, {
        method: "PATCH",
        body: JSON.stringify(bodyPayload)
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Failed to update status: ${res.status} ${text}`);
      }
      const updatedAppt = await res.json();
      appt.status = updatedAppt.status;
      appt.waiting_area_id = updatedAppt.waiting_area_id;
      setStatus("Status updated successfully.");
      await loadDiary(true);
      const el = document.querySelector(`.appt[data-id="${appt.id}"]`);
      if (el) el.classList.add("appt-active");
    }
    await updateFlowPanel();
    return true;
  } catch (err) {
    console.error("Error updating status:", err);
    if (err.message === "401 Unauthorized") {
      showError("Session expired. Please reopen the taskpane to sign in again.");
      setStatus("Session expired.");
    } else {
      showError(err.message || "Failed to update appointment status.");
      setStatus("Error updating status.");
    }
    if (selectEl) {
      if (isWaitingAreaChangeOnly) {
        selectEl.value = appt.waiting_area_id || "";
      } else {
        selectEl.value = appt.status === "Confirmed" ? "Booked" : appt.status;
      }
    }
    return false;
  } finally {
    if (selectEl) selectEl.disabled = false;
  }
}

function toggleFlowPanel() {
  const panel = document.getElementById("diary-flow-panel");
  if (!panel) return;
  const isHidden = panel.classList.contains("hidden");
  if (isHidden) {
    setFlowPanelVisibility(true);
    updateFlowPanel();
  } else {
    setFlowPanelVisibility(false);
    updateFlowBadgeCount();
  }
}

function closeFlowPanel() {
  setFlowPanelVisibility(false);
  updateFlowBadgeCount();
}

function updateFlowBadgeCount() {
  const arrivedCount = todayAppointments.filter(a => a.status === "Arrived").length;
  const countEl = document.getElementById("flow-waiting-count");
  if (countEl) {
    countEl.textContent = arrivedCount;
  }
}

async function loadTodayAppointments() {
  if (isSameClinicDay(diaryDate, new Date())) {
    todayAppointments = activeAppointments;
    return;
  }

  if (isSmokeMode()) {
    todayAppointments = getMockAppointments().filter(a => {
      let dateStr = a.appointment_date;
      if (dateStr && dateStr.includes("T")) dateStr = dateStr.split("T")[0];
      const todayStr = new Date().toISOString().slice(0, 10);
      const apptLocId = a.location_id || "loc-1";
      return dateStr === todayStr && apptLocId === activeLocationId;
    });
    return;
  }

  try {
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
    const todayEnd = new Date(todayStart);
    todayEnd.setHours(23, 59, 59, 999);
      const params = new URLSearchParams({
        date_from: todayStart.toISOString(),
        date_to: todayEnd.toISOString(),
      });
      if (activeLocationId) {
        params.set("location_id", activeLocationId);
      }
      const res = await apiFetch(`/appointments?${params.toString()}`);
      if (res.ok) {
        todayAppointments = await res.json();
      }
  } catch (err) {
    console.warn("Failed to fetch today's appointments for flow badge:", err);
  }
}

async function hydrateCheckinDefaults(appts) {
  if (isSmokeMode() || !token || !Array.isArray(appts) || !waitingAreas.length) return;

  const pending = appts.filter(appt => appt?.id && !checkinDefaultCache.has(appt.id));
  if (!pending.length) return;

  await Promise.all(pending.map(async appt => {
    try {
      const res = await apiFetch(`/appointments/${appt.id}/checkin-defaults`);
      if (!res.ok) {
        checkinDefaultCache.set(appt.id, { waitingAreaId: null, roomName: null });
        return;
      }
      const data = await res.json();
      checkinDefaultCache.set(appt.id, {
        waitingAreaId: data?.suggested_waiting_area_id || null,
        roomName: data?.room_name || null,
      });
    } catch (err) {
      if (err && err.message === "401 Unauthorized") throw err;
      console.warn("Check-in default fetch failed:", err);
      checkinDefaultCache.set(appt.id, { waitingAreaId: null, roomName: null });
    }
  }));
}

function getDefaultWaitingArea(appt) {
  if (!appt) return null;
  // 1. If the appt already has a waiting_area_id, use it
  if (appt.waiting_area_id && waitingAreas.length) {
    const area = waitingAreas.find(item => item.id === appt.waiting_area_id);
    if (area) return area;
  }

  // 2. Prefer the backend's DiaryRoster -> Room.default_waiting_area_id suggestion
  const cachedDefault = appt.id ? checkinDefaultCache.get(appt.id) : null;
  if (cachedDefault?.waitingAreaId && waitingAreas.length) {
    const area = waitingAreas.find(item => item.id === cachedDefault.waitingAreaId);
    if (area) return area;
  }

  // 3. Try to match the practitioner's column default waiting room name
  if (appt.practitioner && appt.practitioner.ahpra_number && activeTemplate && activeTemplate.columns) {
    const col = activeTemplate.columns.find(c => c.practitioner_ahpra === appt.practitioner.ahpra_number);
    if (col && (col.default_waiting_room || col.waiting_room)) {
      const roomName = String(col.default_waiting_room || col.waiting_room).trim().toLowerCase();
      const area = waitingAreas.find(item => item.name.trim().toLowerCase() === roomName);
      if (area) return area;
    }
  }

  // 4. Fall back to the first waiting area in the list
  if (waitingAreas.length) {
    return waitingAreas[0];
  }

  return null;
}

function getAppointmentWaitingRoom(a) {
  if (a.waiting_area_id && waitingAreas.length) {
    const area = waitingAreas.find(item => item.id === a.waiting_area_id);
    if (area) return { key: `area:${area.id}`, label: area.name };
  }
  const cachedDefault = a.id ? checkinDefaultCache.get(a.id) : null;
  if (cachedDefault?.waitingAreaId && waitingAreas.length) {
    const area = waitingAreas.find(item => item.id === cachedDefault.waitingAreaId);
    if (area) return { key: `area:${area.id}`, label: area.name };
  }
  if (a.waiting_room) {
    const room = a.waiting_room.trim();
    if (room) {
      const area = findWaitingAreaByLabel(room);
      if (area) return { key: `area:${area.id}`, label: area.name };
      if (!waitingAreas.length) return { key: `legacy:${normalizeWaitingAreaLabel(room)}`, label: room };
    }
  }
  if (a.practitioner && a.practitioner.ahpra_number && activeTemplate && activeTemplate.columns) {
    const col = activeTemplate.columns.find(c => c.practitioner_ahpra === a.practitioner.ahpra_number);
    if (col && (col.default_waiting_room || col.waiting_room)) {
      const room = String(col.default_waiting_room || col.waiting_room).trim();
      if (room) {
        const area = findWaitingAreaByLabel(room);
        if (area) return { key: `area:${area.id}`, label: area.name };
        if (!waitingAreas.length) return { key: `legacy:${normalizeWaitingAreaLabel(room)}`, label: room };
      }
    }
  }
  return null;
}

function normalizeWaitingAreaLabel(label) {
  return String(label || "")
    .trim()
    .toLowerCase()
    .replace(/^main\s+/, "")
    .replace(/\s+/g, " ");
}

function findWaitingAreaByLabel(label) {
  const normalizedLabel = normalizeWaitingAreaLabel(label);
  if (!normalizedLabel || !waitingAreas.length) return null;
  return waitingAreas.find(area => normalizeWaitingAreaLabel(area.name) === normalizedLabel) || null;
}

function sortWaitingAreaResources(a, b) {
  const orderDelta = (Number(a.display_order) || 0) - (Number(b.display_order) || 0);
  if (orderDelta !== 0) return orderDelta;
  return String(a.name || "").localeCompare(String(b.name || ""));
}

function getUniqueWaitingAreas() {
  const areas = new Map();
  waitingAreas.slice().sort(sortWaitingAreaResources).forEach(area => {
    if (area && area.id && area.name) {
      areas.set(`area:${area.id}`, { key: `area:${area.id}`, label: area.name });
    }
  });

  if (areas.size) {
    return Array.from(areas.values());
  }

  if (activeTemplate && activeTemplate.columns) {
    activeTemplate.columns.forEach(col => {
      const room = col.default_waiting_room || col.waiting_room;
      if (room && room.trim()) {
        areas.set(`legacy:${room.trim().toLowerCase()}`, {
          key: `legacy:${room.trim().toLowerCase()}`,
          label: room.trim(),
        });
      }
    });
  }
  todayAppointments.forEach(a => {
    const room = getAppointmentWaitingRoom(a);
    if (room) {
      areas.set(room.key, room);
    }
  });
  return Array.from(areas.values()).sort((a, b) => a.label.localeCompare(b.label));
}

function renderWaitingAreaTabs(areas) {
  const container = document.getElementById("flow-waiting-area-tabs");
  if (!container) return false;

  container.innerHTML = "";

  const hasUnassigned = !waitingAreas.length && todayAppointments.some(a => {
    if (a.status === "Cancelled") return false;
    const room = getAppointmentWaitingRoom(a);
    return !room;
  });

  const allTabs = [{ key: "all", label: "All" }, ...areas];
  if (hasUnassigned) {
    allTabs.push({ key: "unassigned", label: "Unassigned" });
  }

  if (areas.length <= 1) {
    selectedWaitingAreaTab = "all";
    return false;
  }

  if (!allTabs.some(tab => tab.key === selectedWaitingAreaTab)) {
    selectedWaitingAreaTab = "all";
  }

  allTabs.forEach(tab => {
    const tabEl = document.createElement("button");
    tabEl.className = "flow-tab-btn";
    if (tab.key === selectedWaitingAreaTab) {
      tabEl.classList.add("active");
    }
    tabEl.textContent = tab.label;
    tabEl.type = "button";
    tabEl.onclick = () => {
      if (selectedWaitingAreaTab === tab.key) return;
      selectedWaitingAreaTab = tab.key;
      updateFlowPanel();
    };
    container.appendChild(tabEl);
  });
  return true;
}

async function updateFlowPanel() {
  const panel = document.getElementById("diary-flow-panel");
  if (!panel || panel.classList.contains("hidden")) return;

  const waiting = [];
  const consult = [];
  const expected = [];
  const finished = [];
  const cancelled = [];

  todayAppointments.forEach(a => {
    if (a.status === "Cancelled") {
      cancelled.push(a);
    } else if (a.status === "Arrived") {
      waiting.push(a);
    } else if (a.status === "InConsult") {
      consult.push(a);
    } else if (a.status === "Booked" || a.status === "Confirmed") {
      expected.push(a);
    } else if (["Completed", "NoShow", "DNA"].includes(a.status)) {
      finished.push(a);
    }
  });

  const sortByTime = (x, y) => {
    const tX = apptTimeKey(x) || "00:00";
    const tY = apptTimeKey(y) || "00:00";
    return tX.localeCompare(tY);
  };

  waiting.sort(sortByTime);
  consult.sort(sortByTime);
  expected.sort(sortByTime);
  finished.sort(sortByTime);
  cancelled.sort(sortByTime);

  try {
    await hydrateCheckinDefaults([...waiting, ...consult, ...expected, ...finished]);
  } catch (err) {
    console.warn("Waiting room default hydration failed:", err);
  }

  const areas = getUniqueWaitingAreas();
  const hasAreas = areas.length > 0;
  const tabsContainer = document.getElementById("flow-waiting-area-tabs");
  if (tabsContainer) {
    if (hasAreas) {
      const hasTabs = renderWaitingAreaTabs(areas);
      tabsContainer.classList.toggle("hidden", !hasTabs);
    } else {
      tabsContainer.classList.add("hidden");
      tabsContainer.innerHTML = "";
      selectedWaitingAreaTab = "all";
    }
  }

  let filteredWaiting = waiting;
  let filteredConsult = consult;
  let filteredExpected = expected;
  let filteredFinished = finished;
  let filteredCancelled = cancelled;

  if (hasAreas && selectedWaitingAreaTab !== "all") {
    const filterFn = (a) => {
      const room = getAppointmentWaitingRoom(a);
      if (selectedWaitingAreaTab === "unassigned") {
        return !room;
      }
      return room && room.key === selectedWaitingAreaTab;
    };
    filteredWaiting = waiting.filter(filterFn);
    filteredConsult = consult.filter(filterFn);
    filteredExpected = expected.filter(filterFn);
    filteredFinished = finished.filter(filterFn);
    filteredCancelled = cancelled.filter(filterFn);
  }

  const secWaiting = document.querySelector("#flow-sec-waiting .flow-sec-count");
  if (secWaiting) secWaiting.textContent = filteredWaiting.length;

  const secConsult = document.querySelector("#flow-sec-consult .flow-sec-count");
  if (secConsult) secConsult.textContent = filteredConsult.length;

  const secExpected = document.querySelector("#flow-sec-expected .flow-sec-count");
  if (secExpected) secExpected.textContent = filteredExpected.length;

  const secFinished = document.querySelector("#flow-sec-finished .flow-sec-count");
  if (secFinished) secFinished.textContent = filteredFinished.length;

  const secCancelled = document.querySelector("#flow-sec-cancelled .flow-sec-count");
  if (secCancelled) secCancelled.textContent = filteredCancelled.length;

  renderFlowList("flow-list-waiting", filteredWaiting, "Start Consult", "InConsult");
  renderFlowList("flow-list-consult", filteredConsult, "Complete", "Completed");
  renderFlowList("flow-list-expected", filteredExpected, "Check In", "Arrived");
  renderFlowList("flow-list-finished", filteredFinished, null, null);
  renderFlowList("flow-list-cancelled", filteredCancelled, null, null);

  updateFlowBadgeCount();
}

function renderFlowList(containerId, appts, actionLabel, targetStatus) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = "";

  if (appts.length === 0) {
    const empty = document.createElement("div");
    empty.className = "flow-empty";
    empty.textContent = "No patients";
    container.appendChild(empty);
    return;
  }

  appts.forEach(a => {
    const card = document.createElement("div");
    card.className = `flow-card flow-card-${(a.status || "booked").toLowerCase()}`;
    card.setAttribute("data-testid", "flow-card");
    card.setAttribute("data-status", (a.status || "booked").toLowerCase());

    const header = document.createElement("div");
    header.className = "flow-card-header";

    const name = document.createElement("span");
    name.className = "flow-card-name";
    name.setAttribute("data-testid", "flow-card-name");

    const provisionalName = provisionalPatientName(a);
    const isProvisional = isPatientIdentityUnconfirmed(a);
    const patientName = provisionalName || (a.patient ? `${a.patient.first_name} ${a.patient.last_name}`.trim() : "") || "Unknown Patient";

    if (isProvisional) {
      name.innerHTML = `<span class="appt-prov-icon" title="Provisional Patient">📝</span> ${escHtml(patientName)}`;
    } else {
      name.innerHTML = `<span class="appt-link-icon" title="Linked Patient Record">🔗</span> ${escHtml(patientName)}`;
    }

    if (isProvisional && isClinicalProgressStatus(a.status)) {
      card.classList.add("flow-card-identity-unconfirmed");
    }

    if (!isProvisional) {
      const linkedBadge = document.createElement("span");
      linkedBadge.className = "appt-linked-badge";
      linkedBadge.title = "Linked patient record";
      linkedBadge.textContent = "✓";
      name.appendChild(linkedBadge);
    }

    header.appendChild(name);

    if (a.status !== "Cancelled") {
      if (isProvisional) {
        const linkBtn = document.createElement("button");
        linkBtn.className = "flow-card-link-btn";
        linkBtn.type = "button";
        linkBtn.textContent = "Link";
        linkBtn.title = "Link to an existing patient record";
        linkBtn.onclick = (e) => {
          e.stopPropagation();
          openBookingModalForPatientLink(a);
        };
        header.appendChild(linkBtn);
      }

      const editBtn = document.createElement("button");
      editBtn.className = "flow-card-edit-btn";
      editBtn.type = "button";
      editBtn.innerHTML = "✎";
      editBtn.title = "Edit appointment";
      editBtn.onclick = (e) => {
        e.stopPropagation();
        openBookingModalForEdit(a);
      };
      header.appendChild(editBtn);
    }
    card.appendChild(header);

    const details = document.createElement("div");
    details.className = "flow-card-details";
    const timeStr = apptTimeKey(a) || "09:00";
    const practitionerName = a.practitioner
      ? [a.practitioner.first_name, a.practitioner.last_name].filter(Boolean).join(" ").trim()
      : "";
    const roomStr = practitionerName || a.practitioner?.ahpra_number || "Room";
    details.textContent = `${timeStr} — ${roomStr}`;
    card.appendChild(details);

    if (a.reason) {
      const reason = document.createElement("div");
      reason.className = "flow-card-reason";
      reason.setAttribute("data-testid", "flow-card-reason");
      reason.textContent = a.reason;
      card.appendChild(reason);
    }

    if (a.status === "Cancelled" && a.cancellation_reason) {
      const reason = document.createElement("div");
      reason.className = "flow-card-cancellation-reason";
      reason.setAttribute("data-testid", "flow-card-cancellation-reason");
      reason.textContent = `Reason: ${a.cancellation_reason}`;
      card.appendChild(reason);
    }

    const footer = document.createElement("div");
    footer.className = "flow-card-footer";

    const statusBadge = document.createElement("span");
    statusBadge.className = `flow-status-badge badge-${(a.status || "booked").toLowerCase()}`;
    statusBadge.setAttribute("data-testid", "flow-card-status");
    statusBadge.textContent = getStatusLabel(a.status);
    footer.appendChild(statusBadge);

    // Dropdown for waiting areas when there are multiple waiting areas and status is Expected or Arrived
    if (waitingAreas.length > 1 && (targetStatus === "Arrived" || a.status === "Arrived")) {
      const areaSelect = document.createElement("select");
      areaSelect.className = "flow-card-area-select";
      areaSelect.title = targetStatus === "Arrived" ? "Select waiting area for check-in" : "Reassign waiting area";

      const currentArea = getDefaultWaitingArea(a);

      waitingAreas.forEach(area => {
        const opt = document.createElement("option");
        opt.value = area.id;
        opt.textContent = area.name;
        if (currentArea && area.id === currentArea.id) {
          opt.selected = true;
        }
        areaSelect.appendChild(opt);
      });

      if (a.status === "Arrived") {
        // Live reassignment on selection change
        let updatingArea = false;
        areaSelect.onchange = async () => {
          if (updatingArea) return;
          updatingArea = true;
          areaSelect.disabled = true;
          try {
            await setAppointmentStatus(a, "Arrived", areaSelect, areaSelect.value);
          } finally {
            updatingArea = false;
            areaSelect.disabled = false;
          }
        };
      }

      footer.appendChild(areaSelect);
    }

    if (actionLabel && targetStatus) {
      const actionBtn = document.createElement("button");
      actionBtn.className = "flow-card-action-btn btn-primary-xs";
      actionBtn.type = "button";
      actionBtn.textContent = actionLabel;

      let updatingCardStatus = false;
      actionBtn.onclick = async (e) => {
        e.stopPropagation();
        if (updatingCardStatus) return;
        updatingCardStatus = true;
        actionBtn.disabled = true;
        try {
          let waitingAreaId = null;
          if (targetStatus === "Arrived") {
            const selectEl = footer.querySelector(".flow-card-area-select");
            if (selectEl) {
              waitingAreaId = selectEl.value;
            } else {
              // If only one waiting area exists, default to its ID automatically
              const defaultArea = getDefaultWaitingArea(a);
              if (defaultArea) {
                waitingAreaId = defaultArea.id;
              }
            }
          }
          const changed = await setAppointmentStatus(a, targetStatus, null, waitingAreaId);
          if (!changed) actionBtn.disabled = false;
        } finally {
          updatingCardStatus = false;
          if (document.body.contains(actionBtn)) actionBtn.disabled = false;
        }
      };
      footer.appendChild(actionBtn);
    }

    card.appendChild(footer);

    card.onclick = (e) => {
      if (e.target.closest("button") || e.target.closest("select")) return;

      const apptDate = new Date(a.appointment_date);
      if (!isSameClinicDay(diaryDate, apptDate)) {
        diaryDate = apptDate;
        updateDateLabel();
        loadDiary(false, { scrollToApptId: a.id });
      } else {
        scrollToAppointment(a.id);
      }
    };

    container.appendChild(card);
  });
}

function scrollToAppointment(apptId) {
  const el = document.querySelector(`.appt[data-id="${apptId}"]`);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.classList.add("appt-highlight");
    setTimeout(() => el.classList.remove("appt-highlight"), 2000);

    document.querySelectorAll(".appt-active").forEach(x => x.classList.remove("appt-active"));
    el.classList.add("appt-active");
  }
}

// ─── COLLAPSIBLE WAITING ROOM SECTIONS ─────────────────────
const COLLAPSE_KEY = "emr4_diary_collapsed_sections_v1";

function toggleSectionCollapse(sectionId) {
  const sectionEl = document.getElementById(sectionId);
  if (!sectionEl) return;
  const isCollapsed = sectionEl.classList.toggle("collapsed");
  updateSectionChevron(sectionEl, isCollapsed);

  let states = {};
  try {
    states = JSON.parse(localStorage.getItem(COLLAPSE_KEY) || "{}");
  } catch (_) {}
  states[sectionId] = isCollapsed;
  localStorage.setItem(COLLAPSE_KEY, JSON.stringify(states));
}

function updateSectionChevron(sectionEl, isCollapsed) {
  const chevron = sectionEl.querySelector(".flow-section-chevron");
  if (chevron) {
    chevron.textContent = isCollapsed ? "▶" : "▼";
  }
}

function restoreSectionCollapseStates() {
  let states = {};
  try {
    states = JSON.parse(localStorage.getItem(COLLAPSE_KEY) || "{}");
  } catch (_) {}

  document.querySelectorAll(".flow-section").forEach(sectionEl => {
    const isCollapsed = !!states[sectionEl.id];
    if (isCollapsed) {
      sectionEl.classList.add("collapsed");
    } else {
      sectionEl.classList.remove("collapsed");
    }
    updateSectionChevron(sectionEl, isCollapsed);
  });
}

// ─── PHYSICAL LOCATION SELECTOR ────────────────────────────
async function getLocationOptions() {
  if (isSmokeMode()) return mockLocations;
  if (!token) return activeLocationId ? [{ id: activeLocationId, name: "Main Clinic" }] : [];
  try {
    const res = await apiFetch("/diary/locations");
    if (!res.ok) throw new Error(`Locations: ${res.status}`);
    const locations = await res.json();
    return Array.isArray(locations)
      ? locations.map(loc => ({ id: loc.id, name: loc.name })).filter(loc => loc.id && loc.name)
      : [];
  } catch (err) {
    if (err && err.message === "401 Unauthorized") throw err;
    console.warn("Location fetch failed; using single-location fallback:", err);
    return activeLocationId ? [{ id: activeLocationId, name: "Main Clinic" }] : [];
  }
}

async function initLocationSelector() {
  const selectEl = document.getElementById("diary-location-select");
  if (!selectEl) return;

  selectEl.innerHTML = "";

  const list = await getLocationOptions();
  const visibleList = list.length ? list : [{ id: "", name: "Main Clinic" }];

  if (!activeLocationId && visibleList[0].id) {
    activeLocationId = visibleList[0].id;
    localStorage.setItem(LOCATION_STORAGE_KEY, activeLocationId);
  }

  visibleList.forEach(loc => {
    const opt = document.createElement("option");
    opt.value = loc.id;
    opt.textContent = loc.name;
    if (loc.id === activeLocationId) {
      opt.selected = true;
    }
    selectEl.appendChild(opt);
  });

  // If the saved activeLocationId is no longer in the list (e.g. switching modes), reset it
  if (visibleList.length && !visibleList.some(loc => loc.id === activeLocationId)) {
    activeLocationId = visibleList[0].id || null;
    if (activeLocationId) {
      localStorage.setItem(LOCATION_STORAGE_KEY, activeLocationId);
    } else {
      localStorage.removeItem(LOCATION_STORAGE_KEY);
    }
    selectEl.value = activeLocationId || "";
  }

  selectEl.disabled = visibleList.length <= 1;
  locationOptionsLoaded = true;

  selectEl.onchange = () => {
    activeLocationId = selectEl.value || null;
    if (activeLocationId) {
      localStorage.setItem(LOCATION_STORAGE_KEY, activeLocationId);
    } else {
      localStorage.removeItem(LOCATION_STORAGE_KEY);
    }
    setStatus(`Location changed to ${selectEl.options[selectEl.selectedIndex].text}`);

    loadDiary(true);
  };
}

// ─── RESOURCE ADMIN MOCK DATABASES (Smoke Mode) ────────────────
let mockRooms = [
  { id: "mock-room-1", name: "Room 1", display_order: 0, location_id: "loc-1", default_waiting_area_id: "mock-area-1" },
  { id: "mock-room-2", name: "Room 2", display_order: 1, location_id: "loc-1", default_waiting_area_id: "mock-area-2" },
  { id: "mock-room-3", name: "Room 3", display_order: 2, location_id: "loc-1", default_waiting_area_id: null },
  { id: "mock-room-4", name: "Procedure Room 1", display_order: 0, location_id: "loc-2", default_waiting_area_id: null },
];

let mockWaitingAreas = [
  { id: "mock-area-1", name: "Main Waiting Room", display_order: 0, location_id: "loc-1" },
  { id: "mock-area-2", name: "Sub-waiting Room B", display_order: 1, location_id: "loc-1" },
];

function getMockWaitingAreas() {
  return mockWaitingAreas;
}

function isUserAdminOrOwner() {
  if (isSmokeMode()) return true;
  return isAdminRole(currentUserRole || getRoleFromToken(token));
}

// ─── API WRAPPERS FOR CRUD ─────────────────────────────────────
async function fetchRooms(locationId) {
  if (isSmokeMode()) {
    return mockRooms.filter(r => r.is_active !== false && (!locationId || r.location_id === locationId));
  }
  const query = locationId ? `?location_id=${encodeURIComponent(locationId)}` : "";
  const res = await apiFetch(`/diary/rooms${query}`);
  if (!res.ok) throw new Error(await getErrorMessage(res));
  return await res.json();
}

async function fetchWaitingAreas(locationId) {
  if (isSmokeMode()) {
    return mockWaitingAreas.filter(wa => wa.is_active !== false && (!locationId || wa.location_id === locationId));
  }
  const query = locationId ? `?location_id=${encodeURIComponent(locationId)}` : "";
  const res = await apiFetch(`/diary/waiting-areas${query}`);
  if (!res.ok) throw new Error(await getErrorMessage(res));
  return await res.json();
}

async function saveRoom(room) {
  if (isSmokeMode()) {
    let savedRoom;
    if (room.id) {
      const idx = mockRooms.findIndex(r => r.id === room.id);
      if (idx !== -1) {
        mockRooms[idx] = { ...mockRooms[idx], ...room };
        savedRoom = mockRooms[idx];
      }
    } else {
      room.id = `mock-room-${Date.now()}`;
      savedRoom = { ...room };
      mockRooms.push(savedRoom);
    }
    compactMockResourceOrders(mockRooms, savedRoom, room.display_order);
    return savedRoom || room;
  }
  const method = room.id ? "PATCH" : "POST";
  const url = room.id ? `/diary/rooms/${room.id}` : "/diary/rooms";
  const res = await apiFetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(room)
  });
  if (!res.ok) throw new Error(await getErrorMessage(res));
  return await res.json();
}

async function archiveRoom(roomId) {
  if (isSmokeMode()) {
    const idx = mockRooms.findIndex(r => r.id === roomId);
    if (idx !== -1) mockRooms[idx] = { ...mockRooms[idx], is_active: false };
    compactMockResourceOrders(mockRooms, idx !== -1 ? mockRooms[idx] : null);
    return true;
  }
  const res = await apiFetch(`/diary/rooms/${roomId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_active: false })
  });
  if (!res.ok) throw new Error(await getErrorMessage(res));
  return true;
}

async function saveWaitingArea(area) {
  if (isSmokeMode()) {
    let savedArea;
    if (area.id) {
      const idx = mockWaitingAreas.findIndex(wa => wa.id === area.id);
      if (idx !== -1) {
        mockWaitingAreas[idx] = { ...mockWaitingAreas[idx], ...area };
        savedArea = mockWaitingAreas[idx];
      }
    } else {
      area.id = `mock-area-${Date.now()}`;
      savedArea = { ...area };
      mockWaitingAreas.push(savedArea);
    }
    compactMockResourceOrders(mockWaitingAreas, savedArea, area.display_order);
    return savedArea || area;
  }
  const method = area.id ? "PATCH" : "POST";
  const url = area.id ? `/diary/waiting-areas/${area.id}` : "/diary/waiting-areas";
  const res = await apiFetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(area)
  });
  if (!res.ok) throw new Error(await getErrorMessage(res));
  return await res.json();
}

async function archiveWaitingArea(areaId) {
  if (isSmokeMode()) {
    const idx = mockWaitingAreas.findIndex(wa => wa.id === areaId);
    if (idx !== -1) mockWaitingAreas[idx] = { ...mockWaitingAreas[idx], is_active: false };
    const archivedArea = idx !== -1 ? mockWaitingAreas[idx] : null;
    const locId = archivedArea ? archivedArea.location_id : null;
    compactMockResourceOrders(mockWaitingAreas, archivedArea);

    const activeAreas = mockWaitingAreas.filter(wa => wa.location_id === locId && wa.is_active);
    activeAreas.sort((a, b) => a.display_order - b.display_order);
    const fallbackId = activeAreas.length > 0 ? activeAreas[0].id : null;

    mockRooms.forEach(r => {
      if (r.default_waiting_area_id === areaId) {
        r.default_waiting_area_id = fallbackId;
      }
    });
    return true;
  }
  const res = await apiFetch(`/diary/waiting-areas/${areaId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_active: false })
  });
  if (!res.ok) throw new Error(await getErrorMessage(res));
  return true;
}

async function getErrorMessage(res) {
  try {
    const data = await res.json();
    return data.detail || `Server error: ${res.status}`;
  } catch (e) {
    return `HTTP error ${res.status}`;
  }
}

// ─── ADMIN MODAL CONTROLLER ────────────────────────────────────
let adminActiveTab = "rooms";
let pendingAdminArchiveKey = null;
let adminRoomCache = [];
let adminAreaCache = [];
let adminLastSavedRoomId = null;
let adminLastSavedAreaId = null;

function initAdminPanel() {
  const adminBtn = document.getElementById("btn-admin-panel");
  const adminModal = document.getElementById("admin-modal");
  const closeBtn = document.getElementById("btn-admin-close");

  if (!adminBtn || !adminModal) return;

  adminBtn.onclick = async () => {
    await ensureCurrentUserRole();
    const isAllowed = isUserAdminOrOwner();
    const deniedEl = document.getElementById("admin-access-denied");
    const allowedEl = document.getElementById("admin-allowed-content");

    if (isAllowed) {
      deniedEl.classList.add("hidden");
      allowedEl.classList.remove("hidden");
      loadAdminTabContent();
    } else {
      deniedEl.classList.remove("hidden");
      allowedEl.classList.add("hidden");
    }

    adminModal.classList.remove("hidden");
    clearAdminAlerts();
  };

  closeBtn.onclick = () => {
    adminModal.classList.add("hidden");
    loadDiary(true);
  };

  adminModal.onclick = (e) => {
    if (e.target === adminModal) {
      adminModal.classList.add("hidden");
      loadDiary(true);
    }
  };

  const tabRooms = document.getElementById("tab-btn-rooms");
  const tabAreas = document.getElementById("tab-btn-areas");
  const panelRooms = document.getElementById("tab-panel-rooms");
  const panelAreas = document.getElementById("tab-panel-areas");

  tabRooms.onclick = () => {
    tabRooms.classList.add("active");
    tabAreas.classList.remove("active");
    panelRooms.classList.remove("hidden");
    panelAreas.classList.add("hidden");
    adminActiveTab = "rooms";
    loadAdminTabContent();
  };

  tabAreas.onclick = () => {
    tabAreas.classList.add("active");
    tabRooms.classList.remove("active");
    panelAreas.classList.remove("hidden");
    panelRooms.classList.add("hidden");
    adminActiveTab = "areas";
    loadAdminTabContent();
  };

  document.getElementById("btn-add-room-trigger").onclick = () => showRoomForm(null);
  document.getElementById("btn-cancel-room-form").onclick = () => hideRoomForm();
  document.getElementById("btn-cancel-room-form-top").onclick = () => hideRoomForm();
  document.getElementById("room-form").onsubmit = async (e) => {
    e.preventDefault();
    await handleSaveRoom();
  };

  document.getElementById("btn-add-area-trigger").onclick = () => showAreaForm(null);
  document.getElementById("btn-cancel-area-form").onclick = () => hideAreaForm();
  document.getElementById("btn-cancel-area-form-top").onclick = () => hideAreaForm();
  document.getElementById("area-form").onsubmit = async (e) => {
    e.preventDefault();
    await handleSaveArea();
  };
}

function clearAdminAlerts() {
  const alertEl = document.getElementById("admin-alert");
  const infoEl = document.getElementById("admin-info");
  alertEl.textContent = "";
  alertEl.classList.add("hidden");
  infoEl.textContent = "";
  infoEl.classList.add("hidden");
}

function setAdminError(msg) {
  const alertEl = document.getElementById("admin-alert");
  alertEl.textContent = msg;
  if (msg) {
    alertEl.classList.remove("hidden");
  } else {
    alertEl.classList.add("hidden");
  }
}

function setAdminInfo(msg) {
  const infoEl = document.getElementById("admin-info");
  infoEl.textContent = msg;
  if (msg) {
    infoEl.classList.remove("hidden");
    setTimeout(() => {
      infoEl.classList.add("hidden");
    }, 4000);
  } else {
    infoEl.classList.add("hidden");
  }
}

function confirmAdminArchive(key, message) {
  try {
    if (typeof window.confirm === "function") {
      return window.confirm(message);
    }
  } catch (_) {
  }

  if (pendingAdminArchiveKey === key) {
    pendingAdminArchiveKey = null;
    clearAdminAlerts();
    return true;
  }

  pendingAdminArchiveKey = key;
  setAdminError("Confirmation dialog unavailable here. Click Archive again to confirm.");
  return false;
}

async function loadAdminTabContent() {
  clearAdminAlerts();
  if (adminActiveTab === "rooms") {
    await renderRoomsTab();
  } else {
    await renderAreasTab();
  }
}

function getFallbackWaitingArea(locationId, areasList) {
  if (!Array.isArray(areasList)) return null;
  const activeAreas = areasList.filter(a => a.location_id === locationId && a.is_active);
  if (activeAreas.length === 0) return null;
  activeAreas.sort((a, b) => a.display_order - b.display_order);
  return activeAreas[0];
}

async function renderRoomsTab() {
  const container = document.getElementById("rooms-list-container");
  if (!container) return;
  container.innerHTML = `<div style="text-align:center; padding: 12px; color: var(--grey-3);">Loading rooms…</div>`;
  hideRoomForm();

  try {
    const [roomsList, areasList] = await Promise.all([
      fetchRooms(activeLocationId),
      fetchWaitingAreas(activeLocationId)
    ]);
    adminRoomCache = Array.isArray(roomsList) ? roomsList : [];
    adminAreaCache = Array.isArray(areasList) ? areasList : [];

    const waitingSelect = document.getElementById("room-input-waiting");
    waitingSelect.innerHTML = "";
    const activeAreas = adminAreaCache.filter(a => a.is_active);
    if (activeAreas.length === 0) {
      waitingSelect.innerHTML = `<option value="">[None]</option>`;
    } else {
      activeAreas.sort((a, b) => a.display_order - b.display_order);
      activeAreas.forEach(area => {
        const opt = document.createElement("option");
        opt.value = area.id;
        opt.textContent = area.name;
        waitingSelect.appendChild(opt);
      });
    }

    container.innerHTML = "";
    if (!roomsList.length) {
      container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--grey-3);">No rooms configured for this location.</div>`;
      return;
    }

    roomsList.sort(sortAdminResourceItems);

    roomsList.forEach(room => {
      const card = document.createElement("div");
      card.className = "admin-item-card";
      if (room.id === adminLastSavedRoomId) {
        card.classList.add("admin-item-card--highlight");
        setTimeout(() => card.scrollIntoView({ block: "nearest", inline: "nearest" }), 0);
      }

      const defaultArea = areasList.find(a => a.id === room.default_waiting_area_id && a.is_active);
      let areaLabel = "";
      if (defaultArea) {
        areaLabel = defaultArea.name;
      } else {
        const fallback = getFallbackWaitingArea(room.location_id, areasList);
        areaLabel = fallback ? `${fallback.name} (Fallback)` : "[None]";
      }

      card.innerHTML = `
        <div class="admin-item-info">
          <span class="admin-item-title">${escapeHTML(room.name)}</span>
          <span class="admin-item-meta">Order: ${room.display_order} | Default Area: ${escapeHTML(areaLabel)}</span>
        </div>
        <div class="admin-item-actions">
          <button class="btn-ghost-sm btn-edit-room" style="padding: 2px 6px;">Edit</button>
          <button class="btn-ghost-sm btn-archive-room" style="padding: 2px 6px; color: var(--red);">Archive</button>
        </div>
      `;

      card.querySelector(".btn-edit-room").onclick = () => showRoomForm(room);
      card.querySelector(".btn-archive-room").onclick = () => handleArchiveRoom(room);

      container.appendChild(card);
    });

  } catch (err) {
    setAdminError(`Failed to load rooms: ${err.message}`);
    container.innerHTML = "";
  }
}

async function renderAreasTab() {
  const container = document.getElementById("areas-list-container");
  if (!container) return;
  container.innerHTML = `<div style="text-align:center; padding: 12px; color: var(--grey-3);">Loading waiting areas…</div>`;
  hideAreaForm();

  try {
    const areasList = await fetchWaitingAreas(activeLocationId);
    adminAreaCache = Array.isArray(areasList) ? areasList : [];
    waitingAreas = adminAreaCache;
    container.innerHTML = "";
    if (!areasList.length) {
      container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--grey-3);">No waiting areas configured for this location.</div>`;
      return;
    }

    areasList.sort(sortAdminResourceItems);

    areasList.forEach(area => {
      const card = document.createElement("div");
      card.className = "admin-item-card";
      if (area.id === adminLastSavedAreaId) {
        card.classList.add("admin-item-card--highlight");
        setTimeout(() => card.scrollIntoView({ block: "nearest", inline: "nearest" }), 0);
      }

      card.innerHTML = `
        <div class="admin-item-info">
          <span class="admin-item-title">${escapeHTML(area.name)}</span>
          <span class="admin-item-meta">Order: ${area.display_order}</span>
        </div>
        <div class="admin-item-actions">
          <button class="btn-ghost-sm btn-edit-area" style="padding: 2px 6px;">Edit</button>
          <button class="btn-ghost-sm btn-archive-area" style="padding: 2px 6px; color: var(--red);">Archive</button>
        </div>
      `;

      card.querySelector(".btn-edit-area").onclick = () => showAreaForm(area);
      card.querySelector(".btn-archive-area").onclick = () => handleArchiveArea(area);

      container.appendChild(card);
    });

  } catch (err) {
    setAdminError(`Failed to load waiting areas: ${err.message}`);
    container.innerHTML = "";
  }
}

async function refreshWaitingAreaState() {
  const refreshedAreas = await fetchWaitingAreas(activeLocationId);
  waitingAreas = Array.isArray(refreshedAreas) ? refreshedAreas : [];
  adminAreaCache = waitingAreas;
  checkinDefaultCache.clear();

  const validTabs = new Set(["all", ...getUniqueWaitingAreas().map(area => area.key)]);
  if (!validTabs.has(selectedWaitingAreaTab)) {
    selectedWaitingAreaTab = "all";
  }

  const panel = document.getElementById("diary-flow-panel");
  if (panel && !panel.classList.contains("hidden")) {
    await updateFlowPanel();
  } else {
    updateFlowBadgeCount();
  }

  return waitingAreas;
}

function escapeHTML(str) {
  if (!str) return "";
  return str.replace(/[&<>'"]/g,
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

function sortAdminResourceItems(a, b) {
  const orderDelta = (Number(a.display_order) || 0) - (Number(b.display_order) || 0);
  if (orderDelta !== 0) return orderDelta;
  return String(a.name || "").localeCompare(String(b.name || ""));
}

function compactMockResourceOrders(items, movedItem = null, requestedOrder = null) {
  if (!Array.isArray(items)) return;

  const scopeKey = item => item && item.location_id ? item.location_id : "__practice__";
  const scopes = Array.from(new Set(items.map(scopeKey)));

  scopes.forEach(scope => {
    const scoped = items.filter(item => scopeKey(item) === scope);
    const movedInScope = movedItem && scopeKey(movedItem) === scope ? movedItem : null;
    const activeItems = scoped
      .filter(item => item.is_active !== false && (!movedInScope || item.id !== movedInScope.id))
      .sort(sortAdminResourceItems);
    const inactiveItems = scoped
      .filter(item => item.is_active === false && (!movedInScope || item.id !== movedInScope.id))
      .sort(sortAdminResourceItems);

    if (movedInScope) {
      if (movedInScope.is_active !== false) {
        const targetOrder = Number.isFinite(Number(requestedOrder))
          ? Math.max(0, Math.min(Number(requestedOrder), activeItems.length))
          : Math.max(0, Math.min(Number(movedInScope.display_order) || 0, activeItems.length));
        activeItems.splice(targetOrder, 0, movedInScope);
      } else {
        inactiveItems.push(movedInScope);
      }
    }

    [...activeItems, ...inactiveItems].forEach((item, index) => {
      item.display_order = index;
    });
  });
}

function getNextAdminDisplayOrder(items) {
  const activeCount = (Array.isArray(items) ? items : []).filter(item => item && item.is_active !== false).length;
  return String(activeCount);
}

function showRoomForm(room) {
  document.getElementById("room-list-view").classList.add("hidden");
  document.getElementById("room-form-view").classList.remove("hidden");
  clearAdminAlerts();

  const titleEl = document.getElementById("room-form-title");
  const editIdEl = document.getElementById("room-edit-id");
  const nameEl = document.getElementById("room-input-name");
  const orderEl = document.getElementById("room-input-order");
  const waitingEl = document.getElementById("room-input-waiting");

  if (room) {
    titleEl.textContent = "Edit Room";
    editIdEl.value = room.id;
    nameEl.value = room.name;
    orderEl.value = room.display_order;

    let defaultVal = "";
    if (room.default_waiting_area_id) {
      const isConfiguredActive = adminAreaCache.some(a => a.id === room.default_waiting_area_id && a.is_active);
      if (isConfiguredActive) {
        defaultVal = room.default_waiting_area_id;
      }
    }
    if (!defaultVal) {
      const locId = room.location_id || activeLocationId;
      const fallback = getFallbackWaitingArea(locId, adminAreaCache);
      defaultVal = fallback ? fallback.id : "";
    }
    waitingEl.value = defaultVal;
  } else {
    titleEl.textContent = "Add Room";
    editIdEl.value = "";
    nameEl.value = "";
    orderEl.value = getNextAdminDisplayOrder(adminRoomCache);

    const fallback = getFallbackWaitingArea(activeLocationId, adminAreaCache);
    waitingEl.value = fallback ? fallback.id : "";
  }
  nameEl.focus();
}

function hideRoomForm() {
  document.getElementById("room-list-view").classList.remove("hidden");
  document.getElementById("room-form-view").classList.add("hidden");
}

async function handleSaveRoom() {
  const editId = document.getElementById("room-edit-id").value;
  const name = document.getElementById("room-input-name").value.trim();
  const order = parseInt(document.getElementById("room-input-order").value, 10);
  const waitingId = document.getElementById("room-input-waiting").value || null;

  if (!name) {
    setAdminError("Room name is required.");
    return;
  }

  const roomPayload = {
    name,
    display_order: order,
    default_waiting_area_id: waitingId,
    location_id: activeLocationId || null
  };

  if (editId) {
    roomPayload.id = editId;
  }

  try {
    const savedRoom = await saveRoom(roomPayload);
    adminLastSavedRoomId = savedRoom && savedRoom.id ? savedRoom.id : editId || null;
    setAdminInfo(editId ? "Room updated successfully." : "Room created successfully.");
    await renderRoomsTab();
  } catch (err) {
    setAdminError(`Failed to save room: ${err.message}`);
  }
}

async function handleArchiveRoom(room) {
  if (!confirmAdminArchive(`room:${room.id}`, `Are you sure you want to archive "${room.name}"? Historical booking references will be preserved.`)) {
    return;
  }
  try {
    await archiveRoom(room.id);
    setAdminInfo("Room archived successfully.");
    await renderRoomsTab();
  } catch (err) {
    setAdminError(`Failed to archive room: ${err.message}`);
  }
}

function showAreaForm(area) {
  document.getElementById("area-list-view").classList.add("hidden");
  document.getElementById("area-form-view").classList.remove("hidden");
  clearAdminAlerts();

  const titleEl = document.getElementById("area-form-title");
  const editIdEl = document.getElementById("area-edit-id");
  const nameEl = document.getElementById("area-input-name");
  const orderEl = document.getElementById("area-input-order");

  if (area) {
    titleEl.textContent = "Edit Waiting Area";
    editIdEl.value = area.id;
    nameEl.value = area.name;
    orderEl.value = area.display_order;
  } else {
    titleEl.textContent = "Add Waiting Area";
    editIdEl.value = "";
    nameEl.value = "";
    orderEl.value = getNextAdminDisplayOrder(adminAreaCache);
  }
  nameEl.focus();
}

function hideAreaForm() {
  document.getElementById("area-list-view").classList.remove("hidden");
  document.getElementById("area-form-view").classList.add("hidden");
}

async function handleSaveArea() {
  const editId = document.getElementById("area-edit-id").value;
  const name = document.getElementById("area-input-name").value.trim();
  const order = parseInt(document.getElementById("area-input-order").value, 10);

  if (!name) {
    setAdminError("Waiting area name is required.");
    return;
  }

  const areaPayload = {
    name,
    display_order: order,
    location_id: activeLocationId || null
  };

  if (editId) {
    areaPayload.id = editId;
  }

  try {
    const savedArea = await saveWaitingArea(areaPayload);
    adminLastSavedAreaId = savedArea && savedArea.id ? savedArea.id : editId || null;
    const message = editId ? "Waiting area updated successfully." : "Waiting area created successfully.";
    await refreshWaitingAreaState();
    await renderAreasTab();
    setAdminInfo(message);
  } catch (err) {
    setAdminError(`Failed to save waiting area: ${err.message}`);
  }
}

async function handleArchiveArea(area) {
  if (!confirmAdminArchive(`area:${area.id}`, `Are you sure you want to archive "${area.name}"? Historical booking references will be preserved.`)) {
    return;
  }
  try {
    await archiveWaitingArea(area.id);
    await refreshWaitingAreaState();
    await renderAreasTab();
    setAdminInfo("Waiting area archived successfully.");
  } catch (err) {
    setAdminError(`Failed to archive waiting area: ${err.message}`);
  }
}
