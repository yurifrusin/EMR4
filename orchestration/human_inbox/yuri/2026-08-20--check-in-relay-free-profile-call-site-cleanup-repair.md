# Check-in relay-free profile call-site and cleanup repair

Date: 2026-08-20

Timestamp: 2026-08-20T00:41:43.7639055+10:00 (Australia/Brisbane)

## Plain-language summary

The actual cleanup repair works. Both container paths now check the right
captured network, and if anything fails after a container is created but before
the harness records it, the harness can remove only its own exact never-started
container and must prove it is gone.

The independent reviewer found no defect in that code. It did catch a workflow
mistake: the supposedly provider-free test list contained a database-backed
suite. I then made the same class of mistake twice locally. Those database
fixture contacts are recorded and excluded; I am not calling this a
zero-database tranche.

The next step is to put this rule into the machinery. Before another database
attempt, the runner will reject ordinary pytest and test selections that can
reach the shared PostgreSQL fixture. This turns “remember not to do that” into
a pre-execution interlock.

## Technical summary

- Reviewed candidate: `8bda88069daeb314998341fc961b9aa061d496e5`
- Runtime source: `95d456a1e3861ae463cf3643f347fa666c75fa48`
- Repaired harness SHA-256:
  `eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b`
- Admitted provider-free tests: 146/146 passed
- Hostile relay-free mutations: 582/582 rejected
- Gemini reviews: first control-only rejection, then one corrected pass
- Candidate findings: 0
- Out-of-scope shared-PostgreSQL fixture contacts: 2, excluded from acceptance
- Attempt-003 executions/retries: 1 / 0, unchanged
- DeepSeek: declined pending separate native-harness boot proof
- Native subagents: declined under current policy/no useful separable package
- Protected refs: all four remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

No product/API/config/client behavior, ordinary-practice admission, data,
production, deployment, release, Pages or protected ref has opened.

Clockwork closeout is accepted at Continuity 337 / Compass 319, generation
`gen-c11c8663948b6c7fc2c76feead419a62f2a6b4335c0780a63f86f83665ee83c1`,
lease 27. The non-PHI continuing Pushover notification succeeded with request
`57abe907-5ad2-48a2-8d5f-e0d70734d860`.
