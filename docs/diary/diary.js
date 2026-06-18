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
const MIN_TIME_INCREMENT_MINS = 5;

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

function getMockAppointments() {
  return [
    {
      id: "smoke-appt-1",
      start_time_local: "09:00",
      duration_minutes: 30,
      status: "Confirmed",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Margaret", last_name: "Thompson" },
      reason: "Hypertension follow-up",
      appointment_type_id: "smoke-type-1"
    },
    {
      id: "smoke-appt-2",
      start_time_local: "09:15",
      duration_minutes: 15,
      status: "Booked",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Billy", last_name: "Frusin" },
      reason: "Ear ache",
      appointment_type_id: "smoke-type-2"
    },
    {
      id: "smoke-appt-3",
      start_time_local: "10:00",
      duration_minutes: 45,
      status: "Booked",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Margaret", last_name: "Thompson" },
      reason: "Care Plan review",
      appointment_type_id: "smoke-type-1"
    },
    {
      id: "smoke-appt-4",
      start_time_local: "11:30",
      duration_minutes: 30,
      status: "Confirmed",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "Jane", last_name: "Doe" },
      reason: "Flu vaccine",
      appointment_type_id: "smoke-type-2"
    },
    {
      id: "smoke-appt-5",
      start_time_local: "11:45",
      duration_minutes: 15,
      status: "Arrived",
      practitioner: { ahpra_number: "MED0001234567" },
      patient: { first_name: "John", last_name: "Smith" },
      reason: "Script renewal",
      appointment_type_id: "smoke-type-1"
    },
    {
      id: "smoke-appt-6",
      start_time_local: "10:05",
      duration_minutes: 20,
      status: "Booked",
      practitioner: { ahpra_number: "MED999" },
      patient: { first_name: "Nora", last_name: "Patel" },
      reason: "Dressing change",
      appointment_type_id: "smoke-type-2"
    }
  ];
}

