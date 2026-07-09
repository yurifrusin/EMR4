# plan-antigravity-antigravity-sprint257-practitioner-consumer-boundary

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint257-practitioner-consumer-boundary` |
| Status | pending_plan_review |
| Created | 2026-07-09 13:34 +1000 |
| Source HEAD | `1644c978` |

## Plan Summary

Read-only implementation plan for antigravity-sprint257-practitioner-consumer-boundary task. This plan describes the objectives, scope, and non-intrusive steps for a static boundary review of the GET /api/v1/practice/practitioners endpoint to ensure it meets OpenAPI, query default, and sensitive-field isolation requirements, with zero changes to production code or readiness flags.

## My Understanding

The practitioner directory REST route GET /api/v1/practice/practitioners has been implemented but remains behind the rest_route_ready=false flag. As the Antigravity worker, my role is to perform a consumer-fit, OpenAPI schema, and external-client boundary review to evaluate whether the API shape, default values, bounds, and response properties conform to internal consumer requirements without exposing any data to external client packages or public surfaces.

## Intended Surface / Boundary

The review surface covers app/routers/practice.py, app/schemas/practice.py, app/services/practice/practitioner_directory_read.py, and the corresponding unit tests in tests/test_practitioner_directory_route.py. It also evaluates the contract report in tests/fixtures/api_spine_practitioner_directory/consumer_contract_report.json. The adjacent surfaces (such as GraphQL resolver, provider client, memory/RAG/GraphRAG module, and diary write command routes) must remain completely untouched and isolated.

## Out Of Scope

Modifying rest_route_ready to true or editing any application router/service/schema code, SQL models, or migrations. Editing test files or test fixtures (specifically tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json). Wiring or introducing GraphQL mutations, external providers (live or dry-run), Access AI, or H15/H-series runtime imports.

## Files I Expect To Edit

None in the application space. The only output file is the review packet under orchestration/agent_inbox/codex/codex-sprint257-antigravity-practitioner-consumer-boundary.md.

## Implementation Steps

1. Execute python scripts/agent_worktrees.py handin --agent antigravity (Done).
2. Write and submit this implementation plan via agent_worktrees.py plan (This step).
3. Conduct a static analysis of GET /api/v1/practice/practitioners and its corresponding schemas/services.
4. Verify query parameters (e.g., bounds, defaults) and response schema (e.g., activeOnly, limit, offset, presence of sensitive fields like AHPRA, HPI-I, provider numbers).
5. Run existing route tests to verify correctness and check if they match OpenAPI declarations.
6. Write a comprehensive review packet and save it to orchestration/agent_inbox/codex/codex-sprint257-antigravity-practitioner-consumer-boundary.md detailing pass/fail status, contract ambiguities, and external non-exposure verification.
7. Run git status to verify no modified application code exists, then submit the task packet via agent_worktrees.py submit.

## Visual / Behavioural Acceptance Checks

This is a read-only review, so no visual UI changes or behavioral changes will occur. The acceptance check is that the review packet contains a detailed assessment of the API shape, query default constraints, sensitive-field absence, and external-client non-exposure boundaries, and that all readiness tests continue to pass.

## Risks / Ambiguities

The key risk is ensuring that we do not inadvertently modify any code or flip the readiness flags (such as rest_route_ready). We must ensure that the review packet clearly separates contract evaluation from any permission to flip the readiness flag, which is strictly governed by Yuri's approval.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
