# CLAUDE.md

@AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Prefer architectural guidance via opusplan combined with Sonnet execution

## Project Overview

**EMR4 Centaur** is an AI-native General Practice management system for Australia. Microsoft Word (desktop or online) is the clinical frontend — the GP writes into a Word document and an Office.js add-in taskpane acts as the command interface. A FastAPI/PostgreSQL backend on GCP handles clinical logic; Google Gemini 2.5 Flash provides AI throughout. See [`AGENTS.md`](AGENTS.md) for the definitive handover state and [`implementation_plan.md`](implementation_plan.md) for the 12-phase blueprint.

---

## Commands

### Start the full local stack (one command)
```powershell
.\run_dev.ps1                         # Postgres + uvicorn + ngrok + npm dev-server
.\run_dev.ps1 -Down                   # Stop app processes (leaves Postgres running)
.\run_dev.ps1 -NoDevServer            # Skip webpack dev-server
.\run_dev.ps1 -NoNgrok                # Skip ngrok (e.g. it's already bound)
```
`run_dev.ps1` is idempotent — re-running skips already-running services.
`start_emr.bat` is a double-click shim that calls it.

> **ngrok domain is a cross-file invariant** — `$NgrokDomain` in `run_dev.ps1`
> must match `NGROK_URL` in `sync_taskpane.py`. Change one → change the other.

### Backend (FastAPI) — individual commands
```powershell
# Activate venv (always required first)
.venv\Scripts\activate

# Run dev server (port 8001)
uvicorn app.main:app --reload --port 8001

# Database migrations
alembic upgrade head

# Seed dev data (creates dr.shera@emr4dev.local / Password1!)
python seed.py
```

### Frontend (Office Add-in Taskpane)
**There is no build step in the deploy path.** The taskpane is plain HTML/JS/CSS;
`sync_taskpane.py` copies `EMR4 Sidebar/src/taskpane/*` straight to `docs/` (no bundler).
The webpack/npm setup below is **vestigial Office-generator scaffolding** — it is not
used to produce what ships. Only `npm run lint` / `dev-server` are occasionally useful.
```powershell
cd "EMR4 Sidebar"
npm install
npm run lint           # optional — lint the taskpane source
npm run dev-server     # optional — local dev server on localhost:3000
# npm run build is NOT part of deployment (raw src is copied by sync_taskpane.py)
```

### Deploying to GitHub Pages
```powershell
# After every taskpane edit — copies src → docs/ and patches BACKEND_URL/NGROK_URL
python sync_taskpane.py
# Then increment ?v=N cache-bust params in taskpane.html / command-centre.html, commit docs/, push
# Reload Word: close & reopen the document to clear shared-runtime cache
```

---

## Architecture

### Two-Surface Design

| Surface | Implementation | Purpose |
|---|---|---|
| **Taskpane SPA** | `EMR4 Sidebar/src/taskpane/` → deployed to `docs/taskpane/` | Quick view/jobs: auth, patient search, 8 tabs |
| **Command Centre** | `docs/command-centre/` | Separate `displayDialogAsync` window — real browser window (NOT iframe, which blocks microphone). Hosts AI Scribe. Future home for Billing, Results Review. |

Token + patient ID are passed to the Command Centre via `?pid=` URL param and `messageChild` handshake.

### Backend (`app/`)

```
app/
├── main.py              # FastAPI app, CORS, router mounts
├── config.py            # Pydantic Settings from .env
├── database.py          # SQLAlchemy async session
├── routers/             # auth, patients, consultation, clinical, letters, appointments, search
├── models/              # SQLAlchemy ORM: tenancy, patients, clinical, billing, results, messaging, rag
├── schemas/             # Pydantic request/response schemas
├── services/            # auth_service (bcrypt), sms_service (ClickSend)
└── middleware/error_handler.py
```

Key AI endpoints:
- `POST /api/v1/analyze-consultation` — Gemini analyses typed note, returns MBS/SNOMED/Rx JSON
- `POST /api/v1/scribe-consultation` — Gemini transcribes recorded audio → SOAP note + coding
- Both are wrapped in `asyncio.to_thread` (Vertex AI blocks the event loop)

### Word Document Structure (Document Anchoring)

Patient `.docx` files use **Heading 1** sections (`Contemporaneous Notes`, `Vaccinations`, …). Consult entries are Normal+bold datestamp lines under "Contemporaneous Notes" (newest on top). `getCurrentConsultText()` in the taskpane scopes AI to ONLY the current consult: from the planted header to the next consult header or the next Heading 1.

- `Start Consultation` button / **Ctrl+Alt+N** plants the dated header and sets bookmark `EMR4_NOTE_POINT` (NOT Ctrl+Shift+N — Chrome reserves that for Incognito)
- `consultStarted` flag gates all background AI sync — prevents re-analysing a finalised consult on document open
- Custom XML Part `<emr4:document-type>patient|diary</emr4:document-type>` routes taskpane UI mode

**Section header protection.** Each Heading 1 section is wrapped in a locked content control (`cannotDelete` + `cannotEdit`, tag `emr4-section-*`) so headers can't be accidentally deleted/reformatted. Two sources must stay in sync: `PROTECTED_SECTIONS` in `taskpane.js` and `SECTION_HEADINGS` in `create_patient_file.py`. New files get the controls baked in at creation; `repairDocumentStructure()` in `taskpane.js` retro-fits legacy files on patient load (no-op if already tagged).

