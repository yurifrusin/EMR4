# Davida default-location dry-run proposal design

Date: 2026-08-03

Boundary classification:
`provider_free_unmounted_default_location_proposal_dry_run`

## Topology

```text
accepted authored-synthetic PracticeAdministrationContextFrame
  + canonical selector-only default-location candidate
  -> trusted deterministic resolver and proofreader
       -> exact non-authoritative before/after proposal candidate
       -> OR one closed rejection with no partial proposal
  -> no route, command, confirmation, apply, database or network egress
```

The future Davida probabilistic cell remains unoccupied. The resolver never
reads the clock; `evaluated_at` is supplied by the caller and checked in the
half-open accepted context interval.

## Admission and resolution

Operation allowlisting happens before schema interpretation. The candidate is
strict, extra-forbid, scope/revision bound and canonical-equality checked.
Trusted code revalidates the exact parent context shape, two-minute lifetime,
content revision, source declarations, row counts, unique opaque references,
default-location integrity and literal-false authority ceiling.

The target practitioner and location must each resolve exactly once in their
correct active-only frame. Missing, duplicate, wrong-kind and cross-frame
references reject. The current default location is copied exactly from the
practitioner context row, including `null`; the requested active location is
copied into the after state. A same-location request is `no_change`.

## Released artifact

The released `proposal_candidate` / `dry_run_only` artifact changes only
`practitioner.default_location_ref`. Both states retain the same practitioner
reference. `proposal_hash` binds the canonical candidate, context revision,
source paths and states; `grounding_hash` independently binds the context,
canonical candidate, sorted source paths and states. Expiry is copied from the
context.

The artifact says human confirmation is required while every command-ready,
confirmation, apply, write, provider, model, database, network and
model-to-database authority field remains false. It contains no confirmation
evidence/envelope, command route/payload, idempotency key, aggregate version,
audit/outbox event or apply affordance.

## API Spine and gates

GraphQL remains read-only and unused. This dry-run is not a REST command; a
future effectful action would require a separately authorised backend-owned
REST proposal/confirmation command with fresh authorization, concurrency,
idempotency and audit. Events never grant authority and manifests remain
declarative.

Provider/model, memory/RAG, real identity/data, patient/clinical/document data,
database/network, arbitrary API access, confirmation/apply/write, deployment,
production, release, protected evidence/ref and branding authority remain
closed.
