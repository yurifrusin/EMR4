# Historical Diary Trove Pilot Inventory

Date: 2026-07-06  
Scope: local pilot folder only, `local_data/historical-diary-trove/raw/pilot/`  
Privacy posture: metadata-only; no filenames, document text, document metadata
strings, patient details, or raw paths recorded.

## Summary

Yuri copied the original pilot diary snapshot set into the ignored local trove
directory. The H1 inventory confirms a usable pilot exists and should remain
local/ignored.

Observed safe aggregates:

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

## Timestamp Shape

Filesystem modified-time aggregates:

- Earliest modified timestamp: 2020-08-03T23:39:52Z.
- Latest modified timestamp: 2021-07-18T03:12:14.548Z.
- Median adjacent modified-time gap: 49 seconds.
- Adjacent gaps over 1 hour: 3.
- Adjacent gaps over 1 day: 3.

Files per modified UTC day:

| Modified UTC Day | Count |
|---|---:|
| 2020-08-03 | 1 |
| 2020-12-09 | 1 |
| 2021-06-17 | 1 |
| 2021-07-17 | 203 |
| 2021-07-18 | 205 |

Interpretation:

- The dense 2021-07-17/2021-07-18 clusters look consistent with a diary state
  sequence saved repeatedly during one operational period.
- The three sparse older timestamps and three tiny non-OLE `.doc` signatures may
  be ancillary files, copied artifacts, or edge-case snapshots.
- Filesystem modified timestamps are not yet sufficient proof of diary chronology.
  H2 should test whether sequence order is recoverable from filenames, embedded
  OLE metadata, document content structure, or adjacent diff similarity.

## Local Artifacts

The detailed inventory JSON is intentionally ignored and local-only:

```text
local_data/historical-diary-trove/inventory/pilot_inventory.json
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

1. Select 5-10 consecutive candidate snapshots locally without exposing names.
2. Determine whether the 408 OLE `.doc` files can be parsed with available local
   tools.
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

H2 should not process the full 58k-file trove until the pilot parser and
de-identification boundary are proven.
