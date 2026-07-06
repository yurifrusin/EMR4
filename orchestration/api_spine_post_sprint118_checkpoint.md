# Post-Sprint-118 API Spine Checkpoint

| Item | Value |
|---|---|
| Sprint | 120 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Checkpoint artifact only; no runtime route, provider, database, or schema wiring changed |
| Steward posture | Appointment-first, mixed API spine, provider-boundary gates closed |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/access_ai_api_design.md`
- `orchestration/bernie_release_gates.md`
- `docs/api-spine/graphql/appointment-diary-read.graphql`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `docs/api-spine/async/integration-events.yaml`
- `docs/api-spine/manifests/agent-capability-charters.yaml`
- `docs/api-spine/manifests/practice-onboarding-example.yaml`
- `docs/api-spine/security/permission-matrix.yaml`
- `tests/test_api_spine_artifacts.py`

## Boundary Verdict

The accepted API Spine still holds after the provider-boundary guard
consolidation:

- GraphQL remains a read/context graph only and must keep no `type Mutation`.
- REST/OpenAPI command endpoints remain the only place for irreversible,
  auditable, external, confirmation-grade, or provider-affecting actions.
- Async contracts observe or ingest typed events through authenticated
  integration principals; they do not bypass command endpoints.
- YAML manifests declare setup, policy, capability, and context-frame posture;
  typed backend code remains responsible for authorization, freshness, audit,
  and confirmation.
- Access AI remains the only intended provider invocation boundary, and the
  Bernie booking interpreter provider boundary remains default-disabled unless
  a future reviewed gate changes that posture.

## Artifact State

The current Sprint 101 prototype artifacts are still source-safe and useful:

- The GraphQL SDL exposes appointment, diary, patient, audit, directory, and
  Bernie session read models with display-only affordance hints.
- The OpenAPI draft captures appointment create/update/status/delete
  proposal-confirm command families plus slot-search normalize/search/select
  command-style reads.
- Async placeholder contracts preserve idempotency, integration principals,
  signature posture, and PHI-minimising payload examples.
- Agent capability charters keep Bernie, Davida, and Consultant inside declared
  context-frame and confirmation boundaries.
- The permission matrix stays default-deny and keeps runtime FGA clients, live
  provider runtime, external patient clients, broad historical diary trove
  mining, H15/H-series runtime imports, memory/RAG/GraphRAG runtime, GraphQL
  mutations, and model-to-database writes denied.

## Provider-Boundary Impact

Sprints 110-118 added a stronger preflight layer around any future provider
boundary proposal:

- startup settings fail closed for live Bernie interpreter providers while the
  runtime gate is blocked;
- live provider aliases are centralized and covered by metadata/readiness
  invariants;
- `scripts/bernie_provider_boundary_readiness_report.py` emits a safe aggregate
  provider-boundary posture;
- `orchestration/bernie_release_gates.md` requires that report and its
  `proposal_citation_required_fields` before provider-boundary proposals;
- `scripts/bernie_interpretation_proposal_surface_guard.py` blocks proposal
  markdown that omits required readiness commands or blocked values.

These guards support the API Spine, but they do not themselves implement the
next API surface. The next work should return to appointment-first API
alignment.

## Next Implementation Slice

Recommended Sprint 121:

**Appointment command envelope alignment inventory.**

Build a non-invasive inventory that maps current FastAPI appointment proposal,
confirmation, slot-search, and compatibility write routes to the OpenAPI command
families in `docs/api-spine/openapi/appointment-commands.yaml`.

Acceptance criteria:

- classify each current route as proposal command, confirm command,
  command-style read, compatibility write, or read-only route;
- record whether it has practice scope, actor/confirmer evidence, idempotency,
  freshness/session binding, warning/block envelope, and audit posture;
- identify the smallest next route-level alignment slice;
- keep GraphQL read-only and do not add GraphQL mutations;
- do not enable live providers, runtime FGA clients, external patient clients,
  H15/H-series runtime imports, memory/RAG/GraphRAG, broad trove mining, or
  model-to-database writes.

## Gates Still Closed

This checkpoint does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.
