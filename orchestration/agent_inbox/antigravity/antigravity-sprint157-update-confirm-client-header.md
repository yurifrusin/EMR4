# Sprint 157 - Update Confirm Client Header Worker Packet

## Mission
Review Sprint 157's narrow API-spine change: the Diary frontend should emit HTTP `Idempotency-Key` headers for ordinary signed update-confirm calls.

## Scope
- Target worktree: `C:\Users\sarashera\emr4`.
- Focus files: `docs/diary/diary.js`, `review/test_diary_smoke.py`, `tests/test_api_spine_frontend_header_inventory.py`, and the Sprint 157 orchestration doc.
- Required call sites: edit modal update-confirm and drag/move/resize update-confirm.
- Explicitly deferred: `confirmBernieToolIntentChange`, proposal-only route headers, raw PUT fallback, backend ledger behavior, OpenAPI `minLength: 8` runtime enforcement, providers, memory/RAG/GraphRAG, and historical diary gates.

## Questions
1. Should update-confirm keys derive from `update_proposal_freshness_id`, and is a generated proposal fallback acceptable when freshness is absent/too long?
2. Are both ordinary update-confirm callers covered without granting headers to raw compatibility paths?
3. What tests/docs should be considered blocking before Sprint 157 closeout?

## Output
Write a concise plan or review artifact to `orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint157-update-confirm-client-header.md`.
