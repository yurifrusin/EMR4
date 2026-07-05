# Historical Diary Trove Synthetic Timeline Event Model

Date: 2026-07-06
Sprint: H7 synthetic timeline event model
Scope: synthetic neutral timeline snapshots only
Privacy posture: no raw diary files, filenames, paths, exact timestamps,
document text, patient labels, staff labels, or visible diary content used.

## Model Added

Safe committed event model:

```text
scripts/historical_diary_timeline_events.py
```

The model classifies adjacent neutral snapshots into deliberately non-semantic
event classes:

- `no_structural_change`
- `small_content_delta`
- `layout_shape_change`
- `time_grid_delta`
- `large_unexplained_delta`

These names intentionally avoid claiming real-world appointment actions. They
are structural categories only.

## Tests Added

Synthetic-only tests:

```text
tests/test_historical_diary_timeline_events.py
```

The tests cover:

- no-change classification;
- small content/count deltas;
- layout-shape changes;
- time-grid token deltas;
- large unexplained deltas;
- event-summary generation that passes the H5 safety validator.

H7 also extends `scripts/historical_diary_output_safety.py` so neutral event
summary fields such as `event_model`, `event_class_distribution`,
`snapshot_count`, and `transition_count` are validator-approved.

## Why This Matters

H6 proved that adjacent neutral deltas exist over bounded real pilot samples.
H7 turns those safe delta shapes into a testable synthetic model before any
semantic interpretation is attempted.

This gives the project a safe ladder:

1. Raw historical documents stay local and ignored.
2. Local tools emit only neutral aggregate counts.
3. The H5 validator gates committed outputs.
4. H7 classifies only synthetic neutral snapshots.
5. Future raw-derived event work can compare against this model without
   exposing document content.

## H8 Dry Run

H8 added a local dry-run CLI:

```text
scripts/historical_diary_event_summary_dry_run.py
```

It consumes only an already-safe aggregate JSON payload, such as the ignored H6
`timeline_delta_h6.json`, expands grouped neutral signatures into
synthetic-like snapshots, and writes an ignored event summary:

```text
local_data/historical-diary-trove/inventory/event_summary_h8.json
```

The dry-run output is passed through the H5 validator before it is considered
usable.

Important limitation: H8 does **not** recover the real chronological sequence
of diary edits. The H6 aggregate groups identical neutral signatures, so H8's
transition counts describe a representative aggregate replay, not the exact
order in which the original diary changed.

Local H8 pilot result:

- `pilot`: 40 representative snapshots, 39 transitions, all classified as
  `no_structural_change` or `small_content_delta`.
- `pilot_01`: 40 representative snapshots, 39 transitions, all classified as
  `no_structural_change` or `small_content_delta`.
- Character deltas are intentionally zero in this dry run because per-signature
  character counts are not present in the H6 grouped aggregate.

## H9 Recommendation

Next sprint: **H9 Ordered Local Snapshot Event Export**.

Recommended scope:

1. Extend the local-only classifier to emit an ignored ordered neutral snapshot
   sequence with no filenames, paths, timestamps, labels, or text.
2. Run the H7 event model over that ordered sequence.
3. Validate the ignored output through H5.
4. Compare ordered results with H8's representative replay.
5. Still do not infer appointment creation/deletion/status semantics.
