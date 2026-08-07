# Ariadne agent-error register revision 72

Date: 2026-08-07

Status: third durability-body veto and reviewer path correction preserved

Revision 72 adds AER-0072 and AER-0073.

AER-0072 records the fresh reviewer's first invalid Ruff path transcription.
One underscore-delimited filename was written with hyphens, so Ruff returned
E902 before analysis. The exact packet command was then rerun and passed. No
candidate file, HEAD or worktree state changed.

AER-0073 preserves rejection of exact candidate
`5a3c5b5118f80153d545bf30ae9db99acb187cd7`. Its 192-test packet passed, but
fresh manual review found unconditional source access on receipt replay,
recovery-anchor construction without complete lifecycle/receipt/audit/key
proof, and structurally non-unique set key pairs. The candidate remains
untrusted. The third exact-veto recovery is the only implementation authority
for those three surfaces.

Revision 72 contains 73 bounded incidents. Incident counts remain
workflow-improvement signals only.
