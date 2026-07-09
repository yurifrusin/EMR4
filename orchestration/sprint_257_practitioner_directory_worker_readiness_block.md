# Sprint 257 Practitioner Directory Worker Readiness Block

Date prepared: 2026-07-09

Purpose: prepare the next practitioner-directory block using the corrected
worker-dispatch rule: maximize useful worker gain where possible, but require a
distinct artifact or veto surface for every lane.

This block does not change `rest_route_ready`, route code, schemas, services,
SDL, GraphQL, providers, Access AI, memory/RAG/GraphRAG, H15/H-series runtime
imports, historical diary material access, external patient-client exposure,
deployment posture, production readiness, or write authority.

## Recommended Block Shape

Run Sprint 257 as one multi-worker go/no-go decision block instead of three
small Ariadne-only micro-sprints.

The block decides whether Yuri should be asked to approve
`rest_route_ready=true` for `GET /api/v1/practice/practitioners` only, or
whether the route should remain implemented-but-not-ready with named blockers.
It must not flip the readiness flag by itself.

## Sprint 257 Lane Plan

| Lane | Role | Expected artifact or veto surface | Integration value |
|---|---|---|---|
| Ariadne | Orchestrator/integrator | Final Sprint 257 decision packet and tests | Owns final recommendation and keeps all adjacent gates false |
| Claude | Independent readiness/safety veto | Review packet naming missing evidence, unsafe implication, or no-go blockers before `rest_route_ready=true` | Prevents readiness wording from outrunning runtime/security evidence |
| Antigravity | Consumer/API ergonomics and external-client boundary review | Review packet over OpenAPI shape, response semantics, query defaults, consumer expectations, and external patient-client non-exposure | Tests whether the route is ready for intended internal consumers without implying public exposure |
| DeepSeek | Mechanical safety sweep | Grep/static sweep results for readiness flag flips, sensitive-field exposure, detail route exposure, GraphQL/provider/memory/H15/trove imports, and write side effects | Cheap high-coverage regression/veto lane |

If Claude or Antigravity is unavailable, substitute an additional DeepSeek lane
only when it can preserve the missing role's distinct artifact or veto surface.
If a lane would merely repeat another worker's review, stand it down and record
why.

## Inputs

- `app/routers/practice.py`
- `app/schemas/practice.py`
- `app/services/practice/practitioner_directory_read.py`
- `tests/test_practitioner_directory_route.py`
- `docs/api-spine/practitioner-directory-approved-gate.json`
- `docs/api-spine/practitioner-directory-post-implementation-readiness-review.json`
- `docs/api-spine/practitioner-directory-runtime-evidence-refresh.json`
- `docs/api-spine/practitioner-directory-readiness-criteria.json`
- `docs/api-spine/practitioner-directory-consumer-contract-check.md`
- `tests/fixtures/api_spine_practitioner_directory/consumer_contract_report.json`
- `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json`

## Ariadne Integration Output

The Sprint 257 output should be a decision artifact under `docs/api-spine/`
plus guard tests. It should include:

- worker mix and lane artifacts reviewed;
- yes/no recommendation for asking Yuri to approve
  `rest_route_ready=true` for this route only;
- evidence table mapped to Sprint 255 readiness criteria;
- explicit blockers, if any;
- exact files/tests that would need to change in a later approval sprint;
- explicit statement that GraphQL, provider, memory/RAG/GraphRAG, H15/H-series,
  historical diary, write, deployment, production, and external patient-client
  gates remain false;
- pause condition requiring Yuri approval before any readiness flag flip.

## Stop Conditions

Pause instead of implementing a readiness flip if any worker or Ariadne finds:

- OpenAPI and route tests disagree;
- authn/authz/tenancy or inactive-inclusion semantics are stale or ambiguous;
- sensitive fields are exposed;
- a practitioner detail route exists unexpectedly;
- any GraphQL/provider/memory/H15/trove/write/deployment/production gate changed;
- external patient-client exposure is implied;
- rate-limit, RLS-equivalent, encryption, or deployment-surface caveats are not
  explicitly accepted as deferred internal-route gaps;
- Yuri has not explicitly approved the final readiness flag change.

## Follow-On Blocks

If Sprint 257 recommends no-go, the next block should be a blocker-closure block
with worker lanes mapped to the named blockers.

If Sprint 257 recommends go, pause for Yuri approval. Only after approval should
a later sprint update the isolated readiness snapshot and tests for
`rest_route_ready=true` while proving every adjacent gate remains false.
