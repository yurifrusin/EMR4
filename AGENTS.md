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
| **Current active track** | Sprint 33 - appointment proposal audit/history foundation integrated locally; closeout/push/audit in progress |
| **Next recommended work** | After Sprint 33 push/audit, continue with the next Programme 2D receptionist-safety slice unless Yuri input is needed |

`codex/current` is the durable Codex mirror branch. Codex-app subagents are
separate disposable worker checkouts and may live under `.codex/worktrees/...`.
Use unique branches for those workers, e.g. `codex/time-model` or
`codex/<short-task-name>`, then review/integrate them through the orchestrator
before realigning `master`, `handoff/current`, and the durable mirrors.

Codex role separation:

- Ariadne/orchestrator Codex runs on the integration worktree unless explicitly
  stated otherwise and owns final review/integration.
- Codex worker/subagents use disposable or task-specific branches, never
  `master`; use clear task branches such as `codex/<short-task-name>`.
- Future Codex plan packets should include `| Role | orchestrator |` for
  Ariadne-owned orchestration/review work, or `| Role | codex-worker |` plus
  `| Worker Name | ... |` and `| Worker Branch | codex/<short-task-name> |`
  for separate Codex workers.
- Codex workers may submit plans/reviews to Codex's inbox, but Ariadne remains
  responsible for final integration. Ariadne must not treat an
  orchestrator-created Codex plan as proof that a separate worker has submitted.

### Orchestration changelog / protocol alerts

- Protocol changes are part of the handover state. Worker agents may remember
  older process details, so every significant orchestration change must be added
  to `orchestration/protocol_alerts.md`.
- `handin` prints `orchestration/protocol_alerts.md` before the task packet.
  Workers must trust those alerts over remembered prior-session process details.
- `submit` has been fixed to resolve the active worktree root. Workers should
  use the packet's `submit` command. If it fails, they must stop and report the
  exact command, working directory, branch, and error output. They must not
  manually push to `master` or `handoff/current`.
- Only Codex acting as orchestrator advances `master` and `handoff/current` in
  parallel mode unless the user explicitly says otherwise.
- GitHub Pages deployment is part of the integration surface. Deploy Pages from
  canonical `master` only. Do not manually deploy worker mirror branches
  (`codex/current`, `claude/current`, `antigravity/current`) unless Codex has
  just confirmed they are aligned to `master`; a later worker-branch Pages
  deployment can overwrite the live artifact with stale taskpane/diary assets.

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

After Ariadne announces `HANDIN READY`, Ariadne should prompt external workers
through cheap headless text channels before using GUI automation. Yuri should
not need to explicitly invoke routine sprint prompts.

Antigravity uses the CLI from a fresh project-scoped session unless a current
conversation ID has been verified. Old conversation IDs can disappear after app
or CLI restarts, and `--print` may return no stdout even when the transcript
records progress; poll/git remains the authoritative proof of submission.

```powershell
C:\Users\YuriFrusin\AppData\Local\agy\bin\agy.exe --add-dir C:\Users\YuriFrusin\Documents\EMR4-worktrees\antigravity --print "<prompt>"
```

Antigravity CLI settings live in
`C:\Users\YuriFrusin\.gemini\antigravity-cli\settings.json`; keep this file
valid JSON encoded as UTF-8 without BOM, otherwise the CLI silently falls back
to defaults. The EMR4 routine posture is `toolPermission=always-proceed`,
`artifactReviewPolicy=always-proceed`, `allowNonWorkspaceAccess=false`, and
`trustedWorkspaces` limited to the Antigravity worker worktree.

Claude uses the standalone headless driver from a clean Ariadne shell and the
Claude worker worktree:

```powershell
python scripts\drive_agent_headless.py --cwd C:\Users\YuriFrusin\Documents\EMR4-worktrees\claude --phase plan --mint-session --prompt "handin, write the implementation plan, submit the plan packet, then stop"
python scripts\drive_agent_headless.py --cwd C:\Users\YuriFrusin\Documents\EMR4-worktrees\claude --phase implement --prompt "handin, then complete sprint task"
```

