# Provider-free unmounted status-confirm kernel adapter contract plan

Date: 2026-08-12

Source HEAD: `fe43ff09bcca67e7634790bb6aeadace51702305`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Freeze the pure boundary between the existing signed status-confirm envelope
and the accepted status transaction protocol. The adapter emits either one
closed kernel-request value or one typed stop. It never invokes a kernel,
route, database or command.

## Exact boundary

- accepted operation and family: `confirmAppointmentStatusProposal` /
  `status-confirm`;
- accepted proposal intent and command kind: `update_appointment_status` /
  `status`; the current waiting-area union variant stops as unsupported;
- client input supplies confirmation, the signed proposal envelope, warning
  acknowledgements, freshness token and idempotency header only;
- server context alone supplies current practice, actor, role, session,
  authority, current appointment state and signed-evidence verification;
- all proposal warning codes must be acknowledged exactly, with no duplicate
  or unknown acknowledgement;
- signed evidence must be required, verified for the exact purpose and bound
  to the same practice, actor, command, current state and freshness token;
- terminal-to-different-status input stops effect-free as
  `transition_policy_deferred`;
- a ready request binds the exact `practice -> appointment ->
  idempotency_record` lock plan, current source version and canonical request
  digest; and
- all values are authored-synthetic opaque identifiers with no product data.

## Result and delivery mapping

Committed and replay results are rendered only from a canonical receipt body
already bound to its digest. Replay returns the stored status/body exactly.
Authority, confirmation, freshness, validation and idempotency losers map to
closed transport results without reconstructing success. The status adapter
cannot admit `schedule_conflict`; observing it is an internal fail-closed
contract error with no released body.

Post-commit rendering may fail, but cannot change the stored receipt. A retry
renders the same stored bytes/digest and never emits a second request.

## Acceptance

The tranche passes only if exact source hashes and a closed schema validate;
all admission scenarios match exact stops or request values; at least 30
hostile mutations fail closed; all eight shared outcomes have exact mapping;
terminal and waiting-area cases emit no request; stored-receipt replay is byte
stable after a simulated delivery failure; focused/API/canonical tests pass;
and refs plus unrelated untracked files remain unchanged.

## Forbidden surfaces

No application import/edit/route execution, runtime kernel, database/source,
watcher/event, real signature or credential, provider/network/tool/command,
product/patient data, deployment, production, release, Pages or protected ref.
Only exact non-protected file allowlists may be searched. Never stage
`docs/branding/` or use broad staging.

## Next safe descendant

After acceptance, perform a provider-free read-only status-confirm runtime-gap
admission review. It may compare this pure contract with the current route's
lock order, session ingress, terminal behavior and receipt delivery, but may
not edit or execute the route or database.
