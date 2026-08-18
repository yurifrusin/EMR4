# Ariadne agent error and correction register — revision 416

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 416 preserves incomplete revision 415 and adds AER-0486. Revision 415
correctly captured the repeated pipeline command violation but incorrectly
used `related_incident_ids` to connect records with distinct attempt identities.
The canonical validator rejected that peer linkage before dispatch.

The correction removes the cross-attempt link, preserves the recurrence through
the exact shared recurrence signature and explicit narrative, and extends the
complete register suite. The canonical register contains 486 bounded incidents,
all corrected or explicitly contained and none open.

No worker worktree, container or occupied provider call started. This correction
does not broaden the exact tool view, worker package, provider, data,
application, deployment, release, Pages or protected-ref authority.
