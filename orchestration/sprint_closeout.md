# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 30: Cancelled Appointment Review Surface |
| Integrated through | Sprint 30 backend cancelled-appointment review tests and diary cancelled-appointments review UI |
| Status | Integrated locally, verified, and pending push/audit/deploy observation |
| Last updated | 2026-06-25 |

## What Changed

- Backend contract coverage now proves `GET /appointments?status=Cancelled` is authenticated, practice-scoped, excludes active appointments, and returns `cancellation_reason` as either the captured note or `null`.
- Diary patient-flow panel now includes a read-only `Cancelled` section with a count badge.
- Cancelled cards show the appointment reason plus `Reason: <cancellation_reason>` when present.
- Cancelled cards are visually distinct with muted/struck styling and a `CXL` badge.
- Cancelled cards intentionally omit edit buttons, link buttons, status/action buttons, links, and selects, so the review surface cannot mutate appointments.
- Smoke mode includes a cancelled fixture with a cancellation reason for tool-enabled browser review.
- Ariadne applied one bounded integration hotfix after browser smoke: cancelled-card details no longer render `undefined undefined` when a practitioner object lacks first/last names, falling back to AHPRA/Room instead.
- Diary cache bust moved to `diary.css?v=97` and `diary.js?v=98`.
- No restore/reactivation, cancellation editing, audit-history table, taskpane, Command Centre, Resource Administration, drag/resize, recurrence, SMS, or billing work was included.

## Recommended User Review

Residual user review/testing after closeout: none required before pausing.
Ariadne verified the backend contract, frontend syntax/assets, and local browser
smoke path covering cancelled-section visibility, reason display, read-only card
controls, asset versions, and console cleanliness.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=98` and `diary.css?v=97` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary, cancel an appointment with a reason if no cancelled appointment already exists, then open the Waiting Room/patient-flow pane.
3. Expected review surface: a `Cancelled` section appears in the right pane with a count matching the currently selected waiting-area tab.
4. Expected card content: the cancelled appointment shows patient name, time/practitioner or AHPRA fallback, appointment reason, `Reason: <your cancellation reason>`, and a `CXL` badge.
5. Expected read-only behaviour: the cancelled card has no edit pencil, no link button, no check-in/start/complete action, no waiting-area select, and clicking it must not open mutation controls.
6. Suspicious signs: missing `Cancelled` section, missing cancellation reason, `undefined undefined` text, any mutation control on a cancelled card, cancelled rows showing in active diary grid slots, or browser console errors.
7. Skippable parts: do not retest taskpane, Command Centre, Resource Administration, booking create/edit, drag/resize, recurrence, SMS, billing, or patient search for Sprint 30.
8. Evidence to report: screenshot or short note showing the cancelled card, selected waiting-area tab, cancellation reason, and any unexpected control or console error.

## Not Required Before Moving On

- No manual database repair or migration is required; Sprint 30 added tests/UI only.
- No Word taskpane, Command Centre, patient-file, Resource Administration, recurrence, duplicate-audit, billing, or clinical workflow review is required.
- No additional Yuri-only test is required because Ariadne's browser smoke verified the read-only cancelled review surface.
- Per Yuri's instruction, sprint automation should pause after Sprint 30 rather than dispatch Sprint 31 automatically.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- GitHub Pages deployment should be observed after push until live diary assets serve `diary.js?v=98` and `diary.css?v=97`.
- Future cancellation review work may add restore/reactivation or supervisor audit history, but Sprint 30 intentionally stayed read-only.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 30 review packets.
- Claude worker verification rerun by Ariadne: `pytest tests\test_cancelled_appointment_review.py tests\test_appointment_status_mutations.py -q --tb=short -p no:randomly` -> 39 passed, with the existing pytest-asyncio deprecation warning.
- Antigravity worker verification rerun by Ariadne: `node --check docs\diary\diary.js`; `python scripts\check_frontend_versions.py`; `git diff --check` -> passed after Ariadne's cache-bust hotfix.
- Browser smoke: local diary served at `http://127.0.0.1:8765/diary/diary.html?smoke=true`; page loaded `diary.css?v=97` and `diary.js?v=98`, opened Waiting Room/patient-flow pane, showed `Cancelled 1`, rendered `Reason: Patient had transport issues`, rendered no buttons/selects/links inside the cancelled card, and logged no browser console errors.

## Recommended Next Direction

Pause after Sprint 30 as requested. When Yuri resumes, choose the next Programme 2B slice deliberately rather than continuing on heartbeat autopilot.

## Previous Closeout - Sprint 29

