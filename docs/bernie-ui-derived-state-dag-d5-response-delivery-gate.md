# Bernie UI Derived-State DAG D5 Response Delivery Gate

Date: 2026-07-09

Status: blocked. Sprint 240 proved a frontend-only, route-intercepted consumer
for an optional `bernie.ui_view_model.v1` display payload. It did not approve
backend response delivery, route/schema changes, GraphQL delivery, provider
delivery, memory/RAG/GraphRAG use, H15/H-series runtime inputs, or write
authority.

Gate payload: `docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json`.

Required pre-D5 readiness commands:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected values remain blocked/disabled: `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, `runtime_gate_decision=blocked`,
`default_provider=disabled`, `live_provider_enabled=false`, and
`provider_calls_performed=false`.

## Current Posture

- The primary `renderBernieReview` panel can consume an optional display-only
  view model when route-intercepted fixtures provide it.
- Command authority still comes from existing signed confirm fields:
  `confirm_endpoint`, `confirm_payload`, freshness IDs, evidence, and the
  existing confirm affordance gate.
- The full Diary route-intercepted Playwright harness remains the committed UI
  evidence spine.
- Production routes must not emit or import `BernieUiViewModel` until this gate
  is explicitly reviewed and changed.

## Before Backend Delivery

Any sprint that proposes backend delivery of `BernieUiViewModel` must pause for
explicit review and provide:

- the exact response schema contract and attachment point;
- server-side tests building the view model from a session snapshot without
  provider, memory, H15/H-series, GraphQL, or write coupling;
- browser tests proving existing command payloads still exclude view-model
  fields;
- stale, pressed, awaiting-backend, failed, and confirmed state contracts;
- backward-compatible absence/omission behavior for response paths that do not
  have a server session snapshot;
- route/provider/import isolation evidence.

## Not Approved

This gate does not approve production route emission, GraphQL resolver delivery,
provider prompts, Access AI invocation, memory/RAG/GraphRAG, historical diary
runtime inputs, appointment write changes, or model-to-database writes.
