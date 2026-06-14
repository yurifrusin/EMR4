// ═══════════════════════════════════════════════════════════
//  EMR Centaur — Command Centre & Scribe
//  Launched as a displayDialogAsync popup from the taskpane.
//  Has full microphone access (top-level window, not iframe).
//  Shares localStorage with the taskpane (same origin).
//  Sends Word-insertion requests back via messageParent().
// ═══════════════════════════════════════════════════════════

// BACKEND_URL: same 3-way logic as taskpane.js
// sync_taskpane.py will patch https://property-cinch-backfield.ngrok-free.dev when syncing.
const NGROK_URL  = "https://property-cinch-backfield.ngrok-free.dev";
const BACKEND_URL = (window.location.port === "3000")
  ? "http://localhost:8001"
  : window.location.hostname.includes("ngrok")
    ? window.location.origin
    : NGROK_URL;
const API_BASE = BACKEND_URL + "/api/v1";

// ─── STATE ────────────────────────────────────────────────
let token          = localStorage.getItem("emr4_token");
let currentPatient = null;
let isLocked       = false;
let lastAiResponse = null;
let currentAudioUrl = null;
let mbsRowCount    = 0;
let snomedRowCount = 0;
let rxRowCount     = 0;
let isRecording    = false;
let mediaRecorder  = null;
let audioChunks    = [];
let recordSeconds  = 0;
let recordTimer    = null;
let typeaheadTimer = null;

// ─── UTILITIES ────────────────────────────────────────────
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
  const el = document.getElementById("cc-status");
  if (el) el.textContent = msg;
}

// ─── OFFICE MESSAGING ─────────────────────────────────────
function sendToTaskpane(msg) {
  try { Office.context.ui.messageParent(JSON.stringify(msg)); } catch (_) {}
}

// ─── API ──────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (!(opts.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  if (token) headers["Authorization"] = "Bearer " + token;
  headers["ngrok-skip-browser-warning"] = "1";
  return fetch(API_BASE + path, { ...opts, headers });
}

// ─── PATIENT ──────────────────────────────────────────────
async function loadPatient() {
  const patientId = localStorage.getItem("emr4_cc_patient_id");
  if (!patientId || !token) {
    setStatus("Open from the taskpane with a patient loaded.");
    document.getElementById("cc-patient").textContent = "No patient context";
    return;
  }
  try {
    const res = await apiFetch(`/patients/${patientId}/summary`);
    if (!res.ok) { setStatus("Failed to load patient."); return; }
    const data = await res.json();
    currentPatient = data.patient;
    document.getElementById("cc-patient").textContent =
      `${currentPatient.last_name}, ${currentPatient.first_name}  ·  DOB: ${formatDate(currentPatient.date_of_birth)}  ·  Medicare: ${currentPatient.medicare_number || "—"}`;
    setStatus("Ready.");
    document.getElementById("btn-cc-finalize").disabled = false;
  } catch (e) {
    setStatus("Error: " + e.message);
  }
}

// ─── RECORDING ────────────────────────────────────────────
async function toggleRecording() {
  const btn    = document.getElementById("btn-cc-record");
  const status = document.getElementById("cc-audio-status");

  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks   = [];
      recordSeconds = 0;
      mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
      mediaRecorder.onstop = processAudio;
      mediaRecorder.start();
      isRecording = true;
      btn.textContent = "⏹ Stop Recording";
      btn.classList.add("recording");
      status.classList.remove("hidden");

      recordTimer = setInterval(() => {
        recordSeconds++;
        const m = String(Math.floor(recordSeconds / 60)).padStart(2, "0");
        const s = String(recordSeconds % 60).padStart(2, "0");
        const timerEl = document.getElementById("cc-timer");
        if (timerEl) timerEl.textContent = `${m}:${s}`;
      }, 1000);

      setStatus("Recording…");
    } catch (e) {
      setStatus("Microphone denied: " + e.message);
    }
  } else {
    clearInterval(recordTimer);
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(t => t.stop());
    isRecording = false;
    btn.textContent = "🎤 Start Recording";
    btn.classList.remove("recording");
    status.classList.add("hidden");
    setStatus("Processing…");
  }
}

