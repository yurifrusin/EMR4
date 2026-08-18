# Ariadne agent error and correction register — revision 447

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 447 preserves revision 446 and adds AER-0517. The first repair
preplanning state omitted two configured declined adapter observations, so its
immutable receipt failed closed before planning or dispatch.

The corrected runtime restores the complete adapter inventory and its distinct
receipt passes. The canonical register contains 517 bounded incidents, all
corrected or explicitly contained and none open.
