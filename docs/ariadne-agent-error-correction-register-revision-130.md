# Ariadne agent error and correction register revision 130

Date: 2026-08-09

Status: bounded register correction candidate

Revision 130 adds AER-0155 and brings the register to 155 bounded incidents
with zero open incidents.

## AER-0155 — lifecycle row lock hidden by producer-only UPDATE policy

Behavior attempt 023 stopped at `BTR-E01` with `CF004` in
`register_observer_generation_v1` line 81, admitted zero scenarios and removed
its exact owned container. A bounded networkless diagnosis proved that the
lifecycle principal could see exactly one stream head with a plain read and
had a valid binding, while the same locator returned no row under
`SELECT ... FOR UPDATE`.

PostgreSQL applies both SELECT and UPDATE policy visibility to locking reads.
The structural contract had correctly admitted lifecycle SELECT and INSERT,
but incorrectly kept `pol_cf_01_update USING` producer-only. The exact recovery
adds lifecycle only to that `USING` predicate. `WITH CHECK` remains
producer-only, lifecycle keeps zero direct table DML/SELECT and the row lock is
not weakened or removed. The failed attempt and bounded diagnosis remain
immutable; regenerated and runtime acceptance are still pending.
