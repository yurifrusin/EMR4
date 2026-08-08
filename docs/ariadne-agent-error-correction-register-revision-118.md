# Ariadne agent error and correction register revision 118

Date: 2026-08-08

Status: bounded register correction candidate

Revision 118 adds AER-0141 and brings the register to 141 bounded incidents.

## AER-0141 - generation registration effects lacked forced-RLS coverage

Attempt 018 passed corrected artifact admission and reached `BTR-E01`, then
returned SQLSTATE `42501` with zero admitted scenarios and verified cleanup.
Static reconciliation found that `register_observer_generation_v1` must select
and insert the initial stream head, frame generations and invalidation
watermarks under an exact `LIFECYCLE` binding, but the six relevant forced-RLS
predicates admitted only `PRODUCER` or `COORDINATOR`.

The structural contract now adds `LIFECYCLE` to exactly those six
`SELECT`/`INSERT` predicates. The matching `UPDATE` policies and every direct
table privilege remain unchanged. A new regression test binds the required
operations and proves that lifecycle update authority stays absent.

The body parent, inert artifact, parse/catalogue and behavior descendants must
be rebound and freshly reviewed before another database attempt.
