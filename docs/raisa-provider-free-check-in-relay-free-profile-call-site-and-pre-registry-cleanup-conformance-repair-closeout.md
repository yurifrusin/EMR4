# Check-in relay-free profile call-site and pre-registry cleanup repair closeout

Date: 2026-08-20

Timestamp: 2026-08-20T00:41:43.7639055+10:00 (Australia/Brisbane)

Status: **accepted mechanism with contained verification-scope violations**

## Outcome

The narrow harness repair passes. Both real relay-free container-creation call
sites now pass the captured network name to the accepted profile predicate. A
shared fail-closed helper owns the post-create/pre-registry interval: it can
remove only the exact captured, never-started container after re-inspection
proves its full ID, generated name, image, harness label, ownership nonce,
`created` state and `Running=false`, and it must then prove absence.

This accepts the repair mechanism. It does not accept the original
tranche-wide zero-database claim. Two orchestrator test-selection lapses
reached the shared PostgreSQL fixture boundary and are retained as AER-0658 and
AER-0659. Both runs are excluded from acceptance. The accepted verification is
the corrected 146-test provider-free matrix only.

## Exact sources and evidence

- Frozen plan: `373ee17d54bc7c553c844142a6c4ba0fbf8a421a`
- Runtime implementation: `95d456a1e3861ae463cf3643f347fa666c75fa48`
- Independently reviewed candidate: `8bda88069daeb314998341fc961b9aa061d496e5`
- Repaired harness SHA-256:
  `eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b`
- Historical attempt-003 harness SHA-256:
  `6965328b6dce6ecf939e86456bfcd99f1bdee7d32202e276f37454796e012b6b`
- Attempt-003 failure evidence SHA-256:
  `e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b`
- Attempt-003 envelope SHA-256:
  `91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75`
- Attempt-003 cleanup-recovery SHA-256:
  `048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71`
- Protected local/origin `master` and `handoff/current`:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

## Technical result

- `_create_server` and `_create_sidecar` each pass their captured
  `network_name` to `_container_profile_predicates`.
- One shared cleanup helper validates exact ownership and Created-state
  lifecycle before removing only the resolved full container ID.
- Post-removal absence is mandatory; uncertainty returns `False` and dominates
  the original failure coordinate.
- Known failures remain known after verified cleanup. Unknown controller
  failures receive server- or sidecar-specific closed cleaned coordinates.
- The admitted provider-free matrix passed 146 tests and rejected all 582
  hostile relay-free mutations. Ruff, compilation and diff checks passed.
- The admitted matrix invoked no Docker, database or provider boundary.
- Attempt 003 remains one occupied execution, zero automatic retries and no
  released ambiguous success. It was not retried or reclassified.

Gemini 3.7 Flash/high found no candidate defect. Its first review returned
`revision_required` because the orchestrator's provider-free manifest selected
a conftest-dependent database suite. The candidate remained unchanged and
clean. A corrected manifest substituted pure provider-free route-convergence
tests, was proved locally, and one fresh review then passed all ten commands at
the exact unchanged candidate.

## Efficiency and control reading

Clockwork rejected an unsupported checkpoint-intent filename before
publication, and the five-source pre-verifier gate rejected an invalid
Antigravity observation shape before dispatch. Those controls worked. The
manifest preflight did not detect the database fixture graph, and Sol then
repeated the same class of mistake while verifying the error register. That
remaining gap is not safely solved by another reminder.

The direct successor is therefore an engine-level admission repair. It will
make provider-free/no-database status a validated property of the command and
selected test graph, rejecting ordinary pytest and shared-PostgreSQL fixture
reachability before execution. Attempt 004 remains closed until that repair is
accepted and a new one-run plan is separately frozen.
## Boundaries retained

No product source, API Spine, OpenAPI, GraphQL, configuration, migration,
client, feature flag, allowlist, generic-status `Arrived`, action grammar,
waiting-area behavior or ordinary-practice admission changed. No product,
patient, appointment, clinical, historical or protected data was used. No
occupied DeepSeek work, production runtime, deployment, release, Pages or
protected-ref movement is authorised. `docs/branding/` and every unrelated
untracked file remain preserved.

## Next operation

Proceed under Yuri's standing authority to
`ariadne-provider-free-no-database-manifest-runner-admission-repair`. The
narrow objective is to reject non-provider-free pytest entry points and any
selected test whose fixture graph can acquire shared PostgreSQL before a
command is executable. This is a harness-control repair only; it opens no
attempt-004 execution or product authority.
