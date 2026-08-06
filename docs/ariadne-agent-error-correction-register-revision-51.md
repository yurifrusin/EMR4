# Ariadne agent-error register revision 51

Date: 2026-08-06

Status: migration/transaction alias-bridge recovery active

## AER-0051 remains open

The first two fresh exact-head vetoes and their recoveries remain preserved in
revisions 49 and 50. Candidate
`917dff6f06fdbacdc99e66c6802cac1b7f8b5d7f` closed the bounded admission-
conflict and pending-anchor seams: its receiver-owned primary/conflict model,
source-purge behavior, coordinator locator boundary, anchor fence and all five
first-veto repairs passed the third independent reconciliation.

That third veto nevertheless found one P1 data-ceiling contradiction. The plan
globally prohibited appointment identifiers and raw product UUIDs in every
future durability relation while `diary_context_aggregate_aliases_v1` explicitly
stored the product appointment UUID to maintain one opaque aggregate alias.
The static test proved only that both phrases existed and did not reconcile the
catalogue column against the prohibition.

Sol preserved and rejected the candidate and extended the same recovery lease.
The active recovery defines `diary_context_aggregate_aliases_v1` as the sole
owner-private product-identifier exception. It stores exactly the practice-bound
appointment UUID needed for a stable alias; only an owner-mediated producer
entry point can create or return that alias, and the producer has no direct table
privilege. Observer, admission receiver, coordinator, lifecycle, retention and
application-read principals have no `SELECT`, DML or function path. Only the
opaque alias enters the outbox or any later durability evidence.

The bridge is outside the three durability retention families and supplies no
purge authority. Deletion is disabled by default and remains a distinct later
owner-mediated product-lifecycle policy after the appointment can no longer
emit a source row. It never cascades to or rewrites retained opaque evidence.
No actual product identifier is processed by this architecture-only tranche.
A genuinely fresh exact-head veto remains required before acceptance or the
inert DDL rehearsal.

## AER-0052 corrected

The review environment control remains effective. The third veto used only the
proven absolute system interpreter with `--noconftest`, no cache and no bytecode,
passed 5/5 focused checks and left exact worktree `r25` unchanged. `uv`, `pip`
and environment bootstrap remain prohibited in read-only review worktrees.

Revision 51 contains 52 bounded incidents: 40 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0051 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
