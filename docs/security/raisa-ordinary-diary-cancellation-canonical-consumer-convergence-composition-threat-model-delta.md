# Threat-model delta — ordinary Diary canonical cancellation consumer convergence composition

Date: 2026-08-17

Timestamp: 2026-08-17T20:46:15.7583144+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_client_only_execution`

## Boundary

This tranche changes only the first-party ordinary Diary cancellation consumer
and focused authored-synthetic tests. The accepted backend delete proposal,
canonical confirm transaction, authority, audit, idempotency and strict public
receipt remain read-only controls.

## Threats and controls

| Threat | Required control |
|---|---|
| Semantic downgrade | A delete failure, including 404, never calls status proposal/confirm or raw `DELETE`. |
| Proposal substitution | One shared validator binds appointment, reason, optional note, warnings, blocks, tier and canonical endpoint before confirmation. |
| Confirmation bypass | The existing visible destructive-intent step and explicit proposal confirmation remain mandatory. |
| Endpoint widening | Confirmation posts only to normalized `/appointments/proposals/delete/confirm`; the compatibility alias is not admitted. |
| Receipt widening/private leakage | Only the recursively closed minimal public envelope and receipt validate; no appointment read model or private receipt field is retained. |
| Unknown commit | Transport, HTTP and response-validation uncertainty make no claim until a fresh authorised Diary read completes. |
| Stale or optimistic display | No local appointment removal proves success; every terminal/uncertain path reconciles from the scoped read. |
| Receipt/read contradiction | Current read truth wins display; contradiction is not labelled successful and remains visibly reviewable. |
| Reconciliation failure | Cancellation enters explicit `refresh-required`, stays disabled and makes no success/non-commit claim. |
| Smoke-fixture overclaim | Canonical cancellation browser evidence is route-intercepted and labelled as such; built-in smoke state does not impersonate source truth. |

## Preserved backend controls

- authenticated actor and practice scope;
- dedicated delete proposal with current source evidence;
- signed confirmation evidence and visible staff confirmation;
- current-authority/source-truth recheck inside the mutation transaction;
- delete-specific idempotency, audit and private receipt;
- strict patient-free public receipt; and
- subsequent authorised scoped read.

## Closed surfaces

No backend/API/OpenAPI/GraphQL/schema/service/migration/database change, real
route/database call, provider/ADC, credential/IAM, patient/product/clinical/
historical/protected data, external patient client, deployment, production,
release, Pages or protected ref is opened. `docs/branding/` and unrelated
untracked files remain untouched.
