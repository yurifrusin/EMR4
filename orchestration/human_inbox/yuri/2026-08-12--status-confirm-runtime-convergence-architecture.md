# Status-confirm runtime convergence architecture

Date: 2026-08-12

Result: passed

## Lay summary

We now have a single coherent design for closing the gaps between the current
appointment-status route and the safer transaction kernel. The status operation
will be separated from its waiting-area sibling before it enters the kernel.
Inside one transaction, the backend will lock the practice, appointment and
saved request in a fixed order, recheck the staff member's current authority,
then decide whether this is a new effect, a safe replay or a conflict.

Confirmation is tied to the exact session, appointment version and warnings the
user saw. A disputed terminal-status change stops for policy rather than being
silently allowed. If a change succeeds, the appointment, audit record and saved
receipt succeed together. If the response is lost after commit, retrying the
same request returns that saved receipt without doing the work twice.

Nothing has been connected to the live route or database. This tranche is the
engineering blueprint for a safe rehearsal, not an implementation.

## Technical summary

The architecture freezes nine closed decisions: status-only discrimination;
server-owned authority/session ingress; `practice -> appointment ->
idempotency_record` locking; monotonic locked `appointment_state_version`;
signed evidence; exact warning equality; terminal
`transition_policy_deferred`; atomic mutation/audit/receipt correlation; and
canonical stored initial/replay delivery.

All nine source hashes, 20 scenarios and 56 hostile mutations pass. The focused
packet passes 12/12 and the bounded architecture-through-API lineage passes
138/138 before Continuity binding and 142/142 afterward. The first graph update
used an unsupported descriptive node kind and correctly failed closed; changing
only that vocabulary to the established `foundation` kind passed. No
application source, database, provider, credential or product data was used.

## Deliberately still closed

The physical version column, migration/backfill, ORM/service layout, route
wiring and real PostgreSQL transaction behavior are not selected or proved.
Waiting-area and raw compatibility routes are unchanged. Product data,
providers, commands, deployment, production, release, Pages and protected refs
remain closed.

## Next tranche

Next is a pure in-memory rehearsal of this exact architecture. It will challenge
lock/decision ordering, rollback, authority-first replay disclosure and
lost-response recovery without touching an application route or database.

Yuri's attention is not required; this is the next dependency-satisfied gate
under the standing uninterrupted-development authority.
