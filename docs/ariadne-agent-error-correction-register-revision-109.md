# Ariadne agent error and correction register revision 109

Date: 2026-08-08

Status: accepted register correction

Revision 109 adds AER-0132 and brings the register to 132 bounded incidents.

## AER-0132 - bounded query id was absent from the evidence schema

Whole-document validation of the preserved attempt-010 failure stopped because
the harness emitted the deliberately fixed `query_id: scenario_snapshot` while
the closed evidence schema still rejected every `query_id` property. No review
or database rehearsal followed the failed deterministic check.

The schema now admits only that one literal query id. A negative regression
proves that no caller-selected or additional query identifier can enter the
evidence envelope. Future failure-envelope changes must update and validate the
closed evidence schema in the same candidate.
