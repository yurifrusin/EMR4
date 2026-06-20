// ═══════════════════════════════════════════════════════════
//  EMR4 Centaur — Taskpane SPA
// ═══════════════════════════════════════════════════════════

// When served by Node dev server (localhost:3000), hit the local FastAPI directly.
// When served by FastAPI itself (via ngrok or production), use the same origin.
const BACKEND_URL = (window.location.port === "3000")
  ? "http://localhost:8001"
  : window.location.origin;
const API_BASE    = BACKEND_URL + "/api/v1";
const SESSION_ID  = "word_" + crypto.randomUUID().substring(0, 8);

// ─── STATE ──────────────────────────────────────────────────
let token          = localStorage.getItem("emr4_token");
let currentPatient = null;

// Command Centre dialog handle
let commandCentreDialog = null;
let commandCentreOpen   = false;          // pause background sync while CC is driving
let lastConsultHeader   = "";             // most recent header text inserted (full line)
let consultStarted      = false;          // a consult header has been planted this session
const NOTE_BOOKMARK     = "EMR4_NOTE_POINT"; // anchors note insertion after the consult header
const SECTION_HEADING   = "Contemporaneous Notes"; // where consults are planted
const SECTION_TAG_CN    = "emr4-section-cn";       // content-control tag for the CN heading
// A consult header line: "DD-MM-YYYY  Name  H[:MM] AM/PM  N years old."
const CONSULT_HEADER_RE = /^\d{2}-\d{2}-\d{4}\b.*\byears old\b/i;
const CONSULT_HEADER_PREFIX_RE = /^\d{2}-\d{2}-\d{4}\b.*?\byears old\.\s*/i;

// All known Heading 1 section names in a patient file (Dr Shera structure).
// repairDocumentStructure() wraps each found heading in a locked content control.
const PROTECTED_SECTIONS = [
  { text: "Contemporaneous Notes",                   tag: "emr4-section-cn" },
  { text: "Current Drugs",                           tag: "emr4-section-current-drugs" },
  { text: "Drug Reactions",                          tag: "emr4-section-drug-reactions" },
  { text: "Vaccinations",                            tag: "emr4-section-vaccinations" },
  { text: "Specialist Reports",                      tag: "emr4-section-specialist-reports" },
  { text: "Diagnostic Imaging",                      tag: "emr4-section-imaging" },
  { text: "Pathology Results",                       tag: "emr4-section-pathology" },
  { text: "ECG Records",                             tag: "emr4-section-ecg" },
  { text: "Prescription Records",                    tag: "emr4-section-prescription-records" },
  { text: "Family History",                          tag: "emr4-section-family-history" },
  { text: "Medical History",                         tag: "emr4-section-medical-history" },
  { text: "Social History",                          tag: "emr4-section-social-history" },
  { text: "Correspondence",                          tag: "emr4-section-correspondence" },
  { text: "Care Plans, Health Assessments and Recalls", tag: "emr4-section-care-plans" },
  { text: "Management Articles",                     tag: "emr4-section-management-articles" },
];

// Document mode — "patient" (default) or "diary"
let docMode = "patient";

// Consult tab state
let isLocked       = false;
let lastAiResponse = null;
let isSyncing      = false;
let mbsRowCount    = 0;
let snomedRowCount = 0;
let rxRowCount     = 0;
let lastSyncedText = "";
let debounceTimer  = null;
let backgroundSyncTimer = null;
let syncDebugState = { tick: 0, textLen: 0, fetch: "idle", http: "-", result: "-", extract: "-" };
let typeaheadTimer = null;
let mediaRecorder  = null;
let audioChunks    = [];
let isRecording    = false;
let currentAudioUrl = null;

// ═══════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════

function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-AU");
}

function setStatus(msg) {
  const el = document.getElementById("status-msg");
  if (el) el.textContent = msg;
}

function updateSyncDebug(patch = {}) {
  syncDebugState = { ...syncDebugState, ...patch };
  window.emr4DebugState = {
    ...syncDebugState,
    consultStarted,
    commandCentreOpen,
    isRecording,
    isSyncing,
    apiBase: API_BASE,
  };
}

function updateStartConsultButton() {
  const btn = document.getElementById("btn-start-consult");
  if (!btn) return;
  const canStart = Boolean(currentPatient) && !consultStarted && !commandCentreOpen;
  btn.disabled = !canStart;
  btn.textContent = consultStarted ? "Consultation Started" : "▶ Start Consultation";
  btn.title = consultStarted
    ? "A consultation is already in progress this session."
    : "Insert a dated consult header under Contemporaneous Notes (Ctrl+Alt+N)";
}

// Disable/restore all editing controls while Command Centre is the active surface.
function setTaskpaneLocked(locked) {
  const ids = [
    "btn-command-center", "btn-start-consult", "btn-lock",
    "btn-search-patient", "btn-open-file",
    "btn-add-mbs", "btn-add-snomed", "btn-add-rx",
    "btn-finalize", "consult-type",
  ];
  for (const id of ids) {
    const el = document.getElementById(id);
    if (el) el.disabled = locked;
  }
  if (!locked) updateStartConsultButton();
  // Dynamic coding rows — CSS lock so newly-rendered rows are also covered
  ["mbs-container", "snomed-container", "rx-container"].forEach(id => {
    document.getElementById(id)?.classList.toggle("cc-locked", locked);
  });
}

// ═══════════════════════════════════════════════════════════
// CONNECTIVITY INDICATOR
// ═══════════════════════════════════════════════════════════

function setConnected(ok) {
  const d = document.getElementById("status-dot");
  if (!d) return;
  d.classList.toggle("connected", ok);
  d.classList.toggle("disconnected", !ok);
  d.title = ok ? "Connected" : "Backend unreachable";
}

// ═══════════════════════════════════════════════════════════
// API HELPER — attaches JWT, handles 401, updates status-dot
// ═══════════════════════════════════════════════════════════

async function apiFetch(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (!(opts.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  if (token) headers["Authorization"] = "Bearer " + token;
  headers["ngrok-skip-browser-warning"] = "1";
  let res;
  try {
    res = await fetch(API_BASE + path, { ...opts, headers });
  } catch (networkErr) {
    // Network-level failure (no response at all — ERR_CONNECTION_REFUSED etc.)
    setConnected(false);
    throw networkErr;
  }
  if (res.status === 401) {
    logout();
    return null;
  }
  // Update the banner dot: any successful response means the backend is reachable
  setConnected(res.ok);
  return res;
}

// ═══════════════════════════════════════════════════════════
// VIEW ROUTER
// ═══════════════════════════════════════════════════════════

function showView(viewId) {
  document.querySelectorAll(".view").forEach(v => v.classList.add("hidden"));
  document.getElementById(viewId).classList.remove("hidden");
}

// ═══════════════════════════════════════════════════════════
// TAB ROUTER
// ═══════════════════════════════════════════════════════════

function showTab(tabName) {
  document.querySelectorAll(".tab-btn").forEach(b =>
    b.classList.toggle("active", b.dataset.tab === tabName)
  );
  document.querySelectorAll(".panel").forEach(p => p.classList.add("hidden"));
  const panel = document.getElementById("panel-" + tabName);
  if (panel) panel.classList.remove("hidden");
}

// ═══════════════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════════════

async function login() {
  const email    = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  const errEl    = document.getElementById("login-error");
  const btn      = document.getElementById("btn-login");
  errEl.classList.add("hidden");
  btn.disabled = true;
  btn.textContent = "Signing in…";
  try {
    const form = new URLSearchParams({ username: email, password });
    const res  = await fetch(API_BASE + "/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "ngrok-skip-browser-warning": "1",
      },
      body: form.toString(),
    });
    if (!res.ok) {
      const d = await res.json().catch(() => ({}));
      throw new Error(d.detail || "Login failed");
    }
    const data = await res.json();
    token = data.access_token;
    localStorage.setItem("emr4_token", token);
    showView("view-app");
    initApp();
  } catch (e) {
    errEl.textContent = e.message;
    errEl.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Sign In";
  }
}

function logout() {
  token = null;
  currentPatient = null;
  localStorage.removeItem("emr4_token");
  localStorage.removeItem("emr4_cc_patient_id");
  consultStarted = false;
  if (backgroundSyncTimer) {
    clearInterval(backgroundSyncTimer);
    backgroundSyncTimer = null;
  }
  document.getElementById("btn-command-center").disabled = true;
  updateStartConsultButton();
  showView("view-login");
}

// ═══════════════════════════════════════════════════════════
// PATIENT BANNER & SEARCH
// ═══════════════════════════════════════════════════════════

function setBanner(patient) {
  document.getElementById("patient-name").textContent = patient
    ? `${patient.last_name}, ${patient.first_name}`
    : "No patient loaded";
  document.getElementById("patient-meta").textContent = patient
    ? `DOB: ${formatDate(patient.date_of_birth)} · Medicare: ${patient.medicare_number || "—"}`
    : "";
}

