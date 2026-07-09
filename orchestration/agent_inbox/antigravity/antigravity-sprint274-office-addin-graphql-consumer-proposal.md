# Antigravity Sprint 274 Office Add-in GraphQL Consumer Proposal Review

Verdict: PASS.

Antigravity reviewed the proposal-only migration boundary for the Office add-in
practitioner selector from REST to `Query.practice.practitioners`.

Integrated guardrails:

- Keep Sprint 274 proposal-only: no runtime traffic switch, no UI change, no
  schema change, and no database write.
- Treat HTTP transport failures separately from GraphQL response-body failures.
  The existing REST-style HTTP `401` path can log out; GraphQL `FORBIDDEN` and
  `BAD_USER_INPUT` should be consumer-layer failures.
- Future comparison mode should render from REST while using GraphQL only to
  detect structural drift.
- Future fallback must keep clinician workflow stable; `defaultLocation: null`
  should render as an empty location rather than fail the row.
- Future user-visible copy must avoid raw GraphQL, resolver, endpoint, or
  database strings.
- The client query must request only the approved projection:
  `id`, `displayName`, `roleLabel`, `active`, and
  `defaultLocation { id name }`.
- Any future runtime flag must default false and respect the 2026-08-06 expiry.

Open questions resolved by Ariadne for Sprint 274:

- Do not propose extending the 2026-08-06 approval window in this sprint.
- Do not add client telemetry or a logging endpoint in this sprint; keep
  comparison telemetry out of runtime until separately approved.
