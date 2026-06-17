# EMR4 Centaur — Agent Handover Document

> **Protocol:** This file is the single source of truth for any agent (human or AI) picking up this project.
> Update it at the end of every session, every phase, and whenever a significant architectural decision is made.
> The user can trigger an update at any time by saying **"update the handover doc"**.

---

## 1. Project in One Paragraph

EMR4 Centaur is an AI-native, open-source, cloud-hosted General Practice management system for Australia. Microsoft Word (desktop or online) is the clinical frontend — the GP writes into a Word document and an Office.js add-in taskpane acts as a "Command Center" SPA alongside it. A FastAPI/PostgreSQL backend on GCP handles all clinical logic, and Google Gemini 2.5 Flash provides AI throughout. The full 12-phase implementation plan is in [`implementation_plan.md`](implementation_plan.md).

---

## 1A. Multi-Agent Handoff & Worktree Protocol

Goal: keep **single-track handoff seamless now**, while the repo is already shaped for
true parallel Codex + Claude Code + Antigravity work later.

### Current Baton

| Item | Value |
|---|---|
| **Mode** | Parallel-capable with Codex orchestration; single-track baton remains the integration path |
| **Baton ref** | `handoff/current` |
| **Integration worktree** | `C:\Users\YuriFrusin\Documents\EMR4` on `master` |
| **Agent worktree root** | `C:\Users\YuriFrusin\Documents\EMR4-worktrees\` |
| **Codex worktree** | `...\EMR4-worktrees\codex` on `codex/current` |
| **Claude worktree** | `...\EMR4-worktrees\claude` on `claude/current` |
| **Antigravity worktree** | `...\EMR4-worktrees\antigravity` on `antigravity/current` |
| **Current active track** | Phase 2 — hardening + diary interactivity foundation |
| **Next recommended work** | Canonical appointment time model, interval-based diary rendering, backend-backed room/roster/break config |

### One-time setup

From the integration worktree:

```powershell
python scripts\agent_worktrees.py setup
```

This creates:

- `codex/current`
- `claude/current`
- `antigravity/current`
- `handoff/current`

Each agent branch has its own worktree. Never check out the same branch in two
worktrees at once.

### Starting a session in an agent worktree

If the user says **"handin"**, do this before starting project work:

```powershell
python scripts\agent_worktrees.py handin
```

This is shorthand for `sync --fetch` **plus** the agent intake ritual: infer the
current agent from the worktree branch, list that agent's inbox, and print the
next queued/in-progress task packet. If the user says only "handin", do not ask
for the longer prompt; run this command and follow the printed packet.

1. Open the agent's own worktree.
2. Read `AGENTS.md`, `CLAUDE.md` where relevant, and `implementation_plan.md`.
3. Fetch and fast-forward to the baton:

```powershell
python scripts\agent_worktrees.py sync --fetch
```

or manually:

```powershell
git fetch origin
git merge --ff-only handoff/current
```

4. Run `git status`; proceed only from a clean tracked-code state.

### Ending a session / handing off

If the user says **"handoff"**, do all of this before stopping:

1. Update this file if state, architecture, gotchas, or next steps changed.
2. Run the relevant checks for the touched area, or record why they were not run.
3. Commit all intentional project-code changes on the current agent branch.
4. Move the baton and push the current branch + `handoff/current`:

```powershell
python scripts\agent_worktrees.py handoff --agent codex --commit-message "Short commit message" --message "Short baton note"
```

Use `--agent claude` or `--agent antigravity` from those worktrees.
If the work is already committed and the tree is clean, omit `--commit-message`.
If the user says **"handoff no push"**, run the same command with `--no-push`;
this moves the local baton but does not push the current branch or `handoff/current`.
Use `--no-push` only when the user explicitly asks for a local-only handoff.

### Parallel submit, not integration

For parallel work, non-orchestrator agents should submit their branch without moving
the baton:

```powershell
python scripts\agent_worktrees.py submit --agent claude --commit-message "Short commit message" --message "Short branch note"
```

`submit` commits/checkpoints if requested and pushes the current agent branch only.
It does **not** move `handoff/current`. Codex reviews/integrates submitted branches,
then advances `master` and `handoff/current` after user-approved integration.

### Codex Orchestrator Protocol

Codex is the default orchestration agent for EMR4. This means:

- Codex owns integration sequencing, branch review, and final merge recommendations.
- Claude Code and Antigravity are encouraged to disagree, flag risks, and propose
  better designs; dissent should be preserved in the workstream notes.
- Final technical recommendation sits with Codex, but user approval overrides all
  agent hierarchy.
- No non-orchestrator agent should merge to `master` or move `handoff/current`
  during parallel mode unless the user explicitly says so.
- Each parallel workstream must have a narrow owner, file boundary, verification
  plan, and merge criteria before coding starts.
- The live board is [`orchestration/parallel_workstreams.md`](orchestration/parallel_workstreams.md).
- Agent-specific task packets live under `orchestration/agent_inbox/<agent>/`.

### Agent inbox commands

Codex can dispatch a task packet:

```powershell
python scripts\agent_worktrees.py dispatch --agent claude --title "Short title" --mission "..." --in-scope "..." --out-of-scope "..." --verification "..." --merge-criteria "..."
```

Any agent can list and read its queue:

```powershell
python scripts\agent_worktrees.py inbox --agent claude
python scripts\agent_worktrees.py brief --agent claude
```

When an agent starts a packet, it may mark it:

```powershell
python scripts\agent_worktrees.py claim --agent claude --task claude-short-title --status in_progress
```

The packet itself contains the required `handin` and `submit` commands. Inbox
packets are coordination artifacts; agents may update their packet's completion
notes, but should not edit other agents' packets.

When a worker uses the packet's `submit` command with `--task`, the helper marks
the source packet `submitted`, creates a Codex review packet under
`orchestration/agent_inbox/codex/`, commits it with the branch, and pushes the
worker branch. Codex can check submitted work with:

```powershell
python scripts\agent_worktrees.py poll --fetch
```

### Parallel ownership rule

Split by ownership boundary:

- Backend API/schema branch
- Taskpane/diary frontend branch
- Security/tests/docs branch

Each branch should have a clear owner, a narrow file boundary, and an integration
review before merge back to `master`.

### Worktree mirror boundary

All worktrees should be project-code mirrors when clean. Differences are allowed
only for ignored local/runtime files:

- `.env`, `.venv/`, `node_modules/`
- generated `.docx` files and `patient_files/`
- `.claude/settings.local.json`, `CLAUDE.local.md`, `claude.json`
- logs, temp files, local exports such as root `emr_centaur_logo.png`

Do not commit real patient data, local secrets, generated clinical documents, or
agent session state.

---

## 2. Repository & Git State

| Item | Value |
|---|---|
| **Remote** | https://github.com/yurifrusin/EMR4.git |
| **Branch** | `master` |
| **Last pushed commit** | `01c1d84` — "AGENTS.md: document grid rebuild requirement before interactivity" |

### Tag map (all tags pushed to remote)

| Tag | Commit | What it contains |
|---|---|---|
| `phase-1-raw` | `257e214` | Phase 0 + Phase 1 initial implementation — first working version |
| `phase-1-popout-experiment` | `d79cb1d` | All pop-out / displayDialogAsync experiments from session 2 |
| `phase-1-stable` | _Phase 1 close-out commit_ | Phase 0 + 1 + 1.5 complete & tested: patient file generator, locked section headers, CC lock, demographics, security P0 fixes, doc reconciliation. Ctrl+Alt+N (start consultation) runtime-verified firing from the document body. |

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
| `b160dd0` | Fix `_inject_custom_xml`: overwrite only `item1.xml` body — no duplicate OPC Override → corrupt `.docx` eliminated |
| `a9c045a` | Fix `POST /patients/with-file` 500: validate `PatientOut` first, then construct `PatientWithFileOut` |
| `d0d99b9` | Multi-column Word table diary + `diary_template.json` (retained as reference; **superseded by native grid**) |
| `1a6f15a` | Native Diary Grid (`docs/diary/`): read-only room×time grid with lifecycle colours + date nav + auto-refresh |

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
- **Start Consultation** button + **Ctrl+Alt+N** (shared runtime, ExtendedOverrides/shortcuts.json, manifest v1.1.0.0) plants the dated header under Contemporaneous Notes and bookmarks it (`EMR4_NOTE_POINT`); notes/SOAP insert right after it. **Was Ctrl+Shift+N — changed because Chrome reserves that for Incognito and swallows it before Word sees it.** Avoid Chrome-reserved combos for any future shortcut (e.g. the planned Parse & Lock Ctrl+Shift+B toggles Chrome's bookmarks bar — pick a Ctrl+Alt / Alt+Shift combo instead).
- **Gating**: `runBackgroundSync` does nothing until `consultStarted` (set by Start Consultation / opening Command Centre); prevents re-analysing a previously finalised consult on open. Reset on patient load / logout / finalise.
- **consult_finalized** message: Command Centre pushes its finalised coding back to the taskpane Consult tab (locked) + refreshes history/meds/sidebar.
- Backend `analyze-consultation`/`scribe-consultation` wrapped in `asyncio.to_thread` (Vertex AI was blocking the event loop); MBS descriptions truncated to 200 chars in prompt context (item 23's full text listed every excluded item → huge/slow prompt); encounters saved with `status=Finalized`; `finalize` takes `patient_id`.

### Phase 1.5 addendum (this session) ✅
- **`setTaskpaneLocked(locked)`** — disables/restores all taskpane editing controls while Command Centre is open: `btn-command-center`, `btn-start-consult`, `btn-lock`, `btn-search-patient`, `btn-open-file`, `btn-add-mbs/snomed/rx`, `btn-finalize`, `consult-type` input, and dynamic coding row containers (`.cc-locked` CSS). Called on CC open/close. Finalize stays disabled if consult was already finalised inside CC.
- **`repairDocumentStructure()`** — wraps each known Heading 1 section header in a hidden content control (`cannotDelete: true`, `cannotEdit: true`, `tag: "emr4-section-*"`). Called from `initApp()` (every document open) AND on patient load; no-op if already tagged. Uses the `"Hidden"` appearance string (the enum is undefined at runtime). `insertConsultHeader()` uses tag-based CN lookup (`emr4-section-cn`) as primary with text-search fallback. Safety net for **legacy** files only.
- **`create_patient_file.py`** — the per-patient `.docx` generator (supersedes the blank `create_patient_template.py` `.dotx` approach). Produces `FIRSTNAME LASTNAME DD-MM-YYYY.docx` with demographics header (always all 3 lines: name/dob/age/sex, address, phone+medicare), the 15 Dr Shera section headings each **baked into a locked content control at creation** (`w:lock=sdtContentLocked`), and the `document-type=patient` Custom XML Part. Core fn `create_patient_docx(PatientData, output_dir) -> Path` is the integration point for the future New Patient userform endpoint. CLI: `--first/--last/--dob/--sex/--address/--phone/--medicare/--out`. `SECTION_HEADINGS` (text, tag) pairs MUST stay in sync with `PROTECTED_SECTIONS` in taskpane.js.
- **Fonts** — body **Century Schoolbook 11pt**, headings **Garamond 12pt** bold blue `0000FF`, matching the Margaret Thompson template. Both fonts ship with Microsoft Office, so **no font install is required** on any machine running Word (confirmed present in `C:\Windows\Fonts`: `GARA.TTF`, `CENSCBK.TTF`). If guaranteed rendering on non-Office machines is ever needed, embed the fonts in the `.docx` (`settings.xml` `w:embedTrueTypeFonts` + `/word/fonts/` parts) — note embeddability/licensing bits and that Word Online has limited embedded-font support. For managed fleets, push fonts via Intune/Group Policy.
- **`CLAUDE.md`** added to repo root — codebase guidance for future Claude Code sessions.

### Phase 2 — Appointments & The Living Diary (in progress)

#### ✅ New Patient file↔DB bridge (commits b160dd0, a9c045a)
- `POST /api/v1/patients/with-file` — atomically creates DB row + generates `.docx`
  to `settings.patient_files_dir` (default `./patient_files/`, override in `.env`).
- `_inject_custom_xml` fixed: rewrites only the body of `customXml/item1.xml`,
  leaving all OPC packaging intact — no more corrupt `.docx` from duplicate Override PartNames.
- `PatientWithFileOut` schema returns `generated_filename` alongside the full patient record.
- New Patient form in the taskpane (`+` button in banner) POSTs to `/with-file` and
  shows the generated filename + copy instructions.

#### ⭐ Strategic Pivot — Native Diary Grid (decisions 2026-06-17)
The diary moved **off Word and onto a native HTML/JS web grid** hosted in `docs/diary/`.
Postgres is the single source of truth; lifecycle colours are CSS off `appointment.status`.
This eliminates: the Word-table sync fork, "who writes status to the doc" ambiguity,
Parse & Lock (no free text to parse), co-authoring merge races, and OOXML complexity.
The Word diary `.docx` was built (`d0d99b9`) as a proving exercise — it confirmed the
diary is app-shaped, not document-shaped. The Word diary is now retired from the deploy path.
The clinical note stays in Word (document-shaped, prose, letters, printing).

Per-surface hybrid architecture (locked):
- **Word**: clinical note, letters, referrals — document-shaped content
- **Native web grid**: diary, waiting room, messaging, billing review — app-shaped content
- **Online/mobile booking portal** (future): same appointments API backbone, different client

Online/mobile booking is the clinching architectural reason — `AppointmentType.is_bookable_online`,
`BookingChannel.{Online,App,Kiosk}`, and `GET /slots/{practitioner_id}` already exist.
The staff diary grid and a future patient booking portal are just two clients of the same API.

#### ✅ Native Diary Grid — read-only first slice (commit 1a6f15a)
- **`docs/diary/diary.{html,js,css}`** — dedicated Office dialog window (no patient required).
  - Opens via `displayDialogAsync(DIARY_URL, {height:90,width:90})` from taskpane `📅` button.
  - Same `ready`→`auth` token handshake as the Command Centre.
  - Template config embedded in `diary.js` (mirrors `diary_template.json` at repo root).
  - Fetches `GET /appointments?date_from&date_to` + `GET /appointments/types` in parallel.
  - Renders room×time grid: columns from template, 15-min slots 09:00–17:00, break rows.
  - Appointment→column mapping by practitioner AHPRA (`a.practitioner.ahpra_number`).
  - **Lifecycle colours**: Confirmed/Arrived = ALL-CAPS + bold blue, InConsult = underline,
    Completed = green, Booked = plain black, Cancelled/NoShow/DNA = strikethrough.
  - Appointment-type `color_hex` applied as a left-border accent (join by UUID from types list).
  - Prev/Next/Today date navigation; Refresh button; 60-second auto-refresh.
  - Read-only (no booking/drag/status mutations this slice).
- **`app/schemas/appointments.py`** — added `ahpra_number: Optional[str]` to `PractitionerBrief`
  so the diary JS can map appointments to columns by AHPRA. Zero migration required.
- **`seed.py`** — `AppointmentType` + `PractitionerSchedule` + 3 sample appointments
  (Margaret 09:00 `Confirmed`, Billy 09:15 `Booked`, Margaret 10:00 `Booked`) seeded idempotently.
- **Taskpane** — `📅` Diary button in banner controls; `openDiary()` function (no patient guard).
  Cache-bust bumped to `v=28`.

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
| `AGENTS.md` | **This file** — agent handover |
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
| `EMR4 Sidebar/src/taskpane/shortcuts.json` | Keyboard-shortcut definition (Ctrl+Alt+N → StartConsultation) |
| `docs/taskpane/` | GitHub Pages copy of the taskpane (generated by sync_taskpane.py) |
| `docs/command-centre/command-centre.{html,js,css}` | Command Centre window (Scribe). Edit directly in docs/. |
| `docs/diary/diary.{html,js,css}` | **Native Diary Grid** — edit directly in docs/ (NOT via sync_taskpane.py). Bump `?v=N` on each deploy. |
| `diary_template.json` | Practice diary config (columns, slot defaults, breaks, footer). Embedded verbatim in `diary.js`; must be kept in sync. Future: serve from `/api/v1/diary/template`. |
| `create_diary_file.py` | Word-table diary generator (RETIRED — built `d0d99b9`, superseded by native grid). Retained for reference only. |
| `sync_taskpane.py` | Copies taskpane src → docs/ and patches BACKEND_URL/NGROK_URL. Run after every taskpane edit. |
| `app/routers/consultation.py` | analyze-consultation, scribe-consultation, finalize. Backend AI. Restart uvicorn after edits. |
| `.env.example` | Template for local config (actual `.env` not committed) |

---

## 8. What to Do Next

1. ✅ **Phase 1 closed out** — `phase-1-stable` tagged. Patient file generator, locked
   section headers, CC lock, demographics, and security P0 fixes all tested.
2. ✅ **Ctrl+Alt+N runtime-verified** — confirmed firing while the cursor is in the
   **document body** (not just the taskpane), via the shared runtime
   (`shortcuts.json` → manifest `SharedRuntime` + `ExtendedOverrides` →
   `Office.actions.associate`). The in-taskpane keydown fallback remains as a backstop.
   (Shortcut was Ctrl+Shift+N until it was found to trigger Chrome Incognito; now Ctrl+Alt+N.)
3. **Start Phase 2** — Living Diary: SharePoint-hosted `.docx`, Parse & Lock, appointment
   CRUD, internal messaging, SMS reminders. **First** resolve the New Patient file↔DB
   bridge below.

### 🛠️ Dev stack startup — now one command
`.\run_dev.ps1` brings up the full local stack (Postgres + uvicorn + ngrok on the
reserved domain + npm dev-server) with pre-flight checks, readiness waits, and
idempotent re-run. `start_emr.bat` is a double-click shim. Use `-Down` to stop.

**⚠️ Cross-file invariant:** `$NgrokDomain` in `run_dev.ps1` must match `NGROK_URL`
in `sync_taskpane.py`. The reserved domain is `property-cinch-backfield.ngrok-free.dev`;
plain `ngrok http 8001` (the old `.bat` behaviour) hands out a random URL that the
taskpane can't reach.

### 🛠️ Remaining friction — the taskpane deploy loop
Dev stack startup is solved. The remaining drag is the **taskpane change cycle**:
edit src → `python sync_taskpane.py` → bump `?v=N` in taskpane.html → commit `docs/`
→ push → **close & reopen the Word document**. Candidate future improvement: a
`deploy_taskpane.ps1` that does sync + version-bump + commit in one command.
Not urgent for Phase 2 but worth adding during heavier frontend work.

### ✅ New Patient bridge — RESOLVED
`POST /api/v1/patients/with-file` creates DB row + `.docx` atomically. `document_url`
is left null at creation and backfilled by `autoDetectPatient()` on first open. See §3 Phase 2.

### 🏗️ Next: Diary Grid interactivity (backend additions required)
The read-only first slice is shipped. Before adding booking/drag/status mutations:

1. **Enrich `AppointmentOut`** — embed `appointment_type` (with `color_hex`) and add
   `end_time`. Currently the diary fetches `/types` separately and joins client-side.
2. **Allow `practitioner_id` in `AppointmentUpdate`** — required for drag-across-columns
   (currently only `start_time`/`duration_minutes` are mutable).
3. **Fix `/slots` overlap math** — currently uses exact start-time equality and ignores
   `duration_minutes`. A 30-min booking leaves its overlapping slot "available" → double-book
   bug for any online booking portal. **Must fix before any public-facing booking.**
4. **Conflict validation** on create/update; **role gating** (receptionist vs GP) on
   mutating routes (currently none).
5. **`Room` + `DiaryRoster` models** — date×room→practitioner|label + CRUD. Currently columns
   are hard-coded in `diary_template.json` / embedded in `diary.js`.

#### ⚠️ Grid must be rebuilt before interactivity — per-column independent time slots

The current grid is an HTML `<table>` with shared `<tr>` rows across all columns.
This is **incompatible with interactivity**: you cannot insert a 10:10 slot in Room 1
only, remove 10:15 from Room 2 to create a longer block, or drag-resize an appointment
across arbitrary time boundaries.

**Before any booking/drag/edit work, replace the `<table>` with independent CSS-positioned
column divs.** Each column is its own stack; time labels are text within each slot div;
slot height is proportional to duration (e.g. 15 min = 1 unit). No shared rows. The
time gutter on the left is a reference overlay, not a structural spine. This is also the
prerequisite for SSE push updates (incremental DOM patch vs full re-render).

### 🏗️ Later Phase 2 items (deferred)
- **Parse & Lock** — now unnecessary for the diary (the grid replaces it). Still relevant if
  any Word-based annotation workflow needs structure extraction later.
- **Internal messaging router** — models exist (`InternalMessage`); no endpoints yet.
  Messages tab in the diary window is a placeholder.
- **SMS reminders** — ClickSend, 24–48h scheduler, two-way YES/NO webhook.
- **Waiting Room live feed** — `/waiting-room` endpoint exists; Waiting Room tab is placeholder.
- **Lifecycle actions** (Confirm, Arrived, InConsult, Completed) — as clickable status updates
  on diary grid cells. Keyboard shortcuts (Ctrl+Alt+* class) and/or row buttons.
- **`GET /api/v1/diary/template`** — serve `diary_template.json` via API instead of embedding
  in `diary.js`, as a prelude to the template-builder UI.
- **Multi-room/multi-practitioner roster** — `DiaryRoster` model + per-date assignment UI.
- **Online/mobile patient booking portal** — future separate client of the same appointments API.

### 🔒 Security workstream now in the plan (implementation_plan.md §15A)

A full cybersecurity review was done (2026-06-16). It added a `security-engineer`
sub-agent (§14), expanded §15, and created **§15A Security Workstream** with a
threat-model requirement, foundational controls to land early (PostgreSQL RLS for
tenant isolation, an `audit_log` table, secrets management, CORS/JWT hardening,
field-level encryption), and per-phase security gates (booking/kiosk identity proofing,
prompt-injection defence, Hive Mind de-ID, Results Relay auth, PRODA certs).
**P0 issues — FIXED (commit follows):** `config.py` now fails closed (refuses to
start when `ENVIRONMENT` != `dev` and `secret_key` is the public default), and CORS
is locked to an allow-list (`settings.cors_origins`: GitHub Pages + localhost:3000)
instead of `["*"]`. Set `ENVIRONMENT` + a generated `SECRET_KEY` in prod `.env`.
**Still open (P1+):** tenancy is enforced by manual per-query `practice_id` filters
(correct today, but PostgreSQL RLS is the recommended defense-in-depth); JWT in
`localStorage`; `audit_log` table absent.

### Deploy reminders
- Taskpane edit → `python sync_taskpane.py` → bump `?v=N` in taskpane.html → commit docs/ → push → **close & reopen the document** (shared runtime caches JS for the doc session; a sidebar toggle is not enough).
- Command Centre edit → edit in `docs/command-centre/` → bump `?v=N` → push (loads fresh each open).
- Backend edit (`consultation.py`) → restart uvicorn.
- Manifest edit → re-sideload `manifest.online.xml`.

---

## 9. Handover Protocol

### For the incoming agent
1. Read this file (`AGENTS.md`) in full
2. Read `implementation_plan.md` §2 (Architecture Pivots) and §12 (Phases)
3. Run `git log --oneline` and `git tag` to orient yourself
4. Check `git status` — should be clean
5. Ask the user what they want to work on; don't assume

### For the outgoing agent (before context runs out)
1. Run `git status` — commit anything uncommitted
2. Update this file: current HEAD commit, current state, any new decisions or gotchas
3. Push: `git push origin master`
4. Tell the user: *"AGENTS.md is updated and pushed — safe to start a new session"*

### Triggering updates
The user can say **"update the handover doc"** at any time to trigger a refresh of this file.

> **Note on usage limits:** Claude cannot detect when the user's session limit is approaching. The user should update this file proactively at the end of each major task or when switching topics. Watch for signs of context compression (summaries appearing in the conversation) as a signal that a handover update is due.

---

*Last updated: 2026-06-17 — Phase 2 in progress. New Patient bridge shipped. Strategic pivot: diary on native HTML/JS web grid (locked). Native Diary Grid read-only first slice complete (`docs/diary/`): room×time grid, lifecycle colours, per-column breaks, break-edit modal, date nav, silent auto-refresh, and `📅` taskpane button. Backend hardening now includes authenticated consultation AI endpoints, practice-scoped finalise, transactional patient file generation, appointment role gates, conflict validation, `/slots` duration-overlap logic, `AppointmentOut.end_time`, embedded `appointment_type`, and mutable `practitioner_id`. Multi-agent mode is now parallel-capable with Codex as orchestrator and `orchestration/parallel_workstreams.md` as the live workstream board. Next: canonical appointment time model, interval-based diary rendering, backend-backed Room/DiaryRoster/break config, regression tests, and Gemini SDK migration before the 2026-06-24 deprecation removal date.*
