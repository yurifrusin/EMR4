# Bernie Language Coverage Implementation Plan

Status: approved course correction; implementation not started

Date: 2026-07-14

## Purpose

This plan corrects an overly narrow assumption in the first T2/T3 sequence:
strong deterministic diary tests do not by themselves demonstrate that Bernie
can reliably understand the varied language used by reception staff.

The existing work remains necessary:

- T1 supplies deterministic stateful diary replay;
- T2 supplies the deterministic policy and outcome oracle; and
- T3.1-T3.4 supply provider-neutral, write-disabled shadow-evaluation contracts.

The missing layer is a systematic bridge between open-ended receptionist
language and the finite typed semantics accepted by the deterministic diary
kernel. T3.5 provider adapters are deferred until this bridge has a credible
corpus, coverage model, and integrated evaluator.

## Feasibility And Success Claim

It is not possible to enumerate every utterance a receptionist might use. It is
feasible to:

1. define the finite diary action, entity, temporal, dialogue, state, and safety
   space;
2. measure which meaningful combinations have evidence;
3. use authored examples, real workflow evidence, language models, and
   metamorphic generation to search the open-ended language surface;
4. map every candidate utterance into one typed semantic contract;
5. replay that contract against deterministic synthetic diary state; and
6. turn every confirmed failure or novel pattern into permanent regression
   evidence.

Success therefore means defensible behavioural coverage with a continuous gap
discovery process. It does not mean a claim that all possible language has been
exhausted.

## Architectural Boundary

```mermaid
flowchart LR
  U["Original receptionist utterance"] --> N["Lossless normalization and annotations"]
  N --> I["Deterministic or model interpreter"]
  I --> S["Typed ReceptionScenarioSpec semantics"]
  S --> O["T2 deterministic diary oracle"]
  O --> R["Outcome, clarification, tools, and write-delta evidence"]
  C["Coverage lattice and corpus factory"] --> U
  R --> G["Gap and regression ledger"]
  G --> C
```

The interpreter may propose semantics. Code-owned contracts decide whether the
semantics are valid, whether clarification is required, what tools are allowed,
what the diary state means, and whether any later write may be offered. A model
is never the outcome oracle or write authority.

## Canonical Scenario Contract

The first implementation tranche should introduce a versioned
`ReceptionScenarioSpec` or equivalent with these fields:

- synthetic initial diary state and deterministic clinic clock;
- one or more original dialogue turns;
- the intended, ambiguous, or prohibited diary action;
- patient, practitioner, location, appointment type, and duration semantics;
- a temporal relation such as `exact`, `not_before`, `not_after`, `interval`,
  `approximate`, or `unspecified`;
- normalized values plus source spans back to the original utterance;
- expected clarification requirements and acceptable choices;
- expected deterministic diary outcome and tool sequence;
- expected appointment/audit deltas and forbidden outcomes;
- corpus provenance, evidence tier, adjudication state, and scenario family.

The temporal relation is required because `at 3pm`, `after 3pm`, `before 3pm`,
`around 3pm`, and `between 3 and 4pm` must not collapse into one overloaded
`earliest_time` representation.

## Language Processing Policy

The authoritative path must preserve the original utterance. It may derive a
lossless matching view using Unicode normalization, whitespace normalization,
case folding, punctuation variants, number/time forms, and approved domain
abbreviations.

Stop-word removal, stemming, and lemmatization must not replace the original
input or determine authority. Words such as `at`, `before`, `after`, `from`,
`to`, `not`, and `without` can change booking semantics. Lemmas, stems, and
stop-word-reduced views may be used only for offline clustering, deduplication,
retrieval, and corpus statistics. Any semantic extraction must retain source
spans and be checked against the original utterance.

## Coverage Lattice

Coverage must be measured across intersecting dimensions rather than by a raw
scenario count:

- diary action: create, move, resize, cancel, status and later promoted verbs;
- diary state: empty, exact duplicate, overlap, same-day distinct, terminal,
  stale, concurrent, roster absent, break, no slots, and elapsed window;
- entity state: exact, omitted, ambiguous, corrected, negated, or mismatched;
- temporal form: absolute, relative, exact point, open bound, interval,
  approximate, locale variant, date boundary, daylight-saving boundary;
- dialogue form: one-shot, clarification, correction, reversal, ellipsis,
  anaphora, repeated request, and session restart;
- language form: paraphrase, politeness/filler, abbreviation, typo, speech-like
  transcript, punctuation variation, and adversarial instruction; and
- authority/accessibility: confirmation boundary, stale evidence, keyboard,
  screen reader, and later hands-free workflow.

A complete Cartesian product is neither economical nor necessary. Acceptance
requires every individual capability, broad pairwise coverage, targeted
three-way coverage for high-risk interactions, and explicitly authored hazard
cases. The coverage report must identify empty cells rather than hiding them in
an aggregate pass rate.

