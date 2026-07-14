DECISION: pass

# LC4R6 Sol Acceptance — Temporal Source-Evidence Audit

Date: 2026-07-14

Conductor, sprint planner, architecture/acceptance owner, recovery owner, and
protected integrator: GPT Sol.

## Authority and provenance

Sol planned LC4R6 directly from development-only evidence after the required
pre-plan receipt. DeepSeek V4 Flash/high through Claude Code `--bare` owned one
bounded five-file implementation lane. DeepSeek Pro and Deep Code were not
used. The protected master remained clean during worker execution.

Sol rejected the first candidate before integration. The unchanged worker lane
then removed its duplicated private audit ordering, exercised actual reordered
inputs, repaired fail-closed tests, and separated historical from current
baselines. Sol independently reviewed and tested the revision, then made one
test-only recovery amendment at `d37d229f` so input-order invariance compares
the complete returned taxonomy rather than only bucket fields. Exact provenance
and amendment ownership are recorded in
`lc4r6-sol-recovery-amendment.md`.

Gemini 3.5 Flash/medium independently reviewed exact recovered head
`ffc07bc6cd05acf000e2f1d15673f415c4de6358`, reproduced 29/29 focused tests
and the authoritative report check, and returned `DECISION: pass` in review
commit `ff62e0b9216fcf6fb022afbffe58c5d8c7152afc`.

## Accepted result

The ordinary development audit and composed temporal scorer select exactly 159
aligned temporal failures, hash `f56b4a20aad6161c`. The independent surface
evidence taxonomy is:

- insufficient surface evidence: 84, hash `c341652065504d17`;
- surface/contract conflict: 75, hash `fd04b9c86a54fea4`; and
- parser gap: 0, hash `e3b0c44298fc1c14`.

The 84 insufficient cases reproduce expected-relation counts
18/18/18/18/12 for exact, not-before, not-after, interval, and approximate.
All ten frozen expected/observed conflict-pair counts also reproduce.

The decisive result is the empty parser-gap set. None of the 159 current
development mismatches contains explicit surface temporal evidence that both
supports its Silver contract relation and is missed by the final interpreter.
LC4R6 therefore authorizes no temporal parser remediation. The 84 incomplete
and 75 contradictory cases remain corpus-contract quality evidence.

The current semantic baseline remains intended action 880, action semantics
814, temporal relation 628, normalized values 101, entity semantics 300, and
clarification 782 out of 1,152. Safety remains 1,152/1,152 with zero variance
over 2,304 samples.

## Verification

DeepSeek reported 29 focused tests and the report check passing. Sol reproduced
29/29 before and after its recovery amendment, then reran the authoritative
LC4R6 `--check` and diff hygiene successfully. Gemini independently reproduced
the same 29 tests and report check on the exact recovered head.

Sol's proportional serial preservation gate covered LC1 semantics/lattice,
T1 stateful evidence, all three T2 matrix layers, composed evaluation and
development audit, action grammar and interpretation harness, Ariadne
preflight, T3.1-T3.4 shadow scaffolding, and LC4 repair reports. The only
failure was the documented historical LC4R2 committed-report equality node,
which compares the live post-LC4R5 evaluator to an intentionally frozen report.
With only `test_report_hash_deterministic` deselected, the clean serial gate
completed 765 passes and one established scenario-integrity skip. The audit
module's remaining 32 tests also passed independently; the frozen historical
report was not regenerated.

## Boundaries and continuation

No runtime interpreter, core audit/scorer, generated fixture, generator,
scenario schema, protected holdout evidence, provider, route/API, database, UI,
deployment, historical diary, memory/RAG, confirmation, or write authority
changed. Protected holdout v1 remains sealed. T3.1-T3.4 remain intact and
blocked by default; T3.5 and live-provider execution remain deferred.

The next ordinary development-only step should be LC4R7 Silver contract-quality
reconciliation. Consolidate the already audited normalization, entity,
temporal, action, and clarification residuals into a deterministic adjudication
queue; distinguish malformed, incomplete, contradictory, and genuinely
surface-supported parser gaps; and authorize remediation only for the last
class. If no credible parser-backed subset remains, define the development
corpus quality/exit gate before asking for a separate holdout-v2 or reuse
decision. Do not reopen protected holdout v1 or T3.5 as part of that sprint.
