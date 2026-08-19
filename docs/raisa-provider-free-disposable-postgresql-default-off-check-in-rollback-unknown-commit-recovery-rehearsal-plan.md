# Provider-free disposable PostgreSQL default-off check-in rollback and unknown-commit recovery rehearsal plan

Date: 2026-08-19

Timestamp: 2026-08-19T17:02:15.2064647+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `26402cb8667c2dbf62e86c6eb4c0b000d274559e`

Accepted runtime-role and tenant-isolation source:
`6a2832575e9b4df5c40a13984db7281e79814a94`

Target result:
`raisa_provider_free_disposable_postgresql_default_off_check_in_rollback_unknown_commit_recovery_rehearsal_pass`

Reasoning level: Extra High freezes the database atomicity, idempotency and
commit-uncertainty claim boundary. High is sufficient for the fixed
implementation, the one disposable execution, deterministic verification and
check-gated closeout while this plan remains unchanged.

## Objective

Close only the `atomic_effect_rollback_and_unknown_commit_recovery`
operational-evidence gap identified by the accepted check-in readiness review.
In one uniquely named, locally controlled, disposable PostgreSQL 16 instance,
use the accepted logical runtime-role posture and a new authored-synthetic,
admin-owned, forced-RLS probe to prove:

1. an explicit pre-commit transaction rollback leaves zero receipt, effect or
   audit rows;
2. a one-shot caller whose complete terminal response is lost after one commit
   releases no success and performs no automatic retry;
3. a fresh same-tenant restricted-role readback by the exact server-owned
   command and idempotency identity classifies only a complete, mutually
   consistent one-of-each packet as committed exactly once; and
4. partial, contradictory, duplicated or request-digest-mismatched packets
   fail closed.

This is an unmounted operational rehearsal. It creates no ordinary admission
record, command endpoint, product row, configuration, feature/allowlist change
or activation authority.

## Exact source boundary

The rehearsal decodes strict UTF-8, canonicalizes CRLF to LF, rejects bare CR
bytes and verifies SHA-256 before any Docker or PostgreSQL action.

| SHA-256 | Exact source |
|---|---|
| `857d4d6e54b8f5e20f0c59340585be095ffb8d2efece87e1a665275ceeb4095f` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal-plan.md` |
| `94ac2239a81f06e1404fa6c3fe7a02c9e9df2c0b4cea6b633347a987171a1712` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-contract.json` |
| `826749d9ffa9f6ae6bb00bfd82212d3d6b5ca579c1367de685d933b0c4a1afea` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-contract.schema.json` |
| `1d0e6bfa7224a1f8b57465b44bb6b1df14f997032e7537827b8acb373a777c8a` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/tenant-role-attestation.json` |
| `14c215a44037252a3346025149d8031a87b05094611e49c9f7c7337de92025e4` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-evidence.json` |
| `ee2d0d7b2560a627fdf82f429d061787db75b055de5d38a31ac7910d1c76f90c` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal-closeout.md` |
| `5346bd3c88b0db1ef63890af62ce303cde87b9482def68b724e10583a309240a` | `orchestration/agent_inbox/codex/raisa-check-in-runtime-role-tenant-isolation-attestation-sol-acceptance.md` |
| `e9aab3504520d955a0ce2c94c32a5f9a6ae25d7bbf129c7f2bd21951201c34d8` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/contract.json` |
| `786cab3b19231c391d281cf36568b4206fe5f11b2a2ac51469f0996c3e718e88` | `orchestration/continuity/raisa-provider-free-default-off-check-in-environment-manifest-secret-posture-architecture/environment-manifest.schema.json` |
| `505120968572362a7df8d67ab1d95947ed1cd467df0fbc520aca73a704755ba9` | `orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.json` |
| `d2ad88328ae235d5eb5b059087c7bf896b37d93f66f8ed379677c7a5ba1c1511` | `orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal/contract.json` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` | `orchestration/api_spine_programme.md` |
| `395cb2d8a56deadb839d3df7db6995f4863316aac146343360379c1207ea2041` | `scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_runtime_role_tenant_isolation_attestation_rehearsal.py` |
| `875afd5bdfcac9e8cdbc5deb000645c638b68d1eb2239d3cd55f130366c08bd9` | `scripts/raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal.py` |
| `2598a6258a1ca06efc1ee3de10daf074478307cc5dacd8236eaaf8f092116d10` | `docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-stop-closeout.md` |
| `2157ef208c0aa0ca29a237973faddaecfee3c0b35100f3b2ffecd136a33f58e3` | `docs/raisa-context-fabric-durability-restart-unknown-commit-recovery-descendant-stop-closeout.md` |

