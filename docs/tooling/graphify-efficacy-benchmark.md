# Graphify Efficacy Benchmark

## Purpose

This benchmark tests whether Graphify makes Ariadne faster and more accurate at
finding EMR4 code relationships. It is not testing whether Graphify can replace
normal source reading; it is testing whether it gives a better first map.

## Runner

Run from the repo root after installing Graphify locally:

```powershell
$env:GRAPHIFY_EXE = "$env:TEMP\emr4-graphify-pilot\.venv\Scripts\graphify.exe"
scripts\run_graphify_efficacy_benchmark.ps1 -RefreshGraph
```

The runner:

- refreshes `graphify-out\graph.json` when requested,
- runs six deterministic zero-token Graphify queries,
- writes raw query outputs under `graphify-out\benchmarks\efficacy\`,
- writes `summary.json` with timing, exit code, line count, and output paths.

`graphify-out\` is ignored, so benchmark outputs are local evidence rather than
project artifacts.

## Question Set

| ID | Mode | Target | What It Tests |
|---|---|---|---|
| `symbol-proposal-route` | `explain` | `propose_bernie_supervised_booking` | Finds Bernie proposal route and collaborators |
| `impact-slot-normalizer` | `affected` | `normalize_slot_search_command` | Finds callers and tests affected by normalizer changes |
| `symbol-booking-interpreter` | `explain` | `BookingInstructionInterpreter` | Finds AI interpreter seam |
| `symbol-diary-loader` | `explain` | `loadDiary` | Finds frontend diary loading code |
| `query-clarification-merge` | `query` | `What code handles Bernie clarification merge semantics?` | Tests broad R2-style search quality |
| `query-confirmation-evidence` | `query` | `Where is Bernie confirmation evidence minted and verified?` | Tests domain phrase search quality |

## Manual Scoring

For each benchmark question, score Graphify before using normal file reads:

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| First file usefulness | No relevant file | Relevant but not primary | Primary implementation/test file found |
| Relationship usefulness | Misleading/no edges | Some useful edges | Callers/callees/tests materially useful |
| Noise level | Too noisy to help | Needs filtering | Compact enough to act on |
| Completeness | Misses key surface | Partial map | Enough to plan next read/test step |

Maximum score per question: 8.

## Adoption Gates

Keep Graphify as an opt-in tool if:

- average score is at least 5/8,
- symbol-level questions score at least 6/8,
- broad natural-language questions do not dominate Ariadne's usage pattern,
- the graph can be refreshed without dirtying tracked files.

Consider Codex MCP or auto-indexing only if:

- this benchmark remains useful across two or three real sprints,
- a fresh Codex session can see updated graph data after rebuild,
- post-commit refresh does not slow normal handoff/submit flows,
- worker worktrees do not accidentally share stale or wrong-branch graph data.

## Baseline Notes

The initial spike suggests `explain` and `affected` are the promising commands.
Broad `query` output can return hundreds of nodes and should be treated as a
weak signal unless a narrower context filter proves reliable.

Initial benchmark run on 2026-07-05:

| ID | Runtime | Initial Score | Note |
|---|---:|---:|---|
| `symbol-proposal-route` | 0.858s | 8/8 | Found primary route, collaborators, and proposal helpers |
| `impact-slot-normalizer` | 0.433s | 8/8 | Found importers, route callers, and focused normalizer tests |
| `symbol-booking-interpreter` | 0.809s | 7/8 | Found primary interpreter seam; less complete on call flow |
| `symbol-diary-loader` | 0.807s | 8/8 | Found frontend loader plus key UI callers/callees |
| `query-clarification-merge` | 0.997s | 4/8 | Found relevant surfaces but with hundreds of noisy nodes |
| `query-confirmation-evidence` | 1.699s | 4/8 | Found relevant evidence surfaces but still too broad |

Average initial score: 6.5/8. Symbol/impact average: 7.75/8. Broad-query
average: 4/8. This passes the opt-in-use gate and fails the always-on MCP/hook
gate for now.
