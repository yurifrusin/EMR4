# External Read-Model Implementation Planning Review

Date: 2026-07-08

Sprint: 222

## Purpose

This planning review follows the combined external read-model readiness review
and blocked readiness snapshot.

It defines the minimum planning decisions required before any future sprint may
propose REST route or GraphQL resolver implementation for the external read
model gaps. It does not approve implementation and does not change the blocked
readiness verdict.

It does not add REST routes, GraphQL resolvers, GraphQL mutations, Pydantic
schemas, database queries, migrations, source manifests, provider calls, Access
AI invocation, RAG, GraphRAG, source ingestion, runtime FGA clients, external
patient clients, or write authority.

## Current Readiness Inputs

| Input | Artifact | Required current state |
|---|---|---|
| `combined_readiness_review` | `docs/api-spine/external-read-model-combined-readiness-review.md` | `blocked` decision with every readiness flag `false` |
| `blocked_readiness_snapshot` | `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json` | exact aggregate snapshot with runtime authority count `0` |
| `readiness_status_checker` | `scripts/external_read_model_readiness_status.py` | safe aggregate checker passes without route/source/payload fragments |
| `readiness_dag` | `docs/api-spine/external-read-model-readiness-dag.json` | downstream runtime gates remain `blocked` |

## Planning Verdict

| Planning area | Current state | Required before implementation proposal |
|---|---|---|
| `route_ownership` | `not_reviewed` | owner module, path family, response schema owner, and auth dependency must be selected without adding code |
| `graphql_resolver_ownership` | `not_reviewed` | resolver ownership, schema-to-REST mapping, batching/dataloader policy, and resolver authorization must be selected without adding code |
| `authorization_and_scope` | `not_reviewed` | practice scoping, patient scoping, active filters, source entitlement, role policy, and external-client exposure policy must be documented |
| `pagination_and_ordering` | `not_reviewed` | limit defaults, maximums, cursor/offset policy, deterministic ordering, and tie-breakers must be documented |
| `empty_error_unavailable_states` | `not_reviewed` | empty results, forbidden, unlicensed, expired, unavailable, malformed query, and stale-source behavior must be documented |
| `source_manifest_policy` | `blocked` | RACGP/Cochrane manifests, licence decisions, PHI policy, citation policy, storage policy, and freshness policy remain absent |
| `test_gate_plan` | `not_reviewed` | route tests, resolver tests, source-manifest tests, snapshot updates, security checks, and no-write assertions must be listed before code |

Overall decision: `blocked`.

Runtime implementation proposal ready: `false`.

Sprint engine state: `continuing`.

Pause required before runtime implementation: `true`.

## Route Planning Requirements

Before any route implementation sprint is proposed:

- each future GET path must be named in a planning artifact with owning router
  and response schema owner;
- every route must depend on authenticated user context and documented
  practice/patient/source scoping;
- response shapes must be bounded to the previously reviewed display-safe
  fields only;
- pagination, ordering, empty results, forbidden, unavailable, and validation
  errors must be designed before code;
- no route may expose provider identifiers, raw message bodies, phone numbers,
  source internal IDs, raw licensed passages, or source manifests as runtime
  configuration;
- route implementation must remain blocked until this planning review is
  replaced or extended by an explicit implementation proposal.

## Candidate Planning Sequence

If Yuri later chooses to move toward implementation, the planning-only sequence
should be:

1. Add static route/schema ownership proposals for practitioner, reminder, and
   message reads, including router owner, schema owner, auth dependency, default
   ordering, pagination default, pagination maximum, and error states.
2. Add source-manifest planning for RACGP/Cochrane before assigning any
   directory route or schema ownership.
3. Add GraphQL resolver ownership and resolver authorization mapping after REST
   or read-service ownership is reviewed.
4. Add implementation proposal tests and security review requirements before any
   runtime route, resolver, schema, query, provider, or source-manifest code is
   created.

Candidate defaults such as `default_limit=20` and `max_limit=100` may be
proposed in a later static design amendment, but they are not approved by this
review.

## GraphQL Planning Requirements

Before any GraphQL resolver implementation sprint is proposed:

- resolver ownership and REST/read-service dependencies must be selected;
- resolver authorization must be defined separately from REST route auth;
- batching or dataloader policy must be defined for patient/practice reads;
- resolver pagination and error propagation must be aligned with REST behavior;
- GraphQL mutation support must remain absent;
- resolver implementation must remain blocked until a later explicit
  implementation proposal keeps the readiness snapshot false or consciously
  replaces it through a reviewed gate.

## Test Gate Requirements

Any future implementation proposal must define tests before code for:

- auth and role denial;
- practice and patient scoping;
- active-only practitioner defaults;
- reminder date/status mapping;
- patient-message two-table union and raw-body exclusion;
- RACGP/Cochrane source manifest absent/blocked/unavailable states;
- pagination, deterministic ordering, and maximum result limits;
- GraphQL resolver parity with REST/read-service behavior;
- no provider calls, no Access AI invocation, no RAG/GraphRAG, no H15/H-series
  runtime imports, no broad trove access, and no writes;
- readiness status and blocked snapshot changes if any gate is intentionally
  altered.

## Deliberate Exclusions

This review does not map or approve:

- REST route implementation;
- GraphQL resolver or mutation implementation;
- Pydantic runtime schemas;
- database queries, indexes, migrations, source tables, caches, or sync jobs;
- RACGP or Cochrane source manifests as runtime configuration;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  browser automation, live lookup, or provider retrieval;
- provider calls, live provider gates, provider dry-run wiring, Access AI
  invocation, RAG, GraphRAG, memory, or practice-knowledge facts as directory
  authority;
- H15/H-series runtime imports or broad historical diary trove mining;
- external patient clients or runtime FGA clients;
- patient-specific clinical advice or autonomous clinical decision-making;
- reminder, message, SMS, practitioner, directory, appointment, billing, result,
  or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Closed Gates

This review does not authorize:

- adding REST routes;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- changing the blocked readiness snapshot;
- changing readiness flags to `true`;
- provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- source manifests as approved runtime configuration;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  live lookup, or sync jobs;
- reminder, message, SMS, practitioner, directory, appointment, billing, result,
  or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static implementation-planning review. It does not prove runtime
GraphQL resolver implementation, REST route authorization, source entitlement,
licence compliance, source manifest correctness, citation correctness, database
query shape, pagination, performance, deployment readiness, provider readiness,
external directory readiness, patient-facing client readiness, or production
readiness.

`tests/test_api_spine_external_read_model_implementation_planning_review.py`
validates this packet by parsing only this markdown file, the blocked readiness
snapshot, the combined readiness review, and the readiness DAG.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_implementation_planning_review.py -q
```
