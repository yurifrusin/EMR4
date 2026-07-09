# Bernie UI Derived-State DAG D5 Approval Decision Draft

Date: 2026-07-09

Status: blocked decision draft. This is not an approval and does not change the
D5 response-delivery gate.

Draft payload:
`docs/bernie-ui-derived-state-dag-d5-approval-decision-draft.json`.

## Decision Surface

The only proposed future approval name is
`approved_for_backend_response_delivery_first_slice`. If Yuri later approves
that decision explicitly, the approval should cover only one reviewed Bernie response assembly point
that emits an optional `bernie.ui_view_model.v1` display field.

The draft keeps `decision: blocked`, blank reviewer, blank approved contract
commit, blank expiry date, and `go_no_go_acknowledged: false`.

## Scope Still False

Every approval-scope field remains false in the draft, including backend
response delivery, route/schema change, GraphQL delivery, provider/live-provider
wiring, Access AI invocation, memory/RAG/GraphRAG wiring, H15/H-series runtime
input, historical diary runtime input, appointment write behavior changes,
confirm payload changes, model-to-database writes, external patient-client
exposure, and frontend JavaScript scope expansion.

## If Later Approved

The future first slice may only:

- emit optional `bernie.ui_view_model.v1` from one reviewed Bernie response
  assembly point;
- call `build_bernie_ui_view_model` once from that attachment point;
- omit the field when no server session snapshot exists;
- default server-delivered client confirmation request state to `idle`;
- preserve existing signed confirm endpoint and confirm payload authority.

Even then, GraphQL, providers, Access AI, memory/RAG/GraphRAG, H15/H-series,
historical diary material, external patient clients, frontend scope expansion,
confirm payload changes, appointment write changes, and model-to-database writes
remain out of scope.

## Required Review Values

Before any approval, the pre-D5 checks must still report:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`
- `default_provider=disabled`
- `live_provider_enabled=false`
- `provider_calls_performed=false`

Any change to the decision, reviewer, expiry, contract commit, approval-scope
booleans, allowed future scope, or forbidden future scope requires a sprint
pause and explicit review.
