# Raisa local-only historical Diary structural time-axis recovery rehearsal — report

Date: 2026-08-24

Timestamp: 2026-08-24T04:33:07.7001882+10:00 (Australia/Brisbane)

Result: `raisa_local_only_historical_diary_table_cell_time_axis_revision_required`

Reviewed source: `3bcf2302461874e54d372cf5a71860a495fa7b20`

## Conclusion

The stricter paragraph mapper was useful but did not recover the clock. It
opened 80/80 bound snapshots once, split the fourteen legacy table cells into
12,557 structural segments, preserved 199 stable records and recovered 448
adjacent changes with zero source leakage. It found no complete time token in
those table-cell streams.

That negative result localises the remaining problem. Earlier committed
count-only evidence found 78 time-like tokens in the complete Word document;
the new run proves they are outside the table cells. The next mapper should
therefore bind explicit document-story time labels to table-cell segments using
same-page Word-rendered coordinates. It must not guess from row numbers,
opening hours or the known 10-minute mode.

## Privacy, cleanup and gating

- Source-value leakage: 0.
- Private manifest and projection retained: 0.
- Key, mapping or coordinate persistence: 0.
- Provider/model calls: 0.
- Word cleanup: passed; the pre-existing user Word process remained.
- Content runs: exactly 1; the terminal forbids retry.
- Reusable historical-derived artifacts: 0.

The default-deny first-use gate now exists at the useful boundary: it triggers
before any reusable historical-derived fixture, scenario, replay, corpus,
memory object or product test. It does not apply to authored-synthetic tests or
private aggregate measurement, and this result does not open it.

## Verification

Forty-four focused mapper/gate tests and 101 unchanged privacy/H5/H15 controls
pass through the provider-free runner, 145 total. Ruff, compilation,
PowerShell parsing, source-boundary scanning and Git diff checks also pass.
Five contained prepublication interface lapses are consolidated in register
revision 656; none changed the empirical run or reached publication.

## Next operation

Proceed to
`raisa-local-only-historical-diary-document-story-time-coordinate-recovery-rehearsal`.
It remains synthetic-first, may consume at most one newly bound local content
run and grants no downstream use even on success.