**Patient file generation.** `create_patient_file.py` produces a per-patient `.docx` named `FIRSTNAME LASTNAME DD-MM-YYYY.docx` (so `autoDetectPatient()` can identify it) with demographics header, the Dr Shera section headings, locked content controls, and the `document-type=patient` Custom XML Part. The core `create_patient_docx(PatientData, output_dir)` function is the integration point for the future New Patient userform's FastAPI endpoint. Fonts match the Margaret Thompson template: **Century Schoolbook 11pt** body, **Garamond 12pt** headings — both ship with Microsoft Office, so no font install is needed on Word machines.

### Deployment

| Component | Where |
|---|---|
| Taskpane + Command Centre | GitHub Pages (`docs/`) |
| Backend API | GCP Cloud Run (prod) / `uvicorn --reload` (local) |
| API tunnel (dev) | ngrok (`property-cinch-backfield.ngrok-free.dev`) — patched in by `sync_taskpane.py` |
| Database | Cloud SQL PostgreSQL 16 + pgvector (prod) / local Postgres (dev) |
| Active manifest | `manifest.online.xml` — re-sideload in Word after any manifest change |

---

## Known Hardened Fixes

| Problem | Fix |
|---|---|
| passlib + bcrypt 5.0.0 incompatible | Removed passlib; use `bcrypt` directly in `auth_service.py` |
| Vertex AI blocks event loop | Wrapped in `asyncio.to_thread` |
| MBS item 23 description too long | Truncated to 200 chars in prompt context |
| Command Centre iframe blocks microphone | Use `displayDialogAsync` real window, not iframe |
| Phantom analysis on file open | Gate `runBackgroundSync` on `consultStarted` flag |
| Injected OOXML invisible in Word Online (shading, etc.) | Word Online enforces CT_PPr/CT_RPr child order; Desktop doesn't. Insert with `insert_element_before()`, never `.append()` (see "Word Online is strict" below) |

---

## Word Online is strict (standing constraint)

**Word Online is the primary target and it is stricter than Word Desktop.** Desktop
silently tolerates malformed input; Online silently drops it (no error — the effect
just doesn't apply). This has bitten us repeatedly:
- **OOXML element order** — `<w:shd>` must precede `<w:spacing>`/`<w:jc>` in `<w:pPr>`. Use ordered insertion.
- **Content-control `appearance`** — use the `"Hidden"` string, not the `Word.ContentControlAppearance.hidden` enum (may be undefined at runtime).
- **Shared-runtime JS cache** — a sidebar refresh is NOT enough; close & reopen the document.
- **Keyboard shortcuts vs the browser** — Word Online runs in Chrome, which intercepts its own combos (Ctrl+Shift+N Incognito, Ctrl+Shift+T, Ctrl+Shift+B bookmarks bar, etc.) *before* Word/the add-in see them. Use `Ctrl+Alt+…` or `Alt+Shift+…` for add-in shortcuts (Start Consultation is **Ctrl+Alt+N**).

**Rule of thumb:** when something renders on Desktop but not Online, suspect a
schema-order / strictness issue before anything else. Test in Word Online, not Desktop.

## Cross-File Invariants (keep these in lockstep)

These pairs live in different files and MUST agree; a mismatch fails silently
(this caused a real "and" vs "," heading bug). Change one → change the other.

| Invariant | File A | File B |
|---|---|---|
| Section heading text **and** `emr4-section-*` tags | `PROTECTED_SECTIONS` (taskpane.js) | `SECTION_HEADINGS` (create_patient_file.py) |
| Contemporaneous-Notes anchor name + `emr4-section-cn` tag | `SECTION_HEADING` / `SECTION_TAG_CN` (taskpane.js) | the CN entry in `SECTION_HEADINGS` (create_patient_file.py) |
| Consult-header text format | `buildConsultHeader()` output | `CONSULT_HEADER_RE` (both taskpane.js) |
| Cache-bust `?v=N` | `taskpane.html` (src) | bump on every deploy, then `sync_taskpane.py` → `docs/` |
| ngrok URL patch target string | the `BACKEND_URL` block in `taskpane.js` source | the `.replace()` pattern in `sync_taskpane.py` (breaks silently if the source text drifts) |
| ngrok reserved domain value | `$NgrokDomain` in `run_dev.ps1` | `NGROK_URL` constant in `sync_taskpane.py` |

---

## Key Files to Know

| File | Purpose |
|---|---|
| [`AGENTS.md`](AGENTS.md) | **Read first.** Handover state, architectural decisions, per-phase completion status. Update every significant commit. |
| [`implementation_plan.md`](implementation_plan.md) | 12-phase master blueprint and vision |
| [`sync_taskpane.py`](sync_taskpane.py) | Copies taskpane src → docs/, patches URLs — run after every frontend edit |
| [`create_patient_file.py`](create_patient_file.py) | Generates a per-patient `.docx` (demographics + locked section headers + Custom XML Part). `create_patient_docx()` is importable by the future New Patient userform endpoint. |
| `EMR4 Sidebar/src/taskpane/taskpane.js` | Main taskpane SPA logic |
| `docs/command-centre/command-centre.html` | AI Scribe window (edit directly, no build step) |
| `app/routers/consultation.py` | Core AI analysis and scribe endpoints |
| `alembic/versions/` | Migration history — add a new migration for any schema change |
| `.env` | Local secrets (not committed — see `.env.example`) |
| `gcp-key.json` | GCP service account (not committed) |
