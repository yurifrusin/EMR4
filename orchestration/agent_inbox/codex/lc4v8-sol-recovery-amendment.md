# LC4V8 Sol Recovery Amendment

Date: 2026-07-16

DeepSeek V4 Flash/high through Claude Code `--bare` returned candidate commit
`2beeffe8b32f859a9adfcd4d423829dc7ebcfbb4` from frozen source
`deece41c09c1a23eaaa6e913da14697da5442870`. Sol independently reproduced its
focused claim: 108 tests passed (96 framework plus 12 generic taxonomy tests).
Those tests establish that the submitted helpers behave as their author
specified; they do not satisfy the frozen V8 evidence contract.

Decision: `candidate_rejected_conceptual_fail_open_sol_recovery`

## Preserved rejection grounds

1. There is no single fail-closed one-shot execution surface that validates
   fixture, manifest, seal, thresholds, source bindings, and attempt state;
   creates the exclusive marker; evaluates all 576 samples; validates and
   hashes the complete report; classifies the result; and consumes the attempt
   on every post-marker exit.
2. `AttemptMarker.consume()` changes only an in-memory boolean, while public
   `cleanup()` deletes the exclusive marker. The framework therefore permits
   caller-controlled reuse instead of enforcing irreversible consumption.
3. Fixture validation rejects unknown fields only at the top level. Group,
   scenario, diary-state, and Gold schemas are not exact; missing or malformed
   fields are silently defaulted or string-coerced during conversion.
4. Language-form counts are inferred from a group-level list rather than
   validated per scenario, and report group/form assignments are inferred from
   insertion order. A malformed fixture can therefore satisfy the nominal
   shape while producing false slices.
5. Source verification accepts caller-supplied ancestry and bytes, does not
   bind the seal's attempt ID to the marker, and is not coupled to schema or
   execution. The individual comparisons are useful candidate code but do not
   constitute immutable source verification.
6. Aggregate and product-gate validation do not require all 24 group keys, all
   six language-form keys, all 13 dimensions, exact 576 samples, exact slice
   totals, or a recomputed complete-report hash. Missing evidence can therefore
   be treated as a product miss or omitted entirely rather than returning
   `certification_invalid`.
7. The exception-consumption test manually calls `consume()` after simulating
   an exception; it does not exercise an implementation that guarantees this
   behavior.

These are conceptual evidence-integrity and acceptance-semantics defects, not
bounded mechanical omissions. Under the Flash complexity rule, no same-lane
correction loop is authorized. Sol adopts the committed candidate only as
untrusted source under `docs/ariadne-orchestrator-recovery-lease.md`, records
every amendment, and will obtain a fresh Gemini pre-content veto on the exact
recovered head before any actual V8 corpus content exists.

The protected v1-v7 boundary, T3.1-T3.5 gates, and all product/write boundaries
remain unchanged.

## Sol amendments

Sol replaced the candidate's disconnected helpers with one executable
`run_one_shot` lifecycle and made these material amendments:

- exact top-level, group, scenario, Gold, manifest, seal, threshold, and report
  schemas with unknown-field rejection;
- per-scenario language-form and turn validation, exact public group IDs, all
  fixed distributions, and globally unique coverage cells;
- a callback input containing only utterances and synthetic diary state, with
  exact post-return scoring of all thirteen dimensions;
- raw-output repeat fingerprints, explicit product interpretation/policy/
  integration counters, and complete 24-group/six-form aggregate validation;
- direct Git ancestry and committed-blob reads rather than a caller-supplied
  ancestry boolean;
- a manifest binding fixture, framework, and frozen-threshold bytes at the
  corpus source commit, plus a seal binding the manifest bytes and attempt ID;
- an additional manifest binding for the product-facing evaluator module,
  including direct verification that the supplied callback's Python source
  file is that exact committed module rather than an unbound callable;
- an exclusive persistent marker with no deletion API, a durable consumed
  state, and consumption on pass, fail, invalid, missing-output, exception, and
  report-write failure paths; and
- a final report hash computed only after evidence counters, product failures,
  group/form gates, and decision are populated.

The recovered focused gate passes 41 tests, including temporary-repository
Git/blob verification and complete 576-sample pass, product-fail, and
evidence-invalid executions. The generic decision taxonomy is included in
that count. Formatting-module checks were unavailable because neither `ruff`
nor `black` is installed in the project environment; Python compilation and
`git diff --check` pass.
