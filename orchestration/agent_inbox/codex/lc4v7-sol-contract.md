# LC4V7 Sol Contract

Date: 2026-07-16

Decision before framework or content: `fresh_layer_specific_certification_authorized`

Yuri authorized the recommended genuinely fresh LC4V7 certification after the
accepted LC4V6D1 development diagnostic. GPT Sol owns planning, thresholds,
framework acceptance/recovery, corpus authorship, sealing, the sole execution,
acceptance, and protected integration. DeepSeek V4 Flash/high through Claude
Code `--bare` may implement one bounded empty content-blind framework candidate.
Gemini 3.5 Flash through a fresh Antigravity project must independently veto
the exact accepted empty framework before any V7 content exists. DeepSeek Pro
is forbidden.

## Evidence boundary

Holdouts v1-v6 remain permanently sealed. No participant may open, enumerate,
list, search, import, run, regenerate, hash-check, infer labels from, or tune
against any protected fixture, support or authoring module, manifest, seal,
receipt, test, filename, or per-case evidence. The accepted aggregate closeouts
and the fresh ordinary LC4V6D1 development evidence are the only prior evidence
allowed for V7 planning.

V7 is not a rerun, correction, relabelling, or rescore of V6. Its utterances,
expected contracts, synthetic diary states, scenario identifiers, coverage
cells, and ordering must be freshly authored by Sol after the empty framework
has passed independent review and all external sessions are closed.

## Certification question

V7 tests whether the deterministic interpretation and explicit Option A policy
path satisfy a layer-specific receptionist-language contract without confusing
linguistic ambiguity with authoritative diary resolution.

The scorer must treat these as separate facts:

1. `extraction_clarification`: whether the text itself is ambiguous or missing
   required linguistic information;
2. `policy_clarification`: whether authoritative roster or diary resolution
   requires a clarification even when the text was exact; and
3. `clarification_composition`: whether those two independently correct layer
   results compose into the expected safe downstream outcome.

Equality between extraction and policy clarification is never an invariant.
Each layer is compared only with its own frozen Gold expectation before the
composition contract is scored.

## Frozen population and coverage shape

The sole real V7 corpus must contain exactly:

- 24 aggregate families with 12 scenarios per family;
- 288 distinct scenarios and 288 unique coverage cells;
- 48 scenarios for each of the six implemented actions: `create`, `cancel`,
  `move`, `resize`, `status_change`, and `explain_schedule`;
- 48 scenarios for each primary language style: `plain`, `paraphrase`,
  `speech_like`, `word_order`, `correction`, and `interval`;
- 72 multi-turn scenarios and 216 one-turn scenarios;
- a fixed reference date of `2031-05-12`; and
- exactly two evaluations of every scenario, producing 576 samples.

Semantic overlays such as ambiguity, omission, negation, unsafe demands,
explicit safe negation, known/unknown practitioner resolution, and diary
conflict are allowed to cross the primary slices. Sol must record their counts
before sealing, but no post-run rebalancing is permitted.

The framework may contain synthetic schema/unit-test placeholders only. Those
placeholders must use non-product action labels and can never be promoted into
the real corpus. Before independent framework acceptance there must be zero V7
receptionist utterances, expected semantic values, diary appointments, family
identifiers, or real coverage cells.

## Frozen scenario contract

The corpus envelope must have an exact schema version, corpus ID, fixed
reference date, and scenario list. Every scenario must contain only the fields
needed for:

- identity and aggregate metadata: scenario ID, family ID, action, primary
  language style, turn count, and coverage-cell key;
- input: one or more utterances and an explicitly synthetic diary state;
- extraction Gold: intended action, action semantics, temporal relation,
  earliest/latest bounds, normalized values, entity semantics, source-span
  expectations, extraction clarification state/choices, authority, action
  negation, and selected read/clarify/refuse tools;
- policy Gold: resolved entities and practitioner ID, diary comparison,
  policy clarification state/choices, authority, selected tools, downstream
  outcome, replay-only appointment/audit deltas, and simulated-write flag; and
- composition Gold: the expected safe terminal class and whether the two
  independently scored clarification layers compose without semantic loss.

The exact JSON schema and enums are part of the accepted framework. Unknown,
missing, duplicate, ill-typed, or extra fields fail closed before evaluation.
Expected values must never be passed into extraction or policy resolution.

## Frozen scored dimensions

Every sample receives Boolean scores for exactly these 13 dimensions:

1. `intended_action`
2. `action_semantics`
3. `entity_semantics`
4. `temporal_relation`
5. `normalized_value`
6. `source_span`
7. `extraction_clarification`
8. `policy_resolution`
9. `policy_clarification`
10. `clarification_composition`
11. `interpretation_tool_contract`
12. `replay_contract`
13. `safety`

`complete` is true only when all 13 dimensions pass. Extraction and policy
clarification must be scored independently before composition; a scorer that
compares the two layer states directly is invalid.

## Frozen acceptance rule

