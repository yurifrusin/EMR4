# Provider-free read-only check-in server start/attach created-state failure-coordinate diagnosis plan

Date: 2026-08-23

Timestamp: 2026-08-23T02:11:15.3452260+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`53760513c42a380904136eb4ef2f5ffda397e820`

Accepted attempt-006 occupied source:
`a9567be36c82bc6d2eebc2488b48cd8bfb9f8d23`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Operation:
`raisa-provider-free-read-only-check-in-server-start-attach-created-state-failure-coordinate-diagnosis`

Target result:
`raisa_provider_free_read_only_check_in_server_start_attach_created_state_failure_coordinate_diagnosis_pass`

Reasoning level: High is required to keep observation, inference and future
repair separate while deriving one closed failure coordinate from source,
immutable terminal evidence, CLI help/version and deterministic process fakes.

## Starting fact and authority

Attempt 006 is consumed once and immutable. It passed static admission, created
and verified one captured server without credentials, delivered credentials by
attached stdin, then failed closed at
`environment/server_not_running_after_readiness`. Its safe terminal projection
reports Docker status `created`, `running=false`, safe exit code zero, an empty
state-error relation, restart count zero, attachment-process
`exited_nonzero`, and attachment-stdin `open_after_delivery`.

No readiness success, setup, role creation, transaction, authoritative
readback or attestation occurred. Cleanup removed every owned object and a
postterminal read-only inspection found zero residue. The failure and envelope
remain bound by SHA-256
`3c7049b318fffb28aa70e8b4346f1ed857b7cf34e1780eec21373935f6c88efd`
and
`52470c6c6245f0988dd4f580e68f7a0e21ce5b8636e60119091c089d603bde1c`.

Yuri's standing uninterrupted-development authority permits the narrowest
dependency-satisfied diagnosis. It does not permit an attempt-006 retry,
attempt 007, Docker object mutation, PostgreSQL start, SQL or database work.

## Narrow objective

Bind the exact attempt-006 terminal and exact current start/attach source;
inspect only local Docker CLI help/version evidence; exercise the source
decision logic through deterministic process fakes; then release one closed,
sanitised coordinate that distinguishes:

1. an advertised CLI option-surface mismatch;
2. a nonzero composite start/attach host process while OCI remained `created`;
3. a post-start container exit;
4. a readiness timeout while the container remained running; or
5. insufficient evidence.

The coordinate describes the last supported boundary, not an invented root
cause. In particular, a valid help surface plus a `created` OCI state cannot
distinguish an engine start rejection from an attach-path rejection without
additional future instrumentation.

The tranche must identify the smallest repair surface needed to obtain that
missing distinction. It must not implement the repair or authorise an occupied
run.

## Exact source and evidence bindings

The diagnosis binds these immutable inputs byte-for-byte:

| SHA-256 | Exact source |
|---|---|
| `3c7049b318fffb28aa70e8b4346f1ed857b7cf34e1780eec21373935f6c88efd` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-006/rehearsal-failure-evidence.json` |
| `52470c6c6245f0988dd4f580e68f7a0e21ce5b8636e60119091c089d603bde1c` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-006/attempt-006-execution-envelope.json` |
| `839a9a17b22aa132ea5bddf878f59f4741412cb1ee464020f34aa2aefbdff8e2` | `scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py` |
| `9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b` | `orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/created-state-representation-evidence.json` |

Every Git binding is a machine-resolved full 40-character commit object. The
diagnostic evidence must reject abbreviations, caller-completed identifiers,
digest drift, source drift and any attempt to mutate or reclassify attempts
001 through 006.

## Read-only execution boundary

The only Docker subprocesses admitted are:

- `docker.exe version` with a fixed, non-secret format; and
- `docker.exe start --help`.

They may read CLI/engine metadata but may not name a container, network, image
or volume and may not invoke create, run, start against an object, attach,
exec, inspect, stop, kill, remove, prune, pull, push, login or build. The
diagnostic script must use a closed command manifest and reject caller-supplied
arguments.

All other subprocess behavior is represented by deterministic fakes. No fake
may call Docker, PostgreSQL, a network, a provider or a product path. Source
inspection is limited to exact repository files and Python AST/constants.
Raw Docker help/version output is controller-local only; retained evidence may
contain fixed booleans, a bounded version token, command return codes and
SHA-256 digests, never paths, credentials, environment values, object
identifiers or unbounded streams.

