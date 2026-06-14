# EMR4 Centaur — Agent Handover Document

> **Protocol:** This file is the single source of truth for any agent (human or AI) picking up this project.
> Update it at the end of every session, every phase, and whenever a significant architectural decision is made.
> The user can trigger an update at any time by saying **"update the handover doc"**.

---

## 1. Project in One Paragraph

EMR4 Centaur is an AI-native, open-source, cloud-hosted General Practice management system for Australia. Microsoft Word (desktop or online) is the clinical frontend — the GP writes into a Word document and an Office.js add-in taskpane acts as a "Command Center" SPA alongside it. A FastAPI/PostgreSQL backend on GCP handles all clinical logic, and Google Gemini 2.5 Flash provides AI throughout. The full 12-phase implementation plan is in [`implementation_plan.md`](implementation_plan.md).

---

## 2. Repository & Git State

| Item | Value |
|---|---|
| **Remote** | https://github.com/yurifrusin/EMR4.git |
| **Branch** | `master` |
| **Last pushed commit** | `6bf89dc` — "Add responsive wide layout with patient summary sidebar" |

### Tag map (all tags pushed to remote)

| Tag | Commit | What it contains |
|---|---|---|
| `phase-1-raw` | `257e214` | Phase 0 + Phase 1 initial implementation — first working version |
| `phase-1-popout-experiment` | `d79cb1d` | All pop-out / displayDialogAsync experiments from session 2 |

### Notable un-tagged commits (in order)

| Commit | Description |
|---|---|
| `b0c16d0` | Fix bcrypt auth (passlib removed, direct bcrypt calls) — clean Phase 1 baseline |
| `6bf89dc` | Current HEAD — clean native taskpane + responsive wide layout |

---

## 3. Current State — What Is Built and Working

### Phase 0 ✅ Complete
- FastAPI project structure (`app/routers/`, `services/`, `models/`, `schemas/`, `middleware/`)
- JWT auth with bcrypt (passlib removed — incompatible with bcrypt 5.0.0; see §7)
- Pydantic v2 settings from `.env`
- Alembic migrations, multi-tenant schema
- All 30+ database tables per `implementation_plan.md §7`
- SMS infrastructure stub (ClickSend)

### Phase 1 ✅ Substantially Complete (minor items pending)
- Patient CRUD + search (name, DOB, Medicare, phone)
- `EMR4 Patient File.dotx` template with Custom XML Part (`<emr4:document-type>patient</emr4:document-type>`)
- Taskpane SPA — 8 tabs: Consult, History, Results (placeholder), Meds, Allergies, DDx (placeholder), Rx (placeholder), Letters
- Audio scribe — record, transcribe via Gemini, auto-fill MBS/SNOMED/Rx rows
- Background AI sync — debounced on document selection change
- Lock/unlock AI live editing
- Approve & Finalise — saves encounter to DB
- Encounter history tab
- Medications tab
- Allergies tab (full CRUD)
- Letter writing — AI-drafted via Gemini, insert into Word
- Responsive wide layout — auto-activates at ≥700px via CSS media query (no button)
  - Patient summary sidebar: allergies (from summary API), meds (background fetch), AI diagnoses (live from sync)
  - 2-column card grids for history/meds/allergies
  - Larger text areas
- Manifest updated: ProviderName=EMR4, DefaultLocale=en-AU, button label="EMR4 Copilot"
- `create_patient_template.py` — generates the `.dotx` with Custom XML Part

### Not yet started
- Phase 2 onwards (see `implementation_plan.md §12`)

---

## 4. Key Architectural Decision Pending

### Word Desktop vs Word Online

**Decision in progress** — not yet finalised.

**Context:** The implementation plan (§2.1) calls for the GP to undock the taskpane and maximise it on a second monitor. In Word **desktop**, the taskpane can be undocked by dragging its title bar away from the Word window edge — but only when Word itself is not maximised, and dragging from the side causes it to snap to the opposite dock rather than float. This is counterintuitive for end users.

**Word Online advantage:** `displayDialogAsync` in Word Online opens a true browser popup (not a WebView2 dialog), so `window.resizeTo()` and `window.moveTo()` work — allowing a proper programmatic maximise/restore button. In Word desktop, those APIs are silently blocked.

**Word Online implications to verify before committing:**

| Feature | Risk | Notes |
|---|---|---|
| Custom XML Parts | ⚠️ **Medium** | Used for document-type routing (patient vs diary). Read access works in Word Online but programmatic binding may differ. Need to test `Office.context.document.customXmlParts` in Online. |
| Content Controls (Parse & Lock) | ✅ Low | `cannotEdit` / `cannotDelete` supported in Word Online |
| Co-authoring (Living Diary) | ✅ Positive | Word Online + SharePoint is the native co-authoring environment — better than desktop |
| `Word.run()` / `body.insertParagraph()` | ✅ Low | Core Word.js APIs work in both |
| Keyboard shortcuts (`Ctrl+Shift+B`) | ✅ Low | Add-in keyboard shortcuts work in Word Online |
| `displayDialogAsync` popup resize | ✅ Positive in Online | `window.resizeTo()` works in browser popup; blocked in WebView2 |
| Offline | N/A | Cloud-based system requires internet anyway |

