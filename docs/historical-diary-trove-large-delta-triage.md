# Historical Diary Trove Neutral Large-Delta Triage

Date: 2026-07-06
Sprint: H12 neutral large-delta local triage
Scope: ignored H11 ordered neutral snapshot output only
Privacy posture: ignored local neutral output only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
or visible diary content committed.

## Purpose

H12 turns the single H11 `large_unexplained_delta` into a small local-only
triage report. The goal is to inspect why the neutral classifier called the
transition large without exposing raw diary content or implying appointment
semantics.

The report is deliberately limited to:

- root labels
- adjacent sequence indexes
- neutral before/after counts
- neutral adjacent delta ranges
- event class

It does not include raw diary files, filenames, paths, exact source timestamps,
document text, patient/staff labels, or semantic labels for appointments.

## Tooling

New script:

```text
scripts/historical_diary_large_delta_triage.py
```

Input:

```text
local_data/historical-diary-trove/inventory/ordered_snapshots_h11.json
```

Ignored output:

```text
local_data/historical-diary-trove/inventory/large_delta_triage_h12.json
```

The output is validated with:

```text
scripts/historical_diary_output_safety.py
```

## Local Finding

H12 found one large neutral transition:

- Root: `pilot_01`.
- Transition index: 54.
- Sequence pair: 54 to 55.
- Event class: `large_unexplained_delta`.
- Structure class stayed `strong_diary_grid`.
- Table count stayed `2`.
- Table cell count stayed `14`.
- Table dimension signature stayed `1x11+1x3`.
- Time-like token count stayed `78`.

Neutral before/after count movement:

| Count | Before | After | Absolute delta |
|---|---:|---:|---:|
| Character count | 3142 | 3689 | 547 |
| Paragraph count | 231 | 237 | 6 |
| Non-empty line count | 161 | 167 | 6 |
| Time-like token count | 78 | 78 | 0 |
| Date-like token count | 13 | 14 | 1 |

## Interpretation

The transition is large only because the character-count movement crossed the
current `>500` threshold. The diary grid shape did not change, the time-token
count did not change, and the paragraph/line/date-token movement stayed small.

This is best treated as a content-volume change inside the same diary shape,
not as evidence of a template/layout break and not as a semantic appointment
event.

## Recommendation

Use H12 as the local triage pattern for future larger runs:

1. Keep large-delta inspection neutral and validator-gated.
2. Treat shape-stable large character deltas as prompts for local review, not
   semantic labels.
3. Broaden only after runtime and privacy posture stay stable on larger bounded
   samples.
4. Consider a later semantic-labelling sprint only after a de-identification
   design is explicitly reviewed.
