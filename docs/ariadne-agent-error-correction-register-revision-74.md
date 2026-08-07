# Ariadne agent-error register revision 74

Date: 2026-08-07

Status: R6 parent-constraint rejection and nonterminal challenge preserved

Revision 74 adds AER-0075 and AER-0076.

AER-0075 rejects uncommitted worktree contract
`sha256:49db11e74a46d1056e694614a970037cf021e174d71114f5262e950b9075b01f`.
Its rotation producer and anchor proof treated KEY_ROTATION lifecycle source
position as checkpoint position, while the immutable parent requires that field
to be NULL. The corrected recovery separately proves the unchanged checkpoint
position from the preceding anchor and closes latest-prior-audit continuity.

AER-0076 records that the read-only challenger supplied this material finding
but did not complete its requested terminal response. Sol stopped it after
repeated conclusion requests, preserved only the exact delivered evidence and
independently reproduced the parent mismatch. No acceptance is attributed to
the nonterminal challenge; a fresh exact-HEAD veto remains required.

Revision 74 contains 76 bounded incidents. Incident counts remain
workflow-improvement signals only.
