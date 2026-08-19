# Provider-free default-off check-in relay-free unknown-response transport redesign plan

Date: 2026-08-19

Timestamp: 2026-08-19T18:59:39.4552916+10:00 (Australia/Brisbane)

Status: `frozen`

Decision-transition source HEAD:
`44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4`

Clockwork decision generation:
`gen-2d53ea088396842542bd070e2168078ab9c803d7166e4e20bc9b0135efa7ce47`

Accepted runtime-role and tenant-isolation floor:
`6a2832575e9b4df5c40a13984db7281e79814a94`

Target result:
`raisa_provider_free_default_off_check_in_relay_free_unknown_response_transport_redesign_pass`

Reasoning level: Extra High freezes the replacement transport, credential,
result-channel and claim boundaries. High is sufficient for the fixed
provider-free implementation, one no-database container proof, deterministic
verification and check-gated closeout while this plan remains unchanged.

## Objective

Replace the failed Windows host TCP relay plus `multiprocessing.Queue` evidence
path with a relay-free, Docker-owned caller/result boundary before any further
PostgreSQL execution.

This tranche must:

1. freeze the future database caller as a separately identified OCI container
   whose primary process is the one-shot restricted-role caller;
2. deliver the ephemeral authored-synthetic credential over attached stdin,
   never through Docker configuration, argv, logs, a bind mount or a durable
   file;
3. classify the caller only from exact container identity plus terminal OCI
   state, independently of the lifetime or return code of the host attachment;
4. prove the result-channel mechanism once with an exact cached-image,
   provider-free, network-disabled container fixture that starts no database;
   and
5. leave the three predecessor failures immutable and perform no fourth or
   successor PostgreSQL execution in this tranche.

The result is transport architecture and no-database operational evidence. It
is not rollback, commit-uncertainty, readback or ordinary check-in acceptance.

## Exact evidence boundary

Every source below is strict UTF-8, canonical LF and SHA-256 bound before the
occupied no-database proof:

