# Sprint 159 - Bernie Tool-Intent Confirm Header

## Mission

Review the narrow frontend fix for `confirmBernieToolIntentChange()` so Bernie
tool-intent update-confirm clicks send an HTTP `Idempotency-Key` header.

## Scope

- Target: `docs/diary/diary.js`.
- Tests: `review/test_diary_smoke.py`,
  `tests/test_api_spine_frontend_header_inventory.py`, and any checkpoint docs.
- Preferred strategy from Sprint 158: freshness-derived
  `update-confirm-<update_proposal_freshness_id>` to match ordinary
  update-confirm callers.

## Constraints

No backend ledger changes, proposal-only binding, strict `minLength: 8`
enforcement, providers, GraphQL mutations, memory/RAG/GraphRAG, H15/H-series
runtime imports, broad historical diary material, or raw compatibility writes.

## Output

Write a concise review artifact to
`orchestration/agent_inbox/codex/plan-claude-claude-sprint159-bernie-tool-intent-confirm-header.md`.
