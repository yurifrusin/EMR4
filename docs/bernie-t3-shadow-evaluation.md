# Bernie T3 Nondeterministic Shadow Evaluation

Status: T3.1 contract and deterministic scorer implemented; no live-provider
replay is enabled.

## Purpose

T3 compares candidate models as interpreters and tool selectors against the
authored synthetic T1/T2 semantic corpus. It does not grant model write
authority and does not treat model output as diary truth.

## T3.1 Contract

`app/services/ai/evals/bernie_shadow_eval.py` defines:

- an immutable model-version ledger covering provider, exact model revision,
  prompt version, tool schema version, and sampling temperature;
- synthetic evaluation cases with normalized authored expectations and an
  explicit per-case tool allowlist;
- a fail-closed execution envelope that rejects writes, non-synthetic state,
  non-deterministic tools, and invalid repeat indexes;
- normalized provider responses that retain a response hash rather than
  requiring raw output in the common ledger;
- deterministic exact scoring of intent, entities, date/time, clarification,
  and tool selection; and
- separate safety findings for write-authority claims, claimed completed
  actions, and tools outside the case allowlist.

Latency, token counts, and estimated provider cost are recorded in a separate
operational record. They cannot raise or lower correctness or safety scores.

## Closed Boundaries

T3.1 imports no provider SDK, route, database, persistence model, or diary
mutation service. Live calls, provider adapters, corpus export, promotion
thresholds, and runtime wiring remain out of scope. Later replay must use
synthetic state and deterministic read-only tools, and every provider adapter
must normalize into this contract before scoring.

## Next Slice

T3.2 should build a source-safe loader that projects an explicitly selected
subset of the T1/T2 authored synthetic corpus into `ShadowCase` values. It
should reject PHI-shaped fields, generated expectations, mutable diary state,
and any case whose expected tool is absent from its allowlist. Live model calls
remain a later, separately reviewed slice.
