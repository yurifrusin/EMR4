# Historical Diary Trove Neutral Derived Graph

Date: 2026-07-06
Sprint: H18 neutral derived graph export prototype
Scope: validator-safe graph derived from H17 cross-pilot event trends
Privacy posture: ignored local graph output only; no filenames, raw paths,
exact source document timestamps, document text, patient labels, staff labels,
visible diary content, or semantic appointment labels committed.

## Purpose

H18 proves that the historical diary trove can produce a graph-shaped memory
substrate without exposing raw diary content. This is a GraphRAG runway, not a
runtime Bernie memory integration and not semantic labelling.

## Tooling

Added:

```text
scripts/historical_diary_neutral_graph_export.py
tests/test_historical_diary_neutral_graph_export.py
```

Updated:

```text
scripts/historical_diary_output_safety.py
```

The safety validator now allows a deliberately small set of graph-neutral keys:
nodes, edges, node/edge identifiers, node/edge kinds, source/target node ids,
and aggregate node/edge counts.

Ignored output:

```text
local_data/historical-diary-trove/inventory/neutral_derived_graph_h18.json
```

## Graph Shape

The H18 graph contains:

- `root` nodes for each safe pilot root.
- `event_class` nodes for each observed neutral event class.
- `has_event_class_count` edges from root nodes to event-class nodes.

It does not contain:

- Raw diary text.
- File names or paths.
- Exact document timestamps.
- Patient or staff labels.
- Appointment semantics.
- Sequence-level state reconstruction.
- Write-authority hints for Bernie.

## Local Result

The H18 run over H17 trends produced:

| Item | Count |
|---|---:|
| Root nodes | 3 |
| Event-class nodes | 4 |
| Total nodes | 7 |
| Counted edges | 8 |
| Represented transitions | 297 |

The event-class nodes are:

- `large_unexplained_delta`
- `no_structural_change`
- `small_content_delta`
- `time_grid_delta`

## Interpretation

This is enough to demonstrate a safe GraphRAG direction: Bernie could later ask
read-only questions such as "which pilot roots contain time-grid deltas?" or
"how common are small neutral changes across the sampled roots?" without seeing
raw diary content.

It is not yet enough for appointment-level learning. The graph has no semantic
labels, no patient/resource identity, no true slot movement edges, and no
confirmation/action authority. Those must wait for explicit de-identification
approval and further derived graph sprints.

## Recommendation

Next sprint: enrich the neutral graph with derived delta-bucket nodes and edges
from validator-safe range data. Keep the graph aggregate-only and still block
semantic labels until the H15 gate is approved.
