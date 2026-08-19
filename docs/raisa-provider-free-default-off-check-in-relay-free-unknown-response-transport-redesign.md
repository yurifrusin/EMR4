# Relay-free unknown-response transport redesign

Date: 2026-08-19

Timestamp: 2026-08-19T18:59:39.4552916+10:00 (Australia/Brisbane)

Status: `implementation candidate`

Decision-transition source:
`44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4`

## Decision

The host TCP relay and Windows multiprocessing queue are removed from the
future check-in unknown-response evidence path. The one-shot database caller
becomes the primary process of a separately captured OCI container. Attached
stdin supplies its ephemeral authored-synthetic credential; terminal Docker
state supplies its closed outcome. Those channels cannot substitute for each
other.

The future database server retains its internal-only network and no published
port. Admin setup/observation uses exact-ID `docker exec` against the server's
local Unix socket. The restricted caller uses `psql` from the exact cached
PostgreSQL image over the internal network. Fresh restricted-role readback uses
a new container-local client connection and releases only the closed packet
accepted by the existing pure classifier.

## Why this is narrower

The failed shape contained four independently live transports: PostgreSQL TCP,
Docker-exec TCP forwarding, host loopback TCP and a spawned Python process plus
queue. The replacement has two Docker-owned states: the server container and
the caller container. The host does not forward database bytes and does not
infer an outcome from a pipe, exception or worker message.

The terminal predicate is exact:

```text
captured identity matches
AND running is false
AND exit code is 42
AND OOMKilled is false
AND restart count is zero
AND Docker state error is empty
AND exact post-commit backend wait was observed and terminated
= connection_lost_without_complete_terminal_response
```

Any missing term is `unresolved_denied`. The command is never retried.

## Credential custody

The caller is created and inspected before the credential exists in its
namespace. Docker configuration contains no password or password hash. The
orchestrator attaches to the exact captured ID, sends one bounded credential
line and closes input. The wrapper holds it only in process memory and passes
it to the fixed `psql` child. Container logging is disabled and raw child
output is suppressed. Attachment lifecycle is cleanup evidence only.

This is development containment for an authored-synthetic ephemeral password,
not production secret custody or rotation evidence.

## No-database proof

The current tranche exercises only the result mechanism. A network-disabled
container overrides the image entrypoint with a fixed inert wrapper, receives
a random token over attached stdin, runs a fixed child that exits at the
simulated loss coordinate and terminates with OCI exit 42. The host reads the
captured container's Docker state before considering the attachment process.
No PostgreSQL server, database connection, SQL, network or product data exists
in this proof.

## API Spine boundary

The JSON contract is a declarative fixture. It cannot dispatch Docker, choose
exit status or perform a command. Typed code owns admission, lifecycle and
cleanup. The future database rehearsal remains command-shaped evidence only:
explicit practice scope, command/idempotency/request digest and audit identity
must agree before the pure readback classifier can return exact-once. No API
Spine artifact or product route changes in this tranche.

## Non-claims

This design and its no-database proof do not establish a PostgreSQL rollback,
commit acknowledgement loss, committed-versus-rolled-back readback, exact-one
effect, driver/pool behavior, network partition handling, concurrent command,
production monitoring, ordinary-practice admission or product runtime. Those
remain closed until a separate exact relay-free database plan passes.
