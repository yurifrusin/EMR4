# Provider-free read-only post-cancellation programme orientation

Date: 2026-08-18

Timestamp: 2026-08-18T03:31:00+10:00 (Australia/Brisbane)

Status: `candidate_ready_for_deterministic_verification`

Task baseline: `5981b6cacdd3d488462803748c0d86f1e9bc2457`

Result:
`raisa_provider_free_read_only_post_cancellation_programme_orientation_pass`

Evidence label: `repository_static_authored_synthetic`

## Decision

The next dependency-satisfied tranche is a provider-free read-only
arrival/check-in command-family convergence review.

It must reconcile three current repository facts before any product or route
change:

1. both first-party Diary projections can currently express check-in as the
   general status transition to `Arrived`;
2. a distinct A5.1 check-in proposal/confirm family exists, can bind optional
   waiting-area assignment and emits its own attributable audit, receipt and
   patient-free committed event, but it remains default-off and restricted to
   an authored-synthetic practice allowlist; and
3. the static Diary action grammar, route contract and promotion checklist
   still classify check-in as planned-not-implemented and state that no signed
   check-in confirm endpoint exists.

These layers are not evidence of a corrupt write path. They are an authority
and semantic-lifecycle inconsistency: route existence, product admission,
first-party rendering and agent grammar currently describe different scopes.
The smallest safe next step is to decide their canonical relationship without
opening any of them further.

## Command-family and first-party-consumer matrix

| Family | API Spine/runtime posture | Ordinary Diary | Reception One | Current classification | Smallest next action |
|---|---|---|---|---|---|
| Create plus slot selection | Canonical create proposal/confirm plus non-mutating slot normalize/search/select and Bernie supervised wrapper | Existing booking editor uses create proposal/confirm | Intent projection hands selected evidence to the existing confirmation-grade booking review | Complete for current first-party reference-client scope; later external clients remain closed | Preserve |
| Update/reschedule | Canonical update proposal/confirm | Booking editor uses update proposal/confirm | Time, duration, practitioner and same-family multi-change editor use the same update family | Complete for current selected-appointment field set | Preserve |
| General status | Canonical status proposal and canonical status-confirm, with hidden historical alias only | Status selector uses proposal/confirm and fresh Diary reconciliation | Selected status action uses the same family and fresh projection reconciliation | Two-projection status-only parity accepted | Preserve |
| Waiting-area move | Non-mutating waiting-area proposal feeds the status command shape; no dedicated OpenAPI confirm operation | Ordinary Waiting Room can submit waiting-area/status intent through the existing status path | No selected-action-console waiting-area control | Partly represented; static action grammar still says planned-not-implemented | Retain inside the arrival convergence review; do not add a control yet |
| Delete/cancel | Canonical delete proposal/confirm with strict minimal public receipt | Dedicated delete-only flow now has visible confirmation and fresh-truth reconciliation | Selected cancellation action uses the same kernel | Complete two-projection cancellation convergence at Continuity 313 / Compass 295 | Preserve |
| Dedicated check-in | `/appointments/proposals/check-in/{appointment_id}` and `/check-in/confirm` exist behind default-off `rayleen_a5_check_in_enabled` and an exact authored-synthetic practice allowlist | “Check In” uses general `Arrived` status, optionally with waiting-area input; it does not call A5.1 | `Arrived` is a general status choice; no dedicated check-in bridge/control exists | Implemented bounded A5.1 runtime, not generally admitted; static grammar says unimplemented | Selected provider-free read-only convergence review |
| Link patient | No signed proposal/confirm family | No canonical command consumer | No canonical command consumer | Planned-not-implemented and identity-sensitive | Retain as a later distinct identity/authority gate |

## Exact inconsistency

The conflict is mechanical and bounded:

- `app/config.py` defaults `rayleen_a5_check_in_enabled` to `False` and its
  practice allowlist to empty;
- `app/routers/appointments.py` mounts a Receptionist-only A5.1 proposal and
  confirm route, with gate checks before resource lookup;
- `docs/api-spine/openapi/appointment-commands.yaml` declares
  `proposeAppointmentCheckIn` and `confirmAppointmentCheckInProposal`;
- `app/services/diary/action_grammar.py` says check-in is unimplemented and no
  signed endpoint exists;
- `app/services/diary/action_route_contract.py` points check-in at the generic
  status proposal and says no check-in confirm action exists;