## Corpus Evidence Tiers

### Gold

Independently adjudicated semantics and expected outcomes. Sources include
hand-authored workflow cases, synthetic-diary receptionist simulations,
confirmed user-test failures, and later consented/deidentified shadow examples.

### Silver

Model-generated paraphrases, minimal pairs, corrections, ambiguity variants,
misspellings, and adversarial forms derived from a Gold semantic scenario.
Silver cases require deterministic schema validation and independent review;
the same model must not generate, label, and certify a case.

### Bronze

Unadjudicated discovery material from historical diary transitions, licensed
external dialogue corpora, clustering, or model suggestions. Bronze material
may propose a scenario family but cannot enter promotion scoring until its
semantics are independently adjudicated.

## Historical Diary Boundary

The historical diary trove can help discover appointment-state patterns,
frequencies, unusual transitions, and multi-step workflow skeletons. It cannot
recover the receptionist's original words, caller intent, or reason for a
change from snapshots alone.

Any future use must:

- remain local and comply with the existing H-series/H15 privacy gates;
- extract only source-safe transition hypotheses;
- convert those hypotheses into synthetic diary states and synthetic entities;
- avoid claiming that generated utterances are historical utterances; and
- require adjudication before promotion beyond Bronze evidence.

A broad trove pass remains a separate decision boundary under the existing
gate. This plan does not authorize it.

## Metamorphic And Adversarial Generation

Each Gold semantic scenario should generate relations that can be checked
without asking a model to invent the expected answer:

- paraphrase and harmless filler should preserve semantics;
- changing `at` to `after`, `before`, or `around` should change only the
  temporal relation in the expected direction;
- changing a practitioner, patient, date, or duration should change only that
  field unless the result becomes ambiguous or invalid;
- negation must never be discarded;
- a correction turn must supersede only the corrected field;
- attempts to bypass confirmation must not change authority; and
- repeating an idempotent or already-satisfied request must not create a second
  write.

Property and mutation testing should deliberately damage parser rules,
normalization, temporal relations, and outcome handling to demonstrate that the
corpus detects plausible regressions.

## Integrated Evaluation

For each corpus variant, the evaluator should:

1. preserve the original utterance and derive the lossless normalized view;
2. obtain typed semantics from the deterministic fallback or candidate model;
3. validate the semantics and compare each field with the adjudicated contract;
4. execute the semantics through T2 against synthetic state with writes
   disabled except for explicitly simulated confirmed turns;
5. compare outcome, clarification, tool selection, authority, and row deltas;
6. record repeat variance and unsafe claims separately; and
7. classify the failure layer as interpretation, policy, integration, UI, or
   safety rather than reporting one undifferentiated score.

Correctness must be reported by critical coverage slice and worst-performing
slice. Cost, latency, and token usage remain operational metrics and cannot
compensate for semantic or safety failure.

## Implementation Tranches

These are product tranches with internal tasks, not a requirement to create a
separate coordination sprint for each bullet.

### LC1 - Semantic Foundation And Known Regression

Implementation status: complete on 2026-07-14. Evidence and remaining gaps are
recorded in `docs/bernie-lc1-semantic-foundation.md` and
`docs/bernie-lc1-coverage-gap-report.json`.

- Add a failing regression for Yuri's real `tomorrow at 3pm` request through
  the non-intercepted interpretation path.
- Cover `3pm`, `3 pm`, `3.00pm`, `15:00`, and exact/open/approximate temporal
  operators.
- Introduce the canonical scenario contract and lossless normalization policy.
- Adapt a small independent set of existing T1/T2 scenarios to the contract.
- Produce the first machine-readable coverage lattice and gap report.

Exit: the known exact-time request reaches the correct deterministic duplicate
outcome without a second write; point time and open bounds cannot be confused;
and missing coverage remains visible.

### LC2 - Corpus Factory And Independent Adjudication

Implementation status: complete on 2026-07-14. The deterministic factory and
provenance rules are documented in `docs/bernie-lc2-provenance-rules.md`; the
bounded 15-case generator is documented in
`docs/bernie-lc2-candidate-generation.md`; and Gemini's independent veto pass
plus six adversarial probe envelopes are recorded in
`docs/adversarial/lc2_independent_review.md`. Every generated case remains
Silver/pending with no judge or promotion record. Sol's executable acceptance
confirmed two promotion-time quarantines, three fail-closed candidate payloads,
and one fail-closed adjudication payload; these outcomes are locked by
`tests/test_bernie_corpus_adversarial.py`.

- Implement Gold/Silver/Bronze provenance and promotion rules.
- Add bounded multi-model paraphrase, minimal-pair, ambiguity, correction, and
  adversarial generators.
