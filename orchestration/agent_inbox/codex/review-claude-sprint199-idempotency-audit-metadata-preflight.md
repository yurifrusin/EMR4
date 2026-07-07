# Claude Review - Sprint 199 Idempotency/Audit Metadata Preflight

Claude reviewed the appointment command OpenAPI artifact, API Spine ADR, Diary
route contract, and existing route/API Spine tests.

Recommendation:

- Add one import-free YAML structural pytest module over
  `docs/api-spine/openapi/appointment-commands.yaml`.
- Assert appointment proposal and confirmation command paths carry
  `Idempotency-Key` and `X-Correlation-Id`.
- Assert slot-search command-style read paths carry `X-Correlation-Id` but not
  `Idempotency-Key`.
- Assert `AuditIntent`, `FreshnessRef`, `SignedConfirmationEvidence`,
  confirmation command schemas, and `ConfirmationAuditEvent` preserve the fields
  needed for idempotency/audit linkage.
- Keep the preflight documentation-only and do not import `app.main`, routers, or
  handlers.

Risks called out:

- Flat text checks can miss per-path drift; the new guard should be structural.
- Runtime idempotency enforcement and durable audit writes remain separate
  blocked gates.
- Do not require idempotency on non-mutating slot-search reads.