| SHA-256 | Exact source |
|---|---|
| `0f66b6cb067479c57d419d8aa6bf92e99251946e828f454f24a2bc9e490baa8e` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal-plan.md` |
| `85bf13e548ffd5f4497c29b96b16120488bdc8bf4bb78861aa2f229850a9c182` | `docs/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal-blocked-closeout.md` |
| `34489e42e16defcaf47132ff04f16204dd528b7d7d454d245f281c318b432e57` | `orchestration/agent_inbox/codex/raisa-check-in-rollback-unknown-commit-recovery-sol-blocked-assessment.md` |
| `e357e3a2dec7f0d0740a2ea6f518cb695dc2a5cbf88b9c321dbcd61d6e7bd1c1` | immutable predecessor attempt 001 |
| `bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed` | immutable predecessor attempt 002 |
| `15cebad64c7bfbddb83878e75cf8f3a0d137a7834075e063c92aead8b603e219` | immutable predecessor attempt 003 |
| `94ac2239a81f06e1404fa6c3fe7a02c9e9df2c0b4cea6b633347a987171a1712` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal/rehearsal-contract.json` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` | `orchestration/api_spine_programme.md` |
| `c1ac9a35088927ff3af804db2d162d01d06133973ecb36b5be262697a49e255a` | immutable clockwork user-decision tick evidence |
| `5640874077b42019680b39c8b588844e125ed041527ec6509bf06c48480ba71e` | immutable clockwork user-decision tick report |

The exact attempt-002 source path is
`orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence-attempt-002.json`.
Its row above must equal the actual full SHA-256 before implementation; any
transcription mismatch fails planning admission and must be corrected before
environment action. No abbreviated Git object is accepted anywhere.

## API Spine classification

This is a command-adjacent transport fixture, not a command endpoint. Its JSON
contract is declarative and cannot dispatch a container, choose an outcome or
write a database. Typed Python owns admission, lifecycle, redaction and exact
cleanup. A future restricted-role `psql` sidecar will execute only a separately
frozen transaction fixture.

No REST/OpenAPI, GraphQL, async, YAML-manifest, product schema or client
artifact changes. GraphQL remains read-only; every future state-changing
request must still preserve explicit practice scope, command and idempotency
identity, audit atomicity, default denial and authoritative readback.

## Frozen future database transport

The next database rehearsal may use this transport only after its own frozen
plan, deterministic admission and fresh five-source preexecution receipt.

### Caller process

- Create one uniquely named and labelled caller container from the same exact
  cached `postgres:16-bookworm` image as the disposable server, with pull
  policy `never` and no build.
- Connect it only to the captured internal Docker network. Publish no port and
  create no host listener, TCP forwarder, Docker-exec byte bridge, bind mount,
  volume or external-network attachment.
- Override the image entrypoint with a fixed typed shell wrapper whose primary
  child is `psql`; no caller source, script or credential is supplied by a
  manifest.
- Use read-only rootfs, one exact tmpfs, `no-new-privileges`, dropped
  capabilities, bounded memory/CPU/PIDs and restart policy `no`.
- Use logging driver `none`. Raw `psql` stdout/stderr and exception text are
  never evidence and never enter Docker logs.

### Credential delivery

Create the caller with stdin held open. After exact ID, label, nonce, image,
network and no-secret configuration inspection, attach only to that captured
container and write the random 32-byte runtime password as the first bounded
line. The wrapper reads it directly into process memory, exports it only to its
`psql` child and unsets it after child exit. It must not appear in container
environment configuration, command arguments, labels, logs, evidence, a host
file, a container file, a hash field or a Docker object retained after cleanup.

Attachment is credential input only. Its process state, stdout, stderr and
return code are not outcome evidence.

### Closed outcome mapping

The wrapper has three fixed terminal codes:

- `0`: fixed complete-terminal-response marker reached after the child
  completed normally;
- `42`: child lost its database connection before that marker and no success
  was released; and
- `43`: any other wrapper, marker or child-state inconsistency.

The orchestrator admits the future expected unknown outcome only when the
captured caller container is stopped, has exit code `42`, `OOMKilled=false`,
empty Docker state error, restart count zero, the exact backend was previously
observed at the frozen post-commit wait and only that backend was terminated.
Every missing, running, zero, 43, other, OOM, restarted, mismatched or
unreadable state is `unresolved_denied` and permits no readback claim or retry.

The terminal OCI state is the result channel. The host attachment may be
terminated after the container is stopped and must itself be absent before
cleanup, but it cannot supply or override the outcome.

### Future restricted readback

The database successor must use a fresh restricted-role login without a host
relay. A direct container-local `psql` client may connect over the internal
network or from the server container over loopback, receive the credential
through stdin under the same no-config/no-log rule, and release only the closed
relation packet needed by the existing pure classifier. Admin observation and
setup may use exact captured-container `docker exec` over the server's Unix
socket. Neither path makes Docker, shell or `psql` command authority.

## One occupied no-database proof

After static admission, run exactly one newly named fixture container:

- exact cached image ID
  `sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8`;
- `--pull never`, `--network none`, no published port, bind mount or volume;
- entrypoint overridden to the fixed wrapper; no `postgres` process starts;
- random 32-byte token delivered only over attached stdin after exact
  configuration inspection;
- fixed inert child exits at the wrapper's simulated lost-response coordinate;
- wrapper emits no stdout/stderr/log and exits `42` without a complete marker;
- the host derives the outcome only from exact OCI state, then terminates any
  remaining attachment and deletes the exact captured container by ID after
  label/nonce/image/name reverification.

This proves credential-input separation, OCI-state outcome closure and cleanup
without claiming a database connection, transaction, commit or readback.

## Fixed scenarios

1. `RFT-S01` — full Git and exact source hashes pass;
2. `RFT-S02` — contract and schemas reject caller-authored source, image ID,
   container identity, exit state, generation, lease or evidence digest;
3. `RFT-S03` — the cached exact image is admitted without pull;
4. `RFT-S04` — exact no-network/no-port/no-bind/no-volume/no-log containment
   plus the one allowlisted tmpfs is verified before start;
5. `RFT-S05` — token is absent from Docker config, command and labels before
   attached-stdin delivery;
6. `RFT-S06` — attachment delivers the bounded token but is excluded from
   outcome classification;
7. `RFT-S07` — fixed child loss maps to terminal OCI exit `42` with no complete
   marker, OOM, restart or Docker state error;
8. `RFT-S08` — hostile running/zero/43/other/OOM/restarted/mismatched states
   all deny;
9. `RFT-S09` — no database or `postgres` process, network, provider, product
   row, success release or retry occurs; and
10. `RFT-S10` — attachment and captured container are exactly absent.

## Evidence and redaction

Release only source/digest bindings, closed containment booleans, exact image
ID digest, closed OCI-state classification, hostile-mutation counts, elapsed
bounds and cleanup disposition.

Never serialize the token or its hash, Docker/container name, container ID,
process ID, local path, argv, environment, raw stdout/stderr/log, command text,
exception, SQL, DSN, password, backend PID, product/patient/appointment/
clinical value or protected material.

Evidence label:
`authored_synthetic_provider_free_no_database_relay_free_oci_result_transport`.

## Exact owned outputs

Sol may create or update only:

- this plan and its threat-model delta;
- one design report, closed contract/schema and evidence schema under the named
  Continuity directory;
- one provider-free no-database harness plus focused unit/plan tests;
- one successful evidence artifact or one sanitized failure artifact;
- required Ariadne and exact-candidate review receipts; and
- closeout, Sol acceptance, Yuri summary and clockwork-owned closeout surfaces.

No predecessor failure artifact, `.env*`, `app/**`, migration,
`docs/api-spine/**`, OpenAPI/GraphQL/async, product test, client, provider,
deployment or existing runtime source is editable.

## Deterministic acceptance

Pass requires:

1. fresh five-source receipt and complete DeepSeek/Gemini/native-subagent lane
   dispositions;
2. the clockwork decision generation and full 40-character Git source validate;
3. every exact source hash matches, including the attempt-002 row correction
   gate above;
4. contract/schema validation plus at least 256 hostile contract and 96
   hostile evidence/state mutations with zero escapes;
5. source inspection proves there is no host listener, TCP forwarder,
   Docker-exec byte bridge, multiprocessing process or queue in the new path;
6. the one no-database fixture uses only the exact cached image and frozen
   containment, with no pull, network, port, bind mount, volume or log driver
   and only the one exact tmpfs;
7. token delivery is attached-stdin only and the token is absent from every
   admitted Docker configuration and released value;
8. exact OCI state independently classifies only exit `42` as the fixture's
   closed simulated lost-response outcome, and every hostile state denies;
9. no database or `postgres` process, complete success, retry, provider call,
   product row or ordinary release occurs;
10. exact attachment/container cleanup passes and no matching residue remains;
11. focused transport, plan, clockwork, latch, Current Baton and API Spine
    tests, Ruff, compilation, JSON validation and `git diff --check` pass;
12. one fresh Gemini 3.7 Flash/high exact-candidate read-only veto passes after
    deterministic admission and leaves its worktree unchanged; and
13. one clockwork clean-closeout tick advances only after the accepted
    no-database proof, without manual canonical edits, bespoke updater or
    protected-ref movement.

## Parallelism assessment

- **DeepSeek:** declined. Its native Harness still requires the separate
  stock-headless-to-custom-runner boot proof, Claude Code is no fallback and
  this material result-channel boundary is tightly coupled to one occupied
  container lifecycle.
- **Gemini:** reserved for one fresh exact-candidate read-only veto after every
  deterministic and occupied no-database gate passes.
- **Native subagents:** declined under current developer policy and because the
  clockwork, transport design and one mutable lifecycle are serial.

## Stop and successor

Any source, image, containment, credential-delivery, OCI-state, redaction or
cleanup mismatch emits only sanitized failure evidence, releases no pass and
permits no repeat without a frozen recovery. A running or residual captured
container is cleanup recovery, never transport evidence.

Passing authorizes only a separately planned provider-free disposable
PostgreSQL successor to use the exact relay-free transport. It does not itself
authorize that execution or prove rollback, commit uncertainty, authoritative
readback, exact-one effect, driver/pool behavior, production handling or
ordinary check-in readiness.

No ordinary-practice enablement, feature/allowlist change, product/config/API
change, generic-status `Arrived`, action grammar/client change, waiting-area
movement, product/patient/appointment/clinical/protected data, occupied
DeepSeek run, production runtime, deployment, release, Pages or protected-ref
movement is authorized. Preserve `docs/branding/`; stage explicit paths only.
