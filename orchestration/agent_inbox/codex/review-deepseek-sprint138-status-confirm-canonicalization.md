# DeepSeek Review - Sprint 138 Status-Confirm Canonicalization

| Item | Value |
|---|---|
| Sprint | 138 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Accepted for Sprint 138 wiring |

## Recommendation

Proceed with full validated confirmation-body hashing for
`status-confirm`.

DeepSeek reviewed the Sprint 137 metadata-exclusion suggestion against the
current storage design, the appointment idempotency helper, and existing wired
create-confirm routes. The accepted Sprint 138 decision is:

- use `AppointmentStatusProposalConfirmationIn.model_dump(mode="json")` as the
  `request_body` passed to `claim_appointment_command`;
- do not special-case `_STATUS_CONFIRM_METADATA_FIELDS` in the idempotency
  hash;
- treat metadata-field exclusion as a future cross-route canonicalization
  version change, not a one-off status-confirm behavior.

## Rationale

- Staff create-confirm and Bernie create-confirm already hash the full
  validated confirmation body.
- Storage version `1` is already defined as deterministic hashing of the typed
  request body, excluding only transient request metadata such as correlation
  ids and including confirmation payload fields that the write depends on.
- A same-key request with different signed evidence or freshness metadata is a
  different request body under the current policy and should fail closed with
  `idempotency_key_conflict`.
- Excluding metadata for only status-confirm would create a route-specific
  canonicalization policy and should require a deliberate versioned change.

## Integrated Result

Sprint 138 wired only
`POST /api/v1/appointments/proposals/status-confirm` with full-body hashing,
a status-confirm route family, a no-early-commit path through
`_apply_appointment_status_update(..., commit=False)`, and executable replay/
conflict/in-progress/stale/failed route tests.

No update-confirm, delete-confirm, raw compatibility, proposal-only, provider,
GraphQL, H15/H-series, memory/RAG/GraphRAG, runtime FGA, external patient
client, or broad trove behavior was changed.
