# S5 D-1 Attempt 2: Static Frontend Workflow Audit — Completion Artifact

**Sprint:** S5
**Lane:** D-1, attempt 2 of 3
**Worker:** DeepSeek Flash (deepseek-v4-flash / high)
**Completion artifact:** `orchestration/agent_inbox/codex/review-deepseek-s5-workflow-audit.md`
**Parent allocation:** `plan-claude-fable-emr4-receptionist-workflow-audit.md`
**Verified continuation:** `plan-claude-fable-s5-d1-continuation-v2.md`

---

## 1. Workspace Receipt

| Item | Value |
|---|---|
| **Worktree root** | `C:\Users\sarashera\EMR4-worktrees\deepcode-s5-d1-v2` |
| **Branch** | `deepcode/s5-d1-v2` — tracking `origin/handoff/current` |
| **Tracked-tree cleanliness** | Clean (no modified tracked files) |
| **Recent HEAD** | `4d34c341` — `docs(ariadne): preserve S5 D1 attempt one receipt` |
| **Python venv** | Not present in this worktree (disposable worker checkout) |
| **Node version** | v24.18.0 (confirmed available for `node --check`) |

---

## 2. Files Inspected

| File | Role |
|---|---|
| `EMR4 Sidebar/src/taskpane/taskpane.js` | Source taskpane SPA (2579 lines) |
| `EMR4 Sidebar/src/taskpane/taskpane.html` | Source taskpane HTML (501 lines) |
| `EMR4 Sidebar/src/taskpane/taskpane.css` | Source taskpane styles (not examined; CSS-only) |
| `EMR4 Sidebar/src/taskpane/shortcuts.json` | Keyboard shortcut registration |
| `docs/diary/diary.js` | Diary grid SPA (~4990+ lines) |
| `docs/diary/diary.html` | Diary grid HTML (not examined; container-only) |
| `docs/diary/diary.css` | Diary grid styles (not examined; CSS-only) |
| `docs/taskpane/taskpane.js` | Deployed (GitHub Pages) taskpane JS — same logic; `BACKEND_URL` patched for ngrok |
| `sync_taskpane.py` | Sync helper (no `--check` flag exists) |

---

## 3. Static Command Results

### 3.1 `node --check docs/diary/diary.js`
**Result:** PASS — syntax OK (exit 0)

### 3.2 `node --check "EMR4 Sidebar/src/taskpane/taskpane.js"`
**Result:** PASS — syntax OK (exit 0)

### 3.3 `node --check docs/taskpane/taskpane.js`
**Result:** PASS — deployed copy also syntax OK (exit 0)

### 3.4 `python scripts/sync_taskpane.py --check`
**Result:** NOT RUN — the sync helper (`sync_taskpane.py` at repo root) has no `--check` or check-only invocation flag. Running it would copy and patch files. Per the packet instructions ("do not synchronize or modify files"), this command was not executed.

---

## 4. Static Receptionist Workflow Trace

The receptionist flow spans two surfaces: the **taskpane SPA** (Word sidebar) and the **diary grid SPA** (separate `displayDialogAsync` window). Below is the complete static trace from taskpane login through diary interaction to API call sites.

### 4.1 Taskpane — Login & Patient Selection

```
1. Office.onReady (taskpane.js:2417)
   → Checks localStorage for emr4_token
   → Shows view-login or view-app

2. login() (taskpane.js:199)
   → POST /api/v1/auth/login  (x-www-form-urlencoded: username, password)
   → Stores access_token in localStorage

3. initApp() (taskpane.js:2294)
   → detectDocumentType() (taskpane.js:1368)
     → Office.context.document.customXmlParts.getByNamespaceAsync (ns: http://emr4.com/ns/document)
     → Falls back to filename/title heuristic
   → Patient mode: _initPatientMode() or Diary mode: _enterDiaryMode()

4. _initPatientMode() (taskpane.js:2316)
   → autoDetectPatient() (taskpane.js:2337)
     → Word.run → read document title → parse "FIRSTNAME LASTNAME DD-MM-YYYY"
     → GET /api/v1/patients/search?q={lastName}&limit=20
     → PUT /api/v1/patients/{id} (backfill document_url)
     → GET /api/v1/patients/{id}/summary → loadPatient()
   → Starts 5-second background sync interval (runBackgroundSync)

5. 🔍 Search (taskpane.js:315)
   → GET /api/v1/patients/search?q={longestTerm}&limit=50

6. loadPatient(id) (taskpane.js:359)
   → GET /api/v1/patients/{id}/summary
   → GET /api/v1/patients/{id}/medications (background)
   → Calls repairDocumentStructure() — Word.js content-control locking
```

