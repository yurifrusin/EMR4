# API Spine Appointment Idempotency - Status/Delete Confirm Client Header

| Item | Value |
|---|---|
| Sprint | 156 |
| Programme | Programme 2G / EMR4 API Spine |
| Classification | Client header emission for already-enforced status/delete confirmation routes |
| Runtime backend behavior changed | No |
| Decision | Wire status-confirm and delete-confirm client headers; defer update-confirm, Bernie tool-intent confirm, proposal-only binding, and strict length enforcement |

## Context

Sprint 155 wired the create-confirm client header path. Sprint 156 extends the
same client-readiness work to the two dedicated status/delete confirmation
helpers without changing backend route behavior or idempotency ledger semantics.

## Implemented Client Posture

| Caller | Endpoint family | Header source |
|---|---|---|
| `applySignedStatusProposal` | `/appointments/proposals/status-confirm` | `status-confirm-` plus `status_proposal_freshness_id`, falling back to a proposal-scoped generated key only if freshness is missing or too long |
| `applySignedDeleteProposal` | `/appointments/proposals/delete-confirm` | `delete-confirm-` plus `delete_proposal_freshness_id`, falling back to a proposal-scoped generated key only if freshness is missing or too long |

The freshness-derived key is stable for the same server-prepared proposal and
keeps retries on the existing confirmation ledger replay path. Raw compatibility
fallback branches remain header-free.

## Deferred Gaps

- update-confirm client header emission, including modal update and
  drag/reschedule update-confirm call sites;
- Bernie tool-intent confirm header emission;
- proposal-only backend header binding for update/status/waiting-area/delete;
- raw compatibility write idempotency;
- strict runtime `minLength: 8` enforcement.

## Closed Gates

This sprint does not change backend route behavior, OpenAPI schema, idempotency
ledger semantics, provider calls, GraphQL mutations, H15/H-series runtime
imports, memory/RAG/GraphRAG runtime wiring, or broad historical diary trove
access.

## Next Step

Sprint 157 should address update-confirm client header emission as the last
ordinary Diary confirm-family client gap before returning to proposal-only
backend binding or strict `minLength: 8` enforcement.
