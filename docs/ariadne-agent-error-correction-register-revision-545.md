# Ariadne agent-error and correction register — revision 545

Date: 2026-08-19
Timestamp: 2026-08-19T08:41:24.0023767+10:00 (Australia/Brisbane)

## Revision scope

Revision 545 preserves AER-0633. The rejected revision-544 draft used the continuation-event value `pre_sprint_planning` as a register incident stage. The current register schema rejected it before pattern-report output.

AER-0630 and AER-0631 now use the controlled `deterministic_verification` stage, AER-0633 records the correction, and all 633 incidents are corrected or contained with none open. This fourth repair-construction rerun remains separate from the candidate's steady-state replay reading.

## Prevention

The shadow reducer maps semantic outcomes through surface-specific vocabularies. Until a separate live-adoption gate, manual register updates must read the register schema's stage enum rather than reuse continuation-event vocabulary.
