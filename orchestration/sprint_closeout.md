# EMR4 Sprint Closeout

This file tracks what the user should review after each integrated sprint batch
of parallel-agent work. Codex updates it after submitted work has been polled,
reviewed, integrated, verified, pushed, and audited.

## Current Closeout

| Item | Value |
|---|---|
| Batch | Sprint 50: Bernie Supervised Review Live Adapter |
| Integrated through | Smoke/feature-gated adapter from supervised-booking `staff_review` response into the diary Bernie review panel |
| Status | Integrated locally; pending push, mirror realignment, and final audit |
| Last updated | 2026-06-27 |

## What Changed

- Extended the smoke-gated diary Bernie review panel with `bernie_review=live` adapter mode.
- In smoke/live-adapter mode, the diary client posts deterministic dev input to `/api/v1/appointments/proposals/bernie/supervised-booking` and renders the returned `staff_review` payload.
- Preserved all Sprint 49 fixture modes for `blocked`, `candidate_selection_required`, and `confirmation_ready`.
- Kept real confirmation out of scope: the confirm button still simulates local approval only and does not post to confirm-Bernie.
- Added route-intercepted Playwright checks for live-adapter blocked, candidate-selection, and confirmation-ready responses.
- Added a deterministic guard that fails if the UI tries to call `/api/v1/appointments/proposals/create/confirm-bernie` during this sprint.
- Bumped diary JS to `diary.js?v=106`; diary CSS remains `v=100`.
- Antigravity implemented the live adapter on `antigravity/current`.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified this as a smoke/feature-gated UI adapter with route-intercepted deterministic Playwright tests. It is not active in the normal live diary without `smoke=true&bernie_review=live`, so there is no live staff workflow for Yuri to manually review yet.

## Not Required Before Moving On

- No manual live API test is required; tests intercept the supervised-booking endpoint and prove the UI consumes the expected response shape.
- No manual live UI review is required; the adapter is smoke/feature-gated and covered by deterministic Playwright checks.
- No database migration, data repair, GCP/Gemini, Word taskpane, Command Centre, live diary booking workflow, resource admin, billing, SMS, or security-console action is required.
- No user decision is needed before the next narrow Bernie slice.

## Known Follow-Up

- The next Bernie slice can introduce a deliberately gated staff confirmation submit path, but it must keep `confirmed=false` until explicit approval and should use route-intercepted tests before any live manual review.
- A later product decision is still needed before enabling the Bernie review adapter in ordinary non-smoke diary mode.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert remains outside this sprint.

## Verification