Use `--phase plan` for plan-gated handin and `--phase implement` only after the
plan is approved. Do not `--resume` across the plan gate because the phase
defaults intentionally use different models (`plan` = Opus/medium,
`implement` = Sonnet/medium); `--resume` is only for recovery within the same
phase/model. Keep the default Claude permission posture (`acceptEdits` plus
`Bash`, `Edit`, `Write`, `Read`, `Grep`, `Glob`) on Claude worker branches only.
Do not use `bypassPermissions`, `--bare`, or run from `master`/the integration
worktree unless Yuri explicitly approves a debugging exception. Poll/git remains
the authoritative proof of submission, not the CLI result JSON.

If a CLI is unavailable in the current Codex thread/session, Ariadne should
fall back to Computer Use where appropriate and ask Yuri only for the smallest
manual prompt still needed.
After all plan packets for a sprint are reviewed and accepted, Ariadne should
release implementation to independent workers in parallel where their scopes do
not overlap. Use separate CLI processes for Claude and Antigravity rather than
serial release, unless a worker channel is currently unproven, failing, or likely
to mutate overlapping files. If release is intentionally serialized for safety,
record the reason in the closeout or protocol notes.
After a Codex app or Windows restart, Computer Use may not appear as separate
desktop `click`/`type` tools even when the plugin is installed. Ariadne should
first run the Computer Use skill's JS bootstrap path through the Node REPL and
verify `sky.list_apps()` before declaring it unavailable. Old explicit
plugin-cache paths can become stale after an app update; use the current
available skill path and do not rely on tool-search results alone.

When an agent starts a packet, it may mark it:

```powershell
python scripts\agent_worktrees.py claim --agent claude --task claude-short-title --status in_progress
```

For non-trivial sprint work, workers must pass the implementation-plan gate
before editing project code. After `handin`, write the plan, show it in the GUI,
and capture it for Codex:

```powershell
python scripts\agent_worktrees.py plan --agent claude --task claude-short-title --summary "Short plan summary" --understanding "..." --surface "..." --out-of-scope "..." --files "..." --steps "..." --acceptance "..." --risks "..."
```

Then stop. Do not code until the user/Codex says **"complete sprint task"**.
During the plan gate, workers may create, commit, and push the
implementation-plan packet and minimum coordination-file status changes needed
to submit that plan to Codex's inbox. This permission does **not** allow
production code changes: no `app/`, diary UI, taskpane, migrations, tests, or
runtime docs beyond files explicitly required for the plan itself. For
Antigravity, artifact approval during this phase means "submit the plan packet
only", not "implement the task".
If the agent platform offers or displays an "auto-proceed", "auto-approved", or
similar continuation after the implementation plan, treat that as **not approved**
for EMR4 sprint packets. The worker must stop even if the app would otherwise
continue, and wait for an explicit `complete sprint task` message from the user
or Codex/orchestrator.
Plans must name the intended surface/boundary and any visually adjacent surfaces
that must not change.

If an agent notices a worthwhile follow-up that is outside its current packet,
it should capture the idea for Codex instead of leaving it only in the app chat:

```powershell
python scripts\agent_worktrees.py suggest-task --agent claude --title "Short suggested task" --rationale "Why this matters" --scope "Likely files or boundary" --verification "How Codex should verify it"
```

A suggested task is not permission to implement the work. Codex/orchestrator
triages `suggested` packets from `orchestration/agent_inbox/codex/`, then either
dispatches the work, folds it into an active sprint, defers it, or rejects it.

The packet itself contains the required `handin` and `submit` commands. Inbox
packets are coordination artifacts; agents may update their packet's completion
notes, but should not edit other agents' packets.

When a worker uses the packet's `submit` command with `--task`, the helper marks
the source packet `submitted`, creates a Codex review packet under
`orchestration/agent_inbox/codex/`, commits it with the branch, and pushes the
worker branch. Codex can check submitted durable-worker work with:

```powershell
python scripts\agent_worktrees.py poll --fetch
```

By default `poll` checks Claude/Antigravity durable submits, submit-alert
branches, and the local Codex inbox. It intentionally skips old remote
`codex/*` disposable worker branches because historic Codex worker refs can make
the command slow and noisy. When a current Codex subagent worker is expected to
have submitted on a `codex/<task>` branch, use:

```powershell
python scripts\agent_worktrees.py poll --fetch --include-codex-workers
```

