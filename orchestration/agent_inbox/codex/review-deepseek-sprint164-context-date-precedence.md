# DeepSeek Sprint 164 Review - Context Date Precedence

## Scope

Read-only review of Sprint 164 context-date precedence fixtures:

- `tests/fixtures/bernie_scenarios/interpret_context_date_precedence_selected_diary.yaml`
- `tests/fixtures/bernie_scenarios/interpret_context_date_precedence_selected_proposal.yaml`
- `tests/fixtures/bernie_scenarios/README.md`
- `orchestration/agent_inbox/antigravity/antigravity-sprint164-context-date-precedence.md`

Claude remained session-limited, so this DeepSeek lane acted as the replacement
second review lane.

## Verdict

Approved with no blocking findings. The fixtures correctly prove the current
date context precedence contract:

1. `selected_proposal` wins over `selected_diary_appointment` and
   `visible_diary_page`.
2. `selected_diary_appointment` wins over `visible_diary_page`.

The fixtures remain fake-provider, route-level contract tests and do not open
provider/live backend, H15/H-series, historical trove, memory, RAG, GraphRAG, or
write gates.

## Findings

- Medium observation: the new fixtures assert `assumptions.0.assumed_value`,
  which no earlier nearby fixture asserted. DeepSeek traced the route path and
  confirmed the assertion is correct for these instructions because the date
  context assumption is the only generated assumption. Codex kept the assertion
  after local scenario replay verified it.
- Low: the precedence chain is proven, and the transition table checks frame
  types in precedence order rather than request serialization order.
- Low: README and Antigravity review packet are accurate and boundary-safe.

## Deferred Suggestions

- Add a future fixture for the no-context fallback path, proving omitted dates
  with no selected proposal, selected diary appointment, or visible diary page
  context ask for clarification.
- Consider a future warning-code assertion if resolver warning codes become a
  stable fixture assertion surface.

