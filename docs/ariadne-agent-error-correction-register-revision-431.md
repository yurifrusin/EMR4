# Ariadne agent error and correction register — revision 431

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 431 preserves accepted revision 430 and adds AER-0501. The first
Continuity 321 updater emitted the new Harness node without the two inherited
product-contract evidence blocks required by Compass current-position
validation. The validator failed closed on exactly those two omissions before
staging or acceptance.

The correction restores the parent's combined-intent and committed-reschedule
evidence blocks verbatim and reruns the updater idempotently. The canonical
register contains 501 bounded incidents, all corrected or explicitly contained
and none open.