If a worker app says it submitted but `poll --fetch` does not show the expected
plan or review packet, Ariadne should inspect that worker's durable worktree for
uncommitted `orchestration/agent_inbox/codex/...` files and task-packet status
changes. A local-only plan is not a submission. Nudge the worker to run the
packet/protocol `submit --task ...` path so the plan/review packet is committed
and pushed to its durable branch; do not treat the GUI message as sufficient.

After `poll --fetch` shows the expected implementation review packets for the
active sprint, Codex/orchestrator may proceed through inspection, bounded repair,
verification, and draft closeout unless a packet is missing, out of scope,
unsafe, failing verification, or otherwise needs user or worker clarification.
Before pushing sprint changes to `master`, Ariadne should summarize the review
result, verification run, and manual user tests from `orchestration/sprint_closeout.md`.
Before giving that user-test list, Ariadne should run every feasible Codex-side
or tool-enabled test first, including browser/Chrome checks for real UI
affordances when relevant and available, and should hotfix issues found before
asking the user to test the remainder. If a user-review item appears blocked by
missing tooling, Ariadne should first research and use suitable local or online
tools to complete the review independently where safe. Ariadne may install or
configure such tooling and may log into EMR4 with dummy dev user/dev admin
credentials for non-PHI dev verification; flag Yuri only for material risks,
cost/security implications, or genuine manual intervention such as restarting
Codex or approving an external console action. Then wait for user approval unless the
user explicitly granted proceed-through integration for that sprint. This
post-poll review permission is separate from the plan gate: workers still must
not implement until the explicit `complete sprint task` approval is given.

Cost-conscious UI review rule: Ariadne should conserve model/tool credits during
user-review automation. Use the cheapest reliable signal first and escalate only
when needed:

1. Backend/API tests and direct HTTP probes.
2. Static frontend checks (`node --check`, asset/version checks, lint-like
   project checks where configured).
3. Version-controlled review harnesses and reusable parameterized check
   primitives, such as `assert_text_in(selector, text)`,
   `assert_count(selector, n)`, `assert_api_field(url, field)`, and
   `assert_version(html, v)`.
4. Headless or in-app browser scripts with narrow assertions against known URLs,
   selectors, state, and console logs.
5. Scoped accessibility/DOM summaries for only the relevant pane/modal/control.
6. Targeted browser/Chrome interaction for behaviours that require real input
   events, such as mouse drag/resize or Office dialog behaviour.
7. Cropped/small screenshots only when visual layout or affordance cannot be
   verified structurally.
8. Yuri-only manual tests only when the remaining check genuinely needs Yuri's
   account, device, clinical judgment, external console, or real-world context.

Avoid broad screenshots, full DOM dumps, repeated polling loops, and exploratory
mouse-click navigation unless they are the only practical way to verify the
behaviour. Prefer small Playwright/CDP/JavaScript assertions such as "open this
URL, click this known control, assert this section count/text/classes/buttons"
over step-by-step Computer Use browsing. If a visual check is necessary, reduce
the viewport or crop to the relevant application region where possible.

The main cost win is removing the model from deterministic execution loops, not
swapping one model for another. For recurring review checks, Ariadne should
prefer the pattern "explore once, crystallize into a script, run free forever":
after any paid/exploratory UI review discovers a stable check, convert it into a
stored Playwright/pytest/script primitive or spec that emits compact structured
output (`passed`, `failed`, `evidence`). On future sprints, run the harness and
let Codex interpret only failures or genuinely ambiguous results. Local models
such as Gemma should not be added to the sprint loop unless measured residual
interactive/visual review cost remains high after this scripting approach.
The first ratified deterministic UI harness lives in `review/` and is run with
`pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`; CI
also runs it via `.github/workflows/ui-review.yml` for diary/review changes.

After Codex integrates a submit, it must:

1. Mark the source task packet and Codex review packet `integrated` or `superseded`.
2. Record the outcome in `orchestration/integration_log.md`:

```powershell
python scripts\agent_worktrees.py record-integration --agent antigravity --task antigravity-example --branch antigravity/current --review "Reviewed and integrated" --integration-commit HEAD --result integrated --follow-up "Mirrors realigned"
```

3. Update or finalize `orchestration/sprint_closeout.md`.
4. Report the closeout summary to the user before pushing unless the user has
   explicitly granted proceed-through integration for that sprint.
5. Push `master` and `handoff/current`.
6. Realign each clean durable worker mirror to the integrated baton from that
   worker worktree:

