# LC4V2 Content-Blind Framework

> **Status:** Framework-only — no v2 content exists.  Sol accepts or rejects
> candidate files after independent Gemini veto.
>
> **Branch:** `claude/lc4v2-content-blind-framework`
> **Head:** `8411b6ea622f840f4fd051322ce5762d14beb023` (source), then the
> worker head containing this document.

## Purpose

Implement the provider-free, content-blind contracts and CLI that the
LC4V2 fresh-holdout certification will use once Sol authors the real 24-group,
288-variant, 72-multi-turn synthetic Gold corpus.

All five owned files are **candidates only**.  Sol retains acceptance and may
reject or recover them before v2 content creation.

## Owned files

| Path | Role |
|---|---|
| `app/services/bernie/holdout_v2_contract.py` | Immutable/versioned Pydantic contracts for group envelope, manifest, pre-consumption seal, aggregate report, consumed seal, plus building, verification, seal creation, evaluation placeholder, and one-shot consumption. |
| `scripts/bernie_holdout_v2.py` | Explicit CLI: `build-manifest`, `create-seal`, `evaluate-once`, `consume`, `check`.  Non-mutating by default; `--write` required to create files. |
| `tests/test_bernie_holdout_v2_contract.py` | ~50 tests covering all fail-closed conditions using only tiny temporary synthetic fixtures authored inline.  No v1 reference. |
| `docs/bernie-lc4v2-framework.md` | This document. |
| `orchestration/agent_inbox/codex/lc4v2-dw1-completion.md` | Worker completion artifact (this worker's handoff). |

## Contracts

### 1. `ScenarioGroupEnvelope`

- Contains exactly 12 `ReceptionScenarioSpec` variants.
- Exactly 3 variants are multi-turn (`dialogue_form != "one_shot"`).
- Every variant is Gold (`provenance="gold"`) and adjudicated
  (`adjudication="adjudicated"`).
- All `scenario_id` values within the group are unique.
- `expected_outcome_kind` is always present (explicit `null` allowed).

### 2. `Manifest`

- Binds relative group file paths with `sha256:<hex>` digests.
- Records `corpus_hash` (SHA-256 of concatenated file content).
- Records exact production counts: 24 groups, 288 variants, 72 multi-turn.
- Frozen/immutable.  Rejects absolute/traversal paths, duplicate paths,
  wrong corpus version.

### 3. `PreConsumptionSeal`

- Binds corpus version `lc4-holdout-v2`, manifest hash, source commit,
  evaluator/schema versions, evaluation ID `lc4-holdout-v2-baseline-001`,
  repeat count 2, and state (`created` or `consumed`).
- Frozen/immutable.

### 4. `AggregateReport`

- Contains only dimension passed/failed totals, failure layer totals,
  safety_pass/safety_total, variance, critical-slice aggregates,
  coverage-cell counts, corpus_hash, and report_hash.
- No utterance, dialogue, group/scenario/variant identifier, expected
  label/outcome/tool/delta, source span, normalised value, observation,
  case finding, or per-case result.
- `check_forbidden_keys()` recursively rejects any key in
  `FORBIDDEN_REPORT_KEYS`.
- Every dimension total must equal 576 (288 variants × 2 repeats).
- Extra fields are rejected by Pydantic `extra="forbid"`.

### 5. `ConsumedSeal`

- One-shot: binds the aggregate report hash exactly once.
- Frozen/immutable, state is always `"consumed"`.
- Records `consumed_at` timestamp.

## Key behaviours

- **Manifest verification** rejects missing/extra files, absolute/traversal
  paths, duplicate paths/IDs, byte or hash drift, wrong corpus version, and
  count drift.
- **Consumption** is one-way and one-shot: only a valid `"created"` seal can
  consume a schema-valid aggregate report at the bound source commit.
  Consumed input, report drift, wrong commit, or a second consumption fails
  closed.
- **CLI** commands are explicit and non-mutating by default.  `--write` is
  required to create files.  Never infers or auto-discovers a protected
  directory.  Never invokes Git mutation.
- **Tests** use only tiny temporary synthetic fixtures authored in the test
  file.  No v1 fixture, support module, seal, receipt, report, or path is
  referenced.

## Fail-closed conditions

| Condition | Mechanism |
|---|---|
| Wrong number of variants per group | Pydantic `min_length`/`max_length=12` + model validator |
| Wrong multi-turn count | Model validator checks exactly 3 per group |
| Non-gold provenance | Model validator rejects in envelope |
| Non-adjudicated | Model validator rejects in envelope |
| Duplicate IDs | Model validator (within group) + verify_manifest (cross-group) |
| Missing expected_outcome_kind | Pydantic required field + model validator |
| Missing manifest file | `verify_manifest` compares file sets |
| Extra unlisted file | `verify_manifest` compares file sets |
| Hash mismatch | `verify_manifest` recomputes SHA-256 |
| Corpus version mismatch | Pydantic pattern + verify_manifest check |
| Count drift | `verify_manifest` compares to expected counts |
| Wrong dimension total | `AggregateReport._validate_dimension_totals` |
| Forbidden report key | `check_forbidden_keys()` recursion |
| Report hash mismatch | `consume_report` recomputes hash |
| Already-consumed seal | `consume_report` checks `state == "consumed"` |
| Wrong source commit | `consume_report` compares seal commit |

## Limitations

- The evaluation function (`run_aggregate_evaluation`) is a content-blind
  placeholder that validates the manifest and returns a zero-failure report.
  Sol replaces it with real deterministic interpretation, replay, and scoring
  when v2 content exists.
- The `source_spans` lossless-check is inherited from
  `ReceptionScenarioSpec`'s own validator and is not re-implemented here.
- The `--write` flag creates files at configurable paths but does not perform
  Git operations.
- No provider, database, network, or write surface is invoked.
- All count parameters are injectable only for tests; production CLI defaults
  fail closed to 24/288/72.
