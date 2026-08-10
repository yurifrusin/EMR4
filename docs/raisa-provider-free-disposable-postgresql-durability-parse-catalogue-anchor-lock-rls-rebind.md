# Disposable PostgreSQL parse/catalogue anchor-lock RLS rebind

Date: 2026-08-08

Status: parent rebind and fresh characterization complete; exact reproduction
remains required.

The fixed rehearsal contract now binds accepted inert source
`ad98e6d7148781323ddc963c2d6523c4232cb52a`, canonical LF artifact
`sha256:550336e145eac6ac004447d05ea3e72d970f6d8283d3af2689aed62cfff92bc6`,
1,435,884 bytes and statement count `422`.

Attempt `9c293b77a2ebc1364f602f17` characterized the disposable PostgreSQL
catalogue and cleaned up its exact owned container. Its immutable evidence is
`provider-free-disposable-postgresql-evidence-anchor-lock-rls-characterization.json`
with SHA-256
`e1568e1218fc9663b1490349828a7ea40f5da933e9db0b7b7271164c8981e968`.
Compared with the previous generation-lock catalogue, only the `policies`
digest changed, to
`sha256:9b3c05060a26b4606a8da559ca02289c0fe3a256e5a16dd87a13c493a06e3476`.
The policy population changed from 45 to 46; all other catalogue digests and
kind counts remained exact. The contract now binds those characterized digests
at canonical digest
`sha256:ce968baca442a3a9c3a3b0a6a13e635115378ec91434bd29baaf58dce07786f3`.

The new exact row is `pol_cf_08_update_lock`; all other object, role, function,
trigger, privilege and phase populations remain unchanged. The previous
accepted mutable parse evidence and historical failure stay protected until a
fresh exact reproduction pass has been routed.

This grants one provider-free, networkless, authored-synthetic disposable
PostgreSQL parse/catalogue recovery sequence only. It grants no behavior claim,
applied migration, operational database, application wiring, product or patient
data, provider call, deployment, release, Pages or protected-ref movement.
