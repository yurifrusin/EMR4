# LC4R5 Explanation Clarification/Action Semantics — Sprint Contract

Date: 2026-07-14

Active Conductor, sprint planner, architecture/acceptance owner, recovery
owner, and protected integrator: GPT Sol. Planning mode is
`sol_direct_routine`. DeepSeek V4 Flash/high through Claude Code `--bare` owns
one bounded implementation/test lane. Gemini 3.5 Flash through Antigravity
owns the independent veto review. DeepSeek Pro is not a Conductor or worker
for this sprint.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Direction-dialogue disposition

Skipped. Sol's development-only profiling isolated a narrow explanation
clarification defect. There is no architecture or product-policy dispute.
External models do not plan, allocate, accept, or integrate this sprint.

## Protected evidence boundary

Use only the ordinary Silver/pending LC4 development partition and new
independently authored synthetic regressions. Do not open, enumerate, import,
load, regenerate, evaluate, hash-check, infer from, or tune against protected
holdout v1 or any of its fixtures, support modules, seals, receipts, or
reports. Do not inspect historical diary material or transmit patient/practice
data. No provider inference, T3.5 adapter, route/API, database, UI, deployment,
memory, RAG/GraphRAG, confirmation, or write authority is permitted.

The worker must not edit generated development fixtures or use expected
scenario fields inside interpretation. Selection and interpretation must
derive from utterance surfaces only; scenario expectations remain scorer
oracles.

## Frozen development evidence

LC4R4 leaves 584 one-repeat `aligned_failure` records. Exactly 96 are
development scenarios whose intended action is `explain_schedule`, whose
interpreter already recognizes `explain_schedule`, and whose current
clarification state is true.

Live surface profiling refines that 96-record shorthand into two different
semantic sets:

| Surface-derived family | Records | Selection hash | Required disposition |
|---|---:|---|---|
| resolved practitioner evidence (`exact` or `corrected`) | 84 | `b69abbcbc6febe29` | repair |
| genuinely ambiguous practitioner evidence | 12 | `34c95db64c716f56` | preserve clarification |

The 84-record target contains 72 scenario-declared `exact` and 12
scenario-declared `corrected` practitioner cases. The interpreter's own
surface-derived practitioner state is the runtime input; scenario labels must
not be consulted. The 12 ambiguous cases use wording such as `some doctor` and
must not be optimized to match contradictory Silver no-clarification labels.

## Objective A — Resolved-practitioner explanation semantics

When `explain_schedule` has already been recognized and the reduced
practitioner semantics are `exact` or `corrected`, do not require patient
identity merely to answer the read-only practitioner schedule question. The
observation must remain `intended`, non-clarifying, read-only, and select only
the existing read-only explanation tool sequence.

This is an additive sufficient context rule. Preserve the established
patient-specific explanation behavior so LC4R5 does not redefine adjacent
explanation meanings.

## Objective B — Clarification and anti-overmatch boundaries

Continue to clarify recognized explanation requests when neither a resolved
practitioner nor the already-supported resolved patient context is present.
In particular:

- ambiguous practitioner wording such as `some doctor` remains ambiguous;
- a recognized explanation request with no practitioner or patient context
  remains clarifying;
- generic `calendar`, `schedule`, or `availability` wording must not acquire
  `explain_schedule` action recognition merely to improve the corpus; and
- unsafe, negated, correction, session, tool, authority, and lossless
  normalization boundaries remain unchanged.

Do not broaden `_EXPLAIN_PATTERNS` in this sprint. LC4R5 changes only the
action-relevant clarification rule after action and entity extraction.

## Objective C — Report and authored regressions

Add a deterministic LC4R5 report/check that recomputes the 84-record repair
selection and 12-record preservation selection from development-only observed
behavior. It must record both hashes, the full semantic baseline, safety, and
repeat variance. It must fail closed if selection, corpus, or expected
preservation counts drift.

Focused authored regressions must prove:

- `Can you explain Dr Shera's schedule tomorrow?` is intended, read-only,
  non-clarifying, and uses `find_slots` without `search_patients`;
- a practitioner correction resolves to `corrected` and remains
  non-clarifying;
- `some doctor's schedule` remains ambiguous and clarifying;
- a recognized explanation with omitted practitioner and patient remains
  clarifying;
- existing patient-specific explanation behavior is unchanged;
- generic calendar/availability wording is not promoted into an action;
- unsafe and negated explanation wording retains its current safety posture;
- exact `tomorrow at 3pm` and lossless normalized turns are unchanged; and
- mutating expected scenario fields cannot influence extraction.

## Owned implementation surface

The worker may edit:

- `app/services/bernie/semantic_extraction.py`;
- focused LC4R5 and semantic extraction tests under `tests/`;
- one LC4R5 report/check script under `scripts/`;
- one deterministic JSON report and concise implementation note under `docs/`;
  and
- one completion artifact under `orchestration/agent_inbox/codex/`.

The worker must not edit `AGENTS.md`, generated scale fixtures or generators,
scenario schema, replay/audit policy, action grammar or route contracts,
providers, routes/API/OpenAPI/GraphQL, database/migrations, UI, T3 gates,
deployment, or protected-evidence surfaces.

## Acceptance

The pre-LC4R5 full-development semantic baseline is:

- intended action `880/1152`;
- action semantics `730/1152`;
- temporal relation `628/1152`;
- normalized values `101/1152`;
- entity semantics `300/1152`;
- clarification `698/1152`; and
- safety `1152/1152`.

Acceptance requires:

- the resolved-practitioner target is exactly `84/84`, selection hash
  `b69abbcbc6febe29`;
- all 12 ambiguous-practitioner preservation cases remain clarifying, selection
  hash `34c95db64c716f56`;
- full action-semantics passes are exactly `814/1152` and clarification passes
  exactly `782/1152` unless Sol independently demonstrates a bounded,
  source-supported difference;
- intended action remains `880/1152`, temporal relation `628/1152`, normalized
  values `101/1152`, and entity semantics `300/1152`;
- safety is `1152/1152` and measured per-scenario repeat variance is zero;
- patient-specific explanation behavior, generic anti-overmatch, fixture
  integrity, and oracle independence remain intact;
- focused tests, proportional LC1-LC4 and T1/T2/T3.1-T3.4 checks, blocked
  shadow gate, report `--check`, and `git diff --check` pass;
- Gemini returns `DECISION: pass` on the exact candidate head; and
- no protected-evidence, provider, T3.5, route/API, DB, UI, deployment, or
  write-authority boundary opens.

Sol will independently verify, own any recovery amendment, integrate, commit,
and push. Pause only at a documented user decision boundary.

Sprint engine state: continuing.
