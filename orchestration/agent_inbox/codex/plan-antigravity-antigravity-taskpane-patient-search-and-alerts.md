# plan-antigravity-antigravity-taskpane-patient-search-and-alerts

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-taskpane-patient-search-and-alerts` |
| Status | pending_plan_review |
| Created | 2026-06-23 10:17 +1000 |
| Source HEAD | `0456387` |

## Plan Summary

Taskpane patient search and alert feedback

## My Understanding

Improve patient search in taskpane by splitting query into terms, searching backend for the longest term with limit=50, and filtering candidates. Relocate result divs to the bottom of the scrollable forms, auto-scrolling to the bottom on errors/warnings, and adding action status to new patient form.

## Intended Surface / Boundary

EMR4 Sidebar/src/taskpane/taskpane.{html,js}

## Out Of Scope

Backend changes, diary changes, patient merge/delete implementation, Command Centre redesign.

## Files I Expect To Edit

EMR4 Sidebar/src/taskpane/taskpane.html, EMR4 Sidebar/src/taskpane/taskpane.js

## Implementation Steps

Bump cache-buster version to v=54. Relocate #new-patient-result and #patient-edit-result above actions. Add #new-patient-action-status. Add scroll-to-bottom logic in setResult functions. Implement setNewPatientActionStatus helper. Wire status logs in createNewPatient and submitNewPatient. Update searchPatients to split queries, search for longest term, and filter in JS.

## Visual / Behavioural Acceptance Checks

Verify full-name search, multi-field search, save failure alert visibility next to buttons without scrolling, duplicate create warning at bottom, and normal save.

## Risks / Ambiguities

Longest term selection needs to handle empty/whitespace queries. Client-side filtering depends on candidate list including target record (max 50).

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
