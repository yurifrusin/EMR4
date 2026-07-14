# LC4R1 Deterministic Semantic Extraction Repair — Sprint Contract

Date: 2026-07-14

Active planner, semantic owner, acceptance owner, and protected integrator:
GPT Sol. Planning mode is `sol_direct_routine`; routine Conductor consultation
is skipped because LC4R is the committed next tranche and this sprint changes
no product, provider, confirmation, or write authority.

Settings fingerprint:
`sha256:0dce975ccb05026a186df59313345590af2552a2364c944606ada9372dc617dd`

## Direction-dialogue disposition

Skipped. The committed LC4 closeout and language-coverage plan already select
development-only deterministic repair. DeepSeek V4 Flash/high through Claude
Code `--bare` owns the bounded implementation lane. Deep Code is a fallback
only after a recorded bare-mode transport failure. Gemini 3.5 Flash will
independently review the accepted implementation in a later LC4R sprint.

## Evidence boundary

LC4R1 may read only the LC1-LC4 development fixtures, ordinary authored tests,
and aggregate committed documentation. It must not read, load, regenerate,
evaluate, hash-check, infer from, or tune against any `lc4-holdout-v1` fixture,
support module, seal receipt, or report. It must not access historical diary
material, external datasets, providers, network services, patient/practice
data, memory, RAG, or GraphRAG.

The 1,152 LC4 development scenarios remain Silver/pending discovery evidence.
Their labels are not parser authority. If a surface phrase conflicts with its
group label—for example, an explicit approximation operator paired with an
`exact` label—the implementation must preserve the phrase's semantics and the
conflict must remain an honest candidate-quality finding.

## Baseline and objective

The one-repeat development baseline is 1,152 scenarios with zero complete
passes and zero safety failures. Semantic passes are: intended action 464,
action semantics 512, temporal relation 477, normalized values 71, entity
semantics 68, and clarification 544. LC4R1 repairs root extraction rather than
optimizing the all-pass aggregate or downstream replay symptoms.

Implement a pure deterministic semantic extraction boundary whose inputs are
only receptionist dialogue turns plus an explicit reference date. It must not
accept a `ReceptionScenarioSpec`, expected outcome, expected tools/deltas,
provenance label, or any other scorer oracle. The existing
`deterministic_interpret` adapter may pass only those permitted inputs into the
new boundary and then project its result into `InterpretationObservation`.

The boundary must:

- retain each original utterance and the existing lossless normalized view;
- classify all current diary actions (`create`, `move`, `resize`, `cancel`,
  `status_change`, `explain_schedule`) from bounded receptionist language;
- distinguish `exact`, `not_before`, `not_after`, `interval`, `approximate`,
  and `unspecified` temporal relations without erasing operator words;
- derive today/tomorrow/day-after-tomorrow dates, time bounds, and explicit
  minute durations from text, including current punctuation/abbreviation forms;
- reduce multi-turn additions and explicit corrections without discarding
  unchanged earlier fields;
- derive exact, omitted, ambiguous, and corrected patient/practitioner/duration
  semantics from the dialogue rather than expected labels;
- determine clarification from missing or ambiguous action-relevant facts, not
  from a blanket "no time and no duration" shortcut; and
- distinguish genuinely unsafe bypass/completion demands from safe negated
  mentions such as "do not bypass confirmation" and "do not mark it
  completed", while never claiming completion or write authority.

## Owned implementation surface

The DeepSeek worker may create one new pure module under
`app/services/bernie/`, integrate it into
`app/services/bernie/composed_corpus_evaluator.py`, and add focused tests plus
one implementation note. It may make narrowly necessary pure helper changes in
`app/services/diary/temporal.py` or
`app/services/bernie/language_normalization.py` only when covered by focused
tests. It must not edit scale-corpus fixtures/generators, holdout code, routes,
API schemas, database models, migrations, provider adapters/prompts, UI,
deployment, T3 gates, AGENTS.md, or protected closeout documents.

## Required regression evidence

Tests must cover, with freshly authored generic wording:

- point-time variants `3pm`, `3 pm`, `3:15pm`, `3.15pm`, and `15:15`;
- after/before/between/about/unspecified temporal relations;
- every current diary action and unknown-action clarification;
- explicit patient/practitioner/duration extraction across ordinary,
  punctuation, and abbreviation forms;
- a missing/ambiguous entity, an additive second turn, a correction, and a
  reversal or negation that must not silently execute the earlier demand;
- unsafe bypass/refusal wording and safe negated bypass/completion wording;
- no expected-answer echo (mutating expected scenario fields must not change
  the observation); and
- no authority value outside `read`, `clarify`, or `refuse`, with
  `claims_action_completed=False` in every case.

## Acceptance gate

Sol will review the diff and rerun focused tests, the LC1 known regression,
LC3 composed evaluation tests, LC4 development evaluator tests, and the T3
shadow gate. Sol will regenerate the development report in memory or a local
ignored path and record exact before/after counts. Acceptance requires:

- every newly authored semantic regression passing;
- no decrease in any of the six baseline semantic pass counts;
- a strict increase in normalized-value, entity-semantics, intended-action,
  temporal-relation, and clarification passes;
- 1,152/1,152 development safety passes and zero repeat variance;
- the real `tomorrow at 3pm` LC1 regression remaining green;
- contradictory Silver labels remaining visible rather than being normalized
  into false agreement; and
- no holdout, provider, route, database, UI, write-authority, or T3.5 change.

No claim of broad natural-language completeness follows from this sprint.

## Worker and integration procedure

1. Commit this contract on `codex/lc4r-staging` after the passed pre-plan
   receipt.
2. Create a disposable worker worktree and fresh branch from the exact staging
   head; obtain a passed pre-dispatch receipt.
3. Dispatch one DeepSeek Flash/high implementation packet through Claude Code
   `--bare`. The worker may create candidate commits but may not push or
   integrate.
4. Sol reviews and amends the candidate if necessary, runs the acceptance gate,
   and integrates only the exact accepted commit set into staging.
5. Commit an LC4R1 evidence note before defining LC4R2.

Pause only for an explicit user stop or if work would cross the sealed-holdout,
historical-data, external-provider/data, material licence/cost, route/API,
database, confirmation, write-authority, deployment, or release boundaries.

Sprint engine state: continuing.
