# Directory Read-Shape Design

Date: 2026-07-08

Sprint: 219

## Purpose

This design packet follows
`docs/api-spine/directory-source-licensing-review.md` for the reserved
`Query.directorySearch` RACGP and Cochrane surfaces.

It defines a future read-shape contract only. It does not approve a source
manifest, ingest RACGP or Cochrane content, add a REST route, create a GraphQL
resolver, add Pydantic schemas, call providers, invoke Access AI, use RAG or
GraphRAG, query live sources, scrape web pages, or grant write authority.

## Target Read Surfaces

| GraphQL read surface | Current prerequisite posture | Future REST read shape | Runtime status |
|---|---|---|---|
| `Query.directorySearch(query: String!, source: RACGP_GUIDELINES, limit: Int = 10)` | `source_review_complete_source_manifest_blocked` | `GET /api/v1/directory/search?source=RACGP_GUIDELINES` or equivalent read-only cited directory route | `not_implemented` |
| `Query.directorySearch(query: String!, source: COCHRANE_LIBRARY, limit: Int = 10)` | `source_review_complete_source_manifest_blocked` | `GET /api/v1/directory/search?source=COCHRANE_LIBRARY` or equivalent read-only cited directory route | `not_implemented` |

## Display-Safe Field Mapping

| GraphQL field | Future source | Mapping posture | Notes |
|---|---|---|---|
| `DirectorySearchResult.source` | request `DirectorySource` plus approved source manifest | `manifest_required` | Must echo only an approved source enum; current RACGP/Cochrane manifests do not exist, so runtime must remain unavailable. |
| `DirectorySearchResult.query` | normalized user query | `sanitize_required` | Must be bounded, logged safely, and denied by default when PHI submission is not approved by the source manifest. |
| `DirectorySearchResult.items` | approved local curated snapshot or approved external retrieval result | `source_manifest_required` | Empty or unavailable semantics must be defined before runtime; no provider, web, RAG, or practice-knowledge fallback is allowed. |
| `DirectorySearchResult.evidenceMode` | source manifest evidence policy | `manifest_policy_default` | `MANIFEST_POLICY` is the design-time default for approved local/cited source manifests; any `LIVE_API_FACT` posture needs a separate runtime review. |
| `DirectoryEntry.id` | synthetic stable directory ID | `synthetic_id_required` | Must not expose licensed internal IDs, source document IDs, provider IDs, or raw retrieval keys. |
| `DirectoryEntry.code` | approved source code, guideline code, or null | `optional_map` | May be null when the source does not expose a display-safe code. |
| `DirectoryEntry.title` | approved source title metadata | `citation_required` | Must be display-safe and citation-backed. |
| `DirectoryEntry.summary` | approved snippet or curated summary | `bounded_summary_required` | Must obey licence, snippet, cache, and audience policy; raw retrieved text is not automatically display-safe. |
| `DirectoryEntry.citation` | approved citation metadata | `citation_required` | Required by policy even though SDL marks it nullable; null should only be allowed for blocked/unavailable results with no items. |
| `Citation.title` | approved citation title | `citation_required` | Must identify the cited source item without embedding raw licensed passages. |
| `Citation.url` | approved source URL or null | `optional_map` | URL may be null if licence or source policy forbids display. |
| `Citation.accessedAt` | retrieval or snapshot timestamp | `freshness_required` | Must come from source manifest or retrieval metadata, not from caller clock alone. |

## Current Supporting Evidence

- `DirectorySearchResult`, `DirectoryEntry`, `Citation`, `DirectorySource`, and
  `EvidenceMode` are reserved in the GraphQL SDL.
- `DirectorySource.RACGP_GUIDELINES` and
  `DirectorySource.COCHRANE_LIBRARY` are reserved enum values, but no approved
  source manifests, routes, adapters, tables, sync jobs, or entitlement models
  exist for them.
- The source/licensing review defines source-manifest minimum fields and
  completion criteria for static review only. It explicitly does not approve
  either source for runtime, licence, clinical, or patient-facing use.
- Existing MBS/SNOMED local directory reads are separate source families and do
  not prove RACGP or Cochrane readiness.
- Access AI knowledge-base contracts and historical Cochrane/Wiley notes remain
  provenance only, not `Query.directorySearch` implementation evidence.

## Known Shape Gaps

- No source manifest exists for RACGP or Cochrane.
- No licensing decision records whether EMR4 may index, cache, embed, display
  snippets, store citations, query live APIs, or expose results by audience.
- No route path, response schema, pagination model, empty-result shape, error
  shape, or entitlement policy is implemented.
- `Citation` lacks fields for source label, evidence type, publication date,
  DOI, licence scope, and version; a future schema revision may be needed
  before clinical use.
- `EvidenceMode.MANIFEST_POLICY` can describe a curated manifest-backed result,
  but it is not proof of source entitlement or clinical safety.
- `EvidenceMode.LIVE_API_FACT` would imply a live source path and must remain
  unavailable until a separate runtime/provider review is approved.
- Query PHI policy is unresolved; the safe default is to deny PHI-bearing
  directory queries for both RACGP and Cochrane.
- Summary text cannot be designed as raw retrieved passages until licence,
  snippet, caching, and audit policies are approved.

## Future Route Requirements

Before any implementation sprint may add RACGP/Cochrane directory reads:

- the route must be a read-only GET surface under an explicitly reviewed path;
- the route must depend on authenticated user and practice context, but must not
  expose patient identity or accept PHI unless a source manifest explicitly
  approves it;
- source enum handling must deny unknown, unmanifested, expired, blocked, or
  out-of-scope source manifests by default;
- results must include only `source`, sanitized `query`, bounded `items`, and
  `evidenceMode`, with each item limited to `id`, optional `code`, `title`,
  bounded `summary`, and `citation`;
- citation-backed results must include title and freshness metadata; URL may be
  absent when source policy requires it;
- stable IDs must be synthetic and must not expose licensed internal identifiers
  or retrieval provider keys;
- result count must honor the requested `limit` only within a reviewed maximum;
- ordering must be deterministic and source-defined or relevance-defined with
  documented tie-breakers;
- empty, blocked, unlicensed, expired, and unavailable states must be explicit
  and must not silently fall back to LLM text, practice knowledge, RAG, GraphRAG,
  or raw web search;
- the route must not be used as provider, RAG, GraphRAG, Access AI, clinical
  decision-making, patient-facing advice, or external patient-client authority.

## Closed Gates

This design does not authorize:

- adding a REST directory search route;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- approving source manifests as runtime configuration;
- RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping,
  live lookup, or sync jobs;
- provider calls or live provider gates;
- provider dry-run wiring;
- Access AI invocation wiring;
- memory/RAG/GraphRAG runtime wiring;
- practice-knowledge facts as directory authority;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- broad historical diary trove mining;
- patient-specific clinical advice or autonomous clinical decision-making;
- appointment, reminder, message, practitioner, directory, billing, result, or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static read-shape design packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, source entitlement, licence
compliance, source manifest correctness, citation correctness, database query
shape, retrieval quality, clinical-safety review, provider readiness, external
directory readiness, patient-facing client readiness, or deployment readiness.

`tests/test_api_spine_directory_read_shape_design.py` validates this packet by
parsing only this markdown file, the GraphQL SDL, the source/licensing review,
the external read-model gap inventory, selected source files, and the readiness
DAG.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_directory_read_shape_design.py -q
```
