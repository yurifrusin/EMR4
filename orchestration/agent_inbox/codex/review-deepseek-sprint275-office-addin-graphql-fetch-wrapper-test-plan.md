# DeepSeek Sprint 275 Office Add-in GraphQL Fetch-wrapper Test Plan Review

Verdict: PASS with mandatory guardrails.

DeepSeek reviewed the planned blocked-by-default Office add-in GraphQL
fetch-wrapper test plan for `Query.practice.practitioners`.

Integrated guardrails:

- Use mocked or standalone plan tests only; do not edit `taskpane.js` or `app/`.
- Separate HTTP `401` transport auth failures from GraphQL body-level
  `extensions.code` errors.
- Assert GraphQL `FORBIDDEN` and `BAD_USER_INPUT` do not call logout.
- Treat `data.practice = null` as an empty no-leak result.
- Preserve rows with `defaultLocation = null`.
- Reject projection drift and keep the approved field ceiling.
- Prove expired or disabled feature posture causes zero GraphQL traffic.
- Keep provider, memory/RAG/GraphRAG, H15/H-series, trove, writes, audit writes,
  mutation, subscription, telemetry, deployment, and production gates closed.
