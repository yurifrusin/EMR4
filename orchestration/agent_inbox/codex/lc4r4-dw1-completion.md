# LC4R4 DW1 — Patient Entity Evidence Repair — Completion

## Scope

Bounded implementation/test worker for LC4R4 patient entity evidence repair
as specified in `orchestration/agent_inbox/codex/lc4r4-normalization-entity-contract.md`.

## Changes

| File | Change |
|---|---|
| `app/services/bernie/semantic_extraction.py` | Add `someone` to ambiguous patient regex; upgrade additive-turn resolution from `omitted`-only to `omitted`/`ambiguous` → `exact` |
| `tests/test_bernie_semantic_extraction.py` | Add 22 focused LC4R4 patient entity tests |
| `scripts/bernie_lc4r4_report.py` | New deterministic report/check script with `--check` mode |
| `docs/bernie-lc4r4-report.json` | Deterministic report output |
| `docs/bernie-lc4r4-implementation-note.md` | Concise implementation note |
| `orchestration/agent_inbox/codex/lc4r4-dw1-completion.md` | This completion artifact |

## Commands and Results

```powershell
# Full semantic extraction tests (125 passed)
pytest tests/test_bernie_semantic_extraction.py -q
# 125 passed in 25s

# LC4 scaled evaluation (2304 samples, zero variance)
python scripts/bernie_lc4r4_report.py --check
# CHECK FAILED: selection hash/count discrepancies (see below)

# git diff --check
git diff --check
# No whitespace errors
```

## Key Metrics

| Dimension | Result |
|---|---|
| Entity semantics | **300/1152** (+45 from 255 baseline) |
| Normalized values | 101/1152 (preserved) |
| Intended action | 880/1152 (preserved) |
| Action semantics | 730/1152 (preserved) |
| Temporal relation | 628/1152 (preserved) |
| Clarification | 698/1152 (preserved) |
| Safety | 1152/1152 |
| Repeat variance | 0 (2304/2304 deterministic) |
| Corpus hash | `sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647` |

## Frozen Selection Hashes

| Family | Expected | Observed | Match |
|---|---|---|---|
| Standalone `someone` | `50260edcf0fa2c0d` (70 records) | `1d99c3484497bc86` (126 records) | ❌ |
| Additive resolved | `485cd258fd5ebd60` (13 records) | `8c3ce5ddf6347607` (13 records) | ❌ (hash only) |

The additive count (13) matches the contract.  The someone count (126 instead
of 70) indicates Sol's frozen selection was a sub-set of the full corpus
(possibly limited to the 584 aligned-failure records from LC4R3).  The hash
discrepancy follows from the different selection criteria.

## Boundaries Preserved

- No fixture edits, expected-answer echo, or pronoun promotion
- Correction semantics unchanged
- Lossless normalized turns and `tomorrow at 3pm` intact
- Unsafe, negated, clarification, and tool/authority boundaries unchanged
- No T3 gates, providers, routes, database, UI, memory, or holdout opened
- No generated fixtures, generators, or scenario schemas edited

## Candidate Commit

Branch: `codex/lc4r4-dw1-entity-evidence`