- Ariadne inspected the Antigravity diff against `origin/master`; scope was limited to diary smoke/live-adapter JavaScript, deterministic review harness tests, and orchestration packets.
- `node --check docs\diary\diary.js` -> passed.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed; local/HEAD diary assets are `diary.css?v=100` and `diary.js?v=106`, deployed Pages still showed `diary.js?v=105` before push.
- `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 26 passed.
- Source/diff review confirmed the adapter posts only to supervised-booking under `smoke=true&bernie_review=live`.
- Route-intercepted Playwright checks prove live-adapter rendering for blocked, candidate-selection, and confirmation-ready payloads.
- The confirmation-ready test registers a failing route for `/api/v1/appointments/proposals/create/confirm-bernie`, proving the smoke adapter does not call the write endpoint.
- `git diff --check origin/master...origin/antigravity/current` -> passed.
- `pytest_asyncio` emitted the existing fixture-loop-scope deprecation warning only.

## Recommended Next Direction

After push/mirror/audit, the next useful slice is a supervised confirmation-submit adapter behind the same gate, still with route-intercepted tests and no normal-mode exposure until explicitly approved.


## Previous Closeout - Sprint 49

Sprint 49 added a smoke-gated diary Bernie Booking Review panel and deterministic Playwright checks.

- Added the review panel markup, styling, and fixture rendering for Sprint 48-style `staff_review` payloads.
- Covered `blocked`, `candidate_selection_required`, and `confirmation_ready` review states.
- Confirmation-ready smoke rendering required explicit simulated approval before enabling the confirm button.
- The smoke confirmation path stayed local to the browser fixture and called no live API write path.
- Added stable `data-testid` selectors and default hidden-panel checks.
- Bumped diary assets to `diary.css?v=100` and `diary.js?v=105`.
- Antigravity implemented the UI harness on `antigravity/current`.

Residual user review/testing after Sprint 49 closeout: none required. Ariadne verified it as a smoke-only UI review harness with deterministic Playwright tests.

## Previous Closeout - Sprint 48

Sprint 48 added the additive deterministic `staff_review` payload to the supervised Bernie wrapper response.

- Added `BernieStaffReviewPayload` and `BernieStaffReviewSlotSummary` response schemas.
- Added stable review fields for headline/status, staff action required, confirmation readiness, selected slot summary, candidate slot summaries, warning/block summaries, confirm endpoint, confirm payload, and bounded confirm evidence.
- Preserved existing wrapper `result` discriminators: `blocked`, `candidate_selection_required`, and `confirmation_ready`.
- Kept `staff_review.confirm_payload.confirmed` intentionally false so later UI must require explicit staff approval before posting it.
- Cicero/Boole implemented the backend contract sprint on `codex/bernie-supervised-review-payload`.

Residual user review/testing after Sprint 48 closeout: none required. Ariadne verified it as a backend-only additive API contract with focused and adjacent pytest coverage.

## Previous Closeout - Sprint 47

Sprint 47 added the deterministic backend harness proving the supervised Bernie wrapper's `confirmation_ready` evidence can be explicitly confirmed through the existing confirm-Bernie endpoint, while blocked, stale, candidate-only, and `confirmed=false` paths remain non-mutating.

- Added `tests/test_bernie_wrapper_confirmation_review_harness.py`.
- The success path requires `confirmed=true` and writes exactly one appointment plus exactly one bounded audit evidence trail.
- The negative paths write no appointment rows and no appointment audit rows.
- The harness blocks Gemini/LLM/provider access during the flow.
- Cicero/Feynman implemented the test-only sprint on `codex/bernie-wrapper-confirmation-review-harness`.

Residual user review/testing after Sprint 47 closeout: none required. Ariadne verified it as a backend-only deterministic review harness with focused and adjacent pytest coverage.

## Previous Closeout - Sprint 46

Sprint 46 added the backend-only supervised wrapper for deterministic Bernie booking intake: normalize -> slot search -> slot selection/create-proposal evidence, without writing appointments, writing audit rows, calling confirmation, or invoking Gemini/LLM providers.

- Added authenticated `POST /api/v1/appointments/proposals/bernie/supervised-booking`.
- Added `BernieSupervisedBookingIn` and `BernieSupervisedBookingOut` schemas.
- The wrapper accepts typed deterministic Bernie booking command input plus optional supervised selected-slot context.
- It returns a stable `result` discriminator with `blocked`, `candidate_selection_required`, or `confirmation_ready`.
- It composes existing deterministic command normalization, slot-search proposal, slot-selection, and create-proposal evidence paths.
- Added `tests/test_bernie_supervised_booking_wrapper.py` covering auth, practice scoping, blocked normalization, candidate-selection response, selected-slot confirmation-ready evidence, conflict revalidation, non-mutation row counts, and no-LLM/no-write source proof.
- Cicero/Archimedes implemented the backend-only sprint on `codex/bernie-supervised-booking-wrapper`.

Residual user review/testing after Sprint 46 closeout: none required. Ariadne verified it as a backend-only API contract with focused and adjacent pytest coverage.

## Previous Closeout - Sprint 45

Sprint 45 added the deterministic backend harness proving the full supervised Bernie normalize -> normalized search -> slot selection -> explicit confirmation chain remains no-write/no-LLM until explicit confirmation, then writes exactly one appointment and bounded audit evidence on success.

- Added `tests/test_bernie_confirmed_flow_review_harness.py`.
- The harness exercises the full supervised Bernie backend chain: deterministic command normalization, normalized slot search, supervised slot selection/create-proposal evidence, and explicit confirm-write.
- It proves normalize/search/select steps write no appointment rows and no appointment audit rows.
- It proves `confirmed=false` and stale-conflict confirmation paths write no appointment/audit rows.
- It proves successful explicit confirmation writes exactly one appointment and exactly one bounded audit evidence trail.
- It guards the flow against Gemini/LLM/provider calls and autonomous natural-language execution.
- Cicero/Euclid implemented the test-only sprint on `codex/bernie-confirmed-flow-review-harness`.
- No production code, diary UI, taskpane, Command Centre, live Bernie runtime, Gemini parsing, autonomous booking behavior, billing, SMS, resource admin, or migration changed.

Residual user review/testing after Sprint 45 closeout: none required. Ariadne verified it as a deterministic backend review-harness sprint with no visible UI, deployed asset, Office/Word surface, diary interaction, or live clinical workflow for Yuri to manually review.


## Previous Closeout - Sprint 44

Sprint 44 added the backend-only supervised Bernie confirmation route that writes exactly one appointment only after explicit staff confirmation.

- Added authenticated `POST /api/v1/appointments/proposals/create/confirm-bernie`.
- The route accepts supervised Sprint 42/43 slot-selection/create-proposal evidence plus explicit `confirmed=true`.
- It blocks without appointment or audit writes when confirmation is false, source evidence is unsafe, selected slot and create command mismatch, or revalidation finds a stale conflict.
- On success it revalidates existing appointment safety, creates exactly one appointment through the existing create path, and records bounded Bernie/source evidence in the appointment audit log.
- Added `BernieCreateProposalConfirmationIn` and `AppointmentConfirmCreateProposalOut` schemas.
- Refactored appointment creation into `_create_appointment_from_body(...)` so direct create and confirmed Bernie create share validation, conflict checks, output hydration, break-overlap reporting, and audit writing.
- Added `tests/test_bernie_confirm_create_proposal.py` covering auth, explicit confirmation, no-write blocked paths, stale-conflict revalidation, source mismatch blocking, exactly-one-write success, bounded audit evidence, and no-LLM/no-provider proof.
- Cicero/Franklin implemented the backend-only sprint on `codex/bernie-confirm-create-proposal`.
- No diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous Bernie runtime, SMS, billing, resource admin, migration, or visible workflow changed.


## Previous Closeout - Sprint 43

Sprint 43 added the deterministic backend harness proving the Bernie normalize -> normalized search -> slot selection chain remains no-write/no-LLM before final booking confirmation work.

- Added `tests/test_bernie_slot_flow_review_harness.py`.
- The harness exercises the backend-only Bernie chain across command normalization, normalized slot search, and supervised slot selection proposal.
- It proves a successful normalize -> search -> select path can prepare create-proposal evidence without writing appointment rows or appointment audit rows.
- It covers no-match selection blocking and conflict selection blocking without new writes.
- It adds runtime and source-level guards that fail if the flow instantiates/calls the AI provider surface or performs final booking/audit writes inside the three Bernie proposal routes.
- Cicero/Plato implemented the sprint on `codex/bernie-slot-flow-review-harness`.
- No production route, schema, model, migration, diary UI, taskpane, Command Centre, Gemini parsing, autonomous Bernie runtime, final booking write bridge, audit mutation, billing, SMS, resource admin, or visible workflow changed.


## Previous Closeout - Sprint 42

Sprint 42 added the non-mutating `POST /api/v1/appointments/proposals/slot-search/selection` endpoint that converts one supervised slot-search candidate selection into create-proposal evidence.

- Added authenticated `POST /api/v1/appointments/proposals/slot-search/selection`.
- The endpoint accepts supervised slot-selection evidence, either from a normalized slot-search execution payload plus selected index/candidate or an explicit selected candidate plus required booking context.
- Selected candidates are validated against the search result when evidence is supplied, including index/candidate mismatch and not-in-results blocking.
- The route reuses the existing non-mutating create-proposal path through `_build_create_appointment_proposal(...)`, preserving conflict, break, provisional-patient, practice-scope, and confirmation semantics.
- Added `SlotSelectionProposalIn` and `SlotSelectionProposalOut` schemas for the supervised select-slot-for-create-proposal response.
- Added focused tests for auth, happy-path index selection, no appointment/audit writes, selected-candidate mismatch blocking, create-proposal conflict semantics, and source-level no-LLM/no-mutation proof.
- Cicero/Hegel implemented the backend-only fallback on `codex/bernie-slot-selection-proposal`.
- No diary UI, taskpane, Command Centre, booking write, audit mutation, billing, SMS, migrations, patient demographics, resource admin, or live Bernie autonomous runtime was added.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified this as a backend-only API contract with focused pytest and compile checks. There is no visible UI, deployed asset, appointment mutation, LLM call, or manual clinical workflow to review.

## Not Required Before Moving On

- No manual live API test is required; focused tests cover the route contract, selected-candidate validation, create-proposal reuse, conflict semantics, and non-mutation proof.
- No manual live UI review is required; no frontend files or deployed assets changed.
- No database migration or data repair is required.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, diary grid, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Future Bernie work can now chain command normalization, safe slot search, supervised candidate selection, and create-proposal evidence without writing appointments.
- The endpoint accepts client-supplied normalized search evidence and validates candidate consistency, but the evidence is not server-persisted. Future UI/runtime should still treat it as supervised review evidence and require create-proposal confirmation before any write.
- The next useful slice is either a supervised confirmation bridge that makes the final write semantics explicit or a lightweight deterministic review harness around the Bernie flow.
- A later sprint can decide where DB-backed name-to-UUID resolution belongs; this sprint intentionally treats identifier normalization as UUID/format parsing only.
- Natural language date phrases beyond deterministic `today`/`tomorrow` remain the upstream parser/LLM's responsibility.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert remains outside Sprint 39.

## Verification

- `python scripts\agent_worktrees.py audit --fetch` -> Sprint 42 Codex worker branch submitted and integration worktree clean.
- Worker plan accepted after metadata correction and implementation released to Cicero/Hegel.
- Ariadne reran backend compile check with the project venv: `python -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_slot_selection_proposal.py` -> passed.
- Ariadne reran focused slot-selection tests: `python -m pytest tests\test_slot_selection_proposal.py -q --tb=short -p no:randomly` -> 5 passed.
- Ariadne reran adjacent regression tests: `python -m pytest tests\test_slot_search_normalized_execution.py tests\test_slot_search_proposal.py tests\test_slot_search_normalize_endpoint.py tests\test_appointment_proposals.py -q --tb=short -p no:randomly` -> 41 passed.
- Diff hygiene: `git diff --check origin/master..origin/codex/bernie-slot-selection-proposal` -> passed.

## Recommended Next Direction

Sprint 43 should either add the final supervised confirmation bridge from create-proposal evidence to the existing appointment write path, with explicit audit/write semantics, or add a small deterministic review harness for the Bernie command-normalize-search-select chain before moving to UI/runtime surfaces.


## Previous Closeout - Sprint 41

Sprint 41 added the non-mutating `POST /api/v1/appointments/proposals/slot-search/normalized` endpoint that normalizes a Bernie slot-search command and, only when safe, returns candidate slots. It remains the normalize-and-search foundation used by Sprint 42 selection.


## Previous Closeout - Sprint 40

Sprint 40 added the deterministic, non-mutating `POST /api/v1/appointments/proposals/slot-search/normalize` endpoint. It remains the normalize-only foundation used by the Sprint 41 combined normalize-and-search contract.


## Previous Closeout - Sprint 39

Sprint 39 added the pure deterministic Bernie slot-search command normalizer and its unit tests. It remains the foundation used by the Sprint 40 endpoint.


## Previous Closeout - Sprint 38

| Item | Value |
|---|---|
| Batch | Sprint 38: Bernie-Safe Slot Search Proposal Foundation |
| Integrated through | Sprint 38 backend non-mutating slot-search proposal contract and smoke-only diary preview harness |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added a read-only `POST /api/v1/appointments/proposals/slot-search` endpoint that accepts typed slot-search constraints and returns ranked candidate slots, warnings, blocks, and a human-readable summary.
- Added `SlotSearchProposalIn`, `SlotCandidate`, and `SlotSearchProposalOut` schemas for future Bernie/reception scheduling workflows.
- Extracted `_resolve_day_schedule(...)` from existing slot-generation code so `/slots/{practitioner_id}` and slot-search proposal logic share the same day schedule/override resolution.
- Kept the new backend endpoint role-gated, practice-scoped, practitioner-scoped, optional patient/location constrained, and explicitly non-mutating: no appointment rows and no appointment audit rows are written.
- Added focused backend tests for auth, practice scoping, candidate ordering/duration/timezone fields, duration derivation, date-range validation, conflict filtering, non-blocking terminal statuses, break warnings, location-specific conflict handling, no-schedule days, limit caps, and non-mutation proof.
- Added a deterministic smoke-only diary slot-search preview harness behind `?smoke=true&slot_preview=true`; live diary rendering remains inert unless that explicit smoke/review flag is present.
- Added dashed, read-only slot-preview candidate styling and deterministic Playwright checks proving preview count, labels, and no booking-modal opening on preview click.
- Bumped diary assets to `diary.css?v=99` and `diary.js?v=104`.
- No live Bernie runtime, LLM/Gemini parsing, taskpane, Command Centre, real appointment mutation, waiting-room flow, billing, SMS, resource administration, or live diary slot-search UI was added.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the backend contract, non-mutation behaviour, frontend syntax/assets, and deterministic diary smoke checks. The visible diary preview is smoke/review-harness gated and is not a live user-facing workflow.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=104` and `diary.css?v=99` are loaded.
2. Exact UI path: open the normal live diary without `smoke=true&slot_preview=true`.
3. Expected result: no dashed slot-search preview candidates should appear anywhere in the live diary.
4. Expected safety: normal appointment cards, booking modal open/edit flows, click-to-create/edit behaviour, waiting-room panel, audit history, status controls, and drag/resize affordances should behave as before.
5. Suspicious signs: dashed preview cards visible in the live diary, clicking empty diary space no longer opens the expected booking workflow, slot previews create/edit appointments, console errors, or asset versions failing to update.
6. Skippable parts: do not manually retest backend slot-search API, taskpane, Command Centre, resource admin, billing, SMS, AI provider facade, security workflows, or cancelled appointment review for Sprint 38.
7. Evidence to report: only report a screenshot/console error if smoke preview artifacts leak into the live diary or booking click behaviour regresses.

