# Historical Diary Trove Neutral Graph Report

Date: 2026-07-06
Sprint: H20 safe predefined graph report helper
Scope: validator-safe reports from ignored H19 neutral graph output
Privacy posture: ignored local report output only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
visible diary content, semantic appointment labels, or free-form graph search.

## Purpose

H20 tests whether the neutral graph is useful before making it more complex.
Instead of adding natural-language graph search, it adds a small predefined
report helper with fixed query IDs and validator-safe output.

## Tooling

Added:

```text
scripts/historical_diary_neutral_graph_report.py
tests/test_historical_diary_neutral_graph_report.py
```

Updated:

```text
scripts/historical_diary_output_safety.py
```

Ignored output:

```text
local_data/historical-diary-trove/inventory/neutral_graph_report_h20.json
```

## Report Shape

The report emits two query families:

- `roots_by_notable_event_class`
- `roots_by_delta_bucket`

It does not accept arbitrary query text. This keeps the report deterministic,
repeatable, and safe for future automation.

## Local Result

The H20 report over the H19 graph produced 9 query result groups:

| Query | Result |
|---|---|
| `large_unexplained_delta` | `pilot_01` |
| `time_grid_delta` | `pilot` |
| `char_count_abs_delta_range:large` | `pilot`, `pilot_01`, `pilot_02` |
| `date_like_token_count_abs_delta_range:none` | `pilot` |
| `date_like_token_count_abs_delta_range:tiny` | `pilot_01`, `pilot_02` |
| `non_empty_line_count_abs_delta_range:small` | `pilot`, `pilot_01`, `pilot_02` |
| `paragraph_count_abs_delta_range:small` | `pilot`, `pilot_01`, `pilot_02` |
| `time_like_token_count_abs_delta_range:small` | `pilot` |
| `time_like_token_count_abs_delta_range:tiny` | `pilot_01`, `pilot_02` |

## Interpretation

The graph is already useful for safe aggregate questions. It can identify which
sample roots contain the isolated notable event classes and which roots share
movement buckets, without exposing any raw diary content.

This is still not Bernie runtime memory. It remains a local, ignored,
aggregate-only research artifact. A future Bernie integration would need a
separate privacy/security sprint, a read-only retrieval boundary, and explicit
prompt-consumption gates.

## Recommendation

Next sprint: broaden the graph/report helper across another capped neutral
sample only if more local pilot roots are ready. If not, pause the H-series at
this safe GraphRAG runway and return to diary/Bernie deterministic sprint work.
