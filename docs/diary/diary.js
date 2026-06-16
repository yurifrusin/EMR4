// ═══════════════════════════════════════════════════════════
//  EMR Centaur — Diary Grid  v1
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

// ─── DIARY TEMPLATE (embedded — will move to API when template-builder ships) ─
// Mirrors diary_template.json at the repo root.
const TEMPLATE = {
  practice_name: "EMR4 Dev Clinic",
  slot_defaults: { start: "09:00", end: "17:00", interval_minutes: 15 },
  breaks: [
    { label: "MORNING TEA (10:45 – 11:00)", from: "10:45", to: "11:00" },
    { label: "LUNCH (13:00 – 14:00)",        from: "13:00", to: "14:00" },
  ],
  columns: [
    { room_label: "Room 1", assignment: "Dr Alex Shera",  practitioner_ahpra: "MED0001234567", tint: null },
    { room_label: "Room 2", assignment: "Nurse",          practitioner_ahpra: null,            tint: "FFFF99" },
    { room_label: "Room 3", assignment: "[Available]",    practitioner_ahpra: null,            tint: null },
  ],
  footer: ["Messages:", "Phone Consultations:"],
};

// ─── STATE ────────────────────────────────────────────────
let token      = localStorage.getItem("emr4_token"); // refreshed via messageChild
let diaryDate  = new Date();                          // the day currently displayed
let refreshTimer = null;
const REFRESH_INTERVAL_MS = 60_000;                  // auto-refresh every 60 s

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

// ─── TIME HELPERS ──────────────────────────────────────────
function toMins(t) {
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}
function fromMins(m) {
  return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
}
function dateToAEDT(d) {
  // Returns a Date with time zone coerced to 00:00 local, suitable for ISO string filtering.
  const copy = new Date(d);
  copy.setHours(0, 0, 0, 0);
  return copy;
}

// ─── SLOT GENERATION ───────────────────────────────────────
function generateSlots(template) {
  const { start, end, interval_minutes } = template.slot_defaults;
  const breaks = template.breaks || [];
  const breakWindows = breaks.map(b => ({ from: toMins(b.from), to: toMins(b.to), label: b.label }));

  const slots = [];
  let cur = toMins(start);
  const endMins = toMins(end);

  while (cur < endMins) {
    // At a break start → emit break row, jump to break end
    const brk = breakWindows.find(b => b.from === cur);
    if (brk) {
      slots.push({ type: "break", label: brk.label });
      cur = brk.to;
      continue;
    }
    // Inside a break window → skip
    if (breakWindows.some(b => cur > b.from && cur < b.to)) {
      cur += interval_minutes;
      continue;
    }
    slots.push({ type: "slot", time: fromMins(cur) });
    cur += interval_minutes;
  }
  return slots;
}

