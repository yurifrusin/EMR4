# Practitioner Directory Route Readiness Consumer Boundary

Decision:
`route_scoped_readiness_status_may_feed_static_release_checks_only`.

The Sprint 260 route-scoped readiness status may be consumed by static review
and release-check surfaces only. It must not become runtime behavior.

## Allowed Consumers

- `docs/api-spine` review packets;
- orchestration sprint closeout and integration logs;
- static CI or pytest release-gate checks that emit aggregate readiness status;
- developer-facing release readiness summaries.

## Forbidden Consumers

- production app routers or services;
- provider, Access AI, memory, RAG, or GraphRAG code;
- Office add-in runtime UI decisions;
- deployment or production configuration;
- external patient-client enablement;
- global external-readiness DAG or `blocked_readiness_status.json` mutation;
- appointment or practitioner write authority.

## Runtime Rule

Runtime app code under `app/` must not import
`scripts.practitioner_directory_route_readiness_status` or read
`tests/fixtures/api_spine_external_readiness/practitioner_directory_route_readiness_status.json`.

This preserves the intended split: the route has a reviewed readiness approval
for authenticated internal-staff read use, while broader external-readiness,
GraphQL, provider, memory, write, deployment, production, and patient-client
gates remain closed.
