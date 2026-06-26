# plan-antigravity-antigravity-bernie-staff-pilot-eligibility-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-staff-pilot-eligibility-ui` |
| Status | pending_plan_review |
| Created | 2026-06-27 09:16 +1000 |
| Source HEAD | `af39ff9` |

## Plan Summary

Consume Sprint 59 backend pilot eligibility endpoint and show Bernie review outside dev/query mode only for eligible staff/practices.

## My Understanding

Consume GET /api/v1/appointments/bernie/pilot-eligibility on load. If eligible is true, show launch button btn-bernie-pilot-launch. Clicking it toggles the review panel, retrieves live proposals via POST /appointments/proposals/bernie/supervised-booking, displays pilot banner, and enables POSTing to confirm_endpoint on confirm button click after checkbox is checked.

## Intended Surface / Boundary

Top actions header and Supervised Review sidebar panel.

## Out Of Scope

Backend changes, automated scheduling, taskpane/Command Centre/Office dialog/SMS/billing/resource admin.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. HTML: Add btn-bernie-pilot-launch button. 2. CSS: Style launch button and pilot warning banner. 3. JS: Call pilot-eligibility on load; show/hide button; toggle panel; display pilot banner; enable confirm post in pilot mode. 4. Tests: Add checks in test_diary_smoke.py.

## Visual / Behavioural Acceptance Checks

No launch button shown when ineligible. Button shows when eligible. Clicking it toggles sidebar and fetches live review with pilot banner. Confirm Booking posts to confirm_endpoint only after checking the explicit approval checkbox.

## Risks / Ambiguities

Network errors/failures fail-closed (button stays hidden). Preserving existing dev review/fixture behavior.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
