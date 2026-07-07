# Sprint 158 - Confirm Client Surface Checkpoint

## Mission

Review the compact checkpoint after Sprints 153-157 wired Diary client
`Idempotency-Key` headers for create-proposal and the ordinary confirm family.

## Scope

- Target worktree: `C:\Users\sarashera\emr4`.
- Focus artifacts:
  - `orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md`
  - `orchestration/api_spine_appointment_idempotency_update_confirm_client_header.md`
  - `tests/test_api_spine_frontend_header_inventory.py`
  - `docs/diary/diary.js`
- Decide the safe next slice among:
  - Bernie tool-intent update confirm client header semantics;
  - proposal-only backend/header binding;
  - strict OpenAPI `minLength: 8` runtime enforcement.

## Constraints

Do not open providers, GraphQL mutations, memory/RAG/GraphRAG, H15/H-series
runtime imports, broad historical diary material, raw compatibility write
changes, or backend idempotency ledger changes.

## Output

Write a concise review artifact to
`orchestration/agent_inbox/codex/plan-claude-claude-sprint158-confirm-client-surface-checkpoint.md`.