| Item | Value |
|---|---|
| Batch | Sprint 29: Appointment Cancellation Reason/Note Capture |
| Integrated through | Sprint 29 backend cancellation reason contract and diary cancellation reason capture flow |
| Status | Integrated, pushed, mirrored, audited, and deployed v96 observed |
| Last updated | 2026-06-25 |

## What Changed

- Backend appointments now persist optional `cancellation_reason` on soft-cancelled appointments through a new nullable migration.
- `DELETE /appointments/{id}` accepts an optional JSON body with `cancellation_reason` capped at 500 characters.
- `POST /appointments/proposals/delete/{appointment_id}` accepts the same body and echoes the reason in the non-mutating delete command payload.
- Appointment output/command schemas include `cancellation_reason`, preserving proposal-first safety while retaining receptionist notes for audit/review surfaces.
- Backend regression coverage now exercises persisted reason, null/no-body reason, proposal echo, and too-long reason validation.
- Diary cancel flow now reveals an optional `CANCELLATION REASON` field after the first `Cancel Appointment` click, focuses it, and keeps the first-click whole-appointment warning.
- The reason is included in both the proposal preflight request and final delete request when live mode is active; smoke mode mirrors the same interaction path.
- Abort/cancel paths hide and clear the reason field, reset the button, and leave the appointment intact.
- Diary frontend asset cache-bust moved to `diary.js?v=96` / `diary.css?v=96`.
- No taskpane, Command Centre, patient workflow, Resource Administration, recurrence, drag/resize, or cancellation-review history surface was included.

## Recommended User Review

Residual user review/testing after closeout: none required before the next sprint.
Ariadne verified the backend contract, frontend syntax/assets, and local
browser smoke paths covering first-click warning, reason reveal/focus, entered
reason, proposal dialog, abort/reset, confirm/save, and appointment removal.
The live GitHub Pages deployment is serving v96 assets; no Yuri-only product
test is required before the next sprint.

Optional confidence check only, if Yuri happens to be in the live diary:

1. Setup: after GitHub Pages deploys, hard refresh the live diary and confirm
   `diary.js?v=96` and `diary.css?v=96` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary,
   and choose a cancellable appointment.
3. First-click guard: open the appointment editor, click `Cancel Appointment`,
   and confirm the button changes to `Confirm Cancel`, the inline warning says
   the whole appointment will be cancelled, and a `Cancellation reason
   (optional)` field appears with focus.
4. Reason entry: type a short reason such as `Patient rang to cancel`.
5. Proposal guard: click `Confirm Cancel` and confirm a proposal dialog appears
   before any mutation; for waiting-room appointments it should warn that the
   patient will be removed from the waiting area.
6. Abort result: click `Cancel` in the proposal dialog; the appointment should
   remain present, the modal should stay usable, and the cancel button/reason
   field should reset rather than leaving a stuck confirmation state.
7. Confirm result: repeat the cancel path with a reason and click
   `Confirm & Save`; the modal should close, the appointment should be
   cancelled/removed from active diary display, and the Waiting Room pane should
   not retain a stranded patient.
8. Suspicious signs: appointment disappears before the proposal dialog, reason
   field does not appear/focus, abort leaves stale reason text, `Cancel` still
   mutates data, the confirm button stays stuck after abort, or the console
   shows errors.
9. Skippable parts: do not retest taskpane, Command Centre, Resource
   Administration, room/waiting-area admin, drag/resize, recurrence, or patient
   search for Sprint 29.
10. Evidence to report: screenshot or short note with the appointment, status,
    cancellation reason text, action attempted, and any unexpected dialog or
    console error.

## Not Required Before Moving On

- No manual database repair is required; the Sprint 29 migration is additive and nullable.
- No Word taskpane, Command Centre, patient-file, Resource Administration,
  room/waiting-area admin, recurrence, duplicate-audit, or clinical workflow
  review is required for this sprint.
- No additional Yuri-only test is required because Ariadne's Chrome/CDP smoke
  covered the warning, reason reveal/focus, abort/reset, proposal, confirm, and
  removal path.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- GitHub Pages is serving v96; no deployment propagation follow-up remains for Sprint 29.
- A later cancellation-polish sprint may add a proposal/review history surface
  that displays stored cancellation reasons to supervisors or audit users.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 29 review packets.
