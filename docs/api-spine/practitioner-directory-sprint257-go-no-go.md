# Practitioner Directory Sprint 257 Go/No-Go

Date: 2026-07-09

Sprint: 257

Decision:
`no_go_blocker_closure_required_before_readiness_approval_request`.

Target route:

`GET /api/v1/practice/practitioners`

Target readiness flag:

`rest_route_ready`

The readiness value remains false after this sprint. This packet does not
approve, request, or implement a readiness-flag flip.

## Worker Lanes

Sprint 257 used worker lanes as distinct evidence producers rather than as a
start-of-sprint ritual.

| Lane | Role | Artifact | Recommendation |
|---|---|---|---|
| Claude | readiness/safety veto | `orchestration/agent_inbox/codex/review-claude-sprint257-practitioner-readiness-veto.md` | no-go |
| Antigravity | consumer/API boundary review | `orchestration/agent_inbox/codex/codex-sprint257-antigravity-practitioner-consumer-boundary.md` | pass for internal consumer contract |
| DeepSeek | mechanical static sweep | direct `deepseek-worker` lane Delta plus Ariadne grep verification | no mechanical blockers |

The disagreement is useful. Antigravity found the consumer-facing route shape
sound for internal staff consumers. Claude found that the current evidence does
not yet satisfy the stricter Sprint 255 criteria for asking Yuri to approve
`rest_route_ready=true`. Ariadne adopts the stricter conclusion.

## Criteria Outcome

The implementation and direct route security posture are strong:
authentication, role gating, same-practice tenancy filtering,
anti-enumeration, sensitive-field exclusion, pagination bounds, and read-only
behavior are all covered by source/tests and worker review.

The readiness-approval request is not ready because these items remain missing
or incomplete:

- committed isolated runtime route test pass record;
- committed API-spine artifact test pass record;
- rate-limit or deferred-rate-limit decision;
- deployment surface naming;
- practitioner-directory-specific RLS or RLS-equivalent gap record;
- practitioner-directory-specific field-encryption gap record;
- explicit external-client scope decision;
- separate Yuri approval payload for `rest_route_ready=true`.

The existing `practitioner-directory-approved-gate.json` approved the REST first
implementation slice only. It did not approve a readiness flag change.

## Mechanical Verification Notes

Ariadne ran static sweeps during integration. The readiness-flag grep found only
documentation, tests, and task-packet references to possible future
`rest_route_ready=true`; no committed readiness fixture currently sets the flag
true. The detail-route grep found only documentation/test guard references to
`GET /api/v1/practice/practitioners/{id}`; no implemented detail route was
found. Sensitive-field hits were confined to route tests and fixtures that
prove exclusion, not to `PractitionerOut`. Provider, Access AI, RAG, GraphRAG,
H15/H-series, historical diary, `local_data`, write, audit, and idempotency
hits were confined to tests that prove absence of those surfaces for this
route.

## Closed Scope

The following remain false and out of scope:

- `rest_route_ready`;
- `graphql_resolver_ready`;
- `external_read_model_runtime_ready`;
- `runtime_or_memory_ready`;
- `provider_or_directory_runtime_ready`;
- `write_authority_ready`;
- `deployment_ready`;
- `production_ready`;
- `external_patient_client_ready`.

No route, schema, read-service, SDL, GraphQL resolver, provider, Access AI,
memory/RAG/GraphRAG, H15/H-series, historical diary, external patient client,
write, deployment, or production gate changed in this sprint.

## Next Block

The next safe block is Sprint 258: close the missing readiness evidence and gap
records without creating a Yuri approval payload or flipping readiness. After
that, a separate sprint may draft a `rest_route_ready=true` approval payload for
Yuri, but the flag must not change without explicit approval.
