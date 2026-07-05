# Historical Diary Trove Local Extraction Spike

Date: 2026-07-06
Sprint: H3 local text/structure extraction spike
Scope: tiny local samples from ignored pilot folders only:
`local_data/historical-diary-trove/raw/pilot/` and
`local_data/historical-diary-trove/raw/pilot_01/`
Privacy posture: local Microsoft Word COM read-only extraction; no filenames,
raw paths, document text, metadata strings, patient details, staff labels, or
visible diary content committed.

## Tooling Decision

H2 found no local command-line `.doc` converter, but H3 confirmed Microsoft Word
COM is available locally:

- Word COM available: yes.
- Word version: `16.0`.
- Macro security: forced disabled before opening documents.
- Documents opened read-only.
- Word UI hidden and alerts disabled.
- Output written only to ignored `local_data/`.

This avoids installing a new system converter and avoids sending PHI-bearing
documents to any external provider.

## Probe Added

Safe committed probe:

```text
scripts/historical_diary_word_extract_probe.ps1
```

Local ignored output:

```text
local_data/historical-diary-trove/inventory/word_extract_probe_h3.json
```

The probe:

- selects dense modified-day candidate files from each pilot;
- opens only a tiny sample via local Word automation;
- records aggregate structural ranges;
- records whether time-like and date-like tokens are present as counts only;
- does not emit filenames, raw paths, text, metadata strings, or PHI-bearing
  values.

## Sample Policy

- Roots: both `pilot` and `pilot_01`.
- Dense modified days per root: 1.
- Sample size per root: 5 files.
- Ordering: filesystem modified time within dense-day candidates.

## Results

### `pilot`

- Dense-day candidate files: 205.
- Sampled files: 5.
- Opened read-only through Word: 5.
- Probe errors: 0.
- Character count range: 4,862-4,874.
- Paragraph count range: 252-252.
- Non-empty paragraph count range: 184-184.
- Non-empty line count range: 181-181.
- Table count range: 2-2.
- Table cell count range: 14-14.
- Time-like token count range: 86-86.
- Date-like token count range: 11-11.
- Tab count range: 0-0.

### `pilot_01`

- Dense-day candidate files: 305.
- Sampled files: 5.
- Opened read-only through Word: 5.
- Probe errors: 0.
- Character count range: 3,214-3,251.
- Paragraph count range: 235-238.
- Non-empty paragraph count range: 168-169.
- Non-empty line count range: 166-167.
- Table count range: 2-2.
- Table cell count range: 14-14.
- Time-like token count range: 78-78.
- Date-like token count range: 13-13.
- Tab count range: 0-0.

## Interpretation

H3 proves the pilot `.doc` files are not merely structurally valid Word/OLE
containers; they can be locally opened and interrogated as Word documents.

The repeated table counts, table-cell counts, dense paragraph/line counts, and
stable time-like token counts strongly suggest recoverable diary-grid structure.
The two pilot sets have different size/paragraph profiles, reinforcing that the
original Sunday pilot is probably atypical while still structurally useful.

H3 still does **not** commit or expose the actual diary text. It also does not
yet prove appointment identity, provider labels, visible room names, or state
transitions can be de-identified correctly. That boundary should be proven
before the full 58k-file trove is processed.

## Safety Boundary Confirmed

- No raw diary files were committed.
- No filenames were printed or committed.
- No document text was committed.
- No document metadata strings were committed.
- No external provider or LLM saw raw data.
- Detailed aggregate JSON stayed ignored under `local_data/`.

## H4 Recommendation

Next sprint: **H4 Diary Structure Classifier Prototype**.

Recommended scope:

1. Keep processing local-only and ignored.
2. Use Word COM to extract a tiny sample into memory only.
3. Build a classifier that emits neutral layout facts such as counts of tables,
   rows, time-label density, inferred grid regularity, and snapshot-to-snapshot
   structural deltas.
4. Do not emit patient names, staff labels, appointment text, filenames, raw
   paths, or exact document timestamps.
5. Commit only classifier code plus non-PHI aggregate findings.

Do not process the full 58k-file trove until a de-identification contract and
redaction test harness exist.
