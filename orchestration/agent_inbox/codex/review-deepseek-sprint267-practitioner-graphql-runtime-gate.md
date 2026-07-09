# DeepSeek Review - Sprint 267 Practitioner GraphQL Runtime Gate

Status: PASS

Reviewer lane: DeepSeek Worker the 4th

Scope reviewed:

- Sprint 267 GraphQL runtime/resolver gate packet for
  `Query.practice.practitioners` only
- Sprint 266 SDL alignment evidence
- Practitioner-directory REST route/read-service prerequisites
- API-spine GraphQL read-only boundary

Findings:

- The repository is ready for a runtime/resolver gate packet, not resolver code.
- The gate must define runtime library choice, auth context, error taxonomy,
  depth/cost/alias posture, dependency security risks, and resolver tests.
- Strawberry is the recommended first candidate because of FastAPI integration
  and a type-first Python model that fits the current codebase.
- Dependency installation and server/resolver wiring are still a separate
  decision unless explicitly approved.
- Required tests must cover positive, negative, and boundary behavior:
  auth, practice scoping, role failure, argument bounds, projection parity,
  default-location shape, sensitive-field absence, shared-read-service use,
  no REST-router/HTTP bypass, no provider/memory/H15/trove/write imports, and
  depth/cost fail-closed behavior.

Accepted recommendation:

- Keep this Sprint 267 artifact as a gate packet only. It records Strawberry as
  preferred and defines implementation requirements, but does not add the
  dependency, endpoint, schema runtime, or resolver code.

Verdict:

PASS. The packet can proceed if it keeps all runtime and adjacent readiness gates
false and names the next step as a separate implementation sprint.
