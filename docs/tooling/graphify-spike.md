# Graphify Code Graph Spike

## Outcome

Graphify is useful enough to keep as an opt-in local code navigation aid, but
not yet as an always-on Codex MCP or hook integration.

The controlled spike installed `graphifyy[mcp]` into a disposable temp virtual
environment and ran a zero-token AST rebuild:

```powershell
$env:GRAPHIFY_EXE = "$env:TEMP\emr4-graphify-pilot\.venv\Scripts\graphify.exe"
scripts\refresh_code_graph.ps1
```

Result on 2026-07-05:

- `graphify update . --no-cluster` completed in about 13 seconds.
- The generated graph had about 11.2k nodes and 19.7k edges.
- `graphify-out\graph.json` was about 11.6 MB.
- `graphify-out\` was about 24.4 MB total and is intentionally ignored.
- `graphify benchmark graphify-out\graph.json` estimated about 24x fewer tokens
  for its sample graph queries than reading the whole corpus.

## What Worked

Symbol-level lookups were useful:

```powershell
graphify explain "propose_bernie_supervised_booking" --graph graphify-out\graph.json
graphify affected "normalize_slot_search_command" --graph graphify-out\graph.json --depth 2
```

These produced concrete file and line references for routers, service helpers,
and tests. That is likely helpful before touching Bernie/Diary code.

## What Did Not Work Well

Broad natural-language queries were noisy:

```powershell
graphify query "What code handles Bernie clarification merge semantics?" --graph graphify-out\graph.json
```

This returned hundreds of nodes and was less useful than targeted symbol
queries. Ariadne should treat graph queries as a map, not an oracle.

## Current Recommendation

- Keep `graphify-out\` ignored and local-only.
- Use `scripts\refresh_code_graph.ps1` on demand before architecture or impact
  review work.
- Prefer `explain`, `affected`, and narrow `query --context ...` patterns over
  broad natural-language graph search.
- Do not install Graphify's Codex hooks, MCP server, or post-commit hooks yet.
- Reconsider MCP only after confirming graph refresh/reload behaviour in a fresh
  Codex session and proving that it does not interfere with worker handins,
  DeepSeek bridge runs, or normal shell flow.

## Possible Next Step

If this remains useful across two or three sprints, add a dedicated tooling
sprint to evaluate:

- project-local Graphify Codex instructions,
- a safe post-commit graph refresh hook,
- MCP stdio registration in `C:\Users\sarashera\.codex\config.toml`,
- whether Claude and Antigravity benefit from the same graph artifacts.

Use `docs/tooling/graphify-efficacy-benchmark.md` and
`scripts/run_graphify_efficacy_benchmark.ps1` to score whether the tool is
actually improving code navigation before any stronger integration.
