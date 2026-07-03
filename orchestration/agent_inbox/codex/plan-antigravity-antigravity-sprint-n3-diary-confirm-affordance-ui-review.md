# plan-antigravity-antigravity-sprint-n3-diary-confirm-affordance-ui-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n3-diary-confirm-affordance-ui-review` |
| Status | accepted |
| Created | 2026-07-03 20:31 +1000 |
| Source HEAD | `097ac41` |

## Plan Summary

Diary Bernie panel confirm/review affordance gating and stale-state invalidation

## My Understanding

Ensure Bernie staff confirmation is strictly gated by backend evidence and reception policies, and that editing composer/navigating context invalidates stale staged previews.

## Intended Surface / Boundary

Bernie review panel, composer input, status/action rendering, and staged previews; diary grid and waiting room must remain unchanged.

## Out Of Scope

Backend schema modifications, persisted session tables, visual redesigns, booking write path, and auto-mode changes.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Implement strict validation check in diary.js using confirmation_ready and must_block_confirmation. 2. Clear staged preview and reset state on composer input events. 3. Render block messages for non-confirmable states. 4. Implement deterministic Playwright tests in test_diary_smoke.py.

## Visual / Behavioural Acceptance Checks

Verify confirm button is disabled/hidden on blocked states, typing in composer resets preview state, and tests pass successfully.

## Risks / Ambiguities

Conflict with turn-history state tracking or auto-preview loop triggers when resetting preview.

## Codex Plan Review

- Review result: Accepted by Ariadne with a backend-first gating amendment.
- Required changes before implementation: Diary UI should consume
  `payload.confirm_affordance.can_show_confirm_ui` / equivalent backend-owned
  field once exposed, rather than deriving confirmability from raw status or
  local message inference. Preserve existing layout and grid/waiting-room
  surfaces. Add deterministic review smoke coverage for confirm-ready,
  blocked/stale, and composer-stale-reset cases.
- Approved to proceed: yes, release with `complete sprint task`.
