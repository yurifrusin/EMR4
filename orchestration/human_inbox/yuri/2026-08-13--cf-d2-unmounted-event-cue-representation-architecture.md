# Yuri update — CF-D2 unmounted event and cue representation architecture

Date: 2026-08-13

Timestamp: 2026-08-13T17:46:24+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

## Lay summary

The smaller event-watcher design now has a compact database-shaped blueprint.
It needs seven sorts of record: which synthetic source stream is being watched,
which positions were classified, which refresh reminders are pending, how far
the consumer has safely progressed, what delivery attempts occurred and what
happened when Reception One tried a fresh read.

Those records contain no appointment or patient details. They say only that a
fresh authorised read may be useful. Eighty deliberately damaged versions were
refused, including missing records, crossed gaps, stale ownership, orphaned
reminders, hidden payload fields and invented freshness.

The key honesty improvement is that the blueprint distinguishes what a table
constraint can prove from what still needs a carefully atomic database
transaction. This prevents a neat-looking schema from being mistaken for a
finished durability mechanism.

## Technical summary

Source `16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed` freezes seven abstract
relations and five transaction protocols against the exact accepted
observability and admission contracts. Twelve authored-synthetic row families
pass. Fifty-two hostile contract and 28 hostile row variants reject with the
canonical inputs unchanged. Ninety-two focused lineage/API/latch checks and 193
canonical tests pass.

No SQL was generated and no database, source, provider, network, route or
command was contacted.

## Issues and deliberate limits

No acceptance issue remains. This is representation evidence, not PostgreSQL
or transaction evidence. SQL syntax, catalogue shape, locks, isolation,
restart, unknown commit, delivery, timing, retention and operations remain
unproved.

Protected evidence, patient/product/clinical data, external patient clients,
real identity, provider/ADC, credentials/IAM/network, executable tools,
commands/writes, deployment, production, release, Pages and protected refs
remain closed. `docs/branding/` and unrelated untracked files remain untouched.

## Place in Raisa

This is the database-shaped seam underneath Reception One's quiet refresh cue.
It preserves our simplified principle: sources and atomic commands own
correctness; durable event records merely make useful fresh reads happen sooner
and more reliably.

## Next

The sprint engine is continuing to inert SQL-text lowering of these exact seven
relations. It will prove that the blueprint can be expressed structurally
without connecting to PostgreSQL or executing a migration. Your attention is
not required.