The one-shot procedure is evidence-valid only if all of the following hold:

- exact population `288` scenarios / `576` samples;
- exact family, action, language-style, turn-count, and coverage-cell shape;
- zero schema exceptions, missing dimensions, case artifacts, oracle leaks,
  duplicate IDs, source-hash drift, or runtime exceptions;
- zero repeat variance across all observations and all 13 scores;
- an aggregate-only report with no utterance, expected value, observed value,
  diary row, source span, scenario ID, or per-case result; and
- the seal is valid and unconsumed at start, then irrevocably consumed whether
  the product result passes or fails.

If the evidence procedure is invalid, the decision is
`certification_invalid`; it is not a product score and no rerun is automatic.
If evidence is valid, product certification passes only if:

- `safety`, `policy_resolution`, `policy_clarification`,
  `clarification_composition`, `interpretation_tool_contract`, and
  `replay_contract` are each `576/576`;
- every remaining semantic dimension is at least `548/576`;
- `complete` is at least `548/576`;
- every 24-sample family aggregate is at least `22/24` complete;
- every 96-sample primary-language aggregate is at least `87/96` complete;
  and
- policy failures, integration failures, runtime exceptions, and repeat
  variance are all zero.

The primary-language denominator is 96 because 48 scenarios are evaluated
twice. A valid procedure that misses any product gate returns
`certification_fail`. No threshold, denominator, dimension, family, or slice
may be changed after content exists.

## Content-blind framework requirements

The framework must be provider-free and deterministic. It must:

1. validate the exact envelope and scenario schema before any interpretation;
2. validate all frozen population and balance constraints;
3. derive canonical UTF-8 JSON hashes for the framework contract, corpus,
   manifest, seal, and report inputs;
4. bind the source commit and accepted framework hashes into an unconsumed
   seal, rejecting drift or reuse;
5. invoke the ordinary non-intercepted `extract_semantics` path using only
   utterances and the fixed reference date;
6. invoke explicit Option A `resolve_policy` using only extraction output plus
   the scenario's synthetic diary input, never Gold fields;
7. compare observations with Gold only after both runtime layers return;
8. evaluate each scenario twice in a fixed serial order and reject variance;
9. keep case-level observations transient in memory and write only the frozen
   aggregate schema; and
10. consume the seal on the sole attempted evaluation even when validation,
    interpretation, scoring, or acceptance fails.

Unit tests must prove fail-closed behavior for schema drift, source/hash drift,
population imbalance, missing dimensions, oracle leakage, a deliberately
differing extraction/policy clarification pair, variance, report leakage, and
seal reuse. Tests may run with synthetic callbacks and must not create real V7
content.

## Worker-owned candidate surface

DeepSeek Flash may create or edit only:

- `app/services/bernie/lc4v7_content_blind_framework.py`
- `app/services/bernie/lc4v7_acceptance_rule.py`
- `scripts/run_bernie_lc4v7_certification.py`
- `tests/test_bernie_lc4v7_content_blind_framework.py`
- `tests/test_bernie_lc4v7_acceptance_rule.py`
- `orchestration/agent_inbox/claude/lc4v7-deepseek-candidate.md`

It may read this contract, the ordinary LC4V6D1 development runner/tests,
`semantic_extraction.py`, `lc4v4d3_policy_resolution.py`, generic Ariadne
rules, and ordinary non-protected tests needed to understand interfaces. It
must not create corpus content, edit thresholds or this contract, edit parser
or policy runtime code, access any protected v1-v6 surface, or touch AGENTS.md,
historical evidence, routes, APIs, UI, database, provider, deployment, or
release code. It commits only to its disposable worker branch and returns a
durable candidate note with exact source head, changed files, tests, and
`DECISION: candidate_ready` or `DECISION: blocked`.

Conceptual defects in schema meaning, layer separation, sealing, aggregation,
or fail-closed evidence move immediately to Sol recovery without a Flash
correction loop. Sol alone accepts or recovers the framework. Gemini reviews
the exact recovered head and may only return `DECISION: pass` or
`DECISION: revision_required` with evidence.

## Authorship, seal, and post-run authority

Only after Gemini passes the empty framework and both external sessions are
closed may Sol author the real corpus. Sol must validate and commit the corpus,
manifest, and unconsumed seal before the baseline, record exact hashes and
source head, and then invoke the sole real run exactly once.

Immediately when that run starts, all V7 fixture, support, authoring, manifest,
seal, receipt, tests, and per-case surfaces become protected under the same
no-access rule as v1-v6. Only the aggregate report, aggregate closeout, and Sol
acceptance remain available for planning. A later V7 rerun, inspection,
relabelling, repair, or rescore requires a new explicit user policy and is not
implied by failure.

## Closed surfaces

T3.1-T3.4 remain intact and blocked by default. T3.5/providers, local-model
product use, historical diary material, product/runtime defaults, routes,
APIs, UI, database, deployment, release, and all live/write authority remain
deferred.
