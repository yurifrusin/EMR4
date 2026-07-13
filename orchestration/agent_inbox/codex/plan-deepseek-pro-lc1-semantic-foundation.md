# DeepSeek 4 Pro Conductor Plan: LC1 Semantic Foundation and Known Regression

Role: Conductor
Model: `deepseek-v4-pro` / high
Leverage reason: LC1 freezes the first canonical language-to-diary semantic
contract and temporal ontology; incorrect allocation would contaminate later
corpus and evaluator work.
Settings fingerprint:
`sha256:20e82ee5251321c4987158176b29f8c780ba5debc2c515592c320e869be418d5`

## Direction-Dialogue Disposition

Skipped. The approved product direction is LC1 per
`docs/bernie-language-coverage-implementation-plan.md`; no architecture dispute,
policy change, or material sprint-size disagreement exists.

## Lane Cleanliness and Availability

| Lane | Status | Worktree | Action |
|---|---|---|---|
| Claude CLI | Unavailable | `claude/current` — unintegrated branch residue, not aligned to master | Stand down |
| Antigravity CLI | Unavailable | Dirty with untracked `uv.lock` | Stand down |
| Deep Code | Reachable, zero active managed slots | Disposable worktrees from current master | Allocate three `deepseek-v4-flash`/high lanes |

DeepSeek Flash lane count: 0 active, 0 complete/idle, 0 to close. Three fresh
lanes spawned for this sprint only.

## Boundary Classification

**LC1 is a test/harness/contract sprint with zero surface-mutation authority.**

- No provider calls, no live prompts, no provider adapter work.
- No route wiring, no HTTP interception changes, no GraphQL mutations.
- No database writes, no appointment/audit mutation.
- No diary write authority, no confirmation authority.
- No historical-trove access, no H15/H-series runtime imports.
- No memory/RAG/GraphRAG access.
- No deployment/release/external-client changes.
- Existing T3.1-T3.4 code and tests are preserved (not modified, not removed).
- T3.5 DeepSeek/Gemini provider adapters are out of scope.
- The existing interpretation-harness runtime gate remains `blocked`.

## Scope

1. Reproduce `tomorrow at 3pm` failure through the non-intercepted fake-provider
   interpretation path and add it as permanent regression evidence.

2. Add `_AT_TIME_RE` to `extract_natural_time_constraints()` in
   `app/services/diary/temporal.py` so `at 3pm`, `at 3 pm`, `at 3.00pm`,
   `at 15:00` set both `earliest_time` and `latest_time` to the same value
   (exact point-time semantics).

3. Define a `TemporalRelation` enum with: `exact`, `not_before`, `not_after`,
   `interval`, `approximate`, `unspecified`. Map existing operators: `at` →
   `exact`, `after` → `not_before`, `before` → `not_after`, `between ... and` →
   `interval`. `approximate` and `unspecified` are reserved for future
   `around`, `roughly`, and bare-time forms.

4. Cover time-form variants: `3pm`, `3 pm`, `3.00pm`, `15:00`.

5. Introduce `ReceptionScenarioSpec` as a versioned canonical scenario contract
   with: dialogue turns, deterministic clock, initial diary state, intended/
   ambiguous/prohibited action, entity/duration semantics, temporal relation,
   normalized values plus source spans, expected clarification, expected
   deterministic outcome/tools/deltas, forbidden outcomes, provenance/tier/
   adjudication/family.

6. Implement lossless normalization that preserves the original utterance and
   produces a normalized matching view via Unicode normalization, whitespace
   normalization, case folding, punctuation variants, number/time forms. No
   stop-word removal, stemming, or lemmatization in the authoritative path.

7. Adapt a small independent set of existing T1/T2 authored golden scenarios
   to the new contract. The adapted seed must include at minimum:
   - `booking_create_then_exact_duplicate` (T1.1)
   - `booking_overlap_not_exact_duplicate` (T1.2)
   - One interpret-clarify scenario with temporal bounds

8. Emit the first machine-readable coverage lattice and gap report showing
   empty cells across dimensions: diary action, diary state, entity state,
   temporal form, dialogue form, language form. Report empty cells explicitly
   rather than hiding them in aggregate pass rates.

9. Prove the known exact-time duplicate reaches the deterministic duplicate
   outcome (`existing_booking_found`, zero second appointment/audit write).

## Out of Scope

- T3.5 DeepSeek/Gemini provider adapters.
- Live replay, live-provider calls, static provider-adapter work.
- Runtime provider wiring, provider prompts.
- Broad historical-trove access, H15/H-series runtime imports.
- Memory/RAG/GraphRAG.
- GraphQL mutations, external clients.
- Deployment/release changes.
- Any change to proposal/confirmation/write authority.
- Modifications to T3.1-T3.4 evaluation infrastructure.
- Changes to `master`, `handoff/current`, or protected integration branches.

## Assignments

