# Historical Diary Trove Neutral Graph Delta Buckets

Date: 2026-07-06
Sprint: H19 neutral graph delta-bucket enrichment
Scope: validator-safe graph enrichment from H17 cross-pilot event trends
Privacy posture: ignored local graph output only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
visible diary content, or semantic appointment labels committed.

## Purpose

H19 extends the H18 neutral graph so it captures not only event-class counts,
but also aggregate movement magnitude. This gives future GraphRAG a way to ask
about the shape of structural movement without needing raw diary content.

## Tooling

Updated:

```text
scripts/historical_diary_neutral_graph_export.py
tests/test_historical_diary_neutral_graph_export.py
```

Ignored output:

```text
local_data/historical-diary-trove/inventory/neutral_derived_graph_h19.json
```

## Graph Shape

H19 keeps the H18 graph nodes and edges:

- `root`
- `event_class`
- `has_event_class_count`

It adds:

- `delta_bucket` nodes.
- `has_delta_bucket` edges from root nodes to delta-bucket nodes.

Delta buckets are derived from the maximum value in each safe adjacent neutral
delta range:

| Max value | Bucket |
|---:|---|
| 0 | `none` |
| 1-2 | `tiny` |
| 3-10 | `small` |
| 11-100 | `medium` |
| >100 | `large` |

## Local Result

The H19 run over H17 trends produced:

| Item | Count |
|---|---:|
| Root nodes | 3 |
| Event-class nodes | 4 |
| Delta-bucket nodes | 7 |
| Total nodes | 14 |
| Event-class count edges | 8 |
| Delta-bucket edges | 15 |
| Total edges | 23 |
| Represented transitions | 297 |

Observed delta-bucket nodes:

- `char_count_abs_delta_range:large`
- `date_like_token_count_abs_delta_range:none`
- `date_like_token_count_abs_delta_range:tiny`
- `non_empty_line_count_abs_delta_range:small`
- `paragraph_count_abs_delta_range:small`
- `time_like_token_count_abs_delta_range:small`
- `time_like_token_count_abs_delta_range:tiny`

## Interpretation

This is now a useful neutral GraphRAG substrate for aggregate questions such as:

- Which roots show large character-count movement?
- Which roots had no date-token movement?
- Which movement buckets co-occur with the isolated notable event classes?

It remains intentionally non-semantic. It cannot identify appointment creates,
deletes, patient movement, practitioner movement, status changes, or
confirmation requirements.

## Recommendation

Next sprint: add a safe graph query/report helper that answers a small set of
predefined read-only graph questions from the ignored graph artifact. That will
test whether the derived graph is actually useful before broadening the schema.