- Claude worker verification, rerun by Ariadne with the integration venv: `alembic upgrade head`; `py_compile app\models\appointments.py app\schemas\appointments.py app\routers\appointments.py`; `pytest tests\test_appointment_status_mutations.py -q --tb=short -p no:randomly`; `git diff --check` -> 34 passed.
- Antigravity worker verification, rerun by Ariadne: `node --check docs\diary\diary.js`; `git diff --check` -> passed.
- Integrated-tree backend verification: `alembic upgrade head`, `py_compile app\models\appointments.py app\schemas\appointments.py app\routers\appointments.py`, and `pytest tests\test_appointment_status_mutations.py -q --tb=short -p no:randomly` -> 34 passed, with the existing pytest-asyncio deprecation warning.
- Integrated-tree frontend verification: `node --check docs\diary\diary.js`, `python scripts\check_frontend_versions.py`, and `git diff --check` -> passed; local/head diary v96 and deployed v95 before push.
- Browser smoke: local diary served at `http://127.0.0.1:8765/diary/diary.html?smoke=true`; page identity `EMR - Diary`, 4 smoke appointments, booking modal opened from a visible appointment.
- Browser cancellation-reason smoke: first click revealed the reason field, focused it, changed the button to `Confirm Cancel`, and showed the whole-appointment warning.
- Browser confirm smoke: entering `Patient rang to cancel`, then confirming through the proposal dialog, closed the modal and removed the appointment from the active smoke diary.
- Browser abort smoke: entering a reason, opening the proposal dialog, then clicking dialog `Cancel` left the appointment intact, reset `Cancel Appointment`, hid the reason field, and cleared the stale reason text.

## Recommended Next Direction

1. Continue Programme 2B with the next receptionist-visible appointment mutation slice if no Yuri-only checks remain.
2. Keep using browser/CDP smoke before leaving any UI review to Yuri; Sprint 29 confirms cancellation reason capture can be verified tool-first.

## Previous Closeout - Sprint 28

| Item | Value |
|---|---|
| Batch | Sprint 28: Cancellation/Delete Proposal Safety |
| Integrated through | Sprint 28 backend cancel/delete proposal contract and diary cancel proposal preflight flow |
| Status | Integrated, pushed, mirrored, audited, and deployed v95 observed |
| Last updated | 2026-06-25 |

## Previous Closeout - Sprint 27

| Item | Value |
|---|---|
| Batch | Sprint 27: Visible Diary Mouse Drag/Resize Affordances |
| Integrated through | Sprint 27 backend mouse-equivalent update conflict tests and diary mouse drag/resize proposal flow |
| Status | Integrated locally; verification complete; pending push/audit/deploy observation |
| Last updated | 2026-06-25 |

## What Changed

- Backend conflict coverage now proves confirmed `PUT /appointments/{id}` rejects mouse-equivalent drag move, resize into a next booking, and cross-practitioner conflict writes while allowing adjacent moves.
- Diary appointment cards now expose visible mouse affordances: grab cursor on cards, top/bottom resize handles, dashed ghost preview, 15-minute snapping, cross-column drag target detection, and proposal-gated drop handling.
- Mouse move/resize reuses the same non-mutating update-proposal preflight path as keyboard move/resize: blocked proposals stop writes, warning proposals require `Confirm & Save`, and confirmed changes then use the normal appointment update path.
- Ariadne applied two bounded integration hotfixes from tool-enabled review: delayed ghost creation until the pointer moves beyond a 3px threshold, and restored the Resource Administration access-denied paragraph font size accidentally dropped in the worker CSS diff.
- Diary frontend asset cache-bust moved to `diary.js?v=94` / `diary.css?v=94`.
- No schema migration, taskpane, Command Centre, patient workflow, Waiting Room, Resource Administration behaviour, recurrence, or direct-write bypass was included.

## Recommended User Review

Residual user review/testing after closeout: none required before the next sprint.
Ariadne verified the mouse interaction paths locally with browser/CDP against the
smoke diary fixture, including real browser mouse events for drag preview,
warning proposal, confirm-save, resize preview, and confirm-save. Backend conflict
coverage provides the blocked-conflict safety check for the confirmed write path.

Optional confidence check only, if Yuri happens to be in the live diary:

1. Setup: after GitHub Pages deploys, hard refresh the live diary and confirm
   `diary.js?v=94` and `diary.css?v=94` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary,
   and hover over an appointment card body/name area.
3. Expected drag affordance: the cursor should read as draggable/grabbable, a
   dashed preview should appear while dragging more than a tiny click movement,
   and releasing on a warning-only move should show the existing proposal
   warning before any save.
4. Expected resize affordance: drag the bottom edge of a card; a dashed preview
   should resize in 15-minute increments and the proposal warning/confirm path
   should appear before the duration changes.
