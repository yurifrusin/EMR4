# Ariadne agent error and correction register — revision 428

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 428 preserves accepted revision 427 and adds AER-0498. The AER-0497
update advanced the current latch checkpoint to register revision 427 but left
its exact continuity-test assertion at revision 426. The complete packet
reported that single stale literal while every other register and latch check
passed.

The correction advances the checkpoint and its dedicated assertion together.
The canonical register contains 498 bounded incidents, all corrected or
explicitly contained and none open. No retry or resume of the consumed occupied
attempt is permitted.
