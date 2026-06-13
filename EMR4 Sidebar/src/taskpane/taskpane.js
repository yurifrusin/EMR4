// --- CONFIGURATION ---
const BACKEND_URL = "http://localhost:8001/";

// Unique ID for this taskpane session — stored with each encounter so records are traceable
const SESSION_ID = "word_" + crypto.randomUUID().substring(0, 8);

// --- STATE ---
let lastSyncedText = "";
let debounceTimer = null;
let isLocked = false;        // When true, AI updates are blocked
let lastAiResponse = null;   // Cache of the most recent AI response
let isSyncing = false;       // Mutex: prevents concurrent background sync calls
let mbsRowCount = 0;         // Tracks how many MBS rows exist
let snomedRowCount = 0;      // Tracks how many SNOMED rows exist
let rxRowCount = 0;          // Tracks how many Rx rows exist

// ============================================================
// LOCK / UNLOCK
// ============================================================

window.toggleLock = function () {
  isLocked = !isLocked;
  updateLockUI();
  if (!isLocked) {
    // Apply the cached AI response instead of making a new API call.
    // A new call will happen naturally the next time the document text changes.
    if (lastAiResponse) {
      updateFormFields(lastAiResponse);
      document.getElementById("status").innerText =
        "Last sync: " + new Date().toLocaleTimeString();
    }
    // Do NOT reset lastSyncedText — no unnecessary re-call to Gemini.
  }
};

function autoLock() {
  if (!isLocked) {
    isLocked = true;
    updateLockUI();
  }
}

function updateLockUI() {
  const btn = document.getElementById("btn-lock");
  if (!btn) return;
  if (isLocked) {
    btn.className = "btn-lock locked";
    btn.querySelector(".lock-icon").textContent = "🔒";
    btn.querySelector(".lock-label").textContent = "Locked";
    btn.title = "AI updates are paused. Click to allow AI to update fields again.";
  } else {
    btn.className = "btn-lock unlocked";
    btn.querySelector(".lock-icon").textContent = "🔓";
    btn.querySelector(".lock-label").textContent = "Unlocked";
    btn.title = "AI is live-updating fields. Click to lock and edit manually.";
  }
}

// Auto-lock when the GP types into any taskpane input field
// (Event delegation on the whole sidebar so dynamically added rows are covered)
document.addEventListener("input", function (e) {
  if (e.target && e.target.tagName === "INPUT") {
    autoLock();
  }
});

let currentAudioUrl = null;

window.toggleTranscript = function () {
  const ta = document.getElementById("raw-transcript");
  if (!ta) return;
  if (ta.style.display === "none") {
    ta.style.display = "block";
  } else {
    ta.style.display = "none";
  }
};

// ============================================================
// INITIALIZATION
// ============================================================

Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    document.getElementById("status").innerText = "Initializing workspace...";
    bindFinalizeButton();
    runBackgroundSync();

    Office.context.document.addHandlerAsync(
      Office.EventType.DocumentSelectionChanged,
      onDocumentChanged
    );
    document.getElementById('btn-record').onclick = toggleRecording;
  }
});

function onDocumentChanged() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    runBackgroundSync();
  }, 2000);
}

function bindFinalizeButton() {
  const btn = document.getElementById("btn-finalize");
  if (btn) btn.onclick = approveAndFinalize;
}

// ============================================================
// WORD DOCUMENT READING
// ============================================================

async function getDocumentText() {
  return Word.run(async (context) => {
    const body = context.document.body;
    body.load("text");
    await context.sync();
    return body.text;
  });
}

// ============================================================
// BACKGROUND SYNC
// ============================================================

