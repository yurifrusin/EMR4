# Ariadne agent error and correction register — revision 531

Date: 2026-08-19

Timestamp: 2026-08-19T06:52:17.2546077+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 530

AER-0615 preserves the complete closeout packet's one stale lifecycle fixture.
The architecture plan test still required the operation's planning source
`a29e99c2fbfca59a24c348ded49dd29352b72aa3` after the valid latch had become
`complete` at exact reviewed source
`f6cbd33fd3322754e06ac6dafa1503f5200e0803`.

The correction keeps the operation and full-object checks exact while deriving
the one permitted source from lifecycle status: planning source only while
`in_progress`, reviewed source only when `complete`.

## Register state

Revision 531 contains 615 bounded incidents. All are corrected or contained;
none is open. AER-0615 has the new repository recurrence signature
`repository.completed_operation_latch_test_retained_planning_source`.

## Clockwork consequence

The architecture closeout's conventional comparator advances to fourteen
failure-induced verification reruns. The future clock must derive lifecycle-
sensitive source identity from one typed state transition instead of requiring
tests to remember which full object belongs to each phase.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
