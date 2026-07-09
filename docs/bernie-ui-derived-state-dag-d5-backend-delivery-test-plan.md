# Bernie UI Derived-State DAG D5 Backend Delivery Test Plan

Date: 2026-07-09

Status: blocked test plan only. This plan does not authorize implementation,
backend response delivery, route/schema changes, providers, memory/RAG/GraphRAG,
H15/H-series runtime inputs, historical diary runtime inputs, GraphQL delivery,
external patient clients, confirm payload changes, appointment write behavior
changes, or model-to-database writes.

Structured plan:
`docs/bernie-ui-derived-state-dag-d5-backend-delivery-test-plan.json`.

## Approval Prerequisite

The test plan is executable only after an explicit
`approved_for_backend_response_delivery_first_slice` decision. Until then,
`docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json` remains
`decision: blocked` and the production route import ban remains correct.

## Candidate First Slice

The candidate first slice is a single reviewed Bernie response assembly point,
currently represented as
`POST /api/v1/appointments/proposals/bernie/supervised-booking`, with an
optional `staff_review.bernie.ui_view_model` response field.

The field must be omitted when no server session snapshot exists. If delivered,
server-side client confirmation request state must default to `idle` unless a
separate reviewed transient-state contract exists.

## Required Test Groups

The future approved implementation must cover:

- gate and preflight values before delivery;
- optional response attachment and backward compatibility;
- backend-confirmed-only success state;
- pressed, awaiting-backend, stale, and failed state behavior;
- confirm-payload serialization purity and signed-confirm authority;
- zero appointment/audit writes from supervised booking alone;
- non-Bernie router import isolation;
- provider, memory, GraphQL, H15/H-series, and historical-diary isolation;
- evidence labeling that remains non-live-provider.

## Stop Conditions

Stop and return to review if any test requires provider calls, Access AI,
memory/RAG/GraphRAG, GraphQL, H15/H-series material, historical diary material,
confirm payload changes, appointment write behavior changes, external patient
client exposure, frontend JavaScript expansion, or a broad router refactor.
