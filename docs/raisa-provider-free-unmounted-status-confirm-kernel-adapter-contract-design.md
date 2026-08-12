# Provider-free unmounted status-confirm kernel adapter contract design

Date: 2026-08-12

Status: `frozen_unmounted_design`

The adapter has three pure stages: admit the closed transport shape; intersect
it with server-owned current authority and state; then construct one immutable
kernel request. Client assertions never create practice, actor, role, session,
authority, current-state or evidence-verification facts.

Stops precede request construction in this order: structure, exact operation
and status-only variant, idempotency identity, current authority/session,
explicit confirmation and proposal safety, signed-evidence verification,
freshness and current-target binding, exact warning acknowledgement, then the
terminal-transition policy boundary. This order prevents stored-receipt or
current-state disclosure to a revoked actor.

The request contains no signature or credential. It carries opaque binding
digests, the normalized status command, source version, exact lock plan and
`effect_authority: false`; only the later transaction kernel could turn it into
an effect.

Kernel results are not success-shaped by inference. `committed` uses its
canonical stored receipt; `idempotent_replay` returns that same receipt;
expected losers map to their closed code; and the status-impossible
`schedule_conflict` releases nothing. Delivery serialization is outside the
commit claim and is recoverable only by replaying the stored receipt.
