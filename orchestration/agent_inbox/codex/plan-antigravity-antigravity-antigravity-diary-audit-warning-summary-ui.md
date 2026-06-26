# plan-antigravity-antigravity-antigravity-diary-audit-warning-summary-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-antigravity-diary-audit-warning-summary-ui` |
| Status | integrated |
| Created | 2026-06-26 19:01 +1000 |
| Source HEAD | `d61b791` |

## Plan Summary

Display persisted appointment audit warning metadata in the read-only diary Audit History section without adding mutation controls.

## My Understanding

We need to display the warning codes or summary associated with confirmed appointment proposals in the read-only Audit History panel of the diary. Currently, the UI has placeholders for confirmed_with_warnings and warning_codes in loadAuditHistory in docs/diary/diary.js, but these are not yet populated from the backend or verified. We will display both warning summaries (e.g. from a warning_summary field) and lists of codes (from warning_codes or warnings fields). We will also extend the smoke data to verify warning rendering and add a deterministic assertion in review/test_diary_smoke.py.

## Intended Surface / Boundary

The Audit History collapsible panel inside the active appointment's edit modal (booking modal) in docs/diary/diary.html. Nearby surfaces (appointment grid, practitioner list, waiting area) must not change.

## Out Of Scope

Backend schema modifications, migrations, status/mutation contract implementation (handled by Claude), appointment delete flow changes, SMS/billing, taskpane.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py

## Implementation Steps

1. Update getMockAuditEvents in docs/diary/diary.js to return warning metadata for a smoke test appt. 2. Update loadAuditHistory in docs/diary/diary.js to render warning_summary and warning_codes using CSS class booking-audit-warnings. 3. Update review/test_diary_smoke.py to assert warning text is visible in the audit list. 4. Cache-bust assets in docs/diary/diary.html if needed.

## Visual / Behavioural Acceptance Checks

1. View Margaret Thompson's edit modal. 2. Expand Audit History. 3. Verify 'Double-booked warning' or warning codes are clearly displayed in red/prominent text. 4. Confirm no warnings are displayed for entries that lack warning metadata. 5. Confirm audit remains completely read-only.

## Risks / Ambiguities

Backend contract mismatch if Claude uses a different JSON structure (mitigated by supporting multiple standard shapes in the UI).

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

## Codex Integration Result

Integrated in Sprint 37 after Ariadne review, bounded warning-code sanitization, Alembic head repair, and verification.
