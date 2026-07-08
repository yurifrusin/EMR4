# Claude Fable Task: Bernie UI Derived State DAG Review

Date: 2026-07-08

Preferred reviewer: Claude Fable, if still available. If Fable is unavailable,
use the highest-reasoning Claude reviewer available and label the model
substitution explicitly.

## Context

Yuri proposed using DAG-style conditioning dependencies to simplify Bernie UI
behavior. The core idea is that a small number of canonical state nodes, such as
confirmation state, can drive many otherwise separate UI elements: candidate
slot lists, pending proposal cards, identity checks, confirm controls, stale
warnings, success copy, and old prompt visibility.

Codex drafted the plan packet:

- `docs/bernie-ui-derived-state-dag-plan.md`

This is a design-review request only. Do not implement code, modify gates,
enable providers, add route wiring, add GraphQL resolvers, touch database
writes, or import H15/H-series/historical diary material.

## Proposal-Surface Guard Citation

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected current blocked values:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`
- `default_provider=disabled`
- `live_provider_enabled=false`
- `provider_calls_performed=false`
- `route_behavior_changed=false`
- `database_access_performed=false`
- `memory_or_rag_access_performed=false`
- `historical_diary_material_access_performed=false`

## Required Inputs

Read these files before reviewing:

- `docs/bernie-ui-derived-state-dag-plan.md`
- `orchestration/event_driven_statechart_architecture.md`
- `orchestration/bernie_interaction_model.md`
- `orchestration/bernie_release_gates.md`
- `orchestration/api_spine_adr.md`
- `docs/bernie-prompt-thread-tranche-readiness.md`

## Review Questions

1. Is the event-log plus statechart plus derived-state DAG split coherent, or is
   it too much architecture for the current Bernie UI?
2. Are the proposed canonical nodes the right level of granularity?
3. Which proposed node is most likely to become a hidden write-authority leak?
4. Should the first pure selector live under `app/services/bernie/` as a backend
   contract, in the frontend as a rendering selector, or as a shared schema
   artifact?
5. What minimal fixture matrix should exist before any UI wiring sprint starts?
6. Should this become the next plan-only sprint if Yuri does not approve the
   practitioner-directory runtime route sprint, or should it wait behind the
   prompt-thread fake-provider backend pass?
7. Does the plan preserve the API spine rule that read/display hints are not
   write grants?

## Expected Output

Write a concise review artifact to:

```text
orchestration/agent_inbox/codex/review-claude-fable-bernie-ui-derived-state-dag.md
```

Use this structure:

- verdict;
- direct answer to Yuri's sequencing question;
- strongest reason to do it soon;
- strongest reason to delay it;
- required changes to the plan before implementation;
- recommended first sprint shape;
- no-go boundaries that must remain closed;
- residual risks.

## Non-Approval Boundaries

This task must not approve or perform:

- live provider calls;
- provider prompt wiring;
- provider dry-run wiring;
- runtime route wiring from the interpretation harness;
- memory/RAG/GraphRAG runtime wiring;
- H15/H-series runtime imports;
- historical diary material access;
- GraphQL mutations;
- new GraphQL resolvers;
- external patient clients;
- model-to-database writes;
- appointment writes outside existing REST command handlers.

