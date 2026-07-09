# plan-claude-claude-sprint257-practitioner-readiness-veto

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint257-practitioner-readiness-veto` |
| Status | pending_plan_review |
| Created | 2026-07-09 13:34 +1000 |
| Source HEAD | `1644c978` |

## Plan Summary

Read-only readiness/safety veto review of GET /api/v1/practice/practitioners: decide whether there is enough evidence to ask Yuri for rest_route_ready=true, mapping findings to the Sprint 255 criteria and naming any blockers. No app code, fixtures, tests, or readiness flags change.

## My Understanding

Sprints 254-256 implemented a bounded REST first slice (route+schema+read service+25 runtime tests) and refreshed evidence, but rest_route_ready stays false by design. Sprint 255 defined 13 required_before_true criteria and a separate-Yuri-approval-payload requirement; Sprint 256 recorded an OpenAPI/consumer contract check. My job is an independent go/no-go veto: does current evidence satisfy every Sprint 255 criterion, and are there safety implications, before anyone asks Yuri to flip the flag. This is a safety veto lane, not an approval lane.

## Intended Surface / Boundary

Review/analysis only. Affected surface is a single new review packet under orchestration/agent_inbox/codex/. No runtime surface (route, schema, service), no readiness JSON, no tests, no fixtures, no snapshot, no GraphQL/SDL, no provider/memory/RAG/GraphRAG, no H15/H-series, no deployment or production docs are touched. Nearby readiness fixtures (blocked_readiness_status.json, approved-gate.json, readiness-criteria.json) must NOT change.

## Out Of Scope

Editing route/schema/service code; editing readiness fixtures or the criteria/gate/review JSON; editing tests; approving or flipping rest_route_ready or any readiness flag; GraphQL/SDL; provider/Access-AI/memory/RAG/GraphRAG wiring; H15/H-series/historical-diary material; deployment/production config; external patient client exposure; write authority.

## Files I Expect To Edit

orchestration/agent_inbox/codex/ (one new review packet only, created at submit time). No other files edited. Reading only: docs/api-spine/practitioner-directory-readiness-criteria.json, practitioner-directory-runtime-evidence-refresh.json, practitioner-directory-post-implementation-readiness-review.json, practitioner-directory-approved-gate.json, practitioner-directory-consumer-contract-check.md, app/routers/practice.py, app/schemas/practice.py, app/services/practice/practitioner_directory_read.py, tests/test_practitioner_directory_route.py.

## Implementation Steps

1) Re-read the five readiness artifacts, route, schema, read service, and test file (done during planning). 2) Build a criterion-by-criterion table over the 13 Sprint 255 required_before_true keys, marking each satisfied / partially-satisfied / missing with the concrete evidence or gap. 3) Separately assess safety implications: authn/authz/tenancy fail-closed behaviour, anti-enumeration (no detail route, no existence leak), sensitive-field exclusion, pagination/error contract, and the must_remain_false non-REST flags. 4) Note items that are structurally recorded vs items that require an explicit human/deployment decision (rate-limit deferral, deployment surface naming, RLS gap, field-encryption gap, external-client exposure, and the separate Yuri approval payload existence). 5) Write an explicit go/no-go recommendation with exact blockers, without implying readiness approval. 6) Fill Completion Notes and submit the packet via the packet submit command.

## Visual / Behavioural Acceptance Checks

Packet gives one explicit go/no-go recommendation; every Sprint 255 required_before_true criterion is mapped to satisfied/partial/missing with evidence; blockers (or a clear no-blockers statement) are named; no wording implies rest_route_ready approval; git status shows only the new codex review packet added, no runtime/test/fixture changes. No visually-loaded UI surfaces (cards, slots, diary grid, waiting room, status) are involved.

## Risks / Ambiguities

1) Ambiguity: some criteria (deployment_surface_explicitly_named, rate_limit decision, RLS/field-encryption gap recorded, separate_yuri_approval_payload_exists) are decision/record artifacts I must confirm exist rather than judge technically; if the recording artifact is absent that is itself a blocker. 2) Risk of scope creep into recommending fixes/edits — I will stay review-only. 3) Risk of implying approval — I will phrase strictly as veto/go-no-go input, leaving the flip to a separate Yuri approval packet.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
