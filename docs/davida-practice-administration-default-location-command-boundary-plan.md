# Davida default-location proposal-to-confirm command-boundary plan

Date: 2026-08-03

Status: architecture-only, provider-free, non-executing

Parent: `provider_free_practice_administration_default_location_dry_run_pass`

## Outcome

Freeze a separate documentation-only REST/OpenAPI proposal-to-confirm boundary
for a future practitioner default-location change. The boundary must preserve
the accepted Davida dry run as non-authoritative input, make the trusted EMR4
backend the sole command owner, and require a freshly authorized human practice
manager or practice owner to confirm.

The proposed architecture result is
`davida_practice_administration_default_location_command_boundary_pass`.

## Frozen acceptance

- The proposal route is a non-mutating command-style read. It receives the
  accepted dry-run hash, exact practice/practitioner/location bindings and the
  expected practitioner aggregate version, then reconstructs current state and
  returns a deterministic backend-owned proposal with a maximum two-minute
  expiry. `proposal_id` is a backend-issued signed opaque self-contained
  proposal reference, verified without a proposal store. Its idempotency header
  is syntactic request discipline; it creates no proposal replay ledger and
  grants no command authority.
- The confirmation route accepts only an authenticated human with the current
  `practice_manager` or `practice_owner` role. Davida can supply provenance for
  the proposal but cannot be the confirmer, construct confirmation evidence,
  call the route or apply the change.
- Practice, actor and role authority are derived only from the authenticated
  application session. Any body fields are non-authoritative binding assertions
  that must exactly match or reject.
- Authorization occurs before resource disclosure and is revalidated against
  the exact practice/action/resource immediately before a future write.
- Confirmation echoes the proposal, practice, practitioner, requested location,
  expiry, proposal hash and expected aggregate version. The backend revalidates
  every value from current truth. It carries only an opaque backend-issued,
  server-held, one-use confirmation-evidence reference; a client cannot mint
  confirmation evidence by supplying structured claims.
- Confirmation idempotency is durable. The same key and canonical request
  fingerprint returns the same bounded receipt without another effect; a key
  with a different fingerprint is `idempotency_conflict`; replaying consumed
  single-use confirmation evidence under a different key is
  `confirmation_replay_rejected`.
- One future database transaction would claim the idempotency record, lock and
  update exactly one practitioner aggregate, increment its version once, append
  one audit event, append one outbox event and complete the idempotency receipt.
  Any failure rolls the entire unit back. Publication is after commit only.
- Stale version, stale current state, inactive or cross-practice location,
  expired proposal, changed proposal hash, insufficient role and every replay
  conflict fail closed with no partial effect or sensitive existence leak.

The two human roles are proposed future command-contract policy. Their presence
does not claim that the current prototype permission matrix or any mounted
runtime already grants either confirmation action.

## Artifacts

- `docs/api-spine/openapi/practice-administration-default-location-commands.yaml`
- a closed architecture contract and Draft 2020-12 schema under
  `orchestration/continuity/davida-practice-administration-default-location-command-boundary/`
- deterministic artifact tests and a repository-local acceptance evidence file
- design, threat-model delta and closeout documents

## Closed gates

This tranche adds no FastAPI route, `app.main` import, schema migration, ORM
model, database service, write handler, provider/model call, network access,
real identity/data, patient/clinical/document data, arbitrary API access,
GraphQL mutation, event publisher, deployment, production or release. Actual
command implementation and apply/write authority remain a material Yuri-owned
gate. `docs/branding/` is excluded and untouched.