async function searchPatients(query) {
  if (!query) return;
  const container = document.getElementById("patient-search-results");
  try {
    const res = await apiFetch(`/patients/search?q=${encodeURIComponent(query)}&limit=10`);
    if (!res) return;
    const data = await res.json();
    const patients = Array.isArray(data) ? data : [];
    container.innerHTML = "";
    if (!patients.length) {
      container.innerHTML = '<div class="search-result-item"><span class="search-result-meta">No results found.</span></div>';
      return;
    }
    patients.forEach(p => {
      const div = document.createElement("div");
      div.className = "search-result-item";
      const fileIcon = p.document_url ? ' <span title="Patient file available">📄</span>' : "";
      div.innerHTML = `
        <div class="search-result-name">${escHtml(p.last_name)}, ${escHtml(p.first_name)}${fileIcon}</div>
        <div class="search-result-meta">DOB: ${formatDate(p.date_of_birth)} · Medicare: ${escHtml(p.medicare_number || "—")}</div>
      `;
      div.onclick = () => loadPatient(p.id);
      container.appendChild(div);
    });
  } catch (err) {
    if (container) container.innerHTML = `<div class="search-result-item"><span class="search-result-meta" style="color:red">Search error: ${escHtml(String(err))}</span></div>`;
  }
}

async function loadPatient(patientId) {
  document.getElementById("search-panel").classList.add("hidden");
  document.getElementById("patient-search-input").value = "";
  document.getElementById("patient-search-results").innerHTML = "";

  const res = await apiFetch(`/patients/${patientId}/summary`);
  if (!res || !res.ok) return;
  const data = await res.json();
  currentPatient = data.patient;
  setBanner(currentPatient);
  updateOpenFileButton();
  consultStarted = false;   // new patient = new session
  document.getElementById("btn-command-center").disabled = false;
  updateStartConsultButton();

  // Sidebar — allergies (available immediately from summary)
  _renderSidebarAllergies(data.allergies || []);

  // Sidebar — meds (separate fetch, runs in background)
  apiFetch(`/patients/${patientId}/medications`).then(async r => {
    if (!r || !r.ok) return;
    _renderSidebarMeds(await r.json());
  });

  // Pre-populate whichever tabs are already visible
  if (!document.getElementById("panel-history").classList.contains("hidden")) loadHistory();
  if (!document.getElementById("panel-meds").classList.contains("hidden")) loadMeds();
  if (!document.getElementById("panel-allergies").classList.contains("hidden")) renderAllergies(data.allergies || []);

  // Silently protect section headings — no-op if already tagged, repairs if missing
  repairDocumentStructure();
}

function _renderSidebarAllergies(allergies) {
  const el = document.getElementById("sidebar-allergies");
  if (!el) return;
  if (!allergies.length) { el.innerHTML = '<span class="placeholder">None recorded.</span>'; return; }
  el.innerHTML = allergies.map(a => {
    const danger = /severe|life/i.test(a.severity || "") ? " danger" : "";
    return `<div class="sidebar-chip${danger}">
      <span class="chip-label">${escHtml(a.substance)}</span>
      <span class="chip-meta">${escHtml(a.severity || "")}</span>
    </div>`;
  }).join("");
}

function _renderSidebarMeds(meds) {
  const el = document.getElementById("sidebar-meds");
  if (!el) return;
  if (!meds.length) { el.innerHTML = '<span class="placeholder">None active.</span>'; return; }
  el.innerHTML = meds.map(m =>
    `<div class="sidebar-chip">
      <span class="chip-label">${escHtml(m.drug_name)}</span>
      <span class="chip-meta">${escHtml(m.dosage_text || "")}</span>
    </div>`
  ).join("");
}

// ═══════════════════════════════════════════════════════════
// HISTORY TAB
// ═══════════════════════════════════════════════════════════

window.loadHistory = async function () {
  if (!currentPatient) { return; }
  const list = document.getElementById("history-list");
  list.innerHTML = '<div class="placeholder">Loading…</div>';
  const res = await apiFetch(`/patients/${currentPatient.id}/encounters`);
  if (!res || !res.ok) { list.innerHTML = '<div class="placeholder">Failed to load.</div>'; return; }
  const encounters = await res.json();
  list.innerHTML = "";
  if (!encounters.length) {
    list.innerHTML = '<div class="placeholder">No encounters on record.</div>';
    return;
  }
  encounters.forEach(e => {
    const card = document.createElement("div");
    card.className = "card encounter-card";
    card.innerHTML = `
      <div class="card-header">
        <div>
          <div class="card-title">${escHtml(e.chief_complaint || "Consultation")}</div>
          <div class="card-meta">${formatDate(e.consultation_date)}</div>
        </div>
        <span class="card-badge">${escHtml(e.status || "")}</span>
      </div>
      ${e.soap_subjective ? `<div class="encounter-notes">${escHtml(e.soap_subjective)}</div>` : ""}
    `;
    list.appendChild(card);
  });
};

// ═══════════════════════════════════════════════════════════
// MEDS TAB
// ═══════════════════════════════════════════════════════════

window.loadMeds = async function () {
  if (!currentPatient) { return; }
  const list = document.getElementById("meds-list");
  list.innerHTML = '<div class="placeholder">Loading…</div>';
  const res = await apiFetch(`/patients/${currentPatient.id}/medications`);
  if (!res || !res.ok) { list.innerHTML = '<div class="placeholder">Failed to load.</div>'; return; }
  const meds = await res.json();
  list.innerHTML = "";
  if (!meds.length) {
    list.innerHTML = '<div class="placeholder">No active medications.</div>';
    return;
  }
  meds.forEach(m => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="card-header">
        <div class="card-title">${escHtml(m.drug_name)}</div>
        <span class="card-badge">${escHtml(m.route || "oral")}</span>
      </div>
      <div class="card-meta">${escHtml(m.dosage_text || "")}${m.frequency ? " · " + escHtml(m.frequency) : ""}</div>
    `;
    list.appendChild(card);
  });
};

// ═══════════════════════════════════════════════════════════
// ALLERGIES TAB
// ═══════════════════════════════════════════════════════════

function renderAllergies(allergies) {
  const list = document.getElementById("allergies-list");
  list.innerHTML = "";
  if (!allergies.length) {
    list.innerHTML = '<div class="placeholder">No recorded allergies.</div>';
    return;
  }
  allergies.forEach(a => {
    const sev = (a.severity || "").toLowerCase();
    const badgeClass = sev === "severe" || sev === "life-threatening" ? "severe" : "allergy";
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <div class="card-header">
        <div>
          <div class="card-title">${escHtml(a.substance)}</div>
          <div class="card-meta">${escHtml(a.reaction || "")}</div>
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span class="card-badge ${badgeClass}">${escHtml(a.severity || "—")}</span>
          <button class="btn btn-xs btn-danger" onclick="deleteAllergy('${escHtml(a.id)}')">✕</button>
        </div>
      </div>
    `;
    list.appendChild(card);
  });
}

async function loadAllergies() {
  if (!currentPatient) return;
  const res = await apiFetch(`/patients/${currentPatient.id}/allergies`);
  if (!res || !res.ok) return;
  renderAllergies(await res.json());
}

window.addAllergy = async function () {
  if (!currentPatient) { alert("Load a patient first."); return; }
  const substance = document.getElementById("allergy-substance").value.trim();
  const reaction  = document.getElementById("allergy-reaction").value.trim();
  const severity  = document.getElementById("allergy-severity").value;
  if (!substance) return;
  const res = await apiFetch(`/patients/${currentPatient.id}/allergies`, {
    method: "POST",
    body: JSON.stringify({ substance, reaction, severity, allergy_type: "Drug" }),
  });
  if (!res || !res.ok) { alert("Failed to add allergy."); return; }
  document.getElementById("allergy-substance").value = "";
  document.getElementById("allergy-reaction").value = "";
  document.getElementById("allergy-severity").value = "";
  loadAllergies();
};

window.deleteAllergy = async function (allergyId) {
  if (!currentPatient) return;
  await apiFetch(`/patients/${currentPatient.id}/allergies/${allergyId}`, { method: "DELETE" });
  loadAllergies();
};

// ═══════════════════════════════════════════════════════════
// LETTERS TAB
// ═══════════════════════════════════════════════════════════

window.draftLetter = async function () {
  if (!currentPatient) { alert("Load a patient first."); return; }
  const btn       = document.getElementById("btn-draft-letter");
  const letterType = document.getElementById("letter-type").value;
  const recipient  = document.getElementById("letter-recipient").value.trim();
  const specialty  = document.getElementById("letter-specialty").value.trim();
  const reason     = document.getElementById("letter-reason").value.trim();

  btn.disabled = true;
  btn.textContent = "Drafting…";
  try {
    const res = await apiFetch(`/patients/${currentPatient.id}/letters/draft`, {
      method: "POST",
      body: JSON.stringify({
        letter_type: letterType,
        recipient_name: recipient || null,
        recipient_specialty: specialty || null,
        reason,
      }),
    });
    if (!res || !res.ok) { alert("Letter draft failed."); return; }
    const data = await res.json();
    document.getElementById("letter-subject").textContent = data.subject_line || "";
    document.getElementById("letter-body").value = data.letter_text || "";
    document.getElementById("letter-output").classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.innerHTML = "✨ Draft with AI";
  }
};