async function runBackgroundSync() {
  // Suspend background polling while recording ambient audio
  if (isRecording) return;

  // Mutex: if a sync is already running, skip — the in-flight call will handle it
  if (isSyncing) return;
  isSyncing = true;
  try {
    const text = await getDocumentText();

    if (!text || text.trim() === "") {
      if (!isLocked) updateFormFields({});
      document.getElementById("status").innerText = "Ready for manual input.";
      lastSyncedText = "";
      return;
    }

    if (text === lastSyncedText) return;
    lastSyncedText = text;

    document.getElementById("status").innerText = isLocked
      ? "🔒 Locked — AI running in background..."
      : "Analyzing new text...";

    const response = await fetch(BACKEND_URL + "api/v1/analyze-consultation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_id: SESSION_ID,
        text_delta: text,
        is_finalized: false,
        clinician_overrides: null,
      }),
    });

    const data = await response.json();
    lastAiResponse = data; // Always cache, even when locked

    if (!isLocked) {
      updateFormFields(data);
      document.getElementById("status").innerText =
        "Last sync: " + new Date().toLocaleTimeString();
    } else {
      document.getElementById("status").innerText =
        "🔒 Locked — AI ready. Unlock to apply new results.";
    }
  } catch (error) {
    console.error("Sync error:", error);
    document.getElementById("status").innerText =
      "Waiting for backend connection...";
  } finally {
    isSyncing = false; // Always release the mutex
  }
}

// --- AUDIO SCRIBE ENGINE ---
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

async function toggleRecording() {
  const btnRecord = document.getElementById('btn-record');
  const audioStatus = document.getElementById('audio-status');

  if (!isRecording) {
    // START RECORDING
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = processAudio;

      mediaRecorder.start();
      isRecording = true;
      btnRecord.innerText = "⏹️ Stop Recording";
      btnRecord.classList.add("recording");
      audioStatus.style.display = "flex";
      document.getElementById('status').innerText = "Capturing consultation audio...";

    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Microphone access is required to use the AI Scribe.");
    }
  } else {
    // STOP RECORDING
    mediaRecorder.stop();
    // Stop all microphone tracks to release the hardware
    mediaRecorder.stream.getTracks().forEach(track => track.stop());

    isRecording = false;
    btnRecord.innerText = "🎤 Start Recording";
    btnRecord.classList.remove("recording");
    audioStatus.style.display = "none";
  }
}

async function processAudio() {
  document.getElementById('status').innerText = "⏳ Processing audio with Vertex AI...";

  // Create an audio blob from the recorded chunks
  const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

  // Build a multipart/form-data payload for robust binary upload
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'consultation.webm');

  try {
    const response = await fetch(BACKEND_URL + "api/v1/scribe-consultation", {
      method: "POST",
      // fetch will automatically set the Content-Type to multipart/form-data with the correct boundary
      body: formData
    });

    const data = await response.json();

      // Update our UI boxes with the AI's extraction
      updateFormFields(data);

      // Setup ephemeral audio playback & transcript
      if (data.audio_url) {
        currentAudioUrl = data.audio_url;
        const player = document.getElementById("audio-playback");
        player.src = BACKEND_URL.replace(/\/$/, "") + currentAudioUrl;
        player.style.display = "block";
      }

      if (data.raw_transcript) {
        document.getElementById("raw-transcript").value = data.raw_transcript;
        document.getElementById("btn-toggle-transcript").style.display = "block";
      }

      document.getElementById('status').innerText = "✅ Audio scribe complete!";

      // Auto-lock the panel so the background sync doesn't overwrite it immediately
      isLocked = true;
      updateLockUI();

      // BONUS: Insert the generated clinical summary directly into the Word document!
      if (data.generated_clinical_note) {
        Word.run(async (context) => {
          const body = context.document.body;
          body.insertParagraph(data.generated_clinical_note, Word.InsertLocation.end);
          await context.sync();
        });
      }

    } catch (error) {
      console.error("Scribe error:", error);
      document.getElementById('status').innerText = "❌ Scribe failed.";
    }
}

// ============================================================
// UI RENDERING — called only when UNLOCKED
// ============================================================