```powershell
python scripts\agent_worktrees.py realign --agent claude --apply
python scripts\agent_worktrees.py realign --agent antigravity --apply
python scripts\agent_worktrees.py realign --agent codex --apply
```

This resets the clean mirror to `origin/handoff/current`; it does not replay the
already-integrated submit commit. By default it also updates the durable remote
mirror branch with `--force-with-lease`, so the next worker submit starts from a
clean remote baseline. Use `--no-push` only for a deliberate local-only repair.
Dirty mirrors must be reviewed before realign.

7. Run the orchestration audit:

```powershell
python scripts\agent_worktrees.py audit --fetch
```

8. Retire stale disposable worker worktrees only after audit confirms they are clean:

```powershell
python scripts\agent_worktrees.py retire-stale
python scripts\agent_worktrees.py retire-stale --apply
```

`retire-stale` is a dry run by default. Dirty worktrees are never removed by the
routine; they must be reviewed or explicitly abandoned first.

9. Report final post-push closeout status to the user:
   - every Codex-side/tool-enabled review and test already run, including
     browser/Chrome/Office-dialog checks for UI work when relevant and available
   - any bounded hotfixes applied after those checks
   - what remains for the user to manually review or test because Ariadne could
     not confirm it with available tools, or "none required" with the reason
   - detailed step-by-step user review instructions for each remaining
     Yuri-only check, including setup/preconditions, exact UI path, expected
     result, suspicious/failure signs, what can be skipped, and what evidence or
     screenshots to report back
   - what does not need manual testing yet
   - where Codex recommends taking the project next
   - any project-level concern raised by the integrated submissions

Ariadne's closeout ping is the user's final sprint notification. It must not
hand off avoidable review work: run all feasible tool-enabled checks first, then
state only the residual human checks that still require Yuri's clinical
judgment, external service console, phone/device, real-world account ownership,
or another context Ariadne cannot safely reproduce after tool research. When
residual human checks remain, explain them as practical, detailed test steps
rather than abstract acceptance criteria, including the goal of each check,
setup/preconditions, exact UI path, expected result, suspicious/failure signs,
what can be skipped, and what evidence or screenshots to report back. If local
notification variables are configured, also send a short non-PHI alert with
`python scripts\notify_yuri.py`; keep the full details in Codex/repo docs, not
push notifications. If notification delivery is not configured or fails, report
that in the Codex closeout summary and continue with the in-thread notification.
If a sprint closes cleanly and Ariadne's tool-enabled review leaves no
Yuri-only tests, decisions, or approvals, Ariadne should keep the project moving:
choose the next recommended sprint from the current programme/closeout state,
dispatch it, announce `HANDIN READY`, and use external-agent CLIs to prompt
Claude/Antigravity where available, falling back to Computer Use only when text
channels are unavailable or a GUI interaction is genuinely required. Stop and
notify Yuri only when user input, manual review, unusual risk, or a priority
decision is genuinely needed.

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
| **Latest integration commit** | Current Sprint 31 AI provider boundary + deterministic diary review harness closeout commit |

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
| `0ab2f27` | Integrates Claude appointment/security regression tests + Antigravity diary interval rendering; fixes `submit` worktree root detection |

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
- **GitHub Pages deployment discipline**: Pages must deploy canonical `master`.
  Worker mirror branches can trigger Pages deployments from stale artifacts if
  manually selected; deploy them only immediately after Codex realigns mirrors to
  `master`, then redeploy `master` last. Verify the live taskpane version with the
  console checks in `docs/emr4-development-environment-dummys-guide.md`. The repo
  now has `.github/workflows/pages.yml`; GitHub Pages should use **GitHub Actions**
  as its source so pushes to `master` deploy `docs/` automatically.
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
  (Margaret 09:00 `Confirmed` / 30 min, Billy 09:15 `Booked` / 15 min,
  Margaret 10:00 `Booked` / 45 min) seeded idempotently.
- **Taskpane** — `📅` Diary button in banner controls; `openDiary()` function (no patient guard).
  Cache-bust bumped to `v=28`.

