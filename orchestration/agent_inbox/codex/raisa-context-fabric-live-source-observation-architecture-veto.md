# Independent veto: live-source observation architecture candidate

Date: 2026-08-06

Candidate:
`35a123d61d6d455f80ac312ea6800924989faf6f`

Reviewer: fresh native Sol/xhigh, read-only exact worktree

Decision: `revision_required`

## Findings

1. **P1 — source selector digests could narrow impact.** The source could omit
   an affected selector while the trace bound supplied selectors into the
   temporal signal. The repair must require a backend-owned event/schema/
   aggregate impact floor or bounded full invalidation, never source-defined
   narrowing.
2. **P1 — allowed strings left metadata-smuggling channels.** Event, aggregate,
   stream, correlation, selector and reason values needed exact canonical
   grammars, bounds, closed enums and backend-issued registered aliases or
   domain-separated keyed digests. Recursive closure alone was insufficient.
3. **P2 — positive synthetic admission conflicted with fixed disabled state.**
   The repair must define a sealed synthetic-only zero-effect classification
   activation that cannot enable a connection, credential, cursor, read,
   provider, persistence or command path.
4. **P2 — four paths in the review dispatch were non-canonical or absent.**
   This was a review-packet construction error, not a candidate architecture
   defect. The repaired veto must use the canonical API Spine async contract and
   exact acceptance path named by the live baton.

The existing Diary polling feed was otherwise correctly excluded from no-loss
inheritance, and the next descendant can remain unmounted and provider-free
after the three architecture repairs.

## Reconciliation

- specified packet: 65/65 tests passed;
- candidate diff check: passed;
- HEAD/branch/status before and after: exact candidate, exact review branch,
  clean;
- no edit, provider call, runtime action, command, deployment, Pages operation
  or ref movement occurred.

This review proves no live observation, delivery, database/outbox, durable
checkpoint, source read, patient privacy control, runtime, provider, command,
deployment, production or release behavior.
