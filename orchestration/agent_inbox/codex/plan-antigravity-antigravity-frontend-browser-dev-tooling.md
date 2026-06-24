# plan-antigravity-antigravity-frontend-browser-dev-tooling

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-frontend-browser-dev-tooling` |
| Status | pending_plan_review |
| Created | 2026-06-24 17:14 +1000 |
| Source HEAD | `3780969` |

## Plan Summary

Improve diary/taskpane frontend development, version consistency checks, and browser-feedback loops by adding automated version checks and a comprehensive QA checklist.

## My Understanding

Write a Python script that verifies HTML cache-buster versions (?v=N) against modified assets using Git diffs, add npm script triggers in package.json, and create a comprehensive frontend UI QA developer guide.

## Intended Surface / Boundary

Frontend development tooling, validation scripts (scripts/), package configurations, and QA documentation (docs/)

## Out Of Scope

No diary/taskpane runtime UI changes, no backend changes, no migrations, no Playwright/Puppeteer framework setups.

## Files I Expect To Edit

NEW: scripts/check_frontend_versions.py, docs/frontend-ui-qa-guide.md; MODIFY: EMR4 Sidebar/package.json, orchestration/agent_inbox/antigravity/antigravity-frontend-browser-dev-tooling.md

## Implementation Steps

1. Create check_frontend_versions.py. 2. Register npm check-assets and validate-all scripts. 3. Write frontend-ui-qa-guide.md. 4. Update completion notes. 5. Submit for review.

## Visual / Behavioural Acceptance Checks

NPM validation scripts run successfully. Check-assets script successfully catches assets changed without version bumps. QA guide parses cleanly as markdown.

## Risks / Ambiguities

Low risk of build issues. Mitigated by keeping check script simple and dependent only on native git metadata.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