#### Phase 2 parallel-agent integration addendum (2026-06-17)
- **Appointment/security regression tests integrated** from `claude/current`: 21 pytest tests cover auth gates, practice-scoped finalise, appointment conflict validation, adjacent bookings, non-blocking cancelled/no-show/DNA statuses, role gating, and duration-aware `/slots`.
- **Production fixes integrated with the tests**: `_overlaps()` now tolerates mixed naive/tz-aware datetimes; `finalize` returns explicit `JSONResponse` payloads so `_saved` is not stripped by FastAPI's SQLAlchemy-safe encoder; MBS claim creation uses `ClaimStatus.Submitted`.
- **Diary interval rendering integrated** from `antigravity/current`: multi-slot appointments render as interval blocks and later occupied slots no longer show empty chevrons. Diary assets are cache-busted to `v=6`; local browser QA now guards missing `Office.context.ui` outside the Office dialog.
- **Handoff helper fixed**: `scripts/agent_worktrees.py submit` now resolves the active git root from the current working directory, so a worker can submit from its own worktree even if the script path points at another checkout.

#### ✅ Diary Template API (commit 836697a)
- **`GET /api/v1/diary/template`** — authenticated endpoint returning the practice's room/slot configuration as structured JSON compatible with `diary_template.json`.
- **`DiaryTemplate` / `DiaryColumn` / `DiaryBreak` models** (`app/models/diary.py`) + Alembic migration (`a1b2c3d4e5f6`). Practice-scoped, ordered columns, per-column ordered breaks.
- **Fallback**: if the practice has no `DiaryTemplate` DB row, the endpoint reads and returns `diary_template.json` — so the existing diary grid continues working without any frontend change until a practice configures their DB template.
- **Seed**: `seed.py` populates the dev clinic's 3-column template (Room 1 / Dr Shera, Room 2 / Nurse, Room 3 / Available) with MORNING TEA + LUNCH breaks, matching `diary_template.json`.
- **Tests**: 4 tests in `tests/test_diary_template.py` — 401 without auth, DB record returned, JSON fallback, cross-practice isolation. 26/26 total pass.

#### 🧭 Planned Phase 2B — Bernie Receptionist Copilot
- **Bernie** is the planned internal receptionist copilot: a supervised assistant
  embedded in the diary/waiting-room surface, named after Dr Shera's former head
  receptionist.
- First build should be **staff-facing and confirm-before-write**, not autonomous
  patient-facing chat or phone voice. Bernie should propose actions such as finding
  an appropriate slot next week, linking a provisional patient, taking a message,
  or preparing a booking; reception staff confirm mutations.
- Bernie should act through controlled backend tools/API contracts, not by clicking
  around the UI: `search_patient`, `find_slots`, `create_booking`,
  `link_patient_to_booking`, `arrive_patient`, `take_message`,
  `handoff_to_receptionist`, etc.
- From 2026-06-23, new mutating workflows should use the formal
  command/proposal pattern: intent, typed non-mutating proposal, warnings/blocks,
  command payload, confirmation requirement, result report, and audit context.
  The first concrete slice is `POST /api/v1/appointments/proposals/create`,
  which prepares a booking command without writing to the diary.
- Build timing: after Phase 2 diary foundations settle around appointment create/edit,
  bookable resources, provisional vs linked patient identity, breaks, and physical
  waiting-area semantics. Later online chat, kiosk assistance, and phone voice can
  reuse the same tool layer.

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
| `diary_template.json` | Practice diary config (columns, slot defaults, breaks, footer). Embedded verbatim in `diary.js`; fallback source for `GET /api/v1/diary/template` when the practice has no DB row. |
| `app/models/diary.py` | `DiaryTemplate`, `DiaryColumn`, `DiaryBreak` — per-practice diary config models. |
| `app/routers/diary.py` | `GET /api/v1/diary/template` — returns the practice's diary template (DB or JSON fallback). |
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
The read-only first slice plus interval display, backend conflict/slot hardening, and canonical
clinic-local appointment time model are shipped.
Before adding booking/drag/status mutations:

1. ✅ **Independent positioned-column diary grid** — **DONE**. This is the foundation for
   drag/drop, arbitrary appointment lengths, dense overlap lanes, click-to-expand notes,
   and per-column visual flexibility.
2. **`Room` + `DiaryRoster` models** — date×room→practitioner|label + CRUD. `DiaryTemplate` /
   `DiaryColumn` / `DiaryBreak` models now exist (migration `a1b2c3d4e5f6`); room-per-date
   roster assignment is the next modelling step.
