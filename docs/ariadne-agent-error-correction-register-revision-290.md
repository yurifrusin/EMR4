# Ariadne agent error and correction register — revision 290

Date: 2026-08-15

Timestamp: 2026-08-15T16:19:37+10:00 (Australia/Brisbane)

Revision 290 records AER-0329. The register now contains 329 bounded known
incidents, all corrected or contained by an explicit control.

AER-0329 preserves a recurrence of the source-binding mistake first recorded
as AER-0289. After commit `f6502046`, Sol began a new uncommitted post-model-
change runtime-state draft by extending the abbreviated display into a
forty-character value instead of first copying literal `git rev-parse HEAD`
output. The inferred value was not a commit and was never admitted into a
passed receipt, committed evidence or verifier packet. No provider/model call
occurred and the candidate remained unchanged.

Sol stopped before dispatch, captured the exact object identity
`f650204638287776ba32aea44655ca7e1b01809d`, replaced both draft occurrences,
and then generated the passed five-source receipt. The durable control remains
unchanged but is now recurrent: capture and retain literal full `git rev-parse
HEAD` output immediately after every commit and before drafting any source-
bound packet, state or receipt. Never construct or autocomplete an object ID
from abbreviated terminal output.