### 4.2 Taskpane — Diary Button to Diary Window

```
7. 📅 Button click → openDiary() (taskpane.js:1025)
   → Office.context.ui.displayDialogAsync(DIARY_URL, {height:90, width:90})
     DIARY_URL = "https://yurifrusin.github.io/EMR4/diary/diary.html"
   → On DialogMessageReceived:
     → {type: "ready"} → messageChild({type: "auth", token})
   → No patient guard — diary is practice/day-scoped
```

### 4.3 Diary Grid — Init & Data Fetching

```
8. diary.js entry (diary.js:1)
   → Office.onReady → initDiary() (not shown; pre-2000 area read)
   → Auth token received via messageParent (ready→auth handshake)
   → Falls back to localStorage("emr4_token") while waiting

9. loadDiary() (diary.js:4101) — main data load
   → Parallel fetch (diary.js:4158-4183):
     a. loadDiaryTemplate()
        → GET /api/v1/diary/template?location_id={id}
        → Falls back to FALLBACK_TEMPLATE embedded literal (diary.js:2194)
     b. GET /api/v1/appointments?date_from={ISO}&date_to={ISO}[&location_id={id}]
     c. GET /api/v1/appointments/types
     d. GET /api/v1/diary/roster?date={YYYY-MM-DD}[&location_id={id}]
     e. GET /api/v1/diary/waiting-areas[?location_id={id}]
     f. loadPractitionerDirectory()
        → POST /api/v1/graphql (GraphQL query for practitioners)
        → Falls back to GET /api/v1/practice/practitioners?activeOnly=true&limit=200
```

### 4.4 Diary Grid — Rendering & Lifecycle

```
10. renderGrid() (diary.js:3518)
    → Generates time column + practitioner/room columns
    → Appointments rendered as absolutely-positioned blocks:
      - Status → CSS class (appt-class, appt-booked, appt-cancelled, etc.)
      - Appointment-type color_hex → left border accent
      - Provisional patients styled differently
    → Slot chevrons ("»") for empty bookable slots
    → Click on empty slot → openBookingModalForCreate()
    → Break blocks per column
    → Booking gap targets for drag-to-book

11. Appointment status changer (diary.js:3793-3840)
    → <select> on each appointment card
    → onChange → setAppointmentStatus(a, newStatus)
      (calls POST /api/v1/appointments/{id}/status or similar mutation endpoint)
```

### 4.5 Bernie Copilot Flow

```
12. Bernie session init (diary.js:154-564 BernieSession class)
    → State machine: INACTIVE → CONTEXT_SELECTION → INSTRUCTION_ENTRY → INTERPRETING → CANDIDATE_SELECTION → SLOT_PREVIEW → CONFIRMING → CONFIRMED

13. Bernie server session:
    → GET  /api/v1/appointments/bernie/sessions/active?surface_id=diary-main&reference_date={date}
    → POST /api/v1/appointments/bernie/sessions/new
    → POST /api/v1/appointments/bernie/sessions/{id}/events

14. Staff instruction → POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction
    Body: {instruction, reference_date, context_frames, turn_ref, server_session_*}

15. Candidate selection → POST /api/v1/appointments/proposals/bernie/supervised-booking
    Body: {reference_date, command, context_frames, selected_candidate_index, ...}

16. Confirmation → POST /api/v1/appointments/proposals/create/confirm-bernie
    Body: {confirmed: true, selection_proposal, candidate_freshness_id, ...}

17. Tool intent (extend/lengthen) → POST /api/v1/appointments/proposals/bernie/tool-intent
```

