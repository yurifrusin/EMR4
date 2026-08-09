# Provider-free durability top-level-XID insert/reload recovery

Date: 2026-08-09
Status: bounded renderer recovery candidate; behavior runtime remains closed

## Observed failure

Behavior attempt 022 admitted the exact reviewed PostgreSQL artifact and fixed
authored-synthetic fixtures, then stopped at BTR-E01 with `CF105`, zero admitted
scenarios and verified cleanup. Diagnosis 022a located
`cf_fence_stream_head_v1` line 34. The corrected conjunct diagnosis proved:

- `last_position = 0`: true;
- `stream_epoch = 1`: true; and
- row `xmin = current top-level XID32`: false.

No raw database error or tuple value was persisted.

## Root cause

The accepted transaction architecture intentionally compares every relevant
tuple's PostgreSQL `xmin` with the exact low-32-bit form of
`pg_current_xact_id()`. It forbids savepoints and subtransaction-authored
members; this must not be weakened.

Renderer 2.0.9 lowered each `INSERT_OR_RELOAD_COMPARE` node by putting its
`INSERT` inside a PL/pgSQL block with an `EXCEPTION` clause. PostgreSQL creates
a subtransaction for such a block, while `pg_current_xact_id()` returns the
top-level transaction ID even when called from a subtransaction. The renderer
therefore caused the new stream-head row to carry a subtransaction `xmin`, and
the deferred fence correctly rejected it.

This is a renderer defect, not a PostgreSQL conversion defect and not grounds
to broaden the provenance rule. The governing PostgreSQL 16 semantics are in
the official [transaction information function documentation](https://www.postgresql.org/docs/16/functions-info.html)
and [subtransaction documentation](https://www.postgresql.org/docs/16/subxacts.html).

## Exact repair

Renderer 2.0.10 replaces the exception-driven lowering for all twenty-one
typed `INSERT_OR_RELOAD_COMPARE` nodes with:

```sql
INSERT INTO <exact relation> (...)
VALUES (...)
ON CONFLICT ON CONSTRAINT <exact derived constraint> DO NOTHING
RETURNING ... INTO <typed output>;

IF NOT FOUND THEN
    BEGIN
        SELECT <exact winner columns> INTO STRICT <typed output>
        FROM <exact relation>
        WHERE <exact conflict key and winner predicate>;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN <CF004>;
        WHEN TOO_MANY_ROWS THEN <CF004>;
    END;
END IF;
```

The insert is no longer enclosed by an exception handler and therefore does
not author a subtransaction tuple. The exact derived conflict constraint is
named explicitly. Other uniqueness failures still propagate. The read-only
winner reload retains strict zero/multiple rejection and cannot assign a
subtransaction XID because it writes nothing.

## Acceptance and claim boundary

The recovery must prove all of the following before behavior retry:

1. all twenty-one typed nodes use exact `ON CONFLICT ON CONSTRAINT ... DO
   NOTHING` lowering;
2. no write-bearing `WHEN unique_violation`, stacked constraint diagnostic or
   renderer `cf_constraint_name` local remains;
3. generic untargeted `ON CONFLICT DO NOTHING`, wrong constraints and
   zero/multiple winner paths remain rejected;
4. the immutable typed body and migration/transaction parent semantics remain
   unchanged;
5. inert regeneration, focused tests, exact PostgreSQL parse/catalogue proof,
   behavior-contract rebind and a fresh Gemini 3.6 Flash/high veto all pass;
6. failed behavior evidence 022 remains immutable and mutable behavior evidence
   is not staged until a later successful behavior run.

This recovery grants no product or patient data, provider call, application
runtime, source read, command/write, deployment, release, Pages or protected-ref
authority.
