# Sprint 158 - Confirm Client Surface Checkpoint

## Summary

Sprints 153-157 closed the practical Diary client-header gap for the ordinary
appointment proposal/confirmation loop. The frontend now emits HTTP
`Idempotency-Key` headers for create-proposal and for the ordinary signed
confirm routes used by create, Bernie create, update, status, and delete flows.

This checkpoint does not change runtime behaviour. It records which surfaces are
ready, which remaining client-header gap still affects a user-clickable Bernie
path, and which idempotency topics should stay separate.

## Current Surface

| Surface | Backend posture | Diary client posture | Checkpoint result |
|---|---|---|---|
| Create proposal | Header syntactically required; deterministic re-evaluation, no proposal ledger | `saveBooking()` sends a modal-scoped `Idempotency-Key` | Covered |
| Staff create confirm | Confirmation ledger enforced | `saveBooking()` sends a distinct modal confirm key | Covered |
| Bernie create confirm | Confirmation ledger enforced | Bernie review confirm adapter sends a stable server-route/session key | Covered for create booking review |
| Ordinary update confirm | Confirmation ledger enforced | Edit-modal and drag/reschedule callers send `update-confirm-<freshness>` | Covered |
| Status confirm | Confirmation ledger enforced | `applySignedStatusProposal()` sends `status-confirm-<freshness>` | Covered |
| Delete confirm | Confirmation ledger enforced | `applySignedDeleteProposal()` sends `delete-confirm-<freshness>` | Covered |
| Bernie tool-intent update confirm | Same update-confirm backend route is enforced | `confirmBernieToolIntentChange()` remains header-free | Next fix |
| Proposal-only update/status/waiting-area/delete | OpenAPI declares proposal-command idempotency, but FastAPI binding is not wired | Client proposal-only headers remain mostly unwired except create-proposal | Deferred, broader |
| Strict `minLength: 8` runtime enforcement | OpenAPI documents the stricter shape | Runtime enforcement remains blank/non-blank only | Deferred, compatibility hardening |

## Decision

Sprint 158 recommends **not** using the next sprint on strict `minLength: 8`
runtime enforcement or proposal-only backend binding.

Rationale:

- Strict `minLength: 8` is now more plausible because the known Diary-generated
  keys are long enough, but enforcing it before a product review buys little
  user-visible confidence.
- Proposal-only binding touches multiple routes and should be handled as a
  backend/API-spine slice, not folded into client-confirm readiness.
- Bernie tool-intent update confirm is isolated, but it posts to the same
  already-enforced update-confirm backend route as ordinary update confirm.
  Without an HTTP `Idempotency-Key`, a real non-intercepted click can fail before
  the backend sees the signed update evidence.

## Recommendation

The next sprint should fix the Bernie tool-intent update-confirm header before a
meaningful integrated Bernie/Diary review.

Recommended Sprint 159:

- wire `confirmBernieToolIntentChange()` to send an HTTP `Idempotency-Key`;
- prefer a freshness-derived key from `update_proposal_freshness_id`, matching
  the ordinary update-confirm key strategy unless implementation review finds a
  stronger Bernie server-session discriminator requirement;
- add route-intercepted smoke coverage that captures the header on the
  tool-intent confirm click.

Recommended Sprint 160:

- produce a compact Bernie/Diary review-readiness packet;
- run the existing provider-boundary/readiness commands required by
  `orchestration/bernie_release_gates.md`;
- verify the ordinary create-booking path remains route-intercepted and
  staff-confirmed;
- define exactly what Yuri should run and what evidence would count as useful
  feedback.

Pause for Yuri after the Sprint 160 packet if the release/readiness checks are
clean. Proposal-only binding and strict `minLength: 8` enforcement can follow
after product feedback unless a review check reveals another route/header
failure.

## Gates Kept Closed

This checkpoint does not open:

- live provider enablement;
- runtime memory/RAG/GraphRAG wiring;
- H15/H-series runtime imports;
- broad historical diary material access;
- GraphQL mutations;
- raw compatibility write idempotency changes;
- backend idempotency ledger changes.
