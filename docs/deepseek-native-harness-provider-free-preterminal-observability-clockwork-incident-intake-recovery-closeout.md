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

Exact candidate `7c7ce52a6380637d54dc5ae2d6a778ccd300dd2f` passed 480 tests, Ruff,
compile and a fresh Gemini 3.7 Flash/high independent veto with receipt SHA-256
`32022df8a6c232ae9902c02910f18ebdd01ba546302e70e8aef43b27532fecb9`.

This is a governance-only capability. It changes no product, provider, native
Harness, broker, data, database, runtime, deployment or protected-ref surface.
