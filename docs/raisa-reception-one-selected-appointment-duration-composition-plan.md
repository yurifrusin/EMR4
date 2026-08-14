# Reception One selected-appointment duration-only composition plan

Date: 2026-08-14

Timestamp: 2026-08-14T10:46:25+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_execution`

Task baseline: `268e90316c3ef248385ec19d25768c20aed2f3fe`

Target result: `raisa_reception_one_selected_appointment_duration_composition_pass`

Reasoning level: High. The accepted time-reschedule composition names this
duration-only descendant inside Yuri's selected update/rescheduling direction.
It changes no authority, backend contract or projection-neutral truth meaning.

## Objective

Let an internal staff user select one current appointment in Reception One,
choose a different duration reachable in 15-minute resize increments, and
submit it through the native Diary's existing `handleMoveResize` update
proposal/confirm interaction.

Reception One remains a projection and interaction surface. The existing
update proposal/confirm family remains the only commit path. The backend owns
practice and actor authority, current appointment truth, schedule and break
conflicts, warnings, blocks, signed confirmation evidence, idempotency, audit
and atomic commit.

## Boundary classification

- **Read surface:** the existing scoped appointment snapshot and a fresh
  post-action appointment/projection read.
- **Command surface:** existing `POST /api/v1/appointments/proposals/update/{id}`
  and its proposal-supplied allowlisted confirm endpoint only.
- **UI composition:** one duration control within the selected appointment's
  timing actions and a same-page bridge to `handleMoveResize`.
- **Only mutable meaning:** `duration_minutes`, with the derived end time.
- **Frozen invariants:** appointment id, practice, date, start time,
  practitioner, patient linkage, type, location, status, waiting area, reason,
  notes and booking channel.
- **Not opened:** raw `PUT`, new route or command family, full edit, move,
  cross-day or cross-practitioner action, GraphQL mutation, backend/OpenAPI,
  database/event/provider/external patient work.

## Frozen implementation

1. Show the selected real appointment's current duration/end, a labelled
   duration selector, `Review duration change`, and a patient-free polite live
   outcome. Expose no date, start, practitioner, patient or full-editor control.
2. Generate target options by applying whole 15-minute deltas to the exact
   current duration. Admit only integer targets from 15 through 480 minutes
   that keep the unchanged start and derived end on the same date. Reject
   invalid, unchanged, out-of-range, out-of-day or projection-stale input with
   zero request. This mirrors the accepted grid resize quantum while preserving
   valid non-multiple-of-15 current durations such as 20 minutes.
3. Add a bridge beside the accepted time bridge. It resolves the exact current
   appointment, validates the target, derives `deltaDuration`, fixes
   `deltaStart` at zero, resolves the same practitioner and delegates once to
   `handleMoveResize`. The bridge contains no fetch, route, proposal, confirm,
   payload-signing, idempotency or compatibility-write code.
4. Parameterize `handleMoveResize` through its existing optional action options
   so the accessible dialog says `Confirm Appointment Duration Change` and
   describes the current/proposed duration and derived end. Existing drag,
   keyboard, time-reschedule and other callers keep their current contract.
5. The update request changes only `duration_minutes` in meaning. Preserve
   date/start/practitioner and every other field from the exact current
   appointment. The proposal is non-mutating and owns schedule/break conflict,
   warning and block meaning.
6. Visible staff confirmation is mandatory whenever the proposal requires it.
   Preserve `confirm_payload` opaquely; alter only the existing acknowledgement
   fields and use the existing distinct confirmation idempotency key.
7. The dialog retains focus containment and Escape/Cancel behavior, states that
   current truth will be checked again, and returns focus to the duration
   selector.
8. Status, time and duration actions share mutual exclusion. Blur or visibility
   interruption starts no duplicate and requires fresh reconciliation before
   another action.
9. After every terminal outcome—cancel, block, stale rejection, transport or
   confirmation failure, idempotent replay or commit—perform a fresh
   authoritative read and reconcile both projections. Only that exact fresh
   appointment may supply the displayed duration/end.
10. Preserve visible focus and no horizontal overflow at desktop, tablet and
    phone sizes. The duration control may share the existing timing card, but
    it remains a separate duration-only submission.

## Acceptance scenarios

The provider-free authored-synthetic packet runs both `conventional_grid` and
`reception_one` through six route-intercepted outcomes:

1. safe direct duration commit;
2. warning cancelled by button or Escape;
3. blocked proposal with no confirm;
4. stale confirmation rejection;
5. proposal or transport failure; and
6. warning reviewed and committed.

Every pair normalizes to identical appointment id, date, start, end,
practitioner, duration, patient linkage and status. It proves exact
proposal/confirm counts, zero raw `PUT`, zero unexpected mutations, and no
optimistic target after failure. Separate cases cover invalid/no-op/out-of-day
zero-route denial, interruption/fresh reconciliation, dialog focus/Escape,
time-action regression and desktop/tablet/phone layout.

Evidence labels are `route_intercepted_browser`,
`authored_synthetic_client_fixture` and `repository_static_and_regression`,
never live.

## Parallelism-efficacy allocation

- **DeepSeek V4 Flash/high — planned, positive leverage:** own exactly one new
  isolated route-intercepted duration browser-test artifact. It may not edit
  product, existing tests, orchestration, acceptance or Git integration.
- **Native subagent — planned, positive leverage:** produce a read-only exact
  seam map for bridge delegation, shared action latching, dialog wording,
  responsive reuse and regression surfaces. It owns no edits or acceptance.
- **Sol — serial authority owner:** product HTML/CSS/JavaScript integration,
  worker admission/recovery, deterministic gate, evidence and acceptance.
- **Gemini 3.6 Flash/high — reserved, required independence:** after the exact
  candidate passes deterministically, run one fresh read-only veto over command
  convergence, immutable fields, freshness, accessibility, interruption and
  absence of a second write path.

DeepSeek test authoring and native analysis may proceed concurrently after the
same committed plan/receipt. Sol implementation may proceed beside them.
Worker admission/recovery, deterministic convergence, Gemini dispatch and
acceptance are serial. Reassess all lanes at worker return, material recovery,
new/restored context, pre-verifier admission and closeout; closeout compares
planned with actual use.

## Verification

- New static guards for duration validation, literal zero start delta, same
  practitioner, bridge-only delegation, dialog parameters, mutual exclusion and
  fresh exact reconciliation.
- New paired route-intercepted browser matrix and normalized truth evidence.
- Complete time/status/truth-parity/native Diary regressions, affected API
  Spine/security/idempotency tests, JavaScript syntax, canonical fast profile,
  rendered desktop/tablet/phone inspection and Git whitespace.
- No PostgreSQL, provider, external network, product source or deployment.

## Recovery and stop

Correct mechanical selector, fixture, focus, styling, dialog parameter,
interception or evidence defects within this boundary and rerun. Stop only if
success requires a new route/command, changing a frozen field, real data,
database/source access, provider use, protected evidence, deployment or a
genuinely non-inferable user-owned interaction choice.

## Closed surfaces

No FastAPI, GraphQL, OpenAPI, database/migration/RLS, event/cue runtime,
watcher, product/patient/clinical data, historical Diary/PHI, external patient
identity/client/channel, provider/ADC, credential/IAM/network, executable model
tool, new command/write, deployment, production, release, Pages or protected-
ref action is opened. `docs/branding/` and every unrelated untracked file
remain preserved; staging is explicit-path only.