async function processAudio() {
  setStatus("⏳ Transcribing with Vertex AI…");
  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const form = new FormData();
  form.append("audio_file", blob, "consultation.webm");
  try {
    const headers = {};
    if (token) headers["Authorization"] = "Bearer " + token;
    headers["ngrok-skip-browser-warning"] = "1";
    const res  = await fetch(API_BASE + "/scribe-consultation", { method: "POST", headers, body: form });
    const data = await res.json();

    updateFormFields(data);

    if (data.audio_url) {
      currentAudioUrl = data.audio_url;
      const player = document.getElementById("cc-audio-playback");
      player.src = BACKEND_URL + data.audio_url;
      player.classList.remove("hidden");
    }
    if (data.raw_transcript) {
      document.getElementById("cc-transcript").value = data.raw_transcript;
      document.getElementById("cc-transcript-section").classList.remove("hidden");
    }

    setStatus("✅ Transcription complete.");
    isLocked = true;
    updateLockUI();
    document.getElementById("btn-cc-insert").disabled = false;
  } catch (e) {
    setStatus("❌ Transcription failed: " + e.message);
  }
}

// ─── LOCK / UNLOCK ────────────────────────────────────────
window.toggleLock = function () {
  isLocked = !isLocked;
  updateLockUI();
  if (!isLocked && lastAiResponse) updateFormFields(lastAiResponse);
};

function updateLockUI() {
  const btn = document.getElementById("btn-cc-lock");
  if (!btn) return;
  if (isLocked) {
    btn.className = "btn btn-lock locked";
    btn.querySelector(".lock-icon").textContent = "🔒";
    btn.querySelector(".lock-label").textContent = "Locked";
  } else {
    btn.className = "btn btn-lock unlocked";
    btn.querySelector(".lock-icon").textContent = "🔓";
    btn.querySelector(".lock-label").textContent = "AI live";
  }
}

// ─── FORM FIELDS ──────────────────────────────────────────
function updateFormFields(response) {
  if (!response) return;
  lastAiResponse = response;
  const meta = response.encounter_metadata || {};

  const consultField = document.getElementById("cc-consult-type");
  if (consultField && !consultField.value) consultField.value = meta.consultation_type || "";

  const mbsItems  = meta.mbs_item_candidates?.length  ? meta.mbs_item_candidates  : [{}];
  const diagnoses = response.clinical_diagnoses?.length ? response.clinical_diagnoses : [{}];
  const rx        = response.medications_and_prescriptions?.length ? response.medications_and_prescriptions : [{}];

  document.getElementById("cc-mbs-container").innerHTML    = ""; mbsRowCount    = 0;
  document.getElementById("cc-snomed-container").innerHTML = ""; snomedRowCount = 0;
  document.getElementById("cc-rx-container").innerHTML     = ""; rxRowCount     = 0;

  mbsItems.forEach(m  => appendMbsRow(m.item_number || "",   m.description || ""));
  diagnoses.forEach(d => appendSnomedRow(d.term || "",       d.snomed_ct_au_code || ""));
  rx.forEach(m        => appendRxRow(m.drug_name || "",      m.dosage_text || ""));
}

// ─── ROW BUILDERS ─────────────────────────────────────────
function appendMbsRow(itemNumber, description) {
  const i = mbsRowCount++;
  const div = document.createElement("div");
  div.className = "cc-coding-row";
  div.id = `cc-mbs-group-${i}`;
  div.innerHTML = `
    <div class="cc-input-wrap">
      <input type="text" id="cc-mbs-item-${i}" class="cc-input" value="${escHtml(itemNumber)}"
             autocomplete="off" placeholder="MBS code…">
      <div id="cc-mbs-sugg-${i}" class="cc-autocomplete"></div>
    </div>
    <input type="text" id="cc-mbs-desc-${i}" class="cc-input" value="${escHtml(description)}"
           placeholder="Description" readonly style="flex:2">
    <button class="btn-remove" onclick="removeRow('cc-mbs-group-${i}')">✕</button>
  `;
  document.getElementById("cc-mbs-container").appendChild(div);
  document.getElementById(`cc-mbs-item-${i}`).addEventListener("keyup", () => handleKeystroke("mbs", i));
}

