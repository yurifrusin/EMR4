# Threat-model delta — waiting-area movement command-family readiness review

Date: 2026-08-24

Timestamp: 2026-08-24T18:44:13.5010595+10:00 (Australia/Brisbane)

Status: frozen

`implementation_authorized: false`

| Threat | Required control |
|---|---|
| Existing proposal shape is mistaken for write authority | Classify proposal preparation separately from a family-owned confirmation transaction. |
| Waiting-area input widens status-confirm authority | Preserve the accepted `unsupported_status_confirm_variant` boundary and require a distinct operation and route family. |
| Waiting-area movement becomes an alternate check-in | Require status and arrival state to remain unchanged; check-in retains the only combined `Booked -> Arrived` plus initial-area assignment. |
| Check-in becomes a hidden move command | Preserve `waiting_area_move_not_supported` when check-in sees an existing area. |
| A stale or inactive destination is applied | Require confirmation-time locked current-truth and active-area revalidation within the appointment's practice/location boundary. |
| Route-local mutation bypasses atomic command receipts | Require one family-owned transaction for mutation, attributable audit, idempotency and canonical stored response. |
| Status-only private receipts are relabelled for waiting-area use | Treat hard-coded status operation, route family and receipt constraints as blockers until an explicit sibling contract is accepted. |
| Client smoke-mode behavior is mistaken for backend convergence | Bind the real-mode Diary flow separately and record its current fail-closed status-confirm rejection. |
| An event becomes command authority | Keep events post-commit, non-actuating cues; a dedicated waiting-state event contract remains a later decision. |
| Read-only review accesses historical diary material | Bind only the sixteen repository sources and perform no trove read or runtime execution. |

No product, patient, clinical, provider, credential, network, deployment,
release, Pages or protected-ref authority is opened.
