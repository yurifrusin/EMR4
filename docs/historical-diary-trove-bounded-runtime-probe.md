# Historical Diary Trove Bounded Multi-Day Runtime Probe

Date: 2026-07-06
Sprint: H11 bounded multi-day runtime probe
Scope: two dense local days from ignored pilot folders, capped at 80 files per
root
Privacy posture: ignored local neutral outputs only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
or visible diary content committed.

## Probe Command Shape

H11 used the guarded classifier without `-AllowLargeRun`:

```text
scripts/historical_diary_structure_classifier.ps1
```

The run explicitly raised only the dense-day cap for this bounded probe:

```text
-SampleSize 80 -DenseDays 2 -MaxDenseDays 2 -IncludeOrderedSnapshots
```

All generated outputs stayed ignored under:

```text
local_data/historical-diary-trove/inventory/
```

## Safe Local Outputs

Ignored outputs:

```text
ordered_snapshots_h11.json
runtime_report_h11.json
event_summary_h11.json
```

Each output passed:

```text
scripts/historical_diary_output_safety.py
```

## Runtime Result

- Elapsed runtime: 112.224 seconds.
- Output byte count: 323,755 bytes for the ordered neutral snapshot file.
- Root count: 2.
- Total sampled: 160.
- Total opened read-only through Word COM: 160.
- Total errors: 0.

### `pilot`

- Dense candidates across two selected dense days: 408.
- Sampled: 80.
- Opened: 80.
- Errors: 0.
- Event summary: 80 snapshots, 79 transitions.
- Event classes: 40 `no_structural_change`, 39 `small_content_delta`.
- Character-count absolute delta range: 0-126.
- Paragraph-count absolute delta range: 0-5.
- Non-empty-line absolute delta range: 0-2.
- Time-like-token absolute delta range: 0-2.
- Date-like-token absolute delta range: 0-0.

### `pilot_01`

- Dense candidates across two selected dense days: 582.
- Sampled: 80.
- Opened: 80.
- Errors: 0.
- Event summary: 80 snapshots, 79 transitions.
- Event classes: 50 `no_structural_change`, 28 `small_content_delta`, 1
  `large_unexplained_delta`.
- Character-count absolute delta range: 0-547.
- Paragraph-count absolute delta range: 0-7.
- Non-empty-line absolute delta range: 0-6.
- Time-like-token absolute delta range: 0-1.
- Date-like-token absolute delta range: 0-1.

## Interpretation

H11 shows the local Word COM extraction path remains stable over a larger
bounded sample: 160/160 documents opened read-only with zero errors, and the
validator accepted all neutral outputs.

The one `large_unexplained_delta` in `pilot_01` is still a neutral count event,
not evidence of a specific appointment action. It should be treated as a prompt
for future local-only structural investigation, not as a semantic conclusion.

## H12 Recommendation

Next sprint: **H12 Neutral Large-Delta Local Triage**.

Recommended scope:

1. Add a local-only large-delta triage report that records only sequence index
   pairs and neutral before/after counts.
2. Keep filenames, paths, source timestamps, labels, and text out of output.
3. Validate the triage report through H5 before documenting aggregate findings.
4. Do not infer appointment semantics unless a later privacy-reviewed
   de-identification path can safely support that.
