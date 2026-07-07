# Antigravity Review - Sprint 198 Support Route Boundary

Antigravity reviewed the nine current out-of-contract appointment POST support
routes and split them into two infrastructure families:

- `proposal_support_post`: seven slot-search and Bernie proposal-support rows.
- `state_tracking_post`: two Bernie session lifecycle rows.

Recommendation:

- Make the support-route boundary explicit in documentation.
- Ensure these rows never become Diary grammar confirm routes or raw mutation
  authority merely because they are mounted under the appointment router.
- Add a static guard that detects drift in out-of-contract POST classification.

Implementation stance taken by Ariadne:

- The committed report remains aggregate-only and does not enumerate route paths.
- The guard focuses on `ambiguous_post=0`, so new support POST shapes force review
  without making the safe preflight report path-bearing.
- No route handlers, providers, database sessions, memory/RAG/GraphRAG,
  H15/H-series inputs, historical diary material, or GraphQL surfaces are opened.