| Lane | Worker | Role | Model | Branch |
|---|---|---|---|---|
| DW1 | DeepSeek Flash | Implementation owner — temporal fix + regression | `deepseek-v4-flash`/high | `codex/lc1-dw1-temporal-foundation` |
| DW2 | DeepSeek Flash | Implementation owner — scenario contract + normalization + seed adaptation | `deepseek-v4-flash`/high | `codex/lc1-dw2-scenario-contract` |
| DW3 | DeepSeek Flash | Independent review/veto — coverage report + adversarial pass over DW1/DW2 | `deepseek-v4-flash`/high | `codex/lc1-dw3-coverage-review` |
| Sol | DeepSeek 4 Pro | Architecture, acceptance, integration | Conductor only | (Conductor — this plan) |

DW1 and DW2 may proceed in parallel (disjoint file ownership). DW3 must wait
for both DW1 and DW2 to submit their artifacts.

**Corpus authorship rule:** No model certifies its own corpus. DW2 adapts
existing Sol-authored T1/T2 golden scenarios mechanically; Sol validates the
adapted semantics. DW3 (also DeepSeek Flash) provides independent review, not
certification — its review is veto/adversarial evidence, not corpus authority.

## File Ownership

### DW1 — Temporal Foundation
- **Owns:** `app/services/diary/temporal.py` (add `_AT_TIME_RE`, `TemporalRelation` enum,
  update `extract_natural_time_constraints`), `tests/test_bernie_temporal_policy.py`
  (add `at` operator tests, time-form variant tests, temporal-relation tests),
  `app/services/bernie/temporal.py` (re-export new symbols if needed)
- **Must not touch:** `app/services/bernie_booking_interpreter.py` (DW2 adapts),
  scenario fixtures, T3 eval code, routes, schemas, migrations

### DW2 — Scenario Contract + Normalization + Seed Adaptation
- **Owns:** New `app/services/bernie/scenario_spec.py` (scenario contract class),
  New `app/services/bernie/normalizer.py` or extension to existing
  `app/services/bernie/normalizer.py` (lossless normalization),
  New `tests/fixtures/bernie_scenario_spec/` (adapted T1/T2 seed cases),
  New `tests/test_bernie_scenario_spec.py` (contract validation tests),
  `tests/fixtures/bernie_scenario_spec/README.md` (provenance/tier/adjudication)
- **Must not touch:** `app/services/diary/temporal.py`, T3 eval code, routes,
  schemas, migrations, existing scenario replay fixtures

### DW3 — Coverage Report + Independent Review
- **Owns:** New `scripts/bernie_coverage_lattice.py` (coverage report generator),
  New `tests/test_bernie_coverage_lattice.py` (report validation),
  New `orchestration/agent_inbox/codex/review-deepseek-lc1-dw3-coverage-review.md`
  (review artifact)
- **Must not touch:** Any `app/` code, scenario fixtures, temporal module,
  routes, schemas, migrations

## Ordered Dependencies

```
DW1 (temporal fix) ──┐
                      ├──> DW3 (coverage report + review)
DW2 (contract+seed) ──┘
                        │
                        v
                    Sol acceptance
```

DW1 and DW2 are parallel. DW3 must wait for both artifact submissions. Sol
acceptance gates integration.

## Deterministic Acceptance Checks

### Pre-dispatch (Sol verifies before dispatching any worker)

```powershell
# 1. Reproduce the known failure
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py ^
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3pm duration 15" ^
  --provider fake ^
  --reference-date 2026-07-14 ^
  --json

# Assert: earliest_time is null, latest_time is null
# (Failure confirmed 2026-07-14: earliest_time=null, latest_time=null, result=interpreted, safe=true)
```

### DW1 acceptance

```powershell
# 2. `at` operator sets both earliest and latest (exact point time)
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py ^
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3pm duration 15" ^
  --provider fake ^
  --reference-date 2026-07-14 ^
  --expect-earliest-time 15:00 ^
  --expect-latest-time 15:00 ^
  --expect-result interpreted

# 3. Time-form variants
# at 3 pm → 15:00
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py ^
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3 pm duration 15" ^
  --provider fake --reference-date 2026-07-14 ^
  --expect-earliest-time 15:00 --expect-latest-time 15:00

# at 3.00pm → 15:00
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py ^
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3.00pm duration 15" ^
  --provider fake --reference-date 2026-07-14 ^
  --expect-earliest-time 15:00 --expect-latest-time 15:00

# at 15:00 → 15:00
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py ^
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 15:00 duration 15" ^
  --provider fake --reference-date 2026-07-14 ^
  --expect-earliest-time 15:00 --expect-latest-time 15:00

# 4. Existing operators still work (after/before/between)
.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py ^
  --instruction "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45" ^
  --provider fake --reference-date 2026-07-14 ^
  --expect-earliest-time 14:00 --expect-latest-time 15:45

# 5. All temporal tests pass
.venv\Scripts\python.exe -m pytest tests\test_bernie_temporal_policy.py -q

# 6. All existing smoke tests pass
.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py -q
```