The two stopped CF-D2 closeouts are negative design evidence only. Their
restart, recovery-anchor, lifecycle and broad relation-packet machinery is not
imported. This narrower rehearsal makes no crash/restart claim.

## API Spine classification

The transaction manifest is a closed declarative fixture. It binds the exact
environment, practice reference, runtime logical role, physical role, command
identity, idempotency identity, complete request digest and expected relation
packet. Typed Python and PostgreSQL constraints/RLS enforce the run. The
manifest is not executable policy, command authority or admission authority.

The probe is command-shaped because it tests idempotency and audit atomicity,
but it adds no REST/OpenAPI route and edits no API Spine artifact. GraphQL
remains read-only; async events remain observation-only. No model or manifest
writes the database.

## Fixed containment profile

One execution must use the accepted runtime-role rehearsal's containment:

- cached exact image `postgres:16-bookworm` with pull policy `never`;
- one cryptographically suffixed internal Docker network and one labelled
  container, both controlled by captured IDs and ownership nonce;
- no published port, external network, bind mount, named/anonymous volume,
  host data, local `.env`, cloud/hosted/existing/product database or fallback;
- container-local tmpfs, 512 MiB memory, 1 CPU, 128 PIDs, restart policy `no`;
- one fixed in-process IPv4 loopback relay; and
- ephemeral admin and physical-role passwords held in process memory only.

No live secret is used or claimed. No provider or external network is used.

Cleanup may act only on captured IDs after exact label, nonce, image and name
reverification. Role absence is proved before relay/container/network teardown.

## Exact database boundary

The admin-owned `check_in_recovery_probe` schema contains exactly three
non-product relations:

1. `command_effect` — one opaque authored-synthetic effect per command;
2. `command_receipt` — one immutable command/idempotency/request-digest result;
3. `command_audit` — one minimized patient-free audit member.

Every relation is practice-scoped, has enabled and forced RLS using
transaction-local `app.current_practice_id`, and is owned by the admin. The
ephemeral login role is the same logical role
`appointment_check_in_ordinary_runtime_v1`, is non-owner and `NOBYPASSRLS`,
and receives only `CONNECT`, schema `USAGE`, and `SELECT`/`INSERT` on these
three probe relations. It receives no update/delete, product, public-schema,
migration, role-membership, ownership or default privilege.

Primary/unique/foreign-key and closed check constraints require one effect,
one receipt and one audit row for the exact command. Receipt and audit bind the
same practice, command, idempotency identity, request digest and effect.

## Fixed transaction fixture

The in-memory manifest uses only authored-synthetic opaque identifiers and
binds:

- environment class `test` and one fixed synthetic environment ID;
- accepted runtime-role source
  `6a2832575e9b4df5c40a13984db7281e79814a94`;
- one practice reference and transaction-local practice UUID;
- one rollback command identity and one disjoint ambiguous-response command
  identity;
- one idempotency identity and SHA-256 complete-request digest per command;
- expected packet cardinality `receipt=1`, `effect=1`, `audit=1`; and
- `ordinary_admission_release_count=0`, `automatic_retry_allowed=false` and
  `terminal_success_before_complete_response=false`.

Passwords, DSNs, Docker names, backend PIDs and raw output are never serialized.

## Explicit rollback scenario

Using the restricted role under one same-tenant transaction, insert the fixed
effect, receipt and audit members, prove the transaction-local staged counts,
then explicitly roll back. A fresh restricted-role readback must observe zero
members in all three relations and the canonical empty packet digest. Nothing
may be retried or converted into an ordinary withdrawal/activation operation.

This proves only pre-commit database rollback atomicity. The accepted ordinary
admission architecture's disable-only `withdraw` semantics remain separate and
unchanged.

## Ambiguous terminal-response scenario

One spawned one-shot caller uses the restricted role and a unique closed
application label. It inserts the exact effect, receipt and audit members in
one transaction, commits once, then enters a bounded post-commit
`pg_sleep` before emitting the harness-defined complete terminal response.

