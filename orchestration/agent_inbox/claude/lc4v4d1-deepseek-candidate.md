# LC4V4D1 DeepSeek Candidate — Durable Worker Receipt

**Worker**: DeepSeek V4 Flash/high through Claude Code `--bare`
**Date**: 2026-07-15
**Worktree**: `C:\Users\sarashera\EMR4-worktrees\lc4v4d1-dw1`
**Branch**: `claude/lc4v4d1-diagnostic`
**Source head**: `191144f680ceb982d6c46739fa428f3f23298246`

## Owned paths

- `app/services/bernie/lc4v4_development_diagnostic.py`
- `tests/fixtures/bernie_lc4v4d1_development/`
- `tests/test_bernie_lc4v4d1_development_diagnostic.py`
- `docs/bernie-lc4v4d1-development-diagnostic.json`
- `docs/bernie-lc4v4d1-development-diagnostic.md`
- `orchestration/agent_inbox/claude/lc4v4d1-deepseek-candidate.md`

## Commands executed

```powershell
# Author 60 probes, write fixture files, run full diagnostic pipeline
python -c "from app.services.bernie.lc4v4_development_diagnostic import *; ..."

# Run focused tests
python -m pytest tests/test_bernie_lc4v4d1_development_diagnostic.py -v

# Check whitespace
git diff --check
```

## Fixture counts

| Family | Expected | Authored |
|--------|----------|----------|
| Entity | 30       | 30       |
| Dialogue | 12     | 12       |
| Safety (pairs) | 12 (6) | 12 (6) |
| Diary | 6        | 6        |
| **Total** | **60** | **60** |

## Hashes

- **Fixture hash**: `sha256:d32921760d2c87fb42ffd85918866b777561d0576c7c2733d890de4ee850e0ab`
- **Report hash**: `sha256:1241cf1175837db38b1887a564730cdba4bef388d932ad1b5c80c065bedf89eb`
- **Candidate parser-gap selection hash**: `sha256:ed65fe7821b0239066c532320bff05cc31a0699674987de8587efd74e05bbd44`
- **Empty selection fallback**: `sha256:e3b0c44298fc1c14`

## Classification counts

| Classification | Count |
|----------------|-------|
| authoring_invalid | 0 |
| parser_gap | 60 |
| policy_contract_gap | 0 |
| scorer_gap | 0 |
| planned_unavailable | 0 |
| supported_pass | 0 |

## Variance

- **Total observations**: 120 (60 probes × 2 repeats)
- **Variant observations**: 0
- **All 120 observations are deterministic**: true

## Protected boundary statement

Protected holdouts v1-v4 remain sealed. No protected fixture, support module,
authoring program, quality receipt, manifest, seal, consumed seal, test,
filename population, or case-level surface was accessed. The v4 aggregate
report (`docs/bernie-lc4v4-aggregate-report.json`) was read only as an
accepted historical input for diagnostic category selection; no v4 case,
wording, label, combination, or expected value was reconstructed.

## Decision

**DECISION: candidate_complete**

All 60 fixtures pass surface validation. All 120 observations are
deterministic with zero variance. The report hashes are stable. All
classifications follow the fixed precedence. Remediation is not authorized
in D1.

Any parser gaps identified require Gemini independent confirmation on the
exact recovered head before a future remediation contract.