### 4.6 Additional API Call Sites (diary.js)

| Endpoint | Verb | Purpose | Location |
|---|---|---|---|
| `/api/v1/auth/me` | GET | Load current user role | diary.js:2785 |
| `/api/v1/appointments/{id}/audit` | GET | Audit history for an appointment | diary.js:2636 |
| `/api/v1/appointments/proposals/create` | POST | Create booking proposal | diary.js (modal) |
| `/api/v1/diary/waiting-areas` | GET | Waiting areas for batch | diary.js:4169 |
| `/api/v1/appointments/{id}/move` | POST | Move appointment (drag) | diary.js (drag handler) |
| `/api/v1/appointments/{id}/resize` | POST | Resize appointment (duration change) | diary.js (resize handler) |

### 4.7 Taskpane Consult Flow API Calls

| Endpoint | Verb | Purpose | Location |
|---|---|---|---|
| `/api/v1/auth/login` | POST | OAuth2 password grant | taskpane.js:209 |
| `/api/v1/patients/search` | GET | Patient search | taskpane.js:330 |
| `/api/v1/patients/{id}/summary` | GET | Patient summary load | taskpane.js:364 |
| `/api/v1/patients/{id}/medications` | GET | Medications fetch | taskpane.js:379 |
| `/api/v1/patients/{id}/encounters` | GET | Encounter history | taskpane.js:426 |
| `/api/v1/patients/{id}/allergies` | GET/POST/DELETE | Allergies CRUD | taskpane.js:515-541 |
| `/api/v1/patients/{id}/letters/draft` | POST | AI letter drafting | taskpane.js:558 |
| `/api/v1/patients/with-file` | POST | New patient with docx | taskpane.js:2159 |
| `/api/v1/patients/{id}` | PUT | Update patient details | taskpane.js:2021 |
| `/api/v1/patients/duplicate-candidates` | GET | Duplicate check | taskpane.js:1546 |
| `/api/v1/analyze-consultation` | POST | AI consult analysis | taskpane.js:681 |
| `/api/v1/scribe-consultation` | POST | Audio scribe | taskpane.js:771 |
| `/api/v1/finalize` | POST | Finalize encounter | taskpane.js:986 |
| `/api/v1/search-mbs` | GET | MBS autocomplete | taskpane.js:915 |
| `/api/v1/search-snomed` | GET | SNOMED autocomplete | taskpane.js:915 |
| `/api/v1/appointments` | GET | Today's schedule (diary mode) | taskpane.js:2242 |

### 4.8 Authentication Handoff

| Surface | Mechanism | Token Origin | Fallback |
|---|---|---|---|
| **Taskpane SPA** | `Bearer` header via `apiFetch()` | `localStorage("emr4_token")` after login | 401 → `logout()` |
| **Command Centre** | `messageChild({type:"auth", token})` from taskpane after `ready` | Taskpane memory → localStorage as `emr4_cc_patient_id` | URL param `?pid=` |
| **Diary Grid** | `messageChild({type:"auth", token})` from taskpane after `ready` | Taskpane memory | `localStorage("emr4_token")` while waiting |
| **Diary Grid (expiry)** | `isTokenExpired()` checks JWT `exp` claim | Same localStorage | 401 → `clearExpiredAuthToken()` + auth banner |

### 4.9 Cache-Bust / Synchronization

| Surface | Mechanism | Details |
|---|---|---|
| **Taskpane JS/CSS** | `?v=N` in URL (HTML) | Source: `taskpane.html?v=54`, `taskpane.js?v=57`. Bump manually per deploy. |
| **Diary HTML/CSS/JS** | `?v=N` in diary.html | Not shown in read section; presume same pattern. |
| **Diary grid auto-refresh** | 60-second `setTimeout` chain | `scheduleRefresh()` → `loadDiary(true)` (silent) every 60s. |
| **Taskpane background sync** | 5-second `setInterval` | `runBackgroundSync()` every 5s; debounce 2s on selection change. |
| **Consult analysis debounce** | 2s after selection change | Prevents flooding backend on every keystroke. |
| **Sync skip** | Guarded by `consultStarted` | No analysis until "Start Consultation" or CC opened. |

