# Durability inert DDL outbox-select RLS rebind

Date: 2026-08-08

Status: deterministic inert regeneration complete; execution remains closed.

The inert PostgreSQL 16 renderer now binds structural parent
`sha256:30401808c97e45ad0ecf23242a21c1b7be35bc7d37343bb2f1ab4ef139e83a5f`
at exact commit `e1ca28915b09636e5d9d693216beef450f71a356` and typed-body parent
`sha256:9b079af00e46b5e18f464cc39f9283ce400ee7b2621d875a127af19cb908ee62`
at exact commit `1a06961916bcf73d553eb401eb08094aa4c45e20`.

The generated SQL changes exactly one policy expression: existing forced-RLS
policy `pol_cf_03_select` adds the `COORDINATOR` logical capability beside
`PRODUCER`, `OBSERVER` and `RETENTION`. It creates no direct coordinator table
`SELECT` or DML grant. All 423 statements remain inert and unexecuted.

Fresh disposable parse/catalogue characterization and exact reproduction,
behavior-parent rebind, independent veto and another behavioral execution are
separate descendants. This result grants no migration application, database
contact, product or patient data, runtime wiring, provider call, deployment,
Pages rebuild, release or protected-ref movement.