3. ✅ **`GET /api/v1/diary/template`** — **DONE** (commit `836697a`). Returns the practice's
   `DiaryTemplate` from DB, falling back to `diary_template.json` if no row exists yet.
   **Next: wire `diary.js` to call this endpoint** instead of embedding the template literal.

#### Diary interaction backlog — preserve flexibility

The diary should remain flexible enough for real reception workflows:
- **Arbitrary appointment durations** — the appointment model/API already allows positive
  `duration_minutes` values up to 480, so 10-minute, 20-minute, 45-minute, etc. bookings
  should remain first-class. Conflict checks and `/slots` are duration-aware. Use **5 minutes**
  as the minimum editing/snap unit unless a stronger clinical reason emerges.
- **Per-column slot cadence** — currently `DiaryTemplate.slot_interval_minutes` is practice-wide,
  while `PractitionerSchedule.slot_duration_minutes` is per practitioner. Add an optional
  per-column interval override to `DiaryColumn` / `DiaryColumnOut` before building the template
  editor, so a nurse column can use 10-minute slots while a GP column uses 15-minute slots.
  Validate configured intervals against the 5-minute minimum and prefer multiples of 5.
- **Dense overlap inspection** — keep click-to-expand appointment cards. The active booking rises
  above overlapping bookings and wraps notes, so staff can inspect a long note without inflating
  the whole day.
- **Visible urgent notes, optional quiet notes** — keep appointment reasons visible when there is
  enough duration/space; later add a separate lower-priority bubble/private note field so routine
  notes do not overload the diary.
- **Lifecycle colour bar** — explore using the left appointment accent bar for status/lifecycle
  states (Booked, Confirmed, Arrived, InConsult, Completed) while preserving appointment-type
  colour somewhere else if needed.
- **Now navigation** — add a header button and initial auto-scroll that positions the day just
  before the current time.

### 🏗️ Later Phase 2 items (deferred)
- **Parse & Lock** — now unnecessary for the diary (the grid replaces it). Still relevant if
  any Word-based annotation workflow needs structure extraction later.
- **Internal messaging router** — models exist (`InternalMessage`); no endpoints yet.
  Messages tab in the diary window is a placeholder.
- **SMS reminders** — ClickSend, 24–48h scheduler, two-way YES/NO webhook.
- **Waiting Room live feed** — `/waiting-room` endpoint exists; Waiting Room tab is placeholder.
- **Lifecycle actions** (Confirm, Arrived, InConsult, Completed) — as clickable status updates
  on diary grid cells. Keyboard shortcuts (Ctrl+Alt+* class) and/or row buttons.
- ✅ **`GET /api/v1/diary/template`** — done. Wire `diary.js` to call it (currently still uses embedded template literal).
- **DiaryRoster** — per-date room→practitioner assignment table + CRUD, as a follow-on to the `DiaryColumn` model now in place.
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
- Diary / GitHub Pages edit → bump `?v=N`, push, then verify the deployed
  `https://yurifrusin.github.io/EMR4/...` HTML is actually serving the new
  cache-bust. If GitHub Pages remains on an old commit, trigger a rebuild:
  `gh api --method POST repos/yurifrusin/EMR4/pages/builds`, then poll the live
  URL until the expected `?v=N` appears.
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

*Last updated: 2026-06-18 - Sprint 3 diary operations foundation integrated in the latest master integration commit. Native Diary Grid now includes a `Now` button, current-time marker, today auto-scroll, exact-time hover bubbles/tooltips for off-grid booking and break borders, and smoke fixtures for irregular times. Backend now has Room + DiaryRoster foundation (`c3d4e5f6a7b8`) for date-specific room assignments. Gemini calls have moved to the Google Gen AI SDK path with lazy client construction to avoid blocking app/test imports. Visible website/app branding now says `EMR`, with `cuboid4.png` used for taskpane, command centre, diary, and Office ribbon icon assets. Verification for the integrated batch: `pytest tests -q` -> 38 passed, `compileall`, `node --check docs\diary\diary.js`, manifest XML parse, `git diff --check`, and local browser branding smoke. Next: review live diary time-ruler UX, then wire the diary frontend to Room/DiaryRoster data before booking drag/drop mutations.*
