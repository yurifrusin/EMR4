# DeepSeek 4 Pro Conductor Plan V2: LC1 Semantic Foundation and Known Regression

Role: Conductor
Model: `deepseek-v4-pro` / high
Leverage reason: LC1 freezes the first canonical language-to-diary semantic
contract and temporal ontology; incorrect allocation would contaminate later
corpus and evaluator work.
Settings fingerprint:
`sha256:20e82ee5251321c4987158176b29f8c780ba5debc2c515592c320e869be418d5`

**V2 revision reason:** Protected orchestrator rejoinder under
`docs/ariadne-direction-collaboration.md` identified six blocking defects in V1.
This revision exercises final Conductor authority to correct each one.

## Defect Resolution Summary

| # | Defect | V2 Resolution |
|---|--------|--------------|
| 1 | `earliest==latest` → empty half-open search | `temporal_relation=exact` drives a consumer-side 5-minute widening; `earliest_time` stays 15:00, `latest_time` is set to 15:05 so the search window `[15:00, 15:05)` captures the exact-time slot |
| 2 | `TemporalRelation` not threaded end-to-end | Optional `temporal_relation: str` added to `SlotSearchCommandIn`, `SlotSearchProposalIn`, passed through the normalizer, consumed by the slot-search route and duplicate classifier |
| 3 | `approximate` reserved for future | Defined and tested now: `_ABOUT_TIME_RE` for `around 3pm`/`about 3pm`; ±30 min window; `approximate` never yields `existing_booking_found`; `unspecified` also representable and tested |
| 4 | Worker packets don't exist | All three worker packet files created with this plan |
| 5 | `normalizer.py` already exists | DW2 uses `app/services/bernie/scenario_spec.py` and `app/services/bernie/language_normalization.py` |
| 6 | Wrong T3 test file names | Uses correct committed files: `test_bernie_shadow_eval_contract.py`, `test_bernie_shadow_corpus.py`, `test_bernie_shadow_runner.py`, `test_bernie_shadow_live_gate.py` |

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

### 1. Reproduce and fix the `tomorrow at 3pm` regression

Reproduce the known failure through the non-intercepted fake-provider
interpretation path. The failure is: `at 3pm` produces `earliest_time=null,
latest_time=null` because no `_AT_TIME_RE` pattern exists.

Add `_AT_TIME_RE` to `app/services/diary/temporal.py` matching `at 3pm`,
`at 3 pm`, `at 3.00pm`, `at 15:00`, and `at 3:00pm` variants.

### 2. Define TemporalRelation and thread it end-to-end

Define a `TemporalRelationKind` (string Literal) with:

| Value | Operator pattern | Slot-search window semantics | Duplicate authority |
|---|---|---|---|
| `exact` | `at 3pm`, `at 15:00` | `[earliest, earliest + 5min)` — consumer widens `latest` by 5min | Yes — booking found in window is exact duplicate |
| `not_before` | `after 3pm` | `[earliest, end_of_day)` — existing `earliest`-only behaviour | No |
| `not_after` | `before 3pm` | `[start_of_day, latest)` — existing `latest`-only behaviour | No |
| `interval` | `between 2pm and 3:45` | `[earliest, latest)` — existing both-bounds behaviour | No |
| `approximate` | `around 3pm`, `about 3pm` | `[anchor - 30min, anchor + 30min)` | No — must never claim exact-duplicate |
| `unspecified` | bare `3pm`, no operator | `[earliest, earliest + 5min)` for search; no duplicate authority | No — conservative default |

The consumer-side widening for `exact` (5 minutes, the minimum slot unit)
happens in the slot-search route/service layer, not in the pure temporal parser.
The temporal parser returns the raw relation and raw equal bounds; the consumer
reads `temporal_relation` and adjusts the query window.

The `temporal_relation` field is added as `Optional[str]` to:

1. `SlotSearchCommandIn` — set by the interpreter from extracted relation
2. `SlotSearchProposalIn` — passed through by the normalizer
3. The slot-search route/service reads it to adjust the search window
4. The supervised duplicate classifier reads it to gate `existing_booking_found`

Legacy commands without `temporal_relation` use an inference policy:
`earliest==latest` → `exact`, only `earliest` → `not_before`, only `latest` →
`not_after`, both different → `interval`, none → `unspecified`. This policy is
documented but the field is the authoritative carrier.

### 3. Cover time-form variants

