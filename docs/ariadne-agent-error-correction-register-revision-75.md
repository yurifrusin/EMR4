# Ariadne agent-error register revision 75

Date: 2026-08-07

Status: R6 coordinator lock-order integration rejection preserved

Revision 75 adds AER-0077. The first integrated R6 coordinator candidate
acquired and then reacquired the current recovery anchor around existing
admission locks. The deterministic path validator rejected that uncommitted
state with `lock_ordinal_duplicate` and `lock_ordinal_sequence`; it supplied no
acceptance evidence.

The corrected coordinator locks exactly one current anchor before the primary
or conflict admission row and passes that row symbol through every descendant
rebase branch. Admission-missing rebase paths take one branch-local anchor
lock, while receipt replay and already-terminal replay remain anchor-free. The
source-generated contract now rebuilds and checks at
`sha256:c8d27c85def134056598be7ef12cda3ae7b509b3d06b16a536459baea51bc24b`.
Fresh focused, full-packet and independent exact-HEAD acceptance remain
mandatory.

Revision 75 contains 77 bounded incidents. Incident counts remain
workflow-improvement signals only.
