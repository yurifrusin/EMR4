# Historical Diary Trove Pilot Inventory

Date: 2026-07-06  
Scope: local pilot folders only:
`local_data/historical-diary-trove/raw/pilot/` and
`local_data/historical-diary-trove/raw/pilot_01/`
Privacy posture: metadata-only; no filenames, document text, document metadata
strings, patient details, or raw paths recorded.

## Summary

Yuri copied two pilot diary snapshot sets into ignored local trove directories.
The original set appears to be from a Sunday and is likely atypical; `pilot_01`
adds a larger comparison set that should better reflect busier diary churn.
Both pilots remain local/ignored.

Observed safe aggregates for the original `pilot` set:

- File count: 411 files.
- Expected from user recollection: about 414 files.
- Extension distribution: 411 `.doc` files.
- Total size: 60,631,014 bytes.
- Duplicate SHA-256 prefix count: 0.
- Size buckets:
  - 408 files between 100 KB and 1 MB.
  - 3 files between 1 byte and 10 KB.
  - 0 empty files.
- Binary signature buckets:
  - 408 files have the classic Word/OLE compound-document signature.
  - 3 `.doc` files have a different tiny-file signature and should be treated
    as possible ancillary/non-snapshot files until parser feasibility confirms
    their role.

Observed safe aggregates for `pilot_01`:

- File count: 584 files.
- Extension distribution: 584 `.doc` files.
- Total size: 79,252,804 bytes.
- Duplicate SHA-256 prefix count: 0.
- Size buckets:
  - 528 files between 100 KB and 1 MB.
  - 54 files between 10 KB and 100 KB.
  - 2 files between 1 byte and 10 KB.
  - 0 empty files.
- Binary signature buckets:
  - 582 files have the classic Word/OLE compound-document signature.
  - 2 `.doc` files have a different tiny-file signature and should be treated
    as possible ancillary/non-snapshot files until parser feasibility confirms
    their role.

## Timestamp Shape

Filesystem modified-time aggregates:

- Earliest modified timestamp: 2020-08-03T23:39:52Z.
- Latest modified timestamp: 2021-07-18T03:12:14.548Z.
- Median adjacent modified-time gap: 49 seconds.
- Adjacent gaps over 1 hour: 3.
- Adjacent gaps over 1 day: 3.

Files per modified UTC day for `pilot`:

| Modified UTC Day | Count |
|---|---:|
| 2020-08-03 | 1 |
| 2020-12-09 | 1 |
| 2021-06-17 | 1 |
| 2021-07-17 | 203 |
| 2021-07-18 | 205 |

Files per modified UTC day for `pilot_01`:

| Modified UTC Day | Count |
|---|---:|
| 2020-08-03 | 1 |
| 2020-12-09 | 1 |
| 2021-03-05 | 305 |
| 2021-03-06 | 277 |

Interpretation:

- The dense 2021-07-17/2021-07-18 clusters look consistent with a diary state
  sequence saved repeatedly during one operational period.
- The dense 2021-03-05/2021-03-06 `pilot_01` clusters show a higher-churn
  comparison sequence: 584 files with a 21-second median adjacent modified-time
  gap, compared with 411 files and a 49-second median gap in `pilot`.
- The sparse older timestamps and tiny non-OLE `.doc` signatures may be
  ancillary files, copied artifacts, or edge-case snapshots.
- Filesystem modified timestamps are not yet sufficient proof of diary chronology.
  H2 should test whether sequence order is recoverable from filenames, embedded
  OLE metadata, document content structure, or adjacent diff similarity.

## Local Artifacts

The detailed inventory JSON is intentionally ignored and local-only:

```text
local_data/historical-diary-trove/inventory/pilot_inventory.json
local_data/historical-diary-trove/inventory/pilot_01_inventory.json
```

The reusable inventory script is safe to commit:

```text
scripts/historical_diary_inventory.py
```

The script emits only aggregate metadata and non-reversible hash prefixes. It
does not print filenames, raw paths, document text, document metadata strings,
or PHI-bearing values.

## Safety Decisions

- Do not commit the raw pilot files.
- Do not print or commit filenames until reviewed for PHI.
- Do not extract document text in committed outputs.
- Do not send raw documents or extracted text to external LLM/provider tools.
- Keep H2 parser feasibility local-first and commit only structural findings.
- Use Ariadne-local tooling for raw-data inspection by default; involve external
  workers only on non-PHI summaries, parser code, or synthetic fixtures.

## H2 Recommendation

Next sprint: **H2 Parser Feasibility on Tiny Sample**.

Recommended scope:

1. Select 5-10 consecutive candidate snapshots locally from both `pilot` and
   `pilot_01` without exposing names.
2. Determine whether the 408 + 582 OLE `.doc` files can be parsed with available
   local tools.
3. Extract only structural diary-grid facts into ignored local JSON:
   timestamp/source-order candidate, visible diary date if safely recoverable,
   resource column count, appointment-block count, and coarse time-grid shape.
4. Avoid committing document text or patient/staff labels.
5. Produce a committed non-PHI feasibility summary and update the plan.

Potential tooling paths:

- OLE metadata inspection for old `.doc` containers.
- Local LibreOffice headless conversion to a temporary ignored format, if
  installed and safe.
- Local antiword/catdoc-style extraction only if output can be redacted before
  any committed artifact.
- Binary/structural diffing across adjacent files before text extraction.

H2 should not process the full 58k-file trove until parser and
de-identification boundaries are proven across both pilot sets.
