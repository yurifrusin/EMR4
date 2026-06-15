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
| **Last pushed commit** | `3364bba` — "Fix demographics grey shading not rendering in Word Online" (whitespace-normalisation commit follows) |

### Tag map (all tags pushed to remote)

| Tag | Commit | What it contains |
|---|---|---|
| `phase-1-raw` | `257e214` | Phase 0 + Phase 1 initial implementation — first working version |
| `phase-1-popout-experiment` | `d79cb1d` | All pop-out / displayDialogAsync experiments from session 2 |

### Notable un-tagged commits (in order)

| Commit | Description |
|---|---|
| `b0c16d0` | Fix bcrypt auth (passlib removed, direct bcrypt calls) — clean Phase 1 baseline |
| `7d5546e` | Disable Finalise button while CC open; restore on CC close |
| `87359cc` | `setTaskpaneLocked()` — disable ALL taskpane editing controls while CC open (v=22) |
| `03d5575` | `repairDocumentStructure()` — Heading 1 section headers wrapped in locked content controls (v=23) |
| `28483bb` | Run repair on initApp + fix ContentControlAppearance "Hidden" string (v=24) |
| `3578889` | Add `create_patient_file.py` per-patient generator; fix Care Plans heading text |
| `910c3bb` | Bake template fonts (Century Schoolbook / Garamond) + locked content controls into generator |
| `bbb6b12` | Always render address/phone/medicare demographic lines |
| `aa8bda2` | Demographics as shaded paragraphs (no table) + 1.15 line spacing |
| `3364bba` | Fix grey shading order so it renders in Word Online (CT_PPr schema) |

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

