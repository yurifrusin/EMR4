# Ariadne agent error and correction register — revision 201

Date: 2026-08-08

Revision 201 adds AER-0235 and brings the register to 235 bounded incidents.

## AER-0235 — diagnosis assumed the wrong failure-envelope location

The first focused test of the attempt-046 diagnosis stopped because the draft
treated `preconditions` as an object containing failure telemetry. Direct
schema inspection showed that `preconditions` is an array and the bounded
failure envelope is `environment.failure`. The reader was corrected, both
focused tests passed, and no candidate, database or external action occurred
during the failed draft.
