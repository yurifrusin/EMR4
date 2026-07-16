# LC4V6 DeepSeek Empty-Framework Candidate

**Date:** 2026-07-16
**Worker:** DeepSeek V4 Flash/high through Claude Code `--bare`
**Worktree:** `C:\Users\sarashera\EMR4-worktrees\lc4v6-dw1`
**Branch:** `claude/lc4v6-content-blind-framework`
**Source head:** `4b9caf98064fd5009ac2e5e1673a5a22d70273ed`

## Changed files

| File | Status |
|---|---|
| `app/services/bernie/lc4v6_content_blind_framework.py` | Created |
| `tests/test_bernie_lc4v6_content_blind_framework.py` | Created |

No existing files were modified. No fixtures, content, examples, manifests,
seals, reports, acceptance rules, or scenario utterances were created.

## Test results

**Total:** 75 passed, 0 failed, 0 skipped
**Command:** `C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest tests/test_bernie_lc4v6_content_blind_framework.py -q`

### Test classes

| Class | Tests | Description |
|---|---|---|
| `TestPlaceholderMetadata` | 6 | ScenarioContract/TypedObservation accept valid placeholders |
| `TestManifestValidation` | 11 | Every malformed population boundary rejected |
| `TestAggregateLeakageRefusal` | 4 | AggregateReport leaks no case-level fields |
| `TestHashIntegrity` | 11 | Hash binding detects tampering |
| `TestEvidenceValidation` | 6 | Evidence population, hash/schema consistency |
| `TestDependencyInjection` | 3 | EvaluationContext with injectable protocols |
| `TestStateMachinePreRunFailures` | 8 | State machine fails closed on all invalid states |
| `TestStateMachineSuccess` | 3 | Successful single consumption in temp dir |
| `TestStateMachineRerunCases` | 6 | Refuses rerun, overwrite, reuse |
| `TestFixedShapeConstants` | 6 | Fixed shape matches contract |

### Framework properties

1. **Frozen typed schema:** `ScenarioContract` (group, cell, action, is_multi_turn, data) and `TypedObservation` (dimensions) — both `@dataclass(frozen=True)`, no real V6 content.
2. **Strict manifest validation:** `validate_manifest_shape()` enforces exact fixed shape (24 groups, 288 scenarios, 72 multi-turn, 216 one-shot, 6 actions, 288 cells, 2 repeats). Accepts scenario objects as supplied data.
3. **Hash binding helpers:** `bind_source_hash`, `bind_corpus_hash`, `bind_manifest_hash`, `bind_framework_hash`, `bind_evaluator_hash` plus `hash_content`, `hash_bytes`. All return `sha256:<hexdigest>`. `BoundHashes` frozen container.
4. **Aggregate-only reducer:** `reduce_observations()` returns `AggregateReport` containing only `total_samples`, `complete`, `safe`, `variance`, `dimensions`, `slices`, `hashes`, `attempt_id`. No scenario IDs, utterances, expected values, source spans, normalized turns, labels, or failure selections.
5. **Evidence validator:** `validate_evidence_population()` checks exact population (576 = 288×2), zero variance, hash prefix consistency (`sha256:`), and manifest shape consistency.
6. **One-shot state machine:** `OneShotStateMachine` — fails closed unless seal present/unconsumed and marker/report absent. On success, writes marker (`lc4v6-fresh-attempt-001`), consumes seal (overwrites with empty), writes report. Refuses rerun/overwrite/reuse.
7. **Dependency injection:** `EvaluationContext` with `Extractor`, `PolicyResolver`, `ReplayEvaluator` protocols. All fields optional for empty tests.
8. **No import-time execution:** Module contains only function/class definitions; no top-level side effects.

## Known limitations

- No real V6 scenario contracts, utterances, expected values, or prompts exist.
- Threshold acceptance rule is not implemented (Sol writes the separate frozen rule).
- No scenario ID branching in product interpretation (intentionally absent).
- The `OneShotStateMachine` does not use file locking for cross-process safety (not required for the single-process one-shot evaluation).
- Aggregate slice arithmetic in `reduce_observations` returns empty slices (real computation filled by future evaluator).

## Blockers

None.

---

*End of candidate artifact*

DECISION: pass