## Not Required Before Moving On

- No manual live API test is required; focused pytest covers the slot-search proposal contract and non-mutation proof.
- No manual live UI review is required; deterministic smoke verifies the slot-preview harness and live/default absence condition.
- No database migration or data repair is required.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Future Bernie work can feed LLM-parsed constraints into the typed slot-search endpoint, then present candidates for human confirmation through a separate create-proposal path.
- Future UI work can replace the smoke fixture with real API-backed preview data, but only after an explicit live UI task and confirmation workflow are planned.
- Consider making slot-search warnings code-only plus friendly-label mapping if/when they become user-facing outside the smoke harness.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert remains outside Sprint 38.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 38 plan packets and implementation review packets.
- Backend compile check: `python -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_slot_search_proposal.py` -> passed.
- Focused backend slot-search tests: `python -m pytest tests\test_slot_search_proposal.py -q --tb=short -p no:randomly` -> 20 passed.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `python -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 19 passed.
- Frontend asset version check: `python scripts\check_frontend_versions.py` -> passed; diary CSS moved to `v=99` and diary JS moved to `v=104` while deployed pages still served previous versions before push.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 39 was dispatched as the next narrow Bernie slice: deterministic slot-search command parsing/normalization into the existing `SlotSearchProposalIn` constraint shape, without executing searches or creating appointments.


## Previous Closeout - Sprint 36

| Item | Value |
|---|---|
| Batch | Sprint 36: Diary Audit History Keyboard Accessibility |
| Integrated through | Sprint 36 audit-history toggle keyboard and ARIA semantics |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added `role="button"`, `tabindex="0"`, `aria-controls="booking-audit-content"`, and `aria-expanded="false"` to the booking audit-history header.
- Updated the audit-history click handler to keep `aria-expanded` synchronized with the collapsed/expanded state.
- Added keyboard support for Enter and Space on the audit-history header, with Space default scrolling prevented.
- Reset `aria-expanded` to `false` whenever the booking edit modal opens.
- Added deterministic diary smoke assertions for role, tabindex, `aria-controls`, `aria-expanded`, Enter toggle, Space toggle, click toggle, and reset-on-reopen behaviour.
- Bumped the diary JS cache-bust to `diary.js?v=102` in `docs/diary/diary.html`.
- No backend code, appointment mutation/proposal flow, taskpane, Command Centre, billing, SMS, AI provider, resource administration, cancelled appointment review, or non-audit-history controls were changed.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the keyboard behaviour through deterministic Playwright smoke tests and did not need visual/Computer Use review.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=102` and `diary.css?v=98` are loaded.
2. Exact UI path: open an existing appointment for editing and tab to the `Audit History` header.
3. Expected keyboard behaviour: pressing Enter expands the section, pressing Space collapses it, and clicking still works normally.
4. Expected accessibility state: the section starts collapsed and `aria-expanded` tracks the visible state, though this is mainly for assistive technology and automated checks.
5. Expected safety: no appointment status, waiting-area state, cancellation state, booking details, or proposal confirmation changes occur from toggling audit history.
6. Suspicious signs: focus cannot reach the audit header, Enter/Space do nothing, the page scrolls unexpectedly on Space, visible layout changes, audit rows disappear, console errors appear, or mutation controls appear in audit history.
7. Skippable parts: do not retest backend audit actor fields, test hooks, taskpane, Command Centre, patient files, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, security workflows, or cancelled-appointment review for Sprint 36.
8. Evidence to report: only report a screenshot/console error if keyboard toggling or visible layout regressed.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke passed keyboard and ARIA assertions.
- No database migration, data repair, Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Continue adding keyboard/ARIA assertions opportunistically when a visible control is touched.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 36.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found the Sprint 36 Antigravity plan and review packets.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed; `diary.js` moved to `v=102` while live deployed HTML still served `v=101` before push.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Pause Antigravity-only polishing unless Yuri wants more; prefer waiting for Claude's headless limit to recover before backend-heavy audit/proposal work.




