# LC4V2 Sol Fresh-Holdout Contract

## User decision and authority

Yuri approved the recommended new holdout-v2 path on 2026-07-15. This approval
authorizes a fresh synthetic certification holdout and one initial aggregate
baseline. It does not authorize reuse of holdout v1, T3.5 provider adapters,
live provider calls, product/runtime wiring, deployment, release, historical
diary access, or any write authority.

GPT Sol is Conductor, architecture and acceptance owner, sole v2 content
author, seal owner, one-shot evaluation owner, and protected integrator.
DeepSeek V4 Flash/high through Claude Code `--bare` may implement only the
content-blind framework described below. Gemini 3.5 Flash through a fresh
Antigravity project may review that framework only before v2 content exists.
Neither worker may generate, inspect, label, review, evaluate, certify, or
receive actual v2 cases.

## Protected-evidence boundaries

Holdout v1 remains sealed under its existing prohibition. Do not open,
enumerate, list, search, import, run, regenerate, evaluate, hash-check, infer
from, or tune against any v1 fixture, support module, seal, receipt, or report.
LC4V2 must be created from the canonical public scenario contract, the accepted
LC4R10 development capabilities, the coverage-lattice dimensions, and newly
authored synthetic cases only. It must not copy or reconstruct v1 content.

Before actual v2 content is authored:

1. freeze and commit this contract;
2. implement a content-blind manifest, seal, aggregate-report, and one-shot
   consumption harness with synthetic tests only;
3. obtain an independent Gemini framework veto on the exact framework head;
4. close all external worker sessions; and
5. verify protected-master cleanliness and the absence of provider processes.

After actual v2 content exists, no external model or worker may receive or read
it. Sol performs all remaining authoring, verification, baseline, acceptance,
commit, and push work directly.

## Fresh corpus contract

- version: `lc4-holdout-v2`;
- evidence: synthetic Gold/adjudicated;
- author: protected Sol only;
- scale: exactly 24 semantic groups and 288 variants, including exactly 72
  multi-turn trajectories;
- group shape: exactly 12 variants per group, with three multi-turn variants;
- all entities and diary state are synthetic;
- every scenario validates as `ReceptionScenarioSpec`;
- expected labels, source spans, outcomes, tools, appointment deltas, and audit
  deltas are authored independently of interpreter observations;
- every source span is lossless against the original dialogue turn;
- `expected_outcome_kind` is always present and may be explicit null only for a
  deliberately delta-free contract;
- `check_in` and every other planned-not-implemented action remain excluded;
- no provider prompt, response, production data, historical diary text, or
  copied development utterance enters the corpus.

The 24-group blueprint must cover all four implemented scheduling actions
(`create`, `move`, `resize`, `cancel`), exact/open/interval/approximate temporal
relations, the accepted diary-state policy surface, exact/omitted/ambiguous/
corrected/negated/mismatched entity states, one-shot and multi-turn dialogue,
and plain/paraphrase/filler/abbreviation/typo/speech-like/punctuation/adversarial
language forms. High-risk negation, correction, reversal, stale/concurrent,
duplicate/overlap, roster/break/no-slot, and elapsed-window cases must be
represented without deriving expected answers from current parser output.

## Seal and one-shot baseline

The v2 manifest binds every group and variant plus the full corpus hash. The
consumption seal binds:

- version and manifest hash;
- exact source commit evaluated;
- evaluator/schema versions;
- evaluation ID `lc4-holdout-v2-baseline-001`;
- two deterministic repeats per variant;
- creation and consumption state; and
- an aggregate-only report hash.

Sol may run pre-consumption schema, source-span, count, manifest, determinism,
and fail-closed tests while authoring. After the sealed corpus/framework source
commit is created, Sol runs the real composed baseline exactly once. The
committed report may expose only aggregate dimension totals, aggregate failure
layers, aggregate safety and variance, predefined critical-slice totals,
coverage-cell counts, hashes, and provenance. It must contain no utterance,
dialogue, group/scenario/variant identifier, expected label/outcome/tool/delta,
source span, normalized value, case finding, or per-case result.

After `lc4-holdout-v2-baseline-001` is consumed, v2 becomes sealed under the
same no-read/no-rerun/no-tuning policy as v1. Final closeout checks may validate
only the committed aggregate schema, receipt state, ordinary development
regressions, Git integrity, and documentation; they may not load or hash-check
v2 content again.

## Content-blind implementation surface

The worker/framework phase may add only:

- a new provider-free v2 manifest/seal/aggregate contract module under
  `app/services/bernie/`;
- a new CLI supporting synthetic/injected source directories and explicit
  create/consume transitions;
- synthetic unit tests using temporary fixtures that are not v2 cases;
- framework documentation and worker provenance.

It must not access v1, create a real v2 fixture directory, embed actual v2
utterances or labels, run the composed baseline, call a provider, or modify
parser/extraction/replay policy.

## Acceptance

- all content-blind framework tests pass and fail closed on malformed schema,
  count/hash drift, forbidden report fields, duplicate consumption, wrong
  source commit, and non-aggregate output;
- Gemini returns `DECISION: pass` on the exact framework head before content
  creation;
- actual v2 matches the exact 24/288/72 contract and coverage blueprint;
- all actual cases validate without reading or deriving from v1;
- the one-shot baseline produces a schema-valid aggregate-only report and a
  consumed seal at the exact sealed source commit;
- ordinary LC4R10 development regressions, T1/T2, and T3.1-T3.4 preservation
  checks remain green without loading either protected holdout;
- master and `handoff/current` are clean, aligned, committed, and pushed; and
- closeout stops before T3.5 or any live-provider execution, which remains a
  separate user decision boundary.
