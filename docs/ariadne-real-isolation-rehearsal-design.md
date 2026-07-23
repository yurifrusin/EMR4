# Ariadne Real-Isolation Rehearsal - Design

Date: 2026-07-23

Status: frozen for one local authored-synthetic container run

## Design statement

The accepted in-memory rehearsal remains the work. The container is a narrow
isolation wrapper around that unchanged work, not a new work-cell executor.
There is still no agent in the cell: the fixed tape stands in for the typist,
the accepted deterministic proofreader remains sovereign over egress, and the
container tests only whether the declared physical desk boundary is actually
present for this run.

## Host/control boundary

The host harness owns lifecycle and proof. It accepts only `validate`,
`rehearse` and `trace`; callers cannot supply an image, path, command, name,
resource limit or Docker argument. Subprocesses use fixed argument arrays with
no shell.

`validate` performs repository-only manifest and source validation. `trace`
prints the frozen posture. `rehearse` alone may perform the authorised Docker
lifecycle. It refuses collisions, creates an allowlisted temporary context,
acquires the pinned base if necessary, builds, inspects, creates, inspects,
starts, inspects and cleans up.

## Image boundary

The Dockerfile uses the frozen official digest, contains no `RUN` instruction,
copies only the temporary allowlist, sets a non-root user and fixes the payload
entry point. The full repository is neither build context nor mount. This
prevents `.env`, Git metadata, ignored local files and unrelated user work from
being sent to the daemon.

Digest pinning prevents tag drift. Platform validation prevents a multi-arch
index from silently selecting an unrecorded workload. Image inspection checks
the derived entry point, working directory, user and provenance labels before a
container is created.

## Container boundary

The container has a read-only root filesystem, no mounts and no network
namespace beyond loopback. It runs as UID/GID 65532 with all capabilities
dropped and no-new-privileges enabled. Memory, swap, CPU, process and open-file
limits are finite. No ports, devices, secrets, health checks, restart policy or
host environment values are attached.

Host inspection is authoritative for Docker policy. Workload observations are
a second, deliberately small cross-check: non-root identity, loopback-only
interfaces and an `EROFS` write failure. Neither observation is presented as a
general container-escape proof.

## Evidence boundary

The payload verifies the exact copied source hashes, calls the unchanged
scripted runner twice and compares its committed projection with the accepted
predecessor evidence. Its canonical output excludes host paths, container IDs,
environment values and exception text.

The host projection binds:

- manifest and allowlist hashes;
- pinned image and platform digests;
- sanitised effective-policy booleans and numeric limits;
- the payload's exact deterministic result;
- stopped-state results; and
- explicit cleanup outcomes.

The committed evidence is deterministic except for no random IDs or timestamps
being included. A later rerun would be a new authorised observation, not a
continuing runtime.

## API Spine result

Boundary classification:
`local_disposable_container_authored_synthetic_isolation_rehearsal`.

Typed synthetic context remains non-authoritative. The container cannot read
from or write to GraphQL, REST/OpenAPI, PostgreSQL, an event feed, product API
or command plane. No API Spine file changes.

## What this proves and does not prove

It can prove that one inspected local Docker container ran the accepted tape
under the exact recorded effective policy, returned the accepted deterministic
result and was explicitly removed.

It cannot prove kernel or daemon invulnerability, adaptive-agent safety,
prompt/tool security, live identity or authorisation, PHI minimisation,
network-policy portability, persistence semantics, human approval, backend
revalidation, product behaviour, production readiness or safe autonomous
action.
