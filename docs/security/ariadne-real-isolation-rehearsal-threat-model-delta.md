# Threat Model Delta - Ariadne Real-Isolation Rehearsal

Date: 2026-07-23

Scope: one disposable local, network-disabled, read-only,
authored-synthetic container rehearsal

## Trust boundaries and assets

New trusted surfaces are the local Docker daemon, one pinned Docker Official
Image, the host lifecycle harness, the allowlisted build context and one
short-lived container. The accepted scripted runner and proofreader remain the
semantic sources.

Assets and invariants are:

- no repository-wide daemon exposure;
- exact image provenance and platform;
- no secret, host environment or host filesystem exposure;
- effective network, root, privilege and resource isolation;
- unchanged finite tape and proofreader result;
- inspect-before-start and fail-closed lifecycle;
- sanitised deterministic evidence; and
- explicit scoped cleanup without deleting unrelated daemon objects.

## Threats and mitigations

| Threat | Failure mode | Required mitigation |
|---|---|---|
| Tag or supply-chain drift | A mutable tag selects different image content | Official source plus immutable OCI index digest, recorded linux/amd64 manifest digest and post-pull architecture/digest inspection |
| Wrong-platform selection | Multi-arch index resolves to unreviewed platform | Require local engine and image `linux/amd64`; bind the exact platform manifest digest |
| Repository/secret exfiltration in build context | Docker receives `.env`, Git, ignored or unrelated files | Fresh temporary context copied from a fixed regular-file allowlist; never use repo root; no symlinks, build args or secret mounts |
| Dockerfile execution creep | Build runs package managers or scripts | Frozen Dockerfile has no `RUN`, `ADD`, remote source or shell form; tests inspect instructions |
| Host environment leakage | Container inherits tokens or credentials | No `--env`, env-file or caller input; inspect fixed image environment names and reject secret-like additions without echoing values |
| Host filesystem or daemon breakout | Repository, device or Docker socket is mounted | `--read-only`; empty binds/mounts/tmpfs/devices; no privileged mode; all capabilities dropped; no-new-privileges |
| Network escape | Workload receives routable interface or published port | `--network none`; no port bindings/exposed ports; pre-start inspect plus loopback-only workload observation; payload performs no outbound connection |
| Privilege escalation | Root/capabilities/setuid path widen impact | UID/GID 65532, `CapDrop=ALL`, `Privileged=false`, no-new-privileges and default seccomp retained |
| Resource denial | Infinite memory, processes, CPU or descriptors | 128 MiB memory/swap, 0.5 CPU, 32 PIDs and 64-file ulimit; reject inspect drift; record OOM status |
| Proofreader/tape replacement | Container runs convenient evidence instead of accepted work | Hash every copied source, run accepted modules unchanged twice and exact-compare committed predecessor projection |
| Writable-state laundering | Workload persists correction, mailbox or evidence | Read-only root, no tmpfs/volume and fixed write probe requiring OS failure and no residue |
| Inspect-after-execution gap | Bad policy is discovered only after workload starts | Build-image inspection and container effective-policy inspection must pass before `docker start` |
| Collision/destructive cleanup | Fixed name/tag belongs to unrelated user work | Pre-existing name/tag fails closed; track only resources created by this invocation; never prune or delete unowned objects |
| Failure leaves runtime behind | Payload or inspection error skips cleanup | Structured `finally` cleanup in container, image, acquired-base and temporary-context order; verify absence |
| Diagnostic leakage | Docker output exposes paths, IDs or environment values | Committed evidence keeps only allowlisted hashes, booleans, counts, limits and fixed labels; no raw inspect/log payloads |
| Image or build-cache residue overclaim | Layers survive image-reference removal | Remove scoped references; do not daemon-wide prune; explicitly record possible synthetic-only unreferenced/cache residue |
| Container-safety overclaim | One pass is treated as proof for agents or production | Exact evidence label and explicit unproved surfaces; no adaptive agent/model/product connection |
| Docker daemon compromise | A malicious daemon fabricates inspection or escapes host controls | Local daemon is an accepted trust dependency for this bounded experiment; result is not independent kernel/daemon attestation |

## Failure policy

Any provenance, manifest, hash, image, effective-policy, payload, stopped-state
or cleanup mismatch returns `revision_required`. The harness still attempts
scoped cleanup. A cleanup failure prevents a pass and is reported for manual
inspection; it does not authorise broad removal.

## Residual risks and closed gates

Docker daemon/kernel vulnerabilities, image CVE lifecycle, cross-platform
policy parity and unreferenced layer/cache retention remain residual. No
adaptive model, provider, prompt, tool call, live authorisation, PII, database,
event feed, product API, mailbox, human UI, durable state, appointment command,
production, deployment or autonomous-action risk is opened by this tranche.
