# DeepSeek Review - Sprint 265 Practitioner Runtime Consumer Evidence

Status: PASS

Reviewer lane: DeepSeek Worker Shen the 4th

Scope reviewed:

- Sprint 264 wiring commit `3c48ab59`
- Practitioner-directory REST consumer evidence needed before GraphQL

Required evidence checks identified:

- route-intercept evidence that `GET /api/v1/practice/practitioners` is called
  with `activeOnly=true&limit=200` and an authorization header;
- practitioner-directory 401 behavior fails closed through the auth banner;
- tenancy/practice scoping remains token-derived and backend-tested;
- sensitive fields are absent from browser-visible selector behavior;
- `limit=200` cap behavior is documented and exercised;
- smoke mode does not call the route and keeps template fallback;
- no-write, no-provider, no-memory, no-H15/trove guards are reconfirmed by the
  static and backend route suites.

Accepted risks:

- The selector has no pagination/search UI yet. This is acceptable for the
  first internal consumer, but any practice above 200 active practitioners needs
  an explicit later REST pagination or GraphQL pagination design.
- Practice scoping correctly relies on the bearer token/current user rather
  than a client-supplied practice header.

Verdict:

PASS. Sprint 265 should collect the route-intercept/browser evidence and
backend route evidence before moving to the practitioner-directory GraphQL
SDL/resolver alignment block.