- Add independent review and a quarantine queue for disagreement.
- Evaluate external task-dialogue corpora for licensing and linguistic forms.
- Define synthetic-diary receptionist elicitation without production PHI.

Exit: generated variants cannot silently become Gold, generator/judge
independence is enforced, and corpus additions are reproducible.

### Channel And External-Source Posture After LC2

Text remains the deliberately hard surface-form problem. Typed instructions
and future ASR transcripts must enter the same canonical scenario contract and
lossless normalization layer. Voice is not assumed to be a semantic subset of
text: ASR alternatives, confidence, prosody, and homophones such as
`three/free` remain channel evidence. The future voice adapter should preserve
the raw transcript and alternatives, then emit the same typed relations,
entities, source coordinates, and uncertainty fields. No separate voice
ontology or voice sprint is required before LC3.

The suggested healthcare appointment-booking calls dataset is registered only
as metadata and remains no-import pending licence provenance, recording
consent, privacy/jurisdiction, leakage, and local-processing review. It may
later supply booking-language evaluation surfaces; it is not training or
semantic truth evidence in LC2.

The suggested MedInstruct/AI-doctor fine-tuning dataset is a future
consult-assistant (Davida/GP-assistant) evaluation candidate, not a Bernie LC2
source and not a clinical oracle. Do not download, train on, or promote it
without underlying source-by-source provenance and licence review, PHI/leakage
assessment, clinical-safety review, and Australian general-practice
applicability checks. A Kaggle wrapper licence is not sufficient evidence for
the mixed upstream sources.

### LC3 - Composed T2/T3 Evaluator

Status: complete and independently reviewed on 2026-07-14.

- Run every language variant through typed interpretation and deterministic
  diary replay.
- Add field-level, downstream-outcome, tool, authority, clarification, and
  variance scoring.
- Add metamorphic, property, and mutation tests.
- Produce critical-slice and empty-cell reports.

Exit: failures identify the responsible layer, and intentionally introduced
semantic/parser defects are detected.

LC3 composes the three adjudicated LC1 scenarios and fifteen Silver/pending LC2
candidates into 36 deterministic samples (two repeats each). The committed
report records 26 passes and 10 honest failures, with interpretation and
integration layers separately visible, zero policy/safety/variance failures,
seven passing metamorphic relations, and nine detected scorer mutations. The
candidate-aware lattice retains all 152,061 adjudicated empty cells while
showing seven distinct candidate-only cells; pending evidence does not reduce
Gold gaps. Gemini 3.5 Flash independently returned `DECISION: pass` after
reproducing the focused tests and lattice arithmetic. No candidate was promoted.

### LC4 - Scale And Holdout Evaluation

Status: complete and independently reviewed on 2026-07-14.

- Grow to roughly 100-150 meaningful semantic scenarios with 10-30 linguistic
  variants each, plus several hundred multi-turn trajectories.
- Keep a protected holdout sourced or generated independently from the models
  being evaluated.
- Prioritize harm, frequency, observed novelty, and empty coverage cells rather
  than raw case count.

These are operational starting targets, not proof of completeness.

LC4 met the bounded target with exactly 120 semantic groups, 1,440 variants,
and 360 multi-turn trajectories. The 96-group development partition remains
Silver/pending and produced 0/2,304 complete passes, zero safety failures, and
zero repeat variance. Its 444 candidate-only cells do not reduce the 152,061
adjudicated gaps. Gemini 3.5 Flash independently passed the framework before
the actual holdout existed.

Sol then authored and sealed the 24-group Gold/adjudicated protected holdout.
The first and only `lc4-holdout-v1` baseline produced 0/576 complete passes,
576 interpretation and policy attributions, 538 integration attributions,
eight safety failures, and zero repeat variance. It adds 264 new adjudicated
cells, leaving 151,797 empty. The committed report is aggregate-only; v1 must
not be rerun or tuned against without an explicit reviewed reuse policy or a
new holdout version.

### LC4R - Deterministic Semantic Gap Repair

Status: LC4R1-LC4R10 complete on 2026-07-15.

LC4R was the next credibility tranche before live-model comparison. It used only
the development partition and ordinary authored regression fixtures. It must
not read, re-evaluate, regenerate, or tune against protected holdout labels.

- Repair lossless normalized-value extraction, entity semantics, explicit
  temporal relations, clarification state reduction, and interpretation/replay
  tool selection through the non-intercepted deterministic path.
- Preserve the honest layer attribution exposed by LC4 rather than optimizing
  only the all-pass aggregate.
- Add development regressions for safe negated completion/bypass language
  without disclosing the protected cases that exposed the class.
- Keep Silver/pending discovery separate from Gold/adjudicated evidence.
- Define a new holdout version or explicit reviewed reuse policy before another
  certification evaluation.

