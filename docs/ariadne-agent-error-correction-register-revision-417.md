# Ariadne agent error and correction register — revision 417

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 417 preserves accepted revision 416 and adds AER-0487. The shared
full recurrence composite for AER-0484 and AER-0485 correctly generated a new
two-incident pattern, but revision 416 had not atomically advanced the complete-
suite recurring-pattern baseline. The suite failed only at that equality gate.

The correction adds an exact assertion for the generated pattern and preserves
it outside the residual pattern set. The canonical register contains 487
bounded incidents, all corrected or explicitly contained and none open.

No worker worktree, container or occupied provider call started. This correction
does not broaden the exact tool view, worker package, provider, data,
application, deployment, release, Pages or protected-ref authority.