function appendSnomedRow(term, code) {
  const i = snomedRowCount++;
  const div = document.createElement("div");
  div.className = "cc-coding-row";
  div.id = `cc-snomed-group-${i}`;
  div.innerHTML = `
    <div class="cc-input-wrap" style="flex:2">
      <input type="text" id="cc-snomed-term-${i}" class="cc-input" value="${escHtml(term)}"
             autocomplete="off" placeholder="Diagnosis…">
      <div id="cc-snomed-sugg-${i}" class="cc-autocomplete"></div>
    </div>
    <input type="text" id="cc-snomed-code-${i}" class="cc-input" value="${escHtml(code)}"
           placeholder="SNOMED" readonly style="flex:0 0 90px">
    <button class="btn-remove" onclick="removeRow('cc-snomed-group-${i}')">✕</button>
  `;
  document.getElementById("cc-snomed-container").appendChild(div);
  document.getElementById(`cc-snomed-term-${i}`).addEventListener("keyup", () => handleKeystroke("snomed", i));
}

function appendRxRow(drugName, dosage) {
  const i = rxRowCount++;
  const div = document.createElement("div");
  div.className = "cc-coding-row";
  div.id = `cc-rx-group-${i}`;
  div.innerHTML = `
    <input type="text" id="cc-rx-name-${i}" class="cc-input" value="${escHtml(drugName)}"
           placeholder="Drug name…" style="flex:2">
    <input type="text" id="cc-rx-dose-${i}" class="cc-input" value="${escHtml(dosage)}"
           placeholder="Dosage…">
    <button class="btn-remove" onclick="removeRow('cc-rx-group-${i}')">✕</button>
  `;
  document.getElementById("cc-rx-container").appendChild(div);
}

window.addMbsRow    = () => appendMbsRow("", "");
window.addSnomedRow = () => appendSnomedRow("", "");
window.addRxRow     = () => appendRxRow("", "");
window.removeRow    = id => document.getElementById(id)?.remove();

// ─── AUTOCOMPLETE ─────────────────────────────────────────
async function handleKeystroke(type, index) {
  clearTimeout(typeaheadTimer);
  const inputId = type === "mbs" ? `cc-mbs-item-${index}` : `cc-snomed-term-${index}`;
  const inputEl = document.getElementById(inputId);
  const boxId   = type === "mbs" ? `cc-mbs-sugg-${index}` : `cc-snomed-sugg-${index}`;
  const box     = document.getElementById(boxId);
  if (!inputEl || !box) return;
  const query = inputEl.value.trim();
  if (query.length < 2) { box.style.display = "none"; return; }

  typeaheadTimer = setTimeout(async () => {
    box.style.display = "block";
    box.innerHTML = '<div class="cc-ac-hint">Searching…</div>';
    try {
      const endpoint = type === "mbs" ? "search-mbs" : "search-snomed";
      const res = await apiFetch(`/${endpoint}?q=${encodeURIComponent(query)}`);
      renderSuggestions(await res.json(), type, index);
    } catch {
      box.innerHTML = '<div class="cc-ac-hint">Search failed.</div>';
    }
  }, 400);
}

function renderSuggestions(results, type, index) {
  const boxId = type === "mbs" ? `cc-mbs-sugg-${index}` : `cc-snomed-sugg-${index}`;
  const box   = document.getElementById(boxId);
  if (!box) return;
  box.innerHTML = "";
  if (!results?.length) {
    box.innerHTML = '<div class="cc-ac-hint">No matches.</div>';
    setTimeout(() => (box.style.display = "none"), 2000);
    return;
  }
  results.slice(0, 6).forEach(item => {
    const div = document.createElement("div");
    div.className = "cc-ac-item";
    if (type === "mbs") {
      div.textContent = `${item.item_number} — ${item.description.substring(0, 60)}`;
      div.onclick = () => {
        document.getElementById(`cc-mbs-item-${index}`).value = item.item_number;
        document.getElementById(`cc-mbs-desc-${index}`).value = item.description;
        box.style.display = "none";
      };
    } else {
      div.textContent = item.term;
      div.onclick = () => {
        document.getElementById(`cc-snomed-term-${index}`).value = item.term;
        document.getElementById(`cc-snomed-code-${index}`).value = item.concept_id;
        box.style.display = "none";
      };
    }
    box.appendChild(div);
  });
}

