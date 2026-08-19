# Provider-free disposable PostgreSQL default-off check-in relay-free rollback and unknown-commit recovery rehearsal plan

Date: 2026-08-19

Timestamp: 2026-08-19T20:13:10.6208443+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `b5afa75bfc759efa689d35cd06c5b330e4b7ed05`

Accepted relay-free transport source:
`4f0f54c2b0861828f9994444201b8da1bd54be00`

Accepted runtime-role and tenant-isolation source:
`6a2832575e9b4df5c40a13984db7281e79814a94`

Target result:
`raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal_pass`

Reasoning level: Extra High freezes the transaction, credential, OCI-result,
tenant-isolation and ambiguity-recovery boundaries. High is sufficient for the
fixed implementation, one disposable execution, independent exact-candidate
review and check-gated clockwork closeout while this plan remains unchanged.

## Objective

Close only the `atomic_effect_rollback_and_unknown_commit_recovery` evidence
gap for canonical check-in. In one newly named, locally controlled, disposable
PostgreSQL 16 environment, prove that:

1. one authored-synthetic transaction stages an effect, receipt and audit
   member and an explicit rollback leaves all three absent;
2. a disjoint one-shot transaction commits the same three-member shape, then
   loses its complete terminal response at the accepted post-commit hold;
3. the ambiguous caller releases no success, performs no retry and is admitted
   only from its exact terminal OCI state plus prior exact backend observation;
4. a fresh same-practice restricted-role readback finds one mutually
   consistent packet and no duplicate effect; and
5. partial, contradictory, cross-practice, duplicate or digest-mismatched
   readback shapes deny.

This is an unmounted authored-synthetic rehearsal. It creates no ordinary
admission, route, product record, runtime configuration or activation
authority. It authorises no ordinary-practice enablement.

## Controlling reduction

The three immutable predecessor failures proved that the database cutpoint was
reached but the host relay and multiprocessing result channel were not
traceable enough to close the caller outcome. They are negative transport
evidence only. This descendant imports the predecessor's transaction fixture
and fail-closed classifier semantics, but imports none of its relay subclass,
listener, socket-copy threads, spawned process, queue, join ordering or result
bytes.

The accepted relay-free transport supplies the replacement boundary. The
database server and every client remain inside one captured internal Docker
network. Each client is a uniquely labelled short-lived container whose
primary child is `psql`. Its credential is supplied over attached stdin only
after exact inspection. The host discards attachment output and derives the
closed result only from exact terminal OCI state.

## Exact immutable inputs

All bound text is decoded as strict UTF-8, CRLF is canonicalized to LF, bare CR
is rejected and SHA-256 is verified before Docker or PostgreSQL use.

| SHA-256 | Exact source |
|---|---|
| `3b88e96110a33437895a993dfca7e44164e7a342c420c53cc7f366851f424f1b` | `docs/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign-plan.md` |
| `60f93e73f2e452e62a2cbda436a7738ad53d3c61e0b795c8ec05943823609275` | `docs/security/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign-threat-model-delta.md` |
| `bff78c40b52330e63bcc0775ca7d7c6939c1281d113ac96ca2b4b4a0fc8d9fbe` | `docs/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign.md` |
| `f384dcacf517f24e5f694f9175e225458d850a5f5464303e87cca741792ec5ce` | `orchestration/continuity/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign/contract.json` |
| `735492680f04f8b9de1d1b2397e18c3287d8977125f635412944fc3734708f4e` | `orchestration/continuity/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign/contract.schema.json` |
| `0b5a5a0c6e9d95e87907d6f4f0db264640dd1be35eb4c82a4b55841d0e92ebd0` | `orchestration/continuity/raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign/transport-evidence.json` |
| `eb03366764483a84e9139f85f0a47b0c124cbb36cb085157507a0c92b7983059` | `scripts/raisa_provider_free_default_off_check_in_relay_free_unknown_response_transport_redesign.py` |
| `857d4d6e54b8f5e20f0c59340585be095ffb8d2efece87e1a665275ceeb4095f` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal-plan.md` |
| `94ac2239a81f06e1404fa6c3fe7a02c9e9df2c0b4cea6b633347a987171a1712` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-contract.json` |
| `826749d9ffa9f6ae6bb00bfd82212d3d6b5ca579c1367de685d933b0c4a1afea` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-contract.schema.json` |
| `1d0e6bfa7224a1f8b57465b44bb6b1df14f997032e7537827b8acb373a777c8a` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/tenant-role-attestation.json` |
| `14c215a44037252a3346025149d8031a87b05094611e49c9f7c7337de92025e4` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-evidence.json` |
| `395cb2d8a56deadb839d3df7db6995f4863316aac146343360379c1207ea2041` | `scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_runtime_role_tenant_isolation_attestation_rehearsal.py` |
| `0f66b6cb067479c57d419d8aa6bf92e99251946e828f454f24a2bc9e490baa8e` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal-plan.md` |
| `85bf13e548ffd5f4497c29b96b16120488bdc8bf4bb78861aa2f229850a9c182` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal-blocked-closeout.md` |
| `34489e42e16defcaf47132ff04f16204dd528b7d7d454d245f281c318b432e57` | `orchestration/agent_inbox/codex/raisa-check-in-rollback-unknown-commit-recovery-sol-blocked-assessment.md` |
| `e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-001.json` |
| `bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-002.json` |
| `15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-003.json` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` | `orchestration/api_spine_programme.md` |

