# Claude Sprint 160 - Bernie/Diary Review Readiness

## Mission

Review whether the current Bernie/Diary implementation is ready for Yuri to run
a meaningful hands-on diary review after the confirm-client idempotency header
sprints.

## Scope

- Read-only review of Bernie release gates, API-spine evidence labels, provider
  boundary posture, and recent confirm-client header closeouts.
- Do not change runtime code, routes, providers, database models, H15/H-series
  material, memory/RAG/GraphRAG, or `docs/diary`.
- If Claude is paused or unavailable, Ariadne may use a DeepSeek replacement
  lane for this same review brief.

## Required Checks

- `.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
  must still report `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`.
- `.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py`
  must still report `default_provider=disabled`,
  `runtime_or_provider_wiring_ready=false`, `live_provider_enabled=false`,
  `provider_calls_performed=false`, `route_behavior_changed=false`,
  `database_access_performed=false`,
  `memory_or_rag_access_performed=false`, and
  `historical_diary_material_access_performed=false`.
- Route-intercepted UI checks may support the review decision, but must not be
  called live-backend or live-provider evidence.
- The historical diary/trove, H15/H-series, and memory gates must remain closed.

## Expected Output

Write a concise plan/review packet under `orchestration/agent_inbox/codex/`
summarising whether Yuri should pause for review now, what she should test, and
what still remains blocked.