### Phase 1.5 ✅ Command Centre & Scribe + document anchoring (this work)
- **Hosting**: taskpane static files served from **GitHub Pages** (`docs/`), API calls go to **ngrok** (`property-cinch-backfield.ngrok-free.dev`). `sync_taskpane.py` copies `EMR4 Sidebar/src/taskpane/*` → `docs/taskpane/` and patches BACKEND_URL/NGROK_URL. Run it after every taskpane edit, then push. Cache-bust via `?v=N` on css/js in taskpane.html / command-centre.html — increment on every deploy.
- **Command Centre** (`docs/command-centre/`): separate **window** via `displayDialogAsync` (NOT iframe — iframe denies microphone). Hosts the AI Scribe (record → Gemini transcribe → SOAP note review → insert). Token + patient delivered via `?pid=` URL param and `messageChild` handshake. This is the screen-real-estate surface for future Billing/Results Review — see memory `project_two_surface_architecture`.
- **Document anchoring (Dr Shera method)** — patient `.docx` has Heading 1 section titles (Contemporaneous Notes, Vaccinations, …); consult entries are Normal+bold lines `DD-MM-YYYY  Name  H[:MM] AM/PM  N years old.` under Contemporaneous Notes (newest on top). `getCurrentConsultText()` scopes AI to ONLY the current consult (planted header → previous consult header / next Heading 1). See memory `project_document_anchoring`.
- **Start Consultation** button + **Ctrl+Shift+N** (shared runtime, ExtendedOverrides/shortcuts.json, manifest v1.1.0.0) plants the dated header under Contemporaneous Notes and bookmarks it (`EMR4_NOTE_POINT`); notes/SOAP insert right after it.
- **Gating**: `runBackgroundSync` does nothing until `consultStarted` (set by Start Consultation / opening Command Centre); prevents re-analysing a previously finalised consult on open. Reset on patient load / logout / finalise.
- **consult_finalized** message: Command Centre pushes its finalised coding back to the taskpane Consult tab (locked) + refreshes history/meds/sidebar.
- Backend `analyze-consultation`/`scribe-consultation` wrapped in `asyncio.to_thread` (Vertex AI was blocking the event loop); MBS descriptions truncated to 200 chars in prompt context (item 23's full text listed every excluded item → huge/slow prompt); encounters saved with `status=Finalized`; `finalize` takes `patient_id`.

### Phase 1.5 addendum (this session) ✅
- **`setTaskpaneLocked(locked)`** — disables/restores all taskpane editing controls while Command Centre is open: `btn-command-center`, `btn-start-consult`, `btn-lock`, `btn-search-patient`, `btn-open-file`, `btn-add-mbs/snomed/rx`, `btn-finalize`, `consult-type` input, and dynamic coding row containers (`.cc-locked` CSS). Called on CC open/close. Finalize stays disabled if consult was already finalised inside CC.
- **`repairDocumentStructure()`** — wraps each known Heading 1 section header in a hidden content control (`cannotDelete: true`, `cannotEdit: true`, `tag: "emr4-section-*"`). Called from `initApp()` (every document open) AND on patient load; no-op if already tagged. Uses the `"Hidden"` appearance string (the enum is undefined at runtime). `insertConsultHeader()` uses tag-based CN lookup (`emr4-section-cn`) as primary with text-search fallback. Safety net for **legacy** files only.
- **`create_patient_file.py`** — the per-patient `.docx` generator (supersedes the blank `create_patient_template.py` `.dotx` approach). Produces `FIRSTNAME LASTNAME DD-MM-YYYY.docx` with demographics header (always all 3 lines: name/dob/age/sex, address, phone+medicare), the 15 Dr Shera section headings each **baked into a locked content control at creation** (`w:lock=sdtContentLocked`), and the `document-type=patient` Custom XML Part. Core fn `create_patient_docx(PatientData, output_dir) -> Path` is the integration point for the future New Patient userform endpoint. CLI: `--first/--last/--dob/--sex/--address/--phone/--medicare/--out`. `SECTION_HEADINGS` (text, tag) pairs MUST stay in sync with `PROTECTED_SECTIONS` in taskpane.js.
- **Fonts** — body **Century Schoolbook 11pt**, headings **Garamond 12pt** bold blue `0000FF`, matching the Margaret Thompson template. Both fonts ship with Microsoft Office, so **no font install is required** on any machine running Word (confirmed present in `C:\Windows\Fonts`: `GARA.TTF`, `CENSCBK.TTF`). If guaranteed rendering on non-Office machines is ever needed, embed the fonts in the `.docx` (`settings.xml` `w:embedTrueTypeFonts` + `/word/fonts/` parts) — note embeddability/licensing bits and that Word Online has limited embedded-font support. For managed fleets, push fonts via Intune/Group Policy.
- **`CLAUDE.md`** added to repo root — codebase guidance for future Claude Code sessions.

### Not yet started
- Phase 2 onwards (see `implementation_plan.md §12`)
- **Verify** global Ctrl+Shift+N fires while cursor is in the document body (shared-runtime shortcut)
- **Tag `phase-1-stable`** once full Phase 1.5 testing is confirmed

---

## 4. Key Architectural Decision Pending

### Word Desktop vs Word Online — ✅ RESOLVED: Word Online (browser) is the target

Practices use browsers (Chrome confirmed working). Two-surface architecture is locked in:
**taskpane = quick view/jobs (tabs); Command Centre window = extensive work (mic + real estate)**.
The Command Centre must be a real window (iframe denies microphone). Office shows a
"wants to display a new window" **consent prompt** each time — this is Office's own
security gate, NOT the browser popup blocker, and appears unsuppressible (opening from
the click gesture is the only mitigation tried). Accept one "Allow" click per open.

Original analysis retained below for reference.

### (Reference) Word Desktop vs Word Online tradeoffs

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
| Command Centre iframe: "Microphone denied" | Office `displayInIframe` dialogs don't include `microphone` in their permissions policy | Use a real window (no `displayInIframe`); mic works there |
| "[object Object]" pasted as SOAP note | Gemini sometimes returns `generated_clinical_note` as a {S,O,A,P} object, not a string | `soapNoteToText()` in command-centre.js coerces to plain text; prompt also asks for a string |
| Taskpane filled with previous consult on file open | `getCurrentConsultText` read any consult slice in the doc regardless of session | Gate `runBackgroundSync` on `consultStarted` — no analysis until the doctor starts a consult |
| Phantom "Item 23" on freshly opened file | analyze-consultation defaults to item 23 with no duration; ran on near-empty doc | Same gating fix — nothing analysed until Start Consultation |
| Vertex AI froze whole backend (3+ min loads) | `model.generate_content()` is blocking, called in async route → froze the event loop | Wrap calls in `asyncio.to_thread` |
| Patient saved to "John Citizen" | finalize always used default patient | `FinalizePayload.patient_id`; taskpane + Command Centre both send it |
| Terminal flooded thousands of item numbers | MBS item 23 description literally lists every excluded item (3–11000+) | Truncate MBS descriptions to 200 chars; print one-line summary not full JSON |
| Demographics grey shading invisible in Word Online | `<w:shd>` appended to `<w:pPr>` after `<w:spacing>`/`<w:jc>` — out of CT_PPr schema order; desktop tolerates it, Online drops it (see OOXML note below) | `_shade_paragraph()` inserts `<w:shd>` via `insert_element_before()` at the schema-correct position |
| Word grammar underline under address | Double space between street type and locality in the input value | `_clean()` collapses internal whitespace runs to single spaces on all user-supplied fields (layout separators are literals, untouched) |

### ⚠️ OOXML injection — element order matters, Word Online is strict

When injecting raw OOXML into a `.docx` (e.g. `create_patient_file.py`), child
elements **must follow the schema-defined sequence order** for their parent.
`<w:pPr>` (CT_PPr) and `<w:rPr>` (CT_RPr) both enforce a specific child order —
for example inside `<w:pPr>`, `<w:shd>` must precede `<w:spacing>`, `<w:ind>`,
and `<w:jc>`.

**Word Desktop is lenient** and renders out-of-order elements anyway; **Word
Online is strict** and silently ignores a misplaced element (no error — the
effect just doesn't apply). Since Word Online is our primary target, always insert
injected elements at the correct position with python-docx's
`element.insert_element_before(new, *successor_tags)` rather than `.append()`.
This bit us twice now: the content-control `appearance` enum (use the `"Hidden"`
string) and the paragraph shading order above. Content controls already build a
clean child order; new injections should do the same.

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
| `create_patient_file.py` | **Per-patient `.docx` generator** — demographics + 15 locked section headers + Custom XML Part. `create_patient_docx()` is importable by the New Patient userform endpoint. Fonts match the MT template (Century Schoolbook / Garamond). |
| `create_patient_template.py` | Older blank `.dotx` template generator — **superseded** by `create_patient_file.py` (still uses Calibri defaults, no content controls). |
| `EMR4 Sidebar/src/taskpane/taskpane.js` | Full SPA logic — auth, tabs, audio scribe, AI sync, Word API calls |
| `EMR4 Sidebar/src/taskpane/taskpane.html` | SPA HTML — 8 tab panels + patient sidebar |
| `EMR4 Sidebar/src/taskpane/taskpane.css` | Styles + `@media (min-width:700px)` Command Center layout |
| `EMR4 Sidebar/manifest.xml` | Office add-in manifest (local dev) |
| `manifest.online.xml` | **Active manifest** — GitHub Pages source, shared runtime, ExtendedOverrides → shortcuts.json, v1.1.0.0. Re-sideload after manifest changes. |
| `EMR4 Sidebar/src/taskpane/shortcuts.json` | Keyboard-shortcut definition (Ctrl+Shift+N → StartConsultation) |
| `docs/taskpane/` | GitHub Pages copy of the taskpane (generated by sync_taskpane.py) |
| `docs/command-centre/command-centre.{html,js,css}` | Command Centre window (Scribe). Edit directly in docs/. |
| `sync_taskpane.py` | Copies taskpane src → docs/ and patches BACKEND_URL/NGROK_URL. Run after every taskpane edit. |
| `app/routers/consultation.py` | analyze-consultation, scribe-consultation, finalize. Backend AI. Restart uvicorn after edits. |
| `.env.example` | Template for local config (actual `.env` not committed) |

---

## 8. What to Do Next

1. **Finish testing Phase 1.5** — load Margaret Thompson → confirm "Document structure secured — N sections protected" status; Start Consultation → type/record → review SOAP → finalise; confirm no phantom analysis on open, CC lock/unlock works.
2. **Verify Ctrl+Shift+N** fires while cursor is in the document body (not just taskpane focused).
3. **Tag `phase-1-stable`** once the above is confirmed.
4. **Start Phase 2** — Living Diary: SharePoint-hosted `.docx`, Parse & Lock, appointment CRUD, internal messaging, SMS reminders.

### Deploy reminders
- Taskpane edit → `python sync_taskpane.py` → bump `?v=N` in taskpane.html → commit docs/ → push → **close & reopen the document** (shared runtime caches JS for the doc session; a sidebar toggle is not enough).
- Command Centre edit → edit in `docs/command-centre/` → bump `?v=N` → push (loads fresh each open).
- Backend edit (`consultation.py`) → restart uvicorn.
- Manifest edit → re-sideload `manifest.online.xml`.

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

*Last updated: 2026-06-16 — Phase 1.5 addendum: full taskpane CC lock (`setTaskpaneLocked`), Heading 1 content-control protection (`repairDocumentStructure`), per-patient generator `create_patient_file.py` with baked-in locked headers + template fonts + grey demographics band (shaded paragraphs, Online-safe OOXML order) + whitespace normalisation, CLAUDE.md added. Added §6 OOXML-injection-order note. HEAD at `3364bba` + whitespace-normalisation commit.*
