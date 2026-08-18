# Ariadne agent error and correction register — revision 493

Date: 2026-08-19

Timestamp: 2026-08-19T01:21:19.6063187+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0572 preserves the revision-492 suite's remaining duplicate recurrence
fixture. One expected report block had advanced through AER-0571 while a second
direct assertion still stopped at AER-0566. Both projections now advance
together through AER-0572.

Revision 493 contains 572 bounded incidents. All are corrected or contained;
none is open. These observations do not score a model or provider and confer no
product, data, provider, deployment or protected-ref authority.

## Prevention

The register should have one generated recurrence projection. Tests should
exercise reducer properties and deliberately malformed inputs rather than copy
the complete output population into multiple independently maintained fixtures.
This incident is therefore adoption evidence for the transactional reducer, not
a reason to add another manual checklist item.