**Recommended next step:** Test the add-in in Word Online (office.com) and verify Custom XML Part read/write before committing to Online as the primary target.

---

## 5. Environment Setup

### Backend
```
cd c:\Users\YuriFrusin\Documents\EMR4
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

### Database
- PostgreSQL 16 local (or Cloud SQL in production)
- pgvector extension enabled
- Connection string in `.env` (not committed — see `.env.example`)
- Run migrations: `alembic upgrade head`
- Seed dev data: `python seed.py` — creates practice + `dr.shera@emr4dev.local / Password1!`

### Add-in (taskpane)
- Files: `EMR4 Sidebar/src/taskpane/` — `taskpane.html`, `taskpane.js`, `taskpane.css`
- Manifest: `EMR4 Sidebar/manifest.xml`
- No build step — plain HTML/JS/CSS loaded directly by Office
- Sideload via Word: Insert → Add-ins → My Add-ins → Upload My Add-in → select `manifest.xml`
- Backend URL hardcoded: `http://localhost:8001` (change for production)

### Patient template
```
python create_patient_template.py
```
Generates `EMR4 Patient File.dotx` in the project root.

---

## 6. Known Issues & Hard-Won Fixes

| Issue | Root Cause | Fix Applied |
|---|---|---|
| Login returns "invalid credentials" | passlib 1.7.4 + bcrypt 5.0.0: passlib sends >72-byte test password, bcrypt 5 rejects it | Removed passlib entirely; use `bcrypt.hashpw()` / `bcrypt.checkpw()` directly in `app/services/auth_service.py` |
| `.env.example` not tracked | `.gitignore` had `.env.*` pattern | Added `!.env.example` exception to `.gitignore` |
| `create_patient_template.py` duplicate zip entries | Used `zipfile` append mode then patched | Rewrote as single-pass: read all entries, write new zip with patched rels + new customXml |
| Emoji in print statements crash on Windows | Windows cp1252 console can't encode `✅` | Replaced all emoji in print statements with ASCII equivalents e.g. `[OK]` |
| `window.resizeTo()` / `requestFullscreen()` do nothing | Office WebView2 (desktop) blocks these APIs for `displayDialogAsync` dialogs | No fix possible in desktop Word; works in Word Online browser popup |
| Native taskpane snaps to dock instead of floating | Office behaviour: dragging taskpane to the side of the Word window re-docks it | User must drag from title bar when Word is NOT maximised; or use Word Online |

---

## 7. Files of Note

| File | Purpose |
|---|---|
| `implementation_plan.md` | Master 12-phase plan — the definitive blueprint. Read this first. |
| `agents.md` | **This file** — agent handover |
| `app/services/auth_service.py` | bcrypt auth (no passlib) |
| `app/config.py` | Pydantic settings |
| `app/models/` | All SQLAlchemy models |
| `alembic/versions/` | Migration history |
| `seed.py` | Dev data seeder |
| `create_patient_template.py` | Generates `.dotx` with Custom XML Part |
| `EMR4 Sidebar/src/taskpane/taskpane.js` | Full SPA logic — auth, tabs, audio scribe, AI sync, Word API calls |
| `EMR4 Sidebar/src/taskpane/taskpane.html` | SPA HTML — 8 tab panels + patient sidebar |
| `EMR4 Sidebar/src/taskpane/taskpane.css` | Styles + `@media (min-width:700px)` Command Center layout |
| `EMR4 Sidebar/manifest.xml` | Office add-in manifest |
| `.env.example` | Template for local config (actual `.env` not committed) |

---

## 8. What to Do Next

1. **Decide Word Desktop vs Word Online** — test Custom XML Part read in Word Online (see §4)
2. **If Word Online:** Restore `displayDialogAsync` pop-out from tag `phase-1-popout-experiment` and add working `window.resizeTo()` maximize button
3. **Tag `phase-1-stable`** — once the Command Center layout is confirmed working (wide layout on second monitor), tag and push
4. **Start Phase 2** — Living Diary: SharePoint-hosted `.docx`, Parse & Lock (`Ctrl+Shift+B`), appointment CRUD, internal messaging, SMS reminders

---

## 9. Handover Protocol

### For the incoming agent
1. Read this file (`agents.md`) in full
2. Read `implementation_plan.md` §2 (Architecture Pivots) and §12 (Phases)
3. Run `git log --oneline` and `git tag` to orient yourself
4. Check `git status` — should be clean
5. Ask the user what they want to work on; don't assume

### For the outgoing agent (before context runs out)
1. Run `git status` — commit anything uncommitted
2. Update this file: current HEAD commit, current state, any new decisions or gotchas
3. Push: `git push origin master`
4. Tell the user: *"agents.md is updated and pushed — safe to start a new session"*

### Triggering updates
The user can say **"update the handover doc"** at any time to trigger a refresh of this file.

> **Note on usage limits:** Claude cannot detect when the user's session limit is approaching. The user should update this file proactively at the end of each major task or when switching topics. Watch for signs of context compression (summaries appearing in the conversation) as a signal that a handover update is due.

---

*Last updated: 2026-06-14 — Session 2 complete. Phase 1 substantially done. Word Online decision pending.*
