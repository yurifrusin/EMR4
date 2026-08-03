# Sol acceptance: Davida default-location proposal-to-confirm boundary

Date: 2026-08-03

Accepted result:
`davida_practice_administration_default_location_command_boundary_pass`

## Decision

Accept as architecture-only and non-executing. The separate documentation-only
OpenAPI artifact freezes a backend-owned proposal-to-confirm path for exactly
one future practitioner default-location change. Application-session truth,
fresh practice/action/resource authorization, current aggregate state, expected
version, server-held one-use confirmation evidence, durable idempotency and one
atomic aggregate/audit/outbox/receipt transaction own the boundary.

Davida can propose only. It cannot mint confirmation evidence, confirm, call or
apply the command. `practice_manager` and `practice_owner` are proposed future
contract roles, not current runtime grants. GraphQL remains read-only, the
appointment command contract remains unchanged, and no route, model, migration,
database service, event publisher or write handler was added.

## Verification

- 31 focused architecture tests and 36 API Spine tests passed in serialized
  worker/root runs; the root integrated gate passed 133 tests.
- Fresh Gemini 3.6 Flash/high returned one exact pass with zero findings and 101
  verifier tests on unchanged HEAD `f551a91d861baa65d04fae8f50dfee0a52440035`.
- Contract/schema/OpenAPI parsing, source hashes, Ruff and diff/path gates
  passed.
- Actual command implementation, permission runtime, migration, storage,
  signing-key lifecycle, mutation, audit/outbox dispatcher and apply/write
  authority remain a material Yuri-owned gate.

Reasoning level: High for accepting the frozen architecture-only contract;
future implementation requires the separately retained material decision.