The former contract and harness are not executable inputs. Their immutable
failure artifacts remain preserved, and this tranche writes to a distinct
Continuity directory.

## API Spine classification

The transaction manifest is a closed declarative fixture. It binds one
authored-synthetic environment and practice, the accepted logical runtime
role, a per-run physical role, two disjoint commands, idempotency identities,
complete-request SHA-256 digests and the expected atomic receipt/effect/audit
packet. Neither the manifest nor a model may dispatch Docker or mutate the
database.

No REST/OpenAPI, GraphQL, async contract, YAML command manifest, product schema
or client changes. GraphQL remains read-only. The future product command must
still preserve explicit practice scope, idempotency, audit atomicity, default
denial and authoritative readback.

## Fixed containment and transport

The one execution has exactly one captured internal network and one captured
PostgreSQL server container, plus short-lived captured action sidecars. Every
Docker object has a cryptographic ownership nonce, exact name prefix and
harness label and is acted on only by captured ID after identity reinspection.

- image: exact cached `postgres:16-bookworm` image admitted by ID, pull policy
  `never`, with no build;
- server: no published port, external network, bind mount, named/anonymous
  volume, host data, `.env`, Docker log, restart or fallback; database storage
  is one container-local tmpfs;
- clients: same exact cached image, read-only root filesystem, one bounded
  tmpfs, logging driver `none`, `no-new-privileges`, all capabilities dropped,
  bounded memory/CPU/PIDs and restart policy `no`;
- transport: direct container DNS/TCP only on the captured internal network;
  no host TCP listener, port forwarding, socket-copy relay, Docker-exec byte
  bridge, multiprocessing process or queue; and
- output: all attachment stdout/stderr is discarded and is never evidence.

The server bootstrap password and each sidecar credential are random 32-byte
values held only in controller process memory. Each container is created with
stdin open, then inspected to prove the credential is absent from environment,
arguments, labels, mounts and Docker configuration. Only then may one bounded
credential line be delivered through an exact captured-ID attachment. The
credential may be exported only to the container's primary `postgres` or
`psql` child and must not enter a host/container file, log, artifact, hash or
retained Docker object.

The host attachment is input plumbing only. Its process status, bytes and
return code cannot prove an action or outcome. Each action is admitted only
from exact captured-container stopped state with the expected exit code,
`OOMKilled=false`, empty Docker state error and restart count zero. Attachments
must be absent before object cleanup.

## Fixed database boundary

The admin-owned `check_in_relay_free_recovery_probe` schema contains exactly
three non-product relations: `command_effect`, `command_receipt` and
`command_audit`. Each is practice-scoped, has enabled and forced RLS using
transaction-local `app.current_practice_id`, and has exact primary, unique,
foreign-key and closed-value constraints that bind the same command,
idempotency identity, request digest and effect.

