# Ariadne agent error and correction register — revision 200

Date: 2026-08-08

Revision 200 adds AER-0234 and brings the register to 234 bounded incidents.

## AER-0234 — server-authored admission time was used as replay identity

Behavior attempt 046 proved that `INSERT_OR_RELOAD_COMPARE` could not recognise
an already committed conflict row in a later transaction because its winner
predicate required the stored `admitted_at` value to equal the new transaction
timestamp. The bounded correction removes only that volatile comparison from
all three admission reload nodes while retaining server-authored insertion,
immutable storage and return of `admitted_at`. Stable primary-key and semantic
winner comparisons remain unchanged.
