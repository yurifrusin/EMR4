# Historical Diary Trove Ordered Neutral Event Export

Date: 2026-07-06
Sprint: H9 ordered local neutral snapshot event export
Scope: bounded local dense-day samples from ignored pilot folders only:
`local_data/historical-diary-trove/raw/pilot/` and
`local_data/historical-diary-trove/raw/pilot_01/`
Privacy posture: ordered neutral counts only; no filenames, raw paths, exact
source document timestamps, document text, patient labels, staff labels, or
visible diary content committed.

## What H9 Added

H9 extends the local structure classifier:

```text
scripts/historical_diary_structure_classifier.ps1
```

New opt-in flag:

```text
-IncludeOrderedSnapshots
```

When enabled, the ignored local output includes `ordered_neutral_snapshots`.
Each snapshot contains only count/signature fields plus a zero-based
`sequence_index`. The sequence index preserves the already-local processing
order without exposing filenames, paths, source timestamps, or document text.

H9 also extends:

```text
scripts/historical_diary_event_summary_dry_run.py
```

If ordered snapshots are present, the event-summary CLI uses them instead of
H8's grouped signature replay. This restores real adjacent neutral count deltas
while staying non-semantic and validator-gated.

## Local Outputs

Ignored H9 outputs:

```text
local_data/historical-diary-trove/inventory/ordered_snapshots_h9.json
local_data/historical-diary-trove/inventory/event_summary_h9.json
```

Both outputs passed:

```text
scripts/historical_diary_output_safety.py
```

## Local Result

### `pilot`

- Representative ordered snapshots: 40.
- Adjacent transitions: 39.
- Event classes: 21 `no_structural_change`, 18 `small_content_delta`.
- Character-count absolute delta range: 0-114.
- Paragraph-count absolute delta range: 0-3.
- Non-empty-line absolute delta range: 0-1.
- Time-like-token absolute delta range: 0-1.
- Date-like-token absolute delta range: 0-0.

### `pilot_01`

- Representative ordered snapshots: 40.
- Adjacent transitions: 39.
- Event classes: 32 `no_structural_change`, 7 `small_content_delta`.
- Character-count absolute delta range: 0-109.
- Paragraph-count absolute delta range: 0-7.
- Non-empty-line absolute delta range: 0-4.
- Time-like-token absolute delta range: 0-0.
- Date-like-token absolute delta range: 0-0.

## Interpretation

H9 improves on H8 because it uses ordered neutral snapshots rather than grouped
signature replay. The H9 pilot results show the dense-day samples remain
structurally stable and the observed adjacent changes are still small neutral
deltas.

H9 still does **not** infer appointment creation, deletion, patient arrival,
cancellation, wait-list changes, provider movement, or any other diary
semantics. It only proves that ordered, validator-safe neutral event summaries
can be generated locally.

## H10 Recommendation

Next sprint: **H10 Broad Ignored Ordered Export Guardrail**.

Recommended scope:

1. Add an explicit sample cap and root-count guard for larger ignored runs.
2. Add a local-only summary comparer for H8 grouped replay versus H9 ordered
   snapshot output.
3. Keep every generated file under ignored `local_data/`.
4. Do not process the full 58k-file trove until runtime, output size, Word COM
   stability, and PHI-safety checks are measured on a larger but still bounded
   subset.
