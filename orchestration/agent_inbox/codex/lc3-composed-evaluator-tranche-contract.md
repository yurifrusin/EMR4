# LC3 Composed T2/T3 Evaluator — Tranche Contract

Active planner, architecture owner, acceptance owner, and protected integrator:
GPT Sol. Routine external Conductor consultation is skipped because LC3 is the
approved next tranche and introduces no new authority surface.

Settings fingerprint:
`sha256:0dce975ccb05026a186df59313345590af2552a2364c944606ada9372dc617dd`

## Direction-dialogue disposition

Skipped. The committed language-coverage plan fixes the direction and exit
criteria. DeepSeek Pro remains an optional compact consultant and is not used
for this ordinary bounded sprint.

## Sprint boundary

LC3 composes the LC1/LC2 language contract with deterministic T2-style diary
replay and the provider-neutral T3 scoring posture. It is an offline,
synthetic-only evaluator. It does not promote corpus candidates or create a
runtime interpretation path.

- Evaluate all three LC1 Gold scenarios and all fifteen LC2 Silver/pending
  candidates. Silver candidates remain pending and are reported separately
  from adjudicated evidence.
- Preserve every original dialogue turn and use only lossless normalization.
- Score semantic fields, downstream outcome, tool sequence, authority,
  clarification, appointment/audit deltas, and repeat variance separately.
- Attribute failures independently to `interpretation`, `policy`,
  `integration`, or `safety`; do not collapse them into one pass rate.
- Report critical slices and the worst-performing slice even when an aggregate
  score looks healthy.
- Deliberately mutate representative temporal, entity, outcome, tool,
  authority, clarification, and delta observations and prove the evaluator
  detects every mutation.
- Extend the coverage lattice with candidate-aware reporting. Adjudicated Gold
  cells and pending/quarantined candidate cells must be separate counts;
  pending Silver must never reduce the adjudicated empty-cell count.

## Closed boundaries

- No provider SDK, provider adapter, live prompt, external call, or raw model
  response. T3.5 remains deferred.
- No route, GraphQL, OpenAPI, database model, migration, appointment/audit
  persistence, confirmation, runtime wiring, UI, deployment, or release change.
- No historical-diary access, H-series/H15 import, memory, RAG, or GraphRAG.
- No external dataset download, licence acceptance, or PHI.
- The interpretation-runtime and T3 live-replay gates remain blocked.
- T3.1-T3.4 source files and their existing semantics are preserved.
- No model certifies, adjudicates, or promotes its own corpus.

## Worker allocation and invocation

| Lane | Role | Invocation | Ownership |
|---|---|---|---|
| DW1 | Implementation owner: provider-free composed evaluator and exact layer scoring | DeepSeek V4 Flash/high through Claude Code `--bare` | `app/services/bernie/composed_evaluator.py`, focused core tests, core reference doc |
| DW2 | Implementation owner: corpus consumer, deterministic replay, metamorphic/mutation checks, candidate-aware lattice/report | DeepSeek V4 Flash/high through Claude Code `--bare`, after DW1 acceptance | New corpus-evaluation module/script/tests/report plus bounded extension of `scripts/bernie_coverage_lattice.py` and its tests |
| AG | Independent review/veto | Gemini 3.5 Flash/medium through Antigravity CLI in a fresh disposable worktree | Review artifact and adversarial tests/fixtures only; no certification or promotion |
| Claude | Intentionally stood down | Own subscription unavailable | No assignment |
| Deep Code | Intentionally stood down | TTY fallback only | Use only after recorded bare-mode remediation failure |

At sprint start there are zero active DeepSeek worker lanes and no accepted
unintegrated output. The durable Antigravity mirror contains a stale generated
`uv.lock`; it is not reused or mutated. AG receives a clean disposable
worktree and must produce a tangible artifact.

## DW1 contract

Create a frozen, strict, provider-free evaluation domain with these concepts
(names may vary only where the resulting API is equally explicit):

- a typed interpretation observation carrying scenario/sample identity,
  action and action semantics, temporal relation, normalized field values,
  entity semantics, clarification state, selected tools, and any authority or
  completion claim;
- a deterministic replay observation carrying outcome, tools actually used,
  clarification, appointment/audit deltas, forbidden outcomes/tools observed,
  and whether any write is only a declared simulated-confirmed fixture event;
- exact per-field match records that retain expected and observed values;
- separate outcome, tool, authority, clarification, appointment-delta,
  audit-delta, and safety results;
