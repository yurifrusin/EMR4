# Context Fabric source-owned-truth reorientation

Date: 2026-08-12

## Lay summary

The redesigned boundary is now accepted. The database and its command service
remain the referee. Context Fabric frames help the interface understand the
current race, while events tell it that something may have changed and that it
should look again. Neither a frame nor an event can award the winning ribbon.

If a user confirms an appointment from stale information, the command checks
current database truth before committing. The winner receives the durable
receipt and audit record. A loser receives a clear stale, schedule-conflict or
authority result, nothing is incorrectly written, and the interface can refresh
and try again. Freshness checking does not silently stand in for human
confirmation where confirmation is required.

One watcher can serve the whole database and many users. We describe it as one
logical watcher per event partition. The first runtime can use one physical
process; a future high-availability pair is active/standby, with only the fenced
owner allowed to advance the checkpoint.

The durability work has not been thrown away. CF-D1 is retained, and restart-
safe Durable Event and Cue Delivery remains a named later extension. It is now
responsible for timely, observable cues rather than the correctness of the
appointment record itself. Any return to CF-D2 will begin with better internal
observations rather than repeating the stopped experiment.

## Technical summary

- Accepted result:
  `raisa_context_fabric_source_owned_truth_conditional_command_reorientation_pass`.
- Exact independently reviewed source:
  `037eed060d4519f2f3d6721135143ecb6f70e358`.
- Current source truth, expiring Context Fabric frames, cue delivery and command
  execution have separate authority planes.
- The conditional-command packet binds practice, actor/session, purpose,
  operation, target/conflict domain, expected state, command digest, expiry,
  nonce and signing key.
- Create requires a schedule-conflict-domain fence and final database
  constraint; update/status/delete use locked current appointment state.
- Only `committed` mutates; idempotent replay returns the original receipt and
  all other typed outcomes produce no mutation.
- Raw compatibility routes are unchanged but their migration target is the
  same backend kernel; implicit freshness is not implicit human confirmation.
- All 28 hostile mutations, 53 focused tests and 191 canonical fast tests pass.
- One Sydney Vertex Gemini 2.5 Flash review returned HTTP 200 with no P0-P2
  finding, tools or fallback; no patient/product data was supplied.
- CF-D1 is retained; CF-D2 remains unproved and may reopen only through a fresh
  observability-first plan.
- Protected refs remain `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