A separate admin observer must see the exact allowlisted `Timeout/PgSleep`
wait for that application label. The harness then terminates only that exact
backend with one exact `pg_terminate_backend` target. The caller may return only
`connection_lost_without_complete_terminal_response`; no stdout fragment,
exception text, cutpoint knowledge or timing is accepted as outcome evidence.
The wrapper releases no success, marks readback required and forbids retry.

This is a caller-level lost-complete-response proof. It is not a literal crash
inside PostgreSQL's WAL commit or wire-protocol acknowledgement instruction,
and it proves no container restart, driver/pool behavior or production
availability.

## Authoritative readback classifier

After connection loss, a fresh restricted-role connection sets the same
transaction-local practice and reads only by the exact command and idempotency
identity. A pure classifier receives only the closed readback packet and the
expected request digest. It receives no scenario identifier, cutpoint,
elapsed time, PID, logs, WAL, raw exception or expected branch.

`committed_exactly_once` is admissible only when:

- receipt, effect and audit counts are exactly one;
- every identity, digest, outcome and cross-reference matches;
- no other row exists for either command or idempotency identity; and
- canonical relation packet digests match the frozen shape.

All-zero is `rolled_back_zero_effect`. Any partial, duplicated,
cross-practice, mismatched or contradictory packet is `unresolved_denied`.
The classifier never mutates, retries, chooses a convenient branch or releases
ordinary admission.

## Fixed scenario matrix

1. `RUC-S01` — contract, source and full-Git bindings pass;
2. `RUC-S02` — closed transaction manifest binds the accepted logical/physical
   role and two disjoint command identities;
3. `RUC-S03` — role/catalogue and all three forced-RLS admin-owned relations
   match the frozen least-privilege profile;
4. `RUC-S04` — rollback transaction observes three staged members;
5. `RUC-S05` — explicit rollback leaves exact zero receipt/effect/audit state;
6. `RUC-S06` — one-shot ambiguous caller reaches exact post-commit hold;
7. `RUC-S07` — exact backend termination yields no complete terminal response,
   no success and no retry permission;
8. `RUC-S08` — fresh restricted-role authoritative readback observes one exact
   receipt/effect/audit packet;
9. `RUC-S09` — classifier returns `committed_exactly_once` without mutation;
10. `RUC-S10` — hostile partial, duplicate, digest and identity packets all
    return `unresolved_denied`;
11. `RUC-S11` — canonical ordinary records and ordinary releases remain zero;
12. `RUC-S12` — physical role, relay, captured container and captured network
    are absent in the required order.

## Evidence and redaction boundary

The run emits one closed transaction attestation and one parent evidence
artifact. They retain only source/digest bindings, closed scenario outcomes,
role and relation catalogue booleans/counts, closed terminal-response and
classifier enums, canonical row-set digests, containment facts, elapsed-time
bounds and cleanup disposition.

They may not retain a password, DSN, environment value, raw SQL, client output,
raw exception, server log, WAL, query text, backend PID, Docker/container/
network name, local path, product/patient/appointment/clinical value or secret
material hash. A recursive forbidden-field/value scanner and closed Draft
2020-12 schemas run before release.

Evidence label:
`authored_synthetic_provider_free_disposable_postgresql_check_in_rollback_unknown_terminal_response_recovery`.

## Exact owned outputs

Sol may create or update only:

- this plan and its threat-model delta;
- one closed rehearsal contract, contract schema, transaction-manifest schema,
  attestation schema and parent evidence schema under the named Continuity
  directory;
- one provider-free harness, focused provider-free/unit tests and one plan
  test;
- one successful attestation plus parent evidence, or one sanitized failure
  artifact;
- required Ariadne and exact-candidate review receipts; and
- closeout, Sol acceptance, Yuri summary and clockwork-owned closeout surfaces.

No `.env*`, `app/**`, migration, `docs/api-spine/**`, OpenAPI/GraphQL/async,
product test, client, deployment, provider or existing runtime source is
editable.

## Deterministic acceptance

Pass requires:

1. fresh five-source receipt and all three lane dispositions pass;
2. all 17 source hashes match before environment use;
3. all closed schemas and the canonical transaction manifest validate;
4. at least 256 hostile contract mutations, 96 hostile manifest/evidence
   mutations and 24 hostile classifier packets fail with zero escapes;
