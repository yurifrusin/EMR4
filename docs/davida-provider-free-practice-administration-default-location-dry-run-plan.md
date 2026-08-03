# Davida default-location dry-run proposal plan

Date: 2026-08-03

Status: provider-free, unmounted, unoccupied, authored-synthetic, dry-run only

Parent: `provider_free_practice_administration_advisory_proofreader_pass`

## Outcome

Implement exactly `PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION` as a trusted
deterministic transform over one accepted `PracticeAdministrationContextFrame`.
The component resolves one opaque active-practitioner reference and one opaque
active-location reference, then releases an exact before/after projection. It
does not read or change database truth.

The proposed result is
`provider_free_practice_administration_default_location_dry_run_pass`.

## Frozen input and output

The strict extra-forbid candidate binds the practice, principal, correlation,
context revision, timezone-aware caller-supplied evaluation time, exact
operation, practitioner and location references,
`reason_code=PRACTICE_ASSIGNMENT_UPDATE`, `risk_tier=admin_proposal`, and
literal-false confirmation/apply/write/command/provider/model/database/network/
model-to-database fields. Canonical input equality rejects Pydantic coercion.

The only released object is a non-authoritative `proposal_candidate` with
`status=dry_run_only`, evidence label
`provider_free_unoccupied_default_location_dry_run`, data class
`authored_synthetic`, exact source paths, context binding, before/after states,
one changed path, proposal/grounding hashes and expiry no later than the
context. Human confirmation is required, but no confirmation evidence or
envelope is present.

Same-location input rejects as `no_change`. Missing, duplicate, wrong-kind,
dangling, cross-scope, stale, malformed, noncanonical and authority-bearing
inputs fail closed with no partial proposal, repair or retry.

The public rejection union contains only producer-reachable outcomes. Duplicate
or dangling context references collapse to `context_boundary_invalid` before
target resolution; literal-false authority reversal fails candidate schema or
canonical admission rather than exposing an unreachable later reason.

## API Spine and authority

This is a route-free command-style dry-run artifact, not a command. GraphQL
remains read-only and unchanged. REST commands would own any later effectful
proposal/confirmation path, but no REST route, command payload, idempotency key,
aggregate version, audit/outbox event or apply affordance exists here. Events
and manifests are unchanged.

No model/provider call, memory/RAG, real identity/data, patient/clinical/
document data, database/network/clock, arbitrary API access, confirmation,
apply/write, deployment, production, release or protected action is opened.
`docs/branding/` remains excluded.

## Deterministic acceptance

Focused tests cover exact and current-null changes, repeated determinism,
reference/scope/freshness/context tampering, no-op rejection, operation and
field allowlists, canonical no-coercion admission, exact before/after/hash
binding, atomic rejection, recursive closed schema validation and static
absence of effectful dependencies. Parent boundary, pure-read, advisory, seam
and API Spine tests run serially under the shared PostgreSQL slot.
