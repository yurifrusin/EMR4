# Provider-free check-in relay-free recovery attempt 002 blocked closeout

Date: 2026-08-19

Timestamp: 2026-08-19T22:08:39+10:00 (Australia/Brisbane)

Status: `blocked`

Operation:
`raisa-provider-free-check-in-relay-free-recovery-attempt-002`

Plan source:
`85342f5e203c854090320481bef6a88e63ca565a`

Exact occupied execution source:
`675d1b929fb97d2a0264682d86be95c65b12fd3d`

Retained failure source:
`bd311671d2e803bfb491f37b99f355c6e0ffec24`

Post-execution readback source:
`eabd39771765a2847989fe825bdbdbc731cafa27`

## Result

The one authorised attempt-002 execution is consumed and failed closed before
PostgreSQL startup. It created and admitted the exact internal network, then
denied the created server profile on exactly two predicates:

- `captured_network_id`; and
- `secret_absent`.

The lifecycle-admission repair worked as intended: the captured Created-state
server was removed before the primary error propagated, the network was
removed, attachments/sidecars/server/network are absent, and the independently
read matching container and network counts are zero.

No database process started, no credential was delivered, no SQL or
transaction ran, no success was released and no retry occurred. Ordinary
admission release and product record counts are zero. The historical terminal
path bindings were restored.

## Immutable evidence

- failure artifact:
  `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/rehearsal-failure-evidence.json`,
  SHA-256 `7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff`;
- attempt envelope:
  `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/attempt-002-execution-envelope.json`,
  SHA-256 `6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40`;
- execution count: exactly one;
- automatic retry count: zero;
- ambiguous success release: false;
- cleanup: `cleanup_verified`; and
- terminal binding restored: true.

The closed attempt envelope validates against its Draft 2020-12 schema and
binds the full plan source, lifecycle repair source, exact execution source,
accepted harness digest and immutable attempt-001 evidence digests.

## Diagnosis

`secret_absent` is structurally inconsistent in the accepted harness's
created-container predicate: `forbidden_values` includes the ownership nonce,
while the same nonce is deliberately required in the captured container label
and therefore appears in the serialized Docker configuration being scanned.
That predicate cannot pass as written.

`captured_network_id` shows that Docker Engine 29.5.3 did not represent the
created-but-not-started attachment in the exact `EndpointSettings.NetworkID`
shape required by the repaired predicate. Because raw Docker inspection output
is deliberately not retained, this evidence establishes the mismatch but does
not claim which alternative field is safe. A future correction needs a
provider-free, no-credential created-state representation proof before any
further occupied database attempt.

## Acceptance gates

Before execution, the following passed:

- five-source Ariadne receipt with worker dispatch permitted;
- clockwork lease 14 with zero drift and an exact one-execution stage;
- accepted harness byte-exact SHA-256
  `5c60e6e4b0d554b3c323a932e8aa5a96943705e30a4d09afb2d6b8794a1503f4`;
- 366/366 hostile contract, 96/96 manifest, 96/96 OCI-state and 24/24
  classifier mutations rejected;
- 167 focused attempt, API Spine, A5.1, latch, Baton and clockwork checks;
- Ruff, compilation and diff checks;
- exact cached image
  `sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8`;
  and
- zero matching preexisting containers and networks.

After execution, 24 focused terminal-readback and harness tests passed and
zero matching Docker containers or networks were independently observed.

Gemini was not dispatched: its lane was correctly reserved for a successful
exact candidate, and no successful candidate exists. DeepSeek remained
declined pending its separately frozen native-Harness boot proof; Claude Code
was not used. Native subagents remained declined under developer policy and the
one-cleanup-owner constraint.

## Protected boundaries

No product, API, OpenAPI, GraphQL, route, feature flag, allowlist, client,
generic-status `Arrived`, grammar or waiting-area change occurred. No product,
patient, appointment, clinical or protected data, live provider, production,
deployment, release or Pages action occurred. Local/origin `master` and
`handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`; no protected ref moved.
`docs/branding/` and all unrelated untracked files remain preserved.

## User-attention boundary

This plan cannot be rerun. Any future occupied attempt requires Yuri to
authorise a separately frozen descendant after a no-credential created-state
Docker representation proof and correction of the contradictory nonce scan.
