# Historical Diary Trove Thursday Neutral Sampling

Date: 2026-07-06
Sprint: H21 Thursday neutral sampling and four-root graph refresh
Scope: validator-safe aggregate extraction from ignored local `pilot_03`
Privacy posture: ignored local outputs only; no filenames, raw paths, exact
source document timestamps, document text, patient labels, staff labels, visible
diary content, semantic appointment labels, or external-provider calls.

## Purpose

H21 adds one more ordinary-day sample to test whether the H-series findings
generalise beyond the original Sunday, comparison, and Friday pilot roots. Yuri
provided `pilot_03`, understood to be a Thursday in May.

This sprint intentionally stays neutral. It refreshes the aggregate pipeline
across all four pilot roots, but does not perform semantic labelling or inspect
appointment meaning.

## Local Inputs

Ignored raw local root:

```text
local_data/historical-diary-trove/raw/pilot_03/
```

Local file count:

```text
637 files
```

## Commands

The four-root classifier exceeds the default H10 guardrail of two roots, so H21
used the explicit large-run override while retaining the same caps:

```text
.\scripts\historical_diary_structure_classifier.ps1 -Root @('local_data\historical-diary-trove\raw\pilot','local_data\historical-diary-trove\raw\pilot_01','local_data\historical-diary-trove\raw\pilot_02','local_data\historical-diary-trove\raw\pilot_03') -Output local_data\historical-diary-trove\inventory\ordered_snapshots_h21.json -SampleSize 40 -DenseDays 1 -IncludeOrderedSnapshots -AllowLargeRun
```

Derived outputs:

```text
local_data/historical-diary-trove/inventory/event_summary_h21.json
local_data/historical-diary-trove/inventory/cross_pilot_event_trends_h21.json
local_data/historical-diary-trove/inventory/neutral_derived_graph_h21.json
local_data/historical-diary-trove/inventory/neutral_graph_report_h21.json
```

All outputs above are ignored local artifacts and passed
`scripts/historical_diary_output_safety.py`.

## Local Result

The refreshed capped run sampled 40 snapshots from each of four roots, for 160
snapshots and 156 adjacent transitions.

| Root | Snapshots | Transitions | Neutral event classes |
|---|---:|---:|---|
| `pilot` | 40 | 39 | 21 `no_structural_change`, 18 `small_content_delta` |
| `pilot_01` | 40 | 39 | 32 `no_structural_change`, 7 `small_content_delta` |
| `pilot_02` | 40 | 39 | 32 `no_structural_change`, 7 `small_content_delta` |
| `pilot_03` | 40 | 39 | 17 `no_structural_change`, 22 `small_content_delta` |

`pilot_03` is more active than `pilot_01` and `pilot_02` in this capped slice,
but remains entirely inside the neutral `small_content_delta` envelope.

## Graph Refresh

The refreshed H21 graph has:

| Metric | Value |
|---|---:|
| Root nodes | 4 |
| Total nodes | 14 |
| Total edges | 28 |
| Represented transitions | 156 |

The predefined report emitted no roots for `large_unexplained_delta` or
`time_grid_delta` in this recomputed four-root capped slice.

Delta buckets remain useful for safe aggregate comparison:

| Query | Roots |
|---|---|
| `char_count_abs_delta_range:large` | `pilot`, `pilot_01`, `pilot_02`, `pilot_03` |
| `date_like_token_count_abs_delta_range:none` | `pilot`, `pilot_01` |
| `date_like_token_count_abs_delta_range:tiny` | `pilot_02`, `pilot_03` |
| `non_empty_line_count_abs_delta_range:small` | `pilot_01`, `pilot_02` |
| `non_empty_line_count_abs_delta_range:tiny` | `pilot`, `pilot_03` |
| `paragraph_count_abs_delta_range:small` | `pilot`, `pilot_01`, `pilot_02`, `pilot_03` |
| `time_like_token_count_abs_delta_range:none` | `pilot_01`, `pilot_03` |
| `time_like_token_count_abs_delta_range:tiny` | `pilot`, `pilot_02` |

## Interpretation

The Thursday sample strengthens the case that the trove is useful for building
safe deterministic diary scenarios. Even when the day is more active, the
neutral transitions mostly describe small structural/count movement around a
stable diary grid.

The difference between H20 and H21 should not be overread. H20 reported over
the existing three-root H19 graph; H21 recomputed all four roots with the same
40-snapshot cap. The useful conclusion is that the pipeline can safely compare
ordinary-day movement profiles without exposing raw diary content.

## Recommendation

Pause H-series sampling unless Yuri wants to add a deliberately unusual day
later. The next higher-value sprint is to convert these neutral movement
profiles into deterministic diary/Bernie regression scenarios, while keeping
semantic labelling blocked behind the H15 gate.
