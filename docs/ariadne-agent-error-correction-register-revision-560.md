# Ariadne agent-error and correction register — revision 560

Date: 2026-08-19
Timestamp: 2026-08-19T09:49:44.1344800+10:00 (Australia/Brisbane)

## Revision scope

Revision 560 preserves AER-0649 and AER-0650. The complete revision-559 suite found that the exact-count recurrence fixture omitted AER-0648. A following read-only diagnostic then assumed a nonexistent `composite` field instead of using the already inspected repository fixture.

The exact recurrence fixture now includes both AER-0648 and the recurring correction AER-0649. The report query uses no invented field. The register contains 650 incidents, all corrected or contained and none open. Final end-to-end build cost is twenty reruns.

Repair-only break-even is now three future closeouts. Cumulative break-even, including the predecessor's thirteen sunk reruns, remains four closeouts.

## Prevention

Update counts and recurrence membership atomically, and inspect current structured-data rows before ad hoc selection.