5. Suspicious signs: card moves without a proposal check, a click opens a drag
   preview without meaningful movement, resize shrinks below 15 minutes, the
   status dropdown changes when dragging the card body, or the browser console
   shows errors.
6. Skippable parts: do not retest taskpane, Command Centre, Resource
   Administration, Waiting Room, recurrence, or patient search for Sprint 27.
7. Evidence to report: screenshot or short note with the appointment, action
   attempted, expected time/duration, and any unexpected dialog or console error.

## Not Required Before Moving On

- No database migration or manual data repair is required.
- No Word taskpane, Command Centre, patient-file, Resource Administration,
  Waiting Room, recurrence, duplicate-audit, or clinical workflow review is
  required for this sprint.
- No additional Yuri-only test is required because browser/CDP covered the
  real mouse-input paths that were previously hard for Ariadne to synthesize.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The live GitHub Pages deployment must still be observed after push to confirm
  Pages serves v94; this is a deployment observation, not a manual product test.
- Future UX polish may add a short in-product hint for mouse/keyboard move and
  resize controls once staff workflow feedback accumulates.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 27 review packets.
- Claude worker verification: `pytest tests/test_appointment_conflicts.py -q --tb=short -p no:randomly` on `claude/current` -> 12 passed.
- Antigravity worker verification: `node --check docs\diary\diary.js`, `git diff --check origin/master...HEAD`, and `npm run validate-all` -> passed.
- Integrated-tree backend verification: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_conflicts.py tests\test_appointment_update_proposal.py -q --tb=short -p no:randomly` -> 43 passed, with the existing pytest-asyncio deprecation warning.
- Integrated-tree frontend verification: `node --check docs\diary\diary.js`, `git diff --check`, and `npm run validate-all` -> passed; manifest valid, production npm audit clean, and asset check accepted v94.
- Browser smoke: local diary served at `http://127.0.0.1:8765/diary/diary.html?smoke=true`; page identity `EMR — Diary`, grid rendered 4 smoke appointments, no console warnings/errors.
- Browser/CDP drag smoke: real mouse events on a visible appointment created one dashed ghost preview, snapped the preview down by one slot, opened the proposal warning dialog, and `Confirm & Save` moved the card from `top: 331px` to `top: 361px`.
- Browser/CDP resize smoke: real mouse events on the bottom resize handle created one dashed ghost preview with increased height, opened the proposal warning dialog, and `Confirm & Save` persisted the card height to `88px`.
- Browser smoke confirmed status controls were ignored as drag targets and that ghost previews were removed after drop.

## Recommended Next Direction

1. Push Sprint 27, observe GitHub Pages serving v94, realign mirrors, and audit.
2. Continue Programme 2B with the next receptionist-visible appointment mutation slice: likely cancellation/reschedule reason capture or an appointment proposal/review history surface.
3. Keep running browser/CDP smoke before leaving any UI review to Yuri; this sprint proved the tool path can cover real mouse-input affordances.

## Previous Closeout - Sprint 26

| Item | Value |
|---|---|
| Batch | Sprint 26: Move/Resize Proposal Flow |
| Integrated through | Sprint 26 backend move/resize proposal tests and diary keyboard move/resize proposal flow |
| Status | Integrated, pushed, mirrored, audited, deployed v92 observed, and Yuri physical-keyboard smoke passed |
| Last updated | 2026-06-25 |

## What Changed

- Backend proposal coverage now includes four diary move/resize scenarios for `POST /appointments/proposals/update/{appointment_id}`: resize into next booking blocked, move across practitioner columns into a conflict blocked, adjacent slots safe, and resize-shrink safe.
- The backend proposal route itself was unchanged; the sprint hardens tests around the existing non-mutating contract.
- Diary appointment cards now support proposal-gated keyboard move/resize intent: `Alt+ArrowUp/Down` shifts start time by 15 minutes and `Alt+ArrowLeft/Right` adjusts duration by 15 minutes with a 15-minute floor.
- Move/resize proposal handling uses the existing blocked/warning dialog path before any write, then applies safe/confirmed updates through the normal appointment update path.
- Ariadne hotfixed smoke/runtime gaps found during tool-enabled review: practitioner ID fallback for visible resource columns, diary-date fallback for smoke appointments without `appointment_date`, smoke-cache persistence before reload, existing active-card restoration helper reuse, and capture/nested status-control key routing.
- Diary frontend asset cache-bust moved to `diary.js?v=92` / `diary.css?v=92`.
- No schema migration, taskpane, Command Centre, patient demographics, Resource Administration, Waiting Room layout, recurrence, or visual drag-handle work was included.

