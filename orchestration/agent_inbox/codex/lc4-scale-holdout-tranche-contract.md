# LC4 Scale and Protected Holdout Evaluation — Tranche Contract

Active planner, semantic/holdout owner, acceptance owner, and protected
integrator: GPT Sol. Routine external Conductor consultation is skipped because
LC4 is the already-approved next tranche and changes no product authority.

Settings fingerprint:
`sha256:0dce975ccb05026a186df59313345590af2552a2364c944606ada9372dc617dd`

## Direction-dialogue disposition

Skipped. The committed language-coverage plan fixes LC4's direction and exit
criteria. DeepSeek Pro is not used as routine Conductor. DeepSeek Flash owns
bounded development-corpus/framework implementation; Gemini Flash supplies an
independent framework veto before the protected holdout is created.

## Bounded scale target

LC4 produces a reproducible synthetic corpus with exactly:

- 120 meaningful semantic groups;
- 12 linguistic variants per group (1,440 variant scenarios total);
- exactly 3 multi-turn variants per group (360 trajectories total);
- 96 development groups / 1,152 variants / 288 trajectories; and
- 24 protected-holdout groups / 288 variants / 72 trajectories.

The group, not the surface paraphrase, is the semantic counting unit. Each
group has one canonical semantic contract and twelve independently validated
surface variants. Variant IDs, stable hashes, source spans, normalized values,
and expected fields remain lossless and reproducible.

At least 72 groups must target one or more measured LC3 weaknesses:
clarification dialogue, `interval`/`unspecified` temporal relations,
ambiguous/omitted/corrected entities, or interpretation/replay tool selection.
All six diary actions, all six temporal relations, every entity-state class,
all dialogue forms, all language forms, and all eleven diary states must appear.
Every action and temporal relation must have at least twelve semantic groups.
Coverage priority is harm/frequency/novelty/gap driven; raw Cartesian volume is
not an acceptance argument.

## Evidence tiers and claims

- The 96 development groups are DeepSeek-generated Silver/pending discovery
  evidence. Their variants inherit that provenance. They cannot reduce Gold
  lattice gaps, certify parser correctness, or be promoted in LC4.
- The 24 holdout groups are authored and sealed by protected Sol only after all
  DeepSeek and Gemini implementation/review work ends. They are synthetic
  Gold/adjudicated evaluation evidence with no provider-model generator.
- No external dataset, historical diary, patient/practice data, or PHI is used.
- A pass fraction is a baseline for this finite corpus, never a claim of broad
  natural-language completeness.

## Protected holdout boundary

The holdout is a strict evaluation partition, not another tuning fixture.

1. DeepSeek and Gemini receive no actual holdout utterance, label, blueprint,
   scenario ID, or per-case result during LC4 construction.
2. Worker branches are cut before Sol creates the real holdout material.
3. Generic holdout APIs may be implemented and tested only with miniature
   clearly-labelled dummy fixtures that are not part of the 24-group holdout.
4. Default loaders and evaluators select development only. Real holdout access
   requires an explicit sealed-evaluation capability carrying the expected
   manifest hash, purpose, evaluator identity, and one bounded evaluation ID.
5. Development generation, mutation, parser-tuning, promotion, and gap-closing
   APIs must reject the holdout capability and holdout records.
6. The committed holdout report exposes aggregate/slice counts and stable
   manifest/report hashes only. It must not emit utterances, expected labels,
   source spans, normalized values, case findings, scenario IDs, or per-case
   failures.
7. The first closeout evaluation consumes holdout version `lc4-holdout-v1` once.
   Later implementation must not tune against its per-case labels. Material
   parser changes require a new version or an explicitly documented reuse
   policy before another certification claim.
8. Runtime provider adapters, prompts, and product modules must not import
   holdout labels or evaluation capabilities.

## Scaled evaluator and report

The LC4 evaluator reuses the LC3 scorer and deterministic interpretation/replay
path; it must not introduce an expected-answer echo. For development and sealed
holdout it records separately:

- semantic-group, variant, and trajectory counts;
- per-dimension pass/fail counts;
- simultaneous interpretation/policy/integration/safety attribution;
- action, temporal, entity, dialogue, language, diary-state, and gap-priority
  slices;
- deterministic repeat variance, with cost/latency excluded from correctness;
- aggregate critical-slice and worst-slice evidence;
- candidate-aware lattice discovery counts that preserve adjudicated gaps; and
- corpus/partition/manifest/report hashes.

