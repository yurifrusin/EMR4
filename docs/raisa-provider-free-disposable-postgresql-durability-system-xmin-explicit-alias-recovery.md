# Disposable PostgreSQL durability system-`xmin` explicit-alias recovery

Date: 2026-08-09

Status: bounded renderer recovery candidate; behavior remains closed

Attempt 020 admitted the repaired artifact and catalogue, closed its synthetic
fixtures and reached `BTR-E01`, then stopped with SQLSTATE `42703`, zero
admitted scenarios and verified exact-ID cleanup. A single fresh diagnosis-only
container reproduced the failure and released the bounded coordinate
`emr4_context_fabric.cf_fence_stream_head_v1`, line 33: PostgreSQL could not
identify field `xmin` in record local `final_head`.

The prior repair was necessary but incomplete. It explicitly selected the
system column into a `record`, yet rendered that projection as
`relation.xmin` without naming the result field. The later `(final_head).xmin`
lookup therefore had no stable field identity.

Renderer 2.0.8 lowers every selected system column as
`relation.xmin AS xmin`. It leaves every user-column expression unchanged,
retains the record-local and typed-validator controls from AER-0142, and adds a
whole-artifact regression requiring all 62 exact-read occurrences to be
explicitly aliased with no remaining `.xmin INTO STRICT` form.

The regenerated artifact remains provider-free, inert and unmounted: exactly
412 statements and 1,403,680 LF bytes at SHA-256
`sha256:45c90b927a6e5a9b5b367ddf6ca76dfde0491ddb04d74214383cbca68419b7f6`.
No behavior scenario changes. Exact parse/catalogue proof and a fresh
independent veto remain mandatory before another occupied attempt.

This recovery grants no applied migration, application/API/Diary runtime,
patient, product or protected data, provider, watcher/listener, tool or command
authority, deployment, production, release, Pages or protected-ref movement.
