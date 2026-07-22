# Ariadne Real-Isolation Rehearsal - Closeout

Date: 2026-07-23

Result: `ariadne_real_isolation_rehearsal_pass`

Owner: GPT Sol High

## Outcome

The bounded real-isolation rehearsal passes. One disposable local
`linux/amd64` container ran the unchanged accepted authored-synthetic work-cell
tape under a digest-pinned, inspect-before-start, network-disabled, read-only,
non-root, no-mount, no-secret and resource-bounded Docker policy.

The result is evidence about one isolation envelope around an unchanged finite
workload. No adaptive agent, generated draft, model, provider, database, event
feed, product API, live mailbox, human-gate UI or command was attached.

## What was proved

- The Docker Official Python 3.12.13 Alpine 3.22 OCI index and its
  `linux/amd64` platform manifest matched the frozen digests, official source
  revision and creation annotation.
- The repository was never used as build context or mounted. A temporary
  context contained exactly 14 hash-bound, regular, non-symlink
  authored-synthetic files plus its fixed manifest.
- The Dockerfile contained no `RUN`, `ADD`, `ARG`, package installation,
  exposed port, volume, health check or caller input.
- Its exact path is pinned to LF in `.gitattributes`, preserving the frozen
  byte hash across Windows checkouts.
- Before start, effective inspection proved `NetworkMode=none`, read-only root,
  UID/GID 65532, `CapDrop=ALL`, no added capabilities,
  `no-new-privileges=true`, non-privileged mode, no bind/volume/tmpfs/device,
  no published port, no host environment forwarding and no secret.
- Limits were effective at 128 MiB memory and swap, 0.5 CPU, 32 PIDs and 64
  open files.
- Inside the namespace the payload observed UID/GID 65532 and only loopback.
  It made no outbound connection.
- A fixed write under `/workspace` failed with `EROFS` and left no residue.
- The accepted finite tape ran twice through the unchanged proofreader. Both
  full results were byte-identical and exactly matched the committed
  predecessor projection: 8 scenarios, 53 transitions, 8 releases, 4 inert
  human-gate deliveries, 2 aborted edges and 1 supersession.
- Stopped-state inspection proved exit code zero, no OOM, no engine error and
  no restart.
- The fixed container, derived image, run-acquired base reference and temporary
  context were explicitly removed and independently rechecked absent.

## Canonical image and evidence

- base index:
  `sha256:a190708a2dec1bd18b1decb539f8e8f5407abaa9bf39cacda583f7f8c11db322`;
- `linux/amd64` manifest:
  `sha256:9381e50cc82f4279b949fcd2d2f5e57cf97b1da2399eb956502364ceea2f4e83`;
- effective-policy selected-config hash:
  `sha256:01565821d7e028547c546fd33d76c227745f07bfaf97a51d59812ff64d71988e`;
- predecessor projection hash:
  `sha256:1724f3e804ebe3ef7fe033e2f3f4feaf0c7897054960979a7451735ff15d1566`.

Evidence label:
`authored_synthetic_disposable_local_container_isolation_rehearsal`.

## Cleanup precision

No daemon-wide prune was run. Docker may retain unreferenced layer content or
BuildKit cache containing only the official base and the 14 allowlisted
authored-synthetic files. The result claims removal of scoped runtime and image
references, not forensic erasure of daemon storage.

## API Spine and security result

Boundary classification:
`local_disposable_container_authored_synthetic_isolation_rehearsal`.

Typed synthetic context remains non-authoritative. GraphQL is read-only and
unused; REST/OpenAPI is the future command plane and unused. No API Spine,
product, database, API or UI artifact changed.

The threat delta covers image/tag/platform drift, build-context and secret
exposure, Dockerfile execution creep, host environment leakage, mounts and
Docker-socket exposure, network escape, privilege escalation, resource denial,
tape substitution, writable-state laundering, inspect ordering, collision and
cleanup safety, diagnostic leakage, cache residue and container-safety
overclaim.

## Verification

- one real disposable Docker lifecycle: passed;
- focused real-isolation suite: 28 passed, 0 failed;
- combined real-isolation, predecessor work-cell, Event Router, Sandbox DAG,
  Continuity, Compass, orchestrator, operating-model, API Spine and handover
  population: 177 passed, 0 failed;
- evidence Draft 2020-12 schema and manifest semantics: passed;
- exact predecessor projection and repeated in-container evidence: passed;
- Docker cleanup readback: passed;
- Ruff and Python compilation: passed;
- JSON parsing and `git diff --check`: passed.

The two warnings are existing Starlette and Google GenAI dependency
deprecations and are unrelated to this tranche.

## Allocation and review

Sol High owned architecture, implementation, the single real lifecycle,
deterministic tests, acceptance and protected integration. No implementation
worker, native subagent or external model reviewer was used because provenance,
effective inspection, workload observation and cleanup formed one serial trust
claim. The result claims local Sol acceptance, not an independent external
veto.

The EMR4 API Steward skill preserved the boundary: the container received only
typed authored-synthetic predecessor artifacts; declarative JSON supplied no
authority; GraphQL, REST/OpenAPI and product command surfaces remained absent.

## Preserved gates and next decision

This does not prove daemon/kernel invulnerability, model safety, prompt/tool
security, live identity or authorisation, PHI handling, persistence, human-gate
usability, backend revalidation, product behaviour or production readiness.

Adaptive/generated cognition, models, providers, repeated or long-lived
containers, networking, writable/mounted inputs, secrets, concurrency, durable
state, product reads, databases, event feeds, live mailboxes, human-gate UI,
appointment commands, PII, protected/historical evidence, Stage 3B,
production, deployment, release and autonomous action remain closed.

The smallest next candidate is a bounded agent-admission design: decide the
least authority-widening topology for generated cognition, including local
versus provider transport, context minimisation, prompt injection, model
provenance, token/resources, networking or mounting, secrets and adversarial
evidence before any model call. It requires a fresh Yuri decision and this
closeout grants none of that authority.
