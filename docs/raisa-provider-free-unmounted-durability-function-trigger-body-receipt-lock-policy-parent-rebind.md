# Durability typed-body receipt-lock policy parent rebind

Date: 2026-08-08

Status: unchanged typed body rebound to repaired structural parent.

The structural parent committed at
`a1af31e89c13a0eea72fd90a2934a0c8e0154175` is sealed at
`sha256:18fb00ff02820c31b4fcab4de096393cbea49e0a37ebb28d65c5eb2d6f154cfd`.
It adds only the fail-closed receipt row-lock visibility policy diagnosed from
attempt 042.

The typed function and trigger program is unchanged. Its body population,
operands, effects, call graph, entry points, authority boundaries and renderer
order are rebuilt deterministically with the new structural parent binding.
The resulting body seal is
`sha256:9ef411aa353ba6b39d9fbbd769d94ef5a9237bb7c6aa031dbdafce1bfa62ce83`
and must be propagated through the inert DDL, exact parse catalogue and
behavior parents before another disposable database attempt.

No SQL is mounted or executed by this rebind. It opens no provider, product,
patient, command, operational database, deployment, release, Pages or
protected-ref authority.
