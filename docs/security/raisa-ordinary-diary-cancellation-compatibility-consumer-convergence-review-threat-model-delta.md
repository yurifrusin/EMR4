# Threat-model delta — ordinary Diary cancellation compatibility-consumer convergence review

Date: 2026-08-17

Timestamp: 2026-08-17T17:09:51.0737699+10:00 (Australia/Brisbane)

Status: `frozen_for_repository_static_execution`

## Boundary

This is a provider-free repository-static review. It reads only committed,
non-protected cancellation-client and API-contract source and authors review
evidence. It invokes no route, database, source watcher, provider or command.

## Threats under review

| Threat | Current concern | Required later disposition |
|---|---|---|
| Semantic downgrade | A delete-proposal 404 may route cancellation through status-confirm. | No fallback; canonical delete-only or fail closed. |
| Reason loss | Status fallback omits free-text cancellation reason. | Preserve the exact structured reason and optional bounded note in one delete command. |
| Response confusion | The ordinary dispatcher expects an appointment read model while canonical confirm returns a minimal public receipt. | Recursively validate the public envelope and never require or expose an appointment object. |
| Endpoint widening | The dispatcher admits status-confirm and delete aliases. | The converged consumer admits only canonical `/appointments/proposals/delete/confirm`. |
| Proposal substitution | Current ordinary code does not fully bind proposal identity and reasons before display/confirm. | Validate exact appointment, command, reasons, warnings, blocks and endpoint before confirmation. |
| Unknown commit | Transport or response validation can fail after the backend committed. | Make no commit/non-commit claim until a fresh scoped read reconciles current truth. |
| Optimistic display | Local removal or retained stale state may stand in for source truth. | No optimistic product mutation; every terminal/uncertain outcome requires fresh reconciliation. |

## Preserved controls

- Backend-authenticated practice/actor authority and delete proposal evidence.
- Visible human confirmation.
- Canonical delete-confirm transaction, idempotency, audit, current-authority
  and source-truth recheck.
- Strict minimal public receipt and fresh authorised read.
- Adapter-neutral rule: clients may vary presentation but not command meaning,
  warnings, confirmation, authority, effects, receipt or reconciliation.

## Closed surfaces

No product or API source changes, HTTP calls, database access, real data,
provider/ADC, credentials/IAM, external network, deployment, production,
release, Pages or protected refs. Raw compatibility delete and status fallback
remain observed but uncalled. Protected evidence and `docs/branding/` remain
untouched.
