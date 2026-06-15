# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Prefer architectural guidance via opusplan combined with Sonnet execution

## Project Overview

**EMR4 Centaur** is an AI-native General Practice management system for Australia. Microsoft Word (desktop or online) is the clinical frontend — the GP writes into a Word document and an Office.js add-in taskpane acts as the command interface. A FastAPI/PostgreSQL backend on GCP handles clinical logic; Google Gemini 2.5 Flash provides AI throughout. See [`agents.md`](agents.md) for the definitive handover state and [`implementation_plan.md`](implementation_plan.md) for the 12-phase blueprint.

---

## Commands

### Backend (FastAPI)
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
```powershell
cd "EMR4 Sidebar"
npm install
npm run build          # Production webpack build
npm run build:dev      # Dev webpack build
npm run dev-server     # Dev server on localhost:3000
npm run lint
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

- `Start Consultation` button / **Ctrl+Shift+N** plants the dated header and sets bookmark `EMR4_NOTE_POINT`
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

---

## Key Files to Know

| File | Purpose |
|---|---|
| [`agents.md`](agents.md) | **Read first.** Handover state, architectural decisions, per-phase completion status. Update every significant commit. |
| [`implementation_plan.md`](implementation_plan.md) | 12-phase master blueprint and vision |
| [`sync_taskpane.py`](sync_taskpane.py) | Copies taskpane src → docs/, patches URLs — run after every frontend edit |
| [`create_patient_file.py`](create_patient_file.py) | Generates a per-patient `.docx` (demographics + locked section headers + Custom XML Part). `create_patient_docx()` is importable by the future New Patient userform endpoint. |
| `EMR4 Sidebar/src/taskpane/taskpane.js` | Main taskpane SPA logic |
| `docs/command-centre/command-centre.html` | AI Scribe window (edit directly, no build step) |
| `app/routers/consultation.py` | Core AI analysis and scribe endpoints |
| `alembic/versions/` | Migration history — add a new migration for any schema change |
| `.env` | Local secrets (not committed — see `.env.example`) |
| `gcp-key.json` | GCP service account (not committed) |