## Recommended User Review

Residual user review/testing after push/deploy: complete. Yuri confirmed the
live physical-keyboard shortcut smoke passed after Pages served v92. Ariadne
verified the backend contract, frontend syntax/assets, and local smoke rendering;
the remaining real OS/browser `Alt+Arrow` path was confirmed manually.

Completed Yuri-only check:

1. Setup: open the live diary after deployment and hard refresh. Confirm the
   live page serves `diary.js?v=92` and `diary.css?v=92`.
2. Exact UI path: sign in as a normal dev user or admin, open the Diary, click
   once on an appointment card body/name area rather than the status dropdown.
3. Expected move result: press `Alt+ArrowDown`; if the target slot is safe or
   warning-only, the existing proposal dialog should appear before mutation.
   Cancel should leave the card unchanged; Confirm should move it down by 15
   minutes and keep the card selected/highlighted after reload.
4. Expected block result: choose or create an appointment where a 15-minute move
   or duration increase would overlap another booking, then press the relevant
   shortcut. The dialog should say `Action Blocked`; closing it should leave the
   appointment unchanged.
5. Expected resize result: press `Alt+ArrowRight` on a safe appointment to
   increase duration by 15 minutes, and `Alt+ArrowLeft` to shrink duration. It
   should never shrink below 15 minutes.
6. Suspicious signs: the browser navigates back/forward, the inline status
   dropdown changes instead of move/resize, no proposal dialog appears before a
   risky write, the card moves without confirmation when warnings/blocks exist,
   or the active highlight is lost after reload.
7. Skippable parts: do not test Resource Administration, taskpane, Command
   Centre, patient-file generation, recurrence, or drag-handle UX for Sprint 26.
8. Evidence to report: screenshot of any unexpected dialog/state plus the exact
   card, shortcut pressed, and before/after time/duration.

## Not Required Before Moving On

- No database migration or manual data repair is required.
- No Word taskpane, Command Centre, patient-file, Resource Administration,
  recurrence, duplicate-audit, or clinical workflow review is required for this
  sprint.
- No security or dependency remediation is required; production
  `npm audit --omit=dev` remains clean and Bandit medium+/high checks passed.

## Known Follow-Up

- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The existing GitHub Dependabot moderate alert remains visible on push; it is
  the already-known security queue item and not a Sprint 26 blocker.
- A future UX sprint should consider visible move/resize affordances or a help
  hint for keyboard shortcuts; Sprint 26 intentionally kept the UI slice small.

## Verification

- `.\scripts\check_backend.ps1` -> passed; compileall, Bandit medium+/high scan, and whitespace check all green.
- `.\.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py` -> passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_appointment_update_proposal.py -q --tb=short -p no:randomly` -> passed; 31 passed, 1 existing pytest-asyncio deprecation warning.
- `node --check docs\diary\diary.js` -> passed.
- `npm run validate-all` before Ariadne hotfixes -> passed; manifest valid, production npm audit clean, frontend asset/version check passed. Worker-local diary assets were v87 and deployed Pages was still v86 before push.
- `npm run validate-all` after Ariadne hotfixes -> passed; local diary assets are v92, HEAD before closeout was v87, deployed Pages before push was still v86.
- `npm run check-assets` after push/mirror realignment -> passed; deployed GitHub Pages diary assets now report `diary.js?v=92` and `diary.css?v=92`.
- `git diff --check` -> passed.
- Local browser smoke page loaded via `http://127.0.0.1:8787/diary/diary.html?smoke=true` and confirmed `diary.js?v=92` is requested.
- Browser smoke found and Ariadne fixed two move/resize smoke data issues and one nested status-control key-routing issue before final verification.
- Browser automation could not conclusively synthesize a physical `Alt+Arrow`
  chord; the residual Yuri-only test above covers that specific real-keyboard path.

## Recommended Next Direction

1. Complete the short v92 physical-keyboard live diary smoke above.
2. If it passes, continue Programme 2B with the next appointment mutation affordance slice: a clearer visible move/resize UX or a proposal review/history surface, depending on which feels most useful after the keyboard smoke.
3. Keep using browser/Chrome smoke checks before leaving any UI review to Yuri.

## Previous Closeout - Sprint 25

## Previous Closeout - Sprint 23

| Item | Value |
|---|---|
| Batch | Sprint 23: Room Default Waiting-Area Invariant |
| Integrated through | Sprint 23 waiting-area invariant integration |
| Status | Integrated, pushed, mirrored, audited, and awaiting optional live Admin smoke |
| Last updated | 2026-06-24 |

