# Reception One selected-appointment practitioner-only reassignment composition plan

Date: 2026-08-14

Timestamp: 2026-08-14T12:47:51+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_execution`

Task baseline: `e3015f36a9f93b7fc9382908a16c8a729fefc590`

Target result: `raisa_reception_one_selected_appointment_practitioner_reassignment_composition_pass`

Reasoning level: Extra High. This freezes a small user-visible command
composition, while preserving the accepted update authority and API Spine.

## Objective

Let an internal staff user select one current appointment in Reception One,
choose one different practitioner from the current authenticated
practice-scoped active-practitioner directory, and submit the change through
the native Diary's existing `handleMoveResize` update proposal/confirm
interaction.

Reception One remains a projection and interaction surface. The existing
update proposal/confirm family remains the only commit path. The backend owns
practice and actor authority, current appointment and practitioner truth,
roster/schedule/break conflicts, warnings, blocks, signed confirmation
evidence, idempotency, audit and atomic commit.

## Boundary classification

- **Read surfaces:** the existing scoped appointment snapshot, an exact fresh
  appointment read, the existing authenticated active-practitioner directory,
  and a fresh post-action appointment/projection read.
- **Command surface:** existing
  `POST /api/v1/appointments/proposals/update/{id}` and its proposal-supplied
  allowlisted confirm endpoint only.
- **UI composition:** one practitioner selector within the selected
  appointment actions and a same-page bridge to `handleMoveResize`.
- **Only mutable meaning:** `practitioner_id`.
- **Frozen invariants:** appointment id, practice, date, start time, duration,
  patient linkage, type, location, status, waiting area, reason, notes and
  booking channel.
- **Not opened:** raw `PUT`, new route or command family, full edit, time or
  duration change, cross-day move, GraphQL mutation, backend/OpenAPI/database,
  event/provider or external-patient work.

## Frozen implementation

1. Show the selected real appointment's current practitioner, a labelled
   `New practitioner` selector, `Review practitioner change`, and patient-free
   polite live feedback. Expose no date, time, duration, patient or full-editor
   control inside this action.
2. Offer only distinct entries whose current directory row has
   `active === true`, comes from the existing authenticated practice-scoped
   practitioner directory, and is not the selected appointment's current
   practitioner. Template-only, inactive, malformed, duplicate and synthetic
   non-test entries are never action targets. The accepted 200-row directory
   cap remains an explicit limit; this tranche adds no pagination.
3. Immediately before delegation, read the exact current appointment and the
   active-practitioner directory again. The requested id must still occur
   exactly once with `active === true` and must still differ from current
   truth. Missing, failed, ambiguous, stale or inactive target evidence starts
   zero proposal or confirmation request.
4. Add a bridge beside the accepted time and duration bridges. It supplies
   literal zero `deltaStart`, literal zero `deltaDuration`, an exact target
   practitioner column/reference and delegates once to `handleMoveResize`.
   The bridge contains no update route, proposal, confirm, payload-signing,
   idempotency, compatibility-write or raw-`PUT` implementation.
5. Permit `handleMoveResize` to resolve an exact target directly from the
   column's existing `practitioner_id`, retaining its AHPRA mapping fallback
   for ordinary grid callers. No caller may supply an arbitrary target outside
   the freshly admitted active-directory row.
6. Parameterize the existing dialog options so the accessible title is
   `Confirm Appointment Practitioner Change`, the summary names a practitioner
   reassignment, and the visible transition shows current and proposed display
   names. Existing drag, keyboard, time and duration callers retain their
   existing contract.
7. The update request changes only practitioner meaning. Preserve date, start,
   duration and every other field from the exact fresh appointment. The
   proposal remains non-mutating and owns roster, schedule/break conflict,
   warning and block meaning.
8. Visible staff confirmation is mandatory whenever the proposal requires it.
   Preserve `confirm_payload` opaquely; alter only the accepted acknowledgement
   fields and use the existing distinct confirmation idempotency key.
9. Status, time, duration and practitioner actions share mutual exclusion.
   Blur or visibility interruption starts no duplicate and requires fresh
   reconciliation before any further selected-appointment action.
10. After every terminal outcome--cancel, block, stale rejection, directory or
    transport failure, idempotent replay or commit--perform an exact fresh
    appointment read and reconcile both projections. Only that read may supply
    the displayed practitioner. Terminal bridge callbacks must not outrun the
    required exact read.
11. The dialog retains focus containment and Escape/Cancel behavior and returns
    focus to the practitioner selector. Preserve visible focus and no
    horizontal overflow at desktop, tablet and phone sizes.

## Acceptance scenarios

The provider-free authored-synthetic packet runs both `conventional_grid` and
`reception_one` through six route-intercepted outcomes:

1. safe direct practitioner commit;
2. warning cancelled by button or Escape;
3. blocked proposal with no confirm;
4. stale confirmation rejection;
5. directory/proposal/transport failure; and
6. warning reviewed and committed.

Every pair normalizes to identical appointment id, date, start, end,
practitioner, duration, patient linkage and status. It proves exact
proposal/confirm counts, zero raw `PUT`, zero unexpected mutations, and no
optimistic target after failure. Separate cases cover same, inactive,
unlisted, duplicate and malformed target zero-route denial; fresh-directory
failure; interruption/fresh reconciliation; dialog focus/Escape; status/time/
duration regression; the 200-row boundary; and desktop/tablet/phone layout.

Evidence labels are `route_intercepted_browser`,
`authored_synthetic_client_fixture` and `repository_static_and_regression`,
never live.

## Parallelism-efficacy allocation

- **DeepSeek V4 Flash/high -- planned, positive leverage:** own exactly one new
  isolated route-intercepted practitioner-reassignment browser-test artifact.
  It is capped at 650 source lines and may not edit product, existing tests,
  orchestration, acceptance or Git integration.
- **Native subagent -- planned, positive leverage:** produce a read-only exact
  seam map for active-directory admission, target-column resolution,
  delegation, shared latching, reconciliation, accessibility and regression
  surfaces. It owns no edits or acceptance.
- **Sol -- serial authority owner:** user-visible meaning, product HTML/CSS/
  JavaScript integration, worker admission/recovery, deterministic gate,
  rendered inspection, evidence and acceptance.
- **Gemini 3.6 Flash/high -- reserved, required independence:** after the exact
  candidate passes deterministically, run one fresh read-only veto over active
  target admission, command convergence, immutable fields, freshness,
  accessibility, interruption and absence of a second write path.

DeepSeek test authoring and native analysis may proceed concurrently after the
same committed plan/receipt while Sol implements. Worker admission/recovery,
deterministic convergence, Gemini dispatch and acceptance remain serial.
Reassess all lanes at worker return, material recovery, new/restored context,
pre-verifier admission and closeout; closeout compares planned with actual use.

## Verification

- New static guards for exact active-directory admission, literal zero time and
  duration deltas, direct practitioner-id resolution, bridge-only delegation,
  dialog parameters, four-way mutual exclusion and exact fresh reconciliation.
- New paired route-intercepted browser matrix and normalized truth evidence.
- Complete duration/time/status/truth-parity/native Diary and practitioner-
  directory regressions, affected API Spine/security/idempotency tests,
  JavaScript syntax, canonical fast profile, rendered desktop/tablet/phone
  inspection and Git whitespace.
- No PostgreSQL, provider, external network, real product source or deployment.

## Recovery and stop

Correct mechanical selector, fixture, mapping, focus, styling, dialog,
interception or evidence defects within this boundary and rerun. Stop only if
success requires a new route/command, changing a frozen field, admitting a
target without current active-directory evidence, real data, database/source
access, provider use, protected evidence, deployment or a genuinely
non-inferable user-owned interaction choice.

## Closed surfaces

No FastAPI, GraphQL, OpenAPI, database/migration/RLS, event/cue runtime,
watcher, product/patient/clinical data, historical Diary/PHI, external patient
identity/client/channel, provider/ADC, credential/IAM/network, executable model
tool, new command/write, deployment, production, release, Pages or protected-
ref action is opened. `docs/branding/` and every unrelated untracked file
remain preserved; staging is explicit-path only.