The ephemeral login role represents
`appointment_check_in_ordinary_runtime_v1`, is non-owner and `NOBYPASSRLS`,
has no memberships or ownership, and receives only `CONNECT`, schema `USAGE`
and `SELECT`/`INSERT` on the three probe relations. It receives no product,
public-schema, update/delete, migration, role or default privilege.

The authored-synthetic fixture uses one practice UUID and two disjoint command,
effect, audit, idempotency and digest identities. All identifiers are frozen in
the contract before execution. Ordinary admission release count and canonical
product record count remain zero.

## Purpose-specific sidecars

The harness may create only these closed action classes, each with one primary
`psql` child and exact terminal-state admission:

1. readiness/setup and final role-removal sidecars using the ephemeral admin
   credential;
2. one restricted rollback sidecar and one fresh restricted zero-state
   readback sidecar;
3. one restricted ambiguous caller sidecar;
4. one admin observer/terminator sidecar whose fixed SQL waits boundedly for
   exactly one matching restricted backend in `Timeout/PgSleep` and terminates
   only that backend; and
5. one fresh restricted authoritative readback sidecar.

No sidecar accepts runtime-chosen SQL, command identity or policy. Its SQL and
wrapper are typed constants in the harness and their digests are contract
bound. Synthetic identifiers may be passed as closed arguments; credentials
may not.

## Explicit rollback scenario

The restricted rollback sidecar sets the fixed practice locally, begins one
transaction, inserts all three packet members, proves all three are visible
inside that transaction and explicitly rolls back. Its complete terminal state
must be clean. A fresh restricted sidecar then checks by both exact command and
idempotency identity that all three counts are zero. Any nonzero, partial,
cross-practice or unreadable result denies the tranche.

## Ambiguous terminal-response scenario

The restricted caller begins once, sets the same practice, inserts the disjoint
three-member packet, commits once and enters the fixed post-commit `pg_sleep`
before the wrapper's complete-response marker. The observer/terminator sidecar
must see exactly one backend with the frozen application identity, restricted
role, database and `Timeout/PgSleep` state, then terminate only that backend.

The caller may be classified
`connection_lost_without_complete_terminal_response` only when that prior
observation/termination proof passed and its exact OCI state is stopped with
exit `42`, no OOM, error or restart. Exit zero, the wrapper's denial exit,
missing/running/unreadable/mismatched state or absent observer proof is
`unresolved_denied`. No success is released and no command is reissued.

This is a caller-level lost-response proof after a committed transaction. It
does not claim a crash inside PostgreSQL commit/WAL acknowledgement, container
restart behavior, driver/pool behavior, network-partition recovery or
production availability.

## Authoritative readback

After ambiguity classification, one newly created restricted-role sidecar sets
the same practice and performs read-only queries by the exact command and
idempotency identity. Its fixed predicate succeeds only for one receipt, one
effect and one audit member with matching practice, identities, request digest,
outcome/action and cross-references, and with no competing command or
idempotency row. The sidecar emits no packet bytes; exact clean OCI completion
is the closed authoritative-readback result.

The harness retains a pure equivalent packet classifier for deterministic
hostile-shape testing. It receives only a closed packet plus expected request
digest. All-zero is `rolled_back_zero_effect`; one exact mutually consistent
packet is `committed_exactly_once`; every other shape is
`unresolved_denied`. It cannot mutate, retry or release ordinary admission.

## Fixed scenario matrix

1. `RFR-S01` — full Git and exact source/hash bindings pass;
2. `RFR-S02` — contract, schemas and frozen transaction manifest pass;
3. `RFR-S03` — exact image, internal network and no-host-transport profile pass;
4. `RFR-S04` — restricted non-owner role and all forced-RLS relations match;
5. `RFR-S05` — explicit rollback stages three members then reads back zero;
6. `RFR-S06` — ambiguous caller commits once and reaches exact post-commit hold;
7. `RFR-S07` — exact observer terminates exactly one matching backend;
8. `RFR-S08` — caller OCI exit `42` releases no success and permits no retry;
9. `RFR-S09` — fresh restricted readback proves one exact packet;
10. `RFR-S10` — hostile partial, duplicate, identity and digest packets deny;
11. `RFR-S11` — other-practice visibility and ordinary/product effects are zero;
12. `RFR-S12` — role, attachments, sidecars, server and network are exactly absent.

