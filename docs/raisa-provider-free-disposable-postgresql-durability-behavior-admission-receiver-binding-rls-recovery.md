# Provider-free durability admission-receiver binding-RLS recovery

Date: 2026-08-10

Status: bounded structural recovery candidate; behavior runtime remains closed

## Observed failure and exact diagnosis

Behavior attempt 031 stopped safely at `BTR-E03` with PostgreSQL `CF004` in
`admit_proofread_observation_v1`, completed zero of the frozen twenty
scenarios and removed its exact owned container with absence verified. The
immutable failure is
`provider-free-behavior-transaction-failure-evidence-031.json`.

No additional PostgreSQL run was needed. Exact source mapping proves that the
admission body performs an `EXACTLY_ONE` read of
`context_service_practice_binding` and stores the observer binding revision.
The body is deliberately `SECURITY DEFINER` under the distinct non-login
`context_admission_receiver`, which already has the accepted exact table
`SELECT`. Forced RLS nevertheless admits a binding row only while
`current_user = context_schema_owner`. Inside the admission body,
`current_user` is the receiver, so PostgreSQL hides the otherwise exact
`database_login = session_user` row and the strict lookup fails closed as
`CF004`.

This reconciles all observed facts: the support-function execute-grant defect
is gone, the admission call starts, the binding row is seeded and session-bound,
the receiver has direct `SELECT`, and no scenario effect is released.

## Minimum architecture-strengthening repair

Change only `pol_cf_17_select` so its `current_user` allowlist contains exactly
the two existing non-login function owners that legitimately evaluate binding
rows: `context_schema_owner` and `context_admission_receiver`.

The policy must retain all existing fences:

- `database_login = session_user`;
- the transaction-time active interval;
- forced RLS and `SELECT TO PUBLIC` as policy applicability, with table
  privileges still independently required; and
- no write check because the binding relation remains read-only to runtime
  functions.

No role, membership, login, `BYPASSRLS`, direct grant, body program, entry
point, scenario, fixture or command authority changes. Moving the admission
function to `context_schema_owner` is rejected because it would erase the
accepted privilege separation. Granting the receiver RLS bypass or admitting
a runtime login as `current_user` is also rejected.

## Required descendant proof

Before another behavior attempt, the corrected structural contract/schema
must reject missing receiver visibility, extra owners and loss of either the
session-user or active-time fence. The unchanged typed body must be rebound to
the new parent, the inert artifact regenerated and recognized, fresh
PostgreSQL parse/catalogue characterization and distinct exact reproduction
must pass, and the unchanged twenty-scenario behavior contract must receive a
fresh exact-HEAD Gemini 3.6 Flash/high veto.

Attempt 031 remains immutable. The mutable accepted behavior evidence remains
restored and unstaged.

## Claim and authority boundary

This recovery restores only the exact binding read already granted to the
accepted admission receiver. It grants no applied migration, operational
database or credentials, source/watcher/listener/feed, product/patient/
clinical data, provider, application/API/Diary wiring, command/write,
deployment, production, release, Pages or protected-ref authority.
