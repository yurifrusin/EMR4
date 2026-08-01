# Reception One Bureau explicit-selection retry-readiness plan

Status: provider-free authorised maintenance
Recorded: 2026-07-31
Predecessor: `reception-one-bureau-live-isolated-planner-evaluation`

## Diagnosis inherited

The closed occupied predecessor consumed its one provider call and released
nothing. The frame recorded `selected_appointment_absent`; the model reasonably
asked which appointment to resize, while the proofreader required the
recognized `resize` intent.

The existing provider-free extended-proposal harness already demonstrates the
correct interaction: bind the exact disposable appointment into the synthetic
projection, click it, verify it is selected, and only then submit the resize.

## Objective

Produce a fresh non-intercepted browser/FastAPI/PostgreSQL proof for only the
45-minute resize:

1. use an exact disposable authored-synthetic database;
2. bind its Margaret Thompson / Dr Alex Shera appointment to the smoke
   projection through the existing test-only parameter;
3. click the appointment row visibly;
4. require `aria-selected=true` before submission;
5. submit the same natural-language resize using the default deterministic
   planner;
6. require proofreader admission and the existing proposal-only adapter;
7. require zero provider calls and zero credential reads;
8. retain only boolean selection proof and hashes, not the raw appointment
   identifier; and
9. prove database, process, port and temporary-runtime cleanup.

## Boundaries

This tranche opens no provider call, model runtime, product write,
confirmation, real data, production, deployment or release. It changes no API
schema and no application authority. It may add or repair repository-local
acceptance scripts and tests.

Provider-key variables are not inspected and are omitted from child
environments. The deterministic provider-free path must remain the default.

## Acceptance

Pass only if:

- the exact appointment row becomes selected before submission;
- one authenticated compose request is observed without interception;
- `planner_mode=deterministic`;
- `goal=resize`;
- `proposed_duration_minutes=45`;
- the deterministic proofreader admits;
- the update proposal adapter passes freshness;
- confirmation remains required;
- no write or confirmation occurs;
- provider calls and credential reads are zero;
- database truth is unchanged; and
- cleanup and independent residue checks pass.

On pass, the next occupied step remains blocked pending fresh authority. The
failed predecessor and consumed ledger remain immutable.
