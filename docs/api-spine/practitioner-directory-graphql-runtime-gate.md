# Practitioner Directory GraphQL Runtime Gate

Sprint 267 records Yuri's approval for a gate packet only for
`Query.practice.practitioners`.

This packet does not add a GraphQL dependency, endpoint, schema runtime, or
resolver. It defines the surface that a later implementation sprint must satisfy
before any resolver can be considered ready.

## Runtime Choice

Preferred runtime: `strawberry-graphql`.

Reason: Strawberry has a FastAPI `GraphQLRouter`, a type-first Python model that
fits the current Pydantic/FastAPI codebase, and a direct path to mapping the
current non-runtime SDL shape.

Dependency installation is not authorized by this sprint. Exact version pinning
belongs to the later implementation sprint.

Alternatives considered:

- Ariadne: viable schema-first option, declined for the first slice because it
  adds resolver-binding boilerplate before the repo has a runtime GraphQL
  pattern.
- Graphene: mature ecosystem, declined for the first slice because it fits the
  current FastAPI/Pydantic-v2 code style less naturally.

Before installation, the implementation sprint must check the exact pinned
version, transitive dependencies, known CVEs, Python compatibility, and
conflicts with FastAPI, Pydantic, and SQLAlchemy.

## Scope

Only this future field is in scope:

`Query.practice.practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)`

The future resolver must be a thin facade over
`app/services/practice/practitioner_directory_read.py::list_practitioner_directory`.
It must not call the REST route over HTTP, import REST router modules, perform
independent SQLAlchemy queries, call providers, access memory/RAG/GraphRAG,
import H15/H-series or historical diary material, or write database/audit state.

## Auth And Errors

The GraphQL context must use the existing bearer-token principal model.

- Missing/invalid token: `UNAUTHENTICATED`
- Inactive user: `UNAUTHENTICATED`
- Practice id mismatch: `NOT_FOUND`
- `activeOnly=false` without Admin or PracticeOwner: `FORBIDDEN`
- Invalid `limit` or `offset`: `BAD_USER_INPUT`
- Unhandled resolver/internal errors: `INTERNAL_ERROR`
- Raw SQL/internal details and stack traces: never exposed

## Depth And Cost

A development depth and cost guard must exist before mounting `/api/v1/graphql`.
Production depth/cost, alias repetition, and introspection posture require a
separate deployment review. `practice.practitioners` must keep REST-aligned
defaults and bounds: `limit=50`, `offset=0`, `limit <= 200`.

Proposed development defaults for the first implementation are max depth `6`
and cost budget `500`, with alias repetition counted against the same budget.
Introspection is acceptable in dev/test only and remains blocked for production
until a deployment review.

## Required Test Matrix

The next implementation sprint must add tests for dependency pinning, endpoint
mounting, no mutation root, auth, practice scoping, role failure, argument
bounds, REST projection parity, `PracticeLocationBrief`, sensitive-field
absence, shared-read-service use, closed provider/memory/H15/trove/write imports,
depth/cost fail-closed behavior, alias repetition cost, generic internal-error
mapping, empty-practice behavior, ordering, offset, and the 200-row cap.

GraphQL resolver readiness remains false until those tests pass and the
implementation is separately reviewed.
