# Yuri update — CF-D2 unmounted event and cue admission rehearsal

Date: 2026-08-13

Timestamp: 2026-08-13T17:00:06+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

## Lay summary

The new, smaller durability design has passed its first executable rehearsal.
We gave it a completely artificial stream of event positions and made it deal
with duplicates, conflicting duplicates, missing positions, invalid events,
stale ownership and failed refreshes.

It behaved as intended. A missing event stops progress at the gap. A duplicate
does not create more work. A conflicting duplicate is refused. A required
refresh reminder cannot be lost while the system says the event was handled.
A stale watcher cannot alter the position. Most importantly, the reminder
contains no appointment truth and cannot change the screen: Reception One must
read the current authorised Diary again.

This is still deliberately a tabletop-quality executable model, not a database
or watcher. That is valuable because the simple rules are now settled before
we spend more time on machinery.

## Technical summary

Source `a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b` adds a pure in-memory admission
state machine over the exact CF-D2 observability contract. Twenty-two canonical
scenarios and 60 hostile variants cover closed candidate shape, immutable
duplicate reuse, identity conflict, atomic receipt/obligation admission,
contiguous checkpointing, restricted pending-obligation coalescing, exact
lease-generation fencing, typed lag and delivery-bound fresh-read
reconciliation. Denied transitions preserve the complete normalized state
digest. Ninety-one focused lineage checks and 193 canonical tests pass.

No database or source was contacted, no operational state was persisted, no
provider or network was used, and no command or application route changed.

## Issues and deliberate limits

No acceptance issue remains in this tranche. It does not prove PostgreSQL
representation, transactionality, restart, unknown commit, delivery transport,
retention, operations or product-data safety. Those claims remain closed and
will be opened only in small order.

Protected evidence, patient/product/clinical data, external patient clients,
real identity, provider/ADC, credentials/IAM/network, executable tools,
commands/writes, deployment, production, release, Pages and protected refs
remain closed. `docs/branding/` and unrelated untracked files remain untouched.

## Place in Raisa

This is the first executable slab underneath the accepted visible Reception
One cue behavior. It preserves the central architecture: authoritative sources
and command-time checks own correctness; durable events merely help clients
notice that a fresh read may be useful.

## Next

The sprint engine is continuing to an inert, provider-free unmounted
representation architecture. It will determine the smallest relational facts
needed to represent these already-proved rules, without opening a database,
executing a migration or starting a watcher. Your attention is not required.
