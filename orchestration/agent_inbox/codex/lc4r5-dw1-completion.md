# LC4R5 DW1 — Explanation Clarification / Action Semantics — Completion

## Scope

Repair only the `explain_schedule` clarification rule: a resolved practitioner
is sufficient read-only context.  Preserve clarification for ambiguous and
context-free explanations.  Do not broaden `_EXPLAIN_PATTERNS`.

## Commands / Results

```
pytest tests/test_bernie_semantic_extraction.py -v
# 146 passed (19 new LC4R5 + 127 existing)

pytest tests/test_bernie_lc4r4_report.py -v
# 2 passed (no regression)

python scripts/bernie_lc4r5_report.py --check
# LC4R5 CHECK PASSED
```

## Hashes / Counts

| Item | Expected | Observed |
|---|---|---|
| repair count | 84 | 84 |
| repair hash | `b69abbcbc6febe29` | `b69abbcbc6febe29` |
| preserve count | 12 | 12 |
| preserve hash | `34c95db64c716f56` | `34c95db64c716f56` |
| intended_action | 880/1152 | 880/1152 |
| action_semantics | 814/1152 | 814/1152 |
| temporal_relation | 628/1152 | 628/1152 |
| normalized_values | 101/1152 | 101/1152 |
| entity_semantics | 300/1152 | 300/1152 |
| clarification | 782/1152 | 782/1152 |
| safety | 1152/1152 | 1152/1152 |
| repeat_variance | zero | zero |

## Boundaries Preserved

- `_EXPLAIN_PATTERNS` not broadened
- No edit to generated fixtures, AGENTS.md, scenario schemas, action grammar,
  route contracts, providers, routes/API, DB, UI, T3 gates, deployment
- No holdout v1 access
- Patient-specific explanation behaviour unchanged
- Generic calendar/availability anti-overmatch unchanged
- Safety/negation/tool/authority boundaries unchanged
- Lossless normalization and oracle independence unchanged
- `check_in` remains planned-not-implemented

## Candidate Commit

```
Author: DeepSeek V4 Flash/high via Claude Code --bare
Branch: lc4r5-dw1 (worker branch)
```

## DECISION: pass
