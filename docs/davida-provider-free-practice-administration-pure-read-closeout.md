# Closeout: Davida provider-free practice-administration pure read

Date: 2026-08-03

Result: `provider_free_practice_administration_pure_read_pass`

## Accepted result

Davida now has a provider-free, unmounted backend read/context desk over the
existing active-practitioner projection and a new pure active-location
projection. The location service selects exactly `{id, name}`, is practice-
scoped and active-only, orders by `name, id`, caps at 200 rows under
`db.no_autoflush`, and exposes no route, GraphQL field, role policy or write
path.

The deterministic composer receives already-authorized caller projections and
supplied time/context. It has no database, ORM, model, network, provider or clock
dependency. It maps internal UUIDs to bounded opaque authored-synthetic
references, fails closed on missing/duplicate/wrong-kind/cross-practice
bindings, emits two exact live-api-fact frames, expires after two minutes and
sets every command/write/proposal/provider/event/model-to-database authority
flag to literal false. Rooms, Diary waiting areas and the patient-linked
appointment waiting-room queue remain blocked.

## Deterministic evidence and repair history

- DeepSeek V4 Flash/high produced the ten-file candidate at
  `90781e212ac04a7b58135c9c9d9a202c6682d3f9`.
- Root reproduced Ruff and 91 focused tests. The first disposable PostgreSQL run
  passed every data, tenant, bounds, frame, privilege, integrity and cleanup
  gate but correctly returned `revision_required` because the SQL observer
  uppercased statements and searched for lowercase table fragments.
- The bounded repair `5678a4a953b9ec7bfed15b9804a38ac218a0959e`
  introduces one case-consistent fail-closed classifier and regression coverage
  requiring both pure reads while rejecting any DML/DDL.
- Root reproduced Ruff and 93 focused tests. The acceptance then passed as
  `provider_free_in_process_backend_postgres`; independent scans found zero
  sensitive patterns, task Python processes, matching disposable databases or
  roles. Evidence was committed at
  `24bdb4f0864c2d0fb515596dd204d6414e4c5f5d`.
- One genuinely fresh Gemini 3.6 Flash/high project reproduced 93 tests and
  Ruff, independently inspected the strict context/schema/blocked-source and
  SQL-classifier boundaries, found no defect and left `24bdb4f0` clean and
  unchanged.
- Root replayed the accepted commits and reproduced the combined 170-test/Ruff
  gate at `74ee7f93c9b43a7d34644b58b2584817e7e9cc00`.

## Claims not made

No Davida probabilistic/model runtime, memory/RAG, real identity, patient or
clinical data, mounted route, GraphQL mutation, proposal endpoint, confirmation,
apply/write authority, deployment, production or release is established.
Context remains minimal and non-authoritative; database truth remains solely
authoritative.

Protected refs/evidence and `docs/branding/` remained untouched. The product
Continuity/Compass map remains 206/187 because this result is task-local,
unmounted and read-only.

## Next bounded lane step

Proceed with tranche 2 of the accepted Davida sequence: a provider-free,
unoccupied typed interpretation/proofreader envelope for only
`ADVISORY_EXPLAIN_DIRECTORY` and `ADVISORY_SUMMARIZE_DIRECTORY`. It may consume
the accepted context frame and release a grounded typed advisory draft only.
Unknown operations, proposal/apply, provider execution, memory, database access
and every command/write remain closed.
