# Sprint 195 Out-of-Contract POST Route Classification Review

| Field | Value |
|---|---|
| Agent | Antigravity/Gemini |
| Branch | `antigravity/current` |
| Kind | Independent backend-readiness review |
| Scope | Static appointment route inventory preflight only |

## Findings

Antigravity inspected the mounted FastAPI appointment routes and found the
current out-of-contract POST method rows divide into two broad static shapes:
proposal-support POSTs and Bernie session/state-tracking POSTs. The review
recommended keeping this as a path-pattern classification over route metadata
only, with no handler execution or route-path output.

## Recommended Shape

- Keep the existing aggregate method-family count as the compatibility anchor.
- Add a separate POST sub-family count rather than replacing
  `query_or_command_post`.
- Use fixed, path-free labels such as `proposal_support_post`,
  `state_tracking_post`, and `ambiguous_post`.
- Keep an explicit false guard:
  `out_of_contract_post_rows_are_grammar_dispatch_authority=false`.

## Invariants

- POST sub-family counts must sum to the out-of-contract POST method-row count.
- Out-of-contract POST method-row count must remain within total
  out-of-contract method rows.
- Report serialization must remain path-free and ID-free.
- Runtime/provider/database/write boundary flags must remain false.

## Boundary

The review did not recommend adding these routes to
`DIARY_ACTION_ROUTE_CONTRACTS`. The classification is a planning signal for
later route-contract review, not authority to dispatch, confirm, mutate, call a
provider, or open any H15/H-series or historical-diary gate.
