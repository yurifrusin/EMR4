# Antigravity Sprint 148 Create-Proposal Idempotency Acceptance Packet

| Item | Value |
|---|---|
| Sprint | 148 |
| Lane | Antigravity acceptance packet |
| Status | Queued for bounded review |

## Product/UX Acceptance Frame

Sprint 148 should not change receptionist-visible create-proposal behavior. It
only defines future backend route-test expectations.

## Acceptance Criteria

- `POST /api/v1/appointments/proposals/create` still produces proposal
  envelopes as before.
- No create-proposal route requires `Idempotency-Key` yet.
- No appointment, audit, slot reservation, or confirmation-ledger behavior
  changes.
- Future tests preserve staff confirmation, signed evidence, freshness, and the
  already-wired confirmation ledger.
- Raw compatibility writes and other proposal families remain out of scope.