## Closed diagnostic vocabulary

One source constant must own the exact coordinate vocabulary used by the
classifier, schema, evidence and hostile tests:

- `cli_option_surface_mismatch`
- `composite_start_attach_exited_while_oci_created`
- `container_exited_after_start`
- `readiness_expired_while_running`
- `insufficient_closed_evidence`

The expected attempt-006 classification is admitted only when all of these
closed predicates hold: the exact help surface advertises `--attach`,
`--interactive` and `--sig-proxy`; the exact source builds the closed
start/attach argument vector; the host process relation is `exited_nonzero`;
stdin is `open_after_delivery`; and the OCI projection is valid, `created` and
not running. Missing, contradictory or additional evidence must classify as
`insufficient_closed_evidence` or reject.

This coordinate supports only the conclusion that the composite host command
failed before a running OCI state was observed. It does not attribute fault to
Docker option parsing, the engine, attach, the container entrypoint,
PostgreSQL, credentials or the host platform.

## Construction and proof

The tranche may add only:

- one deterministic diagnostic module;
- one exact contract and schema;
- one canonical diagnosis evidence document and technical report;
- focused plan, classifier, source-binding, CLI-manifest and hostile tests;
- closeout, acceptance, workflow-efficacy, clockwork and Yuri-summary
  artifacts.

The current database harness remains byte-for-byte unchanged. The diagnostic
module exposes only `--check` and one provider-free read-only `--execute` path,
uses a fixed repository-owned output namespace, refuses overwrite, validates
all input hashes before reading CLI help/version, and writes canonical JSON by
exclusive creation.

Hostile coverage includes every closed coordinate, missing and extra keys,
source or digest drift, short Git identifiers, invented state labels,
contradictory OCI/process relations, noncanonical bytes, oversize output,
symlink/path escape, raw stream retention, command-manifest mutation and every
prohibited Docker verb. Static tests must prove zero Docker object arguments,
zero PostgreSQL/database paths, zero provider requests and zero product
effects.

## Acceptance

Acceptance requires:

1. the fresh five-source receipt and explicit three-lane assessment pass;
2. all immutable inputs and full-object ancestry bindings match exactly;
3. the closed Docker command manifest contains only version and start-help;
4. CLI evidence establishes the option surface without naming or mutating an
   object;
5. exact source inspection and deterministic fakes select one vocabulary
   coordinate with no raw output retained;
6. the report separates observed fact, bounded inference, unresolved cause and
   future repair;
7. the proposed repair is narrower than a database retry and remains
   unimplemented;
8. focused tests, Ruff, compilation, JSON/schema checks and
   `git diff --check` pass; and
9. Git/protected/data/product boundaries and every unrelated untracked path
   remain unchanged.

## Parallelism assessment

- **DeepSeek native Harness:** `declined`, negative leverage. Worker allocation
  and provider authority are closed; this small source-plus-terminal forensic
  task has no bounded model work package.
- **Gemini:** `declined`, neutral leverage. No material repair candidate exists
  to veto. Reassess only after deterministic evidence identifies a concrete
  future repair surface.
- **Native subagents:** `declined`, negative leverage. Developer policy
  prohibits proactive delegation and the diagnosis is narrow and serial.
- **GPT Sol:** owns plan meaning, exact evidence, local read-only subprocesses,
  deterministic tests, acceptance, clockwork and Git.

## API Spine, protected and continuation boundaries

This tranche changes no REST/OpenAPI command, GraphQL read model, async
contract, route, application schema, migration, feature flag, authored-
synthetic allowlist, action grammar, first-party client, waiting-area behavior
or product configuration. Dedicated check-in remains default-off. Generic
status does not gain `Arrived` and no ordinary practice is enabled.

No product, patient, appointment, clinical, historical or protected data; live
provider; production runtime; deployment; release; Pages; protected evidence
access; or protected-ref movement is authorised. Local/origin `master` and
`handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Closeout uses clockwork as the sole canonical governance writer. Sol writes
the paired lay/technical Yuri summary, sends the usual non-PHI Pushover,
stages only explicit paths, and preserves `docs/branding/` plus every unrelated
untracked file. No attempt 007 may begin without a separately accepted repair,
new plan, fresh five-source preexecution receipt and distinct one-run
checkpoint.
