# Davida practice-administration boundary plan

Date: 2026-08-03

Status: architecture-only, provider-free, non-executing

Reasoning level: bounded DeepSeek V4 Flash/high implementation worker under
Claude Code `--bare`; root GPT Sol owns material architecture, authority and
security decisions.

## Objective

Freeze the first bounded Davida lane descendant of the accepted
Bernie/Davida parallel seam: the architecture-only Practice Administration
boundary. This tranche defines Davida as a separate custodian work-cell /
container / agent identity over a shared mechanical kernel, with no database
truth ownership, no database credential, no ORM session, no generic database
client, no GraphQL mutation, no REST command credential and no event actuator.

Davida is the custodian interface for relatively stable institutional
knowledge. It is never the owner of database truth and never an autonomous
database actor. This tranche changes no product runtime, opens no provider,
container, route, database migration, product read, command, deployment or
protected-ref movement, and makes no runtime claim.

## Standing authority

The accepted seam `bernie_davida_parallel_seam_pass` records Yuri's standing
authority for bounded logical descendants in the Davida Practice Administration
lane. The seam freezes the Davida lane sequence:

1. architecture-only boundary (this packet);
2. provider-free read and dry-run proposal contracts;
3. one reversible administrative proposal vertical with no apply command;
4. a later human-confirmed command candidate only after the preceding contract
   and risk tier are accepted without a material fork.

Material architecture or product-behaviour forks, new providers/cost/licence,
real patient/clinical/identity data, actual administrative apply authority,
cloud/IAM, deployment, production, release, protected evidence/holdouts,
protected refs and economically preferable manual intervention return to Yuri.

## Scope

### Owned paths

- `docs/davida-practice-administration-boundary-plan.md`
- `docs/davida-practice-administration-boundary-design.md`
- `docs/security/davida-practice-administration-boundary-threat-model-delta.md`
- `orchestration/continuity/davida-practice-administration-boundary/capability-contract.json`
- `orchestration/continuity/davida-practice-administration-boundary/capability-contract.schema.json`
- `tests/test_davida_practice_administration_boundary.py`

### Forbidden paths

`AGENTS.md`, `docs/branding/`, application/runtime code, routers, models,
migrations, `app/main.py`, API Spine artifacts, shared auth, existing agent
charters, workflows, harness settings, protected evidence and other agents'
files. No other file is edited.

## Frozen architecture decisions

- Davida is a separate cell/container/agent identity from Bernie. Each keeps an
  independently pinned immutable policy (proofreader policy, capability
  manifest, call budget, network allowlist, default-off feature gate,
  credentials). Only the provider-neutral mechanical kernel, typed envelopes,
  deterministic proofreader primitives and audit vocabulary are shared.
  Policies, scopes, memory and credentials never cross.
- Davida receives no database credential, ORM session, generic database
  client, GraphQL mutation, REST command credential or event actuator. There is
  no model-to-database path.
- Authoritative structured practice state, advisory provenance-bearing
  interpretation, bounded expiring session/context state and declarative
  manifest policy are four distinct stores and authority classes. Database
  truth remains authoritative; advisory interpretation never becomes roster,
  policy, confirmation or command truth.
- The read/context desk accepts only pure side-effect-free projections. The
  active-practitioner projection `Query.practice.practitioners` /
  `list_practitioner_directory` is the eligible precedent. A future
  active-location source must be a pure projection before admission.
- The current room and waiting-list GET paths are explicitly blocked because
  inspection proves they normalize and commit during a nominal read:
  `GET /api/v1/diary/rooms` and `GET /api/v1/diary/waiting-areas`. The live
  appointment `GET /api/v1/appointments/waiting-room` queue is also blocked as
  patient-linked closed data.
- Davida uses a closed operation enum for the first safe administrative domain
  (practitioner lifecycle administration). Unknown operations fail closed.
- Davida emits typed advisory drafts and typed proposal candidates only. It
  never emits a human confirmation envelope, a signed command,
  `writes_authorized=true` or any release envelope that can mutate state.
- Future writes are backend-owned REST/OpenAPI proposal and confirmation
  envelopes carrying practice binding, actor/session binding, candidate hash,
  expiry, idempotency, optimistic concurrency/precondition, least-privilege
  authorization and audit fields. Trusted backend code constructs command
  authority only after explicit human confirmation.
- Events are hints that may request a fresh authorized read. Their payloads are
  never truth and never commands. Davida holds no event actuator.
- The conservative four-tranche sequence after this architecture is: (1) pure
  read projections, (2) provider-free typed interpretation/proofreading, (3)
  one bounded proposal path, then (4) one separately authorised confirmed write
  vertical.
- Providers, real identity, patient/clinical/document data, autonomous
  writes, memory/RAG/GraphRAG, deployment, production and release remain
  closed. No runtime is claimed.

## Acceptance

- `capability-contract.json` validates against `capability-contract.schema.json`.
- Tests prove Davida identity/policy separation from Bernie, the shared kernel
  boundary and the four distinct authority classes.
- Tests prove every forbidden authority is absent (`database_credential`,
  `orm_session`, `generic_database_client`, `graphql_mutation`,
  `rest_command_credential`, `event_actuator`).
- Tests prove the room/waiting GET paths that normalize/commit are blocked and
  the active-practitioner projection is side-effect-free.
- Tests prove the closed operation enum and fail-closed unknown handling.
- Tests prove Davida's emission ceiling excludes confirmation,
  `writes_authorized=true`, signed commands and mutating release envelopes.
- Tests prove future command envelopes are backend-owned and constructed only
  after explicit human confirmation.
- Tests prove event semantics are hint-only and the four-tranche sequence is
  present.
- `git diff --check` passes; `docs/branding/` remains absent from the staged
  index, test scope and intentional patch.
