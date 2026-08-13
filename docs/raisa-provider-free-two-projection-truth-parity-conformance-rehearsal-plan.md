# Provider-free two-projection truth-parity conformance rehearsal plan

Date: 2026-08-13

Timestamp: 2026-08-13T23:52:49+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_execution`

Task baseline: `fbb2fd1822f73b2469fc774eb001af31dfdfa85b`

Target result: `raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_pass`

Reasoning level: Extra High. This plan freezes the first executable
projection-neutral definition of Diary truth parity. Execution is a small
deterministic browser/evidence task and remains Sol-owned.

## Objective

Prove that the conventional grid and Reception One preserve the same
kernel-owned meaning for the already accepted appointment-status interaction,
despite using different visual and semantic grammars.

This tranche proves truth parity, not feature parity. It adds no command and
changes neither renderer. It records an evidence-only `ProjectionTruthTrace`
for exactly two renderers and compares only fields whose meaning belongs to the
kernel. Layout, wording, focus target and local projection history remain
renderer-owned presentation details.

## Exact exercised surface

- Renderers: exactly `conventional_grid` and `reception_one`.
- Command family: the existing appointment-status proposal/confirm family.
- Starting status: `Booked` for one newly authored synthetic appointment.
- Requested statuses: only existing values already exposed by
  `appointmentStatusOptions`.
- Evidence mode: `route_intercepted_browser`, using the ordinary Diary page and
  its actual checked-in JavaScript without product source modification.
- Network boundary: intercepted authored-synthetic `/api/v1/**` fixtures only;
  no real backend, database, provider or external network.

## Closed trace contract

Each trace must contain exactly:

1. `renderer` and `scenario`;
2. a selected-current coordinate containing the authored-synthetic practice,
   appointment id, observed status and requested existing status;
3. normalized proposal and confirmation outcomes;
4. normalized kernel result;
5. normalized current-truth result and displayed terminal status;
6. exact proposal, confirm and raw-compatibility request counts; and
7. renderer-local layout, wording, focus and history observations that are
   recorded but excluded from kernel equality.

The trace is immutable evidence vocabulary only. It is not a runtime session
object, product event, API model, database row, analytics record, audit record,
transcript or source of truth.

## Frozen scenarios

Run one paired trace for each outcome:

1. `safe`: `Arrived`, safe proposal, no staff dialog, one signed confirm and
   committed current truth;
2. `cancelled`: terminal `Cancelled` proposal, explicit staff cancellation,
   zero confirm and unchanged current truth;
3. `blocked`: blocked proposal, no confirm action and unchanged current truth;
4. `stale`: safe proposal followed by a stale/current-truth confirm rejection,
   no commit and unchanged current truth;
5. `failed`: proposal transport failure, no confirm, no fallback and unchanged
   current truth; and
6. `committed`: terminal `Completed` proposal, explicit staff confirmation,
   one signed confirm and committed current truth.

For every renderer/scenario pair, the normalized selected-current coordinate,
proposal outcome, confirmation outcome, kernel result, current-truth status,
displayed terminal status and exact command-route counts must agree. Raw
compatibility writes must remain zero. The harness must reject any missing
renderer/scenario, duplicate trace, unknown field, unknown enum, second command
path, optimistic-current claim or kernel-field mismatch.

## Acceptance

The tranche passes only if:

1. all twelve route-intercepted browser scenarios exercise visible ordinary
   grid or Reception One controls through the existing interaction;
2. both renderers produce one complete trace for every frozen scenario;
3. paired kernel fields are byte-for-byte equal after deterministic
   normalization;
4. committed traces show the requested status in fixture truth and displayed
   state, while every non-commit trace preserves `Booked`;
5. route counts are exact, raw compatibility writes are zero and no unexpected
   mutation route is called;
6. local presentation fields may differ without weakening kernel equality;
7. the schema, committed evidence and source guards prove the trace cannot be
   mistaken for runtime/API/database/audit authority;
8. focused browser, schema, plan, API Spine/latch/baton and canonical fast
   checks pass; and
9. the closeout states the evidence label and smallest truthful claim.

## Recovery and stop

Correct mechanical fixture, selector, trace normalization, schema, evidence or
test defects inside this frozen boundary and rerun affected deterministic
checks. Do not repair product behavior inside this evidence-only tranche. If
the two existing renderers actually disagree on a kernel field, preserve the
failure and stop for a separately bounded product repair; do not normalize the
difference away.

## Closed surfaces

No product JavaScript/CSS/HTML, runtime session object, FastAPI, Pydantic,
GraphQL, OpenAPI, database/migration/RLS, analytics, audit, transcript, event or
watcher runtime, product/patient/clinical data, historical Diary/PHI, external
patient channel, another command or event family, provider/ADC, credential/
IAM/network access, executable tool, deployment, production, release, Pages or
protected-ref action is authorised. Preserve `docs/branding/` and every
unrelated untracked file; use explicit-path staging only.
