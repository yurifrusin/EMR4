# Sol acceptance — provider-free unmounted status transaction-kernel protocol

Date: 2026-08-12

Accepted source: `bd381de83bc0b5d4b6b43b4bbb4e1e70a68d7f62`

Decision: `accepted`

Accepted result:
`raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal_pass`

Sol accepts the closed packet and evidence as the narrow transaction-semantic
proof required before any status-confirm adapter or runtime work. Fifteen
decision cases, eleven schedules and thirty-seven hostile mutations establish
authority-first receipt disclosure, exact lock ordering, separate confirmation,
freshness and idempotency checks, commit/rollback atomicity, durable response-
loss recovery and typed loser outcomes.

The terminal-transition rule remains deliberately unresolved at the product
policy layer. The accepted protocol returns an effect-free policy-deferred
rejection. The next adapter contract must preserve current fail-closed behavior
until an explicit policy is accepted.

This acceptance grants no runtime, route, database, provider, watcher, event,
tool, command, operational data, product/patient data, deployment, production,
release, Pages or protected-ref authority.

The prior compatibility source citation is corrected in the live baton and
Continuity graph to the actual Git object
`48c1821ad8b28c68204e70dea9972b6ba27e4dc1`; historical closeout evidence is
not rewritten.
