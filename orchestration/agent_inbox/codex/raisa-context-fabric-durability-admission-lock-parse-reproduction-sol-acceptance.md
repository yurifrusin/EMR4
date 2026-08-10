# Sol acceptance — admission-lock parse/catalogue reproduction

Date: 2026-08-08

Decision: accepted for the bounded behavior-parent rebind only.

Exact source commit `a1f8141b05e9f2218412d2d0e7772d3f4dcfead7` preserves the
admission-lock parse contract at canonical digest
`sha256:c48d34397de7c2bb433a28af2c064acdf780877933ee9d7edb28c2cc2c9644e5`.
Characterization evidence SHA-256
`21c9139cf194f8077837de0f97d07a189e89bc5826413a7ddae27ae14a0c18fb`
and exact reproduction evidence SHA-256
`aeaaafc309b2f083688988aed21f77f39283b2c64d391133e8223effc1224de5`
prove the inert artifact parsed and installed atomically in PostgreSQL 16, all
bound catalogue digests matched, rollback was preserved and both exact owned
containers were removed.

The sole catalogue change from the prior accepted parent is policy digest
`sha256:4e5405911b0bf1fc98cd203078639765d0fb37e708e1d2c6c7a2b119104c092d`
and policy count 47, corresponding to `pol_cf_04_update_lock`. This acceptance
grants no behavior result, applied migration, persistence, application wiring,
provider, product/patient data, deployment, release, Pages or protected-ref
authority.
