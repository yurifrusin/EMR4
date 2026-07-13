# S11 DeepSeek Flash - Confirmation Contract Matrix

Implement only a new deterministic test module that derives a compact matrix
over the existing five REST appointment confirmation handlers. Assert existing
Idempotency-Key binding, operation/family constants, request-body idempotency
binding, audit completion linkage, and exclusion of proposal-only/raw
compatibility routes. Do not edit production code, schemas, OpenAPI, models,
migrations, policies, or existing tests. Do not issue HTTP commands or writes.

Run the new test plus `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py`,
`tests/test_api_spine_appointment_idempotency_route_integration_preflight.py`,
and `tests/test_api_spine_artifacts.py`. Commit candidate changes only and write
`orchestration/agent_inbox/codex/review-deepseek-s11-confirmation-contract-matrix.md`
with SHA, tests, scope, and `STATUS: complete`.
