# Harness preactivation diagnosis — lay and technical closeout

Date: 2026-08-21

## Lay summary

We found the failure. It was not DeepSeek and it was not the new harness trying to contact a provider. Our Python generator accidentally turned characters that were meant to remain written as JavaScript escape sequences into real line breaks inside the generated sentinel program. That program could not be read, so it never reached its first “I am alive” event.

This is encouraging because it is narrow, local and repairable. The diagnosis required no further harness attempt and no provider credit. The next step is to correct only those escaped characters and prove the generated sentinel is valid before considering another separately controlled boot.

## Technical summary

- Accepted source: `d1e60a59a0b0cf600721850b96d2914059fe7ca3`.
- Coordinate: `sentinel_source()` ordinary bytes-literal escape translation.
- Failed generated module: three raw line-terminator lexical violations; first fatal coordinate is CR inside the regex literal.
- Passing control: double-escaped source, zero lexical violations, previously emitted both HMR readiness events on pinned rc.7.
- Verification: 50 tests, Ruff and `py_compile` passed.
- Activity: zero Node, Harness, broker, worker, model, provider, network and raw-stream reconstruction.
- Protected refs remain fixed at `2e34bdad732fdab32fbf778280b3d3c70d66d602`; no Pages or product surface opened.
- Non-PHI Pushover closeout notification passed.

The clockwork will allocate four contained observations: the source escape defect, one overbroad provider-counter predicate caught by tests, one transient guessed full-Git-ID draft caught and removed before preflight, and one rejected closeout-intent field-shape mismatch that changed no canonical state.