## Previous Closeout - Sprint 35

| Item | Value |
|---|---|
| Batch | Sprint 35: Diary Audit History Test-Hook Hardening |
| Integrated through | Sprint 35 stable diary audit-history test hooks and deterministic smoke assertions |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added stable `data-testid` hooks to the diary booking audit-history section, header, title, content, list, fallback rows, audit items, metadata, timestamps, and details.
- Updated rendered audit-history list items in `docs/diary/diary.js` to set test hooks without changing visual copy or runtime behaviour.
- Updated `review/test_diary_smoke.py` to use the stable audit-history test hooks instead of brittle CSS class selectors.
- Updated `review/checks_diary.json` to assert the audit header/title through `data-testid` selectors.
- Bumped the diary JS cache-bust to `diary.js?v=101` in `docs/diary/diary.html`.
- No backend code, mutation/proposal flow, taskpane, Command Centre, billing, SMS, AI provider, resource administration, cancelled-appointment review, or broad booking modal redesign was included.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the deterministic diary smoke harness and asset-version checks. This sprint intentionally adds non-functional test hooks and stronger automated assertions only.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=101` and `diary.css?v=98` are loaded.
2. Exact UI path: open an existing appointment for editing, then expand `Audit History`.
3. Expected result: the visible audit-history copy should look unchanged from Sprint 34, but automated tests now target stable hooks under the hood.
4. Expected safety: no new buttons, edits, status changes, waiting-area changes, cancellation changes, or proposal confirmations should appear from the audit section.
5. Suspicious signs: audit history no longer expands, visible text changes unexpectedly, console errors appear, or booking save/cancel/status flows change.
6. Skippable parts: do not retest backend audit actor fields, taskpane, Command Centre, patient files, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, security workflows, or cancelled-appointment review for Sprint 35.
7. Evidence to report: only report a screenshot/console error if the audit section visually regressed or created a new mutation affordance.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke passed using the new hooks.
- No database migration, data repair, Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, billing, SMS, or security-console action is required.

## Known Follow-Up

- Keep moving stable UI review checks from visual/class selectors to `data-testid` hooks when touching a surface.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 35.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found the Sprint 35 Antigravity plan and review packets.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed; `diary.js` moved to `v=101` while live deployed HTML still served `v=100` before push.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 36 has been dispatched as another small Programme 2D slice while Claude's headless limit recovers: keyboard/ARIA semantics for the read-only audit-history toggle.

## Previous Closeout - Sprint 34

| Item | Value |
|---|---|
| Batch | Sprint 34: Appointment Audit History Readability |
| Integrated through | Sprint 34 backend audit actor-display contract and diary readable audit-history UI |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added read-time `confirmed_by_display` and `confirmed_by_role` fields to `AppointmentAuditLogOut`.
- Updated `GET /api/v1/appointments/{appointment_id}/audit` to batch-load confirming users with practitioners, preserve practice scoping, and derive a safe staff display label without adding a migration.
- Actor display falls back from practitioner first/last name to email local-part to `Unknown`; `confirmed_by_user_id` remains in the response for stable machine identity.
- Added audit contract tests proving receptionist fallback (`rec`), clinician practitioner display (`Alex Shera`), actor roles, auth, cross-practice denial, ordering, and empty history.
- Claude's accepted backend plan was recovered by Ariadne because Claude hit a session-limit/429 after committing the plan packet; no production code came from Claude after the plan gate.
- Diary audit history now renders friendly action labels (`Created`, `Updated`, `Status Changed`, `Cancelled`) and friendly status text such as `In Consult` and `Did Not Attend (DNA)`.
- Diary audit actor rendering now uses backend display names when present and restrained UUID fallback text such as `Staff (11111111)` when only a raw UUID is available.
- Diary audit transition copy now reads as `Changed from X to Y` and avoids duplicated `by` wording.
- Deterministic diary smoke checks now assert readable audit names, status transitions, and UUID fallback copy.
- No appointment mutation, proposal safety, taskpane, Command Centre, Gemini/AI provider, billing, SMS, restore/reactivation, or supervisor-dashboard work was included.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the backend audit actor contract, frontend syntax/assets, and deterministic diary Playwright smoke for the readable audit-history section. The change is read-only and does not add a new mutation workflow.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=100` and `diary.css?v=98` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary, and open an existing appointment for editing.
3. Expected collapsed state: the booking modal shows `Audit History`, collapsed by default, below the booking form fields.
4. Expected expansion: click `Audit History`; rows should use readable action/status text and staff labels, or show a clear empty/unavailable/error fallback.
5. Expected actor copy: if backend actor metadata exists, staff names/roles should display instead of raw UUIDs; if only a UUID is available, it should be shortened as `Staff (<first 8 chars>)`.
6. Expected create behaviour: opening an empty slot for a new booking hides `Audit History`.
7. Expected safety: expanding audit history must not change appointment status, waiting-area state, cancellation state, booking details, or proposal confirmation state.
8. Suspicious signs: raw `undefined`, full raw UUIDs in normal rows, confusing action labels, duplicated `by by`, audit history visible on create, edit modal crashes, new mutation controls in audit history, existing save/cancel/delete flow changes, or console errors.
9. Skippable parts: do not retest taskpane, Command Centre, patient file generation, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, security workflows, or cancelled-appointment review for Sprint 34.
10. Evidence to report: screenshot or short note showing the expanded audit section, readable row text/fallback, loaded asset versions, and any console error or unexpected mutation.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke opens the edit modal, expands audit history, and checks readable audit items.
- No database migration or data repair is required; actor display is derived at read time.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, recurrence, billing, SMS, or security-console action is required for this sprint.

