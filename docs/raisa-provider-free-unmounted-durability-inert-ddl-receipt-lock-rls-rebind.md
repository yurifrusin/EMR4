# Durability inert DDL receipt-lock RLS rebind

Date: 2026-08-08

Status: deterministic inert descendant regenerated; execution remains closed.

The inert renderer now binds structural parent
`sha256:18fb00ff02820c31b4fcab4de096393cbea49e0a37ebb28d65c5eb2d6f154cfd`
at exact source commit `a1af31e89c13a0eea72fd90a2934a0c8e0154175`
and unchanged typed-body parent
`sha256:9ef411aa353ba6b39d9fbbd769d94ef5a9237bb7c6aa031dbdafce1bfa62ce83`
at exact source commit `206803a26767d7be02b45514dd02c56cce773a46`.

The generated difference is exactly the fail-closed receipt lock policy required
by attempt 042 diagnosis, plus deterministic parent and artifact hashes. It
does not alter the typed program, relation shape, grants, twenty behavior
scenarios or any runtime wiring.

The regenerated LF artifact contains 424 statements and 1,437,022 bytes, with
SHA-256
`bfd8fd924a1771ea03a2395fbd1f154253f098a3e488188a2f77778c197d7f38`.
The render-manifest file SHA-256 is
`dd4d98a8760487b17c0a70b08ef290c45607c71284a7cef804db126faac17cc6`.

The regenerated SQL remains an inert evidence artifact. Exact parse/catalogue
reproduction, behavior-parent rebind, independent veto and any new disposable
PostgreSQL attempt remain separate descendants. No operational database,
provider, product/patient data, command, deployment, release, Pages or
protected-ref authority is opened.
