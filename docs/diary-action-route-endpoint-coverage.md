# Diary Action Route Endpoint Coverage

Date: 2026-07-07

Sprint: 191, extended in Sprint 192

## Purpose

`tests/test_diary_action_route_endpoint_coverage.py` reconciles the static Diary
action route contract with the FastAPI routes mounted on `app.main:app`.

This is a static route-table scan. It imports the app and inspects `APIRoute`
metadata only. It does not issue HTTP requests, execute route handlers, open a
database session, call provider clients, read memory/RAG/GraphRAG, import
H15/H-series runtime material, access historical diary material, invoke
GraphQL, or perform writes.

## Coverage

The scan checks that every route string documented in
`DIARY_ACTION_ROUTE_CONTRACTS` is mounted:

- read routes;
- proposal routes;
- signed confirm routes; and
- adjacent raw mutation routes documented for boundary awareness.

It also checks method shape:

- proposal and confirm routes are POST-mounted;
- read routes are GET or POST mounted; and
- raw mutation routes expose a mutating HTTP method.

Sprint 192 hardens the same static scan with route-table shape checks:

- documented contract paths must not have duplicate `(path, method)` mounts;
- literal documented contract paths must not be captured by an earlier
  parametric route with an overlapping HTTP method;
- proposal and confirm routes must be POST-only after ignoring framework-level
  HEAD/OPTIONS metadata;
- read routes may be query-style POST routes, but must not expose
  PUT/PATCH/DELETE; and
- planned action proposal routes must not overlap implemented confirm or raw
  mutation targets.

Planned native Diary verbs (`check_in`, `waiting_area_move`, and
`link_patient`) remain `planned_not_implemented`: they may document adjacent
read/proposal surfaces, but still have no confirm route or raw mutation route
authority.

## Boundary

Endpoint existence in the FastAPI registry does not prove route behavior,
authorization, idempotency, confirmation evidence, error handling, provider
quality, availability quality, or safety of any clinical workflow. Those
properties remain covered by separate route contract tests, API-spine tests,
scenario replay, and reviewed gate decisions.

This sprint grants Bernie no new write, availability, or confirmation
authority. The runtime/provider gate remains blocked, and live-provider and
provider-quality evidence remain false.

The broader question of whether every mounted appointment route should be
classified in a source-derived route inventory is intentionally deferred. The
current `DIARY_ACTION_ROUTE_CONTRACTS` module remains a Diary grammar authority
contract, not a complete appointment-router catalogue.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_endpoint_coverage.py -q
.venv\Scripts\python.exe -m pytest tests\test_diary_action_route_contract.py -q
.venv\Scripts\python.exe scripts\bernie_scenario_evidence_snapshot.py
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\historical_diary_leakage_lint.py tests docs
git diff --check
```
