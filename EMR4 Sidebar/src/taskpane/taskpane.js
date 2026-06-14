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

// Consult tab state
let isLocked       = false;
let lastAiResponse = null;
let isSyncing      = false;
let mbsRowCount    = 0;
let snomedRowCount = 0;
let rxRowCount     = 0;
let lastSyncedText = "";
let debounceTimer  = null;
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

// ═══════════════════════════════════════════════════════════
// API HELPER — attaches JWT, handles 401
// ═══════════════════════════════════════════════════════════

async function apiFetch(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (!(opts.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  if (token) headers["Authorization"] = "Bearer " + token;
  headers["ngrok-skip-browser-warning"] = "1";
  const res = await fetch(API_BASE + path, { ...opts, headers });
  if (res.status === 401) {
    logout();
    return null;
  }
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
  document.getElementById("btn-command-center").disabled = true;
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
  document.getElementById("btn-command-center").disabled = false;

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
  if (isRecording || isSyncing) return;
  isSyncing = true;
  try {
    const text = await getDocumentText();
    if (!text || !text.trim()) {
      if (!isLocked) updateFormFields({});
      setStatus("Ready.");
      lastSyncedText = "";
      return;
    }
    if (text === lastSyncedText) return;
    lastSyncedText = text;
    setStatus(isLocked ? "🔒 AI running in background…" : "Analysing…");

    const headers = {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "1",
    };
    if (token) headers["Authorization"] = "Bearer " + token;
    const abort = new AbortController();
    const timeoutId = setTimeout(() => abort.abort(), 15000);
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
    clearTimeout(timeoutId);
    const data = await res.json();
    lastAiResponse = data;
    if (!isLocked) {
      updateFormFields(data);
      setStatus("Synced " + new Date().toLocaleTimeString());
    } else {
      setStatus("🔒 Locked — unlock to apply.");
    }
  } catch (e) {
    setStatus(e?.name === "AbortError" ? "Backend timeout — retrying…" : "Waiting for backend…");
  } finally {
    isSyncing = false;
  }
}

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
    const text    = await getDocumentText();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;
    const res = await fetch(API_BASE + "/finalize", {
      method: "POST",
      headers,
      body: JSON.stringify({ document_id: SESSION_ID, text_delta: text, clinician_overrides: overrides, audio_url: currentAudioUrl }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data._saved === false) {
        setStatus("❌ " + (data._save_error || "Save failed"));
      } else {
        setStatus("✅ Record finalised & saved.");
        isLocked = true;
        updateLockUI();
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
// COMMAND CENTRE
// ═══════════════════════════════════════════════════════════

const CC_URL = "https://yurifrusin.github.io/EMR4/command-centre/command-centre.html";

async function openCommandCentre() {
  if (!currentPatient) {
    setStatus("Load a patient before opening Command Centre.");
    return;
  }

  // Insert the dated consultation header into the Word document
  await insertConsultHeader(currentPatient);

  // Pass patient ID via URL param — more reliable than localStorage cross-context
  const url = `${CC_URL}?pid=${currentPatient.id}`;

  Office.context.ui.displayDialogAsync(url, { height: 75, width: 55 }, result => {
    if (result.status === Office.AsyncResultStatus.Failed) {
      setStatus("Could not open Command Centre: " + result.error.message);
      return;
    }
    commandCentreDialog = result.value;

    commandCentreDialog.addEventHandler(Office.EventType.DialogMessageReceived, arg => {
      try {
        const msg = JSON.parse(arg.message);
        if (msg.type === "ready") {
          // Deliver token to the dialog so it can authenticate against the backend
          commandCentreDialog.messageChild(JSON.stringify({ type: "auth", token }));
        } else if (msg.type === "insert_note" && msg.text) {
          insertNoteIntoWord(msg.text);
        }
      } catch (_) {}
    });

    commandCentreDialog.addEventHandler(Office.EventType.DialogEventReceived, () => {
      commandCentreDialog = null;
    });
  });
}

async function insertConsultHeader(patient) {
  const now = new Date();
  const dd   = String(now.getDate()).padStart(2, "0");
  const mm   = String(now.getMonth() + 1).padStart(2, "0");
  const yyyy = now.getFullYear();
  const timeStr = now.toLocaleTimeString("en-AU", { hour: "numeric", minute: "2-digit", hour12: true })
                      .replace("am", "AM").replace("pm", "PM");
  const dob = new Date(patient.date_of_birth);
  let age = yyyy - dob.getFullYear();
  if (now.getMonth() - dob.getMonth() < 0 ||
      (now.getMonth() === dob.getMonth() && now.getDate() < dob.getDate())) age--;
  const header = `${dd}-${mm}-${yyyy}  ${patient.first_name} ${patient.last_name}  ${timeStr}  ${age} years old.`;
  try {
    await Word.run(async ctx => {
      const para = ctx.document.body.insertParagraph(header, Word.InsertLocation.end);
      para.font.bold = true;
      await ctx.sync();
    });
  } catch (e) {
    setStatus("Header insert failed: " + e.message);
  }
}

async function insertNoteIntoWord(text) {
  try {
    await Word.run(async ctx => {
      ctx.document.body.insertParagraph(text, Word.InsertLocation.end);
      await ctx.sync();
    });
    setStatus("Note inserted into document.");
  } catch (e) {
    setStatus("Insert failed: " + e.message);
  }
}

// ═══════════════════════════════════════════════════════════
// INIT APP (called after successful login or token resume)
// ═══════════════════════════════════════════════════════════

function initApp() {
  showTab("consult");
  setBanner(null);
  setStatus("Ready.");

  updateFormFields({});
  runBackgroundSync();
  autoDetectPatient();

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
      if (!res || !res.ok) return;
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

  // ── Tab navigation ──────────────────────────────────────
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.onclick = () => {
      showTab(btn.dataset.tab);
      if (btn.dataset.tab === "history")  loadHistory();
      if (btn.dataset.tab === "meds")     loadMeds();
      if (btn.dataset.tab === "allergies") loadAllergies();
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

  document.getElementById("btn-search-patient").onclick = () => {
    searchPanel.classList.toggle("hidden");
    if (!searchPanel.classList.contains("hidden")) searchInput.focus();
    else closeSearch();
  };

  // Escape closes the search panel
  document.addEventListener("keydown", e => {
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
