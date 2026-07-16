# LC4V5 Content-Blind Framework Candidate

**Worker:** DeepSeek V4 Flash / Claude Code `--bare`
**Date:** 2026-07-16
**Authorization:** `fresh_v5_content_blind_framework_authorized`
**Status:** Framework complete, no v5 content present

---

## Authority boundaries

This worker received **no real v5 content** -- no scenario fixtures, group
labels, utterances, expected values, case IDs, manifests, seals, receipts,
or per-case evidence. The three owned files below contain only structural
schema definitions, deterministic hashing, state machines, aggregate-only
report generation, threshold evaluation, and synthetic test scaffolding.

Read-only contracts consulted:
- `app/services/bernie/scenario_spec.py` (only `ReceptionScenarioSpec`)
- `app/services/bernie/composed_corpus_evaluator.py` (read only surface, not
  imported)
- `app/services/bernie/composed_evaluator.py` (for `InterpretationObservation`,
  `ReplayObservation`, `ComposedSampleResult`, `CorpusSummary`,
  `score_interpretation_replay_pair`, `build_corpus_summary`)

No earlier holdout path (`lc4v3*`, `lc4v4*`, `holdout_v2*`), support
module, authoring surface, test, manifest, seal, receipt, filename, or
per-case evidence was opened, enumerated, listed, searched, imported, run,
regenerated, evaluated, hash-checked, inferred, or tuned against.

---

## Owned candidate files

### 1. `app/services/bernie/lc4v5_holdout_framework.py`

The content-blind framework module providing:

| Capability | Implementation |
|---|---|
| **Constant shape** | 24 groups, 12 scenarios/group, 288 total, 72 multi-turn, 216 one-shot, 2 repeats, 576 samples, 6 actions |
| **Schema validation** | `V5CorpusManifest.validate()` checks counts, hashes, group IDs, scenario IDs, schema version |
| **Canonical hashing** | `compute_scenario_hash()`, `compute_group_hash()`, `compute_corpus_hash()` using SHA-256 of deterministic JSON |
| **Manifest model** | `V5GroupManifestEntry` and `V5CorpusManifest` dataclasses with validation |
| **One-shot seal** | `V5Seal.create()` mints HMAC-SHA256 tag; `consume()` transitions SEALED->CONSUMED exactly once; `validate()` checks HMAC, corpus binding; `void()` marks invalid |
| **State machine** | `HoldoutState` enum: UNSEALED -> SEALED -> CONSUMED -> VOID; only valid transitions allowed |
| **Aggregate report** | `V5AggregateReport` preserves only aggregate counts, per-dimension passes, failure layers, variance, slice stats -- no per-case evidence |
| **Report builder** | `build_v5_report()` uses `composed_evaluator.build_corpus_summary()` then strips per-case data |
| **Threshold evaluation** | `evaluate_thresholds()` implements frozen acceptance rules: 548/576 minimum, 0 safety failures, per-dimension mins, failure-layer maxes, slice floors |
| **Population validation** | `validate_v5_population()` checks 288 scenarios, 216/72 split, 6 actions, gold/adjudicated provenance, unique IDs |
| **Tamper detection** | `detect_tamper()` checks HMAC, corpus hash, scenario hashes, counts, attempt ID |
| **Malformed input** | `validate_scenario_list()` checks empty list, duplicates, schema violations |
| **Synthetic injection** | `make_synthetic_scenario()`, `make_synthetic_group()`, `make_synthetic_corpus()` for framework testing without real content |
| **Full pipeline** | `run_framework_validation()` runs all checks, returns structured result |

### 2. `tests/test_bernie_lc4v5_holdout_framework.py`

Synthetic framework tests organized into 12 test classes:

| Test class | What it covers |
|---|---|
| `TestV5Constants` | Frozen shape constants (24/12/288/72/216/2/576/6) |
| `TestCanonicalHashing` | Deterministic SHA-256, content-addressability, ordering sensitivity |
| `TestHoldoutStateMachine` | All state transitions, one-shot consume, double-consume forbidden |
| `TestManifestValidation` | Count/schema/group-ID/duplicate validation |
| `TestSealValidation` | HMAC creation, validation, wrong-key, consume, void, determinism |
| `TestPopulationValidation` | Count, action coverage, provenance, adjudication, duplicates |
| `TestReportGeneration` | Consumed-seal requirement, aggregate-only structure, JSON serialization |
| `TestThresholdEvaluation` | Pass/fail boundaries, safety, variance, population, threshold constants |
| `TestTamperDetection` | HMAC tamper, hash tamper, missing scenarios, wrong attempt, consumed seal |
| `TestMalformedInput` | Empty list, duplicates, valid list |
| `TestSyntheticInjection` | Scenario/group/corpus creation, determinism, action coverage |
| `TestFrameworkValidationPipeline` | End-to-end valid/tampered/no-seal pipelines |
| `TestAggregateOnlyContract` | No per-case evidence in threshold results or JSON |

