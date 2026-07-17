# Bernie Synthetic Silver Action/Temporal Tranche Closeout

Date: 2026-07-17

Status: `partial_pass`

## Outcome

The authorized 24-candidate ordinary-development tranche completed. The
pre-repair population was 0/24 complete over 48 observations. The accepted
bounded parser changes now pass all 11 supported action assertions and all 10
supported temporal assertions, while refusing to invent unsurfaced duration
or time values.

The exact final tranche result is:

- complete candidates: 2/24;
- failed candidates: 22/24;
- safety: 48/48;
- repeat variance: zero;
- final report hash:
  `sha256:6a4c89992e7a791164bda581b04ae2216a3c7e2661b4a9f29963b220d90b9db2`.

The two complete candidates are the fully evidenced `3pm or later` create
reversal and `by 5pm` repeated create cases. The low whole-candidate score is
not a failure of the accepted parser rules: most selected candidates retain a
separate hidden-oracle, clarification-policy, entity-transition, or replay
mismatch documented per candidate in the classification.

## Accepted parser changes

- schedule-read staff wording: `diary rundown`, `talk me through it`,
  `run me through it`, and bounded `diary view ... view only`;
- resize wording: `appt length`, `make it N mins`, and possessive existing-
  appointment duration changes;
- `status ... arrived/completed/DNA/no-show` staff shorthand;
- `take out ... appt` cancellation shorthand;
- second-turn action extraction only after the explicit bounded
  `diary request ... details may need clarifying` preface;
- `TIME or later` as `not_before`;
- `by TIME` as `not_after`; and
- corrected `around/about TIME` replacing an earlier exact point as an
  approximate relation.

No entity, clarification-policy, replay, API, route, runtime, database, UI,
confirmation, deployment, release, provider, or write-authority behavior was
changed.

## Broader effect

Across all 192 admitted Silver candidates, complete results improve from 2 to
11. Exact post-remediation full-Silver report hash is
`sha256:b0d7072884b2d8331fbc233de797c112bf11503a04cdd5ce95ad69c327feacc8`:

- intended-action pass observations: 196 -> 312;
- action-semantics: 176 -> 258;
- temporal-relation: 204 -> 328;
- normalized-values: 64 -> 112;
- downstream-outcome: 64 -> 120;
- safety remains 384/384; and
- repeat variance remains zero.

Interpretation and replay tool-sequence observations each decrease by four
because corrected action extraction exposes source policy contracts that ask
for clarification tools despite clear actions and no expected clarification.
Those visible residuals were not hidden by weakening extraction or scoring.

Exact parent-to-candidate comparison over all 1,152 ordinary-development
scenarios finds 32 changes. Every one is an authored resize scenario in groups
33-48, variants 2 and 3, formerly misread as create and now read as resize.
No changed scenario belongs to `LC4R10_RECONCILIATION_IDS`; no ordinary-
development temporal surface changes.

## Verification

- 26 focused action/temporal parser tests pass;
- 164 semantic-extraction preservation tests pass;
- 316 active scenario-schema, tier, composed-evaluator, composed-corpus, and
  scale-corpus tests pass after deselecting exactly two immutable historical
  committed-report regeneration assertions;
- 50 tranche, synthetic-corpus, recovery, baseline-integrity, and handover
  tests pass;
- exact tranche report regeneration passes; and
- full 192-candidate Silver rebuild is deterministic and safety-closed.

A broader historical reconciliation run was diagnostic only. Its failures are
immutable legacy report/hash comparisons or behavior already present at exact
parent `fafe6ad5`; they are not attributed to this tranche. Direct source-head
comparison is the acceptance evidence for changed behavior.

Fresh Gemini 3.5 Flash independently reproduced the exact reports, focused
tests, 32-scenario development impact, zero LC4R10 intersection, safety, and
variance on candidate code head `13214dab` and returned `DECISION: pass`.

## Disposition and next decision

This tranche closes as `partial_pass`: its supported extraction rules are
accepted, while the corpus remains development Silver and 22 selected cases
retain explicitly classified residuals.

The next recommended work is not another parser tranche. It is a bounded audit
of all 192 admitted candidates for semantic-evidence completeness and internal
oracle/policy coherence, followed by quarantine or regeneration of invalid
rows. Changing the admission decision or corpus contract is a new material
choice for Yuri.

DECISION: partial_pass
TRANCHE_COMPLETE: 2/24
FULL_SILVER_COMPLETE: 11/192
SAFETY_PASS: 384/384
VARIANCE: 0
PROTECTED_ACCESS: false
