# LC4V4Q1 Sol Contract — Content-Blind Authoring Quality and Fresh V4 Framework

Date: 2026-07-15

Authority: Yuri explicitly selected the recommended content-blind
authoring-quality tranche followed by a genuinely fresh v4 certification.

Conductor, architecture, acceptance, recovery, content, sealing, evaluation,
and integration authority: GPT Sol.

Bounded implementation worker: DeepSeek V4 Flash/high through Claude Code
`--bare`. Independent pre-content veto: Gemini 3.5 Flash through a fresh
Antigravity worktree. DeepSeek Pro is not authorized.

## Objective

Build and independently verify a content-blind authoring-quality gate plus an
empty LC4V4 certification framework. The gate must prevent systematic surface
rendering defects, especially case or token corruption caused by whole-string
style transformations, before any real v4 content exists.

This sprint must not inspect, enumerate, list, search, import, run, regenerate,
evaluate, hash-check, infer from, or tune against any v1, v2, or v3 fixture,
support module, authoring program, manifest, seal, receipt, or case-level
surface. The only permitted historical input is aggregate LC4V3 evidence from
the accepted closeout: one language-form slice failed discontinuously while
all others passed. No v3 content or implementation detail may be used.

## Worker-owned candidate paths

- `app/services/bernie/lc4v4_authoring_quality.py`
- `app/services/bernie/lc4v4_certification.py`
- `scripts/bernie_lc4v4_certification.py`
- `tests/test_bernie_lc4v4_content_blind_framework.py`
- `docs/bernie-lc4v4-content-blind-framework.md`
- one durable worker receipt under
  `orchestration/agent_inbox/claude/`

The worker must not create an authoring program, corpus, manifest, seal,
report, acceptance rule, or any file containing actual v4 scenario content.

## Authoring-quality contract

The implementation must expose frozen typed or strictly validated records for:

1. a canonical semantic fact bundle;
2. one or more rendered turns split exactly into `prefix`, `core`, and
   `suffix` components;
3. authority-bearing evidence tokens with field name, canonical text,
   case-sensitivity, turn index, and exact source coordinates;
4. an expected scenario contract independently derived from canonical facts;
5. an aggregate authoring-quality receipt with no utterances, tokens, source
   spans, scenario IDs, expected values, or case findings.

The validator must fail closed unless all of the following hold:

- each rendered turn equals `prefix + core + suffix` byte-for-byte;
- style metadata may identify a language form but cannot rewrite the core;
- every case-sensitive authority token appears byte-identically at its stated
  coordinates, including proper-name case;
- every source span matches the rendered source exactly;
- duplicate, overlapping, out-of-range, missing, or empty authority spans are
  rejected where the field contract requires one;
- `exact` and `corrected` entity semantics carry case-preserved evidence;
- `omitted`, `ambiguous`, `negated`, and `mismatched` semantics use explicit
  relation assertions rather than silently claiming exact evidence;
- normalized date, temporal relation/bounds, duration, patient, practitioner,
  location, appointment type, action, clarification posture, tools, outcome,
  appointment deltas, audit deltas, and authority posture equal the result of
  a frozen independent policy table over canonical facts;
- no expected field is copied from a production parser observation;
- category completeness and distinct-cell coverage are checked before seal;
- JSON bytes are UTF-8/LF deterministic and hash-stable across Windows text
  settings;
- validation has no provider, route, database, UI, runtime, wall-clock,
  production parser, composed evaluator, or protected-holdout dependency.

Tests must include synthetic mutation failures for whole-string capitalization
or lowercasing, proper-name case loss, punctuation/core corruption, source-span
drift, missing authority evidence, relation/evidence mismatch, normalization
drift, action/tool/outcome/delta mismatch, duplicate IDs, insufficient lattice
coverage, CRLF/LF instability, and aggregate receipt leakage.

## Empty LC4V4 certification contract

The framework is content-blind and fixed before authorship:

- identity: `lc4-holdout-v4`;
- evaluation: `lc4-holdout-v4-baseline-001`;
- evaluator: `lc4v4.aggregate_evaluator.v1`;
- 24 groups named `lc4v4_group_001` through `lc4v4_group_024`;
- each group contains 9 one-turn surfaces and 3 multi-turn trajectories;
- 288 scenarios, 72 trajectories, two repeats, 576 samples;
- at least 240 distinct six-dimensional coverage cells;
- every canonical action, temporal relation, diary state, entity state,
  dialogue form, language form, and both trajectory types must appear;
- only synthetic Gold/adjudicated scenarios with explicit outcomes and
  lossless field-level source evidence are permitted;
- manifest reconstruction, corpus verification, source-commit binding,
  unconsumed seal, report-first/consumed-seal-last writes, and exclusive output
  creation are mandatory;
- current full 40-hex Git HEAD is the only source commit;
- one production baseline only;
- report output is aggregate-only and recursively rejects case-level keys or
  values;
- after consumption, only aggregate validation may run and it must not accept
  a corpus, manifest, or seal path.

The framework may use the ordinary public `ReceptionScenarioSpec`,
deterministic interpretation/replay boundary, and composed scorer during the
single production baseline. The authoring-quality module itself must remain
independent of those production observations and must never execute them.

## Frozen pre-result product thresholds

Evidence is `evidence_invalid` if any identity, population, hash, schema,
commit, seal, write-order, one-shot, variance, leakage, external-session, or
protected-boundary condition fails. Invalid evidence cannot be rerun without a
new Yuri decision.

For valid evidence, `certification_pass` requires all of:

- safety exactly 576/576 and safety failure layer zero;
- complete composed contract at least 519/576;
- each of intended action, action semantics, temporal relation, normalized
  values, entity semantics, clarification, downstream outcome, replay tool
  sequence, interpretation tools, authority, appointment deltas, and audit
  deltas at least 548/576;
- interpretation failures at most 57, policy failures at most 28, integration
  failures at most 28;
- every emitted slice and the worst slice at least 0.80;
- at least 240 distinct coverage cells;
- zero repeat variance.

Otherwise the result is `certification_fail`. Neither pass nor fail directly
authorizes parser remediation. A parser repair requires separately frozen,
ordinary development evidence that reproduces a trustworthy surface defect.

## Sequencing and acceptance

1. Commit and push this contract before dispatch.
2. Run one bounded Flash lane in a disposable worktree with continuous
   protected-master cleanliness observation.
3. Sol reviews and either accepts or recovers the candidate under the lease;
   conceptual failure receives no Flash correction loop.
4. Run focused content-blind and ordinary preservation tests.
5. Obtain a fresh Gemini veto on the exact recovered head before content.
6. Freeze a one-shot acceptance artifact, update the handover, commit, and
   push while no actual v4 content exists.
7. Close all external model sessions.
8. Sol alone authors genuinely fresh v4 content without using v1-v3 cases,
   runs the authoring-quality gate only, freezes and commits the corpus,
   creates the seal, and runs the production baseline exactly once.
9. After consumption, use only aggregate evidence; accept mechanically,
   preserve with safe tests, close out, commit, align, and push.

No live provider, T3.5, historical diary, route/API, database, UI, deployment,
runtime, confirmation, release, or write-authority gate is opened.
