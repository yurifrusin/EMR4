# plan-antigravity-antigravity-diary-audit-history-readability

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-audit-history-readability` |
| Status | integrated |
| Created | 2026-06-26 18:03 +1000 |
| Source HEAD | `38067fb` |

## Plan Summary

Polish diary audit history rendering to show friendly actor/action/status labels and a restrained UUID fallback without altering unrelated booking workflows.

## My Understanding

Under Sprint 34-B, the appointment audit history rendered in the diary edit modal must be made readable for staff. We need to: 1. Render friendly actor display names when present from the backend. 2. Restrain the fallback when only a raw user UUID is available by showing a shortened ID (e.g. Staff (abc123de)). 3. Map raw actions (create, update, status_change, delete) to human-friendly labels (Created, Updated, Status Changed, Cancelled). 4. Translate raw status values to friendly labels (e.g. InConsult -> In Consult, DNA -> Did Not Attend (DNA)). 5. Keep the audit section hidden on create, collapsed by default on edit, and read-only.

## Intended Surface / Boundary

Booking audit history section in docs/diary/diary.html inside the appointment edit modal. Adjacent fields/layouts of the booking modal are untouched.

## Out Of Scope

Backend schema or API mutations, write operations from the audit history panel, supervisor dashboard features, and general booking modal layout changes.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Implement formatAuditStatus(status) and formatAuditActor(evt) in docs/diary/diary.js to display friendly status names (e.g. In Consult, Did Not Attend (DNA)) and actor names (or restrained UUIDs). 2. Update formatAuditAction(action) to return 'Created', 'Updated', 'Status Changed', 'Cancelled'. 3. Update loadAuditHistory(apptId) to generate clean status transition sentences ('Changed from X to Y') and render the actor without double 'by' words. 4. Refactor getMockAuditEvents mock data to include UUIDs and test display names and fallbacks. 5. Update review/test_diary_smoke.py assertions to check for 'Status Changed', 'Created', and verify display/restrained UUID fallbacks render correctly.

## Visual / Behavioural Acceptance Checks

Verify under ?smoke=true that clicking edit on Margaret Thompson's appointment and expanding the audit history displays friendly status/action copy, displays 'by Dr. Practice Owner' and 'by Staff (11111111)' as expected, and pytest review/test_diary_smoke.py passes successfully.

## Risks / Ambiguities

Mismatch in the exact name of the display field returned by Claude's backend implementation (Workstream S34-A). We mitigate this by checking a fallback sequence of common display fields: confirmed_by_display, confirmed_by_name, confirmed_by_role, confirmed_by, and if all are missing, falling back to a shortened confirmed_by_user_id.

## Codex Plan Review

- Review result: Accepted; implementation submitted and merged after verification.
- Required changes before implementation: None.
- Approved to proceed: yes.
