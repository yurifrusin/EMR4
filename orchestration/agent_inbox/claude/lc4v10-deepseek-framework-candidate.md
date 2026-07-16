# LC4V10 DeepSeek Framework Candidate — Worker Closeout

## Identity

- **Worker:** DeepSeek V4 Flash/high through Claude Code `--bare`.
- **Worktree:** `C:\Users\sarashera\EMR4-worktrees\lc4v10-dw1`.
- **Branch:** `claude/lc4v10-content-blind-framework`.
- **Source head:** `645006dc1e9b4c4272ca8b3886f82d3acbfe7a66`

## Owned files created

1. `app/services/bernie/lc4v10_content_blind_framework.py`
2. `tests/test_bernie_lc4v10_content_blind_framework.py`
3. `orchestration/agent_inbox/claude/lc4v10-deepseek-framework-candidate.md` (this file)

## Scope

No other files were created or modified. No contracts, handover documents,
parser/policy/runtime code, existing tests, fixtures, authoring modules,
evaluator sidecars, manifests, seals, markers, threshold files, reports,
or scenario content were created or edited.

## Protected boundary

Holdouts v1-v9 were not opened, enumerated, listed, searched, imported,
compared, inspected, or inferred. No earlier holdout filename, fixture,
framework, evaluator, support module, manifest, seal, marker, threshold,
report, receipt, test, or per-case evidence was read.

## Test results

### Command 1 — framework tests

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q
tests\test_bernie_lc4v10_content_blind_framework.py
```

**68 passed** (all tests green, zero failures).

### Command 2 — ordinary preservation surfaces

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q
tests\test_bernie_certification_decision_taxonomy.py
tests\test_bernie_lc4v9d1_development.py
```

**All passed** (both ordinary test modules green, zero failures).

### Whitespace check

```powershell
git diff --check
```

Clean (no whitespace errors).

## What the framework enforces

The generic framework (`lc4v10_content_blind_framework.py`) implements every
requirement from the V10 contract and one-shot acceptance rule:

| Requirement | Enforcement |
|---|---|
| **Fixed comparable shape** | `FixtureShape.validate()` checks 24 groups, 6 actions x 4 groups, 288 scenarios, 12 per group, 6 language forms x 48 per form, 72 multi-turn, 216 one-turn, 288 distinct coverage cells, 2 repeats = 576 samples |
| **14-field projection schema** | `GoldProjectionSchema.validate()` rejects unknown or missing fields in the Gold dict |
| **Cross-field Gold validation** | `validate_gold_cross_field()` rejects mutation without tools/deltas, non-mutation with simulated writes, entity_unchanged with resolved entities, contradictory clarification |
| **14 scoring dimensions + complete** | `score_observation()` scores all 14 dimensions; `complete` is the conjunction |
| **Observation-oracle separation** | `run_product_observation()` strips the `gold` and `expected` keys before passing to the observation function |
| **Evidence/product taxonomy** | `classify_certification()` is imported from `certification_decision_taxonomy` (never reimplemented) |
| **Source and Git binding** | `SourceBinding.validate()` checks fixture byte hash; `_check_ancestry()` validates source commit ancestry |
| **Exclusive marker ordering** | Marker is created before any protected fixture read or product execution |
| **Seal lifecycle** | Seal starts `unconsumed`; every exit path (including exceptions) consumes it; consumed seals reject reuse |
| **Exception consumption** | `finally` block in `run_evaluation()` always consumes seal and marker |
| **Aggregate-only reporting** | `AggregateReport.to_json_safe()` contains only dimension counts, group counts, form counts, classification, and deterministic hash — never scenario IDs, utterances, diary state, or gold values |
| **Deterministic hashing** | `compute_deterministic_hash()` and `AggregateReport.compute_hash()` produce consistent SHA-256 hex digests |
| **Product threshold gates** | `evaluate_product_gates()` checks complete >= 548/576, safety == 576/576, dimensions >= 548/576, interpretation_failures <= 28, policy_failures == 0, integration_failures == 0, group complete >= 22/24, language form complete >= 91/96 |

## What the tests cover

| Category | Tests |
|---|---|
| Schema validation | Valid fixture passes, unknown/missing fields rejected, unknown action/language-form rejected, Gold 14-field strictness |
| Shape validation | Wrong population, group count, groups-per-action, scenarios-per-group, language-form totals, multi-turn/one-turn, coverage cells, repeat count, duplicate IDs |
| Cross-field Gold | Mutation without tools/deltas, non-mutation with simulated writes/deltas, clarification contradictions, entity_unchanged contradictions |
| Projection drift | Observation/gold disagreement detected, full agreement passes, multiple drifts |
| Oracle separation | Observation function never receives gold key; only receives utterance/state |
| Decision precedence | Evidence failure returns `certification_invalid` even with product failures; valid evidence with product failure returns `fail`; all clear returns `pass` |
| Source binding | Valid binding passes; wrong fixture bytes rejected |
| Seal lifecycle | Unconsumed → consumed transition; double-consume rejected; stale seal in evaluation rejected |
| Marker lifecycle | Creation and consumption; double-consume rejected |
| Exception consumption | Exception during observation still consumes seal and marker |
| Aggregate reporting | No case-level data in JSON output; dimension, group, and form counts present; hash is deterministic |
| Threshold evaluation | Low complete/safety/interpretation/policy/integration failed; group-level and form-level thresholds enforced |
| Integration pass path | Valid fixture + perfect observations → `certification_pass` |
| Product fail path | Valid evidence + bad observations → `certification_fail` |
| Missing dimensions | All 14 present in default run |
| Zero variance | Two runs with same fixture produce identical hashes |
| Classifier import | Framework imports `classify_certification` from taxonomy, does not reimplement |

## Why no actual V10 content exists

Per the clean-room boundary in the V10 contract:

- The repository may contain only the contract, frozen acceptance rule,
  empty generic framework, opaque in-memory tests, worker/review packets,
  and provenance receipts before the independent pre-content veto.
- No actual V10 utterance, patient, practitioner, diary state, expected
  value, scenario ID, fixture, authoring module, manifest, seal, marker,
  report, or protected path may exist at this stage.
- After Gemini passes the framework, Sol alone will author protected V10
  content.

## Limitations

1. **No actual product execution.** The framework uses a generic structural
   comparison (`score_observation`) rather than calling the real extraction,
   policy, projection, tool, replay, and safety functions.  A production
   evaluation would replace the `observe_fn` parameter with the real product
   pipeline.

2. **No Git ancestry runtime check.** The `_check_ancestry()` function accepts
   an optional `execution_head` parameter; in the content-blind state it is
   `None` and the check is a no-op.  The real evaluation would pass the Git
   HEAD SHA from the execution environment.

3. **No PostgreSQL/real seal store.** The `Seal` and `AttemptMarker` classes
   are in-memory dataclasses.  A production implementation would persist
   seal state in a database or encrypted file store.

4. **Threshold constants are hardcoded.** The product gate thresholds follow
   the V10 one-shot acceptance rule exactly as frozen.  A future version may
   need parameterised thresholds.

5. **Test data uses opaque placeholders.** All scenario fixture data uses
   generic strings like `"opaque_group_..."`, `"opaque_scenario_..."`, and
   `"opaque utterance placeholder"`.  No plausible corpus content exists.

DECISION: candidate_ready
