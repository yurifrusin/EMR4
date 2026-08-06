# Sol recovery lease — observation-to-temporal-signal rehearsal

Date: 2026-08-06

Status: active

Untrusted reviewed source HEAD:
`79aac4333035b72281fb6a47033b78c04c0969e0`

Authority basis:
`docs/ariadne-orchestrator-recovery-lease.md`

## Trigger

The bounded implementation worker consumed one same-lane correction after
Sol rejected its first direct-validator candidate. A fresh independent veto
then found two semantic P1 defects: the mapper contradicted the admitted
raw-id/clock/prior domain by accepting only one literal fixture, and exported
low-level functions permitted signal egress without the required same-packet
proofreader.

No further same-lane worker correction is permitted. GPT Sol adopts the source
only as an untrusted candidate and owns every subsequent amendment and claim.

## Exact recovery

Sol may:

1. make admission and mapping internal implementation details rather than
   exported release surfaces;
2. ensure admitted grammatical raw ids, valid backend clock values and valid
   sealed prior coordinates map without canonical-fixture reconstruction;
3. expose only proofreader-gated packet release as the signal-bearing public
   egress;
4. retain internal deterministic admission classification for focused tests
   without representing it as released output;
5. add adversarial tests proving alternate valid contract coordinates map and
   that the exported surface cannot release an unproofread signal; and
6. regenerate only the owned continuity evidence affected by source/test
   hashes.

## Forbidden scope

No source/database/outbox/feed/watcher/listener, persistence/checkpoint,
product read, patient/product/protected data, provider, API/app route,
GraphQL/REST command, mutation/write, runtime mount, deployment, production,
release, Pages or protected-ref action. Preserve `docs/branding/` and every
unrelated untracked receipt, state, evidence and cost-ledger artifact.

## Recovery acceptance

The corrected task-branch candidate must pass the full focused and inherited
serial packets, compile/lint/format, schema, byte-reproduction, static-surface
and diff checks. The independent veto must be preserved in the agent-error
register before acceptance, and a genuinely fresh read-only exact-head veto
must return one terminal `pass`. The failed worker receipts and first veto are
never rewritten.

## Fresh-veto continuation

The first Sol recovery commit
`d3ce636a6ed12828a45eb0d17a2d5b8251e1a511` remained untrusted after a fresh
exact-head veto found that mapping enforced one-sided timestamp ordering while
admission deliberately permits absolute clock skew in either direction. This
is inside recovery item 2 above, so the same lease remains active. Sol must
make mapping mirror the exact two-sided admission bound, add positive-skew
coverage and obtain another genuinely fresh exact-head veto. No scope or
authority boundary is widened.
