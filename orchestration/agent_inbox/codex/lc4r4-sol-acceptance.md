DECISION: pass

# LC4R4 Sol Acceptance — Patient Entity Evidence Repair

Date: 2026-07-14

Conductor, sprint planner, architecture/acceptance owner, recovery owner, and
protected integrator: GPT Sol.

## Authority and provenance

Sol planned LC4R4 directly. DeepSeek V4 Flash/high through Claude Code
`--bare` implemented one bounded candidate and one unchanged-scope evidence
revision. Its first receipt correctly returned `DECISION: revision_required`;
the revision returned `DECISION: pass` at worker head
`aefb0ddf95aec20894049416e6fc8bcf040abc26`. These are worker artifacts, not
self-acceptance. DeepSeek Pro and Deep Code were not used.

Sol adopted the worker commits as untrusted candidates on the protected LC4R
staging branch. Sol then owned a documented evidence-only recovery amendment:
separating the 83 aligned acceptance records from every matching development
surface and reporting safety on the one-repeat scenario denominator. Gemini
3.5 Flash/medium independently reviewed exact recovered head
`777c21313ba2b4458617f0464a1624d0d4c9d909` through a fresh Antigravity
worktree and returned `DECISION: pass`.

## Accepted result

The oracle-free extraction boundary now treats standalone `someone` as an
ambiguous patient reference and allows a later explicit patient name in a
non-correction turn to resolve an initially omitted or ambiguous patient to
`exact`.

The bounded aligned target passes exactly:

- standalone `someone`: 70/70, selection hash `50260edcf0fa2c0d`;
- additive ambiguous-to-explicit patient resolution: 13/13, selection hash
  `485cd258fd5ebd60`; and
- combined aligned target: 83/83.

Only patient additive ambiguity is changed. Practitioner and duration
additive ambiguity remain unresolved unless previously omitted; explicit
name-to-name corrections remain `corrected`; pronouns are not promoted; and
substring, unsafe, negation, tool, authority, lossless-normalization, and exact
`tomorrow at 3pm` boundaries remain intact.

The report separately discloses the full Silver/pending surface effect: 126
standalone-`someone` scenarios and 16 ambiguous-then-explicit additive
scenarios match the runtime rules. These are not relabelled as aligned or
adjudicated coverage.

Full-development semantic results are:

- intended action: 880/1,152;
- action semantics: 730/1,152;
- temporal relation: 628/1,152;
- normalized values: 101/1,152;
- entity semantics: 300/1,152, up from 255 (+45);
- clarification: 698/1,152; and
- safety: 1,152/1,152 with zero per-scenario variance over 2,304 samples.

## Normalization conclusion

LC4R4 did not teach the parser to echo unsupported or contradictory Silver
defaults. All 489 aligned normalized-value failure records reproduce in seven
evidence signatures:

- unsupported expected value only: 298;
- surface disagreement plus unsupported expected value: 114;
- surface disagreement only: 31;
- observed surface value absent from contract plus unsupported expected value:
  17;
- all three conflict types: 15;
- observed surface value absent from contract plus surface disagreement: 12;
  and
- observed surface value absent from contract only: 2.

No current aligned normalization failure is a missing parser value backed by
a matching explicit source span and matching Silver value. The 489 records
remain diagnostic contract-quality evidence, not a normalization remediation
target.

## Verification

Sol verified the authoritative LC4R4 report check, `git diff --check`, and
1,072 passing tests with one expected skip across the focused semantic/report,
LC4R3 preservation, action grammar, smoke interpreter, Ariadne preflight,
composed evaluator, development audit, replay, LC3 mutation, LC4 scale,
scenario/evidence, interpretation route, and T3.1-T3.4 shadow surfaces. Three
documented historical exact-report comparison nodes were deselected because
they intentionally freeze earlier development baselines.

An initial attempt to run three pytest groups concurrently caused PostgreSQL
test-schema enum creation collisions before test execution. The identical
groups then passed serially; this was a verification-orchestration defect, not
a product failure.

The live shadow gate remains `decision: blocked`, external calls false, and
runtime authority false. Gemini independently reproduced focused semantics,
the LC4R4 report check/regressions, scenario integrity, evidence contracts,
and the shadow contract before returning `DECISION: pass`.

## Boundaries and continuation

No development fixture, generator, scenario schema, scorer/audit policy,
action grammar/route contract, protected holdout evidence, provider, T3.5
adapter, API/route, database, UI, deployment, historical diary, memory,
RAG/GraphRAG, confirmation, or write authority changed. Protected holdout v1
remains sealed; T3.1-T3.4 remain preserved and blocked by default.

Post-LC4R4 profiling leaves 584 aligned-failure records. Entity-semantics
failures inside that slice fall from 485 to 461; intended-action misses remain
only 26. The clearest next genuine surface-supported tranche is the 96 aligned
explicit practitioner schedule questions whose action semantics and
clarification currently fail because explanation handling incorrectly expects
a patient identity. That should be isolated from their remaining temporal,
duration-default, and Silver-label conflicts before any repair.
