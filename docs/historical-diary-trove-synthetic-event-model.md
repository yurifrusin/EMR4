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

## H8 Recommendation

Next sprint: **H8 Local Event Summary Dry Run**.

Recommended scope:

1. Convert the ignored H6 aggregate JSON into neutral synthetic-like snapshots
   in memory only.
2. Produce an ignored event-summary JSON.
3. Validate the event summary through H5.
4. Commit only safe aggregate findings if the event summary remains useful.
5. Do not infer appointment creation/deletion/status semantics yet.
