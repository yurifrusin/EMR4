# Ariadne agent-error and correction register — revision 549

Date: 2026-08-19
Timestamp: 2026-08-19T09:14:20.5352564+10:00 (Australia/Brisbane)

## Revision scope

Revision 549 preserves AER-0637. The complete register suite showed that the intended structural correction for AER-0636 still searched the narrative `observed_error` field for the prose label `near-synonym`. The preserved incident sentence described the mismatch accurately but did not contain that label.

The assertion now checks the exact typed `recurrence_signature`. The register contains 637 incidents, all corrected or contained and none open. This is construction rerun eight and remains separate from the zero-rerun steady-state replay.

## Prevention

A structural register assertion must name a typed key and an exact closed-vocabulary value. It must not search a narrative field for explanatory wording.
