# DeepSeek Review - Sprint 284 Default-On Rollback Packet

Verdict: BLOCK, then integrated.

DeepSeek reviewed the Sprint 284 rollback packet for the already default-on
Office add-in practitioner selector GraphQL path.

## Blocking Finding

The original `post_rollback_validation.required_commands` listed current
default-on baseline tests, including route-intercepted and static runtime suites
that assert `const ENABLE_GRAPHQL_PRACTITIONERS = true;`.

Those commands are correct for today's pre-rollback state but would fail after
the packet's own proposed one-line rollback to
`const ENABLE_GRAPHQL_PRACTITIONERS = false;`.

## Integrated Fix

- Replaced the post-rollback validation command list with rollback-specific
  packet validation, `node --check`, and `git diff --check`.
- Added an operator note stating that current default-on baseline suites must be
  updated or excluded if rollback is actually applied.
- Added a static simulator test proving the one-line rollback would leave the
  loader REST-first while keeping GraphQL query code available for future
  re-enable.

## Remaining Posture

The core packet remains non-runtime: it does not roll the feature back now, does
not remove GraphQL dependency or resolver code, does not remove REST fallback,
and does not open deployment, production, telemetry, global-readiness,
external-client, write/audit-write, provider/memory, H15/H-series,
mutation/subscription, or field-expansion gates.
