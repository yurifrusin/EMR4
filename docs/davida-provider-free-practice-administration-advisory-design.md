# Davida provider-free practice-administration advisory design

Date: 2026-08-03

Boundary classification:
`provider_free_unoccupied_deterministic_practice_administration_advisory_proofreader`

## Topology

```text
accepted authored-synthetic PracticeAdministrationContextFrame
  + frozen selector-only advisory candidate
  -> deterministic Davida-specific proofreader (this tranche)
       -> strict released advisory draft OR closed rejection
  -> no command, database, network, provider, event or product egress
```

The future probabilistic work cell remains absent. The proofreader is the
trusted deterministic boundary, but it does not authorize reads, commands or
writes; it only checks and transforms already supplied context.

## Candidate grammar

Common fields bind schema v1, practice/principal/correlation refs, exact context
revision, `authority_class=advisory`, three literal-false authority flags and a
caller-supplied evaluation time. Explain adds exactly a closed subject kind and
one opaque reference. Summary adds nothing. Extra fields and Pydantic-coercible
but noncanonical values fail closed.

## Context admission

The exact parent model is validated and dumped back to JSON; raw and canonical
forms must be equal. Blocked sources, live-API-fact labels, pure/active-only
source declarations, authority ceiling and non-authoritative labels must equal
the accepted constants. Observed/expiry values must be timezone-aware and
exactly two minutes apart. Frame counts must equal row lengths, references must
be globally unique, and every default-location reference must resolve to one
supplied active location. The parent content revision is independently
recomputed over the canonical frame excluding only `content_revision`.

## Operation-specific derivation

- Summary derives four bounded counts from actual row lengths and nullable
  fields. Empty frames are valid.
- Practitioner explain resolves the subject once in practitioner rows, rejects
  a location-kind collision, and copies only resource ref, display name,
  nullable role, active true and nullable default-location ref. A default
  location must resolve once.
- Location explain resolves the subject once in location rows, rejects a
  practitioner-kind collision, and copies only resource ref and name.

No candidate-supplied fact value reaches output. Grounding hashes the sorted
source paths together with the accepted context revision and the exact derived
payload. The draft also repeats the exact context binding.

## Atomic result

Draft validation completes before a released result is built and validated.
Any candidate/context fault returns only the rejected arm, never a partial
draft. An internally constructed invalid draft raises a programming invariant
error rather than being relabelled as candidate rejection. There is no repair,
retry, inference, lookup or mutation.

## API Spine and gates

This is a context-frame transform, not GraphQL execution. It creates no query,
mutation, REST command, event, manifest or audit/idempotency surface. Provider,
model, memory/RAG, database/network, real identity/data, patient/clinical data,
proposal/apply/write, cloud/IAM, deployment, production, release and protected
actions remain closed.
