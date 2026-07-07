# Sprint 159 - Bernie Tool-Intent Confirm Header

## Mission

Review the frontend/product fix for Bernie tool-intent update-confirm clicks:
`confirmBernieToolIntentChange()` should send HTTP `Idempotency-Key` to the
existing signed update-confirm backend route.

## Scope

- Target: `docs/diary/diary.js`.
- Tests: `review/test_diary_smoke.py`,
  `tests/test_api_spine_frontend_header_inventory.py`, and related docs.
- Check that the visible tool-intent confirm button no longer posts a
  header-free request in route-intercepted smoke coverage.

## Constraints

No UI redesign, provider enablement, backend ledger changes, proposal-only
binding, strict `minLength: 8`, memory/RAG/GraphRAG, H15/H-series runtime
imports, broad historical diary material, or raw compatibility writes.

## Output

Write a concise review artifact to
`orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint159-bernie-tool-intent-confirm-header.md`.