window.insertLetterIntoWord = async function () {
  const text = document.getElementById("letter-body").value;
  if (!text) return;
  await Word.run(async ctx => {
    ctx.document.body.insertText(text, Word.InsertLocation.replace);
    await ctx.sync();
  });
};

window.copyLetter = function () {
  const text = document.getElementById("letter-body").value;
  navigator.clipboard.writeText(text).catch(() => {
    document.getElementById("letter-body").select();
    document.execCommand("copy");
  });
};

// ═══════════════════════════════════════════════════════════
// CONSULT TAB — LOCK / UNLOCK
// ═══════════════════════════════════════════════════════════

window.toggleLock = function () {
  isLocked = !isLocked;
  updateLockUI();
  if (!isLocked && lastAiResponse) {
    updateFormFields(lastAiResponse);
    setStatus("Last sync: " + new Date().toLocaleTimeString());
  }
};

function autoLock() {
  if (!isLocked) { isLocked = true; updateLockUI(); }
}

function updateLockUI() {
  const btn = document.getElementById("btn-lock");
  if (!btn) return;
  if (isLocked) {
    btn.className = "btn btn-sm btn-lock locked";
    btn.querySelector(".lock-icon").textContent = "🔒";
    btn.querySelector(".lock-label").textContent = "Locked";
  } else {
    btn.className = "btn btn-sm btn-lock unlocked";
    btn.querySelector(".lock-icon").textContent = "🔓";
    btn.querySelector(".lock-label").textContent = "AI live";
  }
}

// ═══════════════════════════════════════════════════════════
// CONSULT TAB — BACKGROUND SYNC
// ═══════════════════════════════════════════════════════════

async function getDocumentText() {
  return Word.run(async ctx => {
    const body = ctx.document.body;
    body.load("text");
    await ctx.sync();
    return body.text;
  });
}

