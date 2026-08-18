# Ariadne agent error and correction register — revision 495

Date: 2026-08-19

Timestamp: 2026-08-19T01:52:05.9395004+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0574 preserves the rejected first Gemini 3.7 veto. It returned `pass` and
claimed newly introduced evidence defects remained fail-closed, but the reviewed
predicate exempted evidence absence on both inherited nodes and the newly
appended node. Sol rejected the pass after exact receipt readback.

The corrected candidate exempts only historical ancestor-node evidence absence,
adds a new-node missing-evidence mutation and requires a fresh exact-candidate
veto. Revision 495 contains 574 bounded incidents. All are corrected or
contained; none is open.

## Prevention

Every differential exception must identify both sides of its boundary and carry
one mutation test for each. A reviewer assertion about that boundary is admitted
only after those mutations are reproduced; a terminal `pass` is evidence, not
self-authenticating acceptance.
