# Sol acceptance — provider-free structured diagnostic bounded-worker controller convergence

Date: 2026-08-21

Decision: **accepted**

I accept exact candidate
`ba2e8b1c06acfe88f9f11afa1a58c1371d0cfa3c` as the narrow provider-free
controller convergence.

The result binds the accepted wrapper and v2 reader through a descendant of the
historical bounded-worker controller, selects v2 only for canonical exact-
identity sidecars, retains v1 while failing closed for missing or invalid
sidecars, persists the safe terminal before cleanup, and leaves the base
controller plus all consumed evidence byte-identical. The 43-test focused suite,
deterministic evidence, schema checks, Ruff and compilation pass with zero
Harness, worker, model or provider activity.

This acceptance does not authorise a fresh occupied attempt. The dependency-
satisfied successor is a provider-free repair of the historical startup-
terminal validator's mutable-source coupling, followed by a separately frozen
attempt-004 readiness decision.