Exit: the deterministic language bridge has credible development evidence
across critical slices and no unresolved safety regression, sufficient to make
provider-shadow comparison informative rather than merely confirm universal
semantic failure.

### LC5 - Live-Model Shadow And Continuous Learning

- Resume T3.5 DeepSeek and Gemini adapters behind the existing gate.
- Run repeated write-disabled samples against synthetic state.
- Track exact model/prompt/tool-schema versions and separate cost/latency from
  correctness.
- Promote confirmed failures and novel patterns into the adjudication queue.
- Later add consented/deidentified local shadow intake under an approved data
  and retention policy.

Exit: model comparison is based on critical semantic slices, safety, and
variance, not average accuracy or persuasive output.

### LC4V2 - Fresh Certification Holdout

Status: procedure complete on 2026-07-15; product-readiness baseline failed.

After LC4R10 reconciled the frozen development populations, Yuri authorized a
genuinely fresh holdout instead of reusing v1. DeepSeek implemented only a
content-blind candidate framework; Sol rejected its conceptual fail-open gaps
and recovered under the lease. Gemini independently passed the recovered
framework before actual content existed. Sol alone then authored, sealed, and
consumed the 24-group, 288-variant, 72-multi-turn Gold corpus exactly once.

The 576-sample aggregate baseline produced 0 complete passes, 576 temporal
relation passes, 528 intended-action passes, 410 action-semantics passes, 288
normalized-value passes, zero entity-semantics passes, 308 clarification
passes, 532 safety passes, and zero repeat variance. The construction and
one-shot evidence procedure passed; Bernie product readiness did not. Holdout
v2 is sealed alongside v1 and cannot be used for remediation.

Before LC5 live execution, use only aggregate findings and ordinary
development evidence to repair entity semantics, normalization, clarification,
and safety. A later certification requires a newly authorized fresh holdout or
reviewed reuse policy.

## Agent Allocation

- Sol at High reasoning owns the semantic architecture, coverage decisions,
  authority boundaries, and tranche acceptance.
- Sol Extra High/`max` is reserved for ontology freeze, independent final audit,
  or a live-model promotion decision where the additional reasoning has clear
  leverage.
- Protected Sol directly plans and allocates ordinary bounded sprints.
- DeepSeek Pro is an optional compact consultant for programme/architecture
  leverage or repeated failure, not the routine Conductor.
- DeepSeek Flash and Gemini Flash are suitable for implementation, bulk variant
  generation, independent adversarial passes, and economical repeat runs.
- A model must not certify its own generated corpus. Deterministic validators
  and human adjudication retain final corpus authority.

## Immediate Direction

The next EMR4 product tranche is aggregate-guided development repair, not live
T3.5 execution. LC4V2 confirms that explicit temporal relations generalized,
but entity semantics, normalized values, clarification, and safety still make
the deterministic language bridge non-credible at scale. Repair only against
ordinary development evidence without inspecting or reusing sealed holdouts
v1 or v2. Do not promote Silver/pending candidates merely because the
evaluator can execute them.

No user decision is required for ordinary development-only repair work. Pause if
work would reuse/re-evaluate protected holdout v1 or v2, broaden historical-trove
access, send sensitive data to a provider, accept material licensing/cost
terms, open live-provider execution, or change diary write authority.

## Restart Rehydration

After restarting the app, a new orchestrator should read `AGENTS.md`, this plan,
the T1/T2 closeouts, the T3 shadow-evaluation status, and the active acceptance
named in the Current Baton before changing code. It should verify `master`,
`handoff/current`, and their origin refs; confirm the LC4R10 and LC4V2
closeouts; preserve both sealed holdouts; and keep the blocked T3 gates intact.
Ordinary development-only repair may continue without reopening T3.5 or asking
for routine permission.

Recommended new-task prompt:

```text
Resume EMR4 development from the committed handover on master. Rehydrate from
AGENTS.md and read docs/bernie-language-coverage-implementation-plan.md,
docs/bernie-t1-stateful-scenario-laboratory.md,
docs/bernie-t2-deterministic-behaviour-matrix.md, and
docs/bernie-t3-shadow-evaluation.md. Verify the worktree and origin/master,
then begin an aggregate-guided development-only semantic repair and corpus-
engineering tranche through the normal Ariadne workflow. Use only the
development partition and newly authored ordinary regressions; do not open,
list, search, rerun, regenerate, hash-check, infer from, or tune against sealed
holdouts v1 or v2. Prioritize entity semantics, lossless normalization,
clarification state, and safety while preserving the accepted temporal
foundation. Preserve corpus provenance and keep candidate evidence separate
from adjudicated gaps. Preserve T3.1-T3.4 and defer T3.5 provider adapters and
live calls. Continue
through ordinary implementation, tests, review, commit, and push without
pausing unless a documented user decision boundary is reached.
```
