# S15 Terra Plan - Tranche Acceptance And Process Metrics

Status: approved by Sol for staging-only execution after integrated S13 and S14.

## Boundary

S15 runs deterministic acceptance and records final S13-S15 coordination
metrics only. It does not alter Diary product behaviour, routes, GraphQL,
providers, schema/database, deployment/release, external clients, H15/H-series,
historical trove, memory/RAG/GraphRAG, terminal-to-active policy, or write
authority. S15 does not open any successor sprint.

## Allocation

Terra owns planning, deterministic execution, acceptance, metrics, staging
closeout, and the exact protected-master manifest. No worker, Gemini, DeepSeek,
Conductor, or verifier is allocated because the S13/S14 evidence is explicit
and no conflicting evidence or new-risk trigger is present.

## Acceptance

1. Run the integrated S14 policy/Diary/workflow/API-Spine suite.
2. Run the preflight, Deep Code PTY, observability, adapter-settings, and
   allocation-schema control suites.
3. Verify all closed gates, tracked diff scope, compile checks, and clean
   staging state.
4. Record per-sprint and tranche reliability/economy metrics, including known
   lifecycle corrections and advisory durable durations.
5. Commit only S15 plan, closeout/metrics, handover update, and exact manifest.
   Do not merge or push protected master without a new Sol authorization.
