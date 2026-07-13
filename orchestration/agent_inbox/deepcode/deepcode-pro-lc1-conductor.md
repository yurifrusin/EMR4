# DeepSeek 4 Pro Conductor: LC1 Semantic Foundation and Known Regression

Role: Conductor
Resource: `deepseek-pro-routine-coordinator`
Model: `deepseek-v4-pro`
Reasoning: high
Leverage reason: LC1 freezes the first canonical language-to-diary semantic
contract and temporal ontology; incorrect allocation would contaminate later
corpus and evaluator work.
Settings fingerprint:
`sha256:20e82ee5251321c4987158176b29f8c780ba5debc2c515592c320e869be418d5`
Completion plan:
`orchestration/agent_inbox/codex/plan-deepseek-pro-lc1-semantic-foundation.md`

Act as Ariadne Conductor under the committed operating-model and allocation
settings. You have sprint-definition and worker-allocation authority only. You
must not integrate, commit, push, alter protected `master`, open providers, or
grant diary write authority.

Read, at minimum:

- `AGENTS.md`
- `docs/bernie-language-coverage-implementation-plan.md`
- `docs/bernie-t1-stateful-scenario-laboratory.md`
- `docs/bernie-t2-deterministic-behaviour-matrix.md`
- `docs/bernie-t3-shadow-evaluation.md`
- `orchestration/api_spine_adr.md`
- `orchestration/bernie_release_gates.md`
- the relevant interpreter, temporal, scenario-replay, and T3 evaluation code

The approved product direction is LC1, so direction dialogue is obvious and
may be recorded as skipped. Define exactly one bounded LC1 sprint and allocate
its work. Current diagnostic evidence from the protected orchestrator is:

```text
Instruction: synthetic booking request for tomorrow at 3pm, duration 15
Path: scripts/smoke_bernie_interpreter.py, provider=fake, no HTTP interception,
      no DB write, no provider call
Expected: earliest_time=15:00
Actual: earliest_time=None, latest_time=None; result=interpreted and safe=true
```

The public route and deterministic diary duplicate outcome must become the
authoritative regression evidence. LC1 must:

1. reproduce the real `tomorrow at 3pm` failure through the non-intercepted
   interpretation route/path;
2. introduce a versioned canonical `ReceptionScenarioSpec` (or equivalent)
   that preserves original dialogue, deterministic clock/state, intended or
   ambiguous/prohibited action, entity/duration semantics, expected
   clarification/tool/outcome/deltas/forbidden outcomes, source spans,
   provenance/tier/adjudication/family;
3. define explicit temporal relations `exact`, `not_before`, `not_after`,
   `interval`, `approximate`, and `unspecified` so point time cannot collapse
   into an open lower bound;
4. implement lossless normalization that preserves the original utterance and
   traceable spans while deriving Unicode/whitespace/case/punctuation/time-form
   matching views; authoritative normalization must not use stop-word removal,
   stemming, or lemmatization;
5. cover at least `3pm`, `3 pm`, `3.00pm`, `15:00` and exact/open/approximate
   operators;
6. adapt a small independently authored T1/T2 seed set to the contract;
7. emit and validate the first machine-readable coverage lattice/gap report,
   showing empty cells rather than only aggregate counts; and
8. prove the known exact-time duplicate reaches the deterministic duplicate
   outcome with zero second appointment/audit write.

Preserve T3.1-T3.4 and their tests. T3.5 DeepSeek/Gemini provider adapters,
live replay, live-provider calls, static provider-adapter work, runtime provider
wiring, and provider prompts are out of scope. Also keep broad historical-trove
access, H15/H-series runtime imports, memory/RAG/GraphRAG, GraphQL mutations,
external clients, deployment/release changes, and any change to proposal/
confirmation/write authority closed.

Available lanes for this sprint:

- Claude CLI is reachable but `claude/current` has unintegrated branch residue
  and is not aligned to current master: unavailable for dispatch.
- Antigravity CLI is reachable but its durable mirror is dirty with an
  untracked `uv.lock`: unavailable for dispatch.
- Deep Code is reachable with zero active managed slots. Allocate no more than
  three `deepseek-v4-flash`/high lanes, only where each has a distinct artifact
  or veto surface. Worker sessions must use clean disposable worktrees based on
  current master. The same model must not generate and certify its own corpus;
  authored seed semantics remain Sol-owned acceptance evidence.

The plan must include: boundary classification, scope/out-of-scope, assignments,
file ownership, ordered dependencies, deterministic acceptance checks,
API-spine posture, evidence labels, independent review needs, settings
fingerprint, direction-dialogue disposition, lane-cleanliness assumptions,
regular Sol commit/push checkpoint, and sprint-engine state. Create concrete
DeepCode worker packet files if allocating lanes. Do not add monetary or
wall-clock limits. End the completion plan with exactly:

```text
STATUS: complete
```