## What Changed

- Backend resource-admin room writes now enforce the active-room default waiting-area invariant where possible: room creation auto-selects the lowest-order compatible active waiting area, explicit null on active rooms resolves to a fallback, and reactivating a room fills a fallback.
- Archiving a waiting area now reassigns active rooms that used it to the next compatible active fallback, or clears the default only when no compatible active waiting area remains.
- Resource Administration room cards now show explicit/fallback default waiting-area labels, room forms preselect active defaults/fallbacks, and smoke-mode waiting-area archive behavior mirrors reassignment.
- Diary frontend asset cache-bust moved to `diary.js?v=84` / `diary.css?v=84`.
- No schema migration, taskpane, Command Centre, patient, appointment booking, or clinical-document changes were made.

## Recommended User Review

Residual user review/testing after push/deploy: one short live diary smoke is
useful because this sprint changes the Resource Administration UI and the real
Office dialog/GitHub Pages surface can reveal deployment or browser-state issues
that static checks cannot. Confirm `diary.js?v=84` is loaded, open Admin ->
Resource Administration, and check that room default waiting areas are visible,
preselected in the room form, and remain coherent after archiving a waiting area.

Detailed steps for Yuri-only review:

1. Hard refresh the live diary/Office-dialog surface and confirm `diary.js?v=84`
   and `diary.css?v=84` are loaded.
2. Sign in as an Admin or PracticeOwner-capable user.
3. Open `⚙️ Admin` -> `Resource Administration` -> `Rooms`.
4. Confirm every active room card displays an explicit or fallback default
   waiting area when active waiting areas exist.
5. Edit one room, confirm the default waiting-area dropdown is preselected, then
   cancel and confirm no state changed.
6. Edit the same room again, change the default waiting area, save, close and
   reopen Resource Administration, and confirm the saved default persists.
7. Open `Waiting Areas`, archive a non-critical active waiting area, and confirm
   affected rooms now show another compatible active fallback or no default only
   when no active fallback exists.
8. Reopen the right-side Waiting Room pane and confirm its tabs match active
   waiting areas and exclude archived areas.
9. Skip non-admin denial if the taskpane cannot be resized or logged out safely;
   report that as an accessibility blocker rather than spending time fighting
   the UI.
10. Report whether v84 loaded, whether defaults displayed/preselected correctly,
   whether archive reassignment looked coherent, and screenshots for anything
   suspicious.

## Not Required Before Moving On

- No database migration or manual data repair is required for dev data; existing null active-room defaults are repaired on create/update/archive paths where compatible active areas exist.
- No Word taskpane, Command Centre, patient-file, appointment create/edit, status, duplicate-audit, or clinical workflow review is required for this sprint.
- No security or dependency remediation is required; production `npm audit --omit=dev` remains clean and Bandit medium+/high checks passed.

## Known Follow-Up

- The frontend fallback helper operates over the waiting areas currently loaded for the active location. The backend invariant is authoritative and includes compatible practice-wide areas; consider a later UI/API refinement if practice-wide waiting areas become a real configuration path.
- The broad `python -m pytest tests/` run timed out during Ariadne verification without a failure report. Sprint-targeted resource-admin/waiting-room tests passed; investigate broad-suite runtime/hanging separately rather than blocking this narrow integration.
- Taskpane logout is currently hard to reach when the pane cannot be widened:
  Yuri could not test non-admin Resource Administration denial because the
  logout button sits at the extreme right and the resize affordance was blocked
  by an hourglass cursor. Add a future UI/accessibility task to make logout and
  role-switching reachable without relying on taskpane width.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.

## Verification

- `.\scripts\check_backend.ps1` -> passed; compileall, Bandit medium+/high scan, and whitespace check all green.
- `.venv\Scripts\python.exe -m pytest tests\test_diary_resource_admin.py tests\test_waiting_room.py -q --tb=short -p no:randomly` -> passed; 61 passed, 1 existing pytest-asyncio deprecation warning.
- `node --check docs\diary\diary.js` -> passed.
- `npm run validate-all` in `EMR4 Sidebar` -> passed; manifest valid, production npm audit clean, frontend asset/version check passed. Local/HEAD diary assets are v84; deployed Pages was still v83 before push.
- `git diff --check` -> passed.
- Worker-reported full backend suite on Claude branch passed before integration; Ariadne's post-merge broad full-suite attempt timed out without a failure report and is recorded as a follow-up rather than a blocker.

## Recommended Next Direction

