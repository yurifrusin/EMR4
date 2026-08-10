# Durability typed-body outbox-select-policy parent rebind

Date: 2026-08-08

Status: deterministic parent rebind complete; body semantics unchanged.

The byte-unchanged typed function/trigger body contract now binds structural
parent `sha256:30401808c97e45ad0ecf23242a21c1b7be35bc7d37343bb2f1ab4ef139e83a5f`
from exact task commit `e1ca28915b09636e5d9d693216beef450f71a356`.
The sole parent change adds `COORDINATOR` logical visibility to the existing
forced-RLS outbox SELECT policy without adding any direct table grant.

No typed body program, node, predicate, failure mapping, call edge, effect,
entry point or trigger changed. The resealed body digest is
`sha256:9b079af00e46b5e18f464cc39f9283ce400ee7b2621d875a127af19cb908ee62`.

The broad descendant check also exposed historical continuity assertions that
treated this accepted node as the forever-last graph node and froze global
Compass and error-register revision counters. They now locate the accepted
body node by its immutable ID and source HEAD, require monotonic revision
bounds, and continue to prove its closed authority regardless of later graph
growth. The former admission-lock note remains bound to its own parent; this
new outbox-policy note is the exact current-parent evidence.

This architecture remains unmounted and non-executable. Inert DDL regeneration,
fresh parse/catalogue proof, behavior-parent rebind, independent veto and any
further disposable behavior attempt remain separate closed descendants.
