# Sprint R9 — Status/Delete Route Governance Inventory

This inventory classifies appointment status and delete/cancellation routes. It deliberately excludes slot-writing create/update/reschedule routes, which are covered by `docs/receptionist_review_r7_route_inventory.md` and `docs/receptionist_review_r8_confirm_inventory.md`.

## Route Inventory

| Method | Path | Handler | Type | Temporal policy |
|---|---|---|---|---|
| `POST` | `/api/v1/appointments/proposals/status/{appointment_id}` | `propose_status_update` | Non-mutating status proposal | Exempt; no slot write |
| `POST` | `/api/v1/appointments/proposals/status-confirm` | `confirm_status_proposal_route` | Signed status confirm | Exempt; no slot write |
| `PATCH` | `/api/v1/appointments/{appointment_id}/status` | `update_appointment_status` | Legacy direct status write | Exempt; no slot write |
| `POST` | `/api/v1/appointments/proposals/delete/{appointment_id}` | `propose_delete_appointment` | Non-mutating delete proposal | Exempt; no slot write |
| `POST` | `/api/v1/appointments/proposals/delete-confirm` | `confirm_delete_proposal_route` | Signed delete confirm | Exempt; no slot write |
| `DELETE` | `/api/v1/appointments/{appointment_id}` | `cancel_appointment` | Legacy direct soft-cancel | Exempt; no slot write |

## Safeguard Chains

### Status Proposal/Confirm

- `propose_status_update` blocks `already_in_status`, warns on unusual terminal-state changes, and records waiting-area side effects.
- `confirm_status_proposal_route` requires `confirmed=true`, verifies proposal safety, recomputes status proposal freshness from current appointment state, verifies signed evidence, rechecks waiting-area existence when supplied, and writes through `_apply_appointment_status_update`.
- Successful status confirms record bounded audit evidence including `diary_confirm_status_proposal` and `status_signed_confirmation_evidence_verified`.

### Delete Proposal/Confirm

- `propose_delete_appointment` blocks appointments already `Cancelled`, warns when the waiting-area assignment will be cleared, and carries optional `cancellation_reason`.
- `confirm_delete_proposal_route` requires `confirmed=true`, recomputes delete freshness from current appointment state, verifies signed evidence, checks waiting-area staleness, and writes through `_apply_appointment_delete`.
- Successful delete confirms soft-cancel the appointment, clear waiting-area assignment, persist cancellation reason, and record `diary_confirm_delete_proposal` plus `delete_signed_confirmation_evidence_verified`.

### Legacy Direct Routes

- `update_appointment_status` and `cancel_appointment` preserve raw compatibility and write through shared apply helpers with `raw_compat_*` audit evidence.
- They do not run the proposal-confirm freshness or signed-evidence chain, so new UI work should prefer proposal-confirm routes.

## Current Coverage And Gaps

- Existing tests cover auth, cross-practice isolation, valid/invalid status values, delete soft-cancel behaviour, waiting-area side effects, signed confirm evidence, stale freshness, and audit-log creation.
- R9 adds explicit retrospective-boundary tests proving status/delete past-date operations stay allowed while stale/tampered confirmations still write nothing.
- Future governance work can consider structured cancellation reason codes and stricter UX routing away from raw compatibility endpoints, without adding temporal slot-write blocks to status/delete paths.
