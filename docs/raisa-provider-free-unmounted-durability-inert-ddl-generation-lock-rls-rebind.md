# Durability inert DDL generation-lock RLS rebind

Date: 2026-08-10

Status: deterministic inert-artifact regeneration complete.

The fixed renderer is rebound to structural contract
`sha256:3ce317803da9cbd1a38a1f922627784467b3e8cc7e34dac924c09c4be6bf6a16`
and typed-body contract
`sha256:32edb340c490d509015bcafe9fecddb1057400a14c537f5d3fdb4bbfee6d3e9c`.
It emits the same 421-statement closed surface with inert SQL SHA-256
`aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9`.

The only semantic delta is coordinator admission in the existing generation
UPDATE policy; no direct table grant or body/scenario change is introduced.
Fresh disposable PostgreSQL parse/catalogue characterization and exact
reproduction remain required before behavior rebind and execution.

This artifact is inert and unmounted. It grants no migration, runtime, product,
patient, provider, command, deployment, release, Pages or protected-ref
authority.
