# plan-antigravity-antigravity-diary-resource-admin-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-resource-admin-ui` |
| Status | pending_plan_review |
| Created | 2026-06-23 15:20 +1000 |
| Source HEAD | `1a2ab12` |

## Plan Summary

Restrained diary-admin panel for rooms and waiting areas under active-location context with role-gated JWT checks and local smoke-mode CRUD mocks.

## My Understanding

Provide room/waiting area list, create, edit, and archive options in the diary frontend using Workstream A backend endpoints, with fallback mock databases for smoke mode. Maintain active-location context and role-gated constraints.

## Intended Surface / Boundary

Diary header and a new admin modal (#admin-modal). Grid/Waiting Room/Taskpane surfaces must not change.

## Out Of Scope

Backend changes, roster editing, diary template editor, appointment mutations, patient merge/delete, taskpane/Command Centre, autonomous Bernie.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js

## Implementation Steps

1. Add settings button to header. 2. Implement admin modal markup & CSS. 3. Parse JWT for role verification. 4. Build API calls & smoke-mode mocks. 5. Wire lists, forms, and triggers.

## Visual / Behavioural Acceptance Checks

Admin panel accessible to Admin/PracticeOwner; CRUD works in smoke mode; error message shown on save failure; one-location remains uncluttered.

## Risks / Ambiguities

Dependency on Workstream A API paths; will use wrapper functions to isolate schema changes.

## Codex Plan Review

- Review result: Approved. The plan stays within the diary admin-modal surface and avoids appointment geometry, Waiting Room cards, taskpane, Command Centre, and backend scope.
- Required changes before implementation: Treat JWT role checks as UI affordance only, with backend RBAC still authoritative; isolate smoke-mode mocks so they cannot hide configured API failures; align API wrapper names/payloads to Claude's final contract before submit; cache-bust diary assets if files change.
- Approved to proceed: yes
