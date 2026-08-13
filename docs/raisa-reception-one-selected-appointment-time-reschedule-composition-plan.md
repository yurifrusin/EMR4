# Reception One selected-appointment time-reschedule composition plan

Date: 2026-08-14

Timestamp: 2026-08-14T07:51:51+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_execution`

Task baseline: `2ee298e8b089e1d16133989f9a669d6dd46aff51`

Target result: `raisa_reception_one_selected_appointment_time_reschedule_composition_pass`

Reasoning level: High. Yuri selected the existing appointment update/reschedule
family as the next projection-neutral truth application. This plan freezes the
narrowest useful composition without changing backend authority or creating a
second client command path.

## Objective

Let an internal staff user select one current appointment in Reception One,
choose another 15-minute start time on the same date, and submit it through the
ordinary native Diary's existing `handleMoveResize` update proposal/confirm
interaction.

Reception One remains a projection and interaction surface. The existing
update proposal/confirm family remains the only commit path. The backend owns
practice and actor authority, current appointment truth, safety, warnings,
blocks, signed confirmation evidence, idempotency, audit and atomic commit.

## Boundary classification

- **Read surface:** the existing scoped appointment snapshot and a fresh
  post-action appointment/projection read.
- **Command surface:** existing `POST /api/v1/appointments/proposals/update/{id}`
  and its proposal-supplied allowlisted confirm endpoint only.
- **UI composition:** one selected-appointment time panel and a same-page bridge
  to `handleMoveResize`.
- **Frozen invariants:** appointment id, practice, date, practitioner, duration,
  patient linkage, type, location, status, waiting area, reason, notes and
  booking channel do not change.
- **Not opened:** raw `PUT`, new route or command family, full edit form,
  cross-day move, practitioner move, resize, GraphQL mutation, backend or
  OpenAPI change, database/event/provider/external patient work.

## Frozen implementation

1. Show the selected real appointment's current start/end, a labelled time
   input with a 15-minute step, `Review time change`, and a patient-free polite
   live outcome region. Expose no date, practitioner, duration, patient or full
   editor control.
2. Permit exactly one current non-placeholder appointment. Reject invalid,
   unaligned, unchanged, out-of-day or projection-stale time input locally
   without a request.
3. Add a bridge operation beside the accepted status bridge. It validates the
   selected id and `HH:MM`, derives `deltaStart`, fixes `deltaDuration` at zero
   and resolves the same practitioner column, then delegates to the existing
   `handleMoveResize` interaction. The bridge contains no `fetch`, route,
   proposal, confirm, payload-signing, idempotency or compatibility-write code.
4. Extend `handleMoveResize` compatibly with optional phase observation and a
   structured terminal result. Existing drag, resize and keyboard callers keep
   their present contract.
5. The update request changes only `appointment_date` and `start_time_local` in
   meaning. Preserve every other field from the exact current appointment.
   The proposal is non-mutating and must display backend safety, warnings,
   blocks and old/new time meaning.
6. Visible staff confirmation is mandatory for any proposal requiring it. The
   client preserves the server-created `confirm_payload` opaquely, changes only
   `confirmed` to true, and uses the existing distinct confirmation idempotency
   key. It never reconstructs freshness or signed evidence.
7. Parameterize the accessible proposal dialog as `Confirm Appointment Time
   Change`, retain focus containment and Escape/Cancel behavior, state that
   current truth will be checked again, and deterministically return focus to
   the initiating time input.
8. Latch one action while checking, awaiting confirmation, saving, stale or
   interrupted. Reception One's Escape handler must not close the workspace
   behind the proposal dialog. Blur or visibility interruption starts no
   duplicate and requires reconciliation before another action.
9. After every terminal outcome—cancel, block, stale rejection, transport or
   confirmation failure, idempotent replay or commit—perform a fresh
   authoritative read and reconcile both projections. Retain selection only if
   the exact appointment remains in scope; otherwise announce its absence and
   move focus safely. Event cues never substitute for this read.
10. Mirror the existing selected-action responsive treatment: one column below
    700 px, visible focus, no horizontal overflow and usable desktop, tablet,
    phone and keyboard interaction.

## Acceptance scenarios

The provider-free authored-synthetic packet runs both `conventional_grid` and
`reception_one` through six route-intercepted outcomes:

1. **Safe direct commit:** one proposal and one signed confirm; fresh start/end
   reflect the requested time.
2. **Warning cancelled:** Cancel or Escape; one proposal, zero confirms and
   unchanged fresh truth.
3. **Blocked proposal:** no confirm control or write; unchanged fresh truth.
4. **Stale confirmation:** backend current-truth rejection; no optimistic time
   survives and fresh truth is restored.
5. **Proposal or transport failure:** zero confirm and no fallback mutation;
   fresh truth remains authoritative.
6. **Warning committed:** explicit staff confirmation, one proposal/one confirm
   and fresh committed coordinates.

Every pair must normalize to identical appointment id, date, start, end,
practitioner, duration, patient linkage and status. It must also prove exact
proposal/confirm counts, zero raw `PUT` and zero unexpected mutation routes.
Separate cases prove invalid/no-op input has zero routes, interruption requires
fresh reconciliation, dialog focus/Escape are correct and desktop/tablet/phone
layouts do not overflow.

Intercepted browser evidence is labelled `route_intercepted_browser`, never
live. Static smoke evidence is labelled `authored_synthetic_client_fixture`.

## Parallel execution allocation

- **DeepSeek V4 Flash/high:** owns only one new route-intercepted browser test
  artifact after a passing pre-worker receipt. It may edit that new test file
  only and may not touch product code, existing tests, API/backend surfaces,
  orchestration authority, closeout or Git.
- **Sol:** owns product HTML/CSS/JavaScript integration, deterministic
  admission, rendered-browser execution, evidence and acceptance.
- **Gemini 3.6 Flash/high:** receives a fresh read-only veto packet only after
  the candidate passes locally. It checks command-path convergence, freshness,
  focus/Escape/accessibility, interruption and the absence of a second write
  path; it has no edit or integration authority.

## Verification

- New deterministic source guards for bridge-only delegation, immutable-field
  scope, no bridge-local network/write, phases, fresh reconciliation, focus and
  interruption.
- New route-intercepted browser acceptance driver and paired normalized truth
  evidence, containing no credentials, headers, traces or product data.
- Complete affected native Diary/Reception One packets, update-proposal/API
  Spine/security tests, JavaScript syntax, canonical fast profile, Browser
  plugin rendering at desktop/tablet/phone and Git whitespace.
- No PostgreSQL, provider, external network, product source or deployment.

## Recovery and stop

Correct mechanical selector, focus, styling, fixture, request-interception or
evidence defects inside this exact boundary and rerun. Stop only if success
requires a new route or command, changed immutable field, real data, database
or source access, provider use, protected evidence, deployment or a genuinely
non-inferable user-owned interaction choice.

## Closed surfaces

No FastAPI, GraphQL, OpenAPI, database/migration/RLS, event/cue runtime,
watcher, product/patient/clinical data, historical Diary/PHI, external patient
identity/client/channel, provider/ADC, credential/IAM/network, executable model
tool, new command/write, deployment, production, release, Pages or protected-
ref action is opened. `docs/branding/` and every unrelated untracked file
remain preserved; staging is explicit-path only.
