# Sprint 273 - GraphQL Internal Consumer Harness Review

- Reviewer lane: Claude via `scripts/drive_agent_headless.py`
- Date: 2026-07-09
- Scope: API/contract review only. No implementation files edited by Claude.
- Subject: test-only/internal GraphQL practitioner consumer harness for
  `Query.practice.practitioners` on `/api/v1/graphql`.

## Verdict: PASS

Claude confirmed the planned harness sits inside the Sprint 272 release boundary
for internal authenticated staff consumer development and test-harness use
through 2026-08-06. Querying the existing endpoint with existing bearer auth and
asserting success plus `401`, `BAD_USER_INPUT`, `FORBIDDEN`,
`practice(id)` mismatch null, allowed-fields-only, no sensitive fields, and
no-idempotency-key behavior opens no closed gate.

## Integrated Findings

- The harness must be a reusable consumer-contract primitive, not just a second
  copy of resolver tests.
- The clearest net-new assertion is that no `Idempotency-Key` is required for
  this read. Sprint 273 also asserts that sending one does not change behavior.
- Consumers must distinguish transport auth failures from GraphQL errors:
  missing auth is HTTP 401, while `BAD_USER_INPUT` and `FORBIDDEN` are HTTP 200
  with `errors[].extensions.code`.
- `practice(id:)` mismatch is `data.practice == null` without a GraphQL error.
- Negative allowed-field selection should prove sensitive fields are rejected by
  schema validation.
- The harness must not couple to latency, flip readiness, import runtime UI
  code, expand fields, or create reverse-chaining authority.

