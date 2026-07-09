# Office Add-in GraphQL Mock Contract Boundary

This Sprint 276 scaffold is intentionally not the Office add-in runtime fetch
wrapper.

It lives under `tests/`, is written in Python, and consumes mocked response
dictionaries only. It does not import `app`, `taskpane.js`, FastAPI, Strawberry,
browser APIs, provider code, memory/RAG/GraphRAG code, H15/H-series fixtures,
historical diary material, audit writers, mutation paths, or subscriptions.

The scaffold defines the data-shape contract a future JavaScript taskpane
wrapper must satisfy:

- transport HTTP `401` is an auth/logout event;
- GraphQL `extensions.code` errors are response-body classifications and do not
  request logout;
- `practice = null` is an empty no-leak result;
- `defaultLocation = null` preserves the practitioner row;
- projection drift is discarded at the contract boundary;
- an explicitly disabled gate causes zero GraphQL fetch attempts.

It does not perform real fetch orchestration, render UI copy, manage feature
flags, compare REST and GraphQL live responses, log telemetry, or authorize
runtime traffic. A future runtime switch sprint must add taskpane-specific tests
and receive a separate consumer switch approval before editing
`EMR4 Sidebar/src/taskpane/taskpane.js`.
