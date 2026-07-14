# LC4R3 Aligned Action-Surface Closure — Sprint Contract

Date: 2026-07-14

Active Conductor, planner, architecture/acceptance owner, recovery owner, and
protected integrator: GPT Sol. Planning mode is `sol_direct_routine`.
DeepSeek V4 Flash/high through Claude Code `--bare` owns one bounded
implementation/test lane. Gemini 3.5 Flash through Antigravity owns the
independent veto review. DeepSeek Pro is not a Conductor or worker for this
sprint.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Direction-dialogue disposition

Skipped. Sol's development-only audit isolates a narrow deterministic action
surface without an architecture or product-policy dispute. External models do
not plan, allocate, accept, or integrate this sprint.

## Protected evidence boundary

Use only ordinary LC1-LC4 development fixtures and new authored synthetic
regressions. Do not open, enumerate, import, load, regenerate, evaluate,
hash-check, infer from, or tune against protected holdout fixtures, support
modules, seals, receipts, or reports. Do not inspect historical diary material
or transmit any patient/practice data. No provider inference, routes, API,
database, UI, deployment, memory, RAG, GraphRAG, T3.5 adapter, or write
authority is permitted.

The current 1,152-record development partition remains Silver/pending
discovery evidence. The worker must not edit its fixtures or use expected
scenario fields inside interpretation.

## Evidence and bounded target

LC4R2 leaves 590 one-repeat `aligned_failure` records. Within that subset, 180
records fail `intended_action`. A surface-family audit identifies 154 explicit,
bounded misses that can be repaired without collapsing adjacent product
actions:

| Explicit surface family | Expected action | Records |
|---|---|---:|
| anchored `New booking:` request | `create` | 16 |
| `call off ... booking/appointment` | `cancel` | 13 |
| practitioner availability, appointments, day-view, free-slot, or available-time question | `explain_schedule` | 80 |
| anchored `Arrived:`, anchored `Status: ... ARRIVED`, or `confirm arrival ... booking` | `status_change` | 45 |

Two adjacent 13-record families are explicitly outside the repair target:

- `check in ...` remains the distinct planned `DiaryActionVerb.check_in`; it
  must not be silently recast as executable `status_change` authority; and
- bare narrative `a patient just arrived for an appointment` remains
  insufficient to infer a status command and must continue to clarify.

## Objective A — Bounded action-surface recognition

Extend the pure, oracle-free action detector so the four explicit families
above resolve to their stated existing LC4 action. Keep patterns narrow and
context-bearing:

- require booking/appointment context for `New booking:` and `call off`;
- require schedule/availability context for explanation phrases;
- require explicit command/label form for arrival status phrases; and
- preserve current cancel/status/move/resize/explain/create precedence,
  unsafe-demand handling, action negation, and lossless normalization.

Action recognition must still derive solely from utterance text. It must not
read scenario IDs, expected actions, provenance, adjudication, expected tools,
outcomes, values, clarification, deltas, or diary state.

## Objective B — Preserve planned-action and ambiguity boundaries

Add authored anti-overmatch regressions proving:

- `check in Margaret Thompson` is not classified as `status_change`;
- `a patient just arrived for an appointment` does not become a mutation
  command;
- non-diary uses of `call off`, `new booking`, `availability`, `appointments`,
  `arrived`, and `status` do not acquire a diary action merely from a keyword;
- negated/reversed explicit actions select no mutation tool; and
- unsafe positive completion/bypass wording remains refused.

Do not promote `check_in`, `waiting_area_move`, or `link_patient`; do not alter
their grammar or route contracts.

## Objective C — Development-only evidence report

Add a deterministic LC4R3 report/check that records:

- the frozen pre-LC4R3 semantic-field baseline;
- current one-repeat semantic-field counts;
- the four target-family counts and pass counts;
- the two explicitly deferred adjacent-family counts and observed outcomes;
- full development safety and repeat variance;
- development corpus/report hashes; and
- explicit Silver/pending and no-protected-evidence statements.

The report must fail if the development corpus changes, if a target family is
silently redefined, or if a deferred family becomes `status_change`.

## Owned implementation surface

The worker may edit:

- `app/services/bernie/semantic_extraction.py`;
- focused semantic extraction / LC4R3 tests under `tests/`;
- one LC4R3 development report script under `scripts/`;
- one deterministic LC4R3 report and concise implementation note under
  `docs/`; and
- one completion artifact under `orchestration/agent_inbox/codex/`.

The worker must not edit AGENTS.md, scale generators or fixtures, scenario
schema, replay/audit policy, action grammar or route contracts, providers,
routes/API/OpenAPI/GraphQL, database/migrations, UI, T3 gates, deployment, or
protected-evidence surfaces.

## Required tests

Tests must prove every accepted phrase family and representative punctuation /
case variants, the deferred-family boundaries, anti-overmatch cases, action
priority, negation/refusal behavior, exact `tomorrow at 3pm`, deterministic
report regeneration, and oracle independence under mutated expected fields.

## Acceptance

Sol will independently rerun the focused tests, the LC1 exact-route regression,
LC3/LC4 composed gates proportionate to the touched surface, the LC4R2 report
check, T1/T2/T3.1-T3.4 preservation checks, the blocked shadow gate, and
`git diff --check`. Gemini will review the exact candidate head before Sol
accepts it.

Acceptance requires:

- target-family intended-action recognition `154/154`;
- full development intended-action passes at least `874/1152` (baseline 720);
- the remaining semantic-field baselines do not regress: action semantics
  `>=674`, temporal relation `>=628`, normalized values `>=101`, entity
  semantics `>=255`, clarification `>=642`;
- safety `1152/1152` and measured repeat variance zero;
- both deferred families remain unpromoted and non-mutating;
- no fixture/expected-answer echo or regex overmatch exposed by authored tests;
- Gemini returns `DECISION: pass`; and
- no protected-evidence, provider, route/API, DB, UI, T3.5, deployment, or
  write-authority boundary opens.

Pause only for an explicit user stop or a documented protected-evidence reuse,
historical-data expansion, external sensitive-data/provider call, material
licence/cost, API/route, database, confirmation/write, deployment, or release
boundary.

Sprint engine state: continuing.