function updateFormFields(response) {
  const meta = response.encounter_metadata || {};

  // Only auto-fill Consultation Type if it is currently empty
  const consultField = document.getElementById("consult-type");
  if (consultField && !consultField.value) {
    consultField.value = meta.consultation_type || "";
  }

  const mbsItems =
    meta.mbs_item_candidates && meta.mbs_item_candidates.length > 0
      ? meta.mbs_item_candidates
      : [{}];
  const diagnoses =
    response.clinical_diagnoses && response.clinical_diagnoses.length > 0
      ? response.clinical_diagnoses
      : [{}];
  const rx =
    response.medications_and_prescriptions &&
    response.medications_and_prescriptions.length > 0
      ? response.medications_and_prescriptions
      : [{}];

  // Rebuild MBS rows
  document.getElementById("mbs-container").innerHTML = "";
  mbsRowCount = 0;
  mbsItems.forEach((mbs) => appendMbsRow(mbs.item_number || "", mbs.description || ""));

  // Rebuild SNOMED rows
  document.getElementById("snomed-container").innerHTML = "";
  snomedRowCount = 0;
  diagnoses.forEach((dx) =>
    appendSnomedRow(dx.term || "", dx.snomed_ct_au_code || "")
  );

  // Rebuild RX rows
  document.getElementById("rx-container").innerHTML = "";
  rxRowCount = 0;
  rx.forEach((med) =>
    appendRxRow(med.drug_name || "", med.dosage_text || "")
  );

  bindFinalizeButton();
}

// ============================================================
// ROW BUILDERS
// ============================================================

function appendMbsRow(itemNumber, description) {
  const i = mbsRowCount++;
  const container = document.getElementById("mbs-container");
  const div = document.createElement("div");
  div.className = "form-group";
  div.id = `mbs-group-${i}`;
  div.innerHTML = `
    <label>Item Code ${i + 1}</label>
    <div class="flex-row">
      <div class="input-wrapper" style="flex:0 0 28%">
        <input type="text" id="mbs-item-${i}" value="${escHtml(itemNumber)}" autocomplete="off" placeholder="Code...">
        <div id="mbs-suggestions-${i}" class="autocomplete-results"></div>
      </div>
      <input type="text" id="mbs-desc-${i}" value="${escHtml(description)}" placeholder="Description (auto-filled)" readonly style="flex:1">
      <button class="btn-remove" onclick="removeRow('mbs-group-${i}')" title="Remove this item">✕</button>
    </div>
  `;
  container.appendChild(div);

  // Wire autocomplete
  const el = document.getElementById(`mbs-item-${i}`);
  if (el) el.addEventListener("keyup", () => handleKeystroke("mbs", i));
}

function appendSnomedRow(term, code) {
  const i = snomedRowCount++;
  const container = document.getElementById("snomed-container");
  const div = document.createElement("div");
  div.className = "form-group";
  div.id = `snomed-group-${i}`;
  div.innerHTML = `
    <label>Diagnosis ${i + 1}</label>
    <div class="flex-row">
      <div class="input-wrapper" style="flex:1">
        <input type="text" id="snomed-term-${i}" value="${escHtml(term)}" autocomplete="off" placeholder="Diagnosis term...">
        <div id="snomed-suggestions-${i}" class="autocomplete-results"></div>
      </div>
      <input type="text" id="snomed-code-${i}" value="${escHtml(code)}" placeholder="SNOMED Code" readonly style="flex:0 0 28%">
      <button class="btn-remove" onclick="removeRow('snomed-group-${i}')" title="Remove this diagnosis">✕</button>
    </div>
  `;
  container.appendChild(div);

  const el = document.getElementById(`snomed-term-${i}`);
  if (el) el.addEventListener("keyup", () => handleKeystroke("snomed", i));
}

