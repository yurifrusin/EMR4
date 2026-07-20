# Bernie Meta-grid Live-local Integration and Evaluation Closeout

**Date:** 2026-07-20

**Decision:** `meta_grid_live_local_integration_pass`

**Evidence label:** `live_local_browser_backend_postgres`

## 1. Outcome

Yuri authorised the bounded provider-free live-local synthetic
integration/evaluation tranche recommended by the accepted functional
meta-grid client closeout. The tranche passes.

The accepted meta-grid now has evidence through the ordinary authenticated
Diary UI, existing FastAPI routes and one disposable authored-synthetic
PostgreSQL database. A receptionist can open `Project view`, ask for and refine
a practitioner view, read a patient timeline, inspect backend availability,
select a candidate using touch or keyboard, prepare a supervised proposal,
compare practitioners, mask patient details, recover from interruption and
return to the ordinary Diary.

The meta-grid remains non-authoritative. It did not confirm or write an
appointment, create an audit/idempotency/session/event row, call a provider or
change an API/database contract.

## 2. Bounded implementation

### Provider-disabled local runtime

`scripts/bernie_meta_grid_live_local_harness.py` owns the exact database
`gp_pms_meta_grid_live_local_7f3c2a91_20260720`. It refuses another database,
non-PostgreSQL backend, non-loopback host or existing database. The population
contains only newly authored synthetic practice, staff, practitioner, patient,
schedule, roster and appointment rows.

The runtime sets the interpreter provider to `disabled`, disables deterministic
provider fallback, clears cloud credential variables, rotates a transient
synthetic password and JWT secret, and binds both servers to loopback. Passwords
and tokens are not recorded.

After final readback the harness verified its exact practice/user ownership
marker and dropped only the disposable database. The durable cleanup record is
`orchestration/prototypes/bernie-meta-grid-live-local-integration/database-cleanup-evidence.json`.

### Native browser/Office boundary

The ordinary Diary previously fetched hosted Office.js even for standalone
browser use. The first live run therefore stopped on a forbidden external
origin before performing product scenarios.

`docs/diary/office-bootstrap.js` now provides a narrow
`standalone_diary=true` capability only on `127.0.0.1` or `localhost`. It
supplies the minimal `Office.onReady` lifecycle needed by the unchanged Diary
scripts without an external request. Off loopback, the original hosted
Office.js script loads as before. Existing Office/confirmation browser tests
pass, so normal Office dialog behavior remains compatible.

### Interruption recovery correction

Rendered live acceptance found that interruption from `proposal_review`
discarded the proposal safely but `Refresh current view` returned the ordinary
overview rather than re-reading the exact underlying availability scope.

`refreshCurrent()` now recognizes `proposal_review`, keeps only its
practitioner/date/time/duration scope, discards patient selection and proposal
material, and performs a fresh existing slot-search proposal read. It never
reconstructs the stale proposal.

No API, GraphQL, OpenAPI/Pydantic, database model/migration, provider or
confirmation implementation changed.

API steward scope verdict: **client-only compatibility**. The tranche consumes
existing read/proposal contracts and changes no API Spine contract or command
authority.

## 3. Live-local browser and database evidence

The canonical evidence is
`orchestration/prototypes/bernie-meta-grid-live-local-integration/browser-acceptance-evidence.json`.

The task-scoped Playwright runner:

- used a real Chromium browser and visible Diary/meta-grid controls;
- authenticated through `POST /api/v1/auth/login`;
- used the visible next-day controls to reach the fixed synthetic date and the
  visible `Project view` control to enter the meta-grid;
- made real, non-intercepted calls to the local FastAPI/PostgreSQL runtime;
- used no `page.route`, mocked response, confirmation handoff or page-internal
  projection/command function;
- recorded only loopback traffic and exact bootstrap/read/proposal paths;
- saw zero failed API responses, unexpected paths, confirmation requests,
  session/event routes, console warnings/errors or page errors; and
- used a labelled standards DOM `blur` event only when headless Chromium did
  not emit blur after foreground-page switching. It did not call the
  meta-grid's interruption function directly.

Before and after all five browser contexts:

| Table/surface | Before | After |
|---|---:|---:|
| authored-synthetic appointments | 6 | 6 |
| appointment audit | 0 | 0 |
| command idempotency | 0 | 0 |
| Bernie booking sessions | 0 | 0 |
| Bernie session events | 0 | 0 |

All canonical SHA-256 snapshots were identical. This proves no appointment,
audit, durable command or event/session runtime mutation occurred during the
browser population.

## 4. Plain-language, responsive and keyboard result

