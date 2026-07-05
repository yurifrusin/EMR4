# Historical Diary Trove Structure Classifier Prototype

Date: 2026-07-06
Sprint: H4 structure classifier prototype
Scope: tiny local samples from ignored pilot folders only:
`local_data/historical-diary-trove/raw/pilot/` and
`local_data/historical-diary-trove/raw/pilot_01/`
Privacy posture: local Microsoft Word COM read-only classification; no
filenames, raw paths, exact document timestamps, document text, patient details,
staff labels, or visible diary content committed.

## Classifier Added

Safe committed classifier:

```text
scripts/historical_diary_structure_classifier.ps1
```

Local ignored output:

```text
local_data/historical-diary-trove/inventory/structure_classifier_h4.json
```

The classifier emits only aggregate neutral layout facts:

- table count and cell count ranges;
- table-dimension signatures;
- paragraph and non-empty line count ranges;
- time-like/date-like token count ranges;
- inferred time-interval mode in minutes;
- neutral signature distributions built from counts only;
- adjacent snapshot delta ranges over neutral counts only.

It does not emit filenames, raw paths, exact document timestamps, document text,
metadata strings, patient names, staff labels, appointment text, or raw time
tokens.

## Sample Policy

- Roots: both `pilot` and `pilot_01`.
- Dense modified days per root: 1.
- Sample size per root: 8 files.
- Ordering: filesystem modified time within dense-day candidates.

## Results

### `pilot`

- Dense-day candidate files: 205.
- Sampled files: 8.
- Opened read-only through Word: 8.
- Probe errors: 0.
- Structure class: `strong_diary_grid` in 8/8.
- Table count range: 2-2.
- Table cell count range: 14-14.
- Table dimension signature: `1x11+1x3` in 8/8.
- Character count range: 4,829-4,874.
- Paragraph count range: 249-252.
- Non-empty paragraph count range: 183-184.
- Non-empty line count range: 180-181.
- Time-like token count range: 85-86.
- Unique time-like token count range: 39-39.
- Date-like token count range: 11-11.
- Inferred time-interval mode: 10 minutes in 8/8.
- Adjacent neutral deltas stayed small:
  - character-count absolute delta range: 0-43;
  - paragraph-count absolute delta range: 0-2;
  - non-empty-line absolute delta range: 0-1;
  - time-like-token absolute delta range: 0-1;
  - date-like-token absolute delta range: 0-0.

### `pilot_01`

- Dense-day candidate files: 305.
- Sampled files: 8.
- Opened read-only through Word: 8.
- Probe errors: 0.
- Structure class: `strong_diary_grid` in 8/8.
- Table count range: 2-2.
- Table cell count range: 14-14.
- Table dimension signature: `1x11+1x3` in 8/8.
- Character count range: 3,118-3,251.
- Paragraph count range: 232-238.
- Non-empty paragraph count range: 165-169.
- Non-empty line count range: 162-167.
- Time-like token count range: 78-78.
- Unique time-like token count range: 37-37.
- Date-like token count range: 13-13.
- Inferred time-interval mode: 10 minutes in 8/8.
- Adjacent neutral deltas stayed bounded:
  - character-count absolute delta range: 0-109;
  - paragraph-count absolute delta range: 0-5;
  - non-empty-line absolute delta range: 0-4;
  - time-like-token absolute delta range: 0-0;
  - date-like-token absolute delta range: 0-0.

## Interpretation

H4 proves that safe, non-PHI, count-only classification can identify a stable
diary-grid substrate in both pilot sets. The repeated `1x11+1x3` table
signature, stable two-table/fourteen-cell shape, high time-like token density,
and consistent ten-minute interval mode are enough to treat the source documents
as structurally classifiable without exposing their contents.

The adjacent neutral deltas are also promising: the documents appear to be
successive states of a stable diary layout where relatively small structural
count changes may correspond to edits, bookings, removals, or status changes.
H4 does **not** identify those event types yet; it only proves the neutral
structure signal exists.

## Safety Boundary Confirmed

- No raw diary files were committed.
- No filenames were printed or committed.
- No exact document timestamps were committed.
- No document text was committed.
- No document metadata strings were committed.
- No patient, staff, appointment, or visible diary labels were committed.
- No external provider or LLM saw raw data.
- Detailed aggregate JSON stayed ignored under `local_data/`.

## H5 Recommendation

Next sprint: **H5 De-Identification Contract and Redaction Harness**.

Recommended scope:

1. Formalise which fields are allowed in committed classifier outputs.
2. Add a testable redaction contract for local trove tooling.
3. Create synthetic fixture documents or synthetic classifier payloads for
   tests, rather than using raw diary files.
4. Add automated checks that fail if output contains raw paths, filenames,
   exact timestamps, text snippets, or likely patient/staff labels.
5. Only after H5 should we consider a broader local run over more days.
