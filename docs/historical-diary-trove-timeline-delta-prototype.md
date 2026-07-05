# Historical Diary Trove Safe Timeline Delta Prototype

Date: 2026-07-06
Sprint: H6 safe local timeline delta prototype
Scope: bounded local dense-day samples from ignored pilot folders only:
`local_data/historical-diary-trove/raw/pilot/` and
`local_data/historical-diary-trove/raw/pilot_01/`
Privacy posture: aggregate-only timeline classification; no filenames, raw
paths, exact document timestamps, document text, patient details, staff labels,
or visible diary content committed.

## Method

H6 reused the H4 local classifier:

```text
scripts/historical_diary_structure_classifier.ps1
```

Bounded local output:

```text
local_data/historical-diary-trove/inventory/timeline_delta_h6.json
```

The output was validated through the H5 safety gate:

```text
scripts/historical_diary_output_safety.py
```

The bounded run classified 40 dense-day documents from each pilot. This is still
well below full-trove processing and is intended only to test whether
successive-state signals remain useful after the de-identification contract is
applied.

## Results

### `pilot`

- Dense-day candidate files: 205.
- Sampled files: 40.
- Opened read-only through Word: 40.
- Probe errors: 0.
- Structure class: `strong_diary_grid` in 40/40.
- Table dimension signature: `1x11+1x3` in 40/40.
- Table count range: 2-2.
- Table cell count range: 14-14.
- Character count range: 4,829-5,037.
- Paragraph count range: 249-255.
- Non-empty paragraph count range: 183-188.
- Non-empty line count range: 180-185.
- Time-like token count range: 85-86.
- Unique time-like token count range: 39-39.
- Date-like token count range: 11-11.
- Inferred time-interval mode: 10 minutes in 40/40.
- Adjacent neutral deltas:
  - character-count absolute delta range: 0-114;
  - paragraph-count absolute delta range: 0-3;
  - non-empty-line absolute delta range: 0-1;
  - time-like-token absolute delta range: 0-1;
  - date-like-token absolute delta range: 0-0.

### `pilot_01`

- Dense-day candidate files: 305.
- Sampled files: 40.
- Opened read-only through Word: 40.
- Probe errors: 0.
- Structure class: `strong_diary_grid` in 40/40.
- Table dimension signature: `1x11+1x3` in 40/40.
- Table count range: 2-2.
- Table cell count range: 14-14.
- Character count range: 3,066-3,251.
- Paragraph count range: 225-238.
- Non-empty paragraph count range: 162-169.
- Non-empty line count range: 158-167.
- Time-like token count range: 78-78.
- Unique time-like token count range: 37-37.
- Date-like token count range: 13-13.
- Inferred time-interval mode: 10 minutes in 40/40.
- Adjacent neutral deltas:
  - character-count absolute delta range: 0-109;
  - paragraph-count absolute delta range: 0-7;
  - non-empty-line absolute delta range: 0-4;
  - time-like-token absolute delta range: 0-0;
  - date-like-token absolute delta range: 0-0.

## Interpretation

H6 shows that the neutral structure signal remains stable over a larger bounded
window. Both pilots retain the same diary-grid shape, the same inferred
10-minute interval mode, and small adjacent neutral deltas without exposing
content.

The larger sample suggests the historical trove can support a future local
timeline model that detects state changes by count/signature deltas. H6 does
not yet infer appointment events, identities, statuses, or semantic causes. It
only proves that validator-approved aggregate deltas survive beyond tiny
samples.

## Safety Boundary Confirmed

- The H6 aggregate JSON passed `scripts/historical_diary_output_safety.py`.
- No raw diary files were committed.
- No filenames were printed or committed.
- No exact document timestamps were committed.
- No document text was committed.
- No document metadata strings were committed.
- No patient, staff, appointment, or visible diary labels were committed.
- No external provider or LLM saw raw data.
- Detailed aggregate JSON stayed ignored under `local_data/`.

## H7 Recommendation

Next sprint: **H7 Synthetic Timeline Event Model**.

Recommended scope:

1. Create synthetic neutral timeline payloads that mimic H6 signature/delta
   shapes without using raw diary files.
2. Build event-classification tests over synthetic data only, such as
   `no_structural_change`, `small_content_delta`, `layout_shape_change`, and
   `large_unexplained_delta`.
3. Keep event labels deliberately neutral until raw-content de-identification is
   proven.
4. Use the H5 validator on all committed fixtures and generated summaries.
5. Do not process the full 58k-file trove until H7 proves the synthetic event
   model is useful and safe.