async function runBackgroundSync() {
  if (isRecording || isSyncing || commandCentreOpen) {
    updateSyncDebug({ fetch: isRecording ? "recording" : isSyncing ? "busy" : "cc-open" });
    return;
  }
  // Don't analyse anything until the doctor explicitly starts a consultation this
  // session — otherwise a previously finalised consult left in the document would
  // be re-analysed on open and fill the fields uninvited.
  if (!consultStarted) {
    if (!isLocked) updateFormFields({});
    setStatus("Ready — click Start Consultation to begin.");
    updateSyncDebug({ fetch: "not-started", textLen: 0, http: "-", result: "-" });
    return;
  }
  isSyncing = true;
  let timeoutId = null;
  try {
    updateSyncDebug({ tick: syncDebugState.tick + 1, fetch: "extracting", http: "-", result: "-" });
    const text = await getCurrentConsultText();
    const textLen = (text || "").trim().length;
    updateSyncDebug({ textLen, fetch: "extracted" });
    if (!text || !text.trim()) {
      if (!isLocked) updateFormFields({});
      setStatus("Listening — type your consultation notes…");
      lastSyncedText = "";
      updateSyncDebug({ textLen: 0, fetch: "empty", http: "-", result: "no-text" });
      return;
    }
    if (text === lastSyncedText) {
      updateSyncDebug({ fetch: "unchanged", result: "already-synced" });
      return;
    }
    setStatus(isLocked ? "AI running in background..." : `Analysing ${text.length} chars...`);
    updateSyncDebug({ fetch: "posting", http: "-", result: "request" });

    const headers = {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "1",
    };
    if (token) headers["Authorization"] = "Bearer " + token;
    const abort = new AbortController();
    timeoutId = setTimeout(() => abort.abort(), 45000);
    const res = await fetch(API_BASE + "/analyze-consultation", {
      method: "POST",
      headers,
      signal: abort.signal,
      body: JSON.stringify({
        document_id: SESSION_ID,
        text_delta: text,
        is_finalized: false,
        clinician_overrides: null,
      }),
    });
    updateSyncDebug({ fetch: "response", http: String(res.status) });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status}${body ? ": " + body.slice(0, 120) : ""}`);
    }
    const data = await res.json();
    lastAiResponse = data;
    lastSyncedText = text;
    const meta = data.encounter_metadata || {};
    const mbsCount = meta.mbs_item_candidates?.length || 0;
    const dxCount = data.clinical_diagnoses?.length || 0;
    const rxCount = data.medications_and_prescriptions?.length || 0;
    updateSyncDebug({ fetch: "ok", result: `mbs:${mbsCount} dx:${dxCount} rx:${rxCount}` });
    if (!isLocked) {
      updateFormFields(data);
      setStatus("Synced " + new Date().toLocaleTimeString());
    } else {
      setStatus("🔒 Locked — unlock to apply.");
    }
  } catch (e) {
    console.warn("EMR AI sync failed", e);
    updateSyncDebug({
      fetch: e?.name === "AbortError" ? "timeout" : "error",
      result: String(e?.message || "backend").slice(0, 80),
    });
    setStatus(e?.name === "AbortError" ? "AI analysis slow - retrying..." : `AI sync failed - retrying (${e?.message || "backend"})`);
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
    isSyncing = false;
    updateSyncDebug();
  }
}

window.forceAiSync = function () {
  lastSyncedText = "";
  return runBackgroundSync();
};

// ═══════════════════════════════════════════════════════════
// CONSULT TAB — AUDIO SCRIBE
// ═══════════════════════════════════════════════════════════

async function toggleRecording() {
  const btn         = document.getElementById("btn-record");
  const audioStatus = document.getElementById("audio-status");
  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks   = [];
      mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
      mediaRecorder.onstop = processAudio;
      mediaRecorder.start();
      isRecording = true;
      btn.textContent = "⏹️ Stop Recording";
      btn.classList.add("recording");
      audioStatus.classList.remove("hidden");
      setStatus("Capturing consultation audio…");
    } catch {
      alert("Microphone access is required for the AI Scribe.");
    }
  } else {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(t => t.stop());
    isRecording = false;
    btn.textContent = "🎤 Start Recording";
    btn.classList.remove("recording");
    audioStatus.classList.add("hidden");
  }
}

async function processAudio() {
  setStatus("⏳ Processing audio with Vertex AI…");
  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const form = new FormData();
  form.append("audio_file", blob, "consultation.webm");
  try {
    const headers = {};
    if (token) headers["Authorization"] = "Bearer " + token;
    const res  = await fetch(API_BASE + "/scribe-consultation", { method: "POST", headers, body: form });
    const data = await res.json();

    updateFormFields(data);

    if (data.audio_url) {
      currentAudioUrl = data.audio_url;
      const player    = document.getElementById("audio-playback");
      player.src      = BACKEND_URL + data.audio_url;
      player.classList.remove("hidden");
    }
    if (data.raw_transcript) {
      document.getElementById("raw-transcript").value = data.raw_transcript;
      document.getElementById("transcript-row").classList.remove("hidden");
    }

    setStatus("✅ Audio scribe complete.");
    isLocked = true;
    updateLockUI();

    if (data.generated_clinical_note) {
      Word.run(async ctx => {
        ctx.document.body.insertParagraph(data.generated_clinical_note, Word.InsertLocation.end);
        await ctx.sync();
      });
    }
  } catch {
    setStatus("❌ Scribe failed.");
  }
}

window.toggleTranscript = function () {
  document.getElementById("raw-transcript").classList.toggle("hidden");
};

// ═══════════════════════════════════════════════════════════
// CONSULT TAB — FORM RENDERING
// ═══════════════════════════════════════════════════════════

function updateFormFields(response) {
  const meta = response.encounter_metadata || {};
  const consultField = document.getElementById("consult-type");
  if (consultField && !consultField.value) consultField.value = meta.consultation_type || "";

  const mbsItems  = meta.mbs_item_candidates?.length ? meta.mbs_item_candidates : [{}];
  const diagnoses = response.clinical_diagnoses?.length ? response.clinical_diagnoses : [{}];
  const rx        = response.medications_and_prescriptions?.length ? response.medications_and_prescriptions : [{}];

  document.getElementById("mbs-container").innerHTML = "";    mbsRowCount    = 0;
  document.getElementById("snomed-container").innerHTML = ""; snomedRowCount = 0;
  document.getElementById("rx-container").innerHTML = "";     rxRowCount     = 0;

  mbsItems.forEach(m  => appendMbsRow(m.item_number || "", m.description || ""));
  diagnoses.forEach(d => appendSnomedRow(d.term || "", d.snomed_ct_au_code || ""));
  rx.forEach(m        => appendRxRow(m.drug_name || "", m.dosage_text || ""));

  // Mirror AI diagnoses into the sidebar
  const sidebarDx = document.getElementById("sidebar-dx");
  if (sidebarDx) {
    const realDx = diagnoses.filter(d => d.term);
    if (realDx.length) {
      sidebarDx.innerHTML = realDx.map(d =>
        `<div class="sidebar-chip"><span class="chip-label">${escHtml(d.term)}</span></div>`
      ).join("");
    } else {
      sidebarDx.innerHTML = '<span class="placeholder">Listening…</span>';
    }
  }
}

// ═══════════════════════════════════════════════════════════
// ROW BUILDERS
// ═══════════════════════════════════════════════════════════

function appendMbsRow(itemNumber, description) {
  const i = mbsRowCount++;
  const div = document.createElement("div");
  div.className = "coding-row";
  div.id = `mbs-group-${i}`;
  div.innerHTML = `
    <div class="input-wrapper">
      <input type="text" id="mbs-item-${i}" class="input" value="${escHtml(itemNumber)}" autocomplete="off" placeholder="MBS code…">
      <div id="mbs-suggestions-${i}" class="autocomplete-results"></div>
    </div>
    <input type="text" id="mbs-desc-${i}" class="input" value="${escHtml(description)}" placeholder="Description" readonly style="flex:2">
    <button class="btn-remove" onclick="removeRow('mbs-group-${i}')">✕</button>
  `;
  document.getElementById("mbs-container").appendChild(div);
  document.getElementById(`mbs-item-${i}`).addEventListener("keyup", () => handleKeystroke("mbs", i));
}

function appendSnomedRow(term, code) {
  const i = snomedRowCount++;
  const div = document.createElement("div");
  div.className = "coding-row";
  div.id = `snomed-group-${i}`;
  div.innerHTML = `
    <div class="input-wrapper" style="flex:2">
      <input type="text" id="snomed-term-${i}" class="input" value="${escHtml(term)}" autocomplete="off" placeholder="Diagnosis…">
      <div id="snomed-suggestions-${i}" class="autocomplete-results"></div>
    </div>
    <input type="text" id="snomed-code-${i}" class="input" value="${escHtml(code)}" placeholder="SNOMED code" readonly style="flex:0 0 90px">
    <button class="btn-remove" onclick="removeRow('snomed-group-${i}')">✕</button>
  `;
  document.getElementById("snomed-container").appendChild(div);
  document.getElementById(`snomed-term-${i}`).addEventListener("keyup", () => handleKeystroke("snomed", i));
}

function appendRxRow(drugName, dosage) {
  const i = rxRowCount++;
  const div = document.createElement("div");
  div.className = "coding-row";
  div.id = `rx-group-${i}`;
  div.innerHTML = `
    <input type="text" id="rx-name-${i}" class="input" value="${escHtml(drugName)}" placeholder="Drug name…" style="flex:2">
    <input type="text" id="rx-dose-${i}" class="input" value="${escHtml(dosage)}" placeholder="Dosage…" style="flex:1">
    <button class="btn-remove" onclick="removeRow('rx-group-${i}')">✕</button>
  `;
  document.getElementById("rx-container").appendChild(div);
}

window.addMbsRow    = function () { autoLock(); appendMbsRow("", ""); };
window.addSnomedRow = function () { autoLock(); appendSnomedRow("", ""); };
window.addRxRow     = function () { autoLock(); appendRxRow("", ""); };
window.removeRow    = function (id) { autoLock(); document.getElementById(id)?.remove(); };

// ═══════════════════════════════════════════════════════════
// AUTOCOMPLETE ENGINE
// ═══════════════════════════════════════════════════════════

async function handleKeystroke(type, index) {
  clearTimeout(typeaheadTimer);
  const inputEl = document.getElementById(type === "mbs" ? `mbs-item-${index}` : `snomed-term-${index}`);
  if (!inputEl) return;
  const query = inputEl.value.trim();
  const box   = document.getElementById(`${type}-suggestions-${index}`);
  if (!box) return;
  if (query.length < 2) { box.style.display = "none"; return; }

  typeaheadTimer = setTimeout(async () => {
    box.style.display = "block";
    box.innerHTML = '<div class="autocomplete-searching">Searching…</div>';
    try {
      const endpoint = type === "mbs" ? "search-mbs" : "search-snomed";
      const res = await fetch(`${API_BASE}/${endpoint}?q=${encodeURIComponent(query)}`);
      renderSuggestions(await res.json(), type, index);
    } catch {
      box.innerHTML = '<div class="autocomplete-searching">Search failed.</div>';
    }
  }, 400);
}

function renderSuggestions(results, type, index) {
  const box = document.getElementById(`${type}-suggestions-${index}`);
  if (!box) return;
  box.innerHTML = "";
  if (!results?.length) {
    box.innerHTML = '<div class="autocomplete-searching">No matches found.</div>';
    setTimeout(() => (box.style.display = "none"), 2000);
    return;
  }
  results.slice(0, 5).forEach(item => {
    const div = document.createElement("div");
    div.className = "autocomplete-item";
    if (type === "mbs") {
      div.textContent = `${item.item_number} — ${item.description.substring(0, 55)}`;
      div.onclick = () => {
        document.getElementById(`mbs-item-${index}`).value = item.item_number;
        document.getElementById(`mbs-desc-${index}`).value = item.description;
        box.style.display = "none";
      };
    } else {
      div.textContent = item.term;
      div.onclick = () => {
        document.getElementById(`snomed-term-${index}`).value = item.term;
        document.getElementById(`snomed-code-${index}`).value = item.concept_id;
        box.style.display = "none";
      };
    }
    box.appendChild(div);
  });
}

document.addEventListener("click", e => {
  if (!e.target.closest(".input-wrapper")) {
    document.querySelectorAll(".autocomplete-results").forEach(el => (el.style.display = "none"));
  }
});

// ═══════════════════════════════════════════════════════════
// FINALIZE RECORD
// ═══════════════════════════════════════════════════════════

async function approveAndFinalize() {
  setStatus("⏳ Saving to database…");
  const consultType = document.getElementById("consult-type")?.value || "";
  const overrides   = { consultation_type: consultType, mbs_items: [], diagnoses: [], medications: [] };

  for (let i = 0; i < mbsRowCount; i++) {
    const code = document.getElementById(`mbs-item-${i}`)?.value.trim();
    if (code) overrides.mbs_items.push({ item_number: code, description: document.getElementById(`mbs-desc-${i}`)?.value || "" });
  }
  for (let i = 0; i < snomedRowCount; i++) {
    const term = document.getElementById(`snomed-term-${i}`)?.value.trim();
    if (term) overrides.diagnoses.push({ term, snomed_ct_au_code: document.getElementById(`snomed-code-${i}`)?.value || "" });
  }
  for (let i = 0; i < rxRowCount; i++) {
    const drug = document.getElementById(`rx-name-${i}`)?.value.trim();
    if (drug) overrides.medications.push({ drug_name: drug, dosage_text: document.getElementById(`rx-dose-${i}`)?.value || "" });
  }

  try {
    const text    = await getCurrentConsultText();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;
    const res = await fetch(API_BASE + "/finalize", {
      method: "POST",
      headers,
      body: JSON.stringify({ document_id: SESSION_ID, text_delta: text, clinician_overrides: overrides, audio_url: currentAudioUrl, patient_id: currentPatient ? String(currentPatient.id) : null }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data._saved === false) {
        setStatus("❌ " + (data._save_error || "Save failed"));
      } else {
        setStatus("✅ Record finalised & saved.");
        isLocked = true;
        updateLockUI();
        consultStarted = false;   // allow a new consultation to be started
        updateStartConsultButton();
        const btn = document.getElementById("btn-finalize");
        if (btn) { btn.disabled = true; btn.textContent = "✅ Finalised"; }
        const player = document.getElementById("audio-playback");
        if (player) { player.pause(); player.src = ""; player.classList.add("hidden"); }
        document.getElementById("transcript-row")?.classList.add("hidden");
        currentAudioUrl = null;
      }
    } else {
      setStatus("❌ Server error " + res.status);
    }
  } catch {
    setStatus("❌ Network error. Check the backend.");
  }
}

// ═══════════════════════════════════════════════════════════
// DIARY WINDOW
// ═══════════════════════════════════════════════════════════

const DIARY_URL = "https://yurifrusin.github.io/EMR4/diary/diary.html";
let diaryDialogRef = null;

// NOTE: synchronous within the click gesture — same rule as openCommandCentre.
// No patient guard — the diary is practice/day-scoped, not patient-scoped.
function openDiary() {
  if (diaryDialogRef) {
    try {
      diaryDialogRef.messageChild(JSON.stringify({ type: "focus" }));
      setStatus("Diary window already open.");
      return;
    } catch (_) {
      diaryDialogRef = null;
    }
  }

  Office.context.ui.displayDialogAsync(DIARY_URL, { height: 90, width: 90 }, result => {
    if (result.status === Office.AsyncResultStatus.Failed) {
      setStatus("Could not open Diary: " + result.error.message);
      return;
    }
    diaryDialogRef = result.value;

    diaryDialogRef.addEventHandler(Office.EventType.DialogMessageReceived, arg => {
      try {
        const msg = JSON.parse(arg.message);
        if (msg.type === "ready") {
          // Deliver the auth token so the diary can call the API
          diaryDialogRef.messageChild(JSON.stringify({ type: "auth", token }));
        }
      } catch (_) {}
    });

    diaryDialogRef.addEventHandler(Office.EventType.DialogEventReceived, () => {
      diaryDialogRef = null;
    });
  });
}

// ═══════════════════════════════════════════════════════════
// COMMAND CENTRE
// ═══════════════════════════════════════════════════════════

const CC_URL = "https://yurifrusin.github.io/EMR4/command-centre/command-centre.html";

// NOTE: not async, and displayDialogAsync is called synchronously within the
// click gesture (no await before it). Awaiting first breaks the user-gesture
// chain, which makes Office on the web more likely to block/prompt the window.
function openCommandCentre() {
  if (!currentPatient) {
    setStatus("Load a patient before opening Command Centre.");
    return;
  }

  // Pause the taskpane's own background analysis — the Command Centre is now
  // the single source of truth, so the two AIs don't show conflicting coding.
  commandCentreOpen = true;
  setTaskpaneLocked(true);
  const fbtnCC = document.getElementById("btn-finalize");
  if (fbtnCC) fbtnCC.textContent = "Finalise in Command Centre";
  setStatus("Command Centre open — taskpane editing paused.");

  // Pass patient ID via URL param — more reliable than localStorage cross-context
  const url = `${CC_URL}?pid=${currentPatient.id}`;

  // Must open as a separate window (not displayInIframe) — Office's iframe dialog
  // does not grant microphone access, which the AI Scribe requires.
  Office.context.ui.displayDialogAsync(url, { height: 75, width: 55 }, result => {
    if (result.status === Office.AsyncResultStatus.Failed) {
      setStatus("Could not open Command Centre: " + result.error.message);
      commandCentreOpen = false;
      return;
    }
    commandCentreDialog = result.value;

    // Plant the dated consult header now (after the window opened), unless one
    // was already started this session.
    if (!consultStarted) {
      insertConsultHeader(currentPatient).then(inserted => {
        if (inserted) {
          consultStarted = true;
          lastSyncedText = "";
          updateStartConsultButton();
        }
      });
    }

    commandCentreDialog.addEventHandler(Office.EventType.DialogMessageReceived, arg => {
      try {
        const msg = JSON.parse(arg.message);
        if (msg.type === "ready") {
          commandCentreDialog.messageChild(JSON.stringify({ type: "auth", token }));
          if (lastAiResponse) {
            commandCentreDialog.messageChild(JSON.stringify({ type: "ai_context", data: lastAiResponse }));
          }
        } else if (msg.type === "insert_note" && msg.text) {
          insertNoteIntoWord(msg.text);
        } else if (msg.type === "consult_finalized") {
          // Reflect the Command Centre's finalised coding in the taskpane Consult
          // tab and lock it so background sync won't overwrite it.
          if (msg.data) { updateFormFields(msg.data); isLocked = true; updateLockUI(); }
          consultStarted = false;                 // allow a new consult to be started
          updateStartConsultButton();
          const fbtn = document.getElementById("btn-finalize");
          if (fbtn) { fbtn.disabled = true; fbtn.textContent = "✅ Finalised"; }
          setStatus("✅ Consult finalised in Command Centre.");
          if (currentPatient) loadPatient(currentPatient.id);  // refresh history/meds/sidebar
        } else if (msg.type === "reload_patient" && currentPatient) {
          loadPatient(currentPatient.id);
        }
      } catch (_) {}
    });

    commandCentreDialog.addEventHandler(Office.EventType.DialogEventReceived, () => {
      commandCentreDialog = null;
      commandCentreOpen = false;          // resume taskpane background analysis
      lastSyncedText = "";                // force a fresh re-sync of the document
      setTaskpaneLocked(false);
      // If no consult is active (e.g. CC already finalised it), keep Finalize disabled
      const fbtnClose = document.getElementById("btn-finalize");
      if (fbtnClose) {
        if (consultStarted) {
          fbtnClose.textContent = "Approve & Finalise Record";
        } else {
          fbtnClose.disabled = true;
        }
      }
    });
  });
}

// Time to the nearest half hour: "12 PM" on the hour, otherwise "5:30 PM".
function formatHalfHour(d) {
  const r = new Date(d);
  r.setSeconds(0, 0);
  r.setMinutes(Math.round(r.getMinutes() / 30) * 30); // 60 rolls into the next hour
  let h = r.getHours();
  const ampm = h >= 12 ? "PM" : "AM";
  h = h % 12; if (h === 0) h = 12;
  const mins = r.getMinutes();
  return mins === 0 ? `${h} ${ampm}` : `${h}:${String(mins).padStart(2, "0")} ${ampm}`;
}

// Builds the consult header in two parts so the date can be bold and the rest plain.
function buildConsultHeader(patient) {
  const now = new Date();
  const dd   = String(now.getDate()).padStart(2, "0");
  const mm   = String(now.getMonth() + 1).padStart(2, "0");
  const yyyy = now.getFullYear();
  const dob  = new Date(patient.date_of_birth);
  let age = yyyy - dob.getFullYear();
  if (now.getMonth() - dob.getMonth() < 0 ||
      (now.getMonth() === dob.getMonth() && now.getDate() < dob.getDate())) age--;
  const datePart = `${dd}-${mm}-${yyyy}`;
  const restPart = `${patient.first_name} ${patient.last_name}  ${formatHalfHour(now)}  ${age} years old.`;
  return { datePart, restPart, full: `${datePart}  ${restPart}` };
}

// Wraps each known Heading 1 section in a locked content control so it cannot be
// accidentally deleted or reformatted. Safe to call repeatedly — skips already-tagged
// sections. Called automatically when a patient is loaded.
async function repairDocumentStructure() {
  try {
    await Word.run(async ctx => {
      const existing = ctx.document.contentControls;
      existing.load("items/tag");
      const paras = ctx.document.body.paragraphs;
      paras.load("items/text,items/styleBuiltIn");
      await ctx.sync();

      const existingTags = new Set(existing.items.map(cc => cc.tag));
      const tagMap = new Map(PROTECTED_SECTIONS.map(s => [s.text.toLowerCase(), s.tag]));

      let repaired = 0;
      for (const para of paras.items) {
        if (para.styleBuiltIn !== Word.BuiltInStyleName.heading1) continue;
        const text = (para.text || "").trim();
        const tag = tagMap.get(text.toLowerCase());
        if (!tag || existingTags.has(tag)) continue;

        const cc = para.insertContentControl();
        cc.tag          = tag;
        cc.title        = text;
        cc.cannotDelete = true;
        cc.cannotEdit   = true;
        cc.appearance   = "Hidden";   // string literal — enum may be undefined at runtime
        repaired++;
      }
      await ctx.sync();
      if (repaired > 0) setStatus(`Document structure secured — ${repaired} section${repaired !== 1 ? "s" : ""} protected.`);
    });
  } catch (e) {
    setStatus("Structure repair error: " + (e.message || String(e)));
  }
}

async function insertConsultHeader(patient) {
  const { datePart, restPart, full } = buildConsultHeader(patient);
  lastConsultHeader = full;
  try {
    await Word.run(async ctx => {
      const paras = ctx.document.body.paragraphs;
      paras.load("items/text,items/styleBuiltIn");
      const cnCtrls = ctx.document.contentControls.getByTag(SECTION_TAG_CN);
      cnCtrls.load("items");
      await ctx.sync();

      // Prefer content-control tag (survives minor text edits); fall back to text search
      let insertTarget = cnCtrls.items.length > 0 ? cnCtrls.items[0] : null;
      if (!insertTarget) {
        for (const p of paras.items) {
          if (p.styleBuiltIn === Word.BuiltInStyleName.heading1 &&
              (p.text || "").trim().toLowerCase() === SECTION_HEADING.toLowerCase()) {
            insertTarget = p; break;
          }
        }
      }

      const para = insertTarget
        ? insertTarget.insertParagraph(datePart, Word.InsertLocation.after)
        : ctx.document.body.insertParagraph(datePart, Word.InsertLocation.end);
      para.styleBuiltIn = Word.BuiltInStyleName.normal;
      para.font.bold = true;                              // date in bold
      const rest = para.insertText("  " + restPart, Word.InsertLocation.end);
      rest.font.bold = false;                             // name/time/age plain
      // Bookmark the end of the header so the SOAP note inserts right after it
      para.getRange(Word.RangeLocation.end).insertBookmark(NOTE_BOOKMARK);
      para.getRange(Word.RangeLocation.end).select();
      await ctx.sync();
    });
    return true;
  } catch (e) {
    setStatus("Header insert failed: " + e.message);
    return false;
  }
}

// Starts a new consultation: plants the dated header under Contemporaneous Notes.
window.startConsultation = async function () {
  if (!currentPatient) { setStatus("Load a patient before starting a consultation."); return; }
  if (consultStarted) { setStatus("A consultation is already in progress this session."); return; }
  const inserted = await insertConsultHeader(currentPatient);
  if (!inserted) return;
  consultStarted = true;
  lastSyncedText = "";
  lastAiResponse = null;
  updateSyncDebug({ tick: 0, textLen: 0, fetch: "started", http: "-", result: "-", extract: "-" });
  updateStartConsultButton();
  isLocked = false; updateLockUI();   // fresh consult — AI live again
  updateFormFields({});               // clear any previously displayed coding
  const fbtn = document.getElementById("btn-finalize");
  if (fbtn) { fbtn.disabled = false; fbtn.textContent = "Approve & Finalise Record"; }
  setStatus("Consultation started - type after the header; press Enter for a new line.");
  setTimeout(runBackgroundSync, 0);
};

// Reads ONLY the current consultation's notes: from the planted header down to
// the previous consult header or the next section heading — never the whole doc.
async function getCurrentConsultText() {
  return Word.run(async ctx => {
    const paras = ctx.document.body.paragraphs;
    paras.load("items/text,items/styleBuiltIn");
    await ctx.sync();
    const items = paras.items;
    const sectionHeadings = new Set(PROTECTED_SECTIONS.map(s => s.text.toLowerCase()));
    const paraText = p => (p.text || "").trim();
    const compact = s => String(s || "").replace(/\s+/g, " ").trim();
    const isHeading1 = p =>
      p.styleBuiltIn === Word.BuiltInStyleName.heading1 ||
      sectionHeadings.has(paraText(p).toLowerCase());
    let cnIdx = items.findIndex(p =>
      paraText(p).toLowerCase() === SECTION_HEADING.toLowerCase());
    if (cnIdx === -1) {
      updateSyncDebug({ extract: "cn:-1 hdr:-1 lines:0" });
      return "";
    }

    // Locate the current consult header (first matching line after the section heading)
    const wantedHeader = compact(lastConsultHeader);
    let startIdx = -1;
    let selected = null;
    let fallback = null;
    for (let i = cnIdx + 1; i < items.length; i++) {
      if (isHeading1(items[i])) break;                          // hit next section — no consult yet
      const text = paraText(items[i]);
      if (!CONSULT_HEADER_RE.test(text)) continue;
      const candidate = { idx: i, tail: text.replace(CONSULT_HEADER_PREFIX_RE, "").trim() };
      if (!fallback) fallback = candidate;
      if (!wantedHeader || compact(text).startsWith(wantedHeader)) {
        selected = candidate;
        startIdx = i;
        break;
      }
    }
    if (startIdx === -1 && fallback) {
      selected = fallback;
      startIdx = fallback.idx;
    }
    if (startIdx === -1) {
      updateSyncDebug({ extract: `cn:${cnIdx} hdr:-1 lines:0` });
      return "";
    }

    // Collect notes until the previous consult header or the next section heading
    const lines = selected?.tail ? [selected.tail] : [];
    for (let i = startIdx + 1; i < items.length; i++) {
      const p = items[i];
      if (isHeading1(p)) break;
      if (CONSULT_HEADER_RE.test((p.text || "").trim())) break;
      lines.push(p.text);
    }
    updateSyncDebug({ extract: `cn:${cnIdx} hdr:${startIdx} lines:${lines.length}` });
    return lines.join("\n").trim();
  });
}

async function insertNoteIntoWord(text) {
  // Collapse the SOAP note into a single paragraph to save space in the file —
  // the S:/O:/A:/P: labels still delineate the sections inline.
  const oneLine = (text || "").split("\n").map(s => s.trim()).filter(Boolean).join(" ");
  try {
    await Word.run(async ctx => {
      // Prefer inserting right after the consult header (bookmarked), so the note
      // lands where the doctor is looking — not at the absolute end of the document.
      const bm = ctx.document.getBookmarkRangeOrNullObject(NOTE_BOOKMARK);
      await ctx.sync();

      const para = bm.isNullObject
        ? ctx.document.body.insertParagraph(oneLine, Word.InsertLocation.end)
        : bm.insertParagraph(oneLine, Word.InsertLocation.after);
      para.styleBuiltIn = Word.BuiltInStyleName.normal;
      para.font.bold = false;
      // Move the bookmark to the end of the note so any later insert appends below it
      para.getRange(Word.RangeLocation.end).insertBookmark(NOTE_BOOKMARK);
      await ctx.sync();
    });
    setStatus("Note inserted into document.");
  } catch (e) {
    setStatus("Insert failed: " + e.message);
  }
}

// ═══════════════════════════════════════════════════════════
// DOCUMENT-TYPE DETECTION
// ═══════════════════════════════════════════════════════════

// Read the <emr4:document-type> Custom XML Part.
// Falls back to filename heuristic if the XML read fails (Word Online risk).
async function detectDocumentType() {
  // Primary: Custom XML Part (injected by create_patient_file.py / create_diary_file.py).
  // agents.md flags this as ⚠️ Medium risk in Word Online — wrap defensively.
  try {
    const parts = await new Promise((resolve, reject) => {
      Office.context.document.customXmlParts.getByNamespaceAsync(
        "http://emr4.com/ns/document",
        r => r.status === Office.AsyncResultStatus.Succeeded
          ? resolve(r.value) : reject(new Error(r.error))
      );
    });
    if (parts && parts.length > 0) {
      const xml = await new Promise((resolve, reject) => {
        parts[0].getXmlAsync(
          r => r.status === Office.AsyncResultStatus.Succeeded
            ? resolve(r.value) : reject(new Error(r.error))
        );
      });
      const m = xml.match(/<emr4:document-type>([\w]+)<\/emr4:document-type>/);
      if (m) {
        console.log("[EMR4] Custom XML document-type:", m[1]);
        return m[1].toLowerCase();   // "patient" or "diary"
      }
    }
  } catch (e) {
    console.warn("[EMR4] Custom XML read failed — using filename fallback:", e.message || e);
  }

  // Fallback: parse the filename.
  const docUrl = Office.context.document.url || "";
  let title = "";
  try {
    await Word.run(async ctx => {
      const props = ctx.document.properties;
      props.load("title");
      await ctx.sync();
      title = (props.title || "").trim();
    });
  } catch (_) { /* ignore */ }
  if (!title && docUrl) {
    const raw = docUrl.split("?")[0].split("/").pop();
    if (raw && /\.docx$/i.test(raw)) title = decodeURIComponent(raw).replace(/\.docx$/i, "").trim();
  }

  const type = /^Diary[_\s]/i.test(title) ? "diary" : "patient";
  console.log("[EMR4] Filename fallback document-type:", type, "(title:", title, ")");
  return type;
}

// ═══════════════════════════════════════════════════════════
// NEW PATIENT FORM
// ═══════════════════════════════════════════════════════════

const NEW_PATIENT_FIELD_IDS = [
  "np-first-name", "np-last-name", "np-dob", "np-sex", "np-medicare",
  "np-medicare-irn", "np-ihi", "np-phone", "np-address", "np-suburb",
  "np-state", "np-postcode",
];

const HARD_DUPLICATE_REASONS = new Set(["same_ihi", "same_medicare_card_and_irn"]);

let pendingNewPatientPayload = null;

function setNewPatientResult(html) {
  const result = document.getElementById("new-patient-result");
  if (result) result.innerHTML = html || "";
}

function setNewPatientFieldsDisabled(disabled) {
  NEW_PATIENT_FIELD_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.disabled = disabled;
  });
}

function resetNewPatientActions() {
  const createBtn = document.getElementById("btn-np-create");
  const cancelBtn = document.getElementById("btn-np-cancel");
  pendingNewPatientPayload = null;
  setNewPatientFieldsDisabled(false);
  if (createBtn) {
    createBtn.disabled = false;
    createBtn.textContent = "Create Patient File";
    createBtn.onclick = createNewPatient;
  }
  if (cancelBtn) {
    cancelBtn.disabled = false;
    cancelBtn.textContent = "Cancel";
    cancelBtn.onclick = closeNewPatientForm;
  }
}

function clearNewPatientFields() {
  NEW_PATIENT_FIELD_IDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
}

function collectNewPatientPayload() {
  const fn  = document.getElementById("np-first-name").value.trim();
  const ln  = document.getElementById("np-last-name").value.trim();
  const dob = document.getElementById("np-dob").value;
  if (!fn || !ln || !dob) {
    throw new Error("First name, last name, and date of birth are required.");
  }

  return {
    first_name:       fn,
    last_name:        ln,
    date_of_birth:    dob,
    sex:              document.getElementById("np-sex").value || null,
    medicare_number:  document.getElementById("np-medicare").value.trim() || null,
    medicare_irn:     document.getElementById("np-medicare-irn").value.trim() || null,
    ihi_number:       document.getElementById("np-ihi").value.trim() || null,
    phone_mobile:     document.getElementById("np-phone").value.trim() || null,
    address_line1:    document.getElementById("np-address").value.trim() || null,
    address_suburb:   document.getElementById("np-suburb").value.trim() || null,
    address_state:    document.getElementById("np-state").value.trim() || null,
    address_postcode: document.getElementById("np-postcode").value.trim() || null,
  };
}

async function findNewPatientDuplicateCandidates(body) {
  const params = new URLSearchParams();
  [
    "first_name", "last_name", "date_of_birth", "medicare_number",
    "medicare_irn", "ihi_number", "phone_mobile",
  ].forEach(key => {
    if (body[key]) params.set(key, body[key]);
  });
  params.set("limit", "5");

  const res = await apiFetch(`/patients/duplicate-candidates?${params.toString()}`);
  if (!res) return [];
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    if (res.status === 422) return [];
    throw new Error(detail.detail || `Duplicate check failed (${res.status})`);
  }
  return await res.json();
}

function hasHardDuplicateMatch(candidates) {
  return candidates.some(candidate =>
    (candidate.match_reasons || []).some(reason => HARD_DUPLICATE_REASONS.has(reason))
  );
}

function describeApiError(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (detail.message) return detail.message;
  if (detail.detail) return describeApiError(detail.detail, fallback);
  try {
    return JSON.stringify(detail);
  } catch (_) {
    return fallback;
  }
}

function renderDuplicateCandidate(candidate) {
  const p = candidate.patient || {};
  const name = `${p.last_name || ""}, ${p.first_name || ""}`.replace(/^,\s*/, "").trim() || "Unnamed patient";
  const meta = [
    p.date_of_birth ? `DOB: ${formatDate(p.date_of_birth)}` : "",
    p.medicare_number ? `Medicare: ${p.medicare_number}` : "",
    p.phone_mobile ? `Mobile: ${p.phone_mobile}` : "",
  ].filter(Boolean).join(" · ");
  const reasons = (candidate.match_reasons || []).join(", ");

  return `
    <div class="new-patient-duplicate-item">
      <div class="new-patient-duplicate-name">${escHtml(name)}</div>
      ${meta ? `<div class="new-patient-duplicate-meta">${escHtml(meta)}</div>` : ""}
      ${reasons ? `<div class="new-patient-duplicate-reasons">Matched on: ${escHtml(reasons)}</div>` : ""}
    </div>`;
}

function showDuplicateWarning(candidates, body) {
  const createBtn = document.getElementById("btn-np-create");
  const hardBlocked = hasHardDuplicateMatch(candidates);
  pendingNewPatientPayload = hardBlocked ? null : body;
  setNewPatientFieldsDisabled(!hardBlocked);
  setNewPatientResult(`
    <div class="alert ${hardBlocked ? "alert-error" : "alert-warning"}">
      <strong>${hardBlocked ? "Duplicate patient blocked" : "Possible duplicate patient"}</strong><br>
      ${hardBlocked
        ? "A strong identifier matches an existing patient record. Change the details and check again before creating a file."
        : "Review the existing record before creating a new file."}
      <div class="new-patient-duplicate-list">
        ${candidates.map(renderDuplicateCandidate).join("")}
      </div>
      <div class="new-patient-inline-actions">
        <button type="button" class="btn btn-ghost btn-sm" onclick="reviewNewPatientDetails()">${hardBlocked ? "Change Details" : "Review Details"}</button>
      </div>
    </div>`);
  if (createBtn) {
    createBtn.disabled = false;
    createBtn.textContent = hardBlocked ? "Check Again" : "Create Anyway";
    createBtn.onclick = hardBlocked ? createNewPatient : confirmCreateNewPatient;
  }
}

window.reviewNewPatientDetails = function reviewNewPatientDetails() {
  resetNewPatientActions();
  setNewPatientResult(`
    <div class="alert alert-warning">
      Duplicate warning cleared. Edit the details and create again to re-check for matches.
    </div>`);
  const firstName = document.getElementById("np-first-name");
  if (firstName) firstName.focus();
};

window.showNewPatientForm = function showNewPatientForm() {
  resetNewPatientActions();
  setNewPatientResult("");
  document.getElementById("new-patient-panel").classList.remove("hidden");
  document.getElementById("np-first-name").focus();
}

window.closeNewPatientForm = function closeNewPatientForm() {
  document.getElementById("new-patient-panel").classList.add("hidden");
  resetNewPatientActions();
  clearNewPatientFields();
  setNewPatientResult("");
}

window.resetNewPatientFormForAnother = function resetNewPatientFormForAnother() {
  closeNewPatientForm();
  showNewPatientForm();
}

// ═══════════════════════════════════════════════════════════
// CREATE PATIENT
// ═══════════════════════════════════════════════════════════

window.createNewPatient = async function createNewPatientWithDuplicateCheck() {
  let body;
  try {
    body = collectNewPatientPayload();
  } catch (e) {
    setNewPatientResult(`<div class="alert alert-error">${escHtml(String(e.message || e))}</div>`);
    return;
  }

  const btn = document.getElementById("btn-np-create");
  btn.disabled = true;
  btn.textContent = "Checking...";
  try {
    const candidates = await findNewPatientDuplicateCandidates(body);
    if (candidates.length) {
      showDuplicateWarning(candidates, body);
      return;
    }
    await submitNewPatient(body);
  } catch (e) {
    setNewPatientResult(`<div class="alert alert-error">${escHtml(String(e.message || e))}</div>`);
    btn.disabled = false;
    btn.textContent = "Create Patient File";
    btn.onclick = createNewPatient;
  }
};

window.confirmCreateNewPatient = async function confirmCreateNewPatient() {
  if (!pendingNewPatientPayload) {
    setNewPatientResult(`<div class="alert alert-error">Review the patient details and try again.</div>`);
    resetNewPatientActions();
    return;
  }
  await submitNewPatient(pendingNewPatientPayload);
};

async function submitNewPatient(body) {
  const btn = document.getElementById("btn-np-create");
  const cancelBtn = document.getElementById("btn-np-cancel");
  let created = false;
  btn.disabled = true;
  btn.textContent = "Creating...";
  try {
    const res = await apiFetch("/patients/with-file", {
      method: "POST",
      body: JSON.stringify(body),
    });
    if (!res || !res.ok) {
      const d = await res.json().catch(() => ({}));
      throw new Error(describeApiError(d.detail || d, `Server error ${res.status}`));
    }
    const data = await res.json();
    created = true;
    pendingNewPatientPayload = null;
    setNewPatientFieldsDisabled(true);
    setNewPatientResult(`
      <div class="alert alert-success">
        <strong>&#x2713; Patient created!</strong><br>
        File: <code>${escHtml(data.generated_filename)}</code><br>
        Open it from your OneDrive folder. The taskpane will auto-load the record when the file opens.
      </div>`);
    btn.textContent = "Close";
    btn.onclick = closeNewPatientForm;
    if (cancelBtn) {
      cancelBtn.textContent = "Create Another";
      cancelBtn.onclick = resetNewPatientFormForAnother;
    }
  } catch (e) {
    pendingNewPatientPayload = null;
    setNewPatientFieldsDisabled(false);
    setNewPatientResult(`<div class="alert alert-error">${escHtml(String(e.message || e))}</div>`);
  } finally {
    btn.disabled = false;
    if (!created) {
      btn.textContent = pendingNewPatientPayload ? "Create Anyway" : "Create Patient File";
      btn.onclick = pendingNewPatientPayload ? confirmCreateNewPatient : createNewPatient;
    }
  }
}

// DIARY MODE
// -----------------------------------------------------------

function _enterDiaryMode() {
  // Swap tab nav: hide patient tabs, show diary tabs.
  document.querySelectorAll('[data-mode="patient"]').forEach(b => b.classList.add("hidden"));
  document.querySelectorAll('[data-mode="diary"]').forEach(b => b.classList.remove("hidden"));

  // Update banner to show diary context.
  const today = new Date();
  document.getElementById("patient-name").textContent = "Diary Mode";
  document.getElementById("patient-meta").textContent =
    today.toLocaleDateString("en-AU", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

  // Hide patient-only elements.
  const ccBar = document.getElementById("command-center-bar");
  if (ccBar) ccBar.classList.add("hidden");
  const sidebar = document.getElementById("patient-sidebar");
  if (sidebar) sidebar.classList.add("hidden");

  showTab("diary-schedule");
  setStatus("Diary Mode — loading schedule…");
}

window.loadTodaysSchedule = async function () {
  const list = document.getElementById("diary-schedule-list");
  if (!list) return;
  list.innerHTML = '<div class="placeholder">Loading…</div>';

  const dayStart = new Date(); dayStart.setHours(0, 0, 0, 0);
  const dayEnd   = new Date(); dayEnd.setHours(23, 59, 59, 999);
  const params = `date_from=${dayStart.toISOString()}&date_to=${dayEnd.toISOString()}`;

  try {
    const res = await apiFetch(`/appointments?${params}`);
    if (!res || !res.ok) {
      list.innerHTML = '<div class="placeholder">Could not load schedule.</div>';
      setStatus("Schedule load failed — check the API server.");
      return;
    }
    const appts = await res.json();
    if (!appts.length) {
      list.innerHTML = '<div class="placeholder">No appointments today.</div>';
      setStatus("Diary — no appointments today.");
      return;
    }
    list.innerHTML = "";
    appts.forEach(a => {
      const start = new Date(a.start_time);
      const end   = new Date(start.getTime() + (a.duration_minutes || 15) * 60000);
      const fmt   = t => t.toLocaleTimeString("en-AU", { hour: "2-digit", minute: "2-digit", hour12: true });
      const name  = a.patient
        ? `${escHtml(a.patient.last_name)}, ${escHtml(a.patient.first_name)}`
        : "Unknown";
      const sc = _apptStatusClass(a.status);
      const card = document.createElement("div");
      card.className = "card schedule-card";
      card.innerHTML = `
        <div class="card-header">
          <div>
            <div class="card-title">${name}</div>
            <div class="card-meta">${fmt(start)}&ndash;${fmt(end)}${a.reason ? " &middot; " + escHtml(a.reason) : ""}</div>
          </div>
          <span class="card-badge ${sc}">${escHtml(a.status || "")}</span>
        </div>`;
      list.appendChild(card);
    });
    setStatus(`Schedule: ${appts.length} appointment${appts.length !== 1 ? "s" : ""} today.`);
  } catch (e) {
    list.innerHTML = `<div class="placeholder">Error: ${escHtml(String(e.message || e))}</div>`;
    setStatus("Schedule load error.");
  }
};

function _apptStatusClass(status) {
  const s = (status || "").toLowerCase();
  if (s === "arrived" || s === "inconsult") return "arrived";
  if (s === "completed")                    return "completed";
  if (s === "cancelled" || s === "noshow" || s === "dna") return "cancelled";
  return "";
}

// ═══════════════════════════════════════════════════════════
// INIT APP (called after successful login or token resume)
// ═══════════════════════════════════════════════════════════

function initApp() {
  setBanner(null);
  setStatus("Detecting document…");

  // Detect patient vs diary, then branch into the appropriate mode.
  detectDocumentType().then(type => {
    docMode = type;
    if (type === "diary") {
      _enterDiaryMode();
      loadTodaysSchedule();
    } else {
      _initPatientMode();
    }
  }).catch(e => {
    console.warn("[EMR4] detectDocumentType error, defaulting to patient mode:", e);
    docMode = "patient";
    _initPatientMode();
  });
}

function _initPatientMode() {
  showTab("consult");
  setStatus("Ready.");
  updateSyncDebug({ fetch: "ready", textLen: 0, http: "-", result: "-", extract: "-" });
  updateFormFields({});
  repairDocumentStructure();
  runBackgroundSync();
  autoDetectPatient();
  if (!backgroundSyncTimer) {
    backgroundSyncTimer = setInterval(runBackgroundSync, 5000);
  }
  Office.context.document.addHandlerAsync(
    Office.EventType.DocumentSelectionChanged,
    () => { clearTimeout(debounceTimer); debounceTimer = setTimeout(runBackgroundSync, 2000); }
  );
}

// ─── AUTO-DETECT PATIENT FROM OPEN DOCUMENT ─────────────────
// Reads the document title (= filename without .docx), parses
// "FIRSTNAME LASTNAME DD-MM-YYYY", looks up the patient, loads
// them, and stores the Word Online URL back to their record.
async function autoDetectPatient() {
  try {
    await Word.run(async context => {
      const props = context.document.properties;
      props.load("title");
      await context.sync();

      let title = (props.title || "").trim();
      const docUrl = Office.context.document.url || "";

      // Word Online doesn't expose props.title — fall back to filename in the URL
      if (!title && docUrl) {
        const urlPath = docUrl.split("?")[0];
        const rawName = urlPath.split("/").pop();
        if (rawName && /\.docx$/i.test(rawName)) {
          title = decodeURIComponent(rawName).replace(/\.docx$/i, "").trim();
        }
      }

      if (!title) {
        setStatus(docUrl ? `URL: ${docUrl.substring(0, 50)}` : "No title or URL — open a patient file.");
        return;
      }

      const m = title.match(/^([A-Z]+)\s+([A-Z]+)\s+(\d{2}-\d{2}-\d{4})$/);
      if (!m) { setStatus(`"${title.substring(0, 35)}" — not a patient file.`); return; }

      const [, firstName, lastName] = m;
      // Search by last name only (backend matches on first OR last, not combined)
      const res = await apiFetch(`/patients/search?q=${encodeURIComponent(lastName)}&limit=20`);
      if (!res) return;                          // 401 — apiFetch already called logout()
      if (!res.ok) {                             // 502/500/etc — backend or tunnel problem
        setStatus(`⚠ Backend unreachable (${res.status}) — start the API server, then reopen the file.`);
        return;
      }
      const data = await res.json();
      const allMatches = Array.isArray(data) ? data : [];
      const patient = allMatches.find(p =>
        p.first_name.toUpperCase() === firstName && p.last_name.toUpperCase() === lastName
      );
      if (!patient) { setStatus(`Patient "${firstName} ${lastName}" not found.`); return; }

      if (docUrl && docUrl !== patient.document_url) {
        await apiFetch(`/patients/${patient.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ document_url: docUrl }),
        });
      }
      await loadPatient(patient.id);
      setStatus(`Auto-loaded: ${patient.first_name} ${patient.last_name}${docUrl ? " + URL saved" : " (no URL)"}`);
    });
  } catch (e) {
    setStatus(`Auto-detect: ${String(e.message || e).substring(0, 60)}`);
  }
}

