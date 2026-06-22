# plan-codex-codex-resource-admin-bernie-tool-design

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-resource-admin-bernie-tool-design` |
| Status | integrated |
| Created | 2026-06-22 12:47 +1000 |
| Source HEAD | `e551706` |

## Plan Summary

Plan resource admin and Bernie supervised tool boundaries

## My Understanding

Plan only. Define the next resource/admin foundation before Bernie can safely suggest receptionist actions. Separate rooms/resources, waiting areas, patient identity, attendance status, SMS/reminder confirmation, and future typed Bernie tools. No production code until complete sprint task.

## Intended Surface / Boundary

Design/orchestration surface only first: resource-admin and Bernie tool boundary notes, likely implementation_plan.md/orchestration docs after approval. No diary grid, Waiting Room panel, taskpane, migrations, or runtime UI in plan stage.

## Out Of Scope

Production UI; autonomous Bernie actions; LLM agent runtime; booking drag/drop/resize; production schema migration unless approved later; edits to Claude/Antigravity packets; SMS webhook implementation; patient-facing chat/kiosk/phone voice.

## Files I Expect To Edit

Likely after approval: orchestration/resource_admin_bernie_tool_design.md or similar, implementation_plan.md notes, orchestration/sprint_closeout.md if closing the sprint, maybe app models/schemas/routers/tests only if Codex/user expands from design to thin API proposal.

## Implementation Steps

1. Document canonical vocabulary for rooms, bookable resources, waiting areas, patient identity, attendance state, SMS confirmation. 2. Define resource-admin endpoint/tool candidates without implementing them. 3. Define Bernie typed tools as supervised proposals with human-confirmed writes and audit requirements. 4. Map dependencies to existing appointment/waiting-area contracts and companion Sprint 14 workstreams. 5. Add review/acceptance checklist and future implementation slices.

## Visual / Behavioural Acceptance Checks

Plan accepted when concepts stay separate; future endpoints/tools are concrete/testable; no adjacent diary grid or Waiting Room panel behaviour is claimed by this lane; Bernie writes require staff confirmation and audit; SMS confirmation is not conflated with identity or attendance.

## Risks / Ambiguities

Naming drift between room/resource/waiting area; legacy Confirmed status ambiguity; tool schema may outrun audit_log/RBAC; Claude check-in design may choose a different mutation shape; SMS confirmation needs future reminder metadata; admin UI scope could balloon.

## Codex Plan Review

- Review result: approved by Codex/user in the GUI.
- Required changes before implementation: none beyond keeping implementation to documentation/design only.
- Approved to proceed: yes
