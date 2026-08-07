# Sol acceptance: recovered inert durability DDL rehearsal plan

Date: 2026-08-07

Candidate HEAD reviewed: `e00d5d01d534a9e005cd6deea5c82bb41ec73120`

Result:
`raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan_pass`

The first review's `pass` is not admitted because it misstated both immutable
opcode populations and invented failure SQLSTATEs. The bounded Sol recovery
records 22 declared/21 observed instruction opcodes with only
`DERIVE_BINDING` absent, 34 declared/34 observed expression opcodes, exact
value-free `F_CARDINALITY`/`CF004` handling, expected-constraint fencing for all
21 insert/reload nodes and a narrow fixed-path inert-only activation delta.

One fresh Gemini 3.6 Flash/high project independently reviewed the recovered
exact clean HEAD. It reproduced the populations, reconciled all 21 conflict
keys to one effective enforcing object, verified the failure and rethrow
semantics, ran the eight focused plan tests plus Ruff/diff checks and returned
`pass` with no P0-P3 finding. Sol's readback found no decision-contract or
postflight discrepancy.

Bounded implementation may proceed. This acceptance grants no SQL execution or
application, database/source/outbox/feed/watcher/listener contact, migration,
product/provider call, patient/product/protected data, application/API/Diary or
runtime wiring, deployment, release, Pages rebuild or protected-ref movement.
The renderer and output remain repository-local inert evidence until a later
separately bounded disposable PostgreSQL gate.
