# Practitioner Directory GraphQL Contract Hardening

Sprint 271 adds no new GraphQL runtime field. It hardens the Sprint 270
`Query.practice.practitioners` implementation by proving three boundaries:

- The runtime SDL contains only the approved practitioner slice plus the shell
  `graphqlHealth` field, with no mutation, subscription, patient, appointment,
  diary, provider, memory, write, or external-client surface.
- Strawberry's installed token guard fails closed on abusive query shape, and
  currently preempts alias-flood attempts before the alias limiter is reached.
  The alias limiter remains configured for future surfaces with different token
  budgets.
- The token guard is exercised against both `graphqlHealth` and the
  `practice.practitioners` resolver path.
- The global external-readiness DAG and blocked readiness snapshot remain
  blocked even though the scoped resolver exists.
- Shell, resolver, and hardening evidence agree on the shared
  `must_remain_false` gate set.

Depth limit remains configured at `QueryDepthLimiter(max_depth=6)`. In the
current first slice, a valid query cannot structurally exceed depth six because
the exposed practitioner graph terminates at `PracticeLocationBrief { id name }`.
That is recorded as a current-slice fact, not a waiver for future deeper fields.
When any deeper GraphQL object is added, a true depth-limit negative test must be
added before that sprint closes.
