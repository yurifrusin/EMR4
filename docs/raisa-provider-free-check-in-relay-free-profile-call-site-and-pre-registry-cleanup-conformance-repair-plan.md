# Provider-free check-in relay-free profile call-site and pre-registry cleanup conformance repair plan

Date: 2026-08-19

Timestamp: 2026-08-19T23:56:00+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`78e0202343b4a925a0674e58486d8616df7f7599`

Attempt-003 occupied execution source:
`19e4414fec067fcbb6af12818e432953432878be`

Attempt-003 retained evidence source:
`d2c6f7e465b1bcf2f8cf458a8fbd5721631db422`

Accepted Created-state correction source:
`02a1fbfaa517a0d2a2dff66f31fabe482653c430`

Accepted Created-state reviewed candidate:
`260eeda97a3204a39b0f639d216fd7a53c0d2014`

Operation:
`raisa-provider-free-check-in-relay-free-profile-call-site-and-pre-registry-cleanup-conformance-repair`

Target result:
`raisa_provider_free_check_in_relay_free_profile_call_site_and_pre_registry_cleanup_conformance_repair_pass`

Reasoning level: Extra High freezes the causal interpretation, immutable
failed-attempt boundary and exact cleanup invariant. High is sufficient for
the two keyword corrections, shared cleanup helper, deterministic fault
injection, independent veto and clockwork closeout.

## Objective

Repair only the deterministic harness defects exposed by consumed attempt 003:

1. `_create_server` passes its captured `network_name` to
   `_container_profile_predicates`;
2. `_create_sidecar` passes its captured `network_name` to the same predicate;
3. either function exactly removes its own never-started created container if
   any exception occurs after successful `docker create` but before the
   container is returned for registry admission; and
4. real-call invocation and fault-injection tests prove those controls without
   invoking Docker or a database.

This tranche does not reopen or retry attempt 003 and may not create a Docker
object, credential, process, role, relation, SQL statement or database
transaction.

## Immutable causal floor

| SHA-256 | Exact source |
|---|---|
| `e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/rehearsal-failure-evidence.json` |
| `91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/attempt-003-execution-envelope.json` |
| `048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/attempt-003-cleanup-recovery.json` |
| `9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b` | `orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/created-state-representation-evidence.json` |
| `49c5a3673d388fc84b2f046a993a8f4c747f9887252ef4cdd2dfcc59e9a11410` | `orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/repair-attestation.json` |

The pre-repair relay-free harness is exact SHA-256
`6965328b6dce6ecf939e86456bfcd99f1bdee7d32202e276f37454796e012b6b`.
Attempts 001 through 003, their execution counts, terminal artifacts and
cleanup evidence remain immutable. All Git bindings are full 40-character
object IDs; abbreviated or caller-completed IDs are inadmissible.

## Exact implementation boundary

Only
`scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py`
may receive runtime-source changes, limited to:

- remove the obsolete `del network_name` statements from `_create_server` and
  `_create_sidecar`;
- pass `network_name=network_name` at both real predicate calls;
- add one shared pre-registry cleanup helper that accepts only the already
  generated exact container name, candidate ID and ownership nonce;
- re-inspect by candidate ID when it is a full ID, otherwise by the exact
  generated name; require one row, full resolved ID shape, exact candidate-ID
  relation when available, exact name/image/harness-label/nonce ownership,
  `created` state and `Running=false` before removal;
- remove only the resolved full ID, then require exact absence; and
- on any post-create/pre-registry exception, preserve a known primary
  `RehearsalFailure` after cleanup, convert an unknown controller exception to
  a closed `*_pre_registry_controller_failure_cleaned` coordinate, and replace
  either with `*_pre_registry_cleanup_unverified` if exact cleanup cannot be
  proven.

No accepted profile predicate, Docker command profile, credential path,
transaction program, fixture identity, request digest, role/RLS rule, outcome
classifier, evidence schema or terminal path may change.

## Deterministic acceptance matrix

1. `PCR-S01` — all full Git and SHA-256 causal bindings pass;
2. `PCR-S02` — AST/source inspection finds exactly two real profile-predicate
   creation call sites and both supply the captured `network_name`;
3. `PCR-S03` — a mocked real `_create_server` call reaches the predicate with
   the exact generated name, captured network name/ID, nonce and server kind;
4. `PCR-S04` — a mocked real `_create_sidecar` call reaches the predicate with
   the same exact bindings and the allowlisted action kind;
5. `PCR-S05` — injected unknown server predicate failure removes one exact
   owned Created-state container and returns the closed cleaned coordinate;
6. `PCR-S06` — injected unknown sidecar predicate failure does the same;
7. `PCR-S07` — wrong name, image, label, nonce, state, running flag, candidate
   relation, multiplicity or removal readback denies cleanup success;
8. `PCR-S08` — no test or source path invokes real Docker, starts a process,
   delivers credentials or reaches PostgreSQL;
9. `PCR-S09` — the accepted Created-state predicate suite and all 582 relay-free
   hostile gates continue to pass;
10. `PCR-S10` — attempt-003 failure, envelope, cleanup recovery, source and
    execution/retry counts remain byte-exact;
11. `PCR-S11` — focused API Spine, A5.1, latch, Baton, clockwork, Ruff,
    compilation and diff gates pass; and
12. `PCR-S12` — one fresh Gemini 3.7 Flash/high exact-candidate read-only veto,
    clockwork closeout, paired Yuri summary and non-PHI notification pass.

Every exact verifier assertion is executed locally before Gemini dispatch.
Clockwork check and publish remain separate commands. Failure closes this
repair without admitting attempt 004.

## Explicit parallelism assessment

- **DeepSeek:** declined. Its native Harness still requires the separately
  frozen boot proof, Claude Code is no fallback, and the tiny causal change is
  inseparable from Sol's failure acceptance.
- **Gemini:** reserved for one fresh post-deterministic exact-candidate
  read-only veto because this repair changes a containment lifecycle.
- **Native subagents:** declined under current developer policy and because no
  separable work package has positive leverage.

No worker receives implementation, cleanup, acceptance, Git or protected-ref
authority. Reassess at pre-verifier and closeout.

## Protected and continuation boundaries

No Docker or database execution, product source, API Spine/OpenAPI/GraphQL,
configuration, migration, client, feature flag, allowlist, generic-status
`Arrived`, grammar, waiting-area, ordinary-practice admission, product,
patient, appointment, clinical or protected data, production, deployment,
release, Pages or protected-ref movement is authorised.

At closeout Sol writes the paired lay/technical Yuri summary, sends the usual
non-PHI Pushover notification and uses clockwork as the only canonical
governance writer. All staging uses explicit paths only; `git add .` and
`git add -A` are forbidden. Preserve `docs/branding/` and all unrelated
untracked files.

After acceptance, proceed under Yuri's standing authority to freeze a
separately named attempt 004. Pause only for a truly extraordinary, genuinely
non-inferable or safety-critical fork.
