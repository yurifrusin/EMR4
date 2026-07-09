# DeepSeek Sprint 278 Office Add-in GraphQL Switch Runtime Review

Verdict: PASS with cautions integrated.

DeepSeek reviewed the pre-implementation state and flagged that approval needed
to be recorded before runtime edits. Sprint 278 records Yuri's approval in the
switch packet before implementing the default-off switch.

Integrated cautions:

- Runtime GraphQL traffic remains blocked by default.
- The implementation uses the existing REST path when disabled.
- The GraphQL query requests only the approved projection.
- GraphQL body errors and non-401 transport errors fall back to REST.
- HTTP `401` keeps the existing auth/logout behavior.
- `roleLabel` and `active` are preserved in normalized rows.
- malformed rows without `id` or `displayName` are dropped by the existing
  normalizer filter.
- No backend, schema, readiness, telemetry, provider, memory, H15/trove, write,
  audit-write, mutation, subscription, deployment, production, external-client,
  or field-expansion gate is opened.
