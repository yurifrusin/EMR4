# Preterminal observability clockwork incident-intake recovery closeout

Date: 2026-08-20

Timestamp: 2026-08-20T07:22:35.5977084+10:00 (Australia/Brisbane)

Status: `accepted`

The clockwork can now accept a bounded semantic incident observation during a
clean closeout and atomically derive the next AER ID, stable attempt identity,
category-owned origin, peer links, corrected status, register revision, source
cutoff, complete pattern report and baton register row. Callers author none of
those derived fields.

Intent v1 and blocked, user-decision and checkpoint transitions preserve their
existing byte-preserving semantics. Intent v2 alone changes register and
pattern bytes, and both are bound into the same pointer-last generation as the
other canonical surfaces. A fault injected after the register replacement
restored every canonical and metadata byte; a completed publication remained
byte-recoverable.

The current-register tests now independently recompute aggregates from the
validated incident population rather than requiring manual count edits after
each legitimate intake. Schema, ascending IDs, category/origin, split-attempt
peer links, sensitive-key, exact evidence-path and open-incident controls
remain intact.

The first live incident-intake generation was rolled back byte-exactly when a
post-publication compatibility run found one remaining fixed source-cutoff date
assertion. The corrected assertion derives the maximum incident date. AER-0658
preserves that repository-fixture defect.

The second live generation was also rolled back byte-exactly when the same
post-publication suite found two remaining historical formulas for current
revision and agent-origin population. AER-0660 preserves that recurrence and
the corrected tests now validate canonical or population-derived readings
directly. Only the final fully compatible generation is accepted.

The third live generation was likewise rolled back byte-exactly after one
remaining full recurring-pattern list rejected the new post-baseline peer
group. AER-0661 freezes that list as historical through AER-0656 and makes all
later recurring-pattern assertions population-derived. The final generation is
the only accepted publication.

Before that corrected publication, Sol also caught and corrected one manually
expanded Git ID in conversational commentary. AER-0659 preserves the mismatch;
the repository and dry run always held the correct full object ID. The durable
reporting control now permits a full ID only when copied from machine output or
a persisted receipt.

Exact candidate `7c7ce52a6380637d54dc5ae2d6a778ccd300dd2f` passed 480 tests, Ruff,
compile and a fresh Gemini 3.7 Flash/high independent veto with receipt SHA-256
`32022df8a6c232ae9902c02910f18ebdd01ba546302e70e8aef43b27532fecb9`.

This is a governance-only capability. It changes no product, provider, native
Harness, broker, data, database, runtime, deployment or protected-ref surface.
