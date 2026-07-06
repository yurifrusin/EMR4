# Historical Diary Trove Neutral Transition Neighborhoods

Date: 2026-07-06
Sprint: H14 neutral transition-neighborhood reporter
Scope: ignored H13 ordered neutral snapshot output only
Privacy posture: ignored local neutral outputs only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
or visible diary content committed.

## Purpose

H14 adds a local-only neutral neighborhood report for notable transitions. It
captures the target transition plus adjacent transitions using sequence indexes
and neutral count movement only. This gives context around large or time-grid
events without inspecting or exporting raw diary content.

Default target event classes:

- `large_unexplained_delta`
- `time_grid_delta`

Default radius:

- one adjacent transition before
- one adjacent transition after

## Tooling

New script:

```text
scripts/historical_diary_transition_neighborhoods.py
```

Input used for H14:

```text
local_data/historical-diary-trove/inventory/ordered_snapshots_h13.json
```

Ignored output:

```text
local_data/historical-diary-trove/inventory/transition_neighborhoods_h14.json
```

The output is validated with:

```text
scripts/historical_diary_output_safety.py
```

## Local Result

### `pilot`

One neighborhood was found:

- Center transition: 68, sequence 68 to 69.
- Event class: `time_grid_delta`.
- Center neutral deltas: character count 26, paragraph count 4, non-empty lines
  4, time-like tokens 5, date-like tokens 0.
- Previous neighbor: transition 67, `small_content_delta`, character count 13,
  no paragraph/line/time/date-token movement.
- Next neighbor: transition 69, `no_structural_change`, no neutral count
  movement.

Interpretation: the time-grid event is isolated in this sample and immediately
returns to no neutral movement in the next adjacent transition. This is still a
structural signal only, not an appointment semantic.

### `pilot_01`

One neighborhood was found:

- Center transition: 54, sequence 54 to 55.
- Event class: `large_unexplained_delta`.
- Center neutral deltas: character count 547, paragraph count 6, non-empty
  lines 6, time-like tokens 0, date-like tokens 1.
- Previous neighbor: transition 53, `small_content_delta`, character count 30,
  paragraph count 1, non-empty lines 1, no time/date-token movement.
- Next neighbor: transition 55, `small_content_delta`, character count 1,
  paragraph count 1, non-empty lines 1, no time/date-token movement.

Interpretation: the large transition remains the same H12/H13 shape-stable
content-volume movement. Its immediate neighbors are small content deltas, not
layout-shape or time-grid events.

## Recommendation

H14 gives us enough neutral tooling to inspect bounded samples without semantic
labelling. The next safe step is either:

1. broaden to another capped dense-day/root set and compare frequency of
   neighborhoods; or
2. design a de-identification review gate before any semantic appointment
   labelling is attempted.

Do not infer appointment create/delete/status semantics from H14.