1. After Pages serves v84, run the short live Admin smoke above; if clean, proceed to the next product-growth sprint.
2. Plan the next architecture/dev-tooling optimisation sprint around automating the browser smoke checks Ariadne has been doing manually.
3. Keep the room/waiting-area model steady: every active room should have an active default area where possible, with display-order-zero as the natural fallback.

## Sprint 15 Review Harness - Waiting Room Check-In Operations

Use this section after the Sprint 15 backend and diary UI worker branches are
reviewed and integrated. It is a user-review harness, not evidence that the
implementation has already landed.

### Design Guardrails

- A **Waiting Area** is a named physical place where arrived patients wait.
- A **Room** is a physical consult/procedure room. It may have a default waiting
  area, but it is not itself a waiting area.
- A **Practitioner** is the bookable clinician/resource for the appointment.
- **Attendance status** is same-day workflow: Booked, Arrived/Waiting,
  InConsult, Completed, Cancelled, NoShow, or DNA.
- **Booking confirmation** is the patient's intention/response to attend and is
  separate from attendance status.
- **Patient identity** should be described as **Verified** or **Unverified**.
  Do not use "Confirmed" for identity; reserve it for booking attendance intent
  or legacy appointment status only when clearly qualified.
- Bernie may execute deterministic, low-risk operational actions with audit and
  reporting, such as an unambiguous check-in/status correction. Slot selection,
  booking choice, rescheduling, externally consequential actions, clinical
  actions, and ambiguous identity cases still require staff confirmation.
- Any future request for "stacking" must specify the surface:
  **Waiting Room cards** inside the side panel, or **diary appointment blocks**
  on the room/time grid. These are different layout problems and should not be
  changed together by default.

### Manual User Review Checklist

1. Pull latest, restart the backend, rerun `python seed.py`, and hard refresh
   the deployed/local diary surface. Confirm the diary loads `diary.js?v=68`.
2. Open today's diary and the Waiting Room panel. Confirm Expected Today cards
   are compact, chronological by appointment time, and readable without looking
   like the main diary grid's overlapping appointment blocks.
3. Confirm ordinary diary appointment blocks on the room/time grid still use
   their existing time geometry. The Sprint 15 Waiting Room work must not
   introduce appointment-block stacking/cascade changes in the main diary grid.
4. Check in an appointment from Expected Today without manually selecting a
   waiting area when the appointment's room has a default. Confirm the patient
   appears in the correct/default Waiting Area section and the appointment
   detail shows that area consistently.
5. Check in an appointment while explicitly selecting a non-default waiting
   area. Confirm the explicit choice wins over the room default and survives a
   refresh.
6. If the UI supports changing the waiting area after arrival, move an arrived
   patient to another waiting area. Confirm the patient moves sections without
   changing practitioner, room, appointment time, or patient identity state.
7. Move a checked-in patient through Waiting/Arrived -> InConsult -> Completed.
   Confirm Waiting Room sections update immediately and after refresh:
   Waiting/Arrived patients are active in their area, InConsult patients appear
   only in the in-consult section, and Completed patients appear only in the
   finished/terminal section if that section is displayed.
8. Set terminal statuses Cancelled, NoShow, and DNA on appointments that had a
   waiting area. Confirm they do not remain incorrectly visible in active
   Waiting Area sections. If the backend preserves `waiting_area_id` for
   history, the active UI must still filter terminal statuses out of active
   waiting lists.
9. Test a practice/day with exactly one active waiting area. Confirm the UI does
   not show a clipped, fake, or confusing tab strip; the single area should read
   as the natural context rather than a broken multi-tab control.
10. Test an Unverified/provisional appointment if available. Check-in may be
    allowed, but the UI should not imply that arrival verified the patient
    identity. The displayed language should keep identity verification separate
    from attendance.

### Backend / API Spot Checks

Use these only after getting a staff JWT and real IDs from the dev database or
browser network panel. Route names may need the `/api/v1` prefix depending on
the caller base URL.

```powershell
$base = "http://localhost:8001/api/v1"
$headers = @{ Authorization = "Bearer <JWT>" }
$appointmentId = "<appointment-uuid>"
$waitingAreaId = "<waiting-area-uuid>"

# Explicit check-in to a waiting area.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived"; waiting_area_id = $waitingAreaId } | ConvertTo-Json)

# Default/no explicit waiting area path. Verify this follows the integrated
# backend contract: either room default assignment or existing assignment
# preservation, as specified by the Sprint 15 backend worker.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Arrived" } | ConvertTo-Json)

# Terminal status should not leave the patient visible in active waiting areas.
Invoke-RestMethod -Method Patch `
  -Uri "$base/appointments/$appointmentId/status" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ status = "Completed"; waiting_area_id = $null } | ConvertTo-Json)