`3pm`, `3 pm`, `3.00pm`, `15:00`, `3:00pm`, `at 3pm`, `at 15:00`.

### 4. Introduce canonical scenario contract and lossless normalization

`ReceptionScenarioSpec` in `app/services/bernie/scenario_spec.py` (NOT
overwriting the existing `normalizer.py` slot-normalizer facade):

- Versioned contract with: dialogue turns, deterministic clock, initial diary
  state, intended/ambiguous/prohibited action, entity/duration semantics,
  temporal relation, normalized values plus source spans, expected
  clarification, expected deterministic outcome/tools/deltas, forbidden
  outcomes, provenance/tier/adjudication/family.

Lossless normalization in `app/services/bernie/language_normalization.py`:

- Unicode NFKC normalization, whitespace normalization, case folding,
  punctuation variants, number/time forms.
- Preserves original utterance; produces derived matching view.
- No stop-word removal, stemming, or lemmatization.

### 5. Adapt T1/T2 seed scenarios

Adapt a small independent set to the new contract:
- `booking_create_then_exact_duplicate` (T1.1)
- `booking_overlap_not_exact_duplicate` (T1.2)
- One interpret-clarify scenario with temporal bounds

### 6. Emit coverage lattice and gap report

Machine-readable coverage lattice showing empty cells across dimensions: diary
action, diary state, entity state, temporal form, dialogue form, language form.
Report empty cells explicitly.

### 7. Prove exact-time duplicate reaches deterministic outcome

`existing_booking_found`, zero second appointment/audit write.

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
- Modifying `app/services/bernie/normalizer.py` (the existing slot-normalizer
  facade) — DW2 must use distinct module names.

## Assignments

| Lane | Worker | Role | Model | Branch |
|---|---|---|---|---|
| DW1 | DeepSeek Flash | Implementation owner — complete temporal through-path + regression | `deepseek-v4-flash`/high | `codex/lc1-dw1-temporal-foundation` |
| DW2 | DeepSeek Flash | Implementation owner — scenario contract + normalization + seed + gap report | `deepseek-v4-flash`/high | `codex/lc1-dw2-scenario-contract` |
| DW3 | DeepSeek Flash | Independent review/veto — adversarial sweep over DW1/DW2 artifacts | `deepseek-v4-flash`/high | `codex/lc1-dw3-coverage-review` |
| Sol | DeepSeek 4 Pro | Architecture, acceptance, integration | Conductor only | (Conductor — this plan) |

DW1 and DW2 may proceed in parallel (disjoint file ownership). DW3 must wait
for both DW1 and DW2 to submit their artifacts.

**Corpus authorship rule:** No model certifies its own corpus. DW2 adapts
existing Sol-authored T1/T2 golden scenarios mechanically; Sol validates the
adapted semantics. DW3 (also DeepSeek Flash) provides independent review, not
certification — its review is veto/adversarial evidence, not corpus authority.

## File Ownership

### DW1 — Complete Temporal Through-Path

**Owns:**
- `app/services/diary/temporal.py` — add `_AT_TIME_RE`, `_ABOUT_TIME_RE`,
  `TemporalRelationKind` literal, update `extract_natural_time_constraints` to
  return a `TemporalExtraction` dataclass with `earliest`, `latest`, and
  `temporal_relation` fields, add `infer_temporal_relation()` for legacy
  commands
- `app/schemas/appointments.py` — add `temporal_relation: Optional[str]` to
  `SlotSearchCommandIn` (line ~739, extra="ignore" already present) and
  `SlotSearchProposalIn` (line ~683)
- `app/services/bernie_slot_normalizer.py` — pass `temporal_relation` through
  from `SlotSearchCommandIn` to `SlotSearchProposalIn`
- `app/services/bernie_booking_interpreter.py` — update
  `_extract_fake_command` to set `temporal_relation` on the command from the
  parsed extraction
- `app/services/diary/slot_search.py` or the slot-search route consumer —
  widen `latest_time` by 5 minutes when `temporal_relation == "exact"` (or
  legacy inference) before constructing the ORM query
- `app/services/diary/supervised_booking.py` or the duplicate classifier — gate
  `existing_booking_found` on `temporal_relation in ("exact",)` (only exact
  grants duplicate authority)
- `tests/test_bernie_temporal_policy.py` — add `at` operator tests,
  time-form variant tests, temporal-relation tests, approximate tests,
  unspecified tests, legacy-inference tests

