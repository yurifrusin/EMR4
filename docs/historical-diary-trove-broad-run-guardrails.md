# Historical Diary Trove Broad-Run Guardrails

Date: 2026-07-06
Sprint: H10 broad ignored ordered-export guardrail
Scope: safety controls before any larger historical diary trove processing
Privacy posture: guardrails and safe comparison tooling only; raw diary files
stay local and ignored.

## Guardrails Added

`scripts/historical_diary_structure_classifier.ps1` now refuses broad runs by
default:

- `MaxRootCount`: default 2.
- `MaxSampleSize`: default 100.
- `MaxDenseDays`: default 1.

The script fails before opening Word if any of those caps are exceeded. A caller
must explicitly pass `-AllowLargeRun` to bypass the caps, and that should only
happen after a documented safety/runtime review.

This means the full 58k-file trove cannot be processed accidentally by a casual
classifier invocation.

## Comparison Tooling Added

H10 added:

```text
scripts/historical_diary_event_summary_compare.py
```

The comparer accepts two H5-safe event summaries and writes an ignored
comparison payload:

```text
local_data/historical-diary-trove/inventory/event_summary_compare_h10.json
```

The comparison contains only:

- matched root count;
- per-root snapshot and transition count deltas;
- per-event-class count deltas.

It does not expose raw files, paths, timestamps, document text, patient labels,
staff labels, or diary content.

## Local H8/H9 Comparison

Comparing H8 grouped replay with H9 ordered neutral snapshots:

### `pilot`

- Snapshot count delta: 0.
- Transition count delta: 0.
- `no_structural_change`: -8.
- `small_content_delta`: +8.

### `pilot_01`

- Snapshot count delta: 0.
- Transition count delta: 0.
- `no_structural_change`: -1.
- `small_content_delta`: +1.

Interpretation: grouped replay under-counted small adjacent deltas compared
with ordered neutral snapshots, especially in `pilot`. H9 is therefore the
better basis for future neutral temporal work.

## H11 Recommendation

Next sprint: **H11 Bounded Multi-Day Runtime Probe**.

Recommended scope:

1. Keep `-AllowLargeRun` off.
2. Raise only `MaxDenseDays` or root selection deliberately for a small bounded
   probe if needed; keep `SampleSize` under the default cap.
3. Capture runtime, Word COM open/error counts, output size, and validator
   result in ignored local JSON.
4. Commit only safe aggregate documentation.
5. Still avoid real appointment semantics until neutral multi-day behaviour is
   stable and privacy-reviewed.
