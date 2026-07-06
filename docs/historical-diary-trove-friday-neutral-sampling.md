# Historical Diary Trove Friday Neutral Sampling

Date: 2026-07-06
Sprint: H16 Friday neutral ordered-snapshot sampling
Scope: one capped dense-day sample from ignored `pilot_02`, 100 snapshots from
667 local files, no `-AllowLargeRun`
Privacy posture: ignored local neutral outputs only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
or visible diary content committed.

## Purpose

H16 adds a more representative weekday stress slice after the first Sunday pilot
and the broader comparison pilot. It keeps the H10 cap active and stays
strictly neutral: structural counts and transition classes only, no appointment
semantics.

## Command Shape

The classifier was run against:

```text
local_data/historical-diary-trove/raw/pilot_02/
```

Parameters:

```text
-SampleSize 100 -DenseDays 1 -IncludeOrderedSnapshots
```

Ignored outputs:

```text
local_data/historical-diary-trove/inventory/ordered_snapshots_h16.json
local_data/historical-diary-trove/inventory/event_summary_h16.json
local_data/historical-diary-trove/inventory/large_delta_triage_h16.json
local_data/historical-diary-trove/inventory/transition_neighborhoods_h16.json
```

Each output passed:

```text
scripts/historical_diary_output_safety.py
```

## Local Result

### `pilot_02`

- Local files present: 667.
- Dense candidates selected by the classifier: 437.
- Sampled/opened: 100.
- Read errors: 0.
- Structure class: 100 `strong_diary_grid`.
- Event transitions: 99.
- Event classes: 65 `no_structural_change`, 34 `small_content_delta`.
- Character-count absolute delta range: 0-161.
- Paragraph-count absolute delta range: 0-7.
- Non-empty-line absolute delta range: 0-4.
- Time-like-token absolute delta range: 0-2.
- Date-like-token absolute delta range: 0-1.
- Large-delta triage count: 0.
- Transition-neighborhood count: 0.

## Comparison

- `pilot`: 100 snapshots produced one neutral `time_grid_delta` and no large
  unexplained deltas.
- `pilot_01`: 100 snapshots produced one isolated `large_unexplained_delta`,
  already triaged as a shape-stable content-volume movement.
- `pilot_02`: 100 snapshots produced no large or time-grid notable
  transitions.

The Friday sample therefore strengthens the working hypothesis that the trove
contains a stable diary-grid signal with mostly small adjacent movements. The
notable H12/H14 events remain isolated exceptions rather than the normal shape
of the data.

## Bernie Memory Implication

The 58k-file trove is promising, but not as raw fine-tuning material. The safe
sequence should be:

1. Keep the deterministic diary state machine as the source of truth.
2. Build a neutral transition graph from validator-safe aggregate outputs.
3. Add semantic labels only after the H15 de-identification gate is explicitly
   approved.
4. Use approved, de-identified, synthetic or derived examples for Bernie
   prompt/evaluation fixtures.
5. Consider RAG or GraphRAG over the derived graph before any fine-tuning.

Fine-tuning may become useful later for language style, receptionist phrasing,
clarification wording, and intent paraphrase robustness. It should not train on
raw diary files, raw patient/staff names, visible diary text, or unreviewed
appointment semantics.

RAG is useful for read-only retrieval over approved examples, policy notes,
aggregate transition statistics, and schema/state-machine documentation.
GraphRAG is the more natural fit once the derived graph exists: nodes can
represent neutral slots, transition classes, relative sequence positions,
synthetic resource groups, and approved semantic fixture types; edges can
represent stable adjacency, co-occurrence, movement, resize, status, and
clarification patterns.

Bernie may use that graph to explain, clarify, or propose bounded actions, but
the backend diary transition system must still decide availability, collision
handling, mutation validity, evidence signing, audit, and final write authority.

## Recommendation

Next sprint: build a safe local cross-pilot comparison reporter that reads
validator-safe event summaries and produces a compact trend table across
`pilot`, `pilot_01`, and `pilot_02`. After that, start a neutral graph export
prototype that emits derived nodes/edges only, still without semantic labels.
