# Ariadne agent-error and correction register — revision 561

Date: 2026-08-19
Timestamp: 2026-08-19T09:49:44.1344800+10:00 (Australia/Brisbane)

## Revision scope

Revision 561 preserves AER-0651. A combined verification command yielded during its final focused suite, but the wrapper exposed neither the returned session identifier nor a final exit code. Partial pytest dots are not acceptance evidence.

The focused suite is therefore repeated in a dedicated bounded command whose final exit is retained. The register contains 651 incidents, all corrected or contained and none open. Final end-to-end build cost is twenty-one reruns.

Repair-only break-even remains three future closeouts. Cumulative break-even, including the predecessor's thirteen sunk reruns, remains four closeouts.

## Prevention

Every potentially yielding exec wrapper exposes its session identifier, output and final exit code, or runs the bounded test in a dedicated command.
