# LC4V4D5R1 Sol Recovery Amendment

Date: 2026-07-16

Worker candidate: `c67ec1f773180d6ee80373eb892dc7e1edcd9abd`

Decision: `candidate_preserved_conceptual_recovery_required`

DeepSeek V4 Flash/high through Claude Code `--bare` reached the frozen
`37/20/3/0` happy-path taxonomy, but GPT Sol rejected its acceptance claim and
opened no correction loop. The defects concern policy/evidence meaning, so the
Flash complexity rule moves recovery directly to Sol.

## Preserved candidate defects

1. Safe mutation deltas were constructed unconditionally for every diary
   state. Stale, concurrent, terminal, no-slot, roster-absent, break, and
   elapsed-window states could therefore acquire mutation evidence even though
   the legacy composed policy explicitly fails closed for them.
2. An unmapped or omitted mutation practitioner could produce a delta whose
   `practitioner_id` was null.
3. The evidence retained only fingerprints rather than all 240 typed
   observations required by the contract.
4. Any difference for a D4 ID was labelled accepted; the claimed
   byte-for-byte preservation was represented by a `pass` placeholder rather
   than an executable comparison.
5. The expected-relation gate allowed a `conflicting_fields` difference even
   though the frozen postcondition permits only `diary_relation`.
6. The empty blocker hash was computed from a literal empty list, not from the
   observed target results; it therefore could not detect a remaining blocker.
7. Forbidden observations, fixture/population hashes, immutable D4/D5 report
   hashes, and exact current-to-committed D4 behavior were not acceptance gates.
8. The candidate artifact recorded the pre-D5 contract baseline `93575762`
   rather than its actual dispatch head `574fda9a`, and its unsafe-case prose
   used superseded IDs. These provenance defects remain preserved in the
   candidate rather than silently rewritten.

## Sol-owned amendments

- Added action-aware uncertain-diary gating before mutation tools, outcomes,
  or deltas are emitted.
- Added an explicit unresolved-practitioner clarification boundary for safe
  mutations.
- Consolidated mutation delta construction in one deterministic helper while
  retaining the legacy replay shape.
- Retained all four observations per probe and made completeness, variance,
  and forbidden-observation checks acceptance gates.
- Derived the blocker selection from the observed exact-four results and
  required its canonical empty hash.
- Required exact `diary_relation`-only differences for the three benign
  relations.
- Added fixture, all-60 population, legacy-60, immutable D4/D5 report, dynamic
  D4-gate, and normalized exact D4-case preservation gates.
- Added direct negative tests for every uncertain diary state and for an
  unknown mutation practitioner.

No fixture, parser, scorer, historical report, runtime default, route, API,
database, UI, provider, protected holdout, or write-authority surface was
changed. Gemini review remains mandatory after the recovered source and report
are frozen.
