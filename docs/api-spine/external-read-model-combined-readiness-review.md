# External Read-Model Combined Readiness Review

Date: 2026-07-08

Sprint: 220

## Purpose

This review combines the static external read-model gap inventory, aggregate
gap status checker, read-shape design packets, source/licensing review, and
readiness DAG.

It is a non-runtime checkpoint. It does not add REST routes, GraphQL resolvers,
GraphQL mutations, Pydantic schemas, database queries, provider calls, Access AI
invocation, RAG, GraphRAG, source ingestion, runtime FGA clients, external
patient clients, or write authority.

## Reviewed Prerequisites

| Prerequisite node | Artifact | Review posture |
|---|---|---|
| `external_gap_inventory` | `docs/api-spine/external-router-read-model-gap-inventory.md` | `static_complete` |
| `external_gap_status_checker` | `scripts/external_read_model_gap_status.py` | `static_complete` |
| `practitioner_directory_design` | `docs/api-spine/practitioner-directory-read-shape-design.md` | `design_complete_no_runtime` |
| `patient_reminders_design` | `docs/api-spine/patient-reminders-read-shape-design.md` | `design_complete_no_runtime` |
| `patient_messages_design` | `docs/api-spine/patient-messages-read-shape-design.md` | `design_complete_no_runtime` |
| `directory_source_review` | `docs/api-spine/directory-source-licensing-review.md` | `static_complete` |
| `directory_read_shape_design` | `docs/api-spine/directory-read-shape-design.md` | `design_complete_no_runtime` |

## Combined Verdict

| Readiness field | Value | Reason |
|---|---|---|
| `external_read_model_runtime_ready` | `false` | static packets are complete, but no runtime implementation, authorization, pagination, query, source-manifest, or deployment review exists |
| `graphql_resolver_ready` | `false` | no resolver ownership, authorization policy, dataloader/query plan, pagination contract, or GraphQL integration test exists |
| `rest_route_ready` | `false` | no reviewed route paths, response schemas, auth dependencies, query plans, or endpoint tests exist |
| `provider_or_directory_runtime_ready` | `false` | RACGP/Cochrane source manifests, licence decisions, provider/runtime adapters, and external-client policies remain absent |
| `runtime_or_memory_ready` | `false` | memory, RAG, GraphRAG, H15/H-series runtime import, and practice-knowledge-as-directory-authority gates remain closed |
| `write_authority_ready` | `false` | these surfaces are read-only and do not authorize reminder, message, SMS, practitioner, directory, appointment, billing, result, or clinical writes |
| `raw_compat_mode_change_ready` | `false` | raw compatibility deprecation mode changes are outside this review and remain blocked |

Overall decision: `blocked`.

Sprint engine state: `continuing`.

Pause required: `false`.

## Still-Blocked Runtime Gates

The static design/source packet chain is complete enough to support a later
implementation planning review, not runtime implementation.

Before any runtime work begins, a future sprint must add explicit reviewed
implementation criteria for:

- REST route paths, response schemas, auth dependencies, patient/practice
  scoping, ordering, pagination, and empty/error states;
- GraphQL resolver ownership, resolver authorization, batching/query plan,
  pagination, and resolver-level tests;
- RACGP/Cochrane source manifests, licence decisions, entitlement posture,
  citation policy, PHI policy, storage policy, freshness policy, and unavailable
  state behavior;
- provider/runtime boundaries if any approved source uses external retrieval;
- security review for patient-facing and external-client exposure;
- migration/deployment readiness if any source table, cache, or sync job is
  introduced.

## Deliberate Exclusions

This review does not map or approve:

- REST route implementation;
- GraphQL resolver or mutation implementation;
- Pydantic runtime schemas;
- database queries, query optimization, indexes, migrations, source tables, or
  sync jobs;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  browser automation, live lookup, or source manifests as runtime configuration;
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
- provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  live lookup, or sync jobs;
- source manifests as approved runtime configuration;
- reminder, message, SMS, practitioner, directory, appointment, billing, result,
  or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static combined readiness review. It does not prove runtime GraphQL
resolver implementation, REST route authorization, source entitlement, licence
compliance, source manifest correctness, citation correctness, database query
shape, pagination, performance, deployment readiness, provider readiness,
external directory readiness, patient-facing client readiness, or production
readiness.

`tests/test_api_spine_external_read_model_combined_readiness_review.py`
validates this packet by parsing only this markdown file, the readiness DAG,
the safe aggregate gap status checker, and the referenced static artifacts.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_external_read_model_combined_readiness_review.py -q
```
