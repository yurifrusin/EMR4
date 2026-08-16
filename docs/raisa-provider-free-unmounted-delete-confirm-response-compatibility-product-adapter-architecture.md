# Provider-free unmounted delete-confirm response-compatibility and product-adapter architecture

Date: 2026-08-16

Timestamp: 2026-08-16T16:33:54.6870685+10:00 (Australia/Brisbane)

Status: `frozen_candidate`

Source: `f0c98682568784441991b080681f9beb3b9354c2`

## Architectural decision

Delete-confirm adopts a two-layer response architecture:

```text
authenticated server state + returned opaque proposal evidence
                         |
                         v
             pre-command fail-closed admission
                         |
                         v
     authority-first locked physical transaction seam
                         |
          +--------------+--------------+
          |                             |
     new command                       replay
          |                             |
 appointment + audit +          validate existing six-field
 six-field private receipt       private receipt, no effect
          |                             |
          +--------------+--------------+
                         |
                         v
       versioned pure public-envelope projection
                         |
                         v
        identical canonical HTTP bytes on first/retry
```

The stored six-field receipt is command truth. The public response is a
deterministic delivery projection. Neither is a current appointment read model.

## Private command receipt v1

The accepted physical byte sequence remains unchanged and ordered:

1. `appointment_id`;
2. `status` (`Cancelled`);
3. `status_reason_code`;
4. `cancellation_reason`;
5. `waiting_area_id` (`null`); and
6. `warning_codes`.

It remains the only persisted response authority. It is integrity-bound to the
actor, practice, role, session, authority generation, operation, route, target,
request, pre/post version and audit through the accepted physical transaction.

## Public envelope v1

The complete success envelope is exactly:

```json
{
  "audit_evidence": [
    "delete_product_adapter_v1",
    "delete_signed_confirmation_evidence_verified",
    "delete_current_authority_rechecked"
  ],
  "autonomy_tier": "confirmed_write",
  "blocks": [],
  "intent": "confirm_delete_appointment",
  "receipt": {
    "appointment_id": "<uuid>",
    "cancellation_reason": null,
    "schema_version": "appointment.delete_confirmation_receipt.v1",
    "status": "Cancelled",
    "status_reason_code": "<dedicated-code>",
    "waiting_area_id": null,
    "warning_codes": []
  },
  "requires_confirmation": false,
  "safe": true,
  "schema_version": "raisa.delete_confirm_public_envelope.v1",
  "summary": "Confirmed delete proposal and cancelled one appointment.",
  "warnings": []
}
```

Keys are serialized with sorted-key compact UTF-8 JSON. Warning entries are
pure registry projections from the stored codes. V1 admits only:

```json
{
  "waiting_area_cleared": {
    "code": "waiting_area_cleared",
    "severity": "warning",
    "message": "Deleting this appointment will remove the patient from the waiting area."
  }
}
```

Unknown, duplicate or out-of-order warning codes fail closed. The stored
private `warning_codes` order is canonical sorted order. The public envelope
does not contain `appointment`, `AppointmentOut`, patient, practitioner,
schedule, reason, notes, audit identity or live database projection.

## Why the current full appointment response is retired

The current development handler persists and returns a larger mutable
`AppointmentOut`. Exact replay would either duplicate patient and operational
data indefinitely in an idempotency receipt or reconstruct a different body
from later database truth. Both are architecturally unsound. A cancellation
command needs a stable receipt, while Reception One can refresh its ordinary
read projection separately after success.

Therefore a future route transition must move delete-confirm success to this
minimal receipt envelope on both canonical and compatibility aliases. There is
no dual-mode success response and no silent conversion of the private receipt
into a larger appointment object.

## Server-owned authority packet

The application-owned adapter constructs, but cannot grant effect authority
to, one packet containing:

- constant operation and route family;
- server-loaded practice, actor and role;
- server-loaded positive `authority_generation`;
- a domain-separated HMAC of the authenticated bearer token, actor and practice;
- exact idempotency key and canonical request digest;
- target appointment ID and delete command;
- verified evidence purpose/binding;
- verified positive proposal source version; and
- canonical warning codes.

The packet contains `effect_authority: false`. It never contains a client-
selected capability. The physical seam alone enforces constant
`appointment.cancel.confirm` and repeats the current actor/generation/grant
check twice while locks are held.

## Proposal and lock protocol

The proposal later mints
`raisa.delete_proposal_version_binding.v1`, an HMAC over exactly:

- `source_version`; and
- the signed confirmation evidence signature.

The binding is returned opaque. Pre-command admission verifies its shape,
signature and match to the signed evidence. The physical transaction locks the
user, target appointment and idempotency record in its accepted order. Locked
admission then rebuilds current state from the locked appointment and requires:

- same practice, actor and target;
- same positive appointment source version;
- same status and not already `Cancelled`;
- same waiting-area state and `clears_waiting_area` value;
- same reason and cancellation text command;
- same freshness digest and signed evidence purpose/binding; and
- exact warning acknowledgement.

No unlocked proposal read is promoted into effect authority.

## Composition outcomes

- `new_command`: stage cancellation, attributable audit and private receipt;
  allow the physical seam to validate all three before commit; project public
  bytes from the validated private bytes.
- `replay`: validate private bytes/digest/JSON and project the same public
  bytes; do not read later appointment fields or write.
- `conflict`, `legacy_receipt_not_replayable`,
  `in_progress_not_replayable`, `receipt_integrity_failure`: return only their
  closed mapped status/code; never expose a partial receipt.
- target, authority, wait-budget, scaffold or projection exceptions: roll back
  and map to non-sensitive 404, 403 or 503 outcomes.

## Boundary

This architecture is provider-free, unmounted and source-only. It proves no
adapter implementation, ORM/schema change, route behavior, HTTP serialization,
database transaction, capability provisioning, client compatibility,
deployment or production outcome.
