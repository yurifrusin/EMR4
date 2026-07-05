# Historical Diary Trove Parser Feasibility

Date: 2026-07-06  
Sprint: H2 parser feasibility  
Scope: local ignored pilot folders only:
`local_data/historical-diary-trove/raw/pilot/` and
`local_data/historical-diary-trove/raw/pilot_01/`  
Privacy posture: structural binary probing only; no filenames, raw paths,
document text, document metadata strings, patient details, staff labels, or
visible diary content recorded.

## Tooling Available Locally

Checked local command-line and Python tooling:

- `soffice` / LibreOffice: not available.
- `antiword`: not available.
- `catdoc`: not available.
- `wvText`: not available.
- Python `olefile`: not available.
- Python `win32com` / `pythoncom`: not available.
- Python `docx`: available, but not useful for legacy binary `.doc`.

Because no safe local converter was available, H2 used a committed pure-Python
OLE compound-document probe instead of opening Word or extracting text.

## Probe Added

Safe committed probe:

```text
scripts/historical_diary_doc_probe.py
```

Local ignored output:

```text
local_data/historical-diary-trove/inventory/doc_probe_h2.json
```

The probe:

- reads only OLE container structure;
- selects dense modified-day candidates from each pilot;
- checks for expected Word binary streams;
- reads only the non-PHI `WordDocument` binary header magic/version fields;
- records aggregate stream presence and byte-size ranges;
- does not emit filenames, raw paths, text, metadata strings, or PHI-bearing
  values.

## Sample Policy

- Roots: both `pilot` and `pilot_01`.
- Dense modified days per root: 2.
- Sample size per root: 10 files.
- Ordering: filesystem modified time within dense-day candidates.

## Results

### `pilot`

- Total files in root: 411.
- Dense-day candidate files: 408.
- Sampled files: 10.
- Sampled OLE files: 10.
- Probe errors: 0.
- Word header magic: `eca5` in 10/10 files.
- Word `nFib`: `193` in 10/10 files.
- Required stream presence in 10/10 sampled files:
  - `WordDocument`
  - `1Table`
  - `Data`
  - summary-information streams
- Structural stream-size ranges:
  - `WordDocument`: 35,473-36,497 bytes.
  - `1Table`: 47,340-51,210 bytes.
  - `Data`: 11,986-12,168 bytes.

### `pilot_01`

- Total files in root: 584.
- Dense-day candidate files: 582.
- Sampled files: 10.
- Sampled OLE files: 10.
- Probe errors: 0.
- Word header magic: `eca5` in 10/10 files.
- Word `nFib`: `193` in 10/10 files.
- Required stream presence in 10/10 sampled files:
  - `WordDocument`
  - `1Table`
  - `Data`
  - summary-information streams
- Structural stream-size ranges:
  - `WordDocument`: 29,841-30,865 bytes.
  - `1Table`: 44,189-44,429 bytes.
  - `Data`: 9,449 bytes.

## Interpretation

H2 confirms both pilot sets are structurally feasible for local parser work:

- The dense samples are valid legacy Word/OLE compound documents.
- The expected `WordDocument`, `1Table`, and `Data` streams are present.
- The Word binary header is consistent across sampled files.
- The two pilot sets differ in stream-size profile, which supports the user's
  observation that the original Sunday set is likely atypical.

H2 does **not** yet prove that appointment blocks, visible diary dates, room
columns, or time-grid facts can be extracted safely. It proves the next local
parser step has a real structural substrate.

## Safety Boundary Confirmed

- No raw diary files were committed.
- No filenames were printed or committed.
- No document text was extracted.
- No document metadata strings were extracted.
- No external provider or LLM saw raw data.
- Detailed probe JSON stayed ignored under `local_data/`.

## H3 Recommendation

Next sprint: **H3 Local Text/Structure Extraction Spike**.

Recommended scope:

1. Keep work local-only and ignored for raw/intermediate outputs.
2. Choose 2-3 files from each pilot's dense-day sample without committing names.
3. Try one local extraction path at a time:
   - install or locate a local converter such as LibreOffice only if acceptable;
   - or implement a minimal Word binary piece-table extractor locally;
   - or use hidden/local Microsoft Word automation only if it can be run safely
     without committing text or leaking PHI.
4. Produce ignored local text/HTML only long enough to classify structural
   patterns, then delete or keep under ignored `local_data/`.
5. Commit only aggregate structural findings such as whether visible diary date,
   time labels, resource columns, and appointment-block counts appear recoverable.

Do not run H3 across the full 58k-file trove. Keep it to tiny pilot samples
until the de-identification boundary is formalised.