function appendRxRow(drugName, dosage) {
  const i = rxRowCount++;
  const container = document.getElementById("rx-container");
  const div = document.createElement("div");
  div.className = "form-group";
  div.id = `rx-group-${i}`;
  div.innerHTML = `
    <label>Medication ${i + 1}</label>
    <div class="flex-row">
      <input type="text" id="rx-name-${i}" value="${escHtml(drugName)}" placeholder="Drug name..." style="flex:2">
      <input type="text" id="rx-dose-${i}" value="${escHtml(dosage)}" placeholder="Dosage..." style="flex:1">
      <button class="btn-remove" onclick="removeRow('rx-group-${i}')" title="Remove this medication">✕</button>
    </div>
  `;
  container.appendChild(div);
}

// ============================================================
// ADD BUTTONS (wired to HTML onclick)
// ============================================================

window.addMbsRow = function () {
  autoLock();
  appendMbsRow("", "");
};

window.addSnomedRow = function () {
  autoLock();
  appendSnomedRow("", "");
};

window.addRxRow = function () {
  autoLock();
  appendRxRow("", "");
};

window.removeRow = function (groupId) {
  autoLock();
  const el = document.getElementById(groupId);
  if (el) el.remove();
};

// ============================================================
// AUTOCOMPLETE ENGINE
// ============================================================

let typeaheadTimer;

async function handleKeystroke(type, index) {
  clearTimeout(typeaheadTimer);

  const inputId = type === "mbs" ? `mbs-item-${index}` : `snomed-term-${index}`;
  const inputEl = document.getElementById(inputId);
  if (!inputEl) return;
  const query = inputEl.value.trim();
  const resultsBox = document.getElementById(`${type}-suggestions-${index}`);
  if (!resultsBox) return;

  if (query.length < 2) {
    resultsBox.style.display = "none";
    return;
  }

  typeaheadTimer = setTimeout(async () => {
    resultsBox.style.display = "block";
    resultsBox.innerHTML = '<div class="autocomplete-searching">Searching...</div>';

    try {
      const endpoint = type === "mbs" ? "search-mbs" : "search-snomed";
      const response = await fetch(
        `${BACKEND_URL}api/v1/${endpoint}?q=${encodeURIComponent(query)}`
      );
      const results = await response.json();
      renderSuggestions(results, type, index);
    } catch (err) {
      resultsBox.innerHTML = '<div class="autocomplete-searching">Search failed.</div>';
    }
  }, 400);
}

function renderSuggestions(results, type, index) {
  const resultsBox = document.getElementById(`${type}-suggestions-${index}`);
  if (!resultsBox) return;
  resultsBox.innerHTML = "";

  if (!results || results.length === 0) {
    resultsBox.innerHTML = '<div class="autocomplete-searching">No matches found.</div>';
    setTimeout(() => (resultsBox.style.display = "none"), 2000);
    return;
  }

  results.slice(0, 5).forEach((item) => {
    const div = document.createElement("div");
    div.className = "autocomplete-item";

    if (type === "mbs") {
      const preview =
        item.description.length > 50
          ? item.description.substring(0, 50) + "…"
          : item.description;
      div.innerText = `${item.item_number} — ${preview}`;
      div.onclick = () => {
        const codeEl = document.getElementById(`mbs-item-${index}`);
        const descEl = document.getElementById(`mbs-desc-${index}`);
        if (codeEl) codeEl.value = item.item_number;
        if (descEl) descEl.value = item.description;
        resultsBox.style.display = "none";
      };
    } else {
      div.innerText = item.term;
      div.onclick = () => {
        const termEl = document.getElementById(`snomed-term-${index}`);
        const codeEl = document.getElementById(`snomed-code-${index}`);
        if (termEl) termEl.value = item.term;
        if (codeEl) codeEl.value = item.concept_id;
        resultsBox.style.display = "none";
      };
    }

    resultsBox.appendChild(div);
  });
}

