# Ariadne agent error and correction register revision 142

Date: 2026-08-09

Status: bounded register correction candidate

Revision 142 adds AER-0167 and brings the register to 167 bounded incidents
with zero open incidents.

## AER-0167 — alias lock hidden by absent UPDATE visibility policy

Behavior attempt 027 failed closed at the producer alias `FOR KEY SHARE` lock.
The accepted alias table forced RLS and admitted producer `SELECT` and `INSERT`,
but lacked the `UPDATE USING` visibility PostgreSQL also applies to a locking
read. The newly inserted alias was consequently filtered from its mandatory
locking reselect.

The correction adds only an exact producer-bound alias lock-visibility policy.
Its `WITH CHECK` is the same binding conjoined with literal `FALSE`; the
immutable trigger, row lock, zero producer direct table DML, body program,
twenty-scenario contract and authority boundary remain unchanged. Hostile tests
reject removal, foreign-capability widening and any write check that can pass.

This incident is related to AER-0155 because both arise from PostgreSQL's
SELECT-plus-UPDATE-policy treatment of row-locking reads, but the affected
relation, capability and no-write correction are independently preserved.
