# Directory Source Licensing Review

Date: 2026-07-08

Sprint: 218

## Purpose

This review packet follows
`docs/api-spine/external-router-read-model-gap-inventory.md` for the
`Query.directorySearch.RACGP_GUIDELINES` and
`Query.directorySearch.COCHRANE_LIBRARY` gaps.

It records the source and licensing prerequisites that must be satisfied before
any directory read-shape design or runtime implementation. It does not perform
live web lookup, scrape source material, ingest licensed content, call providers,
add adapters, create routes, create GraphQL resolvers, or grant write authority.

## Target Read Surfaces

| GraphQL read surface | Current gap posture | Future prerequisite | Runtime status |
|---|---|---|---|
| `Query.directorySearch.RACGP_GUIDELINES` | `source_and_licensing_gap` | reviewed local or approved cited source with source labels and permission boundary | `not_implemented` |
| `Query.directorySearch.COCHRANE_LIBRARY` | `source_and_licensing_gap` | licensing/subscription review plus approved cited local or external source | `not_implemented` |

## Current Supporting Evidence

- The GraphQL SDL reserves `DirectorySource.RACGP_GUIDELINES` and
  `DirectorySource.COCHRANE_LIBRARY` under a read-only `directorySearch` field.
- The current backend has local MBS and SNOMED-style directory models/routes,
  but no RACGP or Cochrane table, route, adapter, source manifest, sync job, or
  entitlement model.
- `app/services/ai/knowledge_base.py` defines a provider-neutral Access AI
  knowledge-base boundary for future licensed knowledge retrieval, but that
  boundary is not a directory-search source and must not be treated as directory
  implementation evidence.
- Practice-knowledge advisory facts, provider prompts, RAG, GraphRAG, and raw
  web retrieval are not approved RACGP/Cochrane directory sources.
- `orchestration/research/cochrane_cds_pipeline.md` is historical provenance
  for a Cochrane/Wiley evidence-provider investigation. It is not a source
  approval, licence approval, runtime adapter, or directory-search design.
- No equivalent RACGP-specific source/licensing vetting packet is currently
  mapped in this repository.

## Source Landscape Posture

| Source family | Current repository posture | Directory readiness |
|---|---|---|
| `RACGP_GUIDELINES` | SDL reservation plus gap inventory only; no local source manifest, contact record, access-term review, adapter, table, or route is mapped | `blocked_pending_source_manifest` |
| `COCHRANE_LIBRARY` | SDL reservation plus gap inventory; historical Cochrane/Wiley research note exists, but no licence, entitlement, adapter, table, source manifest, or route is approved | `blocked_pending_source_manifest` |
| `MBS` / `SNOMED` | local directory tables and read routes exist as separate current surfaces | not evidence for RACGP/Cochrane readiness |

## Source Review Requirements

Before a future directory read-shape design may claim either source is ready:

- the source must have an approved source type, either `local_curated_snapshot`
  or `approved_external_retrieval`, recorded in a source manifest;
- the manifest must include source labels, citation requirements, freshness or
  synchronization posture, jurisdiction notes, permitted audience, and PHI query
  policy;
- licensing/subscription review must explicitly state whether EMR4 may index,
  cache, display snippets, display citations, query live APIs, and expose
  results to clinicians, staff, or patients;
- the review must distinguish evidence retrieval from patient-specific medical
  advice and from autonomous clinical decision-making;
- any future query path must be read-only, bounded, cited, auditable, and
  denied by default when source entitlement or licence state is unknown;
- no source may be treated as approved merely because an LLM, provider adapter,
  practice knowledge entry, or web search can produce text about the topic.

## Source Manifest Minimum Fields

Any future source manifest must record, at minimum:

| Field | Requirement |
|---|---|
| `source_name` | Stable source label matching the GraphQL directory source. |
| `source_type` | One of `local_curated_snapshot` or `approved_external_retrieval` until another reviewed type is added. |
| `licence_status` | Explicitly approved, blocked, expired, unknown, or out of scope. |
| `permitted_use` | Separate booleans for read-only retrieval, local indexing, caching, embedding, snippet display, citation display, and audit metadata storage. |
| `audience_policy` | Clinician, staff, and patient visibility must be stated independently. |
| `phi_policy` | Whether PHI may be submitted, and the default must be no PHI unless explicitly approved. |
| `freshness_policy` | Source version, update cadence, sync timestamp posture, and stale-source failure behavior. |
| `citation_shape` | Required title, source label, URL or DOI when available, publication/version date when available, and evidence type when available. |
| `storage_policy` | Retrieved text, cached summary, citation metadata, and audit retention posture. |
| `regulatory_notes` | Australian privacy, cross-border disclosure, clinical-safety, and CDSS posture. |

## Completion Criteria

`directory_source_review` may be treated as a completed static prerequisite only
when:

- RACGP and Cochrane are both named with current repository posture and open
  source/licensing questions;
- a reusable source-manifest minimum field set is documented;
- Access AI knowledge-base boundaries and historical Cochrane research are
  referenced only as provenance, not runtime authority;
- practice-knowledge facts, provider prompts, RAG, GraphRAG, web retrieval, and
  H15/H-series material remain excluded as directory authority;
- the readiness DAG still has `decision: blocked`, all readiness values false,
  and downstream runtime gates blocked.

It does not mean either source is licence-approved, runtime-ready,
clinically-approved, or suitable for patient-facing exposure.

## Future Directory Design Prerequisites

A later directory read-shape design must remain blocked until this packet is
expanded into an approved source manifest or a reviewed explicit decision to
exclude the source from runtime scope.

That later design must define:

- stable directory entry IDs that do not expose licensed internal identifiers;
- code/title/summary/citation mapping for each approved source;
- citation object requirements, including source label and retrieval freshness;
- result count limits, deterministic ordering, and empty-result semantics;
- entitlement and role policy for each audience;
- storage policy for retrieved text, cached summaries, citations, and audit
  metadata;
- failure behavior when a source licence, subscription, sync, adapter, or
  provider is unavailable.

## Deliberate Exclusions

This review does not map or approve:

- RACGP or Cochrane content ingestion;
- raw web retrieval, live web search, scraping, crawling, or browser automation;
- provider prompts, provider responses, Access AI invocation, provider dry-runs,
  Bedrock, Vertex Search, Kendra, OpenSearch, or other retrieval runtime wiring;
- RAG, GraphRAG, memory, practice-knowledge facts, or H15/H-series material as
  directory authority;
- source synchronization jobs, embeddings, vector indexes, or cached passages;
- patient-specific clinical advice, autonomous clinical decision-making, or
  patient-facing clinical content;
- any appointment, reminder, message, practitioner, directory, billing, result, or clinical write authority.

## Closed Gates

This review does not authorize:

- adding a REST directory source route;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- adding source manifests as approved runtime configuration;
- provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- RACGP or Cochrane content ingestion, indexing, caching, scraping, or live
  lookup;
- appointment, reminder, message, practitioner, directory, billing, result, or clinical write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static source/licensing review packet. It does not prove runtime
GraphQL resolver implementation, REST route authorization, source entitlement,
licence compliance, citation correctness, database query shape, retrieval
quality, clinical-safety review, provider readiness, external directory
readiness, patient-facing client readiness, or deployment readiness.

`tests/test_api_spine_directory_source_licensing_review.py` validates this
packet by parsing only this markdown file, the GraphQL SDL, selected source
files, and the external read-model gap inventory.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_directory_source_licensing_review.py -q
```
