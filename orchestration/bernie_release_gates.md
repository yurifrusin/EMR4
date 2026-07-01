# Bernie Release Gates

This checklist records the Sprint 97 release rule for Bernie reception work.
It exists to prevent Sprint 96's false pass pattern from recurring: a basic
happy path must be release evidence, not optional post-closeout user review.

## Blocking Happy Path

A Bernie sprint that changes booking interpretation, candidate selection,
confirmation, staged diary preview, staff-facing Bernie copy, or release/review
harnesses cannot close unless the ordinary receptionist prompt is verified as a
release gate:

```text
Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45
```

The gate may be deterministic, provider-backed, or both, depending on the
sprint scope. It must state the exact execution mode, expected outcome, and
evidence. If this ordinary prompt fails in the relevant release surface, closeout
status is blocked until fixed or the sprint is explicitly narrowed away from
Bernie booking interpretation and documented as such.

## Test Label Rules

- A test that intercepts HTTP routes, uses `page.route(...)`, serves fixture
  payloads, stubs Office, runs with `?smoke=true`, or uses fake/mocked provider
  output is a deterministic, route-intercepted, fixture, fake-provider, or
  mocked-provider check. It must not be described as live.
- A true live-provider check must reach the configured provider path without a
  local route intercept or mocked provider factory, and the resulting evidence
  must include provider metadata showing `live_provider: true`.
- A live UI check means the deployed or local UI made real non-intercepted API
  calls to the intended backend. If the browser/API path is intercepted, call it
  route-intercepted even when the UI is rendered in a real browser.

## Closeout Rules

- Basic Bernie happy paths are blocking release checks, not residual user review.
- Route-intercepted Playwright/pytest results may satisfy deterministic coverage
  only when the closeout names them as route-intercepted.
- If a screenshot or visual failure has been reported and remains reproducible,
  the sprint cannot close as integrated/verified. Closeout must instead record
  the failure, reproduction path, owner, and next required fix.
- Residual user review may remain only for checks Ariadne cannot safely perform
  with available tools, such as Yuri's clinical judgment, real-world phone/device
  context, external account ownership, or production service-console decisions.

## Minimum Sprint 97 Evidence

Before Sprint 97 closes, Ariadne should be able to point to all of:

1. A deterministic automated gate for the Margaret Thompson / Dr Shera ordinary
   prompt.
2. Clear labeling that route-intercepted checks are not live checks.
3. A live-provider readiness result: either a true provider-backed pass with
   `live_provider: true`, or a blocked/deferred release note that explicitly
   says live-provider readiness was not proven.
4. A screenshot-failure status: fixed and no longer reproducible, or sprint
   closeout remains blocked.
