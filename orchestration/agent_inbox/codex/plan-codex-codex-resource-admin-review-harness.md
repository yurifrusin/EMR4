# plan-codex-codex-resource-admin-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | orchestrator |
| Branch | `master` |
| Source Task | `codex-resource-admin-review-harness` |
| Status | pending_plan_review |
| Created | 2026-06-23 15:12 +1000 |
| Source HEAD | `1a2ab12` |

## Plan Summary

Sprint 19 resource-admin review harness plan

## My Understanding

This is the Codex review-harness lane for Sprint 19. It should create documentation/review scaffolding only, after approval, so Codex can review Claude's backend resource-admin contract and Antigravity's diary resource-admin UI without mixing terminology or implementation scopes. The harness must keep physical location, room, waiting area, diary page/view, appointment status, patient identity, and future Bernie actions separate.

## Intended Surface / Boundary

Orchestration and review documentation only: a Sprint 19 resource-admin review harness and closeout scaffolding. It must not change production backend, frontend, taskpane, Command Centre, appointment mutation behavior, or worker task scopes.

## Out Of Scope

No app code, migrations, API implementation, diary UI implementation, taskpane/Command Centre changes, patient merge/delete, appointment mutation changes, autonomous Bernie runtime, or edits to Claude/Antigravity task packets unless Codex explicitly changes sprint scope.

## Files I Expect To Edit

Expected: orchestration/resource_admin_review.md or similarly named Sprint 19 review harness; orchestration/sprint_closeout.md only if adding a pointer/scaffold is useful; possibly orchestration/parallel_workstreams.md status notes after plan approval. No app/, docs/diary/, EMR4 Sidebar/, migrations, tests, or scripts files.

## Implementation Steps

1. Re-read resource_admin_bernie_tool_design.md, location_diary_view_review.md, Sprint 19 board, and the worker packets. 2. Draft a review harness that names backend/API checks, diary UI checks, user-review checklist, API snippets, not-required surfaces, and merge gates. 3. Ensure vocabulary separates PracticeLocation, Room, WaitingArea, Diary view/page, Appointment status, Patient identity, and Booking confirmation. 4. Add closeout scaffold/pointer only if it helps later integration reporting. 5. Run git diff --check and verify snippets against final backend contract after submissions arrive.

## Visual / Behavioural Acceptance Checks

Harness gives Codex and the user exact post-integration checks for room/waiting-area admin. It states what does not need testing. It preserves boundaries around diary grid geometry, Waiting Room cards, appointment statuses, roster/template editing, patient identity, and Bernie runtime. It can be updated after worker submissions without needing production code changes.

## Risks / Ambiguities

Backend route names or payloads may differ from the initial Sprint 19 packet, so API snippets should be labelled as review aids until Claude submits. Antigravity may defer UI if backend contract changes, so the harness must tolerate partial integration. Audit logging is still future work; do not imply Bernie direct writes are enabled.

## Codex Plan Review

- Review result: Approved. This is Ariadne/orchestrator review scaffolding, not a Codex worker implementation branch.
- Required changes before implementation: Keep edits to orchestration/review docs only; label API snippets as review aids until Claude's final contract lands; preserve the vocabulary guardrails around location, room, waiting area, diary view, status, patient identity, booking confirmation, and Bernie proposal-only boundaries.
- Approved to proceed: yes
