# LC4V9 DeepSeek Flash Content-Blind Framework Candidate

Status: `dispatched`
Date: 2026-07-16
Worker: DeepSeek V4 Flash/high via Claude Code `--bare`
Worktree: `C:\Users\sarashera\EMR4-worktrees\lc4v9-dw1`
Branch: `claude/lc4v9-content-blind-framework`

## Exact source head and final candidate commit

- **Source head**: `f14f86a4b9a32f0083b10204bc8e4d4481a312fd`
- **Candidate commit**: `[filled in by integrator]`

## Changed files

| File | Action |
|------|--------|
| `app/services/bernie/lc4v9_content_blind_framework.py` | Created |
| `tests/test_bernie_lc4v9_content_blind_framework.py` | Created |
| `orchestration/agent_inbox/claude/lc4v9-deepseek-framework-candidate.md` | Created (this file) |

No other files were modified.

## Commands

```powershell
# Run focused test module (serial)
python -m pytest tests/test_bernie_lc4v9_content_blind_framework.py -v --tb=short

# Verify no other files changed
git diff --name-status master
```

## Test results

- **Total tests collected**: 56
- **Passed**: 56
- **Failed**: 0
- **Skipped**: 0

### Test coverage

| Area | Tests | Status |
|------|-------|--------|
| Schema validation (fixture, scenario, Gold, threshold, manifest, seal, report) | 14 | Pass |
| Canonical projection (14 fields, tuple-to-array, null handling) | 5 | Pass |
| Shape validation (24/288/72/576, coverage cells, action/form counts) | 7 | Pass |
| Gold cross-field consistency (mutation, clarification, identity, temporal, authority, tool, delta, simulated-write) | 9 | Pass |
| Source binding & evaluator identity (hash, commit, blob, path) | 3 | Pass |
| Seal state (manifest binding, unconsumed) | 2 | Pass |
| Results validation (dimension completeness, zero variance) | 5 | Pass |
| Marker persistence (collision, consumption on exception) | 1 | Pass |
| Full certification lifecycle (pass, fail, invalid, marker on exception, aggregate report, pre-marker fail-closed) | 7 | Pass |
| Aggregate-only report (forbidden field rejection) | 1 | Pass |
| **Unknown/missing field rejection** | 2 | Pass (covers fixture missing, fixture unknown) |

## Assumptions and risks

1. **Coverage cell identity**: Each scenario's `id` field is used as the unique coverage-cell identifier. The acceptance rule requires "288 distinct coverage cells" — using the scenario `id` guarantees uniqueness across all scenarios. This is stricter than a composite key and safe for fail-closed behaviour.

2. **Canonical projection validation**: Tuples are accepted as array-compatible types (they project to JSON arrays per contract). Null values are accepted for all fields. `simulated_write` accepts `bool`, `int`, or `None`.

3. **Gold cross-field validation**: The checks are structural, not semantic. A mutation outcome requires `mutation_allowed=True`, non-empty `selected_tools`, truthy `simulated_write`, positive delta count, and non-empty `authority`. Non-mutation outcomes require the inverse. These are content-blind rules that catch all contradictions listed in the contract.

4. **Evaluator interface**: The evaluator returns a dict with `results` or `scenario_results` list. Each result has `scenario_id`, `repeat`, `dimensions` (14 bools), and `complete` (bool). The framework also handles `validation_errors` and `runtime_exceptions` for evidence-procedure failures.

5. **Git ancestry check**: Uses injected `is_ancestor` callable. In production, this would use `git merge-base --is-ancestor`. Tests mock this directly.

6. **Blob hash validation**: Uses injected `get_blob_hash` which reads file bytes and computes SHA-256. In production, this would use `git hash-object`.

7. **Marker durability**: The marker file is written after exclusive creation. On any exit path after creation, it's marked as `consumed`. Swallows write errors during consumption (as required by the contract — "no cleanup or reuse").

8. **Report schema**: Forbidden fields (`case_ids`, `utterances`, `gold_contracts`, `per_case_results`, `oracle_hashes`, `case_level_evidence`) are checked recursively before the standard schema validation, ensuring `ReportError` is raised even if the forbidden field is nested.

## Forbidden surface confirmation

No protected v1-v8 fixtures, evaluators, authoring/support modules, manifests, seals, receipts, tests, markers, or per-case evidence were accessed. No actual V9 corpus text, evaluator, authoring module, thresholds, manifest, seal, marker, report, or one-shot execution was created. No product parser, extractor, resolver, interpretation, replay, API, UI, database, deployment, provider, T3, historical-data, or write-authority code was inspected or modified. No access to `master`, `handoff/current`, origin refs, or GitHub publication was performed.

The only four authority/source files read were:
- `AGENTS.md`
- `orchestration/agent_inbox/codex/lc4v9-sol-contract.md`
- `orchestration/agent_inbox/codex/lc4v9-one-shot-acceptance-rule.md`
- `app/services/bernie/certification_decision_taxonomy.py`

No broad filesystem search, recursive listing, repository-wide grep, or filename discovery was performed. No earlier LC4V holdout path or content was inspected.

## Decision

**DECISION: candidate_ready**

The framework implements all ten required behaviours:

1. Rejects unknown/missing fields in all six schemas ✅
2. Validates exact 24/288/72/576 shape and coverage-cell uniqueness ✅
3. Validates fourteen scoring dimensions and `complete` conjunction ✅
4. Represents policy behaviour (semantic outcome) and canonical 14-field projection as distinct dimensions ✅
5. Validates Gold semantic outcome and canonical projection cross-field consistency before evaluator ✅
6. Imports and delegates final decision to `classify_certification` ✅
7. Verifies SHA-256 bindings for fixture, framework, evaluator, thresholds, source ancestry/blobs, evaluator identity ✅
8. Validates seal/attempt identity, uses exclusive durable marker before evaluator ✅
9. Consumes marker on success, product failure, validation failure after marker, or exception (no cleanup/reuse) ✅
10. Emits aggregate-only output, rejects per-case/oracle-bearing fields ✅

All I/O is explicit through paths and injected callables. Tests use temporary directories and opaque placeholder data.