The development report may include bounded case identifiers for repair. The
holdout report is aggregate-only. Honest failures are expected and must remain
visible. No threshold may be chosen after seeing holdout results merely to make
LC4 pass.

## Metamorphic, property, mutation, and contamination guards

Tests must prove at least:

- all 1,440 variants validate through the canonical scenario model;
- every group has exactly twelve variants and three multi-turn trajectories;
- harmless variants retain their group's semantic contract;
- declared minimal pairs change only their declared field;
- clarification/correction/reversal/ellipsis/anaphora state reduction is
  lossless outside the changed field;
- unsafe/adversarial variants cannot claim completion or create a second write;
- group/variant IDs and hashes are unique and deterministic;
- shuffled input produces the same aggregate report;
- a duplicate, missing, cross-partition, mislabeled, or tampered record fails
  closed;
- development APIs cannot read, mutate, promote, or report holdout labels;
- holdout access with the wrong hash, purpose, evaluator, evaluation ID, reuse,
  or output shape fails closed; and
- representative semantic, outcome, tool, authority, clarification, delta,
  slice, partition, and hash mutations are detected.

## Closed boundaries

- No provider SDK/adapter, live prompt, external call, or raw model response.
  T3.5 remains deferred.
- No route, GraphQL, OpenAPI, database model, migration, appointment/audit
  persistence, confirmation, UI, runtime wiring, deployment, or release change.
- No historical-diary/H-series/H15 access, memory, RAG, or GraphRAG.
- No external dataset download or licence acceptance.
- T3.1-T3.4 and both blocked interpretation/live-replay gates remain intact.
- No model certifies or promotes its own corpus, and no worker has protected
  integration or push authority.

## Worker allocation

| Lane | Role | Invocation | Ownership |
|---|---|---|---|
| DW1 | Development scale-corpus framework and 96-group Silver/pending corpus | DeepSeek V4 Flash/high through Claude Code `--bare` | New generic scale-corpus module, development generator/fixture/report script, focused tests, developer documentation |
| DW2 | Generic scaled evaluator, partition/report hashing, dummy holdout capability, contamination/mutation tests | DeepSeek V4 Flash/high through Claude Code `--bare`, after DW1 acceptance | New LC4 evaluator/report module and script/tests; bounded reuse of LC3 public APIs only |
| AG | Independent pre-holdout framework/adversarial veto | Gemini 3.5 Flash/medium through a fresh Antigravity worktree | Review artifact and generic adversarial tests only; actual holdout is absent and prohibited |
| Sol | Actual 24-group holdout authorship/seal, one aggregate evaluation, final deterministic acceptance/integration | Protected primary session | Holdout fixture/manifest, seal receipt, aggregate-only report, handover/closeout |

Claude subscription and Deep Code lanes are stood down. Deep Code remains a TTY
fallback only after a recorded bare-mode failure. At tranche start there are no
active or stale DeepSeek worker instances.

## Integration order

1. Commit this contract on `codex/lc4-staging` after a passed pre-plan receipt.
2. Dispatch and accept DW1 in a fresh disposable worktree; run focused tests.
3. Integrate DW1, then dispatch and accept DW2 from the new staging head.
4. Create a fresh Antigravity worktree, run the independent framework veto, and
   resolve every concrete finding. No real holdout exists yet.
5. End all external worker/reviewer activity. Sol authors and seals the 24-group
   holdout, executes its first aggregate-only baseline once, and owns any
   mechanical corrections without exposing labels externally.
6. Run LC1-LC4 plus T1/T2/T3.1-T3.4 gates serially; update the plan, T3 status,
   handover, and integration log.
7. Commit, fast-forward protected `master` and `handoff/current`, push, and read
   back all local/remote refs.

## Acceptance and pause boundaries

LC4 exits only when the exact 120/1,440/360 scale contract is met, the 96/24
partition and holdout contamination guards pass, development and aggregate-only
holdout reports reproduce exactly, honest failures/slices remain visible, all
required dimensions and measured gaps are covered, and the full deterministic
regression gate has no unresolved failure.

Pause only if work would broaden historical-trove access, transmit sensitive
data, accept material licence/cost terms, open live-provider calls, change
write/confirmation authority, or materially change this sprint's scope or
ownership. Dependabot alert 5 remains open; do not force overrides.

Sprint engine state: continuing.
