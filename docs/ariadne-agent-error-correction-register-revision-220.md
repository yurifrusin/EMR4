# Ariadne agent error and correction register — revision 220

Date: 2026-08-11

Revision 220 records AER-0255 and brings the register to 255 bounded known
incidents.

## AER-0255 — complete register population-fixture correction

The second predispatch register correction validated its JSON and produced an
exact 254-incident pattern report, but the full focused suite then exposed two
stale population fixtures: the ordered ID range stopped at AER-0252 and the
by-origin assertion still expected 161 agent-behavior incidents. The exact
recurring-pattern fixture had also not yet been extended for the now-recurring
AER-0080/AER-0253 dispatch-envelope signature. No worker, provider or model
call followed.

The corrected atomic update advances the register through AER-0255 and all
affected revision, population, origin, category and candidate-state assertions.
It also inserts the exact generated recurrence block with both prevention
controls. A fresh standalone validation, pattern generation and complete
focused suite are required before the already-passing v2 dispatch receipt may
be used.

The isolated AES-C3 worktree remains clean and unchanged at
`d44be5cbe0774b6340c7e4f6ca76075242b2f156`.