```

API review expectations:

- Cross-practice or inactive `waiting_area_id` values are rejected.
- Explicit `waiting_area_id = null` clears the appointment's waiting area when
  the contract allows clearing.
- Moving to InConsult, Completed, Cancelled, NoShow, or DNA does not strand the
  patient in active waiting-area feeds.
- Status transitions do not link a provisional patient to a real patient record,
  do not change booking confirmation state, and do not alter practitioner/room
  assignment unless a separate explicit endpoint says so.

### Sprint 15 Review Questions For Codex/Orchestrator

- Did Claude's backend branch make terminal-status clearing explicit, or does it
  preserve `waiting_area_id` for history while filtering in the waiting-room
  endpoint/UI?
- Did Antigravity keep Expected Today compacting scoped to Waiting Room cards
  only, with no diary-grid appointment geometry changes?
- Does the single-waiting-area state read naturally, or should the next UI slice
  replace tabs with a simple heading/count when only one active area exists?
- Are there audit hooks yet for Bernie-style direct check-in/status execution?
  If not, keep Bernie write tools at proposal/report level or limit execution to
  the already validated route behaviour.

---

## Sprint 16 Review Harness - Location-Aware Diary Foundations

Use `orchestration/location_diary_view_review.md` after the Sprint 16 backend
and diary UI worker branches are reviewed and integrated. This closeout pointer
is intentionally brief; the harness file owns the vocabulary table, backend
integration review, diary UI review, Bernie tool vocabulary, manual user review,
API spot checks, and merge gate.

Codex/orchestrator should specifically report whether:

- Backend location scoping keeps practice tenancy separate from physical
  location scoping.
- Rooms, waiting areas, diary templates, rosters, and appointments are
  associated with a physical location or have a deliberate safe fallback.
- The diary UI exposes the active physical location when there is more than one
  site, while the one-location case stays uncluttered.
- Diary page/view groups are treated as screen layout inside a location, not as
  extra locations.
- Waiting Room panels/cards, main diary appointment blocks, booking slots, and
  status controls remain separate review surfaces.
- Bernie tool language requires explicit location/resource context before any
  future write proposal.

---

## Sprint 17 Review Harness - Command/Proposal Workflow Retrofit

Use `orchestration/command_proposal_review.md` after the Sprint 17 backend and
diary UI worker branches are reviewed and integrated. This closeout pointer is
intentionally brief; the harness file owns the command/proposal vocabulary,
integration checklist, expected response classes, and PowerShell snippets.

Codex/orchestrator should specifically report whether:

- Proposal endpoints are non-mutating and return typed commands for staff
  confirmation.
- Safe create proposals still require staff confirmation before the diary is
  written.
- Conflict proposals return `safe=false`, `autonomy_tier=blocked`, and a stable
  `appointment_conflict` block without creating an appointment.
- Break overlaps and provisional patients return warnings, not blocks, and stay
  confirmable by staff.
- The diary UI treats blocked proposals as hard stops and warning proposals as
  explicit confirmation paths.
- Booking slots, diary grid cells, Waiting Room cards, appointment status, and
  patient identity are described as separate surfaces.
- No Sprint 17 work starts a Bernie runtime, bypasses normal appointment route
  validation, or creates a privileged agent-only write path.

### Sprint 17 Integrated Outcome

Integrated submissions:

- Claude: existing-appointment update/status proposal contracts.
- Antigravity: diary new-booking modal create-proposal preflight.
- Codex/Banach: command proposal review harness and API snippets.

Verification run after integration:

```powershell
.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py
node --check docs\diary\diary.js
.venv\Scripts\python.exe -m pytest tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py tests\test_appointment_status_mutations.py tests\test_booking_create_edit.py tests\test_break_overlap_contract.py -q --tb=short -p no:randomly
git diff --check
```

Result: `75 passed`; JS syntax and whitespace checks clean.

Manual user review:

- Confirm diary assets load at `diary.js?v=72`.
- Create a normal non-conflicting booking and confirm it saves.
- Try an overlapping booking and confirm the modal blocks the save before writing.
- Create a booking that crosses a break and confirm the warning appears, then `Confirm & Save` writes it.
- Create a provisional-patient booking and confirm the warning appears, then `Confirm & Save` writes it.
- Confirm the proposal warning/error copy is readable in the booking modal and does not disturb the main diary grid or Waiting Room panel.

User review result: positive after hotfix `d081834`; break-crossing warning now appears for the visible break path.
