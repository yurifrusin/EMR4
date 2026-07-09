# Bernie UI Derived-State DAG D5 Implementation Checklist

Date: 2026-07-09

Status: first-slice checklist. This records the narrow implementation checklist
for the approved `approved_for_backend_response_delivery_first_slice` gate. It
does not approve providers, GraphQL, memory/RAG/GraphRAG, H15/H-series runtime
inputs, historical diary runtime inputs, confirm payload changes, appointment
writes, or model-to-database writes.

Gate prerequisite:
`docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json` now records
`approved_for_backend_response_delivery_first_slice`. The implementation must
stay inside that first slice.

## Pre-Implementation Checks

Run and record:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

Expected values:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`
- `default_provider=disabled`
- `live_provider_enabled=false`
- `provider_calls_performed=false`

## Permitted First Slice

The first delivery slice must remain:

- optional response field only;
- one response assembly attachment point;
- `client_confirmation_request_state=idle` unless a separate reviewed client
  transient-state contract exists;
- synthetic or route-intercepted tests only;
- no frontend JavaScript expansion beyond reading the already-supported field
  location;
- fine-grained import guard that allows only the reviewed Bernie route delivery
  point and keeps non-Bernie routers blocked from importing the selector.

## Required Tests For The First Delivery Slice

1. Response with a server session snapshot includes a valid
   `bernie.ui_view_model.v1` model.
2. Response without a server session snapshot leaves the field null or absent
   rather than constructing a synthetic empty view model.
3. Pre-confirm states never set `confirmation_state=confirmed` or
   `show_success_copy=true`.
4. Confirmed server-snapshot state sets
   `confirmation_state.source=server_snapshot`.
5. Pressed and awaiting-backend states remain not-booked-yet and never show
   success copy.
6. Stale state sets `freshness_state=stale`, shows stale warning, and blocks
   confirm display.
7. Confirm payload serialization excludes `copy_mode`, `confirmation_state`,
   `freshness_state`, `flags`, `primary_copy`, and `secondary_copy`.
8. Non-Bernie production routers do not import
   `app.services.bernie.ui_view_model`.
9. `BernieUiViewModel.model_json_schema()` contains no write-authority fields.
10. Ordinary pre-confirm copy excludes raw UUIDs, snake_case error codes,
    `booked`, and `confirmed`.

## Stop Conditions

Stop and return to review if the implementation needs database queries,
provider calls, Access AI, memory/RAG/GraphRAG, GraphQL, H15/H-series material,
raw diary text, new write behavior, a schema-version change, or broad router
refactoring.