### DW2 acceptance

```powershell
# 7. Scenario spec contract validates
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q

# 8. Adapted T1/T2 seeds pass contract validation
# (Contract shape check — not semantic adjudication, which Sol owns)
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q -k "seed"

# 9. Normalizer preserves original utterance and produces derived view
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q -k "normalize"
```

### DW3 acceptance

```powershell
# 10. Coverage lattice emits valid JSON with empty cells
.venv\Scripts\python.exe scripts\bernie_coverage_lattice.py

# 11. Coverage report tests pass
.venv\Scripts\python.exe -m pytest tests\test_bernie_coverage_lattice.py -q

# 12. Independent review artifact is committable
# (Sol reads review artifact, verifies findings are bounded and substantiated)
```

### End-to-end duplicate regression (Sol after DW1+2+3 integration)

```powershell
# 13. Exact-time duplicate reaches deterministic duplicate outcome
.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q -k "exact_duplicate"

# 14. Full scenario lab still passes
.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\ tests\test_bernie_scenario_integrity.py -q

# 15. T3.1-T3.4 infrastructure unchanged
.venv\Scripts\python.exe -m pytest tests\test_bernie_shadow_eval.py tests\test_bernie_shadow_corpus.py tests\test_bernie_shadow_runner.py -q

# 16. Readiness gate still blocked
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
# Expected: runtime_or_provider_wiring_ready=false, raw_trove_access_ready=false, runtime_gate_decision=blocked
```

## API-Spine Posture

LC1 adds no routes, no GraphQL, no commands, no events. It conforms to the
existing spine:

- REST/command plane: unchanged (no new endpoints, no mutation authority).
- GraphQL read plane: unchanged (no resolvers, no SDL changes).
- YAML manifests: the scenario contract is a test/harness artifact, not a
  runtime manifest. If a future manifest use emerges, it must pass the
  existing `proposal_surface_guard` gate with blocked readiness values.
- Evidence labels: all LC1 evidence is `fake-provider` or `route-intercepted`.
  No `live-backend` or `live-provider` evidence is produced.

## Evidence Labels

| Check | Label |
|---|---|
| Smoke script with `--provider fake` | `fake-provider` |
| `extract_natural_time_constraints` unit tests | `fake-provider` |
| Scenario spec contract validation | `fake-provider` (synthetic authored corpus) |
| Coverage lattice report | `fake-provider` (synthetic authored corpus) |
| Adapted T1/T2 seed | `fake-provider` (synthetic authored corpus) |
| DW3 independent review | `fake-provider` (review artifact, no live calls) |

No `live-backend` or `live-provider` evidence is generated or required for LC1.

## Independent Review Needs

- DW3 provides the independent review lane over both DW1 and DW2 artifacts.
- DW3 must run all deterministic checks listed under DW1 and DW2 acceptance and
  report pass/fail with specific failure evidence.
- DW3 must verify that:
  - `at 3pm` no longer produces `earliest_time=null, latest_time=null`
  - The temporal-relation enum distinguishes exact from not_before/not_after/interval
  - Existing `after`/`before`/`between` operators are unchanged
  - The scenario contract has all required fields from the LC plan
  - The adapted seed cases reference known T1/T2 scenario IDs
  - The coverage report explicitly shows empty cells
- DW3 review is veto/adversarial evidence only. Sol owns final corpus
  authority and semantic adjudication.

## Regular Sol Checkpoint

Sol commits this plan and worker packets to the Conductor branch
`deepcode/lc1-conductor` before dispatching any worker. Sol does **not** push
to `master` or `handoff/current`. Worker dispatch uses separate disposable
worktrees (see worker packets).

After all lanes submit and Sol reviews:

1. Sol integrates accepted artifacts into a single integration commit on
   `deepcode/lc1-conductor` (Conductor branch only — not master).
2. Sol records integration outcome.
3. Sol update AGENTS.md with LC1 closeout notes.
4. **Push to master and advance handoff/current is deferred to the protected
   orchestrator (Codex Ariadne). This Conductor does not have integration
   authority.**

## Sprint-Engine State

**Sprint engine continuing.** LC1 is a bounded test/harness/contract sprint
with no provider, route, DB, write-authority, or external-client surface.
Claude and Antigravity are unavailable; three DeepSeek Flash lanes provide
implementation + independent review coverage. Sol/high owns architecture and
acceptance. No user decision is required unless work would broaden
historical-trove access, send sensitive data externally, accept material
licence/cost terms, open live-provider calls, or change write authority —
none of which are in scope.

## Worker Packet Files

- `orchestration/agent_inbox/deepcode/deepcode-flash-lc1-dw1-temporal-foundation.md`
- `orchestration/agent_inbox/deepcode/deepcode-flash-lc1-dw2-scenario-contract.md`
- `orchestration/agent_inbox/deepcode/deepcode-flash-lc1-dw3-coverage-review.md`

STATUS: complete