- `app/services/diary/planned_action_promotion.py` already anticipates either a
  dedicated signed check-in action or an explicitly reviewed status-confirm
  binding that records check-in semantics; and
- `docs/diary/meta-grid.js` exposes only status, time, duration, practitioner
  and cancellation selected actions, while the ordinary Waiting Room invokes
  its existing status transition for `Arrived`.

The same route-contract layer has one exact path-spelling drift: it records
`/appointments/proposals/status/{appointment_id}`, while FastAPI mounts
`/appointments/proposals/status/{appointment_id:uuid}`. The unchanged baseline
`test_diary_action_route_endpoint_coverage.py` consequently reports six
failures: it cannot match the documented status/check-in proposal path and
misclassifies the literal `/status/confirm` route as shadowed. This is preserved
negative evidence for the next convergence review, not a failure caused by this
documentation-only candidate and not authority to edit the route contract now.

The next review must therefore answer whether A5.1 is:

1. the future canonical arrival command whose Rayleen-specific/default-off
   admission must first be separated from its reusable deterministic kernel;
2. an authored-synthetic Bureau-only proof that should remain gated while
   generic status-confirm becomes the explicitly documented check-in binding;
   or
3. a specialized atomic status-plus-waiting-area command retained alongside a
   narrower generic status operation, with a strict non-overlap rule.

No option is selected by this orientation. The next read-only review freezes
the decision from exact payload, confirmation, authority, transaction, event,
audit, receipt, client and grammar evidence.

## Successor boundary

Open exactly one provider-free repository-static read-only tranche:

`raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review`

It may author only its plan, threat delta, factual review, deterministic tests,
continuity evidence, acceptance and closeout artifacts. It may inspect current
source but may not edit `app/**`, `docs/diary/**`, API Spine schemas, migrations
or product tests.

Its acceptance must:

1. compare exact general status, waiting-area and A5.1 check-in request,
   confirmation, authority, freshness, idempotency, mutation, audit, event,
   receipt and readback contracts;
2. identify reusable deterministic kernel versus A5.1-only gate/provenance;
3. classify the static grammar and route-contract statements as correct,
   superseded or scope-qualified without editing them;
4. reconcile the exact `{appointment_id}` versus `{appointment_id:uuid}`
   route-contract spelling and its literal-route shadow check;
5. choose one canonical product-facing arrival meaning or a strict justified
   non-overlap;
6. freeze the smallest later architecture/implementation tranche; and
7. keep the A5.1 runtime default-off, uncalled and unmodified.

## Alternatives retained

- **Direct Reception One check-in or waiting-area composition:** premature
  until the overlapping semantic surfaces are reconciled.
- **Link-patient action:** identity-sensitive and lacks a signed command family;
  it is not the next dependency-satisfied slice.
- **External patient channel/delegation:** a separate future programme gate.
- **Another Diary event family or operational durability:** does not resolve
  the current command-authority inconsistency and remains separately bounded.
- **General visual polish:** lower architecture leverage at this point.

## API Spine finding

- Boundary classification: mutating appointment arrival/status command-family
  and first-party adapter consistency.
- Accepted invariant: presentation may vary, but intent, confirmation,
  current-authority/source recheck, idempotency, atomic effects, audit, receipt
  and fresh readback may not.
- Events remain acceleration hints and cannot make A5.1 or `Arrived` current
  truth without an authoritative read.
- GraphQL remains read-only; no raw compatibility write becomes canonical.
- Open Yuri decision: none. A read-only convergence review is the narrowest
  fail-closed descendant and does not choose product admission by itself.

## Parallelism efficacy

Sol retained the coupled semantic inventory and selection. DeepSeek remained
declined because no separable mechanical implementation existed. The matrix
freezes material architecture meaning, so Gemini 3.7 Flash/high is required for
one fresh exact-candidate read-only veto after deterministic admission. Native
subagents remained declined under current developer policy.

## Claim boundary

This orientation proves repository facts and selects a later read-only review.
It does not prove a live route/database outcome, general A5.1 admission,
product usability, external-adapter conformance or production readiness.

No product/backend/API/OpenAPI/GraphQL/schema/service/migration/database source,
raw compatibility behavior, feature flag, live route/source/watcher, provider,
product/patient/clinical/historical data, deployment, release, Pages or
protected ref changed. `docs/branding/` and every unrelated untracked file
remain preserved.
