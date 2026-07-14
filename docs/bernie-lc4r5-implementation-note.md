# LC4R5 — Explanation Clarification / Action Semantics

## What was repaired

The `_determine_clarification` function in
`app/services/bernie/semantic_extraction.py` previously required patient
identification for every `explain_schedule` action.  This meant that a
perfectly clear practitioner-relative question such as "Can you explain Dr
Shera's schedule tomorrow?" would be classified as requiring clarification
because no patient was named.

**LC4R5 fix:** a resolved practitioner (`exact` or `corrected`) is now
sufficient read-only context for `explain_schedule`.  Patient identity is
only required when no practitioner is resolved.

## What was preserved

- Clarification for ambiguous practitioner wording (`some doctor`, `a doctor`)
  remains unchanged.
- Clarification for omitted practitioner *and* omitted patient remains
  unchanged.
- Patient-specific explanation behaviour (e.g. "Can you explain Margaret
  Thompson's schedule?") is unchanged.
- Generic `calendar`/`schedule`/`availability` wording is not promoted to
  `explain_schedule`.
- Safety, negation, reversal, time extraction, lossless normalization, and
  oracle independence are unchanged.
- `_EXPLAIN_PATTERNS` is not broadened — the fix is only in the
  action-relevant clarification rule.

## Semantic baseline

| Dimension | Pre-LC4R5 | Post-LC4R5 | Expected |
|---|---|---|---|
| intended_action | 880/1152 | 880/1152 | 880/1152 |
| action_semantics | 730/1152 | 814/1152 | 814/1152 |
| temporal_relation | 628/1152 | 628/1152 | 628/1152 |
| normalized_values | 101/1152 | 101/1152 | 101/1152 |
| entity_semantics | 300/1152 | 300/1152 | 300/1152 |
| clarification | 698/1152 | 782/1152 | 782/1152 |
| safety | 1152/1152 | 1152/1152 | 1152/1152 |

## Frozen selection verification

- Repair target: 84/84 (`b69abbcbc6febe29`)
- Preserve clarification: 12/12 (`34c95db64c716f56`)

## Files owned

- `app/services/bernie/semantic_extraction.py` — one-line rule addition
- `tests/test_bernie_semantic_extraction.py` — 19 new focused tests
- `scripts/bernie_lc4r5_report.py` — deterministic report/check
- `docs/bernie-lc4r5-report.json` — frozen evidence report
- `docs/bernie-lc4r5-implementation-note.md` — this note
- `orchestration/agent_inbox/codex/lc4r5-dw1-completion.md` — completion
  artifact
