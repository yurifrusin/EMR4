# Appointment Support Routes Infrastructure Boundary

Date: 2026-07-08

Sprint: 198

## Purpose

The appointment route inventory preflight currently finds out-of-contract POST
method rows under `/api/v1/appointments`. These rows are support infrastructure
for the appointment proposal and Bernie session pipelines. They are not Diary
grammar dispatch authority and must not be promoted into
`DIARY_ACTION_ROUTE_CONTRACTS` merely because they are mounted appointment
routes.

The preflight keeps this distinction aggregate-only. It does not emit route
paths, handler names, request payloads, IDs, patient/practitioner data, local
historical diary paths, or provider output.

## Current Sub-Families

| Sub-family | Current count | Infrastructure role | Grammar authority |
|---|---:|---|---|
| `proposal_support_post` | 7 | Slot-search and Bernie proposal-support pipeline infrastructure | No |
| `state_tracking_post` | 2 | Bernie session lifecycle and taskpane state tracking infrastructure | No |
| `ambiguous_post` | 0 | Unclassified out-of-contract POST shapes requiring review | No |

These route shapes may support proposal preparation, slot-search normalization,
candidate selection, or session state tracking. They are not themselves Diary
grammar proposals, confirms, raw mutations, or dispatch surfaces.

## Guard

`scripts/appointment_route_inventory_preflight.py` must continue to report
`out_of_contract_post_rows_are_grammar_dispatch_authority=false`.

`tests/test_appointment_route_inventory_preflight.py` also requires
`ambiguous_post` to stay at zero. If a future mounted appointment POST row no
longer fits the fixed proposal-support or state-tracking classifiers, the sprint
engine should pause for explicit review of whether that route is new support
infrastructure or belongs in the Diary action route contract.

This boundary does not authorize runtime route wiring, provider dry-runs,
database writes, memory/RAG/GraphRAG use, H15/H-series runtime imports,
historical diary material access, GraphQL mutation work, or model-to-database
write authority.

## Verification

```powershell
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
```
