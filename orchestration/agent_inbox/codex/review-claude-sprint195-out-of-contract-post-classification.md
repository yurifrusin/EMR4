# Review - Sprint 195 Out-of-Contract POST Classification

| Field | Value |
|---|---|
| Agent | Claude |
| Branch | `claude/current` |
| Kind | Bounded backend-readiness review |
| Scope | Static appointment route inventory preflight only |

## Verdict

Proceed. Sprint 195 can safely add a POST-only sub-classification axis to the
existing count-only appointment route inventory report, provided it stays
anchored to the current `query_or_command_post` method-family count and does
not add Diary grammar authority.

## Recommendations

- Add `out_of_contract_post_route_method_count`.
- Add a count-only POST sub-family field, with fixed enum labels rather than
  route paths or path fragments.
- Add `out_of_contract_post_rows_are_grammar_dispatch_authority=false`.
- Assert that the POST method-row count equals
  `out_of_contract_by_method_family["query_or_command_post"]`.
- Assert that the POST sub-family counts sum to the POST method-row count.
- Extend path-leakage tests so new labels do not emit route paths, handler
  names, IDs, request-body fields, or local material paths.

## Risks

- A label such as `confirm_like` can be misread as dispatch authority. Keep the
  explicit false authority flag and document that this is a planning signal.
- Do not inspect handlers, request bodies, database behavior, or provider
  behavior. The classifier must use static route table metadata only.
- A rising catch-all sub-family count should be treated as a future review
  signal, not as automatic evidence that routes belong in the Diary action
  contract.

## Gates

No blocked gate is touched if the change remains static and aggregate-only: no
runtime route wiring, provider calls, memory/RAG/GraphRAG, H15/H-series runtime
imports, historical diary material, GraphQL mutation, or model-to-database
writes.
