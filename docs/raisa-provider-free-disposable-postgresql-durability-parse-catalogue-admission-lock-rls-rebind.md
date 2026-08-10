# Disposable PostgreSQL parse/catalogue admission-lock RLS rebind

Date: 2026-08-08

Status: parent rebind, fresh characterization and exact reproduction pass.

The fixed rehearsal contract now binds accepted inert source
`b0339bed1090f1f04c198ca0fb2bdf2932ca702c`, canonical LF artifact
`sha256:1ab976d0555021aa6ec41778b2c3de6ef27105f17f8d1d941b714006da93b1d5`,
1,436,426 bytes and statement count `423`.

Attempt `085b2aca8e37483090017aa6` characterized the disposable PostgreSQL
catalogue and cleaned up its exact owned container. Its immutable evidence is
`provider-free-disposable-postgresql-evidence-admission-lock-rls-characterization.json`
with SHA-256
`21c9139cf194f8077837de0f97d07a189e89bc5826413a7ddae27ae14a0c18fb`.
Compared with the prior anchor-lock catalogue, only the `policies` digest
changed, to
`sha256:4e5405911b0bf1fc98cd203078639765d0fb37e708e1d2c6c7a2b119104c092d`.
The policy population changed from 46 to 47; every other catalogue digest and
kind count remained exact. The exact-bound contract is now canonical digest
`sha256:c48d34397de7c2bb433a28af2c064acdf780877933ee9d7edb28c2cc2c9644e5`.

Exact reproduction attempt `8007945b44c65d3ba0670274` matched every bound
digest and exact kind count, proved atomic rollback, and verified removal of
its exact owned container. Its immutable evidence is
`provider-free-disposable-postgresql-evidence-admission-lock-rls-exact-reproduction.json`
with SHA-256
`aeaaafc309b2f083688988aed21f77f39283b2c64d391133e8223effc1224de5`.
The protected mutable parse evidence and characterization were restored
byte-for-byte after routing.

The new exact row is `pol_cf_04_update_lock`; all other object, role, function,
trigger, privilege and phase populations remain unchanged.

This grants one provider-free, networkless, authored-synthetic disposable
PostgreSQL parse/catalogue recovery sequence only. It grants no behavior claim,
applied migration, operational database, application wiring, product or patient
data, provider call, deployment, release, Pages or protected-ref movement.
