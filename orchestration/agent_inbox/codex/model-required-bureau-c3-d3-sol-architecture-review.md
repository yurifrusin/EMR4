# Sol architecture/API/security review: Bureau C3/D3

Date: 2026-08-04

Source HEAD: `3008cdb4d7b5801c45024f7361fb4294aa76fc48`

Decision: `pass_for_fresh_independent_veto`

## Scope reviewed

Provider-free, non-executing C3 recovery risk/authority policy and D3 staged-
promotion/rollback architecture only. No provider/model path, product or
patient data, live read, runtime, command, actuator, download/import/migration,
activation, deployment, release, Pages or protected surface is included.

## Review result

- C3 separates the untrusted recovery candidate from the backend-owned
  authority decision. Risk is derived monotonically from closed operation,
  target, blast-radius and reversibility fields; candidate prose cannot lower
  it. The five plan tiers map to exact Gate-zero authority classes.
- The decision binds a canonical plan hash, earliest evidence expiry, reviewer
  roles/counts and invalidation on amendment or supersession. The model does
  not mint an effective idempotency key. Command and actuator gates remain
  closed and `execution_authorized` is always false.
- D3 preserves four distinct future command families and class-specific canary,
  review, activation-barrier and rollback rules. Database transaction/
  maintenance-barrier proof is distinct from pointer atomicity.
- Source attestation, licence/lifecycle, semantic delta and rollback
  eligibility are required inputs. A withdrawn/expired reference or policy
  artifact is not eligible merely because it was previously active.
- Shadow and canary stages are non-authoritative; pre-canary and post-canary
  review are separate; activation and rollback success require independent
  fresh authoritative readback. Fail-closed terminal states are explicit.
- API Spine alignment is intact: GraphQL remains read-only; future effects are
  class-specific REST/OpenAPI commands and remain closed; events are hints;
  manifests are declarative; Access AI is closed.
- The C3 and D3 native worker advisories were bounded, source-bound and
  non-accepting. Their material findings were reconciled into the Sol-owned
  schemas rather than adopted as authority.

## Deterministic evidence

Four closed Draft 2020-12 schemas and three canonical examples pass. The
acceptance harness proves five C3 tiers, four D3 class mappings, four C3 denial
paths, six D3 denial paths, canonical plan/expiry binding, class-specific
database barriers, immutable audit/readback boundaries and nineteen zero side-
effect counters. The focused inherited Gate-zero, successor-lane, API Spine and
standing-authority regression contains 182 passing tests. Ruff, evidence
staleness and `git diff --check` pass.

## Residual boundary

This candidate may claim only `provider_free_c3_d3_architecture_and_proof`.
The mandatory intelligent provider loop, live technical observation, reviewer
identity, command implementation, canary, updater/importer, actuator,
transactional activation, database migration/restore, deployment, production
and release remain unproved and closed.

No unresolved Sol finding remains. Because this tranche freezes material
recovery/update authority architecture, one fresh Gemini 3.6 Flash/high
source-only veto is required on an exact clean candidate before acceptance.