function updateOpenFileButton() {
  const btn = document.getElementById("btn-open-file");
  if (!btn) return;
  if (currentPatient && currentPatient.document_url) {
    btn.classList.remove("hidden");
    btn.onclick = () => window.open(currentPatient.document_url, "_blank");
  } else {
    btn.classList.add("hidden");
  }
}

// ═══════════════════════════════════════════════════════════
// OFFICE ON READY
// ═══════════════════════════════════════════════════════════

Office.onReady(info => {
  if (info.host !== Office.HostType.Word) return;

  // ── Global keyboard shortcut (Ctrl+Alt+N) ─────────────
  // Registered on the shared runtime so it fires while the cursor is in the
  // document body, reusing the taskpane's currentPatient state.
  // NB: NOT Ctrl+Shift+N — Chrome reserves that for Incognito and the browser
  // swallows it before Word/the add-in can see it.
  if (Office.actions && Office.actions.associate) {
    Office.actions.associate("StartConsultation", function (event) {
      Promise.resolve(startConsultation()).finally(() => event.completed());
    });
  }

  // ── Tab navigation ──────────────────────────────────────
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.onclick = () => {
      showTab(btn.dataset.tab);
      if (btn.dataset.tab === "history")        loadHistory();
      if (btn.dataset.tab === "meds")           loadMeds();
      if (btn.dataset.tab === "allergies")      loadAllergies();
      if (btn.dataset.tab === "diary-schedule") loadTodaysSchedule();
    };
  });

  // ── Auth ────────────────────────────────────────────────
  document.getElementById("btn-login").onclick = login;
  document.getElementById("login-password").addEventListener("keydown", e => {
    if (e.key === "Enter") login();
  });
  document.getElementById("btn-logout").onclick = logout;

  // ── Patient search ──────────────────────────────────────
  const searchPanel = document.getElementById("search-panel");
  const searchInput = document.getElementById("patient-search-input");

  function closeSearch() {
    searchPanel.classList.add("hidden");
    searchInput.value = "";
    document.getElementById("patient-search-results").innerHTML = "";
  }

  document.getElementById("btn-new-patient").onclick = showNewPatientForm;
  document.getElementById("btn-diary").onclick = openDiary;

  document.getElementById("btn-search-patient").onclick = () => {
    searchPanel.classList.toggle("hidden");
    if (!searchPanel.classList.contains("hidden")) searchInput.focus();
    else closeSearch();
  };

  // Escape closes the search panel
  document.addEventListener("keydown", e => {
    const newPatientPanel = document.getElementById("new-patient-panel");
    if (e.key === "Escape" && newPatientPanel && !newPatientPanel.classList.contains("hidden")) {
      closeNewPatientForm();
      return;
    }
    if (e.key === "Escape" && !searchPanel.classList.contains("hidden")) closeSearch();
  });

  // Click outside the search panel or button closes it
  document.addEventListener("click", e => {
    if (!e.target.closest("#search-panel") && !e.target.closest("#btn-search-patient")) {
      if (!searchPanel.classList.contains("hidden")) closeSearch();
    }
  });

  let searchDebounce;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => searchPatients(searchInput.value.trim()), 350);
  });

  // ── Command Centre ──────────────────────────────────────
  document.getElementById("btn-command-center").onclick = openCommandCentre;

  // ── Start Consultation (button + Ctrl+Alt+N while sidebar focused) ──
  const startBtn = document.getElementById("btn-start-consult");
  if (startBtn) startBtn.onclick = startConsultation;
  document.addEventListener("keydown", e => {
    if (e.ctrlKey && e.altKey && (e.key === "N" || e.key === "n")) {
      e.preventDefault();
      startConsultation();
    }
  });

  // ── Consult buttons ─────────────────────────────────────
  document.getElementById("btn-finalize").onclick = approveAndFinalize;

  // Auto-lock when the GP types in the consult panel
  document.addEventListener("input", e => {
    if (e.target.tagName === "INPUT" && e.target.closest("#panel-consult")) autoLock();
  });

  // ── Resume session or show login ─────────────────────────
  if (token) {
    showView("view-app");
    initApp();
  } else {
    showView("view-login");
  }
});
