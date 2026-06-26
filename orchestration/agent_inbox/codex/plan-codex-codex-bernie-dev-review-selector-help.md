# plan-codex-codex-bernie-dev-review-selector-help

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-dev-review-selector-help` |
| Source Task | `codex-bernie-dev-review-selector-help` |
| Status | integrated |
| Created | 2026-06-27 06:11 +1000 |
| Source HEAD | `3a02b3f` |

## Plan Summary

Plan dev-only Bernie selector help

## My Understanding

After explicit implementation approval, add a tiny help affordance beside the existing Bernie fixture-state selector so dev reviewers understand blocked, candidate_selection_required, and confirmation_ready. The affordance must be visible only when bernie_dev_review=true and must not make API calls or alter selector/confirm behavior.

## Intended Surface / Boundary

Only the dev-review Bernie fixture-state selector area in docs/diary, gated by the existing bernie_dev_review=true mode. Nearby diary grid cards/slots, waiting-room/status panels, booking slot rendering, patient/resource admin, Command Centre, and default diary mode must not visually or behaviorally change.

## Out Of Scope

Backend routes/schemas, migrations, taskpane, Command Centre, patient/resource admin, billing/SMS, natural-language parsing, autonomous booking, live API writes in tests, broad diary redesign, and any default/production exposure.

## Files I Expect To Edit

Expected after approval: docs/diary/diary.html and/or docs/diary/diary.js for the dev-only help markup/text; docs/diary/diary.css only if tiny selector-adjacent styling is needed; docs/diary/index/versioned asset references if runtime assets change; review Playwright test file(s) for route-intercepted deterministic coverage. Plan gate changes only coordination packets.

## Implementation Steps

1. Locate current bernie_dev_review gate and fixture-state selector wiring. 2. Add a selector-adjacent help/tooltip element rendered only in bernie_dev_review=true. 3. Use concise static copy: blocked means Bernie cannot safely propose/continue yet; candidate_selection_required means staff must choose one candidate slot; confirmation_ready means a proposal exists and still requires explicit confirm-Bernie approval. 4. Ensure static help text alone has no fetch/POST side effects. 5. Preserve selector change handling and explicit confirm-Bernie gating. 6. Bump asset version if any served runtime asset changes. 7. Add route-intercepted Playwright checks for hidden-by-default, visible-in-dev, no-call-on-help, selector behavior unchanged, and no confirm POST before approval.

## Visual / Behavioural Acceptance Checks

Default diary without bernie_dev_review=true shows no help or selector leakage. Dev-review mode shows concise help near the existing selector. The text explains blocked, candidate_selection_required, and confirmation_ready without implying autonomous booking. Opening/reading/toggling help causes no endpoint calls. Existing fixture selector semantics remain intact. Confirm-Bernie POST only happens after explicit staff approval. node --check, asset version integrity, deterministic route-intercepted Playwright checks, existing diary review harness, and git diff --check pass after approval.

## Risks / Ambiguities

The current selector may already share layout with other dev controls, so the implementation should avoid moving controls or changing grid/card/slot layout. Tooltip-only copy can be missed, so prefer always-visible compact help or an accessible details/summary if space allows. Asset-version bump must match the existing deployment pattern. Tests must intercept routes to avoid live writes and should assert no unintended calls from help rendering.

## Codex Plan Review

- Review result: Accepted and implementation released.
- Required changes before implementation: None.
- Approved to proceed: yes
