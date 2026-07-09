# DeepSeek Review - Sprint 283 Default-On Local Backend Smoke

Verdict: PASS.

DeepSeek reviewed the Sprint 283 local backend smoke for the already default-on
Office add-in practitioner selector GraphQL path.

## Findings

- The smoke adds unique value over the resolver tests because it extracts the
  committed `PRACTITIONER_DIRECTORY_GRAPHQL_QUERY` from `docs/diary/diary.js`
  and posts that exact document to the local `/api/v1/graphql` endpoint.
- Existing resolver tests use a separate hand-authored query literal, so they
  would not catch a broken Office add-in query template.
- The evidence correctly stays local and non-intercepted through FastAPI
  `TestClient`, fake DB rows, and authenticated staff context.
- Practice scoping, active-only filtering, default-location projection,
  sensitive canary absence, and no audit writes are covered.
- No deployment, production, telemetry, global-readiness, external-client,
  write, audit-write, provider/memory, H15/H-series, mutation/subscription, or
  field-expansion gate is opened.

## Integrated Recommendations

- Renamed the evidence claim from `asserts_active_only_default_path` to
  `asserts_active_only`, because the Office add-in explicitly sends
  `activeOnly: true`.
- Added an explicit `practice is not None` assertion before dereferencing the
  GraphQL response shape.
- Pinned the rollback-oriented `next_recommended_work` evidence field in the
  guard test.
