# Historical Diary Trove Broadened Neutral Sampling

Date: 2026-07-06
Sprint: H13 broadened neutral ordered-snapshot sampling
Scope: one capped dense day from each ignored pilot root, 100 snapshots per
root, no `-AllowLargeRun`
Privacy posture: ignored local neutral outputs only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
or visible diary content committed.

## Purpose

H13 checks whether the H12 large-delta finding remains isolated when the
ordered neutral sample is widened to the current H10 cap of 100 files per root.
It keeps the same raw-free, read-only posture and avoids semantic appointment
labelling.

## Command Shape

The classifier was run with H10 guardrails still active:

```text
scripts/historical_diary_structure_classifier.ps1
```

Parameters:

```text
-SampleSize 100 -DenseDays 1 -IncludeOrderedSnapshots
```

Ignored outputs:

```text
local_data/historical-diary-trove/inventory/ordered_snapshots_h13.json
local_data/historical-diary-trove/inventory/event_summary_h13.json
local_data/historical-diary-trove/inventory/large_delta_triage_h13.json
```

Each output passed:

```text
scripts/historical_diary_output_safety.py
```

## Local Result

### `pilot`

- Sampled/opened: 100.
- Event transitions: 99.
- Event classes: 61 `no_structural_change`, 37 `small_content_delta`, 1
  `time_grid_delta`.
- Character-count absolute delta range: 0-214.
- Paragraph-count absolute delta range: 0-4.
- Non-empty-line absolute delta range: 0-4.
- Time-like-token absolute delta range: 0-5.
- Date-like-token absolute delta range: 0-0.
- Large-delta triage count: 0.

### `pilot_01`

- Sampled/opened: 100.
- Event transitions: 99.
- Event classes: 60 `no_structural_change`, 38 `small_content_delta`, 1
  `large_unexplained_delta`.
- Character-count absolute delta range: 0-547.
- Paragraph-count absolute delta range: 0-7.
- Non-empty-line absolute delta range: 0-6.
- Time-like-token absolute delta range: 0-2.
- Date-like-token absolute delta range: 0-1.
- Large-delta triage count: 1.

The `pilot_01` large transition is the same neutral sequence pair as H12:
sequence 54 to 55, with stable diary-grid structure and unchanged time-token
count.

## Interpretation

The widened capped sample did not reveal a new large unexplained transition.
The only large delta remains the H12 shape-stable content-volume movement. The
new `pilot` `time_grid_delta` is a neutral signal that the time-token count
moved by up to 5 in one adjacent transition; it should be treated as a future
local-only structural question, not a semantic appointment conclusion.

## Recommendation

Next sprint: add a neutral transition-triad or neighborhood reporter so future
large/time-grid events can be inspected in context using only adjacent sequence
indexes and count movement. Keep semantic labelling out of scope until the
privacy/de-identification path is explicitly reviewed.
