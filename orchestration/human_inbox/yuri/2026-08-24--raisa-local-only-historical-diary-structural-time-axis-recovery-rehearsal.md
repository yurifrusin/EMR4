# Yuri update — historical Diary structural time-axis recovery rehearsal

Date: 2026-08-24

Timestamp: 2026-08-24T04:33:07.7001882+10:00 (Australia/Brisbane)

Yuri attention required: **no**.

## Lay summary

The local parser now sees much more of the Diary's minute-by-minute movement:
80 snapshots produced 448 changes without exposing private information. The
experiment also answered the important structural question—it found no time
labels inside the appointment table cells, so repeating that method would be
wasteful. The one run has been consumed and cleaned up.

The first-use gate now exists at the point where it becomes useful. It will be
checked before any historical-derived scenario becomes a reusable Raisa test,
but it does not slow ordinary authored-synthetic work or private local
measurement. It is still closed because no such scenario has been created.

## Technical summary

- reviewed source: `3bcf2302461874e54d372cf5a71860a495fa7b20`;
- Phase A: one passing metadata bind, 80 files, 8,151,040 bytes, zero content
  reads before admission;
- Phase B: one run, 80/80 parsed, 12,557 segments, 199 stable records, 448
  changes, zero explicit anchors and zero mapped times;
- privacy: zero leakage; no manifest, private projection, key, mapping or raw
  coordinate retained; no provider/model call;
- verification: 44 focused plus 101 unchanged provider-free controls pass;
- decision: `revision_required`, with no retry; and
- protected local/origin `master` and `handoff/current` remain fixed at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Deliberately closed

No historical-derived fixture, scenario, replay, corpus, memory/RAG, product
runtime, database, ordinary-practice activation, provider/model use,
production, deployment, release, Pages or protected-ref movement is opened.

## Place in Raisa and next work

The trove continues to look valuable for realistic reception-flow development,
and the remaining obstacle is now sharply located. The next tranche will read
only explicit time labels from the Word document's main story and map them to
table entries by bounded same-page rendered coordinates. It remains
synthetic-first and may make at most one fresh local content run.
