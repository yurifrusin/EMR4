# CF-D2 restart and unknown-commit recovery descendant plan

Date: 2026-08-12

Status: `frozen_provider_free_recovery_runtime_closed`

Recovery planning baseline HEAD:
`2edfbf0c5990335947b40a370b676aad25aba023`

Last accepted durability result: Continuity 243 / Compass 225 (CF-D1)

Target result:
`raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_pass`

## Authority and purpose

Yuri explicitly selected the fresh narrow CF-D2 recovery descendant after the
bounded CF-D2 stop. This descendant preserves the original four-scenario
contract and does not reinterpret either failed attempt as database failure or
success.

Its immediate purpose is narrower: replace the adjacent, coordinate-ambiguous
terminal envelope with closed coordinate-specific evidence, then prove the
first R01 apply-and-anchor sequence without a crash. A new four-restart attempt
is ineligible until that no-crash sequence passes and the exact corrected HEAD
passes independent review.

## Immutable starting evidence

- Attempt 001 remains immutable at SHA-256
  `8e2519be3986a6dcb2721f83560a5c62bbb7ac6061f507a6479aab2f58c7b32e`.
  It stopped during fixture setup before a scenario or `SIGKILL`.
- Attempt 002 remains immutable at SHA-256
  `a7e88a267d597ba41d245df926a66ddb6bd98cf000afc46f269871b48604d6b6`.
  It passed all ten setup preconditions and stopped before its first scenario
  record, restart or `SIGKILL` with
  `scenario/unexpected_terminal_success`.
- Attempt 002 cannot distinguish the R01 position-one coordinator terminal
  check from the immediately following lifecycle-anchor terminal check. No
  diagnosis may infer which coordinate failed from source order alone.

The accepted inert SQL, role/RLS boundary, durability settings, complete
recovery classifier, four scenarios and claim boundary remain unchanged.

## Closed terminal-coordinate contract

Every participant call in setup and in the four scenarios receives exactly one
coordinate from a frozen vocabulary. A terminal mismatch records:

- the exact closed coordinate;
- one stable reason code;
- `zero` or `nonzero` return-code class;
- zero or one allowlisted SQLSTATE; and
- only allowlisted result tokens already admitted by CF-D2.

It never records raw SQL, query text, stdout, stderr, error text, PID, lock key,
server log, WAL, database URL, credential, environment value or authored-
synthetic coordinate value. A terminal validator cannot collapse two distinct
coordinates to the same failure stage.

## Phase A — deterministic instrumentation

Before Docker contact:

1. freeze the recovery machine contract, schemas, plan and threat delta;
2. make the terminal coordinate mandatory at every measured participant call;
3. reject unknown, duplicate, missing or overlong coordinates;
4. prove hostile mutations cannot smuggle raw output or an unallowlisted token
   into either diagnostic or later CF-D2 failure evidence;
5. preserve whole-document validation for both immutable historical attempts;
   and
6. pass focused tests, canonical fast-profile tests and `git diff --check`.

A deterministic failure forbids review and Docker contact.

## Phase B — no-crash first-sequence diagnostic

One newly owned networkless disposable `postgres:16-bookworm` container may:

1. install the exact accepted 424-statement inert SQL artifact;
2. verify the accepted catalogue, privileges, roles, RLS and exact durability
   settings;
3. perform the exact ten CF-D2 authored-synthetic setup preconditions once;
4. call only `cfd2_r01_apply_position_1` once;
5. if and only if that succeeds and the complete atomic delta is exact, call
   `cfd2_r01_append_anchor_2` once, where `_2` denotes the second anchor after
   the revision-zero baseline and the entry point receives lifecycle revision
   one, then verify the exact anchor-only delta; and
6. remove only the exact captured container ID and prove scoped absence.

This phase has zero `SIGKILL`, restart, blind retry, provider, product read,
product command and external-network operations. It writes one new immutable
whole-document diagnostic artifact. A failing earlier coordinate prevents all
later measured coordinates.

At most two diagnostic attempts exist:

- attempt 001 identifies or clears the original ambiguity;
- attempt 002 is eligible only after attempt 001 uniquely supports one bounded
  correction, that correction is documented, deterministic gates pass and a
  fresh exact-HEAD veto passes.

If attempt 001 already passes, attempt 002 is forbidden. If a failure is still
ambiguous, contradicts the frozen contract, requires accepted SQL or semantic
change, or attempt 002 does not pass, recovery stops without a new crash run.

## Bounded correction

Exactly one correction may follow a failing diagnostic. It must be fully
explained by the minimized coordinate evidence and be limited to terminal
expectation, participant-script framing, coordinate propagation, or harness
sequencing. It may not change the accepted inert SQL, role or RLS grants,
atomic membership, recovery classification, anchor authority, transaction
isolation, durability setting, scenario meaning or claim boundary.

The correction must pass a fresh exact-HEAD Gemini 3.6 Flash/high read-only
veto before diagnostic attempt 002. No correction may be selected by repeated
execution until an expected answer appears.

## Phase C — one new four-scenario attempt

Only a passing no-crash diagnostic plus fresh exact-repaired-HEAD review opens
one immutable CF-D2 runtime attempt 003. It retains the original plan's exact
four scenarios, four `SIGKILL` operations, same-container/same-cluster restart,
complete durable classification, independent anchor fencing, no participant
retry and exact cleanup.

There is no post-attempt-003 correction or rerun allowance in this descendant.
Any mismatch, partial state, ambiguous result, containment drift or cleanup
uncertainty stops CF-D2 without a pass.

## Review and execution order

1. Fresh five-source rehydration and passed pre-planning receipt.
2. Freeze and deterministically test this planning packet.
3. Commit by explicit path only; explicit-path staging only is permitted.
4. Obtain one fresh exact-HEAD Gemini 3.6 Flash/high planning veto.
5. Implement Phase A and Phase B; pass deterministic gates.
6. Obtain one fresh exact-HEAD implementation veto before Docker contact.
7. Run diagnostic attempt 001 once.
8. If required and eligible, document the exact diagnosis, apply the one
   bounded correction, re-test, re-review and run diagnostic attempt 002 once.
9. After a passing diagnostic, bind attempt 003 to a fresh exact reviewed HEAD,
   run it once, and accept only a complete four-scenario whole document.

Gemini receives an exact allowlisted read-only non-protected worktree and may
not edit, start Docker, inspect unrelated or protected evidence, or accept its
own work. Sol owns planning, implementation, serial runtime, recovery,
acceptance and task-branch publication. No native subagent or DeepSeek worker
is selected because the sequence is small, serial and stateful.

## Evidence and claim boundary

A passing diagnostic proves only that the exact R01 position-one apply and
lifecycle-revision-one second-anchor sequence matches the harness without
crash. It proves no restart or unknown-commit behavior.

Only a later passing attempt 003 can release the original CF-D2 four-scenario
claim. Even then it proves no literal WAL/protocol acknowledgement cut, power
loss, arbitrary crash point, driver/pool retry, repeated restart, availability,
performance, key rotation, retention/purge, operational migration, product
wiring, real data, provider, command, deployment, production or release.

## Closed surfaces

Protected holdouts, historical Diary/PHI, `docs/branding/`, unrelated untracked
files, real/product/patient/clinical data, operational database/source or
watcher access, providers, credentials, IAM, host network, published port,
bind/named/anonymous volume, server logs, WAL, executable product tools,
commands/writes, reusable runtime, deployment, production, release, Pages and
protected refs remain closed.

If CF-D2 passes, key rotation plus retention/purge remains a separate tranche
requiring fresh five-source rehydration and its own narrow fail-closed plan.
