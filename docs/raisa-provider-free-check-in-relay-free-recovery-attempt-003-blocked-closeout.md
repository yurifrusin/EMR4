# Provider-free check-in relay-free recovery attempt 003 blocked closeout

Date: 2026-08-19

Timestamp: 2026-08-19T23:41:16.9577916+10:00 (Australia/Brisbane)

Status: `blocked`

Operation:
`raisa-provider-free-check-in-relay-free-recovery-attempt-003`

Plan source:
`159615440812bf57a5f91d021a0469f84c60dad3`

Exact occupied execution source:
`19e4414fec067fcbb6af12818e432953432878be`

Retained evidence and cleanup source:
`d2c6f7e465b1bcf2f8cf458a8fbd5721631db422`

## Result

The one authorised attempt-003 execution is consumed and failed closed before
PostgreSQL startup. The corrected harness created one exact internal network
and one exact server container. The controller then raised a Python invocation
error while checking the never-started server profile because the corrected
predicate requires `network_name`, but both real container-creation call sites
still omitted that keyword.

The wrapper converted the unexpected exception into a sanitized terminal
failure and released no success or retry. No credential was delivered, the
container remained `created` with `Running=false`, no PostgreSQL process
started, no SQL or transaction ran, and ordinary admission release and product
record counts are zero.

The base controller could not clean an object that had not yet entered its
registry. Sol therefore performed the already-authorised recovery by requiring
one and only one matching labelled candidate, reinspecting its full ID shape,
server-name prefix, exact image, harness label, nonce shape and Created-state
status, then removing that exact captured container. Independent readback now
observes container absence, network absence and zero matching owned resources.
This cleanup is not a proof rerun.

## Immutable evidence

- failure artifact SHA-256:
  `e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b`;
- execution envelope SHA-256:
  `91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75`;
- cleanup recovery SHA-256:
  `048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71`;
- occupied execution count: exactly one;
- automatic retry count: zero;
- ambiguous success release: false;
- terminal binding restored: true; and
- post-recovery matching owned resources: zero.

The attempt-003 envelope validates against its closed Draft 2020-12 schema and
binds the full plan source, exact execution source, Created-state correction
and reviewed candidate, corrected harness digest and immutable attempts 001
and 002. The separate closed cleanup-recovery schema binds the terminal hashes
and retains no Docker ID, name, nonce, credential, raw inspect object or log.

## Diagnosis and prevention boundary

This was not a Docker timing failure and would not benefit from retry. The
defect is deterministic: `_container_profile_predicates` gained the required
`network_name` keyword while `_create_server` and `_run_sidecar` did not pass
it. Direct predicate tests covered the corrected semantics but no deterministic
test invoked both real profile-check call sites with a spy predicate signature.

The narrow successor must:

1. pass the captured network name at both real call sites;
2. add deterministic invocation-contract tests for server and sidecar creation
   that fail on any future required-keyword drift;
3. prove pre-registry exceptions cannot strand a captured Created object;
4. preserve the current corrected harness semantics and all terminal evidence;
   and
5. authorise no database execution.

Only after that repair is accepted may a separately frozen attempt 004 admit
one new occupied execution. Attempt 003 may never be rerun.

## Workflow efficacy reading

The clockwork kept the attempt identity, exact source, one-run limit and
protected boundaries synchronized and made the execution non-repeatable. It
also caught an incorrect caller-authored full-hash transcription before
publication. The remaining weakness is below the governance layer: static
semantic tests did not exercise real call-site compatibility. One redundant
deterministic test suite was also started after the first yielded session was
not visible; both suites passed and neither touched Docker.

The direct improvement is concrete rather than procedural: add executable
call-site contract tests and pre-registry cleanup ownership, then let the same
clockwork take the reading. No new manual checklist is required.

## Parallelism and review

- DeepSeek remained declined pending its native-Harness boot proof; Claude
  Code was not used as fallback.
- Gemini was not dispatched because no successful exact candidate exists.
- Native subagents remained declined under developer policy and the one-owner
  cleanup constraint.

## Protected boundaries

No product, API, OpenAPI, GraphQL, route, feature flag, allowlist, client,
generic-status `Arrived`, grammar or waiting-area change occurred. No product,
patient, appointment, clinical or protected data, live provider, production,
deployment, release or Pages action occurred. Local/origin `master` and
`handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`; no protected ref moved.
`docs/branding/` and every unrelated untracked file remain preserved.

## Next operation

Under Yuri's standing uninterrupted-development authority, proceed to the
narrow provider-free call-site and pre-registry cleanup conformance repair.
After its accepted closeout, freeze attempt 004 separately. Pause only for a
truly extraordinary, genuinely non-inferable or safety-critical fork.

The clockwork published the blocked transition at lease sequence 23 with zero
canonical drift. The usual non-PHI continuing Pushover notification succeeded
with request `d7d99f92-0897-4520-91bd-42332a00523e`.
