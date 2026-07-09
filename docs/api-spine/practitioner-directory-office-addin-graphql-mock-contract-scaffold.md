# Practitioner Directory Office Add-in GraphQL Mock Contract Scaffold

Sprint 276 adds a tests-only Python contract scaffold for the future Office
add-in taskpane GraphQL practitioner fetch wrapper.

It is not runtime code. It does not edit `taskpane.js`, call `/api/v1/graphql`,
import `app`, render UI copy, manage a feature flag, run a shadow fetch, compare
live REST/GraphQL data, write telemetry, or claim readiness.

The scaffold proves the future wrapper contract over mocked response
dictionaries:

- HTTP `401` is a transport auth event and requests logout.
- GraphQL `FORBIDDEN` and `BAD_USER_INPUT` are response-body classifications
  and do not request logout.
- `practice = null` returns an empty no-leak result.
- `defaultLocation = null` preserves the practitioner row.
- extra fields are discarded at the contract boundary.
- an explicitly disabled gate causes zero GraphQL fetch attempts.
- future REST fallback is represented only as an event classification.

The companion `DRIFT.md` records why this Python scaffold must not become the
JavaScript taskpane implementation. A future runtime switch still needs a
separate consumer switch approval.
