# Historical Diary Trove Cross-Pilot Event Trends

Date: 2026-07-06
Sprint: H17 safe cross-pilot event trend reporter
Scope: validator-safe event summaries from `pilot`, `pilot_01`, and `pilot_02`
Privacy posture: ignored local neutral outputs only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
or visible diary content committed.

## Purpose

H17 turns the H13 and H16 event summaries into one compact cross-pilot trend
table. This gives Bernie-memory planning a stable non-PHI substrate without
requiring raw diary content or semantic appointment labels.

## Tooling

Added:

```text
scripts/historical_diary_cross_pilot_event_trends.py
tests/test_historical_diary_cross_pilot_event_trends.py
```

The reporter accepts one or more validator-safe event summary JSON files,
rejects duplicate root labels, sorts roots deterministically, and emits a
validator-safe trend table.

Ignored output:

```text
local_data/historical-diary-trove/inventory/cross_pilot_event_trends_h17.json
```

## Local Result

The H17 run compared 300 sampled snapshots and 297 adjacent transitions across
three pilot roots.

### Event Class Counts

| Root | Snapshots | Transitions | No structural change | Small content delta | Time-grid delta | Large unexplained delta |
|---|---:|---:|---:|---:|---:|---:|
| `pilot` | 100 | 99 | 61 | 37 | 1 | 0 |
| `pilot_01` | 100 | 99 | 60 | 38 | 0 | 1 |
| `pilot_02` | 100 | 99 | 65 | 34 | 0 | 0 |

### Maximum Adjacent Neutral Deltas

| Root | Char | Paragraph | Non-empty line | Time-like token | Date-like token |
|---|---:|---:|---:|---:|---:|
| `pilot` | 214 | 4 | 4 | 5 | 0 |
| `pilot_01` | 547 | 7 | 6 | 2 | 1 |
| `pilot_02` | 161 | 7 | 4 | 2 | 1 |

## Interpretation

Across the current safe pilots, 295 of 297 adjacent transitions are either
`no_structural_change` or `small_content_delta`. The only notable transitions
remain one `time_grid_delta` in `pilot` and one `large_unexplained_delta` in
`pilot_01`; H14 showed both are isolated in their immediate neutral
neighborhoods.

This supports using the trove as a deterministic replay and graph-mining asset.
It does not yet justify semantic appointment labels, provider-visible examples,
or fine-tuning.

## Recommendation

Next sprint: prototype a neutral derived graph export from validator-safe event
trend data. It should emit only derived nodes and edges such as root, sequence,
event class, aggregate delta bucket, and adjacency. Keep semantic labels blocked
until the H15 gate is explicitly approved.