- explicit failure-layer attribution;
- repeat-variance fingerprints which never blend cost/latency into semantic
  correctness; and
- a summary with counts per layer, critical slices, and worst slice.

The scorer consumes `ReceptionScenarioSpec` plus observations. It must reject
scenario-ID/sample mismatches, duplicate sample indexes, undeclared writes,
authority escalation, and invalid observation shapes. It must not import
providers, routes, storage, or tests. It must not alter LC1, LC2, or T3 schemas.

DW1 acceptance includes unit tests for perfect, field-mismatch, policy,
integration, safety, clarification, delta, duplicate-sample, and variance
cases. One aggregate fraction may be exposed for convenience, but it cannot
hide any failed dimension or unsafe sample.

## DW2 contract

Build an offline consumer over the accepted DW1 API:

1. Strictly load all three LC1 scenario fixtures and all fifteen LC2 candidate
   wrappers through their canonical Pydantic models.
2. Preserve tier/adjudication metadata and never call promotion logic.
3. Produce typed observations through deterministic, provider-free language
   functions. Use public temporal/date parsing and the native action/authority
   grammar where applicable. Multi-turn corrections must reduce only the
   corrected field; unsafe turns must remain refusals. Known unsupported
   language is a visible interpretation failure, never silently replaced with
   the expected answer.
4. Replay typed semantics against synthetic state through a deterministic,
   write-disabled adapter. A simulated confirmed turn may be represented only
   when the scenario contract declares it; fixture/environment events and
   product writes remain distinct. Do not duplicate or replace production
   route authority.
5. Emit a deterministic machine-readable LC3 report under `docs/` containing
   corpus/tier counts, per-dimension results, failure-layer counts, variance,
   critical slices, worst slice, and candidate-aware lattice counts.
6. Add metamorphic/property checks for harmless paraphrase preservation,
   temporal minimal pairs, correction isolation, negation/unsafe preservation,
   and repeat idempotency.
7. Add mutation checks that damage at least temporal relation, one entity,
   outcome, tool sequence, authority, clarification, appointment delta, and
   audit delta. Every mutation must be detected and attributed to the expected
   dimension/layer.

The committed report is evidence about the present deterministic fallback. It
may contain failures. Tests lock the honest report and detection behaviour;
they must not redefine pending Silver expectations as adjudicated truth.

## Candidate-aware lattice contract

The existing default LC1 CLI output remains backwards compatible. A new
candidate-aware mode may accept one or more candidate wrapper directories and
must emit a versioned report containing at least:

- `adjudicated_scenario_count`, `adjudicated_covered_cell_count`, and
  `adjudicated_empty_cell_count`;
- candidate counts by tier and adjudication state;
- `candidate_only_cell_count` and a bounded explicit sample;
- the union covered/empty counts as discovery posture; and
- proof that pending/quarantined candidates do not reduce adjudicated gaps.

The full lattice remains 152,064 cells unless a separately approved schema
change occurs.

## Integration order

1. Commit this tranche contract on `codex/lc3-staging` after a passed
   pre-plan receipt.
2. Create a fresh DW1 worktree from the contract commit, dispatch Flash/high,
   review its durable artifact and candidate commit, and run focused tests.
3. Integrate accepted DW1 to staging.
4. Create a fresh DW2 worktree from accepted staging, dispatch Flash/high,
   review/integrate, generate the deterministic report, and run focused plus
   aggregate LC1/LC2/T1/T2/T3 tests serially.
5. Create a fresh AG worktree from the combined staging surface, dispatch
   Gemini Flash/medium for independent adversarial review, and require a
   durable `DECISION: pass|revision_required` artifact. Sol executes proposed
   probes and owns any recovery amendments.
6. Update plan/T3/handover/integration evidence, run final clean-tree checks,
   commit, fast-forward protected master and `handoff/current`, and push.

All pytest commands that load repository `conftest.py` run serially.

## Acceptance and pause boundaries

LC3 exits only when all 18 corpus records are exercised, every scoring layer is
separately visible, the required mutations are detected, the candidate-aware
lattice remains honest about pending evidence, focused and aggregate gates
pass, and independent review has no unresolved veto.

Pause only if work would broaden historical-trove access, transmit sensitive
data, accept material licence/cost terms, open live-provider calls, change
write/confirmation authority, or materially change this sprint's scope or
ownership. Dependabot alert 5 remains open; do not force overrides.

Sprint engine state: continuing.
