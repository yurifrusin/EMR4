# Threat-model delta: alias lock visibility recovery

Date: 2026-08-09

Status: bounded repository-only recovery; behavior runtime remains closed

The repair addresses a fail-closed availability defect: PostgreSQL filters a
producer alias row from `SELECT ... FOR KEY SHARE` when forced RLS has no
applicable `UPDATE USING` policy. Removing the lock would reopen an alias-winner
race; adding ordinary update authority would weaken the immutable alias
boundary.

The bounded mitigation adds only producer-scoped lock visibility. Its
`WITH CHECK` is the same exact practice/source/stream binding conjoined with
literal `FALSE`, no direct table grant is added, all runtime roles remain
`NOINHERIT` and `NOBYPASSRLS`, and the immutable-row trigger remains unchanged.
Hostile tests must reject a missing/foreign-capability `USING`, any write check
that can become true, any new direct DML grant, or removal of the row lock.

Residual risk is confined to unproven runtime behavior until the fresh
parse/catalogue, deterministic packet, independent veto and single owned
networkless behavior retry pass. No operational database, product/patient
data, provider, command, application wiring, deployment, release, Pages or
protected-ref surface is opened.
