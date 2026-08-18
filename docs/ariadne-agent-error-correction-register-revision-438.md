# Ariadne agent error and correction register — revision 438

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 438 preserves revision 437 and adds AER-0508. The first repeated-field
peer-link patch matched historical AER-0003 instead of AER-0503. Canonical
validation named AER-0003's unexpected peers; exact readback then proved the
wrong target before staging or acceptance.

The correction restores AER-0003, patches AER-0503 under exact incident
context and asserts the AER-0490/AER-0508 recurrence. The canonical register
contains 508 bounded incidents, all corrected or explicitly contained and none
open.