**Must not touch:** scenario fixtures, T3 eval code, routes (except the
slot-search consumer), `app/services/bernie/scenario_spec.py`,
`app/services/bernie/language_normalization.py`, migrations

### DW2 — Scenario Contract + Normalization + Seed + Gap Report

**Owns:**
- New `app/services/bernie/scenario_spec.py` — `ReceptionScenarioSpec`
  dataclass/model with versioned canonical scenario contract fields
- New `app/services/bernie/language_normalization.py` — lossless
  normalization (Unicode NFKC, whitespace, case folding, punctuation, number/
  time forms); preserves original utterance
- New `tests/fixtures/bernie_scenario_spec/` — adapted T1/T2 seed cases:
  `booking_create_then_exact_duplicate.json`,
  `booking_overlap_not_exact_duplicate.json`,
  `interpret_clarify_temporal_bounds.json`
- New `tests/test_bernie_scenario_spec.py` — contract validation,
  normalization tests, seed fixture tests
- New `tests/fixtures/bernie_scenario_spec/README.md` — provenance/tier/
  adjudication
- New `scripts/bernie_coverage_lattice.py` — coverage lattice report
  generator (JSON output, explicit empty cells)
- New `tests/test_bernie_coverage_lattice.py` — report validation tests

**Must not touch:** `app/services/diary/temporal.py`, T3 eval code, routes,
schemas, migrations, `app/services/bernie/normalizer.py` (the existing
slot-normalizer facade), `app/services/bernie_slot_normalizer.py`,
existing scenario replay fixtures

### DW3 — Independent Review + Mechanical Sweep

**Owns:**
- New `orchestration/agent_inbox/codex/review-deepseek-lc1-dw3-coverage-review.md`
  (review artifact)

**Must not touch:** Any `app/` code, scenario fixtures, temporal module,
routes, schemas, migrations

DW3 is a read-only review lane. It runs all DW1 and DW2 deterministic acceptance
checks from a clean checkout of the integrated branches, reports pass/fail with
specific failure evidence, and produces the review artifact. It does not modify
any project code.

## Ordered Dependencies

```
DW1 (temporal through-path) ──┐
                                ├──> DW3 (independent review)
DW2 (contract + seed + gap)  ──┘
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
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3pm duration 15" \
  --provider fake \
  --reference-date 2026-07-14 \
  --json

# Assert: earliest_time is null, latest_time is null
# (Failure confirmed 2026-07-14: earliest_time=null, latest_time=null, result=interpreted, safe=true)
```

### DW1 acceptance

```powershell
# 2. `at` operator sets both earliest and latest (exact point time) + temporal_relation=exact
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3pm duration 15" \
  --provider fake \
  --reference-date 2026-07-14 \
  --expect-earliest-time 15:00 \
  --expect-latest-time 15:05 \
  --expect-temporal-relation exact \
  --expect-result interpreted

# 3. Time-form variants (all produce temporal_relation=exact)
# at 3 pm → 15:00, exact
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3 pm duration 15" \
  --provider fake --reference-date 2026-07-14 \
  --expect-earliest-time 15:00 --expect-temporal-relation exact

# at 3.00pm → 15:00, exact
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 3.00pm duration 15" \
  --provider fake --reference-date 2026-07-14 \
  --expect-earliest-time 15:00 --expect-temporal-relation exact

# at 15:00 → 15:00, exact
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow at 15:00 duration 15" \
  --provider fake --reference-date 2026-07-14 \
  --expect-earliest-time 15:00 --expect-temporal-relation exact

# 4. Existing operators still work
# after → not_before
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45" \
  --provider fake --reference-date 2026-07-14 \
  --expect-earliest-time 14:00 --expect-latest-time 15:45 \
  --expect-temporal-relation interval

# 5. Approximate operator (around/about)
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow around 3pm duration 15" \
  --provider fake --reference-date 2026-07-14 \
  --expect-earliest-time 14:30 --expect-latest-time 15:30 \
  --expect-temporal-relation approximate

# 6. Unspecified (bare time, no operator)
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\smoke_bernie_interpreter.py \
  --instruction "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 tomorrow 3pm duration 15" \
  --provider fake --reference-date 2026-07-14 \
  --expect-temporal-relation unspecified

# 7. All temporal tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_temporal_policy.py -q

# 8. All existing smoke tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py -q
```

### DW2 acceptance

