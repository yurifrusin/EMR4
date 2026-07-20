# Reception One availability reconciliation — baseline regression comparison

**Candidate source:** `e469fd60d37ab536152eda8e2cc4997431817110` plus the bounded client tranche  
**Untouched baton baseline:** `e469fd60d37ab536152eda8e2cc4997431817110`  
**Disposition:** no candidate regression in the two observed legacy nodes

The canonical current populations pass. A deliberately broader run added
`tests/test_location_scoped_diary.py` to all current `test_diary_*.py` files and
produced 227 passes plus two failures:

- `test_create_single_location_conflicts_with_legacy_unscoped` expected 409 and
  received the current 422 validation response; and
- `test_create_allows_same_practitioner_at_different_locations` expected 201
  and received the current 422 validation response.

Both exact nodes reproduced unchanged in a clean detached worktree at the
untouched baton source head. This tranche changes no backend route, request
schema, location model or test fixture involved in either observation. No test
or product source was changed to conceal them.

The current acceptance gates passed serially:

- 165 current Reception One, committed-event, functional/live-local,
  combined-scope, update-confirm route, API Spine, Stage 1 proposal, Stage 3A,
  accessibility, handover and Ariadne tests;
- 211 current `test_diary_*.py` tests; and
- the explicitly named 139-case `review/test_diary_smoke.py` population.