document.addEventListener("click", e => {
  if (!e.target.closest(".cc-input-wrap")) {
    document.querySelectorAll(".cc-autocomplete").forEach(el => (el.style.display = "none"));
  }
});

// ─── INSERT INTO WORD (via taskpane bridge) ───────────────
window.insertIntoWord = function () {
  const transcript = document.getElementById("cc-transcript")?.value || "";
  const note = transcript || `[Consultation — ${new Date().toLocaleDateString("en-AU")}]`;
  sendToTaskpane({ type: "insert_note", text: note });
  setStatus("Sent to Word.");
};

// ─── APPROVE & FINALISE ───────────────────────────────────
window.approveAndFinalize = async function () {
  if (!currentPatient) { setStatus("No patient loaded."); return; }
  const finalizeBtn = document.getElementById("btn-cc-finalize");
  finalizeBtn.disabled  = true;
  finalizeBtn.textContent = "Saving…";
  setStatus("⏳ Saving to database…");

  const consultType = document.getElementById("cc-consult-type")?.value || "";
  const overrides   = { consultation_type: consultType, mbs_items: [], diagnoses: [], medications: [] };

  for (let i = 0; i < mbsRowCount; i++) {
    const code = document.getElementById(`cc-mbs-item-${i}`)?.value.trim();
    if (code) overrides.mbs_items.push({
      item_number: code,
      description: document.getElementById(`cc-mbs-desc-${i}`)?.value || "",
    });
  }
  for (let i = 0; i < snomedRowCount; i++) {
    const term = document.getElementById(`cc-snomed-term-${i}`)?.value.trim();
    if (term) overrides.diagnoses.push({
      term,
      snomed_ct_au_code: document.getElementById(`cc-snomed-code-${i}`)?.value || "",
    });
  }
  for (let i = 0; i < rxRowCount; i++) {
    const drug = document.getElementById(`cc-rx-name-${i}`)?.value.trim();
    if (drug) overrides.medications.push({
      drug_name: drug,
      dosage_text: document.getElementById(`cc-rx-dose-${i}`)?.value || "",
    });
  }

  const sessionId   = "cc_" + Date.now();
  const transcript  = document.getElementById("cc-transcript")?.value || "";

  try {
    const headers = {};
    if (token) headers["Authorization"] = "Bearer " + token;
    headers["Content-Type"] = "application/json";
    headers["ngrok-skip-browser-warning"] = "1";
    const res = await fetch(API_BASE + "/finalize", {
      method: "POST",
      headers,
      body: JSON.stringify({
        document_id: sessionId,
        text_delta: transcript,
        clinician_overrides: overrides,
        audio_url: currentAudioUrl,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data._saved === false) {
        setStatus("❌ " + (data._save_error || "Save failed"));
        finalizeBtn.disabled  = false;
        finalizeBtn.textContent = "✅ Approve & Finalise Record";
      } else {
        setStatus("✅ Record finalised & saved.");
        finalizeBtn.textContent = "✅ Finalised";
        // Insert generated clinical note into Word via taskpane bridge
        if (data.generated_clinical_note) {
          sendToTaskpane({ type: "insert_note", text: data.generated_clinical_note });
        }
        isLocked = true;
        updateLockUI();
      }
    } else {
      setStatus("❌ Server error " + res.status);
      finalizeBtn.disabled  = false;
      finalizeBtn.textContent = "✅ Approve & Finalise Record";
    }
  } catch (e) {
    setStatus("❌ Network error: " + e.message);
    finalizeBtn.disabled  = false;
    finalizeBtn.textContent = "✅ Approve & Finalise Record";
  }
};

// ─── INIT ─────────────────────────────────────────────────
Office.onReady(() => {
  document.getElementById("btn-cc-record").onclick = toggleRecording;
  updateFormFields({});
  loadPatient();
});