| Surface | Result |
|---|---|
| desktop 1440×900 | practitioner root, `after 2 pm` refinement, four-entry patient timeline, explanation/Escape focus return and ordinary fallback passed |
| tablet landscape 1024×768 | eight backend availability candidates, touch selection, operational proposal-not-committed review and aligned two-practitioner comparison passed |
| tablet portrait 768×1024 | stacked shell, refinement and exact Back restoration passed |
| smartphone portrait 390×844 | one-column timeline, availability, Space selection, proposal review, privacy mask, interruption, fresh availability recovery and proposal clearing passed |
| smartphone landscape 844×390 | one visible comparison lane and usable next/previous practitioner navigation passed |

Enter submits the plain-language composer, Space selects a slot, Escape closes
the explanation and returns focus, and the native Tab sequence follows the
visible shell. All five viewports recorded zero page/host horizontal overflow,
zero enabled controls below 44 CSS pixels and no visible error overlay.

## 5. Corrected desktop capture evidence

The earlier 1440×900 smoke PNG was a capture artifact: its canvas continued to
1440 pixels but became black after approximately x=768. A live browser
reproduction had already shown full DOM geometry.

The new canonical desktop PNG is
`desktop-live-local-1440x900.png`. Its evidence records:

- window, document, body and meta-grid host width: 1440 CSS pixels;
- page and host horizontal overflow: 0;
- painted-content extent: 1.0 of image width; and
- non-black painted ratio in the rightmost 20%: 1.0.

The acceptance runner decodes the PNG and the deterministic test independently
rechecks the screenshot hash and painted-width thresholds. The client was not
clipped; the prior image was defective evidence and is superseded for current
desktop review without rewriting the historical artifact.

## 6. Verification and independent veto

The final serial populations passed:

- **20** focused live-local/functional artifact tests after cleanup and CLI
  non-disclosure evidence was
  added;
- **180** combined live-local, functional meta-grid, API Spine, slot-search,
  supervised-booking, provider-disabled zero-write, Stage 3A, accessible
  confirmation, handover and Ariadne tests; and
- **139/139** complete Diary smoke tests.

The first complete Diary smoke run had one isolated three-second timing failure
in the visible-date reanchor node. The exact node passed immediately and a full
clean rerun passed 139/139. The failure is not hidden or treated as an accepted
failure.

Node syntax, focused Ruff, screenshot hashes, blocked-route/runtime guards and
`git diff --check` passed.

Gemini 3.5 Flash (High), through a fresh Antigravity project bound to a clean
candidate worktree, returned `pass` with no findings. It judged all closed
boundaries intact and the evidence calibration accurate. The launcher transport
receipt and extracted decision are:

- `orchestration/agent_inbox/antigravity/bernie-meta-grid-live-local-integration-veto.md`; and
- `orchestration/agent_inbox/antigravity/bernie-meta-grid-live-local-integration-veto-decision.md`.

## 7. Correction and recovery record

1. The readiness population initially used the plural expected name for the
   repository's singular `diary_roster` table; the harness expectation was
   corrected before evidence.
2. The first browser run stopped on the existing hosted Office.js request; the
   loopback-only standalone bootstrap was added and compatibility retested.
3. The initial browser URL assumed `reference_date` changed the ordinary Diary
   date; it scopes Bernie only. The runner now changes the date through seven
   visible next-day actions before opening `Project view`.
4. Headless foreground-page switching did not emit blur consistently; the
   standards DOM blur-event fallback is explicit and labelled.
5. Proposal interruption recovery exposed the genuine overview-fallback bug;
   the client now performs a fresh underlying availability read.
6. The first predispatch receipt used unapproved event/method labels and lacked
   a verifier workspace receipt. It remains preserved as
   `predispatch-revision-required`; the corrected receipt passes before Gemini
   dispatch.
7. One complete Diary smoke run had the isolated timing failure described
   above; exact and full reruns passed.
8. PR 52's first GitHub Advanced Security gate raised high-severity alert 492
   because the harness convenience CLI serialized its generic database-derived
   report. Although the values were authored-synthetic counts and hashes, the
   sink was unnecessary. The CLI now emits only a fixed non-sensitive
   completion envelope; imported evidence helpers and canonical evidence are
   unchanged. The adjacent readiness-loop empty-except note was also resolved
   with an explicit expected-exception retry and fail-closed comment.

All corrections stayed within the frozen client/harness/evidence contract.

## 8. Closed boundaries and next decision

The tranche did not open or alter:

- protected holdouts v1-v10 or historical Diary material;
- provider calls, external prompts, design-model subscriptions or costs;
- PII or real patient/practice data;
- API, GraphQL, OpenAPI/Pydantic or database authority;
- appointment confirmation, write, autonomous action or receipt authority;
- event producers, consumers, outbox, durable session runtime, attention
  runtime or subscriptions;
- Stage 3B, representative participants, voice, push-to-talk or ambient
  listening; or
- production, deployment or release.

Return the baton to Yuri. The next useful decision is a focused Yuri review of
the live-local working client and its plain-language/proposal behavior. Visual
reorganization or multi-model design synthesis remains later optional work.
Stage 3B and every closed boundary above still require a fresh decision.