function getMockTypes() {
  return [
    { id: "smoke-type-1", color_hex: "#0050a0" },
    { id: "smoke-type-2", color_hex: "#00B050" }
  ];
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
    const res = await apiFetch("/diary/template");
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
    document.getElementById("diary-body")?.appendChild(footer);
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

function timeRangeLabel(startMins, endMins) {
  return `${fromMins(startMins)}-${fromMins(endMins)}`;
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
  const body = document.getElementById("diary-body");
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
  switch (status) {
    case "Confirmed":  return "appt-confirmed";
    case "Arrived":    return "appt-arrived";
    case "InConsult":  return "appt-inconsult";
    case "Completed":  return "appt-completed";
    case "Cancelled":
    case "NoShow":
    case "DNA":        return "appt-cancelled";
    default:           return "appt-booked";
  }
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
    column.className = "diary-column";

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

      if (!hasBreak && !hasAppt) {
        const empty = document.createElement("span");
        empty.className = "slot-empty";
        empty.textContent = "»";
        slotDiv.appendChild(empty);
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

    // 2c. Appointments (absolute positioned with lane-based cascading)
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

    // Assign lanes to handle overlaps
    const lanes = [];
    colAppts.forEach(a => {
      const start = toMins(apptTimeKey(a));
      const duration = Math.max(apptDurationMins(a, intervalMins), intervalMins);

      let laneIdx = 0;
      while (laneIdx < lanes.length && lanes[laneIdx] > start) {
        laneIdx++;
      }
      lanes[laneIdx] = start + duration;
      a._laneIdx = laneIdx;
    });

    // Render appointments
    colAppts.forEach(a => {
      const start = toMins(apptTimeKey(a));
      const duration = Math.max(apptDurationMins(a, intervalMins), intervalMins);
      const end = start + duration;
      const isIrregular = !isOnMajorGrid(start, template) || !isOnMajorGrid(end, template);

      const topPx = (start - dayStartMins) * (SLOT_HEIGHT_PX / intervalMins);
      const heightPx = duration * (SLOT_HEIGHT_PX / intervalMins);

      const cls = apptClass(a.status);
      const color = a.appointment_type?.color_hex || (a.appointment_type_id ? typeMap[a.appointment_type_id] : null);

      const span = document.createElement("span");
      span.className = `appt ${cls}`;
      if (color) {
        span.dataset.color = color;
        span.style.setProperty("--appt-color", color);
      }

      span.style.position = "absolute";
      span.style.top = (topPx + 1 + a._laneIdx * 4) + "px";
      span.style.left = (1 + a._laneIdx * 8) + "px";
      span.style.right = "1px";
      span.style.zIndex = String(10 + a._laneIdx);
      span.style.height = (heightPx - APPT_BLOCK_GAP_PX) + "px";
      span.style.setProperty("--appt-height", (heightPx - APPT_BLOCK_GAP_PX) + "px");
      span.tabIndex = 0;

      const patientName = `${a.patient.first_name} ${a.patient.last_name}`;
      const timeLabel = timeRangeLabel(start, end);
      span.setAttribute("role", "button");
      span.setAttribute("aria-label", a.reason ? `${patientName}. ${timeLabel}. ${a.reason}` : `${patientName}. ${timeLabel}`);
      span.title = a.reason ? `${patientName} - ${timeLabel} - ${a.reason}` : `${patientName} - ${timeLabel}`;
      const name = document.createElement("span");
      name.className = "appt-name";
      name.textContent = patientName;
      span.appendChild(name);
      if (isIrregular) {
        appendTimeEdges(span, start, end);
      }
      if (a.reason && duration >= intervalMins * 2) {
        const reason = document.createElement("span");
        reason.className = "appt-reason";
        reason.textContent = a.reason;
        span.appendChild(reason);
      }

      span.addEventListener("click", e => {
        e.stopPropagation();
        const wasActive = span.classList.contains("appt-active");
        document.querySelectorAll(".appt-active").forEach(el => el.classList.remove("appt-active"));
        if (!wasActive) span.classList.add("appt-active");
      });

      span.addEventListener("keydown", e => {
        if (e.key !== "Enter" && e.key !== " ") return;
        e.preventDefault();
        span.click();
      });

      columnBody.appendChild(span);
    });

    appendNowMarker(columnBody, template);
    column.appendChild(columnBody);
    grid.appendChild(column);
  });

  document.getElementById("diary-grid").classList.remove("hidden");
  showLoading(false);
  showError("");
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
  if (!silent) {
    showLoading(true);
    document.getElementById("diary-grid").classList.add("hidden");
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

  const apptParams = `date_from=${dayStart.toISOString()}&date_to=${dayEnd.toISOString()}`;

  try {
    let template, appointments, types;

    if (isSmokeMode) {
      template = normalizeTemplate(getMockTemplate());
      appointments = getMockAppointments();
      types = getMockTypes();
    } else {
      const [templateRes, apptRes, typeRes, rosterRes] = await Promise.all([
        loadDiaryTemplate(),
        apiFetch(`/appointments?${apptParams}`),
        apiFetch(`/appointments/types`),
        apiFetch(`/diary/roster?date=${dateStr}`).catch(err => {
          console.warn("Roster fetch failed:", err);
          return null;
        })
      ]);
      template = templateRes;
      if (!apptRes.ok) throw new Error(`Appointments: ${apptRes.status} ${await apptRes.text()}`);
      if (!typeRes.ok) throw new Error(`Types: ${typeRes.status} ${await typeRes.text()}`);
      appointments = await apptRes.json();
      types        = await typeRes.json();

      let rosterEntries = [];
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

          let assignment = "[Available]";
          if (entry.label) {
            assignment = entry.label;
          } else if (entry.practitioner_ahpra) {
            assignment = ahpraToAssignment[entry.practitioner_ahpra] || entry.practitioner_ahpra;
          }

          return {
            room_label: entry.room_name,
            assignment: assignment,
            practitioner_ahpra: entry.practitioner_ahpra || null,
            tint: tmplCol ? tmplCol.tint : null,
            slot_interval_minutes: tmplCol ? tmplCol.slot_interval_minutes : null,
            breaks: tmplCol ? tmplCol.breaks : []
          };
        });

        template.columns = mergedColumns;
      }
    }

    setActiveTemplate(template);

    const typeMap    = {};
    types.forEach(t => { typeMap[t.id] = t.color_hex; });

    const slots      = generateSlots(activeTemplate);
    const apptLookup = buildApptLookup(appointments);

    // Build occupied lookup to hide chevrons in spanned slots
    const occupied = {};
    appointments.forEach(a => {
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
    if (options.scrollToNow || autoScroll) {
      scrollToTime(nowMins(), activeTemplate);
      autoScrolledDateKey = diaryDate.toISOString().slice(0, 10);
    }

    const total = appointments.length;
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
  document.getElementById("diary-grid").addEventListener("click", () => {
    document.querySelectorAll(".appt-active").forEach(el => el.classList.remove("appt-active"));
  });

  // Close modal on backdrop click
  document.getElementById("break-modal").addEventListener("click", e => {
    if (e.target === e.currentTarget) closeBreakModal();
  });

  updateDateLabel();

  if (Office.context?.ui?.addHandlerAsync) {
    Office.context.ui.addHandlerAsync(
      Office.EventType.DialogParentMessageReceived,
      arg => {
        try {
          const msg = JSON.parse(arg.message);
          if (msg.type === "auth" && msg.token) {
            token = msg.token;
            localStorage.setItem("emr4_token", token);
            loadDiary();
            scheduleRefresh();
          }
        } catch (_) {}
      }
    );
  }

  try { Office.context?.ui?.messageParent(JSON.stringify({ type: "ready" })); } catch (_) {}

  const urlParams = new URLSearchParams(window.location.search);
  const isSmokeMode = urlParams.get("smoke") === "true";
  if (token || isSmokeMode) { loadDiary(); scheduleRefresh(); }
});