```powershell
# 9. Scenario spec contract validates
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q

# 10. Adapted T1/T2 seeds pass contract validation
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q -k "seed"

# 11. Normalizer preserves original utterance and produces derived view
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q -k "normalize"

# 12. Coverage lattice emits valid JSON with explicit empty cells
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_coverage_lattice.py

# 13. Coverage report tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_coverage_lattice.py -q
```

### DW3 acceptance

```powershell
# 14. DW3 runs all DW1 and DW2 checks from integrated branches
# DW3 produces review artifact at:
# orchestration/agent_inbox/codex/review-deepseek-lc1-dw3-coverage-review.md

# 15. DW3 verifies:
# - `at 3pm` produces earliest_time=15:00, temporal_relation=exact
# - `at 3pm` no longer produces earliest_time=null, latest_time=null
# - TemporalRelationKind distinguishes all six values
# - Existing after/before/between operators are unchanged
# - approximate is defined, tested, and does not grant duplicate authority
# - unspecified is representable and tested
# - SlotSearchCommandIn and SlotSearchProposalIn carry temporal_relation
# - Scenario spec has all required fields from the LC plan
# - Adapted seed cases reference known T1/T2 scenario IDs
# - Coverage report explicitly shows empty cells
# - Existing T3 tests (test_bernie_shadow_eval_contract.py, test_bernie_shadow_corpus.py,
#   test_bernie_shadow_runner.py, test_bernie_shadow_live_gate.py) pass unchanged
```

### End-to-end duplicate regression (Sol after DW1+2+3 integration)

```powershell
# 16. Exact-time duplicate reaches deterministic duplicate outcome
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\test_scenario_replay.py -q -k "exact_duplicate"

# 17. Full scenario lab still passes
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\ tests\test_bernie_scenario_integrity.py -q

# 18. T3.1-T3.4 infrastructure unchanged
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_shadow_eval_contract.py tests\test_bernie_shadow_corpus.py tests\test_bernie_shadow_runner.py tests\test_bernie_shadow_live_gate.py -q

# 19. Readiness gate still blocked
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
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
| temporal relation threading tests | `fake-provider` |
| Slot-search consumer widening tests | `route-intercepted` |
| Duplicate classifier tests | `fake-provider` |
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
  - `at 3pm` produces `earliest_time=15:00`, `temporal_relation=exact`
  - `at 3pm` no longer produces `earliest_time=null, latest_time=null`
  - The `TemporalRelationKind` literal distinguishes all six values: `exact`,
    `not_before`, `not_after`, `interval`, `approximate`, `unspecified`
  - `exact` grants duplicate authority in the classifier; `approximate` and
    `unspecified` do not
  - Existing `after`/`before`/`between` operators are unchanged
  - `SlotSearchCommandIn` and `SlotSearchProposalIn` carry `temporal_relation`
    as `Optional[str]` with backward-compatible defaults
  - The slot-search consumer widens the window for `exact`
  - The scenario contract has all required fields from the LC plan
  - The adapted seed cases reference known T1/T2 scenario IDs
  - The coverage report explicitly shows empty cells
  - T3 tests (`test_bernie_shadow_eval_contract.py`,
    `test_bernie_shadow_corpus.py`, `test_bernie_shadow_runner.py`,
    `test_bernie_shadow_live_gate.py`) pass unchanged
- DW3 review is veto/adversarial evidence only. Sol owns final corpus
  authority and semantic adjudication.

## Worker Packet Files

All three worker packets are created with this plan:

- `orchestration/agent_inbox/deepcode/deepcode-flash-lc1-dw1-temporal-foundation.md`
- `orchestration/agent_inbox/deepcode/deepcode-flash-lc1-dw2-scenario-contract.md`
- `orchestration/agent_inbox/deepcode/deepcode-flash-lc1-dw3-coverage-review.md`

## Regular Sol Checkpoint

Sol commits this plan and worker packets to the Conductor branch
`deepcode/lc1-conductor` before dispatching any worker. Sol does **not** push
to `master` or `handoff/current`. Worker dispatch uses separate disposable
worktrees (see worker packets).

After all lanes submit and Sol reviews:

1. Sol integrates accepted artifacts into a single integration commit on
   `deepcode/lc1-conductor` (Conductor branch only — not master).
2. Sol records integration outcome.
3. Sol updates AGENTS.md with LC1 closeout notes.
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

STATUS: complete