// ─── APPOINTMENT LOOKUP ────────────────────────────────────
// Returns { ahpra: { "09:00": [appt, ...] } }
// Appointments without a practitioner AHPRA go into key "__none__".
function buildApptLookup(appointments) {
  const lookup = {};
  appointments.forEach(a => {
    const ahpra = a.practitioner?.ahpra_number || "__none__";
    if (!lookup[ahpra]) lookup[ahpra] = {};
    const start = new Date(a.start_time);
    const key = `${String(start.getHours()).padStart(2, "0")}:${String(start.getMinutes()).padStart(2, "0")}`;
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

// ─── RENDER GRID ───────────────────────────────────────────
function renderGrid(slots, columns, apptLookup, typeMap) {
  const colgroup = document.getElementById("diary-colgroup");
  const thead    = document.getElementById("diary-thead");
  const tbody    = document.getElementById("diary-tbody");

  colgroup.innerHTML = "";
  thead.innerHTML    = "";
  tbody.innerHTML    = "";

  // ── colgroup ──────────────────────────────────────────────
  const timeCol = document.createElement("col");
  timeCol.className = "col-time";
  colgroup.appendChild(timeCol);
  columns.forEach(() => {
    const col = document.createElement("col");
    colgroup.appendChild(col);
  });

  // ── thead ─────────────────────────────────────────────────
  const headerRow = document.createElement("tr");

  // Time header cell
  const timeTh = document.createElement("th");
  timeTh.className = "th-time";
  timeTh.textContent = "TIME";
  headerRow.appendChild(timeTh);

  // Room header cells
  columns.forEach(col => {
    const th = document.createElement("th");
    th.innerHTML = `<strong>${escHtml(col.assignment)}</strong>
      <div class="col-room-label">${escHtml(col.room_label)}</div>`;
    if (col.tint) th.style.backgroundColor = `#${col.tint}`;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  // ── tbody ─────────────────────────────────────────────────
  slots.forEach(slot => {
    const tr = document.createElement("tr");

    if (slot.type === "break") {
      // Break row spans all room columns (not the time col — time col gets its own td)
      tr.className = "break-row";
      const timeTd = document.createElement("td");
      timeTd.textContent = "";
      tr.appendChild(timeTd);

      const breakTd = document.createElement("td");
      breakTd.colSpan = columns.length;
      breakTd.textContent = slot.label;
      tr.appendChild(breakTd);

    } else {
      // Normal time slot row
      tr.className = "slot-row";

      // Time label cell
      const timeTd = document.createElement("td");
      timeTd.className = "td-time";
      timeTd.textContent = slot.time;
      tr.appendChild(timeTd);

      // One cell per column
      columns.forEach(col => {
        const td = document.createElement("td");
        td.className = "td-cell";
        if (col.tint) {
          td.classList.add("tinted");
          td.style.backgroundColor = `#${col.tint}22`; // 13% opacity tint
        }

        const appts = (col.practitioner_ahpra && apptLookup[col.practitioner_ahpra]?.[slot.time]) || [];

        if (!appts.length) {
          // Empty bookable slot
          const empty = document.createElement("span");
          empty.className = "slot-empty";
          empty.textContent = "»";
          td.appendChild(empty);
        } else {
          appts.forEach(a => {
            const name = `${a.patient.first_name} ${a.patient.last_name}`;
            const cls  = apptClass(a.status);
            const color = a.appointment_type_id ? typeMap[a.appointment_type_id] : null;

            const span = document.createElement("span");
            span.className = `appt ${cls}`;
            if (color) {
              span.dataset.color = color;
              span.style.setProperty("--appt-color", color);
            }
            span.textContent = name;

            if (a.reason) {
              const reason = document.createElement("span");
              reason.className = "appt-reason";
              reason.textContent = a.reason;
              span.appendChild(reason);
            }

            td.appendChild(span);
          });
        }

        tr.appendChild(td);
      });
    }

    tbody.appendChild(tr);
  });

  // Show the grid, hide loading/error
  document.getElementById("diary-grid").classList.remove("hidden");
  showLoading(false);
  showError("");
}

// ─── LOAD DIARY ────────────────────────────────────────────
async function loadDiary() {
  if (!token) {
    setStatus("Waiting for auth token…");
    return;
  }
  showLoading(true);
  document.getElementById("diary-grid").classList.add("hidden");
  showError("");

  // Build date-range for the selected day (local midnight → next midnight)
  const dayStart = new Date(diaryDate);
  dayStart.setHours(0, 0, 0, 0);
  const dayEnd = new Date(dayStart);
  dayEnd.setHours(23, 59, 59, 999);

  const apptParams = `date_from=${dayStart.toISOString()}&date_to=${dayEnd.toISOString()}`;

  try {
    const [apptRes, typeRes] = await Promise.all([
      apiFetch(`/appointments?${apptParams}`),
      apiFetch(`/appointments/types`),
    ]);

    if (!apptRes.ok) {
      const txt = await apptRes.text();
      throw new Error(`Appointments: ${apptRes.status} ${txt}`);
    }
    if (!typeRes.ok) {
      const txt = await typeRes.text();
      throw new Error(`Types: ${typeRes.status} ${txt}`);
    }

    const appointments = await apptRes.json();
    const types        = await typeRes.json();

    // Build type → color_hex map (UUID → hex string like "#3B82F6")
    const typeMap = {};
    types.forEach(t => { typeMap[t.id] = t.color_hex; });

    const slots      = generateSlots(TEMPLATE);
    const apptLookup = buildApptLookup(appointments);

    renderGrid(slots, TEMPLATE.columns, apptLookup, typeMap);

    const total = appointments.length;
    setStatus(`${total} appointment${total !== 1 ? "s" : ""} · ${formatDateLabel(diaryDate)}`);
  } catch (e) {
    showLoading(false);
    showError("Failed to load diary: " + (e.message || String(e)));
    setStatus("Error loading diary.");
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
  refreshTimer = setTimeout(() => {
    loadDiary();
    scheduleRefresh();
  }, REFRESH_INTERVAL_MS);
}

function doRefresh() {
  loadDiary();
  scheduleRefresh();
}

// ─── INIT ──────────────────────────────────────────────────
Office.onReady(() => {
  // Set practice name from template
  const pnEl = document.getElementById("diary-practice-name");
  if (pnEl) pnEl.textContent = TEMPLATE.practice_name;

  // Date navigation buttons
  document.getElementById("btn-prev-day").onclick = () => shiftDay(-1);
  document.getElementById("btn-next-day").onclick = () => shiftDay(+1);
  document.getElementById("btn-today").onclick    = () => {
    diaryDate = new Date();
    updateDateLabel();
    loadDiary();
  };
  document.getElementById("btn-refresh").onclick  = doRefresh;

  updateDateLabel();

  // Listen for token delivered by taskpane via messageChild
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

  // Signal readiness to the taskpane — it will reply with { type:"auth", token }
  try {
    Office.context.ui.messageParent(JSON.stringify({ type: "ready" }));
  } catch (_) {}

  // If a token is already in localStorage (re-open without full page reload),
  // start loading immediately without waiting for the handshake.
  if (token) {
    loadDiary();
    scheduleRefresh();
  }
});
