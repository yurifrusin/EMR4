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

## Sprint 98 Screenshot Blockers

Sprint 98 release gates must also block the exact regression classes reported
from Yuri's live screenshots:

1. **Resolved practitioner must not become raw missing ID copy.** If the ordinary
   prompt resolves `Dr Shera` to a practitioner, the backend/UI release surface
   must not show `missing_practitioner_id`, `practitioner_id`, raw UUIDs, or
   `Practitioner ID is required` to ordinary reception staff. Developer/debug
   diagnostics may show typed codes only behind the existing debug gates.
2. **Selected booking slot must have a path back.** After staff choose one Bernie
   candidate booking slot and a proposed appointment is staged, the Bernie panel
   must provide a visible path back to the candidate list so staff can choose a
   different slot without closing/reloading the diary.
3. **Confirm failures must be typed, not generic Not Found.** Clicking
   `Confirm booking` must call the configured Bernie confirm endpoint and render
   success or a typed, receptionist-safe failure. A bare `Not Found` / 404 detail,
   raw route error, raw UUID, or snake_case implementation detail in ordinary
   mode blocks closeout.

Recommended blocking evidence:

- Backend/API: focused pytest for the ordinary prompt interpretation ->
  supervised booking contract, confirmation-ready practitioner evidence, and
  invalid/stale confirm payloads returning the typed Bernie confirmation
  envelope with no appointment/audit write.
- Smoke script: deterministic `scripts/smoke_bernie_interpreter.py` run proving
  the ordinary prompt parses `14:00` to `15:45` and carries resolved
  practitioner/patient IDs while compact output remains redacted.
- Route-intercepted UI: `review/test_diary_smoke.py` coverage proving candidate
  slots render, selected-slot state has a visible choose-another-slot path,
  confirming calls `/api/v1/appointments/proposals/create/confirm-bernie`, and
  ordinary panel/card text excludes raw IDs, `missing_practitioner_id`, and
  generic `Not Found`.
- Live/deployed Diary: only a non-intercepted browser/backend/provider run may
  be called live. If not run or not proven, closeout must explicitly say live
  Diary readiness is deferred; route-intercepted checks are not a substitute for
  live evidence.

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