## Evidence and redaction boundary

The run emits one closed transaction attestation and one parent evidence
artifact. They may retain exact source/digest bindings, closed scenario enums,
catalogue booleans/counts, closed OCI predicates, canonical non-secret packet
digests, retry count zero, ordinary/product count zero, elapsed-time bounds and
cleanup disposition.

They may not retain a credential or its hash, DSN, environment value, raw SQL,
argv, attachment bytes/status, stdout/stderr, raw exception, server/Docker log,
WAL, query text, backend PID, Docker object ID/name/nonce, local path, or any
product, patient, appointment, clinical, historical or protected value.
Recursive forbidden-key/value scanning and closed Draft 2020-12 schemas run
before release.

Evidence label:
`authored_synthetic_provider_free_disposable_postgresql_check_in_relay_free_rollback_unknown_terminal_response_recovery`.

## Exact owned outputs

Sol may create or update only:

- this plan and its threat-model delta;
- one distinct Continuity directory containing the closed contract, schemas,
  deterministic intent/evidence and clockwork artifacts;
- one provider-free harness, focused unit/provider-free tests and plan test;
- one successful attestation/evidence pair or one sanitized failure artifact;
- required Ariadne and exact-candidate independent-review receipts; and
- closeout, Sol acceptance and paired Yuri summary.

No `.env*`, `app/**`, migration, `docs/api-spine/**`, product test, OpenAPI,
GraphQL, async, client, provider, deployment or existing-runtime source is
editable. No protected-ref movement is authorised.

## Deterministic admission and one execution

Before any Docker object is created:

1. a fresh five-source receipt and all three explicit parallelism dispositions
   must pass;
2. every immutable source hash, full 40-character Git binding, contract,
   schema and manifest must pass;
3. at least 256 hostile contract mutations, 96 hostile manifest/evidence-state
   mutations and 24 hostile classifier packets must deny with zero escapes;
4. source inspection must prove no listener, port publication, relay,
   `docker exec`, multiprocessing or queue path and no secret in Docker config;
5. focused plan/harness/API Spine/latch/Baton tests, Ruff, compilation and
   `git diff --check` must pass; and
6. one clockwork checkpoint must advance the latch to the exact execution
   stage without bespoke canonical-state editing.

Then exactly one newly named disposable execution is authorised. It must stop
on the first mismatch and may not be rerun under this plan. Pass requires all
12 scenarios, zero retries, zero ordinary/product effects, exact role and
Docker cleanup, and no matching owned residue.

After the successful proof and deterministic packet, one fresh Gemini 3.7
Flash/high exact-candidate read-only veto must pass in a clean unchanged
worktree. DeepSeek occupied work remains closed until its separate native
Harness boot proof; Claude Code is not a fallback. Native subagents remain
serially constrained by the current developer policy. Closeout then uses one
clockwork tick, explicit-path staging, paired lay/technical Yuri summary and
the usual non-PHI Pushover notification.

## Explicit parallelism assessment

- **DeepSeek:** declined for this tranche. Its separate native-Harness boot
  proof is still outstanding, Claude Code is not an authorised fallback, and
  one mutable database lifecycle is not a separable worker package.
- **Gemini:** reserved for one fresh Gemini 3.7 Flash/high exact-candidate
  read-only veto after the deterministic packet and occupied proof pass.
- **Native subagents:** declined because the current developer policy requires
  serial execution and the database lifecycle has one cleanup owner.

All staging uses explicit paths only; `git add .` and `git add -A` are
forbidden. Preserve `docs/branding/` and every unrelated untracked file.

## Fail-closed rule

Any source, identity, credential, image, containment, OCI-state, observer,
transaction, readback, RLS, hostile-mutation, redaction or cleanup mismatch
stops with sanitized failure evidence. Ambiguity never becomes success,
retry, ordinary admission or permission to broaden the tranche.
