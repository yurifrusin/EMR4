# Ariadne agent-error and correction register — revision 562

Date: 2026-08-19
Timestamp: 2026-08-19T20:35:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 562 preserves AER-0652. The first single-owner migration Gemini manifest required the complete Compass evidence-presence suite inside a fresh tracked-only review worktree. Nineteen unrelated historical receipts are intentionally untracked and absent there, so seven Compass tests failed even though Gemini passed every substantive migration challenge and left the candidate clean.

The complete Compass suite had already passed in the main workspace where those preserved receipts exist. The corrected verifier manifest therefore retains that main-workspace result, omits only the non-portable evidence-presence suite from the isolated worktree and reruns every portable migration, governance, latch, register, Current Baton, Ruff, compile and read-only-runner gate. The exact candidate is unchanged.

The register contains 652 incidents, all corrected or contained and none open. Current rehearsal construction cost is sixteen reruns, including one rejected independent review, one fail-closed register-evidence ordering correction and one fail-closed incorrect register-schema path; projected steady-state corrective reruns remain zero.

## Prevention

Before provider dispatch, every verifier command is classified as tracked-only portable or main-workspace evidence-presence dependent. An isolated worktree manifest may include only the former; the latter must pass separately and be named rather than copied or silently weakened.
