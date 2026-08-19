# Ariadne agent-error and correction register — revision 558

Date: 2026-08-19
Timestamp: 2026-08-19T09:49:44.1344800+10:00 (Australia/Brisbane)

## Revision scope

Revision 558 preserves AER-0647. After the focused repair suite passed, a targeted register command used two obsolete pytest function names. Pytest rejected those selectors before execution; no acceptance evidence was inferred from the failed command.

The current symbols were resolved directly from the test file before the corrected command. The register contains 647 incidents, all corrected or contained and none open. Final end-to-end build cost is seventeen reruns.

Repair-only break-even remains two future closeouts. Cumulative break-even, including the predecessor's thirteen sunk reruns, remains four closeouts.

## Prevention

Resolve manually selected pytest nodes from the current repository before invocation; prefer whole exact files when selection precision has no material benefit.
