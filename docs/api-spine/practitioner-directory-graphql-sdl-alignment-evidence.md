# Practitioner Directory GraphQL SDL Alignment Evidence

Sprint 266 aligns the non-runtime GraphQL SDL with the practitioner-directory
REST projection after the named REST consumer evidence passed in Sprint 265.

The SDL now declares:

- `Practice.practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)`
- `PracticeLocationBrief { id, name }`
- `Practitioner.defaultLocation: PracticeLocationBrief`

This resolves the former default-location shape drift and pagination-argument
drift recorded in the Sprint 229 REST/GraphQL drift contract.

Boundary: this is SDL/document/test alignment only. It does not add a GraphQL
runtime dependency, GraphQL server, GraphQL resolver, GraphQL mutation, runtime
database path, provider call, memory/RAG/GraphRAG path, H15/H-series/trove path,
write authority, deployment claim, or production-readiness claim.

Next step: a separate GraphQL runtime/resolver approval packet can define the
exact server/resolver implementation gate. GraphQL readiness remains false
until that runtime work is implemented and verified.
