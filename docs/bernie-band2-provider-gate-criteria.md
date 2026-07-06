# Bernie Band-2 Provider Gate Criteria

Date: 2026-07-07

Status: proposal only. This document is not approval to enable a provider,
runtime route wiring, provider prompt wiring, provider dry-run wiring, external
patient clients, GraphQL mutations, H15/H-series runtime imports, historical
diary material access, memory/RAG/GraphRAG use, or model-to-database writes.

## Current Verdict

Sprint 108 closed the Bernie booking-instruction interpreter's Access AI
evidence gap without opening live providers. Sprint 109 should keep the gate
closed and define what must be true before Yuri could consider a future
no-write live-provider smoke or runtime-provider movement.

Current required readiness evidence remains:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
```

Expected blocked values:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`

If any of those values changes, the sprint engine pauses for explicit review.

## Approval Payload Shape

Any future approval must be a reviewed, dated payload committed before gate
state changes. It should include at least:

```json
{
  "gate": "bernie_band2_provider_runtime",
  "decision": "blocked",
  "reviewer": "",
  "approved_on": "",
  "approval_expires_on": "",
  "scope": {
    "no_write_live_provider_smoke": false,
    "runtime_provider_route_wiring": false,
    "provider_prompt_wiring": false,
    "provider_dry_run_wiring": false,
    "external_patient_clients": false,
    "graphql_mutations": false,
    "h15_h_series_runtime_imports": false,
    "historical_diary_material_access": false,
    "memory_rag_graphrag": false,
    "model_to_database_writes": false
  },
  "acknowledgements": {
    "no_autonomous_booking_writes": false,
    "staff_confirmation_required": false,
    "kill_switch_reviewed": false,
    "cost_cap_reviewed": false,
    "privacy_and_retention_reviewed": false
  }
}
```

The default and current decision is `blocked`. Changing any scope value to
`true` requires Yuri approval and a new closeout checkpoint.

## Blocking Criteria

Before any future gate opening is proposed, all of these must be true:

1. Yuri approval payload is filled, reviewed, dated, scoped, and committed.
2. The readiness command above still reports the expected blocked values before
   the approval payload changes them.
3. A bounded no-write runtime plan exists and explicitly says provider output
   cannot create, update, confirm, delete, or audit-write appointments.
4. A deterministic offline oracle exists for the Margaret Thompson / Dr Shera
   ordinary prompt, so live-provider failures can be compared to a non-provider
   reference result.
5. Access AI audit events have typed schemas for allowed, blocked, and failed
   invocation paths, including provider-error metadata coverage and forbidden
   raw/prompt/PHI key checks.
6. A provider kill switch or startup health check can fail closed if live
   provider configuration appears while the gate decision is `blocked`.
7. Cost controls exist: per-call accounting, hard caps, spike detection, and a
   tested failure path that does not retry in a loop.
8. Route authority remains backend-owned: provider-shaped frames cannot set
   `writes_authorized=true` or bypass signed confirmation evidence.
9. Staff-visible Bernie UI has a tested "not booked yet" affordance for any
   provider-produced proposal-like output.
10. Provider privacy and retention have been reviewed for prompt contents,
    output retention, audit retention, and clinical data handling.
11. H15/H-series and historical diary boundaries are rechecked: provider prompts
    must not reference raw trove material, ignored local payloads, or semantic
    diary-derived fixtures.
12. Focused negative tests prove blocked gate paths remain blocked: fake and
    disabled modes produce no live provider calls; blocked provider config fails
    before route execution; provider output cannot write.

## Staff UX Criteria

A future no-write live-provider smoke is not user-facing product launch. Staff
copy must say what happened without implying availability, booking completion,
or autonomous authority.

Required visible behavior for a future smoke:

- debug/dev metadata must show provider, mode, and `live_provider`;
- ordinary staff copy must avoid "booked", "confirmed", "available", or
  equivalent completion claims unless signed backend evidence exists;
- any provider-produced candidate is staged for staff review only;
- no route-intercepted smoke may be described as live;
- live evidence must include non-intercepted backend/provider metadata and
  `live_provider=true`;
- failure copy must be calm, bounded, and explicit that no appointment was
  changed.

## Adversarial Findings To Carry Forward

DeepSeek's Sprint 109 review identifies the main risk as boundary creep rather
than an obvious gate flip. The highest-priority failure modes are:

- configuration drift that silently routes fake-provider paths to a live
  provider;
- provider output treated as write authority;
- provider failures or raw responses leaking into audit metadata;
- live smoke without a deterministic offline oracle;
- cost/rate-limit spikes before kill-switch and cap instrumentation;
- H15 semantic-gate creep through prompt context rather than imports;
- staff seeing proposal-like output as if it were confirmed.

These findings should shape the next safe sprint if Yuri does not approve a
gate opening: add a runtime/startup assertion that provider configuration cannot
be live while `runtime_gate_decision=blocked`.

## Non-Approval Statement

This document is a checkpoint artifact. It does not approve or perform provider
enablement, runtime route wiring, provider prompt wiring, provider dry-run
wiring, memory/RAG/GraphRAG use, H15/H-series runtime imports, historical diary
material access, external patient clients, GraphQL mutations, or model writes.

All provider/runtime/trove/memory/model-write gates remain blocked pending Yuri.
