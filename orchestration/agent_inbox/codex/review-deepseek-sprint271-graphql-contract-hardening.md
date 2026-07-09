# DeepSeek Review - Sprint 271 GraphQL Contract Hardening

Verdict: PASS.

DeepSeek reviewed the hardening sprint for the existing GraphQL practitioner
first slice. The review confirmed no new runtime fields were added beyond
`graphqlHealth`, `Query.practice(id)`, and
`Practice.practitioners(activeOnly, limit, offset)`, and found no mutation,
subscription, provider, memory/RAG/GraphRAG, H15/trove, write, audit-write,
deployment, production, or external-client gate opening.

Integrated recommendations:

- Document that a true depth-limit negative test is not structurally reachable
  in the current shallow practitioner graph and must be added when deeper
  objects are introduced.
- Record that the 500-token limiter preempts 501-alias attacks in Strawberry
  0.320.3, while the alias limiter remains configured.
- Add a practitioner-path token-budget negative test.
- Broaden readiness snapshot assertions and cross-check the shared
  `must_remain_false` key set across shell, resolver, and hardening evidence.