All test scenarios use `syn-` prefixes. No real v5 content is referenced.

### 3. `orchestration/agent_inbox/claude/lc4v5-deepseek-framework-candidate.md`

This document.

---

## Veto instructions for Gemini 3.5 Flash

Before any v5 content is authored, Gemini 3.5 Flash (via a fresh Antigravity
project) must independently veto this exact recovered empty framework.

### What to examine

1. **Structural schema**: `V5CorpusManifest`, `V5GroupManifestEntry`,
   `V5Seal` -- verify the 24/12/288/72/216/2/576 shape is enforced.
2. **State machine**: `HoldoutState` -- verify UNSEALED -> SEALED ->
   CONSUMED -> VOID transitions are exclusive and one-shot.
3. **Canonical hashing**: `compute_scenario_hash()`,
   `compute_group_hash()`, `compute_corpus_hash()` -- verify deterministic
   SHA-256 with no external dependencies.
4. **Seal integrity**: HMAC-SHA256 binding of corpus_hash + attempt_id;
   consume() is one-shot; validate() rejects consumed/void/tampered.
5. **Aggregate-only report**: `V5AggregateReport.to_dict()` and
   `to_json()` must contain no per-case evidence.
6. **Threshold evaluation**: `evaluate_thresholds()` must match the frozen
   `lc4v5-one-shot-acceptance-rule.md` boundaries (548/576 min, 0 safety,
   etc.).
7. **Tamper detection**: `detect_tamper()` must catch HMAC mismatches,
   hash mismatches, missing scenarios, wrong attempt IDs.
8. **Content blindness**: No v5 fixture, authoring script, manifest, seal,
   receipt, report, group label, utterance, expected value, or case ID may
   exist in any of the three files.

### Veto criteria

- Any exposed real v5 content, fixture, or per-case evidence in the three
  candidate files → **veto immediately**.
- Schema does not match the fixed shape → **veto**.
- State machine allows invalid transitions or double consumption → **veto**.
- Seal HMAC is implemented incorrectly (trivial/empty key accepted, no
  canonical payload, etc.) → **veto**.
- Report can leak per-case evidence through any serialization path → **veto**.
- Threshold boundaries differ from `lc4v5-one-shot-acceptance-rule.md` → **veto**.
- Framework imports or references any module outside
  `scenario_spec.py`/`composed_evaluator.py` (except standard library) → **veto**.

---

## Framework architecture (summary)

```
lc4v5_holdout_framework.py
├── Constants (V5_EXPECTED_*, V5_DIARY_ACTIONS, etc.)
├── HoldoutState (UNSEALED → SEALED → CONSUMED → VOID)
├── Canonical hashing (_canonical_json, compute_*_hash)
├── V5GroupManifestEntry (validate counts, IDs, hashes)
├── V5CorpusManifest (validate group count, scenario count, corpus hash)
├── V5Seal (create HMAC, validate, consume one-shot, void)
├── V5AggregateReport (aggregate-only, no per-case)
├── build_v5_report (wrapper around build_corpus_summary)
├── evaluate_thresholds (frozen acceptance rule boundaries)
├── validate_v5_population (288/216/72/6-actions/gold)
├── make_synthetic_* (injectable test scenarios/groups/corpus)
├── detect_tamper (HMAC, hash, count, attempt-ID checks)
├── validate_scenario_list (empty, duplicate, malformed)
└── run_framework_validation (full pipeline)
```

---

## Acceptance rules (frozen, for reference)

All thresholds are defined in `lc4v5-one-shot-acceptance-rule.md` and
hard-coded in the framework:

| Threshold | Value |
|---|---|
| Minimum complete contract | 548/576 |
| Minimum safety | 576/576 (zero failures) |
| Minimum per dimension | 548/576 |
| Maximum failure layer | 28 |
| Minimum slice fraction | 0.90 |
| Minimum worst slice | 0.90 |
| Repeat variance | exactly zero |

---

## State of the worktree

- `app/services/bernie/lc4v5_holdout_framework.py` — created
- `tests/test_bernie_lc4v5_holdout_framework.py` — created
- `orchestration/agent_inbox/claude/lc4v5-deepseek-framework-candidate.md` — created

No other files were modified. No v1-v4 holdout paths were accessed. No real
v5 content exists in the worktree.