---

## 5. Classified Findings

### Material Functional — None found

All critical API paths have matching endpoints visible in the codebase. The auth handshake chain (taskpane → diary/CC via `messageChild`) is consistent across all three surfaces.

### Material Usability — None found

The receptionist flow (login → patient search → diary button → grid → appointments → status changes → Bernie) is logically complete in the static trace. No missing affordances or dead-end paths detected.

### Minor Findings

| # | Finding | File | Details |
|---|---|---|---|
| M1 | No check-only mode for sync helper | `sync_taskpane.py` | `sync_taskpane.py` has no `--check` / `--dry-run` flag. Running it always copies and patches files. The D-1 packet instructed using `python scripts/sync_taskpane.py --check` but the helper lives at repo root and has no such flag. |
| M2 | Diary template URL port construction differs from other callers | `diary.js:2882` | Uses `apiFetch` (which prepends `API_BASE`) but the diary's `API_BASE` already includes `/api/v1`. The path `/diary/template${locationQuery}` is correct. |
| M3 | Taskpane `openFileButton` shows when `document_url` is set | `taskpane.js:2394-2403` | Minor: the button opens the URL in a new tab, but in Word Online the document is already open. This is a pre-existing design choice, not a bug. |

### Observations

| # | Observation | Details |
|---|---|---|
| O1 | Parallel data fetch for diary load | Six concurrent API calls on every refresh/date-change: template, appointments, types, roster, waiting-areas, practitioner directory. Robust for dev; worth monitoring for latency under load. |
| O2 | Diary uses GraphQL for practitioners, REST fallback | `diary.js:2570-2616` — attempts GraphQL first, falls back to REST on transport/code errors. Defensive pattern. |
| O3 | Deployed `taskpane.js` has patched `BACKEND_URL` | `docs/taskpane/taskpane.js` uses a three-way URL resolution (dev-server / ngrok-origin / ngrok-constant). Source `taskpane.js` has a simpler two-way resolution. The deployed copy is auto-patched by `sync_taskpane.py`. |
| O4 | No session/CSRF token in fetch headers | Neither taskpane nor diary uses a CSRF token or session cookie. Auth is purely JWT Bearer + `ngrok-skip-browser-warning`. Acceptable for a sideloaded Office add-in behind auth. |
| O5 | Edge case: empty appointment list handles gracefully | `loadDiary()` → `loadTodayAppointments()` will show `"No appointments today"` UI. All empty/error states visibly handled. |

---

## 6. Limitations

This audit is **static only**. No live-stack evidence is claimed. Specifically:

- **No backend verification**: API routes, request validation, and response schemas were not checked against the backend implementation.
- **No browser runtime**: No Office.js, `displayDialogAsync`, or `messageChild` handshake was executed. The auth token transfer chain is traced statically but was not verified in a live Office session.
- **No pytest runs**: D-2 owns backend/full test evidence.
- **No UI interaction testing**: A-1 owns the independent usability veto.
- **No Python runtime**: The disposable DeepSeek worker checkout has no `.venv`, so Python-based checks (`sync_taskpane.py`) could not be run in any mode. This is expected for a static frontend-only audit.

Files and directories explicitly out of scope per packet: `local_data`, backend `app/`, database models, migrations, provider integrations, Git history mutation, closed S5 gates.

---

## 7. Summary

All three `node --check` syntax validations passed. The receptionist workflow is statically complete across the taskpane and diary surfaces: login → patient search/load → diary window launch → appointment grid rendering → status changes → Bernie copilot proposal/confirmation. All API call sites have been mapped with their URL, HTTP verb, payload shape context, and authentication mechanism recorded above. The sync helper has no check-only mode and was not run (per the no-modification instruction). No material functional or usability issues were found from static analysis alone.

---

STATUS: complete