5. containment and cached-image admission pass without pull or published port;
6. the role and all three relations match every frozen ownership, grant, RLS,
   constraint and zero-product assertion;
7. explicit rollback stages all three members then leaves exact zero state;
8. the one-shot ambiguous caller commits once, reaches the exact post-commit
   hold, loses its connection and releases no complete terminal success;
9. no command reissue or automatic retry occurs;
10. fresh restricted-role readback sees exactly one mutually consistent packet
    and the pure classifier returns only `committed_exactly_once`;
11. hostile incomplete/duplicate/mismatched classifier inputs deny;
12. ordinary admission records/releases remain zero;
13. the role is absent before teardown and captured container/network IDs are
    absent after relay stop;
14. focused tests, accepted architecture/readiness/kernel/latch/Baton/API Spine
    tests, Ruff, compilation and `git diff --check` pass;
15. one fresh Gemini 3.7 Flash/high exact-candidate read-only veto passes with a
    clean unchanged worktree; and
16. one clockwork tick closes the tranche without bespoke updater, manual
    canonical derived-field edits or protected-ref movement while all unrelated
    untracked paths remain preserved.

The five historical mutable-current readiness/kernel assertions deselected by
the accepted runtime-role plan remain generation-stale for the same recorded
reason. No additional exclusion is authorised.

## Recovery addendum — result-channel consumption before worker join

Timestamp: 2026-08-19T17:33:20.6155269+10:00 (Australia/Brisbane)

The first and only original-plan disposable execution failed closed at
`ambiguous_response/worker_join_timeout` after the parent had observed the
exact post-commit `Timeout/PgSleep` state and terminated only that exact
backend. No complete terminal success was released and no retry occurred. The
physical role was absent before teardown; the relay stopped; the exact
container and network were absent. The sanitized immutable failure artifact is
SHA-256
`e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1`.

The cause is confined to the local Windows multiprocessing result channel: the
parent called `Process.join()` before consuming the child's one-item
`multiprocessing.Queue`. A child that has queued data may remain alive while
its feeder flush waits for the reader, so the ordering can manufacture the
observed join timeout after the database backend has already closed.

The narrow correction must consume the one closed result object with the
existing bounded timeout before joining the process. It must then join within
five seconds and require a zero child exit code. The result shape, database
transaction, exact PgSleep observation, exact backend target, no-retry rule,
readback classifier, evidence schemas, claim boundary and cleanup profile are
unchanged. A focused source-ordering regression test must pass before any
further environment action.

After fresh deterministic admission and a fresh five-source preexecution
receipt, exactly one recovery execution is authorised. It is an explicit
recovery attempt, not an automatic command retry: it creates a new disposable
container/network/role, retains the first failure artifact, and must again stop
without repetition on any mismatch. Closeout must report both execution
attempts and may accept only the recovery execution's complete evidence plus
both attempts' exact cleanup.

## Final recovery addendum — relay EOF propagation and immutable attempts

Timestamp: 2026-08-19T17:41:30.2168631+10:00 (Australia/Brisbane)

The addendum's one execution also failed closed. Moving queue consumption
before join changed the terminal coordinate from `worker_join_timeout` to
`worker_outcome_missing`, proving the queue was not the remaining block. The
exact `Timeout/PgSleep` observation and exact backend termination occurred;
no complete success or retry occurred; role, relay, container and network
cleanup again passed. Attempt 002 is SHA-256
`bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed`.

Read-only source diagnosis found the fixed inherited Docker-exec relay did not
propagate container-side EOF to its loopback client. Its downstream copier
returned after PostgreSQL closed, but its upstream copier remained blocked on
client input; the client simultaneously remained blocked waiting for EOF.
This exactly explains both sanitized terminal coordinates without changing
the committed database outcome.

The final narrow recovery must use a rehearsal-local relay subclass whose
downstream `finally` half-closes only the accepted loopback client's write side
with `shutdown(SHUT_WR)`. A provider-free socket/subprocess regression must
prove that child-process EOF becomes client EOF while the opposite direction
is still open. The shared predecessor relay is not edited. All database,
request, classifier, no-retry, containment and claim semantics remain frozen.

The second execution also exposed that the generic failure path overwrote the
first file. Both closed artifacts have now been restored as immutable numbered
attempts and their bytes match the originally observed full SHA-256 values:
attempt 001 `e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1`
and attempt 002
`bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed`.
The writer must select the first absent numbered path before updating the
latest-failure convenience file; it may never overwrite a numbered attempt.

