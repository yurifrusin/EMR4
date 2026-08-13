# Post-status-action Compass and baton orientation

Date: 2026-08-13

Timestamp: 2026-08-13T23:19:38+10:00 (Australia/Brisbane)

Status: `candidate_ready_for_acceptance`

Result: `raisa_post_status_action_compass_baton_orientation_pass`

## Orientation result

The next dependency-satisfied tranche is a **provider-free two-projection
truth-parity conformance rehearsal**.

It should make the newly established architectural fact executable and hard to
regress: for the existing appointment-status command family, the conventional
grid and Reception One may use different visual and semantic grammars, but they
must submit intention to the same kernel, receive the same proposal/
confirmation/commit meaning, and rebuild their displayed state from the same
current Diary truth.

This is the narrowest useful next step because it does not add another command
or abstraction layer. It records a small typed trace for the two existing
surfaces and proves that their differences stop at presentation.

## The milestone: truth parity, not feature parity

Reception One is now on par with the conventional grid in the rank and source
of truth for one complete command family. Both paths converge on the same
client interaction, REST proposal/confirm family and backend authority kernel.
After a committed result, each reconstitutes visible state from a fresh Diary
read. Neither projection can make selection, display state or conversational
wording become committed truth.

That does **not** mean the two clients yet expose every same action. The grid
still has wider feature coverage. It also does not require identical layouts,
copy or interaction sequences. Truth parity means:

1. the same principal/practice/current-appointment boundary;
2. the same command-family admission and confirmation meaning;
3. the same commit, idempotency, audit and receipt authority;
4. the same fail-closed interpretation of cancel, block, stale and failure;
5. a fresh authoritative read before terminal display is treated as current;
   and
6. no renderer can promote its local selection, proposal, history or model
   wording into source truth.

The kernel therefore sits above every renderer and establishes meaning for
visual grids, meta-grid projections, conversation, and any future email, SMS,
thin-web, voice or delegated-bot modality. A modality may compress, arrange or
explain meaning; it cannot manufacture it.

## Exact repository finding

- The ordinary grid calls `setAppointmentStatus` directly.
- `metaGridSetAppointmentStatus` resolves the exact selected appointment from
  the current snapshot and delegates to that same `setAppointmentStatus`.
- `setAppointmentStatus` owns proposal checking, warnings/blocks, terminal
  confirmation, provisional-identity protection, signed confirmation, failure
  restoration, `loadDiary(true)` and focus return.
- Reception One then performs its additional exact projection reconstruction,
  clears stale history and rebinds or clears the selected appointment.
- The bridge contains no local network or confirm implementation; GraphQL
  remains read-only, and REST/OpenAPI remains the command surface.
- The API Spine exposes create, update, status, check-in and delete proposal/
  confirm families. Their existence does not authorise exposing another one in
  Reception One. Current authority explicitly closes that inference.
- Reception One can already project move, resize and cancellation candidates as
  non-committing review, but marks them `proposal_only` with operational command
  unavailable. Presentation reach therefore exceeds present command authority
  exactly as intended.

## Candidate comparison

| Direction | Classification | Finding |
|---|---|---|
| Two-projection truth-parity conformance rehearsal | `dependency_satisfied` | Uses the just-proved status family, authored-synthetic/route-intercepted evidence and existing surfaces only. It strengthens the kernel/projection invariant without new authority. |
| Another existing Diary command in Reception One | `user_decision` | Update, delete/check-in and other families exist, but the live baton explicitly forbids inferring another command-family choice. |
| Representative Stage 3B sessions | `human_action` | Readiness passes, but execution requires Yuri to reopen it and nominate or schedule five to eight voluntary reception staff. |
| First external patient channel or identity flow | `user_decision` | The renderer-neutral foundation passes, but identity topology, provider, channel, recovery, hosting and retention remain deliberately unsettled. |
| Another event family | `user_decision` | The Compass requires a fresh value/family decision; event coverage is not a default objective. |
| Operational watcher/durability runtime | `authority_closed` | Source/database access, delivery, concurrency/restart and operational retention remain closed; commands do not need watcher delivery for correctness. |
| General visual polish | `lower_leverage` | Safe in principle, but less valuable than protecting the new cross-projection truth invariant before the surface broadens. |

There is no genuine user-attention fork because exactly one direction is both
dependency-satisfied and inside current authority.

## Exact successor boundary to freeze

The next tranche should be limited to:

1. a tiny closed `ProjectionTruthTrace` vocabulary for the existing status
   interaction: renderer, selected-current coordinate, requested existing
   status, proposal outcome, confirmation outcome, kernel result, fresh-read
   result and displayed terminal state;
2. exactly two renderer values: `conventional_grid` and `reception_one`;
3. the existing status vocabulary and exact current status proposal/confirm
   route family only;
4. authored-synthetic, route-intercepted safe, terminal-cancel, blocked, stale,
   failed and committed traces for both renderers;
5. deterministic assertions that kernel-relevant traces agree while local
   layout, wording, focus target and projection history may differ;
6. zero raw fallback, optimistic-current claim, extra confirm, second command,
   event dependence or renderer-owned authority; and
7. one concise architecture note explaining how future modalities may reuse the
   invariant without becoming new sources of truth.

The trace is evidence and conformance vocabulary only. It must not become a
runtime session object, new GraphQL/Pydantic/OpenAPI contract, database record,
analytics stream, audit substitute or durable user transcript.

## What this unlocks

If the two-projection rehearsal passes, future UI or channel work can be judged
against an explicit invariant rather than against the conventional grid's
layout. New renderers need not mimic the grid; they must preserve the kernel
trace. That is the practical foundation for minimum-app/maximum-intelligence:
many modalities, one authoritative meaning.

It still does not select which command family, participant study or patient
channel comes next. Those choices remain at their recorded gates.

## Claim boundary

This is repository-local read-only orientation. It changes no product behavior
and proves no new runtime. Protected evidence, historical Diary/PHI, real or
product patient data, external patient identity/channels, another command or
event family, database/source/watcher/persistence, provider/ADC, credentials/
IAM/network, executable tools, deployment, production, release, Pages and
protected-ref movement remain closed.
