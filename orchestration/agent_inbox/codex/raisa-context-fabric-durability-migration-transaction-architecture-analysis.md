# Durability migration-and-transaction architecture analysis

Date: 2026-08-06

Status: plan input; no acceptance authority

Source HEAD:
`6862572e3bca3a1f1e4b999c6c66cef30b7b61fa`

## Read-only lane synthesis

Two bounded native lanes independently rehydrated from all five authoritative
sources and inspected only the accepted durability/API/security and exact
static PostgreSQL convention surfaces. Both left the tracked worktree and all
refs unchanged and made no database, provider, product-data, runtime or network
call.

The PostgreSQL lane identified caller-set custom-GUC tenancy as unsafe. Its
narrow correction is an owner-controlled binding from actual authenticated
`session_user` to exact logical capability, practice, source and credential
epoch, enforced through hardened entry points with forced RLS only as defense
in depth. It recommended closed normalized relations, a transactional stream
head, payload-free outbox, independent generation anchors, a total-order
lifecycle journal, `SERIALIZABLE` coordinator/key/retention transactions,
separate retention families and whole-transaction bounded retries.

The API/security lane found no user-owned fork. It required internal async
classification with unchanged GraphQL and REST/OpenAPI, no new route,
subscription, acknowledgement, generic database procedure or event-driven
fresh read. It required exact non-overlapping principal ceilings, complete
backend-derived retention census, immutable independent recovery anchors,
future-fenced key intervals, minimized audit and adversarial proof that the
existing staff feed/cursor cannot satisfy durability authority.

## Sol resolutions

- preserve the parent contract's distinct outbox name and its one non-semantic
  raw event UUID; the observer domain-separates and discards it before receipt
  or audit;
- keep stream epoch `1` for this exact source-contract version; disabling an
  enabled producer cannot silently resume under a runtime-incremented epoch;
- use `READ COMMITTED` plus explicit row locks for the existing producer
  transaction, and `SERIALIZABLE` for coordinator, rotation and retention;
- persist no convenience exact obligation counter; derive its closed bucket
  from canonical admitted history under the checkpoint lock;
- order decisions and key rotations through one lifecycle journal; and
- freeze retention execution disabled by default while deferring production
  duration/capacity and key-store selection to later operational gates.

These are architecture-strengthening choices within the planned sequence, not
a fresh user decision fork.
