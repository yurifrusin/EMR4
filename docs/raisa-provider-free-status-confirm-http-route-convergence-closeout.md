# Provider-free status-confirm HTTP route convergence closeout

Date: 2026-08-13

Timestamp: 2026-08-13T13:09:24+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `b414eb256853c301099d9cf7797a69cd3ec077c5`

Result: `raisa_provider_free_status_confirm_http_route_convergence_pass`

## Outcome

The authenticated appointment status-confirm family now has one backend-owned
write path. `POST /api/v1/appointments/proposals/status/confirm` is canonical;
the historical `/api/v1/appointments/proposals/status-confirm` spelling is a
hidden compatibility alias over the same handler. The prior route-local claim,
mutation, audit, receipt and commit implementation has been removed.

The proposal endpoint mints an opaque HMAC-bound database generation after
reading the positive database-owned `appointment_state_version`. Confirmation
carries that object without gaining authority to select or advance a version.
The product adapter verifies signed evidence and the binding, opens a distinct
command session, rechecks current authority and source truth under the accepted
ordered transaction, and atomically commits status, audit and v1 receipt.
Initial success and completed replay both return the exact canonical bytes held
by the private receipt.

Status-only admission is preserved. A waiting-area-only proposal sent to
either spelling receives `unsupported_status_confirm_variant`; there is no
fallback to the removed local write. The raw legacy PATCH compatibility route
and every other command family are unchanged.

## Evidence

- All twelve frozen HTTP/PostgreSQL scenarios pass under a restricted
  authored-synthetic application role and forced five-table RLS.
- All 112 hostile contract mutations fail closed.
- The combined focused/current-lineage packet passes 217/217 tests.
- The canonical `fast` profile passes 193/193 tests, Ruff, in-memory
  compilation of 209 maintained Python files without protected-path
  enumeration, Diary JavaScript syntax and Git whitespace.
- Exact owned container, internal network, relay, synthetic-row and temporary
  artifact cleanup passes. No provider, ADC, external service, product
  database or patient/clinical data was used.

The released evidence is
`orchestration/continuity/raisa-provider-free-status-confirm-http-route-convergence/provider-free-http-postgresql-evidence.json`.
The latest sanitized rejected-run evidence remains preserved separately; it
contains no credentials, tokens, request/response bodies, SQL or synthetic row
values.

## Rehearsal recoveries

The first disposable run exposed two missing zero-row projection tables in the
predecessor scaffold. The second exposed a one-connection test pool that could
not represent the intentionally separate authenticated request and command
sessions. The exact repair added empty patient/appointment-type projections
and a two-connection bounded pool. The third and final run passed without
altering the accepted adapter or physical transaction contract.

The wider regression pass also found historical tests that still assigned
status-confirm ownership to the route-local idempotency helper. Their narrow
repairs now assert adapter ownership, canonical UUID route discrimination,
required binding carriage and the closed waiting-area write boundary.

## Claim boundary and next work

This proves authored-synthetic local HTTP convergence for one status-confirm
family. It does not prove visible Diary behavior, another command family,
durable event/cue delivery, restart or unknown-commit recovery, performance,
deployment or production.

The next dependency-satisfied tranche is visible native Diary status-confirm
wiring against this exact route contract. CF-D2 remains preserved but deferred:
the command already rechecks current authority and database truth atomically,
and the visible interaction boundary should now define the cues and
reconciliation behavior that a later observability-first durability extension
must prove. No watcher retry is opened by this closeout.

After the task-branch closeout push, Yuri requested a pause before the visible
Diary tranche begins. That tranche is unstarted and resumes only on explicit
go-ahead.

Patient/clinical and operational product data, providers, credentials/IAM,
external network, deployment, production, release, Pages and protected refs
remain closed. `docs/branding/` and every unrelated untracked file remain
preserved.
