# Practitioner Directory REST Route Approval Decision Draft

Date: 2026-07-08

Status: draft only; practitioner-directory route implementation remains blocked

Decision authority: Yuri

## Purpose

This packet gives Yuri a concrete decision surface for the future go/no-go on:

```text
GET /api/v1/practice/practitioners
```

It is not approval. The companion JSON keeps `decision` as `blocked`, keeps
`approval.go_no_go_acknowledged` false, and leaves `approval.reviewer`,
`approval.approval_expires_on`, and `approval.approved_contract_commit` blank:

```text
docs/api-spine/practitioner-directory-approval-payload-draft.json
```

There is deliberately no approved gate file yet:

```text
docs/api-spine/practitioner-directory-approved-gate.json
```

That file may exist only after Yuri explicitly instructs Ariadne to approve the
REST first slice.

## Evidence Checklist Before Approval

Before the JSON can be converted from draft to approved, the route approval
decision must verify:

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
   still has `dag_decision: blocked` and readiness flags false.
10. Current production source still has no practitioner directory route, schema,
    shared read service, GraphQL resolver, SDL edit, provider call, memory/RAG/
    GraphRAG wiring, H15/H-series runtime import, or readiness flag change.

## Proposed Scope If Yuri Approves Later

The proposed future approval would allow only the Sprint 232 REST first slice:

- directory response schemas in `app/schemas/practice.py`;
- shared read service in `app/services/practice/practitioner_directory_read.py`;
- REST route and mount for `GET /api/v1/practice/practitioners`;
- runtime tests covering the Sprint 227 and Sprint 230 matrices.

It would still forbid:

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
| `blocked` | Default state. No route, schema, service, SDL, GraphQL, readiness, provider, memory, or database code is authorized. |
| `approved_for_rest_route_first_slice` | Authorizes only Sprint 232 Slice A-D: schemas, shared read service, REST route/mount, and runtime tests. All SDL, GraphQL, provider, memory, write, deployment, and readiness flag gates remain closed. |
| `deferred` | No code change is permitted. Planning may continue or the sprint engine may wait for a later decision checkpoint. |
| `rejected` | No code change is permitted. The route attempt leaves the active implementation queue until a new reviewed proposal supersedes this gate. |
| `expired` | No further route work is permitted until pre-code checks are refreshed and Yuri records a new explicit decision. |

## Manual Decision Required

If Yuri approves later, the approval patch should:

- add `docs/api-spine/practitioner-directory-approved-gate.json`;
- change `decision` to `approved_for_rest_route_first_slice`;
- set `approval.reviewer` to `yuri`;
- set `approval.go_no_go_acknowledged` to `true`;
- set `approval.approval_expires_on` to a reviewed `YYYY-MM-DD` date;
- set `approval.approved_contract_commit` to the reviewed contract commit hash;
- keep every non-REST-first-slice scope field false;
- keep `readiness_flag_changes_allowed` false;
- keep `deployment_or_production_readiness_allowed` false.

No agent should make that approval patch without Yuri explicitly instructing it
to approve this route.

## Boundary

This is a static approval-decision draft. It proves only that the route has a
reviewable future decision surface. It does not prove runtime REST
authorization, route correctness, database query correctness, field-level
authorization, audit implementation, SDL correctness after edit, GraphQL
authorization, resolver correctness, RLS, field encryption, rate limiting,
pagination performance, deployment readiness, provider readiness, external
directory readiness, patient-facing client readiness, production readiness, or
Yuri approval.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_approval_gate_static.py -q
```
