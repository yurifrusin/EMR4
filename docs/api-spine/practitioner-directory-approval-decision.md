# Practitioner Directory REST Route Approval Decision

Date: 2026-07-08

Status: approved for REST first slice only

Decision authority: Yuri

## Purpose

This packet records Yuri's go/no-go decision for:

```text
GET /api/v1/practice/practitioners
```

The original companion draft JSON remains as the pre-approval decision surface:

```text
docs/api-spine/practitioner-directory-approval-payload-draft.json
```

Yuri approved the REST first slice on 2026-07-08. The committed approved gate is:

```text
docs/api-spine/practitioner-directory-approved-gate.json
```

The approved gate has `decision: approved_for_rest_route_first_slice`,
`reviewer: yuri`, `go_no_go_acknowledged: true`,
`approval_expires_on: 2027-07-01`, and
`approved_contract_commit: ce23212d538fbba24e5061def2142b817d5528ad`.

## Evidence Checklist Before Implementation

Before runtime code is written, the route implementation sprint must verify:

1. `docs/api-spine/practitioner-directory-read-shape-design.md` exists.
2. `docs/api-spine/practitioner-directory-route-schema-ownership-candidate.md`
   remains candidate/evidence only.
3. `docs/api-spine/practitioner-directory-first-runtime-implementation-proposal.md`
   defines the first REST route gate.
4. `docs/api-spine/practitioner-directory-graphql-resolver-ownership-plan.md`
   keeps GraphQL sequenced after REST and a shared read service.
5. `docs/api-spine/practitioner-directory-rest-graphql-drift-contract.md`
   records canonical projection and known blocked drift.
6. `docs/api-spine/practitioner-directory-security-audit-test-harness-preflight.md`
   defines authn/authz, tenancy, anti-enumeration, audit, and no-write/provider
   checks.
7. `docs/api-spine/practitioner-directory-sdl-pagination-default-location-resolution-proposal.md`
   defines the later SDL convergence path.
8. `docs/api-spine/practitioner-directory-route-implementation-breakdown-readiness-decision.md`
   defines Slices A-D and the pre-code stop/go points.
9. `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json`
   still has `dag_decision: blocked`, `approval_gate_decision:
   approved_for_rest_route_first_slice`, and readiness flags false.
10. Current production source still has no practitioner directory route, schema,
    shared read service, GraphQL resolver, SDL edit, provider call, memory/RAG/
    GraphRAG wiring, H15/H-series runtime import, or readiness flag change.

## Approved Scope

This approval allows only the Sprint 232 REST first slice:

- directory response schemas in `app/schemas/practice.py`;
- shared read service in `app/services/practice/practitioner_directory_read.py`;
- REST route and mount for `GET /api/v1/practice/practitioners`;
- runtime tests covering the Sprint 227 and Sprint 230 matrices.

It still forbids:

- SDL changes, including `PracticeLocationBrief`;
- GraphQL runtime dependencies, resolvers, or mutations;
- readiness flag changes;
- deployment or production-readiness claims;
- provider calls or live-provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- practitioner create/update/delete/onboarding commands;
- appointment, roster, schedule, diary, billing, result, reminder, message, SMS,
  or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Decision Consequences

| Decision | Consequence |
|---|---|
| `blocked` | Historical pre-approval default. No route, schema, service, SDL, GraphQL, readiness, provider, memory, or database code is authorized. |
| `approved_for_rest_route_first_slice` | Current decision. Authorizes only Sprint 232 Slice A-D: schemas, shared read service, REST route/mount, and runtime tests. All SDL, GraphQL, provider, memory, write, deployment, and readiness flag gates remain closed. |
| `deferred` | No code change is permitted. Planning may continue or the sprint engine may wait for a later decision checkpoint. |
| `rejected` | No code change is permitted. The route attempt leaves the active implementation queue until a new reviewed proposal supersedes this gate. |
| `expired` | No further route work is permitted until pre-code checks are refreshed and Yuri records a new explicit decision. |

## Approval Payload Applied

The approval patch:

- add `docs/api-spine/practitioner-directory-approved-gate.json`;
- set `decision` to `approved_for_rest_route_first_slice`;
- set `approval.reviewer` to `yuri`;
- set `approval.go_no_go_acknowledged` to `true`;
- set `approval.approval_expires_on` to `2027-07-01`;
- set `approval.approved_contract_commit` to
  `ce23212d538fbba24e5061def2142b817d5528ad`;
- keep every non-REST-first-slice scope field false;
- keep `readiness_flag_changes_allowed` false;
- keep `deployment_or_production_readiness_allowed` false.

No further scope expansion is approved by this patch.

## Boundary

This is a static approval decision for the first REST implementation slice. It
does not prove runtime REST authorization, route correctness, database query
correctness, field-level authorization, audit implementation, SDL correctness
after edit, GraphQL authorization, resolver correctness, RLS, field encryption,
rate limiting, pagination performance, deployment readiness, provider
readiness, external directory readiness, patient-facing client readiness, or
production readiness.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_approval_gate_static.py -q
```
