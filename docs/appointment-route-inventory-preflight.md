# Appointment Route Inventory Preflight

Date: 2026-07-07

Sprint: 193

## Purpose

`scripts/appointment_route_inventory_preflight.py` emits a safe aggregate
inventory over mounted FastAPI `APIRoute` metadata under `/api/v1/appointments`.
It separates routes documented by `DIARY_ACTION_ROUTE_CONTRACTS` from broader
appointment-router surfaces without changing route behavior or expanding Diary
grammar authority.

The report is intentionally count-only. It does not emit route paths, handler
names, request bodies, IDs, payload fields, patient/practitioner data, or local
material paths.

## Shape

The preflight reports:

- total mounted appointment route counts;
- total distinct appointment path counts;
- total mounted appointment method-row counts;
- Diary action contract documented path counts;
- contract-covered route and method-row counts;
- grammar-authority route and method-row counts;
- raw-adjacent route and method-row counts;
- out-of-contract route and method-row counts by coarse method family; and
- out-of-contract route counts by coarse category.

`raw_mutation_routes` are counted separately as adjacent route awareness. They
are not counted as grammar dispatch authority, and only mounted write methods
on those paths are counted as raw-adjacent rows. Mounted read methods on the
same path remain out-of-contract unless another non-raw contract field claims
them. The report keeps `raw_adjacent_routes_are_grammar_dispatch_authority=false`.

## Boundary

This is a static route-table preflight only. It does not issue HTTP requests,
execute route handlers, open database sessions, call providers, read
memory/RAG/GraphRAG, import H15/H-series runtime material, access historical
diary material, invoke GraphQL, or perform writes.

`DIARY_ACTION_ROUTE_CONTRACTS` remains a Diary grammar authority contract, not a
complete appointment-router catalogue. Out-of-contract route counts are a
planning signal for later review; they are not automatically bugs and do not
require adding non-grammar infrastructure routes to the Diary action contract.

## Verification

```powershell
.venv\Scripts\python.exe scripts\appointment_route_inventory_preflight.py
.venv\Scripts\python.exe -m pytest tests\test_appointment_route_inventory_preflight.py -q
```
