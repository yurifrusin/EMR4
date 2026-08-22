# Provider-free default-off canonical check-in rollout runbook convergence closeout

Date: 2026-08-22

Timestamp: 2026-08-22T23:19:52.9249303+10:00 (Australia/Brisbane)

Status: `accepted`

Exact reviewed source: `149e377344fab671927682e428af7825e9a0e143`

## Outcome

The canonical default-off check-in rollout/kill-switch/rollback runbook now
exists as one byte-exact API-Spine manifest:

`docs/api-spine/manifests/canonical-check-in-rollout-kill-switch-rollback-runbook.json`

It is exactly 2,331 bytes with SHA-256
`dbd765ef3afe2ffe283a07befff44f745b21a8ec474c58d5a6d944fe3a9c8448`.
The pre-existing closed-form validator accepts the file without normalization
or semantic drift.

This closes the product-facing artifact half of the accepted rollout/runbook
gap. It does not execute a rollout. Ordinary practice and activation authority
remain false, active ordinary records remain zero, the kill switch remains
engaged, and an unknown commit still denies success and blind retry while
requiring source-truth readback.

## API Spine acceptance

The file is declarative policy input only. Existing check-in remains a
REST/OpenAPI proposal and confirmed command with server-owned actor, practice,
role, confirmation, idempotency, freshness/revalidation, append-only audit and
typed receipt enforcement. GraphQL remains read-only and async signals remain
non-authoritative.

No request/response field, operation ID, route, application/configuration
source, feature flag, allowlist or client changed. No P0-P2 API Spine finding
was introduced.

## Verification

- fresh five-source receipt: passed with all five named sources, complete
  DeepSeek/Gemini/native-subagent dispositions and zero caller-supplied Git
  identities;
- exact candidate bytes: 2,331/2,331 and SHA-256 exact;
- closed-form runbook validation: passed;
- focused runbook-manifest tests: 5 passed;
- integrated runbook, API-Spine, OpenAPI drift, latch and Baton packet: 98
  passed;
- full closeout packet including Compass and clockwork: 143 passed;
- Ruff, Python compilation and Git whitespace: passed;
- ordinary-practice/activation/effects: all default-off or false; and
- product runtime, providers, database/Docker and protected refs: unchanged.

Gemini remained declined because byte equality, the frozen digest and the
existing exact validator left no material architecture or authority fork.
DeepSeek remained declined because native-Harness allocation is closed and
Claude Code is historical only. Native subagents remained declined under
developer policy and serial candidate/Git custody.

## Workflow efficacy

This tranche closed one original readiness artifact gap without a provider,
worker, database, Docker, browser or product-runtime run. Candidate construction
and all tests passed on their first attempt.

There were three local control corrections. The first combined PowerShell Git/
latch reading contained a parser error and changed nothing; the corrected
read then passed. The first receipt used the descriptive event `pre_plan`,
which the registered vocabulary rejected; `pre_sprint_planning` then passed.
The first clockwork projection then rejected the `integration` graph kind
because it inherits two unrelated legacy product contracts; the declarative
artifact now uses the admitted `tooling` kind. All three failures were contained
before authoritative action. They still count as workflow cost and reinforce
the case for a typed authoring front end whose invalid values cannot be
expressed.

## Selected next tranche

The next operation is
`raisa-provider-free-default-off-canonical-check-in-non-phi-observability-manifest-convergence-rehearsal`.

The accepted admission-control architecture already freezes exactly five
low-cardinality non-PHI metric families and six critical non-actuating alerts.
The architecture contract is accepted, while the canonical API-Spine manifest
`docs/api-spine/manifests/canonical-check-in-non-phi-observability.json` is
absent and the successor operation is absent from the accepted graph.

The successor may materialize only that exact observability sub-contract as a
default-off declarative manifest with focused validation. It may not add
instrumentation, alert transport, automatic control action, identifiers,
product source, provider, database or runtime authority.

## Boundaries preserved

No ordinary practice is enabled. No feature flag, synthetic allowlist,
application/configuration/route/OpenAPI/GraphQL/client, generic-status
`Arrived`, action grammar, waiting-area movement, product/patient/appointment/
clinical/historical/protected data, native Harness, provider, database/Docker,
production runtime, deployment, release, Pages or protected ref changed.
`docs/branding/` and every unrelated untracked file remain preserved;
staging was explicit-path only.
