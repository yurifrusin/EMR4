# PR 71 CodeQL alert 545 triage

Date: 2026-08-01

Repair head: `d005a1521bd2af7d3ca7a773477567afa3809b71`

Pull request: `yurifrusin/EMR4#71`

## Alert 545 - missing superclass initializer

Verdict: `confirmed_quality`, CodeQL error without a security-severity level.

The PostgreSQL Office compatibility harness inherited from the concrete
in-memory harness but intentionally did not call its initializer. Calling that
initializer would have constructed the wrong in-memory runtime, audit sinks and
unrelated task credentials before replacing them with PostgreSQL dependencies.
The omission was therefore deliberate, but the inheritance shape was unsafe:
future runtime-independent lifecycle fields added to the parent could have been
missing from the PostgreSQL child.

The repair extracts the common Office launch/result lifecycle into
`OfficeCookieCompatibilityHarnessBase`. Both the in-memory and PostgreSQL
concrete harnesses now call `super().__init__()`, then construct only their own
runtime-specific store, transport and denial-audit dependencies. Regression
coverage proves that the PostgreSQL instance has no in-memory store or audit
sink attributes.

## Disposition and proof

No suppression, dismissal or manual native-state mutation was used. Seventeen
focused parent/descendant tests, the exact 176-test shared-auth/Office/API Spine/
security-governance regression, 29 Continuity/Compass/handover tests,
compilation, Ruff, canonical lint and reviewed Bandit pass locally.

Fresh CodeQL run `30698479139` passed both language analyses and the Advanced
Security wrapper at repair head `d005a152`. The PR has zero open CodeQL alerts;
native alert 545 reports `fixed` at `2026-08-01T11:53:22Z` with no dismissal.
Python security and Node/Office manifest security also pass.

The change adds no route, OpenAPI or GraphQL operation, migration, identity,
product/document/patient/clinical read, command, provider, cloud/IAM mutation,
deployment, production, release or protected-ref movement.