// Close autocomplete dropdowns on outside click
document.addEventListener("click", function (e) {
  if (!e.target.closest(".input-wrapper")) {
    document
      .querySelectorAll(".autocomplete-results")
      .forEach((el) => (el.style.display = "none"));
  }
});

// ============================================================
// FINALIZE RECORD
// ============================================================

async function approveAndFinalize() {
  console.log("Finalize button clicked.");
  document.getElementById("status").innerText = "⏳ Saving to Database...";
  document.getElementById("status").style.color = "#0076d6";

  const consultType =
    (document.getElementById("consult-type") || {}).value || "";
  const overrides = {
    consultation_type: consultType,
    mbs_items: [],
    diagnoses: [],
    medications: [],
  };

  // Collect all MBS rows
  for (let i = 0; i < mbsRowCount; i++) {
    const codeEl = document.getElementById(`mbs-item-${i}`);
    if (!codeEl) continue; // row may have been removed
    const code = codeEl.value.trim();
    const desc = (document.getElementById(`mbs-desc-${i}`) || {}).value || "";
    if (code) overrides.mbs_items.push({ item_number: code, description: desc });
  }

  // Collect all SNOMED rows
  for (let i = 0; i < snomedRowCount; i++) {
    const termEl = document.getElementById(`snomed-term-${i}`);
    if (!termEl) continue;
    const term = termEl.value.trim();
    const code = (document.getElementById(`snomed-code-${i}`) || {}).value || "";
    if (term) overrides.diagnoses.push({ term, snomed_ct_au_code: code });
  }

  // Collect all Rx rows
  for (let i = 0; i < rxRowCount; i++) {
    const nameEl = document.getElementById(`rx-name-${i}`);
    if (!nameEl) continue;
    const drug = nameEl.value.trim();
    const dose = (document.getElementById(`rx-dose-${i}`) || {}).value || "";
    if (drug) overrides.medications.push({ drug_name: drug, dosage_text: dose });
  }

  try {
    const text = await getDocumentText();
    // Call the dedicated finalize endpoint — no AI involved, just a DB save
    const response = await fetch(BACKEND_URL + "api/v1/finalize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_id: SESSION_ID,
        text_delta: text,
        clinician_overrides: overrides,
        audio_url: currentAudioUrl
      }),
    });

    if (response.ok) {
      const data = await response.json();

      if (data._saved === false) {
        // Backend returned 200 but the DB save failed — show the real error
        const errMsg = data._save_error || "Unknown database error";
        document.getElementById("status").innerText = "❌ Save failed: " + errMsg;
        document.getElementById("status").style.color = "red";
        console.error("DB save error:", errMsg);
      } else {
        document.getElementById("status").innerText = "✅ Record Finalised & Saved.";
        document.getElementById("status").style.color = "green";

        // Lock the panel so the AI can't overwrite the saved record
        isLocked = true;
        updateLockUI();

        // Disable the Finalize button to prevent double-saves
        const btn = document.getElementById("btn-finalize");
        if (btn) {
          btn.disabled = true;
          btn.textContent = "✅ Finalised";
          btn.style.backgroundColor = "#6c757d";
          btn.style.cursor = "default";
        }

        // Hide the ephemeral playback UI and clear the source to stop playback immediately
        const player = document.getElementById("audio-playback");
        if (player) {
          player.pause();
          player.src = "";
          player.style.display = "none";
        }
        document.getElementById("raw-transcript").style.display = "none";
        document.getElementById("btn-toggle-transcript").style.display = "none";
        currentAudioUrl = null;
      }
    } else {
      document.getElementById("status").innerText =
        "❌ Server error: " + response.status;
      document.getElementById("status").style.color = "red";
    }
  } catch (error) {
    document.getElementById("status").innerText =
      "❌ Network failure. Check your backend server.";
    document.getElementById("status").style.color = "red";
  }
}

// ============================================================
// UTILITIES
// ============================================================

function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}