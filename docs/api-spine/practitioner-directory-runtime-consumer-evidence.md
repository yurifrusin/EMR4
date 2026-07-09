# Practitioner Directory Runtime Consumer Evidence

Sprint 265 records route-intercepted browser evidence plus backend route
evidence for the first approved internal runtime consumer of
`GET /api/v1/practice/practitioners`.

Approved consumer:
`office_addin_diary_booking_practitioner_selector`.

## Evidence

Browser evidence lives in `review/test_diary_smoke.py`:

- `test_practitioner_directory_route_data_populates_booking_selector`
- `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra`
- `test_practitioner_directory_401_fails_closed_with_auth_banner`
- `test_practitioner_directory_smoke_mode_does_not_call_route_and_uses_template_fallback`
- `test_practitioner_directory_limit_200_cap_renders_all_returned_rows`

The browser checks load the non-smoke authenticated Diary path, observe one
`GET /api/v1/practice/practitioners?activeOnly=true&limit=200` request through
the existing bearer-token `apiFetch` path, open the booking practitioner
selector, verify route UUID/display-name/default-location rendering, and prove
legacy AHPRA fallback still works for older unmapped columns.

They also prove a practitioner-directory 401 fails closed through the existing
auth banner and token-clearing path, smoke mode does not call the route and uses
template fallback, and 200 returned rows render into the selector.

Backend evidence remains in `tests/test_practitioner_directory_route.py`, which
covers auth denial, role access, inactive-scope restriction, practice scoping,
default-location scoping, sensitive-field absence, and the `limit <= 200`
contract.

## Boundary

This evidence does not claim deployment, production, external patient-client,
write, provider, memory/RAG/GraphRAG, H15/H-series, historical diary, or
GraphQL resolver readiness.

The accepted remaining limit is the backend `limit=200` cap. Pagination UI is
not implemented in the Diary selector. If a practice exceeds 200 active
practitioners, a later REST pagination or GraphQL pagination design must handle
that explicitly.

## Follow-On

The named REST consumer evidence passes. The next best sprint block is
practitioner-directory GraphQL SDL/resolver alignment, keeping GraphQL readiness
false until that work is separately implemented and verified.