## Known Follow-Up

- Add warning-code or warning-summary persistence later if supervisor review needs proof of warnings confirmed by staff.
- Consider actor display on future proposal-context previews if those become user-facing.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 34.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 34 plan packets and Antigravity's implementation review packet.
- Backend compile check: `.\.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py app\routers\appointments.py tests\test_appointment_audit.py` -> passed.
- Focused audit contract: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_audit.py -q --tb=short -p no:randomly` -> 15 passed.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 35 has been dispatched as a small deterministic-review-friendly slice while Claude's headless session limit recovers: add stable audit-history test hooks and smoke assertions without changing runtime behaviour.

## Previous Closeout - Sprint 33

| Item | Value |
|---|---|
| Batch | Sprint 33: Appointment Proposal Audit/History Foundation |
| Integrated through | Sprint 33 backend confirmed-mutation audit contract and diary read-only audit-history review UI |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added an `appointment_audit_log` table and SQLAlchemy model for confirmed appointment mutation history.
- Added `AppointmentAuditAction` plus `AppointmentAuditLogOut` so audit rows are returned through a typed API response.
- Added `GET /api/v1/appointments/{appointment_id}/audit`, practice-scoped and authenticated, returning the confirmed mutation history for one appointment.
- Confirmed appointment create, update, status-change, and soft-cancel/delete paths now write audit rows in the same transaction as the mutation.
- Proposal endpoints remain non-mutating and do not write audit rows; blocked or aborted proposals leave no audit residue.
- Cancellation audit rows preserve `cancellation_reason`; status audit rows preserve before/after status.
- Added `tests/test_appointment_audit.py` with focused coverage for non-mutating proposals, confirmed writes, empty audit history, auth, cross-practice denial, and ordering.
- Added a read-only collapsed `Audit History` section to the diary booking edit modal; it is hidden for new bookings and visible only when editing an existing appointment.
- The diary calls `/appointments/{id}/audit` in live mode, shows loading/empty/unsupported/error states, and simulates backend-shaped audit events in `?smoke=true`.
- Ariadne applied a bounded integration hotfix so the diary UI renders the backend's actual `status_after`, `status_before`, `confirmed_by_user_id`, and lower-case action enum shape; diary assets moved to `diary.css?v=98` and `diary.js?v=100`.
- No taskpane, Command Centre, Gemini/AI provider, billing, SMS, restore/reactivation, broad supervisor dashboard, or direct Bernie execution work was included.

## Recommended User Review

Residual user review/testing after closeout: none required before continuing.
Ariadne verified the backend audit contract, adjacent appointment proposal/status
regression suites, frontend syntax/assets, and deterministic diary Playwright
smoke for the new audit-history affordance. This is mostly infrastructure and a
read-only review surface, with no new direct mutation affordance.

Optional confidence check only, if Yuri happens to be in the live diary after deployment:

1. Setup: hard refresh the live diary and confirm `diary.js?v=100` and `diary.css?v=98` are loaded.
2. Exact UI path: sign in as a dev Admin or normal dev user, open the Diary, and open an existing appointment for editing.
3. Expected collapsed state: the booking modal shows an `Audit History` row, collapsed by default, below the booking form fields.
4. Expected expansion: click `Audit History`; audit rows, `No audit history found`, or an unavailable/error fallback should appear without enabling any write control.
5. Expected create behaviour: open an empty slot to create a new booking; the `Audit History` section should be hidden.
6. Expected safety: expanding audit history must not change appointment status, waiting-area state, cancellation state, booking details, or proposal confirmation state.
7. Suspicious signs: audit history appears on create, edit modal crashes, audit rows show raw `undefined`, the section enables mutation controls, existing save/cancel/delete flow changes, or browser console errors appear.
8. Skippable parts: do not retest taskpane, Command Centre, patient file generation, resource administration, drag/resize, recurrence, SMS, billing, AI provider facade, or security workflows for Sprint 33.
9. Evidence to report: screenshot or short note showing the edit modal audit section, expanded contents/fallback, loaded diary asset versions, and any console error or unexpected mutation.

## Not Required Before Moving On

- No manual live UI review is required; the deterministic diary smoke opens the edit modal, expands audit history, and checks rendered audit items.
- No manual database repair is required; the migration is additive and the audit table is empty until confirmed mutations occur.
- No Word taskpane, Command Centre, GCP/Gemini, Office dialog, resource admin, recurrence, billing, SMS, or security-console action is required for this sprint.

## Known Follow-Up

- Warning-code or warning-summary persistence was intentionally not completed in Sprint 33 because current confirmed mutation endpoints do not receive the prior proposal warning payload. A later richer audit sprint can add explicit `warning_codes`/`confirmed_with_warnings` capture if supervisor review needs it.
- The diary currently displays `confirmed_by_user_id` when no friendly user name is available; a future user-directory join or backend display field can improve readability.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 33.

## Verification

- `python scripts\agent_worktrees.py poll --fetch` -> found both Sprint 33 implementation review packets.
- Backend compile check: `python -m py_compile app\models\appointments.py app\schemas\appointments.py app\routers\appointments.py tests\test_appointment_audit.py` -> passed.
- Focused audit contract: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_audit.py -q --tb=short -p no:randomly` -> 14 passed.
- Adjacent appointment regressions: `.\.venv\Scripts\python.exe -m pytest tests\test_appointment_status_mutations.py tests\test_appointment_update_proposal.py tests\test_appointment_proposals.py -q --tb=short -p no:randomly` -> 71 passed when rerun serially. A prior parallel pytest launch hit the known Postgres enum creation race and was disregarded.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `.\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 17 passed.
- Frontend asset version check: `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py` -> passed for modified assets.
- Diff hygiene: `git diff --check` -> passed.

## Recommended Next Direction

Sprint 34 has been dispatched as the next Programme 2D readiness slice: appointment audit history readability, focused on safe backend actor-display metadata and diary read-only audit copy. Workers are plan-gated.

## Previous Closeout - Sprint 32

| Item | Value |
|---|---|
| Batch | Sprint 32: No-show/DNA Attendance Outcome Semantics |
| Integrated through | Sprint 32 backend NoShow/DNA status proposal proof suite; diary frontend stood down after existing semantics were verified |
| Status | Integrated, pushed, mirrored, audited, and closed |
| Last updated | 2026-06-26 |

## What Changed

- Added `tests/test_noshow_dna_status_contract.py`, a focused 14-test backend proof suite for NoShow and DNA attendance outcomes.
- Proved `POST /appointments/proposals/status/{id}` for both `NoShow` and `DNA` is non-mutating, safe, confirmation-required, and uses the terminal `proposal` autonomy tier.
- Proved same-status NoShow/DNA proposals block with `already_in_status`.
- Proved re-transitioning away from terminal NoShow/DNA warns with `already_terminal` while leaving the row unchanged.
- Proved NoShow/DNA proposals from a waiting area surface `clears_waiting_area` plus a `waiting_area_cleared` warning without mutating before confirmation.
- Proved confirmed `PATCH /appointments/{id}/status` to NoShow/DNA clears `waiting_area_id` in the database.
- Proved NoShow/DNA appointments do not block the public `/slots` availability API.
- Proved cross-practice NoShow/DNA status proposals return 404.
- No production backend code changed; the existing contract was correct and is now pinned explicitly.
- Antigravity frontend workstream was superseded: its corrected plan was accepted, but the CLI timed out in print mode before submitting implementation. Ariadne verified the current diary already handles NoShow/DNA labels, status options, waiting-area clearing proposals, active-grid exclusion, and Finished-section classification, so no frontend code delta was integrated.
- Added protocol guidance that Antigravity CLI prompts need an explicit `--print-timeout 15m` and that silent returns should be diagnosed with process, worktree, and CLI-log checks before being treated as crashes.

## Recommended User Review

Residual user review/testing after closeout: none required.
Ariadne verified the backend contract, frontend syntax, deterministic diary smoke
harness, and existing NoShow/DNA diary semantics using cheap tool-enabled checks.
Sprint 32 is primarily a contract-proof sprint and intentionally does not add a
new visible user workflow.

Optional confidence check only, if Yuri happens to be in the live diary:

1. Setup: hard refresh the live diary and sign in as a dev Admin or normal dev user.
2. Exact UI path: open an existing appointment, use the status selector, and choose `No Show` or `DNA`.
3. Expected proposal guard: a confirmation/proposal dialog appears before the appointment is mutated.
4. Expected terminal result: after confirming, the appointment should leave the active diary grid and should not remain in Waiting Room or In Consult.
5. Expected review location: the appointment can appear in the Finished section with a clear `No Show` or `DNA` label, depending on the current selected waiting-area tab/filter.
6. Suspicious signs: the appointment mutates before confirmation, remains in active Waiting Room/In Consult, blocks its old slot, shows as an active grid card, or has unclear status text.
7. Skippable parts: do not retest cancellation reasons, cancelled appointment review, resource administration, drag/resize, recurrence, taskpane, Command Centre, billing, SMS, or patient search for Sprint 32.
8. Evidence to report: a screenshot or short note showing the selected status, proposal dialog, final section/filter, and any unexpected active waiting-room/grid residue.

## Not Required Before Moving On

- No manual live UI test is required; the backend proof suite and existing deterministic diary checks cover Sprint 32's intended safety boundary.
- No database migration, data repair, Word taskpane, Command Centre, GCP, Gemini, Office dialog, security-console, or GitHub Pages manual action is required.
- No Antigravity implementation retry is required for Sprint 32; if future user review finds unclear NoShow/DNA copy or missing assertions, dispatch a fresh frontend-only follow-up.

## Known Follow-Up

- Use `--print-timeout 15m` for future Antigravity CLI plan/implementation prompts, and prefer running from the Antigravity worktree/project context.
- Consider a future lightweight frontend assertion specifically for NoShow/DNA terminal labels in the Finished section if those states become more visible in the review surface.
- The existing `pytest_asyncio` fixture-loop-scope warning remains a future test-hygiene item.
- The known moderate Dependabot alert still appears on GitHub pushes and remains outside Sprint 32.

## Verification

- `python scriptsgent_worktrees.py poll --fetch` -> found Claude's Sprint 32 implementation review packet and Antigravity's corrected plan packet.
- Antigravity CLI diagnosis: `tasklist /FI "IMAGENAME eq agy.exe"` showed no running CLI process; `git status --short --branch` in `EMR4-worktreesntigravity` was clean; latest Antigravity CLI log ended with `Print mode: timed out`, not a crash.
- Backend verification: `python -m pytest tests	est_noshow_dna_status_contract.py -q --tb=short -p no:randomly` -> 14 passed.
- Backend compile check: `python -m py_compile app
outersppointments.py app\schemasppointments.py` -> passed.
- Frontend static check: `node --check docs\diary\diary.js` -> passed.
- Deterministic diary review: `python -m pytest review	est_diary_smoke.py --junitxml=review\diary-review.xml -q` -> 14 passed.
- Diff hygiene: `git diff --check` -> passed, with only existing CRLF normalization warnings.

## Recommended Next Direction

Yuri resumed sprint automation after Sprint 32. Sprint 33 has been dispatched as
the next Programme 2D readiness slice: appointment proposal audit/history
foundation.

## Previous Closeout - Sprint 30

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
| Status | Integrated, pushed, mirrored, audited, and closed |
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