After both regressions, the full deterministic suite and a new five-source
receipt pass, exactly one final recovery execution is authorised. It is not an
automatic command retry and must use a new role/container/network. Any further
failure ends bounded recovery and requires user attention; no fourth execution
may be inferred. Acceptance, if achieved, must retain and report both failure
attempts plus all three exact cleanup outcomes.

## Bounded recovery outcome and terminal clockwork addendum

Timestamp: 2026-08-19T17:54:16.7534074+10:00 (Australia/Brisbane)

The final authorised recovery execution reached the exact post-commit
`Timeout/PgSleep` observation after the rehearsal-local relay half-close
regression passed, but the caller again produced no closed worker outcome. It
failed closed at `ambiguous_response/worker_outcome_missing`, released no
success or automatic retry, removed the physical role before teardown and
left the relay, captured container and captured network absent. Immutable
attempt 003 is SHA-256
`15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219`.

All three authorised executions are therefore negative evidence and bounded
database recovery is exhausted. No fourth execution, Gemini veto or
acceptance clockwork tick is authorised.

Read-only inspection then found that the live single-owner clockwork admits
only `clean_closeout`: it always advances Continuity/Compass, marks a node
accepted and creates an `in_progress` successor latch. It cannot truthfully
publish a failed-closed `blocked` latch while preserving the accepted graph,
Compass, Baton, register and pattern report unchanged. A manual latch edit
would violate the accepted single-owner purpose.

Continuous harness self-correction therefore authorises only the missing
terminal gear:

- add a closed blocked-transition intent with no caller-authored Git,
  generation, lease, revision or digest binding;
- derive the blocked latch from the exact live in-progress latch, preserve its
  full 40-character source and protected boundaries, increment only the
  verification counter, require user attention and terminal permission, and
  clear the next executable stage;
- preserve Continuity, Compass JSON/Markdown, Current Baton, agent-error
  register and pattern report byte-for-byte;
- reuse the pointer-last lease, fault rollback, idempotency, full-Git
  predecessor and zero-drift validations of the one clockwork writer; and
- record `event_kind=blocked_transition` without an accepted node, successor
  operation or acceptance claim.

This addendum may update only the generic clockwork tick engine/CLI, its
focused tests, this tranche's closed blocked-transition intent and terminal
evidence/report in addition to the originally owned outputs. It authorises no
database execution, acceptance, successor selection or broader canonical
change.

## Parallelism assessment

- **DeepSeek:** declined. The active latch forbids occupied DeepSeek HMR, the
  native Harness still requires its separate provider-free
  stock-headless-to-custom-runner boot proof and Claude Code is not a fallback. The database
  lifecycle is serial and stateful.
- **Gemini:** reserved for one independent exact-candidate read-only veto after
  deterministic rollback, ambiguous-response, redaction and cleanup admission.
- **Native subagents:** declined under current developer policy and because the
  single mutable disposable PostgreSQL lifecycle is indivisible.

## Stop, claim and successor

No runtime retry is implicit. The result-channel and final relay-EOF recovery
executions are limited by the addenda above. A source, schema, role, RLS, cutpoint, caller,
readback, classifier, evidence-redaction or cleanup mismatch produces only the
sanitized failure artifact and no pass. A residual owned role/container/network
is cleanup recovery, never acceptance evidence.

Passing proves only this fixed authored-synthetic pre-commit rollback and
caller-level lost-complete-response/readback path. It does not prove live
secret custody/rotation, ordinary operational evidence, a product command,
literal in-COMMIT crash, container/database restart, WAL/power-loss durability,
driver/pool retry, concurrency/load/performance, operator response, deployment
or production.

The environment-secret/rotation operational-evidence gap remains separate.
This rehearsal must not infer its successor beyond a clockwork-selected,
dependency-satisfied fail-closed boundary.

No ordinary-practice enablement, feature/allowlist change, product/config/API
change, route mount, generic-status `Arrived`, grammar/client change, waiting-
area movement, product/patient/appointment/clinical/protected data, occupied
DeepSeek HMR, production runtime, deployment, release, Pages or protected-ref
movement is authorized. Preserve `docs/branding/`; stage explicit paths only.
